# Pensar con método

## 1. El problema

Cuando trabajamos con Claude, una misma conversación mezcla cosas muy distintas. Empezamos explorando un tema, aparecen varias opciones, elegimos una, y antes de implementarla ya estamos explorando otro tema. Después decidimos algo de ese segundo tema y empezamos a implementarlo. Al final no queda claro qué se decidió, qué fue solo una idea y qué quedó pendiente.

El problema no es pensar en muchas cosas, sino no saber en qué estamos en cada momento: si estamos generando ideas, eligiendo o ejecutando, y qué hacer con las ideas que aparecen por el camino.

## 2. Lo que dice la psicología

### Creatividad

En psicología, la **creatividad** es la capacidad de producir ideas que son a la vez nuevas y útiles para un fin (Runco y Jaeger, 2012). Una idea solo nueva es una ocurrencia; una idea solo útil ya existía.

Las teorías principales responden a preguntas distintas.

**¿Cómo se piensa al crear?**

- **J. P. Guilford** (1950) separó dos modos de pensar: el **divergente**, que genera muchas respuestas posibles, y el **convergente**, que busca la respuesta correcta. Mezclarlos perjudica a ambos: juzgar mientras se generan ideas las corta antes de tiempo. Su discurso de 1950 se considera el inicio del estudio científico de la creatividad.
- **Sarnoff Mednick** (1962), teoría asociativa: una idea creativa une conceptos que están lejos entre sí.
- **Finke, Ward y Smith** (1992), modelo Geneplore: crear alterna entre generar estructuras mentales en bruto y explorarlas para darles sentido.
- **Dean Keith Simonton**, a partir de Donald Campbell: la creatividad funciona como la evolución, con variación a ciegas y retención selectiva. Se producen muchas variantes y se quedan las que sirven.
- **Roger Beaty**, neurociencia: la red cerebral por defecto genera ideas espontáneas y la red ejecutiva las evalúa. En las personas creativas, las dos cooperan.

**¿En qué etapas ocurre?**

- **Graham Wallas** (1926): preparación, incubación, iluminación y verificación. La incubación es dejar el problema de lado para que madure.
- **Alex Osborn y Sidney Parnes**, *Creative Problem Solving*: cada etapa tiene una mitad divergente y otra convergente. Osborn inventó el *brainstorming* y propuso no juzgar mientras se generan ideas.

**¿Qué hace falta para crear?**

- **Teresa Amabile**, modelo componencial: hacen falta conocimiento del tema, hábitos de pensamiento creativo y, sobre todo, **motivación intrínseca** (hacer algo porque interesa, no por un premio). El entorno puede favorecerla o matarla.
- **Robert Sternberg y Todd Lubart**, teoría de la inversión: la persona creativa "compra barato y vende caro"; apuesta por ideas que nadie valora y las impone.
- **Mihaly Csikszentmihalyi**, modelo de sistemas: la creatividad no está solo en la persona. Hace falta un **dominio** (las reglas de un campo) y un **ámbito** (los expertos que deciden qué se acepta). También describió el **flujo**, el estado de concentración total.
- **Mel Rhodes** (1961), las **4 P**: persona, proceso, producto y entorno (*press*).

**¿Qué clases de creatividad hay?**

- **Margaret Boden**: creatividad **combinatoria** (unir ideas conocidas), **exploratoria** (recorrer un espacio de posibilidades) y **transformacional** (cambiar las reglas del espacio).
- **Kaufman y Beghetto**, las **4 C**: *mini-c* (nuevo para uno mismo), *little-c* (la de todos los días), *Pro-c* (la profesional) y *Big-C* (la que cambia un campo).

**¿Cómo se mide?**

- **E. Paul Torrance** creó los test de pensamiento creativo más usados. Miden **fluidez** (cantidad de ideas), **flexibilidad** (variedad de categorías), **originalidad** (rareza) y **elaboración** (detalle).

### Innovación

La **innovación** va más allá de la creatividad: es llevar una idea a la práctica hasta que alguien la adopte. Se puede resumir como *creatividad + implementación + adopción*. No es un camino lineal: al implementar aparecen problemas que piden más creatividad.

- **Joseph Schumpeter** (economista): fue el primero en separar **invención** de **innovación**. Habló de **destrucción creativa**: lo nuevo desplaza a lo viejo.
- **Everett Rogers** (sociólogo), difusión de innovaciones: una innovación se adopta por etapas y por grupos sucesivos (innovadores, primeros adoptantes, mayoría temprana, mayoría tardía y rezagados).
- **Michael West y James Farr** (psicología del trabajo): definen la innovación como introducir de forma intencional algo nuevo y útil en un grupo u organización.
- **Amabile y Pratt** (2016), modelo componencial dinámico: amplía el modelo de Amabile a las organizaciones. La creatividad de las personas alimenta la innovación de la organización, y el entorno de la organización alimenta o frena esa creatividad.
- **Anderson, Potočnik y Zhou** (2014): la creatividad es la etapa de **generar** ideas y la innovación incluye además **implementarlas**. Es la distinción más aceptada hoy.

### Metacognición

La **metacognición** es el conocimiento y la regulación del propio pensamiento; dicho corto, pensar sobre cómo se está pensando. Tiene dos partes: el **conocimiento** (lo que uno sabe sobre sí mismo, sobre las tareas y sobre las estrategias) y la **regulación** (lo que uno hace con ese conocimiento mientras piensa).

Nelson y Narens describen el mecanismo con dos niveles: uno que trabaja sobre el problema y otro que lo observa y lo dirige. Entre los dos hay dos flujos: el **monitoreo**, la información que sube de cómo van las cosas, y el **control**, los ajustes que bajan.

Todos los autores coinciden en que la regulación sigue un ciclo de cuatro fases: **planificar** antes de empezar, **monitorear** y **controlar** mientras se trabaja, y **evaluar** al terminar. Lo aprendido al evaluar alimenta la siguiente planificación.

Kaufman y Beghetto aplican esto a la creatividad con la idea de **metacognición creativa**: saber cómo uno crea, en qué fase está y cuándo conviene cambiar de fase. Es justamente lo que nos falta cuando la conversación se desordena.

### Por qué nos perdemos

Varios hallazgos explican el desorden y sugieren cómo evitarlo:

- La memoria de trabajo sostiene unos 3 o 4 elementos a la vez (Cowan). Con más hilos abiertos, se pierde el hilo.
- Las tareas sin terminar siguen ocupando la mente (efecto Zeigarnik), pero dejan de interferir en cuanto se anota un plan para ellas (Masicampo y Baumeister). Anotar una idea y seguir no es perderla.
- Cada cambio de tema deja atención pegada al tema anterior (Leroy).
- Las primeras ideas suelen ser las obvias; las mejores llegan después (Beaty y Silvia).
- Somos malos eligiendo nuestras propias mejores ideas (Berg); se elige mejor con criterios escritos.
- Usar IA aumenta la creatividad individual, pero hace que las ideas de distintas personas se parezcan (Doshi y Hauser, 2024). Conviene generar ideas propias antes de pedirle las suyas a Claude.

## 3. Nuestras definiciones

### Niveles

Un **nivel** es un plano del pensamiento que se distingue por su tema. Hay dos:

- el **nivel cognitivo** piensa sobre el problema;
- el **nivel metacognitivo** piensa sobre el propio pensamiento y lo dirige.

Son los que Nelson y Narens llaman *nivel objeto* y *nivel meta*. Usamos *cognitivo* y *metacognitivo* porque se explican solos.

### Procesos y fases

Un **proceso** es una secuencia de fases. Una **fase** es una etapa de un proceso, con un solo objetivo y un resultado concreto al final. Un proceso es **cíclico** cuando vuelve a empezar o retrocede según su resultado.

Cada nivel tiene sus procesos.

En el nivel metacognitivo hay uno solo, el **proceso cíclico metacognitivo (PCM)**. Sus fases (**F-PCM**) son las cuatro de la regulación: planificar, monitorear, controlar y evaluar. Al planificar se fijan el **objetivo** (qué se quiere lograr), el proceso, la fase y la **técnica** (el método concreto con que se trabaja la fase).

```
   ┌───────────────── lo aprendido ──────────────────────┐
   ▼                                                     │
PLANIFICAR ──→ [ MONITOREAR ──→ CONTROLAR ] ──→ EVALUAR ─┘
                   ▲              │
                   └─ repite ─────┘

PCM   = proceso cíclico metacognitivo
F-PCM = fases del proceso cíclico metacognitivo: planificar · monitorear · controlar · evaluar
```

**Planificar.** Antes de empezar se decide qué se quiere lograr, qué tipo de proceso corresponde, en qué fase se empieza, con qué técnica y cómo se va a saber que se terminó. No hace falta un plan largo: alcanza con una o dos frases dichas en voz alta. Zimmerman la llama fase de *previsión*. Todo lo que se fija se refiere al nivel cognitivo; la sección *Planificar en la práctica* lo desarrolla con ejemplos.

*Termina con:* objetivo, proceso, fase, técnica y criterio de terminado. · *Riesgo:* saltarla y empezar "a ver qué sale".

**Monitorear.** Mientras se trabaja, se observa cómo va el trabajo. Las preguntas son: ¿sigo en la fase que planifiqué?, ¿avanzo?, ¿apareció un tema nuevo? Las señales típicas son la **fijación** (dar vueltas sobre lo mismo), la **bifurcación** (saltar a otro tema) y el **juicio prematuro** (evaluar ideas mientras se generan). Es el flujo que sube en el modelo de Nelson y Narens.

*Termina con:* una señal. · *Riesgo:* confiar en la sensación de que algo va bien; los "momentos ajá" también pueden ser falsos (Danek y Wiley).

**Controlar.** Según lo que se observó, se actúa: seguir, cambiar de técnica, cambiar de fase, volver a una fase anterior, aparcar una bifurcación, hacer una pausa para que la idea incube o cortar. Es el flujo que baja.

*Termina con:* una decisión de ajuste. · *Riesgo:* cambiar por impulso sin haber monitoreado, o notar el problema y no hacer nada.

**Evaluar.** Al cerrar una fase o el proceso entero, se revisa el resultado (¿se logró el objetivo?) y el proceso (¿qué funcionó?, ¿qué cambiaría?). Conviene evaluar con criterios escritos, porque somos malos juzgando nuestras propias ideas (Berg). En un PCM chico, la evaluación decide la fase siguiente; en el PCM grande, lo aprendido alimenta la próxima planificación.

*Termina con:* una conclusión y un aprendizaje. · *Riesgo:* cerrar sin evaluar y repetir los mismos errores.

En el nivel cognitivo, en cambio, el proceso depende del objetivo. A cada clase de proceso la llamamos **tipo de proceso**; no es un nivel nuevo, sino una clasificación:

| Objetivo               | Fases                                                        |
| ---------------------- | ------------------------------------------------------------ |
| Comprender             | leer u observar → interpretar → relacionar → resumir         |
| Aprender o recordar    | codificar → repasar → recuperar                              |
| Resolver un problema   | entender → planear → ejecutar → revisar                      |
| Resolver creativamente | explorar → crear → decidir → implementar → verificar         |
| Decidir                | definir criterios → listar opciones → comparar → elegir      |
| Evaluar o juzgar       | fijar criterios → examinar → valorar → justificar            |
| Razonar o demostrar    | plantear premisas → inferir → concluir                       |
| Predecir               | reunir datos → modelar → proyectar → contrastar              |
| Comunicar              | definir mensaje y público → estructurar → expresar → ajustar |

El que más nos interesa es el **proceso cíclico de resolución creativa (PCRC)**, que corresponde a la *resolución creativa de problemas* de Osborn y Parnes. Sus fases (**F-PCRC**):

- **explorar**: entender el problema;
- **crear**: generar opciones sin juzgar (diverge);
- **decidir**: elegir una opción y anotar por qué (converge);
- **implementar**: ejecutar lo decidido sin reabrirlo;
- **verificar**: comprobar que cumple lo pedido.

Si al implementar aparece un problema, vuelve a crear; si al verificar no cumple, vuelve a explorar.

```
EXPLORAR ──→ CREAR ──→ DECIDIR ──→ IMPLEMENTAR ──→ VERIFICAR
    ▲          ▲                        │              │
    │          └─ aparece un problema ──┘              │
    └─ no cumple lo pedido ────────────────────────────┘

PCRC   = proceso cíclico de resolución creativa
F-PCRC = fases del proceso cíclico de resolución creativa: explorar · crear · decidir · implementar · verificar
```

**Explorar.** Antes de buscar soluciones, se entiende el problema: se pregunta, se reúne información, se cuestionan los supuestos y se define qué sería un buen resultado. Getzels y Csikszentmihalyi mostraron que quienes dedican más tiempo a definir el problema llegan a resultados más creativos. Aquí no se decide nada.

*Termina con:* el problema bien formulado y los criterios de éxito. · *Riesgo:* resolver el problema equivocado.

**Crear.** Se diverge: se generan muchas opciones, variadas y sin juzgarlas. Ayudan las técnicas (analogías con otros campos, SCAMPER, invertir el problema) y seguir después de las primeras ideas, que suelen ser las obvias (Beaty y Silvia). Con Claude, conviene anotar ideas propias antes de pedirle las suyas, para no anclarse en su primera propuesta.

*Termina con:* una lista de opciones variadas. · *Riesgo:* quedarse con la primera idea o juzgar antes de tiempo.

**Decidir.** Se converge: se comparan las opciones con los criterios definidos al explorar y se elige una. Se anota la decisión, el motivo y las opciones descartadas con su razón, para que no se vuelvan a discutir.

*Termina con:* una decisión escrita. · *Riesgo:* elegir por intuición, no anotar el motivo o dejar la decisión a medias.

**Implementar.** Se ejecuta lo decidido, en pasos concretos, sin reabrir la decisión. Si aparece un problema que la decisión no previó, no se rediseña sobre la marcha: se anota y el PCM decide si se vuelve a crear.

*Termina con:* algo concreto hecho. · *Riesgo:* rediseñar mientras se implementa y abrir bifurcaciones.

**Verificar.** Se comprueba el resultado contra el criterio de terminado definido al principio, con evidencia (una prueba, un ejemplo, una revisión). Si no cumple, se vuelve a explorar para entender por qué.

*Termina con:* cumple o no cumple, con evidencia. · *Riesgo:* dar el trabajo por bueno sin comprobarlo.

Como segundo ejemplo usamos el **proceso cíclico de aprendizaje (PCA)**, con sus fases (**F-PCA**) codificar, repasar y recuperar. Si falla el recuerdo, vuelve a codificar.

```
CODIFICAR ──→ REPASAR ──→ RECUPERAR
    ▲                         │
    └─ falla el recuerdo ─────┘

PCA   = proceso cíclico de aprendizaje
F-PCA = fases del proceso cíclico de aprendizaje: codificar · repasar · recuperar
```

**Codificar.** Se incorpora la información dándole significado: relacionándola con lo que ya se sabe, buscando ejemplos propios y organizándola. Craik y Lockhart mostraron que lo que se procesa por su significado se recuerda mucho mejor que lo que solo se lee.

*Termina con:* una versión propia de lo aprendido (un resumen, un esquema). · *Riesgo:* leer de forma pasiva.

**Repasar.** Se vuelve sobre lo aprendido para consolidarlo. Desde Ebbinghaus se sabe que el olvido es rápido al principio, y que repasar en sesiones espaciadas funciona mejor que repasar todo junto.

*Termina con:* un recuerdo estable. · *Riesgo:* releer todo de golpe justo antes de necesitarlo.

**Recuperar.** Se trae la información de la memoria sin mirarla. Recuperar no solo comprueba lo aprendido, también lo fortalece (*efecto de la práctica de recuperación*, Roediger y Karpicke). Si falla el recuerdo, se vuelve a codificar.

*Termina con:* un recuerdo comprobado. · *Riesgo:* confundir reconocer algo al verlo con saber recordarlo.

### Cómo se relacionan

El PCM dirige el proceso cognitivo que esté corriendo, y lo hace en dos escalas. Un **PCM grande** corre sobre todo el proceso: planifica el objetivo general, revisa en cada cambio de fase si seguimos bien encaminados y evalúa el resultado final. Un **PCM chico** corre sobre cada fase: la planifica, la vigila mientras dura y, al cerrarla, decide cuál sigue, que puede ser una anterior.

```
NIVEL METACOGNITIVO ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
PCM grande (sobre el proceso cognitivo que esté corriendo)
   ┌──────────────────────────── lo aprendido ─────────────────────────────┐
   ▼                                                                       │
┌────────────┐   ┌─────────────────────────────┐   ┌────────────┐          │
│ PLANIFICAR │ → │ MONITOREAR ──→ CONTROLAR    │ → │ EVALUAR    │──────────┘
│ objetivo y │   │     ▲              │        │   │ ¿se logró? │
│ proceso    │   │     └──────────────┘        │   │            │
└────────────┘   └─────────────────────────────┘   └────────────┘
      │               ↓ ↑ (en cada cambio de fase)        ▲
      ▼                                                   │
PCM chicos (uno por fase del proceso que corre)
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐   ┌─────────────┬─────────────┬─────────────┐
│ P→[M⇄C]→E   │ P→[M⇄C]→E   │ P→[M⇄C]→E   │ P→[M⇄C]→E   │ P→[M⇄C]→E   │   │ P→[M⇄C]→E   │ P→[M⇄C]→E   │ P→[M⇄C]→E   │
└──────┬──▲───┴──────┬──▲───┴──────┬──▲───┴──────┬──▲───┴──────┬──▲───┘   └──────┬──▲───┴──────┬──▲───┴──────┬──▲───┘
       │  │          │  │          │  │          │  │          │  │              │  │          │  │          │  │
NIVEL COGNITIVO ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
       ▼  │          ▼  │          ▼  │          ▼  │          ▼  │              ▼  │          ▼  │          ▼  │
PCRC · resolver creativamente                                             PCA · aprender o recordar
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐   ┌─────────────┬─────────────┬─────────────┐
│ EXPLORAR   ─┼→ CREAR     ─┼→ DECIDIR   ─┼→ IMPLEMENTAR┼→ VERIFICAR  │   │ CODIFICAR  ─┼→ REPASAR   ─┼→ RECUPERAR  │ … otros objetivos
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘   └─────────────┴─────────────┴─────────────┘
                     ▲                           │                               ▲                           │
                     └─ volver a una F-PCRC ─────┘                               └─ falla: volver a codificar┘

▼ control (baja ajustes) · ▲ monitoreo (sube información)
PCM    = proceso cíclico metacognitivo
PCRC   = proceso cíclico de resolución creativa
PCA    = proceso cíclico de aprendizaje
F-PCM  = fases del proceso cíclico metacognitivo: P = planificar · M = monitorear · C = controlar · E = evaluar
F-PCRC = fases del proceso cíclico de resolución creativa: explorar · crear · decidir · implementar · verificar
F-PCA  = fases del proceso cíclico de aprendizaje: codificar · repasar · recuperar
```

### Planificar en la práctica

Al planificar se fijan cinco cosas: objetivo, proceso, fase, técnica y criterio de terminado. Las cinco se refieren al **nivel cognitivo**: el PCM planifica el trabajo, no a sí mismo. Por eso la fase es siempre la de un proceso cognitivo (una F-PCRC, una F-PCA…), nunca una F-PCM.

Qué se fija depende de la escala del PCM:

| Qué se fija | PCM grande (planifica el proceso entero) | PCM chico (planifica una fase) |
|---|---|---|
| **Objetivo** | qué debe lograr el proceso completo | qué debe dejar esa fase |
| **Proceso** | qué tipo de proceso cognitivo corresponde (PCRC, PCA…) | no se fija: ya está elegido |
| **Fase** | con qué fase se empieza | es la fase que toca |
| **Técnica** | no se fija | con qué método se trabaja la fase |
| **Criterio de terminado** | cuándo el proceso cumplió su objetivo | cuándo la fase cumplió su objetivo |

Dos ejemplos muestran cómo se ve esto en un caso real.

**Ejemplo 1: resolver creativamente (PCRC).** Queremos definir cómo se escriben los ejemplos dentro de las normas.

El PCM grande planifica el proceso entero:

- **objetivo**: elegir un formato para los ejemplos y aplicarlo en todas las normas;
- **proceso**: PCRC;
- **fase inicial**: explorar;
- **criterio de terminado**: todas las normas usan el formato y el generador las procesa sin errores.

Después, un PCM chico planifica cada fase:

| Fase | Objetivo | Técnica | Criterio de terminado |
|---|---|---|---|
| Explorar | entender qué tiene que cumplir un ejemplo | revisar 5 normas existentes y hacer preguntas de requisitos | lista de requisitos aprobada |
| Crear | tener opciones variadas | analogías (Rust, Python, las RFC) y SCAMPER | al menos 8 opciones, de al menos 3 enfoques distintos |
| Decidir | elegir una opción | tabla de opciones contra los requisitos | decisión anotada, con motivo y descartadas |
| Implementar | aplicar el formato | cambiar una norma piloto y después el resto | todas las normas cambiadas |
| Verificar | comprobar el resultado | correr el generador y revisar 3 normas al azar | sin errores y con las normas revisadas correctas |

**Ejemplo 2: aprender (PCA).** Queremos aprender la gramática Lark que usa el compilador.

El PCM grande planifica el proceso entero:

- **objetivo**: poder escribir una regla nueva sin consultar la documentación;
- **proceso**: PCA;
- **fase inicial**: codificar;
- **criterio de terminado**: escribir de memoria una regla que el parser acepte.

Y un PCM chico planifica cada fase:

| Fase | Técnica | Criterio de terminado |
|---|---|---|
| Codificar | leer la documentación y resumir cada concepto con un ejemplo propio del repo | un resumen de una página |
| Repasar | repaso espaciado: hoy, en 2 días y en una semana | los tres repasos hechos |
| Recuperar | escribir reglas sin mirar el resumen | tres reglas correctas seguidas |

### Técnicas por fase

Elegir la técnica es parte de planificar cada fase. Las que siguen son algunas de las más usadas; no son todas, y para cada fase existen muchas más.

#### Técnicas del PCRC

**Explorar**

1. **Los 5 porqués**: preguntar "¿por qué?" cinco veces seguidas para llegar a la causa de fondo.
2. **Preguntas de requisitos**: qué tiene que cumplir la solución, para quién es y con qué límites.
3. **Revisar casos existentes**: estudiar cómo se resolvió antes, aquí o en otros proyectos.
4. **Reformular el problema**: escribirlo de varias maneras ("¿cómo podríamos…?") para ver cuál abre más caminos.
5. **Mapa de supuestos**: listar lo que damos por cierto y marcar qué no está comprobado.
6. **Entrevistar a usuarios**: preguntar a quien vive el problema qué necesita de verdad.

**Crear**

1. **Analogías**: buscar cómo se resolvió algo parecido en otro campo y traer la idea.
2. **SCAMPER**: transformar una idea existente con siete verbos: sustituir, combinar, adaptar, modificar, darle otro uso, eliminar e invertir.
3. **Invertir el problema**: preguntar "¿cómo lo haríamos fracasar?" y dar vuelta cada respuesta.
4. **Seis Sombreros** (de Bono): mirar el tema desde seis ángulos, uno por vez: datos, emociones, riesgos, beneficios, creatividad y proceso.
5. **Escritura libre**: escribir ideas sin parar ni corregir durante unos minutos.
6. **Jugar con restricciones**: preguntar "¿y si no hubiera presupuesto?" o "¿y si tuviera que funcionar para un niño?".
7. **Brainwriting**: cada uno escribe ideas en silencio antes de compartirlas. En grupo rinde más que el brainstorming hablado.

**Decidir**

1. **Tabla de criterios**: puntuar cada opción contra los criterios definidos al explorar.
2. **Pros y contras**: listar ventajas y desventajas de cada opción.
3. **Descarte por eliminación**: quitar primero las opciones que violan algún requisito obligatorio.
4. **Premortem**: imaginar que la opción elegida fracasó y explicar por qué.
5. **Votación por puntos**: repartir unos pocos puntos entre las opciones, solo o en grupo.
6. **Registro de decisión**: escribir la decisión, el motivo y las opciones descartadas con su razón.

**Implementar**

1. **Piloto**: aplicar la solución a un solo caso antes de extenderla.
2. **Pasos pequeños**: dividir el trabajo en cambios cortos, cada uno verificable.
3. **Plan de tareas**: una lista ordenada de pasos con su resultado esperado.
4. **Lista de pendientes**: anotar los problemas que aparecen, en lugar de resolverlos sobre la marcha.
5. **Timeboxing**: fijar un tiempo máximo para cada paso.
6. **Prototipo**: construir una versión mínima para aprender antes de hacer la final.

**Verificar**

1. **Pruebas**: comprobar automáticamente que el resultado hace lo esperado.
2. **Lista de chequeo**: repasar punto por punto el criterio de terminado.
3. **Revisión de una muestra**: revisar a mano algunos casos elegidos al azar.
4. **Revisión por otra persona**: que alguien que no lo hizo lo revise.
5. **Comparar con el objetivo**: volver a la formulación del problema y ver si la solución la cumple.
6. **Prueba con usuarios**: ver cómo lo usa alguien real.

#### Técnicas del PCA

**Codificar**

1. **Resumir con palabras propias**: reescribir lo leído sin copiar.
2. **Ejemplos propios**: inventar o buscar un ejemplo de cada concepto en el propio contexto.
3. **Mapa conceptual**: dibujar los conceptos y cómo se relacionan.
4. **Elaboración**: preguntarse "¿por qué es así?" y "¿con qué lo conecto?".
5. **Codificación dual**: combinar palabras con imágenes o diagramas.
6. **Método Cornell**: tomar notas en una columna y escribir preguntas clave en otra.

**Repasar**

1. **Repaso espaciado**: repasar en intervalos cada vez más largos (1 día, 3 días, una semana).
2. **Tarjetas** (como Anki): una pregunta de un lado y la respuesta del otro, con repaso programado.
3. **Intercalado**: mezclar temas distintos en la misma sesión en lugar de repasar uno solo.
4. **Releer el resumen propio**: repasar la versión propia, no el material original completo.
5. **Rehacer el mapa conceptual**: volver a dibujarlo y compararlo con el anterior.

**Recuperar**

1. **Autoexamen**: responder preguntas sin mirar.
2. **Recuerdo libre**: escribir todo lo que se recuerda de un tema antes de consultar.
3. **Técnica Feynman**: explicar el tema con palabras simples, como a un principiante. Donde uno se traba, hay una laguna.
4. **Enseñar a otro**: explicarle el tema a alguien.
5. **Resolver ejercicios**: aplicar lo aprendido a problemas nuevos.
6. **Tarjetas en modo pregunta**: intentar responder antes de dar vuelta la tarjeta.

### Bifurcaciones

#### Qué son y por qué aparecen

Una **bifurcación** es un tema o una idea nueva que aparece en medio de una fase. Estamos explorando cómo nombrar algo y surge una duda sobre el formato; estamos implementando y descubrimos un error en otro archivo; estamos decidiendo y se nos ocurre una opción que cambia el problema.

Las bifurcaciones no son un defecto. El pensamiento creativo funciona por asociación (Mednick): una idea despierta otra que está cerca, y a veces la mejor idea es justamente la que se escapó del camino. El problema no es que aparezcan, sino qué hacemos con ellas.

#### Su relación con el problema

El desorden descrito al principio es, casi siempre, una cadena de bifurcaciones sin gestionar. Aparece un tema nuevo, lo seguimos sin decidirlo, y el tema anterior queda abierto. Eso tiene tres costos que la psicología explica bien:

- el tema abandonado sigue ocupando la mente porque quedó sin terminar (Zeigarnik);
- al saltar de tema, parte de la atención se queda en el anterior (Leroy);
- con más de 3 o 4 hilos abiertos, la memoria de trabajo no da abasto (Cowan).

Al final de la sesión, además, lo que se decidió en un hilo, lo que fue solo una idea en otro y lo que quedó pendiente en un tercero están mezclados en la misma conversación.

En términos de nuestro modelo, una bifurcación es un asunto del PCM:

- **detectarla** es tarea de **monitorear**: "esto es un tema nuevo";
- **decidir qué hacer con ella** es tarea de **controlar**.

Hay cuatro destinos posibles, y lo importante es elegir uno en lugar de dejarse llevar:

1. **Seguirla ahora**: cambiar de hilo a propósito, sabiendo que el anterior queda aparcado.
2. **Aparcarla**: anotarla y seguir con la fase actual.
3. **Descartarla**: decir que no va, con el motivo.
4. **Promoverla a issue**: guardarla fuera de la sesión.

Masicampo y Baumeister mostraron que una tarea pendiente deja de interferir en cuanto se anota un plan para ella. Por eso aparcar o abrir una issue no es perder la idea: es lo que permite dejar de pensar en ella y volver a la fase actual.

```
           aparece una bifurcación en medio de una fase
                              │
                  MONITOREAR: "esto es un tema nuevo"
                              │
                     CONTROLAR: ¿qué hacemos?
       ┌──────────────┬───────┴──────┬──────────────────┐
       ▼              ▼              ▼                  ▼
  seguirla ahora   aparcarla     descartarla     promoverla a issue
  (el hilo actual  (liviana)     (con motivo)       (pesada)
   queda aparcado)    │
                      │ al cerrar la sesión
                      ▼
            ¿cumple alguna condición? ── sí ──→ issue
                      │
                      no ──→ se descarta
```

#### Dos pesos: livianas y pesadas

No todas las bifurcaciones merecen el mismo tratamiento. Anotar cada idea suelta en GitHub llenaría el registro de ruido; dejar todo en la conversación haría perder lo importante. Por eso distinguimos dos pesos.

| | Bifurcación liviana | Bifurcación pesada (issue) |
|---|---|---|
| Qué es | una idea o un tema que surge al pensar | trabajo pendiente, un defecto encontrado o una decisión que falta |
| Dónde vive | en el contexto de la sesión | en GitHub |
| Cuánto dura | lo que dura la sesión | hasta que se cierra la issue |
| Quién la ve | solo la sesión actual | cualquier persona o sesión |
| Cuánto cuesta | casi nada: una línea | escribir contexto, problema y opciones |
| Ejemplo | "¿y si usamos tablas?" mientras exploramos el formato | "el parser falla con comentarios anidados" mientras implementamos otra cosa |

Una bifurcación liviana pasa a pesada solo si cumple al menos una de estas condiciones:

1. deja trabajo que no se va a hacer en esta sesión;
2. hay que compartirla con alguien;
3. necesita una decisión que no se toma ahora.

Si no cumple ninguna, se queda liviana y muere con la sesión, o se descarta antes.

#### Bifurcaciones livianas: el mapa de hilos

Las bifurcaciones livianas se manejan como **hilos** dentro de la sesión. Cada hilo tiene un estado:

| Estado | Significa |
|---|---|
| **abierto** | se está pensando ahora; idealmente hay uno solo |
| **aparcado** | interesa, pero para después |
| **descartado** | no va, y se anota por qué |
| **convergido** | llegó a una conclusión |

Claude puede llevar un mapa de estos hilos y mostrarlo cuando cambia algo o cuando se lo pide. El mapa también marca dónde se abrieron opciones (◇ diverge) y dónde se cerraron (◆ converge):

```
Tema: formato de normas
  ◇ diverge
  ├── YAML            descartado (poco legible)
  ├── Markdown        convergido ✔ → decisión
  │    └── ¿tablas?   aparcado
  └── DSL propio      aparcado
  ◆ converge → Markdown

◇ = se abren opciones · ◆ = se cierran opciones
```

Al cerrar la sesión se repasan los hilos aparcados: cada uno pasa a issue, si cumple alguna condición, o se descarta. Ningún hilo aparcado se queda flotando.

#### Bifurcaciones pesadas: el skill de issues

Antes del skill `/shared:issue`, los pendientes y los defectos encontrados se perdían de varias maneras:

- se dejaban "para el final de la sesión" y la sesión terminaba sin anotarlos;
- se anotaban en archivos del repo o en la memoria de Claude, que solo existe en una máquina y nadie más ve;
- con varias sesiones de Claude trabajando en paralelo, ninguna sabía qué había encontrado la otra;
- no había un lugar único donde ver qué estaba pendiente y qué esperaba una decisión del usuario.

El skill resuelve esto con unas pocas reglas:

1. **En el momento.** La bifurcación se propone apenas aparece, sin esperar al final, y mientras tanto se sigue con la fase actual.
2. **Siempre igual.** La propuesta tiene contexto, problema y opciones numeradas (la primera es la recomendada), para que el usuario pueda decidir sin preguntar más.
3. **Con permiso.** Nada entra al registro sin el sí del usuario, y nada se resuelve sin su sí.
4. **En un árbol.** La issue se crea como sub-issue del nodo donde se encontró. La raíz del árbol es una issue de **línea de base** (*baseline*), y `/shared:tree` muestra el árbol completo, aunque abarque varios repositorios.
5. **Con traspaso.** Cada issue lleva un *hand-off prompt*: el texto que otra sesión necesita para retomarla sin el contexto de la conversación original.

```
#40 línea de base (baseline)
├── #41 normas: formato de los ejemplos            ⏳ espera de ti
│    └── #47 parser falla con comentarios anidados  ▶ Claude puede
└── #43 generador: capa 2 incompleta               ⛔ bloqueado
```

Así, una bifurcación pesada queda guardada fuera de la cabeza y fuera de la sesión, en un lugar que todos ven, enganchada al trabajo que la originó y lista para que cualquier sesión la retome.

## 4. Conclusiones

Con este vocabulario, el desorden del principio tiene nombre: es un PCM que no está corriendo. Nadie planifica qué fase toca, nadie monitorea cuándo se salta de tema y nadie decide qué hacer con cada bifurcación.

Para evitarlo:

1. Una sola fase activa a la vez, y dicha en voz alta al empezar.
2. Cada bifurcación se aparca, se descarta o pasa a issue, pero no se sigue sin decidirlo.
3. Lo decidido pasa a otra sesión por escrito (una spec o una issue), con objetivo, decisión, motivo, opciones descartadas, alcance y criterio de terminado.
4. Claude puede encargarse del monitoreo, avisando cuando aparece una bifurcación o cuando se está evaluando antes de tiempo; el control lo decide la persona.

## 5. Pendiente de decidir

1. No todo proceso cognitivo es cíclico; lo cíclico suele venir del PCM, que decide retroceder. ¿Quitamos "cíclico" del nombre de los procesos cognitivos (PRC, PA)?
2. ¿Usamos "técnica" o "estrategia"?
