---
name: tree
description: Show the tree of pending work (the current baseline issue and its sub-issues, across repositories) in the chat - a one-line summary and a text tree; a page only when the user explicitly asks for it. Use only when the user asks to see the tree, the pending items, what waits for them, or says /shared:tree. Never show it unasked.
---

# tree

Shows the pending-work tree only when the user asks. Never at the start of
a session and never unasked.

## Where the tree lives

The root is the current baseline: an open issue labelled `baseline`. The
script finds it from the repository where the session runs, by climbing
the parents of that repository's open issues, so it can live in another
repository. Nothing is configured, and the user is never asked which
repository to use. If the repository has no pending items in any
baseline, say so.

## Steps

1. Run the script of this plugin (`scripts/`, two directories above this
   skill's base directory):
   ```sh
   python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/issue_tree.py" tree [--tema <name>]
   ```
   `--tema` when the user asks for one subject only (`tema:<name>`
   labels).
2. Show the user what it prints, in the chat:
   - the summary line;
   - the whole tree of the baseline, across repositories (the default);
     only one branch or subject when the user asks for it;
   - the legend line.

   That is all. Do not write or publish a page.

## The page, only when asked

Only when the user explicitly asks for the page ("crea la página",
"publícala", "show it as a page"):

1. Run the same command with `--html "<scratchpad>/arbol-pendientes.html"`.
2. If the baseline issue's body ends with a line `Page: <artifact URL>`,
   publish the HTML file to that URL (`url`); if not, publish it as a new
   artifact (`icon: "tree"`) and append the line to the baseline issue's
   body with `gh issue edit -F`.
3. Give the link. The page is private to its owner; say so if someone
   else is meant to see it.

What the caller's GitHub account cannot see does not appear: each person
sees the part of the tree their access allows.
