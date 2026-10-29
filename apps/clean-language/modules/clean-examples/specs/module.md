# Clean examples

**Prefix:** CEX

**Audience:** The people who write Clean examples in the specs of the project, in layer 0 or layer 1; the Claude sessions that write them; whoever builds the use cases and the hook of the plugin `clean-examples`

**Scope:** The rules of how a Clean example is written, the only place where they are stated; what program an example holds, and how one example holds a program of several files; how an example refers to an error code; how an example states what it prints, in its expected output block; the hook that refuses a malformed example as it is written. What the audit reports is in [audit.md](../use-cases/audit/specs/audit.md). Out of scope: what a Clean program means, which the specs of the project say; the grammar and the other derived norms, which layer 2 generates

The module `clean-examples` of the app Clean Language, listed in [app.md](../../../specs/app.md).

The Clean examples of the specs are how Clean is defined. In layer 2 the
grammar is derived from them, and the semantics, derived from the prose of the
specs, is checked against them, the expected output of an example included; the
acceptance tests of layer 3 check the compiler, built in layer 4, against them.
So every example states, on its opening line, whether its code is valid or which
error it must give, a valid example may state what it prints, and every example
is a whole program, of one file or of several, that nothing outside it completes.
The rules below hold in the repositories
of layers 0 and 1 of the project ([CLN-1](../../../specs/app.md#rules)).

## Terms

| Term | Meaning |
|---|---|
| Repository | The repository of layer 0 or the repository of layer 1 of the project, found as [ORC-21](../../../../indra-software-factory/modules/project-management/specs/module.md#where-the-repositories-are) says. |
| Spec file | A file of a repository whose name ends in `.md`, that git tracks or that git does not ignore. |
| Fenced block | A fenced code block of CommonMark 0.31.2, section 4.5, in a spec file. |
| Info string | The text of a fenced block's opening line after its fence, without the spaces before and after it. |
| Clean example | A fenced block whose info string is `clean-language`, or starts with `clean-language` followed by a space. |
| Expected output block | A fenced block whose info string is `clean-language-output`, or starts with `clean-language-output` followed by a space. It is no Clean example. |
| Blank line | A line of a spec file that holds nothing, or only spaces and tabs. |
| Standard output | The bytes that a program writes to its standard output stream while it runs, in their order. |
| Opening line | The first line of a fenced block: its fence and its info string. |
| Attribute | A `<key>=<value>` pair of the info string of a Clean example, after `clean-language`. |
| Code | The lines of a fenced block between its opening line and its closing fence. Line 1 of the code is the line after the opening line. The indentation of the fenced block itself (CommonMark 4.5) is not part of the code. |
| String literal | In the code, text from a `"` to the next `"` that no `\` escapes, on one line. |
| Comment | In the code, outside a string literal: `//` up to the end of its line, or `/*` up to the next `*/`. |
| Code line | A line of the code that holds something other than blanks and comments. |
| Section line | A code line that starts at column 1 and is one of these forms (complete list): `libraries:` followed by names; `import:`; `source:`; `constant:`; `state:`; `can <Name>:`; `class <Name>`, followed or not by more words; `functions:`; `watch <name>:`; `tests:`; `start:`; `compiletime function` followed by more words; `handles block` followed by more words; `host interface` followed by more words and ending with `:`; a library block, a lower-case name followed by `:` and, or not, by more words. A comment at the end of the line is left out. |
| Clean source file | A file of a program whose every code line at column 1 is a section line. |
| File line | A line of the code that starts at column 1 with `// file:`. It is a comment. |
| Path of a file line | The text of a file line after its first 9 characters, when they are `// file: `. A file line that does not start with `// file: ` has no path. |
| File of a program | A part of the code of a Clean example, found from its file lines alone (CEX-35): the lines from a file line up to the line before the next file line, or up to the last line of the code. A code with no file line has one file: the whole code. The lines before the first file line belong to no file. |
| Program | The files of the code of a Clean example, together, in their order. A program of several files holds two or more file lines. |
| Whole program | Clean code that, read alone, declares every name that it uses, except a name that a norm of the language, or a library that a spec of the project specifies, defines. |
| Stub | A fake declaration: a function, a class, a value or any other name that an example declares in place of a name that it takes as defined outside its program, by a norm, a library or another spec, with a body, a value or a shape that no spec states. A declaration that is a real part of the program that the example shows is no stub. Illustrative: a function `integer tax(integer amount)` that returns 0 only so that an example of invoices builds is a stub; a variable set from a literal that the program then uses, or a function with its real body that the program defines and calls, is no stub. |
| Focus comment | A comment of the code that sets apart the lines that an example is about from the lines that only complete its program. Illustrative: `// focus`, `// --- the example starts here ---`. |
| Error code | A diagnostic code of the project: `PREFIX###`, a prefix of 3 to 6 upper-case ASCII letters and three decimal digits, `^[A-Z]{3,6}[0-9]{3}$`. |
| Definition | A heading of level 3 to 6 of a spec file whose text starts with an error code followed by ` — ` and a title. Illustrative: `### SYN011 — Placeholder Not a Name`. |
| Registry | The spec file `specs/platform/error-codes.md` of the repository of layer 1. |
| Registry row | A row of a table of the registry under its heading `## 5. Code Index` whose first cell holds an error code. |
| Retired code | An error code in the first cell of a row of the table of the registry under its heading `## 6. Reserved Codes`. |
| Violation | One place of a spec file, a line, that breaks one rule of this spec. Each violation names that rule. |

## Where Clean code is written

- **CEX-1.** Every whole program that a spec file shows is written in one Clean example, all its files in it. A code span (CommonMark 6.1) never holds a whole program.
- **CEX-2.** A fenced block whose info string is `clean`, or starts with `clean` followed by a space, is a violation at its opening line: it is the form that `clean-language` replaces.
- **CEX-3.** Clean text that a spec file shows as a part of a program, and not as a whole program, is written in a fenced block whose info string is `text`, and is no Clean example. Illustrative: a list of literals; a signature alone; a part of a program that the prose around it explains. A Clean example whose code is not yet a whole program is no such text: it stays a Clean example, is completed as CEX-33 says, and is never rewritten as a `text` block to get past CEX-31. Rationale: an example that a spec gives as a program checks the language in layer 2 and in layer 3; rewriting it as text would drop that check without a word.

## The opening line

- **CEX-4.** The info string of a Clean example is exactly one of these forms, with one space between its parts and nothing else (complete list):

  ```text
  clean-language expect=valid
  clean-language expect=syntax-error code=<error code> line=<n>
  clean-language expect=error code=<error code>
  ```

  `<n>` is a decimal number with no leading zero. Any other info string of a Clean example is a violation at its opening line.
- **CEX-5.** `expect=valid`: the code is a correct Clean program. It gives no error code.
- **CEX-6.** `expect=syntax-error`: the code gives the error code, whose prefix is `SYN`. `<n>` is the line of the code that the diagnostic points at, from 1 to the number of lines of the code. In a program of several files, too, `<n>` counts the lines of the whole code, not those of one file. A prefix other than `SYN`, or an `<n>` out of that range, is a violation at the opening line.
- **CEX-7.** `expect=error`: the code gives no error code of prefix `SYN`, and gives the error code, whose prefix is not `SYN`, at build or at run time. A prefix `SYN` is a violation at the opening line.
- **CEX-8.** A comment `// prints: <output>` or `// result: <value>` at the end of a code line states what that line prints or computes. It says nothing about whether the code is valid.
- **CEX-9.** A comment of a Clean example that holds `fails:` right after its `//` and the blanks after it is a violation at its line: the opening line states the expected outcome (CEX-4).

## The code

- **CEX-10.** Each file of the program of a Clean example with `expect=valid` or `expect=error` is a Clean source file. Each code line at column 1 of a file that is not a section line is a violation at its line. A line before the first file line is no line of a file: CEX-36 checks it. Rationale: an example with `expect=syntax-error` may show code at column 1 that is not a section line, when that is the error it shows.
- **CEX-12.** The code holds at most one syntax error. Two syntax errors are shown in two Clean examples.
- **CEX-13.** The code indents each block with tab characters, one per level. A space in the blanks at the start of a code line is a violation at its line, except (complete list):
  1. on a line that starts while a `(`, `[` or `{` of an earlier line of the same file is still open, the brackets inside string literals and comments left out;
  2. in an example with `expect=syntax-error code=SYN003`, which shows an indentation error.

## The program

Every Clean example is one whole program, so that the grammar, the semantics
and the acceptance tests can each take one example alone and build the same
thing from it.

- **CEX-31.** The code of a Clean example, whatever its `expect`, is a whole program, with one exception (complete list): in an example with `expect=error`, the code may use, without declaring it, a name whose use with no declaration gives the error code of the example, by a norm of the language that gives that error code for a name that is used and not declared. Illustrative: in an example with `expect=error code=SEM002`, the variable whose missing declaration is the error `SEM002` (a variable used and declared in no enclosing scope); any other name that the example uses and does not declare still breaks this rule. Rationale: an example that leans on a name it does not declare means nothing on its own, and a semantics that guessed the name would check nothing true; an example of the error of an undeclared name can show that error only by leaving the name undeclared. Accepted cost: an example of the specs that is not a whole program is pending in layer 2 until layer 1 completes it ([CDN-4](../../clean-derived-norms/specs/module.md#rules)).
- **CEX-32.** Nothing outside the code of a Clean example builds its program. These never build it (complete list): another Clean example; a line of the spec file outside the code; a prelude or a context that a spec, a reader or a tool supplies; a line of the code that a mark hides from a reader. Rationale: this settles in what context an example builds: in none. A context outside the block would be one more input that each reader of the example could take in a different way.
- **CEX-33.** A Clean example holds no stub. It may repeat a declaration that another Clean example of the specs shows, when that declaration is no stub there. An example that needs a name which the specs do not define yet stays pending until the specs define it: it declares no stub for the name, and is pending in layer 2 as [CDN-4](../../clean-derived-norms/specs/module.md#rules) says. Rationale: a stub makes an example build while it shows the reader, and checks in layer 2, a declaration that no spec stands behind.
- **CEX-34.** A Clean example holds no focus comment. Rationale: every line of a whole program is part of what the example shows; a focus comment would tell a reader which lines to skip, and no check could hold the skipped lines to anything.

## The files of a program

A Clean example holds a program of several files as one block, each file
opened by its file line, in the way of txtar. A script splits the files, with
no model. Illustrative, the form of the files only (what `import:` means is
what the norms of the language say):

```text
// file: app/utils.cln
functions:
	integer double(integer n)
		return n * 2

// file: app/main.cln
import:
	app/utils.cln

start:
	print(double(21))
```

- **CEX-35.** The files of a program are found from its file lines alone, as the term file of a program says: no other reading of the code decides them. A file line opens a file wherever it stands, inside a block comment too. Each file stands alone: a comment or a bracket that one file leaves open does not go on into the next file. Rationale: every reader, the audit, the hook and layer 2, splits the same code into the same files, and each file is parsed as the whole source file it is.
- **CEX-11.** A file line is exactly `// file: <path>`: `// file:`, one space, and a path of this form (complete list of its conditions):
  1. it is one or more parts, with one `/` between two parts;
  2. a part holds one character or more, and no space, tab, `/` or `\`;
  3. no part is `.` or `..`;
  4. the last part ends with `.cln`, with one character or more before it.

  Each file line of another form is a violation at its line. A line of the code that is no file line and that, after the spaces and tabs at its start, starts with `//`, spaces and tabs or none, `file` in any case of its letters, spaces and tabs or none, and `:` is a violation at its line too. Illustrative: `//file: a.cln`, `// File: a.cln` and an indented `// file: a.cln` are violations; `// file: app/utils.cln` is a file line. Rationale: a path of this form names a file below the root of the program, the same for every reader; a line that looks like a file line and opens no file would join two files silently.
- **CEX-36.** No code line stands before the first file line. Each code line before it is a violation at its line. Blank lines and comments may stand there. Rationale: a code line before the first file line belongs to no file, and no reader would build it.
- **CEX-37.** Two file lines of one code never have the same path, compared character for character. Each file line whose path is that of an earlier file line of the code is a violation at its line. Rationale: a path names one file of the program; two files with one path would leave open which one an `import:` names.
- **CEX-38.** In a program of several files of a Clean example with `expect=valid`, exactly one file holds a section line `start:`. When no file holds one, the violation is at the opening line. When more than one file holds one, the violation is at the first section line `start:` of each file after the first file that holds one. This rule says nothing about a program of one file, nor about an example with `expect=error` or `expect=syntax-error`: whether such a program may lack `start:` or hold two is what the norms of the language say, and the error that the example gives shows it. Rationale: the file with `start:` is where a run of the program begins; with several files, only one of them can be it.
- **CEX-39.** In a Clean example with `expect=syntax-error` whose code holds a file line, `<n>` is the line of a file that is not its file line. An `<n>` of a file line, or of a line before the first file line, is a violation at the opening line. Rationale: a file line is a comment and a line before it belongs to no file, so no syntax error of the program is there.

## The expected output

An expected output block states what a valid example prints, so that layer 2
can check the semantics against it. These rules say where it goes and what its
code means.

- **CEX-27.** An expected output block is written right after a Clean example with `expect=valid`: the fenced block just before it is that Clean example, and only blank lines, or none, stand between the closing fence of the example and the opening line of the block. Any other expected output block is a violation at its opening line. The other cases (complete list): no fenced block comes before it; a line that is not blank stands between the two; the fenced block before it is not a Clean example; the Clean example before it has another `expect`. An expected output block is not a Clean example, so a second expected output block after the same example is a violation, and a Clean example has at most one. Rationale: the block names no example, so its place is what ties it to one; a block after an example that fails states an output that no rule checks, and a second block would state a second output for the same run.
- **CEX-28.** The info string of an expected output block is exactly `clean-language-output`. Any other is a violation at its opening line. Rationale: a block such as `clean-language-output text` would look like an expected output and be read as none.
- **CEX-29.** The code of an expected output block, each of its lines followed by one line feed (U+000A), in order, is the whole standard output of the program of its Clean example, byte for byte, in UTF-8. It is the content of the block as CommonMark 0.31.2, section 4.5, gives it, adopted whole. A block with no line states that the program writes nothing. In a program of several files, it is the output of the whole program, not of one file. Rationale: an output that a comment or a reader rounds off cannot check a semantics; byte for byte, it can. Accepted cost: a standard output whose last byte is not a line feed cannot be stated, and its example states no expected output.
- **CEX-30.** A Clean example with `expect=valid` and no expected output block states nothing about its output. A comment `// prints:` (CEX-8) is no expected output, and nothing compares the output with it. Rationale: one place states the output that is checked, and a comment written for a reader is never taken for it.

## Error codes

- **CEX-14.** An error code is defined in the spec of the rule that gives it, by its definition. Until its definition is written, its registry row stands for it.
- **CEX-15.** An error code has at most one definition in the spec files of both repositories together. Each definition of a code after the first, in code point order of path and then by line, is a violation at its heading.
- **CEX-16.** The error code of a Clean example has a definition or a registry row in the spec files of both repositories together. An error code that has neither is a violation at the opening line.
- **CEX-17.** A retired code is never the error code of a Clean example: it is a violation at the opening line.
- **CEX-18.** A retired code never gets a definition: its definition is a violation at its heading.
- **CEX-19.** A Clean example only cites its error code, with `code=`, and holds nothing else about it. Illustrative: no comment of the example gives the name, the meaning or the message of its error code.

## What is checked, and by whom

- **CEX-20.** The rules that the text decides alone are checked by the audit and by the hook (complete list): CEX-2, CEX-4, CEX-6 except its first sentence, CEX-7 except its first sentence, CEX-9, CEX-10, CEX-11, CEX-13, CEX-15 to CEX-18, CEX-27, CEX-28, CEX-36 to CEX-39. Each of them splits the code into files as CEX-35 says. The audit also checks CEX-1 by its fuzzy search ([CAU-6](../use-cases/audit/specs/audit.md#run-the-audit)). Of CEX-31 the text alone decides no part, and the audit and the hook check none of it.
- **CEX-21.** The rules that need a Clean compiler are checked by no use case or hook of this module (complete list): CEX-5, the first sentence of CEX-6, the first sentence of CEX-7, CEX-12, CEX-29, CEX-31. They bind the author of each example. The derived norms of layer 2 check them in part ([CDN-4](../../clean-derived-norms/specs/module.md#rules)): the grammar checks the syntax part of CEX-5, CEX-6 and CEX-7; the semantics checks the rest of CEX-5 and of CEX-7, CEX-29, and CEX-31. The acceptance tests of layer 3, run against the compiler built in layer 4, check all of them, CEX-12 included. CEX-19, CEX-32, CEX-33 and CEX-34 bind the author, and nothing checks them; a program that CEX-32 forbids shows up through CEX-31, as a name it does not declare.

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

1. The format of a definition beyond its heading (name, severity, phase, condition, message template, primary label, suggestion, a passing and a failing example), and the generator in layer 2 of the full list of error codes, belong to the module `clean-derived-norms` and to the project's specs.