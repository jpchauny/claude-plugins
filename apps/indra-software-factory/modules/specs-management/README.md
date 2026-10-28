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

- `/specs-management:check-writing [<path>]`: checks the writing of the draft specs of a layer 0
  repository or the specs of a layer 1 repository against writing-specs.md and recommends rewrites,
  in the chat ([specs/check-writing.md](use-cases/check-writing/specs/check-writing.md)).
- `/specs-management:check-consistency <path>`: checks one spec of layer 0 or layer 1 against the
  whole of layers 0 and 1 (contradictions, repeated facts, terms, broken links), with agents, and
  reports in the chat; it writes nothing and stops nothing. Very costly: run it only on purpose
  ([specs/check-consistency.md](use-cases/check-consistency/specs/check-consistency.md)).
- `/specs-management:promote <path>...`: moves draft specs from layer 0 to
  layer 1, at the same path, and turns the absent links that point at them
  back into plain links ([specs/promote.md](use-cases/promote/specs/promote.md)).
- `/specs-management:demote <path>...`: moves specs from layer 1 back to
  layer 0, and marks the links of layer 1 that point at them as absent links,
  `[text (not specified yet)](absent:path)`
  ([specs/demote.md](use-cases/demote/specs/demote.md)).

- `/specs-management:write [<path>]`: interviews the user about what they want, writes it as a
  draft spec of layer 0, checks it cheaply against layers 0 and 1, and proposes its promote; it also
  changes or deletes a spec of layer 1, after its demote
  ([specs/write.md](use-cases/write/specs/write.md)).

Promote and demote share [scripts/move.py](scripts/move.py) and the rules of
[specs/module.md](specs/module.md#move-specs-between-layers-0-and-1).

Planned:

- Readability review of a spec file.
- Renumbering chapters, and the links that point at them.
- Reviewing a pull request to the specs.
