# Spec-writing dimensions

**Status:** Approved research input, 2026-10-19

The dimensions to consider when writing specifications for spec-driven design, where AI agents implement code and tests from specs written by people. This is the input for the spec-writing guideline, not the guideline itself. It is independent of any particular process or tool.

A first research pass found 131 dimensions (D1 to D131), from requirements engineering, current spec-driven development practice, the ways AI agents fail when reading specs, verifiability, and lifecycle. They were reduced to:

- 20 core dimensions (C1 to C20): 12 for every spec, 8 only where they apply. Each is a writing rule.
- 17 checklist questions, for the person who approves a spec.
- 30 discarded dimensions: covered by a core dimension, or belonging to the process, governance or a particular toolchain.

## Core dimensions for every spec

### C1. Purpose, scope and non-goals

**Definition:** Open with what the component is for and for whom, then state what the spec covers, which adjacent systems surround it, what is explicitly out, and what must never happen. Write each exclusion and prohibition as its own sentence.

**Why:** An agent that reads only part of a spec needs the purpose the rules serve to handle unforeseen cases. Agents over-build and treat silence as freedom; a stated non-goal tells them when to stop, and a prohibition in its own sentence gets its own check.

| Merged | Dimension | Argument |
|---|---|---|
| D9 | What is in and out of scope, and what must not be built. | Stops over-building; core of C1. |
| D10 | Prohibitions and exclusions are written as their own sentences. | Buried negations are dropped and go untested; part of C1. |
| D24 | The system boundary and the adjacent systems around it. | Without a boundary agents modify things outside it; part of C1. |
| D48 | The document opens with what the system does and why. | Gives the purpose every rule serves; part of C1. |

### C2. One reading only

**Definition:** Every sentence has exactly one interpretation for a reader who has only the spec text: plain short sentences, explicit numbers and units, absolutes with their domain, every list marked as complete or illustrative (no 'etc.' or 'such as' in binding text), no pronoun pointing outside the sentence, and no reliance on anything outside the spec (conversations, review discussions, code, or documents not referenced).

**Why:** The implementing agent cannot ask the author. It silently picks a reading, and different runs pick different readings while claiming to satisfy the same requirement. Lists of unclear closure are read as exhaustive or extended at will.

| Merged | Dimension | Argument |
|---|---|---|
| D30 | Each sentence has a single interpretation. | The agent cannot ask the author; core of C2. |
| D31 | A literal reading gives the intended behaviour, or the goal is stated. | Agents swing between over-literal and over-inferred readings; part of C2. |
| D35 | Numbers, units, limits and tolerances are explicit. | Vague magnitudes are resolved from priors; part of C2. |
| D36 | Absolute and closed-set words state their domain, and lists say whether they are complete. | Absolutes are enforced literally and open lists are read as closed or extended; part of C2. |
| D38 | Statements stand alone, with no pronouns pointing outside them. | Statements are read in isolation; part of C2. |
| D39 | Plain, short sentences without idioms, especially from non-native writers. | Idioms raise ambiguity for both reviewers and models; part of C2. |
| D81 | The spec is understood with no access to conversations, code or history. | Anything outside the spec does not exist for the agent; part of C2. |

### C3. Defined terms, one language

**Definition:** Every domain term is defined once and used with one meaning everywhere, with no synonyms and with narrowed meanings made explicit. The spec set is written in one language; only runtime strings the product shows keep their own language (C6).

**Why:** Models treat synonyms as different concepts and replace local jargon with its public meaning. One vocabulary in one language keeps search, retrieval and references consistent.

| Merged | Dimension | Argument |
|---|---|---|
| D32 | Domain terms are defined once and used with one meaning. | Synonyms become different concepts in code; core of C3. |
| D40 | The spec set uses one written language. | Mixed languages split the vocabulary and break search; part of C3. |

### C4. Complete statement: actor, condition, response

**Definition:** Each behavioural statement names who acts, when or in which state it applies (an EARS-style trigger), and what results. When behaviour is step-wise, use numbered steps, ordered fallbacks and explicit stop conditions, and use a numbered list only where order matters.

**Why:** The model fills missing parts from generic priors, and the gap is invisible because the result looks plausible. A stated condition maps directly to a code branch and a test setup; agents read a numbered list as a required order.

| Merged | Dimension | Argument |
|---|---|---|
| D4 | Each statement holds everything needed to implement it. | Missing parts are filled from model priors; this is the core of C4. |
| D14 | States and modes in which behaviour applies, and their transitions. | The 'while in state' condition of a complete statement; part of C4. |
| D34 | Each statement fits a trigger/condition pattern such as EARS. | Conditions map to code branches and test setups; part of C4. |
| D37 | Each statement names who or what performs the action. | Passive voice leaves the agent unsure whether to implement or expect it; part of C4. |
| D54 | Step-wise behaviour uses numbered steps, ordered fallbacks and stop conditions. | Removes choices where agents drift; part of C4. |

### C5. Errors, edges and refused input

**Definition:** For each operation that takes input or calls a dependency, state what input is valid, what is guaranteed, and exactly what happens on invalid input, missing resources, dependency failure, timeouts and limits, with the message and status fixed as in C6.

**Why:** Agents default to the happy path or a generic try/catch and add silent 'fixes'. Unspecified failures are where their inventions diverge most and are hardest to spot.

| Merged | Dimension | Argument |
|---|---|---|
| D12 | Valid input, guarantees and handling of refused input are stated. | Prevents invented defensive handling; core of C5. |
| D13 | Behaviour on errors, edges, failures, timeouts and limits is stated. | Agents default to the happy path; core of C5. |

### C6. Exact observable outputs and interfaces

**Definition:** Every output a user or another part observes (messages, statuses, formats, arguments, configuration with its defaults and precedence, the flow of interactive interfaces, diagnostics, interfaces between parts) is fixed exactly, with user-facing text verbatim in the language the product speaks. Each check states its strictness (byte-exact or equivalent), and where an exact output contains characters that are not visible, the text names them and their positions.

**Why:** Independently generated parts meet at interfaces and must agree exactly. Specified outputs are the test surface; without them tests assert on internals, agents invent configuration knobs, and copied examples silently lose tabs, trailing spaces or line endings.

| Merged | Dimension | Argument |
|---|---|---|
| D19 | Exact inputs, outputs, formats and contracts between parts. | Independently built parts must agree at interfaces; core of C6. |
| D20 | User-visible outputs are fixed exactly. | Outputs are the test surface; core of C6. |
| D61 | Characters that are not visible in exact outputs are named. | Copied examples silently lose tabs, trailing spaces and line endings, breaking byte-exact checks; part of C6. |
| D67 | Whether output must match exactly or only equivalently. | Agents cannot guess assertion strictness; part of C6. |
| D91 | Arguments, defaults, prompts shown and inputs awaited in interactive interfaces. | For interactive interfaces the flow is the observable product; part of C6. |
| D116 | The language the product speaks to users, separate from the spec's language. | Agents translate strings unless quoted verbatim; part of C6. |
| D118 | What the component reports about its own run. | Diagnostics are observable output other tools parse; part of C6 (what must never be printed is C17). |
| D119 | Configuration settings, defaults and precedence. | Agents invent knobs and resolve precedence arbitrarily; part of C6. |

### C7. Verifiable rules with binding examples

**Definition:** Every behavioural statement, including qualities and invariants, has a clear pass or fail: a measurable threshold, a property, or a binding example. Where the text alone does not fix one output (boundaries, formats, ordering, refusals), give examples, each marked binding or illustrative, whose expected results come from the spec, not from the implementer. A required example set includes the boundary case and at least one case that is refused or must not happen; for behaviour that depends on earlier state, examples show the sequence of inputs and the expected result after each step.

**Why:** With a vague rule the agent picks one reading and writes tests that confirm it. An agent that writes both code and tests shares its misreading between them; only an expected result approved in the spec checks it. Happy-path-only examples let edge and must-not behaviour drop silently. Requiring examples only where text is not enough keeps the cost proportionate.

| Merged | Dimension | Argument |
|---|---|---|
| D15 | Properties that must hold for all inputs or states are written as such. | A property is a pass/fail check without listing expected values; part of C7. |
| D17 | Quality attributes are stated with numbers, units and thresholds. | Vague qualities are silently sacrificed; C7 requires a measurable threshold. |
| D55 | Every behavioural sentence has a clear pass or fail. | Core of C7. |
| D57 | Each requirement has a concrete acceptance scenario. | Scenarios turn straight into tests; part of C7 where text alone is not enough. |
| D58 | Each example is marked binding or illustrative. | Agents overfit illustrations or ignore binding examples; part of C7. |
| D59 | Examples cover typical, boundary and must-not cases. | Happy-path-only examples let edge and must-not behaviour drop silently; C7 now requires a boundary and a refused case. |
| D63 | A tiny concrete instance inside the rule itself. | Pins one reading when the rule is read alone; part of C7. |
| D64 | Examples of history-dependent behaviour show sequences. | Single snapshots leave state carry-over without a check, so runs diverge; C7 now requires sequences for stateful behaviour. |
| D66 | Expected results come from the spec, not from the implementer. | Code and tests by one agent share its misreading; core of C7. |

### C8. Explicit unknowns, defaults and decisions

**Definition:** Mark what is undecided as open, state assumptions and defaults, and say for unstated cases whether they are forbidden, free or open. For each gap that would change output or data, state either the default to apply or that the case is open and must be decided by a person before it is built. Mark provisional statements as open or as a decision with its condition (never a bare 'for now'), and record each resolved ambiguity with its reason.

**Why:** Agents fill gaps rather than stall and then point to the nearest rule, which looks like compliance. A marked unknown shows where guessing is not allowed, and a stated default shows where proceeding is.

| Merged | Dimension | Argument |
|---|---|---|
| D6 | For each unstated case, the spec says whether it is forbidden, free or undecided. | Tells the agent where invention is allowed; part of C8. |
| D21 | Assumptions about the environment and defaults are written down. | Unwritten assumptions are reinvented each run; part of C8. |
| D83 | Undecided content is marked as open. | Agents fill gaps silently; core of C8. |
| D84 | Resolved ambiguities are recorded with reason. | Closes gaps the agent must not fill by assumption; part of C8. |
| D101 | Status and temporal validity of statements. | Draft or future text is treated as binding now; part of C8. |

### C9. Rule apart from reason

**Definition:** Binding text is visibly separate from explanation: binding wording follows one convention declared for the spec set (for example must, should, may), rationale and accepted costs are labelled as such, prescribed designs and departures from common practice are labelled as deliberate, and the spec describes behaviour rather than giving instructions to the agent that implements it.

**Why:** Agents give equal weight to everything imperative-sounding and take accidental 'how' hints as requirements. Labelled rationale lets them handle unforeseen cases and resist 'correcting' deliberate choices without implementing the rationale as an obligation.

| Merged | Dimension | Argument |
|---|---|---|
| D7 | Statements fix observable behaviour, and any prescribed design is deliberate. | Accidental 'how' hints are taken as requirements; C9 labels deliberate design. |
| D28 | The reason for a rule is written, apart from the rule. | Rationale guides unforeseen cases without becoming an obligation; core of C9. |
| D29 | Deliberate imperfections and their costs are labelled. | Unlabelled, they get 'fixed'; part of C9. |
| D33 | One declared convention marks obligation, recommendation and information. | Agents weigh all imperative text equally; part of C9, declared once per spec set. |
| D45 | Binding text is visibly separate from informative text. | Core of C9. |
| D46 | Spec text is kept apart from instructions to agents. | Agent-directed imperatives become requirements or hijack agents; part of C9. |
| D123 | Departures from common practice are marked deliberate. | Models pull toward the common solution; part of C9. |

### C10. One claim per statement

**Definition:** Each statement carries exactly one claim that can be checked on its own; separate cases are separate items.

**Why:** A compound statement gets partly implemented and reported as done, and no single check shows which claim failed.

| Merged | Dimension | Argument |
|---|---|---|
| D42 | Each statement carries exactly one checkable claim. | Compound statements get partly implemented; core of C10. |
| D73 | Each statement is specific enough to be checked on its own. | Aspirational statements cannot be checked or claimed as done; part of C10. |

### C11. Say it once, general rule then exceptions

**Definition:** Each fact is stated in one place and referred to elsewhere. A general rule is stated once with its exceptions listed explicitly, and where two rules or qualities can collide, the spec states which wins.

**Why:** Paraphrased duplicates drift apart, and the agent implements whichever copy it loaded. Exceptions scattered through prose are missed, and unstated precedence is resolved by whatever is nearest in context.

| Merged | Dimension | Argument |
|---|---|---|
| D26 | When rules or qualities collide, the spec says which wins. | Agents resolve conflicts by proximity; stated precedence is part of C11. |
| D27 | A general rule is stated once with exceptions listed explicitly. | Scattered exceptions are missed; part of C11. |
| D51 | Each fact is stated in one place. | Duplicates drift apart; core of C11. |

### C12. Proportionate and economical

**Definition:** The amount of specification matches the size and risk of the change, and every sentence is needed. Economy applies to explanation, repetition and emphasis, never to conditions, exclusions, error behaviour or required examples (C1, C4, C5, C7); when they collide, completeness wins. Emphasis is rare and reserved for the few critical rules.

**Why:** Instruction-following drops as rules multiply, and bloated text is skimmed by agents and reviewers. Writers who cut tend to cut edge cases and exclusions first, which are exactly what agents then invent.

| Merged | Dimension | Argument |
|---|---|---|
| D41 | Every sentence is needed, emphasis is rare, and the rule count per task is manageable. | Instruction-following drops as rules multiply; core of C12. |
| D85 | Spec detail is proportional to the size and risk of the change. | Over-specification wastes context and review; core of C12, bounded by its completeness precedence. |

## Core dimensions that apply only in some cases

### C13. Navigable, bounded units

**Applies when:** When the spec set is too large to read whole for one task.

**Definition:** Group rules by subject so all rules on a topic are found together, keep rules that apply everywhere apart from feature rules, use one consistent structure across the set, and keep each unit small enough to load whole for one task.

**Why:** Effective context is smaller than nominal and long contexts lose their middle. Structure decides what an agent loads; a rule placed in the wrong unit is not seen.

| Merged | Dimension | Argument |
|---|---|---|
| D25 | Rules that apply everywhere are kept apart from feature rules. | Where a rule sits decides whether it is loaded with the task; part of C13's grouping. |
| D49 | Rules are grouped by subject so a topic can be found. | Structure decides what retrieval loads; part of C13. |
| D50 | Each unit is small enough to load whole for one task. | Long contexts lose their middle; core of C13. |

### C14. Stable identifiers

**Applies when:** When code, tests, reviews or other statements refer to individual statements.

**Definition:** Each statement has an identifier that is unique in the spec set, never changed or reused, and independent of the file or section where the statement sits. A split or merged statement gets new identifiers and the old ones are retired. Related statements refer to each other by identifier.

**Why:** A requirement must be uniquely identifiable so people and agents can refer to it unambiguously. A reused or location-based identifier silently changes what an existing reference points to.

| Merged | Dimension | Argument |
|---|---|---|
| D52 | Related statements refer to each other by identifier. | Lets a reader of one statement find related ones unambiguously; part of C14. |
| D75 | Identifiers are permanent and never reused. | Renumbering breaks references silently; core of C14. |

### C15. One output: tie-breaking and hidden inputs

**Applies when:** When several results are possible, or output depends on time, time zone, locale, randomness, listing order or the network.

**Definition:** Wherever several results are possible, give a complete order of tie-breakers so exactly one output exists. For each hidden input (clock, time zone, locale, random values, ordering, network), say how it is fixed or supplied.

**Why:** Two runs implementing 'pick the best match' diverge unless every tie is resolved in the text. Hidden inputs make agent-written tests flaky or freeze a value by accident.

| Merged | Dimension | Argument |
|---|---|---|
| D16 | Where several results are possible, tie-breakers make exactly one output. | Independent runs diverge on unresolved ties; core of C15. |
| D115 | Outputs depending on clock, locale, randomness or ordering are fixed or supplied. | Hidden inputs cause flaky tests and divergent runs; part of C15. |

### C16. Binding constraints and external references

**Applies when:** When the solution is bound by a platform, policy, dependency or outside standard.

**Definition:** State the constraints that bind the solution (platform, deployment model, licences, organisational policies), the dependencies allowed and the technology pinned because output depends on it, and cite each outside standard by exact version and section, saying whether it is adopted whole or in part.

**Why:** Agents choose libraries and add dependencies freely, and recall outside standards from training data that may be wrong or outdated. Some outputs are only defined relative to one library or one version.

| Merged | Dimension | Argument |
|---|---|---|
| D8 | External constraints and technology pinned because output depends on it are stated. | Agents pick libraries freely, and some outputs are only defined relative to one; core of C16. |
| D22 | Dependencies the behaviour relies on, and how changes to them are handled. | Agents add or misuse dependencies freely; part of C16. |
| D96 | Organisation-wide policies that bind the component. | Agents follow only the policies they see; part of C16. |
| D98 | Installation and deployment model. | Where it constrains the solution it is a binding constraint under C16; release mechanics are out of scope. |
| D124 | Outside standards are cited by exact version and section. | Recalled standards may be wrong or outdated; part of C16. |

### C17. Security, privacy and trust boundaries

**Applies when:** When the component handles untrusted input, sensitive data or permissions.

**Definition:** State what the component may read, write, execute or fetch, which inputs are untrusted, what sensitive data it touches, where that data may go, and what must never be stored, logged, printed or sent.

**Why:** Agents follow instructions found in data and, when the spec is silent, log, cache or publish data they should not.

| Merged | Dimension | Argument |
|---|---|---|
| D94 | Permissions, untrusted inputs and trust boundaries. | Agents follow instructions found in data; core of C17. |
| D95 | Handling of sensitive data. | Silent specs lead to logged or published data; part of C17. |

### C18. External side effects: consent, retry, concurrency

**Applies when:** When the component changes systems outside itself or runs alongside other actors.

**Definition:** For each action that changes the outside world, state whether it needs explicit human consent and what is shown first, whether it is safe to repeat after an interruption and how already-done work is detected, how it is undone, and whether it must be safe while other sessions or agents work on the same resources.

**Why:** Agents act autonomously unless told otherwise, retry by duplicating work, and assume they are alone.

| Merged | Dimension | Argument |
|---|---|---|
| D93 | Which actions need explicit human consent, and what is shown first. | Agents act autonomously unless told; part of C18. |
| D97 | Safety while other sessions or agents act on the same resources. | Agents assume they are alone; part of C18. |
| D121 | External side effects are idempotent and reversible. | Retries duplicate work; core of C18. |

### C19. Changes to existing behaviour and code

**Applies when:** (a) When the spec changes or removes existing behaviour; (b) when the spec describes code that already exists.

**Definition:** (a) For a change, state what must stay as it is, what is added, modified or removed, why each removal was made, how to migrate, and what happens to data written by earlier versions. (b) For existing code, mark each statement as current, intended or a deliberate change, name accidental behaviours, restate implicit behaviour that lives only in configuration, prompts, scripts or team conventions, and say which existing code the spec does not yet govern.

**Why:** A change spec describes only the change, so an agent free to rewrite breaks nearby behaviour, reintroduces what was removed for a reason, and assumes a clean slate for stored data. A spec recovered from code freezes its accidents into rules and drops what was never written down.

| Merged | Dimension | Argument |
|---|---|---|
| D11 | A change spec states which existing behaviour must stay unchanged. | Agents break unstated invariants near a change; part of C19 (a). |
| D87 | For existing code, statements are marked current, intended or changed, with accidents named. | Recovered specs freeze accidents into rules; part of C19 (b). |
| D89 | Implicit behaviour that lives only in prompts or configuration is restated as requirements. | Implicit behaviour disappears on rebuild; part of C19 (b). |
| D90 | Implicit contracts in scripts and conventions are named. | Anything not written down is dropped on rebuild; part of C19 (b). |
| D103 | Changes state what was added, modified, removed, with migration. | An agent cannot tell removal from omission; part of C19 (a). |
| D104 | The reason for a change reaches the implementer. | Without it, removed behaviour is reintroduced; C19 (a) requires the reason for each removal, labelled as rationale per C9. |
| D120 | Handling of data written by earlier versions. | Agents assume a clean slate; part of C19 (a). |
| D126 | Which existing code a partial spec governs. | Without it a rebuild deletes unspecified behaviour; part of C19 (b). |

### C20. Model-driven runtime behaviour

**Applies when:** When a language model generates the component's output at runtime, or decides at runtime whether to invoke it.

**Definition:** Separate hard invariants that must hold on every run from qualities judged by a rubric, an evaluation set and a pass rate over a stated number of runs. Where a model decides whether to invoke the component (for example from a tool description), state the situations in which it must and must not be invoked. Name the model and settings the behaviour was validated on and what must still hold when they change.

**Why:** Exact expected outputs do not work for output generated anew each run, so an agent either asserts on one sample or asserts nothing. Without a named model, a regression cannot be told apart from a model change.

| Merged | Dimension | Argument |
|---|---|---|
| D92 | When a model decides whether to invoke a component, the situations in which it must and must not be invoked. | Invocation chosen by a model at runtime is behaviour the spec must bound; part of C20. |
| D113 | Correctness of model-generated runtime output via invariants, rubrics and pass rates. | Exact expected outputs fail for generated output; core of C20. |
| D114 | The model and settings a runtime behaviour was validated on. | Model changes silently break behaviour; part of C20. |

## Checklist for the approver

| Dimension | | Related to | Argument |
|---|---|---|---|
| D1 | Each statement expresses a real need, and removing it would break something. | C12 | A judgement the reviewer makes per statement; the writing rule is C12's 'every sentence is needed'. |
| D2 | The spec says what stakeholders want, not a transcription of current behaviour. | C19 | Only a reviewer who knows the intent can check fidelity; the writing side is C19's current-versus-intended marking. |
| D3 | What is specified can be built within platform limits, cost and time. | C16 | Feasibility is a review question, not a wording rule; the constraints it is judged against are stated under C16. |
| D5 | The spec set as a whole covers every function, state, interface, error path and quality. | C4, C5, C6, C7 | Coverage is judged across the whole set by a reviewer and spans several cores; no single sentence carries it. |
| D18 | Measurable, technology-free success criteria for the feature as a whole. | C7 | Useful for judging the feature, but per-statement pass/fail under C7 already binds the agent; a reviewer question. |
| D23 | Whose needs the spec represents, including any agent that uses the component at runtime. | C1 | A reviewer question about missing viewpoints; the writing rule is C1's 'for whom'. |
| D56 | The verification method per requirement and a check the agent can run. | C7 | Choosing test methods is planning, not wording; the reviewer asks whether a runnable check exists. |
| D60 | Examples use one consistent input/expected-output form. | C7 | A consistent form lets examples become test fixtures directly; a reviewer question on C7 examples, not a rule every spec needs. |
| D62 | Choice between realistic and minimal symbolic examples. | C7 | A judgement about example style, not a rule every spec must follow. |
| D65 | The spec points to existing patterns to follow. | C9 | Pointing at code conflicts with self-containment (C2); when used, it is a prescribed design labelled under C9. |
| D68 | Which checks must exercise the real interface and which may substitute it. | C7 | The test plan is process, but a reviewer asks whether rules about interactions with dependencies say if their check may use a substitute, since agents default to mocks that pass while the real interaction fails. |
| D71 | The spec is checked for contradictions and gaps before handoff. | C11 | A pre-handoff review activity; the writing rule against conflict is C11. |
| D82 | Two independent agents would build the same behaviour from the text. | C2 | The outcome test of C2 and C15, asked by a reviewer rather than written. |
| D108 | The approver can review the spec in reasonable time. | C12 | Judged by the reviewer; C12 keeps specs economical. |
| D117 | Accessibility of generated outputs. | C7 | A quality that applies only to some outputs; when it applies it is a measurable quality under C7. |
| D122 | Which real systems tests of a component with external effects must never touch. | C18 | A reviewer question for components with external side effects; test environment setup itself belongs to the project. |
| D130 | Testing a spec by having fresh agents build or question it. | C2 | A review method that measures C2; not a writing rule. |

## Discarded

| Dimension | | Related to | Argument |
|---|---|---|---|
| D43 | Each requirement follows one consistent statement shape. | C10 | Redundant: a single checkable claim (C10) in a complete trigger-response form (C4) is the generic substance; a particular visual layout is a template choice. |
| D44 | Statements are classified into kinds (requirement, example, decision, note). | C9 | Redundant: the distinctions that change how an agent is bound are covered by C9, C7 and C8; a classification scheme adds nothing more. |
| D47 | A header stating maturity, audience and coverage. | C1 | Redundant: coverage and audience are in C1 and maturity in C8; header layout is a template choice. |
| D53 | A consistent document structure across the spec set. | C13 | Redundant: a consistent structure that aids navigation is part of C13; machine-parseable conventions beyond that are tooling. |
| D69 | What makes a requirement done. | process/lifecycle | Done-ness is a process definition; per-statement pass/fail (C7) is the spec's part. |
| D70 | Passages to be formalised are precise enough for it. | C2 | Redundant: precision is C2; formalisation itself is an optional tooling choice. |
| D72 | Requirements trace to needs, and code and tests trace back. | process/lifecycle | Traceability is a process; the spec's part is stable identifiers (C14) where references exist. |
| D74 | Hand-written versus tool-generated identifiers. | process-specific | How identifiers are produced is a tooling choice; C14 states only what they must guarantee. |
| D76 | Identifiers stay unique across related documents. | C14 | Redundant: C14 requires identifiers unique across the spec set; a numbering scheme is a convention. |
| D77 | How wording edits ripple through a change-detection tool. | process-specific | Only matters under one particular change-detection tool. |
| D78 | What happens to identifiers when statements are split, merged, moved or restored. | C14 | Redundant: C14 now states that split or merged statements get new identifiers and old ones are retired. |
| D79 | Identifiers do not depend on file or section location. | C14 | Redundant: C14 now requires identifiers independent of where the statement sits. |
| D80 | Which rules are enforced by tools versus advisory. | process/tooling | Enforcement belongs to tooling and governance, not to spec wording. |
| D86 | Behaviour is split into prioritised slices that build and test alone. | process/lifecycle | Slicing and prioritising work is planning, like mapping units to work items (D127); C10 already keeps each claim checkable alone. |
| D88 | Who validates a spec drafted from code by an agent. | process/lifecycle | A review process, not a writing rule. |
| D99 | Blast radius of changing the spec of a code-generation tool. | process-specific | Only exists in one particular toolchain. |
| D100 | Whether a spec is a one-off brief, a living anchor or the sole source. | process/lifecycle | A methodology choice; its effect on detail is handled by C12. |
| D102 | Metadata per requirement (priority, owner, source, stability). | governance | Requirements-management metadata, not a writing rule. |
| D105 | Likelihood of change and change impact of a rule. | governance | A planning attribute, not a writing rule. |
| D106 | Who owns and approves specs. | governance | Governance, not wording. |
| D107 | Stakeholders confirm the spec before building. | process/lifecycle | A review step in the process. |
| D109 | Who writes the spec and how requirements are elicited. | process/lifecycle | Elicitation method, not spec content. |
| D110 | How disagreement between code and spec is found. | process/lifecycle | A lifecycle activity. |
| D111 | How implementation findings flow back into the spec. | process/lifecycle | A feedback process; marking open items is C8. |
| D112 | How cross-cutting principles are amended. | governance | Governance, not writing. |
| D125 | Formatting carries meaning: numbered lists imply order, code blocks imply literal text. | C4 | Redundant: C4 now uses numbered lists only where order matters, and C6 fixes literal output; tool-specific effects of formatting are out. |
| D127 | Mapping spec units to agent sessions and work items. | process/lifecycle | Work planning, not spec writing; unit size is C13. |
| D128 | The writing guideline follows its own rules. | out of scope | About authoring the guideline, not a dimension of specs. |
| D129 | The guideline shows weak and rewritten statement pairs. | out of scope | A presentation choice for the guideline, not a spec dimension. |
| D131 | Previewing a tool's generated output before approval. | process-specific | Only exists in one particular toolchain. |
## Tensions

Pairs of dimensions that pull against each other, and the decision taken for each.

| # | Tension | Decision |
|---|---|---|
| T1 | One claim per statement vs the context needed to understand it | Small statements, grouped under subject sections that open with their purpose (C10, C13, C1) |
| T2 | What, not how vs pinned technology and determinism | Technology is pinned only where output depends on it, labelled as deliberate (C9, C16) |
| T3 | Completeness vs economy | Completeness wins; economy applies only to explanation, repetition and emphasis (C12) |
| T4 | Precision vs human reviewability | Precision is carried by examples rather than prose; detail scales with risk (C12); the approver checks review time (D108) |
| T5 | Binding examples vs incidental details they freeze | A binding example states which of its details matter; the rest is illustrative (C7) |
| T6 | Rationale in the text vs separation of what binds | Rationale stays, labelled as rationale (C9) |
| T7 | Free form vs consistent structure | One consistent structure, required only when the set is too large to read whole (C13) |
| T8 | Stable identifiers vs restructuring for clarity | Restructuring is allowed; split or merged statements get new identifiers and the old ones are retired (C14) |
| T9 | Spec follows the code vs spec follows intent | Each statement is marked current, intended or changed; the approver checks intent (C19, D2) |
| T10 | Behaviour that is itself instructions to a model vs no instructions to the agent | The spec describes what the component does; the prompt is code built from it (C9, C20) |
| T11 | Self-contained vs say it once | Self-contained means the spec set, not each file: references within the set are allowed (C2, C11) |
| T12 | Stop on unknowns vs proceed on defaults | Defaults only where stated; any other gap is decided by a person (C8) |
| T13 | Spec as the only source vs proportionality | Depth scales with risk; coverage never does (C12) |
| T14 | Change history vs the spec stating current truth | The spec states current truth only. History lives in version control, except the reason for a removal, kept as labelled rationale (C19) |
| T15 | Plain prose vs exact outputs | Exact outputs go in literal blocks; the prose around them stays plain (C2, C6) |
| T16 | Expected results approved in the spec vs their cost | Examples only where the text alone does not fix one output (C7, C12) |
| T17 | Hand-written vs generated identifiers | Dropped: specific to one toolchain |
| T18 | Edit churn under a change detector | Dropped: specific to one toolchain |
| T19 | Tool enforcement vs free form | Dropped: belongs to tooling and governance |
