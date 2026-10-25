---
name: sync
description: Copy the project.json of the repository of layer 1 to every other repository of the project, after showing which copies differ and waiting for the user's yes; commits only project.json in each and pushes it. Use only when the user types /project-management:sync, or asks in words to sync project.json ("sincroniza project.json", "sync project.json").
---

# sync

Copies the `project.json` of the repository of layer 1 to every other
repository of the project. Its specification is
[specs/sync.md](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/project-management/use-cases/sync/specs/sync.md).

## 1. Plan

In the root of the current repository:

```sh
python3 -I "${CLAUDE_PLUGIN_ROOT}/use-cases/sync/scripts/plan.py" --repo "$(git rev-parse --show-toplevel)"
```

When it prints an `error`, write nothing and say it as it is (ORC-21, ORC-28).

## 2. Confirm

When every target is `same`, say that every copy is already the same, and
stop (ORC-30). Otherwise show one line per target, `to write`, `already the
same` or `skipped: <reason>`, and wait for the user's yes. Write nothing
before it.

## 3. Write

For each target `differs`, in the order printed, in its `path`:

```sh
cp "<source_file>" project.json
git add -- project.json
git commit -m "chore: sync project.json from <source_commit>"
git push origin HEAD:<branch>
```

When a command fails, the target is skipped with the error as its reason; go
on with the next one (ORC-32). Never retry, never force, never touch another
file.

## 4. Report

One line per target: `written`, `already the same` or `skipped: <reason>`
(ORC-33).
