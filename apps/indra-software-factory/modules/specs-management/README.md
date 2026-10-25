# specs-management

Layers 0 and 1: tools for the people who write a project's specification, in
the repositories of layers 0 and 1. Nothing here restricts what people write; the tools only
help ([LAY-2](../../specs/layers.md#lay-2--people-work-in-layers-0-and-1)).

## Guideline

[writing-specs.md](writing-specs.md): how every spec is worded. It is a copy, made by hand for now, of
[specs/writing-specs.md](../../../../specs/writing-specs.md) at the root of the marketplace: edit that
file, then copy it here byte for byte. The tools of
this module apply it.

## Tools

None yet. Specified:

- `/specs-management:audit`: audits the specs of a layer 1 repository against
  writing-specs.md and recommends rewrites, in the chat
  ([specs/specs-audit.md](use-cases/audit/specs/audit.md)).

Planned:

- Readability review of a spec file.
- Renumbering chapters, and the links that point at them.
- Reviewing a pull request to the specs.
