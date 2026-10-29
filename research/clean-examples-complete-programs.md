# ¿Cada ejemplo de Clean debe ser un programa completo?

Estudio hecho el 2026-10-28 con un workflow de 12 agentes: 5 lentes que buscan ejes, 1 que une ejes y diseña opciones, 3 jueces con prioridades distintas (pedagogía, verificabilidad, mantenimiento), 1 síntesis, 1 crítico de completitud y 1 revisión. Datos de Clean: clean-language-norms en el commit e7d4ac1.

## 1. Informe final (revisado tras la crítica)


### 1. La pregunta

¿Cada ejemplo `expect=valid` o `expect=error` tiene que ser, leído solo, un programa de Clean completo, o puede ser un fragmento que se entiende por la secuencia y el contexto?

**Respuesta corta: sí, programa completo.** Ese programa puede tener varios archivos si se declaran juntos. Los dos ejes que propusiste no pesan lo mismo:
- El (b), código siempre válido o inválido, se mantiene.
- El (a), la pedagogía de secuencia, es real, pero le toca a un libro que vive fuera de las specs normativas y tiene su propio mecanismo comprobado (sección 4).

### 2. Los ejes que importan

Estos son los 8 ejes que deciden. Los tres jueces les dieron el peso más alto en conjunto.

1. **Etiqueta honesta:** ¿`expect=valid` o `expect=error` describe el bloque tal como es, sin un tercer estado del tipo "válido con un contexto que no ves"? Es tu eje (b). Vale para los generadores y para quien lee el Markdown crudo. GitHub no muestra el info string en ninguna opción, así que para el lector de la página renderizada el estado lo tiene que decir la prosa (sección 4).
2. **Fidelidad:** si alguien copia el bloque y lo ejecuta, ¿obtiene lo que dice el texto, y es el mismo programa que corren la semántica y los tests?
3. **Cierre sin inventar:** ¿cada nombre está declarado en el bloque, de modo que ningún generador tiene que inventar declaraciones? Lo exige DSM-10 (the deriver makes no decision that the norms do not make).
4. **Unidad hermética:** ¿todo lo que decide el veredicto está en los bytes de su hash? Si no, cambiar otro ejemplo deja este desactualizado sin aviso.
5. **Estabilidad al reordenar:** ¿el sentido de un ejemplo sobrevive si se mueven o se insertan ejemplos? R13 (sections, files and bulleted lists are unordered) no ve el orden.
6. **Precisión de los errores:** ¿un ejemplo de error falla solo por la razón que declara?
7. **Referencia leída fuera de orden:** ¿se entiende el ejemplo cuando se abre directamente en esa regla? Así leen los generadores, los tests y la mayoría de las personas.
8. **Unión bien definida:** si se junta contexto con el ejemplo, ¿sale un archivo único, sin choques de nombres, con un solo `start:` y con `line=` intacto?

Estos ejes deciden poco, porque no separan las opciones o porque afectan a pocos ejemplos:

- **Pedagogía de secuencia (tu eje a):** solo 2 a 4 de los 20 fragmentos tienen un ejemplo anterior que les dé los nombres.
- **Andamiaje visible:** completar los ejemplos agrega entre 60 y 90 líneas a las 418 actuales, un 15–20 % más.
- **Alcance del andamiaje:** el andamiaje de un programa completo arrastra otras normas, y un hueco en cualquiera de ellas bloquea la evidencia. No separa las opciones, pero obliga a una regla de autoría (sección 4).
- **Oráculo de salida:** todas las opciones cerradas lo permiten por igual.
- **Formas generales con metavariables:** en la práctica es un solo caso, EXP-106 (Function Calls).
- **Reloj, stdin y librerías:** ningún formato de ejemplo lo resuelve.
- **Costo de autoría:** es parecido entre las opciones serias.

### 3. Matriz de decisión

Es la media de los tres jueces, de 1 a 5. La columna "Media" promedia los 8 ejes de la sección 2. Las dos últimas columnas sirven de contraste: son los ejes donde ganan las opciones perdedoras.

| Opción | Etiqueta | Fidelidad | Sin inventar | Hermética | Estabilidad | Errores | Referencia | Unión | **Media** | Secuencia | Brevedad |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Programa completo | 5 | 5 | 5 | 5 | 5 | 5 | 4,7 | 5 | **5,0** | 2,3 | 3,0 |
| Completo con marcas de foco | 5 | 5 | 5 | 5 | 5 | 5 | 4,7 | 5 | **5,0** | 2,7 | 3,7 |
| Líneas ocultas (`# `) | 3,7 | 1,7 | 5 | 5 | 5 | 4,3 | 3,0 | 3,0 | **3,8** | 2,3 | 2,0 |
| Nivel solo sintaxis* | 3,3 | 2,7 | 2,3 | 4,7 | 4,3 | 3,0 | 4,0 | 4,3 | **3,6** | 2,3 | 4,0 |
| Dependencia explícita `uses=` | 3,3 | 2,0 | 3,7 | 3,0 | 4,0 | 3,3 | 2,7 | 3,0 | **3,1** | 4,0 | 4,7 |
| Sesión por sección | 2,0 | 1,0 | 3,0 | 1,7 | 1,0 | 2,7 | 2,0 | 2,0 | **1,9** | 4,7 | 4,7 |
| Preludio estándar | 2,0 | 1,0 | 2,3 | 1,0 | 3,3 | 2,0 | 2,0 | 1,0 | **1,8** | 2,7 | 4,7 |
| Contexto implícito de la secuencia (hoy) | 1,0 | 1,0 | 1,7 | 1,0 | 1,0 | 1,0 | 1,0 | 2,0 | **1,2** | 3,7 | 5,0 |

\* El nivel solo sintaxis no es una alternativa: sería un complemento para las formas generales. Tras la crítica ya no se recomienda (sección 4).

**Dónde no coinciden los jueces:**

- **Marcas de foco.** Los tres las puntúan alto. Pero el juez de mantenimiento propone no adoptarlas todavía, porque hoy ningún visor pliega el código y la prosa puede señalar el foco sin costo.
- **Tercer puesto.** Las líneas ocultas (3,8) quedan delante del nivel solo sintaxis (3,6). El juez de pedagogía prefiere `uses=`.
- **En qué sí coinciden:** los tres ponen primero el programa completo, con o sin foco, y coinciden en los tres últimos puestos.

### 4. Recomendación

**Cada ejemplo `expect=valid` o `expect=error` es un programa completo y visible**, sin envoltorio y sin preludio. La única unión permitida es la de los archivos de un mismo programa:

- **Programas de varios archivos.** CEX-11 (The code) ya pide un ejemplo por archivo, con `// file:`. Los ejemplos de archivo de un mismo programa llevan una etiqueta de programa común en su línea de apertura. El checker arma el programa con todos los archivos que comparten esa etiqueta dentro del mismo archivo de spec. Sin esto, FIL-70 (A Complete Example) y las reglas de `import:` y `libraries:` no podrían tener ningún ejemplo comprobado. El formato exacto se decide en la spec de ejemplos.
- **Sin nueva forma `expect=syntax`.** De los 4 supuestos esquemas, solo EXP-106 (Function Calls) es una forma general. La forma `functionName(arg1, …)` va en un bloque `text`, como ya dice CEX-3 (Where Clean code is written), junto a un ejemplo concreto y cerrado. Así no cambian la lista completa de CEX-4 (The opening line), ni CEX-20 (What is checked, and by whom), ni los generadores.

**Reglas de autoría que vienen con la recomendación:**

- **Andamiaje mínimo.** El andamiaje usa solo construcciones ya especificadas y derivadas, con las declaraciones más pequeñas posibles. El autor elige los valores de los stubs y la salida que producen como parte del ejemplo. Si no, cerrar un ejemplo cambia un hueco de nombres por un hueco de prosa. Ejemplo: `formatPrice` en FUN-69 (Usage Examples) tropieza con la conversión de número a texto.
- **Variante con parámetros.** Para ejemplos de tipos o de flujo, como STA-9 (Variable Declaration), STA-62 y STA-64 (Printing Multiple Values) y EXP-68 (Comparison Operators), los nombres libres pueden ser parámetros de una función, por ejemplo `void check(integer score)`. El programa sigue completo y comprueba tipos, pero el oráculo es más débil, porque no ejercita la salida.
- **Estado visible en la prosa.** Hay que decirlo en la prosa ("Este programa imprime:", "Este programa falla con SEM004") porque GitHub no muestra la etiqueta de ninguna opción.
- **Alcance.** La regla estricta cubre las specs normativas. Un libro para aprender Clean, si algún día existe, vive fuera de ellas y necesita su propio mecanismo de secuencia comprobado (sesión por sección o `uses=`), o sus ejemplos se pudren.

**Por qué.** Es la única familia de opciones que saca 5 en los 8 ejes decisivos. Los mecanismos de dependencia pierden por fidelidad, hermeticidad, estabilidad y unión, no por cómo se ve la etiqueta en GitHub, que es invisible en todas las opciones. Además, su mejora alcanza solo a 2–4 de los 20 casos.

**El costo, dicho llano:**

- **Duplicación.** FUN-69 (Usage Examples) repite las tres funciones de FUN-66 (Function Parameter Default Values), y los ejemplos crecen un 15–20 %.
- **Pérdida de secuencia.** Se pierde la sensación de libro que acumula lo anterior.
- **Por qué compensa.** Las copias fallan en voz alta, porque cada una se comprueba por separado. El contexto implícito, en cambio, se pudre en silencio: si se renombra `greet` en FUN-66 (Function Parameter Default Values), FUN-69 (Usage Examples) queda obsoleto sin ningún aviso.

### 5. Efecto concreto en Clean

**FUN-66 y FUN-69.** FUN-69 (Usage Examples) pasa a ser un solo archivo con las tres funciones de FUN-66 (Function Parameter Default Values). Sus seis comentarios `// prints:` se convierten en un bloque de salida comprobado:

```clean-language expect=valid
functions:
	string greet(string name = "World")
		return "Hello, " + name
	string formatPrice(number amount, string currency = "USD")
		return currency + " " + amount.toString()
	void logMessage(string message, string level = "INFO")
		print("[" + level + "] " + message)

start:
	print(greet())
	print(greet("Alice"))
	...
```

Hay dos variantes:
- FUN-66 (Function Parameter Default Values) sigue como vista solo de declaraciones.
- Los dos ejemplos se funden en uno. Fundirlos quita el code_block de FUN-66 (Function Parameter Default Values) del árbol, así que los IDs, las unidades de aceptación y las citas de esas normas tienen que seguir el cambio. Editar en el lugar, en cambio, conserva el ID del ejemplo.

**Los 20 fragmentos pendientes por nombres no declarados** (20 = 3 + 1 + 6 + 10):

- **3 se cierran como programas válidos:**
  - EXP-28 (Multi-Line Expressions): declara `total`, `price`, `tax`, etc.
  - STA-12 (Assignment): declara `x`, un arreglo y un objeto.
  - LEX-23 (Spaces within expressions are permitted for readability): declara `x`, `y` y `compute`.

  Así conservan su evidencia semántica: la continuación de línea y la asignación.
- **1 pasa a `text` más un ejemplo concreto:** EXP-106 (Function Calls).
- **6 siguen bloqueados por huecos de la prosa aunque se cierren:**
  - FUN-69 (Usage Examples) y STA-35 (Printing Values of Any Type): falta la conversión de número a texto, la misma que deja pendiente a STA-33 (Printing Values of Any Type).
  - FUN-102 (Background Functions): basta un stub de una línea para `sendUpdateToServer`, pero `background` remite a la programación asíncrona, que no está especificada.
  - FUN-60 (Function Header): lee `result`, que pertenece a los contratos, que no están especificados.
  - EXP-115 (Pairs Literals) y TYP-442 (Type Conversion): usan `Request`, `req` y un servidor. Hay que elegir entre stubs locales o esperar a que se especifique la librería.
- **Los 10 restantes se pueden cerrar, y de ellos se vuelven derivables entre 6 y 8.** Son FUN-90 (Function Call Syntax), que copia las cuatro funciones de FUN-28 (Functions Blocks (Required)), STA-37 (Printing Values of Any Type), que por fin falla con el SEM004 que declara y no con SEM002, STA-9 (Variable Declaration), STA-62 (Printing Multiple Values), STA-64 (Printing Multiple Values), EXP-68 (Comparison Operators) y EXP-110 (Pairs Literals). Tres pueden chocar con otros huecos:
  - LEX-150 (String Literals), con el tipo de `length()`, el mismo hueco que deja pendiente a FUN-42 (Functions Are Not Values).
  - EXP-91 (Required Assertion Operator (`!`)), porque necesita stubs que devuelvan un opcional y el valor elegido decide si el programa se detiene.
  - EXP-83 (Default Operator (`default`)), porque necesita una clase con campos opcionales y puede tropezar con el hueco del constructor de STA-51 (Default toString() Behavior).
- Los otros 13 pendientes, de los 33, son huecos de la prosa que ningún formato arregla.

**Reglas de ejemplos (CEX):**

- **CEX-10 (The code)** se endurece: el ejemplo, leído solo o junto con los archivos de su mismo programa, declara todo lo que usa, salvo lo que define una norma del lenguaje o una librería especificada. Suma la regla de andamiaje mínimo.
- **CEX-11 (The code)** suma la etiqueta de programa que agrupa los ejemplos de archivo.
- **CEX-5 (The opening line)** cierra su pregunta abierta 1: no hay contexto de construcción fuera del bloque, salvo los archivos del mismo programa.
- **CEX-30 (The expected output):** los `// prints:` deterministas pasan a bloques de salida, y la prosa anuncia el estado ("Este programa imprime:").

**Generadores:**

- **Gramática y tests de aceptación:** corren cada programa tal cual, armando los de varios archivos por su etiqueta.
- **Semántica:** reporta "ejemplo no cerrado" como defecto del ejemplo, no como hueco de la prosa.

### 6. Decisiones que te tocan

1. ¿Adoptas la regla "programa completo, quizá de varios archivos declarados juntos", sin `expect=syntax`?
2. ¿Quieres las marcas `// focus` … `// end focus` como ayuda opcional para el lector, o prefieres que la prosa señale el foco? En esto los jueces no coinciden.
3. Para `Request`, `req` y el servidor de EXP-115 (Pairs Literals) y TYP-442 (Type Conversion): ¿se declaran como stubs dentro de cada ejemplo, o esperan a que se especifique la librería del servidor?

### 7. Qué cambió por la crítica

- **Recomendación:** se quita `expect=syntax`. Tres de los cuatro "esquemas" se cierran como programas, y EXP-106 (Function Calls) pasa a `text`.
- **Recomendación:** "sin unión" pasa a "solo la unión de los archivos de un programa". Antes contradecía a CEX-11 (The code) y dejaba a FIL-70 (A Complete Example) sin ejemplo válido posible.
- **Cuentas corregidas:** el desglose ahora suma 20, y los derivables bajan de "hasta 14" a entre 6 y 8. FUN-102 (Background Functions) estaba mal descrito y está bloqueado por la programación asíncrona. FUN-60 (Function Header) está bloqueado por los contratos. FUN-90 (Function Call Syntax) copia cuatro funciones, no una.
- **Argumento corregido:** GitHub no muestra ninguna parte del info string en ninguna opción, así que el argumento contra `uses=` se apoya ahora en los otros ejes. Se agrega la regla del estado dicho en la prosa.
- **Agregados sin cambiar la recomendación:** la regla de andamiaje mínimo, la variante con parámetros, el alcance de la regla (solo specs normativas, el libro va aparte), el costo de fundir FUN-66 (Function Parameter Default Values) con FUN-69 (Usage Examples) y la corrección de lo que dice la matriz sobre el podio y el juez de mantenimiento.

## 2. Ejes por lente

### Lente: pedagogy

**Genre and reading mode: tutorial (read in order) vs normative reference (looked up out of order)** — Is the passage that holds the example read from start to finish as a lesson, or opened at one section to settle a question about the language?

- Por qué importa: Scattered fragments work in a tutorial because the reader has just read the context. A reference is opened at one rule, so any context it does not show is lost, and the Clean specs are references: CEX says the examples are how Clean is defined. The Clean pending set already shows this. FUN-69 needs FUN-66, which sits in a sibling section. FUN-90 needs FUN-28, about 280 lines earlier and under another heading. LEX-147 builds User("Alice", 25), but the only class User is in another file (type-system.md), has four fields and is not a two-argument match.
- Favorece: For normative specs, examples that stand alone (complete, or with context the example itself declares). Sequence-dependent fragments belong in a tutorial written as a separate document.
- Evidencia:
  - Go keeps the two genres apart. The Go spec uses fragments throughout (`i, j := 0, 10`, `r, w, _ := os.Pipe()` with no package or import): https://go.dev/ref/spec. Every Tour of Go slide is a whole runnable program (package main, imports, func main), e.g. https://raw.githubusercontent.com/golang/website/master/_content/tour/basics/packages.go
  - Rust also splits them: the Book is a tutorial and the Reference is the normative text. Python does the same with its Tutorial (REPL sessions) and its Language Reference (grammar plus informal prose).
  - Clean: in the status file, FUN-90 is pending because add, multiply, square and printMessage are undeclared, although FUN-28 declares all four (functions.md line 88 vs line 364).

**Normative weight of the example ("readers believe the examples")** — If the example is normative, is every fact it relies on (a declaration, a value, a type) stated where a checker can see it?

- Por qué importa: In ISO, C++ and the Scheme reports, examples are informative, so a missing context is an editorial blemish. In Clean, examples define the language and generators derive the grammar and the semantics from them. Implicit context is therefore unstated normative content. Either the semantics invents it, which DSM-10 forbids, or the example cannot be checked. Concrete examples also leak details the prose did not intend.
- Favorece: Context that is complete and explicit: either a whole program, or a declared and checkable context mechanism. Never context the reader is left to imagine.
- Evidencia:
  - ISO/IEC Directives Part 2 (9th ed. 2021, cl. 25.5 as quoted second-hand): examples shall not contain requirements and are informative. https://www.iso.org/sites/directives/current/part2
  - C++ working papers: examples and notes are not normative, and notes that carried requirements were moved into body text (N4867 editors' report): https://open-std.org/JTC1/SC22/WG21/docs/papers/2020/n4867.html ; https://www.open-std.org/JTC1/SC22/WG21/docs/wp/html/jun96/intro.html
  - R7RS issue #348 debates whether examples should be normative. Pro: people 'believe the examples', and contradictions expose errors. Con: readers fix on details 'leaked' by examples and miss intended gaps. One proposal is to test the examples automatically. https://codeberg.org/scheme/r7rs/issues/348
  - Clean: STA-37 is declared expect=error SEM004, but because `age` is undeclared it gives SEM002 first. The implicit context changes the normative outcome.

**Focus vs boilerplate (extraneous cognitive load)** — How much of what the reader sees is the point of the example, and how much is scaffolding needed only to make it a program?

- Por qué importa: This is the user's pedagogy axis made concrete. Boilerplate splits the reader's attention and hides the line that matters. The cost is language-specific, and in Clean it is low: the wrapper is one `start:` line, already present in 39 of 64 valid examples, and the usual missing context is 1 to 3 declarations such as `integer score = 72`. Java-style boilerplate, by contrast, roughly doubles a short snippet.
- Favorece: Complete programs when the scaffolding is small, as it is in Clean. Otherwise a complete program with hidden or folded setup lines. Bare fragments only when the setup would outweigh the point.
- Evidencia:
  - rustdoc: 'To keep each code block testable, we want the whole program in each block, but we don't want the reader to see every line every time.' https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html
  - Kotlin Playground: only the code between //sampleStart and //sampleEnd is shown as editable, and the rest can be folded. https://github.com/JetBrains/kotlin-playground
  - Cognitive load and worked-example research (split attention, faded or partial examples): https://static.raspberrypi.org/files/curriculum/quickreads/2-Pedagogy_Summary_Worked_Examples_V6_2023.pdf ; https://static.raspberrypi.org/files/curriculum/quickreads/1-Pedagogy_Summary_Cognitive_Load_Theory_V14b_2023.pdf
  - Rust Book ch03-02: 10 of 14 Rust blocks are full listings with fn main, and the 4 short fragments are wrapped in fn main for testing. https://doc.rust-lang.org/book/ch03-02-data-types.html

**Locality: can one block be understood and checked alone?** — How far from the block, and in which direction, is the context it needs: none, the same section, a sibling section, earlier in the file, another file?

- Por qué importa: Tools that do let examples share state always bound the scope and make it explicit. A dependency within a section that the reader has just read is cheap. A dependency 280 lines away, or in another file, is invisible to the reader and fragile for the author: editing FUN-28 silently changes FUN-90.
- Favorece: Self-contained examples. If dependence is allowed, confine it to a section and name it explicitly (an explicit `uses=` or a named shared context), never implicit and never across files.
- Evidencia:
  - Python doctest: examples share names within one docstring (or one text file), and 'Examples cannot see names defined in other docstrings'. https://docs.python.org/3/library/doctest.html
  - Racket Scribble: each `examples` gets a fresh evaluator unless the author passes a shared one with #:eval, so sharing is an explicit choice. https://docs.racket-lang.org/scribble/eval.html
  - Clean distances: FUN-69 needs FUN-66 (adjacent, sibling section). FUN-90 needs FUN-28 (about 280 lines, another heading). LEX-147 needs a class User that exists only in another file, with a different shape.

**Reproducibility: copy, run, see the stated result** — Can a learner paste the block into a file, run it, and get what the text says it does?

- Por qué importa: Trying an example is how learners confirm understanding. A fragment that does not run, or prints a value nobody gave it, teaches distrust. It is also the same property the acceptance tests need against the compiler, so here pedagogy and verifiability point the same way.
- Favorece: Complete programs with concrete values. The second-best is hidden setup that the reader can expand to see the whole program.
- Evidencia:
  - Tour of Go and Kotlin docs: the examples are runnable in the browser. https://go.dev/tour/ ; https://kotlinlang.org/docs/basic-syntax.html
  - Python tutorial: 'to repeat the example, you must type everything after the prompt'. https://docs.python.org/3/tutorial/introduction.html
  - The Rust Book has to warn that 'if you enter and run a random example, it may not compile', and adds icons for that. https://doc.rust-lang.org/book/ch00-00-introduction.html
  - Clean STA-35: `print("Age: {age}")  // prints: Age: 25`. age is never declared, so neither the reader nor the semantics can reproduce '25', and no expected output block can be written for it.

**Signalled status: does the reader know whether the code is meant to work?** — When a block is incomplete or wrong, can the reader tell 'this fragment needs context' apart from 'this code is invalid'?

- Por qué importa: Read as a whole file, a fragment with undeclared names is an invalid program, yet it is labelled expect=valid. That mixes the two signals CEX-4 exists to keep apart. Good books mark intent explicitly.
- Favorece: One reading rule: every Clean example is judged as a whole program, possibly with declared context. Anything else goes in `text`, which carries no status.
- Evidencia:
  - Rust Book Ferris icons: 'does not compile', 'panics', 'does not produce the desired behavior'. https://doc.rust-lang.org/book/ch00-00-introduction.html
  - rustdoc attributes compile_fail, should_panic, no_run, and ignore (for 'incomplete or pseudocode', which is 'almost never what you want'). https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html
  - test262 frontmatter `negative: {phase: parse|runtime, type}` declares the expected failure. https://github.com/tc39/test262/blob/main/CONTRIBUTING.md
  - Clean: CEX-4 already declares valid, syntax-error or error, and CEX-3 sends non-file text to a `text` block (44 text blocks exist).

**Instance vs schema (metavariables)** — Is the block a concrete program, or a pattern whose names (functionName, arg1, value, x) stand for any code?

- Por qué importa: A reference often needs to show a form rather than an instance. Writing a schema as code makes the placeholders look like real undeclared names. That confuses learners, who may think `functionName` is special, and it blocks checkers. Language reports give holes their own notation.
- Favorece: Schemas in `text` (or grammar notation), each paired with one concrete, complete instance. Never schemas as valid examples.
- Evidencia:
  - Haskell 2010 Report 1.1: 'Holes in program fragments representing arbitrary pieces of Haskell code are written in italics', with mnemonic letters (e, d). https://www.haskell.org/onlinereport/haskell2010/haskellch1.html
  - The Go spec states forms in EBNF and keeps its code examples concrete. https://go.dev/ref/spec
  - Clean: EXP-28 (functionCall, arg1, arg2, defaultValue), EXP-106 (functionName, arg1..arg3) and LEX-23 (compute, arg1..arg3, x, y) are schemas written as expect=valid code. LEX-23 is about spacing, so the names do not matter to it.

**Narrative accumulation (building up across examples)** — Does the teaching benefit from later examples reusing what earlier ones built, and if so, which mechanism keeps that order dependence visible?

- Por qué importa: This is the strongest form of the user's axis (a). SICP, the Python tutorial and the Rust Book build things step by step, which avoids repetition and shows growth. The costs are order dependence, fragility when an earlier example is edited, and unusable random access in a reference. Doctest, Racket and mdBook each answer it with an explicit, scoped mechanism, not silent reliance on earlier text.
- Favorece: Where a sequence really teaches (definition, then usage), an explicit, section-scoped dependency or a joined complete program. Never implicit carry-over.
- Evidencia:
  - SICP 1.1: 'name-object associations can be created incrementally in successive interactions'; 'Having defined square, we can now use it'. https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/6515/sicp.zip/full-text/book/book-Z-H-10.html
  - Racket: a shared evaluator via #:eval, setup run with #:hidden, and eval:alts to show one form while evaluating another. https://docs.racket-lang.org/scribble/eval.html
  - mdBook {{#include file:anchor}} and {{#rustdoc_include}} show part of one complete program kept in a separate file, and 'mdbook test' runs the complete one. https://rust-lang.github.io/mdBook/format/mdbook.html
  - Rust Book source: listings are complete Cargo projects pulled in with {{#rustdoc_include ../listings/...}}. https://raw.githubusercontent.com/rust-lang/book/main/src/ch03-02-data-types.md
  - Clean: the fixed section order (libraries:, import:, ..., functions:, ..., start:) makes joining two non-colliding examples well defined. FUN-66 (functions:) plus FUN-69 (start:) would join cleanly.

**One text, several audiences** — Must the same block serve a learner, a spec author, the grammar and semantics generators and the compiler's acceptance tests, or can the teaching view be separate from the defining view?

- Por qué importa: Mature languages do not ask one document to be both a tutorial and a normative reference: Go has the Tour and the spec, Rust the Book and the Reference, Python the Tutorial and the Reference. When one text must do both, the tools let what is shown differ from what is checked, which brings pedagogy and verifiability together.
- Favorece: Keep normative examples complete and checkable. If teaching needs focus, use a show-vs-check mechanism (hidden lines or a visible region) or a later tutorial, not incomplete normative examples.
- Evidencia:
  - Go Tour vs Go spec; Rust Book vs Reference; Python tutorial vs reference (URLs above).
  - Kotlin KDoc @sample: the doc shows the body of a real, compiled function as the example. https://kotlinlang.org/docs/kotlin-doc.html
  - test262: each test is a whole script, with harness files named in `includes:` evaluated before it, and `flags: [raw]` to run with no prelude. https://github.com/tc39/test262/blob/main/CONTRIBUTING.md
  - Clean CEX module: the audience is spec writers and Claude sessions, and the consumers are the layer 2 grammar and semantics and the layer 3 acceptance tests. No learner-facing tutorial exists yet.

Opciones vistas: Always a complete program (Tour of Go; Rust Book listings kept as complete Cargo projects); Implicit wrapper: rustdoc wraps code without fn main in `fn main() { ... }` (in Clean this would be auto-wrapping statements in `start:`, though most Clean failures are missing declarations, not a missing wrapper); Hidden lines: lines prefixed with `#` are compiled but not shown, and the reader can expand them (rustdoc/mdBook); Visible region inside a complete program: Kotlin Playground //sampleStart ... //sampleEnd, with the rest folded; Show part of a complete program kept elsewhere: mdBook {{#include file:anchor}} and {{#rustdoc_include}}; Kotlin KDoc @sample naming a real function; Explicit shared context: Racket `examples #:eval` shared evaluator plus `#:hidden` setup; Python doctest shares names within one docstring or text file, never across; Display differs from what is evaluated: Racket eval:alts; Standard prelude or harness: test262 `includes:` harness files, with `flags: [raw]` to opt out; Explicit dependency on another example (the uses= idea), joined by the fixed section order of a Clean file; REPL transcript format, where state accumulates within the session (Python tutorial, SICP); Explicit status markers: Rust Ferris icons; rustdoc compile_fail, should_panic, no_run, ignore; test262 negative phase and type; Clean CEX-4 expect=; Separate notation for schemas or holes: Haskell italics holes, Go EBNF, Clean `text` blocks (CEX-3); Label examples informative rather than normative (ISO Directives, C++, the R7RS #348 proposal), which does not fit Clean, where examples define the language; Separate tutorial from normative spec (Go Tour vs spec, Rust Book vs Reference, Python Tutorial vs Reference)

Datos: Counted in /Users/jpchauny/Documents/Clean Language/clean-language-norms (read-only).
- Status file: 67 fragments, 34 derived and 33 pending.
- 21 of the 33 pending are pending because the example uses names it does not declare, in four groups:
  (A) Depends on an earlier example (3): FUN-69 needs FUN-66 (sibling section, adjacent); FUN-90 needs FUN-28 (same file, about 280 lines earlier); LEX-147 builds User("Alice", 25), but the only class User is in another file (type-system.md) and has 4 fields.
  (B) Ambient data or stub functions with values the reader is left to imagine (14): STA-9, STA-12, STA-35, STA-37, STA-62, STA-64, EXP-68, EXP-83, EXP-91, EXP-110, EXP-115, LEX-150, TYP-442, FUN-102. STA-35 even states '// prints: Age: 25' with no age declared. STA-37 gives SEM002 before the SEM004 it declares.
  (C) Schemas with metavariables (3): EXP-28, EXP-106, LEX-23.
  (D) External files or libraries (1): FIL-70.
  Also related: FUN-60 reads `result` in an after: block, but that comes from Contracts not being specified yet, not from missing context.
- The other 12 pending are gaps in the norms (sized literals, toString of numbers, time.now, and so on) that no format for examples would fix.
- Fenced blocks under specs-repo-annotated/specs: 71 Clean examples (64 expect=valid, 4 syntax-error, 3 error), 9 clean-language-output blocks, 8 examples with '// prints:' comments, 44 text blocks.
- 39 of the 64 valid examples have only a start: section, so making a statement-level example complete in Clean usually means adding 1 to 3 declarations, not a large wrapper.

### Lente: verification

**Semantic closure: closed program versus open term with a declared context** — Does the example, read alone, bind every name it uses (types and, to run, values), or does it depend on a context that nothing in the block states?

- Por qué importa: A semantics (Lean), a compiler and an acceptance test can only judge a closed program, or an open term under a context they can read (a judgement of the form Γ ⊢ program). Being a whole file in syntax (CEX-10 (The code)) is not the same as being closed in meaning. The grammar does not care about this; the semantics and the compiler do.
- Favorece: Context that is explicit and machine-readable inside the example: whole programs, or a declared context such as hidden lines or a given: section. Implicit context from the reading order loses. A cross-reference such as uses= would fix only 2 of the 20.
- Evidencia:
  - Grammar status: 71 of 71 derived, the 20 examples with free names included. Syntactic completeness is already met everywhere, so the gap is purely semantic.
  - Semantics status: 34 of 67 derived and 33 pending. 20 of the 33 reasons say 'which it does not declare and no norm declares'.
  - Of those 20, only 2 can be resolved from another example: FUN-69 needs greet, formatPrice and logMessage from FUN-66, and FUN-90 needs add, multiply, square and printMessage, declared about 270 lines earlier in functions.md. The other 18 (for example STA-9 score, STA-35 age and price, EXP-83 user and config, FUN-102 sendUpdateToServer, TYP-442 req) use names that no example declares anywhere.
  - To run, a free name needs a value as well as a type: what STA-9 prints depends on the value of score.
  - Lean and Coq formalize open terms through explicit contexts (variable, Section/Variable), never through implicit ones.

**Hermetic unit: one block, one test, one hash** — Is everything that decides an example's outcome inside the bytes whose hash identifies it, so that a change elsewhere cannot silently change its verdict?

- Por qué importa: The status files and tree.jsonl identify each example by ID@hash, and the derived norms are reproducible only when they are keyed by content. If FUN-69 means something only together with FUN-66, editing FUN-66 changes the verdict on FUN-69@4f2e41f3 while FUN-69's hash stays the same. Invalidation then has to follow a dependency closure.
- Favorece: Context written inside the block (visible or hidden lines), or a small versioned prelude whose hash is part of every dependent example. Implicit sequence or sibling-section dependencies lose, unless the hash covers the whole dependency closure.
- Evidencia:
  - Status reasons cite content hashes, for example 'FUN-69@4f2e41f3, ERR-413@e09c6ce6', and the meta line hashes every generated Lean file.
  - test262: 'Each test must be executed in a new ECMAScript realm dedicated to that test'. The shared context lives only in versioned harness files (includes:) and _FIXTURE files that 'MUST NOT' run alone. https://github.com/tc39/test262/blob/main/INTERPRETING.md
  - Rust doctests keep their hidden context ('#' lines) inside the same block, so the block is still the hermetic unit. https://rust-lang.github.io/mdBook/pre-release/format/mdbook.html

**Oracle strength: what a passing example proves** — When the example passes, what has been checked? Only 'no error code', or an observable result such as stdout or asserted values?

- Por qué importa: A complete program that prints nothing is weak evidence for a semantics: a wrong evaluator still passes it. Completeness and observability are separate properties, and the verdict on 'complete programs' should not hide the fact that most valid examples have no checked oracle.
- Favorece: Whole programs that also have an observable result: an output block, or an assertion convention, for example in tests:. A rule that turns '// prints:' into checked output. A fragment without an oracle adds almost nothing to verification.
- Evidencia:
  - 64 valid examples, but only 9 have a clean-language-output block, and only 5 of those are derived.
  - 20 of the 34 derived examples have no expected output and never call print. The only thing they show is that the code type-checks and terminates without error. 14 examples are functions: only, with no start:.
  - 44 '// prints:' or '// result:' comments in 16 examples are oracles that nothing checks (CEX-30 (The expected output)). FUN-69 alone has 6.
  - Wasm .wast checks every action with assert_return or assert_trap. https://github.com/WebAssembly/spec/blob/main/interpreter/README.md
  - test262 tests assert through the always-loaded assert.js harness.
  - JLS examples are mostly whole programs that state 'This program produces the output:'. https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html

**Phase granularity of the expectation** — Does the example's declared expectation say which phase it is evidence for (parse, name or type check, link, run), so that a snippet that only shows syntax does not have to be complete in meaning?

- Por qué importa: Some examples are only about form: placeholders like functionCall, arg1 and functionName show where parentheses go. Demanding that they run turns illustrations of syntax into pending semantic gaps. Expectations tagged by phase let each consumer take only what it can check.
- Favorece: Expectations tagged by phase, for example an expect=parses or syntax-valid for illustrations of form. These examples are then explicitly not semantic evidence, and every example that claims to run is a closed program.
- Evidencia:
  - EXP-28, EXP-106 and LEX-23 use metasyntactic names (functionCall, arg1, arg2, arg3, defaultValue, compute, functionName). They pass the grammar and are pending in the semantics.
  - Clean has 3 expectations: valid, syntax-error and error, where error means build or run time (CEX-4 (The opening line)).
  - Wasm uses separate assert_malformed, assert_invalid, assert_unlinkable, assert_trap and assert_return.
  - test262's negative: has phase parse, resolution or runtime.
  - ACATS separates class B (illegal, compile only), class C (executable) and class L (link-time) tests. https://gcc.gnu.org/pipermail/gcc/2001-December/073337.html

**Precision of negative examples (error masking)** — Does an error example give its declared code, and is it the first or only error, or can missing context raise a different error first?

- Por qué importa: An error example is evidence only if the code it declares is the only reason it fails. Missing context in a negative example makes the verdict depend on the order of diagnostics, and so on the implementation.
- Favorece: Strict closure for every expect=error example: a whole program with exactly one defect. For negative examples, implicit context is never acceptable.
- Evidencia:
  - STA-37 expects SEM004 but 'uses the name age, which it does not declare … so it gives SEM002 before the SEM004 it expects'.
  - Only 3 expect=error examples exist (2 derived for SEM001, 1 pending), so each one carries a lot of weight.
  - ACATS B-tests mark every expected error line with '-- ERROR:', and all other code must be legal: 11886 errors flagged across 1525 files. https://gcc.gnu.org/pipermail/gcc/2001-December/073337.html
  - Rust Reference: 'each example must appear in a separate code block so that the tests can ensure that each case indeed fails with the appropriate error code'. https://rust-lang.github.io/reference/dev-guide/examples.html

**Determinism of the host and the environment** — Are the results of time, I/O, libraries and imported files fixed by the norms, so that the outcome and the output reproduce byte for byte?

- Por qué importa: An expected output checked byte for byte (CEX-29 (The expected output)) needs a deterministic environment. Libraries, other files and the clock are context too, and a prelude made of declarations does not provide it.
- Favorece: Fixtures defined in the norms: a fixed test host (clock, I/O), named fixture files for multi-file examples, and fixed library stubs. Free names do not settle this; it needs its own mechanism.
- Evidencia:
  - TYP-189 is pending because 'no norm says how much time passes between two calls of time.now()'.
  - FIL-70 imports app/utils.cln and app/mathHelpers.cln and uses the data and server libraries, 'whose content no norm gives'.
  - The Wasm spectest host module gives fixed values (global_i32 = 666, global_f32 = 666.6) and print functions. It is now deprecated in favour of explicit register. https://github.com/WebAssembly/spec/blob/main/interpreter/README.md
  - test262 gives each test a fresh realm, and module tests use _FIXTURE files.

**Trusted base: the prelude or harness is itself a spec artifact** — If there is shared context (prelude, harness, fixtures), is it small, specified, versioned and checked, and can an example opt out of it?

- Por qué importa: Every precedent that uses a prelude makes it part of what every test trusts. A bug in it, or a change to it, invalidates the whole suite. A large prelude with idiosyncratic names (score, price, age, user) would itself be unspecified language.
- Favorece: Context that each example declares for itself, or a small explicit include with a raw opt-out. One large implicit prelude loses.
- Evidencia:
  - test262: assert.js and sta.js are evaluated before every test 'unless the test uses the raw frontmatter flag'. Other includes load in a declared order.
  - ACATS: the REPORT support package is required, and 'if REPORT is not working correctly, validation testing is discontinued'. ACATS also shares 'foundation' units (F-prefixed) across tests (general knowledge, not fetched).
  - Wasm deprecated its implicit spectest module, saying it 'predates the register command and should no longer be needed for new tests'.
  - The 18 Clean names that no example declares are specific to their examples, so one standard prelude would have to declare a made-up vocabulary of fixtures.

**Normative status: one corpus or two** — Are the examples normative evidence, as here, or informative illustrations next to a separate conformance suite?

- Por qué importa: Most language standards keep fragments because their examples are informative and their tests live elsewhere. Clean derives its grammar from the examples and checks its semantics against them, so it takes on the obligations of a conformance suite inside the prose.
- Favorece: Any normative Clean example is complete. Fragments meant for teaching are allowed, but as an explicit non-evidence kind (text, or a fragment kind that has a context).
- Evidencia:
  - ISO/IEC Directives Part 2 make examples informative. The C standard's EXAMPLE paragraphs use fragments with '...'. https://www.iso.org/sites/directives/current/part2/index.xhtml (general knowledge, not fetched)
  - ECMAScript prose has no runnable examples; test262 is separate. Wasm prose is separate from the .wast suite.
  - SpecTec generates the Wasm prose and an interpreter from one source, and the interpreter passes 100% of the applicable Wasm 2.0 test suite. Even so, the test suite is still a separate corpus of whole modules. https://webassembly.org/news/2025-03-27-spectec/
  - The K semantics of C was validated on 776 whole programs from the GCC torture suite, passing 99.2%. https://fsl.cs.illinois.edu/publications/ellison-rosu-2012-popl.html
  - Clean already has an escape for informative text: CEX-3 (Where Clean code is written) puts non-file text in a text block.

**Attribution of failures to norms** — When an example fails, does the failure point at the norm it illustrates, or at another example it silently depends on?

- Por qué importa: Each pending reason, each issue and each acceptance test is tied to a norm ID. Hidden dependencies shift the blame: a defect in FUN-66 would surface as a failure of FUN-69 (Usage Examples).
- Favorece: Self-contained examples, or explicit dependencies named in the opening line or the frontmatter, with the dependency's ID@hash recorded in the status line.
- Evidencia:
  - Status reasons list the norms involved, for example 'FUN-69@4f2e41f3, ERR-413@e09c6ce6'.
  - test262 frontmatter names the spec section each test covers (esid) and the features it needs. Includes are named explicitly, so the dependency is visible.
  - Wasm register and named modules make each cross-module dependency an explicit command.

Opciones vistas: Always a whole, closed program, as in JLS examples, Wasm modules and ACATS C-tests; Whole program plus an observable oracle: an expected output block, assert_return-style assertions, or an assertion harness in tests:; Hidden lines inside the block that complete the program: Rust/mdBook '#' lines, Verso hide_commands for import, open and set_option. The block stays the hermetic unit.; A declared typing and value context per example, like Lean variable or Coq Section/Variable, as a given: section or attribute; Always-loaded small harness or prelude with a raw opt-out (test262 assert.js and sta.js, the raw flag); Explicit includes of named harness files in a declared order (test262 includes:); Named fixture files that never run alone (test262 _FIXTURE) and shared foundation units (ACATS F-files) for multi-file and library examples; Explicit registration of a module or example by name for reuse (Wasm register). The Wasm implicit host module (spectest) was deprecated in favour of it.; Explicit cross-example dependency (uses=<ID>), with the hash taken over the dependency closure. It resolves only FUN-69 and FUN-90 of the 20.; Expectations tagged by phase: parse, resolution or validation, link, run (Wasm assert_malformed, assert_invalid, assert_unlinkable, assert_trap; test262 negative.phase; ACATS classes B, C and L). A possible expect=parses for illustrations of syntax only.; Per-line error markers with every other line legal (ACATS '-- ERROR:'), or one error per block (Rust compile_fail with Exxxx); Turning the '// prints:' comments into checked expected output; A deterministic test host defined in the norms (fixed clock and I/O, library stubs), like the fixed constants of Wasm spectest; Two corpora: informative fragments in the prose (ISO/C EXAMPLE, the CEX-3 (Where Clean code is written) text block) and a separate normative conformance suite (test262, .wast, ACATS); A single-source spec DSL that generates prose, an interpreter and a prover model, checked against a separate suite of whole programs (Wasm SpecTec)

Datos: Counted from clean-language-norms (specs_commit 11bc27ab).

Grammar: 71 examples, all derived (67 accept, 4 reject).

Semantics: 67 examples, 34 derived, 33 pending. The cases are 64 run, 2 'error SEM001' and 1 'error SEM004'.

Of the 33 pending, 20 have free names ('which it does not declare'): FUN-69, FUN-90, FUN-102, EXP-28, EXP-68, EXP-83, EXP-91, EXP-106, EXP-110, EXP-115, LEX-23, LEX-147, LEX-150, STA-9, STA-12, STA-35, STA-37, STA-62, STA-64, TYP-442. Only 2 of them can be resolved by referencing an existing example: FUN-69 from FUN-66, and FUN-90 from the add, multiply, square and printMessage declarations at functions.md lines 88-98. The other 18 use names that no example declares. 3 of the 20 use metasyntactic placeholders (EXP-28, EXP-106, LEX-23). 1 is an error example masked by the missing context (STA-37 gives SEM002 before its SEM004).

The other 13 pending are gaps in the spec, not missing context:
- literal typing for sized types: TYP-197, TYP-200, TYP-209, TYP-436;
- conversions: TYP-440;
- string length type: FUN-42;
- number formatting: STA-33;
- the constructor: STA-51;
- iterate and add: FUN-32;
- contracts: FUN-60;
- error handling: TYP-361;
- the clock: TYP-189;
- files and libraries: FIL-70.

Sections of the 71 examples:
- 39 are start: only (18 derived, 21 pending);
- 14 are functions: only (10 derived);
- 4 are functions plus start;
- the rest mix class, can, host, or are full multi-section files (FIL-70).

Oracles: there are 9 clean-language-output blocks, 5 of them on derived examples. 20 of the 34 derived examples have no expected output and no print call. 44 '// prints:' or '// result:' comments in 16 examples go unchecked.

Error examples: 3 expect=error and 4 syntax-error.

### Lente: pipeline

**What each consumer needs for an example to count as complete** — Is an example complete enough for every consumer that reads it: grammar, Lean semantics, compiler acceptance tests, and a human reader?

- Por qué importa: Each consumer needs a different kind of completeness. The grammar needs only a file whose sections are in the right order. The semantics also needs every name resolved, prose norms behind every operation, and determinism. Acceptance tests need something the compiler can build and run on a fixed host. The reader needs focus. A single rule like 'whole source file' (CEX-10, the code of a valid or error example is a Clean source file) covers only the first kind.
- Favorece: Defining 'complete' as a whole program closed under names: whole file + every name declared in the example or in explicitly stated context. Or levels per consumer (syntax-only versus runnable). It disfavours the current definition, which is purely syntactic.
- Evidencia:
  - Grammar status: 71 of 71 fragments derived, 0 pending. That includes all 20 fragments that use undeclared names. Syntactic wholeness is already met everywhere.
  - Semantics status: 34 of 67 derived, 33 pending. 20 of the pending are context gaps (undeclared names). 12 are prose gaps. 1 is external files and libraries (FIL-70).
  - CEX-10 checks only that every column-1 code line is a section line. Under CEX-21, name closure 'needs a Clean compiler', and no hook checks it.
  - CEX open question 1 (CEX-5, the code is a correct Clean program) leaves the build context of a valid example undecided. DSM-10 (the deriver makes no decision that the norms do not make) forbids inventing it.

**Name closure (self-sufficiency for the semantics)** — Can a consumer resolve every name the example uses from the example's own code plus context that a norm states explicitly?

- Por qué importa: Under DSM-10 the semantics invents no declaration, so any implicit context becomes a permanent gap and an issue in layer 1. The compiler's acceptance tests hit the same wall: an undeclared name is a SEM error, not a pass.
- Favorece: Self-contained programs, or context that is explicit and machine-readable. It rules out context that only a reader of the surrounding prose can infer.
- Evidencia:
  - 20 of 33 pending fragments are undeclared-name gaps: FUN-69, FUN-90, FUN-102, EXP-28, EXP-68, EXP-83, EXP-91, EXP-106, EXP-110, EXP-115, LEX-23, LEX-147, LEX-150, STA-9, STA-12, STA-35, STA-37, STA-62, STA-64, TYP-442.
  - Only 4 of the 20 are declared in an earlier example of the same file: FUN-69 uses FUN-66, the example just before it; FUN-90 uses FUN-28, five examples back; STA-35 and STA-37 use STA-33. 16 are declared nowhere.
  - STA-37 (expect=error SEM004) currently gives SEM002 before the SEM004 it expects, because `age` is undeclared. An incomplete error example tests the wrong error.
  - LEX-147 builds User("Alice", 25). The only User class is in another file (TYP-361), and it has 4 fields.

**Oracle strength (what each example actually checks)** — Does the example have an entry point and an expected output, so that what its comments claim is executed and compared?

- Por qué importa: An example with no start: is only type-checked, and an example with no output block passes with any output (CEX-30). So 'valid' can mean the behaviour the prose claims was never checked. The same holds for acceptance tests run against the compiler.
- Favorece: Complete programs with start: and an expected output block wherever the output is deterministic. Joins or dependencies, so a declaration-only example such as FUN-66 gets exercised by the example that calls it.
- Evidencia:
  - 19 of 67 semantic fragments have no start: section. 13 of them are 'derived', but that checks typing only.
  - TYP-381, TYP-389 and TYP-397 have no start:. They claim FIFO, LIFO and set behaviour in `// result:` and `// prints:` comments that never run.
  - Only 9 examples have a clean-language-output block. Of the 34 derived, 5 compare their output byte for byte, 13 only type-check, and 16 run but compare nothing.
  - FUN-69, STA-35, STA-37 and TYP-397 have `// prints:` comments but no output block. 3 of those 4 depend on another example.

**Change detection and traceability through norm hashes** — When a norm an example depends on changes, does the pipeline notice through IDs and hashes, and re-derive and re-test the example?

- Por qué importa: The work list (DSM-12, only what a change calls for is derived again) re-derives a fragment only when its own norm hash, case, expected output or parse tree changes. With an implicit dependency, renaming greet in FUN-66 leaves FUN-69's hash unchanged, so FUN-69 keeps a stale status. Acceptance units cite norms as hash_in_acceptance_unit, which has the same blind spot.
- Favorece: Self-contained examples, which need no new mechanism. Or explicit dependencies whose hash enters the work list facts and acceptance citations, such as uses=FUN-66 resolved to FUN-66@057a3e83. It disfavours implicit dependency by position or by prose.
- Evidencia:
  - The status line holds hash, expected_output 'FUN-110@b5abd3a1' and parse_tree_hash. Nothing in it records another fragment.
  - DSM-12 already has the right pattern: a pending fragment is re-derived when 'a norm cited in its reason has another norm hash'. So citations of the form ID@hash are an established mechanism.
  - Hidden or inline context lines inside the fence are part of own_text, so the fragment's own hash covers them. A `uses=<ID>` attribute puts the reference in the hash but not the dependency's content, so the work list must add the dependency's hash.

**Stability when examples are inserted or reordered** — Does the meaning of an example survive inserting, moving or reordering examples and sections in its spec file?

- Por qué importa: The tooling assumes that reordering is harmless. A 'join with the previous example' or 'sequence per section' rule turns any insertion into a silent change of meaning, with no hash to signal it.
- Favorece: Self-contained examples or dependencies named by stable norm ID. It disfavours positional or sequential context.
- Evidencia:
  - CEX-23 (hook refusal of new malformed blocks), rationale: 'moving or reordering blocks refuses nothing'.
  - CEX-27 (expected output block right after its example) ties a block to its example by adjacency only, and only for the output block, which names no example.
  - DGR-7 (a partial fragment is not considered) was removed by a decision of the user: a fragment is derived or pending, and its case comes from its opening line alone.
  - FUN-90 depends on FUN-28 across four intervening examples (FUN-42, FUN-46, FUN-49 ... FUN-81). An adjacency rule cannot express that.

**Whether joins compose (section collisions)** — When an example is joined with another, or with a prelude, is the result a valid Clean file without duplicate declarations or duplicate sections?

- Por qué importa: The section order is fixed and a file has at most one start: (FIL-54), so a join is well defined only when sections and names do not collide. Many of the candidate joins collide.
- Favorece: Pairwise explicit dependencies with collision checks, or self-contained examples. It disfavours a file-wide sequence or a large shared prelude.
- Evidencia:
  - FIL-54 (grammar citation): 'a file has at most one start: block'. STA-35 and STA-37 need STA-33, and all three have start:. A join works only if a rule concatenates start bodies.
  - A cumulative join per file is impossible: add is declared in both FUN-28 and FUN-46, and greet in FUN-66 and FUN-97 with different signatures. first, name, count and data are redeclared across type-system start blocks.
  - An ad-hoc fixture prelude would collide with local redeclarations of x, value, total, data, user, price, age, username, count and name in more than 10 examples. The shadowing rules are not specified.

**Determinism and host environment** — Does the example's outcome depend only on its code, or also on the clock, stdin, imported files, libraries or the host world?

- Por qué importa: Byte-for-byte expected output (CEX-29) and repeatable acceptance runs need a fixed host. Context that is not code still counts as context.
- Favorece: Complete programs plus a declared host fixture: a fixed clock and stdin, and multi-file examples using `// file:` (CEX-11). An explicit includes or uses mechanism for library context.
- Evidencia:
  - TYP-189 is pending only because no norm says how much time passes between two time.now() calls. EXP-60 uses time.now() and is derived, but it has no output to compare.
  - FIL-70 is pending because app/utils.cln, app/mathHelpers.cln and the libraries data and server have no content in any norm.
  - EXP-115 (Request) and TYP-442 (req) assume a server context. STA-68 mentions console input (input.integer()), which needs stdin.
  - The standard library is 'not specified yet' (absent stdlib/core.md), so a 'standard prelude' has nothing normative to point to yet.
  - test262 handles this explicitly. Its harness files assert.js and sta.js are prepended to every test unless the test has flags: [raw], and each extra helper is listed in `includes:` (https://github.com/tc39/test262/blob/main/INTERPRETING.md).

**Grammar evidence coverage** — If incomplete examples were moved to `text` blocks under a strict reading of CEX-3 (non-whole Clean text goes in a text block), would the derived grammar lose its only fragment evidence for some rules?

- Por qué importa: The grammar is derived from the fragments (DGR-2, the grammar comes from the fragments and the prose norms a rule needs). Demoting the 20 incomplete examples drops test cases and can leave rules backed by prose alone.
- Favorece: Completing these examples, or giving them a syntax-only status that keeps them as grammar cases. It disfavours demoting them to `text`.
- Evidencia:
  - In clean.lark, rule print_block has STA-62 as its only fragment citation. Rule pair has only EXP-110 and EXP-115. All three are among the 20 undeclared-name fragments.
  - Several of the 20 illustrate syntax forms whose only executable evidence they are: line continuation (EXP-28), the ! assertion (EXP-91), default chains (EXP-83), is and isnt (EXP-68), assignment targets (STA-12).

**Where a context error is caught: when writing or when deriving** — Can the hook or audit catch a missing context textually when the example is written, or does it surface only later, as a semantics gap and an issue in layer 1?

- Por qué importa: Today each context gap becomes its own issue in layer 1 (DSM-14), mixed in with real prose gaps. A mechanism that text alone can check stops the problem at the source, without a compiler.
- Favorece: An explicit dependency or context attribute that the hook validates, plus complete programs. It disfavours implicit context whose absence shows up only in layer 2.
- Evidencia:
  - CEX-20 lists the text-decidable rules checked by the hook. Name closure is not decidable from text, per CEX-21.
  - Resolving context changes the kind of gap rather than closing it. With context, FUN-69 (formatPrice(9.5)) and STA-35 (printing price 19.99) would hit the number-to-text prose gap that keeps STA-33 pending. Only FUN-90 and STA-37 would become fully derivable.
  - A `uses=<ID>` attribute is text-checkable by the hook: the ID exists, is an active valid example of the same or another file, and its sections do not collide. Hidden-line context is not checkable for name closure either.

**Reader focus in the rendered spec** — Does the reader see the point of the example without boilerplate, in the medium the specs are read in (GitHub-rendered markdown and specs-repo-annotated)?

- Por qué importa: Whole programs add declarations that dilute the lesson. Hiding them depends on a renderer, and these specs have none.
- Favorece: Visible minimal context, or a syntax-only status for schematic examples, over hidden lines. Hidden lines suit this project only if a renderer is added.
- Evidencia:
  - Rust doctest hidden `#` lines are hidden only by rustdoc (https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html). In GitHub-rendered markdown they would show.
  - 4 examples are schematic syntax illustrations with metasyntactic names: EXP-106 functionName(arg1, ...), LEX-23 compute(arg1, arg2, arg3), EXP-28 price + tax + shipping, STA-12 x/arr/obj. Fake declarations add noise to them without adding meaning.
  - Most whole programs are already short: 34 derived fragments are self-contained, and most have under 10 lines.

Opciones vistas: Whole program always: every Clean example is closed under names, declarations included inline (the current CEX-1, CEX-3 and CEX-10, plus name closure).; Join with the previous example of the same file, by position. It works cleanly only for FUN-69. STA-35 and STA-37 work only with a start-body concatenation rule. It breaks on insertion.; A sequence per section or file, cumulative like a notebook or REPL. It is impossible as written: add, greet and the start blocks collide.; Explicit dependency attribute in the info string, uses=<norm ID>. It must be checked by the hook, and the dependency's hash must enter DSM-12 work-list facts and acceptance citations. A precedent is test262 `includes:`.; WebAssembly .wast style: an implicit 'most recently defined module' default plus named modules ($name, register). A hybrid of sequence and explicit naming (https://github.com/WebAssembly/spec/blob/main/interpreter/README.md).; A standard prelude or harness prepended to every example, like test262 assert.js and sta.js with a `raw` opt-out. It is blocked until the stdlib is specified. An ad-hoc fixture prelude collides with redeclarations.; Hidden context lines inside the fence, as in Rust doctests' `#`. They are covered by the fragment hash, but GitHub does not hide them.; Context declared in a separate non-example block, such as an HTML comment or a `clean-language expect=context` block, referenced by ID.; Multi-file examples, one Clean example per file with `// file:` (CEX-11), to supply imports such as those of FIL-70.; A syntax-only status, for example expect=parses: checked by the grammar and skipped by the semantics, for schematic examples (EXP-106, LEX-23, EXP-28, STA-12).; Demoting incomplete examples to `text` (strict CEX-3). This loses the only grammar fragment evidence for print_block (STA-62) and pair (EXP-110, EXP-115).; A declared host fixture: a fixed clock, stdin and files, so examples such as TYP-189 and those using input can carry an expected output.; Rewriting each incomplete example to declare its own names. This is the only fix for the 16 examples whose names are declared nowhere.

Datos: Sources: data/tree.jsonl (specs_commit 11bc27a), specs-derived/grammar and semantics status files, and clean.lark. Totals: 71 active Clean examples, of which 4 are expect=syntax-error (EXP-29, EXP-30, FIL-75, LEX-151) and 67 are semantic fragments. There are 9 expected-output blocks, and 1 retired ```clean block (TYP-190). Grammar: 71 of 71 derived. Semantics: 34 derived, 33 pending. The 33 pending split into: 20 with undeclared names; 12 prose gaps (FUN-32, FUN-42, FUN-60, STA-33, STA-51, TYP-189, TYP-197, TYP-200, TYP-209, TYP-361, TYP-436, TYP-440); 1 with external imports or libraries (FIL-70). Self-contained (name-closed) today: 46 of 67. Of those, 34 are derived and 12 pending on prose gaps. Name-closed and with start:: 33. No start: section: 19 of 67, of which 13 are derived (typing only); 3 of these (TYP-381, TYP-389, TYP-397) make behaviour claims that never run. Expected output blocks: 9; 5 derived (FUN-16, FUN-81, FIL-76, LEX-17, STA-28) and 4 pending (FIL-70, STA-33, STA-51, TYP-189). Derived with start: but no output compared: 16. `// prints:` comments without an output block: 4 (FUN-69, STA-35, STA-37, TYP-397). `// result:` comments: 10 examples. Where the 20 undeclared names come from: 4 from an earlier example of the same file (FUN-69 from FUN-66, the example just before; FUN-90 from FUN-28, five back; STA-35 and STA-37 from STA-33); 16 declared nowhere. Of those 16, 3 are host or library context (EXP-115 Request, TYP-442 req, FUN-102 sendUpdateToServer) and 4 are schematic syntax illustrations (EXP-106, LEX-23, EXP-28, STA-12). Fixes, counted out of 20 context gaps: (i) join with the previous example: 1 clean (FUN-69); 3 if start bodies may concatenate (adds STA-35, STA-37), since FIL-54 allows one start: per file. (ii) A standard prelude: 0 normative today (stdlib/core.md 'not specified yet'); at most 2 or 3 with a server library spec (EXP-115, TYP-442, plus FIL-70 outside the 20); an ad-hoc fixture prelude collides with redeclarations of x, value, total, data, user, price, age, username, count and name. (iii) Explicit dependencies: 4 (FUN-69, FUN-90, STA-35, STA-37). Of those, only FUN-90 and STA-37 become fully derivable; FUN-69 and STA-35 then hit the number-to-text prose gap of STA-33. The remaining 16 need declarations written in any scheme (inline, hidden lines, context blocks or rewrite). Cumulative per-file join is impossible: add is in FUN-28 and FUN-46, greet in FUN-66 and FUN-97. Grammar rules whose only fragment evidence is among the 20: print_block (STA-62) and pair (EXP-110, EXP-115). Traceability: a status line records its own hash, the expected output as ID@hash, and the parse_tree_hash, but no dependency. DSM-12 already re-derives a pending fragment when a norm cited in its reason changes hash, which is the mechanism an explicit dependency would reuse. Data dump of all examples: /private/tmp/claude-501/-Users-jpchauny-Documents-claude-plugins/731f6d5f-adb2-4162-bc8d-a0fbadc8e15e/scratchpad/examples.txt

### Lente: maintenance

**Volume of duplicated declarations (authoring cost of completeness)** — How many lines does an option make authors write and keep in step, beyond the lines that show the rule?

- Por qué importa: Duplication is the main cost of 'always complete'. If that cost is small for this corpus, the main argument against complete programs goes away.
- Favorece: Complete programs: with examples this small, the duplication is cheap. Hidden lines can keep the visible size where it is.
- Evidencia:
  - 71 Clean examples in tree.jsonl (64 valid, 4 syntax-error, 3 error) and 9 expected output blocks. They hold 418 code lines, median 5 per example (min 1, max 19). 16 examples have 3 code lines or fewer.
  - 81 of the 418 code lines (19%) are already section lines (start:, functions:, ...). Completeness at the section level is already paid for.
  - The 20 pending examples with undeclared names need about 61 names declared (FUN-69: 3, FUN-90: 4, EXP-28: 9, LEX-23: 8, EXP-83: 5, STA-12: 5, ...). That is roughly 60 to 90 new lines, about +15 to 20% over today's 418.
  - Declarations are already duplicated across examples: add in FUN-28, FUN-46 and FIL-70; greet in FUN-66, FUN-97 and TYP-263, with three different signatures; describe in FUN-49 and TYP-348; load in EXP-115 and TYP-361. The copies drift apart, and nothing breaks because each copy is checked on its own.

**Ripple radius of a change (hash invalidation fan-out)** — When one example changes, how many other norms, derived-semantics status lines and acceptance units become stale?

- Por qué importa: Every example is a norm with a tree hash (norms-tree R31). Layer 3 cites norms by ID@hash and finds stale citations by hash (ACU-27). Layer 2's work list re-checks a fragment when its hash, or the hash of a norm it cites, changes. A dependency multiplies the re-checks and reviews that one edit causes.
- Favorece: Self-contained examples, complete or completed by hidden lines inside the same block. If a dependency exists, it should be explicit, pinned by hash and narrow (one provider), never a global prelude.
- Evidencia:
  - The semantics status already pins one cross-norm dependency per fragment: "expected_output":"FUN-110@b5abd3a1" for FUN-16. The derive-semantics work list marks a fragment 'changed' when its norm hash, its expected output or a norm cited in its reason changes (derive-semantics.md, around lines 410-415).
  - With uses=, editing FUN-66 (3 functions) would invalidate FUN-69 too. The acceptance unit for FUN-69 must also cite FUN-66@hash, or layer 3 never notices the change (ACU-27 only sees cited hashes).
  - With a prelude that every example uses, one prelude edit invalidates all 67 semantic fragments and every acceptance unit that runs an example.
  - With complete programs the fan-out is 1: a change touches only its own norm.

**Stability of the dependency reference across layers** — Can layer 1 write the reference, and does it survive reordering, renumbering and moves without silently changing what the example means?

- Por qué importa: Layer 1 authors write no norm IDs. Layer 2 assigns IDs and pairs nodes across versions. A reference that layer 1 cannot write, or that the hashes cannot see, rots invisibly.
- Favorece: Complete programs. Failing that, explicit named labels written in layer 1. Positional or 'sequence per section' coupling is disfavoured, because the hash model is blind to order.
- Evidencia:
  - Norm IDs such as FUN-66 exist only in layer 2's annotated copy. The foundation (layer 1) text has none, so a literal uses=FUN-66 cannot be written where examples are authored. The reference would need a layer-1 label, such as name=.
  - norms-tree R13: sections, files and bulleted lists are unordered, and moving their children changes no tree hash. A positional dependency ('the previous example') would change meaning on reordering with no hash change and no report.
  - FUN-90 depends on FUN-28: it is about 280 lines later and in another top-level section (FUN-87 vs FUN-25), so 'previous example' does not reach it. FUN-69 depends on FUN-66, which is in a sibling section (FUN-67 vs FUN-64).
  - Precedent: CEX-27 ties an output block to an example by position, but only by strict adjacency, with the rationale 'the block names no example, so its place is what ties it to one'.

**Rot detectability (loud vs silent failure)** — When the spec changes, does an outdated example fail visibly in grammar, semantics or tests, or pass and mislead?

- Por qué importa: Examples define the language. An example that keeps passing for the wrong reason, or whose stated output nobody checks, is a wrong norm nobody notices.
- Favorece: Complete programs with expected output blocks. Every option must make dependencies explicit and checked, never implicit.
- Evidencia:
  - STA-37 (expect=error code=SEM004) uses an undeclared age, so it gives SEM002 before the SEM004 it is meant to show. An incomplete error example tests the wrong failure.
  - 17 examples state their output only in // prints: or // result: comments, which CEX-30 says nothing checks. Only 9 fragments have a checked expected_output block. Values like 'Age: 25' in STA-35 can only become a checked block once age is declared.
  - STA-33 declares age = 25 and price = 19.99, the same values STA-35's comments assume. That is implicit cross-example coupling today, and nothing records it.
  - Duplicated copies rot loudly: each copy goes through grammar and semantics separately. Implicit context rots silently: 20 of the 33 pending fragments are pending only because the context is not written down.

**Review cost for the approver (locality of review)** — Can the approver judge a diff to one example by reading that example alone?

- Por qué importa: Layer 1 changes are approved by a person. The hook (CEX-20, CEX-22, CEX-23) checks only textual rules, block by block. Anything that needs the whole graph of examples falls on the reviewer or on layer 2 after the fact.
- Favorece: Complete visible programs. Hidden lines inside the same block cost a little more. Dependencies and preludes cost the most.
- Evidencia:
  - CEX-23 decides whether a block is 'new' by its info string and code alone. It already assumes that blocks can be judged one at a time.
  - With uses=, a diff to a provider (FUN-66) needs the reviewer to find and recheck every dependent, and no current tool lists them.
  - With hidden lines, the reviewer sees all lines in raw Markdown but the reader does not. The reviewer must also check that the hidden setup does not carry meaning the prose never states.
  - With a prelude, every prelude diff is a review of the whole corpus.

**Spec size and readability (signal-to-noise in the spec files)** — How much of what the reader sees is scaffolding rather than the rule being illustrated?

- Por qué importa: The spec files are also the reading material of layer 1 (functions.md is 467 annotated lines). Scaffolding hides the point of an example, and the industry built hiding mechanisms for exactly this reason.
- Favorece: Hidden lines, or a completion step outside the visible text, for reading. Fully visible complete programs are the most honest but cost readability.
- Evidencia:
  - About 60 to 90 declaration lines would be added to 6 files. type-system.md holds 24 examples, functions.md 17, expressions.md and statements.md 13 each, lexical.md 8, file-structure.md 5.
  - Rustdoc: 'To keep each code block testable, we want the whole program in each block, but we don't want the reader to see every line every time' (https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html).
  - Sphinx testsetup blocks are 'not shown in the output for other builders' (https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html).

**Payoff of a dependency mechanism (how much coupling actually saves)** — For the examples that are incomplete today, how many could be completed by pointing at an existing example instead of writing declarations?

- Por qué importa: Coupling is only worth its ripple and review cost if it removes much duplication. If few providers exist, the mechanism adds complexity for little gain.
- Favorece: Complete programs, or hidden lines. A uses= mechanism would save writing for only about 3 of 20 examples.
- Evidencia:
  - Of the 20 pending examples with undeclared names, only 2 or 3 have a provider example: FUN-69 -> FUN-66 (greet, formatPrice, logMessage), FUN-90 -> FUN-28 (add, multiply, square, printMessage) and plausibly STA-35/STA-37 -> STA-33 (age, price).
  - The other ~17 (EXP-28, EXP-68, EXP-83, EXP-91, EXP-106, EXP-110, EXP-115, LEX-23, LEX-147, LEX-150, STA-9, STA-12, STA-62, STA-64, FUN-102, TYP-442) use names that no example declares: score, req, messages, post, comments, getUser, Request, sendUpdateToServer. They need new declarations under any option.
  - LEX-147's User and TYP-361's User are unrelated uses, and TYP-361 is itself pending.

**ID and hash stability during migration** — Does moving to the option edit existing norms in place, keeping their IDs, or create new norms and retire or rewire old ones?

- Por qué importa: Each edited example is reviewed once (status 'edited', to_review). Its acceptance-unit citations must also be updated once. New setup norms, or a shared prelude file, add IDs that every dependent must cite from then on.
- Favorece: In-place completion, visible or hidden lines in the same fenced block, over separate setup blocks or a prelude norm.
- Evidencia:
  - norms-versions R59 and R60: an example paired with an edited own hash keeps its ID and is 'edited' and to_review for one version, so migrating 20 examples in place costs 20 one-off reviews.
  - A separate setup block or prelude is a new code_block node with a new ID. Every consumer that runs a dependent example must also cite it, permanently.
  - Hidden lines inside the block change only that block's own hash. They add no node and no citation.

**Who decides each gap (issue and decision load on layer 1)** — Does the option settle the missing context with one rule, or leave it to a separate decision per example?

- Por qué importa: Today every pending fragment opens its own issue in layer 1 (DSM-10), and the deriver invents nothing. Gaps that one rule could settle become many small decisions for the owner.
- Favorece: Any option settled once at the rule level. Complete programs need 20 edits but no new mechanism. Multi-file or library context still needs an explicit rule of its own.
- Evidencia:
  - 33 pending fragments have 33 separate issues (for example clean-language-foundation #268, #269 and #270).
  - 20 or 21 of the 33 (FUN-60 counted or not) are pending only for undeclared context, the same open question CEX open question 1 names.
  - FIL-70 uses libraries (data, server) and imported files (app/utils.cln, app/mathHelpers.cln) that no norm gives. Completeness inside one block cannot solve it, because it needs multi-file or library context (CEX-11 says to use one example per file).

Opciones vistas: Always a complete visible program in each block (today's CEX-1, CEX-3, CEX-10 read strictly); Hidden setup lines inside the same block, shown to no reader but compiled and run (Rust doctest '#' lines, with '##' as escape; https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html); A single full program stored once, with visible fragments cut from it by anchors (Rust Book: each listing is a full Cargo project in listings/, shown with {{#rustdoc_include file:anchor}}, outputs in output.txt regenerated by tools/update-rustc.sh; https://github.com/rust-lang/book/blob/main/ADMIN_TASKS.md); Explicit include metadata per example (test262 frontmatter 'includes:' loads harness files before the test; https://github.com/tc39/test262/blob/main/INTERPRETING.md); Implicit global prelude for every example (test262 always loads assert.js and sta.js unless the 'raw' flag is set; Sphinx doctest_global_setup); Named setup groups (Sphinx testsetup/testcleanup per group, 'default' and '*' groups; https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html); Sequence with shared state inside one unit, isolation between units (Python doctest: examples in one docstring share names, other docstrings are invisible; https://docs.python.org/3/library/doctest.html); Whole-file example: the example plus its declarations as one file (Go testing: a file with one Example function and other declarations is shown whole; Output: comments are checked, examples without them are only compiled; https://pkg.go.dev/testing); Merged compilation with a per-example opt-out (Rust 2024 merged doctests, standalone_crate); An explicit dependency by a label written in layer 1 (uses=<name>/name=<name>), resolved and pinned as ID@hash in the derived status, like the existing expected_output field; A positional tie such as 'the previous example' (precedent: CEX-27 for output blocks, limited to strict adjacency); Spec tests linked to spec statements, with the spec version tracked (Kotlin/Core spec; https://discuss.kotlinlang.org/t/kotlin-language-specification-request-for-comments/18607)

Datos: Counts are from the norms repository at specs commit 11bc27ab (data/tree.jsonl). There are 7018 nodes, of which 152 are code_block nodes. 80 of those blocks are clean-language: 64 expect=valid, 4 syntax-error, 3 error and 9 clean-language-output. The other code blocks are 45 text, 14 json, 9 wit, 3 rust and 1 leftover 'clean' block that breaks CEX-2. The Clean examples hold 418 code lines in total, median 5 (min 1, max 19). 16 examples have at most 3 lines, and 81 lines are section lines. Section use: start: 51, functions: 21, class 5, can 2, and libraries:, import:, state:, tests: once each (all in FIL-70). 38 valid examples are start: only and 19 have no start:. Semantics status: 67 fragments, 34 derived and 33 pending, each pending one with its own layer-1 issue. 21 pending fragments are undeclared-name gaps (20 without FUN-60, whose contracts are not specified). The 20 need about 61 names declared. Only 2 or 3 have a providing example (FUN-69 -> FUN-66, FUN-90 -> FUN-28, STA-35/37 -> STA-33). FUN-28 is about 280 lines away in another top-level section, and FUN-66 is in a sibling section. Function names declared in several examples: add x3, greet x3 (3 different signatures), describe x2, load x2. 17 examples state output only in // prints: or // result: comments, and 9 have checked expected output. STA-37 is meant to fail with SEM004 but gives SEM002 first because of an undeclared name. Examples per file: type-system 24, functions 17, expressions 13, statements 13, lexical 8, file-structure 5.

### Lente: hybrids

**Fidelity between what the reader sees and what is checked** — When a reader copies the example exactly as shown into a file, does it build and run the way the spec says, or does it only work with context the reader cannot see?

- Por qué importa: In a language defined by its examples, the shown text is the norm. If the checked program differs from the shown fragment (hidden lines, an implicit wrapper, a prelude), the reader's copy and the acceptance test run different programs. Every hybrid mechanism found makes this trade, and each adds a way to show the hidden part again (a play button, a toggle) or a rule against copying a broken example.
- Favorece: Complete programs as shown, or hybrids that show the context on demand, like the Kotlin read-only regions or the whole-file examples of Go. It goes against invisible hidden lines and implicit preludes.
- Evidencia:
  - Rust doctests: lines that start with '# ' are compiled but not shown, and rustdoc wraps any code with no fn main in 'fn main() { your_code }' after inserting allow(unused...) and 'extern crate <mycrate>;': https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html
  - Rust API Guidelines C-QUESTION-MARK (examples use ?, not unwrap) and C-HIDDEN (hide unhelpful details) assume readers paste examples verbatim: https://rust-lang.github.io/api-guidelines/checklist.html
  - Kotlin playground: //sampleStart and //sampleEnd show the surrounding code read-only instead of hiding it, and extra files go in a <textarea class="hidden-dependency">: https://github.com/JetBrains/kotlin-playground
  - Go: 'The entire test file is presented as the example when it contains a single example function' plus other declarations, so the shown text is the checked text: https://pkg.go.dev/testing#hdr-Examples
  - Clean today: CEX-10 already makes every valid or error example a Clean source file at column 1, so what is shown is file-shaped, but 20 of the 33 pending fragments use names the shown file never declares

**Where the context lives and how it is named** — Does the example carry its own context (inline hidden lines), point to a named earlier example (a reference), get it from one shared prelude, or inherit it from its position in a sequence?

- Por qué importa: The location of the context decides who can find it, what a change breaks, and whether a generator can rebuild the program without guessing. Explicit named references can be checked mechanically. Context implied by position or by a session only works if the order is fixed and nothing in between interferes.
- Favorece: An explicit named reference (uses=<ID>, noweb style) for the few true dependencies, plus an explicit, visible prelude when a context is shared. It goes against implicit sequence or session inheritance.
- Evidencia:
  - Org-babel :noweb yes expands <<name>> into the code of a named block, and :noweb-ref concatenates blocks that share a name (that works for tangling, not for evaluation): https://orgmode.org/manual/Noweb-Reference-Syntax.html
  - Haskell doctest: a named chunk $setup runs before each example group, and if the setup fails, every test in the module is skipped: https://hackage.haskell.org/package/doctest
  - test262: frontmatter 'includes:' lists harness files to evaluate first, and 'flags: [raw]' says the source 'must not be modified in any way': https://github.com/tc39/test262/blob/main/INTERPRETING.md
  - Python doctest extraglobs merges a dict into the globals, so one generic example can be reused across subclasses: https://docs.python.org/3/library/doctest.html
  - Clean data: only 2 pending fragments depend on an earlier example by name (FUN-69 uses greet, formatPrice and logMessage from FUN-66; FUN-90 uses add, multiply, square and printMessage from FUN-28). 13 use free variables or functions that no example declares, and 4 use schematic placeholders.

**Isolation versus leakage between examples** — Can one example's state or declarations silently make another example pass, or fail, so that an example is valid only because of where it sits?

- Por qué importa: Every tool that shares state had to draw an explicit isolation boundary, because leaked state hides missing context. If the semantics shares context between examples, a pass can come from a neighbour and stop being a property of the example's own norm.
- Favorece: An isolated, complete unit per example, with any sharing declared explicitly. It goes against a book-wide session or cell sequence.
- Evidencia:
  - Python doctest uses a shallow copy of the module globals per docstring 'so that one test in M can't leave behind crumbs that accidentally allow another test to work'. Examples cannot see names from other docstrings: https://docs.python.org/3/library/doctest.html
  - Elixir doctests: consecutive iex> lines share bindings, and a blank line starts a new test. The docs also say 'doctests do not run in any kind of sandbox', so modules they define persist for the whole run: https://ex-unit.hexdocs.pm/ExUnit.DocTest.html
  - Racket Scribble: each examples form gets a fresh make-base-eval evaluator unless #:eval passes a shared one: https://docs.racket-lang.org/scribble/eval.html
  - Jupyter (Pimentel et al., MSR 2019, 1.4M notebooks): about 24% ran without errors and about 4% reproduced their results. The causes named include hidden state and out-of-order execution: https://2019.msrconf.org/details/msr-2019-papers/36/A-Large-scale-Study-about-Quality-and-Reproducibility-of-Jupyter-Notebooks (figures as reported at https://koaning.io/til/many-notebooks)

**Graded verification level per example** — Does each example declare how far it is checked (parse only, type-check only, run, run with an exact output, fail with a code), so that a schematic fragment can still be checked at the level it supports?

- Por qué importa: Several pending Clean fragments are syntax schemas (functionName(arg1, arg2, arg3)), not programs. Industry tools rarely force those to be complete programs. They lower the level of checking instead. That lets pedagogy keep the fragments without the semantics inventing declarations, but each lower level is an escape hatch that can be abused.
- Favorece: An explicit parse-only level (for example expect=syntax, checked by the grammar only) for schemas, instead of forcing them into whole programs or into unchecked text. It warns against a generic ignore.
- Evidencia:
  - Rust: ignore, no_run (compile but do not run), compile_fail, should_panic. rustdoc itself says ignore 'is almost never what you want as it's the most generic' and recommends text or hidden lines instead: https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html
  - Go: 'Example functions without output comments are compiled but not executed'. 'Unordered output:' matches lines in any order: https://pkg.go.dev/testing#hdr-Examples
  - mdBook: ignore (not tested), noplayground (tested, no play button), and configurable hidden-line prefixes for other languages: https://rust-lang.github.io/mdBook/format/mdbook.html
  - Clean today has 3 levels: expect=valid with an optional output, expect=error code=, and expect=syntax-error code= line=. CEX-3 sends non-file text to text blocks (44 text blocks are present), which drops even the grammar check.
  - Clean data: 4 pending fragments are schematic (EXP-28, EXP-106, LEX-23, STA-12, with functionName, arg1, functionCall, defaultValue, compute, arr, obj and val). The grammar could check them while the semantics skips them.

**Error examples fail for the right reason** — When an example is expected to fail with a code, can missing context make it fail earlier with a different error, so that a 'fails' result proves nothing?

- Por qué importa: An incomplete example and a negative example look the same to a checker that only asks whether it failed. Precise error codes and phases are how the industry tells them apart, and they only work if the rest of the program is complete.
- Favorece: Complete programs for every error example, at least, with the code checked exactly (as Clean already does with code=). Hidden or implicit context is risky for negative examples.
- Evidencia:
  - Rust compile_fail,E0XXX checks the error code only on nightly (on stable it is ignored), and rustdoc has a MissingErrorCodes failure for code that fails to compile without the expected code. The error index depends on it: https://doc.rust-lang.org/rustdoc/unstable-features.html
  - test262 negative: {phase: parse|resolution|runtime, type: <ErrorConstructor>}: https://github.com/tc39/test262/blob/main/INTERPRETING.md
  - Scribble eval:error expects an exception and eval:check compares the result: https://docs.racket-lang.org/scribble/eval.html
  - Clean: STA-37 (expect=error code=SEM004) uses the undeclared name age, so 'it gives SEM002 before the SEM004 it expects'. The missing context masks the very error the example teaches.

**Change propagation and identity (hashes and IDs)** — When the context of an example changes, does the example's identity (norm ID and hash) change with it, so that derived artifacts are invalidated?

- Por qué importa: Clean's derived semantics and grammar key each fragment by ID@hash (the status file records hash and parse_tree_hash). Inline hidden lines are part of the block, so the hash follows them. A reference (uses=FUN-66) or a global prelude sits outside the block, so a change there leaves the dependent hash unchanged and its derived state silently stale, unless the hash covers the transitive closure.
- Favorece: Self-contained examples, or references whose closure is folded into the hash (hash of the example plus the hashes of its uses=). It goes against an unversioned global prelude.
- Evidencia:
  - Clean status file: each fragment row holds id, hash, parse_tree_hash and expected_output as 'FUN-110@b5abd3a1', so invalidation is per block hash.
  - Haskell doctest $setup: a failure in shared setup skips every test of the module, so one change spreads to all dependents: https://hackage.haskell.org/package/doctest
  - Rust 2024 merged doctests: tests that depend on line numbers break when other doctests change, and standalone_crate isolates them: https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html

**Stability of diagnostic coordinates (line=)** — Does adding context (hidden lines, a wrapper, a prelude, a joined dependency) shift the line numbers that error examples state?

- Por qué importa: Clean syntax-error examples state line=<n>, counted from line 1 of the code. Any mechanism that prepends text changes the line the compiler reports, unless the line map is specified.
- Favorece: Complete programs as shown, or a context mechanism whose line map is specified (for example, context joined only into sections after the error line, or line counted in the shown text).
- Evidencia:
  - Rust: line-dependent doctests break when they are merged, and standalone_crate keeps their 'line information' stable: https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html
  - Rust's fn main wrapping and its inserted allow and extern crate lines shift the compiled lines, and rustdoc has to map them back.
  - Clean: 4 expect=syntax-error examples carry line=. CEX-6 counts line from 1 to the number of lines of the shown code.

**Determinism of the joined program** — Is the program that context plus fragment produce unique and well defined (no name collisions, a fixed order, no output from the context), so that both the Lean semantics and the future compiler build the same program?

- Por qué importa: Joining is only safe when the language gives a canonical way to merge. Clean's fixed section order makes this well defined when sections do not collide. A context that prints, or that declares a name the example redeclares, breaks byte-for-byte output (CEX-29) or changes the error.
- Favorece: An explicit join by sections (uses= that merges by section, with collisions as violations, and a context that holds no start:) over textual hidden lines or sessions.
- Evidencia:
  - Rust inserts the wrapper and hidden lines with fixed preprocessing in 5 steps, and 'Whether doctests are merged or not, they are run in their own process': https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html
  - Org-babel noweb concatenates text with no semantic merge, and noweb-ref references do not work for evaluation: https://orgmode.org/manual/Noweb-Reference-Syntax.html
  - Clean section order: libraries:, import:, source:, constant:, state:, can, class, functions:, watch, tests:, start:. FUN-66 holds only functions: and FUN-69 holds only start:, so their join is unique.
  - Clean: 9 examples have an expected output block, and a context that prints would break them.

**Invention of meaning by generators** — Does the mechanism make a generator, or the spec writer, choose types and values the prose never gave (the type of score, the value of age)?

- Por qué importa: DSM-10 forbids the semantics from inventing declarations. A hidden prelude that declares 'integer score = 75' is a new norm in itself, so it has to be written by layer 1 and reviewed like any other example, or the examples' meaning drifts between the semantics and the compiler.
- Favorece: Complete programs written by the author, or a context written by the author in layer 1 (explicit hidden lines or uses=). Never context inferred downstream.
- Evidencia:
  - Python extraglobs and Haskell $setup put the context in code that the author writes, never in code the tool infers: https://docs.python.org/3/library/doctest.html, https://hackage.haskell.org/package/doctest
  - Clean data: 13 pending fragments (FUN-102, EXP-68, EXP-83, EXP-91, EXP-110, EXP-115, LEX-150, STA-9, STA-35, STA-37, STA-62, STA-64, TYP-442) plus LEX-147 (no class User) need typed declarations that no norm gives. Only 2 (FUN-69, FUN-90) can be filled from existing examples with no invention.

Opciones vistas: Always a complete program as shown (current CEX-1, CEX-3, CEX-10; Go whole-file examples; test262 raw); Implicit wrapper: the tool wraps a fragment in a fixed skeleton (Rust fn main wrapping; for Clean, wrap section-less statements in start:); Inline hidden lines that are compiled but not shown, with an escape (Rust '# ' and '##'; mdBook hidelines prefix per language); Shown but read-only surrounding context (Kotlin playground //sampleStart and //sampleEnd) and hidden dependency files (hidden-dependency textarea); Explicit named reference to another block (org-babel noweb <<name>>, :noweb-ref; a proposed uses=<ID> in the info string, joined by Clean sections); Declared harness or prelude in metadata (test262 includes:, Haskell doctest $setup, Python extraglobs); Session or sequence with an explicit reset boundary (Python per-docstring globals, Elixir iex blocks split by a blank line, Scribble shared #:eval evaluator versus a fresh default, Jupyter cells); Graded verification levels (Rust ignore, no_run, compile_fail, should_panic; Go Output:, Unordered output: and compile-only examples without output; mdBook noplayground; a proposed Clean parse-only level for schematic fragments); Precise negative expectations (Rust compile_fail,E0XXX with MissingErrorCodes; test262 negative phase and type; Scribble eval:error and eval:check; Clean code= and line=); Isolation from line-number coupling (Rust standalone_crate versus merged doctests in the 2024 edition); Keep non-programs as text blocks (CEX-3; rustdoc recommends text over ignore)

Datos: Counted in /Users/jpchauny/Documents/Clean Language/clean-language-norms (read-only). Clean examples in specs-repo-annotated/specs: 71 (64 expect=valid, 3 expect=error, 4 expect=syntax-error), 9 clean-language-output blocks, 44 text blocks. Status file specs-derived/semantics/clean-language-code-examples-status.jsonl: 67 fragments (64 run, 3 error: 2 SEM001, 1 SEM004), 34 derived, 33 pending. 20 pending reasons say 'does not declare'. LEX-147 ('declares no class User') and FIL-70 (imports app/utils.cln and libraries data and server) are also missing context, so 22 of the 33 pending lack context in some way. Classification of the 22: (A) depend by name on an earlier example, all names found: 2 (FUN-69 from FUN-66; FUN-90 from FUN-28). (B) free variables, functions or classes that no example declares, so typed declarations would have to be invented: 14 (FUN-102, EXP-68, EXP-83, EXP-91, EXP-110, EXP-115, LEX-147, LEX-150, STA-9, STA-35, STA-37, STA-62, STA-64, TYP-442). (C) schematic placeholders, really syntax schemas: 4 (EXP-28, EXP-106, LEX-23, STA-12). (D) a spec gap, not context: 1 (FUN-60 reads the contract keyword result in an after: block; Contracts is not specified). (E) multi-file or library context: 1 (FIL-70). STA-37 is an error example (SEM004) that the undeclared name age masks with SEM002. The other 11 pending are spec gaps unrelated to context (literal typing of sized types, number-to-text formatting, time.now, iterate/add, error.message, toInteger/toBoolean, the automatic constructor). So: a uses= or join mechanism alone resolves at most 2 of 22; a parse-only level covers 4 at the grammar level; the remaining 14 need context written in layer 1 (complete programs or author-written hidden context) whichever mechanism is chosen.

## 3. Ejes unidos

- **A1 Pedagogy of a sequence (user's axis a): teaching by accumulation and context:** Does the reader learn better when later examples reuse what earlier ones built, and are short fragments understood from the surrounding prose and sequence?

- **A2 Every example is complete valid or invalid code (user's axis b): one reading rule and a signalled status:** Is each Clean example judged as a whole program, so that expect=valid, expect=error and expect=syntax-error mean exactly what they say, with no third state 'valid given context you cannot see'?

- **A3 Genre and audience: normative reference read out of order vs tutorial read in order:** Is the text that holds the example a reference opened at one rule (by a learner, a spec author, the grammar and semantics generators and the acceptance tests), or a lesson read from start to finish?

- **A4 Focus vs boilerplate in the medium the spec is read in:** How much of what the reader sees is the point of the example, and how much is scaffolding, given that these specs are read as GitHub-rendered Markdown with no doc renderer?

- **A5 Fidelity and reproducibility: what is shown is what is checked:** Can a reader copy the block exactly as shown into a file, run it, and get what the text says, with the same program the semantics and the acceptance tests run?

- **A6 Semantic closure without invention:** Does the example, plus only context that a norm states explicitly and that layer 1 wrote, bind every name it uses with a type and, to run, a value, so that no generator or compiler has to invent declarations?

- **A7 Hermetic unit: one block, one hash, one verdict, one blame:** Is everything that decides an example's outcome inside the bytes whose hash identifies it, so that an edit elsewhere cannot silently change its verdict, and a failure points at the norm it illustrates?

- **A8 Stability of the reference under reordering, insertion and across layers:** Does the meaning of an example survive moving, inserting or reordering examples and sections, and can layer 1, which writes no norm IDs, write the reference?

- **A9 Composability and determinism of the joined program:** When context and example are joined, is the result one well-defined Clean file (fixed section order, no duplicate names, at most one start:, context that prints nothing), with error line numbers still meaning what they say?

- **A10 Oracle strength: what a passing example proves:** Does the example have an entry point and a checked observable result (output block, assertion), or does 'derived' only mean 'type-checks and terminates'?

- **A11 Precision of negative examples (error masking):** Does an error example fail with its declared code for the declared reason only, or can missing context raise another error first?

- **A12 Phase granularity: instance vs schema, and grammar evidence:** Does the expectation say which phase the example is evidence for (parse, check, run), so that a schema with metavariables can stay checked by the grammar without being forced to be a runnable program or demoted to unchecked text?

- **A13 Host, external context and shared trusted base:** Are the clock, stdin, imported files, libraries and any shared prelude fixed by the norms, small, versioned and checked, with an opt-out, so outputs reproduce byte for byte?

- **A14 Authoring, review and migration cost:** How many lines must authors write and keep in step, can the approver judge a diff by reading one block, can the hook catch a missing context at write time, and how many IDs, reviews and citations does migration cost?

## 4. Opciones

### O1 Always a complete visible program (strict closure)

Strengthen CEX-10 (The code): the code of every expect=valid and expect=error example, read alone, is a Clean file that declares every name it uses (types and values), apart from names that a norm of the language or an explicitly specified library defines. The checker builds the program from the block exactly as shown: no join, no wrapper, no prelude. A dependency is resolved by copying the declarations needed, or by merging provider and consumer into one example. '// prints:' comments become a clean-language-output block where the output is deterministic. Schemas go to `text`, each paired with one concrete instance. Name closure stays a layer-2 check (CEX-21); its failure is reported as 'example not closed', not as a prose gap.

Precedente: Tour of Go slides (https://go.dev/tour/), Go whole-file examples (https://pkg.go.dev/testing#hdr-Examples), JLS 'This program produces the output:', ACATS C-tests, Wasm modules, test262 with flags: [raw], Rust Book listings kept as complete Cargo projects.

FUN-66 + FUN-69 con esta opción:

````text
FUN-66 stays as is (functions: only, typing only), or gains a start: with an output block. FUN-69 becomes one file:
```clean-language expect=valid
functions:
	string greet(string name = "World")
		return "Hello, " + name

	string formatPrice(number amount, string currency = "USD")
		return currency + " " + amount.toString()

	void logMessage(string message, string level = "INFO")
		print("[" + level + "] " + message)

start:
	print(greet())
	print(greet("Alice"))
	print(formatPrice(9.5))
	print(formatPrice(9.5, "EUR"))
	logMessage("System started")
	logMessage("Error occurred", "ERROR")
```
```clean-language-output
Hello, World
Hello, Alice
USD 9.5
EUR 9.5
[INFO] System started
[ERROR] Error occurred
```
Alternative: delete FUN-66 and keep this single example under the default-values heading. Either way, it still waits on the number-to-text gap of STA-33 (amount.toString()).
````

### O2 Fragments with implicit context from the sequence (status quo made a rule)

Examples are written as today. When an example uses a name it does not declare, the checker joins it, section by section in the fixed order, with the nearest earlier expect=valid example in the same spec file that declares the name and has no start:. Repeat until all names resolve or none is found. Nothing in the info string records the dependency. The hash stays the example's own hash, so a change to the provider is invisible to DSM-12 unless the work list recomputes the lookup on every run.

Precedente: Books and tutorials read in order: SICP 1.1 ('Having defined square, we can now use it'), the Python tutorial REPL, Jupyter cells run top to bottom. Language specs with informative fragments: the Go spec, C standard EXAMPLE paragraphs.

FUN-66 + FUN-69 con esta opción:

````text
FUN-66 and FUN-69 stay byte for byte as they are now. The checker sees greet, formatPrice and logMessage free in FUN-69, finds FUN-66 as the nearest earlier declarer, and builds functions: (FUN-66) + start: (FUN-69). The same rule applied to FUN-90 picks FUN-46, which declares add closer than FUN-28 does. That is the wrong provider, which shows how fragile the rule is.
````

### O3 Explicit named dependency (name= / uses=), joined by sections

Layer 1 writes the reference with a label, because it has no norm IDs. The provider's opening line gets `name=<label>` (unique in the repo, kebab-case). The consumer's opening line gets `uses=<label>[,<label>]`. The hook checks the text: the label exists and belongs to an active expect=valid example with no start:, there is no cycle, and no section or declared name collides. The checker builds the program by merging the providers' sections and then the consumer's into the fixed section order. Within a section the provider's lines come first. A duplicate name is a violation. line= stays counted in the consumer's shown code. Layer 2 resolves each label to ID@hash and records it in the status line (uses: ["FUN-66@<hash>"]). DSM-12 re-derives the consumer when a provider's hash changes, and the consumer's acceptance unit cites the provider too.

Precedente: Org-babel noweb <<name>> (https://orgmode.org/manual/Noweb-Reference-Syntax.html), test262 includes: (https://github.com/tc39/test262/blob/main/INTERPRETING.md), Wasm named modules and register (https://github.com/WebAssembly/spec/blob/main/interpreter/README.md), Racket Scribble shared #:eval, mdBook {{#include file:anchor}}.

FUN-66 + FUN-69 con esta opción:

````text
```clean-language expect=valid name=default-values
functions:
	string greet(string name = "World")
	...(FUN-66 unchanged)
```
```clean-language expect=valid uses=default-values
start:
	print(greet())
	print(greet("Alice"))
	...(FUN-69 unchanged)
```
```clean-language-output
Hello, World
...
```
The checked program is FUN-66's functions: followed by FUN-69's start:. The status line of FUN-69 records uses FUN-66@<hash>.
````

### O4 Hidden context lines inside the block (Rust-doctest style)

Inside a Clean example, a line whose code starts with `# ` (hash, space) is a context line. The checker drops the `# ` and compiles the full program. A renderer that understands the marker hides these lines and shows a toggle to expand them. GitHub, which has no such renderer, shows them with the `#`. `##` escapes a literal `#`. CEX-10 is amended so that `# <section>:` counts as a section line. The hash covers the context, because it is part of the block's own_text. line= and the expected output refer to the full program (rule to be fixed). The context is written by the layer-1 author and reviewed like any other code (DSM-10).

Precedente: rustdoc hidden `# ` lines and `##` escape (https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html), mdBook per-language hidelines prefix (https://rust-lang.github.io/mdBook/format/mdbook.html), Lean Verso hidden import/open/set_option commands.

FUN-66 + FUN-69 con esta opción:

````text
FUN-66 stays as is. FUN-69:
```clean-language expect=valid
# functions:
# 	string greet(string name = "World")
# 		return "Hello, " + name
# 	string formatPrice(number amount, string currency = "USD")
# 		return currency + " " + amount.toString()
# 	void logMessage(string message, string level = "INFO")
# 		print("[" + level + "] " + message)
start:
	print(greet())
	print(greet("Alice"))
	...
```
followed by the output block. The checker sees the same program as O1; the reader sees only the start: lines, given a renderer.
````

### O5 A standard prelude joined to every example

The norms hold one prelude: a block `clean-language expect=context` in a dedicated spec file (for example specs/language/example-prelude.md). It has no start: and declares shared fixtures (functions, a few constants or state such as score, age, price, user) and later the stdlib stubs. The checker joins the prelude, section by section, before every example unless the example's opening line says `raw`. A local declaration of a prelude name is a collision, and the example must say `raw`, unless shadowing rules are specified. Every derived status line and acceptance unit cites the prelude's ID@hash, so a prelude edit invalidates all 67 fragments. The prelude must print nothing and must not shift line=, which is counted in the example.

Precedente: test262 assert.js and sta.js loaded before every test, with flags: [raw] to opt out; Sphinx doctest_global_setup; Haskell doctest $setup; Wasm's implicit spectest host module, now deprecated in favour of explicit register.

FUN-66 + FUN-69 con esta opción:

````text
The prelude declares greet, formatPrice and logMessage, together with the other fixtures. FUN-69 stays as it is today, and the checker builds prelude + FUN-69. FUN-66 now collides with the prelude's greet, formatPrice and logMessage, so it must say `raw`, or its content moves into the prelude and it stops being an example. FUN-97 and TYP-263 redeclare greet with other signatures, so they need `raw` too.
````

### O6 Session per section or per labelled group (doctest / org-babel :session style)

Examples that share a session label (`session=<label>` on the opening line, or by default all examples under the same H2 heading) form a sequence. The checked program for example k merges the declaration sections of examples 1..k-1 of the session with all of example k. Only example k's start: body runs, which respects FIL-54 (at most one start: per file). Redeclaring a name inside a session is a violation. `fresh` on an opening line starts a new session. The hash of example k must cover the hashes of all earlier examples in its session, and reordering inside a session changes meaning, which R13 cannot see.

Precedente: Python doctest (names shared within one docstring, never across), Elixir iex blocks split by a blank line (https://ex-unit.hexdocs.pm/ExUnit.DocTest.html), org-babel :session, Racket Scribble shared evaluator, Jupyter notebooks (hidden-state problems measured in Pimentel et al., MSR 2019).

FUN-66 + FUN-69 con esta opción:

````text
FUN-66 and FUN-69 sit under sibling H3 headings (FUN-64, FUN-67) of the same H2. With the H2 default they join a session that also holds FUN-28, FUN-46 and FUN-49 to FUN-81, and they collide on add and greet. So both need an explicit label:
```clean-language expect=valid session=default-values
functions:
	...(FUN-66)
```
```clean-language expect=valid session=default-values
start:
	...(FUN-69)
```
The checked program for FUN-69 is FUN-66's functions: plus FUN-69's start:.
````

### O7 Complete program with a marked focus region

As in O1, every example is a complete, closed program shown in full, so copy-paste works and shown = checked. Two comment lines, `// focus` and `// end focus`, mark the lines the prose is about. They are ordinary Clean comments, so the checker, the grammar and the hash need no change, and line= is unaffected. A future renderer may fold everything outside the region, and GitHub shows it all. The hook can check that markers are paired and that at most one region exists. A variant keeps one complete program per section and shows anchored excerpts of it (mdBook include:anchor), checking only the whole program.

Precedente: Kotlin Playground //sampleStart ... //sampleEnd with the rest read-only or folded (https://github.com/JetBrains/kotlin-playground), Kotlin KDoc @sample showing part of a compiled function, mdBook {{#include file:anchor}} / {{#rustdoc_include}} over complete Rust Book listings, Go whole-file examples.

FUN-66 + FUN-69 con esta opción:

````text
FUN-66 stays as is. FUN-69 is the O1 file, with the start: body wrapped:
```clean-language expect=valid
functions:
	string greet(string name = "World")
	...(three functions)
start:
	// focus
	print(greet())
	print(greet("Alice"))
	...
	// end focus
```
followed by the output block.
````

### O8 Phase-graded expectations (syntax-only level for schemas and forms)

Add a fourth expectation, `expect=syntax`: the code must parse as a Clean file (CEX-10 shape), and the grammar uses it as evidence. The semantics and the acceptance tests skip it, apart from a parse check. It is explicitly not semantic evidence, has no output block, and needs no name closure. It is meant for schemas with metavariables (EXP-28, EXP-106, LEX-23, STA-12) and keeps the grammar evidence of print_block and pair. The hook requires that an expect=syntax example sit next to at least one concrete expect=valid instance in the same section, so it cannot become a generic `ignore`. On its own it does not close any example that claims to run, so it complements O1, O3, O4 or O7.

Precedente: Wasm assert_malformed / assert_invalid / assert_unlinkable vs assert_return; test262 negative.phase parse|resolution|runtime; ACATS test classes B, C and L; rustdoc no_run and ignore (the latter 'almost never what you want'); Go examples without Output: are compiled but not run; Haskell Report italic holes and Go EBNF for forms.

FUN-66 + FUN-69 con esta opción:

````text
Used alone for FUN-69, it would be `clean-language expect=syntax` with FUN-66 unchanged. It parses, but the meaning of default values is never checked and the six '// prints:' claims remain unchecked, which shows this is the wrong tool for FUN-69. Its proper use is EXP-106 (`functionName(arg1, arg2, arg3)` as expect=syntax), next to FUN-69 written under O1, O3 or O4.
````

## 5. Jueces

### Juez pedagogy-first

Ranking: O7, O1, O8, O3, O4, O6, O2, O5

Veredicto: From the learner's side, yes: every expect=valid and expect=error example should be a complete, visible program (O1), with O7's // focus markers as an optional aid and O8's expect=syntax kept only for metavariable schemas, each paired with a concrete instance.

1. **What the learner can see.** These specs are read as GitHub Markdown, and GitHub shows only the first word of the info string. So uses=, session= and raw are invisible to the reader, and a non-Clean '# ' prefix shows up as literal noise. That sinks the dependency-based options on readability:
   - O3 and O6 look exactly like today's broken fragments to the reader.
   - O4 shows '# functions:' and fails when pasted.
   - O2 and O5 depend on context the reader cannot find.

2. **User axis (a), pedagogy, does not favour fragments here.**
   - A reference is opened at one rule, not read in order.
   - Only FUN-69 -> FUN-66 and FUN-90 -> FUN-28 have a real provider. Nearest-earlier lookup even picks the wrong one for FUN-90 (FUN-46).
   - About 16 of the 20 pending fragments use names (score, age, price, username) that no earlier text declares, so no sequence teaches them.

3. **What pedagogy needs is O1.**
   - FUN-69 becomes one example that declares greet, formatPrice and logMessage, calls them, and replaces its six unchecked '// prints:' comments with a clean-language-output block.
   - FUN-66 may then be merged into it or kept as the declaration-only view.
   - The cost to the reader is about 15-20% more visible lines, mostly short declarations that are on-topic for defaults anyway.

4. **O1 also fixes what a learner cannot detect.**
   - STA-35's 'Age: 25' becomes reproducible.
   - STA-37 fails with the SEM004 it teaches, not with SEM002.

5. **Conditions on the add-ons.**
   - Focus markers must be optional: on a 5-line block they are noise.
   - expect=syntax must require an adjacent concrete instance, or it becomes rustdoc's 'ignore' under another name.

6. **What the user's axes miss.** Fidelity (A5, what is shown is what is checked) and error precision (A11, an error example fails only for its declared reason) are the axes that decide this for a learner.

7. **What no format fixes.** The roughly 11 prose gaps remain under every option: number-to-text (it still blocks FUN-69's amount.toString()), time.now and the FIL-70 imports.

Read for this: /Users/jpchauny/Documents/Clean Language/clean-language-norms/specs-repo-annotated/specs/language/functions.md (FUN-66 and FUN-69).

Pesos: A1=3, A2=2, A3=3, A4=3, A5=3, A6=1, A7=1, A8=1, A9=1, A10=2, A11=2, A12=1, A13=1, A14=1

| Opción | Eje | Nota | Razón |
|---|---|---|---|
| O1 | A1 | 3 | Loses accumulation, but the prose can still say 'the functions above', and merging FUN-66 and FUN-69 into one example teaches defaults better: declaration, call and result together. |
| O1 | A2 | 5 | expect=valid means exactly that for the block the reader sees, with no hidden third state. |
| O1 | A3 | 5 | A learner who opens functions.md at 'Usage Examples' (FUN-67) gets a program that stands alone, which is how a reference is actually read. |
| O1 | A4 | 3 | About 60-90 visible lines over 418 (+15-20%), all shown on GitHub. Small, but in examples like STA-35 the declarations of age and price compete with the point. |
| O1 | A5 | 5 | Copy, paste, run, see the output block: shown = checked, so STA-35's 'Age: 25' becomes reproducible. |
| O1 | A6 | 5 | Every name is bound in the block, so no deriver invents context (DSM-10). |
| O1 | A7 | 5 | One block, one hash, one verdict. A failure points at the example's own norm. |
| O1 | A8 | 5 | Moving FUN-69 anywhere leaves its meaning unchanged. |
| O1 | A9 | 5 | No join, so section order, a single start: and line= are trivially well defined. |
| O1 | A10 | 4 | Turning FUN-69's six '// prints:' into an output block gives the learner the verified result, not an unchecked claim. |
| O1 | A11 | 5 | STA-37 declares age, so the SEM004 it expects is not masked by SEM002, and a learner is not shown the wrong reason for an error. |
| O1 | A12 | 2 | Schemas such as EXP-106 and LEX-23 go to text: readable as forms, but no longer checked, and the grammar loses its evidence for print_block and pair. |
| O1 | A13 | 3 | Adds no prelude vocabulary. The clock, stdin and the FIL-70 imports stay as open gaps, but they are visible. |
| O1 | A14 | 3 | About 20 one-off edits and reviews. Copies like greet x3 can drift, but they fail loudly. |
| O2 | A1 | 3 | It looks like a book, but only 2-4 of the 20 have a provider, and for FUN-90 nearest-earlier picks FUN-46 instead of FUN-28, which teaches the wrong add. |
| O2 | A2 | 1 | FUN-69 read alone is an invalid program labelled valid: the very mix of signals that A2 forbids. |
| O2 | A3 | 1 | A learner who lands on a rule from a link or a search sees calls to names declared in another section, with nothing to say where. |
| O2 | A4 | 5 | The shortest blocks, and no scaffolding at all. |
| O2 | A5 | 1 | Pasting FUN-69 gives undeclared greet, and STA-35's '25' is unreproducible: precisely the Rust Book 'may not compile' warning. |
| O2 | A6 | 2 | Fills at most FUN-69 and FUN-90. The other ~16 stay pending forever. |
| O2 | A7 | 1 | Renaming greet in FUN-66 silently leaves FUN-69@hash stale. |
| O2 | A8 | 1 | Inserting an example that declares add between FUN-28 and FUN-90 changes FUN-90's meaning, and R13 shows no hash change. |
| O2 | A9 | 2 | Providers must have no start:, so STA-33 cannot serve STA-35 or STA-37, and the cumulative collisions (add, greet) remain. |
| O2 | A10 | 2 | No change. The unchecked '// prints:' comments stay. |
| O2 | A11 | 1 | STA-37 still fails with SEM002 before its SEM004, so a learner sees a misleading error example. |
| O2 | A12 | 1 | Schemas stay mislabelled as valid and pending. |
| O2 | A13 | 2 | Implicit context is unversioned host-like state. |
| O2 | A14 | 2 | Costs zero lines today, but rots silently, and no reviewer can judge one block on its own. |
| O3 | A1 | 4 | An explicit 'continues default-values' link preserves the teaching sequence of FUN-66 then FUN-69 without guessing. |
| O3 | A2 | 4 | The status is honest given the declared context, but the block alone is still not a program. |
| O3 | A3 | 2 | GitHub renders only the first word of the info string, so uses=default-values is invisible to a reader who opens FUN-69 cold. |
| O3 | A4 | 5 | The consumer stays focused on the calls. |
| O3 | A5 | 2 | The copied block does not run, and the label that would explain why is not rendered. |
| O3 | A6 | 4 | It closes the 2-4 examples that have a provider without invention. The rest still need new declarations. |
| O3 | A7 | 3 | The verdict depends on another block, but ID@hash plus DSM-12 tracks it. |
| O3 | A8 | 4 | The label survives reordering and can be written in layer 1. |
| O3 | A9 | 3 | The section merge is well defined, but a provider with start: is excluded, so STA-35 and STA-37 are not solved. |
| O3 | A10 | 4 | FUN-69 can carry an output block. |
| O3 | A11 | 3 | It fixes masking only where a provider exists. |
| O3 | A12 | 1 | Does not address schemas. |
| O3 | A13 | 3 | Neutral. |
| O3 | A14 | 3 | A whole mechanism (labels, hook, status field, ACU citations) for 2-4 cases, and a provider diff needs its dependents rechecked. |
| O4 | A1 | 2 | Not a sequence mechanism: it duplicates context, like O1, but hides it. |
| O4 | A2 | 4 | The checker sees a whole program. |
| O4 | A3 | 3 | Self-contained, but the reader sees a mixed block. |
| O4 | A4 | 2 | No renderer exists, so on GitHub the learner sees '# functions:' lines, foreign syntax in a language whose comments are //, which is worse noise than plain declarations. |
| O4 | A5 | 1 | Pasting from GitHub copies the '# ' prefixes and fails to parse: shown != checked, the worst copy-paste result. |
| O4 | A6 | 5 | Context is explicit and author-written. |
| O4 | A7 | 5 | The hash covers the context. |
| O4 | A8 | 5 | Position-independent. |
| O4 | A9 | 3 | line= and output must now refer to a program the rendered reader does not see in full. |
| O4 | A10 | 4 | Enables output blocks. |
| O4 | A11 | 4 | It closes STA-37, but the reported error lines count hidden lines. |
| O4 | A12 | 2 | Schemas are unaddressed. |
| O4 | A13 | 3 | Neutral. |
| O4 | A14 | 3 | Same lines as O1, plus a CEX-10 amendment and a marker syntax to teach. |
| O5 | A1 | 2 | The learner meets score, age and user from a file never mentioned in the section: magic, not sequence. |
| O5 | A2 | 2 | 'Valid' secretly means 'valid with the prelude'. |
| O5 | A3 | 2 | A reference reader must know about a hidden global file. |
| O5 | A4 | 5 | The shortest blocks. |
| O5 | A5 | 1 | Nothing pasted runs without hunting down the prelude. |
| O5 | A6 | 3 | It binds names, but with an invented fixture vocabulary that is itself unspecified language. |
| O5 | A7 | 1 | One prelude edit invalidates all 67 fragments and every acceptance unit. |
| O5 | A8 | 3 | Order-independent, but global. |
| O5 | A9 | 1 | It collides with local x, value, price and age in more than 10 examples. FUN-66, FUN-97 and TYP-263 need raw, and FUN-66, the example that teaches defaults, gets pushed into the prelude. |
| O5 | A10 | 3 | Enables output, at the cost of a shared trusted base. |
| O5 | A11 | 2 | Prelude names can make a wrong example pass or mask an error. |
| O5 | A12 | 1 | Unaddressed. |
| O5 | A13 | 1 | An unversioned fixture standing in for a stdlib that is 'not specified yet'. |
| O5 | A14 | 2 | Every prelude diff is a review of the whole corpus. |
| O6 | A1 | 4 | The closest to doctest-style teaching by accumulation within a group. |
| O6 | A2 | 2 | Validity depends on invisible predecessors. |
| O6 | A3 | 2 | Opening a rule mid-session breaks, and session= is invisible on GitHub. |
| O6 | A4 | 5 | Short blocks. |
| O6 | A5 | 1 | Example k alone does not run, the Jupyter hidden-state failure in miniature. |
| O6 | A6 | 3 | Closes only what an earlier session member declares. |
| O6 | A7 | 1 | The hash of example k must fold in all its predecessors. |
| O6 | A8 | 1 | Reordering inside a session changes meaning, and R13 cannot see it. |
| O6 | A9 | 2 | The H2 default collides FUN-66 with FUN-28 and FUN-46 on add and greet, so labels are needed everywhere. |
| O6 | A10 | 3 | Allows output. |
| O6 | A11 | 2 | Earlier members can mask or cause errors. |
| O6 | A12 | 1 | Unaddressed. |
| O6 | A13 | 3 | Neutral. |
| O6 | A14 | 2 | Session boundaries and redeclaration rules to maintain. |
| O7 | A1 | 3 | Same as O1, and the focus region lets the prose say 'look here' as a book would. |
| O7 | A2 | 5 | A whole program, honestly labelled. |
| O7 | A3 | 5 | Stands alone wherever it is opened. |
| O7 | A4 | 4 | The markers are plain // comments, legible on GitHub, and they point the eye past the context. They are noise only if forced onto 5-line blocks. |
| O7 | A5 | 5 | Pasting works, and the markers are harmless comments. |
| O7 | A6 | 5 | Closed, as in O1. |
| O7 | A7 | 5 | One hash covers everything. |
| O7 | A8 | 5 | Position-independent. |
| O7 | A9 | 5 | No join, and line= is unaffected. |
| O7 | A10 | 4 | Output block, as in O1. |
| O7 | A11 | 5 | Closed error examples. |
| O7 | A12 | 2 | Schemas are unaddressed. |
| O7 | A13 | 3 | Neutral. |
| O7 | A14 | 3 | O1's cost plus a text-checkable marker rule. |
| O8 | A1 | 3 | Neutral. Keeps general forms such as EXP-106 short next to a concrete instance. |
| O8 | A2 | 3 | A fourth honest label beats a schema mislabelled valid, but alone it leaves FUN-69 unclosed. |
| O8 | A3 | 4 | A form next to an instance is what a reference reader wants. |
| O8 | A4 | 4 | Schemas stay minimal. |
| O8 | A5 | 2 | An expect=syntax block does not run, and GitHub hides the label, so the prose must say 'this is a form'. |
| O8 | A6 | 2 | Alone it closes none of the 20. |
| O8 | A7 | 4 | Self-contained. |
| O8 | A8 | 4 | Only an adjacency check within the section. |
| O8 | A9 | 4 | No join. |
| O8 | A10 | 1 | By design it proves nothing about meaning or output. |
| O8 | A11 | 3 | Neutral. |
| O8 | A12 | 5 | Exactly the tool for EXP-28, EXP-106, LEX-23 and STA-12, and it keeps the grammar evidence for print_block and pair. |
| O8 | A13 | 3 | Neutral. |
| O8 | A14 | 4 | Cheap, and the hook can check it from the text. |

### Juez verification-first

Ranking: O7, O1, O8, O4, O3, O6, O5, O2

Veredicto: The axes that decide this for verification are A2 (Every example is complete valid or invalid code), A6 (Semantic closure without invention), A7 (Hermetic unit: one block, one hash, one verdict, one blame), A8 (Stability of the reference under reordering, insertion and across layers), A9 (Composability and determinism of the joined program) and A11 (Precision of negative examples). They are decisive because four consumers (the Lark grammar, the Lean semantics, the compiler and the acceptance tests) must reach the same verdict from the same bytes. Only the complete-program family (O1 and O7) scores 5 on all six.

Adopt O1 (Always a complete visible program) as the rule, which strengthens CEX-10 (The code). O7's (Complete program with a marked focus region) `// focus` markers are an optional readability aid: they are ordinary comments, so they cost the checkers nothing. Add O8's (Phase-graded expectations) `expect=syntax` only for genuine schemas, and the hook must require a concrete expect=valid sibling in the same section. Those schemas are EXP-28, EXP-106, LEX-23 and STA-12, and the grammar evidence at stake is print_block (STA-62) and pair (EXP-110, EXP-115).

The cost is about 60-90 visible lines over 418, plus 20 in-place edits that keep their IDs under R59/R60 (norms-versions, edited in place). Each edit is reviewed once. Copies that duplicate each other rot loudly, because each one is checked on its own.

FUN-69 becomes one closed file with FUN-66's three functions, and its six '// prints:' turn into a clean-language-output block. It then still waits on the separate number-to-text gap of STA-33. STA-37 declares age and finally tests SEM004 instead of SEM002.

The dependency options look attractive but fail the checkers:
- O2 (Fragments with implicit context from the sequence) resolves add in FUN-90 to FUN-46, the wrong provider, and its verdict depends on bytes outside the hash.
- O6 (Session per section or per labelled group) changes meaning when examples are reordered, which R13 (sections, files and bulleted lists are unordered) cannot see. Its default per-H2 session collides on add and greet.
- O5 (A standard prelude joined to every example) invents an unspecified fixture vocabulary (score, age, price, user), collides with local names in more than 10 examples, and one prelude edit invalidates all 67 fragments.
- O4 (Hidden context lines inside the block) is hermetic, but it adds a preprocessing layer that all four consumers must implement identically (strip, `##` escape, line= map). On GitHub it shows more noise than plain code.
- O3 (Explicit named dependency) is the only sound sharing mechanism, but it pays off for 2-4 of the 20 fragments: FUN-69 and FUN-90 certainly, STA-35 and STA-37 plausibly. It is not worth a merge semantics in the grammar, Lean, the compiler and the tests. Keep it in reserve for a future tutorial genre.

About 16 of the 20 undeclared-name fragments have no provider anywhere, so every option still needs new declarations for them. That fact alone makes closure-by-copy the cheapest deterministic rule.

Pesos: A1=1, A2=3, A3=2, A4=1, A5=2, A6=3, A7=3, A8=3, A9=3, A10=2, A11=3, A12=2, A13=2, A14=1

| Opción | Eje | Nota | Razón |
|---|---|---|---|
| O1 | A1 | 2 | FUN-69 repeats FUN-66's three functions instead of building on them, so there is no accumulation, though the prose can still say 'as declared above'. |
| O1 | A2 | 5 | expect=valid means a closed whole program, with no third state; STA-37 then really tests SEM004 (Constants). |
| O1 | A3 | 4 | It fits a normative reference opened at one rule by four consumers; it is weaker as a linear tutorial, and none exists yet. |
| O1 | A4 | 3 | About 60-90 extra visible lines (+15-20%) on GitHub, and FUN-69 grows from 6 to about 15 lines. |
| O1 | A5 | 5 | The bytes shown are exactly what Lean, the compiler and the acceptance tests run. |
| O1 | A6 | 5 | Every name is bound inside the block, so DSM-10 (the deriver makes no decision the norms do not make) is honoured and 'not declared' can only mean the author's error. |
| O1 | A7 | 5 | FUN-69@hash fully determines its verdict, and renaming greet in FUN-66 cannot leave FUN-69 silently stale. |
| O1 | A8 | 5 | Fully position-independent, so R13 (unordered sections) and CEX-23 (blocks may be moved or reordered) hold, and layer 1 needs no labels. |
| O1 | A9 | 5 | There is no join, so no FIL-54 (at most one start: per file) start: merge, no collisions on add/greet and no line= shift. |
| O1 | A10 | 4 | A closed start: makes FUN-69's six '// prints:' convertible to a checked output block; the number-to-text gap remains. |
| O1 | A11 | 5 | The undeclared-name SEM002 can no longer mask the expected code, as it does in STA-37. |
| O1 | A12 | 2 | Pushing EXP-28/EXP-106/LEX-23/STA-12 schemas to text loses grammar evidence of print_block and pair unless instances replace it. |
| O1 | A13 | 3 | It does not fix clock/stdin/libraries (TYP-189, FIL-70), but CEX-11 per-file examples give an explicit route. |
| O1 | A14 | 3 | 20 in-place edits (20 one-off reviews, same IDs), and duplicate copies rot loudly because each is checked. |
| O2 | A1 | 4 | It reads like a book (FUN-66 then FUN-69), but only 2-4 of the 20 have any provider to read from. |
| O2 | A2 | 1 | It institutionalises 'valid given context you cannot see', which is exactly the mixed signal CEX-4 (The opening line) must avoid. |
| O2 | A3 | 1 | A reference opened at FUN-69 alone is unintelligible to every consumer without replaying a lookup. |
| O2 | A4 | 5 | Zero scaffolding is shown. |
| O2 | A5 | 1 | Pasting FUN-69 or STA-35 alone fails; '25' for age is unreproducible. |
| O2 | A6 | 1 | Nearest-earlier lookup is inference the norms never state, and about 16 of the 20 still resolve to nothing. |
| O2 | A7 | 1 | The verdict depends on bytes outside the hash, and DSM-12 (only what a change calls for is derived again) cannot see provider changes. |
| O2 | A8 | 1 | FUN-90 resolves add to FUN-46 instead of FUN-28, and reordering changes meaning with no hash change under R13. |
| O2 | A9 | 2 | The join is defined only when sections do not collide, and greet has three signatures in FUN-66, FUN-97 and TYP-263. |
| O2 | A10 | 2 | An implicit context could run FUN-69, but its output depends on which provider the lookup picked. |
| O2 | A11 | 1 | An error example's code depends on what the lookup found, and on failure SEM002 masks SEM004. |
| O2 | A12 | 1 | Schemas stay mislabelled as runnable valid code. |
| O2 | A13 | 1 | External context stays unstated. |
| O2 | A14 | 3 | No migration, but the hook cannot check anything and edits rot silently. |
| O3 | A1 | 4 | An explicit uses= link keeps the FUN-66 to FUN-69 sequence readable. |
| O3 | A2 | 3 | The status is 'valid together with named providers': explicit, but no longer a single-file reading. |
| O3 | A3 | 3 | The reader sees uses=default-values and must jump to it; tools can follow it. |
| O3 | A4 | 4 | The consumer shows only its point. |
| O3 | A5 | 2 | Copying the consumer alone fails, and the checked program is a merge nobody sees. |
| O3 | A6 | 4 | Context is explicit and author-written, though it helps only FUN-69, FUN-90 and perhaps STA-35/STA-37. |
| O3 | A7 | 3 | ID@hash of providers is recorded and DSM-12 can re-derive, but the verdict spans several blocks and acceptance units fan out. |
| O3 | A8 | 4 | The label survives reordering and layer 1 can write it, but it needs a layer-2 resolution step and global label uniqueness. |
| O3 | A9 | 3 | The section merge is defined, but a within-section order rule, a provider ban on start: and collision checks must be specified in four consumers. |
| O3 | A10 | 4 | It lets FUN-69 run with an output block. |
| O3 | A11 | 4 | Line= stays in consumer coordinates, but a provider edit can introduce a new earlier error. |
| O3 | A12 | 2 | It does nothing for schemas. |
| O3 | A13 | 3 | It could name a fixture provider, but nothing normative exists to provide. |
| O3 | A14 | 3 | A new mechanism in the hook, the grammar, Lean, the compiler and the tests pays off for only 2-4 examples. |
| O4 | A1 | 2 | The context is repeated in each block, as in O1. |
| O4 | A2 | 4 | The checked program is whole and hermetic, but the shown and checked texts differ by a preprocessing step. |
| O4 | A3 | 3 | With no renderer, every reader sees '# '-prefixed code. |
| O4 | A4 | 2 | On GitHub the hidden lines show with a # prefix, so the result is noisier than O1's plain code. |
| O4 | A5 | 2 | A pasted block has # lines that are not Clean, and a rendered view would hide what runs. |
| O4 | A6 | 5 | Closure is written by the author inside the block. |
| O4 | A7 | 5 | The context sits inside own_text and its hash. |
| O4 | A8 | 5 | Position-independent. |
| O4 | A9 | 3 | The grammar, Lean, the compiler and the acceptance tests all need an identical strip rule, a ## escape and a line= mapping, which can diverge. |
| O4 | A10 | 4 | Output blocks become possible. |
| O4 | A11 | 4 | It is precise once the line coordinates are fixed, which is still an open rule. |
| O4 | A12 | 2 | It does nothing for schemas. |
| O4 | A13 | 3 | Neutral. |
| O4 | A14 | 2 | It adds a lexical layer to every consumer, and the CEX-10 (The code) amendment cannot be checked for closure at write time. |
| O5 | A1 | 3 | Names appear familiar, but they come from a hidden file, not from the sequence. |
| O5 | A2 | 2 | 'Valid given the prelude' is a global third state. |
| O5 | A3 | 2 | Each consumer must load an extra normative file that teaches nothing. |
| O5 | A4 | 4 | Blocks stay short. |
| O5 | A5 | 1 | No block reproduces alone. |
| O5 | A6 | 2 | The fixture vocabulary (score, age, price, user) is made-up language that no norm motivates, and stdlib is unspecified. |
| O5 | A7 | 1 | One prelude edit invalidates all 67 fragments and every acceptance unit. |
| O5 | A8 | 3 | Order-independent, but the prelude itself becomes a single point of meaning. |
| O5 | A9 | 1 | It collides with local x, value, price, age and others in more than 10 examples, and FUN-66, FUN-97 and TYP-263 need raw. |
| O5 | A10 | 3 | Runnable, but outputs depend on fixture values. |
| O5 | A11 | 2 | Prelude names can shadow or mask the intended error. |
| O5 | A12 | 1 | It does nothing for schemas. |
| O5 | A13 | 1 | It is a shared trusted base with no normative content; Wasm deprecated exactly this. |
| O5 | A14 | 2 | Every prelude diff becomes a corpus-wide review. |
| O6 | A1 | 5 | It directly models the doctest/SICP accumulation. |
| O6 | A2 | 2 | Example k is valid only given examples 1..k-1. |
| O6 | A3 | 2 | A reference read out of order breaks. |
| O6 | A4 | 4 | Blocks stay short. |
| O6 | A5 | 1 | No block reproduces alone. |
| O6 | A6 | 3 | The context is explicit by label, but covers only within-session names. |
| O6 | A7 | 2 | Hash k must chain over all earlier session hashes, so the fan-out is large. |
| O6 | A8 | 1 | Reordering inside a session changes meaning invisibly to R13, and the H2 default joins FUN-28, FUN-46 and FUN-66 and collides. |
| O6 | A9 | 2 | The cumulative merge collides on add and greet, so a fresh/session discipline is needed everywhere. |
| O6 | A10 | 3 | Runnable, but each verdict depends on its history. |
| O6 | A11 | 3 | An earlier session block can raise the first error. |
| O6 | A12 | 1 | It does nothing for schemas. |
| O6 | A13 | 2 | Session state is implicit shared context. |
| O6 | A14 | 2 | Every session edit forces a review of all later members, and no tool lists them. |
| O7 | A1 | 3 | Same as O1, but the focus region tells the reader where the lesson is. |
| O7 | A2 | 5 | A whole closed program; the markers are plain comments. |
| O7 | A3 | 4 | It serves the reference, and the focus aids a human reader opening one rule. |
| O7 | A4 | 4 | Scaffolding is visible but demarcated, and works on GitHub with no renderer. |
| O7 | A5 | 5 | The shown text equals the checked program, byte for byte. |
| O7 | A6 | 5 | Closed by the author. |
| O7 | A7 | 5 | Hermetic, one hash. |
| O7 | A8 | 5 | Position-independent. |
| O7 | A9 | 5 | No join, and comments shift no line= because they are counted like any line. |
| O7 | A10 | 4 | Same as O1. |
| O7 | A11 | 5 | Same as O1. |
| O7 | A12 | 2 | Same as O1. |
| O7 | A13 | 3 | Same as O1. |
| O7 | A14 | 3 | O1's cost plus pairing checks the hook can verify, though nothing verifies that the prose matches the region. |
| O8 | A1 | 2 | Neutral to pedagogy; it serves the form being taught. |
| O8 | A2 | 4 | It makes the phase status explicit instead of falsely claiming valid, but adds a fourth state that must not become a dumping ground. |
| O8 | A3 | 4 | It suits a normative grammar reference. |
| O8 | A4 | 4 | Schemas stay short. |
| O8 | A5 | 3 | It honestly claims only 'parses', which the reader can reproduce. |
| O8 | A6 | 3 | It removes the closure requirement legitimately for schemas, but closes none of the 20 runnable fragments. |
| O8 | A7 | 5 | Hermetic parse verdict. |
| O8 | A8 | 5 | Position-independent, apart from the 'concrete sibling in the same section' hook rule. |
| O8 | A9 | 5 | No join. |
| O8 | A10 | 1 | It proves only that the code parses; used for FUN-69 it would bury six unchecked claims. |
| O8 | A11 | 3 | Not about errors, and expect=syntax-error already covers parse failures. |
| O8 | A12 | 5 | It keeps grammar evidence for print_block (STA-62) and pair (EXP-110, EXP-115) without forcing EXP-28, EXP-106, LEX-23 or STA-12 to run. |
| O8 | A13 | 3 | Neutral. |
| O8 | A14 | 4 | A small hook and generator change; the risk is authors choosing it to escape closure. |

### Juez maintenance-first

Ranking: O1, O7, O8, O4, O3, O2, O6, O5

Veredicto: For the people who write and approve the spec for years, the decisive axes are A6 (Semantic closure without invention), A7 (Hermetic unit), A8 (Stability under reordering) and A14 (Authoring, review and migration cost), and they all point to O1 (Always a complete visible program). The verdict for FUN-69 then lives in its own bytes and hash. Reordering or inserting examples changes nothing, as R13 (unordered sections) and CEX-23 (reordering refuses nothing) require. The approver judges a diff by reading one block. Migration is 20 in-place 'edited' reviews under R59/R60 with stable IDs, about 60-90 lines in all.

Duplication is the price, but it fails loudly: each copy of add or greet is checked on its own. Implicit context fails silently instead; renaming greet in FUN-66 leaves FUN-69@4f2e41f3 stale.

Concretely:
- FUN-69 absorbs FUN-66's three functions and gains a 6-line output block. Better still, FUN-66 and FUN-69 merge into one example under the default-values heading, which removes the duplicate.
- STA-37 declares age, so it fails with SEM004 only.
- The ~16 orphans (score, username, age, price, user, req...) get local declarations, because no other option has a provider for them.

O1 should be paired with O8 (Phase-graded expectations), restricted to the 4 real schemas (EXP-28, EXP-106, LEX-23, STA-12). It keeps the grammar evidence of print_block and pair at little cost, but only if 'next to an instance' means the same section, not adjacency.

The other options:
- O7 (Complete program with a marked focus region) is O1 plus marker churn for a renderer that does not exist. The prose can name the focus for free, so skip it.
- O3 (Explicit named dependency, uses=) is the best dependency design, but its full machinery (syntax, hook, label resolution, status field, acceptance-unit citations, DSM-12 wiring) pays off for only 2-4 of the 20 fragments. Defer it until a real tutorial exists.
- O4 (Hidden context lines) is a trap on GitHub: the `# ` lines show up and are not Clean, and every consumer (grammar, semantics, hook, acceptance harness, compiler test runner) must strip them and map lines.
- O2 (Implicit context from the sequence), O6 (Session per section) and O5 (Standard prelude) break determinism. O2 picks FUN-46 instead of FUN-28 for FUN-90, O6 is order-sensitive in a way R13 cannot see, and O5's prelude is invented language: one edit invalidates all 67 fragments.

The user's axis a (pedagogy of a sequence) is real, but it belongs to a future tutorial, not to normative examples.

Pesos: A1=1, A2=2, A3=2, A4=1, A5=2, A6=3, A7=3, A8=3, A9=2, A10=2, A11=2, A12=2, A13=2, A14=3

| Opción | Eje | Nota | Razón |
|---|---|---|---|
| O1 | A1 | 2 | FUN-69 repeats FUN-66's three functions instead of building on them, so the sequence teaches nothing new, though the prose can still say 'as above'. |
| O1 | A2 | 5 | expect=valid means exactly 'this file, read alone, is a correct program', with no third state. |
| O1 | A3 | 5 | A spec author or generator can open any rule, such as STA-37, and understand it without reading the sections before it. |
| O1 | A4 | 3 | It adds about 60-90 visible lines (+15-20%) on GitHub, which is real scaffolding but small next to a median of 5 lines. |
| O1 | A5 | 5 | The bytes a reader copies are the bytes the Lean semantics and the acceptance tests run. |
| O1 | A6 | 5 | The layer-1 author writes every declaration, so DSM-10 (the deriver makes no decision the norms do not make) is satisfied and the 20 'does not declare' pendings close, apart from prose gaps such as number-to-text. |
| O1 | A7 | 5 | FUN-69@hash alone decides FUN-69's verdict, and renaming greet in FUN-66 cannot leave it silently stale. |
| O1 | A8 | 5 | Nothing depends on position, so it is fully compatible with R13 (unordered sections) and CEX-23 (reordering refuses nothing). |
| O1 | A9 | 5 | There is no join, so there are no section collisions, no rule for concatenating start: bodies, and no line map for line=. |
| O1 | A10 | 4 | It turns the six '// prints:' of FUN-69 into a checked output block, though nondeterministic cases such as TYP-189 stay comments. |
| O1 | A11 | 5 | STA-37 declares age itself, so SEM002 disappears and only the SEM004 it expects can fire. |
| O1 | A12 | 3 | Schemas such as EXP-106 and LEX-23 go to text and lose their own grammar evidence; the paired concrete instance keeps print_block and pair covered, but that costs extra examples. |
| O1 | A13 | 4 | It adds no shared trusted base, and FIL-70 can use the existing one-example-per-file `// file:` rule (CEX-11), though host facts such as the clock and stdin stay open. |
| O1 | A14 | 4 | It costs 20 in-place 'edited' reviews under R59/R60 with stable IDs, and every diff is judged in one block; copies such as add x3 can drift, but each copy is checked, so drift shows up. |
| O2 | A1 | 4 | It reads like a book for the one clean pair, FUN-66 -> FUN-69, but only 2-4 of the 20 have any provider, so the sequence teaches little. |
| O2 | A2 | 1 | It makes 'valid given context you cannot see' the rule, which is exactly the mixed signal CEX-4 exists to prevent. |
| O2 | A3 | 1 | A reference opened at FUN-90 cannot tell which earlier example supplies add. |
| O2 | A4 | 5 | It adds no scaffolding at all. |
| O2 | A5 | 1 | Copying FUN-69 or STA-35 gives a program that does not compile, and the checked program is not the one shown. |
| O2 | A6 | 2 | The checker resolves names by a heuristic lookup that layer 1 never wrote down, and for FUN-90 it picks FUN-46 instead of FUN-28: that is invention. |
| O2 | A7 | 1 | FUN-69@4f2e41f3 stays unchanged when FUN-66 changes, so its verdict goes stale silently unless the lookup is recomputed on every run. |
| O2 | A8 | 1 | Inserting a closer declarer of add or greet changes which provider is picked, with no change of hash, contradicting R13. |
| O2 | A9 | 2 | The join is defined only when the heuristic picks a provider without start: and with no collision, and the add and greet redeclarations make it ambiguous. |
| O2 | A10 | 2 | It adds no oracle, and the declaration-only providers are exercised only by accident. |
| O2 | A11 | 1 | STA-37's plausible provider STA-33 has a start:, so the rule excludes it and SEM002 still masks SEM004. |
| O2 | A12 | 1 | Schemas with metavariables stay pending forever, since no example declares arg1. |
| O2 | A13 | 2 | An unbounded implicit context is the worst kind of shared base: unversioned and with no opt-out. |
| O2 | A14 | 2 | It writes nothing today but rots silently, the hook cannot catch a missing provider at write time, and a reviewer cannot judge a diff to FUN-66 without hunting its consumers. |
| O3 | A1 | 4 | It keeps the FUN-66 -> FUN-69 sequence and makes it explicit with uses=default-values. |
| O3 | A2 | 3 | The status is declared honestly, but FUN-69 alone is still not a whole program: a third state, signalled but real. |
| O3 | A3 | 3 | A reference reader must chase a label to a block that may sit in another section or file. |
| O3 | A4 | 5 | Each block shows only its own point. |
| O3 | A5 | 2 | Copying FUN-69 fails; the reader must assemble the program by hand following the merge rule. |
| O3 | A6 | 3 | It is explicit and author-written, so DSM-10 holds, but only 2-4 of the 20 have providers; the other ~16 need new declarations anyway, as new provider blocks with new IDs. |
| O3 | A7 | 3 | Recording uses FUN-66@hash in the status line and reusing DSM-12 works, but the verdict no longer lives in the block's own bytes, and every provider fans out to its dependents. |
| O3 | A8 | 4 | The label survives reordering, but it needs repo-wide label uniqueness and a new resolution from layer 1 to layer 2 (label to ID@hash). |
| O3 | A9 | 3 | The merge is well defined only for providers with no start:, so STA-35 and STA-37 cannot use STA-33, and duplicate names become violations to police. |
| O3 | A10 | 4 | FUN-66 becomes exercised through FUN-69's output block. |
| O3 | A11 | 3 | It cannot fix STA-37, whose plausible provider has a start:, so STA-37 still has to declare age itself. |
| O3 | A12 | 2 | It does nothing for EXP-28, EXP-106, LEX-23 or STA-12. |
| O3 | A13 | 3 | Bounded and explicit, but each provider is a mini-fixture whose correctness its dependents trust. |
| O3 | A14 | 2 | It needs new info-string syntax, hook rules, label resolution, a status field, acceptance-unit citations of providers and DSM-12 wiring, all for 2-4 fragments; a provider diff needs every dependent rechecked, and no tool lists them. |
| O4 | A1 | 3 | With a renderer it hides the repetition; on GitHub it shows the same repetition as O1 plus noise. |
| O4 | A2 | 3 | The block holds a whole program, but what is shown (with `#`) is not Clean code, so 'valid' describes a transformed text. |
| O4 | A3 | 3 | The context is local, but a reader must mentally strip the markers. |
| O4 | A4 | 2 | In the real medium, GitHub, the hidden lines show with `# ` prefixes and look worse than O1's plain lines; the benefit needs a renderer that does not exist. |
| O4 | A5 | 2 | Copying from GitHub gives `#` lines that do not compile, and with a renderer the shown code differs from the checked code. |
| O4 | A6 | 5 | The author writes all the context, so DSM-10 holds. |
| O4 | A7 | 5 | The context is inside own_text, so one hash decides the verdict. |
| O4 | A8 | 5 | It does not depend on position. |
| O4 | A9 | 3 | line= must be redefined against the full program, `# \t` interacts with tab indentation, and CEX-10 must treat `# section:` as a section line, which are three new rules to get right. |
| O4 | A10 | 4 | Same as O1: the output blocks become checkable. |
| O4 | A11 | 5 | STA-37 can carry `# state:` with age and fail only with SEM004. |
| O4 | A12 | 2 | It does not address schemas. |
| O4 | A13 | 4 | It has no shared base. |
| O4 | A14 | 2 | The grammar generator, the semantics, the hook, the acceptance harness and the future compiler test runner all have to strip markers and map lines, a permanent tax with no renderer to repay it. |
| O5 | A1 | 3 | A shared fixture vocabulary (score, age, user) feels familiar, but nobody learns where it comes from. |
| O5 | A2 | 2 | Every example is 'valid given an invisible file'. |
| O5 | A3 | 2 | The reference reader must know the prelude exists and read it. |
| O5 | A4 | 5 | It adds no visible scaffolding. |
| O5 | A5 | 1 | A pasted STA-35 fails unless the reader also finds example-prelude.md. |
| O5 | A6 | 2 | The prelude is invented fixture language (age = 25, price = 19.99) that no norm motivates, and the stdlib it would stub is 'not specified yet'. |
| O5 | A7 | 1 | One prelude edit invalidates all 67 fragments and every acceptance unit. |
| O5 | A8 | 4 | It does not depend on position. |
| O5 | A9 | 1 | It collides with local x, value, price, age and others in more than 10 examples, and FUN-66, FUN-97 and TYP-263 must all say raw. |
| O5 | A10 | 3 | Neutral: output blocks are possible, but a prelude that printed would break every one of them. |
| O5 | A11 | 2 | Prelude names can shadow or collide, so they create new errors that come before the declared one. |
| O5 | A12 | 2 | Declaring arg1 or functionName in the prelude would be absurd. |
| O5 | A13 | 1 | It is a large, unspecified trusted base, the pattern Wasm deprecated with spectest. |
| O5 | A14 | 1 | Every prelude diff is a review of the whole corpus, and migration creates a new node that every dependent must cite. |
| O6 | A1 | 5 | It is closest to how a book accumulates context. |
| O6 | A2 | 2 | The status depends on everything earlier in the session. |
| O6 | A3 | 2 | A reader who opens the reference at example k must read examples 1..k-1. |
| O6 | A4 | 5 | It adds no scaffolding. |
| O6 | A5 | 1 | Copying one block never reproduces the program that is checked. |
| O6 | A6 | 3 | It is author-labelled, but FUN-90 -> FUN-28 crosses top-level sections, and the H2 default joins unrelated examples. |
| O6 | A7 | 2 | The hash of example k must cover all earlier hashes, so edits cascade down the session. |
| O6 | A8 | 1 | Reordering inside a session changes meaning, and R13 cannot see it. |
| O6 | A9 | 2 | With the H2 default, FUN-28, FUN-46 and FUN-66 collide on add and greet. |
| O6 | A10 | 4 | Earlier declarations get exercised later. |
| O6 | A11 | 3 | STA-37 could get age from a session, but only from a declaration section, not from STA-33's start:. |
| O6 | A12 | 1 | It does not address schemas. |
| O6 | A13 | 3 | The context is bounded per session, but the hidden state is implicit, the Jupyter failure mode. |
| O6 | A14 | 1 | It brings order-sensitive cascading reviews, new hash composition and the most new machinery of any option. |
| O7 | A1 | 2 | Same as O1: there is no reuse. |
| O7 | A2 | 5 | Each example is a whole program, as in O1. |
| O7 | A3 | 5 | Each example is self-contained, as in O1. |
| O7 | A4 | 3 | The markers point the eye at the focus, but they add two lines, and GitHub folds nothing. |
| O7 | A5 | 5 | The markers are ordinary comments, so the shown code is the checked code. |
| O7 | A6 | 5 | Same as O1. |
| O7 | A7 | 5 | One hash decides the verdict, although moving a marker alone changes the hash and triggers a review. |
| O7 | A8 | 5 | It does not depend on position. |
| O7 | A9 | 5 | There is no join. |
| O7 | A10 | 4 | Same as O1. |
| O7 | A11 | 5 | Same as O1. |
| O7 | A12 | 3 | Same as O1. |
| O7 | A13 | 4 | Same as O1. |
| O7 | A14 | 3 | It costs what O1 costs plus a hook rule and churn from cosmetic marker edits, for a fold that no renderer performs today; the prose can name the focus for free. |
| O8 | A1 | 2 | It is mostly irrelevant to learning through a sequence. |
| O8 | A2 | 3 | It names the parse-only state honestly instead of mislabelling EXP-106 as valid, but on its own it leaves the running examples unsolved. |
| O8 | A3 | 4 | Showing forms is what normative references do (the Haskell Report's holes, Go's EBNF). |
| O8 | A4 | 4 | Schemas stay compact. |
| O8 | A5 | 3 | It is honest about being unrunnable, so no false promise is made. |
| O8 | A6 | 2 | It closes nothing; it only legitimately exempts the 4 schemas from closure. |
| O8 | A7 | 5 | One block's own bytes decide the parse verdict. |
| O8 | A8 | 4 | The 'next to a concrete instance' rule must mean the same section, not adjacency, to respect R13. |
| O8 | A9 | 4 | There is no join. |
| O8 | A10 | 1 | A pass proves only that the code parses. |
| O8 | A11 | 3 | Neutral. |
| O8 | A12 | 5 | It keeps the grammar evidence of print_block, pair and line continuation without inventing values for arg1..arg3. |
| O8 | A13 | 3 | Neutral. |
| O8 | A14 | 4 | It is one new expectation value, a hook rule and a semantics skip, and it avoids rewriting EXP-28, EXP-106, LEX-23 and STA-12 as text with twins; the risk is that it becomes an 'ignore' dump, which the instance rule limits. |

## 6. Informe antes de la crítica

## ¿Cada ejemplo de Clean debe ser un programa completo?

### 1. La pregunta

¿Cada ejemplo `expect=valid` o `expect=error` tiene que ser, leído solo, un programa de Clean completo, o puede ser un fragmento que se entiende por la secuencia y el contexto?

**Respuesta corta: sí, programa completo.** Los dos ejes que propusiste no pesan lo mismo. El (b), código siempre válido o inválido, se mantiene. El (a), la pedagogía de secuencia, es real, pero le toca a un tutorial, no a ejemplos normativos.

### 2. Los ejes que importan

Estos son los 8 ejes que deciden. Los tres jueces les dieron el peso más alto en conjunto.

1. **Etiqueta honesta:** ¿`expect=valid` o `expect=error` describe el bloque tal como se ve, sin un tercer estado del tipo "válido con un contexto que no ves"? Es tu eje (b).
2. **Fidelidad:** si alguien copia el bloque y lo ejecuta, ¿obtiene lo que dice el texto, y es el mismo programa que corren la semántica y los tests?
3. **Cierre sin inventar:** ¿cada nombre está declarado en el bloque, de modo que ningún generador tiene que inventar declaraciones? Lo exige DSM-10 (the deriver makes no decision that the norms do not make).
4. **Unidad hermética:** ¿todo lo que decide el veredicto está en los bytes de su hash? Si no, cambiar otro ejemplo deja este desactualizado sin aviso.
5. **Estabilidad al reordenar:** ¿el sentido de un ejemplo sobrevive si se mueven o se insertan ejemplos? R13 (sections, files and bulleted lists are unordered) no ve el orden.
6. **Precisión de los errores:** ¿un ejemplo de error falla solo por la razón que declara?
7. **Referencia leída fuera de orden:** ¿se entiende el ejemplo cuando se abre directamente en esa regla? Así leen los generadores, los tests y la mayoría de las personas.
8. **Unión bien definida:** si se junta contexto con el ejemplo, ¿sale un archivo único, sin choques de nombres, con un solo `start:` y con `line=` intacto?

Estos ejes deciden poco, porque no separan las opciones o porque afectan a pocos ejemplos:

- **Pedagogía de secuencia (tu eje a):** solo 2 a 4 de los 20 fragmentos tienen un ejemplo anterior que les dé los nombres.
- **Andamiaje visible:** completar los ejemplos agrega entre 60 y 90 líneas a las 418 actuales, un 15–20 % más.
- **Oráculo de salida:** todas las opciones cerradas lo permiten por igual.
- **Esquemas con metavariables:** son solo 4 casos.
- **Reloj, stdin y librerías:** ningún formato de ejemplo lo resuelve.
- **Costo de autoría:** es parecido entre las opciones serias.

### 3. Matriz de decisión

Media de los tres jueces, de 1 a 5. La columna "Media" promedia los 8 ejes de la sección 2. Las dos últimas columnas se muestran como contraste: son los ejes donde ganan las opciones perdedoras.

| Opción | Etiqueta | Fidelidad | Sin inventar | Hermética | Estabilidad | Errores | Referencia | Unión | **Media** | Secuencia | Brevedad |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Programa completo | 5 | 5 | 5 | 5 | 5 | 5 | 4,7 | 5 | **5,0** | 2,3 | 3,0 |
| Completo con marcas de foco | 5 | 5 | 5 | 5 | 5 | 5 | 4,7 | 5 | **5,0** | 2,7 | 3,7 |
| Líneas ocultas (`# `) | 3,7 | 1,7 | 5 | 5 | 5 | 4,3 | 3,0 | 3,0 | **3,8** | 2,3 | 2,0 |
| Nivel solo sintaxis* | 3,3 | 2,7 | 2,3 | 4,7 | 4,3 | 3,0 | 4,0 | 4,3 | **3,6** | 2,3 | 4,0 |
| Dependencia explícita `uses=` | 3,3 | 2,0 | 3,7 | 3,0 | 4,0 | 3,3 | 2,7 | 3,0 | **3,1** | 4,0 | 4,7 |
| Sesión por sección | 2,0 | 1,0 | 3,0 | 1,7 | 1,0 | 2,7 | 2,0 | 2,0 | **1,9** | 4,7 | 4,7 |
| Preludio estándar | 2,0 | 1,0 | 2,3 | 1,0 | 3,3 | 2,0 | 2,0 | 1,0 | **1,8** | 2,7 | 4,7 |
| Contexto implícito de la secuencia (hoy) | 1,0 | 1,0 | 1,7 | 1,0 | 1,0 | 1,0 | 1,0 | 2,0 | **1,2** | 3,7 | 5,0 |

\* El nivel solo sintaxis no es una alternativa: complementa a las otras opciones y solo sirve para esquemas.

**Dónde no coinciden los jueces:**

- **Marcas de foco.** Los jueces de pedagogía y de verificabilidad las ponen primeras. El de mantenimiento propone no usarlas: hoy ningún visor pliega el código y la prosa puede señalar el foco gratis.
- **Cuarto puesto.** El juez de pedagogía prefiere `uses=`. Los otros dos prefieren las líneas ocultas.
- Los tres coinciden en el podio (completo, completo con foco, solo sintaxis) y en los tres últimos puestos.

### 4. Recomendación

**Cada ejemplo `expect=valid` o `expect=error` es un programa completo y visible**, sin unión, sin envoltorio y sin preludio. Se le injerta el **nivel `expect=syntax`**, limitado a los 4 esquemas con metavariables y siempre junto a un ejemplo concreto de la misma sección.

**Por qué.** Es la única familia de opciones que saca 5 en los 8 ejes decisivos. Los mecanismos de dependencia tienen un problema común: su etiqueta no se ve en GitHub, que solo muestra la primera palabra del bloque. El lector ve exactamente los fragmentos rotos de hoy, y la mejora solo alcanza a 2–4 de los 20 casos.

**El costo, dicho llano:**

- **Duplicación.** FUN-69 (Usage Examples) repite las tres funciones de FUN-66 (Function Parameter Default Values), y los ejemplos crecen un 15–20 %.
- **Pérdida de secuencia.** Se pierde la sensación de libro que acumula lo anterior.
- **Por qué compensa.** Las copias fallan en voz alta, porque cada una se comprueba por separado. El contexto implícito, en cambio, se pudre en silencio: si se renombra `greet` en FUN-66 (Function Parameter Default Values), FUN-69 (Usage Examples) queda obsoleto sin ningún aviso.

### 5. Efecto concreto en Clean

**FUN-66 y FUN-69.** FUN-69 (Usage Examples) pasa a ser un solo archivo con las tres funciones de FUN-66 (Function Parameter Default Values). Sus seis comentarios `// prints:` se convierten en un bloque de salida comprobado:

```clean-language expect=valid
functions:
	string greet(string name = "World")
		return "Hello, " + name
	string formatPrice(number amount, string currency = "USD")
		return currency + " " + amount.toString()
	void logMessage(string message, string level = "INFO")
		print("[" + level + "] " + message)

start:
	print(greet())
	print(greet("Alice"))
	...
```

Hay dos variantes: FUN-66 (Function Parameter Default Values) sigue como vista solo de declaraciones, o los dos ejemplos se funden en uno.

**Los 20 fragmentos pendientes por nombres no declarados:**

- **4 esquemas pasan a `expect=syntax`:** EXP-28 (Multi-Line Expressions), EXP-106 (Function Calls), LEX-23 (Spaces within expressions are permitted for readability) y STA-12 (Assignment). Salen de la semántica y conservan su evidencia para la gramática.
- **Hasta 14 se vuelven derivables** una vez que el autor de capa 1 les escribe declaraciones locales. Entre ellos están FUN-90 (Function Call Syntax), que copia `add` de FUN-28 (Functions Blocks (Required)), y STA-37 (Printing Values of Any Type), que por fin falla con el SEM004 que declara y no con SEM002.
- **Siguen esperando una decisión de capa 1:**
  - FUN-69 (Usage Examples) y STA-35 (Printing Values of Any Type) quedan cerrados, pero chocan con el hueco de la conversión de número a texto, el mismo que tiene pendiente a STA-33 (Printing Values of Any Type).
  - EXP-115 (Pairs Literals), TYP-442 (Type Conversion) y FUN-102 (Background Functions) usan `Request`, `req` y un servidor: hay que elegir entre declararlos como stubs locales o esperar a que se especifique la librería.
- Los otros 12–13 pendientes son huecos de la prosa que ningún formato arregla.

**Reglas de ejemplos (CEX):**

- **CEX-10 (The code)** se endurece: el ejemplo, leído solo, declara todo lo que usa, salvo lo que define una norma del lenguaje o una librería especificada.
- **CEX-5 (The opening line)** cierra su pregunta abierta 1: no hay contexto de construcción fuera del bloque.
- **La sección The opening line** suma `expect=syntax`, con la regla de que vaya junto a un ejemplo concreto.
- **CEX-30 (The expected output):** los `// prints:` deterministas pasan a bloques de salida.

**Generadores:**

- **Gramática:** acepta `expect=syntax` como evidencia.
- **Semántica:** salta los ejemplos `expect=syntax` y reporta "ejemplo no cerrado" como defecto del ejemplo, no como hueco de la prosa.
- **Tests de aceptación:** corren cada bloque tal cual.

### 6. Decisiones que te tocan

1. ¿Adoptas la regla "programa completo" más `expect=syntax` solo para esquemas?
2. ¿Quieres las marcas `// focus` … `// end focus` como ayuda opcional para el lector, o prefieres que la prosa señale el foco? En esto los jueces no coinciden.
3. Para `Request`, `req` y el servidor de EXP-115 (Pairs Literals), TYP-442 (Type Conversion) y FUN-102 (Background Functions): ¿se declaran como stubs dentro de cada ejemplo, o esperan a que se especifique la librería del servidor?

## 7. Crítica de completitud

- Three of the four so-called 'schemas with metavariables' are not schemas. EXP-28 (Multi-Line Expressions) uses total, price, tax, shipping and handling. STA-12 (Assignment) is `x = 42`, `arr[0] = value` and `obj.property = val`. LEX-23 (Spaces within expressions are permitted for readability) is `value  = x + y`. Each of them can be closed with a few declarations. Only EXP-106 (Function Calls), with functionName and arg1..arg3, is a real form, and even it could be closed with a function that has default parameters. — Moving them to expect=syntax throws away semantic evidence that axis A12 lists as a loss: line continuation in EXP-28 and assignment in STA-12. Without these cases, the justification for adding a fourth expectation form is about one example. The recommendation could close all four as valid programs, or keep expect=syntax for EXP-106 only. That avoids changing the complete list in CEX-4 (The opening line), the hook rules in CEX-20 (What is checked, and by whom) and the generators. (cambia la recomendación: sí)
- Multi-file programs. CEX-11 (The code) already says that 'an example of several source files is written as one Clean example per file' (`// file:`). FIL-70 imports app/utils.cln and app/mathHelpers.cln. Under the recommended rule ('the example, read alone, declares everything it uses; no join'), an import example can never be expect=valid. Joining several file examples into one program is itself a dependency between examples, and none of the options designs that unit. — 'Complete program' has to mean 'complete program, possibly made of several files declared together'. That needs an explicit grouping (a program label shared by its file examples, much like O3's name=/uses= limited to files) and a rule for how the checker builds it. Otherwise the import and libraries rules can have no checked example. As written, 'sin unión' (no join) contradicts CEX-11. (cambia la recomendación: sí)
- Scaffolding blast radius, as an axis. A complete program pulls in other norms through its scaffolding, and a gap in any of them blocks the evidence for the norm the example illustrates. FUN-69 (Usage Examples) gets stuck on the number-to-text gap only because of formatPrice's amount.toString(). LEX-150 (messages.length()) runs into the same length() typing gap that keeps FUN-42 pending. EXP-91 (the ! assertion) needs stubs that return an optional, and the value the stub returns decides whether the program halts. EXP-83 (default chains) needs a class with optional fields, so it may run into the constructor gap of STA-51. — The report needs an authoring rule: scaffolding uses only constructs that are already specified and derived, with the smallest declarations possible, and the author picks the stub values (and their output) as part of the example. Without that rule, the 'derivable once closed' estimate is too high, and closing examples can trade a missing-name gap for a prose gap. (cambia la recomendación: no)
- Closing names with parameters is a lighter variant that was not designed. Free variables become parameters of a function (for example `void check(integer score)` around the STA-9 body). This gives every name a type without inventing values, much like Lean `variable`, which A6 already cites. The example type-checks but does not run. — It keeps fragments short for examples about typing or flow (STA-9, STA-62, STA-64, EXP-68), which costs less than inventing values plus a start:. The trade-off is a weaker oracle: the example type-checks but nothing runs. It refines O1 rather than replacing it. (cambia la recomendación: no)
- The argument that GitHub hides the label applies to every option, the recommended one included. GitHub never displays the info string. It uses only the first word, for syntax highlighting, and `clean-language` is not a language GitHub highlights anyway. So expect=error, expect=syntax-error and the proposed expect=syntax are as invisible to a GitHub reader as uses= would be. — The 'honest label' axis (the expect= label describes the block as shown) does not tell the options apart for a rendered reader. A visible status signal is missing from every option, for example the prose saying 'this program fails with X' or 'This program prints:', in the spirit of the Rust Book's Ferris icons and the JLS. It should be added as a rule, and the argument against uses= has to rest on the other axes. (cambia la recomendación: no)
- The user's axis (a), pedagogy of a sequence, is deferred to 'a tutorial' without saying where such a tutorial lives or whether its examples would be checked. No tutorial exists, and the CEX rules apply to every spec file. — If a learner-facing book is ever written in Clean, it will need a sequence mechanism (O6 sessions or O3 uses=) that is checked separately, or its examples will rot. The report should say the strict rule covers normative specs only, and name where book-style examples would go. (cambia la recomendación: no)
- Merging FUN-66 (Function Parameter Default Values) into FUN-69 (Usage Examples) changes the norm tree: it removes FUN-66's code_block, and the IDs, acceptance units and citations of the norms involved have to follow. The cost under R59/R60 (edits in place keep the example's ID) is counted for edits in place but not for a merge. — It is a small migration cost that the 'Hay dos variantes' (two variants) choice should state. (cambia la recomendación: no)

Errores:
- The breakdown of the 20 'does not declare' fragments does not add up. 4 schemas + 'hasta 14' (up to 14) derivable + 5 still waiting (FUN-69, STA-35, EXP-115, TYP-442, FUN-102) + 12-13 prose gaps = 35-36, but only 33 fragments are pending. After the 4 schemas and the 5 waiting fragments, at most 11 remain (FUN-60, FUN-90, EXP-68, EXP-83, EXP-91, EXP-110, LEX-150, STA-9, STA-37, STA-62, STA-64), so 'up to 14' cannot be right.
- FUN-60 is among the 20 'does not declare' fragments, but its reason is that the after: block reads result 'as Contracts are not specified yet'. That is a prose gap no declaration can fix, so the real ceiling is about 10. Since LEX-150, EXP-91 and EXP-83 may also run into other gaps (see 'missing'), a realistic count is about 6-8.
- FUN-102 (Background Functions) is misdescribed as using Request, req and a server. It only calls sendUpdateToServer() inside `void syncCache() background`. A one-line local stub would close it, but background semantics links to 'Asynchronous Programming (not specified yet)', so it is blocked by a prose gap, not by the server library.
- FUN-90 (Function Call Syntax) is said to copy 'add' from FUN-28 (Functions Blocks (Required)). It calls add, multiply, square and printMessage, and FUN-28 declares all four, so it copies four declarations, not one.
- The report says the three judges agree on the podium (complete program, complete with focus marks, syntax-only level). The matrix puts hidden lines (3.8) ahead of syntax-only (3.6), and the report itself says syntax-only is not an alternative. It also says the maintenance judge proposes not using focus marks, which conflicts with that judge putting O7 on the podium.
- 'GitHub solo muestra la primera palabra del bloque' (GitHub shows only the first word of the block) is wrong. GitHub displays no part of the info string; it only uses the first word to pick syntax highlighting.
- Minor count drift (checked against specs-repo-annotated): I count 63 expect=valid Clean examples (the axes say 64), 45 '// prints:'/'// result:' comments in 17 examples (the axes say 44 in 16-17) and 82 section lines (the axes say 81). The grammar status lists 71 fragments, while I parse 70 Clean examples. These differences do not affect the conclusions.
- Checked and correct: 67 semantic fragments with 34 derived and 33 pending; 20 reasons that say 'does not declare'; STA-37 expects SEM004 but gives SEM002; 9 output blocks; 44 text blocks; 4 syntax-error examples with line=; 3 expect=error examples; 39 start:-only valid examples.
