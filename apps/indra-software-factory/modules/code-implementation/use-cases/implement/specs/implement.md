# Implement

**Prefix:** IMP

**Audience:** The people who ask for code to be built from the norms of a project; whoever builds the skill `implement` of the plugin `code-implementation`

**Scope:** The use case that implements a task that the user gives, in the code repository, from the norms of the norms repository alone, with every piece of code and every test citing the norms it comes from and the version of each. How the code is reviewed when a cited norm changes is not here: it is open question 2. How the norms are annotated with IDs is in the specs of `norms-management`. This spec cites [LAY-3](../../../../../specs/layers.md#lay-3--layer-2-is-derived-from-layer-1-only-and-only-what-changed-is-regenerated) (how layer 2 is derived), [LAY-4](../../../../../specs/layers.md#lay-4--layer-3-reads-layer-2-never-layer-1) (layer 3 reads layer 2, never layer 1), [LAY-5](../../../../../specs/layers.md#lay-5--an-inconsistency-is-fixed-in-layer-1-first) (an inconsistency goes back to layer 1) and [ORC-20](../../../../project-management/specs/module.md#where-the-repositories-are) (where the repositories of a project are)

A use case of the module `code-implementation`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md).

## Terms

| Term | Meaning |
|---|---|
| Skill | The skill `implement` of the plugin `code-implementation`, invoked as `/code-implementation:implement`; the actor of every rule that names no other. |
| Task | What the user asks to implement, in their own words, such as "the export of invoices to CSV". |
| Layer | One of the three layers of a project, each in its own repository ([layers.md](../../../../../specs/layers.md)): 1, the specs; 2, the norms; 3, the code. |
| Specs repository | The repository `<project>-specs`: layer 1, written by people, which the skill never reads. |
| Code repository | The repository where the skill runs and writes: an entry of `project.json` with `layer` 3 ([ORC-20, ORC-21](../../../../project-management/specs/module.md#where-the-repositories-are)). |
| Norms repository | The entry of `project.json` with `layer` 2 ([ORC-20](../../../../project-management/specs/module.md#where-the-repositories-are)), which the skill only reads. |
| Norms generator | The command `norms-gen` of the plugin `norms-management`, which writes `specs-repo-annotated/` and `data/tree.jsonl` in the norms repository. |
| Derived specification | A specification of the norms repository that a project's own generator derives from the annotated specs, such as a grammar or a semantics ([LAY-3](../../../../../specs/layers.md#lay-3--layer-2-is-derived-from-layer-1-only-and-only-what-changed-is-regenerated)). |
| Issue | A GitHub issue of the specs repository, which reports an inconsistency of the norms ([LAY-5](../../../../../specs/layers.md#lay-5--an-inconsistency-is-fixed-in-layer-1-first)). |
| Norm | A node of `specs-repo-annotated/` in the norms repository, with its norm ID, such as `SYN-3`. |
| Norm ID | The ID of a norm, such as `SYN-3`, as the norms generator gives it. The skill reads the IDs from `data/tree.jsonl`, the only source of truth for them ([R23](../../../../norms-management/specs/norms-tree.md#storage-and-process)), and not from the markers of the annotated specs, which take several forms ([R24](../../../../norms-management/specs/norms-tree.md#annotations)). |
| Norms of the task | The norms that the task needs, which the skill selects and the user confirms (IMP-4). |
| Norm hash | The first 8 hex digits, in lower case, of the `tree_hash` of a norm in `data/tree.jsonl` of the norms repository ([R31](../../../../norms-management/specs/norms-tree.md#the-tree-in-layer-2), [R61](../../../../norms-management/specs/norms-versions.md#data-and-outputs)), such as `5a627175`. When and why it changes is R31's. Each citation holds the norm hash of the version it was written for, so the code repository pins no single version of layer 2. |
| Citation | One line of comment in code or in a test, `<norm ID>@<norm hash>: <reason>` after the comment mark of the language, where `<reason>` says in a few words what of the norm the code does or the test checks, such as `# INV-7@5a627175: one row per invoice` in Python or `// INV-7@5a627175: one row per invoice` in Rust and JavaScript. It names a norm that the code implements or the test checks, the version of the norm that it was written for, and why. A derived specification cites its norms with the same citation (LAY-3). |

## Implement a task

```gherkin
Feature: Implement a task
  In order to have code that does only what the norms say, and that shows which norm each part comes from
  As a person who asks for code to be built from the norms of a project
  I want a task implemented from the norms of the norms repository, with every part citing its norm IDs

  Rule: IMP-1 The skill runs only in a code repository

    Scenario: Invoked in a code repository
      Given the entry of "project.json" for the repository of the working directory has the layer 3 (ORC-21)
      When the user invokes the skill with a task
      Then the implementation starts

    Scenario Outline: Invoked in another repository
      Given the entry of "project.json" for the repository of the working directory has the layer <layer>
      When the user invokes the skill with a task
      Then the skill writes nothing
      And it says that it runs only in a code repository

      Examples:
        | layer |
        | 0     |
        | 1     |
        | 2     |

    Scenario: The repository is in no project
      Given the repository of the working directory holds no "project.json", or is in no entry of it (ORC-21)
      When the user invokes the skill with a task
      Then the skill writes nothing
      And it says that the repository is not in "project.json"

  Rule: IMP-2 The skill reads the norms at one commit of the norms repository, found as ORC-21 says

    Scenario: The norms repository is at its path
      Given the norms repository is at the project folder followed by its "path"
      When the user invokes the skill with a task
      Then the skill reads the norms at the commit "HEAD" of the norms repository
      And it ignores the uncommitted changes of the norms repository

    Scenario: The norms repository is not at its path
      Given the norms repository is not at the project folder followed by its "path"
      When the user invokes the skill with a task
      Then the skill does as ORC-22 says, and writes nothing

    Scenario: The copy of project.json differs
      Given the "project.json" of the code repository differs from "specs-repo-annotated/project.json" of the norms repository
      When the user invokes the skill with a task
      Then the skill does as ORC-24 says, and writes nothing

  Rule: IMP-3 The skill reads only the norms repository and its own code repository, and writes only its own code repository

    Scenario: What the skill reads and writes
      When the skill implements a task
      Then it reads the norms repository and the code repository only
      And it never reads another repository of layer 3 of the project
      And in the norms repository it reads every file, "specs-repo-annotated/" and every specification derived from the norms (LAY-3)
      And it never reads the repository "billing-specs" (LAY-4)
      And it writes only in the code repository

  Rule: IMP-4 Before coding, the skill shows the norms of the task and waits for the user to confirm them

    Scenario: The user confirms the norms
      Given the task is "the export of invoices to CSV"
      When the skill has selected the norms the task needs
      Then it shows each one by its norm ID and its text, and the commit of the norms repository
      And it writes no code until the user confirms the list

    Scenario: The user changes the list
      Given the skill has shown the norms of the task
      When the user adds or removes norm IDs
      Then the skill shows the new list, and waits for the user to confirm it

  Rule: IMP-5 A task that no norm covers is not implemented

    Scenario: No norm covers the task
      Given no norm of the norms repository covers the task
      When the skill selects the norms of the task
      Then it writes no code
      And it says that the task is not in the norms, and that it must be specified first in the specs repository

    Scenario: The norms cover the task in part
      Given the norms cover only part of the task
      When the skill shows the norms of the task
      Then it also lists each part of the task that no norm covers
      And it implements only the parts that the norms cover

  Rule: IMP-6 Every piece of code and every test cites the norms it comes from, with the norm hash of the commit it read

    Scenario: Code that implements a norm
      Given the norm "INV-7" says that the CSV export has one row per invoice
      And its norm hash in the commit that the skill read is "5a627175"
      When the skill writes the Python function that builds the rows
      Then the function holds the citation "# INV-7@5a627175: one row per invoice"

    Scenario: A test that checks a norm
      When the skill writes a test of "INV-7"
      Then the test holds a citation of "INV-7" with the norm hash "5a627175"

    Scenario: Code that implements three norms
      Given a function implements "INV-7", "INV-12" and "EXP-3"
      When the skill writes it
      Then it holds three citations, one line each, each with its own norm hash and reason

    Scenario Outline: The comment mark follows the language
      When the skill writes a citation of "INV-7" in a file of <language>
      Then the citation is "<citation>"

      Examples:
        | language   | citation                                  |
        | Python     | # INV-7@5a627175: one row per invoice     |
        | Rust       | // INV-7@5a627175: one row per invoice    |
        | JavaScript | // INV-7@5a627175: one row per invoice    |
        | SQL        | -- INV-7@5a627175: one row per invoice    |

    Scenario: Code that comes from no norm of the task
      When the skill implements the task
      Then it writes no code that cites none of the norms of the task, except code that the language or the build requires, such as imports

  Rule: IMP-7 A citation is placed on the smallest part of the code that holds the whole implementation of the norm

    Scenario Outline: Where the citation goes
      Given the norm "<norm>" is implemented by <part>
      When the skill cites it
      Then the citation is <place>

      Examples:
        | norm   | part                                   | place                                |
        | INV-7  | one function                           | on the line just above that function |
        | INV-12 | one line inside a function             | on the line just above that line     |
        | INV-2  | a whole class, and no one method of it | on the line just above that class    |
        | CFG-1  | a whole file                           | at the top of that file              |

  Rule: IMP-13 Code built from a part of a derived specification cites the norms that part cites

    Scenario: A function built from a rule of the grammar
      Given the rule "expr" of the grammar of the norms repository holds the citation "SYN-3@abcd1234: binary operators"
      When the skill writes the function that parses "expr"
      Then the function cites "SYN-3", as IMP-6 says

  Rule: IMP-8 Every citation that the skill writes names a norm of the commit it read, with its norm hash in that commit

    Scenario: Every citation is checked
      When the skill has written the code and the tests
      Then it checks each citation that it wrote: its norm ID exists in that commit, and its norm hash is the one of that norm in that commit

    Scenario Outline: A citation that does not check
      Given the skill wrote the citation "<citation>"
      And <fact>
      When the skill checks the citations
      Then it fixes the citation before it ends, and does not report the task as done until every citation it wrote checks

      Examples:
        | citation                     | fact                                              |
        | # INV-99@1f2e3d4c: a reason  | "INV-99" does not exist in that commit             |
        | # INV-7@00000000: a reason   | the norm hash of "INV-7" in that commit is "5a627175" |

  Rule: IMP-9 The skill changes no citation of a norm that is not a norm of the task

    Scenario: A file holds a citation of another norm
      Given a file that the skill changes holds the citation "# INV-3@aa11bb22: a reason"
      And "INV-3" is not a norm of the task
      When the skill implements the task
      Then the citation of "INV-3" stays as it is, with its norm hash "aa11bb22"
      And the code that it cites stays as it is

  Rule: IMP-10 An inconsistency of the norms stops the implementation and is reported to layer 1

    Scenario: Two norms of the task contradict each other
      Given the norms "INV-7" and "INV-12" of the task contradict each other
      When the skill implements the task
      Then it does not work around the contradiction (LAY-5)
      And it stops implementing the part that they cover
      And it shows the text of an issue for the specs repository that names both norm IDs and what contradicts
      And it opens the issue only after the user confirms

  Rule: IMP-11 The skill ends with the list of what it implemented, by norm ID

    Scenario: The task is implemented
      When the skill has implemented the task
      Then it shows the commit of the norms repository that it read
      And for each norm of the task, the files and the functions or tests that cite it
      And each norm of the task that it did not implement, and why

  Rule: IMP-12 The skill commits only when the user asks

    Scenario: The user does not ask for a commit
      When the skill has implemented the task
      Then nothing is committed

    Scenario: The user asks for a commit
      Given the skill has implemented the task
      When the user asks to commit
      Then the skill commits only the files it changed, each by its path
      And the message of the commit names the commit of the norms repository and the norm IDs it covers
```

## Open questions

1. Where does the citation go for a file whose language has no comment, such as JSON?
2. How is the code reviewed when a cited norm changes, that is, when the norm hash of a citation is no longer the one of its norm in the last commit of the norms repository: by this skill, with the changed norms as its task, or by a use case of its own?
