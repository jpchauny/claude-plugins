# Acceptance management

**Prefix:** ACU

**Audience:** The people who decide what a project delivers and accept it, and the Claude Code sessions of layers 3 and 4; whoever builds the plugin `acceptance-management`

**Scope:** Layer 3: the acceptance areas and the acceptance units of a project, their acceptance tests, how they relate to the norms and to the code, and when a unit, an area and an increment are done. Its use case `define`, with which the acceptance architect creates, changes and deletes the acceptance areas and the acceptance units, is in [define.md](../use-cases/define/specs/define.md). Out of scope: how layer 4 implements a unit, which is in [implement.md](../../code-implementation/use-cases/implement/specs/implement.md); what the five layers are and what each reads, which is in [layers.md](../../development-methodology/specs/layers.md); where this module is installed, which is [APP-6](../../development-methodology/specs/layers.md#where-each-module-is-installed)

The module `acceptance-management` of the app Indra Software Factory, listed in [app.md](../../../specs/app.md). The terms norm, norm ID and norm hash are those of [implement.md](../../code-implementation/use-cases/implement/specs/implement.md#terms).

The norms say what the product must do, rule by rule. They do not say what
the person receives, nor when it is finished: every norm can hold on its own
while the whole does not work. An acceptance unit is that missing piece: a
part of the product that the person can see working end to end, with the
norms it groups, the evidence that it works, and the person's acceptance.

## Terms

| Term | Meaning |
|---|---|
| Acceptance repository | The repository of layer 3 of a project, `<project>-acceptance` by recommendation: one for the whole project ([LAY-1](../../development-methodology/specs/layers.md#rules)). |
| Code repository | A repository of layer 4. |
| Requester | The person who asks for the acceptance areas and the acceptance units of a project, approves them and validates them. |
| Acceptance unit | The smallest part of the product that the requester can recognise and validate end to end (ACU-1). |
| Work item | A piece of work of layer 4 that the requester cannot judge alone, such as "write the parser". |
| Acceptance area | An observable area of the product, made of acceptance units, such as "Billing" (ACU-3). |
| Increment | A set of acceptance units that are delivered together, such as a first release. The implementation planner decides it (ACU-9). |
| Unit ID | The ID of an acceptance unit: `AU-` followed by a number, such as `AU-3`. |
| Area ID | The ID of an acceptance area: `AA-` followed by a number, such as `AA-1`. |
| Scenario ID | The ID of a scenario: `SC-` followed by a number, such as `SC-5`, written as its tag `@SC-5` (ACU-50). |
| Unit hash | The fingerprint of the file of an acceptance unit from its line `## Narrative` to its end, such as `efc7ae86` (ACU-52). |
| Area hash | The fingerprint of the file of an acceptance area from its line `## Purpose` to its end (ACU-53). |
| Scenario hash | The fingerprint of the text of one scenario (ACU-54). |
| Citation | One line `<ID>@<hash>: <text>`, in one of the forms of ACU-56: a norm in `## Norms` of a unit; a unit in the code and the unit tests of layer 4; a unit or an area, and a scenario, in an acceptance test. |
| Non-goal | One thing that a unit does not do: a list item of its section `## Non-goals` (ACU-8). |
| Scenario | One example of use of a unit or an area, in Gherkin: a starting state (`Given`), an action through the external interface (`When`) and a result seen from outside (`Then`). |
| External interface | What the product shows to the outside: its commands, endpoints, screens, files and public functions. |
| Acceptance test | A test of the acceptance repository that runs one scenario through the external interface only. It is evidence of done. |
| Unit test | A test of a code repository, written by the implementing agent, that knows the code. It serves the implementation and is not evidence of done. |
| Product build | What a code repository builds and the acceptance tests run against: a binary, a container image, or the URL of a running service. |
| Demo | A run of the scenarios of a unit that the requester watches, recorded with the commit of each code repository it ran on. |
| Acceptance architect | A Claude Code session of layer 3: it decides the acceptance areas, the acceptance units and the norms of each unit. |
| Implementation planner | A Claude Code session of layer 3: it decides the increments and the order in which the acceptance units are implemented (ACU-39, ACU-44). |
| Test agent | A Claude Code session of layer 3: it writes the acceptance tests. |
| Norms reviewer | A Claude Code session of layer 3, other than the acceptance architect: it selects the norms of a unit without seeing its `## Norms`, when the done profile of the unit asks for it (ACU-15). |
| Implementing agent | A Claude Code session of layer 4: it writes the code. |
| Model family | The models of one provider, such as those of Anthropic or those of OpenAI. |
| Reference commit | For each code repository, the head of its default branch. |
| Release | A version of the product that reaches its users: a deployment to production for a service, a published version (a tag and its published package) for a library or a compiler. |
| Decision block | The comment in the code, just above what it decides, that records one AI decision (ACU-17). |
| Evidence | What shows that a condition of done holds: an acceptance test that passes, a demo, a citation in the code, a decision block, a validation, or an accepted deviation. |
| AI decision | A significant choice that the implementing agent made where the norms leave it free (ACU-17). |
| Deviation | A point where a unit does not meet what was asked and is accepted that way (ACU-18). |
| Done profile | A named level of rigour: `prototype`, `product` or `critical` (ACU-19). |
| State | Where a unit is on the ladder of done: `pending`, `verified`, `validated` or `in use` (ACU-23). |
| Stale | Said of evidence that no longer holds, because what it was produced for changed (ACU-26). |

## The acceptance area and the acceptance unit

- **ACU-1.** An acceptance unit has a criterion of its own: the requester can judge it alone, without waiting for another unit. A work item is not an acceptance unit.

  Examples (illustrative): "the user exports the invoices to CSV" is an
  acceptance unit; "write the CSV writer" is a work item. In a compiler, "a
  program that multiplies two integers prints their product" is an acceptance
  unit; "write the lexer" is a work item.

- **ACU-2.** The acceptance architect analyses every norm of layer 2 against every area and every unit of the acceptance repository, and proposes the changes of the tree: to add, change or delete an area or a unit. A new spec does not need a new unit. The acceptance architect also decides which norms each unit groups, so that the unit can be implemented. It is not bound to put every norm in a unit: a norm that no unit groups is left out (ACU-32). The requester approves each change as [LAY-9](../../development-methodology/specs/layers.md#rules) says. The acceptance architect reads only layer 2 and the acceptance repository ([LAY-8](../../development-methodology/specs/layers.md#rules)).
- **ACU-3.** The acceptance areas and the acceptance units form a tree of two levels: the product, its areas, and the units of each area. Each unit belongs to exactly one area. What an area covers is the union of the norms that its units group. Deliberate design: an area holds no other area.

  Examples (illustrative):

  | Product | Acceptance area | Its acceptance units |
  |---|---|---|
  | A business app | Billing | Issue an invoice; cancel an invoice; export the invoices to CSV |
  | A compiler | Arithmetic expressions | Add two integers; multiply two integers; operator precedence |
  | A game | The 3D world | Terrain; weather; day and night cycle |

- **ACU-4.** An acceptance area or an acceptance unit decides only how the norms are delivered and accepted, never what the product does. What it may decide (complete list):
  - which norms each unit groups;
  - the boundary of each unit, in its non-goals;
  - the area of each unit;
  - its done profile.

  Which units each increment holds is decided by the implementation planner (ACU-44).

  A scenario whose action through the external interface or whose expected result no norm states is a gap of layer 1. The acceptance architect then opens an issue in the repository of layer 1, as [LAY-5](../../development-methodology/specs/layers.md#rules) says, and leaves the scenario out of the change that the requester approves; it adds the scenario in a later change, once layer 2 holds a norm for it.

  Rationale: layer 1 is the only source of truth ([LAY-2](../../development-methodology/specs/layers.md#rules)). A scenario that
  invents a command or a result would make layer 3 a second source.

- **ACU-5.** A unit, an area or a scenario keeps its ID forever; its title, or the name of the scenario, may change. An ID is never given again, even after its unit, area or scenario is removed (ACU-55).
- **ACU-50.** Each scenario, of a unit or of an area, has exactly one tag of the form `@SC-<n>` on its tag lines (ACU-54), where `<n>` is a number without leading zeros: `SC-<n>` is its scenario ID. No two scenarios of the acceptance repository have the same scenario ID. A scenario keeps its scenario ID when its text changes, and when it moves to another unit or area.
- **ACU-55.** The next area ID, unit ID and scenario ID are `AA-`, `AU-` and `SC-` followed by `last_area_id`, `last_unit_id` and `last_scenario_id` of `acceptance.json` (ACU-6), each plus 1. The change that gives an ID sets the field of its kind to the number of that ID, in the same commit. A field never decreases, and is never lower than the number of an ID of its kind in the acceptance repository.

  Example (illustrative): with `last_unit_id` 3, a change that adds two units gives them `AU-4` and `AU-5`, and sets `last_unit_id` to 5; a later change that removes `AU-5` leaves it at 5, and the next unit is `AU-6`.

  Rationale: a removed area, unit or scenario leaves no file behind, so only a
  number that only grows can tell which IDs were already given.

## The files of the acceptance repository

- **ACU-6.** The acceptance repository holds these files and folders (complete list):
  - `README.md`, `CLAUDE.md`, `.claude/settings.json` and `project.json`, which every repository of the project holds, written when the project is created ([ORC-5](../../project-management/use-cases/create-project/specs/create-project.md#create-a-project));
  - `.github/workflows/acceptance.yml`: the continuous integration of ACU-34, written when the project is created ([CRP-1](../../project-management/use-cases/create-project/specs/create-project.md#create-a-project));
  - `acceptance.json`: one object with these fields (complete list):
    - `default_profile`: a done profile, a string;
    - `last_area_id`, `last_unit_id` and `last_scenario_id`: each an integer, 0 or greater, the number of the latest area ID, unit ID or scenario ID given in the project (ACU-55);
    - `test_command`: a string, a shell command (ACU-34):
      - it runs with the root of the acceptance repository as its working directory;
      - it runs the acceptance tests of one folder: the folder whose path, relative to the root of the acceptance repository, is the value of the environment variable `ACCEPTANCE_TARGET`. Example (illustrative): `tests/AU-3`;
      - it may write a JUnit XML report of the tests it ran at the path that is the value of the environment variable `ACCEPTANCE_REPORT`;
    - `product`: an object with one entry per code repository whose product build the acceptance tests need. The key is `<owner>/<name>` of that code repository in `project.json`, and the value an object with these fields (complete list; `published` only when it applies):
      - `build`: a string, the shell command that, at the root of the code repository, builds its product build and prints as the last line of its standard output the value that the acceptance tests use; for a service that is already running, `echo <URL>`. Example (illustrative): the path of a binary, or the URL of a running service;
      - `env`: a string of `A`-`Z`, `0`-`9` and `_` that does not start with a digit, the name of the environment variable that gives that value to the acceptance tests (ACU-11);
      - `published`: a string, the shell command that, in an empty folder outside every repository of the project, obtains the latest published product build of the code repository, without cloning or fetching the code repository, and prints as the last line of its standard output the value that the acceptance tests use; absent when the code repository publishes no product build (ACU-49 says who runs it). Example (illustrative): a command that downloads a released binary, pulls a container image or prints the URL of a deployed service.

    `last_area_id`, `last_unit_id` and `last_scenario_id` are 0 until the first area, unit or scenario is given its ID; `test_command` is the empty string and `product` the empty object until there is code to test (ACU-43). The file is written when the project is created ([CRP-2](../../project-management/use-cases/create-project/specs/create-project.md#create-a-project)). This clause is the only place that defines the fields of `acceptance.json` and the variables `ACCEPTANCE_TARGET` and `ACCEPTANCE_REPORT`; the script of ACU-34 and [IMP-16](../../code-implementation/use-cases/implement/specs/implement.md#implement-a-task) cite it.

    Binding example; what binds is the keys, their nesting and the types of the values, not the names, the commands or the values:

    ```json
    {"default_profile": "product",
     "last_area_id": 1, "last_unit_id": 3, "last_scenario_id": 9,
     "test_command": "pytest \"$ACCEPTANCE_TARGET\" --junitxml \"$ACCEPTANCE_REPORT\"",
     "product": {"acme/billing-code-api": {"build": "make dist && echo \"$PWD/dist/app\"", "env": "PRODUCT_CMD"},
                 "acme/billing-code-web": {"build": "make serve-local", "env": "WEB_URL", "published": "echo https://staging.billing.example.com"}}}
    ```
  - `areas/<area ID>.md`: one file per acceptance area;
  - `units/<unit ID>.md`: one file per acceptance unit;
  - `tests/<area ID or unit ID>/`: the acceptance tests of that area or unit;
  - `records/<area ID or unit ID>.jsonl`: the record of the evidence of that area or unit (ACU-35);
  - `plan.json`: the increments, and the order in which their units are implemented (ACU-39), absent until the implementation planner first writes it.
- **ACU-43.** The acceptance architect fills `test_command` and `product` of `acceptance.json`, and changes them, and changes `default_profile` (ACU-20), in a change that the requester approves as [LAY-9](../../development-methodology/specs/layers.md#rules) says, with the values that the requester states. The acceptance architect does not read a code repository to find them (ACU-12); the requester may take them from what the implementing agent reports.
- **ACU-48.** The implementation planner adds an increment to `increments` of `plan.json` (ACU-39), at the position of its delivery order, in a change of `plan.json` that the requester approves as [LAY-9](../../development-methodology/specs/layers.md#rules) says. The acceptance architect never writes `plan.json`.
- **ACU-7.** The file of an acceptance area holds these parts, in this order (complete list):
  1. a heading of level 1: `<area ID> <title>`;
  2. `## Purpose`: what the area gives to the people who use it, in plain prose;
  3. `## Scenarios`: one `gherkin` code block with the scenarios that cross more than one unit of the area, or the line `None.` when no scenario crosses units. Each scenario has its tag `@SC-<n>` (ACU-50), one tag `@unit:<unit ID>` per unit it crosses, at least two, all of them units of the area, and one tag `@<norm ID>` per norm it checks, each of them in `## Norms` of a unit it crosses, and no other tag.

  Empty lines may stand before and after each part, and no other line stands between two parts.

  Binding example; what binds is the headings, their order, and the form of the tags, not the prose, the names or the values:

  ````markdown
  # AA-1 Billing

  ## Purpose

  The people of the company issue, cancel and export the invoices of their customers.

  ## Scenarios

  ```gherkin
  @SC-9 @unit:AU-1 @unit:AU-2 @unit:AU-3 @INV-15
  Scenario: A cancelled invoice is not exported
    Given a customer with one issued invoice
    When the user cancels the invoice
    And the user exports the invoices to CSV
    Then the CSV has no row for that invoice
  ```
  ````

  Example (illustrative), for a compiler:

  ````markdown
  # AA-2 Arithmetic expressions

  ## Purpose

  The programmers write arithmetic on integers, and the compiled program computes it.

  ## Scenarios

  ```gherkin
  @SC-30 @unit:AU-10 @unit:AU-11 @SEM-12
  Scenario: Multiplication binds tighter than addition
    Given a file "calc.src" that prints 2 + 3 * 4
    When the programmer runs "langc run calc.src"
    Then the output is "14"
  ```
  ````

- **ACU-8.** The file of an acceptance unit holds these parts, in this order (complete list):
  1. a heading of level 1: `<unit ID> <title>`;
  2. one or two lines, in this order: `Area: <area ID>`, and `Profile: <done profile>` only when the unit does not use `default_profile`;
  3. `## Narrative`: three lines, in this order: `In order to <benefit>`, `As a <role>` or `As an <role>`, `I want <what>`;
  4. `## Norms`: one list item per norm that the unit groups, at least one, each a citation of a norm (ACU-56). A norm may be grouped by several units;
  5. `## Scenarios`: one `gherkin` code block. Each scenario has its tag `@SC-<n>` (ACU-50), one tag `@<norm ID>` per norm it checks, each of them in `## Norms`, and no other tag. Each norm of `## Norms` is checked by at least one scenario;
  6. `## Non-goals`: one list item per thing the unit does not do, each its own sentence, or the line `None.`;
  7. `## Assumptions`: one list item per condition of the world that the unit takes as true and does not check, each its own sentence, each followed by the norm ID it rests on in parentheses, or by `(environment)` when it rests on no norm; or the line `None.`.

  Empty lines may stand before and after each part, and no other line stands between two parts. The lines of part 2 follow one another, and so do the three lines of part 3, with no empty line between them.

  Binding example; what binds is the headings, their order, the form of the line `Area:`, of each citation and of the tags, not the prose, the names or the values:

  ````markdown
  # AU-3 Export the invoices to CSV

  Area: AA-1

  ## Narrative

  In order to take my invoices to my accounting program
  As a user of the company
  I want to export my invoices to a CSV file

  ## Norms

  - INV-7@5a627175: one row per invoice
  - INV-12@0c1d2e3f: amounts with two decimals
  - INV-15@9e8d7c6b: cancelled invoices are not exported

  ## Scenarios

  ```gherkin
  @SC-5 @INV-7 @INV-12
  Scenario: Three invoices give three rows
    Given a user with 3 issued invoices
    When the user runs "app export --format csv"
    Then the CSV has 3 rows
    And every amount has two decimals

  @SC-6 @INV-15
  Scenario: A cancelled invoice gives no row
    Given a user with 2 issued invoices and 1 cancelled invoice
    When the user runs "app export --format csv"
    Then the CSV has 2 rows
  ```

  ## Non-goals

  - The unit does not export to PDF.
  - The unit does not export to Excel.

  ## Assumptions

  - The invoices are already in the database (environment).
  - The user may see every invoice of the company (USR-4).
  ````

  Example (illustrative), for a compiler:

  ````markdown
  # AU-11 Multiply two integers

  Area: AA-2

  ## Narrative

  In order to compute products in my programs
  As a programmer
  I want the compiled program to multiply two integers

  ## Norms

  - SYN-3@abcd1234: binary operators
  - SEM-8@11aa22bb: integer multiplication
  - SEM-9@33cc44dd: integer overflow is an error

  ## Scenarios

  ```gherkin
  @SC-21 @SYN-3 @SEM-8
  Scenario: Two integers give their product
    Given a file "mul.src" that prints 2 * 3
    When the programmer runs "langc run mul.src"
    Then the output is "6"

  @SC-22 @SEM-9
  Scenario: An overflow stops the program
    Given a file "big.src" that prints the largest integer * 2
    When the programmer runs "langc run big.src"
    Then the program stops with the error that SEM-9 names
  ```

  ## Non-goals

  - The unit does not multiply decimal numbers.
  - The unit does not fold constants at compile time.

  ## Assumptions

  - The programmer's file is UTF-8 (LEX-1).
  ````

  Rationale: the non-goals tell the implementing agent where to stop, and
  tell the requester that a missing export to PDF is a decision, not a
  mistake. An assumption that stops being true explains a failure that no
  change of the code caused.

- **ACU-9.** The increments are those of `increments` in `plan.json` (ACU-39), in the order in which they are delivered; no two of them have the same name. A unit is in at most one increment. A unit that no increment holds is not yet planned, and layer 4 does not implement it ([IMP-14](../../code-implementation/use-cases/implement/specs/implement.md#implement-a-task)). The file of a unit does not name its increment.

  Rationale: which units are delivered together, and when, is planning, not
  what a unit is; kept out of the file of the unit, a change of the plan
  changes no unit hash (ACU-52) and sends no evidence stale.

- **ACU-10.** The change that removes a unit also removes its folder `tests/<unit ID>/`; the change that moves a unit to another area keeps that folder, which is named by the unit ID. Either change also changes each scenario of an area that names the unit, so that every area still meets ACU-7. Neither change touches the record `records/<unit ID>.jsonl`: lines are only added to a record (ACU-35), and the unit ID is never given again (ACU-5), so the record of a removed unit stays as its history.

## Hashes and citations

- **ACU-51.** The fingerprint of a range of lines of a file is computed in these steps, in this order (complete list):
  1. the bytes of the file are decoded as UTF-8;
  2. each `\r\n` is replaced by `\n`;
  3. the text is split into lines at each `\n`, which belongs to no line;
  4. every space (U+0020) and tab (U+0009) at the end of each line is removed;
  5. the lines of the range are taken, as the clause that uses the fingerprint says;
  6. the empty lines at the end of the range are removed;
  7. the lines that are left are joined, each followed by one `\n`, and encoded as UTF-8;
  8. the fingerprint is the first 8 hex digits, in lower case, of the SHA-256 of those bytes.

  A fingerprint is never stored in the file it is computed from: a script computes it, never the model, in layer 3 and in layer 4 alike.

- **ACU-52.** The unit hash of a unit is the fingerprint (ACU-51) of the range of its file from the first line that is exactly `## Narrative` to the last line of the file. The heading and the lines `Area:` and `Profile:` are outside the range; everything else is inside: the narrative, the citations of `## Norms` with their norm hashes, the scenarios, the non-goals and the assumptions. A file with no line `## Narrative` has no unit hash.

  Binding example; what binds is the hash: the file of AU-3 that ACU-8 shows, without the two spaces that start each of its lines here, has the unit hash `efc7ae86`.

  A norm that changes in layer 2 does not change by itself the unit hash of a unit that groups it: the acceptance architect updates its citation in `## Norms`, which changes the unit hash (ACU-28); until then, the old norm hash already makes the evidence of the unit stale (ACU-26).

  Rationale: renaming a unit, moving it to another area or changing its
  profile does not change what must be built, so it must not send the code
  back to review; every other change of the file may.

- **ACU-53.** The area hash of an area is the fingerprint (ACU-51) of the range of its file from the first line that is exactly `## Purpose` to the last line of the file. The heading is outside the range. A file with no line `## Purpose` has no area hash.

  Binding example; what binds is the hash: the file of AA-1 that ACU-7 shows, read as in ACU-52, has the area hash `3b0900fb`.

- **ACU-54.** A `Scenario:` line is a line inside the `gherkin` block of `## Scenarios` of a unit or an area whose first characters that are not a space or a tab are exactly `Scenario:`. That block holds no line whose first characters that are not a space or a tab are one of these (complete list): `Feature:`, `Rule:`, `Background:`, `Example:`, `Scenario Outline:`, `Scenario Template:`, `Examples:`, `Scenarios:`. The tag lines of a scenario are the lines just above its `Scenario:` line whose first character that is not a space or a tab is `@`, with no other line between them and the `Scenario:` line. The text of a scenario is its tag lines, its `Scenario:` line, and every line after it up to the first tag line of the next scenario, the next `Scenario:` line or the closing fence of its `gherkin` block, whichever comes first, none of them included. Its name is what follows `Scenario:` on its `Scenario:` line, without the spaces and tabs at either end. The scenario hash of a scenario is the fingerprint (ACU-51) of the range of its file that is its text.

  Binding example; what binds is the hash: the scenario `SC-5` of that file of AU-3 (ACU-52) has the scenario hash `147d88d2`.

- **ACU-56.** A citation has one of these forms (complete list), each on one line:

  | Citation of | Form | Where |
  |---|---|---|
  | a norm | `<norm ID>@<norm hash>: <reason>` | a list item of `## Norms` of a unit (ACU-8) |
  | a unit, by the code | `<unit ID>@<unit hash>: <reason>` | after the comment mark of the language, in the code and the unit tests of layer 4 ([IMP-6](../../code-implementation/use-cases/implement/specs/implement.md#implement-a-task)) |
  | a unit or an area, by an acceptance test | `<unit ID>@<unit hash>: <title of the unit>` or `<area ID>@<area hash>: <title of the area>` | the first comment line of an acceptance test (ACU-11) |
  | a scenario | `SC-<n>@<scenario hash>: <name of the scenario>` | the second comment line of an acceptance test (ACU-11) |

  Each `<hash>` of a citation is 8 hex digits in lower case. A norm ID has the form of [R61](../../norms-management/specs/norms-versions.md#data-and-outputs): a prefix of three or more upper-case ASCII letters, alone or followed by `-` and a number from 1 without leading zeros, such as `INV` or `INV-7`. `<reason>` says in a few words what of the norm the unit needs, or what of the unit the code does or the test checks. The title of a unit or an area is what follows its ID and one space in its heading.

  The code and the unit tests of layer 4 cite units only, never a norm ID; a part of the code that serves two units carries one citation of each. The norms that the code implements are those of `## Norms` of the units it cites: the chain goes from the code to a unit and its unit hash, and from the unit to its norms and their norm hashes. Since `## Norms` is inside the unit hash (ACU-52), a citation whose unit hash is the unit hash of its unit names exactly the norms and norm hashes that the code was written for; one whose unit hash differs names code written for another version of the unit, which layer 4 reviews ([ORC-26](../../code-implementation/specs/module.md#implement-the-changed-norms)).

  Example (illustrative), in Python:

  ```python
  # AU-3@efc7ae86: one row per invoice, amounts with two decimals
  def write_row(out, invoice):
  ```

  Rationale: the unit is what the requester accepts; code that cites it is
  tied to what is accepted, and one hash says whether any of it changed. A
  norm cited by the code would say what the code does but not for which
  unit, nor whether that unit changed around it.

## Acceptance tests and independent evidence

- **ACU-11.** The test agent writes one acceptance test per scenario of a unit or an area, in `tests/<unit ID>/` or `tests/<area ID>/`, without reading layer 4. The test runs the scenario through the external interface of the product build only, which it gets from the environment variable that `product` names, and imports no code of a code repository. Each acceptance test opens with these comment lines, in this order (complete list), each a citation of ACU-56 after the comment mark of the language: the citation of its unit or its area, then the citation of its scenario, with the unit hash or area hash and the scenario hash of the commit of the acceptance repository that the test agent read. An acceptance test cites no norm: the tags `@<norm ID>` of its scenario tie it to the norms of `## Norms`.

  Example (illustrative), in Python:

  ```python
  # AU-3@efc7ae86: Export the invoices to CSV
  # SC-5@147d88d2: Three invoices give three rows
  def test_three_invoices_give_three_rows():
      create_user_with_invoices(3)
      csv = run("app export --format csv")
      assert len(csv.rows) == 3
  ```

  Example (illustrative), for a compiler, in Rust:

  ```rust
  // AU-11@a596f507: Multiply two integers
  // SC-21@f032b2a9: Two integers give their product
  #[test]
  fn two_integers_give_their_product() {
      let out = run("langc run tests/AU-11/mul.src");
      assert_eq!(out.stdout, "6");
  }
  ```

  Rationale: a test written without reading the code cannot copy what the
  code does; it can only say what the scenario asks. Through the external
  interface only, the test needs no code to be written, only the interface
  that the norms fix.

- **ACU-12.** The test agent never reads a code repository ([LAY-8](../../development-methodology/specs/layers.md#rules)). The implementing agent reads the acceptance repository and never writes it ([LAY-4](../../development-methodology/specs/layers.md#rules)). The implementing agent runs the acceptance tests with `test_command`, in a copy of the acceptance repository made outside it ([IMP-16](../../code-implementation/use-cases/implement/specs/implement.md#implement-a-task)), as often as it needs, and changes its code until they pass. It gives the tests the product builds as ACU-49 says. A run of the acceptance tests by the implementing agent, and a run in the continuous integration of a code repository, are feedback, not evidence (ACU-34). The implementing agent writes unit tests in layer 4, each citing the units it checks (ACU-56) as [IMP-6](../../code-implementation/use-cases/implement/specs/implement.md#implement-a-task) says; a unit test is never evidence of done. When the implementing agent holds an acceptance test to be wrong, it reports it to the requester and does not change it; the test agent fixes the test, or the requester sends the norm back to layer 1 ([LAY-5](../../development-methodology/specs/layers.md#rules)).

  Rationale: an agent that writes both the code and its tests shares its
  misreading of a norm between them, and every test passes. An agent that may
  change the tests that fail can turn any failure into a pass.

- **ACU-49.** The implementing agent of a code repository runs the acceptance tests of a task only when `test_command` is not the empty string and `product` (ACU-6) has an entry for its own code repository.
  - For each entry of `product`, whatever the components that the task names in `plan.json` (ACU-39), it gives the acceptance tests a value in the variable that the `env` of the entry names: for the entry of its own code repository, the last line that `build` prints when run at the root of its working tree; for the entry of another code repository, the last line that `published` prints, run without reading that code repository.
  - When an entry of another code repository has no `published`, it runs no acceptance test of the task, also when the task names only its own component.
  - Only the implementing agent of a code repository other than the one an entry names runs the `published` of that entry.
  - A run of the acceptance tests with a published build is feedback, not evidence (ACU-12, ACU-34).

  Rationale: an implementing agent that read another code repository to build
  it would cross the separation between code repositories; a published build
  is what any user of that component also gets. Every entry of `product` gets
  a value because `product` holds only the code repositories whose builds the
  acceptance tests need. A published build may not be the build at the
  reference commit, so a run with it cannot be evidence.

- **ACU-13.** The separation of ACU-12 is enforced at three levels (complete list); which of them a unit requires is fixed by its done profile (ACU-19):
  1. in each session, with this access (complete list): a session of layer 3 may neither read nor write a code repository; a session of layer 4 may read the acceptance repository and may not write it. Two means enforce it: rules `deny` of the Claude Code permissions, which create-project writes ([ORC-5](../../project-management/use-cases/create-project/specs/create-project.md#create-a-project)) and sync keeps in step with `project.json` ([SNC-1](../../project-management/use-cases/sync/specs/sync.md#sync-projectjson)); and a hook on the event `PreToolUse`, which the plugin of the role declares: this module in layer 3 (ACU-38), code-implementation in layer 4 ([CIM-1](../../code-implementation/specs/module.md#the-hook-of-the-session));
  2. in the environment: each role works where only the repositories it may read are cloned. Example (illustrative): a container, or a session in the cloud;
  3. on GitHub: the credentials of the implementing agent can read the acceptance repository and cannot push to it; the credentials of the test agent cannot clone or fetch the code repositories; and no code repository, and no workflow of one, holds a credential of the acceptance repository. The continuous integration of ACU-34 is the only holder of both a credential that can write the acceptance repository, its own workflow token, and one that can read the code repositories, `CODE_READ_TOKEN`, which can only read them; the code of layer 4 that it runs gets neither (ACU-34).

  Rationale: a Claude Code session runs as its user and reads every
  repository cloned on that machine, so level 1 guards against mistakes, not
  against a session that bypasses it. Level 3 stops a clone, a fetch and a
  push, but not a copy that is already on the machine; only level 2 makes
  the blindness of the test agent real.

- **ACU-38.** The plugin declares in its file `hooks/hooks.json` one hook on the event `PreToolUse`. It refuses every call of these tools whose fields name a code repository, or, for `Grep`, hold one, with the code repositories found and the paths resolved as ACU-45 says (complete list):

  | Tool | Fields it checks |
  |---|---|
  | `Read`, `Edit`, `Write` | `file_path` |
  | `NotebookEdit` | `notebook_path` |
  | `Grep` | `path`, also when it holds a code repository (ACU-45) |
  | `Glob` | `path`; and `pattern`, a shell pattern (ACU-45), made absolute against `path`, or against `cwd` when `path` is absent |
  | `Bash` | the text of `command`, and each of its words, as ACU-46 says |

  The hook refuses a call by printing on its standard output this JSON object and ending with status 0, where `<reason>` is the reason, word for word, as a JSON string:

  ```json
  {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "<reason>"}}
  ```

  The reason is `ACU-12 and [LAY-8](../../development-methodology/specs/layers.md#rules): a session of layer 3 never reads or writes a code repository of layer 4, and this call names <path>.`, where `<path>` is the real path of the code repository. When it refuses nothing, the hook prints nothing and ends with status 0.

  Deliberate design: the hook checks no tool outside the table, the tools of MCP servers included; the rules `deny` and levels 2 and 3 of ACU-13 cover them. Rationale: `Grep` searches the folders under `path`, so a `path` that holds a code repository reads it. A hook of the plugin works as soon as the plugin is enabled, with nothing to configure in the repository. A shell command can name a path in more ways than a hook recognises, so this hook guards against mistakes; levels 2 and 3 of ACU-13 are the barrier.
- **ACU-45.** Each time it runs, the hook of ACU-38 takes as the repository of the session the folder that the environment variable `CLAUDE_PROJECT_DIR` names, or else the field `cwd` of the input of the hook; finds the project folder from it as [ORC-21](../../project-management/specs/module.md#where-the-repositories-are) says; and takes as the path of each code repository the project folder followed by the `path` of an entry of layer 4 of the `project.json` of that repository, with its symbolic links followed. It resolves each path that a field names, `file_path`, `notebook_path` and `path` included, and each word of ACU-46, in this order: it replaces a leading `~` and the environment variables in it, makes it absolute against the field `cwd` when it is relative, and follows its symbolic links. A path names a code repository when the result is the path of that code repository or a path under it. A path that holds `*`, `?` or `[` is a shell pattern, whether a field names it, `pattern` of `Glob` included, or it is a word of ACU-46. Example (illustrative): `../billing-code-a*`. Its parts before the first part that holds one of those characters are resolved as above, and the rest is appended; it names a code repository when its first parts match the parts of the path of that code repository one by one, as the shell matches a pattern against a name, `*` also matching `/`. Example (illustrative): `**/*.py` against the project folder names every code repository. A path holds a code repository when the path of that code repository is under the result. Example (illustrative): the project folder holds every code repository.
- **ACU-46.** The words of the field `command` of a call of `Bash` are the tokens of a POSIX shell split of it, with quotes removed and `;`, `&`, `|`, `<`, `>` and parentheses as tokens of their own, together with the parts of each token around `=` and `:`. Example (illustrative): `../billing-code-api/bin/app` is a word of `PRODUCT=../billing-code-api/bin/app`. A call of `Bash` names a code repository when its text holds the path of the code repository, with its symbolic links followed, followed by the end of the text, a `/`, a blank or one of `'`, `"`, `;`, `|`, `&`, `<`, `>`, `(`, `)` and `` ` ``, or when one of its words names that code repository (ACU-45). A call of `Bash` also names a code repository when one of its words is a recursive reader and another of its words, not a shell pattern, holds that code repository (ACU-45). Example (illustrative): `..` in `grep -r invoice ..` run from the acceptance repository. The recursive readers are (complete list): `rg`, `ag`, `fd`, `find`, `tree`; and `grep`, `egrep` and `fgrep` when another word is `--recursive` or `--dereference-recursive`, or begins with exactly one `-` and holds `r` or `R`.
- **ACU-40.** The hook of ACU-38 refuses nothing when it cannot find the paths of the code repositories, which happens in these cases (complete list): the repository of the session is not a git repository; it has no `project.json`; its `project.json` is not valid JSON, or holds no list `repositories`; it has no remote `origin`, or not exactly one entry matches its remote `origin`; the `path` of that entry is not valid ([ORC-20](../../project-management/specs/module.md#where-the-repositories-are)); the folder of the repository does not end with that `path`. It also refuses nothing when its input is not a JSON object, and when it fails in any other way. Rationale: a hook that refused every call in a repository it cannot read would stop a session that is not of a project.
- **ACU-14.** When the done profile of a unit requires it (ACU-19), the test agent that writes its acceptance tests and the implementing agent of every commit of layer 4 that changes code citing the unit run on models of different families. Rationale: two agents on the same model tend to misread the same sentence in the same way, and their tests and code then agree on the same mistake.

- **ACU-34.** The only run of the acceptance tests that is evidence is the run of the continuous integration of the acceptance repository. That continuous integration runs on each of these events (complete list): the times of the schedule that its workflow fixes ([CRP-1](../../project-management/use-cases/create-project/specs/create-project.md#create-a-project)); a push to the default branch of the acceptance repository that changes a file outside `records/`. Each run tests the head of the default branch of the acceptance repository when the run starts; that commit is the `acceptance_commit` of its lines (ACU-35). Each run takes these steps, in this order (complete list):
  1. When `acceptance.json` is not one JSON object with the fields of ACU-6, each of its type, or the commit that the run tests cannot be read, the run fails and adds no line to `records/`. When `test_command` is the empty string, the run ends successfully and adds no line to `records/`.
  2. When `product` names a repository that is not of layer 4 in `project.json`, or holds an entry whose fields are not those of ACU-6, the run fails and adds no line to `records/`. Otherwise it reads the reference commit of each code repository of `project.json`. When the reference commit of a code repository cannot be read, the run fails, names that repository and adds no line to `records/`.
  3. It takes as the last recorded run the lines of kind `test`, across all files of `records/`, whose `date` is the latest `date` of any line of kind `test`. When those lines hold, in `reference_commits` (ACU-35), exactly the reference commits of step 2, and no file outside `records/` differs between their `acceptance_commit` and the commit that the run tests, the run ends successfully and adds no line to `records/`. When `records/` holds no line of kind `test`, or that `acceptance_commit` cannot be read, the run goes on.
  4. It makes a copy of the code repository of each entry of `product` at its reference commit, all of them before it runs any `build`. Then, for each entry of `product`, it runs `build` at the root of that copy, and gives the last line of its standard output to the acceptance tests in the variable that `env` names. When the copy of a code repository cannot be made, or its build fails, prints nothing or prints an empty last line, the run fails and adds no line to `records/`: a test that cannot reach the product is evidence neither way.
  5. For each folder `tests/<unit ID or area ID>/`, in the order of the IDs, it runs `test_command` at the root of the acceptance repository, with `ACCEPTANCE_TARGET` set to the path of the folder and `ACCEPTANCE_REPORT` set to a path outside the acceptance repository. Example (illustrative): `tests/AU-3` is the path of the folder of AU-3. When the command wrote there a JUnit XML report that holds at least one test case, each test case is one result: `fail` when it holds a failure or an error, `skipped` when it is skipped, and `pass` otherwise. Otherwise the folder is one result, `pass` when the command ends with status 0 and `fail` otherwise.
  6. It adds to `records/<unit ID or area ID>.jsonl` one line of kind `test` per result (ACU-35), all with the same `date`, commits `records/` and pushes it to the default branch.

  Runs do not overlap: a run that starts while another runs waits until it ends, and of the runs that wait only the latest runs. When the push of step 6 is rejected because the default branch moved, the run rebases its commit onto the default branch and pushes again, at most 3 times; then it fails, and the lines it recorded are lost, so the next run does not take the shortcut of step 3.

  The continuous integration reads the code repositories with `CODE_READ_TOKEN` (level 3 of ACU-13), and no session of layer 3 holds it ([LAY-8](../../development-methodology/specs/layers.md#rules)). The run reads the token from a file and deletes the file before step 2. From then on it keeps the token only in its own memory, never in its environment, and passes it only on the command line of the git commands of steps 2 and 4, each of which ends before any `build` runs; once step 4 has made its copies, it forgets the token, before any `build` runs. Rationale: a `build` or `test_command` runs as the same user as the run, so it could read the environment of the run and of every process that the run starts while it lives. The workflow of the acceptance repository is written by create-project ([CRP-1](../../project-management/use-cases/create-project/specs/create-project.md#create-a-project)).

  Rationale: the implementing agent needs to run the tests as often as it
  likes, but a run it controls cannot be evidence; the run that counts happens
  where the implementing agent cannot write. The acceptance repository asks
  the code repositories for their reference commits instead of being told,
  because a code repository that could notify it would hold a credential that
  can also write it; step 3 keeps a run of the schedule cheap when nothing
  changed.

## The review of the norms selected

- **ACU-15.** When the done profile of a unit requires it (ACU-19), before the requester approves a change to the narrative, the scenarios or `## Norms` of the unit, the norms reviewer selects the norms that the unit needs from its narrative and its scenarios only, without seeing `## Norms`. A script compares the two lists, and each norm that is in one list only is shown to the requester, who decides whether the unit groups it.

  Rationale: "every norm holds" is true and misleading when the unit
  groups fewer norms than it needs, and no test catches it, since no test is
  written for a norm that was not selected. A second agent that sees the first
  list tends to accept it.

## When a unit is done

- **ACU-16.** A unit is done when these five conditions hold together (complete list); what each requires is fixed by the unit's done profile (ACU-19):
  1. **Norms:** each norm of `## Norms` is implemented and checked;
  2. **End to end:** the scenarios of the unit work through the external interface;
  3. **Validation:** the requester saw the unit work and accepted it;
  4. **AI decisions:** each AI decision of the unit is recorded as a decision block;
  5. **Deviations:** each deviation of the unit is recorded and accepted.

  The unit is not done while one of them fails, even when the other four hold.

  Rationale: each condition covers a gap that the others leave open.
  Norms that hold one by one do not prove that the whole works (condition 2);
  tests that pass do not prove that the unit is what the requester wanted
  (condition 3); a unit that works can still hide choices that nobody asked
  for (conditions 4 and 5).

- **ACU-17.** An AI decision is a choice of the implementing agent where the norms leave it free, and which meets at least one of these criteria (complete list):
  1. **Dependency:** it adds or changes an outside library, service or tool;
  2. **Stored shape:** it fixes the shape in which data is stored or exchanged outside the running process. Examples (illustrative): a schema, a file format, a key;
  3. **Trade-off of quality:** it gives up some of one quality of the product to gain another, where the norms set neither. Examples (illustrative): memory over speed, cost over consistency;
  4. **Binding:** a later unit that touches the same code will have to follow it or undo it. Examples (illustrative): an architecture, a model of concurrency, the technique of a parser.

  A choice that meets none of them is not recorded. Example (illustrative): the name of an internal variable. A choice about the external interface that no norm makes is not an AI decision: it is a gap of layer 1, and the implementing agent opens an issue as [LAY-5](../../development-methodology/specs/layers.md#rules) says instead of choosing.

  The implementing agent records each AI decision once, as a decision block in the code, just above the smallest part of the code that holds what it decides, as [IMP-7](../../code-implementation/use-cases/implement/specs/implement.md#implement-a-task) places a citation. A decision block holds these lines, in this order, each after the comment mark of the language (complete list; the last two only when they apply):
  - `DECISION <slug>`, where `<slug>` is 3 to 40 characters among `a`-`z`, `0`-`9` and `-`, unique in the code repository;
  - `chose: <what was chosen, in plain words>`;
  - `instead of: <each alternative, separated by "; ">`;
  - `why: <the reason>`;
  - `for you: <what it means for the requester that is not seen from outside, such as cost, memory, a dependency on a provider, or how hard it is to undo>`;
  - `invalidated if: <each condition under which the decision no longer fits, separated by "; ">`;
  - `supersedes: <slug>`, when it replaces an earlier decision;
  - `scope: project`, when it holds for the whole code repository and not for one part of it.

  The units of a decision are those that the code under the block cites (ACU-56). A decision with `scope: project` is a decision of every unit that the code repository cites.

  Example (illustrative), in Python:

  ```python
  # DECISION export-streaming
  #   chose: write the CSV row by row while reading the invoices
  #   instead of: build the whole file in memory and write it at the end
  #   why: a company may have 100 000 invoices
  #   for you: memory does not grow with the number of invoices; going back costs little
  #   invalidated if: all rows must be sorted or totalled before the first one is written
  # AU-3@efc7ae86: one row per invoice, read and written one at a time
  def export_invoices(company_id, out):
  ```

  Example (illustrative), for a compiler, in Rust:

  ```rust
  // DECISION pratt-parser
  //   chose: a hand-written Pratt parser for expressions
  //   instead of: a parser generated from the grammar
  //   why: it reports a syntax error at the failing token, as ERR-2 asks
  //   for you: a new operator costs one hand-written rule; a generated parser would replace one module only
  //   invalidated if: the grammar gains rules that are not precedence or associativity
  // AU-10@4e5f6a7b: parse additions
  // AU-11@a596f507: parse multiplications
  fn parse_expr(&mut self, min_bp: u8) -> Result<Expr, SyntaxError> {
  ```

  The separator of a CSV, or the text of an error message, is never a decision block: it is seen from outside, so a norm must fix it.

  Rationale: the code is the only place that cannot drift from the code. A
  separate list of decisions would say one thing while the code does another.

- **ACU-33.** The implementing agent writes the decision blocks while it writes the code; no person approves or rejects them. A script computes the inventory of the decision blocks of each unit from the code; the inventory is not stored. Only the count of the decision blocks of each unit reaches layer 3; never a slug or the text of a block ([LAY-8](../../development-methodology/specs/layers.md#rules)).

  Rationale: the code is written by the AI, so the choices about how it is
  built are the AI's; the requester decides what the product does, in layer 1,
  and accepts it in the validation.

- **ACU-18.** A deviation is recorded with what is not met, why it is accepted, who accepted it, and until when: a date, or an event that the requester records when it happens.

  Example (illustrative): "The export of 10 000 invoices takes 8 seconds
  instead of the 5 that PRF-2 asks. Why: the database is slow. Accepted by the
  requester until the event 'database migrated'."

  Example (illustrative), for a compiler: "Compiling the corpus of 10 000
  lines takes 3 seconds instead of the 2 that PRF-1 asks. Why: the optimizer
  is not written yet. Accepted by the requester until 2027-06-30."

  Rationale: no real unit is perfect. What matters is that each imperfection
  is seen and has an owner, not hidden, and not "fixed" by rewriting the unit
  to match what was built.

## Done profiles

- **ACU-19.** Each done profile fixes what each condition of ACU-16 requires, and which of the other rules of this spec apply. This table is the only place that says it (complete list):

  | | `prototype` | `product` | `critical` |
  |---|---|---|---|
  | 1. Norms | The unit is cited by the code of layer 4 with its current unit hash (ACU-56) | As `prototype`, and each norm of `## Norms` is tagged by a scenario of the unit whose acceptance test passes | As `product` |
  | 2. End to end | A demo of each scenario of the unit | Each acceptance test of the unit passes on the reference commits | As `product` |
  | 3. Validation | By the requester | By the requester | By the requester, and by a second person, named by the requester, who knows the domain of the unit's risk (example, illustrative: security or law) |
  | 4. AI decisions | Each AI decision is recorded as a decision block | As `prototype` | As `prototype` |
  | 5. Deviations | Recorded, and accepted by the requester | Recorded, and accepted by the requester | Recorded, and accepted by the requester and by the second person |
  | Acceptance tests (ACU-11) | Not required | Required | Required |
  | Review of the norms (ACU-15) | Not required | Required | Required |
  | Levels of separation (ACU-13) | 1 and 3 | 1, 2 and 3 | 1, 2 and 3 |
  | Different model families (ACU-14) | Not required | Not required | Required |
  | `in use` after | Not reached | 30 days after the first release that holds the reference commits it was validated on, with no open failure (ACU-36) | 90 days, as `product` |

  Deliberate design: three profiles, not one per dimension of done.
  Rationale: no unit can meet every dimension of done; a profile says in
  advance what is asked and what is not, so that nobody assumes another level
  and no agent falls back to the cheapest one.

- **ACU-20.** The project declares its default profile in `acceptance.json`. A unit may declare another profile in its line `Profile:`. The acceptance architect may propose a profile, and the requester approves it as [LAY-9](../../development-methodology/specs/layers.md#rules) says. Rationale: choosing the rigour is choosing how much risk is accepted, which is the requester's decision, not the agent's.
- **ACU-21.** A unit that leaves out something its profile requires records it as a deviation (ACU-18). Example (illustrative): "No load test: three people use it."
- **ACU-22.** A scenario of an area follows the strictest profile among the units it crosses, in the order `prototype`, `product`, `critical`.

## The ladder of states

- **ACU-23.** The state of a unit is computed from its evidence that is not stale; it is not stored. The states are (complete list):
  - `pending`: the unit is not `verified`;
  - `verified`: conditions 1 and 2 of ACU-16 hold, as its profile requires;
  - `validated`: the unit is `verified`, and conditions 3, 4 and 5 hold;
  - `in use`: the unit is `validated`, and its profile's time since a release has passed with no open failure (ACU-36).

  Example (illustrative), for a unit with the profile `product`:

  | Step | Event | State after it |
  |---|---|---|
  | 1 | The requester approves AU-3; its acceptance tests fail, since no code exists | `pending` |
  | 2 | The code exists and every acceptance test passes on the reference commits | `verified` |
  | 3 | The requester sees the export work and accepts it | `validated` |
  | 4 | 30 days after the release that holds the code, with no open failure | `in use` |
  | 5 | The norm INV-12 changes in layer 2 | `pending` |
  | 6 | The acceptance architect updates the citation of INV-12, which changes the unit hash of AU-3; the requester approves the change; the test agent updates the tests and the implementing agent the code, each citing the new unit hash; the tests pass, and the requester validates again | `validated` |

- **ACU-24.** A validation holds across changes of the code while the unit stays `verified`. Deliberate design. Rationale: the acceptance tests guard what the requester saw; asking the requester to validate again after every commit would make validation a formality.
- **ACU-25.** Each state answers one question (complete list): `verified`, whether the unit meets the norms; `validated`, whether it is what the requester wanted; `in use`, whether it works in the real world. Rationale: verifying is almost free for an AI and can be wrong in the same way as the code; only the requester can validate.

## Done is a state, not an event

- **ACU-26.** Each evidence is recorded with what it was produced for, and is stale as soon as one of these happens (complete list):
  - for any evidence: a hash in `hashes` of its `for` is no longer the unit hash, area hash or scenario hash of its ID, or its unit, area or scenario is no longer in the acceptance repository; or a norm hash in `norm_hashes` of its `for` differs from the norm hash of that norm at the head of the default branch of the norms repository, or that norm is not a norm there (ACU-35);
  - for an acceptance test that passes: a file in `files` of its `for` changes, or a reference commit in `reference_commits` of its `for` changes (ACU-35);
  - for a citation in the code: the unit hash it cites is no longer the unit hash of its unit, or its unit is no longer in the acceptance repository;
  - for any evidence: its recorded date passes, or its recorded event is recorded as happened (ACU-18);
  - for every evidence of a unit, the citations in the code included: a norm that its `## Norms` cites is not a norm at the head of the default branch of the norms repository, or has there a norm hash other than the one cited;
  - for every evidence of a unit: an issue of ACU-36 about the unit is open.

  Deliberate design: a demo holds across changes of the code, as a validation does (ACU-24). Rationale: a demo that went stale with each commit of layer 4 would send a `prototype` unit back to `pending` after every commit, and ask the requester for more than `product` asks; in `prototype` no acceptance test guards the demo, which is the risk that the profile accepts (ACU-19).
- **ACU-27.** A script, not the model, says which evidence is stale and computes the state of each unit. When a norm of `## Norms` is no longer in layer 2, the script reports the citation as broken. Rationale: the same as [ORC-25](../../code-implementation/specs/module.md#implement-the-changed-norms): the result must be exact, and must not depend on a reading.
- **ACU-35.** The record of the evidence of a unit or an area is the file `records/<unit ID or area ID>.jsonl` of the acceptance repository: one JSON object per line, lines only added, never changed or removed. Every line holds these common fields (complete list), and each kind adds the fields listed below; a line of kind `validation` holds no other:
  - `kind`: the kind of evidence, one of `test`, `demo`, `validation`, `deviation` and `event`;
  - `for`: what it was produced for (ACU-26), an object with these fields (complete list): `hashes`, an object from each unit ID, area ID and scenario ID to its unit hash, area hash or scenario hash; `norm_hashes`, an object from each norm ID to its norm hash; `files`, an object from the path of each file, relative to the root of the acceptance repository, to its git blob hash, empty for every kind but `test`; `reference_commits`, an object from the `<owner>/<name>` of each code repository to its reference commit, empty for the kinds `validation`, `deviation` and `event`;
  - `date`: when it was produced, in UTC, in exactly this form, with no fractional seconds: `YYYY-MM-DDTHH:MM:SS+00:00`. Example: `2026-10-27T09:30:00+00:00`;
  - `produced_by`: who produced it: the URL of the run of the continuous integration for `test`; for `validation` and `deviation`, the name of the person who validated or accepted it: the requester, or, under the profile `critical`, the second person of ACU-19, each in a line of their own; and the name of the requester for `demo` and `event`.

  Each kind adds these fields (complete list):
  - `test`: `test`, the name of the test, `<classname>::<name>` of its test case in the JUnit report, or the path of the folder when the folder is one result (ACU-34) (example, illustrative: `tests/AU-3`); `result`, one of `pass`, `fail` and `skipped`; `acceptance_commit`, the commit of the acceptance repository that the run tested. In `for`, `hashes` holds the ID of each citation of the files of the folder (ACU-11), with the hash it cites, and, for the folder of an area, each unit that a scenario of the area crosses, with its unit hash at `acceptance_commit`; an ID that the files cite with two different hashes maps to the empty string, which is no hash, so the line is stale (ACU-26). `norm_hashes` holds the norms of `## Norms` of the unit, or of each unit that a scenario of the area crosses, with the norm hash that `## Norms` cites at `acceptance_commit`, and the empty string for a norm that two of those units cite with two different norm hashes; `files` every file that `acceptance_commit` holds in the folder; and `reference_commits` the reference commit that step 2 of ACU-34 read for each code repository of `project.json`, not only for those of `product`.
    The run reads `hashes`, `norm_hashes` and `files` from the files of `acceptance_commit`, before it runs any `build`, and never from the working tree, which the code of layer 4 can change while it runs (level 3 of ACU-13) and which may hold files that git does not track. Example (illustrative): a `__pycache__` folder that a test run writes in `tests/AU-3/` is not in `files`;
  - `demo`: `scenario`, the name of the scenario it shows, as its `Scenario:` line in the `gherkin` block names it;
  - `deviation`: `what`, what is not met; `why`, why it is accepted; `until`, an object with one field, `date` (`YYYY-MM-DD`) or `event` (its name) (ACU-18);
  - `event`: `event`, the name of an event of a deviation, which the requester records as happened (ACU-26). Its `for` holds empty objects.

  For `validation` and `deviation`, `hashes` holds the unit and its unit hash, and `norm_hashes` the norms of `## Norms` of the unit. For a `demo` in the record of a unit, `hashes` holds the unit with its unit hash and its scenario with its scenario hash, and `norm_hashes` the norms of `## Norms` of the unit. For a `demo` in the record of an area, `hashes` holds the area, its scenario and each unit that the scenario crosses, each with its hash, and `norm_hashes` the norm of each tag `@<norm ID>` of its scenario, with the norm hash that the `## Norms` of a unit it crosses cites. For a demo, `reference_commits` holds the commit of each code repository it ran on.

  Binding example of a line of kind `test`; what binds is the keys, their nesting and the types of the values, not the values:

  ```json
  {"kind": "test", "test": "tests.AU-3.test_export::test_three_invoices_give_three_rows", "result": "pass", "for": {"hashes": {"AU-3": "efc7ae86", "SC-5": "147d88d2", "SC-6": "a67eb609"}, "norm_hashes": {"INV-7": "5a627175", "INV-12": "0c1d2e3f", "INV-15": "9e8d7c6b"}, "files": {"tests/AU-3/test_export.py": "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"}, "reference_commits": {"acme/billing-code-api": "9fceb02d0ae598e95dc970b74767f19372d61af8"}}, "acceptance_commit": "1a410efbd13591db07496601ebc7a059dd55cfe9", "date": "2026-10-27T09:30:00+00:00", "produced_by": "https://github.com/acme/billing-acceptance/actions/runs/123"}
  ```

  The continuous integration of ACU-34 writes the lines of kind `test`; the acceptance architect writes the others with what the requester says, in a change that the requester approves as [LAY-9](../../development-methodology/specs/layers.md#rules) says. The decision blocks are not in this record: they are in the code of the code repositories (ACU-33).
- **ACU-36.** A failure of a released unit is an issue of the acceptance repository with the label `failure` that names the unit ID. The acceptance architect may propose which unit a failure belongs to; the requester confirms it. While such an issue is open, the evidence of the unit is stale (ACU-26), and the unit is `pending`.
- **ACU-28.** When a norm that a unit groups changes or leaves layer 2, the acceptance architect updates the unit and its scenarios, the citation of the norm in `## Norms` included, which changes its unit hash (ACU-52); the test agent updates its acceptance tests, the implementation planner updates the plan, and the requester approves the change as [LAY-9](../../development-methodology/specs/layers.md#rules) says; then the unit is verified and validated again, as its profile requires.
- **ACU-37.** In a run ([ORC-15](../../development-methodology/specs/flow.md#start-a-run)), the step of layer 3 starts from the commit of layer 2 of the run ([ORC-9](../../norms-management/specs/module.md#regenerate-the-norms)). The acceptance architect takes its part of the step with the use case define ([define.md](../use-cases/define/specs/define.md)): it analyses every norm of layer 2 against every area and every unit, and proposes the changes it finds, as ACU-2 says; for each new norm it may propose where it goes, and a norm that it groups in no unit is left out without a change (ACU-32). When a change adds, changes or removes a unit, the implementation planner proposes the new `plan.json` (ACU-44), and the test agent proposes the acceptance tests of each scenario that the change adds or changes (ACU-11), when the done profile of the unit requires them (ACU-19); for a norm that a unit groups and that changed or left layer 2, these are the changes of ACU-28. Then the run stops and waits until the requester approves or rejects each change, as [LAY-9](../../development-methodology/specs/layers.md#rules) says.
- **ACU-41.** The hand-off of the step of layer 3 is the head of the default branch of the acceptance repository once the requester has decided on every change of ACU-37, together with the commit of layer 2 of the run. A rejected change is never committed ([LAY-9](../../development-methodology/specs/layers.md#rules)), so that commit holds only the approved changes, and the files that a rejected change touched keep their content from before the run. When the step proposed no change, the hand-off is the head of the default branch before the run. Layer 4 reads the acceptance repository at that commit, and implements no unit whose `## Norms` cites a norm hash other than that of its norm in that commit of layer 2, or a norm that commit no longer holds.

  Rationale: a decision that belongs to a person is never taken in their
  place; the run goes on only once the person has decided, and only with
  what the person approved.

- **ACU-47.** When the requester rejects a change of ACU-37, the agent that proposed it revises it in a later change, or opens an issue in the repository of layer 1 when a norm is wrong ([LAY-5](../../development-methodology/specs/layers.md#rules)).

## The plan of implementation

- **ACU-39.** The implementation planner writes `plan.json`, which implement reads ([IMP-14](../../code-implementation/use-cases/implement/specs/implement.md#implement-a-task)): one object with one field, `increments`, a list with one object per increment, in the order in which the increments are delivered (ACU-9). Each increment holds these fields (complete list): `name`, its name; `units`, a list of its units in the order in which they are implemented. Each unit holds these fields (complete list): `unit`, its unit ID; `depends_on`, a list of the unit IDs it depends on; `components`, a list of groups, each a list of the components of layer 4 that implement the unit, as `component` names them in `project.json`, or the `name` of the code repository when the project has one code repository without `component`.

  Binding example, for a compiler; what binds is the keys, their nesting and the types of the values, not the IDs or the names:

  ```json
  {"increments": [
    {"name": "edition-1", "units": [
      {"unit": "AU-10", "depends_on": [], "components": [["compiler"]]},
      {"unit": "AU-11", "depends_on": ["AU-10"], "components": [["compiler"]]}]},
    {"name": "edition-2", "units": [
      {"unit": "AU-12", "depends_on": ["AU-10", "AU-11"], "components": [["compiler"], ["runtime", "ide"]]}]}]}
  ```

- **ACU-42.** In `plan.json`, a unit comes after every unit it depends on. Each group of `components` is implemented after the group before it; the components of one group may be implemented in parallel, each by the implementing agent of its own code repository; a component comes after every component whose build it needs. ACU-23 says when the unit becomes `verified`.
- **ACU-44.** The implementation planner decides only the plan: the increments, their names and their order, which units each increment holds, the order of the units inside each increment, and the groups of their components. It decides nothing of what a unit or an area is (ACU-4). The implementation planner writes the plan again whenever a unit is added, changed or removed, and the requester approves it as [LAY-9](../../development-methodology/specs/layers.md#rules) says.

  Rationale: what is delivered, and when, stays a decision of the requester,
  who approves the plan; the order in which it is built follows from the
  dependencies between units, and can be computed again without touching a
  unit, its unit hash or its evidence.

## When an area and an increment are done

- **ACU-29.** A scenario of an area belongs to the latest increment, in the order of `increments` of `plan.json`, among the units it crosses. While one of the units it crosses is in no increment, the scenario belongs to no increment.
- **ACU-30.** An area is done when each of its units is at least `validated`, and each scenario of the area has evidence that is not stale, as its profile requires (ACU-22): a demo for `prototype`, an acceptance test that passes for `product` and `critical`.
- **ACU-31.** An increment is done when these two conditions hold together (complete list):
  1. each unit of the increment is at least `validated`;
  2. each scenario of an area that belongs to the increment has evidence that is not stale, as ACU-30 says.

  A script computes it from the evidence, not a person and not the model. An increment that is done stops being done as soon as one of its units stops being `validated`.

  Rationale: whether a project is finished becomes a result that a program
  computes, not an opinion, and it always says the truth about the present.

- **ACU-32.** The script of ACU-27 also reports each norm of layer 2 that no unit groups. Such a norm does not stop an increment from being done. Deliberate design. Rationale: layer 2 also holds text that no unit can accept, such as tables of terms and rationales; the report shows the requester which norms are left out, and the requester decides.

## Open questions

1. How is the code under a decision block found in each language, so that the script of ACU-33 ties each block to its units?
