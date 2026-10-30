# Workflow orchestration

**Prefix:** WFO

**Audience:** The people who start and control a run of a project from its orchestration repository, the requester among them; whoever builds the skills, the scripts and the hook of the plugin `workflow-orchestration`

**Scope:** Running the flow across the modules from the orchestration repository: where the orchestrator runs, how a person starts and controls a run, how each step runs as a headless session in the repository of its layer, the loop that implements the acceptance units one by one, the queue of the requester, the evidence runs that the orchestrator makes, and what the orchestrator never does. The run itself, the order of its steps and their hand-offs, is methodology, in [flow.md](../../development-methodology/specs/flow.md); what the orchestration repository is, in [LAY-11](../../development-methodology/specs/layers.md#the-orchestration-repository); the steps of an evidence run, in [ACU-34](../../acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence); when an acceptance unit is done, in [acceptance-management](../../acceptance-management/specs/module.md). Systems it works with: Claude Code, which runs the headless sessions; git and GitHub, which hold the repositories of the project. Out of scope: the work of each step, which the module of its layer does. The orchestrator must never do the work of a layer.

The module `workflow-orchestration` of the app Indra Software Factory, listed in [app.md](../../../specs/app.md). The orchestrator runs the steps of a run as [ORC-15](../../development-methodology/specs/flow.md#start-a-run) says, and does not restate them.

## Terms

| Term | Meaning |
|---|---|
| Orchestrator | The skills, the scripts and the hook of the plugin `workflow-orchestration`, in a session of the orchestration repository; the actor of every requirement that names no other. |
| Headless session | A session of Claude Code that the orchestrator starts with `claude -p` and one prompt, in the repository of one layer; it asks no person anything, and ends when it has answered. |
| Increments of the run | The increments of `plan.json` ([ACU-39](../../acceptance-management/specs/module.md#the-plan-of-implementation)) that a run implements (WFO-2). |
| Queue of the requester | The acceptance units of the increments of the run that wait only for the requester (WFO-6). |
| Token of the code repositories | The token of GitHub with which the orchestrator reads the code repositories, and that can only read them (WFO-9). |
| Plugin root | The folder in which Claude Code installed the plugin `workflow-orchestration`, as the environment variable `CLAUDE_PLUGIN_ROOT` gives it to a hook. |
| Head before the step of layer 2 | The head of the default branch of the norms repository on GitHub, read before the headless session of the step of layer 2 starts (WFO-13). |
| Head after the step of layer 2 | The head of the default branch of the norms repository on GitHub, read once the headless session of the step of layer 2 has ended (WFO-13). It is not always the commit of layer 2 of the run: after a pull of NRM-10 it is the merge commit of the pull. |

The terms run, step and hand-off are those of [flow.md](../../development-methodology/specs/flow.md#terms); the terms orchestration repository, repository of a layer, specs repository, norms repository, acceptance repository, code repository, norm, norm hash, derived norm, derived norm ID and derived norm fingerprint are those of [layers.md](../../development-methodology/specs/layers.md#terms); the terms acceptance unit, increment, requester, evidence run, done profile, state, reference commit, product build, derived norm citation and acceptance unit behind layer 2 are those of [acceptance-management](../../acceptance-management/specs/module.md#terms); the terms list of derived norms, derived norm behind its norms, types of derived norms of a commit, commit of layer 2 of the run and commit before the last step are those of [norms-management](../../norms-management/specs/module.md#terms).

## Use cases

| Use case | Spec |
|---|---|
| `run` | Not yet specified: starts a run, or resumes one that stopped (WFO-2). |
| `evidence-run` | Not yet specified: makes one evidence run (WFO-8). |
| `queue` | Not yet specified: shows the queue of the requester (WFO-6). |

The messages of each use case, word for word, are in its spec.

## Where the orchestrator runs

- **WFO-1.** The orchestrator runs only in the orchestration repository, the one repository where [APP-6](../../development-methodology/specs/layers.md#where-each-module-is-installed) enables the plugin. Before it does anything else, each use case of the module finds the entry of its repository in `project.json` as [ORC-21](../../project-management/specs/module.md#where-the-repositories-are) says. When that entry has no `role` `orchestration`, the use case writes nothing, starts nothing, and says `workflow-orchestration: runs only from the orchestration repository`. Then it compares its `project.json` as [ORC-24](../../project-management/specs/module.md#where-the-repositories-are) says.

  Rationale: from the repository of a layer, the session of the orchestrator
  would run with the modules and the hooks of that layer, and its own hook
  would not guard the repositories of the other layers.

## Start and control a run

- **WFO-2.** A person starts a run with `/workflow-orchestration:run`, in a session of the orchestration repository.
  - Its argument is the names of the increments of the run, each the `name` of an increment of `plan.json`. Without an argument, the increments of the run are every increment of `plan.json`.
  - The run starts from the head of the default branch of the specs repository on GitHub when the use case starts ([ORC-15](../../development-methodology/specs/flow.md#start-a-run)).
  - When an increment that the argument names is not in `plan.json` at the hand-off of the step of layer 3 ([ACU-41](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event)), the run stops before the step of layer 4, and says which increment is missing.
  - A run keeps nothing between two invocations of `run`, in no repository and in no file. A person resumes a run that stopped by invoking `run` again, which starts a new run. Each step of the new run does only what is left: layer 2 regenerates only what changed ([LAY-3](../../development-methodology/specs/layers.md#rules)), the step of layer 3 proposes no change where none is needed ([ACU-37](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event)), and the loop of WFO-5 passes over the acceptance units that need no more work.

  Rationale: done is a state, computed from the repositories
  ([ACU-23](../../acceptance-management/specs/module.md#the-ladder-of-states),
  [ACU-27](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event));
  a run that stored where it was could disagree with them.

- **WFO-3.** The orchestrator runs each step of a run as one or more headless sessions, each with the clone of the repository of its layer as its working directory, found as [ORC-21 and ORC-22](../../project-management/specs/module.md#where-the-repositories-are) say. Each headless session runs with the modules, the hooks and the `.claude/settings.json` of that repository ([APP-6](../../development-methodology/specs/layers.md#where-each-module-is-installed)). The orchestrator does no work of a step: it starts the headless session, gives it its prompt (WFO-4), waits until it ends, and reads its exit status and its last message. The steps, and what their headless sessions run (complete list):

  | Step | Repository | Use cases, in this order |
  |---|---|---|
  | Layer 2 | The norms repository | `/norms-management:build`, `/norms-management:verify` and the derived-norms generators ([ORC-8](../../norms-management/specs/module.md#regenerate-the-norms), [NRM-2](../../norms-management/specs/module.md#derive-the-derived-norms)) |
  | Layer 3 | The acceptance repository | `/acceptance-management:define`, then `/acceptance-management:plan` ([ACU-37](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event)) |
  | Layer 4 | Each code repository | `/code-implementation:implement`, one headless session per acceptance unit and code repository (WFO-5) |

  When a headless session ends with an exit status other than 0, the run stops, and the orchestrator says which use case ended so, in which repository, with its last message.

  After the step of layer 2, the run stops, ends or goes on with the step of layer 3 as WFO-13 says.

  Rationale: each module is enabled only in the repository of its layer, and
  the hooks of that layer guard what its session does; a step that ran in the
  session of the orchestrator would see every repository of the project, with
  none of those hooks.

- **WFO-13.** After the step of layer 2, the orchestrator stops the run, ends it or goes on with the step of layer 3 as [ORC-10](../../norms-management/specs/module.md#regenerate-the-norms) says. ORC-10 reads two inputs: the changes of `data/report.md`, and, in the report of [NRM-11](../../norms-management/specs/module.md#derive-the-derived-norms), the derived norms that changed, the change of the order of the types, the lists of derived norms that cannot be read and the case of no comparison, which a script computes, not the model. A script of the orchestrator computes both inputs from the norms repository on GitHub, by the rules of NRM-11, and never reads them from the last message of the headless session, where the report of NRM-11 is text that a model passed on. The script, in these steps, in this order:
  1. Before it starts the headless session of the step, it reads the head before the step of layer 2, with the credentials of the person who runs the orchestrator. Once the headless session has ended, it reads the head after the step of layer 2, with the same credentials. It then finds the commit of layer 2 of the run, the hand-off of the step ([ORC-9](../../norms-management/specs/module.md#regenerate-the-norms)), by the first case that holds (complete list):
     1. When the two heads are the same commit, the step made no commit ([NRM-9](../../norms-management/specs/module.md#derive-the-derived-norms)), and the commit of layer 2 of the run is the head before the step of layer 2, as NRM-11 says.
     2. Otherwise it walks the first parents from the head after the step of layer 2, that head included, and stops at the first commit that is the head before the step of layer 2 or one of its ancestors, that commit excluded: these are the commits of the step. A commit of the step with two parents is the merge commit of a pull of [NRM-10](../../norms-management/specs/module.md#derive-the-derived-norms), and the commits that the pull brought are not first parents, so the walk never meets them. When exactly one commit of the step has one parent, it is the commit that the step made, and it is the commit of layer 2 of the run, never the merge commit of the pull, as NRM-11 says.
     3. Otherwise the run stops before the step of layer 3, and the orchestrator says, byte for byte once filled, where `<before>` and `<after>` are the head before and the head after the step of layer 2, and `<count>` the number of commits of the step with one parent:

        ```text
        workflow-orchestration: the commit of layer 2 of the run cannot be found between <before> and <after> of the norms repository (NRM-11): <count> commits of the step have one parent, and one must; the run stops after layer 2
        ```

  2. It reads from GitHub, with the same credentials, never from the clone of the project folder, the files of the norms repository at the commit of layer 2 of the run, and the commits and the files that NRM-11 compares it with. The norms that changed are the lines of `data/report.json` at the commit of layer 2 of the run, which lists the changes of `data/report.md` ([R63](../../norms-management/specs/norms-versions.md#data-and-outputs)); none when that file holds no line or does not exist, which GitHub answers as the paragraph below these steps says.
  3. It compares the derived norms of the commit of layer 2 of the run by every rule of NRM-11, and by no other: the commit it is compared with, which is the commit before the last step, not merely the first parent of the commit of layer 2 of the run, the types compared and their order, the derived norms `new`, `changed` and `gone`, the lists that count as a list with no derived norm, the lists that cannot be read, the change of the order of the types, and the commit that gives no comparison. It checks a list of derived norms ([NRM-12](../../norms-management/specs/module.md#the-list-of-derived-norms)) only as NRM-12 says of a list read alone, and, at the commit of layer 2 of the run, against `data/tree.jsonl` of that commit, as rule 5 of NRM-11 says, so that a derived norm behind its norms stops the run; it reads no file that its `path` names.
  4. When the commit of layer 2 of the run gives no comparison (NRM-11, rule 2), the run stops before the step of layer 3, and the orchestrator says, byte for byte once filled, where `<commit>` is the commit of layer 2 of the run, and `<reason>` the words of the first case of the list of rule 7.2 of NRM-11 that holds. A commit read from GitHub can meet only the last three cases of that list, in its order (complete list): the parents of a commit of the walk along the first parents cannot be read, `project.json` cannot be read at that commit, and its `derived_norms` does not meet [ORC-20](../../project-management/specs/module.md#where-the-repositories-are):

     ```text
     workflow-orchestration: the types of derived norms of <commit> of the norms repository cannot be read (NRM-11): <reason>; the run stops after layer 2 (ORC-10)
     ```

  5. Otherwise, when a list cannot be read at the commit of layer 2 of the run (NRM-11, rule 5), the run stops before the step of layer 3. For each such list, in the order of the types compared, the orchestrator says, byte for byte once filled, where `<type>` is the type, `<path>` the path of the list in the norms repository, `<commit>` the commit of layer 2 of the run, and `<why>` `it does not exist` when the list does not exist at that commit, and otherwise the first thing of NRM-12, or of the check against `data/tree.jsonl`, that the list does not meet, as rule 7 of NRM-11 says, in the words of the table of rule 7 of NRM-11 and of the cases of the check against `data/tree.jsonl` below that table:

     ```text
     workflow-orchestration: the list of derived norms of the type <type>, <path>, cannot be read at <commit> of the norms repository (NRM-11): <why>; the run stops after layer 2 (ORC-10)
     ```

  6. Otherwise, when no norm changed, no derived norm changed and the order of the types did not change, the run ends, and the orchestrator says, byte for byte once filled, where `<commit>` is the commit of layer 2 of the run:

     ```text
     workflow-orchestration: no norm, no derived norm and no order of the types of derived norms changed at <commit> of the norms repository; the run ends after layer 2 (ORC-10)
     ```

  7. Otherwise the orchestrator starts the step of layer 3, with the commit of layer 2 of the run in its prompt (WFO-4).

  The script reads GitHub through its REST API, with the credentials of the person who runs the orchestrator, and makes each read once, with no retry. A read fails in these cases, and the first that holds names it (complete list):
  1. GitHub does not answer within 30 seconds: `no answer within 30 seconds`.
  2. The connection to GitHub fails: `the connection failed`.
  3. GitHub answers with the HTTP status 404 to the read of a head or of a commit of the walk of step 1: `it does not exist`.
  4. GitHub answers with an HTTP status other than 200 and other than the 404 of the next paragraph, among them credentials that GitHub refuses and a rate limit that is reached: `GitHub answered with status <status>`, where `<status>` is the status in decimal.
  5. GitHub answers with the HTTP status 200 and an answer that does not have the form that the REST API of GitHub documents for that read: `the answer cannot be read`.

  The HTTP status 404 is not a read that fails in two cases (complete list): to the read of a file at a commit, the file does not exist at that commit (steps 2, 4 and 5); to the read of a commit of the walk along the first parents of NRM-11, the parents of the commit of the walk whose parent it is cannot be read (step 4). When a read fails, the script reads nothing more, and the run stops, whatever the reads before it gave: before the step of layer 2, with no headless session started, when it is the read of the head before the step of layer 2, and otherwise before the step of layer 3. A read that fails is never a file that does not exist, a list that cannot be read nor a commit that gives no comparison. The orchestrator says, byte for byte once filled, where `<what>` is `the head of the default branch` for the read of a head, `the commit <commit>` for the read of a commit, and `<path> at <commit>` for the read of a file, with `<commit>` in its 40 lower-case hex digits and `<path>` the path of the file from the root of the norms repository; `<why>` the words of the case above that holds; and `<when>` `before layer 2` for the read of the head before the step of layer 2, and otherwise `after layer 2`:

  ```text
  workflow-orchestration: <what> of the norms repository cannot be read from GitHub: <why>; the run stops <when>
  ```

  Rationale: whether layers 3 and 4 run must not depend on a reading of text
  that a model wrote
  ([ORC-25](../../code-implementation/specs/module.md#implement-the-changed-norms)),
  and a comparison made by the rules of NRM-11, and only by them, gives the
  same derived norms that changed, the same lists that cannot be read, the
  same change of the order of the types and the same stop as the report of
  NRM-11, without the text, so that the orchestrator and
  `/norms-management:build` decide ORC-10 the same way. A derived norm counts
  as a norm does, since the acceptance units and the code cite it with its
  derived norm fingerprint
  ([LAY-12](../../development-methodology/specs/layers.md#rules)). Why a step
  that makes no commit is compared as if it had made it, why the merge commit
  of a pull is never compared, which commit the comparison goes back to, why a
  type that `derived_norms` no longer names has its derived norms `gone`, why
  a new order of the types calls for layer 3, and why a list that cannot be
  read stops the run, NRM-11 and ORC-10 say. A read from GitHub that fails
  stops the run, and is never taken for a file that does not exist: a
  `data/report.json` that GitHub did not return would count as no norm
  changed, and the run could end after layer 2 with norms that changed. The step of layer 2 makes at
  most one commit (NRM-9) and merges at most once (NRM-10), so a walk that
  finds no commit with one parent, or more than one, met commits that are not
  of that step, such as those of another session that pushed to the same
  branch; comparing a commit that is not the one of the step could end the run
  while layers 3 and 4 have work to do, so the run stops instead.

- **WFO-4.** The orchestrator is the user of the use case that a headless session runs. The prompt of the headless session names the use case, and holds (complete list):
  - the commits that the step reads in the run: the commit of layer 2 of the run (WFO-13) for the step of layer 3 ([ACU-37](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event)); that commit and the hand-off of the step of layer 3 for the step of layer 4 ([ORC-25](../../code-implementation/specs/module.md#implement-the-changed-norms));
  - for implement, the unit ID of the acceptance unit, as the requested acceptance unit ([IMP-14](../../code-implementation/use-cases/implement/specs/implement.md#implement-a-task)), and, for each group of its components before the group of the code repository, that its part is implemented (WFO-5).

  The prompt holds no file and no path of a repository that the step must not receive (ORC-18). How a step that needs the decision of a person runs headless is open question 1.

  Rationale: a headless session cannot ask; what the use case would ask its
  user must be in its prompt.

- **WFO-5.** Once the step of layer 3 has its hand-off ([ACU-41](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event)), the orchestrator implements the acceptance units of the increments of the run one by one, in the order of `plan.json` ([ACU-39 and ACU-42](../../acceptance-management/specs/module.md#the-plan-of-implementation)). It passes over each acceptance unit that is at least `validated` ([ACU-23](../../acceptance-management/specs/module.md#the-ladder-of-states)) or in the queue of the requester (WFO-6). For each other acceptance unit, it takes these steps, in this order:
  1. For each group of the `components` of the acceptance unit, in their order, and for each component of the group, in the order of the group, it starts one headless session of implement in the code repository of that component, and waits until it ends. Deliberate design: one headless session at a time, although ACU-42 allows the components of one group in parallel.
  2. It makes an evidence run (WFO-8), and computes the states (WFO-10).
  3. When the acceptance unit is at least `validated`, or in the queue of the requester, it goes on with the next acceptance unit.
  4. Otherwise it takes steps 1 to 3 again for the same acceptance unit, at most 3 times in all for that acceptance unit in the run. After the third time, the run stops, and the orchestrator says which acceptance unit is neither at least `validated` nor in the queue of the requester, the conditions of [ACU-16](../../acceptance-management/specs/module.md#when-an-acceptance-unit-is-done) that do not hold for it, the result of each of its acceptance tests in the last evidence run, and how each headless session of implement ended.

  The loop ends when each acceptance unit of the increments of the run is at least `validated` or in the queue of the requester. The orchestrator then shows the queue of the requester (WFO-6).

  Rationale: in the order of the plan, each acceptance unit gets its evidence
  before the next one builds on it; the bound on the attempts keeps one
  acceptance unit that does not pass from using up the run.

- **WFO-6.** The queue of the requester is computed, never stored: it is the acceptance units of the increments of the run that are not at least `validated`, and whose conditions of [ACU-16](../../acceptance-management/specs/module.md#when-an-acceptance-unit-is-done) that do not hold, as their done profile requires them ([ACU-19](../../acceptance-management/specs/module.md#done-profiles)), are only of these (complete list): condition 2 under the done profile `prototype`, a demo; condition 3, the validation; condition 5, the acceptance of a deviation. The script of [ACU-27](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event) computes it.
  - The orchestrator never waits for the queue: an acceptance unit in it does not stop the loop of WFO-5, and the acceptance units after it are implemented, those that depend on it included.
  - The requester works through the queue when the requester can, in the acceptance repository, where the acceptance architect records each demo, validation and deviation in a change that the requester approves ([ACU-35](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event), [LAY-9](../../development-methodology/specs/layers.md#rules)).
  - The orchestrator shows the queue at the end of the loop of WFO-5, and when a person invokes `/workflow-orchestration:queue`, which computes the states with the copies that WFO-10 makes, without an evidence run: each acceptance unit, with the conditions it waits for.

  Rationale: validating is the requester's, and the agents need no requester
  to go on; a loop that waited for each validation would stand still whenever
  the requester is away. A validation holds across changes of the code while
  the acceptance unit stays `verified`
  ([ACU-24](../../acceptance-management/specs/module.md#the-ladder-of-states)),
  so validating later loses nothing. Accepted cost: a later acceptance unit
  may build on one that the requester then does not accept; the change goes
  back through layer 3
  ([ACU-47](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event)),
  and the code of the acceptance units it touches is implemented again.

- **WFO-7.** A run waits for a person only in these cases (complete list): the step of layer 3, until the requester has decided on each change ([ACU-37 and ACU-41](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event)); a step that fails or finds a drift ([ORC-8](../../norms-management/specs/module.md#regenerate-the-norms), [ORC-14](../../drift-management/specs/module.md#report-a-drift)); the stops of WFO-2, WFO-3, WFO-5 and WFO-13; an evidence run that fails ([ACU-34](../../acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence), WFO-9). The queue of the requester is never one of them (WFO-6).

  Rationale: layer 4 implements only what the requester approved in layer 3
  ([ACU-41](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event)), so the step of layer 3 waits; what the requester validates after
  the code exists does not.

## The evidence run

- **WFO-8.** The orchestrator makes an evidence run ([ACU-34 and ACU-76](../../acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence)) in step 2 of WFO-5, and when a person invokes `/workflow-orchestration:evidence-run`. It makes each evidence run in a folder that it creates in the temporary folder of the system, outside the project folder ([PRJ-1](../../project-management/specs/module.md#the-project-folder)), in these steps, in this order:
  1. It clones there the acceptance repository, at the head of its default branch on GitHub.
  2. It takes the steps of ACU-34 in that clone, with the copies of step 4 of ACU-34 made in that folder, and `produced_by` as [ACU-35](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event) says for the orchestrator. Each line of kind `test` that it adds holds in `for` every field that ACU-35 lists, `derived_norm_fingerprints` among them, read from the files of `acceptance_commit` as ACU-35 says.
  3. Before the commit of step 6 of ACU-34, it checks the lines that it adds as the job that pushes `records/` checks them in [CRP-1](../../project-management/use-cases/create-project/specs/create-project.md#create-a-project) (the scenario outline "The code of layer 4 cannot change the recorded evidence"). When one check fails, it commits nothing, and says which check failed.
  4. It commits `records/` in that clone, and pushes it to the default branch of the acceptance repository, with the credentials of the person who runs it.
  5. It removes the folder, whether the evidence run succeeded or failed.

  It never runs an evidence run in a clone of the project folder.

  Rationale: the clones of the project folder are the working trees of the
  sessions of the layers, and may hold work that is not committed; an
  evidence run tests only what is committed, and changes no working tree of a
  person.

- **WFO-9.** The orchestrator reads the code repositories only with the token of the code repositories: a fine-grained token of GitHub with read-only access to the contents of the code repositories of `project.json`, and to no other repository. The person creates it, and saves it, alone, in the file `~/.config/indra-software-factory/<owner>/<name>/code-read-token`, readable only by that person, where `<owner>/<name>` is that of the orchestration repository in `project.json` ([CRP-3](../../project-management/use-cases/create-project/specs/create-project.md#create-a-project)). The orchestrator never reads a code repository with another credential of the person, nor with a credential helper of git. When an evidence run reaches step 2 of [ACU-34](../../acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence) and that file does not exist, cannot be read or is empty, the evidence run adds no line to `records/`, ends, and says, byte for byte once filled, where `<path>` is the path of the file with `~` replaced by the home folder of the person:

  ```text
  workflow-orchestration: no token of the code repositories in <path>; create a fine-grained token with read-only access to the contents of the code repositories, and save it there
  ```

  Rationale: a token that can only read the code repositories cannot change
  the code of layer 4, whatever reads it; the credentials of the person can.
  The file is outside every repository, so no commit can carry it.

- **WFO-10.** After step 6 of [ACU-34](../../acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence), or when the evidence run ends at step 1 or step 3 of ACU-34 without failing, the orchestrator runs the script of [ACU-27](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event) in the folder of WFO-8, on these copies, made in that folder (complete list):
  - a copy of the norms repository at the head of its default branch on GitHub, made with the credentials of the person who runs the orchestrator, never from the clone of the project folder. In it the script reads the norm hashes and the lists of derived norms ([NRM-12](../../norms-management/specs/module.md#the-list-of-derived-norms)) against which [ACU-26](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event) judges evidence stale: the `norm_hashes` and `derived_norm_fingerprints` of `for`, the acceptance units behind layer 2, and the derived norm citations in the code;
  - a copy of each code repository of `project.json` at its reference commit, made with the token of the code repositories as step 4 of ACU-34 makes its copies.

  What else the script reads, [LAY-10](../../development-methodology/specs/layers.md#rules) lists. It counts the decision blocks of each acceptance unit, and writes no slug and no text of a decision block in any repository ([ACU-33](../../acceptance-management/specs/module.md#when-an-acceptance-unit-is-done)). It writes nothing that the script computes in any repository: the states and the queue of the requester are shown, never stored.

  Rationale: the script reads layer 4, which no session of layer 3 may read
  ([LAY-10](../../development-methodology/specs/layers.md#rules)), and its
  results are states, which are computed and not stored
  ([ACU-23](../../acceptance-management/specs/module.md#the-ladder-of-states)).

- **WFO-11.** The orchestrator runs each `build` and each `test_command` of an evidence run with the environment of its session, less the token of the code repositories, less each variable whose name holds `TOKEN`, and less `SSH_AUTH_SOCK` and `GIT_ASKPASS`.

  Accepted cost, until open question 3 is decided: the code of layer 4 that a
  `build` or a test runs, runs as the person who runs the orchestrator, and can
  reach the files of that person, the credentials that git and the command
  `gh` keep there included. Level 3 of
  [ACU-13](../../acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence)
  then holds for the token of the code repositories, and not on the machine of
  that person. Rationale: without the variables, the code of layer 4 gets no
  credential from the environment of the evidence run, which is the part of
  the separation that the orchestrator can give on the machine of a person.

## Keep the layers apart

- **ORC-16.** The orchestrator must never write in the repository of layer 0, of layer 1 or of layer 2: no file, no commit, no branch, no issue. The issues of [ORC-14](../../drift-management/specs/module.md#report-a-drift) are opened by the step that finds the drift, in its own headless session.

  Rationale: people write layers 0 and 1
  ([LAY-2](../../development-methodology/specs/layers.md#rules)) and the
  generators write layer 2
  ([LAY-3](../../development-methodology/specs/layers.md#rules)); the
  orchestrator coordinates the layers and decides nothing in them.

- **ORC-17.** The orchestrator must never write in a repository of layer 4. In the acceptance repository, it writes only the lines of kind `test` that its evidence runs add to `records/`, with the commits that hold them (WFO-8): no other file and no other commit. Every other change of a repository of a layer comes from the step of that layer.

  Rationale: what writes the code must not write its evidence, and every other
  change of layer 3 is approved by the requester
  ([LAY-9](../../development-methodology/specs/layers.md#rules)); the lines of
  kind `test` record a run of the tests and decide nothing.

- **ORC-18.** The step of acceptance-management and the step of code-implementation must never receive layer 1, neither its files nor its path. The step of acceptance-management must never receive a repository of layer 4 either ([LAY-4](../../development-methodology/specs/layers.md#rules), [LAY-8](../../development-methodology/specs/layers.md#rules)).

- **WFO-12.** The plugin declares in its file `hooks/hooks.json` one hook on the event `PreToolUse`, for the tools `Edit`, `Write`, `NotebookEdit` and `Bash` (complete list). Each time it runs, the hook finds the repository of the session and the project folder as [ACU-45](../../acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence) says, and takes as the path of each repository of a layer the project folder followed by the `path` of each entry of `project.json` with `layer`, with its symbolic links followed. It refuses (complete list):
  - every call of `Edit` or `Write` whose `file_path`, and every call of `NotebookEdit` whose `notebook_path`, resolved as ACU-45 resolves a path, is inside a repository of a layer;
  - every call of `Bash` that [CIM-7](../../code-implementation/specs/module.md#the-hook-of-the-session) refuses, read with each repository of a layer in the place of the acceptance repository of [CIM-6](../../code-implementation/specs/module.md#the-hook-of-the-session), except a simple command whose program is `python3` and whose next word is the path of a file of `<plugin root>/scripts/`: the scripts with which the orchestrator starts the headless sessions (WFO-3), decides whether a run ends after layer 2 (WFO-13) and makes the evidence runs (WFO-8).

  It refuses a call with the JSON object of [ACU-38](../../acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence), on its standard output, and ends with status 0; when it refuses nothing, it prints nothing and ends with status 0. The reason of a refusal is, word for word, where `<path>` is the real path of the repository of a layer that the call names, and `<why>` is as [CIM-4](../../code-implementation/specs/module.md#the-hook-of-the-session) says:

  ```text
  The orchestrator never writes the repository of a layer <path> (ORC-16, ORC-17): <why>. It starts a headless session there (WFO-3), and writes records/ only through an evidence run (WFO-8).
  ```

  It refuses nothing in the cases of [CIM-5](../../code-implementation/specs/module.md#the-hook-of-the-session), read with "no entry with `layer`, or an entry with `layer` whose `path` is not valid" in the place of the cases of the entry of layer 3, nor when its input is not a JSON object, nor when it fails in any other way.

  Rationale: a shell command can write a path in more ways than a hook
  recognises, so the hook guards against mistakes; the token of the code
  repositories (WFO-9) and the permissions of GitHub of the person are the
  barrier. The scripts of the plugin are the one way in which the orchestrator
  reaches the repositories of the layers, and their spec bounds what they
  write.

## Open questions

1. How does a step that needs the decision of a person run headless? The cases known (not a complete list): the commits of layer 3, which the requester approves one by one through a rule `ask` ([LAY-9](../../development-methodology/specs/layers.md#rules)), which a headless session cannot answer; the confirmations of implement, the issue of a drift ([IMP-10](../../code-implementation/use-cases/implement/specs/implement.md#implement-a-task)) and the commit ([IMP-12](../../code-implementation/use-cases/implement/specs/implement.md#implement-a-task)); the acceptance tests, whose test agent has no use case yet ([ACU-37](../../acceptance-management/specs/module.md#done-is-a-state-not-an-event)). Candidate: the step of layer 3 runs in a session of the acceptance repository that the requester opens, and the run resumes from its hand-off when a person invokes `run` again (WFO-2).
2. How does the code of a headless session of layer 4 reach the default branch of its code repository on GitHub, where the evidence run reads its reference commit? Implement commits only when its user asks ([IMP-12](../../code-implementation/use-cases/implement/specs/implement.md#implement-a-task)), and no rule of implement pushes.
3. How is the code of layer 4 that an evidence run of the orchestrator builds and tests kept from the credentials of the person who runs the orchestrator (WFO-11)? Candidate: a container that holds no credential, as level 2 of [ACU-13](../../acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence) says.
4. What happens when two people run the orchestrator of the same project at the same time? Their runs may start headless sessions in the same repository, and their evidence runs may overlap ([ACU-34](../../acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence)).
5. Does a merge in the specs repository start a run without a person, and when is the continuous integration of the acceptance repository enabled ([ACU-76](../../acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence))?
