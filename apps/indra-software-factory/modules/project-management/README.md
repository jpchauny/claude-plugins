# project-management

The module `project-management` of Indra Software Factory: the
repositories of a project, their creation and their life cycle. Its use cases
are specified in [specs/](specs/).

## Use cases

- `/project-management:create-project [name]` ([spec](use-cases/create-project/specs/create-project.md)): asks for
  the name, components, owner, visibility, project folder and default done profile, then creates on GitHub
  `<project>-drafts`, `<project>-specs`, `<project>-norms`, `<project>-acceptance` and `<project>-code` (or one `<project>-code-<component>` per component), each with
  `.claude/settings.json` enabling `development-methodology`, `utilities` and the module of its layer, a `CLAUDE.md`, a `README.md` and the `project.json` of the project; the acceptance repository and the code repositories also get the rules `deny` that keep every session of layer 3 out of the code repositories and keep layer 4 from writing the acceptance repository
  ([LAY-1](../development-methodology/specs/layers.md#rules)); the acceptance repository also gets `acceptance.json` with the default done profile chosen, and the workflow of GitHub Actions that runs the acceptance tests every hour and on each push to its `main` that changes a file outside `records/` ([ACU-34](../acceptance-management/specs/module.md)), reading the head of each code repository with a read-only token; no code repository gets a workflow or a credential of the acceptance repository.
- `/project-management:sync` ([spec](use-cases/sync/specs/sync.md)): run in the repository of layer 1, copies its `project.json` to every other repository of the project, and keeps the rules `deny` of the repositories of layers 3 and 4 in step with it, after showing what differs and waiting for the user's yes.

Code that both use cases share, the rules `deny` of ORC-5, is in [scripts/](scripts/).

The initial files are in [templates/](use-cases/create-project/templates/), one folder per layer, `drafts`, `specs`, `norms`, `acceptance` and `code`.
