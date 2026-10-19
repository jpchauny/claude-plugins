"""Tests of structure.block_structure(), the block comparison of verify.

Spec: R26, R30, R48, R64, U1, U2
"""

from __future__ import annotations

from norms_generator.structure import block_structure


def test_control_characters_are_read() -> None:
    """cmark-gfm writes ESC and form feed into its XML; they no longer stop the parse of verify's block comparison.

    Note: D30

    Spec: R64
    """
    assert block_structure(b"esc \x1b[0m\n") == block_structure(b"esc \x1b[0m\n")
    assert block_structure(b"a\x0cb\n") != block_structure(b"a\x0bb\n")


def test_end_markers_inside_an_unclosed_block_are_tolerated_e61() -> None:
    """End markers and blank lines at the end of an unclosed block are tolerated.

    Spec: R48, R64, U1 (E61, E62)
    """
    assert block_structure(b"```\nx\n\n\xe2\x9f\xacTYP-1 end\xe2\x9f\xad\n") == block_structure(b"```\nx\n")
    assert block_structure("<!-- a\n\n⟬TYP-1 end⟭\n".encode()) == block_structure(b"<!-- a\n")


def test_only_trailing_end_markers_are_tolerated_r48() -> None:
    """A marker inside closed code, or a begin marker, or text, still differs.

    Spec: R26, R48, R64
    """
    closed = b"```\nx\n```\n"
    assert block_structure("```\nx\n⟬TYP-1 end⟭\n```\n".encode()) != block_structure(closed)
    assert block_structure("```\nx\n⟬TYP-1 begin⟭\n".encode()) != block_structure(b"```\nx\n")
    assert block_structure(b"```\nx\ny\n") != block_structure(b"```\nx\n")


def test_tightness_is_ignored_e13() -> None:
    """The block comparison ignores list tightness.

    Spec: R30, R64, U2 (E13)
    """
    assert block_structure(b"- a\n- b\n") == block_structure(b"- a\n\n- b\n")


def test_open_blocks_are_known() -> None:
    """Unclosed fences and HTML blocks of types 1-5 are known as open; a `<div>` block is not.

    Spec: R48
    """
    from norms_generator.cmark import html_block_is_open, parse

    assert parse(b"```\nx\n").children[0].open and not parse(b"```\nx\n```\n").children[0].open
    assert html_block_is_open("<!-- a\n\nb\n") and not html_block_is_open("<!-- a -->\n")
    assert html_block_is_open("<pre>\nx\n") and not html_block_is_open("<div>\nx\n")
