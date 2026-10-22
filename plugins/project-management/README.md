# project-management

The module `project-management` of Indra Software Factory: the three
repositories of a project, their creation and their life cycle. Its use cases
are specified in [specs/](specs/).

## Use cases

- `/project-management:create-project [name]` ([spec](specs/create-project.md)): asks for
  the name, owner, visibility and local folder, then creates on GitHub
  `<project>-specs`, `<project>-norms` and `<project>-code`, each with
  `.claude/settings.json` enabling the app, a `CLAUDE.md` and a `README.md`
  ([LAY-1](../../specs/layers.md#lay-1--every-project-has-three-layers-in-three-repositories)).

The initial files are in [templates/](templates/), one folder per layer.
