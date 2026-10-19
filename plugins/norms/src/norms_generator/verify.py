"""Checks of one annotated file against foundation and the JSONL.

`check_file()` returns the problems found in one file, as messages; an
empty list means the file is sound. It checks, in order:

    sha256      the foundation bytes are the ones the JSONL recorded
    strip       removing the recorded insertions from the annotated file
                gives back the foundation file byte for byte
    insertions  the inserted bytes are only markers, spaces, line
                endings, ">" and "|", never a tab
    utf-8       the annotated file decodes as UTF-8
    markers     every marker matches the marker pattern; the file marker
                comes first, on a line of its own; each ID appears once
                inline, or once as begin and once as end, begin first;
                frames nest
    ids         the IDs in the file are exactly the active JSONL nodes
                of that file, the file's prefix included
    tree        the norms tree rebuilt from foundation has the stored
                nodes, in pre-order: same kind, span, hashes and parent
    places      annotating foundation again with the stored IDs gives
                the annotated file and the recorded insertions byte for
                byte: each ID sits at its own node
    structure   cmark-gfm parses the annotated file to the same blocks
                as the foundation file, markers aside; an annotated file
                nested deeper than the parser follows does not

Structure is compared with structure.block_structure(), on cmark-gfm's
XML rendering. Ignored: list tightness (frame markers inside a list make
it loose), paragraphs that hold only markers (marker lines), inline
markers in the text of paragraphs, headings and cells, and the end
markers and blank lines at the end of an unclosed fenced code block or
HTML block: its own and those of the containers that close with it.
Code and HTML blocks must otherwise be equal byte for byte.

Spec: R3, R23, R24, R25, R26, R29, R30, R38, R48, R52, R53, R61, R64, U1, U2 (E13, E61, E62)
"""

from __future__ import annotations

import hashlib
import re

from norms_generator.annotate import annotate, strip
from norms_generator.model import Insertion
from norms_generator.store import StoredFile, StoredNode
from norms_generator.structure import MARKER_RE, Structure, block_structure
from norms_generator.tree import build_tree, walk

__all__ = ["MARKER_RE", "Structure", "block_structure", "check_file"]

ANY_MARKER_RE = re.compile(r"⟬[^⟬⟭]*⟭")  # anything between the delimiters
_BOM = "﻿"


def check_file(
    path: str,
    source: bytes,
    annotated: bytes,
    stored: StoredFile,
    nodes: list[StoredNode],
) -> list[str]:
    """Problems of one file; `nodes` are its active JSONL nodes, in stored order.

    Spec: R3, R23, R61, R64
    """
    problems: list[str] = []
    digest = hashlib.sha256(source).hexdigest()
    if digest != stored.sha256:  # R61: foundation is the version the JSONL recorded
        problems.append(f"{path}: sha256 {digest} differs from the JSONL's {stored.sha256}")
    try:
        if strip(annotated, stored.insertions) != source:  # R23: stripping gives back foundation
            problems.append(f"{path}: stripping the insertions does not give back foundation")
    except ValueError as exc:
        problems.append(f"{path}: {exc}")
    problems += [f"{path}: {p}" for p in _check_insertions(stored.insertions)]
    try:
        text = annotated.decode("utf-8")
    except UnicodeDecodeError as exc:  # R3: annotated files are UTF-8, as foundation is
        return problems + [f"{path}: annotated file is not UTF-8: {exc}"]
    problems += [f"{path}: {p}" for p in _check_markers(text, stored.prefix, nodes)]
    tree_problems = _check_tree(source, nodes)
    problems += [f"{path}: {p}" for p in tree_problems]
    if not tree_problems:
        problems += [f"{path}: {p}" for p in _check_places(source, annotated, stored, nodes)]
    expected = block_structure(source)
    try:
        found = block_structure(annotated)
    except RecursionError:  # R64: nested deeper than the parser follows, as foundation never is
        found = None
    if found != expected:  # R64: same blocks as foundation
        problems.append(f"{path}: the annotated file does not parse to foundation's blocks")
    return problems


def _check_insertions(insertions: list[Insertion]) -> list[str]:
    """Inserted bytes are markers plus " ", line endings, ">" and "|"; never a tab.

    Spec: R23, R38
    """
    problems: list[str] = []
    for ins in insertions:
        rest = MARKER_RE.sub("", ins.text.decode("utf-8", "replace"))
        if not set(rest) <= set(" \r\n>|"):
            problems.append(f"insertion at {ins.offset} adds {ins.text!r}")
    return problems


def _check_markers(text: str, prefix: str, nodes: list[StoredNode]) -> list[str]:
    """Markers well formed, file marker first, each ID once, frames nested.

    Spec: R3, R24, R25, R29, R52, R64
    """
    problems: list[str] = []
    for found in ANY_MARKER_RE.findall(text):
        if not MARKER_RE.fullmatch(found):  # R29: the marker pattern
            problems.append(f"malformed marker {found!r}")
    uses: dict[str, list[str]] = {}
    for match in MARKER_RE.finditer(text):
        uses.setdefault(match.group(1), []).append((match.group(2) or "").strip())
    for ident, roles in uses.items():
        if roles not in (["begin", "end"], [""]):  # R25: inline once, or begin then end
            problems.append(f"{ident} appears as {roles}")
    stack: list[str] = []
    for match in MARKER_RE.finditer(text):  # R24: each end closes the last open frame
        ident, role = match.group(1), (match.group(2) or "").strip()
        if role == "begin":
            stack.append(ident)
        elif role == "end" and ident in stack:
            if stack[-1] != ident:
                problems.append(f"the frame of {ident} ends inside the frame of {stack[-1]}")
            stack.remove(ident)
    body = text[1:] if text.startswith(_BOM) else text  # R29, R52: the file marker goes after a BOM
    if not body.startswith((f"⟬{prefix}⟭\n", f"⟬{prefix}⟭\r")):  # R3, R52: "\n", "\r\n" or a lone "\r"
        problems.append(f"the file marker ⟬{prefix}⟭ is not on the first line")
    expected = {n.id for n in nodes}  # R64: exactly the file's active nodes
    found_ids = set(uses)
    for ident in sorted(expected - found_ids):
        problems.append(f"{ident} is in the JSONL but not in the annotated file")
    for ident in sorted(found_ids - expected):
        problems.append(f"{ident} is in the annotated file but not among the file's JSONL nodes")
    return problems


def _check_tree(source: bytes, nodes: list[StoredNode]) -> list[str]:
    """The rebuilt tree matches the stored nodes, in pre-order.

    Spec: R53, R61, R64
    """
    root = build_tree(source)
    rebuilt = list(walk(root))
    if len(rebuilt) != len(nodes):
        return [f"the tree has {len(rebuilt)} nodes, the JSONL {len(nodes)}"]
    problems: list[str] = []
    stored_id = {id(new): old.id for new, old in zip(rebuilt, nodes)}
    parent_of: dict[int, str | None] = {id(root): None}
    for new in rebuilt:
        for child in new.children:
            parent_of[id(child)] = stored_id[id(new)]
    for new, old in zip(rebuilt, nodes):
        same = (
            new.kind is old.kind
            and new.start == old.start
            and new.end == old.end
            and new.own_hash == old.own_hash
            and new.tree_hash == old.tree_hash
        )
        if not same:
            problems.append(f"{old.id}: kind, span or hash differs from the rebuilt tree")
        elif old.parent != parent_of[id(new)]:  # R53, R61: the next build reads the parent
            problems.append(f"{old.id}: parent {old.parent} in the JSONL, {parent_of[id(new)]} in the tree")
    return problems


def _check_places(source: bytes, annotated: bytes, stored: StoredFile, nodes: list[StoredNode]) -> list[str]:
    """Each ID at its node: annotating again with the stored IDs gives the same bytes.

    Called once the rebuilt tree matches `nodes` node for node, so the
    stored IDs can be given to it in pre-order.

    Spec: R23, R61, R64
    """
    root = build_tree(source)
    for node, old in zip(walk(root), nodes):
        node.id = old.id
    try:
        expected, insertions = annotate(source, root)
    except ValueError as exc:
        return [f"cannot annotate again with the stored IDs: {exc}"]
    problems: list[str] = []
    if expected != annotated:
        problems.append("the annotated file differs from foundation annotated with the stored IDs")
    if [(i.offset, i.text) for i in insertions] != [(i.offset, i.text) for i in stored.insertions]:  # R61: as stored
        problems.append("the recorded insertions differ from those of the stored IDs")
    return problems
