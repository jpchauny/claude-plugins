#!/usr/bin/env python3
"""The deterministic part of the use case derive-grammar of the plugin clean-derived-norms.

Run from the root of the repository of layer 2, the working directory, as:
    uv run --with "lark[interegular]" python3 -I -B <this script> <command>
Commands: worklist, seal --model <model ID>, check, stale-citations. The script
never writes a statement of the grammar and never decides the state of a
fragment.

Spec: use-cases/derive-grammar/specs/derive-grammar.md (DGR) of the plugin.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

TREE_REL = "data/tree.jsonl"
GRAMMAR_REL = "specs-derived/grammar/clean.lark"
STATUS_REL = "specs-derived/grammar/clean-language-code-examples-status.jsonl"
COMMIT_RE = re.compile(r"[0-9a-f]{40}")

# The plugin that holds the script: the folder two levels above the script's
# folder, use-cases/derive-grammar/ (DGR-4, Terms: Plugin version).
PLUGIN_NAME = "clean-derived-norms"
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
# The record of the installed plugins of Claude Code (DGR-4, Terms: Marketplace commit).
INSTALLED_PLUGINS = Path.home() / ".claude" / "plugins" / "installed_plugins.json"

META_KEYS = ["type", "specs_commit", "generator", "model", "grammar_sha256", "status_sha256"]
GENERATOR_KEYS = ["plugin", "version", "marketplace_commit"]
# The model of the meta line (DGR-4, Terms: Model ID).
MODEL_RE = re.compile(r"[A-Za-z0-9._-]+")
FRAGMENT_KEYS = ["type", "id", "hash", "cases", "state", "reason", "issue"]
STATES = ("derived", "pending")
CASES = ("accept", "reject")
ISSUE_RE = re.compile(r"https://github\.com/Ivan-Pasco/clean-language-foundation/issues/[1-9][0-9]*")

NORM_ID = r"[A-Z]{3,}(?:-[0-9]+)?"
GRAMMAR_CITATION_RE = re.compile(r"^// (" + NORM_ID + r")@([0-9a-f]{8}): (\S.*)$")
SCRIPT_CITATION_RE = re.compile(r"^# (" + NORM_ID + r")@([0-9a-f]{8}): (\S.*)$")
SCRIPT_CITATION_ATTEMPT_RE = re.compile(r"^\s*# " + NORM_ID + r"@")
INLINE_CITATION_RE = re.compile(r"(?<![A-Za-z0-9-])(" + NORM_ID + r")@([0-9a-f]{8})(?![0-9A-Za-z])")

# A blank is a space or a tab (DGR-6, Terms): no other whitespace.
BLANKS = " \t"
FENCE_OPEN_RE = re.compile(r"^([ \t]*)(`{3,}|~{3,})(.*)$")
# The info string of a Clean example (CDN, Terms: Fragment).
EXAMPLE_INFO = "clean-language"
# The forms of the opening line (CEX-4), with an error code ^[A-Z]{3,6}[0-9]{3}$
# and a line number with no leading zero. The prefix of the code is not checked (DGR-6).
CODE = r"[A-Z]{3,6}[0-9]{3}"
OPENING_FORMS = (
    (re.compile(r"clean-language expect=valid"), "accept"),
    (re.compile(r"clean-language expect=syntax-error code=" + CODE + r" line=(0|[1-9][0-9]*)"), "reject"),
    (re.compile(r"clean-language expect=error code=" + CODE), "accept"),
)
NO_FORM_REASON = "the opening line is none of the forms of CEX-4"
FIXED_NAMES = ("start", "_NL", "_INDENT", "_DEDENT", "NAME", "RESERVED")


class InputError(Exception):
    """An input that the script cannot read: exit status 2.

    Spec: DGR-4, DGR-12, DGR-13, DGR-18.
    """


# ---------------------------------------------------------------- the tree


class Tree:
    """The norms of data/tree.jsonl.

    Spec: DGR-1, DGR-2.
    """

    def __init__(self, rows):
        """Index the rows of data/tree.jsonl.

        Spec: DGR-1, DGR-2.
        """
        self.meta = next((r for r in rows if r.get("type") == "meta"), {})
        # The commit of layer 1: "specs_commit", or "foundation_commit" in an older tree (DGR-4).
        self.specs_commit = self.meta.get("specs_commit") or self.meta.get("foundation_commit")
        self.nodes = {}
        self.order = {}
        self.children = {}
        for row in rows:
            if row.get("type") != "node":
                continue
            self.nodes[row["id"]] = row
            self.order[row["id"]] = len(self.order)
            if row.get("status") == "active":
                self.children.setdefault(row.get("parent"), []).append(row)
        self.fragments = [n for n in self.nodes.values() if is_fragment(n)]
        self.fragment_ids = {n["id"] for n in self.fragments}

    def norm_hash(self, norm_id):
        """The norm hash of a norm: the first 8 hex digits of its tree_hash.

        Spec: DGR-9 (Terms: Norm hash).
        """
        return self.nodes[norm_id]["tree_hash"][:8]


def load_jsonl(path, what):
    """Read a JSON Lines file; a line that is not a JSON object raises InputError.

    Spec: DGR-4, DGR-12 (exit 2), DGR-13.
    """
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value, error = json_object(line)
        if error:
            raise InputError(f"{what} {path}:{number}: {error}")
        rows.append(value)
    return rows


def json_object(line):
    """One line of JSON Lines as (object, None), or (None, what is wrong).

    Spec: DGR-12 (exit 2), DGR-13.
    """
    try:
        value = json.loads(line)
    except json.JSONDecodeError:
        return None, "not JSON"
    if not isinstance(value, dict):
        return None, "not a JSON object"
    return value, None


def load_tree(root):
    """Load data/tree.jsonl from the working tree.

    Spec: DGR-1, DGR-12, DGR-13, DGR-18.
    """
    path = root / TREE_REL
    if not path.is_file():
        raise InputError(f"{path} does not exist")
    return Tree(load_jsonl(path, "tree"))


def opening_match(own_text):
    """The match of the opening fence on the first line of a code block, or None.

    Spec: DGR-2, DGR-6.
    """
    return FENCE_OPEN_RE.match((own_text or "").split("\n", 1)[0])


def info_string(own_text):
    """The info string of a code block: the text after its fence, without the blanks around it.

    Spec: DGR-2 (Terms: Opening line, info string).
    """
    match = opening_match(own_text)
    return match.group(3).strip(BLANKS) if match else None


def is_fragment(node):
    """A norm of kind code_block, active, whose info string is clean-language or starts with it and a space.

    Spec: DGR-2.
    """
    if node.get("kind") != "code_block" or node.get("status") != "active":
        return False
    info = info_string(node.get("own_text", ""))
    return info is not None and (info == EXAMPLE_INFO or info.startswith(EXAMPLE_INFO + " "))


# ---------------------------------------------------------------- the case


def opening_case(info):
    """The case of an info string and its expected line: ("accept", None), ("reject", n), or None.

    None when the info string is none of the forms of CEX-4.

    Spec: DGR-6.
    """
    for pattern, case in OPENING_FORMS:
        match = pattern.fullmatch(info or "")
        if match:
            return case, int(match.group(1)) if case == "reject" else None
    return None


def case_kinds(node):
    """The cases of a fragment, as the status line holds them: [case], or [] with no form of CEX-4.

    Spec: DGR-5, DGR-6.
    """
    found = opening_case(info_string(node.get("own_text", "")))
    return [found[0]] if found else []


def expected_line(node):
    """The expected line of a fragment with expect=syntax-error, else None.

    Spec: DGR-6 (Terms: Expected line), DGR-13.
    """
    found = opening_case(info_string(node.get("own_text", "")))
    return found[1] if found else None


def container_column(tree, node):
    """The column where the container of a code block starts its content.

    The span of a block starts at its container's content column, so the
    bytes before it on its first line are at the end of the part of the
    parent's own text that comes before the block.

    Spec: DGR-6.
    """
    parent = tree.nodes.get(node.get("parent"))
    if parent is None:
        return 0
    siblings = tree.children.get(parent["id"], [])
    before = sum(s["end"] - s["start"] for s in siblings if s["end"] <= node["start"])
    position = (node["start"] - parent["start"]) - before
    own = parent.get("own_text", "").encode("utf-8")
    if position < 0 or position > len(own):
        return 0
    prefix = own[own.rfind(b"\n", 0, position) + 1:position].decode("utf-8", "replace")
    return len(prefix) if prefix.strip() == "" else 0


def strip_columns(line, columns):
    """Remove up to the given number of columns of leading blanks.

    Spec: DGR-6.
    """
    column = 0
    index = 0
    while index < len(line) and column < columns and line[index] in BLANKS:
        if line[index] == "\t":
            if (column // 4 + 1) * 4 > columns:
                break
            column = (column // 4 + 1) * 4
        else:
            column += 1
        index += 1
    return line[index:]


def fence_indent(tree, node):
    """The indentation of the fence of a code block, in columns: its container's and its own.

    Spec: DGR-6.
    """
    return container_column(tree, node) + len(opening_match(node["own_text"]).group(1).expandtabs(4))


def fragment_lines(tree, node):
    """The lines of a fragment as it is, its opening line and closing fence included, without the indentation of the fence.

    Spec: DGR-6, DGR-14.
    """
    indent = fence_indent(tree, node)
    return [strip_columns(line, indent) for line in node["own_text"].split("\n")]


def case_text(tree, node):
    """The case text of a fragment: its code, without the fences and the indentation of the fence.

    Leading blanks stay as they are (a space in the indentation of a block is
    refused by the indenter, DGR-11, never turned into a tab); blank lines at
    the end are dropped; the text ends with exactly one line break. The
    script never cuts it.

    Spec: DGR-6.
    """
    lines = node["own_text"].split("\n")
    fence = opening_match(node["own_text"]).group(2)
    indent = fence_indent(tree, node)
    body = lines[1:]
    if body and re.match(r"^[ \t]*" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*$", body[-1]):
        body = body[:-1]
    out = [strip_columns(line, indent) for line in body]
    while out and not out[-1].strip(BLANKS):
        out.pop()
    return "\n".join(out) + "\n"


def reject_threshold(text, line):
    """The offset of the line break that ends line `line` - 1 of a case text.

    -1 when the expected line is 1: a failure anywhere passes. When the text
    has no line `line` - 1, the end of the text.

    Spec: DGR-13.
    """
    if line is None or line <= 1:
        return -1
    lines = text.split("\n")
    if line - 1 > len(lines) - 1:
        return len(text)
    return sum(len(l) + 1 for l in lines[: line - 1]) - 1


def reject_ok(text, line, span):
    """True when the place of a failure does not end before the line break that ends the line before the expected one.

    Spec: DGR-13.
    """
    threshold = reject_threshold(text, line)
    start, end = span
    return end > threshold or start >= threshold


# ---------------------------------------------------------------- citations


def check_citation(tree, norm_id, norm_hash, status_by_id=None):
    """What is wrong with one citation, or None when it checks.

    With status_by_id (the grammar), a cited fragment must be derived.

    Spec: DGR-9, DGR-13.
    """
    node = tree.nodes.get(norm_id)
    if node is None:
        return f"{norm_id} is not a norm"
    if node.get("status") != "active":
        return f"{norm_id} is retired"
    if tree.norm_hash(norm_id) != norm_hash:
        return f"{norm_id} has the norm hash {tree.norm_hash(norm_id)}"
    if status_by_id is not None and norm_id in tree.fragment_ids:
        line = status_by_id.get(norm_id)
        if line is None:
            return f"{norm_id} has no status line"
        if line.get("state") != "derived":
            return f"{norm_id} is {line.get('state')}"
    return None


def stale(tree, norm_id, norm_hash):
    """The current norm hash, as a tuple, when a citation no longer matches, else False.

    (None,) means the norm is gone or retired.

    Spec: DGR-12.
    """
    node = tree.nodes.get(norm_id)
    if node is None or node.get("status") != "active":
        return (None,)
    current = tree.norm_hash(norm_id)
    return (current,) if current != norm_hash else False


def script_citations(text):
    """The citations of the code of the script, and the lines that try one and fail.

    Spec: DGR-9, DGR-18.
    """
    found, bad = [], []
    for number, line in enumerate(text.split("\n"), 1):
        if not SCRIPT_CITATION_ATTEMPT_RE.match(line):
            continue
        match = SCRIPT_CITATION_RE.match(line.strip())
        if match:
            found.append((number, match.group(1), match.group(2)))
        else:
            bad.append(number)
    return found, bad


def check_script(tree, text):
    """Problems of the citations in the code of the script.

    Spec: DGR-9, DGR-13.
    """
    problems = []
    found, bad = script_citations(text)
    for number in bad:
        problems.append(("script-citation", f"line {number}", "not a citation"))
    for number, norm_id, norm_hash in found:
        message = check_citation(tree, norm_id, norm_hash)
        if message:
            problems.append(("script-citation", norm_id, f"line {number}: {message}"))
    return problems


def norm_text(tree, node):
    """The text of a norm: its own text, then the text of each active child, one per line.

    Each piece loses its leading and trailing line breaks; an empty one is left out.

    Spec: DGR-18 (Terms: Text of a norm).
    """
    pieces = [node["own_text"].strip("\n")]
    pieces += [norm_text(tree, child) for child in tree.children.get(node["id"], [])]
    return "\n".join(p for p in pieces if p)


def first_words(text, limit=60):
    """The first words of a norm, as the title of a norm without a heading.

    The text loses its leading "#", "-" and blanks and every backtick, and its
    whitespace is collapsed. When it is longer than `limit`, it is cut at the
    last space at or before `limit`; then, while it holds more "(" than ")",
    it is cut before its last "("; then trailing blanks and ",;:-" go.

    Spec: DGR-14, DGR-18 (Terms: First words of a norm).
    """
    words = " ".join((text or "").lstrip("#- \t\n").replace("`", "").split())
    if len(words) > limit:
        cut = words.rfind(" ", 0, limit + 1)
        words = words[:cut] if cut > 0 else words[:limit]
    while words.count("(") > words.count(")"):
        words = words[:words.rfind("(")]
    return words.rstrip(" ,;:-")


def tree_history(root):
    """The versions of data/tree.jsonl in the history of HEAD, newest first, as (commit, Tree), read lazily.

    Spec: DGR-1, DGR-18.
    """
    result = git(root, "log", "--format=%H", "HEAD", "--", TREE_REL)
    if result is None or result.returncode != 0:
        return
    for commit in result.stdout.split():
        shown = git(root, "show", f"{commit}:{TREE_REL}")
        if shown is None or shown.returncode != 0:
            continue
        rows = [v for v, e in (json_object(l) for l in shown.stdout.splitlines() if l.strip()) if not e]
        yield commit, Tree(rows)


def old_norm_text(root, norm_id, norm_hash, cache):
    """The text of a norm at a norm hash, from the newest version of data/tree.jsonl in the history of HEAD that has it.

    Returns (text, commit), or (None, None) when no version has it.

    Spec: DGR-18.
    """
    if "versions" not in cache:
        cache["versions"], cache["source"] = [], tree_history(root)
    index = 0
    while True:
        if index == len(cache["versions"]):
            version = next(cache["source"], None)
            if version is None:
                return None, None
            cache["versions"].append(version)
        commit, old = cache["versions"][index]
        node = old.nodes.get(norm_id)
        if node is not None and old.norm_hash(norm_id) == norm_hash:
            return norm_text(old, node), commit
        index += 1


def stale_script_citations(root, tree, text):
    """The stale citations of the code of the script, one item per cited norm, in the order of the script.

    Each item: "id"; "state" ("changed", "retired" or "gone"); "current_hash"
    and "new_text" (null unless changed); and "citations", one per line that
    cites the norm with a stale hash: "line", "text" (the line without its
    indentation), "cited_hash", "old_text" and "old_commit" (null when no
    version of data/tree.jsonl in the history of HEAD has that hash, or git
    cannot run). A line that tries a citation and is not one is not here.

    Spec: DGR-18.
    """
    lines, items, cache = text.split("\n"), {}, {}
    for number, norm_id, norm_hash in script_citations(text)[0]:
        if not stale(tree, norm_id, norm_hash):
            continue
        if norm_id not in items:
            node = tree.nodes.get(norm_id)
            state = "gone" if node is None else "retired" if node.get("status") != "active" else "changed"
            changed = state == "changed"
            items[norm_id] = {"id": norm_id, "state": state,
                              "current_hash": tree.norm_hash(norm_id) if changed else None,
                              "new_text": norm_text(tree, node) if changed else None, "citations": []}
        old_text, old_commit = old_norm_text(root, norm_id, norm_hash, cache)
        items[norm_id]["citations"].append({"line": number, "text": lines[number - 1].strip(), "cited_hash": norm_hash,
                                            "old_text": old_text, "old_commit": old_commit})
    return list(items.values())


# ---------------------------------------------------------------- the grammar

RULE_HEAD_RE = re.compile(r"^[?!]?([_A-Za-z][_A-Za-z0-9]*)(\{[^}]*\})?(?:\.-?[0-9]+)?[ \t]*:(.*)$")
TOKEN_RE = re.compile(
    r'(?P<str>"(?:\\.|[^"\\\n])*"i?)'
    r"|(?P<comment>//.*)"
    r"|(?P<re>/(?:\\.|[^/\\\n])+/[imslux]*)"
    r"|(?P<arrow>->)"
    r"|(?P<name>[_A-Za-z][_A-Za-z0-9]*)"
    r"|(?P<other>[^\n])"
    r"|(?P<nl>\n)"
)


class Statement:
    """One statement of the grammar: a rule, a terminal or a directive.

    Spec: DGR-8 (Terms: Statement, Key of a statement).
    """

    def __init__(self, line_number, first_line):
        """Start a statement at its first line.

        Spec: DGR-8.
        """
        self.line = line_number
        self.lines = [first_line]
        self.citations = []
        self.refs = set()
        self.defines = set()
        self.strings = []
        self.has_regex = False
        self.inline_comment = False
        head = RULE_HEAD_RE.match(first_line)
        if first_line.startswith("%"):
            self.kind = "directive"
            self.name = None
            self.key = first_line.rstrip()
        elif head:
            self.name = head.group(1)
            self.kind = "terminal" if self.name.lstrip("_")[:1].isupper() else "rule"
            self.key = self.name
        else:
            self.kind = "unknown"
            self.name = None
            self.key = first_line.rstrip()

    def analyse(self):
        """Find the names a statement uses, defines, and its literals.

        Spec: DGR-8, DGR-13.
        """
        text = "\n".join(self.lines)
        params = set()
        if self.kind in ("rule", "terminal"):
            head = RULE_HEAD_RE.match(self.lines[0])
            if head.group(2):
                params = set(re.findall(r"[_A-Za-z][_A-Za-z0-9]*", head.group(2)))
            text = head.group(3) + "\n" + "\n".join(self.lines[1:])
        names = []
        alias = False
        for token in TOKEN_RE.finditer(text):
            kind = token.lastgroup
            if kind == "comment":
                self.inline_comment = True
            elif kind == "str":
                self.strings.append(token.group(0))
            elif kind == "re":
                self.has_regex = True
            elif kind == "arrow":
                alias = True
                continue
            elif kind == "name":
                if not alias:
                    names.append(token.group(0))
            alias = alias and kind == "other" and token.group(0) in BLANKS
        if self.kind == "directive":
            word = names[0] if names else ""
            rest = names[1:]
            if word == "declare":
                self.defines = set(rest)
            elif word == "import":
                self.defines = {rest[-1]} if rest else set()
            else:
                self.refs = set(rest)
        else:
            self.refs = set(names) - params


def parse_grammar(text):
    """Split the grammar into statements, each with the citations just above it.

    Spec: DGR-8, DGR-13.
    """
    statements, problems = [], []
    pending = []
    current = None
    for number, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if not stripped:
            if pending:
                for n, _ in pending:
                    problems.append(("citation", f"line {n}", "a citation not just above a statement"))
                pending = []
            continue
        if stripped.startswith("//"):
            match = GRAMMAR_CITATION_RE.match(line)
            if not match:
                problems.append(("citation", f"line {number}", "not a citation"))
            pending.append((number, match))
            continue
        if line[:1] in BLANKS or line.startswith("|"):
            if current is None:
                problems.append(("statement", f"line {number}", "an indented line outside a statement"))
            else:
                current.lines.append(line)
            for n, _ in pending:
                problems.append(("citation", f"line {n}", f"a citation inside the statement {current.key if current else ''}".rstrip()))
            pending = []
            continue
        current = Statement(number, line)
        current.citations = [(n, m.group(1), m.group(2)) for n, m in pending if m]
        if not pending:
            problems.append(("citation", current.key, "a statement with no citation just above it"))
        pending = []
        statements.append(current)
    for n, _ in pending:
        problems.append(("citation", f"line {n}", "a citation not just above a statement"))
    for statement in statements:
        statement.analyse()
        if statement.kind == "unknown":
            problems.append(("statement", statement.key, "not a rule, a terminal or a directive"))
        if statement.inline_comment:
            problems.append(("citation", statement.key, "a comment that is not on a line of its own"))
    return statements, problems


def bracket_pairs(statements):
    """The OPEN_<X> and CLOSE_<X> terminals, paired, and the unpaired ones.

    Spec: DGR-11.
    """
    names = {s.name for s in statements if s.kind == "terminal"}
    for s in statements:
        names |= {d for d in s.defines if d[:1].isupper()}
    opens = {n[len("OPEN_"):] for n in names if n.startswith("OPEN_")}
    closes = {n[len("CLOSE_"):] for n in names if n.startswith("CLOSE_")}
    paired = sorted(opens & closes)
    problems = [("brackets", f"OPEN_{x}", f"OPEN_{x} has no CLOSE_{x}") for x in sorted(opens - closes)]
    problems += [("brackets", f"CLOSE_{x}", f"CLOSE_{x} has no OPEN_{x}") for x in sorted(closes - opens)]
    return [f"OPEN_{x}" for x in paired], [f"CLOSE_{x}" for x in paired], problems


def check_statements(tree, statements, status_by_id):
    """The checks of the statements that need no Lark.

    Spec: DGR-2, DGR-8, DGR-9, DGR-11, DGR-13.
    """
    problems = []
    seen = {}
    for s in statements:
        if s.key in seen:
            problems.append(("statement", s.key, "defined twice"))
        seen[s.key] = s
        if s.kind == "directive" and s.key.startswith("%import"):
            problems.append(("import", s.key, "the grammar holds %import"))
        cited = set()
        for number, norm_id, norm_hash in s.citations:
            if norm_id in cited:
                problems.append(("citation", s.key, f"line {number}: {norm_id} is cited twice; one citation line per norm"))
            cited.add(norm_id)
            message = check_citation(tree, norm_id, norm_hash, status_by_id)
            if message:
                problems.append(("citation", s.key, f"line {number}: {message}"))
    defined = {s.name: s for s in statements if s.kind in ("rule", "terminal")}
    _, _, bracket_problems = bracket_pairs(statements)
    problems += bracket_problems
    # Usage: reachable from start, the fixed names of DGR-11, or a directive.
    roots = set(FIXED_NAMES)
    for s in statements:
        if s.kind == "directive":
            roots |= s.refs
    reached, todo = set(), [n for n in roots if n in defined]
    while todo:
        name = todo.pop()
        if name in reached:
            continue
        reached.add(name)
        todo += [r for r in defined[name].refs if r in defined and r not in reached]
    for name in defined:
        if name not in reached:
            problems.append(("usage", name, "not used by start, by another statement or by a directive"))

    def cites_fragment(s):
        """True when a statement cites a fragment.

        Spec: DGR-2.
        """
        return any(norm_id in tree.fragment_ids for _, norm_id, _ in s.citations)

    # Source: cites a fragment, or is used by a statement that does.
    grounded = {n for n, s in defined.items() if cites_fragment(s)}
    if "NAME" in defined and "RESERVED" in defined:
        # DGR-11: RESERVED serves NAME, which matches none of its words.
        defined["NAME"].refs.add("RESERVED")
    for s in statements:  # a direct user that cites a fragment grounds the names it uses
        if cites_fragment(s):
            grounded |= {r for r in s.refs if r in defined}
    for name in defined:
        if name not in grounded:
            problems.append(("source", name, "cites no fragment and is not used by a statement that cites one"))
    if "NAME" in defined and "RESERVED" not in defined:
        problems.append(("names", "RESERVED", "the grammar has NAME and no RESERVED"))
    if "RESERVED" in defined and (defined["RESERVED"].has_regex or defined["RESERVED"].refs - {"RESERVED"}):
        problems.append(("names", "RESERVED", "RESERVED lists its words only as string alternatives"))
    return problems


def reserved_words(statement):
    """The words of the terminal RESERVED, from its string alternatives.

    Spec: DGR-11.
    """
    words = []
    for literal in statement.strings:
        body = literal[1:-2] if literal.endswith('"i') else literal[1:-1]
        words.append(re.sub(r"\\(.)", r"\1", body))
    return words


# ---------------------------------------------------------------- Lark


def import_lark():
    """Import Lark; an ImportError is an exit status 2.

    Spec: DGR-13.
    """
    try:
        import interegular  # noqa: F401  (strict needs it)
        import lark
        from lark.indenter import Indenter
    except ImportError as error:
        raise InputError(f"Lark cannot be loaded: {error}")
    return lark, Indenter


class IndentationSpaceError(Exception):
    """A space in the indentation of a line outside brackets: the case does not parse.

    Spec: DGR-11.
    """


def build_parser(text, statements):
    """Build the grammar with Lark: lalr, contextual, start, strict, the indenter.

    Spec: DGR-11, DGR-13.
    """
    lark, Indenter = import_lark()
    opens, closes, _ = bracket_pairs(statements)

    class CleanIndenter(Indenter):
        """The Lark indenter on the fixed names _NL, _INDENT, _DEDENT.

        Spec: DGR-11.
        """

        NL_type = "_NL"
        INDENT_type = "_INDENT"
        DEDENT_type = "_DEDENT"
        OPEN_PAREN_types = opens
        CLOSE_PAREN_types = closes
        # LEX-20@8c358626: each indentation level is exactly one tab character
        tab_len = 1

        def process(self, stream):
            """Remember the last token, to place an error of the indenter.

            Spec: DGR-13.
            """
            def recorded():
                """Pass the tokens on, keeping the last one.

                Spec: DGR-13.
                """
                for token in stream:
                    self.last = token
                    yield token
            self.last = None
            return super().process(recorded())

        def handle_NL(self, token):
            """Refuse a space in the indentation of a line, outside brackets.

            It reads the source after the line break, whatever _NL matches.

            Spec: DGR-11.
            """
            # EXP-27@f74dba8b: inside an open parenthesis a line continues
            if self.paren_level == 0:
                source = getattr(self, "source", "")
                start = (token.start_pos or 0) + token.value.rfind("\n") + 1
                lead = re.match(r"[ \t]*", source[start:]).group(0)
                # LEX-21@7474dff8: mixing tabs and spaces for indentation is not allowed
                if " " in lead:
                    raise IndentationSpaceError(f"a space in the indentation of line {source.count(chr(10), 0, start) + 1}")
            yield from super().handle_NL(token)

    indenter = CleanIndenter()
    parser = lark.Lark(text, parser="lalr", lexer="contextual", start="start", strict=True, postlex=indenter)
    return parser, indenter


def parse_error_span(error, indenter, text):
    """The place of a failure, as start and end offsets in the case text.

    An unexpected token: its span, or the end of the text for the end of
    input; an unexpected character: its position; an error of the indenter:
    the span of the _NL token it handles.

    Spec: DGR-13.
    """
    from lark.exceptions import UnexpectedCharacters, UnexpectedEOF, UnexpectedToken
    if isinstance(error, UnexpectedToken):
        token = error.token
        if token.type == "$END" or token.start_pos is None:
            return len(text), len(text)
        return token.start_pos, token.end_pos if token.end_pos is not None else token.start_pos + 1
    if isinstance(error, UnexpectedCharacters):
        return error.pos_in_stream, error.pos_in_stream + 1
    if isinstance(error, UnexpectedEOF):
        return len(text), len(text)
    token = getattr(indenter, "last", None)
    if token is not None and token.start_pos is not None:
        return token.start_pos, token.end_pos if token.end_pos is not None else token.start_pos + 1
    return 0, 0


def try_parse(parser, indenter, text):
    """Parse a case: None when it parses, else (start, end, message).

    A DedentError or any other error of the indenter is a case that does not parse.

    Spec: DGR-13.
    """
    indenter.source = text
    try:
        parser.parse(text)
        return None
    except Exception as error:  # noqa: BLE001 - every failure is a failed parse
        start, end = parse_error_span(error, indenter, text)
        first = (str(error).strip().split("\n") or [""])[0]
        line = text.count("\n", 0, min(start, len(text))) + 1
        return start, end, f"line {line}: {type(error).__name__}: {first}"


# ---------------------------------------------------------------- the plugin


def plugin_version(plugin_root=None):
    """The version of the .claude-plugin/plugin.json of the plugin; InputError when there is none.

    Spec: DGR-4 (Terms: Plugin version), DGR-13.
    """
    root = plugin_root if plugin_root is not None else PLUGIN_ROOT
    path = root / ".claude-plugin" / "plugin.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise InputError(f"{path}: the plugin.json of the plugin cannot be read: {error}")
    version = value.get("version") if isinstance(value, dict) else None
    if not isinstance(version, str) or not version:
        raise InputError(f"{path}: the plugin has no version in its plugin.json")
    return version


def same_path(a, b):
    """True when two paths name the same folder.

    Spec: DGR-4.
    """
    return os.path.realpath(os.path.expanduser(str(a))) == os.path.realpath(str(b))


def marketplace_commit(plugin_root=None, installed=None):
    """The commit of the marketplace that the plugin was installed from, or "none".

    In this order: the gitCommitSha of the entry of installed_plugins.json
    whose installPath is the plugin's root; else the full sha of HEAD of the
    git checkout that holds the plugin's root; else "none". Never "+dirty".

    Spec: DGR-4 (Terms: Marketplace commit).
    """
    root = plugin_root if plugin_root is not None else PLUGIN_ROOT
    path = installed if installed is not None else INSTALLED_PLUGINS
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = None
    plugins = data.get("plugins") if isinstance(data, dict) else None
    if isinstance(plugins, dict):
        for entries in plugins.values():
            for entry in entries if isinstance(entries, list) else []:
                if not isinstance(entry, dict) or not isinstance(entry.get("installPath"), str):
                    continue
                sha = entry.get("gitCommitSha")
                if same_path(entry["installPath"], root) and isinstance(sha, str) and COMMIT_RE.fullmatch(sha):
                    return sha
    result = git(root, "rev-parse", "--verify", "--quiet", "HEAD^{commit}")
    if result is not None and result.returncode == 0 and COMMIT_RE.fullmatch(result.stdout.strip()):
        return result.stdout.strip()
    return "none"


# ---------------------------------------------------------------- status


def read_status(path):
    """The lines of the status file, as (number, text, object or None, what is wrong).

    Spec: DGR-5, DGR-13.
    """
    out = []
    for number, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        line = line.rstrip("\r")
        if not line.strip():
            continue
        value, error = json_object(line)
        out.append((number, line, value, error))
    return out


def git(root, *args):
    """Run git in a folder, with literal paths; the CompletedProcess, or None when git cannot run.

    Spec: DGR-4, DGR-18.
    """
    try:
        return subprocess.run(["git", "-C", str(root), "--literal-pathspecs", *args], capture_output=True, text=True)
    except OSError:
        return None


def sha256(data):
    """The hex SHA-256 of bytes.

    Spec: DGR-4.
    """
    return hashlib.sha256(data).hexdigest()


def body_bytes(status_text):
    """The bytes of the status file after its first line.

    Spec: DGR-4.
    """
    _, _, rest = status_text.partition("\n")
    return rest.encode("utf-8")


# ---------------------------------------------------------------- commands


def previous_status(root):
    """The fragment lines of the status file of the previous run, or None when it is taken as absent.

    It is absent when the file does not exist, or when its meta line has no
    field "generator", as the local skill /derive-grammar wrote it.

    Spec: DGR-12.
    """
    path = root / STATUS_REL
    if not path.is_file():
        return None
    rows = load_jsonl(path, "status")
    meta = next((r for r in rows if r.get("type") == "meta"), None)
    if meta is not None and "generator" not in meta:
        return None
    return [r for r in rows if r.get("type") == "fragment"]


def worklist(root):
    """The items that a change calls for, one JSON object each.

    Spec: DGR-12.
    """
    tree = load_tree(root)
    lines = previous_status(root)
    absent = lines is None
    lines = lines or []
    by_id = {}
    for line in lines:
        if isinstance(line.get("id"), str):
            by_id.setdefault(line["id"], line)
    items = []
    for node in tree.fragments:
        norm_id = node["id"]
        new_hash = tree.norm_hash(norm_id)
        cases = case_kinds(node)
        old = by_id.get(norm_id)
        item = {"kind": None, "id": norm_id, "old_hash": None, "new_hash": new_hash, "cases": cases, "file": node.get("file")}
        if old is None:
            item["kind"] = "new"
        else:
            item["old_hash"] = old.get("hash")
            reason = old.get("reason") if isinstance(old.get("reason"), str) else ""
            moved = any(stale(tree, i, h) for i, h in INLINE_CITATION_RE.findall(reason))
            if old.get("hash") != new_hash or old.get("cases") != cases or moved:
                item["kind"] = "changed"
        if item["kind"]:
            items.append(item)
    for line in lines:
        if isinstance(line.get("id"), str) and line["id"] not in tree.fragment_ids:
            node = tree.nodes.get(line["id"])
            items.append({"kind": "gone", "id": line["id"], "old_hash": line.get("hash"), "new_hash": None,
                          "cases": line.get("cases"), "file": node.get("file") if node else None})
    grammar_path = root / GRAMMAR_REL
    if not absent and grammar_path.is_file():
        statements, _ = parse_grammar(grammar_path.read_text(encoding="utf-8"))
        for s in statements:
            for _, norm_id, norm_hash in s.citations:
                change = stale(tree, norm_id, norm_hash)
                if change:
                    items.append({"kind": "norm", "statement": s.key, "old_hash": norm_hash, "new_hash": change[0],
                                  "citation": f"{norm_id}@{norm_hash}"})
    return items


def seal(root, model, plugin_root=None, installed=None):
    """Order the fragment lines as data/tree.jsonl and write the meta line first.

    model is the exact model ID the deriver runs as; seal records it as
    given, and check judges it. A missing status file is taken as one with no
    fragment line. Every input is read before anything is written.

    Spec: DGR-4, DGR-5, DGR-17.
    """
    tree = load_tree(root)
    grammar_path, status_path = root / GRAMMAR_REL, root / STATUS_REL
    if not grammar_path.is_file():
        raise InputError(f"{grammar_path} does not exist")
    version = plugin_version(plugin_root)
    fragments = []
    if status_path.is_file():
        for number, line, value, error in read_status(status_path):
            if value is None:
                raise InputError(f"status {status_path}:{number}: {error}")
            if value.get("type") != "meta":
                fragments.append((line, value))
    end = len(tree.order)
    fragments.sort(key=lambda f: tree.order.get(f[1].get("id"), end))
    body = "".join(line + "\n" for line, _ in fragments)
    meta = {
        "type": "meta",
        "specs_commit": tree.specs_commit,
        "generator": {"plugin": PLUGIN_NAME, "version": version,
                      "marketplace_commit": marketplace_commit(plugin_root, installed)},
        "model": model,
        "grammar_sha256": sha256(grammar_path.read_bytes()),
        "status_sha256": sha256(body.encode("utf-8")),
    }
    head = json.dumps(meta, ensure_ascii=False, separators=(",", ":"))
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(head + "\n" + body, encoding="utf-8")
    return head


def valid_cases(cases):
    """True when the cases of a status line are a list of one, accept or reject, or the empty list.

    Spec: DGR-5.
    """
    return isinstance(cases, list) and len(cases) <= 1 and all(c in CASES for c in cases)


def check_status(tree, status_path, rows):
    """The checks of the fragment lines of the status file.

    Spec: DGR-5, DGR-6, DGR-9, DGR-13.
    """
    problems = []
    by_id, counts, order = {}, {}, []
    for index, (number, line, value, error) in enumerate(rows):
        where = f"{status_path}:{number}"
        if value is None:
            problems.append(("status", where, error))
            continue
        if value.get("type") == "meta":
            if index > 0:
                problems.append(("meta", where, "a meta line that is not the first line"))
            continue
        if list(value) != FRAGMENT_KEYS or value.get("type") != "fragment":
            missing = [k for k in FRAGMENT_KEYS if k not in value]
            what = f"lacks the fields {', '.join(missing)}" if missing else f"does not have exactly the fields {', '.join(FRAGMENT_KEYS)}, in that order"
            problems.append(("status", where, what))
            if missing:
                continue
        norm_id = value["id"]
        if not isinstance(norm_id, str):
            problems.append(("status", where, "id is not a string"))
            continue
        counts[norm_id] = counts.get(norm_id, 0) + 1
        by_id.setdefault(norm_id, value)
        order.append(norm_id)
        state, reason, issue = value["state"], value["reason"], value["issue"]
        if not valid_cases(value["cases"]):
            problems.append(("status", norm_id, f"cases {json.dumps(value['cases'])} is not a list of one, accept or reject, or the empty list"))
        if state not in STATES:
            problems.append(("status", norm_id, f"state {state!r} is not derived or pending"))
        if not isinstance(value["hash"], str) or not re.fullmatch(r"[0-9a-f]{8}", value["hash"]):
            problems.append(("status", norm_id, "hash is not 8 hex digits"))
        if state == "derived" and reason is not None:
            problems.append(("status", norm_id, "a derived fragment has a reason"))
        if state != "derived" and not (isinstance(reason, str) and reason.strip()):
            problems.append(("status", norm_id, f"a {state} fragment has no reason"))
        if state != "pending" and issue is not None:
            problems.append(("status", norm_id, "an issue on a fragment that is not pending"))
        if state == "pending" and issue is not None and not (isinstance(issue, str) and ISSUE_RE.fullmatch(issue)):
            problems.append(("status", norm_id, "the issue is not an issue URL of the foundation"))
        if isinstance(reason, str):
            for cited, cited_hash in INLINE_CITATION_RE.findall(reason):
                message = check_citation(tree, cited, cited_hash)
                if message:
                    problems.append(("reason-citation", norm_id, message))
    problems += check_unique_issues(rows)
    for norm_id, count in counts.items():
        if norm_id not in tree.fragment_ids:
            problems.append(("status", norm_id, "a status line of a norm that is not a fragment"))
        elif count > 1:
            problems.append(("status", norm_id, f"{count} status lines"))
    known = [i for i in order if i in tree.fragment_ids]
    if known != sorted(known, key=lambda i: tree.order[i]):
        problems.append(("status", str(status_path), "the fragment lines do not follow the order of data/tree.jsonl"))
    for node in tree.fragments:
        norm_id = node["id"]
        line = by_id.get(norm_id)
        if line is None:
            problems.append(("status", norm_id, "no status line"))
            continue
        if line["hash"] != tree.norm_hash(norm_id):
            problems.append(("status", norm_id, f"the status line holds the hash {line['hash']}; the norm hash is {tree.norm_hash(norm_id)}"))
        cases = case_kinds(node)
        if line["cases"] != cases:
            problems.append(("status", norm_id, f"the status line holds the cases {json.dumps(line['cases'])}; the script gives {json.dumps(cases)}"))
        reason = line["reason"] if isinstance(line["reason"], str) else ""
        if not cases and line["state"] != "pending":
            problems.append(("opening line", norm_id, f"{NO_FORM_REASON}, and its state is {line['state']}, not pending"))
        if line["state"] == "pending":
            problems.append(("pending", norm_id, f"pending: {reason}"))
            if cases and not INLINE_CITATION_RE.search(reason):
                problems.append(("pending", norm_id, "the reason cites no norm"))
    return problems, by_id


def check_unique_issues(rows):
    """No two status lines hold the same issue URL: an issue belongs to one fragment.

    A null issue is never compared. Each line that repeats a URL is reported
    by its ID, naming the ID of the first line that holds it.

    Spec: DGR-5, DGR-13, DGR-14.
    """
    problems, holder = [], {}
    for _, _, value, _ in rows:
        if not isinstance(value, dict) or value.get("type") != "fragment":
            continue
        norm_id, issue = value.get("id"), value.get("issue")
        if not isinstance(norm_id, str) or not isinstance(issue, str):
            continue
        if issue in holder:
            problems.append(("issue", norm_id, f"holds the issue {issue}, which {holder[issue]} holds too; one issue per fragment"))
        else:
            holder[issue] = norm_id
    return problems


def check_meta(tree, root, status_path, rows, version):
    """The meta line: first, its six fields, the specs commit, the generator, the model and the hashes.

    Spec: DGR-4, DGR-13, DGR-17.
    """
    where = str(status_path)
    if not rows:
        return [("meta", where, "the status file has no meta line")]
    number, _, meta, _ = rows[0]
    if meta is None:
        return []  # check_status reports a first line that is not JSON
    if meta.get("type") != "meta":
        return [("meta", f"{where}:{number}", "the first line is not the meta line")]
    problems = []
    if list(meta) != META_KEYS:
        problems.append(("meta", f"{where}:{number}", f"the meta line does not have exactly the fields {', '.join(META_KEYS)}, in that order"))
    if meta.get("specs_commit") != tree.specs_commit:
        problems.append(("meta", "specs_commit", f"{meta.get('specs_commit')}; data/tree.jsonl has {tree.specs_commit}"))
    problems += check_generator(meta, version)
    problems += check_model(meta)
    if meta.get("grammar_sha256") != sha256((root / GRAMMAR_REL).read_bytes()):
        problems.append(("meta", "grammar_sha256", "the grammar does not match the hash of its meta line: changed after the last seal"))
    if meta.get("status_sha256") != sha256(body_bytes(status_path.read_text(encoding="utf-8"))):
        problems.append(("meta", "status_sha256", "the status file does not match the hash of its meta line: changed after the last seal"))
    return problems


def check_generator(meta, version):
    """The generator of the meta line names this plugin and its version; its marketplace commit is not judged.

    Spec: DGR-4, DGR-13.
    """
    if "generator" not in meta:
        return [("meta", "generator", "the meta line has no generator")]
    generator = meta["generator"]
    if not isinstance(generator, dict):
        return [("meta", "generator", f"{generator!r} is not an object")]
    problems = []
    if list(generator) != GENERATOR_KEYS:
        problems.append(("meta", "generator", f"the generator does not have exactly the fields {', '.join(GENERATOR_KEYS)}, in that order"))
    if generator.get("plugin") != PLUGIN_NAME:
        problems.append(("meta", "generator", f"the meta line names the plugin {generator.get('plugin')!r}; check runs from the plugin {PLUGIN_NAME!r}"))
    if generator.get("version") != version:
        problems.append(("meta", "generator", f"the meta line names the version {generator.get('version')!r}; check runs from the version {version!r}"))
    return problems


def check_model(meta):
    """The model of the meta line: present, a non-empty string of the form of a model ID.

    check cannot know that the model is the one that derived; it checks only the form.

    Spec: DGR-4, DGR-13.
    """
    if "model" not in meta:
        return [("meta", "model", "the meta line records no model")]
    model = meta["model"]
    if not isinstance(model, str) or not model:
        return [("meta", "model", f"{model!r} is not a non-empty string")]
    if not MODEL_RE.fullmatch(model):
        return [("meta", "model", f"{model!r} holds a character that is not a letter, a digit, '.', '-' or '_'")]
    return []


def check_layout(folder):
    """specs-derived/grammar/ holds exactly the grammar and the status file.

    Spec: DGR-3.
    """
    expected = {Path(GRAMMAR_REL).name, Path(STATUS_REL).name}
    return [("layout", str(folder / p.name), "a file that is not the grammar or the status file")
            for p in sorted(folder.iterdir()) if p.name not in expected]


def check_names(parser, statements):
    """NAME matches no word of RESERVED.

    Spec: DGR-11.
    """
    reserved = next((s for s in statements if s.name == "RESERVED"), None)
    terminals = {t.name: t for t in parser.terminals}
    if reserved is None or "NAME" not in terminals:
        return []
    pattern = re.compile(terminals["NAME"].pattern.to_regexp())
    return [("names", "NAME", f"NAME matches the reserved word {w!r}") for w in reserved_words(reserved) if pattern.fullmatch(w)]


def check(root, script_path, plugin_root=None):
    """Every check of DGR-13; returns the problems and the counts.

    With no fragment in data/tree.jsonl, it does not build the grammar and
    checks only the meta line and the citations of the script.

    Spec: DGR-13.
    """
    tree = load_tree(root)
    grammar_path, status_path = root / GRAMMAR_REL, root / STATUS_REL
    for path in (grammar_path, status_path):
        if not path.is_file():
            raise InputError(f"{path} does not exist")
    import_lark()
    version = plugin_version(plugin_root)
    rows = read_status(status_path)
    script_problems = check_script(tree, script_path.read_text(encoding="utf-8"))
    counts = {state: 0 for state in STATES}
    parsed = {"accept": [0, 0], "reject": [0, 0]}
    if not tree.fragments:
        problems = [("status", f"{status_path}:{n}", e) for n, _, v, e in rows[:1] if v is None]
        problems += check_meta(tree, root, status_path, rows, version) + script_problems
        return problems, {"states": counts, "parsed": parsed}
    grammar = grammar_path.read_text(encoding="utf-8")
    problems = check_layout(grammar_path.parent)
    problems += check_meta(tree, root, status_path, rows, version)
    status_problems, by_id = check_status(tree, status_path, rows)
    problems += status_problems
    statements, grammar_problems = parse_grammar(grammar)
    problems += grammar_problems
    problems += check_statements(tree, statements, by_id)
    problems += script_problems
    cited = {norm_id for s in statements for _, norm_id, _ in s.citations}
    for norm_id, line in by_id.items():
        if norm_id in tree.fragment_ids and isinstance(line.get("state"), str) and line["state"] in counts:
            counts[line["state"]] += 1
    for node in tree.fragments:
        line = by_id.get(node["id"])
        if line and line.get("state") == "derived" and node["id"] not in cited:
            problems.append(("cited", node["id"], "derived, and no statement cites it"))
    try:
        parser, indenter = build_parser(grammar, statements)
    except Exception as error:  # noqa: BLE001 - every build error fails the check
        first = (str(error).strip().split("\n") or [""])[0]
        problems.append(("build", str(grammar_path), f"{type(error).__name__}: {first}"))
        parser = None
    if parser is not None:
        problems += check_names(parser, statements)
        for node in tree.fragments:
            line = by_id.get(node["id"])
            cases = case_kinds(node)
            if not line or line.get("state") != "derived" or not cases:
                continue
            name, case, text = node["id"], cases[0], case_text(tree, node)
            failure = try_parse(parser, indenter, text)
            parsed[case][1] += 1
            if case == "accept":
                if failure is None:
                    parsed[case][0] += 1
                else:
                    problems.append(("accept", name, f"does not parse: {failure[2]}"))
            elif failure is None:
                problems.append(("reject", name, "parses, and its case is reject"))
            elif not reject_ok(text, expected_line(node), failure[:2]):
                problems.append(("reject", name, f"fails before the line break that ends the line before its expected line {expected_line(node)}: {failure[2]}"))
            else:
                parsed[case][0] += 1
    return problems, {"states": counts, "parsed": parsed}


def main(argv=None):
    """The command line: worklist, seal --model <model ID>, check, stale-citations.

    The root of the repository of layer 2 is the working directory. seal
    without --model exits with 2 and writes nothing.

    Spec: DGR-4, DGR-12, DGR-13, DGR-17, DGR-18.
    """
    parser = argparse.ArgumentParser(prog="derive_grammar.py", description="The deterministic part of /clean-derived-norms:derive-grammar.")
    parser.add_argument("command", choices=["worklist", "seal", "check", "stale-citations"])
    parser.add_argument("--model", help="seal only, and required there: the exact model ID the deriver runs as, such as claude-opus-5-5")
    args = parser.parse_args(argv)
    root = Path.cwd()
    if args.command == "seal" and args.model is None:
        print("error: seal needs --model <model ID>, the exact model ID the deriver runs as", file=sys.stderr)
        return 2
    script = Path(__file__).resolve()
    try:
        if args.command == "worklist":
            for item in worklist(root):
                print(json.dumps(item, ensure_ascii=False))
            return 0
        if args.command == "seal":
            print(seal(root, args.model))
            return 0
        if args.command == "stale-citations":
            for item in stale_script_citations(root, load_tree(root), script.read_text(encoding="utf-8")):
                print(json.dumps(item, ensure_ascii=False))
            return 0
        problems, summary = check(root, script)
    except InputError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    for name, subject, message in problems:
        print(f"{name}: {subject}: {message}")
    states, parsed = summary["states"], summary["parsed"]
    print(
        f"fragments: {states['derived']} derived, {states['pending']} pending; "
        f"accept parsed {parsed['accept'][0]}/{parsed['accept'][1]}; "
        f"reject rejected {parsed['reject'][0]}/{parsed['reject'][1]}; "
        f"problems: {len(problems)}"
    )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
