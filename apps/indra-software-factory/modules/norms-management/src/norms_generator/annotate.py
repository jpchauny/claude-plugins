"""Norms tree + IDs -> annotated copy of a spec file.

`annotate(source, root)` writes each node's ID into the source by pure
insertion and returns the annotated bytes with the list of
`Insertion`s; `strip()` removes them again and gives back the source
byte for byte.

Where an ID goes: at the end of the node's text when it can
(`TreeNode.anchor` >= 0, set by tree.py), as " ⟬ID⟭" (always a space
before it, or the source's tab after "-\t"); otherwise the node is
framed with "⟬ID begin⟭" on a line of its own before it and
"⟬ID end⟭" on a line of its own after it.

    inline   heading (before an ATX closing sequence; at the end of
             the last text line of a setext heading), paragraph of
             one line, item (end of its own text), table cell (end of
             its text), body row (after its closing pipe, as an extra
             cell that is not displayed)
    framed   section, paragraph of several lines, code block, HTML
             block, link reference definition, table, block quote, list
    file     "⟬TYP⟭" on a line of its own at the start, no end

Marker lines: a frame marker goes in the gap between
two blocks, at the start of a line, written with the node's `margin`
(the item content indentation and "> " for each enclosing block quote).
It has a blank line before and after it (a bare ">" inside a quote),
except at the start or end of the file; blank lines already in the gap
are reused. Several markers at one place are written ends first,
innermost first (sections close innermost first), then begins,
outermost first.

A node that starts on the line of its item's marker ("- ```" or "- - a")
cannot be framed at the start of a line: the markers go right before it
and the rest of the line moves to a new line, indented by the item's
content indentation (`TreeNode.inner`). An item whose first block is not
a paragraph has its ID right after its marker ("- ⟬TYP-3⟭"), followed by
a blank line when its first block was on the same line. When
moving the rest of the line would change how it parses ("- - [ ] a":
on a line of its own, the inner item becomes a task item), the item's
ID goes at the end of its first line instead, and so does the ID of a
node framed there. Whether the move is safe is probed on the whole
file (structure.py), and so is an ID at the end of that line: it can
land in an indented code block, a code span or a link that runs on, or
turn a definition into a paragraph. Then the node is framed at the
start and end of the top-level block that holds it.

A rest of line that moves keeps its column, counted from its quote's
content, and its tabs their width: it is written after the line's own
prefix, ">" kept and every other byte a space. Two moves on one
line are computed and probed together.

The whole annotated file is checked at the end; nodes whose placements
clash are framed at the bounds of their top-level block.

An unclosed fenced code block or HTML block is framed like any other
block, and nothing else is written: no closing fence, no closing tag.
It runs to the end of its container, so its end marker falls inside it
for a parser.

An empty item's ID has the blank `TreeNode.pad` before it and, when
`TreeNode.brk` is set, a blank line after it. A table cell's
`TreeNode.lead` ("|") is written at its row's start, after any marker
line there.

Line endings: an inserted line ends like the file's lines ("\r\n" in a
file that has one, else "\r" in a file of lone "\r", else "\n"), but
after a lone "\r" it ends with "\r", so that the inserted line ending
does not join the source's "\r" into one "\r\n".

Spec: R3, R18, R23, R24, R25, R26, R27, R29, R30, R35, R36, R37, R38, R39, R40, R41, R42, R43, R44, R45, R46, R47, R48, R49, R50, R51, R52 (E2, E3, E7, E8, E10, E12, E13, E14, E15, E32, E36, E61, E64, E65, E66)
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass, field

from norms_generator.model import Insertion, Kind, TreeNode
from norms_generator.structure import Structure, block_structure
from norms_generator.tree import HOIST, blank_line, build_tree, is_blank_under, line_ending, vcol, walk

_EOL = re.compile(rb"\r\n|\r|\n")
_BOM = b"\xef\xbb\xbf"
_UNESCAPED_PIPE_END = re.compile(rb"(?<!\\)\|$")  # R45: a pipe after "\" is escaped


def marker(ident: str, role: str = "") -> bytes:
    """The marker of an ID: "⟬TYP-3⟭", "⟬TYP-3 begin⟭" or "⟬TYP-3 end⟭", in UTF-8.

    Spec: R3, R25
    """
    return f"⟬{ident}{' ' + role if role else ''}⟭".encode()


def number_first_run(root: TreeNode, prefix: str) -> None:
    """Give IDs as on a first run: the file `prefix`, its nodes prefix-1, ... in pre-order.

    Spec: R9
    """
    root.id = prefix
    for n, node in enumerate(walk(root)):
        if n:
            node.id = f"{prefix}-{n}"


def annotate_text(
    source: bytes, prefix: str, file_marker: bool = True
) -> tuple[bytes, list[Insertion]]:
    """Build the tree of `source`, number it as a first run and annotate it, as the examples are.

    Spec: R28
    """
    root = build_tree(source)
    number_first_run(root, prefix)
    return annotate(source, root, file_marker=file_marker)


def strip(annotated: bytes, insertions: list[Insertion]) -> bytes:
    """Remove `insertions` from `annotated`: the spec file again.

    Spec: R23
    """
    out: list[bytes] = []
    pos = 0  # in annotated
    shift = 0  # bytes inserted before the current point
    for ins in sorted(insertions, key=lambda i: i.offset):
        at = ins.offset + shift
        if annotated[at : at + len(ins.text)] != ins.text:
            raise ValueError(f"insertion at {ins.offset} not found in the annotated text")
        out.append(annotated[pos:at])
        pos = at + len(ins.text)
        shift += len(ins.text)
    out.append(annotated[pos:])
    return b"".join(out)


def annotate(
    source: bytes, root: TreeNode, file_marker: bool = True
) -> tuple[bytes, list[Insertion]]:
    """Return the annotated `source` and its insertions; every node needs an `id`.

    The whole annotated file is checked against the source's blocks
    (structure.py). When a placement still changes them (two placements
    probed apart can clash), the nodes that change them are found, one
    top-level block at a time and node by node in the blocks that need it,
    and framed at the bounds of their top-level block.

    Spec: R49, R50 (E66)
    """
    structure: list[Structure | None] = []
    out, insertions = _annotate(source, root, file_marker, structure)
    if not structure:
        structure.append(block_structure(source))
    target = structure[0]
    if block_structure(out) == target:
        return out, insertions
    units: dict[int, list[TreeNode]] = {}
    for _, node, top in _nodes(root):
        if node.kind is not Kind.FILE:
            units.setdefault(id(top), []).append(node)
    placed: set[int] = set()
    hoisted: set[int] = set()

    def sound() -> bool:
        trial = _annotate(source, root, file_marker, structure, placed, hoisted)[0]
        return block_structure(trial) == target

    for nodes in units.values():
        placed |= {id(n) for n in nodes}
        if sound():
            continue
        placed -= {id(n) for n in nodes}
        for node in nodes:
            placed.add(id(node))
            if not sound():
                hoisted.add(id(node))
    return _annotate(source, root, file_marker, structure, None, hoisted)


def _annotate(
    source: bytes,
    root: TreeNode,
    file_marker: bool,
    structure: list[Structure | None],
    placed: set[int] | None = None,
    hoisted: set[int] = frozenset(),  # type: ignore[assignment]
) -> tuple[bytes, list[Insertion]]:
    """annotate() of the nodes in `placed` (all when None), those in `hoisted` framed at their top block."""
    writer = _Writer(source, structure)
    if file_marker:  # R29: after a UTF-8 BOM, which must stay first
        writer.line(writer.bom, (0, 0), root.margin, marker(_ident(root)))
    columns = 0
    for depth, node, top in _nodes(root):
        if node.kind is Kind.FILE:
            continue
        if top is node:
            writer.top_depth = depth
        writer.top = top
        if node.kind is Kind.TABLE:
            columns = sum(1 for c in node.children if c.kind is Kind.TABLE_CELL)
        if placed is not None and id(node) not in placed:
            continue
        if id(node) in hoisted:  # R50: its placement clashes in the whole file
            writer.hoist(node, depth, _ident(node))
            continue
        if node.lead:  # R46: a row's inserted "|"
            writer.lead(node.start, node.lead)
        if node.anchor < 0:
            writer.frame(node, depth)
        elif node.kind is Kind.TABLE_ROW:
            writer.inline(node.anchor, depth, _row_marker(source, node, columns))
        elif node.kind is Kind.ITEM and writer.moved_away(node):
            writer.hoist(node, depth, _ident(node))  # R37: its line's move would change it
        elif not (node.kind is Kind.ITEM and writer.item_head(node, depth)):
            # R39: an empty item's blank line stays inside the item's quotes, even when
            # the item took the place of its quote: its margin is then outside it (E43)
            after = writer.eol + blank_line(node.inner) if node.brk else b""
            writer.inline(node.anchor, depth, node.pad + marker(_ident(node)) + after)
    insertions = writer.insertions()
    out: list[bytes] = []
    pos = 0
    for ins in insertions:
        out.append(source[pos : ins.offset])
        out.append(ins.text)
        pos = ins.offset
    out.append(source[pos:])
    return b"".join(out), insertions


def _ident(node: TreeNode) -> str:
    """The node's ID; annotate() needs every node numbered."""
    if node.id is None:
        raise ValueError(f"{node.kind.value} at {node.start} has no ID")
    return node.id


def _nodes(
    root: TreeNode, depth: int = 0, top: TreeNode | None = None
) -> Iterator[tuple[int, TreeNode, TreeNode]]:
    """(depth, node, top) of `root` and its descendants, in pre-order.

    `top` is the top-level block that holds the node (a child of the file
    or of a section), the node itself at that level.

    Spec: R49
    """
    if top is None and root.kind not in (Kind.FILE, Kind.SECTION):
        top = root
    yield depth, root, top if top is not None else root
    for child in root.children:
        yield from _nodes(child, depth + 1, top)


def _row_marker(source: bytes, row: TreeNode, columns: int) -> bytes:
    """The row's ID as an extra cell after its closing pipe.

    A short row first gets its missing cells as empty ones (" |"), so that
    the ID lands past the last column and is not displayed.

    Spec: R45 (E10, E54, E55)
    """
    text = source[row.start : row.anchor]
    closed = bool(_UNESCAPED_PIPE_END.search(text))
    missing = max(columns - len(row.children), 0)
    head = (b"" if closed else b" |") + b" |" * missing
    tail = b" |" if closed else b""
    return head + b" " + marker(_ident(row)) + tail


_blank = blank_line


def _common(a: bytes, b: bytes) -> bytes:
    """The margin of a blank line between lines of margins `a` and `b`: the one with fewer quotes.

    Margins differ by their indentation, and by the blanks around their
    ">" when one keeps the columns of a source line: " > " and "> "
    are the same quote.

    Spec: R30, R37
    """
    if a.count(b">") != b.count(b">"):
        return a if a.count(b">") < b.count(b">") else b
    n = 0
    while n < len(a) and n < len(b) and a[n] == b[n]:
        n += 1
    return a[:n] if a[:n].count(b">") == a.count(b">") else a


@dataclass
class _Group:
    """What is inserted at one offset of the source."""

    inline: list[tuple[int, bytes]] = field(default_factory=list)  # (-depth, text)
    lines: list[tuple[tuple[int, float, int], bytes, bytes]] = field(default_factory=list)  # (order, margin, text)
    tail: bytes | None = None  # mid-line group: margin of the rest of the line
    lead: bytes = b""  # R46: written last, right before the source byte: a row's "|"


class _Writer:
    """Collects markers per offset and renders them with their blank lines."""

    def __init__(self, source: bytes, structure: list[Structure | None] | None = None) -> None:
        self.source = source
        self.eol = line_ending(source)
        self.bom = len(_BOM) if source.startswith(_BOM) else 0  # where line 1 starts
        self.groups: dict[int, _Group] = {}
        self.seq = 0
        self.no_move: set[int] = set()  # R36: offsets where the rest of the line must stay
        self.top: TreeNode | None = None  # R49: the top-level block of the node being placed
        self.top_depth = 0  # its depth
        self.hoisted = 0  # R49: frames hoisted so far
        self._structure = structure if structure is not None else []  # the source's, once computed

    def _group(self, offset: int) -> _Group:
        """The group of insertions at `offset`, created if needed."""
        return self.groups.setdefault(offset, _Group())

    def _line_start(self, offset: int) -> int:
        """Offset of the first byte of the line holding `offset` (after a BOM)."""
        start = max(self.source.rfind(b"\n", 0, offset), self.source.rfind(b"\r", 0, offset)) + 1
        return start or self.bom

    def _next_line(self, offset: int) -> int:
        """Offset of the line after the one holding `offset`; len(source) at the end."""
        m = _EOL.search(self.source, offset)
        return m.end() if m else len(self.source)

    def _line_end(self, offset: int) -> int:
        """Offset of the line ending of the line holding `offset`; len(source) at the end."""
        m = _EOL.search(self.source, offset)
        return m.start() if m else len(self.source)

    def _eol_at(self, offset: int) -> bytes:
        """The line ending of lines inserted at `offset`: "\r" right after a lone "\r".

        Spec: R3, R52
        """
        if self.source[offset - 1 : offset] == b"\r" and self.source[offset : offset + 1] != b"\n":
            return b"\r"
        return self.eol

    def inline(self, offset: int, depth: int, text: bytes) -> None:
        """`text` inserted at `offset`, at the end of a node's text.

        At one offset the deepest node's ID comes first: a cell's ID
        before its row's, which closes the row; on a marker line that
        cannot be split, the deeper IDs first.

        Spec: R36 (E10)
        """
        self._group(offset).inline.append((-depth, text))

    def lead(self, offset: int, text: bytes) -> None:
        """`text` written at `offset` after everything else inserted there.

        Spec: R46
        """
        self._group(offset).lead += text

    def line(self, offset: int, order: tuple[int, float], margin: bytes, text: bytes) -> None:
        """A marker line at `offset`; `order` sorts the lines of one place.

        Spec: R30
        """
        self.seq += 1
        self._group(offset).lines.append(((order[0], order[1], self.seq), margin, text))

    def frame(self, node: TreeNode, depth: int) -> None:
        """Begin and end markers around `node`.

        Spec: R24
        """
        ident = _ident(node)
        if node.begin == HOIST:  # R40, R43, R44, R49: no place of its own keeps the file's blocks
            self.hoist(node, depth, ident)
            return
        line_start = self._line_start(node.start if node.begin < 0 else node.begin)
        if node.begin < 0 and self.source[line_start : node.start].strip(b" \t>"):
            begin = node.start  # R35: after an item marker on the same line
            if begin in self.no_move:  # R36: the line cannot be split there: an ID at its end
                self._line_end_id(node, begin, depth, marker(ident))
                return
            group = self._group(begin)
            if group.tail is None:
                # R37: the rest of the line keeps its column, and its tabs their width
                group.tail = self._keep_columns(begin)
        else:
            begin = line_start
        self.line(begin, (1, depth), node.margin, marker(ident, "begin"))
        self.line(self._next_line(node.end), (0, -depth), node.margin, marker(ident, "end"))

    def item_head(self, node: TreeNode, depth: int) -> bool:
        """An item whose first node starts on its marker line: ID right there.

        The rest of the line moves to a new line, at the column it had,
        counted from its quote's content, or else at the column it
        had on the line. When that would change how the file parses, the
        ID goes at the end of the line instead, and the rest stays.
        Returns False when the item's ID is an ordinary inline one.

        Spec: R35, R36, R37
        """
        rest_end = self._line_end(node.anchor)
        if not self.source[node.anchor : rest_end].strip(b" \t"):
            return False
        # R37: the rest of the line keeps its column, so that its tabs keep their
        # width: written under the line's own prefixes, not the margin's "> "
        at = min(node.content, node.anchor) if node.content >= 0 else node.anchor
        ident = marker(_ident(node))
        for content in dict.fromkeys((self._keep_columns(at), self._keep_columns(at, absolute=True))):
            if self._preserves(node.anchor, self._moved(node.anchor, content, ident)):
                group = self._group(node.anchor)
                group.tail = content
                self.line(node.anchor, (1, depth), content, ident)
                return True
        # R36: at the end of the line, after the IDs of the deeper nodes there
        self.no_move.add(node.anchor)
        self._line_end_id(node, node.anchor, depth, ident)
        return True

    def _line_end_id(self, node: TreeNode, offset: int, depth: int, ident: bytes) -> None:
        """The ID of a node on a line that cannot be split: at the line's end, or hoisted.

        At the end of the line it can land in an indented code block, a
        code span or a link that runs on, or turn a definition into a
        paragraph: that is probed on the whole file. When it does, the
        node is framed at the start and end of its top-level block.

        Spec: R36, R49 (E65)
        """
        line_start = self._line_start(offset)
        end = line_start + len(self.source[line_start : self._line_end(offset)].rstrip(b" \t"))
        if self._preserves(end, b" " + ident):
            self.inline(end, depth, b" " + ident)
            return
        self.hoist(node, depth, ident.decode()[1:-1])

    def hoist(self, node: TreeNode, depth: int, name: str) -> None:
        """Frame `node` at the start and end of its top-level block.

        Spec: R49
        """
        top = self.top if self.top is not None else node
        start = top.begin if top.begin >= 0 else top.start
        # R49: right inside the top block's own markers, before (after) those of its
        # descendants, whose margins can hold a ">": deeper nodes nest inside, and
        # of two at one depth the later nests in the earlier (E48, E64)
        self.hoisted += 1
        level = self.top_depth + 0.5 + depth / 1000 + self.hoisted / 10**7
        self.line(self._line_start(start), (1, level), top.margin, marker(name, "begin"))
        self.line(self._next_line(top.end), (0, -level), top.margin, marker(name, "end"))

    def _keep_columns(self, offset: int, absolute: bool = False) -> bytes:
        """The prefix that puts a moved rest of line at the column of `offset`.

        The line's bytes before `offset` with every ">" kept and everything
        else made spaces, a tab as many as the columns it took: the quotes
        stay, list markers become the indentation of their items' content,
        and the rest of the line starts at its column, counted from the
        content of its quote, as cmark-gfm counts an item's content. A ">"
        followed by a byte that is not blank (">-") had no optional space,
        while the space written in that byte's place would be one: one
        more space is written after that ">". The rest of the line then
        starts one column later on the line, and a tab in it can take one
        column less; `absolute` keeps the line's columns instead, which a
        tab can need.

        Spec: R37
        """
        head = self.source[self._line_start(offset) : offset]
        moved = self._moved_before(offset)
        if moved is not None:  # its line already starts at an earlier move: that line's columns
            head = self.groups[moved].tail + self.source[moved:offset]
        out = bytearray()
        for i, byte in enumerate(head):
            if byte == 0x09:
                out += b" " * (4 - vcol(head, i) % 4)
            elif byte == 0x3E:
                out.append(0x3E)
                if not absolute and i + 1 < len(head) and head[i + 1] not in (0x20, 0x09):
                    out.append(0x20)  # R37: the optional space this ">" did not have, GFM §5.1
            else:
                out.append(0x20)
        return bytes(out)

    def _moved(self, offset: int, content: bytes, text: bytes) -> bytes:
        """What _render() writes at `offset` for one marker that moves the rest of the line.

        Spec: R35, R37
        """
        space = b"" if self.source[offset - 1 : offset] in (b" ", b"\t") else b" "
        return space + text + self.eol + _blank(content) + self.eol + content

    def moved_away(self, node: TreeNode) -> bool:
        """True if an item's ID at the end of its text, on a line whose rest moves, changes the file.

        The item was probed on the source line ("- - [x]"); once the outer
        item's rest moves to a line of its own, "- [x] ⟬ID⟭" can become a
        task item. Such an item is then framed at its top-level block.

        Spec: R37, R49
        """
        if self.source[node.anchor : self._line_end(node.anchor)].strip(b" \t"):
            return False  # R37: an item_head: probed with the moves
        if self._moved_before(node.anchor) is None:
            return False
        return not self._preserves(node.anchor, node.pad + marker(_ident(node)))

    def _moved_before(self, offset: int) -> int | None:
        """The last offset before `offset`, on its line, where the rest of the line moves.

        Spec: R37
        """
        start = self._line_start(offset)
        found = [o for o, g in self.groups.items() if start < o < offset and g.tail is not None]
        return max(found) if found else None

    def _preserves(self, offset: int, text: bytes) -> bool:
        """True if `text` inserted at `offset` leaves the file's blocks as they are.

        The moves of the rest of the line decided before on that line are
        inserted too: two moves on one line are probed together.

        Spec: R37
        """
        if not self._structure:
            self._structure.append(block_structure(self.source))
        start, end = self._line_start(offset), self._line_end(offset)
        inserts = [(o, self._render(o, g)) for o, g in self.groups.items() if start < o <= end and g.tail is not None and o != offset]
        parts: list[bytes] = []
        pos = 0
        for at, data in sorted([*inserts, (offset, text)], key=lambda i: i[0]):
            parts += [self.source[pos:at], data]
            pos = at
        parts.append(self.source[pos:])
        return block_structure(b"".join(parts)) == self._structure[0]

    def insertions(self) -> list[Insertion]:
        """One Insertion per offset, in source order: what strip() removes.

        Spec: R23
        """
        return [
            Insertion(offset, self._render(offset, self.groups[offset]))
            for offset in sorted(self.groups)
            if self.groups[offset].inline or self.groups[offset].lines or self.groups[offset].lead
        ]

    # --- rendering ------------------------------------------------------

    def _is_blank_line_before(self, offset: int, margin: bytes) -> bool:
        """True at the start of the file or after a blank line, reused as a marker's.

        A bare ">" counts as blank inside a block quote (`margin` holds
        a ">"), not elsewhere, nor a ">" past the quotes of `margin`:
        "    >" is a lazy line or code, "> >" a nested quote (is_blank_under).

        Spec: R30, R47
        """
        if offset <= self.bom:
            return True
        end = offset - 1
        if self.source[end : end + 1] == b"\n" and self.source[end - 1 : end] == b"\r":
            end -= 1
        start = self._line_start(end)
        return is_blank_under(self.source[start:end], margin)

    def _is_blank_line_at(self, offset: int, margin: bytes) -> bool:
        """True at the end of the file or when the line at `offset` is blank (see above)."""
        if offset >= len(self.source):
            return True
        end = _EOL.search(self.source, offset)
        stop = end.start() if end else len(self.source)
        return is_blank_under(self.source[offset:stop], margin)

    def _render(self, offset: int, group: _Group) -> bytes:
        """The bytes inserted at `offset`: inline IDs, marker lines, then a lead.

        Spec: R30
        """
        return self._render_lines(offset, group) + group.lead

    def _render_lines(self, offset: int, group: _Group) -> bytes:
        """Inline IDs, then marker lines with their blank lines.

        Spec: R30
        """
        out = b"".join(text for _, text in sorted(group.inline, key=lambda x: x[0]))
        lines = sorted(group.lines, key=lambda x: x[0])
        if not lines:
            return out
        eol = self._eol_at(offset)
        at_line_start = offset == self.bom or self.source[offset - 1 : offset] in (b"\n", b"\r")
        if not at_line_start and offset < len(self.source):  # R37: mid-line: the rest moves
            tail = group.tail if group.tail is not None else lines[0][1]
            prev = lines[0][1]
            if not (out or self.source[offset - 1 : offset]).endswith((b" ", b"\t")):
                out += b" "
            out += lines[0][2]
            for _, margin, text in lines[1:]:
                out += eol + _blank(_common(prev, margin)) + eol + margin + text
                prev = margin
            return out + eol + _blank(_common(prev, tail)) + eol + tail
        if not at_line_start:  # R30: end of a file without a final line ending: no blank after
            out += eol
            blank = False
        else:
            blank = self._is_blank_line_before(offset, lines[0][1])
        prev: bytes | None = None
        for _, margin, text in lines:
            if not blank:
                out += _blank(margin if prev is None else _common(prev, margin)) + eol
            out += margin + text + eol
            blank = False
            prev = margin
        if not self._is_blank_line_at(offset, prev or b""):
            out += _blank(prev or b"") + eol
        return out
