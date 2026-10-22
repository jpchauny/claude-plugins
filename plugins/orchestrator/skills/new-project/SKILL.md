---
name: new-project
description: Start a new project from scratch in three layers - ask for its name, create on GitHub its three repositories <project>-specs, <project>-norms and <project>-code, enable in each the plugins of its layer, and write and push the initial documents. Use when the user says /new-project, "nuevo proyecto", "crear proyecto", "scaffold", "start a new project".
argument-hint: "[project name]"
---

# new-project

Creates the three repositories of a new project, as
[plugins/orchestrator/specs/layers.md](https://github.com/jpchauny/claude-plugins/blob/main/plugins/orchestrator/specs/layers.md) requires (LAY-1): one per
layer, each with the plugins of its layer enabled.

## 1. Ask

Ask in one message, numbered, with the default of each:

1. **Project name**, lowercase-dash (`billing`, `clean-language`). Skip if given as argument.
2. **GitHub owner**. Default: the logged-in account, `gh api user --jq .login`.
3. **Visibility** of the three repositories. Default: private.
4. **Local folder** where the three clones go side by side. Default: the current directory.

## 2. Check

Before anything is created, and stop with the reason if any fails:

- `gh auth status` succeeds.
- None of the three names exists: `gh repo view <owner>/<project>-<layer>` fails for each.
- None of the three local folders exists.

## 3. Confirm

Creating repositories on GitHub is outward-facing. Show the plan and wait for
the user's yes:

```text
Project:     <project>
Owner:       <owner> (<visibility>)
Repositories <owner>/<project>-specs   plugins: shared, specs
             <owner>/<project>-norms   plugins: shared, norms
             <owner>/<project>-code    plugins: shared, code
Local:       <folder>/<project>-{specs,norms,code}
```

## 4. Create

1. Render the initial files:
   ```sh
   python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/scaffold.py" --project <project> --owner <owner> --out <folder>
   ```
2. For each layer, in its folder:
   ```sh
   git init -b main
   git add -- <each file the script printed for this layer>
   git commit -m "chore: start <project>-<layer> (layer N of <project>)"
   gh repo create <owner>/<project>-<layer> --<visibility> --source . --push \
     --description "<layer N of <project>: what it holds>"
   ```

## 5. Report

The three repository URLs, and:

- Open each repository **alone** in its own VS Code window. A folder added to
  the same workspace becomes readable and writable from the session, which
  breaks LAY-4.
- On first opening each one, accept the folder's trust dialog; the plugins
  install from `.claude/settings.json`.
