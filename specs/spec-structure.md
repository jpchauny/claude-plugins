# Spec structure

**Prefix:** SST
**Audience:** Whoever writes or changes a spec of this marketplace, people and Claude sessions

**Scope:** How every spec of this marketplace is structured: which specs each level holds, the parts of a spec, the IDs of its clauses, how specs cite one another, and the format of a use case. How a spec is worded is in [writing-specs.md](writing-specs.md); how an app is developed, in [development.md](development.md)

## Terms

| Term | Meaning |
|---|---|
| Level | The marketplace, an app, a module or a use case ([DEV-5](development.md#levels)). |
| Spec | A Markdown file in the folder `specs/` of a level. |
| Clause | One binding statement of a spec, with its own ID. |
| Prefix | The upper-case letters that start the ID of every clause of one spec. |

## Specs of each level

- **SST-1.** Each level holds its specs in its own folder `specs/`. Each level has the spec that says what it is (complete list):

  | Level | Spec |
  |---|---|
  | Marketplace | `specs/marketplace.md` |
  | App | `apps/<app>/specs/app.md` |
  | Module | `.../modules/<module>/specs/module.md` |
  | Use case | `.../use-cases/<use case>/specs/<use case>.md` |

  A level may hold other specs beside it, each about one subject that holds for the level and every level inside it, such as `development.md` or `layers.md`.
- **SST-2.** A spec states only what holds for its level and the levels inside it. What a level above already states, it cites (SST-9) and does not repeat ([DEV-4](development.md#method)).

## Parts of a spec

- **SST-3.** A spec has these parts, in this order (complete list):
  1. its title, as the only heading of level 1;
  2. `**Prefix:**`, its prefix (SST-6);
  3. `**Audience:**`, who reads it;
  4. `**Scope:**`, what it covers, and where what it does not cover is;
  5. one line that names the spec of the level above, with a link, except in the specs of the marketplace, which has none;
  6. `## Terms`: a table of each term that the spec uses in a meaning of its own, with that meaning. A spec defines its own terms, and relies on no glossary;
  7. its clauses, in sections of level 2;
  8. `## Open questions`, only while it has any.
- **SST-4.** A spec has no status. A spec in the default branch of the repository is in force, whole. A new spec, or a change to one, enters the default branch only after the user approved it ([DEV-1](development.md#method)).
- **SST-5.** An open question binds nothing, and leaves every clause of its spec in force.

## IDs of clauses

- **SST-6.** Each spec has its own prefix: three or more upper-case ASCII letters, given to no other spec of the marketplace.
- **SST-7.** Each clause has the ID `<prefix>-<n>`, where `<n>` is the next number never given in that spec, starting at 1. An ID never changes and is never given again: a clause that is removed leaves its number unused.
- **SST-8.** A clause starts with its ID: in bold at the start of a list item, `**SST-1.**`, or after `Rule:` in a use case (SST-10).

## Citing

- **SST-9.** A clause of the same spec is cited by its ID alone. A clause of another spec is cited by its ID, linked to that spec: `[DEV-4](development.md#method)`.

## Format of a use case

- **SST-10.** The clauses of a use case are a Gherkin feature, in one `gherkin` code block:
  - the feature opens with its narrative, in this order: `In order to <benefit>`, `As a <role>`, `I want <what>`;
  - each clause is a `Rule:` that starts with its ID;
  - each example of a clause is a `Scenario:`, or a `Scenario Outline:` with its `Examples:` table when the scenarios differ only by values.
