# Development methodology

**Prefix:** MTH

**Audience:** The people who work in a repository of a project, and the Claude Code sessions there; whoever builds the plugin `development-methodology`

**Scope:** The meta module `development-methodology`: which of its meta specs are the development methodology of the meta app, how they link to the rest of the marketplace, and the hook that gives every session in a repository of a project an index of the methodology. The meta rules of the methodology are in [layers.md](layers.md) and [flow.md](flow.md), not here. Where the meta module is installed is [APP-6](layers.md#where-each-module-is-installed)

The meta module `development-methodology` of the meta app Indra Software Factory, listed in [app.md](https://github.com/jpchauny/indra-software-factory/blob/main/apps/indra-software-factory/specs/app.md).

Its purpose: a Claude Code session in any repository of a project, of one of the five layers or the orchestration repository ([LAY-11](layers.md#the-orchestration-repository)), knows the whole process, not only the work of its own repository, and can answer questions about it.

## Terms

| Term | Meaning |
|---|---|
| Methodology | The meta specs of this meta module that state how a project is specified and built (MTH-1). |
| Plugin root | The folder in which Claude Code installed the plugin `development-methodology`: the folder of this meta module, as the environment variable `CLAUDE_PLUGIN_ROOT` gives it to a hook. |
| Hook | The command that Claude Code runs on the event `SessionStart`, as the plugin declares it (MTH-4). |
| Index | The text that the hook prints, which Claude Code adds to the context of the session (MTH-6). |
| Table of layers | The table of [layers.md](layers.md) with the columns `Layer`, `Recommended name`, `Holds` and `Written by`, in this order. |
| Table of modules | The table of [APP-6](layers.md#where-each-module-is-installed), with the columns `Module` and `Where`, in this order. |

## The methodology

- **MTH-1.** The methodology is these meta specs of this meta module (complete list):
  - [layers.md](layers.md): the five layers, the orchestration repository, the tooling repository, their rules (the clauses LAY-n), their terms, and where each meta module is installed (APP-6);
  - [flow.md](flow.md): the run, its steps in order and their hand-offs (ORC-15), and the terms run, step and hand-off.
- **MTH-2.** The reason of a meta rule of the methodology is written with that meta rule, and in no other place ([DEV-4](https://github.com/jpchauny/indra-software-factory/blob/main/specs/development.md#method)). The methodology states only the reasons that its meta rules state; a meta rule without a stated reason is an open question of this meta spec.
- **MTH-3.** In every meta spec of this meta module, a link to a file inside the folder of the meta module is relative. A link to any other file of the marketplace is its absolute URL `https://github.com/jpchauny/indra-software-factory/blob/main/<path from the root of the repository>`, followed by its anchor when it has one. Deliberate design. Rationale: Claude Code installs only the folder of the plugin in the repository's sessions, so a relative link that leaves that folder points to no file there. The templates of the meta use case [create-project](https://github.com/jpchauny/indra-software-factory/blob/main/apps/indra-software-factory/modules/project-management/use-cases/create-project/specs/create-project.md) link to the marketplace in the same form.

## The index of every session

- **MTH-4.** The plugin has no meta use case and no skill ([DEV-7](https://github.com/jpchauny/indra-software-factory/blob/main/specs/development.md#levels)). It declares one hook, in `hooks/hooks.json` of the meta module, for the event `SessionStart`, with no matcher: the hook runs at every start of a session, new, resumed, forked, after `/clear` and after a compaction (complete list of the starts of a session that Claude Code reports). The hook declares nothing else.
- **MTH-5.** The hook runs the script `<plugin root>/scripts/index.py`, with Python 3.9 or later and its standard library only. The working directory of the script is the one that Claude Code gives it, and the script does not depend on it. Deliberate design: the other scripts of the meta app are Python 3 with the standard library only.
- **MTH-6.** When the script can read the table of layers, it prints the index to its standard output and exits with status 0. The index is these lines, in this order, each followed by one line feed (LF), UTF-8 without a byte order mark; a check must match it byte for byte:

  ```text
  Development methodology of Indra Software Factory (plugin development-methodology).
  This repository is one repository of a project: of one of its five layers, or its orchestration repository, which is no layer.
  The five layers:
  - <Layer>: <Holds>; written by: <Written by>; repository: <Recommended name>
  The modules of the app, each one a plugin, and where each is installed:
  - <Module>: <Where>
  Read for detail, before answering about the process:
  - The five layers, the orchestration repository, the tooling repository, their rules, their terms, and where each module is installed: <plugin root>/specs/layers.md
  - The flow across the layers (a run, its steps and hand-offs): <plugin root>/specs/flow.md
  - What carries the methodology to every repository: <plugin root>/specs/module.md
  - What each module of the app does: https://github.com/jpchauny/indra-software-factory/blob/main/apps/indra-software-factory/specs/app.md
  ```

  - The line that starts with `- <Layer>` is written once per row of the table of layers, in the order of the table, and only there.
  - The line that starts with `- <Module>` is written once per row of the table of modules, in the order of the table, and only there.
  - Each `<column>` is the text of that cell of the row, without the spaces around it, with every other character as it is in [layers.md](layers.md).
  - `<plugin root>` is the absolute path of the folder that holds the folder `scripts/` of the script, without a final `/`. The script finds it from its own path, not from the environment.

  Binding example, with the plugin root `/p` and the table of layers.md as it is: the fourth line of the index is

  ```text
  - 0. Drafts: The draft specs, in plain prose; written by: People; repository: `<project>-drafts`
  ```

  and the line after the five lines of the layers is

  ```text
  The modules of the app, each one a plugin, and where each is installed:
  ```

- **MTH-7.** The index restates no meta rule of the methodology: apart from the lines of the table of layers and of the table of modules, it holds only the paths and the URL of MTH-6 ([DEV-4](https://github.com/jpchauny/indra-software-factory/blob/main/specs/development.md#method)).
- **MTH-8.** When `<plugin root>/specs/layers.md` does not exist or cannot be read as UTF-8, or holds no table of layers or no table of modules, or one of them has no row, the script prints nothing to its standard output, prints to its standard error the line below followed by one LF, and exits with status 1. Claude Code then starts the session without the index.

  ```text
  development-methodology: cannot read the tables of layers and of modules in <plugin root>/specs/layers.md
  ```

- **MTH-9.** The script only reads the file `<plugin root>/specs/layers.md`. It must never write a file, run another program, read the repository of the session, or use the network.
- **MTH-10.** Every path that the index names exists in the installed plugin.

## Open questions

None.
