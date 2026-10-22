# Exponentes del Spec Driven Development (SDD)

**Fecha:** 2026-10-22

## Resumen

El SDD (Spec Driven Development, desarrollo guiado por especificaciones) con IA (inteligencia artificial) es un enfoque en el que una especificación escrita, versionada y revisable por humanos pasa a ser la fuente de verdad: el agente de código la usa para planificar, dividir en tareas e implementar, y el código se verifica contra ella. Lo popularizaron en 2025 herramientas como GitHub Spec Kit, Kiro (AWS (Amazon Web Services)), Tessl, OpenSpec y BMAD-METHOD (Breakthrough Method for Agile AI-Driven Development), y lo discuten divulgadores y críticos que lo ven como un regreso del Waterfall. Sus raíces son mucho más antiguas: la lógica de Hoare y TLA+ (Temporal Logic of Actions) en los métodos formales, el Design by Contract de Meyer, el property-based testing de QuickCheck, BDD (Behavior-Driven Development), Specification by Example y el diseño API-first (API (Application Programming Interface)) con OpenAPI. Todas comparten la idea de que la especificación debe ser precisa y comprobable contra el código.

Dos pasadas posteriores añadieron, sin quitar a nadie, GSD (Get Shit Done), JetBrains y el primer estudio empírico amplio sobre el SDD con IA (Carnegie Mellon), y sumaron EARS (Easy Approach to Requirements Syntax) a los precursores. Una sección de menciones honoríficas recoge 31 nombres con un aporte real pero menor, derivado o tangencial al SDD.

## Metodología

1. **Búsqueda:** 8 agentes, cada uno con un enfoque distinto: creadores de herramientas, divulgadores y blogs, papers académicos, charlas y podcasts, organizaciones, precursores de métodos formales y Design by Contract, precursores de BDD, Specification by Example y API-first, y señales de la comunidad (GitHub, Hacker News, Reddit).
2. **Curación:** un agente juntó los resultados, eliminó duplicados y eligió 20 exponentes del SDD con IA más los precursores.
3. **Verificación adversarial:** 9 agentes intentaron refutar cada candidato: datos reales, enlaces vivos, relevancia no inflada. Se corrigieron cifras, fechas y afiliaciones (ver el apartado "Verificación" de cada ficha).
4. **Crítico de completitud:** buscó ausencias importantes y revisó los casos dudosos.
5. **Segunda pasada (ausentes recientes):** 6 agentes buscadores rastrearon ausencias de 2025-2026, 10 agentes verificaron a los candidatos más fuertes y un agente editor propuso altas, menciones y descartes. Entraron GSD y el estudio de Carnegie Mellon, sin reemplazar a nadie.
6. **Tercera pasada:** se verificaron 30 candidatos que habían quedado pendientes por el tope de verificaciones de la segunda pasada. Resultado: 2 altas (JetBrains en la lista principal y Alistair Mavin entre los precursores), 25 menciones honoríficas y 3 descartes.

**Resultado:** 33 fichas verificadas (23 de SDD con IA y 10 precursores) y 31 menciones honoríficas. En la primera pasada se quitó 1 ficha (CodeSpeak, de Andrey Breslav, por datos clave sin verificar y por su pivot en julio de 2026 hacia la captura de intención) y se añadió 1 (Jesse Vincent, Superpowers); en la segunda y la tercera se añadieron 4 fichas sin quitar ninguna. Ninguna ficha de la lista principal quedó como "dudosa" ni "refutada"; la mayoría de las menciones honoríficas sí quedaron como dudosas en cuanto a su relevancia.

**Limitaciones:**
- El presupuesto compartido de búsquedas web se agotó durante la verificación; buena parte de los datos se comprobó con descarga directa de URLs conocidas. Por eso el crítico no pudo hacer un barrido abierto de ausencias recientes.
- Algunas páginas devolvieron error (LinkedIn, MIT Press, ACM, O'Reilly, GeekWire, Real Python) y esos datos se excluyeron o se marcan como no confirmados.
- Sesgo de organizaciones: hay tres entradas ligadas a AWS (Kiro, Marc Brooker y el Automated Reasoning Group). Google solo aparece como coautor del estudio de Carnegie Mellon y en las menciones honoríficas (Google DevAI Research y el codelab de Antigravity). Suplentes verificados y no incluidos: Martin Kleppmann (Cambridge; post del 08-12-2025 "Prediction: AI will make formal verification go mainstream") y Google Conductor (post del 17-12-2025 que lo llama "context-driven development", no SDD). También hay solapamiento entre GitHub Spec Kit y Den Delimarsky, y entre JetBrains y la mención de Paul Everitt.
- De los 35 candidatos que quedaron pendientes tras la segunda pasada, 5 siguen sin verificar.

**Descartados en la segunda y tercera pasada:**
- Eyal Toledano (Task Master AI): es planificación PRD (Product Requirements Document) → tareas, no SDD; el PRD no se mantiene como fuente de verdad, el repo no usa el término spec-driven y Toledano pasó a otro producto (Hamster).
- Laura Tacho: fue invitada, no presentadora, del episodio "What is spec-driven development?" del podcast de Thoughtworks (28-05-2026); su aporte al SDD se reduce a esa aparición.
- Louis Knight-Webb (bloop, Vibe Kanban): su charla "Software Engineering Is Becoming Plan and Review" y Vibe Kanban tratan de orquestar y revisar agentes, no de SDD.
- Tomasz Lelek y Artur Skowroński: su libro "Vibe Engineering" (Manning) no trata de SDD; solo comparte un bundle de Manning con libros de SDD.

## Índice

**[Exponentes del SDD con IA](#exponentes-del-sdd-con-ia)** (23, sin ranking)

- [Creadores de herramientas](#creadores-de-herramientas) (9): GitHub (Spec Kit y SpecLang), Den Delimarsky, Kiro (AWS), Guy Podjarny, Tabish Bidiwale (OpenSpec), BMad Code (BMAD-METHOD), Jesse Vincent (Superpowers), GSD (Get Shit Done), JetBrains (Junie / JetBrains AI)
- [Teoría y divulgación](#teoría-y-divulgación) (7): Birgitta Böckeler, Sean Grove, Marc Brooker, Patrick Debois, Addy Osmani, Drew Breunig, Harper Reed
- [Investigación académica](#investigación-académica) (2): Shuvendu K. Lahiri, estudio de Carnegie Mellon (Shyam Agarwal, Bogdan Vasilescu y equipo)
- [Investigación aplicada y métodos formales](#investigación-aplicada-y-métodos-formales) (1): AWS Automated Reasoning Group (Byron Cook)
- [Críticos y debate](#críticos-y-debate) (2): Kent Beck, François Zaninotto
- [Libros y formación](#libros-y-formación) (2): Hari Krishnan, Simon Martinelli

**[Precursores clásicos](#precursores-clásicos)** (10)

- Métodos formales: Tony Hoare, Leslie Lamport, K. Rustan M. Leino
- Design by Contract: Bertrand Meyer
- Property-based testing: John Hughes
- BDD: Dan North
- Specification by Example y tests de aceptación: Gojko Adzic, Ward Cunningham
- API-first y contratos: OpenAPI Initiative
- Notaciones de requisitos: Alistair Mavin (EARS)

**[Menciones honoríficas](#menciones-honoríficas)** (31)

- [Herramientas y flujos de trabajo](#herramientas-y-flujos-de-trabajo) (13)
- [Divulgación, libros y formación](#divulgación-libros-y-formación) (10)
- [Investigación: especificaciones formales y verificación con LLM](#investigación-especificaciones-formales-y-verificación-con-llm) (8)

**[Para seguir investigando](#para-seguir-investigando)**

---

## Exponentes del SDD con IA

### Creadores de herramientas

#### GitHub (Spec Kit y GitHub Next SpecLang)

- **Tipo:** organización
- **Afiliación:** GitHub (Microsoft). Spec Kit: Den Delimarsky y John Lam (creadores), Manfred Riem (mantenedor principal desde el 22-01-2026). SpecLang: equipo de GitHub Next (Johan Rosenkilde, Russell Horton, Krzysztof Cieślak, Jonathan Carter).
- **Quién es:** la plataforma de código de Microsoft. Publica Spec Kit, el toolkit open source de desarrollo guiado por especificaciones más usado con agentes de IA. Antes, su laboratorio GitHub Next exploró el "código en prosa" con SpecLang.
- **Qué aportó:** popularizó el flujo de SDD con IA. Spec Kit propone fases explícitas con artefactos revisables (constitution → specify → plan → tasks → implement), en las que la especificación guía al agente de código. El proyecto pasó de un CLI (Command-Line Interface) a un harness extensible: extensiones (feb-2026), presets (mar-2026), motor de workflows (abr-2026) y v1.0.0 (21-08-2026), con 38 integraciones de agentes. SpecLang (GitHub Next, nov-2023) fue un prototipo de investigación en el que un spec en Markdown estructurado se convertía en código ejecutable mediante un LLM (Large Language Model, modelo de lenguaje grande): la idea "spec-as-source".
- **Obras o herramientas clave:**
  - Spec Kit (repo github/spec-kit, MIT; commit inicial 21-08-2025; anuncio 02-09-2025)
  - Blog "Spec-driven development with AI: Get started with a new open source toolkit" (Den Delimarsky, 02-09-2025)
  - Spec Kit v1.0.0 (21-08-2026)
  - GitHub Next SpecLang (prototipo de investigación, nov-2023)
- **Por qué está en la lista:** es la herramienta de referencia del SDD con IA por adopción (unas 142k estrellas en GitHub, más de 270 contribuidores y 38 agentes integrados) y por haber fijado el vocabulario del flujo specify/plan/tasks. SpecLang suma un antecedente temprano del enfoque spec-as-source dentro de la misma organización.
- **Verificación:** confirmado. Corregido: unas 142,4k estrellas (no 115k); Spec Kit empezó en agosto de 2025 aunque el blog de lanzamiento es del 02-09-2025; SpecLang no lo creó el equipo de Spec Kit y se presenta como antecedente conceptual, no como predecesor directo. "Constitution" es un paso previo del CLI, no una de las 4 fases del blog de lanzamiento.
- **Enlaces:** [Repositorio github/spec-kit](https://github.com/github/spec-kit) · [Historia de Spec Kit (docs oficiales)](https://github.github.com/spec-kit/history.html) · [GitHub Next – SpecLang](https://githubnext.com/projects/speclang/)
- **Fuentes:** [Spec Kit – History](https://github.github.com/spec-kit/history.html) · [GitHub Blog – Spec-driven development with AI (02-09-2025)](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit) · [github/spec-kit (estrellas y licencia)](https://github.com/github/spec-kit) · [GitHub Next – SpecLang](https://githubnext.com/projects/speclang/)

#### Den Delimarsky

- **Tipo:** persona
- **Afiliación:** ex GitHub (Principal Product Manager al lanzar Spec Kit) y ex Microsoft; hoy se presenta como lead maintainer de MCP (Model Context Protocol).
- **Quién es:** ingeniero y product manager de herramientas para desarrolladores. Trabajó en Microsoft y en GitHub, donde co-creó Spec Kit.
- **Qué aportó:** concibió Spec Kit junto con John Lam (más de 142.000 estrellas). Hizo el commit inicial y dirigió el proyecto hasta enero de 2026. En el post de lanzamiento resumió el cambio de paradigma como el paso de "el código es la fuente de verdad" a "la intención es la fuente de verdad" ("intent is the source of truth"). Divulgó el flujo constitution → specify → clarify → plan → tasks → analyze → implement, y advirtió que las specs "no son una panacea" y que los agentes siguen necesitando supervisión.
- **Obras o herramientas clave:**
  - GitHub Spec Kit, co-creador (commit inicial del 21-08-2025)
  - "Spec-driven development with AI: Get started with a new open source toolkit", GitHub Blog (02-09-2025)
  - "Diving Into Spec-Driven Development With GitHub Spec Kit", Microsoft for Developers (15-09-2025)
  - Post sobre GitHub Spec Kit en den.dev (12-10-2025)
- **Por qué está en la lista:** es la voz del autor de la herramienta de SDD con IA más adoptada. Acuñó la formulación "intent is the source of truth" y fue quien más la divulgó en su etapa fundacional.
- **Verificación:** confirmado. Spec Kit fue una co-creación con John Lam. Su afiliación actual no está confirmada: su página "about" no nombra empleador. Se solapa en parte con la ficha de GitHub.
- **Enlaces:** [Blog den.dev](https://den.dev/) · [GitHub (dend)](https://github.com/dend) · [LinkedIn](https://www.linkedin.com/in/dendeli/) · [Repositorio Spec Kit](https://github.com/github/spec-kit)
- **Fuentes:** [Spec Kit: History](https://github.github.com/spec-kit/history.html) · [GitHub Blog: Spec-driven development with AI (lanzamiento)](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit) · [den.dev: GitHub Spec Kit](https://den.dev/blog/github-spec-kit/) · [Microsoft for Developers: Spec-driven development with Spec Kit](https://developer.microsoft.com/blog/spec-driven-development-spec-kit/) · [den.dev: About](https://den.dev/about/)

#### Kiro (AWS)

- **Tipo:** organización
- **Afiliación:** Amazon Web Services. Caras visibles: Nikhil Swaminathan (Product Lead) y Deepak Singh (VP DevEx & Agents).
- **Quién es:** el IDE (Integrated Development Environment) y CLI agéntico de AWS, basado en VS Code. Se lanzó en preview el 14-07-2025 y alcanzó la GA (General Availability, disponibilidad general) en noviembre de 2025. Hoy también tiene versiones Web y Mobile.
- **Qué aportó:** es la primera gran herramienta comercial que convierte el SDD en el flujo por defecto de un IDE con IA. Cada spec genera tres archivos: requirements.md (user stories con criterios de aceptación en notación EARS (Easy Approach to Requirements Syntax)), design.md (arquitectura, diagramas, interfaces, esquemas) y tasks.md (tareas trazadas a los requisitos). A eso suma steering (memoria de proyecto con product, structure y tech), hooks (agentes disparados por eventos de archivo) y, desde la GA, PBT (property-based testing) para comprobar que el código cumple la spec. Además de las Feature Specs, ofrece Bugfix Specs y Quick Spec.
- **Obras o herramientas clave:**
  - Kiro IDE, preview (14-07-2025)
  - Kiro GA con property-based testing, checkpointing y Kiro CLI (noviembre de 2025)
  - Specs: requirements.md / design.md / tasks.md con criterios EARS; Feature, Bugfix y Quick Spec
  - Post "Requirements analysis: catching requirement bugs before they become code" (12-05-2026)
  - Post "Kiro: one year" (14-07-2026)
- **Por qué está en la lista:** es la herramienta SDD más citada junto a GitHub Spec Kit y Tessl: Birgitta Böckeler la toma como uno de sus tres casos de estudio y la prensa técnica la presentó como el paso "de prompts a specs". Su alcance público es masivo porque la respalda AWS.
- **Verificación:** confirmado. Que fuera "la primera" en llevar el SDD a las herramientas de IA y la cifra de más de 100.000 desarrolladores en 5 días son afirmaciones del propio vendedor. Kiro no tiene blip propio en el Thoughtworks Radar: aparece solo como ejemplo dentro de la entrada de OpenSpec (Assess, vol. 34, abril de 2026). Böckeler lo critica por pesado para cambios pequeños (un bug menor generó 4 user stories y 16 criterios de aceptación). Las charlas de re:Invent no se pudieron verificar.
- **Enlaces:** [Kiro, sitio oficial](https://kiro.dev/) · [Kiro docs: Specs](https://kiro.dev/docs/specs/) · [Kiro blog](https://kiro.dev/blog/)
- **Fuentes:** [Introducing Kiro (Swaminathan y Singh, 14-07-2025)](https://kiro.dev/blog/introducing-kiro/) · [Kiro: one year (Deepak Singh, 14-07-2026)](https://kiro.dev/blog/one-year/) · [InfoWorld: From prompts to specs (17-07-2025)](https://www.infoworld.com/article/4023980/from-prompts-to-specs-awss-kiro-signals-the-next-phase-of-ai-coding-tools.html) · [Böckeler: Understanding Spec-Driven-Development (15-10-2025)](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) · [Thoughtworks Radar: OpenSpec (cita a Kiro como alternativa)](https://www.thoughtworks.com/radar/tools/kiro)

#### Guy Podjarny

- **Tipo:** persona
- **Afiliación:** Tessl (fundador y CEO); antes fundador de Snyk.
- **Quién es:** emprendedor israelí-británico, fundador de Snyk (seguridad para desarrolladores) y luego de Tessl, startup de desarrollo "AI native" financiada con 125 M USD (2024). Co-presenta con Simon Maple el podcast AI Native Dev.
- **Qué aportó:** planteó públicamente el paso de un desarrollo "code-centric" a uno "spec-centric", en el que la especificación es la fuente de verdad y el código pasa a ser un detalle de implementación generado por IA. Desde Tessl llevó esa idea a productos: Tessl Framework, para que los agentes trabajen a partir de specs combinadas con tests, y Spec Registry, specs de librerías open source para evitar alucinaciones de API. Es el principal exponente del nivel "spec-as-source" del SDD.
- **Obras o herramientas clave:**
  - Anuncio de la Serie A de Tessl y visión "spec-centric" del AI Native Software Development (14-11-2024)
  - Charla con GV en GenAI London Meetup: "Five AI realities" (marzo de 2025)
  - Tessl Framework y Tessl Spec Registry (anuncio del 16-09-2025)
  - Podcast AI Native Dev (co-presentador con Simon Maple)
- **Por qué está en la lista:** fue el primero en convertir la idea de "spec como fuente de verdad" en una empresa con mucha financiación y productos específicos de SDD. Böckeler (martinfowler.com) cita a Tessl como uno de los tres referentes de herramientas SDD y el único que explora el nivel spec-as-source.
- **Verificación:** confirmado. Advertencia: en 2026 Tessl se reposicionó como "agent enablement platform" basada en skills y su home ya no menciona SDD ni specs; su aporte al SDD pertenece sobre todo a 2024-2025. Böckeler analiza Tessl pero no nombra a Podjarny.
- **Enlaces:** [Tessl (web oficial)](https://tessl.io/) · [Tessl Community / AI Native Dev podcast](https://tessl.io/community)
- **Fuentes:** [Tessl — Announcing our Series A (14-11-2024)](https://www.tessl.io/blog/announcing-our-series-a-for-ai-native-software-development) · [Tessl — Announcing Tessl's products to unlock the power of agents (16-09-2025)](https://tessl.io/blog/announcing-tessls-products-to-unlock-the-power-of-agents/) · [Tessl — Tessl launches spec-driven framework and registry (23-09-2025)](https://tessl.io/blog/tessl-launches-spec-driven-framework-and-registry) · [GV — Five AI realities with Tessl's Guy Podjarny (27-03-2025)](https://gv.com/news/five-ai-realities-with-tessl-guy-podjarny) · [Böckeler — Understanding Spec-Driven-Development (15-10-2025)](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)

#### Tabish Bidiwale (OpenSpec / Fission AI)

- **Tipo:** persona
- **Afiliación:** Fission AI / OpenSpec (fundador; lead maintainer de OpenSpec).
- **Quién es:** desarrollador radicado en San Francisco, creador y lead maintainer de OpenSpec, el framework open source de spec-driven development publicado bajo la organización Fission-AI en GitHub. YC (Y Combinator) lo presenta como fundador de OpenSpec.
- **Qué aportó:** creó OpenSpec, un framework ligero de SDD para asistentes de código con IA. Cada cambio vive en su propia carpeta (openspec/changes/) con proposal.md, specs/, design.md y tasks.md, y al archivarlo se actualizan las specs vigentes: se especifica el cambio incremental sobre un sistema existente. El flujo tiene cinco comandos: explore, propose, apply, verify y archive. Es una de las alternativas más populares a GitHub Spec Kit.
- **Obras o herramientas clave:**
  - OpenSpec (repo Fission-AI/OpenSpec, MIT, unas 72,7k estrellas en GitHub a oct-2026; v1.14.2)
  - openspec.dev, web y documentación del framework
  - Lanzamiento en YC Launches: "OpenSpec: the spec framework for coding agents"
- **Por qué está en la lista:** es el creador y principal mantenedor de una de las dos herramientas SDD con IA más adoptadas (decenas de miles de estrellas y más de 265k desarrolladores al mes según su web), que aparece en comparativas independientes frente a Spec Kit.
- **Verificación:** confirmado. No se pudo verificar el lote de YC. Los términos "brownfield-first" y "delta specs" son etiquetas de terceros, no del proyecto. La relevancia es alta para la herramienta y suficiente para la persona, que tiene poca presencia pública.
- **Enlaces:** [OpenSpec (GitHub)](https://github.com/Fission-AI/OpenSpec) · [openspec.dev](https://openspec.dev/) · [Perfil GitHub TabishB](https://github.com/TabishB)
- **Fuentes:** [OpenSpec MAINTAINERS.md](https://github.com/Fission-AI/OpenSpec/blob/main/MAINTAINERS.md) · [YC Launches — OpenSpec](https://www.ycombinator.com/launches/Pdc-openspec-the-spec-framework-for-coding-agents) · [Fission-AI/OpenSpec (README)](https://github.com/Fission-AI/OpenSpec) · [Kai Hendry — Comparing SDD Frameworks (18-05-2026)](https://dabase.com/blog/2026/sdd-framework-comparison/)

#### BMad Code (BMAD-METHOD)

- **Tipo:** organización
- **Afiliación:** BMad Code, LLC / organización de GitHub bmad-code-org. Según Augment Code, el creador es Brian Madison ("BMad").
- **Quién es:** la organización detrás de BMAD-METHOD, un marco open source (MIT) de agentes y skills para Claude Code, Cursor y otras herramientas. Lleva una idea o un cambio por fases de análisis, planificación, arquitectura e implementación.
- **Qué aportó:** popularizó el desarrollo con agentes por rol (analista, PM (Product Manager), arquitecto, desarrollador, UX (User Experience), tech writer), donde cada fase deja un artefacto en Markdown que es la fuente de contexto de la siguiente. El brief alimenta el PRD (Product Requirements Document), el PRD la arquitectura, y la arquitectura los story files ({epic}.{story}.{título}.md), que dan al agente desarrollador el contexto completo de una unidad de trabajo, junto con project-context.md. Es una de las variantes de SDD más adoptadas por la comunidad.
- **Obras o herramientas clave:**
  - BMAD-METHOD (repositorio de GitHub, licencia MIT; unas 54,4k estrellas en octubre de 2026)
  - BMad Method v6 (estable v6.12) y v7 (alfa, 2026): skills y ciclo Clarify / Plan / Build and verify / Learn and adjust
  - Documentación oficial docs.bmad-method.org
  - Canal de YouTube @BMadCode
- **Por qué está en la lista:** es uno de los marcos de SDD con IA de más tracción y lleva la idea de "especificación como contexto" a una cadena completa de artefactos (PRD, arquitectura, stories) que consumen los agentes. Guías independientes, como la de Augment Code, lo analizan y lo comparan con OpenSpec.
- **Verificación:** confirmado. El nombre de Brian Madison solo lo da Augment Code; ni el repo ni la documentación oficial nombran a una persona. Los roles cambiaron (Scrum Master y QA se fusionaron en Developer; la v7 añade un Product Owner). No se pudo comprobar que aparezca "en todas las comparativas" junto a Spec Kit y Kiro.
- **Enlaces:** [GitHub - bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) · [Documentación oficial BMad Method](https://docs.bmad-method.org/)
- **Fuentes:** [GitHub - bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) · [Augment Code - guía BMAD method](https://www.augmentcode.com/guides/bmad-method-ai-development) · [Documentación oficial BMad Method](https://docs.bmad-method.org/)

#### Jesse Vincent (Superpowers)

- **Tipo:** persona
- **Afiliación:** Prime Radiant (desde 2025); antes fundador de Best Practical y Keyboardio.
- **Quién es:** desarrollador y emprendedor de Berkeley (California). Fundó Best Practical (2001) y Keyboardio (2012). Es el autor de Superpowers, el framework de skills para agentes de código con más adopción de la comunidad.
- **Qué aportó:** Superpowers convierte un flujo spec-first en el comportamiento por defecto del agente. Empieza con una fase de brainstorming en la que el agente pregunta hasta extraer una spec de la conversación y la muestra en fragmentos cortos para que el humano la apruebe. Con el diseño aprobado, "writing-plans" divide el trabajo en tareas de 2 a 5 minutos con rutas de archivo y pasos de verificación. Después, "subagent-driven-development" asigna cada tarea a un subagente nuevo y aplica una revisión en dos etapas: primero el cumplimiento de la spec y después la calidad del código. Todo con TDD (Test-Driven Development) red-green-refactor. No usa la etiqueta "SDD", pero en la práctica implementa especificar → planificar → tareas → implementar con verificación contra la spec. Funciona en Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot CLI y otros agentes.
- **Obras o herramientas clave:**
  - Superpowers (github.com/obra/superpowers, 2025-2026; MIT; unas 303k estrellas)
  - Post "Superpowers: How I'm using coding agents in October 2025" (blog.fsck.com, 09-10-2025)
  - Superpowers 6 (15-06-2026) y 6.4 (21-09-2026)
  - Post "What a year" (09-10-2026): aniversario y Superpowers 7.0, con el brainstorming rehecho
- **Por qué está en la lista:** es la señal de comunidad más fuerte de todo el ecosistema de flujos spec-first para agentes. Según su autor (09-10-2026): cerca de 300k estrellas (el 12.º proyecto más popular de GitHub por estrellas), el plugin de terceros n.º 1 de Claude Code con más de 1,1 M de instalaciones, y presencia en el marketplace oficial de Anthropic. Su revisión explícita de "spec compliance" lo sitúa dentro del SDD práctico aunque no use el término.
- **Verificación:** confirmado y añadido en la revisión de completitud, en sustitución de CodeSpeak. Las cifras de adopción las da el propio autor; las estrellas se comprobaron en el repo.
- **Enlaces:** [Superpowers (GitHub)](https://github.com/obra/superpowers) · [Blog de Jesse Vincent (Massively Parallel Procrastination)](https://blog.fsck.com/) · [Perfil de GitHub (obra)](https://github.com/obra)
- **Fuentes:** [README de Superpowers](https://raw.githubusercontent.com/obra/superpowers/main/README.md) · [Superpowers: How I'm using coding agents in October 2025 (09-10-2025)](https://blog.fsck.com/2025/10/09/superpowers/) · [What a year (09-10-2026)](https://blog.fsck.com/2026/10/09/what-a-year/) · [Repositorio en GitHub](https://github.com/obra/superpowers)

#### GSD (Get Shit Done) / GSD Core

- **Tipo:** organización (proyecto open source)
- **Afiliación:** proyecto open source con licencia MIT. El repo original, gsd-build/get-shit-done, es de TÂCHES (glittercowboy en GitHub) y se archivó el 26-06-2026. El desarrollo sigue como GSD Core en la organización Open GSD (open-gsd/gsd-core, creada el 22-05-2026).
- **Quién es:** framework open source de flujo de trabajo para agentes de código, nacido para Claude Code (primer commit de diciembre de 2025). Su autor original firma como TÂCHES y su perfil lo sitúa en Costa Rica, con la bio "Music + Code"; el nombre real "Lex Christopherson" solo consta en fuentes secundarias. GSD Core funciona hoy con Claude Code, OpenCode, Codex, Cursor, Copilot, Windsurf y otros agentes.
- **Qué aportó:** se define como un sistema ligero de meta-prompting, ingeniería de contexto y spec-driven development. Cada fase de un milestone sigue el ciclo discuss → plan → execute → verify → ship: se discuten las decisiones, se arma un plan verificado que quepa en una ventana de contexto limpia, se ejecuta en oleadas paralelas con subagentes de contexto fresco, se verifica lo construido y se cierra con un PR (pull request) y el archivo de la fase. Mantiene el estado entre sesiones con artefactos persistentes (STATE.md, CONTEXT.md) y un commit atómico por tarea. Su aporte distintivo es unir la planificación por specs con el aislamiento de contexto para evitar el "context rot". Es SDD spec-first: la spec funciona como documento de arranque, no como contrato vivo ni como fuente de verdad.
- **Obras o herramientas clave:**
  - get-shit-done (gsd-build/get-shit-done): unas 64,2k estrellas, archivado el 26-06-2026; se instala con npx get-shit-done-cc
  - GSD Core (open-gsd/gsd-core, paquete npm @opengsd/gsd-core): unas 10,8k estrellas
  - gsd-2 (gsd-build/gsd-2): meta-prompting para agentes autónomos de larga duración, archivado
- **Por qué está en la lista:** es una de las herramientas SDD comunitarias más adoptadas de 2025-2026. Las comparativas de 2026 (SoftwareSeni, Kai Hendry, Augment Code, CodeMySpec) la ponen junto a Spec Kit, OpenSpec, BMAD y Superpowers y la presentan como "la alternativa ligera a BMAD". Representa la vertiente del SDD centrada en gestionar el contexto del agente; su peso es de adopción práctica, no de aporte teórico.
- **Verificación:** confirmado, con importancia media; añadido en la segunda pasada. Las ~64k estrellas son del repo original, archivado el 26-06-2026; GSD Core (open-gsd) tiene unas 10,8k. No está confirmado que la 1.7.0 sea la última versión. El autor no tiene escritos ni charlas propios sobre SDD y el proyecto cambió de manos en junio de 2026. Augment Code dice que su núcleo es la ingeniería de contexto, CodeMySpec lo clasifica como "spec-first scaffolding" y Kai Hendry lo critica por "burocrático" y por gastar muchos tokens.
- **Enlaces:** [gsd-build/get-shit-done (GitHub, archivado)](https://github.com/glittercowboy/get-shit-done) · [open-gsd/gsd-core (GitHub)](https://github.com/open-gsd/gsd-core) · [Perfil de glittercowboy / TÂCHES (GitHub)](https://github.com/glittercowboy)
- **Fuentes:** [gsd-build/get-shit-done (GitHub)](https://github.com/glittercowboy/get-shit-done) · [open-gsd/gsd-core (GitHub)](https://github.com/open-gsd/gsd-core) · [Hora de Codar: O que é o get-shit-done (GSD) e o que ele não é (25-08-2026)](https://horadecodar.com.br/?p=44090) · [Augment Code: GSD, stars, spec-driven (abril de 2026)](https://www.augmentcode.com/learn/gsd-stars-spec-driven) · [Kai Hendry: Comparing SDD Frameworks (18-05-2026)](https://dabase.com/blog/2026/sdd-framework-comparison/) · [SoftwareSeni: The 30-Plus Framework Landscape (29-05-2026)](https://www.softwareseni.com/the-30-plus-framework-landscape-navigating-spec-driven-development-options-in-2026) · [CodeMySpec: Spec-Driven Development in 2026 (03-06-2026)](https://codemyspec.com/blog/spec-driven-development)

#### JetBrains (Junie / JetBrains AI)

- **Tipo:** organización
- **Afiliación:** JetBrains. Caras visibles en SDD: Anton Arhipov (blog de Junie), Paul Everitt (curso de DeepLearning.AI y livestreams) y Arun Gupta (vicepresidente de Developer Experience).
- **Quién es:** empresa checa creadora de los IDE IntelliJ IDEA, PyCharm y otros, del agente de código Junie y de JetBrains AI Assistant.
- **Qué aportó:** difunde el SDD con IA entre los usuarios de sus IDE. (1) Guía de Anton Arhipov en el blog de Junie (octubre de 2025), "How to Use a Spec-Driven Approach for Coding with AI": escribir los requisitos de alto nivel en requirements.md, pedir a Junie un plan.md revisable antes de tocar código y convertirlo en un tasks.md que se ejecuta y marca paso a paso, con reglas en .junie/guidelines.md. El prompt reutilizable, publicado en un gist, pide criterios de aceptación WHEN/THEN y que cada tarea quede enlazada a su requisito y al punto del plan. (2) El plan mode de Junie CLI escribe un documento de diseño (requisitos, diseño técnico, testing y pasos de entrega) que se revisa antes de implementar. (3) El livestream "Spec-Driven AI Development: Turning Requirements into Reliable Code" (IntelliJ IDEA + JetBrains AI) parte de documentos de requisitos, genera plan, código y tests, y valida el resultado contra la spec original. (4) El curso corto de DeepLearning.AI "Spec-Driven Development with Coding Agents", hecho con JetBrains y dado por Paul Everitt (2026), enseña la constitución del proyecto, las specs por feature, el ciclo plan-implement-verify, el SDD en código legado y el empaquetado del flujo como agent skill. (5) Arun Gupta sostuvo en febrero de 2026 que el SDD "becomes the only viable approach for regulated industries".
- **Obras o herramientas clave:**
  - "How to Use a Spec-Driven Approach for Coding with AI" (blog de Junie, Anton Arhipov, octubre de 2025)
  - spec-driven-development-with-junie.md (gist con el prompt de Anton Arhipov)
  - Junie CLI plan mode (documentación)
  - Livestream "Spec-Driven AI Development: Turning Requirements into Reliable Code" (2025)
  - Curso "Spec-Driven Development with Coding Agents" (DeepLearning.AI + JetBrains, Paul Everitt, 2026)
- **Por qué está en la lista:** es uno de los grandes proveedores de IDE que adoptó y enseña el SDD con IA de forma explícita, y su curso con DeepLearning.AI es una de las vías de formación en SDD de más alcance. Su enfoque es más bien spec-first (requisitos → plan → tareas) que spec como fuente de verdad viva, y no define una herramienta ni un formato propio de referencia.
- **Verificación:** confirmado, con importancia media; añadido en la tercera pasada. La documentación del plan mode de Junie CLI no habla de "spec" ni de SDD: lo llama "design document" y es un plan previo a implementar, no una spec que se mantenga. Según una búsqueda, la propia JetBrains no estandariza requirements.md/plan.md/tasks.md como funciones del producto. La página del livestream no muestra la fecha de la sesión. No se verificó la fecha de disponibilidad general de Junie y se sacó de la ficha. Se solapa con la mención honorífica de Paul Everitt.
- **Enlaces:** [JetBrains Blog: How to Use a Spec-Driven Approach for Coding with AI](https://blog.jetbrains.com/junie/2025/10/how-to-use-a-spec-driven-approach-for-coding-with-ai/) · [Junie CLI: plan mode](https://junie.jetbrains.com/docs/junie-cli-plan-mode.html) · [DeepLearning.AI: Spec-Driven Development with Coding Agents](https://www.deeplearning.ai/short-courses/spec-driven-development-with-coding-agents/) · [JetBrains livestream: Spec-Driven AI Development](https://info.jetbrains.com/jetbrains-livestream-november20-2025.html)
- **Fuentes:** [JetBrains Blog (Anton Arhipov): How to Use a Spec-Driven Approach for Coding with AI](https://blog.jetbrains.com/junie/2025/10/how-to-use-a-spec-driven-approach-for-coding-with-ai/) · [Gist de Anton Arhipov: spec-driven-development-with-junie.md](https://gist.github.com/antonarhipov/4e89f27b38eab1fa5719a2c169969f7c) · [Junie CLI plan mode (docs)](https://junie.jetbrains.com/docs/junie-cli-plan-mode.html) · [JetBrains livestream: Spec-Driven AI Development: Turning Requirements into Reliable Code](https://info.jetbrains.com/jetbrains-livestream-november20-2025.html) · [DeepLearning.AI: Spec-Driven Development with Coding Agents (con JetBrains, Paul Everitt)](https://www.deeplearning.ai/short-courses/spec-driven-development-with-coding-agents/) · [TFIR: AI predictions 2026 (Arun Gupta, JetBrains, sobre SDD)](https://tfir.io/ai-predictions-2026-quality-over-speed/)

### Teoría y divulgación

#### Birgitta Böckeler

- **Tipo:** persona
- **Afiliación:** Thoughtworks (Distinguished Engineer, experta en entrega asistida por IA); autora de la serie "Exploring Gen AI" en martinfowler.com.
- **Quién es:** ingeniera alemana con más de 20 años como desarrolladora, arquitecta y líder técnica. Es Distinguished Engineer en Thoughtworks, especializada en desarrollo de software asistido por IA.
- **Qué aportó:** escribió el análisis comparativo de referencia sobre las herramientas de SDD (Kiro, spec-kit y Tessl) y propuso una taxonomía en tres niveles: spec-first (el spec se escribe antes de programar la tarea), spec-anchored (el spec se conserva para evolucionar la funcionalidad) y spec-as-source (el spec es el artefacto principal y los humanos solo editan el spec). Su mirada es crítica y no depende de ningún vendedor. También divulga el tema en el podcast tecnológico de Thoughtworks.
- **Obras o herramientas clave:**
  - "Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl" (martinfowler.com, 15-10-2025)
  - Serie "Exploring Generative AI" en martinfowler.com
  - Podcast de Thoughtworks "What is spec-driven development?" (host, con Laura Tacho, 28-05-2026)
- **Por qué está en la lista:** su artículo es el texto más citado para entender y comparar las herramientas de SDD, y su taxonomía spec-first / spec-anchored / spec-as-source aparece en la literatura posterior (por ejemplo, en el arXiv 2602.00180). Aporta una perspectiva independiente desde una consultora cuyo Radar puso el SDD en "Assess" en noviembre de 2025.
- **Verificación:** confirmado. El arXiv 2602.00180 usa los tres niveles pero su abstract no la cita. La página del Radar no la nombra como autora de la entrada.
- **Enlaces:** [Artículo en martinfowler.com](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) · [Thoughtworks Technology Podcast – What is spec-driven development?](https://www.thoughtworks.com/insights/podcasts/technology-podcasts/what-is-spec-driven-development)
- **Fuentes:** [Understanding Spec-Driven-Development (15-10-2025)](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) · [Thoughtworks Technology Radar – Spec-driven development (Assess, 05-11-2025)](https://www.thoughtworks.com/radar/techniques/spec-driven-development) · [Thoughtworks podcast (28-05-2026)](https://www.thoughtworks.com/insights/podcasts/technology-podcasts/what-is-spec-driven-development) · [arXiv 2602.00180 – Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants](https://arxiv.org/abs/2602.00180)

#### Sean Grove

- **Tipo:** persona
- **Afiliación:** fundador de Linzumi (Y Combinator); antes trabajó en los equipos de post-training y alineamiento de OpenAI.
- **Quién es:** ingeniero y emprendedor estadounidense. Fue investigador de alineamiento en OpenAI y hoy dirige Linzumi, un chat de equipo con agentes de código dentro de cada canal.
- **Qué aportó:** formuló el manifiesto más citado del SDD con IA en "The New Code" (AI Engineer World's Fair 2025). Sostiene que la especificación es el artefacto valioso y que el código es solo una "proyección con pérdida" de la intención; que quien escribe la spec es ahora el programador, y que hay que dejar de tirar los prompts y conservar specs versionadas y verificables. Pone como ejemplo el Model Spec de OpenAI, un documento Markdown vivo cuyas cláusulas llevan ejemplos que funcionan como tests.
- **Obras o herramientas clave:**
  - "The New Code" / "Specifications Are the New Code", charla en la AI Engineer World's Fair 2025
  - OpenAI Model Spec (2025), en cuya autoría participó según ThursdAI; repositorio público openai/model_spec
  - Linzumi (2026), startup de agentes de código colaborativos
- **Por qué está en la lista:** su charla es la referencia teórica más citada del SDD con IA y la recogen medios como The Decoder y HackerNoon/Tessl. Dio el marco conceptual de "la spec como nuevo código fuente".
- **Verificación:** confirmado. Su salida de OpenAI, su coautoría del Model Spec y las más de 1,2 M de vistas solo constan en ThursdAI. Su obra en SDD es una sola charla, no una herramienta.
- **Enlaces:** [X: @sgrove](https://x.com/sgrove) · [Linzumi](https://linzumi.com) · [Charla "The New Code" en YouTube](https://www.youtube.com/watch?v=8rABwKRsec4) · [OpenAI Model Spec (GitHub)](https://github.com/openai/model_spec)
- **Fuentes:** [AI Engineer: Specifications Are the New Code](https://ai.engineer/talks/specifications-are-the-new-code) · [The Decoder: Code is just a lossy projection of intent (12-07-2025)](https://the-decoder.com/code-is-just-a-lossy-projection-of-intent-according-to-openai-researcher-sean-grove/) · [HackerNoon (Tessl): OpenAI's new code could make spec authors the new rockstars of dev (15-09-2025)](https://hackernoon.com/openais-new-code-could-make-spec-authors-the-new-rockstars-of-dev) · [ThursdAI: perfil de Sean Grove](https://thursdai.news/guests/sgrove)

#### Marc Brooker

- **Tipo:** persona
- **Afiliación:** Amazon Web Services (VP / Distinguished Engineer).
- **Quién es:** ingeniero de AWS en Seattle que trabaja en IA agéntica, sobre todo en seguridad y políticas para agentes. Antes trabajó en EC2, EBS, bases de datos y serverless.
- **Qué aportó:** es el principal teórico público del SDD en AWS y Kiro. Define la especificación como un "super prompt" versionado y legible por humanos, que sirve de referencia a los agentes y les permite abordar tareas más grandes sin perder el rumbo. Conecta el SDD con la tradición escrita de Amazon (press releases "working backwards", documentos de diseño y especificaciones formales en TLA+ y P). Sostiene que el SDD no es waterfall: la spec es un artefacto vivo que se itera, y el código fluye de ella.
- **Obras o herramientas clave:**
  - "Kiro and the future of AI spec-driven software development" (blog de Kiro, 15-07-2025)
  - "Spec Driven Development isn't Waterfall" (blog personal, 09-04-2026)
  - SE Radio 710: "Marc Brooker on Spec-Driven AI Dev" (podcast, 04-03-2026)
  - "Agentic software development hypothesis" (blog, 20-05-2026)
  - "Use of Formal Methods at Amazon Web Services" (2014) y "How Amazon Web Services Uses Formal Methods" (2015), sobre TLA+ en AWS
  - "Formal Methods: Just Good Engineering Practice?" (blog, 17-04-2024)
- **Por qué está en la lista:** une la tradición de los métodos formales en AWS con el SDD moderno con IA. Sus textos y entrevistas son una referencia conceptual sobre Kiro y sobre el debate SDD contra waterfall.
- **Verificación:** confirmado. El episodio de Real Python no se pudo verificar (error 403) y queda fuera.
- **Enlaces:** [Marc's Blog](https://brooker.co.za/blog/) · [Publicaciones y vídeos](https://brooker.co.za/blog/publications.html) · [X/Twitter @MarcJBrooker](https://twitter.com/MarcJBrooker) · [Mastodon](https://fediscience.org/@marcbrooker)
- **Fuentes:** [Kiro blog: Kiro and the future of AI spec-driven software development](https://kiro.dev/blog/kiro-and-the-future-of-software-development/) · [Spec Driven Development isn't Waterfall](https://brooker.co.za/blog/2026/04/09/waterfall-vs-spec.html) · [SE Radio 710](https://se-radio.net/2026/03/se-radio-710-marc-brooker-on-spec-driven-ai-dev/) · [Formal Methods: Just Good Engineering Practice?](https://brooker.co.za/blog/2024/04/17/formal.html) · [Agentic software development hypothesis](https://brooker.co.za/blog/2026/05/20/hypothesis.html)

#### Patrick Debois

- **Tipo:** persona
- **Afiliación:** Tessl / comunidad AI Native Dev (autor y ponente); blog jedi.be.
- **Quién es:** ingeniero y divulgador belga al que se atribuye haber acuñado el término "DevOps". Organizó los primeros DevOpsDays (2009) y es coautor de The DevOps Handbook. Desde 2025 se dedica al desarrollo "AI native".
- **Qué aportó:** formuló "los 4 patrones del desarrollo AI native". Uno de ellos, "de la implementación a la intención", describe el paso a un desarrollo guiado por especificaciones en el que los requisitos importan más que el código. En su guía "10 cosas que hay que saber sobre las specs" define qué es una spec frente a un prompt, propone una tipología de specs y trata los límites de contexto, la regeneración, la compartición de specs, la revisión humana, el legado y la madurez del enfoque. También reunió y difundió las charlas sobre SDD de Devoxx 2025.
- **Obras o herramientas clave:**
  - "The 4 Patterns of AI Native Development" (charla y post, jedi.be, junio de 2025)
  - Serie "Four Patterns of AI Native Dev: From Implementation to Intent" (abril de 2025)
  - "Spec-Driven Development: 10 things you need to know about specs" (Tessl, 29-10-2025)
  - "Four Patterns of AI Native Development", InfoQ Dev Summit Munich (publicado el 09-03-2026)
  - "Devoxx 2025: 8 Talks on Spec-Driven Development" (jedi.be, 21-10-2025)
  - Coautor de The DevOps Handbook
- **Por qué está en la lista:** es una de las voces más citadas para explicar el SDD con IA de forma práctica: una guía de referencia sobre specs y un marco conceptual (de implementación a intención) presentado en InfoQ y Devoxx, con el respaldo de su reconocimiento previo en DevOps.
- **Verificación:** confirmado. No hay un cargo exacto en Tessl verificado: aparece como autor de su blog. La charla verificada es la de InfoQ Dev Summit Munich, no la de AI Engineer.
- **Enlaces:** [jedi.be (blog)](https://www.jedi.be/) · [Comunidad AI Native Dev (Tessl)](https://tessl.io/community) · [Vídeo: The 4 Patterns of AI Native Development](https://www.youtube.com/watch?v=9u6xvcNJaxc)
- **Fuentes:** [Tessl — Spec-Driven Development: 10 things you need to know about specs](https://tessl.io/blog/spec-driven-development-10-things-you-need-to-know-about-specs/) · [jedi.be — The 4 Patterns of AI Native Development (talk)](https://jedi.be/blog/2025/talk-2025-four-patterns-of-ai-native-development/) · [jedi.be — From Implementation to Intent](https://jedi.be/blog/2025/from-implementation-to-intent/) · [InfoQ — Four Patterns of AI Native Development](https://infoq.com/presentations/patterns-ai-native-development/) · [jedi.be — Devoxx 2025: 8 Talks on Spec-Driven Development](https://jedi.be/blog/2025/devoxx-2025-spec-driven-development-talks/) · [jedi.be — 10 Things (repost)](https://jedi.be/blog/2025/spec-driven-development-10-things-you-need-to-know/)

#### Addy Osmani

- **Tipo:** persona
- **Afiliación:** Anthropic (Member of Technical Staff, Claude Code); antes Google durante más de 14 años (último cargo: Director en Google Cloud AI); autor de O'Reilly.
- **Quién es:** ingeniero y autor muy conocido en la comunidad web y de ingeniería con IA. Escribió libros como "Beyond Vibe Coding" y "Learning JavaScript Design Patterns".
- **Qué aportó:** escribió una de las guías prácticas más citadas para escribir specs para agentes de IA. Propone la spec como documento estructurado al estilo PRD o SRS (Software Requirements Specification), con seis áreas (comandos, testing, estructura, estilo, git, límites), límites en tres niveles (Always / Ask first / Never) y viva y versionada como fuente de verdad. Además publica una skill reutilizable de spec-driven development (Specify → Plan → Tasks → Implement con revisión humana) en su repositorio agent-skills.
- **Obras o herramientas clave:**
  - "How to write a good spec for AI agents", addyosmani.com (13-01-2026); republicado en O'Reilly Radar (20-02-2026)
  - addyosmani/agent-skills, skill "spec-driven-development" (repositorio con unas 109.000 estrellas)
  - "Beyond Vibe Coding" (libro)
- **Por qué está en la lista:** es la referencia práctica más difundida sobre cómo escribir specs para agentes, con mucho alcance (O'Reilly, más de 100.000 estrellas en agent-skills); su skill de SDD está disponible en registros como Tessl.
- **Verificación:** confirmado. Corregida la afiliación: ya no está en Google. Es un divulgador práctico, no un creador de metodología original.
- **Enlaces:** [Web y blog](https://addyosmani.com/) · [X](https://twitter.com/addyosmani) · [GitHub](https://github.com/addyosmani) · [LinkedIn](https://www.linkedin.com/in/addyosmani/)
- **Fuentes:** [How to write a good spec for AI agents (blog)](https://addyosmani.com/blog/good-spec/) · [O'Reilly Radar: How to write a good spec for AI agents](https://oreilly.com/radar/how-to-write-a-good-spec-for-ai-agents) · [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) · [Tessl registry: spec-driven-development skill](https://tessl.io/registry/skills/github/addyosmani/agent-skills/spec-driven-development)

#### Drew Breunig

- **Tipo:** persona
- **Afiliación:** independiente (dbreunig.com); CEO y cofundador de Cmpnd (trabaja en DSPy); editor de "The Context Engineering Handbook" (O'Reilly).
- **Quién es:** escritor y tecnólogo que trabaja entre la antropología cultural, la informática y los medios. Escribe sobre IA, construye herramientas para ingenieros de IA y es conocido por sus textos sobre context engineering.
- **Qué aportó:** propone el SDD como especificación más tests de conformidad, independiente del lenguaje. whenwords lo demuestra: es una librería sin código (solo SPEC.md, tests en YAML y un prompt de instalación) que los agentes implementan en Ruby, Python, Rust, Elixir, Swift, PHP o Bash. Además formula el "Spec Driven Development Triangle": spec, tests y código deben mantenerse sincronizados en un bucle de retroalimentación, no en una cascada. Para eso propone Plumb, que extrae decisiones de los commits y de las trazas de los agentes.
- **Obras o herramientas clave:**
  - whenwords, librería sin código (enero de 2026)
  - "The Rise of Spec Driven Development" (06-02-2026)
  - "Learnings from a No-Code Library: Keeping the Spec Driven Development Triangle in Sync" (04-03-2026), versión escrita de su charla en MLOps Community "Coding Agents" (03-03-2026)
  - Plumb, prueba de concepto de sincronización spec-tests-código (2026)
- **Por qué está en la lista:** aporta un modelo conceptual propio y citado (el triángulo spec-tests-código) y un experimento muy difundido (whenwords, unas 1.300 estrellas, amplificado por Simon Willison). Es útil para estudiar cómo se verifica que el código cumple la spec.
- **Verificación:** confirmado. Corregido: el tests.yaml tiene unos 123 casos repartidos en 5 funciones, no "unos 750 tests". Es un divulgador influyente pero secundario frente a Böckeler o los creadores de herramientas.
- **Enlaces:** [Blog dbreunig.com](https://www.dbreunig.com/) · [GitHub dbreunig](https://github.com/dbreunig) · [Repo whenwords](https://github.com/dbreunig/whenwords)
- **Fuentes:** [The Rise of Spec Driven Development (06-02-2026)](https://www.dbreunig.com/2026/02/06/the-rise-of-spec-driven-development.html) · [The Spec Driven Development Triangle (04-03-2026)](https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html) · [Simon Willison: A Software Library with No Code (10-01-2026)](https://simonwillison.net/2026/jan/10/a-software-library-with-no-code) · [github.com/dbreunig/whenwords](https://github.com/dbreunig/whenwords)

#### Harper Reed

- **Tipo:** persona
- **Afiliación:** 2389.ai (CEO); blog harper.blog.
- **Quién es:** tecnólogo estadounidense: fue CTO de la campaña de reelección de Obama (2012) y de Threadless, y cofundó Modest, adquirida por PayPal. Escribe desde hace unos 24 años en harper.blog.
- **Qué aportó:** publicó en febrero de 2025 uno de los primeros flujos de trabajo populares con "spec primero" para programar con LLMs. Un LLM entrevista al desarrollador (de a una pregunta) hasta producir un spec.md; un modelo de razonamiento lo convierte en un plan de prompts pequeños guiados por tests (prompt_plan.md) y en una checklist (todo.md) que mantiene el estado entre sesiones; luego un agente o LLM ejecuta paso a paso. Es la misma estructura especificar → planificar → tareas → implementar que formalizaron después Kiro y Spec Kit.
- **Obras o herramientas clave:**
  - "My LLM codegen workflow atm" (harper.blog, 16-02-2025)
- **Por qué está en la lista:** es el antecedente práctico más citado del flujo spec → plan → tareas con IA, anterior a las herramientas SDD de 2025, y Simon Willison lo amplificó ("very well-thought out").
- **Verificación:** confirmado, con menos peso que los creadores de herramientas: su aporte es un post, no una metodología ni una herramienta. Que fuera "muy imitado" o el antecedente directo de Kiro y Spec Kit es una interpretación; la reseña de Böckeler no lo cita.
- **Enlaces:** [harper.blog](https://harper.blog/) · [harperreed.com](https://harperreed.com/)
- **Fuentes:** [Harper Reed — My LLM codegen workflow atm (16-02-2025)](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/) · [Simon Willison — enlace y comentario (21-02-2025)](https://simonwillison.net/2025/Feb/21/my-llm-codegen-workflow-atm/) · [harperreed.com — biografía y cronología](https://harperreed.com/)

### Investigación académica

#### Shuvendu K. Lahiri

- **Tipo:** persona
- **Afiliación:** MSR (Microsoft Research) Redmond, grupo RiSE (Research in Software Engineering); Senior Principal Researcher.
- **Quién es:** investigador de Microsoft Research. Trabaja en métodos formales (verificación, análisis de programas, síntesis) y en su combinación con LLMs para un desarrollo de software fiable.
- **Qué aportó:** encabeza la línea de "user-intent formalization": usar LLMs para traducir intención informal (lenguaje natural, docstrings, documentación de APIs) en especificaciones verificables, como tests, postcondiciones o specs en Dafny/F\*, y medir su calidad con métricas inspiradas en mutation testing. En 2026 formuló la "intent formalization" como gran desafío para programar con agentes de IA de forma fiable, que es el fundamento académico del SDD: especificaciones precisas y comprobables para el código que generan los agentes.
- **Obras o herramientas clave:**
  - TiCoder: "Interactive Code Generation via Test-Driven User-Intent Formalization" (2022)
  - nl2postcond: "Can Large Language Models Transform Natural Language Intent into Formal Method Postconditions?" (FSE (Foundations of Software Engineering) 2024)
  - "Evaluating LLM-driven User-Intent Formalization for Verification-Aware Languages" (FMCAD (Formal Methods in Computer-Aided Design) 2024)
  - Charla "AI for Program Specifications" (UW PLSE, 25-02-2025)
  - "Intent Formalization: A Grand Challenge for Reliable Coding in the Age of AI Agents" (arXiv 2603.17150, marzo de 2026)
  - Keynote en SpecOps 2026: "Intent Formalization: Assessing the Quality of AI-Generated Formal Program Specifications" (06-10-2026)
- **Por qué está en la lista:** es el investigador más identificado con la base formal del SDD con IA: cómo convertir la intención en especificaciones verificables para el código que generan los LLMs. Dio la keynote del primer workshop académico dedicado al SDD (SpecOps 2026, colocalizado con ISSTA/SPLASH en Oakland).
- **Verificación:** confirmado. Se retiró de la ficha su supuesto papel en el programa "Trusted AI-assisted Programming" porque su página de MSR no lo menciona. Su perfil es más de investigador que de figura pública.
- **Enlaces:** [Perfil en Microsoft Research](https://www.microsoft.com/en-us/research/people/shuvendu/) · [arXiv 2603.17150 – Intent Formalization](https://arxiv.org/abs/2603.17150)
- **Fuentes:** [arXiv 2603.17150](https://arxiv.org/abs/2603.17150) · [arXiv 2406.09757 (FMCAD 2024)](https://arxiv.org/abs/2406.09757v2) · [arXiv 2310.01831 – nl2postcond (FSE 2024)](https://arxiv.org/abs/2310.01831) · [MSR – TiCoder](https://www.microsoft.com/en-us/research/publication/interactive-code-generation-via-test-driven-user-intent-formalization/) · [SpecOps 2026 – keynotes](https://conf.researchr.org/home/specops-2026) · [UW PLSE colloquium (25-02-2025)](https://uwplse.org/colloquia/20250225-shuvendu-lahiri.html) · [Perfil MSR](https://www.microsoft.com/en-us/research/people/shuvendu/)

#### Estudio de Carnegie Mellon sobre el SDD en la práctica (Shyam Agarwal, Bogdan Vasilescu y equipo)

- **Tipo:** grupo de investigación
- **Afiliación:** CMU (Carnegie Mellon University), School of Computer Science, Software and Societal Systems Department (laboratorio STRUDEL). Coautor externo: Andrew Macvean (Google).
- **Quién es:** el primer autor es Shyam Agarwal, doctorando de Bogdan Vasilescu, con contribución igual de Anmol Singhal. Vasilescu es el autor sénior: profesor asociado en CMU, dirige el laboratorio STRUDEL (minería de repositorios y aspectos socio-técnicos del software) y es editor asociado de ACM TOSEM (Transactions on Software Engineering and Methodology). Completan el equipo Travis Breaux (CMU, ingeniería de requisitos) y Andrew Macvean (Google).
- **Qué aportó:** el primer estudio empírico amplio sobre cómo se practica de verdad el SDD con agentes de IA: "Spec-Driven Development as Prescribed and as Practiced" (arXiv 2608.25202; v1 del 25-08-2026, v4 del 15-10-2026). Combina un análisis temático de Reddit, 21 entrevistas (8 a creadores de herramientas, anónimos) y 266 repositorios activos. Hallazgos: hay consenso en que la spec debe capturar la intención, pero en la práctica se llena de detalles de implementación, lo que ayuda al agente pero hace que la spec envejezca mal; el SDD se usa de forma selectiva, sobre todo en funcionalidades nuevas; los agentes ganan fiabilidad a cambio de más coste de planificación y revisión; la estructura que impone cada herramienta condiciona lo que ven personas y agentes; y la coherencia entre spec y código se revisa al terminar el cambio, no de forma continua. Además liberan SpecMine (licencia CC BY 4.0): un censo de 470.795 specs en 73.030 repositorios atribuidas a 17 herramientas (OpenSpec, Spec Kit, Conductor, Agent OS, Claude Code, Codex, Cursor y otras), un censo aparte de Kiro (98.574 artefactos en 12.910 repositorios), 5.992 pull requests que tocan specs y un índice de trazabilidad.
- **Obras o herramientas clave:**
  - Agarwal, Singhal, Macvean, Vasilescu y Breaux: "Spec-Driven Development as Prescribed and as Practiced", arXiv 2608.25202 (2026)
  - SpecMine, corpus de artefactos de SDD en GitHub (Zenodo, DOI (Digital Object Identifier) 10.5281/zenodo.22102779; espejo en Hugging Face; muestra de 500 repositorios en GitHub)
  - SpecMine como uno de los dos datasets oficiales del Mining Challenge de la conferencia Mining Software Repositories 2027 (Dublín, 26 y 27 de abril de 2027)
- **Por qué está en la lista:** es la evidencia empírica independiente más directa sobre el SDD con IA, en una literatura dominada por los fabricantes de herramientas. Su corpus abierto es la mejor fuente cuantitativa para comparar Spec Kit, OpenSpec, Kiro y otras, y al ser dataset del Mining Challenge de 2027 dará pie a muchos estudios.
- **Verificación:** confirmado, con importancia media; añadido en la segunda pasada. Es un preprint sin revisión por pares y con poco eco fuera de arXiv. El primer autor es Shyam Agarwal, no Vasilescu, y el aporte es de grupo; Macvean es de Google, no de CMU. El paper da dos listas de 18 herramientas que no coinciden (17 en el censo general más Kiro aparte). Los cuatro autores de CMU son co-chairs del Mining Challenge. El aporte es descriptivo: no propone un método de SDD.
- **Enlaces:** [arXiv 2608.25202: Spec-Driven Development as Prescribed and as Practiced](https://arxiv.org/abs/2608.25202) · [Texto completo en HTML (arXiv)](https://arxiv.org/html/2608.25202) · [alphaXiv 2608.25202](https://www.alphaxiv.org/abs/2608.25202) · [SpecMine en Zenodo](https://doi.org/10.5281/zenodo.22102779) · [SpecMine en Hugging Face](https://huggingface.co/datasets/ShyAgarwal/specmine) · [SpecMine: muestra oficial de 500 repositorios (GitHub)](https://github.com/shyamagarwal13/specmine-official) · [Mining Software Repositories 2027: Mining Challenge](https://2027.msrconf.org/track/msr-2027-mining-challenge) · [Página personal de Bogdan Vasilescu](https://bvasiles.github.io/)
- **Fuentes:** [arXiv abs 2608.25202 (autores, versiones y resumen)](https://arxiv.org/abs/2608.25202) · [arXiv HTML 2608.25202 (afiliaciones, herramientas, censo de Kiro)](https://arxiv.org/html/2608.25202) · [Mining Challenge 2027 (SpecMine seleccionado y co-chairs)](https://2027.msrconf.org/track/msr-2027-mining-challenge) · [specmine-official en GitHub (tabla de cifras)](https://github.com/shyamagarwal13/specmine-official) · [Página de Bogdan Vasilescu (cargo y laboratorio)](https://bvasiles.github.io/)

### Investigación aplicada y métodos formales

#### AWS Automated Reasoning Group (Byron Cook)

- **Tipo:** organización
- **Afiliación:** Amazon Web Services; Byron Cook, VP y Distinguished Scientist.
- **Quién es:** grupo de Amazon dedicado a llevar la lógica matemática y la verificación formal (solvers SMT (Satisfiability Modulo Theories), demostradores, Lean) a servicios en producción. Lo lidera Byron Cook y cumplió 10 años en 2026.
- **Qué aportó:** une la spec informal del SDD con IA y la verificación formal. Kiro incorporó un análisis de requisitos en el que el LLM traduce los criterios de aceptación EARS a lógica (SMT-LIB) y un motor de razonamiento detecta contradicciones y huecos antes de escribir código. Además, Bedrock Guardrails (Automated Reasoning checks) y Policy en AgentCore aplican razonamiento automático para verificar salidas y acotar las acciones de agentes. Cook defiende que la especificación se está volviendo mainstream y que los usuarios acabarán exigiendo conceptos como la lógica temporal en las herramientas guiadas por especificación.
- **Obras o herramientas clave:**
  - Kiro: "Requirements analysis: catching requirement bugs before they become code" (12-05-2026)
  - Amazon Bedrock Guardrails: Automated Reasoning checks
  - "A chat with Byron Cook on automated reasoning and trust in AI systems", All Things Distributed (17-02-2026)
  - Byron Cook, "A decade of mathematical certainty: Reflections on the Automated Reasoning Group" (11-08-2026)
  - Byron Cook, "Three challenges in machine-based reasoning" (04-08-2025)
  - Inversión de Amazon en la Lean Focused Research Organization (26-07-2026)
- **Por qué está en la lista:** es el ejemplo más concreto, desplegado a escala, de métodos formales aplicados a specs escritas para agentes de IA: detecta contradicciones en los requisitos con solvers antes de generar el código, con el respaldo público de un científico de referencia en verificación.
- **Verificación:** confirmado. El post de PBT de Kiro (17-11-2025, de Aaron Eline) no debe atribuirse al grupo; el post de requirements analysis lo firman científicos aplicados y el vínculo con el grupo lo establece el post de Cook. Ninguna fuente usa la expresión "spec-driven development". Hay solapamiento con Kiro y Marc Brooker (tres entradas de AWS).
- **Enlaces:** [Byron Cook en Amazon Science](https://www.amazon.science/author/byron-cook) · [Kiro blog](https://kiro.dev/blog/)
- **Fuentes:** [All Things Distributed: A chat with Byron Cook](https://www.allthingsdistributed.com/2026/02/a-chat-with-byron-cook-on-automated-reasoning-and-trust-in-ai-systems.html) · [Amazon Science: A decade of mathematical certainty](https://www.amazon.science/blog/a-decade-of-mathematical-certainty-reflections-on-the-automated-reasoning-group) · [Kiro: Requirements analysis](https://kiro.dev/blog/deep-spec-analysis/) · [Kiro: Does your code match your spec? (property-based testing)](https://kiro.dev/blog/property-based-testing/) · [The New Stack: Kiro requirements analysis (solo se vio el titular)](https://thenewstack.io/kiro-requirements-analysis-automated-reasoning/)

### Críticos y debate

#### Kent Beck

- **Tipo:** persona
- **Afiliación:** independiente (newsletter "Software Design: Tidy First?"); creador de XP (Extreme Programming) y redescubridor de TDD.
- **Quién es:** ingeniero de software estadounidense, creador de Extreme Programming, divulgador de TDD y uno de los firmantes del Manifiesto Ágil. Hoy escribe y da charlas sobre programar con agentes de IA.
- **Qué aportó:** es la voz crítica más citada del SDD. Considera "bizarre" suponer que la implementación no enseña nada que obligue a cambiar la especificación, y cuestiona escribir la spec completa antes de implementar (Martin Fowler lo recogió en enero de 2026). Como alternativa propone el "augmented coding": dirigir al agente con TDD estricto, un plan.md con la lista de tests pendientes y revisión continua del diseño, en contraste con el vibe coding. Avisa de señales de alarma como bucles, funcionalidad no pedida y tests desactivados o borrados.
- **Obras o herramientas clave:**
  - Test-Driven Development: By Example (2002)
  - Extreme Programming Explained (1999)
  - "Augmented Coding: Beyond the Vibes" (newsletter, 25-06-2025): BPlusTree3 con TDD y plan.md
  - Entrevista "TDD, AI agents and coding with Kent Beck" (The Pragmatic Engineer, 11-06-2025)
  - O11ycast ep. 80 "Augmented Coding with Kent Beck" (30-04-2025)
  - Post en LinkedIn criticando el SDD de "spec completa primero" (citado por Fowler, 08-01-2026)
- **Por qué está en la lista:** es el contrapunto imprescindible para entender los límites del SDD: su crítica al "big spec up front", amplificada por Martin Fowler, y su alternativa basada en TDD y en un plan vivo (plan.md) marcan el debate sobre cuánta especificación hace falta antes de que el agente escriba código.
- **Verificación:** confirmado como crítico, no como exponente. El post de LinkedIn no se abrió (exige login); la cita consta por el fragmento de Fowler. El episodio de The Pragmatic Engineer trata de TDD y agentes, no de SDD.
- **Enlaces:** [Newsletter: Augmented Coding: Beyond the Vibes](https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes) · [kentbeck.com - resumen de Augmented Coding](https://kentbeck.com/summaries/augmented-coding-beyond-the-vibes/) · [Post de LinkedIn citado por Fowler](https://www.linkedin.com/feed/update/urn:li:activity:7413956151144542208/)
- **Fuentes:** [martinfowler.com fragment 2026-01-08](https://martinfowler.com/fragments/2026-01-08.html) · [Augmented Coding: Beyond the Vibes (25-06-2025)](https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes) · [The Pragmatic Engineer: TDD, AI agents and coding with Kent Beck (11-06-2025)](https://newsletter.pragmaticengineer.com/p/tdd-ai-agents-and-coding-with-kent) · [O11ycast ep. 80 (30-04-2025)](https://www.heavybit.com/library/podcasts/o11ycast/ep-80-augmented-coding-with-kent-beck)

#### François Zaninotto

- **Tipo:** persona
- **Afiliación:** Marmelab (fundador y CEO), Nancy, Francia.
- **Quién es:** desarrollador y emprendedor francés, CEO de Marmelab y autor de proyectos open source muy usados, como react-admin (unas 27k estrellas), Faker para PHP (unas 26,6k) y gremlins.js. Practica la gestión lean y ágil.
- **Qué aportó:** fijó el marco crítico de "Waterfall" en el debate sobre el SDD con IA. Sostiene que herramientas como Spec Kit y Kiro producen montañas de Markdown que hay que revisar, añaden burocracia y aportan poco frente a los modos de planificación de los agentes. Como alternativa propone un desarrollo iterativo, en pasos pequeños, inspirado en Agile y Lean Startup.
- **Obras o herramientas clave:**
  - "Spec-Driven Development: The Waterfall Strikes Back" (blog de Marmelab, 12-11-2025)
  - react-admin (framework de frontend, open source)
  - Faker para PHP (biblioteca de datos falsos, archivada)
  - gremlins.js (monkey testing)
- **Por qué está en la lista:** es la crítica más difundida del SDD con IA: 225 puntos y 191 comentarios en HN (Hacker News), con réplicas como la de Allstacks ("SDD isn't Waterfall"). Da contrapeso a una lista dominada por promotores de herramientas.
- **Verificación:** confirmado como voz crítica, no como creador del SDD. Que lo citen "decenas de artículos" no se pudo comprobar; consta al menos una réplica directa.
- **Enlaces:** [Spec-Driven Development: The Waterfall Strikes Back](https://marmelab.com/blog/2025/11/12/spec-driven-development-waterfall-strikes-back) · [François Zaninotto en GitHub](https://github.com/fzaninotto) · [Marmelab](https://marmelab.com)
- **Fuentes:** [Marmelab: The Waterfall Strikes Back (12-11-2025)](https://marmelab.com/blog/2025/11/12/spec-driven-development-waterfall-strikes-back) · [Hacker News: envíos de marmelab.com (ítem 45935763)](https://news.ycombinator.com/from?site=marmelab.com) · [Allstacks: SDD isn't Waterfall (12-03-2026)](https://allstacks.com/blog/spec-driven-development-isnt-waterfall-why-the-ai-coding-bottleneck-changed-everything) · [GitHub: fzaninotto](https://github.com/fzaninotto)

### Libros y formación

#### Hari Krishnan

- **Tipo:** persona
- **Afiliación:** Polarizer Technologies (fundador y CEO); creador de intent-driven.dev; advisor de OpenSpec; ex-ThoughtWorks.
- **Quién es:** estratega de IA y plataformas con más de veinte años de experiencia (ThoughtWorks, Citrix, McAfee).
- **Qué aportó:** escribe el primer libro de referencia de una gran editorial dedicado al SDD con IA. Es una guía práctica e independiente de herramientas: specs como superficie de control para agentes, extensión de Spec-Kit y OpenSpec, SDD en código existente sin specs, corrección de defectos vía spec, medición de la calidad de las specs y escalado a microservicios y varios repos. Además asesora la dirección técnica de OpenSpec y escribe sobre la adopción empresarial del SDD.
- **Obras o herramientas clave:**
  - "Spec-Driven Development: Engineering with Intent" (Manning, MEAP (Manning Early Access Program) desde agosto de 2026, 4 de 10 capítulos; edición final estimada para la primavera de 2027; ISBN 9781633433465)
  - "Spec-Driven Development – Adoption at Enterprise Scale" (InfoQ, 19-02-2026)
  - intent-driven.dev (sitio, canal de YouTube y GitHub sobre desarrollo guiado por intención)
  - Advisor de dirección técnica de OpenSpec (Fission-AI)
- **Por qué está en la lista:** autor del libro de referencia sobre SDD con IA y asesor de una de las herramientas SDD principales (OpenSpec). Es lectura recomendada para seguir investigando.
- **Verificación:** confirmado. En OpenSpec figura como Advisor, no como maintainer. El libro aún está incompleto y su alcance es menor que el de los creadores de herramientas.
- **Enlaces:** [Sitio personal](https://harikrishnan.io) · [intent-driven.dev — libro](https://intent-driven.dev/book/) · [LinkedIn](https://www.linkedin.com/in/harikrishnan83) · [GitHub](https://github.com/harikrishnan83) · [YouTube Intent-Driven Development](https://www.youtube.com/@intent-driven-development)
- **Fuentes:** [Manning: Spec-Driven Development](https://manning.com/books/spec-driven-development) · [OpenSpec MAINTAINERS.md](https://github.com/Fission-AI/OpenSpec/blob/main/MAINTAINERS.md) · [intent-driven.dev book](https://intent-driven.dev/book/) · [InfoQ — Spec Driven Development (artículos)](https://www.infoq.com/spec-driven-development/articles)

#### Simon Martinelli

- **Tipo:** persona
- **Afiliación:** Martinelli LLC (Erlach, Suiza); Java Champion, Vaadin Champion y Oracle ACE Pro; profesor en dos universidades suizas.
- **Quién es:** arquitecto, desarrollador, consultor y formador suizo con más de 30 años de experiencia. Asesora a equipos en desarrollo con IA y escribe el blog "Keep IT Simple".
- **Qué aportó:** escribió uno de los primeros libros sobre SDD con agentes de IA y creó el AIUP (AI Unified Process). AIUP es un método "spec-anchored": requisitos, casos de uso, especificaciones de casos de uso y modelo de entidades viven en el repositorio, y los tests se trazan a los casos de uso con una anotación @UseCase. Se apoya en la ingeniería de requisitos de RUP (Rational Unified Process) y admite proyectos brownfield.
- **Obras o herramientas clave:**
  - Libro "Spec-Driven Development: From Specs to Code with AI Agents" (Apress Pocket Guides, agosto de 2026; 152 páginas, 10 capítulos)
  - AI Unified Process (AIUP), método de SDD anclado en casos de uso
  - Charla "From Developer to Builder: A Spec-Driven Development Deep Dive" (Sessionize, 2026)
  - Charla en AI Native DevCon London (01-06-2026)
  - Artículo "The Three Levels of Spec-Driven Development, and Where the AI Unified Process Sits" (11-10-2026)
- **Por qué está en la lista:** autor de uno de los pocos libros publicados por una editorial técnica (Apress/Springer) sobre SDD con IA, creador de una metodología propia (AIUP) y ponente habitual sobre SDD en conferencias internacionales.
- **Verificación:** confirmado. Relevancia real pero de nicho: libro breve y alcance sobre todo en la comunidad Java/Vaadin.
- **Enlaces:** [Blog Keep IT Simple](https://martinelli.ch/blog) · [Formación en Spec-Driven Development](https://martinelli.ch/training/spec-driven-development/) · [X: @simas_ch](https://x.com/simas_ch) · [LinkedIn](https://www.linkedin.com/in/simonmartinelli) · [Perfil en Sessionize](https://sessionize.com/simon-martinelli)
- **Fuentes:** [Springer/Apress: Spec-Driven Development: From Specs to Code with AI Agents](https://link.springer.com/book/10.1007/979-8-8688-2851-5) · [Martinelli: publicaciones](https://martinelli.ch/about-me/publications/) · [Martinelli: The Three Levels of Spec-Driven Development](https://martinelli.ch/the-three-levels-of-spec-driven-development-and-where-the-ai-unified-process-sits/) · [Sessionize: From developer to builder](https://sessionize.com/s/simon-martinelli/from-developer-to-builder-a-spec-driven-developmen/184599) · [dabase.com: AI Native DevCon London 2026](https://dabase.com/blog/2026/ai-native-devcon-london-2026/)

---

## Precursores clásicos

### Métodos formales

#### Tony Hoare (C. A. R. Hoare)

- **Tipo:** persona
- **Afiliación:** Universidad de Oxford; Microsoft Research Cambridge; antes Queen's University Belfast (1934-2026).
- **Quién es:** informático británico (sir Charles Antony Richard Hoare), inventor de Quicksort, de la lógica de Hoare y de CSP (Communicating Sequential Processes). Premio Turing 1980 y Premio Kyoto 2000. Murió el 5 de marzo de 2026, a los 92 años.
- **Qué aportó:** su artículo de 1969 introdujo el razonamiento axiomático sobre programas mediante triples {P} C {Q} (precondición, comando, postcondición), la base teórica de la especificación de comportamiento por contratos: Design by Contract de Meyer, JML (Java Modeling Language), Dafny y la verificación deductiva. También formalizó la especificación de procesos concurrentes con CSP. Es la raíz conceptual de tratar la especificación como algo verificable contra el código.
- **Obras o herramientas clave:**
  - "An Axiomatic Basis for Computer Programming", Communications of the ACM (Association for Computing Machinery) (1969)
  - Quicksort (1959-1961)
  - Monitores para sistemas operativos (década de 1970)
  - "Communicating Sequential Processes" (libro, 1985)
  - Premio Turing (1980); Premio Kyoto (2000)
- **Por qué está en la lista:** es el precursor teórico fundamental de la idea de especificar formalmente qué debe cumplir un programa (pre y postcondiciones), que sustenta Design by Contract y las herramientas de verificación que hoy se combinan con código generado por IA.
- **Verificación:** confirmado. La conexión con la verificación de código generado por LLMs es conceptual y no se verificó con una fuente específica.
- **Enlaces:** [Wikipedia — Tony Hoare](https://en.wikipedia.org/wiki/Tony_Hoare)
- **Fuentes:** [Wikipedia — Tony Hoare](https://en.wikipedia.org/wiki/Tony_Hoare) · [Merton College — Professor Sir Tony Hoare 1934-2026](https://www.merton.ox.ac.uk/news/professor-sir-charles-anthony-richard-tony-hoare-1934-2026) · [Kyoto Prize — In Memory of Professor Sir Antony Hoare](https://www.kyotoprize.org/en/260323)

#### Leslie Lamport

- **Tipo:** persona
- **Afiliación:** Microsoft Research (2001-2025, retirado); TLA+ hoy está bajo la TLA+ Foundation (Linux Foundation).
- **Quién es:** informático estadounidense y Premio Turing 2013 por sus trabajos sobre sistemas distribuidos y concurrentes. Es autor del algoritmo Paxos, desarrollador inicial de LaTeX y creador del lenguaje de especificación formal TLA+.
- **Qué aportó:** defiende que todo software debe tener una especificación, el "plano" que se escribe antes de programar ("pensar por encima del código"), y creó TLA+ con su comprobador de modelos TLC para especificar y verificar sistemas concurrentes y distribuidos. TLA+ tiene uso industrial en AWS desde 2011 (DynamoDB, S3, EBS) y en Microsoft (Xbox 360, Cosmos DB). Hoy es un destino natural para generar y comprobar especificaciones con LLMs: la TLA+ Foundation y NVIDIA premiaron en 2025 herramientas de IA que pasan de código a spec (Specula, ganadora) y de spec a código Rust.
- **Obras o herramientas clave:**
  - TLA+ (lenguaje de especificación, 1999) y el comprobador de modelos TLC
  - "Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers" (Addison-Wesley, 2002)
  - "Thinking Above the Code" (keynote, Microsoft Research Faculty Summit, 2014)
  - "The Part-Time Parliament" (Paxos, 1998)
- **Por qué está en la lista:** es el precursor más influyente de la idea de "especificar antes de codificar" en los métodos formales, con uso industrial probado y hoy uno de los objetivos principales de la generación y verificación de especificaciones asistida por LLMs.
- **Verificación:** confirmado. El vínculo con la IA es de la comunidad de TLA+, no del propio Lamport.
- **Enlaces:** [Web de Leslie Lamport](https://lamport.org/) · [Specifying Systems (página oficial del libro)](https://lamport.org/tla/book.html) · [TLA+ Foundation](https://foundation.tlapl.us/)
- **Fuentes:** [Microsoft Research — Thinking Above the Code (2014)](https://www.microsoft.com/en-us/research/video/thinking-above-the-code/) · [Wikipedia — Leslie Lamport](https://en.wikipedia.org/wiki/Leslie_Lamport) · [Wikipedia — TLA+](https://en.wikipedia.org/wiki/TLA%2B) · [TLA+ Foundation — GenAI-accelerated TLA+ Challenge (2025)](https://foundation.tlapl.us/challenge/index.html)

#### K. Rustan M. Leino

- **Tipo:** persona
- **Afiliación:** Amazon Web Services (Senior Principal Applied Scientist); antes Microsoft Research.
- **Quién es:** informático especializado en verificación de programas. Diseñó Dafny y antes trabajó en ESC/Modula-3, ESC/Java y Spec#. Es autor del libro "Program Proofs".
- **Qué aportó:** creó Dafny (2009), un lenguaje "verification-aware" en el que especificación (precondiciones, postcondiciones, invariantes) y código conviven y un verificador automático (Boogie/Z3) comprueba que se cumplen. Hoy Dafny es uno de los principales bancos de prueba del "vericoding", es decir, que los LLMs generen código formalmente verificado a partir de specs formales: en el benchmark de 2025, los LLMs resuelven el 82 % de las tareas en Dafny, frente al 44 % en Verus y el 27 % en Lean. También se propone como lenguaje intermedio verificado para generar código con LLMs.
- **Obras o herramientas clave:**
  - Dafny (lenguaje y verificador, desde 2009)
  - Spec# y ESC/Java (verificación estática con contratos, años 2000)
  - Program Proofs (MIT Press; libro sobre verificación con Dafny)
  - Keynote del workshop Dafny 2025 en POPL (Principles of Programming Languages) (19-01-2025)
- **Por qué está en la lista:** es el puente más directo entre Design by Contract y los métodos formales clásicos y el SDD con IA: en Dafny la especificación formal se vuelve verificable por máquina, y es donde hoy se mide si los LLMs pueden generar código correcto respecto de una spec.
- **Verificación:** confirmado. Corregido: el arXiv 2501.06283 no es de Leino (es de Li, Zetzsche y Somayyajula) y se cita como prueba del uso de Dafny con LLMs. El dato del 82 % viene del benchmark de vericoding (arXiv 2509.22908). El año de "Program Proofs" no se pudo comprobar en MIT Press.
- **Enlaces:** [Web personal de Rustan Leino](https://leino.science/) · [Dafny (web oficial)](https://dafny.org/) · [Program Proofs (web del libro)](https://program-proofs.com/)
- **Fuentes:** [Wikipedia - Dafny](https://en.wikipedia.org/wiki/Dafny) · [POPL 2025 - Dafny workshop keynote](https://popl25.sigplan.org/details/dafny-2025-papers/17/Keynote) · [A benchmark for vericoding (arXiv 2509.22908)](https://arxiv.org/abs/2509.22908) · [Dafny as Verification-Aware Intermediate Language for Code Generation (arXiv 2501.06283)](https://arxiv.org/abs/2501.06283) · [dafny.org](https://dafny.org/)

### Design by Contract

#### Bertrand Meyer

- **Tipo:** persona
- **Afiliación:** Constructor Institute, Schaffhausen (profesor y Provost); Eiffel Software (Chief Architect); profesor en ETH Zürich entre 2001 y 2016.
- **Quién es:** informático francés, creador del lenguaje Eiffel y del concepto de Design by Contract. Es autor de "Object-Oriented Software Construction", ACM Fellow y ganador del ACM Software System Award 2006.
- **Qué aportó:** Design by Contract (precondiciones, postcondiciones e invariantes escritas dentro del código, con require y ensure en Eiffel) es la raíz clásica de "la especificación como contrato ejecutable". En la era de la IA sostiene que el prompt engineering es ingeniería de requisitos y que el código generado por LLM solo vale si se puede verificar contra una especificación formal. Propone combinar la generación por IA con contratos y pruebas formales: pasar "de lo probable a lo demostrable".
- **Obras o herramientas clave:**
  - Lenguaje Eiffel y Design by Contract (finales de los 80)
  - "Object-Oriented Software Construction" (2.ª ed., 1997)
  - "Eiffel: The Language" (1992)
  - "AI for software engineering: from probable to provable" (arXiv 2511.23159, 2025-2026)
  - ACM Tech Talk "Software Verification in the Age of Artificial Intelligence" (07-05-2026)
- **Por qué está en la lista:** es el precursor directo de la idea de spec como contrato verificable y uno de los pocos clásicos que interviene activamente en el debate actual sobre IA, especificación y verificación.
- **Verificación:** confirmado. Corregida la afiliación: no es "ETH emérito".
- **Enlaces:** [Blog y web de Bertrand Meyer](https://bertrandmeyer.com/) · [Bio oficial](https://bertrandmeyer.com/bio/) · [Eiffel: Design by Contract and Assertions](https://www.eiffel.org/doc/solutions/Design_by_Contract_and_Assertions)
- **Fuentes:** [arXiv 2511.23159: AI for software engineering: from probable to provable](https://arxiv.org/abs/2511.23159) · [Questions and answers on AI and verification (21-07-2026)](https://bertrandmeyer.com/2026/07/21/questions-and-answers-on-ai-and-verification-a-follow-up-to-my-may-acm-tech-talk/) · [Bio de Bertrand Meyer](https://bertrandmeyer.com/bio/) · [Wikipedia: Bertrand Meyer](https://en.wikipedia.org/wiki/Bertrand_Meyer) · [ICTSS 2025, keynote speaker](https://conf.researchr.org/info/ictss-2025/keynote-speaker)

### Property-based testing

#### John Hughes

- **Tipo:** persona
- **Afiliación:** Chalmers University of Technology (profesor); QuviQ AB (cofundador y CEO).
- **Quién es:** informático sueco nacido en 1958 (doctorado en Oxford, 1984). Es profesor de Chalmers, co-diseñador de Haskell y ACM Fellow (2018). Cofundó QuviQ para llevar el property-based testing a la industria.
- **Qué aportó:** co-inventó con Koen Claessen QuickCheck y el property-based testing: el desarrollador escribe propiedades que el código debe cumplir, la herramienta genera casos aleatorios y reduce los fallos a contraejemplos mínimos. Las propiedades son especificaciones ejecutables. Esa es la base de cómo Kiro convierte hoy los criterios de aceptación de la spec en tests PBT (con Hypothesis, heredero de QuickCheck) para comprobar que el código cumple la spec.
- **Obras o herramientas clave:**
  - Claessen y Hughes, "QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs", ICFP (International Conference on Functional Programming) 2000
  - QuickCheck (Haskell, 1999) y su versión comercial Quviq QuickCheck (Erlang)
  - "Why Functional Programming Matters" (1989)
  - Charla "Experiences with QuickCheck: Testing the Hard Stuff", GitHub Next Speaker Series (2020)
- **Por qué está en la lista:** es el origen del property-based testing, donde la especificación se escribe como propiedades verificables automáticamente. Las herramientas de SDD con IA lo retoman: Kiro cita QuickCheck como origen de su verificación código-spec.
- **Verificación:** confirmado. QuickCheck es una co-creación con Koen Claessen. El post de Kiro cita QuickCheck pero no nombra a Hughes: el linaje es real pero indirecto.
- **Enlaces:** [Página personal en Chalmers](https://www.cse.chalmers.se/~rjmh/) · [QuviQ](https://www.quviq.com/) · [GitHub Next Speaker Series: John Hughes](https://githubnext.com/speaker-series/johnhughes/)
- **Fuentes:** [Wikipedia: John Hughes (computer scientist)](https://en.wikipedia.org/wiki/John_Hughes_(computer_scientist)) · [Wikipedia: QuickCheck](https://en.wikipedia.org/wiki/QuickCheck) · [GitHub Next Speaker Series: John Hughes](https://githubnext.com/speaker-series/johnhughes/) · [Kiro: Does your code match your spec? (cita QuickCheck)](https://kiro.dev/blog/property-based-testing/) · [Paper de QuickCheck (PDF, copia en Tufts)](https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf)

### BDD

#### Dan North (Daniel Terhorst-North)

- **Tipo:** persona
- **Afiliación:** Dan North & Associates Limited (consultor independiente); antes Thoughtworks Londres (2002-2011 aprox.).
- **Quién es:** consultor británico y creador de BDD. Fue el primer empleado técnico de Thoughtworks en Londres y se le atribuye haber co-inventado el build pipeline y prácticas pioneras de Continuous Delivery.
- **Qué aportó:** creó BDD como evolución de TDD centrada en el comportamiento y en un vocabulario compartido con el negocio. Introdujo la plantilla de escenarios Given/When/Then, que Cucumber formalizó después como Gherkin, y escribió JBehave (iniciado hacia 2003). Es la forma más extendida de especificación ejecutable en lenguaje natural, antecedente directo del SDD: la Wikipedia de SDD dice que este "refleja los mismos pasos" que BDD. En el debate actual, junto a Gojko Adzic, critica el SDD "one-shot" (comparándolo con CASE (Computer-Aided Software Engineering) y MDA (Model-Driven Architecture)) y defiende ciclos iterativos cortos.
- **Obras o herramientas clave:**
  - JBehave (framework de BDD para Java, iniciado hacia 2003)
  - "Introducing BDD" (Better Software, marzo de 2006)
  - Plantilla de escenarios Given/When/Then (2006)
  - Sesión GOTO Unscripted "Spec-Driven Development Is Back. But Not How You Think", con Gojko Adzic
  - "Best Simple System for Now" (blog, 03-02-2025)
- **Por qué está en la lista:** BDD y Given/When/Then son el antecedente más cercano de las especificaciones en lenguaje natural que hoy consumen los agentes de IA, y North participa de forma explícita en el debate actual sobre el SDD.
- **Verificación:** confirmado. La Wikipedia de SDD no lo nombra a él, solo a BDD. Su blog no tiene posts sobre IA ni SDD; su postura consta solo por la sesión de GOTO.
- **Enlaces:** [dannorth.net (web oficial)](https://dannorth.net/) · [Perfil de Daniel Terhorst-North](https://dannorth.net/profile/) · [Introducing BDD](https://dannorth.net/blog/introducing-bdd/)
- **Fuentes:** [Dan North: Introducing BDD (2006)](https://dannorth.net/blog/introducing-bdd/) · [Dan North & Associates: perfil](https://dannorth.net/profile/) · [GOTO: Spec-Driven Development Is Back. But Not How You Think](https://gotopia.tech/sessions/4066/spec-driven-development-is-back-but-not-how-you-think) · [Wikipedia: Spec-driven development](https://en.wikipedia.org/wiki/Spec-driven_development) · [Wikipedia: Behavior-driven development](https://en.wikipedia.org/wiki/Behavior-driven_development)

### Specification by Example y tests de aceptación

#### Gojko Adzic

- **Tipo:** persona
- **Afiliación:** Neuri Consulting LLP (socio); fundador de Narakeet; autor.
- **Quién es:** autor y consultor británico especializado en entrega de software. Escribió siete libros, entre ellos Specification by Example, Impact Mapping y Lizard Optimization, y da keynotes con frecuencia.
- **Qué aportó:** formalizó Specification by Example: equipos de negocio y desarrollo especifican requisitos con ejemplos concretos que se convierten en pruebas ejecutables y documentación viva. Es una raíz directa de la idea de la especificación como fuente de verdad verificable. Hoy participa en el debate sobre el SDD con IA con una postura crítica: rechaza la generación "spec-to-product" de un solo paso (como en CASE y MDA) y defiende ciclos cortos de feedback y reglas verificadas automáticamente en CI (Continuous Integration).
- **Obras o herramientas clave:**
  - Specification by Example (Manning, 2011)
  - Bridging the Communication Gap (2009)
  - Impact Mapping (2012)
  - Fifty Quick Ideas To Improve Your Tests / User Stories
  - "Spec-Driven Dev Is Back. But Not How You Think" (GOTO Unscripted con Daniel Terhorst-North, podcast del 29-05-2026)
  - "Specification Driven Development (SDD): The future of AI-assisted coding, or the revenge of Waterfall?" (lección abierta, Politécnica de Poznań, 25-03-2026)
- **Por qué está en la lista:** creador de Specification by Example, uno de los antecedentes directos del SDD, y voz crítica de referencia en el debate actual.
- **Verificación:** confirmado. El Jolt Award solo lo confirma una fuente secundaria. Se descartó una fuente de GOTO Copenhagen que era de otra ponente.
- **Enlaces:** [Web personal](https://gojko.net/) · [Libros](https://gojko.net/books/) · [LinkedIn](https://uk.linkedin.com/in/gojko) · [GitHub](https://github.com/gojko)
- **Fuentes:** [Manning: Specification by Example](https://www.manning.com/books/specification-by-example) · [GOTO — Spec-Driven Development Is Back](https://gotopia.tech/sessions/4066/spec-driven-development-is-back-but-not-how-you-think) · [GOTO podcast (29-05-2026)](https://goto.buzzsprout.com/1714721/episodes/19171518-spec-driven-dev-is-back-but-not-how-you-think-daniel-terhorst-north-gojko-adzic) · [Poznań — Open lecture: SDD (2026)](https://www.poznan.pl/mim/studia/en/news/open-lecture-specification-driven-development-sdd-the-future-of-ai-assisted-coding-or-the,274288.html)

#### Ward Cunningham

- **Tipo:** persona
- **Afiliación:** Cunningham & Cunningham Inc.
- **Quién es:** programador estadounidense (n. 1949), creador de la primera wiki (WikiWikiWeb, 1995), coautor del Manifiesto Ágil (2001) y autor del concepto de "deuda técnica".
- **Qué aportó:** creó Fit (Framework for Integrated Test, 2002), un marco de tests de aceptación en el que el cliente escribe ejemplos en tablas legibles por negocio que se ejecutan contra el software y se colorean en verde, rojo o amarillo. Fue una de las primeras formas de "especificación ejecutable". De Fit salieron FitNesse y la línea de Specification by Example y ATDD (Acceptance Test-Driven Development), antecedente de la idea actual de specs verificables automáticamente.
- **Obras o herramientas clave:**
  - Fit, Framework for Integrated Test (2002)
  - WikiWikiWeb (1995)
  - Manifiesto Ágil (2001, coautor)
  - Tarjetas CRC (Class-Responsibility-Collaborator), con Kent Beck
  - Metáfora de la deuda técnica (1992)
- **Por qué está en la lista:** Fit fue uno de los primeros mecanismos prácticos para que la especificación del cliente, en forma de ejemplos en tablas, fuera ejecutable y sirviera de criterio de aceptación.
- **Verificación:** confirmado como precursor indirecto. No consta ninguna opinión suya sobre SDD con IA. El libro "Fit for Developing Software" (con Rick Mugridge, 2005) no se pudo verificar.
- **Enlaces:** [Wikipedia: Ward Cunningham](https://en.wikipedia.org/wiki/Ward_Cunningham) · [FitNesse](https://fitnesse.org/)
- **Fuentes:** [Wikipedia: Framework for integrated test](https://en.wikipedia.org/wiki/Framework_for_integrated_test) · [Wikipedia: Ward Cunningham](https://en.wikipedia.org/wiki/Ward_Cunningham) · [FitNesse: web oficial](https://fitnesse.org/)

### API-first y contratos

#### OpenAPI Initiative (Linux Foundation)

- **Tipo:** organización
- **Afiliación:** proyecto de la Linux Foundation; origen en Swagger (Tony Tam, Wordnik, 2010), donado por SmartBear en 2015.
- **Quién es:** consorcio abierto bajo la Linux Foundation que custodia la OpenAPI Specification, el estándar de descripción de APIs HTTP más usado, y las especificaciones complementarias Arazzo y Overlay.
- **Qué aportó:** consolidó el enfoque API-first o contract-first: un contrato legible por máquinas y por humanos que funciona como fuente de verdad para generar código cliente y servidor, tests, mocks y documentación. Es la práctica de "la especificación manda" que el SDD con IA generaliza. Con Arazzo, que describe flujos de varias llamadas a APIs, el estándar se orienta explícitamente a los agentes de IA como consumidores de primera clase ("AI agents become first-class API consumers").
- **Obras o herramientas clave:**
  - Swagger Specification 1.0 (2011) y 2.0 (2014), de Tony Tam en Wordnik
  - Creación de la OpenAPI Initiative en la Linux Foundation (nov-2015); renombrado a OpenAPI Specification (01-01-2016)
  - OpenAPI 3.0.0 (jul-2017), 3.1.0 (feb-2021, alineada con JSON Schema), 3.2.0 (sep-2025)
  - Arazzo Specification (v1.1.0): workflows de APIs para humanos y agentes de IA
  - Overlay Specification 1.0.0
- **Por qué está en la lista:** es el precursor más directo y extendido en la industria de la idea de un spec ejecutable como fuente de verdad: el diseño API-first con contratos OpenAPI, de los que se genera código, se practica desde hace más de una década y hoy enlaza explícitamente con los agentes a través de Arazzo.
- **Verificación:** confirmado. Llamarla "SDD aplicado a APIs" es una lectura editorial: OpenAPI no se presenta como SDD.
- **Enlaces:** [OpenAPI Initiative (web oficial)](https://www.openapis.org/) · [Arazzo Specification](https://www.openapis.org/arazzo-specification) · [OpenAPI Specification – Wikipedia](https://en.wikipedia.org/wiki/OpenAPI_Specification)
- **Fuentes:** [OpenAPI Specification – Wikipedia (historia y versiones)](https://en.wikipedia.org/wiki/OpenAPI_Specification) · [Arazzo Specification – OpenAPI Initiative](https://www.openapis.org/arazzo-specification) · [OpenAPI Initiative – home](https://www.openapis.org/)

### Notaciones de requisitos

#### Alistair Mavin (EARS)

- **Tipo:** persona
- **Afiliación:** consultor independiente de ingeniería de requisitos (Reino Unido); antes Rolls-Royce plc durante 14 años.
- **Quién es:** ingeniero británico especializado en ingeniería de requisitos y autor principal de EARS y EARS+. Fue especialista en requisitos en Rolls-Royce y ha dirigido proyectos de requisitos en aeroespacial, automoción, defensa, ferrocarril y software. Fue Industry Chair de RE13 e Industry Laboratory Chair de RE14, conferencias del IEEE (Institute of Electrical and Electronics Engineers); es miembro del IEEE, del INCOSE (International Council on Systems Engineering) y de la BCS (British Computer Society), y Chartered Engineer.
- **Qué aportó:** creó EARS con colegas de Rolls-Royce mientras analizaban normativa de aeronavegabilidad para el sistema de control de un motor a reacción. EARS restringe de forma ligera el lenguaje natural de los requisitos: las cláusulas van siempre en el mismo orden y usan unas pocas palabras clave (WHEN, WHILE, IF/THEN, WHERE, SHALL) que forman cinco patrones básicos (ubicuo, dirigido por eventos, dirigido por estados, comportamiento no deseado y opcional). El objetivo es reducir la ambigüedad, la vaguedad y lo incompleto. Su relación con el SDD con IA es indirecta: en 2025 Kiro adoptó EARS como notación nativa de los criterios de aceptación en requirements.md, y desde entonces se cita como sintaxis neutral, legible a la vez por personas y por LLMs, para la fase de requisitos de una spec. Hay plugins y servidores MCP que la llevan a otros asistentes de código.
- **Obras o herramientas clave:**
  - Mavin, Wilkinson, Harwood y Novak: "Easy Approach to Requirements Syntax (EARS)", RE'09 (17th IEEE International Requirements Engineering Conference), 2009, págs. 317-322, DOI 10.1109/RE.2009.9
  - EARS+ (extensión de EARS, de la que es autor principal)
- **Por qué está en la lista:** es un precursor genuino del SDD con IA. Su notación es el formato oficial de requirements.md en Kiro, y las guías de SDD de 2025-2026 la recomiendan para escribir specs que los agentes interpreten sin ambigüedad. Su peso viene de que otros adoptaron EARS: él no ha aportado nada directo al SDD con IA.
- **Verificación:** confirmado, con importancia media; añadido en la tercera pasada. Es un precursor puro ("Kiro adopted it, did not invent it"). EARS cubre solo la fase de requisitos, no la especificación completa. No se pudo verificar el supuesto premio Most Influential Paper de RE'19 y se dejó fuera; las listas de adoptantes no coinciden entre fuentes; el sitio personal alistairmavin.com no respondió.
- **Enlaces:** [Easy Approach to Requirements Syntax (Wikipedia)](https://en.wikipedia.org/wiki/Easy_Approach_to_Requirements_Syntax) · [Paper RE'09 (DOI, redirige a IEEE Xplore)](https://doi.org/10.1109/RE.2009.9) · [Kiro docs: Feature specs (requirements.md usa notación EARS)](https://kiro.dev/docs/specs/feature-specs/) · [Charla de Alistair Mavin sobre EARS en la FIB-UPC (Facultat d'Informàtica de Barcelona, Universitat Politècnica de Catalunya)](https://www.fib.upc.edu/en/node/20258)
- **Fuentes:** [Wikipedia: Easy Approach to Requirements Syntax](https://en.wikipedia.org/wiki/Easy_Approach_to_Requirements_Syntax) · [Kiro: Feature specs](https://kiro.dev/docs/specs/feature-specs/) · [FIB-UPC: seminario de Alistair Mavin sobre EARS (2020)](https://www.fib.upc.edu/en/node/20258) · [CodeMySpec: Spec-Driven Development in 2026 ("Kiro adopted it, did not invent it")](https://codemyspec.com/blog/spec-driven-development) · [IET EngX: EARS by Alistair Mavin, Rolls-Royce](https://engx.theiet.org/f/discussions/27493/easy-approach-to-requirements-syntax-ears-by-alistair-mavin-requirements-specialist-at-rolls-royce-plc) · [SD Times: Amazon launches spec-driven AI IDE, Kiro](https://sdtimes.com/ai/amazon-launches-spec-driven-ai-ide-kiro/)

---

## Menciones honoríficas

Nombres verificados con un aporte real pero que no entran en la lista principal: su aporte es derivado de otra herramienta, divulgativo, de nicho, tangencial al SDD (verificación formal, context engineering) o con poca adopción comprobada. Sin ranking.

### Herramientas y flujos de trabajo

- **Dex (Dexter) Horthy** (HumanLayer, fundador y CEO). Creó el flujo RPI (Research-Plan-Implement), donde los artefactos de investigación y plan sustituyen al PR como objeto de revisión, y declaró haber adoptado "algo como el spec-driven development de Sean Grove". En el AI Engineer Code Summit (Nueva York, noviembre de 2025) dijo que el término SDD está "semánticamente difuso", y en 2026 corrigió en público su tesis: revisar solo el plan degradó su base de código en meses y RPI evolucionó a CRISPY. No entra porque buena parte de su obra es context engineering general; es el primer suplente como practicante crítico. [12-Factor Agents](https://github.com/humanlayer/12-factor-agents) · [Advanced Context Engineering for Coding Agents](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md) · [Tessl podcast ep. 124: Why We Stopped Trusting AI to Write the Plan](https://tessl.io/podcast/124)
- **Brian Casel** (Builder Methods, fundador). Creó Agent OS (julio de 2025), una de las primeras herramientas open source que se presentaron explícitamente como SDD; la v2 tenía un flujo de seis fases con specs, y la v3 (enero de 2026) giró a los estándares de código y delegó la spec en el Plan Mode del agente ("standards-first rather than spec-first", según CodeMySpec). No entra por su poca tracción (unas 5,5k estrellas) y su escasa cobertura independiente; sirve como caso de estudio de ese giro. [Agent OS (Builder Methods)](https://buildermethods.com/agent-os) · [buildermethods/agent-os](https://github.com/buildermethods/agent-os) · [Spec-Driven Development in the Real World](https://buildermethods.com/library/real-spec-driven-development)
- **Augment Code: Intent (Amelia Wattenberger)** (Augment Code; Wattenberger es Product Lead de Intent). Intent es una app de escritorio para macOS, en beta, que propone una "living spec" bidireccional: un agente coordinador redacta la spec, el humano la aprueba antes de escribir código, los agentes la actualizan al trabajar y un agente verificador contrasta el resultado con ella. El ensayo "What spec-driven development gets wrong" (20-02-2026) critica que las specs estáticas se desactualizan. No entra porque casi toda la evidencia viene del propio vendedor y no figura en los rankings independientes de herramientas SDD de junio de 2026. [Intent: a workspace for agent orchestration](https://www.augmentcode.com/blog/intent-a-workspace-for-agent-orchestration) · [What spec-driven development gets wrong](https://augmentcode.com/blog/what-spec-driven-development-gets-wrong) · [intentapp.dev](https://intentapp.dev)
- **Gota (gotalab, @gota_bara)** (independiente, Japón). Creó cc-sdd (unas 3,7k estrellas, MIT), que lleva el flujo de specs de Kiro (requisitos en EARS → diseño → tareas, con aprobación humana) a Claude Code, Codex y otros agentes; desde la v3.0 (09-04-2026) es un "SDD harness" basado en Agent Skills. En su charla de Findy (noviembre de 2025, unas 49k visitas) analiza los límites del SDD y propone tests basados en propiedades y specs mínimas. No entra porque el aporte es derivado de Kiro y su alcance es sobre todo japonés. [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) · [Charla en Speaker Deck (Findy, noviembre de 2025)](https://speakerdeck.com/gotalab555/shi-yang-qu-dong-kai-fa-noli-xiang-toxian-shi-sositexiang-kihe-ifang)
- **Aaron Friel** (OpenAI, Member of Technical Staff), creador de ExecPlans / PLANS.md. Presentó el patrón en la sesión "Shipping with Codex" de OpenAI DevDay (octubre de 2025) y lo publicó como receta del OpenAI Cookbook (07-10-2025, hoy archivada). Un ExecPlan es un documento de diseño autocontenido en el repo (.agent/PLANS.md, referenciado desde AGENTS.md) que el agente sigue y actualiza durante sesiones de varias horas; el Cookbook lo llama "executable specification" y "living document". No entra porque ocupa la capa del plan (el cómo) más que la de la especificación del comportamiento (el qué). [OpenAI Cookbook: Using PLANS.md for multi-hour problem solving](https://developers.openai.com/cookbook/articles/codex_exec_plans) · [PLANS.md en openai/openai-agents-python](https://github.com/openai/openai-agents-python/blob/main/PLANS.md) · [OpenAI DevDay 2025: Shipping with Codex](https://youtu.be/Gr41tYOzE20?si=ZqfoPD7mnKeXtN4-&t=756)
- **Matt Pocock** (Total TypeScript y AI Hero). Su repo "Skills for Real Engineers" formaliza un flujo spec-first: interrogar el plan (grill-me, con modelo de dominio, glosario y ADR (Architecture Decision Record)), convertir la conversación en una spec en el issue tracker, partirla en tickets "tracer bullet", implementar con TDD desde la spec y revisar el diff contra ella. Lo enseña en workshops como "AI Coding For Real Engineers" (AI Engineer Europe, 08-04-2026). No entra porque su spec es un artefacto por feature, no una fuente de verdad viva, y él mismo critica los frameworks SDD prescriptivos (GSD, BMAD, Spec Kit). [mattpocock/skills](https://github.com/mattpocock/skills) · [Perfil de speaker en AI Engineer](https://www.ai.engineer/speakers/matt-pocock) · [Claude plugins: Matt Pocock's Skills](https://claude.com/plugins/mattpocock-skills)
- **Zach Lloyd** (Warp, fundador y CEO). Propone un SDD en dos documentos: PRODUCT.md (el qué, con invariantes verificables) y TECH.md (el cómo), versionados en el PR; el agente implementa contra ellos y después se valida que la implementación los cumpla. Publicó el flujo como skills abiertos en warpdotdev/common-skills (write-product-spec, write-tech-spec, check-impl-against-spec y otros). No entra por su alcance todavía limitado (un artículo de junio de 2026 y un repo de unas 628 estrellas). [Warp blog: Three skills you need for spec-driven development](https://www.warp.dev/blog/three-skills-for-spec-driven-development) · [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills)
- **Backlog.md (Alex Gavrilescu, alias MrLesk)** (desarrollador independiente, Viena). Backlog.md (unas 7,1k estrellas, MIT) guarda cada tarea como un .md versionado en el repo y propone un flujo que llama "spec-driven AI development" con tres revisiones humanas: la spec de la tarea, el plan del agente y el código. El framework comunitario Codex-Spec lo usa como artefacto de especificación. No entra porque la spec funciona a nivel de tarea, no como especificación viva del sistema. [MrLesk/Backlog.md](https://github.com/MrLesk/Backlog.md) · [Perfil GitHub de MrLesk](https://github.com/MrLesk)
- **Traycer AI** (startup de herramientas de IA para desarrolladores). Es una capa de planificación y verificación por encima del agente de código: genera planes por fases, los pasa a un agente externo y verifica el resultado contra el plan. Su Epic Mode es SDD genuino, con "living specs" (mini-specs que se actualizan), tickets y verificación contra la spec. No entra porque la única comparativa externa que la llama SDD es de un competidor (Augment) y no aparece en las comparativas generales de herramientas SDD. [Traycer: documentación](https://docs.traycer.ai/index.md) · [Traycer: Epic Mode](https://docs.traycer.ai/tasks/epic)
- **Qoder (Alibaba), Quest Mode con Spec-driven.** Qoder (agosto de 2025) implementó en un IDE comercial un flujo SDD del estilo de Kiro: aclarar requisitos, generar una spec (requisitos, diseño, tareas y criterios de aceptación), revisarla y ejecutarla. No entra porque el aporte es derivado (llegó un mes después de Kiro), la cifra de "más de 10x de eficiencia" es de Alibaba sin verificar y la ventana Quest se retiró el 15-10-2026. [Qoder docs: Quest, Spec-driven](https://docs.qoder.com/user-guide/quest/spec-driven) · [Aviso de retiro de la ventana Quest](https://docs.qoder.com/release-notes/quest-retirement-notice)
- **Factory (Droid, Spec Mode)** (startup de agentes de desarrollo; cofundador y CTO: Eno Reyes). El Spec Mode del CLI Droid investiga el repo en solo lectura, propone un plan de implementación y pide aprobación antes de tocar código; opcionalmente guarda el plan aprobado en Markdown. Eno Reyes defiende separar la spec (qué construir) del plan (cómo). No entra porque la documentación oficial lo describe como planificación previa a la implementación, sin mantener la spec como fuente de verdad. [Factory docs: Spec Mode](https://docs.factory.com/cli/user-guides/specification-mode) · [Behind the Craft: Eno Reyes sobre spec mode](https://pod.wave.co/podcast/behind-the-craft/full-tutorial-use-ai-agents-for-coding-and-product-management-eno-reyes-factory)
- **Google: Antigravity y su codelab de SDD.** El codelab oficial "Getting started with Spec Driven Development in Antigravity" (sin autor ni fecha) propone un ciclo de 5 pasos (requisitos, arquitectura y especificación a cargo de humanos; código y pruebas a cargo de la IA) y declara la especificación "Single Source of Truth". No entra porque en la práctica el lab usa un prompt en lenguaje natural sin archivos de spec persistentes, y el anuncio de Antigravity no habla de specs ni de SDD. [Google Codelabs: SDD in Antigravity](https://codelabs.developers.google.com/codelabs/getting-started-with-spec-driven-development-in-antigravity) · [Build with Google Antigravity](https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/)
- **Anthropic: "Effective harnesses for long-running agents"** (post de Justin Young, 26-11-2025, con un quickstart oficial). Un agente inicializador expande la spec de la aplicación en un feature_list.json de más de 200 funcionalidades verificables, y los agentes de código solo pueden cambiar el campo "passes": editar o borrar pruebas está prohibido. Así la lista de requisitos es una definición de "terminado" que el agente no puede manipular; el quickstart la llama "source of truth". No entra porque el post lo presenta como harness / context engineering, no como SDD. [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) · [Quickstart autonomous-coding](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)

### Divulgación, libros y formación

- **Paul Everitt** (JetBrains, Developer Advocate; instructor en DeepLearning.AI). Es el único instructor del curso corto "Spec-Driven Development with Coding Agents" (DeepLearning.AI + JetBrains, actualizado el 18-04-2026): constitución, spec por feature, planificar-implementar-validar, código heredado y empaquetado del flujo como skills. También presentó los livestreams de JetBrains sobre "Spec-Driven AI Development". No entra porque su aporte es didáctico (la constitución viene de Spec Kit y en los livestreams usa Agent OS); su trabajo figura también en la ficha de [JetBrains](#jetbrains-junie--jetbrains-ai). [DeepLearning.AI: Spec-Driven Development with Coding Agents](https://www.deeplearning.ai/short-courses/spec-driven-development-with-coding-agents/) · [Repositorio del curso](https://github.com/https-deeplearning-ai/sc-spec-driven-development-files) · [JetBrains livestream: Episode 2](https://info.jetbrains.com/jetbrains-ai-livestream-february11-2026.html)
- **Simon Maple** (Tessl, Head of Developer Relations; co-host del podcast AI Native Dev). Escribió el anuncio del Tessl Framework y el Spec Registry (septiembre de 2025) y da charlas sobre el paso del desarrollo centrado en el código al centrado en la spec. No entra porque es difusión: el aporte conceptual y el producto son de Tessl y de Guy Podjarny, que ya están en la lista. [Perfil en Sessionize](https://sessionize.com/simon-maple/) · [Speaker en QCon AI New York](https://newyork.qcon.ai/speakers/simonmaple)
- **Apoorv Gupta** (Microsoft, Principal Software Engineer). En dos posts del Microsoft Developer Blog (10-06-2026 y 07-10-2026) explica el SDD con GitHub Spec Kit para empresas: la spec como fuente de verdad compartida ("Spec quality = output quality"), las 7 etapas de Spec Kit, la adopción gradual y una constitución por capas (organización, dominio, equipo). No entra porque explica y aplica funciones que ya tiene Spec Kit, no aportes propios. [Spec-Driven Development: A Spec-First Approach to AI-Native Engineering](https://developer.microsoft.com/blog/spec-driven-development-ai-native-engineering/) · [From spec-first to enterprise-ready: extending GitHub Spec Kit](https://developer.microsoft.com/blog/from-spec-first-to-enterprise-ready-extending-github-spec-kit/)
- **Erik Hanchett** (AWS, Senior Developer Advocate; canal "Program With Erik"). Divulga el SDD con Kiro en conferencias (GitNation, ConFoo, AI Engineer World's Fair 2026): requisitos, diseño y tareas revisados en cada paso, archivos de instrucciones para el agente y tests basados en propiedades para verificar contra los requisitos. No entra porque no es autor del método ni de la herramienta. [AI Engineer: Using Spec-Driven Development for Production Workflows](https://www.ai.engineer/talks/IddXPepIAS4-using-spec-driven-development-production-workflows) · [GitNation: la misma charla](https://gitnation.com/contents/using-spec-driven-development-for-production-workflows-3455)
- **Leigh Griffin y Ray Carroll** (ingenieros de software; afiliación no publicada). Su artículo de InfoQ (12-01-2026) plantea el SDD como patrón arquitectónico: la spec es la fuente de verdad, el código se regenera ("la arquitectura pasa a ser ejecutable y exigible") y proponen un modelo de cinco capas (Specification, Generation, Artifact, Validation, Runtime) con detección de drift. No entran porque su aporte se reduce a ese artículo, sin libros, charlas ni herramientas. [InfoQ: Spec Driven Development: When Architecture Becomes Executable](https://infoq.com/articles/spec-driven-development)
- **Bezael Pérez** (DominiCode; desarrollador frontend y formador en español). Escribió el libro autoeditado "Spec Driven Development: Construye con IA sin Perder el Control" (Leanpub, actualizado el 25-05-2026, con ediciones en inglés y portugués): un flujo de 7 fases, el reparto del PRD en issues, Spec Kit, OpenSpec y otros flujos, y antipatrones. No entra porque es síntesis y divulgación, no un método ni una herramienta original. [Leanpub: Spec Driven Development (español)](https://leanpub.com/sdd-spec-driven-development) · [Leanpub: edición en inglés](https://leanpub.com/spec-driven-development-build-with-ai)
- **Scrum Manager (guía SDD de Juan Palacio)** (marca española de formación en agilidad). Publicó una guía didáctica abierta (CC BY-NC 4.0) sobre SDD en equipos ágiles con IA (v1.0 de abril de 2026; edición vigente de septiembre de 2026, 18 capítulos) que encaja el método de Kiro, Spec Kit y Thoughtworks en Scrum, con antipatrones como el "teatro de especificación" y una etiqueta de madurez por concepto. No entra porque es una síntesis pedagógica de alcance hispanohablante. [Ficha del recurso](https://scrummanager.com/website/c/info/resource.php?id=374) · [Guía SDD en equipos ágiles (PDF)](https://scrummanager.com/skillarena/docs/10/Guia-SDD-equipos-agiles.pdf)
- **Deepak Babu Piskala** (autor independiente, Seattle). Su preprint "Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants" (arXiv 2602.00180, enero de 2026) es una guía de 8 páginas que recorre herramientas desde BDD hasta Spec Kit, Kiro y Tessl. No entra porque los tres niveles que presenta (spec-first, spec-anchored, spec-as-source) son de Birgitta Böckeler y no se los atribuye, es un preprint sin aceptación confirmada y no trae datos empíricos. [arXiv 2602.00180](https://arxiv.org/abs/2602.00180v1)
- **Christopher Clark (Chris Paliqaw)** (instructor de Addison-Wesley Professional). Su curso en vídeo "Spec-Driven Development for Agentic AI" (más de 4 h, con Claude Code) cubre constitución, specs de features, tareas, TDD, replanificación y SDD en proyectos legados. No entra porque sigue el flujo de Spec Kit sin método propio, el curso aún no ha salido (fecha estimada 30-10-2026) y el autor no tiene presencia pública verificable. [InformIT: Spec-Driven Development for Agentic AI](https://www.informit.com/store/spec-driven-development-for-agentic-ai-video-course-9780135995570)
- **Anatoly Volkhover** (ejecutivo tecnológico de Silicon Valley, según su autodescripción). Escribió el libro autoeditado "Agentic Spec-Driven Development" (2026, 198 páginas), con la tesis de que el resultado lo decide la especificación y no el código. No entra porque no tiene reseñas, adopción ni herramientas públicas asociadas. [IBS: ficha del libro](https://www.ibs.it/agentic-spec-driven-development-practical-libro-inglese-anatoly-volkhover/e/9798197989857)

### Investigación: especificaciones formales y verificación con LLM

- **Max Tegmark y la BAIF (Beneficial AI Foundation): vericoding** (BAIF y MIT (Massachusetts Institute of Technology)). En septiembre de 2025 acuñaron "vericoding": un LLM genera código y prueba formalmente verificados a partir de specs formales, frente al "vibe coding". Su benchmark tiene 12.504 specs (Dafny, Verus/Rust y Lean), con un 82 %, 44 % y 27 % de éxito; Tegmark es el autor sénior de un trabajo colectivo. No entra porque es el extremo formal (la spec en lenguaje natural queda excluida a propósito) y su adopción es baja. [arXiv 2509.22908](https://arxiv.org/abs/2509.22908) · [Beneficial-AI-Foundation/vericoding](https://github.com/Beneficial-AI-Foundation/vericoding) · [Max Tegmark: Provably Safe AI (FAR.AI)](https://www.far.ai/events/sessions/max-tegmark-provably-safe-ai-12aee)
- **Google DevAI Research (Michele Tufano, Pat Rondon y equipo).** Proponen la Spec-Driven Test Generation: antes de escribir tests, el agente documenta precondiciones, postcondiciones y comportamientos indefinidos. Sobre bugs reales de Google con Gemini 3 Flash, sube la detección de bugs en 9,8 puntos y la cobertura de ramas en 2,5. Se presentó en SpecOps '26, el primer workshop académico sobre SDD. No entra porque la spec es un andamio de razonamiento derivado del código, no una fuente de verdad mantenida. [Google Research: Grounding AI Agents in Contracts](https://research.google/pubs/grounding-ai-agents-in-contracts-an-empirical-evaluation-of-spec-driven-test-generation/) · [arXiv 2608.17177 (PDF)](https://arxiv.org/pdf/2608.17177)
- **Grupo Sunblaze de UC Berkeley (Dawn Song), con Kaiyu Yang (Meta FAIR (Fundamental AI Research)): benchmark VERINA.** VERINA tiene 189 tareas en Lean, cada una con descripción, código de referencia, especificación formal y tests, y mide por separado la generación de código, de specs y de pruebas (ICLR (International Conference on Learning Representations) 2026). Según la v3, el mejor modelo logra 72,6 % de código correcto, 52,3 % de specs correctas y completas y 4,9 % de pruebas: los LLM todavía escriben mal las specs formales. No entra porque es un benchmark del extremo formal, no SDD. [VERINA en arXiv](https://arxiv.org/abs/2505.23135v2) · [sunblaze-ucb/verina](https://github.com/sunblaze-ucb/verina)
- **Bryan Parno y Sean Welleck, con Pranjal Aggarwal** (CMU). AlphaVerus (ICML (International Conference on Machine Learning) 2025) genera con LLM código Rust verificado con Verus a partir de specs formales, sin datos humanos, y filtra specs desalineadas para evitar el reward hacking cuando la spec es el árbitro. Parno es coautor de Verus y Amazon Scholar en AWS. No entra porque es investigación de vericoding, no SDD en sentido corriente. [AlphaVerus](https://alphaverus.github.io) · [cmu-l3/alphaverus](https://github.com/cmu-l3/alphaverus) · [Página de Bryan Parno](https://www.andrew.cmu.edu/user/bparno/)
- **Shan Lu y Chenyuan Yang (AutoVerus / VeruSAGE; con Chris Hawblitzel y Jacob R. Lorch)** (Microsoft Research y UIUC (University of Illinois Urbana-Champaign)). AutoVerus (OOPSLA (Object-Oriented Programming, Systems, Languages and Applications) 2025, Distinguished Artifact Award) es una red de agentes LLM que genera las anotaciones de prueba para que código Rust verifique contra specs Verus escritas por humanos, con más del 90 % de éxito en 150 tareas. No entra porque la IA no genera ni la spec ni el código, solo la prueba. [AutoVerus en Microsoft Research](https://www.microsoft.com/en-us/research/publication/autoverus-automated-proof-generation-for-rust-code/) · [arXiv 2409.13082](https://arxiv.org/abs/2409.13082) · [microsoft/verus-proof-synthesis](https://github.com/microsoft/verus-proof-synthesis)
- **Clark Barrett (grupo Clover: Chuyue Sun, Ying Sheng, Oded Padon y Clark Barrett)** (Stanford). Clover (Closed-Loop Verifiable Code Generation, 2023-2024) filtra código incorrecto generado por LLM comprobando la coherencia entre código, docstring y anotaciones formales en Dafny; acepta hasta el 87 % de los casos correctos y ningún caso incorrecto adversarial. Sun y Sheng son las coautoras principales; Barrett es el investigador sénior. No entra porque busca coherencia entre tres artefactos, no trata la spec como fuente única de verdad. [arXiv 2310.17807](https://arxiv.org/abs/2310.17807v4) · [POPL 2024, Dafny workshop: CLOVER](https://popl24.sigplan.org/details/dafny-2024-papers/1/CLOVER-Closed-Loop-Verifiable-Code-Generation)
- **Sarah Fakhoury (con Madeline Endres)** (Microsoft Research). Es primera autora de TiCoder (IEEE TSE (Transactions on Software Engineering) 2024), donde el usuario aprueba o rechaza tests generados que funcionan como spec ligera antes de aceptar el código, y coautora de nl2postcond (FSE 2024), que traduce intención en lenguaje natural a postcondiciones formales. No entra porque su línea se solapa con la de Shuvendu Lahiri, que ya está en la lista. [Perfil en Microsoft Research](https://www.microsoft.com/en-us/research/people/sfakhoury/) · [TiCoder en arXiv (2404.10100)](https://arxiv.org/abs/2404.10100)
- **Erik Meijer** (Leibniz Labs, Research Scholar; antes Microsoft y Meta). Propone que el agente entregue su plan de ejecución con una prueba de seguridad y corrección verificable por máquina, escrita en Universalis y comprobada por un checker pequeño antes de ejecutar (keynote "In Code They Act, In Proof We Trust", AI Engineer World's Fair 2026). No entra porque toca el SDD de forma tangencial: la spec es un contrato de las acciones del agente, no la fuente de verdad del código. [Perfil de ponente en AI Engineer](https://www.ai.engineer/speakers/erik-meijer) · [Return of the Theorem (IT Revolution)](https://videos.itrevolution.com/watch/1183220333)

---

## Para seguir investigando

### Artículos y guías

- [Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) — Birgitta Böckeler (15-10-2025). Punto de partida: taxonomía spec-first / spec-anchored / spec-as-source.
- [Spec-driven development with AI: Get started with a new open source toolkit](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit) — Den Delimarsky, GitHub Blog (02-09-2025).
- [Diving Into Spec-Driven Development With GitHub Spec Kit](https://developer.microsoft.com/blog/spec-driven-development-spec-kit/) — Microsoft for Developers (15-09-2025).
- [Kiro and the future of AI spec-driven software development](https://kiro.dev/blog/kiro-and-the-future-of-software-development/) — Marc Brooker (15-07-2025).
- [Spec Driven Development isn't Waterfall](https://brooker.co.za/blog/2026/04/09/waterfall-vs-spec.html) — Marc Brooker (09-04-2026).
- [How to write a good spec for AI agents](https://addyosmani.com/blog/good-spec/) — Addy Osmani (13-01-2026).
- [Spec-Driven Development: 10 things you need to know about specs](https://tessl.io/blog/spec-driven-development-10-things-you-need-to-know-about-specs/) — Patrick Debois (29-10-2025).
- [From Implementation to Intent](https://jedi.be/blog/2025/from-implementation-to-intent/) — Patrick Debois (2025).
- [The Rise of Spec Driven Development](https://www.dbreunig.com/2026/02/06/the-rise-of-spec-driven-development.html) y [The Spec Driven Development Triangle](https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html) — Drew Breunig (2026).
- [My LLM codegen workflow atm](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/) — Harper Reed (16-02-2025).
- [Kiro: Requirements analysis](https://kiro.dev/blog/deep-spec-analysis/) y [Does your code match your spec?](https://kiro.dev/blog/property-based-testing/) — razonamiento automático y PBT aplicados a specs.
- [A chat with Byron Cook on automated reasoning and trust in AI systems](https://www.allthingsdistributed.com/2026/02/a-chat-with-byron-cook-on-automated-reasoning-and-trust-in-ai-systems.html) (17-02-2026).
- [The Three Levels of Spec-Driven Development, and Where the AI Unified Process Sits](https://martinelli.ch/the-three-levels-of-spec-driven-development-and-where-the-ai-unified-process-sits/) — Simon Martinelli (11-10-2026).
- [Superpowers: How I'm using coding agents in October 2025](https://blog.fsck.com/2025/10/09/superpowers/) — Jesse Vincent.
- [How to Use a Spec-Driven Approach for Coding with AI](https://blog.jetbrains.com/junie/2025/10/how-to-use-a-spec-driven-approach-for-coding-with-ai/) — Anton Arhipov, blog de Junie (JetBrains, octubre de 2025).
- [Using PLANS.md for multi-hour problem solving](https://developers.openai.com/cookbook/articles/codex_exec_plans) — Aaron Friel, OpenAI Cookbook (07-10-2025): ExecPlans.
- [Advanced Context Engineering for Coding Agents](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md) — Dex Horthy (agosto de 2025): flujo RPI.
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — Justin Young, Anthropic (26-11-2025).
- [Spec-Driven Development in the Real World](https://buildermethods.com/library/real-spec-driven-development) — Brian Casel, Builder Methods (09-10-2025).
- [Spec Driven Development: When Architecture Becomes Executable](https://infoq.com/articles/spec-driven-development) — Leigh Griffin y Ray Carroll, InfoQ (12-01-2026).
- [Spec-Driven Development: A Spec-First Approach to AI-Native Engineering](https://developer.microsoft.com/blog/spec-driven-development-ai-native-engineering/) y [From spec-first to enterprise-ready: extending GitHub Spec Kit](https://developer.microsoft.com/blog/from-spec-first-to-enterprise-ready-extending-github-spec-kit/) — Apoorv Gupta, Microsoft (2026).
- [Three skills you need for spec-driven development](https://www.warp.dev/blog/three-skills-for-spec-driven-development) — Zach Lloyd, Warp (11-06-2026).
- [Getting started with Spec Driven Development in Antigravity](https://codelabs.developers.google.com/codelabs/getting-started-with-spec-driven-development-in-antigravity) — Google Codelabs.
- [The 30-Plus Framework Landscape: Spec-Driven Development Options in 2026](https://www.softwareseni.com/the-30-plus-framework-landscape-navigating-spec-driven-development-options-in-2026) — SoftwareSeni (29-05-2026) y [Spec-Driven Development in 2026](https://codemyspec.com/blog/spec-driven-development) — CodeMySpec (03-06-2026): comparativas de herramientas.

### Críticas y debate

- [Spec-Driven Development: The Waterfall Strikes Back](https://marmelab.com/blog/2025/11/12/spec-driven-development-waterfall-strikes-back) — François Zaninotto (12-11-2025).
- [SDD isn't Waterfall](https://allstacks.com/blog/spec-driven-development-isnt-waterfall-why-the-ai-coding-bottleneck-changed-everything) — Allstacks, réplica (12-03-2026).
- [Fragmento de Martin Fowler con la crítica de Kent Beck](https://martinfowler.com/fragments/2026-01-08.html) (08-01-2026).
- [Augmented Coding: Beyond the Vibes](https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes) — Kent Beck (25-06-2025).
- [Comparing SDD Frameworks: spec-kit vs OpenSpec vs get-shit-done](https://dabase.com/blog/2026/sdd-framework-comparison/) — Kai Hendry (18-05-2026).
- [What spec-driven development gets wrong](https://augmentcode.com/blog/what-spec-driven-development-gets-wrong) — Amelia Wattenberger, Augment Code (20-02-2026): la "living spec" frente a las specs estáticas.

### Libros y cursos

- [Spec-Driven Development: Engineering with Intent](https://manning.com/books/spec-driven-development) — Hari Krishnan (Manning, MEAP 2026).
- [Spec-Driven Development: From Specs to Code with AI Agents](https://link.springer.com/book/10.1007/979-8-8688-2851-5) — Simon Martinelli (Apress, 2026).
- [Specification by Example](https://www.manning.com/books/specification-by-example) — Gojko Adzic (Manning, 2011).
- [Specifying Systems](https://lamport.org/tla/book.html) — Leslie Lamport (Addison-Wesley, 2002).
- [Program Proofs](https://program-proofs.com/) — K. Rustan M. Leino.
- [Spec-Driven Development with Coding Agents](https://www.deeplearning.ai/short-courses/spec-driven-development-with-coding-agents/) — curso corto de DeepLearning.AI con JetBrains, Paul Everitt (2026); [repositorio del curso](https://github.com/https-deeplearning-ai/sc-spec-driven-development-files).
- [Spec Driven Development: Construye con IA sin Perder el Control](https://leanpub.com/sdd-spec-driven-development) — Bezael Pérez (Leanpub, 2026); [edición en inglés](https://leanpub.com/spec-driven-development-build-with-ai) y [en portugués](https://leanpub.com/spec-driven-development-construa-com-ia).
- [Guía SDD en equipos ágiles](https://scrummanager.com/skillarena/docs/10/Guia-SDD-equipos-agiles.pdf) y [State of the art: SDD en equipos ágiles](https://scrummanager.com/skillarena/docs/10/SOTA-SDD-equipos-agiles.pdf) — Juan Palacio, Scrum Manager (septiembre de 2026, CC BY-NC 4.0).
- [Spec-Driven Development for Agentic AI](https://www.informit.com/store/spec-driven-development-for-agentic-ai-video-course-9780135995570) — Christopher Clark (Addison-Wesley, curso en vídeo; salida estimada 30-10-2026).
- [Agentic Spec-Driven Development](https://www.ibs.it/agentic-spec-driven-development-practical-libro-inglese-anatoly-volkhover/e/9798197989857) — Anatoly Volkhover (autoedición, 2026).

### Repositorios y herramientas

- [github/spec-kit](https://github.com/github/spec-kit) y su [historia](https://github.github.com/spec-kit/history.html)
- [Kiro](https://kiro.dev/) y [Kiro docs: Specs](https://kiro.dev/docs/specs/)
- [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) y [openspec.dev](https://openspec.dev/)
- [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) y [docs.bmad-method.org](https://docs.bmad-method.org/)
- [obra/superpowers](https://github.com/obra/superpowers)
- [Tessl](https://tessl.io/)
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
- [dbreunig/whenwords](https://github.com/dbreunig/whenwords) (librería sin código: solo spec y tests)
- [OpenAI Model Spec](https://github.com/openai/model_spec)
- [GitHub Next – SpecLang](https://githubnext.com/projects/speclang/)
- [Dafny](https://dafny.org/), [TLA+ Foundation](https://foundation.tlapl.us/), [OpenAPI Initiative](https://www.openapis.org/) y [Arazzo](https://www.openapis.org/arazzo-specification)
- GSD: [get-shit-done (archivado)](https://github.com/glittercowboy/get-shit-done) y [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core)
- JetBrains Junie: [gist de Anton Arhipov con el prompt de SDD](https://gist.github.com/antonarhipov/4e89f27b38eab1fa5719a2c169969f7c) y [Junie CLI plan mode](https://junie.jetbrains.com/docs/junie-cli-plan-mode.html)
- [Kiro docs: Feature specs](https://kiro.dev/docs/specs/feature-specs/) (requisitos en notación EARS)
- [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) (SDD al estilo de Kiro para otros agentes)
- [buildermethods/agent-os](https://github.com/buildermethods/agent-os) y su [CHANGELOG](https://github.com/buildermethods/agent-os/blob/main/CHANGELOG.md)
- [mattpocock/skills](https://github.com/mattpocock/skills)
- [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills)
- [MrLesk/Backlog.md](https://github.com/MrLesk/Backlog.md)
- [humanlayer/12-factor-agents](https://github.com/humanlayer/12-factor-agents)
- [PLANS.md en openai/openai-agents-python](https://github.com/openai/openai-agents-python/blob/main/PLANS.md)
- [anthropics/claude-quickstarts: autonomous-coding](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
- [Intent (Augment Code)](https://intentapp.dev), [Traycer: Epic Mode](https://docs.traycer.ai/tasks/epic), [Factory: Spec Mode](https://docs.factory.com/cli/user-guides/specification-mode) y [Qoder: Quest Spec-driven](https://docs.qoder.com/user-guide/quest/spec-driven)
- Verificación formal con LLM: [Beneficial-AI-Foundation/vericoding](https://github.com/Beneficial-AI-Foundation/vericoding), [sunblaze-ucb/verina](https://github.com/sunblaze-ucb/verina), [cmu-l3/alphaverus](https://github.com/cmu-l3/alphaverus) y [microsoft/verus-proof-synthesis](https://github.com/microsoft/verus-proof-synthesis)

### Charlas y podcasts

- ["The New Code"](https://www.youtube.com/watch?v=8rABwKRsec4) — Sean Grove, AI Engineer World's Fair 2025.
- [SE Radio 710: Marc Brooker on Spec-Driven AI Dev](https://se-radio.net/2026/03/se-radio-710-marc-brooker-on-spec-driven-ai-dev/) (04-03-2026).
- [Thoughtworks: What is spec-driven development?](https://www.thoughtworks.com/insights/podcasts/technology-podcasts/what-is-spec-driven-development) — Böckeler y Laura Tacho (28-05-2026).
- [Spec-Driven Development Is Back. But Not How You Think](https://gotopia.tech/sessions/4066/spec-driven-development-is-back-but-not-how-you-think) — Dan North y Gojko Adzic (GOTO; [podcast](https://goto.buzzsprout.com/1714721/episodes/19171518-spec-driven-dev-is-back-but-not-how-you-think-daniel-terhorst-north-gojko-adzic)).
- [Four Patterns of AI Native Development](https://infoq.com/presentations/patterns-ai-native-development/) — Patrick Debois (InfoQ).
- [Devoxx 2025: 8 Talks on Spec-Driven Development](https://jedi.be/blog/2025/devoxx-2025-spec-driven-development-talks/) — selección de Patrick Debois.
- [Thinking Above the Code](https://www.microsoft.com/en-us/research/video/thinking-above-the-code/) — Leslie Lamport (2014).
- [Spec-Driven AI Development: Turning Requirements into Reliable Code](https://info.jetbrains.com/jetbrains-livestream-november20-2025.html) (noviembre de 2025) y [Episode 2](https://info.jetbrains.com/jetbrains-ai-livestream-february11-2026.html) — livestreams de JetBrains con Paul Everitt.
- [Shipping with Codex](https://youtu.be/Gr41tYOzE20?si=ZqfoPD7mnKeXtN4-&t=756) — OpenAI DevDay 2025: Aaron Friel presenta ExecPlans.
- [Tessl podcast ep. 124: Why We Stopped Trusting AI to Write the Plan](https://tessl.io/podcast/124) — Dex Horthy (22-09-2026).
- [Using Spec-Driven Development for Production Workflows](https://www.ai.engineer/talks/IddXPepIAS4-using-spec-driven-development-production-workflows) — Erik Hanchett, AI Engineer World's Fair 2026.
- [仕様駆動開発の理想と現実、そして向き合い方](https://speakerdeck.com/gotalab555/shi-yang-qu-dong-kai-fa-noli-xiang-toxian-shi-sositexiang-kihe-ifang) (El ideal y la realidad del SDD) — Gota, Findy (noviembre de 2025).
- [Provably Safe AI](https://www.far.ai/events/sessions/max-tegmark-provably-safe-ai-12aee) — Max Tegmark, FAR.AI (noviembre de 2025).
- [Return of the Theorem](https://videos.itrevolution.com/watch/1183220333) — Erik Meijer, IT Revolution AI Summit (2026).

### Papers y trabajo académico

- [Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants](https://arxiv.org/abs/2602.00180) — arXiv 2602.00180 (2026).
- [Intent Formalization: A Grand Challenge for Reliable Coding in the Age of AI Agents](https://arxiv.org/abs/2603.17150) — Shuvendu Lahiri (2026).
- [nl2postcond](https://arxiv.org/abs/2310.01831) (FSE 2024) y [Evaluating LLM-driven User-Intent Formalization](https://arxiv.org/abs/2406.09757v2) (FMCAD 2024) — Lahiri y coautores.
- [AI for software engineering: from probable to provable](https://arxiv.org/abs/2511.23159) — Bertrand Meyer (2025-2026).
- [A benchmark for vericoding](https://arxiv.org/abs/2509.22908) — LLMs que generan código verificado en Dafny, Verus y Lean (2025).
- [Dafny as Verification-Aware Intermediate Language for Code Generation](https://arxiv.org/abs/2501.06283) (2025).
- [SpecOps 2026](https://conf.researchr.org/home/specops-2026) — primer workshop académico sobre el ciclo de vida del desarrollo guiado por especificaciones.
- [QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs](https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf) — Claessen y Hughes (ICFP 2000).
- [TLA+ Foundation — GenAI-accelerated TLA+ Challenge](https://foundation.tlapl.us/challenge/index.html) (2025).
- [Spec-Driven Development as Prescribed and as Practiced](https://arxiv.org/abs/2608.25202) — Agarwal, Singhal, Macvean, Vasilescu y Breaux (CMU, 2026; preprint). Dataset [SpecMine en Zenodo](https://doi.org/10.5281/zenodo.22102779), [en Hugging Face](https://huggingface.co/datasets/ShyAgarwal/specmine) y [muestra en GitHub](https://github.com/shyamagarwal13/specmine-official); [Mining Challenge 2027](https://2027.msrconf.org/track/msr-2027-mining-challenge).
- [Easy Approach to Requirements Syntax (EARS)](https://doi.org/10.1109/RE.2009.9) — Mavin, Wilkinson, Harwood y Novak (RE'09, 2009).
- [Grounding AI Agents in Contracts: An Empirical Evaluation of Spec-Driven Test Generation](https://research.google/pubs/grounding-ai-agents-in-contracts-an-empirical-evaluation-of-spec-driven-test-generation/) — Tufano, Rondon y equipo, Google (SpecOps '26; [arXiv 2608.17177](https://arxiv.org/pdf/2608.17177)).
- [VERINA: Verifiable Code Generation Arena](https://arxiv.org/abs/2505.23135v2) — Ye, Yan, He, Kasriel, Yang y Song (ICLR 2026).
- [AlphaVerus](https://alphaverus.github.io) — Aggarwal, Parno y Welleck (ICML 2025).
- [AutoVerus: Automated Proof Generation for Rust Code](https://arxiv.org/abs/2409.13082) — Chenyuan Yang, Shan Lu y coautores (OOPSLA 2025).
- [Clover: Closed-Loop Verifiable Code Generation](https://arxiv.org/abs/2310.17807v4) — Sun, Sheng, Padon y Barrett (SAIV (Symposium on AI Verification) 2024).
- [TiCoder: LLM-based Test-driven Interactive Code Generation](https://arxiv.org/abs/2404.10100) — Sarah Fakhoury y coautores (IEEE TSE 2024).
