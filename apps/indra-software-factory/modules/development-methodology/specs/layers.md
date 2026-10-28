# Layers

**Prefix:** LAY

**Audience:** The people who work in a repository of a project, and the Claude Code sessions there; whoever builds a module of the app

**Scope:** The five layers of every project: what each holds, who writes it, how each depends on the others, and where each module of the app is installed. How a run goes across them is in [flow.md](flow.md); what each module does is in [app.md](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/specs/app.md#modules)

A spec of the module `development-methodology` of the app Indra Software Factory, listed in [app.md](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/specs/app.md); the module is specified in [module.md](module.md).

## Terms

| Term | Meaning |
|---|---|
| Draft spec | A spec of layer 0: not yet ready to be the source of truth, because it is incomplete or not yet reviewed. |
| Spec | A spec of layer 1, the source of truth. |
| Spec part | A part of a spec that holds information, at any depth: a section, a paragraph, a list or one of its items, a table or one of its rows or cells, a code block, a block quote ([R1 and R7](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/norms-management/specs/norms-tree.md#the-specs)). A spec part has no ID in layer 1: an ID that its author writes in it, such as `**LAY-2.**`, is part of its text. Citing a spec part cites every spec part below it. |
| Norm | A spec or a spec part as layer 2 gives it: with its norm ID and its norm hash, in `specs-repo-annotated/` and `data/tree.jsonl`. Each spec and each spec part is one norm, which keeps its norm ID when it moves or is edited ([R11](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/norms-management/specs/norms-tree.md#the-tree-in-layer-2)). |
| Derived norm | An item of the output of a type, in `specs-derived/<type>/` of layer 2, that a derived-norms generator derives from the norms, to make the implementation clearer to an agent: a rule of a grammar or of a formal semantics, an example of a corpus. It cites every norm it comes from, and decides nothing that the norms do not decide (LAY-3). What one item is, and how it is identified, is in the spec of its generator. |
| Acceptance unit | The smallest part of the product that the person who asks for it can recognise and validate end to end, as [acceptance-management](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md) specifies it. |
| Acceptance area | An observable area of the product, made of acceptance units, as [acceptance-management](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md) specifies it. |
| Acceptance test | A test of layer 3 that runs one scenario of an acceptance unit or an acceptance area through the external interface of the product only, as [acceptance-management](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md) specifies it. |
| Unit hash | The fingerprint of what an acceptance unit asks, which changes whenever it changes, as [acceptance-management](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#hashes-and-citations) specifies it (ACU-52). |

The first five terms are not used for one another. A draft spec becomes a spec
when it is promoted, a spec is made of spec parts, and each spec and spec part
becomes a norm when it is annotated. "Norm" alone means a norm annotated from
layer 1, never a derived norm.

## The five layers

Every project is specified and built in five layers, each in its own
repositories.

| Layer | Recommended name | Holds | Written by |
|---|---|---|---|
| 0. Drafts | `<project>-drafts` | The draft specs, in plain prose | People |
| 1. Specs | `<project>-specs` | The specs, in plain prose | People |
| 2. Norms | `<project>-norms` | The norms and the derived norms | Generated from layer 1 only |
| 3. Acceptance | `<project>-acceptance` | The acceptance areas, the acceptance units and their acceptance tests | Agents, each change approved by a person, except the first commit, the evidence of tests and what sync writes |
| 4. Code | `<project>-code`, or one `<project>-code-<component>` per component | Code and its unit tests | Agents |

The work of each layer is done with the modules of the app Indra Software
Factory installed in its repository, as
[APP-6](#where-each-module-is-installed) says.

## Rules

- **LAY-1.** Every project has five layers, each in its own repositories. A project always has the five layers. There is no variant with fewer.

  Layers 0, 1, 2 and 3 live each in one repository. Layer 4 lives in one
  repository, or in one repository per component. A component is a part of the
  project that is built, versioned and released on its own, such as a compiler
  or a server. A project uses one of the two forms, never both. Every repository
  of layer 4 reads the same layers 2 and 3.

  Which repositories belong to a project, the layer of each, and where each is,
  are written in the file `project.json` of the project
  ([ORC-20](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/project-management/specs/module.md#where-the-repositories-are)), not in the names of the repositories. The names in the
  table above are recommended, not required.

  Layer 0 holds the draft specs. Nothing is derived from it, and no layer reads
  it. A spec is in layer 0 or in layer 1, never in both: promoting a draft spec
  makes it a spec, adding it to layer 1 and removing it from layer 0, and
  demoting a spec does the reverse. It is moved, never copied.

  Rationale: each layer is one stage of the way from a person's intent to code.
  Layer 0 is where a spec starts, as a draft. When it is ready, it is promoted
  to layer 1, where it becomes law. Layer 2 is generated from layer 1: a spec
  becomes a norm when it gets an ID and a fingerprint, its hash. Layer 3 says
  what is delivered and how each part of it is accepted, in acceptance units
  that cite the norms; it is one repository for the whole project because an
  acceptance unit may need more than one component. Layer 4 builds the code
  that the acceptance units accept. People write layers 0 and 1 and approve layer 3; layer 2 is
  regenerated automatically.

- **LAY-2.** People work in layers 0 and 1. Layers 0 and 1 are the only layers people write. Layer 1 is the only source of truth. Neither has a required structure: any folders, any files, at any depth.

  A person may ask an agent to write a change in layer 0 or 1. The agent never
  changes either layer without the person's approval:

  1. The agent shows the whole diff of the change.
  2. The agent commits the change and pushes it to the default branch in one
     command.
  3. The person approves that command before it runs. The repository's
     `.claude/settings.json` makes every command that commits or pushes ask the
     person, through a rule `ask` of its permissions, which Claude Code applies
     in every permission mode.

  There is no pull request: the approval of the command is the review.

  The copy of `project.json` that `/project-management:sync` writes in the
  repository of layer 0, once the user confirmed it, is not a change that
  follows the three steps above: it copies what layer 1 decided and decides
  nothing of layer 0, as the same copy in layer 3 (LAY-9)
  ([ORC-23](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/project-management/specs/module.md#where-the-repositories-are)).

  Rationale: spec-driven development turns the intent of people into code with
  the help of AI. The authors of layers 0 and 1 get total freedom: there are
  recommendations on how to write a spec, but no required structure.

- **LAY-3.** Layer 2 is derived from layer 1 only, and only what changed is regenerated. Nobody, person or agent, edits layer 2 by hand. It is derived from a commit of layer 1: the norms generator annotates the specs with norm IDs, which makes them norms, and the project's own generators derive the derived norms from the norms (the rules of a grammar or of a formal semantics, the examples of a corpus). A new commit of layer 1 regenerates only what a change of it calls for: an annotated file whose source changed, and each derived norm that comes from a norm that changed or is gone. Everything else stays as it is. Each regeneration records the commit of layer 1 it comes from and the generator that produced it: for the norms, the version of the norms generator; for each derived norm, the plugin of its generator and its version ([NRM-5](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/norms-management/specs/module.md#derive-the-derived-norms)).

  The copy of `project.json` that `/project-management:sync` writes in the
  repository of layer 2, once the user confirmed it, is not an edit of layer 2
  by hand: it copies what layer 1 decided and decides nothing of layer 2, as
  the same copy in layer 3 (LAY-9)
  ([ORC-23](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/project-management/specs/module.md#where-the-repositories-are)).

  Every derived norm cites the norms it comes from, one citation per norm, in
  the form in which an acceptance unit cites a norm
  ([ACU-56](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#hashes-and-citations)):
  `<norm ID>@<norm hash>: <reason>` after the comment mark of its language. A
  derived norm makes no decision that the norms do not make: where they leave a
  gap, no derived norm is written and an issue goes to layer 1
  (LAY-5).

  The norms generator writes `specs-repo-annotated/`: a mirror of the whole
  layer 1 repository, at the same paths, its Markdown files annotated with norm
  IDs and every other file copied as it is. It leaves out only what is
  certainly not specification, such as the configuration of tools and the
  instructions for agents; the generator's specification fixes that list
  ([R62](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/norms-management/specs/norms-versions.md)). When in doubt, a file is
  copied.

  Rationale: layer 2 is generated, and is read, never written, to define
  acceptance in layer 3 and to implement in layer 4: by the agents, and by the
  people who approve layer 3 and see the norms its changes cite
  ([ACU-15](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#the-review-of-the-norms-selected)). It holds
  two kinds of norms: the norms, from the annotated specs of layer 1, and, when
  a project needs them, the derived norms that the project's generators produce
  from the norms, such as a semantics, a grammar or an architecture diagram.
  Regenerating layer 2 is fast; what is costly is generating the derived norms,
  such as the grammar of the code fragments or the semantics. Each derived norm
  cites the ID and the hash of the norm it comes from, so regenerating the whole
  of layer 2 would also regenerate every derived norm, at a cost that nothing
  calls for: only the changes of layer 1 flow into layer 2.

- **LAY-4.** Layer 4 reads layers 2 and 3, never layer 1. Code is built from the norms of layer 2, within the acceptance units of layer 3 that it implements. The code and the unit tests cite the acceptance units they implement or check, each with its unit hash, and never a norm ID; the norms they implement are those that the units they cite group ([ACU-56](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#hashes-and-citations)). The acceptance tests of layer 3 are run by layer 4, never changed by it. A session of layer 4 never reads or writes layer 1, and never writes layers 2 or 3.

  Rationale: code must always be traced to the norms it comes from: the code
  cites a unit and its unit hash, and the unit cites its norms and their norm
  hashes. Layer 1 is not annotated, so it cannot be cited exactly; only layer
  2 gives each norm a stable ID. A unit hash changes whenever what the unit
  asks changes, so one comparison tells layer 4 which code to review.

- **LAY-8.** A session of layer 3 reads layer 2 and layer 3, never layer 1 and never layer 4. Its acceptance areas, acceptance units and acceptance tests are written from the norms of layer 2. A unit cites the norms it groups, each with its norm hash, and the scenarios of units and areas tag the norm IDs they check; an acceptance test cites its unit or its area and its scenario, each with its hash, and never a norm ([ACU-56](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#hashes-and-citations)). A session of layer 3 never writes layer 1, 2 or 4. A hook of the plugin `acceptance-management` refuses the calls of a session of layer 3 that name a repository of layer 4 ([ACU-38](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence)).

  Rationale: an acceptance test is evidence only when it is written without
  seeing the code it checks. An agent that reads the code writes tests that
  confirm what the code does, not what the norms ask.

- **LAY-10.** The continuous integration of the acceptance repository reads layer 4; no session of layer 3 does. It runs the scripts that compute when a unit is done ([ACU-27](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#done-is-a-state-not-an-event)), not a session and not the continuous integration of a code repository. Besides layers 2 and 3, those scripts read (complete list): the results of the acceptance tests and the other evidence, in `records/` of layer 3 ([ACU-35](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#done-is-a-state-not-an-event)); the reference commit of each repository of layer 4; the citations of units ([ACU-56](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#hashes-and-citations)) and the decision blocks in the code of layer 4 ([ACU-33](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#when-a-unit-is-done)); and the issues of the repository of layer 3 with the label `failure` ([ACU-36](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#done-is-a-state-not-an-event)). The same continuous integration also makes a copy of each code repository at its reference commit and builds it, to run the acceptance tests against the product ([ACU-34](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence)). It reads the code repositories with a token that can only read them, and no session of layer 3 holds that token or sees those copies. Of the decision blocks, only the count of each unit reaches layer 3, never their text (ACU-33).

- **LAY-9.** In layer 3 an agent writes and a person approves. Every change of layer 3 is committed with the three steps of LAY-2: the agent shows the whole diff, commits it and pushes it to the default branch in one command, and the person approves that command. Three writes of layer 3 are not such changes, because they record or copy what was decided elsewhere and decide nothing of layer 3 (complete list): the first commit of the repository, which `/project-management:create-project` writes from its templates and from the plan that the person approved, its `project.json` and its default done profile ([ORC-4](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/project-management/use-cases/create-project/specs/create-project.md#create-a-project), [ORC-5](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/project-management/use-cases/create-project/specs/create-project.md#create-a-project), [CRP-1](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/project-management/use-cases/create-project/specs/create-project.md#create-a-project), [CRP-2](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/project-management/use-cases/create-project/specs/create-project.md#create-a-project)); the lines of kind `test` that the continuous integration of [ACU-34](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#acceptance-tests-and-independent-evidence) adds to `records/` ([ACU-35](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#done-is-a-state-not-an-event)); and what `/project-management:sync` writes once the user confirmed it, the copy of `project.json` and the rules `deny` of `.claude/settings.json` ([ORC-23](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/project-management/specs/module.md#where-the-repositories-are), [SNC-1](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/project-management/use-cases/sync/specs/sync.md#sync-projectjson)). Layer 3 is not a source of truth: an acceptance area or an acceptance unit decides only how the norms are delivered and accepted, never what the product does ([ACU-4](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#the-acceptance-area-and-the-acceptance-unit)).

- **LAY-7.** An absent link names a spec that is not in layer 1. It is a link of layer 1 whose destination starts with `absent:`, in the form that the promote and demote of `specs-management` write ([ORC-36](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/specs-management/specs/module.md#rules)). What its target would specify is not specified: no agent, of any layer, infers it, implements it, or looks for it in another repository, layer 0 included. Checking whether a file exists at the path of its target, without reading the file, is not looking for it: the audit of `specs-management` does it ([AUD-55](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/specs-management/use-cases/audit/specs/audit.md)). The norms generator copies an absent link into layer 2 as it is, so the same holds in layers 2, 3 and 4.

  Rationale: layer 1 keeps only the specs that are reviewed, and a spec still
  in layer 0 is not law (LAY-1). The mark says that the spec is missing, not
  where its draft is.

- **LAY-5.** An inconsistency is fixed in layer 1 first. When defining acceptance or implementing shows that a norm or a derived norm is wrong, missing or contradictory, layers 3 and 4 do not work around it:

  1. The layer that found it, 3 or 4, opens an issue in the repository of layer 1.
  2. A person fixes layer 1, as LAY-2 says.
  3. Layer 2 is regenerated from the new commit.
  4. Layer 3 updates the acceptance units that group a changed norm, as [ACU-28](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/acceptance-management/specs/module.md#done-is-a-state-not-an-event) says, each change approved as LAY-9 says; layer 4 takes the regenerated layer 2 and the updated layer 3, and implements again what changed.

  Rationale: layer 1 is the only source of truth. In spec-driven development,
  with the spec as the source, the spec always changes first and the code is
  implemented after it.

- **LAY-6.** Every project uses the latest version of the plugins. There is no pinned version of a plugin per project: sessions and automation use the latest one. A change to a generator therefore changes layer 2 of every project at its next regeneration.

  Rationale: every project stays aligned with the latest version of the
  plugins. GitHub keeps the versions, so no project pins one.

## Where each module is installed

APP-6 keeps the ID it had in [app.md](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/specs/app.md), as a clause moved from it ([SST-11](https://github.com/jpchauny/claude-plugins/blob/main/specs/spec-structure.md#ids-of-clauses)).

- **APP-6.** Where each module is installed (complete list):

  | Module | Where |
  |---|---|
  | `development-methodology` | Enabled in the `.claude/settings.json` of each repository of the project, of the five layers. |
  | `project-management` | At user scope, once per person: its use case `create-project` runs before the repositories of a project exist. |
  | `specs-management` | Enabled in the `.claude/settings.json` of the repositories of layers 0 and 1 only. |
  | `norms-management` | Enabled in the `.claude/settings.json` of the repository of layer 2 only. |
  | `acceptance-management` | Enabled in the `.claude/settings.json` of the repository of layer 3 only. |
  | `code-implementation` | Enabled in the `.claude/settings.json` of each repository of layer 4 only. |
  | `utilities` | Enabled in the `.claude/settings.json` of each repository of the project. |
  | `workflow-orchestration`, `drift-management` | Not yet decided: open question 1 of layers.md. |

  Rationale: a module of a layer is enabled only in the repositories of that layer, so that its use cases are not run in the wrong repository.

## Open questions

1. Where are `workflow-orchestration` and `drift-management` installed? Both work across the repositories of a project, and neither has a use case yet.
