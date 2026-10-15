---
name: issue
description: Propose, and after the user's yes open, a GitHub issue for a pending item or a finding (a "bifurcation") the moment it appears, linked as a sub-issue of the node where it was found and carrying a hand-off prompt. Use whenever work is left undone, something is found wrong, or a decision of the user is needed, and when the user says /team-workflow:issue, "anótalo", "abre una issue", "crea un issue".
---

# issue

Every pending item or finding that the current change does not resolve
goes into the **tree of issues** at the moment it appears. It never goes to
a file of the repo, to memory, or to the end of the session, where it gets
lost.

- A **pending item** is work left to do. A **finding** is something found
  wrong: a defect, a contradiction, a gap.
- The tree: an open issue labelled `baseline` is the root (see the
  `baseline` skill). Its children are the top-level pending items. Every
  later bifurcation is a sub-issue of the node where it was found, in any
  repository.
- **Nothing enters the tree without the user's yes.** Claude detects and
  proposes; the user approves.
- **Nothing is resolved without the user's yes either.** A hand-off never
  authorises a change: the session that resumes it presents each element
  and waits (section 4).
- Issues are always created from Claude Code with `gh`, never from the
  GitHub web. They are written in **English**, whatever language the
  conversation uses.

## 1. Propose, short and simple

When a bifurcation appears, propose it at once and keep working on the
current node meanwhile. The proposal always has the same shape; the user
never has to ask for more:

1. **Context.** What the reader needs to understand it, every term defined
   the first time it appears.
2. **Problem.** What is wrong or what is missing, and why it matters.
3. **Options**, numbered, option 1 always the recommended one, with one
   line on why. Opening the issue, resolving it now or leaving it are
   options like any other.

Then the question, in one line:

```text
↳ ¿anoto? "<title>" · hija de: <parent> · <⏳ espera de ti | ▶ Claude puede | ⛔ bloqueado | 🔴 rompe CI>
```

- Several bifurcations at once: one message, each with its context,
  problem and options, numbered, so the user answers once ("sí a 1 y 3").
- The user answers yes, no, or with a change (title, parent, state). Only
  a yes creates the issue.
- A rejected proposal is not created, and is not proposed again.
- When nothing in the tree fits and the subject will outlive the session,
  propose it as a new top-level child of the baseline.

## 2. Create, after the yes

1. **Repository.** The one whose code or document is wrong or unfinished,
   which is not always the one in use. Always pass `-R <owner>/<repo>`.
2. **Duplicates.**
   `gh issue list -R <owner>/<repo> --state all --search "<key terms>"`.
   If one covers it, comment there instead, and propose linking it.
3. **Labels.** Create them once per repository when missing:
   ```sh
   R=<owner>/<repo>
   gh label create finding   -R $R --color d73a4a --description "Something found wrong, to resolve" 2>/dev/null
   gh label create pending   -R $R --color fbca04 --description "Work left to do, not a fault" 2>/dev/null
   gh label create question  -R $R --color d876e3 --description "Waits for a decision of the user" 2>/dev/null
   gh label create blocked   -R $R --color 6a6f75 --description "Waits for another issue or for someone else" 2>/dev/null
   gh label create breaks-ci -R $R --color b3261e --description "Keeps a CI check red" 2>/dev/null
   ```
   (An existing label makes `gh label create` fail; that is fine.)
   Every issue gets `finding` or `pending`, plus the state labels that
   apply (`question`, `blocked`, `breaks-ci`). An optional subject label,
   `tema:<name>`, groups issues in the tree view (create it like the rest).
4. **Title.** The files or the area it touches, and the problem in one
   sentence.
5. **Body.** Write it to a file in the scratchpad and pass it with
   `--body-file` (inline bodies break code blocks). Sections, leaving out
   the ones that do not apply:
   - **What happens.** Plainly, with `path:line` and the commit
     (`git rev-parse --short HEAD`).
   - **Where the work stands.** If it was left half done: the branch, the
     files, what is done and what is not.
   - **Decision needed.** The options, the recommended one and why. For
     code or language matters, a ✅ and a ❌ minimal example.
   - **Proposed change.** When there is a concrete one, a unified patch
     (`diff -u --label a/<path> --label b/<path> <old> <new>`, checked with
     `git apply --check`) in a ```` ```diff ```` block, with the recipe:
     ```sh
     git apply --check change.patch
     patch -o /tmp/<file>.proposed <path> < change.patch   # compare without touching the file
     code --diff <path> /tmp/<file>.proposed
     # the user's yes goes here; nothing is applied before it
     git apply change.patch
     ```
   - **Hand-off.** Always. See section 3.
   - Last line: `Found while <what was being done> (PR #N | commit <sha>)`.
6. **Create and link.**
   ```sh
   gh issue create -R <owner>/<repo> -t "<title>" -l <labels> -F <body file>
   python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/issue_tree.py" link <parent URL> <new issue URL>
   ```
   (The script is in `scripts/` of this plugin, two directories above this
   skill's base directory.) Report in one line: number, title and parent.

## 3. The hand-off

The hand-off holds the context of the node. With it, Claude or a person
can resume the issue in any session, without this conversation. Size
follows the item:

- **Small item:** context in two lines, what is missing, and when it is
  done.
- **Item with a decision:** the full prompt below.

Wrap it in a ````` ````text ````` block (four backticks, so code fences
inside do not close it). Never write "as discussed" or "see the chat".

```text
You are resolving issue #<N> of <owner>/<repo>: <title>.

Context: <repositories (owner/repo and usual local path), what each is for,
the source of truth, the facts the reader needs>.
Problem: <what is wrong, path:line>.
Decision: <taken by the user on <date>: X | proposed: X; the user has not decided>.
Steps:
1. Present the element to the user, short and simple: the context, the
   problem, and the options numbered, option 1 the recommended one. Wait
   for the yes; change nothing before it.
2. <...>
Verification: <commands> → <expected result> (from the repository's CLAUDE.md
"Issue verification" section when there is one).
Rules: the user decides: one element per message, presented short and
simple (context, problem, options numbered, option 1 the recommended one),
applied only after the yes in the chat; the Decision line above never
replaces that yes. <the repository's CLAUDE.md rules that apply: language,
branches and worktrees, no `git add -A`, commit only when asked>.
Done when: <observable condition>. "Closes #<N>" in the resolving PR.
```

**The Decision line.** `taken by the user on <date>` only when the user
said yes in the chat to that exact change. A patch Claude wrote, a
recommendation, the conclusion of an audit: all `proposed`. Never `taken`
without `by the user on <date>`.

**Keep it current.** When the user takes a decision, or the context
changes, edit the hand-off (`gh issue edit -F`). A decision is also left
as a comment. When a node moves from ⏳ to ▶, remove `question`.

## 4. Resolving from a hand-off

The session that resumes an issue answers short, concise and simple, in
the shape of section 1: for each element, in one message, the context, the
problem and the options numbered, option 1 the recommended one; then the
plain question, and the wait. Nothing is written to the working
tree before the yes; a `Decision: taken` line, a patch in the issue body or
a `Steps` list are not a yes. One element per message.

## 5. Closing

The commit or PR that resolves an issue says `Closes #N`
(`Closes owner/repo#N` across repositories).
