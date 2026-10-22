# Implement

**Prefix:** IMP

**Audience:** The people who ask for code to be built from the norms of a project; whoever builds the skill `implement` of the plugin `code-implementation`

**Scope:** The use case that implements a task that the user gives, in the code repository, from the norms of the norms repository alone, with every piece of code and every test citing the norms it comes from and the version of each. How the code is reviewed when a cited norm changes is not here: it is open question 3. How the norms are annotated with IDs is in the specs of `norms-management`; how an inconsistency goes back to layer 1 is [LAY-5](../../../../../specs/layers.md#lay-5--an-inconsistency-is-fixed-in-layer-1-first)

A use case of the module `code-implementation`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md).

Where the three repositories of a project are is [ORC-20](../../../../project-management/specs/module.md#where-the-three-repositories-are), which this spec cites.

## Terms

| Term | Meaning |
|---|---|
| Skill | The skill `implement` of the plugin `code-implementation`, invoked as `/code-implementation:implement`; the actor of every requirement that names no other. |
| Task | What the user asks to implement, in their own words, such as "the export of invoices to CSV". |
| Code repository | The repository `<project>-code`: layer 3, where the skill runs and writes. |
| Norms repository | The repository `<project>-norms`: layer 2, which the skill only reads. |
| Norm | A node of `specs-repo-annotated/` in the norms repository, with its norm ID, such as `SYN-3`. |
| Norm ID | The ID of a norm, as the norms generator gives it, written in the annotated specs between `⟬` and `⟭`. |
| Norms of the task | The norms that the task needs, which the skill selects and the user confirms (IMP-4). |
| Norm hash | The first 8 hex digits of the `tree_hash` of a norm in `data/tree.jsonl` of the norms repository ([R31](../../../../norms-management/specs/norms-tree.md), [R61](../../../../norms-management/specs/norms-versions.md)), such as `5a627175`. It changes when the text of the norm, or of any node inside it, changes, and only then. |
| Citation | One line of comment in code or in a test, `<norm ID>@<norm hash>: <reason>` after the comment mark of the language, such as `# INV-7@5a627175: one row per invoice` in Python or `// INV-7@5a627175: one row per invoice` in Rust and JavaScript. It names a norm that the code implements or the test checks, the version of the norm that it was written for, and why. |

## Implement a task

```gherkin
Feature: Implement a task
  In order to have code that does only what the norms say, and that shows which norm each part comes from
  As a person who asks for code to be built from the norms of a project
  I want a task implemented from the norms of the norms repository, with every part citing its norm IDs

  Rule: IMP-1 The skill runs only in a code repository

    Scenario: Invoked in the code repository
      Given the working directory is in the repository "billing-code"
      When the user invokes the skill with a task
      Then the implementation starts

    Scenario Outline: Invoked in another repository
      Given the working directory is in the repository "<repository>"
      When the user invokes the skill with a task
      Then the skill writes nothing
      And it says that it runs only in a code repository

      Examples:
        | repository     |
        | billing-specs  |
        | billing-norms  |

  Rule: IMP-2 The skill reads the norms at one commit of the norms repository, found as ORC-20 says

    Scenario: The norms repository is beside the code repository
      Given the repository "billing-norms" is a sibling of "billing-code"
      When the user invokes the skill with a task
      Then the skill reads the norms at the commit "HEAD" of "billing-norms"
      And it ignores the uncommitted changes of "billing-norms"

    Scenario: The norms repository is not there
      Given no repository "billing-norms" is a sibling of "billing-code"
      When the user invokes the skill with a task
      Then the skill asks for the path of the norms repository, and writes nothing until it has it

  Rule: IMP-3 The skill reads only layer 2 and layer 3, and writes only layer 3

    Scenario: What the skill reads and writes
      When the skill implements a task
      Then it reads the norms repository and the code repository only
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

  Rule: IMP-8 Every citation that the skill writes names a norm of the commit it read, with its norm hash in that commit

    Scenario: Every citation is checked
      When the skill has written the code and the tests
      Then it checks each citation that it wrote: its norm ID exists in that commit (ORC-12), and its norm hash is the one of that norm in that commit

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
2. How does code cite a part of a specification derived from the norms (a grammar, a semantics, a corpus of examples, [LAY-3](../../../../../specs/layers.md#lay-3--layer-2-is-regenerated-whole-from-layer-1-only)), which has no norm ID? `norms-management` does not specify those derived specifications yet.
3. How does this use case relate to [ORC-11](../../../specs/module.md#implement-the-changed-norms), where the step implements every changed norm from a hand-off, and not a task the user gives? Is it the same skill with two ways to start, or two use cases?
