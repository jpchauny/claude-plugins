# Marketplace

**Prefix:** MKT

**Audience:** Whoever installs a meta app of this marketplace, or adds or changes one

**Scope:** What this repository is, which meta apps it holds, and how a person installs one. How a meta app is developed, and the terms of the meta methodology, are in [development.md](development.md)

## Terms

| Term | Meaning |
|---|---|
| Marketplace | The Claude Code plugin marketplace `indra-software-factory`: this repository, `jpchauny/indra-software-factory`, a meta repository. |
| Meta app, meta module, meta repository, meta spec | As [development.md](development.md#terms) defines them. |

## Meta rules

- **MKT-1.** The marketplace is a set of meta apps. Each meta app is in its folder `apps/<app>/` ([DEV-5](development.md#levels)).
- **MKT-2.** The meta apps (complete list):

  | Meta app | Folder |
  |---|---|
  | Indra Software Factory | [apps/indra-software-factory/](../apps/indra-software-factory/specs/app.md) |

- **MKT-3.** `.claude-plugin/marketplace.json` lists every plugin of every meta app, one per meta module, with the folder of each.
- **MKT-4.** A person adds the marketplace once:

  ```sh
  claude plugin marketplace add jpchauny/indra-software-factory
  ```

  Which meta modules of a meta app are installed, at which scope and in which repository, the meta spec of the meta app says.
