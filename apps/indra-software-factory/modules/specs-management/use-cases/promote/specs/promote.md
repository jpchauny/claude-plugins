# Promote

**Audience:** The people who write a project's draft specs and specs, and decide when a draft spec becomes a spec; whoever builds the skill `promote` of the plugin `specs-management`

**Scope:** The meta use case that moves draft specs from layer 0 to layer 1, and rewrites the links of layer 1 that point at them. What a move shares with demote, its terms included, is [module.md](../../../specs/module.md#move-specs-between-layers-0-and-1), ORC-35 to ORC-48 and ORC-58

A meta use case of the meta module `specs-management`, specified in [module.md](../../../specs/module.md); the meta modules of the meta app are listed in [app.md](../../../../../specs/app.md). Out of scope: reviewing whether a draft spec is ready; changing its content.

## Terms

| Term | Meaning |
|---|---|
| Skill | The skill `promote` of the plugin `specs-management`, invoked as `/specs-management:promote <path>...`; the actor of every meta rule that names no other. |

The terms move, source, target, moved file, path, link, link target, absent link and plain link are those of [module.md](../../../specs/module.md#terms). For promote, the source is layer 0 and the target is layer 1.

## Promote draft specs

```gherkin
Feature: Promote draft specs
  In order to make a reviewed draft spec part of the source of truth
  As a person who writes the specs of a project
  I want the draft spec moved to layer 1, with the links of layer 1 that point at it working again

  Rule: ORC-49 The skill moves each selected file from layer 0 to layer 1, at the same path

    Scenario: One file
      Given layer 0 tracks "specs/language/expressions.md"
      And layer 1 has no "specs/language/expressions.md"
      When the user types "/specs-management:promote specs/language/expressions.md" and confirms
      Then layer 1 tracks "specs/language/expressions.md" with the bytes it had in layer 0, apart from the links of ORC-50
      And layer 0 no longer tracks "specs/language/expressions.md"

    Scenario: A folder
      Given layer 0 tracks "specs/manager/README.md" and "specs/manager/cln.md", and nothing else under "specs/manager/"
      When the user types "/specs-management:promote specs/manager" and confirms
      Then both files are moved, and nothing else

  Rule: ORC-50 Links that point at the promoted files work again, and the promoted files point at no draft

    Scenario: An absent link in layer 1 becomes plain again
      Given "specs/process.md" of layer 1 holds "[Expressions (not specified yet)](absent:language/expressions.md)"
      When "specs/language/expressions.md" is promoted
      Then that link becomes "[Expressions](language/expressions.md)"

    Scenario: A link of the promoted file to a draft becomes absent
      Given "specs/language/expressions.md" holds "[Types](types.md)"
      And "specs/language/types.md" is in layer 0 and is not promoted in the same run
      When "specs/language/expressions.md" is promoted
      Then in layer 1 that link becomes "[Types (not specified yet)](absent:types.md)"

    Scenario: Two files promoted together
      Given "specs/language/expressions.md" holds "[Types](types.md)"
      When "specs/language/expressions.md" and "specs/language/types.md" are promoted in the same run
      Then that link stays "[Types](types.md)"

    Scenario Outline: Text that is not a link stays as it is (must not)
      Given "specs/language/expressions.md" holds <text>
      And "specs/language/types.md" is in layer 0 and is not promoted in the same run
      When "specs/language/expressions.md" is promoted
      Then that text does not change

      Examples:
        | text                                   |
        | "[Spec](https://example.com/spec.md)"  |
        | "`[Types](types.md)`"                  |
        | "![Diagram](types.md)"                 |

  Rule: ORC-51 The skill refuses, and writes nothing, when a condition of ORC-39 holds

    Scenario Outline: A refused promote
      Given <state>
      When the user types "/specs-management:promote specs/a.md"
      Then the skill writes nothing
      And it says "<message>"

      Examples:
        | state                                                     | message                                                              |
        | layer 0 does not have "specs/a.md" at HEAD                | specs-management:promote: specs/a.md: not in layer 0                 |
        | layer 1 already has "specs/a.md"                          | specs-management:promote: specs/a.md: already in layer 1             |
        | layer 1 already has "specs/A.md"                          | specs-management:promote: specs/a.md: already in layer 1             |
        | "specs/a.md" has uncommitted changes in layer 0           | specs-management:promote: specs/a.md: uncommitted changes in layer 0 |
        | layer 1 is one commit ahead of "origin/main"              | specs-management:promote: layer 1: not at origin/main                |

    Scenario: No path
      When the user types "/specs-management:promote"
      Then the skill writes nothing
      And it says "specs-management:promote: expected at least one path"

    Scenario Outline: Invoked from a layer other than 0 and 1
      Given the working directory is a repository of layer <layer>
      When the user types "/specs-management:promote specs/a.md"
      Then the skill writes nothing
      And it says "specs-management:promote: runs only from the repository of layer 0 or of layer 1"

      Examples:
        | layer |
        | 2     |
        | 3     |
        | 4     |

  Rule: ORC-52 The skill shows the move, commits only after the user's yes, and reports each commit

    Scenario: The user says no
      Given the skill showed the move as ORC-42 says
      When the user replies anything other than yes
      Then both repositories are unchanged

    Scenario: The user says yes
      When the user confirms
      Then layer 1 gets one commit, pushed, with the subject "docs: promote specs from layer 0"
      And then layer 0 gets one commit, pushed, with the subject "docs: promote specs to layer 1"
      And the skill ends with "layer 1: <commit> pushed" and then "layer 0: <commit> pushed"

    Scenario: A file changes while the skill waits
      Given the skill showed the move as ORC-42 says
      And another session then changes "specs/process.md" of layer 1, whose links the move rewrites
      When the user confirms
      Then the skill writes nothing
      And it shows the move again

    Scenario: The commit of layer 0 fails, and a rerun resumes
      Given the user confirmed, layer 1 is pushed, and the commit of layer 0 failed
      When the user types the same "/specs-management:promote specs/language/expressions.md" again and confirms
      Then layer 1 gets no new commit
      And layer 0 gets one commit, pushed, with the subject "docs: promote specs to layer 1"
```
