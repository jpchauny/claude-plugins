# project-management

The module `project-management` of Indra Software Factory: the
repositories of a project, their creation and their life cycle. Its use cases
are specified in [specs/](specs/).

## Use cases

- `/project-management:create-project [name]` ([spec](use-cases/create-project/specs/create-project.md)): asks for
  the name, components, owner, visibility and project folder, then creates on GitHub
  `<project>-drafts`, `<project>-specs`, `<project>-norms` and `<project>-code` (or one `<project>-code-<component>` per component), each with
  `.claude/settings.json` enabling `utilities` and the module of its layer, a `CLAUDE.md`, a `README.md` and the `project.json` of the project
  ([LAY-1](../../specs/layers.md#lay-1--every-project-has-four-layers-each-in-its-own-repositories)).

The initial files are in [templates/](use-cases/create-project/templates/), one folder per layer, `drafts`, `specs`, `norms` and `code`.
