# Responsabilidades del toolchain de Clean y mejoras propuestas

Análisis de las responsabilidades de los cuatro binarios del toolchain de Clean
(Manager `cln`, Framework, Compiler, Runtime) tal como las fijan las specs del repositorio
`clean-language-foundation` (commit 338b544e, 2026-10-26), y las mejoras que sobreviven a
una verificación adversarial.

## Cómo se hizo

Un workflow de 80 agentes en cinco fases: 7 lectores (uno por componente, más el grafo de
llamadas, los concerns transversales y la terminología) produjeron mapas con tensiones y
cita archivo:línea; 5 lentes (cohesión, seguridad, experiencia de desarrollador,
operabilidad, calidad de la spec) propusieron 34 mejoras; un agente las fusionó en 22; cada
una pasó por 3 refutadores (evidencia, decisiones ya tomadas, valor) y sobrevivió con 2 de 3
votos a favor: 9 aprobadas, 13 refutadas. El informe que sigue es la síntesis.

---


Rutas relativas a `specs/`. *Launch*: lo que el Framework devuelve y el Manager arranca.
*Handshake*: la comprobación `--version --json` previa a cada despacho. *Lock*: `clean.lock`.

## Parte 1 — Responsabilidades

### Manager (`cln`)

«The front door: takes every command, installs and pins versions, resolves libraries, verifies
downloads, and starts the Runtime with the launch the Framework prepares» (boundaries.md:17).

- `[project] version`: boundaries.md:86, :96 y :106 lo dan al Manager (`cln ship --tag`);
  MA-03 (Project files) en manager/architecture.md:61, MA-09 (What the Manager reads from
  `clean.toml`) en :76, manager/README.md:53 y project-manifest.md:97 lo omiten. El
  `versionFile` de `toolchain.toml`, el commit y el tag (contracts.md:88; cln.md:353) no están
  en ninguna lista cerrada. Mejora 5.
- `cln new`: el Framework escribe `[toolchain]` y `[dependencies]` (framework/architecture.md:133;
  cli.md:59), tablas que MA-03 (Project files) reserva al Manager, y el verbo `new` no recibe los
  pins (process-contracts.md:313). Mejora 2.
- `[dev] watch`/`watchExclude`: `cln dev` es «the only watch loop» (cln.md:207) y `[dev]` «is
  consumed by `cln dev`» (project-manifest.md:511), pero MA-09 (What the Manager reads from
  `clean.toml`) no incluye `[dev]` y el resultado de `run` solo trae `hotReload`
  (process-contracts.md:568). Mejora 6.
- Paquetes host (el host browser, edge o embedded instalado aparte del runtime): `cln sync` instala
  solo `[toolchain]` (cln.md:492) y el paquete «when a build or run needs it» (cln.md:462), contra
  C-18 (Offline operation) (concerns.md:91); el manifiesto no admite `host:embedded`
  (supply-chain.md:50) y `build` no acepta `--edge-host` (process-contracts.md:317) aunque MA-08
  (Host packages) lo pasa (manager/architecture.md:75). Mejora 3.
- Estado del Manager que acaba en el Framework: `cln fix --list` «is answered by the Framework»
  (error-reporting.md:1024) con exit *dispatch* (cln.md:266), pero MA-61 (Unreadable file) lo hace
  salir con MGR018 (StateFileInvalid) (manager/architecture.md:208) y compara con versiones
  instaladas (error-reporting.md:1027). Mejoras 1 y 9.

### Framework (`clean-framework`)

«The project builder: reads the project, lowers it, runs block handlers, drives the compiler,
packages the result, and prepares the launch» (boundaries.md:18).

- Cinco declaraciones de su rol que difieren: §2.2 omite `api-spec`, `api-sdk`, `why` y
  `library-build` (process-contracts.md:280, :286-289); README «five jobs» (README.md:28);
  boundaries.md:142 «the Compiler's error reports» vs error-reporting.md:67 «compiler, library
  and framework»; framework/architecture.md:108 «never opens a database or the network» vs
  boundaries.md:148. Mejora 9.
- Decisiones de versión y lecturas de estado del Manager, contra el test de frontera
  (boundaries.md:152): `installed.manager` (mcp-server.md:587), FRM107 (ComponentUnavailable) por
  pin no instalado (:44), compilador por defecto sin proyecto (:43), paseo de directorios (:40),
  `lock_up_to_date` (:372); red fuera de boundaries.md:148: registro (:529), dashboard (:593).
  Mejora 1.
- `cln new`: primera escritura de las dos tablas del Manager sin canal para los pins
  (process-contracts.md:313; PC-01 (Argv is the only configuration channel), :44). Mejora 2.
- `cln explain`: cln.md:276 «every code, of every component and library» desde el índice del
  compilador vs framework/architecture.md:150 (código de librería desde `[mcp.diagnostics]`);
  diagnostics.md:296 lo sirve por `query`; mcp-server.md:613 «It starts no process». Mejoras 1
  y 8.

### Compiler (`clean-compiler`)

«The translator: a pure function from one request document to a WebAssembly component and its
output files, plus the API, docs index and language server built on the same data»
(boundaries.md:19).

- El docs index (índice de documentación embebido en el binario) cubre «every diagnostic code»
  (boundaries.md:167), familias MGR, REP, RUN, SRV y BRG incluidas, que el compilador «never
  emits» (compiler/architecture.md:185); un código que el registro añade tras la release del
  compilador no se explica offline, contra C-20 (Structured introspection) (concerns.md:98) y
  C-09 (Small surface) (:49). Mejora 8.
- Dos mecanismos para el índice: diagnostics.md:296 y :304 y contract.md:376 lo sirven por
  `query`; mcp-server.md:613 «It starts no process» y la tabla §7 (:618) no tiene consulta
  `explain`. Mejoras 1 y 8.
- Ningún archivo define el índice (contenido, esquema, procedencia desde las specs), aunque
  overview.md:216 exige un dueño por interfaz. La mejora 8 le da forma para los códigos.

### Runtime (`clean-runtime`)

«The host: runs the component as the host of one world, and plugs in the capability bridges the
build selected» (boundaries.md:20); el §2.4 dice «The hosts» (:186).

- Paquetes host como quinto artefacto versionado: «released with `clean-runtime`»
  (hosts/README.md:20) «at the same version» (embedded/interface.md:16), pero con manifiesto
  propio (SC-01 (Every release is signed), supply-chain.md:20), árbol `~/.cln/hosts/`
  (manager/architecture.md:39) y entrada `[host]` del lock derivada del pin (lockfile.md:68, :94).
  Mejora 3.
- Edge sin camino: MA-08 (Host packages) pasa «a `browser` or `edge` package directory to the
  Framework» (manager/architecture.md:75; :151), `build` solo tiene `--browser-host` y
  `--embedded-host` (process-contracts.md:317); edge/interface.md:106 lo registra en el lock.
  Mejora 3.

## Parte 2 — Mejoras propuestas

**1. Sacar del Framework toda consulta de estado del Manager y definir la invocación sin
proyecto** (impacto alto; tres lentes)

Problema. El test de frontera excluye «a version decision» (boundaries.md:152), pero `cln fix
--list` compara `fixed_in` con versiones instaladas (error-reporting.md:1027),
`check_reported_fixes` devuelve `installed.manager` sin flag que lo traiga (mcp-server.md:587;
process-contracts.md:332, :336; mcp-server.md:90 veda llamar a `cln`), `list_ecosystem` hace GET
al registro (mcp-server.md:529) fuera de boundaries.md:148, y el servidor MCP pasea directorios
(:40) con `--project` obligatorio (process-contracts.md:252) y un modo sin proyecto (:42-43) que
la gramática no permite. Dos mecanismos para el índice: diagnostics.md:296 vs mcp-server.md:613.

Cambio.
- (a) `cln fix --list` pasa a nativo del Manager (cuenta, `sent.toml`, versiones, red); `fix`
  pierde `--list` y `--all` (process-contracts.md:322, :352-353); error-reporting.md:1024 dice
  «answered by the Manager»; cln.md:266 parte el exit (`fix` *dispatch*, `fix --list` *native*).
- (b) Sin fichero `--toolchain-state`: `installed` se elimina o llega por flag (`--installed=…`
  o `--manager-version`); `lock_up_to_date` sigue vivo en el Framework (las siete reglas de
  lockfile.md:86 se computan desde `--project`, `--lock`, `--libraries`, y el Manager no las aplica
  a `cln mcp`: lockfile.md:104-105), con lockfile.md como única definición normativa;
  `list_ecosystem` se elimina o sigue con `--registry=<url>` y una línea más en boundaries.md:148
  (sin snapshot: rompería C-18 (Offline operation) y la búsqueda `query`/`limit` de :529).
- (c) mcp-server.md:40 pierde el paseo (el proyecto es `--project`; cln.md:15 ya lo hace el
  Manager); :44 se reduce a «stopped responding» de FRM107 (ComponentUnavailable), porque MA-13
  (Missing versions stop the command) y PC-10 (The Manager handshakes before it dispatches)
  garantizan el pin instalado.
- (d) `--project`, `--lock` y `--libraries` opcionales para `explain`, `templates`, `report` y
  `mcp`; fuera de proyecto el Manager pasa `--compiler` del default de MA-14 (User defaults), como
  PC-10 (The Manager handshakes before it dispatches) paso 3 ya prevé (process-contracts.md:157);
  PC-02 (Flag syntax) :53 añade el caso sin proyecto (cwd del usuario); un código de librería sin
  proyecto es FRM106 (ItemNotFound); los tools de proyecto siguen fallando con FRM102
  (NoProjectSelected).
- (e) Fila `explain` en la tabla §7 de mcp-server.md (:618); :613 pasa a «runs `clean-compiler
  query explain`»; cln.md:276, boundaries.md:141 y :167 adoptan la regla de dos fuentes de
  framework/architecture.md:150. Se descarta que el Manager llame a `query explain` él mismo
  (contradice process-contracts.md:423 y :31).
- (f) Opcional, una frase en §2.2: «proyecto o librerías resueltas → Framework; `~/.cln`,
  registro, dashboard o versión → Manager».

Beneficio. El test de frontera del Framework se cumple sin excepción y lee solo lo que su argv
nombra (salvo su cola de informes); MGR018 (StateFileInvalid) lo emite quien posee el fichero;
`cln explain` funciona en cualquier directorio y offline (cln.md:278); un mecanismo para el índice.

Riesgo. Toca C-12 (MCP is the AI-facing contract) (`check_reported_fixes` pierde `installed` o lo
recibe congelado), mcp-server.md §1 y §6.20, error-reporting.md §9.3, el encaminamiento de
cln.md:28, boundaries.md §2.2 y la gramática argv del Framework. La lente de valor lo refutó solo
por el fichero `--toolchain-state`, aquí ya retirado.

**2. `cln new`: un dueño y un canal para la primera escritura de `[toolchain]` y
`[dependencies]`** (alto; tres lentes)

Problema. MA-03 (Project files) reserva `[toolchain]` (`cln use`) y `[dependencies]` al Manager
(manager/architecture.md:61; boundaries.md:104-105; project-manifest.md:152), pero el verbo `new`
escribe ambas (framework/architecture.md:133; cli.md:59) sin canal para los pins: argv
`--template`, `--starter-libraries`, `--with-shared` (process-contracts.md:313), y PC-01 (Argv is
the only configuration channel) veda `config.toml`, donde MA-14 (User defaults) los guarda (:88).
Para `[dependencies]` llegan nombres y lock, no la política de requisito (project-manifest.md:174).
Derivas: `--libraries` en framework/architecture.md:131 y getting-started.md:31 contra cln.md:59
(:5 «No other file lists commands»); el lock de `new` existe antes que el directorio
(process-contracts.md:253; LCK-12 (Atomic writes), lockfile.md:80).

Cambio. El verbo `new` crea directorio, carpetas, starters y `clean.toml` sin `[toolchain]` ni
`[dependencies]`; tras la respuesta el Manager escribe ambas por los caminos de `cln use` y
`cln add` (sin heredar la confirmación de cln.md:386: decir si `new` pregunta) y escribe
`<name>/clean.lock` conforme a LCK-02 (Only the Manager writes it) y LCK-12 (Atomic writes); el
lock temporal es solo entrada del verbo. Reescribir framework/architecture.md:131 y :133,
cli.md:59, cln.md:64, getting-started.md:31; boundaries.md:104-105, MA-03 (Project files) y
project-manifest.md:152 añaden `cln new`; cln.md:75 nombra el exit de una escritura fallida del
Manager (como cln.md:388); PC-02 (Flag syntax) :53 fija el cwd de `new` (el padre de `<name>`);
MA-12 (Missing pins stop the command) gana «inside a project», ya necesario por PC-10 (The Manager
handshakes before it dispatches) paso 3 (process-contracts.md:157). Alternativa:
`--toolchain=compiler=<v>,framework=<v>,runtime=<v>` en `new`, con excepción única en MA-03
(Project files) y boundaries.md:102-106 (la política de requisito pasaría al Framework).

Beneficio. Un escritor por tabla en todo momento; sin canal nuevo; PC-01 (Argv is the only
configuration channel) y MA-03 (Project files) exactos; el verbo `new` no decide versiones
(boundaries.md:152); C-01 (Learnability) deja de depender de un traspaso indefinido; un archivo
lista el comando.

Riesgo. Toca «`[toolchain]`, through `cln use`» (boundaries.md:104; project-manifest.md:152) y
MA-14 (User defaults). Dos escritores de `clean.toml` en un comando ya es práctica en
`cln add --scaffold` (framework/architecture.md:135-137).

**3. Paquetes host oficiales como ficheros de la release del runtime** (alto; dos lentes)

Problema. Los paquetes browser, edge y embedded salen «with `clean-runtime`» «at the same
version» (hosts/README.md:20; embedded/interface.md:16) pero son un quinto artefacto:
manifiesto propio (SC-01 (Every release is signed), supply-chain.md:20) sin valor
`host:embedded` (:50), árbol `~/.cln/hosts/` (manager/architecture.md:39), instalación «when a
build or run needs it» (cln.md:462) que `cln sync` (:492) y `cln fetch` (:424) no cubren, de
modo que el primer build offline para con MGR022 (ArtifactNotInStore) (MA-43 (Offline),
manager/architecture.md:140) contra C-18 (Offline operation) (concerns.md:91); entrada `[host]`
del lock derivada del pin (lockfile.md:68, :94); y MA-08 (Host packages) pasa un paquete edge
que `build` no acepta (process-contracts.md:317). La costura Framework↔paquete sí queda acotada
transitivamente por MA-20 (Every pair is checked, both ways): falta definir «matches» para
browser y edge.

Cambio. Los tres paquetes son ficheros `platform: any` (supply-chain.md:54) del manifiesto de
`runtime`, desempaquetados en `~/.cln/versions/runtime/<v>/hosts/<kind>/` por `cln install
runtime` y `cln sync`, siempre eager: la variante bajo demanda rompe MA-01 (One version, one
directory) (manager/architecture.md:54). El paso 5 de verificación (supply-chain.md:119) descarga
también los ficheros `any`. Se eliminan `~/.cln/hosts/` (:39), `host:browser`/`host:edge` (:50) y
el paso instalar-y-registrar de MA-08 (Host packages), que queda en pasar `<runtime>/hosts/<kind>/`
como `--browser-host`, `--embedded-host` y `--edge-host` (nuevo en process-contracts.md:317).
`[host]` del lock solo para hosts de terceros (lockfile.md:65-69; regla 7 sin la cláusula
`[toolchain] runtime`). Reescribir project-manifest.md:156, boundaries.md:197 y :199,
hosts/README.md:20, cln.md:462, process-contracts.md:531, :542 y :575-576, edge/interface.md:106,
manager/architecture.md:151, supply-chain.md:122, lockfile.md:12.

Beneficio. Una release, una firma, un rango `compat.json`; `cln sync` prepara el trabajo offline
para los seis mundos; lock más corto; un árbol menos bajo C-14 (Bounded on-disk footprint);
`--edge-host` y `host:embedded` se cierran por construcción.

Riesgo. Toca MA-08 (Host packages), la lista de SC-01 (Every release is signed), la tabla `[host]`
del Lockfile y la nota de C-16 (Hosts are swappable) (concerns.md:84); la descarga del runtime
crece con el bundle browser y un firmware por familia de placa, coste a aceptar. La lente de
valor lo refutó por ese coste y propone en su lugar cuatro arreglos puntuales: `host:embedded`
en supply-chain.md:50, `--edge-host` en `build`, `cln sync` instala el paquete que `[build]
target` pide, y `cln uninstall`/`cln cleanup` cubren `~/.cln/hosts/` (cln.md:496, :514).

**4. Lanzamientos de test con una configuración restringida que devuelve el Framework**
(alto; una lente)

Problema. PC-60 (One Runtime per test launch) arranca `clean-runtime --world=cli <wasm>` sin
`config` (process-contracts.md:616, :619) y sin `--config` «every key takes its default»
(cli/interface.md:167): todo el entorno del proceso (:158), cwd en lectura-escritura (:157), HTTP
«unrestricted» (:159). Un test corre el código de librería alcanzable (contract.md:363) con los
secretos de un CI (`CLN_API_KEY`, error-reporting.md:130), escritura en el proyecto y red, contra
CV-03 (Locked and read-only) (contracts.md:55) y «no ambient authority» (component-model.md:58);
server y worker ya deniegan por defecto (configuration.md:207; worker/interface.md:192).

Cambio. (1) `test` y `conformance` devuelven `config` en cada launch: un `host-config` de test
(fila nueva en process-contracts.md:213-214) con `cli.inheritEnv = false`, `cli.preopenCwd =
false`, un `cli.preopens` de `tests/fixtures/` (contracts.md:243) en solo lectura,
`environment.pass = []` y `outboundHttp.allowedHosts = []`; el host `cli` lee las tablas
`[environment]` y `[outboundHttp]` que ya definen server (configuration.md:203, :207) y worker
(worker/interface.md:192), sin clave `http` nueva. (2) Una tabla `[test]` en `clean.toml`
(allowlist de variables y hosts) que el Framework baja a ese fichero, como `[dev]`: entra en el
esquema cerrado (project-manifest.md:88, CFG004 (UnknownManifestKey)) y en «Not lowered»
(:505-513); MA-09 (What the Manager reads from `clean.toml`) no cambia. (3) PC-60 (One Runtime
per test launch) sustituye «`config` and `assets` are absent» (:616) por «`config` is the test
`host-config` artifact»; el Manager ya lo pasa por :572. Alternativa más ligera (lente de valor):
para `build --tests`, `test` y `conformance` el Framework baja `security.allowed_imports`
(project-manifest.md:496) sin `wasi:cli/environment`, `wasi:filesystem/*` ni `wasi:http/*`,
salvo lo que `[test]` liste; la denegación ocurre al compilar con COM013 (ProgramImportDenied) y
LIB013 (HostFunctionSandboxDenied) (contract.md:297) y el Runtime no cambia.

Beneficio. El código de una dependencia no lee secretos, no escribe en el proyecto ni sale a la
red durante `cln test` y `cln verify`; coherente con «Elision is a security property»
(contract.md:370); la decisión vive en quien ya prepara el launch (boundaries.md:139).

Riesgo. Cambio de conducta para suites que usan entorno o red (necesitan `[test]`); toca PC-60
(One Runtime per test launch), el esquema del launch, la tabla `[cli]` y Testing. No cubre
`cln run` de un proyecto `cli` (mismos defaults; `host-config` solo existe para `server`,
process-contracts.md:221) ni `cln library build`, que corre tests dentro del Framework
(authoring.md:315) contra boundaries.md:150: hueco aparte. `cln test` corre bajo PC-41 (Other
dispatches forward) (:959), no PC-40 (`cln run` replaces itself); la herencia del entorno es
conducta por defecto, no escrita.

**5. Lista cerrada de ficheros del Manager: un dueño, con `[project] version`, `versionFile`
y `.git/`** (alto; una lente)

Problema. boundaries.md:86, :96 y :106 dan al Manager `[project] version`; MA-03 (Project files)
(manager/architecture.md:60-61), MA-09 (What the Manager reads from `clean.toml`) (:76),
manager/README.md:53 y project-manifest.md:97 lo omiten, y boundaries.md:108 remite a MA-02 (Nothing
outside the footprint) y MA-03 (Project files) como las reglas de su lista. `cln ship --tag` escribe
además `toolchain.toml [release] versionFile` y hace commit y tag (contracts.md:88; cln.md:353),
fuera de la tabla «and no others» (boundaries.md:82), de MA-02 (Nothing outside the footprint)
(manager/architecture.md:55-59) y de C-14 (Bounded on-disk footprint) (concerns.md:65).

Cambio. Elegir un dueño de la lista (Boundaries, al que los demás enlazan por :5 y :11, o MA-03
(Project files) y MA-09 (What the Manager reads from `clean.toml`) con :108 y :93 como base) y que
el otro enlace. Añadir `[project] version` a MA-03 (Project files), MA-09 (What the Manager reads
from `clean.toml`), README.md:53 y project-manifest.md:97; añadir a MA-02 (Nothing outside the
footprint), de ámbito global, el `versionFile` de un repositorio de componente u host; añadir a
MA-02 (Nothing outside the footprint), MA-03 (Project files), C-14 (Bounded on-disk footprint) y la
tabla de boundaries.md:82-91 el `.git/` (un commit, un tag, solo `cln ship --tag`; las lecturas de
`core.hooksPath` ya están en :91) y la lectura de `toolchain.toml` `[verify]` y `[release]`. C-14
(Bounded on-disk footprint) ya lista `clean.toml` entero: solo gana el commit y el tag. Se descarta
mover el bump fuera del Manager: un proyecto Clean no tiene `toolchain.toml` (CV-11 (CI uses the
digest), contracts.md:150) ni hay verbo del Framework para git.

Beneficio. Una lista, un dueño; un revisor obtiene la misma respuesta desde MA-03 (Project files)
y desde Boundaries; `cln ship --tag` deja de violar MA-02 (Nothing outside the footprint) y
MA-03 (Project files) tal como están escritos.

Riesgo. Toca la decisión de que el Manager corre `cln ship` (boundaries.md:78; contracts.md §3
paso 3, :88) solo en su redacción; la garantía de huella ya es falsa hoy, y escribirla con la
excepción acotada la hace verdadera.

**6. `[dev] watch` y `watchExclude` viajan en el resultado de `run --dev`** (medio; tres
lentes)

Problema. `cln dev` es «the only watch loop» (cln.md:207) y «watches the source tree» (:192);
`[dev]` «is consumed by `cln dev`» (project-manifest.md:511) con `watch` y `watchExclude`
(:442-443); pero MA-09 (What the Manager reads from `clean.toml`) cierra la lista sin `[dev]`
(manager/architecture.md:76; boundaries.md:93) y el resultado de `run` solo trae `hotReload`
(process-contracts.md:568). Quien vigila no puede leer qué vigilar. process-contracts.md:817 y
cln.md:193 nombran `clean.toml` como fuente de `hotReload` para el Manager, lectura que MA-09
veda, aunque :578 ya toma el valor del resultado.

Cambio. El Framework sigue como único lector de `[dev]` (precedente: process-contracts.md:370) y
añade `watch` (rutas relativas resueltas; vacío si `[dev] watch = false`) y `watchExclude` a la
tabla del resultado de `run --dev` (:562-568), ausentes fuera de `--dev` y en los test launches
(:614); definir qué hace el Manager si faltan (Framework antiguo). Reescribir :817 y cln.md:193
a «cuando el `hotReload` del resultado…»; :370, cli.md:66 y glossary.md:150 nombran los campos;
project-manifest.md:511 pasa a «lowered by the Framework into the `run --dev` result». Como
`cln dev` llama a `run` en cada rebuild (:298), un cambio de `[dev]` surte efecto al siguiente.
Se descartan añadir `[dev]` a MA-09 (segunda tabla con dos lectores) y el verbo stream `dev` del
Framework (rompería el paso 1 del build order, del Manager: PC-50 (Each step belongs to one
component), :122; boundaries.md:146-147).

Beneficio. Cierra un hueco sin dueño en el comando de uso diario; el canal es la respuesta que el
Framework ya usa (:493); MA-09 (What the Manager reads from `clean.toml`) sigue cerrado;
`hotReload` con una fuente; cambio aditivo bajo PC-20 (Strict writers, tolerant readers) (:223).

Riesgo. Dos campos opcionales en un documento de `schema_version` 1; toca project-manifest.md:511 y
cln.md:192-193; mantiene que `cln dev`, no el Framework, posee el bucle.

**7. Acotar los `dataFiles` de una librería a `app/`, `public/` y `clean.toml`** (medio; una
lente)

Problema. La garantía del sandbox (entorno sin importaciones donde corre el handler) es que
solo ve «the data files its library declares» (block-handlers.md:275), pero el único límite al
patrón es «no `..`» (package-format.md:226) y el Framework «reads every matching file and
passes the contents» (:229). Una librería puede declarar `.cln/dev/admin-token` (PC-73
(Hand-off), process-contracts.md:797; PC-72 (Generation) :795 «never … a bundle»),
`.cln/traces/*.json` con cuerpos completos (:696; error-reporting.md:739), `.cln/repro/` o un
secreto `<key>File` del proyecto (configuration.md:28, :32), y el IR del handler entra en el
componente; `cln dev` vuelve a correr los handlers en cada rebuild con el token presente
(:298). Los scaffolds ya están acotados a `app/`/`public/` (package-format.md:248); SC-02
(Registry libraries are signed by the registry) «does not certify the library's quality»
(supply-chain.md:21).

Cambio. Package Format §4.6: un patrón empieza por `app/` o `public/`, o es exactamente
`clean.toml` (:228 se mantiene); cualquier otro es LIB004 (LibraryManifestInvalid), con un bullet
nuevo en las condiciones de semantics.md:2224-2230 y otro en §7.3 (package-format.md:369) con
«`cln library build` and every reader reject», como en :199. Opcional: `cln add` imprime los
patrones junto a las capacidades (cln.md:386). Se descartan (3) —semantics.md:2273-2274 ya asigna
la llamada a `cln library build` y la importación al Framework «when it loads the package»; a lo
sumo un enlace desde block-handlers.md:275 y :297— y (4) —boundaries.md:11 prohíbe restatear y
:130 ya enlaza—. Hallazgo aparte: LIB007 (CompiletimeSideEffect) tiene fase `expand`
(error-codes.md:320) pero su definición lo sitúa en la carga del paquete (fase `config`).

Beneficio. La garantía «solo ficheros declarados» tiene enforcer en el build del proyecto
consumidor, donde está la frontera de confianza; el límite es el complemento de lo que
project-manifest.md:52 y error-reporting.md:685 ya protegen; ninguna librería publicada se ve
afectada (`locale`: locale.md:82; `ui`: ui/architecture.md:13).

Riesgo. Una librería que leyera `clean.lock` o `host.toml` al compilar necesitaría otro mecanismo;
toca Package Format §4.6 y §7.3, Semantic Rules LIB004 (LibraryManifestInvalid) y, si (2),
cln.md:386. Componentes: Framework; Manager solo en (2).

**8. Cada componente publica las explicaciones de sus propios códigos (`codes.json`)** (medio;
una lente)

Problema. El compilador carga «the docs index … of every diagnostic code» (boundaries.md:167),
«every code, of every component and library» (cln.md:276), familias RUN, MGR, REP, SRV y BRG
incluidas, que «never emits» (compiler/architecture.md:185); el índice está «built into the
compiler» (contract.md:376) y su directorio no tiene fichero de docs
(manager/architecture.md:23-29). Un código que el registro (error-codes.md:8; §4, :110) añade
tras la release del compilador y que un runtime dentro del rango `compat.json` emite no tiene
explicación offline —ausente, no desfasada: error-codes.md:33—, contra C-20 (Structured
introspection) (concerns.md:98) y C-09 (Small surface) (:49). Y el mecanismo se afirma de dos
modos: `query` (diagnostics.md:296, :304; contract.md:376) vs «It starts no process»
(mcp-server.md:613) sin fila `explain` en §7 (:618).

Cambio. Cada release publica `codes.json` (`schema_version`, una entrada por código de sus
familias, en la forma del documento de explicación de diagnostics.md:304), listado en su
manifiesto firmado e instalado junto a `compat.json`; `cln`, sin directorio de versión
(manager/architecture.md:23-24), lo deja en `~/.cln/bin/codes.json`, repuesto por `cln
self-update`. El Manager pasa `--codes=<path>[,…]` (flag común junto a `--wit`,
process-contracts.md:243-256) a `explain` y `mcp`; el Framework responde un código core desde
esos ficheros —también los que el compilador emite sin poseer: LIB008 (CompiletimeTypeError),
LIB011 (HostFunctionSignatureMismatch), LIB012 (HostFunctionUnbound), LIB013
(HostFunctionSandboxDenied), MEM002 (ArenaValueEscapes), compiler/architecture.md:178— y uno de
librería desde `[mcp.diagnostics]`, sin proceso (mcp-server.md:613 pasa a ser verdad). El
índice del compilador guarda solo datos de lenguaje y su propio `codes.json`;
`list_error_codes` desaparece; `LanguageMeta` (mcp-server.md:145) gana `owner` y
`owner_version`. Reescribir boundaries.md:167 y :141, cln.md:276, contract.md:376,
process-contracts.md:281 (`--compiler` «—» para `explain`), :304, :308, mcp-server.md:26-29 y
:295, framework/architecture.md:149, diagnostics.md:304, supply-chain.md:119. La comprobación
contra el registro va en la etapa `snapshot` o `lint` vía `toolchain.toml [verify]`, no en una
etapa nueva (CV-01 (No skipping, no adding)). Dirección opuesta a la mejora 1(e): elegir una.

Beneficio. Cada código viaja con el componente que lo posee y emite, y la explicación coincide
con el set pinado (C-20 (Structured introspection)); el compilador pierde una carga ajena (C-09
(Small surface)); un mecanismo para el índice; explicaciones testeables con ficheros fixture.

Riesgo. Toca boundaries.md:167 y la tabla §7 de mcp-server.md; cuatro ficheros a mantener en
sintonía con el registro. La lente de valor lo refutó: el texto es dato de la foundation
(diagnostics.md:300), serían cuatro snapshots en vez de uno con más maquinaria, y cada
diagnóstico ya lleva `doc_url` (diagnostics.md:59); su alternativa es corregir
mcp-server.md:613, añadir la fila `explain` (= mejora 1(e)) y, si se quiere, una frase: código
ausente del índice → `doc_url` y aviso de actualizar el compilador.

**9. La lista de responsabilidades del Framework coincide con la tabla de verbos y con una
superficie de red enumerable** (medio; una lente)

Problema. framework/architecture.md:24 dice que §2.2 es la única declaración, pero §2.2 omite
`api-spec`, `api-sdk`, `why` y `library-build` (process-contracts.md:280, :286-289); README.md:28
cuenta «five jobs»; boundaries.md:142 dice «the Compiler's error reports» mientras
error-reporting.md:67 dice «compiler, library and framework» y :494 envía FRM004
(FrameworkInternalError) desde el build path; framework/architecture.md:108 «never opens a
database or the network» y :158 «the compiler's error reports» contradicen boundaries.md:148 y el
§9 del mismo archivo. Red: :148 permite dos destinos; cli.md:25 «one network traffic»;
mcp-server.md:529 añade el registro y :593 el dashboard, con `installed.manager` (:587) sin
fuente en argv (process-contracts.md:332, :336; mcp-server.md:90).

Cambio. §2.2 añade `api-spec`/`api-sdk` (OpenAPI y SDKs), `why` (diagnósticos del último build)
y `library-build` (validar, probar y empaquetar una librería); `config-*` y `templates` ya los
cubren :126 y :143. boundaries.md:142 pasa a «error reports: the build path's compiler, library
and framework failures, and those filed through `cln report`, `cln report submit --file` and the
MCP `report_error` tool, whatever component they name» (error-reporting.md:497;
mcp-server.md:539); framework/architecture.md:108 y :158 se alinean. `cln fix --list` pasa al
Manager (= mejora 1(a); resuelve el reparto que ya existe: manager/architecture.md:188 y MA-61
(Unreadable file) :208 vs cln.md:266). `check_reported_fixes` conserva la lectura del dashboard y
pierde `installed` y la comparación (o recibe `--installed=<json>` en `mcp`: decidir una ruta);
`list_ecosystem` se elimina o se enumera en :148, sin snapshot. :148 nombra exactamente los
destinos; cli.md:25 se corrige; sustituir el «five jobs» del README es opcional (README.md:38 ya
enlaza).

Beneficio. Una lista que coincide con la tabla de verbos; el test de frontera (boundaries.md:152)
se cumple; la excepción de red queda enumerable; Error Reporting y Boundaries coinciden en quién
envía los informes FRM y LIB.

Riesgo. Cambia el despacho de un comando (`cln fix --list` *native*; C-13 (Single front door) no
se toca) y la semántica de dos tools bajo C-12 (MCP is the AI-facing contract); si se mantienen,
hay que ensanchar :148 y el test de frontera.

## Descartadas en verificación

- **Documento de launch único para `run` y `migrate`**: `host.toml` nunca va en un `.clapp`
  (framework/architecture.md:110) y la regla del manifiesto junto a `<wasm>` es deliberada
  (process-contracts.md:543); lo real —dónde está el registro `[data]` para `migrate` y quién
  decide `--config`— son arreglos puntuales (`--bridges`/`--manifest` en `migrate`).
- **Un solo emisor de informes (el Manager)**: el Framework necesita credencial y dashboard para
  `cln fix --list` y `check_reported_fixes` (mcp-server.md:90 veda el callback), `report_error`
  perdería `report_id`/`fingerprint` síncronos, y entregar el informe ya saneado rompe el
  fingerprint sobre el mensaje sin sanear (error-reporting.md:397, :606); salvable solo la mitad
  del Runtime (sin drain al arranque).
- **Nombrar la «segunda tarea» del Manager (gate de repositorio)**: ya está en boundaries.md:78 y
  contracts.md; process-contracts.md:31 solo cubre llamadas entre componentes; el `cln` pinado se
  instala por paquete (MA-30 (Install path)); lo que queda son filas de la tabla cerrada,
  absorbidas por la mejora 5.
- **Captura de `cln repro` al Framework**: la redacción es deber de cada emisor
  (error-reporting.md:481, :485), el token ya llega al Framework por PC-74 (Readers)
  (process-contracts.md:804), y la captura pasaría a depender de un Framework, lock y store sanos
  justo cuando algo falló; basta una fila de lectura opaca en boundaries.md §2.1 y reformular
  :111 y :117.
- **Consentimiento de capacidades grabado en `clean.lock`**: `wit/<name>.wit` solo lista las
  interfaces propias de la librería (package-format.md:72), no `wasi:*` ni bridges; un bridge
  nuevo ya para con CFG005 (MissingManifestKey) (capabilities.md:87); `[security]
  allowedImports` ya aplica LIB013 (HostFunctionSandboxDenied); el set grabado no contendría lo
  que pretende guardar.
- **Verificación en cada uso (hash del binario en el handshake, store por hash)**: el manifiesto
  lista archivos, no binarios (supply-chain.md:40); el adversario sería el mismo usuario, fuera
  del modelo; el check de `checksums.toml` alimenta los hashes de la request
  (package-format.md:345); solo falta definir «entry with the locked hash» en MA-40 (Sources)
  (manager/architecture.md:134).
- **Autoverificación offline del primer arranque**: C-18 (Offline operation) excluye instalar; el
  registro de SC-52 (Self-verification on first run) viaja en `~/.cln/trust/`
  (supply-chain.md:172); un manifiesto dentro del archivo no puede listar ese mismo archivo.
- **Pinar e instalar `cln` por versión**: MA-30 (Install path) ya publica paquetes por versión
  (manager/architecture.md:118); el protocolo es un conjunto (PC-10 (The Manager handshakes before
  it dispatches) paso 4, process-contracts.md:158); `requires.cln` duplicaría el campo `protocol`;
  a lo sumo `cln self-update <version>` y que CV-10 (Mismatch stops the gate) lo nombre.
- **Protocolo por invocación en cada llamada**: solo existe el protocolo 1
  (process-contracts.md:152); la compatibilidad por pares es de la lista (MA-20 (Every pair is
  checked, both ways), MA-22 (Compatibility is decided by the list only)); la request ya se
  filtra por `schema_version` (contract.md:54, REQ001 (UnsupportedRequestVersion)); exit 2 no es
  FRM002 (CompilerFailed); quedan dos huecos del lsp (`--protocol` y `frameworkVersion`,
  language-server.md:86).
- **Cobertura de reproducibilidad (versión del Framework en la request, `host.toml` en el
  bundle)**: el bundle ya graba las versiones y `clean.toml [toolchain]`; `host.toml` es del
  operador (framework/architecture.md:110) y pararía el retest; los handlers son deterministas
  (block-handlers.md:274); solo falta el hash de los data files en la sección del Framework del
  manifiesto.
- **§2.4 «from the `clean.toml` sections» vs «never from `clean.toml`»**: boundaries.md:191 ya
  nombra el build manifest como fuente; el productor del WIT ya lo fijan SC-60 (Official hosts)
  (supply-chain.md:150) y contract-validation.md:41; el único hueco, `--edge-host`, va en la
  mejora 3.
- **Diagrama de Boundaries con tres de nueve llamadas**: la segunda frase de boundaries.md:58 ya
  remite a Process Contracts; PC-50 (Each step belongs to one component) ya dice «During a build»
  (process-contracts.md:122); queda corregir una cláusula («only») y hacer explícita la
  excepción del lsp.
- **Deriva de los satélites del compilador**: la propiedad de `query` es delegación coherente
  (contract.md:379; process-contracts.md:485; mcp-server.md:615-616); el resto son erratas (fila
  `explain`, excepción de FRM006 (DocumentVerbTimeout) en compiler/architecture.md:185, variable
  de entorno) absorbidas por las mejoras 1(e) y 8.