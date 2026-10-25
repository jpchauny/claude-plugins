# CLAUDE.md

## What this repository is

Layer 3 of `{{project}}`: code and tests, built by agents from layer 2
alone ([LAY-4](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).

{{repositories}}

## Working here

- Never write code that is not in layer 2. Code and tests cite the norm IDs they implement or check.
- When a norm or a derived norm is wrong, missing or contradictory, do not work around it: open an issue in `{{owner}}/{{project}}-specs` ([LAY-5](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).
- Open this repository alone in its VS Code window: a folder added to the same workspace becomes readable and writable from the session.

## Issues

Pending items and findings go to the issue tree with `/utilities:issue`.
