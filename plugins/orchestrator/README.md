# orchestrator

Works above the three layers, across the three repositories of a project.

## Tools

- `/orchestrator:new-project [name]` starts a new project from scratch: asks for
its name, owner, visibility and local folder, then creates on GitHub
`<project>-specs`, `<project>-norms` and `<project>-code`, each with
`.claude/settings.json` enabling `shared` and the plugin of its layer, a
`CLAUDE.md` and a `README.md` ([LAY-1](specs/layers.md#lay-1--every-project-has-three-layers-in-three-repositories)).

Install it once per person, at user scope; it is not enabled in any project:

```sh
claude plugin install orchestrator@jpchauny-plugins --scope user
```

The initial files are in [templates/](templates/), one folder per layer.
