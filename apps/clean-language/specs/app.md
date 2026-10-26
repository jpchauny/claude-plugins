# Clean Language

**Prefix:** CLN

**Audience:** The people who write the specs of the Clean Language project; whoever builds one of the modules of this app

**Scope:** What the app is, its modules, and where each one is installed. Each module specifies its own use cases and hooks. How the four layers of a project work is in [layers.md](../../indra-software-factory/modules/development-methodology/specs/layers.md) of the app Indra Software Factory

The app of the marketplace listed in [marketplace.md](../../../specs/marketplace.md).

Clean Language is a programming language, specified in a project of four
layers of Indra Software Factory. This app holds the plugins that are specific
to that project, and that no other project uses: what they check or generate
is Clean itself. A plugin that serves every project belongs to Indra Software
Factory, not to this app.

## Terms

| Term | Meaning |
|---|---|
| App | Clean Language: its modules, each one a plugin installed on its own. The app itself is no plugin. |
| Module | A part of the app with one responsibility, its use cases, its hooks or both, built as one plugin of the same name ([DEV-7](../../../specs/development.md#levels)). |
| Use case | One thing the user invokes, as `/<module>:<use case>`. |
| The project | The project Clean Language: the repositories that its `project.json` lists, with the layer of each ([LAY-1](../../indra-software-factory/modules/development-methodology/specs/layers.md#rules)). |

## Modules

| Module | Responsibility | Specs |
|---|---|---|
| `clean-examples` | Layers 0 and 1: the rules of how a Clean example is written, the audit of the examples of a layer, and the hook that refuses a malformed example as it is written | [module.md](../modules/clean-examples/specs/module.md) |
| `clean-derived-norms` | Layer 2: the derived norms of Clean, each with its own generator, such as the grammar and the semantics | [module.md](../modules/clean-derived-norms/specs/module.md) |

## Rules

How a module is built, one plugin that depends on no other, is [DEV-7](../../../specs/development.md#levels).

- **CLN-1.** Where each module is installed (complete list): each one is enabled in the `.claude/settings.json` of these repositories of the project, and of no other repository:

  | Module | Repositories |
  |---|---|
  | `clean-examples` | the repository of layer 0 and the repository of layer 1 |
  | `clean-derived-norms` | the repository of layer 2 |

- **CLN-2.** Every module obeys the rules of the four layers, LAY-1 to LAY-7, in [layers.md](../../indra-software-factory/modules/development-methodology/specs/layers.md#rules).