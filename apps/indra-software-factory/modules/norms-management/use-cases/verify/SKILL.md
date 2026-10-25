---
name: verify
description: Check that layer 2 in this norms repository is exactly what the generator produces from layer 1 at the commit pinned in data/tree.jsonl - nothing edited by hand, nothing missing. Use when the user says /norms-management:verify, "verifica las normas", "verify layer 2", or before a commit or release of layer 2.
---

# verify

Layer 2 is never edited by hand
([LAY-3](https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).
This checks it, from the norms repository of the project.

1. Find layer 1 as the `build` skill of this plugin does.
2. Run:
   ```sh
   uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}" norms-gen verify --specs <layer 1>
   ```
3. Exit 0: say it verifies, in one line. Otherwise show the problems as the
   generator prints them, and change nothing: the fix is a new `build`, or a
   change in layer 1.
