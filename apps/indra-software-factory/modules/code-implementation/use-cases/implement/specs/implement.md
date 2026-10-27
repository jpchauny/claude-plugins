# Implement

**Prefix:** IMP

**Audience:** The people who ask for code to be built from the norms of a project; whoever builds the skill `implement` of the plugin `code-implementation`

**Scope:** The use case that implements a task in the code repository: one acceptance unit of the acceptance repository, in the order of the plan of implementation, from the norms and the derived norms of the norms repository alone, with every piece of code and every unit test citing the norms it comes from and the version of each. How the code of a unit is updated after a norm that it cites changes is open question 2. How the norms are annotated with IDs is in the specs of `norms-management`. What an acceptance unit, an acceptance test, a decision block and the plan of implementation are, and when a unit is done, is in [acceptance-management](../../../../acceptance-management/specs/module.md). The clauses of other specs that the rules below cite are (complete list): [LAY-1](../../../../development-methodology/specs/layers.md#rules) (the five layers), [LAY-3](../../../../development-methodology/specs/layers.md#rules) (how layer 2 is derived), [LAY-4](../../../../development-methodology/specs/layers.md#rules) (layer 4 reads layers 2 and 3, never layer 1), [LAY-5](../../../../development-methodology/specs/layers.md#rules) (an inconsistency goes back to layer 1); [ORC-20, ORC-21, ORC-22 and ORC-24](../../../../project-management/specs/module.md#where-the-repositories-are) (where the repositories of a project are); [ORC-25, ORC-26, ORC-27 and CIM-2](../../../specs/module.md#implement-the-changed-norms) (the commits that the module reads, and the review of the citations of the code repository); [ACU-2 and ACU-4](../../../../acceptance-management/specs/module.md#the-acceptance-area-and-the-acceptance-unit) (who decides the norms of a unit); [ACU-6 and ACU-8](../../../../acceptance-management/specs/module.md#the-files-of-the-acceptance-repository) (the files of the acceptance repository); [ACU-12, ACU-34 and ACU-49](../../../../acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence) (acceptance tests are run, never changed, and their run here is feedback; which build each entry of `product` gives them); [ACU-17](../../../../acceptance-management/specs/module.md#when-a-unit-is-done) (the AI decisions and their decision blocks); [ACU-23](../../../../acceptance-management/specs/module.md#the-ladder-of-states) (the state `verified`); [ACU-28](../../../../acceptance-management/specs/module.md#done-is-a-state-not-an-event) (a unit whose norm changed is updated in layer 3); [ACU-41](../../../../acceptance-management/specs/module.md#done-is-a-state-not-an-event) (the hand-off of the step of layer 3); [ORC-9](../../../../norms-management/specs/module.md#regenerate-the-norms) (the commit of layer 2 of a run); [ORC-15](../../../../development-methodology/specs/flow.md#start-a-run) (a run); [ACU-39 and ACU-42](../../../../acceptance-management/specs/module.md#the-plan-of-implementation) (the plan of implementation, and the order of its units and components)

A use case of the module `code-implementation`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md). The terms acceptance unit, unit ID, acceptance test, unit test, product build, AI decision, decision block, non-goal, evidence, acceptance architect, implementation planner and requester are those of [acceptance-management](../../../../acceptance-management/specs/module.md#terms); the term user is that of [module.md](../../../specs/module.md#terms).

## Terms

| Term | Meaning |
|---|---|
| Skill | The skill `implement` of the plugin `code-implementation`, invoked as `/code-implementation:implement`; the actor of every rule that names no other. |
| Task | The acceptance unit that the skill implements in an invocation, by its unit ID, such as `AU-3`. Which unit it is, IMP-14 says. |
| Requested unit | What the user gives when they invoke the skill: a unit ID, such as `AU-12`, words of their own, or nothing. The skill implements a requested unit only when it is the task (IMP-5, IMP-14). |
| Component of the code repository | The `component` of the entry of the code repository in `project.json` ([ORC-20](../../../../project-management/specs/module.md#where-the-repositories-are)), or its `name` when it has no `component` ([ACU-39](../../../../acceptance-management/specs/module.md#the-plan-of-implementation)). |
| Part | The part of a unit that one component implements: the code of the unit in the code repository of that component. The state `verified` is of the whole unit, not of a part ([ACU-23](../../../../acceptance-management/specs/module.md#the-ladder-of-states), [ACU-42](../../../../acceptance-management/specs/module.md#the-plan-of-implementation)). |
| Layer | One of the five layers of a project, 0 to 4, each in its own repositories, as [LAY-1](../../../../development-methodology/specs/layers.md#rules) says; the code is layer 4. |
| Specs repository | The repository `<project>-specs`: layer 1, written by people, which the skill never reads. |
| Code repository | The repository where the skill runs and writes: an entry of `project.json` with `layer` 4 ([ORC-20, ORC-21](../../../../project-management/specs/module.md#where-the-repositories-are)). |
| Norms repository | The entry of `project.json` with `layer` 2 ([ORC-20](../../../../project-management/specs/module.md#where-the-repositories-are)), which the skill only reads. |
| Acceptance repository | The entry of `project.json` with `layer` 3, one for the project ([ORC-20](../../../../project-management/specs/module.md#where-the-repositories-are)), which the skill only reads. |
| Norms generator | The command `norms-gen` of the plugin `norms-management`, which writes `specs-repo-annotated/` and `data/tree.jsonl` in the norms repository. |
| Derived norm | A norm of the norms repository that a project's own generator derives from the norms, such as a rule of a grammar or of a semantics ([LAY-3](../../../../development-methodology/specs/layers.md#rules)). |
| Issue | A GitHub issue of the specs repository, which reports an inconsistency of the norms ([LAY-5](../../../../development-methodology/specs/layers.md#rules)). |
| Norm | A node of `specs-repo-annotated/` in the norms repository, with its norm ID, such as `SYN-3`. |
| Norm ID | The ID of a norm, such as `SYN-3`, as the norms generator gives it. The skill reads the IDs from `data/tree.jsonl`, the only source of truth for them ([R23](../../../../norms-management/specs/norms-tree.md#storage-and-process)), and not from the markers of `specs-repo-annotated/`, which take several forms ([R24](../../../../norms-management/specs/norms-tree.md#annotations)). |
| Norms of the task | The norms that the `## Norms` of the task groups, each with its norm hash in the commit of the norms repository that the skill read. The acceptance architect decides them; the skill adds none and removes none (IMP-4). |
| Norm hash | The first 8 hex digits, in lower case, of the `tree_hash` of a norm in `data/tree.jsonl` of the norms repository ([R31](../../../../norms-management/specs/norms-tree.md#the-tree-in-layer-2), [R61](../../../../norms-management/specs/norms-versions.md#data-and-outputs)), such as `5a627175`. When and why it changes is R31's. Each citation holds the norm hash of the version it was written for, so the code repository pins no single version of layer 2. |
| Citation | One line of comment in code or in a test, `<norm ID>@<norm hash>: <reason>` after the comment mark of the language, where `<reason>` says in a few words what of the norm the code does or the test checks, such as `# INV-7@5a627175: one row per invoice` in Python or `// INV-7@5a627175: one row per invoice` in Rust and JavaScript. It names a norm that the code implements or the test checks, the version of the norm that it was written for, and why. A derived norm cites its norms with the same citation (LAY-3). |

## Implement a task

```gherkin
Feature: Implement a task
  In order to have code that does only what the norms say, and that shows which norm each part comes from
  As a person who asks for code to be built from the norms of a project
  I want a task implemented from the norms of the norms repository, with every part citing its norm IDs

  Rule: IMP-1 The skill runs only in a code repository

    Scenario: Invoked in a code repository
      Given the entry of "project.json" for the repository of the working directory has the layer 4 (ORC-21)
      When the user invokes the skill
      Then the implementation starts

    Scenario Outline: Invoked in another repository
      Given the entry of "project.json" for the repository of the working directory has the layer <layer>
      When the user invokes the skill
      Then the skill writes nothing
      And it says that it runs only in a code repository

      Examples:
        | layer |
        | 0     |
        | 1     |
        | 2     |
        | 3     |

    Scenario: The repository is in no project
      Given the repository of the working directory holds no "project.json", or is in no entry of it (ORC-21)
      When the user invokes the skill
      Then the skill writes nothing
      And it says that the repository is not in "project.json"

  Rule: IMP-2 The skill reads the norms repository and the acceptance repository each at one commit, found as ORC-21 says (ORC-25)

    Scenario Outline: The repository is at its path, outside a run
      Given the <repository> is at the project folder followed by its "path"
      And the skill runs outside a run (ORC-15)
      When the user invokes the skill
      Then the skill reads the <repository> at its commit "HEAD"
      And it ignores the uncommitted changes of the <repository>

      Examples:
        | repository            |
        | norms repository      |
        | acceptance repository |

    Scenario Outline: The repository is at its path, in a run
      Given the <repository> is at the project folder followed by its "path"
      And the skill runs as the step of layer 4 of a run (ORC-15)
      When the step starts
      Then the skill reads the <repository> at <commit>, whatever the "HEAD" of its clone
      And it ignores the uncommitted changes of the <repository>
      And when the clone does not hold that commit, the skill writes nothing, and says which commit is missing (ORC-25)

      Examples:
        | repository            | commit                                           |
        | norms repository      | the commit of layer 2 of the run (ORC-9)         |
        | acceptance repository | the hand-off of the step of layer 3 (ACU-41)     |

    Scenario Outline: The repository is not at its path
      Given the <repository> is not at the project folder followed by its "path"
      When the user invokes the skill
      Then the skill does as ORC-22 says, and writes nothing

      Examples:
        | repository            |
        | norms repository      |
        | acceptance repository |

    Scenario: The copy of project.json differs
      Given the "project.json" of the code repository differs from "specs-repo-annotated/project.json" of the norms repository
      When the user invokes the skill
      Then the skill does as ORC-24 says, and writes nothing

  Rule: IMP-3 The skill reads only the norms repository, the acceptance repository and its own code repository, and writes only its own code repository

    Scenario: What the skill reads and writes
      When the skill implements a task
      Then it reads the norms repository, the acceptance repository and the code repository only
      And it never reads another repository of layer 4 of the project; the published build of another component, which it obtains with "published" of its entry in "product" of "acceptance.json" (ACU-49), is not a repository (IMP-16)
      And in the norms repository it reads every file, "specs-repo-annotated/" and every derived norm (LAY-3)
      And in the acceptance repository it reads every file, and changes none, acceptance tests included (LAY-4)
      And it never reads the repository "billing-specs" (LAY-4)
      And it writes only in the code repository

  Rule: IMP-18 Before it starts the task, the skill shows the review of the citations of the code repository (ORC-25, ORC-26)

    Scenario: A citation of the code repository changed
      Given the code repository holds the citation "# INV-3@aa11bb22: a reason"
      And "INV-3" has the norm hash "cc33dd44" in the commit of the norms repository that the skill read
      When the user invokes the skill
      Then before it shows the task (IMP-4), the skill shows the citation of "INV-3" as "changed", with the files that hold it and the units of CIM-2
      And it lists no other norm, and adds none to the task
      And when "INV-3" is not a norm of the task, the citation stays as it is (IMP-9)

    Scenario: The comparison cannot run
      Given the comparison of ORC-25 cannot run
      When the user invokes the skill
      Then the skill writes nothing, and says why (ORC-27)

  Rule: IMP-4 Before coding, the skill shows the task, its norms and its non-goals, as the acceptance architect decided them

    Scenario: The skill starts a unit
      Given the task is "AU-3", whose "## Norms" groups "INV-7", "INV-12" and "INV-15"
      When the skill starts the task
      Then it shows "AU-3", each of its norms by its norm ID and its text, its non-goals, and the commit of the norms repository
      And it adds no norm to the task and removes none: the norms of a unit are decided in layer 3 (ACU-2)

  Rule: IMP-19 The skill implements the task only when each citation of its "## Norms" names a norm of the commit of the norms repository that it read, with its norm hash in that commit

    Scenario: The task cites one of its norms with another norm hash
      Given "AU-3" groups "INV-12" with the norm hash "0c1d2e3f"
      And "INV-12" has the norm hash "7b8c9d0e" in the commit of the norms repository that the skill read
      When the skill starts the task
      Then it does not implement "AU-3", and says that the acceptance architect must update it (ACU-28)

    Scenario: A norm of the unit is no longer in layer 2
      Given the "## Norms" of "AU-3" holds the citation "INV-15@9e8d7c6b: cancelled invoices are not exported"
      And "INV-15" is not in the commit of the norms repository that the skill read
      When the skill starts the task
      Then it does not implement "AU-3"
      And it says that the citation of "INV-15" in "AU-3" is broken, and that the acceptance architect must update the unit (ACU-28)

  Rule: IMP-5 A requested unit that is not a unit ID is not implemented

    Scenario: The user asks in their own words
      When the user invokes the skill with the requested unit "the export of invoices to CSV"
      Then the skill writes no code
      And it says that it implements only acceptance units, and that the acceptance architect must define the unit first (ACU-2)

  Rule: IMP-14 The skill implements the acceptance units in the order of the plan of implementation, each only in the code repositories of the components it names

    Scenario: Which unit is the task
      When the user invokes the skill
      Then the task is the first unit, in the order of the plan of implementation (ACU-39), whose "components" names the component of the code repository, that is not "verified" (ACU-23), and whose part in the code repository the user has not confirmed as implemented in this invocation
      And when the requested unit is a unit ID, the skill implements it only when it is the task

    Scenario: The confirmation holds only for the invocation
      Given in an earlier invocation the user said that the part of "api" in "AU-3" is implemented
      And "AU-3" is still not "verified"
      When the user invokes the skill with no requested unit in the code repository of "api"
      Then the skill asks again whether the part of "api" in "AU-3" is implemented
      And it keeps no record of what the user confirms

    Scenario: No unit ID given
      Given the code repository has the component "compiler"
      And the plan of implementation lists "AU-10", "AU-11" and "AU-12" in this order, each naming "compiler", and "AU-10" is "verified"
      When the user invokes the skill with no requested unit
      Then the skill shows "AU-11" and asks the user whether the part of "compiler" in "AU-11" is already implemented
      And when the user says it is not, the task is "AU-11" (ACU-39)

    Scenario: A unit that does not name the component
      Given the plan gives "AU-11" the components [["compiler"]] and "AU-12" the components [["compiler"], ["runtime", "ide"]], in this order
      And neither unit is "verified"
      When the user invokes the skill with no requested unit in the code repository of "runtime"
      Then the skill passes over "AU-11", and shows "AU-12"

    Scenario: The part of the component is implemented and the unit is not yet verified
      Given the plan gives "AU-3" the components [["api"], ["web"]] and lists "AU-4" after it, naming "api"
      And "AU-3" is not "verified"
      When the user invokes the skill with no requested unit in the code repository of "api"
      And the user says that the part of "api" in "AU-3" is already implemented
      Then the skill passes over "AU-3", and shows "AU-4"

    Scenario: A unit of several components
      Given the plan gives "AU-3" the components [["api"], ["web"]]
      When the skill runs in the code repository of "web" with the requested unit "AU-3"
      Then it asks the user whether the part of "api" in "AU-3" is implemented, and never reads the repository of "api" (IMP-3)
      And it implements the part of "web" only once the user says it is, and writes nothing in the repository of "api"
      And it runs the acceptance tests as IMP-16 says

    Scenario: An earlier group is not implemented
      Given the plan gives "AU-3" the components [["api"], ["web"]]
      When the skill runs in the code repository of "web" with the requested unit "AU-3"
      And the user says that the part of "api" in "AU-3" is not implemented
      Then the skill writes nothing
      And it says that the part of "api" in "AU-3" comes first in the plan

    Scenario: A unit ID that is not next in the plan
      Given the plan lists "AU-11" before "AU-12", both naming the component of the code repository, and "AU-11" is the task
      When the user invokes the skill with the requested unit "AU-12"
      Then the skill writes nothing
      And it says that "AU-11" comes first in the plan

    Scenario: A unit ID whose unit does not name the component
      Given the plan gives "AU-11" the components [["compiler"]]
      When the user invokes the skill with the requested unit "AU-11" in the code repository of "runtime"
      Then the skill writes nothing
      And it says that "AU-11" is not implemented by the component "runtime" (ACU-39)

    Scenario: No task left
      Given every unit of the plan that names the component of the code repository is "verified", or its part the user confirmed as implemented in this invocation
      When the user invokes the skill with no requested unit
      Then the skill writes nothing, and says that no unit of the plan is left for the component

    Scenario: No plan
      Given the acceptance repository holds no "plan.json" (ACU-6)
      When the user invokes the skill
      Then the skill writes nothing, and says that the implementation planner must write the plan first (ACU-39)

    Scenario: The non-goals of the unit
      Given "AU-3" has the non-goal "The unit does not export to PDF."
      When the skill implements "AU-3"
      Then it writes no code that exports to PDF

    Scenario: The unit is not in the acceptance repository
      Given the acceptance repository holds no file "units/AU-99.md"
      When the user invokes the skill with the requested unit "AU-99"
      Then the skill writes nothing
      And it says that "AU-99" is not a unit of the acceptance repository

  Rule: IMP-15 The skill implements no norm that the task does not group

    Scenario: The unit needs a norm it does not group
      Given the task is "AU-3"
      And implementing "AU-3" needs the norm "INV-20", which "AU-3" does not group
      When the skill finds it
      Then it writes no code that cites "INV-20"
      And it writes no more code for "AU-3", and leaves the code it already wrote for "AU-3" in the code repository, uncommitted (IMP-12)
      And it does not report the task as done, names the files it changed, and says that the acceptance architect must group "INV-20" in a unit (ACU-2, IMP-11)

  Rule: IMP-6 Every piece of code and every unit test cites the norms it comes from, with the norm hash of the commit of the norms repository that it read

    Scenario: Code that implements a norm
      Given the norm "INV-7" says that the CSV export has one row per invoice
      And its norm hash in the commit of the norms repository that the skill read is "5a627175"
      When the skill writes the Python function that builds the rows
      Then the function holds the citation "# INV-7@5a627175: one row per invoice"

    Scenario: A unit test that checks a norm
      When the skill writes a test of "INV-7"
      Then the test is a unit test of the code repository, and never an acceptance test (ACU-12)
      And it holds a citation of "INV-7" with the norm hash "5a627175"

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
      Then it writes no code that cites none of the norms of the task, except code that the language or the build requires, such as imports, and decision blocks (IMP-17)

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

  Rule: IMP-13 Code built from a derived norm cites the norms that derived norm cites

    Scenario: A function built from a rule of the grammar
      Given the rule "expr" of the grammar of the norms repository holds the citation "SYN-3@abcd1234: binary operators"
      When the skill writes the function that parses "expr"
      Then the function cites "SYN-3", as IMP-6 says

  Rule: IMP-8 Every citation that the skill writes names a norm of the commit of the norms repository that it read, with its norm hash in that commit

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

  Rule: IMP-16 The skill runs the acceptance tests of the task as feedback, with the builds that ACU-49 says, and never changes them (ACU-12)

    Scenario: The acceptance tests guide the code
      Given the task has acceptance tests in the acceptance repository
      And "product" of "acceptance.json" holds an entry for the code repository, and "test_command" is not empty (ACU-6)
      And each other entry of "product" has "published" (ACU-6)
      When the skill has written the code
      Then it obtains the product build of the code repository with "build" of its entry, run in its working tree, uncommitted changes included (ACU-49)
      And it obtains the build of each other code repository of "product" with "published" of its entry, and never reads, clones or builds that code repository (ACU-49, IMP-3)
      And it runs "test_command" in a copy of the commit of the acceptance repository that it read (IMP-2), made outside the acceptance repository, with each build in the environment variable that its entry names, and with "ACCEPTANCE_TARGET" and "ACCEPTANCE_REPORT" set as ACU-6 says
      And that copy holds none of the uncommitted changes of the acceptance repository, and the run writes no file into the acceptance repository (IMP-3)
      And it changes the code and the unit tests of the code repository, and never an acceptance test, until the acceptance tests of the task pass

    Scenario: Nothing to run the acceptance tests with
      Given "product" of "acceptance.json" holds no entry for the code repository, or "test_command" is empty (ACU-6)
      When the skill has written the code
      Then it runs no acceptance test
      And it says what "acceptance.json" lacks, and does not report the task as done (IMP-11)

    Scenario: The acceptance tests need the build of another component
      Given the plan gives "AU-3" the components [["api"], ["web"]], and the skill runs in the code repository of "web"
      And the entry of "product" of "acceptance.json" for the code repository of "api" has "published" (ACU-6)
      When the skill has written the code
      Then it runs the acceptance tests of "AU-3" with the value that "build" of "web" prints in its working tree and the value that "published" of "api" prints (ACU-49)
      And it never runs the "build" of "api", because that command runs in the repository of "api" (IMP-3)

    Scenario: The entry of another component has no "published"
      Given the plan gives "AU-3" the components [["api"], ["web"]], and the skill runs in the code repository of "web"
      And the entry of "product" of "acceptance.json" for the code repository of "api" has no "published" (ACU-6)
      When the skill has written the code
      Then it runs no acceptance test (ACU-49), and never runs the "build" of "api", because that command runs in the repository of "api" (IMP-3)
      And it says that the acceptance tests of "AU-3" did not run because the entry of "api" in "product" has no "published", and does not report the task as done (IMP-11)

    Scenario: An acceptance test does not pass and the skill holds it to be wrong
      Given an acceptance test of "AU-3" fails
      And the skill holds that the test does not say what the norms say
      When the skill implements the task
      Then it does not change the test, and does not make the code depart from the norms to make the test pass
      And it reports the test, and why it holds it wrong, to the requester, as ACU-12 says

    Scenario: An acceptance test still fails
      Given an acceptance test of "AU-3" fails
      And the skill cannot make it pass without working around a norm or changing the test
      When the skill ends
      Then it does not report the task as done, and names the test that fails (IMP-11)

    Scenario: No acceptance test
      Given the task has no acceptance test in the acceptance repository
      When the skill has written the code
      Then it says that the task has no acceptance test, and runs none

    Scenario: The result of the run
      When the skill has run the acceptance tests
      Then it reports the result as feedback, never as evidence that a unit is done (ACU-34)

  Rule: IMP-17 The skill records each AI decision it makes as a decision block

    Scenario: A choice where the norms leave the skill free
      Given the norms of the task leave free how the CSV is written
      And the choice meets a criterion of an AI decision, such as a trade-off of quality
      When the skill makes the choice
      Then it writes one decision block, in the form and at the place that ACU-17 says

    Scenario: A choice about the external interface that no norm makes
      Given no norm fixes the separator of the CSV
      When the skill implements the export
      Then it does not choose the separator, and writes no decision block for it
      And it does as IMP-10 says (ACU-17)


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
      Then it shows the commit of the norms repository and the commit of the acceptance repository that it read
      And for each norm of the task, the files and the functions or tests that cite it
      And each norm of the task that it did not implement, and why
      And each acceptance test of the task, and whether it passed in the run of IMP-16
      And the slug of each decision block that it wrote, and the units of each (ACU-17)

  Rule: IMP-12 The skill commits only when the user asks

    Scenario: The user does not ask for a commit
      When the skill has implemented the task
      Then nothing is committed

    Scenario: The user asks for a commit
      Given the skill has implemented the task
      When the user asks to commit
      Then the skill commits only the files it changed, each by its path
      And the message of the commit names the commit of the norms repository, the commit of the acceptance repository, and the norm IDs it covers
```

## Open questions

1. Where does the citation go for a file whose language has no comment, such as JSON?
2. When a unit is updated in layer 3 after a norm that it groups changes ([ACU-28](../../../../acceptance-management/specs/module.md#done-is-a-state-not-an-event)), is the code that cites the old norm hash updated by implementing that unit again as the task (IMP-14), or by a use case of its own?
