# code

Layer 3, in `<project>-code`: the implementation method. Code and tests are
built from layer 2 alone and cite its norm IDs
([LAY-4](../orchestrator/specs/layers.md#lay-4--layer-3-reads-layer-2-never-layer-1));
an inconsistency goes back to layer 1 first
([LAY-5](../orchestrator/specs/layers.md#lay-5--an-inconsistency-is-fixed-in-layer-1-first)).

## Tools

None yet. Planned:

- The implementation method: nothing is coded that is not in layer 2.
- Traceability: how code and tests cite norm IDs, and the check that every cited ID exists.
- Reporting an inconsistency as an issue in `<project>-specs`.
- Hooks that keep the session from writing layer 2.
