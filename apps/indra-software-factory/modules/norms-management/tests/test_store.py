"""Tests of store.py.

Trees are made by hand; hashes are the spec's two hashes (own hash, then
the children's tree hashes, in order for a numbered list and sorted
otherwise).

Spec: R7, R11, R12, R13, R15, R31, R53, R54, R55, R56, R57, R58, R59, R60, R61, R62, R63
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from norms_generator.model import Insertion, Kind, TreeNode
from norms_generator.prefixes import assign_prefixes
from norms_generator.store import (
    Status,
    Store,
    assign_ids,
    build_store,
    detect_renames,
    read_store,
    report_json,
    report_markdown,
    write_store,
)

K = Kind


def n(kind: Kind, text: str = "", *children: TreeNode, ordered: bool = False) -> TreeNode:
    return TreeNode(kind=kind, start=0, end=0, children=list(children), ordered=ordered, own_text=text.encode())


def finish(root: TreeNode) -> TreeNode:
    """Set positions (pre-order, cumulative) and both hashes.

    Spec: R31
    """
    offset = 0

    def place(node: TreeNode) -> None:
        nonlocal offset
        node.start = offset
        offset += len(node.own_text) + 1
        for child in node.children:
            place(child)
        node.end = offset

    def hashes(node: TreeNode) -> str:
        kids = [hashes(c) for c in node.children]
        if not node.ordered:
            kids.sort()
        node.own_hash = hashlib.sha256(node.own_text).hexdigest()
        node.tree_hash = hashlib.sha256((node.own_hash + "".join(kids)).encode()).hexdigest()
        return node.tree_hash

    place(root)
    hashes(root)
    return root


def file(*children: TreeNode) -> TreeNode:
    return finish(n(K.FILE, "\n", *children))


def types_tree(numbers_text: str = "Numbers are always signed.") -> TreeNode:
    """The tree of the example of a types file.

    Spec: (E2)
    """
    return file(
        n(
            K.SECTION,
            "\n\n",
            n(K.HEADING, "# Types"),
            n(K.PARAGRAPH, "Clean has a small set of built-in types."),
            n(
                K.SECTION,
                "\n\n",
                n(K.HEADING, "## Numbers ##"),
                n(K.PARAGRAPH, numbers_text),
                n(
                    K.SECTION,
                    "\n\n",
                    n(K.HEADING, "### Overflow"),
                    n(K.PARAGRAPH, "Integers wrap on overflow."),
                ),
            ),
            n(K.SECTION, "\n\n", n(K.HEADING, "## Strings"), n(K.PARAGRAPH, "Strings are UTF-8.")),
        )
    )


TYP = "specs/language/types/type-system.md"
SYN = "specs/language/syntax.md"


def ids(root: TreeNode) -> list[str | None]:
    out: list[str | None] = []

    def walk(node: TreeNode) -> None:
        out.append(node.id)
        for c in node.children:
            walk(c)

    walk(root)
    return out


def texts(root: TreeNode) -> dict[str, str]:
    out: dict[str, str] = {}

    def walk(node: TreeNode) -> None:
        assert node.id
        out[node.own_text.decode()] = node.id
        for c in node.children:
            walk(c)

    walk(root)
    return out


def run(trees: dict[str, TreeNode], previous: Store, commit: str) -> tuple[Store, list]:
    renames = detect_renames(trees, previous)
    prefixes = assign_prefixes(sorted(trees), previous.prefixes(), previous.retired_prefixes(), renames)
    changes = assign_ids(trees, previous, prefixes)
    store = build_store(trees, prefixes, previous, changes, foundation_commit=commit, generator_version="0.1.0")
    return store, changes


def by_id(changes: list) -> dict:
    return {c.id: c for c in changes}


# ------------------------------------------------------------------ tests


def test_first_run_numbers_in_preorder() -> None:
    """On a first run every node is new and numbered in pre-order.

    Spec: R9, R53 (E2)
    """
    tree = types_tree()
    store, changes = run({TYP: tree}, Store(), "c1")
    assert ids(tree) == ["TYP"] + [f"TYP-{i}" for i in range(1, 13)]
    assert {c.status for c in changes} == {Status.NEW}
    assert [nd.id for nd in store.nodes] == ids(tree)


def test_rerun_identical_keeps_ids_and_reports_nothing(tmp_path: Path) -> None:
    """A rerun of the same tree keeps every ID, reports nothing, and writes the same JSONL.

    Spec: R60, R61, R62
    """
    store1, _ = run({TYP: types_tree(), SYN: file(n(K.PARAGRAPH, "Blocks use tabs."))}, Store(), "c1")
    path = tmp_path / "data" / "tree.jsonl"
    write_store(path, store1)
    previous = read_store(path)
    trees = {TYP: types_tree(), SYN: file(n(K.PARAGRAPH, "Blocks use tabs."))}
    store2, changes = run(trees, previous, "c1")
    assert ids(trees[TYP]) == ["TYP"] + [f"TYP-{i}" for i in range(1, 13)]
    assert {c.status for c in changes} == {Status.UNCHANGED}
    assert report_json(changes) == ""
    path2 = tmp_path / "again.jsonl"
    write_store(path2, store2)
    assert path.read_bytes() == path2.read_bytes()


def test_jsonl_format(tmp_path: Path) -> None:
    """The JSONL's lines, keys and fields.

    Spec: R61
    """
    tree = file(n(K.PARAGRAPH, "Números ⟬ firmados."))
    prefixes = {TYP: "TYP"}
    changes = assign_ids({TYP: tree}, Store(), prefixes)
    store = build_store(
        {TYP: tree},
        prefixes,
        Store(),
        changes,
        foundation_commit="abc",
        generator_version="0.1.0",
        sha256s={TYP: "f" * 64},
        insertions={TYP: [Insertion(0, "⟬TYP⟭\n\n".encode())]},
    )
    path = tmp_path / "tree.jsonl"
    write_store(path, store)
    raw = path.read_text(encoding="utf-8")
    assert "Números" in raw and "⟬TYP⟭" in raw  # ensure_ascii=False
    lines = [json.loads(line) for line in raw.splitlines()]
    assert [line["type"] for line in lines] == ["meta", "file", "node", "node"]
    for line, text in zip(lines, raw.splitlines()):
        assert list(json.loads(text)) == sorted(json.loads(text))
    assert lines[0]["foundation_commit"] == "abc"
    assert lines[1]["insertions"] == [[0, "⟬TYP⟭\n\n"]]
    node = lines[3]
    assert node["id"] == "TYP-1" and node["parent"] == "TYP" and node["status"] == "active"
    assert node["own_text"] == "Números ⟬ firmados."
    assert node["to_review"] is False and node["changed_since"] is None
    back = read_store(path)
    assert back.files[TYP].insertions == [Insertion(0, "⟬TYP⟭\n\n".encode())]
    assert back.nodes == store.nodes


def test_edited_node_keeps_id_and_is_to_review() -> None:
    """An edited node keeps its ID, is edited and to review; its containers are child_changed.

    Spec: R15, R55, R59, R60, R63 (E69)
    """
    store1, _ = run({TYP: types_tree()}, Store(), "c1")
    tree = types_tree("Numbers are always signed integers.")
    store2, changes = run({TYP: tree}, store1, "c2")
    assert ids(tree) == ["TYP"] + [f"TYP-{i}" for i in range(1, 13)]
    c = by_id(changes)
    assert c["TYP-6"].status is Status.EDITED
    assert c["TYP-6"].old_text == "Numbers are always signed."
    assert c["TYP-6"].new_text == "Numbers are always signed integers."
    assert c["TYP-6"].similarity is not None and c["TYP-6"].similarity >= 0.6
    assert c["TYP-4"].status is Status.CHILD_CHANGED and c["TYP-4"].changed_children == ["TYP-6"]
    assert c["TYP-1"].status is Status.CHILD_CHANGED and c["TYP-1"].changed_children == ["TYP-4"]
    assert c["TYP"].status is Status.CHILD_CHANGED
    assert c["TYP-12"].status is Status.UNCHANGED
    node = {nd.id: nd for nd in store2.nodes}
    assert node["TYP-6"].to_review and node["TYP-6"].changed_since == "c1"
    assert not node["TYP-4"].to_review and node["TYP-4"].changed_since == "c1"
    assert not node["TYP-12"].to_review and node["TYP-12"].changed_since is None
    md = report_markdown(changes)
    assert "TYP-6" in md and "Numbers are always signed integers." in md
    records = [json.loads(line) for line in report_json(changes).splitlines()]
    assert {r["id"] for r in records} == {"TYP", "TYP-1", "TYP-4", "TYP-6"}


def test_unrelated_text_is_new_and_old_retired() -> None:
    """Text below the similarity threshold is new, and the old node retired.

    Spec: R55, R57
    """
    store1, _ = run({TYP: types_tree()}, Store(), "c1")
    tree = types_tree("Completely different wording here about bytes.")
    _, changes = run({TYP: tree}, store1, "c2")
    c = by_id(changes)
    assert c["TYP-6"].status is Status.RETIRED
    assert c["TYP-6"].old_text == "Numbers are always signed."
    assert texts(tree)["Completely different wording here about bytes."] == "TYP-13"


def test_move_within_file_keeps_id() -> None:
    """A paragraph moved to another section keeps its ID and is moved.

    Spec: R7, R54, R59
    """
    store1, _ = run({TYP: types_tree()}, Store(), "c1")
    # "Integers wrap on overflow." moves from Overflow (TYP-7) to Strings (TYP-10).
    tree = file(
        n(
            K.SECTION,
            "\n\n",
            n(K.HEADING, "# Types"),
            n(K.PARAGRAPH, "Clean has a small set of built-in types."),
            n(
                K.SECTION,
                "\n\n",
                n(K.HEADING, "## Numbers ##"),
                n(K.PARAGRAPH, "Numbers are always signed."),
                n(K.SECTION, "\n\n", n(K.HEADING, "### Overflow")),
            ),
            n(
                K.SECTION,
                "\n\n",
                n(K.HEADING, "## Strings"),
                n(K.PARAGRAPH, "Strings are UTF-8."),
                n(K.PARAGRAPH, "Integers wrap on overflow."),
            ),
        )
    )
    _, changes = run({TYP: tree}, store1, "c2")
    t = texts(tree)
    assert t["Integers wrap on overflow."] == "TYP-9"
    assert t["### Overflow"] == "TYP-8"
    assert t["## Strings"] == "TYP-11"
    c = by_id(changes)
    assert c["TYP-9"].status is Status.MOVED
    assert (c["TYP-9"].old_parent, c["TYP-9"].new_parent) == ("TYP-7", "TYP-10")
    assert c["TYP-10"].status is Status.CHILD_CHANGED and "TYP-9" in c["TYP-10"].changed_children
    assert c["TYP-7"].status is Status.CHILD_CHANGED and "TYP-9" in c["TYP-7"].changed_children
    assert not any(ch.status is Status.NEW or ch.status is Status.RETIRED for ch in changes)


def test_move_to_another_file_keeps_id() -> None:
    """A paragraph moved to another file keeps its ID and its prefix.

    Spec: R11, R54, R59 (E77)
    """
    syn = file(n(K.PARAGRAPH, "Blocks use tabs."))
    store1, _ = run({TYP: types_tree(), SYN: syn}, Store(), "c1")
    assert ids(syn) == ["SYN", "SYN-1"]
    # "Strings are UTF-8." (TYP-12) moves to syntax.md.
    tree = types_tree()
    strings = tree.children[0].children.pop()  # the Strings section
    finish(tree)
    syn2 = file(n(K.PARAGRAPH, "Blocks use tabs."), strings.children[1])
    trees = {TYP: tree, SYN: syn2}
    _, changes = run(trees, store1, "c2")
    assert ids(syn2) == ["SYN", "SYN-1", "TYP-12"]  # R11: its prefix no longer matches
    c = by_id(changes)
    assert c["TYP-12"].status is Status.MOVED and c["TYP-12"].file == SYN and c["TYP-12"].old_file == TYP
    assert c["TYP-10"].status is Status.RETIRED  # the section, left empty
    assert c["TYP-11"].status is Status.RETIRED  # its heading was not moved


def test_bullet_reorder_is_no_change_numbered_reorder_is() -> None:
    """Reordering bullets changes nothing; reordering a numbered list changes its tree hash.

    Spec: R8, R13, R31, R59 (E74, E75)
    """
    def tree(order: list[int], ordered: bool) -> TreeNode:
        items = [n(K.ITEM, f"- item {i}") for i in order]
        return file(n(K.LIST, "", *items, ordered=ordered))

    bullets = tree([1, 2, 3], False)
    numbered = tree([1, 2, 3], True)
    store1, _ = run({TYP: bullets, SYN: numbered}, Store(), "c1")
    bullets2 = tree([3, 1, 2], False)
    numbered2 = tree([3, 1, 2], True)
    assert bullets2.children[0].tree_hash == bullets.children[0].tree_hash
    assert numbered2.children[0].tree_hash != numbered.children[0].tree_hash
    _, changes = run({TYP: bullets2, SYN: numbered2}, store1, "c2")
    c = by_id(changes)
    assert texts(bullets2) == texts(bullets) and texts(numbered2) == texts(numbered)
    assert c["TYP-1"].status is Status.UNCHANGED
    assert c["SYN-1"].status is Status.CHILD_CHANGED and c["SYN-1"].reordered
    assert c["SYN-2"].status is Status.UNCHANGED


def test_retired_number_never_reused(tmp_path: Path) -> None:
    """Retired IDs stay in the JSONL and are never candidates; text that comes back gets new numbers.

    Spec: R57, R61 (E76)
    """
    store1, _ = run({TYP: types_tree()}, Store(), "c1")
    # Remove the Strings section: TYP-10, TYP-11, TYP-12 retire.
    tree = types_tree()
    tree.children[0].children.pop()
    finish(tree)
    store2, changes = run({TYP: tree}, store1, "c2")
    retired = sorted(ch.id for ch in changes if ch.status is Status.RETIRED)
    assert retired == ["TYP-10", "TYP-11", "TYP-12"]
    path = tmp_path / "tree.jsonl"
    write_store(path, store2)
    store2 = read_store(path)
    assert [nd.status for nd in store2.nodes[-3:]] == ["retired"] * 3
    assert store2.nodes[-1].own_text == "Strings are UTF-8."
    # The same text comes back: retired IDs are not candidates; it is new.
    tree3 = types_tree()
    store3, _ = run({TYP: tree3}, store2, "c3")
    t3 = texts(tree3)
    assert t3["## Strings"] == "TYP-14"
    assert t3["Strings are UTF-8."] == "TYP-15"
    assert {nd.id for nd in store3.nodes if nd.status == "retired"} == {"TYP-10", "TYP-11", "TYP-12"}


def test_rename_keeps_prefix_and_ids() -> None:
    """A renamed file keeps its prefix and IDs; only its file node moved.

    Spec: R12, R58, R59 (E78)
    """
    store1, _ = run({TYP: types_tree()}, Store(), "c1")
    new_path = "specs/language/typing.md"
    tree = types_tree()
    renames = detect_renames({new_path: tree}, store1)
    assert renames == {new_path: TYP}
    store2, changes = run({new_path: tree}, store1, "c2")
    assert ids(tree) == ["TYP"] + [f"TYP-{i}" for i in range(1, 13)]
    c = by_id(changes)
    assert c["TYP"].status is Status.MOVED and c["TYP"].old_file == TYP
    assert all(ch.status is Status.UNCHANGED for ch in changes if ch.id != "TYP")
    assert store2.files[new_path].prefix == "TYP"
    assert store2.retired_prefix_list == []


def test_vanished_file_retires_its_prefix() -> None:
    """A vanished file's prefix is retired and never given again.

    Spec: R10, R58
    """
    store1, _ = run({TYP: types_tree(), SYN: file(n(K.PARAGRAPH, "Blocks use tabs."))}, Store(), "c1")
    store2, changes = run({TYP: types_tree()}, store1, "c2")
    assert {ch.id for ch in changes if ch.status is Status.RETIRED} == {"SYN", "SYN-1"}
    assert store2.retired_prefix_list == ["SYN"]
    # A new file named like the vanished one gets another prefix.
    store3, _ = run({TYP: types_tree(), SYN: file(n(K.PARAGRAPH, "Other."))}, store2, "c3")
    assert store3.files[SYN].prefix != "SYN"


def test_duplicate_text_prefers_same_file() -> None:
    """Copies of one text pair in the same file first.

    Spec: R54
    """
    a = file(n(K.PARAGRAPH, "**Example (passes):**"), n(K.PARAGRAPH, "A text."))
    b = file(n(K.PARAGRAPH, "**Example (passes):**"), n(K.PARAGRAPH, "B text."))
    store1, _ = run({TYP: a, SYN: b}, Store(), "c1")
    a2 = file(n(K.PARAGRAPH, "A text."), n(K.PARAGRAPH, "**Example (passes):**"))
    b2 = file(n(K.PARAGRAPH, "B text."), n(K.PARAGRAPH, "**Example (passes):**"))
    _, changes = run({TYP: a2, SYN: b2}, store1, "c2")
    assert ids(a2) == ["TYP", "TYP-2", "TYP-1"]
    assert ids(b2) == ["SYN", "SYN-2", "SYN-1"]
    assert {c.status for c in changes} == {Status.UNCHANGED}


# ------------------------------------------------------------------ regressions of the review (fix1)


def parsed(**files: str) -> dict[str, TreeNode]:
    """Trees of real sources; keyword `a_b` is the path "specs/a/b.md"."""
    from norms_generator.tree import build_tree

    return {f"specs/{name.replace('_', '/')}.md": build_tree(text.encode()) for name, text in files.items()}


def text_ids(trees: dict[str, TreeNode]) -> dict[tuple[str, str], str]:
    """(path, own text) -> ID of every node."""
    out: dict[tuple[str, str], str] = {}
    for path, root in trees.items():
        stack = [root]
        while stack:
            node = stack.pop()
            assert node.id
            out[(path, node.own_text.decode())] = node.id
            stack.extend(node.children)
    return out


def test_read_store_keeps_line_separators_in_text(tmp_path: Path) -> None:
    """U+2028, U+2029 and U+0085 stay unescaped in the JSONL; reading splits on "\\n" only.

    Spec: R61
    """
    trees = parsed(t="Line one still one.\n\nNEL\u0085here  .\n")
    store, _ = run(trees, Store(), "c1")
    path = tmp_path / "tree.jsonl"
    write_store(path, store)
    back = read_store(path)
    assert [n.own_text for n in back.nodes] == [n.own_text for n in store.nodes]


def test_a_child_coming_or_going_is_not_an_edit_of_its_section_e86() -> None:
    """A section whose own text changed only by blank lines is child_changed, not edited.

    Spec: R59 (E86)
    """
    store1, _ = run(parsed(a="# A\n\nalpha one.\n\nbeta two.\n", b="# B\n\ngamma.\n"), Store(), "c1")
    store2, changes = run(parsed(a="# A\n\nbeta two.\n", b="# B\n\ngamma.\n\nalpha one.\n"), store1, "c2")
    sections = [c for c in changes if c.kind is K.SECTION]
    assert {c.status for c in sections} == {Status.CHILD_CHANGED}
    assert not any(n.to_review for n in store2.nodes if n.kind is K.SECTION)


def test_an_edited_paragraph_is_still_an_edit() -> None:
    """A paragraph paired by similar text whose own hash changed is edited.

    Spec: R55, R59
    """
    store1, _ = run(parsed(a="# A\n\nalpha one two three.\n"), Store(), "c1")
    _, changes = run(parsed(a="# A\n\nalpha one two four.\n"), store1, "c2")
    assert [c.status for c in changes if c.kind is K.PARAGRAPH] == [Status.EDITED]


def test_a_copy_does_not_take_the_ids_of_the_original() -> None:
    """A copy elsewhere never takes the ID of an original that did not move.

    Spec: R54 (E71)
    """
    sec = "## Overflow\n\nIntegers wrap on overflow.\n\nUse checked_add when needed.\n"
    v1 = parsed(types="# Types\n\nIntro.\n\n" + sec)
    store1, _ = run(v1, Store(), "c1")
    before = text_ids(v1)
    v2 = parsed(arith=sec, types="# Types\n\nIntro edited.\n\n" + sec)
    _, changes = run(v2, store1, "c2")
    after = text_ids(v2)
    for text in ("## Overflow", "Integers wrap on overflow.", "Use checked_add when needed."):
        assert after[("specs/types.md", text)] == before[("specs/types.md", text)]
        assert after[("specs/arith.md", text)].startswith("ARI-")
    assert not [c for c in changes if c.status is Status.MOVED]


def test_a_copied_paragraph_does_not_take_its_section_away() -> None:
    """A copied paragraph neither takes the original's ID nor moves its section.

    Spec: R54, R56
    """
    v1 = parsed(types="# Types\n\nIntro.\n\nIntegers wrap on overflow.\n")
    store1, _ = run(v1, Store(), "c1")
    v2 = parsed(arith="# Arithmetic\n\nIntegers wrap on overflow.\n", types="# Types\n\nIntro, edited.\n\nIntegers wrap on overflow.\n")
    _, changes = run(v2, store1, "c2")
    assert text_ids(v2)[("specs/types.md", "Integers wrap on overflow.")] == "TYP-4"
    assert by_id(changes)["TYP-1"].file == "specs/types.md"
    assert not [c for c in changes if c.moved]


def test_identical_paragraphs_in_two_sections_keep_their_ids() -> None:
    """Identical paragraphs in two sections keep their IDs by their parent.

    Spec: R54
    """
    def doc(intro: str, floats: str) -> str:
        return (
            "# Types\n\n## Integers\n\n" + intro + "**Example (passes):**\n\nIntegers are signed.\n\n"
            "## Floats\n\n**Example (passes):**\n\n" + floats + "\n"
        )

    v1 = parsed(types=doc("", "Floats are IEEE 754."))
    store1, _ = run(v1, Store(), "c1")
    long = "A long new paragraph about integers, long enough to shift every offset below it.\n\n"
    v2 = parsed(types=doc(long, "Floats are IEEE 754 binary64."))
    _, changes = run(v2, store1, "c2")
    root = v2["specs/types.md"]
    integers, floats = root.children[0].children[1], root.children[0].children[2]
    label = "**Example (passes):**"
    assert [c.id for c in integers.children if c.own_text.decode() == label] == ["TYP-5"]
    assert [c.id for c in floats.children if c.own_text.decode() == label] == ["TYP-9"]
    assert not [c for c in changes if c.moved]


def test_moved_file_keeps_its_prefix_when_a_new_file_takes_its_path_r12() -> None:
    """A file moved away keeps its prefix; the new file at its old path gets another.

    Spec: R12, R58
    """
    body = "# Types\n\nClean has types.\n\n## Numbers\n\nSigned.\n\n## Strings\n\nUTF-8.\n"
    store1, _ = run(parsed(lang_types=body), Store(), "c1")
    v2 = parsed(lang_types="# Types index\n\nSee overview.\n", types_overview=body)
    store2, changes = run(v2, store1, "c2")
    assert store2.files["specs/types/overview.md"].prefix == "TYP"
    assert store2.files["specs/lang/types.md"].prefix != "TYP"
    assert by_id(changes)["TYP"].status is Status.MOVED
    assert "TYP" not in store2.retired_prefix_list


def test_swapped_file_names_keep_their_prefixes_r12() -> None:
    """Two files that swapped names keep their prefixes with their content.

    Spec: R12, R58 (E79)
    """
    alpha, beta = "# Alpha\n\nAlpha one.\n\nAlpha two.\n", "# Beta\n\nBeta one.\n\nBeta two.\n"
    store1, _ = run(parsed(a=alpha, b=beta), Store(), "c1")
    prefix_a, prefix_b = store1.files["specs/a.md"].prefix, store1.files["specs/b.md"].prefix
    store2, _ = run(parsed(a=beta, b=alpha), store1, "c2")
    assert store2.files["specs/a.md"].prefix == prefix_b
    assert store2.files["specs/b.md"].prefix == prefix_a


def test_a_file_edited_in_place_keeps_its_prefix() -> None:
    """A file rewritten in place keeps its prefix.

    Spec: R12, R58
    """
    store1, _ = run(parsed(a="# Clean\n\nClean one.\n\nClean two.\n"), Store(), "c1")
    store2, _ = run(parsed(a="# Cleanlang\n\nCleanlang one.\n\nCleanlang two.\n"), store1, "c2")
    assert store2.files["specs/a.md"].prefix == store1.files["specs/a.md"].prefix


def test_renamed_and_lightly_edited_file_keeps_its_prefix_e78() -> None:
    """A file renamed and lightly edited keeps its prefix.

    Spec: R12, R58 (E78)
    """
    v1 = "# Clean types\n\nClean has a small set of types.\n\nIn Clean, integers are signed.\n\nClean strings are UTF-8.\n"
    store1, _ = run(parsed(types=v1), Store(), "c1")
    v2 = parsed(lang_typesystem=v1.replace("Clean", "Cleanlang"))
    assert detect_renames(v2, store1) == {"specs/lang/typesystem.md": "specs/types.md"}
    store2, _ = run(v2, store1, "c2")
    assert store2.files["specs/lang/typesystem.md"].prefix == store1.files["specs/types.md"].prefix
    assert store2.retired_prefix_list == []


# ------------------------------------------------------------------ regressions of the review (fix2)


def test_a_new_subsection_does_not_take_its_section_id_e70() -> None:
    """A subsection added inside a section never takes the section's ID.

    Spec: R56 (E70)
    """
    v1 = parsed(types="# Types\n\nIntro.\n\nIntegers wrap on overflow.\n\nFloats are IEEE.\n")
    store1, _ = run(v1, Store(), "c1")
    v2 = parsed(types="# Types\n\nIntro.\n\n## Numbers\n\nIntegers wrap on overflow.\n\nFloats are IEEE.\n")
    _, changes = run(v2, store1, "c2")
    section = v2["specs/types.md"].children[0]
    assert section.kind is K.SECTION and section.id == "TYP-1"
    c = by_id(changes)
    assert c["TYP-2"].status is Status.UNCHANGED and c["TYP-3"].status is Status.UNCHANGED
    assert c[section.children[2].id].status is Status.NEW  # the "## Numbers" section


def test_a_heading_only_subsection_that_grows_keeps_its_parent_r56() -> None:
    """A section goes to the old section of its heading, so its parent keeps its ID.

    Spec: R5, R56
    """
    v1 = parsed(types="# Types\n\nIntro.\n\n## Overflow\n\n## Floats\n\nF.\n")
    store1, _ = run(v1, Store(), "c1")
    v2 = parsed(types="# Types\n\nIntro.\n\n## Overflow\n\nIntegers wrap.\n\n## Floats\n\nF.\n")
    _, changes = run(v2, store1, "c2")
    assert v2["specs/types.md"].children[0].id == "TYP-1"
    assert by_id(changes)["TYP-5"].status is Status.UNCHANGED  # "## Floats"


def test_copies_of_one_text_keep_their_ids_in_document_order_e71() -> None:
    """Text inserted above two copies does not swap their IDs.

    Spec: R54 (E71)
    """
    p = "Run the build again before you push."
    v1 = parsed(t=f"# T\n\nIntro.\n\n{p}\n\nMiddle short.\n\n{p}\n\nEnd.\n")
    store1, _ = run(v1, Store(), "c1")
    first, second = [c.id for c in v1["specs/t.md"].children[0].children if c.own_text == p.encode()]
    long = "A brand new paragraph, quite a bit longer than the others, inserted early to shift offsets.\n\n"
    v2 = parsed(t=f"# T\n\nIntro.\n\n{long}{p}\n\nMiddle short.\n\n{p}\n\nEnd.\n")
    _, changes = run(v2, store1, "c2")
    assert [c.id for c in v2["specs/t.md"].children[0].children if c.own_text == p.encode()] == [first, second]
    assert not [c for c in changes if c.moved]


def test_repeated_items_of_a_numbered_list_are_not_reordered_r8() -> None:
    """Repeated items of a numbered list keep their IDs in order, so the list is not reordered.

    Spec: R8, R54, R59
    """
    q = "1. Run the full test suite once more."
    v1 = parsed(steps=f"{q}\n1. Fix.\n{q}\n1. Ship.\n")
    store1, _ = run(v1, Store(), "c1")
    before = [c.id for c in v1["specs/steps.md"].children[0].children]
    v2 = parsed(steps=f"#### Some intro paragraph that is long enough to shift every offset after it.\n\n{q}\n1. Fix.\n{q}\n1. Ship it.\n")
    _, changes = run(v2, store1, "c2")
    lst = v2["specs/steps.md"].children[0].children[1]
    assert [c.id for c in lst.children] == before
    assert not by_id(changes)[lst.id].reordered


def test_an_item_inserted_in_a_numbered_list_renumbers_the_later_ones_u4() -> None:
    """The ordinal is part of an item's own text: the renumbered later items are edited and to review.

    Spec: R8, R59, U4 (E73)
    """
    v1 = parsed(build="1. Parse the file.\n2. Check the types.\n3. Emit WebAssembly.\n")
    store1, _ = run(v1, Store(), "c1")
    first, check, emit = [c.id for c in v1["specs/build.md"].children[0].children]
    v2 = parsed(build="1. Parse the file.\n2. Resolve the names.\n3. Check the types.\n4. Emit WebAssembly.\n")
    _, changes = run(v2, store1, "c2")
    items = v2["specs/build.md"].children[0].children
    assert [items[0].id, items[2].id, items[3].id] == [first, check, emit]
    found = by_id(changes)
    assert found[first].status is Status.UNCHANGED
    assert found[items[1].id].status is Status.NEW
    for ident in (check, emit):
        assert found[ident].status is Status.EDITED
    assert not found[v2["specs/build.md"].children[0].id].reordered


def test_the_copy_that_stayed_keeps_its_id_by_its_neighbours_r11() -> None:
    """The copy that stayed keeps its ID by its neighbours; the one that came from another file moved.

    Spec: R11, R54
    """
    p = "Always run the formatter before committing any change."
    v1 = parsed(a=f"# Alpha\n\nIntro alpha.\n\n{p}\n", b=f"# Beta\n\nX.\n\n{p}\n")
    store1, _ = run(v1, Store(), "c1")
    stayed = text_ids(v1)[("specs/b.md", p)]
    v2 = parsed(a="# Alpha\n\nIntro alpha.\n", b=f"# Beta\n\n{p}\n\nX.\n\n{p}\n")
    _, changes = run(v2, store1, "c2")
    beta = v2["specs/b.md"].children[0].children
    assert beta[3].id == stayed and beta[1].id == text_ids(v1)[("specs/a.md", p)]
    assert [c.id for c in changes if c.moved] == [beta[1].id]


def test_a_moved_file_without_content_keeps_its_prefix_r12() -> None:
    """A file without content nodes moved with the same own text keeps its prefix.

    Spec: R12, R58 (E82)
    """
    store1, _ = run(parsed(t_types="# Types\n\nA.\n", t_placeholder=""), Store(), "c1")
    prefix = store1.files["specs/t/placeholder.md"].prefix
    v2 = parsed(t_types="# Types\n\nA.\n", u_placeholder="")
    assert detect_renames(v2, store1) == {"specs/u/placeholder.md": "specs/t/placeholder.md"}
    store2, changes = run(v2, store1, "c2")
    assert store2.files["specs/u/placeholder.md"].prefix == prefix
    assert by_id(changes)[prefix].status is Status.MOVED and prefix not in store2.retired_prefix_list


def test_a_file_replaced_at_its_path_gets_a_new_prefix_e80() -> None:
    """A file replaced at its path, none of its content kept, gets a new prefix; the old one retires.

    Spec: R58 (E80)
    """
    store1, _ = run(parsed(t_types="# Types\n\nIntegers are signed.\n\nFloats are IEEE.\n"), Store(), "c1")
    v2 = parsed(t_types="# Glossary\n\nA word list of terms used by the compiler.\n\nNothing else.\n")
    assert detect_renames(v2, store1) == {"specs/t/types.md": None}
    store2, changes = run(v2, store1, "c2")
    assert store2.files["specs/t/types.md"].prefix != "TYP"
    assert by_id(changes)["TYP"].status is Status.RETIRED and "TYP" in store2.retired_prefix_list


def test_a_list_turned_loose_reports_its_own_text_e86() -> None:
    """A list turned loose is child_changed with no changed children, and its entry gives old and new own text.

    Spec: R59, R63 (E86)
    """
    store1, _ = run(parsed(t_list="# L\n\n- one\n- two\n"), Store(), "c1")
    _, changes = run(parsed(t_list="# L\n\n- one\n\n- two\n"), store1, "c2")
    lst = [c for c in changes if c.kind is K.LIST][0]
    assert lst.status is Status.CHILD_CHANGED and not lst.changed_children
    report = report_markdown(changes)
    part = report[report.index(f"### {lst.id} ") :]
    assert part.split("### ")[1].count("```text") == 2  # old and new own text


def test_a_retired_section_reports_its_whole_last_text_r21() -> None:
    """A retired section reports its whole last text, children put back.

    Spec: R21, R63 (E85)
    """
    source = "# Types\n\nIntegers are signed.\n\n## Int\n\nIntegers.\n"
    store1, _ = run(parsed(t_types=source), Store(), "c1")
    _, changes = run(parsed(t_types="Integers.\n"), store1, "c2")
    section = by_id(changes)["TYP-1"]
    assert section.status is Status.RETIRED and section.last_text == source.rstrip("\n")
    assert "# Types\n\nIntegers are signed.\n\n## Int\n\nIntegers." in report_markdown(changes)
    assert json.loads(report_json(changes).splitlines()[-1])["last_text"] is not None


def test_lazy_similar_pairs_equal_scoring_every_pair() -> None:
    """Stage C yields the pairs of a full sort of every scored pair.

    Note: D27c

    Spec: R55
    """
    import random

    from norms_generator.store import SAME_FILE_BONUS, _similarity, _SimilarPairs

    rng = random.Random(7)
    words = "the a type value integer float string list map signed wraps on overflow is are".split()

    def sentence() -> str:
        return " ".join(rng.choice(words) for _ in range(rng.randint(2, 12)))

    for _ in range(20):
        olds = [(rng.choice([K.PARAGRAPH, K.ITEM]), sentence(), rng.choice("AB")) for _ in range(25)]
        news = [(rng.choice([K.PARAGRAPH, K.ITEM]), sentence(), rng.choice("AB")) for _ in range(25)]
        tie = lambda n, o: (n, o)  # noqa: E731
        scored = []
        for i, (kind, text, prefix) in enumerate(news):
            for j, (okind, otext, oprefix) in enumerate(olds):
                ratio = _similarity(text, otext) if kind is okind else None
                if ratio is not None:
                    score = ratio + (SAME_FILE_BONUS if prefix == oprefix else 0.0)
                    scored.append((-score, tie(i, j), i, j))
        scored.sort()
        expected, used_n, used_o = [], set(), set()
        for _, _, i, j in scored:
            if i not in used_n and j not in used_o:
                expected.append((i, j))
                used_n.add(i)
                used_o.add(j)
        pairs = _SimilarPairs(news, olds)
        got = []
        for i, j, _ in pairs.best_first(tie):
            got.append((i, j))
            pairs.taken(i, j)
        assert got == expected


def test_a_moved_file_reports_its_old_and_new_path_not_a_parent_r63() -> None:
    """A file has no parent: its moved entry names its two paths.

    Spec: R63 (E78)
    """
    source = "# Types\n\nNumbers are signed.\n\nStrings are UTF-8.\n"
    store1, _ = run(parsed(t_types=source), Store(), "c1")
    _, changes = run(parsed(t_language_types=source), store1, "c2")
    report = report_markdown(changes)
    assert "None" not in report
    assert "### TYP (file, specs/t/types.md -> specs/t/language/types.md)\n\nFile specs/t/types.md -> specs/t/language/types.md.\n" in report
    # moved and edited: the entry of another status says it moved, by path too
    store1, _ = run(parsed(t_types=source), Store(), "c1")
    _, changes = run(parsed(t_language_types="﻿" + source), store1, "c2")
    entry = report_markdown(changes)
    assert "Moved: file specs/t/types.md -> specs/t/language/types.md.\n" in entry and "None" not in entry


def test_a_bom_added_makes_the_file_edited_r31_r59() -> None:
    """A BOM is in the file's own text, and is information.

    Spec: R31, R59
    """
    store1, _ = run(parsed(t_types="# Types\n\nNumbers are signed.\n"), Store(), "c1")
    _, changes = run(parsed(t_types="﻿# Types\n\nNumbers are signed.\n"), store1, "c2")
    file_change = by_id(changes)["TYP"]
    assert file_change.status is Status.EDITED and file_change.new_text == "﻿\n"
    assert file_change.similarity is None
