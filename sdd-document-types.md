# Document Types in Spec-Driven Development with AI

*2026-10-20 · Audience: software practitioners*

In spec-driven development (SDD) with AI, teams write structured documents that coding agents work from and that the agents' output is checked against. These documents cover context, intent, design, plans and tests. This catalogue lists the types of SDD document for **software projects only**, without tying them to any tool. Tool names appear only as illustrations. The catalogue was built by researching several kinds of source in parallel: SDD toolkits, AI vendor documentation, classic software engineering, practitioner writing and academic papers. The documents found were merged into one set of tool-agnostic types. Three adversarial verifiers then challenged each type, and the types a majority rejected were merged or dropped.

**How to read the entries**

- **Core** means that almost every SDD workflow needs the type. **Optional** types come with the condition under which they are worth writing.
- **Lifespan** is either *throwaway*, *per feature or change* (often archived afterwards) or *living* (kept in sync with the code).
- A second property cuts across all types: whether the document is **always loaded** into the agent's context or **loaded on demand**. Keep always-loaded documents short, and link to the rest.
- Tool examples, file names and tool commands are illustrations, not requirements.

## Summary table

| # | Type | Phase | Core / optional | Lifespan | Author |
|---|---|---|---|---|---|
| 1 | Agent instructions file | Context | Core | Living | Human-owned; AI drafts or proposes edits |
| 2 | Project constitution | Context | Optional | Living; amended rarely | Human; AI may draft |
| 3 | Product context | Context | Core (greenfield or product-scale work) | Living | AI drafts; human approves |
| 4 | Market and domain research report | Context | Optional | Static reference; refreshed | AI analyst; human reviews |
| 5 | Technology stack and technical constraints | Context | Core content; a separate file is optional | Living | AI infers or interviews; human confirms |
| 6 | Codebase map | Context | Optional | Living | AI generates; human reviews |
| 7 | Coding standards | Context | Optional | Living | Human; AI may draft |
| 8 | Design system file | Context | Optional (projects with a UI) | Living | Human; often tool-generated |
| 9 | Glossary | Context | Optional | Living | Human; AI drafts |
| 10 | Reference exemplars | Context | Optional | Living | Human |
| 11 | On-demand project knowledge base | Context | Optional | Living | AI, directed by the developer |
| 12 | External dependency and standards reference | Context | Optional | Tied to each dependency version | Third party; human curates |
| 13 | Development workflow definition | Context | Optional | Living | Human (often a tool template) |
| 14 | Document templates and authoring rules | Context (setup) | Optional | Living | Tool; human customises |
| 15 | Agent autonomy and guardrail policy | Context | Optional | Living | Human; AI may draft hooks |
| 16 | Agent context exclusion file | Context | Optional | Long-lived | Human |
| 17 | Reusable agent commands and skills | Context (cross-cutting) | Optional | Living | Human or vendor; AI drafts |
| 18 | Specialist agent definitions | Context (cross-cutting) | Optional | Living | Human or AI; reviewed |
| 19 | Agent environment setup and tool configuration | Context (setup) | Optional | Living | Human or CLI |
| 20 | Agent context evaluation suite | Context + Maintenance | Optional | Living | Human with AI help |
| 21 | Idea exploration and assessment | Intent (ideation) | Optional | Per initiative | AI facilitates; human decides |
| 22 | Product requirements document (PRD) | Intent | Optional | Living for the initiative | AI drafts; human approves |
| 23 | Feature specification | Intent | **Core** | Per change, or merged into #54 | AI drafts; human approves |
| 24 | Change proposal | Intent | Optional | Per change; archived | AI drafts; human reviews |
| 25 | Bug specification | Intent | Optional | Per bug; the tests persist | Human reports; AI drafts |
| 26 | Clarification record | Intent (and later phases) | Optional | Per feature; kept | AI asks and records; human answers |
| 27 | Research notes | Design | Optional | Per feature | AI; human steers |
| 28 | System architecture description | Design | Optional | Living | AI drafts; human decides |
| 29 | Feature technical design | Design | **Core** (light for small changes) | Per change | AI; human approves |
| 30 | Data model | Design | Optional | Per feature or living | AI; human reviews |
| 31 | Interface contracts | Design | Optional | Living; versioned | AI, or human (API-first) |
| 32 | UX/UI specification | Design | Optional (projects with a UI) | Per feature | Human decides; AI facilitates |
| 33 | Security requirements and threat model | Design | Optional | Living | Human; AI assists |
| 34 | Operations specification and runbooks | Design + Maintenance | Optional | Living | AI drafts; human approves |
| 35 | Decision record | Design (cross-cutting) | Optional | Living; superseded rather than rewritten | Human decides; AI drafts |
| 36 | Formal and semi-formal behavioural specification | Design | Optional | Living or intermediate | AI; human refines |
| 37 | Roadmap and work breakdown | Planning | Optional | Living | AI drafts; PO or PM approves |
| 38 | Implementation plan and task list | Planning | **Core** | Per change | AI; human reviews |
| 39 | Agent work order | Planning | Optional | Per task; kept | Human or AI; human reviews |
| 40 | Risk and technical debt register | Planning (also intent and maintenance) | Optional | Living; per-story snapshots | AI drafts; human reviews |
| 41 | Test plan and strategy | Planning | Optional | Per feature or epic; project-level plan is living | AI QA agent; human QA |
| 42 | Progress and status record | Implementation (cross-cutting) | Optional | Living | AI or tool; humans record approvals |
| 43 | Session handoff summary | Implementation | Optional | Throwaway | AI |
| 44 | Implementation log and audit trail | Implementation | Optional | History; append-only | AI or system |
| 45 | In-code specification and documentation | Implementation | Optional | Directives throwaway; the rest living | Human directives; AI-generated notes |
| 46 | Commits and pull request descriptions | Implementation → Verification | **Core** | Permanent; PR description frozen at merge | AI writes; human reviews |
| 47 | Specification review | Verification (before implementation) | Optional | Checklists kept; reports ephemeral | AI; human decides |
| 48 | Acceptance scenarios and validation guide | Verification | Optional | Per feature or per project | AI; human reviews |
| 49 | Executable test specification | Verification | **Core** | Living | AI writes; human approves |
| 50 | Code review report | Verification | **Core** practice | Per change; often ephemeral | AI reviewer; human triages |
| 51 | Verification report and evidence pack | Verification | Optional | Per feature or phase | AI verifier; human does UAT |
| 52 | Traceability matrix | Verification | Optional | Regenerated | AI or tool; human checks |
| 53 | Gate decision record | Verification (at every phase boundary) | Optional | Per gate; kept | AI proposes; human decides |
| 54 | Living system specification | Maintenance (brownfield bootstrap at context) | Optional | Living | AI or mechanical merge; human reviews |
| 55 | Drift report | Maintenance | Optional | Per run, or a cumulative log | Tool or AI; human curates |
| 56 | Lessons learned and agent memory | Maintenance | Optional | Cumulative | AI; human promotes lessons |
| 57 | User and developer documentation | Implementation end + Maintenance | Optional | Living | Human, or AI with review |
| 58 | Production feedback report | Maintenance | Optional | Dated; append-only | AI drafts; human approves |

---

## 1. Context

### 1. Agent instructions file
- **Purpose:** A version-controlled briefing that gives any coding agent the project knowledge it cannot infer from the code. It is the entry point and router of the context chain: it summarises the fuller documents (#2, #5, #6, #7, #28) and links to them rather than duplicating them. Its instructions are advisory context, not enforced. Anything that must hold whatever the model does belongs in #15.
- **Typical contents:**
  - Build, test and lint commands.
  - Conventions that differ from the defaults.
  - Repository etiquette (branches, commits, PRs).
  - A short architecture summary.
  - Environment quirks and pitfalls.
  - Boundaries.
  - Typically, pointers to specs, plans, rules and skills.

  The file comes in scope layers: organisation-managed policy, the user's global file, the project root file, nested per-directory files and local or temporary overrides. Nested files are more specific. In some tools the closest file takes precedence; in Claude Code nested files are added on demand, and conflicting instructions may be resolved arbitrarily.

  The root and ancestor layers are always loaded. Nested files often load just in time, when the agent works in that directory. Keep the file short and prune it. Claude Code suggests a target of about 200 lines and skips files over 4 MiB. Codex's default limit for the combined files is 32 KiB, which is configurable (`project_doc_max_bytes`).
- **When written:** At project setup, often bootstrapped by the agent (`/init`, generated steering docs). Edited whenever the agent repeats a mistake or a convention changes.
- **Author:** Owned by a human. Often drafted by AI, and the AI may propose edits that a human approves. In one study, LLM-generated files lowered success slightly (about 0.5–3%), developer-written files gave only a marginal gain, and both raised inference cost by more than 20% (arXiv 2602.11988).
- **Core or optional:** Core.
- **Lifespan:** Living. Committed and pruned like code. Personal and local layers are not committed.
- **Also called / tool examples:** AGENTS.md, CLAUDE.md, GEMINI.md, AGENT.md, copilot-instructions.md, rules file, README for agents, context file, always-on steering file.
  - Claude Code: `CLAUDE.md`, `CLAUDE.local.md`, managed `CLAUDE.md` (it does not read `AGENTS.override.md`).
  - Codex: `AGENTS.md`, `AGENTS.override.md`, `~/.codex/AGENTS.md`.
  - Copilot: `.github/copilot-instructions.md` and organisation instructions.
  - Gemini CLI: `GEMINI.md`.
  - Cursor, Windsurf, Kiro, Junie, Cline and Aider: AGENTS.md support.
  - Ralph loop: `AGENT.md`.
  - Codified Context: the "hot-memory constitution" is in fact a file of this type.
  - Spec Kit's plan step regenerates the agent-context file.

  AGENTS.md is used by more than 60,000 projects and supported by more than 20 agents, and it is stewarded by the Agentic AI Foundation (Linux Foundation). Agent-written "memory" belongs to #56.
- **Sources:** [AGENTS.md](https://agents.md/) · [Claude Code memory](https://code.claude.com/docs/en/memory) · [Claude Code best practices](https://code.claude.com/docs/en/best-practices) · [OpenAI Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) · [Copilot repository instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions) · [Gemini CLI GEMINI.md](https://geminicli.com/docs/cli/gemini-md/) · [Junie guidelines](https://junie.jetbrains.com/docs/guidelines-and-memory.html) · [Cursor rules](https://cursor.com/docs/context/rules) · [BMAD project context](https://docs.bmad-method.org/existing-codebases/set-and-maintain-project-context/) · [Fowler: context engineering](https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html) · [Huntley: Ralph](https://ghuntley.com/ralph/) · [arXiv 2509.14744](https://arxiv.org/html/2509.14744v1) · [arXiv 2511.12884](https://arxiv.org/html/2511.12884v1) · [arXiv 2510.21413](https://arxiv.org/html/2510.21413v4) · [arXiv 2602.11988](https://arxiv.org/html/2602.11988v1) · [arXiv 2601.20404](https://arxiv.org/abs/2601.20404) · [arXiv 2602.20478 (Codified Context)](https://arxiv.org/html/2602.20478) · [arXiv 2609.00252](https://arxiv.org/html/2609.00252v1)

### 2. Project constitution
- **Purpose:** A short set of project-wide principles and non-negotiable rules. Every spec, plan and change must follow them, and they are used as gates during planning and review. The constitution is stable and changes only through an explicit, rare amendment that a human approves.
- **Typical contents:**
  - Numbered articles, each with its rationale. Spec Kit's example articles are library-first, CLI interface mandate, test-first, simplicity, anti-abstraction and integration-first testing; a project may define its own.
  - Some projects add security principles mapped to CWE, each with an RFC 2119 enforcement level.
  - The amendment procedure.

  The constitution holds only cross-cutting principles. Rules for one area belong in #7, process steps and the Definition of Done in #13, and agent permissions in #15.
- **When written:** At project start. It is checked whenever a plan or analysis runs. In Spec Kit, the gates are the Phase -1 gates of the plan template, and justified exceptions are recorded in the plan's "Complexity Tracking" section.
- **Author:** Human (maintainers, tech lead or architect). Often drafted by AI from an interview and approved by a human.
- **Core or optional:** Optional. Worth having when several people or agents contribute and the team wants explicit gates. Otherwise its rules live in #1. Many tools, including Kiro and the lighter frameworks, have no constitution.
- **Lifespan:** Living and versioned, with dated amendments.
- **Also called / tool examples:** constitution.md, project principles, non-negotiables.
  - Spec Kit: `.specify/memory/constitution.md`, created with `/speckit.constitution`. Its analyze step treats violations as CRITICAL.
  - Akka Specify: `constitution.md`, created with `/akka:constitution` and checked by `/akka:clarify`, `/akka:implement` and `/akka:review`.
  - Constitutional SDD: a versioned constitution mapped to CWE. The evidence is a single-developer case study.

  Fowler frames the constitution as a heavily used rules file in the memory bank.
- **Sources:** Primary: [Spec Kit spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) · [Spec Kit agentic SDD reference](https://github.github.io/spec-kit/reference/agentic-sdd.html) · [Akka SDD](https://doc.akka.io/sdk/spec-driven-development.html) · [arXiv 2602.02584 (Constitutional SDD)](https://arxiv.org/html/2602.02584v1). Secondary: [Fowler: SDD tools](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) · [Thoughtworks Radar](https://www.thoughtworks.com/radar/techniques/spec-driven-development) · [GEICO](https://www.geico.com/techblog/an-introduction-to-spec-driven-development/)

### 3. Product context (vision)
- **Purpose:** A persistent, project-wide explanation of why the product exists: its users, the problems it solves, its goals and its scope. It lets the agent make decisions that fit the product, and it is the context every requirement must align with.
- **Typical contents:** Purpose and vision, target users, problems, key features, business and UX goals, and scope. Success metrics and non-goals are common, though they come mainly from brief- and PRD-style sources. Optionally, prose and brand guidelines. The classic forerunners are the RUP vision document, IEEE 1362 ConOps and the Scrum Product Goal; these are analogies, and none of the SDD sources cites them.
- **When written:** At project start. Generated on request from the repo or from an AI interview, then approved by a human. Kiro's "Generate Steering Docs" runs only when the user triggers it. Revised when the product changes direction.
- **Author:** Human and AI.
- **Core or optional:** Core for greenfield or product-scale work. Often absent in minimal, change-centric flows: Spec Kit has no product-context file, and small brownfield changes often skip it.
- **Lifespan:** Living and project-wide.
- **Also called / tool examples:** product.md, mission.md, PROJECT.md, projectbrief.md, productContext.md, vision document, product-guidelines.md.
  - Kiro: `.kiro/steering/product.md`.
  - cc-sdd: steering `product.md`.
  - Agent OS: `product/mission.md`.
  - Conductor: `product.md`, `product-guidelines.md`.
  - GSD: `.planning/PROJECT.md`, always loaded.
  - Cline: `projectbrief.md`, `productContext.md`.

  Briefs for one initiative are not this type. The BMAD product brief and AI-DLC's `intent-statement.md` and `initiative-brief.md` belong to #21 or are precursors of #22.
- **Sources:** [Kiro steering](https://kiro.dev/docs/steering/) · [Agent OS product planning](https://buildermethods.com/agent-os/product-planning) · [Conductor](https://github.com/gemini-cli-extensions/conductor) · [spec-workflow MCP](https://github.com/Pimzino/spec-workflow-mcp/blob/main/docs/WORKFLOW.md) · [cc-sdd commands](https://github.com/gotalab/cc-sdd/blob/main/docs/guides/command-reference.md) · [GSD docs](https://mintlify.wiki/gsd-build/get-shit-done) · [Cline Memory Bank](https://docs.cline.bot/prompting/cline-memory-bank) · [Osmani: good spec](https://addyosmani.com/blog/good-spec/) · [Scrum Guide](https://scrumguides.org/scrum-guide.html)

### 4. Market and domain research report
- **Purpose:** Gives the product brief and the PRD cited evidence about the market, competitors and customer needs, and about the business domain: terminology, standards, regulations and stakeholder workflows. Scope and MVP cuts then rest on sourced facts rather than on the model's assumptions. Research into technical feasibility belongs to #27, and the decision whether to build belongs to #21.
- **Typical contents:**
  - Research objectives and method.
  - Market definition, sizing, segments and trends.
  - Customer analysis: jobs-to-be-done and customer journeys.
  - Competitive landscape: profiles, a feature matrix, SWOT, positioning and pricing.
  - Industry analysis.
  - Domain terminology, standards, regulations and workflows.
  - Recommendations for scope, MVP, go-to-market and pricing.
  - A bibliography with URLs and access dates, with unverified claims flagged.

  It may be split into a market and competitive report and a separate domain report.
- **When written:** Before the brief or PRD, for a new product or a major new capability. Refreshed when it goes stale or before a scope decision. A fixed refresh cadence is an editorial suggestion, not something the sources prescribe.
- **Author:** An AI analyst agent using web or deep-research tools, guided and reviewed by a human product owner or analyst.
- **Core or optional:** Optional. Worth writing for greenfield products, new markets, and regulated or unfamiliar domains. The main code-centric SDD toolkits (Spec Kit, Kiro, OpenSpec, Tessl, Agent OS) do not have it. The evidence comes from BMAD and from AI product-management tools.
- **Lifespan:** Kept as reference while the brief and PRD are written, then mostly static. Its findings should migrate into #9, #12, #33 and #3 so that the report does not become a stale parallel source.
- **Also called / tool examples:** market research report, competitor analysis, domain research report.
  - BMAD v4: `market-research-tmpl.yaml` and `competitor-analysis-tmpl.yaml`, both optional before the Project Brief.
  - BMAD v6: the Market Research (MR) and Domain Research (DR) workflows.
  - The `bmad-research` skill writes one combined report; only its market, competitive and domain parts belong here.
  - Product-management tools: ChatPRD's Competitive Analysis Report, Spec and Productboard Spark.
- **Sources:** [BMAD analyst reference](https://mintlify.wiki/bmad-code-org/BMAD-METHOD/reference/agents/analyst) · [BMAD getting started](https://mintlify.wiki/bmad-code-org/BMAD-METHOD/tutorials/getting-started) · [BMAD v4 market research template](https://github.com/bmad-code-org/BMAD-METHOD/blob/v4.44.0/bmad-core/templates/market-research-tmpl.yaml) · [BMAD v4 competitor analysis template](https://github.com/bmad-code-org/BMAD-METHOD/blob/v4.44.0/bmad-core/templates/competitor-analysis-tmpl.yaml) · [BMAD v4.43.1 user guide](https://cdn.jsdelivr.net/npm/@ptnglobal/bmad-method@4.43.1/docs/user-guide.md) · [bmad-research skill](https://claudeskills.info/skills/aj-geddes/claude-code-bmad-skills/bmad-research/) · [ChatPRD templates](https://www.chatprd.ai/docs/included-templates) · [Spec](https://www.shyft.ai/tools/spec) · [Productboard Spark](https://www.productboard.com/blog/introducing-spark-ai-product-management-agent/) · [Vibe Coding Academy (course-level illustration)](https://www.vibecodingacademy.ai/lessons/coming-up-with-a-comprehensive-competitive-analysis)

### 5. Technology stack and technical constraints
- **Purpose:** Records the chosen languages, frameworks, libraries, versions and technical constraints, so that the agent stays within the stack. It records what was chosen. The executable commands and MCP configuration belong to #19, and API usage documentation belongs to #12.
- **Typical contents:** Languages and versions, frameworks, libraries and the alternatives to prefer, the chosen build and dev-setup tooling, hosting and runtime constraints, and dependencies. Some tools also put architecture decisions and non-functional constraints in this file (spec-workflow's `tech.md`), which overlaps #28. It partly corresponds to arc42 section 2 (Constraints) and to the design and implementation constraints of an SRS. A feature design, such as Spec Kit's "Technical Context" section in `plan.md`, may refine the stack for one feature but not override it.
- **When written:** At setup. Updated when a dependency or framework changes.
- **Author:** Inferred from the codebase (brownfield) or captured by interviewing the human (greenfield), then confirmed by a human.
- **Core or optional:** Core content. A separate file is optional: in small projects this is a section of #1.
- **Lifespan:** Living.
- **Also called / tool examples:** tech.md, tech-stack.md, techContext.md, technical steering.
  - Kiro: `.kiro/steering/tech.md`, included in every interaction by default.
  - Agent OS: `product/tech-stack.md`, created by `/plan-product`.
  - Conductor: `tech-stack.md`.
  - BMAD v4: `docs/architecture/tech-stack.md`.
  - Cline: `techContext.md`.
  - spec-workflow MCP and cc-sdd: `steering/tech.md`.
- **Sources:** [Kiro steering](https://kiro.dev/docs/steering/) · [Agent OS product planning](https://buildermethods.com/agent-os/product-planning) · [Agent OS file structure](https://buildermethods.com/agent-os/file-structure) · [Conductor](https://github.com/gemini-cli-extensions/conductor) · [BMAD v4 user guide](https://github.com/bmad-code-org/BMAD-METHOD/blob/v4.44.3/docs/user-guide.md) · [spec-workflow MCP](https://github.com/Pimzino/spec-workflow-mcp/blob/main/docs/WORKFLOW.md) · [Cline Memory Bank](https://docs.cline.bot/prompting/cline-memory-bank) · [arc42](https://docs.arc42.org/home/)

### 6. Codebase map
- **Purpose:** Describes how the existing code is organised, so that generated code lands in the right place, especially in brownfield systems. It covers the physical layout of the repository. The intended system structure belongs to #28, the stack to #5, and risks and concerns can be cross-referenced to #40.
- **Typical contents:** Directory and module layout, naming and import conventions, module boundaries, critical paths, implicit rules and structural hotspots. Optionally, the last commit that was mapped, for drift checks. A packed dump of the code (such as repomix output) is a related throwaway input, not an authored map.
- **When written:** Generated at onboarding. Refreshed after major refactors or when drift is detected. GSD runs an automated drift gate after each phase and can remap automatically.
- **Author:** Generated by AI from the repo and reviewed by a human. GSD's `last_mapped_commit` stamp is written by a deterministic tool step, not by the AI.
- **Core or optional:** Optional. Worth writing for brownfield or large codebases. In small projects it is a section of #1.
- **Lifespan:** Living.
- **Also called / tool examples:** structure.md, source-tree.md, project-structure.md, codebase overview, onboarding summary.
  - Kiro: `.kiro/steering/structure.md`, which also holds some architectural decisions.
  - cc-sdd and spec-workflow MCP: `steering/structure.md`.
  - BMAD v4: `docs/architecture/source-tree.md`, listed in `devLoadAlwaysFiles`.
  - GSD: `.planning/codebase/` (from map-codebase) and `.planning/onboarding/STRUCTURE.md`.
  - AI-DLC: a per-repo CodeKB with `code-structure.md`, reused across intents and refreshed by a full or focused rescan.
  - Cline: `systemPatterns.md`, a weak partial match.
- **Sources:** [Kiro steering](https://kiro.dev/docs/steering/) · [spec-workflow MCP](https://github.com/Pimzino/spec-workflow-mcp/blob/main/docs/WORKFLOW.md) · [BMAD v4 core-config.yaml](https://github.com/bmad-code-org/BMAD-METHOD/blob/v4.44.3/bmad-core/core-config.yaml) · [BMAD: design UX and architecture](https://docs.bmad-method.org/plan/design-ux-and-architecture/) · [GSD architecture](https://github.com/open-gsd/gsd-core/blob/main/docs/ARCHITECTURE.md) · [AI-DLC artifacts](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/14-artifacts-reference.md) · [arXiv 2605.18684 (Reversa), supporting evidence](https://arxiv.org/abs/2605.18684) · [Harper Reed](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/) · [Garg: knowledge priming](https://www.martinfowler.com/articles/reduce-friction-ai/knowledge-priming.html) · [Osmani](https://addyosmani.com/blog/good-spec/)

### 7. Coding standards
- **Purpose:** Normative rules for how code is written in each area: API style, error handling, testing, security, migrations and language idioms. The type is defined by its content, not by how it is loaded. The rules are often loaded only when relevant (by path or glob, by description, or by manual mention) and sometimes always loaded: Kiro recommends always loading core security standards, and Aider loads CONVENTIONS.md through `--read`. AI reviewers also check diffs against them. Coding standards say how to write code; #6 says where things are. Deployment procedures belong to #34.
- **Typical contents:**
  - Topic files containing rules, good and bad examples, and preferred libraries and patterns.
  - Activation metadata.
  - Review instructions per path.
- **When written:** When conventions are agreed, or discovered from existing code. Updated through #56 and whenever the agent repeats a mistake.
- **Author:** Human (team or corporate standards). The AI may discover patterns or draft rules; humans curate them.
- **Core or optional:** Optional. Worth a separate file when the conventions are too many or too area-specific for #1.
- **Lifespan:** Living and versioned. Can be shared across projects as global or profile-level rules. Copies made for one spec, such as Agent OS's per-spec `standards.md`, are snapshots.
- **Also called / tool examples:** coding-standards.md, CONVENTIONS.md, standards/, code_styleguides/, style guide for agents, code review instructions. The containers `.cursor/rules/*.mdc`, `.github/instructions/*.instructions.md` and `.claude/rules/` can hold this type but also hold other types.
  - Claude Code: `.claude/rules/` with `paths` frontmatter.
  - Cursor: `.mdc` files (`globs`, `alwaysApply`).
  - Copilot: `applyTo`.
  - Windsurf: `.windsurf/rules`.
  - Cline: `.clinerules/`.
  - Kiro: steering files with fileMatch, auto or manual inclusion, and `steering/security-policies.md`. All four inclusion modes need Kiro CLI V3 or the IDE.
  - Agent OS: `agent-os/standards/` and `index.yml`.
  - Conductor: `code_styleguides/`.
  - Aider: `CONVENTIONS.md`.
  - CodeRabbit: `path_instructions`.
  - Tessl: rules as versioned context (unverified).
- **Sources:** [Agent OS file structure](https://buildermethods.com/agent-os/file-structure) · [Agent OS shape spec](https://buildermethods.com/agent-os/shape-spec) · [Conductor](https://github.com/gemini-cli-extensions/conductor) · [Kiro steering](https://kiro.dev/docs/steering/) · [Aider conventions](https://aider.chat/docs/usage/conventions.html) · [Claude Code memory](https://code.claude.com/docs/en/memory) · [Cursor rules](https://cursor.com/docs/context/rules) · [Copilot instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions) · [Windsurf/Devin rules](https://docs.devin.ai/desktop/cascade/memories) · [Cline rules](https://docs.cline.bot/features/cline-rules) · [Red Hat: SDD quality](https://developers.redhat.com/articles/2025/10/22/how-spec-driven-development-improves-ai-coding-quality) · [arXiv 2512.18925 (Cursor rules study)](https://arxiv.org/html/2512.18925v2) · [CodeRabbit path instructions](https://docs.coderabbit.ai/configuration/path-instructions)

### 8. Design system file
- **Purpose:** A persistent, machine-readable description of the project's visual identity. Agents load it so that generated UI stays on-brand and consistent. Mockups and flows for one feature belong to #32, which should reference these tokens rather than restate them. (Calling it the UI counterpart of #1 and #7 is this catalogue's framing, not a claim from the sources.)
- **Typical contents:**
  - YAML design tokens: colors, typography, rounded, spacing and components. Token types are Color, Dimension, Token Reference and Typography. Tokens can reference each other, as in `{colors.primary}`.
  - Markdown prose in a fixed section order: Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, and Do's and Don'ts. Sections are optional, but those present must follow this order, and a duplicate heading is an error.
  - Component reuse rules.
  - Community extensions (VoltAgent): responsive behaviour, an agent prompt guide and preview pages.

  The CLI lints the file (11 rules, including WCAG contrast), diffs versions (exit code 1 on regressions), exports to Tailwind and W3C DTCG tokens, and prints the spec for agent prompts.
- **When written:** When a project with a UI is set up or a design system is adopted. The file may be exported from a design tool, extracted from an existing site, copied from a template or written by hand. Updated, with lint and diff, whenever the tokens change.
- **Author:** Designer or developer. Often generated or extracted by tooling, then curated by a human.
- **Core or optional:** Optional. For projects with a UI where visual consistency matters.
- **Lifespan:** Living and versioned. Usually kept at the repository root.
- **Also called / tool examples:** DESIGN.md, design tokens file, design system rules.
  - Google Labs DESIGN.md format and the `@google/design.md` CLI. Both are alpha, and the spec, schema and CLI are still changing.
  - Google Stitch: DESIGN.md export.
  - VoltAgent: awesome-design-md.
  - Figma MCP: the `create_design_system_rules` prompt. Its output is saved to a rules or instructions folder, such as `.cursor/rules` with `alwaysApply` or a section of CLAUDE.md. It also covers the codebase and stack, so it overlaps #7.
- **Sources:** [google-labs-code/design.md](https://github.com/google-labs-code/design.md) · [Better Stack guide](https://betterstack.com/community/guides/ai/design-md-ai/) · [Google DESIGN.md overview](https://themenonlab.blog/blog/google-design-md-ai-agents-design-systems) · [VoltAgent awesome-design-md](https://github.com/VoltAgent/awesome-design-md) · [Figma MCP tools and prompts](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/) · [Figma MCP custom rules](https://developers.figma.com/docs/figma-mcp-server/add-custom-rules/)

### 9. Glossary (ubiquitous language)
- **Purpose:** Defines business and technical terms, so that humans and agents use one vocabulary in specs and code and the agent does not misread the domain.
- **Typical contents:**
  - Terms with definitions.
  - Synonyms to avoid.
  - Relationships and invariants between terms.
  - Flagged ambiguities (overloaded words).
  - Links to entities.
  - Grouping by bounded context.
  - Optional translations (arc42).
- **When written:** Created lazily, when the first domain term is resolved (often in spec or plan interviews) or when a terminology conflict appears. Extended whenever a spec introduces or disambiguates a term, and updated before the code when a term changes. Larger systems keep one glossary per bounded context.
- **Author:** Humans (domain experts and engineers). The AI often drafts it from conversations, flags ambiguous terms and synonyms, and proposes canonical names for a human to approve. Agents read it every iteration, or #1 points to it.
- **Core or optional:** Optional. Worth having when the domain language is non-trivial and not already encoded in types. Context files have measured costs.
- **Lifespan:** Living.
- **Also called / tool examples:** domain glossary, ubiquitous language (DDD), UBIQUITOUS_LANGUAGE.md, DOMAIN_GLOSSARY.md, CONTEXT.md (a glossary for one bounded context).
  - arc42 section 12.
  - The mattpocock/skills `ubiquitous-language` skill.
  - The grill-with-docs and domain-model skills, which write `CONTEXT.md` and `CONTEXT-MAP.md`.
- **Sources:** [arc42 §12](https://docs.arc42.org/section-12/) · [ubiquitous-language skill](https://skills.sh/mattpocock/skills/ubiquitous-language) · [grill-with-docs skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md) · [AI Hero changelog](https://www.aihero.dev/skills-changelog-ubiquitous-language-grill-with-docs) · [agentpatterns: ubiquitous language](https://www.agentpatterns.ai/instructions/ubiquitous-language-for-ai-plans/) · [Glossary as agent constraint](https://understandingdata.com/posts/domain-glossary-as-agent-constraint/). Supporting the practice only: [Thoughtworks](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices) · [GEICO](https://www.geico.com/techblog/an-introduction-to-spec-driven-development/)

### 10. Reference exemplars
- **Purpose:** Points the agent to real code that shows the desired patterns, style and tests. The agent imitates it as few-shot context, and it is the baseline for spotting pattern drift. The drift output itself belongs to #55.
- **Typical contents:** Usually code, or a list of pointers to code, rather than prose. Fowler and Boeckeler found that keeping code samples in Markdown was tedious and moved to a compilable reference project. Forms include an `examples/` folder with a README, a reference application or service template, and pointers to existing features to copy (`references.md`, or the EXAMPLES section of INITIAL.md). For a port, the existing implementation is the reference; its test suite belongs to #49. Mockups belong to #32.
- **When written:** With the project or template. For one piece of work, when the feature is shaped. Agent OS asks the user to "point to existing features or files to study".
- **Author:** Human, sometimes with AI help.
- **Core or optional:** Optional. Worth having when established patterns must be imitated, or when porting.
- **Lifespan:** Living, and must be kept current. Lists made for one feature are kept with the spec.
- **Also called / tool examples:** references.md, examples/, reference implementation, reference application, service template.
  - Agent OS: `specs/<x>/references.md`.
  - Context Engineering: `examples/`, listed in INITIAL.md.
  - Boeckeler: a reference app exposed through an MCP server that serves code samples and recent commits.
- **Sources:** [Agent OS shape spec](https://buildermethods.com/agent-os/shape-spec) · [Fowler: anchoring to a reference application](https://www.martinfowler.com/articles/exploring-gen-ai/anchoring-to-reference.html) · [Willison: porting JustHTML](https://simonwillison.net/2025/Dec/15/porting-justhtml/) · [Osmani](https://addyosmani.com/blog/good-spec/) · [Context Engineering intro](https://github.com/coleam00/context-engineering-intro)

### 11. On-demand project knowledge base
- **Purpose:** Deeper documents, each on one subsystem or topic, that the agent fetches only when relevant (progressive disclosure), keeping the always-loaded context small. They hold descriptive knowledge only: rules belong in #7 and runbooks in #34. They are also maintained with each change.
- **Typical contents:** Subsystem descriptions (file paths, parameters, expected behaviour), failure-mode and symptom-cause-fix tables, and integration and testing notes. They are referenced from #1 but not eagerly imported (Claude Code `@imports` load at launch, so they are not on demand), discovered by path, or served by an MCP retrieval server.
- **When written:** When a subsystem becomes complex, or repeated agent failures expose missing knowledge. Codified Context recommends updating the documents in the same session as the code change, a periodic review (biweekly, 30–45 minutes), and a drift check at session start that compares recent commits against the map of subsystems to files.
- **Author:** Usually written by AI at the developer's direction. The developer decides structure and scope.
- **Core or optional:** Optional. For large codebases or complex subsystems. The evidence comes without controlled benchmarks.
- **Lifespan:** Living. Staleness is the main way it fails.
- **Also called / tool examples:** cold-memory specs, subsystem specs, agent_docs/, docs/ for agents, Memory Bank additional files.
  - Cline: additional Memory Bank files.
  - Claude Code: subdirectory CLAUDE.md files, loaded when Claude touches that directory.
  - Gemini CLI: just-in-time discovery of subdirectory GEMINI.md files.
  - Codified Context: Tier 3 subsystem documents retrieved through MCP (for example `find_relevant_context(task)`).
  - HumanLayer: `agent_docs/`.
- **Sources:** [arXiv 2602.20478 (Codified Context)](https://arxiv.org/html/2602.20478) · [Cline Memory Bank](https://docs.cline.bot/prompting/cline-memory-bank) · [HumanLayer: writing a good CLAUDE.md](https://humanlayer.com/blog/writing-a-good-claude-md) · [Claude Code memory](https://code.claude.com/docs/en/memory) · [Gemini CLI GEMINI.md](https://geminicli.com/docs/cli/gemini-md/) · [arXiv 2609.00252, supporting evidence](https://arxiv.org/html/2609.00252v1)

### 12. External dependency and standards reference
- **Purpose:** Authoritative, version-matched material on how to use external libraries, APIs and standards, and the organisation's own shared libraries and platforms. It stops the agent relying on outdated training data or inventing APIs. #5 names the dependencies and versions; this type holds the usage material for them. The project's own subsystem documents belong to #11.
- **Typical contents:**
  - Usage material per library version (patterns and pitfalls).
  - llms.txt files.
  - Standards included as git submodules.
  - Guides for internal shared libraries, platforms and organisation standards.
  - Documentation served through MCP.

  In lightweight practice this is just a curated list of 5–10 official documentation links, each pinned to a version, inside the stack section or #1 ("reference, do not duplicate").
- **When written:** When a dependency is adopted or upgraded, or when the agent hallucinates an API.
- **Author:** Mostly third-party material that humans select and pin. Teams may publish internal guides.
- **Core or optional:** Optional. Worth having for dependencies that are newer than the model's training, niche or internal.
- **Lifespan:** Persistent while the dependency is in use, and updated when its version changes. Much of it (llms.txt, MCP-served documentation) is fetched live from the vendor rather than stored in the repo.
- **Also called / tool examples:** usage spec, library spec, llms.txt, API docs for agents.
  - Tessl: a registry of versioned docs, skills and rules.
  - llms.txt files.
  - Context7 and other MCP documentation servers.
  - Cursor FastRender: the WhatWG and CSS-WG specs included as git submodules.
- **Sources:** [Tessl launch](https://tessl.io/blog/tessl-launches-spec-driven-framework-and-registry) · [Tessl docs](https://docs.tessl.io/) · [Willison: conformance suites (FastRender)](https://simonwillison.net/tags/conformance-suites/) · [Osmani](https://addyosmani.com/blog/good-spec/) · [Garg: knowledge priming (version-pinned links)](https://www.martinfowler.com/articles/reduce-friction-ai/knowledge-priming.html)

### 13. Development workflow definition
- **Purpose:** States how work proceeds: which phases and agents run in what order, the review checkpoints, the evidence each class of work needs, the TDD and commit strategy, and the Definition of Done. The constitution (#2) holds the principles and non-negotiable gates; this type holds the procedure. Acceptance criteria for one feature belong in #23 and #48, and autonomy and permissions in #15.
- **Typical contents:**
  - Phase sequence and gates.
  - Task decomposition strategy.
  - Rigour and required evidence for each class or risk level of work.
  - Commit and PR policy.
  - Review steps.
  - The Definition of Done (tests pass, review done, no weakened tests, docs updated, security checks).
  - A schema stating which artifacts are produced and in what order.
- **When written:** At project start. Revised when the process changes.
- **Author:** Human (team, coach or process owner). Often a tool template customised by humans.
- **Core or optional:** Optional. A separate file when several people or agents must follow the same process; otherwise a section of #1 or of #2.
- **Lifespan:** Living and versioned.
- **Also called / tool examples:** workflow.md, SOP, LoopScript, process definition, Definition of Done (DoD), quality bar, workflow schema.
  - Conductor: `conductor/workflow.md`. Verified only as holding team preferences such as TDD and commit strategy.
  - Spec Kit: the "Development Workflow / Review Process / Quality Gates" section of `constitution.md`.
  - SASE: LoopScript.
  - OpenSpec: a schema that sets the order of artifacts.
  - BMAD: workflow definitions that sequence agents. Borderline, since they overlap #17.
- **Sources:** [Conductor](https://github.com/gemini-cli-extensions/conductor) · [arXiv 2509.06216 (SASE)](https://arxiv.org/html/2509.06216v2) · [arXiv 2609.00252 (workflow definitions; evidence-backed acceptance)](https://arxiv.org/html/2609.00252v1) · [OpenSpec glossary](https://openspec.dev/docs/glossary) · [Scrum Guide](https://scrumguides.org/scrum-guide.html) · [Shiplight: DoD for AI code](https://www.shiplight.ai/blog/definition-of-done-ai-generated-code) · [sd-workflow](https://github.com/mode41/sd-workflow) · [Factory: agent-driven development](https://docs.factory.ai/agent-driven-development)

### 14. SDD document templates and authoring rules
- **Purpose:** Editable templates that fix the structure of each SDD document, plus the rules the AI follows when it writes them, so that its output is consistent. They are setup or meta documents: they shape the other documents rather than describe the project. The commands and skills in #17 fill the templates in, and #7 governs code, not documents.
- **Typical contents:** Skeletons for the spec, plan, tasks, checklists and PRPs; generation rules and judgment criteria; per-artifact templates; plan-authoring rulebooks. PLANS.md, for example, also governs how plans are carried out, which partly overlaps #13.
- **When written:** Installed with the SDD tool. Customised when the team standardises its documents.
- **Author:** Shipped by the tool, and humans may customise it. A rulebook like PLANS.md can be written by a human from scratch.
- **Core or optional:** Optional. Not universal: Kiro and Tessl have no templates the user can see.
- **Lifespan:** Living.
- **Also called / tool examples:** templates/, user-templates/, settings/rules/, PLANS.md, prp_base.md.
  - Spec Kit: `templates/*.md`, filled in by its slash commands.
  - cc-sdd: `settings/templates/` and `settings/rules/`, where teams customise them.
  - spec-workflow MCP: `templates/` and `user-templates/`.
  - OpenSpec: per-artifact templates supplied by its schema.
  - Codex: `.agent/PLANS.md`.
  - Context Engineering: `PRPs/templates/prp_base.md`.
- **Sources:** [cc-sdd](https://github.com/gotalab/cc-sdd) · [spec-workflow MCP](https://github.com/Pimzino/spec-workflow-mcp) · [Spec Kit spec template](https://github.com/github/spec-kit/blob/main/templates/spec-template.md) · [OpenSpec glossary](https://openspec.dev/docs/glossary) · [Codex ExecPlans](https://developers.openai.com/cookbook/articles/codex_exec_plans) · [Context Engineering intro](https://github.com/coleam00/context-engineering-intro) · [Fowler: SDD tools (Spec Kit templates)](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)

### 15. Agent autonomy and guardrail policy
- **Purpose:** Defines what the agent may do on its own, what needs human approval and what is forbidden, and turns rules that must never depend on the model into deterministic checks. The type is the policy, wherever it is stored. The prose boundaries usually sit inside #1 or the spec; the enforced part lives in harness configuration.
- **Typical contents:**
  - Always / Ask first / Never boundaries.
  - Permission rules (allow and deny, including denying reads).
  - Sandbox settings.
  - Hooks that enforce a boundary: block writes to protected paths, block dangerous commands, make format and lint mandatory.
  - Risk classes that decide how much autonomy is allowed.

  Hooks that automate the workflow (keep the turn open until tests pass, sync docs) are enforced workflow gates and belong to #13. The evidence each risk class needs belongs to #13, and the record of passing a gate to #53.
- **When written:** At setup. Tightened after incidents, or when agents gain more autonomy.
- **Author:** Human (team lead, platform or security). The AI may draft hook scripts.
- **Core or optional:** Optional. Worth having when agents run with autonomy, touch sensitive code, or a rule must be enforced deterministically.
- **Lifespan:** Living configuration under version control.
- **Also called / tool examples:** boundaries, boundaries section of AGENTS.md or CLAUDE.md, permissions policy, hooks.
  - Claude Code: permissions and hooks in `.claude/settings.json`.
  - Kiro: `.kiro/hooks/*.json`, or `~/.kiro/hooks/` for global hooks, with triggers PreToolUse, PostToolUse, PostFileSave and Stop.
  - VS Code Copilot: hooks.
  - Osmani: a "## Boundaries" section in the spec.
  - Agentic Agile-V: R0–R3 risk-adaptive acceptance gates. Illustrative only, from a single source.
- **Sources:** [Osmani](https://addyosmani.com/blog/good-spec/) · [Claude Code best practices](https://code.claude.com/docs/en/best-practices) · [Claude Code hooks](https://code.claude.com/docs/en/hooks-guide) · [Kiro hooks](https://kiro.dev/docs/hooks/) · [VS Code customization](https://code.visualstudio.com/docs/copilot/customization/overview) · [Kent Beck: augmented coding](https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes) · [Agentic Agile-V](https://www.alphaxiv.org/abs/2605.20456)

### 16. Agent context exclusion file
- **Purpose:** Lists the files and folders that agents must not index, retrieve or read: secrets, generated or vendored code, large binaries and data, and legacy code the agent should not imitate. It keeps context relevant and lowers the chance of exposing sensitive content. It is a best-effort context control, not a security boundary: Cursor states that its agent's terminal and MCP tools can still reach ignored files. Tools without an ignore file express the same intent as read-deny permissions (overlapping #15) or as a platform setting.
- **Typical contents:** gitignore-syntax patterns, usually at the repo root. Some tools also read hierarchical variants (opt-in in Cursor; `.aiexclude` applies at and below its own directory) or global ones. Some tools read other tools' files: Qwen reads `.agentignore` and `.aiignore`, and JetBrains honours `.cursorignore`, `.codeiumignore` and `.aiexclude`. Cursor already excludes git-ignored files and a built-in default list. Gemini Code Assist honours the root `.gitignore`, and `.aiexclude` wins when they conflict.
- **When written:** When the repository is set up for AI work, alongside #1. Updated when new sensitive, generated or deprecated paths appear. Some tools apply changes only after a session restart.
- **Author:** Human (developer, tech lead or security owner). It may be imposed centrally, in which case it is not versioned with the repository.
- **Core or optional:** Optional. No SDD framework requires it.
- **Lifespan:** Long-lived and versioned.
- **Also called / tool examples:**
  - Cursor: `.cursorignore`.
  - Gemini Code Assist: `.aiexclude`.
  - Gemini CLI: `.geminiignore`. Historical: per its documentation page, Gemini CLI was replaced by Antigravity CLI on 2026-06-18.
  - Qwen: `.qwenignore`.
  - JetBrains: `.aiignore`.
  - Aider: `.aiderignore`.
  - Windsurf `.codeiumignore`, Cline `.clineignore`, Roo `.rooignore`, Augment `.augmentignore`.
  - Claude Code: `permissions.deny` rules such as `Read(./.env)`.
  - GitHub Copilot: content exclusion in repository or organisation settings.
  - `.llmignore`: a v0.1.0 crate proposal, not an adopted standard.
- **Sources:** [Cursor ignore files](https://cursor.com/docs/context/ignore-files) · [Gemini Code Assist .aiexclude](https://docs.cloud.google.com/gemini/docs/codeassist/create-aiexclude-file) · [Gemini CLI .geminiignore](https://geminicli.com/docs/cli/gemini-ignore/) · [Qwen Code .qwenignore](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/qwen-ignore/) · [JetBrains .aiignore](https://www.jetbrains.com/help/ai-assistant/disable-ai-assistant.html) · [Aider options](https://aider.chat/docs/config/options.html) · [Claude Code settings](https://code.claude.com/docs/en/settings) · [llmignore crate](https://docs.rs/crate/llmignore/latest)

### 17. Reusable agent commands and skills
- **Phase:** Context. The type is cross-cutting: phase commands are invoked in every phase.
- **Purpose:** Stored prompts and procedure packages that run a repeatable step, including the SDD phases themselves (specify, plan, tasks, implement, review). A skill is discovered through its always-visible name and description, and its body is loaded on demand by the agent or the user; frontmatter decides who may invoke it. Commands and prompt files are invoked explicitly. In Claude Code, commands and skills are now one mechanism. A skill that holds only reference knowledge belongs to #11, a role with its own prompt and tools to #18, and the templates skills fill in to #14.
- **Typical contents:**
  - Name and description, the only required fields in the Agent Skills spec.
  - Instructions and arguments.
  - Optional license, compatibility, metadata and allowed-tools.
  - Tool-specific extensions: model, agent or mode, invocation controls, dynamic context injection.
  - Supporting references, templates and scripts.

  In loop workflows, the type also covers the prompt fed to the agent on every iteration. Ralph's PROMPT.md is borderline, since it sits close to #13.
- **When written:** When a step recurs. Installed by SDD toolkits. Tuned over time.
- **Author:** A human or a tool vendor. Often drafted by AI (skill-creator) and reviewed, and often reused from registries. Only agents run them.
- **Core or optional:** Optional. Usually shipped by the SDD tool; write your own when a workflow step repeats.
- **Lifespan:** Living and versioned.
- **Also called / tool examples:** SKILL.md, slash command, `.claude/commands/*.md` (the legacy form, which still works), `*.prompt.md`, workflow command, PROMPT.md.
  - Claude Code: `.claude/skills/<name>/SKILL.md`.
  - VS Code: `.github/prompts/*.prompt.md`. VS Code now recommends skills for portable workflows.
  - Windsurf and Cline: workflows.
  - Gemini CLI: custom commands.
  - Spec Kit: `/speckit-*` (formerly `/speckit.*`).
  - OpenSpec: `/opsx:*` (propose, apply, archive).
  - Superpowers: the writing-plans skill.
- **Sources:** [Claude Code skills](https://code.claude.com/docs/en/skills) · [Agent Skills spec](https://agentskills.io/specification) · [VS Code prompt files](https://code.visualstudio.com/docs/copilot/customization/prompt-files) · [VS Code customization](https://code.visualstudio.com/docs/copilot/customization/overview) · [Windsurf/Devin workflows](https://docs.devin.ai/desktop/cascade/memories) · [Huntley: Ralph](https://ghuntley.com/ralph/) · [Superpowers](https://blog.fsck.com/2025/10/09/superpowers/) · [OpenSpec](https://github.com/Fission-AI/OpenSpec) · [Red Hat: vibes, specs, skills, agents](https://developers.redhat.com/articles/2026/03/30/vibes-specs-skills-agents-ai-coding) · [arXiv 2607.01456](https://arxiv.org/abs/2607.01456) · [arXiv 2607.00911](https://arxiv.org/pdf/2607.00911)

### 18. Specialist agent definitions
- **Phase:** Context. Cross-cutting, since these agents act in planning, implementation and verification.
- **Purpose:** Define specialised roles (planner, architect, reviewer, test writer, security reviewer, researcher), each with its own system prompt, tools, model and context, so that SDD phases can be split across agents. Chat modes and custom modes switch the main agent's role instead of spawning an isolated subagent. They still belong here, because they bundle a role prompt, tool and path restrictions and handoffs.
- **Typical contents:**
  - The role and when to delegate to it (the description).
  - Instructions.
  - Allowed tools and paths, and the model.
  - Permission mode, MCP servers, preloaded skills, hooks, memory and isolation.
  - Domain knowledge and common mistakes.
  - Output format.
  - Handoffs to the next agent.
- **When written:** When a phase or domain needs its own context, often after repeated failures in that domain.
- **Author:** Human, or generated by AI and then reviewed.
- **Core or optional:** Optional. When work is split across role-specific agents.
- **Lifespan:** Living configuration.
- **Also called / tool examples:** `.claude/agents/*.md`, `*.agent.md`, chat modes (the former VS Code name), custom modes (Roo), roles.
  - Claude Code: `.claude/agents/*.md`.
  - VS Code: `.github/agents/*.agent.md` with handoffs.
  - Copilot coding agent: Markdown custom agent profiles.
  - Roo: `.roomodes`.
  - BMAD: role agents (v4 Analyst, PM, Architect, SM, Dev, QA). Current BMAD delivers these roles as skills.
  - Superpowers subagent-driven development: implementer, spec-compliance reviewer and code-quality reviewer.
  - MetaGPT: roles defined in framework code. Illustration only.
- **Sources:** [Claude Code subagents](https://code.claude.com/docs/en/sub-agents) · [VS Code custom agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents) · [Copilot coding agent](https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results) · [Roo custom modes](https://roocodeinc.github.io/Roo-Code/features/custom-modes) · [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) · [Superpowers subagent-driven development](https://www.skills.sh/obra/superpowers/subagent-driven-development) · [arXiv 2602.20478](https://arxiv.org/html/2602.20478) · [arXiv 2308.00352 (MetaGPT)](https://arxiv.org/html/2308.00352v7)

### 19. Agent environment setup and tool configuration
- **Phase:** Context (setup). It is written before feature work and read at the start of every session.
- **Purpose:** The executable or declarative setup that lets every session build, run and test the software, plus the repository-level declaration of which tools and MCP servers are available. Build commands written as prose belong to #1, permissions to #15, and the tool list for each role to #18.
- **Typical contents:**
  - A bootstrap script (install dependencies, start the dev server, run a smoke test).
  - Setup steps for cloud agents.
  - MCP server and tool declarations (names, transports, URLs, scope), kept as a file or as a repository setting.

  Tool descriptions come from the MCP server itself, unless the team writes its own tools.
- **When written:** When agents first run the project. Updated when the setup or tools change.
- **Author:** Human, or generated by a CLI (for example `claude mcp add`). In some long-running harnesses, an initialiser agent writes it.
- **Core or optional:** Optional. Worth having when agents run unattended or in cloud sandboxes, or need external tools.
- **Lifespan:** Living.
- **Also called / tool examples:** init.sh, copilot-setup-steps.yml, .mcp.json, environment.json, dev bootstrap.
  - Anthropic long-running harness: `init.sh`.
  - Copilot coding agent: `copilot-setup-steps.yml`, with MCP configured in repository settings.
  - Claude Code: a project-scope `.mcp.json`, checked into version control.
  - Cursor background agents: `.cursor/environment.json`.
- **Sources:** [Anthropic: long-running harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) · [Copilot coding agent](https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results) · [Claude Code MCP](https://code.claude.com/docs/en/mcp) · [Cursor background agents](https://docs.cursor.com/background-agent)

### 20. Agent context evaluation suite
- **Phase:** Context (when agent-facing documents are written) and Maintenance (when they, the model or the agent change).
- **Purpose:** Tests the agent-facing documents themselves (#1, #7, #17, #18 and hooks), not the software product. It shows:
  - whether a document actually changes the agent's behaviour compared with a baseline or the previous version;
  - whether a skill triggers when it should and not when it shouldn't;
  - whether behaviour regresses when the instructions, the model or the agent change.

  It also exposes guidance the model no longer needs, so the context can be cut. A skill's own evals may sit in the skill folder, but this type covers all agent-facing documents.
- **Typical contents:**
  - A set of representative tasks: about 3 per skill, up to 20–50 real tasks per repository (a guideline).
  - For each task: the prompt, input files, a pinned starting commit, the expected behaviour, and checks. Checks are deterministic where possible (build, lint, tests, files, trace contents, diff stays in scope); rubric or LLM-as-judge assertions cover fuzzy qualities.
  - Trigger cases for skills, including near-misses.
  - The configurations compared, and stored results (pass rate, tokens, time).
  - A runner script the team builds itself (Anthropic has no built-in runner) and rubric schemas.
- **When written:** Before or while drafting an instructions file or skill (evaluation-driven development). Rerun on every change to these documents (as a CI gate and nightly), on model upgrades and on agent switches. Add a case after every real failure.
- **Author:** Humans with AI help. The AI drafts prompts and assertions; humans pick the real tasks, approve the expected behaviour and calibrate any LLM judge.
- **Core or optional:** Optional. Worth having for non-trivial instructions, shared skills, or multiple models or agents. Anthropic's skill checklist asks for at least three evaluations before a skill is shared. Among SDD tools, only Tessl promotes this artifact explicitly.
- **Lifespan:** Kept and versioned in the repo (for example `evals/`). Cases grow as failures are found, and results are kept as baselines.
- **Also called / tool examples:** skill evals, context evals, evals/evals.json, trigger evals.
  - Anthropic skill best practices: an evaluation JSON format (illustrative, not a standard runner format).
  - Anthropic skill-creator: `evals/evals.json`, `benchmark.json` and `benchmark.md`, and 20 should-trigger and should-not-trigger queries.
  - OpenAI: `evals/*.prompts.csv` with `codex exec --json` traces.
  - Claude Academy: CI evals that run on changes to CLAUDE.md, `.claude/**` or hooks.
  - Vercel Next.js 16 evals: baseline 53%, skill by default 53%, skill with explicit instructions 79%, AGENTS.md docs index 100%.
  - Tessl: "If context is the new code, evals are its tests".
  - Research analogue: AGENTbench (ETH Zurich and LogicStar.ai; 138 tasks from 12 repositories).
- **Sources:** [Anthropic skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) · [skill-creator SKILL.md](https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/SKILL.md) · [OpenAI: testing skills with evals](https://developers.openai.com/blog/eval-skills) · [Claude Academy: evals in CI](https://academy.claude.com/courses/ai-native-sdlc-playbook/continuous-evals-in-ci) · [Vercel: AGENTS.md vs skills](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) · [Tessl evals pattern](https://tessl.io/patterns/agentic-development-workflow/evals/) · [arXiv 2602.11988 (AGENTbench)](https://arxiv.org/html/2602.11988v1)

---

## 2. Intent / Requirements

### 21. Idea exploration and assessment
- **Phase:** Intent (ideation, before requirements).
- **Purpose:** Explores an idea before committing to it, and records whether to build it and in what shape. Market and domain evidence belongs to #4. Once the decision is go, a PRFAQ or brief can feed into, or become, the product brief that precedes #22.
- **Typical contents:**
  - Brainstorming notes.
  - Feasibility, build-versus-buy and competitive notes.
  - A constraint register or RAID log (overlapping #40).
  - A go, needs-clarification or kill decision, with reasons.
  - Optionally a PRFAQ (working-backwards press release and FAQ).
- **When written:** Before any requirements are written, for a new product or an uncertain initiative.
- **Author:** The AI facilitates; the human drives the content and decides.
- **Core or optional:** Optional.
- **Lifespan:** Per initiative. Throwaway, or kept as a record of the decision.
- **Also called / tool examples:** brainstorm.html, brainstorm-<topic>.md (optional), forge-report.html, forge-<slug>.md, PRFAQ, problem.md, decision.md, feasibility-assessment.md, build-vs-buy.md, intent-statement.md, initiative-brief.md.
  - BMAD: `bmad-brainstorming` and `bmad-forge-idea` (under "Explore and Validate an Idea"). `bmad-prfaq` sits under requirements, as an alternative to the brief that feeds the PRD.
  - Spec Kit assess extension: bundled and opt-in (`specify extension add assess`), with the steps intake, research, define, shape and decide. The decide step requires `problem.md`, and a go verdict hands off to `/speckit-specify`.
  - AI-DLC conditional Ideation stages: 1.1 intent capture, 1.2 market research (`competitive-analysis.md`, `build-vs-buy.md`), 1.3 feasibility (`feasibility-assessment.md`, `constraint-register.md`, `raid-log.md`) and 1.7 `initiative-brief.md`.
- **Sources:** [BMAD skills and agents](https://docs.bmad-method.org/reference/skills-and-agents/) · [BMAD: define requirements](https://docs.bmad-method.org/plan/define-requirements-and-a-specification/) · [Spec Kit](https://github.com/github/spec-kit) · [Spec Kit README (assess extension)](https://raw.githubusercontent.com/github/spec-kit/cb610277fdea781fcfa83d20522c2db37c94068d/README.md) · [AI-DLC artifacts](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/14-artifacts-reference.md)

### 22. Product requirements document (PRD)
- **Purpose:** Product-level requirements for a whole product or a large initiative. The architecture follows it, and epics and stories are derived from it. It is needed when several stakeholders must agree on the product or several epics must stay aligned. Smaller work goes straight from a brief or issue to feature specs. A "PRD" scoped to one feature is classed as #23.
- **Typical contents:**
  - A recap of the vision, and the goals.
  - Capabilities.
  - Functional requirements with stable IDs.
  - Non-functional requirements.
  - Success metrics.
  - UX considerations.
  - Scope (v1 or v2) and what is out of scope.
  - Optionally, a competitive analysis and open questions.

  Technical choices are kept out (BMAD v6 puts them in `addendum.md`). Breaking the PRD into epics belongs to #37. Forerunners: the SRS (IEEE 830) and the ISO/IEC/IEEE 29148 stakeholder and software requirements specifications.
- **When written:** After the product brief or PRFAQ, and before the architecture and the breakdown into epics. Updated as the initiative evolves; BMAD v6 has an update mode that reconciles the PRD with change signals.
- **Author:** A PM agent or skill drafts it through dialogue, or a human writes it. A human PM or PO approves it.
- **Core or optional:** Optional. For greenfield products or initiatives with several epics.
- **Lifespan:** Living for the product or initiative.
- **Also called / tool examples:** PRD, prd.md, prd-<slug>.md, REQUIREMENTS.md, SRS, FRD.
  - BMAD v6: `bmad-prd` writes `prd-<slug>.md` and `addendum.md`. BMAD v4 used `prd.md`, written by the PM agent.
  - GSD: `.planning/REQUIREMENTS.md`, with v1/v2 scoped requirements and phase traceability.
  - Task Master: `.taskmaster/docs/prd.txt` (`scripts/prd.txt` in older versions), parsed into `tasks.json`.
  - Traycer: a PRD for larger efforts.
  - MetaGPT: a PRD written by its Product Manager agent.
- **Sources:** [BMAD v4 user guide](https://github.com/bmad-code-org/BMAD-METHOD/blob/v4.44.3/docs/user-guide.md) · [BMAD: define requirements](https://docs.bmad-method.org/plan/define-requirements-and-a-specification/) · [GSD docs](https://mintlify.wiki/gsd-build/get-shit-done) · [Task Master PRD quick start](https://docs.task-master.dev/getting-started/quick-start/prd-quick.md) · [Task Master setup](https://docs.task-master.dev/docs/cursor-setup) · [Traycer](https://traycer.ai/blog/build-with-intent-ship-with-confidence) · [Spec Kit spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) · [ISO/IEC/IEEE 29148](https://webstore.iec.ch/publication/64315) · [arXiv 2602.00180](https://arxiv.org/html/2602.00180) · [arXiv 2508.09648](https://arxiv.org/html/2508.09648v1) · [arXiv 2308.00352 (MetaGPT)](https://arxiv.org/html/2308.00352v7) · [arXiv 2404.17842](https://arxiv.org/html/2404.17842v1)

### 23. Feature specification
- **Purpose:** The central SDD document. It says what one feature or change must do and why; design, tasks and tests are derived from it. It should leave out how the feature is built, but in practice it often mixes that in: about 78% of spec files in public repositories contain implementation detail (arXiv 2608.25202). Acceptance criteria written inside the spec belong here. Runnable validation guides belong to #48, test code to #49, and long-lived behaviour to #54.
- **Typical contents:**
  - Prioritised user stories.
  - Acceptance criteria in Given/When/Then, EARS ("WHEN … THE SYSTEM SHALL"), or RFC 2119 SHALL/MUST with scenarios.
  - Numbered functional requirements.
  - Key entities.
  - Edge cases.
  - Measurable success criteria.
  - Assumptions.
  - `[NEEDS CLARIFICATION]` markers.
  - Often also non-functional constraints and non-goals or out-of-scope items (from Osmani, Kiro and observed practice; Spec Kit's template has no dedicated section for them).

  Use cases are an alternative notation. In change-based workflows the spec is written as a delta (ADDED, MODIFIED or REMOVED requirements) against #54.
- **When written:** For each feature or change (specs are more often written per change request than per feature), after #3 or #22 and before design. Reviewed and approved at a gate. For a small change a full spec can be excessive (Fowler saw a small bug turn into 4 user stories and 16 acceptance criteria); use #25 instead.
- **Author:** Drafted by AI from a human prompt, brief or interview; reviewed and approved by a human.
- **Core or optional:** Core.
- **Lifespan:** Per feature or change by default (spec-first; in practice Kiro and Spec Kit work this way). It is kept only by being merged into #54 (spec-anchored or spec-as-source). A third pattern is observed: an accumulated record, with a new spec kept for each change and never merged, most of them with a single commit.
- **Also called / tool examples:** spec.md, SPEC.md, requirements.md, shape.md, functional spec, delta spec, EARS requirements.
  - Spec Kit: `specs/<branch>/spec.md`.
  - Kiro: `.kiro/specs/<f>/requirements.md` (EARS). Defects use a separate `bugfix.md`.
  - OpenSpec: the delta spec `changes/<name>/specs/<capability>/spec.md`. The `proposal.md` beside it is #24.
  - cc-sdd and spec-workflow MCP: `requirements.md`.
  - Conductor: `tracks/<id>/spec.md`.
  - Agent OS: `specs/<x>/shape.md`.
  - Claude Code: an interview, then `SPEC.md`.
  - Tessl: `*.spec.md`.
- **Sources:** [Spec Kit spec template](https://github.com/github/spec-kit/blob/main/templates/spec-template.md) · [Kiro feature specs](https://kiro.dev/docs/specs/feature-specs/) · [Kiro specs](https://kiro.dev/docs/specs/) · [OpenSpec concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md) · [OpenSpec glossary](https://openspec.dev/docs/glossary) · [Conductor](https://github.com/gemini-cli-extensions/conductor) · [Agent OS shape spec](https://buildermethods.com/agent-os/shape-spec) · [Claude Code best practices](https://code.claude.com/docs/en/best-practices) · [Fowler: SDD tools](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) · [EARS](https://alistairmavin.com/ears/) · [Osmani](https://addyosmani.com/blog/good-spec/) · [Grove: specifications are the new code](https://www.ai.engineer/talks/8rABwKRsec4-specifications-are-the-new-code) · [Marmelab](https://marmelab.com/blog/2025/11/12/spec-driven-development-waterfall-strikes-back.html) · [arXiv 2608.25202](https://arxiv.org/html/2608.25202) · [arXiv 2602.00180](https://arxiv.org/html/2602.00180) · [arXiv 2511.09231 (use cases)](https://arxiv.org/html/2511.09231v2) · [arXiv 2610.07534 (spec quality, supporting)](https://arxiv.org/abs/2610.07534)

### 24. Change proposal
- **Purpose:** For a change to an existing system, states why the change is needed, what changes and what is in or out of scope. It is written first; the scope is agreed with it, and the other change artifacts derive from it. In tools that use change folders, it is the entry point of the bundle for that change.
- **Typical contents:**
  - Why, or the intent.
  - What changes.
  - New and modified capabilities (which name the delta specs to write).
  - Scope in and out.
  - A high-level approach.
  - Optionally, the impact on code, APIs and users.

  The delta specs, design and tasks sit beside it in the change folder and depend on it.
- **When written:** At the start of each change in brownfield, change-based workflows, or when re-scoping mid-stream. In OpenSpec's default flow, `/opsx:propose` generates the proposal, delta specs, design and tasks in one step, and a human reviews the whole set. The proposal is reviewed on its own only in the expanded, step-by-step flow.
- **Author:** Drafted by AI from human intent; reviewed by a human.
- **Core or optional:** Optional. For change-based brownfield workflows.
- **Lifespan:** Per change. Updated if the intent or scope shifts, then archived read-only with its change folder under a date prefix. Its deltas merge into #54; the proposal itself does not.
- **Also called / tool examples:** proposal.md, change request, sprint change proposal; RFC as a loose analogy. In the OpenSpec glossary, "change proposal" names the whole change folder.
  - OpenSpec: `openspec/changes/<name>/proposal.md`, archived to `changes/archive/`.
  - BMAD: `sprint-change-proposal-{date}.md` from the correct-course workflow, a mid-course impact analysis with before/after edits.
  - Precedent outside AI: Oxide RFDs, which are general design discussions and closer to #35 and #29.
- **Sources:** [OpenSpec](https://github.com/Fission-AI/OpenSpec) · [OpenSpec concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md) · [OpenSpec glossary](https://openspec.dev/docs/glossary) · [BMAD correct-course](https://www.skills.sh/bmad-code-org/bmad-method/bmad-correct-course) · [Oxide RFD 1 (precedent)](https://rfd.shared.oxide.computer/rfd/0001)

### 25. Bug specification
- **Purpose:** A lightweight spec for a defect, used instead of a full feature spec. It states the current wrong behaviour, the expected behaviour and the behaviour that must not change, and it drives tests that reproduce the bug.
- **Typical contents:** Current, expected and unchanged behaviour (Kiro's WHEN/THEN sections). Reproduction steps usually come from the human's bug description. A companion design and tasks part holds the root cause, the fix approach and the properties to test. Kiro's property-based tests check that the bug reproduces, that it is fixed, and that nothing regressed.
- **When written:** For each bug, from a report plus inspection of the codebase.
- **Author:** A human reports; the AI analyses and drafts; a human reviews.
- **Core or optional:** Optional. For defect fixes.
- **Lifespan:** Per bug, usually archived with the change. The tests and regression properties persist.
- **Also called / tool examples:** bugfix.md, bug analysis. Bug report and defect report are related precursors, not exact synonyms.
  - Kiro: `bugfix.md` plus a companion `design.md`.
  - Spec Kit: an opt-in bug extension, bundled since v0.9.5, with assess, fix and test/validate steps and one directory per bug. These details were confirmed only through a documentation summary.
  - Spec Kit community extension: `/speckit.bugfix`.
  - spec-workflow MCP: a five-step bug resolution workflow (prompts only; no named files).
- **Sources:** [Kiro bugfix specs](https://kiro.dev/docs/specs/bugfix-specs/) · [Kiro specs](https://kiro.dev/docs/specs/) · [Spec Kit history](https://github.github.com/spec-kit/history.html) · [speckit-bugfix skill](https://skills.sh/pradeepmouli/zod-to-form/speckit-bugfix) · [spec-workflow MCP](https://github.com/Pimzino/spec-workflow-mcp/blob/main/docs/WORKFLOW.md) · [Fowler: SDD tools (why full specs are overkill for bugs)](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)

### 26. Clarification record
- **Phase:** Mainly Intent / Requirements, but also any later phase.
- **Purpose:** Records the ambiguities found and the human's answers, so that later phases and agents do not guess. It covers both questions raised while specifying and decision requests the agent raises during implementation. Answers that amount to significant decisions also go into #35, and blocking escalations also appear as blockers in #42.
- **Typical contents:**
  - Each question, with options where they were offered.
  - The answer.
  - The date or session.
  - Optionally, who must answer.
  - Unresolved `[NEEDS CLARIFICATION]` markers.

  Spec Kit allows at most 5 questions per session and records them as "Q → A" bullets. AI-DLC records options A–E plus "Other" with `[Answer]:` tags.
- **When written:** After the spec is drafted and before planning, and whenever an agent hits an ambiguity.
- **Author:** The AI asks, the human answers, and the AI records.
- **Core or optional:** Optional. Often a section of the spec.
- **Lifespan:** Per feature, and kept. Spec Kit keeps it inside `spec.md` as dated sessions. AI-DLC keeps one file per stage, committed, and replaces it only if the stage is redone.
- **Also called / tool examples:** Clarifications section, open questions, questions file, Consultation Request Pack and resolution, CONTEXT.md (a partial match).
  - Spec Kit: `/speckit.clarify`.
  - AI-DLC: `{stage-name}-questions.md` (for example `intent-capture-questions.md`, `code-generation-questions.md`).
  - GSD: `XX-CONTEXT.md`, a record of user decisions from the discuss phase, checked against plans by a coverage gate.
  - SASE: the agent raises a Consultation Request Pack (CRP), and the human answers with a version-controlled resolution.
- **Sources:** [Spec Kit agentic SDD](https://github.github.io/spec-kit/reference/agentic-sdd.html) · [Spec Kit spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) · [Spec Kit clarify template](https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md) · [Garg: context anchoring](https://martinfowler.com/articles/reduce-friction-ai/context-anchoring.html) · [AI-DLC artifacts](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/14-artifacts-reference.md) · [GSD architecture](https://github.com/open-gsd/gsd-core/blob/main/docs/ARCHITECTURE.md) · [arXiv 2509.06216 (SASE)](https://arxiv.org/html/2509.06216v2)

---

## 3. Design

### 27. Research notes
- **Phase:** Design (Phase 0, before the technical design). Also used at project inception.
- **Purpose:** Resolves technical and codebase unknowns before design: how the existing code works for this task, which library or approach to choose, and which pitfalls to avoid. It is a high-leverage review point, because errors in research multiply into bad code. Market research and the decision whether to build belong to #4 and #21. Durable decisions found here are promoted to #35.
- **Typical contents:**
  - Relevant files and data flow.
  - For each unknown: Decision, Rationale and Alternatives considered (Spec Kit's format).
  - Compatibility, performance and security findings.
  - Ecosystem pitfalls.
  - A subagent's findings, returned as a short report.

  Research tasks come from unknowns, dependencies, integrations and technology choices.
- **When written:** At project inception (before the requirements and roadmap) and/or at the start of each feature's design, whenever there are unknowns. It is a mandatory step of Spec Kit's `/plan`, where an unresolved clarification is a gate error. In cc-sdd it is conditional.
- **Author:** AI (research agents or subagents), steered and reviewed by a human.
- **Core or optional:** Optional. Some tools make it a mandatory step.
- **Lifespan:** Per feature and kept in the spec folder (Spec Kit; cc-sdd updates it in place). GSD reloads its research files in later planning. Subagent summaries are throwaway.
- **Also called / tool examples:** research.md, RESEARCH.md, spike, codebase research.
  - Spec Kit: `specs/<f>/research.md`.
  - cc-sdd: `research.md`.
  - BMAD: `bmad-deep-recon`, technical part only.
  - GSD: `.planning/research/` (STACK, FEATURES, ARCHITECTURE, PITFALLS and SUMMARY, written by four parallel researchers).
  - HumanLayer: research documents in `thoughts/`.
  - Claude Code: subagent investigations.
- **Sources:** [Spec Kit plan template](https://github.com/github/spec-kit/blob/main/templates/commands/plan.md) · [cc-sdd commands](https://github.com/gotalab/cc-sdd/blob/main/docs/guides/command-reference.md) · [BMAD skills](https://docs.bmad-method.org/reference/skills-and-agents/) · [GSD planning directory](https://www.mintlify.com/gsd-build/get-shit-done/reference/planning-directory) · [HumanLayer ACE](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md) · [Anthropic: context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) · [Claude Code workflows](https://code.claude.com/docs/en/common-workflows)

### 28. System architecture description
- **Purpose:** Describes the structure of the whole system, or of a large epic or subsystem, and its cross-cutting decisions, so that many features and agents stay consistent. It summarises accepted decisions and links to them; the rationale for each lives in #35. The stack, folder tree and full data shapes are only starting points, which the code takes over once it exists (#5, #6, #30).
- **Typical contents:**
  - Context, containers and building blocks.
  - Boundaries, and who owns which state and data.
  - Integration and data patterns.
  - Runtime and deployment views.
  - Security concepts and design patterns.

  Some tools hold only the decisions that would conflict if features chose them independently, each with a stable ID (BMAD's "spine"). An epic-level spine inherits its parent's decisions and records only what the parent left open.
- **When written:** After #22 or #3 and before feature design. Updated when the structure changes.
- **Author:** An architect agent or skill drafts it. BMAD offers a coaching mode, where the human chooses among weighed alternatives, and a fast path that drafts everything with `[ASSUMPTION]` tags. A human architect decides.
- **Core or optional:** Optional. For systems with several components, or when many features and agents share structural decisions.
- **Lifespan:** Living.
- **Also called / tool examples:** architecture.md, architecture spine, software architecture document. arc42 and C4 are classic formats, not AI tools.
  - BMAD: `docs/architecture.md` (v4) and the `bmad-architecture` spine. In v4, the PO shards it into coding standards, tech stack and project structure files.
  - Memory banks: `architecture.md` (per Fowler).
  - Cline: `systemPatterns.md`, which describes existing code and so partly overlaps #6.
  - MetaGPT: a one-shot system design per project. Illustration only; closer to #29 and #31.
- **Sources:** [BMAD v4 user guide](https://github.com/bmad-code-org/BMAD-METHOD/blob/v4.44.3/docs/user-guide.md) · [BMAD: design UX and architecture](https://docs.bmad-method.org/plan/design-ux-and-architecture/) · [arc42](https://docs.arc42.org/home/) · [C4 model](https://c4model.com/) · [Cline Memory Bank](https://docs.cline.bot/prompting/cline-memory-bank) · [Fowler: SDD tools (architecture.md as a memory-bank file)](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) · [arXiv 2308.00352 (MetaGPT)](https://arxiv.org/html/2308.00352v7)

### 29. Feature technical design
- **Purpose:** Says how one feature or change will be built. It maps requirements to technical decisions and, before tasks are written, is checked against the architecture and, where one exists, the constitution.
- **Typical contents:**
  - Approach and components.
  - Interactions and sequence diagrams.
  - Data flow.
  - Affected files and a file-structure plan.
  - Error handling.
  - Often a testing strategy, migration notes and alternatives with their rationale.

  It points to #30 and #31 rather than containing them. Spec Kit adds a constitution check (the Phase -1 gates), a Complexity Tracking section that justifies exceptions, and an instruction to put bulky detail in an `implementation-details/` annex.
- **When written:** Per feature, usually after the spec is approved and before tasks. Kiro allows a design-first workflow, and in OpenSpec the design can be written in parallel with the specs. Updated when the spec changes, or when the approach turns out to be unworkable.
- **Author:** Generated by AI from the spec, the codebase and the human's technical constraints; approved by a human. In cc-sdd, the review step checks for boundary violations.
- **Core or optional:** Core in most workflows. For small changes it can be a few lines, merged into the plan, or skipped (OpenSpec makes it optional).
- **Lifespan:** Per feature or change. Kept in the feature folder (Spec Kit) or archived with the change (OpenSpec). Rarely maintained after delivery; the living spec is what persists.
- **Also called / tool examples:** design.md, technical plan, tech spec, design doc, HLD/LLD. Spec Kit's `plan.md` is this type; its `tasks.md` is #38.
  - Kiro: `design.md`.
  - Spec Kit: `plan.md`, with `research.md`, `data-model.md`, `contracts/` and `quickstart.md` beside it.
  - OpenSpec: `changes/<name>/design.md`.
  - cc-sdd: `design.md`, with Mermaid diagrams and a File Structure Plan.
  - spec-workflow MCP: `design.md`.
- **Sources:** [Kiro specs](https://kiro.dev/docs/specs/) · [Kiro feature specs](https://kiro.dev/docs/specs/feature-specs/) · [Spec Kit spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) · [OpenSpec concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md) · [cc-sdd](https://github.com/gotalab/cc-sdd) · [spec-workflow MCP](https://github.com/Pimzino/spec-workflow-mcp/blob/main/docs/WORKFLOW.md) · [Design docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/) · [GitHub blog: Spec Kit](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/) · [Marmelab](https://marmelab.com/blog/2025/11/12/spec-driven-development-waterfall-strikes-back.html) · [arXiv 2605.30314 (SpecBench)](https://arxiv.org/abs/2605.30314)

### 30. Data model
- **Purpose:** States the entities, fields, relationships, validation rules and state transitions explicitly, so that the agent does not have to infer the schema. Payload schemas that are exposed through interfaces live in #31 and are referenced from here.
- **Typical contents:** Entities with attributes and types, relationships, validation rules, and state transitions where they apply. Invariants, migration notes and an ERD are optional extensions.
- **When written:** During design, extracted from the spec's key entities (Spec Kit plan, Phase 1).
- **Author:** Generated by AI from the spec; reviewed by a human.
- **Core or optional:** Optional. When the feature creates or changes persistent data or domain entities.
- **Lifespan:** Per feature, or living (a system-level schema, or spec-as-source).
- **Also called / tool examples:** data-model.md, schema, entities.md, domain model, ERD.
  - Spec Kit: `specs/<f>/data-model.md`.
  - Kiro: data models inside `design.md`, per community templates and practitioner reports.
  - AI-DLC: `entities.md`, produced per unit in Functional Design. Its `rules.md` holds business rules and only partly overlaps.
  - MetaGPT: data structures.
- **Sources:** [Spec Kit plan template](https://github.com/github/spec-kit/blob/main/templates/commands/plan.md) · [Spec Kit spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) · [InfoQ: SDD](https://infoq.com/articles/spec-driven-development) · [AI-DLC artifacts](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/14-artifacts-reference.md)

### 31. Interface contracts
- **Purpose:** Precise, preferably machine-readable definitions of the interfaces the system owns or exposes, plus contracts agreed between its own components (consumer-driven contracts, agreed event schemas). They are written before the code. They allow parallel work, generated stubs and contract tests, and they reduce invented endpoints, since without a spec the AI has to infer behaviour.
  - Third-party APIs the system only consumes belong to #12.
  - Domain entities and invariants belong to #30.
  - The contract tests themselves belong to #49.
- **Typical contents:**
  - A format suited to the project type: OpenAPI, AsyncAPI, GraphQL SDL, Protocol Buffers, JSON Schema, public library APIs, CLI command schemas, parser grammars or UI contracts.
  - Behavioural guarantees.
  - Versioning and compatibility rules.
- **When written:** During design, before tests and code (first of all, in API-first work). Updated with each change to an interface.
- **Author:** The agent running the plan step drafts them and a human reviews; in API-first work, a human writes them.
- **Core or optional:** Optional. Spec Kit says to skip them for purely internal projects (build scripts, one-off tools).
- **Lifespan:** Living and versioned across compatibility windows. Contracts written for one feature are often promoted to living ones.
- **Also called / tool examples:** contracts/, API spec, OpenAPI, AsyncAPI, GraphQL SDL, Protobuf, event schemas.
  - Spec Kit: `specs/<f>/contracts/`.
  - Tessl: the API section of a spec (a component's public API; a weak, unit-level example).
  - Kiro: a steering reference such as `#[[file:api/openapi.yaml]]`.
  - Specmatic: contract tests.
  - AI-DLC: `contract-summary.md`.
- **Sources:** [Spec Kit plan template](https://github.com/github/spec-kit/blob/main/templates/commands/plan.md) · [Spec Kit spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) · [AsyncAPI document](https://www.asyncapi.com/docs/concepts/asyncapi-document) · [Kinde: spec-driven APIs](https://kinde.com/learn/ai-for-software-engineering/using-ai-for-apis/spec-driven-apis-designing-and-building-services-the-ai-friendly-way/) · [Tessl launch](https://tessl.io/blog/tessl-launches-spec-driven-framework-and-registry) · [fast.io: Cline and OpenAPI](https://fast.io/resources/cline-openapi/) · [arXiv 2602.00180](https://arxiv.org/html/2602.00180)

### 32. UX/UI specification
- **Purpose:** Defines how the interface of a feature looks and behaves, and gives the agent visual targets to compare its output against. The project-wide visual identity and tokens belong to #8.
- **Typical contents:**
  - Information architecture, flows, screen states and interactions.
  - Accessibility requirements or a checklist.
  - Wireframes, mockups and screenshots.
  - References to design tokens and components.
- **When written:** During design, before UI tasks. Mockups are made for each feature.
- **Author:** The human decides the design. The AI facilitates and records: BMAD's facilitator records the human's vision and never proposes colours or directions, and its fast path drafts with `[ASSUMPTION]` tags. Visuals may come from an external design tool.
- **Core or optional:** Optional. When the software has a user interface.
- **Lifespan:** Per feature for mockups and flows. BMAD's DESIGN.md and EXPERIENCE.md are project-level, living, and take precedence over mocks.
- **Also called / tool examples:** front-end-spec.md, EXPERIENCE.md, UI-SPEC.md, visuals/, wireframes, mockups, interaction-spec.md, user-flow.md, accessibility-checklist.md.
  - BMAD `bmad-ux`: DESIGN.md (look) and EXPERIENCE.md (behaviour, information architecture, states, accessibility, flows). BMAD v4 used `front-end-spec.md`.
  - Agent OS: `specs/<x>/visuals/`.
  - GSD: `XX-UI-SPEC.md`, optional, written in the UI phase before planning and checked by a UI auditor.
  - AI-DLC: `wireframes.md` and `user-flow.md` in Ideation; `mockups.md`, `interaction-spec.md` and `accessibility-checklist.md` in Inception.
  - Conductor: the visual-identity part of `product-guidelines.md` (a weak example).
  - Claude Code: a screenshot as a visual target; Figma through MCP.
- **Sources:** [BMAD: design UX and architecture](https://docs.bmad-method.org/plan/design-ux-and-architecture/) · [BMAD v4 user guide](https://github.com/bmad-code-org/BMAD-METHOD/blob/v4.44.3/docs/user-guide.md) · [Agent OS shape spec](https://buildermethods.com/agent-os/shape-spec) · [GSD architecture](https://github.com/open-gsd/gsd-core/blob/main/docs/ARCHITECTURE.md) · [AI-DLC artifacts](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/14-artifacts-reference.md) · [Claude Code best practices](https://code.claude.com/docs/en/best-practices) · [Conductor](https://github.com/gemini-cli-extensions/conductor)

### 33. Security requirements and threat model
- **Purpose:** A system-level model of what must be protected and from whom (assets, trust boundaries, data flows, threats and abuse cases), with the mitigations and security requirements that follow and how each will be verified. Agents read it before designing or implementing. It is the source that the security constraints in specs, data models and contracts trace back to; it does not replace them.
  - Secure-coding rules belong in #7.
  - Non-negotiable security principles belong in #2.
  - Limits on the agent itself belong in #15.
- **Typical contents:**
  - System description and assumptions.
  - Assets, trust boundaries and data flows.
  - Threats (for example STRIDE) and abuse cases.
  - Mitigations.
  - Security requirements mapped to CWE, ASVS or regulations.
  - The security design.
  - How each requirement is validated.
- **When written:** A first draft during intent or early design (OWASP), refined for each feature or unit during design. Updated after new features, incidents, or changes to the architecture or infrastructure.
- **Author:** A human security engineer, with AI helping to identify assets, entry points, abuse cases and threats. Some tools generate the model from code and regenerate it on every change.
- **Core or optional:** Optional. When the software handles sensitive data or authentication, is exposed externally, or is subject to compliance.
- **Lifespan:** Living.
- **Also called / tool examples:** threat model, STRIDE analysis, security requirements, security design.
  - AI-DLC: `security-requirements.md` (stage 3.2) and `security-design.md` (stage 3.3), produced conditionally for each unit. AI-DLC does not use the term "threat model".
  - TMDD (attasec): a YAML threat model in `.tmdd/`; `tmdd feature` updates it and generates an agent prompt that includes the mitigations.
  - Pixee: a threat model generated from the code and regenerated on change.
- **Sources:** [OWASP threat modeling](https://community.owasp.org/Threat_Modeling) · [AI-DLC artifacts](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/14-artifacts-reference.md) · [ENISA AI-assisted development (draft v0.4)](https://www.enisa.europa.eu/sites/default/files/2026-09/ENISA%20Technical%20Advisory-AI-assisted-software-development-draft.pdf) · [Pixee: SDD security](https://www.pixee.ai/blog/spec-driven-development-security) · [TMDD](https://www.producthunt.com/products/attasec/launches/attasec-tmdd) · [CSA agentic secure development lifecycle](https://labs.cloudsecurityalliance.org/agentic/agentic-secure-development-lifecycle-v1/) · [arXiv 2606.00167 (body not verified)](https://arxiv.org/pdf/2606.00167)

### 34. Operations specification and runbooks
- **Phase:** Design (operational non-functional requirements and observability) and Maintenance (deployment, SLO configuration, runbooks).
- **Purpose:** Specifies the operational qualities and procedures of deployed software: performance, observability, deployment, rollback and incident handling. Runbooks are written so that humans or agents can execute them. A runbook packaged as an agent skill is still this type, by its content.
- **Typical contents:**
  - Performance and SLO targets.
  - Observability and monitoring design.
  - Deployment strategy and rollback plan.
  - Step-by-step runbooks, an incident plan and an escalation matrix.

  Load-test plans belong to #41.
- **When written:** During design, for anything that is deployed. Runbooks are maintained during operations.
- **Author:** Drafted by AI and approved by a human at stage gates (AI-DLC). Runbooks are often written by humans for agents to execute.
- **Core or optional:** Optional. When the agent builds or changes deployed services. All AI-DLC Operation artifacts are conditional.
- **Lifespan:** Living.
- **Also called / tool examples:** runbook, playbook, deployment-strategy.md, rollback-runbook.md, slo-config.md.
  - AI-DLC, Construction: 3.2 `observability-requirements.md` and `performance-requirements.md`; 3.3 `observability-design.md` and `monitoring-design.md`.
  - AI-DLC, Operation: 4.1 `deployment-strategy.md`, `cd-config.md` and `rollback-runbook.md`; 4.4 `slo-config.md`, `dashboards.md` and `alarms.md`; 4.5 `runbooks.md`, `incident-plan.md` and `escalation-matrix.md`.
  - Kiro: the steering file `deployment-workflow.md`, which is agent context and overlaps #13.
  - Azure SRE Agent: Markdown runbooks. It is an operations agent, not an SDD tool, so this is an illustration only.
- **Sources:** [AI-DLC artifacts](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/14-artifacts-reference.md) · [Kiro steering](https://kiro.dev/docs/steering/) · [Azure SRE Agent overview](https://learn.microsoft.com/en-us/azure/sre-agent/overview) · [Azure SRE Agent: first value](https://sre.azure.com/docs/get-started/first-value) · [ISO/IEC 25010 (quality attributes only)](https://iso25000.com/en/iso-25000-standards/iso-25010)

### 35. Decision record
- **Phase:** Design. Also written during implementation and replanning, so it is cross-cutting.
- **Purpose:** Keeps the why behind significant decisions, which the code cannot show, across sessions and agents. Agents treat accepted decisions as binding constraints. They should also be told to stop and flag a decision that no longer fits rather than work around it: Davidson saw an agent add layers to keep an obsolete abstraction alive.
  - #28 links to these records.
  - #53 records phase approvals, not technical choices.
  - Durable findings from #27 are promoted here.
- **Typical contents:** Context, options, the decision, consequences, a status (for example proposed, accepted, rejected, deprecated, superseded), and a stable ID or a date. Embedded form: a decision log inside a feature or plan, with rejected alternatives; its significant entries are promoted to standalone records.
- **When written:** Whenever a significant choice is made, during research, design, implementation or replanning.
- **Author:** A human makes or approves significant decisions. The AI drafts records, proposes new ones and logs smaller decisions during implementation. These are sometimes extracted automatically from agent traces.
- **Core or optional:** Optional. When decisions have lasting consequences or the work spans many sessions or agents.
- **Lifespan:** Living. A record is usually superseded rather than rewritten. Some teams edit accepted records in place with a dated "Updated:" line and rely on git for history. Logs for one feature are append-only.
- **Also called / tool examples:** ADR, MADR, decision log, decisions.md, context anchor.
  - MADR: `docs/decisions/NNNN-*.md`.
  - AI-DLC: `decisions.md`.
  - Vercel: adr-skill.
  - Plumb: a JSONL decision log.
  - Embedded forms: the Decision Log section of an OpenAI ExecPlan; Spec Kit's Decision/Rationale/Alternatives entries in `research.md` (mainly #27); BMAD's dated "Decision:" lines in story or epic notes when replanning.
- **Sources:** [Nygard: documenting architecture decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) · [MADR](https://adr.github.io/madr/) · [Davidson: agents love decisions](https://duncandavidson.com/agents-love-decisions) · [Garg: context anchoring](https://martinfowler.com/articles/reduce-friction-ai/context-anchoring.html) · [ADRs with AI assistants](https://blog.thestateofme.com/2025/07/10/using-architecture-decision-records-adrs-with-ai-coding-assistants/) · [Codex ExecPlans](https://developers.openai.com/cookbook/articles/codex_exec_plans) · [Breunig: SDD triangle](https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html) · [arXiv 2403.01709](https://arxiv.org/abs/2403.01709v1) · [BMAD: break work into stories](https://docs.bmad-method.org/plan/break-work-into-stories-and-track-it/)

### 36. Formal and semi-formal behavioural specification
- **Purpose:** Precise, checkable statements of behaviour for code units, used as a test oracle or for mechanical verification. They may be formal (Dafny, code contracts) or semi-formal (Design-by-Contract in natural language, or universal correctness properties). The tests that check them belong to #49. Docstrings that state a contract overlap #45.
- **Typical contents:**
  - Preconditions, postconditions and invariants.
  - Dafny or code-contract annotations.
  - Semi-formal `.spec.md` blocks for each API: a description in natural language, pre- and postconditions, test suggestions, and a tested/untested mark on each condition.
  - Properties of the form "for any X where P holds, Q holds", derived from requirements and linked to requirement IDs.
- **When written:** During design (Kiro derives properties from its EARS requirements in the design document), or generated from natural-language intent alongside the code. The result feeds verification.
- **Author:** Generated by AI from intent or code; optionally refined by a human.
- **Core or optional:** Optional. For correctness-critical code, verified code generation or property-based testing.
- **Lifespan:** Living when embedded in code (Clover). Intermediate in pipelines that turn contracts into tests. Kiro's properties stay in the design.
- **Also called / tool examples:** pre/postconditions, code contracts, Dafny specs, correctness properties.
  - Kiro: correctness properties checked by property-based tests (Kiro states this is not formal verification).
  - Clover: Dafny annotations.
  - nl2postcond.
  - AxDafny.
  - Contract `.spec.md` files used to generate tests (arXiv 2608.17177).
- **Sources:** [Kiro correctness properties](https://kiro.dev/docs/specs/correctness/) · [Kiro property-based testing](https://kiro.dev/blog/property-based-testing/) · [arXiv 2310.17807 (Clover)](https://arxiv.org/abs/2310.17807v4) · [arXiv 2310.01831 (nl2postcond)](https://arxiv.org/abs/2310.01831v2) · [arXiv 2608.17177](https://arxiv.org/html/2608.17177) · [arXiv 2606.32007 (AxDafny)](https://arxiv.org/pdf/2606.32007)

---

## 4. Planning / Tasks

### 37. Roadmap and work breakdown
- **Phase:** Planning, at product or initiative level, before feature specs.
- **Purpose:** Sequences and splits a product or initiative into deliverable chunks (phases, epics, units of work) with priorities and dependencies. It decides which specs get written next and keeps deferred ideas out of the current scope. It can also drive batch or parallel spec generation by dependency wave (cc-sdd `/kiro-spec-batch`).
- **Typical contents:**
  - Phases or milestones mapped to requirements.
  - MVP versus later.
  - Epics, each with its outcome, boundaries and done-when checks.
  - Dependency waves.
  - Coarse phase or epic status only; live per-task status belongs to #42.
  - A list of deferred items; assessing an idea belongs to #21.
- **When written:** After #22 or #3. Updated as work completes or priorities change.
- **Author:** The AI drafts it from the brief or PRD; a PO or PM approves.
- **Core or optional:** Optional. When a product or initiative needs more than one feature spec.
- **Lifespan:** Living for the product or initiative.
- **Also called / tool examples:** roadmap.md, ROADMAP.md, epics, unit-of-work.md, product backlog, milestones.
  - Agent OS: `product/roadmap.md`.
  - cc-sdd: `roadmap.md`.
  - GSD: `.planning/ROADMAP.md`, with `todos/` and `seeds/` as idea stores for deferred items.
  - BMAD: epic files with `tickets/tickets.toml` (outcome, boundaries, done-when, refined flag), plus a `backlog/` folder.
  - AI-DLC: `unit-of-work.md`, `unit-of-work-dependency.md` and `intent-backlog.md` (stage 1.4; named only, contents not described), and `bolt-plan.md` and `risk-and-sequencing-rationale.md` (stage 2.9).
  - Conductor: `tracks.md`. Borderline: it is a registry of tracks with their status, closer to #42.
- **Sources:** [Agent OS product planning](https://buildermethods.com/agent-os/product-planning) · [cc-sdd](https://github.com/gotalab/cc-sdd) · [GSD docs](https://mintlify.wiki/gsd-build/get-shit-done) · [GSD architecture](https://github.com/open-gsd/gsd-core/blob/main/docs/ARCHITECTURE.md) · [BMAD: break work into stories](https://docs.bmad-method.org/plan/break-work-into-stories-and-track-it/) · [BMAD v4 user guide](https://github.com/bmad-code-org/BMAD-METHOD/blob/v4.44.3/docs/user-guide.md) · [Conductor](https://github.com/gemini-cli-extensions/conductor) · [AI-DLC artifacts](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/14-artifacts-reference.md) · [Scrum Guide](https://scrumguides.org/scrum-guide.html)

### 38. Implementation plan and task list
- **Purpose:** Turns the spec and the technical design (or the spec alone, for small changes) into an ordered set of small, checkable steps that the agent executes and ticks off. The persisted plan or task list is the main point to review before code is written.
- **Typical contents:**
  - Phases and tasks traced to user stories or requirement IDs (Spec Kit uses `[US1]` labels).
  - Dependencies and `[P]` markers for parallel tasks.
  - Files to touch.
  - Test tasks: optional, but when included they come first and must fail before implementation.
  - How each step is verified.
  - Status checkboxes.

  Variants:
  - A single-session plan from plan mode.
  - A living execution plan (OpenAI's ExecPlan). It adds Purpose, Context, Validation and Interfaces sections, and it embeds Progress, Surprises & Discoveries, a Decision Log, and Outcomes & Retrospective; see #42, #44, #35 and #56.
  - The lightest variant: the agent's own in-session to-do list, which is ephemeral and rarely reviewed.
- **When written:** After design, or directly after the spec for small changes. The agent updates the status during implementation.
- **Author:** Generated by AI and reviewed or edited by a human; the AI updates the status.
- **Core or optional:** Core. The plan can be skipped for changes you can describe in one sentence.
- **Lifespan:** Plan-mode plans are usually disposable: one study found 85 plan files in 10 of 36,710 repositories, mostly committed once (arXiv 2608.04661). Task lists managed by a tool are kept in the spec folder (Spec Kit, Kiro) or archived with the change (OpenSpec). ExecPlans are kept until the work is done.
- **Also called / tool examples:** tasks.md, PLAN.md, todo.md, fix_plan.md, prompt_plan.md, ExecPlan, implementation checklist. "plan.md" means this type only where it really is a list of steps.
  - Spec Kit: `tasks.md` with `[P]` markers (its `plan.md` is #29).
  - Kiro: `tasks.md`, executed in waves.
  - OpenSpec: `tasks.md`.
  - cc-sdd: `tasks.md` with `_Boundary:_` and `_Depends:_`.
  - Conductor: `tracks/<id>/plan.md`.
  - GSD: `PLAN.md`.
  - Claude Code and Cursor: plan mode.
  - Codex: ExecPlan.
  - Harper Reed: `prompt_plan.md` and `todo.md`.
  - Kent Beck: a `plan.md` test list.
  - Traycer: phases.
- **Sources:** [Spec Kit spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) · [Kiro specs](https://kiro.dev/docs/specs/) · [OpenSpec concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md) · [cc-sdd](https://github.com/gotalab/cc-sdd) · [Conductor](https://github.com/gemini-cli-extensions/conductor) · [Traycer phases](https://docs.traycer.ai/extension/tasks/phases) · [Claude Code permission modes](https://code.claude.com/docs/en/permission-modes) · [Claude Code best practices](https://code.claude.com/docs/en/best-practices) · [Cursor planning](https://cursor.com/docs/agent/planning) · [Codex ExecPlans](https://developers.openai.com/cookbook/articles/codex_exec_plans) · [Harper Reed](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/) · [HumanLayer ACE](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md) · [Kent Beck](https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes) · [Ronacher: plan mode](https://lucumr.pocoo.org/2025/12/17/what-is-plan-mode/) · [arXiv 2608.04661](https://arxiv.org/html/2608.04661)

### 39. Agent work order
- **Purpose:** A self-contained unit of work handed to an implementing agent, typically run as one agent invocation (for example, one per ticket). It carries just enough requirements, context and validation for that one piece of work.
- **Typical contents:**
  - Goal, scope and non-goals.
  - Acceptance criteria.
  - Curated context (a slice of the spec or architecture).
  - Optionally, the files to change (Copilot does not require exact paths).
  - Known pitfalls.
  - The validation plan.
  - Status.

  BMAD-specific additions: the work order's own task checklist, a change log, a dev agent record (model used, debug log, completion notes, file list), and review notes appended to it.
- **When written:** When work is dispatched: drawn up from the plan or epics, or written directly by a human (an issue or feature request).
- **Author:** A human, or AI working from a human request or the planning docs, then reviewed by a human. Agents may enrich a ticket a human filed. A PRP is generated by AI from a human-written INITIAL.md. A BriefingScript is written by a human "agent coach" and refined with the agent.
- **Core or optional:** Optional. When work is dispatched to agents one unit at a time (story-based flows, issue trackers, background agents).
- **Lifespan:** Per task, kept as a record.
- **Also called / tool examples:** user story file, ticket, GitHub issue, PRP (Product Requirement Prompt), BriefingScript, task brief, work package, context packet.
  - BMAD v4: `docs/stories/*.md`, from `story-tmpl.yaml`.
  - BMAD v6: `story-<slug>-plan.md` for each `tickets.toml` entry, with dated Code Review blocks appended.
  - GitHub Copilot: an issue assigned to Copilot.
  - Context Engineering: INITIAL.md expanded into `PRPs/<feature>.md`.
  - SASE: BriefingScript.
  - Traycer tickets and Spec Kitty work packages (not verified).
  - Spec Kit: `/speckit.taskstoissues` projects tasks into issues (a weak example).
- **Sources:** [BMAD v4 story template](https://github.com/bmad-code-org/BMAD-METHOD/blob/v4.44.3/bmad-core/templates/story-tmpl.yaml) · [BMAD: break work into stories](https://docs.bmad-method.org/plan/break-work-into-stories-and-track-it/) · [Copilot coding agent](https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results) · [Spec Kit agentic SDD](https://github.github.io/spec-kit/reference/agentic-sdd.html) · [Traycer docs](https://docs.traycer.ai/index.md) · [Spec Kitty](https://github.com/Priivacy-ai/spec-kitty) · [Context Engineering intro](https://github.com/coleam00/context-engineering-intro) · [arXiv 2509.06216 (SASE)](https://arxiv.org/html/2509.06216v2) · [Osmani](https://addyosmani.com/blog/good-spec/)

### 40. Risk and technical debt register
- **Phase:** Planning. It also starts in intent (feasibility) and is revisited in maintenance.
- **Purpose:** Lists known risks, assumptions, constraints and technical debt, so that planning, test priorities and later evolution take them into account.
- **Typical contents:**
  - Risks scored by probability and impact, with mitigations.
  - Assumptions, issues and dependencies (RAID; this reading comes from general practice).
  - Constraints.
  - Debt items.

  Related: justified exceptions to gates, recorded in a plan's Complexity Tracking section.
- **When written:** During feasibility and planning. In BMAD, a risk profile is scored for each story before development, and the score feeds test design and the gate. Revisited during maintenance.
- **Author:** Typically drafted by AI (BMAD's QA agent) and reviewed by a human.
- **Core or optional:** Optional. For high-risk work or long-lived systems. Most minimal flows (Spec Kit, OpenSpec, Kiro) have none.
- **Lifespan:** A living register. BMAD's per-story risk profiles are dated snapshots.
- **Also called / tool examples:** RAID log, risk profile, constraint register, risks and technical debt (arc42 §11, classic background), known issues.
  - BMAD v4: `docs/qa/assessments/*-risk-*.md`.
  - AI-DLC: `raid-log.md` and `constraint-register.md` (stage 1.3, conditional) and `risk-and-sequencing-rationale.md` (stage 2.9).
  - Spec Kit: the Complexity Tracking section of `plan.md` (related).
- **Sources:** [BMAD v4 user guide](https://github.com/bmad-code-org/BMAD-METHOD/blob/v4.44.3/docs/user-guide.md) · [arc42 §11](https://docs.arc42.org/section-11/) · [AI-DLC artifacts](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/14-artifacts-reference.md) · [Spec Kit spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md)

### 41. Test plan and strategy
- **Phase:** Planning. It is written during design or planning, although its subject is verification.
- **Purpose:** Decides how correctness will be established: which test levels and kinds verify which requirements, how they are prioritised by risk, and the thresholds for non-functional requirements. In test-first SDD it is written before implementation.
  - The mapping of requirements to tests belongs to #52.
  - Scenarios belong to #48.
  - How to run the tests belongs to #19 or #48.
  - Release and rollback criteria belong to #53 and #34.
  - SLO thresholds should be cross-referenced with #34.
- **Typical contents:**
  - Test levels: contract, integration, end-to-end, unit, property-based, load.
  - Coverage priorities by requirement and risk.
  - Oracles and coverage principles.
  - Required checks.
  - Non-functional thresholds.
- **When written:** During design or planning, before or alongside implementation. Some tools write it per unit during construction.
- **Author:** Drafted by AI (a test-architect or QA agent) and reviewed by a human (QA).
- **Core or optional:** Optional. A separate document when risk is high or testing spans several levels; otherwise the testing-strategy section of #29.
- **Lifespan:** Per feature or epic; a project-level strategy is living. BMAD TEA writes `test-design-architecture.md` and `test-design-qa.md` once per project, after the architecture, and `test-design-epic-N.md` before each epic's stories are built.
- **Also called / tool examples:** testing strategy, test design, validation plan, test plan (IEEE 829 / ISO 29119).
  - Kiro: error handling and testing strategy in `design.md`.
  - BMAD v4: `qa/assessments/*-test-design-*.md`.
  - BMAD TEA: `/bmad-tea-test-design` (formerly prefixed `bmad-testarch-`).
  - AI-DLC: `load-test-plan.md` and `nfr-validation-matrix.md` (stage 4.6, late and conditional).
  - GSD: `XX-VALIDATION.md`, a test-coverage mapping. Tentative; closer to #52.
- **Sources:** [BMAD v4 user guide](https://github.com/bmad-code-org/BMAD-METHOD/blob/v4.44.3/docs/user-guide.md) · [BMAD TEA](https://github.com/bmad-code-org/bmad-method-test-architecture-enterprise) · [BMAD TEA: run test design](https://bmad-code-org.github.io/bmad-method-test-architecture-enterprise/how-to/workflows/run-test-design/) · [Kiro specs](https://kiro.dev/docs/specs/) · [Kiro bugfix specs](https://kiro.dev/docs/specs/bugfix-specs/) · [GSD architecture](https://github.com/open-gsd/gsd-core/blob/main/docs/ARCHITECTURE.md) · [AI-DLC artifacts](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/14-artifacts-reference.md)

---

## 5. Implementation

### 42. Progress and status record
- **Phase:** Implementation. Cross-cutting: it is read and updated in every phase.
- **Purpose:** The persistent, cumulative state of the whole effort across sessions and agents: what is done, what is in progress, blockers, next steps and the status of each item. Agents and dashboards read it at the start of a session.
  - A point-in-time snapshot taken at a pause belongs to #43.
  - The after-the-fact trail belongs to #44 (some tools, such as Anthropic's `claude-progress.txt`, combine the two).
  - Only approval status flags are kept here; the reasons belong to #53.
  - Feature pass flags belong to #48.
- **Typical contents:**
  - Current focus and position.
  - Recent changes.
  - What works and what is left.
  - Known issues and blockers.
  - Next steps.
  - A machine-readable index of specs, stories or tracks, with their phase, approval and completion status.
- **When written:** Read at the start of each session; updated at the end of each session or task.
- **Author:** Maintained by AI or the tool. Humans record approvals (cc-sdd `spec.json`, the spec-workflow dashboard). Cline updates are often triggered by the user.
- **Core or optional:** Optional. When work spans several sessions or agents.
- **Lifespan:** Living for the duration of the effort; changes often.
- **Also called / tool examples:** progress.md, claude-progress.txt, STATE.md, sprint-status.yaml, tracks.md, spec.json, aidlc-state.md.
  - Anthropic harness: `claude-progress.txt`.
  - Cline: `progress.md` (its `activeContext.md` is closer to a handoff).
  - GSD: `.planning/STATE.md`.
  - BMAD: `sprint-status.yaml` from `bmad-sprint-planning`. In current BMAD, `tickets.toml` and the story plan files own the status.
  - Conductor: `tracks.md`.
  - cc-sdd: `spec.json`.
  - spec-workflow MCP: approval status in its dashboard.
  - AI-DLC: `aidlc-state.md`.
- **Sources:** [Anthropic: long-running harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) · [Cline Memory Bank](https://docs.cline.bot/prompting/cline-memory-bank) · [GSD docs](https://mintlify.wiki/gsd-build/get-shit-done) · [GSD core](https://github.com/open-gsd/gsd-core) · [bmad-sprint-planning](https://tessl.io/registry/skills/github/bmad-code-org/BMAD-METHOD/bmad-sprint-planning) · [Conductor](https://github.com/gemini-cli-extensions/conductor) · [cc-sdd commands](https://github.com/gotalab/cc-sdd/blob/main/docs/guides/command-reference.md) · [spec-workflow MCP](https://github.com/Pimzino/spec-workflow-mcp) · [HumanLayer ACE](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md) · [AI-DLC introduction](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/00-introduction.md) · [arXiv 2512.10398 (Confucius)](https://arxiv.org/pdf/2512.10398)

### 43. Session handoff summary
- **Purpose:** A point-in-time snapshot that lets a fresh context window or another agent continue a long task after a pause, a compaction or a hand-off. It is consumed on resume, unlike #42, which is updated continuously.
- **Typical contents:**
  - Phase or position, and completion status.
  - Files changed.
  - Decisions made.
  - Blockers and unresolved bugs.
  - Test commands.
  - Next steps and context notes.
  - A timestamp and the git state.
- **When written:** At a pause, before or at context compaction, or when handing work to another agent.
- **Author:** AI, steered by compaction instructions or a handoff template. A human may trigger it.
- **Core or optional:** Optional. For long tasks that exceed one context window or move between agents.
- **Lifespan:** Throwaway: consumed on resume. GSD commits it as work in progress.
- **Also called / tool examples:** handoff, HANDOFF.md, continue-here.md. A compaction summary is a related mechanism that lives in context rather than in a file.
  - GSD: `/gsd:pause-work` writes `.planning/phases/<phase>/.continue-here.md`, which `/gsd:resume-work` reads.
  - Community session-handoff skills (softaworks, davila7) write a templated handoff document with the git state and a staleness check.
  - Claude Code: `/compact <instructions>` produces an in-context summary, which can be steered through compaction rules in CLAUDE.md.
- **Sources:** [GSD architecture](https://github.com/open-gsd/gsd-core/blob/main/docs/ARCHITECTURE.md) · [GSD pause-work](https://mintlify.wiki/gsd-build/get-shit-done/commands/pause-work) · [softaworks session-handoff](https://skills.sh/softaworks/agent-toolkit/session-handoff) · [davila7 session-handoff](https://claudemarketplaces.com/skills/davila7/claude-code-templates/session-handoff) · [Claude Code best practices (compaction)](https://code.claude.com/docs/en/best-practices) · [Anthropic: context engineering (compaction)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### 44. Implementation log and audit trail
- **Purpose:** An after-the-fact, append-only record of what the agent did for each task or phase: decisions, files changed, commits and commands, and the deviations and gotchas that later tasks need to know about. It is evidence for review and audit, and later executors and verifiers also read it as context (GSD). Distilled, reusable lessons belong to #56.
- **Typical contents:**
  - Summaries per task or phase.
  - Implementation notes.
  - Files changed and commits.
  - Optionally, commands and agent actions (a raw transcript is an optional form).
  - Optional provenance metadata: the spec revision, the model and the gate outcomes.
- **When written:** Appended at the end of each task or phase.
- **Author:** The executor agent (GSD, cc-sdd, AI-DLC's code summary), or the system and its hooks (AI-DLC's `audit/`, spec-workflow's logs).
- **Core or optional:** Optional. For multi-phase work, or when audit or provenance is required.
- **Lifespan:** Kept as history; append-only.
- **Also called / tool examples:** SUMMARY.md, Implementation Notes, code-summary.md, audit log, provenance record.
  - GSD: `XX-YY-SUMMARY.md` (`files_modified`, Task Commits), read by the verifier and by later waves.
  - AI-DLC: `audit/<host>-<clone>.md` shards, which are committed, and `code-summary.md` for each unit.
  - spec-workflow MCP: searchable implementation logs with code statistics.
  - cc-sdd: an `## Implementation Notes` section in `tasks.md` (a weak example).
- **Sources:** [GSD docs](https://mintlify.wiki/gsd-build/get-shit-done) · [GSD architecture](https://github.com/open-gsd/gsd-core/blob/main/docs/ARCHITECTURE.md) · [cc-sdd](https://github.com/gotalab/cc-sdd) · [spec-workflow MCP](https://github.com/Pimzino/spec-workflow-mcp) · [AI-DLC artifacts](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/14-artifacts-reference.md) · [arXiv 2608.20341 (SDAD, provenance as a governance requirement)](https://arxiv.org/html/2608.20341)

### 45. In-code specification and documentation
- **Purpose:** Short specs and notes placed at the code location they govern. Directive comments steer the agent. Anchor notes, which the agent greps for orientation, help it find its way. Prose summaries aid comprehension and review; with natural-language outlines, the code remains the source of truth.
- **Typical contents:**
  - TODO mini-specs for the agent to implement.
  - Aider "AI!" watch-mode comments, which the agent executes and then removes.
  - Anchor comments (AIDEV-NOTE, AIDEV-TODO, AIDEV-QUESTION): the agent greps them first and updates them after each task, and AIDEV-QUESTION raises questions for humans.
  - Natural-language outlines.
  - Docstrings (general practice). A docstring that states a contract overlaps #36.
- **When written:** Directive comments are scaffolded by a human before implementation. Outlines and anchors are generated and kept in sync during implementation.
- **Author:** Humans write the directives. The AI generates outlines and anchors, and a human verifies or edits them.
- **Core or optional:** Optional.
- **Lifespan:** Directive comments are throwaway. Anchors, outlines and docstrings are living.
- **Also called / tool examples:** TODO comments, AI comments, anchor comments, NL outlines, docstrings.
  - Aider: watch mode.
  - AIDEV anchors (Diwank).
  - Google NL Outlines (a research prototype).
- **Sources:** [arXiv 2408.04820 (NL Outlines)](https://arxiv.org/html/2408.04820v1) · [Osmani](https://addyosmani.com/blog/good-spec/) · [Aider watch mode](https://aider.chat/docs/usage/watch.html) · [Field notes: AIDEV anchors](https://hn.svelte.dev/item/44211417)

### 46. Commits and pull request descriptions
- **Phase:** Implementation, extending into verification, because the PR is the unit of review and merge.
- **Purpose:** The change record native to version control (commit messages plus the PR title and body), tied to the diff and ideally linked to specs and tasks. Agents read recent history together with #42 at session start to recover recent work. Commits are revert and recovery points. The PR is where review feedback (#50) reaches the agent. More detailed trails belong to #44, and curated release notes to #57.
- **Typical contents:**
  - Descriptive commit messages.
  - A PR description: summary, linked spec or issue, test evidence.
- **When written:** After each verified step (commit often), and when the change is ready for review.
- **Author:** The AI writes the commit messages and the PR body, and keeps the PR body in sync as changes are pushed (Copilot). A human reviews, approves and merges.
- **Core or optional:** Core. Linking to specs is recommended, not universal.
- **Lifespan:** Commits are permanent and immutable. The PR description is updated until merge, then frozen.
- **Also called / tool examples:** git log, commit messages, PR description, change summary.
  - Anthropic harness: `git log --oneline -20` at session start.
  - Copilot coding agent: keeps the PR updated and takes `@copilot` review comments.
  - Claude Code: the "create a pr" recipe.
  - HumanLayer: commit messages used for intentional compaction.
  - `sdd-pr` skill: generates a PR from the completed spec and the git history.
- **Sources:** [Anthropic: long-running harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) · [Copilot coding agent](https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results) · [Claude Code workflows](https://code.claude.com/docs/en/common-workflows) · [HumanLayer ACE](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md) · [webreference: SDD (spec links in PRs)](https://webreference.com/ai/building/spec-driven-development/) · [sdd-pr skill](https://www.skills.sh/tylerburleigh/claude-sdd-toolkit/sdd-pr) · [arXiv 2601.17581](https://arxiv.org/abs/2601.17581) · [arXiv 2602.09185](https://arxiv.org/html/2602.09185v1)

---

## 6. Verification

### 47. Specification review (checklist and consistency analysis)
- **Purpose:** Verifies the documents themselves before implementation; it is not testing. It asks whether the requirements are complete, clear, consistent and measurable ("unit tests for English"), and whether the spec, plan and tasks agree with each other, with the constitution and with the existing code.
  - Its coverage check maps requirements to tasks only; the full mapping belongs to #52.
  - Checking finished code against the spec belongs to #55 and #51.
  - GO/NO-GO verdicts overlap #53.
- **Typical contents:**
  - Checklist items (CHK###) for each domain (UX, API, security, accessibility) on the quality of the requirements.
  - Findings on duplication, ambiguity, under-specification, conflicts with the constitution, coverage gaps and inconsistencies, each with a severity and a next action.
  - A gap analysis against the existing codebase.
- **When written:** While the spec is being drafted (Spec Kit's specify and clarify steps write `checklists/requirements.md`), and after the spec, design or tasks are drafted, before implementation. Repeated when they change.
- **Author:** The AI generates it. A human ticks the items (the command never does) and decides. Fixes need the user's approval.
- **Core or optional:** Optional. For features where requirement errors are costly, or in tools that build it into the workflow.
- **Lifespan:** Checklists are kept per feature (`specs/<feature>/checklists/<domain>.md`, with new items appended). Analysis reports are often not files at all: Spec Kit's analyze is strictly read-only and prints to the chat.
- **Also called / tool examples:** checklists/<domain>.md, requirements quality checklist, analyze report, validate-gap, validate-design, phase-check.
  - Spec Kit: `/speckit.checklist` and `/speckit.analyze`.
  - Kiro: Analyze Requirements.
  - cc-sdd: `/kiro:validate-gap` and `/kiro:validate-design`, which returns GO, CONDITIONAL GO or NO-GO.
  - AI-DLC: `verification/phase-check-ideation.md` and `phase-check-inception.md`.
- **Sources:** [Spec Kit checklist command](https://github.com/github/spec-kit/blob/main/templates/commands/checklist.md) · [Spec Kit checklist template](https://github.com/github/spec-kit/blob/main/templates/checklist-template.md) · [Spec Kit analyze command](https://github.com/github/spec-kit/blob/main/templates/commands/analyze.md) · [Spec Kit agentic SDD](https://github.github.io/spec-kit/reference/agentic-sdd.html) · [Kiro specs](https://kiro.dev/docs/specs/) · [cc-sdd commands](https://github.com/gotalab/cc-sdd/blob/main/docs/guides/command-reference.md) · [AI-DLC artifacts](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/14-artifacts-reference.md)

### 48. Acceptance scenarios and validation guide
- **Phase:** Verification. It is written during design or planning.
- **Purpose:** Concrete end-to-end scenarios, with run instructions, that prove the feature works and define "done". For long-running agents it takes the form of a project-wide feature list with pass flags that agents may only flip, so they cannot silently drop scope or declare done too early.
  - Given/When/Then criteria written inside the spec belong to #23.
  - Automated test code and Gherkin bound to step definitions belong to #49.
  - Pass flags are the only status this type holds; narrative progress belongs to #42.
- **Typical contents:**
  - Prerequisites, setup and run commands.
  - Key validation scenarios with their expected results.
  - An end-to-end verification step.
  - Links to the contracts and the data model.
  - A JSON feature list, each entry with a category, a description, ordered verification steps and `passes: false/true`. Features are checked end to end, "as a human user would".
- **When written:** Spec Kit's `quickstart.md` is generated during `/plan`, Phase 1, together with the data model and contracts. Anthropic's `feature_list.json` is written once, at project initialisation, from the high-level prompt. Both are run, and the flags flipped, after implementation.
- **Author:** Generated by AI (the plan command, or an initialiser agent). Human review is usual for quickstart.md and optional for feature lists. Coding agents only update the flags.
- **Core or optional:** Optional. A separate document for long-running or multi-session work, or complex setup; otherwise the spec's acceptance criteria plus a final verification step.
- **Lifespan:** `quickstart.md` lives as long as its feature folder. `feature_list.json` is project-wide (more than 200 features in Anthropic's example) and lasts for the whole project.
- **Also called / tool examples:** quickstart.md, feature_list.json, end-to-end verification step.
  - Spec Kit: `specs/<f>/quickstart.md`.
  - Anthropic harness: `feature_list.json`.
  - Claude Code: a spec that ends with an end-to-end verification step.
- **Sources:** [Spec Kit plan template](https://github.com/github/spec-kit/blob/main/templates/commands/plan.md) · [Spec Kit spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) · [Claude Code best practices](https://code.claude.com/docs/en/best-practices) · [Anthropic: long-running harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

### 49. Executable test specification
- **Phase:** Verification. In test-first SDD it is written during planning or before implementation; it runs in verification and maintenance.
- **Purpose:** Tests that encode the expected behaviour and give the agent an objective pass/fail signal; the verifiable core of the spec. Deleting or weakening them counts as cheating (Kent Beck; Anthropic's harness says it is "unacceptable to remove or edit tests"). A test kept after delivery can stand as the record of behaviour even when the prose spec is thrown away.
- **Typical contents:**
  - Failing tests written first (unit, integration, end-to-end).
  - Contract tests generated from #31.
  - Gherkin `.feature` files bound to step definitions.
  - Conformance suites that do not depend on any one implementation (input and expected output).
  - Property-based tests (the properties themselves are stated in #36).
  - Evals tied to spec clauses, only for AI or nondeterministic features of the software being built; evals of the agent's own context belong to #20.
- **When written:** Before implementation in test-first SDD, or alongside it. Kept and extended with every change. Spec Kit orders them contract → integration → end-to-end → unit.
- **Author:** The AI often writes them and a human approves the scenarios (Spec Kit Article III requires the user to approve the tests). They may also come from a third-party standard.
- **Core or optional:** Core.
- **Lifespan:** Living. Conformance suites that are independent of any implementation can be reused across implementations.
- **Also called / tool examples:** test-first tests, TDD tests, .feature files, contract tests, conformance suite, golden fixtures, property-based tests.
  - Cucumber, Reqnroll, Behave.
  - Specmatic.
  - Spec Kit: Article III (test-first) and Article IX (contract tests before implementation).
  - whenwords YAML conformance tests, html5lib-tests, test262.
  - Breunig: about 750 YAML conformance tests.
  - Hypothesis.
  - Kiro: property-based tests for bug fixes.
  - Reversa: Gherkin parity scenarios. Borderline: its final parity validation was not completed.
- **Sources:** [Gherkin reference](https://cucumber.io/docs/gherkin/reference/) · [Spec Kit spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) · [Kent Beck](https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes) · [Willison: porting JustHTML](https://simonwillison.net/2025/Dec/15/porting-justhtml/) · [Willison: a library with no code](https://simonwillison.net/2026/Jan/10/a-software-library-with-no-code/) · [Breunig: SDD triangle](https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html) · [Developer Toolkit: BDD](https://developertoolkit.ai/en/workflows/plan/behavior-driven-dev/) · [Anthropic: long-running harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) · [Anthropic: evals (supporting)](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) · [arXiv 2402.13521](https://arxiv.org/abs/2402.13521) · [arXiv 2505.09027](https://arxiv.org/pdf/2505.09027) · [arXiv 2506.18315 (PBT)](https://arxiv.org/html/2506.18315v1) · [arXiv 2605.18684 (Reversa)](https://arxiv.org/abs/2605.18684) · [Grove: specifications are the new code](https://www.ai.engineer/talks/8rABwKRsec4-specifications-are-the-new-code)

### 50. Code review report
- **Purpose:** Findings from an independent reviewer (a fresh subagent, another session or a human) who checks the diff, or the existing code, against the spec, plan and standards. The findings become fix tasks. #51 gives positive evidence of conformance, and #53 records the decision. A maintenance variant reviews the whole codebase against a reference app or spec (see #55).
- **Typical contents:** Findings, often classified by severity:
  - requirements not implemented;
  - untested edge cases;
  - changes outside the scope;
  - standards violations;
  - missing tests;
  - cleanliness issues in existing code.

  Flag only gaps that affect correctness or the stated requirements, because a reviewer told to find gaps usually reports some. A review with no findings is a valid outcome.
- **When written:** After each task, phase or change, before merge.
- **Author:** An AI reviewer agent; a human triages the findings and decides.
- **Core or optional:** Core as a practice. The artifact is often throwaway.
- **Lifespan:** Per change. Usually not kept as a file: it is returned to the session, appended to the plan, story or PR as comments, and sometimes kept as numbered review files.
- **Also called / tool examples:** code-review.md, review findings, verification comments, adversarial review, missing-tests.md.
  - Claude Code: a reviewer subagent prompted to review the diff against PLAN.md; `/code-review` reviews the diff for bugs.
  - BMAD: `bmad-code-review` uses several independent reviewers, triages their findings, and appends a dated Code Review block to the ticket's plan. The separate `bmad-review` applies lenses (adversarial, edge case, verification gap). v4 had a QA Results section.
  - Traycer: verification comments rated Critical, Major, Minor or Outdated.
  - Conductor: review appends a "Review Fixes" phase to `plan.md`.
  - Harper Reed: `code-review.md` generated from the packed repo.
  - GSD: `UI-REVIEW.md`.
- **Sources:** [Claude Code best practices](https://code.claude.com/docs/en/best-practices) · [BMAD skills](https://docs.bmad-method.org/reference/skills-and-agents/) · [BMAD: break work into stories](https://docs.bmad-method.org/plan/break-work-into-stories-and-track-it/) · [Traycer phases](https://docs.traycer.ai/extension/tasks/phases) · [Conductor](https://github.com/gemini-cli-extensions/conductor) · [Harper Reed](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/) · [Osmani](https://addyosmani.com/blog/good-spec/)

### 51. Verification report and evidence pack
- **Purpose:** Shows that the implementation actually meets the spec and the goals of the phase, not merely that tasks were ticked. It bundles the evidence, so that reviewers can audit it rather than work it out again. The formal PASS, FAIL or WAIVED decision belongs to #53, and the list of defects to #50.
- **Typical contents:**
  - A verification status: verified, partial or failed.
  - Results against each acceptance criterion.
  - UAT results.
  - Test, static-analysis and security-scan output.
  - An assessment of the non-functional requirements.
  - Screenshots and logs.
  - Residual risks.
  - A rationale summary.
  - Links to the audit trail (briefing, tools, agent trajectory).
  - Plans to close any gaps.
- **When written:** After a feature or phase is implemented, before release or merge.
- **Author:** An AI verifier produces it; a human performs UAT and reviews.
- **Core or optional:** Optional. When completion must be shown by more than passing tests: multi-phase work, UAT, audits, autonomous agents.
- **Lifespan:** Per feature or phase. Kept as evidence when the tool writes it to disk (GSD); often it exists only in the session.
- **Also called / tool examples:** VERIFICATION.md, UAT.md, Merge-Readiness Pack, evidence bundle, NFR assessment.
  - GSD: `XX-VERIFICATION.md`, written by gsd-verifier and read by gap-closure planning, and `XX-UAT.md`, written by `/gsd-verify-work` as the human's final gate.
  - SASE Merge-Readiness Pack: functional completeness, sound verification, software engineering hygiene, a clear rationale and full auditability, with progressive disclosure.
  - BMAD v4: `*-nfr-*.md`.
  - AI-DLC: `build-and-test-summary.md`.
  - In-session only, with no saved file: cc-sdd `/kiro:validate-impl` and OpenSpec `/opsx:verify`.
  - Spec Kit: a community verify extension.
- **Sources:** [arXiv 2509.06216 (SASE)](https://arxiv.org/html/2509.06216v2) · [GSD architecture](https://github.com/open-gsd/gsd-core/blob/main/docs/ARCHITECTURE.md) · [GSD core](https://github.com/open-gsd/gsd-core) · [cc-sdd commands](https://github.com/gotalab/cc-sdd/blob/main/docs/guides/command-reference.md) · [OpenSpec concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md) · [BMAD v4 user guide](https://github.com/bmad-code-org/BMAD-METHOD/blob/v4.44.3/docs/user-guide.md)

### 52. Traceability matrix
- **Phase:** Verification. A partial version first appears during planning.
- **Purpose:** Maps each requirement, or each constitutional principle, to the decisions, tasks, code, tests and PRs that cover it. It exposes requirements nothing covers, and tasks or tests that trace to no requirement. It is best generated, not maintained by hand. #47 uses a partial matrix as input, and #51 and #53 cite the matrix as evidence.
- **Typical contents:** Requirement IDs mapped to tasks, tests, evidence and status, plus a coverage summary. Constitutional SDD maps principles to file and line.
- **When written:** Once tasks are planned, at checkpoints during implementation (BMAD `*trace`) and after implementation. Regenerated on change.
- **Author:** Generated by AI or the tool; checked by a human.
- **Core or optional:** Optional. For regulated or compliance work, large requirement sets or audits.
- **Lifespan:** Dated snapshots per story (BMAD), or regenerated each time and living.
- **Also called / tool examples:** trace report, traceability.md, traceability.json, coverage table, compliance traceability matrix.
  - BMAD v4: `docs/qa/assessments/{epic}.{story}-trace-{YYYYMMDD}.md`.
  - BMAD TEA: the trace workflow.
  - AI-DLC: `traceability.json` for each unit (contents not documented), plus `verification/phase-check-*.md`.
  - Constitutional SDD: a compliance traceability matrix.
  - Partial or embedded forms: Spec Kit's coverage table in the `/analyze` output (not saved), GSD's traceability section in REQUIREMENTS.md, and Kiro's requirement references in `tasks.md`.
- **Sources:** [BMAD v4 user guide](https://github.com/bmad-code-org/BMAD-METHOD/blob/v4.44.3/docs/user-guide.md) · [Spec Kit analyze command](https://github.com/github/spec-kit/blob/main/templates/commands/analyze.md) · [GSD docs](https://mintlify.wiki/gsd-build/get-shit-done) · [Glukhov: specs–tests–code traceability](https://glukhov.org/app-architecture/testing-architecture/specs-tests-code-traceability-ai-development/) · [arXiv 2602.02584](https://arxiv.org/html/2602.02584v1) · [AI-DLC artifacts](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/14-artifacts-reference.md)

### 53. Gate decision record
- **Phase:** Verification. It is listed here for placement only: gates sit at every phase boundary.
- **Purpose:** Records the explicit decision taken at a phase boundary (spec approved, design approved, ready to implement, story done, ready to merge or release), with the outcome and the reasons. It refers to the evidence in #51, #50 and #52 rather than containing it. Many tools store a gate only as status metadata, which overlaps #42.
- **Typical contents:**
  - The gate.
  - The outcome: PASS, CONCERNS, FAIL or WAIVED; GO, CONDITIONAL GO or NO-GO; or approve, request changes or reject.
  - The reasons and a summary of the top issues.
  - Who signed off, and the date.
  - For a waiver: the reason, the approver and an expiry date.
- **When written:** At each review point between phases.
- **Author:** An AI reviewer proposes the outcome; a human approves, rejects or waives. BMAD's QA gates are advisory ("teams choose their quality bar"), and a human approver is required only for WAIVED.
- **Core or optional:** Optional. When phases need formal approval (team workflows, regulated contexts).
- **Lifespan:** Per gate, kept as a record.
- **Also called / tool examples:** QA gate, gate .yml, readiness check, approval, sign-off.
  - BMAD v4: `docs/qa/gates/{epic}.{story}-{slug}.yml`, with the schema `qa-gate-tmpl.yaml`.
  - spec-workflow MCP: `.spec-workflow/approval/`; approving a document locks it.
  - cc-sdd: phase approval flags in `spec.json` (the validate-design verdict is not saved).
  - SASE: the version-controlled resolution of a Merge-Readiness Pack.
  - Kiro's review points and SDAD's Spec Fidelity Gate show that gates exist, but they leave no record.
- **Sources:** [BMAD v4 user guide](https://github.com/bmad-code-org/BMAD-METHOD/blob/v4.44.3/docs/user-guide.md) · [BMAD QA gate template](https://github.com/bmad-code-org/BMAD-METHOD/blob/v4.44.3/bmad-core/templates/qa-gate-tmpl.yaml) · [cc-sdd commands](https://github.com/gotalab/cc-sdd/blob/main/docs/guides/command-reference.md) · [spec-workflow MCP](https://github.com/Pimzino/spec-workflow-mcp/blob/main/docs/WORKFLOW.md) · [Kiro specs](https://kiro.dev/docs/specs/) · [arXiv 2608.20341 (SDAD)](https://arxiv.org/html/2608.20341)

---

## 7. Maintenance / Evolution

### 54. Living system specification
- **Phase:** Maintenance / Evolution. When an existing codebase is first brought under SDD, the recovered spec is written at the context phase.
- **Purpose:** A persistent description of how the system currently behaves, organised by capability or component and kept in sync with the code.
  - In spec-anchored SDD it is the source of truth: each change updates it, and feature or change specs are merged into it.
  - In spec-as-source SDD it is the artifact humans edit, and the code is generated from it. In tools with one spec per component (Tessl), the feature spec and the living spec can be the same file.

  Specs decay over time ("spec rot"), so pair it with #55.
- **Typical contents:** Capability and component specs with requirements (SHALL/MUST) and testable scenarios, links to tests and the public API, and generation targets. For brownfield systems it is recovered from the existing code. For migrations it records the legacy behaviour to preserve, with confidence marks.
- **When written:** Updated whenever a change is archived (its deltas are merged in), or edited directly in spec-as-source. Created by reverse engineering when an existing codebase is brought under SDD.
- **Author:** The merge is done mechanically or by AI at archive time, or the AI generates the spec from code. A human reviews.
- **Core or optional:** Optional. Used in spec-anchored or spec-as-source SDD; spec-first work throws specs away after delivery. Spec Kit calls its specs "living" but works spec-first in practice.
- **Lifespan:** Living.
- **Also called / tool examples:** capability spec, source-of-truth spec, main specs, as-built spec, recovered or reverse-engineered spec.
  - OpenSpec: `openspec/specs/`, into which the archive step merges deltas.
  - Tessl: `.spec.md` with `@generate` and `@describe`, and linked tests.
  - AfterVibe: a research prototype that recovers specs from the code and the agent conversation and validates them by blind regeneration.
  - Reversa: claims with confidence marks and Gherkin parity scenarios; its final parity validation and cutover were not completed.
- **Sources:** [OpenSpec concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md) · [OpenSpec glossary](https://openspec.dev/docs/glossary) · [Tessl launch](https://tessl.io/blog/tessl-launches-spec-driven-framework-and-registry) · [Tessl SDD tile](https://tessl.io/registry/tessl-labs/spec-driven-development) · [Fowler: SDD tools (spec levels)](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) · [arXiv 2608.25202 (spec rot)](https://arxiv.org/html/2608.25202) · [arXiv 2602.00180](https://arxiv.org/html/2602.00180) · [arXiv 2607.09900 (AfterVibe)](https://arxiv.org/abs/2607.09900) · [arXiv 2605.18684 (Reversa)](https://arxiv.org/abs/2605.18684)

### 55. Drift report (spec or pattern)
- **Purpose:** Compares the declared intent (spec, contracts, reference app) with the actual code and behaviour, to find where they have diverged. The result is either a code fix or a spec update.
  - Coverage gaps belong to #52.
  - A check of one change at its gate belongs to #51.
  - Drift of the codebase map is handled in #6.
  - AI-DLC's infrastructure `drift-report.md` is a different thing (see #58).
- **Typical contents:** Divergences found by schema validation, contract tests, spec diffs, pattern comparison or reconciliation at commit time, each with a suggested resolution. Some tools classify the drift: vibe-spec-sync labels it extending, modifying or contradicting; specalign labels it behaviour, constraint or missing-spec drift. The report can act as a CI merge gate.
- **When written:** Continuously in CI, at commit time, or on demand.
- **Author:** Tooling or AI generates it. A human curates or edits it and judges each finding before the agent acts.
- **Core or optional:** Optional. In spec-anchored or spec-as-source work, or when a reference application anchors the patterns.
- **Lifespan:** Throwaway for each run, or kept as a cumulative drift log.
- **Also called / tool examples:** drift detection, spec diff, pattern drift report, spec-code reconciliation.
  - Boeckeler: a drift report against a reference app, with an MCP server that fetches the reference app's commits.
  - Spec Kit: `/speckit.converge` assesses the codebase against the spec, plan and tasks and appends a Convergence section to `tasks.md`.
  - Purlin: a drift skill.
  - vibe-spec-sync, specalign, spec-kit-reconcile.
  - Plumb: a proof of concept that extracts decisions at commit time and syncs spec coverage.
  - CI contract tests.
- **Sources:** [Fowler: anchoring to a reference application](https://www.martinfowler.com/articles/exploring-gen-ai/anchoring-to-reference.html) · [Spec Kit agentic SDD (converge)](https://github.github.io/spec-kit/reference/agentic-sdd.html) · [Purlin drift skill](https://www.claudepluginhub.com/skills/rlabarca-purlin/drift) · [Spec Growth Engine preprint](https://www.emergentmind.com/papers/2606.27045) · [Glukhov: traceability](https://glukhov.org/app-architecture/testing-architecture/specs-tests-code-traceability-ai-development/) · [Breunig: SDD triangle (Plumb)](https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html) · [InfoQ (drift checks in CI)](https://infoq.com/articles/spec-driven-development) · [Thoughtworks](https://www.thoughtworks.com/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices)

### 56. Lessons learned and agent memory
- **Purpose:** Distils mistakes, fixes and successful strategies from past sessions and work, and feeds them back into future context, so the same errors are not repeated. It is a cumulative store across tasks and sessions (unlike #44, which records events task by task). It also acts as a staging area: validated lessons graduate into #1, #7, #2 or the specs.
- **Typical contents:**
  - Errors and build failures, with their fixes.
  - Validated lessons.
  - Corrections from the user.
  - Proposed updates to the instructions, rules or specs.
- **When written:** At the end of a session, task or epic, or when the agent is corrected.
- **Author:** Written by AI, often automatically. Human review, and promotion of lessons into instructions or specs, is recommended but not built in.
- **Core or optional:** Optional. For long-running projects where agents repeat mistakes.
- **Lifespan:** Living and cumulative. Auto memory is often local to one machine and not committed. Red Hat's `LessonsLearned.md` is committed in the specs folder.
- **Also called / tool examples:** LessonsLearned.md, learnings.md, auto memory, MEMORY.md, memory.md, agent-written project memory.
  - Claude Code auto memory: written by Claude, scoped per repository and shared across worktrees; the first 200 lines or 25 KB are loaded every session; stored locally.
  - Windsurf: legacy Cascade memories in `~/.codeium/windsurf/memories/`. Its docs advise moving durable knowledge into rules or AGENTS.md.
  - Red Hat: `LessonsLearned.md`.
  - GSD: `debug/knowledge-base.md`.
  - AI-DLC: `memory.md`.
  - Embedded forms: the Surprises & Discoveries and Outcomes & Retrospective sections of an ExecPlan. Ralph folds its learnings into `AGENT.md`.
- **Sources:** [Claude Code memory](https://code.claude.com/docs/en/memory) · [Windsurf/Devin memories](https://docs.devin.ai/desktop/cascade/memories) · [Red Hat: SDD quality](https://developers.redhat.com/articles/2025/10/22/how-spec-driven-development-improves-ai-coding-quality) · [Huntley: Ralph](https://ghuntley.com/ralph/) · [Codex ExecPlans](https://developers.openai.com/cookbook/articles/codex_exec_plans) · [GSD architecture](https://github.com/open-gsd/gsd-core/blob/main/docs/ARCHITECTURE.md) · [arXiv 2512.10398 (Confucius, abstract only)](https://arxiv.org/pdf/2512.10398) · [MindStudio (vendor blog)](https://www.mindstudio.ai/blog/how-to-build-learnings-loop-claude-code-skills)

### 57. User and developer documentation
- **Phase:** The end of implementation, then maintenance (regeneration).
- **Purpose:** Documentation written for humans (README, usage, build and contribution guides, changelog and release notes), produced or regenerated by the agent from the spec and/or the code. It is kept separate from the instructions written only for agents (#1).
- **Typical contents:**
  - Quick start, usage, and build and run instructions.
  - A contribution guide.
  - Generated API reference docs.
  - A changelog and release notes, drafted from specs, commits and PRs (for example using Keep a Changelog sections).

  Documentation conventions belong in #7 or #14.
- **When written:** At the end of a feature or release, or automatically on code changes through hooks. Willison asks for the README in the final prompt.
- **Author:** Written by a human, or generated by AI and reviewed by a human.
- **Core or optional:** Optional. When the software has users or contributors other than the agent.
- **Lifespan:** Living (regenerated).
- **Also called / tool examples:** README.md, CONTRIBUTING.md, CHANGELOG.md, release notes, generated docs.
  - Harper Reed: a README generated from the packed repo with an LLM CLI.
  - Willison: the README requested in the final prompt.
  - Kiro: a doc-sync agent hook that updates the README and OpenAPI.
  - An update-changelog skill.
- **Sources:** [Harper Reed](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/) · [Willison: porting JustHTML](https://simonwillison.net/2025/Dec/15/porting-justhtml/) · [Kiro: README files](https://kiro.dev/blog/how-i-stopped-worrying-about-readme-files/) · [Kiro hook examples](https://kiro.dev/docs/hooks/examples/) · [Kiro agent hooks](https://kiro.dev/blog/automate-your-development-workflow-with-agent-hooks/) · [Red Hat: SDD quality](https://developers.redhat.com/articles/2025/10/22/how-spec-driven-development-improves-ai-coding-quality) · [InfoQ (generated API docs)](https://infoq.com/articles/spec-driven-development) · [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · [update-changelog skill](https://claudeskills.info/skills/mitsuhiko/agent-stuff/update-changelog/)

### 58. Production feedback report
- **Purpose:** Records what the deployed software actually did and turns it into input for the next SDD iteration. Incidents, metrics, performance bottlenecks, cost findings and security vulnerabilities become new or amended requirements, bug specs (#25) or updates to #54, instead of ending as hotfixes only.
- **Typical contents:**
  - Reporting period and scope.
  - SLO/SLI compliance and error-budget burn.
  - Incidents with timeline, impact and root cause.
  - Performance bottlenecks and load observations.
  - Cost analysis and recommendations.
  - Improvement proposals, each mapped to the spec artifact it should change.

  Classifying a root cause as a spec gap (the spec was silent, ambiguous or wrong) is this catalogue's recommendation, not an established practice in the sources.
- **When written:** After deployment: on a regular cadence, after significant incidents, or at the end of an operation cycle. It is read at the start of the next ideation or specification cycle.
- **Author:** An AI agent drafts it from observability, cost and incident data (in AI-DLC, the operations agent with the platform agent). Humans approve it at the stage gate and decide what goes back into the spec loop.
- **Core or optional:** Optional. Only for software deployed and operated in production; AI-DLC skips it for proofs of concept and non-production deployments.
- **Lifespan:** A dated, append-only record per period or incident. Its proposals are used up when they become spec changes.
- **Also called / tool examples:** operational feedback report, feedback loop report, SLO report, cost and performance analysis.
  - AI-DLC stage 4.7, Continuous Feedback & Optimization: `slo-report.md`, `cost-analysis.md`, `feedback-loop.md` and `feedback-optimization-questions.md`. Its `drift-report.md` covers infrastructure drift and is not #55. The gate offers Approve, Request Changes, or Start New Ideation Cycle, which feeds `feedback-loop.md` into a new stage 1.1.
  - Spec Kit: the Feedback Loop principle (conceptual; no template).
  - Runbooks written before incidents (AI-DLC stage 4.5) belong to #34.
- **Sources:** [AI-DLC Operation stages](https://awslabs.github.io/aidlc-workflows/reference/04-stages/operation/) · [Spec Kit spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) · [aidlc-workflows repository](https://github.com/awslabs/aidlc-workflows)

---

## Minimum viable set

For a small feature in an existing repository, these core types are enough:

1. **Agent instructions file (#1).** Include the stack (#5) and the build and test commands as sections.
2. **Feature specification (#23), or a bug specification (#25) for a defect.** User stories and acceptance criteria, with clarifications (#26) recorded as a section.
3. **Feature technical design (#29).** A few lines, or merged into the plan.
4. **Implementation plan and task list (#38).** Skip it only for a change you can describe in one sentence.
5. **Executable test specification (#49).** Tests that encode the acceptance criteria, written first where possible.
6. **Code review report (#50).** An independent review against the spec; the findings can be ephemeral.
7. **Commits and pull request description (#46).** Link the spec.

For greenfield work, add **product context (#3)**. When a choice will have lasting consequences, add a **decision record (#35)**.

---

## Appendix: considered and excluded or merged

### Rejected as types

| Item | Outcome | Reason |
|---|---|---|
| Change archive | Became a lifespan note on #24 | It is a storage location and end-of-life state. Archiving moves existing documents (proposal, deltas, design, tasks) to a dated folder and creates no new content. GSD's MILESTONES.md is a changelog-like history, which belongs to #57. |
| Changelog and release notes | Merged into #57 | No SDD toolkit produces a changelog as an SDD artifact. The "recent changes and deprecations for agents" role belongs in #1 or #7, where the Cursor rules study actually found that content. |
| Ephemeral prompt (critique baseline) | Excluded | Not a document type. It is the counter-example in the prompts-versus-specs debate. |
| OpenSpec explore step (`/opsx:explore`) | Excluded from #21 | A thinking conversation that writes no document. |
| Output style definition | Excluded from #18 | It sets the tone and format of the main session, with no separate tools, model or context, and it does not apply to subagents. At most, it is session-level instruction content (#1). |

### Folded into kept types

| Folded item(s) | Into | Reason |
|---|---|---|
| Agent instructions file; project agent instructions; agent context or project instructions file; rules or guidance file; repository-level context file; always-loaded rules | #1 | Same role. |
| Nested or subdirectory, personal (user-global), organisation-managed, and local or override instructions | #1 | Same mechanism at a different scope; listed as scope layers. |
| Codified Context "hot-memory constitution" | #1 | A single always-loaded manifest file, not a constitution. |
| Project constitution; engineering principles; non-negotiable principles; normative specification | #2 | Same role; a security constitution is a variant. |
| MentorScript and other team-norms rulebooks | #7 | Granular norms grown from coaching feedback, not cross-cutting gates. |
| Constraints / non-goals record | #23 and #2 | Non-goals for one task go in the spec's out-of-scope section; persistent constraints go in the constitution. |
| Product context or overview; Cline productContext.md; projectbrief.md; vision or mission | #3 | Same role (why the product exists). |
| Product brief for one initiative; PRFAQ | #21, and precursor of #22 | Per-initiative inputs, not standing project context. |
| Product guidelines (non-code style) | #3; visual identity to #8 or #32 | Prose and brand guidance belong to product context; visuals have their own types. |
| Knowledge-priming or memory-bank cheat sheet | Split across #3, #5, #6, #10 | A composite of existing roles. |
| Technology stack document; technical context (techContext.md) | #5 | Same role. |
| Tech stack and structure context | #5 and #6 | Stack part to #5, structure part to #6. |
| Project structure or codebase map; brownfield structural docs | #6 | Same role; recovered behavioural specs go to #54. |
| Packed codebase context bundle (repomix) | #6, as a related input | A generated, throwaway dump, not a maintained map. |
| System patterns / architecture and structure overview | #28 and #6 | Architecture and patterns to #28; file organisation to #6. |
| Coding standards or conventions (CONVENTIONS.md); "how" specs; path-scoped and conditional rule files; code review instructions | #7 | The same normative content; scoping is a loading mechanism, not a role. |
| Kiro `security-policies.md` | #7 | Secure-coding rules, not a threat model. |
| Change and deprecation notes for agents | #1 and #7 | Content of the instruction and rule files. |
| Development workflow and process definition; LoopScript; SOPs; Definition of Done | #13 | The team's standing procedure and quality bar. |
| Artifact templates; workflow schema; spec templates and generation rules; plan rulebook (PLANS.md) | #14; the order of artifacts to #13 | Templates shape documents; phase sequencing is process. |
| Agent hooks; deterministic guardrail configuration; boundaries and autonomy or permission policy | #15; workflow-automation hooks to #13 | Enforcement belongs to guardrails; process gates belong to the workflow. |
| Skills; reusable procedures; custom commands, prompt files and workflows; prompt and command libraries | #17 | A stored procedure for a repeatable step; differs only in how it is triggered. |
| Subagent, persona, custom agent and mode definitions | #18 | Same role. |
| Environment bootstrap script; tool and MCP server configuration | #19 | Executable or declarative runtime setup. |
| Dependency and library usage specs; external reference material and upstream standards | #12 | Authoritative outside knowledge. |
| Supplementary reference docs; agent-oriented subsystem knowledge base | #11 | Deeper project knowledge loaded on demand. |
| Code references and exemplars; reference application; golden examples | #10 | Same role. |
| Idea exploration and brainstorming notes; go/no-go decision; feasibility assessment | #21 | The assessment before committing to an idea. |
| PRD; SRS; product or functional requirements document (PRD, FRD) | #22 | Product-level requirements; SRS is the classic forerunner. |
| ISO 29148 stakeholder requirements | #22 | A requirements specification, not a vision. |
| Feature, behavioural, functional and change specs; requirements documents; user stories and acceptance criteria; EARS requirements; use cases; delta specs | #23 | The same "what" document in different notations or forms. |
| Non-functional / quality requirements | #23, #34, #51 | A section of the spec or PRD; operational NFRs go to #34, assessing them to #51. |
| Acceptance criteria / executable scenarios | #23; the executable form to #49 | Criteria are spec content; runnable checks are tests. |
| Story files handed to a dev agent; issue as task spec; PRP; work packet; sub-spec slice; raw feature request (INITIAL.md) | #39 | A self-contained unit of work for one agent. |
| Change proposal / RFC | #24 | Same role; RFC is only a loose analogy. |
| Bug report, bug analysis and bugfix specs | #25 | Same role. |
| Clarification log; open questions; discussion record; consultation request and resolution | #26 | The same Q&A role, at any phase. |
| Research and spike notes; codebase research; subagent research reports | #27 | Same role; subagent summaries are the throwaway form. |
| System architecture document / description | #28 | Same role. |
| Technical design and system design documents; Spec Kit-style plan.md; implementation-details annex | #29 | The "how" document for one feature. |
| Data and domain models, ERDs, schemas and invariants | #30 | Same role. |
| API and interface contracts | #31 | Same role. |
| UX/UI design specs | #32 | Same role. |
| Threat model; security or compliance specification | #33 | Same role. |
| Non-functional / operational spec; runbooks and playbooks | #34 | The same concern for deployed services. |
| ADRs; decision logs; feature decision logs | #35 | The same "why" role. |
| Formal and contract specifications | #36 | Base of the type. |
| Product roadmap and backlog; milestones; epics; work breakdown; ideas backlog | #37 | The initiative-level breakdown; story files go to #39. |
| Implementation, step-by-step and plan-mode plans; ExecPlan; task lists and checklists; the agent's in-session to-do list | #38 | The ordered, checkable plan in its variants. |
| Risk profile; risks and debt register; risk and constraint register | #40 | Same role at different grains. |
| Test design, test strategy and validation strategy | #41 | Same role. |
| Work status tracker; STATE.md; active context; progress logs and files | #42; one-off snapshots to #43 | The cumulative "where are we" state. |
| Structured notes / scratchpad | #42 | Persistent progress notes, not a one-off handoff. |
| Compaction or handoff summary; session handoff note | #43 | Point-in-time continuity snapshot. |
| Implementation logs and summaries; audit trail; provenance or trajectory record | #44 | The after-the-fact record. |
| Natural-language code documentation; inline TODO mini-specs | #45 | Prose and specs placed in the code. |
| Commit history; commit messages; PR description and change summary | #46 | Same role. |
| PR review comments | #50 | Review findings, not the change record. |
| Requirements and spec quality checklists; cross-artifact consistency analysis | #47 | Pre-implementation check of the documents; gate waivers go to #40. |
| Spec Kit converge / convergence analysis | #55 | It checks the codebase after implementation, not the documents. |
| Quickstart and validation guides; feature list / acceptance tracking file (feature_list.json) | #48 | A runnable definition of done. |
| BDD/Gherkin files; conformance suites; test-first suites; property-based tests; spec-clause evals for product features | #49 | Executable pass/fail specification. |
| Evals of agent instructions and skills | #20 | They test the agent's context, not the product. |
| Code review reports; review against plan or spec; gap or issue lists from analysis | #50 | Same reviewer role. |
| Verification and UAT reports; merge-readiness or evidence packs; NFR assessments | #51 | Positive evidence of conformance. |
| Traceability matrix; trace part of a quality-gate report | #52; gate decision to #53, NFR assessment to #51, diff review to #50 | Each part goes to the type that owns it. |
| Quality gate decision; review gate and sign-off records | #53 | Same role. |
| BMAD retrospective (epic acceptance review) | #53 and #51 | An acceptance review with a verdict, not a store of lessons. |
| Living capability specs; spec-as-source specs; reverse-engineered, recovered and migration specs | #54 | The living source of truth, however it is bootstrapped. |
| Drift report / spec diff | #55 | Base of the type. |
| Retrospectives for agents; lessons-learned logs; agent memory notes; auto memory | #56 | The same feedback loop. |
| README and generated user or developer docs; changelog and release notes | #57 | Documentation written for humans. |