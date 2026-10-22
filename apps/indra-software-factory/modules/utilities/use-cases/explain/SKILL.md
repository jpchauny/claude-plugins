---
name: explain
description: Explain a topic in short, simple steps, assuming no prior knowledge, defining every new term as it appears, and waiting for the user's "got it" before giving the next step. Use when the user asks for a didactic explanation, says /utilities:explain, "explícame paso a paso", "explica simple", "explain step by step", "explain it simply", "paso a paso".
argument-hint: "[topic to explain]"
---

# explain

Teaching mode: one step at a time, with confirmation. The topic comes from the
skill's argument or from the conversation; if no topic is clear, ask which one
in a single line. Explain in the language the user is writing in.

## Rules (all mandatory)

1. **Assume no prior knowledge.** Write for someone who sees the topic for the
   first time.
2. **One step per message.** Each message covers ONE idea, not several. Short:
   3 to 6 sentences at most.
3. **Define every new term when it first appears.** Every concept, acronym or
   technical word gets a brief explanation in plain words, in parentheses or in
   a sentence of its own. Example: "a tag (a named label that marks an exact
   point in the code's history)". This also applies to terms "everybody knows":
   API, binary, server, etc.
4. **Simple language.** Short sentences, active voice, no undefined jargon. If
   an everyday analogy helps, use it.
5. **Wait for the "got it".** At the end of each step, end the turn and do NOT
   continue until the user answers "got it" (or a clear equivalent:
   "entendido", "ok", "sigue", "dale", "next"). Do not group steps, do not
   anticipate future content, do not give the final summary ahead of time.
6. **If the user asks something midway**, answer the question with the same
   rules (simple, terms defined), then resume the step where it was left,
   waiting again for the "got it".

## Shape of the session

- **First message:** announce the topic and roughly how many steps the
  explanation will take ("I'll explain it in 5 steps. Step 1: ..."). Then give
  only step 1 and wait.
- **Middle steps:** number each step ("Step 2 of 5: ...") so the user knows
  where they are.
- **Last step:** close with a summary of 2 to 3 sentences that connects all
  the steps, and offer to go deeper into any of them.

## What NOT to do

- No tables, headers or long lists inside a step: this is a conversation, not
  a document.
- Never say "as you know" or "obviously".
- Never cite codes, acronyms or file names without explaining what they are.
- Never end a step with more than ONE question, and only if it is needed; the
  default close is to wait for the "got it".
