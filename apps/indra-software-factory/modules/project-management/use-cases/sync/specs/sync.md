# Sync

**Prefix:** SNC

**Audience:** The people who change the repositories of a project; whoever builds the skill `sync` of the plugin `project-management`

**Scope:** The use case that copies the `project.json` of the repository of layer 1 to every other repository of the project, and keeps the rules `deny` of the `.claude/settings.json` of the repositories of layers 3 and 4 in step with it (SNC-1). How `project.json` is written, and which copy is the one that is edited, is [ORC-20 and ORC-23](../../../specs/module.md#where-the-repositories-are)

A use case of the module `project-management`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md). The terms project and project folder are those of [module.md](../../../specs/module.md#terms).

## Terms

| Term | Meaning |
|---|---|
| Skill | The skill `sync` of the plugin `project-management`, invoked as `/project-management:sync`; the actor of every rule that names no other. |
| Source | The `project.json` of the repository of layer 1, at its commit `HEAD` (ORC-23). |
| Target | Every repository of the project other than the one of layer 1, as the source lists them, the orchestration repository included (SNC-2). |
| Managed rule | A rule `deny` of the exact form `Read(//**/<path>/**)` or `Edit(//**/<path>/**)`, where `<path>` is the `path` of a repository of layer 3 or 4 in the source, in the `project.json` of the target before the sync, or in any version of `project.json` committed in the target. Every other rule `deny` was written by a person. |
| Rules of ORC-5 | The rules `deny` that [ORC-5](../../create-project/specs/create-project.md#create-a-project) writes in the `.claude/settings.json` of a repository of layer 3 or 4, computed for the repositories that the source lists. |

## Sync project.json

```gherkin
Feature: Sync project.json
  In order to have the same project.json in every repository of a project
  As a person who changed the repositories of a project
  I want the copy of layer 1 copied to every other repository, and the rules "deny" of layers 3 and 4 kept in step with it

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
        | 4     |

    Scenario: Invoked in the orchestration repository
      Given the entry of "project.json" for the repository of the working directory has the "role" "orchestration" and no layer
      When the user types "/project-management:sync"
      Then the skill writes nothing
      And it says that it runs only in the repository of layer 1

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
      And the rules "deny" of every target of layers 3 and 4 are already those of SNC-1
      When the sync starts
      Then the skill writes nothing
      And it says that every copy is already the same

  Rule: ORC-31 For each target whose project.json differs, the skill writes the source, commits it in a commit that holds only project.json, and pushes

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

  Rule: SNC-2 The orchestration repository is a target, and its rules "deny" are not kept in step
    Rationale: every repository of a project holds the same project.json (ORC-20), and the orchestrator finds the repositories of the layers in its own copy; the orchestrator is held back by its hook and by the token of the code repositories (WFO-9, WFO-12), not by rules "deny", so none is managed there.

    Scenario: The project.json of the orchestration repository
      Given the source lists "billing-orchestration" with the "role" "orchestration"
      And the "project.json" of "billing-orchestration" differs from the source
      When the user confirms the sync
      Then the skill writes, commits and pushes the "project.json" of "billing-orchestration" as ORC-31 says

    Scenario: The settings of the orchestration repository
      Given the source lists "billing-orchestration" with the "role" "orchestration"
      When the sync writes the targets
      Then the skill does not change the ".claude/settings.json" of "billing-orchestration"
      And it reports no rules "deny" for "billing-orchestration" (ORC-33)

    Scenario: A source without an orchestration repository
      Given the source has no entry with "role", as a project.json written before the orchestration repository existed (PRJ-2)
      When the sync starts
      Then the targets are the repositories of the layers 0, 2, 3 and 4 that the source lists

  Rule: SNC-1 The skill keeps the rules "deny" of the repositories of layers 3 and 4 in step with project.json

    Scenario: A repository of layer 4 is added
      Given the source adds the repository "billing-code-mobile" of layer 4
      When the user confirms the targets
      Then the ".claude/settings.json" of "billing-acceptance" also denies the reading and the editing of "billing-code-mobile", as the rules of ORC-5 do
      And the ".claude/settings.json" of "billing-code-mobile" denies the editing of "billing-acceptance"

    Scenario: A repository of layer 4 is removed
      Given the source removes the repository "billing-code-web"
      When the user confirms the targets
      Then no ".claude/settings.json" of the project holds a managed rule that names "billing-code-web"
      And a rule "deny" that a person wrote and that names "billing-code-web" is kept unchanged

    Scenario: A removed repository whose rules were skipped once
      Given the source removes the repository "billing-code-web"
      And a sync wrote the "project.json" of "billing-acceptance", but skipped its ".claude/settings.json" because it had uncommitted changes
      And the user then committed that ".claude/settings.json"
      When the user runs the sync again and confirms the targets
      Then the ".claude/settings.json" of "billing-acceptance" holds no managed rule that names "billing-code-web", since "billing-code-web" is in a version of "project.json" committed in "billing-acceptance"

    Scenario: The rules "deny" are shown, and committed apart
      Given the rules "deny" of "billing-acceptance" differ from the rules of ORC-5
      When the sync starts
      Then the skill shows the diff of the ".claude/settings.json" of "billing-acceptance", together with the list of targets of ORC-30, before the user confirms
      And once the user confirms, it commits only ".claude/settings.json", by its path, with the message "chore: sync deny rules from <full object name of the source commit>", and pushes it to the default branch of "billing-acceptance"

    Scenario: The managed rules are replaced by the rules of ORC-5
      Given the ".claude/settings.json" of "billing-acceptance" holds managed rules
      When the sync writes the rules "deny" of "billing-acceptance"
      Then its rules "deny" are the rules of ORC-5, followed by every rule "deny" that is not managed, in the order they had

    Scenario Outline: A rule "deny" that a person wrote is kept unchanged
      Given the ".claude/settings.json" of "billing-acceptance" holds the rule "deny" "<rule>"
      And "secrets" is not the "path" of a repository in the source, or in the "project.json" of "billing-acceptance" or in any version of it committed in "billing-acceptance"
      When the sync writes the rules "deny" of "billing-acceptance"
      Then that rule is kept unchanged

      Examples:
        | rule                    |
        | Bash(rm -rf *)          |
        | Read(//**/secrets/**)   |

    Scenario Outline: The settings of a target cannot be written
      Given the ".claude/settings.json" of "billing-code" <state>
      When the sync writes the targets
      Then the skill does not write the ".claude/settings.json" of "billing-code"
      And at the end it reports its rules "deny" as skipped, with the reason "<reason>" (ORC-32)

      Examples:
        | state                                                         | reason                                                      |
        | has uncommitted changes                                       | uncommitted changes in .claude/settings.json                |
        | does not exist                                                | no .claude/settings.json                                    |
        | is not valid JSON                                             | .claude/settings.json is not a JSON object of Claude Code   |
        | is valid JSON that is not an object, or whose "permissions" is not an object, or whose "permissions.deny" is not a list of strings | .claude/settings.json is not a JSON object of Claude Code |

    Scenario: Settings without rules "deny"
      Given the ".claude/settings.json" of "billing-code" is a JSON object with no "permissions" or no "permissions.deny"
      When the sync writes the rules "deny" of "billing-code"
      Then its "permissions.deny" is the list of the rules of ORC-5, and every other setting is kept

  Rule: ORC-33 The skill ends with what it did for the project.json of each target, and for the rules "deny" of each target of layers 3 and 4

    Scenario: The sync ends
      When the skill has gone through every target
      Then it shows, for the "project.json" of each target, one of "written", "already the same" or "skipped", with the reason of each skip
      And for the rules "deny" of each target of layers 3 and 4 whose "project.json" was not skipped, one of "written", "already the same" or "skipped", with the reason of each skip

    Scenario: A target whose project.json is skipped
      Given the "project.json" of the target "billing-code" is skipped (ORC-32)
      When the sync ends
      Then the skill shows "billing-code" as skipped, with the reason, once
      And it does not write the rules "deny" of "billing-code"
```
