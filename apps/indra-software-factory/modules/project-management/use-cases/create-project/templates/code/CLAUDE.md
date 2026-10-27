# CLAUDE.md

## What this repository is

Layer 4 of `{{project}}`: code and its unit tests, built by agents from the
norms of layer 2, within the acceptance units of layer 3 that it implements
([LAY-4](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).

{{repositories}}

## Working here

- Implement only acceptance units of `{{owner}}/{{project}}-acceptance`, one at a time, in the order of its `plan.json`, with `/code-implementation:implement`: no work that is not a unit, no norm that the unit does not group, nothing that its non-goals exclude ([IMP-5, IMP-14 and IMP-15](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/code-implementation/use-cases/implement/specs/implement.md), [ACU-39](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#the-plan-of-implementation)).
- Never write code that is not in layer 2. Code and unit tests cite the norm IDs they implement or check, with their norm hash ([IMP-6](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/code-implementation/use-cases/implement/specs/implement.md)).
- Run the acceptance tests of the unit as feedback, with `test_command` and `product` of `acceptance.json`, in a copy of the acceptance repository made outside it, until they pass; that run is never evidence of done. When an acceptance test seems wrong, report it to the requester; never change it ([IMP-16](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/code-implementation/use-cases/implement/specs/implement.md), [ACU-12](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence)).
- Record each AI decision as a decision block (`DECISION <slug>`) just above the code it decides, while writing the code; nobody approves it ([IMP-17](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/code-implementation/use-cases/implement/specs/implement.md), [ACU-17 and ACU-33](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md)).
- Read `{{owner}}/{{project}}-norms` and `{{owner}}/{{project}}-acceptance`, never layer 1, and never write either of them; the plugin `code-implementation` refuses writes to the acceptance repository ([the hook of the session](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/code-implementation/specs/module.md#the-hook-of-the-session)) ([LAY-4](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).
- When a norm or a derived norm is wrong, missing or contradictory, do not work around it: open an issue in `{{owner}}/{{project}}-specs` ([LAY-5](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).
- The continuous integration of `{{owner}}/{{project}}-acceptance` reads the head of `main` of this repository every hour and runs its acceptance tests when it changed, the only run that is evidence. This repository holds no credential of the acceptance repository, and sends it nothing ([ACU-34](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence)).
- Open this repository alone in its VS Code window: a folder added to the same workspace becomes readable and writable from the session.

## Issues

Pending items and findings go to the issue tree with `/utilities:issue`.
