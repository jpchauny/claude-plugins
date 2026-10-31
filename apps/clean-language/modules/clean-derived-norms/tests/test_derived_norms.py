"""Tests of scripts/derived_norms.py, the module script, and of how the scripts of the use cases use it.

Run from the root of the marketplace:
    uv run --with pytest --with "lark[interegular]" python3 -I -B -m pytest -q -p no:cacheprovider \
        apps/clean-language/modules/clean-derived-norms/tests
Spec: specs/module.md (CDN-7, CDN-8). The functions of the module script are
tested by the tests of the use case whose rule they implement; the list of
derived norms, which knows no type, is tested here (CDN-8, DGR-20, NRM-12 to
NRM-14).
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1]
MODULE_SCRIPT = MODULE / "scripts" / "derived_norms.py"
SCRIPTS_OF_THE_USE_CASES = sorted((MODULE / "use-cases").glob("*/*.py"))
sys.path.insert(0, str(MODULE / "scripts"))
import derived_norms  # noqa: E402

CITATION_RE = derived_norms.GRAMMAR_CITATION_RE
PATH_OF_LIST_OF_DERIVED_NORMS = "specs-derived/grammar/derived-norms.jsonl"
POWER = ["// EXP-11@e105eaa8: ^ is right-associative", "// EXP-8@a0b54578: the operators and their order",
         'power: unary ("^" power)?']


def imported_modules(path):
    """The names of the modules that a file imports."""
    names = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_cdn7_each_script_of_a_use_case_imports_the_module_script():
    assert [p.relative_to(MODULE).as_posix() for p in SCRIPTS_OF_THE_USE_CASES] == [
        "use-cases/derive-grammar/derive_grammar.py", "use-cases/derive-semantics/derive_semantics.py"]
    for path in SCRIPTS_OF_THE_USE_CASES:
        assert "derived_norms" in imported_modules(path), path


def test_cdn7_no_script_of_a_use_case_imports_the_script_of_another():
    stems = {p.stem for p in SCRIPTS_OF_THE_USE_CASES}
    for path in SCRIPTS_OF_THE_USE_CASES:
        text = path.read_text(encoding="utf-8")
        assert not (imported_modules(path) & (stems - {path.stem})), path
        assert "importlib" not in imported_modules(path), path
        for other in SCRIPTS_OF_THE_USE_CASES:
            if other != path:
                assert other.stem not in text, (path, other)


def test_cdn7_the_module_script_imports_no_script_of_a_use_case():
    assert not imported_modules(MODULE_SCRIPT) & {p.stem for p in SCRIPTS_OF_THE_USE_CASES}


def test_every_function_of_the_module_script_cites_its_rule():
    tree = ast.parse(MODULE_SCRIPT.read_text(encoding="utf-8"))
    missing = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))
               and not any(f"Spec: {prefix}-" in (ast.get_docstring(n) or "") for prefix in ("DGR", "DSM", "CDN"))]
    assert missing == []


# ------------------------------------------------------------------ the name of a derived norm (CDN-10)


@pytest.mark.parametrize("key, name", [
    ("power", "power"), ("%ignore COMMENT", "%ignore COMMENT"), ("%ignore\tWS", "%ignore WS"),
    ("Clean/Evaluation.lean:instance\t: ToString Value", "Clean/Evaluation.lean:instance : ToString Value"),
    ("%ignore\x0bA\x85B\u2028C\u2029D", "%ignore A B C D"), ("%ignore\t\tWS", "%ignore  WS"),
])
def test_cdn10_the_name_is_the_key_with_each_forbidden_character_replaced_by_a_space(key, name):
    assert derived_norms.name_of_derived_norm(key) == name
    assert derived_norms.derived_norm(["// EXP-8@a0b54578: x", key], key, "specs-derived/grammar/clean.lark", 1, 2, CITATION_RE).name == name


def test_cdn10_the_list_of_a_directive_with_a_tab_checks(tmp_path, monkeypatch):
    no_commit_yet(tmp_path, monkeypatch)
    lines = ["// EXP-1@0123abcd: blanks", "%ignore\tWS"]
    item = found(lines, "%ignore\tWS", 1, 2, G)
    text = derived_norms.seal_derived_norms(tmp_path, PATH_OF_LIST_OF_DERIVED_NORMS, "grammar", [item])
    assert json.loads(text.splitlines()[1])["name"] == "%ignore WS"
    (tmp_path / PATH_OF_LIST_OF_DERIVED_NORMS).parent.mkdir(parents=True)
    (tmp_path / PATH_OF_LIST_OF_DERIVED_NORMS).write_text(text)
    assert check(tmp_path, [item]) == []


# ------------------------------------------------------------------ the derived norm fingerprint (NRM-14)


def found(lines, name, first, last, path="specs-derived/grammar/clean.lark"):
    return derived_norms.derived_norm(lines, name, path, first, last, CITATION_RE)


def test_nrm14_the_binding_derived_norm_fingerprint_of_power():
    item = found(POWER, "power", 1, 3)
    assert item.cited_norms == [("EXP-11", "e105eaa8"), ("EXP-8", "a0b54578")]
    assert item.derived_norm_fingerprint == "0ced57c3"


def test_nrm14_the_derived_norm_fingerprint_is_the_sha256_of_the_text_to_hash():
    import hashlib
    text = 'EXP-11@e105eaa8\nEXP-8@a0b54578\n\npower: unary ("^" power)?\n'
    assert hashlib.sha256(text.encode()).hexdigest()[:8] == "0ced57c3"


@pytest.mark.parametrize("lines", [
    ["// EXP-8@a0b54578: another reason", "// EXP-11@e105eaa8: ^ binds to the right", 'power: unary ("^" power)?'],
    [l + " \t " for l in POWER],
    ["x: \"a\"", "", ""] + POWER,
])
def test_nrm14_reasons_order_trailing_blanks_and_place_do_not_change_it(lines):
    first = len(lines) - 2
    assert found(lines, "power", first, len(lines)).derived_norm_fingerprint == "0ced57c3"


def test_nrm14_crlf_is_read_as_lf():
    lines = derived_norms.output_file_lines("\r\n".join(POWER).encode())
    assert found(lines, "power", 1, 3).derived_norm_fingerprint == "0ced57c3"


@pytest.mark.parametrize("lines", [
    ["// EXP-11@e105eaa9: ^ is right-associative"] + POWER[1:],
    POWER[1:],
    POWER[:2] + ['power: unary ("^" unary)?'],
    ["// LEX-6@4b1bae1f: comments"] + POWER,
])
def test_nrm14_a_cited_norm_hash_a_cited_norm_or_the_content_changes_it(lines):
    assert found(lines, "power", 1, len(lines)).derived_norm_fingerprint != "0ced57c3"


# ------------------------------------------------------------------ the derived norm IDs (NRM-13, CDN-8)


def before(last, *pairs):
    return last, [{"kind": "derived_norm", "derived_norm_id": i, "name": n} for i, n in pairs]


def derived_norm_ids_and_names(entries):
    return [(e["derived_norm_id"], e["name"]) for e in entries]


def items(*names_and_lines):
    return [derived_norms.DerivedNorm(n, path, line, line, [("EXP-8", "a0b54578")], "0ced57c3") for n, path, line in names_and_lines]


G = "specs-derived/grammar/clean.lark"


def test_nrm13_a_derived_norm_keeps_its_derived_norm_id_whatever_its_content_norms_or_place():
    last, entries = derived_norms.give_derived_norm_ids("grammar", before(41, ("grammar:12", "power")),
                                             [derived_norms.DerivedNorm("power", G, 90, 95, [("EXP-11", "00000000")], "12345678")])
    assert derived_norm_ids_and_names(entries) == [("grammar:12", "power")] and last == 41
    assert entries[0]["derived_norm_fingerprint"] == "12345678" and entries[0]["first_line"] == 90


def test_nrm13_new_derived_norm_ids_follow_last_derived_norm_number_in_the_order_of_path_then_first_line():
    last, entries = derived_norms.give_derived_norm_ids("grammar", before(41, ("grammar:12", "power")),
                                             items(("index", G, 30), ("call", G, 20), ("power", G, 10), ("aaa", "z.lark", 1)))
    assert derived_norm_ids_and_names(entries) == [("grammar:12", "power"), ("grammar:42", "call"), ("grammar:43", "index"), ("grammar:44", "aaa")]
    assert last == 44


def test_nrm13_a_derived_norm_id_is_never_given_again():
    _, entries = derived_norms.give_derived_norm_ids("grammar", before(43, ("grammar:42", "call")), items(("call", G, 1)))
    assert derived_norm_ids_and_names(entries) == [("grammar:42", "call")]
    last, entries = derived_norms.give_derived_norm_ids("grammar", before(43), items(("other", G, 1)))
    assert derived_norm_ids_and_names(entries) == [("grammar:44", "other")] and last == 44


def test_nrm13_last_derived_norm_number_never_decreases_and_is_never_lower_than_a_derived_norm_id_of_a_list():
    assert derived_norms.give_derived_norm_ids("grammar", before(43), [])[0] == 43
    assert derived_norms.give_derived_norm_ids("grammar", before(2, ("grammar:9", "x")), items(("y", G, 1)))[1][0]["derived_norm_id"] == "grammar:10"


def test_nrm13_a_type_with_no_list_starts_from_0():
    last, entries = derived_norms.give_derived_norm_ids("grammar", None, items(("b", G, 2), ("a", G, 1)))
    assert derived_norm_ids_and_names(entries) == [("grammar:1", "a"), ("grammar:2", "b")] and last == 2




def test_cdn8_two_derived_norms_of_one_name_the_first_keeps_the_lowest_derived_norm_id():
    last, entries = derived_norms.give_derived_norm_ids("grammar", before(5, ("grammar:3", "x")), items(("x", G, 9), ("x", G, 2)))
    assert [(e["derived_norm_id"], e["first_line"]) for e in entries] == [("grammar:3", 2), ("grammar:6", 9)]


def test_cdn8_derived_norms_of_one_name_pair_in_order_with_the_derived_norm_ids_of_that_name():
    list_before_the_run = before(9, ("grammar:7", "x"), ("grammar:2", "x"), ("grammar:4", "x"))
    _, entries = derived_norms.give_derived_norm_ids("grammar", list_before_the_run, items(("x", G, 9), ("x", G, 2)))
    assert [(e["derived_norm_id"], e["first_line"]) for e in entries] == [("grammar:2", 2), ("grammar:4", 9)]
    last, entries = derived_norms.give_derived_norm_ids("grammar", before(9, ("grammar:2", "x")), items(("x", G, 1), ("x", G, 2), ("x", G, 3)))
    assert [(e["derived_norm_id"], e["first_line"]) for e in entries] == [("grammar:2", 1), ("grammar:10", 2), ("grammar:11", 3)] and last == 11


def test_cdn8_two_derived_norms_of_one_name_keep_their_derived_norm_ids_run_after_run():
    found = items(("%ignore WS", G, 1), ("%ignore WS", G, 4))
    list_before_the_run, runs = None, []
    for _ in range(3):
        last, entries = derived_norms.give_derived_norm_ids("grammar", list_before_the_run, found)
        runs.append((last, [(e["derived_norm_id"], e["first_line"]) for e in entries]))
        list_before_the_run = last, entries
    assert runs == [(2, [("grammar:1", 1), ("grammar:2", 4)])] * 3


# ------------------------------------------------------------------ the list of derived norms (NRM-12)


def test_nrm12_the_binding_example():
    item = derived_norms.DerivedNorm("power", G, 40, 42, [("EXP-11", "e105eaa8"), ("EXP-8", "a0b54578")], "0ced57c3")
    last, entries = derived_norms.give_derived_norm_ids("grammar", before(41, ("grammar:12", "power")), [item])
    assert derived_norms.text_of_list_of_derived_norms("grammar", last, entries) == (
        '{"kind": "header", "type": "grammar", "last_derived_norm_number": 41}\n'
        '{"kind": "derived_norm", "derived_norm_id": "grammar:12", "derived_norm_fingerprint": "0ced57c3", "name": "power", '
        '"path": "specs-derived/grammar/clean.lark", "first_line": 40, "last_line": 42, "cited_norms": '
        '[{"norm_id": "EXP-11", "norm_hash": "e105eaa8"}, {"norm_id": "EXP-8", "norm_hash": "a0b54578"}]}\n')


def test_nrm12_a_type_with_no_derived_norm_has_its_header_line_only():
    assert derived_norms.text_of_list_of_derived_norms("grammar", 0, []) == '{"kind": "header", "type": "grammar", "last_derived_norm_number": 0}\n'


@pytest.mark.parametrize("text", [
    "{bad\n",
    "",
    '{"kind": "header", "type": "semantics", "last_derived_norm_number": 0}\n',
    '{"kind": "header", "type": "grammar", "last_derived_norm_number": -1}\n',
    '{"kind": "header", "type": "grammar", "last_derived_norm_number": true}\n',
    '{"kind": "header", "type": "grammar", "last_derived_norm_number": 0}\n[1]\n',
    '{"kind": "header", "type": "grammar", "last_derived_norm_number": 0}\n\n',
    '{"kind": "header", "type": "grammar", "last_derived_norm_number": 0}\n   \n',
    '\n{"kind": "header", "type": "grammar", "last_derived_norm_number": 0}\n',
    '\n',
])
def test_dgr20_a_list_that_cannot_be_read(text):
    with pytest.raises(derived_norms.InputError):
        derived_norms.read_list_of_derived_norms(text.encode(), "grammar", "the list")


def test_dgr20_an_empty_line_cannot_be_read_and_the_error_names_it():
    with pytest.raises(derived_norms.InputError, match=r"^the list:2: not JSON$"):
        derived_norms.read_list_of_derived_norms(b'{"kind": "header", "type": "grammar", "last_derived_norm_number": 0}\n\n', "grammar", "the list")


@pytest.mark.parametrize("data", [
    b'{"kind": "header", "type": "grammar", "last_derived_norm_number": 3}\n',
    b'{"kind": "header", "type": "grammar", "last_derived_norm_number": 3}',
])
def test_dgr20_only_the_empty_text_after_the_last_line_feed_is_no_line(data):
    assert derived_norms.read_list_of_derived_norms(data, "grammar", "the list") == (3, [])


def test_nrm12_a_list_written_before_the_header_line_was_named_so_is_read():
    """NRM-12: the kind "meta" of an older header line is read as "header", so the list before the run keeps its IDs."""
    data = b'{"kind": "meta", "type": "grammar", "last_derived_norm_number": 3}\n'
    assert derived_norms.read_list_of_derived_norms(data, "grammar", "the list") == (3, [])
    with pytest.raises(derived_norms.InputError):
        derived_norms.read_list_of_derived_norms(data.replace(b'"meta"', b'"other"'), "grammar", "the list")


def test_dgr20_a_list_that_is_not_utf8_cannot_be_read_and_the_error_names_the_line():
    with pytest.raises(derived_norms.InputError, match=r"^the list:2: not UTF-8$"):
        derived_norms.read_list_of_derived_norms(b'{"kind": "header", "type": "grammar", "last_derived_norm_number": 0}\n\xff\n', "grammar", "the list")


# ------------------------------------------------------------------ the check of the list (DGR-20)


def write_list(root, last, entries):
    path = root / PATH_OF_LIST_OF_DERIVED_NORMS
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(derived_norms.text_of_list_of_derived_norms("grammar", last, entries))


def power_list(root, lines=None):
    """A list with power at lines 1 to 3 of the grammar, and the derived norms the grammar gives."""
    item = found(lines or POWER, "power", 1, 3, G)
    last, entries = derived_norms.give_derived_norm_ids("grammar", before(41, ("grammar:12", "power")), [item])
    write_list(root, last, entries)
    return [item], entries


def check(root, items_found):
    return [(p[1], p[2]) for p in derived_norms.check_list_of_derived_norms(root, PATH_OF_LIST_OF_DERIVED_NORMS, "grammar", items_found)]


def no_commit_yet(tmp_path, monkeypatch):
    """The temporary folder as a repository of layer 2 with no commit yet: no list before the run (CDN-9)."""
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))
    git(tmp_path, "init", "-q")


def test_dgr20_a_list_that_checks(tmp_path, monkeypatch):
    no_commit_yet(tmp_path, monkeypatch)
    items_found, _ = power_list(tmp_path)
    assert check(tmp_path, items_found) == []


def entry_change(root, change):
    path = root / PATH_OF_LIST_OF_DERIVED_NORMS
    lines = path.read_text().splitlines()
    header, entry = json.loads(lines[0]), json.loads(lines[1])
    change(header, entry)
    path.write_text(json.dumps(header) + "\n" + json.dumps(entry, ensure_ascii=False) + "\n")


@pytest.mark.parametrize("change,subject,words", [
    (lambda m, e: e.update(derived_norm_fingerprint="00000000"), "grammar:12", "NRM-14"),
    (lambda m, e: e.update(derived_norm_fingerprint="0CED57C3"), "grammar:12", "8 hex digits"),
    (lambda m, e: e.update(last_line=4), "grammar:12", "no derived norm of the output"),
    (lambda m, e: e.update(first_line=3, last_line=1), "grammar:12", "line numbers"),
    (lambda m, e: e.update(cited_norms=e["cited_norms"][:1]), "grammar:12", "citation lines cite"),
    (lambda m, e: e.update(cited_norms=[]), "grammar:12", "at least one"),
    (lambda m, e: e.update(cited_norms=e["cited_norms"][::-1]), "grammar:12", "order of the norm IDs"),
    (lambda m, e: e.update(name=" \t"), "grammar:12", "only blanks"),
    (lambda m, e: e.update(name="po\u2028wer"), "grammar:12", "separator"),
    (lambda m, e: e.update(derived_norm_id="grammar:42"), "derived-norms.jsonl:2", "greater than last_derived_norm_number"),
    (lambda m, e: e.update(derived_norm_id="grammar:012"), "derived-norms.jsonl:2", "not a derived norm ID"),
    (lambda m, e: e.update(derived_norm_id="semantics:12"), "derived-norms.jsonl:2", "not a derived norm ID"),
    (lambda m, e: e.pop("path"), "derived-norms.jsonl:2", "exactly the fields"),
    (lambda m, e: m.update(type="semantics"), "derived-norms.jsonl:1", "header line"),
    (lambda m, e: m.pop("kind"), "derived-norms.jsonl:1", "header line"),
])
def test_dgr20_a_list_that_does_not_check(tmp_path, monkeypatch, change, subject, words):
    no_commit_yet(tmp_path, monkeypatch)
    items_found, _ = power_list(tmp_path)
    entry_change(tmp_path, change)
    problems = check(tmp_path, items_found)
    assert any(s == subject and words in m for s, m in problems), problems


def test_dgr20_a_derived_norm_that_the_list_does_not_hold(tmp_path, monkeypatch):
    no_commit_yet(tmp_path, monkeypatch)
    items_found, _ = power_list(tmp_path)
    write_list(tmp_path, 41, [])
    assert check(tmp_path, items_found) == [("power", "a derived norm of specs-derived/grammar/clean.lark lines 1 to 3 that the list does not hold")]


def test_dgr20_bytes_and_lines_of_the_list(tmp_path, monkeypatch):
    no_commit_yet(tmp_path, monkeypatch)
    items_found, _ = power_list(tmp_path)
    path = tmp_path / PATH_OF_LIST_OF_DERIVED_NORMS
    good = path.read_bytes()
    for data, subject in [(b"\xef\xbb\xbf" + good, "derived-norms.jsonl"), (good.rstrip(b"\n"), "derived-norms.jsonl"),
                          (good + b"\n", "derived-norms.jsonl:3"), (good + b"{bad\n", "derived-norms.jsonl:3"),
                          (b"\xff\n", "derived-norms.jsonl")]:
        path.write_bytes(data)
        assert subject in [s for s, _ in check(tmp_path, items_found)], data


def test_dgr20_a_list_with_carriage_returns_does_not_check(tmp_path, monkeypatch):
    no_commit_yet(tmp_path, monkeypatch)
    items_found, _ = power_list(tmp_path)
    path = tmp_path / PATH_OF_LIST_OF_DERIVED_NORMS
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    problems = check(tmp_path, items_found)
    assert ("derived-norms.jsonl:1", "the line holds a carriage return") in problems
    assert ("derived-norms.jsonl:2", "the line holds a carriage return") in problems


@pytest.mark.parametrize("line,words", [(1, '"type"'), (2, '"kind"'), (2, '"norm_id"')])
def test_dgr20_a_line_that_gives_one_field_twice_does_not_check(tmp_path, monkeypatch, line, words):
    no_commit_yet(tmp_path, monkeypatch)
    items_found, _ = power_list(tmp_path)
    path = tmp_path / PATH_OF_LIST_OF_DERIVED_NORMS
    lines = path.read_text().split("\n")
    old = {'"type"': '"type": "grammar", ', '"kind"': '"kind": "derived_norm", ', '"norm_id"': '"norm_id": "EXP-11", '}[words]
    lines[line - 1] = lines[line - 1].replace(old, old + old, 1)
    path.write_text("\n".join(lines))
    problems = check(tmp_path, items_found)
    assert any(s == f"derived-norms.jsonl:{line}" and f"the field {words} is given twice" in m for s, m in problems), problems


def test_dgr20_order_twice_and_shared_lines(tmp_path, monkeypatch):
    no_commit_yet(tmp_path, monkeypatch)
    a = derived_norms.DerivedNorm("a", G, 1, 3, [("EXP-8", "a0b54578")], "11111111")
    b = derived_norms.DerivedNorm("b", G, 3, 4, [("EXP-8", "a0b54578")], "22222222")
    _, entries = derived_norms.give_derived_norm_ids("grammar", None, [a, b])
    write_list(tmp_path, 2, entries[::-1])
    problems = check(tmp_path, [a, b])
    assert ("grammar:1", "the lines are not in the ascending order of the numbers of their derived norm IDs") in problems
    assert any(s == "grammar:1" and "a line in common with grammar:2" in m for s, m in problems)
    write_list(tmp_path, 2, [entries[0], entries[0]])
    assert ("grammar:1", "the list holds this derived norm ID twice") in check(tmp_path, [a])


# ------------------------------------------------------------------ the list before the run (CDN-8, DGR-20)


def git(root, *args):
    """Run git in a temporary repository of a test, never in a real repository."""
    return subprocess.run(["git", "-C", str(root), "-c", "user.email=t@example.com", "-c", "user.name=t",
                           "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
                          check=True, capture_output=True, text=True).stdout


def branch(root):
    """The branch that HEAD names in a temporary repository of a test."""
    return git(root, "symbolic-ref", "--short", "HEAD").strip()


@pytest.fixture
def committed(tmp_path, monkeypatch):
    """A repository whose HEAD holds a list with power as grammar:12 and call as grammar:13, last 41."""
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q")
    p = derived_norms.DerivedNorm("power", G, 1, 3, [("EXP-8", "a0b54578")], "11111111")
    c = derived_norms.DerivedNorm("call", G, 5, 6, [("EXP-8", "a0b54578")], "22222222")
    write_list(root, 41, [dict(e, derived_norm_id=i) for e, i in zip(derived_norms.give_derived_norm_ids("grammar", None, [p, c])[1], ["grammar:12", "grammar:13"])])
    git(root, "add", "--", PATH_OF_LIST_OF_DERIVED_NORMS)
    git(root, "commit", "-q", "-m", "list")
    return root, p, c


def test_cdn8_seal_reads_the_list_before_the_run_at_head(committed):
    root, p, c = committed
    (root / PATH_OF_LIST_OF_DERIVED_NORMS).write_text(derived_norms.text_of_list_of_derived_norms("grammar", 0, []))
    text = derived_norms.seal_derived_norms(root, PATH_OF_LIST_OF_DERIVED_NORMS, "grammar", [p, c, derived_norms.DerivedNorm("new", G, 9, 9, p.cited_norms, "33333333")])
    assert [json.loads(l)["derived_norm_id"] for l in text.splitlines()[1:]] == ["grammar:12", "grammar:13", "grammar:42"]
    assert json.loads(text.splitlines()[0])["last_derived_norm_number"] == 42


@pytest.mark.parametrize("data", [b"{bad\n", b'{"kind": "header", "type": "grammar", "last_derived_norm_number": 41}\n\xff\n'])
def test_dgr20_seal_with_a_list_before_the_run_that_cannot_be_read(committed, data):
    root, p, _ = committed
    (root / PATH_OF_LIST_OF_DERIVED_NORMS).write_bytes(data)
    git(root, "add", "--", PATH_OF_LIST_OF_DERIVED_NORMS)
    git(root, "commit", "-q", "-m", "broken")
    with pytest.raises(derived_norms.InputError, match=f"^{branch(root)}:{PATH_OF_LIST_OF_DERIVED_NORMS}:"):
        derived_norms.seal_derived_norms(root, PATH_OF_LIST_OF_DERIVED_NORMS, "grammar", [p])


def test_cdn8_new_derived_norm_ids_follow_the_place_in_the_whole_output_across_the_seals_of_one_run(committed):
    root, p, c = committed
    late = derived_norms.DerivedNorm("late", "specs-derived/grammar/z.lark", 1, 1, p.cited_norms, "33333333")
    (root / PATH_OF_LIST_OF_DERIVED_NORMS).write_text(derived_norms.seal_derived_norms(root, PATH_OF_LIST_OF_DERIVED_NORMS, "grammar", [p, c, late]))
    assert derived_norm_ids_and_names(json.loads(l) for l in (root / PATH_OF_LIST_OF_DERIVED_NORMS).read_text().splitlines()[1:]) == [
        ("grammar:12", "power"), ("grammar:13", "call"), ("grammar:42", "late")]
    early = derived_norms.DerivedNorm("early", "specs-derived/grammar/a.lark", 1, 1, p.cited_norms, "44444444")
    text = derived_norms.seal_derived_norms(root, PATH_OF_LIST_OF_DERIVED_NORMS, "grammar", [p, c, late, early])
    assert derived_norm_ids_and_names(json.loads(l) for l in text.splitlines()[1:]) == [
        ("grammar:12", "power"), ("grammar:13", "call"), ("grammar:42", "early"), ("grammar:43", "late")]
    assert json.loads(text.splitlines()[0])["last_derived_norm_number"] == 43


def test_cdn8_seal_ignores_the_list_in_the_working_tree(committed):
    root, p, c = committed
    (root / PATH_OF_LIST_OF_DERIVED_NORMS).write_bytes(b"\xff{bad\n")
    text = derived_norms.seal_derived_norms(root, PATH_OF_LIST_OF_DERIVED_NORMS, "grammar", [p, c])
    assert derived_norm_ids_and_names(json.loads(l) for l in text.splitlines()[1:]) == [("grammar:12", "power"), ("grammar:13", "call")]


@pytest.mark.parametrize("entries,last,subject,words", [
    ([("grammar:12", "call", 5, 6)], 41, "grammar:12", "never moves to another derived norm"),
    ([("grammar:12", "power", 1, 3), ("grammar:30", "other", 5, 6)], 41, "grammar:30", "never given again"),
    ([("grammar:42", "power", 1, 3)], 42, "power", "keeps the k-th derived norm ID of that name"),
    ([("grammar:12", "power", 1, 3)], 40, "derived-norms.jsonl:1", "lower than 41"),
])
def test_dgr20_the_check_against_the_list_before_the_run(committed, entries, last, subject, words):
    root, p, c = committed
    by_name = {"power": p, "call": c, "other": derived_norms.DerivedNorm("other", G, 5, 6, p.cited_norms, "33333333")}
    found_now = []
    rows = []
    for derived_norm_id, name, first, last_line in entries:
        item = by_name[name]
        item = derived_norms.DerivedNorm(name, G, first, last_line, item.cited_norms, item.derived_norm_fingerprint)
        found_now.append(item)
        row = derived_norms.give_derived_norm_ids("grammar", None, [item])[1][0]
        rows.append(dict(row, derived_norm_id=derived_norm_id))
    write_list(root, last, rows)
    problems = check(root, found_now)
    assert any(s == subject and words in m for s, m in problems), problems


def test_dgr20_a_list_that_checks_against_the_list_before_the_run(committed):
    root, p, c = committed
    assert check(root, [p, c]) == []


@pytest.mark.parametrize("name", [["power"], {"power": 1}, 5, None])
def test_dgr20_a_name_that_is_not_a_string_is_reported_and_not_compared(committed, name):
    root, p, c = committed
    entry_change(root, lambda m, e: e.update(name=name))
    problems = check(root, [p, c])
    assert any(s == "grammar:12" and "is not a string" in m for s, m in problems), problems
    assert ("power", "a derived norm of specs-derived/grammar/clean.lark lines 1 to 3 that the list does not hold") in problems


def test_cdn9_a_list_before_the_run_that_is_not_utf8_stops_seal_and_check_reports_it(committed):
    root, p, c = committed
    good = (root / PATH_OF_LIST_OF_DERIVED_NORMS).read_bytes()
    (root / PATH_OF_LIST_OF_DERIVED_NORMS).write_bytes(good + b"\xff\n")
    git(root, "add", "--", PATH_OF_LIST_OF_DERIVED_NORMS)
    git(root, "commit", "-q", "-m", "broken")
    (root / PATH_OF_LIST_OF_DERIVED_NORMS).write_bytes(good)
    with pytest.raises(derived_norms.InputError, match=f"^{branch(root)}:{PATH_OF_LIST_OF_DERIVED_NORMS}:4: not UTF-8$"):
        derived_norms.seal_derived_norms(root, PATH_OF_LIST_OF_DERIVED_NORMS, "grammar", [p, c])
    assert (root / PATH_OF_LIST_OF_DERIVED_NORMS).read_bytes() == good
    problems = check(root, [p, c])
    assert [s for s, _ in problems] == ["derived-norms.jsonl"]
    assert problems[0][1].startswith(f"the list before the run cannot be read: {branch(root)}:{PATH_OF_LIST_OF_DERIVED_NORMS}:4: not UTF-8;")


def test_dgr15_the_module_script_compares_no_two_lists_of_derived_norms():
    assert not [name for name in dir(derived_norms) if "change" in name.lower()]


# ------------------------------------------------------------------ where the list before the run is read (CDN-9)


def list_with(root, *pairs, last=41):
    """Write a list of the grammar holding each (derived norm ID, name) at its own line."""
    rows = []
    for n, (derived_norm_id, name) in enumerate(pairs, 1):
        item = derived_norms.DerivedNorm(name, G, n, n, [("EXP-8", "a0b54578")], "11111111")
        rows.append(dict(derived_norms.give_derived_norm_ids("grammar", None, [item])[1][0], derived_norm_id=derived_norm_id))
    write_list(root, last, rows)


def test_cdn9_the_list_before_the_run_is_read_at_the_head_of_the_branch_of_origin_head(committed):
    root, p, c = committed
    default = branch(root)
    git(root, "symbolic-ref", "refs/remotes/origin/HEAD", f"refs/remotes/origin/{default}")
    git(root, "checkout", "-q", "-b", "work")
    list_with(root, ("grammar:50", "power"), last=60)
    git(root, "add", "--", PATH_OF_LIST_OF_DERIVED_NORMS)
    git(root, "commit", "-q", "-m", "on another branch")
    assert derived_norms.bytes_of_list_before_the_run(root, PATH_OF_LIST_OF_DERIVED_NORMS)[1] == f"{default}:{PATH_OF_LIST_OF_DERIVED_NORMS}"
    text = derived_norms.seal_derived_norms(root, PATH_OF_LIST_OF_DERIVED_NORMS, "grammar", [p])
    assert json.loads(text.splitlines()[1])["derived_norm_id"] == "grammar:12"
    assert json.loads(text.splitlines()[0])["last_derived_norm_number"] == 41


def test_cdn9_without_origin_head_the_branch_that_head_names(committed):
    root, p, _ = committed
    git(root, "checkout", "-q", "-b", "work")
    list_with(root, ("grammar:50", "power"), last=60)
    git(root, "add", "--", PATH_OF_LIST_OF_DERIVED_NORMS)
    git(root, "commit", "-q", "-m", "on the branch checked out")
    text = derived_norms.seal_derived_norms(root, PATH_OF_LIST_OF_DERIVED_NORMS, "grammar", [p])
    assert json.loads(text.splitlines()[1])["derived_norm_id"] == "grammar:50"


def test_cdn9_a_head_that_does_not_hold_the_list_has_no_list_before_the_run(tmp_path, monkeypatch):
    no_commit_yet(tmp_path, monkeypatch)
    (tmp_path / "README").write_text("x\n")
    git(tmp_path, "add", "--", "README")
    git(tmp_path, "commit", "-q", "-m", "first")
    assert derived_norms.read_list_before_the_run(tmp_path, PATH_OF_LIST_OF_DERIVED_NORMS, "grammar") is None
    item = derived_norms.DerivedNorm("power", G, 1, 3, [("EXP-8", "a0b54578")], "11111111")
    text = derived_norms.seal_derived_norms(tmp_path, PATH_OF_LIST_OF_DERIVED_NORMS, "grammar", [item])
    assert json.loads(text.splitlines()[1])["derived_norm_id"] == "grammar:1"


def test_cdn9_a_repository_with_no_commit_yet_has_no_list_before_the_run(tmp_path, monkeypatch):
    no_commit_yet(tmp_path, monkeypatch)
    assert derived_norms.read_list_before_the_run(tmp_path, PATH_OF_LIST_OF_DERIVED_NORMS, "grammar") is None


def assert_cannot_be_read(root, words):
    """seal stops with an InputError, and check reports the one problem of the list before the run."""
    item = derived_norms.DerivedNorm("power", G, 1, 3, [("EXP-8", "a0b54578")], "11111111")
    with pytest.raises(derived_norms.InputError, match=words):
        derived_norms.seal_derived_norms(root, PATH_OF_LIST_OF_DERIVED_NORMS, "grammar", [item])
    write_list(root, 1, derived_norms.give_derived_norm_ids("grammar", None, [item])[1])
    problems = check(root, [item])
    assert len(problems) == 1 and problems[0][0] == "derived-norms.jsonl", problems
    assert "the list before the run cannot be read" in problems[0][1] and "NRM-13" in problems[0][1]


def test_cdn9_a_folder_that_is_not_in_a_git_work_tree_cannot_be_read(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))
    assert_cannot_be_read(tmp_path, "is not in a git work tree")


def test_cdn9_git_that_cannot_run_cannot_be_read(tmp_path, monkeypatch):
    no_commit_yet(tmp_path, monkeypatch)
    monkeypatch.setattr(derived_norms, "git", lambda *args, **kwargs: None)
    assert_cannot_be_read(tmp_path, "git cannot run")


def test_cdn9_git_that_fails_to_give_the_bytes_of_the_list_cannot_be_read(committed):
    root, _, _ = committed
    blob = git(root, "rev-parse", f"HEAD:{PATH_OF_LIST_OF_DERIVED_NORMS}").strip()
    loose_object = root / ".git" / "objects" / blob[:2] / blob[2:]
    assert loose_object.is_file()
    loose_object.unlink()
    assert_cannot_be_read(root, "git cannot give the list before the run")


def test_cdn9_a_detached_head_without_origin_head_cannot_be_read(committed):
    root, _, _ = committed
    git(root, "checkout", "-q", "--detach")
    assert_cannot_be_read(root, "HEAD names no branch")


def test_cdn9_a_default_branch_with_no_commit_in_a_repository_with_commits_cannot_be_read(committed):
    root, _, _ = committed
    git(root, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
    assert_cannot_be_read(root, "the default branch trunk has no commit")
