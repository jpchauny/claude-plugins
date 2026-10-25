# Norms management

**Audience:** The people who run a project's flow from specs to code; whoever builds the skills of the plugin `norms-management`

**Scope:** Layer 2: the norms and every specification derived from them

The module `norms-management` of the app Indra Software Factory, listed in [app.md](../../../specs/app.md).

## Terms

| Term | Meaning |
|---|---|
| Run | One pass of the flow from specs to code, for one commit of layer 1. |
| Step | The work of one layer in one run, done in the repository of that layer. |
| Hand-off | What a step gives the next one: a commit, a report, or an issue. |

## Regenerate the norms

- **ORC-8.** In the repository of layer 2, the step runs `/norms-management:build` at the commit of layer 1 that starts the run ([ORC-15](../../workflow-orchestration/specs/module.md#start-a-run)), then `/norms-management:verify`. A failure of either ends the run, with the generator's message shown as it is ([LAY-3](../../../specs/layers.md#lay-3--layer-2-is-derived-from-layer-1-only-and-only-what-changed-is-regenerated)).
- **ORC-9.** Its hand-off is the commit of the repository of layer 2 that holds the regenerated `data/` and `specs-repo-annotated/`, and its `data/report.md`, which lists by norm ID what changed.
- **ORC-10.** When `data/report.md` shows no change of norm, the run ends after this step: there is nothing to implement.

## Open questions

1. Commit of layer 2: does the step commit and push `data/` and `specs-repo-annotated/` directly, or open a pull request for a person to approve?
