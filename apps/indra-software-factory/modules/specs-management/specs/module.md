# Specs management

**Audience:** The people who run a project's flow from specs to code; whoever builds the meta use cases of the meta module `specs-management`

**Scope:** Layers 0 and 1: the AI recommends how to improve the draft specs and the specs that the authors write, checks one spec against the whole of the two layers when a person asks for it, writes draft specs from an interview of a person, and moves specs between the two layers when a person asks for it

The meta module `specs-management` of the meta app Indra Software Factory, listed in [app.md](../../../specs/app.md).

<a id="use-cases"></a>

## Meta use cases

| Meta use case | Meta spec |
|---|---|
| `check-writing` | [check-writing.md](../use-cases/check-writing/specs/check-writing.md) |
| `check-consistency` | [check-consistency.md](../use-cases/check-consistency/specs/check-consistency.md) |
| `promote` | [promote.md](../use-cases/promote/specs/promote.md) |
| `demote` | [demote.md](../use-cases/demote/specs/demote.md) |
| `write` | [write.md](../use-cases/write/specs/write.md) |

## Recommend improvements to the specs

- **ORC-7.** The draft specs and the specs are free: nothing restricts what the authors write ([LAY-2](../../development-methodology/specs/layers.md#rules)). The check of writing, `/specs-management:check-writing`, recommends how to improve the draft specs of layer 0 and the specs of layer 1, and changes nothing; its specification is [check-writing.md](../use-cases/check-writing/specs/check-writing.md). The check of consistency, `/specs-management:check-consistency`, checks one spec of layer 0 or of layer 1 against the whole of the two layers, reports each inconsistency it confirms, and changes nothing; its specification is [check-consistency.md](../use-cases/check-consistency/specs/check-consistency.md). Both run only when the user asks for them, no other meta use case runs them, and their reports stop nothing. No meta use case of this meta module writes the content of a spec, except `/specs-management:write`, which writes a draft spec of layer 0 from the interview of the user, after the user's yes, and deletes the links to a spec that the user deletes, and rewrites the sentences they leave broken as the user accepts ([write.md](../use-cases/write/specs/write.md)). Promote and demote (ORC-35) only move the files that a person names, and rewrite the links that point at them.

## Move specs between layers 0 and 1

This section states what promote and demote share. Promoting a spec moves it from layer 0 to layer 1, and demoting a spec moves it from layer 1 to layer 0 ([LAY-1](../../development-methodology/specs/layers.md#rules)).

### Terms

| Term | Meaning |
|---|---|
| Move | One run of `/specs-management:promote` or `/specs-management:demote`. |
| Source | The repository that a move takes the files from: layer 0 for promote, layer 1 for demote. |
| Target | The repository that a move puts the files in: layer 1 for promote, layer 0 for demote. |
| Moved file | A file that the move takes from the source and puts in the target, at the same path. |
| Path | A path relative to the root of a repository, its parts separated by `/`. A path names the same place in both repositories. |
| Exists | A path exists in a repository when a file, or a folder that holds a file, with that path is in the tree of the repository's commit `HEAD`. "Before the move" is that tree when the move starts; "after the move" is that tree as the move's commit will leave it. |
| Link | An inline link of CommonMark 0.31.2, section 6.3, adopted in part, in a file whose name ends in `.md` (complete list of what is not a link): an image `![...](...)`; text in a code span, in a fenced or indented code block, in an HTML block or in an HTML comment; a destination that is empty, that starts with `/` or `#`, or that has a URI scheme, such as `https:` or `mailto:`, other than `absent:`. Reference-style links are not links. |
| Absent link | A link whose destination starts with `absent:` and whose text ends with ` (not specified yet)`. |
| Plain link | A link whose destination does not start with `absent:`. |
| Link target | The path that a link's destination resolves to from the folder of the file that holds it, without `absent:` at its start and without its `#<anchor>`. A destination that resolves outside the repository has no link target, and the move does not rewrite it. |

<a id="rules"></a>

### Meta rules

- **ORC-35.** Promote and demote run only when the user asks for them (complete list): the user types `/specs-management:promote` or `/specs-management:demote`; the user asks in words to promote or to demote specs; the user says yes to the promote or the demote that `/specs-management:write` proposes (ORC-62, ORC-67). The model must never start a move on its own.
- **ORC-36.** A plain link `[<text>](<destination>)` becomes the absent link `[<text> (not specified yet)](absent:<destination>)`, and nothing else in it changes. Its meaning, in every layer, is [LAY-7](../../development-methodology/specs/layers.md#rules). The mark names no repository.
- **ORC-37.** A move finds the repositories of layers 0 and 1 as [ORC-21](../../project-management/specs/module.md#where-the-repositories-are), ORC-22 and ORC-24 say. It runs from the repository of layer 0 or from that of layer 1, and from no other.
- **ORC-38.** Valid input: one or more paths of the source. A path names a file, or a folder whose files at `HEAD` are all selected. The paths are relative to the root of the source; the working directory does not change them. When the user asks in words, the paths are those the request names. A path that is empty, is absolute, has a part `.` or `..`, or names the root of the repository is invalid.
- **ORC-39.** Before it writes anything, the move tests these conditions, and when any holds it writes nothing and lists every one that holds, in this order (complete list):
  1. no path is given, or a path is invalid (ORC-38);
  2. a path names nothing at `HEAD` of the source;
  3. a selected file is a symbolic link or a submodule;
  4. a moved file's path is in the target's working tree, tracked or not, compared ignoring case, or one of its folders is a file there;
  5. a file to move or to rewrite (ORC-40) has uncommitted changes, staged or not;
  6. a link that the move would rewrite has a title, a destination in angle brackets, a backslash escape or a percent-encoded character in its destination; or a reference-style link of layer 1 has a link target that the move would leave not existing in layer 1;
  7. the source or the target is not on its default branch;
  8. after `git fetch`, the default branch of the source or of the target is not at the same commit as on its remote `origin`.
- **ORC-40.** The move rewrites only these links (complete list):
  1. promote: in each moved file, each plain link whose link target does not exist in layer 1 after the move and exists in layer 0 after the move becomes an absent link;
  2. promote: in each file of layer 1 other than the moved files, each absent link whose link target does not exist in layer 1 before the move and exists after it becomes a plain link (ORC-41);
  3. demote: in each file of layer 1 other than the moved files, each plain link whose link target exists in layer 1 before the move and does not exist after it becomes an absent link;
  4. demote: in each moved file, each absent link whose link target exists in layer 0 after the move becomes a plain link (ORC-41).

  The move changes no other byte of any file. An untracked file of layer 1 is never rewritten; ORC-42 lists each one that holds a link to a moved file.
- **ORC-41.** An absent link becomes a plain link by removing ` (not specified yet)` from the end of its text and `absent:` from the start of its destination, and nothing else. When, before the first move, every plain link of layer 1 has a link target that exists in layer 1 and no moved file holds an absent link in layer 0, a promote followed by the demote of the same paths, or a demote followed by the promote of the same paths, with no other change between the two, gives back every file of both repositories byte for byte.
- **ORC-42.** Before it writes anything, the move shows, and waits for the user's yes (complete list):
  1. each moved file, as `<path>`, in code point order of the paths;
  2. for each moved file whose links it rewrites, the diff between its bytes in the source and its bytes in the target;
  3. for each other file it rewrites, its diff against `HEAD`;
  4. each untracked file of layer 1 that holds a link to a moved file, as `<path> (untracked, not rewritten)`;
  5. the two commits, with their repositories and messages (ORC-43).

  Any reply other than yes leaves both repositories unchanged. Rationale: a moved file's bytes are those of the source apart from its rewritten links, so items 1 and 2 are the whole diff of a move that [LAY-2](../../development-methodology/specs/layers.md#rules) requires.
- **ORC-43.** After the yes, the move tests ORC-39 again and checks that every file it shows still has the bytes it showed. When a condition holds or a byte changed, it writes nothing and shows the move again (ORC-42). Otherwise it writes the files and runs one command per repository, first in the target, then in the source, that commits and pushes to the default branch. Each commit holds only the moved files and the files the move rewrote in that repository, by explicit path, and nothing that another session staged. Each commit message is, byte for byte, the subject in this table, an empty line, and one line `<path>` per moved file, in code point order of the paths; trailers after the paths are free:

  | Move | Target commit | Source commit |
  |---|---|---|
  | promote | `docs: promote specs from layer 0` | `docs: promote specs to layer 1` |
  | demote | `docs: demote specs from layer 1` | `docs: demote specs to layer 0` |
- **ORC-44.** When a command of ORC-43 fails, or the user denies or interrupts it, the move stops and reports what it leaves, as ORC-47 says (complete list):
  1. the target's commit failed or did not run: the move writes back the bytes each file of the target had before the move, deletes the files it created there, and writes nothing in the source;
  2. the target's commit is made and its push failed or did not run: the move leaves that local commit, and writes nothing in the source;
  3. the target's push is made and the source's command failed or did not run: the move leaves the files of the source as they were, so that the moved files are in both repositories, and, when the source's commit is made and its push failed, it leaves that local commit.
- **ORC-45.** A rerun of the same move, with the same paths, resumes it: when every moved file exists in the target at `HEAD`, which is at the commit of its remote `origin`, with the bytes the move would write, and still exists in the source, the move skips the target and does only the source's commit and push. When a commit of ORC-44 is left local, in the target (state 2) or in the source (state 3), the rerun refuses at ORC-39 condition 8; once the person pushes that commit, a rerun after state 2 resumes, and after state 3 the move is complete.
- **ORC-46.** A move never uses `git stash`, `git reset`, `git checkout`, `git restore`, `git clean`, or `git add` of a folder or of all changes, and never touches a file it does not move or rewrite. Several sessions may work in the same repositories: ORC-39 refuses only on the files the move touches.
- **ORC-47.** The move ends with one line per repository, target first, in this form, byte for byte once filled, where `<layer>` is `layer 0` or `layer 1`, `<commit>` the full object name of the commit, and `<error>` the first line of git's error output, or `denied` or `interrupted`:

  ```
  <layer>: <commit> pushed
  <layer>: <commit> committed, not pushed: <error>
  <layer>: nothing committed: <error>
  <layer>: not run
  ```
- **ORC-48.** The refusals of ORC-37 and ORC-39 are given in English, one line each, byte for byte once filled, where `<use case>` is `promote` or `demote`, `<layer>` is `layer 0` or `layer 1`, `<branch>` the default branch, `<line>` the line of the link and `<n>` the number of paths given. ORC-21, ORC-22 and ORC-24 keep their own messages. The lines of ORC-39 follow its order, and within a condition the code point order of their paths:

  ```
  specs-management:<use case>: runs only from the repository of layer 0 or of layer 1
  specs-management:<use case>: expected at least one path
  specs-management:<use case>: <path>: invalid path
  specs-management:<use case>: <path>: not in <layer>
  specs-management:<use case>: <path>: a symbolic link or a submodule
  specs-management:<use case>: <path>: already in <layer>
  specs-management:<use case>: <path>: uncommitted changes in <layer>
  specs-management:<use case>: <path>:<line>: link cannot be rewritten
  specs-management:<use case>: <layer>: not on its default branch <branch>
  specs-management:<use case>: <layer>: not at origin/<branch>
  ```
- **ORC-58.** The norms generator writes an absent link into layer 2 as it is, as every other byte of a spec, and its meaning there is that of [LAY-7](../../development-methodology/specs/layers.md#rules). Decision of the user, 2026-10-26: no rewriting of absent links in layer 2. Rationale: layer 2 stays a byte-for-byte copy of layer 1 apart from its norm IDs.
