"""Tests of verify.check_file(), the per-file checks of verify.

A file is annotated as `norms-gen build` does it, stored as a first run,
then checked; each test spoils one thing and expects check_file() to
report it.

Spec: R23, R48, R52, R64
"""

from __future__ import annotations

import hashlib

from norms_generator.annotate import annotate
from norms_generator.model import Insertion
from norms_generator.prefixes import assign_prefixes
from norms_generator.store import StoredFile, StoredNode, Store, assign_ids, build_store
from norms_generator.tree import build_tree
from norms_generator.verify import check_file

PATH = "specs/t.md"


def stored(source: bytes) -> tuple[bytes, StoredFile, list[StoredNode]]:
    """Annotated bytes, file line and active nodes of `source` on a first run."""
    trees = {PATH: build_tree(source)}
    prefixes = assign_prefixes([PATH], {}, set(), {})
    changes = assign_ids(trees, Store(), prefixes)
    annotated, insertions = annotate(source, trees[PATH])
    store = build_store(
        trees,
        prefixes,
        Store(),
        changes,
        sha256s={PATH: hashlib.sha256(source).hexdigest()},
        insertions={PATH: insertions},
    )
    return annotated, store.files[PATH], store.active()


def test_a_sound_file_has_no_problem() -> None:
    """A file annotated by build, an unclosed fence included, passes every check.

    Spec: R48, R64
    """
    source = b"# T\n\nAlpha.\n\n```\ncode\n"  # an unclosed fence too
    annotated, file, nodes = stored(source)
    assert check_file(PATH, source, annotated, file, nodes) == []


def test_swapped_ids_are_found() -> None:
    """Each ID must sit at its own node, not just appear once: annotating again with the stored IDs must give the same bytes.

    Spec: R64
    """
    source = b"Alpha.\n\nBeta.\n"
    annotated, file, nodes = stored(source)
    one, two = (f"⟬{n.id}⟭".encode() for n in nodes[1:3])

    def swap(data: bytes) -> bytes:
        return data.replace(one, b"\0").replace(two, one).replace(b"\0", two)

    insertions = [Insertion(i.offset, swap(i.text)) for i in file.insertions]
    spoiled = StoredFile(file.path, file.prefix, file.sha256, insertions)
    problems = check_file(PATH, source, swap(annotated), spoiled, nodes)
    assert any("annotated with the stored IDs" in p for p in problems)


def test_a_file_of_lone_cr_line_endings_is_sound() -> None:
    """A file whose only line endings are lone CR passes every check.

    Spec: R52, R64
    """
    source = b"a\rb\r\rc\r"
    annotated, file, nodes = stored(source)
    assert check_file(PATH, source, annotated, file, nodes) == []


# --- regressions of the review (fix2) --------------------------------------


def test_unclosed_blocks_are_sound_with_only_their_markers_e61() -> None:
    """Unclosed blocks are framed with nothing else inserted, and pass every check.

    Spec: R48, R64, U1 (E61, E62, E63)
    """
    for source in (b"<!-- a\n\nb\n", b"- ```\n  x\n\n- b\n", b"# H\n\n```\nx\n"):
        annotated, file, nodes = stored(source)
        assert check_file(PATH, source, annotated, file, nodes) == []
        assert all(b"```" not in i.text and b"-->" not in i.text for i in file.insertions)


def test_a_closing_fence_inserted_is_a_problem_r48() -> None:
    """An inserted closing fence is not a marker byte, and verify reports it.

    Spec: R48, R64, U1
    """
    source = b"```\nx\n"
    annotated, file, nodes = stored(source)
    spoiled = [Insertion(i.offset, b"```\n" + i.text if b"end" in i.text else i.text) for i in file.insertions]
    text = annotate_bytes(source, spoiled)
    problems = check_file(PATH, source, text, StoredFile(file.path, file.prefix, file.sha256, spoiled), nodes)
    assert any("insertion" in p for p in problems)


def test_control_characters_are_checked_not_crashed() -> None:
    """A file holding ESC and form feed is checked, not crashed on.

    Note: D30

    Spec: R64
    """
    source = b'# Colors\n\n```\nprintf "\x1b[31mred\x1b[0m"\n```\n\nesc \x1b and \x0c\n'
    annotated, file, nodes = stored(source)
    assert check_file(PATH, source, annotated, file, nodes) == []


def annotate_bytes(source: bytes, insertions: list[Insertion]) -> bytes:
    out, pos = [], 0
    for ins in sorted(insertions, key=lambda i: i.offset):
        out += [source[pos : ins.offset], ins.text]
        pos = ins.offset
    return b"".join(out + [source[pos:]])
