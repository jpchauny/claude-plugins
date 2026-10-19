"""Regressions of the eighth review (fix round 8): one test or more per finding.

The code defects (a JSONL that cannot be opened crashing build and
verify, a symbolic link at an annotated copy's path written through, a
path holding a line break, the false reason given for two folders that
differ only in case) were reproduced before they were fixed. The other
tests pin behaviour the specs now state.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from norms_generator.cli import FoundationError, check_paths, main
from norms_generator.store import Store, StoreError, read_store
from test_cli import Foundation
from test_review5 import _add_blob
from test_store import parsed, run


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


# --- what the case/normalization refusal names --------------------------------


@pytest.mark.parametrize(
    ("paths", "named", "reason"),
    [
        (["specs/A.md", "specs/a.md"], "specs/A.md and specs/a.md", "would be one file and overwrite each other"),
        (["specs/X.md/b.md", "specs/x.md"], "specs/X.md and specs/x.md", "an annotated copy and a folder"),
        (["specs/A/x.md", "specs/a/y.md"], "specs/A and specs/a", "would share one folder"),
    ],
)
def test_the_case_refusal_names_the_two_names_and_a_true_reason_r34(
    paths: list[str], named: str, reason: str
) -> None:
    """The case refusal names the two names and gives a true reason.

    Spec: R34
    """
    with pytest.raises(FoundationError) as info:
        check_paths(paths)
    message = str(info.value)
    assert message.startswith(f"{named} differ only in case or Unicode normalization; ")
    assert reason in message
    assert "overwrite" not in message or reason.endswith("overwrite each other")


# --- a path holding a control character ---------------------------------------


@pytest.mark.parametrize("name", [b"specs/a\nb.md", b"specs/a\tb.md", b"specs/a\x7fb.md", "specs/a\u0085b.md".encode()])
def test_a_md_path_holding_a_control_character_is_refused_r34(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], name: bytes
) -> None:
    """A `.md` path holding a control character is refused.

    Spec: R34, R61
    """
    f = Foundation(tmp_path / "foundation")
    _add_blob(f, name, b"# A\n")
    f.git("commit", "-q", "-m", "c")
    out = tmp_path / "norms"
    assert _build(f, out) == 2
    err = capsys.readouterr().err
    assert err.endswith(": path holds a control character\n")
    assert err.count("\n") == 1  # one line: the character is written as \x..
    assert "\\x" in err
    assert not out.exists()


def test_a_stored_path_holding_a_control_character_has_not_the_form_r61(tmp_path: Path) -> None:
    """A stored path holding a control character has not the form of a path.

    Spec: R34, R61
    """
    p = tmp_path / "tree.jsonl"
    p.write_text(json.dumps({"type": "file", "path": "specs/a\nb.md", "prefix": "ABC"}) + "\n")
    with pytest.raises(StoreError, match=r"tree\.jsonl:1: ValueError: bad path"):
        read_store(p)


# --- a JSONL that cannot be opened --------------------------------------------


def test_a_folder_at_the_jsonl_path_is_refused_by_build_and_reported_by_verify_r34_r64(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A folder at the JSONL path is refused by build and reported by verify.

    Spec: R34, R64
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "# A\n")
    f.commit()
    out = tmp_path / "norms"
    (out / "data/tree.jsonl").mkdir(parents=True)
    assert _build(f, out) == 2
    err = capsys.readouterr().err
    assert err.startswith("norms-gen: ") and "tree.jsonl: cannot be opened: " in err
    assert _verify(f, out) == 1
    err = capsys.readouterr().err
    assert "tree.jsonl: cannot be opened: " in err and err.endswith("verify: 1 problems\n")


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads any file")
def test_a_jsonl_without_read_permission_is_refused_r34(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A JSONL without read permission is refused.

    Spec: R34, R64
    """
    f, out = _one_file(tmp_path)
    jsonl = out / "data/tree.jsonl"
    jsonl.chmod(0)
    try:
        assert _build(f, out) == 2
        assert "tree.jsonl: cannot be opened: " in capsys.readouterr().err
    finally:
        jsonl.chmod(0o644)


# --- a symbolic link at an annotated copy's path ------------------------------


def test_build_replaces_a_symbolic_link_at_a_copy_s_path_and_verify_reports_it_r62_r64(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Build replaces a symbolic link at a copy's path, and verify reports one.

    Spec: R62, R64
    """
    f, out = _one_file(tmp_path)
    copy = out / "annotated/specs/a.md"
    good = copy.read_bytes()
    victim = tmp_path / "victim.md"
    victim.write_text("old\n")
    copy.unlink()
    copy.symlink_to(victim)
    assert _verify(f, out) == 1
    assert "specs/a.md: no annotated file at " in capsys.readouterr().err
    assert _build(f, out) == 0
    assert victim.read_text() == "old\n"
    assert not copy.is_symlink() and copy.read_bytes() == good
    assert _verify(f, out) == 0


def test_verify_reports_a_copy_reached_through_a_linked_folder_r64(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify reports a copy reached through a linked folder.

    Spec: R62, R64
    """
    f, out = _one_file(tmp_path)
    folder = out / "annotated/specs"
    elsewhere = tmp_path / "elsewhere"
    folder.rename(elsewhere)
    folder.symlink_to(elsewhere)
    assert _verify(f, out) == 1
    assert "specs/a.md: no annotated file at " in capsys.readouterr().err
    assert _build(f, out) == 0
    assert not folder.is_symlink()
    assert _verify(f, out) == 0


# --- a name repeated in one object ---------------------------------------------


def test_a_repeated_name_keeps_its_last_value_and_the_earlier_is_not_checked_r61(tmp_path: Path) -> None:
    """A name repeated in one object keeps its last value; the earlier one is not checked.

    Spec: R61
    """
    p = tmp_path / "tree.jsonl"
    p.write_text('{"path":"../../../x.md","path":"specs/a.md","prefix":"SPA","type":"file"}\n')
    assert sorted(read_store(p).files) == ["specs/a.md"]


# --- a path present in both that is not a candidate keeps its prefix ------------


def test_a_path_emptied_or_filled_in_keeps_its_prefix_r58() -> None:
    """A path present in both that is not a candidate, emptied or filled in, keeps its prefix.

    Spec: R58
    """
    v1 = parsed(other="# Other\n\nText.\n", memory="")
    store1, _ = run(v1, Store(), "c1")
    v2 = parsed(other="", memory="# Memory\n\nAll new.\n")
    store2, _ = run(v2, store1, "c2")
    assert {p: s.prefix for p, s in store2.files.items()} == {p: s.prefix for p, s in store1.files.items()}
    assert store2.retired_prefix_list == []
