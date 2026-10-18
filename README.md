# claude-plugins

A Claude Code plugin marketplace (`jpchauny-plugins`) for working in three
layers: specifications written by people, norms generated from them, code
built from the norms by agents.

The spec-driven design process, in prose, is in [spec-driven-design-process/](spec-driven-design-process/README.md): the single
source of truth. The plugins are its tools.

| Plugin | Enabled in | What for |
|--------|------------|----------|
| `shared` | every repository | Explore before specifying or building (`/shared:explore`); pending items and findings as a tree of GitHub issues (`/shared:issue`, `/shared:tree`, `/shared:baseline`); explanations one step at a time (`/shared:explain`) |
| `specs` | `<project>-specs` | Layer 1: tools that help people write the specification |
| `norms` | `<project>-norms` | Layer 2: the norms generator, and the method for a project's own generators |
| `code` | `<project>-code` | Layer 3: the implementation method and code traceability |
| `new-project` | nowhere: user scope | Creates the three repositories of a new project (`/new-project:new-project`) |
| `recap` | nowhere: user scope | Puts you back up to speed on the session you invoke it from (`/recap:recap`) |

## Start a new project

Once per person:

```sh
claude plugin marketplace add jpchauny/claude-plugins
claude plugin install new-project@jpchauny-plugins --scope user
```

Then, in any session, `/new-project:new-project <name>`. It creates the three
repositories with the plugins of each layer enabled in their
`.claude/settings.json`.

## Add the plugins to an existing repository

In the repository (the commands write `.claude/settings.json`; commit it):

```sh
claude plugin marketplace add jpchauny/claude-plugins --scope project
claude plugin install shared@jpchauny-plugins --scope project
claude plugin install <specs|norms|code>@jpchauny-plugins --scope project
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
claude plugin install <plugin>@jpchauny-plugins --scope project
```

## Updates

Every project uses the latest version
([LAY-6](spec-driven-design-process/layers.md#lay-6--every-project-uses-the-latest-version-of-the-plugins)).
Change a plugin here, push to `main`. Updates are not automatic for a
third-party marketplace: each teammate runs

```sh
claude plugin marketplace update jpchauny-plugins
claude plugin update <plugin>@jpchauny-plugins
```

then `/reload-plugins` or a new session. (Or enable auto-update for this
marketplace in `/plugin`, tab **Marketplaces**.)

Validate before pushing:

```sh
claude plugin validate .
for p in plugins/*/; do claude plugin validate "$p"; done
```
