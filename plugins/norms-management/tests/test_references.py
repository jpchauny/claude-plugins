"""References to nodes: citing a node cites everything below it.

A reference is an ID. Layer 3 learns that a cited node changed by its tree
hash, so the tree hash of a node must cover every node below it, at any
depth, and nothing beside it. An agent finds a cited ID in the annotated
copy, so the frame of a node must hold the markers of every node below it,
and no other node's.

Spec: R4, R31
"""

from __future__ import annotations

import re

from norms_generator.annotate import annotate_text, number_first_run
from norms_generator.model import Kind, TreeNode
from norms_generator.tree import build_tree, walk

SOURCE = (
    "# A\n\nintro\n\n## B\n\n- one\n  - deep\n\n    > quoted\n- two\n\n"
    "| h |\n|---|\n| c |\n\n```\ncode\n```\n\n# C\n\nother\n"
)


def _by_text(root: TreeNode, source: bytes) -> dict[tuple[Kind, bytes], TreeNode]:
    """Each node by its kind and the first line of its span: a list and its first item share that line."""
    out: dict[tuple[Kind, bytes], TreeNode] = {}
    for node in walk(root):
        out.setdefault((node.kind, source[node.start : node.end].split(b"\n")[0]), node)
    return out


def test_a_tree_hash_covers_every_node_below_it_and_nothing_beside_it() -> None:
    """An edit deep in a section changes the tree hash of every node above it, not their own hashes.

    Spec: R4, R31
    """
    old_src = SOURCE.encode()
    new_src = SOURCE.replace("> quoted", "> quoted again").encode()
    old, new = _by_text(build_tree(old_src), old_src), _by_text(build_tree(new_src), new_src)
    above = [  # the file, the section, the subsection, the list, its item, the item below it
        (Kind.FILE, b"# A"),
        (Kind.SECTION, b"# A"),
        (Kind.SECTION, b"## B"),
        (Kind.LIST, b"- one"),
        (Kind.ITEM, b"- one"),
        (Kind.ITEM, b"- deep"),
    ]
    for key in above:
        assert old[key].tree_hash != new[key].tree_hash, key
        assert old[key].own_hash == new[key].own_hash, key
    beside = [
        (Kind.PARAGRAPH, b"intro"),
        (Kind.HEADING, b"# A"),
        (Kind.SECTION, b"# C"),
        (Kind.PARAGRAPH, b"other"),
        (Kind.ITEM, b"- two"),
        (Kind.TABLE, b"| h |"),
        (Kind.CODE_BLOCK, b"```"),
    ]
    for key in beside:
        assert old[key].tree_hash == new[key].tree_hash, key


def test_the_frame_of_a_node_holds_the_markers_of_its_whole_subtree_and_no_others() -> None:
    """Between `⟬ID begin⟭` and `⟬ID end⟭` are the markers of every node below it, and of no other node.

    Spec: R4, R24, R29
    """
    source = SOURCE.encode()
    out, _ = annotate_text(source, "TYP")
    text = out.decode()
    root = build_tree(source)
    number_first_run(root, "TYP")
    assert text.startswith("⟬TYP⟭")  # the file marker: the whole file is below the file
    framed = 0
    for node in walk(root):
        if node is root or f"⟬{node.id} begin⟭" not in text:
            continue
        framed += 1
        inside = text[text.index(f"⟬{node.id} begin⟭") + 1 : text.index(f"⟬{node.id} end⟭")]
        found = set(re.findall(r"⟬([A-Z]+-[0-9]+)", inside)) - {node.id}
        below = {d.id for d in walk(node)} - {node.id}
        assert found == below, node.id
    assert framed >= 4  # the sections, the list, the table and the code block at least
