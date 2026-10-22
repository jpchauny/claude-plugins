---
name: build
description: Regenerate layer 2 of the current project - mirror its whole layer 1 repository into specs-repo-annotated/ of this norms repository, Markdown annotated with stable norm IDs and every other file copied as it is, record the tree in data/, then verify the output and show the change report. Use when the user says /norms-management:build, "regenera las normas", "regenerate layer 2", "build norms", or after layer 1 changed.
argument-hint: "[path of the layer 1 repository] [--commit SHA]"
---

# build

Regenerates layer 2 whole from one commit of layer 1
([LAY-3](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/specs/layers.md#lay-3--layer-2-is-regenerated-whole-from-layer-1-only)).
Run it from the norms repository of the project: the output goes to the root
of the git repository of the working directory.

## 1. Find layer 1

The first that applies:

1. The path given as argument.
2. The layer 1 repository named in this repository's `CLAUDE.md` or `README.md`.
3. The sibling folder `../<project>-specs`, where `<project>` is this repository's folder name without `-norms`.
4. Otherwise ask the user for the path, in one line.

## 2. Build, verify, report

```sh
uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}" norms-gen build --foundation <layer 1> [--commit <SHA>]
uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}" norms-gen verify --foundation <layer 1>
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
