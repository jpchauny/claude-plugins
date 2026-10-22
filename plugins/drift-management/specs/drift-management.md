# Drift management

**Status:** Draft
**Audience:** The people who run a project's flow from specs to code; whoever builds the skills of the plugin `drift-management`

**Scope:** A drift between specs and code, sent back to layer 1

The module `drift-management` of the app Indra Software Factory, built as the plugin of the same name; the modules are listed in [modules.md](../../../specs/modules.md).

## Terms

| Term | Meaning |
|---|---|
| Run | One pass of the flow from specs to code, for one commit of layer 1. |
| Drift | A place where layer 2 cannot be implemented as it stands, because the specification is wrong, missing or contradictory. |

## Report a drift

- **ORC-14.** When the step of [code-implementation](../../code-implementation/specs/code-implementation.md) finds a drift, it opens an issue in `<project>-specs` and does not work around it. The run ends there for the affected norms; a new run starts from the commit of layer 1 that fixes it ([LAY-5](../../../specs/layers.md#lay-5--an-inconsistency-is-fixed-in-layer-1-first)).
