# Sync

**Audience:** The people who change the repositories of a project; whoever builds the skill `sync` of the plugin `project-management`

**Scope:** The use case that copies the `project.json` of the repository of layer 1 to every other repository of the project. How `project.json` is written, and which copy is the one that is edited, is [ORC-20](../../../specs/module.md#where-the-repositories-are) and ORC-23

A use case of the module `project-management`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md). The terms project and project folder are those of [module.md](../../../specs/module.md#terms).

## Terms

| Term | Meaning |
|---|---|
| Skill | The skill `sync` of the plugin `project-management`, invoked as `/project-management:sync`; the actor of every rule that names no other. |
| Source | The `project.json` of the repository of layer 1, at its commit `HEAD` (ORC-23). |
| Target | Every repository of the project other than the one of layer 1, as the source lists them. |

## Sync project.json

```gherkin
Feature: Sync project.json
  In order to have the same project.json in every repository of a project
  As a person who changed the repositories of a project
  I want the copy of layer 1 copied to every other repository

  Rule: ORC-28 The skill runs only in the repository of layer 1, when the user asks for it

    Scenario: Invoked in the repository of layer 1
      Given the entry of "project.json" for the repository of the working directory has the layer 1 (ORC-21)
      When the user types "/project-management:sync"
      Then the sync starts

    Scenario Outline: Invoked in another repository
      Given the entry of "project.json" for the repository of the working directory has the layer <layer>
      When the user types "/project-management:sync"
      Then the skill writes nothing
      And it says that it runs only in the repository of layer 1

      Examples:
        | layer |
        | 0     |
        | 2     |
        | 3     |

  Rule: ORC-29 The skill copies the source as it is committed

    Scenario: The source has uncommitted changes
      Given "project.json" of the repository of layer 1 has uncommitted changes
      When the sync starts
      Then the skill copies the bytes of "project.json" at the commit "HEAD", not those of the working tree

  Rule: ORC-30 Before it writes anything, the skill shows which targets differ and waits for the user to confirm

    Scenario: Some targets differ
      Given the "project.json" of "billing-norms" differs from the source
      And the "project.json" of "billing-code" is the same as the source
      When the sync starts
      Then the skill shows "billing-norms" as to be written and "billing-code" as already the same
      And it writes nothing until the user confirms

    Scenario: Every target is the same
      Given the "project.json" of every target is the same as the source
      When the sync starts
      Then the skill writes nothing
      And it says that every copy is already the same

  Rule: ORC-31 For each target, the skill writes the source, commits only that file and pushes

    Scenario: A target is written
      Given the user confirmed the sync
      When the skill writes the target "billing-norms"
      Then "project.json" of "billing-norms" holds the bytes of the source
      And the skill commits only "project.json", by its path, with the message "chore: sync project.json from <full object name of the source commit>"
      And it pushes that commit to the default branch of "billing-norms"

  Rule: ORC-32 A target that cannot be written is skipped and reported, and the others go on

    Scenario Outline: A target that is skipped
      Given the target "billing-code" <state>
      When the sync writes the targets
      Then the skill does not write "billing-code"
      And it goes on with the other targets
      And at the end it reports "billing-code" as skipped, and why

      Examples:
        | state                                                      |
        | is not at its path, as ORC-22 says                         |
        | has uncommitted changes in "project.json"                  |
        | is not on its default branch                               |
        | refuses the push                                           |

  Rule: ORC-33 The skill ends with what it did for each target

    Scenario: The sync ends
      When the skill has gone through every target
      Then it shows, for each target, one of "written", "already the same" or "skipped", with the reason of each skip
```
