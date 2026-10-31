# Development

**Prefix:** DEV

**Audience:** Whoever develops a meta repository, people and Claude sessions

**Scope:** How every meta repository is developed with the meta methodology: the method, the four meta levels and where the meta specs and the meta implementation of each meta level live, the format of a meta use case, and the terms of the meta methodology. What this repository is, is in [marketplace.md](marketplace.md). Out of scope: the methodology ISF, which the meta app Indra Software Factory implements for the projects of its users, and which this spec never states.

Every meta repository is built of plugins, and is developed with
spec-driven development: the meta spec comes first, and the meta
implementation follows it.

## Terms

| Term | Meaning |
|---|---|
| ISF | Indra Software Factory: a methodology to develop projects of any kind. The meta app Indra Software Factory implements it. |
| Meta methodology | The methodology with which every meta repository is developed: the method of this meta spec, with [spec-structure.md](spec-structure.md) and [writing-specs.md](writing-specs.md). |
| Meta repository | A repository developed with the meta methodology (complete list): this repository, and every `<project>-tooling` repository. |
| `<project>-tooling` repository | The one repository of a project that holds the project's own plugins, for example its generators of derived norms. |
| Meta level | One of the four parts that hold one another: the meta repository, a meta app, a meta module, a meta use case. |
| Meta app | A set of meta modules, each installed on its own. |
| Meta module | A part of one meta app with one responsibility: its meta use cases, its hooks, or both. |
| Meta use case | One thing the user invokes, as a skill of a meta module. |
| Meta spec | A Markdown file that specifies a meta level, in the folder `specs/` of that meta level. The meta specs of this repository are those of its folder `specs/` and those of its meta apps; the meta specs of the meta app Indra Software Factory define ISF. |
| Meta rule | One binding statement of a meta spec, with its own ID: DEV-n, SST-n, SPC-n, MKT-n and the IDs of the meta specs of each meta app. |
| Meta implementation | The skill of a meta use case, and the code, scripts, templates and tests it uses; the hooks of a meta module, and the scripts and tests they use. |
| Unqualified term | A term without the word `meta` in front; for example (not a complete list): spec, draft spec, use case, module, rule, norm. An unqualified term always means the term of ISF: that of a project that uses ISF. A term of the meta methodology always starts with the word `meta`, in prose (meta spec) and in code and JSON (`meta_spec`). An unqualified term never means a part of a meta repository as the meta methodology develops it: the module `utilities` of ISF (DEV-10) is a module as a project that uses ISF sees it, and a meta module as this repository develops it. |

Rationale of the unqualified term: the common case is a project that uses ISF, so its terms go without a qualifier; the meta methodology, used only to build ISF and the tooling of each project, carries the word `meta`, so no reader takes one methodology's term for the other's. ISF never cites this table.

## Method

- **DEV-1.** Every change starts in a meta spec: a new meta use case, a change of behaviour or a fix that the meta spec does not already require. The user approves the meta spec before it is implemented.
- **DEV-2.** A meta use case is implemented from its meta spec, and from nothing else. The hooks of a meta module are implemented from the meta spec of the meta module, and from nothing else.
- **DEV-3.** Once implemented, the meta implementation is checked against every meta rule and scenario of its meta spec. A gap is fixed in the meta implementation; when the meta spec is what is wrong, the meta spec is fixed first, and approved again.
- **DEV-4.** Each fact is written in one place. Every other place that needs it refers to that place, and does not repeat it.
- **DEV-9.** Every meta spec must follow [writing-specs.md](writing-specs.md).
- **DEV-10.** The development of a meta repository never runs a use case, hook or script of ISF on a meta repository. The development of a meta repository never takes a rule of ISF as a meta rule. Exception (complete list): the module `utilities` of ISF, usable in any project, a meta repository included, because its use cases implement no rule of a methodology. Rationale: ISF is a product whose methodology is for the projects of its users; a meta repository developed with ISF's five layers would need ISF to build ISF, and a `<project>-tooling` repository developed with them would need the project's tooling to build that tooling. Any tool that the meta methodology needs is part of the meta methodology.
- **DEV-11.** A `<project>-tooling` repository cites this spec by its URL, [https://github.com/jpchauny/claude-plugins/blob/main/specs/development.md](https://github.com/jpchauny/claude-plugins/blob/main/specs/development.md), and does not copy it. Rationale: a copy would drift from this spec (DEV-4).

## Levels

- **DEV-5.** The four meta levels, each inside the one above (complete list):

  | Meta level | Folder |
  |---|---|
  | Meta repository | the root of the meta repository |
  | Meta app | `apps/<app>/` |
  | Meta module | `apps/<app>/modules/<module>/` |
  | Meta use case | `apps/<app>/modules/<module>/use-cases/<use case>/` |

  A `<project>-tooling` repository holds one meta app, at its root: there the folder of the meta app is the root, and its meta modules are in `modules/<module>/`.

- **DEV-6.** Each meta level holds its meta specs in its own folder `specs/`. A meta spec states what is true for its meta level and for every meta level inside it, and cites the meta levels above it instead of repeating them (DEV-4). The meta specs of a meta use case are `specs/<use case>.md`; the meta spec that says what a meta module is, is `specs/module.md`; the one that says what a meta app is, is `specs/app.md`.
- **DEV-7.** Each meta level is built as a part of Claude Code (complete list):
  - a meta app is no plugin: it is the folder `apps/<app>/` of its meta specs and its meta modules. No plugin installs the meta modules of a meta app together;
  - a meta module is one plugin, named as the meta module, which depends on no other plugin. Once it has a meta use case, its `.claude-plugin/plugin.json` declares `"skills": "./use-cases/"`. It has no folder `skills/`;
  - a meta module may have hooks, with or without a meta use case. Its hooks are declared in its file `hooks/hooks.json`, and the scripts they run are in its folder `scripts/`. A meta module with no meta use case has no skill;
  - a meta use case is one skill, named as the meta use case and invoked as `/<module>:<use case>`. Its folder holds its `SKILL.md`, and the scripts and templates that only it uses. Code that several meta use cases of a meta module share is in the meta module's folder.

## Format of a meta use case

- **DEV-8.** A meta use case is specified as a Gherkin feature, in a `gherkin` code block:
  - the feature opens with its narrative, in this order: `In order to <benefit>`, `As a <role>`, `I want <what>`;
  - each meta rule is a `Rule:` that starts with its ID;
  - each example of a meta rule is a `Scenario:`, or a `Scenario Outline:` with its `Examples:` table when the scenarios differ only by values.
