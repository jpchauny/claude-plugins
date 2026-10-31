# Project management

**Prefix:** PRJ

**Audience:** The people who use the meta app; whoever builds a meta use case of the plugin `project-management`

**Scope:** The meta module `project-management`: the repositories of a project, the repositories of its five layers, its orchestration repository and its tooling repository, the project folder that holds them, their creation and their life cycle. Their creation is in [create-project.md](../use-cases/create-project/specs/create-project.md); keeping `project.json` and the rules deny in step is in [sync.md](../use-cases/sync/specs/sync.md)

The meta module `project-management` of the meta app Indra Software Factory, listed in [app.md](../../../specs/app.md).

## Terms

| Term | Meaning |
|---|---|
| Project | The repositories of its five layers ([LAY-1](../../development-methodology/specs/layers.md#rules)), its orchestration repository ([LAY-11](../../development-methodology/specs/layers.md#the-orchestration-repository)) and its tooling repository, when it has one ([LAY-14](../../development-methodology/specs/layers.md#the-tooling-repository)), as its `project.json` lists them (ORC-20). |
| Project folder | The folder that holds the repositories of a project, each at its `path` (ORC-20). Each person chooses it, and it is written nowhere. |

The terms repository of a layer, orchestration repository and tooling repository are those of [layers.md](../../development-methodology/specs/layers.md#terms).

<a id="use-cases"></a>

## Meta use cases

| Meta use case | Meta spec |
|---|---|
| `create-project` | [create-project.md](../use-cases/create-project/specs/create-project.md) |
| `sync` | [sync.md](../use-cases/sync/specs/sync.md) |

## Where the repositories are

- **ORC-20.** Every repository of a project holds at its root the file `project.json`, with the same bytes in all of them. Its fields are (complete list):
  - `project`: the name of the project;
  - `repositories`: one entry per repository of the project, with
    - `owner` and `name`: the repository on GitHub, `<owner>/<name>`, unique in the list;
    - `layer`: `0`, `1`, `2`, `3` or `4`, only in the entry of a repository of a layer;
    - `role`: `orchestration`, only in the entry of the orchestration repository ([LAY-11](../../development-methodology/specs/layers.md#the-orchestration-repository)), or `tooling`, only in the entry of the tooling repository ([LAY-14](../../development-methodology/specs/layers.md#the-tooling-repository));
    - `component`: the component of a repository of layer 4, only when layer 4 has one repository per component;
    - `path`: where the repository is, relative to the project folder, its parts separated by `/`, none of them empty, `.` or `..`;
  - `derived_norms`: optional; the types of derived norms of the project, in the order they are generated, one entry per type, with
    - `type`: the name of the folder of its output under `specs-derived/`, one or more lower-case ASCII letters, digits and `-`, unique in the list;
    - `use_case`: the meta use case that generates it, `/<module>:<use case>`, where `<module>` is a plugin of the tooling repository of the project ([LAY-14](../../development-methodology/specs/layers.md#the-tooling-repository), [NRM-1](../../norms-management/specs/module.md#derive-the-derived-norms)).

  The list holds exactly one entry of each of the layers 0, 1, 2 and 3, none of them with `component`. Layer 4 is either one entry without `component`, or one or more entries each with a different `component` ([LAY-1](../../development-methodology/specs/layers.md#rules)). The list holds exactly one entry with `role` `orchestration`, except a `project.json` written before the orchestration repository existed, which holds none (PRJ-2), and at most one entry with `role` `tooling` (PRJ-3); an entry with `role` has no `layer` and no `component`. Every other entry has `layer` and no `role`. For example:

  ```json
  {
    "project": "billing",
    "repositories": [
      { "owner": "acme", "name": "billing-drafts", "layer": 0, "path": "billing-drafts" },
      { "owner": "acme", "name": "billing-specs", "layer": 1, "path": "billing-specs" },
      { "owner": "acme", "name": "billing-norms", "layer": 2, "path": "billing-norms" },
      { "owner": "acme", "name": "billing-acceptance", "layer": 3, "path": "billing-acceptance" },
      { "owner": "acme", "name": "billing-api", "layer": 4, "component": "api", "path": "billing-api" },
      { "owner": "acme", "name": "billing-web", "layer": 4, "component": "web", "path": "billing-web" },
      { "owner": "acme", "name": "billing-orchestration", "role": "orchestration", "path": "billing-orchestration" },
      { "owner": "acme", "name": "billing-tooling", "role": "tooling", "path": "billing-tooling" }
    ],
    "derived_norms": [
      { "type": "grammar", "use_case": "/billing-grammar:derive-grammar" }
    ]
  }
  ```

  In the example, `billing-grammar` is a plugin of `acme/billing-tooling`.

  The recommended project folder is one folder named as the project, with each repository in a folder named as the repository, `path` equal to `name`.

  Rationale of `role`: an entry with no `layer` keeps every reader that looks for the entries of the layers by `layer` unchanged (PRJ-2), and `role` says what the entry is, not only what it is not.
- **ORC-21.** A skill finds the repository it runs in by its remote `origin`: the entry of `project.json` whose `<owner>/<name>` is the one of that remote. The project folder is the folder of that repository without its `path`. Every other repository is the project folder followed by its `path`. When no entry matches the remote `origin`, the skill writes nothing, and says that the repository is not in `project.json`.
- **ORC-22.** `project.json` is the only source of where the repositories are. When a repository is not at its `path`, the skill writes nothing, says which repository it did not find and where it expected it, and recommends the command `git clone https://github.com/<owner>/<name> <project folder>/<path>`. It never looks for the repository anywhere else, and never asks for its path.
- **ORC-23.** The copy of `project.json` in the repository of layer 1 is the only one that is edited, with the approval of a person ([LAY-2](../../development-methodology/specs/layers.md#rules)). Every other copy is written only by `/project-management:sync`, which copies it. A skill of layer 3 or 4 reads that copy as `specs-repo-annotated/project.json` of the repository of layer 2, where the norms generator copies it ([R62](../../norms-management/specs/norms-versions.md#data-and-outputs)), and never in layer 1 ([LAY-4 and LAY-8](../../development-methodology/specs/layers.md#rules)).
- **ORC-24.** Before it uses `project.json`, a skill compares its own copy with the copy of ORC-23, byte for byte. When they differ, it writes nothing, says that the two copies differ, and recommends `/project-management:sync`.

## The project folder

- **PRJ-1.** The project folder is no git repository. It holds the clone of each repository of the project, of the layers, the orchestration repository and the tooling repository alike, each at its `path` (ORC-20), and nothing that a skill writes. Deliberate design, as [LAY-11](../../development-methodology/specs/layers.md#the-orchestration-repository) says. Rationale: a project folder that was a repository would hold the clones of every layer in one history, under one set of permissions, which [LAY-1](../../development-methodology/specs/layers.md#rules) keeps apart by repository.

## The entry of the orchestration repository

- **PRJ-2.** Every meta use case and every hook of a meta module other than `workflow-orchestration` finds the repositories of the layers by the entries of `project.json` with `layer`, and neither requires nor refuses an entry with `role`, of the orchestration repository or of the tooling repository; `/project-management:sync` copies `project.json` to it as to every other repository ([SNC-2](../use-cases/sync/specs/sync.md#sync-projectjson)), and `/project-management:create-project` creates it ([ORC-5](../use-cases/create-project/specs/create-project.md#create-a-project)). A `project.json` without that entry, written before the orchestration repository existed, stays valid for all of them; only the meta use cases of `workflow-orchestration` need the entry, since they run only in the orchestration repository ([WFO-1](../../workflow-orchestration/specs/module.md#where-the-orchestrator-runs)). Migration of a project created before: a person creates the repository on GitHub, clones it into the project folder at its `path`, adds its entry to the copy of `project.json` of layer 1 as ORC-23 says, runs `/project-management:sync`, and enables the plugins of [APP-6](../../development-methodology/specs/layers.md#where-each-module-is-installed) in its `.claude/settings.json`. Rationale: the projects created before keep working with no change, and get their orchestration repository when a person decides it.

## The entry of the tooling repository

- **PRJ-3.** The entry of the tooling repository is optional in every `project.json`: no meta use case and no hook of the meta app requires it, and none refuses it (PRJ-2). `/project-management:create-project` creates the tooling repository of every new project ([CRP-4](../use-cases/create-project/specs/create-project.md#create-a-project)), and `/project-management:sync` copies `project.json` to it as to every other repository, and keeps no rule `deny` there ([SNC-3](../use-cases/sync/specs/sync.md#sync-projectjson)). Migration of a project created before: a person creates the repository on GitHub, clones it into the project folder at its `path`, writes in it the files of CRP-4, adds its entry to the copy of `project.json` of layer 1 as ORC-23 says, runs `/project-management:sync`, and then moves into it, as plugins, the project's own tools that the repositories of layers 0 to 3 held ([LAY-13](../../development-methodology/specs/layers.md#rules)). Rationale: a project whose derived-norms generators are plugins of another marketplace keeps working, and a project with no tool of its own needs no tooling repository; a new project gets one, so that its first tool has a place that is no layer.

## Open questions

1. Should a meta use case add the orchestration repository to a project created before it existed, instead of the steps of the migration of PRJ-2?
