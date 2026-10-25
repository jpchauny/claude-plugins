# Specs management

**Audience:** The people who run a project's flow from specs to code; whoever builds the skills of the plugin `specs-management`

**Scope:** Layers 0 and 1: the AI recommends how to improve the draft specs and the specs that the authors write

The module `specs-management` of the app Indra Software Factory, listed in [app.md](../../../specs/app.md).

## Recommend improvements to the specs

- **ORC-7.** The draft specs and the specs are free: nothing restricts what the authors write ([LAY-2](../../../specs/layers.md#lay-2--people-work-in-layers-0-and-1)). The only use case of this module is the audit, `/specs-management:audit` of the plugin `specs-management`, which recommends how to improve the specs and changes nothing; its specification is [specs-audit.md](../use-cases/audit/specs/audit.md).
