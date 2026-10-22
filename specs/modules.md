# Indra Software Factory

**Status:** Draft
**Audience:** The people who use the app; whoever builds one of its modules

**Scope:** What the app is, how it is installed and used, and its modules; each module specifies its own use cases

Indra Software Factory is an app of Claude Code plugins for working in three
layers: specifications written by people, norms generated from them, code
built from the norms by agents. A person installs the app once, and then
invokes its use cases.

Every module obeys the rules of the three layers, LAY-1 to LAY-6, in
[layers.md](layers.md): they are the foundation of the app, not a module.

## Terms

| Term | Meaning |
|---|---|
| App | The plugin `indra-software-factory`, which holds no use case and declares every module as a dependency, so that installing it installs them all. |
| Module | A set of use cases with one responsibility, built as one plugin of the same name. |
| Use case | One thing the user invokes, as `/<module>:<use case>`. |

## Modules

| Module | Responsibility | Specs |
|---|---|---|
| `project-management` | The three repositories of a project: their creation and their life cycle | [specs/](../plugins/project-management/specs/) |
| `specs-management` | Layer 1: the AI recommends how to improve the specs that the authors write | [specs/](../plugins/specs-management/specs/) |
| `norms-management` | Layer 2: the norms and every specification derived from them | [specs/](../plugins/norms-management/specs/) |
| `code-implementation` | Layer 3: code built from the norms, and its traceability to norm IDs | [specs/](../plugins/code-implementation/specs/) |
| `drift-management` | A drift between specs and code, sent back to layer 1 | [specs/](../plugins/drift-management/specs/) |
| `workflow-orchestration` | The flow across the modules: what starts a run, the order of the steps, the hand-offs, and how each step runs in its repository | [specs/](../plugins/workflow-orchestration/specs/) |
| `shared` | What is the same in the three layers: exploring, issues, explanations, a recap of the session | not yet specified |

## Rules

How the app is developed, a module as a plugin and a use case as a skill
of it, is in [development.md](development.md).

- **APP-1.** The app is installed once per person, at user scope. Each repository of a project also enables the app in its `.claude/settings.json`.
- **APP-2.** Every use case is installed in every repository, so a use case that belongs to one layer checks the repository it runs in and refuses outside its layer.
