# Flow

**Prefix:** FLW

**Audience:** The people who run a project's flow from specs to code, and the Claude Code sessions in the repositories of a project; whoever builds a module of the app

**Scope:** How the work goes from one layer to the next: what starts a run, the order of its steps and the hand-off between them. What each layer holds is in [layers.md](layers.md); how a step does its work is in the module of its layer; what triggers a run and runs its steps is the module [workflow-orchestration](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/workflow-orchestration/specs/module.md)

A spec of the module `development-methodology` of the app Indra Software Factory, listed in [app.md](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/specs/app.md); the module is specified in [module.md](module.md).

ORC-15 keeps the ID it had in the module `workflow-orchestration`, as a clause moved from it ([SST-11](https://github.com/jpchauny/claude-plugins/blob/main/specs/spec-structure.md#ids-of-clauses)).

## Terms

| Term | Meaning |
|---|---|
| Run | One pass of the flow from specs to code, for one commit of layer 1. |
| Step | The work of one layer in one run, done in the repository of that layer. |
| Hand-off | What a step gives the next one: a commit, a report, or an issue. |

## Start a run

- **ORC-15.** A run starts from one commit of the repository of layer 1 on its default branch, which a person approved ([LAY-2](layers.md#rules)). Its steps are, in this order: [norms-management](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/norms-management/specs/module.md) ([ORC-8](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/norms-management/specs/module.md#regenerate-the-norms)), then [code-implementation](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/code-implementation/specs/module.md) ([ORC-25](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/code-implementation/specs/module.md#implement-the-changed-norms)), each from the hand-off of the one before. Rationale: layer 1 is the only source of truth ([LAY-2](layers.md#rules)), so a run starts from it.
