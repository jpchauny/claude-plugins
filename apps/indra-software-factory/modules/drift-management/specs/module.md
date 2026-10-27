# Drift management

**Audience:** The people who run a project's flow from specs to code; whoever builds the skills of the plugin `drift-management`

**Scope:** A drift found while defining acceptance in layer 3 or implementing in layer 4, sent back to layer 1. What each layer holds is in [layers.md](../../development-methodology/specs/layers.md)

The module `drift-management` of the app Indra Software Factory, listed in [app.md](../../../specs/app.md).

## Terms

| Term | Meaning |
|---|---|
| Drift | A norm or a derived norm of layer 2 that defining acceptance in layer 3 or implementing in layer 4 shows to be wrong, missing or contradictory ([LAY-5](../../development-methodology/specs/layers.md#rules)). |

The term run is that of [flow.md](../../development-methodology/specs/flow.md#terms).

## Report a drift

- **ORC-14.** When the step of [acceptance-management](../../acceptance-management/specs/module.md) or the step of [code-implementation](../../code-implementation/specs/module.md) finds a drift, it opens an issue in the repository of layer 1 and does not work around it. The run ends there for the affected norms; a new run starts from the commit of layer 1 that fixes it ([LAY-5](../../development-methodology/specs/layers.md#rules)).
