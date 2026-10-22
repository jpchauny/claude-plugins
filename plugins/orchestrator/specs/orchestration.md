# Orchestration

**Status:** Draft
**Audience:** The people who run a project's flow from specs to code; whoever builds the skills of the plugin `orchestrator`

**Scope:** How a change in layer 1 reaches layer 3: the steps from a commit of `<project>-specs` to a regenerated `<project>-norms` and to code in `<project>-code`, what each step hands to the next, and what the orchestrator never does

The orchestrator coordinates the three repositories of one project
([LAY-1](layers.md#lay-1--every-project-has-three-layers-in-three-repositories)).
It does not do the work of any layer: each step runs in the repository of its
layer, with the plugin of that layer, and the orchestrator only starts the
step, checks its result and passes the hand-off to the next one.

## Terms

| Term | Meaning |
|---|---|
| Orchestrator | The skills of the plugin `orchestrator` that run the flow; the actor of every requirement that names no other. |
| Run | One pass of the flow, for one commit of layer 1. |
| Step | The work of one layer in one run, done in the repository of that layer. |
| Hand-off | What a step gives the next one: a commit, a report, or an issue. |

## Flow

- **ORC-1.** A run starts from one commit of `<project>-specs` on its default branch, which a person approved by pull request ([LAY-2](layers.md#lay-2--people-work-in-layer-1)).
- **ORC-2.** Step 1, norms: in `<project>-norms`, the orchestrator runs `/norms:build` at the commit of ORC-1, then `/norms:verify`. A failure of either ends the run, with the generator's message shown as it is ([LAY-3](layers.md#lay-3--layer-2-is-regenerated-whole-from-layer-1-only)).
- **ORC-3.** Hand-off 1: the commit of `<project>-norms` that holds the regenerated `data/` and `specs-repo-annotated/`, and its `data/report.md`, which lists by norm ID what changed.
- **ORC-4.** When `data/report.md` shows no change of norm, the run ends after step 1: there is nothing to implement.
- **ORC-5.** Step 2, code: in `<project>-code`, the orchestrator starts the implementation from the commit of ORC-3 alone. The step implements every new or changed norm, removes what implements a retired norm, and cites in code and tests the norm IDs ([LAY-4](layers.md#lay-4--layer-3-reads-layer-2-never-layer-1)).
- **ORC-6.** Hand-off 2: the commit or pull request of `<project>-code` with the implementation, and the list of the norm IDs it covers.
- **ORC-7.** When step 2 finds the specification wrong, missing or contradictory, it opens an issue in `<project>-specs` and does not work around it. The run ends there for the affected norms; a new run starts from the commit of layer 1 that fixes it ([LAY-5](layers.md#lay-5--an-inconsistency-is-fixed-in-layer-1-first)).

## Prohibitions

- **ORC-8.** The orchestrator must never write in `<project>-specs`, except to open the issues of ORC-7.
- **ORC-9.** The orchestrator must never edit a file of `<project>-norms` or of `<project>-code` itself: every change there comes from the step of that layer.
- **ORC-10.** The step of layer 3 must never receive layer 1, neither its files nor its path.

## Open questions

These decisions are pending before the skills are built.

1. Trigger: does a person start each run (`/orchestrator:run`), or does a merge in `<project>-specs` start it automatically (GitHub Actions)?
2. How a step runs in its repository: the plugins of a layer are enabled by the `.claude/settings.json` of its repository, and a subagent of the orchestrator's session inherits that session's plugins, not those of the repository. Candidate: each step is a headless session, `claude -p`, started with the repository as working directory.
3. Commit of layer 2: does step 1 commit and push `data/` and `specs-repo-annotated/` directly, or open a pull request for a person to approve?
4. Layer 3: does step 2 open a pull request for a person to review, or push to the default branch?
5. Where the orchestrator finds the three repositories: sibling folders `<project>-specs`, `<project>-norms` and `<project>-code`, as `/norms:build` already assumes, or a configuration?
