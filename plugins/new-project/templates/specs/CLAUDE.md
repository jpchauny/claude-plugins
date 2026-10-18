# CLAUDE.md

## What this repository is

Layer 1 of `{{project}}`: its specification, in plain prose, written by
people. The only source of truth of the project
([LAY-2](https://github.com/jpchauny/claude-plugins/blob/main/spec-driven-design-process/layers.md#lay-2--people-work-in-layer-1)).

| Layer | Repository |
|---|---|
| 1. Specs | `{{owner}}/{{project}}-specs` (this one) |
| 2. Norms | `{{owner}}/{{project}}-norms`, regenerated from this one |
| 3. Code | `{{owner}}/{{project}}-code`, built from layer 2 |

## Working here

- The specs live under `specs/`. Every change reaches `main` by a pull request a person approves.
- Issues opened by layer 3 (inconsistencies found while implementing) are fixed here first ([LAY-5](https://github.com/jpchauny/claude-plugins/blob/main/spec-driven-design-process/layers.md#lay-5--an-inconsistency-is-fixed-in-layer-1-first)).

## Issues

Pending items and findings go to the issue tree with `/shared:issue`.
