# Clean derived norms

**Prefix:** CDN

**Audience:** The people who keep layer 2 of the Clean Language project; whoever builds a use case of the plugin `clean-derived-norms`

**Scope:** The derived norms of Clean, one use case per type, each a derived-norms generator of the interface of [norms-management](../../../../indra-software-factory/modules/norms-management/specs/module.md#derive-the-derived-norms), NRM-1 to NRM-11. What each type derives, and how, is in the spec of its use case. Out of scope: the norms, which `/norms-management:build` writes; the rules of the Clean examples, which are in [clean-examples](../../clean-examples/specs/module.md)

The module `clean-derived-norms` of the app Clean Language, listed in [app.md](../../../specs/app.md). It is installed in the repository of layer 2 of the project ([CLN-1](../../../specs/app.md#rules)).

## Terms

| Term | Meaning |
|---|---|
| Fragment | A norm of `data/tree.jsonl` of kind `code_block`, with status `active`, whose code block is a Clean example of [clean-examples](../../clean-examples/specs/module.md#terms): its info string is `clean-language`, or starts with `clean-language` followed by a space. |
| File line, path of a file line, file of a program, program | As [clean-examples](../../clean-examples/specs/module.md#terms) defines them, for the code of a fragment. |

## Use cases

| Use case | Type | Spec |
|---|---|---|
| `derive-grammar` | `grammar` | [derive-grammar.md](../use-cases/derive-grammar/specs/derive-grammar.md) |
| `derive-semantics` | `semantics` | [derive-semantics.md](../use-cases/derive-semantics/specs/derive-semantics.md) |

## Rules

- **CDN-1.** Each use case of this module is the derived-norms generator of one type of the `derived_norms` of the project's `project.json`, and follows [NRM-1 to NRM-11](../../../../indra-software-factory/modules/norms-management/specs/module.md#derive-the-derived-norms).
- **CDN-2.** A use case of this module takes the expected outcome of each fragment from its opening line, as [CEX-4 to CEX-7](../../clean-examples/specs/module.md#the-opening-line) state it, and its expected output only from its expected output block, as [CEX-27 to CEX-30](../../clean-examples/specs/module.md#the-expected-output) state it; never from a comment of its code.
- **CDN-3.** A fragment whose opening line is none of the forms of CEX-4 is a pending item of every use case of this module, and gets its issue in layer 1 ([NRM-8](../../../../indra-software-factory/modules/norms-management/specs/module.md#derive-the-derived-norms)).
- **CDN-4.** No use case of this module checks the rules of [CEX-20](../../clean-examples/specs/module.md#what-is-checked-and-by-whom), which the audit and the hook of `clean-examples` check in layers 0 and 1. Of the rules of [CEX-21](../../clean-examples/specs/module.md#what-is-checked-and-by-whom), the use cases of this module check these, and no other (complete list):
  - `derive-grammar`, the syntax: that each file of the program of a fragment with `expect=valid` or `expect=error` parses, and that the program of one with `expect=syntax-error` does not (its spec states where the parse may fail);
  - `derive-semantics`, the rest of CEX-5 and of CEX-7, CEX-29, and CEX-31: that a fragment with `expect=valid` gives no error code and, when it has an expected output block, writes exactly its expected output; that a fragment with `expect=error` gives exactly its error code, at build or at run time (its spec states how); and that a fragment that is not a whole program, outside the exception of CEX-31 for a fragment with `expect=error`, is pending, with the reason that it is not a whole program (CEX-31), and gets its issue in layer 1 as a defect of the example; a fragment that the exception covers is checked for its error code, as any fragment with `expect=error`. It does not check `expect=syntax-error`.
- **CDN-5.** A citation of a norm in the code of a use case of this module that becomes stale (its norm has another norm hash, is retired or is gone) gets its own issue in `jpchauny/claude-plugins`, the repository of this plugin, opened at once by the use case.
- **CDN-6.** A use case of this module reads the code of a fragment as its program: it splits the code into its files as [CEX-35](../../clean-examples/specs/module.md#the-files-of-a-program) says, from the file lines alone, and reads each file as a whole Clean source file, alone. The `<n>` of `line=<n>` counts the lines of the whole code ([CEX-6](../../clean-examples/specs/module.md#the-opening-line)), and a use case that compares a place in a file with it maps that place to the lines of the whole code (its spec states how). Splitting the files is no check of them: whether a path has the form of CEX-11, whether two files have one path (CEX-37), whether a code line stands before the first file line (CEX-36), which file holds `start:` (CEX-38) and whether `<n>` is a line of a file (CEX-39) are rules of CEX-20, which CDN-4 leaves to layers 0 and 1. Rationale: a program of several files is one example, and every generator of layer 2 must split it into the same files, the way the audit and the hook do, so that the grammar parses and the semantics runs the same program.
