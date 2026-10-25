---
name: build
description: Regenerate layer 2 of the current project - mirror its whole layer 1 repository into specs-repo-annotated/ of this norms repository, Markdown annotated with stable norm IDs and every other file copied as it is, record the tree in data/, then verify the output and show the change report. Use when the user says /norms-management:build, "regenera las normas", "regenerate layer 2", "build norms", or after layer 1 changed.
argument-hint: "[--commit SHA]"
---

# build

Brings the norms of layer 2 up to date with one commit of layer 1
([LAY-3](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).
Run it from the norms repository of the project: the output goes to the root
of the git repository of the working directory.

## 1. Find layer 1

Only through `project.json` (ORC-34), with the script of this plugin:

```sh
python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/find_layer1.py" --repo "$(git rev-parse --show-toplevel)"
```

It prints the absolute path of the repository of layer 1, or an error. It
also checks that this repository's `project.json` is the same as the one of
layer 1 (ORC-24). On an
error, write nothing, show it as it is and stop: never look for layer 1
anywhere else, and never ask for its path (ORC-22).

## 2. Build, verify, report

```sh
uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}" norms-gen build --specs <layer 1> [--commit <SHA>]
uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}" norms-gen verify --specs <layer 1>
```

`build` reads layer 1 through git at the commit (default `HEAD`), never from
its working tree, so uncommitted changes there are not built. On a non-zero
exit, show its message as it is and stop: the meaning of each status is in
the generator's spec,
[R62](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/norms-management/specs/norms-versions.md).

## 3. Show

- `git status --short -- data specs-repo-annotated`: what changed in this repository.
- `data/report.md`: what changed since the previous version, by norm ID.

Commit only when the user asks, and only `data/` and `specs-repo-annotated/`, by
explicit path.
