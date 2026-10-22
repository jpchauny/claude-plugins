"""Tests of norms_generator.cmark: the ctypes binding and its position rules.

Raw positions (parse_raw) pin what cmark-gfm 0.29.0.gfm.13 reports, as
checked empirically; repaired positions (parse) pin the rule of cmark.py:
a block ends at the last byte of its last line, never on a blank line,
never past its parent.

Note: D1

Spec: R16, R17
"""

from __future__ import annotations

import pytest

from norms_generator.cmark import (
    SourceLines,
    line_col_to_offset,
    node_span,
    parse,
    parse_raw,
    parse_str,
    version,
)
from norms_generator.model import AstNode


def pos(node: AstNode) -> tuple[int, int, int, int]:
    """(start_line, start_col, end_line, end_col) of `node`."""
    return node.start_line, node.start_col, node.end_line, node.end_col


def text(source: bytes, node: AstNode) -> bytes:
    """The bytes of `node` in `source`, from its repaired span."""
    start, end = node_span(node, line_col_to_offset(source))
    return source[start:end]


def blocks(node: AstNode) -> list[AstNode]:
    """`node` and its descendants in pre-order."""
    out = [node]
    for child in node.children:
        out.extend(blocks(child))
    return out


# --- binding --------------------------------------------------------------------


def test_version() -> None:
    """The parser is the cmark-gfm of GFM Spec 0.29.

    Spec: R3, R17
    """
    assert version().startswith("0.29.0.gfm.")


def test_parse_str_and_types() -> None:
    """The binding returns cmark-gfm's block types.

    Note: D1

    Spec: R17
    """
    doc = parse_str("# T\n\npara\n\n- a\n\n> q\n\n---\n\n    code\n\n<div>\n</div>\n")
    assert [n.type for n in doc.children] == [
        "heading",
        "paragraph",
        "list",
        "block_quote",
        "thematic_break",
        "code_block",
        "html_block",
    ]
    assert doc.type == "document"


def test_inlines_are_not_returned() -> None:
    """Inlines are not nodes.

    Spec: R17 (E17)
    """
    doc = parse(b"a *b* `c` [d](e) ~~f~~ www.x.com\n")
    assert doc.children[0].type == "paragraph"
    assert doc.children[0].children == []


def test_attributes() -> None:
    """The binding reads heading, list and code attributes.

    Note: D1

    Spec: R17
    """
    src = b"## H\n\n1. a\n2. b\n\n- x\n\n- y\n\n```clean  extra\nz\n```\n\n```   \nw\n```\n\n    i\n"
    doc = parse(src)
    heading, ordered, bullet, fenced, no_info, indented = doc.children
    assert heading.heading_level == 2 and not heading.setext
    assert (ordered.list_type, ordered.list_tight) == ("ordered", True)
    assert (bullet.list_type, bullet.list_tight) == ("bullet", False)
    assert (fenced.fence_info, fenced.literal) == ("clean  extra", "z\n")
    assert no_info.fence_info == ""  # fenced without info: "" ...
    assert (indented.fence_info, indented.literal) == (None, "i\n")  # ... indented: None


def test_html_literal() -> None:
    """The binding reads an HTML block's literal.

    Note: D1

    Spec: R17
    """
    doc = parse(b"<div>\n  <img>\n</div>\n")
    assert doc.children[0].literal == "<div>\n  <img>\n</div>\n"


def test_tasklist_is_item() -> None:
    """With the tasklist extension, a task item is an item.

    Spec: R17 (E15)
    """
    src = b"- [ ] t\n- [x] b\n- c\n"
    raw = parse_raw(src)
    items = raw.children[0].children
    assert [i.type for i in items] == ["item", "item", "item"]  # cmark says "tasklist"
    assert [i.task_checked for i in items] == [False, True, None]
    # the paragraph starts after the checkbox
    assert pos(items[0].children[0]) == (1, 7, 1, 7)


def test_table_header_is_table_row() -> None:
    """With the table extension, the header row is a row.

    Note: D1

    Spec: R17
    """
    src = b"| a |\n|---|\n| b |\n"
    rows = parse(src).children[0].children
    assert [r.type for r in rows] == ["table_row", "table_row"]  # cmark: "table_header"
    assert [r.is_header for r in rows] == [True, False]


def test_many_parses() -> None:
    """The binding frees cmark-gfm's memory over many parses.

    Note: D1

    Spec: R17
    """
    src = b"# T\n\n| a | b |\n|---|---|\n| c | d |\n" * 50
    for _ in range(200):
        assert len(parse(src).children) == 100


def test_extensions() -> None:
    # tagfilter, strikethrough and autolink do not change blocks; table and tasklist do
    """The table and tasklist extensions are attached.

    Spec: R17
    """
    assert parse(b"a | b\n--|--\n").children[0].type == "table"
    assert parse(b"- [ ] x\n").children[0].children[0].task_checked is False


# --- line_col_to_offset ----------------------------------------------------------


def test_line_col_to_offset() -> None:
    """Byte offsets from cmark-gfm's lines and columns, over UTF-8 and every line ending.

    Spec: R3, R16, R52
    """
    src = "é⟬\nab\r\ncd\re".encode()
    off = line_col_to_offset(src)
    assert off(1, 1) == 0
    assert off(1, 3) == 2  # "⟬" starts after the 2 bytes of "é"
    assert off(2, 1) == 6
    assert off(3, 1) == 10  # after "\r\n"
    assert off(4, 1) == 13  # after a lone "\r"
    assert off(2, 0) == 5  # col 0: the byte before the line (its EOL)
    lines = SourceLines(src)
    assert lines.count == 4
    assert [lines.content(i) for i in range(1, 5)] == ["é⟬".encode(), b"ab", b"cd", b"e"]
    assert SourceLines(b"a\n").count == 1
    assert SourceLines(b"").count == 1


# --- raw positions: what cmark-gfm reports ------------------------------------------


@pytest.mark.parametrize(
    ("src", "path", "expected"),
    [
        # paragraph: last byte of its last line, trailing spaces included
        (b"abc   \n\nx\n", [0], (1, 1, 1, 6)),
        (b"a\nb\n\n\n\nc\n", [0], (1, 1, 2, 1)),
        # ATX: end of the text, closing sequence and trailing blanks excluded
        (b"## Numbers ##\n", [0], (1, 1, 1, 10)),
        (b"# T   \n", [0], (1, 1, 1, 3)),
        (b"  ### V\n", [0], (1, 3, 1, 7)),
        # setext: end of underline; (L, 0) before a blank; next line's byte before a block
        (b"Numbers\n-------\n", [0], (1, 1, 2, 7)),
        (b"Whole\nnumbers\n===\n\nx\n", [0], (1, 1, 4, 0)),
        (b"T\n===\nx\n", [0], (1, 1, 3, 1)),
        # fenced code: closing fence included
        (b"```clean\nx = 1\n```\n\nafter\n", [0], (1, 1, 3, 3)),
        (b"```\nx\n```   \n", [0], (1, 1, 3, 6)),
        (b"1. a\n\n   ```\n   f\n   ```\n", [0, 0, 1], (3, 4, 5, 6)),
        # unclosed fence closed by its item: runs past the item onto "next"
        (b"- ```\n  x\n\nnext\n", [0, 0, 0], (1, 3, 4, 4)),
        # indented code: starts after the indentation; (L, 0) on the last trailing blank
        (b"    a\n\n    b\n\n\nx\n", [0], (1, 5, 5, 0)),
        (b"    a\n    b", [0], (1, 5, 2, 5)),
        (b">     a\n>\n>     b\n>\n> x\n", [0, 0], (1, 7, 4, 1)),
        # tabs are one byte; a partly consumed tab is the start
        (b"-\t\tcode\n", [0, 0, 0], (1, 3, 1, 7)),
        (b">\t  code\n", [0, 0], (1, 5, 1, 8)),
        # html block with a blank line inside: end reported inside the block
        (b"<!-- a\n\nb -->\n", [0], (1, 1, 2, 0)),
        (b"<div>\n  <img>\n</div>\n\nafter\n", [0], (1, 1, 3, 6)),
        # thematic break before a blank line
        (b"---\n\nx\n", [0], (1, 1, 2, 0)),
        # list and items: (L, 0) on a following blank line
        (b"- a\n\n- b\n\nx\n", [0], (1, 1, 4, 0)),
        (b"- a\n\n- b\n\nx\n", [0, 0], (1, 1, 2, 0)),
        (b"- a\n- bb\n  cont\n", [0, 1], (2, 1, 3, 6)),
        # item in a quote: ends on the ">" of a blank quote line
        (b"> - a\n>\n> - b\n", [0, 0, 0], (1, 3, 2, 1)),
        # block quote: trailing ">" line included; lazy line included
        (b"> a\n>\n\nb\n", [0], (1, 1, 2, 1)),
        (b"> a\nlazy\n", [0], (1, 1, 2, 4)),
        # link reference definitions are inside the paragraph's span
        (b"[a]: /u\nText\n", [0], (1, 1, 2, 4)),
        # multi-byte UTF-8: byte columns
        ("é ⟬x⟭\n".encode(), [0], (1, 1, 1, 10)),
        # UTF-8 BOM: three bytes of column
        ("﻿# T\n".encode(), [0], (1, 4, 1, 6)),
        # CRLF: "\r" excluded from the end
        (b"a\r\nb\r\n", [0], (1, 1, 2, 1)),
    ],
)
def test_raw_positions(src: bytes, path: list[int], expected: tuple[int, int, int, int]) -> None:
    """What cmark-gfm reports, before the spans are repaired.

    Note: D1

    Spec: R17
    """
    node = parse_raw(src)
    for i in path:
        node = node.children[i]
    assert pos(node) == expected


def test_raw_table() -> None:
    """What cmark-gfm reports for a table.

    Note: D1

    Spec: R17
    """
    src = b"| Type | Size |\n| --- | --- |\n| integer | 64 |\n| float | 64 |\n\nafter\n"
    table = parse_raw(src).children[0]
    assert pos(table) == (1, 1, 4, 14)
    header, row1, row2 = table.children
    assert pos(header) == (1, 1, 1, 15)
    assert [pos(c) for c in header.children] == [(1, 2, 1, 7), (1, 9, 1, 14)]  # " Type ", " Size "
    assert pos(row1) == (3, 1, 3, 16)
    assert [pos(c) for c in row2.children] == [(4, 2, 4, 8), (4, 10, 4, 13)]


def test_raw_table_cells() -> None:
    # no pipes: first cell from the row start; missing cell at (L, 0); "||" empty
    """What cmark-gfm reports for table cells.

    Note: D1

    Spec: R17
    """
    table = parse_raw(b"a | b\n--|--\nc | d\ne\n").children[0]
    assert [pos(c) for c in table.children[0].children] == [(1, 1, 1, 2), (1, 4, 1, 5)]
    assert [pos(c) for c in table.children[2].children] == [(4, 1, 4, 1), (4, 0, 4, 0)]
    table = parse_raw(b"| a | b |\n|---|---|\n|| x |\n").children[0]
    assert [pos(c) for c in table.children[1].children] == [(3, 2, 3, 1), (3, 3, 3, 5)]
    # row: trailing spaces and text past the last column included
    table = parse_raw(b"| a |  \n|---|\n| c | extra\n").children[0]
    assert [pos(r) for r in table.children] == [(1, 1, 1, 7), (3, 1, 3, 11)]
    # UTF-8 in cells: byte columns
    table = parse_raw("| é | ⟬ |\n|---|---|\n".encode()).children[0]
    assert [pos(c) for c in table.children[0].children] == [(1, 2, 1, 5), (1, 7, 1, 11)]
    # in a block quote: real columns
    table = parse_raw(b"> | a | b |\n> |---|---|\n> | c | d |\n").children[0].children[0]
    assert pos(table) == (1, 3, 3, 11)
    assert [pos(c) for c in table.children[1].children] == [(3, 4, 3, 6), (3, 8, 3, 10)]


def test_raw_table_after_paragraph_bug() -> None:
    """cmark-gfm's positions of a table that interrupts a paragraph.

    Note: D1

    Spec: R44
    """
    src = b"x\ny\n| a | b |\n|---|---|\n| b | c |\n"
    para, table = parse_raw(src).children
    assert pos(para) == (0, 0, 0, 0)
    assert pos(table) == (1, 1, 5, 9)  # starts at the paragraph's start
    header, row = table.children
    assert pos(header) == (1, 1, 1, 13)  # 13 = len(b"x\ny\n| a | b |")
    assert [pos(c) for c in header.children] == [(1, 6, 1, 8), (1, 10, 1, 12)]
    assert pos(row) == (5, 1, 5, 9)  # body rows are right


# --- repaired positions -------------------------------------------------------------


def test_atx_heading() -> None:
    """An ATX heading spans its line; its text ends before the closing sequence.

    Spec: R16, R18 (E2)
    """
    src = b"## Numbers ##   \n# T\n"
    h1, h2 = parse(src).children
    assert pos(h1) == (1, 1, 1, 16)
    assert (h1.text_end_line, h1.text_end_col) == (1, 10)
    assert text(src, h1) == b"## Numbers ##   "
    assert not h1.setext
    assert (h2.text_end_line, h2.text_end_col) == (2, 3)


@pytest.mark.parametrize(
    ("src", "expected", "text_end", "span"),
    [
        (b"Numbers\n-------\n", (1, 1, 2, 7), (1, 7), b"Numbers\n-------"),
        (b"Whole\nnumbers\n===\n\nx\n", (1, 1, 3, 3), (2, 7), b"Whole\nnumbers\n==="),
        (b"T\n===\nx\n", (1, 1, 2, 3), (1, 1), b"T\n==="),
        (b"T  \n===  \n\nx\n", (1, 1, 2, 5), (1, 1), b"T  \n===  "),
        (b"#5 bolts\n===\n", (1, 1, 2, 3), (1, 8), b"#5 bolts\n==="),
        (b"[a]: /u\nT\n===\n", (2, 1, 3, 3), (2, 1), b"T\n==="),
    ],
)
def test_setext_heading(
    src: bytes, expected: tuple[int, int, int, int], text_end: tuple[int, int], span: bytes
) -> None:
    """A setext heading spans its text and underline; its text ends above it.

    Spec: R16, R24 (E3)
    """
    heading = parse(src).children[0]
    assert heading.type == "heading" and heading.setext
    assert pos(heading) == expected
    assert (heading.text_end_line, heading.text_end_col) == text_end
    assert text(src, heading) == span


def test_setext_in_containers() -> None:
    """A setext heading in a quote or item spans its two lines.

    Spec: R16 (E3)
    """
    src = b"> T\n> ===\n> x\n"
    quote = parse(src).children[0]
    assert pos(quote.children[0]) == (1, 3, 2, 5)
    assert text(src, quote.children[0]) == b"T\n> ==="
    src = b"- T\n  ---\n"
    heading = parse(src).children[0].children[0].children[0]
    assert heading.setext and pos(heading) == (1, 3, 2, 5)


@pytest.mark.parametrize(
    ("src", "path", "span"),
    [
        (b"```clean\nx = 1\n```\n\nafter\n", [0], b"```clean\nx = 1\n```"),
        (b"```\nx\n```   \n", [0], b"```\nx\n```   "),
        (b"~~~ py\ncode\n\n~~~~\n", [0], b"~~~ py\ncode\n\n~~~~"),
        (b"```\n```\n", [0], b"```\n```"),
        (b"```\nx\n", [0], b"```\nx"),
        (b"```\nx\n\n\n", [0], b"```\nx"),
        (b"1. a\n\n   ```\n   f\n   ```\n\n2. b\n", [0, 0, 1], b"```\n   f\n   ```"),
        (b"> ```\n> x\n> ```\n", [0, 0], b"```\n> x\n> ```"),
        # unclosed fence closed by its item: ends with its last content line
        (b"- ```\n  x\n\nnext\n", [0, 0, 0], b"```\n  x"),
        # a fence outside the item does not close the item's fence
        (b"- ```\n  x\n```\n", [0, 0, 0], b"```\n  x"),
        (b"- ```\n  x\n```\n", [1], b"```"),
    ],
)
def test_fenced_code(src: bytes, path: list[int], span: bytes) -> None:
    """A fenced code block spans its fences; an unclosed one ends with its code.

    Spec: R16, R48 (E5, E63)
    """
    node = parse(src)
    for i in path:
        node = node.children[i]
    assert node.type == "code_block" and node.fence_info is not None
    assert text(src, node) == span


@pytest.mark.parametrize(
    ("src", "path", "expected", "span"),
    [
        (b"Run:\n\n    cln build\n    cln test\n\nafter\n", [1], (3, 5, 4, 12), b"cln build\n    cln test"),
        (b"    a\n\n    b\n\n\nx\n", [0], (1, 5, 3, 5), b"a\n\n    b"),
        (b">     a\n>\n>     b\n>\n> x\n", [0, 0], (1, 7, 3, 7), b"a\n>\n>     b"),
        (b"- a\n\n      code\n- b\n", [0, 0, 1], (3, 7, 3, 10), b"code"),
        (b"\tcode\n\t\tmore\n", [0], (1, 2, 2, 6), b"code\n\t\tmore"),
        (b"-\t\tcode\n", [0, 0, 0], (1, 3, 1, 7), b"\tcode"),
    ],
)
def test_indented_code(
    src: bytes, path: list[int], expected: tuple[int, int, int, int], span: bytes
) -> None:
    """An indented code block's span ends with its last code line.

    Spec: R16 (E4)
    """
    node = parse(src)
    for i in path:
        node = node.children[i]
    assert node.type == "code_block" and node.fence_info is None
    assert pos(node) == expected
    assert text(src, node) == span


@pytest.mark.parametrize(
    ("src", "span"),
    [
        (b"<div>\n  <img>\n</div>\n\nafter\n", b"<div>\n  <img>\n</div>"),
        (b"<!-- a\n\nb -->\n", b"<!-- a\n\nb -->"),
        (b"<div>\nx", b"<div>\nx"),
        (b"<div\n>\n", b"<div\n>"),
    ],
)
def test_html_block(src: bytes, span: bytes) -> None:
    """An HTML block spans its lines, an unclosed one too.

    Spec: R16, R48 (E6, E62)
    """
    node = parse(src).children[0]
    assert node.type == "html_block"
    assert text(src, node) == span


def test_thematic_break() -> None:
    """A thematic break spans its line.

    Spec: R16 (E1)
    """
    src = b"a\n\n---\n\n***\n"
    doc = parse(src)
    assert [pos(n) for n in doc.children[1:]] == [(3, 1, 3, 3), (5, 1, 5, 3)]


def test_paragraph() -> None:
    """A paragraph ends at the last byte of its last line, trailing spaces included.

    Spec: R16 (E8)
    """
    src = b"Hello world\nsecond line   \n\n\n\nNext\n"
    first, second = parse(src).children
    assert pos(first) == (1, 1, 2, 14)
    assert text(src, first) == b"Hello world\nsecond line   "
    assert pos(second) == (6, 1, 6, 4)


@pytest.mark.parametrize(
    ("src", "path", "expected", "span"),
    [
        (b"[a]: /u\nText\n", [0], (2, 1, 2, 4), b"Text"),
        (b"[a]: /u\n[b]:\n  /v\n  *Te*xt\nmore\n", [0], (4, 3, 5, 4), b"*Te*xt\nmore"),
        (b"> [a]: /u\n>  Text\n", [0, 0], (2, 4, 2, 7), b"Text"),
        (b"- [a]: /u\n  Text\n", [0, 0, 0], (2, 3, 2, 6), b"Text"),
        (b"[not a def] x\ny\n", [0], (1, 1, 2, 1), b"[not a def] x\ny"),
        (b"Text\n[a]: /u\n", [0], (1, 1, 2, 7), b"Text\n[a]: /u"),
    ],
)
def test_link_ref_defs_before_paragraph(
    src: bytes, path: list[int], expected: tuple[int, int, int, int], span: bytes
) -> None:
    """A paragraph starts after the definitions before it.

    Note: D2

    Spec: R7, R41 (E7)
    """
    node = parse(src)
    for i in path:
        node = node.children[i]
    assert node.type == "paragraph"
    assert pos(node) == expected
    assert text(src, node) == span


def test_link_ref_defs_only() -> None:
    """Definitions are not AST blocks: the generator finds them in the gaps.

    Note: D2

    Spec: R7
    """
    assert [n.type for n in parse(b"[a]: /u\n[b]: /v\n\nx\n").children] == ["paragraph"]


def test_lists() -> None:
    """A list and its items end at the last byte of their last lines.

    Spec: R16, R33 (E12)
    """
    src = b"- a\n- bb\n  cont\n\n  more\n- c\n\nafter\n"
    lst, after = parse(src).children
    assert pos(lst) == (1, 1, 6, 3)
    assert [pos(i) for i in lst.children] == [(1, 1, 1, 3), (2, 1, 5, 6), (6, 1, 6, 3)]
    assert text(src, lst.children[1]) == b"- bb\n  cont\n\n  more"
    assert pos(after) == (8, 1, 8, 5)


def test_nested_lists() -> None:
    """Nested lists end at their last item.

    Spec: R16 (E13)
    """
    src = b"- a\n  - b\n\n  - c\n\n- d\n"
    lst = parse(src).children[0]
    first = lst.children[0]
    assert pos(first) == (1, 1, 4, 5)
    assert pos(first.children[1]) == (2, 3, 4, 5)
    assert [pos(i) for i in first.children[1].children] == [(2, 3, 2, 5), (4, 3, 4, 5)]


def test_empty_items() -> None:
    """An empty item spans its marker.

    Spec: R16, R39
    """
    src = b"-\n\n- a\n"
    items = parse(src).children[0].children
    assert [pos(i) for i in items] == [(1, 1, 1, 1), (3, 1, 3, 3)]
    assert items[0].children == []


def test_block_quotes() -> None:
    """cmark-gfm ends a quote at its last child's line, before blank lines; tree.py adds its trailing blank `>` lines.

    Note: D1

    Spec: R16, R17, R47
    """
    src = b"> **Note:** x.\n>\n> Use.\n>\n\nafter\n"
    quote = parse(src).children[0]
    assert pos(quote) == (1, 1, 3, 6)
    assert [pos(p) for p in quote.children] == [(1, 3, 1, 14), (3, 3, 3, 6)]
    src = b"> - a\n>\n> - b\n>\n> c\n"
    quote = parse(src).children[0]
    lst = quote.children[0]
    assert [pos(i) for i in lst.children] == [(1, 3, 1, 5), (3, 3, 3, 5)]
    assert pos(lst) == (1, 3, 3, 5)
    src = b"> > a\n> > b\n>\n> c\n"
    inner = parse(src).children[0].children[0]
    assert pos(inner) == (1, 3, 2, 5)
    assert pos(parse(b"> a\nlazy\n").children[0]) == (1, 1, 2, 4)


def test_tables() -> None:
    """Table, row and cell spans; a cell is the bytes between its pipes.

    Spec: R16, R45 (E10)
    """
    src = b"| Type | Size |\n| --- | --- |\n| integer | 64 |\n| float | 64 |\n\nafter\n"
    table = parse(src).children[0]
    assert pos(table) == (1, 1, 4, 14)
    header, row1, _ = table.children
    assert header.is_header and not row1.is_header
    assert [text(src, c) for c in header.children] == [b" Type ", b" Size "]
    assert [text(src, c) for c in row1.children] == [b" integer ", b" 64 "]
    assert text(src, row1) == b"| integer | 64 |"


def test_table_missing_and_empty_cells() -> None:
    """A missing cell is past its row; an empty cell lies between its pipes.

    Spec: R33, R45 (E54)
    """
    src = b"| a | b |\n|---|---|\n|  | x |\n| y |\n||z|\n"
    rows = parse(src).children[0].children
    assert [text(src, c) for c in rows[1].children] == [b"  ", b" x "]
    # a missing cell: an empty span just past its row
    assert [pos(c) for c in rows[2].children] == [(4, 2, 4, 4), (4, 6, 4, 5)]
    assert [text(src, c) for c in rows[2].children] == [b" y ", b""]
    # "||": an empty cell, an empty span between the pipes
    assert [pos(c) for c in rows[3].children] == [(5, 2, 5, 1), (5, 3, 5, 3)]


def test_table_without_body_rows() -> None:
    """A table of a header row only ends at its delimiter row.

    Spec: R16, R33
    """
    src = b"| a |\n|---|\n# H\n"
    table = parse(src).children[0]
    assert pos(table) == (1, 1, 2, 5)


@pytest.mark.parametrize(
    ("src", "path", "para", "table", "cells"),
    [
        (
            b"x\ny\n| a | b |\n|---|---|\n| b | c |\n",
            [],
            b"x\ny",
            b"| a | b |\n|---|---|\n| b | c |",
            [b" a ", b" b "],
        ),
        (b"> x\n> | a |\n> |---|\n", [0], b"x", b"| a |\n> |---|", [b" a "]),
        (b"x   \n  | a |\n|---|\n", [], b"x   ", b"| a |\n|---|", [b" a "]),
        (b"x\n| a |   \n|---|\n", [], b"x", b"| a |   \n|---|", [b" a "]),
        (b"x\n\t| a |\n|---|\n", [], b"x", b"| a |\n|---|", [b" a "]),
        ("é\n| ⟬ | b |\n|---|---|\n".encode(), [], "é".encode(), "| ⟬ | b |\n|---|---|".encode(), [" ⟬ ".encode(), b" b "]),
        (b"x\na | b\n--|--\n", [], b"x", b"a | b\n--|--", [b"a ", b" b"]),
        (
            b"- x\n  | a | b |\n  |---|---|\n  | c | d |\n",
            [0, 0],
            b"x",
            b"| a | b |\n  |---|---|\n  | c | d |",
            [b" a ", b" b "],
        ),
    ],
)
def test_table_after_paragraph(
    src: bytes, path: list[int], para: bytes, table: bytes, cells: list[bytes]
) -> None:
    """A table interrupting a paragraph is split from it.

    Spec: R44 (E50, E51)
    """
    node = parse(src)
    for i in path:
        node = node.children[i]
    p, t = node.children
    assert (p.type, t.type) == ("paragraph", "table")
    assert text(src, p) == para
    assert text(src, t) == table
    header = t.children[0]
    assert header.is_header and header.start_line == p.end_line + 1
    assert [text(src, c) for c in header.children] == cells


def test_multibyte_and_tabs() -> None:
    """Columns count bytes, a tab as one.

    Spec: R3, R16, R38
    """
    src = "é ⟬x⟭\n\n-\tx\n\n>\tq\n".encode()
    para, lst, quote = parse(src).children
    assert pos(para) == (1, 1, 1, 10)
    assert pos(lst.children[0].children[0]) == (3, 3, 3, 3)
    assert pos(quote.children[0]) == (5, 3, 5, 3)


def test_line_endings() -> None:
    """Spans end before CRLF and lone-CR line endings.

    Spec: R16, R52
    """
    for src in (b"a\r\nb\r\n\r\nc\r\n", b"a\rb\r\rc\r"):
        first, second = parse(src).children
        assert pos(first) == (1, 1, 2, 1)
        assert text(src, first) in (b"a\r\nb", b"a\rb")
        assert pos(second) == (4, 1, 4, 1)


def test_document_span() -> None:
    """The document's span.

    Spec: R16
    """
    assert pos(parse(b"a\n\n")) == (1, 1, 1, 1)
    assert pos(parse(b"para")) == (1, 1, 1, 4)
    doc = parse(b"")
    assert node_span(doc, line_col_to_offset(b"")) == (0, 0)


def test_invariants() -> None:
    """Every block lies inside its parent, after its previous sibling, not on a blank line.

    Spec: R16
    """
    src = (
        b"# T ##\n\n[r]: /u\ntext\n> - a\n>\n> - b\n>     code\n\n"
        b"x\n| a | b |\n|---|---|\n| c |\n\n- ```\n  y\n\nz\n\n<!-- c\n\nd -->\n\nT\n---\n"
    )
    off = line_col_to_offset(src)

    def check(node: AstNode, lo: int, hi: int) -> None:
        start, end = node_span(node, off)
        assert lo <= start <= end <= hi, (node.type, pos(node))
        if node.type != "table_cell":
            assert end > start and src[end - 1 : end] not in (b"\n", b"\r"), node.type
        prev = start
        for child in node.children:
            child_start, child_end = node_span(child, off)
            assert child_start >= prev, child.type
            prev = child_end
            check(child, start, end)

    check(parse(src), 0, len(src))
    assert len(blocks(parse(src))) > 15


def test_nul_keeps_columns_in_source_bytes() -> None:
    """cmark-gfm turns NUL into U+FFFD (3 bytes); parse() keeps columns exact.

    Spec: R16
    """
    heading = parse(b"# a\x00b\n").children[0]
    assert (heading.text_end_line, heading.text_end_col) == (1, 5)  # the "b"


# --- regressions of the review (fix2) --------------------------------------


def test_setext_underline_before_a_definition() -> None:
    """A definition after the underline is no block: cmark-gfm still ends the heading on it.

    Spec: R16
    """
    heading = parse(b"===\n---\n[r]: /u\n").children[0]
    assert heading.setext and (heading.end_line, heading.text_end_line) == (2, 1)


def test_setext_heading_whose_text_looks_like_an_underline() -> None:
    """A setext heading after a definition, its text a `---` line.

    Spec: R16, R41
    """
    heading = parse(b"[r]: /u\n---\nSet\n---\n").children[0]
    assert (heading.start_line, heading.text_end_line, heading.end_line) == (2, 3, 4)


def test_link_ref_defs_end_where_the_lines_alone_are_only_definitions() -> None:
    """Inline positions after a hard break are on the line before: they cannot count lines.

    Note: D2

    Spec: R7 (E7)
    """
    para = parse(b"[x]\nfoo\\\nbar\n\n[x]: /u\n").children[0]
    assert (para.start_line, para.end_line) == (1, 3)
    para = parse(b"[r]: /u\na\\\nb\nc\n").children[0]
    assert (para.start_line, para.end_line) == (2, 4)
    para = parse(b"[a]: /u\n'title\nmore'\ntext\n").children[0]
    assert para.start_line == 4


def test_paragraph_before_a_table_keeps_its_definitions() -> None:
    """cmark-gfm renders "[r]: /u" as text there.

    Spec: R44 (E50, E51)
    """
    para, table = parse(b"[r]: /u\ntext\n| a |\n|---|\n").children
    assert para.before_table and (para.start_line, para.end_line) == (1, 2) and table.type == "table"
