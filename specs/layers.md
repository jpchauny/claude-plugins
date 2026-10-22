# Layers

**Status:** Draft

Every project is specified and built in three layers, each in its own
repository.

| Layer | Repository | Holds | Written by | Plugin |
|---|---|---|---|---|
| 1. Specs | `<project>-specs` | The specification, in plain prose | People | `specs-management` |
| 2. Norms | `<project>-norms` | The specs annotated with stable norm IDs, and every specification derived from them | Generated from layer 1 only | `norms-management` |
| 3. Code | `<project>-code` | Code and tests | Agents | `code-implementation` |

Each plugin is a module of the app Indra Software Factory, listed in
[modules.md](modules.md). The module `shared` holds what is the same in the
three layers; `project-management`, `workflow-orchestration` and
`drift-management` work across the three repositories.

## Rules

### LAY-1 — Every project has three layers, in three repositories

A project always has the three layers, and each lives in its own repository,
named `<project>-specs`, `<project>-norms` and `<project>-code`. There is no
variant with fewer.

### LAY-2 — People work in layer 1

Layer 1 is the only layer people write, and the only source of truth. It
changes only by a pull request that a person approves. It has no required
structure: any folders, any files, at any depth.

### LAY-3 — Layer 2 is regenerated whole, from layer 1 only

Nobody, person or agent, edits layer 2 by hand. It is regenerated whole from a
commit of layer 1: the norms generator annotates the specs, and the project's
own generators derive the rest (a grammar, a formal semantics, a corpus of
examples). Each regeneration records the commit of layer 1 it comes from and
the commit of the generators that produced it.

The norms generator writes `specs-repo-annotated/`: a mirror of the whole
layer 1 repository, at the same paths, its Markdown files annotated with norm
IDs and every other file copied as it is. It leaves out only what is
certainly not specification, such as the configuration of tools and the
instructions for agents; the generator's specification fixes that list
([R62](../plugins/norms-management/specs/norms-versions.md)). When in doubt, a file is
copied.

### LAY-4 — Layer 3 reads layer 2, never layer 1

Code and tests are built from layer 2 alone, and cite the norm IDs they
implement or check. A session of layer 3 never reads or writes layer 1, and
never writes layer 2.

### LAY-5 — An inconsistency is fixed in layer 1 first

When implementing shows that the specification is wrong, missing or
contradictory, layer 3 does not work around it:

1. Layer 3 opens an issue in `<project>-specs`.
2. A person fixes layer 1, by pull request.
3. Layer 2 is regenerated from the new commit.
4. Layer 3 takes the regenerated layer 2 and implements again what changed.

### LAY-6 — Every project uses the latest version of the plugins

There is no pinned version of a plugin per project: sessions and automation
use the latest one. A change to a generator therefore changes layer 2 of every
project at its next regeneration.
