# Development

**Prefix:** DEV

**Audience:** Whoever develops an app of this marketplace, people and Claude sessions

**Scope:** How every app of this marketplace is developed: the method, the four levels and where the specs and the implementation of each level live, and the format of a use case. What the marketplace is, is in [marketplace.md](marketplace.md)

Every app of this marketplace is built of plugins, and is developed with
spec-driven development: the spec comes first, and the implementation
follows it.

## Terms

| Term | Meaning |
|---|---|
| Level | One of the four parts that hold one another: the marketplace, an app, a module, a use case. |
| App | What a person installs: a set of modules. |
| Module | A set of use cases of one app, with one responsibility. |
| Use case | One thing the user invokes. |
| Spec | A file that specifies a level. |
| Implementation | The skill of a use case, and the code, scripts, templates and tests it uses. |

## Method

- **DEV-1.** Every change starts in a spec: a new use case, a change of behaviour or a fix that the spec does not already require. The user approves the spec before it is implemented.
- **DEV-2.** A use case is implemented from its spec, and from nothing else.
- **DEV-3.** Once implemented, the implementation is checked against every rule and scenario of its spec. A gap is fixed in the implementation; when the spec is what is wrong, the spec is fixed first, and approved again.
- **DEV-4.** Each fact is written in one place. Every other place that needs it refers to that place, and does not repeat it.
- **DEV-9.** Every spec of this marketplace must follow [writing-specs.md](writing-specs.md).

## Levels

- **DEV-5.** The four levels, each inside the one above (complete list):

  | Level | Folder |
  |---|---|
  | Marketplace | the root of this repository |
  | App | `apps/<app>/` |
  | Module | `apps/<app>/modules/<module>/` |
  | Use case | `apps/<app>/modules/<module>/use-cases/<use case>/` |

- **DEV-6.** Each level holds its specs in its own folder `specs/`. A spec states what is true for its level and for every level inside it, and cites the levels above it instead of repeating them (DEV-4). The specs of a use case are `specs/<use case>.md`; the spec that says what a module is, is `specs/module.md`; the one that says what an app is, is `specs/app.md`.
- **DEV-7.** Each level is built as a part of Claude Code (complete list):
  - an app is one plugin, at `apps/<app>/`, named as the app. It holds no use case, and declares each of its modules as a dependency, so that installing it installs them all;
  - a module is one plugin, named as the module. Once it has a use case, its `.claude-plugin/plugin.json` declares `"skills": "./use-cases/"`. It has no folder `skills/`;
  - a use case is one skill, named as the use case and invoked as `/<module>:<use case>`. Its folder holds its `SKILL.md`, and the scripts and templates that only it uses. Code that several use cases of a module share is in the module's folder.

## Format of a use case

- **DEV-8.** A use case is specified as a Gherkin feature, in a `gherkin` code block:
  - the feature opens with its narrative, in this order: `In order to <benefit>`, `As a <role>`, `I want <what>`;
  - each rule is a `Rule:` that starts with its ID;
  - each example of a rule is a `Scenario:`, or a `Scenario Outline:` with its `Examples:` table when the scenarios differ only by values.
