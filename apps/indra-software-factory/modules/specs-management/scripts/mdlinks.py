"""Find the inline links of a Markdown file, with CommonMark 0.31.2 semantics.

Spec: specs/module.md, section "Move specs between layers 0 and 1", term Link:
an inline link of CommonMark 0.31.2 section 6.3. Not a link: an image (its
description included), text in a code span, in a fenced or indented code
block, in an HTML block or in an HTML comment. Reference-style links are not
links; their definitions are reported apart by find_refdefs. The filtering by
destination stays with the caller.

    find_links(text)   -> [{open, close, dest_start, dest_end, end, line, angle, title}]
    find_refdefs(text) -> [{line, dest_start, dest_end, angle}]

`text` is the whole file (decoded with errors="surrogateescape"); every
offset is an index into it, so that a caller can rewrite links byte-exactly.

The block parser follows the algorithm of commonmark.js (the reference
implementation): each line goes first through the open containers
(blockquote, list item, ...), then through the block starts, then is added to
a leaf. Paragraph and heading text is kept with, for each character, its
index in `text`; leading whitespace of each line is dropped (CommonMark drops
it too) so that every kept character is a real character of the file. The
inline parser then runs over the whole paragraph, and only cares about what
can hide or make a link: backslash escapes, code spans, autolinks, raw HTML
and the brackets of links and images.
"""

import bisect
import re

# ---------------------------------------------------------------- shared grammar

ESCAPABLE = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
EOL = re.compile(r"\r\n|\n|\r")

_TAGNAME = r"[A-Za-z][A-Za-z0-9-]*"
_ATTR = (r"(?:[ \t\n]+[a-zA-Z_:][a-zA-Z0-9:._-]*"
         r"(?:[ \t\n]*=[ \t\n]*(?:[^\"'=<>`\x00-\x20]+|'[^']*'|\"[^\"]*\"))?)")
_OPENTAG = r"<" + _TAGNAME + _ATTR + r"*[ \t\n]*/?>"
_CLOSETAG = r"</" + _TAGNAME + r"[ \t\n]*>"
# Inline raw HTML (section 6.6): tags, comments, processing instructions,
# declarations and CDATA. `<!-->` and `<!--->` are complete comments.
HTML_TAG = re.compile(
    "(?:" + _OPENTAG + "|" + _CLOSETAG + r"|<!-->|<!--->|<!--.*?-->|<\?.*?\?>"
    r"|<![A-Za-z][^>]*>|<!\[CDATA\[.*?\]\]>)", re.S)
AUTOLINK = re.compile(
    r"<[A-Za-z][A-Za-z0-9.+-]{1,31}:[^<>\x00-\x20]*>"
    r"|<[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*>")
SPNL = re.compile(r"[ \t]*(?:\n[ \t]*)?")          # spaces, up to one line ending
ANGLE_DEST = re.compile(r"<(?:[^<>\n\\]|\\.)*>")
TITLE = re.compile(r'"(?:\\.|[^\\"])*"' r"|'(?:\\.|[^\\'])*'" r"|\((?:\\.|[^\\()])*\)", re.S)
LABEL = re.compile(r"\[(?:[^\\\[\]]|\\.){0,1000}\]", re.S)
LINE_END = re.compile(r"[ \t]*(?:\n|\Z)")
SPECIAL = re.compile(r"[\\`<!\[\]]")
TICKS = re.compile(r"`+")


def normalize_label(label):
    """Matching form of a link label (section 4.7): case-folded, inner whitespace collapsed."""
    return re.sub(r"[ \t\r\n]+", " ", label.strip(" \t\r\n")).lower().upper()


def parse_dest(s, p):
    """(start, end, angle, after) of the link destination at s[p], or None (section 6.3)."""
    if p < len(s) and s[p] == "<":
        m = ANGLE_DEST.match(s, p)
        return (p, m.end(), True, m.end()) if m else None
    q, depth = p, 0
    while q < len(s):
        c = s[q]
        if c == "\\" and q + 1 < len(s) and s[q + 1] in ESCAPABLE:
            q += 2
        elif c == "(":
            depth += 1
            q += 1
        elif c == ")":
            if depth < 1:
                break
            depth -= 1
            q += 1
        elif ord(c) <= 0x20 or ord(c) == 0x7F:
            break
        else:
            q += 1
    if (q == p and (q >= len(s) or s[q] != ")")) or depth:
        return None
    return p, q, False, q


# ---------------------------------------------------------------- inlines

def parse_inlines(s, refmap):
    """Inline links and images of one paragraph or heading text.

    Returns (links, images): links as tuples (open, close, how, end), where
    how is (dest_start, dest_end, angle, title) for an inline link and the
    normalized label for a reference link; images as (start, end). All are
    indexes into s.
    Mirrors the bracket stack of commonmark.js: a `]` looks at the nearest
    open bracket; a matched link (inline or reference) deactivates every
    earlier `[`, because a link cannot contain a link.
    """
    n = len(s)
    brackets = []           # [index of "[", image, active, a bracket opened after it]
    links, images = [], []
    i = 0
    while True:
        m = SPECIAL.search(s, i)
        if not m:
            break
        i = m.start()
        c = s[i]
        if c == "\\":
            i += 2 if i + 1 < n and (s[i + 1] in ESCAPABLE or s[i + 1] == "\n") else 1
        elif c == "`":
            # Code span: the next backtick run of the same length closes it;
            # without one, the opening run is literal text.
            j = i
            while j < n and s[j] == "`":
                j += 1
            i = j
            for t in TICKS.finditer(s, j):
                if t.end() - t.start() == j - m.start():
                    i = t.end()
                    break
        elif c == "<":
            t = AUTOLINK.match(s, i) or HTML_TAG.match(s, i)
            i = t.end() if t else i + 1
        elif c == "!":
            if i + 1 < n and s[i + 1] == "[":
                if brackets:
                    brackets[-1][3] = True
                brackets.append([i + 1, True, True, False])
                i += 2
            else:
                i += 1
        elif c == "[":
            if brackets:
                brackets[-1][3] = True
            brackets.append([i, False, True, False])
            i += 1
        else:
            i = close_bracket(s, i, brackets, refmap, links, images)
    return links, images


def close_bracket(s, i, brackets, refmap, links, images):
    """Handle the `]` at s[i]; return the index to resume from."""
    if not brackets:
        return i + 1
    opener = brackets.pop()
    if not opener[2]:
        return i + 1
    end, inline = None, None
    p = i + 1
    if p < len(s) and s[p] == "(":
        # Inline link: ( spnl destination [spnl title] spnl )
        q = SPNL.match(s, p + 1).end()
        d = parse_dest(s, q)
        if d:
            ds, de, angle, q = d
            q2 = SPNL.match(s, q).end()
            title = False
            if q2 > q:
                t = TITLE.match(s, q2)
                if t:
                    title, q2 = True, t.end()
            q2 = SPNL.match(s, q2).end()
            if q2 < len(s) and s[q2] == ")":
                end, inline = q2 + 1, (ds, de, angle, title)
    if end is None:
        # Reference link: full [text][label], collapsed [text][] or shortcut [text].
        lab = LABEL.match(s, p)
        label = None
        n = len(lab.group()) if lab and len(lab.group()) <= 1001 else 0
        if n > 2:
            label = lab.group()[1:-1]
        elif not opener[3]:
            label = s[opener[0] + 1:i]
        if label is not None and len(label) <= 999 and normalize_label(label) in refmap:
            end, inline = p + n, normalize_label(label)
    if end is None:
        return i + 1
    if opener[1]:
        images.append((opener[0] - 1, end))
    else:
        links.append((opener[0], i, inline, end))
        for b in brackets:
            if not b[1]:
                b[2] = False
    return end


# ---------------------------------------------------------------- blocks

HTML_OPEN = [None,
             re.compile(r"<(?:script|pre|textarea|style)(?:[ \t>]|\Z)", re.I),
             re.compile(r"<!--"),
             re.compile(r"<\?"),
             re.compile(r"<![A-Za-z]"),
             re.compile(r"<!\[CDATA\["),
             re.compile(r"</?(?:address|article|aside|base|basefont|blockquote|body|caption|center|col"
                        r"|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer"
                        r"|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main"
                        r"|menu|menuitem|nav|noframes|ol|optgroup|option|p|param|search|section"
                        r"|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul)(?:[ \t]|/?>|\Z)", re.I),
             re.compile("(?:" + _OPENTAG + "|" + _CLOSETAG + r")[ \t]*\Z")]
HTML_CLOSE = [None,
              re.compile(r"</(?:script|pre|textarea|style)>", re.I),
              re.compile(r"-->"),
              re.compile(r"\?>"),
              re.compile(r">"),
              re.compile(r"\]\]>")]
MAYBE_SPECIAL = re.compile(r"[#`~*+_=<>0-9-]")
ATX = re.compile(r"#{1,6}(?:[ \t]+|\Z)")
FENCE = re.compile(r"`{3,}(?!.*`)|~{3,}")
CLOSE_FENCE = re.compile(r"(?:`{3,}|~{3,})(?=[ \t]*\Z)")
SETEXT = re.compile(r"(?:=+|-+)[ \t]*\Z")
HR = re.compile(r"(?:(?:\*[ \t]*){3,}|(?:_[ \t]*){3,}|(?:-[ \t]*){3,})\Z")
BULLET = re.compile(r"[*+-]")
ORDERED = re.compile(r"(\d{1,9})([.)])")


class Block:
    def __init__(self, kind, parent):
        self.kind = kind            # document, blockquote, list, item, paragraph, heading, code, html, hr
        self.parent = parent
        self.children = []
        self.open = True
        self.content = ""           # paragraph and heading: the inline text...
        self.map = []               # ...and the index in the file of each of its characters


def _sp(c):
    return c == " " or c == "\t"


class Parser:
    """Block structure of a document (CommonMark section 4 and 5), as commonmark.js parses it."""

    def __init__(self, text):
        self.text = text
        self.doc = Block("document", None)
        self.tip = self.doc
        self.refmap = {}            # normalized label -> raw destination of its first definition
        self.refdefs = []
        self.leaves = []            # paragraphs and headings, whose text is inline content
        start = 0
        for m in EOL.finditer(text):
            self.line_in(start, text[start:m.start()], m.start())
            start = m.end()
        if start < len(text):
            self.line_in(start, text[start:], len(text))
        while self.tip:
            self.finalize(self.tip)

    # -- cursor over the current line (columns count tabs to the next multiple of 4)

    def peek(self, i):
        return self.ln[i] if i < len(self.ln) else ""

    def find_next_nonspace(self):
        i, cols = self.offset, self.column
        while i < len(self.ln):
            c = self.ln[i]
            if c == " ":
                cols += 1
            elif c == "\t":
                cols += 4 - cols % 4
            else:
                break
            i += 1
        self.blank = i >= len(self.ln)
        self.nn, self.nn_col = i, cols
        self.indent = cols - self.column
        self.indented = self.indent >= 4

    def advance(self, count, columns):
        while count > 0 and self.offset < len(self.ln):
            if self.ln[self.offset] == "\t":
                to_tab = 4 - self.column % 4
                if columns:
                    # A tab may be consumed in part (e.g. one column of it after `>`).
                    step = min(to_tab, count)
                    self.column += step
                    if to_tab <= count:
                        self.offset += 1
                    count -= step
                else:
                    self.column += to_tab
                    self.offset += 1
                    count -= 1
            else:
                self.offset += 1
                self.column += 1
                count -= 1

    def advance_next_nonspace(self):
        self.offset, self.column = self.nn, self.nn_col

    # -- tree

    def add_child(self, kind):
        while not (self.tip.kind in ("document", "blockquote", "item") and kind != "item"
                   or self.tip.kind == "list" and kind == "item"):
            self.finalize(self.tip)
        b = Block(kind, self.tip)
        self.tip.children.append(b)
        self.tip = b
        if kind == "paragraph":
            self.leaves.append(b)
        return b

    def finalize(self, b):
        b.open = False
        if b.kind == "paragraph":
            self.take_refdefs(b)
        self.tip = b.parent

    def close_unmatched(self):
        if not self.all_closed:
            while self.oldtip is not self.last_matched:
                parent = self.oldtip.parent
                self.finalize(self.oldtip)
                self.oldtip = parent
            self.all_closed = True

    def add_line(self, b):
        if b.kind == "paragraph":
            b.content += self.ln[self.offset:] + "\n"
            b.map.extend(range(self.base + self.offset, self.base + len(self.ln)))
            b.map.append(self.eol)

    # -- one line

    def line_in(self, base, ln, eol):
        self.base, self.ln, self.eol = base, ln, eol
        self.offset = self.column = 0
        self.oldtip = self.tip
        container = self.doc
        # 1. The open containers that the line continues.
        while container.children and container.children[-1].open:
            container = container.children[-1]
            self.find_next_nonspace()
            r = self.cont(container)
            if r == 2:
                return
            if r == 1:
                container = container.parent
                break
        self.all_closed = container is self.oldtip
        self.last_matched = container
        # 2. New block starts.
        leaf = container.kind in ("code", "html")
        starts = (self.blockquote, self.atx, self.fence, self.html, self.setext, self.hr,
                  self.item, self.indented_code)
        while not leaf:
            self.find_next_nonspace()
            if not self.indented and not MAYBE_SPECIAL.match(self.ln, self.nn):
                self.advance_next_nonspace()
                break
            for start in starts:
                r = start(container)
                if r:
                    container = self.tip
                    leaf = r == 2
                    break
            else:
                self.advance_next_nonspace()
                break
        # 3. The rest of the line: lazy paragraph continuation, or a leaf's content.
        if not self.all_closed and not self.blank and self.tip.kind == "paragraph":
            self.add_line(self.tip)
            return
        self.close_unmatched()
        if container.kind in ("paragraph", "code", "html"):
            self.add_line(container)
            if container.kind == "html" and container.htype <= 5 \
                    and HTML_CLOSE[container.htype].search(self.ln, self.offset):
                self.finalize(container)
        elif self.offset < len(self.ln) and not self.blank:
            b = self.add_child("paragraph")
            self.advance_next_nonspace()
            self.add_line(b)

    def cont(self, b):
        """0: the line continues block b; 1: it does not; 2: it closed b (closing fence)."""
        k = b.kind
        if k == "blockquote":
            if not self.indented and self.peek(self.nn) == ">":
                self.advance_next_nonspace()
                self.advance(1, False)
                if _sp(self.peek(self.offset)):
                    self.advance(1, True)
                return 0
            return 1
        if k == "item":
            if self.blank:
                if not b.children:
                    return 1
                self.advance_next_nonspace()
            elif self.indent >= b.marker_offset + b.padding:
                self.advance(b.marker_offset + b.padding, True)
            else:
                return 1
            return 0
        if k == "code":
            if b.fenced:
                m = (self.indent <= 3 and self.peek(self.nn) == b.fchar
                     and CLOSE_FENCE.match(self.ln, self.nn))
                if m and len(m.group()) >= b.flen:
                    self.finalize(b)
                    return 2
                i = b.foff
                while i > 0 and _sp(self.peek(self.offset)):
                    self.advance(1, True)
                    i -= 1
            elif self.indent >= 4:
                self.advance(4, True)
            elif self.blank:
                self.advance_next_nonspace()
            else:
                return 1
            return 0
        if k == "html":
            return 1 if self.blank and b.htype >= 6 else 0
        if k == "paragraph":
            return 1 if self.blank else 0
        if k in ("heading", "hr"):
            return 1
        return 0                    # document, list

    # -- block starts: 0 no match, 1 a container, 2 a leaf

    def blockquote(self, container):
        if self.indented or self.peek(self.nn) != ">":
            return 0
        self.advance_next_nonspace()
        self.advance(1, False)
        if _sp(self.peek(self.offset)):
            self.advance(1, True)
        self.close_unmatched()
        self.add_child("blockquote")
        return 1

    def atx(self, container):
        m = not self.indented and ATX.match(self.ln, self.nn)
        if not m:
            return 0
        self.advance_next_nonspace()
        self.advance(len(m.group()), False)
        self.close_unmatched()
        h = self.add_child("heading")
        a, e = self.offset, len(self.ln)
        if re.fullmatch(r"[ \t]*#+[ \t]*", self.ln[a:]):
            e = a                    # only a closing sequence: empty heading
        else:
            t = re.search(r"[ \t]+#+[ \t]*\Z", self.ln[a:])
            if t:
                e = a + t.start()
        h.content = self.ln[a:e]
        h.map = list(range(self.base + a, self.base + e))
        self.leaves.append(h)
        self.offset = len(self.ln)
        return 2

    def fence(self, container):
        m = not self.indented and FENCE.match(self.ln, self.nn)
        if not m:
            return 0
        self.close_unmatched()
        b = self.add_child("code")
        b.fenced, b.fchar, b.flen, b.foff = True, m.group()[0], len(m.group()), self.indent
        self.advance_next_nonspace()
        self.advance(len(m.group()), False)
        return 2

    def html(self, container):
        if self.indented or self.peek(self.nn) != "<":
            return 0
        s = self.ln[self.nn:]
        lazy = not self.all_closed and not self.blank and self.tip.kind == "paragraph"
        for t in range(1, 8):
            # Type 7 cannot interrupt a paragraph, not even a lazy one.
            if HTML_OPEN[t].match(s) and (t < 7 or (container.kind != "paragraph" and not lazy)):
                self.close_unmatched()
                self.add_child("html").htype = t
                return 2
        return 0

    def setext(self, container):
        if self.indented or container.kind != "paragraph" or not SETEXT.match(self.ln, self.nn):
            return 0
        self.close_unmatched()
        self.take_refdefs(container)
        if not container.content:
            return 0
        container.kind = "heading"   # same text, now a heading; the next line closes it
        self.offset = len(self.ln)
        return 2

    def hr(self, container):
        if self.indented or not HR.match(self.ln, self.nn):
            return 0
        self.close_unmatched()
        self.add_child("hr")
        self.offset = len(self.ln)
        return 2

    def item(self, container):
        if self.indented and container.kind != "list":
            return 0
        data = self.list_marker(container)
        if not data:
            return 0
        self.close_unmatched()
        if self.tip.kind != "list" or self.tip.marker != data[0]:
            self.add_child("list").marker = data[0]
        it = self.add_child("item")
        it.marker, it.marker_offset, it.padding = data
        return 1

    def list_marker(self, container):
        """(marker kind, marker offset, padding) of a list item starting here, or None."""
        if self.indent >= 4:
            return None
        rest = self.ln[self.nn:]
        m = BULLET.match(rest)
        if m:
            kind = m.group()
        else:
            m = ORDERED.match(rest)
            # An ordered list interrupts a paragraph only when it starts at 1.
            if not m or (container.kind == "paragraph" and int(m.group(1)) != 1):
                return None
            kind = m.group(2)
        after = self.nn + len(m.group())
        if self.peek(after) not in ("", " ", "\t"):
            return None
        if container.kind == "paragraph" and not self.ln[after:].strip(" \t"):
            return None             # an empty item cannot interrupt a paragraph
        marker_offset = self.indent
        self.advance_next_nonspace()
        self.advance(len(m.group()), True)
        col0, off0 = self.column, self.offset
        while True:
            self.advance(1, True)
            if not (self.column - col0 < 5 and _sp(self.peek(self.offset))):
                break
        spaces = self.column - col0
        if spaces >= 5 or spaces < 1 or self.peek(self.offset) == "":
            # Indented code after the marker, or an empty item: one space of padding.
            padding = len(m.group()) + 1
            self.column, self.offset = col0, off0
            if _sp(self.peek(self.offset)):
                self.advance(1, True)
        else:
            padding = len(m.group()) + spaces
        return kind, marker_offset, padding

    def indented_code(self, container):
        if not self.indented or self.tip.kind == "paragraph" or self.blank:
            return 0
        self.advance(4, True)
        self.close_unmatched()
        self.add_child("code").fenced = False
        return 2

    # -- link reference definitions (section 4.7), at the start of a paragraph

    def take_refdefs(self, b):
        while b.content.startswith("["):
            n = self.refdef(b.content, b.map)
            if not n:
                break
            b.content, b.map = b.content[n:], b.map[n:]

    def refdef(self, s, smap):
        """Length of the definition at the start of s (0 if none); records it."""
        lab = LABEL.match(s)
        if not lab or len(lab.group()) > 1001 or not s.startswith(":", lab.end()):
            return 0
        norm = normalize_label(lab.group()[1:-1])
        if not norm:
            return 0
        p = SPNL.match(s, lab.end() + 1).end()
        d = parse_dest(s, p)
        if not d or d[0] == d[1]:
            return 0
        ds, de, angle, p = d
        before_title = p
        q = SPNL.match(s, p).end()
        t = TITLE.match(s, q) if q > p else None
        m = LINE_END.match(s, t.end()) if t else None
        if not m:
            m = LINE_END.match(s, before_title)   # no title, or text after it on its line
            if not m:
                return 0
        self.refmap.setdefault(norm, s[ds:de])
        self.refdefs.append(dict(open=smap[0], dest_start=smap[ds], dest_end=smap[ds] + de - ds,
                                 angle=angle))
        return m.end()


# ---------------------------------------------------------------- API

def _parse(text):
    p = Parser(text)
    starts = [0] + [m.end() for m in EOL.finditer(text)]
    return p, (lambda i: bisect.bisect_right(starts, i))


def _scan(text):
    """(open, how, end, refmap, line_of) of every link, inline or reference, outside images."""
    p, line_of = _parse(text)
    for b in p.leaves:
        s = b.content.rstrip(" \t\n")
        lo = len(s) - len(s.lstrip(" \t\n"))
        links, images = parse_inlines(s[lo:], p.refmap)
        for o, c, how, e in links:
            if any(a <= o < z for a, z in images):
                continue            # a link inside an image description is part of the image
            m = b.map
            if isinstance(how, tuple):
                ds, de, angle, title = how
                how = dict(close=m[lo + c], dest_start=m[lo + ds], dest_end=m[lo + ds] + de - ds,
                           angle=angle, title=title)
            yield m[lo + o], how, m[lo + e - 1] + 1, p.refmap, line_of


def find_links(text):
    """Every inline link of `text` (CommonMark 0.31.2, section 6.3), images excluded, by `open`."""
    found = [dict(open=o, close=how["close"], dest_start=how["dest_start"], dest_end=how["dest_end"],
                  end=e, line=line_of(o), angle=how["angle"], title=how["title"])
             for o, how, e, _, line_of in _scan(text) if isinstance(how, dict)]
    return sorted(found, key=lambda l: l["open"])


def find_refdefs(text):
    """Every link reference definition of `text` that CommonMark recognises, in file order."""
    p, line_of = _parse(text)
    return sorted((dict(line=line_of(d["open"]), dest_start=d["dest_start"], dest_end=d["dest_end"],
                        angle=d["angle"]) for d in p.refdefs), key=lambda d: d["dest_start"])
