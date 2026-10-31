# Spec structure

**Prefix:** SST
**Audience:** Whoever writes or changes a meta spec, people and Claude sessions

**Scope:** How every meta spec is structured: which meta specs each meta level holds, the parts of a meta spec, the IDs of its meta rules, how meta specs cite one another, and the format of a meta use case. How a meta spec is worded is in [writing-specs.md](writing-specs.md); how a meta repository is developed, and the terms of the meta methodology, in [development.md](development.md). Out of scope: the structure of a spec of a project that uses ISF.

## Terms

| Term | Meaning |
|---|---|
| Meta level, meta spec, meta rule, meta use case, meta repository | As [development.md](development.md#terms) defines them. |
| Prefix | The upper-case letters that start the ID of every meta rule written in one meta spec, except a meta rule moved into it from another meta spec (SST-11). |

## Meta specs of each meta level

- **SST-1.** Each meta level holds its meta specs in its own folder `specs/`, as Markdown files. Each meta level has the meta spec that says what it is (complete list):

  | Meta level | Meta spec |
  |---|---|
  | Meta repository | `specs/marketplace.md` in this repository |
  | Meta app | `apps/<app>/specs/app.md` |
  | Meta module | `.../modules/<module>/specs/module.md` |
  | Meta use case | `.../use-cases/<use case>/specs/<use case>.md` |

  A meta level may hold other meta specs beside it, each about one subject that holds for the meta level and every meta level inside it, such as `development.md` or `layers.md`.
- **SST-2.** A meta spec states only what holds for its meta level and the meta levels inside it. What a meta level above already states, it cites (SST-9) and does not repeat ([DEV-4](development.md#method)).

## Parts of a meta spec

- **SST-3.** A meta spec has these parts, in this order (complete list):
  1. its title, as the only heading of level 1;
  2. `**Prefix:**`, its prefix (SST-6);
  3. `**Audience:**`, who reads it;
  4. `**Scope:**`, what it covers, and where what it does not cover is;
  5. one line that names the meta spec of the meta level above, with a link, except in the meta specs of the meta repository, which has none;
  6. `## Terms`: a table of each term that the meta spec uses in a meaning of its own, with that meaning. A meta spec defines its own terms, and relies on no glossary;
  7. its meta rules, in sections of level 2;
  8. `## Open questions`, only while it has any.
- **SST-4.** A meta spec has no status. A meta spec in the default branch of the repository is in force, whole. A new meta spec, or a change to one, enters the default branch only after the user approved it ([DEV-1](development.md#method)).
- **SST-5.** An open question binds nothing, and leaves every meta rule of its meta spec in force.

<a id="ids-of-clauses"></a>
## IDs of meta rules

- **SST-6.** Each meta spec has its own prefix: three or more upper-case ASCII letters, given to no other meta spec of the meta repository.
- **SST-7.** Each meta rule written in a meta spec has the ID `<prefix>-<n>`, where `<n>` is the next number never given in that meta spec, starting at 1. An ID never changes and is never given again: a meta rule that is removed leaves its number unused.
- **SST-8.** A meta rule starts with its ID: in bold at the start of a list item, `**SST-1.**`, or after `Rule:` in a meta use case (SST-10).
- **SST-11.** A meta rule moved from one meta spec to another keeps its ID, prefix included (SST-7): it is no meta rule of the meta spec whose prefix it bears any more, and that meta spec never gives its number again. The meta spec it moved to gives its own prefix to every meta rule written in it afterwards.

## Citing

- **SST-9.** A meta rule of the same meta spec is cited by its ID alone. A meta rule of another meta spec is cited by its ID, linked to that meta spec: `[DEV-4](development.md#method)`.

## Format of a meta use case

- **SST-10.** The meta rules of a meta use case are a Gherkin feature, in one `gherkin` code block:
  - the feature opens with its narrative, in this order: `In order to <benefit>`, `As a <role>`, `I want <what>`;
  - each meta rule is a `Rule:` that starts with its ID;
  - each example of a meta rule is a `Scenario:`, or a `Scenario Outline:` with its `Examples:` table when the scenarios differ only by values.

## Open questions

1. Which meta spec says what a `<project>-tooling` repository is, at the meta level of the meta repository (SST-1)? Until decided, SST-1 names that meta spec only for this repository.
