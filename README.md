# claude-plugins

A private Claude Code plugin marketplace (`jpchauny-plugins`) with the skills the team shares across projects.

| Plugin | Skills | What for |
|--------|--------|----------|
| `team-workflow` | `/team-workflow:issue` | Every pending item or finding goes to a GitHub issue the moment it appears, with a self-contained hand-off prompt. |

## Use it in a project

Once, in the project repository (the commands write `.claude/settings.json`; commit it):

```sh
claude plugin marketplace add jpchauny/claude-plugins --scope project
claude plugin install team-workflow@jpchauny-plugins --scope project
```

Then add to the project's `CLAUDE.md`:

```markdown
## Issues

Every pending item or finding not resolved in the current change goes to a GitHub
issue at the moment it appears, with `/team-workflow:issue` (plugin `team-workflow`,
marketplace `jpchauny/claude-plugins`). Never to a file, to memory or to the close of
the session.
```

A project can add an `## Issue verification` section to its `CLAUDE.md`: the commands that tell whether an issue is resolved. The skill copies them into each hand-off.

## Each teammate, once per machine

The repository is private: Claude Code fetches it with your own git credentials.

```sh
gh auth login          # an account with access to jpchauny/claude-plugins
gh auth setup-git      # lets git (and so Claude Code) use it over HTTPS
```

Opening a project that declares the marketplace, accept the folder's trust dialog. If Claude Code reports that the plugin is enabled but not installed:

```sh
claude plugin install team-workflow@jpchauny-plugins --scope project
```

## Updates

Change a skill here, push to `main`. Updates are not automatic for a private marketplace: each teammate runs

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
