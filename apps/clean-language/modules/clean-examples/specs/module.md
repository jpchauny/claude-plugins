# Clean examples

**Prefix:** CEX

**Audience:** The people who write Clean examples in the specs of the project, in layer 0 or layer 1; the Claude sessions that write them; whoever builds the use cases and the hook of the plugin `clean-examples`

**Scope:** The rules of how a Clean example is written, the only place where they are stated; how an example refers to an error code; the hook that refuses a malformed example as it is written. What the audit reports is in [audit.md](../use-cases/audit/specs/audit.md). Out of scope: what a Clean program means, which the specs of the project say; the grammar and the other derived norms, which layer 2 generates

The module `clean-examples` of the app Clean Language, listed in [app.md](../../../specs/app.md).

The Clean examples of the specs are how Clean is defined: the grammar and the
semantics are derived from them in layer 2, and the compiler is tested against
them in layer 3. So every example states, on its opening line, whether its
code is valid or which error it must give, and every example is a whole source
file. The rules below hold in the repositories of layers 0 and 1 of the project
([CLN-1](../../../specs/app.md#rules)).

## Terms

| Term | Meaning |
|---|---|
| Repository | The repository of layer 0 or the repository of layer 1 of the project, found as [ORC-21](../../../../indra-software-factory/modules/project-management/specs/module.md#where-the-repositories-are) says. |
| Spec file | A file of a repository whose name ends in `.md`, that git tracks or that git does not ignore. |
| Fenced block | A fenced code block of CommonMark 0.31.2, section 4.5, in a spec file. |
| Info string | The text of a fenced block's opening line after its fence, without the spaces before and after it. |
| Clean example | A fenced block whose info string is `clean-language`, or starts with `clean-language` followed by a space. |
| Opening line | The first line of a fenced block: its fence and its info string. |
| Attribute | A `<key>=<value>` pair of the info string of a Clean example, after `clean-language`. |
| Code | The lines of a fenced block between its opening line and its closing fence. Line 1 of the code is the line after the opening line. The indentation of the fenced block itself (CommonMark 4.5) is not part of the code. |
| String literal | In the code, text from a `"` to the next `"` that no `\` escapes, on one line. |
| Comment | In the code, outside a string literal: `//` up to the end of its line, or `/*` up to the next `*/`. |
| Code line | A line of the code that holds something other than blanks and comments. |
| Section line | A code line that starts at column 1 and is one of these forms (complete list): `libraries:` followed by names; `import:`; `source:`; `constant:`; `state:`; `can <Name>:`; `class <Name>`, followed or not by more words; `functions:`; `watch <name>:`; `tests:`; `start:`; `compiletime function` followed by more words; `handles block` followed by more words; `host interface` followed by more words and ending with `:`; a library block, a lower-case name followed by `:` and, or not, by more words. A comment at the end of the line is left out. |
| Clean source file | Clean source text that is a whole source file: every code line at column 1 of it is a section line. |
| Error code | A diagnostic code of the project: `PREFIX###`, a prefix of 3 to 6 upper-case ASCII letters and three decimal digits, `^[A-Z]{3,6}[0-9]{3}$`. |
| Definition | A heading of level 3 to 6 of a spec file whose text starts with an error code followed by ` — ` and a title. Illustrative: `### SYN011 — Placeholder Not a Name`. |
| Registry | The spec file `specs/platform/error-codes.md` of the repository of layer 1. |
| Registry row | A row of a table of the registry under its heading `## 5. Code Index` whose first cell holds an error code. |
| Retired code | An error code in the first cell of a row of the table of the registry under its heading `## 6. Reserved Codes`. |
| Violation | One place of a spec file, a line, that breaks one rule of this spec. Each violation names that rule. |

## Where Clean code is written

- **CEX-1.** Every Clean source file of a spec file is written in a Clean example. A code span (CommonMark 6.1) is never a Clean source file.
- **CEX-2.** A fenced block whose info string is `clean`, or starts with `clean` followed by a space, is a violation at its opening line: it is the form that `clean-language` replaces.
- **CEX-3.** Clean text that is not a whole source file is written in a fenced block whose info string is `text`, and is no Clean example. Illustrative: a list of literals; a signature alone.

## The opening line

- **CEX-4.** The info string of a Clean example is exactly one of these forms, with one space between its parts and nothing else (complete list):

  ```text
  clean-language expect=valid
  clean-language expect=syntax-error code=<error code> line=<n>
  clean-language expect=error code=<error code>
  ```

  `<n>` is a decimal number with no leading zero. Any other info string of a Clean example is a violation at its opening line.
- **CEX-5.** `expect=valid`: the code is a correct Clean program. It gives no error code.
- **CEX-6.** `expect=syntax-error`: the code gives the error code, whose prefix is `SYN`. `<n>` is the line of the code that the diagnostic points at, from 1 to the number of lines of the code. A prefix other than `SYN`, or an `<n>` out of that range, is a violation at the opening line.
- **CEX-7.** `expect=error`: the code gives no error code of prefix `SYN`, and gives the error code, whose prefix is not `SYN`, at build or at run time. A prefix `SYN` is a violation at the opening line.
- **CEX-8.** A comment `// prints: <output>` or `// result: <value>` at the end of a code line states what that line prints or computes. It says nothing about whether the code is valid.
- **CEX-9.** A comment of a Clean example that holds `fails:` right after its `//` and the blanks after it is a violation at its line: the opening line states the expected outcome (CEX-4).

## The code

- **CEX-10.** The code of a Clean example with `expect=valid` or `expect=error` is a Clean source file. Each code line at column 1 of it that is not a section line is a violation at its line. Rationale: an example with `expect=syntax-error` may show code at column 1 that is not a section line, when that is the error it shows.
- **CEX-11.** The code holds at most one line that starts at column 1 with `// file: ` followed by a character that is not a blank, and when it holds one, it is line 1. Each other such line is a violation at its line. An example of several source files is written as one Clean example per file.
- **CEX-12.** The code holds at most one syntax error. Two syntax errors are shown in two Clean examples.
- **CEX-13.** The code indents each block with tab characters, one per level. A space in the blanks at the start of a code line is a violation at its line, except (complete list):
  1. on a line that starts while a `(`, `[` or `{` of an earlier line is still open, the brackets inside string literals and comments left out;
  2. in an example with `expect=syntax-error code=SYN003`, which shows an indentation error.

## Error codes

- **CEX-14.** An error code is defined in the spec of the rule that gives it, by its definition. Until its definition is written, its registry row stands for it.
- **CEX-15.** An error code has at most one definition in the spec files of both repositories together. Each definition of a code after the first, in code point order of path and then by line, is a violation at its heading.
- **CEX-16.** The error code of a Clean example has a definition or a registry row in the spec files of both repositories together. An error code that has neither is a violation at the opening line.
- **CEX-17.** A retired code is never the error code of a Clean example: it is a violation at the opening line.
- **CEX-18.** A retired code never gets a definition: its definition is a violation at its heading.
- **CEX-19.** A Clean example only cites its error code, with `code=`, and holds nothing else about it. Illustrative: no comment of the example gives the name, the meaning or the message of its error code.

## What is checked, and by whom

- **CEX-20.** The rules that the text decides alone are checked by the audit and by the hook (complete list): CEX-2, CEX-4, CEX-6 except its first sentence, CEX-7 except its first sentence, CEX-9, CEX-10, CEX-11, CEX-13, CEX-15 to CEX-18. The audit also checks CEX-1 by its fuzzy search ([CAU-6](../use-cases/audit/specs/audit.md#run-the-audit)).
- **CEX-21.** The rules that need a Clean compiler are checked by no use case or hook of this module (complete list): CEX-5, the first sentence of CEX-6, the first sentence of CEX-7, CEX-12. They bind the author of each example. The derived norms of layer 2 check the syntax part of CEX-5, CEX-6 and CEX-7 ([CDN-4](../../clean-derived-norms/specs/module.md#rules)); the tests of layer 3 check all of them, CEX-12 included. CEX-19 binds the author, and nothing checks it.

## The hook

- **CEX-22.** The plugin has a hook before each run of the tools that write a file (complete list): Write, Edit, MultiEdit and NotebookEdit. When the file the tool writes is a spec file, the hook computes the text the file would have after the change, and checks it against the rules of CEX-20, except CEX-1.
- **CEX-23.** The hook refuses the change when the text after it holds a violation in a fenced block that is new, and names, for each, the line, the rule and the message of [CAU-8](../use-cases/audit/specs/audit.md#run-the-audit). A fenced block of the text after the change is new unless the text before holds a fenced block with the same info string and the same code, counted with multiplicity: a block that appears `n` times after and `m` times before, `m < n`, is new `n − m` times. A violation outside every new block never refuses a change. Rationale: moving or reordering blocks refuses nothing, copying a malformed block does, and the examples that exist are migrated with the audit while every other edit of their files goes on.
- **CEX-24.** For CEX-15 to CEX-18 the hook reads the spec files of both repositories, as they are in their working trees, and the file being written as it will be after the change.
- **CEX-25.** When the hook cannot read the other repository or the registry, it skips CEX-15 to CEX-18, checks the other rules, and says which repository or file it did not read and where it expected it.
- **CEX-26.** The hook never changes a file.

## Use cases

| Use case | Spec |
|---|---|
| `audit` | [audit.md](../use-cases/audit/specs/audit.md) |
| `explore` | not yet specified |

## Open questions

1. CEX-5: what context a valid example builds in, such as the libraries in scope, imported files, and names it uses without declaring them. The derived norms of layer 2 need it before they check CEX-5.
2. The format of a definition beyond its heading (name, severity, phase, condition, message template, primary label, suggestion, a passing and a failing example), and the generator in layer 2 of the full list of error codes, belong to the module `clean-derived-norms` and to the project's specs.
3. Which error code code at column 1 that is not a section line gives (the registry has none today), so that an example of it can be written (CEX-10).
