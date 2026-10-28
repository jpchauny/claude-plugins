# Define

**Audience:** The requesters of a project, who approve its acceptance areas and acceptance units; whoever builds the skill `define` of the plugin `acceptance-management`

**Scope:** The use case in which the acceptance architect analyses every norm of layer 2 against every acceptance area and every acceptance unit of the acceptance repository, and creates, changes and deletes acceptance areas and acceptance units, with their scenarios, in changes that the requester approves. A script, with no model, computes the inventory that the analysis starts from and checks every file before it is committed

A use case of the module `acceptance-management`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md). Out of scope: the increments and `plan.json`, which the implementation planner decides ([ACU-44](../../../specs/module.md#the-plan-of-implementation)); the acceptance tests, which the test agent writes ([ACU-11](../../../specs/module.md#acceptance-tests-and-independent-evidence)); the record of the evidence ([ACU-35](../../../specs/module.md#done-is-a-state-not-an-event)); the fields `default_done_profile`, `test_command` and `product` of `acceptance.json` ([ACU-43](../../../specs/module.md#the-files-of-the-acceptance-repository)); the review of the norms of [ACU-15](../../../specs/module.md#the-review-of-the-norms-selected), which is open question 1; the derived norms; layers 0, 1, 2 and 4.

## Terms

| Term | Meaning |
|---|---|
| Skill | The skill `define` of the plugin `acceptance-management`, invoked as `/acceptance-management:define`; it acts as the acceptance architect, and is the actor of every rule that names no other. |
| Default branch | Of a repository: the branch that `git ls-remote --symref origin HEAD`, run in that repository, names. |
| Norms commit | The head of the default branch of the remote `origin` of the norms repository, after the fetch of ACU-58. |
| Inventory | The JSON object that the script of ACU-60 prints. |
| Citation status | What the norms commit says of one norm citation of `## Norms` of an acceptance unit: `current`, `changed` or `retired` (ACU-62). |
| Change | One item of the proposal: to add, change or delete one acceptance area or one acceptance unit, with every other file that ACU-10 and ACU-70 make it touch, and the file of each acceptance unit out of which it moves a scenario or a norm citation (ACU-67). |
| Proposal | The numbered list of changes that the skill shows to the requester (ACU-64). |
| Acceptance unit with evidence | An acceptance unit whose record holds at least one line. |

The terms norm, norm ID, norm hash, derived norm, specs repository, norms repository, acceptance repository and code repository are those of [layers.md](../../../../development-methodology/specs/layers.md#terms); a norm, its norm ID and its norm hash are those of the norms commit. The form of a norm ID is that of [ACU-56](../../../specs/module.md#hashes-and-citations). The terms requester, acceptance area, acceptance unit, work item, increment, unit ID, area ID, scenario ID, title, fingerprint, unit hash, area hash, scenario hash, citation, norm citation, scenario, external interface, gap of layer 1, acceptance test, acceptance architect, implementation planner, test agent, evidence, record, done profile, default done profile, state and stale are those of [module.md](../../../specs/module.md#terms). The terms run and step are those of [flow.md](../../../../development-methodology/specs/flow.md#terms). The fingerprints are computed as [ACU-51 to ACU-54](../../../specs/module.md#hashes-and-citations) say. A commit of layer 3 follows [LAY-9](../../../../development-methodology/specs/layers.md#rules).

## Define the acceptance areas and acceptance units

```gherkin
Feature: Define the acceptance areas and acceptance units
  In order to receive the norms of my project in parts that I can see working and accept
  As a requester
  I want the AI to analyse every norm against every acceptance area and acceptance unit, and to propose the acceptance areas, the acceptance units and their scenarios that I approve

  Rule: ACU-57 The skill runs when the user asks for it or as the step of layer 3 of a run, only from the acceptance repository, and takes no argument

    Scenario: Invoked by the user
      When the user types "/acceptance-management:define", or asks in words to define, change or delete acceptance areas or acceptance units
      Then the skill runs

    Scenario: Invoked by a run
      Given a run is at its step of layer 3 (ORC-15, ACU-37)
      Then the skill runs as when the user invokes it, and the run waits until it ends

    Scenario: Never on its own (must not)
      Given the user talks about acceptance units but asks for none of the above
      Then the model does not start the skill

    Scenario: The refusals
      Then an argument, and a repository other than the acceptance repository, end the skill as ACU-58 says

  Rule: ACU-58 Before it reads anything else, a script with no model makes these checks, in this order, and the first that fails ends the skill with its message (complete list)

    Scenario Outline: A check fails
      Given <condition>
      When the skill starts
      Then the skill writes nothing
      And it says "acceptance-management:define: <message>"

      Examples:
        | condition | message |
        | the user gave an argument | takes no argument |
        | the working directory is in no git repository; or its repository has at its root no "project.json" that ORC-21 can read, or not exactly one entry of it matches its remote "origin" (ORC-21), or its entry has a layer other than 3, or the "path" of its entry is not valid (ORC-20), or the folder of the repository does not end with that "path" (ORC-21) | runs only from the acceptance repository |
        | "project.json" has not exactly one entry with "layer" 2, or the "path" of that entry is not valid (ORC-20) | project.json has not exactly one entry of layer 2, the norms repository, with a valid path |
        | the norms repository "acme/billing-norms" is not at "/p/billing-norms" (ORC-22) | acme/billing-norms not found at /p/billing-norms; run: git clone https://github.com/acme/billing-norms /p/billing-norms |
        | "git fetch origin" fails in the acceptance repository "acme/billing-acceptance" | cannot fetch acme/billing-acceptance |
        | "git fetch origin" fails in the norms repository | cannot fetch acme/billing-norms |
        | "git ls-remote --symref origin HEAD" names no branch in the acceptance repository | cannot find the default branch of acme/billing-acceptance |
        | "git ls-remote --symref origin HEAD" names no branch in the norms repository | cannot find the default branch of acme/billing-norms |
        | the norms commit holds no "data/tree.jsonl" | acme/billing-norms has no data/tree.jsonl on main |
        | "data/tree.jsonl" of the norms commit is not UTF-8, or a line of it cannot be read as R23 and R61 say | acme/billing-norms: data/tree.jsonl is not valid |
        | the norms commit holds no "specs-repo-annotated/project.json" | acme/billing-norms has no specs-repo-annotated/project.json on main |
        | "project.json" differs from "specs-repo-annotated/project.json" of the norms commit, byte for byte (ORC-24) | project.json differs from that of acme/billing-norms; run /project-management:sync |
        | the acceptance repository is not on its default branch "main" | the acceptance repository is not on main |
        | its "HEAD" holds a commit that "origin/main" does not | the acceptance repository has commits that are not on origin/main |
        | "origin/main" holds a commit that its "HEAD" does not | the acceptance repository is behind origin/main; run git pull |
        | "units/AU-3.md" is the first path, in sorted order, with an uncommitted change among "acceptance.json" and the files of "areas/" and "units/" | uncommitted change in units/AU-3.md |
        | "units/AU-4.md" is the first path, in sorted order, of an untracked file under "areas/" or "units/" | untracked file units/AU-4.md |
        | "acceptance.json" is not one JSON object with the fields of ACU-6, each of its type | acceptance.json does not meet ACU-6 |

      And "main" stands for the default branch of the repository that the row names

    Scenario: Other uncommitted changes
      Given the acceptance repository has an uncommitted change in "tests/AU-3/test_export.py" or in "records/AU-3.jsonl"
      When the skill starts
      Then no check fails because of it
      And the skill never stages, commits or changes that file

  Rule: ACU-59 The skill reads layer 2 at the norms commit and layer 3 at its "HEAD", and never changes the working tree of the norms repository

    Scenario: The commits read
      Given every check of ACU-58 passed
      Then the skill reads the norms repository only at the norms commit, with "git show" and "git ls-tree" of that commit
      And it reads the acceptance repository at its "HEAD", which ACU-58 made equal to "origin/main"
      And in a run it reads the same commits

    Scenario: The working tree of the norms repository (must not)
      Given the norms repository has a checked-out branch "old" and uncommitted changes
      When the skill runs
      Then its working tree, its index and its local branches are as before; only its remote-tracking branches moved, by the fetch
      And no file of its working tree is read

  Rule: ACU-60 The script prints the inventory: one JSON object on its standard output, computed with no model (complete list of fields)

    Scenario: The fields of the inventory (complete list)
      Then the inventory holds these fields:
        | field             | value                                                                                                                                                 |
        | norms_commit      | the norms commit, 40 hex digits                                                                                                                       |
        | acceptance_commit | the commit of the acceptance repository read, 40 hex digits                                                                                           |
        | default_done_profile   | "default_done_profile" of "acceptance.json": the default done profile                                                                                      |
        | next_ids          | an object: "acceptance_area", "acceptance_unit" and "scenario", the next area ID, unit ID and scenario ID (ACU-55): its prefix and the highest of its field of "acceptance.json" and the numbers of the IDs of its kind in the files read, plus 1; for the inventory of the working tree, the highest also counts the IDs at "HEAD" |
        | norms             | one object per norm, in the order of "data/tree.jsonl": "norm_id", "file" (its path under "specs-repo-annotated/"), "kind", "parent_norm_id" (the norm ID of its "parent" in "data/tree.jsonl", or null), "norm_hash" and "own_text" (its "own_text" of R61: the text of the node in its file of "specs-repo-annotated/", without the text of its children and without the markers of the IDs) |
        | acceptance_areas  | one object per file "areas/<area ID>.md", in the order of the numbers of the area IDs                                                                 |
        | acceptance_units  | one object per file "units/<unit ID>.md", in the order of the numbers of the unit IDs                                                                 |
        | errors            | the errors of the repository that are not of one file (ACU-61), each an object "path", "line" and "message"                                           |
      And each acceptance area holds "area_id", "path", "title" (or null when its heading does not meet ACU-7), "area_hash" (or null), "acceptance_units" (the unit IDs whose line "Area:" names it), "scenarios", "evidence" and "errors"
      And each acceptance unit holds "unit_id", "path", "title" (or null when its heading does not meet ACU-8), "area_id" (the area ID of its line "Area:", or null when no line "Area:" meets ACU-8), "done_profile" (that of its line "Profile:", or else the default done profile), "unit_hash" (or null), "norm_citations", "scenarios", "evidence" and "errors"
      And each norm citation holds "norm_id", "hash_in_acceptance_unit" (the norm hash that the norm citation holds), "citation_status" (ACU-62) and "hash_in_norms_repository" (the norm hash of its norm at the norms commit, or null)
      And each scenario holds "scenario_id" (or null when it has not exactly one tag "@SC-<n>"), "name", "scenario_hash", "norms" (the norm IDs of its tags "@<norm ID>"), and, in an acceptance area, "acceptance_units" (the unit IDs of its tags "@unit:<unit ID>")
      And "evidence" holds the count of the lines of the record of the acceptance area or the acceptance unit of each kind of ACU-35: "test", "demo", "validation", "deviation" and "event", 0 for a kind with no line
      And each error of a file holds "line" (the number of the line that holds it, or null when no single line holds it) and "message"
      And for an error of the repository, "path" is the first file, in path order, that holds what it names, or null when it names no file, and "line" is as for an error of a file

    Scenario: The binding example of the inventory
      Then the inventory of a repository with the files of AA-1 and AU-3 of ACU-7 and ACU-8, and the files of AU-1 and AU-2 of AA-1, looks as below, where the lists "norms", "acceptance_units" and the texts are abridged to what is shown, and what binds is the keys, their nesting and the types of the values, not the values:
        """
        {"norms_commit": "9fceb02d0ae598e95dc970b74767f19372d61af8",
         "acceptance_commit": "1a410efbd13591db07496601ebc7a059dd55cfe9",
         "default_done_profile": "product",
         "next_ids": {"acceptance_area": "AA-2", "acceptance_unit": "AU-4", "scenario": "SC-10"},
         "norms": [{"norm_id": "INV-7", "file": "billing/invoices.md", "kind": "item", "parent_norm_id": "INV-3", "norm_hash": "5a627175", "own_text": "- Each invoice is one row of the CSV."},
                   {"norm_id": "INV-12", "file": "billing/invoices.md", "kind": "item", "parent_norm_id": "INV-3", "norm_hash": "7d6e5f40", "own_text": "- Every amount has two decimals, with a point."},
                   {"norm_id": "INV-15", "file": "billing/invoices.md", "kind": "item", "parent_norm_id": "INV-3", "norm_hash": "9e8d7c6b", "own_text": "- A cancelled invoice is not exported."}],
         "acceptance_areas": [{"area_id": "AA-1", "path": "areas/AA-1.md", "title": "Billing", "area_hash": "3b0900fb", "acceptance_units": ["AU-1", "AU-2", "AU-3"],
                    "scenarios": [{"scenario_id": "SC-9", "name": "A cancelled invoice is not exported", "scenario_hash": "1bd67ec5", "norms": ["INV-15"], "acceptance_units": ["AU-1", "AU-2", "AU-3"]}],
                    "evidence": {"test": 1, "demo": 0, "validation": 0, "deviation": 0, "event": 0}, "errors": []}],
         "acceptance_units": [{"unit_id": "AU-3", "path": "units/AU-3.md", "title": "Export the invoices to CSV", "area_id": "AA-1", "done_profile": "product", "unit_hash": "efc7ae86",
                    "norm_citations": [{"norm_id": "INV-7", "hash_in_acceptance_unit": "5a627175", "citation_status": "current", "hash_in_norms_repository": "5a627175"},
                                       {"norm_id": "INV-12", "hash_in_acceptance_unit": "0c1d2e3f", "citation_status": "changed", "hash_in_norms_repository": "7d6e5f40"},
                                       {"norm_id": "INV-15", "hash_in_acceptance_unit": "9e8d7c6b", "citation_status": "current", "hash_in_norms_repository": "9e8d7c6b"}],
                    "scenarios": [{"scenario_id": "SC-5", "name": "Three invoices give three rows", "scenario_hash": "147d88d2", "norms": ["INV-7", "INV-12"]},
                                  {"scenario_id": "SC-6", "name": "A cancelled invoice gives no row", "scenario_hash": "a67eb609", "norms": ["INV-15"]}],
                    "evidence": {"test": 2, "demo": 0, "validation": 1, "deviation": 0, "event": 0}, "errors": []}],
         "errors": []}
        """

    Scenario: The inventory of the working tree
      Given the skill has written the files of a change (ACU-69)
      Then the same script prints the inventory of the files of "areas/", "units/" and "acceptance.json" as they are in the working tree, against the same norms commit
      And it adds the errors of ACU-61 that compare the working tree with "HEAD"

  Rule: ACU-61 The script reports each format error of ACU-6, ACU-7, ACU-8, ACU-50, ACU-54, ACU-55 and ACU-56 (complete list)

    Scenario Outline: A format error
      Given <file> where <condition>
      When the script prints the inventory
      Then "errors" of that file, or of the repository, holds "<message>", with its line as ACU-60 says

      Examples:
        | file                 | condition                                                                                            | message                                                                     |
        | "units/AU-3.md"      | its bytes are not UTF-8                                                                              | not UTF-8                                                                   |
        | "units/AU-3.md"      | the first line is not "# AU-3 " followed by a title                                                  | heading is not "# AU-3 <title>"                                             |
        | "units/AU-3.md"      | the first line after the heading that is not empty is not "Area: <area ID>"                         | no line "Area: <area ID>"                                                   |
        | "units/AU-3.md"      | its line "Area:" names "AA-7", which has no file                                                     | acceptance area AA-7 has no file                                                       |
        | "units/AU-3.md"      | its line "Profile:" is "Profile: gold"                                                               | done profile gold is not prototype, product or critical                          |
        | "units/AU-3.md"      | its line "Profile:" names the default done profile                                                   | done profile product is the default done profile                                      |
        | "units/AU-3.md"      | its parts are not those of ACU-8 in their order, or a line that is not empty stands between them, "Increment:" included | parts are not those of ACU-8                                           |
        | "units/AU-3.md"      | "## Narrative" is not the lines "In order to ", "As a " or "As an ", and "I want ", each followed by text | narrative is not In order to, As a, I want                             |
        | "units/AU-3.md"      | "## Norms" has no list item                                                                          | no norm citation in ## Norms                                                |
        | "units/AU-3.md"      | a list item of "## Norms" is not "<norm ID>@<8 lower-case hex digits>: <reason>" (ACU-56)            | not a norm citation                                                         |
        | "units/AU-3.md"      | "## Norms" cites "INV-7" twice                                                                       | INV-7 is cited twice                                                        |
        | "units/AU-3.md"      | "## Norms" cites "INV-15", and no scenario has the tag "@INV-15"                                     | INV-15 is checked by no scenario                                            |
        | "units/AU-3.md"      | a scenario has the tag "@INV-99", which "## Norms" does not cite                                     | tag @INV-99 is not in ## Norms                                              |
        | "units/AU-3.md"      | "## Non-goals" or "## Assumptions" is neither a list nor the line "None."                            | ## Non-goals is not a list or None.                                         |
        | "units/AU-3.md"      | an assumption ends neither with "(<norm ID>)" of a norm nor with "(environment)"                     | assumption rests on no norm and not on (environment)                        |
        | "areas/AA-1.md"      | the first line is not "# AA-1 " followed by a title                                                  | heading is not "# AA-1 <title>"                                             |
        | "areas/AA-1.md"      | its parts are not those of ACU-7 in their order, or "## Purpose" holds no text                       | parts are not those of ACU-7                                                |
        | "areas/AA-1.md"      | a scenario has fewer than two tags "@unit:<unit ID>"                                                 | scenario SC-9 crosses fewer than two acceptance units                                  |
        | "areas/AA-1.md"      | a scenario has the tag "@unit:AU-8", and the line "Area:" of AU-8 does not name AA-1                 | AU-8 is not an acceptance unit of AA-1                                                  |
        | "areas/AA-1.md"      | a scenario has the tag "@INV-40", which no acceptance unit that it crosses cites in "## Norms"                  | tag @INV-40 is in ## Norms of no acceptance unit it crosses                            |
        | "units/AU-3.md"      | a tag of a scenario is not "@SC-<n>" nor "@" and a norm ID (ACU-56)                                  | tag @wip is not @SC-<n> or @<norm ID>                                       |
        | "areas/AA-1.md"      | a tag of a scenario is not "@SC-<n>" nor "@" and a norm ID (ACU-56), nor "@unit:<unit ID>"           | tag @wip is not @SC-<n>, @<norm ID> or @unit:<unit ID>                      |
        | "units/AU-3.md"      | a line of the "gherkin" block starts, after spaces and tabs, with a word that ACU-54 excludes        | Scenario Outline: is not allowed in ## Scenarios                            |
        | "units/AU-3.md"      | "## Scenarios" is not one "gherkin" code block (in an acceptance area, nor the line "None.")                    | ## Scenarios is not one gherkin block                                       |
        | "units/AU-3.md"      | a scenario has no tag "@SC-<n>", or more than one, or "<n>" has a leading zero                       | scenario "Three invoices give three rows" has not exactly one tag @SC-<n>   |
        | the repository       | two scenarios have the tag "@SC-5"                                                                   | SC-5 is the ID of more than one scenario                                    |
        | the repository       | "units/AU-9.md" exists and "last_unit_id" is 8                                                       | AU-9 is greater than last_unit_id of acceptance.json                        |
        | the repository       | a file of "areas/" or "units/" is not named "<area ID>.md" or "<unit ID>.md" of its folder           | not the file of an acceptance area or an acceptance unit                                           |
        | the working tree     | "units/AU-2.md" is new, and "last_unit_id" was 3 at "HEAD", or "HEAD" holds "units/AU-3.md"           | AU-2 was already given                                                      |
        | the working tree     | "last_unit_id" is not the highest of its value at "HEAD" and the numbers of the unit IDs at "HEAD" and in the working tree | last_unit_id of acceptance.json is 4, not 5           |

    Scenario: The same checks for each kind of ID
      Then the errors "AU-9 is greater than last_unit_id of acceptance.json", "AU-2 was already given" and "last_unit_id of acceptance.json is 4, not 5" hold for acceptance areas and scenarios alike, with "last_area_id" and "last_scenario_id"
      And a scenario ID that "HEAD" holds in any file is not new, even when it moved to another file (ACU-50)

    Scenario: A file that is not UTF-8
      Given "units/AU-3.md" is not UTF-8
      Then its "errors" hold only "not UTF-8", and its "title", "area_id" and "unit_hash" are null, and it has no norm citation and no scenario

  Rule: ACU-62 Each norm citation of "## Norms" gets one citation status, from the norms commit, where a retired node of "data/tree.jsonl" is not a norm (complete list)

    Scenario Outline: The citation status of a norm citation
      Given "units/AU-3.md" cites "INV-12@0c1d2e3f: amounts with two decimals"
      And <norms commit>
      Then the citation status of the norm citation is "<citation status>"

      Examples:
        | norms commit                                              | citation status |
        | "INV-12" is a norm with the norm hash "0c1d2e3f"           | current         |
        | "INV-12" is a norm with the norm hash "7d6e5f40"           | changed         |
        | "INV-12" is a retired node of "data/tree.jsonl"            | retired         |
        | "data/tree.jsonl" has no node "INV-12"                     | retired         |

  Rule: ACU-63 Each time the skill runs, it analyses every norm against every acceptance area and every acceptance unit, and is not bound to group every norm (ACU-2, ACU-32)

    Scenario: The analysis is always whole
      Given the norms commit adds only "INV-20" to the commit that the acceptance units cite
      When the skill runs
      Then it analyses every norm from the inventory, with its "own_text", and every file of "areas/" and "units/" at "HEAD"
      And it may propose to change any acceptance area or acceptance unit, an acceptance unit with evidence included (ACU-66)

    Scenario: A changed or retired norm citation
      Given the inventory shows the norm citation of "INV-12" in AU-3 as "changed"
      Then the proposal holds a change of AU-3 that cites "INV-12" with its norm hash at the norms commit, and reviews each scenario of AU-3 and of its acceptance area that has the tag "@INV-12" (ACU-28)
      And for a norm citation "retired", the change removes the norm citation and each tag "@INV-12", and proposes to delete AU-3 when no norm citation is left

    Scenario: A format error of a file at HEAD
      Given the inventory shows an error in "units/AU-3.md"
      Then the proposal holds a change of AU-3 that fixes it

    Scenario: A norm left out
      Given the skill groups "INV-30" in no acceptance unit
      Then the proposal is complete without it

    Scenario: A norm with no text of its own
      Given the norm "INV-3" of kind "list" has an empty "own_text", and its children are "INV-7", "INV-12" and "INV-15"
      Then the skill cites its children, and cites "INV-3" only in an acceptance unit that groups every one of its children

    Scenario: No list of the norms that no acceptance unit groups (must not)
      When the skill shows the inventory or the proposal
      Then it shows no list and no count of the norms that no acceptance unit groups

  Rule: ACU-64 The skill shows a proposal, and revises it with the requester until the requester accepts it as final

    Scenario: The summary of the inventory
      Given the inventory
      Then before the proposal the skill says this one line, filled with the values of the inventory, which binds byte for byte once filled:
        """
        Layer 2 at <first 7 hex digits of norms_commit>: <n> norms. Layer 3 at <first 7 hex digits of acceptance_commit>: <a> acceptance areas, <u> acceptance units; <c> norm citations changed, <r> retired; <e> format errors.
        """
      And each of "norms", "acceptance areas", "acceptance units", "norm citations" and "format errors" is singular when its count is 1, and plural otherwise
      And <c> and <r> count the norm citations of every acceptance unit with the citation status "changed" and "retired", and <e> counts every entry of "errors" of the inventory: of the repository, of each acceptance area and of each acceptance unit
      And an example is "Layer 2 at 9fceb02: 240 norms. Layer 3 at 1a410ef: 2 acceptance areas, 5 acceptance units; 1 norm citation changed, 0 retired; 0 format errors."

    Scenario: The form of the proposal
      Then the skill shows the proposal as below, where what binds is one numbered line per change, in the order add acceptance area, add acceptance unit, change acceptance unit, change acceptance area, delete acceptance unit, delete acceptance area, and in the order of the IDs within each, starting with "add", "change" or "delete", then "acceptance area" or "acceptance unit", its ID and its title in quotes, and the lines of ACU-66 and ACU-68; not the rest of the wording:
        """
        1. add acceptance area AA-2 "Customers"
        2. add acceptance unit AU-4 "Register a customer" in AA-2: norms CUS-1, CUS-2; scenarios SC-10, SC-11
        3. change acceptance unit AU-3 "Export the invoices to CSV": INV-12 0c1d2e3f -> 7d6e5f40; scenario SC-5 changed
           AU-3 -> pending: its evidence goes stale (test 2, validation 1)
           AA-1: its evidence goes stale (test 1)
        4. delete acceptance unit AU-2 "Cancel an invoice": INV-9 left layer 2; tests/AU-2/ deleted; scenario SC-9 of AA-1 changed
           AU-2 has evidence (test 3, validation 1): it is deleted only with its own yes
        Gaps of layer 1, one issue each after your yes:
          a. AU-4: no norm states what is shown when the email is already registered
        """

    Scenario: The requester proposes
      Given the requester says "put CUS-3 and CUS-4 in a new acceptance unit of AA-2"
      Then the skill adds that change to the proposal, with the next unit ID and a title that it proposes

    Scenario: The skill takes the initiative
      Given the requester proposes nothing
      Then the skill proposes every change that its analysis finds

    Scenario: A change that breaks a clause of module.md
      Given the requester asks for an acceptance unit "write the CSV writer"
      Then the skill does not add it, and says that it is a work item, not an acceptance unit (ACU-1)

    Scenario: The requester rejects a change
      Given the requester rejects change 1, "add acceptance area AA-2"
      Then the skill drops it, says which other changes need it, here change 2, and revises them before the proposal is final

    Scenario: The proposal is final
      When the requester says that the proposal is final
      Then the skill writes nothing before that, and only the changes of the final proposal afterwards

    Scenario: Nothing to propose
      Given the analysis finds no change, and the requester asks for none
      Then the skill writes nothing
      And it says "acceptance-management:define: no change to propose"

  Rule: ACU-65 New IDs follow the next IDs of the inventory; an ID never changes and is never given again, and a title may change (ACU-5, ACU-55)

    Scenario: New IDs in the final proposal
      Given "next_ids" holds "AU-4", and the final proposal adds two acceptance units
      Then they are AU-4 and AU-5, in the order of the proposal, which is the order of the commits of ACU-71
      And the new scenario IDs follow the order of the changes, so that each commit gives higher IDs of each kind than the commits before it
      And each time the proposal is revised, the skill gives its new IDs again in that order: a change dropped before the proposal is final gives no ID, and the IDs after it follow on without a hole

    Scenario: A title
      Then the skill proposes the title of each new acceptance area and acceptance unit: one line, in the language of the norms, that holds no ID
      And it may propose a new title for an existing acceptance area or acceptance unit, which changes only its heading

    Scenario: A deleted ID is never given again
      Given AU-2 is deleted, and "last_unit_id" is 5
      Then the next acceptance unit is AU-6, and the field stays at 5 until AU-6 is committed

    Scenario: A field lower than an ID at HEAD
      Given "HEAD" holds "units/AU-9.md", and "last_unit_id" is 8
      Then "next_ids" holds "AU-10", and the next commit sets "last_unit_id" to 9 or more, whatever it changes

    Scenario: The field is raised in the commit that gives the ID
      Given a commit adds AU-4 and scenarios SC-10 and SC-11
      Then the same commit sets "last_unit_id" to 4 and "last_scenario_id" to 11, and changes no other field of "acceptance.json"

  Rule: ACU-66 The proposal says which evidence each change makes stale; it avoids touching acceptance units with evidence; deleting or splitting one needs its own yes

    Scenario Outline: The evidence that a change makes stale (complete list)
      Given <ID> has evidence
      And the change <change>
      Then the proposal shows under that change the line "<line>", with the counts of "evidence" of the inventory, kinds with 0 left out

      Examples:
        | ID   | change                                                                   | line                                                   |
        | AU-3 | changes the unit hash of AU-3                                            | AU-3 -> pending: its evidence goes stale (test 2, validation 1) |
        | AA-1 | changes the area hash of AA-1                                            | AA-1: its evidence goes stale (test 1)                 |
        | AA-1 | changes the unit hash of AU-3, and a scenario of AA-1 crosses AU-3       | AA-1: its evidence goes stale (test 1)                 |

    Scenario: A change that leaves every unit hash and every area hash as they are
      Given the change of AU-3 changes only its title, its line "Area:" or its line "Profile:", and no acceptance area file
      Then the proposal shows no line of evidence for it (ACU-52)

    Scenario: The skill prefers what does not touch evidence
      Given two changes reach the same grouping of the norms, and only one of them changes the unit hash of an acceptance unit with evidence
      Then the skill proposes the other one

    Scenario Outline: An acceptance unit with evidence is deleted or split only with its own yes
      Given AU-2 has evidence (test 3, validation 1)
      And the final proposal holds a change that <change>
      Then before it writes anything, the skill asks "AU-2 has evidence (test 3, validation 1). <question> (yes/no)"
      And on any reply but yes, it drops that change, and revises the changes that need it

      Examples:
        | change                                                     | question       |
        | deletes AU-2                                               | Delete it?     |
        | moves a scenario or a norm citation of AU-2 to another acceptance unit | Split it?      |

  Rule: ACU-67 The skill writes the scenarios of each acceptance unit and the scenarios that cross the acceptance units of an acceptance area, as ACU-7, ACU-8 and ACU-50 say

    Scenario: The scenarios of an acceptance unit
      Given a change adds or changes an acceptance unit
      Then each norm of its "## Norms" has at least one scenario with its tag
      And each step acts through the external interface or states a result seen from outside, as the norms state them

    Scenario: The scenarios of an acceptance area
      Given an acceptance area has two acceptance units, and a norm of one of them is seen only when both work together
      Then the skill writes in the acceptance area a scenario with a tag "@unit:<unit ID>" per acceptance unit that it crosses

    Scenario Outline: The scenario ID
      Given the change <change>
      Then the scenario <result>

      Examples:
        | change                                              | result                                                     |
        | rewrites the steps of SC-5                          | keeps the tag @SC-5                                        |
        | moves SC-5 from AU-3 to AU-4                        | keeps the tag @SC-5, and leaves AU-3 in the same change    |
        | adds a new example of a norm                        | gets the next scenario ID                                  |
        | removes SC-6                                        | is removed, and SC-6 is never given again                  |

    Scenario: A scenario that moves is in one file at each commit
      Given the change "add acceptance unit AU-4" takes SC-5 and the norm citation of INV-7 out of AU-3
      Then that change also writes "units/AU-3.md" without them, so that no commit holds SC-5 twice

  Rule: ACU-68 A gap of layer 1 becomes an issue of the specs repository after the requester's yes, and its scenario is left out (ACU-4, LAY-5)

    Scenario: A gap of layer 1
      Given the skill needs for AU-4 a scenario of what is shown when an email is already registered, and no norm states it
      Then the proposal lists the gap of layer 1 under "Gaps of layer 1"
      And the changes of the final proposal hold no scenario for it; a norm that only that scenario would check is left out of "## Norms" too

    Scenario: The issue
      When the requester has said that the proposal is final
      Then before the choice of ACU-71, for each gap of layer 1, in the order of the proposal, the skill asks "Open the issue '<title>' in <owner>/<name>? (yes/no)"
      And on yes it opens it at once with "gh issue create -R <owner>/<name> --title <title> --body <body>", where "<owner>/<name>" is that of the specs repository, without reading the specs repository
      And "<title>" is "Gap of layer 1: <unit ID or area ID>: <the action or the result that no norm states>", here "Gap of layer 1: AU-4: what is shown when the email is already registered"
      And its body names the unit ID or area ID, the norm IDs that come closest, and the action or the result that no norm states

    Scenario: No specs repository
      Given "project.json" has not exactly one entry with "layer" 1
      Then the proposal still lists each gap of layer 1, and the skill asks no question of the gaps of layer 1
      And before the choice of ACU-71 it says "acceptance-management:define: project.json has not exactly one entry of layer 1, the specs repository; no issue is opened"

    Scenario: The issue cannot be opened
      Given "gh issue create" fails for the issue of a gap of layer 1
      Then the skill says "acceptance-management:define: cannot open the issue in acme/billing-specs", and goes on with the next gap of layer 1
      And the changes and their commits are not affected

    Scenario: No issue without a yes (must not)
      Given the requester says anything but yes to the gap of layer 1
      Then the skill opens no issue

  Rule: ACU-69 Every file that a commit writes passes the checks of the script before the commit

    Scenario: The files written
      When the skill has written the files of a commit
      Then every norm citation in the file of an acceptance unit that it wrote has the citation status "current"
      And the inventory of the working tree (ACU-60) shows no error in a file that the commit writes, and no other error that the inventory at "HEAD" does not hold with the same path and message

    Scenario: An error already at HEAD
      Given "units/AU-7.md" has an error at "HEAD", and the requester rejected the change that fixes it, or it comes in a later commit
      Then that error does not stop a commit that does not write "units/AU-7.md"

    Scenario: An error after writing
      Given the inventory of the working tree shows an error that ACU-69 forbids
      Then the skill fixes the files it wrote and runs the script again, and commits nothing while that error is left

  Rule: ACU-70 A deleted acceptance unit follows ACU-10, and an acceptance area left with no acceptance unit is proposed for deletion

    Scenario: An acceptance unit is deleted
      Given the final proposal deletes AU-2, and SC-9 of AA-1 crosses AU-1, AU-2 and AU-3
      Then the change deletes "units/AU-2.md" and every file of "tests/AU-2/"
      And it removes "@unit:AU-2" from SC-9, or removes SC-9 when it would cross fewer than two acceptance units, and removes from SC-9 each tag "@<norm ID>" that only AU-2 cited
      And it keeps "records/AU-2.jsonl" as it is
      And the script builds no command for that change while a file of "tests/AU-2/" that "HEAD" holds is still in the working tree

    Scenario: An acceptance unit moves to another acceptance area
      Given a change moves AU-3 from AA-1 to AA-2
      Then the change keeps "tests/AU-3/", and changes each scenario of AA-1 that crosses AU-3, as ACU-10 says

    Scenario: An acceptance area left with no acceptance unit
      Given the final proposal deletes or moves every acceptance unit of AA-1
      Then the proposal also holds "delete acceptance area AA-1", and the requester may reject it

  Rule: ACU-71 The requester chooses one commit for the whole proposal or one commit per change; each commit follows LAY-9

    Scenario: The choice
      Given the requester has said that the proposal is final, and answered every question of ACU-66 and ACU-68
      Then the skill asks "1. one commit with every change; 2. one commit per change", and writes nothing until the requester answers

    Scenario: One commit with every change
      Given the requester answers 1
      Then the skill writes every change, runs the checks of ACU-69, shows the whole diff, and shows one command that stages each file it wrote or deleted by its path, commits, and pushes to the default branch, here "origin main"
      And it runs that command only when the requester approves it

    Scenario: One commit per change
      Given the requester answers 2
      Then the skill takes the changes in the order of the proposal (ACU-64)
      And for each change it writes its files, with "acceptance.json" as that commit leaves it, runs the checks of ACU-69, shows the diff of that change, and shows its command, which it runs only when the requester approves it

    Scenario Outline: The commit message
      Given a commit holds <changes>
      Then its subject is "<subject>", followed by an empty line and one line "<verb> <ID>" per change of the commit, in the order of the proposal

      Examples:
        | changes                       | subject                                  |
        | one addition of an acceptance unit        | docs: add acceptance unit                |
        | one change of an acceptance unit          | docs: change acceptance unit             |
        | one deletion of an acceptance unit        | docs: delete acceptance unit             |
        | one addition of an acceptance area       | docs: add acceptance area                |
        | one change of an acceptance area         | docs: change acceptance area             |
        | one deletion of an acceptance area       | docs: delete acceptance area             |
        | more than one change          | docs: change acceptance areas and units  |

    Scenario: A body
      Given a commit adds AU-4 and changes AU-3
      Then its message is "docs: change acceptance areas and units", an empty line, "add AU-4" and "change AU-3"

    Scenario: What a command stages (must not)
      Then each command names every file by its path, the files of a deleted folder included
      And it never stages a folder, never uses "git add -A", "git add ." or "git commit -a", and never stages a file that the skill did not write or delete

    Scenario: A file that belongs to no change of the commit (must not)
      Given "units/AU-1.md" and "areas/AA-1.md" differ from "HEAD", and the only change of the commit is "change AU-1", which moves nothing out of "areas/AA-1.md"
      Then the script builds no command, and says "areas/AA-1.md differs from HEAD, and no change of the commit names it (ACU-71)"
      And a file belongs to a change as the term change says: the file of its ID, the files of "tests/<unit ID>/" of a deleted acceptance unit, "acceptance.json", the file out of which it moves a scenario or a norm citation (ACU-67), and the file of an acceptance area with a scenario at "HEAD" that crosses an acceptance unit that the change deletes, moves to another acceptance area, or makes no longer cite a norm of a tag of that scenario (ACU-10, ACU-70)

    Scenario: The requester refuses the command of the one commit
      Given the requester answered 1, and refuses the command
      Then the skill puts each file it wrote or deleted back as it is at "HEAD", commits nothing, and stops

    Scenario: The requester refuses the command of one change
      Given the requester answered 2, and refuses the command of a change
      Then the skill puts each file of that change back as it is at "HEAD", and drops that change and each later change that needs it, as ACU-64 says
      And it goes on with the next change that is left, which, with the later ones, takes the IDs that follow those already committed (ACU-65)
      And the changes already pushed stay

    Scenario: The default branch moved
      Given "git fetch origin", run when the script builds a command and again as the first step of that command, shows that "origin/main" holds a commit that "HEAD" does not, or fails
      Then the command stages and commits nothing, and the skill puts each file it wrote and did not commit back as it is at "HEAD", and commits nothing more
      And it says "acceptance-management:define: origin/main moved; run the skill again", or, when the fetch failed, "acceptance-management:define: cannot fetch acme/billing-acceptance"

    Scenario: The push is rejected
      Given the push of a command is rejected
      Then the skill stops, and says "acceptance-management:define: push rejected; commit 1a410ef is not on origin/main"

  Rule: ACU-72 After its commits the skill names the agents that come next, and in a run it hands off as ACU-41 says

    Scenario: The line after the commits
      Given the commits are pushed
      Then the skill says one line "Next: <parts>.", where the parts are joined by "; ", in this order (complete list):
        | part                                                     | when                                                                                   |
        | the implementation planner updates plan.json             | the commits added, changed or deleted an acceptance unit                                           |
        | the test agent updates the acceptance tests of <IDs>     | the commits created or changed the area hash or the unit hash of an acceptance area or an acceptance unit     |
      And "<IDs>" are those acceptance areas and acceptance units, the acceptance areas first, each in the order of the numbers, joined by ", "
      And when no part applies, the skill says no line "Next:"

    Scenario: Two parts
      Given the commits changed the unit hash of AU-3 and added AU-4
      Then the skill says "Next: the implementation planner updates plan.json; the test agent updates the acceptance tests of AU-3, AU-4."

    Scenario: Only a title
      Given the commits changed only the title of AU-3
      Then the skill says "Next: the implementation planner updates plan.json."

    Scenario: In a run
      Given the skill runs as the step of layer 3 of a run
      Then it does as ACU-64 to ACU-71 say, and the run goes on only once the requester has decided on every change (ACU-37, ACU-41)

  Rule: ACU-73 The skill writes only the files of the acceptance areas and the acceptance units, the ID fields of acceptance.json and the deletion of the tests of a deleted acceptance unit (must not)

    Scenario: What the skill writes (complete list)
      Then the skill writes only "areas/<area ID>.md", "units/<unit ID>.md", the fields "last_area_id", "last_unit_id" and "last_scenario_id" of "acceptance.json", and the deletion of the files of "tests/<unit ID>/" of an acceptance unit that it deletes
      And it writes no file of "records/", no other file of "tests/", no "plan.json", and no other field of "acceptance.json"

    Scenario: No increment
      Then the skill names no increment, writes no line "Increment:", and decides nothing of "plan.json" (ACU-9, ACU-44)

    Scenario: Other layers
      Then the skill writes nothing in the repositories of layers 0, 1, 2 and 4, other than the issues of ACU-68
      And it never reads the specs repository or a code repository (LAY-8)

    Scenario: The work of other sessions
      Then the skill never uses "git stash", "git reset", "git checkout", "git restore" or "git clean"
```

## Open questions

1. Until the use case of the review of the norms of [ACU-15](../../../specs/module.md#the-review-of-the-norms-selected) exists, the skill does not run that review, which the done profiles `product` and `critical` require ([ACU-19](../../../specs/module.md#done-profiles)). Is a change of an acceptance unit with one of those done profiles committed without it, or held back?
2. Should the skill take an argument that narrows the analysis of ACU-63, such as one acceptance area or the norms that changed? Issue [jpchauny/claude-plugins#10](https://github.com/jpchauny/claude-plugins/issues/10) decides it from the measured cost of a whole analysis.
3. When an acceptance area is deleted, is its folder `tests/<area ID>/` deleted in the same change, as ACU-10 says for an acceptance unit? Until decided, the skill does not delete it (ACU-73).
4. In a run, is the head of the default branch of the norms repository always the hand-off of the step of layer 2 ([ORC-9](../../../../norms-management/specs/module.md#regenerate-the-norms))? Until decided, the skill reads that head (ACU-59).
5. The line of ACU-66 names the state that an acceptance unit falls to, `pending`, and not the state that it loses, such as `AU-3 validated -> pending`: the state is computed by the scripts of [ACU-27](../../../specs/module.md#done-is-a-state-not-an-event), which read layer 4 and run in the continuous integration ([LAY-10](../../../../development-methodology/specs/layers.md#rules)), and is not stored ([ACU-23](../../../specs/module.md#the-ladder-of-states)), so a session of layer 3 cannot compute it. Should the continuous integration record the state where the skill can read it? Until decided, the line names no current state.
