"""Regressions of the ninth review (the round-7 findings): one test or more per finding.

The code defects (a path both not UTF-8 and holding a line break named
with the raw line break, a broken link at the JSONL taken as a first
run, output paths of the wrong type crashing build or written through
as links, the removal of a vanished copy followed through a link, a
folder at a report crashing `report`, an unreadable annotated copy
crashing verify) were reproduced before they were fixed.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from norms_generator.cli import main
from test_cli import Foundation
from test_review5 import _add_blob


def _build(f: Foundation, out: Path) -> int:
    return main(["build", "--foundation", str(f.root), "--out", str(out)])


def _verify(f: Foundation, out: Path) -> int:
    return main(["verify", "--foundation", str(f.root), "--out", str(out)])


def _one_file(tmp_path: Path) -> tuple[Foundation, Path]:
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "# A\n\nText.\n")
    f.commit()
    out = tmp_path / "norms"
    assert _build(f, out) == 0
    return f, out


def _snapshot(root: Path) -> dict[str, bytes | str]:
    """Every entry under `root`, links as their targets, without following them."""
    seen: dict[str, bytes | str] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            p = Path(dirpath) / name
            rel = str(p.relative_to(root))
            if p.is_symlink():
                seen[rel] = "-> " + os.readlink(p)
            elif p.is_file():
                seen[rel] = p.read_bytes()
            else:
                seen[rel] = "dir"
    return seen


# --- a path not UTF-8 that also holds a control character ---------------------


def test_a_path_not_utf8_with_a_line_break_is_named_on_one_line_r34(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A path not UTF-8 that also holds a line break is named on one line.

    Spec: R34
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "# A\n\nx\n")
    f.git("add", "-A")
    _add_blob(f, b"specs/a\xff\nb.md", b"y\n")
    f.git("commit", "-q", "-m", "c")
    out = tmp_path / "norms"
    assert _build(f, out) == 2
    err = capsys.readouterr().err
    assert err == "norms-gen: specs/a\\xff\\x0ab.md: path not UTF-8\n"
    assert not out.exists()


# --- a JSONL that is a broken link cannot be opened ---------------------------


@pytest.mark.parametrize("target", ["/nonexistent/zz", "tree.jsonl"])
def test_a_broken_link_at_the_jsonl_is_refused_not_a_first_run_r34(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], target: str
) -> None:
    """A broken link at the JSONL cannot be opened: it is refused, not a first run.

    Spec: R34, R64
    """
    f, out = _one_file(tmp_path)
    store = out / "data" / "tree.jsonl"
    store.unlink()
    store.symlink_to(target)
    before = _snapshot(out)
    capsys.readouterr()
    assert _build(f, out) == 2
    assert f"{store}: cannot be opened: " in capsys.readouterr().err
    assert _snapshot(out) == before
    assert _verify(f, out) == 1
    assert "cannot read the JSONL: " in capsys.readouterr().err


def test_a_file_at_data_is_refused_not_a_first_run_r34(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A file at data/ is refused, not taken for a first run.

    Spec: R34, R64
    """
    f, out = _one_file(tmp_path)
    data = out / "data"
    for p in data.iterdir():
        p.unlink()
    data.rmdir()
    data.write_text("x")
    before = _snapshot(out)
    capsys.readouterr()
    assert _build(f, out) == 2
    assert f"{data / 'tree.jsonl'}: cannot be opened: Not a directory" in capsys.readouterr().err
    assert _snapshot(out) == before


# --- output paths in the way are refused, before anything is written


def _make(path: Path, what: str, elsewhere: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        for p in sorted(path.rglob("*"), reverse=True):
            p.rmdir() if p.is_dir() and not p.is_symlink() else p.unlink()
        path.rmdir()
    if what == "file":
        path.write_text("x")
    elif what == "folder":
        path.mkdir()
    else:
        elsewhere.mkdir(exist_ok=True)
        path.symlink_to(elsewhere / path.name)
        if what == "link to a folder":
            (elsewhere / path.name).mkdir()


@pytest.mark.parametrize(
    ("rel", "what", "message"),
    [
        ("specs-repo-annotated", "file", "not a folder"),
        ("specs-repo-annotated", "link to a folder", "a symbolic link"),
        ("data/report.md", "folder", "a folder"),
        ("data/report.json", "folder", "a folder"),
        ("data/report.md", "link", "a symbolic link"),
        ("data/report.json", "link", "a symbolic link"),
        ("data/tree.jsonl.tmp", "link", "a symbolic link"),
        ("data/tree.jsonl.tmp", "folder", "a folder"),
    ],
)
def test_an_output_path_in_the_way_is_refused_and_nothing_written_r62(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], rel: str, what: str, message: str
) -> None:
    """An output path in the way is refused, and nothing is written.

    Spec: R34, R62
    """
    f, out = _one_file(tmp_path)
    f.write("specs/a.md", "# A\n\nOther text.\n")
    f.write("specs/b.md", "# B\n")
    f.commit()
    elsewhere = tmp_path / "elsewhere"
    _make(out / rel, what, elsewhere)
    before = _snapshot(out)
    capsys.readouterr()
    assert _build(f, out) == 2
    assert capsys.readouterr().err == f"norms-gen: {out / rel}: {message}" + (
        "; a build never writes outside the output folder through a link\n" if "link" in message else "\n"
    )
    assert _snapshot(out) == before
    assert not elsewhere.exists() or not any(p.is_file() for p in elsewhere.rglob("*"))


def test_a_link_at_data_is_refused_r62(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A link at data/ is refused.

    Spec: R34, R62
    """
    f, out = _one_file(tmp_path)
    elsewhere = tmp_path / "elsewhere"
    (out / "data").rename(elsewhere)
    (out / "data").symlink_to(elsewhere)
    before = _snapshot(elsewhere)
    capsys.readouterr()
    assert _build(f, out) == 2
    assert f"{out / 'data'}: a symbolic link" in capsys.readouterr().err
    assert _snapshot(elsewhere) == before


def test_a_rebuild_with_a_folder_at_a_report_is_refused_r60(tmp_path: Path) -> None:
    """A folder at a report is refused, also on a rebuild that would keep the reports.

    Spec: R34, R60, R62
    """
    f, out = _one_file(tmp_path)
    (out / "data" / "report.md").unlink()
    (out / "data" / "report.md").mkdir()
    assert _build(f, out) == 2


# --- removing a vanished copy never goes through a link -----------------------


def test_removing_a_vanished_copy_does_not_follow_a_link_inside_annotated_r62(tmp_path: Path) -> None:
    """A link at a vanished copy's folder is removed itself, and the file it led to, no copy, too.

    Spec: R62, U6
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/old/c.md", "# C\n")
    f.write("specs/b.md", "# B\n")
    f.commit()
    out = tmp_path / "norms"
    assert _build(f, out) == 0
    ann = out / "specs-repo-annotated" / "specs"
    (ann / "new").mkdir()
    (ann / "old" / "c.md").rename(ann / "new" / "c.md")
    (ann / "old").rmdir()
    (ann / "old").symlink_to("new")
    kept = (ann / "new" / "c.md").read_bytes()
    (f.root / "specs" / "old" / "c.md").unlink()
    f.commit()
    assert _build(f, out) == 0
    assert not (ann / "old").is_symlink() and not (ann / "old").exists()
    assert kept and not (ann / "new").exists()  # no copy: removed with its folder
    assert _verify(f, out) == 0


def test_removing_a_vanished_copy_removes_a_link_at_its_path_only_r62(tmp_path: Path) -> None:
    """Removing a vanished copy removes a link at its path, never what it leads to.

    Spec: R62
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/x/c.md", "# C\n")
    f.write("specs/b.md", "# B\n")
    f.commit()
    out = tmp_path / "norms"
    assert _build(f, out) == 0
    outside = tmp_path / "outside.md"
    outside.write_text("keep")
    copy = out / "specs-repo-annotated" / "specs" / "x" / "c.md"
    copy.unlink()
    copy.symlink_to(outside)
    (f.root / "specs" / "x" / "c.md").unlink()
    f.commit()
    assert _build(f, out) == 0
    assert outside.read_text() == "keep"
    assert not (out / "specs-repo-annotated" / "specs" / "x").exists()


# --- report on a folder; verify on an unreadable copy ---------------------------


def test_report_on_a_folder_says_it_cannot_be_opened_r62(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Report on a folder says it cannot be opened.

    Spec: R62, R64
    """
    _, out = _one_file(tmp_path)
    (out / "data" / "report.md").unlink()
    (out / "data" / "report.md").mkdir()
    capsys.readouterr()
    assert main(["report", "--out", str(out)]) == 1
    assert capsys.readouterr().err == f"{out / 'data' / 'report.md'}: cannot be opened: Is a directory\n"


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads any file")
def test_verify_reports_an_annotated_copy_it_cannot_read_r64(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify reports an annotated copy it cannot read.

    Spec: R62, R64
    """
    f, out = _one_file(tmp_path)
    copy = out / "specs-repo-annotated" / "specs" / "a.md"
    copy.chmod(0)
    try:
        capsys.readouterr()
        assert _verify(f, out) == 1
        err = capsys.readouterr().err
        assert f"specs/a.md: annotated file at {copy} cannot be opened: Permission denied\n" in err
    finally:
        copy.chmod(0o644)
