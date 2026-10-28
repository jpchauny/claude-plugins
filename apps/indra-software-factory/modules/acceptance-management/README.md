# acceptance-management

The module `acceptance-management` of Indra Software Factory, layer 3,
enabled in the repository of layer 3 only
([APP-6](../development-methodology/specs/layers.md#where-each-module-is-installed)):
the acceptance areas and the acceptance units of a project, their acceptance
tests, the plan of implementation, and when a unit, an area and an increment
are done. It is specified in [specs/](specs/module.md).

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
  their scenarios, in changes that
  the requester approves. Its skill is
  [use-cases/define/SKILL.md](use-cases/define/SKILL.md); its script,
  `use-cases/define/define.py`, computes with no model the checks before the
  skill starts, the inventory of the norms, the acceptance areas and the
  acceptance units with their format
  errors, and the checks, the ID fields and the commit command of each
  change. Its tests are `tests/test_define.py`, and run with the command
  above.

## Not built yet

No script of this module computes yet which evidence is stale and the state
of each unit ([ACU-26 and ACU-27](specs/module.md#done-is-a-state-not-an-event),
[ACU-23](specs/module.md#the-ladder-of-states)), when an increment is done, or
the norms that no unit groups
([ACU-31 and ACU-32](specs/module.md#when-an-acceptance-area-and-an-increment-are-done)).
The continuous integration records what each line of `records/` is for
(ACU-35), but nothing reads it yet.
