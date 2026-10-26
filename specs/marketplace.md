# Marketplace

**Prefix:** MKT

**Audience:** Whoever installs an app of this marketplace, or adds or changes one

**Scope:** What this repository is, which apps it holds, and how a person installs one. How an app is developed is in [development.md](development.md)

## Terms

| Term | Meaning |
|---|---|
| Marketplace | The Claude Code plugin marketplace `jpchauny-plugins`: this repository, `jpchauny/claude-plugins`. |
| App | A set of modules, each one a plugin that a person installs on its own ([DEV-7](development.md#levels)). |

## Rules

- **MKT-1.** The marketplace is a set of apps. Each app is in its folder `apps/<app>/` ([DEV-5](development.md#levels)).
- **MKT-2.** The apps (complete list):

  | App | Folder |
  |---|---|
  | Indra Software Factory | [apps/indra-software-factory/](../apps/indra-software-factory/specs/app.md) |
  | Clean Language | [apps/clean-language/](../apps/clean-language/specs/app.md) |

- **MKT-3.** `.claude-plugin/marketplace.json` lists every plugin of every app, one per module, with the folder of each.
- **MKT-4.** A person adds the marketplace once:

  ```sh
  claude plugin marketplace add jpchauny/claude-plugins
  ```

  Which modules of an app are installed, at which scope and in which repository, the spec of the app says.
