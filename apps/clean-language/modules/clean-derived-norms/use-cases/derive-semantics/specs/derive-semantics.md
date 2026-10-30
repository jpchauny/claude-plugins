# Derive semantics

**Prefix:** DSM

**Audience:** The people who keep layer 2 of the Clean Language project; whoever builds or changes the use case `derive-semantics` of the plugin `clean-derived-norms`; the agents of layers 3 and 4, who read the semantics it derives

**Scope:** The use case `/clean-derived-norms:derive-semantics`, the generator of the type `semantics`, which derives, from the norms of layer 2, one formal semantics of Clean in Lean 4: its abstract syntax, its typing and its evaluation ([LAY-3](../../../../../../indra-software-factory/modules/development-methodology/specs/layers.md#rules)). It covers what the use case reads, what it writes, how the Lean code meets the parse tree of a fragment and of each file of its program, how it cites the norms, how it lists its derived norms, how it finds what to derive again, how it checks the semantics against the fragments and their expected output, and how a gap goes to layer 1 ([LAY-5](../../../../../../indra-software-factory/modules/development-methodology/specs/layers.md#rules)). The interface that it follows as a generator, NRM-1 to NRM-15, is in norms-management, [NRM-1 to NRM-11](../../../../../../indra-software-factory/modules/norms-management/specs/module.md#derive-the-derived-norms) and [NRM-12 to NRM-15](../../../../../../indra-software-factory/modules/norms-management/specs/module.md#the-list-of-derived-norms), and what holds for every use case of its module, CDN-1 to CDN-10, is in [module.md](../../../specs/module.md#rules); neither is repeated here. Where this use case does what the use case `derive-grammar` does, its rule cites the rule of [derive-grammar.md](../../derive-grammar/specs/derive-grammar.md) (DGR) and states only what differs. The rules of the Clean examples, the expected output block among them, are in [clean-examples](../../../../clean-examples/specs/module.md); this use case does not check them ([CDN-4](../../../specs/module.md#rules)). Systems it works with: the grammar of `derive-grammar`, which parses each fragment; Lean 4 and its build tool Lake, which build and run the semantics; GitHub, through `gh`, for the issues. Out of scope: the grammar, which `derive-grammar` derives; the syntax errors of Clean (`expect=syntax-error`), which the grammar checks; the commit and the push of the output, which the build makes ([NRM-9](../../../../../../indra-software-factory/modules/norms-management/specs/module.md#derive-the-derived-norms)); adding the type `semantics` to `derived_norms` of the project's `project.json`, a change of layer 1. The use case must never decide what the norms do not decide.

A use case of the module `clean-derived-norms`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md).

The use case has two parts. The script does what is deterministic: the work list, the case of each fragment, its parse tree, the fixed files of the Lake project, the list of derived norms, the meta line, and the checks, which build the semantics and run every fragment. The deriver, following `SKILL.md`, does the derivation: it writes the Lean code and the status lines. The script never writes a declaration of the Lean code, never decides a state, and holds nothing specific to Clean.

## Terms

| Term | Meaning |
|---|---|
| Use case | The use case `derive-semantics` of the plugin `clean-derived-norms`, invoked as `/clean-derived-norms:derive-semantics`; the actor of every requirement that names no other. A run is one invocation of it, by `/norms-management:build` ([NRM-2](../../../../../../indra-software-factory/modules/norms-management/specs/module.md#derive-the-derived-norms)) or by a person. |
| Repository | The repository of layer 2 of the project, where the use case runs, from its root ([CLN-1](../../../../../specs/app.md#rules)). |
| Script | `use-cases/derive-semantics/derive_semantics.py` of the plugin, run from the root of the repository as `uv run --with "lark[interegular]" python3 -I <script> <command>`. Its commands are `worklist`, `tree <norm ID>...`, `seal --model <model ID>`, `check` and `stale-citations`. It imports the module script, and not the script of `derive-grammar` ([CDN-7](../../../specs/module.md#rules)). Its tests are `tests/test_derive_semantics.py` of the module. |
| Module script | As [module.md](../../../specs/module.md#terms) defines it: the code that the script shares with the script of `derive-grammar`, the parser of the grammar among it. |
| Deriver | The AI that runs the use case and writes the Lean code. |
| Grammar | The file `specs-derived/grammar/clean.lark`, the output of `derive-grammar`. |
| Semantics folder | The folder `specs-derived/semantics/`: a Lake project of Lean 4. |
| Fixed file | One of the files `lakefile.toml`, `lean-toolchain`, `Fragment.lean` and `Main.lean` of the semantics folder, whose text the script holds and writes (DSM-3). |
| Lean code | The files `Clean.lean`, `Clean/Ast.lean`, `Clean/Syntax.lean`, `Clean/Typing.lean` and `Clean/Evaluation.lean` of the semantics folder, which the deriver writes. |
| Status file | The file `specs-derived/semantics/clean-language-code-examples-status.jsonl`, the status file of the type `semantics` (NRM-5). |
| List of derived norms | The file `specs-derived/semantics/derived-norms.jsonl`, the list of derived norms of the type `semantics` (NRM-12), which `seal` writes (DSM-18). |
| Derived norm, derived norm ID, derived norm fingerprint, lines of a derived norm, citation line, content of a derived norm, list before the run | As the terms of [module.md](../../../specs/module.md#terms) say, which take them from layers.md and norms-management; the module script reads the list before the run as [CDN-9](../../../specs/module.md#rules) says. A derived norm of the semantics is one declaration of the Lean code (DSM-18). |
| Lean line comment | In the Lean code, outside a string literal and a character literal: `--` up to the end of its line. |
| Lean block comment | In the Lean code, outside a string literal and a character literal: `/-` up to its matching `-/`, nested ones included; `/--` and `/-!` start one too. |
| Citation | One line `-- <norm ID>@<norm hash>: <reason>` at column 1 of the Lean code, as LAY-3 defines a citation, with the comment mark of Lean, such as `-- TYP-12@4be10a7e: a number never stands for a duration`. A line is a citation when it matches `^-- ([A-Z]{3,}(-[0-9]+)?)@([0-9a-f]{8}): (\S.*)$`. In a status reason, the same form without `-- `; in the script, with `# ` in place of `-- `, as [DGR-9](../../derive-grammar/specs/derive-grammar.md#derive-the-grammar) says. |
| Declaration | A command of the Lean code that defines something, with all its lines: a line that starts at column 1 with one of the words `def`, `theorem`, `abbrev`, `inductive`, `structure`, `class`, `instance`, `opaque`, `example`, `macro`, `macro_rules`, `syntax`, `notation`, `infix`, `infixl`, `infixr`, `prefix`, `postfix` or `deriving instance` (complete list), after any attributes `@[...]` and modifiers `private`, `protected`, `noncomputable`, `partial`, `unsafe` and `nonrec` (complete list), and the lines after it up to the next line at column 1 that starts another declaration, a structural line or a citation. A line at column 1 that starts with `|`, `where`, `deriving`, `termination_by` or `decreasing_by` continues its declaration. |
| Structural line | A line of the Lean code at column 1 that starts with `import`, `namespace`, `end`, `open`, `section`, `mutual`, `variable`, `universe` or `set_option` (complete list). It is no declaration and needs no citation. |
| Key of a declaration | `<path>:<name>`: its path in the semantics folder, and the name after its first word, qualified by the `namespace` lines around it, such as `Clean/Typing.lean:Clean.typeOf`; for a declaration with no name, such as `instance : ToString Value`, `<path>:<its first line>`, without its trailing blanks. The work list and the check name a declaration by its key. |
| Norm, norm hash, model ID, plugin version, marketplace commit, first words of a norm, text of a norm, HEAD, blank, foundation | As [derive-grammar.md](../../derive-grammar/specs/derive-grammar.md#terms) defines them. |
| Fragment | As [module.md](../../../specs/module.md#terms) defines it: a norm of `data/tree.jsonl` of kind `code_block`, active, whose code block is a Clean example. |
| Opening line, info string, code | As [clean-examples](../../../../clean-examples/specs/module.md#terms) defines them. |
| Semantic fragment | A fragment whose info string is not of the form `clean-language expect=syntax-error code=<error code> line=<n>` of [CEX-4](../../../../clean-examples/specs/module.md#the-opening-line). A fragment whose opening line is none of the forms of CEX-4 is a semantic fragment. |
| Expected output block | A norm of `data/tree.jsonl` of kind `code_block`, active, whose info string is exactly `clean-language-output` ([CEX-28](../../../../clean-examples/specs/module.md#the-expected-output)). |
| Expected output of a fragment | The expected output block right after a fragment whose info string is `clean-language expect=valid`: the next active child of the fragment's parent in the order of `data/tree.jsonl`, when it is an expected output block and the own text of the parent between the two holds only blanks and line breaks. A fragment has one or none. |
| Expected output text | The code of an expected output block, without the indentation of its fence, each line followed by one line feed, as [CEX-29](../../../../clean-examples/specs/module.md#the-expected-output) says. |
| Prose norm | A norm that is neither a fragment nor an expected output block. |
| Case | What the semantics must give for a semantic fragment, from its opening line (DSM-6): `run`, or `error <error code>`. A semantic fragment has one case, or none when its opening line is none of the forms of CEX-4. |
| Case text | The code of a fragment, as [DGR-6](../../derive-grammar/specs/derive-grammar.md#derive-the-grammar) builds it. |
| File line, path of a file line, file of a program, program, file text, offset of a file | As [derive-grammar.md](../../derive-grammar/specs/derive-grammar.md#terms) defines them: the files of the case text of a fragment, split as [DGR-19](../../derive-grammar/specs/derive-grammar.md#derive-the-grammar) says. |
| Parse tree | The tree that the grammar gives for the program of a fragment, as DSM-7 builds it: the tree of its one file when its case text holds no file line, otherwise a tree that holds the tree of each file with its path. |
| Serialized tree | The text of a parse tree that the script gives the semantics, in the form of DSM-7. |
| Parse tree hash | The first 8 hex digits of the SHA-256 of the serialized tree of a fragment, in UTF-8. |
| Outcome | What the semantics gives for a parse tree: an error code or none, and a standard output (DSM-11). |
| Gap | A semantic fragment whose case the Lean code cannot give without deciding something that no norm says. |
| Example that is not a whole program | A semantic fragment whose code is no whole program, outside the exception of [CEX-31](../../../../clean-examples/specs/module.md#the-program) for a fragment with `expect=error`: it uses a name that it does not declare, that no norm defines, and whose use with no declaration does not give its error code by a norm. It is a defect of the example, not a gap of the norms. |
| Stale citation of the script, stale cited norm | As derive-grammar.md defines them, for the code of the script of this use case: the script alone. The citations of the module script are the ones of `derive-grammar` (DSM-17). |

The binding words are those of [writing-specs.md](../../../../../../../specs/writing-specs.md#how-to-read-the-rules); the text after `Rationale:` explains and does not bind.

## Derive the semantics

This section states how the use case derives the semantics, checks it against the fragments, and hands its gaps to layer 1.

```gherkin
Feature: Derive the semantics of Clean from the norms
  In order to have a semantics of Clean that says only what the norms say, that runs, and that shows which norm each part comes from
  As a person who keeps layer 2 of the Clean Language project
  I want the semantics derived from the prose norms, checked against every fragment and its expected output, every declaration citing its norms, and only what changed derived again

  Rule: DSM-1 The use case reads only layer 2 and the grammar (NRM-3), and writes in the repository only under specs-derived/semantics/
    Rationale: the semantics reads each fragment as the grammar parses it, so it comes after the grammar and never parses Clean in a way of its own; it writes only its own folder, so the other outputs of layer 2 stay as their generators left them.

    Scenario: What the use case reads and writes
      When the use case runs
      Then it reads "data/tree.jsonl" as it is in the working tree, and may read "specs-repo-annotated/"
      And it reads the grammar, the output of the type "grammar", which "derived_norms" lists before "semantics" (NRM-1, NRM-3)
      And it reads what DGR-1 lists for "derive-grammar", with the semantics folder in place of the grammar's files and the list of derived norms of the type "semantics" in place of the one of "grammar", and the issues of "Ivan-Pasco/clean-language-foundation" and of "jpchauny/claude-plugins"
      And it never reads a file of the foundation, nor "project.json"
      And in the repository it writes only the semantics folder, the list of derived norms among it
      And outside the repository it writes only its work files in the scratchpad, and, during "check", a copy of the semantics folder in a new temporary folder of the system, which "check" removes before it ends
      And, during the run, it writes in "Ivan-Pasco/clean-language-foundation" and in "jpchauny/claude-plugins" only what DGR-1 lists there, for the issues of DSM-14 and DSM-17
      And it never writes "data/", "specs-repo-annotated/" or "specs-derived/grammar/", and commits and pushes nothing

    Scenario: No grammar
      Given the grammar does not exist, or Lark cannot build it as DGR-13 builds it
      When the script runs "worklist", "tree" or "check"
      Then it prints the error, naming the grammar, and exits with 2, and writes nothing
      And the use case stops with that error (NRM-2): "derive-grammar" must run first

  Rule: DSM-2 The semantics comes from the prose norms; the fragments and their expected outputs check it
    Rationale: the prose states the rule, and an example shows one run of it; a semantics built from the examples alone would hold whatever they happen to show, and decide the rest.

    Scenario: The source of the semantics
      When the deriver writes a declaration
      Then it comes from one or more prose norms, which it cites (DSM-8)
      And it may also cite the fragments and the expected output blocks that show what it does
      And a fragment is a check: the deriver never writes a declaration that only one fragment calls for and that no prose norm says

    Scenario Outline: Which fragments are semantic fragments
      Given the fragment "<id>" opens with "<opening line>"
      Then it <is> a semantic fragment

      Examples:
        | id      | opening line                                              | is     |
        | STA-9   | ```clean-language expect=valid                            | is     |
        | TYP-472 | ```clean-language expect=error code=SEM001                | is     |
        | SEM-183 | ```clean-language                                         | is     |
        | EXP-29  | ```clean-language expect=syntax-error code=SYN002 line=4  | is not |

    Scenario Outline: The expected output of a fragment
      Given the fragment "FUN-16" opens with "<opening line>"
      And the next active child of its parent is <next>
      Then the expected output of "FUN-16" is <output>

      Examples:
        | opening line                                | next                                                                                  | output |
        | ```clean-language expect=valid              | the code block "FUN-17" whose info string is "clean-language-output", with a blank line between | "FUN-17" |
        | ```clean-language expect=valid              | the code block "FUN-17" whose info string is "clean-language-output", with no line between     | "FUN-17" |
        | ```clean-language expect=valid              | the paragraph "FUN-17", and the code block "FUN-18" with "clean-language-output" after it      | none     |
        | ```clean-language expect=valid              | the code block "FUN-17" whose info string is "clean-language-output text"                      | none     |
        | ```clean-language expect=error code=SEM004  | the code block "FUN-17" whose info string is "clean-language-output"                           | none: only a fragment with expect=valid has one |

    Scenario: The expected output text
      Given the expected output block "FUN-17" holds the two lines "Hello, World!" and "42" between its fences
      Then its expected output text is "Hello, World!\n42\n", each line followed by one line feed
      And an expected output block with no line has the empty text

    Scenario: A misplaced expected output block is not read
      Given an expected output block is not the expected output of a fragment, as after a paragraph or a second one in a row
      When the use case runs
      Then it reads it as the text of a norm only, and checks no fragment against it
      And it reports nothing about its place: CEX-27 and CEX-28 are rules of the examples, checked in layers 0 and 1 (CDN-4)

  Rule: DSM-3 The output is one Lake project, one list of derived norms and one status file in the semantics folder
    Rationale: a fixed set of files, each with one role, lets the meta line hash each file (NRM-5) and lets an agent of layer 4 find the typing or the evaluation at once; the fixed files are where the script and the Lean code meet, and one text of them, in the script, keeps both sides in step. Deliberate design: the version of Lean is pinned, so that the same Lean code builds and runs the same way in every run; another version of Lean is a new version of the plugin.

    Scenario: The layout
      When the use case has run
      Then the semantics folder holds exactly these files, and no other:
        | file                                         | written by | what it holds |
        | lakefile.toml                                | the script | the Lake project: the libraries "Fragment" and "Clean", and the executable "fragment", whose root is "Main" |
        | lean-toolchain                               | the script | the line "leanprover/lean4:v4.34.1" |
        | Fragment.lean                                | the script | the parse tree, the outcome and the reader of a serialized tree (DSM-7, DSM-11) |
        | Main.lean                                    | the script | the executable that runs one fragment (DSM-11) |
        | Clean.lean                                   | the deriver | "Clean.outcome", which converts the parse tree, types it and evaluates it |
        | Clean/Ast.lean                               | the deriver | the abstract syntax of Clean |
        | Clean/Syntax.lean                            | the deriver | the conversion of a parse tree into the abstract syntax |
        | Clean/Typing.lean                            | the deriver | the typing: the error code that the program gives at build time, if any |
        | Clean/Evaluation.lean                        | the deriver | the evaluation: the error code that the program gives at run time, if any, and its standard output |
        | derived-norms.jsonl                          | "seal"      | the list of derived norms (DSM-18) |
        | clean-language-code-examples-status.jsonl    | the deriver and "seal" | the status file |
      And "Clean.lean" imports the four files of "Clean/", so that one build builds them all

    Scenario: The fixed files
      When the script runs "seal --model <model ID>"
      Then it writes each fixed file with the text that the script holds, whatever the file held before
      And "check" reports each fixed file whose text is not the one that the script holds
      And no fixed file holds anything specific to Clean

  Rule: DSM-4 The first line of the status file records the specs commit, the generator, the model and the hashes of the output (NRM-5)
    Rationale: NRM-5 asks for the hash of each file of the output; with them a change by hand shows (DSM-16), and the specs commit, the generator and the model tell where the semantics comes from.

    Scenario: The meta line
      When the script runs "seal --model claude-opus-5-5"
      Then the first line of the status file is one line of compact JSON with exactly these fields, in this order: "type" ("meta"), "specs_commit", "generator", "model", "lakefile_sha256", "lean_toolchain_sha256", "fragment_sha256", "main_sha256", "clean_sha256", "ast_sha256", "syntax_sha256", "typing_sha256", "evaluation_sha256", "derived_norms_sha256", "status_sha256"
      And "specs_commit", "generator" and "model" are as DGR-4 says, with the plugin "clean-derived-norms"
      And each "<name>_sha256" is the SHA-256 of one file, in this order: "lakefile.toml", "lean-toolchain", "Fragment.lean", "Main.lean", "Clean.lean", "Clean/Ast.lean", "Clean/Syntax.lean", "Clean/Typing.lean", "Clean/Evaluation.lean", the list of derived norms that the same "seal" writes (DSM-18), and the status file without its first line
      And the script computes each value itself, except "model", which it takes from "--model"

    Scenario: seal without a model, with a missing or malformed input, or with an unknown marketplace commit
      When the script runs "seal" as the scenarios of DGR-4 say
      Then it behaves as they say, with the five files of the Lean code in place of the grammar: when one of them does not exist or is not UTF-8, or the list before the run cannot be read as DGR-20 "A list that cannot be read" says, "seal" prints the error and exits with 2, and writes nothing

  Rule: DSM-5 After the meta line, the status file has one line for each semantic fragment, and no other
    Rationale: one line per semantic fragment is the index of what the semantics covers and of what waits for layer 1, and its expected output and parse tree hash tell the work list that a fragment must be checked again. The grammar runs first and opens the issue of each fragment that it cannot take; a second issue for the same fragment and the same fix would split one decision of layer 1 in two.

    Scenario: The fields of a status line
      When the deriver writes the status line of a semantic fragment
      Then it holds exactly "type" "fragment", "id", "hash" (its norm hash), "cases", "expected_output", "parse_tree_hash", "state", "reason" and "issue", in that order
      And "cases" is the list that the script gives (DSM-6): ["run"], ["error <error code>"], or [] when the opening line is none of the forms of CEX-4
      And "expected_output" is "<norm ID>@<norm hash>" of its expected output, or null when it has none
      And "parse_tree_hash" is the parse tree hash that the script gives, or null when the script does not parse it (DSM-7)
      And "state" is "derived" or "pending"
      And "reason" is null if and only if the state is "derived"
      And "issue" is null unless the state is "pending", and then null or "https://github.com/Ivan-Pasco/clean-language-foundation/issues/<n>"
      And no two status lines hold the same issue URL
      And the meta line is first, and the fragment lines follow the order of "data/tree.jsonl" ("seal" orders them)

    Scenario Outline: The states
      Given the semantic fragment "<id>", where only the fields and the reasons bind, and the hashes are illustrative
      When the use case has run
      Then its status line is <line>

      Examples:
        | id      | line |
        | FUN-16  | {"type":"fragment","id":"FUN-16","hash":"509f049c","cases":["run"],"expected_output":"FUN-17@0c1d2e3f","parse_tree_hash":"7a6b5c4d","state":"derived","reason":null,"issue":null} |
        | TYP-472 | {"type":"fragment","id":"TYP-472","hash":"<its norm hash>","cases":["error SEM001"],"expected_output":null,"parse_tree_hash":"<its hash>","state":"derived","reason":null,"issue":null} |
        | STA-9   | {"type":"fragment","id":"STA-9","hash":"<its norm hash>","cases":["run"],"expected_output":null,"parse_tree_hash":"<its hash>","state":"pending","reason":"STA-9 is not a whole program (CEX-31): it uses the name score, which it does not declare and no norm defines: STA-9@<its norm hash>","issue":"<URL of its issue>"} |
        | SEM-183 | {"type":"fragment","id":"SEM-183","hash":"78c5dddb","cases":[],"expected_output":null,"parse_tree_hash":null,"state":"pending","reason":"the opening line is none of the forms of CEX-4","issue":null} |
        | COR-638 | {"type":"fragment","id":"COR-638","hash":"9d3a4f10","cases":["run"],"expected_output":null,"parse_tree_hash":null,"state":"pending","reason":"the grammar does not parse it","issue":null} |

    Scenario Outline: The reasons that open no issue of their own
      Given the semantic fragment "<id>" is pending with the reason "<reason>"
      Then its "issue" is null, and stays null
      And the issue that "derive-grammar" opens for that fragment in layer 1 stands for it (DGR-14)

      Examples:
        | id      | reason                                         |
        | SEM-183 | the opening line is none of the forms of CEX-4 |
        | COR-638 | the grammar does not parse it                  |

    Scenario: The other states and issues
      When a fragment stops being pending, or its issue was closed, or a status line is left with a null issue
      Then the use case does what the scenarios of DGR-5 and DGR-14 say for the grammar, with this status file

  Rule: DSM-6 The script takes the one case of a fragment from its opening line, and its expected output only from its expected output block
    Rationale: the opening line and the expected output block are the only places where an example states its expected outcome (CEX-4, CEX-29, CDN-2); a comment written for a reader is never read as one.

    Scenario Outline: The case
      Given the semantic fragment "<id>", whose opening line is "<opening line>"
      When the script takes its case
      Then its "cases" is <cases>

      Examples:
        | id      | opening line                                  | cases              |
        | FUN-16  | ```clean-language expect=valid                | ["run"]            |
        | TYP-472 | ```clean-language expect=error code=SEM001    | ["error SEM001"]   |
        | SEM-183 | ```clean-language                             | []                 |
        | SEM-184 | ```clean-language expect=error code=sem001    | []                 |

    Scenario: No comment decides the case or the output (CDN-2)
      Given a line of the code of "STA-35" holds the comment "// prints: 42", and "STA-35" has no expected output
      When the script takes its case
      Then its case is "run", and the check compares no output for it (CEX-30)
      And the script reads no comment of the code, for the case or for the output

    Scenario: The case text
      When the script takes the case text of a fragment
      Then it is the case text of DGR-6, the same text that the grammar checks
      And the script never cuts it

  Rule: DSM-7 The script gives the Lean code the parse tree of each fragment in a generic form, and holds nothing specific to Clean
    Rationale: without its keywords and operators, the tree of "integer x = 42" loses "integer", and the semantics could not tell one type from another. Deliberate design: the bridge is generic, so that every choice about Clean is in the Lean code, where it cites its norms; and the script builds the parser with the code of the module script, the code with which the script of derive-grammar builds it (CDN-7), so that the semantics parses each fragment exactly as the check of the grammar does. Deliberate design: a program of several files reaches the Lean code as one value of the same type "Fragment.Tree", under names that no grammar of Lark can give, so that the fixed files stay as they are and the tree of an example of one file stays the same.

    Scenario: The parse
      When the script parses the case text of a semantic fragment that has a case
      Then it builds the parser from the grammar as DGR-11 and DGR-13 build it: the same options, the same indenter, the same refusal of a space in the indentation
      And it splits the case text into the files of its program and parses each file alone, in their order, as DGR-19 says
      And it keeps in the tree every token that Lark leaves out by default, a keyword or an operator that the grammar writes as a string among them, except a token of a terminal that the grammar names with one leading "_", such as "_NL", "_INDENT" and "_DEDENT"
      And a token keeps the type that Lark gives it: the name of its terminal, or, for a string of the grammar, a name that Lark makes, such as "PRINT" or "__ANON_0", which starts with two "_" and is kept
      And it keeps the rules as the grammar shapes them: a rule whose name starts with "_" or "?" is inlined as Lark inlines it

    Scenario: A fragment that the grammar does not parse
      Given the parse of the case text of "COR-638" fails: for a program of several files, the parse of one of its files fails
      When the script gives its "parse_tree_hash"
      Then it is null, and the work list gives the message of the failure as "parse_error", worded as DGR-19 says: for a program of several files, the message of the first file that does not parse
      And the fragment is pending with the reason "the grammar does not parse it", whatever else it holds
      And no fragment with no case, or with no form of CEX-4, is parsed

    Scenario: The parse tree in Lean
      When the Lean code reads a parse tree
      Then it is a value of the type "Fragment.Tree" of "Fragment.lean":
        """
        inductive Tree where
          | rule (name : String) (children : List Tree)
          | token (type : String) (text : String)
          | absent
        """
      And "rule" is a node of the tree with the name of its rule and its children in order, "token" a token with its type and its text, and "absent" the place of an optional part that is missing, which Lark gives as None
      And "Clean/Syntax.lean" converts it into the abstract syntax of "Clean/Ast.lean"; the script knows no rule and no token of Clean

    Scenario: The serialized tree
      When the script gives the semantics a parse tree
      Then it gives its serialized tree: one line per node, in preorder, each line ended by one line feed, in UTF-8:
        """
        rule <name> <number of children>
        token <type> <text>
        absent
        """
      And in "<text>", each "\" is written "\\", each line feed "\n" and each carriage return "\r"; every other character is written as it is
      And, illustrative, the tree of "print("hi")" under a rule "call" of four tokens, whose types the grammar gives, is
        """
        rule call 4
        token PRINT print
        token LPAR (
        token STRING "hi"
        token RPAR )
        """
      And the parse tree hash is computed from this text

    Scenario: The parse tree of a program of several files
      Given the case text of a semantic fragment holds one or more file lines, and every file of its program parses
      When the script gives its parse tree
      Then it is a rule "%program" with one child per file, in the order of the files
      And the child of a file is a rule "%file" with two children: a token of the type "%path" whose text is the path of the file, or "absent" when the file has no path; then the tree of its file text
      And the lines before the first file line are in no part of it
      And no grammar of Lark gives a rule or a token type with a "%": the names "%program", "%file" and "%path" never meet a rule or a terminal of the grammar
      And, illustrative, the serialized tree of the program of the two files of DGR-19 "The files of a program of two files" is
        """
        rule %program 2
        rule %file 2
        token %path app/utils.cln
        <the serialized tree of the file text of app/utils.cln>
        rule %file 2
        token %path app/main.cln
        <the serialized tree of the file text of app/main.cln>
        """

    Scenario: The parse tree of a program of one file
      Given the case text of a semantic fragment holds no file line
      When the script gives its parse tree
      Then it is the tree of its one file, with no "%program" and no "%file"
      And so its serialized tree and its parse tree hash stay as an earlier version of the plugin gave them, and its status line stays valid

    Scenario: The fixed files and a program of several files
      When the Lean code reads the parse tree of a program of several files
      Then it reads it as any other value of "Fragment.Tree", through "Clean.outcome" (DSM-11): the fixed files hold no type and no function for the files
      And "Clean/Syntax.lean" finds each file, with its path, in the children of the rule "%program"

    Scenario: The tree for the deriver
      When the deriver runs "tree STA-9 FUN-16"
      Then the script prints, for each ID in that order, the line "== <norm ID>@<norm hash> cases=<cases> expected_output=<expected output> parse_tree_hash=<hash> <file>", each value as JSON, then its opening line, its case text, the line "-- expected output --" and its expected output text when it has one, and the line "-- parse tree --" and the tree, one node per line, two spaces of indentation per level: a rule as its name, a token as its type and its text as a JSON string, "absent" as "(absent)"
      And when the grammar does not parse it, the line "-- parse error --" and the message, in place of the tree
      And it exits with 0, and with 2, printing nothing, when an ID is not a semantic fragment, or an input is missing as DSM-12 says

  Rule: DSM-8 Every declaration of the Lean code cites its norms, one citation line per norm, just above it
    Rationale: a declaration that shows its norms can be checked against them, and is found again when one of them changes (DSM-12); a comment that is not a citation would say something that no norm checks.

    Scenario: A declaration derived from two prose norms
      Given the function "Clean.typeOf" of "Clean/Typing.lean" comes from the prose norms "TYP-12" and "TYP-188"
      When the deriver writes it
      Then the lines just above its first line are its citations, one per norm, such as
        """
        -- TYP-12@4be10a7e: every value has exactly one type
        -- TYP-188@3c2d1e0f: a number never stands for a duration
        def typeOf (environment : Environment) : Expression → Result Ty
        """
      And no blank line stands between a citation and the line below it

    Scenario: The rules of citations
      When the deriver writes the Lean code
      Then every declaration has at least one citation just above it, and cites at least one prose norm
      And it cites each norm once
      And every Lean line comment is a citation, and no Lean block comment is written: no doc comment, no comment at the end of a line, no indented comment
      And a citation stands just above a declaration, never above a structural line, a blank line or the end of the file
      And a declaration, its attributes and its modifiers start on its first line
      And every line at column 1 of the Lean code that is not blank is a citation, the first line of a declaration, a structural line, or a line that continues a declaration as the term "Declaration" lists
      And the deriver writes a declaration and its citations in the same edit

  Rule: DSM-9 Every citation names an active norm, with its norm hash in data/tree.jsonl
    Rationale: a citation that does not check points at a text that is not the one the declaration came from.

    Scenario: Where citations are checked
      When the script runs "check"
      Then it checks every citation of the Lean code, every citation in the "reason" of a status line, and every citation in the code of the script, as DGR-9 says
      And a cited fragment is "derived" in the status file of the semantics; a cited expected output block, a cited fragment with "expect=syntax-error" and a cited prose norm need only be active with that norm hash

    Scenario Outline: A citation that does not check
      Given <place> holds the citation "<citation>"
      When the script checks it
      Then it reports "<problem>"

      Examples:
        | place                       | citation                                    | problem                          |
        | Clean/Typing.lean           | -- TYP-999@4be10a7e: a reason               | TYP-999 is not a norm            |
        | Clean/Typing.lean           | -- TYP-12@00000000: a reason                | TYP-12 has the norm hash 4be10a7e |
        | Clean/Evaluation.lean       | -- STA-9@<its hash>: a reason               | STA-9 is pending                 |
        | Clean/Typing.lean           | -- TYP-12@4be10a7e:                         | not a citation                   |
        | the reason of "STA-9"       | STA-9@11111111: a reason                    | STA-9 has the norm hash <its hash> |

  Rule: DSM-10 The deriver makes no decision that the norms do not make
    Rationale: layer 2 decides nothing (LAY-3); a semantics that fills a gap, or that knows the fragments by heart, passes every check and says nothing true about any other program.

    Scenario: A gap
      Given a fragment needs something that no norm says, such as the type of an operation that no norm types, or the text that print writes for a value that no norm formats
      When the deriver derives it
      Then it writes no declaration for it, and removes any part it began
      And it marks the fragment "pending", with a reason that says what the norms leave open and cites at least one norm involved, as "<norm ID>@<norm hash>"
      And it goes on with the next item of the work list

    Scenario: An example that is not a whole program
      Given the fragment "STA-9", with "expect=valid", uses the name "score", which its code does not declare, in none of the files of its program
      And no norm defines "score": no norm of the language, and no library that a spec of the project specifies
      When the deriver derives it
      Then it invents no declaration of "score", no value and no type for it, and no context in which an undeclared name is known: nothing outside the code of an example builds its program (CEX-32)
      And "STA-9" is an example that is not a whole program: "pending", with a reason of the form "<norm ID> is not a whole program (CEX-31): it uses <the name or the names>, which it does not declare and no norm defines: <norm ID>@<norm hash>", that names each such name and cites the fragment, and then any other norm involved, such as "STA-9 is not a whole program (CEX-31): it uses the name score, which it does not declare and no norm defines: STA-9@<its norm hash>"
      And CEX-31 is cited as text, not as "<norm ID>@<norm hash>": it is a rule of the examples, not a norm of layer 2
      And it gets its own issue in layer 1 at once, as a defect of the example (DSM-14)
      And the same holds for a fragment with "expect=error" that uses "score" and does not declare it, when no norm gives its error code for a name that is used and not declared

    Scenario: An example of the error of an undeclared name
      Given the fragment "SEM-40" opens with "```clean-language expect=error code=SEM002", and its code uses the variable "lenght", which it does not declare
      And a norm gives the error code "SEM002" for a variable that is used and declared in no enclosing scope
      When the deriver derives it
      Then "SEM-40" is no example that is not a whole program: the exception of CEX-31 covers "lenght"
      And it is checked against its case "error SEM002" as any fragment (DSM-11): "derived" when the Lean code, from that norm, gives "SEM002", and a gap when it cannot without deciding something that no norm says
      And when its code also uses another name that it does not declare, whose use gives no "SEM002", such as a function "report", it is an example that is not a whole program, for that name only

    Scenario: A reason of an earlier version
      Given the status line of "STA-9", written by an earlier version of the plugin, is pending with the reason "STA-9 uses the name score, which it does not declare and no norm declares: STA-9@<its norm hash>"
      When the use case runs, and nothing puts "STA-9" on the work list (DSM-12)
      Then its status line and its issue stay as they are: the work list does not list a fragment for the words of its reason
      And the deriver writes the reason of CEX-31 the next time it writes the status line of "STA-9"

    Scenario: A program of several files that imports a file
      Given the program of a fragment has the files "app/utils.cln" and "app/main.cln", and "app/main.cln" names "app/utils.cln" in its "import:"
      When the deriver derives it
      Then the Lean code finds the imported file only by its path, among the files of the program, and only as the norms define "import:"
      And when no norm says what "import:" means, such as while layer 1 holds no spec of modules, the fragment is a gap: "pending", with a reason that says so and cites the fragment and the norms involved
      And the Lean code never resolves an import by a guess: no other path, no name of a file, no order of the files that a norm does not give

    Scenario: An output or an error code that the norms do not explain
      Given the expected output of a fragment, or its error code, does not follow from the prose norms that the Lean code cites
      When the deriver derives it
      Then the fragment is a gap, and the deriver never shapes the Lean code to give that output or that code without a norm that says it

    Scenario: No shortcut
      When the deriver writes the Lean code
      Then it holds no "sorry", no "admit" and no "axiom"
      And it imports only "Fragment" and the files of "Clean/": nothing of a library, whose choices no norm makes
      And no string literal of it holds the norm ID of a fragment, or is the expected output text of a fragment of two lines or more
      And no part of it tells one fragment from another by its ID or by its text

  Rule: DSM-11 The semantics gives the outcome of a program, and the check compares it with the case of the fragment
    Rationale: one entry point with one result lets the script run any semantics without knowing Clean; the typing comes first because a program that does not build never runs.

    Scenario: The entry point
      When the deriver writes "Clean.lean"
      Then it defines, in the namespace "Clean", "def outcome (tree : Fragment.Tree) : Fragment.Outcome", of the type of "Fragment.lean":
        """
        structure Outcome where
          code : Option String
          output : String
        """
      And "code" is the error code that the program gives, at build time by the typing or at run time by the evaluation, or none; "output" is its standard output, empty when the typing gives a code
      And the typing comes first: when it gives a code, the program does not run

    Scenario: One run of one fragment
      When "check" runs a fragment
      Then it gives its serialized tree on the standard input of the executable "fragment" that the build made
      And the executable prints the code, or "-" for none, then one line feed, then the output, and exits with 0
      And it exits with 2, printing a message on its standard error, when its input is not a serialized tree

    Scenario Outline: Whether a case passes
      Given the fragment has the case "<case>" and <expected>
      And the semantics gives the code <code> and the output "<output>"
      When the script checks it
      Then the case <result>

      Examples:
        | case          | expected                                  | code     | output        | result |
        | run           | the expected output text "42\n"           | none     | 42\n          | passes |
        | run           | the expected output text "42\n"           | none     | 42            | fails: the output differs, byte for byte |
        | run           | the expected output text "42\n"           | "RUN001" | 42\n          | fails: a valid program gives no code |
        | run           | no expected output                        | none     | anything      | passes: no output is compared (CEX-30) |
        | error SEM001  | no expected output                        | "SEM001" | anything      | passes: the output is not compared |
        | error SEM001  | no expected output                        | "SEM004" | (empty)       | fails: another code |
        | error SEM001  | no expected output                        | none     | (empty)       | fails: no code |

  Rule: DSM-12 Only what a change calls for is derived again (NRM-7)
    Rationale: deriving again only what a change calls for keeps every part that no change reached as it was, and the run short (NRM-7); a new version of the plugin is the exception, since any declaration may be one that it fixes and no change of the norms would reach it, and a declaration that it leaves as it is keeps its derived norm fingerprint, so only what it corrects makes acceptance units and code stale (NRM-7, LAY-12).

    Scenario Outline: The work list
      Given the status file and the Lean code of the previous run
      And <fact>
      When the script runs "worklist"
      Then the work list holds <item>

      Examples:
        | fact                                                                                                  | item |
        | the status file does not exist                                                                        | every semantic fragment, as "new" |
        | nothing of "FUN-16" changed: its norm hash, its cases, its expected output and its parse tree hash are those of its status line | nothing for "FUN-16" |
        | "FUN-16" has another norm hash                                                                        | "FUN-16" as "changed" |
        | the expected output of "FUN-16" changed, is new or is gone                                            | "FUN-16" as "changed" |
        | the grammar now gives "FUN-16" another parse tree                                                    | "FUN-16" as "changed" |
        | the case of "FUN-16" changed                                                                          | "FUN-16" as "changed" |
        | "STA-9" is pending, and a norm cited in its reason has another norm hash, is retired or is gone       | "STA-9" as "changed" |
        | "EXP-29", a fragment with "expect=syntax-error", has a status line                                    | "EXP-29" as "gone" |
        | "FUN-16" has a status line and is no longer a fragment                                                | "FUN-16" as "gone" |
        | "Clean/Typing.lean:Clean.typeOf" cites "TYP-12@4be10a7e", and "TYP-12" now has another norm hash, or is retired or gone | that declaration as "norm", with the citation |
        | the meta line of the status file names, in "generator", another "version" than the plugin version of the plugin that runs "worklist", or none (a new version, NRM-7) | every semantic fragment that has a status line as "changed", and every declaration of the Lean code as "version" |

    Scenario: The output of the work list
      When the script runs "worklist"
      Then it prints one JSON line per item, the fragments in the order of "data/tree.jsonl", then the "gone" ones, then the "norm" ones in the order of the Lean code, then the "version" ones in the order of the Lean code
      And a fragment item has exactly "kind" ("new", "changed" or "gone"), "id", "old_hash", "new_hash", "cases", "expected_output", "parse_tree_hash", "parse_error" and "file"; a "gone" one has the "cases", "expected_output" and "parse_tree_hash" of its old status line, "new_hash" and "parse_error" null, and the "file" of its node, or null when the node no longer exists
      And a "norm" item has exactly "kind", "declaration" (its key), "old_hash", "new_hash" (null when the norm is retired or gone) and "citation"
      And a "version" item has exactly "kind", "declaration" (its key), "old_version" (the "version" of "generator" in the meta line of the status file, null when there is none) and "new_version" (the plugin version of the plugin that runs "worklist")
      And it exits with 0, whether the list is empty or not
      And it exits with 2 when "data/tree.jsonl" or the grammar does not exist, a line of the status file or of "data/tree.jsonl" is not JSON, the grammar does not build, Lark cannot be loaded, or the plugin has no "version" in its "plugin.json"

    Scenario: Working through the items
      When the deriver works through the work list
      Then it does what DGR-12 says for the grammar, with declarations in place of statements: a "changed" fragment is checked again against the Lean code, a "gone" one loses its citations and its status line, and a declaration of a "norm" item is evaluated again against the current text of every norm it cites
      And a declaration of a "version" item is evaluated again against the current text of every norm it cites, as for a "norm" item, and a "changed" fragment is checked again, as DGR-12 "A new version of the plugin derives the whole grammar again" says for the grammar: a declaration that still follows keeps its content and its derived norm fingerprint, and one that the new version corrects gets another derived norm fingerprint, or its derived norm is gone
      And every declaration and status line that no item reaches keeps the same content
      And "seal" writes the list of derived norms again at every run, from the whole Lean code, as DGR-12 "The list of derived norms is written again at every run" says, with declarations in place of statements (DSM-18)

  Rule: DSM-13 The script checks the semantics against every fragment, and pending counts as a failure (NRM-6)
    Rationale: a semantics is worth what it runs; a check that builds it and runs every fragment shows at once each case that it does not give.

    Scenario: The checks
      When the script runs "check"
      Then the semantics folder holds exactly the files of DSM-3, each fixed file holds the text that the script holds, and "Clean.lean" imports the four files of "Clean/"
      And the Lean code meets DSM-8, DSM-9 and DSM-10 "No shortcut"
      And the meta line is first and meets DSM-4: its specs commit is the one of "data/tree.jsonl", its generator names the plugin "clean-derived-norms" and the plugin version of the plugin that runs "check", its model is of the form of a model ID, and its hashes are those of the files (DSM-16)
      And the list of derived norms meets DSM-18
      And every status line meets DSM-5, and every semantic fragment has exactly one status line, with its current norm hash, cases, expected output and parse tree hash
      And every fragment with no form of CEX-4 and every fragment that the grammar does not parse is "pending", with its fixed reason of DSM-5 and a null issue
      And every other pending reason cites at least one norm
      And it copies the semantics folder to a new temporary folder, builds it there with "lake build" within 900 seconds, and runs there every "derived" fragment, each within 10 seconds (DSM-11)
      And every case of a "derived" fragment passes (DSM-11)
      And no fragment is "pending"

    Scenario: The last line of check
      When the script runs "check"
      Then its last line is "fragments: <d> derived, <p> pending; run passed <r>/<R>; error passed <e>/<E>; problems: <n>", each count a decimal number
      And "<R>" counts the "derived" fragments of case "run" that it ran, "<E>" those of case "error <code>", and "<r>" and "<e>" the ones that passed

    Scenario: How problems are shown
      Given a check fails
      When the script runs "check"
      Then it prints one line per problem, "<check>: <norm ID, key or path>: <what is wrong>", before the last line
      And the checks are named "layout", "fixed", "comment", "citation", "declaration", "shortcut", "status", "meta", "reason-citation", "opening line", "parse", "pending", "issue", "build", "run", "script-citation" and "derived-norms"

    Scenario Outline: Exit statuses
      Given <fact>
      When the script runs "check"
      Then it exits with <status>

      Examples:
        | fact                                                                                       | status |
        | every check passes                                                                         | 0      |
        | the Lean code does not build                                                               | 1      |
        | the build takes more than 900 seconds                                                      | 1      |
        | the case of "FUN-16" does not pass                                                         | 1      |
        | the run of "FUN-16" takes more than 10 seconds, or its executable exits with a status that is not 0 | 1, as a case that does not pass |
        | "STA-9" is "pending"                                                                       | 1      |
        | a declaration has no citation, or a comment is not a citation                              | 1      |
        | the Lean code holds "sorry"                                                                | 1      |
        | "Fragment.lean" was changed after the last "seal"                                          | 1      |
        | a citation of the script names a norm with another norm hash, a retired norm or a norm that is gone | 1 |
        | the list of derived norms does not hold what DSM-18 says                                   | 1      |
        | "data/tree.jsonl", the grammar, the status file, the list of derived norms or a file of the Lean code does not exist, or a file of the Lean code is not UTF-8 | 2      |
        | the grammar does not build, Lark cannot be loaded, or "lake" cannot be run                 | 2      |

    Scenario: No semantic fragment yet
      Given "data/tree.jsonl" holds no semantic fragment
      When the script runs "check"
      Then it does what DGR-13 "No fragment yet" says: it checks only the meta line, the fixed files, the list of derived norms (DSM-18) and the citations of the script, builds nothing, and exits with 0 when they pass

  Rule: DSM-14 Each pending fragment that is a gap, or an example that is not a whole program, gets its own issue in layer 1 at once (NRM-8), and the derivation goes on
    Rationale: a gap and an example that is not a whole program are fixed in layer 1 (LAY-5); one issue per fragment, opened at once, is how layer 1 learns of it, as for the grammar.

    Scenario: As for the grammar
      When the deriver marks a semantic fragment pending as a gap, or as an example that is not a whole program
      Then the use case opens its issue at once, as DGR-14 says, with no yes of the user and no parent, with these differences only (complete list):
        | in DGR-14                                                      | here |
        | the label "derive-grammar"                                     | the label "derive-semantics" |
        | the search lists the issues with the label "derive-grammar"    | it lists those with the label "derive-semantics" |
        | the last line "Found while deriving the Lark grammar of Clean (/clean-derived-norms:derive-grammar), …" | "Found while deriving the Lean semantics of Clean (/clean-derived-norms:derive-semantics), foundation @ <sha>, norms @ <sha>." |
        | the fragment as it is                                          | the fragment as it is, followed by its expected output block as it is when it has one |
        | the hand-off names "specs-derived/grammar/" and its use case   | it names "specs-derived/semantics/" and "/clean-derived-norms:derive-semantics" |
        | the verification on the status line of the grammar             | the verification on the status line of the semantics: after "/norms-management:build", the fragment is "derived" and "check" no longer lists it as pending |
      And a fragment pending with a fixed reason of DSM-5 gets no issue of its own (DSM-5)

    Scenario: The issue of an example that is not a whole program
      Given "STA-9" is pending because it is not a whole program (DSM-10), with no issue
      When the use case opens its issue at once, as for a gap, with the same search for a duplicate, title form and order of the body, and the differences of "As for the grammar"
      Then its labels are exactly "finding" and "derive-semantics", without "question": CEX-31 decides that the example must declare what it uses, so nothing waits for a decision on the norms
      And the gap in one sentence is "an example that is not a whole program (CEX-31)"
      And in place of "Decision needed", the body holds "Fix needed": the example declares each of them as a real part of its program, or repeats the declaration that another Clean example shows (CEX-33); never a stub, a fake stand-in for a name defined elsewhere (CEX-33), nor a focus comment (CEX-34); and when the specs define no such declaration yet, the specs define it first, and the example stays pending until then
      And the hand-off asks for that fix; its first step shows the user the fragment and the names that it does not declare, and waits for the yes; and its verification is that, after "/norms-management:build", the fragment is no longer pending for that reason
      And the full template is in "SKILL.md"

  Rule: DSM-15 The use case ends by showing what it did, the issues it opened, and the result of the check
    Rationale: as for DGR-15.

    Scenario: The end of a run
      When the use case has run
      Then it shows what DGR-15 lists, with the declarations added, changed or removed, by key, in place of the statements
      And, as DGR-15 says, it does not list the derived norms new, changed and gone, which the step of layer 2 compares as NRM-11 says
      And then the output of the check, and its exit status

  Rule: DSM-16 The output, the list of derived norms among it, changes only through a run of the use case
    Rationale: layer 2 is never edited by hand (LAY-3); the hashes of the meta line show a change that no run made.

    Scenario: A change by hand
      Given a person or another session changed a file of the semantics folder, such as the list of derived norms, after the last "seal"
      When the script runs "check"
      Then it reports that the file does not match the hash of its meta line, and exits with 1, as DGR-17 says

  Rule: DSM-17 Each stale cited norm of the script gets its own issue in jpchauny/claude-plugins at once (CDN-5), and check still fails
    Rationale: a stale citation of the script means that the script may no longer follow its norm, and only a new version of the plugin fixes the script (CDN-5).

    Scenario: As for the grammar
      When the script runs "stale-citations"
      Then it prints what DGR-18 says, for the citations in the code of this script
      And the use case opens the issue of each stale cited norm at once, as DGR-18 says, with the label "derive-semantics", the title "clean-derived-norms derive-semantics: <norm ID> <changed | was retired | is gone>, its citation is stale (<norm ID>)", the path "apps/clean-language/modules/clean-derived-norms/use-cases/derive-semantics/derive_semantics.py" and the last line "Found while checking the Lean semantics of Clean (/clean-derived-norms:derive-semantics), foundation @ <sha>, norms @ <sha>."

    Scenario: The citations of the script
      When the script is written
      Then its code cites no norm: it holds nothing specific to Clean (DSM-7)
      And the parse cites, in the module script, the norms of the indenter (DGR-18), whose stale citations "derive-grammar" reports

  Rule: DSM-18 Each declaration of the Lean code is one derived norm, which the list of derived norms names by its derived norm ID and its derived norm fingerprint (NRM-12 to NRM-15, CDN-8)
    Rationale: an agent of layer 4 cites the typing or the evaluation of one construct by the derived norm ID of its declaration, and sees by its derived norm fingerprint that it changed; a declaration is the smallest part of the Lean code that cites its own norms (DSM-8), so it is the derived norm; its name, which CDN-10 makes from its key, is what keeps it the same from one run to the next, as CDN-8 says for every use case of the module.

    Scenario: What one derived norm of the semantics is (NRM-15)
      Given the Lean code
      Then each declaration of the Lean code is one derived norm, and nothing else of the semantics folder is one: the fixed files, which the script writes, hold none
      And its lines go from the first of the citations just above it, with no blank line between (DSM-8), or from its first line when it has none, to its last line that is not blank, as the term "Declaration" bounds it: the lines of a string literal or of a comment inside it count
      And its name in the list of derived norms is the key of the declaration as CDN-10 makes a name of it: the key itself, such as "Clean/Typing.lean:Clean.typeOf", when it holds no tab nor other character that CDN-10 replaces
      And a declaration with no name whose first line is "instance<tab>: ToString Value", in "Clean/Evaluation.lean", has the key "Clean/Evaluation.lean:instance<tab>: ToString Value" and the name "Clean/Evaluation.lean:instance : ToString Value", which "check" does not report
      And its citation lines are the citations of DSM-8, of the form "-- <norm ID>@<norm hash>: <reason>" at column 1: in its lines, each line that matches "^-- ([A-Z]{3,}(-[0-9]+)?)@([0-9a-f]{8}): (\S.*)$" once the blanks at its end are removed
      And its "path" is the path of its file from the root of the repository, such as "specs-derived/semantics/Clean/Typing.lean"
      And what keeps it the same derived norm from one run to the next is its name, as CDN-8 says
      And its derived norm ID is "semantics:<n>"

    Scenario Outline: The same derived norm (NRM-13)
      Given the list before the run names the declaration "Clean/Typing.lean:Clean.typeOf" with the derived norm ID "semantics:7"
      And the run <change>
      When the script runs "seal --model <model ID>"
      Then <result>

      Examples:
        | change                                                                            | result |
        | rewrites the body of "typeOf", or changes the norm hash in one of its citations   | it keeps "semantics:7", with another derived norm fingerprint |
        | moves "typeOf" to another place of "Clean/Typing.lean", in the same namespace     | it keeps "semantics:7" |
        | moves "typeOf" to "Clean/Evaluation.lean", or renames it                          | its key, and so its name, changes: it is a new derived norm, with a new derived norm ID, and "semantics:7" is gone |

    Scenario: As for the grammar
      When the script runs "seal --model <model ID>" or "check"
      Then it gives the derived norm IDs, writes the list of derived norms, and checks it, also against the list before the run, as DGR-20 says, with these differences only (complete list):
        | in DGR-20                                       | here |
        | a statement of the grammar, and its key         | a declaration of the Lean code, and its key |
        | the type "grammar", "grammar:<n>"               | the type "semantics", "semantics:<n>" |
        | "specs-derived/grammar/derived-norms.jsonl"     | "specs-derived/semantics/derived-norms.jsonl" |
        | the citations of DGR-8, "// "                   | the citations of DSM-8, "-- " |
        | the path "specs-derived/grammar/clean.lark"     | the path of each file of the Lean code |
        | the end report of DGR-15                        | the end report of DSM-15 |
```
