# norms

Layer 2, in `<project>-norms`: the norms generator common to every project,
and the method for writing a project's own generators of derived
specifications ([LAY-3](../../spec-driven-design-process/layers.md#lay-3--layer-2-is-regenerated-whole-from-layer-1-only)).

## Tools

None yet. Planned:

- The norms generator: annotates layer 1 with stable norm IDs. It moves here
  from `clean-language-norms`, and is callable both from a session and from
  automation without Claude Code.
- The method for a project's own generators (a grammar, a formal semantics):
  what they read, what they write, how they cite norm IDs.
- A skeleton for a new generator.
