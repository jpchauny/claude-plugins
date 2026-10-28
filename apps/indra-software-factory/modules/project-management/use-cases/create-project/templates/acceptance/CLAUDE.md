# CLAUDE.md

## What this repository is

Layer 3 of `{{project}}`: its acceptance areas, acceptance units, their
acceptance tests, the plan of implementation and the record of the evidence,
written by agents from the norms of layer 2, each change approved by a person
([LAY-8 and LAY-9](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).
What each file holds is in
[acceptance-management](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md).

{{repositories}}

## Who works here

Four kinds of session work here, each in its own role
([ACU terms](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#terms)):

- **Acceptance architect**: with `/acceptance-management:define`, proposes the acceptance areas, the acceptance units, the norms that each unit groups, its scenarios and its non-goals, in `areas/` and `units/`; the requester approves them. Outside `/acceptance-management:define`, which never writes `records/`, it writes there the demos, validations and deviations that the requester states ([ACU-35](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#done-is-a-state-not-an-event)).
- **Implementation planner**: writes `plan.json`: the increments, their names and order, the units of each and their order, and the components of each unit; the requester approves it ([ACU-39 and ACU-44](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#the-plan-of-implementation)).
- **Norms reviewer**: when the done profile of a unit asks for it, selects the norms that the unit needs from its narrative and its scenarios only, without seeing its `## Norms`; a script compares the two lists and the requester decides each difference ([ACU-15](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#the-review-of-the-norms-selected)).
- **Test agent**: writes only the acceptance tests, in `tests/<unit or area ID>/`, one per scenario, through the external interface of the product only, blind to the code ([ACU-11 and ACU-12](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence)).

The default done profile and how the product builds are obtained are in
`acceptance.json` ([ACU-6](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#the-files-of-the-acceptance-repository)).
The lines of kind `test` in `records/` are written only by the continuous
integration, `.github/workflows/acceptance.yml`
([ACU-34](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence)); no session writes them.

## Working here

- Read only `{{owner}}/{{project}}-norms` and this repository: never layer 1, and never a repository of code; the plugin `acceptance-management` refuses any tool call that names one ([ACU-38](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence)) ([LAY-8](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).
- When a scenario needs an action or a result that no norm states, do not invent it: open an issue in `{{owner}}/{{project}}-specs` ([LAY-5](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).
- No change that a session makes is committed without a person's approval: the agent shows the whole diff, and the person approves the command that commits and pushes it to `main`. There is no pull request. Only three writes need no approval: the first commit, the lines of kind `test` that the CI adds to `records/`, and the `project.json` and rules deny that `/project-management:sync` writes ([LAY-9](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).
- Open this repository alone in its VS Code window: a folder added to the same workspace becomes readable and writable from the session.

## Issues

Pending items and findings go to the issue tree with `/utilities:issue`.
