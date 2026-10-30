#!/usr/bin/env python3
"""The deterministic part of the use case derive-grammar of the plugin clean-derived-norms.

Run from the root of the repository of layer 2, the working directory, as:
    uv run --with "lark[interegular]" python3 -I -B <this script> <command>
Commands: worklist, seal --model <model ID>, check, stale-citations. The
script never writes a statement of the grammar and never decides the state of a
fragment.

Spec: use-cases/derive-grammar/specs/derive-grammar.md (DGR) of the plugin.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# The module script, scripts/derived_norms.py of the plugin, which this script imports (CDN-7).
MODULE_SCRIPT_FOLDER = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(MODULE_SCRIPT_FOLDER))
sys.dont_write_bytecode = True

from derived_norms import (  # noqa: E402
    CODE, GRAMMAR_CITATION_RE, GRAMMAR_REL, INLINE_CITATION_RE, INSTALLED_PLUGINS, ISSUE_RE,
    LIST_OF_DERIVED_NORMS_FILE_NAME, MODULE_SCRIPT, NO_FORM_REASON, PLUGIN_NAME, PLUGIN_ROOT, InputError, body_bytes,
    bracket_pairs, build_parser, case_text, check_citation, check_generator, check_list_of_derived_norms, check_model,
    check_script, check_unique_issues, derived_norm, import_lark, info_string, load_jsonl, load_tree,
    marketplace_commit, output_file_lines, parse_grammar, parse_program, plugin_version, read_code_of_the_script,
    read_status, seal_derived_norms, sha256, stale, stale_script_citations, version_of_generator_in_status,
)

STATUS_REL = "specs-derived/grammar/clean-language-code-examples-status.jsonl"
# The list of derived norms of the type grammar (DGR-20, NRM-12).
TYPE_OF_DERIVED_NORMS = "grammar"
PATH_OF_LIST_OF_DERIVED_NORMS = "specs-derived/grammar/" + LIST_OF_DERIVED_NORMS_FILE_NAME

META_KEYS = ["type", "specs_commit", "generator", "model", "grammar_sha256", "derived_norms_sha256", "status_sha256"]
FRAGMENT_KEYS = ["type", "id", "hash", "cases", "state", "reason", "issue"]
STATES = ("derived", "pending")
CASES = ("accept", "reject")

# The forms of the opening line (CEX-4), with an error code ^[A-Z]{3,6}[0-9]{3}$
# and a line number with no leading zero. The prefix of the code is not checked (DGR-6).
OPENING_FORMS = (
    (re.compile(r"clean-language expect=valid"), "accept"),
    (re.compile(r"clean-language expect=syntax-error code=" + CODE + r" line=(0|[1-9][0-9]*)"), "reject"),
    (re.compile(r"clean-language expect=error code=" + CODE), "accept"),
)
FIXED_NAMES = ("start", "_NL", "_INDENT", "_DEDENT", "NAME", "RESERVED")



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


# ---------------------------------------------------------------- the grammar


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


def grammar_derived_norms(data):
    """The derived norms of the grammar: one per statement, its key as its name, from its first comment line to its last line.

    data: the bytes of the grammar. A line that is no statement is no derived
    norm. InputError when the grammar is not UTF-8.

    Spec: DGR-20.
    """
    try:
        lines = output_file_lines(data)
    except UnicodeDecodeError as error:
        raise InputError(f"{GRAMMAR_REL} is not UTF-8: {error}") from error
    statements, _ = parse_grammar("\n".join(lines))
    return [derived_norm(lines, s.key, GRAMMAR_REL, s.derived_norm_first_line, s.derived_norm_last_line, GRAMMAR_CITATION_RE)
            for s in statements if s.kind != "unknown"]


# ---------------------------------------------------------------- Lark


def try_parse(parser, indenter, text):
    """Parse the program of a case: None when every file parses, else (start, end, message) in the case text.

    Spec: DGR-13, DGR-19.
    """
    _, _, failure = parse_program(parser, indenter, text)
    return failure


# ---------------------------------------------------------------- commands


def previous_status(root):
    """The lines of the status file of the previous run, or None when it is taken as absent.

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
    return rows


def worklist(root, plugin_root=None):
    """The items that a change calls for, one JSON object each.

    A new version of the plugin (the meta line of the status file names
    another version of the generator, or none) makes every fragment with a
    status line "changed" and every statement an item "version" (NRM-7).

    Spec: DGR-12.
    """
    tree = load_tree(root)
    version_of_plugin = plugin_version(plugin_root if plugin_root is not None else PLUGIN_ROOT)
    rows = previous_status(root)
    absent = rows is None
    rows = rows or []
    version_of_generator_in_status_file = version_of_generator_in_status(rows)
    plugin_version_changed = not absent and version_of_generator_in_status_file != version_of_plugin
    lines = [r for r in rows if r.get("type") == "fragment"]
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
            if plugin_version_changed or old.get("hash") != new_hash or old.get("cases") != cases or moved:
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
        if plugin_version_changed:
            items += [{"kind": "version", "statement": s.key, "old_version": version_of_generator_in_status_file, "new_version": version_of_plugin}
                      for s in statements if s.kind != "unknown"]
    return items


def seal(root, model, plugin_root=None, installed=None):
    """Write the list of derived norms, order the fragment lines as data/tree.jsonl and write the meta line first.

    model is the exact model ID the deriver runs as; seal records it as
    given, and check judges it. A missing status file is taken as one with no
    fragment line. Every input is read before anything is written.

    Spec: DGR-4, DGR-5, DGR-17, DGR-20.
    """
    tree = load_tree(root)
    plugin_root = plugin_root if plugin_root is not None else PLUGIN_ROOT
    installed = installed if installed is not None else INSTALLED_PLUGINS
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
    grammar = grammar_path.read_bytes()
    text_of_the_list_of_derived_norms = seal_derived_norms(root, PATH_OF_LIST_OF_DERIVED_NORMS, TYPE_OF_DERIVED_NORMS, grammar_derived_norms(grammar))
    meta = {
        "type": "meta",
        "specs_commit": tree.specs_commit,
        "generator": {"plugin": PLUGIN_NAME, "version": version,
                      "marketplace_commit": marketplace_commit(plugin_root, installed)},
        "model": model,
        "grammar_sha256": sha256(grammar),
        "derived_norms_sha256": sha256(text_of_the_list_of_derived_norms.encode("utf-8")),
        "status_sha256": sha256(body.encode("utf-8")),
    }
    head = json.dumps(meta, ensure_ascii=False, separators=(",", ":"))
    status_path.parent.mkdir(parents=True, exist_ok=True)
    (root / PATH_OF_LIST_OF_DERIVED_NORMS).write_bytes(text_of_the_list_of_derived_norms.encode("utf-8"))
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


def check_meta(tree, root, status_path, rows, version):
    """The meta line: first, its seven fields, the specs commit, the generator, the model and the hashes.

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
    if meta.get("derived_norms_sha256") != sha256((root / PATH_OF_LIST_OF_DERIVED_NORMS).read_bytes()):
        problems.append(("meta", "derived_norms_sha256", "the list of derived norms does not match the hash of its meta line: changed after the last seal"))
    if meta.get("status_sha256") != sha256(body_bytes(status_path.read_text(encoding="utf-8"))):
        problems.append(("meta", "status_sha256", "the status file does not match the hash of its meta line: changed after the last seal"))
    return problems


def check_layout(folder):
    """specs-derived/grammar/ holds exactly the grammar, the list of derived norms and the status file.

    Spec: DGR-3.
    """
    expected = {Path(GRAMMAR_REL).name, LIST_OF_DERIVED_NORMS_FILE_NAME, Path(STATUS_REL).name}
    return [("layout", str(folder / p.name), "a file that is not the grammar, the list of derived norms or the status file")
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


def check(root, code_of_the_script, plugin_root=None):
    """Every check of DGR-13; returns the problems and the counts.

    code_of_the_script: [(path of the file in the plugin, text)], as
    read_code_of_the_script gives it. With no fragment in data/tree.jsonl, it
    does not build the grammar and checks only the meta line and the
    citations of the code of the script.

    Spec: DGR-13.
    """
    tree = load_tree(root)
    grammar_path, status_path = root / GRAMMAR_REL, root / STATUS_REL
    for path in (grammar_path, status_path, root / PATH_OF_LIST_OF_DERIVED_NORMS):
        if not path.is_file():
            raise InputError(f"{path} does not exist")
    import_lark()
    version = plugin_version(plugin_root if plugin_root is not None else PLUGIN_ROOT)
    rows = read_status(status_path)
    script_problems = check_script(tree, code_of_the_script)
    list_problems = check_list_of_derived_norms(root, PATH_OF_LIST_OF_DERIVED_NORMS, TYPE_OF_DERIVED_NORMS,
                                             grammar_derived_norms(grammar_path.read_bytes()))
    counts = {state: 0 for state in STATES}
    parsed = {"accept": [0, 0], "reject": [0, 0]}
    if not tree.fragments:
        problems = [("status", f"{status_path}:{n}", e) for n, _, v, e in rows[:1] if v is None]
        problems += check_meta(tree, root, status_path, rows, version) + list_problems + script_problems
        return problems, {"states": counts, "parsed": parsed}
    grammar = grammar_path.read_text(encoding="utf-8")
    problems = check_layout(grammar_path.parent)
    problems += check_meta(tree, root, status_path, rows, version)
    status_problems, by_id = check_status(tree, status_path, rows)
    problems += status_problems
    statements, grammar_problems = parse_grammar(grammar)
    problems += grammar_problems
    problems += check_statements(tree, statements, by_id)
    problems += list_problems
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

    Spec: DGR-4, DGR-12, DGR-13, DGR-17, DGR-18, DGR-20.
    """
    parser = argparse.ArgumentParser(prog="derive_grammar.py", description="The deterministic part of /clean-derived-norms:derive-grammar.")
    parser.add_argument("command", choices=["worklist", "seal", "check", "stale-citations"])
    parser.add_argument("--model", help="seal only, and required there: the exact model ID the deriver runs as, such as claude-opus-5-5")
    args = parser.parse_args(argv)
    root = Path.cwd()
    if args.command == "seal" and args.model is None:
        print("error: seal needs --model <model ID>, the exact model ID the deriver runs as", file=sys.stderr)
        return 2
    code_of_the_script = read_code_of_the_script(Path(__file__), MODULE_SCRIPT)
    try:
        if args.command == "worklist":
            for item in worklist(root):
                print(json.dumps(item, ensure_ascii=False))
            return 0
        if args.command == "seal":
            print(seal(root, args.model))
            return 0
        if args.command == "stale-citations":
            for item in stale_script_citations(root, load_tree(root), code_of_the_script):
                print(json.dumps(item, ensure_ascii=False))
            return 0
        problems, summary = check(root, code_of_the_script)
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
