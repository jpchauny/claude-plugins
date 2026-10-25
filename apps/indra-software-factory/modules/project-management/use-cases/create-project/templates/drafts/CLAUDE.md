# CLAUDE.md

## What this repository is

Layer 0 of `{{project}}`: the specs not yet ready to be the source of
truth, because they are incomplete or not yet reviewed. Nothing is derived
from it, and no layer reads it
([LAY-1](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/specs/layers.md#lay-1--every-project-has-four-layers-each-in-its-own-repositories)).

{{repositories}}

## Working here

- Keep each spec at the path it will have in layer 1.
- A spec is here or in layer 1, never in both: promoting it adds it to layer 1 and removes it from here. It is moved, never copied.
- Every change reaches `main` by a pull request a person approves ([LAY-2](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/specs/layers.md#lay-2--people-work-in-layers-0-and-1)).

## Issues

Pending items and findings go to the issue tree with `/utilities:issue`.
