# Layers

Every project is specified and built in four layers, each in its own
repositories.

| Layer | Recommended name | Holds | Written by | Plugin |
|---|---|---|---|---|
| 0. Drafts | `<project>-drafts` | The draft specs, in plain prose | People | `specs-management` |
| 1. Specs | `<project>-specs` | The specs, in plain prose | People | `specs-management` |
| 2. Norms | `<project>-norms` | The norms and the derived norms | Generated from layer 1 only | `norms-management` |
| 3. Code | `<project>-code`, or one `<project>-code-<component>` per component | Code and tests | Agents | `code-implementation` |

Each plugin is a module of the app Indra Software Factory, listed in
[app.md](app.md). The module `utilities` holds tools usable in any of the
four layers; `project-management`, `workflow-orchestration` and
`drift-management` work across the repositories of a project.

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

## Rules

### LAY-1 — Every project has four layers, each in its own repositories

A project always has the four layers. There is no variant with fewer.

Layers 0, 1 and 2 live each in one repository. Layer 3 lives in one
repository, or in one repository per component. A component is a part of the
project that is built, versioned and released on its own, such as a compiler
or a server. A project uses one of the two forms, never both. Every repository
of layer 3 reads the same layer 2.

Which repositories belong to a project, the layer of each, and where each is,
are written in the file `project.json` of the project
([ORC-20](../modules/project-management/specs/module.md#where-the-repositories-are)), not in the names of the repositories. The names in the
table above are recommended, not required.

Layer 0 holds the draft specs. Nothing is derived from it, and no layer reads
it. A spec is in layer 0 or in layer 1, never in both: promoting a draft spec
makes it a spec, adding it to layer 1 and removing it from layer 0, and
demoting a spec does the reverse. It is moved, never copied.

### LAY-2 — People work in layers 0 and 1

Layers 0 and 1 are the only layers people write. Layer 1 is the only source
of truth. Neither has a required structure: any folders, any files, at any
depth.

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

### LAY-3 — Layer 2 is derived from layer 1 only, and only what changed is regenerated

Nobody, person or agent, edits layer 2 by hand. It is derived from a commit of
layer 1: the norms generator annotates the specs with norm IDs, which makes
them norms, and the project's own generators derive the derived norms from the
norms (the rules of a grammar or of a formal semantics, the examples of a
corpus). A new commit of layer 1 regenerates only what a change of it calls
for: an annotated file whose source changed, and each derived norm that comes
from a norm that changed or is gone. Everything else stays as it is. Each
regeneration records the commit of layer 1 it comes from and the commit of the
generators that produced it.

Every derived norm cites the norms it comes from, one citation per norm, in
the form that code uses
([IMP-6](../modules/code-implementation/use-cases/implement/specs/implement.md)):
`<norm ID>@<norm hash>: <reason>` after the comment mark of its language. A
derived norm makes no decision that the norms do not make: where they leave a
gap, no derived norm is written and an issue goes to layer 1
([LAY-5](#lay-5--an-inconsistency-is-fixed-in-layer-1-first)).

The norms generator writes `specs-repo-annotated/`: a mirror of the whole
layer 1 repository, at the same paths, its Markdown files annotated with norm
IDs and every other file copied as it is. It leaves out only what is
certainly not specification, such as the configuration of tools and the
instructions for agents; the generator's specification fixes that list
([R62](../modules/norms-management/specs/norms-versions.md)). When in doubt, a file is
copied.

### LAY-4 — Layer 3 reads layer 2, never layer 1

Code and tests are built from layer 2 alone, and cite the norm IDs they
implement or check. A session of layer 3 never reads or writes layer 1, and
never writes layer 2.

### LAY-5 — An inconsistency is fixed in layer 1 first

When implementing shows that a norm or a derived norm is wrong, missing or
contradictory, layer 3 does not work around it:

1. Layer 3 opens an issue in the repository of layer 1.
2. A person fixes layer 1, as LAY-2 says.
3. Layer 2 is regenerated from the new commit.
4. Layer 3 takes the regenerated layer 2 and implements again what changed.

### LAY-6 — Every project uses the latest version of the plugins

There is no pinned version of a plugin per project: sessions and automation
use the latest one. A change to a generator therefore changes layer 2 of every
project at its next regeneration.
