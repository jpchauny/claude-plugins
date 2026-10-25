"""Tests of cli.py: `norms-gen build`, `verify` and `report` on a temporary git specs repository.

Each test makes a small specs repository, commits it, builds, edits
and commits again, and rebuilds, checking the outputs.

Spec: R7, R11, R12, R13, R15, R34, R57, R58, R59, R60, R61, R62, R63, R64
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from norms_generator.cli import main
from norms_generator.store import read_store


class SpecsRepo:
    """A throwaway specs git repository."""

    def __init__(self, root: Path) -> None:
        self.root = root
        root.mkdir()
        self.git("init", "-q", "-b", "main")

    def git(self, *args: str) -> str:
        done = subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "-C", str(self.root), *args],
            capture_output=True,
            check=True,
        )
        return done.stdout.decode()

    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))

    def commit(self, message: str = "c") -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self.git("rev-parse", "HEAD").strip()


@pytest.fixture
def specs_repo(tmp_path: Path) -> SpecsRepo:
    return SpecsRepo(tmp_path / "specs")


@pytest.fixture
def out(tmp_path: Path) -> Path:
    return tmp_path / "norms"


def build(specs_repo: SpecsRepo, out: Path, *extra: str) -> None:
    assert main(["build", "--specs", str(specs_repo.root), "--out", str(out), *extra]) == 0


def verify(specs_repo: SpecsRepo, out: Path) -> int:
    return main(["verify", "--specs", str(specs_repo.root), "--out", str(out)])


def nodes(out: Path) -> list[dict[str, object]]:
    lines = (out / "data" / "tree.jsonl").read_text(encoding="utf-8").splitlines()
    return [obj for obj in map(json.loads, lines) if obj["type"] == "node"]


def by_text(out: Path, text: str, status: str = "active") -> dict[str, object]:
    """The one node of `status` whose own text is `text`."""
    found = [n for n in nodes(out) if n["own_text"] == text and n["status"] == status]
    assert len(found) == 1, found
    return found[0]


def snapshot(out: Path) -> dict[str, bytes]:
    return {p.relative_to(out).as_posix(): p.read_bytes() for p in sorted(out.rglob("*")) if p.is_file()}


TYPES = """\
# Types

Clean has a small set of built-in types.

## Numbers

Numbers are always signed.

- integer is 64 bits
- float is 64 bits
- string is UTF-8

1. Parse the file.
1. Check the types.
1. Emit WebAssembly.
"""

BUILD = """\
# Build

Run the build.
"""


def first(specs_repo: SpecsRepo, out: Path) -> str:
    specs_repo.write("specs/language/type-system.md", TYPES)
    specs_repo.write("specs/tooling/build.md", BUILD)
    specs_repo.write("README.md", "Not a spec.\n")
    sha = specs_repo.commit()
    build(specs_repo, out)
    return sha


def test_first_build(specs_repo: SpecsRepo, out: Path) -> None:
    """A first run writes the JSONL, the annotated copies of every selected file, the README included, and the reports, and verifies.

    Spec: R10, R29, R53, R62, R63, R64
    """
    sha = first(specs_repo, out)
    store = read_store(out / "data" / "tree.jsonl")
    assert store.specs_commit == sha
    assert sorted(store.files) == ["README.md", "specs/language/type-system.md", "specs/tooling/build.md"]
    assert store.files["specs/language/type-system.md"].prefix == "TYP"
    assert store.files["specs/tooling/build.md"].prefix == "BUI"
    annotated = (out / "specs-repo-annotated" / "specs/language/type-system.md").read_text(encoding="utf-8")
    assert annotated.startswith("⟬TYP⟭\n\n⟬TYP-1 begin⟭\n\n# Types ⟬TYP-2⟭\n")
    assert "- integer is 64 bits ⟬TYP-" in annotated
    assert (out / "specs-repo-annotated" / "README.md").read_text(encoding="utf-8").startswith("⟬REA⟭")
    report = (out / "data" / "report.md").read_text(encoding="utf-8")
    assert "first run" in report and "new: " in report
    assert all(json.loads(line)["status"] == "new" for line in (out / "data" / "report.json").read_text().splitlines())
    assert verify(specs_repo, out) == 0


def test_rebuild_is_a_no_op(specs_repo: SpecsRepo, out: Path) -> None:
    """A rebuild of the same commit leaves every output byte for byte as it was.

    Spec: R60, R62
    """
    first(specs_repo, out)
    before = snapshot(out)
    build(specs_repo, out)
    assert snapshot(out) == before


def test_rebuild_keeps_flags_and_report(specs_repo: SpecsRepo, out: Path) -> None:
    """A rebuild that changed nothing keeps the reports and the flags of its step.

    Spec: R60
    """
    first(specs_repo, out)
    specs_repo.write("specs/tooling/build.md", BUILD.replace("Run the build.", "Run the whole build."))
    specs_repo.commit()
    build(specs_repo, out)
    before = snapshot(out)
    build(specs_repo, out)
    assert snapshot(out) == before
    assert by_text(out, "Run the whole build.")["to_review"] is True


def test_flags_describe_one_version_only_u3(specs_repo: SpecsRepo, out: Path) -> None:
    """to_review and changed_since compare version N with N-1; the next version clears them.

    Spec: R21, R31, R60, U3 (E84)
    """
    first(specs_repo, out)
    specs_repo.write("specs/tooling/build.md", BUILD.replace("Run the build.", "Run the whole build."))
    specs_repo.commit()
    build(specs_repo, out)
    assert by_text(out, "Run the whole build.")["to_review"] is True
    specs_repo.write("specs/language/type-system.md", TYPES.replace("always signed.", "always signed, 64 bits."))
    specs_repo.commit()
    build(specs_repo, out)
    node = by_text(out, "Run the whole build.")
    assert node["to_review"] is False and node["changed_since"] is None
    assert by_text(out, "Numbers are always signed, 64 bits.")["to_review"] is True


def test_edit_marks_to_review(specs_repo: SpecsRepo, out: Path) -> None:
    """An edited paragraph keeps its ID, is to review, and is reported with its old text; its section is changed below.

    Spec: R15, R59, R60, R63 (E69)
    """
    old_sha = first(specs_repo, out)
    old = by_text(out, "Numbers are always signed.")
    specs_repo.write("specs/language/type-system.md", TYPES.replace("always signed.", "always signed, 64 bits."))
    specs_repo.commit()
    build(specs_repo, out)
    new = by_text(out, "Numbers are always signed, 64 bits.")
    assert new["id"] == old["id"] and new["to_review"] is True
    assert new["changed_since"] == old_sha
    section = next(n for n in nodes(out) if n["id"] == new["parent"])
    assert section["changed_since"] == old_sha and section["to_review"] is False
    report = [json.loads(line) for line in (out / "data" / "report.json").read_text().splitlines()]
    edited = [r for r in report if r["status"] == "edited"]
    assert [r["id"] for r in edited] == [old["id"]]
    assert edited[0]["old_text"] == "Numbers are always signed."
    assert old["id"] in (out / "data" / "report.md").read_text(encoding="utf-8")
    assert verify(specs_repo, out) == 0


def test_move_to_another_file_keeps_id(specs_repo: SpecsRepo, out: Path) -> None:
    """A paragraph moved to another file keeps its ID and its prefix.

    Spec: R11, R54 (E77)
    """
    first(specs_repo, out)
    old = by_text(out, "Numbers are always signed.")
    specs_repo.write("specs/language/type-system.md", TYPES.replace("Numbers are always signed.\n\n", ""))
    specs_repo.write("specs/tooling/build.md", BUILD + "\nNumbers are always signed.\n")
    specs_repo.commit()
    build(specs_repo, out)
    new = by_text(out, "Numbers are always signed.")
    assert new["id"] == old["id"] and new["file"] == "specs/tooling/build.md"
    assert str(new["id"]).startswith("TYP-")  # R11: the prefix stays
    annotated = (out / "specs-repo-annotated" / "specs/tooling/build.md").read_text(encoding="utf-8")
    assert f"Numbers are always signed. ⟬{old['id']}⟭" in annotated
    assert verify(specs_repo, out) == 0


def test_rename_keeps_prefix(specs_repo: SpecsRepo, out: Path) -> None:
    """A renamed file keeps its prefix and IDs; its old annotated copy and empty folders are removed.

    Spec: R12, R58, R62 (E78)
    """
    first(specs_repo, out)
    old_ids = {n["id"] for n in nodes(out) if n["file"] == "specs/language/type-system.md"}
    (specs_repo.root / "specs/core").mkdir()
    specs_repo.git("mv", "specs/language/type-system.md", "specs/core/types.md")
    specs_repo.commit()
    build(specs_repo, out)
    store = read_store(out / "data" / "tree.jsonl")
    assert store.files["specs/core/types.md"].prefix == "TYP"
    assert {n["id"] for n in nodes(out) if n["file"] == "specs/core/types.md"} == old_ids
    assert not (out / "specs-repo-annotated" / "specs/language").exists()
    assert (out / "specs-repo-annotated" / "specs/core/types.md").exists()
    assert verify(specs_repo, out) == 0


def test_deleted_node_retired_and_number_not_reused(specs_repo: SpecsRepo, out: Path) -> None:
    """A removed node is retired and kept; a new node never takes its number.

    Spec: R57, R61 (E76)
    """
    first(specs_repo, out)
    gone = by_text(out, "Run the build.")
    top = max(int(str(n["id"]).split("-")[1]) for n in nodes(out) if str(n["id"]).startswith("BUI-"))
    specs_repo.write("specs/tooling/build.md", "# Build\n")
    specs_repo.commit()
    build(specs_repo, out)
    retired = by_text(out, "Run the build.", status="retired")
    assert retired["id"] == gone["id"]
    specs_repo.write("specs/tooling/build.md", "# Build\n\nSomething entirely different here.\n")
    specs_repo.commit()
    build(specs_repo, out)
    fresh = by_text(out, "Something entirely different here.")
    assert int(str(fresh["id"]).split("-")[1]) > top
    assert by_text(out, "Run the build.", status="retired")["id"] == gone["id"]
    assert verify(specs_repo, out) == 0


def _list_node(out: Path, item_text: str) -> dict[str, object]:
    item = by_text(out, item_text)
    return next(n for n in nodes(out) if n["id"] == item["parent"])


def test_reorder_bullets_is_no_change(specs_repo: SpecsRepo, out: Path) -> None:
    """Reordering bullets changes no hash and reports nothing.

    Spec: R8, R13, R59 (E74)
    """
    first(specs_repo, out)
    before = _list_node(out, "- integer is 64 bits")
    items = "- integer is 64 bits\n- float is 64 bits\n- string is UTF-8\n"
    specs_repo.write("specs/language/type-system.md", TYPES.replace(items, "- string is UTF-8\n- integer is 64 bits\n- float is 64 bits\n"))
    specs_repo.commit()
    build(specs_repo, out)
    after = _list_node(out, "- integer is 64 bits")
    assert after["id"] == before["id"] and after["tree_hash"] == before["tree_hash"]
    assert after["changed_since"] is None
    assert (out / "data" / "report.json").read_text() == ""


def test_reorder_numbered_is_a_change(specs_repo: SpecsRepo, out: Path) -> None:
    """Reordering a numbered list changes its tree hash; it is child_changed and reordered.

    Spec: R8, R59 (E75)
    """
    old_sha = first(specs_repo, out)
    before = _list_node(out, "1. Parse the file.")
    specs_repo.write(
        "specs/language/type-system.md",
        TYPES.replace("1. Parse the file.\n1. Check the types.\n", "1. Check the types.\n1. Parse the file.\n"),
    )
    specs_repo.commit()
    build(specs_repo, out)
    after = _list_node(out, "1. Parse the file.")
    assert after["id"] == before["id"] and after["tree_hash"] != before["tree_hash"]
    assert after["changed_since"] == old_sha
    report = {r["id"]: r for r in map(json.loads, (out / "data" / "report.json").read_text().splitlines())}
    assert report[after["id"]]["status"] == "child_changed" and report[after["id"]]["reordered"] is True


def test_verify_detects_tampering(specs_repo: SpecsRepo, out: Path) -> None:
    """verify exits 1 when an annotated copy was edited by hand.

    Spec: R64
    """
    first(specs_repo, out)
    path = out / "specs-repo-annotated" / "specs/tooling/build.md"
    path.write_bytes(path.read_bytes().replace(b"Run the build.", b"Run the builds."))
    assert verify(specs_repo, out) == 1


def test_verify_uses_the_pinned_commit(specs_repo: SpecsRepo, out: Path) -> None:
    """verify re-reads the specs at the commit the JSONL pins, not HEAD.

    Spec: R64
    """
    first(specs_repo, out)
    specs_repo.write("specs/tooling/build.md", "# Build\n\nChanged after the build.\n")
    specs_repo.commit()
    assert verify(specs_repo, out) == 0


def test_build_at_an_older_commit(specs_repo: SpecsRepo, out: Path) -> None:
    """`--commit` builds the specs at that commit.

    Spec: R62
    """
    sha = first(specs_repo, out)
    specs_repo.write("specs/tooling/build.md", "# Build\n\nLater.\n")
    specs_repo.commit()
    other = out.parent / "other"
    build(specs_repo, other, "--commit", sha)
    assert snapshot(other)["data/tree.jsonl"] == snapshot(out)["data/tree.jsonl"]


def test_report_prints_last_report(specs_repo: SpecsRepo, out: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`report` prints data/report.md, or data/report.json with `--json`, byte for byte.

    Spec: R62
    """
    first(specs_repo, out)
    capsys.readouterr()
    assert main(["report", "--out", str(out)]) == 0
    assert capsys.readouterr().out == (out / "data" / "report.md").read_text(encoding="utf-8")
    assert main(["report", "--out", str(out), "--json"]) == 0
    assert capsys.readouterr().out == (out / "data" / "report.json").read_text(encoding="utf-8")


def test_bad_specs_exits_non_zero(tmp_path: Path) -> None:
    """A spec path that is not a git repository is refused.

    Spec: R34
    """
    (tmp_path / "plain").mkdir()
    assert main(["build", "--specs", str(tmp_path / "plain"), "--out", str(tmp_path / "o")]) != 0


def test_default_out_is_the_git_root_of_the_working_directory(tmp_path, monkeypatch):
    """Without --out, the output folder is the git repository the command runs in, from any of its folders.

    Spec: R62
    """
    from norms_generator.cli import default_out

    repo = tmp_path / "project-norms"
    (repo / "sub").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    monkeypatch.chdir(repo / "sub")
    assert default_out().resolve() == repo.resolve()


def test_default_out_outside_git_is_the_working_directory(tmp_path, monkeypatch):
    """Without --out and outside any git repository, the output folder is the working directory.

    Spec: R62
    """
    from norms_generator.cli import default_out

    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    assert default_out().resolve() == tmp_path.resolve()
