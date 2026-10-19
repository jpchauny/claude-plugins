"""Regressions of the fifth review (fix round 5): one test or more per code defect.

Each case was reproduced before it was fixed.
"""

from __future__ import annotations

import subprocess
from itertools import islice
from pathlib import Path

import pytest

from norms_generator.model import Kind
from norms_generator.prefixes import candidates
from norms_generator.store import Store, StoreError, _SimilarPairs, read_store
from test_cli import Foundation, main
from test_review4 import _built, _edit_jsonl
from test_store import parsed, run, text_ids


# --- the same-file bonus is exact ---------------------------------------------


def test_same_file_pair_wins_a_tie_with_a_pair_across_files_r55() -> None:
    """The same-file bonus is exact, so a same-file pair wins its tie.

    Note: D27c

    Spec: R55
    """
    # ratio 0.7 in the same file ranks as 0.8, so it ties with 0.8 across files
    # and wins the tie; in floats 0.7 + 0.1 < 0.8
    pairs = _SimilarPairs(
        [(Kind.PARAGRAPH, "abcdefghij", "SPA")],
        [(Kind.PARAGRAPH, "abcdefgXYZ", "SPA"), (Kind.PARAGRAPH, "abcdefghXY", "SPB")],
    )
    n, o, ratio = next(pairs.best_first(lambda n, o: (0 if o == 0 else 1 << 62,)))
    assert (n, o) == (0, 0) and ratio == pytest.approx(0.7)


def test_same_file_tie_keeps_the_id_of_the_same_file_r55() -> None:
    """At a tie, the node of the same file keeps the ID.

    Spec: R55
    """
    v1 = parsed(a="abcdefgXYZ\n", b="abcdefghXY\n")
    s1, _ = run(v1, Store(), "c1")
    old = text_ids(v1)
    v2 = parsed(a="abcdefghij\n")
    run(v2, s1, "c2")
    assert text_ids(v2)[("specs/a.md", "abcdefghij")] == old[("specs/a.md", "abcdefgXYZ")]


# --- childless containers pair in order among their copies --------------------


def test_text_inserted_above_childless_quotes_does_not_swap_their_ids_r56() -> None:
    """Childless quotes pair in order among their free copies.

    Spec: R54, R56
    """
    v1 = "> ***\n\n>\n\n> ***\n"
    t1 = parsed(typ=v1)
    s1, _ = run(t1, Store(), "c1")
    first = [c.id for c in t1["specs/typ.md"].children]
    t2 = parsed(typ="P" * 48 + "\n\n" + v1)
    run(t2, s1, "c2")
    assert [c.id for c in t2["specs/typ.md"].children][1:] == first


# --- prefix letters -----------------------------------------------------------


def test_a_file_named_dot_md_has_an_empty_name_r10() -> None:
    """`.md` has an empty name and takes the counter, as `1.md` does.

    Spec: R10
    """
    assert list(islice(candidates("specs/.md"), 2)) == list(islice(candidates("specs/1.md"), 2)) == ["SPEA", "SPEB"]


@pytest.mark.parametrize(("path", "first"), [("specs/ßeta.md", "ETA"), ("specs/ﬁle.md", "SLE"), ("specs/ıtem.md", "TEM")])
def test_only_ascii_letters_count_before_upper_casing_r10(path: str, first: str) -> None:
    """Only ASCII letters count, before upper-casing.

    Spec: R10
    """
    assert next(candidates(path)) == first


# --- a prefix or ID ending in a line break is malformed -----------------------


@pytest.mark.parametrize(
    "edit",
    [
        lambda o: dict(o, prefix=o["prefix"] + "\n") if o["type"] == "file" else o,
        lambda o: dict(o, id=o["id"] + "\n") if o["type"] == "node" and o["kind"] == "paragraph" else o,
    ],
)
def test_a_prefix_or_id_with_a_final_line_break_is_refused_r61(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], edit
) -> None:
    """A prefix or an ID followed by a line break does not have the form.

    Spec: R34, R61
    """
    f, out = _built(tmp_path)
    _edit_jsonl(out, lambda lines: [edit(o) for o in lines])
    with pytest.raises(StoreError):
        read_store(out / "data" / "tree.jsonl")
    assert main(["build", "--foundation", str(f.root), "--out", str(out)]) == 2
    assert "tree.jsonl:" in capsys.readouterr().err


# --- a .md path that is not UTF-8 is refused ----------------------------------


def _add_blob(f: Foundation, path: bytes, data: bytes) -> None:
    sha = subprocess.run(
        ["git", "-C", str(f.root), "hash-object", "-w", "--stdin"], input=data, capture_output=True, check=True
    ).stdout.strip()
    subprocess.run(
        ["git", "-C", str(f.root), "update-index", "--add", "--cacheinfo", b"100644," + sha + b"," + path],
        check=True,
    )


def test_a_md_path_not_utf8_is_refused_naming_it_r34(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A .md path that is not UTF-8 is refused, naming it.

    Spec: R34
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "# A\n\nx\n")
    f.git("add", "-A")
    _add_blob(f, b"specs/x\xff.md", b"y\n")
    f.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c")
    out = tmp_path / "norms"
    assert main(["build", "--foundation", str(f.root), "--out", str(out)]) == 2
    assert "specs/x\\xff.md: path not UTF-8" in capsys.readouterr().err
    assert not out.exists()


def test_an_excluded_path_not_utf8_is_ignored_r34(tmp_path: Path) -> None:
    """An excluded path is ignored whatever its bytes.

    Spec: R34, R62
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "# A\n\nx\n")
    f.git("add", "-A")
    _add_blob(f, b".tool/x\xff.txt", b"y\n")
    f.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c")
    out = tmp_path / "norms"
    assert main(["build", "--foundation", str(f.root), "--out", str(out)]) == 0
    assert sorted(read_store(out / "data" / "tree.jsonl").files) == ["specs/a.md"]


def test_a_selected_path_not_utf8_is_refused_whatever_its_name_r34(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A selected path that is not UTF-8 is refused, a plain copy's as a .md file's.

    Spec: R34, R62
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "# A\n\nx\n")
    f.git("add", "-A")
    _add_blob(f, b"specs/x\xff.txt", b"y\n")
    f.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c")
    out = tmp_path / "norms"
    assert main(["build", "--foundation", str(f.root), "--out", str(out)]) == 2
    assert capsys.readouterr().err == "norms-gen: specs/x\\xff.txt: path not UTF-8\n"
    assert not out.exists()
