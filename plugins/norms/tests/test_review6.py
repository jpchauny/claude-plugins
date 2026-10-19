"""Regressions of the sixth review (fix round 6): one test or more per code defect.

Each case was reproduced before it was fixed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from norms_generator.store import Status, Store, StoreError, read_store
from norms_generator.tree import build_tree
from test_cli import Foundation, main
from test_store import by_id, parsed, run

# --- a column moved with its delimiter cell changes no hash -------------------


def _table(text: str):
    return build_tree(text.encode()).children[0]


@pytest.mark.parametrize(
    ("v1", "v2"),
    [
        ("| a | bb |\n|---|:---|\n| 1 | 22 |\n", "| bb | a |\n|:---|---|\n| 22 | 1 |\n"),
        ("| a | b |\n| ------- | --- |\n| 1 | 2 |\n", "| b | a |\n| --- | ------- |\n| 2 | 1 |\n"),
        ("> | a | b |\n> | :-: | --: |\n", "> | b | a |\n> | --: | :-: |\n"),
    ],
)
def test_moving_a_column_with_its_delimiter_cell_changes_no_hash_u5(v1: str, v2: str) -> None:
    """A column moved with its delimiter cell changes no hash.

    Spec: R13, R16, R31, U5 (E74)
    """
    old, new = _table(v1), _table(v2)
    assert old.own_text != new.own_text  # the own text keeps its exact bytes
    assert (old.own_hash, old.tree_hash) == (new.own_hash, new.tree_hash)


def test_a_column_moved_with_its_alignment_is_unchanged_u5() -> None:
    """A column moved with its alignment is unchanged.

    Spec: R13, R31, R59, U5 (E74)
    """
    v1 = parsed(a="| a | bb |\n|---|:---|\n| 1 | 22 |\n")
    s1, _ = run(v1, Store(), "c1")
    v2 = parsed(a="| bb | a |\n|:---|---|\n| 22 | 1 |\n")
    _, changes = run(v2, s1, "c2")
    assert {c.status for c in changes} == {Status.UNCHANGED}


def test_a_changed_alignment_still_edits_the_table_r59() -> None:
    """A changed delimiter cell edits the table.

    Spec: R13, R31, R59, U5
    """
    v1 = parsed(a="| a | b |\n|---|---|\n| 1 | 2 |\n")
    s1, _ = run(v1, Store(), "c1")
    v2 = parsed(a="| a | b |\n|:---|---|\n| 1 | 2 |\n")
    _, changes = run(v2, s1, "c2")
    table = v2["specs/a.md"].children[0]
    assert by_id(changes)[table.id].status is Status.EDITED


# --- copies rank among the free copies only -----------------------------------


def test_copies_keep_their_ids_when_a_block_holding_another_copy_moves_r54() -> None:
    """Copies rank only among the free copies of their text.

    Spec: R54 (E71)
    """
    v1 = parsed(a="> X\n>\n> Y\n\nX\n\nX\n")
    s1, _ = run(v1, Store(), "c1")
    first, second = (c.id for c in v1["specs/a.md"].children[1:])
    v2 = parsed(a="X\n\nX\n\n> X\n>\n> Y\n")
    _, changes = run(v2, s1, "c2")
    assert [c.id for c in v2["specs/a.md"].children[:2]] == [first, second]
    assert {c.status for c in changes} == {Status.UNCHANGED}


# --- a file replaced by a folder of its name, or the reverse -------------------


@pytest.mark.parametrize(
    ("before", "after"),
    [("specs/x.md/b.md", "specs/x.md"), ("specs/x.md", "specs/x.md/b.md")],
)
def test_a_file_and_a_folder_of_one_name_replace_each_other_r62(tmp_path: Path, before: str, after: str) -> None:
    """A file and a folder may take each other's name between versions.

    Spec: R34, R62, U6
    """
    f = Foundation(tmp_path / "foundation")
    out = tmp_path / "norms"
    f.write("specs/keep.md", "Keep.\n")
    f.write(before, "Before.\n")
    f.commit()
    assert main(["build", "--foundation", str(f.root), "--out", str(out)]) == 0
    f.git("rm", "-q", "-r", before)
    f.write(after, "After.\n")
    f.commit()
    assert main(["build", "--foundation", str(f.root), "--out", str(out)]) == 0
    assert (out / "annotated" / after).is_file()
    assert sorted(p.relative_to(out / "annotated").as_posix() for p in (out / "annotated").rglob("*.md") if p.is_file()) == sorted(["specs/keep.md", after])
    assert main(["verify", "--foundation", str(f.root), "--out", str(out)]) == 0


def test_verify_reports_a_folder_in_place_of_an_annotated_copy_r64(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A folder at a copy's path is a problem for verify, and build removes it.

    Spec: R34, R62, R64, U6
    """
    f = Foundation(tmp_path / "foundation")
    out = tmp_path / "norms"
    f.write("specs/x.md", "X.\n")
    f.commit()
    assert main(["build", "--foundation", str(f.root), "--out", str(out)]) == 0
    copy = out / "annotated" / "specs" / "x.md"
    copy.unlink()
    copy.mkdir()
    capsys.readouterr()
    assert main(["verify", "--foundation", str(f.root), "--out", str(out)]) == 1
    assert "no annotated file" in capsys.readouterr().err
    # and build clears the way
    assert main(["build", "--foundation", str(f.root), "--out", str(out)]) == 0
    assert copy.is_file()


# --- lines split at "\n" only; strings must be valid Unicode ------------------


def test_a_lone_cr_does_not_split_lines_r61(tmp_path: Path) -> None:
    """JSONL lines are split at `\n` only.

    Spec: R61
    """
    path = tmp_path / "t.jsonl"
    path.write_bytes(b'{"type":"meta","foundation_commit":"x"}\r{"type":"file","path":"a.md","prefix":"AAA"}\r')
    with pytest.raises(StoreError, match=r"t\.jsonl:1:"):
        read_store(path)


def test_a_cr_inside_a_line_is_json_whitespace_r61(tmp_path: Path) -> None:
    """A `\r` inside a line is JSON whitespace.

    Spec: R61
    """
    path = tmp_path / "t.jsonl"
    path.write_bytes(b'{"type":\r"meta","foundation_commit":"x"}\r\n')
    assert read_store(path).foundation_commit == "x"


def test_a_lone_surrogate_is_refused_and_the_jsonl_kept_r61(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A lone surrogate is not valid Unicode; build refuses it and keeps the JSONL.

    Spec: R34, R61, R64
    """
    f = Foundation(tmp_path / "foundation")
    out = tmp_path / "norms"
    f.write("specs/a.md", "A.\n")
    f.commit()
    assert main(["build", "--foundation", str(f.root), "--out", str(out)]) == 0
    path = out / "data" / "tree.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    lines.append(
        json.dumps(
            {
                "type": "node", "id": "SPA-9", "file": "specs/a.md", "kind": "paragraph", "start": 0, "end": 1,
                "own_text": "\ud800", "own_hash": "h", "tree_hash": "h", "status": "retired",
            }
        )
    )
    saved = "".join(line + "\n" for line in lines).encode("utf-8")
    path.write_bytes(saved)
    with pytest.raises(StoreError, match=r"tree\.jsonl:\d+: .*not valid Unicode"):
        read_store(path)
    capsys.readouterr()
    assert main(["build", "--foundation", str(f.root), "--out", str(out)]) == 2
    assert path.read_bytes() == saved
    assert main(["verify", "--foundation", str(f.root), "--out", str(out)]) == 1
    assert "not valid Unicode" in capsys.readouterr().err


# --- `report` prints the report's exact bytes ----------------------------------


def test_report_prints_crlf_as_it_is_r62(tmp_path: Path, capfdbinary: pytest.CaptureFixture[bytes]) -> None:
    """`report` prints the report's exact bytes.

    Spec: R62
    """
    f = Foundation(tmp_path / "foundation")
    out = tmp_path / "norms"
    f.write("specs/a.md", "# A\r\n\r\nabcdef\r\nghijkl\r\n")
    f.commit()
    assert main(["build", "--foundation", str(f.root), "--out", str(out)]) == 0
    f.write("specs/a.md", "# A\r\n\r\nabcdef\r\nghijkm\r\n")
    f.commit()
    assert main(["build", "--foundation", str(f.root), "--out", str(out)]) == 0
    report = (out / "data" / "report.md").read_bytes()
    assert b"\r" in report
    capfdbinary.readouterr()
    assert main(["report", "--out", str(out)]) == 0
    assert capfdbinary.readouterr().out == report
