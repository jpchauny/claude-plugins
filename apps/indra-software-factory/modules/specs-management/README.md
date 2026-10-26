# specs-management

Layers 0 and 1: tools for the people who write a project's draft specs and specs, in
the repositories of layers 0 and 1. Nothing here restricts what people write; the tools only
help ([LAY-2](../development-methodology/specs/layers.md#rules)).

## Guideline

[writing-specs.md](writing-specs.md): how every spec is worded. It is a copy, made by hand for now, of
[specs/writing-specs.md](../../../../specs/writing-specs.md) at the root of the marketplace: edit that
file, then copy it here byte for byte. The tools of
this module apply it.

## Tools

- `/specs-management:audit`: audits the specs of a layer 1 repository against
  writing-specs.md and recommends rewrites, in the chat
  ([specs/audit.md](use-cases/audit/specs/audit.md)).
- `/specs-management:promote <path>...`: moves draft specs from layer 0 to
  layer 1, at the same path, and turns the absent links that point at them
  back into plain links ([specs/promote.md](use-cases/promote/specs/promote.md)).
- `/specs-management:demote <path>...`: moves specs from layer 1 back to
  layer 0, and marks the links of layer 1 that point at them as absent links,
  `[text (not specified yet)](absent:path)`
  ([specs/demote.md](use-cases/demote/specs/demote.md)).

Promote and demote share [scripts/move.py](scripts/move.py) and the rules of
[specs/module.md](specs/module.md#move-specs-between-layers-0-and-1).

Planned:

- Readability review of a spec file.
- Renumbering chapters, and the links that point at them.
- Reviewing a pull request to the specs.
