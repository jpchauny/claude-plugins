# Spec-driven design

**Status:** Draft

Spec-driven design: how every project of the company is specified and built. This folder is the
single source of truth for the process: the plugins in [../plugins](../plugins)
are its tools, and each tool cites the rules of this folder it carries out.

| File | What it holds |
|---|---|
| [layers.md](layers.md) | The three layers, who writes each, what each may read, and how a change moves between them |
| [writing-specs.md](writing-specs.md) | How every spec is worded: the rules, the approver's checklist, and the decisions between rules |
| [research/](research/spec-dimensions.md) | The research behind the rules: the dimensions of a spec and the tensions between them |

Rules carry an ID (`LAY-1`) that is given once and never reused. A tool
without a rule is surplus; a rule without a tool, where it needs one, is work
left to do.
