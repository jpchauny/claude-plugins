# Workflow orchestration

**Audience:** The people who run a project's flow from specs to code; whoever builds the skills of the plugin `workflow-orchestration`

**Scope:** The flow across the modules: what starts a run, the order of the steps, the hand-offs, how each step runs in its repository, and what the orchestrator never does

The module `workflow-orchestration` of the app Indra Software Factory, listed in [app.md](../../../specs/app.md).

## Terms

| Term | Meaning |
|---|---|
| Orchestrator | The skills of the plugin `workflow-orchestration`; the actor of every requirement that names no other. |
| Run | One pass of the flow from specs to code, for one commit of layer 1. |
| Step | The work of one layer in one run, done in the repository of that layer. |
| Hand-off | What a step gives the next one: a commit, a report, or an issue. |

## Start a run

- **ORC-15.** A run starts from one commit of the repository of layer 1 on its default branch, which a person approved ([LAY-2](../../../specs/layers.md#lay-2--people-work-in-layers-0-and-1)). Its steps are, in this order: [norms-management](../../norms-management/specs/module.md) ([ORC-8](../../norms-management/specs/module.md#regenerate-the-norms)), then [code-implementation](../../code-implementation/specs/module.md) ([ORC-25](../../code-implementation/specs/module.md#implement-the-changed-norms)), each from the hand-off of the one before.

## Keep the layers apart

- **ORC-16.** The orchestrator must never write in the repository of layer 1, except to open the issues of [ORC-14](../../drift-management/specs/module.md#report-a-drift).
- **ORC-17.** The orchestrator must never edit a file of the repository of layer 2 or of a repository of layer 3 itself: every change there comes from the step of that layer.
- **ORC-18.** The step of code-implementation must never receive layer 1, neither its files nor its path.

## Open questions

1. Trigger: does a person start each run (`/workflow-orchestration:run`), or does a merge in the repository of layer 1 start it automatically (GitHub Actions)?
2. How a step runs in its repository: the orchestrator works across the repositories of a project, so a step that ran in the orchestrator's session would see all of them, and the module of each layer is enabled only in the repository of its layer ([APP-6](../../../specs/app.md#rules)). Candidate: each step is a headless session, `claude -p`, started with its repository as working directory, which sees only that repository.
