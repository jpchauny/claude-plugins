# Development

**Status:** Draft
**Audience:** Whoever develops Indra Software Factory, people and Claude sessions

**Scope:** How the app is developed: the method, where each spec lives, and the format of a use case. What the app does is in [modules.md](modules.md) and [layers.md](layers.md)

The app is built of plugins, and is developed with spec-driven development:
the spec of a use case comes first, and the implementation follows it.

## Terms

| Term | Meaning |
|---|---|
| Module | A set of use cases with one responsibility; the modules are listed in [modules.md](modules.md). |
| Use case | One thing the user invokes. |
| Spec | The file that specifies one use case. |
| Implementation | The skill of a use case, and the scripts, templates and tests it uses. |

## Method

- **DEV-1.** Every change starts in a spec: a new use case, a change of behaviour or a fix that the spec does not already require. The user approves the spec before it is implemented.
- **DEV-2.** A use case is implemented from its spec, and from nothing else.
- **DEV-3.** Once implemented, the implementation is checked against every rule and scenario of its spec. A gap is fixed in the implementation; when the spec is what is wrong, the spec is fixed first, and approved again.
- **DEV-4.** Each fact is written in one place. Every other place that needs it refers to that place, and does not repeat it.

## Where things live

- **DEV-5.** Each module is one plugin, `plugins/<module>/`, named as the module. Each use case is one skill of it, `skills/<use case>/`, named as the use case and invoked as `/<module>:<use case>`.
- **DEV-6.** The spec of a use case is `plugins/<module>/specs/<use case>.md`. What concerns the whole app is in this folder, `specs/`.

## Format of a use case

- **DEV-7.** A use case is specified as a Gherkin feature, in a `gherkin` code block:
  - the feature opens with its narrative, in this order: `In order to <benefit>`, `As a <role>`, `I want <what>`;
  - each rule is a `Rule:` that starts with its ID;
  - each example of a rule is a `Scenario:`, or a `Scenario Outline:` with its `Examples:` table when the scenarios differ only by values.
