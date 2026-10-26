# Norms management

**Prefix:** NRM

**Audience:** The people who run a project's flow from specs to code; whoever builds the skills of the plugin `norms-management`; whoever builds the generator of a type of derived norms

**Scope:** Layer 2: the norms and the derived norms. What each type of derived norms derives, and how, is in the spec of its generator

The module `norms-management` of the app Indra Software Factory, listed in [app.md](../../../specs/app.md).

## Terms

| Term | Meaning |
|---|---|
| Run | One pass of the flow from specs to code, for one commit of layer 1. |
| Step | The work of one layer in one run, done in the repository of that layer. |
| Hand-off | What a step gives the next one: a commit, a report, or an issue. |
| Norms generator | The program of this plugin that `/norms-management:build` and `/norms-management:verify` run, which writes `data/` and `specs-repo-annotated/`. |
| Derived-norms generator | The use case that a `derived_norms` entry of `project.json` names for one type ([ORC-20](../../project-management/specs/module.md#where-the-repositories-are)): a use case of a plugin that the project installs in its repository of layer 2. |
| Output of a type | Every file under `specs-derived/<type>/` of the repository of layer 2. |
| Status file | The one file of the output of a type, named by the spec of its derived-norms generator, that records how the output was made and the state of each item it derives. |
| Pending item | An item of the output of a type that the norms leave open ([LAY-5](../../development-methodology/specs/layers.md#rules)). |

## Regenerate the norms

- **ORC-34.** The skills of the module find the repository of layer 1 only through `project.json`, as [ORC-21 and ORC-22](../../project-management/specs/module.md#where-the-repositories-are) say, and the repository they run in must be the one of layer 2. There is no other way: no argument, no `CLAUDE.md`, no folder name.
- **ORC-8.** In the repository of layer 2, the step runs `/norms-management:build` at the commit of layer 1 that starts the run ([ORC-15](../../development-methodology/specs/flow.md#start-a-run)), then `/norms-management:verify`. A failure of either ends the run, with the norms generator's message shown as it is ([LAY-3](../../development-methodology/specs/layers.md#rules)).
- **ORC-9.** Its hand-off is the commit of the repository of layer 2 that holds the regenerated `data/`, `specs-repo-annotated/` and `specs-derived/` (NRM-9), and its `data/report.md`, which lists by norm ID what changed.
- **ORC-10.** When `data/report.md` shows no change of norm, the run ends after this step: there is nothing to implement.

## Derive the derived norms

A project may have derived norms of zero or more types, such as a grammar or a
semantics ([LAY-3](../../development-methodology/specs/layers.md#rules)). Each
type has its own derived-norms generator. The clauses below are the interface
that every derived-norms generator follows, whatever it derives.

- **NRM-1.** The derived norms of a project are the entries of `derived_norms` in its `project.json`, in their order. A project without `derived_norms` has none.
- **NRM-2.** When `/norms-management:build` and `/norms-management:verify` succeed, the step of layer 2 (ORC-8) runs the derived-norms generator of each type in the order of NRM-1, with no question to the user, also when the build changed no norm. A derived-norms generator that stops with an error does not stop the next one. A check that fails (NRM-5) is no error of its generator.
- **NRM-3.** A derived-norms generator takes the norms only from `data/tree.jsonl`, `specs-repo-annotated/` and the versions of `data/tree.jsonl` in the history of the repository, and never reads a file of layer 1. Besides the norms it reads only (complete list): the output of its type; the files of its own plugin; the record of the installed plugins of Claude Code and the git data of the checkout that holds its plugin (NRM-4); the issues of the repositories where it opens issues (NRM-7).
- **NRM-4.** A derived-norms generator writes in the repository only the output of its type.
- **NRM-5.** The first line of the status file is a JSON object with these fields, and with others only when the spec of its derived-norms generator names them (complete list of the fields every status file has):
  - `"type": "meta"`;
  - `"specs_commit"`: the commit of layer 1 that the meta line of `data/tree.jsonl` records;
  - `"generator"`: an object with exactly `"plugin"`, the name of the plugin of the derived-norms generator; `"version"`, the `version` of the plugin's `.claude-plugin/plugin.json`; and `"marketplace_commit"`, the commit of the marketplace that the plugin was installed from, as the spec of the derived-norms generator says how it is found, or `"none"`;
  - `"model"`: the exact model ID that ran the derived-norms generator;
  - one field `"<name>_sha256"` for each other file of the output, whose `<name>` the spec of the derived-norms generator gives, with the SHA-256 of that file.

  Every plugin with a derived-norms generator has a `version` in its `plugin.json`.
- **NRM-6.** Each derived-norms generator has a check, which fails when its output does not follow from the current `data/tree.jsonl`, when NRM-5 does not hold, or when its output holds a pending item.
- **NRM-7.** A derived-norms generator derives again only what a change of `data/tree.jsonl` calls for: an item whose norm changed, is new or is gone, and each part of the output that cites such a norm ([LAY-3](../../development-methodology/specs/layers.md#rules)).
- **NRM-8.** Each pending item gets its own issue in the repository of layer 1, opened at once by its derived-norms generator, with no question to the user ([LAY-5](../../development-methodology/specs/layers.md#rules)).
- **NRM-9.** After the last derived-norms generator, the step of layer 2 makes one commit of every changed file of `data/`, `specs-repo-annotated/` and `specs-derived/`, each added by its path, never a folder, and pushes it to the default branch, also when a check failed. When nothing changed, it makes no commit. Its message names the commit of layer 1, the plugin and version of each derived-norms generator, the norms that changed and the issues opened.
- **NRM-10.** When the push is rejected, the step runs `git pull --no-rebase --no-edit` and pushes again, once. It never runs `git stash`, `git reset --hard`, `git clean` or `git pull --rebase`: other sessions may work in the same repository.
- **NRM-11.** The step ends with one report: the norms that changed by norm ID (`data/report.md`), and, for each type in the order of NRM-1, its derived-norms generator with its version, what it derived, the issues it opened, the output of its check, and its error when it stopped with one.
