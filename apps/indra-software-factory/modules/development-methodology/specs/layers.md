# Layers

**Prefix:** LAY

**Audience:** The people who work in a repository of a project, and the Claude Code sessions there; whoever builds a module of the app

**Scope:** The four layers of every project: what each holds, who writes it, how each depends on the others, and where each module of the app is installed. How a run goes across them is in [flow.md](flow.md); what each module does is in [app.md](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/specs/app.md#modules)

A spec of the module `development-methodology` of the app Indra Software Factory, listed in [app.md](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/specs/app.md); the module is specified in [module.md](module.md).

## Terms

| Term | Meaning |
|---|---|
| Draft spec | A spec of layer 0: not yet ready to be the source of truth, because it is incomplete or not yet reviewed. |
| Spec | A spec of layer 1, the source of truth. |
| Norm | A part of a spec of layer 1 with a stable norm ID, as the norms generator annotates it in layer 2. A spec annotated with norm IDs is made of norms. |
| Derived norm | A norm of layer 2 that a project's own generator derives from the norms, to make the implementation clearer to an agent, such as a rule of a grammar or of a formal semantics, or an example of a corpus. |

These four terms are not used for one another. A draft spec becomes a spec
when it is promoted, and a spec becomes norms when it is annotated. "Norm"
alone means a norm annotated from layer 1, never a derived norm.

## The four layers

Every project is specified and built in four layers, each in its own
repositories.

| Layer | Recommended name | Holds | Written by |
|---|---|---|---|
| 0. Drafts | `<project>-drafts` | The draft specs, in plain prose | People |
| 1. Specs | `<project>-specs` | The specs, in plain prose | People |
| 2. Norms | `<project>-norms` | The norms and the derived norms | Generated from layer 1 only |
| 3. Code | `<project>-code`, or one `<project>-code-<component>` per component | Code and tests | Agents |

The work of each layer is done with the modules of the app Indra Software
Factory installed in its repository, as
[APP-6](#where-each-module-is-installed) says.

## Rules

- **LAY-1.** Every project has four layers, each in its own repositories. A project always has the four layers. There is no variant with fewer.

  Layers 0, 1 and 2 live each in one repository. Layer 3 lives in one
  repository, or in one repository per component. A component is a part of the
  project that is built, versioned and released on its own, such as a compiler
  or a server. A project uses one of the two forms, never both. Every repository
  of layer 3 reads the same layer 2.

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
  becomes a norm when it gets an ID and a fingerprint, its hash. People write
  layers 0 and 1; layer 2 is regenerated automatically.

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

  Rationale: spec-driven development turns the intent of people into code with
  the help of AI. The authors of layers 0 and 1 get total freedom: there are
  recommendations on how to write a spec, but no required structure.

- **LAY-3.** Layer 2 is derived from layer 1 only, and only what changed is regenerated. Nobody, person or agent, edits layer 2 by hand. It is derived from a commit of layer 1: the norms generator annotates the specs with norm IDs, which makes them norms, and the project's own generators derive the derived norms from the norms (the rules of a grammar or of a formal semantics, the examples of a corpus). A new commit of layer 1 regenerates only what a change of it calls for: an annotated file whose source changed, and each derived norm that comes from a norm that changed or is gone. Everything else stays as it is. Each regeneration records the commit of layer 1 it comes from and the generator that produced it: for the norms, the version of the norms generator; for each derived norm, the plugin of its generator and its version ([NRM-5](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/norms-management/specs/module.md#derive-the-derived-norms)).

  Every derived norm cites the norms it comes from, one citation per norm, in
  the form that code uses
  ([IMP-6](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/code-implementation/use-cases/implement/specs/implement.md)):
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

  Rationale: layer 2 is generated, and only AI reads it, to implement. It holds
  two kinds of norms: the norms, from the annotated specs of layer 1, and, when
  a project needs them, the derived norms that the project's generators produce
  from the norms, such as a semantics, a grammar or an architecture diagram.
  Regenerating layer 2 is fast; what is costly is generating the derived norms,
  such as the grammar of the code fragments or the semantics. Each derived norm
  cites the ID and the hash of the norm it comes from, so regenerating the whole
  of layer 2 would also regenerate every derived norm, at a cost that nothing
  calls for: only the changes of layer 1 flow into layer 2.

- **LAY-4.** Layer 3 reads layer 2, never layer 1. Code and tests are built from layer 2 alone, and cite the norm IDs they implement or check. A session of layer 3 never reads or writes layer 1, and never writes layer 2.

  Rationale: code must always cite the norms it comes from. Layer 1 is not
  annotated, so it cannot be cited exactly; only layer 2 gives each norm a
  stable ID.

- **LAY-7.** An absent link names a spec that is not in layer 1. It is a link of layer 1 whose destination starts with `absent:`, in the form that the promote and demote of `specs-management` write ([ORC-36](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/specs-management/specs/module.md#rules)). What its target would specify is not specified: no agent, of any layer, infers it, implements it, or looks for it in another repository, layer 0 included. The norms generator copies an absent link into layer 2 as it is, so the same holds in layers 2 and 3.

  Rationale: layer 1 keeps only the specs that are reviewed, and a spec still
  in layer 0 is not law (LAY-1). The mark says that the spec is missing, not
  where its draft is.

- **LAY-5.** An inconsistency is fixed in layer 1 first. When implementing shows that a norm or a derived norm is wrong, missing or contradictory, layer 3 does not work around it:

  1. Layer 3 opens an issue in the repository of layer 1.
  2. A person fixes layer 1, as LAY-2 says.
  3. Layer 2 is regenerated from the new commit.
  4. Layer 3 takes the regenerated layer 2 and implements again what changed.

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
  | `development-methodology` | Enabled in the `.claude/settings.json` of each repository of the project, of the four layers. |
  | `project-management` | At user scope, once per person: its use case `create-project` runs before the repositories of a project exist. |
  | `specs-management` | Enabled in the `.claude/settings.json` of the repositories of layers 0 and 1 only. |
  | `norms-management` | Enabled in the `.claude/settings.json` of the repository of layer 2 only. |
  | `code-implementation` | Enabled in the `.claude/settings.json` of each repository of layer 3 only. |
  | `utilities` | Enabled in the `.claude/settings.json` of each repository of the project. |
  | `workflow-orchestration`, `drift-management` | Not yet decided: open question 1 of layers.md. |

  Rationale: a module of a layer is enabled only in the repositories of that layer, so that its use cases are not run in the wrong repository.

## Open questions

1. Where are `workflow-orchestration` and `drift-management` installed? Both work across the repositories of a project, and neither has a use case yet.
