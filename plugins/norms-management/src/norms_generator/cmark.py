"""ctypes binding to the cmark-gfm library shipped inside `cmarkgfm`.

`cmarkgfm` exposes no AST to Python, but its compiled extension module
(`cmarkgfm._cmark`) embeds the whole cmark-gfm C library, so `ctypes`
reaches the C API directly. `parse()` returns the block-level AST as
`AstNode` (model.py); inline nodes (text, emph, code, link, ...) are not
returned.

Parsing
    Options: CMARK_OPT_DEFAULT (0). CMARK_OPT_SOURCEPOS only adds
    `data-sourcepos` to rendered HTML; positions are always tracked in
    the AST. Extensions attached: table, strikethrough, autolink,
    tagfilter, tasklist. No footnotes. Library version: `version()`
    ("0.29.0.gfm.13" when this was written).

Type strings
    `AstNode.type` is cmark's type string, except that two extension
    overrides are folded back into the base type, so that downstream
    code has one name per kind:
      "tasklist"     -> "item"       (task_checked is True/False)
      "table_header" -> "table_row"  (is_header is True)
    The other block types are: document, block_quote, list, item,
    code_block, html_block, paragraph, heading, thematic_break, table,
    table_row, table_cell. Link reference definitions are not nodes.

Positions
    Lines are 1-based. Columns are 1-based BYTE columns counted from the
    real start of the line (container prefixes such as "> " or list
    indentation included; a tab is one byte; a UTF-8 BOM is three bytes;
    "é" is 2 bytes, "⟬" is 3). Line endings are "\\n", "\\r\\n" or a lone
    "\\r", as in cmark. An end position is INCLUSIVE: (end_line, end_col)
    is the last byte of the node. `line_col_to_offset()` maps (line, col)
    to a byte offset; `node_span()` gives [start, end) offsets.

    `parse()` repairs cmark-gfm's positions so that every block obeys one
    rule: it starts at its first byte and ends at the last byte of its
    last line, trailing whitespace of that line included, never on a
    trailing blank line, never past its parent. `parse_raw()` returns the
    positions exactly as cmark-gfm reports them. What cmark-gfm reports,
    checked empirically (tests/test_cmark.py pins every case):

    - paragraph: start = first non-blank byte; end = last byte of its
      last line (trailing spaces included). Correct as reported.
    - ATX heading: start = the first "#"; end = last byte of the TEXT:
      the closing "#" sequence and trailing whitespace are excluded
      ("## Numbers ##" ends at the "s"). Repaired end = end of the line;
      the text end is kept in text_end_line/text_end_col.
    - setext heading: start = first byte of the text; end = end of the
      underline, BUT (L, 0) when a blank line follows, and the first
      byte of the NEXT line when a block follows directly
      ("T\\n===\\nx" reports the heading ending at (3, 1), on "x"), and on
      the line after it when a link reference definition follows. The
      underline is the last line, up to cmark's end line, that looks like
      one and starts no block (a text line may look like one too:
      "[r]: /u\\n---\\nSet\\n---" is the heading "---\\nSet"). Repaired
      end = end of the underline; text_end = last non-blank byte of the
      last text line. `setext` is True.
    - fenced code: start = first fence byte; end = end of the closing
      fence line (trailing spaces included). Unclosed fence closed by
      its container: the end runs past its parent, onto the line that
      closed the container. Repaired from the literal's line count; an
      unclosed fence has `open` set.
    - indented code: start = first byte after the 4 columns of
      indentation (may be a tab only partly consumed: "-\\t\\tcode" starts
      on the second tab and the literal is "  code"); end = (L, 0) when a
      blank line follows, L being the LAST of the trailing blank lines,
      or the ">" of a blank quote line. Repaired from the literal.
    - html block: end = last line, but for types 1-5 containing a blank
      line ("<!-- a\\n\\nb -->") cmark reports (2, 0), inside the block.
      Repaired from the literal's line count. A block of type 1-5 without
      its closing sequence has `open` set.
    - thematic break: (L, 0) when a blank line follows. Repaired.
    - list, item: end = (L, 0) when a blank line follows, or (L, 1) on
      the ">" of a blank quote line. Block quote: includes trailing ">"
      lines. Repaired: a container ends where its last child ends; an
      empty item ("-") keeps its own line.
    - task item: the item starts at "-"; its paragraph starts after the
      checkbox ("- [ ] t": paragraph at column 7).
    - link reference definitions at the start of a paragraph (or setext
      heading) are INSIDE its reported span ("[a]: /u\\nText" reports
      the paragraph at (1, 1)-(2, 4)), while its inline positions are
      relative to the remaining text, and the inlines after a hard line
      break, or of a link over two lines, are reported on the line
      before: they cannot count the lines left. Repaired: the start moves
      to the first line after the definitions, which are the longest run
      of first lines that, parsed alone, renders no block. A paragraph
      that a table interrupts keeps its definitions as text (cmark-gfm
      does not extract them there); it has `before_table` set.
    - table: start = start of the header row; end = end of the last row
      (or of the delimiter row when there is no body row). The delimiter
      row is not a node.
    - table row: start = first byte of the row (a leading "|" or the
      first cell); end = last byte of the line, trailing spaces and text
      after the last column included ("| c | extra" with one column).
    - table cell: the bytes between its pipes, padding included
      ("| Type |" -> the cell is " Type "); without a leading pipe, the
      first cell starts at the row start. An empty cell "||" has
      end_col = start_col - 1 (an empty span). A cell missing from a
      short row is synthesized by cmark-gfm at (L, 0)-(L, 0); repaired
      to an empty span just past the end of its row. BUG: the columns of
      a body row are counted from the row's first non-blank byte as if
      its line started like the header's line, so they are wrong when it
      does not (an indented row, a BOM before the header, a row in a task
      item or after "-\\t"). Not repaired here: tree.py reads rows and
      cells from the source; the row's line is right.
    - BUG, table right after a paragraph ("x\\n| a |\\n|---|"): the
      paragraph is reported at (0, 0)-(0, 0); the table and its header
      row are reported on the PARAGRAPH's first line, and the header
      columns count bytes into the paragraph's content (prefixes and
      leading blanks stripped, lines joined by "\\n"). Body rows are
      correct. Repaired: the header line is the delimiter line minus
      one; header columns are shifted so that the header row ends at
      the end of its real line; the paragraph runs from the table's
      reported start to the line before the header.
    - document: repaired to (1, 1) through the last non-blank line; an
      empty source gives (1, 1)-(1, 0), the empty span [0, 0).
    - positions of soft breaks are (0, 0); inline positions are only used
      to count the text lines of a paragraph after link ref defs.
    - NUL: cmark-gfm turns each NUL byte into U+FFFD (3 bytes), so the
      columns after it on its line count 2 bytes too many. parse() feeds
      cmark-gfm 0x01 in place of NUL, which keeps the columns exact.

    Detecting setext vs ATX: a heading is ATX when its first byte starts
    "#{1,6}" followed by a blank or the end of the line; "#5 bolts\\n==="
    is setext. A paragraph followed by "---" with no blank line is a
    setext heading (foundation has one, by accident or not:
    specs/components/framework/libraries/server.md line 187).

Note: D1, D2

Spec: R3, R16, R17, R44, R45, R48
"""

from __future__ import annotations

import ctypes
import re
from collections.abc import Callable

import cmarkgfm._cmark  # the compiled extension that embeds libcmark-gfm

from norms_generator.model import AstNode

_lib = ctypes.CDLL(cmarkgfm._cmark.__file__)
_P = ctypes.c_void_p

EXTENSIONS: tuple[str, ...] = ("table", "strikethrough", "autolink", "tagfilter", "tasklist")  # R17: the extensions attached
CMARK_OPT_DEFAULT = 0

_NODE_TYPE_MASK = 0xC000
_NODE_TYPE_BLOCK = 0x8000

_LIST_TYPES = {1: "bullet", 2: "ordered"}
_TYPE_ALIASES = {"tasklist": "item", "table_header": "table_row"}
_CONTAINERS = {"document", "block_quote", "list", "item"}


def _bind(name: str, restype: object, *argtypes: object) -> Callable[..., object]:
    """Return the C function `name` with its result and argument types set."""
    fn = getattr(_lib, name)
    fn.restype = restype
    fn.argtypes = list(argtypes)
    return fn


_version_string = _bind("cmark_version_string", ctypes.c_char_p)
_ensure_registered = _bind("cmark_gfm_core_extensions_ensure_registered", None)
_parser_new = _bind("cmark_parser_new", _P, ctypes.c_int)
_parser_free = _bind("cmark_parser_free", None, _P)
_parser_feed = _bind("cmark_parser_feed", None, _P, ctypes.c_char_p, ctypes.c_size_t)
_parser_finish = _bind("cmark_parser_finish", _P, _P)
_find_ext = _bind("cmark_find_syntax_extension", _P, ctypes.c_char_p)
_attach_ext = _bind("cmark_parser_attach_syntax_extension", ctypes.c_int, _P, _P)
_node_free = _bind("cmark_node_free", None, _P)
_first_child = _bind("cmark_node_first_child", _P, _P)
_next = _bind("cmark_node_next", _P, _P)
_get_type = _bind("cmark_node_get_type", ctypes.c_int, _P)
_get_type_string = _bind("cmark_node_get_type_string", ctypes.c_char_p, _P)
_start_line = _bind("cmark_node_get_start_line", ctypes.c_int, _P)
_start_col = _bind("cmark_node_get_start_column", ctypes.c_int, _P)
_end_line = _bind("cmark_node_get_end_line", ctypes.c_int, _P)
_end_col = _bind("cmark_node_get_end_column", ctypes.c_int, _P)
_literal = _bind("cmark_node_get_literal", ctypes.c_char_p, _P)
_heading_level = _bind("cmark_node_get_heading_level", ctypes.c_int, _P)
_list_type = _bind("cmark_node_get_list_type", ctypes.c_int, _P)
_list_tight = _bind("cmark_node_get_list_tight", ctypes.c_int, _P)
_fence_info = _bind("cmark_node_get_fence_info", ctypes.c_char_p, _P)
# int cmark_node_get_fenced(node, int *length, int *offset, char *character)
_fenced = _bind(
    "cmark_node_get_fenced",
    ctypes.c_int,
    _P,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_char),
)
_row_is_header = _bind("cmark_gfm_extensions_get_table_row_is_header", ctypes.c_int, _P)
_task_checked = _bind("cmark_gfm_extensions_get_tasklist_item_checked", ctypes.c_bool, _P)
_render_xml = _bind("cmark_render_xml", _P, _P, ctypes.c_int)  # char*, freed with free()

_libc = ctypes.CDLL(None)
_free = _libc.free
_free.restype = None
_free.argtypes = [_P]

_LINE_END = re.compile(rb"\r\n|\r|\n")


def version() -> str:
    """Return cmark-gfm's version string, e.g. "0.29.0.gfm.13"."""
    return _version_string().decode()


# --- source lines -------------------------------------------------------------


class SourceLines:
    """Line table of a source: maps cmark (line, col) to byte offsets."""

    def __init__(self, source: bytes) -> None:
        self.source = source
        self.starts: list[int] = [0]  # offset of each line's first byte
        self.ends: list[int] = []  # offset just past each line's content (before EOL)
        for m in _LINE_END.finditer(source):
            self.ends.append(m.start())
            self.starts.append(m.end())
        self.ends.append(len(source))

    @property
    def count(self) -> int:
        """Number of lines that hold bytes (a final EOL opens no new line)."""
        n = len(self.starts)
        if n > 1 and self.starts[-1] == len(self.source):
            n -= 1
        return n

    def offset(self, line: int, col: int) -> int:
        """Byte offset of 1-based byte column `col` of 1-based `line`.

        col 0 gives the offset just before the line (the last byte of the
        previous line's EOL); col = width + 1 gives the offset of the EOL.
        """
        return self.starts[line - 1] + col - 1

    def content(self, line: int) -> bytes:
        """The bytes of `line` without its line ending."""
        return self.source[self.starts[line - 1] : self.ends[line - 1]]

    def width(self, line: int) -> int:
        """Number of bytes of `line` without its line ending."""
        return self.ends[line - 1] - self.starts[line - 1]


def line_col_to_offset(source: bytes) -> Callable[[int, int], int]:
    """Return a function mapping cmark's (line, col) to a byte offset of `source`."""
    return SourceLines(source).offset


def node_span(node: AstNode, offset: Callable[[int, int], int]) -> tuple[int, int]:
    """Return [start, end) byte offsets of `node`, `offset` from line_col_to_offset.

    Spec: R16
    """
    return offset(node.start_line, node.start_col), offset(node.end_line, node.end_col) + 1


# --- parsing --------------------------------------------------------------------


class _Raw:
    """What the raw walk records besides the AstNode tree."""

    def __init__(self) -> None:
        self.inline_lines: dict[int, int] = {}  # id(AstNode) -> max inline line
        self.fences: dict[int, tuple[bytes, int]] = {}  # id(AstNode) -> (char, length)
        self.block_starts: set[int] = set()  # start lines of every block


def _max_inline_line(node: int) -> int:
    """Largest line number reported by the inline descendants of `node`."""
    best = 0
    child = _first_child(node)
    while child:
        best = max(best, _start_line(child), _end_line(child), _max_inline_line(child))
        child = _next(child)
    return best


def _convert(node: int, raw: _Raw) -> AstNode:
    """Build the AstNode of the block `node` and of its block descendants."""
    type_string = _get_type_string(node).decode()
    ast = AstNode(
        type=_TYPE_ALIASES.get(type_string, type_string),
        start_line=_start_line(node),
        start_col=_start_col(node),
        end_line=_end_line(node),
        end_col=_end_col(node),
    )
    raw.block_starts.add(ast.start_line)
    lit = _literal(node)
    if ast.type in ("code_block", "html_block"):
        ast.literal = (lit or b"").decode("utf-8", "surrogateescape")
    if ast.type == "code_block":
        length, offset, char = ctypes.c_int(0), ctypes.c_int(0), ctypes.c_char(b"\0")
        if _fenced(node, ctypes.byref(length), ctypes.byref(offset), ctypes.byref(char)):
            info = _fence_info(node) or b""
            ast.fence_info = info.decode("utf-8", "surrogateescape")
            raw.fences[id(ast)] = (char.value, length.value)
    elif ast.type == "heading":
        ast.heading_level = _heading_level(node)
    elif ast.type == "list":
        ast.list_type = _LIST_TYPES.get(_list_type(node))
        ast.list_tight = bool(_list_tight(node))
    elif ast.type == "table_row":
        ast.is_header = bool(_row_is_header(node))
    if type_string == "tasklist":
        ast.task_checked = bool(_task_checked(node))
    if ast.type in ("paragraph", "heading"):
        raw.inline_lines[id(ast)] = _max_inline_line(node)
    child = _first_child(node)
    while child:
        if _get_type(child) & _NODE_TYPE_MASK == _NODE_TYPE_BLOCK:
            ast.children.append(_convert(child, raw))
        child = _next(child)
    return ast


def _parse(source: bytes) -> tuple[AstNode, _Raw]:
    """Parse with cmark-gfm and its extensions; return the raw AstNode tree; free C memory.

    Spec: R17
    """
    _ensure_registered()
    parser = _parser_new(CMARK_OPT_DEFAULT)
    if not parser:
        raise MemoryError("cmark_parser_new failed")
    doc = None
    try:
        for name in EXTENSIONS:
            ext = _find_ext(name.encode())
            if not ext or not _attach_ext(parser, ext):
                raise RuntimeError(f"cmark-gfm extension {name!r} unavailable")
        _parser_feed(parser, source, len(source))
        doc = _parser_finish(parser)
        raw = _Raw()
        return _convert(doc, raw), raw
    finally:
        if doc:
            _node_free(doc)
        _parser_free(parser)


def parse_raw(source: bytes) -> AstNode:
    """Parse `source` and return the AST with cmark-gfm's positions untouched."""
    return _parse(source)[0]


def parse(source: bytes) -> AstNode:
    """Parse `source` (UTF-8 GFM) and return its document AstNode, positions repaired.

    cmark-gfm replaces each NUL byte with U+FFFD, three bytes, which
    shifts every column after it on its line by 2. The source is parsed
    with each NUL replaced by the one byte 0x01 instead (like U+FFFD, it
    is neither a blank nor punctuation), so that columns stay exact source
    bytes; literals then hold 0x01 where the source holds NUL.

    Spec: R3, R16
    """
    root, raw = _parse(source.replace(b"\0", b"\x01"))
    _Repair(SourceLines(source), raw).node(root, in_quote=0)
    return root


def render_xml(source: bytes) -> bytes:
    """Parse `source` with the GFM extensions and return cmark-gfm's XML rendering.

    The XML holds inline nodes too (text, code, links, ...), so it serves
    to compare two sources block by block and text by text (verify.py).

    Spec: R64
    """
    _ensure_registered()
    parser = _parser_new(CMARK_OPT_DEFAULT)
    if not parser:
        raise MemoryError("cmark_parser_new failed")
    doc = None
    try:
        for name in EXTENSIONS:
            ext = _find_ext(name.encode())
            if not ext or not _attach_ext(parser, ext):
                raise RuntimeError(f"cmark-gfm extension {name!r} unavailable")
        _parser_feed(parser, source, len(source))
        doc = _parser_finish(parser)
        rendered = _render_xml(doc, CMARK_OPT_DEFAULT)
        try:
            return ctypes.string_at(rendered)
        finally:
            _free(rendered)
    finally:
        if doc:
            _node_free(doc)
        _parser_free(parser)


def parse_str(text: str) -> AstNode:
    """parse() of `text` encoded as UTF-8."""
    return parse(text.encode("utf-8"))


# --- repair of positions -------------------------------------------------------

_ATX_OPEN = re.compile(rb"#{1,6}(?:[ \t]|$)")
_SETEXT_UNDERLINE = re.compile(rb"[ \t>]*(?:=+|-+)[ \t]*")


def _count_lines(text: str) -> int:
    """Number of lines of a cmark literal (each ends with a line ending)."""
    data = text.encode("utf-8", "surrogateescape")
    if not data:
        return 0
    n = len(_LINE_END.findall(data))
    return n if _LINE_END.search(data[-1:]) else n + 1


# HTML blocks of types 1-5 end at a closing sequence, not at a blank line (GFM §4.6;
# cmark-gfm counts <textarea> in type 1)
# R48: without that closing sequence they are unclosed
_HTML_OPEN_END = (
    (re.compile(r"<(?:script|pre|style|textarea)(?:\s|>|$)", re.I), re.compile(r"</(?:script|pre|style|textarea)>", re.I)),
    (re.compile(r"<!--"), re.compile(r"-->")),
    (re.compile(r"<\?"), re.compile(r"\?>")),
    (re.compile(r"<![A-Za-z]"), re.compile(r">")),
    (re.compile(r"<!\[CDATA\["), re.compile(r"\]\]>")),
)


def quote_content(line: bytes, depth: int) -> bytes:
    """`line` after the ">" prefixes of `depth` block quotes, each after up to 3 spaces.

    Stops at a lazy line (no ">" where one is expected); a ">" past
    `depth` quotes is content.
    """
    pos = 0
    for _ in range(depth):
        start = pos
        while pos < len(line) and pos - start < 3 and line[pos] == 0x20:
            pos += 1
        if line[pos : pos + 1] != b">":
            return line[start:]
        pos += 1
    return line[pos:]


def html_block_is_open(literal: str) -> bool:
    """True if an HTML block of type 1-5 has no closing sequence: it runs to its container's end.

    Spec: R48 (E62)
    """
    text = literal.lstrip(" \t")  # a tab partly taken by its container stays in the literal
    for start, end in _HTML_OPEN_END:
        m = start.match(text)
        if m:
            return end.search(text, m.end()) is None
    return False


def only_link_ref_defs(text: bytes) -> bool:
    """True if `text`, parsed alone, holds only link reference definitions (no block)."""
    return bool(text.strip()) and not _parse(text.replace(b"\0", b"\x01"))[0].children


_only_link_ref_defs = only_link_ref_defs


class _Repair:
    """Rewrites raw cmark-gfm positions to the rule stated in the module doc."""

    def __init__(self, lines: SourceLines, raw: _Raw) -> None:
        self.lines = lines
        self.raw = raw
        self.task_heads: set[int] = set()  # id() of the blocks on a task item's marker line

    def _blank(self, line: int, in_quote: int) -> bool:
        """True if `line` holds no content: only blanks, after the ">" of its `in_quote` quotes.

        A ">" past those is content ("> >" is not blank in one quote:
        it holds a nested quote, or the ">" of an HTML or code block).

        Spec: R47 (E60)
        """
        return not quote_content(self.lines.content(line), in_quote).strip(b" \t")

    def _trim(self, line: int, floor: int, in_quote: int) -> int:
        """Step back from `line` over blank lines, never above `floor`."""
        line = min(line, self.lines.count)
        while line > floor and self._blank(line, in_quote):
            line -= 1
        return line

    def _end_at(self, node: AstNode, line: int) -> None:
        """Make `node` end at the last byte of `line`, its trailing blanks included.

        Spec: R16
        """
        node.end_line = line
        node.end_col = self.lines.width(line)

    def node(self, node: AstNode, in_quote: int) -> None:
        """Repair `node` and its descendants in place; `in_quote` is its number of enclosing quotes."""
        child_quote = in_quote + (node.type == "block_quote")
        if node.type == "item" and node.task_checked is not None:
            # R18: on a task item's marker line a heading is setext: its line starts
            # with the checkbox, a paragraph, even when "#" follows (E33)
            self.task_heads.update(id(c) for c in node.children if c.start_line == node.start_line)
        for i, child in enumerate(node.children):
            if (
                child.type == "paragraph"
                and child.start_line == 0
                and i + 1 < len(node.children)
                and node.children[i + 1].type == "table"
            ):
                self._paragraph_before_table(child, node.children[i + 1])
            elif child.type == "table" and not (i and node.children[i - 1].type == "paragraph" and node.children[i - 1].start_line == 0):
                self._header_line(child)
        for child in node.children:
            self.node(child, child_quote)
        handler = getattr(self, "_" + node.type, None)
        if handler is not None:
            handler(node, in_quote)
        elif node.type in _CONTAINERS:
            self._container(node, in_quote)

    # containers

    def _container(self, node: AstNode, in_quote: int) -> None:
        if node.children:
            last = node.children[-1]
            node.end_line, node.end_col = last.end_line, last.end_col
        else:  # an empty item: its own line
            self._end_at(node, node.start_line)

    def _document(self, node: AstNode, in_quote: int) -> None:
        node.start_line, node.start_col = 1, 1
        self._end_at(node, self._trim(self.lines.count, 1, in_quote=0))

    # leaves

    def _paragraph(self, node: AstNode, in_quote: int) -> None:
        self._end_at(node, node.end_line)
        self._skip_link_ref_defs(node, node.end_line)

    def _thematic_break(self, node: AstNode, in_quote: int) -> None:
        self._end_at(node, node.start_line)

    def _heading(self, node: AstNode, in_quote: int) -> None:
        first = self.lines.content(node.start_line)
        opening = None if id(node) in self.task_heads else _ATX_OPEN.match(first, node.start_col - 1)
        if opening:
            hashes = len(opening.group(0).rstrip(b" \t"))
            # R51: an empty heading ("  #", "> #") is reported ending before it
            # starts; its text ends with its opening sequence (E67, E68)
            last = max(node.end_col, node.start_col + hashes - 1)
            node.text_end_line, node.text_end_col = node.start_line, last
            self._end_at(node, node.start_line)
            return
        node.setext = True
        # R18: the text end is where its ID goes (E3). The underline is its
        # last line: cmark's end line, or the line before when cmark ended it
        # on what follows (a blank line, a block, a definition); a line of the
        # text may look like an underline too ("[r]: /u\n---\nSet\n---" is the
        # heading "---\nSet")
        underline = node.end_line - 1
        for line in range(min(node.end_line, self.lines.count), node.start_line, -1):
            if line not in self.raw.block_starts and _SETEXT_UNDERLINE.fullmatch(self.lines.content(line)):
                underline = line
                break
        text_line = underline - 1
        node.text_end_line = text_line
        node.text_end_col = len(self.lines.content(text_line).rstrip(b" \t"))
        self._end_at(node, underline)
        self._skip_link_ref_defs(node, text_line)

    def _code_block(self, node: AstNode, in_quote: int) -> None:
        n = _count_lines(node.literal or "")
        fence = self.raw.fences.get(id(node))
        if fence is None:  # indented: one source line per literal line
            self._end_at(node, node.start_line + n - 1)
            return
        char, length = fence
        closing = node.start_line + n + 1
        pattern = rb"[ \t>]*" + re.escape(char) + b"{%d,}[ \t]*" % length
        if (
            closing <= self.lines.count
            and node.end_line >= closing
            and closing not in self.raw.block_starts
            and re.fullmatch(pattern, self.lines.content(closing))
        ):
            self._end_at(node, closing)
        else:  # R16, R48: unclosed, it ends with its content, blank lines dropped; tree.py runs it on
            node.open = True
            self._end_at(node, self._trim(node.start_line + n, node.start_line, in_quote))

    def _html_block(self, node: AstNode, in_quote: int) -> None:
        n = _count_lines(node.literal or "")
        last = node.start_line + max(n, 1) - 1
        node.open = html_block_is_open(node.literal or "")
        self._end_at(node, self._trim(last, node.start_line, in_quote))

    def _skip_link_ref_defs(self, node: AstNode, last_text_line: int) -> None:
        """Move the start of a paragraph/setext heading past leading link ref defs.

        cmark-gfm keeps the definitions inside the block's span and gives
        no trace of where they end. They always end at a line end, so the
        definitions are the longest run of the block's first lines that,
        parsed alone, is nothing but definitions (it renders no block). A
        paragraph that a table interrupts keeps its definitions: cmark-gfm
        does not extract them there (it renders "[r]: /u" as text).

        Spec: R44 (E50)
        """
        if node.before_table:
            return
        first = self.lines.content(node.start_line)[node.start_col - 1 :]
        if not first.startswith(b"["):
            return
        texts = [first] + [
            self.lines.content(line).lstrip(b" \t>") for line in range(node.start_line + 1, last_text_line + 1)
        ]
        if b"]:" not in b"\n".join(texts):
            return
        defs = 0
        for k in range(1, len(texts)):
            if _only_link_ref_defs(b"\n".join(texts[:k])):
                defs = k
        if not defs:
            return
        start = node.start_line + defs
        content = self.lines.content(start)
        node.start_line = start
        node.start_col = len(content) - len(content.lstrip(b" \t>")) + 1

    # tables

    def _table(self, node: AstNode, in_quote: int) -> None:
        rows = node.children
        if rows:
            node.start_line, node.start_col = rows[0].start_line, rows[0].start_col
        if len(rows) > 1:
            last = rows[-1].end_line
        else:  # header only: ends with the delimiter row
            last = node.start_line + 1
        self._end_at(node, last)

    def _table_row(self, node: AstNode, in_quote: int) -> None:
        self._end_at(node, node.start_line)
        for cell in node.children:
            if cell.start_col == 0:  # missing from a short row: empty span past the row
                cell.start_line = cell.end_line = node.start_line
                cell.start_col = node.end_col + 1
                cell.end_col = node.end_col

    def _header_line(self, table: AstNode) -> int:
        """Move a table's header row to its line, the delimiter row's line minus one; return it.

        cmark-gfm reports the header row on the first line of the paragraph
        it came from, with columns counted into that paragraph's content:
        wrong when the paragraph began with definitions it consumed whole
        ("[a]: /u" then "---" then "|-|": the header is "---").

        Spec: R44 (E66)
        """
        rows = table.children
        delimiter = rows[1].start_line - 1 if len(rows) > 1 else table.end_line
        header_line = delimiter - 1
        header = rows[0]
        if header.start_line == header_line:
            return header_line
        delta = header.end_col - self.lines.width(header_line)
        for n in [header, *header.children]:
            n.start_line = n.end_line = header_line
            n.start_col -= delta
            n.end_col -= delta
        if header.children:
            first = header.children[0].start_col
            line = self.lines.content(header_line)
            header.start_col = first - 1 if first >= 2 and line[first - 2 : first - 1] == b"|" else first
        table.start_line, table.start_col = header.start_line, header.start_col
        return header_line

    def _paragraph_before_table(self, para: AstNode, table: AstNode) -> None:
        """Repair cmark-gfm's positions of a table that interrupts a paragraph.

        Spec: R44
        """
        para.before_table = True
        start = table.start_line, table.start_col
        header_line = self._header_line(table)
        para.start_line, para.start_col = start
        self._end_at(para, header_line - 1)
