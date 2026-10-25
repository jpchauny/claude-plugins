# Workflow orchestration

**Audience:** The people who run a project's flow from specs to code; whoever builds the skills of the plugin `workflow-orchestration`

**Scope:** Running the flow across the modules: what triggers a run, how each step runs in its repository, and what the orchestrator never does. The run itself, the order of its steps and their hand-offs, is methodology, in [flow.md](../../development-methodology/specs/flow.md)

The module `workflow-orchestration` of the app Indra Software Factory, listed in [app.md](../../../specs/app.md). The orchestrator runs the steps of a run as [ORC-15](../../development-methodology/specs/flow.md#start-a-run) says, and does not restate them.

## Terms

| Term | Meaning |
|---|---|
| Orchestrator | The skills of the plugin `workflow-orchestration`; the actor of every requirement that names no other. |

The terms run, step and hand-off are those of [flow.md](../../development-methodology/specs/flow.md#terms).

## Keep the layers apart

- **ORC-16.** The orchestrator must never write in the repository of layer 1, except to open the issues of [ORC-14](../../drift-management/specs/module.md#report-a-drift).
- **ORC-17.** The orchestrator must never edit a file of the repository of layer 2 or of a repository of layer 3 itself: every change there comes from the step of that layer.
- **ORC-18.** The step of code-implementation must never receive layer 1, neither its files nor its path.

## Open questions

1. Trigger: does a person start each run (`/workflow-orchestration:run`), or does a merge in the repository of layer 1 start it automatically (GitHub Actions)?
2. How a step runs in its repository: the orchestrator works across the repositories of a project, so a step that ran in the orchestrator's session would see all of them, and the module of each layer is enabled only in the repository of its layer ([APP-6](../../development-methodology/specs/layers.md#where-each-module-is-installed)). Candidate: each step is a headless session, `claude -p`, started with its repository as working directory, which sees only that repository.
