# acceptance-management

The module `acceptance-management` of Indra Software Factory, layer 3,
enabled in the repository of layer 3 only
([APP-6](../development-methodology/specs/layers.md#where-each-module-is-installed)):
the acceptance areas and the acceptance units of a project, their acceptance
tests, the plan of implementation, and when an acceptance unit, an acceptance
area and an increment are done. It is specified in [specs/](specs/module.md).

Four agents of layer 3 work from the norms of layer 2, without reading the
code ([LAY-8](../development-methodology/specs/layers.md#rules)), and a person
approves each change
([LAY-9](../development-methodology/specs/layers.md#rules)):

- the acceptance architect decides the acceptance areas, the acceptance units
  and the norms of each unit;
- the implementation planner writes `plan.json`: the increments, the units
  of each, and the order in which the units and their components are
  implemented;
- the test agent writes the acceptance tests;
- the norms reviewer selects the norms of a unit without seeing those that the
  acceptance architect chose, when the done profile of the unit asks for it
  (ACU-15).

## Hook

`hooks/hooks.json` declares one hook on the event `PreToolUse`
([ACU-38, ACU-45, ACU-46 and ACU-40](specs/module.md#acceptance-tests-and-independent-evidence)):
`scripts/deny_code_repositories.py` reads the paths of the code repositories
of layer 4 from `project.json`, and refuses every call of `Read`, `Edit`,
`Write`, `NotebookEdit`, `Grep`, `Glob` or `Bash` that names one of them. It guards against mistakes, not
against a session that bypasses it. Its tests run with:

    python3 -m unittest discover -s apps/indra-software-factory/modules/acceptance-management/tests

## Continuous integration

`scripts/acceptance_ci.py` is the script that the workflow
`.github/workflows/acceptance.yml` of the acceptance repository runs, which
`/project-management:create-project` writes: the only run of the acceptance
tests that is evidence
([ACU-34](specs/module.md#acceptance-tests-and-independent-evidence)). It
reads `acceptance.json` (ACU-6), builds the product of each code repository at
its reference commit, runs the tests, and adds their results to `records/`
([ACU-35](specs/module.md#done-is-a-state-not-an-event)). It runs only when a
reference commit or a file outside `records/` changed since the last recorded
run. It takes the read-only token of the code repositories in `--token-file`,
which it deletes at once, and refuses it in its environment, where a build
could read it. Its tests run with the command above.

## Use cases

- `/acceptance-management:define`
  ([define.md](use-cases/define/specs/define.md)): the acceptance architect
  analyses every norm of layer 2, at the head of the default branch of the
  norms repository, against every acceptance area and acceptance unit, and
  creates, changes and deletes acceptance areas and acceptance units with
  their scenarios, and fills `test_command` and `product` of
  `acceptance.json` while they are empty
  ([ACU-77](use-cases/define/specs/define.md#define-the-acceptance-areas-and-acceptance-units)),
  in changes that the requester approves. Its skill is
  [use-cases/define/SKILL.md](use-cases/define/SKILL.md); its script,
  `use-cases/define/define.py`, computes with no model the checks before the
  skill starts, the inventory of the norms, the acceptance areas and the
  acceptance units with their format
  errors, the checks and the proposal of the values of `acceptance.json`
  that the requester states, and the checks, the ID fields and the commit
  command of each change, with the code of `scripts/` that the use cases share (below). Its
  tests are `tests/test_define.py`, and run with the command above.
- `/acceptance-management:plan`
  ([plan.md](use-cases/plan/specs/plan.md)): the implementation planner
  reviews the whole plan of implementation against every acceptance unit and
  proposes the increments, their acceptance units, their order, their
  dependencies and their groups of components, changing as little of the
  current plan as it can; it commits only `plan.json`, after the requester's
  yes. Its skill is [use-cases/plan/SKILL.md](use-cases/plan/SKILL.md); its
  script, `use-cases/plan/plan.py`, computes with no model the checks before
  the skill starts, the inventory of the plan, the errors of a plan, the
  rendering of each draft and its changes of the plan, and writes and checks
  `plan.json` and builds its commit command. Its tests are
  `tests/test_plan.py`, and run with the command above.
- `/acceptance-management:write-acceptance-tests`
  ([write-acceptance-tests.md](use-cases/write-acceptance-tests/specs/write-acceptance-tests.md)):
  the test agent writes one acceptance test per scenario of each acceptance
  unit and acceptance area, from the scenario and the norms of its tags,
  without reading the code and without running any acceptance test, in
  changes that the requester approves. Its skill is
  [use-cases/write-acceptance-tests/SKILL.md](use-cases/write-acceptance-tests/SKILL.md);
  its script, `use-cases/write-acceptance-tests/write_acceptance_tests.py`,
  computes with no model the checks before the skill starts, the inventory of
  the acceptance tests (the opening, the status and the errors of each), the
  summary and the proposal of the acceptance tests, deletes the folders of
  acceptance tests that belong to no acceptance unit or acceptance area,
  checks the files written and builds the commit command of each change, and
  puts files back. It reads the format errors and the citation statuses from
  the inventory of define, in `scripts/acceptance_repository_files.py`. Its
  tests are `tests/test_write_acceptance_tests.py`, and run with the command
  above.

The code that the three use cases share is in `scripts/`, and no script of a
use case imports the script of another:

- `scripts/acceptance_repository_checks.py`: the checks that the three use
  cases make before they read anything else
  ([ACU-74](specs/module.md#the-files-of-the-acceptance-repository)), the
  checks before a commit of
  [ACU-75](specs/module.md#the-files-of-the-acceptance-repository), the
  command that makes them again, stages, commits and pushes, the diff of
  each file of a commit that the three use cases show, and the checks of the
  values of `test_command` and `product` of `acceptance.json`
  ([ACU-77](use-cases/define/specs/define.md#define-the-acceptance-areas-and-acceptance-units)),
  which define makes on the values that the requester states and
  write-acceptance-tests on those at `HEAD`.
- `scripts/acceptance_repository_files.py`: the reading of the files of the
  acceptance repository, the inventory of define (the norms, the acceptance
  areas and acceptance units with their format errors, the citation statuses
  and the ID fields) and a citation found in a line
  ([ACU-56](specs/module.md#hashes-and-citations)), which define and
  write-acceptance-tests read, and the
  forms of the paths of `areas/` and `units/`, which plan reads too.

## Not built yet

No script of this module computes yet which evidence is stale and the state
of each unit ([ACU-26 and ACU-27](specs/module.md#done-is-a-state-not-an-event),
[ACU-23](specs/module.md#the-ladder-of-states)), when an increment is done, or
the norms that no unit groups
([ACU-31 and ACU-32](specs/module.md#when-an-acceptance-area-and-an-increment-are-done)).
The continuous integration records what each line of `records/` is for
(ACU-35), but nothing reads it yet.
