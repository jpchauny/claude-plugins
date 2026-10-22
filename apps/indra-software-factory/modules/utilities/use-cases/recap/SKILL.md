---
name: recap
description: Bring the user back up to speed on the current Claude Code session after time away - a short report in the chat of this session only - its goal, what was done, the decisions taken, and what is pending to do or decide. Use when the user says /recap, "recap", "ponme al tanto", "¿dónde estábamos?", "¿en qué quedamos?", "where were we", "catch me up".
---

# recap

The user comes back to this session after a while and has forgotten it. Tell
them, from this session only, where it stands. Not the project's history,
not other sessions: only what happened in this conversation.

Read-only: change nothing, commit nothing, start no work. After the report,
wait for the user.

## 1. Gather

- **The conversation.** It is already in context; it is the main source.
- **Compacted?** If the context starts with a summary of an earlier part of
  the session, details are lost. Recover them from this session's transcript,
  `~/.claude/projects/<project folder>/${CLAUDE_SESSION_ID}.jsonl` (the
  project folder is the working directory with every `/`, space and `.`
  turned into `-`). Read only what fills the gaps — the user's requests and
  the decisions — not the whole file.
- **Real state**, from commands, not from memory of the conversation:
  - `git status --short` and `git log @{u}..` in each repository this session
    touched, limited to the files this session touched. Other sessions work
    in the same tree: never report their changes as this session's.
  - Background shells, monitors, subagents or workflows this session started
    and that are still running.

## 2. Report

In the chat, in the user's language, at most about 20 lines, with exactly
this template:

```markdown
## Recap — <tema de la sesión en pocas palabras>

**1. Objetivo:** <lo que pediste; si cambió: "empezó como X, ahora es Y">

**2. Hecho**
- 2.1 <logro, agrupado por tema>
  - 2.1.1 <detalle, solo si hace falta>
- 2.2 <…>

**3. Decisiones**
- 3.1 <decisión tomada, en una línea>

**4. Pendiente**
- 4.1 Decidir: <pregunta abierta para vos>
- 4.2 Hacer: <lo que falta, incluido lo sin commitear o sin pushear>

¿Quieres ahondar en algún punto? Escribe su número (por ejemplo `2` o `2.1`).
```

Rules:

- Only these four sections, numbered 1 to 4. An empty one stays, in one
  line ("Nada.").
- Every item is numbered by level: section `N`, item `N.M`, sub-item
  `N.M.K`. At most 5 items per section; a third level only when an item
  really needs it.
- In **4. Pendiente**, the items that wait for the user's decision come
  first, marked "Decidir"; the rest are marked "Hacer".
- Uncommitted or unpushed files of this session, and background work still
  running, come from the commands of step 1 and go in **4. Pendiente**.
- If the session was compacted, put above the report the line
  *"Sesión compactada: completado desde el transcript"*.
- The report always ends with the closing question.

## 3. Go deeper

If the user answers with a number, expand that point and everything
numbered under it — `2` is the whole section 2, `2.1` only 2.1 and its
sub-items — and nothing else:

- More detail from the conversation (and the transcript if compacted): what
  was asked, what was done and why, files and commits, with clickable links.
- Keep the numbers: the expansion of `2.1` uses `2.1.1`, `2.1.2`…, so the
  user can go deeper again.
- End with the same closing question.
