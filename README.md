# claude-plugins

A Claude Code plugin marketplace (`jpchauny-plugins`) with the skills the team shares across projects.

| Plugin | Skills | What for |
|--------|--------|----------|
| `team-workflow` | `/team-workflow:explore` | Think a problem through before it deserves a spec, a plan or code: numbered candidates, trade-offs, what is already decided, open questions. No implementation proposals, no next steps, nothing written until the user promotes. |
| `team-workflow` | `/team-workflow:issue`, `/team-workflow:tree`, `/team-workflow:baseline` | Pending work as a tree of GitHub issues: every bifurcation is proposed, created after the user's yes as a sub-issue of the node where it was found, and carries a hand-off prompt. |
| `team-workflow` | `/team-workflow:explain` | Explain a topic one step at a time, assuming no prior knowledge: every new term defined as it appears, one idea per message, and the next step only after the user's "got it". |

## How the team works with it

- **Root:** an open issue labelled `baseline` (`Línea de base YYYY-MM-DD`), found from any repository that has pending items under it; nothing is configured. Its children are the top-level pending items; each bifurcation hangs under the node where it was found, across repositories.
- **Bifurcation:** Claude proposes it in one line; nothing enters the tree without the user's yes. Every issue carries a hand-off: the context to resume it in any session.
- **State, from labels:** `question` ⏳ waits for the user, `blocked` ⛔, `breaks-ci` 🔴, otherwise ▶ Claude can advance. Optional subject: `tema:<name>`.
- **Seeing it:** only on request (`/team-workflow:tree`): a summary and the tree in the chat. A page with the same view only when explicitly asked. Each person sees what their GitHub access allows.
- **New baseline:** only when the user declares it (`/team-workflow:baseline`): a new root, the open items move under it, the old root closes as a dated snapshot.
- **Exploring is not implementing:** while exploring, Claude answers and proposes no implementation. While working, it shows where it is in one line (baseline › node › step).
- **Explaining is one step at a time:** on `/team-workflow:explain`, Claude gives one short step per message, defines every new term, and waits for the user's "got it" before the next.

## Use it in a project

Once, in the project repository (the commands write `.claude/settings.json`; commit it):

```sh
claude plugin marketplace add jpchauny/claude-plugins --scope project
claude plugin install team-workflow@jpchauny-plugins --scope project
```

Then add to the project's `CLAUDE.md`:

```markdown
## Issues

Pending items and findings go to the issue tree with `/team-workflow:issue`
(plugin `team-workflow`, marketplace `jpchauny/claude-plugins`).
```

And, to make exploratory mode reliable:

```markdown
## Exploring

When the user opens a problem to think about before specifying or building it,
or says "exploremos", "modo exploratorio", "qué opciones hay", use
`/team-workflow:explore`: candidates and trade-offs, no implementation
proposals, nothing written until the user promotes.
```

And, to make the step-by-step explanation reliable:

```markdown
## Explaining

When the user asks for a didactic explanation, or says "explícame paso a
paso", "explica simple", "explain step by step", use `/team-workflow:explain`:
one short step per message, every new term defined, the next step only after
the user's "got it".
```

A project can add an `## Issue verification` section to its `CLAUDE.md`: the commands that tell whether an issue is resolved. The skill copies them into each hand-off.

## Each teammate

The repository is public: nothing to configure. Opening a project that declares the marketplace, accept the folder's trust dialog. If Claude Code reports that the plugin is enabled but not installed:

```sh
claude plugin install team-workflow@jpchauny-plugins --scope project
```

## Updates

Change a skill here, push to `main`. Updates are not automatic for a third-party marketplace: each teammate runs

```sh
claude plugin marketplace update jpchauny-plugins
claude plugin update team-workflow@jpchauny-plugins
```

then `/reload-plugins` or a new session. (Or enable auto-update for this marketplace in `/plugin`, tab **Marketplaces**.)

Validate before pushing:

```sh
claude plugin validate .
claude plugin validate ./plugins/team-workflow
```
