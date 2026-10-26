---
name: build
description: Regenerate layer 2 of the current project - mirror its whole layer 1 repository into specs-repo-annotated/ of this norms repository, Markdown annotated with stable norm IDs and every other file copied as it is, record the tree in data/, then verify the output, run every derived-norms generator of the project, commit and push layer 2, and show the change report. Use when the user says /norms-management:build, "regenera las normas", "regenerate layer 2", "build norms", or after layer 1 changed.
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

## 3. Derive the derived norms

Run each derived-norms generator of the project, in the order of its
`project.json` (NRM-1, NRM-2), with no question to the user, also when the
build changed no norm:

```sh
python3 -I -c 'import json; [print(e["type"], e["use_case"]) for e in json.load(open("project.json")).get("derived_norms", [])]'
```

Each line is `<type> /<module>:<use case>`. Invoke each use case, in that
order, with the Skill tool (`<module>:<use case>`), and follow it to its end
before the next one. When a use case stops with an error, note it and go on
with the next one; a check that fails is no error (NRM-2). No line: the
project has no derived norms.

## 4. Commit and push

Run it on the default branch (`B`, the branch of `origin/HEAD`). One commit of every changed file of `data/`, `specs-repo-annotated/` and
`specs-derived/`, each by its path, never a folder (NRM-9), also when a check
failed:

```sh
git ls-files -z --modified --deleted --others --exclude-standard -- data specs-repo-annotated specs-derived \
  | xargs -0 git add --
git diff --cached --stat
git diff --cached --quiet || git commit -F <scratchpad>/commit-message.txt
B=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##'); B=${B:-$(git branch --show-current)}
git push origin "$B" || { git pull --no-rebase --no-edit origin "$B" && git push origin "$B"; }
```

Before the commit, `git diff --cached --stat` lists only those three folders;
take anything else out with `git restore --staged <file>`. The message names
the commit of layer 1, the plugin and version of each derived-norms generator
(from the meta line of its status file), the norms that changed (from
`data/report.md`) and the issues opened. Never `git stash`, `git reset
--hard`, `git clean` or `git pull --rebase` (NRM-10). When nothing is staged,
make no commit, and push anyway.

## 5. Report

One report (NRM-11): the norms that changed by norm ID (`data/report.md`);
for each type in order, its generator with its version, what it derived, the
issues it opened, the output of its check and its error, if any; and the
commit pushed, or the error of the push.
