# Indra Software Factory

A Claude Code app, published as the plugin marketplace `jpchauny-plugins`, for
working in three layers: specifications written by people, norms generated
from them, code built from the norms by agents.

The app is built from specs: the rules of the three layers are in
[specs/layers.md](specs/layers.md), the modules in
[specs/modules.md](specs/modules.md), and each module specifies its use cases
in the folder `specs/` of its plugin.

| Module (plugin) | Use cases |
|--------|----------|
| `project-management` | Create a project (`/project-management:create-project`) |
| `specs-management` | Recommend improvements to the specs (`/specs-management:audit`) |
| `norms-management` | Regenerate the norms (`/norms-management:build`, `/norms-management:verify`) |
| `code-implementation` | Implement the changed norms (not yet built) |
| `drift-management` | Report a drift (not yet built) |
| `workflow-orchestration` | Start a run (not yet built) |
| `shared` | Explore (`/shared:explore`); the issue tree (`/shared:issue`, `/shared:tree`, `/shared:baseline`); explain one step at a time (`/shared:explain`); recap the session (`/shared:recap`) |

The plugin `indra-software-factory` is the app itself: it declares every
module as a dependency, so installing it installs them all.

## Install

Once per person:

```sh
claude plugin marketplace add jpchauny/claude-plugins
claude plugin install indra-software-factory@jpchauny-plugins --scope user
```

Then, in any session, `/project-management:create-project <name>`. It creates
the three repositories, each enabling the app in its `.claude/settings.json`.

## Add the app to an existing repository

In the repository (the commands write `.claude/settings.json`; commit it):

```sh
claude plugin marketplace add jpchauny/claude-plugins --scope project
claude plugin install indra-software-factory@jpchauny-plugins --scope project
```


### How `shared` works

- **Root:** an open issue labelled `baseline` (`Línea de base YYYY-MM-DD`), found from any repository that has pending items under it; nothing is configured. Its children are the top-level pending items; each bifurcation hangs under the node where it was found, across repositories.
- **Bifurcation:** Claude proposes it in one line; nothing enters the tree without the user's yes. Every issue carries a hand-off: the context to resume it in any session.
- **State, from labels:** `question` ⏳ waits for the user, `blocked` ⛔, `breaks-ci` 🔴, otherwise ▶ Claude can advance. Optional subject: `tema:<name>`.
- **Seeing it:** only on request (`/shared:tree`): a summary and the tree in the chat. A page with the same view only when explicitly asked. Each person sees what their GitHub access allows.
- **New baseline:** only when the user declares it (`/shared:baseline`): a new root, the open items move under it, the old root closes as a dated snapshot.
- **Exploring is not implementing:** while exploring, Claude answers and proposes no implementation. While working, it shows where it is in one line (baseline › node › step).
- **Explaining is one step at a time:** on `/shared:explain`, Claude gives one short step per message, defines every new term, and waits for the user's "got it" before the next.

## Use it in a project


## Each teammate

The repository is public: nothing to configure. Opening a project that
declares the marketplace, accept the folder's trust dialog. If Claude Code
reports that a plugin is enabled but not installed:

```sh
claude plugin install indra-software-factory@jpchauny-plugins --scope project
```

## Updates

Every project uses the latest version
([LAY-6](specs/layers.md#lay-6--every-project-uses-the-latest-version-of-the-plugins)).
Change a plugin here, push to `main`. Updates are not automatic for a
third-party marketplace: each teammate runs

```sh
claude plugin marketplace update jpchauny-plugins
claude plugin update indra-software-factory@jpchauny-plugins
```

then `/reload-plugins` or a new session. (Or enable auto-update for this
marketplace in `/plugin`, tab **Marketplaces**.)

Validate before pushing:

```sh
claude plugin validate .
for p in plugins/*/; do claude plugin validate "$p"; done
```
