# Implement

**Prefix:** IMP

**Audience:** The people who ask for code to be built from the norms of a project; whoever builds the skill `implement` of the plugin `code-implementation`

**Scope:** The use case that implements a task in the code repository: one acceptance unit of the acceptance repository, in the order of the plan of implementation, from the norms and the derived norms of the norms repository alone, with every piece of code and every unit test citing the acceptance unit it implements and the version of that acceptance unit. How the code of an acceptance unit that is not the task is updated after the acceptance unit changes is open question 2. How the norms are annotated with IDs is in the specs of `norms-management`. What an acceptance unit, an acceptance test, a decision block and the plan of implementation are, and when an acceptance unit is done, is in [acceptance-management](../../../../acceptance-management/specs/module.md). The clauses of other specs that the rules below cite are (complete list): [LAY-1](../../../../development-methodology/specs/layers.md#rules) (the five layers), [LAY-3](../../../../development-methodology/specs/layers.md#rules) (how layer 2 is derived), [LAY-4](../../../../development-methodology/specs/layers.md#rules) (layer 4 reads layers 2 and 3, never layer 1), [LAY-5](../../../../development-methodology/specs/layers.md#rules) (an inconsistency goes back to layer 1); [ORC-20, ORC-21, ORC-22 and ORC-24](../../../../project-management/specs/module.md#where-the-repositories-are) (where the repositories of a project are); [ORC-25, ORC-26, ORC-27 and CIM-2](../../../specs/module.md#implement-the-changed-norms) (the commits that the module reads, and the review of the citations of the code repository); [ACU-2 and ACU-4](../../../../acceptance-management/specs/module.md#the-acceptance-area-and-the-acceptance-unit) (who decides the norms of an acceptance unit); [ACU-9](../../../../acceptance-management/specs/module.md#the-files-of-the-acceptance-repository) (an acceptance unit that no increment holds is not implemented); [ACU-48](../../../../acceptance-management/specs/module.md#the-files-of-the-acceptance-repository) (only the implementation planner, with the use case plan, writes plan.json); [ACU-52 and ACU-56](../../../../acceptance-management/specs/module.md#hashes-and-citations) (the unit hash, and the forms of a citation); [ACU-6 and ACU-8](../../../../acceptance-management/specs/module.md#the-files-of-the-acceptance-repository) (the files of the acceptance repository); [ACU-12, ACU-34 and ACU-49](../../../../acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence) (acceptance tests are run, never changed, and their run here is feedback; which build each entry of `product` gives them); [ACU-17](../../../../acceptance-management/specs/module.md#when-an-acceptance-unit-is-done) (the AI decisions and their decision blocks); [ACU-23](../../../../acceptance-management/specs/module.md#the-ladder-of-states) (the state `verified`); [ACU-28](../../../../acceptance-management/specs/module.md#done-is-a-state-not-an-event) (an acceptance unit whose norm changed is updated in layer 3); [ACU-41](../../../../acceptance-management/specs/module.md#done-is-a-state-not-an-event) (the hand-off of the step of layer 3); [ORC-9](../../../../norms-management/specs/module.md#regenerate-the-norms) (the commit of layer 2 of a run); [ORC-15](../../../../development-methodology/specs/flow.md#start-a-run) (a run); [ACU-39 and ACU-42](../../../../acceptance-management/specs/module.md#the-plan-of-implementation) (the plan of implementation, and the order of its acceptance units and components); [PLN-5 and PLN-13](../../../../acceptance-management/use-cases/plan/specs/plan.md#plan-the-implementation) (the checks of a plan, and the hand-off of a run that keeps a plan.json with errors)

A use case of the module `code-implementation`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md). The terms acceptance unit, unit ID, unit hash, increment, plan of implementation, citation, norm citation, acceptance test, unit test, product build, AI decision, decision block, non-goal, evidence, acceptance architect, implementation planner and requester are those of [acceptance-management](../../../../acceptance-management/specs/module.md#terms); the terms norm, norm ID, norm hash, derived norm, specs repository, norms repository, acceptance repository and code repository are those of [layers.md](../../../../development-methodology/specs/layers.md#terms); the term norms generator is that of [norms-management](../../../../norms-management/specs/module.md#terms); the terms user and acceptance unit behind layer 2 are those of [module.md](../../../specs/module.md#terms). The code repository holds no norm citation (IMP-6). The skill reads the norm IDs from `data/tree.jsonl`, and not from the markers of `specs-repo-annotated/`, which take several forms ([R24](../../../../norms-management/specs/norms-tree.md#annotations)).

## Terms

| Term | Meaning |
|---|---|
| Skill | The skill `implement` of the plugin `code-implementation`, invoked as `/code-implementation:implement`, which runs and writes in one code repository, only reads the norms repository and the acceptance repository, and never reads the specs repository; the actor of every rule that names no other. |
| Task | The acceptance unit that the skill implements in an invocation, by its unit ID, such as `AU-3`. Which acceptance unit it is, IMP-14 says. |
| Requested acceptance unit | What the user gives when they invoke the skill: a unit ID, such as `AU-12`, words of their own, or nothing. The skill implements a requested acceptance unit only when it is the task (IMP-5, IMP-14). |
| Component of the code repository | The `component` of the entry of the code repository in `project.json` ([ORC-20](../../../../project-management/specs/module.md#where-the-repositories-are)), or its `name` when it has no `component` ([ACU-39](../../../../acceptance-management/specs/module.md#the-plan-of-implementation)). |
| Part | The part of an acceptance unit that one component implements: the code of the acceptance unit in the code repository of that component. The state `verified` is of the whole acceptance unit, not of a part ([ACU-23](../../../../acceptance-management/specs/module.md#the-ladder-of-states), [ACU-42](../../../../acceptance-management/specs/module.md#the-plan-of-implementation)). |
| Layer | One of the five layers of a project, 0 to 4, each in its own repositories, as [LAY-1](../../../../development-methodology/specs/layers.md#rules) says; the code is layer 4. |
| Issue | A GitHub issue of the specs repository, which reports an inconsistency of the norms ([LAY-5](../../../../development-methodology/specs/layers.md#rules)). |
| Norms of the task | The norms that the `## Norms` of the task groups, each with its norm hash in the commit of the norms repository that the skill read. The acceptance architect decides them; the skill adds none and removes none (IMP-4). |

## Implement a task

```gherkin
Feature: Implement a task
  In order to have code that does only what the norms say, and that shows which acceptance unit, and through it which norms, each part comes from
  As a person who asks for code to be built from the norms of a project
  I want a task implemented from the norms of the norms repository, with every part citing the acceptance unit it implements

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
      Given the code repository holds the citation "# AU-5@aa11bb22: a reason"
      And "AU-5" has the unit hash "cc33dd44" in the commit of the acceptance repository that the skill read
      When the user invokes the skill
      Then before it shows the task (IMP-4), the skill shows the citation of "AU-5" as "changed", with the files that hold it and what CIM-2 says of it
      And it lists no other acceptance unit, and adds no norm to the task
      And when "AU-5" is not the task, the citation stays as it is (IMP-9)

    Scenario Outline: A citation of an acceptance unit that is not in the acceptance repository
      Given the code repository holds the citation "# <unit>@aa11bb22: a reason"
      And the commit of the acceptance repository that the skill read holds no file "units/<unit>.md", and its "acceptance.json" has "last_unit_id" 9
      When the user invokes the skill
      Then the skill shows the citation of "<unit>" as "<state>", with the files that hold it (ORC-25, CIM-2)

      Examples:
        | unit  | state   |
        | AU-7  | retired |
        | AU-12 | unknown |

    Scenario: A cited acceptance unit is behind layer 2
      Given the code repository holds the citation "# AU-3@efc7ae86: one row per invoice", and "efc7ae86" is the unit hash of "AU-3" in the commit of the acceptance repository that the skill read
      And "## Norms" of "AU-3" holds "INV-12@0c1d2e3f: amounts with two decimals", and "INV-12" has the norm hash "7b8c9d0e" in the commit of the norms repository that the skill read
      When the user invokes the skill
      Then the skill shows "AU-3" as an acceptance unit behind layer 2, because of "INV-12" (ORC-26)

    Scenario: The comparison cannot run
      Given the comparison of ORC-25 cannot run
      When the user invokes the skill
      Then the skill writes nothing, and says why (ORC-27)

  Rule: IMP-4 Before coding, the skill shows the task, its norms and its non-goals, as the acceptance architect decided them

    Scenario: The skill starts an acceptance unit
      Given the task is "AU-3", whose "## Norms" groups "INV-7", "INV-12" and "INV-15"
      When the skill starts the task
      Then it shows "AU-3", each of its norms by its norm ID and its text, its non-goals, and the commit of the norms repository
      And it adds no norm to the task and removes none: the norms of an acceptance unit are decided in layer 3 (ACU-2)

  Rule: IMP-19 The skill implements the task only when each norm citation of its "## Norms" names a norm of the commit of the norms repository that it read, with its norm hash in that commit: the task is not an acceptance unit behind layer 2

    Scenario: The task cites one of its norms with another norm hash
      Given "AU-3" groups "INV-12" with the norm hash "0c1d2e3f"
      And "INV-12" has the norm hash "7b8c9d0e" in the commit of the norms repository that the skill read
      When the skill starts the task
      Then it does not implement "AU-3", and says that the acceptance architect must update it (ACU-28)
      And the code that cites "AU-3" stays as it is

    Scenario: A norm of the acceptance unit is no longer in layer 2
      Given the "## Norms" of "AU-3" holds the citation "INV-15@9e8d7c6b: cancelled invoices are not exported"
      And "INV-15" is not in the commit of the norms repository that the skill read
      When the skill starts the task
      Then it does not implement "AU-3"
      And it says that the citation of "INV-15" in "AU-3" is broken, and that the acceptance architect must update the acceptance unit (ACU-28)

  Rule: IMP-5 A requested acceptance unit that is not a unit ID is not implemented

    Scenario: The user asks in their own words
      When the user invokes the skill with the requested acceptance unit "the export of invoices to CSV"
      Then the skill writes no code
      And it says that it implements only acceptance units, and that the acceptance architect must define the acceptance unit first (ACU-2)

  Rule: IMP-14 The skill implements the acceptance units in the order of the plan of implementation, each only in the code repositories of the components it names

    Scenario: Which acceptance unit is the task
      When the user invokes the skill
      Then the task is the first acceptance unit, in the order of the plan of implementation (ACU-39), whose "components" names the component of the code repository, that is not "verified" (ACU-23), and whose part in the code repository the user has not confirmed as implemented in this invocation
      And when the requested acceptance unit is a unit ID, the skill implements it only when it is the task

    Scenario: The confirmation holds only for the invocation
      Given in an earlier invocation the user said that the part of "api" in "AU-3" is implemented
      And "AU-3" is still not "verified"
      When the user invokes the skill with no requested acceptance unit in the code repository of "api"
      Then the skill asks again whether the part of "api" in "AU-3" is implemented
      And it keeps no record of what the user confirms

    Scenario: No unit ID given
      Given the code repository has the component "compiler"
      And the plan of implementation lists "AU-10", "AU-11" and "AU-12" in this order, each naming "compiler", and "AU-10" is "verified"
      When the user invokes the skill with no requested acceptance unit
      Then the skill shows "AU-11" and asks the user whether the part of "compiler" in "AU-11" is already implemented
      And when the user says it is not, the task is "AU-11" (ACU-39)

    Scenario: An acceptance unit that does not name the component
      Given the plan gives "AU-11" the components [["compiler"]] and "AU-12" the components [["compiler"], ["runtime", "ide"]], in this order
      And neither acceptance unit is "verified"
      When the user invokes the skill with no requested acceptance unit in the code repository of "runtime"
      Then the skill passes over "AU-11", and shows "AU-12"

    Scenario: The part of the component is implemented and the acceptance unit is not yet verified
      Given the plan gives "AU-3" the components [["api"], ["web"]] and lists "AU-4" after it, naming "api"
      And "AU-3" is not "verified"
      When the user invokes the skill with no requested acceptance unit in the code repository of "api"
      And the user says that the part of "api" in "AU-3" is already implemented
      Then the skill passes over "AU-3", and shows "AU-4"

    Scenario: An acceptance unit of several components
      Given the plan gives "AU-3" the components [["api"], ["web"]]
      When the skill runs in the code repository of "web" with the requested acceptance unit "AU-3"
      Then it asks the user whether the part of "api" in "AU-3" is implemented, and never reads the repository of "api" (IMP-3)
      And it implements the part of "web" only once the user says it is, and writes nothing in the repository of "api"
      And it runs the acceptance tests as IMP-16 says

    Scenario: An earlier group is not implemented
      Given the plan gives "AU-3" the components [["api"], ["web"]]
      When the skill runs in the code repository of "web" with the requested acceptance unit "AU-3"
      And the user says that the part of "api" in "AU-3" is not implemented
      Then the skill writes nothing
      And it says that the part of "api" in "AU-3" comes first in the plan

    Scenario: A unit ID that is not next in the plan
      Given the plan lists "AU-11" before "AU-12", both naming the component of the code repository, and "AU-11" is the task
      When the user invokes the skill with the requested acceptance unit "AU-12"
      Then the skill writes nothing
      And it says that "AU-11" comes first in the plan

    Scenario: A unit ID whose acceptance unit does not name the component
      Given the plan gives "AU-11" the components [["compiler"]]
      When the user invokes the skill with the requested acceptance unit "AU-11" in the code repository of "runtime"
      Then the skill writes nothing
      And it says that "AU-11" is not implemented by the component "runtime" (ACU-39)

    Scenario: No task left
      Given every acceptance unit of the plan that names the component of the code repository is "verified", or its part the user confirmed as implemented in this invocation
      When the user invokes the skill with no requested acceptance unit
      Then the skill writes nothing, and says that no acceptance unit of the plan is left for the component

    Scenario: No plan
      Given the acceptance repository holds no "plan.json" (ACU-6)
      When the user invokes the skill
      Then the skill writes nothing, and says that the implementation planner must write the plan first with /acceptance-management:plan (ACU-39)

    Scenario: The non-goals of the acceptance unit
      Given "AU-3" has the non-goal "The unit does not export to PDF."
      When the skill implements "AU-3"
      Then it writes no code that exports to PDF

    Scenario: The acceptance unit is not in the acceptance repository
      Given the acceptance repository holds no file "units/AU-99.md"
      When the user invokes the skill with the requested acceptance unit "AU-99"
      Then the skill writes nothing
      And it says that "AU-99" is not an acceptance unit of the acceptance repository

    Scenario: The acceptance unit is in no increment
      Given the acceptance repository holds the file "units/AU-20.md"
      And no increment of "plan.json" holds "AU-20"
      When the user invokes the skill with the requested acceptance unit "AU-20"
      Then the skill writes nothing
      And it says that "AU-20" is not yet planned, and that the implementation planner must add it to the plan with /acceptance-management:plan (ACU-9, ACU-39)

  Rule: IMP-21 Before it chooses the task, the skill checks "plan.json" as PLN-5 says, and refuses a plan.json that fails a check
    Rationale: a plan.json with an error gives IMP-14 no single answer: it can name an acceptance unit with no file, a component with no code repository, or a dependency that comes later. Passing over the faulty acceptance units would implement a plan that the requester never approved, so the skill stops and sends the plan back to the implementation planner, who alone writes it. plan.json can hold an error in four cases (complete list): between a commit of define that deletes an acceptance unit and the next commit of the skill plan; in the hand-off of a run in which the requester rejected a proposal of the plan while plan.json held an error (PLN-13); after a change of the entries of layer 4 of project.json (ORC-20) that removes or renames a component that plan.json names, or that switches between one entry without component and entries with component; and after a commit of plan.json made without the skill plan, which ACU-48 forbids but no check of the acceptance repository prevents.

    Scenario: The check
      Given the acceptance repository holds "plan.json" (ACU-6)
      When the user invokes the skill
      Then before IMP-14 chooses the task, the skill checks "plan.json" with every check of PLN-5, against the files of "units/" at the commit of the acceptance repository that it read (IMP-2) and the components of layer 4 of "project.json" (ORC-20, ACU-39)

    Scenario: A plan.json with errors (must not)
      Given "plan.json" names "AU-7", and the acceptance repository holds no "units/AU-7.md"
      When the user invokes the skill
      Then the skill writes nothing, and implements no acceptance unit, not even one that the error does not name
      And it says that plan.json is not valid, gives each error as PLN-5 words it, one per line, here "AU-7 is in plan.json and has no file units/AU-7.md", and says that the implementation planner must fix plan.json with /acceptance-management:plan

    Scenario: A plan.json without errors
      Given "plan.json" passes every check of PLN-5
      Then the skill chooses the task as IMP-14 says

  Rule: IMP-15 The skill implements no norm that the task does not group

    Scenario: The acceptance unit needs a norm it does not group
      Given the task is "AU-3"
      And implementing "AU-3" needs the norm "INV-20", which "AU-3" does not group
      When the skill finds it
      Then it writes no code for "INV-20"
      And it writes no more code for "AU-3", and leaves the code it already wrote for "AU-3" in the code repository, uncommitted (IMP-12)
      And it does not report the task as done, names the files it changed, and says that the acceptance architect must group "INV-20" in an acceptance unit (ACU-2, IMP-11)

  Rule: IMP-6 Every piece of code and every unit test cites the acceptance units it implements or checks, with the unit hash of the commit of the acceptance repository that it read, and never a norm ID (ACU-56)

    Scenario: Code that implements the task
      Given the task is "AU-3", whose unit hash in the commit of the acceptance repository that the skill read is "efc7ae86"
      And "AU-3" groups "INV-7", which says that the CSV export has one row per invoice
      When the skill writes the Python function that builds the rows
      Then the function holds the citation "# AU-3@efc7ae86: one row per invoice"
      And it holds no norm citation, such as "# INV-7@5a627175: one row per invoice"

    Scenario: A unit test that checks the task
      When the skill writes a test of "AU-3"
      Then the test is a unit test of the code repository, and never an acceptance test (ACU-12)
      And it holds a citation of "AU-3" with the unit hash "efc7ae86"

    Scenario: Code that serves two acceptance units
      Given the function "parse_expr" holds the citation "// AU-10@4e5f6a7b: parse additions"
      And the task is "AU-11", whose unit hash is "a596f507"
      When the skill changes "parse_expr" so that it also parses multiplications
      Then the function holds two citations, one line each, "// AU-10@4e5f6a7b: parse additions" and "// AU-11@a596f507: parse multiplications"

    Scenario Outline: The comment mark follows the language
      When the skill writes a citation of "AU-3" in a file of <language>
      Then the citation is "<citation>"

      Examples:
        | language   | citation                                  |
        | Python     | # AU-3@efc7ae86: one row per invoice      |
        | Rust       | // AU-3@efc7ae86: one row per invoice     |
        | JavaScript | // AU-3@efc7ae86: one row per invoice     |
        | SQL        | -- AU-3@efc7ae86: one row per invoice     |

    Scenario: Code that does not serve the task
      When the skill implements the task
      Then it writes no code that holds no citation of the task, except code that the language or the build requires, such as imports, and decision blocks (IMP-17)

  Rule: IMP-20 When the code cites the task with another unit hash, the skill reviews that code against the task, and cites the unit hash of the task

    Scenario: The task changed since its code was written
      Given the task is "AU-3", whose unit hash is "efc7ae86"
      And the code repository holds the citation "# AU-3@1a2b3c4d: one row per invoice", shown as "changed" in the review (ORC-26)
      When the skill implements the task
      Then it changes the code under that citation, and its unit tests, as the diff of CIM-2 and the norms of the task ask
      And it replaces the citation with "# AU-3@efc7ae86: one row per invoice", or removes the citation and the code under it when the task no longer needs that code
      And when it ends, no citation of "AU-3" in the code repository holds a unit hash other than "efc7ae86"

  Rule: IMP-7 A citation is placed on the smallest part of the code that holds the whole of what its reason says

    Scenario Outline: Where the citation goes
      Given what of "AU-3" the reason of the citation says is implemented by <part>
      When the skill cites it
      Then the citation is <place>

      Examples:
        | part                                   | place                                |
        | one function                           | on the line just above that function |
        | one line inside a function             | on the line just above that line     |
        | a whole class, and no one method of it | on the line just above that class    |
        | a whole file                           | at the top of that file              |

  Rule: IMP-13 Code built from a derived norm cites the task, as IMP-6 says, and never the norms that the derived norm cites

    Scenario: A function built from a rule of the grammar
      Given the rule "expr" of the grammar of the norms repository holds the norm citation "SYN-3@abcd1234: binary operators"
      And the task is "AU-11", whose "## Norms" groups "SYN-3", and whose unit hash is "a596f507"
      When the skill writes the function that parses "expr"
      Then the function holds the citation "// AU-11@a596f507: parse multiplications", and no citation of "SYN-3"

  Rule: IMP-8 Every citation that the skill writes names an acceptance unit of the commit of the acceptance repository that it read, with its unit hash in that commit

    Scenario: Every citation is checked
      When the skill has written the code and the tests
      Then a script checks each citation that the skill wrote: its unit ID is the ID of a file "units/<unit ID>.md" of that commit, and its unit hash is the one of that acceptance unit in that commit (ACU-52)

    Scenario Outline: A citation that does not check
      Given the skill wrote the citation "<citation>"
      And <fact>
      When the skill checks the citations
      Then it fixes the citation before it ends, and does not report the task as done until every citation it wrote checks

      Examples:
        | citation                     | fact                                                  |
        | # AU-99@1f2e3d4c: a reason   | "AU-99" is not an acceptance unit of that commit                  |
        | # AU-3@00000000: a reason    | the unit hash of "AU-3" in that commit is "efc7ae86"  |
        | # INV-7@5a627175: a reason   | "INV-7" is a norm ID, not a unit ID (IMP-6)           |

  Rule: IMP-9 The skill changes no citation of an acceptance unit that is not the task

    Scenario: A file holds a citation of another acceptance unit
      Given a file that the skill changes holds the citation "# AU-5@aa11bb22: a reason"
      And "AU-5" is not the task
      When the skill implements the task
      Then the citation of "AU-5" stays as it is, with its unit hash "aa11bb22"
      And the code under it changes only so that it also serves the task, with a citation of the task added (IMP-6)
      And it does not change that code when "AU-5" is an acceptance unit behind layer 2, or its citation is not "unchanged" (CIM-2)
      And the unit tests that cite "AU-5" still pass

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
      Then it reports the result as feedback, never as evidence that an acceptance unit is done (ACU-34)

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

  Rule: IMP-11 The skill ends with the list of what it implemented for the task

    Scenario: The task is implemented
      When the skill has implemented the task
      Then it shows the commit of the norms repository and the commit of the acceptance repository that it read
      And the task, with its unit hash, and the files and the functions or tests that cite it
      And each norm of the task that it did not implement, and why
      And each acceptance test of the task, and whether it passed in the run of IMP-16
      And the slug of each decision block that it wrote, and the acceptance units of each (ACU-17)

  Rule: IMP-12 The skill commits only when the user asks

    Scenario: The user does not ask for a commit
      When the skill has implemented the task
      Then nothing is committed

    Scenario: The user asks for a commit
      Given the skill has implemented the task
      When the user asks to commit
      Then the skill commits only the files it changed, each by its path
      And the message of the commit names the commit of the norms repository, the commit of the acceptance repository, and the unit ID of the task with its unit hash
```

## Open questions

1. Where does the citation go for a file whose language has no comment, such as JSON?
2. When an acceptance unit is updated in layer 3 ([ACU-28](../../../../acceptance-management/specs/module.md#done-is-a-state-not-an-event)), the code that cites its old unit hash is updated when the acceptance unit is the task again (IMP-14, IMP-20). Must a use case of its own update it sooner, when the acceptance unit comes late in the plan of implementation?
