"""Tests of use-cases/derive-semantics/derive_semantics.py, on small fixtures in temporary folders.

Run from the root of the marketplace:
    uv run --with pytest --with "lark[interegular]" python3 -I -B -m pytest -q -p no:cacheprovider \
        apps/clean-language/modules/clean-derived-norms/tests
The tests that build Lean are skipped when lake is absent.
Spec: use-cases/derive-semantics/specs/derive-semantics.md (DSM). Each test names the clause it checks.
"""

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1]
SCRIPT = MODULE / "use-cases" / "derive-semantics" / "derive_semantics.py"
_spec = importlib.util.spec_from_file_location("derive_semantics", SCRIPT)
ds = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ds)
# The module script, which the script imports (CDN-7): the same module as the script's.
sys.path.insert(0, str(MODULE / "scripts"))
import derived_norms  # noqa: E402

# The code of the script of this use case: the script alone (DSM-17).
CODE_OF_THE_SCRIPT = derived_norms.read_code_of_the_script(SCRIPT)

SPECS = "e" * 40
MODEL = "claude-opus-5-5"
VERSION = "0.1.0"
F = "```"


# ------------------------------------------------------------------ fixtures


def h8(norm_id, text):
    return hashlib.sha256((norm_id + text).encode()).hexdigest()[:8]


def fence(info, *lines):
    return f"{F}{info}\n" + "\n".join(lines) + f"\n{F}"


VALID = "clean-language expect=valid"


def section(parent_id, parts, start=0, file="specs/a.md"):
    """A section and its children laid out in one file: parts are gaps (str) and children (id, kind, own text)."""
    nodes, position, gaps = [], start, []
    for part in parts:
        if isinstance(part, str):
            gaps.append(part)
            position += len(part.encode())
            continue
        norm_id, kind, own = part
        size = len(own.encode())
        nodes.append({"type": "node", "id": norm_id, "kind": kind, "file": file, "parent": parent_id, "start": position,
                      "end": position + size, "own_text": own, "own_hash": "0" * 64,
                      "tree_hash": h8(norm_id, own) + "0" * 56, "status": "active", "to_review": False, "changed_since": None})
        position += size
    head = {"type": "node", "id": parent_id, "kind": "section", "file": file, "parent": None, "start": start,
            "end": position, "own_text": "".join(gaps), "own_hash": "0" * 64, "tree_hash": h8(parent_id, "") + "0" * 56,
            "status": "active", "to_review": False, "changed_since": None}
    return [head] + nodes


def base_parts():
    return [
        ("TST-1", "code_block", fence(VALID, "start:", '\tprint("a")', '\tprint("b")')),
        "\n\n",
        ("OUT-1", "code_block", fence("clean-language-output", "a", "b")),
        "\n\n",
        ("TST-2", "code_block", fence(VALID, "start:", '\tprint("c")   // prints: z')),
        "\n\n",
        ("PRO-1", "paragraph", "print writes its text and a line feed"),
        "\n\n",
        ("OUT-2", "code_block", fence("clean-language-output", "never read")),
        "\n\n",
        ("TST-3", "code_block", fence("clean-language expect=error code=SEM001", "start:", '\tstop("SEM001")')),
        "\n\n",
        ("TST-4", "code_block", fence("clean-language expect=syntax-error code=SYN002 line=2", "start:", "\tprint(")),
        "\n\n",
        ("TST-5", "code_block", fence("clean-language", "start:", '\tprint("d")')),
        "\n\n",
        ("TST-6", "code_block", fence(VALID, "start:", "\tprint(1)")),
        "\n\n",
        ("PRO-2", "paragraph", "stop ends the program with its code"),
        "\n",
    ]


def base_nodes():
    return section("SEC-1", base_parts())


SEMANTIC = ["TST-1", "TST-2", "TST-3", "TST-5", "TST-6"]

GRAMMAR = "\n".join([
    "start: _NL? section+",
    'section: "start" ":" _NL _INDENT statement+ _DEDENT',
    'statement: "print" OPEN_PAREN STRING CLOSE_PAREN _NL',
    '    | "stop" OPEN_PAREN STRING CLOSE_PAREN _NL',
    'STRING: /"[^"\\n]*"/',
    'OPEN_PAREN: "("',
    'CLOSE_PAREN: ")"',
    "_NL: /(\\r?\\n[\\t ]*)+/",
    "WS: / +/",
    "COMMENT: /\\/\\/[^\\n]*/",
    "%ignore WS",
    "%ignore COMMENT",
    "%declare _INDENT _DEDENT",
    "",
])


def cite(nodes, norm_id, reason="a reason"):
    n = next(n for n in nodes if n["id"] == norm_id)
    return f"-- {norm_id}@{n['tree_hash'][:8]}: {reason}"


def lean_code(nodes):
    c = lambda i, r="shown here": cite(nodes, i, r)
    return {
        "Clean/Ast.lean": "\n".join([
            "namespace Clean", "",
            c("PRO-1", "a statement prints a text"), c("PRO-2", "or stops with a code"),
            "inductive Statement where", "  | print (text : String)", "  | stop (code : String)", "",
            "end Clean", ""]),
        "Clean/Syntax.lean": "\n".join([
            "import Fragment", "import Clean.Ast", "", "namespace Clean", "",
            c("PRO-1", "the text of a string is between its quotes"),
            "def unquote (text : String) : String := String.mk ((text.toList.drop 1).dropLast)", "",
            c("PRO-1", "the statements of a parse tree, in order"),
            "partial def statements : Fragment.Tree → List Statement",
            '  | .rule "statement" [.token word _, _, .token "STRING" text, _] =>',
            '    if word == "PRINT" then [Statement.print (unquote text)] else [Statement.stop (unquote text)]',
            "  | .rule _ children => children.foldl (fun found child => found ++ statements child) []",
            "  | _ => []", "", "end Clean", ""]),
        "Clean/Typing.lean": "\n".join([
            "import Clean.Ast", "", "namespace Clean", "",
            c("PRO-2", "no code at build time"),
            "def typing (_program : List Statement) : Option String := none", "", "end Clean", ""]),
        "Clean/Evaluation.lean": "\n".join([
            "import Fragment", "import Clean.Ast", "", "namespace Clean", "",
            c("PRO-1", "print writes its text and a line feed"), c("PRO-2", "stop ends the program with its code"),
            "def evaluate : List Statement → Fragment.Outcome",
            '  | [] => { code := none, output := "" }',
            "  | Statement.print text :: rest =>",
            "    let after := evaluate rest",
            '    { after with output := text ++ "\\n" ++ after.output }',
            '  | Statement.stop code :: _ => { code := some code, output := "" }', "", "end Clean", ""]),
        "Clean.lean": "\n".join([
            "import Fragment", "import Clean.Ast", "import Clean.Syntax", "import Clean.Typing", "import Clean.Evaluation", "",
            "namespace Clean", "",
            c("PRO-1", "a program is typed, then run"),
            "def outcome (tree : Fragment.Tree) : Fragment.Outcome :=",
            "  let program := statements tree",
            "  match typing program with",
            '  | some code => { code := some code, output := "" }',
            "  | none => evaluate program", "", "end Clean", ""]),
    }


def status_line(root, nodes, norm_id, state="derived", reason=None, issue=None):
    tree = derived_norms.Tree(nodes)
    fact = ds.facts(tree, ds.load_grammar(root), tree.nodes[norm_id])
    return {"type": "fragment", "id": norm_id, "hash": tree.norm_hash(norm_id), "cases": fact["cases"],
            "expected_output": fact["expected_output"], "parse_tree_hash": fact["parse_tree_hash"],
            "state": state, "reason": reason, "issue": issue}


def good_status(root, nodes):
    lines = [status_line(root, nodes, i) for i in ("TST-1", "TST-2", "TST-3")]
    lines.append(status_line(root, nodes, "TST-5", "pending", derived_norms.NO_FORM_REASON))
    lines.append(status_line(root, nodes, "TST-6", "pending", ds.NOT_PARSED_REASON))
    return lines


def write_tree(root, nodes):
    rows = [{"type": "meta", "specs_commit": SPECS, "generator_version": "0.1.0", "retired_prefixes": []},
            {"type": "file", "path": "specs/a.md", "prefix": "TST", "sha256": "0" * 64, "insertions": []}] + nodes
    (root / "data").mkdir(parents=True, exist_ok=True)
    (root / derived_norms.TREE_REL).write_text("".join(json.dumps(r) + "\n" for r in rows))


def write_lean(root, code):
    folder = root / ds.FOLDER_REL
    for rel, text in code.items():
        (folder / rel).parent.mkdir(parents=True, exist_ok=True)
        (folder / rel).write_text(text)


def write_status(root, lines):
    path = root / ds.STATUS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    head = json.dumps({"type": "meta"}) + "\n"
    path.write_text(head + "".join(json.dumps(l, ensure_ascii=False, separators=(",", ":")) + "\n" for l in lines))


@pytest.fixture(autouse=True)
def plugin(tmp_path, monkeypatch):
    """The plugin that runs the script: a plugin.json of version 0.1.0, and no record of installed plugins."""
    root = tmp_path / "plugin"
    (root / ".claude-plugin").mkdir(parents=True)
    (root / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "clean-derived-norms", "version": VERSION}))
    monkeypatch.setattr(ds, "PLUGIN_ROOT", root)
    monkeypatch.setattr(ds, "INSTALLED_PLUGINS", tmp_path / "installed_plugins.json")
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    return root


@pytest.fixture
def repo(tmp_path):
    """A repository of layer 2 with no commit yet, so with no list before the run (CDN-9)."""
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q")
    nodes = base_nodes()
    write_tree(root, nodes)
    (root / "specs-derived" / "grammar").mkdir(parents=True)
    (root / derived_norms.GRAMMAR_REL).write_text(GRAMMAR)
    write_lean(root, lean_code(nodes))
    write_status(root, good_status(root, nodes))
    ds.seal(root, MODEL)
    return root, nodes


class FakeLean:
    """A stand-in for lake: build gives a path, and each run gives the outcome of the fixture semantics."""

    def __init__(self, monkeypatch, outcomes=None, build_error=None):
        self.runs = []
        self.outcomes = outcomes or {}
        monkeypatch.setattr(ds, "lake_command", lambda: "lake")
        monkeypatch.setattr(ds, "build", lambda folder, work, lake: (None, build_error) if build_error else (Path("fragment"), None))
        monkeypatch.setattr(ds, "run_fragment", self.run)

    def run(self, executable, serialized):
        self.runs.append(serialized)
        texts = [l.split(" ", 2)[2] for l in serialized.split("\n") if l.startswith("token STRING ")]
        if serialized in self.outcomes:
            return self.outcomes[serialized]
        if any(l.startswith("token STOP ") for l in serialized.split("\n")):
            return texts[0].strip('"'), b"", None
        return None, "".join(t.strip('"') + "\n" for t in texts).encode(), None


def run_check(root):
    return ds.check(root, CODE_OF_THE_SCRIPT)


def names(problems):
    return [(p[0], p[1]) for p in problems]


def main_in(root, monkeypatch, *argv):
    monkeypatch.chdir(root)
    return ds.main(list(argv))


def reseal(root, nodes, code=None, lines=None):
    write_lean(root, code if code is not None else lean_code(nodes))
    write_status(root, lines if lines is not None else good_status(root, nodes))
    ds.seal(root, MODEL)


def git(root, *args):
    """Run git in a temporary repository of a test, never in a real repository."""
    return subprocess.run(["git", "-C", str(root), "-c", "user.email=t@example.com", "-c", "user.name=t",
                           "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
                          check=True, capture_output=True, text=True).stdout


def commit_the_list(root):
    """Commit the list of derived norms, as the step of layer 2 does at the end of a run (NRM-9): the list before the next run."""
    if not (root / ".git").exists():
        git(root, "init", "-q")
    git(root, "add", "--", ds.PATH_OF_LIST_OF_DERIVED_NORMS)
    git(root, "commit", "-q", "-m", "layer 2")


# ------------------------------------------------------------------ DSM-1


def test_dsm1_no_grammar_exits_2(repo, monkeypatch, capsys):
    root, _ = repo
    (root / derived_norms.GRAMMAR_REL).unlink()
    for command in (["worklist"], ["tree", "TST-1"], ["check"]):
        assert main_in(root, monkeypatch, *command) == 2
    assert "derive-grammar runs first" in capsys.readouterr().err


def test_dsm1_a_grammar_that_does_not_build_exits_2(repo, monkeypatch, capsys):
    root, _ = repo
    (root / derived_norms.GRAMMAR_REL).write_text("start: undefined_rule\n")
    assert main_in(root, monkeypatch, "worklist") == 2
    assert "the grammar does not build" in capsys.readouterr().err


def test_dsm1_check_writes_nothing_in_the_repository(repo, monkeypatch):
    root, _ = repo
    FakeLean(monkeypatch)
    before = sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))
    run_check(root)
    assert sorted(p.relative_to(root).as_posix() for p in root.rglob("*")) == before


# ------------------------------------------------------------------ DSM-2


def test_dsm2_which_fragments_are_semantic_fragments(repo):
    root, _ = repo
    tree = derived_norms.load_tree(root)
    assert [n["id"] for n in ds.semantic_fragments(tree)] == SEMANTIC


def test_dsm2_the_expected_output_of_a_fragment(repo):
    root, _ = repo
    tree = derived_norms.load_tree(root)
    assert ds.expected_output(tree, tree.nodes["TST-1"])["id"] == "OUT-1"
    assert ds.expected_output(tree, tree.nodes["TST-2"]) is None  # a paragraph comes next
    assert ds.expected_output(tree, tree.nodes["TST-3"]) is None


@pytest.mark.parametrize("gap,info,first,found", [
    ("\n\n", "clean-language-output", VALID, True),
    ("\n", "clean-language-output", VALID, True),
    ("\n  \t\n", "clean-language-output", VALID, True),
    ("\nIt prints:\n", "clean-language-output", VALID, False),
    ("\n\n", "clean-language-output text", VALID, False),
    ("\n\n", "clean-language-output", "clean-language expect=error code=SEM004", False),
])
def test_dsm2_the_expected_output_cases(gap, info, first, found):
    nodes = section("SEC-1", [("A-1", "code_block", fence(first, "start:", '\tprint("a")')), gap,
                              ("A-2", "code_block", fence(info, "a"))])
    tree = derived_norms.Tree(nodes)
    assert (ds.expected_output(tree, tree.nodes["A-1"]) is not None) is found


def test_dsm2_the_expected_output_text():
    nodes = section("SEC-1", [("A-1", "code_block", fence("clean-language-output", "Hello, World!", "42")),
                              "\n", ("A-2", "code_block", f"{F}clean-language-output\n{F}"),
                              "\n", ("A-3", "code_block", fence("clean-language-output", "a  ", "", "b"))])
    tree = derived_norms.Tree(nodes)
    assert ds.expected_output_text(tree, tree.nodes["A-1"]) == "Hello, World!\n42\n"
    assert ds.expected_output_text(tree, tree.nodes["A-2"]) == ""
    assert ds.expected_output_text(tree, tree.nodes["A-3"]) == "a  \n\nb\n"


def test_dsm2_the_expected_output_text_inside_a_list_item():
    item = "- intro:\n\n  "
    code = "```clean-language expect=valid\n  start:\n  \tprint(\"a\")\n  ```"
    out = "```clean-language-output\n  a\n  ```"
    nodes = section("SEC-1", [("ITM-1", "item", item)])
    item_node = nodes[1]
    start = item_node["start"] + len(item)
    item_node["end"] = start + len(code) + 4 + len(out)
    item_node["own_text"] = item + "\n\n  "
    for norm_id, own, at in (("A-1", code, start), ("A-2", out, start + len(code) + 4)):
        nodes.append(dict(item_node, id=norm_id, kind="code_block", parent="ITM-1", start=at, end=at + len(own), own_text=own))
    nodes[0]["end"] = item_node["end"]
    tree = derived_norms.Tree(nodes)
    block = ds.expected_output(tree, tree.nodes["A-1"])
    assert block["id"] == "A-2"
    assert ds.expected_output_text(tree, block) == "a\n"


def test_dsm2_a_misplaced_expected_output_block_is_not_read(repo):
    root, _ = repo
    tree = derived_norms.load_tree(root)
    facts = [ds.expected_output_citation(tree, n) for n in ds.semantic_fragments(tree)]
    assert not any(f and f.startswith("OUT-2@") for f in facts)


# ------------------------------------------------------------------ DSM-3


def test_dsm3_seal_writes_the_fixed_files(repo):
    root, _ = repo
    folder = root / ds.FOLDER_REL
    assert (folder / "lean-toolchain").read_text() == "leanprover/lean4:v4.34.1\n"
    for rel, text in ds.FIXED.items():
        assert (folder / rel).read_text() == text
    (folder / "Main.lean").write_text("changed\n")
    ds.seal(root, MODEL)
    assert (folder / "Main.lean").read_text() == ds.MAIN_LEAN


def test_dsm3_the_fixed_files_hold_nothing_of_clean():
    for text in (ds.FRAGMENT_LEAN, ds.MAIN_LEAN, ds.LAKEFILE):
        for word in ('"print"', "integer", "start:", "SEM0", "SYN0", "clean-language"):
            assert word not in text


def test_dsm3_the_layout(repo, monkeypatch):
    root, _ = repo
    FakeLean(monkeypatch)
    folder = root / ds.FOLDER_REL
    assert sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()) == sorted(ds.LAYOUT)
    (folder / "notes.md").write_text("x\n")
    (folder / "Clean" / "Extra.lean").write_text("x\n")
    (folder / ".lake").mkdir()
    found = names(run_check(root)[0])
    assert ("layout", str(folder / "notes.md")) in found
    assert ("layout", str(folder / "Clean" / "Extra.lean")) in found
    assert ("layout", str(folder / ".lake")) in found


def test_dsm3_clean_lean_imports_the_four_files(repo, monkeypatch):
    root, nodes = repo
    FakeLean(monkeypatch)
    code = lean_code(nodes)
    code["Clean.lean"] = code["Clean.lean"].replace("import Clean.Typing\n", "")
    reseal(root, nodes, code=code)
    assert ("layout", "Clean.lean", "does not import Clean.Typing") in run_check(root)[0]


def test_dsm3_a_fixed_file_changed_by_hand(repo, monkeypatch):
    root, _ = repo
    FakeLean(monkeypatch)
    (root / ds.FOLDER_REL / "Fragment.lean").write_text("changed\n")
    found = names(run_check(root)[0])
    assert ("fixed", "Fragment.lean") in found
    assert ("meta", "fragment_sha256") in found


# ------------------------------------------------------------------ DSM-4


def test_dsm4_the_meta_line(repo):
    root, _ = repo
    lines = (root / ds.STATUS_REL).read_text().split("\n")
    meta = json.loads(lines[0])
    assert list(meta) == ["type", "specs_commit", "generator", "model", "lakefile_sha256", "lean_toolchain_sha256",
                          "fragment_sha256", "main_sha256", "clean_sha256", "ast_sha256", "syntax_sha256",
                          "typing_sha256", "evaluation_sha256", "derived_norms_sha256", "status_sha256"]
    assert meta["specs_commit"] == SPECS and meta["model"] == MODEL
    assert meta["generator"] == {"plugin": "clean-derived-norms", "version": VERSION, "marketplace_commit": "none"}
    folder = root / ds.FOLDER_REL
    assert meta["typing_sha256"] == hashlib.sha256((folder / "Clean/Typing.lean").read_bytes()).hexdigest()
    assert meta["derived_norms_sha256"] == hashlib.sha256((root / ds.PATH_OF_LIST_OF_DERIVED_NORMS).read_bytes()).hexdigest()
    assert meta["status_sha256"] == hashlib.sha256("\n".join(lines[1:]).encode()).hexdigest()
    assert lines[0] == json.dumps(meta, separators=(",", ":"))


def test_dsm4_seal_without_model_exits_2_and_writes_nothing(repo, monkeypatch):
    root, _ = repo
    before = (root / ds.STATUS_REL).read_text()
    assert main_in(root, monkeypatch, "seal") == 2
    assert (root / ds.STATUS_REL).read_text() == before


def test_dsm4_seal_with_a_missing_lean_file_exits_2_and_writes_nothing(repo, monkeypatch):
    root, _ = repo
    (root / ds.FOLDER_REL / "Clean/Typing.lean").unlink()
    (root / ds.FOLDER_REL / "Main.lean").write_text("x\n")
    before = (root / ds.STATUS_REL).read_text()
    assert main_in(root, monkeypatch, "seal", "--model", MODEL) == 2
    assert (root / ds.STATUS_REL).read_text() == before
    assert (root / ds.FOLDER_REL / "Main.lean").read_text() == "x\n"


# ------------------------------------------------------------------ DSM-5


def test_dsm5_the_fields_of_a_status_line(repo):
    root, nodes = repo
    lines = [json.loads(l) for l in (root / ds.STATUS_REL).read_text().splitlines()[1:]]
    assert [list(l) for l in lines] == [ds.FRAGMENT_KEYS] * 5
    first = lines[0]
    assert first["cases"] == ["run"] and first["expected_output"].startswith("OUT-1@")
    assert first["parse_tree_hash"] and len(first["parse_tree_hash"]) == 8
    assert lines[2]["cases"] == ["error SEM001"] and lines[2]["expected_output"] is None
    assert lines[3]["cases"] == [] and lines[3]["parse_tree_hash"] is None
    assert lines[4]["parse_tree_hash"] is None


def test_dsm5_a_fixed_reason_opens_no_issue(repo, monkeypatch):
    root, nodes = repo
    FakeLean(monkeypatch)
    lines = good_status(root, nodes)
    lines[3]["issue"] = "https://github.com/Ivan-Pasco/clean-language-foundation/issues/3"
    reseal(root, nodes, lines=lines)
    assert ("issue", "TST-5") in names(run_check(root)[0])


def test_dsm5_a_stale_expected_output_or_parse_tree_hash(repo, monkeypatch):
    root, nodes = repo
    FakeLean(monkeypatch)
    lines = good_status(root, nodes)
    lines[0]["expected_output"] = None
    lines[1]["parse_tree_hash"] = "00000000"
    reseal(root, nodes, lines=lines)
    problems = run_check(root)[0]
    assert any(p[:2] == ("status", "TST-1") and "expected_output" in p[2] for p in problems)
    assert any(p[:2] == ("status", "TST-2") and "parse_tree_hash" in p[2] for p in problems)


def test_dsm5_a_line_of_a_syntax_error_fragment_is_refused(repo, monkeypatch):
    root, nodes = repo
    FakeLean(monkeypatch)
    lines = good_status(root, nodes)
    lines.insert(3, dict(lines[0], id="TST-4"))
    reseal(root, nodes, lines=lines)
    assert ("status", "TST-4") in names(run_check(root)[0])


# ------------------------------------------------------------------ DSM-6


@pytest.mark.parametrize("info,cases", [
    ("clean-language expect=valid", ["run"]),
    ("clean-language expect=error code=SEM001", ["error SEM001"]),
    ("clean-language", []),
    ("clean-language expect=error code=sem001", []),
    ("clean-language  expect=valid", []),
])
def test_dsm6_the_case_comes_from_the_opening_line(info, cases):
    node = section("SEC-1", [("A-1", "code_block", fence(info, "start:"))])[1]
    assert ds.case_kinds(node) == cases


def test_dsm6_no_comment_decides_the_case_or_the_output(repo):
    root, _ = repo
    tree = derived_norms.load_tree(root)
    fact = ds.facts(tree, ds.load_grammar(root), tree.nodes["TST-2"])
    assert fact["cases"] == ["run"] and fact["expected_output"] is None and fact["expected_output_text"] is None
    assert ds.judge("run", None, None, b"anything") is None


# ------------------------------------------------------------------ DSM-7


def test_dsm7_the_serialized_tree():
    tree = ("rule", "call", [("token", "PRINT", "print"), ("token", "LPAR", "("), ("token", "STRING", '"h\\i\n"'),
                             ("absent",), ("rule", "inner", [])])
    assert ds.serialize(tree) == 'rule call 5\ntoken PRINT print\ntoken LPAR (\ntoken STRING "h\\\\i\\n"\nabsent\nrule inner 0\n'
    assert ds.tree_hash(ds.serialize(tree)) == hashlib.sha256(ds.serialize(tree).encode()).hexdigest()[:8]


def test_dsm7_keywords_are_kept_and_layout_tokens_left_out(repo):
    root, _ = repo
    tree = derived_norms.load_tree(root)
    fact = ds.facts(tree, ds.load_grammar(root), tree.nodes["TST-1"])
    lines = fact["serialized"].split("\n")
    assert "token PRINT print" in lines and 'token STRING "a"' in lines and "token START start" in lines
    assert not any(l.startswith("token _") for l in lines)
    assert ds.hidden_terminal("_NL") and not ds.hidden_terminal("__ANON_0") and not ds.hidden_terminal("NAME")


def test_dsm7_a_fragment_that_the_grammar_does_not_parse(repo):
    root, _ = repo
    tree = derived_norms.load_tree(root)
    fact = ds.facts(tree, ds.load_grammar(root), tree.nodes["TST-6"])
    assert fact["parse_tree_hash"] is None and fact["parse_error"].startswith("line 2: ")


def test_dsm7_no_case_is_not_parsed(repo):
    root, _ = repo
    tree = derived_norms.load_tree(root)
    fact = ds.facts(tree, ds.load_grammar(root), tree.nodes["TST-5"])
    assert fact["parse_tree_hash"] is None and fact["parse_error"] is None


def test_dsm7_a_derived_fragment_that_does_not_parse_fails(repo, monkeypatch):
    root, nodes = repo
    FakeLean(monkeypatch)
    lines = good_status(root, nodes)
    lines[4] = dict(lines[4], state="derived", reason=None)
    reseal(root, nodes, lines=lines)
    assert ("parse", "TST-6") in names(run_check(root)[0])


def test_dsm7_the_tree_command(repo, monkeypatch, capsys):
    root, _ = repo
    assert main_in(root, monkeypatch, "tree", "TST-1", "TST-6") == 0
    out = capsys.readouterr().out.split("\n")
    assert out[0].startswith('== TST-1@') and 'cases=["run"] expected_output="OUT-1@' in out[0] and out[0].endswith(" specs/a.md")
    assert out[1] == "```clean-language expect=valid"
    assert "-- expected output --" in out and "-- parse tree --" in out and "-- parse error --" in out
    assert '      PRINT "print"' in out


def test_dsm7_the_tree_command_refuses_a_fragment_that_is_not_semantic(repo, monkeypatch, capsys):
    root, _ = repo
    assert main_in(root, monkeypatch, "tree", "TST-1", "TST-4") == 2
    assert capsys.readouterr().out == ""


def test_dsm7_the_script_holds_nothing_specific_to_clean():
    text = SCRIPT.read_text()
    code = text[text.index("# ---------------------------------------------------------------- fragments"):]
    for word in ('"print"', "integer", "SEM0", "SYN0", "start_section"):
        assert word not in code


# ------------------------------------------------------------------ DSM-8


def lean_problems(text, path="Clean/Typing.lean"):
    return ds.parse_lean(path, text)


def test_dsm8_a_declaration_and_its_citations():
    text = "namespace Clean\n\n-- TYP-12@4be10a7e: a type\n-- TYP-13@4be10a7f: another\ndef typeOf : Nat := 1\nend Clean\n"
    declarations, problems, _ = lean_problems(text)
    assert problems == []
    assert [(d.key, [c[1] for c in d.citations]) for d in declarations] == [("Clean/Typing.lean:Clean.typeOf", ["TYP-12", "TYP-13"])]


@pytest.mark.parametrize("text,problem", [
    ("def f : Nat := 1\n", ("citation", "Clean/Typing.lean:f")),
    ("-- TYP-12@4be10a7e: a type\n\ndef f : Nat := 1\n", ("citation", "Clean/Typing.lean:1")),
    ("-- a note\ndef f : Nat := 1\n", ("comment", "Clean/Typing.lean:1")),
    ("-- TYP-12@4be10a7e: x\ndef f : Nat := 1 -- why\n", ("comment", "Clean/Typing.lean:2")),
    ("/-- doc -/\n-- TYP-12@4be10a7e: x\ndef f : Nat := 1\n", ("comment", "Clean/Typing.lean:1")),
    ("-- TYP-12@4be10a7e: x\ndef f : Nat :=\n  -- inside\n  1\n", ("comment", "Clean/Typing.lean:3")),
    ("-- TYP-12@4be10a7e: x\nnamespace Clean\n", ("citation", "Clean/Typing.lean:1")),
    ("  def f : Nat := 1\n", ("declaration", "Clean/Typing.lean:1")),
    ("-- TYP-12@4be10a7e: x\ndef f : Nat := 1\nfoo bar\n", ("declaration", "Clean/Typing.lean:3")),
])
def test_dsm8_the_rules_of_citations(text, problem):
    _, problems, _ = lean_problems(text)
    assert problem in names(problems)


def test_dsm8_lines_that_continue_a_declaration():
    text = ("-- TYP-12@4be10a7e: x\ninductive T where\n| a\n| b\nderiving Repr\n\n"
            "-- TYP-12@4be10a7e: x\n@[simp] private partial def g : Nat → Nat\n| 0 => 1\n| n => n\ntermination_by n => n\n"
            "-- TYP-12@4be10a7e: x\ninstance : Inhabited T := ⟨T.a⟩\n"
            "-- TYP-12@4be10a7e: x\nderiving instance BEq for T\n")
    declarations, problems, _ = lean_problems(text)
    assert problems == []
    assert [d.key for d in declarations] == ["Clean/Typing.lean:T", "Clean/Typing.lean:g",
                                             "Clean/Typing.lean:instance : Inhabited T := ⟨T.a⟩",
                                             "Clean/Typing.lean:deriving instance BEq for T"]


def test_dsm8_strings_and_characters_are_not_comments():
    text = '-- TYP-12@4be10a7e: x\ndef f : String := "-- not a comment /- nor this"\n-- TYP-12@4be10a7e: x\ndef c : Char := \'-\'\n'
    _, problems, literals = lean_problems(text)
    assert problems == [] and literals == [(2, "-- not a comment /- nor this")]


def test_dsm8_each_norm_once_and_one_prose_norm(repo):
    root, nodes = repo
    tree = derived_norms.load_tree(root)
    twice = cite(nodes, "PRO-1") + "\n" + cite(nodes, "PRO-1") + "\ndef f : Nat := 1\n"
    only_fragment = cite(nodes, "TST-1") + "\n" + cite(nodes, "OUT-1") + "\ndef g : Nat := 1\n"
    found = []
    for text in (twice, only_fragment):
        declarations, _, _ = ds.parse_lean("Clean/Typing.lean", text)
        found += ds.check_declarations(tree, declarations, {"TST-1": {"state": "derived"}})
    assert any(p[1] == "Clean/Typing.lean:f" and "cited twice" in p[2] for p in found)
    assert ("citation", "Clean/Typing.lean:g", "cites no prose norm") in found


# ------------------------------------------------------------------ DSM-9


def test_dsm9_a_citation_that_does_not_check(repo):
    root, nodes = repo
    tree = derived_norms.load_tree(root)
    text = "\n".join(["-- PRO-999@4be10a7e: x", "def a : Nat := 1",
                      "-- PRO-1@00000000: x", "def b : Nat := 1",
                      cite(nodes, "PRO-1"), cite(nodes, "TST-6"), "def c : Nat := 1", ""])
    declarations, _, _ = ds.parse_lean("Clean/Typing.lean", text)
    messages = [p[2] for p in ds.check_declarations(tree, declarations, {"TST-6": {"state": "pending"}})]
    assert "line 1: PRO-999 is not a norm" in messages
    assert f"line 3: PRO-1 has the norm hash {tree.norm_hash('PRO-1')}" in messages
    assert "line 6: TST-6 is pending" in messages


def test_dsm9_a_reason_citation_that_does_not_check(repo, monkeypatch):
    root, nodes = repo
    FakeLean(monkeypatch)
    lines = good_status(root, nodes)
    lines[1] = dict(lines[1], state="pending", reason="no norm says it: PRO-1@11111111")
    reseal(root, nodes, lines=lines)
    assert ("reason-citation", "TST-2") in names(run_check(root)[0])


# ------------------------------------------------------------------ DSM-10


@pytest.mark.parametrize("line", ["  sorry", "  admit"])
def test_dsm10_no_sorry(line):
    _, problems, _ = lean_problems("-- TYP-12@4be10a7e: x\ntheorem t : 1 = 1 := by\n" + line + "\n")
    assert any(p[0] == "shortcut" for p in problems)


def test_dsm10_no_axiom_and_no_library():
    _, problems, _ = lean_problems("import Std.Data.HashMap\n-- TYP-12@4be10a7e: x\naxiom a : False\n")
    assert ("shortcut", "Clean/Typing.lean:1") in names(problems)
    assert ("shortcut", "Clean/Typing.lean:3") in names(problems)
    _, fine, _ = lean_problems("import Fragment\nimport Clean.Ast\n")
    assert fine == []


def test_dsm10_no_shortcut_by_a_literal(repo):
    root, nodes = repo
    tree = derived_norms.load_tree(root)
    literals = [("Clean/Evaluation.lean", 3, "TST-1"), ("Clean/Evaluation.lean", 4, "a\nb\n"), ("Clean/Evaluation.lean", 5, "a\n")]
    found = ds.check_literals(tree, literals, {"TST-1": "a\nb\n"})
    assert names(found) == [("shortcut", "Clean/Evaluation.lean:3"), ("shortcut", "Clean/Evaluation.lean:4")]


# ------------------------------------------------------------------ DSM-11


@pytest.mark.parametrize("case,expected,code,output,passes", [
    ("run", "42\n", None, b"42\n", True),
    ("run", "42\n", None, b"42", False),
    ("run", "42\n", "RUN001", b"42\n", False),
    ("run", None, None, b"anything", True),
    ("error SEM001", None, "SEM001", b"anything", True),
    ("error SEM001", None, "SEM004", b"", False),
    ("error SEM001", None, None, b"", False),
])
def test_dsm11_whether_a_case_passes(case, expected, code, output, passes):
    assert (ds.judge(case, expected, code, output) is None) is passes


def test_dsm11_a_run_that_fails_or_takes_too_long(tmp_path):
    slow = tmp_path / "slow"
    slow.write_text("#!/bin/sh\nexit 3\n")
    slow.chmod(0o755)
    assert ds.run_fragment(slow, "absent\n")[2].startswith("the executable exited with 3")
    good = tmp_path / "good"
    good.write_text("#!/bin/sh\ncat > /dev/null\nprintf 'SEM001\\nout'\n")
    good.chmod(0o755)
    assert ds.run_fragment(good, "absent\n") == ("SEM001", b"out", None)


# ------------------------------------------------------------------ DSM-12


def test_dsm12_no_status_file_lists_every_semantic_fragment_as_new(repo):
    root, _ = repo
    (root / ds.STATUS_REL).unlink()
    items = ds.worklist(root)
    assert [(i["kind"], i["id"]) for i in items] == [("new", i) for i in SEMANTIC]
    assert list(items[0]) == ["kind", "id", "old_hash", "new_hash", "cases", "expected_output", "parse_tree_hash", "parse_error", "file"]


def test_dsm12_nothing_changed_gives_an_empty_list(repo, monkeypatch, capsys):
    root, _ = repo
    assert main_in(root, monkeypatch, "worklist") == 0
    assert capsys.readouterr().out == ""


def test_dsm12_a_changed_expected_output(tmp_path, repo):
    root, nodes = repo
    parts = base_parts()
    parts[2] = ("OUT-1", "code_block", fence("clean-language-output", "a", "c"))
    write_tree(root, section("SEC-1", parts))
    assert [(i["kind"], i["id"]) for i in ds.worklist(root)] == [("changed", "TST-1")]
    parts[1] = "\nIt prints:\n"
    write_tree(root, section("SEC-1", parts))
    item = ds.worklist(root)[0]
    assert (item["kind"], item["id"], item["expected_output"]) == ("changed", "TST-1", None)


def test_dsm12_a_changed_parse_tree(repo):
    root, _ = repo
    (root / derived_norms.GRAMMAR_REL).write_text(GRAMMAR.replace('statement: "print"', 'statement: print_word') + 'print_word: "print"\n')
    kinds = {(i["kind"], i["id"]) for i in ds.worklist(root)}
    assert ("changed", "TST-1") in kinds and ("changed", "TST-2") in kinds
    assert ("changed", "TST-3") not in kinds


def test_dsm12_gone_and_norm_items(repo):
    root, nodes = repo
    changed = [dict(n, tree_hash="12345678" + "0" * 56) if n["id"] == "PRO-2" else n for n in nodes if n["id"] != "TST-2"]
    write_tree(root, changed)
    items = ds.worklist(root)
    gone = [i for i in items if i["kind"] == "gone"]
    assert [(i["id"], i["cases"], i["new_hash"], i["file"]) for i in gone] == [("TST-2", ["run"], None, None)]
    norm = [i for i in items if i["kind"] == "norm"]
    assert {i["declaration"] for i in norm} == {"Clean/Ast.lean:Clean.Statement", "Clean/Typing.lean:Clean.typing",
                                                "Clean/Evaluation.lean:Clean.evaluate"}
    assert all(i["new_hash"] == "12345678" and i["citation"].startswith("PRO-2@") for i in norm)
    assert list(norm[0]) == ["kind", "declaration", "old_hash", "new_hash", "citation"]


def test_dsm12_a_pending_fragment_whose_cited_norm_changed(repo):
    root, nodes = repo
    lines = good_status(root, nodes)
    lines[1] = dict(lines[1], state="pending", reason="no norm says it: " + cite(nodes, "PRO-2")[3:].split(":")[0])
    reseal(root, nodes, lines=lines)
    assert ds.worklist(root) == []
    write_tree(root, [dict(n, tree_hash="12345678" + "0" * 56) if n["id"] == "PRO-2" else n for n in nodes])
    assert ("changed", "TST-2") in {(i["kind"], i.get("id")) for i in ds.worklist(root)}


def test_dsm12_exit_status_2(tmp_path, monkeypatch):
    assert main_in(tmp_path, monkeypatch, "worklist") == 2


def set_version_in_status(root, version):
    """Write another version of the generator in the meta line of the status file, or none when version is None."""
    path = root / ds.STATUS_REL
    head, _, body = path.read_text().partition("\n")
    meta = json.loads(head)
    if version is None:
        meta["generator"].pop("version")
    else:
        meta["generator"]["version"] = version
    path.write_text(json.dumps(meta, separators=(",", ":")) + "\n" + body)


def declaration_keys(root):
    declarations, _, _ = ds.read_lean(root / ds.FOLDER_REL)
    return [d.key for d in declarations]


@pytest.mark.parametrize("old_version", ["0.0.9", None])
def test_dsm12_a_new_version_of_the_plugin_derives_every_fragment_and_declaration_again(repo, old_version):
    root, nodes = repo
    write_tree(root, [n for n in nodes if n["id"] != "TST-2"])
    set_version_in_status(root, old_version)
    items = ds.worklist(root)
    assert [(i["kind"], i["id"]) for i in items if "id" in i] == [("changed", i) for i in SEMANTIC if i != "TST-2"] + [("gone", "TST-2")]
    version = [i for i in items if i["kind"] == "version"]
    assert [i["declaration"] for i in version] == declaration_keys(root) and version
    assert version[0] == {"kind": "version", "declaration": declaration_keys(root)[0], "old_version": old_version, "new_version": VERSION}
    assert list(version[0]) == ["kind", "declaration", "old_version", "new_version"]
    assert items[-len(version):] == version


def test_dsm12_a_declaration_that_a_new_version_leaves_as_it_is_keeps_its_derived_norm_fingerprint(repo):
    root, _ = repo
    list_before = (root / ds.PATH_OF_LIST_OF_DERIVED_NORMS).read_text()
    set_version_in_status(root, "0.0.9")
    assert ds.worklist(root)
    ds.seal(root, MODEL)
    assert (root / ds.PATH_OF_LIST_OF_DERIVED_NORMS).read_text() == list_before
    assert ds.worklist(root) == []


def test_dsm12_worklist_exits_2_when_the_plugin_has_no_version(tmp_path, repo, monkeypatch, capsys):
    root, _ = repo
    other = tmp_path / "another-plugin"
    (other / ".claude-plugin").mkdir(parents=True)
    (other / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "clean-derived-norms"}))
    monkeypatch.setattr(ds, "PLUGIN_ROOT", other)
    assert main_in(root, monkeypatch, "worklist") == 2
    assert "no version" in capsys.readouterr().err


# ------------------------------------------------------------------ DSM-13


def test_dsm13_only_pending_fails_on_the_fixture(repo, monkeypatch, capsys):
    root, _ = repo
    lean = FakeLean(monkeypatch)
    assert main_in(root, monkeypatch, "check") == 1
    out = capsys.readouterr().out.split("\n")
    assert [l.split(":")[0] for l in out if l and not l.startswith("fragments:")] == ["pending", "pending"]
    assert out[-2] == "fragments: 3 derived, 2 pending; run passed 2/2; error passed 1/1; problems: 2"
    assert len(lean.runs) == 3


def test_dsm13_every_check_passes(repo, monkeypatch, capsys):
    root, nodes = repo
    FakeLean(monkeypatch)
    keep = [n for n in nodes if n["id"] not in ("TST-5", "TST-6")]
    write_tree(root, keep)
    reseal(root, keep, lines=[status_line(root, keep, i) for i in ("TST-1", "TST-2", "TST-3")])
    assert main_in(root, monkeypatch, "check") == 0
    assert capsys.readouterr().out == "fragments: 3 derived, 0 pending; run passed 2/2; error passed 1/1; problems: 0\n"


def test_dsm13_a_case_that_does_not_pass(repo, monkeypatch):
    root, nodes = repo
    tree = derived_norms.load_tree(root)
    serialized = ds.facts(tree, ds.load_grammar(root), tree.nodes["TST-1"])["serialized"]
    FakeLean(monkeypatch, outcomes={serialized: (None, b"a\n", None)})
    problems, summary = run_check(root)
    assert ("run", "TST-1") in names(problems) and summary["passed"]["run"] == [1, 2]


def test_dsm13_a_build_that_fails(repo, monkeypatch):
    root, _ = repo
    FakeLean(monkeypatch, build_error="lake build exited with 1: error: unknown identifier")
    problems, summary = run_check(root)
    assert ("build", str(root / ds.FOLDER_REL)) in names(problems)
    assert summary["passed"] == {"run": [0, 2], "error": [0, 1]}


def test_dsm13_the_fixed_reasons_are_required(repo, monkeypatch):
    root, nodes = repo
    FakeLean(monkeypatch)
    lines = good_status(root, nodes)
    lines[3] = dict(lines[3], state="derived", reason=None)
    lines[4] = dict(lines[4], reason="some other reason: PRO-1@" + cite(nodes, "PRO-1")[9:17])
    reseal(root, nodes, lines=lines)
    found = names(run_check(root)[0])
    assert ("opening line", "TST-5") in found and ("parse", "TST-6") in found


def test_dsm13_a_pending_gap_reason_must_cite_a_norm(repo, monkeypatch):
    root, nodes = repo
    FakeLean(monkeypatch)
    lines = good_status(root, nodes)
    lines[1] = dict(lines[1], state="pending", reason="no norm says it")
    reseal(root, nodes, lines=lines)
    assert any(p[:2] == ("pending", "TST-2") and "cites no norm" in p[2] for p in run_check(root)[0])


@pytest.mark.parametrize("missing", ["status", "lean", "tree"])
def test_dsm13_missing_inputs_exit_2(repo, monkeypatch, missing):
    root, _ = repo
    FakeLean(monkeypatch)
    path = {"status": root / ds.STATUS_REL, "lean": root / ds.FOLDER_REL / "Clean.lean", "tree": root / derived_norms.TREE_REL}[missing]
    path.unlink()
    assert main_in(root, monkeypatch, "check") == 2


@pytest.mark.parametrize("command", [["seal", "--model", MODEL], ["check"]])
def test_dsm4_dsm13_a_lean_file_that_is_not_utf8_exits_2_and_writes_nothing(repo, monkeypatch, capsys, command):
    root, _ = repo
    FakeLean(monkeypatch)
    typing_file = root / ds.FOLDER_REL / "Clean/Typing.lean"
    typing_file.write_bytes(typing_file.read_bytes() + b"-- \xff\n")
    before = (root / ds.STATUS_REL).read_bytes()
    assert main_in(root, monkeypatch, *command) == 2
    assert "is not UTF-8" in capsys.readouterr().err
    assert (root / ds.STATUS_REL).read_bytes() == before


def test_dsm13_lake_that_cannot_be_run_exits_2(repo, monkeypatch, capsys):
    root, _ = repo
    monkeypatch.setattr(ds.shutil, "which", lambda name: None)
    assert main_in(root, monkeypatch, "check") == 2
    assert "lake cannot be run" in capsys.readouterr().err


def test_dsm13_no_semantic_fragment_yet(repo, monkeypatch, capsys):
    root, nodes = repo
    monkeypatch.setattr(ds.shutil, "which", lambda name: None)
    keep = [n for n in nodes if not ds.is_semantic_fragment(n)]
    write_tree(root, keep)
    reseal(root, keep, lines=[])
    assert main_in(root, monkeypatch, "check") == 0
    assert capsys.readouterr().out == "fragments: 0 derived, 0 pending; run passed 0/0; error passed 0/0; problems: 0\n"


def test_dsm13_duplicate_issue_urls(repo, monkeypatch):
    root, nodes = repo
    FakeLean(monkeypatch)
    url = "https://github.com/Ivan-Pasco/clean-language-foundation/issues/12"
    lines = good_status(root, nodes)
    lines[0] = dict(lines[0], state="pending", reason="gap: " + cite(nodes, "PRO-1")[3:].split(":")[0], issue=url)
    lines[1] = dict(lines[1], state="pending", reason="gap: " + cite(nodes, "PRO-1")[3:].split(":")[0], issue=url)
    reseal(root, nodes, lines=lines)
    assert ("issue", "TST-2") in names(run_check(root)[0])


# ------------------------------------------------------------------ DSM-16


def test_dsm16_a_change_by_hand_after_seal_fails(repo, monkeypatch):
    root, _ = repo
    FakeLean(monkeypatch)
    path = root / ds.FOLDER_REL / "Clean/Typing.lean"
    path.write_text(path.read_text() + "\n")
    assert ("meta", "typing_sha256") in names(run_check(root)[0])


# ------------------------------------------------------------------ DSM-17


def test_dsm17_the_script_cites_no_norm(repo, monkeypatch, capsys):
    root, _ = repo
    found, bad = derived_norms.script_citations(SCRIPT.read_text())
    assert found == [] and bad == []
    assert main_in(root, monkeypatch, "stale-citations") == 0
    assert capsys.readouterr().out == ""


def test_dsm17_a_stale_citation_of_the_script_fails_check(repo, monkeypatch):
    root, nodes = repo
    FakeLean(monkeypatch)
    problems, _ = ds.check(root, [("script.py", "# PRO-1@11111111: a reason\n")])
    assert ("script-citation", "PRO-1") in names(problems)
    assert [p for p in problems if p[0] == "script-citation"][0][2].startswith("script.py line 1: ")


def test_dsm17_the_code_of_the_script_is_the_script_alone():
    assert [path for path, _ in CODE_OF_THE_SCRIPT] == ["use-cases/derive-semantics/derive_semantics.py"]


# ------------------------------------------------------------------ the docstrings


def test_every_function_cites_its_rule():
    import ast
    tree = ast.parse(SCRIPT.read_text())
    missing = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))
               and "Spec: DSM-" not in (ast.get_docstring(n) or "")]
    assert missing == []


# ------------------------------------------------------------------ Lean (skipped without lake)


needs_lake = pytest.mark.skipif(shutil.which("lake") is None, reason="lake is absent")


@needs_lake
def test_dsm11_dsm13_the_fixture_semantics_builds_and_runs(repo, monkeypatch, capsys):
    root, nodes = repo
    keep = [n for n in nodes if n["id"] not in ("TST-5", "TST-6")]
    write_tree(root, keep)
    reseal(root, keep, lines=[status_line(root, keep, i) for i in ("TST-1", "TST-2", "TST-3")])
    assert main_in(root, monkeypatch, "check") == 0, capsys.readouterr().out
    assert capsys.readouterr().out == "fragments: 3 derived, 0 pending; run passed 2/2; error passed 1/1; problems: 0\n"


@needs_lake
def test_dsm11_a_wrong_semantics_fails_its_cases(repo, monkeypatch):
    root, nodes = repo
    code = lean_code(nodes)
    code["Clean/Evaluation.lean"] = code["Clean/Evaluation.lean"].replace('text ++ "\\n" ++ after.output', 'text ++ after.output')
    reseal(root, nodes, code=code)
    problems, summary = run_check(root)
    assert ("run", "TST-1") in names(problems) and ("run", "TST-2") not in names(problems)
    assert summary["passed"] == {"run": [1, 2], "error": [1, 1]}


@needs_lake
def test_dsm11_a_semantics_that_does_not_build(repo):
    root, nodes = repo
    code = lean_code(nodes)
    code["Clean/Typing.lean"] = code["Clean/Typing.lean"].replace(":= none", ":= undefinedName")
    reseal(root, nodes, code=code)
    problems, _ = run_check(root)
    assert ("build", str(root / ds.FOLDER_REL)) in names(problems)


@needs_lake
def test_dsm7_the_reader_of_the_serialized_tree(tmp_path):
    executable_dir = tmp_path / "w"
    executable_dir.mkdir()
    folder = tmp_path / "semantics"
    for rel, text in ds.FIXED.items():
        (folder / rel).parent.mkdir(parents=True, exist_ok=True)
        (folder / rel).write_text(text)
    echo = "\n".join(["import Fragment", "namespace Clean", "partial def render : Fragment.Tree → String",
                      '  | .rule n cs => "(" ++ n ++ String.join (cs.map (" " ++ render ·)) ++ ")"',
                      '  | .token t x => t ++ "=" ++ x', '  | .absent => "_"',
                      "def outcome (t : Fragment.Tree) : Fragment.Outcome := { code := none, output := render t }",
                      "end Clean", ""])
    (folder / "Clean.lean").write_text(echo)
    for rel in ds.LEAN_CODE[1:]:
        (folder / rel).parent.mkdir(parents=True, exist_ok=True)
        (folder / rel).write_text("")
    executable, error = ds.build(folder, executable_dir, shutil.which("lake"))
    assert error is None
    tree = ("rule", "r", [("token", "T", 'a\\b\nc\r'), ("absent",), ("rule", "s", [])])
    assert ds.run_fragment(executable, ds.serialize(tree)) == (None, "(r T=a\\b\nc\r _ (s))".encode(), None)
    assert ds.run_fragment(executable, "rule r 2\nabsent\n")[2].startswith("the executable exited with 2")


# ------------------------------------------------------------------ DSM-7, DSM-10: programs of several files


def two_file_repo(root, first_path="// file: app/a.cln", second_path="// file: app/b.cln", second='\tprint("b")', output=None):
    """The fixture, with TST-7: a program of two files, derived; with output, followed by its expected output block OUT-7."""
    parts = base_parts() + [("TST-7", "code_block", fence(VALID, "// the files", first_path, "start:", '\tprint("a")',
                                                          "", second_path, "start:", second)), "\n"]
    if output is not None:
        parts += ["\n", ("OUT-7", "code_block", fence("clean-language-output", *output)), "\n"]
    nodes = section("SEC-1", parts)
    write_tree(root, nodes)
    reseal(root, nodes, lines=good_status(root, nodes) + [status_line(root, nodes, "TST-7")])
    tree = derived_norms.load_tree(root)
    return nodes, ds.facts(tree, ds.load_grammar(root), tree.nodes["TST-7"])


def test_dsm7_the_parse_tree_of_a_program_of_several_files(repo):
    root, _ = repo
    _, fact = two_file_repo(root)
    lines = fact["serialized"].split("\n")
    assert lines[:4] == ["rule %program 2", "rule %file 2", "token %path app/a.cln", "rule start 1"]
    assert "token %path app/b.cln" in lines and lines.count("rule %file 2") == 2
    assert not any("the files" in l for l in lines)
    assert fact["parse_tree_hash"] == ds.tree_hash(fact["serialized"]) and fact["parse_error"] is None


def test_dsm7_a_file_with_no_path_has_an_absent_path(repo):
    root, _ = repo
    _, fact = two_file_repo(root, second_path="// file:app/b.cln")
    lines = fact["serialized"].split("\n")
    second = [i for i, l in enumerate(lines) if l == "rule %file 2"][1]
    assert lines[second + 1] == "absent"


def test_dsm7_the_parse_tree_of_a_program_of_one_file_has_no_files(repo):
    root, _ = repo
    tree = derived_norms.load_tree(root)
    fact = ds.facts(tree, ds.load_grammar(root), tree.nodes["TST-1"])
    assert fact["serialized"].startswith("rule start ") and "%" not in fact["serialized"]


def test_dsm7_a_program_of_several_files_that_the_grammar_does_not_parse(repo):
    root, _ = repo
    _, fact = two_file_repo(root, second="\tprint(")
    assert fact["parse_tree_hash"] is None
    assert fact["parse_error"].startswith("line 8 (file 2, app/b.cln, line 3): ")


def test_dsm7_a_program_of_several_files_is_checked_as_any_fragment(repo, monkeypatch):
    root, _ = repo
    lean = FakeLean(monkeypatch)
    two_file_repo(root)
    problems, summary = run_check(root)
    assert [p for p in problems if p[0] != "pending"] == []
    assert summary["passed"]["run"] == [3, 3]
    assert any(s.startswith("rule %program 2\n") for s in lean.runs)


def test_dsm7_cex29_the_expected_output_of_a_program_of_several_files(repo, monkeypatch):
    root, _ = repo
    lean = FakeLean(monkeypatch)
    _, fact = two_file_repo(root, output=["a", "b"])
    assert fact["expected_output"] is not None and fact["expected_output"].startswith("OUT-7@")
    problems, summary = run_check(root)
    assert [p for p in problems if p[0] != "pending"] == [] and summary["passed"]["run"] == [3, 3]
    assert any(s == fact["serialized"] for s in lean.runs)
    FakeLean(monkeypatch, outcomes={fact["serialized"]: (None, b"a\n", None)})
    problems, summary = run_check(root)
    assert ("run", "TST-7") in names(problems) and summary["passed"]["run"] == [2, 3]


def test_dsm10_an_example_of_the_error_of_an_undeclared_name_is_checked_for_its_code(repo, monkeypatch):
    """The script never decides whether a name is declared: a derived SEM002 fragment is checked for its code alone."""
    root, _ = repo
    parts = base_parts() + [("TST-8", "code_block", fence("clean-language expect=error code=SEM002", "start:", '\tprint("lenght")')), "\n"]
    nodes = section("SEC-1", parts)
    write_tree(root, nodes)
    reseal(root, nodes, lines=good_status(root, nodes) + [status_line(root, nodes, "TST-8")])
    tree = derived_norms.load_tree(root)
    serialized = ds.facts(tree, ds.load_grammar(root), tree.nodes["TST-8"])["serialized"]
    FakeLean(monkeypatch, outcomes={serialized: ("SEM002", b"", None)})
    problems, summary = run_check(root)
    assert [p for p in problems if p[1] == "TST-8"] == [] and summary["passed"]["error"] == [2, 2]
    FakeLean(monkeypatch, outcomes={serialized: (None, b"lenght\n", None)})
    problems, summary = run_check(root)
    assert ("run", "TST-8") in names(problems) and summary["passed"]["error"] == [1, 2]


def test_dsm10_the_reason_of_an_example_that_is_not_a_whole_program_cites_a_norm(repo, monkeypatch):
    root, nodes = repo
    FakeLean(monkeypatch)
    lines = good_status(root, nodes)
    hash8 = lines[1]["hash"]
    lines[1] = dict(lines[1], state="pending",
                    reason=f"TST-2 is not a whole program (CEX-31): it uses the name score, which it does not declare and no norm defines: TST-2@{hash8}")
    reseal(root, nodes, lines=lines)
    found = [p for p in run_check(root)[0] if p[1] == "TST-2"]
    assert [p[0] for p in found] == ["pending"]


@needs_lake
def test_dsm7_the_reader_takes_the_tree_of_a_program_of_several_files(tmp_path):
    folder = tmp_path / "semantics"
    for rel, text in ds.FIXED.items():
        (folder / rel).parent.mkdir(parents=True, exist_ok=True)
        (folder / rel).write_text(text)
    echo = "\n".join(["import Fragment", "namespace Clean", "partial def render : Fragment.Tree → String",
                      '  | .rule n cs => "(" ++ n ++ String.join (cs.map (" " ++ render ·)) ++ ")"',
                      '  | .token t x => t ++ "=" ++ x', '  | .absent => "_"',
                      "def outcome (t : Fragment.Tree) : Fragment.Outcome := { code := none, output := render t }",
                      "end Clean", ""])
    (folder / "Clean.lean").write_text(echo)
    for rel in ds.LEAN_CODE[1:]:
        (folder / rel).parent.mkdir(parents=True, exist_ok=True)
        (folder / rel).write_text("")
    work = tmp_path / "w"
    work.mkdir()
    executable, error = ds.build(folder, work, shutil.which("lake"))
    assert error is None
    tree = ("rule", ds.PROGRAM_RULE, [("rule", ds.FILE_RULE, [("token", ds.PATH_TYPE, "app/a.cln"), ("rule", "s", [])]),
                                      ("rule", ds.FILE_RULE, [("absent",), ("rule", "s", [])])])
    assert ds.run_fragment(executable, ds.serialize(tree)) == (None, b"(%program (%file %path=app/a.cln (s)) (%file _ (s)))", None)


# ------------------------------------------------------------------ DSM-18


def list_rows(root):
    return [json.loads(line) for line in (root / ds.PATH_OF_LIST_OF_DERIVED_NORMS).read_text().splitlines()]


def by_name(root):
    return {r["name"]: r for r in list_rows(root)[1:]}


def test_dsm18_each_declaration_is_one_derived_norm(repo):
    root, nodes = repo
    rows = list_rows(root)
    assert rows[0] == {"kind": "meta", "type": "semantics", "last_derived_norm_number": len(rows) - 1}
    names_found = [r["name"] for r in rows[1:]]
    # In the order of NRM-13, by path, then by first_line: "." comes before "/".
    assert names_found == ["Clean.lean:Clean.outcome", "Clean/Ast.lean:Clean.Statement", "Clean/Evaluation.lean:Clean.evaluate",
                           "Clean/Syntax.lean:Clean.unquote", "Clean/Syntax.lean:Clean.statements",
                           "Clean/Typing.lean:Clean.typing"]
    assert [r["derived_norm_id"] for r in rows[1:]] == [f"semantics:{n}" for n in range(1, 7)]
    evaluate = by_name(root)["Clean/Evaluation.lean:Clean.evaluate"]
    lines = lean_code(nodes)["Clean/Evaluation.lean"].split("\n")
    assert evaluate["path"] == "specs-derived/semantics/Clean/Evaluation.lean"
    assert lines[evaluate["first_line"] - 1].startswith("-- PRO-1@")
    assert lines[evaluate["last_line"] - 1].startswith("  | Statement.stop")
    assert [c["norm_id"] for c in evaluate["cited_norms"]] == ["PRO-1", "PRO-2"]


def test_dsm18_the_lines_of_a_string_literal_inside_a_declaration_count():
    text = "\n".join(["-- PRO-1@11111111: a text", "def text : String := \"one", "two\"", "", "end Clean", ""])
    declarations, _, _ = ds.parse_lean("Clean/Ast.lean", text)
    assert [(d.derived_norm_first_line, d.derived_norm_last_line) for d in declarations] == [(1, 3)]


def test_dsm18_the_fixed_files_hold_no_derived_norm(repo):
    root, _ = repo
    assert not [r for r in list_rows(root)[1:] if r["path"].endswith(("Fragment.lean", "Main.lean"))]


def test_dsm18_the_same_declaration_keeps_its_derived_norm_id_and_a_moved_one_gets_a_new_one(repo):
    root, nodes = repo
    commit_the_list(root)
    before = by_name(root)
    code = lean_code(nodes)
    code["Clean/Typing.lean"] = code["Clean/Typing.lean"].replace(":= none", ":= Option.none")
    reseal(root, nodes, code)
    commit_the_list(root)
    after = by_name(root)
    typing = "Clean/Typing.lean:Clean.typing"
    assert after[typing]["derived_norm_id"] == before[typing]["derived_norm_id"]
    assert after[typing]["derived_norm_fingerprint"] != before[typing]["derived_norm_fingerprint"]
    code["Clean/Typing.lean"] = code["Clean/Typing.lean"].replace("def typing", "def typingOf").replace("typing program", "typingOf program")
    code["Clean.lean"] = code["Clean.lean"].replace("typing program", "typingOf program")
    reseal(root, nodes, code)
    after = by_name(root)
    assert typing not in after
    assert after["Clean/Typing.lean:Clean.typingOf"]["derived_norm_id"] == "semantics:7"
    assert list_rows(root)[0]["last_derived_norm_number"] == 7


def test_dsm18_cdn8_the_name_and_not_the_key_keeps_a_declaration_the_same(repo, monkeypatch):
    """DSM-18 and CDN-8: what keeps a declaration the same derived norm from one run to the next is its name.
    A key that changes only by a tab that CDN-10 replaces with a space gives the same name, so the declaration
    keeps its derived norm ID."""
    root, nodes = repo
    FakeLean(monkeypatch)
    code = lean_code(nodes)
    with_tab = code["Clean/Evaluation.lean"].replace(
        "\nend Clean", "\n" + cite(nodes, "PRO-1", "an outcome is shown as its output") +
        "\ninstance\t: ToString Fragment.Outcome where\n  toString outcome := outcome.output\n\nend Clean")
    code["Clean/Evaluation.lean"] = with_tab
    reseal(root, nodes, code)
    commit_the_list(root)
    name = "Clean/Evaluation.lean:instance : ToString Fragment.Outcome where"
    before = by_name(root)[name]["derived_norm_id"]
    code["Clean/Evaluation.lean"] = with_tab.replace("instance\t:", "instance :")
    reseal(root, nodes, code)
    assert "Clean/Evaluation.lean:instance : ToString Fragment.Outcome where" in declaration_keys(root)
    assert by_name(root)[name]["derived_norm_id"] == before
    assert [n for n in names(run_check(root)[0]) if n[0] == "derived-norms"] == []

def test_dsm18_a_list_that_does_not_check(repo, monkeypatch):
    root, _ = repo
    FakeLean(monkeypatch)
    rows = list_rows(root)
    rows[1]["derived_norm_fingerprint"] = "00000000"
    (root / ds.PATH_OF_LIST_OF_DERIVED_NORMS).write_text("".join(json.dumps(r) + "\n" for r in rows))
    path = root / ds.STATUS_REL
    head, _, body = path.read_text().partition("\n")
    meta = json.loads(head)
    meta["derived_norms_sha256"] = hashlib.sha256((root / ds.PATH_OF_LIST_OF_DERIVED_NORMS).read_bytes()).hexdigest()
    path.write_text(json.dumps(meta, separators=(",", ":")) + "\n" + body)
    problems = run_check(root)[0]
    assert [n for n in names(problems) if n[0] != "pending"] == [("derived-norms", rows[1]["derived_norm_id"])]
    assert main_in(root, monkeypatch, "check") == 1


def test_dsm16_a_change_by_hand_of_the_list_fails(repo, monkeypatch):
    root, _ = repo
    FakeLean(monkeypatch)
    path = root / ds.PATH_OF_LIST_OF_DERIVED_NORMS
    path.write_text(path.read_text() + "\n")
    assert ("meta", "derived_norms_sha256") in names(run_check(root)[0])


def test_dsm13_a_missing_list_exits_2(repo, monkeypatch):
    root, _ = repo
    FakeLean(monkeypatch)
    (root / ds.PATH_OF_LIST_OF_DERIVED_NORMS).unlink()
    assert main_in(root, monkeypatch, "check") == 2


def test_dsm13_no_semantic_fragment_yet_still_checks_the_list(repo, monkeypatch):
    root, nodes = repo
    monkeypatch.setattr(ds.shutil, "which", lambda name: None)
    keep = [n for n in nodes if not ds.is_semantic_fragment(n)]
    write_tree(root, keep)
    reseal(root, keep, lines=[])
    rows = list_rows(root)
    (root / ds.PATH_OF_LIST_OF_DERIVED_NORMS).write_text("".join(json.dumps(r) + "\n" for r in rows[:-1]))
    path = root / ds.STATUS_REL
    head, _, body = path.read_text().partition("\n")
    meta = dict(json.loads(head), derived_norms_sha256=hashlib.sha256((root / ds.PATH_OF_LIST_OF_DERIVED_NORMS).read_bytes()).hexdigest())
    path.write_text(json.dumps(meta, separators=(",", ":")) + "\n" + body)
    assert names(run_check(root)[0]) == [("derived-norms", rows[-1]["name"])]


def test_dsm15_the_script_has_no_command_that_compares_two_lists_of_derived_norms(repo, monkeypatch, capsys):
    root, _ = repo
    with pytest.raises(SystemExit) as error:
        main_in(root, monkeypatch, "derived-norm-changes")
    assert error.value.code == 2
    assert "invalid choice: 'derived-norm-changes'" in capsys.readouterr().err


# ------------------------------------------------------------------ CDN-10, the name of a derived norm


def test_cdn10_a_declaration_with_no_name_and_a_tab_is_named_with_a_space(repo, monkeypatch):
    root, nodes = repo
    FakeLean(monkeypatch)
    code = lean_code(nodes)
    code["Clean/Evaluation.lean"] = code["Clean/Evaluation.lean"].replace(
        "\nend Clean", "\n" + cite(nodes, "PRO-1", "an outcome is shown as its output") +
        "\ninstance\t: ToString Fragment.Outcome where\n  toString outcome := outcome.output\n\nend Clean")
    reseal(root, nodes, code)
    key = "Clean/Evaluation.lean:instance\t: ToString Fragment.Outcome where"
    assert key in declaration_keys(root)
    assert "Clean/Evaluation.lean:instance : ToString Fragment.Outcome where" in by_name(root)
    assert [n for n in names(run_check(root)[0]) if n[0] == "derived-norms"] == []
