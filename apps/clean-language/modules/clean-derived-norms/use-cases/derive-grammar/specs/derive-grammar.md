# Derive grammar

**Prefix:** DGR

**Audience:** The people who keep layer 2 of the Clean Language project; whoever builds or changes the use case `derive-grammar` of the plugin `clean-derived-norms`

**Scope:** The use case `/clean-derived-norms:derive-grammar`, the generator of the type `grammar`, which derives, from the norms of layer 2, one Lark grammar of Clean ([LAY-3](../../../../../../indra-software-factory/modules/development-methodology/specs/layers.md#rules)). It covers what the use case reads, what it writes, how it splits a fragment into the files of its program and parses each one, how it cites the norms, how it lists its derived norms, how it finds what to derive again, how it verifies, and how a gap goes to layer 1 ([LAY-5](../../../../../../indra-software-factory/modules/development-methodology/specs/layers.md#rules)). The interface that it follows as a generator, NRM-1 to NRM-15, is in norms-management, [NRM-1 to NRM-11](../../../../../../indra-software-factory/modules/norms-management/specs/module.md#derive-the-derived-norms) and [NRM-12 to NRM-15](../../../../../../indra-software-factory/modules/norms-management/specs/module.md#the-list-of-derived-norms), and what holds for every use case of its module, CDN-1 to CDN-10, is in [module.md](../../../specs/module.md#rules); neither is repeated here. The rules of the Clean examples are in [clean-examples](../../../../clean-examples/specs/module.md), and this use case does not check them ([CDN-4](../../../specs/module.md#rules)). Out of scope: the semantics of Clean, and any other type of derived norms; how the norms get their IDs, which is in the specs of `norms-management`; the commit and the push of the output, which the build makes ([NRM-9](../../../../../../indra-software-factory/modules/norms-management/specs/module.md#derive-the-derived-norms)). Each citation line of a derived norm is a citation of a norm, as [LAY-3](../../../../../../indra-software-factory/modules/development-methodology/specs/layers.md#rules) says, in the form of the citation of a norm of [ACU-56](../../../../../../indra-software-factory/modules/acceptance-management/specs/module.md#hashes-and-citations). How an issue is opened is the skill `utilities:issue`; DGR-14 adds what the issue of a pending fragment holds, and that this use case opens it without the yes of the user, DGR-18 does the same for the issue of a stale citation of the script, in `jpchauny/claude-plugins`, and `SKILL.md` holds the templates.

A use case of the module `clean-derived-norms`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md).

The use case has two parts. The script does what is deterministic: the work list, the case of each fragment, the list of derived norms, the header line and the checks. The deriver, following `SKILL.md`, does the derivation: it writes the statements of the grammar and the status lines. The script never writes a statement and never decides a state.

## Terms

| Term | Meaning |
|---|---|
| Use case | The use case `derive-grammar` of the plugin `clean-derived-norms`, invoked as `/clean-derived-norms:derive-grammar`; the actor of every requirement that names no other. A run is one invocation of it, by `/norms-management:build` ([NRM-2](../../../../../../indra-software-factory/modules/norms-management/specs/module.md#derive-the-derived-norms)) or by a person. |
| Repository | The repository of layer 2 of the project, where the use case runs, from its root ([CLN-1](../../../../../specs/app.md#rules)). |
| Script | `use-cases/derive-grammar/derive_grammar.py` of the plugin, run from the root of the repository as `uv run --with "lark[interegular]" python3 -I <script> <command>`. Its commands are `worklist`, `seal --model <model ID>`, `check` and `stale-citations`. The root of the repository of layer 2 is the working directory; the script takes no `--root`. It imports the module script ([CDN-7](../../../specs/module.md#rules)). Its tests are `tests/test_derive_grammar.py` of the module. |
| Code of the script | The code of the script and of the module script ([module.md](../../../specs/module.md#terms)). A line of it is named by the path of its file in the plugin and its number in that file, such as `scripts/derived_norms.py line 753`. |
| Deriver | The AI that runs the use case and writes the grammar. |
| Model ID | The exact ID of the model that the deriver runs as, such as `claude-opus-5-5`, which the deriver knows from its own context. The header line of the status file records it as `model` (DGR-4). Its form is letters, digits, `.`, `-` and `_`, at least one: `^[A-Za-z0-9._-]+$`. |
| Plugin version | The `version` of the `.claude-plugin/plugin.json` of the plugin `clean-derived-norms` that holds the script, a string; the plugin always has one ([NRM-5](../../../../../../indra-software-factory/modules/norms-management/specs/module.md#derive-the-derived-norms)). |
| Tooling commit | The commit of the tooling repository, the marketplace that the plugin was installed from ([NRM-5](../../../../../../indra-software-factory/modules/norms-management/specs/module.md#derive-the-derived-norms), [LAY-14](../../../../../../indra-software-factory/modules/development-methodology/specs/layers.md#the-tooling-repository)), found in this order: the `gitCommitSha` of the entry of `~/.claude/plugins/installed_plugins.json` whose `installPath` is the plugin's root; otherwise the full sha of `HEAD` of the git checkout that holds the plugin's root; otherwise `none`. |
| Norm | A node of `data/tree.jsonl` with its norm ID, such as `EXP-11`. |
| Norm hash | The first 8 hex digits of the `tree_hash` of a norm in `data/tree.jsonl`, such as `e105eaa8` for `EXP-11`. |
| Citation | One comment line `// <norm ID>@<norm hash>: <reason>`, as LAY-3 defines it with the comment mark of Lark, such as `// EXP-11@e105eaa8: ^ is right-associative`. A line is a citation when it matches `^// ([A-Z]{3,}(-[0-9]+)?)@([0-9a-f]{8}): (\S.*)$`. In a status reason and in the code of the script, the same form without `// ` (the code of the script uses `# `). |
| Fragment | As [module.md](../../../specs/module.md#terms) defines it: a norm of `data/tree.jsonl` of kind `code_block`, active, whose code block is a Clean example. |
| Opening line, info string, code | As [clean-examples](../../../../clean-examples/specs/module.md#terms) defines them. Line 1 of the code is the line after the opening line. |
| Prose norm | A norm that is not a fragment, such as `EXP-11` or `FIL-70`. |
| Grammar | The file `specs-derived/grammar/clean.lark`. |
| Statement | One definition of the grammar, a rule or a terminal, or one directive (`%ignore`, `%declare`), with all its lines. |
| Key of a statement | The name of a rule or terminal, such as `power` or `NAME`; for a directive, its exact first line, such as `%ignore COMMENT`. The work list and the check name a statement by its key. |
| Status file | The file `specs-derived/grammar/clean-language-code-examples-status.jsonl`, the status file of the type `grammar` (NRM-5). |
| List of derived norms | The file `specs-derived/grammar/derived-norms.jsonl`, the list of derived norms of the type `grammar` (NRM-12), which `seal` writes (DGR-20). |
| Derived norm, derived norm ID, derived norm fingerprint, lines of a derived norm, citation line, content of a derived norm, list before the run, commit of layer 2 of the run | As the terms of [module.md](../../../specs/module.md#terms) say, which take them from layers.md and norms-management; the module script reads the list before the run as [CDN-9](../../../specs/module.md#rules) says. A derived norm of the grammar is one statement (DGR-20). |
| Case text | The code of a fragment, as DGR-6 "The case text" builds it. The script never cuts it (DGR-6). |
| File line, path of a file line, file of a program, program | As [clean-examples](../../../../clean-examples/specs/module.md#terms) defines them, for the case text. |
| File text | The text of one file of the program of a case, as DGR-19 builds it. A case text with no file line has one file, whose file text is the whole case text. |
| Offset of a file | The offset, in the case text, of the first character of the first line of a file. |
| Case | The case text of a fragment, which the grammar must accept or reject, as its opening line says (DGR-6). A fragment is exactly one case, or none when its opening line is none of the forms of [CEX-4](../../../../clean-examples/specs/module.md#the-opening-line). |
| Expected line | The `<n>` of `line=<n>` in the opening line of a fragment with `expect=syntax-error`. Where its case "reject" may fail is DGR-13. |
| Blank | A space or a tab. No other character, such as a no-break space or a form feed, is a blank. |
| Blank line | A line of a case text that holds nothing, or only blanks. |
| Gap | A fragment that cannot be turned into grammar without deciding something that no fragment and no prose norm says. |
| Foundation | Layer 1, the repository `Ivan-Pasco/clean-language-foundation`. |
| Stale citation of the script | A citation in the code of the script whose norm has another norm hash in `data/tree.jsonl`, is retired, or is gone (DGR-9). A line that tries a citation and is not one is not a stale citation. |
| Stale cited norm | A norm that one or more stale citations of the script name. |
| First words of a norm | The title of a norm that has no heading child, in the issue of a pending fragment and in the issue of a stale cited norm: its text without its leading `#`, `-` and blanks and without any backtick, its whitespace collapsed; when longer than 60 characters, cut at the last space at or before the 60th; then, while it holds more `(` than `)`, cut before its last `(`; then without trailing blanks or `,;:-`. The script computes it (`first_words`). For `LEX-21` it is `Mixing tabs and spaces for indentation is not allowed`, never a cut inside a code span such as `(`SYN0`. |
| Text of a norm | Its `own_text` in a version of `data/tree.jsonl`, then the text of each of its active children in the order of that version, one per line, each piece without its leading and trailing line breaks and the empty ones left out, such as `- one\n- two` for a list of two items. |
| HEAD | The current commit of the repository, as `git rev-parse HEAD` gives it: the full sha of 40 hex digits. |

## Derive the grammar

This section states how the use case derives the grammar, checks it, and hands its gaps to layer 1.

DGR-7 (A partial fragment is not considered) is removed: by a decision of the user, a fragment is derived or pending, and its case comes from its opening line ([CDN-2](../../../specs/module.md#rules), DGR-6). DGR-16 (The run commits and pushes its output to main) is removed: the step of layer 2 commits and pushes the output ([NRM-9](../../../../../../indra-software-factory/modules/norms-management/specs/module.md#derive-the-derived-norms)), and the use case commits nothing. Both numbers stay unused ([SST-7](../../../../../../../specs/spec-structure.md#ids-of-clauses)).

```gherkin
Feature: Derive the grammar of Clean from the norms
  In order to have a grammar of Clean that says only what the norms say, and that shows which norm each rule comes from
  As a person who keeps layer 2 of the Clean Language project
  I want the grammar derived from the fragments, every rule citing its norms, and only what changed derived again

  Rule: DGR-1 The use case reads only layer 2 (NRM-3), and writes in the repository only under specs-derived/grammar/

    Scenario: What the use case reads and writes
      When the use case runs
      Then it reads "data/tree.jsonl" as it is in the working tree, and may read "specs-repo-annotated/"
      And for the old text of a stale cited norm, it reads the versions of "data/tree.jsonl" in the history of HEAD, with git (DGR-18)
      And it reads the grammar, the status file and the list of derived norms, and, with git, the list before the run (DGR-20)
      And it reads the files of its plugin, its "plugin.json" among them, and, for the tooling commit, "~/.claude/plugins/installed_plugins.json" and the git data of the checkout that holds the plugin (DGR-4)
      And it reads the issues of "Ivan-Pasco/clean-language-foundation" (DGR-14) and of "jpchauny/claude-plugins" (DGR-18)
      And it never reads a file of the foundation
      And in the repository it writes only the grammar, the status file and the list of derived norms
      And outside the repository it writes only its work files in the scratchpad (the work list, the titles, bodies and comments of issues, and the record of the issues)
      And, during the run, in the foundation "Ivan-Pasco/clean-language-foundation": the issue of each pending fragment, a comment on an open issue that already has the ID of the fragment, the labels that the foundation lacks, and the edit that writes the number of an issue in its body (DGR-14)
      And, during the run, in "jpchauny/claude-plugins": the issue of each stale cited norm, a comment on an open issue that already has the ID of the norm, the labels that the repository lacks, and the edit that writes the number of an issue in its body (DGR-18)
      And it never writes "data/" or "specs-repo-annotated/", and commits and pushes nothing

  Rule: DGR-2 The grammar comes from the fragments, and from the prose norms that a rule needs

    Scenario: The source of the grammar
      When the deriver writes a rule or a terminal
      Then it comes from one or more fragments, which it cites
      And it may also come from any prose norm that it needs, which it then cites

    Scenario: A technical statement
      Given a statement only serves another one, such as "%ignore COMMENT" or a helper rule
      When the deriver writes it
      Then it cites the norm it serves (DGR-8)
      And a rule or terminal that cites no fragment is used by a statement that cites one

    Scenario Outline: Which code blocks are fragments
      Given the norm "<id>" of kind "code_block" with status "<status>" opens with the line "<opening line>"
      Then it <is> a fragment

      Examples:
        | id      | status  | opening line                                          | is     |
        | SEM-79  | active  | ```clean-language expect=syntax-error code=SYN007 line=1 | is     |
        | LEX-6   | active  | ```clean-language expect=valid                        | is     |
        | MOD-73  | active  |  ```clean-language expect=valid                       | is     |
        | SEM-183 | active  | ```clean-language                                     | is     |
        | FIL-70  | active  | ```clean                                              | is not |
        | ACO-130 | active  | ```toml                                               | is not |
        | EXP-28  | retired | ```clean-language expect=valid                        | is not |

  Rule: DGR-3 The output is one grammar, one status file and one list of derived norms under specs-derived/grammar/

    Scenario: The layout
      When the use case has run
      Then "specs-derived/" holds one folder per type of derived norms
      And "specs-derived/grammar/" holds exactly "clean.lark", "derived-norms.jsonl" and "clean-language-code-examples-status.jsonl"

  Rule: DGR-4 The first line of the status file records the specs commit, the generator, the model and the hashes of the output (NRM-5)

    Scenario: The header line
      Given the header line of "data/tree.jsonl" holds the commit of layer 1 "3a4ba07351c7f3f0f5f7e9a86e583263191ba15e" as "specs_commit" ("foundation_commit" in an older tree)
      And the plugin version is "0.1.0", and the tooling commit is "<sha of 40 hex digits>"
      And the deriver runs as the model "claude-opus-5-5"
      When the script runs "seal --model claude-opus-5-5"
      Then the first line of the status file is
        """
        {"type":"header","specs_commit":"3a4ba07351c7f3f0f5f7e9a86e583263191ba15e","generator":{"plugin":"clean-derived-norms","version":"0.1.0","tooling_commit":"<sha of 40 hex digits>"},"model":"claude-opus-5-5","grammar_sha256":"<sha256 of the grammar>","derived_norms_sha256":"<sha256 of the list of derived norms>","status_sha256":"<sha256 of the other lines of the status file>"}
        """
      And its fields are exactly these seven, in this order: "type", "specs_commit", "generator", "model", "grammar_sha256", "derived_norms_sha256", "status_sha256"
      And "derived_norms_sha256" is the SHA-256 of the list of derived norms that the same "seal" writes (NRM-5, DGR-20)
      And the fields of "generator" are exactly these three, in this order: "plugin", "version", "tooling_commit"
      And the script computes each value itself, except "model", which it takes from "--model"; the deriver writes none of them in the file

    Scenario: The model of the header line
      When the deriver runs "seal"
      Then it passes "--model <model ID>", the exact model ID it runs as, never a family name such as "Opus" or a value it guesses
      And "seal" records the value as given, with no check: "check" judges its form (DGR-13)
      And so a change of the grammar with no change of the specs or of the plugin can be traced to a change of the model

    Scenario: seal without a model
      When the script runs "seal" with no "--model"
      Then it prints an error naming "--model" and exits with 2
      And it writes nothing: the status file keeps its content

    Scenario: seal with a missing or malformed input
      When "data/tree.jsonl" or the grammar does not exist, the grammar is not UTF-8, a line of the status file or of "data/tree.jsonl" is not JSON, the list before the run cannot be read as DGR-20 "A list that cannot be read" says, or the plugin has no "version" in its "plugin.json"
      Then "seal" prints the error and exits with 2, and writes nothing

    Scenario: An unknown tooling commit
      Given the script cannot tell the commit of the checkout of the marketplace that holds the plugin
      When the script runs "seal --model <model ID>"
      Then the header line records "tooling_commit" "none", and "seal" exits with 0
      And it never adds "+dirty"

  Rule: DGR-5 After the header line, the status file has one line for each fragment, and no other

    Scenario: The fields of a status line
      When the deriver writes the status line of a fragment
      Then it holds exactly "type" "fragment", "id", "hash" (its norm hash), "cases", "state", "reason" and "issue", in that order
      And "cases" is the list that the script gives (DGR-6): a list of one, "accept" or "reject", or the empty list when the opening line is none of the forms of CEX-4
      And "state" is "derived" or "pending"
      And a gap, or an opening line that is none of the forms of CEX-4, makes the fragment "pending", and then its case is not parsed
      And "reason" is null if and only if the state is "derived"
      And "issue" is null unless the state is "pending", and then null or "https://github.com/Ivan-Pasco/clean-language-foundation/issues/<n>"
      And an issue URL belongs to one fragment: no two status lines hold the same one (DGR-13, DGR-14)

    Scenario: The order of the lines
      When the script runs "seal --model <model ID>"
      Then the header line is first, and the fragment lines follow the order of "data/tree.jsonl"

    Scenario Outline: The states
      Given the fragment "<id>"
      When the use case has run
      Then its status line is <line>

      Examples:
        | id      | line |
        | SEM-79  | {"type":"fragment","id":"SEM-79","hash":"048fdf74","cases":["reject"],"state":"derived","reason":null,"issue":null} |
        | LAU-42  | {"type":"fragment","id":"LAU-42","hash":"5c1e07a2","cases":["accept"],"state":"derived","reason":null,"issue":null} |
        | COR-638 | {"type":"fragment","id":"COR-638","hash":"9d3a4f10","cases":["accept"],"state":"pending","reason":"no norm says whether onError binds tighter than +: EXP-8@a0b54578, ERR-34@b0f47afe","issue":"<URL of its issue>"} |
        | SEM-183 | {"type":"fragment","id":"SEM-183","hash":"78c5dddb","cases":[],"state":"pending","reason":"the opening line is none of the forms of CEX-4","issue":"<URL of its issue>"} |

    Scenario: A pending gap
      Given the fragment "COR-638" is a gap
      When the use case has run
      Then its state is "pending"
      And its "reason" says what the norms leave open, and cites at least one norm that leaves it open, as "<norm ID>@<norm hash>"
      And its "issue" is null until the issue is opened, and then the URL of the issue

    Scenario Outline: The issue of a fragment that is no longer pending
      Given "COR-638" was "pending" with the issue "https://github.com/Ivan-Pasco/clean-language-foundation/issues/12"
      When the use case has run and "COR-638" <now>
      Then <result>
      And the end report (DGR-15) lists that issue as one that the fix in layer 1 may close

      Examples:
        | now               | result                                |
        | is "derived"      | its "issue" is null                   |
        | is gone           | its status line is removed            |

    Scenario: Every fragment has its line
      When the use case has run
      Then each fragment has exactly one status line, with its current norm hash
      And no status line names a norm that is not a fragment

  Rule: DGR-6 The script takes the one case of a fragment from its opening line, never cuts it, and the deriver decides nothing about it

    Scenario: The case text
      Given a fragment
      When the script takes its case text
      Then the text is the fragment without its opening line and its closing fence, with the indentation of the fence removed from each line, as in "MOD-73"
      And the leading blanks of a line stay as they are: a run of four spaces is never turned into a tab
      And a space in the indentation of a line is refused by the indenter outside brackets (DGR-11), so a case indented with four spaces does not parse
      And a leading tab stays a tab, as in "LEX-182"
      And spaces at the end of a line stay as they are
      And blank lines at the end are dropped, and the text ends with exactly one line break

    Scenario: The case text of LEX-182
      Given the fragment "LEX-182" opens with "```clean-language expect=syntax-error code=SYN011 line=2"
      When the script takes its case text
      Then the text is the two lines below, with one tab before "string", followed by exactly one line break
        """
        start:
        	string notice = "You have {messages.length()} messages"
        """

    Scenario Outline: Accept or reject
      Given the fragment "<id>", whose opening line is "<opening line>"
      When the script takes its case
      Then the case is "<case>"

      Examples:
        | id      | opening line                                              | case   |
        | COR-638 | ```clean-language expect=valid                            | accept |
        | MOD-83  | ```clean-language expect=error code=SEM005                | accept |
        | SEM-79  | ```clean-language expect=syntax-error code=SYN007 line=1  | reject |

    Scenario: The opening line decides the case, and no comment does (CDN-2)
      Given the fragment "LAU-42" opens with "```clean-language expect=valid", and a line of its code holds the comment "// fails: SYN007"
      When the script takes its case
      Then the case is "accept"
      And a case is "reject" only when the opening line has "expect=syntax-error"
      And the script cites no norm for the case: it comes from the opening line, and no comment of the code is read for it

    Scenario: An error that is not of syntax
      Given the fragment "MOD-83" opens with "```clean-language expect=error code=SEM005"
      When the script takes its case
      Then the case is "accept": the text is well formed, and fails in a later phase that the semantics checks

    Scenario Outline: An opening line that is none of the forms of CEX-4
      Given the fragment "SEM-183" opens with "<opening line>"
      When the script takes its case
      Then it gives no case, and its "cases" is the empty list

      Examples:
        | opening line                                          |
        | ```clean-language                                     |
        | ```clean-language expect=syntax-error code=SYN007     |
        | ```clean-language expect=valid line=3                 |
        | ```clean-language  expect=valid                       |
        | ```clean-language expect=error code=sem005            |

    Scenario: A fragment whose opening line is none of the forms of CEX-4 is pending (CDN-3)
      Given the work list gives "SEM-183" with the cases [] (DGR-12)
      When the deriver works on it
      Then it marks it "pending", whatever else it holds
      And its "reason" is "the opening line is none of the forms of CEX-4": CEX-4 is cited as text, not as "<norm ID>@<norm hash>", since it is not a norm of layer 2
      And no statement cites it, and the script does not parse it
      And the run opens its issue in the foundation at once, as DGR-14 says

    Scenario: One case per fragment
      Given a fragment with an opening line of one of the forms of CEX-4
      When the script takes its case
      Then its case is its whole case text, and its "cases" is a list of one, whatever the number of files of its program (DGR-19)
      And the script never cuts a fragment

    Scenario: The error code is not checked
      Given the case of "SEM-79" is "reject"
      When the script checks it
      Then the grammar must reject the text, as DGR-13 says
      And the error code "SYN007" itself, and its prefix, are not checked: they are rules of the examples (CDN-4), and the compiler's business

  Rule: DGR-8 Every statement of the grammar cites its norms, one citation line per norm, just above it

    Scenario: A rule derived from a fragment and two prose norms
      Given the rule "power" comes from the fragment "COR-135" and from the prose norms "EXP-6" and "EXP-11"
      When the deriver writes it
      Then the lines just above it are
        """
        // COR-135@ee2cd287: radius ^ 2.0 inside an expression
        // EXP-6@96dcd388: all binary operators are left-associative except ^
        // EXP-11@e105eaa8: ^ is right-associative
        """

    Scenario: A rule that several fragments show
      Given the fragments "LAU-42" and "FUN-141" both show "host function"
      When the deriver writes the rule of "host function"
      Then it cites both, each on its own line

    Scenario: A new fragment that an existing rule already covers
      Given the rule of "host function" cites "LAU-42" and "FUN-141"
      And a new fragment shows a host function too
      When the deriver derives the new fragment
      Then it adds the citation of the new fragment to that rule, and writes no second rule for it

    Scenario: A technical statement
      Given the statement "%ignore COMMENT" serves the comments of "LEX-6"
      When the deriver writes it
      Then it cites "LEX-6@4b1bae1f" just above it

    Scenario: No statement without a citation
      When the deriver writes the grammar
      Then every statement has at least one citation just above it, with no blank line between
      And every comment line of the grammar is a citation
      And the deriver writes a statement and its citations in the same edit

    Scenario: No import
      When the deriver writes the grammar
      Then it holds no "%import": every terminal is written out and cites the norms it comes from
      And so nothing comes from the common library of Lark, which makes lexical choices that no norm makes

  Rule: DGR-9 Every citation names an active norm, with its norm hash in data/tree.jsonl

    Scenario: Where citations are checked
      When the script runs "check"
      Then it checks every citation of the grammar, every citation in the "reason" of a status line, and every citation in the code of the script

    Scenario Outline: A citation that does not check
      Given <place> holds the citation "<citation>"
      When the script checks it
      Then it reports "<problem>"

      Examples:
        | place                       | citation                                   | problem                                   |
        | the grammar                 | // EXP-999@e105eaa8: a reason              | EXP-999 is not a norm                     |
        | the grammar                 | // EXP-28@76497615: a reason               | EXP-28 is retired                         |
        | the grammar                 | // EXP-11@00000000: a reason               | EXP-11 has the norm hash e105eaa8         |
        | the grammar                 | // COR-638@9d3a4f10: a reason              | COR-638 is pending                        |
        | the grammar                 | // EXP-11@e105eaa8:                        | not a citation                            |
        | the grammar                 | // EXP-11@E105EAA8: x                      | not a citation                            |
        | the reason of "COR-638"     | EXP-8@11111111: onError is not listed      | EXP-8 has the norm hash a0b54578          |
        | the script                  | # LEX-20@11111111: one tab per level       | LEX-20 has the norm hash 8c358626         |

  Rule: DGR-10 The deriver makes no decision that the norms do not make

    Scenario: A gap
      Given a fragment that would hold "integer n = count + text.toInteger() onError 0"
      And no norm says whether "onError" binds tighter than "+": EXP-8 (items EXP-9 to EXP-20) does not list it, and ERR-34 says only "expression onError fallback"
      When the deriver derives it
      Then it writes no rule for it
      And it marks the fragment "pending", with a reason that cites "EXP-8@a0b54578" and "ERR-34@b0f47afe"
      And it goes on with the next item of the work list

    Scenario: A conflict that no norm settles
      Given a statement makes Lark report a shift/reduce or reduce/reduce conflict
      And no cited norm says which way it goes, such as a precedence or an associativity
      When the deriver derives it
      Then the fragments that need it are a gap, as in "A gap"
      And the deriver never settles the conflict by itself

    Scenario: A choice that the norms make
      Given EXP-27 says that a line break inside parentheses does not end the expression
      When the deriver writes the rule of the line break
      Then it writes it, and cites "EXP-27@f74dba8b"

    Scenario: Rewriting a construct for LALR
      Given the construct, as the norms write it, is not LALR(1), such as "expr '+' expr | expr '*' expr"
      When the deriver rewrites it so that the strict LALR build accepts it (DGR-13)
      Then every case keeps the same structure of the construct that the norms describe
      And a rewriting that brings in a precedence, an associativity or an order of evaluation cites the norm that says it, such as "EXP-11@e105eaa8" for "^"
      And when no norm says it, the fragments that need it are a gap, as in "A gap"

  Rule: DGR-11 Indentation, line breaks and names reach the parser through fixed names

    Scenario: The indentation
      When the script builds the parser
      Then the start rule is "start"
      And it uses the Lark indenter with the terminals "_NL", "_INDENT" and "_DEDENT" of the grammar, and with "tab_len" 1, citing "LEX-20@8c358626" (each indentation level is exactly one tab character) in its code
      And which terminals these are, and what they match, is derived and cited like any other statement, as from LEX-11, LEX-20 and EXP-27

    Scenario Outline: A space in the indentation
      Given the case "<text>"
      When the script parses it
      Then the case <result>
      And the indenter reads the indentation from the source after the line break, whatever "_NL" matches
      And it refuses a space in the indentation of a line when no bracket is open, citing "LEX-21@7474dff8" (mixing tabs and spaces for indentation is not allowed) and "EXP-27@f74dba8b" (inside an open parenthesis a line continues) in its code
      And the refusal is a case that does not parse, at the line break before that line

      Examples:
        | text                                     | result                                              |
        | start:\n\tprint(1)\n\t  print(2)\n  | does not parse: a tab and two spaces, no bracket open |
        | start:\n  print(1)\n                   | does not parse: spaces only                          |
        | start:\n\ttotal = (price + tax +\n\t\t shipping + handling)\n | is not refused by the indenter: the parenthesis is open |
        | a block comment whose lines begin with spaces | is not refused: the comment is ignored and holds no line break for the indenter, as in LEX-6 |

    Scenario: The brackets
      When the script builds the parser
      Then the open brackets of the indenter are every terminal named "OPEN_<X>" that has a terminal "CLOSE_<X>", and the close brackets are those "CLOSE_<X>"
      And a line break between an "OPEN_<X>" and its "CLOSE_<X>" does not end a line
      And the grammar names each bracket as a terminal: an anonymous string such as "(" is named "LPAR" by Lark and is not a bracket of the indenter
      And the script reports an "OPEN_<X>" with no "CLOSE_<X>", and a "CLOSE_<X>" with no "OPEN_<X>"

    Scenario: Names and reserved words
      Given the lexer of Lark does not reserve a keyword: where only a name is expected, a keyword is read as a name
      When the deriver writes the terminal "NAME" of identifiers
      Then the terminal "RESERVED" lists, as string alternatives, every reserved keyword and reserved name, citing LEX-37, LEX-46 and LEX-181
      And "NAME" matches no word of "RESERVED"
      And a contextual keyword is not in "RESERVED", and "NAME" may match it, citing LEX-146
      And the script reports each word of "RESERVED" that "NAME" matches

  Rule: DGR-12 Only what a change calls for is derived again (NRM-7)
    Rationale: deriving again only what a change calls for keeps every statement that no change reached as it was, so its derived norm fingerprint does not change for nothing (NRM-7); a new version of the plugin is the exception, since any statement may be one that it fixes and no change of the norms would reach it, and a statement that it leaves as it is keeps its derived norm fingerprint, so only what it corrects makes acceptance units and code stale (NRM-7, LAY-12, ORC-14).

    Scenario Outline: The work list
      Given the status file and the grammar of the previous run
      And <fact>
      When the script runs "worklist"
      Then the work list holds <item>

      Examples:
        | fact                                                                                                     | item |
        | the status file does not exist                                                                           | every fragment, as "new" |
        | "SEM-79" has the norm hash "048fdf74" in its status line and in "data/tree.jsonl"                        | nothing for "SEM-79" |
        | "MOD-83" has "1a2b3c4d" in its status line and "441d1c1c" in "data/tree.jsonl"                           | "MOD-83" as "changed" |
        | the status line of "SEM-79" holds the cases ["accept"], and the script now gives ["reject"]              | "SEM-79" as "changed" |
        | "SEM-79" has a status line and is no longer a fragment                                                   | "SEM-79" as "gone" |
        | "LEX-182" is a fragment with no status line                                                              | "LEX-182" as "new" |
        | "COR-638" is "pending", and neither it nor any norm cited in its reason changed                          | nothing for "COR-638" |
        | "COR-638" is "pending" with "EXP-8@a0b54578" in its reason, and "EXP-8" has another norm hash, or is retired or gone | "COR-638" as "changed" |
        | "SEM-183" is "pending" because its opening line is none of the forms of CEX-4, and it did not change     | nothing for "SEM-183" |
        | the rule "power" cites "EXP-11@e105eaa8" and "EXP-11" now has another norm hash                          | the rule "power" as "norm", with the citation |
        | the rule "power" cites "EXP-11", and "EXP-11" is retired or no longer exists                             | the rule "power" as "norm", with the citation |
        | "%ignore COMMENT" cites "LEX-6" with a stale norm hash                                                   | "%ignore COMMENT" as "norm", with the citation |
        | "SEM-79" moved to another file, with the same norm hash                                                  | nothing for "SEM-79"; only its status line moves, to keep the order of "data/tree.jsonl" |
        | "SEM-79" moved into a list item, so its norm hash changed                                                | "SEM-79" as "changed" |
        | the header line of the status file names, in "generator", another "version" than the plugin version of the plugin that runs "worklist", or none (a new version, NRM-7) | every fragment that has a status line and is still a fragment as "changed", and every statement of the grammar as "version" |
        | the header line of the status file names, in "generator", the plugin version of the plugin that runs "worklist" | no item for that reason |

    Scenario: The output of the work list
      When the script runs "worklist"
      Then it prints one JSON line per item, the fragments in the order of "data/tree.jsonl", then the "gone" ones, then the "norm" ones in the order of the grammar, then the "version" ones in the order of the grammar
      And a fragment item and a "norm" item have exactly "kind" ("new", "changed", "gone" or "norm"), "id" or "statement" (its key), "old_hash", "new_hash", and, for a fragment, its "cases" and its "file", and, for a "norm" item, its "citation"
      And a "version" item has exactly "kind", "statement" (its key), "old_version" (the "version" of "generator" in the header line of the status file, null when there is none) and "new_version" (the plugin version of the plugin that runs "worklist")
      And the "cases" of a "new" or "changed" fragment are the ones that the script gives now from its opening line, [] when it is none of the forms of CEX-4 (DGR-6); a "gone" fragment has no text, so its "cases" are the ones of its old status line
      And it exits with 0, whether the list is empty or not
      And it exits with 2 when "data/tree.jsonl" does not exist, a line of the status file or of "data/tree.jsonl" is not JSON, or the plugin has no "version" in its "plugin.json"

    Scenario: A fragment that is gone
      Given "SEM-79" is in the work list as "gone"
      When the deriver works on it
      Then it removes every citation of "SEM-79" from the grammar
      And it deletes each statement left with no citation
      And each statement that lost a citation of "SEM-79" but keeps others is evaluated again, as an item "norm", against the norms it still cites, and loses what only "SEM-79" called for
      And it removes the status line of "SEM-79"

    Scenario: A statement that cites a changed norm
      Given the rule "power" is in the work list as "norm"
      When the deriver works on it
      Then it evaluates the rule again against the current text of every norm it cites
      And if the rule still follows from them, only the norm hashes of its citations change
      And otherwise it rewrites or removes the rule

    Scenario: A changed fragment
      Given "MOD-83" is in the work list as "changed"
      When the deriver works on it
      Then it derives "MOD-83" again, as a new fragment
      And each statement that cites the old norm hash of "MOD-83" is evaluated again, as an item "norm"

    Scenario: A new version of the plugin derives the whole grammar again (NRM-7)
      Given the header line of the status file names the version "0.3.1" in "generator", and the plugin that runs "worklist" has the plugin version "0.4.0"
      When the script runs "worklist"
      Then every fragment that has a status line is "changed", also when its norm hash and its cases did not change, each new fragment is "new" and each fragment that is gone is "gone"
      And every statement of the grammar is an item "version", with "old_version" "0.3.1" and "new_version" "0.4.0"
      And the deriver evaluates each statement of a "version" item again against the current text of every norm it cites, as for an item "norm", and each "changed" fragment again, as a new fragment
      And a statement that still follows from its norms keeps its content and its citations, so it keeps its derived norm ID and its derived norm fingerprint (NRM-14)
      And a statement that the new version corrects is rewritten or removed, so it gets another derived norm fingerprint, or its derived norm is gone (LAY-12 item 2)
      And "seal" then writes the plugin version "0.4.0" in the header line, so the next run with the same plugin version derives again only what a change calls for

    Scenario: Nothing else is touched
      When the deriver has worked through the work list
      Then every statement and status line that no item reaches keeps the same content
      And a statement that the deriver changes while it works on an item is part of that item, and DGR-15 reports it
      And an empty work list leaves the grammar and the status file with the same content, except the header line
      And a new version of the plugin gives no empty work list while the grammar holds a statement or the status file a fragment line (NRM-7)

    Scenario: The list of derived norms is written again at every run (NRM-7)
      When the deriver has worked through the work list, whether it was empty or not
      Then "seal" writes the list of derived norms again, from the whole grammar and the lists before it (DGR-20)
      And a statement whose citations alone changed, such as only the norm hash of "EXP-11" in the citations of "power", keeps its derived norm ID and gets another derived norm fingerprint (NRM-14)
      And a statement that no item reaches keeps its derived norm ID and its derived norm fingerprint, and only its "first_line" and "last_line" change when the statements above it gained or lost lines

    Scenario: A status file of the local skill
      Given the status file has a header line with no field "generator", as the local skill "/derive-grammar" of the repository of layer 2 wrote it
      When the use case runs
      Then the work list takes the status file and the grammar as absent: every fragment is "new"
      And the run writes both files anew

    Scenario: A status file written before its first line was named the header line
      Given the first line of the status file has "type" "meta", and "generator" holds "plugin", "version" "0.4.0" and "marketplace_commit", as version "0.4.0" of the plugin wrote it
      And the plugin that runs "worklist" has the plugin version "0.5.0"
      When the use case runs
      Then the work list reads that first line as the header line, and its "version" "0.4.0" as the version of the generator: a new version (NRM-5, NRM-7)
      And "seal" drops that line and writes the header line of DGR-4, with "type" "header" and "tooling_commit"

  Rule: DGR-13 The script checks the grammar and the status file, and pending counts as a failure (NRM-6)

    Scenario: The checks
      When the script runs "check"
      Then it builds the grammar with Lark: parser "lalr", lexer "contextual", start "start", strict, with "lark[interegular]", and the indenter of DGR-11
      And the grammar holds no "%import"
      And every statement has at least one citation, and every comment line is a citation
      And every citation of the grammar, of the status reasons and of the script checks (DGR-9)
      And every rule and terminal is used by "start", by another statement or by a directive, or is one of the fixed names of DGR-11
      And every rule and terminal cites a fragment, or is used by a statement that cites one (DGR-2)
      And the brackets, "NAME" and "RESERVED" meet DGR-11
      And every case "accept" of a fragment "derived" parses, each case on its own: every file of its program parses (DGR-19)
      And every case "reject" of a fragment "derived" fails to parse: a file of its program does not parse (DGR-19); and the place of the failure does not end before the line break that ends the line before its expected line: it may be at that line break, at the expected line or later; when the expected line is 1, anywhere
      And the place of a failure is, in the file text: for an unexpected token, the span from its start to its end, or the end of the text for the end of input; for an unexpected character, its position; for an error of the indenter, the span of the "_NL" token it handles; and, in the case text, that span moved by the offset of the file (DGR-19)
      And every fragment whose opening line is none of the forms of CEX-4 is "pending", and its case is not parsed (DGR-6)
      And every fragment cited is "derived", and every fragment "derived" is cited at least once
      And a citation names the fragment, as "<norm ID>@<norm hash>"; "<norm ID>#<n>" is not a citation
      And the header line is first, and every fragment line has the fields, values and order of DGR-5
      And every fragment has exactly one status line, with its current norm hash and the cases that the script gives
      And the specs commit of the header line is the one of "data/tree.jsonl"
      And its generator names the plugin "clean-derived-norms" and the plugin version of the plugin that runs "check"; "check" does not judge its tooling commit
      And its model is a non-empty string of the form of a model ID: "check" cannot know that it is the model that derived, only that the field is there and well formed (DGR-4)
      And the hashes of the header line are the ones of the grammar, the list of derived norms and the status file (DGR-17)
      And the list of derived norms meets DGR-20 "The check of the list"
      And no two status lines hold the same issue URL (DGR-5)
      And no fragment is "pending"

    Scenario: A stale citation of the script
      Given line 753 of the module script holds "# LEX-20@8c358626: each indentation level is exactly one tab character"
      And "data/tree.jsonl" gives "LEX-20" another norm hash, or "LEX-20" is retired or gone
      When the script runs "check"
      Then it reports the problem "script-citation" "LEX-20", naming "scripts/derived_norms.py line 753" and what is wrong, such as "LEX-20 has the norm hash 12345678"
      And it exits with 1, until a new version of the plugin fixes the script
      And the run then opens the issue of "LEX-20" in "jpchauny/claude-plugins" (DGR-18)

    Scenario Outline: One issue URL, one fragment
      Given the status line of "COR-638" holds the issue <first>
      And the status line of "LAU-42" holds the issue <second>
      When the script runs "check"
      Then <result>

      Examples:
        | first                                                            | second                                                           | result |
        | "https://github.com/Ivan-Pasco/clean-language-foundation/issues/12" | "https://github.com/Ivan-Pasco/clean-language-foundation/issues/12" | it reports the problem "issue", naming "COR-638" and "LAU-42" |
        | "https://github.com/Ivan-Pasco/clean-language-foundation/issues/12" | "https://github.com/Ivan-Pasco/clean-language-foundation/issues/13" | it reports no problem "issue" |
        | null                                                             | null                                                             | it reports no problem "issue": a null issue is never compared |

    Scenario: Two status lines with one issue URL are fixed in the same run
      Given the status lines of "COR-638" and "LAU-42" hold the issue "https://github.com/Ivan-Pasco/clean-language-foundation/issues/12", in that order in the status file
      When "check" reports the problem "issue"
      Then the use case fixes it at once, with no question
      And "COR-638", the first of those lines in the order of the status file, keeps the URL
      And "LAU-42" gets "issue": null and, when it is pending, its own issue is opened in the same run, as DGR-14 says
      And the use case runs "seal --model <model ID>" and "check" again, and the end report lists each line changed (DGR-15)

    Scenario Outline: The generator at check time
      Given the header line records the generator <recorded>, and its other fields and hashes are right
      And "check" runs from the plugin "clean-derived-norms" with the plugin version "0.1.0"
      When the script runs "check"
      Then <result>

      Examples:
        | recorded                                                                          | result |
        | {"plugin":"clean-derived-norms","version":"0.1.0","tooling_commit":"<sha>"}   | it reports no problem "header" |
        | {"plugin":"clean-derived-norms","version":"0.1.0","tooling_commit":"none"}    | it reports no problem "header" |
        | {"plugin":"clean-derived-norms","version":"0.0.9","tooling_commit":"<sha>"}   | it reports the problem "header generator", naming both versions |
        | {"plugin":"derive-grammar","version":"0.1.0","tooling_commit":"<sha>"}        | it reports the problem "header generator", naming both names |
        | none: the header line has no field "generator"                                      | it reports the problem "header generator", and that the header line does not have exactly its seven fields |

    Scenario Outline: The model at check time
      Given the header line <model>, and its other fields and hashes are right
      When the script runs "check"
      Then <result>

      Examples:
        | model                                  | result |
        | records "model" "claude-opus-5-5"      | it reports no problem "header" |
        | records "model" "claude-sonnet-4.5"    | it reports no problem "header" |
        | has no field "model"                   | it reports the problem "header" "model", and that the header line does not have exactly its seven fields |
        | records "model" ""                     | it reports the problem "header" "model" |
        | records "model" null, or a number      | it reports the problem "header" "model" |
        | records "model" "claude opus"          | it reports the problem "header" "model": a blank is not of the form of a model ID |

    Scenario Outline: Where a case "reject" must fail
      Given the case "reject" of "<id>", whose expected line is <line>
      And "EXP-147" opens with "```clean-language expect=syntax-error code=SYN002 line=3", and its code is the three lines below, with two tabs before "shipping"
        """
        // ❌ Invalid: multi-line without parentheses
        total = price + tax +
        		shipping
        """
      When the parse of the case <fails>
      Then the check of "<id>" <result>

      Examples:
        | id        | line | fails                                                     | result |
        | SEM-79    | 1    | at line 1                                                 | passes |
        | EXP-147   | 3    | at line 3                                                 | passes |
        | EXP-147   | 3    | at the end of its text                                    | passes |
        | EXP-147   | 3    | at line 1, because the grammar is empty                   | fails  |
        | EXP-147   | 3    | at line 2, before its line break                          | fails  |
        | EXP-147   | 3    | at the line break that ends line 2                        | passes: the indenter reports there the line that does not continue |

    Scenario: No fragment yet
      Given "data/tree.jsonl" holds no fragment
      When the use case runs
      Then the grammar holds no statement, the status file only its header line, and the list of derived norms only its header line
      And "check" does not build the grammar, checks only the header line, the list of derived norms (DGR-20) and the citations of the script, and exits with 0 when they pass
      And the end report says that layer 2 holds no Clean example yet

    Scenario: The last line of check
      When the script runs "check"
      Then its last line is "fragments: <d> derived, <p> pending; accept parsed <a>/<A>; reject rejected <r>/<R>; problems: <n>", each count a decimal number

    Scenario Outline: Exit statuses
      Given <fact>
      When the script runs "check"
      Then it exits with <status>

      Examples:
        | fact                                                                                      | status |
        | every check passes                                                                        | 0      |
        | a conflict makes the strict build fail                                                    | 1      |
        | the grammar does not load, for any other error of the grammar                             | 1      |
        | a case "accept" of "TES-50" does not parse                                                | 1      |
        | a case of "TES-50" makes the indenter raise "DedentError"                                 | 1, as a case that does not parse |
        | the case "reject" of "EXP-147", as above, fails at line 2, before its line break           | 1      |
        | "COR-638" is "pending"                                                                    | 1      |
        | "SEM-183", whose opening line is none of the forms of CEX-4, is "derived"                 | 1      |
        | the status lines of "COR-638" and "LAU-42" hold the same issue URL                        | 1      |
        | a citation of the script names a norm with another norm hash, a retired norm or a norm that is gone | 1 |
        | a line of the status file is not JSON, or lacks a field                                   | 1, naming the file and the line |
        | the grammar holds "%import common.CNAME"                                                  | 1      |
        | the grammar was changed after the last "seal"                                             | 1      |
        | the generator of the header line is not the plugin that runs "check", by name or by version | 1      |
        | the header line has no model, or its model is empty or not of the form of a model ID         | 1      |
        | the list of derived norms does not hold what DGR-20 "The check of the list" says           | 1      |
        | "data/tree.jsonl", the grammar, the status file or the list of derived norms does not exist, the grammar is not UTF-8, or Lark cannot be loaded | 2      |

    Scenario: How problems are shown
      Given a check fails
      When the script runs "check"
      Then it prints one line per problem: the check, the norm ID or the key of the statement, and what is wrong
      And a fragment whose opening line is none of the forms of CEX-4 and that is not "pending" is the problem "opening line", naming CEX-4
      And the last line counts the fragments by state, and the cases "accept" and "reject", each case counted once, that pass

  Rule: DGR-14 Each pending fragment gets its own issue in layer 1 at once (NRM-8), and the derivation goes on

    Scenario: The run
      When "/norms-management:build" runs the use case as the generator of the type "grammar" (NRM-2), or a person invokes "/clean-derived-norms:derive-grammar"
      Then it lists the work, derives every item, opens the issue of each pending fragment, seals and checks, opens the issue of each stale cited norm (DGR-18), and waits for no answer of the user

    Scenario: No yes
      When the use case finds a pending fragment
      Then it opens its issue at once, during the run, without proposing it and without waiting for a yes of the user (decision of the user, 2026-10-23)
      And it writes no message of proposals and no line "↳ ¿anoto? …"
      And when an open issue counts as a duplicate, it comments on it at once, and proposes no link
      And this use case departs from "utilities:issue" only in the yes and in the parent ("No parent"): the template, the search for a duplicate, the labels and the hand-off stay as this rule says

    Scenario: A gap found
      Given the deriver marks "COR-638" pending, with no issue
      When it has written the status line
      Then the use case searches for a duplicate, fills in the template, writes the body of the issue in the scratchpad, and opens the issue at once in the foundation "Ivan-Pasco/clean-language-foundation", unless an open duplicate counts
      And it writes the URL of the issue, or of the open duplicate, in the "issue" of the status line
      And it goes on with the next item, without waiting for an answer

    Scenario: One issue per pending fragment
      Given "COR-638" and "LAU-42" are pending for the same gap, and neither has an issue
      When the use case opens their issues
      Then it opens two issues, one for each fragment
      And never one issue shared by several fragments

    Scenario: No parent
      When the use case opens the issue of a pending fragment
      Then the issue has no parent in the tree of issues
      And the label "derive-grammar" identifies it, and the status file is its index; the baseline is the tree of the findings of a conversation, not of a generator

    Scenario: The search for a duplicate
      Given "COR-638" is pending, with no issue
      When the use case searches for a duplicate, before it opens the issue
      Then it lists the open and closed issues of the foundation with the label "derive-grammar", without the search index of GitHub: gh issue list -R Ivan-Pasco/clean-language-foundation --state all --label derive-grammar -L 5000 --json number,title,state,url
      And a result counts only when its title ends with "(COR-638)"
      And an issue of another fragment is never a duplicate, even with a gap that looks alike
      And when one that counts is open, the use case opens no issue: it comments on that one at once, with the line "Still pending at foundation @ <sha>, norms @ <sha>: <reason>", proposes no link and waits for no yes, and writes its URL in the "issue" of the status line
      And the list does not go through the search index of GitHub, so an issue created a moment ago is already in it, and the use case never opens a second issue for one fragment

    Scenario: A closed duplicate
      Given the search for "COR-638" finds the closed issue #12, whose title ends with "(COR-638)", and no open one that counts
      When the use case opens the issue of "COR-638"
      Then it opens a new issue, whose body holds the line "Related: #12", which links the closed one
      And when several closed issues count, the line links every one of them, such as "Related: #12, #15"
      And it does not reopen a closed one and does not comment on it
      And it writes the URL of the new issue in the "issue" of the status line

    Scenario: The issue of a gap
      Given "COR-638" is pending as a gap, with no issue, and the search found no open duplicate
      When the use case opens its issue, as "utilities:issue" does but without the yes
      Then it opens it in "Ivan-Pasco/clean-language-foundation", in English, with the body written to the scratchpad first
      And its title is "<spec file> — <section>: <the gap in one sentence> (COR-638)", which ends with the ID of the fragment in parentheses
      And its labels are exactly "finding", "question" and "derive-grammar", each created first if the repository lacks it
      And its body holds, in this order: what happens, with the ID of the fragment, its file, its section, the foundation commit, the gap, and each norm involved as "<norm ID> (<title>) @<norm hash>"; the fragment as it is, its opening line and its closing fence included; "Decision needed", with each reading that the specs allow and a ✅ or ❌ minimal example of each, none of them recommended (DGR-10); the line "Related: #<m>, ...", which links on one line every closed issue that counts as a duplicate and every other gap issue that looks alike, when there is one; "Hand-off", in a "text" block of four backticks; and the last line "Found while deriving the Lark grammar of Clean (/clean-derived-norms:derive-grammar), foundation @ <sha>, norms @ <sha>."
      And the hand-off names the issue and the two repositories, says that the fragment is pending with its reason, gives the problem with "specs/<file>:<line>", where "<file>" is the path of the fragment under "specs/" of the foundation, such as "language/syntax/expressions.md", leaves the decision open with the readings numbered as options, says that the fix must change the fragment itself or a norm its reason cites, so that the next run tries it again, and holds the steps, the verification, the rules of the foundation, when it is done, and "Closes #<n>"
      And its verification is that, after "/norms-management:build", which runs the use case (NRM-2), the status line of "COR-638" is "derived" and "check" no longer lists "COR-638" as pending
      And the full template is in "SKILL.md", with where each value comes from: the status line, "data/tree.jsonl" and git
      And once it is opened, the use case at once writes the URL of the issue in the "issue" of the status line
      And then it writes the number of the issue, the last part of its URL, for "#<n>" in the body, never in the line "Related:", and edits the issue with it
      And it seals and checks at the end of the file (DGR-13, DGR-17)

    Scenario: The issue of a fragment whose opening line is none of the forms of CEX-4 (CDN-3)
      Given "SEM-183" is pending because its opening line is none of the forms of CEX-4 (DGR-6), with no issue
      When the use case opens its issue, as for a gap, with the same search for a duplicate, title form and order of the body
      Then its labels are exactly "finding" and "derive-grammar", without "question": CEX-4 decides the form, so nothing waits for a decision on the norms
      And the gap in one sentence is "an opening line that is none of the forms of CEX-4"
      And in place of "Decision needed", the body holds "Fix needed": write the opening line as CEX-4 says, keeping every line of the code byte for byte and in order
      And the hand-off asks for that fix; its first step shows the user the fragment and the opening line to write and waits for the yes; and its verification is that, after "/norms-management:build", the opening line of the fragment is one of the forms of CEX-4 and the fragment is no longer pending for it
      And the full template is in "SKILL.md"

    Scenario: Gaps that look alike
      Given the gaps of "COR-638" and "LAU-42" look alike, and the issue of "COR-638" is #12
      When the use case opens the issue of "LAU-42"
      Then its body holds the line "Related: #12"
      And that line is a link only: each fragment keeps its own issue, and nothing is grouped

    Scenario: An issue that cannot be opened
      Given the use case cannot open the issue of "COR-638", such as when "gh" fails
      When the use case goes on
      Then the "issue" of the status line of "COR-638" stays null
      And the end report (DGR-15) shows the error
      And the next run opens it, as "A pending fragment with no issue" says

    Scenario: A pending fragment with no issue
      Given the status line of "COR-638" is "pending" with "issue": null, left by an earlier run that stopped or whose "gh" failed
      And "COR-638" did not change, so it is not on the work list
      When the use case runs
      Then it opens the issue of "COR-638" in this run, as for any pending fragment, with the search for a duplicate by its ID first
      And it does so for every pending status line with a null issue, whether or not its fragment changed, since a null issue only means that it was not opened yet

    Scenario: An issue whose number cannot be written
      Given the use case opened the issue of "COR-638", and the edit that writes its number in the body fails
      When the use case goes on
      Then the "issue" of the status line of "COR-638" keeps the URL of the issue
      And the end report (DGR-15) says that the body of the issue still holds "#<n>"

    Scenario: A pending fragment that already has its issue
      Given "COR-638" is pending, and its status line holds the URL of an issue
      When the use case runs again and "COR-638" is still pending
      Then it keeps the issue and opens no new one, when that issue is open

    Scenario: A pending fragment whose issue was closed
      Given "COR-638" is still pending, and the issue in its status line is closed
      When the use case runs, whether or not "COR-638" changed
      Then it opens a new issue for "COR-638" at once, with the line "Related: #<m>" naming the closed one, as for a closed duplicate
      And it writes the new URL in the status line of "COR-638", in place of the old one
      And the end report (DGR-15) lists it among the issues opened

  Rule: DGR-15 The use case ends by showing what it did, the issues it opened, and the result of the check
    Rationale: the report is what the person, and the step of layer 2 (NRM-11), see of the run. The derived norms that changed are not in it: NRM-11 is the only rule that compares them, so that the report of the step and the orchestrator (ORC-10) tell the same ones; the use case ends before the commit of layer 2 of the run exists (NRM-9), so a comparison of its own could only take another base, and a run that builds again the same commit of layer 1 would show no change where NRM-11 shows one.

    Scenario: The end of a run
      When the use case has run
      Then it shows the specs commit, the generator (plugin, version and tooling commit) and the model, from the header line
      And the count of fragments by state
      And the items of the work list, by norm ID or key, and what was done with each
      And the statements added, changed or removed, by key
      And the fragments newly marked pending, each with its reason
      And the issues opened in this run, each in one line with its number, its title, its fragment and its URL, with no parent
      And each open duplicate commented on instead, with its fragment and its URL
      And each issue that could not be opened, with its fragment and the error, and each issue whose number could not be written in its body
      And the issues of fragments that are no longer pending, which the fix in layer 1 may close
      And the stale citations of the script, which need a change of the plugin, released as a new version, each with the issue of its norm opened in "jpchauny/claude-plugins", or the open duplicate commented on instead, or the error, and each issue whose number could not be written in its body (DGR-18)
      And then the output of the check, and its exit status
      And it does not list the derived norms new, changed and gone, and its script has no command that compares two lists of derived norms: the step of layer 2 compares them, for its report, as NRM-11 says

  Rule: DGR-17 The grammar, the list of derived norms and the status file change only through a run of the use case

    Scenario: A run seals its output
      When the deriver has worked through the work list
      Then the deriver runs "seal --model <model ID>", with its own model ID, and the script writes the list of derived norms (DGR-20), then the header line with that model and the hashes of the grammar, of the list of derived norms and of the fragment lines
      And the deriver never writes the list of derived norms

    Scenario: A change by hand
      Given a person or another session changed a line of the grammar after the last "seal"
      When the script runs "check"
      Then it reports that the grammar does not match the hash of its header line
      And it exits with 1

    Scenario: A change by hand of the list of derived norms
      Given a person or another session changed a line of the list of derived norms after the last "seal"
      When the script runs "check"
      Then it reports the problem "header" "derived_norms_sha256": the list does not match the hash of its header line
      And it exits with 1

  Rule: DGR-18 Each stale cited norm of the script gets its own issue in jpchauny/claude-plugins at once (CDN-5), and check still fails

    Scenario: The list of the stale citations
      Given line 753 of the module script holds "# LEX-20@8c358626: each indentation level is exactly one tab character"
      And "data/tree.jsonl" gives "LEX-20" the norm hash "12345678"
      When the script runs "stale-citations"
      Then it prints one JSON line per stale cited norm, in the order of its first stale citation in the code of the script, the script first and then the module script, with "id", "state", "current_hash", "new_text" and "citations"
      And "citations" holds, for each line of the code of the script that cites that norm with a stale norm hash, "path" (the path of its file in the plugin, such as "scripts/derived_norms.py"), "line" (its number in that file), "text" (the line without its indentation), "cited_hash", "old_text" and "old_commit"
      And "old_text" is the text of the norm in the newest version of "data/tree.jsonl" in the history of HEAD where the norm has the cited hash, and "old_commit" is the commit of that version; both are null when no version has it, or git cannot run
      And a citation whose norm is active with the cited norm hash gives nothing
      And a line that tries a citation and is not one gives nothing: "check" reports it (DGR-9)
      And it exits with 0, with or without lines, and with 2 when "data/tree.jsonl" does not exist or a line of it is not JSON

    Scenario: The citations of the script
      When the script is written
      Then its code cites "LEX-20@8c358626" (each indentation level is exactly one tab character), "LEX-21@7474dff8" (mixing tabs and spaces for indentation is not allowed) and "EXP-27@f74dba8b" (inside an open parenthesis a line continues), where the indenter uses them (DGR-11), which is in the module script (CDN-7)
      And it cites no norm for the case of a fragment, which comes from the opening line (DGR-6)

    Scenario Outline: The state of a stale cited norm
      Given the script cites "LEX-20@8c358626"
      And in "data/tree.jsonl" "LEX-20" <fact>
      When the script runs "stale-citations"
      Then its "state" is "<state>", its "current_hash" is <current> and its "new_text" is <new>

      Examples:
        | fact                                   | state   | current    | new                                   |
        | is active, with the norm hash 12345678 | changed | "12345678" | its text in "data/tree.jsonl" now     |
        | is retired                             | retired | null       | null                                  |
        | does not exist                         | gone    | null       | null                                  |

    Scenario: The run opens the issues
      Given "check" at the end of the run reports the problem "script-citation" for "LEX-20" (DGR-13)
      When the use case has run "stale-citations"
      Then it opens the issue of "LEX-20" at once, in "jpchauny/claude-plugins", without proposing it and without waiting for a yes of the user (decision of the user, 2026-10-23)
      And "check" still fails with that problem: the issue does not silence it
      And the use case never changes the script: a person fixes it in the plugin, which is released as a new version
      And it goes on with the end report (DGR-15)

    Scenario: One issue per stale cited norm
      Given lines 2 and 9 of the module script cite "LEX-21" with a stale norm hash, and line 5 cites "LEX-20" with one
      When the use case opens their issues
      Then it opens two issues: one for "LEX-21", which names lines 2 and 9, and one for "LEX-20"
      And never one issue shared by several norms

    Scenario: The search for a duplicate
      Given "LEX-20" is a stale cited norm
      When the use case searches for a duplicate, before it opens the issue
      Then it lists the open and closed issues of "jpchauny/claude-plugins" with the label "derive-grammar", without the search index of GitHub: gh issue list -R jpchauny/claude-plugins --state all --label derive-grammar -L 5000 --json number,title,state,url
      And a result counts only when its title begins with "clean-derived-norms derive-grammar: " and ends with "(LEX-20)"
      And when one that counts is open, the use case opens no issue: it comments on that one at once, with one line per stale citation "Still stale at norms @ <sha>: <path> line <line> cites LEX-20@<cited hash>; LEX-20 <now has the norm hash <current hash> | is retired | is gone>.", and waits for no yes
      And when the ones that count are all closed, it opens a new issue whose body holds the line "Related: #<m>, ...", which links every one of them, and it neither reopens nor comments on them

    Scenario: The issue of a stale cited norm
      Given "LEX-20" is a stale cited norm, and the search found no open duplicate
      When the use case opens its issue, as "utilities:issue" does but without the yes
      Then it opens it in "jpchauny/claude-plugins", in English, with its title and its body written to the scratchpad first
      And its title is "clean-derived-norms derive-grammar: LEX-20 <changed | was retired | is gone>, its citation is stale (LEX-20)", which ends with the ID of the norm in parentheses
      And its labels are exactly "finding" and "derive-grammar", each created first if the repository lacks it
      And it has no parent in the tree of issues
      And its body holds, in this order: what happens, with the norm as "<norm ID> (<title>)", its state, the cited norm hash and the current one, the foundation commit and the lines of the code of the script that cite it; those lines, each with its path and its number, in a "python" block; for each cited norm hash, the old text in a "text" block, or the sentence that no version of "data/tree.jsonl" in the history of HEAD has it; the new text in a "text" block, or the sentence that the norm is retired or gone; "Decision needed", which asks whether the code still follows from the new text and recommends no option; the line "Related: #<m>, ..." when a closed duplicate counts; "Hand-off", in a "text" block of four backticks; and the last line "Found while checking the Lark grammar of Clean (/clean-derived-norms:derive-grammar), foundation @ <sha>, norms @ <sha>."
      And the hand-off names the issue and the repository, gives the problem with "apps/clean-language/modules/clean-derived-norms/<path>:<line>" of each of those lines, leaves the decision open with the options numbered, holds the steps, the verification, the rules of the repository and when it is done, and says that the fix is a change of the plugin, released as a new version, not a commit in the repository of layer 2
      And its verification is that the tests of the script pass and that, after the new version of the plugin runs, "check" prints no problem "script-citation" for "LEX-20"
      And the full template is in "SKILL.md", with where each value comes from: "stale-citations", "data/tree.jsonl" and git
      And once it is opened, the use case writes the number of the issue, the last part of its URL, for "#<n>" in the body, never in the line "Related:", and edits the issue with it

    Scenario: An issue that cannot be opened or whose number cannot be written
      Given "gh" fails when the use case opens the issue of "LEX-20", or when it edits its body
      When the use case goes on
      Then the end report (DGR-15) shows the error, or says that the body of the issue still holds "#<n>"
      And the next run, whose "check" still finds the stale citation, searches and opens again, as above

  Rule: DGR-19 The script splits the case text into the files of its program, and parses each file alone, as a whole source file (CDN-6)
    Rationale: one Clean example may hold a program of several files (CEX-35); each file is a source file of its own, so the grammar must take it as one, from its start rule, and never as the tail of the file before it. Splitting by the file lines alone gives every reader the same files, with no model and no reading of the Clean code. Parsing the files in their order, and comparing the first failure with the expected line counted on the whole case text, holds a program of several files to what DGR-13 holds a program of one file to: everything before the expected line parses.

    Scenario: The files of a case text
      Given the case text of a fragment holds one or more file lines
      When the script splits it
      Then it splits it into the files of its program from its file lines alone, as the term file of a program and CEX-35 say
      And no other reading of the case text decides where a file starts: a file line inside a block comment or after an open bracket opens a file too
      And the file text of a file is its lines, its file line first, each followed by one line feed, with the blank lines at its end dropped
      And the path of a file is the path of its file line, as the term says, and a file whose file line has no path has no path
      And the script parses none of the lines before the first file line

    Scenario: The files of a program of two files
      Given the case text is the nine lines below, with one tab before "integer" and before "print", and two tabs before "return"; only the lines and their order bind
        """
        // a program of two files
        // file: app/utils.cln
        functions:
        	integer double(integer n)
        		return n * 2

        // file: app/main.cln
        start:
        	print(double(21))
        """
      When the script splits it
      Then it gives two files, in this order:
        | file | path          | lines of the case text | file text                                         |
        | 1    | app/utils.cln | 2 to 6                 | lines 2 to 5, each with a line feed; line 6, blank, is dropped |
        | 2    | app/main.cln  | 7 to 9                 | lines 7 to 9, each with a line feed               |
      And line 1 belongs to no file, and is not parsed
      And the offset of file 2 is the offset of line 7 in the case text

    Scenario: A case text with no file line
      Given the case text of a fragment holds no file line
      When the script splits it
      Then its program is one file with no path, whose file text is the whole case text and whose offset is 0
      And the script parses it, places a failure and words its message exactly as DGR-13 says, with no word about files

    Scenario: Each file is parsed alone
      When the script parses the program of a case
      Then it parses the file text of each file on its own, from the start rule "start", with the indenter of DGR-11 started anew
      And a comment, a string literal or a bracket that one file leaves open does not go on into the next one (CEX-35)
      And it parses the files in their order, and stops at the first one that does not parse: that failure is the failure of the program
      And the place of the failure of the program, in the case text, is its place in the file text moved by the offset of the file
      And the expected line counts the lines of the whole case text (CEX-6), and DGR-13 compares the place of the failure of the program with it

    Scenario Outline: Where a program of several files fails
      Given the case text of "TST-9" is the one of "The files of a program of two files", and its case is "<case>" with the expected line <line>
      And its parse is: <parse>; this column, not the text of the lines, fixes how each file parses
      When the script checks "TST-9"
      Then <result>

      Examples:
        | case   | line | parse                                                                    | result |
        | accept | none | both files parse                                                         | the case passes |
        | accept | none | file 1 parses, and file 2 fails at its line 3                            | the case fails, and the message names line 9 of the case text, file 2 and its line 3 |
        | reject | 9    | file 1 parses, and file 2 fails at its line 3, which is line 9           | the case passes |
        | reject | 9    | file 1 parses, and file 2 fails at the end of its text                   | the case passes |
        | reject | 9    | file 1 fails at its line 2, which is line 3; file 2 is not parsed        | the case fails: the failure of the program ends before the line break that ends line 8 |
        | reject | 9    | both files parse                                                         | the case fails: the program parses, and its case is "reject" |
        | reject | 1    | file 1 parses, and file 2 fails at its line 2                            | the case passes: with the expected line 1, anywhere |

    Scenario: The message of a failure in a file
      Given the program of a case holds a file line, and its file 2, of the path "app/main.cln", fails at its line 3, which is line 9 of the case text
      When the script words the failure
      Then the message starts with "line 9 (file 2, app/main.cln, line 3): " and goes on with the type of the error and the first line of its text, as for a case text with no file line
      And for a file with no path, it starts with "line 9 (file 2, no path, line 3): "
      And a case text with no file line keeps the message "line <n>: <type of the error>: <first line of its text>"

    Scenario: The script checks no rule of the files (CDN-4, CDN-6)
      Given the program of a fragment has two files with one path, a path that is not of the form of CEX-11, a code line before its first file line, no file or two files with "start:", or an expected line on a file line or before the first file line
      When the script checks it
      Then it reports none of these: they are rules of CEX-20, checked in layers 0 and 1
      And it splits and parses the program all the same, as above: a file line with no path opens a file, two files with one path are two files, and an expected line before the first file line comes before every place of every file

    Scenario: The status file and the work list
      Given a fragment whose program has several files
      Then it is one case, as DGR-6 says, and its status line and its item of the work list have the fields of DGR-5 and DGR-12, and nothing more for its files

  Rule: DGR-20 Each statement of the grammar is one derived norm, which the list of derived norms names by its derived norm ID and its derived norm fingerprint (NRM-12 to NRM-15, CDN-8)
    Rationale: layers 3 and 4 cite a rule of the grammar by its derived norm ID and see that it changed by its derived norm fingerprint, with one reader that knows no type (NRM-12); a statement is the smallest part of the grammar that cites its own norms (DGR-8), so it is the derived norm; its name, which CDN-10 makes from its key, is what keeps it the same from one run to the next, as CDN-8 says for every use case of the module; a name need not be unique, since two keys may give one name (CDN-10), and CDN-8 then pairs the statements of that name in order.

    Scenario: What one derived norm of the grammar is (NRM-15)
      Given the grammar
      Then each statement of the grammar, a rule, a terminal or a directive, is one derived norm, and nothing else of the grammar is one
      And its lines go from the first of the comment lines just above it, with no blank line between (DGR-8), or from its first line when it has none, to its last line that is not blank
      And its name in the list of derived norms is the key of the statement as CDN-10 makes a name of it: the key itself, such as "power", "NAME" or "%ignore COMMENT", when it holds no tab nor other character that CDN-10 replaces
      And its citation lines are the citations of DGR-8, of the form "// <norm ID>@<norm hash>: <reason>": in its lines, each line that matches "^// ([A-Z]{3,}(-[0-9]+)?)@([0-9a-f]{8}): (\S.*)$" once the blanks at its end are removed
      And its "path" is "specs-derived/grammar/clean.lark"
      And a line that is neither a statement, a line of one, a comment line nor a blank line, which "check" reports (DGR-13), is no derived norm
      And what keeps it the same derived norm from one run to the next is its name, as CDN-8 says

    Scenario: A key with a tab (CDN-10)
      Given the grammar holds the directive below, whose first line has a tab between "%ignore" and "WS", and the citation of a norm above it
        """
        // LEX-6@0123abcd: blanks between tokens are ignored
        %ignore<tab>WS
        """
      When the script runs "seal --model <model ID>"
      Then the work list and the check name the statement by its key, "%ignore<tab>WS"
      And its name in the list of derived norms is "%ignore WS", with a space in place of the tab
      And "check" reports no problem "derived-norms" for that name
      And a directive "%ignore WS", with a space, in the same grammar, has the same name, so the first of the two in the order of NRM-13 keeps the lowest derived norm ID of that name in the list before the run, and the second keeps the next one there, or is new when there is none (CDN-8)
      And a second "seal" over the list that the first one wrote, committed as the list before the run, with the grammar unchanged, gives both the derived norm IDs that the first one gave them

    Scenario: The list after a run
      Given the grammar holds, at its lines 40 to 42, the rule "power" below, and the list before the run names "power" with the derived norm ID "grammar:12" and holds "last_derived_norm_number" 41
        """
        // EXP-11@e105eaa8: ^ is right-associative
        // EXP-8@a0b54578: the operators and their order
        power: unary ("^" power)?
        """
      When the script runs "seal --model <model ID>"
      Then the list of derived norms is the binding example of NRM-12, with the line of "power":
        """
        {"kind": "derived_norm", "derived_norm_id": "grammar:12", "derived_norm_fingerprint": "0ced57c3", "name": "power", "path": "specs-derived/grammar/clean.lark", "first_line": 40, "last_line": 42, "cited_norms": [{"norm_id": "EXP-11", "norm_hash": "e105eaa8"}, {"norm_id": "EXP-8", "norm_hash": "a0b54578"}]}
        """
      And each line is the JSON object of its fields as Python's "json.dumps" writes it with "ensure_ascii" false and its default separators, ", " and ": "

    Scenario Outline: The same derived norm (NRM-13)
      Given the list before the run names the statement "<before>" with the derived norm ID "grammar:12"
      And the run <change>
      When the script runs "seal --model <model ID>"
      Then <result>

      Examples:
        | before          | change                                                              | result |
        | power           | rewrites the rule "power", or changes only the reasons of its citations | "power" keeps "grammar:12" |
        | power           | changes the norm hash of "EXP-11" in a citation of "power"          | "power" keeps "grammar:12", with another derived norm fingerprint |
        | power           | moves "power" to another place of the grammar                       | "power" keeps "grammar:12", with other "first_line" and "last_line" |
        | power           | renames the rule "power" to "exponent"                              | "exponent" is a new derived norm, with a new derived norm ID, and "grammar:12" is gone |
        | %ignore COMMENT | writes "%ignore COMMENT" again, citing other norms                  | "%ignore COMMENT" keeps "grammar:12" |
        | %ignore COMMENT | replaces it with "%ignore WS"                                       | "%ignore WS" is a new derived norm, and "grammar:12" is gone |

    Scenario: The derived norm IDs that a seal gives
      When the script runs "seal --model <model ID>"
      Then it gives each statement its derived norm ID as NRM-13 and CDN-8 say, from the list before the run alone: the one of the same name in the list before the run, paired in order when several have one name (CDN-8), otherwise a new one, in the order of NRM-13: by "path", then by "first_line"
      And a list before the run that does not exist counts as a list with no derived norm and "last_derived_norm_number" 0
      And it does not read the list in the working tree, so a later "seal" of the same run gives each new statement its derived norm ID again, in the order of the whole grammar (CDN-8)
      And the deriver gives no derived norm ID and computes no derived norm fingerprint: the script does (NRM-15)

    Scenario: A list that cannot be read
      Given git cannot give the list before the run, in a case of CDN-9 where it cannot be read, or the list before the run has a line that is not UTF-8 or is not a JSON object (an empty line or a line of only blanks is none), or its first line is not a JSON object with "kind" "header", or "meta" as a list written before the header line was named so (NRM-12), "type" "grammar" and "last_derived_norm_number" an integer, 0 or greater
      When the script runs "seal --model <model ID>"
      Then it prints the error, naming the list and, when the error is in a line of it, the line, and exits with 2
      And it writes nothing (DGR-4)
      And so it never gives a derived norm ID again that a list it cannot read may hold
      And its lines are the text between line feeds; only the empty text after the line feed that ends the list is no line

    Scenario: The check of the list
      When the script runs "check"
      Then it checks the list of derived norms against NRM-12 to NRM-14 and against the grammar, and reports each fact below as the problem "derived-norms" (complete list):
        | fact | subject of the problem |
        | the list is not UTF-8, starts with a byte order mark, holds a carriage return, does not end with a line feed, or holds an empty line | "derived-norms.jsonl" or "derived-norms.jsonl:<n>" |
        | a line is not a JSON object, or gives one field twice | "derived-norms.jsonl:<n>" |
        | the first line is not the header line of NRM-12 for the type "grammar": not exactly its three fields in their order, "kind" neither "header" nor "meta" (NRM-12), "type" not "grammar", or "last_derived_norm_number" not an integer, 0 or greater | "derived-norms.jsonl:1" |
        | a line after the first does not have exactly the eight fields of NRM-12 in their order, or "kind" is not "derived_norm" | "derived-norms.jsonl:<n>" |
        | a "derived_norm_id" is not "grammar:<n>", with <n> a number from 1 without leading zeros, or its number is greater than "last_derived_norm_number" | "derived-norms.jsonl:<n>" |
        | a "derived_norm_fingerprint" is not 8 hex digits in lower case | the derived norm ID |
        | a "name" is not a string of NRM-12: empty, only blanks, or with a control character, a line separator or a paragraph separator | the derived norm ID |
        | "first_line" or "last_line" is not an integer from 1, or "first_line" is greater than "last_line" | the derived norm ID |
        | "cited_norms" is not a list of at least one object with exactly "norm_id" (a norm ID) and "norm_hash" (8 hex digits in lower case), in the order of the norm IDs, with no norm ID twice | the derived norm ID |
        | the lines of the derived norms are not in the ascending order of the numbers of their derived norm IDs, or two hold one derived norm ID | the derived norm ID |
        | two derived norms of one file have a line in common | the derived norm ID of the second |
        | a line names a "name", "path", "first_line" and "last_line" that are no derived norm of the grammar | the derived norm ID |
        | a derived norm of the grammar has no line with its name, its "path", its "first_line" and its "last_line" | its name |
        | the "cited_norms" of a derived norm are not the norms, with their norm hashes, that its citation lines cite | the derived norm ID |
        | the "derived_norm_fingerprint" of a derived norm is not the one that NRM-14 computes from its lines and its "cited_norms" | the derived norm ID |
        | the list before the run cannot be read, as "A list that cannot be read" says | "derived-norms.jsonl" |
        | the list before the run holds a greater "last_derived_norm_number" | "derived-norms.jsonl:1" |
        | a derived norm ID that the list before the run also holds names another derived norm there, by name | the derived norm ID |
        | a derived norm ID that the list before the run does not hold has a number not greater than the "last_derived_norm_number" of that list: an ID given again | the derived norm ID |
        | a derived norm of a name that the list before the run gives derived norm IDs does not hold the one that CDN-8 pairs it with: the k-th derived norm of that name in the list, in the order of NRM-13, does not hold the k-th derived norm ID of that name in the list before the run, in the ascending order of their numbers | the name |
      And it prints each one as "derived-norms: <subject>: <what is wrong>", which says the fact and the values involved
      And with no list before the run (CDN-9), or with one that cannot be read, the last four facts are not checked: with none, the type starts from 0 (NRM-13), so none of them can fail; one that cannot be read is the fact before them
      And when a line is not a JSON object or gives one field twice, or the header line does not check, it reports that line and checks no derived norm of the list against the grammar
      And a line that does not have exactly the fields of NRM-12, whose "derived_norm_id" is not "grammar:<n>", whose "name" or "path" is not a string, or whose "first_line" and "last_line" are not line numbers, it reports, and compares neither with the grammar nor with the list before the run; the other lines it checks

    Scenario Outline: A list that does not check
      Given the list of derived norms, sealed from the grammar, then <change>
      And the hash of the header line of the status file is made to match the list again
      When the script runs "check"
      Then it reports "derived-norms" "<subject>", and exits with 1

      Examples:
        | change                                                                        | subject      |
        | gives the derived norm "power" the derived norm fingerprint "00000000"        | grammar:12   |
        | drops the line of "power"                                                     | power        |
        | gives "power" the "last_line" of the line after it                            | grammar:12   |
        | drops "EXP-8" from the "cited_norms" of "power"                               | grammar:12   |
        | gives "power" the "name" ["power"], a JSON array                              | grammar:12   |
        | gives "power" the derived norm ID "grammar:42", with "last_derived_norm_number" 41 | derived-norms.jsonl:<its line> |
```
