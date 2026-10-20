# specs

Layer 1: tools for the people who write a project's specification, in
`<project>-specs`. Nothing here restricts what people write; the tools only
help ([LAY-2](../../spec-driven-design-process/layers.md#lay-2--people-work-in-layer-1)).

## Guideline

[writing-specs.md](writing-specs.md): how every spec is worded. The tools of
this plugin apply it.

## Tools

None yet. Specified:

- `/specs:audit`: audits the specs of a layer 1 repository against
  writing-specs.md and recommends rewrites, in the chat
  ([specs/specs-audit.md](specs/specs-audit.md)).

Planned:

- Readability review of a spec file.
- Renumbering chapters, and the links that point at them.
- Reviewing a pull request to the specs.
