# Write

**Audience:** The people who write a project's draft specs and specs; whoever builds the skill `write` of the plugin `specs-management`

**Scope:** The use case in which the AI interviews a person about what they want, and writes it as a draft spec of layer 0: a new draft spec, a change to a draft spec, or a change to or the deletion of a spec of layer 1 after its demote. It checks the draft against layers 0 and 1 and, when it is consistent, proposes its promote

A use case of the module `specs-management`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md). The guideline that every draft spec follows is [writing-specs.md](../../../writing-specs.md). Out of scope: writing a new spec directly in layer 1; changing a spec of layer 1 in place; promoting or demoting without the user's yes; layers 2, 3 and 4.

## Terms

| Term | Meaning |
|---|---|
| Skill | The skill `write` of the plugin `specs-management`, invoked as `/specs-management:write [<path>]`; the actor of every rule that names no other. |
| Draft | The file of layer 0 that a run writes, changes or deletes. |
| Intent | What the user wants the draft to say, in their own words. |
| Paraphrase | The skill's restatement of the intent: the narrative `In order to <benefit>`, `As a <role>`, `I want <what>`, followed by the rules, the examples of each rule, and the open questions. |
| Neighbour | A file of layer 0 or of layer 1 that the draft links to, that links to the draft, or that holds a term defined in the draft. |
| Inconsistency | A statement of the draft that contradicts a statement of the draft or of another file of layers 0 and 1; a fact that the draft states and another file already states ([SPC-11](../../../writing-specs.md)); a term that the draft defines with a meaning other than its meaning in another file ([SPC-3](../../../writing-specs.md)); a link of the draft whose link target does not exist. |

The terms path, link, link target, absent link and plain link are those of [module.md](../../../specs/module.md#terms). Promote and demote are the use cases [promote.md](../../promote/specs/promote.md) and [demote.md](../../demote/specs/demote.md).

## Write a draft spec

```gherkin
Feature: Write a draft spec
  In order to turn what I want into a professional spec, consistent with the rest of the project
  As a person who writes the specs of a project
  I want the AI to interview me, write the draft spec in layer 0, check it against layers 0 and 1, and propose its promote

  Rule: ORC-59 The skill runs only when the user asks for it, and only from the repository of layer 0 or of layer 1

    Scenario: Invoked by the user
      When the user types "/specs-management:write", or asks in words to write, change or delete a spec
      Then the skill runs

    Scenario: Never on its own (must not)
      Given the user talks about a spec but asks for none of the above
      Then the model does not start the skill

    Scenario Outline: Invoked from a layer other than 0 and 1
      Given the working directory is a repository of layer <layer>
      When the user types "/specs-management:write"
      Then the skill writes nothing
      And it says "specs-management:write: runs only from the repository of layer 0 or of layer 1"

      Examples:
        | layer |
        | 2     |
        | 3     |
        | 4     |

  Rule: ORC-60 The input selects one of four cases (complete list)

    Scenario Outline: The case
      Given <given>
      When the user types "/specs-management:write <argument>"
      Then the case is <case>

      Examples:
        | given                                               | argument     | case                       |
        | nothing                                             |              | new draft spec             |
        | neither layer has "specs/a.md"                      | specs/a.md   | new draft spec             |
        | layer 0 tracks "specs/a.md"                         | specs/a.md   | change of a draft spec     |
        | layer 1 tracks "specs/a.md", and the user says change | specs/a.md | change of a spec           |
        | layer 1 tracks "specs/a.md", and the user says delete | specs/a.md | deletion of a spec         |

    Scenario: A path of layer 1 without a verb
      Given layer 1 tracks "specs/a.md"
      When the user types "/specs-management:write specs/a.md"
      Then the skill asks whether to change or to delete it, and does nothing else until the user answers

    Scenario: An invalid path
      When the user types "/specs-management:write ../a.md"
      Then the skill writes nothing
      And it says "specs-management:write: ../a.md: invalid path"

    Scenario: A path that a layer tracks with other case
      Given layer 0 tracks "specs/a.md"
      When the user types "/specs-management:write specs/A.md"
      Then the skill writes nothing, since paths are compared ignoring case
      And it says "specs-management:write: specs/A.md: already in layer 0"

  Rule: ORC-61 A new spec is born only in layer 0 (must not)

    Scenario: A new draft spec
      Given the case is new draft spec
      When the user accepts the paraphrase
      Then the skill proposes a path, and writes the draft in layer 0 at the path the user accepts
      And it creates no file in layer 1

  Rule: ORC-62 A spec of layer 1 is changed or deleted only after its demote

    Scenario: The user accepts the demote
      Given the case is change of a spec or deletion of a spec, for "specs/a.md"
      When the skill proposes "/specs-management:demote specs/a.md" and the user says yes
      Then the skill runs the demote, and then works on "specs/a.md" of layer 0 as a draft

    Scenario: The user refuses the demote
      Given the skill proposed the demote of "specs/a.md"
      When the user replies anything other than yes
      Then the skill writes nothing in either layer, and stops

  Rule: ORC-63 The skill interviews the user, and writes nothing until the user accepts the paraphrase

    Scenario: The interview
      Given the case is new draft spec, change of a draft spec or change of a spec
      Then the skill asks, in this order: the benefit, the role and what the user wants; the rules and an example of each rule; the edge cases and the negative cases; the open questions
      And it numbers each question, and starts from the draft when the draft exists

    Scenario: The paraphrase
      Given the interview is over
      When the skill shows the paraphrase
      Then it writes the draft only after the user accepts it
      And a reply other than yes resumes the interview

  Rule: ORC-64 The draft follows writing-specs.md

    Scenario: Writing the draft
      Given the user accepted the paraphrase
      Then the skill writes the draft from the paraphrase, following writing-specs.md
      And every open question of the paraphrase is in the draft, marked as open (SPC-8)

  Rule: ORC-65 After each change of the draft, the skill checks it cheaply against layers 0 and 1, and only reports

    Scenario: The checks after a change (complete list)
      Given the skill changed the draft
      Then a script, with no model, lists each link of the draft whose link target does not exist, each term defined in the draft that another file of layers 0 and 1 also defines, and each statement ID of the draft that another file of layers 0 and 1 also uses
      And the skill, in the session, looks for inconsistencies in the draft against itself and its neighbours only
      And it shows each inconsistency found, with the path and line of each statement involved

    Scenario: What the script counts as a term and as a statement ID (complete list)
      Then a term defined in a file is the first cell of a row of a table, outside code blocks, whose first header cell is "Term", compared ignoring case and bold, italics and code marks
      And a statement ID declared in a file is an ID that starts a Gherkin "Rule:", a bold "**ID**" at the start of a list item, or a heading, fenced blocks included
      And another file uses an ID when it mentions it anywhere

    Scenario: An inconsistency does not stop the writing (must not)
      Given the checks found an inconsistency
      Then the skill does not refuse to write, nor change the draft without the user's yes

  Rule: ORC-66 Each change of layer 0 follows LAY-2

    Scenario: The user approves the change
      Given the skill has a change of the draft to write
      Then it shows the whole diff, and commits and pushes it to the default branch of layer 0 in one command, which the user approves
      And the commit holds only the draft, by explicit path

    Scenario Outline: The commit message
      Given the case is <case>
      Then the subject of the commit of layer 0 is "<subject>", followed by an empty line and the line "<path>"

      Examples:
        | case                   | subject                    |
        | new draft spec         | docs: add draft spec       |
        | change of a draft spec | docs: change draft spec    |
        | change of a spec       | docs: change draft spec    |
        | deletion of a spec     | docs: delete spec          |

  Rule: ORC-67 Before it proposes the promote, the skill runs the audit and the full check of consistency

    Scenario: The full check
      Given the user says the draft is ready
      Then the skill runs "/specs-management:audit <path>" in layer 0
      And it checks the draft for inconsistencies against the whole of layer 0 and the whole of layer 1, in workflow mode, with one skeptic per inconsistency, which answers "refuted" or "confirmed"
      And it shows the findings of the audit and each confirmed inconsistency

    Scenario: Consistent
      Given the full check confirmed no inconsistency
      Then the skill proposes "/specs-management:promote <path>", with the number of findings of the audit
      And it runs the promote only after the user's yes

    Scenario: Not consistent
      Given the full check confirmed at least one inconsistency
      Then the skill does not propose the promote
      And it resumes the interview on the inconsistencies

    Scenario: The full check runs only when asked (must not)
      Given the user has not said that the draft is ready
      Then the skill does not run the full check

  Rule: ORC-68 Deleting a spec deletes its draft and every link to it, in both layers

    Scenario: The deletion
      Given the case is deletion of a spec, and "specs/a.md" is in layer 0 after its demote (ORC-62)
      When the user approves the deletion
      Then the skill deletes "specs/a.md" from layer 0
      And it deletes each link to "specs/a.md" in every file of layers 0 and 1, absent or plain, with its text and its destination
      And where deleting a link leaves its sentence broken, it proposes how to rewrite the sentence, or to delete it, and applies only the proposals the user accepts
      And it shows the whole diff of both layers before the commit

    Scenario: No link text stays (must not)
      Given "specs/process.md" of layer 1 holds "[A (not specified yet)](absent:a.md)"
      When "specs/a.md" is deleted
      Then neither "A (not specified yet)" nor "A" stays in place of the link

    Scenario: A link that cannot be deleted as written
      Given "specs/process.md" holds "[A](a%2Emd)" at line 3, whose destination resolves to "specs/a.md" only once its backslash escapes and %XX are decoded
      When the user asks to delete "specs/a.md"
      Then the skill writes nothing in either layer
      And it says "specs-management:write: specs/process.md:3: link cannot be rewritten"

    Scenario: The commits of a deletion
      Given the user approved the diff
      Then layer 0 gets one commit, pushed, with the subject "docs: delete spec" and the line "specs/a.md"
      And then layer 1 gets one commit, pushed, with the subject "docs: delete links to a deleted spec" and the line "specs/a.md", when a file of layer 1 changed
      And each commit holds only the files the deletion changed, by explicit path

  Rule: ORC-69 The skill never writes layer 1 except to delete links, and never touches the work of another session (must not)

    Scenario: Layer 1 is never written
      Then the skill writes no file of layer 1 other than the deletion of links of ORC-68 and the rewrites of their sentences that the user accepts
      And it never uses "git stash", "git reset", "git checkout", "git restore", "git clean", or "git add" of a folder or of all changes
```
