# Define

**Audience:** The requesters of a project, who approve its acceptance areas and acceptance units; whoever builds the skill `define` of the plugin `acceptance-management`

**Scope:** The use case in which the acceptance architect analyses every norm of layer 2 against every acceptance area and every acceptance unit of the acceptance repository, and creates, changes and deletes acceptance areas and acceptance units, with their scenarios, and fills `test_command` and `product` of `acceptance.json` while they are empty, in changes that the requester approves. A script, with no model, computes the inventory that the analysis starts from and checks every file before it is committed. Systems it works with (complete list): git and the remote `origin` of the acceptance repository, which it reads and pushes to, and of the norms repository, which it only fetches and reads; the records of the installed plugins of Claude Code, `~/.claude/plugins/installed_plugins.json` and `~/.claude/plugins/known_marketplaces.json`, which it only reads, to find the marketplace repository (ACU-79); GitHub, through `gh`, only to open the issues of a gap of layer 1 in the specs repository (ACU-68) and of a defect of a derived-norms generator in the marketplace repository (ACU-79)

A use case of the module `acceptance-management`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md). Out of scope: the increments and `plan.json`, which the implementation planner decides ([ACU-44](../../../specs/module.md#the-plan-of-implementation)); the acceptance tests, which the test agent writes ([ACU-11](../../../specs/module.md#acceptance-tests-and-independent-evidence)); the record of the evidence ([ACU-35](../../../specs/module.md#done-is-a-state-not-an-event)); the field `default_done_profile` of `acceptance.json`, and a `test_command` or a `product` that is not empty ([ACU-43](../../../specs/module.md#the-files-of-the-acceptance-repository)); the review of the norms of [ACU-15](../../../specs/module.md#the-review-of-the-norms-selected), which is open question 1; what a derived norm is, its derived norm ID, its derived norm fingerprint and its list of derived norms, which layer 2 writes ([NRM-12 to NRM-15](../../../../norms-management/specs/module.md#the-list-of-derived-norms)), and the types of derived norms of a commit ([NRM-16](../../../../norms-management/specs/module.md#derive-the-derived-norms)); the files of the specs repository and of the marketplace repository, of which define reads none and only opens issues; the plugins installed, which define does not change; layers 0, 1, 2 and 4.

## Terms

| Term | Meaning |
|---|---|
| Skill | The skill `define` of the plugin `acceptance-management`, invoked as `/acceptance-management:define`; it acts as the acceptance architect, and is the actor of every rule that names no other. |
| Default branch | Of a repository: the branch that `git ls-remote --symref origin HEAD`, run in that repository, names. |
| Norms commit | The head of the default branch of the remote `origin` of the norms repository, after the fetch of [ACU-74](../../../specs/module.md#the-files-of-the-acceptance-repository). |
| Inventory | The JSON object that the script of ACU-60 prints. |
| Citation status | What the norms commit says of one norm citation of `## Norms`, or of one derived norm citation of `## Derived norms`, of an acceptance unit: `current`, `changed` or `retired` (ACU-62). |
| Order of ACU-78 | The order of the derived norm citations of `## Derived norms`: by the place of the type of the derived norm ID in the types of derived norms of the norms commit, a type that they do not hold coming after every type they hold, in the order of the types compared code point by code point; then by the number of the derived norm ID (ACU-61, ACU-78). |
| Change | One item of the proposal: to add, change or delete one acceptance area or one acceptance unit, with every other file that ACU-10 and ACU-70 make it touch, and the file of each acceptance unit out of which it moves a scenario or a norm citation (ACU-67); or to fill `test_command` and `product` of `acceptance.json` (ACU-77). |
| Proposal | The numbered list of changes that the skill shows to the requester (ACU-64). |
| Marketplace repository | Of a defect of a derived-norms generator: the GitHub repository, `<owner>/<name>`, of the marketplace that holds the plugin that `generator` of the status file of the type of the derived norm names, as the script finds it (ACU-79): for a plugin of the project, its tooling repository ([LAY-14](../../../../development-methodology/specs/layers.md#the-tooling-repository)). |
| Acceptance unit with evidence | An acceptance unit whose record holds at least one line. |
| Expected head | Of a command of ACU-71: the commit from which the requester saw the acceptance repository, which the command must find at `HEAD`: `acceptance_commit` of the inventory for the first command of the invocation, and for each later one the commit that the command before it pushed, whose 40 hex digits that command prints as its last line. |

The terms norm, norm ID, norm hash, derived norm, derived norm ID, derived norm fingerprint, specs repository, norms repository, acceptance repository and code repository are those of [layers.md](../../../../development-methodology/specs/layers.md#terms); a norm, its norm ID and its norm hash are those of the norms commit, and so are a derived norm, its derived norm ID, its derived norm fingerprint and a derived norm not cited. The terms list of derived norms, lines of a derived norm, derived-norms generator, status file, record of the types of derived norms and types of derived norms of a commit are those of [norms-management](../../../../norms-management/specs/module.md#terms); the term defect of a derived-norms generator is that of [drift-management](../../../../drift-management/specs/module.md#terms). The forms of a norm ID and of a derived norm ID are those of [ACU-56](../../../specs/module.md#hashes-and-citations). The terms requester, acceptance area, acceptance unit, work item, increment, unit ID, area ID, scenario ID, title, fingerprint, unit hash, area hash, scenario hash, citation, norm citation, derived norm citation, derived norms of a commit, scope of an acceptance unit, derived norm not cited, acceptance unit behind layer 2, scenario, external interface, gap of layer 1, acceptance test, acceptance architect, implementation planner, test agent, evidence, record, done profile, default done profile, state and stale are those of [module.md](../../../specs/module.md#terms). The terms run and step are those of [flow.md](../../../../development-methodology/specs/flow.md#terms). The fingerprints are computed as [ACU-51 to ACU-54](../../../specs/module.md#hashes-and-citations) say. A commit of layer 3 follows [LAY-9](../../../../development-methodology/specs/layers.md#rules).

## Define the acceptance areas and acceptance units

```gherkin
Feature: Define the acceptance areas and acceptance units
  In order to receive the norms of my project in parts that I can see working and accept
  As a requester
  I want the AI to analyse every norm against every acceptance area and acceptance unit, and to propose the acceptance areas, the acceptance units and their scenarios that I approve

  Rule: ACU-57 The skill runs when the user asks for it or as the step of layer 3 of a run, only from the acceptance repository, and takes no argument
    Rationale: the acceptance areas and the acceptance units decide what layer 4 builds and what the requester accepts, so they change only when a person or a run asks for it; run from another repository, or with an argument it does not read, the skill would analyse or write the wrong files, and the checks that refuse both are shared by every use case of the module (ACU-74).

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
      Then an argument, and a repository other than the acceptance repository, end the skill as ACU-74 says

  Rule: ACU-58 Before it reads anything else, the skill makes the checks of ACU-74, and then a script with no model makes these checks, in this order, and the first that fails ends the skill with its message (complete list)
    Rationale: the files that define writes must start from what "HEAD" holds, so an uncommitted or untracked file of an acceptance area or an acceptance unit, which the skill would overwrite or commit by mistake, stops it; an "acceptance.json" it cannot read gives no next IDs (ACU-55); and a list of derived norms that is missing or that does not meet NRM-12 gives no scope of an acceptance unit, so the skill could write no "## Derived norms" that layer 4 can trust (ACU-78). The checks that every use case of the module shares are written once, in ACU-74.

    Scenario: The checks of the module
      When the skill starts
      Then it makes the checks of ACU-74 first, with "define" as the use case, and the first that fails ends the skill as ACU-74 says

    Scenario Outline: A check of define fails
      Given every check of ACU-74 passed
      And <condition>
      When the skill starts
      Then the skill writes nothing
      And it says "acceptance-management:define: <message>"
      And the message binds byte for byte once filled, where "units/AU-3.md" and "units/AU-4.md" stand for the path found, "acme/billing-norms" for "<owner>/<name>" of the norms repository in "project.json", "grammar" for the type found and "9fceb02" for the first 7 hex digits of the norms commit
      And a path is printed as it is when it holds no control character (Unicode category Cc), no line separator (U+2028), no paragraph separator (U+2029) and no byte that is not UTF-8; otherwise it is printed as its JSON text, between double quotes, where a double quote and a backslash are escaped as \" and \\, the line feed, the carriage return, the tab, the backspace and the form feed as \n, \r, \t, \b and \f, and every other such character, and each byte that is not UTF-8 as the code point U+DC00 plus that byte, as \u followed by 4 lower-case hex digits; so no path forges a line of the output (ACU-8); an untracked file "units/a", a line feed and "b.md" gives "untracked file \"units/a\\nb.md\""

      Examples:
        | condition | message |
        | "units/AU-3.md" is the first path, in sorted order, with an uncommitted change among "acceptance.json" and the files of "areas/" and "units/" | uncommitted change in units/AU-3.md |
        | "units/AU-4.md" is the first path, in sorted order, of an untracked file under "areas/" or "units/", a file that a ".gitignore" names included | untracked file units/AU-4.md |
        | "acceptance.json" does not meet ACU-6, as the paragraph "acceptance.json meets ACU-6" of ACU-6 says | acceptance.json does not meet ACU-6 |
        | the types of derived norms of the norms commit cannot be read (see "The types of derived norms read") | acme/billing-norms: the types of derived norms at 9fceb02 cannot be read (NRM-16) |
        | "grammar" is the first type, in the order of the types of derived norms of the norms commit, whose list of derived norms cannot be read, and the norms commit holds no file "specs-derived/grammar/derived-norms.jsonl" | acme/billing-norms has no specs-derived/grammar/derived-norms.jsonl at 9fceb02 |
        | "grammar" is that first type, and its list of derived norms at the norms commit does not meet NRM-12 (see "The list of derived norms read") | acme/billing-norms: specs-derived/grammar/derived-norms.jsonl does not meet NRM-12 |

    Scenario: The types of derived norms read
      Then the script reads the types of derived norms of the norms commit, with "git show" of that commit: those of "specs-derived/types-of-derived-norms.json" when it meets NRM-16; otherwise those of "derived_norms" of "project.json" at the root of the norms repository at that commit, read as NRM-1 says, so that an entry without a "use_case" of the form of ORC-20 makes them unreadable too
      And they cannot be read when that commit holds no record that meets NRM-16 and its "project.json" cannot be read, or its "derived_norms" does not meet ORC-20, both as NRM-1 says (ACU-78)
      And the script never takes them from "derived_norms" of "project.json" of the acceptance repository, which may name other types than those by which the step of layer 2 ran (ACU-78, NRM-16)

    Scenario: The list of derived norms read
      Then the script reads, for each of the types of derived norms of the norms commit, in their order, the list of derived norms "specs-derived/<type>/derived-norms.jsonl" at the norms commit, with "git show" of that commit, never from the working tree of the norms repository
      And whether the list meets NRM-12 is what NRM-12 says of a list read alone, with no other file of the output, which states it once for every script of layer 3 or 4 and for the orchestrator (ACU-78); define checks no other condition of the list
      And the script computes no derived norm fingerprint, and does not read the files that "path" names to check the list (ACU-78, NRM-15)
      And the lists read are those of ACU-60 and of every later command of the invocation, against the same norms commit

    Scenario: A project without derived norms
      Given the types of derived norms of the norms commit are none: its record of the types of derived norms holds "[]", or it holds no record that meets NRM-16 and its "project.json" holds no "derived_norms", or holds an empty list
      Then no list of derived norms is read, and no check of a list fails
      And the norms commit has no derived norm, the scope of every acceptance unit is empty, and every derived norm citation that an acceptance unit holds is "retired" (ACU-62)

    Scenario: Other uncommitted changes
      Given the acceptance repository has an uncommitted change in "tests/AU-3/test_export.py" or in "records/AU-3.jsonl"
      When the skill starts
      Then no check fails because of it
      And the skill never stages, commits or changes that file

  Rule: ACU-59 The skill reads layer 2 at the norms commit and layer 3 at its "HEAD", and never changes the working tree of the norms repository
    Rationale: the acceptance units must cite the norms that layer 2 committed, and be written from what layer 3 committed, which is what every other session reads (ACU-41); reading a working tree would cite a norm that no commit holds, and changing the working tree of the norms repository would destroy the work of another session in it.

    Scenario: The commits read
      Given every check of ACU-58 passed
      Then the skill reads the norms repository only at the norms commit, with "git show" and "git ls-tree" of that commit, the lists of derived norms and the lines of a derived norm included
      And it reads the acceptance repository at its "HEAD", which ACU-74 made equal to "origin/main"
      And in a run it reads the same commits

    Scenario: The working tree of the norms repository (must not)
      Given the norms repository has a checked-out branch "old" and uncommitted changes
      When the skill runs
      Then its working tree, its index and its local branches are as before; only its remote-tracking branches moved, by the fetch
      And no file of its working tree is read

  Rule: ACU-60 The script prints the inventory: one JSON object on its standard output, computed with no model (complete list of fields)
    Rationale: the facts that the analysis starts from (the norms, the derived norms, the files, their hashes, their errors, their evidence and the next IDs) must be exact and the same on every run; a script with no model computes them, and only the judgement of ACU-63 is left to the model.

    Scenario: The fields of the inventory (complete list)
      Then the inventory holds these fields:
        | field             | value                                                                                                                                                 |
        | norms_commit      | the norms commit, 40 hex digits                                                                                                                       |
        | acceptance_commit | the commit of the acceptance repository read, 40 hex digits                                                                                           |
        | default_done_profile   | "default_done_profile" of "acceptance.json": the default done profile                                                                                      |
        | next_ids          | an object: "acceptance_area", "acceptance_unit" and "scenario", the next area ID, unit ID and scenario ID (ACU-55): its prefix and the highest of its field of "acceptance.json" and the numbers of the IDs of its kind in the files read, plus 1; for the inventory of the working tree, the highest also counts the IDs at "HEAD" |
        | norms             | one object per norm, in the order of "data/tree.jsonl": "norm_id", "file" (its path under "specs-repo-annotated/"), "kind", "parent_norm_id" (the norm ID of its "parent" in "data/tree.jsonl", or null), "norm_hash" and "own_text" (its "own_text" of R61: the text of the node in its file of "specs-repo-annotated/", without the text of its children and without the markers of the IDs) |
        | derived_norms     | one object per derived norm of the norms commit (ACU-78), in the order of the types of derived norms of the norms commit and, in each type, of the numbers of the derived norm IDs: "derived_norm_id", "derived_norm_fingerprint", "name", "path", "first_line", "last_line" and "cited_norms" (each an object "norm_id" and "norm_hash"), as its line of the list of derived norms gives them; an empty list when the norms commit has no types of derived norms |
        | acceptance_areas  | one object per file "areas/<area ID>.md", in the order of the numbers of the area IDs                                                                 |
        | acceptance_units  | one object per file "units/<unit ID>.md", in the order of the numbers of the unit IDs                                                                 |
        | errors            | the errors of the repository that are not of one file (ACU-61), each an object "path", "line" and "message"                                           |
      And each acceptance area holds "area_id", "path", "title" (or null when its heading does not meet ACU-7), "area_hash" (or null), "acceptance_units" (the unit IDs whose line "Area:" names it), "scenarios", "evidence" and "errors"
      And each acceptance unit holds "unit_id", "path", "title" (or null when its heading does not meet ACU-8), "area_id" (the area ID of its line "Area:", or null when no line "Area:" meets ACU-8), "done_profile" (that of its line "Profile:", or else the default done profile), "unit_hash" (or null), "norm_citations", "derived_norm_citations", "derived_norms_not_cited", "scenarios", "evidence" and "errors"
      And each norm citation holds "norm_id", "hash_in_acceptance_unit" (the norm hash that the norm citation holds), "citation_status" (ACU-62) and "hash_in_norms_repository" (the norm hash of its norm at the norms commit, or null)
      And "derived_norm_citations" holds the derived norm citations of "## Derived norms", in the order of the file, each with "derived_norm_id", "derived_norm_fingerprint_in_acceptance_unit" (the derived norm fingerprint that the derived norm citation holds), "citation_status" (ACU-62) and "derived_norm_fingerprint_in_norms_repository" (the derived norm fingerprint of its derived norm at the norms commit, or null)
      And "derived_norms_not_cited" holds each derived norm not cited of the acceptance unit, in the order of ACU-78, each with "derived_norm_id" and "derived_norm_fingerprint" (that of the norms commit)
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
         "derived_norms": [],
         "acceptance_areas": [{"area_id": "AA-1", "path": "areas/AA-1.md", "title": "Billing", "area_hash": "3b0900fb", "acceptance_units": ["AU-1", "AU-2", "AU-3"],
                    "scenarios": [{"scenario_id": "SC-9", "name": "A cancelled invoice is not exported", "scenario_hash": "1bd67ec5", "norms": ["INV-15"], "acceptance_units": ["AU-1", "AU-2", "AU-3"]}],
                    "evidence": {"test": 1, "demo": 0, "validation": 0, "deviation": 0, "event": 0}, "errors": []}],
         "acceptance_units": [{"unit_id": "AU-3", "path": "units/AU-3.md", "title": "Export the invoices to CSV", "area_id": "AA-1", "done_profile": "product", "unit_hash": "efc7ae86",
                    "norm_citations": [{"norm_id": "INV-7", "hash_in_acceptance_unit": "5a627175", "citation_status": "current", "hash_in_norms_repository": "5a627175"},
                                       {"norm_id": "INV-12", "hash_in_acceptance_unit": "0c1d2e3f", "citation_status": "changed", "hash_in_norms_repository": "7d6e5f40"},
                                       {"norm_id": "INV-15", "hash_in_acceptance_unit": "9e8d7c6b", "citation_status": "current", "hash_in_norms_repository": "9e8d7c6b"}],
                    "derived_norm_citations": [], "derived_norms_not_cited": [],
                    "scenarios": [{"scenario_id": "SC-5", "name": "Three invoices give three rows", "scenario_hash": "147d88d2", "norms": ["INV-7", "INV-12"]},
                                  {"scenario_id": "SC-6", "name": "A cancelled invoice gives no row", "scenario_hash": "a67eb609", "norms": ["INV-15"]}],
                    "evidence": {"test": 2, "demo": 0, "validation": 1, "deviation": 0, "event": 0}, "errors": []}],
         "errors": []}
        """

    Scenario: The binding example of the derived norms in the inventory
      Then the inventory of a repository with AU-11 of ACU-78, whose "## Derived norms" cites "grammar:7@3a4b5c6d" and "semantics:31@5e6f7a8b", where the norms commit holds "grammar:7" with that derived norm fingerprint, "semantics:31" with another, and "semantics:32" in the scope of AU-11, holds these fields, where the lists and the values are abridged to what is shown, and what binds is the keys, their nesting and the types of the values, not the values:
        """
        {"derived_norms": [{"derived_norm_id": "grammar:7", "derived_norm_fingerprint": "3a4b5c6d", "name": "mul_expr", "path": "specs-derived/grammar/clean.lark", "first_line": 18, "last_line": 20, "cited_norms": [{"norm_id": "SYN-3", "norm_hash": "1f2e3d4c"}]},
                           {"derived_norm_id": "semantics:31", "derived_norm_fingerprint": "6a7b8c9d", "name": "E-Mul", "path": "specs-derived/semantics/eval.md", "first_line": 40, "last_line": 47, "cited_norms": [{"norm_id": "SEM-8", "norm_hash": "2b3c4d5e"}, {"norm_id": "TYP-2", "norm_hash": "3c4d5e6f"}]},
                           {"derived_norm_id": "semantics:32", "derived_norm_fingerprint": "9c0d1e2f", "name": "E-Mul-Overflow", "path": "specs-derived/semantics/eval.md", "first_line": 49, "last_line": 55, "cited_norms": [{"norm_id": "SEM-9", "norm_hash": "4d5e6f7a"}]}],
         "acceptance_units": [{"unit_id": "AU-11",
                    "derived_norm_citations": [{"derived_norm_id": "grammar:7", "derived_norm_fingerprint_in_acceptance_unit": "3a4b5c6d", "citation_status": "current", "derived_norm_fingerprint_in_norms_repository": "3a4b5c6d"},
                                               {"derived_norm_id": "semantics:31", "derived_norm_fingerprint_in_acceptance_unit": "5e6f7a8b", "citation_status": "changed", "derived_norm_fingerprint_in_norms_repository": "6a7b8c9d"}],
                    "derived_norms_not_cited": [{"derived_norm_id": "semantics:32", "derived_norm_fingerprint": "9c0d1e2f"}]}]}
        """

    Scenario: The inventory of the working tree
      Given the skill has written the files of a change (ACU-69)
      Then the same script prints the inventory of the files of "areas/", "units/" and "acceptance.json" as they are in the working tree, against the same norms commit
      And it adds the errors of ACU-61 that compare the working tree with "HEAD"

  Rule: ACU-61 The script reports each format error of ACU-6, ACU-7, ACU-8, ACU-50, ACU-54, ACU-55, ACU-56 and ACU-78 (complete list)
    Rationale: a file that breaks the format of the module gives the scripts that read it, and layer 4, no single reading; reported by a script, with its path and line, every format error is found on every run, and the proposal can fix it (ACU-63). A derived norm citation that cites the derived norm fingerprint of the norms commit for a derived norm outside the scope is no change of layer 2 but a citation that ACU-78 never allows; a derived norm citation whose derived norm fingerprint changed gets the citation status "changed" instead (ACU-62), since layer 2, not the file, moved.

    Scenario Outline: A format error
      Given <file> where <condition>
      When the script prints the inventory
      Then "errors" of that file, or of the repository, holds "<message>", with its line as ACU-60 says

      Examples:
        | file                 | condition                                                                                            | message                                                                     |
        | "units/AU-3.md"      | its bytes are not UTF-8                                                                              | not UTF-8                                                                   |
        | "units/AU-3.md"      | the first line is not "# AU-3 " followed by a title, or the title holds a character that ACU-8 forbids in a title | heading is not "# AU-3 <title>"                                             |
        | "units/AU-3.md"      | the first line after the heading that is not empty is not "Area: <area ID>"                         | no line "Area: <area ID>"                                                   |
        | "units/AU-3.md"      | its line "Area:" names "AA-7", which has no file                                                     | acceptance area AA-7 has no file                                                       |
        | "units/AU-3.md"      | its line "Profile:" is "Profile: gold"                                                               | done profile gold is not prototype, product or critical                          |
        | "units/AU-3.md"      | its line "Profile:" names the default done profile                                                   | done profile product is the default done profile                                      |
        | "units/AU-3.md"      | its parts are not those of ACU-8 in their order, part 5 "## Derived norms" being the only one that may be absent, or a line that is not empty stands between them, "Increment:" included | parts are not those of ACU-8                                           |
        | "units/AU-3.md"      | "## Derived norms" stands elsewhere than between "## Norms" and "## Scenarios", or more than once | parts are not those of ACU-8                                           |
        | "units/AU-3.md"      | "## Narrative" is not the lines "In order to ", "As a " or "As an ", and "I want ", each followed by text | narrative is not In order to, As a, I want                             |
        | "units/AU-3.md"      | "## Norms" has no list item                                                                          | no norm citation in ## Norms                                                |
        | "units/AU-3.md"      | a list item of "## Norms" is not "<norm ID>@<8 lower-case hex digits>: <reason>" (ACU-56)            | not a norm citation                                                         |
        | "units/AU-3.md"      | "## Norms" cites "INV-7" twice                                                                       | INV-7 is cited twice                                                        |
        | "units/AU-3.md"      | "## Derived norms" has no list item                                                                  | no derived norm citation in ## Derived norms                                |
        | "units/AU-3.md"      | a list item of "## Derived norms" is not "<derived norm ID>@<8 lower-case hex digits>: <reason>" (ACU-56) | not a derived norm citation                                            |
        | "units/AU-3.md"      | "## Derived norms" cites "grammar:7" twice                                                           | grammar:7 is cited twice                                                    |
        | "units/AU-3.md"      | "## Derived norms" cites "grammar:9" with its derived norm fingerprint at the norms commit, and "grammar:9" is not in the scope of AU-3 at the norms commit (ACU-78) | grammar:9 is not in the scope of AU-3 (ACU-78) |
        | "units/AU-3.md"      | a derived norm citation of "## Derived norms", "grammar:7", comes after one that the order of ACU-78 puts after it; the error is on the first such citation | grammar:7 is not in the order of ACU-78 |
        | "units/AU-3.md"      | "## Norms" cites "INV-15", and no scenario has the tag "@INV-15"                                     | INV-15 is checked by no scenario                                            |
        | "units/AU-3.md"      | a scenario has the tag "@INV-99", which "## Norms" does not cite                                     | tag @INV-99 is not in ## Norms                                              |
        | "units/AU-3.md"      | "## Non-goals" or "## Assumptions" is neither a list nor the line "None."                            | ## Non-goals is not a list or None.                                         |
        | "units/AU-3.md"      | an assumption ends neither with "(<norm ID>)" of a norm nor with "(environment)"                     | assumption rests on no norm and not on (environment)                        |
        | "areas/AA-1.md"      | the first line is not "# AA-1 " followed by a title, or the title holds a character that ACU-8 forbids in a title | heading is not "# AA-1 <title>"                                             |
        | "areas/AA-1.md"      | its parts are not those of ACU-7 in their order, or "## Purpose" holds no text                       | parts are not those of ACU-7                                                |
        | "areas/AA-1.md"      | a scenario has fewer than two tags "@unit:<unit ID>"                                                 | scenario SC-9 crosses fewer than two acceptance units                                  |
        | "areas/AA-1.md"      | a scenario has the tag "@unit:AU-8", and the line "Area:" of AU-8 does not name AA-1                 | AU-8 is not an acceptance unit of AA-1                                                  |
        | "areas/AA-1.md"      | a scenario has the tag "@INV-40", which no acceptance unit that it crosses cites in "## Norms"                  | tag @INV-40 is in ## Norms of no acceptance unit it crosses                            |
        | "units/AU-3.md"      | a tag of a scenario is not "@SC-<n>" nor "@" and a norm ID (ACU-56)                                  | tag @wip is not @SC-<n> or @<norm ID>                                       |
        | "areas/AA-1.md"      | a tag of a scenario is not "@SC-<n>" nor "@" and a norm ID (ACU-56), nor "@unit:<unit ID>"           | tag @wip is not @SC-<n>, @<norm ID> or @unit:<unit ID>                      |
        | "units/AU-3.md"      | a line of the "gherkin" block starts, after spaces and tabs, with a word that ACU-54 excludes        | Scenario Outline: is not allowed in ## Scenarios                            |
        | "units/AU-3.md"      | "## Scenarios" is not one "gherkin" code block (in an acceptance area, nor the line "None.")                    | ## Scenarios is not one gherkin block                                       |
        | "units/AU-3.md"      | a scenario has no tag "@SC-<n>", or more than one, or "<n>" has a leading zero                       | scenario "Three invoices give three rows" has not exactly one tag @SC-<n>   |
        | "units/AU-3.md"      | the name of a scenario (ACU-54) is empty: its "Scenario:" line holds nothing after "Scenario:" but spaces and tabs | scenario has no name                                                        |
        | "units/AU-3.md"      | the name of a scenario holds a character that ACU-8 forbids in a title (ACU-54), such as a carriage return | scenario "A cancelled\rinvoice" has a character that breaks a line |
        | "units/AU-3.md"      | the name of a scenario holds a citation found in a line (ACU-56)                                     | scenario "A cancelled invoice CSV@deadbeef gives no row" holds a citation |
        | "units/AU-3.md"      | the title holds a citation found in a line (ACU-56)                                                  | title holds a citation                                                      |
        | "areas/AA-1.md"      | the title holds a citation found in a line (ACU-56)                                                  | title holds a citation                                                      |
        | the repository       | two scenarios have the tag "@SC-5"                                                                   | SC-5 is the ID of more than one scenario                                    |
        | the repository       | "units/AU-9.md" exists and "last_unit_id" is 8                                                       | AU-9 is greater than last_unit_id of acceptance.json                        |
        | the repository       | a file of "areas/" or "units/" is not named "<area ID>.md" or "<unit ID>.md" of its folder           | not the file of an acceptance area or an acceptance unit                                           |
        | the working tree     | "units/AU-2.md" is new, and "last_unit_id" was 3 at "HEAD", or "HEAD" holds "units/AU-3.md"           | AU-2 was already given                                                      |
        | the working tree     | "last_unit_id" is not the highest of its value at "HEAD" and the numbers of the unit IDs at "HEAD" and in the working tree | last_unit_id of acceptance.json is 4, not 5           |

    Scenario: The name of a scenario in a message
      Then in each message of the table above, the name of a scenario is printed between double quotes when it holds no character that ACU-58 escapes in a path, and otherwise as ACU-58 says for a path, whose JSON text brings its own double quotes; so no name forges a line of the output
      And an error of the name of a scenario has the line that the other errors of that scenario have, the first line of its text (ACU-54), and the error "title holds a citation" has line 1

    Scenario: The same checks for each kind of ID
      Then the errors "AU-9 is greater than last_unit_id of acceptance.json", "AU-2 was already given" and "last_unit_id of acceptance.json is 4, not 5" hold for acceptance areas and scenarios alike, with "last_area_id" and "last_scenario_id"
      And a scenario ID that "HEAD" holds in any file is not new, even when it moved to another file (ACU-50)

    Scenario: A file that is not UTF-8
      Given "units/AU-3.md" is not UTF-8
      Then its "errors" hold only "not UTF-8", and its "title", "area_id" and "unit_hash" are null, and it has no norm citation, no derived norm citation, no derived norm not cited and no scenario

    Scenario: The one format error that reads the derived norms
      Then "grammar:9 is not in the scope of AU-3 (ACU-78)" is the only error of the table above that reads the derived norms of the norms commit; the order of ACU-78 reads only the types of derived norms of the norms commit

  Rule: ACU-62 Each norm citation of "## Norms" and each derived norm citation of "## Derived norms" gets one citation status, from the norms commit, where a retired node of "data/tree.jsonl" is not a norm (complete list); and each derived norm of the scope that "## Derived norms" does not cite is a derived norm not cited
    Rationale: an acceptance unit that cites a norm hash or a derived norm fingerprint that layer 2 no longer holds, or that does not cite a derived norm of its scope, is behind layer 2, and layer 4 does not implement it (ACU-41); a status computed from the norms commit tells the skill exactly which citations to review, and a retired node counts as no norm, since layer 2 no longer states it.

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

    Scenario Outline: The citation status of a derived norm citation
      Given "units/AU-11.md" cites "grammar:7@3a4b5c6d: the rule of the binary operators" in "## Derived norms"
      And <norms commit>
      Then the citation status of the derived norm citation is "<citation status>"

      Examples:
        | norms commit                                                                                   | citation status |
        | the derived norms of the norms commit hold "grammar:7" with the derived norm fingerprint "3a4b5c6d" | current    |
        | they hold "grammar:7" with the derived norm fingerprint "4b5c6d7e"                             | changed         |
        | they hold no "grammar:7": the list of "grammar" no longer holds it, or the types of derived norms of the norms commit do not hold "grammar" | retired |

    Scenario: A derived norm not cited
      Given the scope of AU-11 at the norms commit holds "semantics:32", with the derived norm fingerprint "9c0d1e2f", and "## Derived norms" of AU-11 does not cite "semantics:32", or AU-11 has no "## Derived norms"
      Then "derived_norms_not_cited" of AU-11 holds "semantics:32" with "9c0d1e2f"
      And a derived norm that "## Derived norms" cites with another derived norm fingerprint is no derived norm not cited: its derived norm citation is "changed"

    Scenario: The scope is that of "## Norms" as the file holds it
      Then the scope of an acceptance unit is computed from the norm IDs of the norm citations of its "## Norms", whatever their citation status, as ACU-78 says
      And a file whose "## Norms" holds no norm citation has an empty scope

  Rule: ACU-63 Each time the skill runs, it analyses every norm against every acceptance area and every acceptance unit, and is not bound to group every norm (ACU-2, ACU-32)
    Rationale: a norm of layer 2 can touch any acceptance area or acceptance unit, and an analysis that reads only what changed misses the acceptance units that a new norm should change; a norm that fits no acceptance unit yet is left out, since grouping it by force would make an acceptance unit that no requester can accept as one thing (ACU-2, ACU-32).

    Scenario: The analysis is always whole
      Given the norms commit adds only "INV-20" to the commit that the acceptance units cite
      When the skill runs
      Then it analyses every norm from the inventory, with its "own_text", and every file of "areas/" and "units/" at "HEAD"
      And it may propose to change any acceptance area or acceptance unit, an acceptance unit with evidence included (ACU-66)

    Scenario: A changed or retired norm citation
      Given the inventory shows the norm citation of "INV-12" in AU-3 as "changed"
      Then the proposal holds a change of AU-3 that cites "INV-12" with its norm hash at the norms commit, and reviews each scenario of AU-3 and of its acceptance area that has the tag "@INV-12" (ACU-28)
      And for a norm citation "retired", the change removes the norm citation and each tag "@INV-12", and proposes to delete AU-3 when no norm citation is left

    Scenario: A changed or retired derived norm citation, or a derived norm not cited
      Given the inventory shows a derived norm citation of AU-11 "changed" or "retired", or a derived norm not cited of AU-11
      Then the proposal holds a change of AU-11 whose "## Derived norms" cites the scope of its "## Norms" at the norms commit, as ACU-67 says (ACU-28, ACU-78)
      And the skill reads, at the norms commit, the lines of each derived norm that changed or entered the scope, and reviews each scenario of AU-11, and of each acceptance area with a scenario that crosses AU-11, against them and against the norms of their tags
      And it changes a scenario only where those lines show that the scenario no longer states what the norms of its tags state

    Scenario: The derived norms are not grouped (must not)
      Then the skill never proposes a derived norm citation that the scope does not call for, nor leaves out one that it calls for, nor adds a norm to "## Norms" because a derived norm of the scope cites it (ACU-4, ACU-78)

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
    Rationale: what the requester accepts is the requester's decision (LAY-9); a proposal revised until the requester says it is final keeps every file unwritten until then, and a summary first tells the requester what the analysis starts from.

    Scenario: The summary of the inventory
      Given the inventory
      Then before the proposal the skill says this one line, filled with the values of the inventory, which binds byte for byte once filled:
        """
        Layer 2 at <first 7 hex digits of norms_commit>: <n> norms. Layer 3 at <first 7 hex digits of acceptance_commit>: <a> acceptance areas, <u> acceptance units; <c> norm citations changed, <r> retired; <e> format errors.
        """
      And each of "norms", "acceptance areas", "acceptance units", "norm citations" and "format errors" is singular when its count is 1, and plural otherwise
      And <c> and <r> count the norm citations of every acceptance unit with the citation status "changed" and "retired", and <e> counts every entry of "errors" of the inventory: of the repository, of each acceptance area and of each acceptance unit
      And an example is "Layer 2 at 9fceb02: 240 norms. Layer 3 at 1a410ef: 2 acceptance areas, 5 acceptance units; 1 norm citation changed, 0 retired; 0 format errors."

    Scenario: The summary of a project with derived norms
      Given the types of derived norms of the norms commit hold at least one type
      Then the line of the summary holds ", <d> derived norms" after "<n> norms", and "; <dc> derived norm citations changed, <dr> retired, <dm> not cited" before "; <e> format errors", and is otherwise the same
      And <d> counts the objects of "derived_norms" of the inventory, <dc> and <dr> the derived norm citations of every acceptance unit with the citation status "changed" and "retired", and <dm> the derived norms not cited of every acceptance unit
      And "derived norms" and "derived norm citations" are singular when their count is 1, and plural otherwise
      And an example, which binds byte for byte once filled, is "Layer 2 at 9fceb02: 240 norms, 31 derived norms. Layer 3 at 1a410ef: 2 acceptance areas, 5 acceptance units; 1 norm citation changed, 0 retired; 2 derived norm citations changed, 0 retired, 1 not cited; 0 format errors."

    Scenario: The form of the proposal
      Then the skill shows the proposal as below, where what binds is one numbered line per change, in the order fill acceptance.json, add acceptance area, add acceptance unit, change acceptance unit, change acceptance area, delete acceptance unit, delete acceptance area, and in the order of the IDs within each, starting with "fill acceptance.json" (ACU-77), or with "add", "change" or "delete", then "acceptance area" or "acceptance unit", its ID and its title in quotes, and the lines of ACU-66, ACU-68, ACU-77 and ACU-79; not the rest of the wording:
        """
        1. fill acceptance.json: test_command, product
           test_command: pytest "$ACCEPTANCE_TARGET" --junitxml "$ACCEPTANCE_REPORT"
           product acme/billing-code-api: build make dist && echo "$PWD/dist/app"; env PRODUCT_CMD
        2. add acceptance area AA-2 "Customers"
        3. add acceptance unit AU-4 "Register a customer" in AA-2: norms CUS-1, CUS-2; scenarios SC-10, SC-11
        4. change acceptance unit AU-3 "Export the invoices to CSV": INV-12 0c1d2e3f -> 7d6e5f40; scenario SC-5 changed
           AU-3 -> pending: its evidence goes stale (test 2, validation 1)
           AA-1: its evidence goes stale (test 1)
        5. delete acceptance unit AU-2 "Cancel an invoice": INV-9 left layer 2; tests/AU-2/ deleted; scenario SC-9 of AA-1 changed
           AU-2 has evidence (test 3, validation 1): it is deleted only with its own yes
        Gaps of layer 1, one issue each after your yes:
          a. AU-4: no norm states what is shown when the email is already registered
        """
      And a change of "## Derived norms" is shown after the changes of "## Norms" of its line, as "<derived norm ID> <old derived norm fingerprint> -> <new derived norm fingerprint>", "<derived norm ID> added" or "<derived norm ID> removed", such as "change acceptance unit AU-11 \"Multiply two integers\": semantics:31 5e6f7a8b -> 6a7b8c9d; semantics:32 added", whose wording does not bind either

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
      Given the requester rejects change 2, "add acceptance area AA-2"
      Then the skill drops it, says which other changes need it, here change 3, and revises them before the proposal is final

    Scenario: The proposal is final
      When the requester says that the proposal is final
      Then the skill writes nothing before that, and only the changes of the final proposal afterwards

    Scenario: Nothing to propose
      Given the analysis finds no change, the requester asks for none, and the proposal holds no change "fill acceptance.json" (ACU-77)
      Then the skill writes nothing
      And it says "acceptance-management:define: no change to propose"

  Rule: ACU-77 While "test_command" or "product" of "acceptance.json" is empty at "HEAD", the proposal holds a change that fills it with the values that the requester states (ACU-43)
    Rationale: the test agent writes no acceptance test until both fields hold a value (WAT-2), and only the requester knows how the product of each code repository is built, since the skill reads no code repository (ACU-12, LAY-8); asking for them in the proposal that the requester already reviews fills them as early as they are known, through the same approval and the same checks as every other change (LAY-9, ACU-69). A field that holds a value is out of the scope of define: the acceptance architect changes it by hand, in a commit that the requester approves (ACU-43), since a change of it changes how the evidence is produced from then on and is rare enough not to need a use case.

    Scenario: The questions
      Given "test_command" of "acceptance.json" at "HEAD" is the empty string, or "product" is the empty object
      When the skill has said the summary of ACU-64, and before it shows the proposal
      Then it asks the requester, as numbered questions, the value of each field that is empty: for "test_command", the command that runs the acceptance tests of one folder (ACU-6); for "product", for each code repository of layer 4 of "project.json", whether the acceptance tests need its product build, and then its "build", its "env" and, when it publishes a product build, its "published"
      And it may propose "test_command" from the language and the test framework that the requester names, and the name of each "env"; it never proposes a "build" or a "published", which only the requester states
      And it reads no code repository to find a value (ACU-12, LAY-8); the requester may take the values from what the implementing agent reports (ACU-43)

    Scenario: A field that holds a value (must not)
      Given "test_command" of "acceptance.json" at "HEAD" is not the empty string
      Then the skill asks nothing of "test_command", and no change of the proposal changes it
      And the same holds for a "product" that is not the empty object, and always for "default_done_profile"

    Scenario: The change
      Given the requester stated the value of at least one empty field
      Then the proposal holds, as its first change, the change "fill acceptance.json", which fills each empty field whose value the requester stated, and nothing else
      And under its line it shows one line per value: "test_command: <command>", and one line "product <owner>/<name>: build <command>; env <name>" per entry of "product", followed by "; published <command>" when the entry has one, in the order in which the requester gave the entries
      And a command, a name or a key is shown as ACU-58 says for a path, so that no value forges a line of the proposal
      And the lines of the example of ACU-64 bind byte for byte once filled

    Scenario: The requester does not know a value yet
      Given the requester states no value for "test_command"
      Then the change fills only the other field, or the proposal holds no change "fill acceptance.json" when the requester stated no value at all
      And before the choice of ACU-71 the skill says, for each field that stays empty, "acceptance-management:define: acceptance.json keeps test_command empty; /acceptance-management:write-acceptance-tests stops until define fills it (WAT-2)", with "product" for the other field

    Scenario Outline: A value that ACU-77 refuses
      Given the requester states <value>
      Then the script refuses it, the skill says "acceptance-management:define: <message>" and asks the requester the value again, and the proposal holds no value that the script refuses
      And the paragraph "acceptance.json meets ACU-6" of ACU-6 also refuses, in an "acceptance.json" at "HEAD", these values of the table (complete list): a "test_command" that is not a string or not valid Unicode; a "product" that is not an object; an entry that has not the fields of ACU-6; a "build" or a "published" that is not a string or not valid Unicode; an "env" that is not of the form of ACU-6
      And only ACU-77 refuses the others (complete list): a command that holds only spaces, tabs and characters that break a line (ACU-8); a "product" with no entry; a key that is not a code repository of "project.json"; an "env" that is a variable of "test_command"; two entries with the same "env"; a value for a field that is not empty at "HEAD"
      And an "acceptance.json" at "HEAD" whose values only that second list refuses, written by hand, still meets ACU-6, and write-acceptance-tests refuses it (WAT-2)
      And the message binds byte for byte once filled, where "acme/billing-code-api" and "PRODUCT_CMD" stand for the key and the name found, each printed as ACU-58 says for a path

      Examples:
        | value                                                                                                   | message                                                                                             |
        | a "test_command" that is not a string, that holds only spaces, tabs and characters that break a line (ACU-8), or that is not valid Unicode (ACU-6) | test_command is not a command                                                                       |
        | a "product" that is not an object, or that has no entry                                                 | product has no entry                                                                                |
        | an entry of "product" whose key is not "<owner>/<name>" of an entry of "project.json" with "layer" 4    | acme/billing-code-api is not a code repository of project.json                                      |
        | an entry that is not an object with the fields "build" and "env", and "published" or no other field     | the entry acme/billing-code-api of product has not the fields of ACU-6                              |
        | an entry whose "build" is not a string, holds only spaces, tabs and characters that break a line (ACU-8), or is not valid Unicode (ACU-6) | build of acme/billing-code-api is not a command                                                     |
        | an entry whose "published" is not a string, holds only spaces, tabs and characters that break a line (ACU-8), or is not valid Unicode (ACU-6) | published of acme/billing-code-api is not a command                                                 |
        | an entry whose "env" is not a string of "A"-"Z", "0"-"9" and "_" that does not start with a digit       | env PRODUCT_CMD of acme/billing-code-api is not a name of A-Z, 0-9 and _ that does not start with a digit |
        | an entry whose "env" is "ACCEPTANCE_TARGET" or "ACCEPTANCE_REPORT"                                      | env PRODUCT_CMD of acme/billing-code-api is a variable of test_command (ACU-6)                      |
        | two entries with the same "env"                                                                         | env PRODUCT_CMD is named by more than one entry of product                                          |
        | a value for a field that is not empty at "HEAD"                                                         | test_command of acceptance.json is not empty; define fills only an empty field (ACU-43)             |

    Scenario Outline: The acceptance tests that the implementing agents will not run (ACU-49)
      Given the change fills "product"
      And <condition>
      Then under the line of the change the proposal shows the line "<line>", one per code repository found, in the order of "project.json"
      And the line binds byte for byte once filled, where "acme/billing-code-api" and "acme/billing-code-web" stand for the code repositories found, and a list of code repositories is joined by ", "

      Examples:
        | condition                                                                                                   | line                                                                                                  |
        | "acme/billing-code-web" is a code repository of layer 4 of "project.json", and "product" has no entry for it | acme/billing-code-web has no entry in product: its implementing agent runs no acceptance test (ACU-49) |
        | the entry of "acme/billing-code-api" has no "published", and "product" has an entry for "acme/billing-code-web" | acme/billing-code-api has no published: no acceptance test runs in the tasks of acme/billing-code-web (ACU-49) |

  Rule: ACU-65 New IDs follow the next IDs of the inventory; an ID never changes and is never given again, and a title may change (ACU-5, ACU-55)
    Rationale: an ID is what every other file, test, record and commit uses to name an acceptance area, an acceptance unit or a scenario (ACU-5); an ID that changed or was given again would make an old record or test name another thing, while a title only describes, and may change freely (ACU-5).

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
      Then the same commit sets "last_unit_id" to 4 and "last_scenario_id" to 11, and changes no other field of "acceptance.json" than those that a change "fill acceptance.json" of the same commit fills (ACU-77)

  Rule: ACU-66 The proposal says which evidence each change makes stale; it avoids touching acceptance units with evidence; deleting or splitting one needs its own yes
    Rationale: evidence of an acceptance unit is the work of layer 4 and of the test agent, and a change of its unit hash makes it stale (ACU-27); the requester must see that cost before accepting the change, and deleting or splitting an acceptance unit with evidence loses that work, so it needs its own yes.

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

    Scenario: An update of "## Derived norms" is never left out to spare evidence (must not)
      Given AU-11 has evidence, and a derived norm citation of AU-11 that is "changed" or "retired", or a derived norm not cited of AU-11
      Then the skill proposes the change of AU-11 of ACU-63 all the same, with the lines of ACU-66 that its new unit hash calls for
      And that evidence is already stale, since AU-11 is behind layer 2 at the head of the norms repository (ACU-26)

    Scenario Outline: An acceptance unit with evidence is deleted or split only with its own yes
      Given AU-2 has evidence (test 3, validation 1)
      And the final proposal holds a change that <change>
      Then before it writes anything, the skill asks "AU-2 has evidence (test 3, validation 1). <question> (yes/no)"
      And on any reply but yes, it drops that change, and revises the changes that need it

      Examples:
        | change                                                     | question       |
        | deletes AU-2                                               | Delete it?     |
        | moves a scenario or a norm citation of AU-2 to another acceptance unit | Split it?      |

  Rule: ACU-67 The skill writes the scenarios of each acceptance unit and the scenarios that cross the acceptance units of an acceptance area, as ACU-7, ACU-8 and ACU-50 say, and the "## Derived norms" of each acceptance unit, as ACU-78 says
    Rationale: the scenarios are what the acceptance tests check and what the requester accepts (ACU-11); each norm of an acceptance unit needs a scenario that shows it from outside, and a norm seen only when several acceptance units work together needs a scenario of their acceptance area, or no test ever checks it. The derived norms that an acceptance unit cites follow from its norms (ACU-78): a script that gives them leaves the model only the reasons, so that every acceptance unit cites the same derived norms with the same derived norm fingerprints that layer 4 reads.

    Scenario: The scenarios of an acceptance unit
      Given a change adds or changes an acceptance unit
      Then each norm of its "## Norms" has at least one scenario with its tag
      And each step acts through the external interface or states a result seen from outside, as the norms state them

    Scenario: The derived norms of an acceptance unit
      Given a change adds or changes an acceptance unit, and the skill has written its "## Norms"
      When the skill runs the command "derived-norms" of the script with the norms commit and the unit ID of the acceptance unit
      Then the script prints, for the file of the acceptance unit as the working tree holds it, one JSON list of the derived norms of its scope at the norms commit, in the order of ACU-78, one object per derived norm with exactly these fields, in this order: "derived_norm_id", "derived_norm_fingerprint", "name", "path", "first_line" and "last_line", as the list of derived norms of the norms commit gives them; "lines_of_derived_norm", the lines of a derived norm, from "first_line" to "last_line" of its file at the norms commit, as steps 1 and 2 of NRM-14 give them, joined by line feeds, or null when that commit holds no such lines; "reason_in_acceptance_unit", the reason that the file already gives for that derived norm ID in "## Derived norms", or null; and "derived_norm_citation_without_reason", "- <derived norm ID>@<derived norm fingerprint>: ", the list item of the derived norm citation that the reason completes
      And the skill reads the lines of a derived norm only through that output (ACU-59, ACU-63)
      And when that list is not empty, the skill writes "## Derived norms" between "## Norms" and "## Scenarios": one list item "- <derived norm ID>@<derived norm fingerprint>: <reason>" per derived norm of the list, in its order, with the reason that the file already gives, or a reason of its own that says in a few words what of the derived norm the acceptance unit needs (ACU-56)
      And when that list is empty, the file holds no "## Derived norms"
      And the set of derived norms, their order and their derived norm fingerprints are those of the script, never of the model; only the reasons are the skill's
      And no scenario has the tag of a derived norm (ACU-8)

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
    Rationale: layer 3 must not invent behaviour that no norm states (ACU-4); a gap of layer 1 is fixed where the norms are written, so it becomes an issue of the specs repository (LAY-5), and a scenario for it would make layer 4 build what nobody specified.

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
      And the message binds byte for byte once filled, where "acme/billing-specs" stands for "<owner>/<name>" of the specs repository in "project.json"
      And the changes and their commits are not affected

    Scenario: No issue without a yes (must not)
      Given the requester says anything but yes to the gap of layer 1
      Then the skill opens no issue

  Rule: ACU-79 A derived norm that does not follow from right norms becomes, after the requester's yes, an issue of the marketplace repository of its derived-norms generator, and no scenario is built from what it adds (ACU-4, LAY-5, ORC-14)
    Rationale: a derived norm that says what its norms do not say would make layers 3 and 4 build what nobody specified; when its norms are right the fault is in its derived-norms generator, which is fixed where it is built (ORC-14), and an issue in the specs repository would ask to change norms that are already right. The facts of the issue come from a script, so that the issue names the derived norm, its norms and the generator exactly as layer 2 recorded them.

    Scenario: A defect of a derived-norms generator
      Given the skill reads, in the output of the command "derived-norms" for AU-11 (ACU-67), that "grammar:7" says what "SYN-3", the only norm it cites, does not say, and "SYN-3" is right
      Then the proposal lists the defect after the gaps of layer 1, under "Defects of derived-norms generators, one issue each after your yes:", one line per derived norm, such as "a. grammar:7 (AU-11): makes * right-associative, which SYN-3 does not say", whose wording does not bind
      And the changes of the final proposal hold no scenario that checks what "grammar:7" adds to "SYN-3"
      And "## Derived norms" of AU-11 still cites "grammar:7", as ACU-78 says

    Scenario: What the script prints for the issue
      When the skill runs the command "derived-norms-generator" of the script with the norms commit and "grammar:7"
      Then the script prints one JSON object with exactly these fields: "derived_norm_id", "derived_norm_fingerprint", "type", "name", "path", "first_line", "last_line" and "cited_norms", as the list of derived norms of its type, "grammar", at the norms commit gives them; "status_file", the path of the status file of the type at the norms commit, or null; "generator", the object "generator" of its first line, or null; "marketplace_repository", or null; "issue_body_start"; and "no_issue_message", null or the line that says why no issue can be opened
      And the status file of the type is the one file under "specs-derived/<type>/" at the norms commit, other than its list of derived norms, whose first line, its header line, is a JSON object with "type" "header" and with "generator" an object of exactly "plugin", "version" and "tooling_commit", each a string (NRM-5); or, a status file written before its first line was named the header line, with "type" "meta" and with "generator" an object of exactly "plugin", "version" and "marketplace_commit", each a string, whose "marketplace_commit" the script gives as "tooling_commit" (NRM-5); when no file, or more than one, is such a file, "status_file", "generator" and "marketplace_repository" are null
      And "issue_body_start" is these four lines, each ended by a line feed, which bind byte for byte once filled, the cited norms in the order of "cited_norms", joined by ", ":
        """
        Derived norm: <derived norm ID>@<derived norm fingerprint>, of the type <type>, lines <first_line> to <last_line> of <path>
        Cited norms: <norm ID>@<norm hash>, <norm ID>@<norm hash>
        Generator: <plugin> <version>, tooling commit <tooling_commit>
        Norms commit: <norms commit, 40 hex digits>
        """
      And when "generator" is null, its third line is "Generator: no status file with a generator (NRM-5)"
      And the script reads nothing else of the norms repository than, at the norms commit, with "git ls-tree" and "git show" (ACU-59), what gives the types of derived norms of the norms commit and the files of "specs-derived/<type>/": of the lists of derived norms, only that of the type of the derived norm ID, so a list of another type that cannot be read changes nothing of the output

    Scenario Outline: The derived norm ID cannot be looked up
      Given <case>
      When the skill runs the command "derived-norms-generator" of the script with the norms commit and "grammar:7"
      Then the script prints "acceptance-management:define: <message>" and exits 1
      And the message binds byte for byte once filled, where "grammar:7" stands for the derived norm ID given, "grammar" for its type, "acme/billing-norms" for "<owner>/<name>" of the norms repository in "project.json" and "9fceb02" for the first 7 hex digits of the norms commit

      Examples:
        | case | message |
        | the types of derived norms of the norms commit cannot be read, as the scenario "The types of derived norms read" of ACU-58 says | acme/billing-norms: the types of derived norms at 9fceb02 cannot be read (NRM-16) |
        | the types of derived norms of the norms commit do not hold "grammar" | grammar:7 is not a derived norm of the norms commit |
        | the norms commit holds no file "specs-derived/grammar/derived-norms.jsonl" | acme/billing-norms has no specs-derived/grammar/derived-norms.jsonl at 9fceb02 |
        | "specs-derived/grammar/derived-norms.jsonl" at the norms commit does not meet NRM-12, as the scenario "The list of derived norms read" of ACU-58 says | acme/billing-norms: specs-derived/grammar/derived-norms.jsonl does not meet NRM-12 |
        | that list holds no line with "derived_norm_id" "grammar:7" | grammar:7 is not a derived norm of the norms commit |

    Scenario Outline: The marketplace repository
      Given "generator" names the plugin "clean-derived-norms" with the tooling commit "<sha>"
      And <installed>
      Then "marketplace_repository" is <result>

      Examples:
        | installed | result |
        | "plugins" of "~/.claude/plugins/installed_plugins.json" holds the key "clean-derived-norms@jpchauny-plugins", and "~/.claude/plugins/known_marketplaces.json" holds "jpchauny-plugins" with "source" {"source": "github", "repo": "jpchauny/claude-plugins"} | "jpchauny/claude-plugins" |
        | "plugins" holds the keys "clean-derived-norms@a" and "clean-derived-norms@b", and only an entry of "clean-derived-norms@a" has "gitCommitSha" "<sha>" | the "repo" of "a" |
        | "plugins" holds the keys "clean-derived-norms@a" and "clean-derived-norms@b", and an entry of each, or of neither, has "gitCommitSha" "<sha>" | null |
        | "plugins" holds no key "clean-derived-norms@<marketplace>" | null |
        | the "source" of the marketplace is not "github", or its "repo" is not "<owner>/<name>" | null |
        | either file is missing or is not a JSON object | null |

    Scenario Outline: Why no issue can be opened
      Given <case>
      Then "no_issue_message" is "<message>"
      And the message binds byte for byte once filled, where "grammar:7" stands for the derived norm ID given, "grammar" for its type and "clean-derived-norms" for "plugin" of "generator", printed as ACU-58 says for a path, so that no name of a plugin forges a line

      Examples:
        | case | message |
        | "generator" is null | acceptance-management:define: the output of grammar has no status file with a generator (NRM-5); no issue is opened for grammar:7 |
        | "generator" is not null and "marketplace_repository" is null | acceptance-management:define: no installed marketplace on GitHub holds the plugin clean-derived-norms; no issue is opened for grammar:7 |

    Scenario: The issue
      When the requester has said that the proposal is final
      Then after the questions of ACU-68, and before the choice of ACU-71, for each defect of a derived-norms generator whose "no_issue_message" is null, in the order of the proposal, the skill shows the title and the body of its issue and asks "Open the issue '<title>' in <marketplace_repository>? (yes/no)"
      And "<title>" is "Defect of a derived-norms generator: <derived norm ID>: <what does not follow>", here "Defect of a derived-norms generator: grammar:7: makes * right-associative, which SYN-3 does not say"
      And the body is "issue_body_start", one empty line, and what of the derived norm does not follow from which of its cited norms
      And on yes it opens it at once with "gh issue create -R <marketplace_repository> --title <title> --body <body>", and reads no file of the marketplace repository

    Scenario: No issue can be opened
      Given "no_issue_message" of a defect is not null
      Then the proposal still lists the defect, the skill asks no question of it, and before the choice of ACU-71 it says "no_issue_message" as it is

    Scenario: The issue cannot be opened
      Given "gh issue create" fails for the issue of a defect of a derived-norms generator
      Then the skill says "acceptance-management:define: cannot open the issue in jpchauny/claude-plugins", and goes on with the next defect
      And the message binds byte for byte once filled, where "jpchauny/claude-plugins" stands for "marketplace_repository" of the defect
      And the changes and their commits are not affected

    Scenario: No issue without a yes (must not)
      Given the requester says anything but yes to the defect
      Then the skill opens no issue

  Rule: ACU-69 Every file that a commit writes passes the checks of the script before the commit
    Rationale: every reader of the acceptance repository, the scripts of the module and layer 4 among them, must be able to read every committed file; checked by the script before the commit, no commit of define adds a format error, a norm citation or a derived norm citation that is not current, or a derived norm not cited, while an error already at HEAD that the commit does not touch does not block it.

    Scenario: The files written
      When the skill has written the files of a commit
      Then every norm citation and every derived norm citation in the file of an acceptance unit that it wrote has the citation status "current", and that file has no derived norm not cited (ACU-62)
      And the inventory of the working tree (ACU-60) shows no error in a file that the commit writes, and no other error that the inventory at "HEAD" does not hold with the same path and message
      And "acceptance.json" differs from "HEAD" only in the fields that ACU-73 lets the skill write, and each value of "test_command" and "product" that differs from "HEAD" is one that ACU-77 does not refuse

    Scenario: An error already at HEAD
      Given "units/AU-7.md" has an error at "HEAD", and the requester rejected the change that fixes it, or it comes in a later commit
      Then that error does not stop a commit that does not write "units/AU-7.md"

    Scenario: An error after writing
      Given the inventory of the working tree shows an error that ACU-69 forbids
      Then the skill fixes the files it wrote and runs the script again, and commits nothing while that error is left

  Rule: ACU-70 A deleted acceptance unit follows ACU-10, and an acceptance area left with no acceptance unit is proposed for deletion
    Rationale: a deleted acceptance unit leaves tests, scenarios of its acceptance area and tags that name it, and those would name something that no longer exists (ACU-10); the record stays, since it is the history of the evidence (ACU-35); an acceptance area with no acceptance unit holds nothing to accept, so its deletion is proposed, and the requester decides it.

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
    Rationale: the requester approves each commit (LAY-9), and may want one commit to review or one per change to keep each apart; a command that stages only the files of its changes keeps the work of other sessions out of the commit, and the checks that the repository did not move since the start keep the command from publishing what the requester never saw.

    Scenario: The choice
      Given the requester has said that the proposal is final, and answered every question of ACU-66, ACU-68 and ACU-79
      Then the skill asks "1. one commit with every change; 2. one commit per change", and writes nothing until the requester answers

    Scenario: One commit with every change
      Given the requester answers 1
      Then the skill writes every change, runs the checks of ACU-69, shows the whole diff, and shows one command that stages each file it wrote or deleted by its path, even when a ".gitignore" names it, commits, and pushes to the default branch, here "origin main"
      And it runs that command only when the requester approves it

    Scenario: One commit per change
      Given the requester answers 2
      Then the skill takes the changes in the order of the proposal (ACU-64)
      And for each change it writes its files, with "acceptance.json" as that commit leaves it, runs the checks of ACU-69, shows the diff of that change, and shows its command, which it runs only when the requester approves it

    Scenario Outline: The commit message
      Given a commit holds <changes>
      Then its subject is "<subject>", followed by an empty line and one line "<verb> <ID>" per change of the commit, in the order of the proposal, the line of the change of ACU-77 being "fill acceptance.json"

      Examples:
        | changes                       | subject                                  |
        | one addition of an acceptance unit        | docs: add acceptance unit                |
        | one change of an acceptance unit          | docs: change acceptance unit             |
        | one deletion of an acceptance unit        | docs: delete acceptance unit             |
        | one addition of an acceptance area       | docs: add acceptance area                |
        | one change of an acceptance area         | docs: change acceptance area             |
        | one deletion of an acceptance area       | docs: delete acceptance area             |
        | one filling of acceptance.json           | docs: fill acceptance.json               |
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
      And the path in that message is printed as ACU-58 says for the path found
      And "test_command" or "product" of "acceptance.json" belongs only to the change "fill acceptance.json": when either differs from "HEAD" and no change of the commit is "fill acceptance.json", the script builds no command, and says "acceptance.json differs from HEAD in test_command or product, and no change of the commit names it (ACU-71)"
      And a file belongs to a change as the term change says: the file of its ID, the files of "tests/<unit ID>/" of a deleted acceptance unit, "acceptance.json", the file out of which it moves a scenario or a norm citation (ACU-67), and the file of an acceptance area with a scenario at "HEAD" that crosses an acceptance unit that the change deletes, moves to another acceptance area, or makes no longer cite a norm of a tag of that scenario (ACU-10, ACU-70)

    Scenario: The requester refuses the command of the one commit
      Given the requester answered 1, and refuses the command
      Then the skill puts each file it wrote or deleted back as it is at "HEAD", commits nothing, and stops

    Scenario: The requester refuses the command of one change
      Given the requester answered 2, and refuses the command of a change
      Then the skill puts each file of that change back as it is at "HEAD", and drops that change and each later change that needs it, as ACU-64 says
      And it goes on with the next change that is left, which, with the later ones, takes the IDs that follow those already committed (ACU-65)
      And the changes already pushed stay

    Scenario: The repository moved since the start
      Then the script, when it builds a command, and the command, before it stages anything, make the checks of [ACU-75](../../../specs/module.md#the-files-of-the-acceptance-repository), whose commit seen by the requester is the expected head
      And when one fails, the command stages and commits nothing, exits with the status 3 and says the message of ACU-75, and the skill puts each file it wrote and did not commit back as it is at "HEAD", and commits nothing more
      And the command prints nothing of the output of its "git fetch" and its "git push", their errors included, so that a failed fetch or a rejected push prints only the message of ACU-75; the output of its "git add" and its "git commit" is printed as git gives it

    Scenario: The command pushed
      Given the push of a command succeeds
      Then the last line of the output of the command is the 40 hex digits of the commit it pushed, which is the expected head of the next command

    Scenario: The push is rejected
      Given the push of a command is rejected
      Then the command exits with the status 4 and says the message of ACU-75, here "acceptance-management:define: push rejected; commit 1a410ef is not on origin/main; run git pull --rebase, then git push, and run the skill again"
      And the skill says that line as it is and stops; the commit stays on the local default branch, and nothing is put back

    Scenario: Git or a hook refuses the commit
      Given the command staged its files, and git or a hook refuses the commit, so that the command exits with a status other than 0, 3 and 4
      Then the skill says the output of the command as it is, puts each file it wrote and did not commit back as it is at "HEAD", and stops

    Scenario: The stand-ins of the messages of ACU-71
      Then the messages of ACU-75 that ACU-71 says bind byte for byte once filled with the stand-ins that ACU-75 states

  Rule: ACU-72 After its commits the skill names the agents that come next, and in a run it hands off as ACU-41 says
    Rationale: the commits of define are worth nothing to layer 4 until the plan of implementation and the acceptance tests follow them (ACU-37); naming each agent with its command tells the requester where to go, and naming none when nothing they read changed, or the test agent when write-acceptance-tests would refuse to start because "test_command" or "product" is empty (WAT-2), sends nobody to work for nothing.

    Scenario: The line after the commits
      Given the commits are pushed
      Then the skill says one line "Next: <parts>.", where the parts are joined by "; ", in this order (complete list):
        | part                                                     | when                                                                                   |
        | the implementation planner updates plan.json with /acceptance-management:plan | the commits added or deleted an acceptance unit, or changed the unit hash of one |
        | the test agent updates the acceptance tests of <IDs> with /acceptance-management:write-acceptance-tests | the commits created or changed the area hash or the unit hash of an acceptance area or an acceptance unit, or filled "test_command" or "product" of "acceptance.json" (ACU-77); and neither "test_command" nor "product" of "acceptance.json" is empty at "HEAD"; and "HEAD" holds an acceptance area or an acceptance unit |
      And "<IDs>" are those acceptance areas and acceptance units, or, when the commits filled "test_command" or "product", every acceptance area and every acceptance unit that "HEAD" holds; the acceptance areas first, each in the order of the numbers, joined by ", "
      And when no part applies, the skill says no line "Next:"

    Scenario: Two parts
      Given the commits changed the unit hash of AU-3 and added AU-4, and neither "test_command" nor "product" of "acceptance.json" is empty at "HEAD"
      Then the skill says "Next: the implementation planner updates plan.json with /acceptance-management:plan; the test agent updates the acceptance tests of AU-3, AU-4 with /acceptance-management:write-acceptance-tests."

    Scenario: Only a title
      Given the commits changed only the title of AU-3
      Then the skill says no line "Next:", since no unit hash and no area hash changed (ACU-52)

    Scenario: Hash changed, product still empty
      Given the commits changed the unit hash of AU-3, and "product" of "acceptance.json" is still the empty object at "HEAD"
      Then the line "Next:" holds no part of the test agent, since write-acceptance-tests would refuse to start (WAT-2); here it says "Next: the implementation planner updates plan.json with /acceptance-management:plan."

    Scenario: Only acceptance.json filled
      Given "HEAD" holds AA-1, AU-1, AU-2 and AU-3, and the only commit filled "product", while "test_command" already held a value
      Then the skill says "Next: the test agent updates the acceptance tests of AA-1, AU-1, AU-2, AU-3 with /acceptance-management:write-acceptance-tests."

    Scenario: In a run
      Given the skill runs as the step of layer 3 of a run
      Then it does as ACU-64 to ACU-71, ACU-77 and ACU-79 say, and the step goes on only once the requester has decided on every change (ACU-37, ACU-41)
      And when its line "Next:" holds the part of the implementation planner, the step goes on with /acceptance-management:plan (ACU-37, PLN-1)
      And then, whatever its line "Next:" holds, when neither "test_command" nor "product" of "acceptance.json" is empty at "HEAD", the step goes on with /acceptance-management:write-acceptance-tests, which proposes every acceptance test that is missing or stale, also those that no commit of this step changed (ACU-37, WAT-1)

  Rule: ACU-73 The skill writes only the files of the acceptance areas and the acceptance units, the ID fields of acceptance.json, its test_command and product while they are empty, and the deletion of the acceptance tests of a deleted acceptance unit (must not)
    Rationale: the acceptance architect decides only what an acceptance area and an acceptance unit are, and fills the fields of acceptance.json that ACU-43 gives it (ACU-44, ACU-48); keeping it to its own files keeps a change of define from changing the plan of implementation, the evidence or the acceptance tests of the test agent, and the commands that may change the files or the index of many paths would destroy the work of other sessions.

    Scenario: What the skill writes (complete list)
      Then the skill writes only "areas/<area ID>.md", "units/<unit ID>.md", the fields "last_area_id", "last_unit_id" and "last_scenario_id" of "acceptance.json", the fields "test_command" and "product" of "acceptance.json" when they are empty at "HEAD" (ACU-77), and the deletion of the files of "tests/<unit ID>/" of an acceptance unit that it deletes
      And it writes no file of "records/", no other file of "tests/", no "plan.json", and no other field of "acceptance.json"

    Scenario: No increment
      Then the skill names no increment, writes no line "Increment:", and decides nothing of "plan.json" (ACU-9, ACU-44)

    Scenario: Other layers
      Then the skill writes nothing in the repositories of layers 0, 1, 2 and 4, other than the issues of ACU-68, and nothing in any other repository, other than the issues of ACU-79
      And it never reads the specs repository or a code repository (LAY-8)

    Scenario: The work of other sessions
      Then the skill never uses "git stash", "git reset", "git checkout", "git restore" or "git clean"
```

## Open questions

1. Until the use case of the review of the norms of [ACU-15](../../../specs/module.md#the-review-of-the-norms-selected) exists, the skill does not run that review, which the done profiles `product` and `critical` require ([ACU-19](../../../specs/module.md#done-profiles)). Is a change of an acceptance unit with one of those done profiles committed without it, or held back?
2. Should the skill take an argument that narrows the analysis of ACU-63, such as one acceptance area or the norms that changed? Issue [jpchauny/claude-plugins#10](https://github.com/jpchauny/claude-plugins/issues/10) decides it from the measured cost of a whole analysis.
3. When an acceptance area is deleted, is its folder `tests/<area ID>/` deleted in the same change, as ACU-10 says for an acceptance unit? Until decided, the skill does not delete it (ACU-73).
4. In a run, is the head of the default branch of the norms repository always the hand-off of the step of layer 2 ([ORC-9](../../../../norms-management/specs/module.md#regenerate-the-norms))? Until decided, the skill reads that head (ACU-59).
5. The line of ACU-66 names the state that an acceptance unit falls to, `pending`, and not the state that it loses, such as `AU-3 validated -> pending`: the state is computed by the scripts of [ACU-27](../../../specs/module.md#done-is-a-state-not-an-event), which read layer 4 and are run by the orchestrator, or by the continuous integration once it is enabled ([LAY-10](../../../../development-methodology/specs/layers.md#rules)), and is not stored ([ACU-23](../../../specs/module.md#the-ladder-of-states)), so a session of layer 3 cannot compute it. Should the orchestrator record the state where the skill can read it? Until decided, the line names no current state.
