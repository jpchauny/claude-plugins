---
name: recap
description: Bring the user back up to speed on the current Claude Code session after time away - a short report in the chat of this session only - its goal, what was done, where it stopped, what waits for the user, what is pending, the real state of its files and background work, and the next step. Use when the user says /recap, "recap", "ponme al tanto", "¿dónde estábamos?", "¿en qué quedamos?", "where were we", "catch me up".
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

In the chat, in the user's language, at most about 25 lines, with exactly
this template:

```markdown
## Recap — <tema de la sesión en pocas palabras>

**Objetivo:** <lo que pediste al empezar; si cambió: "empezó como X, ahora es Y">

**Hecho**
- <logro o decisión 1> — `archivo` (commiteado / sin commitear)
- <logro o decisión 2>
- <máx. 5 viñetas, agrupadas por tema>

**Dónde quedó:** <una frase: lo último que hacía Claude o lo último que pasó>

**Te espera a vos**
1. <pregunta sin responder o aprobación pendiente>
2. <…>
(si no hay: "Nada.")

**Pendiente**
- <lo que falta para cumplir el objetivo>
(si no hay: "Objetivo cumplido.")

**Estado real**
- Sin commitear: <archivos de esta sesión> | Sin pushear: <n commits>
- En segundo plano: <tareas/subagentes corriendo> (o "nada")

**Siguiente paso:** <una acción concreta>
```

Rules:

- **Te espera a vos** is numbered and comes before **Pendiente**: it is what
  the user needs first to go on.
- An empty section stays, in one line ("Nada."); it is never dropped.
- **Hecho** groups by subject, not step by step; at most 5 bullets.
- **Estado real** comes only from the commands of step 1.
- If the session was compacted, put above the report the line
  *"Sesión compactada: completado desde el transcript"*.
- **Siguiente paso** is one action, concrete; no alternatives.
