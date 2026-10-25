# Insights: alcance, "terminado" y orden de implementación

Síntesis de [investigacion-spec-driven-development.md](investigacion-spec-driven-development.md) (inv.), [spec-dimensions.md](spec-dimensions.md) y [sdd-document-types.md](sdd-document-types.md) (tipos). Fecha: 2026-10-25. Lo marcado **(inferencia)** no está en la investigación.

## 1. Alcance (scope)

- **En cada spec:** C1 (Purpose, scope and non-goals). La spec abre con para qué sirve y para quién, qué cubre, qué sistemas tiene alrededor, qué queda fuera y qué no debe pasar nunca. Cada exclusión va en su propia frase. Un agente toma el silencio como permiso; un non-goal le dice dónde parar.
- **En el producto:** PRD (tipos n.º 22, Product requirements document), con v1/v2 y lo que queda fuera; y roadmap (tipos n.º 37, Roadmap and work breakdown): MVP frente a lo posterior, épicas con "done-when" y lista de ideas postergadas.
- **En el código:** la spec de capacidad tiene "Fuera de alcance", "Targets" y "Fuera de targets" (inv. anexo A). Regla 1 (inv. §0): nada se implementa sin una cláusula con ID que lo pida; código o test sin cláusula es deriva.

## 2. Qué es "terminado" (inv. §6)

No es "compila y los tests pasan". Son tres cosas a la vez (6.1):

1. Cada cláusula afectada tiene evidencia vigente y trazada.
2. La evidencia la produjo o validó alguien independiente del agente que escribió el código.
3. La spec consolidada describe el comportamiento real (el delta está fusionado).

Capas (6.2): DoR de la spec (G1), DoD de tarea (G4), DoD de feature (G5 + G6), DoD de release (G7), mantenimiento (G8). La evidencia mínima depende del tipo de spec (6.3).

## 3. Cuándo una app está terminada (inv. 6.5, 6.8, 6.9)

- **Cobertura de spec = 100 % de las cláusulas MUST** de la versión, sin evidencia caducada, sin deuda de spec y con los NFR medidos en un entorno representativo. La cobertura de líneas solo sirve para encontrar huecos.
- Una matriz de trazabilidad generada en CI lo hace cumplir: MUST sin test en verde → falla; test sin cláusula → aviso; archivo sin spec dueña → falla.
- En mantenimiento, sigue "terminada" mientras spec, código y tests sigan consistentes.

## 4. Feature frente a capacidad (inv. 1.6, 3.12; tipos n.º 23)

La investigación no define "feature"; la usa como **unidad de trabajo**: algo que se pide, planifica y entrega.

| | Capacidad | Feature |
|---|---|---|
| Qué es | Área estable de negocio | Cambio sobre una o varias capacidades |
| Spec | Consolidada, permanente: unidad de verdad | Delta (ADDED/MODIFIED/REMOVED): unidad de trabajo |
| Vida | Mientras exista el sistema | Se fusiona en las capacidades y se archiva |

Done de feature: las cláusulas de su delta tienen evidencia. Done de proyecto: las tienen todas las cláusulas vigentes.

## 5. Cómo se navegan las specs para implementar

- **Contexto (3.11):** siempre la constitución, el glosario y el índice de cláusulas generado por CI (`spec/INDEX.md`); por tarea, solo las cláusulas que toca y las que estas referencian.
- **Estructura:** C13 (Navigable, bounded units): agrupar por tema, separar las reglas generales de las de cada feature, unidades que se puedan cargar enteras. C14 (Stable identifiers): ID permanente por cláusula; las cláusulas se citan por ID.
- **Unidades (3.12):** verdad = spec consolidada de capacidad; trabajo = delta; identidad = cláusula con ID; regeneración = archivo entero. Cada archivo tiene como mucho una spec dueña.

## 6. Proceso de implementación (inv. §4 y gates de §10)

1. Intención y carril: trivial, estándar o completo (G0, Intención y carril).
2. Spec como delta aprobado por un humano, con IDs y verificación por cláusula; ambigüedad → `[NEEDS CLARIFICATION]` y se para (G1, Definition of Ready de la spec).
3. Tests de aceptación derivados, aprobados y vistos en rojo; el implementador no los toca (G2, Tests de aceptación).
4. Plan técnico: stack, arquitectura, lo que ya existe (G3, Plan técnico).
5. Tareas con targets y un check ejecutable en rojo (G4, Tarea).
6. Bucle del agente por tarea: sesión limpia, solo las cláusulas tocadas, generar → ejecutar → corregir, una funcionalidad a la vez, evidencia y no afirmaciones, tope de intentos, decisiones en `decisions.log` aprobadas por un humano.
7. Verificación independiente: otro agente en contexto limpio y después un humano (delta primero, luego el diff).
8. Cierre de feature: evidencia en la matriz, suite sin regresión, delta fusionado (G5, DoD de feature; G6, Merge e integración).
9. Release: 100 % de las MUST con evidencia vigente y NFR medidos (G7, Release).

Ante una desalineación entre spec, código y tests se corrige primero la spec. Únicas excepciones: hotfix, refactor estructural, spike desechable, zona brownfield sin spec.

## 7. Sistemas sin "use cases": el caso del lenguaje (inv. 3.13)

| App de negocio | Lenguaje / compilador |
|---|---|
| Módulo / capacidad | Aspecto: léxico, sintaxis concreta, precedencia, AST, semántica estática y dinámica, orden de evaluación, errores |
| Use case | Construcción del lenguaje (cláusulas `SYN-`, `SEM-`) |
| Escenario de aceptación | Caso de conformidad: programa, veredicto, árbol y valor esperados |
| Dueño de archivo | Tabla de autoridad: un único dueño normativo por aspecto |

Orden que propone la investigación:

1. Ediciones: el lenguaje crece por subconjuntos (la edición 1, sin tipos).
2. Primero el contrato compartido (el AST), del que dependen parser, semántica e intérprete.
3. Escalones de formalización (3.13.5, Cuándo formalizar): E0 prosa + casos de conformidad, E1 gramática, E2 semántica ejecutable, E3 teoremas, E4 implementación verificada. Se sube solo cuando el anterior está estable.
4. Greenfield: walking skeleton y después la primera funcionalidad (inv. 8.8, 11).

## 8. Hueco: cómo definir cualquier sistema para tener un orden **(inferencia)**

La investigación no da una regla general. Propuesta: un sistema se define con

1. **Unidades de comportamiento** con verificación propia (use cases, construcciones del lenguaje, comandos...).
2. **Un grafo de dependencias** entre unidades y contratos compartidos (AST, modelo de datos).
3. **Incrementos** (MVP, ediciones) como conjuntos de unidades.

Orden: elegir el incremento y recorrer el grafo, contratos primero, luego unidades en rebanadas verticales (en un compilador, `+` atraviesa lexer, parser, AST e intérprete, en vez de terminar el lexer antes de empezar el parser). Lo guarda el roadmap (tipos n.º 37), con oleadas de dependencias.
