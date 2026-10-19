"""Tests of annotate.py beyond the examples.

Every case is checked for the properties the fixtures check (test_examples):
strip() gives back the source, the insertions are markers and blank
lines only, markers are well formed and used once, marker lines
have their blank lines, and cmark-gfm parses the annotated text to
the same blocks as the source (structure.block_structure, which lets the
end marker of an unclosed code or HTML block fall inside it). Some
cases also pin the exact output.

Spec: R18, R23, R24, R25, R26, R27, R28, R29, R30, R35, R36, R37, R38, R39, R40, R41, R42, R43, R44, R45, R46, R47, R48, R49, R50, R51, R52
"""

from __future__ import annotations

import re

import cmarkgfm
import pytest

from norms_generator.annotate import annotate, annotate_text, marker, number_first_run, strip
from norms_generator.model import Insertion
from norms_generator.structure import block_structure
from norms_generator.tree import build_tree, walk
from test_examples import (
    MARKER_RE,
    check_blank_lines,
    check_markers,
)

CASES: dict[str, str] = {
    "quote of two paragraphs": "> a\n>\n> b\n",
    "quote with code": "> ```\n> x\n> ```\n>\n> after\n",
    "nested quote": "> > a\n> > b\n>\n> c\n",
    "lazy line in a quote": "> a\nb\n>\n> c\n",
    "list in a quote": "> - a\n> - b\n>\n> text\n",
    "code in an item in a quote": "> - a\n>\n>   ```\n>   x\n>   ```\n> - b\n",
    "html block": "<div>\nx\n</div>\n\npara\n",
    "html comment with a blank line": "<!-- a\n\nb -->\ntext\n",
    "link ref defs": "[a]: /u\n[b]: /v\n  \"title\"\n\nSee [a] and [b].\n",
    "link ref def before text": "[a]: /u\nText [a].\n",
    "link ref def in a quote": "> [a]: /u\n>\n> See [a].\n",
    "link ref def at the end of an item": "- See [a].\n\n  [a]: /u\n- b\n",
    "item starting with code": "- ```\n  x\n  ```\n- b\n",
    "item starting with a list": "- - a\n  - b\n- c\n",
    "item starting with a one-item list": "- - a\n- c\n",
    "empty item": "-\n- b\n",
    "empty first line then code": "-\n  ```\n  x\n  ```\n- b\n",
    "item starting with a quote": "- > q\n  > r\n- b\n",
    "item starting with a framed quote": "- > q\n  >\n  > r\n- b\n",
    "item starting with a heading": "- # H\n- b\n",
    "task items": "- [ ] a\n- [x] b\n  more\n",
    "ordered with parens": "1) a\n2) b\n",
    "wide item content": "1.  a\n\n    ```\n    x\n    ```\n2.  b\n",
    "two-digit numbers": "9. a\n10. b\n\n    ```\n    x\n    ```\n11. c\n",
    "indented code in an item": "- a\n\n      code\n- b\n",
    "short row": "| a | b |\n|---|---|\n| c |\n",
    "table without pipes": "a | b\n--|--\nc | d\n",
    "empty cells": "| a | b |\n|---|---|\n|| |\n",
    "header only": "| a | b |\n|---|---|\n",
    "table after a paragraph": "x\n| a |\n|---|\n| b |\n",
    "table in an item": "- t\n\n  | a |\n  |---|\n  | b |\n- c\n",
    "table in a quote": "> | a |\n> |---|\n> | b |\n>\n> x\n",
    "escaped pipe at the row end": "| a |\n|---|\n| b \\|\n",
    "excess cells": "| a |\n|---|\n| b | c |\n",
    "no final newline": "# T\n\npara",
    "no final newline after code": "```\nx\n```",
    "trailing blank lines": "a\nb\n\n\n",
    "leading blank lines": "\n\n# T\n\nx\n",
    "setext of two lines": "A\nB\n===\n\ntext\n",
    "setext then text": "Title\n-----\ntext\n",
    "empty atx heading": "#\n\nx\n",
    "hard line break": "a\\\nb\n",
    "trailing backslash": "a b\\\n",
    "trailing spaces": "abc   \n",
    "autolink": "See www.x.com\n",
    "email autolink": "Mail a@b.co.\n",
    "code span over two lines": "a `b\nc` d\n",
    "unmatched backtick": "a `b\n",
    "thematic breaks": "a\n\n***\n\n# H\n\n---\n\nb\n",
    "thematic break ends a section": "# A\n\nx\n\n---\n# B\n",
    "heading in an item": "- a\n\n  ## H\n\n  b\n",
    "levels out of order": "### A\n\n# B\n\n## C\n",
    "indented code": "    code\n\n    more\n",
    "unclosed raw html": "a <b\n",
    "link at the end": "a [b](c)\n",
    "image": "![x](y)\n",
    "only a thematic break": "---\n",
    "empty": "",
    "blank lines only": "\n\n",
    "lazy item line": "- a\nb\n- c\n",
    "quote in a quote": "> > a\n",
    "loose list": "- a\n\n- b\n",
    "code then list": "```\nx\n```\n- a\n- b\n",
    "list then thematic break": "- a\n- b\n\n---\n",
    "tilde fence in an item": "1. x\n   ~~~\n   y\n   ~~~\n",
    "tab after the marker": "-\ta\n-\tb\n",
    "heading interrupts a list": "- a\n- b\n# H\n\nx\n",
    "fence interrupts a paragraph": "text\n```\ncode\n```\n",
    "deep nesting": "- a\n  - b\n    - c\n    - d\n  - e\n- f\n",
    # regressions of the review (fix1)
    "unclosed fence": "```\nx\n",
    "unclosed fence with blank lines": "```\nx\n\n\n",
    "unclosed fence without a final newline": "```",
    "unclosed fence in an item": "- ```\n  x\n",
    "unclosed fence in an item, then text": "- ```\n  x\n\nnext\n",
    "unclosed fence in an item, then an item": "- ```\n  x\n\n- b\n",
    "unclosed fence in a section": "# H\n\n```\nx\n",
    "unclosed fence in a quote": "> ```\n> x\n>\n\nnext\n",
    "item of a link ref def": "- [a]: /u\n- b\n\n[a]\n",
    "item of a link ref def, cited": "- [x]: /u\n- b [x]\n",
    "ordered item of a link ref def": "1. [r]: /url\n",
    "nested item of a link ref def": "- 1. [r]: /url\n",
    "empty task item with trailing spaces": "- [ ]  \n- b\n",
    "item of indented code": "-     code\n  more\n- b\n",
    "ordered item of indented code": "1.     code\n\n   para\n2. b\n",
    "item of indented code after a tab": "-\t\tcode\n- b\n",
    "tab after the marker, then code": "-\tone\n\n\t```\n\tcode\n\t```\n-\ttwo\n",
    "tab after an ordered marker, then code": "1.\tone\n\n\t```\n\tcode\n\t```\n2.\ttwo\n",
    "tab after the marker, nested list": "-\tone\n\t-\ta\n\t-\tb\n-\ttwo\n",
    "tab after the marker, indented code": "-\tfoo\n\n\t\tbar\n",
    "tab-indented nested item with code": "- a\n\t- b\n\n\t\t```\n\t\tx\n\t\t```\n",
    "item text like a checkbox": "- [ ]\n",
    "item text like a checked box": "- [x]\n- b\n",
    "ordered item text like a checkbox": "1. [ ]\n2. b\n",
    "lone CR line endings": "# T\r\rpara one\rline two\r\r- a\r- b\r",
    "lone CR paragraphs": "a\rb\r\rc\r",
    "childless ordered item of a thematic break": "1. a\n2. ***\n",
    "two-digit item of a thematic break": "10. ***\n",
    "nested item text like a checkbox": "- - [ ] task\n",
    "NUL in a heading": "# a\x00b\n",
    "html block after a tab on the marker line": "-\t<div>\n",
    "nested item of a thematic break in a quote": "> -\t- <div>\n>\n>     - ***\n",
    "nested item of a heading in a quote": "> - ## Sub ##\n",
    "item of a heading in a quote in an item": "- > 1. ## Sub ##\n",
    "nested html block on the marker line": "1. a\n2. 1. b\n   2. <div>\n      html\n      </div>\n",
    "code of a lone quote marker": "    >\n",
    # regressions of the review (fix2)
    "unclosed html comment": "<!-- a\n\nb\n",
    "unclosed html comment in an item": "- <!-- a\n- b\n",
    "indented body row": "| a | b |\n|---|---|\n   x | y |\n",
    "table after an indented paragraph": '  "t"\n| a | b |\n|---|---|\n| 1 | 2 |\n',
    "indented body row without pipes": "a | b\n--|--\n  long text | y\n",
    "indented table": " a | b\n --|--\n  cell one | two\n",
    "indented header only": "   name | value\n---|---\nx | y\n",
    "indented body row with utf-8": "Name | Value\n-----|------\n  café | 1\n",
    "table in a task item": "- [ ] box\n  a | b\n  -|-\n  c | d\n",
    "table in a wide task item": "-   [ ] box\n    a | b\n    -|-\n    c | d\n",
    "table in a tab item": "-\t| a | b |\n    |---|---|\n    | c | d |\n",
    "table without pipes in a tab item": "-\ta | b\n    -|-\n    c | d\n",
    "first cell like a bullet": "a | b\n--|--\n-|x\n",
    "first cell like a plus": "a | b\n--|--\n+|x\n",
    "first cell like a number": "a | b\n--|--\n1.|x\n",
    "first cell like a paren number": "a | b\n--|--\n7)|x\n",
    "first cell like a heading": "a | b\n--|--\n##|x\n",
    "first cell like html": "a | b\n--|--\n<div|x\n",
    "header cell like a heading": "#|b\n-|-\nc|d\n",
    "body rows of dashes": "x | y\n-|-\n-|-\n",
    "body row of dashes after a row": "x | y\n-|-\nz | w\n-|-\n",
    "body row of dashes in a quote": "> x | y\n> -|-\n> -|-\n",
    "definition with its destination below": "[a]:\n[x]\n\n[t][a]\n",
    "definition then an indented line": "[r]: /u\n    ind\n",
    "definition then dashes": "[r]: /u\n---\n",
    "definition in an item then a lazy line": "- [r]: /u\nlazy\n",
    "definition then html": "[r]: /u\n<img src=x>\n",
    "definition then a setext heading": "[r]: /u\n---\nSet\n---\n",
    "definition in an item then strikethrough": "- [r]: /u\n~~s~~\n",
    "definition like text before a table": "[r]: /u\n| a |\n|---|\n",
    "definition like text and text before a table": "[r]: /u\ntext\n| a |\n|---|\n",
    "definition like text with a title before a table": "[r]: /u 'title\nmore'\ntext\n| a | b |\n|---|---|\n| c | d |\n",
    "brackets then a hard break": "[x]\nfoo\\\nbar\n\n[x]: /u\n",
    "links then a hard break": "[a] [b]\nc\\\nd\n",
    "link over two lines": '[link](http://x\n"title") rest\n',
    "definition then a hard break": "text\n\n[r]: /u\na\\\nb\nc\n",
    "empty item then a paragraph": "-\npara\n",
    "empty item with a space then a paragraph": "- \na\n",
    "empty item then a hard break": "-\na\\\n",
    "empty item then an underline": "-\n===\n",
    "empty item then a setext heading": "-\nSet\n===\n",
    "empty ordered item then text": "1.\nfoo bar\n",
    "empty item then an indented item": "-\n\n  - b\n",
    "quote ending with a blank line": "> a\n> b\n>\n",
    "quote of two paragraphs ending with a blank line": "> a\n>\n> b\n>\n\nnext\n",
    "list in a quote ending with a blank line": "> - a\n> - b\n>\n\nnext\n",
    "quote of a thematic break ending with a blank line": "> ***\n> ",
    "nested quote ending with a blank line": "> > a\n> >\n> c\n",
    "escape character": "esc \x1b[0m\n",
    "form feed": "a\x0cb\n",
    "escape character in a nested item": "- - a\x1b\n",
    "escape character in code": "# Colors\n\n```\nprintf \"\x1b[31mred\x1b[0m\"\n```\n",
    "tab after a quote marker, nested list": ">\t- a\n>\t  - b\n>\t  - c\n",
    "tab after a quote marker, code in an item": ">\t- a\n>\n>\t      code\n",
    "tab after a quote marker, html in an item": ">\t1. <!-- c -->\n",
    "quote without a space, item of indented code": ">7)     code\n",
    "definition on the marker line, then text": "- [a]: /u\n\n  text\n- c\n",
    "ordered definition on the marker line, then text": "1. [a]: /u\n   para\n2. c\n",
    "quoted definition on the marker line, then text": "> - [a]: /u\n>   text\n> - c\n",
    "nested list starting like a task": "- - [ ] t\n  - b\n",
    "ordered nested list starting like a task": "1. - [ ] t\n   - b\n",
    "setext underline then a definition": "===\n---\n[r]: /u\n",
    "setext heading like a definition": "[a]:\n===\n",
    "setext heading like a definition, then text": "[a]:\n---\n\ntext\n",
}


def check_insertions(insertions: list[Insertion]) -> None:
    """Only markers, spaces, line endings, ">" and "|" are inserted.

    strip() already shows that the rest of the text is untouched; this
    replaces test_examples.check_pure_insertion, whose diff can align an
    item marker "-" with the "-" of an ID.

    Spec: R23, R64
    """
    for ins in insertions:
        rest = MARKER_RE.sub("", ins.text.decode("utf-8"))
        assert set(rest) <= set(" \r\n>|"), f"inserted {ins.text!r}"


@pytest.mark.parametrize("name", sorted(CASES))
def test_properties(name: str) -> None:
    """Each case: strip() gives the source back and only allowed bytes are inserted,
    markers are well formed, marker lines have their blank lines, and the blocks are
    kept.

    Spec: R23, R29, R30, R64
    """
    source = CASES[name].encode()
    out, insertions = annotate_text(source, "TYP")
    assert strip(out, insertions) == source
    check_insertions(insertions)
    lines = out.replace(b"\r\n", b"\n").replace(b"\r", b"\n")  # the checks split on "\n"
    check_markers(lines, file_marker=True)
    check_blank_lines(lines)
    assert block_structure(out) == block_structure(source)


def run(text: str, file_marker: bool = False) -> str:
    return annotate_text(text.encode(), "TYP", file_marker=file_marker)[0].decode()


# --- exact outputs -------------------------------------------------------


def test_cell_id_before_row_id_at_the_same_place() -> None:
    """A row without a closing pipe: its last cell's ID, then the row's.

    Spec: R45 (E55)
    """
    assert run("a | b\n--|--\nc | d\n") == (
        "⟬TYP-1 begin⟭\n\na ⟬TYP-2⟭ | b ⟬TYP-3⟭\n--|--\nc ⟬TYP-5⟭ | d ⟬TYP-6⟭ | ⟬TYP-4⟭\n\n⟬TYP-1 end⟭\n"
    )


def test_short_row_gets_its_missing_cells() -> None:
    """The row ID lands past the last column, so it is not displayed.

    Spec: R45 (E54)
    """
    assert run("| a | b |\n|---|---|\n| c |\n") == (
        "⟬TYP-1 begin⟭\n\n| a ⟬TYP-2⟭ | b ⟬TYP-3⟭ |\n|---|---|\n| c ⟬TYP-5⟭ | | ⟬TYP-4⟭ |\n\n⟬TYP-1 end⟭\n"
    )


def test_quote_markers_take_the_quote_prefix_e24() -> None:
    """Marker lines inside a quote take its `> ` prefix; their blank lines are `>`.

    Spec: R30 (E24)
    """
    assert run("> > a\n> > b\n>\n> c\n") == (
        "⟬TYP-1 begin⟭\n\n"
        "> ⟬TYP-2 begin⟭\n>\n> > a\n> > b\n>\n> ⟬TYP-2 end⟭\n>\n> c ⟬TYP-3⟭\n\n"
        "⟬TYP-1 end⟭\n"
    )


def test_code_in_an_item_in_a_quote() -> None:
    """A code block in an item in a quote is framed, its marker lines taking `> ` and the
    item's content indentation.

    Spec: R26, R30 (E14, E24)
    """
    assert run("> - a\n>\n>   ```\n>   x\n>   ```\n> - b\n") == (
        "⟬TYP-1 begin⟭\n\n"
        "> - a ⟬TYP-2⟭\n>\n>   ⟬TYP-3 begin⟭\n>\n>   ```\n>   x\n>   ```\n>\n>   ⟬TYP-3 end⟭\n>\n> - b ⟬TYP-4⟭\n\n"
        "⟬TYP-1 end⟭\n"
    )


def test_item_starting_with_code() -> None:
    """The item's ID right after its marker; the code moves to its own line.

    Spec: R35 (E25)
    """
    assert run("- ```\n  x\n  ```\n- b\n") == (
        "⟬TYP-1 begin⟭\n\n- ⟬TYP-2⟭\n\n  ⟬TYP-3 begin⟭\n\n  ```\n  x\n  ```\n\n  ⟬TYP-3 end⟭\n\n- b ⟬TYP-4⟭\n\n⟬TYP-1 end⟭\n"
    )


def test_wide_item_content_indentation_r30() -> None:
    """Marker lines take the item's content indentation, four spaces for `10. `.

    Spec: R30 (E14)
    """
    assert run("10. a\n\n    ```\n    x\n    ```\n11. b\n") == (
        "⟬TYP-1 begin⟭\n\n10. a ⟬TYP-2⟭\n\n    ⟬TYP-3 begin⟭\n\n    ```\n    x\n    ```\n\n    ⟬TYP-3 end⟭\n\n11. b ⟬TYP-4⟭\n\n⟬TYP-1 end⟭\n"
    )


def test_link_ref_def_framed_e7() -> None:
    """A definition is framed, and the text after it keeps its own ID.

    Spec: R24, R41 (E7)
    """
    assert run("[a]: /u\nText [a].\n") == "⟬TYP-1 begin⟭\n\n[a]: /u\n\n⟬TYP-1 end⟭\n\nText [a]. ⟬TYP-2⟭\n"


def test_sections_close_innermost_first_at_the_end_of_the_file() -> None:
    """At the end of the file, every open section closes, innermost first.

    Spec: R30 (E18)
    """
    assert run("# A\n\n## B\n\nx") == (
        "⟬TYP-1 begin⟭\n\n# A ⟬TYP-2⟭\n\n⟬TYP-3 begin⟭\n\n## B ⟬TYP-4⟭\n\nx ⟬TYP-5⟭\n\n⟬TYP-3 end⟭\n\n⟬TYP-1 end⟭\n"
    )


def test_trailing_spaces_stay_after_the_id() -> None:
    """The ID goes before the line's trailing spaces, which stay after it.

    Spec: R18
    """
    assert run("abc   \n") == "abc ⟬TYP-1⟭   \n"


def test_crlf_line_endings_are_kept() -> None:
    """Inserted lines end with the file's line ending, `\\r\\n` here.

    Spec: R52
    """
    out = run("# T\r\n\r\na\r\nb\r\n", file_marker=True)
    assert out == (
        "⟬TYP⟭\r\n\r\n⟬TYP-1 begin⟭\r\n\r\n# T ⟬TYP-2⟭\r\n\r\n⟬TYP-3 begin⟭\r\n\r\na\r\nb\r\n\r\n"
        "⟬TYP-3 end⟭\r\n\r\n⟬TYP-1 end⟭\r\n"
    )


def test_file_marker_after_a_bom_r29() -> None:
    """The file marker goes after a BOM.

    Spec: R29, R52
    """
    source = "\ufeff# T\n".encode()
    out, insertions = annotate_text(source, "TYP")
    assert out == "\ufeff⟬TYP⟭\n\n# T ⟬TYP-1⟭\n".encode()
    assert strip(out, insertions) == source
    assert block_structure(out) == block_structure(source)


def test_file_marker_on_a_blank_first_line() -> None:
    """A blank first line is reused as the file marker's blank line.

    Spec: R29 (E23)
    """
    assert run("\nx\n", file_marker=True) == "⟬TYP⟭\n\nx ⟬TYP-1⟭\n"


def test_empty_file_has_only_its_marker() -> None:
    """An empty file holds only its marker and a line ending.

    Spec: R29
    """
    assert run("", file_marker=True) == "⟬TYP⟭\n"


# --- numbering, insertions, strip ---------------------------------------


def test_number_first_run_is_pre_order_r9() -> None:
    """On a first run, a file's nodes are numbered 1, 2, ... in pre-order; the file is its bare
    prefix.

    Spec: R9
    """
    root = build_tree(b"# A\n\n- x\n- y\n")
    number_first_run(root, "ABC")
    assert [n.id for n in walk(root)] == ["ABC", "ABC-1", "ABC-2", "ABC-3", "ABC-4", "ABC-5"]


def test_annotate_uses_the_given_ids() -> None:
    """The annotated file writes in the IDs stored for the tree, even one whose prefix is
    another file's.

    Spec: R11, R23
    """
    source = b"a\n\nb\n"
    root = build_tree(source)
    root.id = "FOO"
    root.children[0].id, root.children[1].id = "BAR-7", "FOO-30"
    out, _ = annotate(source, root)
    assert out == "⟬FOO⟭\n\na ⟬BAR-7⟭\n\nb ⟬FOO-30⟭\n".encode()


def test_annotate_needs_every_id() -> None:
    """Every node to annotate must have its ID.

    Spec: R7, R23
    """
    with pytest.raises(ValueError):
        annotate(b"a\n", build_tree(b"a\n"))


def test_one_insertion_per_offset_in_order() -> None:
    """One insertion record per offset, in ascending order of offset.

    Spec: R23, R61
    """
    _, insertions = annotate_text(b"# A\n\n## B\n\nx\n\n# C\n", "TYP")
    offsets = [i.offset for i in insertions]
    assert offsets == sorted(set(offsets))


def test_strip_rejects_insertions_that_do_not_match() -> None:
    """Stripping checks that each recorded insertion is in the annotated text.

    Spec: R23, R64
    """
    with pytest.raises(ValueError):
        strip(b"abc", [Insertion(1, b"X")])


def test_marker_shapes_r25() -> None:
    """The three markers and the file marker match the pattern every marker matches.

    Spec: R25, R29
    """
    assert marker("TYP-3") == "⟬TYP-3⟭".encode()
    assert marker("TYP-3", "begin") == "⟬TYP-3 begin⟭".encode()
    assert MARKER_RE.fullmatch(marker("TYP", "").decode())


# --- regressions of the review (fix1): exact outputs -----------------------


def test_unclosed_fence_is_framed_and_left_open_e61() -> None:
    """Begin marker before, end marker after, nothing else: no closing fence.

    Spec: R48, U1 (E61, E63)
    """
    assert run("```\nx\n") == "⟬TYP-1 begin⟭\n\n```\nx\n\n⟬TYP-1 end⟭\n"
    assert run("```\nx\n\n\n") == "⟬TYP-1 begin⟭\n\n```\nx\n\n\n⟬TYP-1 end⟭\n"
    assert run("- ~~~~\n  x\n\nnext\n") == (
        "- ⟬TYP-1⟭\n\n  ⟬TYP-2 begin⟭\n\n  ~~~~\n  x\n\n  ⟬TYP-2 end⟭\n\nnext ⟬TYP-3⟭\n"
    )


@pytest.mark.parametrize(
    "source", ["```\nx\n", "- ```\n  x\n\n- b\n", "<!-- a\n\nb\n", "- <!-- a\n- b\n", "# H\n\n~~~\nx"]
)
def test_unclosed_block_gets_only_its_markers_r48(source: str) -> None:
    """Every insertion is a marker line or a blank line; the end marker lands inside the block.

    Spec: R48, U1 (E61, E62, E63)
    """
    out, insertions = annotate_text(source.encode(), "TYP")
    for ins in insertions:
        assert not re.search(r"[`~]|-->", ins.text.decode()), ins.text
    assert strip(out, insertions) == source.encode()
    assert block_structure(out) == block_structure(source.encode())


def test_item_of_a_link_ref_def_keeps_the_definition_e30() -> None:
    """An item whose first block is a definition has its ID after its marker; the definition,
    framed, still resolves.

    Spec: R35 (E30)
    """
    out = run("- [a]: /u\n- b\n\n[a]\n")
    assert out.startswith("⟬TYP-1 begin⟭\n\n- ⟬TYP-2⟭\n\n  ⟬TYP-3 begin⟭\n\n  [a]: /u\n\n  ⟬TYP-3 end⟭\n")
    html = cmarkgfm.github_flavored_markdown_to_html(out)
    assert '<a href="/u">a</a>' in html


def test_item_of_indented_code_moves_the_code_whole() -> None:
    """The indented code moves to a line of its own and keeps its column.

    Spec: R35, R37 (E26)
    """
    assert run("-     code\n  more\n- b\n") == (
        "⟬TYP-1 begin⟭\n\n- ⟬TYP-2⟭\n\n  ⟬TYP-3 begin⟭\n\n      code\n\n  ⟬TYP-3 end⟭\n\n"
        "  more ⟬TYP-4⟭\n- b ⟬TYP-5⟭\n\n⟬TYP-1 end⟭\n"
    )


def test_tab_after_the_marker_indents_markers_to_the_content_r30() -> None:
    """After `-\\t`, marker lines take spaces to the virtual column 4.

    Spec: R30, R38 (E38)
    """
    out = run("-\tone\n\n\t```\n\tcode\n\t```\n-\ttwo\n")
    assert "\n    ⟬TYP-3 begin⟭\n" in out and "\n    ⟬TYP-3 end⟭\n" in out


def test_item_text_like_a_checkbox_does_not_become_a_task_e28() -> None:
    """`- [ ]` takes its ID after the marker, so it does not become a task item.

    Spec: R35 (E28)
    """
    assert run("- [ ]\n") == "- ⟬TYP-1⟭\n\n  [ ]\n"


def test_nested_item_like_a_task_keeps_its_line() -> None:
    """A marker line that cannot be split keeps its line, the deeper ID first.

    Spec: R36 (E32)
    """
    assert run("- - [ ] task\n") == "- - [ ] task ⟬TYP-2⟭ ⟬TYP-1⟭\n"


def test_childless_ordered_item_moves_its_rest_to_its_content_column() -> None:
    """An item whose only content is a thematic break has its ID after the marker; the break moves
    to the content column.

    Spec: R35 (E27)
    """
    assert run("1. a\n2. ***\n") == (
        "⟬TYP-1 begin⟭\n\n1. a ⟬TYP-2⟭\n2. ⟬TYP-3⟭\n\n   ***\n\n⟬TYP-1 end⟭\n"
    )


def test_lone_cr_line_endings_keep_their_blank_lines_r30() -> None:
    """In a lone-CR file, inserted lines end with `\\r`; marker lines keep their blanks.

    Spec: R30, R52
    """
    assert run("a\rb\r\rc\r") == "⟬TYP-1 begin⟭\r\ra\rb\r\r⟬TYP-1 end⟭\r\rc ⟬TYP-2⟭\r"


def test_nul_keeps_the_id_on_its_line() -> None:
    """A heading holding NUL has its ID at the end of its text.

    Spec: R18, R24
    """
    source = b"# a\x00b\n"
    out, insertions = annotate_text(source, "TYP")
    assert out == "⟬TYP⟭\n\n# a\x00b ⟬TYP-1⟭\n".encode()
    assert strip(out, insertions) == source


# --- regressions of the review (fix2): exact outputs -----------------------


def test_body_row_cells_are_read_from_the_source_r45() -> None:
    """An indented row, or a row in a task or tab item: each ID at the end of its cell (rows without end pipes; after a BOM).

    Spec: R29, R45 (E55)
    """
    assert run("| a | b |\n|---|---|\n   x | y |\n") == (
        "⟬TYP-1 begin⟭\n\n| a ⟬TYP-2⟭ | b ⟬TYP-3⟭ |\n|---|---|\n   x ⟬TYP-5⟭ | y ⟬TYP-6⟭ | ⟬TYP-4⟭ |\n\n⟬TYP-1 end⟭\n"
    )
    assert run("- [ ] box\n  a | b\n  -|-\n  c | d\n").endswith(
        "  c ⟬TYP-6⟭ | d ⟬TYP-7⟭ | ⟬TYP-5⟭\n\n  ⟬TYP-2 end⟭\n"
    )
    assert "    | c ⟬TYP-6⟭ | d ⟬TYP-7⟭ | ⟬TYP-5⟭ |\n" in run("-\t| a | b |\n    |---|---|\n    | c | d |\n")
    out = annotate_text("﻿| a |\n|---|\n| 1 |\n".encode(), "TYP")[0].decode()
    assert out == "﻿⟬TYP⟭\n\n⟬TYP-1 begin⟭\n\n| a ⟬TYP-2⟭ |\n|---|\n| 1 ⟬TYP-4⟭ | ⟬TYP-3⟭ |\n\n⟬TYP-1 end⟭\n"


def test_a_pipe_opens_a_row_whose_first_cell_would_start_a_block_e57() -> None:
    """A row whose first cell would start a block gets a leading `|`.

    Spec: R46 (E57, E58)
    """
    assert run("a | b\n--|--\n-|x\n").splitlines()[4] == "|- ⟬TYP-5⟭|x ⟬TYP-6⟭ | ⟬TYP-4⟭"
    assert run("#|b\n-|-\nc|d\n").splitlines()[2] == "|# ⟬TYP-2⟭|b ⟬TYP-3⟭"
    assert run("a | b\n--|--\nc | d\n").splitlines()[4] == "c ⟬TYP-5⟭ | d ⟬TYP-6⟭ | ⟬TYP-4⟭"


def test_empty_item_id_leaves_the_next_line_out_of_the_item_r39() -> None:
    """An empty item's ID is probed with a blank line, then 2 to 4 blanks, so the next line stays
    out of the item.

    Spec: R39 (E40, E41)
    """
    assert run("-\npara\n") == "- ⟬TYP-1⟭\n\npara ⟬TYP-2⟭\n"
    assert run("1.\nfoo bar\n") == "1. ⟬TYP-1⟭\n\nfoo bar ⟬TYP-2⟭\n"
    assert run("-\n\n  - b\n") == "⟬TYP-1 begin⟭\n\n-  ⟬TYP-2⟭\n\n  - b ⟬TYP-3⟭\n\n⟬TYP-1 end⟭\n"
    assert run("-\n- b\n") == "⟬TYP-1 begin⟭\n\n- ⟬TYP-2⟭\n- b ⟬TYP-3⟭\n\n⟬TYP-1 end⟭\n"


def test_definition_with_its_destination_below_is_one_node_e47() -> None:
    """A definition whose destination starts with `[` on the next line is one node.

    Spec: R42 (E47)
    """
    assert run("[a]:\n[x]\n\n[t][a]\n") == "⟬TYP-1 begin⟭\n\n[a]:\n[x]\n\n⟬TYP-1 end⟭\n\n[t][a] ⟬TYP-2⟭\n"


def test_definition_that_cannot_be_framed_apart_starts_its_block_e45() -> None:
    """A definition joins the text that framing it apart would change.

    Text that parses the same keeps it apart.

    Spec: R41 (E7, E45, E46)
    """
    assert run("[r]: /u\n    ind\n") == "⟬TYP-1 begin⟭\n\n[r]: /u\n    ind\n\n⟬TYP-1 end⟭\n"
    assert run("- [r]: /u\nlazy\n") == "- [r]: /u\nlazy ⟬TYP-1⟭\n"
    assert run("[r]: /u\n---\nSet\n---\n") == "[r]: /u\n---\nSet ⟬TYP-1⟭\n---\n"
    # text that does not change keeps the definition apart
    assert run("[r]: /u\nfoo\n") == "⟬TYP-1 begin⟭\n\n[r]: /u\n\n⟬TYP-1 end⟭\n\nfoo ⟬TYP-2⟭\n"


def test_definition_like_text_stays_right_above_its_table_r44() -> None:
    """A paragraph that a table interrupts stays text, with the begin marker between them or above
    the paragraph.

    Spec: R44 (E50, E51)
    """
    assert run("[r]: /u\n| a |\n|---|\n") == (
        "[r]: /u ⟬TYP-1⟭\n\n⟬TYP-2 begin⟭\n\n| a ⟬TYP-3⟭ |\n|---|\n\n⟬TYP-2 end⟭\n"
    )
    assert run("[r]: /u\ntext\n| a |\n|---|\n") == (
        "⟬TYP-2 begin⟭\n\n[r]: /u\ntext ⟬TYP-1⟭\n| a ⟬TYP-3⟭ |\n|---|\n\n⟬TYP-2 end⟭\n"
    )


def test_quote_end_marker_follows_its_blank_lines_e11() -> None:
    """A quote's end marker goes after its trailing blank `>` lines.

    Spec: R47 (E11, E59)
    """
    assert run("> a\n> b\n>\n") == "⟬TYP-1 begin⟭\n\n> a\n> b\n>\n\n⟬TYP-1 end⟭\n"
    assert run("> - a\n> - b\n>\n\nnext\n") == (
        "⟬TYP-1 begin⟭\n\n> - a ⟬TYP-2⟭\n> - b ⟬TYP-3⟭\n>\n\n⟬TYP-1 end⟭\n\nnext ⟬TYP-4⟭\n"
    )


def test_tab_after_a_quote_marker_takes_one_column_r30() -> None:
    """After `>`, a tab takes one column for the optional space.

    Spec: R30, R38 (E39)
    """
    out = run(">\t- a\n>\t  - b\n>\t  - c\n")
    assert ">     ⟬TYP-2 begin⟭\n" in out  # "> " and the item content, 4 more columns


def test_quote_without_a_space_moves_indented_code_whole_e35() -> None:
    """After a `>` with no space, the moved code keeps its column with one more space.

    Spec: R37 (E35)
    """
    assert run(">7)     code\n") == ">7) ⟬TYP-1⟭\n>\n>    ⟬TYP-2 begin⟭\n>\n>        code\n>\n>    ⟬TYP-2 end⟭\n"


def test_definition_on_the_marker_line_gives_the_id_after_the_marker_e30() -> None:
    """An item whose first block is a definition has its ID after its marker.

    Spec: R35 (E30)
    """
    assert run("- [a]: /u\n\n  text\n- c\n").startswith("⟬TYP-1 begin⟭\n\n- ⟬TYP-2⟭\n\n  ⟬TYP-3 begin⟭\n")


def test_node_framed_on_a_line_that_cannot_be_split_e32() -> None:
    """On a marker line that cannot be split, the IDs of the nodes starting there end the line,
    deeper first.

    Spec: R36 (E32)
    """
    assert run("- - [ ] t\n  - b\n") == "- - [ ] t ⟬TYP-3⟭ ⟬TYP-2⟭ ⟬TYP-1⟭\n  - b ⟬TYP-4⟭\n"


def test_control_characters_do_not_stop_the_annotation() -> None:
    """The whole-file check reads control characters.

    Note: D30

    Spec: R50
    """
    assert run("- - a\x1b\n") == "- ⟬TYP-1⟭\n\n  - a\x1b ⟬TYP-2⟭\n"


def test_setext_heading_that_an_id_would_make_a_definition_is_framed_r24() -> None:
    """A setext heading whose text would become a definition with the ID is framed.

    Spec: R24
    """
    assert run("[a]:\n===\n") == "⟬TYP-1 begin⟭\n\n[a]:\n===\n\n⟬TYP-1 end⟭\n"
