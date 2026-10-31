# CLAUDE.md

## What this repository is

Layer 2 of `{{project}}`: the norms, which are `{{owner}}/{{project}}-specs`
annotated with stable norm IDs, and the derived norms, each with its derived
norm ID (such as `grammar:12`) and its derived norm fingerprint, listed in
`specs-derived/<type>/derived-norms.jsonl`
([NRM-12](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/norms-management/specs/module.md#the-list-of-derived-norms)).
It is derived from
layer 1 only, regenerated only where layer 1 or a derived-norms generator
changed (a new version of a generator derives its type again, also when no norm
changed), and never edited by hand
([LAY-3](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).

{{repositories}}

## Working here

- The output of the norms generator (plugin `norms-management`) and of this project's own derived-norms generators is never edited by hand.
- Nothing here is written by hand: this repository holds the norms and the derived norms, never a generator, a plugin or a script ([LAY-13](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)). This project's own derived-norms generators are plugins of `{{owner}}/{{project}}-tooling`, enabled in `.claude/settings.json` as [LAY-14](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#the-tooling-repository) says.

## Issues

Pending items and findings go to the issue tree with `/utilities:issue`.
