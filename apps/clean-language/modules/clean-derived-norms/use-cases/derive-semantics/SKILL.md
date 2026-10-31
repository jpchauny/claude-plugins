---
name: derive-semantics
description: Derive the semantics of Clean in Lean 4 (abstract syntax, typing, evaluation) as a Lake project in specs-derived/semantics/ of the repository of layer 2, from the prose norms of data/tree.jsonl, checked against every Clean example (clean-language fragment) and its expected output (clean-language-output block) - every declaration citing its norms, each fragment parsed by the derived grammar, only what changed derived again, gaps marked pending and opened at once as issues in layer 1, then seal and check, which builds the project and runs every fragment. Run by /norms-management:build as the generator of the type semantics, after the grammar, or by the user typing /clean-derived-norms:derive-semantics.
---

# derive-semantics

Implements [specs/derive-semantics.md](specs/derive-semantics.md) (DSM), with
the rules of the module, CDN-1 to CDN-10, in [module.md](../../specs/module.md),
and the interface of a derived-norms generator, NRM-1 to NRM-15, of the plugin
`norms-management`. Where a step does what `derive-grammar` does, it says so;
its `SKILL.md` is `${CLAUDE_PLUGIN_ROOT}/use-cases/derive-grammar/SKILL.md`.

Two parts. The script does what is deterministic: the work list, the case of
each fragment, its parse tree, the fixed files, the header line and the checks,
which build the Lake project and run every fragment. You, the deriver, write
the Lean code and the status lines. The script never writes a declaration,
never decides a state, and knows nothing of Clean.

Run everything from the root of the repository of layer 2, the working
directory. The script is

```sh
S="${CLAUDE_PLUGIN_ROOT}/use-cases/derive-semantics/derive_semantics.py"
uv run --with "lark[interegular]" python3 -I -B "$S" <command>
```

It imports the module script, the code that it shares with the script of
`derive-grammar`, the parser of the grammar among it (CDN-7 (The script of
each use case of this module imports the module script, and no script of a
use case imports the script of another use case)):

```sh
M="${CLAUDE_PLUGIN_ROOT}/scripts/derived_norms.py"
```

What you read and write (DSM-1 (The use case reads only layer 2 and the
grammar (NRM-3), and writes in the repository only under
specs-derived/semantics/), DSM-3 (The output is one Lake project, one list
of derived norms and one status file in the semantics folder)):

- Read `data/tree.jsonl`, `specs-repo-annotated/` for the context of a norm,
  and the grammar `specs-derived/grammar/clean.lark` (the script parses with
  it). Never read a file of the foundation, nor `project.json`.
- Write only, in `specs-derived/semantics/`, the five files of the Lean code
  (`Clean.lean`, `Clean/Ast.lean`, `Clean/Syntax.lean`, `Clean/Typing.lean`,
  `Clean/Evaluation.lean`) and the status lines of
  `clean-language-code-examples-status.jsonl`; `seal` writes the fixed files
  (`lakefile.toml`, `lean-toolchain`, `Fragment.lean`, `Main.lean`), the
  list of derived norms `derived-norms.jsonl` and the header line. Never edit
  them. Never run `lake` in the semantics folder: its
  `.lake/` would break the layout; `check` builds in a temporary copy.
- Outside the repository: your work files in the scratchpad, and the issues
  of steps 4 and 5.
- Never write `data/`, `specs-repo-annotated/` or `specs-derived/grammar/`.
  Commit nothing and push nothing (NRM-9).

## The order of a run

With no question to the user:

1. The work list (`worklist`).
2. Derive, file by file of the specs.
3. Seal and check (`seal`, `check`).
4. The issue of each pending gap, opened at once while you derive.
5. The issue of each stale citation of the script, after the last check.
6. Show the end report.

## 1. The work list

```sh
uv run --with "lark[interegular]" python3 -I -B "$S" worklist > <scratchpad>/worklist.jsonl
```

Exit 2: show the message and stop; when it names the grammar,
`derive-grammar` must run first (DSM-1). Otherwise one JSON line per item
(DSM-12 (Only what a change calls for is derived again (NRM-7))):

- `new`, `changed`, `gone`: a semantic fragment, with `kind`, `id`,
  `old_hash`, `new_hash`, `cases` (`["run"]`, `["error <code>"]`, or `[]`
  when the opening line is none of the forms of CEX-4), `expected_output`
  (`<ID>@<hash>` or null), `parse_tree_hash` (null when not parsed),
  `parse_error` (the message when the grammar does not parse it) and `file`.
- `norm`: a declaration whose citation no longer checks, with `kind`,
  `declaration` (its key, `<path>:<name>`), `old_hash`, `new_hash` (null when
  retired or gone) and `citation`.
- `version`: a declaration of the Lean code when this plugin is a new version
  (the header line of the status file names another `version` in `generator`,
  or none), with `kind`, `declaration` (its key), `old_version` and
  `new_version`. Then every declaration is a `version` item and every
  semantic fragment with a status line is `changed`: a new version derives
  the whole semantics again (NRM-7).

Then, before you change anything:

- When the status file does not exist, every semantic fragment is `new`.
  Create the folder `specs-derived/semantics/Clean/`, the five files of the
  Lean code (empty is fine for now) and an empty status file, so that `seal`
  can run; run `seal` once to write the fixed files.
- Note every status line that is `pending` with an `issue`: the end report
  needs them.

An empty work list: go to step 3.

## 2. Derive

Group the fragment items by `file` and work one file at a time. For each:

1. Read each fragment as the script takes it, with its expected output and
   its parse tree (DSM-7 (The script gives the Lean code the parse tree of
   each fragment in a generic form, and holds nothing specific to Clean)):

   ```sh
   uv run --with "lark[interegular]" python3 -I -B "$S" tree <ID> <ID> ...
   ```

   It prints, for each, a header line, the opening line, the case text, the
   expected output text (after `-- expected output --`, when it has one),
   and the parse tree (after `-- parse tree --`): a rule as its name, a token
   as its type and its text as JSON, two spaces per level. A string of the
   grammar has a type that Lark makes, such as `PRINT` or `__ANON_3`: tell it
   by its text. `_NL`, `_INDENT` and `_DEDENT` are left out.

   A case text with file lines (`// file: <path>` at column 1) holds a
   program of several files: the script parses each file alone (DGR-19 of
   `derive-grammar`), and its tree is a rule `%program` with one rule
   `%file` per file, in their order; each `%file` holds a token `%path` with
   the path of the file, or `(absent)` when it has none, then the tree of the
   file (DSM-7). A program of one file gives the tree of its file, as
   always. No grammar gives a name with `%`.
2. Read the prose norms that say what those programs mean: types, values,
   operators, statements, functions, errors and their codes, and what
   `print` writes. Read the section around each fragment in
   `specs-repo-annotated/`. A norm's hash is the first 8 hex digits of its
   `tree_hash` in `data/tree.jsonl`.
3. Work through each item, as below.

### The Lean code

The Lake project builds the library `Fragment` (fixed), the library `Clean`
(yours) and the executable `fragment`. Your files, each with one role:

| File | What it holds |
|---|---|
| `Clean/Ast.lean` | the abstract syntax: types, expressions, statements, declarations, programs |
| `Clean/Syntax.lean` | the conversion of a `Fragment.Tree` into the abstract syntax |
| `Clean/Typing.lean` | the typing: the error code of build time, or none |
| `Clean/Evaluation.lean` | the evaluation: the error code of run time, or none, and the standard output |
| `Clean.lean` | imports the four, and defines `Clean.outcome` |

The fixed interface, in `Fragment.lean` (DSM-7, DSM-11 (The semantics gives
the outcome of a program, and the check compares it with the case of the
fragment)):

```lean
namespace Fragment
inductive Tree where
  | rule (name : String) (children : List Tree)
  | token (type : String) (text : String)
  | absent
structure Outcome where
  code : Option String
  output : String
end Fragment
```

`Clean.lean` defines, in `namespace Clean`,
`def outcome (tree : Fragment.Tree) : Fragment.Outcome`: convert the tree,
type the program, and when the typing gives a code return it with an empty
output; otherwise evaluate and return the code of run time, if any, and the
standard output. `partial def` is allowed; the run of one fragment has 10
seconds.

A program of several files reaches `Clean.outcome` as the tree `%program`
(DSM-7): find each file and its path in its children. Find the file that an
`import:` names only by its path, among the files of the program, and only
as the norms define `import:`; never by a guess (another path, a file name,
an order). When no norm says what `import:` means, the fragment is a gap
(DSM-10 (The deriver makes no decision that the norms do not make)).

Rules of the Lean code (DSM-8 (Every declaration of the Lean code cites its
norms, one citation line per norm, just above it), DSM-10 (The deriver makes
no decision that the norms do not make)):

- Every declaration (`def`, `theorem`, `abbrev`, `inductive`, `structure`,
  `class`, `instance`, `opaque`, `example`, the notation commands, `deriving
  instance`) has its citations just above its first line, one per norm, no
  blank line between: `-- <norm ID>@<norm hash>: <reason>`, at column 1.
  Attributes and modifiers go on the first line: `@[simp] partial def f`.
- Each declaration cites at least one prose norm (a norm that is neither a
  fragment nor an expected output block). It may also cite the fragments and
  expected output blocks that show it. Never write a declaration that only a
  fragment calls for.
- Every comment is a citation line. No `/- -/`, no `/-- -/` doc comment, no
  comment at the end of a line, no indented comment.
- At column 1, only: citations, the first line of a declaration, the lines
  `import`, `namespace`, `end`, `open`, `section`, `mutual`, `variable`,
  `universe`, `set_option`, and lines that continue a declaration (`|`,
  `where`, `deriving`, `termination_by`, `decreasing_by`). Write the
  declarations of a `mutual` block at column 1.
- Import only `Fragment` and `Clean.Ast`, `Clean.Syntax`, `Clean.Typing`,
  `Clean.Evaluation`. No `sorry`, no `admit`, no `axiom`.
- No string literal holds the ID of a fragment, or is the expected output of
  a fragment; nothing tells one fragment from another. The semantics gives
  each fragment its outcome by the rules of the norms, or the fragment is a
  gap.

### new or changed

Decide the state (DSM-5 (After the header line, the status file has one line
for each semantic fragment, and no other)). Exactly one of:

- `cases` is `[]`: `pending`, reason exactly
  `"the opening line is none of the forms of CEX-4"`, `"issue": null`. No
  issue of its own: the grammar opened it.
- `parse_error` is not null: `pending`, reason exactly
  `"the grammar does not parse it"`, `"issue": null`. No issue of its own.
- `derived`, when the Lean code, from the prose norms and deciding nothing,
  gives its case: `run` gives no code, and, with an expected output, exactly
  that output, byte for byte; `error <code>` gives exactly that code. No
  comment decides it: `// prints:` is never an expected output (CDN-2,
  CEX-30).
- `pending` as an example that is not a whole program ("Not a whole
  program" below).
- `pending` as a gap ("A gap" below).

Write or extend the declarations it needs. A declaration that already covers
what it needs gets nothing new; never a second one for the same thing. Then
write its status line, fields in this order, compact JSON:

```json
{"type":"fragment","id":"FUN-16","hash":"509f049c","cases":["run"],"expected_output":"FUN-17@0c1d2e3f","parse_tree_hash":"baf0f33a","state":"derived","reason":null,"issue":null}
{"type":"fragment","id":"STA-9","hash":"<hash>","cases":["run"],"expected_output":null,"parse_tree_hash":"<hash>","state":"pending","reason":"STA-9 is not a whole program (CEX-31): it uses the name score, which it does not declare and no norm defines: STA-9@<hash>","issue":null}
```

`hash`, `cases`, `expected_output` and `parse_tree_hash` are those of the
work list. `reason` is null if and only if `derived`. Keep the `issue` of a
fragment that stays pending; a fragment that is no longer pending gets
`"issue": null`, and its old issue goes in the end report.

### gone and norm

As `derive-grammar` does (its SKILL.md, "gone" and "norm"), with
declarations in place of statements: a `gone` fragment loses every citation
of it and its status line; a declaration left with no prose citation goes. A
`norm` item: read the current text of every norm the declaration cites; if
it still follows, update only the hashes of its citations; otherwise rewrite
or remove it, and the fragments it serves are checked again. A `version`
item: the same, but a declaration that still follows stays exactly as it is,
so it keeps its derived norm fingerprint; one that the new version corrects
is rewritten or removed (DSM-12).

### Not a whole program

An example is a whole program: read alone, it declares every name it uses,
except a name that a norm of the language or a specified library defines
(CEX-31 of clean-examples). Nothing outside its code builds it: no other
example, no prelude, no context (CEX-32). A fragment that uses a name which
none of its files declares, and which no norm defines, such as `score` in a
`start:` that never declares it, is not a whole program (DSM-10). It is a
defect of the example, not a gap of the norms.

One exception (CEX-31): in a fragment with `expect=error`, a name whose use
with no declaration gives its error code by a norm is allowed undeclared,
such as the variable of `expect=error code=SEM002` when a norm gives `SEM002`
for a variable declared in no enclosing scope. Such a fragment is not
pending for that name: check it for its error code as any other (`derived`,
or a gap). Any other undeclared name in it is still a defect. For a defect:

1. Invent no declaration, no value, no type and no context for the name.
   Write no declaration for the fragment, and remove any part you began.
2. Write its status line `"state":"pending"`, with the reason, naming each
   such name:
   `"<ID> is not a whole program (CEX-31): it uses the name <name>, which it does not declare and no norm defines: <ID>@<hash>"`
   (`the names <a>, <b> and <c>` for several), then any other norm involved
   after `<ID>@<hash>`, comma-separated. CEX-31 is cited as text: it is no
   norm of layer 2. Keep its `issue` if it has one; otherwise `null`.
3. If it has no issue, open it at once (step 4, "Not a whole program"). No
   proposal, no yes. Then go on.

A pending line that an earlier version of the plugin wrote with the words
`uses the name ..., which it does not declare and no norm declares` stays as
it is while its fragment is not on the work list; write the reason above the
next time you write its line.

### A gap

Never decide what the norms do not decide (DSM-10). A fragment is a gap when
its case needs something that no norm says, such as:

- what `import:` means, for a program of several files, while no norm says
  it;
- the type of an operation, a conversion, or the text that `print` writes
  for a value, that no norm states;
- an expected output or an error code that does not follow from the norms.

1. Write no declaration for it, and remove any part you began.
2. Write its status line `"state":"pending"`, with a `reason` that says what
   the norms leave open and cites at least one norm involved, as
   `<norm ID>@<norm hash>` (the fragment itself when nothing else fits).
   Keep its `issue` if it has one; otherwise `null`.
3. If it has no issue, open it at once (step 4), one issue for this fragment
   alone. No proposal, no yes. Then go on.

After the work list, for every pending status line that is a gap or not a
whole program (not one of the two fixed reasons), from this run or an
earlier one: with
`"issue": null`, open its issue in this run; with an issue, check it with
`gh issue view <URL> --json state`, keep it when open, and open a new one at
once when closed, with `Related: #<m>`, writing the new URL in its place.

## 3. Seal and check

After each file, and at the end:

```sh
uv run --with "lark[interegular]" python3 -I -B "$S" seal --model <your model ID>
uv run --with "lark[interegular]" python3 -I -B "$S" check
```

`seal` writes the fixed files and the list of derived norms, orders the
status lines as `data/tree.jsonl` and writes the header line (DSM-4 (The first
line of the status file records the specs commit, the generator, the model
and the hashes of the output (NRM-5))), whose `derived_norms_sha256` comes
after `evaluation_sha256` and before `status_sha256`. `--model` is required:
your exact model ID, from your own context, never a family name or a guess.
Exit 2: a missing or malformed input, or a list before the run that it cannot read,
or git that cannot give it (CDN-9); it wrote nothing.

The list of derived norms (DSM-18 (Each declaration of the Lean code is one
derived norm, which the list of derived norms names by its derived norm ID
and its derived norm fingerprint (NRM-12 to NRM-15, CDN-8))) holds one
derived norm per declaration, named by its key (`<path>:<name>`; a tab or
other control character of the key becomes a space in the name, CDN-10 (The name of a derived norm in the list of derived norms is the key of
its item, with each character that a name of NRM-12 may not hold replaced by
one space)), from its
first citation to its last line, with its derived norm ID (`semantics:<n>`)
and its derived norm fingerprint. A declaration keeps its derived norm ID
while it keeps its key; renaming it, or moving it to another file or
namespace, makes it a new derived norm, and its old derived norm ID is gone
for good: do it only when the norms call for it. You never give a derived
norm ID nor compute a derived norm fingerprint: the script does.

`check` copies the project to a temporary folder, runs `lake build` there
(900 seconds at most) and runs each derived fragment (10 seconds each)
(DSM-13 (The script checks the semantics against every fragment, and pending
counts as a failure (NRM-6))). It prints one line per problem,
`<check>: <ID, key or path>: <what>`, then the last line
`fragments: <d> derived, <p> pending; run passed <r>/<R>; error passed <e>/<E>; problems: <n>`.
Exit 0: all passes; 1: problems; 2: an input is missing (the list of derived
norms among them), the grammar does not build, Lark cannot be loaded, or
`lake` cannot be run.

Fix the problems your code or lines caused (`layout`, `comment`, `citation`,
`declaration`, `shortcut`, `status`, `reason-citation`, `opening line`,
`parse`, `build`, `run`), only as the norms allow, and seal again. A `build`
problem gives the first error of Lean: fix the code. A `run` problem names
the fragment and what it gave: fix the semantics from the norms, or, when no
norm says what it should give, mark the fragment a gap.

- `fixed` or `header ... _sha256`: a file changed after the last `seal`: seal
  again once your change is done.
- `header` `generator` or `model`: seal again with your exact model ID.
- `derived-norms`: the list of derived norms does not match the Lean code, or
  gives a derived norm ID again or to another declaration (DSM-18). Never
  edit the list: seal again. If it stays after a `seal`, report it in the end
  report as a defect of the plugin.
- `issue`: two lines hold one URL, or a fixed reason holds an issue. Fix it
  at once: the first line keeps the URL, every other gets `"issue": null`
  and, when it is a gap, its own issue now; a fixed reason gets
  `"issue": null`. Seal and check again, and list each line changed.
- `pending` stays until layer 1 (or the grammar) is fixed.
- `script-citation` needs a new version of the plugin: never change the
  script; step 5.

## 4. The issue of a pending gap, or of an example that is not a whole program

As step 4 of the SKILL.md of `derive-grammar` ("The issue of a pending
fragment", "Fill in the template", "Open it at once"), with these
differences only (DSM-14 (Each pending fragment that is a gap, or an example
that is not a whole program, gets its own issue in layer 1 at once (NRM-8),
and the derivation goes on)):

- Only a gap, or an example that is not a whole program, gets an issue; a
  fragment pending with one of the two fixed reasons gets none.
- The label is `derive-semantics`, never `derive-grammar`: labels exactly
  `finding`, `question`, `derive-semantics`. Create it when missing:

  ```sh
  gh label create derive-semantics -R Ivan-Pasco/clean-language-foundation --color c5def5 --description "Found by /clean-derived-norms:derive-semantics in clean-language-norms" 2>/dev/null
  ```

- The search for a duplicate lists the issues with the label
  `derive-semantics`:
  `gh issue list -R Ivan-Pasco/clean-language-foundation --state all --label derive-semantics -L 5000 --json number,title,state,url`.
- The values: run the snippet of `derive-grammar`, which loads the module
  script `$M`, with its status file
  `"specs-derived/grammar/clean-language-code-examples-status.jsonl"`
  replaced by `"specs-derived/semantics/clean-language-code-examples-status.jsonl"`.
- After the fragment as it is, the body holds its expected output block as it
  is, when it has one (the `tree` command prints its text; write it inside a
  `clean-language-output` fence).
- In the hand-off, layer 2 is `specs-derived/semantics/ (the Lean semantics
  and its status file), derived by /clean-derived-norms:derive-semantics from
  the prose norms and checked against the Clean examples`; the line after it
  is `The semantics never decides what the specs do not say.`; step 3 runs
  `/norms-management:build`, which runs `/clean-derived-norms:derive-semantics`.
- The verification: `in clean-language-norms, after step 3, the status line of
  <ID> in specs-derived/semantics/ is "derived", and check no longer lists
  <ID> as pending.`
- The last line: `Found while deriving the Lean semantics of Clean
  (/clean-derived-norms:derive-semantics), foundation @ <sha>, norms @ <sha>.`

### Not a whole program

The issue of a fragment pending because it is not a whole program (DSM-14,
"The issue of an example that is not a whole program") is opened as a gap's,
with the differences above, the same values, search for a duplicate, title
form and order of the body, and these changes only (as "A malformed opening
line" of `derive-grammar` does for CEX-4):

- `<the gap>` is `an example that is not a whole program (CEX-31)`. Norms
  involved: the fragment itself, `<ID> (<title>) @<hash>`, and any other norm
  of the reason; name the rules as text, `CEX-31 (a Clean example is a whole
  program), CEX-33 (no stub) and CEX-34 (no focus comment) of the plugin
  clean-examples`.
- In place of `**Decision needed** — ...`, the body holds:

  ```markdown
  **Fix needed** — the example uses <the names>, which it does not declare and no norm
  defines (CEX-31: a Clean example is a whole program). Complete it: declare each of them
  as a real part of its program, or repeat the declaration that another Clean example of
  the specs shows (CEX-33). Never a stub, a fake stand-in for a name defined elsewhere
  (CEX-33), and never a focus comment (CEX-34). When the name stands for something that
  the specs define nowhere yet, define it in the specs first; the example stays pending
  until then.
  ```

- In the hand-off, `Problem:` is `fragment <ID> is not a whole program
  (CEX-31): it uses <the names> without declaring them, specs/<file>:<line>.`;
  `Decision:` is `decided by CEX-31 and CEX-33; complete the example as Fix
  needed says.`; step 1 is `1. Show the user the fragment and the names it
  does not declare, short and simple, with where the specs declare each one,
  if they do. Wait for the yes; change nothing before it.`; step 2 is `Complete
  fragment <ID> in specs/<file> (<section>) as Fix needed says, keeping its
  other lines. Show the diff first.`; the verification is `in
  clean-language-norms, after step 3, <ID> is no longer pending in
  specs-derived/semantics/ for a name it does not declare.`; and `Done when:`
  is `the example is a whole program in foundation, and <ID> is no longer
  pending for it in clean-language-norms.`
- Its labels are exactly `finding` and `derive-semantics`, without
  `question`: CEX-31 decides that the example declares what it uses, so
  nothing waits for a decision on the norms.

Append each event to `<scratchpad>/issues-opened.jsonl`, as there.

## 5. The issue of a stale citation of the script

The script cites no norm today: it holds nothing of Clean (DSM-17 (Each
stale cited norm of the script gets its own issue in jpchauny/claude-plugins
at once (CDN-5), and check still fails)). Its `stale-citations` reads the
script alone: the citations of the module script, those of the indenter, are
reported by `derive-grammar`. Run once per run, after the last check:

```sh
uv run --with "lark[interegular]" python3 -I -B "$S" stale-citations > <scratchpad>/stale-citations.jsonl
```

An empty file: nothing to do. Otherwise do step 5 of the SKILL.md of
`derive-grammar`, with: the label `derive-semantics` (created in
`jpchauny/claude-plugins` when missing); the title
`clean-derived-norms derive-semantics: <ID> <changed | was retired | is gone>, its citation is stale (<ID>)`;
the search for titles that begin with `clean-derived-norms derive-semantics: `;
the spec `.../use-cases/derive-semantics/specs/derive-semantics.md` (the path
of each line, `use-cases/derive-semantics/derive_semantics.py`, comes from
`stale-citations`); and
the last line `Found while checking the Lean semantics of Clean
(/clean-derived-norms:derive-semantics), foundation @ <sha>, norms @ <sha>.`

## 6. Show

End with (DSM-15 (The use case ends by showing what it did, the issues it
opened, and the result of the check)):

- The specs commit, the generator (plugin, version, tooling commit) and
  the model, from the header line.
- The count of fragments by state; with none, that layer 2 holds no
  semantic fragment yet.
- The items of the work list, by norm ID or key, and what was done with each.
- The declarations added, changed or removed, by key.
- The fragments newly marked pending, each with its reason.
- From `<scratchpad>/issues-opened.jsonl`: the issues opened (number, title,
  fragment, URL, no parent), the open duplicates commented on, each issue
  that could not be opened with its error, and each body that still holds
  `#<N>`.
- The issues of fragments that are no longer pending: the fix in layer 1 may
  close them.
- The stale citations of the script, if any, with their issues.
- Then the output of `check` and its exit status.

Do not list the derived norms new, changed and gone: the step of layer 2
compares them for its report (NRM-11). When `/norms-management:build` runs
this use case, this report is its part of the build's report; the build
commits and pushes (NRM-9).
