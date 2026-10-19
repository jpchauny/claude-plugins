# Norms Versions

**Status:** Draft
**Audience:** Whoever builds the layer 2 generator, and the agents that read its output

**Scope:** How the generator follows the nodes of foundation from one version to the next: matching, numbers and prefixes over time, statuses, the JSONL, the outputs, the change report and verify's checks

Each build reads foundation at one commit and the JSONL of the previous build, and gives every node of the new tree an ID. A node that is still there keeps its ID, even when it moved or was edited; a node that is gone is retired; a node that is new gets a number never given before. The build then records each ID's status for this one step, writes the JSONL, the annotated files and a report of what changed, and `verify` checks all of it. This document holds those requirements (R53–R64) and their examples (E69–E89). It builds on specs/norms-tree.md, which defines the tree, the IDs, the prefixes, the hashes and the annotation (R1–R34), and on specs/norms-annotation-cases.md, which places IDs in special cases (R35–R52). As there, the examples are requirements and test cases (R28).

## Requirements

### Matching

- **R53. Matching stages.** A new tree is matched against the previous JSONL in four stages. Each stage pairs only the nodes that the earlier ones left unpaired, and a retired node is never a candidate.
  - Two kinds of node are matched differently. The containers are sections, lists, block quotes, tables and rows: they follow their children (R56). In R53–R58, "container" has only this meaning. A file is neither a container nor a content node. The content nodes are every other node but files: headings, paragraphs, code and HTML blocks, definitions, items and table cells. An item is a content node, though it has children.
  - Two nodes are in the same file when the old node's file had the prefix that the new node's file has now (R12, R58).
  - A. Identical subtrees (R54).
  - B. Exact own text (R54). Partway through, it also pairs the containers whose paired children all agree (R54).
  - C. Similar text (R55).
  - D. Containers by their children, bottom-up, then the containers without children (R56).

  Then the new nodes left unpaired get new numbers (R57), and the old nodes left unpaired are retired. A file node's ID is its prefix, and it is paired by prefix (R58). The first run is the same process with an empty JSONL: every node is new. Examples: E69, E70.
- **R54. Identical subtrees and exact twins.**
  - Stage A pairs a new node that has children with an old active node of the same kind and tree hash, together with all their descendants. Larger subtrees are paired first.
  - Stage B pairs content nodes of the same kind and own hash, across all files (R11).
  - In stage B, texts that occur once among the free new nodes and once among the free old ones come first.
  - Then comes a pass over the containers, with the rules of R56 but for two: a container is paired only when its paired children all vote for one old container, and a container without children is not paired in this pass. A child votes for the old parent of the node it is paired with. Before that, each free section goes to the old section whose heading is the old node its own heading is paired with (R56).
  - Then come the repeated texts.
  - In stages A and B, every candidate pair is ranked at once, best first: same file, then same parent ID, then next to the same neighbour, then closest in order among the copies of that text in its file that are still free when the pass ranks them, then the old node that comes first in the previous JSONL's order, then the new node that comes first in pre-order over all files, the files in path order. In stage A, larger subtrees come before all of these. A node is next to the same neighbour when its sibling just before or after it is paired with the old node's sibling there.
  - Order is not byte offset: text inserted above two copies does not swap their IDs. A copy paired already, in an identical subtree or as a unique text, is not counted, so moving a quote that holds a third copy past two copies does not swap their IDs either.
  - So a copy elsewhere never takes the ID of an original that did not move. Examples: E71, E77.
- **R55. Similar text (stage C).**
  - The remaining content nodes of the same kind are paired by the ratio of `difflib.SequenceMatcher`, with `autojunk` off, over their own text. Every run of spaces, tabs and `>` that starts a line of the own text is removed before comparing: at the start of the text and after each line ending. This holds in every kind of node, so in a code or HTML block a `>` that starts a line is removed too, although it is content there: the lines `> run the build` and `run the build` compare as equal. Only the similarity sees this; the hashes keep every byte (R16).
  - The ratio must be at least 0.6. A pair in the same file ranks as if its ratio were 0.1 higher.
  - The ratio is `SequenceMatcher(None, new, old, autojunk=False).ratio()`, with the new node's text first. It is not symmetric, so the order counts.
  - Pairs are taken best first, as from a full sort of every scored pair. Ties go to the smaller byte distance between the two nodes' starts when they are in the same file (a pair across files comes after), then to the new node that comes first in pre-order over all files, the files in path order, then to the old node that comes first in the previous JSONL's order.
  - The similarity stored in the report is the ratio rounded to 4 decimals (0.8525). The threshold and the ranking use the ratio before rounding.
  - A node paired here whose own hash changed is `edited` and to review (R59). Hashes still cover the exact bytes (R16).
  - So a paragraph that leaves a quote of one paragraph, or moves to another nesting level, keeps its ID. Examples: E69, E72.
- **R56. Containers follow their children (stage D).**
  - Sections, lists, block quotes, tables and rows are paired bottom-up: the deepest first, and at one depth in pre-order. Each goes to an old container of its kind, not yet paired, that was the parent of most of its paired children.
  - Ties go, in order, to the same own hash, the same file, the same parent ID, the same neighbour (R54), the smaller byte distance between the two starts, and then the old container that comes first in the previous JSONL's order. So a list next to a paragraph that kept its ID takes the ID of the list that was next to it, even when another candidate is closer (E87).
  - A section goes first to the old section whose heading is the old node its own heading is paired with (R5). So a subsection added inside a section, whose paragraphs all come from that section while its heading is new, never takes the section's ID (E70).
  - A container none of whose children was paired gets a new ID.
  - A container without children, such as a quote of `>` alone or of a thematic break, is paired by kind and own hash, like a content node, so it keeps its ID when its text is still there in the next version (E83). It is paired last, after the bottom-up pass: stage B and the bottom-up pass never see it paired, so it casts no vote for its parent and is nobody's neighbour there. Its candidates are ranked as in R54: same file, same parent ID, same neighbour, then closest in order among the free childless containers of that kind and own hash in its file, not by byte distance, so text inserted above two copies of `> ***` does not swap their IDs. Then come the old container that comes first in the previous JSONL's order and the new one that comes first in pre-order.

### Numbers and prefixes over time

- **R57. Numbers are never reused.**
  - A node that is not paired with an old one (R53) takes the next number of its file's prefix: one more than the highest number ever given under that prefix, retired IDs included.
  - New nodes are numbered in pre-order, like the first run (R9).
  - A retired ID is never a candidate for pairing: text that comes back after it was removed gets a new ID.
  - Examples: E76, E70.
- **R58. Prefixes over time.** Content nodes are as in R53. How a new path chooses its prefix is R10.
  - **Candidates.** The old paths that vanished, the new paths, and each path present in both, holding content in both versions, at most half of whose new content nodes have an exact twin in its old content.
  - **One matching.** The candidates' content nodes are matched once, over all of them. The nodes are taken in path order, and in document order within a path.
    - First exact twins, of the same kind and own hash. For each text, the copies at one path pair with the copies at the same path, in document order. The copies left over pair in path and document order, the first old with the first new.
    - Then similar text among the rest, with R55's ratio and threshold, the same path ranking as if its ratio were 0.1 higher. Pairs are taken best first. Ties go to the old node that comes first, then to the new node that comes first, in that path and document order. Byte distance plays no part, unlike in R55.
  - **Renamed.** An old path is renamed to the new path that holds more than half of its active content nodes. The best fraction comes first. At an equal fraction, a path paired with itself wins, then the order of the paths. A renamed or moved file keeps its prefix (E78), and two files that swapped names swap prefixes (E79).
  - **No content.** A file without content nodes holds only blank lines, thematic breaks, and block quotes without children, such as `>` or `> ***`. It is paired with a new file without content nodes whose file node has the same own text, so the same own hash. The bytes of a childless quote are in the quote's own text, not the file's. So a file of `>` and one of `> ***` have the same file own text, a line ending, and they pair, although their bytes differ (E82).
  - **Replaced.** A path present in both and not paired with itself gets a new prefix only when it was renamed to another path, which holds more than half of its old content nodes (Renamed), or when none of its old content nodes is matched at that path, as with a new file put at the old path (E80). In the first case its old prefix goes with it to the path it was renamed to (Renamed, E79). In the second, it was renamed nowhere, and its old prefix is retired. Either way, it takes its new prefix as a new path does (R10).
  - **Not a candidate.** A path present in both that is not a candidate is paired with itself and keeps its prefix, without matching: a path without content nodes in one of the two versions, as a file emptied or an empty file filled in, and a path more than half of whose new content nodes have an exact twin in its old content. None of its content is matched to another path, and no other path's content to it.
  - **Rewritten in place.** Any other path present in both and not renamed from another path keeps its prefix: it was not renamed to another path, and some of its old content nodes are matched at that path, as with a stub filled in (E81). Some of its old content may have gone to other paths, as long as none of them holds more than half of it.
  - **Retired.** A prefix is retired when no current file holds it. So the prefix of a vanished file is retired unless a renamed file keeps it (E78, E79), the old prefix of a replaced path is retired unless a renamed file keeps it (E80), and so is every prefix used by a stored ID that is no current file's prefix. A retired prefix is never given again.

### Statuses

- **R59. Statuses.** Each ID has one status between two versions. The status is written in `data/report.json` (R63), not in the JSONL, whose own `status` field says only whether a node is `active` or `retired` (R61).
  - The statuses compare hashes: the own hash (R31), not the own text. For every node but a table they say the same, since its own hash is over its own text. A table's own hash takes its delimiter cells sorted, so a table whose columns moved has another own text but the same own hash (E74).
  - `edited`: its own hash changed. It is to review.
  - `child_changed`: its own hash is the same, but its tree hash changed.
  - A file, section, list or block quote whose own text changed only by blank lines, `>` prefixes and the blanks around them, or thematic breaks is `child_changed`, not `edited`: its own text holds no information. This holds even when none of its children changed, as when a blank line is added between two items (E86). Tables and rows are not covered: a change to their own hash makes them `edited`.
  - A BOM is not among those bytes. A file that gains or loses one is `edited` and to review (R31).
  - `moved`: the same own hash and tree hash, but another parent or another file.
  - "Another file" means a file of another prefix (R53): a node of a renamed file, which keeps its prefix, has not moved. A file node itself has moved when its path changed (E78).
  - `unchanged`, `new` and `retired`.
  - Each record also says `moved` (its parent or its file changed, in the sense above, whatever its status), `reordered` (a numbered list whose children changed order) and `changed_children`.
  - `changed_children` lists its direct children that came into it, that changed, or that left it. First come its new children, in source order, whose tree hash differs from the one they had under it; a child that came in from elsewhere is always listed, even with an unchanged tree hash (E77). Then come the old children that left it, in their old order (E85).
  - By U4, renumbered items are `edited` (R8, E73). By R8 and R13, reordering bullets changes nothing; by U5, neither does reordering rows or cells, nor moving a column with its delimiter cell (R31, E74), unless the move changes a cell's padding at an end of a row without a pipe (R13). Reordering a numbered list whose ordinals are equal makes it `child_changed` and `reordered` (E75).
- **R60. `to_review` and `changed_since` belong to one version (U3).**
  - `to_review` is true when the status is `edited`.
  - `changed_since` is the previous version's commit, the previous JSONL's `foundation_commit` (an empty string when it pins none), when the node's tree hash changed in this step, including a node retired in this step. Otherwise it is null. A new node and a node with the status `moved` have null. A node that moved and changed, with the flag `moved` and the status `edited`, has the commit (E72).
  - Both are computed again from scratch for each new version. Nothing is carried over: a node edited at the previous step and untouched at this one has no flag, and a node retired at an earlier step has none.
  - A rebuild is a build of the commit the previous JSONL pins: the previous JSONL holds at least one `file` line, and the full object name that `--commit` resolves to equals the stored `foundation_commit`, as strings (R61). A JSONL without `file` lines, which only a hand-made one is, gives no rebuild: every flag is computed again, and a retired ID's `changed_since` becomes null. `--commit HEAD`, a branch or a short SHA of that commit all give a rebuild. A meta line that holds a short SHA, or another name, is not a rebuild, though verify resolves it (R64). An ID whose status in the rebuild is `unchanged` keeps the `to_review` and `changed_since` it had, and an ID retired before the rebuild keeps its `changed_since`. With the same generator and the same `--specs-dir`, every ID is `unchanged`, and the rebuild leaves every output as it was when both reports exist (R62, R63); when one is missing, the next bullet but one applies.
  - A rebuild changed nothing when every ID's status is `unchanged`, whatever else differs, such as the generator version in the meta line or the insertions of a newer generator. It keeps both reports as they are. Its JSONL and annotated copies are written as this build makes them.
  - When either report is missing, a rebuild that changed nothing writes both again, from the stored version to the same one (``Foundation `c2` -> `c2`.``): every count but `unchanged` is 0, and `data/report.json` is empty.
  - A rebuild that changes an ID's status, as a newer generator or another `--specs-dir` may, computes the flags of the IDs it changes as any step does, against that same commit: an ID it retires has as `changed_since` the commit itself. Its report is written again, from the stored version to the new one (``Foundation `c2` -> `c2`.``), so it no longer shows the changes of the step that first built that commit, while the JSONL may still flag them.
  - Layer 3 learns what changed since the version it pinned by comparing that version's tree hashes with the new ones (R21, R31). Example: E84.

### Data and outputs

- **R61. The JSONL.** `data/tree.jsonl` holds one JSON object per line, with its keys sorted, no spaces between tokens, and non-ASCII characters written as they are. Each object has a `type`: `meta`, `file` or `node`. The lines, in order:
  - One `meta` line: `foundation_commit`, `generator_version`, and `retired_prefixes`, sorted. `foundation_commit` is the full object name, 40 lower-case hex digits in a SHA-1 repository, that `git rev-parse --verify --quiet <c>^{commit}` gives for `--commit` (R62). `generator_version` is the version of the Python package `norms-generator` that ran the build, as its `pyproject.toml` gives it (`0.1.0`).
  - One `file` line per file, by path: `path`, `prefix`, `sha256` of the foundation bytes, and `insertions` as `[offset, text]` pairs (R23). Offsets are byte offsets in the foundation file. There is one pair per offset, in ascending order of offset, and its text is everything inserted there, joined in the order it appears in the annotated file. `verify` compares this list as it is (R64).
  - One `node` line per active node, by file path, then in pre-order: `id`, `file`, `kind`, `parent` (null for a file), `start` and `end` as the byte offsets of the node's span, `end` exclusive (R16), `own_text`, `own_hash`, `tree_hash`, `status` (`active`), `to_review` and `changed_since` (R60).
  - `kind` is one of `file`, `section`, `heading`, `paragraph`, `code_block`, `html_block`, `link_ref_def`, `table`, `table_row`, `table_cell`, `block_quote`, `list` and `item`.
  - Retired nodes come last, by file path, then prefix, then number, with status `retired` and their last own text. They are never removed.
  - This `status` is only `active` or `retired`. The status of R59 (`edited`, `moved`, …) is in the report (R63).
  - Text is stored as the decoded UTF-8 string.
  - The next build reads this file as the previous version, parents included (R53), and verify reads it too (R64).
  - When reading it, these fields are required: `path` and `prefix` on a `file` line; `id`, `file`, `kind`, `start`, `end`, `own_text`, `own_hash` and `tree_hash` on a `node` line.
  - The other fields take a default when absent: an empty string for `foundation_commit`, `generator_version` and `sha256`; an empty list for `retired_prefixes` and `insertions`; null for `parent` and `changed_since`; `active` for `status`; false for `to_review`.
  - A field that is present must have its type and form. Strings are strings, and valid Unicode: an escape of a lone surrogate (`"\ud800"`) is valid JSON but not UTF-8, so it does not have the form, in any string of any line; `start`, `end` and offsets are integers of 0 or more; each insertion is an offset and a string; a prefix matches R10's form (three or more upper-case ASCII letters), and an ID and a parent are a prefix or a prefix, `-` and a number from 1, without leading zeros (`TYP-0` and `TYP-01` do not have the form); a `path` is relative and ends in `.md`, its parts separated by `/`, none of them empty, `.` or `..`, and none holding a control character (Unicode category Cc, a NUL or a line break among them), as git lists a foundation path that `build` accepts (R34) (`/x.md`, `../x.md` and `specs//a.md` do not have the form), so that a JSONL path never leads outside annotated/ (R62, R64); `kind` is one of the kinds above; `status` is `active` or `retired`; `to_review` is true or false.
  - A line that is not a JSON object, has another `type`, lacks a required field, or has a field of the wrong type or form makes the JSONL unreadable. `build` refuses it (R34), and `verify` reports it (R64). Both name the file and the line. A prefix or an ID followed by a line break does not have the form.
  - A line nested deeper than the reader can follow, as `[` written 100000 times and then `]` as often, is not a JSON object it can read either. Its error is Python's `RecursionError`, named as any other: `<path>:1: RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string`. `build` refuses it with status 2 (R34), and `verify` reports it with status 1 (R64), never as an unexpected error.
  - A name repeated in one object keeps its last value, and the earlier ones are not checked: `{"path":"../x.md","path":"specs/a.md",…}` reads as a `file` line for `specs/a.md`.
  - The tokens `NaN`, `Infinity` and `-Infinity` are not JSON (RFC 8259): a line that holds one is not a JSON object.
  - An empty line, or a line of only whitespace, is skipped wherever it is. Whitespace here is every character for which Python's `str.isspace()` is true: JSON's space, tab and carriage return, and also such characters as a form feed, U+001C to U+001F, U+00A0 and U+2028. Before or after a JSON object on a line, only JSON whitespace may stand. Lines are split at `\n` only, and a line may end in `\r`, so a JSONL with CRLF line endings reads as one with LF. A lone `\r` does not end a line: inside a line it is JSON whitespace, so two objects separated by a lone `\r` are one line that is not a JSON object.
  - The order of the lines is not checked when reading. A second `meta` line, or a second `file` line for one path, replaces the first: the last one wins. Two `node` lines with one ID, active or retired, are kept as they are: the JSONL reads, but it is not consistent, and `build` refuses it, as it refuses two files with one prefix, a retired prefix a file holds, and an active node whose file has no `file` line (R34); `verify` reports each (R64). Without a `meta` line, its fields take their defaults. A JSONL that is not UTF-8 is named with the offset of its first bad byte instead of a line (R34).
- **R62. Inputs and outputs.**
  - The command line is `norms-gen build --foundation <repo> [--commit <c>] [--specs-dir <d>] [--out <dir>]`, `norms-gen verify --foundation <repo> [--out <dir>]` and `norms-gen report [--out <dir>] [--json]`. `--commit` defaults to `HEAD`, and `--out`, the output folder, defaults to the root of the norms repository.
  - `report` prints `data/report.md`, or `data/report.json` with `--json`, byte for byte: CRLF and a lone CR in its texts stay as they are. When nothing at all is at that path, it prints ``no report at <path>; run `norms-gen build` first`` on standard error and exits with status 1. As for the JSONL (R34), nothing is there when the system finds no entry at the path, as also under a `data/` link that leads nowhere; a symbolic link at the path that leads nowhere or loops is something there. When it cannot be opened, as a folder or such a link at its path, a file without read permission, or a `data/` that cannot be searched, it prints `<path>: cannot be opened: <reason>` (`Is a directory`) on standard error and exits with status 1.
  - `--specs-dir` loses its trailing slashes, and `/` is added, so `specs`, `specs/` and `specs//` read the same folder. `.` reads every `.md` file of the repository. An empty, absolute or `..` path is passed to git, which rejects it (R34).
  - Foundation is read through git at one commit, never from its working tree: every regular `.md` file under the specs folder (`--specs-dir`, default `specs`), with its exact bytes. A regular file is a blob of mode `100644` or `100755`. A symbolic link (mode `120000`) and a submodule are left out, even with a name ending in `.md`, so a specs folder whose only `.md` is a link holds no `.md` file (R34). Paths are relative to the root of the foundation repository.
  - Under the output folder go `data/tree.jsonl` (R61), `data/report.md` and `data/report.json` (R63), and `annotated/<path>`. The JSONL is first written to `data/tree.jsonl.tmp`, then moved over `data/tree.jsonl`, so a failure never leaves a truncated JSONL; the move replaces a symbolic link at `data/tree.jsonl` and never writes through it. A file at `annotated/`, a symbolic link at `data/` or `annotated/`, and a folder or a symbolic link at `data/report.md`, `data/report.json` or `data/tree.jsonl.tmp`, is refused before anything is written; a file at `data/` is refused as a JSONL that cannot be opened (R34). The annotated copies: one annotated copy per foundation file, at the same relative path, so the folder tree of foundation is kept (E20). Paths that one file system would fold into one are refused (R34).
  - Every output is written as a new file, never into the file that stands at its path: the annotated copies, `data/report.md`, `data/report.json` and `data/tree.jsonl.tmp`, which is then moved over `data/tree.jsonl`. What stands at the path is removed first, then the file is created with an exclusive create, which fails rather than open a file that someone put there in between. So a hard link at an output path, a name that shares its bytes with another name inside or outside the output folder, as a file of foundation's working tree, is never written through: the other name keeps its bytes, and a build never writes anything outside the output folder, through a symbolic link or a hard link. An output is left as it is, when it already holds this build's bytes, only as a regular file with one name (one link); a file with more than one link is written anew whatever it holds, and a rebuild keeps its reports (R63) only when both are such files. So after a build no output shares its bytes with another name. A file without write permission is replaced as any other, since it is not written into; what the system refuses is the removal or the creation in its folder (below).
  - After every build, annotated/ holds exactly this build's annotated copies and the folders that hold them, and nothing else (U6). Before the copies are written, everything else under annotated/ is removed: a file that is no copy of this build, as the copy of a vanished file or one left by a build whose JSONL was lost; a folder that holds no copy of this build, with everything in it, as a folder left empty by a vanished copy; a folder at the path of a copy, with everything in it; a file at the path of a folder of copies; and every symbolic link under annotated/, wherever it stands and wherever it leads. A symbolic link is removed itself and never followed, so nothing behind it is touched, and a build never removes or writes anything outside the output folder through a link. A regular file at the path of a copy is that copy, written anew when its bytes differ or when it has more than one link (above). A name is kept only when it is, character for character, the name of a copy or of a folder of copies: a name that differs from it only in case or Unicode normalization is removed, and the copy is written under its own name. So a file and a folder may take each other's name from one version to the next (`specs/x.md` and `specs/x.md/b.md`), and a rebuild of the same commit removes these paths too. Then the copies are written, then the JSONL, then the reports.
  - A build is deterministic: with the same generator and the same `--specs-dir`, a rebuild of the same commit leaves every output byte for byte as it was, when both reports exist; when one is missing, both are written again (R60).
  - What `build` refuses is R34.
  - When the system refuses a read, a write, a creation or a removal under the output folder while `build` writes its outputs, as for a folder without write permission or one that cannot be searched, `build` stops there, prints `norms-gen: <path>: cannot be written: <reason>` (`Permission denied`) on standard error, the path being the one the system names, and exits with status 3: some outputs are written. The outputs written before it stay as they are, and the JSONL is the previous one or the new one, never a truncated one. An existing output it cannot read is replaced: it is not compared first. Fixing the permissions and building again finishes the build.
  - Messages: `build` prints ``built <n> files, <a> active nodes, <r> retired, at <commit>`` on standard output. `verify` prints each problem on a line of its own on standard error, worded as R64 lists them, a path under annotated/ with each control character written as R34 writes it (`\x0a`), so that no problem takes two lines, then ``verify: <n> problems``, also on standard error, and exits with status 1; when it finds none, it prints ``verify: <n> files, <a> active nodes, all sound`` on standard output. A refusal (R34), or a build stopped by the system (above), prints `norms-gen: ` and its message on standard error. `report`'s missing file is above.
  - Exit statuses, the same for every command:
    - 0: the command did what it was asked: `build` wrote its outputs, `verify` found no problem, `report` printed the report, or `--help` printed the usage.
    - 1: `verify` found a problem (R64), or `report` has no report to print, as nothing at its path or a report that cannot be opened (above). Nothing is written.
    - 2: `build` refused its input (R34), or the command line is wrong, as a missing `--foundation` or an unknown command, which prints the usage message on standard error. Nothing is written.
    - 3: the system stopped `build` part way (above). Some outputs are written, and the JSONL is the previous one or the new one.
    - 4: an unexpected error, one that no requirement words, as a defect of the generator or a failure of the system that the cases above do not cover. The command prints `norms-gen: unexpected error: <type>: <message>` on standard error, `<type>` being the name of the exception's class and `<message>` its text as Python's `str()` gives it (`norms-gen: unexpected error: RuntimeError: boom`), then the full Python stack trace (traceback), as Python prints one for an uncaught exception, also on standard error, so the defect can be found. What was written before it stays as it is, and the JSONL is the previous one or the new one.
    - A closed standard output, as with `norms-gen report | head -c 10`, whose reader stops reading before the command has written everything, is not an error either: the command stops writing to it, prints nothing about it, and exits with the status of what it did, 0 for `report`, and for `build` and for `verify`, which write to standard output only their last line, once their work is done.
    - An interrupt, as Ctrl-C (Python's `KeyboardInterrupt`), is not an error of the generator, and keeps Python's default behaviour: Python prints its traceback and the process ends by the interrupt signal (status 130 in a shell). As for status 3, the JSONL is the previous one or the new one.
- **R63. The change report.** Each build writes two reports, unless it is a rebuild of the same commit that changed nothing, every status `unchanged`, which keeps them when both exist (R60).
  - `data/report.md` starts with the title `# Changes`, then the line ``Foundation `<old>` -> `<new>`.``, where `<old>` is the previous JSONL's `foundation_commit`. When it pins none, `nothing (first run)` takes the old commit's place: on a first run, and for a previous JSONL whose `foundation_commit` is empty or absent, even when it holds files and nodes. Then come the counts per status, in the order `unchanged`, `moved`, `edited`, `child_changed`, `new`, `retired`.
  - Its sections are, in order, each only when it has an entry: `Edited (to review)`, `Changed below`, `Retired`, `New` and `Moved`. Each entry is headed `### <ID> (<kind>, <file>)`, with `<old file> -> <new file>` when the path of its file changed. That is a path, not a move: an edited paragraph of a renamed file is headed `(paragraph, specs/p.md -> specs/q.md)`, but has no `Moved:` line, since it has not moved (R59).
  - Within a section, entries come in the order of the change records: first the IDs of the new tree, in pre-order over all files, the files in path order; then the IDs retired in this step, in the previous JSONL's order. `data/report.json` lists its lines in that same order.
  - An entry's lines come in this order, each only when it applies: where it moved from, its changed children, `Children reordered.`, and then its texts.
  - A moved entry gives its old and new parent (`Parent TYP-1 -> TYP-5.`). An entry of another status that also moved says so (`Moved: parent TYP-1 -> TYP-5.`). A file has no parent, so a moved file gives its old and new path instead (`File specs/type-system.md -> specs/language/types.md.`, E78), and a file of another status that also moved says so with a lower-case `file` (`Moved: file specs/drafts/quote.md -> specs/later/quote.md.`, the `child_changed` file of E82's v4).
  - An edited entry gives its changed children, if any, then its similarity, then its old and new own text. Only a node paired by similar text has a similarity (R55). A table or row paired by its children (R56), or a file edited by its BOM, has none, and its entry has no `Similarity` line (E88).
  - A `Changed below` entry gives its changed children and `Children reordered.`, each when it applies, both when both do. When neither applies, as for a container whose tree hash changed while none of its children did, it gives its old and new own text (E86).
  - A retired entry gives its whole last text. A new entry gives only its own text, with its children's text cut out: a new file's entry may show only a line ending, and a new section's only its blank lines.
  - Texts are in fences of backticks with the info string `text`. A fence is its opening line (the backticks and `text`), then the text, then one line ending, then the closing backticks. So a text that ends with a line ending leaves an empty line before the closing fence, and a text that is only a line ending gives two empty lines (E82). A fence has three backticks, or one more than the longest run of backticks in its text, so a text that holds a fence keeps it: a text holding ```` ``` ```` is in a fence of four backticks.
  - A retired ID's last text is its own text with its children's text put back where their spans were, so a retired section shows what it said (R21, E85).
  - `data/report.json` holds one JSON line per ID that is not `unchanged`, with `id`, `status`, `kind`, `file`, `old_file`, `old_parent`, `new_parent`, `old_text`, `new_text`, `old_tree_hash`, `new_tree_hash`, `moved`, `reordered`, `changed_children`, `similarity` and `last_text`. Each line is written as the JSONL's are: keys sorted, no spaces between tokens, non-ASCII characters as they are, and `\n` after it (R61).
    - `status` is R59's; `kind` is R61's. `file` is the node's file now, and for a retired ID its last file. `old_file`, `old_parent`, `old_text` and `old_tree_hash` are those of the old node; `new_parent`, `new_text` and `new_tree_hash` those of the new one. Each is null where there is no such node: the `old_` fields of a new ID, the `new_` fields of a retired one. A parent is null for a file.
    - `old_text` and `new_text` are own texts, children cut out, for every kind, a `child_changed` container included, although report.md shows them only as R63 says.
    - `moved` and `reordered` are true or false (R59). `changed_children` is a list of IDs, empty when none. `similarity` is a number, the ratio rounded to 4 decimals, for a node paired by similar text (R55), and null otherwise. `last_text` is the whole last text of a retired ID, and null for every other.
  - Examples: E85, E86.

### Verify

- **R64. verify.** `verify` re-reads foundation at the commit pinned in the JSONL. It exits with status 1 when it finds a problem, and 0 when it finds none; an unexpected error exits with status 4 (R62). It checks:
  - that the JSONL exists and can be read (R61 says when a line cannot be read; a folder at its path, a file without read permission, or a symbolic link that leads nowhere or loops, cannot be opened, as R34 words it), and that the pinned commit exists. As in R34, the JSONL is absent only when the system finds no entry at its path, which is so too under a `data/` link that leads nowhere; a `data/` link that loops, or a file at `data/`, cannot be opened;
  - that each ID is stored once, active or retired, that no two files share a prefix, and that no retired prefix is a current file's (`build` refuses such a JSONL, R34);
  - that each active node's file is a `file` line of the JSONL;
  - for each file, that it exists in foundation at the pinned commit, that its annotated copy exists as a file (a folder or a symbolic link there, a file or a symbolic link at one of its folders under annotated/, or a symbolic link or a file at annotated/ itself, is a problem, not a copy) and can be read, that it has one name, as a build leaves it (a hard link, which shares its bytes with another name that could write there, is a problem; R62), and its `sha256`;
  - that annotated/ is a folder, and holds nothing but the copies of the JSONL's files and their folders (U6, R62);
  - that stripping the recorded insertions gives foundation back (R23);
  - that the inserted bytes are only markers, spaces, line endings, `>` and `|`: a tab is never inserted, since the tab of `-\t` is the source's (R38);
  - the markers: each matches R29's pattern, the file marker comes first, each ID appears once inline or as begin then end, and frames nest;
  - that the IDs in the annotated file are exactly the file's active nodes;
  - that the tree rebuilt from foundation has the stored nodes in pre-order, with the same kind, span, hashes and parent;
  - that annotating foundation again with the stored IDs gives the same bytes and the same insertions;
  - that the annotated file parses to foundation's blocks.

  The problems of the JSONL and of a file's presence are worded as follows; the first three stop verify, being the only problem it reports. Those of the JSONL's consistency are the ones `build` names when it refuses such a JSONL (R34), joined there by `; `. The problems of a file's content, from the `sha256` on, are worded by the check that finds them and name the file first.
  - ``<store>: no JSONL; run `norms-gen build` first``, when nothing at all is at `data/tree.jsonl`;
  - `cannot read the JSONL: <message>`, with R34's message for a JSONL that cannot be read;
  - `pinned commit '<c>' not in <repo>: <git's message, as R34 words it>`, `<c>` written as Python's `repr()` writes a string; an empty `foundation_commit` gives `pinned commit '' not in <repo>: '' is not a commit of <repo>`;
  - `<ID> is stored twice (<status> in <file>, <status> in <file>)`, the first line first;
  - `prefix <P> is used by <file> and <file>`, in path order;
  - `prefix <P> is retired but used by <file>`;
  - `<ID> is in <file>, which is not a JSONL file`;
  - `<path>: not in foundation at <commit>: <git's message, as R34 words it>`, the full object name of the pinned commit: `specs/b.md: not in foundation at <commit>: git cat-file blob <commit>:specs/b.md: fatal: path 'specs/b.md' does not exist in '<commit>'`;
  - `<path>: no annotated file at <annotated path>`, for a missing copy, a folder or a symbolic link;
  - `<path>: annotated file at <annotated path> cannot be opened: <reason>` (`Permission denied`), for a copy without read permission or under a folder that cannot be searched;
  - `<path>: annotated file at <annotated path> has <n> links; build writes it anew (U6)`, for a copy with more than one link, `<n>` being their number; the copy's content is then checked as any other's;
  - `<annotated path>: not an annotated copy of a JSONL file; build removes it (U6)`, for each path under annotated/ that is neither the path of a copy of a file of the JSONL nor the path of one of their folders, whatever stands there: a file, a folder, named once without what it holds, a symbolic link, never followed, or anything else. As R62 keeps names, a name that differs only in case or Unicode normalization is such a path. What stands at the path of a copy or of one of its folders and is not a copy or a folder is the `no annotated file` above, and is not named again;
  - `<annotated path>: cannot be opened: <reason>`, for annotated/ or a folder of copies under it whose names cannot be read;
  - `<annotated/>: a symbolic link; a build never writes outside the output folder through a link`, for a symbolic link at annotated/ itself, and `<annotated/>: not a folder`, for a file there, as `build` words its refusal of them (R34). The link is never followed, so nothing behind it is read, and each copy is then `no annotated file`.

  These last four come after the problems of the files, in the code point order of their paths. In each of them, a path is written with its control characters escaped as R34 writes them (`\x0a` for a line break), so that it stays on one line (R62). A foundation file that the JSONL does not hold is not checked.

  An annotated copy nested deeper than the parser can follow, as a line of 20000 `>`, does not parse to foundation's blocks, which never nest that deep since `build` parsed them: it is that problem, reported with the copy's other problems and those of every other file, never an unexpected error.

  The block comparison ignores list tightness (R30), paragraphs made only of markers, and inline markers in paragraphs, headings and cells. It tolerates only the end markers and blank lines at the end of an unclosed block (R26, R48). It does see a marker inside a code span, raw inline HTML, or a link's text or destination (E17), and it keeps the line breaks inside a paragraph or heading. Inside each line of a paragraph, heading or cell, it reads every run of white space, Unicode white space included, as one space, and drops the white space at both ends of the line (`a  b` reads as `a b`, `a b ` as `a b`). An inline ID with its blank leaves such a run once it is removed. So an extra space inserted inside a line of text would not be seen by this comparison.

## Examples

Each example is a sequence of foundation versions, built one after the other from an empty JSONL, as commits `c1`, `c2`, …: version k is commit `c<k>`. For each version it shows each foundation file and its annotated copy, with the file marker (R29) and the IDs the JSONL assigned. Under every version after the first, it lists the IDs whose status is not `unchanged`, or that carry a flag, with `to_review` and `changed_since` (R59, R60). An active ID not listed is `unchanged`, with no flag. An ID retired at an earlier step is not listed either: it keeps its status `retired` in the JSONL, with `changed_since` null (E76, E84). Every annotated block is the generator's exact output, and strips back to its foundation file (R23).

### E69. Edit

Under R15, R53, R55, R59 and R60. A paragraph is edited.

v1, `specs/type-system.md`:

```markdown
# Types

Numbers are always signed.

Strings are UTF-8.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Numbers are always signed. ⟬TYP-3⟭

Strings are UTF-8. ⟬TYP-4⟭

⟬TYP-1 end⟭
```

v2, `specs/type-system.md`:

```markdown
# Types

Numbers are always signed integers.

Strings are UTF-8.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Numbers are always signed integers. ⟬TYP-3⟭

Strings are UTF-8. ⟬TYP-4⟭

⟬TYP-1 end⟭
```

Statuses at v2:

- `TYP` (file): `child_changed`, changed children `TYP-1`, `changed_since` `c1`.
- `TYP-1` (section): `child_changed`, changed children `TYP-3`, `changed_since` `c1`.
- `TYP-3` (paragraph): `edited`, similarity 0.8525, `to_review`, `changed_since` `c1`.

`TYP-3` keeps its ID: it is paired by similar text (R55), and it is to review. Its section and its file hold a changed child. `TYP-2` and `TYP-4` are unchanged.

### E70. A subsection added

Under R56. A subsection is added inside a section, and takes two of its paragraphs.

v1, `specs/type-system.md`:

```markdown
# Types

Intro.

Integers wrap on overflow.

Floats are IEEE.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Intro. ⟬TYP-3⟭

Integers wrap on overflow. ⟬TYP-4⟭

Floats are IEEE. ⟬TYP-5⟭

⟬TYP-1 end⟭
```

v2, `specs/type-system.md`:

```markdown
# Types

Intro.

## Numbers

Integers wrap on overflow.

Floats are IEEE.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Intro. ⟬TYP-3⟭

⟬TYP-6 begin⟭

## Numbers ⟬TYP-7⟭

Integers wrap on overflow. ⟬TYP-4⟭

Floats are IEEE. ⟬TYP-5⟭

⟬TYP-6 end⟭

⟬TYP-1 end⟭
```

Statuses at v2:

- `TYP` (file): `child_changed`, changed children `TYP-1`, `changed_since` `c1`.
- `TYP-1` (section): `child_changed`, changed children `TYP-6`, `TYP-4`, `TYP-5`, `changed_since` `c1`.
- `TYP-6` (section): `new`, `changed_since` null.
- `TYP-7` (heading): `new`, `changed_since` null.
- `TYP-4` (paragraph): `moved`, parent `TYP-1` → `TYP-6`, `changed_since` null.
- `TYP-5` (paragraph): `moved`, parent `TYP-1` → `TYP-6`, `changed_since` null.

`TYP-1` stays the `#` section, since its heading `TYP-2` is paired with the old heading. The new `##` section takes a new ID, though all its paragraphs come from `TYP-1`. `TYP-4` and `TYP-5` keep their IDs and are moved.

### E71. Copies of one text

Under R54. A file holds two copies of one text, and a paragraph is inserted above both.

v1, `specs/type-system.md`:

```markdown
# Types

Run the build again.

Integers are signed.

Run the build again.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Run the build again. ⟬TYP-3⟭

Integers are signed. ⟬TYP-4⟭

Run the build again. ⟬TYP-5⟭

⟬TYP-1 end⟭
```

v2, `specs/type-system.md`:

```markdown
# Types

A new paragraph, inserted above both copies.

Run the build again.

Integers are signed.

Run the build again.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

A new paragraph, inserted above both copies. ⟬TYP-6⟭

Run the build again. ⟬TYP-3⟭

Integers are signed. ⟬TYP-4⟭

Run the build again. ⟬TYP-5⟭

⟬TYP-1 end⟭
```

Statuses at v2:

- `TYP` (file): `child_changed`, changed children `TYP-1`, `changed_since` `c1`.
- `TYP-1` (section): `child_changed`, changed children `TYP-6`, `changed_since` `c1`.
- `TYP-6` (paragraph): `new`, `changed_since` null.

The copies keep `TYP-3` and `TYP-5` in order, and neither is moved: order is not byte offset.

### E72. A paragraph that leaves a quote of one paragraph

Under R55. A quote of one paragraph has one ID, its paragraph's (R27). A second paragraph is added to the quote.

v1, `specs/type-system.md`:

```markdown
# Types

Intro.

> Integers never promote.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Intro. ⟬TYP-3⟭

> Integers never promote. ⟬TYP-4⟭

⟬TYP-1 end⟭
```

v2, `specs/type-system.md`:

```markdown
# Types

Intro.

> Integers never promote.
>
> Use an explicit cast.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Intro. ⟬TYP-3⟭

⟬TYP-5 begin⟭

> Integers never promote. ⟬TYP-4⟭
>
> Use an explicit cast. ⟬TYP-6⟭

⟬TYP-5 end⟭

⟬TYP-1 end⟭
```

Statuses at v2:

- `TYP` (file): `child_changed`, changed children `TYP-1`, `changed_since` `c1`.
- `TYP-1` (section): `child_changed`, changed children `TYP-5`, `TYP-4`, `changed_since` `c1`.
- `TYP-5` (block_quote): `new`, `changed_since` null.
- `TYP-4` (paragraph): `edited`, similarity 1.0, moved, parent `TYP-1` → `TYP-5`, `to_review`, `changed_since` `c1`.
- `TYP-6` (paragraph): `new`, `changed_since` null.

The paragraph keeps `TYP-4`. Its own text changed: at v1 the quote of one paragraph was collapsed into it (R27), so its own text was `> Integers never promote.`; at v2 the quote holds two paragraphs and keeps its `> ` prefixes, so the paragraph's own text is `Integers never promote.`. It is edited and to review, with similarity 1.0: the ratio ignores the `>` prefixes. The quote, now a container of two children, and the second paragraph are new.

### E73. Renumbering

Under R8 and R59 (U4). An item is inserted in a numbered list.

v1, `specs/build.md`:

```markdown
1. Parse the file.
2. Check the types.
3. Emit WebAssembly.
```

```markdown
⟬BUI⟭

⟬BUI-1 begin⟭

1. Parse the file. ⟬BUI-2⟭
2. Check the types. ⟬BUI-3⟭
3. Emit WebAssembly. ⟬BUI-4⟭

⟬BUI-1 end⟭
```

v2, `specs/build.md`:

```markdown
1. Parse the file.
2. Resolve the names.
3. Check the types.
4. Emit WebAssembly.
```

```markdown
⟬BUI⟭

⟬BUI-1 begin⟭

1. Parse the file. ⟬BUI-2⟭
2. Resolve the names. ⟬BUI-5⟭
3. Check the types. ⟬BUI-3⟭
4. Emit WebAssembly. ⟬BUI-4⟭

⟬BUI-1 end⟭
```

Statuses at v2:

- `BUI` (file): `child_changed`, changed children `BUI-1`, `changed_since` `c1`.
- `BUI-1` (list): `child_changed`, changed children `BUI-5`, `BUI-3`, `BUI-4`, `changed_since` `c1`.
- `BUI-5` (item): `new`, `changed_since` null.
- `BUI-3` (item): `edited`, similarity 0.9474, `to_review`, `changed_since` `c1`.
- `BUI-4` (item): `edited`, similarity 0.95, `to_review`, `changed_since` `c1`.

The later items are renumbered, so their own text changed: they are edited and to review. The list is `child_changed`, and not reordered.

### E74. Bullets, columns and cells reordered

Under R13 and R59: bullets have no order (R8), and neither have rows and cells (U5). The bullets are swapped, and so are the table's columns and cells. Each column moves with its delimiter cell, `:---` or `---:`, and the table's own hash takes those cells sorted, so the table's own text changes but not its own hash (R31). Its rows have pipes at both ends, so no cell's padding changes (R13).

v1, `specs/type-system.md`:

```markdown
- integer is 64 bits
- float is 64 bits

| Type | Size |
| :--- | ---: |
| integer | 64 bits |
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

- integer is 64 bits ⟬TYP-2⟭
- float is 64 bits ⟬TYP-3⟭

⟬TYP-1 end⟭

⟬TYP-4 begin⟭

| Type ⟬TYP-5⟭ | Size ⟬TYP-6⟭ |
| :--- | ---: |
| integer ⟬TYP-8⟭ | 64 bits ⟬TYP-9⟭ | ⟬TYP-7⟭ |

⟬TYP-4 end⟭
```

v2, `specs/type-system.md`:

```markdown
- float is 64 bits
- integer is 64 bits

| Size | Type |
| ---: | :--- |
| 64 bits | integer |
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

- float is 64 bits ⟬TYP-3⟭
- integer is 64 bits ⟬TYP-2⟭

⟬TYP-1 end⟭

⟬TYP-4 begin⟭

| Size ⟬TYP-6⟭ | Type ⟬TYP-5⟭ |
| ---: | :--- |
| 64 bits ⟬TYP-9⟭ | integer ⟬TYP-8⟭ | ⟬TYP-7⟭ |

⟬TYP-4 end⟭
```

Statuses at v2:

- None: every ID is `unchanged`, with no flag set.

No hash changes, so every ID is unchanged and no flag is set. The IDs follow their text: the header cell `Type` keeps `TYP-5` in its new column.

### E75. A numbered list reordered with equal ordinals

Under R8 and R59. A numbered list whose ordinals are all `1.` is reordered.

v1, `specs/build.md`:

```markdown
1. Parse the file.
1. Check the types.
```

```markdown
⟬BUI⟭

⟬BUI-1 begin⟭

1. Parse the file. ⟬BUI-2⟭
1. Check the types. ⟬BUI-3⟭

⟬BUI-1 end⟭
```

v2, `specs/build.md`:

```markdown
1. Check the types.
1. Parse the file.
```

```markdown
⟬BUI⟭

⟬BUI-1 begin⟭

1. Check the types. ⟬BUI-3⟭
1. Parse the file. ⟬BUI-2⟭

⟬BUI-1 end⟭
```

Statuses at v2:

- `BUI` (file): `child_changed`, changed children `BUI-1`, `changed_since` `c1`.
- `BUI-1` (list): `child_changed`, reordered, `changed_since` `c1`.

No item's own text changed, so the items are unchanged. The list is `child_changed` and `reordered`, with no changed children.

### E76. Numbers never reused

Under R57. Three versions: a subsection is removed, then the same text comes back.

v1, `specs/type-system.md`:

```markdown
# Types

Intro.

## Strings

Strings are UTF-8.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Intro. ⟬TYP-3⟭

⟬TYP-4 begin⟭

## Strings ⟬TYP-5⟭

Strings are UTF-8. ⟬TYP-6⟭

⟬TYP-4 end⟭

⟬TYP-1 end⟭
```

v2, `specs/type-system.md`:

```markdown
# Types

Intro.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Intro. ⟬TYP-3⟭

⟬TYP-1 end⟭
```

Statuses at v2:

- `TYP` (file): `child_changed`, changed children `TYP-1`, `changed_since` `c1`.
- `TYP-1` (section): `child_changed`, changed children `TYP-4`, `changed_since` `c1`.
- `TYP-4` (section): `retired`, `changed_since` `c1`.
- `TYP-5` (heading): `retired`, `changed_since` `c1`.
- `TYP-6` (paragraph): `retired`, `changed_since` `c1`.

v3, `specs/type-system.md`:

```markdown
# Types

Intro.

## Strings

Strings are UTF-8.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Intro. ⟬TYP-3⟭

⟬TYP-7 begin⟭

## Strings ⟬TYP-8⟭

Strings are UTF-8. ⟬TYP-9⟭

⟬TYP-7 end⟭

⟬TYP-1 end⟭
```

Statuses at v3:

- `TYP` (file): `child_changed`, changed children `TYP-1`, `changed_since` `c2`.
- `TYP-1` (section): `child_changed`, changed children `TYP-7`, `changed_since` `c2`.
- `TYP-7` (section): `new`, `changed_since` null.
- `TYP-8` (heading): `new`, `changed_since` null.
- `TYP-9` (paragraph): `new`, `changed_since` null.

At v2 the subsection, its heading and its paragraph are retired. At v3 the same text is new, as `TYP-7`, `TYP-8` and `TYP-9`: a retired ID is never a candidate, and its number is never given again. `TYP-4` to `TYP-6` stay retired, with no flag at v3.

### E77. A move to another file

Under R11 and R54. A paragraph moves to another file.

v1, `specs/type-system.md`:

```markdown
# Types

Intro.

Strings are UTF-8.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Intro. ⟬TYP-3⟭

Strings are UTF-8. ⟬TYP-4⟭

⟬TYP-1 end⟭
```

v1, `specs/syntax.md`:

```markdown
# Syntax

Blocks use tabs.
```

```markdown
⟬SYN⟭

⟬SYN-1 begin⟭

# Syntax ⟬SYN-2⟭

Blocks use tabs. ⟬SYN-3⟭

⟬SYN-1 end⟭
```

v2, `specs/type-system.md`:

```markdown
# Types

Intro.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Intro. ⟬TYP-3⟭

⟬TYP-1 end⟭
```

v2, `specs/syntax.md`:

```markdown
# Syntax

Blocks use tabs.

Strings are UTF-8.
```

```markdown
⟬SYN⟭

⟬SYN-1 begin⟭

# Syntax ⟬SYN-2⟭

Blocks use tabs. ⟬SYN-3⟭

Strings are UTF-8. ⟬TYP-4⟭

⟬SYN-1 end⟭
```

Statuses at v2:

- `SYN` (file): `child_changed`, changed children `SYN-1`, `changed_since` `c1`.
- `SYN-1` (section): `child_changed`, changed children `TYP-4`, `changed_since` `c1`.
- `TYP-4` (paragraph): `moved`, from `specs/type-system.md`, parent `TYP-1` → `SYN-1`, `changed_since` null.
- `TYP` (file): `child_changed`, changed children `TYP-1`, `changed_since` `c1`.
- `TYP-1` (section): `child_changed`, changed children `TYP-4`, `changed_since` `c1`.

`TYP-4` keeps its ID inside `syntax.md`, though its prefix is not that file's. Both sections and both files hold a changed child.

### E78. A file renamed and moved

Under R58. A file is renamed and moved to a folder, with the same bytes.

v1, `specs/type-system.md`:

```markdown
# Types

Numbers are signed.

Strings are UTF-8.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Numbers are signed. ⟬TYP-3⟭

Strings are UTF-8. ⟬TYP-4⟭

⟬TYP-1 end⟭
```

v2, `specs/language/types.md`:

```markdown
# Types

Numbers are signed.

Strings are UTF-8.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Numbers are signed. ⟬TYP-3⟭

Strings are UTF-8. ⟬TYP-4⟭

⟬TYP-1 end⟭
```

Statuses at v2:

- `TYP` (file): `moved`, from `specs/type-system.md`, `changed_since` null.

`data/report.md` at v2, without its `Foundation` line:

````markdown
# Changes

unchanged: 4, moved: 1, edited: 0, child_changed: 0, new: 0, retired: 0

## Moved

### TYP (file, specs/type-system.md -> specs/language/types.md)

File specs/type-system.md -> specs/language/types.md.
````

The file keeps `TYP`: its node is moved, every other ID is unchanged, and no prefix is retired. A file has no parent, so its moved entry gives its old and new path (R63).

### E79. Two files that swapped names

Under R58. Two files swap their contents, which is a swap of names.

v1, `specs/alpha.md`:

```markdown
# Alpha

Alpha one.

Alpha two.
```

```markdown
⟬ALP⟭

⟬ALP-1 begin⟭

# Alpha ⟬ALP-2⟭

Alpha one. ⟬ALP-3⟭

Alpha two. ⟬ALP-4⟭

⟬ALP-1 end⟭
```

v1, `specs/beta.md`:

```markdown
# Beta

Beta one.

Beta two.
```

```markdown
⟬BET⟭

⟬BET-1 begin⟭

# Beta ⟬BET-2⟭

Beta one. ⟬BET-3⟭

Beta two. ⟬BET-4⟭

⟬BET-1 end⟭
```

v2, `specs/alpha.md`:

```markdown
# Beta

Beta one.

Beta two.
```

```markdown
⟬BET⟭

⟬BET-1 begin⟭

# Beta ⟬BET-2⟭

Beta one. ⟬BET-3⟭

Beta two. ⟬BET-4⟭

⟬BET-1 end⟭
```

v2, `specs/beta.md`:

```markdown
# Alpha

Alpha one.

Alpha two.
```

```markdown
⟬ALP⟭

⟬ALP-1 begin⟭

# Alpha ⟬ALP-2⟭

Alpha one. ⟬ALP-3⟭

Alpha two. ⟬ALP-4⟭

⟬ALP-1 end⟭
```

Statuses at v2:

- `BET` (file): `moved`, from `specs/beta.md`, `changed_since` null.
- `ALP` (file): `moved`, from `specs/alpha.md`, `changed_since` null.

Each prefix follows its content: `alpha.md` now has `BET` and `beta.md` has `ALP`. Both file nodes are moved; every other ID is unchanged.

### E80. A file replaced at its path

Under R58. A new file is put at the path of an old one, with none of its content.

v1, `specs/type-system.md`:

```markdown
# Types

Integers are signed.

Floats are IEEE.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Integers are signed. ⟬TYP-3⟭

Floats are IEEE. ⟬TYP-4⟭

⟬TYP-1 end⟭
```

v2, `specs/type-system.md`:

```markdown
# Glossary

A word list of terms used by the compiler.

Nothing else.
```

```markdown
⟬STY⟭

⟬STY-1 begin⟭

# Glossary ⟬STY-2⟭

A word list of terms used by the compiler. ⟬STY-3⟭

Nothing else. ⟬STY-4⟭

⟬STY-1 end⟭
```

Statuses at v2:

- `STY` (file): `new`, `changed_since` null.
- `STY-1` (section): `new`, `changed_since` null.
- `STY-2` (heading): `new`, `changed_since` null.
- `STY-3` (paragraph): `new`, `changed_since` null.
- `STY-4` (paragraph): `new`, `changed_since` null.
- `TYP` (file): `retired`, `changed_since` `c1`.
- `TYP-1` (section): `retired`, `changed_since` `c1`.
- `TYP-2` (heading): `retired`, `changed_since` `c1`.
- `TYP-3` (paragraph): `retired`, `changed_since` `c1`.
- `TYP-4` (paragraph): `retired`, `changed_since` `c1`.

`retired_prefixes`: `TYP`.

None of the old content nodes is matched, so the path gets a new prefix, `STY`, and `TYP` is retired: every old ID is retired and every new one is new. `TYP` would be the first candidate, but a retired prefix is never given again (R10).

### E81. A stub filled in

Under R58. A stub is filled in.

v1, `specs/memory.md`:

```markdown
# Memory

To be written.
```

```markdown
⟬MEM⟭

⟬MEM-1 begin⟭

# Memory ⟬MEM-2⟭

To be written. ⟬MEM-3⟭

⟬MEM-1 end⟭
```

v2, `specs/memory.md`:

```markdown
# Memory

Values are reference counted and freed when the count reaches zero.
```

```markdown
⟬MEM⟭

⟬MEM-1 begin⟭

# Memory ⟬MEM-2⟭

Values are reference counted and freed when the count reaches zero. ⟬MEM-4⟭

⟬MEM-1 end⟭
```

Statuses at v2:

- `MEM` (file): `child_changed`, changed children `MEM-1`, `changed_since` `c1`.
- `MEM-1` (section): `child_changed`, changed children `MEM-4`, `MEM-3`, `changed_since` `c1`.
- `MEM-4` (paragraph): `new`, `changed_since` null.
- `MEM-3` (paragraph): `retired`, `changed_since` `c1`.

The heading `# Memory` (`MEM-2`) has an exact twin at `specs/memory.md` in v2, so some of the path's old content is matched there, and none went to another path: the file is rewritten in place and keeps `MEM` (R58). In E80, by contrast, none of the old content is matched at the path, and it gets a new prefix. The new paragraph is too different to pair with the old one: `MEM-3` is retired and `MEM-4` is new.

### E82. An empty file moved

Under R58. An empty file is moved to another folder. Then a file of a childless quote is moved, and its quote changes.

v1, `specs/type-system.md`:

```markdown
# Types

A.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

A. ⟬TYP-3⟭

⟬TYP-1 end⟭
```

v1, `specs/drafts/placeholder.md`:

```markdown
```

```markdown
⟬PLA⟭
```

v2, `specs/type-system.md`:

```markdown
# Types

A.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

A. ⟬TYP-3⟭

⟬TYP-1 end⟭
```

v2, `specs/later/placeholder.md`:

```markdown
```

```markdown
⟬PLA⟭
```

Statuses at v2:

- `PLA` (file): `moved`, from `specs/drafts/placeholder.md`, `changed_since` null.

The file has no content nodes, so it is paired with the new file without content nodes whose file node has the same own text, here the empty text. It keeps `PLA`, and its node is moved. Its annotated copy holds only its marker (R29).

v3 adds `specs/drafts/quote.md`, which holds only a quote without children. The quote is not a content node, so the file has no content nodes either.

v3, `specs/type-system.md`:

```markdown
# Types

A.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

A. ⟬TYP-3⟭

⟬TYP-1 end⟭
```

v3, `specs/drafts/quote.md`:

```markdown
>
```

```markdown
⟬QUO⟭

⟬QUO-1 begin⟭

>

⟬QUO-1 end⟭
```

v3, `specs/later/placeholder.md`:

```markdown
```

```markdown
⟬PLA⟭
```

Statuses at v3:

- `QUO` (file): `new`, `changed_since` null.
- `QUO-1` (block_quote): `new`, `changed_since` null.

`data/report.md` at v3, without its `Foundation` line:

````markdown
# Changes

unchanged: 5, moved: 0, edited: 0, child_changed: 0, new: 2, retired: 0

## New

### QUO (file, specs/drafts/quote.md)

```text


```

### QUO-1 (block_quote, specs/drafts/quote.md)

```text
>
```
````

A new entry gives only its own text (R63). The file's own text is the line ending after `>`, so its fence holds that line ending and then the fence's own one: two empty lines (R63).

In v4 the file moves to `specs/later/quote.md`, and its quote becomes `> ***`.

v4, `specs/type-system.md`:

```markdown
# Types

A.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

A. ⟬TYP-3⟭

⟬TYP-1 end⟭
```

v4, `specs/later/placeholder.md`:

```markdown
```

```markdown
⟬PLA⟭
```

v4, `specs/later/quote.md`:

```markdown
> ***
```

```markdown
⟬QUO⟭

⟬QUO-2 begin⟭

> ***

⟬QUO-2 end⟭
```

Statuses at v4:

- `QUO` (file): `child_changed`, moved from `specs/drafts/quote.md`, changed children `QUO-2`, `QUO-1`, `changed_since` `c3`.
- `QUO-2` (block_quote): `new`, `changed_since` null.
- `QUO-1` (block_quote): `retired`, `changed_since` `c3`.

The bytes of the two files differ, but the bytes of each quote are in the quote's own text. The file's own text is a line ending in both, so the two files pair and the new one keeps `QUO` (R58). The quotes do not pair: their own texts differ, and a quote without children is paired only by kind and own hash (R56). So `QUO-1` is retired and `QUO-2` is new.

### E83. A childless quote in the next version

Under R56. A quote holds only a thematic break, so it has no children. The same bytes are committed again as `c2` and built: a new version, not a rebuild of the same commit (R60).

v1, `specs/notes.md`:

```markdown
Intro.

> ***

Text.
```

```markdown
⟬NOT⟭

Intro. ⟬NOT-1⟭

⟬NOT-2 begin⟭

> ***

⟬NOT-2 end⟭

Text. ⟬NOT-3⟭
```

v2, `specs/notes.md`:

```markdown
Intro.

> ***

Text.
```

```markdown
⟬NOT⟭

Intro. ⟬NOT-1⟭

⟬NOT-2 begin⟭

> ***

⟬NOT-2 end⟭

Text. ⟬NOT-3⟭
```

Statuses at v2:

- None: every ID is `unchanged`, with no flag set.

The quote is paired by kind and own hash, like a content node, so `c2` keeps `NOT-2`. Every ID is unchanged.

### E84. The flags of one version

Under R60 (U3). Three versions: a paragraph is edited and another removed, then a paragraph is added.

v1, `specs/type-system.md`:

```markdown
# Types

Numbers are always signed.

Strings are UTF-8.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Numbers are always signed. ⟬TYP-3⟭

Strings are UTF-8. ⟬TYP-4⟭

⟬TYP-1 end⟭
```

v2, `specs/type-system.md`:

```markdown
# Types

Numbers are always signed integers.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Numbers are always signed integers. ⟬TYP-3⟭

⟬TYP-1 end⟭
```

Statuses at v2:

- `TYP` (file): `child_changed`, changed children `TYP-1`, `changed_since` `c1`.
- `TYP-1` (section): `child_changed`, changed children `TYP-3`, `TYP-4`, `changed_since` `c1`.
- `TYP-3` (paragraph): `edited`, similarity 0.8525, `to_review`, `changed_since` `c1`.
- `TYP-4` (paragraph): `retired`, `changed_since` `c1`.

v3, `specs/type-system.md`:

```markdown
# Types

Numbers are always signed integers.

Floats are IEEE 754.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Numbers are always signed integers. ⟬TYP-3⟭

Floats are IEEE 754. ⟬TYP-5⟭

⟬TYP-1 end⟭
```

Statuses at v3:

- `TYP` (file): `child_changed`, changed children `TYP-1`, `changed_since` `c2`.
- `TYP-1` (section): `child_changed`, changed children `TYP-5`, `changed_since` `c2`.
- `TYP-5` (paragraph): `new`, `changed_since` null.

At v2, `TYP-3` is to review and four IDs changed since `c1`. At v3, only the new paragraph's parents changed, since `c2`. `TYP-3` has no flag: nothing is carried over from v2. Retired `TYP-4` has `changed_since` null, since it was retired in an earlier step.

### E85. A retired section in the report

Under R63. A file loses its sections and keeps one paragraph.

v1, `specs/type-system.md`:

```markdown
# Types

Integers are signed.

## Int

Integers.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Integers are signed. ⟬TYP-3⟭

⟬TYP-4 begin⟭

## Int ⟬TYP-5⟭

Integers. ⟬TYP-6⟭

⟬TYP-4 end⟭

⟬TYP-1 end⟭
```

v2, `specs/type-system.md`:

```markdown
Integers.
```

```markdown
⟬TYP⟭

Integers. ⟬TYP-6⟭
```

Statuses at v2:

- `TYP` (file): `child_changed`, changed children `TYP-6`, `TYP-1`, `changed_since` `c1`.
- `TYP-6` (paragraph): `moved`, parent `TYP-4` → `TYP`, `changed_since` null.
- `TYP-1` (section): `retired`, `changed_since` `c1`.
- `TYP-2` (heading): `retired`, `changed_since` `c1`.
- `TYP-3` (paragraph): `retired`, `changed_since` `c1`.
- `TYP-4` (section): `retired`, `changed_since` `c1`.
- `TYP-5` (heading): `retired`, `changed_since` `c1`.

`data/report.md` at v2, without its `Foundation` line:

````markdown
# Changes

unchanged: 0, moved: 1, edited: 0, child_changed: 1, new: 0, retired: 5

## Changed below

### TYP (file, specs/type-system.md)

Children changed: TYP-6, TYP-1.


## Retired

### TYP-1 (section, specs/type-system.md)

Last text:

```text
# Types

Integers are signed.

## Int

Integers.
```

### TYP-2 (heading, specs/type-system.md)

Last text:

```text
# Types
```

### TYP-3 (paragraph, specs/type-system.md)

Last text:

```text
Integers are signed.
```

### TYP-4 (section, specs/type-system.md)

Last text:

```text
## Int

Integers.
```

### TYP-5 (heading, specs/type-system.md)

Last text:

```text
## Int
```


## Moved

### TYP-6 (paragraph, specs/type-system.md)

Parent TYP-4 -> TYP.
````

The retired section `TYP-1` shows its whole last text, its children's text put back. The `Foundation` line, which here would read ``Foundation `c1` -> `c2`.``, follows the title in the real report (R63).

### E86. A list turned loose

Under R59 and R63. A blank line is added between two items, so the list turns loose.

v1, `specs/type-system.md`:

```markdown
# L

- one
- two
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# L ⟬TYP-2⟭

⟬TYP-3 begin⟭

- one ⟬TYP-4⟭
- two ⟬TYP-5⟭

⟬TYP-3 end⟭

⟬TYP-1 end⟭
```

v2, `specs/type-system.md`:

```markdown
# L

- one

- two
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# L ⟬TYP-2⟭

⟬TYP-3 begin⟭

- one ⟬TYP-4⟭

- two ⟬TYP-5⟭

⟬TYP-3 end⟭

⟬TYP-1 end⟭
```

Statuses at v2:

- `TYP` (file): `child_changed`, changed children `TYP-1`, `changed_since` `c1`.
- `TYP-1` (section): `child_changed`, changed children `TYP-3`, `changed_since` `c1`.
- `TYP-3` (list): `child_changed`, `changed_since` `c1`.

`data/report.md` at v2, without its `Foundation` line:

````markdown
# Changes

unchanged: 3, moved: 0, edited: 0, child_changed: 3, new: 0, retired: 0

## Changed below

### TYP (file, specs/type-system.md)

Children changed: TYP-1.

### TYP-1 (section, specs/type-system.md)

Children changed: TYP-3.

### TYP-3 (list, specs/type-system.md)

Own text changed (blank lines, `>` prefixes and the blanks around them, or thematic breaks only):

Old:

```text


```

New:

```text



```
````

Only the list's own text changed, by a blank line: it is `child_changed`, not edited, with no changed children. Its report entry shows its old and new own text. No item is edited.

### E87. A list that follows its neighbour

Under R56. A paragraph is added at the top of the section, the first item of the first list and the last item of the second are removed, and the paragraph between the lists moves after them. The new list holds `beta two` and `gamma three`, one item from each old list.

v1, `specs/type-system.md`:

```markdown
# Types

Numbers are signed.

- alpha one
- beta two

Strings are UTF-8 and every string is a sequence of bytes that holds valid text, always.

- gamma three
- delta four
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

Numbers are signed. ⟬TYP-3⟭

⟬TYP-4 begin⟭

- alpha one ⟬TYP-5⟭
- beta two ⟬TYP-6⟭

⟬TYP-4 end⟭

Strings are UTF-8 and every string is a sequence of bytes that holds valid text, always. ⟬TYP-7⟭

⟬TYP-8 begin⟭

- gamma three ⟬TYP-9⟭
- delta four ⟬TYP-10⟭

⟬TYP-8 end⟭

⟬TYP-1 end⟭
```

v2, `specs/type-system.md`:

```markdown
# Types

A new paragraph comes first now, long enough to move every later block far down the file.

Numbers are signed.

- beta two
- gamma three

Strings are UTF-8 and every string is a sequence of bytes that holds valid text, always.
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

# Types ⟬TYP-2⟭

A new paragraph comes first now, long enough to move every later block far down the file. ⟬TYP-11⟭

Numbers are signed. ⟬TYP-3⟭

⟬TYP-4 begin⟭

- beta two ⟬TYP-6⟭
- gamma three ⟬TYP-9⟭

⟬TYP-4 end⟭

Strings are UTF-8 and every string is a sequence of bytes that holds valid text, always. ⟬TYP-7⟭

⟬TYP-1 end⟭
```

Statuses at v2:

- `TYP` (file): `child_changed`, changed children `TYP-1`, `changed_since` `c1`.
- `TYP-1` (section): `child_changed`, changed children `TYP-11`, `TYP-4`, `TYP-8`, `changed_since` `c1`.
- `TYP-11` (paragraph): `new`, `changed_since` null.
- `TYP-4` (list): `child_changed`, changed children `TYP-9`, `TYP-5`, `changed_since` `c1`.
- `TYP-9` (item): `moved`, parent `TYP-8` → `TYP-4`, `changed_since` null.
- `TYP-5` (item): `retired`, `changed_since` `c1`.
- `TYP-8` (list): `retired`, `changed_since` `c1`.
- `TYP-10` (item): `retired`, `changed_since` `c1`.

Each old list gets one vote, and both have the same own text, file and parent. The old list `TYP-8` starts closer to the new list in bytes, but `TYP-4` was next to `Numbers are signed.`, which kept `TYP-3` and is still next to the new list. The same neighbour comes before the byte distance, so the new list keeps `TYP-4` and `TYP-8` is retired. Its changed children are `TYP-9`, which came in, then `TYP-5`, which left (R59).

### E88. An edited row

Under R56, R59 and R63. The last row loses its closing pipe.

v1, `specs/type-system.md`:

```markdown
| Type | Size |
|---|---|
| int | 64 |
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

| Type ⟬TYP-2⟭ | Size ⟬TYP-3⟭ |
|---|---|
| int ⟬TYP-5⟭ | 64 ⟬TYP-6⟭ | ⟬TYP-4⟭ |

⟬TYP-1 end⟭
```

v2, `specs/type-system.md`:

```markdown
| Type | Size |
|---|---|
| int | 64
```

```markdown
⟬TYP⟭

⟬TYP-1 begin⟭

| Type ⟬TYP-2⟭ | Size ⟬TYP-3⟭ |
|---|---|
| int ⟬TYP-5⟭ | 64 ⟬TYP-6⟭ | ⟬TYP-4⟭

⟬TYP-1 end⟭
```

Statuses at v2:

- `TYP` (file): `child_changed`, changed children `TYP-1`, `changed_since` `c1`.
- `TYP-1` (table): `child_changed`, changed children `TYP-4`, `changed_since` `c1`.
- `TYP-4` (table_row): `edited`, changed children `TYP-6`, `to_review`, `changed_since` `c1`.
- `TYP-6` (table_cell): `edited`, similarity 0.8, `to_review`, `changed_since` `c1`.

`data/report.md` at v2, without its `Foundation` line:

````markdown
# Changes

unchanged: 3, moved: 0, edited: 2, child_changed: 2, new: 0, retired: 0

## Edited (to review)

### TYP-4 (table_row, specs/type-system.md)

Children changed: TYP-6.

Old:

```text
|||
```

New:

```text
||
```

### TYP-6 (table_cell, specs/type-system.md)

Similarity 0.8.

Old:

```text
 64 
```

New:

```text
 64
```


## Changed below

### TYP (file, specs/type-system.md)

Children changed: TYP-1.

### TYP-1 (table, specs/type-system.md)

Children changed: TYP-4.
````

The row's own text changed from `|||` to `||`, so it is edited. It was paired by its children, not by similar text, so it has no similarity, and its report entry has no `Similarity` line. Its entry lists its changed child first. The cell lost its padding space and was paired by similar text (R55).

### E89. Two similar texts at the same ratio

Under R55. Two paragraphs differ only in their last word, and the new paragraph is as similar to both: its ratio is 0.8235 with each.

v1, `specs/type-system.md`:

```markdown
The limit is one.

# Notes

Floats are IEEE.

The limit is two.
```

```markdown
⟬TYP⟭

The limit is one. ⟬TYP-1⟭

⟬TYP-2 begin⟭

# Notes ⟬TYP-3⟭

Floats are IEEE. ⟬TYP-4⟭

The limit is two. ⟬TYP-5⟭

⟬TYP-2 end⟭
```

v2, `specs/type-system.md`:

```markdown
# Notes

The limit is six.

Floats are IEEE.
```

```markdown
⟬TYP⟭

⟬TYP-2 begin⟭

# Notes ⟬TYP-3⟭

The limit is six. ⟬TYP-1⟭

Floats are IEEE. ⟬TYP-4⟭

⟬TYP-2 end⟭
```

Statuses at v2:

- `TYP` (file): `child_changed`, changed children `TYP-2`, `TYP-1`, `changed_since` `c1`.
- `TYP-2` (section): `child_changed`, changed children `TYP-1`, `TYP-5`, `changed_since` `c1`.
- `TYP-1` (paragraph): `edited`, similarity 0.8235, moved, parent `TYP` → `TYP-2`, `to_review`, `changed_since` `c1`.
- `TYP-5` (paragraph): `retired`, `changed_since` `c1`.

The tie goes to the smaller byte distance in the same file. The new paragraph starts at byte 9; `TYP-1` started at byte 0 and `TYP-5` at byte 46. So it keeps `TYP-1`, which also moved into the section, and `TYP-5` is retired.
