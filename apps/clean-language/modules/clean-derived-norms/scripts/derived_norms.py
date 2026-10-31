#!/usr/bin/env python3
"""The module script of the plugin clean-derived-norms: the code that the scripts of its use cases share.

The scripts of the use cases derive-grammar and derive-semantics import it
(CDN-7); it is not run on its own. It holds the reading of data/tree.jsonl,
the fragments, their case text and the files of their program, the
citations in the code of a script, the plugin and the parts of a header line
that every status file has, the parser of the grammar with its indenter, and
the list of derived norms of a type, which knows no type.

Spec: specs/module.md (CDN-7, CDN-8) of the plugin, and the rules of
use-cases/derive-grammar/specs/derive-grammar.md (DGR) that each function cites.
"""

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

TREE_REL = "data/tree.jsonl"
GRAMMAR_REL = "specs-derived/grammar/clean.lark"
COMMIT_RE = re.compile(r"[0-9a-f]{40}")

# The plugin that holds the module script: the folder above the module script's
# folder, scripts/ (DGR-4, Terms: Plugin version).
PLUGIN_NAME = "clean-derived-norms"
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
# The module script itself, a file of the code of the script of derive-grammar (DGR, Terms: Code of the script).
MODULE_SCRIPT = Path(__file__).resolve()
# The record of the installed plugins of Claude Code (DGR-4, Terms: Tooling commit).
INSTALLED_PLUGINS = Path.home() / ".claude" / "plugins" / "installed_plugins.json"

GENERATOR_KEYS = ["plugin", "version", "tooling_commit"]
# NRM-5: the "type" of the header line of a status file; "meta" is that of a status file written before the
# header line was named so, read as "header" and never written.
TYPES_OF_HEADER_LINE_OF_STATUS_FILE = ("header", "meta")
# NRM-12: the "kind" of the header line of a list of derived norms; "meta" is that of a list written before the
# header line was named so, read as "header" and never written.
KINDS_OF_HEADER_LINE_OF_LIST_OF_DERIVED_NORMS = ("header", "meta")
# The model of the header line (DGR-4, Terms: Model ID).
MODEL_RE = re.compile(r"[A-Za-z0-9._-]+")
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
# The error code of the forms of the opening line (CEX-4): ^[A-Z]{3,6}[0-9]{3}$.
# The prefix of the code is not checked (DGR-6).
CODE = r"[A-Z]{3,6}[0-9]{3}"
NO_FORM_REASON = "the opening line is none of the forms of CEX-4"
# A file line starts at column 1 with "// file:"; its path follows "// file: " (CDN-6,
# DGR-19, Terms: File line, path of a file line).
FILE_LINE_START = "// file:"
FILE_PATH_START = "// file: "


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
        self.header = next((r for r in rows if r.get("type") == "meta"), {})
        # The commit of layer 1: "specs_commit", or "foundation_commit" in an older tree (DGR-4).
        self.specs_commit = self.header.get("specs_commit") or self.header.get("foundation_commit")
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


class ProgramFile:
    """One file of the program of a case text: its number, the path of its file line, its offset, its first line and its file text.

    path_of_file_line is None when the file has no path; file_line is False only for the
    one file of a case text that holds no file line.

    Spec: DGR-19.
    """

    def __init__(self, number_of_file, path_of_file_line, offset_of_file, first_line_in_case_text, file_text, file_line):
        """Hold the facts of one file.

        Spec: DGR-19.
        """
        self.number_of_file = number_of_file
        self.path_of_file_line = path_of_file_line
        self.offset_of_file = offset_of_file
        self.first_line_in_case_text = first_line_in_case_text
        self.file_text = file_text
        self.file_line = file_line


def program_files(text):
    """The files of the program of a case text, split from its file lines alone, in their order.

    Each file runs from its file line to the line before the next one, or to
    the last line; its file text is those lines, each followed by one line
    feed, without the blank lines at its end. The lines before the first file
    line belong to no file. A case text with no file line is one file with no
    path: the whole case text, at offset 0.

    Spec: DGR-19.
    """
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    starts = [index for index, line in enumerate(lines) if line.startswith(FILE_LINE_START)]
    if not starts:
        return [ProgramFile(1, None, 0, 1, text, False)]
    offsets, position = [], 0
    for line in lines:
        offsets.append(position)
        position += len(line) + 1
    files = []
    for number, start in enumerate(starts, 1):
        end = starts[number] if number < len(starts) else len(lines)
        body = lines[start:end]
        while len(body) > 1 and not body[-1].strip(BLANKS):
            body.pop()
        head = lines[start]
        path = head[len(FILE_PATH_START):] if head.startswith(FILE_PATH_START) else None
        files.append(ProgramFile(number, path, offsets[start], start + 1, "\n".join(body) + "\n", True))
    return files


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


def plugin_path(path):
    """The path of a file in the plugin, such as scripts/derived_norms.py; a file outside the plugin keeps its full path.

    Spec: DGR-9, DGR-18 (Terms: Code of the script).
    """
    full = Path(path).resolve()
    try:
        return full.relative_to(PLUGIN_ROOT).as_posix()
    except ValueError:
        return str(full)


def read_code_of_the_script(*paths):
    """The code of a script: (path of the file in the plugin, text) of each of its files, in the order given.

    Spec: DGR-9, DGR-18 (Terms: Code of the script), DSM-17, CDN-7.
    """
    return [(plugin_path(path), Path(path).read_text(encoding="utf-8")) for path in paths]


def check_script(tree, code_of_the_script):
    """Problems of the citations in the code of the script, each line named by the path of its file and its number.

    code_of_the_script: [(path of the file in the plugin, text)], as
    read_code_of_the_script gives it.

    Spec: DGR-9, DGR-13.
    """
    problems = []
    for path, text in code_of_the_script:
        found, bad = script_citations(text)
        for number in bad:
            problems.append(("script-citation", f"{path} line {number}", "not a citation"))
        for number, norm_id, norm_hash in found:
            message = check_citation(tree, norm_id, norm_hash)
            if message:
                problems.append(("script-citation", norm_id, f"{path} line {number}: {message}"))
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


def stale_script_citations(root, tree, code_of_the_script):
    """The stale citations of the code of the script, one item per cited norm, in the order of its files and of their lines.

    code_of_the_script: [(path of the file in the plugin, text)], as
    read_code_of_the_script gives it. Each item: "id"; "state" ("changed",
    "retired" or "gone"); "current_hash" and "new_text" (null unless
    changed); and "citations", one per line that cites the norm with a stale
    hash: "path" (of its file in the plugin), "line" (its number in that
    file), "text" (the line without its indentation), "cited_hash",
    "old_text" and "old_commit" (null when no version of data/tree.jsonl in
    the history of HEAD has that hash, or git cannot run). A line that tries
    a citation and is not one is not here.

    Spec: DGR-18.
    """
    items, cache = {}, {}
    for path, text in code_of_the_script:
        lines = text.split("\n")
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
            items[norm_id]["citations"].append({"path": path, "line": number, "text": lines[number - 1].strip(),
                                                "cited_hash": norm_hash, "old_text": old_text, "old_commit": old_commit})
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
        # The lines of the derived norm that the statement is (DGR-20): from the
        # first comment line just above it, set by parse_grammar, to its last line.
        self.derived_norm_first_line = line_number
        self.derived_norm_last_line = line_number
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
                current.derived_norm_last_line = number
            for n, _ in pending:
                problems.append(("citation", f"line {n}", f"a citation inside the statement {current.key if current else ''}".rstrip()))
            pending = []
            continue
        current = Statement(number, line)
        current.citations = [(n, m.group(1), m.group(2)) for n, m in pending if m]
        if pending:
            current.derived_norm_first_line = pending[0][0]
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


def build_parser(text, statements, keep_all_tokens=False):
    """Build the grammar with Lark: lalr, contextual, start, strict, the indenter.

    keep_all_tokens is the one option that derive-semantics adds, so that its
    tree keeps every token (DSM-7); derive-grammar leaves it False, the
    default of Lark.

    Spec: DGR-11, DGR-13, DSM-7.
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
    parser = lark.Lark(text, parser="lalr", lexer="contextual", start="start", strict=True, postlex=indenter,
                       keep_all_tokens=keep_all_tokens)
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


def parse_program(parser, indenter, text):
    """Parse the files of the program of a case text alone, in their order, up to the first that does not parse.

    Returns (files, trees, None) when every file parses, else (files, None,
    (start, end, message)), the place of the failure moved by the offset of
    its file into the case text. A DedentError or any other error of the
    indenter is a file that does not parse.

    Spec: DGR-13, DGR-19.
    """
    files = program_files(text)
    trees = []
    for file in files:
        indenter.source = file.file_text
        try:
            trees.append(parser.parse(file.file_text))
        except Exception as error:  # noqa: BLE001 - every failure is a failed parse
            start, end = parse_error_span(error, indenter, file.file_text)
            return files, None, (file.offset_of_file + start, file.offset_of_file + end, failure_message(file, start, error))
    return files, trees, None


def failure_message(file, start, error):
    """The message of a failure: "line <n>: ...", and, with a file line, the file and its line.

    <n> counts the lines of the whole case text.

    Spec: DGR-13, DGR-19.
    """
    first = (str(error).strip().split("\n") or [""])[0]
    line_in_file = file.file_text.count("\n", 0, min(start, len(file.file_text))) + 1
    line = file.first_line_in_case_text + line_in_file - 1
    if not file.file_line:
        return f"line {line}: {type(error).__name__}: {first}"
    path = file.path_of_file_line if file.path_of_file_line is not None else "no path"
    return f"line {line} (file {file.number_of_file}, {path}, line {line_in_file}): {type(error).__name__}: {first}"


# ---------------------------------------------------------------- the plugin


def plugin_version(plugin_root):
    """The version of the .claude-plugin/plugin.json of the plugin; InputError when there is none.

    Spec: DGR-4 (Terms: Plugin version), DGR-13.
    """
    path = plugin_root / ".claude-plugin" / "plugin.json"
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


def tooling_commit(plugin_root, installed_plugins):
    """The commit of the tooling repository, the marketplace that the plugin was installed from, or "none" (NRM-5).

    In this order: the gitCommitSha of the entry of installed_plugins.json
    whose installPath is the plugin's root; else the full sha of HEAD of the
    git checkout that holds the plugin's root; else "none". Never "+dirty".

    Spec: DGR-4 (Terms: Tooling commit).
    """
    try:
        data = json.loads(Path(installed_plugins).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = None
    plugins = data.get("plugins") if isinstance(data, dict) else None
    if isinstance(plugins, dict):
        for entries in plugins.values():
            for entry in entries if isinstance(entries, list) else []:
                if not isinstance(entry, dict) or not isinstance(entry.get("installPath"), str):
                    continue
                sha = entry.get("gitCommitSha")
                if same_path(entry["installPath"], plugin_root) and isinstance(sha, str) and COMMIT_RE.fullmatch(sha):
                    return sha
    result = git(plugin_root, "rev-parse", "--verify", "--quiet", "HEAD^{commit}")
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


def git(root, *args, text=True):
    """Run git in a folder, with literal paths; the CompletedProcess, or None when git cannot run.

    With text False, its output is bytes, which git() never decodes.

    Spec: DGR-4, DGR-18, DGR-20.
    """
    try:
        return subprocess.run(["git", "-C", str(root), "--literal-pathspecs", *args], capture_output=True, text=text)
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


# ---------------------------------------------------------------- the status lines and the header line


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


def version_of_generator_in_status(rows):
    """The "version" of "generator" in the header line of a status file, or None when there is none.

    rows: the JSON objects of the lines of the status file. The header line is
    the first object whose "type" is "header", or "meta" in a status file
    written before the header line was named so (NRM-5).

    Spec: CDN-7, DGR-12, DSM-12 (NRM-7).
    """
    header = next((r for r in rows if r.get("type") in TYPES_OF_HEADER_LINE_OF_STATUS_FILE), None)
    generator = header.get("generator") if header is not None else None
    version = generator.get("version") if isinstance(generator, dict) else None
    return version if isinstance(version, str) else None


def check_generator(header, version):
    """The generator of the header line names this plugin and its version; its tooling commit is not judged.

    Spec: DGR-4, DGR-13.
    """
    if "generator" not in header:
        return [("header", "generator", "the header line has no generator")]
    generator = header["generator"]
    if not isinstance(generator, dict):
        return [("header", "generator", f"{generator!r} is not an object")]
    problems = []
    if list(generator) != GENERATOR_KEYS:
        problems.append(("header", "generator", f"the generator does not have exactly the fields {', '.join(GENERATOR_KEYS)}, in that order"))
    if generator.get("plugin") != PLUGIN_NAME:
        problems.append(("header", "generator", f"the header line names the plugin {generator.get('plugin')!r}; check runs from the plugin {PLUGIN_NAME!r}"))
    if generator.get("version") != version:
        problems.append(("header", "generator", f"the header line names the version {generator.get('version')!r}; check runs from the version {version!r}"))
    return problems


def check_model(header):
    """The model of the header line: present, a non-empty string of the form of a model ID.

    check cannot know that the model is the one that derived; it checks only the form.

    Spec: DGR-4, DGR-13.
    """
    if "model" not in header:
        return [("header", "model", "the header line records no model")]
    model = header["model"]
    if not isinstance(model, str) or not model:
        return [("header", "model", f"{model!r} is not a non-empty string")]
    if not MODEL_RE.fullmatch(model):
        return [("header", "model", f"{model!r} holds a character that is not a letter, a digit, '.', '-' or '_'")]
    return []


# ---------------------------------------------------------------- the list of derived norms (NRM-12 to NRM-15)

LIST_OF_DERIVED_NORMS_FILE_NAME = "derived-norms.jsonl"
HEADER_LINE_OF_LIST_OF_DERIVED_NORMS_KEYS = ["kind", "type", "last_derived_norm_number"]
DERIVED_NORM_KEYS = ["kind", "derived_norm_id", "derived_norm_fingerprint", "name", "path", "first_line", "last_line",
                     "cited_norms"]
CITED_NORM_KEYS = ["norm_id", "norm_hash"]
NORM_HASH_RE = re.compile(r"[0-9a-f]{8}")
DERIVED_NORM_FINGERPRINT_RE = re.compile(r"[0-9a-f]{8}")
NORM_ID_RE = re.compile(NORM_ID)
# Characters a name never holds (NRM-12): control characters (Cc), the line and paragraph separators.
NAME_FORBIDDEN_RE = re.compile("[\x00-\x1f\x7f-\x9f\u2028\u2029]")


class DerivedNorm:
    """One derived norm of the output, as the files of the output give it.

    cited_norms: [(norm ID, norm hash)], in the order of the norm IDs.

    Spec: CDN-7, DGR-20, DSM-18.
    """

    def __init__(self, name, path, first_line, last_line, cited_norms, derived_norm_fingerprint):
        """A derived norm with its place, its cited norms and its derived norm fingerprint.

        Spec: DGR-20.
        """
        self.name = name
        self.path = path
        self.first_line = first_line
        self.last_line = last_line
        self.cited_norms = cited_norms
        self.derived_norm_fingerprint = derived_norm_fingerprint


def output_file_lines(data):
    """The lines of a file of the output, as step 1 of NRM-14 splits them: UTF-8, CRLF as LF, split at each LF.

    Spec: CDN-7, DGR-20 (NRM-14).
    """
    return data.decode("utf-8").replace("\r\n", "\n").split("\n")


def derived_norm_lines(lines, first_line, last_line):
    """The lines of a derived norm, from first_line to last_line, without the blanks at their end (NRM-14 step 2).

    Spec: DGR-20.
    """
    return [line.rstrip(BLANKS) for line in lines[first_line - 1:last_line]]


def cited_norms_of_lines(lines, first_line, last_line, citation_re):
    """The norms that the citation lines of a derived norm cite: [(norm ID, norm hash)], sorted, each pair once.

    Spec: DGR-20, DSM-18.
    """
    cited = set()
    for line in derived_norm_lines(lines, first_line, last_line):
        match = citation_re.match(line)
        if match:
            cited.add((match.group(1), match.group(2)))
    return sorted(cited)


def derived_norm_fingerprint(lines, first_line, last_line, citation_re, cited_norms):
    """The derived norm fingerprint of NRM-14, from the lines of the file and the cited norms.

    Spec: DGR-20 (NRM-14).
    """
    content = [line for line in derived_norm_lines(lines, first_line, last_line) if not citation_re.match(line)]
    while content and content[0] == "":
        content.pop(0)
    while content and content[-1] == "":
        content.pop()
    text = "".join(f"{norm_id}@{norm_hash}\n" for norm_id, norm_hash in cited_norms) + "\n"
    text += "".join(line + "\n" for line in content)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


def name_of_derived_norm(key):
    """The name of a derived norm: the key of its item, each character that NRM-12 forbids in a name replaced by one space.

    Spec: CDN-10, DGR-20, DSM-18.
    """
    return NAME_FORBIDDEN_RE.sub(" ", key)


def derived_norm(lines, key, path, first_line, last_line, citation_re):
    """A derived norm of a file of the output, named from the key of its item, with its cited norms and its derived norm fingerprint.

    Spec: CDN-10, DGR-20, DSM-18.
    """
    cited = cited_norms_of_lines(lines, first_line, last_line, citation_re)
    return DerivedNorm(name_of_derived_norm(key), path, first_line, last_line, cited,
                       derived_norm_fingerprint(lines, first_line, last_line, citation_re, cited))


def derived_norm_number(type_of_derived_norms, derived_norm_id):
    """The number of a derived norm ID of the type, or None when it is not of the form <type>:<n>.

    Spec: DGR-20 (NRM-13).
    """
    if not isinstance(derived_norm_id, str):
        return None
    match = re.fullmatch(re.escape(type_of_derived_norms) + r":([1-9][0-9]*)", derived_norm_id)
    return int(match.group(1)) if match else None


def read_list_of_derived_norms(data, type_of_derived_norms, where):
    """The last_derived_norm_number and the derived norm lines of a list, from its bytes.

    InputError, naming the list and the line, when a line is not UTF-8 or not
    a JSON object (an empty line or a line of only blanks is none), or the
    first line is not a header line of the type with a last_derived_norm_number
    that is an integer, 0 or greater. Only the empty text after the line feed
    that ends the list is no line.

    Spec: CDN-8, DGR-20 (A list that cannot be read).
    """
    rows = []
    raw_lines = data.split(b"\n")
    if raw_lines[-1] == b"":
        raw_lines.pop()
    for number, raw in enumerate(raw_lines, 1):
        try:
            line = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise InputError(f"{where}:{number}: not UTF-8") from None
        value, error = json_object(line)
        if value is None:
            raise InputError(f"{where}:{number}: {error}")
        rows.append((number, value))
    if not rows:
        raise InputError(f"{where}: no header line")
    number, header = rows[0]
    last_derived_norm_number = header.get("last_derived_norm_number")
    if (header.get("kind") not in KINDS_OF_HEADER_LINE_OF_LIST_OF_DERIVED_NORMS or header.get("type") != type_of_derived_norms
            or not isinstance(last_derived_norm_number, int) or isinstance(last_derived_norm_number, bool) or last_derived_norm_number < 0):
        raise InputError(f"{where}:{number}: not a header line with the type {type_of_derived_norms} and a last_derived_norm_number")
    return last_derived_norm_number, [value for _, value in rows[1:]]


def default_branch(root):
    """The default branch of the repository of layer 2: the branch of refs/remotes/origin/HEAD, or else the branch HEAD names.

    InputError when git cannot run, the folder is not in a git work tree,
    or HEAD names no branch and there is no refs/remotes/origin/HEAD.

    Spec: CDN-9.
    """
    inside = git(root, "rev-parse", "--is-inside-work-tree")
    if inside is None:
        raise InputError("git cannot run, so the list before the run cannot be read (CDN-9)")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        raise InputError(f"{root} is not in a git work tree, so the list before the run cannot be read (CDN-9)")
    origin = git(root, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    if origin is not None and origin.returncode == 0 and origin.stdout.strip().startswith("origin/"):
        return origin.stdout.strip()[len("origin/"):]
    head = git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    if head is None or head.returncode != 0 or not head.stdout.strip():
        raise InputError("HEAD names no branch and there is no refs/remotes/origin/HEAD, so the default branch, "
                         "and the list before the run, cannot be told (CDN-9)")
    return head.stdout.strip()


def bytes_of_list_before_the_run(root, path_of_list_of_derived_norms):
    """The list before the run, as (its bytes, where it was read), or (None, where) when there is none.

    Read with git at the head of the default branch, never from the working
    tree. None only when that commit does not hold the list, or the repository
    has no commit yet; InputError in every other case where git cannot give it.

    Spec: CDN-9 (Terms: List before the run), DGR-20.
    """
    branch = default_branch(root)
    where = f"{branch}:{path_of_list_of_derived_norms}"
    commit = git(root, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}^{{commit}}")
    if commit is None:
        raise InputError("git cannot run, so the list before the run cannot be read (CDN-9)")
    if commit.returncode != 0:
        any_commit = git(root, "rev-list", "-n", "1", "--all")
        if any_commit is not None and any_commit.returncode == 0 and not any_commit.stdout.strip():
            return None, where
        raise InputError(f"the default branch {branch} has no commit in this repository, so the list before the run cannot be read (CDN-9)")
    commit = commit.stdout.strip()
    blob = git(root, "rev-parse", "--verify", "--quiet", f"{commit}:./{path_of_list_of_derived_norms}")
    if blob is None:
        raise InputError("git cannot run, so the list before the run cannot be read (CDN-9)")
    if blob.returncode != 0:
        return None, where
    shown = git(root, "cat-file", "blob", blob.stdout.strip(), text=False)
    if shown is None or shown.returncode != 0:
        error = shown.stderr.decode("utf-8", "replace").strip() if shown is not None else "git cannot run"
        raise InputError(f"{where}: git cannot give the list before the run: {error} (CDN-9)")
    return shown.stdout, where


def read_list_before_the_run(root, path_of_list_of_derived_norms, type_of_derived_norms):
    """The list before the run that seal gives the derived norm IDs from, as (last_derived_norm_number, derived norm lines), or None.

    seal never reads the list in the working tree. InputError when the list
    before the run cannot be read.

    Spec: CDN-8, CDN-9, DGR-20.
    """
    bytes_of_list, where = bytes_of_list_before_the_run(root, path_of_list_of_derived_norms)
    if bytes_of_list is None:
        return None
    return read_list_of_derived_norms(bytes_of_list, type_of_derived_norms, where)


def numbers_of_derived_norm_ids_by_name(type_of_derived_norms, entries):
    """The numbers of the derived norm IDs that each name holds in a list, in ascending order.

    A line whose derived norm ID is not of the form of the type, or whose
    name is not a string, gives none.

    Spec: CDN-8, DGR-20 (NRM-13).
    """
    numbers_by_name = {}
    for entry in entries:
        number_of_derived_norm_id = derived_norm_number(type_of_derived_norms, entry.get("derived_norm_id"))
        if number_of_derived_norm_id is not None and isinstance(entry.get("name"), str):
            numbers_by_name.setdefault(entry["name"], []).append(number_of_derived_norm_id)
    return {name: sorted(set(numbers)) for name, numbers in numbers_by_name.items()}


def give_derived_norm_ids(type_of_derived_norms, list_before_the_run, found):
    """The last_derived_norm_number and the lines of the list of derived norms, in the order of their numbers.

    list_before_the_run: (last_derived_norm_number, derived norm lines), or
    None when there is none. The k-th derived norm of a name, in the order
    of NRM-13, takes the k-th derived norm ID of that name there, in the
    ascending order of their numbers; one beyond them gets a new one, in
    that order.

    Spec: CDN-8, DGR-20 (NRM-13).
    """
    last_derived_norm_number, numbers_by_name = 0, {}
    if list_before_the_run is not None:
        last_derived_norm_number, entries = list_before_the_run
        for entry in entries:
            number_of_derived_norm_id = derived_norm_number(type_of_derived_norms, entry.get("derived_norm_id"))
            if number_of_derived_norm_id is not None:
                last_derived_norm_number = max(last_derived_norm_number, number_of_derived_norm_id)
        numbers_by_name = numbers_of_derived_norm_ids_by_name(type_of_derived_norms, entries)
    count_of_derived_norms_of_name, entries = {}, []
    for item in sorted(found, key=lambda d: (d.path, d.first_line)):
        position_in_name = count_of_derived_norms_of_name.get(item.name, 0)
        count_of_derived_norms_of_name[item.name] = position_in_name + 1
        numbers_of_name = numbers_by_name.get(item.name, [])
        if position_in_name < len(numbers_of_name):
            number_of_derived_norm_id = numbers_of_name[position_in_name]
        else:
            last_derived_norm_number += 1
            number_of_derived_norm_id = last_derived_norm_number
        entries.append((number_of_derived_norm_id, {
            "kind": "derived_norm", "derived_norm_id": f"{type_of_derived_norms}:{number_of_derived_norm_id}",
            "derived_norm_fingerprint": item.derived_norm_fingerprint, "name": item.name, "path": item.path,
            "first_line": item.first_line, "last_line": item.last_line,
            "cited_norms": [{"norm_id": i, "norm_hash": h} for i, h in item.cited_norms]}))
    entries.sort(key=lambda e: e[0])
    return last_derived_norm_number, [entry for _, entry in entries]


def text_of_list_of_derived_norms(type_of_derived_norms, last_derived_norm_number, entries):
    """The text of the list of derived norms: the header line, then one line per derived norm.

    Spec: DGR-20 (NRM-12).
    """
    header = {"kind": "header", "type": type_of_derived_norms, "last_derived_norm_number": last_derived_norm_number}
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in [header] + entries)


def seal_derived_norms(root, path_of_list_of_derived_norms, type_of_derived_norms, found):
    """The text of the list of derived norms that seal writes, from the derived norms found and the list before the run.

    Reads the list before the run before it writes nothing; InputError when it cannot be read.

    Spec: CDN-8, DGR-20, DSM-18.
    """
    last_derived_norm_number, entries = give_derived_norm_ids(type_of_derived_norms, read_list_before_the_run(root, path_of_list_of_derived_norms, type_of_derived_norms), found)
    return text_of_list_of_derived_norms(type_of_derived_norms, last_derived_norm_number, entries)


def is_whole_number(value, low):
    """True when a JSON value is an integer, not a boolean, and not lower than low.

    Spec: DGR-20.
    """
    return isinstance(value, int) and not isinstance(value, bool) and value >= low


def check_derived_norm_fields(type_of_derived_norms, last_derived_norm_number, number, entry):
    """The problems of the fields of one derived norm line, as (subject, what is wrong), and whether its place can be compared.

    Its place can be compared when it has exactly its fields, its derived
    norm ID is of the form of the type, its name and its path are strings,
    and its lines are line numbers.

    Spec: DGR-20 (The check of the list, NRM-12).
    """
    where = f"{LIST_OF_DERIVED_NORMS_FILE_NAME}:{number}"
    if list(entry) != DERIVED_NORM_KEYS or entry.get("kind") != "derived_norm":
        return [(where, f"does not have exactly the fields {', '.join(DERIVED_NORM_KEYS)}, in that order, with kind derived_norm")], False
    derived_norm_id = entry["derived_norm_id"]
    number_of_derived_norm_id = derived_norm_number(type_of_derived_norms, derived_norm_id)
    if number_of_derived_norm_id is None:
        return [(where, f"{json.dumps(derived_norm_id)} is not a derived norm ID {type_of_derived_norms}:<n>")], False
    problems, comparable = [], True
    if number_of_derived_norm_id > last_derived_norm_number:
        problems.append((where, f"{derived_norm_id} has a number greater than last_derived_norm_number {last_derived_norm_number}"))
    derived_norm_fingerprint = entry["derived_norm_fingerprint"]
    if not (isinstance(derived_norm_fingerprint, str) and DERIVED_NORM_FINGERPRINT_RE.fullmatch(derived_norm_fingerprint)):
        problems.append((derived_norm_id, f"the derived norm fingerprint {json.dumps(derived_norm_fingerprint)} is not 8 hex digits in lower case"))
    name = entry["name"]
    if not isinstance(name, str):
        problems.append((derived_norm_id, f"the name {json.dumps(name, ensure_ascii=False)} is not a string"))
        comparable = False
    elif not (name.strip(BLANKS) and not NAME_FORBIDDEN_RE.search(name)):
        problems.append((derived_norm_id, f"the name {json.dumps(name, ensure_ascii=False)} is empty, only blanks, or holds a control character or a line or paragraph separator"))
    if not isinstance(entry["path"], str):
        problems.append((derived_norm_id, "the path is not a string"))
        comparable = False
    first_line, last_line = entry["first_line"], entry["last_line"]
    if not (is_whole_number(first_line, 1) and is_whole_number(last_line, 1) and first_line <= last_line):
        problems.append((derived_norm_id, f"first_line {json.dumps(first_line)} and last_line {json.dumps(last_line)} are not line numbers from 1 with first_line not greater than last_line"))
        comparable = False
    cited = entry["cited_norms"]
    good = isinstance(cited, list) and bool(cited) and all(
        isinstance(c, dict) and list(c) == CITED_NORM_KEYS and isinstance(c["norm_id"], str)
        and NORM_ID_RE.fullmatch(c["norm_id"]) and isinstance(c["norm_hash"], str) and NORM_HASH_RE.fullmatch(c["norm_hash"])
        for c in cited)
    if good:
        cited_norm_ids = [c["norm_id"] for c in cited]
        good = cited_norm_ids == sorted(cited_norm_ids) and len(set(cited_norm_ids)) == len(cited_norm_ids)
    if not good:
        problems.append((derived_norm_id, "cited_norms is not a list of at least one object with exactly norm_id and norm_hash, in the order of the norm IDs, with no norm ID twice"))
    return problems, comparable


def json_object_with_each_field_once(line):
    """One line of the list of derived norms as (object, None), or (None, what is wrong): not JSON, not a JSON object, or a field given twice.

    Spec: DGR-20 (The check of the list).
    """
    def each_field_once(pairs):
        """The object of the pairs; FieldGivenTwice when a name is given twice.

        Spec: DGR-20 (The check of the list).
        """
        names = [name for name, _ in pairs]
        twice = sorted({name for name in names if names.count(name) > 1})
        if twice:
            raise FieldGivenTwice(twice[0])
        return dict(pairs)

    try:
        value = json.loads(line, object_pairs_hook=each_field_once)
    except FieldGivenTwice as error:
        return None, f"the field {json.dumps(str(error.args[0]), ensure_ascii=False)} is given twice"
    except json.JSONDecodeError:
        return None, "not JSON"
    if not isinstance(value, dict):
        return None, "not a JSON object"
    return value, None


class FieldGivenTwice(Exception):
    """A JSON object of the list of derived norms that gives one field twice.

    Spec: DGR-20 (The check of the list).
    """


def read_list_for_check(data, type_of_derived_norms):
    """The rows of the list of derived norms that check reads, and the problems of its bytes, its lines and its header line.

    The rows are None when a line is not a JSON object or the header line does
    not check: then no derived norm of the list is compared with the output.

    Spec: DGR-20 (The check of the list).
    """
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None, [(LIST_OF_DERIVED_NORMS_FILE_NAME, "the list is not UTF-8")]
    problems = []
    if text.startswith("\ufeff"):
        problems.append((LIST_OF_DERIVED_NORMS_FILE_NAME, "the list starts with a byte order mark"))
        text = text[1:]
    if not text.endswith("\n"):
        problems.append((LIST_OF_DERIVED_NORMS_FILE_NAME, "the list does not end with a line feed"))
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    rows, broken = [], False
    for number, line in enumerate(lines, 1):
        if not line:
            problems.append((f"{LIST_OF_DERIVED_NORMS_FILE_NAME}:{number}", "an empty line"))
            continue
        if "\r" in line:
            problems.append((f"{LIST_OF_DERIVED_NORMS_FILE_NAME}:{number}", "the line holds a carriage return"))
        value, error = json_object_with_each_field_once(line)
        if value is None:
            problems.append((f"{LIST_OF_DERIVED_NORMS_FILE_NAME}:{number}", f"not a JSON object: {error}"))
            broken = True
        else:
            rows.append((number, value))
    if broken:
        return None, problems
    if not rows:
        return None, problems + [(LIST_OF_DERIVED_NORMS_FILE_NAME, "the list has no header line")]
    number, header = rows[0]
    if (list(header) != HEADER_LINE_OF_LIST_OF_DERIVED_NORMS_KEYS or header.get("kind") not in KINDS_OF_HEADER_LINE_OF_LIST_OF_DERIVED_NORMS
            or header.get("type") != type_of_derived_norms or not is_whole_number(header.get("last_derived_norm_number"), 0)):
        return None, problems + [(f"{LIST_OF_DERIVED_NORMS_FILE_NAME}:{number}", f"not the header line of the type {type_of_derived_norms}: exactly kind header, type {type_of_derived_norms} and last_derived_norm_number, an integer, 0 or greater, in that order")]
    return rows, problems


def check_list_of_derived_norms(root, path_of_list_of_derived_norms, type_of_derived_norms, found):
    """Every check of the list of derived norms: NRM-12 to NRM-14, the output, and the list before the run.

    found: the derived norms of the output (DerivedNorm), each with the
    derived norm fingerprint of NRM-14. Returns [("derived-norms", subject, what)].

    Spec: DGR-13, DGR-20 (The check of the list), DSM-18.
    """
    rows, problems = read_list_for_check((root / path_of_list_of_derived_norms).read_bytes(), type_of_derived_norms)
    if rows is None:
        return [("derived-norms", s, m) for s, m in problems]
    line_number_of_header_line, header = rows[0]
    last_derived_norm_number = header["last_derived_norm_number"]
    entries, previous_number, derived_norm_ids_seen, lines_taken = [], 0, set(), {}
    for number, entry in rows[1:]:
        fields, comparable = check_derived_norm_fields(type_of_derived_norms, last_derived_norm_number, number, entry)
        problems += fields
        if not comparable:
            continue
        derived_norm_id, path = entry["derived_norm_id"], entry["path"]
        number_of_derived_norm_id = derived_norm_number(type_of_derived_norms, derived_norm_id)
        if derived_norm_id in derived_norm_ids_seen:
            problems.append((derived_norm_id, "the list holds this derived norm ID twice"))
        elif number_of_derived_norm_id < previous_number:
            problems.append((derived_norm_id, "the lines are not in the ascending order of the numbers of their derived norm IDs"))
        derived_norm_ids_seen.add(derived_norm_id)
        previous_number = max(previous_number, number_of_derived_norm_id)
        taken = lines_taken.setdefault(path, {})
        span = range(entry["first_line"], entry["last_line"] + 1)
        shared = sorted({taken[n] for n in span if n in taken})
        if shared:
            problems.append((derived_norm_id, f"has a line in common with {', '.join(shared)} in {path}"))
        for n in span:
            taken.setdefault(n, derived_norm_id)
        entries.append(entry)
    by_place = {(d.name, d.path, d.first_line, d.last_line): d for d in found}
    listed = set()
    for entry in entries:
        place = (entry["name"], entry["path"], entry["first_line"], entry["last_line"])
        derived_norm_id = entry["derived_norm_id"]
        item = by_place.get(place)
        if item is None:
            problems.append((derived_norm_id, f"names {json.dumps(entry['name'], ensure_ascii=False)} at {entry['path']} lines {entry['first_line']} to {entry['last_line']}, which is no derived norm of the output"))
            continue
        listed.add(place)
        cited = entry["cited_norms"]
        cited = [(c.get("norm_id"), c.get("norm_hash")) for c in cited if isinstance(c, dict)] if isinstance(cited, list) else []
        if cited != item.cited_norms:
            problems.append((derived_norm_id, "cited_norms are not the norms that its citation lines cite: "
                             + (", ".join(f"{i}@{h}" for i, h in item.cited_norms) or "none")))
        elif entry["derived_norm_fingerprint"] != item.derived_norm_fingerprint:
            problems.append((derived_norm_id, f"the derived norm fingerprint {entry['derived_norm_fingerprint']} is not the one that NRM-14 computes, {item.derived_norm_fingerprint}"))
    for place, item in by_place.items():
        if place not in listed:
            problems.append((item.name, f"a derived norm of {item.path} lines {item.first_line} to {item.last_line} that the list does not hold"))
    problems += check_against_the_list_before_the_run(root, path_of_list_of_derived_norms, type_of_derived_norms, last_derived_norm_number, line_number_of_header_line, entries)
    return [("derived-norms", s, m) for s, m in problems]


def check_against_the_list_before_the_run(root, path_of_list_of_derived_norms, type_of_derived_norms, last_derived_norm_number, line_number_of_header_line, entries):
    """No derived norm ID given again or moved to another derived norm, compared with the list before the run.

    Nothing to check when there is no list before the run; a list before
    the run that cannot be read is the one problem reported.

    Spec: CDN-9, DGR-20 (The check of the list, NRM-13).
    """
    try:
        list_before_the_run = read_list_before_the_run(root, path_of_list_of_derived_norms, type_of_derived_norms)
    except InputError as error:
        return [(LIST_OF_DERIVED_NORMS_FILE_NAME, f"the list before the run cannot be read: {error}; the derived norm IDs are not checked against it (NRM-13)")]
    if list_before_the_run is None:
        return []
    last_derived_norm_number_before_the_run, derived_norms_before_the_run = list_before_the_run
    problems = []
    if last_derived_norm_number < last_derived_norm_number_before_the_run:
        problems.append((f"{LIST_OF_DERIVED_NORMS_FILE_NAME}:{line_number_of_header_line}", f"last_derived_norm_number {last_derived_norm_number} is lower than {last_derived_norm_number_before_the_run}, the one of the list before the run"))
    name_before_the_run = {}
    for entry in derived_norms_before_the_run:
        if derived_norm_number(type_of_derived_norms, entry.get("derived_norm_id")) is not None:
            name_before_the_run[entry["derived_norm_id"]] = entry.get("name")
    entries_of_name = {}
    for entry in entries:
        derived_norm_id = entry["derived_norm_id"]
        entries_of_name.setdefault(entry["name"], []).append(entry)
        if derived_norm_id in name_before_the_run:
            if name_before_the_run[derived_norm_id] != entry["name"]:
                problems.append((derived_norm_id, f"names {json.dumps(entry['name'], ensure_ascii=False)}; the list before the run gives it to {json.dumps(name_before_the_run[derived_norm_id], ensure_ascii=False)}: a derived norm ID never moves to another derived norm"))
        elif derived_norm_number(type_of_derived_norms, derived_norm_id) <= last_derived_norm_number_before_the_run:
            problems.append((derived_norm_id, f"is not in the list before the run, and its number is not greater than {last_derived_norm_number_before_the_run}, its last_derived_norm_number: a derived norm ID is never given again"))
    for name, numbers_before_the_run in numbers_of_derived_norm_ids_by_name(type_of_derived_norms, derived_norms_before_the_run).items():
        if name not in entries_of_name:
            continue
        derived_norm_ids_in_order = [e["derived_norm_id"] for e in sorted(entries_of_name[name], key=lambda e: (e["path"], e["first_line"]))]
        derived_norm_ids_before_the_run = [f"{type_of_derived_norms}:{n}" for n in numbers_before_the_run]
        paired = min(len(derived_norm_ids_in_order), len(derived_norm_ids_before_the_run))
        if derived_norm_ids_in_order[:paired] != derived_norm_ids_before_the_run[:paired]:
            problems.append((name, f"had the derived norm IDs {', '.join(derived_norm_ids_before_the_run)} before the run, and the list gives {', '.join(derived_norm_ids_in_order)} to its derived norms in the order of NRM-13: the k-th derived norm of a name keeps the k-th derived norm ID of that name (CDN-8)"))
    return problems

