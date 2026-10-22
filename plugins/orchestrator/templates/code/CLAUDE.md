# CLAUDE.md

## What this repository is

Layer 3 of `{{project}}`: its code and tests, built by agents from layer 2
alone ([LAY-4](https://github.com/jpchauny/claude-plugins/blob/main/plugins/orchestrator/specs/layers.md#lay-4--layer-3-reads-layer-2-never-layer-1)).

| Layer | Repository |
|---|---|
| 1. Specs | `{{owner}}/{{project}}-specs`: never read or written from here |
| 2. Norms | `{{owner}}/{{project}}-norms`: read only |
| 3. Code | `{{owner}}/{{project}}-code` (this one) |

## Working here

- Never write code that is not in layer 2. Code and tests cite the norm IDs they implement or check.
- When the specification is wrong, missing or contradictory, do not work around it: open an issue in `{{owner}}/{{project}}-specs` ([LAY-5](https://github.com/jpchauny/claude-plugins/blob/main/plugins/orchestrator/specs/layers.md#lay-5--an-inconsistency-is-fixed-in-layer-1-first)).
- Open this repository alone in its VS Code window: a folder added to the same workspace becomes readable and writable from the session.

## Issues

Pending items and findings go to the issue tree with `/shared:issue`.
