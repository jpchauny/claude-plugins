# Indra Software Factory

**Prefix:** APP

**Audience:** The people who use the app; whoever builds one of its modules

**Scope:** What the app is, how it is used, and its modules. The app is one of the marketplace, listed in [marketplace.md](../../../specs/marketplace.md); each module specifies its own use cases; where each module is installed is in [layers.md](../modules/development-methodology/specs/layers.md#where-each-module-is-installed)

Indra Software Factory is an app of Claude Code plugins for working in five
layers: draft specs and specs written by people, norms and derived norms
generated from them, acceptance areas and acceptance units that agents write
from the norms and people approve, and code built from the norms and the
derived norms by agents. Every project also has one orchestration
repository, which is no layer, from which a person starts and controls a run
across the layers
([LAY-11](../modules/development-methodology/specs/layers.md#the-orchestration-repository)).
A person installs each module where
[APP-6](../modules/development-methodology/specs/layers.md#where-each-module-is-installed)
says, and then invokes its use cases, if it has any.

Every module obeys the rules of the five layers, the clauses LAY-n of
[layers.md](../modules/development-methodology/specs/layers.md), and the flow of a run,
[ORC-15](../modules/development-methodology/specs/flow.md#start-a-run). Both are
specs of the module `development-methodology`, which carries the methodology to
every repository of a project.

## Terms

| Term | Meaning |
|---|---|
| App | Indra Software Factory: its modules, each one a plugin installed on its own. The app itself is no plugin. |
| Module | A part of the app with one responsibility, its use cases, its hooks or both, built as one plugin of the same name. |
| Use case | One thing the user invokes, as `/<module>:<use case>`. |

## Modules

| Module | Responsibility | Specs |
|---|---|---|
| `development-methodology` | The development methodology: the five layers, the flow of a run across them, and their terms; an index of it in every session of every repository of a project | [module.md](../modules/development-methodology/specs/module.md) |
| `project-management` | The repositories of a project: their creation and their life cycle | [module.md](../modules/project-management/specs/module.md) |
| `specs-management` | Layers 0 and 1: the AI recommends how to improve the draft specs and the specs that the authors write, and moves specs between the two layers | [module.md](../modules/specs-management/specs/module.md) |
| `norms-management` | Layer 2: the norms and the derived norms | [module.md](../modules/norms-management/specs/module.md) |
| `acceptance-management` | Layer 3: the acceptance areas and the acceptance units, the increments and the order in which the units are implemented, their acceptance tests, and when a unit, an area and an increment are done | [module.md](../modules/acceptance-management/specs/module.md) |
| `code-implementation` | Layer 4: code built from the norms and the derived norms, and its traceability to the acceptance units it implements, and through them to the norms | [module.md](../modules/code-implementation/specs/module.md) |
| `drift-management` | A drift found while defining acceptance in layer 3 or implementing in layer 4, sent back to layer 1 | [module.md](../modules/drift-management/specs/module.md) |
| `workflow-orchestration` | Runs the flow across the modules from the orchestration repository: a person starts and controls a run there; each step runs as a headless session in the repository of its layer; the evidence run of the acceptance tests; the queue of the requester | [module.md](../modules/workflow-orchestration/specs/module.md) |
| `utilities` | Tools usable in any layer: exploring, the issue tree, explanations, a recap of the session | not yet specified |

## Rules

How the app is developed, a module as a plugin and a use case as a skill
of it, is in [development.md](../../../specs/development.md). Where each
module is installed is
[APP-6](../modules/development-methodology/specs/layers.md#where-each-module-is-installed),
a clause of the methodology since it moved there
([SST-11](../../../specs/spec-structure.md#ids-of-clauses)).

- **APP-5.** Each module is a plugin of its own. No module depends on another, and no plugin installs them together.
- **APP-7.** A use case of one layer is not installed outside the repository of its layer ([APP-6](../modules/development-methodology/specs/layers.md#where-each-module-is-installed)), so it cannot be invoked there.
