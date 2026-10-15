---
name: issue
description: Open a GitHub issue for a pending item or a finding the moment it appears, with a self-contained hand-off prompt so anyone (person or agent) can resolve it later without this conversation. Use whenever work is left undone, something is found wrong, a decision is needed from the user, or the user says /team-workflow:issue, "abre una issue", "crea un issue", "anótalo como issue".
---

# issue

Every pending item or finding not resolved in the current change goes to a
GitHub issue **at the moment it appears**: never to a file of the repo, to
memory, or to the close of the session, where it is lost.

- A **pending item** is work left to do.
- A **finding** is something found wrong: a defect, a contradiction, a gap.

Everything happens with `git` and `gh` from the session; the user does not
operate the GitHub web interface. Issues are written in **English**, even
when the conversation is in another language.

## Steps

1. **Repository.** The issue goes to the repository whose code or
   document is wrong or unfinished, which is not always the one you are
   working in. Name it explicitly: `gh ... -R <owner>/<repo>`.

2. **Duplicates first.**
   `gh issue list -R <owner>/<repo> --state all --search "<key terms>"`.
   If one already covers it, comment on it (`gh issue comment`) with what is
   new, instead of opening another. Report its number.

3. **Labels.** Use `finding` or `pending` (plus `question` when a decision
   of the user is needed). If the repository lacks them, create them once:
   ```sh
   gh label create finding  -R <owner>/<repo> --color d73a4a --description "Something found wrong, to resolve" 2>/dev/null || true
   gh label create pending  -R <owner>/<repo> --color fbca04 --description "Work left to do, not a fault"     2>/dev/null || true
   gh label create question -R <owner>/<repo> --color d876e3 --description "Needs a decision"                 2>/dev/null || true
   ```

4. **Title.** The files or sections it touches, and the problem in one
   sentence: `block-handlers.md §9: reserved name used as a variable`.

5. **Body.** Write it to a file in the scratchpad and pass it with
   `--body-file` (never inline: quoting breaks code blocks). Sections, in
   this order; leave out the ones that do not apply:

   - **What happens.** Plainly, with `path:line` references and the
     commit or version they refer to (`git rev-parse --short HEAD`).
   - **Where the work stands.** If work was left half done: the branch,
     the files touched, what is done and what is not.
   - **Decision needed.** The options, the recommended one and why. When
     the subject is code or a language, give two minimal examples, one
     ✅ (what should hold) and one ❌ (what should not).
   - **Proposed change.** When there is a concrete change, embed it as a
     unified patch (`diff -u --label a/<path> --label b/<path> <old> <new>`)
     in a ```` ```diff ```` block, and the recipe to check, compare and
     apply it. Verify first that the patch applies (`git apply --check`):
     ```sh
     git apply --check change.patch
     patch -o /tmp/<file>.proposed <path> < change.patch     # compare without touching the file
     code --diff <path> /tmp/<file>.proposed
     git apply change.patch
     ```
   - **Hand-off.** A prompt, in a ```` ```text ```` block, ready to paste
     into a new session of an agent that knows nothing of this
     conversation. See below.
   - Last line: `Found while <what was being done> (PR #N | commit <sha>)`.

6. **Create** with
   `gh issue create -R <owner>/<repo> -t "<title>" -l <label> -F <body file>`,
   and report in the chat the number, the title and the URL.

7. **Closing.** The commit or PR that resolves it says `Closes #N`
   (`Closes owner/repo#N` across repositories). A decision taken in the
   conversation is recorded as a comment on the issue before closing it.

## The hand-off prompt

Self-contained: everything needed to understand and resolve the issue
without this conversation. Never "as discussed", "the file above", "see
the chat". It holds, in this order:

1. **Context.** The repositories involved (`owner/repo` and the local
   path when there is a usual one), what each is for, and the facts the
   reader needs: what the source of truth is, what is derived from it.
2. **The problem.** What is wrong, with `path:line`.
3. **The decision.** Taken (which, by whom) or still open (the options;
   the agent asks the user and does not choose alone).
4. **Steps.** What to change, where; the patch of the issue if there is
   one, and what to do if it no longer applies.
5. **Verification.** The commands that prove it is resolved and the
   result to expect. Take them from the `## Issue verification` section
   of the repository's `CLAUDE.md` when there is one.
6. **Rules in force.** The ones of the repository's `CLAUDE.md` that apply
   (language, approval before changing specifications, branches and
   worktrees, no `git add -A`, no commit unless asked).
7. **Done when.** The observable condition that closes the issue, and
   `Closes #N` in the resolving commit or PR.

Example skeleton:

```text
You are resolving issue #<N> of <owner>/<repo>: <title>.

Context: <repositories, local paths, what each is for, source of truth>.
Problem: <what is wrong, path:line>.
Decision: <taken: X, by the user on <date> | open: options A/B; ask the user before choosing>.
Steps:
1. <...>
2. <apply the patch in the issue; if `git apply --check` fails, redo the same change by hand>.
Verification: <commands> → <expected result>.
Rules: <the repository's rules that apply>.
Done when: <condition>. Reference "Closes #<N>" in the PR.
```
