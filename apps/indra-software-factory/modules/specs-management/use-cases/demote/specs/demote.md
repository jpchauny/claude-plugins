# Demote

**Audience:** The people who write a project's specs and decide that a spec goes back to being a draft; whoever builds the skill `demote` of the plugin `specs-management`

**Scope:** The use case that moves specs from layer 1 to layer 0, and marks the links of layer 1 that point at them as absent. What a move shares with promote, its terms included, is [module.md](../../../specs/module.md#move-specs-between-layers-0-and-1), ORC-35 to ORC-48 and ORC-58

A use case of the module `specs-management`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md). Out of scope: choosing which specs to demote; changing their content; rewriting the text around an absent link.

## Terms

| Term | Meaning |
|---|---|
| Skill | The skill `demote` of the plugin `specs-management`, invoked as `/specs-management:demote <path>...`; the actor of every rule that names no other. |

The terms move, source, target, moved file, path, link, link target, absent link and plain link are those of [module.md](../../../specs/module.md#terms). For demote, the source is layer 1 and the target is layer 0.

## Demote specs

```gherkin
Feature: Demote specs
  In order to keep in the source of truth only the specs that are reviewed
  As a person who writes the specs of a project
  I want a spec moved back to layer 0, with the links of layer 1 that point at it marked as absent

  Rule: ORC-53 The skill moves each selected file from layer 1 to layer 0, at the same path

    Scenario: One file
      Given layer 1 tracks "specs/manager/cln.md"
      And layer 0 has no "specs/manager/cln.md"
      When the user types "/specs-management:demote specs/manager/cln.md" and confirms
      Then layer 0 tracks "specs/manager/cln.md" with the bytes it had in layer 1, apart from the links of ORC-54
      And layer 1 no longer tracks "specs/manager/cln.md"

  Rule: ORC-54 Links of layer 1 that point at a demoted file become absent links

    Scenario: A link in a file that stays
      Given "specs/process.md" of layer 1 holds "[cln](manager/cln.md#run)"
      When "specs/manager/cln.md" is demoted
      Then that link becomes "[cln (not specified yet)](absent:manager/cln.md#run)"

    Scenario: A link to a demoted folder
      Given "specs/README.md" of layer 1 holds "[Manager](manager/)"
      When the folder "specs/manager" is demoted
      Then that link becomes "[Manager (not specified yet)](absent:manager/)"

    Scenario: An absent link of the demoted file becomes plain in layer 0
      Given "specs/manager/cln.md" holds "[Lockfile (not specified yet)](absent:lockfile.md)"
      And layer 0 tracks "specs/manager/lockfile.md"
      When "specs/manager/cln.md" is demoted
      Then in layer 0 that link becomes "[Lockfile](lockfile.md)"

    Scenario: Layer 0 is not rewritten (must not)
      Given "specs/drafts-index.md" of layer 0 holds "[cln](manager/cln.md)"
      When "specs/manager/cln.md" is demoted
      Then "specs/drafts-index.md" does not change

  Rule: ORC-55 Demote and promote undo each other, under the condition of ORC-41

    Scenario: Demote, then promote
      Given layer 1 is at a commit C, and every plain link of layer 1 has a link target that exists in layer 1
      When "specs/manager" is demoted, and then promoted, with no other change between the two moves
      Then every file of both repositories has the bytes it had before the demote

    Scenario: A link to a folder emptied file by file
      Given "specs/README.md" of layer 1 holds "[Manager](manager/)"
      And "specs/manager/" holds only "README.md" and "cln.md"
      When "specs/manager/README.md" and "specs/manager/cln.md" are demoted in the same run
      Then that link becomes "[Manager (not specified yet)](absent:manager/)"

  Rule: ORC-56 The skill refuses, and writes nothing, when a condition of ORC-39 holds

    Scenario Outline: A refused demote
      Given <state>
      When the user types "/specs-management:demote specs/a.md"
      Then the skill writes nothing
      And it says "<message>"

      Examples:
        | state                                                                  | message                                                                     |
        | layer 1 does not have "specs/a.md" at HEAD                             | specs-management:demote: specs/a.md: not in layer 1                         |
        | layer 0 already has "specs/a.md"                                       | specs-management:demote: specs/a.md: already in layer 0                     |
        | "specs/b.md" of layer 1 links to "specs/a.md" and has uncommitted changes | specs-management:demote: specs/b.md: uncommitted changes in layer 1      |
        | line 7 of "specs/b.md" is "[A](a.md \"title\")"                        | specs-management:demote: specs/b.md:7: link cannot be rewritten             |
        | layer 0 is on the branch "work", and its default branch is "main"      | specs-management:demote: layer 0: not on its default branch main            |

  Rule: ORC-57 The skill shows the move, commits only after the user's yes, and reports each commit

    Scenario: The user says yes
      Given the skill showed the move as ORC-42 says
      When the user confirms
      Then layer 0 gets one commit, pushed, with the subject "docs: demote specs from layer 1"
      And then layer 1 gets one commit, pushed, with the subject "docs: demote specs to layer 0"
      And the skill ends with "layer 0: <commit> pushed" and then "layer 1: <commit> pushed"
```
