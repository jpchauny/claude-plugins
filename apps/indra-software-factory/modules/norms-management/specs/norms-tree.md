# Norms Tree

**Audience:** Whoever builds the layer 2 generator, and the agents that read its output

**Scope:** How layer 2 represents the specs as a tree, gives each node an ID, and writes an annotated copy of each spec file

Layer 2 represents the specs as one tree. Each node that holds information has an ID. The generator writes a copy of each spec file with those IDs annotated in it. Agents search that copy, reason over it, and cite its IDs in what they write from it: the derived norms of layer 2 cite the norms they follow from; the acceptance units of layer 3 cite the norms they group and the derived norms that cite those norms; the code of layer 4 cites the acceptance units and the derived norms it is built from; and the acceptance tests cite the acceptance units ([LAY-3, LAY-4, LAY-8 and LAY-12](../../development-methodology/specs/layers.md#rules), [ACU-56](../../acceptance-management/specs/module.md#hashes-and-citations)), so that each can be traced back to the specification.

The terms norm, norm ID, norm hash, derived norm and derived norm fingerprint are those of [layers.md](../../development-methodology/specs/layers.md#terms), the terms acceptance unit, unit hash, norm citation and derived norm citation are those of [acceptance-management](../../acceptance-management/specs/module.md#terms), and the term derived norm behind its norms is that of [module.md](module.md#terms).

This document holds the requirements R1–R34 and the examples E1–E24: one example for each element (E1–E20), and four for meta rules that the elements do not show (E21–E24). The examples are requirements too, and serve as test cases for the generator.

Two companion documents complete it, with requirement and example numbers that follow on from these:

- [norms-annotation-cases.md](norms-annotation-cases.md): where IDs go in special cases, such as items whose first block is not a paragraph, tabs, empty items, definitions next to text, short or long table rows, and unclosed blocks (R35–R52, E25–E68).
- [norms-versions.md](norms-versions.md): how nodes are followed from one version of the specs to the next, how numbers and prefixes are given and never reused, the statuses, the JSONL, the output files, the change report and `verify` (R53–R64, E69–E89).

Everything that affects the generator's output or its data is in these three documents. The decisions of the user that the requirements cite (U1–U7) are recorded, with their reasons, in [Decisions of the user](#decisions-of-the-user).

## Requirements

A requirement's number is its name. It never changes, since code, tests and the other documents cite it. The requirements are grouped by subject, so one added later sits in its group, not at its rank: R31 and R33 are in The tree in layer 2, and R32 and R34 in Storage and process.

### The specs

- **R1. A tree.** Authors think of the specs as a tree, like a book with chapters, with folders above the files. The whole tree is: folders → Markdown files → headings (`#` to `######`, ATX or setext) → elements (paragraph, list, table, code, quote) → nested elements (items, sub-items, rows, cells). The shape of items and tables is given by R33.
- **R2. Freedom.** Within that tree, authors write as they wish: folders, files, headings and elements in any arrangement. The generator follows what is written; it asks nothing of the authors.
- **R3. GFM.** The specs are written in GitHub Flavored Markdown, GFM Spec 0.29: the Markdown that Claude writes and that Claude Code and GitHub display. Authors already know it: they build sections, tables, lists and code blocks with it.
  - Spec files are UTF-8. GFM sets no encoding, but the Markdown Claude writes is UTF-8, the JSONL stores text as UTF-8 strings, and the markers are UTF-8.
  - Line endings may be LF, CRLF or a lone CR. GFM accepts all three (R52).

### The tree in layer 2

- **R4. References to nodes.** A reference points to a node of the tree, at any level: a file, a section, an element or a nested element. Citing a node cites everything below it.
- **R5. The generator builds the tree.** The file system gives folders and files. The GFM parser gives elements and nested elements. Sections are the one level the parser does not give, because a heading does not contain what follows it; the generator builds them by grouping each heading with what follows.
  - Only a heading at the top level of the file opens a section, at any level 1 to 6.
  - A heading inside a list item or a block quote is a heading node of that container. It opens no section, because a section cannot cross out of its container (E22).
- **R6. Layer 2 is that tree.** Each of its nodes has an ID that can be referenced.
- **R7. Every node that holds information has an ID, and keeps it when it moves.** A horizontal rule and a blank line hold none, and have no ID.
- **R8. Order.** The order of a container's children counts as a change only in a numbered list (a sequence). In a bulleted list (an enumeration), and in every other container, moving children around is not a change (R13).
  - The ordinal belongs to the item's own text (R16, R31). A numbered list is a sequence, and renumbering it changes it.
  - Inserting or removing an item renumbers the later ones. They become `edited` and to review (U4, R59, E73).
  - Reordering items whose ordinals stay the same (`1.` `1.`) changes no own hash. It changes the tree hash of the list, and so of every node above it (R31, E75).
- **R9. Unique IDs with a prefix per file.** Each ID is unique. Each file has a prefix, and its nodes use it: `type-system.md` → `TYP`, its nodes `TYP-1`, `TYP-2`, …
  - On the first run, the nodes of a file are numbered 1, 2, … in pre-order, in document order: a container before its children, and the children in source order (E2, E10, E13 show it).
  - The file itself is its bare prefix (R29).
  - A number is never reused (R57).
- **R10. The generator assigns the prefixes.**
  - A prefix is upper-case ASCII letters, at least three.
  - The letters of a file name or a folder are its ASCII letters (`A`–`Z`, `a`–`z`), upper-cased; everything else is dropped before upper-casing, so `ß` and `ﬁ` give no letter (`type-system.md` → `TYPESYSTEM`, `ßeta.md` → `ETA`). A folder without letters is skipped.
  - Candidates for a path use the letters of its file name without `.md`, then of its folders, nearest folder first. Every folder of the path counts, the specs folder included (`specs/type-system.md` → `TYP`, `STY`, `SPT`, …).
  - The candidates come by length, from 3 up to the letters of the name plus the letters of all its folders. For each length L, in this order:
    - the name's first L letters, when it has that many;
    - then for each folder, nearest first, and for each k from 1 to L-1: the folder's first k letters followed by the name's first L-k letters, when the folder has k letters and the name L-k.
  - So all of one folder's candidates of a length come before the next folder's: `a/bb/name.md` gives `NAM`, `BNA`, `BBN`, `ANA`, then `NAME`, `BNAM`, `BBNA`, `ANAM`, … A candidate already given is skipped.
  - `compiler/architecture.md` gives `ARC`, then `CAR`, then `COA`.
  - A name with fewer than three letters starts with folder letters (`language/ai.md` → `LAI`).
  - Last comes a counter: three letters, then a counter in letters (`A`, `B`, …, `Z`, `AA`, `AB`, …). The three letters are the first three of the name's letters followed by its folders' letters, nearest folder first, padded with `X`. So `specs/1.md`, whose name has no letters, gives `SPEA`, as does `specs/.md`, whose name without `.md` is empty; `ai.md` gives `AIXA`.
  - New paths, and the paths that R58 replaces, which get a new prefix although they were in the previous JSONL, take, in sorted order, the first candidate that is not retired, not held by a file of the previous JSONL and not given in this run.
  - So the result is deterministic, and adding a file never changes another file's prefix.
  - Prefixes over time are in R58.
- **R11. A node moved to another file keeps its ID,** even though its prefix no longer matches the file it is in.
- **R12. A file renamed or moved keeps its prefix.** When a file counts as renamed or moved, as rewritten in place, or as replaced at its path is stated in R58 (norms-versions.md).
- **R13. Only numbered lists are ordered.** Every other node with children is unordered: files, sections, block quotes, bulleted lists, items (their blocks after the first paragraph), tables (header cells and body rows) and rows (cells). Moving their children does not change the parent's tree hash.
  - Moving a row or a column changes no hash: a table is not a sequence (U5). A column moves with its delimiter cell (`:---`, `---:`, a wider `-------`), which is in the table's own text, so the table's own hash takes the delimiter row's cells in sorted order (R31). Swapping two columns' delimiter cells without moving the columns changes no hash either.
  - In a row without a pipe at one end, the cell at that end has no padding on that side, so moving a column to or from that end changes the bytes of its cells and of its delimiter cell (`a | b |` → `b | a |`: the cell `a ` becomes ` a `). Those cells, and the table when its sorted delimiter cells differ, are then `edited` (R16, R59). With pipes at both ends, a moved column keeps its bytes.
  - A header cell's ID identifies its column wherever the column is (E74).
- **R14. Files have a prefix; folders have no ID.** The prefix alone identifies the whole file (`TYP`); `PREFIX-n` identifies a node in it. Every prefix is unique. A folder is identified by its path.
- **R15. An edited node keeps its ID** and is marked *to review*: whoever cited it must check, and may have to implement it again.
  - The generator pairs old and new nodes in stages (R53).
  - First identical subtrees and exact twins (R54).
  - Then similar text, ignoring every run of spaces, tabs and `>` that starts one of its lines, in a code or HTML block too (R55).
  - Then sections, lists, block quotes, tables and rows by their children, with a section following its heading (R56).
  - A file, section, list or block quote is not edited when its own text changes only by blank lines, `>` prefixes and the blanks around them, or thematic breaks, as when a blank line is added between two items. Those bytes hold no information. It is `child_changed` (R59). Its report entry is R63's: its old and new own text appear only when it has no changed child and its children were not reordered (E86).
  - A file's BOM is information: a file that gains or loses one is `edited` (R31, R59).
- **R16. Exact text.** A hash covers the exact bytes of the text, invisible characters included. One more space changes it. Nothing is normalized, because indentation is meaningful in Clean. The one exception is the order of a table's delimiter cells (R31, U5): their bytes count, their order does not.
  - A block's span starts at its container's content column on its first line, not where the parser says. So the indentation of its first line (0-3 spaces, or what a tab leaves) is its own, like that of its later lines.
  - Indenting an HTML block, paragraph, heading, table, item, quote or definition changes its own hash.
  - For a code block, the indentation before an opening fence decides how many spaces are stripped from every line of the code. The indentation of an indented code block is part of its code. Both are in the code block's own text.
  - The blank after a task item's checkbox stays outside the block that follows it.
  - On a lazy line (a table header row without its `>`), the span starts where the parser puts it.
  - A node's span ends at the end of its last line: the line's trailing spaces and tabs are in the span, its line ending is not (`para   ` keeps its three spaces). A block's last line is the last line the parser gives it, but for the three cases below.
  - A file's span is the whole file, from its first byte to its last.
  - A section's span runs from the start of its heading to the end of its last child. Blank lines and thematic breaks after its last child are not in it. They are in the own text of the node that holds the section: the enclosing section, or the file at the top level (E18, E18b, E18c).
  - A table cell spans the bytes between its pipes, its padding included.
  - Three cases end later than the last line the parser gives:
    - a block quote ends with its trailing blank `>` lines (R47);
    - a block quote or item whose definitions run onto lazy lines ends with the last of those lines (R43, E48);
    - an unclosed block runs to the end of its container (R48).
  - The spans are stored as `start` and `end` (R61). They are byte offsets, and `end` is exclusive: the span is the bytes from `start` up to, but not including, `end`. For `ab` followed by a line ending, the paragraph's span is 0 to 2.
- **R17. The parser is `cmark-gfm`,** the GFM implementation that GitHub uses, as bundled in the Python package `cmarkgfm` and reached through its C API. The extensions table, strikethrough, autolink, tagfilter and tasklist are attached. Footnotes are not used: they are not in GFM Spec 0.29. The generator is written in Python.
- **R31. Two hashes per node.** Each node has two SHA-256 hashes: **own**, over its own text, and **tree**, over its own hash and the tree hashes of its children. An acceptance unit and a derived norm cite a node by its norm ID and its norm hash, which [layers.md](../../development-methodology/specs/layers.md#terms) defines from its tree hash; the code of layer 4 and the acceptance tests never cite a node: the acceptance tests cite acceptance units, the code cites acceptance units and the derived norms it is built from, and both reach the nodes through the norm citations of what they cite ([ACU-56](../../acceptance-management/specs/module.md#hashes-and-citations), [LAY-4](../../development-methodology/specs/layers.md#rules)). Layer 3 learns that a cited node changed when its tree hash no longer starts with the norm hash of the citation ([ACU-27](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event)). A derived norm that cites the node gets another derived norm fingerprint when its generator updates the citation ([NRM-14](module.md#the-list-of-derived-norms)); one whose citation still holds the old norm hash is a derived norm behind its norms, and the run stops after layer 2 ([NRM-11 and ORC-10](module.md#derive-the-derived-norms)). Layer 4 learns it through the acceptance units it cites, whose unit hash changes when their citations are updated, and through the derived norms it cites, whose derived norm fingerprint changes ([ACU-52](../../acceptance-management/specs/module.md#hashes-and-citations), [ORC-25 and CIM-9](../../code-implementation/specs/module.md#implement-the-changed-norms), [LAY-12](../../development-methodology/specs/layers.md#rules)). The own hash lets the generator follow a node that moved (R7).
  - **Own text** is the exact bytes of the node's span with its children's spans cut out. List markers, `>` prefixes, pipes and indentation are included (R16).
  - **Own hash** is SHA-256 over the own text. For a table, whose own text holds its delimiter row, the delimiter row's cells (the bytes between its pipes, padding included) are first put in sorted byte order, each in the place of one of them, the pipes kept: `|---|:---|` and `|:---|---|` give one own hash. So moving a column with its delimiter cell changes no hash (U5), unless the move changes its padding at an end without a pipe (R13). The own text keeps the delimiter row as it is.
  - **Tree hash** is SHA-256 over the own hash, followed by the children's tree hashes. They are in source order for a numbered list, and sorted for every other container (R13).
  - Hashes are written as 64 lower-case hex digits. The tree hash's input is that hex text, in ASCII, with nothing between the hashes: not the raw 32-byte digests. A node without children has as tree hash the SHA-256 of its own hash's hex text.
  - So the own text of a file, section, list or block quote holds only blank lines, `>` prefixes and the blanks around them, and thematic breaks. A file's own text also holds its BOM, when it has one, and that BOM is information: adding or removing it makes the file `edited` and to review (R59).
  - A node moved to another nesting level changes its own hash. R55 still pairs it.
- **R33. Shape of items and tables.**
  - A list item and its first paragraph are one node: the item's own text holds that paragraph (E12).
  - The item's other blocks are its children (E14).
  - An item whose first block is not a paragraph has no paragraph of its own. That block is its first child (R35).
  - A table's children are its header cells, then its body rows. The header row has no node.
  - A body row's children are its cells.
  - An empty cell keeps a node and an ID.
  - A cell missing from a short row has no node.
  - Cells past the header's columns are not cells: they are text of their row, with no ID (E54).

### Annotations

- **R18. The ID goes at the end of the node's content.**
  - It goes before any trailing spaces or tabs of its line, which stay after it (`abc   ` → `abc ⟬TYP-1⟭   `).
  - For an ATX heading with a closing sequence, it goes right after the content. The blanks before the sequence stay after the ID (`# a  ##` → `# a ⟬TYP-2⟭  ##`, E2b).
  - An empty ATX heading has no content to end. Without a closing sequence, its ID goes at the end of its line, after any trailing spaces or tabs (`#   ` → `#    ⟬TYP-1⟭`, R51). With one, it goes right after the opening `#`s, and the blanks before the sequence stay after the ID (`# #` → `# ⟬TYP-1⟭ #`, `#  ##` → `# ⟬TYP-1⟭  ##`, E2b).
  - The exceptions are R24's.
- **R19. Delimiters `⟬` and `⟭`** (U+27EC and U+27ED, MATHEMATICAL LEFT and RIGHT WHITE TORTOISE SHELL BRACKET). They appear nowhere in the specs, in Clean, in the Lean 4 core, in Mathlib or in `clean-formal-pilot`, and Lean gives them no meaning.
  - The generator refuses a spec file that holds `⟬` or `⟭` (R34). Its markers would not be IDs, and a search for an ID could find the specs' own text.
- **R20. The agent comes first.** The overriding criterion is that the norms corpus is optimal for an agent to search and reason over. Where another criterion conflicts, such as readability for people or line numbers matching the specs, this one wins. Layer 2 is not for people to read: people read the specs.
- **R24. Hybrid annotation.** If a node's ID can go at the end of the node, it goes there. If it cannot, the node is framed: `⟬ID begin⟭` on a line of its own before it, `⟬ID end⟭` on a line of its own after it.
  - A heading has its ID at the end of its text, also when its text runs over several lines (E3b). It is framed when the ID there would change it, as when a setext heading's text would become a definition or a list item.
  - A paragraph of one line has its ID at its end (E17), unless the ID there would change how it renders. Then it is framed, as `[x]:`, which would become a definition (E17b).
  - A paragraph of several lines is framed, so that a search finds its start and its end (E8).
  - An item has its ID at the end of its first paragraph, also when that paragraph runs over several lines (R33, E12).
  - A table cell and a body row have their IDs at the end of their text (R45).
  - Everything else is framed: a definition (E7), a code or HTML block (R26), and every section, list, block quote and table.

  The exceptions:
  - An item whose first block is not a paragraph has its ID right after its marker, or after its checkbox for a task item (R35). So does an item whose first paragraph would change how the item parses with the ID at its end, as `- [ ]` (R35, E28, E29).
  - A paragraph that a table interrupts may have its ID at the end of its last line, or of an earlier one (R44).
  - On an item's marker line that cannot be split, the IDs of the nodes that start there go at the end of that line (R36).
  - When no placement at the node keeps the file's blocks, the node is framed at the bounds of the top-level block that holds it (a child of the file or of a section), inside that block's own frame (R49).
  - The whole annotated file is checked, and nodes whose placements clash are framed the same way (R50).

  Frames always nest.
- **R25. IDs without leading zeros, and three markers.**

  | Marker          | Meaning                           |
  | --------------- | --------------------------------- |
  | `⟬TYP-3⟭`       | A node, at the end of its content |
  | `⟬TYP-3 begin⟭` | The start of a framed node        |
  | `⟬TYP-3 end⟭`   | The end of a framed node          |

  A search for an ID must include the end of the marker, so that `TYP-3` does not also find `TYP-30`: `grep "⟬TYP-3[⟭ ]"`.
- **R26. Every code block is framed,** fenced or indented, whatever its language. Nothing is written inside a code block, not even on its opening line, so the Clean examples stay intact byte for byte.
  - An unclosed block is framed like any other: a fenced code block never closed, or an HTML block of types 1-5 without its closing sequence.
  - Nothing else is inserted (no closing fence, no closing tag), since the specs are never corrected.
  - Such a block runs to the end of its container, so for a parser its end marker falls inside it, and so do the end markers of the containers that close there (a section, a quote, a list). So may the blank lines R30 adds next to those markers. This is the one accepted exception (U1, R48), and `verify` tolerates exactly those end markers and blank lines at the end of the unclosed block (R64, E61).
- **R27. One child, one ID.** A block quote, list or section whose single child covers its whole content has one ID: the child's.
  - Examples are a quote of one paragraph, a list of one item, and a section with only its heading.
  - The node left is the child: its kind, its ID and its children. It takes the container's span, so its own text holds what the container's held besides: the `> ` prefixes and the trailing blank `>` lines, and its `start` and `end` are the container's (R61). `> a`, `>`, `>` is one `paragraph` whose own text is all three lines, and adding one more blank `>` line makes it `edited`.
  - It also takes the container's place for its markers: a marker line of it takes the prefix of the containers around the collapsed one, as the container's own marker lines would, not the collapsed quote's `> ` (R30). In `- > a`, `  > b`, the paragraph spans both lines of the quote, and its marker lines are `  ⟬TYP-2 begin⟭` and `  ⟬TYP-2 end⟭`, with no `>`. In E24, the inner quote's paragraph takes only the outer quote's `> `.
  - What the child may leave of the container is only `>` prefixes and blank lines, including the quote's trailing blank `>` lines (R47).
  - A container that also holds a thematic break in its span keeps its own node (E21).
  - A thematic break after a section's last child is not in the section's span (R16). So a section of a heading and such a break holds only its heading, and is collapsed into it (E21b).
  - The file is never collapsed: it has a prefix, not a number (R14, R29, E19).
- **R28. The approved examples are requirements,** and serve as test cases for the generator: E1–E24 here, E25–E68 in norms-annotation-cases.md and E69–E89 in norms-versions.md. Every annotated example is the generator's exact output.
  - An annotated example of this file and of norms-annotation-cases.md is numbered as on a first run, with the prefix `TYP`, and is shown without the file marker (R29), unless its prose says it is shown with it (E19, E23).
  - An example heading may hold several pairs of a spec text and its annotated copy. The first pair is cited by the heading's number, the later ones by that number and a letter: the second pair of E2 is E2b, the third of E18 is E18c.
- **R29. The file is marked once,** with `⟬TYP⟭` on its first line and no end: it extends to the end of the file. Every marker matches `⟬[A-Z]+(-[0-9]+)?( begin| end)?⟭`.
  - The file marker goes after a BOM when the file has one.
  - A blank first line is reused as the marker's blank line (E23).
  - An empty file holds only its marker (`⟬TYP⟭` and a line ending).
- **R30. Blank lines and indentation.**
  - A marker on a line of its own goes in the gap between two blocks. It has a blank line before and after it, except at the start or end of the file.
  - An end marker goes on the line right after the framed span's last line, and a begin marker on the line right before its first line. So in a gap of several blank lines, an end marker comes first and a begin marker last.
  - The line next to the marker on each side is reused as its blank line when it is blank, and a blank line is added on a side where it is not. So the gap's blank lines serve only on the marker's far side. The paragraph `x`, `y`, then two blank lines and `z`, gives `y`, an added blank line, the end marker, and the two blank lines. E65 shows the same after a definition: the gap's two blank lines follow its end markers.
  - Several markers at one place are written ends first, innermost first, then begins, outermost first, with one blank line between two of them.
  - Inside a container, a marker line takes the container's prefix: `> ` for each enclosing block quote and the item's content indentation, because GFM requires it. Inside a quote, the blank line is a bare `>` (E24).
  - The item content indentation is counted from the quote's content, after the optional space that follows `>`. That space takes one column, or a tab's first column when a tab follows `>` (R38).
  - A marker at the end of a line always has a blank before it: a space, or the source's tab after `-\t` (R38). An empty item's ID instead has 1 to 4 inserted spaces before it, even after `-\t` (R39).
  - The marker lines inside a list keep their blank lines, so a tight list that holds a framed node renders loose. This is accepted for the agent (R20, U2).
  - Nothing else is indented, except the rest of a marker line moved to a line of its own, which keeps its column (R37).

### Storage and process

- **R21. The process.**
  - **A. First implementation:** the acceptance architect of layer 3 searches the annotated files of norms, picks the nodes that each acceptance unit groups, and cites their IDs in the acceptance unit, each with its norm hash ([ACU-8](../../acceptance-management/specs/module.md#the-files-of-the-acceptance-repository)); the acceptance unit also cites the derived norms that cite those nodes, each with its derived norm fingerprint, which a script computes ([ACU-78](../../acceptance-management/specs/module.md#the-files-of-the-acceptance-repository)). The implementing agent of layer 4 implements those nodes through the acceptance units and their derived norms, and cites in the code the acceptance units, each with its unit hash, and the derived norms that the code is built from, each with its derived norm fingerprint ([IMP-6](../../code-implementation/use-cases/implement/specs/implement.md), [CIM-11](../../code-implementation/specs/module.md#the-derived-norms-of-the-code), [ACU-56](../../acceptance-management/specs/module.md#hashes-and-citations)).
  - **B. A change:** in layer 3, the acceptance architect takes the citations of norms that [ACU-27](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event) finds changed or no longer in layer 2, compares the old text with the new, and updates the acceptance units and their scenarios, and the derived norm citations whose derived norm fingerprint changed, as [ACU-28](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event) says; each updated citation takes the new norm hash or derived norm fingerprint, which changes the unit hash of its acceptance unit ([ACU-52](../../acceptance-management/specs/module.md#hashes-and-citations)). In layer 4, an agent takes the citations of acceptance units and the derived norm citations of the code that [ORC-25 and CIM-9](../../code-implementation/specs/module.md#implement-the-changed-norms) find `changed`, `retired` or `unknown`, finds each in the code, and its acceptance unit in the acceptance repository or its derived norm in the norms repository, and decides whether to implement it again. Each citation implemented again takes the new unit hash or derived norm fingerprint.
  - Each version of norms is published with a report of what changed, by ID: the old text and the new, the child that changed inside a cited container, and, for a retired ID, its last text (R63).
  - `to_review` and `changed_since` describe one version's change only, from version N-1 to N (R60, U3). Layers 3 and 4 learn what changed for them as R31 says.
  - "For a retired ID, its last text" is the node's whole text, with its children's text put back, so a retired section shows what it said (R63).
- **R22. For now, a person tells the repositories of layers 3 and 4 that a new version exists.**
- **R23. The JSONL is the only source of truth for the IDs; the specs, for the content.** The tree is stored as JSONL, one line per node, and holds the IDs and their history (R61). The specs are the single source of truth for what the files say (U6). The annotated file is generated from the specs at the pinned commit and the JSONL, by writing each ID in at its place. It is never read as input. The first run is the same process with an empty JSONL.
  - The annotated file is the spec file with bytes inserted. Nothing of the specs is moved or removed, so columns are not realigned.
  - The insertions are: markers; the blank before an inline ID; blank lines where R30 needs one; `>` prefixes and item indentation on marker lines (R30); the ` |` of a row's ID: after the ID of a row with a closing pipe (` ⟬ID⟭ |`), before the ID of a row without one (` | ⟬ID⟭`), and for each empty cell added to a short row (R45); a leading `|` (R46); the line break and indentation that move the rest of an item's marker line (R35, R37); and the blanks and blank line of an empty item's ID (R39).
  - The JSONL records the insertions as one record per offset, in ascending order of offset. A record holds everything inserted at its offset, joined in the order it appears in the annotated file: at offset 0, the file marker and a begin marker are one record (R61).
  - Removing exactly those gives back the spec file byte for byte, which `verify` checks (R64).
- **R32. A viewer.** A viewer of the specs with their layer 2 references will be a meta app in this repository.
- **R34. Refused input.** `build` writes nothing and exits with status 2 (R62 lists every exit status) in each of these cases:
  - a spec file is not UTF-8. It names the file, the first bad byte and its offset: `norms-gen: specs/a.md: not UTF-8 (byte 0xff at offset 3); spec files must be UTF-8 (R34)`;
  - a file holds `⟬` or `⟭`. It names the file, the first delimiter it holds and its offset: `norms-gen: specs/a.md: holds the delimiter ⟭ at offset 4; the specs never hold ⟬ or ⟭ (R19, R34)`;
  - the path of a selected file (R62) is not UTF-8 (it names the path, its bad bytes written as `\xff`); an excluded path is ignored whatever it holds. A path that is not UTF-8 and also holds a control character is refused as not UTF-8, with its control characters written as in the next case, so the message stays on one line: `norms-gen: specs/a\xff\x0ab.md: path not UTF-8`;
  - the path of a selected file holds a control character, one of Unicode category Cc (U+0000 to U+001F, U+007F to U+009F), such as a tab or a line break: a line break would split an entry heading of the report (R63) and a problem line of verify (R62). It names the path, each such character written as `\x0a`: `norms-gen: specs/a\x0ab.md: path holds a control character`;
  - the repository holds no selected `.md` file at the commit (R62), as with a `--specs` that names the wrong repository, which would otherwise retire every ID and prefix for good. It names the commit's full object name: `norms-gen: no .md file to build at <commit>; is --specs right?`;
  - the previous JSONL cannot be read: it names the file and the line, then the name of the error and its message as Python's `json` module or the reader gives them (`<path>:1: JSONDecodeError: Expecting value: line 1 column 1 (char 0)`), or, for a JSONL that is not UTF-8, the file and Python's message, which names the first bad byte and its offset (`<path>: not UTF-8: 'utf-8' codec can't decode byte 0xff in position 2: invalid start byte`), or, for one that cannot be opened, as a folder at its path, a file without read permission, a symbolic link there that leads nowhere or loops, or a file in place of `data/`, the file and the system's reason (`<path>: cannot be opened: Is a directory`). Only a JSONL of which nothing at all is at its path is absent, which makes a first run (R23): a broken link is not, so a build never renumbers every ID because the JSONL's link is broken. A line cannot be read when it is not a JSON object (a line nested deeper than the reader can follow included, R61), has an unknown `type`, lacks a required field, or has a field of the wrong type or form, such as a prefix `ab` or `SUB` followed by a line break (R61). An empty line, or one of only whitespace, is skipped, and a line may end in a carriage return (R61);
  - the previous JSONL can be read but is not consistent: an ID stored twice, active or retired, two `file` lines with one prefix, a retired prefix that a `file` line holds, or an active node whose file has no `file` line. The build would write duplicate IDs or prefixes, or give a retired prefix again (R9, R14, R58). It names the file and every problem, joined by `; `, as verify words them (R64): `<path>: not consistent: SPA-1 is stored twice (active in specs/a.md, active in specs/b.md)`;
  - an output path is in the way (R62): `specs-repo-annotated/` under the output folder is a file (`<path>: not a folder`), `data/` or `specs-repo-annotated/` is a symbolic link (`<path>: a symbolic link; a build never writes outside the output folder through a link`), or `data/report.md`, `data/report.json` or `data/tree.jsonl.tmp` is a folder or a symbolic link (`<path>: a folder`, or the same link message). Writing there would crash half way or write outside the output folder through a link, and a folder there is not the generator's to remove. It is checked after the previous JSONL is read and before anything is written, so a file at `data/`, or a link there that leads to a file or loops, is the JSONL that cannot be opened of the bullet above, not an output in the way, and a link at `data/` that leads to a folder, or nowhere (no JSONL is then found), gets the link message;
  - two selected paths, a path and a folder of another one, or two folders of them, differ only in case or Unicode normalization (`specs/A.md` and `specs/a.md`, `specs/X.md/b.md` and `specs/x.md`, `specs/A/x.md` and `specs/a/y.md`). On a file system that ignores case or normalization, as macOS and Windows do by default, two copies would be one file and overwrite each other, a copy and a folder would take one name, and two folders would be one, so the folder tree of the specs would not be kept (R62, E20). It names the two names that differ, each a path or a folder, the first in path order first, and says which of the three it is: `norms-gen: specs/A and specs/a differ only in case or Unicode normalization; on a file system that ignores both, their copies would share one folder, and the folder tree would not be kept (R34)`. For two paths it ends `their copies would be one file and overwrite each other (R34)`, and for a path and a folder `a copy and a folder of copies would take one name (R34)`, naming the folder (`specs/X.md and specs/x.md`). Two names that are equal once each is put in Unicode NFD, case-folded with Python's `str.casefold()`, and put in NFD again, count as such a pair;
  - git fails: the specs path is not a git repository, or `--commit` does not name a commit of it. The message is the git command, without `git -C <path>`, then `: ` and git's own message, as for a path that is not a git repository: `git rev-parse --verify --quiet HEAD^{commit}: fatal: not a git repository (or any of the parent directories): .git`. For a commit git does not know (`--commit nope`), git gives no message, and the generator writes `'nope' is not a commit of <path>`.

  `verify`'s side is R64.

## Decisions of the user

The user took these decisions where the generator had to choose between two readings. The requirements cite them as U1–U6.

- **U1. Unclosed blocks are not corrected.** An unclosed fenced code block, or an HTML block of types 1-5 without its closing sequence, is framed like any other block, and nothing else is inserted.
  - Why: the content of the specs is never corrected. A closing fence or tag would change the code of the specs.
  - The cost: for a parser, the block's end marker, those of the containers that close with it, and the blank lines next to them fall inside the block. This is accepted, and `verify` tolerates exactly those end markers and blank lines (R26, R48, R64).
- **U2. Marker lines keep their blank lines, even inside a list.** A tight list that holds a framed node then renders loose.
  - Why: the blank lines make the frames easy to read for the agent (R20), and a list's tightness holds no information.
  - The structure check ignores list tightness (R30, R64, E13).
- **U3. `to_review` and `changed_since` belong to one version.** They describe the step from version N-1 to version N only. Nothing is carried over from earlier steps.
  - Why: each version of norms is published with its own report. A repository of layer 3 that skipped versions compares the norm hash of each of its citations with the tree hash of its node now, which is exact; layer 4 follows the unit hashes of the acceptance units it cites (R21, R31).
  - Details: R60, E84.
- **U4. The ordinal belongs to the item's own text.** Inserting or removing an item renumbers the later ones, and they are `edited` and to review.
  - Why: a numbered list is a sequence, and renumbering it changes it.
  - Details: R8, R59, E73.
- **U5. Rows and cells have no order.** Moving a row or a column changes no hash, and is not reported.
  - Why: a table is not a sequence. Moving a row or a column changes nothing of what it says.
  - A column moves with its delimiter cell, so the delimiter row's cells have no order either: the table's own hash takes them sorted (R31).
  - A header cell's ID identifies its column wherever the column is (R13, E74).
  - The limit: a hash covers exact bytes (R16). In a row without a pipe at one end, a column moved to or from that end changes its cells' padding, so those bytes changed and the cells are `edited` (R13).
- **U6. `specs-repo-annotated/` belongs to the generator.** After every build, `specs-repo-annotated/` holds exactly this build's copies, annotated and plain, and the folders that hold them, and nothing else. Everything else under it is removed: a file that is no copy, a folder that holds no copy (with everything in it), a symbolic link wherever it stands, a folder at the path of a copy, a file at the path of a folder of copies, and the copies left by a build whose JSONL was lost. A symbolic link is removed itself and never followed, so nothing outside the output folder is touched. `verify` reports each such path as a problem.
  - Why: `specs-repo-annotated/` is derived from the specs, and only the generator writes there. The specs are the single source of truth: anything else written there skips the process, and is not kept.
  - Details: R62, R64.
- **U7. Everything of the generator is in the plugin `norms-management`.** Everything developed for the generator lives in the folder `apps/indra-software-factory/modules/norms-management/` of the repository `jpchauny/indra-software-factory`, and nowhere else: these meta specs (`specs/`), the code (`src/`), the tests and their fixtures (`tests/`), the documents of its development (`docs/`), the meta use cases that run it (`use-cases/`), and the files of its package (`pyproject.toml`, `uv.lock`). A project's norms repository holds only the output of a build (R62), never a part of the generator, and no other folder of `jpchauny/indra-software-factory` holds one either.
  - Why: one generator serves every project, so it has one place, and every project uses the same version of it. A plugin is installed as its own folder and nothing else of the repository, so a part of the generator outside `apps/indra-software-factory/modules/norms-management/` would be missing wherever the plugin is installed.

## Elements

The elements follow the GFM Spec 0.29 in its order, with its extensions, then the three levels that are not GFM, then four examples of meta rules (E21–E24). Each example shows the spec text and its annotated copy.

Some examples hold bytes that do not show, such as a tab. The prose under each example says where they are.

Every annotated example was checked with `cmark-gfm`. The elements of the original survive, except that a tight list holding a framed node may become loose (R30, U2). Every marker on a line of its own stays outside them, except the end markers that fall inside an unclosed code or HTML block: its own, and those of the containers that close with it (R26, R48). Every annotated example is the generator's exact output (R28), numbered as on a first run with the prefix `TYP` and shown without the file marker (R29), unless its prose says otherwise (E19, E23). Special cases are in norms-annotation-cases.md, versions in norms-versions.md.

### E1. Thematic break (GFM §4.1)

Not annotated: it holds no information (R7).

```markdown
Numbers are always signed.

---

Strings are UTF-8.
```

```markdown
Numbers are always signed. ⟬TYP-1⟭

---

Strings are UTF-8. ⟬TYP-2⟭
```

A `---` right under a paragraph, with no blank line, is not a thematic break but a setext heading (E3).

### E2. ATX heading, and its section (GFM §4.2)

The heading has its ID at the end of its text. If it has a closing `#` sequence, the ID goes before it: `## Numbers ⟬TYP-5⟭ ##`, which keeps the title `Numbers ⟬TYP-5⟭`; after it, the `##` would become part of the title. The section (E18) is framed. Sections close innermost first. An empty ATX heading without a closing sequence has its ID at the end of its line, after any trailing blanks, at column 1 or not (`  #`, `> #`: R18, R51). One with a closing sequence is shown below.

```markdown
# Types

Clean has a small set of built-in types.

## Numbers ##

Numbers are always signed.

### Overflow

Integers wrap on overflow.

## Strings

Strings are UTF-8.
```

```markdown
⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Clean has a small set of built-in types. ⟬TYP-3⟭

⟬TYP-4 begin⟭

## Numbers ⟬TYP-5⟭ ##

Numbers are always signed. ⟬TYP-6⟭

⟬TYP-7 begin⟭

### Overflow ⟬TYP-8⟭

Integers wrap on overflow. ⟬TYP-9⟭

⟬TYP-7 end⟭

⟬TYP-4 end⟭

⟬TYP-10 begin⟭

## Strings ⟬TYP-11⟭

Strings are UTF-8. ⟬TYP-12⟭

⟬TYP-10 end⟭

⟬TYP-1 end⟭
```

An empty ATX heading with a closing sequence has its ID right after its opening `#`s. The blanks before the sequence stay after the ID, as they do after the text of `# a  ##` (R18). Each line here has two spaces before its closing sequence. Each section holds only its heading, so it has the heading's ID (R27).

```markdown
#  ##

# a  ##
```

```markdown
# ⟬TYP-1⟭  ##

# a ⟬TYP-2⟭  ##
```

### E3. Setext heading (GFM §4.3)

A heading underlined with `===` (level 1) or `---` (level 2). Its ID goes at the end of its last line of text, above the underline. A marker right above it, with no blank line, would become part of the title.

```markdown
Numbers
-------

Numbers are always signed.
```

```markdown
⟬TYP-1 begin⟭

Numbers ⟬TYP-2⟭
-------

Numbers are always signed. ⟬TYP-3⟭

⟬TYP-1 end⟭
```

Over several lines, the ID goes at the end of the last line. This file is a section with only its heading, so it has one ID (R27):

```markdown
Whole
numbers
=======
```

```markdown
Whole
numbers ⟬TYP-1⟭
=======
```

### E4. Indented code block (GFM §4.4)

Code marked by four spaces of indentation. Framed (R26). Without the blank line after the begin marker, the code is no longer code: it becomes part of the marker's paragraph, since an indented line cannot interrupt a paragraph. The blank line before the end marker is R30's.

```markdown
Run the build:

    cln build
    cln test
```

```markdown
Run the build: ⟬TYP-1⟭

⟬TYP-2 begin⟭

    cln build
    cln test

⟬TYP-2 end⟭
```

### E5. Fenced code block (GFM §4.5)

Framed (R26), whatever its language. Nothing is written on its opening line: there, a fence with no language would take the ID as its language. A label before the code, such as `**Example (passes):**`, is a node of its own with its own ID.

````markdown
**Example (passes):**
```clean
integer x = 5
```
````

````markdown
**Example (passes):** ⟬TYP-1⟭

⟬TYP-2 begin⟭

```clean
integer x = 5
```

⟬TYP-2 end⟭
````

### E6. HTML block (GFM §4.6)

HTML written directly in the Markdown. Framed: an ID inside would change the HTML. An HTML block of types 6-7 ends only at a blank line, so without one the end marker would fall inside it.

An unclosed HTML or code block (types 1-5, such as `<!--` with no `-->`, or a fence never closed) runs to the end of its container. It is framed like any other, and its end marker then falls inside it for a parser. This is accepted (R26, R48, E62). The block is unchanged.

```markdown
<div align="center">
  <img src="logo.png">
</div>
```

```markdown
⟬TYP-1 begin⟭

<div align="center">
  <img src="logo.png">
</div>

⟬TYP-1 end⟭
```

### E7. Link reference definition (GFM §4.7)

Defines elsewhere the URL of a link. Framed: an ID at its end turns it into a paragraph, and the link no longer works. A definition cannot follow text directly, so the begin marker needs the blank line after it.

- A definition directly followed by text that would parse differently on its own is not framed apart: it belongs to the paragraph or heading after it (R41).
- A paragraph that a table interrupts keeps a definition-like first line as text, and may share the table's frame (R44).
- Definitions can continue on the lazy lines of a quote or item (R43).

```markdown
See [GFM].

[GFM]: https://github.github.com/gfm
```

```markdown
See [GFM]. ⟬TYP-1⟭

⟬TYP-2 begin⟭

[GFM]: https://github.github.com/gfm

⟬TYP-2 end⟭
```

### E8. Paragraph (GFM §4.8)

A paragraph of one line has its ID at the end. A paragraph of several lines is framed, so that a search finds its start and its end.

```markdown
Numbers are always signed.

An integer is 64 bits wide,
signed, and wraps on overflow.
```

```markdown
Numbers are always signed. ⟬TYP-1⟭

⟬TYP-2 begin⟭

An integer is 64 bits wide,
signed, and wraps on overflow.

⟬TYP-2 end⟭
```

### E9. Blank lines (GFM §4.9)

Not annotated: they hold no information (R7); they only separate blocks.

```markdown
Numbers are always signed.

Strings are UTF-8.
```

```markdown
Numbers are always signed. ⟬TYP-1⟭

Strings are UTF-8. ⟬TYP-2⟭
```

### E10. Table (GFM §4.10, extension)

| Node   | Where its ID goes                              |
| ------ | ---------------------------------------------- |
| Table  | A frame: no line belongs to the table alone    |
| Column | At the end of its header cell                  |
| Row    | After the row's closing `\|`, as an extra cell |
| Cell   | At the end of its text                         |

- The parser drops every cell past the header's columns, so the row's ID is not in the parsed table. It lives only in the text, where agents search for it.
- The delimiter row has no ID. It is in the table's own text, and its cells move with their columns: their order changes no hash (R31, U5). The header row cannot take an extra cell: the table would stop being a table.
- The table's children are its header cells and body rows, and a row's children are its cells (R33). A column is not a node: it is referenced through its header cell.
- Rows and columns have no order (R13).
- Columns are not realigned: the annotated file only gains bytes (R23).
- Without a blank line, the end marker would become one more row.
- Short rows, long rows, rows without pipes and inserted pipes are in R45 and R46.

```markdown
| Type    | Size    | Default |
| ------- | ------- | ------- |
| integer | 64 bits | 0       |
| float   | 64 bits | 0.0     |
```

```markdown
⟬TYP-1 begin⟭

| Type ⟬TYP-2⟭    | Size ⟬TYP-3⟭    | Default ⟬TYP-4⟭ |
| ------- | ------- | ------- |
| integer ⟬TYP-6⟭ | 64 bits ⟬TYP-7⟭ | 0 ⟬TYP-8⟭       | ⟬TYP-5⟭ |
| float ⟬TYP-10⟭   | 64 bits ⟬TYP-11⟭ | 0.0 ⟬TYP-12⟭     | ⟬TYP-9⟭ |

⟬TYP-1 end⟭
```

### E11. Block quote (GFM §5.1)

A container: framed, and each block inside it annotated. Without a blank line, the end marker would join the quote's last paragraph. A quote's end marker goes after its trailing blank `>` lines, which belong to the quote (R47, E59).

```markdown
> **Note:** integers never promote.
>
> Use an explicit cast.
```

```markdown
⟬TYP-1 begin⟭

> **Note:** integers never promote. ⟬TYP-2⟭
>
> Use an explicit cast. ⟬TYP-3⟭

⟬TYP-1 end⟭
```

A quote of one paragraph has one ID, the paragraph's (R27):

```markdown
> **Note:** integers never promote.
```

```markdown
> **Note:** integers never promote. ⟬TYP-1⟭
```

### E12. List item (GFM §5.2)

The ID goes at the end of the item's own text, even over several lines; the item and its first paragraph are one node (R33). An item is not framed in place: a marker outside the list splits it into several lists. When no place at the item keeps the file's blocks, it is framed at its top-level block (R49). The list itself is framed (E16). An item whose first block is not a paragraph has its ID right after its marker (R35, E25), and so does an item whose first paragraph would change how the item parses with the ID at its end (R35, E28, E29). An empty item is in R39.

```markdown
- integer is 64 bits
- float follows IEEE 754 and is
  64 bits wide
- string is UTF-8
```

```markdown
⟬TYP-1 begin⟭

- integer is 64 bits ⟬TYP-2⟭
- float follows IEEE 754 and is
  64 bits wide ⟬TYP-3⟭
- string is UTF-8 ⟬TYP-4⟭

⟬TYP-1 end⟭
```

### E13. Nested list items (GFM §5.2)

Each item, parent or child, has its ID at the end of its own text. A parent item covers its nested items: it ends at the next item of the same or a higher level. A nested list of more than one item is framed (E16), with the indentation of the parent item's content (R30). The blank lines around the nested list's frame make the outer list loose: it renders with paragraphs in its items. This is accepted for the agent (R20, R30, U2).

```markdown
- Exit codes:
  - 0 when the build passes;
  - 1 when it fails.
- Output goes to stderr.
```

```markdown
⟬TYP-1 begin⟭

- Exit codes: ⟬TYP-2⟭

  ⟬TYP-3 begin⟭

  - 0 when the build passes; ⟬TYP-4⟭
  - 1 when it fails. ⟬TYP-5⟭

  ⟬TYP-3 end⟭

- Output goes to stderr. ⟬TYP-6⟭

⟬TYP-1 end⟭
```

### E14. List item with blocks inside (GFM §5.2)

The item has its ID at the end of its text and covers everything inside it. A code block inside is framed (R26). Its markers take the indentation of the item's content, three spaces for `1. `; without it, the list splits in two and the code falls outside the item. The code line `integer add(...)` is indented with three spaces and then a tab, in the input and in the output: the tab is the code's own, and the markers take only the three spaces.

````markdown
1. Declare the function:

   ```clean
   functions:
   	integer add(integer a, integer b)
   ```

2. Call it.
````

````markdown
⟬TYP-1 begin⟭

1. Declare the function: ⟬TYP-2⟭

   ⟬TYP-3 begin⟭

   ```clean
   functions:
   	integer add(integer a, integer b)
   ```

   ⟬TYP-3 end⟭

2. Call it. ⟬TYP-4⟭

⟬TYP-1 end⟭
````

### E15. Task list item (GFM §5.3, extension)

A list item (E12). Its checkbox must stay first after `- `, which an ID at the end leaves untouched. Checking or unchecking it changes the exact text, so it changes the hash (R16). An item whose text alone would become a checkbox once followed by an ID (`- [ ]`) has its ID after its marker (R35, E28). A nested list starting with `[ ]` on its parent item's marker line takes its ID at the end of that line (R36, E32).

```markdown
- [ ] write the tests
- [x] build passes
```

```markdown
⟬TYP-1 begin⟭

- [ ] write the tests ⟬TYP-2⟭
- [x] build passes ⟬TYP-3⟭

⟬TYP-1 end⟭
```

### E16. List (GFM §5.4)

The container of its items: framed, and each item annotated. Numbered or bulleted, the annotation is the same; only the tree hash differs (R13). A list of one item has one ID, the item's (R27). A tight list stays tight unless it holds a framed node (R30).

```markdown
1. Parse the file.
2. Check the types.
3. Emit WebAssembly.
```

```markdown
⟬TYP-1 begin⟭

1. Parse the file. ⟬TYP-2⟭
2. Check the types. ⟬TYP-3⟭
3. Emit WebAssembly. ⟬TYP-4⟭

⟬TYP-1 end⟭
```

### E17. Inline extensions (GFM §6.5, §6.9, §6.11)

Strikethrough, extended autolinks and disallowed raw HTML live inside the text of a node and are not nodes. An ID is never written inside them, nor inside a link or a code span. The space before the ID ends an autolink, which would otherwise take the ID into its URL.

```markdown
The old size was ~~32 bits~~

See www.github.github.com/gfm

Never write <script> in a page.
```

```markdown
The old size was ~~32 bits~~ ⟬TYP-1⟭

See www.github.github.com/gfm ⟬TYP-2⟭

Never write <script> in a page. ⟬TYP-3⟭
```

A paragraph of one line is framed when its ID at the end would change it: `[x]: ⟬TYP-1⟭` would be a definition (R24).

```markdown
[x]:
```

```markdown
⟬TYP-1 begin⟭

[x]:

⟬TYP-1 end⟭
```

### E18. Section (not GFM)

Built by the generator (R5): a section starts at its heading and takes the blocks up to the next heading of the same or a higher level, or up to the end of the file. Its span ends at the end of its last child, so blank lines and thematic breaks after that child are not in it: its end marker goes before them (R16). It is framed (E2). Content before the first heading belongs to the file, not to a section. At the end of the file, every open section closes, innermost first. Only a heading at the top level of the file opens a section, at any level 1 to 6. One inside a list or quote is an element (R5, E22).

```markdown
**Status:** Accepted

# Types

## Strings

Strings are UTF-8.
```

```markdown
**Status:** Accepted ⟬TYP-1⟭

⟬TYP-2 begin⟭

# Types ⟬TYP-3⟭

⟬TYP-4 begin⟭

## Strings ⟬TYP-5⟭

Strings are UTF-8. ⟬TYP-6⟭

⟬TYP-4 end⟭

⟬TYP-2 end⟭
```

A thematic break after a section's last paragraph is not in the section. The end marker of `TYP-1` goes before it, and the break is in the file's own text.

```markdown
# a

b

---

# c

d
```

```markdown
⟬TYP-1 begin⟭

# a ⟬TYP-2⟭

b ⟬TYP-3⟭

⟬TYP-1 end⟭

---

⟬TYP-4 begin⟭

# c ⟬TYP-5⟭

d ⟬TYP-6⟭

⟬TYP-4 end⟭
```

After a subsection's last child, a thematic break that does not close the outer section is in that section's own text, not the file's. The end marker of `TYP-3` goes before the break, which stays inside the frame of `TYP-1`.

```markdown
# a

## b

c

---

## d

e
```

```markdown
⟬TYP-1 begin⟭

# a ⟬TYP-2⟭

⟬TYP-3 begin⟭

## b ⟬TYP-4⟭

c ⟬TYP-5⟭

⟬TYP-3 end⟭

---

⟬TYP-6 begin⟭

## d ⟬TYP-7⟭

e ⟬TYP-8⟭

⟬TYP-6 end⟭

⟬TYP-1 end⟭
```

### E19. File (not GFM)

One marker, `⟬TYP⟭`, on the first line, with no end (R29): the file extends to its end. A search for `⟬TYP⟭` finds the file. The file's only child here is one section that covers all its text, yet the file is not collapsed with it (R27). The file has a prefix, not a number, and the section keeps `TYP-1`.

```markdown
# Types

Clean has a small set of built-in types.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Clean has a small set of built-in types. ⟬TYP-3⟭

⟬TYP-1 end⟭
```

### E20. Folder (not GFM)

Not annotated, and has no ID (R14): a folder is identified by its path, such as `specs/language/`. The annotated files of layer 2 keep the folder tree of the specs.

### E21. A container with a thematic break (R27)

A quote whose paragraph covers all but a thematic break keeps its own node: the break is not a `>` prefix or a blank line, so the paragraph does not cover the quote (R27). The break itself has no ID (E1).

```markdown
> a
>
> ***
```

```markdown
⟬TYP-1 begin⟭

> a ⟬TYP-2⟭
>
> ***

⟬TYP-1 end⟭
```

A section is different: its span ends with its last child (R16). Here the section of `# a` holds only its heading, since the break after it is not in its span, so it is collapsed into its heading (R27).

```markdown
# a

---
```

```markdown
# a ⟬TYP-1⟭

---
```

### E22. Section levels, and a heading in a quote (R1, R5)

A section opens at any heading level, 1 to 6, so `######` opens one inside the `#` section. A heading inside a block quote is an element of the quote and opens no section (R5). The section frames close innermost first.

```markdown
# Types

###### Six

Text.

> ## Note
>
> Quoted.
```

```markdown
⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

⟬TYP-3 begin⟭

###### Six ⟬TYP-4⟭

Text. ⟬TYP-5⟭

⟬TYP-6 begin⟭

> ## Note ⟬TYP-7⟭
>
> Quoted. ⟬TYP-8⟭

⟬TYP-6 end⟭

⟬TYP-3 end⟭

⟬TYP-1 end⟭
```

### E23. A file that starts with a blank line (R29)

Shown with the file marker. The blank first line is reused as the marker's blank line, so no other is added (R29, R30).

```markdown

x
```

```markdown
⟬TYP⟭

x ⟬TYP-1⟭
```

### E24. Marker lines inside a quote (R30)

A marker line inside a quote takes the quote's prefix, `> `, and its blank lines are bare `>` lines. Here the inner quote holds one paragraph of two lines, so it has one ID (R27), and that paragraph is framed (E8) inside the outer quote.

```markdown
> > a
> > b
>
> c
```

```markdown
⟬TYP-1 begin⟭

> ⟬TYP-2 begin⟭
>
> > a
> > b
>
> ⟬TYP-2 end⟭
>
> c ⟬TYP-3⟭

⟬TYP-1 end⟭
```
