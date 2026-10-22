"""Tests of tree.py: AST -> norms tree.

The fixtures of the examples (test_examples.py) check the annotated
output; these tests check the tree itself: kinds, nesting, exact spans,
own text and hashes.

Note: D2

Spec: R5, R7, R8, R13, R16, R27, R31, R33
"""

from __future__ import annotations

import hashlib

from norms_generator.model import Kind, TreeNode
from norms_generator.tree import build_tree, inline_id_is_safe, walk

K = Kind


def shape(source: bytes) -> list[tuple[int, str, bytes]]:
    """(depth, kind, span text) of every node, in pre-order."""
    out: list[tuple[int, str, bytes]] = []

    def visit(node: TreeNode, depth: int) -> None:
        out.append((depth, node.kind.value, source[node.start : node.end]))
        for child in node.children:
            visit(child, depth + 1)

    visit(build_tree(source), 0)
    return out


def kinds(source: bytes) -> list[tuple[int, str]]:
    return [(d, k) for d, k, _ in shape(source)]


def node_at(source: bytes, text: bytes) -> TreeNode:
    """The first node whose span is exactly `text`."""
    root = build_tree(source)
    for node in walk(root):
        if source[node.start : node.end] == text:
            return node
    raise AssertionError(f"no node spans {text!r}")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --- kinds and nesting ---------------------------------------------------


def test_file_spans_the_whole_source() -> None:
    """A file's span is the whole file, from its first byte to its last.

    Spec: R16
    """
    src = b"a\n\nb\n\n\n"
    root = build_tree(src, "x.md")
    assert root.kind is K.FILE and (root.start, root.end) == (0, len(src))


def test_empty_file() -> None:
    """An empty file is a file node with no children and an empty own text.

    Spec: R16, R31
    """
    root = build_tree(b"")
    assert root.kind is K.FILE and root.children == []
    assert root.own_text == b"" and root.own_hash == sha(b"")


def test_sections_nest_by_level_e18() -> None:
    """Top-level headings open sections nested by level.

    Spec: R5, R27 (E18, E22)
    """
    src = b"intro\n\n# A\n\na\n\n## B\n\nb\n\n### C\n\n## D\n\n# E\n"
    assert kinds(src) == [
        (0, "file"),
        (1, "paragraph"),
        (1, "section"),
        (2, "heading"),
        (2, "paragraph"),
        (2, "section"),
        (3, "heading"),
        (3, "paragraph"),
        (3, "heading"),  # ### C: a section of its heading only
        (2, "heading"),  # ## D, collapsed too
        (1, "heading"),  # # E
    ]


def test_section_ends_with_its_last_block() -> None:
    """A section ends at its last child, before a thematic break.

    Spec: R16 (E18)
    """
    src = b"# A\n\nx\n\n---\n\n# B\n\ny\n"
    sec = build_tree(src).children[0]
    assert sec.kind is K.SECTION and src[sec.start : sec.end] == b"# A\n\nx"


def test_deeper_heading_first_then_shallower() -> None:
    """A section opens at any level 1 to 6, in any order.

    Spec: R5 (E22)
    """
    src = b"### A\n\na\n\n# B\n\nb\n"
    root = build_tree(src)
    assert [c.kind for c in root.children] == [K.SECTION, K.SECTION]


def test_headings_in_containers_open_no_section() -> None:
    """A heading inside a list item opens no section.

    Spec: R5 (E22)
    """
    src = b"- a\n\n  ## H\n\n  b\n- c\n"
    assert K.SECTION not in {n.kind for n in walk(build_tree(src))}


def test_thematic_breaks_and_blank_lines_have_no_node_r7() -> None:
    """Thematic breaks and blank lines have no node.

    Spec: R7, R31 (E1, E9)
    """
    src = b"a\n\n***\n\n---\n\nb\n"
    assert kinds(src) == [(0, "file"), (1, "paragraph"), (1, "paragraph")]
    root = build_tree(src)
    assert root.own_text == b"\n\n***\n\n---\n\n\n"


def test_setext_paragraph_then_dashes_is_a_heading() -> None:
    """A paragraph underlined with `---` is a setext heading, and opens a section.

    Spec: R1, R5 (E3)
    """
    src = b"Title\n---\n\nx\n"
    assert kinds(src)[1:3] == [(1, "section"), (2, "heading")]


def test_item_owns_its_first_paragraph_e12() -> None:
    """An item and its first paragraph are one node; later blocks are children.

    Spec: R33 (E12, E14)
    """
    src = b"- a\n  b\n\n  more\n- c\n"
    assert kinds(src) == [
        (0, "file"),
        (1, "list"),
        (2, "item"),
        (3, "paragraph"),  # "more": the item's second block
        (2, "item"),
    ]
    item = build_tree(src).children[0].children[0]
    assert src[item.anchor - 1 : item.anchor] == b"b"  # end of its own text
    assert item.own_text == b"- a\n  b\n\n  "


def test_item_without_paragraph_first() -> None:
    """An item whose first block is not a paragraph has its ID after the marker.

    Spec: R33, R35 (E25)
    """
    src = b"- ```\n  x\n  ```\n- b\n"
    item = build_tree(src).children[0].children[0]
    assert [c.kind for c in item.children] == [K.CODE_BLOCK]
    assert item.anchor == 2  # where its first block starts


def test_empty_item() -> None:
    """An empty item has no children and its ID right after its marker.

    Spec: R39
    """
    src = b"-\n- b\n"
    item = build_tree(src).children[0].children[0]
    assert item.children == [] and src[item.start : item.end] == b"-"
    assert item.anchor == 1


def test_ordered_flag_only_for_numbered_lists() -> None:
    """Only numbered lists are ordered.

    Spec: R8, R13
    """
    assert build_tree(b"1. a\n2. b\n").children[0].ordered
    assert build_tree(b"3) a\n4) b\n").children[0].ordered
    assert not build_tree(b"- a\n- b\n").children[0].ordered
    assert not build_tree(b"> a\n>\n> b\n").children[0].ordered


def test_table_e10() -> None:
    """A table's children are its header cells and body rows.

    Spec: R33 (E10, E54)
    """
    src = b"| a | b |\n|---|---|\n| c | d |\n| e |\n"
    assert shape(src) == [
        (0, "file", src),
        (1, "table", src[:-1]),
        (2, "table_cell", b" a "),
        (2, "table_cell", b" b "),
        (2, "table_row", b"| c | d |"),
        (3, "table_cell", b" c "),
        (3, "table_cell", b" d "),
        (2, "table_row", b"| e |"),  # the missing cell has no node
        (3, "table_cell", b" e "),
    ]
    table = build_tree(src).children[0]
    assert table.own_text == b"|||\n|---|---|\n\n"


def test_empty_cell_keeps_a_node() -> None:
    """An empty cell keeps a node, its ID right after its opening pipe.

    Spec: R33, R45 (E54)
    """
    src = b"| a | b |\n|---|---|\n|| x |\n"
    row = build_tree(src).children[0].children[2]
    first = row.children[0]
    assert first.start == first.end and first.anchor == first.start


def test_table_after_paragraph() -> None:
    """A paragraph that a table interrupts is a node of its own, before the table.

    Spec: R44
    """
    src = b"x\n| a |\n|---|\n| b |\n"
    assert shape(src)[1:4] == [
        (1, "paragraph", b"x"),
        (1, "table", b"| a |\n|---|\n| b |"),
        (2, "table_cell", b" a "),
    ]


def test_block_quote_and_nested_quote() -> None:
    """A quote holds its blocks; a nested quote of one paragraph is that paragraph.

    Spec: R27 (E11)
    """
    src = b"> a\n>\n> > b\n> > c\n"
    assert shape(src)[1:] == [
        (1, "block_quote", src[:-1]),
        (2, "paragraph", b"a"),
        (2, "paragraph", b"> b\n> > c"),  # a quote of one paragraph
    ]


def test_margins_e24() -> None:
    """Marker lines take the `> ` of the quotes and the item's indentation.

    Spec: R30 (E14, E24)
    """
    src = b"> - a\n>\n>   ```\n>   x\n>   ```\n> - b\n\n1. x\n\n   ~~~\n   y\n   ~~~\n"
    root = build_tree(src)
    codes = [n for n in walk(root) if n.kind is K.CODE_BLOCK]
    assert [c.margin for c in codes] == [b">   ", b"   "]


def test_nested_list_margin() -> None:
    """A nested list's marker lines take the item's content indentation.

    Spec: R27, R30 (E13)
    """
    src = b"- a\n  - b\n  - c\n"
    item = build_tree(src).children[0]  # a list of one item is the item
    inner = item.children[0]
    assert item.kind is K.ITEM and inner.kind is K.LIST and inner.margin == b"  "


# --- link reference definitions -----------------------------------------------


def test_link_ref_defs_in_gaps() -> None:
    """Each definition is a node of its own, found in the gaps between blocks.

    Note: D2

    Spec: R7, R41, R42, R43 (E7)
    """
    src = b"[a]: /u\n[b]: /v\n  'title'\n\nSee [a] and [b].\n"
    assert shape(src)[1:] == [
        (1, "link_ref_def", b"[a]: /u"),
        (1, "link_ref_def", b"[b]: /v\n  'title'"),
        (1, "paragraph", b"See [a] and [b]."),
    ]


def test_link_ref_def_before_paragraph_text() -> None:
    """A definition followed by text that parses the same is framed apart.

    Note: D2

    Spec: R7, R41, R42, R43 (E7)
    """
    src = b"[a]: /u\nText [a].\n"
    assert shape(src)[1:] == [(1, "link_ref_def", b"[a]: /u"), (1, "paragraph", b"Text [a].")]


def test_link_ref_def_at_the_end_of_an_item_and_a_quote() -> None:
    """The definitions of an item or quote are its children, in its span.

    Note: D2

    Spec: R7, R41, R42, R43
    """
    src = b"- See [a].\n\n  [a]: /u\n- b\n\n> x\n>\n> [b]: /v\n"
    root = build_tree(src)
    item = root.children[0].children[0]
    assert [src[c.start : c.end] for c in item.children] == [b"[a]: /u"]
    assert src[item.start : item.end] == b"- See [a].\n\n  [a]: /u"
    quote = root.children[1]
    assert quote.kind is K.BLOCK_QUOTE
    assert [c.kind for c in quote.children] == [K.PARAGRAPH, K.LINK_REF_DEF]


# --- collapse -----------------------------------------------------------------


def test_quote_of_one_paragraph_is_one_node_r27() -> None:
    """A quote of one paragraph is that paragraph, with the quote's span.

    Spec: R27 (E11)
    """
    src = b"> one line\n"
    (node,) = build_tree(src).children
    assert node.kind is K.PARAGRAPH and src[node.start : node.end] == b"> one line"
    assert node.own_text == b"> one line" and node.children == []


def test_list_of_one_item_is_one_node() -> None:
    """A list of one item is that item.

    Spec: R27 (E16)
    """
    src = b"- only\n"
    (node,) = build_tree(src).children
    assert node.kind is K.ITEM and node.children == []


def test_file_is_never_collapsed_e19() -> None:
    """The file is never collapsed.

    Spec: R27 (E19)
    """
    src = b"# Types\n\ntext\n"
    root = build_tree(src)
    assert root.kind is K.FILE and root.children[0].kind is K.SECTION


# --- anchors (where an inline ID goes) ---------------------------------


def test_anchors() -> None:
    """Where an inline ID goes.

    Spec: R18, R24 (E2, E3, E8)
    """
    src = b"## Numbers ##\n\nT\n=\n\nabc   \n\nx\ny\n"
    root = build_tree(src)
    nodes = list(walk(root))
    atx = [n for n in nodes if n.kind is K.HEADING][0]
    assert src[: atx.anchor] == b"## Numbers"  # before the closing sequence
    setext = [n for n in nodes if n.kind is K.HEADING][1]
    assert src[setext.anchor - 1 : setext.anchor + 1] == b"T\n"  # above the underline
    paras = [n for n in nodes if n.kind is K.PARAGRAPH]
    assert src[paras[0].start : paras[0].anchor] == b"abc"  # trailing blanks after the ID
    assert paras[1].anchor == -1  # several lines: framed
    assert all(n.anchor == -1 for n in nodes if n.kind in (K.SECTION, K.FILE))


def test_framed_kinds_have_no_anchor() -> None:
    """Code, HTML, definitions, tables, quotes and lists are framed.

    Spec: R24, R26 (E7)
    """
    src = b"```\nx\n```\n\n<div>\nx\n</div>\n\n[a]: /u\n\n| a |\n|---|\n\n> a\n>\n> b\n\n- a\n- b\n"
    for node in walk(build_tree(src)):
        if node.kind in (K.CODE_BLOCK, K.HTML_BLOCK, K.LINK_REF_DEF, K.TABLE, K.BLOCK_QUOTE, K.LIST):
            assert node.anchor == -1, node.kind


def test_inline_id_safety_e17() -> None:
    """An ID is never written inside an autolink.

    Spec: R24 (E17)
    """
    assert inline_id_is_safe(b"See www.github.github.com/gfm", 29)
    assert inline_id_is_safe(b"The old size was ~~32 bits~~", 28)
    assert inline_id_is_safe(b"Never write <script> in a page.", 31)
    assert inline_id_is_safe(b"a `b", 4)
    assert inline_id_is_safe(b"a\\", 2)  # a final backslash stays a backslash
    # In the middle of an autolink, the space would cut the URL.
    assert not inline_id_is_safe(b"www.x.com/ab", 10)


# --- own text and hashes -------------------------------------------------------


def test_own_text_and_tree_hash() -> None:
    """Own text is the span minus the children; the tree hash sorts them.

    Spec: R13, R16, R31
    """
    src = b"- a\n- b\n"
    lst = build_tree(src).children[0]
    a, b = lst.children
    assert lst.own_text == b"\n"
    assert a.own_text == b"- a" and a.own_hash == sha(b"- a")
    assert a.tree_hash == sha(a.own_hash.encode())
    kids = sorted([a.tree_hash, b.tree_hash])
    assert lst.tree_hash == sha((lst.own_hash + "".join(kids)).encode())


def test_bullet_order_does_not_change_the_tree_hash_r13() -> None:
    """Moving the items of a bulleted list changes no tree hash.

    Spec: R13, R16, R31
    """
    one = build_tree(b"- a\n- b\n").children[0]
    two = build_tree(b"- b\n- a\n").children[0]
    assert one.tree_hash == two.tree_hash


def test_numbered_order_changes_the_tree_hash_r8() -> None:
    """Reordering a numbered list changes its tree hash.

    Spec: R8, R13, R16, R31 (E75)
    """
    one = build_tree(b"1. a\n1. b\n").children[0]
    two = build_tree(b"1. b\n1. a\n").children[0]
    assert one.tree_hash != two.tree_hash


def test_one_more_space_changes_the_hash_r16() -> None:
    """One more space changes the own hash.

    Spec: R13, R16, R31
    """
    one = build_tree(b"Numbers are signed.\n").children[0]
    two = build_tree(b"Numbers are  signed.\n").children[0]
    assert one.own_hash != two.own_hash


def test_checking_a_task_changes_the_hash_e15() -> None:
    """Checking a task changes the item's own hash.

    Spec: R13, R16, R31 (E15)
    """
    one = build_tree(b"- [ ] a\n- [ ] b\n").children[0].children[0]
    two = build_tree(b"- [x] a\n- [ ] b\n").children[0].children[0]
    assert one.own_hash != two.own_hash


def test_child_change_changes_parent_tree_hash_only() -> None:
    """A changed child changes its parent's tree hash, not its own hash.

    Spec: R13, R16, R31
    """
    one = build_tree(b"# A\n\nx\n").children[0]
    two = build_tree(b"# A\n\ny\n").children[0]
    assert one.own_hash == two.own_hash and one.tree_hash != two.tree_hash


def test_spans_are_exact_bytes_utf8_and_crlf() -> None:
    """Spans are exact UTF-8 bytes and end before the line ending.

    Spec: R3, R13, R16, R31
    """
    src = "# Tipos é\r\n\r\nÜber ⟬\r\n".encode()
    root = build_tree(src)
    texts = [src[n.start : n.end] for n in walk(root)][1:]
    assert texts == ["# Tipos é\r\n\r\nÜber ⟬".encode(), "# Tipos é".encode(), "Über ⟬".encode()]


def test_every_byte_belongs_to_exactly_one_own_text() -> None:
    """The own texts of all nodes cover the file once.

    Spec: R13, R16, R31
    """
    src = (
        b"intro\n\n# A\n\n- a\n  - b\n  - c\n- d\n\n| x | y |\n|---|---|\n| 1 | 2 |\n\n"
        b"> q\n>\n> ```\n> c\n> ```\n\n[r]: /u\n\n---\n\n## B\n\ntext\n"
    )
    root = build_tree(src)
    assert sum(len(n.own_text) for n in walk(root)) == len(src)


# --- regressions of the review (fix1) --------------------------------------


def _code(source: bytes) -> TreeNode:
    return next(n for n in walk(build_tree(source)) if n.kind is K.CODE_BLOCK)


def test_fence_indentation_is_in_the_code_own_text_r16() -> None:
    """The opening fence's indentation decides what is stripped from the code.

    Spec: R16, R31
    """
    flush, indented = _code(b"```\n  x\n```\n"), _code(b"  ```\n  x\n```\n")
    assert indented.own_text == b"  ```\n  x\n```"
    assert flush.own_hash != indented.own_hash and flush.tree_hash != indented.tree_hash


def test_indented_code_own_text_keeps_its_indentation() -> None:
    """An indented code block's indentation is in its own text.

    Spec: R16
    """
    tab, spaces = _code(b"\tcode\n"), _code(b"    code\n")
    assert (tab.own_text, spaces.own_text) == (b"\tcode", b"    code")
    assert tab.own_hash != spaces.own_hash


def test_clean_example_indented_fence_changes_the_code_hash() -> None:
    """Indenting a fence changes the code block's hashes.

    Spec: R16, R31
    """
    v1 = b"Example:\n\n```clean\nfunctions:\n  integer f()\n```\n"
    v2 = b"Example:\n\n  ```clean\nfunctions:\n  integer f()\n```\n"
    assert _code(v1).tree_hash != _code(v2).tree_hash


def test_code_in_an_item_starts_at_the_item_content() -> None:
    """A block's span starts at its container's content column.

    Spec: R16 (E26)
    """
    src = b"-     code\n  more\n"
    code = _code(src)
    assert src[code.start : code.end] == b"    code"


def test_unclosed_fence_spans_its_blank_lines_e61() -> None:
    """An unclosed fence is framed and spans its trailing blank lines.

    Spec: R26, R48, U1 (E61, E63)
    """
    code = _code(b"```\nx\n\n\n")
    assert code.end == len(b"```\nx\n\n") and code.anchor == -1
    in_item = _code(b"- ~~~~\n  x\n\nnext\n")
    assert b"- ~~~~\n  x\n\nnext\n"[in_item.start : in_item.end] == b"~~~~\n  x\n"
    assert not hasattr(code, "close")


def test_item_of_a_link_ref_def_has_its_id_after_the_marker() -> None:
    """An item whose first block is a definition has its ID after its marker.

    Spec: R35 (E30)
    """
    src = b"- [a]: /u\n- b\n\n[a]\n"
    item = build_tree(src).children[0].children[0]
    assert item.kind is K.ITEM and item.anchor == 2
    assert [c.kind for c in item.children] == [K.LINK_REF_DEF]


def test_empty_task_item_has_no_link_ref_def() -> None:
    """An empty task item is an empty item, not a definition.

    Spec: R40
    """
    assert K.LINK_REF_DEF not in {n.kind for n in walk(build_tree(b"- [ ]  \n- b\n"))}


def test_item_text_like_a_checkbox_has_its_id_after_the_marker_e28() -> None:
    """`- [ ]` has its ID after the marker.

    Spec: R35 (E28)
    """
    item = build_tree(b"- [ ]\n- b\n").children[0].children[0]
    assert item.anchor == 2  # at the end, "- [ ] ⟬ID⟭" would be a task item


def test_tab_after_the_marker_gives_the_content_column_e38() -> None:
    """A tab after the marker reaches the content column 4.

    Spec: R38 (E38)
    """
    src = b"-\tone\n\n\t```\n\tcode\n\t```\n-\ttwo\n"
    item = build_tree(src).children[0].children[0]
    assert item.inner == b"    " and item.children[0].margin == b"    "
    assert build_tree(b"1.\tone\n\n\tx\n").children[0].inner == b"    "


# --- regressions of the review (fix2) --------------------------------------


def _cells(source: bytes) -> list[bytes]:
    return [source[n.start : n.end] for n in walk(build_tree(source)) if n.kind is K.TABLE_CELL]


def test_cells_are_the_bytes_between_their_pipes_r45() -> None:
    """Each cell is the bytes between its pipes, read from the source.

    cmark-gfm's body-row columns are wrong when the row starts otherwise than the header.

    Spec: R16, R45
    """
    assert _cells(b"| a | b |\n|---|---|\n   x | y |\n") == [b" a ", b" b ", b"x ", b" y "]
    assert _cells("﻿| a |\n|---|\n| 1 |\n".encode()) == [b" a ", b" 1 "]
    assert _cells(b'  "t"\n| a | b |\n|---|---|\n| 1 | 2 |\n') == [b" a ", b" b ", b" 1 ", b" 2 "]
    assert _cells(b"- [ ] box\n  a | b\n  -|-\n  c | d\n") == [b"a ", b" b", b"c ", b" d"]
    assert _cells(b"-\t| a | b |\n    |---|---|\n    | c | d |\n") == [b" a ", b" b ", b" c ", b" d "]
    assert _cells(b"   name | value\n---|---\nx | y\n") == [b"name ", b" value", b"x ", b" y"]
    assert _cells("Name | Value\n-----|------\n  café | 1\n".encode()) == [
        b"Name ", b" Value", "café ".encode(), b" 1"
    ]


def test_cells_split_on_unescaped_pipes_only() -> None:
    """Cells split on unescaped pipes only; excess cells are row text.

    Spec: R33, R45 (E54, E56)
    """
    assert _cells(b"| a | b |\n|---|---|\n| x \\| y | z |\n") == [b" a ", b" b ", b" x \\| y ", b" z "]
    assert _cells(b"| a | b |\n|---|---|\n| `x|y` |\n") == [b" a ", b" b ", b" `x", b"y` "]
    assert _cells(b"| a |\n|---|\n| b | extra\n") == [b" a ", b" b "]  # excess cells are text of the row


def test_row_whose_first_cell_would_start_a_block_gets_a_lead_pipe_e57() -> None:
    """A row whose first cell would start a block gets a leading `|`.

    Spec: R46 (E57)
    """
    root = build_tree(b"a | b\n--|--\n-|x\nc | d\n")
    leads = [n.lead for n in walk(root) if n.kind is K.TABLE_CELL]
    assert leads == [b"", b"", b"|", b"", b"", b""]


def test_definition_with_its_destination_below_is_one_node_d2() -> None:
    """A definition whose destination starts with `[` on the next line is one node.

    Spec: R42 (E47)
    """
    assert [k for _, k, _ in shape(b"[a]:\n[x]\n\n[t][a]\n")][1:] == ["link_ref_def", "paragraph"]
    assert [t for _, k, t in shape(b"[a]: /u\n[b]: /v\n") if k == "link_ref_def"] == [b"[a]: /u", b"[b]: /v"]


def test_definition_joins_the_text_it_cannot_be_framed_apart_from_e45() -> None:
    """A definition joins the text that framing it apart would change.

    Spec: R41 (E7, E45)
    """
    assert shape(b"[r]: /u\n    ind\n")[1:] == [(1, "paragraph", b"[r]: /u\n    ind")]
    assert shape(b"[r]: /u\n---\nSet\n---\n")[1:] == [(1, "heading", b"[r]: /u\n---\nSet\n---")]
    assert shape(b"[r]: /u\nfoo\n")[1:] == [(1, "link_ref_def", b"[r]: /u"), (1, "paragraph", b"foo")]


def test_definitions_before_a_hard_break_d2() -> None:
    """Definitions are found whatever precedes them.

    cmark-gfm reports inlines after a hard break on the line before: no line count from them.

    Note: D2

    Spec: R7 (E7)
    """
    assert [k for _, k in kinds(b"[x]\nfoo\\\nbar\n\n[x]: /u\n")][1:] == ["paragraph", "link_ref_def"]
    assert [t for _, k, t in shape(b"text\n\n[r]: /u\na\\\nb\nc\n") if k == "link_ref_def"] == [b"[r]: /u"]


def test_definition_like_text_before_a_table_is_a_paragraph() -> None:
    """A definition-like line that a table interrupts is a paragraph.

    Spec: R44 (E51)
    """
    assert [k for _, k in kinds(b"[r]: /u\ntext\n| a |\n|---|\n")][1:3] == ["paragraph", "table"]
    table = node_at(b"[r]: /u\ntext\n| a |\n|---|\n", b"| a |\n|---|")
    assert table.begin == 0  # its begin marker goes above the paragraph


def test_quote_ends_with_its_blank_lines_e11() -> None:
    """A quote's span ends with its trailing blank `>` lines.

    Spec: R16, R47 (E11, E59)
    """
    assert shape(b"> a\n>\n> b\n>\n\nnext\n")[1][2] == b"> a\n>\n> b\n>"
    assert shape(b"> > a\n> >\n> c\n")[2][2] == b"> a\n> >"


def test_empty_item_with_the_next_line_lazy_e40() -> None:
    """An empty item's ID keeps the next line out of the item.

    Spec: R39 (E40, E41)
    """
    item = build_tree(b"-\npara\n").children[0]
    assert item.kind is K.ITEM and (item.pad, item.brk) == (b" ", True)
    item = build_tree(b"-\n\n  - b\n").children[0].children[0]
    assert (item.pad, item.brk) == (b"  ", False)
    item = build_tree(b"-\n- b\n").children[0].children[0]
    assert (item.pad, item.brk) == (b" ", False)


def test_tab_after_a_quote_marker_is_one_column_of_the_quote_r30() -> None:
    """After `>`, a tab takes one column for the optional space.

    Spec: R30, R38 (E39)
    """
    item = build_tree(b">\t- a\n>\t  - b\n>\t  - c\n").children[0]
    assert item.kind is K.ITEM and item.inner == b">     "
