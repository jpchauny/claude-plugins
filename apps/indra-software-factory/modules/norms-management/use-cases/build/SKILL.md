---
name: build
description: Regenerate layer 2 of the current project - mirror its whole layer 1 repository into specs-repo-annotated/ of this norms repository, Markdown annotated with stable norm IDs and every other file copied as it is, record the tree in data/, then verify the output, run every derived-norms generator of the project, commit and push layer 2, and show the change report, with the norms and the derived norms that changed. Use when the user says /norms-management:build, "regenera las normas", "regenerate layer 2", "build norms", or after layer 1 changed.
argument-hint: "[--commit SHA]"
---

# build

Brings the norms of layer 2 up to date with one commit of layer 1
([LAY-3](https://github.com/jpchauny/indra-software-factory/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).
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
the generator's meta spec,
[R62](https://github.com/jpchauny/indra-software-factory/blob/main/apps/indra-software-factory/modules/norms-management/specs/norms-versions.md).

## 3. Derive the derived norms

Run each derived-norms generator of the project, in the order of its
`project.json` (NRM-1, NRM-2), with no question to the user, also when the
build changed no norm:

```sh
python3 -I -c 'import json; [print(e["type"], e["use_case"]) for e in json.load(open("project.json")).get("derived_norms", [])]'
```

Each line is `<type> /<module>:<use case>`. Invoke each meta use case, in that
order, with the Skill tool (`<module>:<use case>`), and follow it to its end
before the next one. When a meta use case stops with an error, note it and go on
with the next one; a check that fails is no error (NRM-2). No line: the
project has no derived norms. Each `<module>` is a meta module, a plugin of the tooling
repository of the project, which `.claude/settings.json` of this repository
enables (LAY-14); when its meta use case is not available in the session, that is
an error of its generator: note it and go on.

Then, also when the project has no derived norms and when a meta use case
stopped with an error, write the record of the types of derived norms
(`specs-derived/types-of-derived-norms.json`, NRM-16) with the script of
this plugin:

```sh
python3 -I "${CLAUDE_PLUGIN_ROOT}/use-cases/build/write_types_of_derived_norms.py" --norms-repository "$(git rev-parse --show-toplevel)"
```

On exit status 1, show its line as it is and go on: the record of the
working tree is left as it was (NRM-16).

## 4. Commit and push

Run it on the default branch (`B`, the branch of `origin/HEAD`). One commit of every changed file of `data/`, `specs-repo-annotated/` and
`specs-derived/`, each by its path, never a folder (NRM-9), also when a check
failed:

```sh
git ls-files -z --modified --deleted --others --exclude-standard -- data specs-repo-annotated specs-derived \
  | xargs -0 git add --
git diff --cached --stat
git diff --cached --quiet || git commit -F <scratchpad>/commit-message.txt
echo "COMMIT=$(git rev-parse HEAD)"
B=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##'); B=${B:-$(git branch --show-current)}
git push origin "$B" || { git pull --no-rebase --no-edit origin "$B" && git push origin "$B"; }
```

Before the commit, `git diff --cached --stat` lists only those three folders;
take anything else out with `git restore --staged <file>`. The message names
the commit of layer 1, the plugin and version of each derived-norms generator
(from the header line of its status file), the norms that changed (from
`data/report.md`) and the issues opened. Never `git stash`, `git reset
--hard`, `git clean` or `git pull --rebase` (NRM-10). When nothing is staged,
make no commit, and push anyway. Note the value of `COMMIT` for step 5,
since each command runs in a shell of its own: it is the commit of layer 2
of the run (ORC-9), the head right after the commit and before the push,
which is the head from before the step when no commit was made. Never take
the head after the push: after a pull it is the merge commit, or a commit
that the pull brought, and step 5 would then miss the derived norms that
this step changed (NRM-11).

## 5. Compare the derived norms

A script, never the model, compares the list of derived norms
(`specs-derived/<type>/derived-norms.jsonl`, NRM-12) of each type at the
commit of layer 2 of the run with the list at the commit before the last
step, the first parent of the last commit of the step of layer 2 along the
first parents (NRM-11), also when the step made no commit. It also checks
each derived norm of the commit of layer 2 of the run against the norm hashes
of `data/tree.jsonl` there: a derived norm behind its norms makes its list
unreadable, and the run stops (NRM-11, rule 5):

```sh
python3 -I "${CLAUDE_PLUGIN_ROOT}/use-cases/build/compare_derived_norms.py" --norms-repository "$(git rev-parse --show-toplevel)" --commit <COMMIT>
```

Its lines are those of NRM-11, rule 7: one line or more per type, then the
change of the order of the types, if any, and last `derived norms cannot be
read`, `derived norms changed: yes` or `derived norms changed: no`. Use its
output as it is, never rewritten. On exit status 1 it writes one line on
standard error, which says why the derived norms cannot be compared: show it
as it is.

## 6. Report

One report (NRM-11): the norms that changed by norm ID (`data/report.md`);
for each type in order, its generator with its version, what it derived, the
derived norms that changed (the output of step 5), the issues it opened, the
output of its check and its error, if any; and the commit pushed, or the
error of the push.

This report and the commit are the hand-off of layer 2 (ORC-9). End it with
exactly one of these lines, by the first case that holds (NRM-11, ORC-10):

1. step 5 exited with status 1, or its last line is `derived norms cannot be
   read`:
   `The run stops after layer 2: the derived norms cannot be read (ORC-10).`
2. `data/report.md` shows no change of norm and the last line of step 5 is
   `derived norms changed: no`:
   `The run ends after layer 2: no norm, no derived norm and no order of the types of derived norms changed (ORC-10).`
3. otherwise: `Layers 3 and 4 follow (ORC-10).`
