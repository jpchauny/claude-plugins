# code-implementation

Layer 3, in each repository of layer 3: the implementation method. Code and tests are
built from layer 2 alone and cite its norm IDs
([LAY-4](../development-methodology/specs/layers.md#rules));
an inconsistency goes back to layer 1 first
([LAY-5](../development-methodology/specs/layers.md#rules)).

## Tools

None yet. Planned:

- The implementation method: nothing is coded that is not in layer 2.
- Traceability: how code and tests cite norm IDs, and the check that every cited ID exists.
- Reporting an inconsistency as an issue in the repository of layer 1.
- Hooks that keep the session from writing layer 2.
