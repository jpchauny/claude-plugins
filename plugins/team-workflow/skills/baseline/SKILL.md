---
name: baseline
description: Declare a new baseline of pending work - a new root issue for the tree, with the still-open top-level items moved under it and the previous baseline closed as a dated snapshot. Use only when the user declares a baseline ("nueva línea de base", "esto es la línea de base") or says /team-workflow:baseline.
---

# baseline

A baseline is a dated root issue, `Línea de base YYYY-MM-DD`, labelled
`baseline`. A new one goes in the repository of the current baseline (the
`tree` script finds it from the session's repository); if there is none,
in the session's repository. Its children are the top-level
pending items; every bifurcation hangs further down, under the node where
it was found. At any time there is one open baseline: the current tree.

Only the user declares a baseline. The list of what goes into it is
proposed, and created after the user's yes.

## A new baseline

1. **Find the current one:** `issue_tree.py tree` prints it (or says
   there is none).
2. **Propose** the top-level items: the open children of the current
   baseline, plus any pending item the user names, each as one line with
   its state. Wait for the yes and its adjustments.
3. **Create the root.** Make sure the `baseline` label exists
   (`gh label create baseline --color 1f6f63 --description "Root of the
   pending-work tree" 2>/dev/null || true`), then
   `gh issue create -R <that repository> -t "Línea de base YYYY-MM-DD" -l baseline -F <body>`.
   Body: one paragraph on what this baseline is, and the line
   `Page: <artifact URL>` copied from the previous baseline, if it had one.
4. **Move or link** each approved item, keeping its subtree:
   `python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/issue_tree.py" link <new root URL> <item URL>`
   (`scripts/` of this plugin; a child that has a parent moves). New items
   are created with the `issue` skill first.
5. **Close the previous baseline** with a snapshot comment: the date, the
   items closed since it was opened, the items moved, and the items
   created during it. Then `gh issue close`.
6. Show the tree with the `tree` skill.
