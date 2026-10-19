"""Regressions of the tenth review (the round-8 findings): one test or more per finding.

The code defects (verify and report crashing on a folder they cannot
search, build crashing half way on an output it cannot read or write)
were reproduced before they were fixed. The other tests pin what the
specs now word exactly.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from norms_generator.cli import main
from test_cli import Foundation

needs_permissions = pytest.mark.skipif(os.geteuid() == 0, reason="root reads and searches anything")


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


# --- an annotated folder verify cannot search ---------------------------------


@needs_permissions
def test_verify_reports_a_copy_under_a_folder_it_cannot_search_r64(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify reports a copy under a folder it cannot search, and the folder whose names it cannot read.

    Spec: R64, U6
    """
    f, out = _one_file(tmp_path)
    folder = out / "annotated" / "specs"
    folder.chmod(0)
    try:
        capsys.readouterr()
        assert _verify(f, out) == 1
        err = capsys.readouterr().err
        copy = folder / "a.md"
        assert err == (
            f"specs/a.md: annotated file at {copy} cannot be opened: Permission denied\n"
            f"{folder}: cannot be opened: Permission denied\nverify: 2 problems\n"
        )
    finally:
        folder.chmod(0o755)


# --- report under a data/ it cannot search; a broken link at a report ---------


@needs_permissions
def test_report_under_a_folder_it_cannot_search_cannot_be_opened_r62(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Report under a data/ it cannot search says it cannot be opened.

    Spec: R62
    """
    _, out = _one_file(tmp_path)
    data = out / "data"
    data.chmod(0)
    try:
        capsys.readouterr()
        assert main(["report", "--out", str(out)]) == 1
        assert capsys.readouterr().err == f"{data / 'report.md'}: cannot be opened: Permission denied\n"
    finally:
        data.chmod(0o755)


def test_report_at_a_broken_link_cannot_be_opened_r62(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Report at a broken link says it cannot be opened.

    Spec: R62
    """
    _, out = _one_file(tmp_path)
    report = out / "data" / "report.md"
    report.unlink()
    report.symlink_to("nowhere")
    capsys.readouterr()
    assert main(["report", "--out", str(out)]) == 1
    assert capsys.readouterr().err == f"{report}: cannot be opened: No such file or directory\n"


def test_report_at_a_looping_link_cannot_be_opened_r62(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Report at a looping link says it cannot be opened.

    Spec: R62
    """
    _, out = _one_file(tmp_path)
    report = out / "data" / "report.md"
    report.unlink()
    report.symlink_to("report.md")
    capsys.readouterr()
    assert main(["report", "--out", str(out)]) == 1
    assert capsys.readouterr().err == f"{report}: cannot be opened: Too many levels of symbolic links\n"


def test_report_absent_says_no_report_r62(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """With no report, report says there is none.

    Spec: R62
    """
    _, out = _one_file(tmp_path)
    (out / "data" / "report.json").unlink()
    capsys.readouterr()
    assert main(["report", "--out", str(out), "--json"]) == 1
    err = capsys.readouterr().err
    assert err == f"no report at {out / 'data' / 'report.json'}; run `norms-gen build` first\n"


def test_verify_takes_a_broken_data_link_as_no_jsonl_r64(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Under a data/ link that leads nowhere, the JSONL is absent: no JSONL.

    Spec: R62, R64
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "# A\n")
    f.commit()
    out = tmp_path / "norms"
    out.mkdir()
    (out / "data").symlink_to(tmp_path / "nonexistent")
    capsys.readouterr()
    assert _verify(f, out) == 1
    err = capsys.readouterr().err
    assert err == f"{out / 'data' / 'tree.jsonl'}: no JSONL; run `norms-gen build` first\nverify: 1 problems\n"


# --- build on an output it cannot read or write -------------------------------


@needs_permissions
def test_build_writes_over_a_report_it_cannot_read_r62(tmp_path: Path) -> None:
    """An existing output build cannot read but can write is written over.

    Spec: R60, R62
    """
    f, out = _one_file(tmp_path)
    report = out / "data" / "report.md"
    report.chmod(0o200)  # write only
    (out / "data" / "report.json").unlink()
    try:
        assert _build(f, out) == 0
    finally:
        report.chmod(0o644)
    assert report.read_bytes().startswith(b"# Changes\n")  # written again, of this rebuild
    assert (out / "data" / "report.json").exists()


@needs_permissions
def test_build_stops_with_a_message_in_a_data_folder_it_cannot_write_r62(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Build stops with a message on the JSONL's .tmp in a data/ it cannot write; fixed, it finishes.

    Spec: R62
    """
    f, out = _one_file(tmp_path)
    data = out / "data"
    before = (data / "tree.jsonl").read_bytes()
    data.chmod(0o555)  # read and search, no write
    try:
        capsys.readouterr()
        assert _build(f, out) == 3  # stopped part way
        err = capsys.readouterr().err
        assert err == f"norms-gen: {data / 'tree.jsonl.tmp'}: cannot be written: Permission denied\n"
        assert (data / "tree.jsonl").read_bytes() == before  # the previous JSONL, never a truncated one
    finally:
        data.chmod(0o755)
    assert _build(f, out) == 0
    assert _verify(f, out) == 0


@needs_permissions
def test_build_replaces_a_report_without_write_permission_r62(tmp_path: Path) -> None:
    """A report without write permission is replaced by a new file, never written into.

    Spec: R62
    """
    f, out = _one_file(tmp_path)
    report = out / "data" / "report.md"
    report.chmod(0)
    (out / "data" / "report.json").unlink()
    assert _build(f, out) == 0
    assert report.read_bytes().startswith(b"# Changes\n")


@needs_permissions
def test_build_stops_with_a_message_under_a_folder_it_cannot_search_r62(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Build stops with a message, naming the folder under annotated/ it cannot search.

    Spec: R62, U6
    """
    f, out = _one_file(tmp_path)
    folder = out / "annotated" / "specs"
    folder.chmod(0)
    try:
        capsys.readouterr()
        assert _build(f, out) == 3  # stopped part way
        err = capsys.readouterr().err
        assert err == f"norms-gen: {folder}: cannot be written: Permission denied\n"  # read before writing
    finally:
        folder.chmod(0o755)
    assert _build(f, out) == 0
    assert _verify(f, out) == 0


# --- a file at data/ is a JSONL that cannot be opened --------------------------


def test_a_file_at_data_is_a_jsonl_that_cannot_be_opened_r34(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A file at data/ is a JSONL that cannot be opened.

    Spec: R34
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "# A\n")
    f.commit()
    out = tmp_path / "norms"
    out.mkdir()
    (out / "data").write_text("x")
    capsys.readouterr()
    assert _build(f, out) == 2
    err = capsys.readouterr().err
    assert err == f"norms-gen: {out / 'data' / 'tree.jsonl'}: cannot be opened: Not a directory\n"


# --- a rebuild needs a file line in the previous JSONL -------------------------


def test_a_jsonl_without_file_lines_gives_no_rebuild_r60(tmp_path: Path) -> None:
    """A rebuild needs a file line in the previous JSONL.

    Spec: R60
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "# A\n")
    f.commit()
    sha = subprocess.run(
        ["git", "-C", str(f.root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    out = tmp_path / "norms"
    (out / "data").mkdir(parents=True)
    meta = {"foundation_commit": sha, "generator_version": "0.1.0", "retired_prefixes": ["XYZ"], "type": "meta"}
    node = {
        "changed_since": "deadbeef", "end": 0, "file": "specs/old.md", "id": "XYZ-1", "kind": "paragraph",
        "own_hash": "", "own_text": "", "parent": "XYZ", "start": 0, "status": "retired", "to_review": False,
        "tree_hash": "", "type": "node",
    }  # fmt: skip
    lines = [json.dumps(o, sort_keys=True, separators=(",", ":")) for o in (meta, node)]
    (out / "data" / "tree.jsonl").write_text("\n".join(lines) + "\n")
    assert _build(f, out) == 0
    stored = [json.loads(line) for line in (out / "data" / "tree.jsonl").read_text().splitlines()]
    retired = [o for o in stored if o.get("id") == "XYZ-1"]
    assert retired and retired[0]["changed_since"] is None


# --- the not-in-foundation problem holds the git command --------------------------


def test_not_in_foundation_is_worded_as_r34_words_git_r64(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The not-in-foundation problem holds the git command, worded as a refusal words git's.

    Spec: R34, R64
    """
    f, out = _one_file(tmp_path)
    store = out / "data" / "tree.jsonl"
    store.write_text(store.read_text().replace('"specs/a.md"', '"specs/b.md"'))
    sha = json.loads(store.read_text().splitlines()[0])["foundation_commit"]
    capsys.readouterr()
    assert _verify(f, out) == 1
    err = capsys.readouterr().err
    assert (
        f"specs/b.md: not in foundation at {sha}: git cat-file blob {sha}:specs/b.md: "
        f"fatal: path 'specs/b.md' does not exist in '{sha}'\n"
    ) in err


# --- the refusal messages worded exactly --------------------------------------------


def test_refusal_messages_are_worded_as_r34_says(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A refusal is worded exactly as the spec words it: no .md file under the folder.

    Spec: R34
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "# A\n")
    f.commit()
    out = tmp_path / "norms"
    capsys.readouterr()
    assert main(["build", "--foundation", str(f.root), "--out", str(out), "--specs-dir", "nope"]) == 2
    sha = subprocess.run(
        ["git", "-C", str(f.root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert capsys.readouterr().err == f"norms-gen: no .md file under 'nope' at {sha}; is --specs-dir right?\n"

    (f.root / "specs" / "a.md").write_bytes(b"# A\xff\n")
    f.commit()
    assert _build(f, out) == 2
    assert capsys.readouterr().err == (
        "norms-gen: specs/a.md: not UTF-8 (byte 0xff at offset 3); foundation files must be UTF-8 (R34)\n"
    )

    f.write("specs/a.md", "# A ⟭\n")
    f.commit()
    assert _build(f, out) == 2
    assert capsys.readouterr().err == (
        "norms-gen: specs/a.md: holds the delimiter ⟭ at offset 4; foundation never holds ⟬ or ⟭ (R19, R34)\n"
    )

    f.write("specs/a.md", "# A\n")
    f.commit()
    store = out / "data" / "tree.jsonl"
    store.parent.mkdir(parents=True)
    store.write_text("nope\n")
    assert _build(f, out) == 2
    assert capsys.readouterr().err == (
        f"norms-gen: {store}:1: JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n"
    )
    store.write_bytes(b"{}\xff\n")
    assert _build(f, out) == 2
    assert capsys.readouterr().err == (
        f"norms-gen: {store}: not UTF-8: 'utf-8' codec can't decode byte 0xff in position 2: invalid start byte\n"
    )
