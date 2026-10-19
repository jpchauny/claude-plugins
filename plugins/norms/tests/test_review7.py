"""Regressions of the seventh review (fix round 7): one test or more per finding.

The code defects (a JSONL path that leads out of specs-repo-annotated/, an
inconsistent JSONL that build accepted, `NaN` read as JSON, paths that
one file system folds into one) were reproduced before they were fixed.
The other tests pin behaviour the specs now state.
"""

from __future__ import annotations

import json
import unicodedata
from importlib import metadata
from pathlib import Path

import pytest

from norms_generator.cli import main
from norms_generator.store import Status, Store, StoreError, read_store
from norms_generator.tree import build_tree
from test_cli import Foundation
from test_review5 import _add_blob
from test_store import by_id, parsed, run


def _build(f: Foundation, out: Path, *extra: str) -> int:
    return main(["build", "--foundation", str(f.root), "--out", str(out), *extra])


def _verify(f: Foundation, out: Path) -> int:
    return main(["verify", "--foundation", str(f.root), "--out", str(out)])


def _two_files(tmp_path: Path) -> tuple[Foundation, Path]:
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "alpha\n\nbeta\n")
    f.write("specs/b.md", "gamma\n")
    f.commit()
    out = tmp_path / "norms"
    assert _build(f, out) == 0
    return f, out


def _lines(out: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in (out / "data/tree.jsonl").read_text().splitlines()]


def _write_lines(out: Path, lines: list[dict[str, object]]) -> None:
    text = "".join(json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n" for o in lines)
    (out / "data/tree.jsonl").write_text(text)


def _snapshot(out: Path) -> dict[str, bytes]:
    return {str(p.relative_to(out)): p.read_bytes() for p in sorted(out.rglob("*")) if p.is_file()}


# --- a `file` line's path cannot lead out of specs-repo-annotated/ -----------------------


@pytest.mark.parametrize("path", ["/abs/x.md", "../x.md", "specs/../../x.md", "specs//a.md", "./a.md", "specs/a.txt", ""])
def test_a_file_path_of_another_form_makes_the_jsonl_unreadable_r61(tmp_path: Path, path: str) -> None:
    """A `file` line whose path has another form makes the JSONL unreadable.

    Spec: R61, R62
    """
    p = tmp_path / "tree.jsonl"
    p.write_text(json.dumps({"type": "file", "path": path, "prefix": "VIC"}) + "\n")
    with pytest.raises(StoreError, match=r"tree\.jsonl:1: ValueError: bad path"):
        read_store(p)


def test_build_never_removes_a_file_outside_the_output_folder_r62(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Nothing outside specs-repo-annotated/ is removed; build refuses the JSONL as unreadable.

    Spec: R34, R61, R62
    """
    f, out = _two_files(tmp_path)
    victim = tmp_path / "victim"
    (victim / "sub").mkdir(parents=True)
    (victim / "x.md").write_text("keep\n")
    (victim / "sub" / "y.md").write_text("keep\n")
    lines = _lines(out)
    lines.insert(1, {"type": "file", "path": str(victim / "x.md"), "prefix": "VIC"})
    lines.insert(1, {"type": "file", "path": "../../victim/sub/y.md", "prefix": "VID"})
    _write_lines(out, lines)
    assert _build(f, out) == 2
    assert "bad path" in capsys.readouterr().err
    assert (victim / "x.md").read_text() == "keep\n"
    assert (victim / "sub" / "y.md").read_text() == "keep\n"


# --- build refuses a JSONL that is readable but not consistent


def _edit_store(out: Path, edit) -> None:  # type: ignore[no-untyped-def]
    lines = _lines(out)
    edit(lines)
    _write_lines(out, lines)


def _dup_id(lines: list[dict[str, object]]) -> None:
    for o in lines:
        if o.get("id") == "SPB-1":
            o["id"] = "SPA-1"


def _dup_prefix(lines: list[dict[str, object]]) -> None:
    for o in lines:
        if o.get("type") == "file" and o["path"] == "specs/b.md":
            o["prefix"] = "SPA"


def _retired_in_use(lines: list[dict[str, object]]) -> None:
    lines[0]["retired_prefixes"] = ["SPA"]


def _node_without_file(lines: list[dict[str, object]]) -> None:
    lines[:] = [o for o in lines if not (o.get("type") == "file" and o["path"] == "specs/b.md")]


def _retired_copy(lines: list[dict[str, object]]) -> None:
    copy = dict(next(o for o in lines if o.get("id") == "SPA-1"))
    copy.update(status="retired", own_text="other")
    lines.append(copy)


@pytest.mark.parametrize(
    ("edit", "problem"),
    [
        (_dup_id, "SPA-1 is stored twice"),
        (_retired_copy, "SPA-1 is stored twice"),
        (_dup_prefix, "prefix SPA is used by specs/a.md and specs/b.md"),
        (_retired_in_use, "prefix SPA is retired but used by specs/a.md"),
        (_node_without_file, "is in specs/b.md, which is not a JSONL file"),
    ],
)
def test_build_refuses_a_jsonl_that_is_not_consistent_r34(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], edit, problem: str  # type: ignore[no-untyped-def]
) -> None:
    """Build refuses a JSONL that is not consistent.

    Spec: R34, R61, R64
    """
    f, out = _two_files(tmp_path)
    _edit_store(out, edit)
    before = _snapshot(out)
    capsys.readouterr()
    assert _build(f, out) == 2
    err = capsys.readouterr().err
    assert "tree.jsonl: not consistent: " in err and problem in err
    assert _snapshot(out) == before  # nothing written
    assert _verify(f, out) == 1  # verify reports the same problem
    assert problem in capsys.readouterr().err


# --- NaN, Infinity and -Infinity are not JSON ---------------------------------


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
def test_nan_and_infinity_make_the_jsonl_unreadable_r61(tmp_path: Path, token: str) -> None:
    """NaN, Infinity and -Infinity are not JSON, so the JSONL is unreadable.

    Spec: R61
    """
    p = tmp_path / "tree.jsonl"
    p.write_text('{"type":"meta","x":' + token + "}\n")
    with pytest.raises(StoreError, match=r"tree\.jsonl:1: ValueError: " + token + " is not JSON"):
        read_store(p)


# --- a line of only white space, as str.isspace() sees it, is skipped ---------


@pytest.mark.parametrize("blank", [" ", " ", "\x0c", "\x1c ", " \t\r"])
def test_a_line_of_unicode_white_space_is_skipped_r61(tmp_path: Path, blank: str) -> None:
    """A line of only Unicode white space is skipped.

    Spec: R61
    """
    p = tmp_path / "tree.jsonl"
    p.write_text('{"type":"meta","foundation_commit":"c1"}\n' + blank + "\n")
    assert read_store(p).foundation_commit == "c1"


# --- an ID's number starts at 1 -----------------------------------------------


@pytest.mark.parametrize("node_id", ["SPP-0", "SPP-01"])
def test_an_id_numbered_0_or_with_a_leading_zero_is_refused_r61(tmp_path: Path, node_id: str) -> None:
    """An ID numbered 0, or with a leading zero, is refused.

    Spec: R61
    """
    line = {
        "type": "node", "id": node_id, "file": "specs/p.md", "kind": "paragraph", "start": 0, "end": 1,
        "own_text": "a", "own_hash": "h", "tree_hash": "t",
    }  # fmt: skip
    p = tmp_path / "tree.jsonl"
    p.write_text(json.dumps(line) + "\n")
    with pytest.raises(StoreError, match="bad id"):
        read_store(p)


# --- paths that differ only in case or Unicode normalization ------------------


@pytest.mark.parametrize(
    ("first", "second"),
    [
        (b"specs/A.md", b"specs/a.md"),
        (b"specs/Sub/x.md", b"specs/sub/y.md"),
        (b"specs/X.md/b.md", b"specs/x.md"),
    ],
)
def test_paths_one_file_system_folds_into_one_are_refused_r34(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], first: bytes, second: bytes
) -> None:
    """Two paths that one file system folds into one are refused.

    Spec: R34
    """
    f = Foundation(tmp_path / "foundation")
    _add_blob(f, first, b"# alpha\n")
    _add_blob(f, second, b"# beta\n")
    f.git("commit", "-q", "-m", "c")
    out = tmp_path / "norms"
    assert _build(f, out) == 2
    assert "differ only in case or Unicode normalization" in capsys.readouterr().err
    assert not out.exists()


def test_paths_that_differ_only_in_unicode_normalization_are_refused_r34() -> None:
    """Two paths that differ only in Unicode normalization are refused.

    Spec: R34
    """
    # git on macOS stores such paths precomposed, so they are checked directly
    from norms_generator.cli import FoundationError, check_paths

    nfc, nfd = (unicodedata.normalize(form, "specs/é.md") for form in ("NFC", "NFD"))
    assert nfc != nfd
    with pytest.raises(FoundationError, match="differ only in case or Unicode normalization"):
        check_paths([nfc, nfd])
    check_paths(["specs/a.md", "specs/b.md", "specs/a/b.md"])


# --- a column moved to or from an open end changes its padding


def test_moving_a_column_to_an_open_end_of_a_table_changes_hashes_u5() -> None:
    """A column moved to or from an end without a pipe changes its padding, so its hashes.

    Spec: R13, R16, R31, R59, U5
    """
    v1 = parsed(a="a | b |\n:-- | --- |\nx | y |\n")
    s1, _ = run(v1, Store(), "c1")
    v2 = parsed(a="b | a |\n--- | :-- |\ny | x |\n")
    _, changes = run(v2, s1, "c2")
    edited = {c.id for c in changes if c.status is Status.EDITED}
    table = v2["specs/a.md"].children[0]
    assert table.id in edited  # its delimiter cells' bytes changed: `:-- ` became ` :-- `
    cells = [c.id for c in table.children if c.kind.value == "table_cell"]
    cells += [c.id for row in table.children for c in row.children]
    assert len(cells) == 4 and set(cells) <= edited  # `a ` became ` a`: the padding is the cell's own text
    # with pipes at both ends the same move changes no hash
    closed = build_tree(b"| a | b |\n| :-- | --- |\n").children[0]
    moved = build_tree(b"| b | a |\n| --- | :-- |\n").children[0]
    assert (closed.own_hash, closed.tree_hash) == (moved.own_hash, moved.tree_hash)


# --- a node of a renamed file has not moved, but its heading shows the path


def test_a_node_of_a_renamed_file_has_not_moved_but_its_entry_shows_both_paths_r63() -> None:
    """A node of a renamed file has not moved, but its entry shows both paths.

    Spec: R59, R63 (E78)
    """
    from norms_generator.store import report_markdown

    v1 = parsed(p="# Head\n\nNumbers are always signed.\n\nStrings are text.\n")
    s1, _ = run(v1, Store(), "c1")
    v2 = parsed(q="# Head\n\nNumbers are always signed.\n\nStrings are UTF-8 text.\n")
    _, changes = run(v2, s1, "c2")
    edited = [c for c in changes if c.status is Status.EDITED]
    assert len(edited) == 1 and not edited[0].moved
    md = report_markdown(changes)
    assert f"### {edited[0].id} (paragraph, specs/p.md -> specs/q.md)" in md
    assert "Moved:" not in md.split(f"### {edited[0].id}")[1].split("###")[0]
    files = by_id(changes)
    assert files["SPP"].moved  # a file node moves when its path changes


# --- what the meta line holds -------------------------------------------------


def test_the_meta_line_holds_the_full_sha_and_the_package_version_r61(tmp_path: Path) -> None:
    """The meta line, the report's first-run line, and another name of the commit is a rebuild.

    Spec: R60, R61, R63
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "alpha\n")
    sha = f.commit()
    out = tmp_path / "norms"
    assert _build(f, out, "--commit", sha[:7]) == 0
    meta = _lines(out)[0]
    assert meta["foundation_commit"] == sha and len(sha) == 40
    assert meta["generator_version"] == metadata.version("norms-generator")
    report = (out / "data/report.md").read_text()
    assert f"Foundation nothing (first run) -> `{sha}`." in report
    before = _snapshot(out)
    assert _build(f, out, "--commit", "main") == 0  # the same commit by another name: a rebuild
    assert _snapshot(out) == before


def test_a_short_sha_in_the_meta_line_is_not_a_rebuild_r60(tmp_path: Path) -> None:
    """A short SHA in the meta line is not a rebuild, though verify resolves it.

    Spec: R60, R61, R64
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "alpha\n")
    sha = f.commit()
    out = tmp_path / "norms"
    assert _build(f, out) == 0
    _edit_store(out, lambda lines: lines[0].update(foundation_commit=sha[:7]))
    assert _verify(f, out) == 0  # verify resolves the pinned commit
    assert _build(f, out) == 0
    assert f"Foundation `{sha[:7]}` -> `{sha}`." in (out / "data/report.md").read_text()


# --- report.json's encoding and values ----------------------------------------


def test_report_json_lines_and_values_r63(tmp_path: Path) -> None:
    """The encoding and the values of `report.json`.

    Spec: R63
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "# Types\n\nNumbers are always signed.\n\nGone ä.\n")
    f.commit()
    out = tmp_path / "norms"
    assert _build(f, out) == 0
    f.write("specs/a.md", "# Types\n\nNumbers are signed.\n\nNew one.\n")
    f.commit()
    assert _build(f, out) == 0
    raw = (out / "data/report.json").read_text()
    records = {}
    for line in raw.splitlines():
        record = json.loads(line)
        assert line == json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        records[record["id"]] = record
    assert len(records["SPA-1"]) == 16
    edited = next(r for r in records.values() if r["status"] == "edited")
    assert edited["similarity"] == round(edited["similarity"], 4) and edited["last_text"] is None
    new = next(r for r in records.values() if r["status"] == "new")
    assert (new["old_file"], new["old_parent"], new["old_text"], new["old_tree_hash"]) == (None,) * 4
    retired = next(r for r in records.values() if r["status"] == "retired")
    assert retired["file"] == retired["old_file"] == "specs/a.md"
    assert (retired["new_parent"], retired["new_text"], retired["new_tree_hash"]) == (None,) * 3
    assert retired["old_text"] == retired["last_text"] == "Gone ä."
    section = records["SPA-1"]
    assert section["status"] == "child_changed" and isinstance(section["changed_children"], list)
    assert section["old_text"] == section["new_text"]  # own texts, also for a container


# --- stray files under specs-repo-annotated/ ---------------------------------------------


def test_stray_files_under_annotated_are_reported_then_removed_u6(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify reports a stray file under specs-repo-annotated/, and the next build removes it and its folder.

    Spec: R62, R64, U6
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "alpha\n")
    f.commit()
    out = tmp_path / "norms"
    assert _build(f, out) == 0
    stray = out / "specs-repo-annotated/specs/old/stale.md"
    stray.parent.mkdir(parents=True)
    stray.write_text("⟬OLD⟭\n")
    capsys.readouterr()
    assert _verify(f, out) == 1
    assert capsys.readouterr().err == (
        f"{stray.parent}: not a copy of a JSONL file; build removes it (U6)\nverify: 1 problems\n"
    )
    assert _build(f, out) == 0
    assert not stray.parent.exists()
    assert _verify(f, out) == 0


# --- the whole repository, the excluded paths, the plain copies --------------------


def _whole_repository(tmp_path: Path) -> tuple[Foundation, Path]:
    f = Foundation(tmp_path / "foundation")
    f.write("README.md", "top\n")
    f.write("specs/a.md", "alpha\n")
    f.write("docs/guide.md", "guide\n")
    f.write("sub/LICENSE.md", "not at the root\n")
    f.write("CLAUDE.md", "agents\n")
    f.write("sub/claude.md", "agents\n")
    f.write("sub/AGENTS.md", "agents\n")
    f.write("CLAUDE.local.md", "agents\n")
    f.write(".claude/notes.md", "tool\n")
    f.write(".github/pr.md", "tool\n")
    f.write("specs/.hidden/x.md", "tool\n")
    f.write("License.MD", "community\n")
    f.write("CHANGELOG.md", "community\n")
    f.write("CONTRIBUTING.md", "community\n")
    f.write("CODE_OF_CONDUCT.md", "community\n")
    f.write("SECURITY.md", "community\n")
    (f.root / "specs" / "img").mkdir()
    (f.root / "specs" / "img" / "d.png").write_bytes(b"\x89PNG\r\n\x00\xff")
    f.write("specs/notes.txt", "plain\r\n")
    f.commit()
    return f, tmp_path / "norms"


def test_the_whole_repository_is_read_but_the_excluded_paths_r62(tmp_path: Path) -> None:
    """Every .md file of the repository is annotated, in any folder, a README included; the excluded paths are not.

    Spec: R62
    """
    f, out = _whole_repository(tmp_path)
    assert _build(f, out) == 0
    store = read_store(out / "data/tree.jsonl")
    assert sorted(store.files) == ["README.md", "docs/guide.md", "specs/a.md", "sub/LICENSE.md"]
    folder = out / "specs-repo-annotated"
    assert sorted(str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file()) == [
        "README.md", "docs/guide.md", "specs/a.md", "specs/img/d.png", "specs/notes.txt", "sub/LICENSE.md",
    ]


def test_every_other_selected_file_is_a_plain_copy_r61_r62(tmp_path: Path) -> None:
    """A selected file that is not Markdown is copied byte for byte, and its path and sha256 go to a copy line.

    Spec: R61, R62
    """
    f, out = _whole_repository(tmp_path)
    assert _build(f, out) == 0
    folder = out / "specs-repo-annotated"
    assert (folder / "specs/img/d.png").read_bytes() == b"\x89PNG\r\n\x00\xff"
    assert (folder / "specs/notes.txt").read_bytes() == b"plain\r\n"
    lines = [json.loads(line) for line in (out / "data/tree.jsonl").read_text(encoding="utf-8").splitlines()]
    copies = [line for line in lines if line["type"] == "copy"]
    assert [c["path"] for c in copies] == ["specs/img/d.png", "specs/notes.txt"]
    kinds = [line["type"] for line in lines]
    assert kinds.index("copy") > max(i for i, k in enumerate(kinds) if k == "file")  # R61: after the file lines
    assert kinds.index("copy") < kinds.index("node")
    assert read_store(out / "data/tree.jsonl").copies == {c["path"]: c["sha256"] for c in copies}
    assert _verify(f, out) == 0


def test_verify_checks_each_plain_copy_r64(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A plain copy that is missing, edited or foreign is a problem of verify, worded as the spec words it.

    Spec: R64, U6
    """
    f, out = _whole_repository(tmp_path)
    assert _build(f, out) == 0
    folder = out / "specs-repo-annotated"
    (folder / "specs/img/d.png").unlink()
    (folder / "specs/notes.txt").write_bytes(b"edited\n")
    (folder / "specs/img/stray.png").write_bytes(b"x")
    capsys.readouterr()
    assert _verify(f, out) == 1
    err = capsys.readouterr().err
    assert f"specs/img/d.png: no copy at {folder / 'specs/img/d.png'}\n" in err
    assert f"specs/notes.txt: copy at {folder / 'specs/notes.txt'} differs from foundation\n" in err
    assert f"{folder / 'specs/img/stray.png'}: not a copy of a JSONL file; build removes it (U6)\n" in err
    assert _build(f, out) == 0
    assert _verify(f, out) == 0
    assert not (folder / "specs/img/stray.png").exists()


def test_a_copy_line_reads_back_and_its_path_has_the_form_r61(tmp_path: Path) -> None:
    """A copy line needs a path that does not end in .md; a file line's path must.

    Spec: R61
    """
    jsonl = tmp_path / "tree.jsonl"
    jsonl.write_text('{"type":"copy","path":"specs/d.png","sha256":"ab"}\n', encoding="utf-8")
    assert read_store(jsonl).copies == {"specs/d.png": "ab"}
    jsonl.write_text('{"type":"copy","path":"specs/a.md"}\n', encoding="utf-8")
    with pytest.raises(StoreError):
        read_store(jsonl)
    jsonl.write_text('{"type":"copy","path":"../d.png"}\n', encoding="utf-8")
    with pytest.raises(StoreError):
        read_store(jsonl)
