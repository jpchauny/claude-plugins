# Indra Software Factory

**Audience:** The people who use the app; whoever builds one of its modules

**Scope:** What the app is, how it is used, and its modules. The app is one of the marketplace, listed in [marketplace.md](../../../specs/marketplace.md); each module specifies its own use cases

Indra Software Factory is an app of Claude Code plugins for working in three
layers: specifications written by people, norms generated from them, code
built from the norms by agents. A person installs each module where APP-6
says, and then invokes its use cases.

Every module obeys the rules of the three layers, LAY-1 to LAY-6, in
[layers.md](layers.md): they are the foundation of the app, not a module.

## Terms

| Term | Meaning |
|---|---|
| App | Indra Software Factory: its modules, each one a plugin installed on its own. The app itself is no plugin. |
| Module | A set of use cases with one responsibility, built as one plugin of the same name. |
| Use case | One thing the user invokes, as `/<module>:<use case>`. |

## Modules

| Module | Responsibility | Specs |
|---|---|---|
| `project-management` | The three repositories of a project: their creation and their life cycle | [module.md](../modules/project-management/specs/module.md) |
| `specs-management` | Layer 1: the AI recommends how to improve the specs that the authors write | [module.md](../modules/specs-management/specs/module.md) |
| `norms-management` | Layer 2: the norms and every specification derived from them | [module.md](../modules/norms-management/specs/module.md) |
| `code-implementation` | Layer 3: code built from the norms, and its traceability to norm IDs | [module.md](../modules/code-implementation/specs/module.md) |
| `drift-management` | A drift between specs and code, sent back to layer 1 | [module.md](../modules/drift-management/specs/module.md) |
| `workflow-orchestration` | The flow across the modules: what starts a run, the order of the steps, the hand-offs, and how each step runs in its repository | [module.md](../modules/workflow-orchestration/specs/module.md) |
| `utilities` | Tools usable in any layer: exploring, the issue tree, explanations, a recap of the session | not yet specified |

## Rules

How the app is developed, a module as a plugin and a use case as a skill
of it, is in [development.md](../../../specs/development.md).

- **APP-5.** Each module is a plugin of its own. No module depends on another, and no plugin installs them together.
- **APP-6.** Where each module is installed (complete list):

  | Module | Where |
  |---|---|
  | `project-management` | At user scope, once per person: its use case `create-project` runs before the repositories of a project exist. |
  | `specs-management` | Enabled in the `.claude/settings.json` of `<project>-specs` only. |
  | `norms-management` | Enabled in the `.claude/settings.json` of `<project>-norms` only. |
  | `code-implementation` | Enabled in the `.claude/settings.json` of `<project>-code` only. |
  | `utilities` | Enabled in the `.claude/settings.json` of each of the three repositories. |
  | `workflow-orchestration`, `drift-management` | Not yet decided: open question 1. |

- **APP-7.** A use case of one layer is not installed outside the repository of its layer (APP-6), so it cannot be invoked there.

## Open questions

1. Where are `workflow-orchestration` and `drift-management` installed? Both work across the three repositories, and neither has a use case yet.
