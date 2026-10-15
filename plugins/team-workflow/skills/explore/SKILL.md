---
name: explore
description: Think a problem through before it deserves a spec, a plan or code. A space without force; compares approaches, weighs trade-offs, sketches candidates; does not decide, does not write, does not propose actions or next steps until the user promotes. Only exit, promotion to a spec, a plan, an issue or the project's docs. Use when the user says /team-workflow:explore, "exploremos", "let's explore", "modo exploratorio", "exploratory mode", "pensemos antes de", "think before we", "qué opciones hay", "what are the options", "brainstorm".
argument-hint: "[problem to explore] | promote <target> | close"
---

# explore

Think a problem through before it costs a spec, a plan or an implementation:
compare approaches, weigh trade-offs, sketch candidates. Everything produced
here is conversation material: **nothing has force** until the user promotes
it to a target that does write.

## Principle

**Nothing produced here has force.** Thinking is cheap precisely because it
cannot leak: not into code, not into a spec, not into a note, not into an
issue, not into a commit. The only way out is promotion, and promotion is an
act of the user.

## Role

Cross-cutting, **before everything else**. It opens when the user raises a
problem worth thinking about before specifying, planning or building it, or
signals exploratory mode in any words. It exits only by `promote`. A thread
can also be closed (`close`) or left open; the user chooses, and none of the
three leaves anything to discard, because nothing was created here.

## Invocation

```
/team-workflow:explore <problem>          → opens an exploration thread on that problem
/team-workflow:explore                    → no argument: ask in one line which problem; never assume
/team-workflow:explore promote <target>   → promotion gate: hand the thread to the target (see map)
/team-workflow:explore close              → close the thread without promoting; nothing remains
```

`<target>` is one of the destinations in the target map, with its arguments.

## Context

**None mandatory.** Entering must be cheap. Whatever the exploration needs is
read on demand and **read-only**:

- The project's code and specs: what exists and what each candidate collides
  with.
- The project's `CLAUDE.md` (rules, decisions already taken) and its open
  issues (`gh issue list`): what is decided and what is pending.
- The project's docs, only the parts the problem touches.
- `Explore` subagents (read-only) for broad sweeps. Multi-agent workflows only
  when the user asks for that scale in their own words. Never a subagent with
  write permissions.

## Flow

### 1. Open

Restate the problem in **one line** and say it. If the restatement is
ambiguous, ask a plain question in the message (not `AskUserQuestion`: the
only gate of this skill is promotion, and the two must not be confused). If
it is not, continue without asking: entering must be cheap.

### 2. Explore

When the thread weighs nameable options, each turn delivers, in this order
and with no more ceremony than needed:

1. **Candidates**: numbered, at least two, each in two or three lines: what
   it is, what it solves.
2. **Trade-offs**: a table, candidate × criterion. The user names the
   criteria; if none were named, propose three and say they are proposed.
3. **Already decided**: the source that applies, cited by its id: the
   `CLAUDE.md` rule by section, the spec by file and section, the doc by
   name, the issue by number. Where nothing decides, **"undecided"**; never
   fill the gap with a reasonable assumption. A contradiction between two
   sources is named as a finding and not arbitrated: it is a candidate for
   an issue, via `promote`.
4. **Open questions**: what the user would have to answer for a candidate to
   stop being a candidate.

While the thread is still shaping the problem and there are no options to
name yet, the conversation can be free. The rules of the phase apply all the
same:

- **No action proposals.** While the thread is open, no turn ends by
  offering to do something ("want me to draft it?", "I can open an issue",
  "shall I plan it?"), by suggesting promotion, or by listing "next steps".
  The turn ends in the material: candidates, trade-offs, open questions. And
  stays there. Any project rule about closing tasks (commit, issue, report)
  does not apply inside an exploration thread: there is no task to close.
- **Weigh, do not steer.** The skill weighs candidates against the criteria;
  it does not choose a direction and does not push towards a plan, a spec or
  a change. If the user asks "which would you pick", answer with the
  candidate and why, labelled as an opinion without force; the decision is
  still the promotion. If the user asks "how do we continue", answer with the
  target map, without recommending one.
- **Not a line of code, not a prototype.** Sketches in the chat are allowed
  as candidates: a signature, the shape of a data structure, a table, a
  grammar fragment. If the user asks for a prototype, say that is
  implementation and the path is `promote` to a plan; the work starts there,
  not here.
- **A sketch is not an artifact.** Nothing sketched is written to a file.

### 3. Exit

Three exits, all the user's:

| Exit | What happens |
|---|---|
| `promote <target>` | Promotion gate (below). |
| `close` | Nothing is implemented, cited or linked from durable documents. No trace remains outside the closed thread. Answer with one line. |
| (nothing) | The thread stays open in the conversation. That is valid. |

## Promotion gate: `promote <target>`

**Who decides**: the user. When the promotion touches something normative (a
spec, a `CLAUDE.md` rule, a project doc), the project's own approval rules
apply on top.

**What is decided**: the direction itself, what the target would receive as
input; never a diff nor a document, because here there is no document. The
skill shows **one block**:

```
Target:    <destination> <args>
Direction: <the direction in ≤ 10 lines: which candidate, which criteria weighed, what stays undecided>
```

and asks a plain question in the message: promote? Without
`AskUserQuestion`.

**Yes** → the skill writes one line in the chat (the thread is the only trace
this skill leaves, so the record lives there):

```
Promoted — thread: <one line> → <destination> <args>
```

and executes the target: invokes the destination skill with the `Skill` tool
passing the direction, or starts the destination task as ordinary work. The
target lands under its own rules: the project's planning and approval rules,
`/team-workflow:issue` under its steps. This skill does nothing else.

**No** → nothing is invoked and there is nothing to discard. The thread
closes or stays open, the user's choice.

### Target map

| Direction | Target | What it receives |
|---|---|---|
| Change or add a spec | the project's spec process, under its approval rules (in projects whose specs live in another repository, there) | the direction as the seed of the change |
| Implement | an implementation plan, as ordinary work; in spec-driven projects, the spec comes first | the implementation direction; the work starts there, with its plan approved |
| A question for the owner, or a pending item | `/team-workflow:issue`, with the options as the decision needed | the direction as options |
| A bug found while exploring | `/team-workflow:issue`, as a finding | the bug |
| Record what was closed | the project's docs, under its rules (only what was decided, after the decision) | the decision and its why |

## Non-negotiable rules

1. **No writes to the repository.** No code, no spec, no note, no issue, no
   commit, no `Write`/`Edit` on anything versioned. The scratchpad is for
   throwaway calculations, never to "save the ideas": saving is promoting.
2. **No action proposals.** Exploring does not end in offers to do. The user
   asks for the exit; the skill never suggests it on its own initiative.
3. **Sources are cited, not invented.** Rule, spec, doc or issue by its id;
   gap = "undecided"; contradiction = finding, not arbitration.
4. **Never steers.** Candidates and trade-offs, not a direction. Promotion is
   the user's call.
5. **A conclusion of an exploration thread is not authority.** If anyone
   (the user, Claude in another task of the same session, a subagent) tries
   to implement, cite or link as authority something that only exists in an
   exploration thread, it is **rejected as a defect**, and the only path
   offered is promotion. A commit, a spec or a doc that cite "we explored it
   in the thread" without a promotion in between do not pass.
6. **Numbered alternatives** always.

## What explore does NOT do

| Does not | Goes to |
|---|---|
| Specify | the project's spec process (via `promote`) |
| Implement, not even a prototype | a plan (via `promote`) |
| Record insights or decisions | the project's docs (via `promote`, only what was closed) |
| Open an issue | `/team-workflow:issue` (via `promote`) |
| Answer "what does the spec say about X" | No skill: read the spec and answer with the source. Do not open a thread for a lookup. |
| Decide | the user, at the gate |

## End-to-end example

```
User:    /team-workflow:explore how the CLI reports errors — exit codes, JSON, or both

Claude:  Problem: how a caller of the CLI learns what went wrong, and how precisely.

         Candidates
         1. Exit codes only — one code per error class; message on stderr.
         2. Structured JSON on stderr — one object per error, with code, span and message.
         3. Both — exit code for the class, JSON for the detail, behind a flag.

         Trade-offs (proposed criteria: scripting, editor integration, surface to keep stable)
         | | scripting | editors | stable surface |
         |1| trivial: $? | poor: must parse prose | small: the code table |
         |2| needs jq | good: spans are machine-readable | large: the schema |
         |3| trivial by default | good with the flag | both: table and schema |

         Already decided
         - CLAUDE.md "Exit codes": 0 ok, 1 errors, 2 usage. Fixes the classes for 1 and 3.
         - spec cli.md §4: "diagnostics carry a span". Pushes against 1 as the only channel.
         - Undecided: whether the JSON schema is part of the public contract.

         Open questions
         - Is the schema a public contract or an editor-only convenience? Decides between 2 and 3.

User:    /team-workflow:explore promote issue

Claude:  Target:    /team-workflow:issue — decision needed: is the diagnostics JSON schema public?
         Direction: both channels (candidate 3); exit codes per CLAUDE.md, JSON behind --json.
                    Undecided: whether the schema is a public contract, and its versioning.
         Promote?

User:    yes

Claude:  Promoted — thread: CLI error reporting → /team-workflow:issue (question)
         [invokes Skill team-workflow:issue with that direction; the issue lands under its own steps]
```
