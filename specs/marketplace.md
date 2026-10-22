# Marketplace

**Status:** Draft
**Audience:** Whoever installs an app of this marketplace, or adds or changes one

**Scope:** What this repository is, which apps it holds, and how a person installs one. How an app is developed is in [development.md](development.md)

## Terms

| Term | Meaning |
|---|---|
| Marketplace | The Claude Code plugin marketplace `jpchauny-plugins`: this repository, `jpchauny/claude-plugins`. |
| App | What a person installs from the marketplace: one plugin that brings its modules with it ([DEV-7](development.md#levels)). |

## Rules

- **MKT-1.** The marketplace is a set of apps. Each app is in its folder `apps/<app>/` ([DEV-5](development.md#levels)).
- **MKT-2.** The apps (complete list):

  | App | Folder |
  |---|---|
  | Indra Software Factory | [apps/indra-software-factory/](../apps/indra-software-factory/specs/app.md) |

- **MKT-3.** `.claude-plugin/marketplace.json` lists every plugin of every app, the app's own and each of its modules', with the folder of each.
- **MKT-4.** A person adds the marketplace once, then installs an app at user scope:

  ```sh
  claude plugin marketplace add jpchauny/claude-plugins
  claude plugin install <app>@jpchauny-plugins --scope user
  ```
