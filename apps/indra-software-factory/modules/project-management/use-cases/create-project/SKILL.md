---
name: create-project
description: Start a new project from scratch in five layers - ask for its name and components, create on GitHub the repositories <project>-drafts, <project>-specs, <project>-norms, <project>-acceptance and <project>-code (or one <project>-code-<component> per component), and the orchestration repository <project>-orchestration and the tooling repository <project>-tooling, enable in each the modules of its layer, write the same project.json in all of them, and push the initial documents. Use when the user types /project-management:create-project, or says in words that they want to start a new project ("nuevo proyecto", "crear proyecto", "start a new project").
argument-hint: "[project name]"
---

# create-project

Creates the repositories of the five layers of a new project, as
[specs/layers.md](https://github.com/jpchauny/indra-software-factory/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md) requires (LAY-1), each with `development-methodology`, `utilities` and the module of its layer enabled (APP-6);
its orchestration repository, with `development-methodology`, `utilities` and
`workflow-orchestration` (LAY-11, ORC-5); and its tooling repository, an empty
Claude Code marketplace with `utilities` alone, developed with the meta
methodology, not with this app (LAY-14, CRP-4). The
`project.json` of the project is in every one (ORC-20). Its specification is
[specs/create-project.md](https://github.com/jpchauny/indra-software-factory/blob/main/apps/indra-software-factory/modules/project-management/use-cases/create-project/specs/create-project.md).

## 1. Ask

Ask in one message, numbered, with the default of each:

1. **Project name**, lowercase-dash (`billing`, `clean-language`). Skip if given as argument.
2. **More than one component** in layer 4? Default: no, and layer 4 is one repository `<project>-code`.
3. **GitHub owner**. Default: the logged-in account, `gh api user --jq .login`.
4. **Visibility** of the repositories. Default: private.
5. **Project folder**, where every repository is cloned. Default: the folder `<project>` in the current directory.
6. **Default done profile** of the acceptance units: `prototype`, `product` or `critical` ([ACU-19 and ACU-20](https://github.com/jpchauny/indra-software-factory/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md)). No default: the user chooses it, since choosing the rigour is choosing how much risk is accepted.

When the answer to 2 is yes, ask in a second message for the **names of the
components**, lowercase-dash, comma-separated (`api, web`): layer 4 is one
repository `<project>-code-<component>` per component. Layer 3 is always the
one repository `<project>-acceptance`, for every component (LAY-1). When fewer than two
names come, ask again for them, at least two. When the answer is no, ask for
no names.

The name and each component must match `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`.
When one does not, ask again for it alone, in lowercase-dash, before going on
to the check. When the profile is not one of the three, ask again for it
alone.

## 2. Check

Before anything is created, and stop with the reason if any fails:

- `gh auth status` succeeds, and its token has the scope `workflow`, without
  which GitHub refuses the push of `.github/workflows/` (ORC-3, CRP-1); when
  it lacks it, say to run `gh auth refresh -s workflow`.
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
              3 <owner>/<project>-acceptance  acceptance-management
              4 <owner>/<project>-code[-<c>]  code-implementation
              - <owner>/<project>-orchestration  workflow-orchestration
              (development-methodology and utilities enabled in every one above)
              - <owner>/<project>-tooling     the project's own plugins: a marketplace, utilities only
Folder:       <project folder>/<name of each repository>
Profile:      <default done profile> (acceptance.json of <project>-acceptance)
CI:           acceptance tests in <project>-acceptance, run every hour and on each push to its main
```

## 4. Create

1. Render the initial files, `project.json` included:
   ```sh
   python3 -I "${CLAUDE_PLUGIN_ROOT}/use-cases/create-project/scripts/scaffold.py" \
     --project <project> --owner <owner> --folder <project folder> \
     --profile <prototype|product|critical> [--components <a,b>]
   ```
   It prints, for each repository, a line `<layer> <name>`, or `orchestration
   <name>` and `tooling <name>` for the two repositories that are no layer, and
   then the files it wrote for it. It also writes the rules `deny` of ACU-13, level 1, in
   `.claude/settings.json`: the acceptance repository may not read or edit a
   code repository, and a code repository may not edit the acceptance
   repository (ORC-5). It writes `acceptance.json` in the acceptance repository
   (CRP-2), and the workflow of GitHub Actions of ACU-34 (CRP-1),
   `.github/workflows/acceptance.yml`, in the acceptance repository only: no
   code repository gets a workflow. The tooling repository gets
   `.claude-plugin/marketplace.json`, a marketplace named as the repository
   that lists no plugin yet (CRP-4); no repository of a layer names it in its
   `.claude/settings.json` until a person adds a plugin that the layer uses
   (LAY-14).
2. For each repository, in the order printed, in its folder:
   ```sh
   git init -b main    # the default branch is main (ORC-5)
   git add -- <each file the script printed for this repository>
   git commit -m "chore: start <name> (layer <layer> of <project>)"
   gh repo create <owner>/<name> --<visibility> --source . --push \
     --description "Layer <layer> of <project>: <what it holds>"
   ```
   For the two repositories that are no layer, the message is
   `chore: start <name> (<orchestration|tooling> repository of <project>)`,
   and the description `Orchestration repository of <project>: runs across
   the layers` or `Tooling repository of <project>: its own plugins`.

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
  breaks LAY-4 and LAY-8.
- On first opening each one, accept the folder's trust dialog; the plugins
  install from `.claude/settings.json`.
- The secret of the workflow (ORC-6, CRP-1), in these words, with the names
  of the repositories of the project; the skill creates no token and no secret:

  ```text
  The workflow of <project>-acceptance needs one secret, which I did not create. Add it on GitHub, in <project>-acceptance, Settings > Secrets and variables > Actions:
  - CODE_READ_TOKEN: a fine-grained token with read-only access to the contents of <each code repository, joined by ", " and " and ">, and to no other repository.
  ```
- Only when the visibility is public, right after it (ORC-6):

  ```text
  <project>-acceptance is public: GitHub disables its scheduled workflow after 60 days without activity in <project>-acceptance, and a push to a code repository is not activity there. When that happens, the acceptance tests stop running and record nothing; enable the workflow again in <project>-acceptance, Actions > acceptance.
  ```
- The acceptance tests run once `test_command` and `product` of
  `acceptance.json` are filled, when there is code to test (ACU-6); until
  then the workflow records nothing.
