"""Block structure of a GFM source, annotations ignored.

`block_structure(source)` parses `source` with cmark-gfm (cmark.render_xml)
and returns its blocks as nested tuples, so that two sources can be
compared block by block: verify.py compares the annotated file with the
foundation file, annotate.py checks the whole annotated file,
and tree.py and annotate.py probe whether one insertion would change how
a source parses.

Ignored: list tightness (the blank lines around frame markers make a
tight list loose), paragraphs that hold only markers (marker
lines), and inline markers in the text of paragraphs, headings and
cells, but not inside a code span, raw inline HTML or a link, where an
ID must never be. Begin and end markers inside a text block are kept, so a marker
that a paragraph absorbed (a missing blank line) shows. Code and
HTML blocks must be equal byte for byte, except, in a block that
is never closed (a fenced code block without its closing fence, an HTML
block of type 1-5 without its closing sequence), for the lines that only
hold an end marker, or nothing, at its end: such a block runs to the end
of its container, and its end marker, and those of the containers that
close with it, fall inside it.

cmark-gfm writes control characters (ESC, form feed, ...) into its XML
as they are, which XML 1.0 forbids; each one is replaced with its
Unicode control picture (U+2400 + byte) before the XML is read. Note: D30

Spec: R26, R30, R35, R36, R37, R39, R44, R48, R50, R64, U1, U2 (E13, E17, E61, E62)
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from norms_generator.cmark import parse, render_xml
from norms_generator.model import AstNode

MARKER_RE = re.compile(r"⟬([A-Z]+(?:-[0-9]+)?)( begin| end)?⟭")  # R29: every marker's form

Structure = tuple[object, ...]

_TEXT_BLOCKS = {"paragraph", "heading", "table_cell"}
_INLINE_WRAP = {"emph": ("*", "*"), "strong": ("**", "**"), "strikethrough": ("~~", "~~")}
_CONTROL = re.compile(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_TRAILING_END = re.compile(r"(?:\n[ \t]*(?:⟬[A-Z]+(?:-[0-9]+)? end⟭)?[ \t]*)+\n?\Z")


def _tag(elem: ET.Element) -> str:
    """An element's tag without the CommonMark namespace."""
    return elem.tag.rsplit("}", 1)[-1]


def _sealed(text: str) -> str:
    """`text` with its marker delimiters escaped: a marker there is never ignored.

    Spec: R64 (E17)
    """
    return text.replace("⟬", "\\u27ec").replace("⟭", "\\u27ed")


def _inline_text(elem: ET.Element, sealed: bool = False) -> str:
    """The inlines of a block flattened into a string that keeps their kinds.

    An ID is never written inside a code span, raw inline HTML or a link:
    their text is `sealed`, so that a marker inside them stays visible to
    the comparison, even with a space on each side.

    Spec: R64 (E17)
    """
    parts: list[str] = []
    for child in elem:
        tag = _tag(child)
        if tag == "text":
            parts.append(_sealed(child.text or "") if sealed else child.text or "")
        elif tag == "html_inline":
            parts.append(_sealed(child.text or ""))
        elif tag == "code":
            parts.append("`" + _sealed(child.text or "") + "`")
        elif tag == "softbreak":
            parts.append("\n")
        elif tag == "linebreak":
            parts.append(" <br> ")  # R64: blanks around it are normalized like any other
        elif tag in _INLINE_WRAP:
            left, right = _INLINE_WRAP[tag]
            parts.append(left + _inline_text(child, sealed) + right)
        elif tag in ("link", "image"):
            bang = "!" if tag == "image" else ""
            target = _sealed(child.get("destination", "") + " " + child.get("title", ""))
            parts.append(f"{bang}[{_inline_text(child, True)}]({target})")
        else:
            parts.append(f"<{tag}>{_inline_text(child, sealed)}</{tag}>")
    return "".join(parts)


def _clean_text(text: str) -> str:
    """Inline IDs removed, blanks normalized line by line; begin/end markers kept.

    The line breaks stay: an ID that took a line of its own in a
    paragraph or heading (an empty item's ID above a setext heading)
    leaves an empty line, which the foundation text never has.

    Spec: R39, R64 (E42)
    """
    inline = MARKER_RE.sub(lambda m: " " if not m.group(2) else m.group(0), text)
    return "\n".join(" ".join(line.split()) for line in inline.split("\n"))


def _literal(text: str) -> str:
    """A code or HTML literal without its trailing blank and end-marker lines.

    Spec: R48
    """
    return _TRAILING_END.sub("", "\n" + text)[1:] if text else text


def _structure(elem: ET.Element, open_blocks: list[bool]) -> Structure | None:
    """Block structure of an element; None for a paragraph of markers only.

    `open_blocks` holds, in document order, whether each code or HTML
    block left is open (never closed); one is taken per such block.

    Spec: R64
    """
    tag = _tag(elem)
    if tag in _TEXT_BLOCKS:
        raw = _inline_text(elem)
        if tag == "paragraph" and not MARKER_RE.sub("", raw).strip():
            return None  # R30: a marker line, or several
        return (tag, elem.get("level"), _clean_text(raw))
    if tag in ("code_block", "html_block"):
        is_open = open_blocks.pop(0) if open_blocks else False
        text = elem.text or ""  # R26, R48: byte for byte, an open one's tail tolerated
        return (tag, elem.get("info"), _literal(text) if is_open else text)
    attrs: tuple[object, ...] = ()
    if tag == "list":
        attrs = (elem.get("type"), elem.get("start"), elem.get("delim"))  # U2: no tightness
    elif tag == "tasklist":
        attrs = (elem.get("completed"),)
    children = tuple(s for s in (_structure(c, open_blocks) for c in elem) if s is not None)
    return (tag, attrs, children)


def _xml(source: bytes) -> bytes:
    """cmark-gfm's XML of `source`, control characters made printable.

    Note: D30
    """
    return _CONTROL.sub(lambda m: chr(0x2400 + m.group(0)[0]).encode(), render_xml(source))


def _open_blocks(node: AstNode) -> list[bool]:
    """Whether each code and HTML block under `node` is open, in document order.

    Spec: R48
    """
    out: list[bool] = []
    if node.type in ("code_block", "html_block"):
        out.append(node.open)
    for child in node.children:
        out += _open_blocks(child)
    return out


def block_structure(source: bytes) -> Structure | None:
    """Parse `source` and return its block structure, annotations ignored.

    Spec: R64
    """
    return _structure(ET.fromstring(_xml(source)), _open_blocks(parse(source)))
