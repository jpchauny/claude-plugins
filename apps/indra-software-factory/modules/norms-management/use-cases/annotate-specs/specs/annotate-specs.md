# Annotate the specs

**Status:** Draft
**Audience:** The people who regenerate the norms of a project; whoever builds the skill `annotate-specs` of the plugin `norms-management`

**Scope:** The use case that annotates the specs of a project's specs repository with stable norm IDs, from one commit, in its norms repository. How the generator builds the tree, places the IDs and keeps them from one version to the next is in its own specs, which this one cites and does not repeat: [norms-tree.md](../../../specs/norms-tree.md) (R1–R34), [norms-annotation-cases.md](../../../specs/norms-annotation-cases.md) (R35–R52) and [norms-versions.md](../../../specs/norms-versions.md) (R53–R64)

A use case of the module `norms-management`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md).

Where the three repositories of a project are is [ORC-20](../../../../project-management/specs/module.md#where-the-three-repositories-are), which this spec cites.

## Terms

| Term | Meaning |
|---|---|
| Skill | The skill `annotate-specs` of the plugin `norms-management`, invoked as `/norms-management:annotate-specs`; the actor of every requirement that names no other. |
| Specs repository | The repository `<project>-specs`: layer 1, written by people ([LAY-2](../../../../../specs/layers.md#lay-2--people-work-in-layer-1)). |
| Norms repository | The repository `<project>-norms`: layer 2, where the skill runs and writes. |
| Norm ID | The ID that the generator gives a node of the specs, such as `SPA-3` (R1–R34). |
| Generator | The command `norms-gen` of this plugin, which builds and verifies the annotation. |

## Annotate the specs

```gherkin
Feature: Annotate the specs
  In order to let code and tests cite every part of the specification by an ID that does not change
  As a person who regenerates the norms of a project
  I want the specs of the specs repository annotated with stable norm IDs, in the norms repository

  Rule: ORC-21 The skill runs only in a norms repository

    Scenario: Invoked in the norms repository
      Given the working directory is in the repository "billing-norms"
      When the user invokes the skill
      Then the annotation starts

    Scenario Outline: Invoked in another repository
      Given the working directory is in the repository "<repository>"
      When the user invokes the skill
      Then the skill writes nothing
      And it says that it runs only in a norms repository

      Examples:
        | repository     |
        | billing-specs  |
        | billing-code   |

  Rule: ORC-22 A path given wins; otherwise the specs repository is found as ORC-20 says

    Scenario: The path is given
      When the user invokes the skill with the path of the specs repository
      Then the skill annotates that repository

    Scenario: No path given
      Given no path is given
      When the user invokes the skill
      Then the skill finds the specs repository as ORC-20 says, and asks for its path when it is not there

  Rule: ORC-23 The skill annotates the specs of one commit, never of the working tree

    Scenario: No commit given
      Given the specs repository has uncommitted changes
      When the user invokes the skill with no commit
      Then the generator annotates the specs at the commit "HEAD" of the specs repository (R62)
      And the uncommitted changes are not annotated (R62)

    Scenario: A commit given
      When the user invokes the skill with the commit "a1b2c3d"
      Then the generator annotates the specs at that commit
      And "data/tree.jsonl" records the full object name of that commit (R61)

  Rule: ORC-24 Every spec is annotated, and every other file is copied as it is

    Scenario: The first annotation
      Given the norms repository holds no annotation yet
      When the skill annotates the specs
      Then "specs-repo-annotated/" mirrors the specs repository, at the same paths
      And each Markdown file there holds the norm IDs of its nodes (R1–R52)
      And each other file is copied byte for byte (R62)
      And no excluded path is there, such as "CLAUDE.md" or ".claude/settings.json" (R62)

  Rule: ORC-25 A norm keeps its ID from one annotation to the next

    Scenario Outline: A paragraph that changes but stays
      Given a paragraph of the specs was annotated "SPA-3"
      And the paragraph was <change> in a later commit
      When the skill annotates that later commit
      Then the paragraph is still annotated "SPA-3" (R53–R56)

      Examples:
        | change                                     |
        | moved                                      |
        | edited, its text still similar (R55)       |

    Scenario: A paragraph removed and another added
      Given a paragraph of the specs was annotated "SPA-3"
      And a later commit removes it and adds a new paragraph whose text is not similar to it (R55)
      When the skill annotates that later commit
      Then "SPA-3" is retired, and never given again (R53, R57)
      And the new paragraph gets a number never given before (R57)

  Rule: ORC-26 When the generator fails, the skill shows its message as it is and stops

    Scenario: A spec file that is not UTF-8
      Given a Markdown file of the specs at the commit is not UTF-8
      When the skill annotates the specs
      Then the generator refuses it and writes nothing (R34)
      And the skill shows the generator's message as it is, and stops

    Scenario: Any failure of the generator
      Given the generator exits with a status other than 0, whose meaning R62 gives
      When the skill annotates the specs
      Then the skill shows the generator's message as it is
      And it does not run the verification, show the changes or commit
      And it stops

  Rule: ORC-27 Every annotation is verified, and its changes shown

    Scenario: The annotation verifies
      When the skill has annotated the specs
      Then it runs the verification of the generator (R64)
      And it shows which files of "data/" and "specs-repo-annotated/" changed
      And it shows "data/report.md", which lists by norm ID what changed (R63)

    Scenario: The verification fails
      When the skill has annotated the specs
      And the verification finds a problem
      Then the skill shows each problem as the generator prints it
      And it changes nothing

  Rule: ORC-28 The skill commits only when the user asks

    Scenario: The user does not ask for a commit
      When the skill has annotated and verified the specs
      Then nothing is committed

    Scenario: The user asks for a commit
      Given the skill has annotated and verified the specs
      When the user asks to commit
      Then the skill commits only "data/" and "specs-repo-annotated/", each file by its path
```
