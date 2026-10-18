# new-project

Starts a new project from scratch: `/new-project:new-project [name]` asks for
its name, owner, visibility and local folder, then creates on GitHub
`<project>-specs`, `<project>-norms` and `<project>-code`, each with
`.claude/settings.json` enabling `shared` and the plugin of its layer, a
`CLAUDE.md` and a `README.md` ([LAY-1](../../spec-driven-design-process/layers.md#lay-1--every-project-has-three-layers-in-three-repositories)).

Install it once per person, at user scope; it is not enabled in any project:

```sh
claude plugin install new-project@jpchauny-plugins --scope user
```

The initial files are in [templates/](templates/), one folder per layer.
