"""Regressions of the third review (fix round 3): one test or more per defect.

Each case was found by a reviewer and reproduced before it was fixed;
the exact outputs pin where the IDs go, the property test checks every
case for pure insertion, well-formed markers, blank lines and the
same block structure as foundation.

Spec: R30
"""

from __future__ import annotations

from pathlib import Path

import pytest

from norms_generator.annotate import annotate_text, strip
from norms_generator.model import Kind
from norms_generator.store import Store, assign_ids, build_store
from norms_generator.structure import block_structure
from norms_generator.tree import build_tree, walk
from norms_generator.verify import _check_markers
from test_annotate import check_insertions
from test_cli import Foundation, build, main, nodes
from test_examples import check_blank_lines, check_markers

# Every input of the review's findings that broke the structure or the markers.
CASES: list[str] = [
    # R27: no collapse with a thematic break (E21)
    "> a\n>\n> ***\n",
    "> a\n>\n>\n",
    # R38, R49: a tab after the marker on an item's marker line: indented code there (E64)
    ">-\t\tc", " > -\t\tc", "  >-\t\tc", ">*\t\tc", " > 1.\t\tc", ">  > 2) \tc", " > -\t e",
    "- >-\t\tc", "1.\n    > -\t\tc", ">1.\n>    1. -\t\tc", "> -\t\tc",
    # R36: a line-end ID inside a code span or a link that runs on (E34)
    "- - [ ] see `a\n  b`\n", "- - [ ] ```\n        ```\n", "- - [ ] [l](\n  /u)\n",
    # R35: a bare list marker ends a multi-line item paragraph (E29)
    "- a\n  1.\n", "- see the list\n  1.\n", "- a\n  +\n", "* t\n  1.\n", "2) H\n   1.\n",
    # R35: a definition after a task checkbox (E31)
    "- [ ] [a]: /u\n", "1. [ ] [a]: /url\n2. b\n", "* [a]:u\n  -\n",
    # R43: a definition ending on a lazy line (E49)
    "> [a]:\n/u\n", "- [a]:\n/u\n", "1. [a]:\n/u\n", "> 1. [a]:\n> /u\n", "1. 1. [a]:\n:\n", "[a]:\n/u\n",
    # R47: a ">" content line in a quote is not blank (E60)
    "> <div>\n> >\n", "><e>\n>>\n", "><!--\n>>\n", ">     >\n>>\n", ">)\n    >\n>- a\n", "-\t>\n  > >\n",
    # R27, R39: an empty item that took its quote's place (E43)
    ">-\n>   2)\n", "> -\n>   [b]: /v\n", ">-\n>   <e>\n", ">-\n>       e\n", ">1.\r>    1.\r", "- a\n> -\n>   2)\n",
    # R44: a table whose header row is an indented or lazy line of a paragraph (E53)
    "para\n    a | b\n--|--\n", "]\n    a|b\n-|-\n", "]\r    a|b\r-|-\r",
    "-\r  `\ra|b\r  -|-\r", "-\n  `\na|b\n  -|-\n",
    # R35, R38: a table on a task item's marker line
    "- [ ] | a | b |\n  |---|---|\n", "- [ ] x|\n  -|\n",
    # R38, R45: an item in a quote with another indentation on the next line
    " > 1.\n>    a|b\n>    -|-\n",
    # R36, R64: an inline ID before a hard line break
    "- - [ ]  \nd\n", "- - [ ]  \n  d\n",
    # R38, R47: a line after an item, not indented into it
    "- > a\n  >\n  > b\n<p>\n", "-   >a\nb\n<div>\n", "> - >x\ny\n<div>\n",
    # R18, R51: empty ATX headings (E2, E67, E68)
    "  #\n", "> #\n", "   ##\n", "> ######\n", "1. > #\n", "#\n", "# #\n",
    # R36, R49: a definition on a marker line that cannot be split (E65)
    "- [a]: /u\n\n\n  b\n", "- [a]: /u\r\n\r\n\r\n  b\r\n", "1. [a]:\n   /u\n\n\n   ```x\n", "- [a]:u\n\n\n  `\n",
    # R37, R44, R49: minimized from the review's fuzz files (mins.json, bad_*.json)
    ">1. [a]:u\n>    a||\n>    -|-\n", ">~~~\n>~~~\n  >-\t\tc\n", ">- - ]\n>   x\n>     -|\n", "- >-\t\tc\n  >- \n  >--\n",
]


@pytest.mark.parametrize("source", CASES)
def test_properties_of_review3_cases(source: str) -> None:
    """Each case is pure insertion, its markers well formed, its blank lines right and its blocks foundation's.

    Spec: R23, R29, R30, R64
    """
    data = source.encode()
    out, insertions = annotate_text(data, "TYP")
    assert strip(out, insertions) == data
    check_insertions(insertions)
    lines = out.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    check_markers(lines, file_marker=True)
    check_blank_lines(lines)
    assert block_structure(out) == block_structure(data)
    assert _check_markers(out.decode(), "TYP", [_Node(i) for i in _ids(data)]) == []


class _Node:
    """The one field of a StoredNode that _check_markers reads."""

    def __init__(self, ident: str) -> None:
        self.id = ident


def _ids(source: bytes) -> list[str]:
    root = build_tree(source)
    return ["TYP"] + [f"TYP-{n}" for n in range(1, len(list(walk(root))))]


def run(text: str) -> str:
    return annotate_text(text.encode(), "TYP", file_marker=False)[0].decode()


# --- a quote with a thematic break is not collapsed ---------------------------


def test_quote_with_a_thematic_break_keeps_its_node_e21() -> None:
    """A quote that also holds a thematic break keeps its own node.

    Spec: R27 (E21)
    """
    root = build_tree(b"> a\n>\n> ***\n")
    (quote,) = root.children
    assert quote.kind is Kind.BLOCK_QUOTE
    (para,) = quote.children
    assert para.kind is Kind.PARAGRAPH and para.own_text == b"a"
    assert b"***" in quote.own_text
    assert run("> a\n>\n> ***\n") == "⟬TYP-1 begin⟭\n\n> a ⟬TYP-2⟭\n>\n> ***\n\n⟬TYP-1 end⟭\n"


def test_quote_with_only_blank_lines_after_its_paragraph_collapses_r27() -> None:
    """Trailing blank `>` lines do not keep a quote of one paragraph from collapsing.

    Spec: R27
    """
    (para,) = build_tree(b"> a\n>\n>\n").children
    assert para.kind is Kind.PARAGRAPH


def _step(files: dict[str, bytes], previous: Store, commit: str) -> tuple[Store, dict[str, str]]:
    from norms_generator.prefixes import assign_prefixes
    from norms_generator.store import detect_renames

    trees = {p: build_tree(s, p) for p, s in files.items()}
    prefixes = assign_prefixes(sorted(trees), previous.prefixes(), previous.retired_prefixes(), detect_renames(trees, previous))
    changes = assign_ids(trees, previous, prefixes)
    store = build_store(trees, prefixes, previous, changes, foundation_commit=commit)
    return store, {c.id: c.status.value for c in changes}


def test_paragraph_leaving_a_collapsed_quote_keeps_its_id_e72() -> None:
    """"> q" was one node; once the quote holds more, "q" is paired by its words.

    Spec: R27, R55 (E72)
    """
    v1, _ = _step({"specs/a.md": b"# A\n\nx\n\n> q\n"}, Store(), "c1")
    para = next(n for n in v1.nodes if n.own_text == "> q")
    for added in (b">\n> ***\n", b">\n> r\n"):
        _, status = _step({"specs/a.md": b"# A\n\nx\n\n> q\n" + added}, v1, "c2")
        assert status[para.id] == "edited"


# --- non-UTF-8 foundation, no .md file to build (cli) ---------------------------------


def test_non_utf8_file_is_refused_naming_it_r34(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A foundation file that is not UTF-8 is refused, naming it, and nothing is written.

    Spec: R3, R34
    """
    f = Foundation(tmp_path / "foundation")
    (f.root / "specs").mkdir()
    (f.root / "specs" / "a.md").write_bytes(b"# Caf\xe9\n\nText.\n")
    f.commit()
    out = tmp_path / "norms"
    assert main(["build", "--foundation", str(f.root), "--out", str(out)]) == 2
    assert "specs/a.md: not UTF-8" in capsys.readouterr().err
    assert not out.exists()


def test_no_md_file_to_build_is_refused_and_keeps_the_store(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A repository with no selected .md file is refused, and the outputs stay as they were.

    Spec: R3, R34, R62
    """
    f = Foundation(tmp_path / "foundation")
    f.write("specs/alpha.md", "# A\n\nx\n")
    f.commit()
    out = tmp_path / "norms"
    build(f, out)
    before = (out / "data" / "tree.jsonl").read_bytes()
    (f.root / "specs" / "alpha.md").unlink()
    f.write("CLAUDE.md", "# Agents only\n")
    f.commit()
    assert main(["build", "--foundation", str(f.root), "--out", str(out)]) == 2
    assert "no .md file to build at " in capsys.readouterr().err
    assert (out / "data" / "tree.jsonl").read_bytes() == before
    assert (out / "specs-repo-annotated" / "specs" / "alpha.md").exists()


# --- a retired node's changed_since is of its own step --------------------------


def test_retired_node_changed_since_is_of_the_step_it_retired_in_e84(tmp_path: Path) -> None:
    """A retired node's changed_since is the commit of the step it retired in.

    Spec: R60, U3 (E84)
    """
    f = Foundation(tmp_path / "foundation")
    out = tmp_path / "norms"
    f.write("specs/a.md", "# A\n\nfirst paragraph here\n\nsecond one, to be removed entirely\n")
    c1 = f.commit()
    build(f, out)
    f.write("specs/a.md", "# A\n\nfirst paragraph here\n")
    f.commit()
    build(f, out)
    retired = [n for n in nodes(out) if n["status"] == "retired"]
    assert retired and all(n["changed_since"] == c1 for n in retired)
    build(f, out)  # a rebuild of the same version keeps its flags
    assert [n["changed_since"] for n in nodes(out) if n["status"] == "retired"] == [c1] * len(retired)
    f.write("specs/a.md", "# A\n\nfirst paragraph here\n\nthird\n")
    f.commit()
    build(f, out)
    assert all(n["changed_since"] is None for n in nodes(out) if n["id"] in {r["id"] for r in retired})


# --- annotation: exact places --------------------------------------------------


def test_code_on_a_marker_line_that_cannot_move_is_hoisted_e64() -> None:
    """The tabs would expand otherwise on a line of their own; nothing goes in the code.

    Spec: R26, R49 (E64)
    """
    assert run(">-\t\tc\n") == "⟬TYP-1 begin⟭\n\n⟬TYP-2 begin⟭\n\n>-\t\tc\n\n⟬TYP-2 end⟭\n\n⟬TYP-1 end⟭\n"


def test_line_end_id_never_in_a_code_span_e34() -> None:
    """The line-end ID goes at the end of a code span that runs on.

    Spec: R36 (E34)
    """
    assert run("- - [ ] see `a\n  b`\n") == "⟬TYP-1 begin⟭\n\n- - [ ] see `a\n  b` ⟬TYP-2⟭\n\n⟬TYP-1 end⟭\n"


def test_definition_on_a_line_that_cannot_be_split_is_hoisted_e65() -> None:
    """A definition on a marker line that cannot be split is framed at its top-level block.

    Spec: R36, R49 (E65)
    """
    assert run("- [a]: /u\n\n\n  b\n") == (
        "⟬TYP-1 begin⟭\n\n⟬TYP-2 begin⟭\n\n- [a]: /u\n\n⟬TYP-2 end⟭\n\n⟬TYP-1 end⟭\n\n\n  b ⟬TYP-3⟭\n"
    )


def test_bare_list_marker_ending_an_item_paragraph_e29() -> None:
    """An item paragraph ending with a bare list marker has its ID after the item's marker.

    Spec: R35 (E29)
    """
    assert run("- a\n  1.\n") == "- ⟬TYP-1⟭\n\n  a\n  1.\n"


def test_definition_after_a_task_checkbox_e31() -> None:
    """After a task checkbox the item's ID goes before the definition, which is framed.

    Spec: R35 (E31)
    """
    assert run("- [ ] [a]: /u\n") == "- [ ] ⟬TYP-1⟭\n\n  ⟬TYP-2 begin⟭\n\n  [a]: /u\n\n  ⟬TYP-2 end⟭\n"


def test_definition_ending_on_a_lazy_line_e49() -> None:
    """A definition completed on a lazy line stays in its quote.

    Spec: R43 (E49)
    """
    assert run("> [a]:\n/u\n") == "⟬TYP-1 begin⟭\n\n> [a]:\n/u\n\n⟬TYP-1 end⟭\n"


def test_gt_content_line_in_a_quote_is_not_blank_e60() -> None:
    """A `>` past the quotes of its block is content, not a blank line.

    Spec: R47 (E60)
    """
    assert run("> <div>\n> >\n") == "⟬TYP-1 begin⟭\n\n> <div>\n> >\n\n⟬TYP-1 end⟭\n"


def test_empty_item_out_of_its_quote_keeps_the_quote_in_its_blank_line_e43() -> None:
    """An empty item that took its quote's place keeps the `>` in its blank line.

    Spec: R39 (E43)
    """
    assert run(">-\n>   2)\n") == ">- ⟬TYP-1⟭\n>\n>   2) ⟬TYP-2⟭\n"


def test_table_whose_header_is_an_indented_paragraph_line_e53() -> None:
    """A header row that was an indented line of the paragraph stays one.

    Spec: R44 (E53)
    """
    assert run("para\n    a | b\n--|--\n") == (
        "⟬TYP-2 begin⟭\n\npara ⟬TYP-1⟭\n    a ⟬TYP-3⟭ | b ⟬TYP-4⟭\n--|--\n\n⟬TYP-2 end⟭\n"
    )


def test_table_whose_header_is_a_lazy_line_of_an_item_r44() -> None:
    """Above the paragraph of an empty item, the probe includes the item's ID.

    Spec: R39, R44
    """
    assert run("-\n  `\na|b\n  -|-\n") == (
        # R39: alone, the empty item's ID would join "`" (the structure check keeps
        # line breaks since fix 4): the empty item's blank line follows it
        "- ⟬TYP-1⟭\n\n\n  ⟬TYP-2 begin⟭\n\n  `\na ⟬TYP-3⟭|b ⟬TYP-4⟭\n  -|-\n\n  ⟬TYP-2 end⟭\n"
    )


def test_table_on_a_task_item_marker_line_r35() -> None:
    """A table first in a task item has the item's ID after the checkbox, as a definition does.

    Spec: R35, R38 (E31)
    """
    assert run("- [ ] | a | b |\n  |---|---|\n") == (
        "- [ ] ⟬TYP-1⟭\n\n  ⟬TYP-2 begin⟭\n\n  | a ⟬TYP-3⟭ | b ⟬TYP-4⟭ |\n  |---|---|\n\n  ⟬TYP-2 end⟭\n"
    )


def test_item_content_follows_the_quote_on_each_line_r38() -> None:
    """On each line, the item's content and its rows start at the quote's content.

    Spec: R38, R45
    """
    assert run(" > 1.\n>    a|b\n>    -|-\n") == (
        " > 1. ⟬TYP-1⟭\n>\n>    ⟬TYP-2 begin⟭\n>\n>    a ⟬TYP-3⟭|b ⟬TYP-4⟭\n>    -|-\n>\n>    ⟬TYP-2 end⟭\n"
    )


def test_empty_atx_heading_off_column_one_e67() -> None:
    """An empty ATX heading off column 1 has its ID at the end of its line.

    Spec: R51 (E67, E68)
    """
    assert run("  #\n") == "  # ⟬TYP-1⟭\n"
    assert run("> #\n") == "> # ⟬TYP-1⟭\n"
    assert annotate_text(b"  #\n", "TYP")[0].decode().startswith("⟬TYP⟭\n")


def test_line_after_an_item_not_indented_into_it_r47() -> None:
    """A line not indented to its item's content is not in the item.

    Spec: R38, R47
    """
    root = build_tree(b"- > a\n  >\n  > b\n<p>\n")
    item, html = root.children
    assert item.end == 15 and html.kind is Kind.HTML_BLOCK and html.start == 16
    assert run("- > a\n  >\n  > b\n<p>\n").endswith("  ⟬TYP-2 end⟭\n\n⟬TYP-5 begin⟭\n\n<p>\n\n⟬TYP-5 end⟭\n")


# --- structure and markers checks of verify ------------------------------------


def test_structure_sees_a_marker_inside_a_code_span_or_link_e17() -> None:
    """The block comparison sees a marker inside a code span, raw HTML or a link.

    Spec: R64 (E17)
    """
    assert block_structure(b"see `a\n b`\n") != block_structure("see `a ⟬X-1⟭\n b` ⟬X-2⟭\n".encode())
    assert block_structure(b"see [a\nb](u)\n") != block_structure("see [a ⟬X-1⟭\nb](u)\n".encode())
    assert block_structure(b"see <span>\n") != block_structure("see <span ⟬X-1⟭>\n".encode())
    assert block_structure(b"see `a` [b](u)\n") == block_structure("see `a` [b](u) ⟬X-1⟭\n".encode())


def test_structure_ignores_an_id_before_a_hard_break() -> None:
    """The block comparison ignores an inline ID before a hard line break.

    Spec: R36, R64
    """
    assert block_structure(b"- - [ ]  \nd\n") == block_structure("- - [ ] ⟬TYP-1⟭  \nd ⟬TYP-2⟭\n".encode())


def test_markers_check_requires_nested_frames_r24() -> None:
    """Verify's markers check requires frames to nest.

    Spec: R24, R64
    """
    text = "⟬T⟭\n\n⟬T-1 begin⟭\n\n⟬T-2 begin⟭\n\nx\n\n⟬T-1 end⟭\n\n⟬T-2 end⟭\n"
    problems = _check_markers(text, "T", [_Node("T"), _Node("T-1"), _Node("T-2")])
    assert problems == ["the frame of T-1 ends inside the frame of T-2"]


def test_hoisted_frames_sit_right_inside_their_top_block_r49() -> None:
    """At one place, a hoisted frame's lines come before those of the top block's quoted children.

    Spec: R49
    """
    assert run(">~~~\n>~~~\n  >-\t\tc\n") == (
        "⟬TYP-1 begin⟭\n\n⟬TYP-3 begin⟭\n\n⟬TYP-4 begin⟭\n\n> ⟬TYP-2 begin⟭\n>\n>~~~\n>~~~\n>\n"
        "> ⟬TYP-2 end⟭\n>\n  >-\t\tc\n\n⟬TYP-4 end⟭\n\n⟬TYP-3 end⟭\n\n⟬TYP-1 end⟭\n"
    )


def test_table_after_a_marker_line_paragraph_with_no_place_is_hoisted_r49() -> None:
    """A table and paragraph with no placement are framed at their top-level block.

    Spec: R44, R49
    """
    assert run(">- - ]\n>   x\n>     -|\n") == (
        "⟬TYP-3 begin⟭\n\n>- ⟬TYP-1⟭\n>\n>   - ] ⟬TYP-2⟭\n>   x ⟬TYP-4⟭\n>     -|\n\n⟬TYP-3 end⟭\n"
    )


def test_item_paragraph_before_a_table_is_probed_in_the_file_r44() -> None:
    """Alone, "[a]:u" is a definition; before a table it is text, and takes the item's ID.

    Spec: R44
    """
    assert run(">1. [a]:u\n>    a||\n>    -|-\n") == (
        ">1. [a]:u ⟬TYP-1⟭\n>\n>    ⟬TYP-2 begin⟭\n>\n>    a ⟬TYP-3⟭| ⟬TYP-4⟭|\n>    -|-\n>\n>    ⟬TYP-2 end⟭\n"
    )


def test_frame_begun_after_a_tight_quote_marker_keeps_the_column() -> None:
    """">-" with no space: the rest of the line goes on after ">", not "> " (its tabs keep their width).

    Spec: R37, R49
    """
    out = run("- >-\t\tc\n  >- \n  >--\n")
    assert "  > ⟬TYP-3 begin⟭\n  >\n  >-\t\tc\n" in out
