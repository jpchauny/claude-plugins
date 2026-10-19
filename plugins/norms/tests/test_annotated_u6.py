"""After every build, annotated/ holds exactly this build's copies and their folders.

Everything else under annotated/ is removed before the copies are
written, a symbolic link itself and never what it leads to, and verify
names each such path as a problem.

Spec: R62, R64, U6
"""

from __future__ import annotations

from pathlib import Path

import pytest

from norms_generator.cli import main
from test_cli import Foundation


def _build(f: Foundation, out: Path) -> int:
    return main(["build", "--foundation", str(f.root), "--out", str(out)])


def _verify(f: Foundation, out: Path) -> int:
    return main(["verify", "--foundation", str(f.root), "--out", str(out)])


def _foreign(path: Path) -> str:
    return f"{path}: not an annotated copy of a JSONL file; build removes it (U6)"


def _built(tmp_path: Path) -> tuple[Foundation, Path, Path]:
    """A foundation of `specs/a.md` and `specs/sub/b.md`, built once; its annotated/ and the files under it."""
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "# A\n\nText.\n")
    f.write("specs/sub/b.md", "# B\n")
    f.commit()
    out = tmp_path / "norms"
    assert _build(f, out) == 0
    return f, out, out / "annotated"


def _tree(ann: Path) -> list[str]:
    return sorted(str(p.relative_to(ann)) for p in ann.rglob("*"))


_CLEAN = ["specs", "specs/a.md", "specs/sub", "specs/sub/b.md"]


def _rebuilt_clean(f: Foundation, out: Path, ann: Path, snapshot: dict[str, bytes]) -> None:
    """A rebuild of the same commit leaves exactly the copies, byte for byte as they were.

    Spec: R62, U6
    """
    assert _build(f, out) == 0
    assert _tree(ann) == _CLEAN
    assert {p: (ann / p).read_bytes() for p in ("specs/a.md", "specs/sub/b.md")} == snapshot
    assert _verify(f, out) == 0


def _copies(ann: Path) -> dict[str, bytes]:
    return {p: (ann / p).read_bytes() for p in ("specs/a.md", "specs/sub/b.md")}


def test_a_foreign_file_is_reported_and_removed_u6(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A file that is no copy, here next to a copy, is a problem of verify, then removed.

    Spec: R62, R64, U6
    """
    f, out, ann = _built(tmp_path)
    copies = _copies(ann)
    (ann / "specs" / "notes.txt").write_text("mine")
    (ann / "README.md").write_text("mine")
    capsys.readouterr()
    assert _verify(f, out) == 1
    assert capsys.readouterr().err == (
        f"{_foreign(ann / 'README.md')}\n{_foreign(ann / 'specs' / 'notes.txt')}\nverify: 2 problems\n"
    )
    _rebuilt_clean(f, out, ann, copies)


def test_a_foreign_folder_is_named_once_and_removed_with_its_contents_u6(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A folder that holds no copy is named once, and removed with everything in it.

    Spec: R62, R64, U6
    """
    f, out, ann = _built(tmp_path)
    copies = _copies(ann)
    (ann / "specs" / "old" / "deep").mkdir(parents=True)
    (ann / "specs" / "old" / "deep" / "x.md").write_text("⟬OLD⟭\n")
    (ann / "specs" / "empty").mkdir()
    capsys.readouterr()
    assert _verify(f, out) == 1
    assert capsys.readouterr().err == (
        f"{_foreign(ann / 'specs' / 'empty')}\n{_foreign(ann / 'specs' / 'old')}\nverify: 2 problems\n"
    )
    _rebuilt_clean(f, out, ann, copies)


@pytest.mark.parametrize("where", ["specs/link", "specs/sub/link.md", "top"])
@pytest.mark.parametrize("to", ["folder", "file", "nowhere"])
def test_a_link_to_outside_is_removed_and_its_target_survives_u6(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], where: str, to: str
) -> None:
    """A symbolic link is removed itself, never followed: what it leads to stays as it was.

    Spec: R62, R64, U6
    """
    f, out, ann = _built(tmp_path)
    copies = _copies(ann)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep.md").write_text("keep")
    target = {"folder": outside, "file": outside / "keep.md", "nowhere": outside / "none"}[to]
    link = ann / where
    link.symlink_to(target)
    capsys.readouterr()
    assert _verify(f, out) == 1
    assert capsys.readouterr().err == f"{_foreign(link)}\nverify: 1 problems\n"
    _rebuilt_clean(f, out, ann, copies)
    assert not link.is_symlink()
    assert sorted(p.name for p in outside.iterdir()) == ["keep.md"]
    assert (outside / "keep.md").read_text() == "keep"


def test_a_link_inside_a_foreign_folder_is_not_followed_u6(tmp_path: Path) -> None:
    """A foreign folder is removed with the links in it, and nothing they lead to is touched.

    Spec: R62, U6
    """
    f, out, ann = _built(tmp_path)
    copies = _copies(ann)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep.md").write_text("keep")
    (ann / "specs" / "old").mkdir()
    (ann / "specs" / "old" / "to-folder").symlink_to(outside)
    (ann / "specs" / "old" / "to-file.md").symlink_to(outside / "keep.md")
    _rebuilt_clean(f, out, ann, copies)
    assert (outside / "keep.md").read_text() == "keep"


def test_a_link_at_a_folder_of_copies_is_replaced_by_a_folder_u6(tmp_path: Path) -> None:
    """A link at a folder's path is removed, its target kept, and the folder written again.

    Spec: R62, U6
    """
    f, out, ann = _built(tmp_path)
    copies = _copies(ann)
    outside = tmp_path / "outside"
    (ann / "specs" / "sub").rename(outside)
    (ann / "specs" / "sub").symlink_to(outside)
    _rebuilt_clean(f, out, ann, copies)
    assert (outside / "b.md").read_bytes() == copies["specs/sub/b.md"]


def test_a_file_at_a_folder_s_path_is_replaced_by_the_folder_u6(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A file at a folder's path is the copy's `no annotated file`, not named again; build replaces it.

    Spec: R62, R64, U6
    """
    f, out, ann = _built(tmp_path)
    copies = _copies(ann)
    for child in (ann / "specs" / "sub").iterdir():
        child.unlink()
    (ann / "specs" / "sub").rmdir()
    (ann / "specs" / "sub").write_text("mine")
    capsys.readouterr()
    assert _verify(f, out) == 1
    assert capsys.readouterr().err == (
        f"specs/sub/b.md: no annotated file at {ann / 'specs' / 'sub' / 'b.md'}\nverify: 1 problems\n"
    )
    _rebuilt_clean(f, out, ann, copies)


def test_a_folder_at_a_copy_s_path_is_replaced_by_the_copy_u6(tmp_path: Path) -> None:
    """A folder at a copy's path is removed with everything in it, and the copy written.

    Spec: R62, U6
    """
    f, out, ann = _built(tmp_path)
    copies = _copies(ann)
    (ann / "specs" / "a.md").unlink()
    (ann / "specs" / "a.md" / "inner").mkdir(parents=True)
    (ann / "specs" / "a.md" / "inner" / "x.md").write_text("mine")
    _rebuilt_clean(f, out, ann, copies)


def test_a_name_that_differs_only_in_case_is_foreign_u6(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A name is kept only character for character; one differing in case is removed.

    Spec: R62, R64, U6
    """
    f, out, ann = _built(tmp_path)
    copies = _copies(ann)
    (ann / "specs" / "sub" / "b.md").unlink()
    (ann / "specs" / "sub").rename(ann / "specs" / "SUB")
    (ann / "specs" / "SUB" / "b.md").write_bytes(copies["specs/sub/b.md"])
    capsys.readouterr()
    assert _verify(f, out) == 1
    err = capsys.readouterr().err
    assert _foreign(ann / "specs" / "SUB") in err
    _rebuilt_clean(f, out, ann, copies)


def test_the_copies_a_lost_jsonl_left_are_removed_u6(tmp_path: Path) -> None:
    """With the JSONL lost, the copies of files foundation no longer holds are removed all the same.

    Spec: R62, U6
    """
    f, out, ann = _built(tmp_path)
    (f.root / "specs" / "sub" / "b.md").unlink()
    f.commit()
    (out / "data" / "tree.jsonl").unlink()
    assert _build(f, out) == 0
    assert _tree(ann) == ["specs", "specs/a.md"]
    assert _verify(f, out) == 0


def test_a_rebuild_of_the_same_commit_also_cleans_and_keeps_the_reports_u6(tmp_path: Path) -> None:
    """A rebuild of the same commit removes the foreign paths and leaves every output as it was.

    Spec: R60, R62, U6
    """
    f, out, ann = _built(tmp_path)
    outputs = {p: (out / "data" / p).read_bytes() for p in ("tree.jsonl", "report.md", "report.json")}
    copies = _copies(ann)
    (ann / "specs" / "stray.md").write_text("mine")
    (ann / "specs" / "sub" / "old").mkdir()
    _rebuilt_clean(f, out, ann, copies)
    assert {p: (out / "data" / p).read_bytes() for p in outputs} == outputs


def test_nothing_outside_the_output_folder_is_touched_u6(tmp_path: Path) -> None:
    """A sibling of the output folder, and the foundation, are left as they were.

    Spec: R62, U6
    """
    f, out, ann = _built(tmp_path)
    sibling = tmp_path / "sibling"
    sibling.mkdir()
    (sibling / "x.md").write_text("keep")
    (ann / "specs" / "up").symlink_to(Path("..") / ".." / ".." / "sibling")
    (ann / "specs" / "found").symlink_to(f.root / "specs")
    before = sorted(str(p) for p in tmp_path.rglob("*") if not str(p).startswith(str(out)))
    assert _build(f, out) == 0
    after = sorted(str(p) for p in tmp_path.rglob("*") if not str(p).startswith(str(out)))
    assert before == after
    assert (sibling / "x.md").read_text() == "keep"
    assert (f.root / "specs" / "a.md").read_text() == "# A\n\nText.\n"
