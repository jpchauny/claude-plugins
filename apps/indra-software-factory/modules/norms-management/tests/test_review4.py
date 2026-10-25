"""Regressions of the fourth review (fix round 4): one test or more per defect.

Each case was reproduced before it was fixed. The property test checks
every input of the findings with the whole of verify.check_file (pure
insertion, markers, IDs, rebuilt tree, places and block structure);
the other tests pin the tree, the exact output or the store's result.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import pytest

from norms_generator import cmark
from norms_generator.annotate import _annotate, annotate, annotate_text, number_first_run
from norms_generator.model import Kind
from norms_generator.prefixes import assign_prefixes
from norms_generator.store import (
    Status,
    Store,
    StoredFile,
    StoredNode,
    StoreError,
    assign_ids,
    build_store,
    detect_renames,
    read_store,
    report_markdown,
)
from norms_generator.structure import block_structure
from norms_generator.tree import build_tree, walk
from norms_generator.verify import check_file
from test_cli import SpecsRepo, main, snapshot

CASES: list[bytes] = [
    # R43: definitions on lazy lines: a second definition, a lazy line that completes one (E48, E49)
    b"- [l]: /u\n[m]: /v\n\n- b\n", b"1. [l]: /u\n[m]: /v\n2. b\n", b"> [l]: /u\n[m]: /v\n> - x\n",
    b"> [l]: /u\n[m]: /v\n\nafter\n", b"- [a]: /u\n[b]: /v\n- c\n", b"2) [a]:u\n[a]:u\n2)\n",
    b"> \t[x]: /u\nb\nc\n", b">[a]:\n:-\n", b"> [a]:\n=\n", b"1. [a]:\n=\n", b"1. [a]:\r:-\r", b"  1. [a]:\n    >\n",
    b">[x]:\n=", b"- [x]:\n=", b"2) [x]:\n=", b">[x]:\n    ***", b">[x]:\n    ```", b">[x]:\n    <div>",
    b">[x]:\r--", b"2) [x]:\n===\n",
    # R44: a paragraph that a table interrupts, ending with a bare list marker (E52)
    b"[l]: /u\n1.\na | b\n--|--\n", b">b\n>1.\n |b\n>-|-\n", b"a\n1.\n\t- x\n|---|\n", b"[r]: /u\n*\na | b\n--|--\n",
    # R44, R46: a header row that is a row only after its paragraph
    b"a\n+\n-:\n| 1 |\n", b"a\n+\n:-\n", b"$\n1.\n:-", b">b\n>1.\n>-:", b"- a\n  +\n  -|\n",
    b"[r]: /u\n1.\n|-|\n", b"a\n1.\n|-|\n",
    # R44, R50: a header row after a paragraph of definitions only (E66)
    b"[a]: /u\n---\n|-|\n", b'[a]: <b> "t"\n---\n|-|\n',
    # R37: moved rest of line under ">" with no space or " > ": columns and tabs (E35, E36)
    b">- -\t<div>\n", b">- -\t<!--\n", b">* -\t<v>\n", b">1. -\t<v>\n", b">2) -\t<v>\n",
    b" > 1. -\t# h\n", b">1. -\t<p\n", b" > * -\t1)\n", b" > -\t-\t>\n", b" > 2) -\t#\n",
    b">* -\t<e>", b" > 1. -\t<v>", b">-\t-\t<!--", b" > - -\t#", b"  > 2) -\t<pre>\n   -->\n",
    # R16, R37: an HTML block indented in a quote on an item's marker line
    b"- >  <div>\n  >\n  > b\n", b"2) >  <p\n   >\n   >~\n",
    # R40: an empty task item (E44)
    b"- [ ] \n\n  b\n", b"- [x] \n\n  - b\n", b"- [ ] \n\n  -\n",
    # R36: a setext heading starting with "#" in a task item (E33)
    b"- a\n- [ ] #\n  -\n", b"-\n- [ ] #\n  -", b"#\r- [ ] #\r  -", b"- [ ] # done\n  ---\n",
    # R47: a ">" line indented less than its item
    b"-    > a\n    >\n     > > c\n", b" 10. >`\n    >\n     >>\n",
    # R36, R37: a nested item "[x]" that its line's move would make a task item
    b"- - [x]\n |b\n    -|-\n", b"- * [x]\n |b\n    -|-\n", b"1. 1. [x]\n |b\n      -|-\n", b"-\t* [x]\n ||\n      -|-\n",
    # R35: a one-line item paragraph after a tab, probed on the whole file (E28)
    b" -\t  [x]\n",
    # R35: a definition after a checkbox and a tab or 4 spaces (E31)
    b"- [ ]    [x]: /u\n", b"- [ ]\t[x]:u\n",
    # R39: an empty item's ID above a setext heading (E42)
    b"+\n  t\n  =\n", b")\n* 1.\n     a\n     -\n", b">+\n>   s\n>   -\n",
    # R48, U1: an unclosed HTML block after a tab (E62)
    b"- a\n\n  \t<!-- note\n", b"-\n  \t<!--", b"1.\n   \t<pre", b">]\n   > \t<pre",
    # R16: first-line indentation
    b"# T\n\n   <div>\n  x\n</div>\n", b"> a\n>\n>   <div>\n>   x", b"  a\n  b\n", b"  # A\n", b"  | a |\n  |---|\n",
]


def _stored(root, path: str = "f") -> list[StoredNode]:
    out: list[StoredNode] = []

    def rec(node, parent: str | None) -> None:
        text = node.own_text.decode("utf-8", "replace")
        out.append(StoredNode(node.id, path, node.kind, parent, node.start, node.end, text, node.own_hash, node.tree_hash))
        for child in node.children:
            rec(child, node.id)

    rec(root, None)
    return out


@pytest.mark.parametrize("source", CASES)
def test_cases_of_review4_are_sound(source: bytes) -> None:
    """Every case passes the whole of verify's check of one file.

    Spec: R23, R64
    """
    root = build_tree(source)
    number_first_run(root, "TST")
    annotated, insertions = annotate(source, root)
    stored = StoredFile("f", "TST", hashlib.sha256(source).hexdigest(), insertions)
    assert check_file("f", source, annotated, stored, _stored(root)) == []


def run(source: bytes) -> str:
    return annotate_text(source, "TYP", file_marker=False)[0].decode()


def kinds(source: bytes) -> list[tuple[str, bytes]]:
    return [(n.kind.value, n.own_text) for n in walk(build_tree(source))]


def _step(files: dict[str, bytes], previous: Store, commit: str) -> tuple[Store, dict[str, Status]]:
    trees = {p: build_tree(s, p) for p, s in files.items()}
    renames = detect_renames(trees, previous)
    prefixes = assign_prefixes(sorted(trees), previous.prefixes(), previous.retired_prefixes(), renames)
    changes = assign_ids(trees, previous, prefixes)
    return build_store(trees, prefixes, previous, changes, specs_commit=commit), {c.id: c.status for c in changes}


# --- the indentation of a block's first line is its own ------------------------


def test_html_block_first_line_indentation_is_its_own_text_r16() -> None:
    """The indentation of a block's first line is in its own text.

    Spec: R16
    """
    root = build_tree(b"# T\n\n   <div>\n  x\n</div>\n")
    html = [n for n in walk(root) if n.kind is Kind.HTML_BLOCK][0]
    assert html.own_text == b"   <div>\n  x\n</div>"
    quote = build_tree(b"> a\n>\n>   <div>\n>   x").children[0]
    assert [c.own_text for c in quote.children] == [b"a", b"  <div>\n>   x"]


def test_indenting_an_html_block_marks_it_to_review_r60() -> None:
    """Indenting an HTML block makes it edited and to review.

    Spec: R16, R59, R60
    """
    v1, _ = _step({"specs/t.md": b"# T\n\n<div>\n  x\n</div>\n"}, Store(), "c1")
    html = next(n for n in v1.nodes if n.kind is Kind.HTML_BLOCK)
    v2, status = _step({"specs/t.md": b"# T\n\n   <div>\n  x\n</div>\n"}, v1, "c2")
    assert status[html.id] is Status.EDITED
    assert next(n for n in v2.nodes if n.id == html.id).to_review


def test_first_line_indentation_is_in_the_paragraph_r16() -> None:
    """First-line indentation is own text; its containers are child_changed.

    Spec: R16, R27, R59
    """
    assert kinds(b"  a\n  b\n") == [("file", b"\n"), ("paragraph", b"  a\n  b")]
    assert kinds(b"  # A\n")[1] == ("heading", b"  # A")  # its section collapsed
    assert ("table", b"  ||\n  |---|") in kinds(b"  | a |\n  |---|\n")
    v1, _ = _step({"specs/t.md": b"# T\n\npara one here\n\nother text\n"}, Store(), "c1")
    para = next(n for n in v1.nodes if n.own_text == "para one here")
    _, status = _step({"specs/t.md": b"# T\n\n   para one here\n\nother text\n"}, v1, "c2")
    assert status[para.id] is Status.EDITED
    # its section and file changed below them only: their own text did not change
    assert sorted(i for i, s in status.items() if s is Status.CHILD_CHANGED) == sorted([para.parent, "SPT"])


def test_container_report_names_the_blanks_of_its_prefixes_e86() -> None:
    """The report says a container changed only by blanks and prefixes.

    Spec: R15, R16, R59, R63 (E86)
    """
    v1, _ = _step({"specs/t.md": b"# L\n\n- one\n- two\n"}, Store(), "c1")
    trees = {"specs/t.md": build_tree(b"# L\n\n- one\n\n- two\n")}
    changes = assign_ids(trees, v1, {"specs/t.md": "TYP"})
    assert "`>` prefixes and the blanks around them" in report_markdown(changes)


# --- definitions on lazy lines ---------------------------------------------------


def test_second_definition_on_a_lazy_line_has_its_node_r43() -> None:
    """A second definition on a lazy line of an item has its node.

    Spec: R43
    """
    tree = kinds(b"- [l]: /u\n[m]: /v\n\n- b\n")
    assert ("link_ref_def", b"[m]: /v") in tree
    assert run(b"- [l]: /u\n[m]: /v\n\n- b\n") == (
        "⟬TYP-1 begin⟭\n\n⟬TYP-3 begin⟭\n\n⟬TYP-4 begin⟭\n\n- ⟬TYP-2⟭\n\n  [l]: /u\n[m]: /v\n\n- b ⟬TYP-5⟭\n\n"
        "⟬TYP-4 end⟭\n\n⟬TYP-3 end⟭\n\n⟬TYP-1 end⟭\n"
    )


def test_lazy_definitions_belong_to_their_quote_e48() -> None:
    """Definitions on lazy lines belong to their quote.

    Spec: R43 (E48)
    """
    root = build_tree(b"> [l]: /u\n[m]: /v\n\nafter\n")
    quote = root.children[0]
    assert quote.kind is Kind.BLOCK_QUOTE
    assert [c.kind for c in quote.children] == [Kind.LINK_REF_DEF, Kind.LINK_REF_DEF]


def test_lazy_line_that_opens_a_block_alone_completes_the_definition_e49() -> None:
    """A lazy line that would open a block alone completes the definition.

    Spec: R43 (E49)
    """
    assert run(b"> [a]:\n:-\n") == "⟬TYP-1 begin⟭\n\n> [a]:\n:-\n\n⟬TYP-1 end⟭\n"
    assert kinds(b"2) [x]:\n===\n")[-1] == ("link_ref_def", b"[x]:\n===")


def test_definition_after_a_checkbox_and_a_tab_is_found_e31() -> None:
    """A definition after a checkbox and blanks is found.

    Spec: R35, R41, R43 (E31)
    """
    for source in (b"- [ ]    [x]: /u\n", b"- [ ]\t[x]:u\n"):
        assert Kind.LINK_REF_DEF in [n.kind for n in walk(build_tree(source))]
    # after "> \t" the definition is found, and joins the paragraph its lazy lines continue
    para = build_tree(b"> \t[x]: /u\nb\nc\n").children[0]
    assert para.kind is Kind.PARAGRAPH and para.own_text.startswith(b"> \t[x]: /u")


# --- paragraph before a table, header rows ---------------------------------------


def test_paragraph_ending_with_a_bare_marker_before_a_table_e52() -> None:
    """The ID goes at the end of an earlier line when the last is a bare marker.

    Spec: R44 (E52)
    """
    assert run(b"[l]: /u\n1.\na | b\n--|--\n") == (
        "[l]: /u ⟬TYP-1⟭\n1.\n\n⟬TYP-2 begin⟭\n\na ⟬TYP-3⟭ | b ⟬TYP-4⟭\n--|--\n\n⟬TYP-2 end⟭\n"
    )


def test_header_row_that_is_a_row_only_after_its_paragraph_gets_a_pipe_r46() -> None:
    """A header row that would become an item gets a leading pipe.

    Spec: R44, R46
    """
    assert run(b"a\n+\n-:\n| 1 |\n") == "⟬TYP-2 begin⟭\n\na ⟬TYP-1⟭\n|+ ⟬TYP-3⟭\n-:\n| 1 ⟬TYP-5⟭ | ⟬TYP-4⟭ |\n\n⟬TYP-2 end⟭\n"


def test_table_after_a_paragraph_of_definitions_reads_its_header_e66() -> None:
    """Definitions above a header row are part of the table's text.

    Spec: R44 (E66)
    """
    root = build_tree(b"[a]: /u\n---\n|-|\n")
    table = root.children[0]
    assert table.kind is Kind.TABLE and table.start == 0
    assert [c.own_text for c in table.children] == [b"---"]


# --- a moved rest of line keeps its column -----------------------------------------


def test_moved_rest_keeps_its_column_under_a_tight_quote_e35() -> None:
    """A moved rest of line keeps its column under `>` and ` > `.

    Spec: R37 (E35, E36)
    """
    assert run(b">- -\t<div>\n") == (
        ">- ⟬TYP-1⟭\n>\n>   -\t⟬TYP-2⟭\n>\n>        ⟬TYP-3 begin⟭\n>\n>       <div>\n>\n>        ⟬TYP-3 end⟭\n"
    )
    assert run(b" > 1. -\t# h\n") == " > 1. ⟬TYP-1⟭\n >\n >    -\t⟬TYP-2⟭\n >\n >      # h ⟬TYP-3⟭\n"
    assert run(b">7)     code\n") == ">7) ⟬TYP-1⟭\n>\n>    ⟬TYP-2 begin⟭\n>\n>        code\n>\n>    ⟬TYP-2 end⟭\n"


def test_html_block_indented_in_a_quote_on_a_marker_line_keeps_its_space_r37() -> None:
    """A moved HTML block keeps its indentation in the quote.

    Spec: R16, R37
    """
    source = b"- >  <div>\n  >\n  > b\n"
    assert "  >  <div>\n" in run(source)
    assert block_structure(annotate_text(source, "TYP")[0]) == block_structure(source)


def test_nested_item_that_its_line_move_would_make_a_task_item_r37() -> None:
    """A move that would make `[x]` a task item is not made.

    Spec: R36, R37
    """
    out = run(b"- - [x]\n |b\n    -|-\n")
    assert "[x] ⟬" not in out and "  - [x]\n" in out


def test_one_line_item_after_a_tab_is_probed_on_the_whole_file_e28() -> None:
    """An item text that its ID would make a checkbox, after a tab.

    Spec: R35, R37, R38 (E28)
    """
    assert run(b" -\t  [x]\n") == " -\t  ⟬TYP-1⟭\n\n      [x]\n"


# --- empty items ----------------------------------------------------------------


def test_empty_task_item_is_framed_at_its_block_e44() -> None:
    """An empty task item with no safe placement is framed at its block.

    Spec: R39, R40, R49 (E44)
    """
    assert run(b"- [ ] \n\n  b\n") == "⟬TYP-1 begin⟭\n\n- [ ] \n\n⟬TYP-1 end⟭\n\n  b ⟬TYP-2⟭\n"


def test_empty_item_id_never_joins_a_setext_heading_e42() -> None:
    """An empty item's ID never joins a setext heading on the next line.

    Spec: R39, R40 (E42)
    """
    assert run(b"+\n  t\n  =\n") == "+ ⟬TYP-1⟭\n\n  t ⟬TYP-2⟭\n  =\n"
    joined = "+ ⟬TYP-1⟭\n  t ⟬TYP-2⟭\n  =\n".encode()  # the placement the old probe took
    assert block_structure(joined) != block_structure(b"+\n  t\n  =\n")


# --- setext heading in a task item ----------------------------------------------------


def test_setext_heading_starting_with_hash_in_a_task_item_e33() -> None:
    """A setext heading starting with `#` in a task item keeps its line.

    Spec: R36 (E33)
    """
    root = build_tree(b"- [ ] # done\n  ---\n")
    heading = [n for n in walk(root) if n.kind is Kind.HEADING][0]
    assert heading.own_text == b"# done\n  ---" and heading.anchor == 12
    assert run(b"- [ ] # done\n  ---\n") == "- [ ] # done ⟬TYP-2⟭ ⟬TYP-1⟭\n  ---\n"
    assert "  -\n\n⟬TYP-1 end⟭" in run(b"- a\n- [ ] #\n  -\n")


# --- a ">" indented less than its item ---------------------------------------------


def test_gt_line_indented_less_than_its_item_is_not_blank_r47() -> None:
    """A `>` line indented less than its item is not in it.

    Spec: R47
    """
    out = run(b"-    > a\n    >\n     > > c\n")
    assert "    >\n     >\n     > ⟬TYP-3 end⟭" in out


# --- an unclosed HTML block after a tab ------------------------------------------------


def test_unclosed_html_block_after_a_tab_is_open_e62() -> None:
    """An unclosed HTML block after a tab is framed, and nothing else inserted.

    Spec: R48, U1 (E62)
    """
    assert cmark.html_block_is_open("\t<!-- note\n")
    source = b"- a\n\n  \t<!-- note\n"
    out = annotate_text(source, "TYP")[0]
    assert out.endswith("  \t<!-- note\n\n  ⟬TYP-2 end⟭\n".encode())  # nothing but the frame
    assert block_structure(out) == block_structure(source)


# --- the whole annotated file is checked -----------------------------------------------


def test_clashing_placements_are_framed_at_their_block_d39() -> None:
    """Placements that clash in the whole file are framed at their block.

    Spec: R50 (E66)
    """
    source = b"[a]: /u\n---\n|-|\n"
    root = build_tree(source)
    number_first_run(root, "TYP")
    first, _ = _annotate(source, root, False, [])
    assert block_structure(first) != block_structure(source)  # the header cell's ID alone
    assert run(source) == "⟬TYP-1 begin⟭\n\n⟬TYP-2 begin⟭\n\n[a]: /u\n---\n|-|\n\n⟬TYP-2 end⟭\n\n⟬TYP-1 end⟭\n"


# --- renames --------------------------------------------------------------------------------


def _corpus(n: int, words: str = "value") -> dict[str, bytes]:
    return {
        f"specs/f{i:02}.md": "".join(
            f"# File {i}\n\n" if k == 0 else f"Paragraph {k} of file {i} says the {words} number {k * i} is kept.\n\n"
            for k in range(25)
        ).encode()
        for i in range(n)
    }


def test_a_folder_moved_whole_is_detected_quickly_d40() -> None:
    """A folder moved whole is renamed, in seconds (one matching).

    Note: D40

    Spec: R58
    """
    v1, _ = _step(_corpus(40), Store(), "c1")
    moved = {p.replace("specs/", "specs/all/"): s for p, s in _corpus(40).items()}
    trees = {p: build_tree(s, p) for p, s in moved.items()}
    started = time.monotonic()
    renames = detect_renames(trees, v1)
    assert time.monotonic() - started < 10
    assert renames == {p.replace("specs/", "specs/all/"): p for p in _corpus(40)}


def test_a_wording_change_across_the_corpus_is_detected_quickly_d40() -> None:
    """A wording change across the corpus renames nothing, in seconds.

    Note: D40

    Spec: R58
    """
    v1, _ = _step(_corpus(40), Store(), "c1")
    trees = {p: build_tree(s, p) for p, s in _corpus(40, "amount").items()}
    started = time.monotonic()
    assert detect_renames(trees, v1) == {}
    assert time.monotonic() - started < 10


def test_a_stub_filled_in_keeps_its_prefix_e81() -> None:
    """A stub filled in keeps its prefix.

    Spec: R58 (E81)
    """
    v1, _ = _step({"specs/language/memory.md": b"# Memory\n\nTo be written.\n"}, Store(), "c1")
    filled = b"# Memory\n\nValues are reference counted and freed when the count reaches zero.\n"
    v2, status = _step({"specs/language/memory.md": filled}, v1, "c2")
    assert v2.files["specs/language/memory.md"].prefix == "MEM" and v2.retired_prefix_list == []
    assert status["MEM"] is not Status.NEW and status["MEM-1"] is not Status.RETIRED


def test_a_file_rewritten_in_place_keeps_its_prefix_r58() -> None:
    """A file rewritten in place keeps its prefix.

    Spec: R58
    """
    body = b"# Types\n\nOne a.\n\nTwo b.\n\nThree c.\n\nFour d.\n"
    v1, _ = _step({"specs/type-system.md": body}, Store(), "c1")
    rewritten = b"# Types\n\nOne a.\n\nZwei rewritten fully.\n\nDrei rewritten fully.\n\nVier rewritten fully.\n"
    v2, _ = _step({"specs/type-system.md": rewritten}, v1, "c2")
    assert v2.files["specs/type-system.md"].prefix == "TYP"


# --- containers without children keep their ID ---------------------------------------------------


def test_childless_quote_keeps_its_id_on_a_rebuild_e83() -> None:
    """A container without children keeps its ID on a rebuild.

    Spec: R56 (E83)
    """
    for source in (b">\n-->\n-\n10. ten\n", b"Intro.\n\n> ***\n\n# Notes\n\nText.\n", b"Intro.\n\n>\n\nText.\n"):
        v1, _ = _step({"specs/a.md": source}, Store(), "c1")
        _, status = _step({"specs/a.md": source}, v1, "c1")
        assert set(status.values()) == {Status.UNCHANGED}, source


def test_rebuild_of_a_childless_quote_is_byte_identical(tmp_path: Path) -> None:
    """A rebuild with a childless quote leaves every output as it was.

    Spec: R56, R62
    """
    f = SpecsRepo(tmp_path / "specs")
    f.write("specs/t.md", "Intro.\n\n> ***\n\n# Notes\n\nText.\n")
    f.commit()
    out = tmp_path / "norms"
    args = ["build", "--specs", str(f.root), "--out", str(out)]
    assert main(args) == 0
    before = snapshot(out)
    assert main(args) == 0
    assert snapshot(out) == before


# --- verify of the JSONL, delimiters, a corrupt JSONL ---------------------------------------------


def _built(tmp_path: Path) -> tuple[SpecsRepo, Path]:
    f = SpecsRepo(tmp_path / "specs")
    f.write("specs/lang/alpha.md", "# Alpha\n\nOne.\n\n- a\n- b\n")
    f.write("specs/lang/beta.md", "# Beta\n\nTwo.\n")
    f.commit()
    out = tmp_path / "norms"
    assert main(["build", "--specs", str(f.root), "--out", str(out)]) == 0
    return f, out


def _edit_jsonl(out: Path, edit) -> None:
    path = out / "data" / "tree.jsonl"
    lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    lines = edit(lines)
    path.write_text("".join(json.dumps(o, ensure_ascii=False) + "\n" for o in lines), encoding="utf-8")


def _verify(f: SpecsRepo, out: Path, capsys: pytest.CaptureFixture[str]) -> tuple[int, str]:
    code = main(["verify", "--specs", str(f.root), "--out", str(out)])
    return code, capsys.readouterr().err


def test_verify_sees_a_wrong_parent_r64(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verify sees a stored parent the rebuilt tree does not have.

    Spec: R34, R64
    """
    f, out = _built(tmp_path)

    def edit(lines):
        item = next(o for o in lines if o["type"] == "node" and o["kind"] == "item")
        item["parent"] = "BET-1"
        return lines

    _edit_jsonl(out, edit)
    code, err = _verify(f, out, capsys)
    assert code == 1 and "parent BET-1 in the JSONL" in err


def test_verify_sees_an_id_stored_twice_and_a_retired_prefix_in_use_r64(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify reports an ID stored twice and a retired prefix in use.

    Spec: R34, R64
    """
    f, out = _built(tmp_path)

    def edit(lines):
        node = next(o for o in lines if o["type"] == "node" and o["id"] == "ALP-3")
        lines.append(dict(node, status="retired"))
        lines[0]["retired_prefixes"] = ["BET"]
        return lines

    _edit_jsonl(out, edit)
    code, err = _verify(f, out, capsys)
    assert code == 1 and "ALP-3 is stored twice" in err and "prefix BET is retired but used" in err


def test_build_refuses_a_file_holding_a_delimiter_r19(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A spec file holding a delimiter is refused, naming its offset.

    Spec: R19, R34, R64
    """
    f = SpecsRepo(tmp_path / "specs")
    f.write("specs/t.md", "See ⟬TYP-1⟭ here.\n\nNext.\n")
    f.commit()
    out = tmp_path / "norms"
    assert main(["build", "--specs", str(f.root), "--out", str(out)]) == 2
    err = capsys.readouterr().err
    assert "specs/t.md" in err and "offset 4" in err
    assert not out.exists()


def test_a_corrupt_jsonl_is_a_problem_not_a_crash_r34(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A JSONL that is not JSON is refused by build and reported by verify.

    Spec: R34, R61, R64
    """
    f, out = _built(tmp_path)
    (out / "data" / "tree.jsonl").write_text("{not json\n", encoding="utf-8")
    code, err = _verify(f, out, capsys)
    assert code == 1 and "tree.jsonl:1" in err
    assert main(["build", "--specs", str(f.root), "--out", str(out)]) == 2
    assert "tree.jsonl:1" in capsys.readouterr().err
    with pytest.raises(StoreError):
        read_store(out / "data" / "tree.jsonl")


@pytest.mark.parametrize(
    "edit",
    [
        lambda o: dict(o, prefix="ab") if o["type"] == "file" else o,  # malformed prefix
        lambda o: {k: v for k, v in o.items() if k != "id"} if o["type"] == "node" else o,  # required field missing
        lambda o: dict(o, insertions=5) if o["type"] == "file" else o,  # wrong type
        lambda o: dict(o, start="0") if o["type"] == "node" else o,  # wrong type
        lambda o: dict(o, type="other") if o["type"] == "meta" else o,  # unknown line type
    ],
)
def test_an_unreadable_jsonl_line_is_refused_with_its_line_r34(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], edit
) -> None:
    """A line of the wrong type or form is refused, naming its line.

    Spec: R34, R61, R64
    """
    f, out = _built(tmp_path)
    _edit_jsonl(out, lambda lines: [edit(o) for o in lines])
    assert main(["build", "--specs", str(f.root), "--out", str(out)]) == 2
    assert "tree.jsonl:" in capsys.readouterr().err
    code, err = _verify(f, out, capsys)
    assert code == 1 and "tree.jsonl:" in err


def test_optional_jsonl_fields_take_their_defaults_r61(tmp_path: Path) -> None:
    """Absent optional fields take their defaults.

    Spec: R34, R61, R64
    """
    path = tmp_path / "tree.jsonl"
    path.write_text(
        '{"type":"meta"}\n{"path":"specs/x.md","prefix":"XXX","type":"file"}\n'
        '{"end":0,"file":"specs/x.md","id":"XXX","kind":"file","own_hash":"h","own_text":"",'
        '"start":0,"tree_hash":"t","type":"node"}\n',
        encoding="utf-8",
    )
    store = read_store(path)
    assert store.specs_commit == "" and store.files["specs/x.md"].sha256 == ""
    node = store.nodes[0]
    assert (node.parent, node.status, node.to_review, node.changed_since) == (None, "active", False, None)


def test_an_unknown_commit_has_a_message_r34(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A --commit git does not know has its own message.

    Spec: R34, R64
    """
    f, out = _built(tmp_path)
    assert main(["build", "--specs", str(f.root), "--commit", "nope", "--out", str(out)]) == 2
    assert "'nope' is not a commit of" in capsys.readouterr().err


def test_a_lone_cr_file_ends_every_inserted_line_with_cr_r52() -> None:
    """Inserted lines end with the file's line ending.

    Spec: R34, R52, R64
    """
    out, _ = annotate_text(b"```\rx\r```\r", "TYP", file_marker=True)
    assert out == "⟬TYP⟭\r\r⟬TYP-1 begin⟭\r\r```\rx\r```\r\r⟬TYP-1 end⟭\r".encode()
    out, _ = annotate_text(b"a\rb\n", "TYP", file_marker=False)
    assert out == "⟬TYP-1 begin⟭\n\na\rb\n\n⟬TYP-1 end⟭\n".encode()
