"""AST of one spec file -> its norms tree (specs/norms-tree.md).

`build_tree(source, path)` parses a file with cmark-gfm (cmark.py) and
returns its tree as `TreeNode`s (model.py), the root of kind FILE:

    FILE                       the whole source, [0, len(source))
      SECTION                  heading + what follows, only at
        HEADING                the top level of the file; content before
        ...                    the first heading belongs to the file
        SECTION                nested: a deeper heading opens a subsection
      PARAGRAPH | CODE_BLOCK | HTML_BLOCK | LINK_REF_DEF | HEADING
      BLOCK_QUOTE              children: the blocks inside
      LIST                     children: ITEMs; `ordered` for numbered lists
        ITEM                   owns its first paragraph; other blocks
                               are its children
      TABLE                    children: header cells, then body rows
        TABLE_CELL             a header cell (the header row has no node)
        TABLE_ROW              a body row; children: its cells
          TABLE_CELL

Thematic breaks and blank lines have no node: their bytes stay in
the own text of the node around them. Link reference definitions are not
AST nodes; they are found in the lines no AST block covers.

A block quote, list or section whose single child covers its
whole content (what the child leaves is only ">" prefixes and blank
lines, no thematic break) is replaced by that child, whose span grows to the
container's span (a quote of one paragraph is one PARAGRAPH node whose
text includes the "> " prefixes). The file is never collapsed.

Spans are exact byte offsets [start, end): a node ends at the last byte
of its last line, trailing whitespace included, line ending excluded
(cmark.parse() repairs the positions to that rule). A table cell spans
the bytes between its pipes, padding included; a cell missing from a
short row has no bytes and no node.

Own text is the node's span with its children's spans cut out:
list markers (a numbered item's ordinal too), "> " prefixes, pipes and
indentation included. A block's span starts at its container's content
column, so that the indentation of its first line is its own, like that
of its later lines. The own hash is SHA-256 of the own text, a table's
with the cells of its delimiter row sorted, so that moving a column
changes no hash; the tree hash is SHA-256 over the own hash followed by
the children's tree hashes, in source order for a numbered list and
sorted otherwise. Hashes are hex.

Fields that serve annotate.py (model.py documents them): `anchor`, the
offset where the node's inline ID goes, or -1 when it is framed;
`margin`, the container prefix of a marker line written around the
node: the item content indentation and "> " for each enclosing block
quote; `inner`, that prefix inside an item; `pad` and `brk`, the blank
before an inline ID and whether a blank line follows it (an empty
item); and `lead`, the "|" written before a row whose first cell would
otherwise start another block.

Code blocks. A code block's span starts at its container's
content column, as every block's does, not where cmark-gfm says its
fence or its code starts:
the indentation before the opening fence decides how many spaces are
stripped from every line of the code, and the indentation of an
indented code block is part of the code, so both are in its own text.
An unclosed fence runs to the end of its container, blank lines
included (they are in the code); its span runs as far. It is framed like
any other code block, and nothing else is written: its end marker falls
inside it for a parser.

Columns. cmark-gfm counts columns in bytes, GFM in virtual columns with
a tab stop every 4 (a tab after "-" reaches column 4). Item content
columns are kept in both: the virtual column decides the indentation of
a marker line inside the item, the byte column where to read the
item's content on a line. On a later line the item's content column is
counted from where its container's content starts on that line (a quote
can start at another column), and a line not indented that far is not in
the item (a lazy line, or a line after it). On a task item's marker line
its content starts after the checkbox.

Item IDs. An item whose first block is a paragraph has its ID
at the end of that paragraph, unless the ID there would change how the
item parses ("- [ ]" followed by an ID becomes a task item; a
last line "1." becomes an item, probed on the whole file): then,
as for an item whose first block is not a paragraph, the anchor is the
start of the first node on the marker line, and annotate.py writes the
ID right after the marker. An item with nothing on its marker line has
its ID at the end of that line, with more blanks before it or a blank
line after it when the ID alone would give the item content that the
next line continues.

Tables. Rows and cells are read from the source, not from
cmark-gfm's columns, which are wrong for a body row whose line starts
otherwise than the header's (indentation, a BOM, a tab item, a task
item): a row starts at its container's content, its blanks skipped, and
its cells are the bytes between its unescaped pipes.

Link reference definitions. A definition directly followed by
the text of a paragraph or setext heading is one block for cmark-gfm.
When framing the definition apart would change how that text parses
(an indented line, "---", a lazy line in an item, ...), the definition
is not a node of its own: the block starts at it. The definitions at
the end of a quote or item run on over the lazy lines after them, as
the rest of a definition or new ones, which are framed at their
top-level block when a frame would cut the lazy line off.

Probes. Where a placement can change how the file parses, the builder
inserts the probe marker into the whole source and compares the block
structure (structure.py) with the source's.

Note: D2, D39

Spec: R5, R7, R13, R16, R24, R26, R27, R30, R31, R33, R35, R38, R39, R41, R43, R45, R46, R48, U1, U4, U5 (E8, E12, E14, E18, E19, E21, E22, E28, E29, E61)
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable

import bisect

import cmarkgfm

from norms_generator import cmark
from norms_generator.cmark import SourceLines
from norms_generator.model import AstNode, Kind, TreeNode
from norms_generator.structure import Structure, block_structure

_KINDS: dict[str, Kind] = {
    "paragraph": Kind.PARAGRAPH,
    "heading": Kind.HEADING,
    "code_block": Kind.CODE_BLOCK,
    "html_block": Kind.HTML_BLOCK,
    "block_quote": Kind.BLOCK_QUOTE,
    "list": Kind.LIST,
    "item": Kind.ITEM,
    "table": Kind.TABLE,
}

# R27: containers that collapse into their single child.
_COLLAPSIBLE = {Kind.BLOCK_QUOTE, Kind.LIST, Kind.SECTION}

_LIST_MARKER = re.compile(rb"[-+*]|[0-9]{1,9}[.)]")
_LINK_REF_DEF_START = re.compile(rb"[ \t]*\[")  # R35: on a line no block covers, after any blanks; Note: D2
_CHECKBOX = re.compile(rb"[ \t]*\[[ xX]\]")  # R38: a task item's checkbox, its content starts after it (E15)
_EOL = re.compile(rb"\r\n|\r|\n")
TAB_STOP = 4  # R38: a tab stop every 4 columns, GFM §2.2
_BOM = b"\xef\xbb\xbf"
HOIST = -2  # R49: TableNode.begin, framed at its top-level block
# R29: probe markers, of the shape of the real ones
PROBE = "⟬PROBE-1⟭".encode()
PROBE_BEGIN = "⟬PROBE-1 begin⟭".encode()
PROBE_END = "⟬PROBE-1 end⟭".encode()


def line_ending(source: bytes) -> bytes:
    """The line ending of lines inserted into `source`: "\r\n", a lone "\r" or "\n".

    Spec: R3, R52
    """
    if b"\r\n" in source:
        return b"\r\n"
    if b"\r" in source and b"\n" not in source:
        return b"\r"
    return b"\n"


def blank_line(margin: bytes) -> bytes:
    """A blank line inside the containers of `margin`: ">" stays, spaces go.

    Spec: R30 (E24)
    """
    return margin.rstrip(b" \t")


def is_blank_under(line: bytes, margin: bytes) -> bool:
    """True if `line` holds nothing inside the containers of `margin`.

    Each ">" of `margin` takes a ">" of the line, after up to 3 spaces
    more than the margin's indentation before it; a ">" past them is
    content ("> >" in one quote, "    >" a lazy line or code), and so is
    a line that lacks one of them (a lazy line).

    Spec: R30, R47
    """
    pos = 0
    allowance = 0
    for byte in margin:
        if byte != 0x3E:  # ">"
            allowance += 1 if byte == 0x20 else TAB_STOP
            continue
        start = pos
        while pos < len(line) and vcol(line, pos) - vcol(line, start) < allowance + 3 and line[pos] in (0x20, 0x09):
            pos += 1
        # R47: a ">" indented less than the item that holds it is not in the
        # item: a lazy line ("    >" under "     > "), content
        if line[pos : pos + 1] != b">" or vcol(line, pos) - vcol(line, start) < allowance:
            return not line.strip(b" \t")
        pos += 1
        allowance = -1  # the optional space after ">" is part of the margin
    return not line[pos:].strip(b" \t")


def vcol(text: bytes, index: int) -> int:
    """Virtual column (0-based, tabs to the next multiple of 4) of byte `index` of a line.

    Spec: R38
    """
    col = 0
    for byte in text[:index]:
        col = col + TAB_STOP - col % TAB_STOP if byte == 0x09 else col + 1
    return col


def _index_at_vcol(text: bytes, target: int) -> int:
    """Index of the byte of a line that covers virtual column `target`; len(text) past its end.

    A tab that is only partly before `target` covers it (GFM consumes
    part of it).

    Spec: R38
    """
    col = 0
    for i, byte in enumerate(text):
        width = TAB_STOP - col % TAB_STOP if byte == 0x09 else 1
        if col + width > target:
            return i
        col += width
    return len(text)


def _cells(source: bytes, start: int, end: int) -> list[tuple[int, int]]:
    """[start, end) of each cell of the table row in source[start:end] (GFM §4.10).

    A cell is the bytes between its pipes, padding included; a leading
    pipe opens the row, a trailing one (blanks after it allowed) closes
    it, and without it the last cell runs to the end of the line. A pipe
    right after a backslash is escaped, as cmark-gfm reads it, even
    inside a code span.

    Spec: R45 (E56)
    """
    pos = start
    if pos < end and source[pos] == 0x7C:
        pos += 1
    cells: list[tuple[int, int]] = []
    while True:
        p = pos
        while p < end and not (source[p] == 0x7C and source[p - 1] != 0x5C):
            p += 1
        cells.append((pos, p))
        if p >= end:
            return cells
        pos = p + 1
        if not source[pos:end].strip(b" \t"):
            return cells


def build_tree(source: bytes, path: str = "") -> TreeNode:
    """Return the norms tree of one spec file, root of kind FILE.

    `path` is the file's path in the specs; it is not stored in the
    tree (store.py keys trees by path) and only names the file in errors.

    Spec: R5
    """
    try:
        return _Builder(source).build()
    except Exception as exc:  # pragma: no cover - names the file in the traceback
        raise RuntimeError(f"cannot build the norms tree of {path or '<source>'}") from exc


_PROBE_ID = "⟬PROBE-1⟭"


def _defs_only(texts: list[bytes], lazy: list[bool]) -> bool:
    """True if the lines of a definition are only definitions.

    Without lazy lines they are parsed alone; with them, in a quote, the
    `lazy` ones as lazy lines: alone, "=", ":-", "***" or a fence would
    open a block that a lazy line cannot.

    Spec: R42, R43
    """
    if not any(lazy):
        return cmark.only_link_ref_defs(b"\n".join(texts))
    probe = b"".join(
        (b"\n" if i else b"") + (b"" if is_lazy else b"> ") + text for i, (text, is_lazy) in enumerate(zip(texts, lazy))
    )
    blocks = cmark.parse_raw(probe.replace(b"\0", b"\x01")).children
    return len(blocks) == 1 and blocks[0].type == "block_quote" and not blocks[0].children


def inline_id_is_safe(text: bytes, at: int) -> bool:
    """True if " ⟬ID⟭" inserted at `at` in `text` leaves its rendering unchanged.

    `text` is rendered as GFM alone, with and without the ID; once the ID
    is removed from the second rendering, the two must be equal. An ID
    taken into a URL, a code span or raw HTML fails this test.

    Spec: R24 (E17)
    """
    plain = text.decode("utf-8", "replace")
    marked = text[:at].decode("utf-8", "replace") + " " + _PROBE_ID + text[at:].decode("utf-8", "replace")
    before = cmarkgfm.github_flavored_markdown_to_html(plain)
    after = cmarkgfm.github_flavored_markdown_to_html(marked)
    return after.replace(" " + _PROBE_ID, "") == before


def walk(node: TreeNode) -> Iterable[TreeNode]:
    """Yield `node` and its descendants in pre-order (document order)."""
    yield node
    for child in node.children:
        yield from walk(child)


def sha256(data: bytes) -> str:
    """Hex SHA-256 of `data`."""
    return hashlib.sha256(data).hexdigest()


def own_text(source: bytes, node: TreeNode) -> bytes:
    """The node's span with its children's spans cut out.

    Spec: R31
    """
    parts: list[bytes] = []
    pos = node.start
    for child in sorted(node.children, key=lambda c: c.start):
        parts.append(source[pos : child.start])
        pos = max(pos, child.end)
    parts.append(source[pos : node.end])
    return b"".join(parts)


def _hashed_text(source: bytes, node: TreeNode) -> bytes:
    """What a node's own hash covers: its own text, a table's with its delimiter cells sorted.

    Moving a column moves its delimiter cell (`:---`, `---:`, a wider
    `-------`) with it; sorting the cells in place, the pipes between
    them kept, makes the move change no hash, as for the cells.

    Spec: R13, R31, U5
    """
    if not node.delimiters:
        return own_text(source, node)
    first, last = node.delimiters[0][0], node.delimiters[-1][1]
    cells = sorted(source[s:e] for s, e in node.delimiters)
    parts: list[bytes] = []
    pos = first
    for (s, e), cell in zip(node.delimiters, cells):
        parts.append(source[pos:s])
        parts.append(cell)
        pos = e
    parts.append(source[pos:last])
    return own_text(source[:first] + b"".join(parts) + source[last:], node)


def compute_hashes(source: bytes, node: TreeNode) -> None:
    """Set own_text, own_hash and tree_hash of `node` and its subtree.

    The tree hash covers the whole subtree, so that citing a node cites
    everything below it.

    Spec: R4, R13, R31
    """
    for child in node.children:
        compute_hashes(source, child)
    node.own_text = own_text(source, node)
    node.own_hash = sha256(_hashed_text(source, node))
    hashes = [c.tree_hash for c in node.children]
    if not node.ordered:
        hashes.sort()
    node.tree_hash = sha256((node.own_hash + "".join(hashes)).encode("ascii"))


def _cover_children(node: TreeNode) -> None:
    """Make a container end no earlier than its last child (a link ref def).

    Spec: R43
    """
    if node.children:
        node.end = max(node.end, max(c.end for c in node.children))


class _Builder:
    """Builds the tree of one source; holds its line table."""

    def __init__(self, source: bytes) -> None:
        self.source = source
        self.lines = SourceLines(source)
        # id(AstNode) -> (parent AstNode or None); filled by _index()
        self.parent: dict[int, AstNode | None] = {}
        self.content_cols: dict[int, int] = {}  # id(item AstNode) -> content byte column (1-based)
        self.content_vcols: dict[int, int] = {}  # id(item AstNode) -> content virtual column (0-based)
        # id(AstNode) -> its last line, link ref defs at its end included
        self.last_line: dict[int, int] = {}
        self.doc: AstNode | None = None
        self.eol = line_ending(source)
        self._source_structure: Structure | None = None
        self._structure_known = False
        self.block_lines: set[int] = set()  # lines that an AST block starts on or that a leaf covers
        self.lazy_def_lines: set[int] = set()  # R43: lazy lines that end a definition of a container

    # --- offsets --------------------------------------------------------

    def offset(self, line: int, col: int) -> int:
        """Byte offset of cmark's (line, col)."""
        return self.lines.offset(line, col)

    def span(self, node: AstNode) -> tuple[int, int]:
        """[start, end) byte offsets of an AST node."""
        return cmark.node_span(node, self.lines.offset)

    def line_end(self, line: int) -> int:
        """Offset just past the content of `line` (before its line ending)."""
        return self.lines.ends[line - 1]

    def line_of(self, offset: int) -> int:
        """1-based line holding byte `offset`."""
        return bisect.bisect_right(self.lines.starts, offset)

    def next_line_start(self, offset: int) -> int:
        """Offset of the line after the one holding `offset`; len(source) at the end."""
        line = self.line_of(offset)
        return self.lines.starts[line] if line < len(self.lines.starts) else len(self.source)

    # --- probes ---------------------------------------------------------

    def preserves(self, insertions: list[tuple[int, bytes]]) -> bool:
        """True if the source with `insertions` parses to the source's blocks (structure.py).

        Note: D39
        """
        if not self._structure_known:
            self._source_structure = block_structure(self.source)
            self._structure_known = True
        parts: list[bytes] = []
        pos = 0
        for offset, text in sorted(insertions, key=lambda i: i[0]):
            parts += [self.source[pos:offset], text]
            pos = offset
        parts.append(self.source[pos:])
        return block_structure(b"".join(parts)) == self._source_structure

    def frame_probe(self, start: int, end: int, margin: bytes) -> list[tuple[int, bytes]]:
        """The insertions of a frame around [start, end): marker lines with blank lines around.

        Spec: R30
        """
        eol, blank = self.eol, blank_line(margin)
        begin = blank + eol + margin + PROBE_BEGIN + eol + blank + eol
        after = blank + eol + margin + PROBE_END + eol + blank + eol
        at = self.next_line_start(end)
        if at >= len(self.source) and not self.source.endswith((b"\n", b"\r")):
            after = eol + after
        return [(self.line_start(start), begin), (at, after)]

    def line_start(self, offset: int) -> int:
        """Offset of the first byte of the line holding `offset`, after a BOM.

        Spec: R52
        """
        start = self.lines.starts[self.line_of(offset) - 1]
        return len(_BOM) if start == 0 and self.source.startswith(_BOM) else start

    # --- build ----------------------------------------------------------

    def build(self) -> TreeNode:
        doc = self.doc = cmark.parse(self.source)
        self._index(doc, None)
        self._extend(doc, self.lines.count)
        self._block_lines(doc)
        root = TreeNode(kind=Kind.FILE, start=0, end=len(self.source))
        blocks = self._blocks(doc, b"")
        root.children = self._sections(blocks)
        root.children = [self._collapse(c) for c in root.children]
        compute_hashes(self.source, root)
        return root

    def _index(self, node: AstNode, parent: AstNode | None) -> None:
        """Record parents and item content columns.

        Spec: R38
        """
        self.parent[id(node)] = parent
        if node.type == "item":
            content = self._item_content_vcol(node)
            line = self.lines.content(node.start_line)
            self.content_vcols[id(node)] = content
            self.content_cols[id(node)] = _index_at_vcol(line, content) + 1
        for child in node.children:
            self._index(child, node)

    def _block_lines(self, node: AstNode) -> None:
        """Record the lines that an AST block starts on, and those a leaf block covers.

        Spec: R43
        """
        if node.type != "document":
            self.block_lines.add(node.start_line)
            if node.type not in ("block_quote", "list", "item"):
                self.block_lines.update(range(node.start_line, node.end_line + 1))
        for child in node.children:
            self._block_lines(child)

    def _blocks(self, container: AstNode, margin: bytes) -> list[TreeNode]:
        """Tree nodes of the children of an AST container, link ref defs included.

        Note: D2
        """
        nodes: list[TreeNode] = []
        previous: tuple[AstNode, TreeNode] | None = None
        for child in container.children:
            node = self._node(child, margin)
            if node is not None:
                nodes.append(node)
                if previous is not None and previous[0].before_table and node.kind is Kind.TABLE:
                    self._before_table(previous[1], node, margin, container)
                previous = (child, node)
        nodes.extend(self._link_ref_defs(container, margin))
        nodes.sort(key=lambda n: n.start)
        return self._merge_link_ref_defs(nodes, margin)

    def _merge_link_ref_defs(self, nodes: list[TreeNode], margin: bytes) -> list[TreeNode]:
        """Join a definition to the paragraph, heading or table it directly precedes, if needed.

        cmark-gfm reads the definition and the text right after it as one
        block. Framed apart, the text is parsed again on its own, which
        changes it when it is an indented line, a "---", a lazy line of
        an item, an HTML tag, ...: then the block starts at the definition.

        Spec: R24, R41, R44 (E8, E45, E66)
        """
        i = len(nodes) - 2
        while i >= 0:
            a, b = nodes[i], nodes[i + 1]
            if (
                a.kind is Kind.LINK_REF_DEF
                and b.kind in (Kind.PARAGRAPH, Kind.HEADING, Kind.TABLE)
                and self._adjacent(a, b)
                and not self.preserves(self.frame_probe(a.start, a.end, margin))
            ):
                b.start = a.start
                if b.kind is Kind.PARAGRAPH:
                    b.anchor = -1  # R24: several lines now, framed (E8)
                del nodes[i]
            i -= 1
        return nodes

    def _adjacent(self, a: TreeNode, b: TreeNode) -> bool:
        """True if `b` starts on the line right after `a` ends, with no blank line between."""
        gap = self.source[a.end : b.start]
        m = _EOL.match(gap)
        return m is not None and not _EOL.search(gap, m.end()) and not gap[m.end() :].strip(b" \t>")

    def _node(self, ast: AstNode, margin: bytes) -> TreeNode | None:
        """The tree node of one AST block, or None (thematic break).

        Spec: R7, R16, R18, R24, R31 (E17)
        """
        kind = _KINDS.get(ast.type)
        if kind is None:
            return None
        start, end = self.span(ast)
        node = TreeNode(kind=kind, start=start, end=end, margin=margin)
        # R16: the indentation of its first line is the block's own text, as that
        # of its later lines is: the span starts at its container's content
        node.start = self._block_start(ast, start)
        if kind is Kind.PARAGRAPH:
            if ast.start_line == ast.end_line:  # R24: one line, inline if it is safe (E17)
                anchor = self._text_end(start, end)
                if inline_id_is_safe(self.source[start:end], anchor - start):
                    node.anchor = anchor
        elif kind is Kind.HEADING:
            node.anchor = self.offset(ast.text_end_line, ast.text_end_col) + 1  # R18: at the end of its text
            if ast.setext and not self.preserves([(node.anchor, b" " + PROBE)]):
                # R24: "[a]:" then "===", with " ⟬ID⟭" the text is a definition,
                # a last text line "-" a list item: the heading is framed
                node.anchor = -1
        elif kind is Kind.CODE_BLOCK:
            if ast.fence_info is not None:
                self._unclosed_fence(ast, node)
        elif kind is Kind.BLOCK_QUOTE:
            node.children = self._blocks(ast, margin + b"> ")
            _cover_children(node)
            self._quote_tail(ast, node)
        elif kind is Kind.LIST:
            node.ordered = ast.list_type == "ordered"
            node.children = [self._item(item, margin) for item in ast.children]
            _cover_children(node)
        elif kind is Kind.TABLE:
            table_start, node.children = self._table(ast, margin)
            line = ast.children[0].start_line + 1  # R31: the delimiter row follows the header row
            node.delimiters = _cells(self.source, self._row_start(self.parent[id(ast)], line), self.line_end(line))
            node.start = self._block_start(ast, table_start)
        return node

    def _before_table(self, para: TreeNode, table: TreeNode, margin: bytes, container: AstNode) -> None:
        """A paragraph that a table interrupts.

        The table's begin marker, with its blank lines, parts them, which
        can change how they parse: a paragraph like a definition, which
        cmark-gfm keeps as text there ("[r]: /u"), is a definition again;
        a header row that was an indented line of the paragraph
        ("para" then "    a | b") becomes indented code. The first
        placement that keeps the file's blocks wins: the usual one;
        the paragraph's ID at the end of its last line; that ID, with the
        table's begin marker moved before the paragraph, which then stays
        right above the table, inside its frame.

        Spec: R39, R44, R49 (E50, E51, E52, E53)
        """
        eol, blank = self.eol, blank_line(margin)
        split = (self.line_start(table.start), blank + eol + margin + PROBE_BEGIN + eol + blank + eol)
        usual = [(para.anchor, b" " + PROBE)] if para.anchor >= 0 else self.frame_probe(para.start, para.end, margin)
        if self.preserves([*usual, split]):
            return
        # R44: the paragraph's ID at the end of its last line, the table's begin
        # marker between them or above the paragraph; else at the end of an
        # earlier line: a last line "1." or "*" would become a list item
        first, last = self.line_of(para.start), self.line_of(para.end)
        ends = [
            self._text_end(max(self.lines.starts[n - 1], para.start), min(self.line_end(n), para.end))
            for n in range(last, first - 1, -1)
        ]
        line_start = self.line_start(para.start)
        on_marker_line = bool(self.source[line_start : para.start].strip(b" \t>"))
        above = [(line_start, blank + eol + margin + PROBE_BEGIN + eol + blank + eol)]
        if container.type == "item" and self.line_of(para.start) > container.start_line:
            # R39: an empty marker line then gets the item's ID, or the begin
            # marker after a blank line would leave the item
            head_end = self.line_end(container.start_line)
            content = min(self.offset(container.start_line, self.content_cols[id(container)]), head_end)
            if not self.source[content:head_end].strip(b" \t"):
                above.append((head_end, b" " + PROBE))
        for candidates in (ends[:1], ends[1:]):
            for inline in candidates:
                if self.preserves([(inline, b" " + PROBE), split]):
                    para.anchor = inline
                    return
            if on_marker_line:  # R49: the table's begin cannot go above the paragraph
                para.anchor, table.begin = ends[0], HOIST
                return
            for inline in candidates:
                if self.preserves([(inline, b" " + PROBE), *above]):
                    para.anchor, table.begin = inline, line_start
                    return
        para.anchor, para.begin, table.begin = -1, HOIST, HOIST  # R49: both framed at their top-level block

    def _quote_tail(self, ast: AstNode, node: TreeNode) -> None:
        """A block quote ends with its blank ">" lines.

        cmark.parse() ends a quote with its last child; the ">" lines
        after it still belong to it, and an end marker before them would
        leave them to open a new, empty block quote.

        Spec: R47 (E59)
        """
        line = self.line_of(node.end) + 1
        while line <= self.lines.count:
            col = self._content_col(ast, line)
            if col == 0 or self.lines.content(line)[col - 1 :].strip(b" \t"):
                break
            node.end = self.line_end(line)
            line += 1

    @staticmethod
    def _after_checkbox(container: AstNode | None, line: int) -> bool:
        """True on a task item's marker line, where the blank after its checkbox parts it from its content.

        Spec: R16
        """
        return container is not None and container.task_checked is not None and line == container.start_line

    def _block_start(self, ast: AstNode, start: int) -> int:
        """Start of a block: back over the blanks before it, to its container's content.

        For a code block the indentation before its fence decides how many
        spaces are stripped from its lines, and that of an indented code
        block is part of its code; for every other block, the indentation
        of its first line is its bytes as much as that of its later lines.
        On a lazy line (no container content there) it stays.

        Spec: R16
        """
        parent = self.parent[id(ast)]
        col = self._content_col(parent, ast.start_line) if parent is not None else 1
        line_start = self.lines.starts[ast.start_line - 1]
        if not col or self._after_checkbox(parent, ast.start_line):
            return start
        bound = self.offset(ast.start_line, col)
        pos = start
        while pos > max(bound, line_start) and self.source[pos - 1 : pos] in (b" ", b"\t"):
            pos -= 1
        return pos

    def _unclosed_fence(self, ast: AstNode, node: TreeNode) -> None:
        """An unclosed fence: its span runs to the end of its code, blank lines included.

        Spec: R48, U1 (E61)
        """
        literal = (ast.literal or "").encode("utf-8", "surrogateescape")
        n = len(_EOL.findall(literal)) if literal else 0
        if literal and not _EOL.search(literal[-1:]):
            n += 1
        if ast.end_line == ast.start_line + n + 1:
            return  # closed: the closing fence is its last line
        last = min(ast.start_line + n, self.lines.count)
        node.end = max(node.end, self.line_end(last))

    def _item(self, ast: AstNode, margin: bytes) -> TreeNode:
        """An ITEM: owns its first paragraph; other blocks are children.

        Its span starts at its marker, so the marker, and a numbered item's
        ordinal, are in its own text.

        Spec: R16, R33, R35, R39, R44, U4 (E12, E14, E28, E29)
        """
        start, end = self.span(ast)
        inner = margin + b" " * max(self.content_vcols[id(ast)] - self._container_vcol(ast), 0)
        node = TreeNode(kind=Kind.ITEM, start=start, end=end, margin=margin, inner=inner, head=start)
        node.start = self._block_start(ast, start)  # R16: the marker's indentation too
        node.content = min(self.offset(ast.start_line, self.content_cols[id(ast)]), self.line_end(ast.start_line))
        children = self._blocks(ast, inner)
        first = ast.children[0] if ast.children else None
        first_line_end = self.line_end(ast.start_line)
        para = None
        if first is not None and first.type == "paragraph":
            p_end = self.span(first)[1]
            para = next((c for c in children if c.kind is Kind.PARAGRAPH and c.end == p_end), None)
        if para is not None and para.start > first_line_end and any(c.start <= first_line_end for c in children):
            para = None  # R35: a definition on the marker line is the item's first block
        if para is not None:
            children = [c for c in children if c is not para]
            p_start, p_end = para.start, para.end
            anchor = self._text_end(p_start, p_end)
            # R35: a one-line paragraph on the marker line is probed from the
            # marker, out of its containers (it can turn into a task item); a
            # longer one on the whole file: its last line can be a bare list
            # marker ("- a" then "  1."), which the ID turns into an item (E28, E29)
            one_line = p_start <= first_line_end and not _EOL.search(self.source, p_start, p_end)
            # alone, "[a]:u" would be a definition, and a tab would reach another
            # tab stop without the bytes before the marker (" -\t  [x]")
            tabs = b"\t" in self.source[self.line_start(start) : p_end]
            if one_line and not first.before_table and not tabs:
                safe = inline_id_is_safe(self.source[start:p_end], anchor - start)
            else:
                safe = self.preserves([(anchor, b" " + PROBE)])
            if safe:
                node.anchor = anchor
            else:  # R35: the ID at its end would change the item, after the marker
                node.anchor = p_start
            if p_start > first_line_end and any(
                c.kind is Kind.TABLE and 0 <= c.begin <= p_start for c in children
            ):  # R39, R44: a table's frame begins above the paragraph, "-" then a
                # marker line would make the item start with a blank line and lose
                # its content: the ID gives the marker line content
                node.anchor = self._text_end(start, first_line_end)
                node.pad, node.brk = self._empty_item_id(node)
        else:
            heads = [c.start for c in children if c.start <= first_line_end]
            if first is not None and first.start_line == ast.start_line:  # a thematic break too
                heads.append(self.offset(first.start_line, first.start_col))
            if heads:  # R35: a block, or a link ref def, on the marker line, the ID after the marker
                node.anchor = min(heads)
            else:  # R39: empty first line, the ID goes at its end
                node.anchor = self._text_end(start, first_line_end)
                node.pad, node.brk = self._empty_item_id(node)
        node.children = children
        _cover_children(node)
        return node

    _EMPTY_ITEM_OPTIONS = (  # R39: its placements, in its order
        (b" ", False),
        (b" ", True),
        (b"  ", False),
        (b"   ", False),
        (b"    ", False),
        (b"  ", True),
        (b"   ", True),
        (b"    ", True),
    )

    def _empty_item_id(self, node: TreeNode) -> tuple[bytes, bool]:
        """The blank before an empty item's ID, and whether a blank line follows it.

        The ID gives the item content: the next line could continue it (a
        lazy line, a setext underline) or nest in it (an item indented to
        its new content column). The first placement that keeps the
        file's blocks wins; more blanks before the ID move the item's
        content column past the next line's indentation (at most 4, or
        the ID would be indented code).

        Spec: R39, R40, R49 (E43)
        """
        blank = blank_line(node.inner)  # R39: inside the item's quotes, even once collapsed (E43)
        for pad, brk in self._EMPTY_ITEM_OPTIONS:
            text = pad + PROBE + (self.eol + blank if brk else b"")
            if self.preserves([(node.anchor, text)]):
                return pad, brk
        # R40, R49: no place on its line keeps the blocks ("- [ ] " then a blank
        # line and "  b", which the ID would take into the item): framed at its
        # top-level block
        node.anchor, node.begin = -1, HOIST
        return b" ", False

    def _table(self, ast: AstNode, margin: bytes) -> tuple[int, list[TreeNode]]:
        """The table's start, and its header cells, then body rows with their cells.

        Spec: R33, R45
        """
        container = self.parent[id(ast)]
        children: list[TreeNode] = []
        table_start = self.span(ast)[0]
        for i, row in enumerate(ast.children):
            line = row.start_line
            r_start, r_end = self._row_start(container, line), self.line_end(line)
            if i == 0:
                table_start = r_start
            cells = []
            for c_start, c_end in _cells(self.source, r_start, r_end)[: len(row.children)]:
                anchor = self._text_end(c_start, c_end)  # an empty cell: its start
                cells.append(TreeNode(Kind.TABLE_CELL, c_start, c_end, anchor=anchor, margin=margin))
            if cells and cells[0].start == r_start and self.source[r_start : r_start + 1] != b"|":
                cells[0].lead = self._lead(r_start, r_end, cells[0].anchor)
            if row.is_header:
                children.extend(cells)
            else:
                anchor = self._text_end(r_start, r_end)
                children.append(TreeNode(Kind.TABLE_ROW, r_start, r_end, cells, anchor=anchor, margin=margin))
        return table_start, children

    def _row_start(self, container: AstNode | None, line: int) -> int:
        """Offset of a table row's first byte: its container's content, blanks skipped.

        A header row can be a lazy line of a paragraph (not indented into
        its item, or without the ">" of its quote): it starts after the
        prefixes of the containers it does reach.

        Spec: R45
        """
        pos = self._reached(container, line)
        end = self.line_end(line)
        while pos < end and self.source[pos] in (0x20, 0x09):
            pos += 1
        return pos

    def _reached(self, container: AstNode | None, line: int) -> int:
        """Offset where the content of `container`, or of the nearest container `line` reaches, starts.

        A lazy line lacks the indentation of its item or the ">" of its
        quote; its content starts after the prefixes of the outer
        containers it does reach.
        """
        col = 0
        while container is not None and not col:
            col = self._content_col(container, line)
            container = self.parent[id(container)]
        return self.offset(line, col) if col else self.lines.starts[line - 1]

    def _lead(self, start: int, end: int, anchor: int) -> bytes:
        """b"|" when the first cell's ID would make its row start another block.

        A row without a leading pipe whose first cell is "-", "1.", "#" or
        "<div" becomes a list item, a heading or an HTML block once " ⟬ID⟭"
        follows that cell. A pipe written before the row keeps it a row.

        Spec: R46 (E57, E58)
        """
        text = self.source[start:end]
        at = anchor - start
        probe = text[:at] + b" " + PROBE + text[at:]
        alone = cmark.parse_raw(text).children
        marked = cmark.parse_raw(probe).children
        if alone and alone[0].type == "paragraph":
            return b"" if marked and marked[0].type == "paragraph" else b"|"
        # R46: alone the row is another block ("+", "1."), it is a row only after
        # the paragraph above it, so the ID is probed on the whole file
        if self.preserves([(anchor, b" " + PROBE)]):
            return b""
        return b"|" if self.preserves([(anchor, b" " + PROBE), (start, b"|")]) else b""

    def _text_end(self, start: int, end: int) -> int:
        """Offset just past the last non-blank byte of [start, end), or start: where an ID goes.

        Spec: R18
        """
        text = self.source[start:end].rstrip(b" \t")
        return start + len(text)

    # --- sections ------------------------------------------------------

    def _sections(self, blocks: list[TreeNode]) -> list[TreeNode]:
        """Group the top-level blocks into nested sections.

        Spec: R5 (E18)
        """
        top: list[TreeNode] = []
        stack: list[tuple[int, TreeNode]] = []  # (heading level, section)
        levels = self._heading_levels()
        for block in blocks:
            if block.kind is Kind.HEADING and block.end in levels:
                level = levels[block.end]
                while stack and stack[-1][0] >= level:
                    stack.pop()
                section = TreeNode(Kind.SECTION, block.start, block.end, [block], margin=b"")
                (stack[-1][1].children if stack else top).append(section)
                stack.append((level, section))
            else:
                (stack[-1][1].children if stack else top).append(block)
        for node in top:
            self._close_section(node)
        return top

    def _close_section(self, node: TreeNode) -> None:
        """Make a section end where its last descendant ends.

        Spec: R16
        """
        if node.kind is not Kind.SECTION:
            return
        for child in node.children:
            self._close_section(child)
        node.end = max(c.end for c in node.children)

    def _heading_levels(self) -> dict[int, int]:
        """End offset -> level of the top-level headings (a definition may move a start).

        Spec: R41
        """
        levels: dict[int, int] = {}
        assert self.doc is not None
        for child in self.doc.children:
            if child.type == "heading":
                levels[self.span(child)[1]] = child.heading_level
        return levels

    # --- collapse ------------------------------------------------------

    def _collapse(self, node: TreeNode) -> TreeNode:
        """Replace a container with its single child, bottom-up.

        Only when the child covers the container's text: what the child
        leaves of it is ">" prefixes and blank lines. A quote that also
        holds a thematic break keeps its own node: the break holds no
        information and must not become the child's text.

        Spec: R7, R27 (E21)
        """
        node.children = [self._collapse(c) for c in node.children]
        if node.kind in _COLLAPSIBLE and len(node.children) == 1:
            child = node.children[0]
            if own_text(self.source, node).strip(b" \t\r\n>"):
                return node
            child.start, child.end, child.margin = node.start, node.end, node.margin
            return child
        return node

    # --- link reference definitions ------------------------------------

    def _link_ref_defs(self, container: AstNode, margin: bytes) -> list[TreeNode]:
        """LINK_REF_DEF nodes in the lines of `container` no child covers, and in its lazy lines.

        Note: D2

        Spec: R16, R42, R43 (E47)
        """
        if container.type not in ("document", "block_quote", "item"):
            return []
        first, last = container.start_line, self.last_line[id(container)]
        covered: set[int] = set()
        for child in container.children:
            covered.update(range(child.start_line, self.last_line[id(child)] + 1))
        covered |= self.lazy_def_lines
        if container.type == "item" and container.children:
            if container.children[0].start_line == container.start_line:
                covered.add(first)
        defs: list[TreeNode] = []
        current: TreeNode | None = None
        texts: list[bytes] = []  # the lines of the current definition
        lazy: list[bool] = []  # whether each of them is a lazy line
        line = first
        while line <= self.lines.count:
            if line > last:  # past the container: only the lazy lines of its open definitions
                if (
                    current is None
                    or container.type == "document"
                    or line in self.block_lines
                    or line in self.lazy_def_lines
                ):
                    break
                col = 0
            elif line in covered:
                current = None
                line += 1
                continue
            else:
                col = self._content_col(container, line)
            begin = self.offset(line, col) if col else self._reached(container, line)
            end = self.line_end(line)
            text = self.source[begin:end] if begin <= end else b""
            if not text.strip(b" \t"):
                current = None
                if line > last:
                    break
                line += 1
                continue
            is_lazy = not col and container.type != "document"
            # R42: a "[" starts a new definition once the current one is whole,
            # "[a]:" followed by "[x]" is one definition, of destination [x] (E47)
            if _LINK_REF_DEF_START.match(text) and (current is None or _defs_only(texts, lazy)):
                # R16: its indentation is its own, but not the blank after a checkbox
                bare = not col or self._after_checkbox(container, line)
                lead = len(text) - len(text.lstrip(b" \t")) if bare else 0
                node = TreeNode(Kind.LINK_REF_DEF, begin + lead, end, margin=margin)
                if is_lazy and current is not None:
                    # R43: a frame between the two would end their paragraph, the
                    # lazy line would leave the container
                    current.begin = node.begin = HOIST
                current = node
                defs.append(current)
                texts, lazy = [], []
            elif current is None:
                line += 1
                continue
            current.end = end
            texts.append(text.lstrip(b" \t") if is_lazy else text)
            lazy.append(is_lazy)
            if is_lazy:
                self.lazy_def_lines.add(line)
            line += 1
        return defs

    # --- extent of containers ------------------------------------------

    def _extend(self, node: AstNode, limit: int) -> None:
        """Record the last line of `node` and its descendants, `limit` at most.

        cmark.parse() ends a container with its last child, but link
        reference definitions after that child are not AST nodes: the
        lines that follow and still belong to the container (indented
        enough for an item, carrying the ">" of a quote) extend it.

        Spec: R43
        """
        if node.type == "document":
            last = limit
        elif node.type in ("block_quote", "item"):
            last = node.end_line
            for line in range(node.end_line + 1, limit + 1):
                inside = self._inside(node, line)
                if inside is None:
                    break
                if inside:
                    last = line
        else:
            last = node.end_line
        children = node.children
        for i, child in enumerate(children):
            child_limit = children[i + 1].start_line - 1 if i + 1 < len(children) else (
                limit if node.type == "list" else last
            )
            self._extend(child, max(child_limit, child.end_line))
        if node.type == "list" and children:
            last = self.last_line[id(children[-1])]
        self.last_line[id(node)] = last

    def _inside(self, container: AstNode, line: int) -> bool | None:
        """Whether `line` lies in `container`: None if not, False if blank there, True.

        Spec: R38
        """
        text = self.lines.content(line)
        if container.type == "document":
            return bool(text.strip(b" \t"))
        if container.type == "list":
            parent = self.parent[id(container)]
            return self._inside(parent, line) if parent is not None else None
        parent = self.parent[id(container)]
        if parent is None or self._inside(parent, line) is None:
            return None
        if container.type == "block_quote":
            col = self._content_col(container, line)
            if col == 0:
                return None
            return bool(text[col - 1 :].strip(b" \t"))
        # R38: an item, content indented to its content column (virtual columns)
        outer = self._content_col(self.parent[id(parent)] or parent, line) if parent.type == "list" else 0
        if outer == 0:
            return None
        rest = text[outer - 1 :]
        if not rest.strip(b" \t>"):
            return False
        lead = len(rest) - len(rest.lstrip(b" \t"))
        target = self._content_vcol_on(container, line)
        return True if target is not None and vcol(text, outer - 1 + lead) >= target else None

    # --- columns of container content -----------------------------------

    def _item_content_vcol(self, item: AstNode) -> int:
        """Virtual column (0-based) where the content of `item` starts (GFM §5.2).

        Spec: R38
        """
        line = self.lines.content(item.start_line)
        pos = item.start_col - 1
        m = _LIST_MARKER.match(line, pos)
        if m is None:  # not expected: fall back on the first child
            col = item.children[0].start_col if item.children else item.start_col + 2
            return vcol(line, col - 1)
        after = m.end()
        marker_end = vcol(line, after)
        rest = line[after:]
        lead = len(rest) - len(rest.lstrip(b" \t"))
        width = vcol(line, after + lead) - marker_end  # columns of blanks after the marker
        if not rest.strip(b" \t") or width > 4 or width == 0:
            return marker_end + 1  # marker + one column
        return marker_end + width

    def _container_vcol(self, item: AstNode) -> int:
        """Virtual column where the content of the item's container starts, on its line."""
        found = self._container_vcol_on(item, item.start_line)
        return found if found is not None else 0

    def _container_vcol_on(self, item: AstNode, line: int) -> int | None:
        """Virtual column where the item's container's content starts on `line`; None if lazy there.

        Spec: R38
        """
        parent = self.parent[id(item)]  # the list
        container = self.parent[id(parent)] if parent is not None else None
        if container is None or container.type == "document":
            return 0
        if container.type == "item":
            return self._content_vcol_on(container, line)
        col = self._content_col(container, line)
        if not col:
            return None
        text = self.lines.content(line)
        if col >= 3 and text[col - 2] == 0x09 and text[col - 3] == ord(">"):
            # R38: ">" then a tab, the optional space takes one column of the tab (GFM §5.1)
            return vcol(text, col - 3) + 2
        return vcol(text, col - 1)

    def _content_vcol_on(self, item: AstNode, line: int) -> int | None:
        """Virtual column where the item's content starts on `line`; None if its container is lazy there.

        The item's content column is kept relative to its container's
        content, which can start at another column on another line
        (" > 1." then ">    a").

        Spec: R38
        """
        if line == item.start_line:
            return self.content_vcols[id(item)]
        base = self._container_vcol_on(item, line)
        if base is None:
            return None
        return base + self.content_vcols[id(item)] - self._container_vcol(item)

    def _outer_col(self, item: AstNode, line: int) -> int:
        """1-based column where the item's container's content starts on `line`; 0 if lazy."""
        parent = self.parent[id(item)]  # the list
        container = self.parent[id(parent)] if parent is not None else None
        return self._content_col(container, line) if container is not None else 1

    def _content_col(self, container: AstNode, line: int) -> int:
        """1-based column where `container`'s content starts on `line`; 0 if unknown.

        Spec: R38
        """
        if container.type == "document":
            return len(_BOM) + 1 if line == 1 and self.source.startswith(_BOM) else 1
        if container.type == "item":
            if line == container.start_line:
                col = self.content_cols[id(container)]
                if container.task_checked is not None:  # R38: after its checkbox
                    m = _CHECKBOX.match(self.lines.content(line), col - 1)
                    if m:
                        return m.end() + 1
                return col
            target = self._content_vcol_on(container, line)
            outer = self._outer_col(container, line)
            if target is None or not outer:
                return 0
            text = self.lines.content(line)
            first = outer - 1 + len(text[outer - 1 :]) - len(text[outer - 1 :].lstrip(b" \t"))
            if first < len(text) and vcol(text, first) < target:
                return 0  # R38: not indented into the item, a lazy line or a line after it
            return _index_at_vcol(text, target) + 1
        if container.type == "block_quote":
            parent = self.parent[id(container)]
            outer = self._content_col(parent, line) if parent is not None else 1
            if outer == 0:
                return 0
            text = self.lines.content(line)
            pos = outer - 1
            while pos < len(text) and pos < outer - 1 + 3 and text[pos] == 0x20:
                pos += 1
            if pos < len(text) and text[pos] == ord(">"):  # R38: the optional space after it is the quote's
                pos += 1
                if pos < len(text) and text[pos] in (0x20, 0x09):
                    pos += 1
                return pos + 1
            return 0  # a lazy line
        parent = self.parent[id(container)]  # a list: its own container
        return self._content_col(parent, line) if parent is not None else 1
