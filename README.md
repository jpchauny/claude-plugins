# Indra Software Factory

A Claude Code app, published as the plugin marketplace `jpchauny-plugins`, for
working in four layers: draft specs and specs written by people, norms and
derived norms generated from them, code built from the norms and the derived norms by agents.

The repository is a marketplace of apps, built from specs at four levels:
marketplace, app, module and use case, each with its folder `specs/`. The
marketplace is in [specs/marketplace.md](specs/marketplace.md), how an app is
developed in [specs/development.md](specs/development.md), and this app in
[apps/indra-software-factory/specs/app.md](apps/indra-software-factory/specs/app.md).

| Module (plugin) | Use cases |
|--------|----------|
| `development-methodology` | None: it gives every session an index of the development methodology (the four layers, the flow, their terms) |
| `project-management` | Create a project (`/project-management:create-project`) |
| `specs-management` | Recommend improvements to the specs (`/specs-management:audit`); write draft specs from an interview (`/specs-management:write`); move specs between layers 0 and 1 (`/specs-management:promote`, `/specs-management:demote`) |
| `norms-management` | Regenerate the norms (`/norms-management:build`, `/norms-management:verify`) |
| `code-implementation` | Implement the changed norms (not yet built) |
| `drift-management` | Report a drift (not yet built) |
| `workflow-orchestration` | Run the flow (not yet built) |
| `utilities` | Explore (`/utilities:explore`); the issue tree (`/utilities:issue`, `/utilities:tree`, `/utilities:baseline`); explain one step at a time (`/utilities:explain`); recap the session (`/utilities:recap`) |

Each module is a plugin of its own. A repository enables
`development-methodology`, `utilities` and the module of its layer
([APP-6](apps/indra-software-factory/modules/development-methodology/specs/layers.md#where-each-module-is-installed)).

## Install

Once per person:

```sh
claude plugin marketplace add jpchauny/claude-plugins
claude plugin install project-management@jpchauny-plugins --scope user
```

Then, in any session, `/project-management:create-project <name>`. It creates
the repositories of the four layers, each enabling in its `.claude/settings.json`
`development-methodology`, `utilities` and the module of its layer.

## Add the modules to an existing repository

In the repository (the commands write `.claude/settings.json`; commit it),
with `<module>` the module of its layer: `specs-management`,
`norms-management` or `code-implementation`:

```sh
claude plugin marketplace add jpchauny/claude-plugins --scope project
claude plugin install development-methodology@jpchauny-plugins --scope project
claude plugin install utilities@jpchauny-plugins --scope project
claude plugin install <module>@jpchauny-plugins --scope project
```


### How `utilities` works

- **Root:** an open issue labelled `baseline` (`Línea de base YYYY-MM-DD`), found from any repository that has pending items under it; nothing is configured. Its children are the top-level pending items; each bifurcation hangs under the node where it was found, across repositories.
- **Bifurcation:** Claude proposes it in one line; nothing enters the tree without the user's yes. Every issue carries a hand-off: the context to resume it in any session.
- **State, from labels:** `question` ⏳ waits for the user, `blocked` ⛔, `breaks-ci` 🔴, otherwise ▶ Claude can advance. Optional subject: `tema:<name>`.
- **Seeing it:** only on request (`/utilities:tree`): a summary and the tree in the chat. A page with the same view only when explicitly asked. Each person sees what their GitHub access allows.
- **New baseline:** only when the user declares it (`/utilities:baseline`): a new root, the open items move under it, the old root closes as a dated snapshot.
- **Exploring is not implementing:** while exploring, Claude answers and proposes no implementation. While working, it shows where it is in one line (baseline › node › step).
- **Explaining is one step at a time:** on `/utilities:explain`, Claude gives one short step per message, defines every new term, and waits for the user's "got it" before the next.

## Use it in a project


## Each teammate

The repository is public: nothing to configure. Opening a project that
declares the marketplace, accept the folder's trust dialog. If Claude Code
reports that a plugin is enabled but not installed, install each plugin
that the repository's `.claude/settings.json` enables:

```sh
claude plugin install <plugin>@jpchauny-plugins --scope project
```

## Updates

Every project uses the latest version
([LAY-6](apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).
Change a plugin here, push to `main`. Updates are not automatic for a
third-party marketplace: each teammate runs

```sh
claude plugin marketplace update jpchauny-plugins
claude plugin update <plugin>@jpchauny-plugins
```

for each plugin they have installed.

then `/reload-plugins` or a new session. (Or enable auto-update for this
marketplace in `/plugin`, tab **Marketplaces**.)

Validate before pushing:

```sh
claude plugin validate .
claude plugin validate apps/indra-software-factory
for p in apps/indra-software-factory/modules/*/; do claude plugin validate "$p"; done
```
