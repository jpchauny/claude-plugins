---
name: create-project
description: Start a new project from scratch in four layers - ask for its name and components, create on GitHub the repositories <project>-drafts, <project>-specs, <project>-norms and <project>-code (or one <project>-code-<component> per component), enable in each the modules of its layer, write the same project.json in all of them, and push the initial documents. Use when the user types /project-management:create-project, or says in words that they want to start a new project ("nuevo proyecto", "crear proyecto", "start a new project").
argument-hint: "[project name]"
---

# create-project

Creates the repositories of the four layers of a new project, as
[specs/layers.md](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/specs/layers.md) requires (LAY-1), each with `utilities` and the module of its layer enabled (APP-6), and the
`project.json` of the project in every one (ORC-20). Its specification is
[specs/create-project.md](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/project-management/use-cases/create-project/specs/create-project.md).

## 1. Ask

Ask in one message, numbered, with the default of each:

1. **Project name**, lowercase-dash (`billing`, `clean-language`). Skip if given as argument.
2. **Components** of layer 3, lowercase-dash, comma-separated (`api, web`). Default: none, and layer 3 is one repository `<project>-code`.
3. **GitHub owner**. Default: the logged-in account, `gh api user --jq .login`.
4. **Visibility** of the repositories. Default: private.
5. **Project folder**, where every repository is cloned. Default: the folder `<project>` in the current directory.

The name and each component must match `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`.
When one does not, ask again for it alone, in lowercase-dash, before going on
to the check.

## 2. Check

Before anything is created, and stop with the reason if any fails:

- `gh auth status` succeeds.
- None of the repositories exists: `gh repo view <owner>/<name>` fails for each.
- The project folder does not exist.

## 3. Confirm

Creating repositories on GitHub is outward-facing. Show the plan and wait for
the user's yes:

```text
Project:      <project>
Owner:        <owner> (<visibility>)
Repositories  0 <owner>/<project>-drafts      specs-management
              1 <owner>/<project>-specs       specs-management
              2 <owner>/<project>-norms       norms-management
              3 <owner>/<project>-code[-<c>]  code-implementation
              (utilities enabled in every one)
Folder:       <project folder>/<name of each repository>
```

## 4. Create

1. Render the initial files, `project.json` included:
   ```sh
   python3 -I "${CLAUDE_PLUGIN_ROOT}/use-cases/create-project/scripts/scaffold.py" \
     --project <project> --owner <owner> --folder <project folder> \
     [--components <a,b>]
   ```
   It prints, for each repository, a line `<layer> <name>` and then the files
   it wrote for it.
2. For each repository, in the order printed, in its folder:
   ```sh
   git init -b main
   git add -- <each file the script printed for this repository>
   git commit -m "chore: start <name> (layer <layer> of <project>)"
   gh repo create <owner>/<name> --<visibility> --source . --push \
     --description "Layer <layer> of <project>: <what it holds>"
   ```

If any command of this step fails, stop at once: do not retry, do not go on
to another repository, and remove nothing, neither on GitHub nor locally.
Report instead of step 5:

- the error, as the command printed it;
- the repositories that exist on GitHub, with their URLs;
- the local folders that exist, and for each whether it has a commit and a
  remote.

## 5. Report

The URL of every repository, and:

- Open each repository **alone** in its own VS Code window. A folder added to
  the same workspace becomes readable and writable from the session, which
  breaks LAY-4.
- On first opening each one, accept the folder's trust dialog; the plugins
  install from `.claude/settings.json`.
