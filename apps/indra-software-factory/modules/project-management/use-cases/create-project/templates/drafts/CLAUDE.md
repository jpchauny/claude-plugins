# CLAUDE.md

## What this repository is

Layer 0 of `{{project}}`: the draft specs, not yet ready to be the source
of truth, because they are incomplete or not yet reviewed. Nothing is derived
from it, and no layer reads it
([LAY-1](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).

{{repositories}}

## Working here

- Keep each draft spec at the path it will have, as a spec, in layer 1.
- A draft spec is here, or it is a spec in layer 1, never both: promoting it adds it to layer 1 as a spec and removes it from here. It is moved, never copied.
- No change is made without a person's approval: the agent shows the whole diff, and the person approves the command that commits and pushes it to `main`. There is no pull request ([LAY-2](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).

## Issues

Pending items and findings go to the issue tree with `/utilities:issue`.
