---
name: sync
description: Copy the project.json of the repository of layer 1 to every other repository of the project, and keep the rules deny of layers 3 and 4 in step with it, after showing which copies differ and waiting for the user's yes; commits only project.json, and apart .claude/settings.json, in each and pushes it. Use only when the user types /project-management:sync, or asks in words to sync project.json ("sincroniza project.json", "sync project.json").
---

# sync

Copies the `project.json` of the repository of layer 1 to every other
repository of the project, and keeps the rules `deny` of the repositories of
layers 3 and 4 in step with it (SNC-1). Its meta spec is
[specs/sync.md](https://github.com/jpchauny/indra-software-factory/blob/main/apps/indra-software-factory/modules/project-management/use-cases/sync/specs/sync.md).

## 1. Plan

In the root of the current repository:

```sh
python3 -I "${CLAUDE_PLUGIN_ROOT}/use-cases/sync/scripts/plan.py" --repo "$(git rev-parse --show-toplevel)"
```

When it prints an `error`, write nothing and say it as it is (ORC-21, ORC-28).

Each target of layer 3 or 4 also has `settings_state`: `differs` (with
`deny`, the new rules `deny`, and `settings_file`, the whole new
`.claude/settings.json`), `same`, or `skipped` with `settings_reason`. The
managed rules (`Read` or `Edit` of the folder of a repository of layer 3 or
4 of the source, of the target's `project.json` before the sync, or of any
version of it committed in the target) are
replaced; any other rule `deny` is kept unchanged (SNC-1).
The orchestration repository and the tooling repository, the entries with
`role`, are targets of `project.json` only: their `.claude/settings.json` is
never changed (SNC-2, SNC-3).

## 2. Confirm

When every target is `same` and no `settings_state` is `differs`, say that
every copy is already the same, and stop (ORC-30). Otherwise show one line
per target, `to write`, `already the same` or `skipped: <reason>`, and for
each `settings_state` `differs` the diff of its settings,
`git diff --no-index -- <path>/.claude/settings.json <settings_file>`, and
wait for the user's yes. Write nothing before it.

## 3. Write

For each target `differs`, in the order printed, in its `path`:

```sh
cp "<source_file>" project.json
git add -- project.json
git commit -m "chore: sync project.json from <source_commit>"
git push origin HEAD:<branch>
```

Then, for each target whose `settings_state` is `differs` and whose
`project.json` was written or already the same in this run, in its `path`,
after its `project.json` (SNC-1). A target whose `project.json` was skipped,
in the plan or by a command above that failed, such as a refused push, gets
no write of its `.claude/settings.json` (ORC-33):

```sh
cp "<settings_file>" .claude/settings.json
git add -- .claude/settings.json
git commit -m "chore: sync deny rules from <source_commit>"
git push origin HEAD:<branch>
```

When a command fails, the target is skipped with the error as its reason; go
on with the next one (ORC-32). Never retry, never force, never touch another
file.

## 4. Report

One line per target for its `project.json`: `written`, `already the same` or
`skipped: <reason>` (ORC-33); and for a target of layer 3 or 4 whose
`project.json` was not skipped, the same for its rules `deny`. When a command
of the commit of `.claude/settings.json` fails, only its rules `deny` are
`skipped`.
Then remove the temporary files that the plan printed.
