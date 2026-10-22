# Code implementation

**Status:** Draft
**Audience:** The people who run a project's flow from specs to code; whoever builds the skills of the plugin `code-implementation`

**Scope:** Layer 3: code built from the norms, and its traceability to norm IDs

The module `code-implementation` of the app Indra Software Factory, listed in [app.md](../../../specs/app.md).

## Terms

| Term | Meaning |
|---|---|
| Step | The work of one layer in one run, done in the repository of that layer. |
| Hand-off | What a step gives the next one: a commit, a report, or an issue. |

## Implement the changed norms

- **ORC-11.** In `<project>-code`, the step starts from the hand-off of [ORC-9](../../norms-management/specs/module.md#regenerate-the-norms) alone. It implements every new or changed norm, and removes what implements a retired norm ([LAY-4](../../../specs/layers.md#lay-4--layer-3-reads-layer-2-never-layer-1)).
- **ORC-12.** Code and tests cite the norm IDs they implement or check, and every cited ID exists in the commit of layer 2 that the step started from.
- **ORC-13.** Its hand-off is the commit or pull request of `<project>-code` with the implementation, and the list of the norm IDs it covers.

## Open questions

1. Does the step open a pull request for a person to review, or push to the default branch?
