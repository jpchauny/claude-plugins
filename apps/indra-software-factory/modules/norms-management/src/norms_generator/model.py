"""Shared data model of the layer 2 generator (specs/norms-tree.md).

Every module works on these types. Offsets are byte offsets into the
UTF-8 source of the spec file, whatever its line endings; lines are
1-based like cmark's.

Modules (each cites the rules it implements):
    cmark.py     ctypes binding to the cmark-gfm library shipped inside
                 `cmarkgfm`: parse(bytes) -> AstNode.
    tree.py      AstNode + source bytes -> TreeNode tree of one file:
                 sections, spans, collapse, hashes, order.
    annotate.py  TreeNode tree + IDs -> annotated bytes and the list of
                 Insertion; strip() undoes it.
    prefixes.py  file path -> prefix.
    store.py     JSONL read/write and matching of a new tree against
                 the previous JSONL: IDs kept, moved, edited, retired, new;
                 change report.
    structure.py block structure of a source, annotations ignored: what
                 verify.py compares, what tree.py/annotate.py probe and
                 the final check.
    verify.py    checks of an annotated file against the specs and the
                 JSONL, used by `norms-gen verify`.
    cli.py       `norms-gen build`, `verify`, `report`.

Spec: R3, R16
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Kind(str, Enum):
    """Kinds of node in the norms tree, as the JSONL's `kind`. Folders have no node.

    Spec: R1, R5, R14, R33, R61 (E2, E3, E4, E5, E6, E7, E8, E10, E11, E12, E13, E14, E15, E16, E18)
    """

    FILE = "file"
    SECTION = "section"  # heading + what follows
    HEADING = "heading"  # ATX or setext
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"  # fenced or indented
    HTML_BLOCK = "html_block"
    LINK_REF_DEF = "link_ref_def"  # not an AST node, found in the gaps between blocks; Note: D2
    TABLE = "table"
    TABLE_ROW = "table_row"  # R33: body rows only; header cells are children of TABLE
    TABLE_CELL = "table_cell"  # R33: an empty cell too; none for a missing one (E54)
    BLOCK_QUOTE = "block_quote"
    LIST = "list"
    ITEM = "item"  # R33, U4: owns its first paragraph, its ordinal too, as its own text (E12, E13, E14, E15)


@dataclass
class AstNode:
    """One node of the cmark-gfm AST (block level, plus table cells).

    Spec: R17
    """

    type: str  # cmark type string: "document", "paragraph", "table_cell", ...
    # ("tasklist" is reported as "item", "table_header" as "table_row")
    start_line: int
    start_col: int  # 1-based, in bytes; repaired by cmark.parse() (see cmark.py)
    end_line: int
    end_col: int  # inclusive: the node's last byte
    children: list[AstNode] = field(default_factory=list)
    literal: str | None = None  # code/html content
    heading_level: int = 0
    list_type: str | None = None  # "bullet" | "ordered"
    list_tight: bool = False
    fence_info: str | None = None  # None for an indented code block
    is_header: bool = False  # table_row: the header row
    task_checked: bool | None = None  # R33: item: None if not a task item (E15)
    setext: bool = False  # R18: heading: underlined with === or --- (E3)
    before_table: bool = False  # R44: paragraph: a table interrupts it (its definitions stay text)
    open: bool = False  # R48: fenced code or HTML block (types 1-5) never closed: runs to its container's end
    text_end_line: int = 0  # R18: heading: last byte of its text, where the ID goes (E2, E3)
    text_end_col: int = 0  # (before an ATX closing sequence, above a setext underline)


@dataclass
class TreeNode:
    """One node of the norms tree of one file, before IDs are known."""

    kind: Kind
    start: int  # R16: byte offset of the node's first byte
    end: int  # R3, R16: byte offset just past its last byte, before its line ending (LF, CRLF or CR)
    children: list[TreeNode] = field(default_factory=list)
    ordered: bool = False  # R8, R13: True only for a numbered list
    own_text: bytes = b""  # R31: exact bytes of the node minus its children
    own_hash: str = ""  # R31, U5: sha256 hex of own_text; a table's with its delimiter cells sorted
    tree_hash: str = ""  # R31: sha256 over own_hash + children tree hashes
    id: str | None = None  # R9, R14: "TYP-3", or "TYP" for the file; set by store.py
    # Placement of the ID, set by tree.py and used by annotate.py:
    anchor: int = -1  # R18, R24: offset where its inline ID goes (end of its text); -1: framed
    margin: bytes = b""  # R30: container prefix of a marker line around it
    inner: bytes = b""  # R30: ITEM: container prefix of a line inside it, its content indentation
    head: int = -1  # R16, R27: ITEM: offset of its list marker (`start` moves: indentation, collapse)
    pad: bytes = b" "  # R30, R39: blank written before its inline ID; wider for an empty item
    brk: bool = False  # R39: a blank line written after its inline ID (an empty item)
    lead: bytes = b""  # R46: TABLE_CELL: written before the cell, at its row's start: "|"
    begin: int = -1  # R44, R49: line where its begin marker goes, when not its own: above its paragraph for a TABLE, -2 for a frame widened to its top-level block (E51)
    content: int = -1  # R37: ITEM: offset of its content column on its marker line
    delimiters: list[tuple[int, int]] = field(default_factory=list)  # R31, U5: TABLE: its delimiter row's cells


@dataclass
class Insertion:
    """Bytes added at one offset of the spec file.

    Spec: R23
    """

    offset: int
    text: bytes
