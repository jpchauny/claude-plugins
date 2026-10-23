# CLAUDE.md

## What this repository is

Layer 2 of `{{project}}`: `{{owner}}/{{project}}-specs` annotated with stable
norm IDs, and every specification derived from it. It is derived from
layer 1 only, regenerated only where layer 1 changed, and never edited by hand
([LAY-3](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/specs/layers.md#lay-3--layer-2-is-derived-from-layer-1-only-and-only-what-changed-is-regenerated)).

| Layer | Repository |
|---|---|
| 1. Specs | `{{owner}}/{{project}}-specs`, the only source |
| 2. Norms | `{{owner}}/{{project}}-norms` (this one) |
| 3. Code | `{{owner}}/{{project}}-code`, built from this one |

## Working here

- The output of the norms generator (plugin `norms-management`) and of this project's own generators is never edited by hand.
- What is written by hand here is only this project's own generators, under `generators/`.

## Issues

Pending items and findings go to the issue tree with `/utilities:issue`.
