# Layers

**Status:** Draft

Every project is specified and built in three layers, each in its own
repository.

| Layer | Repository | Holds | Written by | Plugin |
|---|---|---|---|---|
| 1. Specs | `<project>-specs` | The specification, in plain prose | People | `specs` |
| 2. Norms | `<project>-norms` | The specs annotated with stable norm IDs, and every specification derived from them | Generated from layer 1 only | `norms` |
| 3. Code | `<project>-code` | Code and tests | Agents | `code` |

Every repository also enables the plugin `shared`: what is the same in the
three layers. The plugin `new-project` creates the three repositories.

## Rules

### LAY-1 — Every project has three layers, in three repositories

A project always has the three layers, and each lives in its own repository,
named `<project>-specs`, `<project>-norms` and `<project>-code`. There is no
variant with fewer.

### LAY-2 — People work in layer 1

Layer 1 is the only layer people write, and the only source of truth. It
changes only by a pull request that a person approves.

### LAY-3 — Layer 2 is regenerated whole, from layer 1 only

Nobody, person or agent, edits layer 2 by hand. It is regenerated whole from a
commit of layer 1: the norms generator annotates the specs, and the project's
own generators derive the rest (a grammar, a formal semantics, a corpus of
examples). Each regeneration records the commit of layer 1 it comes from and
the commit of the generators that produced it.

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
