"""JSONL store of the norms tree and matching against the previous run.

The JSONL is the only source of truth for the IDs and their history, as
the specs are for the content: it holds every ID ever given, with its
node's place and text. This module reads and writes it, gives IDs to
the nodes of a new tree by matching it against the previous JSONL, and
reports what changed between two versions.

JSONL format, one JSON object per line, keys sorted,
`ensure_ascii=False`:

    {"type": "meta", "specs_commit": ..., "generator_version": ...,
     "retired_prefixes": [...]}
    {"type": "file", "path": ..., "prefix": ..., "sha256": ...,
     "insertions": [[offset, text], ...]}
    {"type": "node", "id": ..., "file": ..., "kind": ..., "parent": ...,
     "start": ..., "end": ..., "own_text": ..., "own_hash": ...,
     "tree_hash": ..., "status": "active" | "retired",
     "to_review": bool, "changed_since": commit | null}

Order: meta; files by path; active nodes by file path, then pre-order;
retired nodes after, by file path, then prefix, then number. Text is
stored as `str` (the UTF-8 bytes decoded); offsets are byte offsets.

`to_review` is true when the node's status is `edited`: its own hash
changed in this run, however it was paired. A container whose own text
holds no information (a file, section, list or block quote: only blank
lines, `>` prefixes and thematic breaks) is not edited when only that
text changed: a child came or went, and its status is `child_changed`.
`changed_since` is the specs commit of the previous version when the
node's tree hash changed in this run (it, or something below it, changed:
whoever cited it must check). Both describe one version, the step from
the previous version to this one: the next version computes them again
from its own step, nothing is carried over; a rebuild of the same version
keeps them (in cli.py). Layer 3 compares the version it pinned with the
new one through the tree hashes.

Typical run:

    previous = read_store(path)                  # or Store() on the first run
    renames = detect_renames(trees, previous)    # before prefixes
    prefixes = assign_prefixes(sorted(trees), previous.prefixes(),
                               previous.retired_prefixes(), renames)
    changes = assign_ids(trees, previous, prefixes)
    store = build_store(trees, prefixes, previous, changes, ...)
    write_store(path, store)
    report_markdown(changes)

Matching (`assign_ids`), in stages; each stage only pairs nodes left
unpaired by the earlier ones, and a retired node is never a candidate:

A. Identical subtrees: a new node with children and a previous active
   node of the same kind and tree hash are paired, with all their
   descendants. Largest subtrees first.
B. Exact text: a new content node and a previous one of the same kind
   and own hash, across all files. First the texts that occur
   once among the free new nodes and once among the free old ones; then
   the structural containers whose paired children all come from one
   old container (stage D, unanimous votes only), so that the parents of
   repeated texts are known; then the repeated texts.

Stages A and B rank every candidate pair at once and pair the best pairs
first, so a node never takes an old node that another new node fits
better (a copy elsewhere never takes the ID of an original that did not
move). The best pair is in the same file (same prefix), then under the
same parent ID, then next to the same neighbour (a sibling before or
after it paired with the old node's sibling there), then closest in
order among the copies of its text in its file (byte offsets would let
text inserted above two copies swap their IDs).
C. Similar text: the remaining content nodes of the same kind are paired
   by `difflib.SequenceMatcher` ratio of their own text (without the ">"
   prefixes and indentation that start its lines), at least
   `SIMILARITY_THRESHOLD`, greedy best pair first; a pair in the same
   file ranks as if its ratio were `SAME_FILE_BONUS` higher. The node
   keeps its ID and is marked to review. The ratios are computed
   lazily, best upper bound first (`_SimilarPairs`): the result is that of
   scoring every pair, without the cost when a wording change touches the
   whole corpus.
D. Structural containers (`STRUCTURAL` kinds: their own text is only
   gaps, pipes or `>` markers, alike in every node) are paired by their
   children, bottom-up: the previous container that was the parent of
   most of the new container's paired children; tie-break same own
   hash, same file, same parent ID, same neighbour, byte distance,
   then previous JSONL order. A section goes first to the old
   section whose heading its heading is paired with, so a new
   subsection never takes its parent's ID. A container none of whose
   children was paired gets a new ID. Containers without children are
   paired last, by kind and own hash.

Then every node still unpaired gets the next number of its file's prefix,
in pre-order: numbers are never reused, since the highest number of
each prefix is taken over all IDs ever stored, retired ones included.
Previous nodes left unpaired are retired with their last text. A FILE
node's ID is its file's prefix, paired by prefix, so a renamed
file (same prefix) keeps its FILE node.

Note: D27c

Spec: R4, R7, R11, R15, R23, R31, R53, R54, R55, R56, R57, R58, R59, R60, R61, R63, U3 (E70, E71, E72, E76, E78, E83, E84, E86, E87)
"""

from __future__ import annotations

import bisect
import difflib
import heapq
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Any

from norms_generator.model import Insertion, Kind, TreeNode

SIMILARITY_THRESHOLD = 0.6  # R55: the least ratio of a similar pair
SAME_FILE_BONUS = 0.1  # R55: a pair in one file ranks this much higher
_BONUS = Fraction(1, 10)  # R55: SAME_FILE_BONUS exactly, so that 0.7 + 0.1 ties with 0.8; Note: D27c
RENAME_MIN_FRACTION = 0.5  # R58: a rename takes more than half

STRUCTURAL = frozenset(  # R53, R56: the containers, which follow their children
    {Kind.SECTION, Kind.LIST, Kind.BLOCK_QUOTE, Kind.TABLE, Kind.TABLE_ROW}
)

_ID_RE = re.compile(r"^([A-Z]+)-([0-9]+)$")


# ---------------------------------------------------------------- records


@dataclass
class StoredFile:
    """One `file` line: a spec file and what the annotation added.

    Spec: R61
    """

    path: str
    prefix: str
    sha256: str = ""  # of the spec file's bytes
    insertions: list[Insertion] = field(default_factory=list)


@dataclass
class StoredNode:
    """One `node` line.

    Spec: R61
    """

    id: str
    file: str  # path of the file the node is in (or was last in)
    kind: Kind
    parent: str | None  # parent's ID; None for a FILE node
    start: int
    end: int
    own_text: str
    own_hash: str
    tree_hash: str
    status: str = "active"  # "active" | "retired"
    to_review: bool = False
    changed_since: str | None = None


@dataclass
class Store:
    """The whole JSONL: meta, files and nodes. `Store()` is the empty store.

    Spec: R23, R61
    """

    specs_commit: str = ""
    generator_version: str = ""
    retired_prefix_list: list[str] = field(default_factory=list)
    files: dict[str, StoredFile] = field(default_factory=dict)
    nodes: list[StoredNode] = field(default_factory=list)
    copies: dict[str, str] = field(default_factory=dict)  # R61, R62: plain copy path -> sha256 of its bytes

    def prefixes(self) -> dict[str, str]:
        """path -> prefix of the files in this store."""
        return {path: f.prefix for path, f in self.files.items()}

    def retired_prefixes(self) -> set[str]:
        """Prefixes that must never be given again to a new file.

        The recorded retired prefixes, plus every prefix used by a stored
        ID that is not a current file's (a node moved out of a vanished
        file keeps its old prefix).

        Spec: R11, R58
        """
        out = set(self.retired_prefix_list)
        current = {f.prefix for f in self.files.values()}
        for node in self.nodes:
            prefix = _prefix_of(node.id)
            if prefix not in current:
                out.add(prefix)
        return out

    def active(self) -> list[StoredNode]:
        """Active nodes, in stored order."""
        return [n for n in self.nodes if n.status == "active"]


class Status(str, Enum):
    """What happened to one ID between two versions.

    Spec: R59
    """

    UNCHANGED = "unchanged"
    MOVED = "moved"  # same text and tree, other parent or other file
    EDITED = "edited"  # R59, R60: own hash changed, to review
    CHILD_CHANGED = "child_changed"  # R59: own hash same, tree hash changed (E74)
    NEW = "new"
    RETIRED = "retired"


@dataclass
class Change:
    """The change record of one ID: a line of `data/report.json`.

    Spec: R63
    """

    id: str
    status: Status
    kind: Kind
    file: str  # current file; for a retired ID, its last file
    old_file: str | None = None
    old_parent: str | None = None
    new_parent: str | None = None
    old_text: str | None = None  # None for a new ID
    new_text: str | None = None  # None for a retired ID
    old_tree_hash: str | None = None
    new_tree_hash: str | None = None
    moved: bool = False  # R59: parent or file changed, also for edited etc.
    reordered: bool = False  # R59: numbered list whose children changed order
    changed_children: list[str] = field(default_factory=list)  # R59: direct children
    similarity: float | None = None  # R55: set when paired by similar text
    last_text: str | None = None  # R63: a retired ID's whole last text, children included (E85)
    old: StoredNode | None = None  # previous node line, not reported

    def to_json(self) -> dict[str, object]:
        """The JSON form of the record (without `old`), with the report's fields.

        Spec: R63
        """
        return {
            "id": self.id,
            "status": self.status.value,
            "kind": self.kind.value,
            "file": self.file,
            "old_file": self.old_file,
            "old_parent": self.old_parent,
            "new_parent": self.new_parent,
            "old_text": self.old_text,
            "new_text": self.new_text,
            "old_tree_hash": self.old_tree_hash,
            "new_tree_hash": self.new_tree_hash,
            "moved": self.moved,
            "reordered": self.reordered,
            "changed_children": list(self.changed_children),
            "similarity": self.similarity,
            "last_text": self.last_text,
        }


# ---------------------------------------------------------------- helpers


def _prefix_of(node_id: str) -> str:
    """"TYP-3" -> "TYP"; "TYP" -> "TYP"."""
    return node_id.split("-", 1)[0]


def _number_of(node_id: str) -> int:
    """"TYP-3" -> 3; a FILE ID -> 0."""
    m = _ID_RE.match(node_id)
    return int(m.group(2)) if m else 0


def _text(data: bytes) -> str:
    """The specs bytes as `str`: spec files are UTF-8.

    Spec: R3
    """
    return data.decode("utf-8")


def _walk(node: TreeNode, parent: TreeNode | None = None) -> Iterator[tuple[TreeNode, TreeNode | None]]:
    """(node, parent) in pre-order."""
    yield node, parent
    for child in node.children:
        yield from _walk(child, node)


def _dumps(obj: dict[str, object]) -> str:
    """One JSON line: keys sorted, no spaces, non-ASCII as it is.

    Spec: R61, R63
    """
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------- read / write


def store_lines(store: Store) -> list[str]:
    """The JSONL lines of `store`, in the order the JSONL format and this module fix.

    Spec: R61
    """
    lines = [
        _dumps(
            {
                "type": "meta",
                "specs_commit": store.specs_commit,
                "generator_version": store.generator_version,
                "retired_prefixes": sorted(set(store.retired_prefix_list)),
            }
        )
    ]
    for path in sorted(store.files):
        f = store.files[path]
        lines.append(
            _dumps(
                {
                    "type": "file",
                    "path": f.path,
                    "prefix": f.prefix,
                    "sha256": f.sha256,
                    "insertions": [[i.offset, _text(i.text)] for i in f.insertions],
                }
            )
        )
    for path in sorted(store.copies):  # R61: one copy line per plain copy, by path
        lines.append(_dumps({"type": "copy", "path": path, "sha256": store.copies[path]}))
    for node in _ordered_nodes(store):
        lines.append(
            _dumps(
                {
                    "type": "node",
                    "id": node.id,
                    "file": node.file,
                    "kind": node.kind.value,
                    "parent": node.parent,
                    "start": node.start,
                    "end": node.end,
                    "own_text": node.own_text,
                    "own_hash": node.own_hash,
                    "tree_hash": node.tree_hash,
                    "status": node.status,
                    "to_review": node.to_review,
                    "changed_since": node.changed_since,
                }
            )
        )
    return lines


def _ordered_nodes(store: Store) -> list[StoredNode]:
    """Active nodes by file (stable: pre-order kept), then retired ones by file, prefix, number.

    Spec: R61
    """
    active = [n for n in store.nodes if n.status == "active"]
    retired = [n for n in store.nodes if n.status != "active"]
    active.sort(key=lambda n: n.file)  # stable sort keeps pre-order
    retired.sort(key=lambda n: (n.file, _prefix_of(n.id), _number_of(n.id)))
    return active + retired


def write_store(path: str | Path, store: Store) -> None:
    """Write `store` to `path` as JSONL, UTF-8 with `\\n` line ends.

    Spec: R3, R61, R62
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = "".join(line + "\n" for line in store_lines(store)).encode("utf-8")
    # R62: encoded first, then written aside and moved in: a failure leaves the
    # previous JSONL as it was, never a truncated one; Note: D45
    tmp = p.with_name(p.name + ".tmp")
    write_new(tmp, data)
    os.replace(tmp, p)


def write_new(path: str | Path, data: bytes) -> None:
    """Write `data` to `path` as a new file, never into the file that stands there.

    What stands at `path` is removed first, then the file is created with
    an exclusive create (`O_CREAT | O_EXCL`), which fails rather than open
    a file someone put there meanwhile. So a hard link at `path`, sharing
    its bytes with another name inside or outside the output folder, is
    never written through: that name keeps its bytes. A folder at `path`
    is refused by the system (check_outputs and the sweep of specs-repo-annotated/
    leave none there).

    Spec: R62, U6
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.unlink(p)
    except FileNotFoundError:
        pass
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o666)
    with os.fdopen(fd, "wb") as f:
        f.write(data)


def store_absent(path: str | Path) -> bool:
    """Whether nothing at all is at `path`, so that a build is a first run.

    Not `Path.exists()`, which follows a symbolic link: a link that leads
    nowhere or loops, or a file in place of `data/`, is a JSONL that
    cannot be opened, not an absent one.

    Spec: R23, R34
    """
    try:
        os.lstat(path)
    except FileNotFoundError:
        return True
    except OSError:
        return False
    return False


class StoreError(ValueError):
    """The JSONL cannot be read: not UTF-8, a line that is not JSON, or a field missing or wrong.

    Spec: R34, R61
    """


def read_store(path: str | Path) -> Store:
    """Read a JSONL store; a missing file gives the empty store.

    Raises StoreError, naming the file and the line, when it is corrupt.

    Spec: R23, R34, R61
    """
    p = Path(path)
    if store_absent(p):
        return Store()
    try:
        # bytes, not read_text(): its universal newlines would split at a lone "\r"
        data = p.read_bytes()
    except OSError as exc:  # R34, R64: a folder or a broken link at its path, no permission to read it
        raise StoreError(f"{p}: cannot be opened: {exc.strerror or exc}") from None
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:  # R34, R61: not UTF-8, named with the first bad byte's offset
        raise StoreError(f"{p}: not UTF-8: {exc}") from None
    store = Store()
    # R61: split on "\n" only; str.splitlines() also splits on "\r", U+2028,
    # U+2029, U+0085 and others, which json.dumps(ensure_ascii=False) leaves as is
    for number, line in enumerate(text.split("\n"), 1):
        if not line.strip():  # R61: empty or str.isspace() only, skipped
            continue
        try:
            obj = json.loads(line, parse_constant=_not_json)
            _check_unicode(obj)
            _read_line(store, obj)
        # R34, R61: file, line, error name, message; a line nested deeper than
        # the reader goes gives RecursionError, and is no JSON object it can read
        except (ValueError, KeyError, TypeError, AttributeError, RecursionError) as exc:
            raise StoreError(f"{p}:{number}: {type(exc).__name__}: {exc}") from None
    return store


def _not_json(token: str) -> Any:
    """ValueError for `NaN`, `Infinity` and `-Infinity`: json.loads takes them, but they are not JSON.

    Spec: R61
    """
    raise ValueError(f"{token} is not JSON")


def _check_unicode(value: Any) -> None:
    """ValueError for a string holding a lone surrogate (`"\\ud800"`): valid JSON, but not UTF-8.

    Spec: R61
    """
    if isinstance(value, str):
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise ValueError(f"a string that is not valid Unicode: {value!r}") from None
    elif isinstance(value, list):
        for v in value:
            _check_unicode(v)
    elif isinstance(value, dict):
        for k, v in value.items():
            _check_unicode(k)
            _check_unicode(v)


_STORED_PREFIX_RE = re.compile(r"[A-Z]{3,}")  # R10, R61: a prefix's form; fullmatch, since "$" also matches before a final "\n"
_STORED_ID_RE = re.compile(r"[A-Z]{3,}(-[1-9][0-9]*)?")  # R61: no leading zeros, no `-0`
_MISSING = object()


def _field(obj: dict[str, Any], name: str, check: Callable[[Any], bool], default: Any = _MISSING) -> Any:
    """`obj[name]`, or `default` when it is absent; ValueError when it is of the wrong type or form.

    Spec: R61
    """
    if name not in obj:
        if default is _MISSING:
            raise KeyError(name)
        return default
    value = obj[name]
    if not check(value):
        raise ValueError(f"bad {name} {value!r}")
    return value


def _is_str(v: Any) -> bool:
    return isinstance(v, str)


def _is_int(v: Any) -> bool:
    """An integer of 0 or more, not a bool.

    Spec: R61
    """
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def _is_prefix(v: Any) -> bool:
    return isinstance(v, str) and bool(_STORED_PREFIX_RE.fullmatch(v))


def _is_id(v: Any) -> bool:
    return isinstance(v, str) and bool(_STORED_ID_RE.fullmatch(v))


def has_control(text: str) -> bool:
    """Whether `text` holds a control character, Unicode category Cc: U+0000-U+001F, U+007F-U+009F.

    Spec: R34, R61
    """
    return any(unicodedata.category(c) == "Cc" for c in text)


def escape_controls(text: str) -> str:
    """`text` with each control character written as `\\x0a`, as a message names such a path.

    Spec: R34
    """
    return "".join(f"\\x{ord(c):02x}" if unicodedata.category(c) == "Cc" else c for c in text)


def _is_path(v: Any, markdown: bool = True) -> bool:
    """A spec path as git lists it: relative, `/`-separated, a `.md` name (a file line) or another (a copy line).

    No part is empty, `.` or `..`, and none holds a NUL, so the path stays
    under specs-repo-annotated/: build removes the annotated copy of a vanished
    file's path, which must never reach outside the output folder.
    Nor does it hold another control character, which build refuses in
    a spec path: a line break would split a heading of the
    report or a line of verify's output.

    Spec: R34, R61, R62
    """
    if not (isinstance(v, str) and v.endswith(".md") == markdown and not has_control(v)):
        return False
    return all(part not in ("", ".", "..") for part in v.split("/"))


def _is_insertions(v: Any) -> bool:
    """A list of `[offset, text]` pairs.

    Spec: R61
    """
    return isinstance(v, list) and all(
        isinstance(i, list) and len(i) == 2 and _is_int(i[0]) and _is_str(i[1]) for i in v
    )


def _read_line(store: Store, obj: dict[str, Any]) -> None:
    """Add one JSONL line to `store`.

    Required: `path` and `prefix` on a file line; `path` on a copy line; `id`, `file`, `kind`,
    `start`, `end`, `own_text`, `own_hash` and `tree_hash` on a node line.
    Every other field has a default. A field present with the wrong type
    or form, or an unknown line type, is an error.

    Spec: R34, R61, R64
    """
    if not isinstance(obj, dict):
        raise ValueError("not a JSON object")
    kind = obj.get("type")
    # R61: a second meta line, or a second file or copy line for one path, replaces the first
    if kind == "meta":
        store.specs_commit = _field(obj, "specs_commit", _is_str, "")
        store.generator_version = _field(obj, "generator_version", _is_str, "")
        store.retired_prefix_list = list(
            _field(obj, "retired_prefixes", lambda v: isinstance(v, list) and all(map(_is_prefix, v)), [])
        )
    elif kind == "file":
        path = _field(obj, "path", _is_path)
        store.files[path] = StoredFile(
            path=path,
            prefix=_field(obj, "prefix", _is_prefix),
            sha256=_field(obj, "sha256", _is_str, ""),
            insertions=[
                Insertion(offset, text.encode("utf-8"))
                for offset, text in _field(obj, "insertions", _is_insertions, [])
            ],
        )
    elif kind == "copy":
        store.copies[_field(obj, "path", lambda v: _is_path(v, markdown=False))] = _field(obj, "sha256", _is_str, "")
    elif kind == "node":
        store.nodes.append(
            StoredNode(
                id=_field(obj, "id", _is_id),
                file=_field(obj, "file", _is_str),
                kind=Kind(_field(obj, "kind", _is_str)),
                parent=_field(obj, "parent", lambda v: v is None or _is_id(v), None),
                start=_field(obj, "start", _is_int),
                end=_field(obj, "end", _is_int),
                own_text=_field(obj, "own_text", _is_str),
                own_hash=_field(obj, "own_hash", _is_str),
                tree_hash=_field(obj, "tree_hash", _is_str),
                status=_field(obj, "status", lambda v: v in ("active", "retired"), "active"),
                to_review=_field(obj, "to_review", lambda v: isinstance(v, bool), False),
                changed_since=_field(obj, "changed_since", lambda v: v is None or _is_str(v), None),
            )
        )
    else:
        raise ValueError(f"unknown line type {kind!r}")


# ---------------------------------------------------------------- renames


def detect_renames(new_trees: dict[str, TreeNode], previous: Store) -> dict[str, str | None]:
    """Files renamed or moved since `previous`: new path -> old path.

    Runs before prefixes are assigned. The candidates are the previous
    paths that vanished and the new paths that did not exist, plus every
    path present in both whose new content does not mostly come from its
    old content (another file was moved there, or two files swapped
    names). The content nodes of the candidates are matched once, over
    all of them (`_pool_matches`): exact twins (same kind and own hash),
    then, among the rest, nodes of the same kind with similar text, as
    stages B and C of `assign_ids` do, lazily. An old path is
    renamed to the new path that holds more than `RENAME_MIN_FRACTION`
    of its active content nodes. Pairs are taken best fraction first; at
    equal fraction a path paired with itself (no rename) wins, then by
    path. An old file without content nodes (blank lines, thematic breaks and
    block quotes without children) is renamed to a new one without content
    nodes whose FILE node has the same own text, so the same own hash,
    although their bytes may differ (the case "No content").

    A path present in both and not paired with itself maps to None, a
    new file put there that gets a new prefix, when its old
    path was renamed to another path (more than half of its content went
    there), or when none of its old content nodes is matched at that path.
    A path that keeps some of its content, and was not renamed, keeps its
    prefix, even when some of its content went elsewhere: a stub filled
    in, a file rewritten in place.

    Note: D27c, D40

    Spec: R12, R58 (E78, E79, E80, E81, E82)
    """
    old_nodes: dict[str, list[StoredNode]] = defaultdict(list)
    for n in previous.active():
        if n.kind is not Kind.FILE and n.kind not in STRUCTURAL:
            old_nodes[n.file].append(n)
    new_nodes: dict[str, list[TreeNode]] = {
        path: [n for n, _ in _walk(root) if n.kind is not Kind.FILE and n.kind not in STRUCTURAL]
        for path, root in new_trees.items()
    }
    old_pool = sorted(set(previous.files) - set(new_trees))
    new_pool = sorted(set(new_trees) - set(previous.files))
    for path in sorted(set(previous.files) & set(new_trees)):
        kept = new_nodes[path]
        if not kept or not old_nodes[path]:  # R58: emptied or filled in, not a candidate
            continue
        shared = _shared_exact(old_nodes[path], kept)
        if shared / len(kept) <= RENAME_MIN_FRACTION:  # R58: mostly not its old content, a candidate
            old_pool.append(path)
            new_pool.append(path)
    if not old_pool or not new_pool:
        return {}
    counts = _pool_matches(old_nodes, new_nodes, old_pool, new_pool)
    old_file_hash = {n.file: n.own_hash for n in previous.active() if n.kind is Kind.FILE}
    scored: list[tuple[float, int, str, str]] = []
    for old_path in old_pool:
        olds = old_nodes[old_path]
        for new_path in new_pool:
            if not olds:  # R58: no content, the same own hash of the file node (E82)
                same = not new_nodes[new_path] and new_trees[new_path].own_hash == old_file_hash.get(old_path)
                fraction = 1.0 if same else 0.0
            else:
                fraction = counts.get((old_path, new_path), 0) / len(olds)
            if fraction > RENAME_MIN_FRACTION:
                scored.append((-fraction, 0 if new_path == old_path else 1, old_path, new_path))
    scored.sort()  # R58: best fraction, then a path paired with itself, then the paths (E79)
    renames: dict[str, str | None] = {}
    taken_old: set[str] = set()
    taken_new: set[str] = set()
    for _, _, old_path, new_path in scored:
        if old_path in taken_old or new_path in taken_new:
            continue
        taken_old.add(old_path)
        taken_new.add(new_path)
        if new_path != old_path:
            renames[new_path] = old_path
    for path in sorted(set(old_pool) & set(new_pool) - taken_new):
        if path in taken_old or not counts.get((path, path)):
            renames[path] = None  # R58: replaced, renamed elsewhere or none of its old content is here (E79, E80)
    return renames


def _shared_exact(olds: list[StoredNode], news: list[TreeNode]) -> int:
    """Number of exact twins (same kind and own hash) between two lists of nodes, for the rename candidates.

    Spec: R58
    """
    old_keys = Counter((n.kind, n.own_hash) for n in olds)
    new_keys = Counter((n.kind, n.own_hash) for n in news)
    return sum((old_keys & new_keys).values())


def _pool_matches(
    old_nodes: dict[str, list[StoredNode]],
    new_nodes: dict[str, list[TreeNode]],
    old_pool: list[str],
    new_pool: list[str],
) -> Counter[tuple[str, str]]:
    """(old path, new path) -> content nodes of the old file matched in the new one.

    One matching over every node of the candidate files, each node
    matched at most once: exact twins (same kind and own hash), in the
    same path first, then in path and document order; then similar text
    among the rest, best pair first and the same path ranking higher, as
    in stage C, with its lazy bounds: a folder moved or a wording changed
    across the corpus costs one matching, not one per pair of files.

    Note: D27c, D40

    Spec: R55, R58
    """
    olds = [(path, n) for path in sorted(set(old_pool)) for n in old_nodes[path]]
    news = [(path, n) for path in sorted(set(new_pool)) for n in new_nodes[path]]
    counts: Counter[tuple[str, str]] = Counter()
    old_by_key: dict[tuple[Kind, str], list[int]] = defaultdict(list)
    for i, (_, n) in enumerate(olds):
        old_by_key[(n.kind, n.own_hash)].append(i)
    new_by_key: dict[tuple[Kind, str], list[int]] = defaultdict(list)
    for j, (_, m) in enumerate(news):
        new_by_key[(m.kind, m.own_hash)].append(j)
    used_old: set[int] = set()
    used_new: set[int] = set()
    for key, js in new_by_key.items():
        is_ = old_by_key.get(key)
        if not is_:
            continue
        old_at: dict[str, list[int]] = defaultdict(list)
        new_at: dict[str, list[int]] = defaultdict(list)
        for i in is_:
            old_at[olds[i][0]].append(i)
        for j in js:
            new_at[news[j][0]].append(j)
        left_old: list[int] = []
        left_new: list[int] = []
        for path in sorted(set(old_at) | set(new_at)):
            a, b = old_at.get(path, []), new_at.get(path, [])
            k = min(len(a), len(b))
            pairs_here = list(zip(a[:k], b[:k]))
            left_old += a[k:]
            left_new += b[k:]
            for i, j in pairs_here:
                used_old.add(i)
                used_new.add(j)
            counts[(path, path)] += k
        for i, j in zip(sorted(left_old), sorted(left_new)):
            used_old.add(i)
            used_new.add(j)
            counts[(olds[i][0], news[j][0])] += 1
    rest_old = [i for i in range(len(olds)) if i not in used_old]
    rest_new = [j for j in range(len(news)) if j not in used_new]
    pairs = _SimilarPairs(
        [(news[j][1].kind, _comparable(_text(news[j][1].own_text)), news[j][0]) for j in rest_new],
        [(olds[i][1].kind, _comparable(olds[i][1].own_text), olds[i][0]) for i in rest_old],
    )
    for n, o, _ in pairs.best_first(lambda n, o: (o, n)):  # R58: ties: old first, then new; no byte distance
        pairs.taken(n, o)
        counts[(olds[rest_old[o]][0], news[rest_new[n]][0])] += 1
    return counts


_LINE_PREFIX = re.compile(r"(^|\r\n|\r|\n)[ \t>]+")  # R3: a line starts after any of the three line endings


def _comparable(text: str) -> str:
    """Own text without the runs of spaces, tabs and ">" that start its lines, for similarity only.

    Every such run goes, in a code or HTML block too, where a ">" that
    starts a line is content. A line starts after an LF, a CRLF or a
    lone CR.

    A paragraph that leaves a quote of one paragraph (one child, one ID:
    "> q" becomes "q" once the quote holds more) or moves to another
    nesting level keeps its words; its hashes still change, and it is
    paired and marked to review like any edit.

    Spec: R3, R15, R16, R27, R31, R55 (E72)
    """
    return _LINE_PREFIX.sub(r"\1", text)


def _similarity(a: str, b: str) -> float | None:
    """`difflib` ratio of two texts, or None below `SIMILARITY_THRESHOLD`.

    Spec: R55
    """
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    if matcher.real_quick_ratio() < SIMILARITY_THRESHOLD or matcher.quick_ratio() < SIMILARITY_THRESHOLD:
        return None
    ratio = matcher.ratio()
    return ratio if ratio >= SIMILARITY_THRESHOLD else None


_NO_INFORMATION = re.compile(r"[\s>*_-]")  # blank lines, ">" prefixes and their blanks, thematic breaks
_INFORMATION_FREE = frozenset({Kind.FILE, Kind.SECTION, Kind.LIST, Kind.BLOCK_QUOTE})


def _same_information(kind: Kind, old_text: str, new_text: str) -> bool:
    """True if two own texts of a container differ only where they hold no information.

    The own text of a file, section, list or block quote is what its
    children leave: blank lines, ">" prefixes and the blanks around them,
    and thematic breaks; the indentation of a child's first line is
    the child's own text. Nothing else is ever compared away: tables
    and rows are not covered, and a BOM is information.

    Spec: R7, R15, R16, R59 (E86)
    """
    if kind not in _INFORMATION_FREE:
        return old_text == new_text
    return _NO_INFORMATION.sub("", old_text) == _NO_INFORMATION.sub("", new_text)


# ---------------------------------------------------------------- matching


class _SimilarPairs:
    """Pairs of similar texts, yielded best first without scoring every pair (stage C).

    A pair's score is its `difflib` ratio, plus `SAME_FILE_BONUS` when both
    are in the same file (same prefix), computed exactly as fractions (in
    floats 0.7 + 0.1 < 0.8, and a same-file pair would lose a tie); a pair below `SIMILARITY_THRESHOLD`
    is never yielded. Pairs come in the order of (-score, tie) where `tie`
    is the caller's tie-break, exactly as a sort of all scored pairs.

    Lazy evaluation with upper bounds: the length bound (`real_quick_ratio`,
    known from the two lengths), then the character bound (`quick_ratio`),
    then the ratio. A heap holds, for each new text, its next candidate by
    length bound (olds sorted by length: the bound falls on both sides of
    the new text's length), and the bounds and scores computed so far. A
    bound sorts before a score of the same value, so a score popped from
    the heap is the best of all the pairs left. Pairs whose new or old text
    is taken are dropped when they come up.

    Note: D27c

    Spec: R55
    """

    def __init__(self, news: list[tuple[Kind, str, str]], olds: list[tuple[Kind, str, str | None]]):
        self.news, self.olds = news, olds
        # olds by kind (all files) and by kind and prefix (one file), sorted by length
        self.pools: dict[tuple[Kind, str | None] | Kind, list[int]] = defaultdict(list)
        for o, (kind, _, prefix) in enumerate(olds):
            self.pools[kind].append(o)
            self.pools[(kind, prefix)].append(o)
        for pool in self.pools.values():
            pool.sort(key=lambda o: (len(olds[o][1]), o))
        self.lengths = {key: [len(olds[o][1]) for o in pool] for key, pool in self.pools.items()}
        self.matchers: dict[int, difflib.SequenceMatcher[str]] = {}
        self.taken_new: set[int] = set()
        self.taken_old: set[int] = set()

    def taken(self, n: int, o: int) -> None:
        """The caller paired new text `n` with old text `o`."""
        self.taken_new.add(n)
        self.taken_old.add(o)

    def _candidates(self, n: int, same_file: bool) -> Iterator[tuple[Fraction, int]]:
        """(length bound, old) of new text `n`, bound not increasing, same file or not."""
        kind, text, prefix = self.news[n]
        key: tuple[Kind, str | None] | Kind = (kind, prefix) if same_file else kind
        idx, lengths = self.pools.get(key, []), self.lengths.get(key, [])
        la = len(text)

        def bound(lb: int) -> Fraction:
            return Fraction(2 * min(la, lb), la + lb) if la + lb else Fraction(1)

        right = bisect.bisect_left(lengths, la)
        left = right - 1
        while left >= 0 or right < len(idx):
            b_left = bound(lengths[left]) if left >= 0 else Fraction(-1)
            b_right = bound(lengths[right]) if right < len(idx) else Fraction(-1)
            if b_right >= b_left:
                b, o = b_right, idx[right]
                right += 1
            else:
                b, o = b_left, idx[left]
                left -= 1
            if b < SIMILARITY_THRESHOLD:
                return
            if (self.olds[o][2] == prefix) is same_file:
                yield b, o

    def _matcher(self, o: int, text: str) -> difflib.SequenceMatcher[str]:
        """A SequenceMatcher of (text, old text `o`), the old side's index kept."""
        matcher = self.matchers.get(o)
        if matcher is None:
            matcher = self.matchers[o] = difflib.SequenceMatcher(None, "", self.olds[o][1], autojunk=False)
        matcher.set_seq1(text)
        return matcher

    def best_first(self, tie: Callable[[int, int], tuple[int, ...]]) -> Iterator[tuple[int, int, float]]:
        """(new, old, ratio) of the pairs, best first; the caller marks the ones it takes."""
        heap: list[tuple[object, ...]] = []
        cursors: list[tuple[int, Fraction, Iterator[tuple[Fraction, int]]]] = []

        def advance(c: int) -> None:
            n, bonus, candidates = cursors[c]
            for b, o in candidates:
                if o not in self.taken_old:
                    heapq.heappush(heap, (-(b + bonus), 0, 0, (), 0, n, o, c))
                    return

        for n in range(len(self.news)):
            for same_file in (True, False):
                cursors.append((n, _BONUS if same_file else Fraction(0), self._candidates(n, same_file)))
                advance(len(cursors) - 1)
        while heap:
            entry = heapq.heappop(heap)
            exact, level, n, o, c = entry[1], entry[4], entry[5], entry[6], entry[7]
            if level == 0:
                advance(c)
            if n in self.taken_new or o in self.taken_old:
                continue
            bonus = cursors[c][1]
            if exact:
                yield n, o, entry[8]
                continue
            matcher = self._matcher(o, self.news[n][1])
            total = len(self.news[n][1]) + len(self.olds[o][1])
            if level == 0:
                quick = matcher.quick_ratio()
                if quick >= SIMILARITY_THRESHOLD:
                    # exact value of 2.0 * matches / total, from the float
                    exact_quick = Fraction(2 * round(quick * total / 2), total) if total else Fraction(1)
                    heapq.heappush(heap, (-(exact_quick + bonus), 0, 0, (), 1, n, o, c))
            else:
                ratio = matcher.ratio()
                if ratio >= SIMILARITY_THRESHOLD:
                    matches = sum(block.size for block in matcher.get_matching_blocks())
                    exact_ratio = Fraction(2 * matches, total) if total else Fraction(1)
                    heapq.heappush(heap, (-(exact_ratio + bonus), 1, 0, tie(n, o), 2, n, o, c, ratio))


@dataclass
class _New:
    """A new node with its context during matching."""

    node: TreeNode
    parent: _New | None
    file: str
    prefix: str
    rank: int  # pre-order rank over all files
    depth: int
    size: int = 1  # nodes in its subtree


class _Matcher:
    """State of one `assign_ids` run."""

    def __init__(self, trees: dict[str, TreeNode], previous: Store, prefixes: dict[str, str]):
        self.previous = previous
        self.prefixes = prefixes
        self.old_prefix = previous.prefixes()
        self.news: list[_New] = []
        self.wrap: dict[int, _New] = {}
        self.new_index: dict[int, int] = {}  # id(TreeNode) -> index among its siblings
        for path in sorted(trees):
            self._index(trees[path], None, path, 0)
        for item in reversed(self.news):
            if item.parent is not None:
                item.parent.size += item.size
        self.olds = [n for n in previous.active() if n.kind is not Kind.FILE]
        self.old_by_id = {n.id: n for n in previous.active()}
        self.old_rank = {n.id: i for i, n in enumerate(self.olds)}
        self.old_children: dict[str, list[StoredNode]] = defaultdict(list)
        for n in previous.active():
            if n.parent is not None:
                self.old_children[n.parent].append(n)
        self.old_size: dict[str, int] = {}
        for n in reversed(self.olds):
            self.old_size[n.id] = 1 + sum(self.old_size.get(c.id, 1) for c in self.old_children[n.id])
        self.old_sibling: dict[str, tuple[str | None, int]] = {}  # id -> (parent, index among siblings)
        for parent, kids in self.old_children.items():
            for i, kid in enumerate(kids):
                self.old_sibling[kid.id] = (parent, i)
        self.pair_of_new: dict[int, StoredNode] = {}  # id(TreeNode) -> old
        self.paired_old: set[str] = set()
        self.similarity: dict[int, float] = {}

    def _index(self, node: TreeNode, parent: _New | None, path: str, depth: int) -> None:
        item = _New(node, parent, path, self.prefixes[path], len(self.news), depth)
        self.news.append(item)
        self.wrap[id(node)] = item
        for i, child in enumerate(node.children):
            self.new_index[id(child)] = i
            self._index(child, item, path, depth + 1)

    # -- helpers

    def _old_prefix(self, old: StoredNode) -> str | None:
        return self.old_prefix.get(old.file)

    def _parent_id(self, item: _New) -> str | None:
        """The ID the new node's parent has so far (paired or file)."""
        if item.parent is None:
            return None
        if item.parent.node.kind is Kind.FILE:
            return item.parent.prefix
        old = self.pair_of_new.get(id(item.parent.node))
        return old.id if old else None

    def _rank_key(self, item: _New, old: StoredNode, order: int | None = None) -> tuple[int, int, int, int, int]:
        """Smaller is better: same file, same parent, same neighbours, closest position.

        `order` is the distance between the two nodes' ranks among the
        nodes of their key (same text) in their file, so that copies of one
        text pair in document order; byte offsets would let text inserted
        above them swap their IDs. Without it, the byte distance.

        Spec: R54, R56
        """
        same_file = 0 if self._old_prefix(old) == item.prefix else 1  # R53: same file, same prefix
        parent = self._parent_id(item)
        same_parent = 0 if parent is not None and parent == old.parent else 1
        neighbours = 0 if self._same_neighbour(item, old) else 1
        distance = order if order is not None else abs(old.start - item.node.start)
        return (same_file, same_parent, neighbours, distance, self.old_rank[old.id])

    def _same_neighbour(self, item: _New, old: StoredNode) -> bool:
        """True if a sibling next to the new node is paired with the old node's sibling there.

        Spec: R54
        """
        if item.parent is None or old.id not in self.old_sibling:
            return False
        siblings = item.parent.node.children
        index = self.new_index[id(item.node)]
        parent, old_index = self.old_sibling[old.id]
        old_siblings = self.old_children[parent] if parent is not None else []
        for step in (-1, 1):
            j, k = index + step, old_index + step
            if 0 <= j < len(siblings) and 0 <= k < len(old_siblings):
                paired = self.pair_of_new.get(id(siblings[j]))
                if paired is not None and paired.id == old_siblings[k].id:
                    return True
        return False

    @staticmethod
    def _ordinals(entries: list[tuple[object, str, int]]) -> dict[int, int]:
        """(key, file, ident) in document order -> ident: rank among its key in its file.

        Spec: R54
        """
        seen: Counter[tuple[object, str]] = Counter()
        out: dict[int, int] = {}
        for key, file, ident in entries:
            out[ident] = seen[(key, file)]
            seen[(key, file)] += 1
        return out

    def _pair(self, item: _New, old: StoredNode) -> None:
        self.pair_of_new[id(item.node)] = old
        self.paired_old.add(old.id)

    def _free(self, item: _New) -> bool:
        return id(item.node) not in self.pair_of_new and item.node.kind is not Kind.FILE

    # -- stages

    def stage_subtrees(self) -> None:
        """A: identical subtrees, largest first, best pairs first.

        Spec: R54
        """
        by_key: dict[tuple[Kind, str], list[StoredNode]] = defaultdict(list)
        for old in self.olds:
            if self.old_children[old.id]:
                by_key[(old.kind, old.tree_hash)].append(old)
        old_ord = self._ordinals([((o.kind, o.tree_hash), o.file, id(o)) for o in self.olds])
        new_ord = self._ordinals([((i.node.kind, i.node.tree_hash), i.file, id(i)) for i in self.news])
        pairs: list[tuple[tuple[object, ...], _New, StoredNode]] = []
        for item in self.news:
            if not item.node.children or item.node.kind is Kind.FILE:
                continue
            for old in by_key.get((item.node.kind, item.node.tree_hash), []):
                order = abs(old_ord[id(old)] - new_ord[id(item)])
                pairs.append(((-item.size, self._rank_key(item, old, order), item.rank), item, old))
        pairs.sort(key=lambda p: p[0])
        for _, item, old in pairs:
            if self._free(item) and old.id not in self.paired_old:
                self._pair_subtree(item, old)

    def _pair_subtree(self, item: _New, old: StoredNode) -> None:
        """Pair two identical subtrees, with all their descendants.

        Spec: R54
        """
        if not self._free(item) or old.id in self.paired_old:
            return
        self._pair(item, old)
        remaining = [c for c in self.old_children[old.id] if c.id not in self.paired_old]
        for child in item.node.children:
            for j, cand in enumerate(remaining):
                if cand.kind is child.kind and cand.tree_hash == child.tree_hash:
                    self._pair_subtree(self.wrap[id(child)], cand)
                    del remaining[j]
                    break

    def stage_exact(self) -> None:
        """B: same kind and own hash, content nodes: unique texts, parents, then the rest.

        Spec: R54 (E71)
        """
        olds_by_key: dict[tuple[Kind, str], list[StoredNode]] = defaultdict(list)
        for old in self.olds:
            if old.kind not in STRUCTURAL and old.id not in self.paired_old:
                olds_by_key[(old.kind, old.own_hash)].append(old)
        news_by_key: dict[tuple[Kind, str], list[_New]] = defaultdict(list)
        for item in self.news:
            if self._free(item) and item.node.kind not in STRUCTURAL:
                news_by_key[(item.node.kind, item.node.own_hash)].append(item)
        for key, items in news_by_key.items():
            olds = olds_by_key.get(key, [])
            if len(items) == 1 and len(olds) == 1:
                self._pair(items[0], olds[0])
        self.stage_structural(unanimous=True)  # R54: the parents of the repeated texts
        # R54: ranks among the copies still free: a copy paired already (in a
        # subtree, or as a unique text) does not shift the others
        free_olds = [o for o in self.olds if o.kind not in STRUCTURAL and o.id not in self.paired_old]
        free_news = [i for i in self.news if self._free(i) and i.node.kind not in STRUCTURAL]
        old_ord = self._ordinals([((o.kind, o.own_hash), o.file, id(o)) for o in free_olds])
        new_ord = self._ordinals([((i.node.kind, i.node.own_hash), i.file, id(i)) for i in free_news])
        pairs: list[tuple[tuple[object, ...], _New, StoredNode]] = []
        for key, items in news_by_key.items():
            for item in items:
                if not self._free(item):
                    continue
                for old in olds_by_key.get(key, []):
                    if old.id not in self.paired_old:
                        order = abs(old_ord[id(old)] - new_ord[id(item)])
                        pairs.append(((self._rank_key(item, old, order), item.rank), item, old))
        pairs.sort(key=lambda p: p[0])
        for _, item, old in pairs:
            if self._free(item) and old.id not in self.paired_old:
                self._pair(item, old)

    def stage_similar(self) -> None:
        """C: similar own text, same kind, content nodes, best pair first.

        The pairs are taken in the order of their score (ratio, plus
        `SAME_FILE_BONUS` in the same file), then position, as if every
        pair were scored and sorted; but scores are computed lazily, best
        upper bound first (`_SimilarPairs`), so that a change of wording
        across the whole corpus does not compare every node with every
        other one.

        Note: D27c

        Spec: R55 (E69, E72)
        """
        news = [i for i in self.news if self._free(i) and i.node.kind not in STRUCTURAL]
        olds = [o for o in self.olds if o.id not in self.paired_old and o.kind not in STRUCTURAL]
        pairs = _SimilarPairs(
            [(i.node.kind, _comparable(_text(i.node.own_text)), i.prefix) for i in news],
            [(o.kind, _comparable(o.own_text), self._old_prefix(o)) for o in olds],
        )
        for n, o, ratio in pairs.best_first(
            # R55: ties: byte distance in the same file, then the new node, then the old one (E89)
            lambda n, o: (
                abs(olds[o].start - news[n].node.start) if self._old_prefix(olds[o]) == news[n].prefix else 1 << 62,
                news[n].rank,
                self.old_rank[olds[o].id],
            )
        ):
            item, old = news[n], olds[o]
            if self._free(item) and old.id not in self.paired_old:
                self._pair(item, old)
                self.similarity[id(item.node)] = round(ratio, 4)  # R55: rounded for the report only
                pairs.taken(n, o)

    def stage_structural(self, unanimous: bool = False) -> None:
        """D: structural containers by their paired children, bottom-up.

        `unanimous`: pair a container only when all its paired children
        come from one old container (used early, in stage B).

        A section is first paired by its heading: the old section whose
        first child is the old node of the new section's heading. So a
        subsection added inside a section, whose children all come from
        that section, does not take the section's ID.

        Spec: R5, R54, R56 (E70, E87)
        """
        for item in self.news:
            if not self._free(item) or item.node.kind is not Kind.SECTION or not item.node.children:
                continue
            heading = self.pair_of_new.get(id(item.node.children[0]))
            if heading is None or heading.parent is None or heading.parent in self.paired_old:
                continue
            section = self.old_by_id.get(heading.parent)
            kids = self.old_children.get(heading.parent, [])
            if section is not None and section.kind is Kind.SECTION and kids and kids[0].id == heading.id:
                self._pair(item, section)
        for item in sorted(self.news, key=lambda i: (-i.depth, i.rank)):
            if not self._free(item) or item.node.kind not in STRUCTURAL:
                continue
            votes: Counter[str] = Counter()
            for child in item.node.children:
                old_child = self.pair_of_new.get(id(child))
                if old_child is not None and old_child.parent is not None:
                    votes[old_child.parent] += 1
            options = [
                self.old_by_id[pid]
                for pid in votes
                if pid in self.old_by_id
                and pid not in self.paired_old
                and self.old_by_id[pid].kind is item.node.kind
            ]
            if not options or (unanimous and len(votes) != 1):
                continue

            # R54, R56: most votes, then same own hash, then the ranking of stages A and B with byte distance
            def key(o: StoredNode, item: _New = item) -> tuple[int, int, tuple[int, int, int, int]]:
                same_hash = 0 if o.own_hash == item.node.own_hash else 1
                return (-votes[o.id], same_hash, self._rank_key(item, o))

            self._pair(item, min(options, key=key))
        if not unanimous:
            self._childless()

    def _childless(self) -> None:
        """Structural containers without children ("> ***", ">"): by own hash, best pair first.

        No child can vote for them, so their text is all they have, as for
        a content node in stage B: same kind and own hash, same file, same
        parent, neighbours, closest in order.

        Spec: R56 (E83)
        """
        olds_by_key: dict[tuple[Kind, str], list[StoredNode]] = defaultdict(list)
        # R56: only the free ones, a copy paired already does not shift the others' ranks
        childless_olds = [
            o for o in self.olds if o.kind in STRUCTURAL and not self.old_children[o.id] and o.id not in self.paired_old
        ]
        childless_news = [i for i in self.news if i.node.kind in STRUCTURAL and not i.node.children and self._free(i)]
        old_ord = self._ordinals([((o.kind, o.own_hash), o.file, id(o)) for o in childless_olds])
        new_ord = self._ordinals([((i.node.kind, i.node.own_hash), i.file, id(i)) for i in childless_news])
        for old in childless_olds:
            if old.id not in self.paired_old:
                olds_by_key[(old.kind, old.own_hash)].append(old)
        pairs: list[tuple[tuple[object, ...], _New, StoredNode]] = []
        for item in childless_news:
            if self._free(item):
                for old in olds_by_key.get((item.node.kind, item.node.own_hash), []):
                    order = abs(old_ord[id(old)] - new_ord[id(item)])
                    pairs.append(((self._rank_key(item, old, order), item.rank), item, old))
        pairs.sort(key=lambda p: p[0])
        for _, item, old in pairs:
            if self._free(item) and old.id not in self.paired_old:
                self._pair(item, old)

    # -- results

    def number(self) -> None:
        """Set IDs: paired ones kept, files by prefix, new ones numbered.

        Spec: R53, R57 (E76)
        """
        top: dict[str, int] = defaultdict(int)
        for n in self.previous.nodes:  # R57: retired IDs included, numbers are never reused
            prefix = _prefix_of(n.id)
            top[prefix] = max(top[prefix], _number_of(n.id))
        for item in self.news:
            if item.node.kind is Kind.FILE:
                item.node.id = item.prefix
            elif id(item.node) in self.pair_of_new:
                item.node.id = self.pair_of_new[id(item.node)].id
            else:
                top[item.prefix] += 1
                item.node.id = f"{item.prefix}-{top[item.prefix]}"

    def changes(self) -> list[Change]:
        """One change record per active ID, then one per retired ID.

        Spec: R59, R63
        """
        out: list[Change] = []
        for item in self.news:
            node = item.node
            assert node.id is not None
            parent_id = item.parent.node.id if item.parent else None
            old = self.old_by_id.get(node.id) if node.kind is Kind.FILE else self.pair_of_new.get(id(node))
            if old is None:
                out.append(
                    Change(
                        id=node.id,
                        status=Status.NEW,
                        kind=node.kind,
                        file=item.file,
                        new_parent=parent_id,
                        new_text=_text(node.own_text),
                        new_tree_hash=node.tree_hash,
                    )
                )
                continue
            if node.kind is Kind.FILE:  # R59: a file node moved when its path changed (E78)
                moved = old.file != item.file
            else:  # R59: another file means another prefix
                moved = old.parent != parent_id or self._old_prefix(old) != item.prefix
            # R59: changed children: new ones whose tree hash differs or that came in, then the ones that left (E77, E85)
            old_kids = self.old_children.get(old.id, [])
            old_tree = {c.id: c.tree_hash for c in old_kids}
            new_ids = [c.id for c in node.children if c.id]
            changed = [cid for cid, c in zip(new_ids, node.children) if old_tree.get(cid) != c.tree_hash]
            changed += [c.id for c in old_kids if c.id not in set(new_ids)]
            reordered = node.ordered and [i for i in new_ids if i in old_tree] != [  # R59: a numbered list reordered (E75)
                c.id for c in old_kids if c.id in set(new_ids)
            ]
            # R59: the statuses compare own and tree hashes
            if node.own_hash != old.own_hash and not _same_information(
                node.kind, old.own_text, _text(node.own_text)
            ):
                status = Status.EDITED
            elif node.tree_hash != old.tree_hash:
                status = Status.CHILD_CHANGED
            elif moved:
                status = Status.MOVED
            else:
                status = Status.UNCHANGED
            out.append(
                Change(
                    id=node.id,
                    status=status,
                    kind=node.kind,
                    file=item.file,
                    old_file=old.file,
                    old_parent=old.parent,
                    new_parent=parent_id,
                    old_text=old.own_text,
                    new_text=_text(node.own_text),
                    old_tree_hash=old.tree_hash,
                    new_tree_hash=node.tree_hash,
                    moved=moved,
                    reordered=bool(reordered),
                    changed_children=changed,
                    similarity=self.similarity.get(id(node)),
                    old=old,
                )
            )
        # R53, R58: old nodes left unpaired are retired, and file nodes whose prefix no current file holds
        current_files = {item.node.id for item in self.news if item.node.kind is Kind.FILE}
        for old in self.previous.active():
            if old.kind is Kind.FILE:
                if old.id in current_files:
                    continue
            elif old.id in self.paired_old:
                continue
            out.append(
                Change(
                    id=old.id,
                    status=Status.RETIRED,
                    kind=old.kind,
                    file=old.file,
                    old_file=old.file,
                    old_parent=old.parent,
                    old_text=old.own_text,
                    old_tree_hash=old.tree_hash,
                    last_text=self._full_text(old).decode("utf-8", "replace"),
                    old=old,
                )
            )
        return out

    def _full_text(self, old: StoredNode) -> bytes:
        """The whole text of a previous node: its own text with its children's put back.

        The own text is the node's span with its children's spans cut out,
        so each child's text goes back where its span starts.

        Spec: R31, R63 (E85)
        """
        own = old.own_text.encode("utf-8")
        parts: list[bytes] = []
        pos, taken = old.start, 0
        for child in sorted(self.old_children.get(old.id, []), key=lambda c: c.start):
            gap = max(child.start - pos, 0)
            parts += [own[taken : taken + gap], self._full_text(child)]
            taken += gap
            pos = max(pos, child.end)
        parts.append(own[taken:])
        return b"".join(parts)


def assign_ids(
    new_trees: dict[str, TreeNode], previous_store: Store, prefixes: dict[str, str]
) -> list[Change]:
    """Set `id` on every node of `new_trees` and return the change records.

    Args:
        new_trees: path -> root (kind FILE) of each spec file, with
            own text and both hashes set (tree.py).
        previous_store: the previous JSONL; `Store()` on the first run.
        prefixes: path -> prefix of every path in `new_trees`
            (`prefixes.assign_prefixes`).

    Returns:
        One `Change` per active ID (pre-order, files by path), then one
        per newly retired ID (the report's order). Matching is described
        in the module docstring.

    Spec: R23, R53, R63
    """
    missing = set(new_trees) - set(prefixes)
    if missing:
        raise ValueError(f"no prefix for {sorted(missing)}")
    for path, root in new_trees.items():
        if root.kind is not Kind.FILE:
            raise ValueError(f"root of {path} is {root.kind.value}, not file")
    matcher = _Matcher(new_trees, previous_store, prefixes)
    matcher.stage_subtrees()
    matcher.stage_exact()
    matcher.stage_similar()
    matcher.stage_structural()
    matcher.number()
    return matcher.changes()


# ---------------------------------------------------------------- new store


def build_store(
    new_trees: dict[str, TreeNode],
    prefixes: dict[str, str],
    previous: Store,
    changes: list[Change],
    *,
    specs_commit: str = "",
    generator_version: str = "",
    sha256s: dict[str, str] | None = None,
    insertions: dict[str, list[Insertion]] | None = None,
) -> Store:
    """The new store: current nodes active, every other ID retired.

    IDs must have been set by `assign_ids`, which produced `changes`.
    Nodes retired earlier stay retired, with no `changed_since` (it
    describes this step only); nodes retired now keep their last
    text and have the previous commit as `changed_since`. Prefixes of
    files that vanished join the retired prefixes.

    Spec: R58, R60, R61 (E84)
    """
    sha256s = sha256s or {}
    insertions = insertions or {}
    by_id = {c.id: c for c in changes}
    store = Store(specs_commit=specs_commit, generator_version=generator_version)
    for path in sorted(new_trees):
        store.files[path] = StoredFile(path, prefixes[path], sha256s.get(path, ""), list(insertions.get(path, [])))
    current_prefixes = set(prefixes.values())
    store.retired_prefix_list = sorted(
        (previous.retired_prefixes() | {f.prefix for f in previous.files.values()}) - current_prefixes
    )
    for path in sorted(new_trees):
        for node, parent in _walk(new_trees[path]):
            if node.id is None:
                raise ValueError(f"node without ID in {path} at {node.start}")
            change = by_id.get(node.id)
            edited = change is not None and change.status is Status.EDITED
            tree_changed = change is not None and change.old is not None and change.old.tree_hash != node.tree_hash
            store.nodes.append(
                StoredNode(
                    id=node.id,
                    file=path,
                    kind=node.kind,
                    parent=parent.id if parent else None,
                    start=node.start,
                    end=node.end,
                    own_text=_text(node.own_text),
                    own_hash=node.own_hash,
                    tree_hash=node.tree_hash,
                    to_review=edited,  # R60: to review when edited in this step
                    changed_since=previous.specs_commit if tree_changed else None,  # R60: its tree changed in this step
                )
            )
    active_ids = {n.id for n in store.nodes}
    for old in previous.nodes:
        if old.id in active_ids:
            continue
        store.nodes.append(
            StoredNode(
                id=old.id,
                file=old.file,
                kind=old.kind,
                parent=old.parent,
                start=old.start,
                end=old.end,
                own_text=old.own_text,
                own_hash=old.own_hash,
                tree_hash=old.tree_hash,
                status="retired",
                to_review=False,
                # R60: retired in this step, changed since the previous version; retired
                # earlier, nothing changed in this step (nothing carried over)
                changed_since=None if old.status == "retired" else previous.specs_commit,
            )
        )
    return store


# ---------------------------------------------------------------- reports


def report_json(changes: list[Change], *, include_unchanged: bool = False) -> str:
    """The change report as JSON Lines, one record per ID not `unchanged`.

    Spec: R63
    """
    return "".join(
        _dumps(c.to_json()) + "\n"
        for c in changes
        if include_unchanged or c.status is not Status.UNCHANGED
    )


def _fence(text: str) -> str:
    """`text` in a `text` fence of three backticks, or one more than its longest run.

    Spec: R63
    """
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    ticks = "`" * max(3, longest + 1)
    return f"{ticks}text\n{text}\n{ticks}"


_SECTION_ORDER = [  # R63: the sections of the report, in order
    (Status.EDITED, "Edited (to review)"),
    (Status.CHILD_CHANGED, "Changed below"),
    (Status.RETIRED, "Retired"),
    (Status.NEW, "New"),
    (Status.MOVED, "Moved"),
]


def report_markdown(changes: list[Change]) -> str:
    """The change report for people and agents, by ID.

    Edited IDs with old and new text, containers whose children changed
    with the IDs of those children (or, when none did, their own text old
    and new: a list that turned loose), retired IDs with their whole last
    text, children included, new IDs with their text, and moved IDs with
    where they were and are.

    Spec: R21, R63
    """
    counts = Counter(c.status for c in changes)
    lines = ["# Changes", ""]
    lines.append(", ".join(f"{s.value}: {counts.get(s, 0)}" for s in Status))  # R63: the counts, in the statuses' order
    for status, title in _SECTION_ORDER:
        items = [c for c in changes if c.status is status]
        if not items:
            continue
        lines += ["", f"## {title}", ""]
        for c in items:
            where = c.file if c.old_file in (None, c.file) else f"{c.old_file} -> {c.file}"
            lines.append(f"### {c.id} ({c.kind.value}, {where})")
            lines.append("")
            if c.moved:
                # R63: a file has no parent, it moves from one path to another (E78, E82)
                if c.kind is Kind.FILE:
                    where_from = f"file {c.old_file} -> {c.file}"
                else:
                    where_from = f"parent {c.old_parent} -> {c.new_parent}"
                if status is Status.MOVED:
                    lines += [where_from[0].upper() + where_from[1:] + ".", ""]
                else:
                    lines += [f"Moved: {where_from}.", ""]
            if c.changed_children:
                lines += ["Children changed: " + ", ".join(c.changed_children) + ".", ""]
            if c.reordered:
                lines += ["Children reordered.", ""]
            if status is Status.CHILD_CHANGED and not c.changed_children and not c.reordered:  # R63: own text only (E86)
                lines += [
                    "Own text changed (blank lines, `>` prefixes and the blanks around them, or thematic breaks only):",
                    "",
                    "Old:",
                    "",
                    _fence(c.old_text or ""),
                    "",
                    "New:",
                    "",
                    _fence(c.new_text or ""),
                    "",
                ]
            if status is Status.EDITED:
                if c.similarity is not None:  # R63: only a node paired by similar text (E88)
                    lines += [f"Similarity {c.similarity}.", ""]
                lines += ["Old:", "", _fence(c.old_text or ""), "", "New:", "", _fence(c.new_text or ""), ""]
            elif status is Status.RETIRED:  # R63: its whole last text (E85)
                lines += ["Last text:", "", _fence(c.last_text if c.last_text is not None else c.old_text or ""), ""]
            elif status is Status.NEW:  # R63: its own text only
                lines += [_fence(c.new_text or ""), ""]
    return "\n".join(lines).rstrip("\n") + "\n"
