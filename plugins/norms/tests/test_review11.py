"""Regressions of the eleventh review: one test or more per finding.

Each defect was reproduced before it was fixed: a build that wrote
through a hard link outside the output folder, a JSONL line or an
annotated copy nested too deeply that gave status 4, a foreign name with
a line break that split verify's problem in two, a closed pipe reported
as an unexpected error, and verify calling a symbolic link at annotated/
sound.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from norms_generator.cli import main
from test_cli import Foundation


def _build(f: Foundation, out: Path) -> int:
    return main(["build", "--foundation", str(f.root), "--out", str(out)])


def _verify(f: Foundation, out: Path) -> int:
    return main(["verify", "--foundation", str(f.root), "--out", str(out)])


def _built(tmp_path: Path) -> tuple[Foundation, Path]:
    """A foundation of `specs/a.md` and `specs/sub/b.md`, built once."""
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "# A\n\nText.\n")
    f.write("specs/sub/b.md", "# B\n")
    f.commit()
    out = tmp_path / "norms"
    assert _build(f, out) == 0
    return f, out


def _hard_link(path: Path, target: Path) -> None:
    """Put a hard link to `target` at `path`, in place of what stands there."""
    if os.path.lexists(path):
        path.unlink()
    os.link(target, path)


# --- hard links at the output paths -------------------------------------------


def test_build_never_writes_through_a_hard_link_at_an_output_path_r62(tmp_path: Path) -> None:
    """A hard link at a copy, a report or the JSONL's .tmp is replaced; the file outside keeps its bytes.

    Spec: R62, U6
    """
    f, out = _built(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    outputs = [
        out / "annotated" / "specs" / "a.md",
        out / "data" / "report.md",
        out / "data" / "report.json",
        out / "data" / "tree.jsonl.tmp",
    ]
    outside = []
    for n, path in enumerate(outputs):
        victim = home / f"h{n}"
        victim.write_bytes(f"SECRET{n}".encode())
        _hard_link(path, victim)
        outside.append(victim)
    f.write("specs/a.md", "# A\n\nText, edited.\n")  # a new commit: every output is written
    f.commit()
    assert _build(f, out) == 0
    for n, victim in enumerate(outside):
        assert victim.read_bytes() == f"SECRET{n}".encode()
        assert os.stat(victim).st_nlink == 1
    for path in outputs[:3]:
        assert os.stat(path).st_nlink == 1
    assert not os.path.lexists(outputs[3])  # moved over tree.jsonl
    assert os.stat(out / "data" / "tree.jsonl").st_nlink == 1
    assert _verify(f, out) == 0


def test_build_never_writes_into_foundation_s_working_tree_through_a_hard_link_r62(tmp_path: Path) -> None:
    """A copy hard-linked to foundation's own working-tree file: foundation stays clean.

    Spec: R62, U6
    """
    f, out = _built(tmp_path)
    copy = out / "annotated" / "specs" / "sub" / "b.md"
    _hard_link(copy, f.root / "specs" / "sub" / "b.md")
    assert _build(f, out) == 0  # a rebuild of the same commit
    assert f.git("status", "--porcelain") == ""
    assert (f.root / "specs" / "sub" / "b.md").read_bytes() == b"# B\n"
    assert os.stat(copy).st_nlink == 1
    assert _verify(f, out) == 0


def test_a_rebuild_replaces_a_hard_linked_copy_that_holds_the_right_bytes_r62(tmp_path: Path) -> None:
    """A copy with the right bytes but two links is written anew: it no longer shares its bytes.

    Spec: R62, U6
    """
    f, out = _built(tmp_path)
    copy = out / "annotated" / "specs" / "a.md"
    twin = tmp_path / "twin"
    os.link(copy, twin)
    assert _build(f, out) == 0
    assert os.stat(copy).st_nlink == 1 and os.stat(twin).st_nlink == 1
    assert copy.read_bytes() == twin.read_bytes()


def test_a_rebuild_keeps_its_reports_only_as_files_of_their_own_r63(tmp_path: Path) -> None:
    """A rebuild that changed nothing writes its reports again when one of them is a hard link.

    Spec: R60, R62, R63
    """
    f, out = _built(tmp_path)
    report = out / "data" / "report.md"
    os.link(report, tmp_path / "twin")
    assert _build(f, out) == 0
    assert os.stat(report).st_nlink == 1
    assert report.read_bytes().startswith(b"# Changes\n")


def test_verify_reports_a_hard_linked_copy_r64(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verify names a copy with more than one link; build writes it anew.

    Spec: R64, U6
    """
    f, out = _built(tmp_path)
    copy = out / "annotated" / "specs" / "a.md"
    os.link(copy, tmp_path / "twin")
    capsys.readouterr()
    assert _verify(f, out) == 1
    assert capsys.readouterr().err == (
        f"specs/a.md: annotated file at {copy} has 2 links; build writes it anew (U6)\nverify: 1 problems\n"
    )
    assert _build(f, out) == 0
    assert _verify(f, out) == 0


# --- nested too deeply ----------------------------------------------------------


DEEP_LINE = "[" * 100000 + "]" * 100000 + "\n"
DEEP_MESSAGE = "RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string"


def test_build_refuses_a_jsonl_line_nested_too_deeply_r34(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A JSONL line nested deeper than the reader goes cannot be read: status 2, file and line named.

    Spec: R34, R61
    """
    f, out = _built(tmp_path)
    jsonl = out / "data" / "tree.jsonl"
    jsonl.write_text(DEEP_LINE, encoding="utf-8")
    capsys.readouterr()
    assert _build(f, out) == 2
    assert capsys.readouterr().err == f"norms-gen: {jsonl}:1: {DEEP_MESSAGE}\n"
    assert jsonl.read_text(encoding="utf-8") == DEEP_LINE  # nothing written


def test_verify_reports_a_jsonl_line_nested_too_deeply_r64(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verify reports a JSONL line nested too deeply as a JSONL it cannot read: status 1.

    Spec: R61, R64
    """
    f, out = _built(tmp_path)
    jsonl = out / "data" / "tree.jsonl"
    jsonl.write_text(DEEP_LINE, encoding="utf-8")
    capsys.readouterr()
    assert _verify(f, out) == 1
    assert capsys.readouterr().err == f"cannot read the JSONL: {jsonl}:1: {DEEP_MESSAGE}\nverify: 1 problems\n"


def test_verify_reports_the_problems_of_a_copy_nested_too_deeply_r64(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An annotated copy nested deeper than the parser follows has problems, reported with status 1.

    Spec: R64
    """
    f, out = _built(tmp_path)
    copy = out / "annotated" / "specs" / "a.md"
    copy.write_bytes(copy.read_bytes() + b">" * 20000 + b" x\n")
    capsys.readouterr()
    assert _verify(f, out) == 1
    err = capsys.readouterr().err
    assert "unexpected error" not in err
    assert "specs/a.md: stripping the insertions does not give back foundation\n" in err
    assert "specs/a.md: the annotated file does not parse to foundation's blocks\n" in err
    assert "specs/sub/b.md" not in err  # the other file is checked, and sound


# --- a foreign name with a line break -------------------------------------------


def test_verify_writes_a_foreign_name_with_a_line_break_on_one_line_r64(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A foreign name holding a line break is named with it escaped, so its problem takes one line.

    Spec: R34, R62, R64, U6
    """
    f, out = _built(tmp_path)
    ann = out / "annotated"
    (ann / "a\nb.md").write_bytes(b"")
    capsys.readouterr()
    assert _verify(f, out) == 1
    assert capsys.readouterr().err == (
        f"{ann}/a\\x0ab.md: not an annotated copy of a JSONL file; build removes it (U6)\nverify: 1 problems\n"
    )
    assert _build(f, out) == 0
    assert not os.path.lexists(ann / "a\nb.md")


# --- a closed standard output ---------------------------------------------------


def test_a_closed_standard_output_is_no_error_r62(tmp_path: Path) -> None:
    """`report | head`: the reader stops, report exits 0 with nothing on standard error.

    Spec: R62
    """
    f, out = _built(tmp_path)
    (out / "data" / "report.md").write_bytes(b"# Changes\n" + b"x" * 3_000_000 + b"\n")
    proc = subprocess.Popen(
        [sys.executable, "-m", "norms_generator.cli", "report", "--out", str(out)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.stdout is not None and proc.stderr is not None
    assert proc.stdout.read(10) == b"# Changes\n"
    proc.stdout.close()
    err = proc.stderr.read()
    assert proc.wait(timeout=60) == 0
    assert err == b""


# --- annotated/ itself a link or a file -----------------------------------------


def test_verify_reports_a_symbolic_link_at_annotated_r64(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A link at annotated/ is never followed: each copy is missing, and the link is named as build refuses it.

    Spec: R34, R64, U6
    """
    f, out = _built(tmp_path)
    ann = out / "annotated"
    ann.rename(tmp_path / "real")
    ann.symlink_to(tmp_path / "real")
    capsys.readouterr()
    assert _verify(f, out) == 1
    assert capsys.readouterr().err == (
        f"specs/a.md: no annotated file at {ann / 'specs' / 'a.md'}\n"
        f"specs/sub/b.md: no annotated file at {ann / 'specs' / 'sub' / 'b.md'}\n"
        f"{ann}: a symbolic link; a build never writes outside the output folder through a link\n"
        "verify: 3 problems\n"
    )
    assert _build(f, out) == 2  # build refuses it


def test_verify_reports_a_file_at_annotated_r64(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A file at annotated/ is named as build refuses it, after each missing copy.

    Spec: R34, R64, U6
    """
    f, out = _built(tmp_path)
    ann = out / "annotated"
    ann.rename(tmp_path / "real")
    ann.write_bytes(b"")
    capsys.readouterr()
    assert _verify(f, out) == 1
    assert capsys.readouterr().err == (
        f"specs/a.md: no annotated file at {ann / 'specs' / 'a.md'}\n"
        f"specs/sub/b.md: no annotated file at {ann / 'specs' / 'sub' / 'b.md'}\n"
        f"{ann}: not a folder\n"
        "verify: 3 problems\n"
    )
