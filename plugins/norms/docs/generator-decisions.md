# Generator decisions

Implementation notes of the layer 2 generator: how it does what the specs ask, where that does not change its output or its data. Everything that does (where IDs go, what is inserted, the tree, the hashes, matching, prefixes, numbering, statuses, the JSONL, the report, verify's checks) is in the specs, the one source of truth:

- `specs/norms-tree.md`: R1–R34, E1–E24, and the decisions of the user U1–U6 with their reasons.
- `specs/norms-annotation-cases.md`: R35–R52, E25–E68.
- `specs/norms-versions.md`: R53–R64, E69–E89.

The examples are the test fixtures: `tests/spec_examples.py` writes them under `tests/fixtures/`, and `tests/test_examples.py` checks that they still match the specs.

## Implementation notes

- **D1. Binding.** `cmarkgfm` exposes no AST to Python. The generator reaches the `cmark-gfm` library compiled inside it through `ctypes` (`cmark_parser_new`, `cmark_node_first_child`, `cmark_node_get_start_line`, …), so the parser is still the one R17 names. The parser, its extensions and the absence of footnotes are R17.
- **D2. Link reference definitions** are not AST nodes. The generator finds them in the gaps between blocks that the AST does not cover. What a definition's node is: R7, R41–R43.
- **D27c. Lazy similarity.** Stage C (R55) must yield the pairs of a full sort of every scored pair. The generator computes the ratios lazily, best upper bound first (the length bound, then the character bound, then the ratio), so a wording change across the whole corpus takes seconds, not tens of minutes. The result is the full sort's. Bounds and scores are exact fractions (`fractions.Fraction`), not floats: in floats a same-file ratio of 0.7 plus the bonus 0.1 is 0.7999999999999999 and would lose its tie with 0.8 across files (R55).
- **D30. Control characters.** cmark-gfm writes control characters (ESC, form feed) into its XML as they are, which XML forbids. The structure check replaces each with its Unicode control picture before reading the XML, on both sides, so a file holding them is checked, not crashed on.
- **D39. Probing.** Placements are probed one at a time on the whole file. When two of them still clash in the annotated file (R50), the nodes that cause it are found one top-level block at a time, and node by node inside the blocks that need it.
- **D40. One matching for renames.** The content nodes of every rename candidate are matched once, over all candidates (R58), not once per pair of files, so a folder moved whole takes seconds.
- **D45. The JSONL is written aside.** `write_store` encodes the whole JSONL first, writes it to `data/tree.jsonl.tmp` and moves it over `data/tree.jsonl`, so a failure never leaves a truncated JSONL. The order of the writes, and the refusal of a folder or a link at the `.tmp` path, is R62 and R34.

## Moved to the specs

Each decision taken during the implementation now lives in a spec. Its number stays here, pointing to where it went.

- D1 (parser and extensions) → R17, specs/norms-tree.md
- D3 → R9, specs/norms-tree.md; R57, E76, specs/norms-versions.md
- D4 → R33, E12, E14, specs/norms-tree.md
- D5 → R33, E10, specs/norms-tree.md; E54, specs/norms-annotation-cases.md
- D6 → R16, R31, specs/norms-tree.md
- D7 → R13, R31, specs/norms-tree.md
- D8 → R27, E21, specs/norms-tree.md
- D9 → R23, E10, specs/norms-tree.md
- D10 → R30, specs/norms-tree.md
- D11 → R30, E24, specs/norms-tree.md; R38, E39, specs/norms-annotation-cases.md
- D12 → R45, E55, specs/norms-annotation-cases.md
- D13 → R61, specs/norms-versions.md
- D14 → R62, specs/norms-versions.md; E20, specs/norms-tree.md
- D15 → R10, specs/norms-tree.md; R58, E78–E80, specs/norms-versions.md
- D16 → R26, U1, specs/norms-tree.md; R48, E61–E63, specs/norms-annotation-cases.md; R64, specs/norms-versions.md
- D17 → R35, R36, R38, E25–E31, E37, specs/norms-annotation-cases.md
- D18 → R15, specs/norms-tree.md; R59, E86, specs/norms-versions.md
- D19 → R30, U2, E13, specs/norms-tree.md
- D20 → R21, U3, specs/norms-tree.md; R60, E84, specs/norms-versions.md
- D21 → R39, E40–E43, specs/norms-annotation-cases.md
- D22 → R46, E57, E58, specs/norms-annotation-cases.md
- D23 → R41, R42, R44, E45–E47, E50, specs/norms-annotation-cases.md
- D24 → R36, E32, specs/norms-annotation-cases.md
- D25 → R45, E54–E56, specs/norms-annotation-cases.md
- D26 → R47, E59, E60, specs/norms-annotation-cases.md
- D27 (a, b) → R54, R56, E70, E71, specs/norms-versions.md; (c, the result) → R55, specs/norms-versions.md
- D28 → R58, E80, E82, specs/norms-versions.md
- D29 → R21, specs/norms-tree.md; R63, E85, E86, specs/norms-versions.md
- D31 → R24, specs/norms-tree.md; R49, E64, E65, specs/norms-annotation-cases.md; R64, specs/norms-versions.md
- D32 → R15, specs/norms-tree.md; R55, E72, specs/norms-versions.md
- D33 → R3, R34, specs/norms-tree.md
- D33 placement fixes → R35 and E29, E31; R43 and E49; R44 and E53; R45; R39 and E43; R47 and E60; R51 and E67, E68, specs/norms-annotation-cases.md
- D34 → R16, R31, specs/norms-tree.md
- D35 → R43, E48, E49, specs/norms-annotation-cases.md
- D36 → R44, E50–E53, specs/norms-annotation-cases.md
- D37 → R30, specs/norms-tree.md; R37, E35, E36, specs/norms-annotation-cases.md
- D38 → R40, E44, specs/norms-annotation-cases.md
- D39 (the check) → R24, specs/norms-tree.md; R50, E66, specs/norms-annotation-cases.md; R64, specs/norms-versions.md
- D40 (the rules) → R12, specs/norms-tree.md; R58, E81, specs/norms-versions.md
- D41 → R56, E83, specs/norms-versions.md
- D42 → R64, specs/norms-versions.md
- D43 → R19, R34, specs/norms-tree.md
- D44 → R34, specs/norms-tree.md; R61, R64, specs/norms-versions.md

## Spec changes settled

The spec changes proposed during the implementation are all in the specs. In every case the spec was corrected to match the generator.

- R26 and E5/E6 (unclosed blocks) → R26, U1, E6, the preamble of Elements; R48, E61–E63
- E12, E13, E16 (a tight list made loose) → R30, U2, E13, the preamble of Elements
- R21 and R31 (flags of one version) → R21, U3; R60, E84
- E12 / R24 (empty item) → R39, E40–E43
- E10 / R23 (inserted pipes) → R23, E10; R45, R46, E55, E57, E58
- E7 (definitions joined to text, a paragraph a table interrupts) → E7; R41, R44, E45, E50
- E11 (trailing blank `>` lines) → E11; R47, E59
- E15 / R24 (a task-like list on its parent's marker line) → R24; R36, E32
- R21 (a retired container's last text) → R21; R63, E85
- R24 / E12 (frames wider than their node) → R24, E12; R49, E64, E65
- R3 / R2 (UTF-8) → R3, R34
- R15 (similarity without line prefixes) → R15; R55, E72
- R27 (blank `>` lines, thematic breaks) → R27, E21
- R16 and D6 (spans start at the content column) → R16, R31
- E7 / R7 (definitions on lazy lines) → E7; R43, E48, E49
- R24 (the whole annotated file checked) → R24; R50, E66
- R12 (a file rewritten in place) → R12; R58, E81
- R19 / R3 (`⟬` and `⟭` refused) → R19, R34
- E6 / R26 (U1) → E6, R26, U1; R48, E62; R64
- E10 / R23 (no realignment) → E10, R23
- E10 (row IDs, short and long rows) → E10; R45, E54
- R23 (what is removed) → R23; R61, R64
- E3 and E11 fragments (E3b, E11b) → E3 and E11 numbered as files of their own, `TYP-1`
- E19 / R27 (the file never collapsed) → R27, E19
- E13 / E12 / E16 and the preamble of Elements → the preamble of Elements, E13
- E4 (which blank line keeps the code) → E4
- R30 (a blank before an inline ID) → R30; R37, R38, R39
- R18 / R24 / E12 (items whose first block is not a paragraph) → R24, E12; R35, E25–E30
- R5 / E18 (headings inside containers) → R5, E18, E22
- R1 (heading levels) → R1, E22
- R8 / R13 / R16 (ordinals, U4) → R8, U4; R59, E73, E75
- R13 / E10 (order of cells, U5) → R13, U5, E10; E74
- R15 / R21 (containers without information) → R15; R59, E86
- R17 (D1) → R17
- R9 / R10 / R12 / R14 (numbers and prefixes) → R9, R10, R12; R57, R58
- R31 / R16 (own text, tree hash) → R31
- R1 / E10 / E12 (shape of items and tables) → R1, R33
- R15 (matching stages) → R15; R53–R56
- R23 / R21 (the JSONL) → R23; R61, R63
