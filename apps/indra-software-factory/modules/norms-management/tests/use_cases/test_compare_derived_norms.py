"""Tests of use-cases/build/compare_derived_norms.py and write_types_of_derived_norms.py.

The comparison of the lists of derived norms of the commit of layer 2 of the
run with those of the commit before the last step, as NRM-11 of
specs/module.md says, of lists in the form of NRM-12, for the decision of
ORC-10; and the record of the types of derived norms of NRM-16. Each test names the clause it checks. The fixtures are
temporary git repositories of layer 2 with a project.json. The tests of the
scripts of the use cases are in tests/use_cases/, out of the traceability of
the norms generator (docs/traceability.md), whose rules they do not check.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[2]
SCRIPT = PLUGIN / "use-cases" / "build" / "compare_derived_norms.py"
WRITER = PLUGIN / "use-cases" / "build" / "write_types_of_derived_norms.py"
sys.path.insert(0, str(SCRIPT.parent))

import compare_derived_norms  # noqa: E402

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
           GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")


def git(norms_repository: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(norms_repository), *args], check=True, capture_output=True, text=True, env=ENV).stdout.strip()


def derived_norm_list(derived_norm_type: str, last: int, derived_norm_fingerprints: dict[str, str]) -> str:
    lines = [{"kind": "meta", "type": derived_norm_type, "last_derived_norm_number": last}]
    for line_number, (derived_norm_id, derived_norm_fingerprint) in enumerate(derived_norm_fingerprints.items(), start=1):
        lines.append({"kind": "derived_norm", "derived_norm_id": derived_norm_id, "derived_norm_fingerprint": derived_norm_fingerprint,
                      "name": f"rule{line_number}", "path": f"specs-derived/{derived_norm_type}/out.txt",
                      "first_line": 2 * line_number - 1, "last_line": 2 * line_number,
                      "cited_norms": [{"norm_id": "EXP-11", "norm_hash": "e105eaa8"}]})
    return "".join(json.dumps(line) + "\n" for line in lines)


@pytest.fixture
def norms_repository(tmp_path: Path) -> Path:
    root = tmp_path / "project-norms"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    write(root, "project.json", json.dumps({"repositories": [], "derived_norms": [
        {"type": "grammar", "use_case": "/clean-derived-norms:derive-grammar"},
        {"type": "semantics", "use_case": "/clean-derived-norms:derive-semantics"},
    ]}))
    commit(root)
    return root


def write(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")


def commit(root: Path) -> str:
    git(root, "add", "-A")
    git(root, "commit", "-q", "--allow-empty", "-m", "c")
    return git(root, "rev-parse", "HEAD")


def comparison(root: Path, commit_name: str) -> dict:
    """The comparison of NRM-11 as the script computes it, in this process, for the values that its output does not
    show: the commit before the last step, the types of each commit."""
    root = root.resolve()
    return compare_derived_norms.compare(root, compare_derived_norms.resolve_commit(root, commit_name))


def no_comparison(commit_name: str, reason: str) -> str:
    """NRM-11, rule 7, outcome 2."""
    return (f"norms-management: the derived norms of {commit_name} of the norms repository cannot be compared (NRM-11): "
            f"{reason}; the run stops after layer 2 (ORC-10)\n")


def run(root: Path, commit: str, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", str(SCRIPT), "--norms-repository", str(root), "--commit", commit, *extra],
                          capture_output=True, text=True, env=ENV)


TREE_PATH = "data/tree.jsonl"
NORM_HASHES_IN_TREE = {"EXP-11": "e105eaa8", "EXP-8": "a0b54578"}


def write_tree(root: Path, norm_hashes: dict[str, str]) -> None:
    """data/tree.jsonl in the form of R61, with one line of type node per norm ID, whose tree_hash starts with its
    norm hash."""
    lines = [{"generator_version": "0.1.0", "retired_prefixes": [], "specs_commit": "0" * 40, "type": "meta"}]
    for norm_id, norm_hash in norm_hashes.items():
        lines.append({"id": norm_id, "own_text": "x\u2028y", "status": "active", "tree_hash": norm_hash + "0" * 56,
                      "type": "node"})
    write(root, TREE_PATH, "".join(json.dumps(line, sort_keys=True, ensure_ascii=False) + "\n" for line in lines))


def grammar_path() -> str:
    return "specs-derived/grammar/derived-norms.jsonl"


def semantics_path() -> str:
    return "specs-derived/semantics/derived-norms.jsonl"


@pytest.fixture
def both(norms_repository: Path) -> Path:
    """A repository whose two types have valid lists at every commit from the next one on, and whose data/tree.jsonl
    holds the norms that the lists cite, with the norm hashes they cite."""
    write_tree(norms_repository, NORM_HASHES_IN_TREE)
    write(norms_repository, grammar_path(), derived_norm_list("grammar", 0, {}))
    write(norms_repository, semantics_path(), derived_norm_list("semantics", 0, {}))
    commit(norms_repository)
    return norms_repository


def test_new_changed_gone_by_derived_norm_id_in_number_order(both: Path) -> None:
    """NRM-11: new, changed and gone by derived norm ID, in the order of their numbers."""
    write(both, grammar_path(), derived_norm_list("grammar", 10, {
        "grammar:1": "11111111", "grammar:2": "22222222", "grammar:3": "33333333", "grammar:10": "aaaaaaaa"}))
    commit(both)
    write(both, grammar_path(), derived_norm_list("grammar", 12, {
        "grammar:1": "11111111", "grammar:2": "2222ffff", "grammar:10": "aaaabbbb", "grammar:11": "bbbbbbbb", "grammar:12": "cccccccc"}))
    after = commit(both)
    result = run(both, after)
    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        "grammar: 2 new, 2 changed, 1 gone\n"
        "  new: grammar:11, grammar:12\n"
        "  changed: grammar:2, grammar:10\n"
        "  gone: grammar:3\n"
        "semantics: no change\n"
        "derived norms changed: yes\n"
    )


def test_the_head_from_before_a_step_without_commit_is_compared_with_its_first_parent(both: Path) -> None:
    """NRM-11 rule 1, ORC-10: when the step makes no commit, the head from before the step, a commit of a step, is
    compared with its first parent, so a derived norm that an earlier step changed still reaches layers 3 and 4."""
    write(both, grammar_path(), derived_norm_list("grammar", 12, {"grammar:12": "11111111"}))
    commit(both)
    write(both, grammar_path(), derived_norm_list("grammar", 12, {"grammar:12": "22222222"}))
    head = commit(both)
    result = run(both, "HEAD")
    assert result.stdout == "grammar: 0 new, 1 changed, 0 gone\n  changed: grammar:12\nsemantics: no change\nderived norms changed: yes\n"
    data = comparison(both, head)
    assert data["last_commit_of_a_step"] == head
    assert data["commit_before_the_last_step"] == git(both, "rev-parse", "HEAD^1")


def test_a_merge_commit_of_a_pull_is_compared_with_the_commit_before_the_last_step(both: Path) -> None:
    """NRM-11 rule 1, NRM-10, ORC-10: after a rejected push, the pull makes a merge commit whose first parent is the
    commit of the step. The commit of the step is compared with its first parent; and when a later step makes no
    commit, the merge commit, the head from before it, is compared with the commit before the last step, never with
    its own first parent, so the derived norms that the earlier step changed are not hidden."""
    base = git(both, "rev-parse", "HEAD")
    write(both, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "11111111"}))
    step = commit(both)
    git(both, "checkout", "-q", "-b", "remote", base)
    write(both, "other.txt", "another session\n")
    commit(both)
    git(both, "checkout", "-q", "main")
    git(both, "merge", "-q", "--no-ff", "--no-edit", "remote")
    merge = git(both, "rev-parse", "HEAD")
    assert git(both, "rev-parse", "HEAD^1") == step
    assert run(both, step).stdout.splitlines()[:2] == ["grammar: 1 new, 0 changed, 0 gone", "  new: grammar:1"]
    assert run(both, merge).stdout.splitlines()[:2] == ["grammar: 1 new, 0 changed, 0 gone", "  new: grammar:1"]
    data = comparison(both, merge)
    assert data["commit_of_layer_2_of_the_run"] == merge and data["last_commit_of_a_step"] == step
    assert data["commit_before_the_last_step"] == base


def test_a_list_absent_at_the_commit_before_the_last_step_counts_as_empty(both: Path) -> None:
    """NRM-11 rule 4: at the commit before the last step, a list that does not exist counts as a list with no derived norm."""
    (both / grammar_path()).unlink()
    commit(both)
    write(both, grammar_path(), derived_norm_list("grammar", 2, {"grammar:1": "11111111", "grammar:2": "22222222"}))
    result = run(both, commit(both))
    assert result.stdout.splitlines()[:2] == ["grammar: 2 new, 0 changed, 0 gone", "  new: grammar:1, grammar:2"]
    assert result.stdout.endswith("derived norms changed: yes\n")


def test_a_list_at_the_commit_before_the_last_step_that_does_not_meet_nrm_12_counts_as_empty(both: Path) -> None:
    """NRM-11 rule 4: at the commit before the last step, a list that does not meet NRM-12 counts as a list with no derived norm."""
    write(both, grammar_path(), "not json\n")
    commit(both)
    write(both, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "11111111"}))
    result = run(both, commit(both))
    assert result.stdout.splitlines()[:2] == ["grammar: 1 new, 0 changed, 0 gone", "  new: grammar:1"]


def test_every_list_counts_as_empty_when_the_commit_has_no_parent(tmp_path: Path) -> None:
    """NRM-11: every list counts as a list with no derived norm when the commit has no parent."""
    root = tmp_path / "first"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    write(root, "project.json", json.dumps({"derived_norms": [{"type": "grammar", "use_case": "/x:y"}]}))
    write_tree(root, NORM_HASHES_IN_TREE)
    write(root, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "11111111"}))
    data = comparison(root, commit(root))
    assert data["commit_before_the_last_step"] is None
    assert data["comparisons_of_types_of_derived_norms"] == [{"type": "grammar", "named_by_derived_norms": True, "new": ["grammar:1"], "changed": [],
                              "gone": [], "error": None}]
    assert data["derived_norms_changed"] is True and data["derived_norms_readable"] is True


def test_gone_a_derived_norm_id_that_the_list_before_held(both: Path) -> None:
    """NRM-11 rule 3: gone, a derived norm ID that the list before held and the other does not."""
    write(both, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "11111111"}))
    commit(both)
    write(both, grammar_path(), derived_norm_list("grammar", 1, {}))
    assert "  gone: grammar:1\n" in run(both, commit(both)).stdout


def test_same_derived_norm_fingerprints_are_no_change_whatever_else_changed(both: Path) -> None:
    """NRM-11, ORC-10: only the derived norm fingerprint makes a derived norm changed."""
    write(both, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "11111111"}))
    commit(both)
    moved = derived_norm_list("grammar", 1, {"grammar:1": "11111111"}).replace('"first_line": 1', '"first_line": 2')
    write(both, grammar_path(), moved.replace('"last_derived_norm_number": 1', '"last_derived_norm_number": 5'))
    result = run(both, commit(both))
    assert result.stdout == "grammar: no change\nsemantics: no change\nderived norms changed: no\n"


def test_a_list_absent_at_the_commit_cannot_be_read(both: Path) -> None:
    """NRM-11, ORC-10: at the commit of layer 2 of the run, a list that does not exist cannot be read: the run stops."""
    (both / semantics_path()).unlink()
    after = commit(both)
    result = run(both, after)
    assert result.returncode == 0
    assert result.stdout == (f"grammar: no change\nsemantics: cannot be read: {semantics_path()} at {after}: it does not exist\n"
                             "derived norms cannot be read\n")
    data = comparison(both, after)
    assert data["derived_norms_readable"] is False and data["derived_norms_changed"] is False


def valid_line(**fields) -> str:
    line = {"kind": "derived_norm", "derived_norm_id": "grammar:1", "derived_norm_fingerprint": "11111111", "name": "power",
            "path": "specs-derived/grammar/clean.lark", "first_line": 1, "last_line": 2,
            "cited_norms": [{"norm_id": "EXP-11", "norm_hash": "e105eaa8"}]}
    line.update(fields)
    return json.dumps(line) + "\n"


META = '{"kind": "meta", "type": "grammar", "last_derived_norm_number": 3}\n'


@pytest.mark.parametrize("text, reason", [
    ("", "no meta line"),
    ("not json\n", "line 1: not a JSON object"),
    ("﻿" + META, "a byte order mark"),
    (META.rstrip("\n"), "its last line is not followed by a line feed"),
    (META.replace("\n", "\r\n"), "a carriage return"),
    (META + "\n", "line 2: not a JSON object"),
    ('{"kind": "derived_norm"}\n', "line 1: not the fields kind, type, last_derived_norm_number, in this order"),
    ('{"type": "grammar", "kind": "meta", "last_derived_norm_number": 3}\n', "line 1: not the fields kind, type, last_derived_norm_number, in this order"),
    (META.replace('"meta"', '"other"'), "line 1: not the meta line"),
    (META.replace('"grammar"', '"semantics"'), "line 1: its type is not grammar"),
    (META.replace("3}", "-1}"), "line 1: last_derived_norm_number is not an integer, 0 or greater"),
    (META + '{"kind": "derived_norm", "derived_norm_id": "grammar:1"}\n', "line 2: not the fields kind"),
    (META + valid_line(kind="meta"), "line 2: kind is not derived_norm"),
    (META + valid_line(derived_norm_id="semantics:1"), "line 2: derived_norm_id is not a derived norm ID of grammar (NRM-13)"),
    (META + valid_line(derived_norm_id="grammar:01"), "line 2: derived_norm_id is not a derived norm ID of grammar (NRM-13)"),
    (META + valid_line() + valid_line(first_line=3, last_line=3), "line 3: grammar:1 is not after the derived norm ID before it"),
    (META + valid_line(derived_norm_id="grammar:4"), "line 2: grammar:4 is after last_derived_norm_number"),
    (META + valid_line(derived_norm_fingerprint="ABCDEF12"), "line 2: derived_norm_fingerprint is not 8 lower-case hex digits (NRM-14)"),
    (META + valid_line(name=" \t"), "line 2: name is not a name of NRM-12"),
    (META + valid_line(name="a b"), "line 2: name is not a name of NRM-12"),
    (META + valid_line(path="specs-derived/grammar/derived-norms.jsonl"), "line 2: path is not a file of the output of grammar"),
    (META + valid_line(path="specs-derived/grammar/../x"), "line 2: path is not a file of the output of grammar"),
    (META + valid_line(path="specs-derived/other/x"), "line 2: path is not a file of the output of grammar"),
    (META + valid_line(first_line=3, last_line=2), "line 2: first_line and last_line are not line numbers, the first not after the last"),
    (META + valid_line(first_line=True), "line 2: first_line and last_line are not line numbers, the first not after the last"),
    (META + valid_line(cited_norms=[]), "line 2: cited_norms is not a list of at least one norm"),
    (META + valid_line(cited_norms={}), "line 2: cited_norms is not a list of at least one norm"),
    (META + valid_line(cited_norms={"norm_id": "EXP-11", "norm_hash": "e105eaa8"}),
     "line 2: cited_norms is not a list of at least one norm"),
    (META + valid_line(cited_norms=[{"norm_id": "EX-1", "norm_hash": "e105eaa8"}]), "line 2: a cited norm is not a norm ID and its norm hash"),
    (META + valid_line(cited_norms=[{"norm_hash": "e105eaa8", "norm_id": "EXP-1"}]), "line 2: not the fields norm_id, norm_hash, in this order"),
    (META + valid_line(cited_norms=[{"norm_id": "EXP-8", "norm_hash": "a0b54578"}, {"norm_id": "EXP-11", "norm_hash": "e105eaa8"}]),
     "line 2: cited_norms is not in the order of the norm IDs, each once"),
    (META + valid_line() + valid_line(derived_norm_id="grammar:2", first_line=2, last_line=4),
     "lines 2 and 3: two derived norms share a line"),
    (META + valid_line(first_line=5, last_line=6) + valid_line(derived_norm_id="grammar:2", first_line=1, last_line=5),
     "lines 2 and 3: two derived norms share a line"),
])
def test_a_list_at_the_commit_that_does_not_meet_nrm_12_cannot_be_read(both: Path, text: str, reason: str) -> None:
    """NRM-11, NRM-12, ORC-10: the type, the path and the first thing of NRM-12 it does not meet are named, and the
    run stops."""
    write(both, grammar_path(), text)
    after = commit(both)
    result = run(both, after)
    assert result.returncode == 0, result.stderr
    first = result.stdout.splitlines()[0]
    assert first.startswith(f"grammar: cannot be read: {grammar_path()} at {after}: {reason}")
    assert result.stdout.endswith("derived norms cannot be read\n")


def test_a_list_at_the_commit_that_is_not_utf_8_cannot_be_read(both: Path) -> None:
    """NRM-11, NRM-12: a list whose bytes are not UTF-8 cannot be read at the commit of layer 2 of the run."""
    line = valid_line(name="caf\u00e9").replace("\\u00e9", "\u00e9")
    (both / grammar_path()).write_bytes(META.encode("utf-8") + line.encode("latin-1"))
    after = commit(both)
    result = run(both, after)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0] == f"grammar: cannot be read: {grammar_path()} at {after}: not UTF-8"
    assert result.stdout.endswith("derived norms cannot be read\n")


@pytest.mark.parametrize("field", ["name", "path"])
def test_a_list_at_the_commit_with_a_lone_surrogate_cannot_be_read(both: Path, field: str) -> None:
    """NRM-11, NRM-12: a name or a path that a JSON escape writes as a lone surrogate is no UTF-8 string: the list
    cannot be read at the commit of layer 2 of the run."""
    value = "power\ud800" if field == "name" else "specs-derived/grammar/clean\ud800.lark"
    line = valid_line(**{field: value})
    assert "\\ud800" in line
    write(both, grammar_path(), META + line)
    after = commit(both)
    result = run(both, after)
    reason = "name is not a name of NRM-12" if field == "name" else "path is not a file of the output of grammar"
    assert result.stdout.splitlines()[0] == f"grammar: cannot be read: {grammar_path()} at {after}: line 2: {reason}"
    assert result.stdout.endswith("derived norms cannot be read\n")


def test_the_binding_example_of_nrm_12_can_be_read(both: Path) -> None:
    """NRM-12: the list of its binding example meets it."""
    write(both, grammar_path(),
          '{"kind": "meta", "type": "grammar", "last_derived_norm_number": 41}\n'
          '{"kind": "derived_norm", "derived_norm_id": "grammar:12", "derived_norm_fingerprint": "0ced57c3", "name": "power", '
          '"path": "specs-derived/grammar/clean.lark", "first_line": 40, "last_line": 42, "cited_norms": '
          '[{"norm_id": "EXP-11", "norm_hash": "e105eaa8"}, {"norm_id": "EXP-8", "norm_hash": "a0b54578"}]}\n')
    result = run(both, commit(both))
    assert result.stdout.splitlines()[:2] == ["grammar: 1 new, 0 changed, 0 gone", "  new: grammar:12"]


def test_the_binding_example_of_a_derived_norm_behind_its_norms(both: Path) -> None:
    """NRM-11 rules 5 and 7, ORC-10: the derived norm grammar:12 of NRM-12 cites EXP-11@e105eaa8 while the norm hash of
    EXP-11 in data/tree.jsonl of the same commit is 5a627175: the list cannot be read and the run stops."""
    write_tree(both, {"EXP-11": "5a627175", "EXP-8": "a0b54578"})
    write(both, grammar_path(),
          '{"kind": "meta", "type": "grammar", "last_derived_norm_number": 41}\n'
          '{"kind": "derived_norm", "derived_norm_id": "grammar:12", "derived_norm_fingerprint": "0ced57c3", "name": "power", '
          '"path": "specs-derived/grammar/clean.lark", "first_line": 40, "last_line": 42, "cited_norms": '
          '[{"norm_id": "EXP-11", "norm_hash": "e105eaa8"}, {"norm_id": "EXP-8", "norm_hash": "a0b54578"}]}\n')
    after = commit(both)
    result = run(both, after)
    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        f"grammar: cannot be read: {grammar_path()} at {after}: line 2: grammar:12 cites EXP-11@e105eaa8, and the norm "
        "hash of EXP-11 in data/tree.jsonl is 5a627175\n"
        "semantics: no change\n"
        "derived norms cannot be read\n")


def test_a_derived_norm_that_cites_a_norm_the_tree_does_not_hold_is_behind_its_norms(both: Path) -> None:
    """NRM-11 rules 5 and 7: a cited norm ID that no line of type node of data/tree.jsonl holds."""
    write_tree(both, {"EXP-8": "a0b54578"})
    write(both, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "11111111"}))
    after = commit(both)
    assert run(both, after).stdout.splitlines()[0] == (
        f"grammar: cannot be read: {grammar_path()} at {after}: line 2: grammar:1 cites EXP-11, which data/tree.jsonl "
        "does not hold")


def write_tree_with_a_retired_node(root: Path, retired_norm_id: str, norm_hash: str, status: object = "retired") -> None:
    """data/tree.jsonl of NORM_HASHES_IN_TREE without retired_norm_id, then, last as R61 says, one line of type node of
    retired_norm_id with the given status and its last tree_hash."""
    write_tree(root, {norm_id: h for norm_id, h in NORM_HASHES_IN_TREE.items() if norm_id != retired_norm_id})
    with (root / TREE_PATH).open("a", encoding="utf-8") as tree:
        tree.write(json.dumps({"id": retired_norm_id, "own_text": "x", "status": status,
                               "tree_hash": norm_hash + "0" * 56, "type": "node"}, sort_keys=True) + "\n")


@pytest.mark.parametrize("status", ["retired", "edited", None])
def test_a_derived_norm_that_cites_a_retired_norm_is_behind_its_norms(both: Path, status: object) -> None:
    """NRM-11 rules 5 and 7, case 2 of the check against data/tree.jsonl, R61: a retired node stays in data/tree.jsonl
    as a line of type node with its last tree_hash, but holds no norm; nor does a node of any status but active.
    A derived norm that still cites the retired norm with its last norm hash is behind its norms, and the run stops."""
    write_tree_with_a_retired_node(both, "EXP-11", "e105eaa8", status)
    write(both, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "11111111"}))
    after = commit(both)
    result = run(both, after)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0] == (
        f"grammar: cannot be read: {grammar_path()} at {after}: line 2: grammar:1 cites EXP-11, which data/tree.jsonl "
        "does not hold")
    assert result.stdout.endswith("derived norms cannot be read\n")


def test_a_node_without_status_is_an_active_norm(both: Path) -> None:
    """NRM-11 rule 5, R61: a line of type node without status takes the default active, so it holds its norm."""
    lines = [{"type": "meta"}] + [{"id": norm_id, "tree_hash": norm_hash + "0" * 56, "type": "node"}
                                  for norm_id, norm_hash in NORM_HASHES_IN_TREE.items()]
    write(both, TREE_PATH, "".join(json.dumps(line) + "\n" for line in lines))
    write(both, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "11111111"}))
    result = run(both, commit(both))
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0] == "grammar: 1 new, 0 changed, 0 gone"


def test_a_norm_the_tree_does_not_hold_comes_before_an_old_norm_hash(both: Path) -> None:
    """NRM-11 rule 7: case 2 of the check against data/tree.jsonl, over the whole list, before case 3."""
    write_tree(both, {"EXP-11": "5a627175"})
    write(both, grammar_path(),
          META + valid_line()
          + valid_line(derived_norm_id="grammar:2", first_line=3, last_line=4,
                       cited_norms=[{"norm_id": "EXP-8", "norm_hash": "a0b54578"}]))
    after = commit(both)
    assert run(both, after).stdout.splitlines()[0] == (
        f"grammar: cannot be read: {grammar_path()} at {after}: line 3: grammar:2 cites EXP-8, which data/tree.jsonl "
        "does not hold")


@pytest.mark.parametrize("tree", [
    None,
    b"\xff\n",
    b'{"type": "meta"}\nnot json\n',
    b'["node"]\n',
    b'{"id": 11, "tree_hash": "e105eaa8", "type": "node"}\n',
    b'{"id": "EXP-11", "type": "node"}\n',
])
def test_a_tree_that_cannot_be_read_makes_a_list_with_a_derived_norm_unreadable(norms_repository: Path,
                                                                              tree: bytes | None) -> None:
    """NRM-11 rule 7, case 1 of the check against data/tree.jsonl."""
    if tree is not None:
        (norms_repository / "data").mkdir()
        (norms_repository / TREE_PATH).write_bytes(tree)
    write(norms_repository, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "11111111"}))
    write(norms_repository, semantics_path(), derived_norm_list("semantics", 0, {}))
    after = commit(norms_repository)
    assert run(norms_repository, after).stdout == (
        f"grammar: cannot be read: {grammar_path()} at {after}: data/tree.jsonl cannot be read\n"
        "semantics: no change\n"
        "derived norms cannot be read\n")


def test_a_list_without_derived_norms_needs_no_tree(norms_repository: Path) -> None:
    """NRM-11 rule 7: only a list that holds a derived norm is checked against data/tree.jsonl."""
    write(norms_repository, grammar_path(), derived_norm_list("grammar", 3, {}))
    write(norms_repository, semantics_path(), derived_norm_list("semantics", 0, {}))
    result = run(norms_repository, commit(norms_repository))
    assert result.stdout == "grammar: no change\nsemantics: no change\nderived norms changed: no\n"


def test_the_list_of_the_commit_before_the_last_step_is_not_checked_against_the_tree(both: Path) -> None:
    """NRM-11 rules 4 and 7: a list of the commit before the last step whose derived norm cites an old norm hash still
    counts with its derived norms; the derived norm whose generator updated its citation is changed."""
    write(both, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "11111111"}))
    commit(both)
    write_tree(both, {"EXP-11": "5a627175", "EXP-8": "a0b54578"})
    write(both, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "22222222"}).replace("e105eaa8", "5a627175"))
    result = run(both, commit(both))
    assert result.stdout == "grammar: 0 new, 1 changed, 0 gone\n  changed: grammar:1\nsemantics: no change\nderived norms changed: yes\n"


def test_a_tree_line_with_a_line_separator_is_one_line(both: Path) -> None:
    """R61, NRM-11 rule 5: a JSON string of data/tree.jsonl may hold U+2028 as it is; it splits no line."""
    assert "\u2028" in (both / TREE_PATH).read_text(encoding="utf-8")
    write(both, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "11111111"}))
    assert run(both, commit(both)).stdout.endswith("derived norms changed: yes\n")


def test_types_in_the_order_of_project_json(both: Path) -> None:
    """NRM-11: each type in the order of NRM-1, also with the json output."""
    write(both, semantics_path(), derived_norm_list("semantics", 1, {"semantics:1": "11111111"}))
    after = commit(both)
    data = comparison(both, after)
    assert data["commit_of_layer_2_of_the_run"] == after
    assert [t["type"] for t in data["comparisons_of_types_of_derived_norms"]] == ["grammar", "semantics"]
    assert data["comparisons_of_types_of_derived_norms"][1] == {"type": "semantics", "named_by_derived_norms": True, "new": ["semantics:1"], "changed": [],
                                "gone": [], "error": None}
    assert data["derived_norms_changed"] is True and data["derived_norms_readable"] is True


def test_the_types_come_from_the_project_json_of_the_commit(both: Path) -> None:
    """NRM-1, NRM-11: the types are those of the project.json of the commit of layer 2 of the run."""
    head = git(both, "rev-parse", "HEAD")
    write(both, "project.json", json.dumps({"repositories": []}))
    assert run(both, head).stdout.endswith("semantics: no change\nderived norms changed: no\n")


def test_a_project_without_derived_norms(norms_repository: Path) -> None:
    """NRM-1, NRM-11: a project without derived_norms has none, and none changed."""
    write(norms_repository, "project.json", json.dumps({"repositories": []}))
    commit(norms_repository)
    result = run(norms_repository, commit(norms_repository))
    assert result.stdout == "no type of derived norms\nderived norms changed: no\n"


@pytest.mark.parametrize("commit_name", ["0000000000000000000000000000000000000000", "nothing-here"])
def test_a_commit_that_cannot_be_read_is_an_error(norms_repository: Path, commit_name: str) -> None:
    """NRM-11 rules 2 and 7: without the commit there is no comparison: exit 1 with the reason, the commit as given."""
    result = run(norms_repository, commit_name)
    assert result.returncode == 1
    assert result.stderr == no_comparison(commit_name, f"it is not a commit of {norms_repository.resolve()}")
    assert result.stdout == ""


def test_a_folder_that_is_not_a_git_repository_gives_no_comparison(tmp_path: Path) -> None:
    """NRM-11 rules 2 and 7: a norms repository that is not a git repository gives no comparison."""
    folder = tmp_path / "not-a-repository"
    folder.mkdir()
    result = subprocess.run([sys.executable, "-I", str(SCRIPT), "--norms-repository", str(folder), "--commit", "HEAD"],
                            capture_output=True, text=True, env={**ENV, "GIT_CEILING_DIRECTORIES": str(tmp_path)})
    assert result.returncode == 1 and result.stdout == ""
    assert result.stderr == no_comparison("HEAD", f"{folder.resolve()} is not a git repository")


@pytest.mark.parametrize("arguments", [[], ["--commit", "HEAD"], ["--norms-repository", "."], ["--json"],
                                       ["--norms", "{root}", "--com", "HEAD"], ["--norms-repository", "{root}", "--com", "HEAD"],
                                       ["--help"], ["-h"], ["--norms-repository", "{root}", "--commit", "HEAD", "--help"]])
def test_wrong_arguments_exit_2(norms_repository: Path, arguments: list[str]) -> None:
    """NRM-11 rule 7, outcome 3: without --norms-repository or --commit, or with another argument, exit 2 with the
    usage message on standard error and nothing on standard output; an abbreviated option and --help are other
    arguments."""
    if arguments == ["--json"]:
        arguments = ["--norms-repository", str(norms_repository), "--commit", "HEAD", "--json"]
    arguments = [argument.replace("{root}", str(norms_repository)) for argument in arguments]
    result = subprocess.run([sys.executable, "-I", str(SCRIPT), *arguments], capture_output=True, text=True, env=ENV)
    assert result.returncode == 2 and result.stdout == "" and result.stderr.startswith("usage: ")


def test_a_missing_project_json_is_an_error(norms_repository: Path) -> None:
    """NRM-1: the types come from project.json."""
    (norms_repository / "project.json").unlink()
    after = commit(norms_repository)
    result = run(norms_repository, after)
    assert result.returncode == 1 and result.stdout == ""
    assert result.stderr == no_comparison(after, "project.json cannot be read")


def remove_commit_object(root: Path, commit_of_the_walk: str) -> None:
    """Make git unable to read a commit: delete its loose object, as the commits of these fixtures are."""
    (root / ".git" / "objects" / commit_of_the_walk[:2] / commit_of_the_walk[2:]).unlink()


def test_a_commit_of_the_walk_whose_parents_cannot_be_read_gives_no_comparison(norms_repository: Path) -> None:
    """NRM-11, rule 2 and rule 7, outcome 2: a commit of the walk along the first parents whose parents git cannot
    read gives no comparison; the reason names that commit, in its 40 hex digits, and the message the commit of
    layer 2 of the run."""
    first = git(norms_repository, "rev-parse", "HEAD")
    commit_of_the_walk = commit(norms_repository)
    after = commit(norms_repository)
    remove_commit_object(norms_repository, first)
    result = run(norms_repository, after)
    assert result.returncode == 1 and result.stdout == ""
    assert result.stderr == no_comparison(after, f"the parents of {commit_of_the_walk} cannot be read")


def test_the_parents_that_cannot_be_read_come_before_project_json(norms_repository: Path) -> None:
    """NRM-11, rule 7, outcome 2: when the parents of a commit of the walk cannot be read and project.json cannot be
    read either, the reason is the first case that holds in the order of the list: the parents."""
    first = git(norms_repository, "rev-parse", "HEAD")
    (norms_repository / "project.json").unlink()
    after = commit(norms_repository)
    remove_commit_object(norms_repository, first)
    result = run(norms_repository, after)
    assert result.returncode == 1 and result.stdout == ""
    assert result.stderr == no_comparison(after, f"the parents of {after} cannot be read")


DERIVED_NORMS_THAT_DO_NOT_MEET_ORC_20 = [
    [{"type": "Grammar", "use_case": "/x:y"}],
    [{"type": "g", "use_case": "/x:y"}, {"type": "g", "use_case": "/x:z"}],
    "grammar",
    None,
    [{"use_case": "/x:y"}],
    [{"type": "grammar"}],
    [{"type": "grammar", "use_case": None}],
    [{"type": "grammar", "use_case": "x:y"}],
    [{"type": "grammar", "use_case": "/x"}],
    [{"type": "grammar", "use_case": "/x:"}],
    [{"type": "grammar", "use_case": "/:y"}],
    [{"type": "grammar", "use_case": "/X:y"}],
    [{"type": "grammar", "use_case": "/x:y:z"}],
    [{"type": "grammar", "use_case": "/x:y\n"}],
    [{"type": "grammar", "use_case": "/x:y"}, {"type": "semantics"}],
    ["grammar"],
]


@pytest.mark.parametrize("derived_norms", DERIVED_NORMS_THAT_DO_NOT_MEET_ORC_20)
def test_derived_norms_that_do_not_meet_orc_20_are_an_error(norms_repository: Path, derived_norms) -> None:
    """NRM-1, rule 2, ORC-20: a list of objects, each with a type of lower-case ASCII letters, digits and -, unique in
    the list, and a use_case /<module>:<use case>."""
    write(norms_repository, "project.json", json.dumps({"derived_norms": derived_norms}))
    after = commit(norms_repository)
    result = run(norms_repository, after)
    assert result.returncode == 1 and result.stdout == ""
    assert result.stderr == no_comparison(after, "derived_norms of project.json does not meet ORC-20")


@pytest.mark.parametrize("text", ["[]", "\"x\"", "null", "not json"])
def test_a_project_json_that_cannot_be_read_is_an_error(norms_repository: Path, text: str) -> None:
    """NRM-1, rule 1, NRM-11, rule 2: a project.json that is not a JSON object cannot be read: no comparison."""
    write(norms_repository, "project.json", text)
    after = commit(norms_repository)
    result = run(norms_repository, after)
    assert result.returncode == 1 and result.stderr == no_comparison(after, "project.json cannot be read")
    assert result.stdout == ""


def test_a_project_json_that_is_not_utf_8_is_an_error(norms_repository: Path) -> None:
    """NRM-1, rule 1."""
    (norms_repository / "project.json").write_bytes(b'{"derived_norms": [{"type": "gr\xe9", "use_case": "/x:y"}]}')
    after = commit(norms_repository)
    result = run(norms_repository, after)
    assert result.returncode == 1 and result.stderr == no_comparison(after, "project.json cannot be read")


def test_a_use_case_with_digits_and_hyphens_meets_orc_20(norms_repository: Path) -> None:
    """NRM-1, rule 2; rule 3: whether the use case exists is not checked."""
    write(norms_repository, "project.json", json.dumps({"derived_norms": [
        {"type": "grammar-2", "use_case": "/no-such-module-9:derive-2"}]}))
    write(norms_repository, "specs-derived/grammar-2/derived-norms.jsonl", derived_norm_list("grammar-2", 0, {}))
    result = run(norms_repository, commit(norms_repository))
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("grammar-2: no change\n")
    assert result.stdout.endswith("derived norms changed: no\n")


def record_path() -> str:
    return "specs-derived/types-of-derived-norms.json"


def record(*types: str) -> str:
    return json.dumps({"types_of_derived_norms": list(types)}) + "\n"


def project_json(*types: str) -> str:
    return json.dumps({"repositories": [], "derived_norms": [{"type": t, "use_case": f"/x:{t}"} for t in types]})


def test_a_commit_that_changed_only_project_json_is_compared_with_the_commit_before_the_last_step(both: Path) -> None:
    """NRM-11 rule 1, Commit of a step: a head from before the step that changed only project.json, as a sync does, is
    no commit of a step; the walk goes on to the last commit of a step, whose first parent is compared."""
    write(both, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "11111111"}))
    step = commit(both)
    write(both, "project.json", project_json("grammar", "semantics") + " ")
    sync = commit(both)
    data = comparison(both, sync)
    assert data["last_commit_of_a_step"] == step
    assert data["commit_before_the_last_step"] == git(both, "rev-parse", f"{step}^1")
    assert data["comparisons_of_types_of_derived_norms"][0]["new"] == ["grammar:1"]


def test_what_a_pull_brought_is_compared_with_the_commit_before_the_last_step(both: Path) -> None:
    """NRM-11 rules 1 and 3: the merge commit of an earlier pull, the head from before the step, is what layers 3 and 4
    read; compared with the commit before the last step, it shows both what the earlier step changed and what the
    pull brought."""
    base = git(both, "rev-parse", "HEAD")
    write(both, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "11111111"}))
    commit(both)
    git(both, "checkout", "-q", "-b", "remote", base)
    write(both, semantics_path(), derived_norm_list("semantics", 1, {"semantics:1": "22222222"}))
    commit(both)
    git(both, "checkout", "-q", "main")
    git(both, "merge", "-q", "--no-ff", "--no-edit", "remote")
    assert run(both, "HEAD").stdout == ("grammar: 1 new, 0 changed, 0 gone\n  new: grammar:1\n"
                                        "semantics: 1 new, 0 changed, 0 gone\n  new: semantics:1\n"
                                        "derived norms changed: yes\n")


def test_a_history_without_a_commit_of_a_step_has_no_derived_norms_before(norms_repository: Path) -> None:
    """NRM-11 rule 4, Last commit of a step: when the walk meets no commit of a step, there is no commit before the last
    step, and every list counts there as a list with no derived norm."""
    data = comparison(norms_repository, "HEAD")
    assert data["last_commit_of_a_step"] is None and data["commit_before_the_last_step"] is None
    assert [t["error"] for t in data["comparisons_of_types_of_derived_norms"]] == [
        f"{grammar_path()} at {data['commit_of_layer_2_of_the_run']}: it does not exist",
        f"{semantics_path()} at {data['commit_of_layer_2_of_the_run']}: it does not exist"]


def test_a_type_that_derived_norms_no_longer_names_is_gone(both: Path) -> None:
    """NRM-11 rules 2 and 5, NRM-16: the derived norms of a type that the record of the commit no longer names are gone,
    even when its list stays in the repository, and the type comes after the others; the next step does not report
    them again."""
    write(both, grammar_path(), derived_norm_list("grammar", 2, {"grammar:1": "11111111", "grammar:2": "22222222"}))
    write(both, record_path(), record("grammar", "semantics"))
    commit(both)
    write(both, "project.json", project_json("semantics"))
    write(both, record_path(), record("semantics"))
    dropped = commit(both)
    result = run(both, dropped)
    assert result.stdout == ("semantics: no change\n"
                             "grammar (no longer in derived_norms): 0 new, 0 changed, 2 gone\n"
                             "  gone: grammar:1, grammar:2\n"
                             "derived norms changed: yes\n")
    data = comparison(both, dropped)
    assert data["comparisons_of_types_of_derived_norms"][1]["named_by_derived_norms"] is False
    assert data["types_of_derived_norms_of_commit_of_layer_2_of_the_run"] == ["semantics"] and data["types_of_derived_norms_of_commit_before_the_last_step"] == ["grammar", "semantics"]
    write(both, semantics_path(), derived_norm_list("semantics", 1, {"semantics:1": "33333333"}))
    assert run(both, commit(both)).stdout == ("semantics: 1 new, 0 changed, 0 gone\n  new: semantics:1\n"
                                              "derived norms changed: yes\n")


def test_a_type_named_again_compares_with_no_derived_norm(both: Path) -> None:
    """NRM-11 rule 4: at the commit before the last step, the list of a type that is not one of its types of derived
    norms counts as a list with no derived norm, even when the list is still there."""
    write(both, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "11111111"}))
    write(both, record_path(), record("semantics"))
    commit(both)
    write(both, record_path(), record("grammar", "semantics"))
    assert run(both, commit(both)).stdout.splitlines()[:2] == ["grammar: 1 new, 0 changed, 0 gone", "  new: grammar:1"]


def test_a_new_order_of_the_types_is_a_change(both: Path) -> None:
    """NRM-11 rule 6, ORC-10: two types in another order than at the commit before the last step is a change, also when
    no derived norm changed."""
    write(both, record_path(), record("grammar", "semantics"))
    commit(both)
    write(both, "project.json", project_json("semantics", "grammar"))
    write(both, record_path(), record("semantics", "grammar"))
    after = commit(both)
    assert run(both, after).stdout == ("semantics: no change\ngrammar: no change\n"
                                       "order of the types changed: grammar, semantics -> semantics, grammar\n"
                                       "derived norms changed: yes\n")
    data = comparison(both, after)
    assert data["order_of_the_types_changed"] is True and data["derived_norms_changed"] is False


def test_a_new_type_between_two_others_is_no_new_order(both: Path) -> None:
    """NRM-11 rule 6: only the order of the types that both commits hold counts."""
    write(both, record_path(), record("grammar", "semantics"))
    commit(both)
    write(both, "specs-derived/lexicon/derived-norms.jsonl", derived_norm_list("lexicon", 0, {}))
    write(both, record_path(), record("grammar", "lexicon", "semantics"))
    data = comparison(both, commit(both))
    assert data["order_of_the_types_changed"] is False and data["derived_norms_changed"] is False


def test_the_record_comes_before_project_json(both: Path) -> None:
    """Types of derived norms of a commit, NRM-16: the record of the commit, when it meets NRM-16, gives its types, not
    its project.json."""
    write(both, record_path(), record("grammar"))
    data = comparison(both, commit(both))
    assert data["types_of_derived_norms_of_commit_of_layer_2_of_the_run"] == ["grammar"]
    assert [t["type"] for t in data["comparisons_of_types_of_derived_norms"]] == ["grammar", "semantics"]
    assert data["comparisons_of_types_of_derived_norms"][1]["named_by_derived_norms"] is False


@pytest.mark.parametrize("text", [
    "",
    '{"types_of_derived_norms": ["grammar"]}',
    ' {"types_of_derived_norms": ["grammar"]}\n',
    '{"types_of_derived_norms": ["grammar"]} \n',
    '{"types_of_derived_norms": ["grammar"]}\t\n',
    '{\n"types_of_derived_norms": ["grammar"]\n}\n',
    '{"types_of_derived_norms": ["grammar"]}\r\n',
    '﻿{"types_of_derived_norms": ["grammar"]}\n',
    '{"types_of_derived_norms": ["grammar"]}\n\n',
    '{"types_of_derived_norms": ["Grammar"]}\n',
    '{"types_of_derived_norms": ["grammar", "grammar"]}\n',
    '{"types_of_derived_norms": "grammar"}\n',
    '{"types_of_derived_norms": {}}\n',
    '{"types_of_derived_norms": {"grammar": 1}}\n',
    '{"types_of_derived_norms": ["grammar"], "other": 1}\n',
    '["grammar"]\n',
])
def test_a_record_that_does_not_meet_nrm_16_gives_way_to_project_json(both: Path, text: str) -> None:
    """Types of derived norms of a commit, NRM-16: a record that does not meet NRM-16 is not read, and the types are
    those of project.json."""
    write(both, record_path(), text)
    data = comparison(both, commit(both))
    assert data["types_of_derived_norms_of_commit_of_layer_2_of_the_run"] == ["grammar", "semantics"]


@pytest.mark.parametrize("text", [
    '{"types_of_derived_norms": ["semantics"]}\n',
    '{"types_of_derived_norms":["semantics"]}\n',
    '{ "types_of_derived_norms" : [ "semantics" ] }\n',
])
def test_a_record_that_meets_nrm_16_is_read(both: Path, text: str) -> None:
    """NRM-16: a record of one line, its JSON object from the first character to the line feed, is read, with or
    without white space inside the object."""
    write(both, record_path(), text)
    data = comparison(both, commit(both))
    assert data["types_of_derived_norms_of_commit_of_layer_2_of_the_run"] == ["semantics"]


def test_a_commit_before_the_last_step_without_types_has_none(both: Path) -> None:
    """NRM-11 rule 4: a commit before the last step with neither a record nor a project.json that can be read has no
    types of derived norms."""
    (both / "project.json").write_text("not json", encoding="utf-8")
    commit(both)
    write(both, "project.json", project_json("grammar", "semantics"))
    write(both, grammar_path(), derived_norm_list("grammar", 1, {"grammar:1": "11111111"}))
    data = comparison(both, commit(both))
    assert data["types_of_derived_norms_of_commit_before_the_last_step"] == []
    assert data["comparisons_of_types_of_derived_norms"][0]["new"] == ["grammar:1"]


def run_writer(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", str(WRITER), "--norms-repository", str(root)], capture_output=True, text=True, env=ENV)


def test_the_writer_writes_the_record_of_the_types_of_derived_norms(norms_repository: Path) -> None:
    """NRM-16: the record holds the types of derived_norms of project.json, in their order, in one line."""
    result = run_writer(norms_repository)
    assert result.returncode == 0, result.stderr
    assert result.stdout == record_path() + "\n"
    assert (norms_repository / record_path()).read_bytes() == b'{"types_of_derived_norms": ["grammar", "semantics"]}\n'


def test_the_writer_writes_an_empty_record_without_derived_norms(norms_repository: Path) -> None:
    """NRM-16: [] when the project has no derived norms."""
    write(norms_repository, "project.json", json.dumps({"repositories": []}))
    assert run_writer(norms_repository).returncode == 0
    assert (norms_repository / record_path()).read_text(encoding="utf-8") == record()


@pytest.mark.parametrize("text", [
    "not json", "[]", "null",
    json.dumps({"derived_norms": [{"type": "Grammar", "use_case": "/x:y"}]}),
    json.dumps({"derived_norms": [{"type": "grammar"}]}),
    json.dumps({"derived_norms": [{"type": "grammar", "use_case": "derive-grammar"}]}),
    None,
])
def test_the_writer_writes_nothing_when_derived_norms_cannot_be_read(norms_repository: Path, text: str | None) -> None:
    """NRM-16: when derived_norms does not meet ORC-20, or project.json cannot be read, the script writes nothing and
    says why."""
    if text is None:
        (norms_repository / "project.json").unlink()
    else:
        write(norms_repository, "project.json", text)
    result = run_writer(norms_repository)
    reason = ("project.json cannot be read" if text is None or not text.startswith('{"derived_norms"')
              else "derived_norms of project.json does not meet ORC-20")
    assert result.returncode == 1 and result.stdout == ""
    assert result.stderr == f"norms-management: the record of the types of derived norms is not written (NRM-16): {reason}\n"
    assert not (norms_repository / record_path()).exists()


def test_the_writer_leaves_the_record_before_unchanged_on_an_error(norms_repository: Path) -> None:
    """NRM-16, outcome 2: the record that the working tree held stays as it was."""
    write(norms_repository, record_path(), record("grammar"))
    write(norms_repository, "project.json", "not json")
    assert run_writer(norms_repository).returncode == 1
    assert (norms_repository / record_path()).read_text(encoding="utf-8") == record("grammar")


def test_the_writer_says_when_the_file_cannot_be_written(norms_repository: Path) -> None:
    """NRM-16, outcome 2: a record that cannot be written, here because specs-derived is a file."""
    write(norms_repository, "specs-derived", "a file\n")
    result = run_writer(norms_repository)
    assert result.returncode == 1 and result.stdout == ""
    assert result.stderr == ("norms-management: the record of the types of derived norms is not written (NRM-16): "
                             "the file cannot be written\n")


@pytest.mark.parametrize("arguments", [[], ["--norms", "{root}"], ["--help"], ["-h"],
                                       ["--norms-repository", "{root}", "--help"], ["--norms-repository", "{root}", "--json"]])
def test_the_writer_without_its_argument_or_with_another_exits_2(norms_repository: Path, arguments: list[str]) -> None:
    """NRM-16, outcome 3: without --norms-repository, or with another argument, an abbreviated option and --help among
    them, it writes nothing, no record either, and exits 2 with the usage message on standard error."""
    arguments = [argument.replace("{root}", str(norms_repository)) for argument in arguments]
    result = subprocess.run([sys.executable, "-I", str(WRITER), *arguments], capture_output=True, text=True, env=ENV)
    assert result.returncode == 2 and result.stdout == "" and result.stderr.startswith("usage: ")
    assert not (norms_repository / record_path()).exists()


def test_the_record_that_the_writer_writes_meets_nrm_16(norms_repository: Path) -> None:
    """NRM-16: the comparison reads the record that the writer wrote."""
    write(norms_repository, "project.json", project_json("semantics"))
    run_writer(norms_repository)
    write(norms_repository, "project.json", project_json("grammar"))
    data = comparison(norms_repository, commit(norms_repository))
    assert data["types_of_derived_norms_of_commit_of_layer_2_of_the_run"] == ["semantics"]


PYTHON_3_9 = Path("/usr/bin/python3")


def python_3_9() -> str:
    """The python3 of macOS, 3.9, the lowest that the app supports (MTH-5); skips when this machine has none."""
    if not PYTHON_3_9.is_file():
        pytest.skip("no /usr/bin/python3")
    version = subprocess.run([str(PYTHON_3_9), "-c", "import sys; print(sys.version_info[:2] == (3, 9))"],
                             capture_output=True, text=True)
    if version.stdout.strip() != "True":
        pytest.skip("/usr/bin/python3 is not Python 3.9")
    return str(PYTHON_3_9)


def test_both_scripts_run_with_python_3_9(both: Path) -> None:
    """MTH-5: the step of layer 2 runs both scripts as python3 -I, which may be Python 3.9."""
    python = python_3_9()
    write(both, "project.json", project_json("grammar"))
    writer = subprocess.run([python, "-I", str(WRITER), "--norms-repository", str(both)], capture_output=True, text=True, env=ENV)
    assert writer.returncode == 0, writer.stderr
    result = subprocess.run([python, "-I", str(SCRIPT), "--norms-repository", str(both), "--commit", commit(both)],
                            capture_output=True, text=True, env=ENV)
    assert result.returncode == 0, result.stderr
    assert result.stdout == "grammar: no change\nsemantics (no longer in derived_norms): no change\nderived norms changed: no\n"


def test_every_script_of_the_build_imports_annotations_from_the_future() -> None:
    """MTH-5: annotations such as str | None are not evaluated under Python 3.9, also where no 3.9 can be run."""
    for script in (SCRIPT, WRITER):
        assert "from __future__ import annotations\n" in script.read_text(encoding="utf-8"), script


@pytest.mark.parametrize("text", [b'{"types_of_derived_norms": {}}\n', b'{"types_of_derived_norms": {"grammar": 1}}\n'])
def test_a_record_whose_field_is_a_json_object_does_not_meet_nrm_16(text: bytes) -> None:
    """NRM-16: the types are a JSON array; a JSON object, even an empty one, is no list of types."""
    with pytest.raises(compare_derived_norms.TypesOfDerivedNormsError):
        compare_derived_norms.types_of_derived_norms_of_record(text)


def test_the_skill_ends_the_report_with_the_lines_of_nrm_11() -> None:
    """NRM-11, ORC-10: the closing line of the report is one of the three lines of NRM-11, byte for byte."""
    spec = (PLUGIN / "specs" / "module.md").read_text(encoding="utf-8")
    skill = (PLUGIN / "use-cases" / "build" / "SKILL.md").read_text(encoding="utf-8")
    for line in ("The run stops after layer 2: the derived norms cannot be read (ORC-10).",
                 "The run ends after layer 2: no norm, no derived norm and no order of the types of derived norms "
                 "changed (ORC-10).",
                 "Layers 3 and 4 follow (ORC-10)."):
        assert f"`{line}`" in spec and f"`{line}`" in skill
