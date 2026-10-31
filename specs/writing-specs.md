# Writing meta specs

**Prefix:** SPC

This guideline says how to word a good meta spec. Its goal is that the implementing agent builds what the authors of the meta spec meant. Meta rule SPC-n comes from core dimension Cn in [spec-dimensions.md](https://github.com/jpchauny/claude-plugins/blob/main/research/SDD/spec-dimensions.md). Decision SPC-Tn comes from tension Tn in the same file. That file gives the reasons for each meta rule.

## Purpose and scope

- This guideline is for the people who write meta specs and for the approver.
- It applies to every meta spec, of this repository and of every `<project>-tooling` repository, which must follow it ([DEV-9](https://github.com/jpchauny/claude-plugins/blob/main/specs/development.md#method)). It does not apply to the specs of a project that uses ISF: the module `specs-management` of ISF has its own guide for those, with its own prefix, and neither guide cites the other.
- Where meta specs live and how they change is outside this guideline.
- This guideline covers what a meta spec must say and how the meta spec words it. This includes results that a test can check.
- No meta rule in this guideline requires a particular tool, template or folder structure.
- This guideline is a process document, not a meta spec: nobody implements it, so its meta rules do not apply to it. Its authority comes from the approval of the people who own the process.
- Out of scope (complete list): who writes meta specs; who approves meta specs; how needs are gathered; planning tests; templates and layout; how identifiers are produced; which meta rules a tool enforces.

## Terms

| Term | Meaning |
|---|---|
| Meta spec, meta rule, meta module, meta repository, ISF | As [development.md](https://github.com/jpchauny/claude-plugins/blob/main/specs/development.md#terms) defines them. |
| Approver | The person who approves a change to a meta spec before the component is built. |
| Binding | Describes text that the implementation must satisfy. |
| Claim | One thing that a statement says, which can be true or false. |
| Component | A program, service, meta module or tool that is built from a meta spec. |
| External effect | A change that an operation makes outside the component's own data and that remains after the run: in another system, in the user's files, or in a message to a person. |
| Free | Describes a case where the implementing agent may choose. |
| Hidden input | An input that changes the output but that the caller does not pass in. Examples (not a complete list): the clock, the time zone, the locale, random values, the order in which files or records are listed, the network. |
| Illustrative | Describes text that shows a case but does not bind. |
| Implementing agent | The AI agent that builds code and tests from the meta spec. |
| Invariant | A condition that must hold on every run. |
| Label | A word followed by a colon that marks the role of a statement, for example `Open:` or `Rationale:`. |
| Literal block | Text in code formatting. Its content is exact. |
| Observable output | Anything that a user or another component can see or set from outside the component, including its arguments and its configuration. |
| Open | Describes a case that is marked as undecided. |
| Operation | One thing that a component can be asked to do, for example a command, a request or a function call. |
| Quality | A property of the component as a whole rather than of one behaviour, for example speed, accessibility or the accuracy of generated text. It passes or fails against a measurable threshold (SPC-7). For output that a model generates at runtime, it passes or fails by a rubric and a pass rate (SPC-20). |
| Meta spec set | All the meta specs of one meta repository. |
| Statement | One sentence or list item of a meta spec that carries a claim. |
| Unit | A file, or a section of a file, that a reader loads as one piece. |

<a id="how-to-read-the-rules"></a>
## How to read the meta rules

- This section declares the binding words of this guideline.
- Everywhere in this guideline except after "Why:":
  - "must" and "must not" state an obligation;
  - "should" states a recommendation;
  - "may" states a permission.
- A sentence without one of these words is information.
- The text after "Why:" explains. It does not bind.
- Weak statements break the meta rules on purpose.
- Rewrites are illustrative. Each rewrite uses this same convention, so it shows what binding text looks like.
- An "Applies when:" line states when a meta rule binds.
- The decisions SPC-T4, SPC-T5, SPC-T11, SPC-T14 and SPC-T15 bind in the same way as meta rules.
- The approver's review checks every meta rule. "Checked by:" names the checklist questions that also check the meta rule.
- Each meta rule has these parts, in this order:
  1. the title, which states the meta rule;
  2. for SPC-13 to SPC-20, the "Applies when:" line;
  3. the details, one claim per item;
  4. "Why:";
  5. a weak statement and its rewrite;
  6. "Checked by:".

## Meta rules

SPC-1 to SPC-12 apply to every meta spec. SPC-13 to SPC-20 apply only when their "Applies when:" line holds.

### SPC-1 — A meta spec must open with its purpose and audience, then state its scope and non-goals

- The opening must say what the component is for.
- The opening must say who the component is for.
- After the opening, the meta spec must state what it covers.
- The meta spec must name the systems that the component works with.
- The meta spec must state what is out of scope.
- The meta spec must state what must never happen.
- Each exclusion must be its own sentence.
- Each prohibition must be its own sentence.

**Why:** An agent that reads only part of a meta spec needs the purpose that the statements serve. With the purpose, the agent can handle cases that nobody foresaw. Agents build too much, and where a meta spec says nothing, agents assume that anything is allowed. A stated non-goal tells the agent when to stop. A prohibition in its own sentence gets its own check.

**Weak:** "The booking service handles reservations, and probably should not deal with payments or double bookings."

**Rewrite:** "The booking service lets guests reserve hotel rooms. The booking service covers creating, changing and cancelling reservations. System it works with: the payment service, which takes payments. Out of scope: taking payments. The booking service must never confirm a room that is already booked for that night."

**Checked by:** SPC-Q1.

### SPC-2 — Every sentence must have exactly one reading for a reader who has only the meta spec set

- Sentences must be plain.
- Sentences must be short.
- The approver judges whether a sentence is short.
- Every quantity must be an explicit number with its unit.
- Every absolute word must state what it covers. Examples of absolute words: all, every, never, always.
- Every list in binding text must say whether it is complete or illustrative.
- Binding text must not use "etc." or "such as".
- A pronoun must not point outside its sentence.
- The meta spec must not rely on anything outside the meta spec set and the documents that the meta spec set references. Examples of things outside the meta spec set: conversations, review discussions, code.
- SPC-T11 says what "the meta spec set" means here.

**Why:** The implementing agent cannot ask the author, so it silently picks one reading. Different runs pick different readings, and each run claims to satisfy the same statement. An agent reads a list that does not say whether it is complete as complete, or adds items to it.

**Weak:** "Large orders get free shipping, etc. They usually ship the next day."

**Rewrite:** "An order of 50.00 EUR or more after discounts must ship free. An order placed before 14:00, warehouse local time, must ship on the next working day. Working day: Monday to Friday, except public holidays in the warehouse's country."

**Checked by:** SPC-Q2, SPC-Q3.

### SPC-3 — Each meta spec must define its own domain terms, and each term must keep one meaning across the whole meta spec set

- Each meta spec must define, in its own terms section, every domain term that it uses.
- The meta spec set must not have a central glossary.
- A term that two meta specs define must have the same meaning in both.
- A term must not have synonyms.
- Where a term has a narrower meaning than in everyday use, its definition must say so.
- The meta spec set must be written in one language.
- The only exception to the one-language rule is user-facing text, which must be in the language that the component speaks to its users (SPC-6).

**Why:** Models treat synonyms as different concepts. Models also replace local terms with their public meaning. One vocabulary in one language keeps search and references consistent. A meta spec that defines its own terms can be read alone, without loading a glossary.

**Weak:** "A member can borrow 5 books. A user with an overdue book cannot borrow."

**Rewrite:** "Member: a person with a valid library card. A member may borrow at most 5 books at a time. A member who has an overdue book must not borrow another book."

**Checked by:** the approver's review only.

### SPC-4 — Each behavioural statement must name the actor, the condition and the response

- The statement must name who or what acts.
- The statement must name the trigger or the state in which it applies, for example with "When …" or "While …".
- The statement must name what results.
- Behaviour in steps must use numbered steps.
- Behaviour in steps must list the alternatives that are tried after a failure, in the order in which they are tried.
- Behaviour in steps must state when it stops.
- A numbered list must be used only where order matters.

**Why:** A model fills missing parts from general knowledge. Nobody sees the gap, because the result looks plausible. A stated condition maps directly to a branch in the code and to the setup of a test. Agents read a numbered list as a required order.

**Weak:** "The password is reset and an email is sent."

**Rewrite:** "When a user asks for a password reset for a registered email address, the system must send a reset link to that address."

**Checked by:** SPC-Q4.

### SPC-5 — For each operation that takes input or calls a dependency, the meta spec must state its valid input, its guarantees and its failures

- The meta spec must state what input is valid.
- The meta spec must state what the operation guarantees.
- The meta spec must state exactly what happens in each of these cases (complete list):
  - invalid input;
  - a missing resource;
  - a failed dependency;
  - a timeout;
  - a limit that is reached.
- The meta spec must state the message and the status of each failure exactly (SPC-6).

**Why:** By default, agents build only the case where nothing goes wrong, or they catch every error in the same generic way. Agents also add silent repairs. Where failures are not specified, different agents invent different behaviour, and these differences are the hardest to find.

**Weak:** "The upload handles errors gracefully."

**Rewrite (excerpt):** "Valid input: a JPEG or PNG file of at most 20 MB. When an upload succeeds, the file must be stored unchanged. When the file is larger than 20 MB, the upload must be refused with the error code `FILE_TOO_LARGE` and the message `File too large: the limit is 20 MB.` When the storage service does not answer within 10 seconds, the upload must fail with the error code `STORAGE_TIMEOUT`. After a failed upload, the service must not store any part of the file."

**Checked by:** SPC-Q4.

### SPC-6 — Every observable output must be stated exactly

- The observable outputs include at least: messages, statuses, formats, arguments, configuration with its defaults and the order in which settings win, the order of screens and prompts, log and error output, and interfaces between components.
- User-facing text must be given word for word.
- User-facing text must be in the language that the component speaks to its users.
- Each exact output must state whether a check must match it byte for byte, or which differences the check may allow.
- Where an exact output contains characters that are not visible, the meta spec must name each of them and its position.
- SPC-T15 says where exact outputs go.

**Why:** Components that are built separately meet at interfaces, and they must agree exactly. Stated outputs are what tests check. Without them, tests check internals, agents invent configuration settings, and copied examples silently lose tabs, trailing spaces or line endings.

**Weak:** "The command prints a friendly greeting and exits normally."

**Rewrite:** "The component speaks Spanish to its users. The command `greet Ana` must print `¡Hola, Ana!` followed by one line feed. The command must exit with status 0. The check must match byte for byte."

**Checked by:** SPC-Q4.

### SPC-7 — Every behavioural statement, quality and invariant must have a clear pass or fail

- The pass or fail must be a measurable threshold, a property, or a binding example.
- Where the text alone does not fix one output, the meta spec must give examples. Examples of such cases (not a complete list): boundaries, formats, ordering, refusals.
- Each example must be marked binding or illustrative.
- The meta spec must state the expected result of each example.
- A required set of examples must include the boundary case.
- A required set of examples must include at least one case that is refused or that must not happen.
- For behaviour that depends on earlier state, the examples must show the sequence of inputs and the expected result after each step.
- SPC-T5 says which details of a binding example bind.

**Why:** When a statement is vague, the agent picks one reading and writes tests that confirm it. An agent that writes both the code and the tests puts the same misreading into both. Only an expected result that is approved in the meta spec, so that the implementing agent does not choose it, catches the misreading. When examples show only the normal case, boundary cases and must-not cases drop out silently. Asking for examples only where the text is not enough keeps the cost reasonable.

**Weak:** "Members get a discount on large orders."

**Rewrite:** "A member must get 10% off an order of 100.00 EUR or more. Binding examples, in which only the customer's status and the order amount matter:

- a member's order of 99.99 EUR gets no discount;
- a member's order of 100.00 EUR gets 10.00 EUR off;
- a guest's order of 150.00 EUR gets no discount."

**Checked by:** SPC-Q4 to SPC-Q10.

### SPC-8 — Open cases, defaults and decisions must be explicit

- The meta spec must mark undecided content as open.
- The meta spec must state its assumptions.
- The meta spec must state its defaults.
- For the cases that it does not list, the meta spec must say whether they are forbidden, free or open.
- For each gap that would change output or data, the meta spec must state the default to apply, or mark the case as open.
- A person must decide an open case before the behaviour that depends on it is built.
- A provisional statement must be marked as open, or as a decision with its condition.
- The words "for now" must not be used without a condition.
- The meta spec must record each resolved ambiguity with its reason.

**Why:** Agents fill gaps instead of stopping. Then the agent cites the closest statement, so its guess looks as if it follows the meta spec. A case marked as open shows where guessing is not allowed. A stated default shows where going ahead is allowed.

**Weak:** "For now, refunds go back to the card."

**Rewrite:** "Refunds must go back to the card used for payment. Payment methods not listed here: open. Decision, until bank transfers are supported: refunds must not be made by bank transfer. Open: a refund to a card that has expired. A person must decide this case before refunds are built."

**Checked by:** the approver's review only.

### SPC-9 — Binding text must be visibly separate from explanation

- The meta spec set must use one convention for binding words. Example convention: must, should, may.
- The meta spec set must declare the convention once.
- A meta spec set may adopt the convention of this guideline by reference.
- Rationale must be labelled as rationale.
- Each statement that has an ID must have a rationale: why it exists, and what would go wrong without it.
- A rationale must give reasons that stay true as long as its statement stays as it is. It must not record how the decision was taken: no dates, votes, studies, tool versions or issue numbers. Version control keeps them (SPC-T14).
- A change of a statement must update its rationale in the same change.
- Accepted costs must be labelled as accepted costs.
- A prescribed design must be labelled as deliberate.
- A departure from common practice must be labelled as deliberate.
- The meta spec must describe behaviour. The meta spec must not give instructions to the implementing agent.
- Where the component's behaviour is itself a set of instructions to a model, the meta spec must describe what the component does.
- The instructions given to that model are code built from the meta spec.

**Why:** Agents give equal weight to everything that sounds like an order. Agents treat any hint about how to build something as a requirement. Labelled rationale helps an agent handle cases that nobody foresaw, and stops the agent from "correcting" deliberate choices. The label also keeps the rationale from becoming an obligation.

**Weak:** "Use a queue here because the mail server is slow. Make sure you write tests."

**Rewrite:** "The confirmation email must be sent within 5 minutes of the order. Deliberate design: the email must go through a queue. Rationale: the mail server can take up to 30 seconds to answer, and without a queue the order page would wait for it."

**Checked by:** SPC-Q11.

### SPC-10 — Each statement must carry exactly one claim that can be checked on its own

- Separate cases must be separate items.
- Each section must open with its purpose.

**Why:** When a statement has several claims, an agent implements part of it and reports the whole statement as done. No single check then shows which claim failed.

**Weak:** "The thermostat keeps the set temperature, saves energy at night and warns about faults."

**Rewrite:**

- "While in day mode, the thermostat must keep the room within 0.5 °C of the set temperature."
- "Between 23:00 and 06:00, the thermostat must lower the set temperature by 3 °C."
- "When a sensor gives no reading for 60 seconds, the thermostat must show the warning `Sensor fault`."

**Checked by:** the approver's review only.

### SPC-11 — Each fact must be stated in one place, as a general statement followed by its exceptions

- Other places must refer to that fact, not repeat it.
- Exception: a term definition is repeated in each meta spec that uses the term (SPC-3).
- The exceptions to a general statement must be listed explicitly with it.
- Where two statements or two qualities can collide, the meta spec must state which one wins.

**Why:** Copies in different words drift apart, and the agent implements whichever copy it loaded. Exceptions spread through the text get missed. When the meta spec does not say which statement wins, the agent follows whatever text is closest in what it has loaded.

**Weak:** Chapter 2: "Parking costs 2 EUR per hour." Chapter 5: "Residents park for free." Chapter 7: "Sundays are free."

**Rewrite:** "Parking must cost 2.00 EUR per hour. Exceptions (complete list):

- parking must be free on Sundays;
- parking must be free for residents with a permit."

**Checked by:** SPC-Q12.

### SPC-12 — The amount of specification must match the size and risk of what it specifies

- Every sentence must be needed.
- Shortening must apply only to explanation, repetition and emphasis.
- Shortening must never remove conditions, exclusions, error behaviour or required examples (complete list; SPC-1, SPC-4, SPC-5, SPC-7).
- Size and risk change only the depth of detail. Every behaviour, output and error path in what the meta spec covers must still be specified, whatever its risk.
- Emphasis must be used only on the few critical statements.
- The approver judges which statements are critical.
- SPC-T4 says how precision and review effort are balanced.

**Why:** Agents follow instructions less well as the number of statements grows. Agents and approvers skim long text. Writers who cut text tend to cut boundary cases and exclusions first, and agents then invent exactly those.

**Weak:** "IMPORTANT!!! Dates MUST ALWAYS be shown correctly. This matters a lot, because users rely heavily on dates every day."

**Rewrite:** "Dates must be shown in the form `YYYY-MM-DD`."

**Checked by:** SPC-Q13, SPC-Q14.

### SPC-13 — A large meta spec set must be split into units, each small enough to read whole for one task

**Applies when:** the meta spec set is too large to read whole for one task.

- The meta spec set must group statements by subject, so that all the statements on a topic are found together.
- The meta spec set must keep statements that apply to the whole meta repository in units apart from statements that apply to one component.
- The meta spec set must use one consistent structure.

**Why:** An agent uses well only part of the text that it can load, and it often misses text in the middle of a long input. The structure decides what an agent loads. An agent does not see a statement that is in the wrong unit.

**Weak:** One file of 4,000 lines, with the rounding statements for all amounts written inside the checkout chapter.

**Rewrite:** "`rounding.md` holds the rounding statements for every amount. `checkout.md` holds the checkout statements and refers to `rounding.md` for rounding."

**Checked by:** the approver's review only.

### SPC-14 — Each statement must have a stable identifier

**Applies when:** code, tests, reviews or other statements refer to individual statements.

- Each identifier must be unique in the meta spec set.
- An identifier must never change.
- An identifier must never be reused.
- An identifier must not depend on the file or the section where the statement is.
- A statement that is split or merged must get new identifiers.
- The old identifiers of a split or merged statement must no longer be used.
- Related statements must refer to each other by identifier.

**Why:** People and agents must be able to point to one statement without doubt. A reused identifier, or an identifier based on location, silently changes what an existing reference points to.

**Weak:** "As stated in section 3.2, second bullet, …"

**Rewrite:** "As stated in SHIP-14, …"

**Checked by:** the approver's review only.

### SPC-15 — The meta spec must fix exactly one output

**Applies when:** several results are possible, or the output depends on a hidden input.

- Where several results are possible, the meta spec must give a complete, ordered list of tie-breakers for choosing between equal results.
- For each hidden input, the meta spec must say how the hidden input is fixed or supplied.

**Why:** Two runs that implement "pick the best match" give different results unless the text resolves every tie. Hidden inputs give agent-written tests that pass on some runs and fail on others, or tests that use one fixed value by accident.

**Weak:** "Show the nearest store. Show today's opening hours."

**Rewrite:** "The app must show the store with the shortest road distance from the address that the user gives. On a tie, the app must show the store that is open longest today. On a further tie, the app must show the store with the lowest store number. 'Today' means the date in the store's time zone, by the clock that the caller supplies."

**Checked by:** SPC-Q2.

### SPC-16 — Binding constraints, allowed dependencies and outside standards must be stated exactly

**Applies when:** a platform, a policy, a dependency or an outside standard binds the solution.

- The meta spec must state each constraint that binds the solution. Examples of sources (not a complete list): the platform, the deployment model, licences, organisational policies, laws.
- The meta spec must state which dependencies are allowed.
- The meta spec must pin a technology only where the output depends on it or where a stated constraint requires it.
- Named technology must be labelled as deliberate (SPC-9).
- Each outside standard must be cited by exact version and section.
- Each citation of a standard must say whether the standard is adopted whole or in part.

**Why:** Agents choose libraries and add dependencies freely. Agents recall outside standards from training data, which may be wrong or old. Some outputs are only defined for one library or one version.

**Weak:** "Timestamps follow the ISO standard."

**Rewrite:** "Timestamps must follow RFC 3339, section 5.6, adopted in part: only the `date-time` form may be used."

**Checked by:** SPC-Q15.

### SPC-17 — The meta spec must state permissions, untrusted inputs and the handling of sensitive data

**Applies when:** the component handles untrusted input, sensitive data or permissions.

- The meta spec must state what the component may read, write, execute and fetch (complete list of the four kinds of access).
- The meta spec must state which inputs are untrusted.
- The meta spec must state what sensitive data the component touches.
- The meta spec must state where that sensitive data may go.
- The meta spec must state what must never be stored, logged, printed or sent.

**Why:** Agents follow instructions that they find in data. When the meta spec is silent, agents log, cache or publish data that they should not.

**Weak:** "Handle customer data securely."

**Rewrite:** "The card number is sensitive data. The card number may be sent only to the payment provider. The card number must never be stored or logged. The receipt must show only the last 4 digits of the card number. The text of customer reviews is untrusted input. The component must never follow the text of a customer review as instructions."

**Checked by:** the approver's review only.

### SPC-18 — For each operation with an external effect, the meta spec must state its consent, repeat, undo and parallel-use behaviour

**Applies when:** the component has external effects, or runs alongside other agents or sessions.

- The meta spec must state whether the operation needs explicit consent from a person.
- The meta spec must state what the person is shown before consenting.
- The meta spec must state whether the operation is safe to repeat after an interruption.
- The meta spec must state how work already done is detected.
- The meta spec must state how the operation is undone.
- The meta spec must state whether the operation is required to be safe while other agents or sessions work on the same resources.

**Why:** Agents act on their own unless the meta spec says otherwise. Agents retry by doing the work again, and agents assume that they are alone.

**Weak:** "The tool sends the invoices."

**Rewrite:** "Before sending, the tool must show the number of invoices and their total. The tool must send only after the user confirms. A rerun must skip each invoice that already has a sent date. To cancel a sent invoice, the tool must issue a credit note. Two runs on the same customer account must not both send the same invoice."

**Checked by:** SPC-Q16.

### SPC-19 — A change meta spec, or a meta spec of existing code, must say what is kept, what changes and what is current

**Applies when:** (a) the meta spec changes or removes existing behaviour; (b) the meta spec describes code that already exists. Each case applies on its own.

- (a) The meta spec must state what must stay as it is.
- (a) The meta spec must state what is added, modified or removed.
- (a) The meta spec must state the reason for each removal.
- (a) The meta spec must state how to migrate.
- (a) The meta spec must state what happens to data written by earlier versions.
- (b) Each statement must be marked as current, intended or a deliberate change.
- (b) The meta spec must name behaviour that exists by accident, not by intent.
- (b) The meta spec must restate implicit behaviour that lives outside the code. Examples (not a complete list): configuration, prompts, scripts, team conventions.
- (b) The meta spec must say which existing code it does not yet govern.
- SPC-T14 says how this meta rule relates to change history.

**Why:** A change meta spec describes only the change. An agent that is free to rewrite then breaks nearby behaviour, brings back what was removed for a reason, and assumes that there is no stored data. A meta spec recovered from code turns the accidents of the code into rules, and drops what was never written down.

**Weak:** "Remove the fax field."

**Rewrite:** "Removed: the contact form must no longer have a fax number field. Rationale: no customer has entered a fax number since 2021. Unchanged: all other contact fields must keep the validation stated in CONTACT-3 to CONTACT-9. Migration: the next schema migration must delete the fax number column, together with the stored fax numbers."

**Checked by:** SPC-Q17.

<a id="spc-20--where-a-model-produces-output-or-decides-on-invocation-at-runtime-the-spec-must-separate-invariants-from-qualities-bound-invocation-and-name-the-validated-model"></a>
### SPC-20 — Where a model produces output or decides on invocation at runtime, the meta spec must separate invariants from qualities, bound invocation, and name the validated model

**Applies when:** a language model generates the component's output at runtime, or decides at runtime whether to invoke the component.

- The meta spec must separate the invariants from the qualities.
- Each quality of the output that the model generates must be judged by a rubric, an evaluation set, and a pass rate over a stated number of runs.
- Where a model decides whether to invoke the component, the meta spec must state the situations in which the model must invoke the component.
- Where a model decides whether to invoke the component, the meta spec must state the situations in which the model must not invoke the component.
- The meta spec must name the model and the settings that the behaviour was validated on.
- The meta spec must state what must still hold when that model or those settings change.

**Why:** Exact expected outputs do not work for output that is different on each run. Without invariants and qualities, an agent checks one sample, or checks nothing. Without a named model, nobody can tell a regression from a change of model.

**Weak:** "The assistant writes good summaries."

**Rewrite:** "Invariant: each summary must have at most 80 words. Invariant: a summary must not name a person who is absent from the source. Quality: over 3 runs on the 50-article evaluation set, at least 45 summaries in each run must score 4 or more on the accuracy rubric. Validated on: model X, temperature 0.2. After a change of model, the invariants must still hold."

**Checked by:** the approver's review only.

## Checklist for the approver

The approver must answer these questions before approving a meta spec. The questions are judgements that need a reviewer, not wording meta rules. Their IDs are SPC-Q1 to SPC-Q17. The "Source" column gives the dimension in the research file.

| ID | Question | Meta rule | Source |
|---|---|---|---|
| SPC-Q1 | Does the meta spec name everyone it serves, including any agent that uses the component at runtime? | SPC-1 | D23 |
| SPC-Q2 | Would two independent agents build the same behaviour from the text? | SPC-2, SPC-15 | D82 |
| SPC-Q3 | If a new agent session that has only the meta spec set builds the component or asks questions about it, does that show no gap and no second reading? | SPC-2 | D130 |
| SPC-Q4 | Does the meta spec set as a whole cover every operation, state, interface, error path and quality? | SPC-4 to SPC-7 | D5 |
| SPC-Q5 | Does the meta spec as a whole have measurable success criteria that name no technology? | SPC-7 | D18 |
| SPC-Q6 | Does each statement have a check that an agent can run? | SPC-7 | D56 |
| SPC-Q7 | Do the examples use one consistent form of input and expected output? | SPC-7 | D60 |
| SPC-Q8 | Does the choice between realistic and minimal examples fit what each example must show? | SPC-7 | D62 |
| SPC-Q9 | Does each statement about an interaction with a dependency say whether its check may use a substitute for the real dependency? | SPC-7 | D68 |
| SPC-Q10 | Where generated outputs must be accessible, is accessibility stated as a measurable quality? | SPC-7 | D117 |
| SPC-Q11 | Where the meta spec prescribes a design that follows an existing pattern, does the meta spec state that pattern in the meta spec set and label it as deliberate? | SPC-9 | D65 |
| SPC-Q12 | Is the whole meta spec free of contradictions and gaps before it goes to the implementing agent? | SPC-11 | D71 |
| SPC-Q13 | Does each statement express a real need, so that removing it would break something? | SPC-12 | D1 |
| SPC-Q14 | Can the approver review the meta spec in a reasonable time? | SPC-12 | D108 |
| SPC-Q15 | Can what is specified be built within the platform limits, the cost and the time available? | SPC-16 | D3 |
| SPC-Q16 | For a component with external effects, does the meta spec name the real systems that its tests must never touch? | SPC-18 | D122 |
| SPC-Q17 | Does the meta spec say what the people it serves want, and not just copy current behaviour? | SPC-19 | D2 |

## Decisions between meta rules

Some meta rules conflict. The meta rules above already settle most of these conflicts. The decisions below settle the rest. Decision SPC-Tn comes from tension Tn in the research file. The other tensions (T1 to T3, T6 to T10, T12, T13, T16) are settled inside the meta rules; T17 to T19 were dropped.

| ID | Conflict | Decision |
|---|---|---|
| SPC-T4 | Precision versus the effort of review | Where short prose does not give enough precision, the meta spec must add examples, not longer prose. The amount of detail must match the risk (SPC-12). SPC-Q14 checks the review time. |
| SPC-T5 | Binding examples versus details in them that do not matter | A binding example must state which of its details matter. Its other details do not bind. |
| SPC-T11 | A self-contained meta spec versus saying each fact once | "The meta spec set" in SPC-2 means the whole meta spec set, not each file. A statement may refer to another place in the meta spec set (SPC-11). |
| SPC-T14 | Change history versus the meta spec as the approved behaviour | The meta spec must state the behaviour as it is approved now. The meta spec must not record earlier versions; version control keeps them. Exception: the reason for each removal must be kept, labelled as rationale (SPC-9, SPC-19). The list of what a change adds, modifies or removes (SPC-19) describes the approved change, and is not history. |
| SPC-T15 | Plain prose versus exact outputs | Exact outputs must go in literal blocks. The prose around a literal block must stay plain (SPC-2). |
