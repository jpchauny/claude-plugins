---
name: derive-grammar
description: Derive the Lark grammar of Clean in specs-derived/grammar/ of the repository of layer 2, from its Clean examples (the clean-language fragments of data/tree.jsonl) and the prose norms they need - every statement citing its norms, only what changed derived again, the case of each fragment from its opening line, gaps marked pending and opened at once as issues in layer 1, then seal and check. Run by /norms-management:build as the generator of the type grammar, or by the user typing /clean-derived-norms:derive-grammar.
---

# derive-grammar

Implements [specs/derive-grammar.md](specs/derive-grammar.md) (DGR), with the
rules of the module, CDN-1 to CDN-7, in [module.md](../../specs/module.md),
and the interface of a derived-norms generator, NRM-1 to NRM-11, of the plugin
`norms-management`. Each step below names the rule it follows.

Two parts. The script does what is deterministic: the work list, the case of
each fragment, the meta line and the checks. You, the deriver, write the
statements of the grammar and the status lines. The script never writes a
statement and never decides a state.

Run everything from the root of the repository of layer 2, the working
directory. The script is

```sh
S="${CLAUDE_PLUGIN_ROOT}/use-cases/derive-grammar/derive_grammar.py"
uv run --with "lark[interegular]" python3 -I -B "$S" <command>
```

It imports the module script, the code that it shares with the script of
`derive-semantics` (CDN-7 (The script of each use case of this module
imports the module script, and no script of a use case imports the script
of another use case)); the snippets below load it as `m`:

```sh
M="${CLAUDE_PLUGIN_ROOT}/scripts/derived_norms.py"
```

What you read and write (DGR-1 (The use case reads only layer 2 (NRM-3), and
writes in the repository only under specs-derived/grammar/), DGR-3 (The output
is one grammar and one status file under specs-derived/grammar/)):

- Read `data/tree.jsonl` and, when you need the context of a norm,
  `specs-repo-annotated/`. Never read a file of the foundation. For the old
  text of a stale cited norm, `stale-citations` reads the versions of
  `data/tree.jsonl` in the history of HEAD.
- Write only `specs-derived/grammar/clean.lark` (the grammar) and
  `specs-derived/grammar/clean-language-code-examples-status.jsonl` (the
  status file), plus your work files in the scratchpad (the work list, the
  titles, bodies and comments of issues, and the record of the issues).
  Outside the repository, during the run: in
  `Ivan-Pasco/clean-language-foundation`, the issue of each pending fragment,
  a comment on an open duplicate, the labels it lacks, and the edit that
  writes each issue's number in its body (DGR-14); in
  `jpchauny/claude-plugins`, the same for each stale cited norm of the script
  (DGR-18). Nothing else goes in `specs-derived/grammar/`.
- Never write `data/` or `specs-repo-annotated/`. Never edit the meta line
  of the status file: `seal` writes it.
- Commit nothing and push nothing: the step of layer 2 commits and pushes
  the output after the last generator (NRM-9).

## The order of a run

Every run goes in this order, with no question to the user (DGR-14 (Each
pending fragment gets its own issue in layer 1 at once (NRM-8), and the
derivation goes on)):

1. The work list (`worklist`).
2. Derive, file by file.
3. Seal and check (`seal`, `check`).
4. The issue of each pending fragment, opened at once while you derive
   (step 2 sends you there).
5. The issue of each stale citation of the script, after the last check.
6. Show the end report.

## 1. The work list

```sh
uv run --with "lark[interegular]" python3 -I -B "$S" worklist > <scratchpad>/worklist.jsonl
```

Exit 2: show the message and stop. Otherwise one JSON line per item
(DGR-12 (Only what a change calls for is derived again (NRM-7))):

- `new`, `changed`, `gone`: a fragment, with exactly `kind`, `id`,
  `old_hash`, `new_hash`, `cases` and `file` (`null` for a `gone` fragment
  whose node no longer exists). `cases` is the one the script gives from the
  opening line: `["accept"]`, `["reject"]`, or `[]` when the opening line is
  none of the forms of CEX-4 (DGR-6); for a `gone` one, the cases of its old
  status line.
- `norm`: a statement whose citation no longer checks, with exactly `kind`,
  `statement` (its key), `old_hash`, `new_hash` (null when the norm is
  retired or gone) and `citation` (`<norm ID>@<norm hash>`).

Then, before you change anything:

- When the status file does not exist, or its first line has no field
  `generator` (it was written by the local skill `/derive-grammar` of the
  repository of layer 2), the work list took it and the grammar as absent:
  every fragment is `new`. Write both files anew: empty the grammar, and
  empty the status file (zero bytes), before the first file (DGR-12, "A
  status file of the local skill"). The issues of the old pending lines are
  found again by the search for a duplicate (step 4).
- When the grammar does not exist, create it empty, so that `seal` can run.
- Note every status line that is `pending` with an `issue`: the end report
  needs them.
- Count the fragments of the tree:

  ```sh
  uv run --with "lark[interegular]" python3 -I -B - "$M" <<'PY'
  import importlib.util as u, pathlib, sys
  s = u.spec_from_file_location("derived_norms", sys.argv[1]); m = u.module_from_spec(s); s.loader.exec_module(m)
  print(len(m.load_tree(pathlib.Path(".")).fragments))
  PY
  ```

  With 0, layer 2 holds no Clean example yet (DGR-13, "No fragment yet"):
  the grammar holds no statement and the status file only its meta line.
  Work through the `gone` items (if any) until both are so, then go to
  step 3; the end report says that layer 2 holds no Clean example yet.

An empty work list: go to step 3, which still seals and checks (DGR-12,
DGR-17).

## 2. Derive, file by file

Group the fragment items by `file` and work one file at a time, to keep the
context small. For each file:

1. Read the case text, the cases and the expected line of its `new` and
   `changed` fragments (a `gone` one has no text), as the script takes them
   (DGR-6 (The script takes the one case of a fragment from its opening line,
   never cuts it, and the deriver decides nothing about it)):

   ```sh
   uv run --with "lark[interegular]" python3 -I -B - "$S" <ID> <ID> ... <<'PY'
   import importlib.util as u, pathlib, sys
   s = u.spec_from_file_location("dg", sys.argv[1]); g = u.module_from_spec(s); s.loader.exec_module(g)
   import derived_norms as m  # the module script, which the script puts on sys.path
   t = m.load_tree(pathlib.Path("."))
   for i in sys.argv[2:]:
       n = t.nodes[i]
       print(f"== {i}@{t.norm_hash(i)} cases={g.case_kinds(n)} expected_line={g.expected_line(n)} {n['file']}")
       print(m.fragment_lines(t, n)[0])
       print(m.case_text(t, n), end="")
       fs = m.program_files(m.case_text(t, n))
       if fs[0].file_line: print("-- files:", [(f.number_of_file, f.path_of_file_line, f.first_line_in_case_text) for f in fs])
   PY
   ```

   It prints the opening line, then the case text. The case is the whole
   case text: the script never cuts a fragment. The case text keeps the
   leading blanks of the fragment: a run of four spaces is never turned into
   a tab, and a space in the indentation of a block fails through the
   indenter (DGR-11). The case comes from the opening line only, never from
   a comment of the code (CDN-2): `expect=valid` and `expect=error` are
   `accept`; `expect=syntax-error ... line=<n>` is `reject`, with `<n>` the
   expected line; any other opening line gives `[]`. The error code is not
   checked (CDN-4). You decide nothing about the case.

   A case text with file lines (a line that starts at column 1 with
   `// file:`) holds a program of several files (DGR-19 (The script splits
   the case text into the files of its program, and parses each file alone,
   as a whole source file (CDN-6))); the snippet then prints `-- files:`,
   each file with its number, its path (None when it has none) and the line
   of the case text where it starts. The script splits the files from those
   lines alone, and parses each file alone, in order, from `start`, as a
   whole source file; the lines before the first file line are not parsed.
   So write the grammar for a source file: never a rule that joins two
   files, or that reads a file line as more than a comment. The expected
   line counts the lines of the whole case text. The form of a path, two
   files with one path, which file holds `start:`: none of it is yours to
   check (CDN-4).
2. Read the prose norms the fragments need: the section of the file around
   them in `specs-repo-annotated/`, and the norms about the syntax they use
   (lexical, expressions, statements, file structure). A norm's hash is the
   first 8 hex digits of its `tree_hash` in `data/tree.jsonl`.
3. Work through each item, as below.

### new or changed

Decide the state of the fragment (DGR-5 (After the meta line, the status
file has one line for each fragment, and no other), DGR-6). A fragment is
`derived` or `pending`, nothing else:

- `pending` when its `cases` is `[]`: its opening line is none of the forms
  of CEX-4 (CDN-3), whatever else it holds. Write no statement for it, and
  it is not parsed. Its `reason` is exactly
  `"the opening line is none of the forms of CEX-4"` (CEX-4 is cited as
  text: it is not a norm of layer 2). Then open its issue at once (step 4,
  "A malformed opening line").
- `derived` when you can write the grammar that it needs, from the
  fragments and the prose norms, deciding nothing. Its case `accept` must
  parse; its case `reject` must fail to parse, and the place of the failure
  must not end before the line break that ends the line before its expected
  line (anywhere when the expected line is 1) (DGR-13).
- `pending` when it is a gap ("A gap" below).

For a derived fragment, write or extend the statements it needs (DGR-2 (The
grammar comes from the fragments, and from the prose norms that a rule
needs), DGR-8 (Every statement of the grammar cites its norms, one citation
line per norm, just above it)):

- A rule that already covers what the fragment shows gets one more
  citation line for it. Never write a second rule for the same thing.
- Every statement has its citations just above it, one line per norm, no
  blank line between: `// <norm ID>@<norm hash>: <reason>`, such as
  `// EXP-11@e105eaa8: ^ is right-associative`. Write a statement and its
  citations in the same edit. Every comment line is a citation; no comment
  at the end of a line. A statement starts at column 0; each further line
  of it, an alternative `| ...` included, is indented.
- A helper rule, a terminal or a directive (`%ignore`, `%declare`) cites the
  norm it serves. Every rule and terminal is used by `start` or by another
  statement, and cites a fragment or is used by one that does.
- No `%import`: write every terminal out and cite where it comes from.
- A citation names the fragment, as `<norm ID>@<norm hash>`; never
  `<norm ID>#<n>`.

The fixed names that the script builds the parser with (DGR-11
(Indentation, line breaks and names reach the parser through fixed names)):

- `start` is the start rule.
- `_NL`, `_INDENT`, `_DEDENT` feed the Lark indenter, with one column per
  tab (LEX-20). The indenter reads the indentation after the last line break
  of a `_NL` token, so `_NL` matches the line break and the blanks after it.
  The script itself refuses a space in the indentation when no bracket is
  open (LEX-21, EXP-27): do not write a rule for that.
  `%declare _INDENT _DEDENT`. Derive and cite them like any statement, as
  from LEX-11, LEX-20 and EXP-27.
- Each bracket is a named terminal `OPEN_<X>` with its `CLOSE_<X>`, such
  as `OPEN_PAREN: "("` and `CLOSE_PAREN: ")"`. A line break between them
  does not end a line. Never write a bracket as an anonymous string in a rule.
- The lexer of Lark does not reserve keywords. `RESERVED` lists, as string
  alternatives, every reserved keyword and reserved name (LEX-37, LEX-46,
  LEX-181). `NAME` matches none of them, such as with a negative lookahead.
  A contextual keyword (LEX-146) stays out of `RESERVED`.

Then write the status line of the fragment, with the fields in this order,
as one line of compact JSON:

```json
{"type":"fragment","id":"SEM-79","hash":"048fdf74","cases":["reject"],"state":"derived","reason":null,"issue":null}
{"type":"fragment","id":"COR-638","hash":"9d3a4f10","cases":["accept"],"state":"pending","reason":"no norm says whether onError binds tighter than +: EXP-8@a0b54578, ERR-34@b0f47afe","issue":null}
{"type":"fragment","id":"SEM-183","hash":"78c5dddb","cases":[],"state":"pending","reason":"the opening line is none of the forms of CEX-4","issue":null}
```

`hash` is its current norm hash and `cases` the list the script gives.
`reason` is null if and only if the state is `derived`. `issue` is null
unless the state is `pending`. Keep the `issue` of a fragment that stays
pending. A fragment that is no longer pending gets `"issue":null`; list its
old issue for the end report.

A `changed` fragment is derived again as a new one. The statements that
cited its old hash come as `norm` items: work through them too. A fragment
that becomes `pending` loses every citation in the grammar, as in steps 1 to
3 of "gone": only a `derived` fragment is cited.

### gone

1. Remove every citation of the fragment from the grammar.
2. Delete each statement left with no citation.
3. Each statement that lost a citation but keeps others: evaluate it again
   as a `norm` item, and remove what only that fragment called for.
4. Remove its status line.

### norm

Read the current text of every norm the statement cites. If the statement
still follows from them, update only the norm hashes of its citations.
Otherwise rewrite it or remove it, and the fragments it serves are
evaluated again. Change nothing that no item reaches (DGR-12).

### A gap

You never decide what the norms do not decide, and never fill a gap
(DGR-10 (The deriver makes no decision that the norms do not make)). A
fragment is a gap when it cannot be turned into grammar without deciding
something that no fragment and no prose norm says, such as the precedence
of an operator that no norm lists. A shift/reduce or reduce/reduce conflict
that no cited norm settles is a gap too: never settle it yourself. A
rewriting for LALR keeps the structure the norms describe, and cites the norm
of any precedence, associativity or order of evaluation it brings in.

1. Write no statement for it, and remove any part you began.
2. Write its status line `"state":"pending"`, with a `reason` that says
   what the norms leave open and cites at least one norm that leaves it
   open, as `<norm ID>@<norm hash>`, such as
   `"no norm says whether onError binds tighter than +: EXP-8@a0b54578, ERR-34@b0f47afe"`.
   Keep its `issue` if it has one; otherwise `null`.
3. If it has no issue, open it at once, as step 4 says: one issue for this
   fragment alone, never one shared with other fragments, even with the
   same gap. Do not propose it and do not wait for a yes. Then go on with
   the next item.

After the work list, for every status line that is `pending`, from this run
or an earlier one, whether or not its fragment changed:

- with `"issue": null` (a run that stopped, a `gh` that failed): open its
  issue in this run, as step 4 says. The search for a duplicate by ID never
  opens it twice.
- with an issue: check it with `gh issue view <URL> --json state`. Open:
  keep it, open no new one. Closed: open a new issue at once, as step 4
  says, with the line `Related: #<m>` naming the closed one, and write the
  new URL in its status line in place of the old one.

## 3. Seal and check

After each file, and at the end:

```sh
uv run --with "lark[interegular]" python3 -I -B "$S" seal --model <your model ID>
uv run --with "lark[interegular]" python3 -I -B "$S" check
```

`seal` orders the status lines as `data/tree.jsonl` and writes the meta
line (DGR-4 (The first line of the status file records the specs commit, the
generator, the model and the hashes of the output (NRM-5)), DGR-17 (The
grammar and the status file change only through a run of the use case)),
such as

```
{"type":"meta","specs_commit":"3a4ba07351c7f3f0f5f7e9a86e583263191ba15e","generator":{"plugin":"clean-derived-norms","version":"0.1.0","marketplace_commit":"<sha>"},"model":"claude-opus-5-5","grammar_sha256":"<sha256>","status_sha256":"<sha256>"}
```

`--model` is required: pass the exact model ID you run as, from your own
context, such as `--model claude-opus-5-5`; never a family name such as
`Opus`, and never a guess. Without `--model`, `seal` exits with 2 and
writes nothing. The script computes every other value itself: the specs
commit from `data/tree.jsonl`, the version from the plugin's
`.claude-plugin/plugin.json`, the marketplace commit from
`~/.claude/plugins/installed_plugins.json` or the checkout that holds the
plugin, or `none`. Exit 2 (a missing or malformed input, or a plugin with no
version): show the message, it wrote nothing.

`check` prints one line per problem, `<check>: <ID or key>: <what>`; for a
program of several files, the message of a failure names the line of the
case text, then the file and its line, such as
`line 9 (file 2, app/main.cln, line 3): UnexpectedToken: ...` (DGR-19). Then
the last line
`fragments: <d> derived, <p> pending; accept parsed <a>/<A>; reject rejected <r>/<R>; problems: <n>`
(DGR-13 (The script checks the grammar and the status file, and pending
counts as a failure (NRM-6))). Exit 0: all passes; 1: problems; 2: an input
is missing or Lark cannot be loaded. With no fragment in the tree, it does
not build the grammar and checks only the meta line and the citations of the
script.

Fix the problems your statements caused (`build`, `citation`, `usage`,
`source`, `brackets`, `names`, `accept`, `reject`, `cited`, `statement`,
`import`, `status`, `reason-citation`, `layout`), only as the norms allow,
and seal again.

- `opening line`: a fragment whose opening line is none of the forms of
  CEX-4 is not `pending`: mark it pending, as "new or changed" says.
- `meta` `generator`: the meta line was sealed by another plugin or
  version, or by the local skill (no `generator`): seal again.
- `meta` `model`: no model, or one not of the form of a model ID: seal
  again with your exact model ID. `check` judges only the form.
- `meta` `grammar_sha256` or `status_sha256`: a file changed after the last
  `seal`: seal again once your change is done.
- `issue`: two status lines hold the same issue URL. Fix it at once, with
  no question: the first of those lines in the order of the status file
  keeps the URL; every other one gets `"issue": null` and, when it is
  pending, its own issue is opened in this same run, as step 4 says. Then
  `seal` and `check` again, and list each line changed in the end report.
- `pending` stays until layer 1 is fixed.
- `script-citation` needs a new version of the plugin: never change the
  script; step 5 opens the issue of its norm in `jpchauny/claude-plugins`,
  and `check` keeps failing until the plugin is fixed (DGR-18).

## 4. The issue of a pending fragment

The issues of pending fragments go to `Ivan-Pasco/clean-language-foundation`
(NRM-8), one per pending fragment (DGR-14). Open each one at once, while you
derive: no proposal, no `↳ ¿anoto?` line, no yes. The same holds for the
comment on an open duplicate: it is posted at once, and no link is proposed.
This use case departs from `/utilities:issue` only in the yes (decision of
the user, 2026-10-23) and in the parent: an issue of a pending fragment has
no parent in the tree of issues. The label `derive-grammar` identifies it,
and the status file is its index.

### Fill in the template

The values come from the status line, `data/tree.jsonl` and git. This
prints, for each ID, one JSON line (`id`, `hash`, `reason`, `issue`, `file`,
`spec_file`, `section`, `line`, `foundation`, `norms`, `norms_involved`) and
then the fragment as it is, its opening line and its closing fence included,
without the indentation of its fence:

```sh
uv run --with "lark[interegular]" python3 -I -B - "$M" <ID> <ID> ... <<'PY'
import importlib.util as u, json, pathlib, subprocess, sys
s = u.spec_from_file_location("derived_norms", sys.argv[1]); m = u.module_from_spec(s); s.loader.exec_module(m)
root = pathlib.Path("."); t = m.load_tree(root)
rows = [json.loads(l) for l in (root / m.TREE_REL).read_text(encoding="utf-8").splitlines() if l.strip()]
files = {r["path"]: r for r in rows if r.get("type") == "file"}
st = root / "specs-derived/grammar/clean-language-code-examples-status.jsonl"
status = {v["id"]: v for v in (json.loads(l) for l in st.read_text(encoding="utf-8").splitlines() if l.strip()) if v.get("type") == "fragment"} if st.is_file() else {}
kids = {}
for r in rows:
    if r.get("type") == "node": kids.setdefault(r["parent"], []).append(r)
def heading(i):
    h = [k for k in kids.get(i, []) if k["kind"] == "heading"]
    return h[0]["own_text"].lstrip("#").strip() if h else None
def section(n):
    while n.get("parent"):
        n = t.nodes[n["parent"]]
        if heading(n["id"]): return heading(n["id"])
def title(i):
    n = t.nodes[i]
    while not heading(i) and not n["own_text"].strip() and kids.get(n["id"]): n = kids[n["id"]][0]
    return heading(i) or m.first_words(n["own_text"])
def line(n):
    ann = (root / "specs-repo-annotated" / n["file"]).read_bytes(); out, pos, prev = bytearray(), 0, 0
    for off, ins in files[n["file"]]["insertions"]:
        out += ann[pos:pos + off - prev]; pos += off - prev + len(ins.encode()); prev = off
    return bytes(out + ann[pos:])[:n["start"]].count(b"\n") + 1
norms = subprocess.run(["git", "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True).stdout.strip()
for i in sys.argv[2:]:
    n = t.nodes[i]; v = status.get(i, {}); reason = v.get("reason") or ""
    print(json.dumps({"id": i, "hash": t.norm_hash(i), "reason": reason, "issue": v.get("issue"),
        "file": n["file"].removeprefix("specs/"), "spec_file": n["file"].rsplit("/", 1)[-1], "section": section(n), "line": line(n),
        "foundation": t.specs_commit[:8], "norms": norms,
        "norms_involved": [f"{c} ({title(c)}) @{h}" for c, h in m.INLINE_CITATION_RE.findall(reason)]}, ensure_ascii=False))
    print("\n".join(m.fragment_lines(t, n)))
PY
```

| Placeholder | Value |
|---|---|
| `<ID>` | `id`: the ID of the fragment, everywhere but in Norms involved. |
| `<reason>` | `reason` of the status line, as it is. |
| `<reason IDs>` | The norm IDs cited in `reason`, comma-separated, such as `EXP-8, ERR-34`. |
| `<spec file>` | `spec_file`: the base name of its file, such as `expressions.md`. |
| `<file>` | `file`: its path under `specs/` of the foundation, such as `language/syntax/expressions.md`. The template always writes `specs/<file>`. |
| `<section>`, `<heading>` | `section`: the heading of the nearest section around it. |
| `<line>` | `line`: the line of its opening fence in the foundation file at the foundation commit, from its `start` and the `insertions` of its file. |
| `<sha>` of foundation | `foundation`: the first 8 hex digits of `specs_commit` (`foundation_commit` in an older tree) in the meta line of `data/tree.jsonl`. |
| `<sha>` of norms | `norms`: `git rev-parse --short=8 HEAD` of the repository of layer 2. |
| `<ID> (<title>) @<hash>, ...` in Norms involved | `norms_involved`: one entry per norm cited in the reason, `<norm ID> (<title of the norm>) @<norm hash>`; the title is its heading or, without one, its first words as the script cuts them (`first_words`). Add any other norm you read that leaves the gap open. |
| `<the fragment, as it is>` | The lines printed after the JSON line, as they are: its opening line, its code and its closing fence. |
| `<the gap>` | What the norms leave open, in one plain sentence. |
| Readings, and `<options, numbered>` | Each reading the specs allow, with a ✅ or ❌ minimal example; in the hand-off, the same readings numbered, in the same order. Recommend none: the decision stays open (DGR-10). |
| `<title>` in the hand-off | The title of the issue. |
| `#<N>` | The number of this issue, known once it is opened: the last part of the URL that `gh issue create` prints. Used only for the issue's own number. |
| `#<M>, ...` in Related | The numbers of the other issues that the line links: every closed duplicate that counts, and the gap issues that look alike. |

Title (it ends with the ID of the fragment in parentheses):

```text
<spec file> — <section>: <the gap in one sentence> (<ID>)
```

such as `expressions.md — Operator Precedence: where does onError bind?
(EXP-<n>)`, for an imagined fragment `EXP-<n>` of that section. Take the
section and the ID from the values above, never from this example.

Labels, exactly: `finding`, `question`, `derive-grammar` (a malformed opening
line has no `question`: see "A malformed opening line").

Body, in English. The first paragraph is what happens; then the fragment as
it is; then the decision needed:

`````markdown
Fragment <ID> (specs/<file>, section "<heading>", foundation @ <sha>)
cannot be turned into grammar: <the gap, plainly>. Norms involved:
<ID> (<title>) @<hash>, ...

<the fragment, as it is>

**Decision needed** — the readings the specs allow, each with a ✅/❌ minimal example.

Related: #<M>, ...

**Hand-off**
````text
You are resolving issue #<N> of Ivan-Pasco/clean-language-foundation: <title>.

Context:
- Ivan-Pasco/clean-language-foundation (local: ~/Documents/Clean Language/clean-language-foundation)
  is the specification of Clean and its single source of truth.
- Ivan-Pasco/clean-language-norms (local: ~/Documents/Clean Language/clean-language-norms) is
  layer 2: specs-repo-annotated/ (the specs with stable norm IDs, from /norms-management:build)
  and specs-derived/grammar/ (clean.lark and its status file), derived by
  /clean-derived-norms:derive-grammar from the Clean examples (```clean-language fragments).
  The grammar never decides what the specs do not say.
- Fragment <ID> is pending with the reason "<reason>".
Problem: <the gap>, specs/<file>:<line>.
Decision: open; the user has not decided. <options, numbered>
Steps:
1. Present the element to the user, short and simple: the context, the problem, and the
   options numbered, recommending none: the user chooses. Wait for the yes; change nothing before it.
2. Write the rule, with an example, in specs/<file> (<section>). Show the diff first.
   The fix must change fragment <ID> itself, or one of the norms its reason cites
   (<reason IDs>), so that the next run tries it again.
3. After the merge, in clean-language-norms: /norms-management:build, which runs
   /clean-derived-norms:derive-grammar.
Verification: in clean-language-norms, after step 3, the status line of <ID> is "derived",
and `check` no longer lists <ID> as pending.
Rules (foundation CLAUDE.md): the user decides, one element per message; English; every change
to specs/ shown as a diff and applied after the yes; a branch in its own worktree, PR against
main; files added by explicit path.
Done when: the rule is in foundation and <ID> is "derived" in clean-language-norms.
"Closes #<N>" in the PR.
````

Found while deriving the Lark grammar of Clean (/clean-derived-norms:derive-grammar), foundation @ <sha>, norms @ <sha>.
`````

The line `Related: #<M>, ...` is a link only: each fragment keeps its own
issue, and nothing is grouped. It links, on one line, every closed duplicate
that counts (step 1 below) and every other gap issue that looks alike, such
as `Related: #12, #15`. Leave it out when none of them exists. Find the
issues that look alike in the list of step 1 below.

### A malformed opening line

A fragment whose `cases` is `[]` is pending because its opening line is none
of the forms of CEX-4 (CDN-3; DGR-14, "The issue of a fragment whose opening
line is none of the forms of CEX-4"). Its issue is opened as a gap's, with
the same values, search for a duplicate, title form and order of the body,
with these changes only:

- `<the gap>` is `an opening line that is none of the forms of CEX-4`.
  Norms involved: none of layer 2; name the rule as text, `CEX-4 (the forms
  of the opening line) of the plugin clean-examples`.
- In place of `**Decision needed** — ...`, the body holds:

  ```markdown
  **Fix needed** — write the opening line as CEX-4 says, one of
  `clean-language expect=valid`, `clean-language expect=syntax-error code=<error code> line=<n>`
  or `clean-language expect=error code=<error code>`, keeping every line of the code byte
  for byte and in order. CEX-4 decides the form; only the expected outcome is to tell.
  ```

- In the hand-off, `Problem:` is `the opening line of fragment <ID> is none of
  the forms of CEX-4, specs/<file>:<line>.`; `Decision:` is `decided by CEX-4;
  write the opening line as Fix needed says.`; step 1 is `1. Show the user the
  fragment and the opening line to write, short and simple. Wait for the yes;
  change nothing before it.`; step 2 is `Write the opening line of fragment
  <ID> in specs/<file> (<section>) as Fix needed says, keeping every line of
  the code byte for byte. Show the diff first.`; the verification is `in
  clean-language-norms, after step 3, the opening line of <ID> is one of the
  forms of CEX-4, and <ID> is no longer pending for it.`; and `Done when:` is
  `the opening line is fixed in foundation, and <ID> is no longer pending for
  it in clean-language-norms.`
- Its labels are exactly `finding` and `derive-grammar`, without
  `question`: CEX-4 decides the form, so nothing waits for a decision on the
  norms. In step 4 below, it is `-l finding,derive-grammar`.

### Open it at once

For the fragment, without a proposal and without a yes. Append each event
to `<scratchpad>/issues-opened.jsonl` as it happens, one JSON line each
(item 7 below): the end report is built from that file.

1. Search for a duplicate by the ID of the fragment only, never by the
   words of the gap:

   ```sh
   gh issue list -R Ivan-Pasco/clean-language-foundation --state all --label derive-grammar -L 5000 --json number,title,state,url
   ```

   Only an issue whose title ends with `(<ID>)` counts. An issue of another
   fragment is never a duplicate, even with a gap that looks alike. The
   list is read with `--label`, never with `--search`: it does not go
   through the search index of GitHub, so an issue created a moment ago is
   already in it.

   When one that counts is open, open nothing. Comment on it at once, with
   no proposal of a link and no yes: write the comment to
   `<scratchpad>/comment-<ID>.md`, as the line below, and post it:

   ```text
   Still pending at foundation @ <sha>, norms @ <sha>: <reason>
   ```

   ```sh
   gh issue comment <number> -R Ivan-Pasco/clean-language-foundation -F <scratchpad>/comment-<ID>.md
   ```

   Then write its URL in the `issue` of the status line, do step 7, and go
   on with the next item.

   When the ones that count are all closed, open a new issue (steps 2 to
   7): its line `Related:` links every one of them. Do not reopen them, and
   do not comment on them.
2. Fill in the template above. Write the title to
   `<scratchpad>/title-<ID>.txt` and the body to
   `<scratchpad>/issue-<ID>.md`. The title may hold a backtick, a `$` or a
   `"`: never write it into the command itself.
3. Create the labels that the foundation lacks:

   ```sh
   R=Ivan-Pasco/clean-language-foundation
   gh label create finding  -R $R --color d73a4a --description "Something found wrong, to resolve" 2>/dev/null
   gh label create question -R $R --color d876e3 --description "Waits for a decision of the user" 2>/dev/null
   gh label create derive-grammar -R $R --color c5def5 --description "Found by /clean-derived-norms:derive-grammar in clean-language-norms" 2>/dev/null
   ```
4. Open it with the title file and the body file. It gets no parent:

   ```sh
   gh issue create -R Ivan-Pasco/clean-language-foundation -t "$(cat <scratchpad>/title-<ID>.txt)" -l finding,question,derive-grammar -F <scratchpad>/issue-<ID>.md
   ```

   It prints the URL of the issue; its number `<N>` is the last part of
   that URL.
5. At once, write that URL in the `issue` of the status line, before
   anything else, so that the status file never misses an issue that
   exists.
6. Write `<N>` for `#<N>` in the body file, never in the line `Related:`,
   and update the issue:
   `gh issue edit <N> -R Ivan-Pasco/clean-language-foundation -F <scratchpad>/issue-<ID>.md`.
   The `seal` and `check` at the end of the file (step 3) follow.
7. Append to `<scratchpad>/issues-opened.jsonl` the issue opened (fragment,
   number, title, URL) or the open duplicate commented on (fragment, URL).
   When `gh issue create` fails, leave `"issue":null`, append the fragment
   and the error, and go on: the next run opens it. When only
   `gh issue edit` fails, keep the URL, and append that the body of the
   issue still holds `#<N>`.

## 5. The issue of a stale citation of the script

The code of the script, the script and the module script, cites the norms it
follows (`# <norm ID>@<norm hash>: <reason>`); today the module script, where
the indenter is, cites LEX-20 (each indentation level is exactly one tab
character), LEX-21 (mixing tabs and spaces for indentation is not allowed)
and EXP-27 (inside an open parenthesis a line continues). When one of those
norms changes its hash, is retired or is gone, `check` reports
`script-citation` and fails. Only a new version of the plugin fixes the
script, so the run opens, at once and with no yes, one issue per stale cited
norm in the repository of the plugin, `jpchauny/claude-plugins` (CDN-5,
DGR-18 (Each stale cited norm of the script gets its own issue in
jpchauny/claude-plugins at once (CDN-5), and check still fails); decision of
the user, 2026-10-23). Never change the script yourself. The issue has no
parent in the tree of issues.

Do this once per run, after the last `seal` and `check` of step 3, also
when the work list was empty:

```sh
uv run --with "lark[interegular]" python3 -I -B "$S" stale-citations > <scratchpad>/stale-citations.jsonl
```

Exit 2: show the message in the end report and skip this step. An empty
file: nothing to open. Otherwise one JSON line per stale cited norm, in the
order of the code of the script (the script, then the module script): `id`;
`state` (`changed`, `retired` or `gone`); `current_hash` and `new_text`
(null unless `changed`); and `citations`, one per line of the code of the
script that cites the norm with a stale hash: `path` (of its file in the
plugin, such as `scripts/derived_norms.py`), `line` (its number in that
file), `text` (the line, without its indentation), `cited_hash`, `old_text` and
`old_commit` (the text of the norm at the cited hash, from the newest
version of `data/tree.jsonl` in the history of HEAD that has it; both null
when none has it or git cannot run).

### Fill in the template

This writes, for each stale cited norm, `<scratchpad>/script-title-<ID>.txt`,
`<scratchpad>/script-issue-<ID>.md` and `<scratchpad>/script-comment-<ID>.md`,
from `stale-citations.jsonl`, `data/tree.jsonl` and git:

```sh
uv run --with "lark[interegular]" python3 -I -B - "$M" <scratchpad> <<'PY'
import importlib.util as u, json, pathlib, subprocess, sys
s = u.spec_from_file_location("derived_norms", sys.argv[1]); m = u.module_from_spec(s); s.loader.exec_module(m)
root, out = pathlib.Path("."), pathlib.Path(sys.argv[2]); t = m.load_tree(root)
A = "apps/clean-language/modules/clean-derived-norms"
T = "apps/clean-language/modules/clean-derived-norms/tests"
SPEC = "apps/clean-language/modules/clean-derived-norms/use-cases/derive-grammar/specs/derive-grammar.md"
norms = subprocess.run(["git", "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True).stdout.strip()
found = t.specs_commit[:8]; F = "`" * 3; H = "`" * 4
def title(i, text):
    h = [k for k in t.children.get(i, []) if k["kind"] == "heading"] if i in t.nodes else []
    return h[0]["own_text"].lstrip("#").strip() if h else m.first_words(text) or i
for l in (out / "stale-citations.jsonl").read_text(encoding="utf-8").splitlines():
    v = json.loads(l); i, st, cs, cur, new = v["id"], v["state"], v["citations"], v["current_hash"], v["new_text"]
    tt = title(i, new or next((c["old_text"] for c in cs if c["old_text"]), ""))
    what = {"changed": "changed", "retired": "was retired", "gone": "is gone"}[st]
    now = {"changed": f"now has the norm hash {cur}", "retired": "is retired", "gone": "is gone"}[st]
    head = f"clean-derived-norms derive-grammar: {i} {what}, its citation is stale ({i})"
    cited = ", ".join(sorted({c["cited_hash"] for c in cs})); at = ", ".join(f"{A}/{c['path']}:{c['line']}" for c in cs)
    where = ", ".join(dict.fromkeys(f"{A}/{c['path']}" for c in cs))
    old = []
    for h in dict.fromkeys(c["cited_hash"] for c in cs):
        c = next(c for c in cs if c["cited_hash"] == h)
        old += [f"Text of {i} at {h} (old, data/tree.jsonl @ {c['old_commit'][:8]}):", "", F + "text", c["old_text"], F, ""] if c["old_text"] is not None else [f"No version of data/tree.jsonl in the history of HEAD has {i} at {h}.", ""]
    newp = [f"Text of {i} now ({cur}):", "", F + "text", new, F] if st == "changed" else [f"{i} is retired in data/tree.jsonl: it has no current text." if st == "retired" else f"{i} is gone: data/tree.jsonl no longer has it."]
    body = [f"The code of the script of /clean-derived-norms:derive-grammar cites {i} ({tt}), and that citation is stale: {i} {now} (cited at {cited}), at foundation @ {found}.",
        "`check` fails with the problem `script-citation` until a new version of the plugin changes the code of the script. The lines that cite it:", "",
        F + "python", *[f"{c['path']}:{c['line']}: {c['text']}" for c in cs], F, "", *old, *newp, "",
        "**Decision needed** — does the code still follow from the new text? The options are numbered in the hand-off; none is recommended here.", "",
        "**Hand-off**", H + "text",
        f"You are resolving issue #<N> of jpchauny/claude-plugins: {head}.", "",
        "Context:",
        "- jpchauny/claude-plugins (local: ~/Documents/claude-plugins) is the marketplace that holds the plugin",
        "  clean-derived-norms; its use case /clean-derived-norms:derive-grammar derives the Lark grammar of Clean",
        "  in specs-derived/grammar/ of Ivan-Pasco/clean-language-norms (layer 2) from the norms of data/tree.jsonl.",
        f"- The code of its script cites, in {where},",
        f"  the norms it follows, as \"# <norm ID>@<norm hash>: <reason>\" (DGR-9 and DGR-18 of {SPEC});",
        "  a norm hash is the first 8 hex digits of the tree_hash of the norm in data/tree.jsonl of layer 2.",
        f"- {i} ({tt}) {now} (cited at {cited}), at foundation @ {found}, norms @ {norms}.",
        "  The old and the new text are in the body of this issue.",
        f"Problem: the citation of {i} in the code of the script is stale, so `check` fails with \"script-citation: {i}\", {at}.",
        "Decision: open; the user has not decided.",
        "  1. The code still follows from the new text: only the norm hash of the citation changes.",
        "  2. The code no longer follows: change the code and its citation, and the spec and the tests that describe it.",
        "  3. The norm no longer says it, is retired or is gone: cite the norm that says it now, or remove the code",
        "     that rests on it.",
        "Steps:",
        "1. Present the element to the user, short and simple: the context, the problem, the old and the new text,",
        "   and the options numbered, recommending none: the user chooses. Wait for the yes; change nothing before it.",
        f"2. Change the spec first where it names {i}@{cited} (DGR-11, DGR-18), and have the user approve it (DEV-1).",
        "   Then change the code of the script as chosen, each citation as \"# <norm ID>@<norm hash>: <reason>\", with the norm hash",
        f"   of data/tree.jsonl, and every place of the tests that names {i}@{cited}. Show the diff first.",
        f"3. Run the tests: cd ~/Documents/claude-plugins && uv run --with pytest --with \"lark[interegular]\" python3 -I -B -m pytest -q -p no:cacheprovider {T}",
        "4. Release the change as a new version of the plugin: raise the version of its .claude-plugin/plugin.json.",
        "   The fix is a change of the plugin, never a commit in the repository of layer 2.",
        "Verification: the tests pass; after the new version of the plugin runs (/norms-management:build in",
        f"clean-language-norms), `check` prints no line \"script-citation: {i}\", and stale-citations prints no line for {i}.",
        "Rules (jpchauny/claude-plugins, specs/development.md and its CLAUDE.md): the spec comes first and the user",
        "approves it; the user decides, one element per message; English; files added each by its path, never a folder",
        "or git add -A; never git stash, git reset --hard or git clean: other sessions work in the repository.",
        f"Done when: no citation of {i} in the code of the script is stale, the new version of the plugin is released, and its",
        f"check prints no \"script-citation: {i}\". Then close #<N> with a comment that names that version.",
        H, "", f"Found while checking the Lark grammar of Clean (/clean-derived-norms:derive-grammar), foundation @ {found}, norms @ {norms}.", ""]
    (out / f"script-title-{i}.txt").write_text(head, encoding="utf-8")
    (out / f"script-issue-{i}.md").write_text("\n".join(body), encoding="utf-8")
    (out / f"script-comment-{i}.md").write_text("\n".join(f"Still stale at norms @ {norms}: {c['path']} line {c['line']} cites {i}@{c['cited_hash']}; {i} {now}." for c in cs) + "\n", encoding="utf-8")
    print(i, st, head)
PY
```

The title of the norm is its heading, or, without one, its first words as
the script cuts them (`first_words`). Title of the issue (it ends with the ID
of the norm in parentheses):

```text
clean-derived-norms derive-grammar: <ID> <changed | was retired | is gone>, its citation is stale (<ID>)
```

Labels, exactly: `finding`, `derive-grammar`. The body holds, in this order:
what happens; the lines of the code of the script, each with its path and
number, in a `python` block; one old-text block
per cited hash, or the sentence that no version has it; the new text, or the
sentence that the norm is retired or gone; **Decision needed**; the line
`Related: #<M>, ...` when a closed duplicate counts (step 1 below adds it);
**Hand-off**; and the last line `Found while checking ...`.

### Open it at once

For each line of `stale-citations.jsonl`, without a proposal and without
a yes. Append each event to `<scratchpad>/issues-opened.jsonl`, as in
step 4, with `"kind":"script"` and the norm ID.

1. Search for a duplicate by the ID of the norm only:

   ```sh
   gh issue list -R jpchauny/claude-plugins --state all --label derive-grammar -L 5000 --json number,title,state,url
   ```

   Only an issue whose title begins with `clean-derived-norms derive-grammar: `
   and ends with `(<ID>)` counts. When one that counts is open, open nothing:
   comment on it at once with the comment file, one line per stale citation,
   `Still stale at norms @ <sha>: <path> line <line> cites <ID>@<cited hash>; <ID>
   <now has the norm hash <current hash> | is retired | is gone>.`:

   ```sh
   gh issue comment <number> -R jpchauny/claude-plugins -F <scratchpad>/script-comment-<ID>.md
   ```

   Then append it to the record and go on with the next norm. When the
   ones that count are all closed, add the line `Related: #<M>, ...`, which
   links every one of them, on its own line just before `**Hand-off**`,
   with a blank line before and after it, and open a new issue (steps 2 to
   5). Do not reopen them, and do not comment on them.
2. Create the labels that the repository lacks:

   ```sh
   R=jpchauny/claude-plugins
   gh label create finding -R $R --color d73a4a --description "Something found wrong, to resolve" 2>/dev/null
   gh label create derive-grammar -R $R --color c5def5 --description "Found by /clean-derived-norms:derive-grammar" 2>/dev/null
   ```
3. Open it with the title file and the body file. It gets no parent:

   ```sh
   gh issue create -R jpchauny/claude-plugins -t "$(cat <scratchpad>/script-title-<ID>.txt)" -l finding,derive-grammar -F <scratchpad>/script-issue-<ID>.md
   ```

   It prints the URL of the issue; its number `<N>` is the last part of
   that URL.
4. Write `<N>` for `#<N>` in the body file, never in the line `Related:`,
   and update the issue:
   `gh issue edit <N> -R jpchauny/claude-plugins -F <scratchpad>/script-issue-<ID>.md`.
5. Append to `<scratchpad>/issues-opened.jsonl` the issue opened (norm,
   number, title, URL) or the open duplicate commented on (norm, URL). When
   `gh issue create` fails, append the norm and the error, and go on: the
   next run, whose `check` still finds the stale citation, searches and
   opens again. When only `gh issue edit` fails, append that the body of
   the issue still holds `#<N>`.

`check` still fails with `script-citation`: the issue does not silence it.

## 6. Show

End with (DGR-15 (The use case ends by showing what it did, the issues it
opened, and the result of the check)):

- The specs commit, the generator (plugin, version and marketplace commit)
  and the model, from the meta line.
- The count of fragments by state; with none, that layer 2 holds no Clean
  example yet.
- The items of the work list, by norm ID or key, and what was done with each.
- The statements added, changed or removed, by key.
- The fragments newly marked pending, each with its reason.
- From `<scratchpad>/issues-opened.jsonl`: the issues opened in this run,
  each in one line with its number, its title, its fragment and its URL,
  with no parent; each open duplicate commented on instead, with its
  fragment and its URL; each issue that could not be opened, with its
  fragment and the error; and each issue whose body still holds `#<N>`.
- The issues of fragments that are no longer pending: the fix in layer 1
  may close them.
- The stale citations of the script (step 5), which need a new version of
  the plugin: for each stale cited norm, its lines, and the issue opened
  (number, title, URL), or the open duplicate commented on (URL), or the
  error, or that its body still holds `#<N>`.
- Then the output of `check` and its exit status.

When `/norms-management:build` runs this use case, this report is its part of
the build's report (NRM-11); the build commits and pushes (NRM-9).
