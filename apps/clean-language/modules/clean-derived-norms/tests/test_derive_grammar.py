"""Tests of use-cases/derive-grammar/derive_grammar.py, on small fixtures in temporary folders.

Run from the root of the marketplace:
    uv run --with pytest --with "lark[interegular]" python3 -I -B -m pytest -q -p no:cacheprovider \
        apps/clean-language/modules/clean-derived-norms/tests
Spec: use-cases/derive-grammar/specs/derive-grammar.md (DGR). Each test names the clause it checks.
"""

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1]
SCRIPT = MODULE / "use-cases" / "derive-grammar" / "derive_grammar.py"
_spec = importlib.util.spec_from_file_location("derive_grammar", SCRIPT)
dg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dg)
# The module script, which the script imports (CDN-7): the same module as the script's.
sys.path.insert(0, str(MODULE / "scripts"))
import derived_norms  # noqa: E402

# The code of the script: the script and the module script (DGR, Terms: Code of the script).
CODE_OF_THE_SCRIPT = derived_norms.read_code_of_the_script(SCRIPT, derived_norms.MODULE_SCRIPT)

SPECS = "f" * 40
MODEL = "claude-opus-5-5"
VERSION = "0.1.0"
SHA = "a" * 40


# ------------------------------------------------------------------ fixtures


def h8(norm_id, text):
    return hashlib.sha256((norm_id + text).encode()).hexdigest()[:8]


def node(norm_id, kind, own_text, parent="SEC-1", status="active", tree8=None, start=0, end=None, file="specs/a.md"):
    tree8 = tree8 or h8(norm_id, own_text)
    end = start + len(own_text.encode()) if end is None else end
    return {"type": "node", "id": norm_id, "kind": kind, "file": file, "parent": parent, "start": start, "end": end,
            "own_text": own_text, "own_hash": "0" * 64, "tree_hash": tree8 + "0" * 56, "status": status,
            "to_review": False, "changed_since": None}


def fence(info, *lines):
    return f"```{info}\n" + "\n".join(lines) + "\n```"


VALID = "clean-language expect=valid"
ERROR = "clean-language expect=error code=SEM005"


def syntax(line, code="SYN004"):
    return f"clean-language expect=syntax-error code={code} line={line}"


ITEM_PREFIX = "- intro:\n\n  "
TST4 = "```clean-language expect=valid\n  start:\n  \tprint(4)\n  ```"


def base_nodes():
    """A section, an item, fragments, code blocks that are not fragments, and prose norms."""
    return [
        node("SEC-1", "section", "", parent=None),
        node("TST-1", "code_block", fence(VALID, "start:", "\tprint(1)"), start=10),
        node("TST-2", "code_block", fence(syntax(3), "start:", "\tprint(1)", "\tprint 2"), start=100),
        node("TST-3", "code_block", fence(ERROR, "start:", "\tprint(3)"), start=200),
        node("ITM-1", "item", ITEM_PREFIX, start=1000, end=1000 + len(ITEM_PREFIX) + len(TST4)),
        node("TST-4", "code_block", TST4, parent="ITM-1", start=1000 + len(ITEM_PREFIX)),
        node("TST-5", "code_block", fence(VALID, "start:", "\tprint(", "\t\t5)"), start=2000),
        node("OLD-1", "code_block", fence("clean", "start:", "\tprint(6)"), start=3000),
        node("TOM-1", "code_block", "```toml\na = 1\n```", start=4000),
        node("LEX-20", "item", "- one tab per level", tree8="8c358626"),
        node("LEX-21", "item", "- Mixing tabs and spaces for indentation is not allowed", tree8="7474dff8"),
        node("EXP-27", "paragraph", "The parser reads across lines until every ( is closed", tree8="f74dba8b"),
        node("PRO-1", "paragraph", "sections only at the top level"),
        node("PRO-3", "paragraph", "reserved words"),
        node("RET-1", "paragraph", "old", status="retired"),
        node("RET-2", "code_block", fence(VALID, "old()"), status="retired"),
    ]


FRAGMENTS = ["TST-1", "TST-2", "TST-3", "TST-4", "TST-5"]


def write_tree(root, nodes, meta=None):
    rows = [meta or {"type": "meta", "specs_commit": SPECS, "generator_version": "0.1.0", "retired_prefixes": []}]
    rows += [{"type": "file", "path": "specs/a.md", "prefix": "TST", "sha256": "0" * 64, "insertions": []}]
    rows += nodes
    (root / "data").mkdir(parents=True, exist_ok=True)
    (root / derived_norms.TREE_REL).write_text("".join(json.dumps(r) + "\n" for r in rows))


def cite(nodes, norm_id, reason="a reason"):
    n = next(n for n in nodes if n["id"] == norm_id)
    return f"// {norm_id}@{n['tree_hash'][:8]}: {reason}"


def good_grammar(nodes):
    c = lambda i, r="shown here": cite(nodes, i, r)
    return "\n".join([
        c("TST-1", "a source text is a list of sections"),
        "start: _NL? section+",
        "",
        c("TST-1", "start opens a section"),
        c("TST-4"),
        'section: "start" ":" _NL _INDENT statement+ _DEDENT',
        "",
        c("TST-1", "a call"),
        c("TST-2"),
        c("TST-3", "an error of a later phase parses"),
        c("TST-5", "arguments may span lines inside parentheses"),
        "statement: NAME OPEN_PAREN NUMBER CLOSE_PAREN _NL",
        "",
        c("TST-1", "a name"),
        "NAME: /(?!(start|functions)\\b)[a-z]+/",
        c("PRO-3", "the reserved words"),
        'RESERVED: "start" | "functions"',
        c("TST-1", "a number"),
        "NUMBER: /[0-9]+/",
        c("TST-1", "parentheses"),
        'OPEN_PAREN: "("',
        c("TST-1", "parentheses"),
        'CLOSE_PAREN: ")"',
        c("LEX-20", "a line break and the indentation after it"),
        c("TST-1", "lines"),
        "_NL: /(\\r?\\n[\\t ]*)+/",
        c("TST-1", "blanks"),
        "WS: / +/",
        c("TST-1", "blanks between tokens"),
        "%ignore WS",
        c("TST-2", "comments"),
        "COMMENT: /\\/\\/[^\\n]*/",
        c("TST-2", "comments are ignored"),
        "%ignore COMMENT",
        c("LEX-20", "indentation"),
        "%declare _INDENT _DEDENT",
        "",
    ])


def status_line(nodes, norm_id, state="derived", reason=None, issue=None, cases=None, hash8=None):
    n = next(n for n in nodes if n["id"] == norm_id)
    cases = dg.case_kinds(n) if cases is None else cases
    return {"type": "fragment", "id": norm_id, "hash": hash8 or n["tree_hash"][:8], "cases": cases,
            "state": state, "reason": reason, "issue": issue}


def good_status(nodes):
    return [status_line(nodes, i) for i in FRAGMENTS]


def write_outputs(root, grammar, lines, meta_first=True):
    folder = root / "specs-derived" / "grammar"
    folder.mkdir(parents=True, exist_ok=True)
    (root / derived_norms.GRAMMAR_REL).write_text(grammar)
    text = ""
    if meta_first:
        text = json.dumps({"type": "meta", "specs_commit": "", "generator": {}, "model": "",
                           "grammar_sha256": "", "status_sha256": ""}) + "\n"
    text += "".join(json.dumps(l, ensure_ascii=False, separators=(",", ":")) + "\n" for l in lines)
    (root / dg.STATUS_REL).write_text(text)


def git(root, *args):
    """Run git in a temporary repository of a test, never in a real repository."""
    result = subprocess.run(
        ["git", "-C", str(root), "-c", "user.email=t@example.com", "-c", "user.name=t",
         "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
        check=True, capture_output=True, text=True)
    return result.stdout.strip()


def git_init(root):
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q")
    (root / "README").write_text("x\n")
    git(root, "add", "--", "README")
    git(root, "commit", "-q", "-m", "first")
    return git(root, "rev-parse", "HEAD")


@pytest.fixture(autouse=True)
def plugin(tmp_path, monkeypatch):
    """The plugin that runs the script: a plugin.json of version 0.1.0, and no record of installed plugins.

    GIT_CEILING_DIRECTORIES keeps git from finding a checkout above the temporary folder.
    """
    root = tmp_path / "plugin"
    (root / ".claude-plugin").mkdir(parents=True)
    (root / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "clean-derived-norms", "version": VERSION}))
    monkeypatch.setattr(dg, "PLUGIN_ROOT", root)
    monkeypatch.setattr(dg, "INSTALLED_PLUGINS", tmp_path / "installed_plugins.json")
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    return root


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    nodes = base_nodes()
    write_tree(root, nodes)
    write_outputs(root, good_grammar(nodes), good_status(nodes))
    dg.seal(root, MODEL)
    return root, nodes


def run_check(root):
    return dg.check(root, CODE_OF_THE_SCRIPT)


def names(problems):
    return [(p[0], p[1]) for p in problems]


def reseal_with(root, nodes, grammar=None, lines=None):
    write_outputs(root, grammar if grammar is not None else good_grammar(nodes), lines if lines is not None else good_status(nodes))
    dg.seal(root, MODEL)


def main_in(root, monkeypatch, *argv):
    monkeypatch.chdir(root)
    return dg.main(list(argv))


def meta_of(root):
    return json.loads((root / dg.STATUS_REL).read_text().split("\n")[0])


def set_meta(root, key, value=None, drop=False):
    """Write a value of the meta line, or drop the key, keeping the status hash valid."""
    path = root / dg.STATUS_REL
    head, _, body = path.read_text().partition("\n")
    meta = json.loads(head)
    if drop:
        del meta[key]
    else:
        meta[key] = value
    path.write_text(json.dumps(meta, separators=(",", ":")) + "\n" + body)


def meta_problems(root):
    problems, _ = run_check(root)
    return [p for p in problems if p[0] == "meta"]


def add_fragment(root, nodes, own, state="derived", reason=None, issue=None):
    """Add TST-7, cited by the rule statement when it is derived."""
    nodes.append(node("TST-7", "code_block", own, start=5000))
    write_tree(root, nodes)
    grammar = good_grammar(nodes)
    if state == "derived":
        anchor = cite(nodes, "TST-5", "arguments may span lines inside parentheses") + "\n"
        grammar = grammar.replace(anchor, anchor + cite(nodes, "TST-7") + "\n")
    reseal_with(root, nodes, grammar, good_status(nodes) + [status_line(nodes, "TST-7", state, reason, issue)])


# ------------------------------------------------------------------ DGR-2


@pytest.mark.parametrize("opening,status,is_fragment", [
    ("```clean-language expect=syntax-error code=SYN007 line=1", "active", True),
    ("```clean-language expect=valid", "active", True),
    (" ```clean-language expect=valid", "active", True),
    ("```clean-language", "active", True),
    ("```clean-language  expect=valid", "active", True),
    ("~~~clean-language expect=valid", "active", True),
    ("```clean", "active", False),
    ("```clean expect=valid", "active", False),
    ("```clean-languages", "active", False),
    ("```toml", "active", False),
    ("```clean-language expect=valid", "retired", False),
])
def test_dgr2_which_code_blocks_are_fragments(opening, status, is_fragment):
    own = opening + "\nx\n" + opening.strip()[:3]
    assert derived_norms.is_fragment(node("X-1", "code_block", own, status=status)) is is_fragment


def test_dgr2_a_paragraph_is_not_a_fragment():
    assert not derived_norms.is_fragment(node("X-1", "paragraph", "```clean-language expect=valid"))


def test_dgr2_a_statement_that_cites_no_fragment_and_serves_none_fails(repo):
    root, nodes = repo
    grammar = good_grammar(nodes) + cite(nodes, "PRO-1") + "\nhelper: NUMBER\n"
    grammar = grammar.replace("statement: NAME OPEN_PAREN NUMBER CLOSE_PAREN _NL", "statement: NAME OPEN_PAREN NUMBER CLOSE_PAREN _NL\n    | helper _NL")
    reseal_with(root, nodes, grammar)
    problems, _ = run_check(root)
    assert ("source", "helper") not in names(problems)
    orphan = good_grammar(nodes) + cite(nodes, "PRO-1") + "\nTABS: /\\t+/\n" + cite(nodes, "PRO-1") + "\n%ignore TABS\n"
    reseal_with(root, nodes, orphan)
    problems, _ = run_check(root)
    assert ("source", "TABS") in names(problems)
    assert ("usage", "TABS") not in names(problems)


def test_dgr2_an_old_clean_block_is_never_a_case(repo):
    root, _ = repo
    tree = derived_norms.load_tree(root)
    assert [n["id"] for n in tree.fragments] == FRAGMENTS


# ------------------------------------------------------------------ DGR-3


def test_dgr3_the_folder_holds_only_the_two_files(repo):
    root, _ = repo
    (root / "specs-derived" / "grammar" / "notes.md").write_text("x\n")
    problems, _ = run_check(root)
    assert any(p[0] == "layout" and p[1].endswith("notes.md") for p in problems)


# ------------------------------------------------------------------ DGR-4


def test_dgr4_seal_writes_the_meta_line_first(repo):
    root, _ = repo
    lines = (root / dg.STATUS_REL).read_text().split("\n")
    meta = json.loads(lines[0])
    assert list(meta) == ["type", "specs_commit", "generator", "model", "grammar_sha256", "status_sha256"]
    assert list(meta["generator"]) == ["plugin", "version", "marketplace_commit"]
    assert meta["type"] == "meta" and meta["specs_commit"] == SPECS
    assert meta["generator"] == {"plugin": "clean-derived-norms", "version": VERSION, "marketplace_commit": "none"}
    assert meta["model"] == MODEL
    assert meta["grammar_sha256"] == hashlib.sha256((root / derived_norms.GRAMMAR_REL).read_bytes()).hexdigest()
    assert meta["status_sha256"] == hashlib.sha256("\n".join(lines[1:]).encode()).hexdigest()
    assert lines[0] == json.dumps(meta, separators=(",", ":"))


def test_dgr4_the_plugin_root_is_two_levels_above_the_folder_of_the_script():
    spec = importlib.util.spec_from_file_location("derive_grammar_fresh", SCRIPT)
    fresh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fresh)
    assert fresh.PLUGIN_ROOT == MODULE
    assert fresh.INSTALLED_PLUGINS == Path.home() / ".claude" / "plugins" / "installed_plugins.json"


def test_dgr4_seal_records_the_version_of_the_plugin_json(repo, plugin):
    root, _ = repo
    (plugin / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "clean-derived-norms", "version": "2.3.4"}))
    dg.seal(root, MODEL)
    assert meta_of(root)["generator"]["version"] == "2.3.4"


def installed(path, entries):
    path.write_text(json.dumps({"version": 2, "plugins": entries}))


def test_dgr4_the_marketplace_commit_of_the_installed_plugins(tmp_path, plugin):
    installed(tmp_path / "installed_plugins.json", {
        "other@m": [{"installPath": str(tmp_path / "elsewhere"), "gitCommitSha": "b" * 40}],
        "clean-derived-norms@m": [{"scope": "project", "installPath": str(plugin), "gitCommitSha": SHA}],
    })
    assert derived_norms.marketplace_commit(dg.PLUGIN_ROOT, dg.INSTALLED_PLUGINS) == SHA


def test_dgr4_the_marketplace_commit_of_the_checkout_that_holds_the_plugin(tmp_path, monkeypatch):
    market = tmp_path / "market"
    head = git_init(market)
    root = market / "apps" / "x" / "modules" / "clean-derived-norms"
    (root / ".claude-plugin").mkdir(parents=True)
    (root / ".claude-plugin" / "plugin.json").write_text(json.dumps({"version": VERSION}))
    monkeypatch.setattr(dg, "PLUGIN_ROOT", root)
    installed(tmp_path / "installed_plugins.json", {"p@m": [{"installPath": str(tmp_path / "elsewhere"), "gitCommitSha": "b" * 40}]})
    assert derived_norms.marketplace_commit(dg.PLUGIN_ROOT, dg.INSTALLED_PLUGINS) == head
    (root / "dirty").write_text("x\n")
    assert derived_norms.marketplace_commit(dg.PLUGIN_ROOT, dg.INSTALLED_PLUGINS) == head


@pytest.mark.parametrize("record", [None, "{not json", "[]", '{"plugins": {"p@m": [{"installPath": 5}]}}'])
def test_dgr4_an_unknown_marketplace_commit_is_none(repo, tmp_path, monkeypatch, record):
    root, _ = repo
    if record is not None:
        (tmp_path / "installed_plugins.json").write_text(record)
    assert derived_norms.marketplace_commit(dg.PLUGIN_ROOT, dg.INSTALLED_PLUGINS) == "none"
    assert main_in(root, monkeypatch, "seal", "--model", MODEL) == 0
    assert meta_of(root)["generator"]["marketplace_commit"] == "none"


def test_dgr4_an_entry_with_a_sha_that_is_not_40_hex_is_skipped(tmp_path, plugin):
    installed(tmp_path / "installed_plugins.json", {"p@m": [{"installPath": str(plugin), "gitCommitSha": "abc+dirty"}]})
    assert derived_norms.marketplace_commit(dg.PLUGIN_ROOT, dg.INSTALLED_PLUGINS) == "none"


def test_dgr4_seal_writes_the_model_it_is_given(repo, monkeypatch, capsys):
    root, _ = repo
    assert main_in(root, monkeypatch, "seal", "--model", "claude-sonnet-4.5_x") == 0
    assert meta_of(root)["model"] == "claude-sonnet-4.5_x"
    assert capsys.readouterr().out.strip() == (root / dg.STATUS_REL).read_text().split("\n")[0]


def test_dgr4_seal_records_a_bad_model_as_given(repo, monkeypatch):
    root, _ = repo
    assert main_in(root, monkeypatch, "seal", "--model", "claude opus") == 0
    assert meta_of(root)["model"] == "claude opus"
    assert ("meta", "model") in names(meta_problems(root))


def test_dgr4_seal_without_model_exits_2_and_writes_nothing(repo, monkeypatch, capsys):
    root, _ = repo
    before = (root / dg.STATUS_REL).read_bytes()
    assert main_in(root, monkeypatch, "seal") == 2
    assert "--model" in capsys.readouterr().err
    assert (root / dg.STATUS_REL).read_bytes() == before


@pytest.mark.parametrize("breakage", ["no-tree", "no-grammar", "status-not-json", "status-not-object", "tree-not-json",
                                      "no-plugin-json", "plugin-json-not-json", "no-version", "empty-version"])
def test_dgr4_seal_with_a_missing_or_malformed_input_exits_2_and_writes_nothing(repo, plugin, monkeypatch, breakage):
    root, _ = repo
    status = root / dg.STATUS_REL
    pj = plugin / ".claude-plugin" / "plugin.json"
    if breakage == "no-tree":
        (root / derived_norms.TREE_REL).unlink()
    elif breakage == "no-grammar":
        (root / derived_norms.GRAMMAR_REL).unlink()
    elif breakage == "status-not-json":
        status.write_text(status.read_text() + "{bad\n")
    elif breakage == "status-not-object":
        status.write_text(status.read_text() + "42\n")
    elif breakage == "tree-not-json":
        (root / derived_norms.TREE_REL).write_text((root / derived_norms.TREE_REL).read_text() + "{bad\n")
    elif breakage == "no-plugin-json":
        pj.unlink()
    elif breakage == "plugin-json-not-json":
        pj.write_text("{bad")
    elif breakage == "no-version":
        pj.write_text(json.dumps({"name": "clean-derived-norms"}))
    else:
        pj.write_text(json.dumps({"name": "clean-derived-norms", "version": ""}))
    before = status.read_bytes()
    assert main_in(root, monkeypatch, "seal", "--model", MODEL) == 2
    assert status.read_bytes() == before


def test_dgr4_seal_without_a_status_file_writes_only_the_meta_line(repo):
    root, _ = repo
    (root / dg.STATUS_REL).unlink()
    dg.seal(root, MODEL)
    text = (root / dg.STATUS_REL).read_text()
    assert text.count("\n") == 1 and json.loads(text)["type"] == "meta"


def test_dgr4_seal_reads_the_foundation_commit_of_an_older_tree(repo):
    root, nodes = repo
    write_tree(root, nodes, {"type": "meta", "foundation_commit": "e" * 40})
    dg.seal(root, MODEL)
    assert meta_of(root)["specs_commit"] == "e" * 40


# ------------------------------------------------------------------ DGR-5


def test_dgr5_seal_orders_the_fragment_lines_as_the_tree(repo):
    root, nodes = repo
    reseal_with(root, nodes, lines=list(reversed(good_status(nodes))))
    ids = [json.loads(l)["id"] for l in (root / dg.STATUS_REL).read_text().splitlines()[1:]]
    assert ids == FRAGMENTS
    problems, _ = run_check(root)
    assert problems == []


def test_dgr5_status_lines_out_of_order_fail(repo):
    root, nodes = repo
    write_outputs(root, good_grammar(nodes), list(reversed(good_status(nodes))))
    problems, _ = run_check(root)
    assert any(p[0] == "status" and "order" in p[2] for p in problems)


@pytest.mark.parametrize("change,expected", [
    (lambda l: l.pop("issue"), "lacks the fields issue"),
    (lambda l: l.update(reason="why"), "a derived fragment has a reason"),
    (lambda l: l.update(issue="https://github.com/Ivan-Pasco/clean-language-foundation/issues/3"), "an issue on a fragment that is not pending"),
    (lambda l: l.update(state="partial"), "state 'partial' is not derived or pending"),
    (lambda l: l.update(cases=["maybe"]), 'cases ["maybe"] is not a list of one'),
    (lambda l: l.update(cases=["accept", "accept"]), 'cases ["accept", "accept"] is not a list of one'),
    (lambda l: l.update(cases="accept"), 'cases "accept" is not a list of one'),
    (lambda l: l.update(hash="ABC"), "hash is not 8 hex digits"),
])
def test_dgr5_fields_of_a_status_line(repo, change, expected):
    root, nodes = repo
    lines = good_status(nodes)
    change(lines[0])
    reseal_with(root, nodes, lines=lines)
    problems, _ = run_check(root)
    assert any(expected in p[2] for p in problems), problems


def test_dgr5_field_order(repo):
    root, nodes = repo
    lines = good_status(nodes)
    lines[0] = {k: lines[0][k] for k in reversed(dg.FRAGMENT_KEYS)}
    reseal_with(root, nodes, lines=lines)
    problems, _ = run_check(root)
    assert any("in that order" in p[2] for p in problems)


@pytest.mark.parametrize("bad", [
    "https://github.com/other/repo/issues/1",
    "https://github.com/Ivan-Pasco/clean-language-foundation/issues/12\n",
    "https://github.com/Ivan-Pasco/clean-language-foundation/issues/12/",
    " https://github.com/Ivan-Pasco/clean-language-foundation/issues/12",
    "https://github.com/Ivan-Pasco/clean-language-foundation/issues/012",
])
def test_dgr5_a_pending_issue_is_a_whole_issue_url_of_the_foundation(repo, bad):
    root, nodes = repo
    lines = good_status(nodes)
    lines[0].update(state="pending", reason=cite(nodes, "PRO-1", "x")[3:], issue=bad)
    reseal_with(root, nodes, lines=lines)
    problems, _ = run_check(root)
    assert ("status", "TST-1", "the issue is not an issue URL of the foundation") in [tuple(p) for p in problems]


def test_dgr5_every_fragment_has_exactly_one_line(repo):
    root, nodes = repo
    lines = good_status(nodes)
    reseal_with(root, nodes, lines=lines[1:] + [status_line(nodes, "TST-2"), {**status_line(nodes, "TST-1"), "id": "OLD-1"}])
    problems, _ = run_check(root)
    assert ("status", "TST-1") in names(problems)
    assert any(p[1] == "TST-2" and "2 status lines" in p[2] for p in problems)
    assert any(p[1] == "OLD-1" and "not a fragment" in p[2] for p in problems)


def test_dgr5_hash_and_cases_of_a_line_must_be_current(repo):
    root, nodes = repo
    lines = good_status(nodes)
    lines[0]["hash"] = "00000000"
    lines[1]["cases"] = ["accept"]
    reseal_with(root, nodes, lines=lines)
    problems, _ = run_check(root)
    assert any(p[1] == "TST-1" and "the norm hash is" in p[2] for p in problems)
    assert any(p[1] == "TST-2" and 'the script gives ["reject"]' in p[2] for p in problems)


def test_dgr5_a_line_that_is_not_json_names_the_file_and_line(repo, monkeypatch):
    root, _ = repo
    path = root / dg.STATUS_REL
    path.write_text(path.read_text() + "{not json\n")
    problems, _ = run_check(root)
    assert any(p[0] == "status" and p[1].endswith(":7") and p[2] == "not JSON" for p in problems)
    assert main_in(root, monkeypatch, "check") == 1


@pytest.mark.parametrize("bad", ["42", '["x"]', '{"type":"fragment","id":["TST-1"],"hash":"00000000","cases":["accept"],"state":"derived","reason":null,"issue":null}'])
def test_dgr5_a_line_that_is_not_an_object_fails_without_a_crash(repo, monkeypatch, bad):
    root, _ = repo
    path = root / dg.STATUS_REL
    path.write_text(path.read_text() + bad + "\n")
    problems, _ = run_check(root)
    assert any(p[0] == "status" and p[1].endswith(":7") for p in problems), problems
    assert main_in(root, monkeypatch, "check") == 1


def test_dgr5_a_pending_reason_that_is_not_text(repo):
    root, nodes = repo
    lines = good_status(nodes)
    lines[0].update(state="pending", reason=["x"])
    reseal_with(root, nodes, lines=lines)
    problems, _ = run_check(root)
    assert any(p[1] == "TST-1" and "no reason" in p[2] for p in problems)
    assert any(p[1] == "TST-1" and p[2] == "the reason cites no norm" for p in problems)


def test_dgr5_the_first_line_must_be_the_meta_line(repo):
    root, nodes = repo
    write_outputs(root, good_grammar(nodes), good_status(nodes), meta_first=False)
    problems, _ = run_check(root)
    assert any(p[0] == "meta" and "not the meta line" in p[2] for p in problems)


def test_dgr5_a_second_meta_line_fails(repo):
    root, nodes = repo
    write_outputs(root, good_grammar(nodes), good_status(nodes) + [{"type": "meta"}])
    dg.seal(root, MODEL)
    path = root / dg.STATUS_REL
    head, _, body = path.read_text().partition("\n")
    body += '{"type":"meta"}\n'
    meta = json.loads(head)
    meta["status_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    path.write_text(json.dumps(meta, separators=(",", ":")) + "\n" + body)
    problems, _ = run_check(root)
    assert any(p[0] == "meta" and "not the first line" in p[2] for p in problems)


def test_dgr5_the_states_of_the_spec():
    nodes = [node("SEM-79", "code_block", fence(syntax(1, "SYN007"), "x"), parent=None),
             node("SEM-183", "code_block", fence("clean-language", "x"), parent=None)]
    assert status_line(nodes, "SEM-79")["cases"] == ["reject"]
    assert status_line(nodes, "SEM-183")["cases"] == []
    assert list(status_line(nodes, "SEM-183")) == dg.FRAGMENT_KEYS


# ------------------------------------------------------------------ DGR-6


def test_dgr6_case_text_of_a_top_level_fragment():
    tree = derived_norms.Tree(base_nodes())
    assert derived_norms.case_text(tree, tree.nodes["TST-1"]) == "start:\n\tprint(1)\n"


def test_dgr6_the_indentation_of_the_fence_is_removed():
    tree = derived_norms.Tree(base_nodes())
    assert derived_norms.container_column(tree, tree.nodes["TST-4"]) == 2
    assert derived_norms.case_text(tree, tree.nodes["TST-4"]) == "start:\n\tprint(4)\n"


def test_dgr6_a_fence_indented_in_its_own_line_and_its_container_as_mod73():
    prefix = "2. intro:\n\n   "
    own = " ```clean-language expect=valid\n    libraries: auth\n    ```"
    nodes = [node("SEC-1", "section", "", parent=None),
             node("ITM-1", "item", prefix, start=0, end=len(prefix) + len(own)),
             node("MOD-73", "code_block", own, parent="ITM-1", start=len(prefix))]
    tree = derived_norms.Tree(nodes)
    assert derived_norms.case_text(tree, tree.nodes["MOD-73"]) == "libraries: auth\n"
    assert dg.case_kinds(tree.nodes["MOD-73"]) == ["accept"]
    assert derived_norms.fragment_lines(tree, tree.nodes["MOD-73"]) == ["```clean-language expect=valid", "libraries: auth", "```"]


@pytest.mark.parametrize("lines,expected", [
    (["a", "\t\tb", "\t  c", "\td", "x  "], "a\n\t\tb\n\t  c\n\td\nx  \n"),
    (["a", "", "  ", ""], "a\n"),
    (["", "a"], "\na\n"),
    (["start:", "    print(1)"], "start:\n    print(1)\n"),
    (["start:", "\t    print(1)"], "start:\n\t    print(1)\n"),
])
def test_dgr6_tabs_spaces_and_line_ends(lines, expected):
    tree = derived_norms.Tree([node("X-1", "code_block", fence(VALID, *lines), parent=None)])
    assert derived_norms.case_text(tree, tree.nodes["X-1"]) == expected


def test_dgr6_the_case_text_of_lex182():
    own = fence(syntax(2, "SYN011"), "start:", '\tstring notice = "You have {messages.length()} messages"')
    tree = derived_norms.Tree([node("LEX-182", "code_block", own, parent=None)])
    assert derived_norms.case_text(tree, tree.nodes["LEX-182"]) == 'start:\n\tstring notice = "You have {messages.length()} messages"\n'
    assert dg.case_kinds(tree.nodes["LEX-182"]) == ["reject"]
    assert dg.expected_line(tree.nodes["LEX-182"]) == 2


@pytest.mark.parametrize("info,cases", [
    ("clean-language expect=valid", ["accept"]),
    ("clean-language expect=error code=SEM005", ["accept"]),
    ("clean-language expect=syntax-error code=SYN007 line=1", ["reject"]),
    ("clean-language expect=valid ", ["accept"]),
    ("clean-language", []),
    ("clean-language expect=syntax-error code=SYN007", []),
    ("clean-language expect=valid line=3", []),
    ("clean-language  expect=valid", []),
    ("clean-language expect=error code=sem005", []),
    ("clean-language expect=syntax-error code=SYN007 line=0", ["reject"]),
    ("clean-language expect=syntax-error code=SYN007 line=03", []),
    ("clean-language expect=error code=SEM05", []),
    ("clean-language expect=error code=ABCDEFG001", []),
    ("clean-language expect=error code=SYN001", ["accept"]),
    ("clean-language expect=syntax-error code=SEM005 line=2", ["reject"]),
])
def test_dgr6_the_case_comes_from_the_opening_line(info, cases):
    assert dg.case_kinds(node("X-1", "code_block", fence(info, "x"), parent=None)) == cases


def test_dgr6_no_comment_decides_the_case():
    own = fence(VALID, "start:", "\tprint(1)    // fails: SYN007")
    assert dg.case_kinds(node("LAU-42", "code_block", own, parent=None)) == ["accept"]
    own = fence(syntax(2), "start:", "\tprint 1")
    assert dg.case_kinds(node("X-1", "code_block", own, parent=None)) == ["reject"]


def test_dgr6_the_script_cites_no_norm_for_the_case_and_reads_no_marker():
    for _, source in CODE_OF_THE_SCRIPT:
        found, bad = derived_norms.script_citations(source)
        assert bad == []
        assert "ERR-32" not in [i for _, i, _ in found]
        assert "fails:" not in source
        assert 'replace("    ", "\\t")' not in source


def test_dgr6_one_case_per_fragment_and_no_cut():
    assert not hasattr(dg, "case_parts") and not hasattr(dg, "fragment_cases") and not hasattr(dg, "violations")
    two = fence(syntax(2), "// file: a.cln", "x", "// file: b.cln", "y  // fails: SYN001", "z  // fails: SYN002")
    assert dg.case_kinds(node("X-1", "code_block", two, parent=None)) == ["reject"]


# ------------------------------------------------------------------ DGR-8


def test_dgr8_a_statement_without_citation(repo):
    root, nodes = repo
    reseal_with(root, nodes, good_grammar(nodes).replace(cite(nodes, "TST-1", "a number") + "\n", ""))
    problems, _ = run_check(root)
    assert ("citation", "NUMBER") in names(problems)


def test_dgr8_a_blank_line_between_citation_and_statement(repo):
    root, nodes = repo
    c = cite(nodes, "TST-1", "a number")
    reseal_with(root, nodes, good_grammar(nodes).replace(c + "\n", c + "\n\n"))
    problems, _ = run_check(root)
    assert any(p[2] == "a citation not just above a statement" for p in problems)
    assert ("citation", "NUMBER") in names(problems)


def test_dgr8_every_comment_line_is_a_citation(repo):
    root, nodes = repo
    reseal_with(root, nodes, "// a note\n" + good_grammar(nodes))
    problems, _ = run_check(root)
    assert ("citation", "line 1") in names(problems)


def test_dgr8_an_inline_comment_and_a_comment_inside_a_statement(repo):
    root, nodes = repo
    grammar = good_grammar(nodes).replace("NUMBER: /[0-9]+/", "NUMBER: /[0-9]+/ // digits")
    grammar = grammar.replace("statement: NAME OPEN_PAREN NUMBER CLOSE_PAREN _NL",
                              "statement: NAME OPEN_PAREN NUMBER CLOSE_PAREN _NL\n" + cite(nodes, "TST-1") + "\n    | NAME _NL")
    reseal_with(root, nodes, grammar)
    problems, _ = run_check(root)
    assert any(p[1] == "NUMBER" and "not on a line of its own" in p[2] for p in problems)
    assert any("inside the statement statement" in p[2] for p in problems)


def test_dgr8_one_citation_line_per_norm(repo):
    root, nodes = repo
    c = cite(nodes, "TST-1", "a number")
    reseal_with(root, nodes, good_grammar(nodes).replace(c + "\n", c + "\n" + cite(nodes, "TST-1", "again") + "\n"))
    problems, _ = run_check(root)
    assert any(p[1] == "NUMBER" and "cited twice" in p[2] for p in problems)


def test_dgr8_statements_and_keys():
    statements, problems = derived_norms.parse_grammar(
        "// ABC-1@00000000: x\n?expr: a b -> alias\n    | c\n// ABC-1@00000000: x\n%ignore WS\n// ABC-1@00000000: x\n%declare _INDENT\n")
    assert [s.key for s in statements] == ["expr", "%ignore WS", "%declare _INDENT"]
    assert statements[0].refs == {"a", "b", "c"}
    assert statements[1].refs == {"WS"}
    assert statements[2].defines == {"_INDENT"}
    assert problems == []


def test_dgr8_no_import(repo, monkeypatch):
    root, nodes = repo
    reseal_with(root, nodes, good_grammar(nodes) + cite(nodes, "TST-1") + "\n%import common.CNAME\n")
    problems, _ = run_check(root)
    assert ("import", "%import common.CNAME") in names(problems)
    assert main_in(root, monkeypatch, "check") == 1


# ------------------------------------------------------------------ DGR-9


@pytest.mark.parametrize("citation,problem", [
    ("// EXP-999@e105eaa8: a reason", "EXP-999 is not a norm"),
    ("// RET-1@{RET-1}: a reason", "RET-1 is retired"),
    ("// PRO-1@00000000: a reason", "PRO-1 has the norm hash {PRO-1}"),
    ("// PRO-1@{PRO-1}:", "not a citation"),
    ("// PRO-1@ABCDEF12: x", "not a citation"),
])
def test_dgr9_a_citation_that_does_not_check(repo, citation, problem):
    root, nodes = repo
    hashes = {n["id"]: n["tree_hash"][:8] for n in nodes}
    citation, problem = citation.format(**hashes), problem.format(**hashes)
    grammar = good_grammar(nodes).replace("NUMBER: /[0-9]+/", citation + "\nNUMBER: /[0-9]+/")
    reseal_with(root, nodes, grammar)
    problems, _ = run_check(root)
    assert any(p[2].endswith(problem) for p in problems), problems


def test_dgr9_a_citation_of_a_pending_fragment(repo):
    root, nodes = repo
    lines = good_status(nodes)
    lines[0].update(state="pending", reason="open: " + cite(nodes, "PRO-1", "x")[3:])
    reseal_with(root, nodes, lines=lines)
    problems, _ = run_check(root)
    assert any(p[0] == "citation" and p[2].endswith("TST-1 is pending") for p in problems)


def test_dgr9_a_reason_citation_that_does_not_check(repo):
    root, nodes = repo
    lines = good_status(nodes)
    lines[0].update(state="pending", reason="onError is not listed: PRO-1@11111111")
    reseal_with(root, nodes, lines=lines)
    problems, _ = run_check(root)
    pro1 = next(n for n in nodes if n["id"] == "PRO-1")["tree_hash"][:8]
    assert ("reason-citation", "TST-1", f"PRO-1 has the norm hash {pro1}") in [tuple(p) for p in problems]


def test_dgr9_a_script_citation_that_does_not_check():
    tree = derived_norms.Tree(base_nodes())
    problems = derived_norms.check_script(tree, [("script.py", "x = 1\n    # LEX-20@11111111: one tab per level\n")])
    assert problems == [("script-citation", "LEX-20", "script.py line 2: LEX-20 has the norm hash 8c358626")]
    assert derived_norms.check_script(tree, [("script.py", "# LEX-20@8c358626:\n")]) == [("script-citation", "script.py line 1", "not a citation")]


def test_dgr9_a_line_of_the_code_of_the_script_is_named_by_its_file():
    tree = derived_norms.Tree(base_nodes())
    code = [("use-cases/derive-grammar/derive_grammar.py", "# LEX-21@11111111: a\n"),
            ("scripts/derived_norms.py", "x = 1\n# LEX-20@11111111: b\n")]
    assert derived_norms.check_script(tree, code) == [
        ("script-citation", "LEX-21", "use-cases/derive-grammar/derive_grammar.py line 1: LEX-21 has the norm hash 7474dff8"),
        ("script-citation", "LEX-20", "scripts/derived_norms.py line 2: LEX-20 has the norm hash 8c358626")]
    assert [path for path, _ in CODE_OF_THE_SCRIPT] == ["use-cases/derive-grammar/derive_grammar.py", "scripts/derived_norms.py"]


def test_dgr9_the_citations_of_the_script_check_against_the_fixture():
    assert derived_norms.check_script(derived_norms.Tree(base_nodes()), CODE_OF_THE_SCRIPT) == []


# ------------------------------------------------------------------ DGR-10


def test_dgr10_a_conflict_fails_the_strict_build(repo, monkeypatch):
    root, nodes = repo
    grammar = good_grammar(nodes).replace("statement: NAME OPEN_PAREN NUMBER CLOSE_PAREN _NL",
                                          "statement: NAME OPEN_PAREN expr CLOSE_PAREN _NL")
    grammar += cite(nodes, "TST-1") + '\nexpr: expr "+" expr | NUMBER\n'
    reseal_with(root, nodes, grammar)
    problems, _ = run_check(root)
    assert [p for p in problems if p[0] == "build"]
    assert main_in(root, monkeypatch, "check") == 1


# ------------------------------------------------------------------ DGR-11


def fixture_parser(extra=""):
    grammar = good_grammar(base_nodes()) + extra
    statements, problems = derived_norms.parse_grammar(grammar)
    assert problems == []
    return derived_norms.build_parser(grammar, statements)


def test_dgr11_a_line_break_inside_brackets_does_not_end_a_line(repo):
    root, _ = repo
    problems, _ = run_check(root)
    assert ("accept", "TST-5") not in names(problems)


def test_dgr11_unpaired_brackets(repo):
    root, nodes = repo
    reseal_with(root, nodes, good_grammar(nodes).replace("OPEN_PAREN", "OPEN_X"))
    problems, _ = run_check(root)
    assert ("brackets", "OPEN_X") in names(problems)
    assert ("brackets", "CLOSE_PAREN") in names(problems)


def test_dgr11_name_must_not_match_a_reserved_word(repo):
    root, nodes = repo
    grammar = good_grammar(nodes).replace("NAME: /(?!(start|functions)\\b)[a-z]+/", "NAME: /(?!(start)\\b)[a-z]+/")
    reseal_with(root, nodes, grammar)
    problems, _ = run_check(root)
    assert any(p[0] == "names" and "'functions'" in p[2] for p in problems)
    assert not any(p[0] == "names" and "'start'" in p[2] for p in problems)


def test_dgr11_name_needs_reserved(repo):
    root, nodes = repo
    grammar = good_grammar(nodes).replace(cite(nodes, "PRO-3", "the reserved words") + '\nRESERVED: "start" | "functions"\n', "")
    reseal_with(root, nodes, grammar)
    problems, _ = run_check(root)
    assert ("names", "RESERVED") in names(problems)


def test_dgr11_reserved_lists_strings(repo):
    root, nodes = repo
    reseal_with(root, nodes, good_grammar(nodes).replace('RESERVED: "start" | "functions"', "RESERVED: /start|functions/"))
    problems, _ = run_check(root)
    assert any(p[0] == "names" and "string alternatives" in p[2] for p in problems)


@pytest.mark.parametrize("text,parses", [
    ("start:\n\tprint(1)\n", True),
    ("start:\n\tprint(\n\t\t 5)\n", True),
    ("start:\n\tprint(\n   5)\n", True),
    ("start:\n  print(1)\n", False),
    ("start:\n    print(1)\n", False),
    ("start:\n\t print(1)\n", False),
    ("start:\n\tprint(1)\n\t  print(2)\n", False),
])
def test_dgr11_a_space_in_the_indentation_outside_brackets_does_not_parse(text, parses):
    parser, indenter = fixture_parser()
    assert (dg.try_parse(parser, indenter, text) is None) is parses


def test_dgr11_the_refusal_is_at_the_line_break_before_that_line():
    parser, indenter = fixture_parser()
    text = "start:\n\tprint(1)\n\t  print(2)\n"
    start, end, message = dg.try_parse(parser, indenter, text)
    assert "IndentationSpaceError" in message and "line 3" in message
    assert start == text.index("\n\t  print(2)")


def test_dgr11_spaces_inside_an_ignored_block_comment_are_not_indentation():
    nodes = base_nodes()
    parser, indenter = fixture_parser("\n".join([
        cite(nodes, "TST-2", "block comments"),
        "BLOCK_COMMENT: /\\/\\*(.|\\n)*?\\*\\//",
        cite(nodes, "TST-2", "block comments are ignored"),
        "%ignore BLOCK_COMMENT",
        "",
    ]))
    assert dg.try_parse(parser, indenter, "start:\n\tprint(1) /*\n   Multi-line\n   comment\n*/\n") is None


def test_dgr11_dgr18_the_script_cites_lex20_lex21_and_exp27_for_the_indenter():
    cited = {}
    for path, source in CODE_OF_THE_SCRIPT:
        found, bad = derived_norms.script_citations(source)
        assert bad == []
        cited[path] = sorted((i, h) for _, i, h in found)
    assert cited == {"use-cases/derive-grammar/derive_grammar.py": [],
                     "scripts/derived_norms.py": [("EXP-27", "f74dba8b"), ("LEX-20", "8c358626"), ("LEX-21", "7474dff8")]}


# ------------------------------------------------------------------ DGR-12


def test_dgr12_no_status_file_lists_every_fragment_as_new(tmp_path):
    nodes = base_nodes()
    write_tree(tmp_path, nodes)
    items = dg.worklist(tmp_path)
    assert [(i["kind"], i["id"]) for i in items] == [("new", i) for i in FRAGMENTS]
    assert [i["cases"] for i in items] == [["accept"], ["reject"], ["accept"], ["accept"], ["accept"]]
    assert list(items[0]) == ["kind", "id", "old_hash", "new_hash", "cases", "file"]


def test_dgr12_nothing_changed_gives_an_empty_list(repo, monkeypatch, capsys):
    root, _ = repo
    assert dg.worklist(root) == []
    assert main_in(root, monkeypatch, "worklist") == 0
    assert capsys.readouterr().out == ""


def test_dgr12_a_changed_hash(repo):
    root, nodes = repo
    nodes[1]["tree_hash"] = "1a2b3c4d" + "0" * 56
    write_tree(root, nodes)
    items = dg.worklist(root)
    changed = [i for i in items if i.get("id") == "TST-1"]
    assert changed[0]["kind"] == "changed" and changed[0]["new_hash"] == "1a2b3c4d"
    norm = [i for i in items if i["kind"] == "norm"]
    assert {i["statement"] for i in norm} == {"start", "section", "statement", "NAME", "NUMBER", "OPEN_PAREN", "CLOSE_PAREN", "_NL", "WS", "%ignore WS"}
    assert all(i["new_hash"] == "1a2b3c4d" for i in norm)
    assert list(norm[0]) == ["kind", "statement", "old_hash", "new_hash", "citation"]


def test_dgr12_a_changed_case(repo):
    root, nodes = repo
    lines = good_status(nodes)
    lines[1]["cases"] = ["accept"]
    write_outputs(root, good_grammar(nodes), lines)
    assert [(i["kind"], i["id"], i["cases"]) for i in dg.worklist(root)] == [("changed", "TST-2", ["reject"])]


def test_dgr12_a_gone_fragment(repo):
    root, nodes = repo
    nodes = [n for n in nodes if n["id"] != "TST-4"]
    write_tree(root, nodes)
    items = dg.worklist(root)
    assert items[0] == {"kind": "gone", "id": "TST-4", "old_hash": h8("TST-4", TST4), "new_hash": None,
                        "cases": ["accept"], "file": None}
    assert [(i["kind"], i["statement"]) for i in items[1:]] == [("norm", "section")]
    assert items[1]["new_hash"] is None


def test_dgr12_a_gone_fragment_keeps_the_cases_and_file_of_its_old_line(repo):
    root, nodes = repo
    lines = good_status(nodes)
    tst2 = next(n for n in nodes if n["id"] == "TST-2")
    tst2["status"] = "retired"
    write_tree(root, nodes)
    gone = [i for i in dg.worklist(root) if i["kind"] == "gone"]
    assert gone == [{"kind": "gone", "id": "TST-2", "old_hash": lines[1]["hash"], "new_hash": None,
                     "cases": ["reject"], "file": "specs/a.md"}]


def test_dgr12_a_new_fragment(repo):
    root, nodes = repo
    nodes.append(node("TST-9", "code_block", fence(VALID, "start:", "\tprint(9)"), start=9000))
    write_tree(root, nodes)
    assert [(i["kind"], i["id"]) for i in dg.worklist(root)] == [("new", "TST-9")]


def test_dgr12_a_new_fragment_with_no_form_of_cex4_has_no_case(repo):
    root, nodes = repo
    nodes.append(node("SEM-183", "code_block", fence("clean-language", "start:", "\tprint(9)"), start=9000))
    write_tree(root, nodes)
    assert [(i["kind"], i["id"], i["cases"]) for i in dg.worklist(root)] == [("new", "SEM-183", [])]


def test_dgr12_pending_with_nothing_changed_and_with_a_cited_norm_changed(repo):
    root, nodes = repo
    lines = good_status(nodes)
    lines[0].update(state="pending", reason="no norm says it: " + cite(nodes, "PRO-1", "x")[3:].split(":")[0])
    write_outputs(root, good_grammar(nodes), lines)
    assert dg.worklist(root) == []
    next(n for n in nodes if n["id"] == "PRO-1")["tree_hash"] = "22222222" + "0" * 56
    write_tree(root, nodes)
    assert [(i["kind"], i["id"]) for i in dg.worklist(root)] == [("changed", "TST-1")]


@pytest.mark.parametrize("how", ["retired", "gone"])
def test_dgr12_pending_whose_cited_norm_is_retired_or_gone(repo, how):
    root, nodes = repo
    lines = good_status(nodes)
    lines[0].update(state="pending", reason="open: " + cite(nodes, "PRO-1", "x")[3:].split(":")[0])
    write_outputs(root, good_grammar(nodes), lines)
    pro1 = next(n for n in nodes if n["id"] == "PRO-1")
    if how == "retired":
        pro1["status"] = "retired"
    else:
        nodes.remove(pro1)
    write_tree(root, nodes)
    assert [(i["kind"], i["id"]) for i in dg.worklist(root)] == [("changed", "TST-1")]


def test_dgr12_a_pending_fragment_with_no_form_of_cex4_that_did_not_change(repo):
    root, nodes = repo
    add_fragment(root, nodes, fence("clean-language", "start:", "\tprint(7)"), "pending", derived_norms.NO_FORM_REASON)
    assert dg.worklist(root) == []


@pytest.mark.parametrize("how", ["hash", "retired", "gone"])
def test_dgr12_a_statement_citing_a_changed_norm(repo, how):
    root, nodes = repo
    pro3 = next(n for n in nodes if n["id"] == "PRO-3")
    old = pro3["tree_hash"][:8]
    if how == "hash":
        pro3["tree_hash"] = "44444444" + "0" * 56
    elif how == "retired":
        pro3["status"] = "retired"
    else:
        nodes.remove(pro3)
    write_tree(root, nodes)
    assert dg.worklist(root) == [{"kind": "norm", "statement": "RESERVED", "old_hash": old,
                                  "new_hash": "44444444" if how == "hash" else None, "citation": f"PRO-3@{old}"}]


def test_dgr12_a_directive_is_named_by_its_first_line(repo):
    root, nodes = repo
    next(n for n in nodes if n["id"] == "LEX-20")["tree_hash"] = "55555555" + "0" * 56
    write_tree(root, nodes)
    assert {i["statement"] for i in dg.worklist(root)} == {"_NL", "%declare _INDENT _DEDENT"}


def test_dgr12_a_fragment_moved_with_the_same_hash(repo):
    root, nodes = repo
    tst1 = nodes.pop(1)
    tst1["file"] = "specs/b.md"
    nodes.append(tst1)
    write_tree(root, nodes)
    assert dg.worklist(root) == []
    dg.seal(root, MODEL)
    ids = [json.loads(l)["id"] for l in (root / dg.STATUS_REL).read_text().splitlines()[1:]]
    assert ids[-1] == "TST-1"


def test_dgr12_a_status_file_of_the_local_skill_is_taken_as_absent(repo):
    root, nodes = repo
    path = root / dg.STATUS_REL
    head, _, body = path.read_text().partition("\n")
    old_meta = {"type": "meta", "foundation_commit": SPECS, "generators_commit": SHA, "model": MODEL,
                "grammar_sha256": "", "status_sha256": ""}
    gone = json.dumps(status_line(nodes, "TST-1", hash8="00000000") | {"id": "GONE-1"}, separators=(",", ":"))
    path.write_text(json.dumps(old_meta) + "\n" + body + gone + "\n")
    next(n for n in nodes if n["id"] == "PRO-3")["tree_hash"] = "44444444" + "0" * 56
    write_tree(root, nodes)
    assert [(i["kind"], i["id"]) for i in dg.worklist(root)] == [("new", i) for i in FRAGMENTS]


@pytest.mark.parametrize("bad", ["{bad", "42", '["x"]'])
def test_dgr12_exit_status_2(tmp_path, repo, monkeypatch, bad):
    assert main_in(tmp_path, monkeypatch, "worklist") == 2
    root, _ = repo
    path = root / dg.STATUS_REL
    good = path.read_text()
    path.write_text(good + bad + "\n")
    assert main_in(root, monkeypatch, "worklist") == 2
    path.write_text(good)
    (root / derived_norms.TREE_REL).write_text((root / derived_norms.TREE_REL).read_text() + bad + "\n")
    assert main_in(root, monkeypatch, "worklist") == 2


# ------------------------------------------------------------------ DGR-13


LAST_LINE = re.compile(r"fragments: [0-9]+ derived, [0-9]+ pending; accept parsed [0-9]+/[0-9]+; "
                       r"reject rejected [0-9]+/[0-9]+; problems: [0-9]+")


def test_dgr13_every_check_passes(repo, monkeypatch, capsys):
    root, _ = repo
    assert main_in(root, monkeypatch, "check") == 0
    out = capsys.readouterr().out.splitlines()
    assert out == ["fragments: 5 derived, 0 pending; accept parsed 4/4; reject rejected 1/1; problems: 0"]


def test_dgr13_the_last_line_of_check(repo, monkeypatch, capsys):
    root, nodes = repo
    reseal_with(root, nodes, good_grammar(nodes) + cite(nodes, "TST-1") + '\nlonely: "x"\n')
    assert main_in(root, monkeypatch, "check") == 1
    out = capsys.readouterr().out.splitlines()
    assert "usage: lonely: not used by start, by another statement or by a directive" in out
    assert LAST_LINE.fullmatch(out[-1]) and out[-1].endswith(f"problems: {len(out) - 1}")


def test_dgr13_an_accept_case_that_does_not_parse(repo):
    root, nodes = repo
    nodes[1]["own_text"] = fence(VALID, "start:", "\tprint 1")
    write_tree(root, nodes)
    reseal_with(root, nodes)
    problems, summary = run_check(root)
    assert ("accept", "TST-1") in names(problems)
    assert summary["parsed"]["accept"] == [3, 4]


def test_dgr13_an_error_case_is_an_accept_case(repo):
    root, nodes = repo
    nodes[3]["own_text"] = fence(ERROR, "start:", "\tprint 3")
    write_tree(root, nodes)
    reseal_with(root, nodes)
    problems, _ = run_check(root)
    assert ("accept", "TST-3") in names(problems)


def test_dgr13_a_case_indented_with_four_spaces_fails_through_the_indenter(repo, monkeypatch):
    root, nodes = repo
    nodes[1]["own_text"] = fence(VALID, "start:", "    print(1)")
    write_tree(root, nodes)
    reseal_with(root, nodes)
    problems, _ = run_check(root)
    assert any(p[:2] == ("accept", "TST-1") and "IndentationSpaceError" in p[2] and "line 2" in p[2] for p in problems), problems
    assert main_in(root, monkeypatch, "check") == 1


def test_dgr13_a_dedent_error_is_a_case_that_does_not_parse(repo, monkeypatch):
    root, nodes = repo
    nodes[1]["own_text"] = fence(VALID, "start:", "\t\tprint(1)", "\tprint(2)")
    write_tree(root, nodes)
    reseal_with(root, nodes)
    problems, _ = run_check(root)
    assert any(p[:2] == ("accept", "TST-1") and "DedentError" in p[2] for p in problems)
    assert main_in(root, monkeypatch, "check") == 1


def test_dgr13_a_reject_case_that_parses(repo):
    root, nodes = repo
    nodes[2]["own_text"] = fence(syntax(2), "start:", "\tprint(1)")
    write_tree(root, nodes)
    reseal_with(root, nodes)
    problems, _ = run_check(root)
    assert ("reject", "TST-2") in names(problems)


def test_dgr13_a_reject_case_that_fails_before_its_expected_line(repo, monkeypatch):
    root, nodes = repo
    nodes[2]["own_text"] = fence(syntax(3), "start:", "\tprint 1", "\tprint(2)")
    write_tree(root, nodes)
    reseal_with(root, nodes)
    problems, summary = run_check(root)
    assert any(p[:2] == ("reject", "TST-2") and "before the line break" in p[2] for p in problems), problems
    assert summary["parsed"]["reject"] == [0, 1]
    assert main_in(root, monkeypatch, "check") == 1


def test_dgr13_a_reject_case_that_the_indenter_refuses_at_the_line_break_passes(repo):
    root, nodes = repo
    nodes[2]["own_text"] = fence(syntax(3, "SYN003"), "start:", "\tprint(1)", "  print(2)")
    write_tree(root, nodes)
    reseal_with(root, nodes)
    problems, summary = run_check(root)
    assert problems == []
    assert summary["parsed"]["reject"] == [1, 1]


EXP147 = "// ❌ Invalid: multi-line without parentheses\ntotal = price + tax +\n\t\tshipping\n"
BREAK2 = EXP147.index("\n\t\tshipping")


@pytest.mark.parametrize("text,line,span,passes", [
    ("start:\n\tx\n", 1, (0, 5), True),
    (EXP147, 3, (EXP147.index("shipping"), EXP147.index("shipping") + 8), True),
    (EXP147, 3, (len(EXP147), len(EXP147)), True),
    (EXP147, 3, (0, 2), False),
    (EXP147, 3, (BREAK2 - 1, BREAK2), False),
    (EXP147, 3, (BREAK2, BREAK2 + 3), True),
])
def test_dgr13_where_a_reject_case_must_fail(text, line, span, passes):
    assert dg.reject_ok(text, line, span) is passes


def test_dgr13_pending_counts_as_a_failure(repo, monkeypatch):
    root, nodes = repo
    lines = good_status(nodes)
    lines[0].update(state="pending", reason="open: " + cite(nodes, "PRO-1", "x")[3:])
    reseal_with(root, nodes, lines=lines)
    problems, summary = run_check(root)
    assert ("pending", "TST-1") in names(problems)
    assert summary["states"] == {"derived": 4, "pending": 1}
    assert main_in(root, monkeypatch, "check") == 1


def test_dgr13_a_pending_gap_reason_must_cite_a_norm(repo):
    root, nodes = repo
    lines = good_status(nodes)
    lines[3].update(state="pending", reason="no norm says it")
    reseal_with(root, nodes, lines=lines)
    problems, _ = run_check(root)
    assert any(p[1] == "TST-4" and p[2] == "the reason cites no norm" for p in problems)


def test_dgr13_a_fragment_with_no_form_of_cex4_that_is_derived(repo, monkeypatch):
    root, nodes = repo
    add_fragment(root, nodes, fence("clean-language", "start:", "\tprint(7)"))
    problems, summary = run_check(root)
    assert any(p[:2] == ("opening line", "TST-7") and "CEX-4" in p[2] for p in problems), problems
    assert not any(p[1] == "TST-7" and p[0] in ("accept", "reject") for p in problems)
    assert summary["parsed"] == {"accept": [4, 4], "reject": [1, 1]}
    assert main_in(root, monkeypatch, "check") == 1


def test_dgr13_a_fragment_with_no_form_of_cex4_that_is_pending_is_not_parsed(repo):
    root, nodes = repo
    add_fragment(root, nodes, fence("clean-language", "start", "x"), "pending", derived_norms.NO_FORM_REASON)
    problems, summary = run_check(root)
    assert names(problems) == [("pending", "TST-7")]
    assert summary["parsed"] == {"accept": [4, 4], "reject": [1, 1]}


def test_dgr13_a_citation_names_the_fragment_never_a_case(repo):
    root, nodes = repo
    hash1 = nodes[1]["tree_hash"][:8]
    grammar = good_grammar(nodes).replace(f"// TST-1@{hash1}:", f"// TST-1#1@{hash1}:")
    reseal_with(root, nodes, grammar)
    problems, _ = run_check(root)
    assert any(p[0] == "citation" and p[2] == "not a citation" for p in problems)
    assert ("cited", "TST-1") in names(problems)


def test_dgr13_a_derived_fragment_that_no_statement_cites(repo):
    root, nodes = repo
    reseal_with(root, nodes, good_grammar(nodes).replace(cite(nodes, "TST-5", "arguments may span lines inside parentheses") + "\n", ""))
    problems, _ = run_check(root)
    assert ("cited", "TST-5") in names(problems)


def test_dgr13_an_unused_statement(repo):
    root, nodes = repo
    reseal_with(root, nodes, good_grammar(nodes) + cite(nodes, "TST-1") + '\nlonely: "x"\n')
    problems, _ = run_check(root)
    assert ("usage", "lonely") in names(problems)


def test_dgr13_the_grammar_does_not_load(repo):
    root, nodes = repo
    reseal_with(root, nodes, good_grammar(nodes).replace("start: _NL? section+", "start: _NL? section+ missing_rule"))
    problems, _ = run_check(root)
    assert [p for p in problems if p[0] == "build"]


@pytest.mark.parametrize("missing", ["tree", "grammar", "status"])
def test_dgr13_missing_inputs_exit_2(repo, monkeypatch, missing):
    root, _ = repo
    (root / {"tree": derived_norms.TREE_REL, "grammar": derived_norms.GRAMMAR_REL, "status": dg.STATUS_REL}[missing]).unlink()
    assert main_in(root, monkeypatch, "check") == 2


def test_dgr13_lark_that_cannot_be_loaded_exits_2(repo, monkeypatch):
    root, _ = repo

    def no_lark():
        raise derived_norms.InputError("Lark cannot be loaded: test")
    monkeypatch.setattr(dg, "import_lark", no_lark)
    assert main_in(root, monkeypatch, "check") == 2


def test_dgr13_the_specs_commit_must_match(repo):
    root, nodes = repo
    write_tree(root, nodes, {"type": "meta", "specs_commit": "e" * 40})
    problems, _ = run_check(root)
    assert ("meta", "specs_commit") in names(problems)


@pytest.mark.parametrize("recorded,problem,words", [
    ({"plugin": "clean-derived-norms", "version": VERSION, "marketplace_commit": SHA}, False, []),
    ({"plugin": "clean-derived-norms", "version": VERSION, "marketplace_commit": "none"}, False, []),
    ({"plugin": "clean-derived-norms", "version": "0.0.9", "marketplace_commit": SHA}, True, ["'0.0.9'", "'0.1.0'"]),
    ({"plugin": "derive-grammar", "version": VERSION, "marketplace_commit": SHA}, True, ["'derive-grammar'", "'clean-derived-norms'"]),
    ({"plugin": "clean-derived-norms", "version": VERSION}, True, ["exactly the fields plugin, version, marketplace_commit"]),
    ("clean-derived-norms", True, ["not an object"]),
])
def test_dgr13_the_generator_at_check_time(repo, monkeypatch, recorded, problem, words):
    root, _ = repo
    set_meta(root, "generator", recorded)
    problems = meta_problems(root)
    if not problem:
        assert problems == []
        return
    assert names(problems) == [("meta", "generator")]
    assert all(w in problems[0][2] for w in words), problems
    assert main_in(root, monkeypatch, "check") == 1


def test_dgr13_a_meta_line_without_generator(repo, monkeypatch):
    root, _ = repo
    set_meta(root, "generator", drop=True)
    problems = meta_problems(root)
    assert ("meta", "generator") in names(problems)
    assert any("exactly the fields" in p[2] for p in problems)
    assert main_in(root, monkeypatch, "check") == 1


def test_dgr13_check_runs_from_the_version_of_the_plugin(repo, plugin):
    root, _ = repo
    (plugin / ".claude-plugin" / "plugin.json").write_text(json.dumps({"version": "0.2.0"}))
    problems = meta_problems(root)
    assert names(problems) == [("meta", "generator")] and "'0.2.0'" in problems[0][2]


@pytest.mark.parametrize("value", ["", None, 5, "claude opus", "claude/opus", "modèle", "claude-opus-5-5\n"])
def test_dgr13_an_empty_or_malformed_model_fails(repo, monkeypatch, value):
    root, _ = repo
    set_meta(root, "model", value)
    assert names(meta_problems(root)) == [("meta", "model")]
    assert main_in(root, monkeypatch, "check") == 1


def test_dgr13_a_missing_model_fails(repo, monkeypatch):
    root, _ = repo
    set_meta(root, "model", drop=True)
    problems = meta_problems(root)
    assert ("meta", "model") in names(problems)
    assert any("exactly the fields" in p[2] for p in problems)
    assert main_in(root, monkeypatch, "check") == 1


@pytest.mark.parametrize("value", ["claude-opus-5-5", "claude-sonnet-4.5", "gpt_5", "M1"])
def test_dgr13_a_good_model_passes(repo, value):
    root, _ = repo
    set_meta(root, "model", value)
    assert meta_problems(root) == []


ISSUE_12 = "https://github.com/Ivan-Pasco/clean-language-foundation/issues/12"
ISSUE_13 = "https://github.com/Ivan-Pasco/clean-language-foundation/issues/13"


def issue_problems(repo, first, second):
    """TST-1 and TST-2 pending, with the issues given; the problems "issue" of check."""
    root, nodes = repo
    lines = good_status(nodes)
    reason = cite(nodes, "PRO-1", "x")[3:]
    lines[0].update(state="pending", reason=reason, issue=first)
    lines[1].update(state="pending", reason=reason, issue=second)
    reseal_with(root, nodes, lines=lines)
    problems, _ = run_check(root)
    return [p for p in problems if p[0] == "issue"]


def test_dgr13_two_status_lines_with_one_issue_url_fail(repo, monkeypatch):
    found = issue_problems(repo, ISSUE_12, ISSUE_12)
    assert len(found) == 1, found
    assert found[0][1] == "TST-2"
    assert "TST-1" in found[0][2] and ISSUE_12 in found[0][2]
    assert main_in(repo[0], monkeypatch, "check") == 1


def test_dgr13_distinct_issue_urls_pass(repo):
    assert issue_problems(repo, ISSUE_12, ISSUE_13) == []


def test_dgr13_null_issues_are_not_compared(repo):
    assert issue_problems(repo, None, None) == []


def test_dgr13_the_unique_issue_check_names_every_repeat():
    rows = [(n, "", {"type": "fragment", "id": i, "issue": u}, None)
            for n, (i, u) in enumerate([("A-1", ISSUE_12), ("B-1", ISSUE_13), ("C-1", ISSUE_12), ("D-1", ISSUE_12)], 2)]
    rows.insert(0, (1, "", {"type": "meta"}, None))
    rows.append((9, "{bad", None, "not JSON"))
    found = derived_norms.check_unique_issues(rows)
    assert [(p[0], p[1]) for p in found] == [("issue", "C-1"), ("issue", "D-1")]
    assert all("A-1" in p[2] for p in found)


def test_dgr13_a_stale_script_citation_still_fails_check(repo):
    root, _ = repo
    code = [("script.py", "# LEX-20@11111111: each indentation level is exactly one tab character\n")]
    problems, _ = dg.check(root, code)
    assert ("script-citation", "LEX-20", "script.py line 1: LEX-20 has the norm hash 8c358626") in problems


def no_fragment_repo(root, grammar=""):
    nodes = [n for n in base_nodes() if n["kind"] != "code_block"]
    write_tree(root, nodes)
    write_outputs(root, grammar, [])
    dg.seal(root, MODEL)
    return nodes


def test_dgr13_no_fragment_yet(tmp_path, monkeypatch, capsys):
    root = tmp_path / "repo"
    no_fragment_repo(root, "this would not build\n")
    assert (root / dg.STATUS_REL).read_text().count("\n") == 1
    assert dg.worklist(root) == []
    problems, summary = run_check(root)
    assert problems == []
    assert main_in(root, monkeypatch, "check") == 0
    assert capsys.readouterr().out.splitlines() == ["fragments: 0 derived, 0 pending; accept parsed 0/0; reject rejected 0/0; problems: 0"]


def test_dgr13_no_fragment_yet_still_checks_the_meta_line_and_the_script(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    no_fragment_repo(root)
    (root / derived_norms.GRAMMAR_REL).write_text("changed\n")
    code = [("script.py", "# LEX-21@11111111: mixing tabs and spaces for indentation is not allowed\n")]
    problems, _ = dg.check(root, code)
    assert names(problems) == [("meta", "grammar_sha256"), ("script-citation", "LEX-21")]
    assert main_in(root, monkeypatch, "check") == 1


def test_dgr13_no_fragment_yet_with_a_status_file_of_the_local_skill(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    no_fragment_repo(root)
    path = root / dg.STATUS_REL
    _, _, body = path.read_text().partition("\n")
    old = {"type": "meta", "foundation_commit": SPECS, "generators_commit": SHA, "model": MODEL,
           "grammar_sha256": hashlib.sha256(b"").hexdigest(), "status_sha256": hashlib.sha256(body.encode()).hexdigest()}
    path.write_text(json.dumps(old, separators=(",", ":")) + "\n" + body)
    assert dg.worklist(root) == []
    problems, _ = run_check(root)
    assert ("meta", "generator") in names(problems) and ("meta", "specs_commit") in names(problems)
    assert any("exactly the fields" in p[2] for p in problems)
    assert main_in(root, monkeypatch, "check") == 1


# ------------------------------------------------------------------ DGR-17


def test_dgr17_a_change_by_hand_after_seal_fails(repo, monkeypatch):
    root, _ = repo
    path = root / derived_norms.GRAMMAR_REL
    path.write_text(path.read_text() + "\n")
    problems, _ = run_check(root)
    assert ("meta", "grammar_sha256") in names(problems)
    assert main_in(root, monkeypatch, "check") == 1


def test_dgr17_a_status_line_changed_after_seal_fails(repo):
    root, _ = repo
    path = root / dg.STATUS_REL
    path.write_text(path.read_text().replace('"TST-1","hash"', '"TST-1", "hash"'))
    problems, _ = run_check(root)
    assert ("meta", "status_sha256") in names(problems)


# ------------------------------------------------------------------ DGR-18


def tree_repo(root, nodes):
    """A git repository whose history holds data/tree.jsonl with the nodes; the commit."""
    git_init(root)
    write_tree(root, nodes)
    git(root, "add", "--", derived_norms.TREE_REL)
    git(root, "commit", "-q", "-m", "build")
    return git(root, "rev-parse", "HEAD")


def with_node(nodes, norm_id, **changes):
    return [dict(n, **changes) if n["id"] == norm_id else n for n in nodes]


def test_dgr18_first_words_cut_at_a_word_and_never_inside_a_code_span():
    text = "- Mixing tabs and spaces for indentation is not allowed (`SYN003`)"
    assert derived_norms.first_words(text) == "Mixing tabs and spaces for indentation is not allowed"
    assert "`" not in derived_norms.first_words("`match` takes `x`")
    assert derived_norms.first_words("## A short title (`SYN001`)") == "A short title (SYN001)"
    assert derived_norms.first_words("a (b c d e", limit=6) == "a"
    assert derived_norms.first_words("") == ""


def test_dgr18_first_words_never_end_with_an_open_parenthesis_or_backtick():
    for limit in range(1, 70):
        words = derived_norms.first_words("- Mixing tabs and spaces for indentation is not allowed (`SYN003`), never", limit)
        assert len(words) <= limit
        assert words.count("(") <= words.count(")") and "`" not in words
        assert not words.endswith(("(", " ", ",", ";", ":", "-"))


def test_dgr18_the_text_of_a_leaf_norm_is_its_own_text():
    tree = derived_norms.Tree(base_nodes())
    assert derived_norms.norm_text(tree, tree.nodes["LEX-21"]) == "- Mixing tabs and spaces for indentation is not allowed"


def test_dgr18_the_text_of_a_norm_holds_its_active_children_one_per_line():
    nodes = [node("SEC-1", "section", "", parent=None),
             node("LST-1", "list", "\n\n"),
             node("LST-2", "item", "- one", parent="LST-1"),
             node("LST-3", "item", "- old", parent="LST-1", status="retired"),
             node("LST-4", "item", "- two\n", parent="LST-1")]
    tree = derived_norms.Tree(nodes)
    assert derived_norms.norm_text(tree, tree.nodes["LST-1"]) == "- one\n- two"


def test_dgr18_no_stale_citation_gives_no_item(tmp_path):
    nodes = base_nodes()
    root = tmp_path / "repo"
    tree_repo(root, nodes)
    assert derived_norms.stale_script_citations(root, derived_norms.Tree(nodes), CODE_OF_THE_SCRIPT) == []


def test_dgr18_a_changed_norm_gives_its_old_and_new_text_and_the_line(tmp_path):
    nodes = base_nodes()
    root = tmp_path / "repo"
    old_commit = tree_repo(root, nodes)
    write_tree(root, with_node(nodes, "LEX-20", own_text="- one tab per level, never a space", tree_hash="12345678" + "0" * 56))
    text = "x = 1\n    # LEX-20@8c358626: one tab per level\n"
    items = derived_norms.stale_script_citations(root, derived_norms.load_tree(root), [("script.py", text)])
    assert items == [{"id": "LEX-20", "state": "changed", "current_hash": "12345678",
                      "new_text": "- one tab per level, never a space",
                      "citations": [{"path": "script.py", "line": 2, "text": "# LEX-20@8c358626: one tab per level", "cited_hash": "8c358626",
                                     "old_text": "- one tab per level", "old_commit": old_commit}]}]


def test_dgr18_the_old_text_comes_from_the_newest_version_that_has_the_hash(tmp_path):
    nodes = base_nodes()
    root = tmp_path / "repo"
    tree_repo(root, nodes)
    write_tree(root, with_node(nodes, "LEX-20", own_text="- middle", tree_hash="aaaaaaaa" + "0" * 56))
    git(root, "add", "--", derived_norms.TREE_REL)
    git(root, "commit", "-q", "-m", "build 2")
    middle_commit = git(root, "rev-parse", "HEAD")
    write_tree(root, with_node(nodes, "LEX-20", own_text="- now", tree_hash="bbbbbbbb" + "0" * 56))
    items = derived_norms.stale_script_citations(root, derived_norms.load_tree(root), [("script.py", "# LEX-20@aaaaaaaa: a\n# LEX-20@8c358626: b\n")])
    assert len(items) == 1
    assert [(c["line"], c["old_text"]) for c in items[0]["citations"]] == [(1, "- middle"), (2, "- one tab per level")]
    assert items[0]["citations"][0]["old_commit"] == middle_commit


@pytest.mark.parametrize("change,state", [("retired", "retired"), ("gone", "gone")])
def test_dgr18_a_retired_or_gone_norm_has_no_new_text(tmp_path, change, state):
    nodes = base_nodes()
    root = tmp_path / "repo"
    tree_repo(root, nodes)
    now = with_node(nodes, "LEX-21", status="retired") if change == "retired" else [n for n in nodes if n["id"] != "LEX-21"]
    write_tree(root, now)
    items = derived_norms.stale_script_citations(root, derived_norms.load_tree(root), CODE_OF_THE_SCRIPT)
    assert [(i["id"], i["state"], i["current_hash"], i["new_text"]) for i in items] == [("LEX-21", state, None, None)]
    citation = items[0]["citations"][0]
    assert citation["cited_hash"] == "7474dff8" and citation["text"].startswith("# LEX-21@7474dff8: ")
    assert citation["old_text"] == "- Mixing tabs and spaces for indentation is not allowed"
    assert citation["path"] == "scripts/derived_norms.py"
    assert (MODULE / citation["path"]).read_text().split("\n")[citation["line"] - 1].strip() == citation["text"]


def test_dgr18_an_old_hash_that_no_version_has_gives_null(tmp_path):
    nodes = base_nodes()
    root = tmp_path / "repo"
    tree_repo(root, nodes)
    items = derived_norms.stale_script_citations(root, derived_norms.Tree(nodes), [("script.py", "# LEX-20@11111111: x\n")])
    assert items[0]["citations"][0]["old_text"] is None and items[0]["citations"][0]["old_commit"] is None


def test_dgr18_no_git_history_gives_null_old_text(tmp_path):
    nodes = base_nodes()
    write_tree(tmp_path, nodes)
    items = derived_norms.stale_script_citations(tmp_path, derived_norms.Tree(nodes), [("script.py", "# LEX-20@11111111: x\n")])
    assert items[0]["citations"][0]["old_text"] is None


def test_dgr18_a_line_that_is_not_a_citation_gives_no_item(tmp_path):
    nodes = base_nodes()
    write_tree(tmp_path, nodes)
    assert derived_norms.stale_script_citations(tmp_path, derived_norms.Tree(nodes), [("script.py", "# LEX-20@8c358626:\n# LEX-20@8C358626: x\n")]) == []


def test_dgr18_one_item_per_norm_in_the_order_of_the_script(tmp_path):
    nodes = base_nodes()
    write_tree(tmp_path, nodes)
    text = "# LEX-21@11111111: a\n# LEX-20@11111111: b\n# LEX-21@22222222: c\n"
    items = derived_norms.stale_script_citations(tmp_path, derived_norms.Tree(nodes), [("script.py", text)])
    assert [(i["id"], [c["line"] for c in i["citations"]]) for i in items] == [("LEX-21", [1, 3]), ("LEX-20", [2])]
    assert list(items[0]) == ["id", "state", "current_hash", "new_text", "citations"]
    assert list(items[0]["citations"][0]) == ["path", "line", "text", "cited_hash", "old_text", "old_commit"]


def test_dgr18_the_files_of_the_code_of_the_script_in_their_order(tmp_path):
    nodes = base_nodes()
    write_tree(tmp_path, nodes)
    code = [("use-cases/derive-grammar/derive_grammar.py", "# LEX-20@11111111: a\n"),
            ("scripts/derived_norms.py", "# LEX-21@11111111: b\n# LEX-20@22222222: c\n")]
    items = derived_norms.stale_script_citations(tmp_path, derived_norms.Tree(nodes), code)
    assert [(i["id"], [(c["path"], c["line"]) for c in i["citations"]]) for i in items] == [
        ("LEX-20", [("use-cases/derive-grammar/derive_grammar.py", 1), ("scripts/derived_norms.py", 2)]),
        ("LEX-21", [("scripts/derived_norms.py", 1)])]


def test_dgr18_the_command_prints_one_json_line_per_stale_norm(tmp_path, monkeypatch, capsys):
    nodes = base_nodes()
    root = tmp_path / "repo"
    tree_repo(root, nodes)
    write_tree(root, with_node(nodes, "EXP-27", own_text="changed", tree_hash="cccccccc" + "0" * 56))
    assert main_in(root, monkeypatch, "stale-citations") == 0
    lines = [json.loads(l) for l in capsys.readouterr().out.splitlines()]
    assert [(i["id"], i["state"], i["current_hash"]) for i in lines] == [("EXP-27", "changed", "cccccccc")]


def test_dgr18_the_command_prints_nothing_when_every_citation_checks(tmp_path, monkeypatch, capsys):
    root = tmp_path / "repo"
    tree_repo(root, base_nodes())
    assert main_in(root, monkeypatch, "stale-citations") == 0
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("bad", [None, "{bad"])
def test_dgr18_the_command_exits_2_without_a_readable_tree(tmp_path, monkeypatch, bad):
    if bad is not None:
        (tmp_path / "data").mkdir()
        (tmp_path / derived_norms.TREE_REL).write_text(bad + "\n")
    assert main_in(tmp_path, monkeypatch, "stale-citations") == 2


# ------------------------------------------------------------------ the docstrings


def test_every_function_cites_its_rule():
    import ast
    tree = ast.parse(SCRIPT.read_text())
    missing = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))
               and "Spec: DGR-" not in (ast.get_docstring(n) or "")]
    assert missing == []


# ------------------------------------------------------------------ DEV-3 regressions


def with_grammar(root, nodes, text):
    write_outputs(root, text, good_status(nodes))
    dg.seal(root, MODEL)
    return run_check(root)[0]


def test_dgr11_reserved_built_from_terminals_is_refused(repo):
    root, nodes = repo
    text = good_grammar(nodes).replace('RESERVED: "start" | "functions"', "RESERVED: KW_START\n" + cite(nodes, "TST-1", "a keyword") + '\nKW_START: "start"')
    assert ("names", "RESERVED") in names(with_grammar(root, nodes, text))


def test_dgr2_grounding_needs_a_direct_user_that_cites_a_fragment(repo):
    root, nodes = repo
    text = good_grammar(nodes).replace("statement: NAME OPEN_PAREN NUMBER CLOSE_PAREN _NL", "statement: NAME OPEN_PAREN body CLOSE_PAREN _NL")
    text += cite(nodes, "PRO-3", "a body") + "\nbody: item\n" + cite(nodes, "PRO-3", "an item") + "\nitem: NUMBER\n"
    assert ("source", "item") in names(with_grammar(root, nodes, text))


def test_dgr13_an_unused_bracket_pair_is_reported(repo):
    root, nodes = repo
    text = good_grammar(nodes) + cite(nodes, "TST-1", "angle brackets") + '\nOPEN_ANGLE: "<"\n' + cite(nodes, "TST-1", "angle brackets") + '\nCLOSE_ANGLE: ">"\n'
    found = names(with_grammar(root, nodes, text))
    assert ("usage", "OPEN_ANGLE") in found and ("usage", "CLOSE_ANGLE") in found


def test_dgr13_a_state_that_is_no_string_does_not_crash(repo):
    root, nodes = repo
    lines = good_status(nodes)
    lines[0]["state"] = ["derived"]
    write_outputs(root, good_grammar(nodes), lines)
    dg.seal(root, MODEL)
    problems, _ = run_check(root)
    assert problems


def test_dgr8_an_alternative_at_column_0_continues_its_statement(repo):
    root, nodes = repo
    text = good_grammar(nodes).replace("statement: NAME OPEN_PAREN NUMBER CLOSE_PAREN _NL", "statement: NAME OPEN_PAREN NUMBER CLOSE_PAREN _NL\n| NAME _NL")
    found = names(with_grammar(root, nodes, text))
    assert not any(p[0] == "statement" for p in found) and not any(p[0] == "citation" and p[1].startswith("|") for p in found)


# ------------------------------------------------------------------ DGR-19


TWO_FILES = "\n".join([
    "// a program of two files",
    "// file: app/utils.cln",
    "functions:",
    "\tinteger double(integer n)",
    "\t\treturn n * 2",
    "",
    "// file: app/main.cln",
    "start:",
    "\tprint(double(21))",
]) + "\n"


def test_dgr19_the_files_of_a_program_of_two_files():
    files = derived_norms.program_files(TWO_FILES)
    lines = TWO_FILES.split("\n")
    assert [(f.number_of_file, f.path_of_file_line, f.first_line_in_case_text, f.file_line) for f in files] == [(1, "app/utils.cln", 2, True), (2, "app/main.cln", 7, True)]
    assert files[0].file_text == "\n".join(lines[1:5]) + "\n"
    assert files[1].file_text == "\n".join(lines[6:9]) + "\n"
    assert files[1].offset_of_file == TWO_FILES.index("// file: app/main.cln")
    assert all("a program of two files" not in f.file_text for f in files)


def test_dgr19_a_case_text_with_no_file_line_is_one_file():
    text = "start:\n\tprint(1)\n"
    [only] = derived_norms.program_files(text)
    assert (only.number_of_file, only.path_of_file_line, only.offset_of_file, only.first_line_in_case_text, only.file_text, only.file_line) == (1, None, 0, 1, text, False)


@pytest.mark.parametrize("line,path,opens", [
    ("// file: a.cln", "a.cln", True),
    ("// file:a.cln", None, True),
    ("// file: ", "", True),
    ("// file: dir/x y.cln", "dir/x y.cln", True),
    ("\t// file: a.cln", None, False),
    (" // file: a.cln", None, False),
    ("//file: a.cln", None, False),
    ("// File: a.cln", None, False),
])
def test_dgr19_only_a_line_that_starts_at_column_1_with_the_mark_opens_a_file(line, path, opens):
    files = derived_norms.program_files("start:\n\tprint(1)\n" + line + "\nstart:\n\tprint(2)\n")
    if opens:
        assert len(files) == 1 and files[0].path_of_file_line == path and files[0].first_line_in_case_text == 3
    else:
        assert len(files) == 1 and not files[0].file_line


def test_dgr19_a_file_line_inside_a_block_comment_opens_a_file():
    files = derived_norms.program_files("// file: a.cln\n/* a comment\n// file: b.cln\n*/\n")
    assert [f.path_of_file_line for f in files] == ["a.cln", "b.cln"]
    assert files[0].file_text == "// file: a.cln\n/* a comment\n"


def two_file_fragment(info, first, second, paths=("app/a.cln", "app/b.cln")):
    return fence(info, f"// file: {paths[0]}", "start:", first, f"// file: {paths[1]}", "start:", second)


def test_dgr19_each_file_is_parsed_alone():
    lark_parser = fixture_parser()
    # A bracket that file 1 leaves open does not go on into file 2: file 1 fails, and alone it parses with ")".
    text = "// file: a.cln\nstart:\n\tprint(\n// file: b.cln\n\t\t1)\n"
    failure = dg.try_parse(*lark_parser, text)
    assert failure is not None and "(file 1, a.cln, line " in failure[2]
    assert failure[1] <= text.index("// file: b.cln")
    assert dg.try_parse(*lark_parser, "start:\n\tprint(\n\t\t1)\n") is None
    assert dg.try_parse(*lark_parser, "// file: a.cln\nstart:\n\tprint(1)\n// file: b.cln\nstart:\n\tprint(2)\n") is None


def test_dgr19_an_accept_program_of_two_files_passes(repo):
    root, nodes = repo
    add_fragment(root, nodes, two_file_fragment(VALID, "\tprint(1)", "\tprint(2)"))
    problems, summary = run_check(root)
    assert problems == [] and summary["parsed"]["accept"] == [5, 5]


def test_dgr19_an_accept_program_whose_second_file_does_not_parse(repo):
    root, nodes = repo
    add_fragment(root, nodes, two_file_fragment(VALID, "\tprint(1)", "\tprint 2"))
    problems, _ = run_check(root)
    [problem] = [p for p in problems if p[:2] == ("accept", "TST-7")]
    assert problem[2].startswith("does not parse: line 6 (file 2, app/b.cln, line 3): UnexpectedToken: ")


@pytest.mark.parametrize("line,first,second,passes", [
    (6, "\tprint(1)", "\tprint 2", True),
    (6, "\tprint(1)", "\tprint(", True),
    (6, "\tprint 1", "\tprint 2", False),
    (6, "\tprint(1)", "\tprint(2)", False),
    (1, "\tprint(1)", "\tprint 2", True),
])
def test_dgr19_where_a_program_of_several_files_fails(repo, line, first, second, passes):
    root, nodes = repo
    add_fragment(root, nodes, two_file_fragment(syntax(line), first, second))
    problems, summary = run_check(root)
    assert (("reject", "TST-7") not in names(problems)) is passes, problems
    assert summary["parsed"]["reject"] == ([2, 2] if passes else [1, 2])


def test_dgr19_the_message_of_a_file_with_no_path():
    lark_parser = fixture_parser()
    failure = dg.try_parse(*lark_parser, "// file: a.cln\nstart:\n\tprint(1)\n// file:b.cln\nstart:\n\tprint 2\n")
    assert failure[2].startswith("line 6 (file 2, no path, line 3): UnexpectedToken: ")


def test_dgr19_a_case_text_with_no_file_line_keeps_its_message():
    lark_parser = fixture_parser()
    failure = dg.try_parse(*lark_parser, "start:\n\tprint 1\n")
    assert failure[2].startswith("line 2: UnexpectedToken: ")


def test_dgr19_the_script_checks_no_rule_of_the_files(repo):
    root, nodes = repo
    own = fence(VALID, "start:", "\tprint(0)", "// file: same.cln", "start:", "\tprint(1)",
                "// file: same.cln", "start:", "\tprint(2)", "// file: ../bad path.lean", "start:", "\tprint(3)")
    add_fragment(root, nodes, own)
    problems, summary = run_check(root)
    assert problems == [] and summary["parsed"]["accept"] == [5, 5]


def test_dgr19_an_expected_line_before_the_first_file_line(repo):
    root, nodes = repo
    add_fragment(root, nodes, fence(syntax(2), "// a", "// b", "// file: a.cln", "start:", "\tprint 1"))
    problems, summary = run_check(root)
    assert ("reject", "TST-7") not in names(problems)
    assert summary["parsed"]["reject"] == [2, 2]


def test_dgr19_a_program_of_several_files_is_one_case(repo):
    root, nodes = repo
    add_fragment(root, nodes, two_file_fragment(VALID, "\tprint(1)", "\tprint(2)"))
    line = next(json.loads(l) for l in (root / dg.STATUS_REL).read_text().splitlines() if '"TST-7"' in l)
    assert list(line) == dg.FRAGMENT_KEYS and line["cases"] == ["accept"]
