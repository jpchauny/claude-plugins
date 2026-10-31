# CLAUDE.md

## What this repository is

The orchestration repository of `{{project}}`: no layer. From here a person
starts and controls a run across the layers, with the plugin
`workflow-orchestration`; each step runs in the repository of its layer
([LAY-11](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#the-orchestration-repository)).

{{repositories}}

## Working here

- Start a run with `/workflow-orchestration:run`. The orchestrator does the work of no layer, and writes in the repositories of the layers only the lines of kind `test` of its evidence runs ([ORC-16 and ORC-17](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/workflow-orchestration/specs/module.md#keep-the-layers-apart)).
- A run keeps nothing in this repository.
- Open this repository alone in its VS Code window: a folder added to the same workspace becomes readable and writable from the session.

## Issues

Pending items and findings go to the issue tree with `/utilities:issue`.
