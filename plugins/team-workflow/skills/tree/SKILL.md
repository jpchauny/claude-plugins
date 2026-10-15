---
name: tree
description: Show the tree of pending work (the current baseline issue and its sub-issues, across repositories) as a one-line summary, a text tree in the chat and a link to the same view as a page. Use only when the user asks to see the tree, the pending items, what waits for them, or says /team-workflow:tree. Never show it unasked.
---

# tree

Shows the pending-work tree only when the user asks. Never at the start of
a session and never unasked.

## Where the tree lives

The root is the open issue labelled `baseline` in the project's **home
repository**. The project's `CLAUDE.md` names it in a section
`## Issue tree` (for example, "baseline issues live in
Ivan-Pasco/clean-language-foundation"). If there is no such section, ask
the user which repository holds it.

## Steps

1. Run the script of this plugin (`scripts/`, two directories above this
   skill's base directory):
   ```sh
   python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/issue_tree.py" tree <owner/repo> \
       [--tema <name>] --html "<scratchpad>/arbol-pendientes.html"
   ```
   `--tema` when the user asks for one subject only (`tema:<name>`
   labels).
2. Show the user what it prints:
   - the summary line;
   - the tree. When the user asked for one branch or subject, show only
     that branch. The full tree only when they asked for everything;
   - the legend line.
3. Publish the page and give its link. The baseline issue's body ends with
   a line `Page: <artifact URL>`. If that line exists, publish the HTML
   file to that URL (`url`); if not, publish it as a new artifact
   (`icon: "tree"`) and append the line to the baseline issue's body with
   `gh issue edit -F`. The page is private to its owner; say so if someone
   else is meant to see it.

What the caller's GitHub account cannot see does not appear: each person
sees the part of the tree their access allows.
