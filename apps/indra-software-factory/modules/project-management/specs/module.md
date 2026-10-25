# Project management

**Audience:** The people who use the app; whoever builds a use case of the plugin `project-management`

**Scope:** The module `project-management`: the repositories of a project, their creation and their life cycle. For now, only their creation is specified

The module `project-management` of the app Indra Software Factory, listed in [app.md](../../../specs/app.md).

## Terms

| Term | Meaning |
|---|---|
| Project | The repositories of its four layers ([LAY-1](../../../specs/layers.md#lay-1--every-project-has-four-layers-each-in-its-own-repositories)), as its `project.json` lists them (ORC-20). |
| Project folder | The folder that holds the repositories of a project, each at its `path` (ORC-20). Each person chooses it, and it is written nowhere. |

## Use cases

| Use case | Spec |
|---|---|
| `create-project` | [create-project.md](../use-cases/create-project/specs/create-project.md) |
| `sync` | [sync.md](../use-cases/sync/specs/sync.md) |

## Where the repositories are

- **ORC-20.** Every repository of a project holds at its root the file `project.json`, with the same bytes in all of them. Its fields are (complete list):
  - `project`: the name of the project;
  - `repositories`: one entry per repository of the project, with
    - `owner` and `name`: the repository on GitHub, `<owner>/<name>`, unique in the list;
    - `layer`: `0`, `1`, `2` or `3`;
    - `component`: the component of a repository of layer 3, only when layer 3 has one repository per component;
    - `path`: where the repository is, relative to the project folder, its parts separated by `/`, none of them empty, `.` or `..`.

  The list holds exactly one entry of each of the layers 0, 1 and 2. Layer 3 is either one entry without `component`, or one or more entries each with a different `component` ([LAY-1](../../../specs/layers.md#lay-1--every-project-has-four-layers-each-in-its-own-repositories)). For example:

  ```json
  {
    "project": "billing",
    "repositories": [
      { "owner": "acme", "name": "billing-drafts", "layer": 0, "path": "billing-drafts" },
      { "owner": "acme", "name": "billing-specs", "layer": 1, "path": "billing-specs" },
      { "owner": "acme", "name": "billing-norms", "layer": 2, "path": "billing-norms" },
      { "owner": "acme", "name": "billing-api", "layer": 3, "component": "api", "path": "billing-api" },
      { "owner": "acme", "name": "billing-web", "layer": 3, "component": "web", "path": "billing-web" }
    ]
  }
  ```

  The recommended project folder is one folder named as the project, with each repository in a folder named as the repository, `path` equal to `name`.
- **ORC-21.** A skill finds the repository it runs in by its remote `origin`: the entry of `project.json` whose `<owner>/<name>` is the one of that remote. The project folder is the folder of that repository without its `path`. Every other repository is the project folder followed by its `path`. When no entry matches the remote `origin`, the skill writes nothing, and says that the repository is not in `project.json`.
- **ORC-22.** `project.json` is the only source of where the repositories are. When a repository is not at its `path`, the skill writes nothing, says which repository it did not find and where it expected it, and recommends the command `git clone https://github.com/<owner>/<name> <project folder>/<path>`. It never looks for the repository anywhere else, and never asks for its path.
- **ORC-23.** The copy of `project.json` in the repository of layer 1 is the only one that is edited, with the approval of a person ([LAY-2](../../../specs/layers.md#lay-2--people-work-in-layers-0-and-1)). Every other copy is written only by `/project-management:sync`, which copies it. A skill of layer 3 reads that copy as `specs-repo-annotated/project.json` of the repository of layer 2, where the norms generator copies it ([R62](../../norms-management/specs/norms-versions.md#data-and-outputs)), and never in layer 1 ([LAY-4](../../../specs/layers.md#lay-4--layer-3-reads-layer-2-never-layer-1)).
- **ORC-24.** Before it uses `project.json`, a skill compares its own copy with the copy of ORC-23, byte for byte. When they differ, it writes nothing, says that the two copies differ, and recommends `/project-management:sync`.
