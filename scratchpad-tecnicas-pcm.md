# Técnicas para las fases del PCM

PCM = proceso cíclico metacognitivo. Resúmenes investigados y verificados por agentes. No son todas las técnicas posibles: hay más.

## Planificar

### Intenciones de implementación

**Nivel de evidencia:** fuerte

#### 1. Origen, teoría y evidencia

**Quién la investigó.** El psicólogo alemán Peter Gollwitzer propuso el concepto a comienzos de los años 90 (Gollwitzer, 1993, *European Review of Social Psychology*). Lo hizo conocido con un artículo clave: Gollwitzer (1999), "Implementation intentions: Strong effects of simple plans", *American Psychologist*. Paschal Sheeran es su coautor frecuente en las revisiones posteriores.

**La teoría.** Gollwitzer separa dos cosas:
- Una **intención de meta** dice *qué* quiero lograr ("quiero terminar la especificación").
- Una **intención de implementación** dice *cuándo, dónde y cómo* voy a actuar, con la forma **"si ocurre X, entonces hago Y"**. Por eso también se llaman *planes si-entonces*.

Este plan vincula de antemano una situación crítica con una respuesta concreta. Cuando aparece la situación, la respuesta se dispara casi sola, sin tener que decidir en ese momento. Gollwitzer y sus colegas lo describen como pasar el control de la conducta a una señal de la situación. Llaman a este efecto *automaticidad estratégica*: un hábito instantáneo que nace de una sola decisión, no de la repetición. Esto ayuda en los problemas típicos de llevar una meta a la acción: no empezar, distraerse, no notar el momento oportuno o seguir con un camino que ya no sirve.

**La evidencia.**
- **Gollwitzer y Sheeran (2006)**, *Advances in Experimental Social Psychology*. Es un metaanálisis (estudio que combina los resultados de muchos estudios) de 94 pruebas independientes. El efecto medio sobre el logro de metas fue **d = 0,65**. La "d" mide la diferencia entre el grupo que planifica y el que no; 0,65 es un efecto de mediano a grande. Gollwitzer y Oettingen (2013) citan el mismo metaanálisis con d = 0,61.
- **Sheeran, Listrom y Gollwitzer (2025)**, *European Review of Social Psychology*, metaanálisis de **642 pruebas**. Confirma el efecto sobre pensamientos, emociones y acciones, con tamaños de d = 0,27 a d = 0,66 según el tipo de resultado. El efecto es mayor cuando el plan tiene forma estricta si-entonces, cuando la persona está muy motivada y cuando ensaya el plan.
- **Wang, Wang y Gai (2021)**, *Frontiers in Psychology*, metaanálisis de 24 efectos sobre la combinación con el contraste mental (imaginar la meta y luego los obstáculos). Encontraron un efecto pequeño a mediano: g = 0,34 ("g" es una medida parecida a "d"). Detectaron un posible sesgo de publicación: los estudios con resultados nulos se publican menos, y eso infla el promedio. Al corregirlo, el efecto bajó a g = 0,24.

**Límites.** El efecto depende de que la meta importe de verdad. Si la meta es débil, el plan sirve poco. Casi todos los estudios vienen de la psicología de la salud, la educación y el laboratorio. No encontré estudios en trabajo de software ni con asistentes de IA.

**Nivel de evidencia: fuerte** para la técnica en general (cientos de pruebas y varios metaanálisis). Los tamaños de efecto pueden estar algo inflados por sesgo de publicación, como muestra el caso de Wang y colaboradores (2021).

#### 2. Proceso y buenas prácticas

**Pasos**
1. **Fijar la meta de la sesión.** Escribir en una frase qué se quiere lograr. Comprobar que importa.
2. **Anticipar las situaciones críticas.** Preguntarse: ¿qué puede descarrilar esta meta? Por ejemplo, una bifurcación que aparece, una prueba que falla o una respuesta de Claude que no se entiende.
3. **Elegir la respuesta para cada situación.** Una acción concreta, pequeña y que se pueda hacer en el momento.
4. **Escribir el plan en forma "si… entonces…".** Un plan por situación, con la condición observable y la acción precisa.
5. **Ensayar el plan.** Leerlo en voz alta o repetirlo una vez. El ensayo aumenta el efecto (Sheeran, Listrom y Gollwitzer, 2025).
6. **Dejarlo visible.** Pegarlo al inicio de la sesión con Claude y pedirle que avise cuando se cumpla una condición.

**Buenas prácticas**
- Usar condiciones observables ("si la prueba falla dos veces"), no vagas ("si me trabo").
- Pocos planes: dos o tres por sesión. Es una recomendación práctica: muchos planes son difíciles de recordar.
- Combinarlo con el contraste mental: primero imaginar el resultado, luego el obstáculo, luego el plan.
- Conectar con las otras fases del PCM: el "si" alimenta monitorear y el "entonces" es controlar.

**Errores comunes**
- Escribir solo la meta, sin el "si".
- Elegir respuestas que exigen decidir otra vez ("entonces veo qué hago").
- Planear para una meta que no importa.
- Mantener planes rígidos para situaciones que cambian mucho: revisarlos en la fase evaluar.

#### 3. Ejemplo

Lucía escribe con Claude la especificación de un módulo de pagos. En sesiones anteriores perdió horas siguiendo bifurcaciones y terminó sin cerrar nada. Hoy empieza por **planificar**.

**Meta.** Lucía escribe:
> "Meta de hoy: cerrar la fase *decidir* del PCRC para el manejo de reintentos. Al final quiero un requisito redactado y aprobado."

**Situaciones críticas.** Le pide a Claude: "Antes de empezar, ¿qué suele descarrilarme en esta fase?". Juntos identifican tres riesgos: bifurcaciones sobre otros módulos, volver a *explorar* opciones ya descartadas y alargar la sesión sin cerrar nada.

**Planes si-entonces.** Lucía escribe y pega al inicio de la sesión:
> 1. "Si aparece un tema que no es reintentos, entonces le pido a Claude que lo anote como bifurcación liviana en estado *aparcado* y sigo."
> 2. "Si vuelvo a proponer una opción que ya descartamos, entonces leo el motivo del descarte y no reabro el debate."
> 3. "Si pasan 50 minutos sin un requisito redactado, entonces paro y elijo la mejor opción disponible."
>
> "Claude, avísame cuando se cumpla alguna de estas condiciones."

Lee los tres planes en voz alta una vez.

**Durante la sesión.** A los 20 minutos Lucía escribe: "Oye, ¿y si cambiamos también el formato de los logs?". Claude responde: "Se cumple tu plan 1. Lo dejo como bifurcación liviana *aparcada*: 'formato de logs'." Lucía sigue con reintentos. Más tarde vuelve a proponer reintentos infinitos. Claude avisa: "Se cumple tu plan 2. Descartamos esa opción hace 15 minutos porque satura el servicio externo." Lucía lee el motivo y no reabre el debate.

**Resultado.** A los 45 minutos, Lucía aprueba el requisito: "Reintentar como máximo 3 veces, con espera creciente." Al cerrar, revisa la bifurcación aparcada. Decide que tiene peso propio y la convierte en bifurcación pesada: un issue en GitHub. En la fase **evaluar** anota: "Los planes 1 y 2 funcionaron. El plan 3 no se activó; lo mantengo."

#### Fuentes

- [Gollwitzer (1999). Implementation intentions: Strong effects of simple plans. American Psychologist, 54(7), 493-503 (PDF, Univ. Konstanz)](https://www.socmot.uni-konstanz.de/sites/default/files/99_Gollwitzer_Implementation_Intentions.pdf)
- [Gollwitzer y Sheeran (2006). Implementation intentions and goal achievement: A meta-analysis of effects and processes. Advances in Experimental Social Psychology, 38, 69-119](https://www.socmot.uni-konstanz.de/publications/implementation-intentions-and-goal-achievement-meta-analysis-effects-and-processes)
- [Sheeran, Listrom y Gollwitzer (2025). The when and how of planning: Meta-analysis of the scope and components of implementation intentions in 642 tests. European Review of Social Psychology, 36(1), 162-194 (KOPS)](https://kops.uni-konstanz.de/handle/123456789/69905)
- [Wang, Wang y Gai (2021). A meta-analysis of the effects of mental contrasting with implementation intentions on goal attainment. Frontiers in Psychology](https://pmc.ncbi.nlm.nih.gov/articles/PMC8149892/)
- [Gollwitzer y Oettingen (2013). Implementation intentions (cita d = 0,61 del metaanálisis de 2006)](https://www.socmot.uni-konstanz.de/sites/default/files/gollwitzer_oettingen_2013-Implementation_Intentions.pdf)
- [Gollwitzer, Bayer y Wieber: planes si-entonces, control delegado a señales de la situación y automaticidad estratégica (KOPS)](https://kops.uni-konstanz.de/entities/publication/7f6816cc-8a62-46d3-9902-9e314d4452e2)

### WOOP / contraste mental (MCII)

**Nivel de evidencia:** moderada

#### 1. Origen, teoría y evidencia

**Quién.** La psicóloga Gabriele Oettingen (Universidad de Nueva York y Universidad de Hamburgo) investigó el **contraste mental**: imaginar el futuro deseado y, enseguida, el obstáculo del presente que lo frena. Después lo combinó con las **intenciones de implementación** de Peter Gollwitzer, que son planes del tipo "si ocurre X, entonces hago Y". La combinación se llama **MCII** (contraste mental con intenciones de implementación). **WOOP** es su versión fácil de recordar: *Wish* (deseo), *Outcome* (resultado), *Obstacle* (obstáculo), *Plan*.

**Teoría.** La teoría de realización de fantasías (Oettingen, 2000; revisión en Oettingen, 2012) distingue tres modos de pensar el futuro:
- **Fantasear** solo con lo positivo: relaja y reduce el esfuerzo.
- **Detenerse** solo en los obstáculos del presente: no da dirección.
- **Contrastar** deseo y obstáculo, en ese orden: si la expectativa de éxito es alta, la persona se compromete; si es baja, suelta la meta. Esto ayuda a elegir bien en qué invertir esfuerzo.

El plan "si… entonces" convierte el obstáculo en una señal que dispara la acción sin tener que decidir de nuevo.

**Evidencia.** Un **metaanálisis** junta los resultados de muchos estudios. El **tamaño de efecto** (g o d) mide cuánto cambia el resultado: 0,2 es pequeño, 0,5 medio y 0,8 grande. El **sesgo de publicación** ocurre cuando los estudios con resultados positivos se publican más, y eso infla el efecto.
- Wang, Wang y Gai (2021), metaanálisis de 21 artículos (24 efectos, 15.907 participantes): efecto pequeño a medio del MCII sobre el logro de metas, g = 0,34. El efecto fue mayor cuando un experimentador guiaba el ejercicio cara a cara (g = 0,47) que cuando se hacía con un documento, en línea o en papel (g = 0,28). Los autores detectaron sesgo de publicación; al corregirlo, el efecto bajó a g = 0,24.
- Cross y Sheffield (2019), metaanálisis en conductas de salud (1.528 participantes): contraste mental, g = 0,28 hasta cuatro semanas y g = 0,38 hasta tres meses (5 estudios). Con el plan "si… entonces" agregado (MCII, 7 estudios) el efecto fue similar, g = 0,28: agregar el plan no aumentó el efecto, aunque hay pocos estudios.
- Gollwitzer y Sheeran (2006), metaanálisis de 94 pruebas sobre intenciones de implementación por separado: d = 0,65 (efecto medio a grande).
- Duckworth y colegas (2011): 66 estudiantes de secundaria que se preparaban para un examen importante. Los que hicieron un ejercicio escrito de MCII de 30 minutos completaron más de un 60 % más de preguntas de práctica que el grupo de control.

**Nivel de evidencia: moderada.** Hay metaanálisis con efectos consistentes, pero pequeños a medios, con sesgo de publicación detectado y pocos estudios en trabajo intelectual o de software.

#### 2. Proceso y buenas prácticas

**Pasos (unos 5 a 10 minutos, al empezar una sesión o una fase):**
1. **Deseo (W).** Escribe una meta concreta, desafiante y alcanzable en el tiempo que tienes. Una sola frase.
2. **Resultado (O).** Imagina el mejor resultado y cómo te sentirías. Dedícale unos segundos de verdad, no solo una lista.
3. **Obstáculo (O).** Busca el obstáculo **interno** principal: un hábito, una distracción, una emoción o una creencia tuya. Imagínalo con detalle.
4. **Plan (P).** Escribe un plan "si [obstáculo], entonces [acción concreta]". La acción debe ser pequeña y posible en el momento.
5. **Revisa el compromiso.** Si al contrastar ves que la meta no es realista, ajústala o suéltala. Eso también es un buen resultado.

**Buenas prácticas:**
- Haz los pasos en este orden. Pensar primero en el obstáculo y después en el deseo no produce el mismo compromiso (Kappes, Singmann y Oettingen, 2012; Oettingen, 2012).
- Elige un obstáculo que dependa de ti. "El cliente cambia de idea" no sirve; "me pongo a codificar sin cerrar la especificación" sí.
- Pide que alguien te guíe. En los estudios, el ejercicio guiado por una persona funcionó mejor que el hecho con un documento. Que Claude haga las preguntas es una adaptación razonable, pero no está probada.
- Deja el plan "si… entonces" a la vista para monitorear durante la sesión.

**Errores comunes:**
- Escribir solo el deseo y el resultado: eso es fantasear y puede bajar el esfuerzo.
- Metas vagas ("mejorar el módulo").
- Planes que son buenas intenciones ("si me distraigo, me concentro"), sin una acción observable.
- Tratar WOOP como un trámite: sin imaginar, el contraste pierde fuerza.

#### 3. Ejemplo

**Situación.** Lucía escribe la especificación de un módulo de permisos. Tiene dos horas, de 9:30 a 11:30. Le pide a Claude: *"Antes de empezar, hazme las preguntas de WOOP, una por una."*

**Deseo.** Claude pregunta qué quiere lograr hoy. Lucía escribe: *"Cerrar la sección de roles de la especificación, con los cinco roles definidos y sus permisos en una tabla."*

**Resultado.** *"Si lo logro, mañana empiezo a implementar sin dudas, y la revisión con el equipo será corta."*

**Obstáculo.** Claude pregunta: *"¿Qué hay en ti que podría impedirlo?"* Lucía piensa y escribe: *"Me engancho con temas laterales. La última vez pasé una hora pensando en auditoría de accesos y no cerré nada."*

**Plan.** *"Si aparece un tema que no es roles, entonces lo anoto como bifurcación liviana en estado aparcado y vuelvo a la tabla. Si a las 11:00 la tabla no está, entonces paso a decidir con lo que tengo."*

Lucía le pide a Claude: *"Recuérdame este plan si me ves abrir otro tema."*

**Durante la sesión.** En la fase explorar del PCRC, Lucía escribe: *"¿Y si los permisos caducan a los 90 días?"* Claude responde: *"Esto parece un tema nuevo. Según tu plan, ¿lo aparco como bifurcación liviana?"* Lucía contesta: *"Sí, aparcado. Seguimos con los roles."* Más tarde surge otra idea, el registro de auditoría, que afecta a otros módulos. Claude vuelve a recordarle el plan. Lucía decide: *"Esta no la aparco. Es una bifurcación pesada. Ábrela como issue en GitHub."*

**Cierre.** A las 10:50 la tabla de cinco roles está lista y Lucía pasa a la fase decidir. Al terminar, en la fase evaluar del PCM, revisa con Claude: el plan se activó dos veces, quedó una bifurcación liviana aparcada (caducidad) y una bifurcación pesada abierta como issue (auditoría). Ve que su plan no cubría el segundo caso. Para la próxima sesión agrega otro plan: *"Si una bifurcación toca otro módulo, entonces la abro como issue de inmediato."*

#### Fuentes

- [Wang, Wang y Gai (2021). A Meta-Analysis of the Effects of Mental Contrasting With Implementation Intentions on Goal Attainment. Frontiers in Psychology, 12, 565202](https://pmc.ncbi.nlm.nih.gov/articles/PMC8149892/)
- [Cross y Sheffield (2019). Mental contrasting for health behaviour change: a systematic review and meta-analysis of effects and moderator variables. Health Psychology Review](https://doi.org/10.1080/17437199.2019.1594332)
- [Gollwitzer y Sheeran (2006). Implementation intentions and goal achievement: A meta-analysis of effects and processes. Advances in Experimental Social Psychology, 38, 69-119](https://doi.org/10.1016/S0065-2601(06)38002-1)
- [Oettingen (2012). Future thought and behaviour change. European Review of Social Psychology, 23(1), 1-63](https://www.psy.uni-hamburg.de/arbeitsbereiche/paedagogische-psychologie-und-motivation/personen/oettingen-gabriele/dokumente/oettingen-2012.pdf)
- [Kappes, Singmann y Oettingen (2012). Mental contrasting instigates goal pursuit by linking obstacles of reality with instrumental behavior. Journal of Experimental Social Psychology](https://www.psy.uni-hamburg.de/arbeitsbereiche/paedagogische-psychologie-und-motivation/personen/oettingen-gabriele/dokumente/kappes-singmann-oettingen-2012.pdf)
- [Oettingen y Reininger (2016). The power of prospection: mental contrasting and behavior change. Social and Personality Psychology Compass, 10(11), 591-604](https://www.psy.uni-hamburg.de/arbeitsbereiche/paedagogische-psychologie-und-motivation/personen/oettingen-gabriele/dokumente/oettingen-reininger-2016.pdf)
- [Duckworth, Grant, Loew, Oettingen y Gollwitzer (2011). Self-regulation strategies improve self-discipline in adolescents: benefits of mental contrasting and implementation intentions. Educational Psychology, 31(1), 17-26](https://www.socmot.uni-konstanz.de/sites/default/files/duckworth_self-regulation_11.pdf)

### Preguntas de planificación

**Nivel de evidencia:** moderada

#### 1. Origen, teoría y evidencia

**Quién.** Gregory Schraw, psicólogo educativo, propuso una lista corta de preguntas fijas para cada fase de la regulación del pensamiento: planificar, monitorear y evaluar. La llamó *lista de control de la regulación* (Regulatory Checklist). Se cita como Schraw (1998), "Promoting general metacognitive awareness", *Instructional Science* 26, 113-125. El mismo texto se reeditó como capítulo de libro en 2001, por eso algunas fuentes la citan como Schraw (2001). Para planificar, la lista pregunta: ¿qué tipo de tarea es?, ¿cuál es mi objetivo?, ¿qué información y qué estrategias necesito?, ¿cuánto tiempo y cuántos recursos necesito? La lista trae preguntas parecidas para monitorear y para evaluar.

**Teoría.** Schraw divide la metacognición en dos partes. El *conocimiento de la cognición* es saber cómo pensamos. La *regulación de la cognición* es dirigir ese pensamiento, y planificar es su primer paso. Schraw sostiene que estas habilidades sirven en cualquier campo y que se pueden enseñar. Antes, Schraw y Dennison (1994) crearon el *Inventario de Conciencia Metacognitiva* (MAI), un cuestionario de 52 ítems. Una de sus escalas mide la planificación: fijar metas y repartir recursos antes de empezar. El MAI mide la habilidad. No prueba que las preguntas la mejoren. Además, revisiones posteriores del MAI no confirmaron sus ocho escalas por separado. Recomiendan usar solo dos puntajes: conocimiento y regulación. Por eso la escala de planificación sola no es una medida fiable.

**Evidencia.**
- Un *metaanálisis* junta los resultados de muchos estudios para calcular un efecto promedio. El metaanálisis de de Boer y colegas (2018) revisó 48 intervenciones que enseñaban estrategias metacognitivas, que casi siempre incluyen planificar. El efecto sobre el rendimiento fue g = 0,50 al terminar y g = 0,63 en el seguimiento. (*g* mide la diferencia entre el grupo que recibió la enseñanza y el que no. Un 0,5 se considera un efecto medio.)
- Dignath y Büttner (2008) revisaron intervenciones en primaria y secundaria y también encontraron efectos positivos sobre el rendimiento.
- **Ningún estudio aísla las preguntas de Schraw.** El efecto medido corresponde a paquetes completos: planificar, monitorear y evaluar, más práctica guiada.

**Nivel de evidencia: moderado.** El enfoque general tiene evidencia sólida. La lista concreta de preguntas no tiene evidencia propia.

#### 2. Proceso y buenas prácticas

**Pasos**
1. **Detente antes de actuar.** Al empezar una sesión o una fase del PCRC, no le pidas a Claude que produzca nada todavía.
2. **Nombra la tarea.** ¿Qué tipo de tarea es? ¿Explorar, crear, decidir, implementar o verificar? ¿Un error, una función nueva o una especificación?
3. **Escribe el objetivo en una frase que puedas comprobar.** "Terminé cuando…".
4. **Lista qué necesitas.** Archivos, especificaciones, decisiones previas y lo que todavía no sabes.
5. **Elige la estrategia.** Por ejemplo, escribir primero los tests (pruebas automáticas del código) o escribir primero un borrador.
6. **Fija el presupuesto.** Tiempo, alcance y qué queda fuera.
7. **Deja el plan por escrito**, en el chat o en el issue (una tarea registrada en GitHub). Así podrás monitorear contra él.

La lista de Schraw junta información y estrategias en una sola pregunta. Aquí van en dos pasos separados, así que quedan cinco preguntas.

**Buenas prácticas**
- Usa siempre las mismas preguntas. El hábito importa más que la redacción.
- Pídele a Claude que te haga las preguntas al empezar. Respóndelas tú.
- Escribe lo que queda fuera. Así reconoces una bifurcación cuando aparece.
- Une el plan con planes "si… entonces". Ejemplo: "si paso de 30 minutos, paro y reviso".
- Ajusta el detalle al tamaño de la tarea. Un cambio de una línea no necesita las cinco preguntas.

**Errores comunes**
- Responder de memoria, sin escribir nada.
- Fijar un objetivo vago, como "mejorar el parser".
- Planificar una vez y no volver al plan.
- Dejar que Claude conteste por ti. Así el plan deja de ser tuyo.

#### 3. Ejemplo

**Caso: Ana va a especificar la validación de fechas de un formulario.**

Ana abre la sesión y escribe:

> "Antes de empezar, hazme las preguntas de planificación. No propongas nada todavía."

Claude pregunta y Ana responde:

- **¿Qué tipo de tarea es?** "Estoy en la fase *explorar* del PCRC. Todavía no quiero decidir el formato."
- **¿Cuál es el objetivo?** "Terminé cuando tenga una lista de 3 opciones de formato de fecha, cada una con sus pros y sus contras."
- **¿Qué información necesito?** "La especificación actual, `specs/forms.md`, y los errores de fecha del último mes."
- **¿Qué estrategia?** "Primero leemos los errores reales. Después comparamos opciones."
- **¿Tiempo y alcance?** "45 minutos. Las zonas horarias quedan fuera."

Claude resume el plan en cinco líneas y Ana lo fija al inicio del chat.

A los 20 minutos, Claude menciona que el backend guarda las fechas en UTC. Ana reconoce una **bifurcación**: está fuera del alcance que escribió. Le dice a Claude:

> "Zonas horarias está fuera del plan. Ábrela como bifurcación liviana y déjala *aparcada*."

Al minuto 40, Ana tiene las tres opciones. Revisa la frase "Terminé cuando…" y confirma que la cumplió. Pasa la bifurcación aparcada a **pesada**, como issue en GitHub, porque afecta a otra especificación.

**Resultado.** La sesión no se desvió hacia las zonas horarias. El objetivo escrito le dio a Ana un punto claro para monitorear y otro para evaluar. Además, la idea nueva quedó guardada y no se perdió.

#### Fuentes

- [Schraw (1998) Promoting general metacognitive awareness, Instructional Science 26 (DOI)](https://doi.org/10.1023/A:1003044231033)
- [Schraw (1998) Promoting general metacognitive awareness (registro LearnTechLib)](https://learntechlib.org/p/165105)
- [Metacognition techniques (OpenLearn, lista de Schraw)](https://www.open.edu/openlearncreate/mod/page/view.php?id=236090)
- [Metacognitive Awareness Inventory, Schraw y Dennison 1994 (CHIRAL)](https://chiral.chemedx.org/instrument/metacognitive-awareness-inventory)
- [de Boer et al. (2018) Long-term effects of metacognitive strategy instruction on student academic performance: a meta-analysis (DOI)](https://doi.org/10.1016/j.edurev.2018.03.002)
- [Dignath y Büttner (2008) Components of fostering self-regulated learning among students, Metacognition and Learning 3 (DOI)](https://doi.org/10.1007/s11409-008-9029-x)

### Criterio de terminado escrito

**Nivel de evidencia:** moderada

#### 1. Origen, teoría y evidencia

**Qué es.** Antes de empezar, escribir en pocas líneas cómo se verá el trabajo cuando esté terminado. Es una lista de condiciones que se pueden comprobar con un sí o un no.

**Dos raíces.**

- **Teoría del establecimiento de metas** (Locke y Latham, 1990 y 2002). Una meta específica y exigente rinde más que un "haz lo mejor que puedas". La meta orienta la atención, sostiene el esfuerzo y permite saber cuándo parar. En su revisión, Locke y Latham (2002) resumen metaanálisis anteriores. Un metaanálisis es un estudio que combina los resultados de muchos estudios para sacar una cifra común. Según esa revisión, las metas difíciles mejoran el rendimiento con tamaños de efecto entre d = 0,52 y 0,82. Las metas específicas y difíciles, frente a "haz lo mejor que puedas", dan entre d = 0,42 y 0,80. (El tamaño de efecto *d* mide la diferencia entre dos grupos: 0,2 es pequeño, 0,5 mediano y 0,8 grande.) El efecto baja cuando la meta supera la capacidad de la persona o cuando la persona deja de comprometerse con ella. Uno de los metaanálisis de esa época es el de Mento, Steel y Karren (1987), que reúne estudios de 1966 a 1984.
- **Definition of Done de Scrum** (Schwaber y Sutherland, Guía de Scrum 2020). Scrum es un marco de trabajo ágil para equipos de software. La Definition of Done (definición de terminado) es la descripción formal del estado que debe tener el trabajo para darlo por terminado. Si una tarea no la cumple, no se entrega ni se presenta, y vuelve a la lista de pendientes.

**Evidencia.**

- Metas específicas y difíciles en tareas de laboratorio y de trabajo: **fuerte**, con cientos de estudios.
- En cambio de conducta (salud, hábitos) el efecto es menor. Epton, Currie y Armitage (2017) reunieron 141 artículos con ensayos aleatorizados (384 tamaños de efecto, unas 16.500 personas) y hallaron d = 0,34, un efecto pequeño. Era mayor con metas difíciles, públicas o de grupo.
- Definition of Done en software: **débil**. Hay una encuesta a 137 profesionales ágiles (Kopczyńska y colegas, 2022). El 93 % la considera al menos valiosa, pero uno de cada dos proyectos tiene problemas con ella: criterios irrealizables, erróneos, no disponibles o que crecen sin control. No encontramos experimentos controlados.

**Nivel general: moderado.** La teoría de base es sólida. Su aplicación concreta al trabajo con Claude no se ha estudiado.

#### 2. Proceso y buenas prácticas

**Pasos**

1. Al empezar la sesión, en la fase planificar del PCM, escribir el objetivo en una frase.
2. Convertirlo en 3 a 6 condiciones verificables, es decir, que se puedan comprobar con un sí o un no ("pasan los tests", "la sección X define Y").
3. Agregar una línea "fuera de alcance" con lo que no se hará hoy.
4. Pedir a Claude que lea el criterio y señale condiciones ambiguas o imposibles.
5. Dejar el criterio a la vista: en el chat, en el issue o al inicio del archivo.
6. Al monitorear, comparar el avance con el criterio. Si aparece una bifurcación que no está en él, decidir si se aparca o se descarta.
7. En la fase evaluar, revisar condición por condición. Solo se termina cuando todas dicen sí.

**Buenas prácticas**

- Usar verbos que se puedan observar: "compila", "contiene", "rechaza". Evitar "mejorar" u "ordenar".
- Elegir metas exigentes pero alcanzables. Una meta imposible rompe el compromiso.
- Escribir el criterio antes de abrir el código, no a mitad de camino.
- Cambiar el criterio solo de forma explícita: tachar, escribir la versión nueva y anotar el motivo.

**Errores comunes**

- Criterio vago ("que quede bien"). Equivale a "haz lo mejor que puedas".
- Criterio que crece sin control: cada idea nueva entra como condición. Es mejor registrarla como bifurcación.
- Dar por terminado porque Claude dice "listo", sin revisar cada condición.
- Copiar una lista larga y genérica que nadie revisa.

#### 3. Ejemplo

Lucía escribe la especificación del módulo de facturas de una API. Un endpoint es una dirección de la API que recibe un tipo de petición. Lucía abre la sesión con Claude y, en la fase planificar del PCM, escribe:

> "Objetivo de hoy: especificar el endpoint `POST /facturas`.
> Terminado cuando:
> 1. Cada campo del cuerpo tiene tipo, si es obligatorio y un ejemplo.
> 2. Hay una tabla de errores con código HTTP y mensaje.
> 3. Hay al menos tres ejemplos de petición y respuesta, uno de ellos con error.
> 4. No queda ningún 'por definir' en la sección.
> Fuera de alcance: anulación de facturas e impuestos de otros países."

Luego pide: "Antes de empezar, dime qué condición te parece ambigua". Claude responde que la condición 2 no dice si incluye los errores de autenticación. Lucía la corrige: "2. Tabla de errores propios del endpoint; la autenticación ya está en la sección general".

Empieza el PCRC. En explorar y crear, Claude propone un campo `moneda` y pregunta si la factura admite varias monedas. Esa pregunta es una bifurcación. Lucía mira su criterio y ve que el multimoneda no está en él. Escribe: "Bifurcación liviana, aparcada: multimoneda. Por ahora la moneda es fija, EUR". Más tarde decide que el tema merece seguimiento y lo convierte en bifurcación pesada, con un issue en GitHub.

En verificar, ya en la fase evaluar del PCM, Lucía pide: "Revisa el criterio punto por punto y responde sí o no con evidencia". Claude contesta: 1 sí, 2 sí, 3 no (solo hay dos ejemplos), 4 sí. Lucía pide el tercer ejemplo con un error 422, lo revisa y cierra la sesión.

**Resultado:** una sección completa, con alcance acotado, un tema nuevo aparcado y registrado, y una decisión de "terminado" que Lucía puede justificar sin depender de su impresión.

#### Fuentes

- [Locke y Latham (2002). Building a practically useful theory of goal setting and task motivation. American Psychologist](https://goal-lab.psych.umn.edu/orgpsych/2020/readings/5.%20Motivation/Locke%20&%20Latham%20(2002).pdf)
- [Epton, Currie y Armitage (2017). Unique effects of setting goals on behavior change: systematic review and meta-analysis. Journal of Consulting and Clinical Psychology (PubMed)](https://pubmed.ncbi.nlm.nih.gov/29189034/)
- [Mento, Steel y Karren (1987). A meta-analytic study of the effects of goal setting on task performance: 1966-1984](https://zenodo.org/records/1258559)
- [Kopczyńska, Piechowiak, Ochodek y Nawrocki (2022). On the benefits and problems related to using Definition of Done: a survey study](https://arxiv.org/abs/2208.04003)
- [Scrum.org: the 2020 Scrum Guide, Definition of Done created by the Scrum Team](https://www.scrum.org/resources/blog/2020-scrum-guide-definition-done-created-scrum-team)
- [Scrum Guide 2020 (Schwaber y Sutherland)](https://scrumguides.org/scrum-guide.html)

### Premortem

**Nivel de evidencia:** débil

#### 1. Origen, teoría y evidencia

**Quién la creó.** Gary Klein es un psicólogo que estudia cómo deciden los expertos en situaciones reales. Publicó la técnica en Harvard Business Review (Klein, 2007, "Performing a Project Premortem"). Kahneman (2011) la difundió en *Pensar rápido, pensar despacio* como una defensa contra el exceso de optimismo.

**Teoría.** Un *postmortem* analiza por qué fracasó un proyecto cuando ya es tarde. El *premortem* hace lo mismo antes de empezar: el equipo supone que el proyecto **ya fracasó** y explica por qué. La técnica se apoya en la *retrospectiva prospectiva* (*prospective hindsight*). Consiste en explicar un hecho futuro como si ya hubiera ocurrido, con certeza, en vez de preguntar si podría ocurrir. Mitchell, Russo y Pennington (1989) estudiaron dos factores: si el hecho está en el pasado o en el futuro, y si es seguro o incierto. Lo que más cambió las explicaciones fue la **certeza**, no el tiempo verbal. Con un hecho seguro, la gente dio explicaciones más largas. Según Klein (2007), ese encuadre aumenta cerca de un 30 % las razones que se generan. Además, la técnica da permiso social para criticar: señalar un riesgo deja de ser deslealtad y pasa a ser la tarea.

**Evidencia.**
- Mitchell, Russo y Pennington (1989): el 30 % mide la **cantidad** de razones, no su calidad. Klein (2007) habla de mejorar la "capacidad de identificar correctamente las razones", y eso va más allá de lo que midió el estudio.
- Veinott, Klein y Wiggins (2010, actas del congreso ISCRAM): 178 estudiantes evaluaron un plan de cierre ante un brote de gripe H1N1, en cinco condiciones. El premortem bajó la confianza en el plan cerca del doble que listar pros y contras o listar solo contras. No encontré el artículo original. Los datos vienen de resúmenes secundarios (Klein, 2021; Collins).
- Gallop y Bischoff (2016): 101 gerentes de programa e ingenieros con experiencia, en equipos de 4 a 6 personas. Con premortem, los equipos encontraron más riesgos de calidad y propusieron mejores cambios al plan que con lluvia de ideas. Un panel de expertos juzgó la calidad. Solo encontré este estudio resumido por Collins. Una tesis doctoral de la Universidad George Washington compara las mismas dos técnicas, pero no pude confirmar que sea de estos autores.
- Peabody (2017, tesis de maestría): con 52 cadetes del ejército, los equipos con premortem cometieron menos faltas en ejercicios de campo y se aferraron menos a una sola idea, sin tardar más. En un segundo experimento (72 personas) no hubo diferencia en la cantidad de razones frente al método del peor caso. En un tercero (82 personas), el premortem sí generó más razones que ese método.

**Nivel de evidencia: débil.** Los resultados apuntan en la misma dirección. Pero son pocos estudios y pequeños, y varios no pasaron por revisión de una revista científica. No encontré metaanálisis (estudios que combinan los resultados de muchos otros). Los resúmenes disponibles tampoco dan tamaños de efecto (cifras que dicen cuánto cambia el resultado). Es una práctica razonable con apoyo experimental limitado.

#### 2. Proceso y buenas prácticas

**Pasos**

1. **Tener un plan concreto.** El premortem revisa un plan. Sobre una idea vaga no sirve.
2. **Fijar el fracaso como un hecho seguro.** "Pasaron tres meses. El proyecto fracasó de forma clara." Lo que importa es la certeza. Por eso conviene hablar en pasado y no en condicional.
3. **Generar causas en silencio.** Cada persona escribe por su cuenta, unos minutos, todas las razones del fracaso. Con Claude, la persona escribe su lista antes de leer la de Claude.
4. **Juntar las causas por turnos.** Una causa por vez, hasta agotar las listas.
5. **Priorizar.** Elegir las dos o tres causas más probables o más graves.
6. **Cambiar el plan.** Para cada causa elegida, definir una acción concreta o una señal de alarma ("si pasa X, entonces hago Y").
7. **Guardar el resultado** junto al plan, para revisarlo en las fases monitorear y evaluar.

**Buenas prácticas y errores comunes**

- Presentar el fracaso como seguro. "Fracasó: ¿por qué?" genera más razones que "¿qué podría salir mal?".
- Pensar por separado antes de compartir. Si Claude responde primero, la persona puede quedarse atada a su lista.
- Buscar causas internas (decisiones propias), no solo mala suerte externa.
- Limitar el tiempo. Para un plan pequeño suelen bastar 15 a 30 minutos. Es una recomendación práctica, no un dato de estudio.
- Error: quedarse en la lista. Sin cambios al plan, el ejercicio no sirve.
- Error: caer en el pesimismo general. El objetivo es corregir el plan, no abandonarlo.
- Error: hacerlo tarde, cuando el plan ya no se puede cambiar.

#### 3. Ejemplo

**Caso: especificación de un módulo de permisos**

Lucía termina de explorar con Claude cómo especificar el módulo de permisos de su aplicación. En la fase **decidir** del PCRC elige un modelo por roles. Antes de **implementar**, entra en la fase **planificar** del PCM y propone un premortem.

**1. Fijar el fracaso.** Lucía escribe:

> "Supongamos que estamos en febrero. La especificación de permisos fracasó: el equipo la abandonó y cada uno programó los permisos a su manera. Antes de que me des tus razones, escribo las mías."

**2. Su lista, en silencio:**
- Los roles no alcanzaron para los clientes con varias sucursales.
- La especificación era tan larga que nadie la leyó.

**3. Pide la lista de Claude:**

> "Ahora dame tus razones del fracaso. Escríbelas en pasado, como hechos."

Claude agrega:
- No había ejemplos de casos límite, así que cada desarrollador interpretó las reglas a su modo.
- Nadie definió qué pasa con los permisos de un usuario dado de baja.
- La especificación no decía quién podía cambiar los roles.

**4. Priorizar y cambiar el plan.** Lucía elige tres causas:

> "Me quedo con sucursales, casos límite y bajas. Para cada una, una acción."

El plan cambia así:
- **Sucursales:** agregar un ejemplo con un cliente de tres sucursales antes de cerrar el modelo.
- **Casos límite:** cada regla lleva al menos un ejemplo de entrada y resultado.
- **Bajas:** registrar el tema como issue (paso 5).
- **Señal de alarma:** "si al escribir los ejemplos aparece un caso que los roles no cubren, entonces vuelvo a la fase decidir".

**5. Bifurcaciones.** La causa "quién puede cambiar los roles" abre un tema nuevo. Lucía lo anota como **bifurcación liviana**, en estado *aparcado*: "Lo retomamos al terminar los ejemplos." La causa de las bajas toca también el módulo de facturación. Por eso la convierte en **bifurcación pesada**, es decir, en un issue (una tarea registrada en GitHub):

> "Abre un issue: definir qué pasa con permisos y facturas al dar de baja a un usuario."

**Resultado.** En 20 minutos, la especificación ganó tres cambios concretos, una señal de alarma y un issue sobre un tema que, si no, podía aparecer recién en producción. Días después, Lucía escribe el ejemplo de las tres sucursales y encuentra un caso que los roles no cubren. En la fase **monitorear** detecta que se cumplió la señal de alarma. En la fase **controlar** aplica el plan: vuelve a la fase **decidir** y agrega un rol por sucursal. Todo esto ocurre antes de escribir código.

#### Fuentes

- [Klein (2007). Performing a Project Premortem. Harvard Business Review](https://hbr.org/2007/09/performing-a-project-premortem)
- [Mitchell, Russo y Pennington (1989). Back to the future: Temporal perspective in the explanation of events. Journal of Behavioral Decision Making 2(1), 25-38](https://onlinelibrary.wiley.com/doi/10.1002/bdm.3960020103)
- [Peabody (2017). Improving Planning: Quantitative Evaluation of the Premortem Technique in Field and Laboratory Settings (tesis de maestría, Michigan Tech)](https://digitalcommons.mtu.edu/etdr/374)
- [Collins, J. The premortem (apuntes de curso; resume Mitchell et al. 1989, Veinott et al. 2010 y Gallop y Bischoff 2016)](https://corporate.jcx.au/premortem)
- [Klein (2021). The Pre-Mortem Method. Psychology Today (cita a Veinott, Klein y Wiggins 2010)](https://www.psychologytoday.com/ie/blog/seeing-what-others-dont/202101/the-pre-mortem-method)
- [How to Catch a Black Swan: Measuring the Benefits of the Premortem Technique for Risk Identification (tesis doctoral, Universidad George Washington; autor no confirmado)](https://scholarspace.library.gwu.edu/concern/gw_etds/5712m6681)

### Timeboxing

**Nivel de evidencia:** débil

#### 1. Origen, teoría y evidencia

**Qué es.** Un *timebox* (caja de tiempo) es un plazo fijo que se asigna a una tarea antes de empezarla. Cuando el plazo se acaba, la persona se detiene y decide: entregar lo que hay, recortar el alcance (lo que la tarea debe incluir) o abrir otra caja. El tiempo es fijo; el alcance cambia.

**Origen.** La idea nació en el desarrollo de software. La Agile Alliance la ubica en 1988, como pieza central del método *Rapid Iterative Production Prototyping* de Scott Schultz. Martin (1991) le dedicó un capítulo en su libro *Rapid Application Development*. Después la adoptaron DSDM (método de desarrollo de sistemas dinámicos, cuyo consorcio se fundó en 1994) y Scrum (un marco ágil de trabajo en ciclos cortos), donde los eventos tienen duración máxima. Zao-Sanders (2018) la popularizó como técnica personal en Harvard Business Review.

**Teoría.** Hay dos ideas detrás:
- **Ley de Parkinson** (Parkinson, 1955, en *The Economist*): "el trabajo se expande hasta llenar el tiempo disponible". Es una observación satírica, no un resultado experimental. Los textos sobre timeboxing la citan como el problema que la técnica busca contrarrestar.
- **Falacia de planificación** (Kahneman y Tversky, 1979): la tendencia a subestimar cuánto tardará el propio trabajo. Buehler, Griffin y Ross (1994) la midieron: 37 estudiantes estimaron en promedio 33,9 días para su tesis y tardaron 55,5. Solo cerca del 30 % terminó en el plazo estimado. Un plazo fijo con punto de control obliga a ver el desvío pronto.

**Evidencia.**
- No hay estudios revisados por pares que prueben el timeboxing en sí. En internet circulan cifras de éxito sin fuente verificable. La frase "duplica la productividad" viene de Zao-Sanders, que luego admitió que era "una corazonada, no rigor científico".
- La gestión del tiempo en general sí tiene respaldo. El metaanálisis (estudio que combina muchos estudios) de Aeon, Faber y Panaccio (2021), con 158 estudios y 53 957 participantes, encontró una relación moderada con el desempeño laboral (r ≈ 0,25) y con menos malestar psicológico (r ≈ −0,36). Son correlaciones: no prueban causa y no aíslan el timeboxing.
- Ariely y Wertenbroch (2002) mostraron que los plazos ayudan a reducir la postergación. Una réplica de Hyndman y Bisin (2026) repitió su estudio 2 y no reprodujo el resultado: los plazos impuestos y espaciados casi no cambiaron el desempeño.

**Nivel de evidencia: débil.** El mecanismo de fondo (la falacia de planificación) está bien probado; la técnica concreta es sobre todo práctica profesional.

#### 2. Proceso y buenas prácticas

**Pasos**
1. Define el resultado de la caja en una frase: qué cuenta como "hecho".
2. Asigna una duración fija y corta (de 25 a 90 minutos para trabajo individual).
3. Fija un punto de control a mitad de la caja: ¿voy bien?
4. Pon un temporizador. Claude no mide el tiempo por su cuenta: el aviso lo das tú.
5. Trabaja solo en ese resultado. Lo que aparezca fuera de él es una bifurcación: anótala y apárcala.
6. Al sonar el final, detente de verdad.
7. Decide: entregar, recortar alcance o abrir una nueva caja con objetivo propio.
8. Compara lo estimado con lo real. Ese dato mejora tus próximas estimaciones.

**Buenas prácticas**
- Que el objetivo sea un entregable, no una actividad ("lista de 5 requisitos", no "trabajar en requisitos").
- Usa cajas para tareas sin fin natural, como explorar o investigar.
- Deja un margen entre cajas para imprevistos.

**Errores comunes**
- Extender la caja "solo diez minutos más". Eso anula la técnica.
- Medir el éxito por terminar todo. El éxito es decidir con información al cierre.
- Usar cajas tan largas que no obligan a revisar nada.
- Planificar cada minuto del día: el plan se rompe y se abandona.

#### 3. Ejemplo

Lucía escribe la especificación de un módulo de permisos con Claude. Sabe que la fase **explorar** del PCRC tiende a no terminar nunca.

**Planificar (PCM).** Pone un temporizador de 45 minutos con un aviso a los 20 y escribe:

> "Claude, vamos a explorar modelos de permisos durante 45 minutos. Resultado: una tabla con 3 opciones y sus pros y contras. Cuando te diga 'control', revisamos si vamos bien. Cuando diga 'fin', paramos aunque falte algo."

**Monitorear.** A los 20 minutos suena el aviso y Lucía escribe "control". Claude resume: llevan dos opciones, roles fijos y RBAC (control de acceso basado en roles). Lucía responde:

> "Vamos bien. Falta la tercera, ABAC (permisos según atributos del usuario o del recurso)."

**Bifurcación.** Mientras comparan, Claude menciona que el sistema actual guarda roles en dos tablas distintas. Lucía la trata como bifurcación liviana:

> "Eso es otro tema. Apárcalo, no lo resolvemos ahora."

La bifurcación queda en estado *aparcado*.

**Controlar.** A los 45 minutos suena el temporizador. La tabla tiene tres opciones, pero ABAC solo tiene pros. Lucía decide:

> "Fin. ABAC queda a medias. Abro una caja de 15 minutos solo para sus contras y después pasamos a **decidir**."

**Evaluar.** Al cerrar, revisa la bifurcación aparcada. Ve que afecta la migración de datos, así que la convierte en bifurcación pesada:

> "Claude, propón una issue en GitHub para las dos tablas de roles."

**Resultado.** En una hora tiene una tabla completa, una issue abierta y un dato útil: había estimado 45 minutos y necesitó 60. La próxima exploración la planifica con más margen.

#### Fuentes

- [Agile Alliance Glossary: Timebox](https://agilealliance.org/glossary/timebox)
- [Buehler, Griffin y Ross (1994). Exploring the planning fallacy. JPSP 67](https://bear.warrington.ufl.edu/brenner/mar7588/Papers/buehler-et-al-1994.pdf)
- [Planning fallacy (Wikipedia, apoyo)](https://en.wikipedia.org/wiki/Planning_fallacy)
- [Timeboxing (Wikipedia, apoyo: DSDM y Scrum)](https://en.wikipedia.org/wiki/Timeboxing)
- [Dynamic systems development method (Wikipedia, apoyo: consorcio fundado en 1994)](https://en.wikipedia.org/wiki/Dynamic_systems_development_method)
- [Aeon, Faber y Panaccio (2021). Does time management work? A meta-analysis. PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0245066)
- [Ariely y Wertenbroch (2002). Procrastination, deadlines, and performance. Psychological Science](https://scholars.duke.edu/publication/810365)
- [Hyndman y Bisin (2026). Replication of Procrastination, Deadlines, and Performance. Psychological Science 37(8)](https://www.psychologicalscience.org/journals/psychological-science/09567976261460772/)
- [Zao-Sanders (2024): Timeboxing doubles productivity (blog, solo apoyo)](https://marczaosanders.substack.com/p/timeboxing-doubles-productivity)

## Monitorear

### Pensar en voz alta

**Nivel de evidencia:** moderada

#### 1. Origen, teoría y evidencia

**Quién la investigó.** Ericsson y Simon (1980) publicaron "Verbal Reports as Data" en *Psychological Review*. Luego la desarrollaron en el libro *Protocol Analysis: Verbal Reports as Data* (1984; edición revisada de 1993, MIT Press). El análisis de protocolos es el método de grabar a una persona que piensa en voz alta mientras resuelve una tarea y luego estudiar lo que dijo.

**Teoría.** Según Ericsson y Simon (1980), una persona puede decir en voz alta lo que tiene en la memoria de trabajo (la información que usa en ese momento) sin cambiar su forma de pensar. La condición es que solo diga lo que ya piensa. Si se le pide explicar o justificar, agrega trabajo nuevo y su pensamiento cambia.

Esa diferencia separa dos usos:
- **Pensar en voz alta puro**: narrar lo que uno piensa, sin explicarlo. Sirve para *ver* el pensamiento, es decir, para monitorear.
- **Autoexplicación**: explicarse a uno mismo por qué algo es así. Chi y colegas la estudiaron (Chi et al., 1989; Chi, de Leeuw, Chiu y LaVancher, 1994). Esta sí cambia el pensamiento, y lo mejora.

**Evidencia.** Un metaanálisis es un estudio que junta los resultados de muchos estudios para calcular un efecto promedio.
- Fox, Ericsson y Best (2011), metaanálisis de 94 estudios con casi 3.500 personas, en *Psychological Bulletin*. Pensar en voz alta puro no cambia el rendimiento: el efecto es casi cero (r = −0,03; r mide la fuerza de una relación, y 0 significa ninguna). Pedir que se describan o expliquen los pasos sí lo cambia, por lo general para mejor. Todas las formas de verbalizar alargan la tarea.
- Double y Birney (2019) revisan ese resultado y advierten que el efecto puede depender de la tarea.
- Chi et al. (1994): 14 alumnos de octavo grado se autoexplicaron, línea por línea, un texto sobre el sistema circulatorio. Aprendieron más que un grupo control (el grupo que no recibe la técnica) de 10 alumnos que leyó el texto dos veces. La muestra es pequeña.
- Bisra et al. (2018), metaanálisis de 64 informes en *Educational Psychology Review*: pedir autoexplicaciones tiene un efecto medio (g = 0,55; g mide la diferencia entre grupos, y 0,5 se considera un efecto medio).

**Nivel de evidencia.** La evidencia es **fuerte** en dos puntos: narrar no distorsiona el pensamiento y autoexplicarse mejora el aprendizaje. Pero no hay estudios conocidos que midan pensar en voz alta como herramienta para monitorear al trabajar con un asistente de IA. Ese uso es una aplicación razonable de la evidencia, no un resultado probado. Por eso, para el uso que propone este documento, el nivel es **moderado**.

#### 2. Proceso y buenas prácticas

**Pasos**

1. **Elegir el momento.** Úsala en tramos donde es fácil perderse: depurar, decidir entre opciones, revisar una especificación.
2. **Narrar, no explicar.** Escribe o di lo que haces y lo que esperas: "Ahora miro X porque espero Y". Frases cortas, en presente.
3. **Marcar las señales de monitoreo.** Di en voz alta cuándo algo no encaja: "esto no lo esperaba", "no sé por qué funciona", "me estoy desviando".
4. **Pasar a explicar a propósito.** Cuando aparezca una señal, cambia a autoexplicación: "¿Por qué pasa esto?". Ahí está el beneficio para aprender.
5. **Convertir la señal en control.** Decide: seguir, cambiar de enfoque o registrar una bifurcación.
6. **Cerrar con una frase.** Resume dónde estás y qué sigue. Esa frase sirve luego para evaluar.

**Buenas prácticas y errores comunes**

- Al escribirle a Claude, tu narración es el registro. Pídele que te avise cuando tus frases muestren una contradicción o una duda sin resolver.
- No narres todo el día: cansa y alarga la tarea (Fox et al., 2011). Úsala en tramos cortos.
- Error: confundir narrar con justificarte ante otro. Si buscas quedar bien, dejas de ver lo que piensas.
- Error: narrar sin actuar. Una señal que no lleva a una decisión no sirve para monitorear.
- Presta atención a las frases "no sé por qué": muestran dónde falta comprensión.

#### 3. Ejemplo

**Contexto.** Laura escribe con Claude la especificación de un módulo de permisos. Está en la fase *verificar* del PCRC (proceso cíclico de resolución creativa). En el PCM (proceso cíclico metacognitivo) está en *monitorear*.

**Narración (lo que Laura escribe en el chat):**

> "Pienso en voz alta. Reviso la regla R7: un editor puede borrar documentos de su equipo. Ahora miro el caso de un editor que cambia de equipo. Espero que pierda los permisos del equipo viejo... No, la especificación no dice nada de eso. Esto no lo esperaba."

Señal de monitoreo: "esto no lo esperaba". Laura pasa a autoexplicarse:

> "¿Por qué falta? Porque R7 habla del equipo, pero no de *cuándo* se evalúa la pertenencia. Si se evalúa al crear el documento, el editor que se fue sigue pudiendo borrar. Eso es un hueco."

Mientras narra aparece otra idea:

> "También me pregunto si hace falta un historial de cambios de equipo. Eso no es de esta fase."

Laura lo marca como **bifurcación liviana**, estado *aparcado*: "Claude, aparca 'historial de cambios de equipo'". Luego decide (fase *controlar*):

> "Sigo con R7. Claude, propón dos redacciones: una que evalúe la pertenencia en el momento de borrar y otra al crear el documento."

Claude propone ambas. Laura elige la primera y cierra:

> "Resumen: R7 queda con la pertenencia evaluada al borrar. Hay una bifurcación aparcada. Lo siguiente es revisar R8."

**Resultado.** Laura encontró un hueco que una lectura en silencio podía pasar por alto. Lo encontró porque escribió lo que esperaba y vio que no se cumplía. La bifurcación quedó registrada sin cortar la fase. Al final de la sesión decide si la convierte en **bifurcación pesada** (un issue en GitHub) o la descarta.

#### Fuentes

- [Ericsson y Simon (1980). Verbal Reports as Data. Psychological Review, 87(3), 215-251 (DOI)](https://doi.org/10.1037/0033-295X.87.3.215)
- [Ericsson y Simon (1993). Protocol Analysis: Verbal Reports as Data, edición revisada (MIT Press)](https://mitpressbookstore.mit.edu/book/9780262550239)
- [Fox, Ericsson y Best (2011). Do procedures for verbal reporting of thinking have to be reactive? A meta-analysis and recommendations for best reporting methods. Psychological Bulletin, 137(2), 316-344 (material suplementario de la APA)](https://supp.apa.org/psycarticles/supplemental/a0021663/a0021663_supp.html)
- [Double y Birney (2019). Reactivity to Measures of Metacognition. Frontiers in Psychology, 10:2755](https://pmc.ncbi.nlm.nih.gov/articles/PMC6908488/)
- [Chi, de Leeuw, Chiu y LaVancher (1994). Eliciting self-explanations improves understanding. Cognitive Science, 18, 439-477](https://education.asu.edu/lcl/publications/chi-m-t-h-de-leeuw-n-chiu-m-h-lavancher-c-1994-eliciting-self-explanations)
- [Bisra, Liu, Nesbit, Salimi y Winne (2018). Inducing Self-Explanation: a Meta-Analysis. Educational Psychology Review, 30, 703-725 (DOI)](https://doi.org/10.1007/s10648-018-9434-x)

### Preguntas de monitoreo

**Nivel de evidencia:** moderada

#### 1. Origen, teoría y evidencia

**Quién la investigó.** Flavell (1979) creó el término *metacognición* y habló de "monitoreo cognitivo": vigilar el propio pensamiento. Brown (1987) separó dos partes: *saber* sobre el propio pensamiento y *regular* ese pensamiento. Schraw y Moshman (1995) dividieron la regulación en tres actividades: planificar, monitorear y evaluar. Schraw (1998, *Instructional Science* 26) propuso una lista de chequeo con preguntas fijas para cada actividad. Las de monitoreo son: ¿entiendo con claridad lo que estoy haciendo?, ¿la tarea tiene sentido?, ¿me acerco a mis objetivos?, ¿necesito hacer cambios?

**Teoría.** Monitorear es vigilar el propio avance mientras se trabaja. Una pregunta fija funciona como una alarma. Corta el trabajo en el nivel cognitivo (pensar sobre el problema) y obliga a subir al nivel metacognitivo (pensar sobre el propio pensamiento y dirigirlo). La idea es que, sin esa pausa, es fácil seguir con la misma estrategia aunque no funcione.

**Estudios concretos.**
- King (1991, *Journal of Educational Psychology* 83): 46 estudiantes de quinto grado resolvieron problemas en computadora, en parejas. Hubo tres grupos: preguntas estratégicas guiadas, preguntas entre compañeros sin guía, y sin entrenamiento. Según el resumen del artículo, al grupo con preguntas guiadas le fue mejor que a los otros dos.
- Mevarech y Kramarski (1997, *American Educational Research Journal* 34) crearon IMPROVE, un método para enseñar matemática. Usa tres tipos de autopregunta: comprensión (¿de qué trata el problema?), conexión (¿en qué se parece a otros que ya resolví?) y estrategia (¿qué método sirve y por qué?). Trabajos posteriores de los mismos autores agregaron preguntas de reflexión (¿tiene sentido el resultado?). En dos estudios con estudiantes de séptimo grado, el grupo IMPROVE superó al grupo de control. Los propios autores señalan un límite: aplicaron a la vez preguntas, trabajo en grupo y retroalimentación, así que no se puede aislar el efecto de las preguntas.
- Kramarski y Mevarech (2003, *American Educational Research Journal* 40) separaron dos factores con 384 estudiantes de octavo grado: entrenamiento metacognitivo (las autopreguntas de IMPROVE) y trabajo en grupo. Los grupos con entrenamiento metacognitivo superaron a los grupos sin él en construcción de gráficos (una tarea de transferencia, es decir, aplicar lo aprendido a algo nuevo) y en conocimiento metacognitivo. El mejor grupo combinó entrenamiento metacognitivo y trabajo en grupo.
- Revisiones amplias: el metaanálisis (estudio que combina los resultados de muchos estudios) de Dignath, Büttner y Langfeldt (2008) encontró efectos positivos del entrenamiento en autorregulación en estudiantes de primaria. La Education Endowment Foundation estima unos 8 meses de progreso extra por año escolar para la metacognición en general (actualización de mayo de 2025; antes estimaba 7). Esa cifra no corresponde a las preguntas solas.

**Nivel de evidencia: moderada.** Los programas que enseñan autopreguntas tienen buen respaldo en estudiantes. Casi siempre combinan las preguntas con otras técnicas, y no encontré un tamaño de efecto para las preguntas solas. Tampoco encontré estudios con adultos que trabajen con un asistente de IA. Pasar estos resultados a ese contexto es una extrapolación.

#### 2. Proceso y buenas prácticas

**Pasos**
1. **Elegir pocas preguntas fijas** (3 o 4). Partir de Schraw o de IMPROVE y adaptarlas a la tarea.
2. **Definir cuándo se hacen.** Usar puntos de control concretos: al terminar cada fase del PCRC, cada 30 minutos o después de cada respuesta larga de Claude.
3. **Responder por escrito y en una línea.** Así la respuesta queda a la vista y se puede revisar.
4. **Comparar con el plan.** Contrastar la respuesta con el objetivo que se fijó al planificar.
5. **Pasar a controlar si hay desvío.** Si una respuesta es "no" o "no sé", decidir: cambiar de estrategia, volver a una fase anterior o aparcar una bifurcación.

**Buenas prácticas**
- Hacer preguntas que piden evidencia ("¿qué prueba tengo de que esto funciona?") y no preguntas de sí o no que se contestan en automático.
- Pedir a Claude que haga las preguntas en los puntos de control. Así no dependen de que uno se acuerde.
- Incluir siempre una pregunta sobre el rumbo ("¿sigo en el objetivo o me desvié?"). Ayuda a detectar bifurcaciones.
- Cambiar la redacción de las preguntas cada tanto si empiezan a contestarse en automático. Esto es un consejo práctico, no un resultado de los estudios.

**Errores comunes**
- Preguntar y no actuar: el monitoreo sin control no cambia nada.
- Usar demasiadas preguntas: la persona deja de hacerlas.
- Confiar en la sensación de entender. Hay que verificarla con algo concreto: una prueba, un ejemplo, una explicación con palabras propias.

#### 3. Ejemplo

**Caso: Lucía especifica un módulo de permisos con Claude.**

Al planificar, Lucía fija el objetivo: "Especificar los roles y permisos del módulo de facturas. Sin código todavía." Luego le escribe a Claude:

> "Al cerrar cada fase del PCRC y después de cada respuesta larga tuya, hazme estas tres preguntas: 1) ¿Sigo en el objetivo? 2) ¿Qué evidencia tengo de que lo hecho está bien? 3) ¿Necesito cambiar algo?"

**Punto de control 1 (fin de explorar).** Claude hace las preguntas. Lucía responde:

> "1) Sí. 2) Tengo cuatro roles, pero no revisé el caso de un contador externo. 3) Volver a explorar diez minutos ese caso."

Se queda en explorar y agrega un quinto rol: el contador externo, que puede ver facturas pero no editarlas.

**Punto de control 2 (en medio de crear, tras una respuesta larga).** Claude escribió una respuesta larga que propone cómo guardar los permisos en la base de datos. Hace las preguntas. Lucía responde:

> "1) No. Me fui al diseño de la base de datos y eso no es especificar. 2) Ninguna: eso no estaba en el plan. 3) Abro una bifurcación liviana 'esquema de permisos' y la dejo aparcada."

Como la idea servirá más adelante, decide pasarla a pesada. Claude propone una issue en GitHub con el título "Diseñar esquema de permisos en la base de datos", y Lucía la aprueba. Luego vuelve a crear.

**Punto de control 3 (fin de verificar).** Lucía responde:

> "1) Sí. 2) Recorrí los cinco roles con tres casos cada uno y no quedan huecos. 3) Nada."

**Resultado.** La especificación queda completa y dentro del objetivo. El desvío al diseño de la base de datos se detecta en minutos y no al final. La idea no se pierde: queda guardada como issue.

#### Fuentes

- [Schraw (1998). Promoting general metacognitive awareness. Instructional Science 26, 113-125](https://learntechlib.org/p/165105)
- [Metacognition techniques (OpenLearn, lista de Schraw)](https://www.open.edu/openlearncreate/mod/page/view.php?id=236090)
- [Mevarech y Kramarski (1997). IMPROVE: A multidimensional method for teaching mathematics in heterogeneous classrooms. AERJ 34, 365-394](https://education.biu.ac.il/en/node/266)
- [Kramarski y Mevarech (2003). Enhancing mathematical reasoning in the classroom: the effects of cooperative learning and metacognitive training. AERJ 40(1), 281-310](https://education.biu.ac.il/en/node/260)
- [King (1991). Effects of training in strategic questioning on children's problem-solving performance. JEP 83(3) (DOI 10.1037/0022-0663.83.3.307)](https://synapsesocial.com/papers/W2000425207)
- [EEF Teaching and Learning Toolkit: Metacognition and self-regulation (apéndice técnico)](https://educationendowmentfoundation.org.uk/education-evidence/teaching-learning-toolkit/metacognition-and-self-regulation/technical-appendix)
- [EEF: actualización de mayo de 2025 de diez líneas del Toolkit (metacognición de +7 a +8 meses)](https://educationendowmentfoundation.org.uk/news/updates-ten-strands-toolkit)
- [Comentario sobre IMPROVE y sus límites (blog, solo como apoyo)](https://www.ollielovell.com/?p=615)

### Juicios de confianza

**Nivel de evidencia:** moderada

#### 1. Origen, teoría y evidencia

**Quién la investigó.** Un juicio de confianza es una estimación propia de cuánto sabes o de qué tan bien hiciste algo. Por ejemplo: "estoy 70 % seguro de que esto es correcto". Hart (1965) hizo uno de los primeros estudios experimentales del *sentimiento de saber* (feeling of knowing): la sensación de saber una respuesta que no logras recordar. Las personas predijeron qué respuestas reconocerían después, y acertaron más que el azar. Después, los investigadores estudiaron los *juicios de aprendizaje* (judgments of learning): predecir si recordarás algo en una prueba futura.

**Teoría.** Nelson y Narens (1990) propusieron un modelo de dos niveles. El nivel cognitivo hace la tarea. El nivel metacognitivo la observa y la dirige. La información que sube del nivel cognitivo al metacognitivo es *monitorear*. La que baja es *controlar*. Los juicios de confianza son una herramienta central de monitorear: sin ellos, controlar no tiene datos. Koriat (1997) explicó de dónde salen esos juicios. No leemos la memoria directamente. Inferimos a partir de pistas, por ejemplo la dificultad del material o la fluidez (la facilidad con que algo se procesa). Por eso los juicios pueden fallar.

Dos medidas de calidad:
- **Calibración**: si tu confianza coincide con tus aciertos. Si dices 80 % y aciertas 80 %, estás calibrado.
- **Resolución**: si distingues lo que sabes de lo que no sabes.

**Evidencia.** Dos términos: un *metaanálisis* combina los resultados de muchos estudios. El *tamaño de efecto g* mide cuánto cambia un resultado; como guía, 0,2 es pequeño, 0,5 mediano y 0,8 grande.
- Lichtenstein, Fischhoff y Phillips (1982) revisaron los estudios de calibración. En tareas de dificultad media o alta, las personas suelen tener *sobreconfianza*: creen que saben más de lo que saben. Con tareas fáciles pasa lo contrario: *subconfianza*.
- Koriat, Sheffer y Ma'ayan (2002): en juicios de aprendizaje, la sobreconfianza leve del primer intento se vuelve subconfianza cuando se practica varias veces. La sobreconfianza no es universal.
- Rhodes y Tauber (2011), metaanálisis: los juicios hechos *con demora*, un rato después de estudiar, distinguen mucho mejor lo que se recordará que los inmediatos (g = 0,93, 112 tamaños de efecto). El efecto sobre lo recordado fue pequeño (g = 0,08, 98 tamaños de efecto).
- Thiede, Anderson y Therriault (2003): quienes escribieron palabras clave de un texto un rato después de leerlo juzgaron mejor su comprensión. Por eso eligieron mejor qué repasar y comprendieron más en la prueba. Monitorear con precisión ayuda a controlar.
- Double, Birney y Walker (2018), metaanálisis: hacer el juicio no cambia la memoria por sí solo (g = 0,05, no significativo). Sí la mejora un poco con listas de palabras y con pares de palabras relacionadas.

**Nivel de evidencia: moderado.** La evidencia es fuerte en que los juicios se pueden medir, en que suelen fallar de forma sistemática y en que la demora mejora la precisión. Es moderada en que mejorar la precisión mejora el resultado. Casi toda viene de laboratorio, con listas de palabras y textos. No encontré estudios en trabajo de software ni con asistentes de IA.

#### 2. Proceso y buenas prácticas

**Proceso**
1. Elige qué juzgar: una pieza concreta (un requisito, una función, un concepto).
2. Antes de verificar, escribe tu confianza en número (0 a 100 %) y una razón breve.
3. Si puedes, juzga con demora: deja pasar un rato o cambia de tarea antes de juzgar.
4. Verifica contra algo externo: pruebas, una revisión de Claude, una pregunta de recuperación (una pregunta que respondes sin mirar).
5. Compara confianza y resultado. Anota la diferencia.
6. Pasa a controlar: lo de baja confianza o mal calibrado recibe más atención.

**Buenas prácticas**
- Usa números, no "más o menos". Un número se puede comparar después.
- Juzga piezas pequeñas. Un juicio global ("el proyecto va bien") no sirve para decidir.
- Juzga si puedes *recuperar* o *explicar*, no si el texto te resulta familiar.
- Lleva un registro breve. Con muchos juicios a lo largo del tiempo ves tu calibración real.

**Errores comunes**
- Juzgar justo después de leer: la fluidez infla la confianza.
- Confundir "Claude lo explicó claro" con "yo lo entiendo".
- Sacar conclusiones de pocos juicios. Cinco juicios dan una pista, no una medida.
- Juzgar y no hacer nada con el juicio. Monitorear sin controlar no cambia el resultado.

#### 3. Ejemplo

Lucía escribe con Claude la especificación de un módulo de pagos y su código. Está en la fase **implementar** del PCRC. Claude acaba de generar el código para cinco requisitos (R1 a R5).

Antes de ejecutar las pruebas, Lucía va a buscar un café. Diez minutos después (juicio con demora) escribe:

> "Antes de ver las pruebas, mi confianza: R1 90 %, R2 85 %, R3 60 % (no sé si cubre reembolsos parciales), R4 80 %, R5 40 % (la regla de redondeo no me queda clara). Claude, no me digas todavía si están bien. Hazme una pregunta sobre R3 y otra sobre R5 que yo deba responder sin mirar el código."

Claude pregunta: "¿Qué pasa si se reembolsa el 30 % de un pago en dos cuotas?". Lucía no sabe responder. Baja R3 a 40 %.

Pasa a la fase **verificar** y ejecuta las pruebas. Resultado:
- R1, R2 y R5 pasan.
- R3 falla con reembolsos parciales.
- R4 falla con montos en cero.

Lucía compara:

> "R4 lo tenía en 80 % y falló: sobreconfianza. R5 en 40 % y pasó: subconfianza. Me fié de que R4 'se veía simple'."

Anota los cinco juicios y sus resultados en su registro. Cinco juicios no miden su calibración, pero se suman a los de otras sesiones.

Ahora **controla**. Pide a Claude corregir R3 y R4. Agrega una regla para la próxima sesión: "Si un requisito toca montos, entonces escribo un caso con cero antes de juzgar".

Durante la revisión aparece una pregunta nueva: ¿qué hacer con monedas sin decimales? Es una **bifurcación**. Como afecta a todo el módulo, Lucía la vuelve **pesada**: "Claude, abre una issue con esto, no lo resolvamos ahora".

**Resultado**: Lucía encontró dos errores antes de integrar. Tiene una pista de que la sencillez aparente le infla la confianza, y su registro dirá si se repite. Además vio que responder una pregunta concreta le dio un juicio más realista que releer el código.

#### Fuentes

- [Hart (1965) y Nelson y Narens (1990), resumen en Metamemory (Wikipedia)](https://en.wikipedia.org/wiki/Metamemory)
- [Dunlosky y Bjork (2008), The integrated nature of metamemory and memory, en Handbook of metamemory and memory](https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/07/Dunlosky_RBjork_2008b.pdf)
- [Koriat (1997), Monitoring one's own knowledge during study: A cue-utilization approach to judgments of learning](https://newiipdm.haifa.ac.il/wp-content/uploads/2015/05/1997-Koriat-CueUtilization-JEPG.pdf)
- [Lichtenstein, Fischhoff y Phillips (1982), Calibration of probabilities: The state of the art to 1980](https://www.cambridge.org/core/books/abs/judgment-under-uncertainty/calibration-of-probabilities-the-state-of-the-art-to-1980/9F0C9EC2997AEEB6DDDB304C2F935A16)
- [Koriat, Sheffer y Ma'ayan (2002), Comparing objective and subjective learning curves: Judgments of learning exhibit increased underconfidence with practice](https://newiipdm.haifa.ac.il/wp-content/uploads/2015/05/2002-KorShefMaaJEPG.pdf)
- [Tekin y Roediger (2021), The effect of delayed judgments of learning on retention (resume a Rhodes y Tauber, 2011)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7912969)
- [Thiede, Anderson y Therriault (2003), Accuracy of metacognitive monitoring affects learning of texts](https://wp.stolaf.edu/cila/files/2012/11/thiede_jedp.pdf)
- [Double, Birney y Walker (2018), A meta-analysis and systematic review of reactivity to judgements of learning](https://durham-repository.worktribe.com/output/2253677/a-meta-analysis-and-systematic-review-of-reactivity-to-judgements-of-learning)

### Puntos de control

**Nivel de evidencia:** moderada

#### 1. Origen, teoría y evidencia

**Qué es.** Un punto de control es una pausa fijada de antemano para revisar cómo va el trabajo. Puede ser por tiempo (cada 25 minutos), por hito (al terminar una parte) o por evento (al cambiar de fase del PCRC).

**Quién la investigó y qué teoría la sostiene.**
- Nelson y Narens (1990) describieron la metacognición en dos niveles. El nivel metacognitivo *monitorea* (observa) el nivel cognitivo y lo *controla* (corrige). Un punto de control es el momento en que el nivel metacognitivo mira hacia abajo.
- Zimmerman (2000) ubicó la autoobservación dentro del aprendizaje autorregulado. Sin observarse, la persona no puede ajustar lo que hace.
- Cirillo creó la técnica Pomodoro a fines de los años 80. La describió en un texto propio (Cirillo, 2006) y después en un libro (Cirillo, 2018). Propone bloques de 25 minutos con pausas cortas. Es una práctica, no una teoría probada.
- La revisión por hitos viene de la gestión de proyectos. Es práctica habitual, sin evidencia experimental propia.

**Evidencia.**
Dos términos primero. Un *metaanálisis* junta los resultados de muchos estudios para calcular un efecto promedio. El *tamaño de efecto d* mide cuánto cambia el resultado: 0,2 es pequeño, 0,5 es moderado y 0,8 es grande.
- Harkin y colegas (2016) hicieron un metaanálisis de 138 estudios con grupo de control y asignación al azar, con 19.951 personas. Monitorear el progreso mejoró el logro de metas (d = 0,40, efecto entre pequeño y moderado). El efecto fue mayor cuando el progreso se registraba por escrito o se informaba a otros o en público.
- Dignath y colegas (2023) hicieron un metaanálisis de herramientas que ayudan a monitorear el aprendizaje, como diarios, portafolios y rúbricas: 32 estudios, 3.492 personas. Encontraron un efecto moderado sobre el rendimiento (d = 0,42). Funcionaron mejor las herramientas que hacían revisar el contenido y también la conducta de estudio.
- Sobre Pomodoro hay pocos estudios. Biwer y colegas (2023) compararon pausas fijas y pausas libres en 87 estudiantes durante un día de estudio. Las pausas fijas eran de 6 minutos cada 24 o de 3 minutos cada 12. Con pausas fijas hubo menos fatiga y distracción, y más concentración y motivación. El esfuerzo y la tarea completada fueron iguales. Los autores sugieren, con cautela, que las pausas fijas fueron más eficientes: el mismo trabajo en menos tiempo. Las medidas fueron autoinformadas.

**Nivel de evidencia: moderada.** Monitorear el progreso, y sobre todo registrarlo, tiene buen respaldo. El intervalo exacto (25 minutos) y la revisión por hitos no tienen evidencia formal propia.

#### 2. Proceso y buenas prácticas

**Pasos**
1. **Definir los puntos al planificar.** Elegir el tipo de punto: por tiempo, por hito o por cambio de fase del PCRC.
2. **Escribir dos o tres preguntas fijas.** Por ejemplo: ¿sigo en el objetivo?, ¿qué bifurcaciones están abiertas?, ¿mi confianza en lo hecho es alta o baja?
3. **Pedir el aviso.** Pedir a Claude que avise al llegar al punto, o usar un temporizador.
4. **Detenerse y responder por escrito.** Una o dos líneas por pregunta.
5. **Decidir.** Seguir, corregir el rumbo (eso ya es controlar) o aparcar una bifurcación.
6. **Registrar.** Guardar las respuestas en la sesión o en el issue.

**Buenas prácticas**
- Registrar por escrito. Es lo que más aumenta el efecto (Harkin y colegas, 2016).
- Revisar el contenido y también el proceso: qué se hizo y cómo se está trabajando (Dignath y colegas, 2023).
- Usar puntos por hito en tareas largas y puntos por tiempo en tareas que atrapan.
- Mantener el punto corto. Dos minutos alcanzan.

**Errores comunes**
- Saltarse el punto "porque va bien". Justo ahí aparece la deriva: alejarse del objetivo sin notarlo.
- Hacer preguntas vagas ("¿todo bien?"). No obligan a mirar nada concreto.
- Revisar sin decidir. Un punto de control sin decisión no sirve para controlar.
- Poner puntos tan seguidos que cortan el trabajo profundo.

#### 3. Ejemplo

**Caso.** Lucía escribe con Claude la especificación de un módulo de permisos. Está en la fase *crear* del PCRC.

**Al planificar**, escribe:
> "Vamos a redactar la especificación de permisos. Pon un punto de control al terminar cada sección y otro antes de pasar a *decidir*. En cada punto pregúntame: 1) ¿seguimos en el alcance?, 2) ¿qué bifurcaciones están abiertas?, 3) ¿qué tan segura estoy de lo escrito, del 1 al 5?"

**Durante la sección de roles**, Lucía nota un problema: los permisos heredados entre equipos. Escribe:
> "Abro una bifurcación liviana: herencia entre equipos. La dejo aparcada."

**Punto de control 1** (fin de la sección de roles). Claude pregunta y Lucía responde:
> "1) Sí, seguimos en el alcance. 2) Una abierta: herencia entre equipos, aparcada. 3) Confianza 3. No sé si el rol 'auditor' puede ver borradores."

Decide: *"Antes de seguir, aclaremos el rol auditor."* Claude propone dos opciones y ella elige una.

**Punto de control 2** (antes de *decidir*). Lucía revisa:
> "La herencia entre equipos afecta tres secciones. Ya no es liviana. Ábrela como issue en GitHub y enlázala aquí."

La bifurcación pasa de liviana a pesada.

**Resultado.** La especificación llega a *decidir* sin la duda del auditor. La herencia queda registrada en un issue y no contamina el alcance actual. Las notas de los puntos de control quedan en la sesión. Lucía las usa después en la fase *evaluar* del PCM para comparar su confianza con lo que encontró la revisión.

#### Fuentes

- [Harkin et al. (2016). Does monitoring goal progress promote goal attainment? A meta-analysis. Psychological Bulletin, 142(2), 198-229](https://eprints.whiterose.ac.uk/id/eprint/91437/)
- [Dignath, van Ewijk, Perels y Fabriz (2023). Let learners monitor the learning content and their learning behavior! A meta-analysis on the effectiveness of tools to foster monitoring. Educational Psychology Review, 35, 62](https://link.springer.com/article/10.1007/s10648-023-09718-4)
- [Biwer et al. (2023). Understanding effort regulation: Comparing 'Pomodoro' breaks and self-regulated breaks. British Journal of Educational Psychology, 93(2), 353-367](https://cris.maastrichtuniversity.nl/en/publications/understanding-effort-regulation-comparing-pomodoro-breaks-and-sel)
- [Biwer et al. (2023), PubMed](https://pubmed.ncbi.nlm.nih.gov/36859717/)
- [Pomodoro Technique (Wikipedia, apoyo para el origen a fines de los 80)](https://en.wikipedia.org/wiki/Pomodoro_Technique)

### Mapa de hilos

**Nivel de evidencia:** práctica sin evidencia formal

#### 1. Origen, teoría y evidencia

## 1. Origen, teoría y evidencia

Nadie "inventó" el mapa de hilos con ese nombre. Es una práctica que une varias líneas de investigación. Un **hilo** es una línea de trabajo en curso: la tarea principal o una bifurcación.

**Memoria de trabajo limitada.** La memoria de trabajo es el espacio mental donde sostenemos lo que estamos usando ahora. Cowan (2001) revisó muchos estudios y concluyó que su capacidad ronda los 4 elementos con sentido (en inglés, "chunks"), con un rango de 3 a 5. Un hilo no equivale exactamente a un elemento, pero la idea se aplica: con muchos hilos abiertos a la vez, es fácil perder alguno.

**Los objetivos pendientes compiten por la atención.** Altmann y Trafton (2002) propusieron un modelo en el que un objetivo pierde activación con el tiempo. Para retomar un objetivo pendiente hace falta una **señal**: algo externo que lo recuerde. Masicampo y Baumeister (2011) mostraron, en varios experimentos, que las metas sin terminar generan pensamientos intrusivos y empeoran el rendimiento en otra tarea. Escribir un plan concreto para esa meta eliminó esos efectos. No encontré réplicas independientes de este estudio.

**Descarga cognitiva.** La descarga cognitiva es usar el mundo externo para aliviar la mente, por ejemplo con una nota o un recordatorio. Risko y Gilbert (2016) revisaron esta línea de investigación. Advierten que la gente no siempre juzga bien cuándo le conviene descargar. Kirsh (2010) explica que las representaciones externas hacen más que ahorrar memoria: crean referentes que persisten, se pueden compartir y ayudan a coordinar el pensamiento. Esto se vincula con la idea de **cognición distribuida**: el pensamiento ocurre entre la mente y sus herramientas.

**Programadores interrumpidos.** Parnin y Rugaber (2011) analizaron unas 10 000 sesiones de programación grabadas, de 86 programadores. Solo en el 10 % de las sesiones la persona empezó a editar código en menos de un minuto al retomar el trabajo. DeLine y Parnin (2010) encuestaron a 371 programadores y vieron que dependen mucho de las notas para retomar una tarea. En el mismo trabajo, un experimento mostró que unas señales automáticas (resúmenes de lo que se hizo antes) duplicaron la tasa de éxito frente a tomar notas sin ayuda. Las notas ayudan, pero una señal bien armada ayuda más.

**Nivel de evidencia: práctica sin evidencia formal, apoyada en mecanismos con evidencia.** Que la memoria de trabajo es limitada tiene evidencia fuerte. Que escribir planes y notas externas reduce la interferencia y ayuda a retomar tiene evidencia moderada. El formato concreto del mapa de hilos no se ha probado en estudios controlados. No encontré tamaños de efecto aplicables a la técnica.

#### 2. Proceso y buenas prácticas

## 2. Proceso y buenas prácticas

### Pasos

1. **Abrir el mapa** al empezar la sesión: una lista visible (un archivo o un mensaje fijo en el chat) con el hilo principal y su fase del PCRC.
2. **Registrar cada bifurcación** en cuanto aparece: una línea con nombre corto y estado (abierto, aparcado, descartado, convergido).
3. **Escribir la señal de regreso** de cada hilo aparcado: dónde se quedó y qué haría primero al retomarlo. Así el hilo queda con un plan y deja de ocupar la cabeza.
4. **Revisar el mapa en cada cambio de fase** (por ejemplo, de explorar a decidir): ¿sigo en el hilo principal?, ¿cuántos hay abiertos?
5. **Controlar**: si hay más de tres o cuatro hilos abiertos, aparcar o descartar hasta volver a ese número. Este límite es una regla práctica inspirada en Cowan (2001), no un número probado.
6. **Cerrar la sesión** con el mapa: cada hilo queda convergido, descartado o, si debe sobrevivir, se convierte en bifurcación pesada (issue en GitHub).

### Buenas prácticas

- Una línea por hilo. Si necesita un párrafo, quizá merece un issue.
- Un solo hilo activo a la vez. Los demás están aparcados.
- Pedir a Claude que mantenga el mapa y lo muestre cuando se lo pidas o cuando aparezca una bifurcación.
- Anotar la señal de regreso en concreto: "falta validar el campo fecha", no "seguir con validación".

### Errores comunes

- Anotar demasiado tarde, cuando el hilo ya se perdió.
- Dejar hilos abiertos para siempre. Abierto debe ser un estado breve.
- Convertir el mapa en una lista de tareas larga. Es un instrumento para monitorear, no un backlog.
- Escribir el mapa y no mirarlo nunca. Si no lo revisas en cada cambio de fase, no sirve.

#### 3. Ejemplo

## 3. Ejemplo concreto

Lucía escribe con Claude la especificación de un módulo de reservas. Está en la fase **crear** del PCRC.

Al empezar escribe:

> "Claude, abre un mapa de hilos. Hilo principal: reglas de cancelación, fase crear."

A los veinte minutos, Claude nota que las zonas horarias afectan los plazos de cancelación. Es una bifurcación liviana. Lucía dice:

> "Anótala como aparcada. Señal de regreso: decidir si los plazos se cuentan en la hora del hotel o del cliente."

Poco después surge otra idea: permitir cancelaciones parciales. Lucía duda y pide:

> "Muéstrame el mapa."

Claude responde:

```
Hilo principal: reglas de cancelación (crear) - activo
1. Zonas horarias - aparcado. Regreso: ¿hora del hotel o del cliente?
2. Cancelación parcial - abierto
```

Lucía revisa (monitorear) y decide (controlar):

> "La 2 no entra en esta versión. Márcala descartada."

Termina las reglas y, antes de pasar a la fase **decidir**, revisa el mapa otra vez. Retoma el hilo 1, que ahora sí importa, y lo resuelve: los plazos usan la hora del hotel. Claude lo marca convergido.

Al cerrar la sesión, Lucía pide:

> "Cierra el mapa. ¿Queda algo abierto?"

Claude confirma que no. Pero Lucía recuerda que la cancelación parcial podría volver en la versión 2:

> "Convierte la 2 en issue, como bifurcación pesada, enlazada a la especificación."

**Resultado:** la sesión terminó con el hilo principal completo, una bifurcación convergida y otra descartada para esta versión pero guardada en GitHub. Lucía no tuvo que recordar nada de memoria, y al día siguiente sabe por dónde seguir.

#### Fuentes

- [Cowan (2001). The magical number 4 in short-term memory: A reconsideration of mental storage capacity. Behavioral and Brain Sciences, 24(1), 87-114](https://doi.org/10.1017/S0140525X01003922)
- [Altmann y Trafton (2002). Memory for goals: An activation-based model. Cognitive Science, 26, 39-83](https://www.interruptions.net/literature/Altmann-CogSci02.pdf)
- [Masicampo y Baumeister (2011). Consider it done! Plan making can eliminate the cognitive effects of unfulfilled goals. Journal of Personality and Social Psychology, 101(4), 667-683](https://doi.org/10.1037/a0024192)
- [Risko y Gilbert (2016). Cognitive offloading. Trends in Cognitive Sciences, 20(9), 676-688](https://discovery.ucl.ac.uk/id/eprint/1508770/)
- [Kirsh (2010). Thinking with external representations. AI & Society, 25(4), 441-454](https://philarchive.org/rec/KIRTWE)
- [Parnin y Rugaber (2011). Resumption strategies for interrupted programming tasks. Software Quality Journal](https://sites.cc.gatech.edu/reverse/repository/resumptionstrategies.pdf)
- [DeLine y Parnin (2010). Evaluating cues for resuming interrupted programming tasks. CHI 2010](https://www.microsoft.com/en-us/research/publication/evaluating-cues-for-resuming-interrupted-programming-tasks/)

### Semáforo

**Nivel de evidencia:** práctica sin evidencia formal

#### 1. Origen, teoría y evidencia

**Quién la usó primero.** El semáforo viene de la **evaluación formativa**. La evaluación formativa evalúa durante el trabajo para corregir el rumbo, no para poner una nota al final. Black y Wiliam (1998) revisaron unos 250 estudios en "Assessment and Classroom Learning" y resumieron sus conclusiones para docentes en *Inside the Black Box*. Después, el proyecto King's-Medway-Oxfordshire (KMOFAP) llevó esas ideas al aula durante dos años con 36 docentes de Medway y Oxfordshire. Los propios docentes del proyecto crearon el semáforo. Black, Harrison, Lee, Marshall y Wiliam lo describieron en *Working Inside the Black Box* (2002) y en *Assessment for Learning: Putting it into Practice* (2003). Cada alumno marca su comprensión con un color: verde (lo entiendo), amarillo (dudo), rojo (no lo entiendo).

**Teoría.** Es una forma rápida de **autoevaluación**: la persona juzga su propio nivel frente a un objetivo. En términos del PCM, hace visible el monitoreo. Así el control se dirige donde hace falta.

**Evidencia.**
- Black y Wiliam (1998) hablaron de efectos de 0,4 a 0,7 desviaciones estándar para la evaluación formativa en general. Pero ese rango no sale de un metaanálisis (un estudio que combina con estadística los resultados de muchos estudios): resume estudios muy distintos entre sí. Kingston y Nash (2011) sí hicieron un metaanálisis y estimaron un efecto medio de cerca de 0,20. Briggs, Ruiz-Primo, Furtak, Shepard y Yin (2012) criticaron sus métodos y concluyeron que el efecto real sigue siendo incierto.
- Panadero, Jonsson y Botella (2017) reunieron 19 estudios sobre autoevaluación en general, con 2305 alumnos. Encontraron efectos de 0,23 a 0,65 sobre la autorregulación y de 0,73 sobre la autoeficacia (la confianza en la propia capacidad).
- No encontré ningún estudio controlado sobre el semáforo como técnica aislada. Wiliam (2011) advierte que muchas veces queda en un autoinforme poco fiable como indicador de aprendizaje, y propone cambiar lo que significa el verde.

**Nivel de evidencia:** el semáforo es una **práctica sin evidencia formal propia**. Lo apoya de forma indirecta una evidencia **moderada** sobre la autoevaluación y la evaluación formativa.

#### 2. Proceso y buenas prácticas

**Pasos**
1. Definir criterios claros para cada parte del trabajo antes de empezar: qué significa "entendido" o "terminado".
2. En puntos fijos (al cerrar cada fase o cada parte), asignar un color a cada parte: verde, amarillo o rojo.
3. Dar una razón concreta por cada color. Para el verde, una prueba: "puedo explicarlo" o "pasa el test".
4. Actuar según el color (es la fase controlar): el rojo se atiende ya, el amarillo se revisa o se aparca, el verde sigue.
5. Al final, comparar los colores con el resultado real. Eso es calibrar: ver si la confianza coincidía con los hechos.

**Buenas prácticas**
- Endurecer el verde. Wiliam (2011) propone que verde signifique "podría enseñárselo a otra persona", no solo "lo sé". En software sirve también "tengo una prueba que lo demuestra".
- Pedir a Claude un color independiente y comparar los dos.
- Un color sin acción no sirve: cada rojo lleva un siguiente paso.

**Errores comunes**
- Marcar todo en verde por optimismo o por prisa.
- Usar el color solo como sensación, sin un criterio detrás.
- Convertir un rojo en una bifurcación que crece dentro de la sesión, en lugar de aparcarlo o pasarlo a un issue.

#### 3. Ejemplo

**Caso:** Lucía escribe con Claude la especificación de un módulo de permisos y está en la fase *decidir* del PCRC.

Antes de pasar a *implementar*, escribe:

> "Semáforo antes de implementar. Mis colores: roles = verde, herencia de permisos = amarillo, permisos sobre recursos borrados = rojo. Dame tus colores con una razón y una prueba para cada verde."

Claude responde:

> "Roles: verde. Los tres casos de la sección 2 tienen ejemplo y criterio de aceptación. Herencia: rojo, no amarillo. La regla 4 dice 'el hijo hereda', pero la regla 7 permite quitarle permisos al hijo, y no está claro cuál gana. Recursos borrados: rojo. No hay ninguna regla."

Lucía compara los colores. En la herencia había puesto amarillo y era rojo: se había sobreestimado. Decide:

> "Herencia: resolvemos el conflicto ahora. Gana la regla 7 y agregamos un ejemplo. Recursos borrados: es una bifurcación pesada, abre un issue y sigamos sin eso en esta versión."

Mientras resuelven la herencia, aparece una idea: auditar los cambios de permisos. Lucía dice:

> "Bifurcación liviana: auditoría. Aparcada."

**Resultado.** La herencia pasa a verde, con un ejemplo que funciona como prueba. Los recursos borrados quedan en un issue de GitHub, fuera del alcance de esta versión. La auditoría queda aparcada en la sesión. Lucía entra en *implementar* sin ningún rojo abierto. En la fase *evaluar* del PCM, anota: "En la herencia me sobreestimé. La próxima vez, pido el color de Claude antes de dar el mío".

#### Fuentes

- [OECD (2005), Formative Assessment: Improving Learning in Secondary Classrooms (describe el semáforo creado por docentes del KMOFAP)](https://t4.oecd.org/education/ceri/35661078.pdf)
- [Black, Harrison, Lee, Marshall y Wiliam (2002), Working Inside the Black Box (UCL Discovery)](https://discovery.ucl.ac.uk/id/eprint/1507188/)
- [Panadero, Jonsson y Botella (2017), Effects of self-assessment on self-regulated learning and self-efficacy: Four meta-analyses](https://portalinvestigacion.deusto.es/documentos/6326545dd50fae52cd317f7b)
- [Briggs, Ruiz-Primo, Furtak, Shepard y Yin (2012), Meta-Analytic Methodology and Inferences About the Efficacy of Formative Assessment](https://experts.colorado.edu/display/pubid_97215)
- [Sawchuk (2009), Has the research on formative assessment been oversold? (Education Week)](https://www.edweek.org/education/has-the-research-on-formative-assessment-been-oversold/2009/05)
- [Traffic Lights, adaptado de Wiliam (2011), Embedded Formative Assessment (NWESD)](https://www.nwesd.org/wp-content/uploads/2013/08/PROL_Traffic_Lights_kdj.pdf)

## Controlar

### Reglas si-entonces ante cada señal

**Nivel de evidencia:** fuerte

#### 1. Origen, teoría y evidencia

**Quién la investigó.** La base es la idea de **intenciones de implementación** (planes "si… entonces"). La propuso el psicólogo Peter Gollwitzer (1993, 1999). Una intención de meta dice *qué* quiero lograr ("quiero terminar la especificación"). Una intención de implementación dice *cuándo y cómo* actuar: "si ocurre la situación X, entonces hago Y".

**Teoría.** Entre querer algo y hacerlo hay una brecha. El plan "si… entonces" la reduce por dos mecanismos, que comprobaron Webb y Sheeran (2007, 2008):
1. **Detección de la señal**: la situación X queda más presente en la mente y se nota antes.
2. **Respuesta automática**: el vínculo entre X e Y se vuelve fuerte, y la respuesta sale casi sin pensar ni gastar fuerza de voluntad.

En el PCM esto une dos fases. *Monitorear* detecta la señal; *controlar* ejecuta la respuesta ya decidida. Achtziger, Gollwitzer y Sheeran (2008) mostraron en dos experimentos de campo (dieta y deporte) que estos planes sirven también para **proteger una meta en curso** frente a interferencias (antojos, pensamientos y emociones que distraen). No sirven solo para empezar.

**Evidencia.**
- Gollwitzer y Sheeran (2006), metaanálisis (estudio que combina muchos estudios) de 94 pruebas: efecto medio a grande sobre el logro de metas, d = 0,65. El valor d mide la diferencia entre grupos en desviaciones estándar.
- Sheeran, Listrom y Gollwitzer (2025, *European Review of Social Psychology*), 642 pruebas: efectos de d = 0,27 a 0,66 en resultados cognitivos, emocionales y de conducta. Los efectos son mayores cuando el plan usa el formato literal "si… entonces", cuando la persona está muy motivada y cuando ensaya el plan.
- Wang, Wang y Gai (2021), metaanálisis del contraste mental con intenciones de implementación (una técnica que combina imaginar la meta y sus obstáculos con un plan si-entonces). Reunió 21 estudios con 24 tamaños de efecto: g = 0,34 (g es una medida parecida a d). Hallaron indicios de sesgo de publicación (se publican más los estudios con resultados positivos). Al corregirlo, el efecto bajó a g = 0,24.
- Harkin y colegas (2016), 138 estudios: monitorear el avance mejora el logro de metas (d = 0,40). El efecto es mayor si el avance se registra por escrito o se informa a otros. Esto apoya el lado de *monitorear*.

**Nivel de evidencia: fuerte** para los planes si-entonces en general, aunque el efecto real puede ser algo menor por el sesgo de publicación. Su uso como reglas de control metacognitivo al trabajar con una IA **no tiene estudios directos**: es una extrapolación razonable.

#### 2. Proceso y buenas prácticas

**Pasos**
1. **Elegir la meta de la sesión** (viene de *planificar*).
2. **Listar las señales críticas**: momentos en que suele torcerse el trabajo. Por ejemplo, aparece una bifurcación, Claude se sale del alcance o un error se repite.
3. **Escribir una regla por señal** con el formato literal: "Si [señal concreta y observable], entonces [acción concreta]".
4. **Ensayar las reglas**: leerlas en voz alta o repetirlas una vez al empezar.
5. **Dejarlas a la vista**: en el prompt inicial o en un archivo de la sesión, para que Claude avise cuando se cumple la condición.
6. **Ejecutar sin volver a deliberar** cuando aparece la señal.
7. **Revisar las reglas en *evaluar***: ¿qué regla se disparó?, ¿qué regla faltó?, ¿cuál sobra?

**Buenas prácticas y errores comunes**
- La señal debe poder observarse. "Si me pierdo" no sirve; "si llevo 20 minutos en el mismo error" sí sirve.
- La acción debe ser pequeña e inmediata, no "replantear todo".
- Pocas reglas, por ejemplo de tres a cinco por sesión. Es una recomendación práctica: con muchas reglas cuesta recordarlas y aplicarlas.
- Úsalas también para lo interno: "si siento ganas de seguir puliendo, entonces…".
- La acción puede ser hacer algo nuevo, ignorar una distracción o frenar una respuesta. Los estudios prueban planes de los tres tipos.
- Error común: escribir la regla y no ensayarla. Ensayar el plan aumenta el efecto.
- Error común: reglas rígidas que bloquean lo imprevisto. Revísalas en cada ciclo.

#### 3. Ejemplo

**Contexto.** Lucía escribe con Claude la especificación de un módulo de pagos. Está en la fase *implementar* del PCRC. En sesiones anteriores perdió horas por dos cosas: abrir temas nuevos a mitad de camino y dejar que Claude tocara archivos fuera del alcance.

**Al planificar**, Lucía escribe en el primer mensaje:

> "Meta de hoy: cerrar la sección de reembolsos. Reglas para esta sesión. Avísame cuando se cumpla una:
> 1. Si aparece una bifurcación, entonces la anotamos como liviana *aparcada* y seguimos con reembolsos.
> 2. Si la bifurcación afecta a otro módulo, entonces propones un issue en GitHub (bifurcación pesada) y no la tratamos hoy.
> 3. Si un cambio toca un archivo fuera de `specs/pagos/`, entonces te detienes y me preguntas.
> 4. Si discutimos el mismo punto más de tres turnos, entonces volvemos a *decidir* con dos opciones escritas."

Lee las cuatro reglas una vez antes de empezar.

**Durante la sesión.** Claude redacta los casos de reembolso parcial y dice:

> "Señal de la regla 1: surgió la pregunta de cómo tratar monedas distintas. ¿La aparco?"

Lucía responde: "Sí, aparcada. Sigue." No delibera; la decisión ya estaba tomada.

Más tarde, Claude quiere ajustar `specs/facturacion/impuestos.md`. Lo detiene la regla 3:

> "Este cambio sale de `specs/pagos/`. ¿Lo hago o lo dejo como issue?"

Lucía ve que el cambio afecta a otro módulo y aplica la regla 2: "Abre el issue y enlázalo al issue del módulo de pagos."

**Al evaluar.** Lucía revisa: la sección de reembolsos quedó cerrada. Hay una bifurcación liviana aparcada (monedas) y un issue abierto (impuestos). La regla 4 nunca se disparó. Anota: "La regla 4 sobra por ahora. Agrego una nueva: si Claude propone un ejemplo sin caso de prueba, entonces pido el caso de prueba."

**Resultado.** La sesión terminó en su meta, sin desvíos. Las interrupciones quedaron registradas y el trabajo pendiente quedó visible.

#### Fuentes

- [Gollwitzer y Sheeran (2006). Implementation intentions and goal achievement: a meta-analysis of effects and processes, Advances in Experimental Social Psychology 38 (ficha)](https://stafforini.com/works/gollwitzer-2006-implementation-intentions-and/)
- [Sheeran, Listrom y Gollwitzer (2025). The when and how of planning: Meta-analysis of the scope and components of implementation intentions in 642 tests, European Review of Social Psychology 36(1)](https://kops.uni-konstanz.de/handle/123456789/69905)
- [Achtziger, Gollwitzer y Sheeran (2008). Implementation intentions and shielding goal striving from unwanted thoughts and feelings, PSPB 34(3)](https://journals.sagepub.com/doi/10.1177/0146167207311201)
- [Webb y Sheeran (2007). How do implementation intentions promote goal attainment? A test of component processes, JESP 43(2)](https://eprints.whiterose.ac.uk/10753/)
- [Wieber, Thürmer y Gollwitzer (2015). Promoting the translation of intentions into action by implementation intentions: behavioral effects and physiological correlates, Frontiers in Human Neuroscience](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2015.00395/full)
- [Wang, Wang y Gai (2021). A meta-analysis of the effects of mental contrasting with implementation intentions on goal attainment, Frontiers in Psychology](https://pmc.ncbi.nlm.nih.gov/articles/PMC8149892/)
- [Harkin y colegas (2016). Does monitoring goal progress promote goal attainment? A meta-analysis of the experimental evidence, Psychological Bulletin 142(2)](https://eprints.whiterose.ac.uk/91437/)

### Aparcar (parking lot)

**Nivel de evidencia:** débil

#### 1. Origen, teoría y evidencia

**Quién la inventó.** Nadie en particular. El "parking lot" nació como práctica de facilitación de reuniones: un papel en la pared donde se anotan los temas que se salen de la agenda, para volver a ellos después. Allen (2001), en *Getting Things Done* (GTD), llevó una idea parecida al trabajo personal. Su idea es la *captura*: anotar todo "ciclo abierto" (tarea o idea sin cerrar) en un sistema externo y confiable, para que la mente deje de recordarlo. Allen no presenta estudios; su libro es una guía práctica.

**La teoría.** Zeigarnik (1927) observó que las personas recordaban mejor las tareas interrumpidas que las terminadas. La explicación clásica viene de Lewin, su director: una meta sin cumplir deja una "tensión" que mantiene la tarea activa en la mente. Masicampo y Baumeister (2011) propusieron algo más preciso: lo que molesta no es la tarea sin terminar, sino la tarea **sin plan**. Si uno decide cuándo y cómo la va a retomar, la mente la suelta.

**La evidencia.**
- Masicampo y Baumeister (2011, *Journal of Personality and Social Psychology*, 101(4), 667-683) hicieron varios experimentos con estudiantes. Una meta pendiente produjo pensamientos intrusivos (que aparecen sin querer) durante una lectura, más accesibilidad de palabras ligadas a la meta y peor rendimiento en anagramas. Escribir un plan concreto para esa meta eliminó estos efectos. El efecto dependió de qué tan en serio se hizo el plan. El plan no redujo la ansiedad al pensar en la meta pendiente. No se encontraron réplicas directas de este trabajo.
- Scullin y colegas (2018, *Journal of Experimental Psychology: General*, 147(1), 139-146) estudiaron a 57 adultos jóvenes sanos en un laboratorio de sueño. Antes de dormir, la mitad escribió durante 5 minutos una lista de tareas pendientes y la otra mitad una lista de tareas ya hechas. El grupo de la lista de pendientes se durmió antes, unos 9 minutos según la nota de prensa de la universidad. Cuanto más concreta era la lista, más rápido se dormían. Faltó un grupo de control sin escritura, así que no se sabe si escribir pendientes ayuda o si escribir lo hecho perjudica.
- Ghibellini y Meier (2025, *Humanities and Social Sciences Communications*) hicieron un metaanálisis (un estudio que combina los resultados de muchos estudios) del efecto Zeigarnik y del efecto Ovsiankina. No encontraron ventaja de memoria para las tareas interrumpidas, pero sí una tendencia general a retomarlas (efecto Ovsiankina). El "efecto Zeigarnik" popular está, por tanto, sobrevendido.

**Nivel de evidencia: débil.** La base teórica es razonable y hay dos estudios de apoyo, pero son pocos, con muestras pequeñas, sin réplicas directas y con una teoría de fondo (Zeigarnik) que no se sostuvo en el metaanálisis. El aparcar tal como se usa en reuniones o en GTD es una práctica sin evidencia formal propia.

#### 2. Proceso y buenas prácticas

**Proceso**

1. **Detectar** la bifurcación: una idea o tema nuevo que aparece en medio de una fase y no es lo que estás haciendo ahora.
2. **Decidir rápido** si es liviana (vive solo en la sesión) o pesada (merece un issue en GitHub).
3. **Anotar** en una frase: qué es y por qué importa. Si es liviana, queda en la lista de la sesión con estado *aparcado*. Si es pesada, se abre el issue.
4. **Fijar el regreso**: cuándo o con qué condición la vas a retomar ("al cerrar la fase de decidir", "antes de verificar"). En los experimentos de Masicampo y Baumeister (2011), tener un plan concreto fue lo que liberó la mente.
5. **Volver** de inmediato a la fase en curso.
6. **Revisar** la lista en el punto fijado y cambiar cada estado: *abierto* (se trabaja ahora), *descartado* o *convergido* (se integró a otra cosa).

**Buenas prácticas**

- Anota con un plan de regreso, no solo el tema. Una lista sin un "cuándo" es un cajón, no un aparcamiento.
- Usa una sola lista por sesión. Varias listas sueltas no dan confianza.
- Pide a Claude que lleve la lista y que te la muestre al cerrar cada fase.
- Revisa siempre. Si nunca vuelves a la lista, dejas de confiar en ella y la técnica pierde su efecto.

**Errores comunes**

- Aparcar lo urgente: si la bifurcación bloquea la fase actual, no se aparca, se trata.
- Escribir notas largas: el objetivo es soltar el tema, no resolverlo al anotarlo.
- Dejar bifurcaciones livianas aparcadas al cerrar la sesión: al final, cada una pasa a descartada, convergida o pesada (issue).

#### 3. Ejemplo

**Contexto.** Laura escribe con Claude la especificación de un módulo de pagos. Está en la fase *decidir* del PCRC: debe elegir entre reintentos automáticos o manuales cuando falla un cobro.

**La bifurcación aparece.** Mientras Claude compara opciones, a Laura se le ocurre otra cosa:

> "Espera. ¿Y si el cliente cambia de moneda a mitad del cobro? No lo pensamos."

Siente el impulso de seguir esa pista. En vez de eso, pasa al nivel metacognitivo y controla:

> "Esto es una bifurcación. Apárcala como liviana: 'cambio de moneda durante un cobro, puede afectar los reintentos'. La retomamos al terminar *decidir*, antes de *implementar*. Ahora sigamos con los reintentos."

Claude responde:

> "Aparcada. Lista de la sesión:
> 1. Cambio de moneda durante un cobro. Estado: aparcado. Regreso: al cerrar *decidir*."

**Otra bifurcación, esta pesada.** Diez minutos después, Claude nota que el módulo de facturación usa otro formato de fechas. Laura:

> "Eso no es de esta sesión y toca otro módulo. Abre un issue en GitHub, enlazado al de pagos, y seguimos."

**El cierre de la fase.** Laura elige reintentos automáticos con un tope de tres. Antes de pasar a *implementar*, Claude muestra la lista. Laura revisa:

> "El cambio de moneda sí afecta: un reintento podría cobrar en otra moneda. Lo integramos a la decisión: cada reintento usa la moneda del primer intento."

Claude cambia el estado de la bifurcación a *convergido* y agrega esa regla a la especificación.

**Resultado.** Laura terminó la fase *decidir* sin perder el hilo. La idea del cambio de moneda no se perdió y mejoró la decisión. El tema de las fechas quedó en un issue. Al cerrar la sesión no quedó ninguna bifurcación aparcada.

#### Fuentes

- [Masicampo y Baumeister (2011), Consider it done! Plan making can eliminate the cognitive effects of unfulfilled goals, JPSP 101(4), 667-683 (DOI)](https://doi.org/10.1037/a0024192)
- [Ghibellini y Meier (2025), Interruption, recall and resumption: a meta-analysis of the Zeigarnik and Ovsiankina effects, Humanities and Social Sciences Communications](https://www.nature.com/articles/s41599-025-05000-w)
- [Ghibellini y Meier (2025), registro en IDEAS/RePEc](https://ideas.repec.org/a/pal/palcom/v12y2025i1d10.1057_s41599-025-05000-w.html)
- [Scullin et al. (2018), The effects of bedtime writing on difficulty falling asleep (PubMed)](https://pubmed.ncbi.nlm.nih.gov/29058942/)
- [Nota de prensa de Baylor University sobre Scullin et al. (2018)](https://news.web.baylor.edu/news/story/2018/can-writing-your-dos-help-you-doze-baylor-study-suggests-jotting-down-tasks-can)
- [BPS Research Digest sobre Scullin et al. (2018), con sus limitaciones](https://bps.org.uk/node/2257)
- [Zeigarnik effect (Wikipedia, apoyo)](https://en.wikipedia.org/wiki/Zeigarnik_effect)

### Pausa de incubación

**Nivel de evidencia:** moderada

#### 1. Origen, teoría y evidencia

**Quién.** Wallas (1926), en *The Art of Thought*, describió cuatro etapas del pensamiento creativo: preparación, incubación, iluminación y verificación. La **incubación** es el tiempo en que una persona deja a propósito de trabajar en un problema y después vuelve a él, a veces con una idea nueva.

**Teoría.** Hay dos explicaciones principales:
- **Liberar la fijación.** Una fijación es quedar atrapado en una idea equivocada que bloquea las demás. La pausa debilita esa idea y deja ver otras (Smith y Blankenship, 1989).
- **Trabajo no consciente.** La mente seguiría haciendo asociaciones mientras la persona hace otra cosa. Esta explicación está más discutida y tiene menos apoyo experimental directo.

**Evidencia.**
- Sio y Ormerod (2009) publicaron un metaanálisis en *Psychological Bulletin*. Un metaanálisis combina muchos estudios para estimar un efecto promedio. Reunieron 117 estudios y hallaron un efecto positivo de pequeño a moderado (d medio ≈ 0,29, según Gilhooly, 2016). La d mide el tamaño del efecto: 0,2 se considera pequeño y 0,5 mediano. La pausa ayudó más en tareas de **pensamiento divergente** (generar muchas ideas) que en problemas de *insight* (problemas con una solución única que aparece de golpe). El efecto fue mayor cuando hubo una **preparación más larga** antes de la pausa. Una tarea poco exigente durante la pausa funcionó mejor que una tarea exigente.
- Baird y otros (2012) hallaron que una tarea poco exigente durante la pausa mejoraba las ideas en problemas ya vistos antes. Lo atribuyeron a la divagación mental (pensamientos ajenos a la tarea). Estudios posteriores no confirmaron el papel de la divagación: Smeekens y Kane (2016), Steindorf y otros (2021) y Murray y otros (2024; dos estudios con 443 personas en total). El efecto de la pausa se sostiene mejor que la explicación de Baird.

**Nivel de evidencia: moderada.** El efecto de la pausa existe, pero es modesto y depende del tipo de problema y de haber trabajado antes a fondo. El mecanismo exacto sigue en discusión.

#### 2. Proceso y buenas prácticas

**Pasos**

1. **Preparar a fondo.** Antes de pausar, trabaja el problema en serio. Con más preparación, la pausa rinde más (Sio y Ormerod, 2009).
2. **Detectar el atasco (monitorear).** Nota las señales: das vueltas a la misma idea, Claude y tú repiten propuestas parecidas, o llevas un buen rato sin avanzar (por ejemplo, 15 a 20 minutos; es una referencia práctica, no un dato de los estudios).
3. **Decidir la pausa (controlar).** Dile a Claude por escrito que pausas y por qué. Escribe en una línea dónde quedaste y qué te bloquea: es la **nota de retorno**.
4. **Ordenar lo abierto.** Si en la sesión apareció un tema nuevo, regístralo como bifurcación liviana en estado *aparcado*, para que no te distraiga al volver. Si la pausa va a durar días, guarda la nota de retorno en un issue de GitHub.
5. **Hacer algo liviano.** Camina, ordena, responde correos simples. Evita tareas que exijan mucha concentración.
6. **Volver y releer.** Relee la nota de retorno y el problema. Anota la primera idea que aparezca, aunque parezca rara.
7. **Verificar.** Prueba la idea nueva. La pausa da candidatas, no respuestas seguras.

**Buenas prácticas y errores comunes**

- Usa la pausa en problemas abiertos: diseño, nombres, alternativas. Ante un error concreto en el código, depurar con método suele rendir más.
- No pauses al primer obstáculo. Pausar sin haber preparado es solo distraerse.
- Deja siempre una nota de retorno corta. Sin ella, pierdes el hilo.
- Error común: llenar la pausa con otra tarea difícil. Eso reduce el efecto.
- Error común: volver y repetir lo mismo. Cambia el punto de partida: otro ejemplo, otra pregunta.
- Pide a Claude que vigile las señales de atasco con un plan "si… entonces": "si repetimos la misma propuesta dos veces, sugiéreme una pausa".

#### 3. Ejemplo

**Situación.** Lucía escribe con Claude la especificación de permisos de una API. Está en la fase **crear** del PCRC. Lleva 40 minutos buscando cómo modelar los permisos por proyecto y por organización. A mitad de camino surgió un tema nuevo: el registro de auditoría de accesos.

**Monitorear.** Claude propone por tercera vez una tabla de roles con herencia. Lucía nota que las propuestas se parecen y que ninguna resuelve el caso "invitado externo".

**Controlar.** Lucía escribe:

> "Paro aquí. Estamos fijados en roles con herencia. Nota de retorno: el bloqueo es el invitado externo, que no pertenece a ninguna organización. Registra la auditoría de accesos como bifurcación liviana, estado aparcado. Vuelvo en 30 minutos."

Claude responde con un resumen de tres líneas: lo decidido, lo abierto y la pregunta que bloquea.

**Pausa.** Lucía sale a caminar y luego ordena su bandeja de entrada. No piensa en la API a propósito.

**Vuelta.** Relee la nota y escribe:

> "Idea nueva: ¿y si el permiso no cuelga del usuario sino de una *invitación* con alcance y fecha de vencimiento? Así el invitado externo no necesita organización."

**Resultado.** Pasan a la fase **decidir**. Claude compara las dos opciones: roles con herencia contra invitaciones con alcance. Las invitaciones resuelven el caso que bloqueaba y simplifican la revocación. Lucía elige esa opción. En la fase **implementar**, Claude redacta la sección de la especificación. En la fase **verificar**, Lucía pide: "Escribe tres casos de prueba para el invitado externo: acceso válido, acceso vencido y acceso revocado." Los tres casos encajan en el nuevo modelo. Al cerrar la sesión, Lucía convierte la bifurcación de auditoría en bifurcación pesada: un issue en GitHub.

**Lo que hizo funcionar la pausa:** 40 minutos de preparación real, una nota de retorno clara y una tarea liviana durante la pausa.

#### Fuentes

- [Sio y Ormerod (2009). Does incubation enhance problem solving? A meta-analytic review. Psychological Bulletin, 135(1), 94-120 (PubMed)](https://pubmed.ncbi.nlm.nih.gov/19210055/)
- [Sio y Ormerod (2009), ficha con resumen (Lancaster ePrints; sin texto completo)](https://eprints.lancs.ac.uk/id/eprint/56211)
- [Gilhooly (2016). Incubation and Intuition in Creative Problem Solving. Frontiers in Psychology (cita el metaanálisis: 117 estudios, d medio = 0,29)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4956660)
- [Baird y otros (2012). Inspired by distraction: Mind wandering facilitates creative incubation. Psychological Science (PDF)](https://www.cmhp.ucsb.edu/sites/default/files/2018-12/Baird%20et%20al.%20%282012%29%20Inspired%20by%20distraction.pdf)
- [Murray, Liang, Brosowsky y Seli (2024). What are the benefits of mind wandering to creativity? Psychology of Aesthetics, Creativity, and the Arts (dos estudios, N = 443, sin efecto de la divagación)](https://doi.org/10.1037/aca0000420)
- [Du, Gordon y Tolmie (2025). The Role of Mind Wandering During Incubation in Divergent and Convergent Creative Thinking. Brain Sciences (resume Smeekens y Kane, 2016; Steindorf y otros, 2021; Murray y otros, 2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12190454/)

### Cambio de técnica

**Nivel de evidencia:** moderada

#### 1. Origen, teoría y evidencia

**Qué es.** Cambiar de técnica significa dejar a propósito el método que usas cuando deja de dar resultado, y probar otro. En el PCM ocurre en la fase de controlar. Monitorear detecta que estás atascado y controlar decide el cambio.

**Fijación.** Jansson y Smith (1991, *Design Studies*) llamaron fijación a "una adhesión ciega a un conjunto de ideas o conceptos que limita el resultado del diseño conceptual". Mostraron dibujos de soluciones existentes a estudiantes de ingeniería y a diseñadores. Esas personas copiaron rasgos de los ejemplos, incluso rasgos defectuosos, y siguieron copiándolos aunque se les pidió evitarlos. Antes, Luchins (1942) había descrito el efecto Einstellung (en alemán, "disposición mental"): un método aprendido impide ver otro más simple.

**Flexibilidad y persistencia.** El modelo de doble vía de De Dreu, Baas y Nijstad (2008) y Nijstad, De Dreu, Rietzschel y Baas (2010) propone dos caminos hacia ideas originales. Uno es la flexibilidad: saltar entre categorías de ideas. El otro es la persistencia: profundizar mucho en pocas categorías. El modelo no habla de cambiar de técnica. Nuestra lectura: cambiar de técnica se parece a pasar de una vía a la otra cuando una se agota.

**Elección adaptativa de estrategias.** Siegler (1996) propuso el modelo de "olas superpuestas": una persona conoce varias estrategias a la vez, y el uso de cada una sube y baja con el tiempo y según el problema. Lemaire y Siegler (1995) estudiaron cómo niños aprenden a multiplicar y describieron cuatro aspectos del cambio: el repertorio (qué estrategias conoces), la distribución (con qué frecuencia usas cada una), la eficiencia (qué tan rápido y bien la ejecutas) y la selección (si eliges la adecuada para cada problema). Según fuentes que citan a Siegler y Pyke (2013), muchos alumnos usan estrategias correctas en unos problemas de fracciones e incorrectas en otros parecidos, y confían casi lo mismo en unas que en otras. Si no notas que una estrategia falla, no sabes cuándo cambiarla.

**Pausa.** Un metaanálisis es un estudio que combina los resultados de muchos estudios. El metaanálisis de Sio y Ormerod (2009, *Psychological Bulletin*) halló que una pausa (incubación) ayuda a resolver problemas. El efecto es mayor en tareas de pensamiento divergente (generar muchas ideas) y cuando la pausa se llena con una tarea poco exigente. Fuentes secundarias informan 117 estudios y un tamaño de efecto pequeño a mediano (d de Cohen ≈ 0,3 en general; el d de Cohen mide cuán grande es una diferencia). No pudimos comprobar estas cifras en el artículo original.

**Nivel de evidencia: moderada.** La fijación y la elección adaptativa de estrategias están bien documentadas. En cambio, hay poca evidencia directa sobre la regla práctica "si estoy atascado, cambio de técnica". Casi toda la evidencia viene de laboratorio, con niños o estudiantes, y no de trabajo con IA.

#### 2. Proceso y buenas prácticas

**Pasos**

1. **Define la señal de atasco antes de empezar.** Ejemplo: "si en 3 intentos no avanzo" o "si Claude me da la misma respuesta con otras palabras".
2. **Nombra la técnica actual.** Decir "estoy depurando a prueba y error" vuelve visible el método.
3. **Detente y diagnostica.** Pregúntate si falla la técnica o falta información.
4. **Elige otra técnica de tu repertorio.** El repertorio es la lista de técnicas que conoces. Elige una de otro tipo y no una variante de la misma. Por ejemplo, pasa de leer código a escribir un test mínimo.
5. **Fija un límite a la nueva técnica.** Decide cuánto tiempo o cuántos intentos le das.
6. **Evalúa y registra.** Anota qué técnica funcionó para ese tipo de problema.

**Buenas prácticas y errores comunes**

- Ten una lista corta de técnicas a mano. Sin repertorio no hay a qué cambiar.
- No cambies demasiado pronto. La persistencia también produce ideas originales.
- No confundas cambiar de técnica con cambiar de tema. Si aparece un tema nuevo, trátalo como bifurcación.
- Desconfía de tu primera idea y de los ejemplos que te da Claude. Los ejemplos fijan.
- Si nada funciona, haz una pausa breve con una tarea liviana.
- Error común: repetir el mismo prompt (la instrucción que le escribes a Claude) con otras palabras. Eso es la misma técnica.

#### 3. Ejemplo

Lucía escribe con Claude la especificación de un sistema de permisos. Está en la fase **crear** del PCRC.

**Señal de atasco.** Al planificar, Lucía escribió: "Si en tres rondas no tengo una regla clara para los permisos heredados, cambio de técnica."

**El atasco.** Lleva tres rondas pidiendo: "Redacta la regla de herencia de permisos." Cada versión se parece a la anterior. Al monitorear, Lucía ve que se cumplió su señal y que repite la misma técnica: pedir redacción en prosa.

**Diagnóstico.** Escribe: "Claude, paremos. Llevamos tres versiones casi iguales. Creo que falla la forma de pensar, no la redacción."

**Cambio de técnica.** Pasa de redactar a usar casos concretos: "Dame una tabla con 6 casos límite: usuario, carpeta padre, carpeta hija, permiso esperado. No escribas la regla todavía." Pone un límite: "Si con la tabla no sale la regla, probamos con un diagrama de decisión."

**Resultado.** La tabla muestra que dos casos se contradicen: un permiso denegado en la carpeta padre y concedido en la hija. Esa contradicción era el bloqueo. Lucía decide que "denegar gana siempre" y la regla queda en una línea.

**Bifurcación.** En la tabla aparece una pregunta nueva sobre permisos temporales. Lucía dice: "Esto es otra cosa. Lo aparco." Es una bifurcación liviana en estado aparcado. Al cerrar la sesión la convierte en bifurcación pesada: un issue en GitHub.

**Evaluar.** En su registro anota: "Reglas ambiguas: los casos límite en tabla funcionan mejor que la prosa."

#### Fuentes

- [Jansson y Smith (1991), Design fixation, Design Studies 12(1), 3-11](https://doi.org/10.1016/0142-694X(91)90003-F)
- [Luchins (1942), Mechanization in problem solving: The effect of Einstellung, Psychological Monographs 54(6)](https://doi.org/10.1037/h0093502)
- [De Dreu, Baas y Nijstad (2008), Hedonic tone and activation level in the mood-creativity link: Toward a dual pathway to creativity model, JPSP 94(5)](https://pure.rug.nl/ws/portalfiles/portal/177023097/Hedonic_tone_and_activation_level_in_the_mood_creativity_link.pdf)
- [Nijstad, De Dreu, Rietzschel y Baas (2010), The dual pathway to creativity model, European Review of Social Psychology 21(1)](https://pure.rug.nl/ws/portalfiles/portal/156012256/The_dual_pathway_to_creativity_model_Creative_ideation_as_a_function.pdf)
- [Lemaire y Siegler (1995), Four aspects of strategic change: Contributions to children's learning of multiplication, JEP: General 124(1)](https://doi.org/10.1037/0096-3445.124.1.83)
- [Siegler y Pyke (2013), Developmental and individual differences in understanding of fractions, Developmental Psychology 49(10)](https://doi.org/10.1037/a0031200)
- [Sio y Ormerod (2009), Does incubation enhance problem solving? A meta-analytic review, Psychological Bulletin 135(1)](https://pubmed.ncbi.nlm.nih.gov/19210055/)
- [Boom (2015), A new visualization and conceptualization of categorical longitudinal development (modelo de olas superpuestas), Frontiers in Psychology 6:289](https://www.frontiersin.org/articles/10.3389/fpsyg.2015.00289/full)

### Regla de corte

**Nivel de evidencia:** moderada

#### 1. Origen, teoría y evidencia

**Qué es.** Una regla de corte es una condición que la persona fija *antes* de empezar. Dice cuándo parar, cambiar de rumbo o abandonar. Ejemplo: "si en 2 horas el test sigue fallando, cambio de enfoque".

**El problema que resuelve.** Dos líneas de investigación muestran por qué cuesta parar:

- **Efecto del costo hundido** (*sunk cost*): seguir con algo porque ya se invirtió tiempo, dinero o esfuerzo, aunque esa inversión ya no se recupera. Arkes y Blumer (1985) vendieron abonos de teatro a tres precios, asignados al azar: precio completo, con un descuento pequeño y con un descuento grande. Quienes pagaron el precio completo fueron a más funciones durante la primera mitad de la temporada. En cuestionarios, quienes ya habían invertido en un proyecto estimaban que tenía más probabilidades de éxito que quienes no habían invertido.
- **Escalada de compromiso**: invertir más en un curso de acción que va mal para justificar la decisión inicial. Staw (1976) mostró que los estudiantes que se sentían responsables de una decisión que salió mal asignaban más dinero a esa misma opción. El metaanálisis de Sleesman, Conlon, McNamara y Miles (2012) reunió 166 muestras independientes. Un metaanálisis es un estudio que combina los resultados de muchos estudios. Confirmó que sentirse responsable de la decisión inicial y estar cerca de terminar el proyecto aumentan la escalada. El efecto del costo hundido fue más débil de lo esperado: muchos estudios lo mezclaban con la cercanía al final del proyecto, y sin esa mezcla el efecto era pequeño e incierto.

**Por qué funciona una regla fijada de antemano.** Simonson y Staw (1992) compararon en experimentos varias técnicas para reducir la escalada. Tres funcionaron mejor: fijar un **nivel mínimo de resultados** que, si no se alcanza, obliga a cambiar de política; hacer que los malos resultados se sientan menos amenazantes; y evaluar a las personas por su proceso de decisión y no por el resultado. Heath (1995) propuso que las personas fijan un **presupuesto mental** para controlar lo que gastan. En su experimento de laboratorio, las personas escalaban sobre todo cuando no fijaban un presupuesto o cuando el gasto era difícil de seguir. Sleesman y colegas (2012) citan este hallazgo como una pista para entender el costo hundido.

**Otras raíces.** Simon (1955, 1956) propuso la *racionalidad limitada* y el *satisficing*: dejar de buscar cuando una opción alcanza un nivel "suficientemente bueno". Gigerenzer, Todd y el grupo ABC (1999) describen las heurísticas simples (atajos de decisión) como piezas combinadas, y una de esas piezas es una **regla de detención** (*stopping rule*). Duke (2022), en el libro *Quit*, popularizó los **criterios de abandono** (*kill criteria*): un estado medible más una fecha límite ("estados y fechas"). Duke escribe divulgación, no investigación nueva.

**Nivel de evidencia: moderada.** El fenómeno que la regla combate tiene evidencia fuerte: la escalada de compromiso está muy estudiada. El costo hundido por sí solo tiene un efecto más discutido. Que fijar límites antes reduzca la escalada se apoya en experimentos de laboratorio (Simonson y Staw, 1992; Heath, 1995). No encontramos un metaanálisis de estas técnicas ni tamaños de efecto que pudiéramos verificar. Los criterios de abandono de Duke son práctica sin evidencia formal propia. No encontramos estudios con asistentes de IA.

#### 2. Proceso y buenas prácticas

**Pasos**

1. **En planificar, antes de empezar**, escribe la regla de corte. Debe tener un **estado** medible y un **límite**: tiempo, intentos o tokens (las unidades de texto que consume Claude). Formato: "Si [estado] cuando llegue a [límite], entonces [acción]".
2. **Elige la acción de antemano**: parar, cambiar de enfoque, volver a explorar en el PCRC o abrir una bifurcación pesada (una issue en GitHub).
3. **Pide a Claude que la vigile**: "avísame cuando llegue al límite".
4. **En monitorear**, compara el estado real con la regla en cada punto de control. Un punto de control es un momento fijado para revisar el avance, por ejemplo al final de cada intento.
5. **En controlar**, cuando se cumple la condición, ejecuta la acción sin renegociar en caliente. Si quieres cambiar la regla, decide en frío y anota por qué.
6. **En evaluar**, revisa si el límite era razonable y ajústalo para la próxima vez.

**Buenas prácticas**

- Fija la regla antes de invertir. Después, el costo hundido ya pesa.
- Usa criterios observables ("el test pasa"), no sensaciones ("siento que avanzo").
- Haz que la regla diga también qué hacer después, no solo cuándo parar.
- Pide a Claude que la recuerde. Un tercero que mira el proceso ayuda a no justificarse.
- Separa la decisión de parar del juicio sobre ti: cortar a tiempo es un buen proceso. Simonson y Staw (1992) encontraron que evaluar el proceso, y no el resultado, reduce la escalada.

**Errores comunes**

- "Solo un intento más", repetido muchas veces.
- Mover el límite justo cuando se alcanza.
- Reglas tan estrictas que cortan algo que iba bien. Heath (1995) también muestra que las personas a veces desescalan cuando no deberían, es decir, abandonan demasiado pronto.
- Mezclar lo ya invertido con el valor futuro. Pregúntate: "si empezara hoy, ¿elegiría este camino?".

#### 3. Ejemplo

**Contexto.** Lucía escribe con Claude la especificación de un sistema de permisos. Está en la fase *crear* del PCRC. Quiere expresar los permisos con una gramática formal propia. Trabaja por rondas: en cada ronda, Claude propone una versión de la gramática y Lucía la prueba contra 5 casos de ejemplo.

**Planificar (nivel metacognitivo).** Antes de empezar, Lucía escribe:

> "Regla de corte: si después de 3 rondas la gramática todavía no cubre los 5 casos de ejemplo, paro. Vuelvo a *explorar* y comparo con una tabla simple de roles. Claude, avísame al cerrar la tercera ronda."

**Monitorear.** En la ronda 2, Claude informa: "Cubre 3 de 5 casos. Fallan la herencia de roles y los permisos temporales." En ese momento aparece una idea nueva: "¿y si usamos un motor de políticas existente?". Lucía la registra como **bifurcación liviana** y la deja **aparcada**: "Lo anoto, pero ahora no lo abro".

**Controlar.** Al cerrar la ronda 3, Claude avisa:

> "Llegamos al límite: 4 de 5 casos. Falla la herencia de roles. Tu regla dice volver a explorar."

Lucía siente la tentación: "Falta poco, una ronda más". Se hace la pregunta de control: "Si empezara hoy, ¿elegiría esta gramática?". La respuesta honesta es que no lo sabe. Cumple la regla:

> "Paramos aquí. Volvemos a *explorar*: compara la gramática, la tabla de roles y la bifurcación aparcada del motor de políticas. Dame ventajas y riesgos de cada una."

**Resultado.** La comparación muestra que el motor de políticas ya resuelve la herencia de roles. La bifurcación pasa de *aparcada* a **convergida**: se integra al flujo principal. Lucía avanza a *decidir* con tres opciones claras. La gramática a medias no se tira: se guarda como **bifurcación pesada**, una issue en GitHub titulada "Gramática propia de permisos: 4 de 5 casos, falta herencia".

**Evaluar.** Al cerrar la sesión, Lucía anota: "El corte en 3 rondas fue útil. Sin la regla habría seguido dos horas más. Próxima vez: probar los casos más difíciles desde la ronda 1".

#### Fuentes

- [Arkes y Blumer (1985). The Psychology of Sunk Cost. Organizational Behavior and Human Decision Processes 35, 124-140](https://cognition.aau.at/bg/BA/Arkes%20%26%20Blumer%201985.pdf)
- [Sleesman, Conlon, McNamara y Miles (2012). Cleaning Up the Big Muddy: A Meta-Analytic Review of the Determinants of Escalation of Commitment. Academy of Management Journal 55(3), 541-562](https://gwern.net/doc/psychology/cognitive-bias/sunk-cost/2012-sleesman.pdf)
- [Simonson y Staw (1992). Deescalation Strategies: A Comparison of Techniques for Reducing Commitment to Losing Courses of Action. Journal of Applied Psychology 77(4), 419-426](https://gwern.net/doc/psychology/cognitive-bias/sunk-cost/1992-simonson.pdf)
- [Heath (1995). Escalation and De-escalation of Commitment in Response to Sunk Costs: The Role of Budgeting in Mental Accounting. OBHDP 62(1), 38-54](https://gwern.net/doc/psychology/cognitive-bias/sunk-cost/1995-heath.pdf)
- [Escalation of commitment (resumen general, incluye Staw 1976)](https://en.wikipedia.org/wiki/Escalation_of_commitment)
- [Duke (2022). Quit: The Power of Knowing When to Walk Away (editorial)](https://penguinrandomhouse.ca/books/692752/quit-by-annie-duke)
- [Kill Criteria (resumen de Duke: estados y fechas)](https://elliotrobia.substack.com/p/kill-criteria)

### Retroceder de fase

**Nivel de evidencia:** débil

#### 1. Origen, teoría y evidencia

**Retroceder de fase** quiere decir volver a una fase anterior del PCRC cuando la fase actual muestra que algo de antes estaba mal. Por ejemplo, volver de *implementar* a *explorar*. Nadie inventó la técnica como tal. Sale de tres líneas de trabajo.

- **Aprendizaje de doble ciclo** (Argyris y Schön, 1978, *Organizational Learning: A Theory of Action Perspective*). En el *ciclo simple*, la persona corrige un error dentro de las reglas que ya tiene y no cambia sus supuestos. En el *doble ciclo*, revisa los supuestos de base (metas, reglas, criterios) que llevaron al error. Retroceder de fase es una forma de doble ciclo. No basta con arreglar el código: hay que revisar la decisión o el problema que lo originó.
- **Creative Problem Solving (CPS)**, o resolución creativa de problemas. Es el modelo de Osborn y Parnes, que después revisaron Isaksen, Treffinger y colegas. Con el tiempo dejaron de presentarlo como una secuencia fija de etapas. Pasó a ser un conjunto de componentes que se usan en el orden que pide la situación. Isaksen y Treffinger (2004) resumen esa historia de versiones.
- **Investigación sobre diseño**. Dorst y Cross (2001) analizaron sesiones de nueve diseñadores industriales con experiencia. Vieron que el problema y la solución evolucionan juntos (*coevolución*): al crear una solución, el diseñador entiende mejor el problema y lo reformula. Guindon (1990) estudió a diseñadores de software. Encontró que no siguen un orden de arriba hacia abajo: saltan entre niveles según lo que descubren. Para Guindon, esto es una respuesta normal a problemas mal definidos, no un error. Atman y colegas (2007) compararon a ingenieros expertos con estudiantes. Los expertos dedicaron más tiempo a definir el problema y pasaron más veces de un paso de diseño a otro.

**Nivel de evidencia: débil.** Los estudios de diseño son descriptivos: observan a pocas personas mientras piensan en voz alta. Muestran que los expertos iteran, pero no prueban que enseñar a retroceder mejore los resultados. No hay ensayos controlados ni metaanálisis sobre la técnica, ni tamaños de efecto. El doble ciclo de Argyris es un marco teórico con mucha influencia y poca prueba experimental.

#### 2. Proceso y buenas prácticas

**Pasos**

1. **Detectar la señal.** Durante *monitorear*, aparece un síntoma: una prueba que no se puede escribir, una contradicción en la especificación, una solución que crece sin parar.
2. **Diagnosticar el origen.** Preguntar: "¿Este problema nació en esta fase o en una anterior?". Si es un detalle de la fase actual, se corrige ahí (ciclo simple).
3. **Elegir a qué fase volver.** Volver a la fase más cercana que explique el problema: *decidir* si la elección fue mala, *explorar* si el problema estaba mal entendido.
4. **Nombrar el supuesto que cae.** Escribir en una frase qué se creía y ya no se cree (doble ciclo).
5. **Conservar lo hecho.** Marcar qué partes del trabajo siguen sirviendo y cuáles quedan en duda.
6. **Rehacer y volver a avanzar.** Completar la fase anterior con la información nueva y seguir el ciclo desde ahí.

**Buenas prácticas**

- Fijar antes, en *planificar*, condiciones "si… entonces" para retroceder. Ejemplo: "si una regla necesita más de dos excepciones, reviso si la falla viene de una fase anterior".
- Distinguir retroceder de abrir una bifurcación. Si la idea nueva no invalida la fase actual, es una bifurcación: se aparca y se sigue.
- Pedirle a Claude que señale contradicciones con decisiones anteriores.

**Errores comunes**

- Parchear síntomas con ciclo simple cuando falla un supuesto.
- Volver al principio por reflejo y perder trabajo válido.
- Retroceder sin dejar escrito por qué. El mismo error vuelve en el siguiente ciclo.
- Retroceder sin parar por perfeccionismo. Hay que poner un límite de tiempo.

#### 3. Ejemplo

Lucía escribe con Claude la especificación de permisos de una aplicación de facturas. En *decidir* eligieron un modelo de roles fijos: administrador, contador y lector. Ahora están en *implementar* y escriben las reglas.

Claude propone la regla 14: "El contador puede aprobar facturas, salvo las de su propio departamento, salvo que sea jefe del departamento". Es la tercera regla con dos excepciones anidadas.

Lucía activa la condición que fijó al *planificar*:

> "Para. Es la tercera regla con dos excepciones. Mi condición era: si pasa esto, revisamos si la falla viene de antes. ¿El problema está en la redacción o en el modelo de roles?"

Claude responde que las excepciones dependen siempre del departamento y del cargo, y que esos datos no existen en el modelo de roles fijos. Lucía diagnostica:

> "Entonces no es un problema de *implementar*. La falla está en *decidir*, y quizás en *explorar*: nunca preguntamos si los permisos dependían de la estructura de la empresa."

Lucía nombra el supuesto que cae:

> "Supuesto descartado: 'los permisos dependen solo del rol'. Supuesto nuevo a verificar: 'dependen del rol y del departamento'."

Lucía vuelve a *explorar* y le pide a Claude tres preguntas para el cliente. En la conversación surge otra idea: registrar quién aprobó cada factura. La idea no invalida nada, así que no es motivo para retroceder: es una bifurcación. Como no se va a tratar en esta sesión y no quiere perderla, Lucía le pide a Claude abrir una issue en GitHub. Queda como bifurcación pesada, y ella sigue con lo suyo.

El cliente confirma que los permisos dependen del departamento. Lucía vuelve a *decidir* y elige un modelo de roles por departamento. Conserva las reglas 1 a 10, que no dependían de esto. Reescribe las reglas 11 a 14 como dos reglas nuevas, sin excepciones.

**Resultado:** en 40 minutos de retroceso, la especificación pasó de 14 reglas con 6 excepciones a 12 reglas sin excepciones. Además, quedó escrito qué supuesto cambió y por qué.

#### Fuentes

- [Double-loop learning (Wikipedia; Argyris y Schön, 1978)](https://en.wikipedia.org/wiki/Double-loop_learning)
- [Dorst y Cross (2001), Creativity in the design process: co-evolution of problem–solution, Design Studies 22(5), 425-437](https://oro.open.ac.uk/3278)
- [Guindon (1991), The opportunistic dynamics of the design process: some implications for HCI (resumen de seminario, Stanford)](https://hci.stanford.edu/seminar/abstracts/90-91/910403-guindon.html)
- [Atman et al. (2007), Engineering design processes: A comparison of students and expert practitioners, Journal of Engineering Education 96(4), 359-379](https://doi.org/10.1002/j.2168-9830.2007.tb00945.x)
- [Isaksen y Treffinger (2004), Celebrating 50 years of reflective practice: Versions of Creative Problem Solving, Journal of Creative Behavior 38(2), 75-101](https://doi.org/10.1002/j.2162-6057.2004.tb01234.x)

## Evaluar

### Revisión después de la acción (After Action Review, AAR)

**Nivel de evidencia:** fuerte

#### 1. Origen, teoría y evidencia

**Quién la creó.** La revisión después de la acción nació en el Ejército de EE.UU., que la usa desde hace décadas para aprender de sus ejercicios de entrenamiento (Tannenbaum y Cerasoli, 2013). Morrison y Meliza (1999) reúnen su historia y su base de investigación en un informe del Instituto de Investigación del Ejército (ARI Special Report 42). Suele contarse que surgió en los años 70, como alternativa a la crítica de arriba hacia abajo, y que se consolidó en el Centro Nacional de Entrenamiento. No pudimos abrir el informe original para confirmar esas fechas y detalles.

**Teoría.** Una AAR es una conversación breve y estructurada justo después de una acción. Compara lo planeado con lo que pasó, busca por qué hubo diferencias y decide qué mantener y qué cambiar. Combina retroalimentación (información sobre el resultado propio), reflexión y discusión. No busca culpables: busca aprender.

**Evidencia.**
- Tannenbaum y Cerasoli (2013), metaanálisis en *Human Factors* (un metaanálisis combina los resultados de muchos estudios): 46 muestras y 2.136 participantes. Efecto medio d = 0,67. La d mide cuánto se separan dos grupos; 0,5 se considera moderado y 0,8 grande. Las revisiones posteriores (en inglés, *debriefs*) mejoraron el desempeño entre un 20 % y un 25 %. El efecto fue parecido en equipos e individuos, en simulación y en trabajo real, en medicina y fuera de ella. Funcionó mejor cuando la revisión estaba alineada: si se quiere mejorar al equipo, se revisa y se mide al equipo. La facilitación y la estructura parecían ayudar, pero los datos no alcanzaron para confirmarlo.
- Keiser y Arthur (2021), metaanálisis en *Journal of Applied Psychology*: 61 estudios y 107 tamaños de efecto. Efecto medio d = 0,79 en varios resultados del entrenamiento. Dos factores ayudaron de forma constante: la alineación con el equipo o el individuo y revisar con registros objetivos (video, documentos) en vez de solo con la memoria. Una estructura alta funcionó mejor en el ámbito militar; en salud, estructura alta y baja rindieron parecido.
- Ellis y Davidi (2005), cuasiexperimento de campo con soldados en ejercicios de navegación: revisar éxitos y fallos mejoró más el desempeño que revisar solo los fallos.

**Nivel de evidencia: fuerte** para mejorar el desempeño. Los estudios provienen sobre todo de entrenamiento militar y médico. No hay estudios sobre AAR aplicada al trabajo con un asistente de IA.

#### 2. Proceso y buenas prácticas

**Pasos**
1. **Hacerla pronto.** Al cerrar una sesión o una fase, con los hechos frescos.
2. **¿Qué queríamos lograr?** Repetir el objetivo y el criterio de éxito definidos al planificar.
3. **¿Qué pasó en realidad?** Describir hechos, no opiniones: archivos, pruebas, decisiones.
4. **¿Por qué hubo diferencias?** Buscar causas en el proceso, no en personas.
5. **¿Qué mantener y qué mejorar?** Sacar dos o tres lecciones concretas.
6. **Convertir lecciones en acción.** Escribir cada una como regla o plan "si… entonces" y guardarla donde se vaya a ver: el CLAUDE.md (archivo de instrucciones que Claude lee al empezar), un issue (tarea registrada en GitHub) o un documento.

**Buenas prácticas**
- Revisar también los éxitos, no solo los fallos (Ellis y Davidi, 2005).
- Apoyarse en registros objetivos (diff, resultados de pruebas, registro de la sesión) y no solo en la memoria (Keiser y Arthur, 2021).
- Usar siempre las mismas preguntas. Facilita la revisión, aunque la evidencia sobre cuánto ayuda la estructura es mixta.
- Ajustar la duración al tamaño de la sesión. No hay una cifra probada para este uso.

**Errores comunes**
- Buscar culpables: frena la honestidad.
- Quedarse en "salió bien" o "salió mal" sin causas.
- Sacar lecciones que nadie registra: no cambian nada.
- Hacerla días después, cuando ya no se recuerdan los detalles.

#### 3. Ejemplo

Lucía termina una sesión con Claude. Escribió la especificación de un módulo de exportación y su primera implementación. Antes de cerrar, abre la fase **evaluar** del PCM.

**Lucía:** "Hagamos una revisión después de la acción. Primero: ¿qué queríamos lograr hoy?"

**Claude:** "Al planificar dijimos: especificación aprobada y exportación a CSV con todas las pruebas pasando, en dos horas."

**Lucía:** "¿Qué pasó en realidad? Usá el diff y el resultado de las pruebas."

**Claude:** "La especificación quedó aprobada. La exportación funciona, pero dos pruebas fallan con caracteres especiales. Usamos tres horas. Abrimos dos bifurcaciones livianas: el formato JSON (aparcada) y el manejo de zonas horarias (convergida en la especificación)."

**Lucía:** "¿Por qué hubo diferencias?"

**Claude:** "Pasamos de **decidir** a **implementar** sin ejemplos de datos reales. Los caracteres especiales aparecieron recién al **verificar**. La bifurcación de zonas horarias costó 40 minutos porque la exploramos en medio de la fase."

**Lucía:** "¿Y qué salió bien?"

**Claude:** "Escribir las pruebas antes del código detectó el error enseguida. Convergir la bifurcación en la especificación evitó rehacer trabajo después."

**Lucía:** "Bien. Lecciones:
1. Mantener: pruebas antes del código.
2. Mejorar: si una bifurcación pasa de 15 minutos, entonces la aparcamos y seguimos.
3. Mejorar: antes de implementar, pedir tres ejemplos de datos reales."

Lucía agrega la regla 2 al CLAUDE.md del proyecto. Convierte la bifurcación aparcada del JSON en bifurcación pesada: un issue en GitHub. La falla de caracteres especiales queda como primera tarea de la próxima sesión.

**Resultado:** en la sesión siguiente, Claude pide los ejemplos de datos antes de implementar. Aparece una bifurcación sobre compresión y se aparca a los 10 minutos. La fase termina dentro del tiempo planificado.

#### Fuentes

- [Tannenbaum y Cerasoli (2013). Do team and individual debriefs enhance performance? A meta-analysis. Human Factors, 55(1), 231-245 (PubMed)](https://pubmed.ncbi.nlm.nih.gov/23516804/)
- [Tannenbaum y Cerasoli (2013), texto completo (CEBMa)](https://cebma.org/assets/Uploads/Tannenbaum-Cerasoli.pdf)
- [Keiser y Arthur (2021). A meta-analysis of the effectiveness of the after-action review (or debrief) and factors that influence its effectiveness. Journal of Applied Psychology, 106(7), 1007-1032 (PubMed)](https://pubmed.ncbi.nlm.nih.gov/32852990/)
- [Paul (2021). Umbrella summary: After-action reviews. QIC-WD (resume a Keiser y Arthur)](https://www.qic-wd.org/sites/default/files/Umbrella%20Summary%20-%20After-Action%20Reviews%20050221.pdf)
- [Ellis y Davidi (2005). After-event reviews: drawing lessons from successful and failed experience. Journal of Applied Psychology, 90(5), 857-871 (PubMed)](https://pubmed.ncbi.nlm.nih.gov/16162059/)
- [Morrison y Meliza (1999). Foundations of the After Action Review Process. ARI Special Report 42 (DTIC)](https://apps.dtic.mil/sti/pdfs/ADA368651.pdf)

### Exam wrapper

**Nivel de evidencia:** mixta

#### 1. Origen, teoría y evidencia

**Quién la propuso.** Marsha Lovett, de la Universidad Carnegie Mellon, describió el *exam wrapper* ("envoltorio del examen") en un capítulo de 2013: "Make exams worth more than the grade: Using exam wrappers to promote metacognition". El capítulo está en el libro *Using reflection and metacognition to improve student learning*, editado por Kaplan, Silver, LaVaque-Manty y Meizlish (2013, editorial Stylus). Un exam wrapper es una hoja breve que la persona completa cuando recibe el resultado de un examen. Tiene tres partes: cómo se preparó, qué errores cometió y de qué tipo, y qué cambiará la próxima vez.

**Teoría.** Se apoya en el aprendizaje autorregulado (Zimmerman, 2002): la persona fija metas, observa cómo aprende y ajusta sus estrategias. La idea es usar el resultado para mirar el propio proceso, y no solo la nota. En nuestro vocabulario, es una herramienta del nivel metacognitivo: actúa en la fase de evaluar del PCM y su salida alimenta la fase de planificar del ciclo siguiente.

**Evidencia.**
- Lovett (2013) informa datos de sus cursos introductorios de matemática y ciencias. Los estudiantes que usaban wrappers en más cursos a la vez adoptaban más estrategias de estudio efectivas. Es un capítulo de libro con datos de aula, no un experimento controlado.
- Soicher y Gurung (2017, *Psychology Learning and Teaching*, 16(1), 64–73) hicieron un experimento con 86 estudiantes en un solo curso. Compararon tres grupos: wrapper real, wrapper "falso" y grupo de control (un grupo que no recibe la intervención). No hubo diferencias en los tres exámenes, en la nota final ni en la conciencia metacognitiva, medida con el Metacognitive Awareness Inventory (MAI, un cuestionario de autoevaluación).
- Hodges y otros (2020, *Journal of College Science Teaching*) estudiaron nueve cursos grandes de ciencias con 1.894 estudiantes. Cinco cursos usaban wrappers y cuatro de física sirvieron de comparación. En primer año encontraron una correlación positiva pero pequeña entre usar wrappers y la nota (r de 0,10 a 0,14; r mide cuánto se mueven juntas dos variables, de 0 a 1). La relación fue más fuerte donde el wrapper era obligatorio o daba puntos. En quienes cursaban varias materias con wrappers, el uso se relacionó con el promedio general (r = 0,22), pero solo en hombres. Es un estudio correlacional: muestra que dos cosas van juntas, no que una cause la otra. El puntaje del MAI no se relacionó con el uso de wrappers.
- Weimer (2017, *Faculty Focus*) revisa estos resultados contradictorios. Propone que el efecto puede depender de las actividades que acompañan al wrapper, de usarlo en varios cursos y de que la persona realmente cambie sus hábitos.

**Nivel: evidencia mixta.** Hay pocos estudios bien controlados y no encontramos metaanálisis (estudios que combinan los resultados de muchos estudios). El efecto parece depender del uso repetido y de que la persona actúe sobre su plan.

#### 2. Proceso y buenas prácticas

**Pasos**
1. **Definir el "examen".** Elegir un resultado verificable: una revisión de código, una prueba que falla, la lectura de una especificación por otra persona.
2. **Recordar la preparación.** Anotar qué se hizo antes y cuánto tiempo llevó cada cosa.
3. **Clasificar los errores.** Agrupar cada fallo por tipo, por ejemplo: concepto mal entendido, descuido, falta de verificación, requisito ausente.
4. **Buscar el patrón.** Ver qué tipo de error domina y qué parte de la preparación lo explica.
5. **Escribir un plan concreto.** Una o dos acciones para el próximo ciclo, de preferencia como plan "si… entonces" (una regla que une una situación con una acción).
6. **Releer el plan antes del siguiente examen.** Leer el wrapper anterior al empezar a planificar.

**Buenas prácticas y errores comunes**
- Repetirlo en cada ciclo. Usado en un solo curso, no mostró efecto (Soicher y Gurung, 2017).
- Hacerlo obligatorio para uno mismo. En Hodges y otros (2020) la relación con la nota fue más fuerte donde el wrapper era obligatorio.
- Completarlo pronto, cuando el resultado está fresco.
- Usar preguntas fijas, siempre las mismas, para poder comparar un ciclo con otro.
- Contar los errores por tipo, no solo describirlos.
- Error común: quedarse en "tengo que esforzarme más". El plan debe nombrar una acción observable.
- Error común: escribirlo y no releerlo. Sin el paso 6, la técnica pierde su sentido.

#### 3. Ejemplo

Lucía escribe con Claude la especificación de un módulo de pagos. Recorre el PCRC: explora, crea, decide, implementa y verifica. Un revisor devuelve la especificación con 9 observaciones. Ese es su "examen".

Al cerrar, Lucía pide: *"Hagamos un exam wrapper de esta revisión. Hazme las preguntas una por una."*

**1. Preparación.** Claude pregunta cómo repartió el tiempo. Lucía responde: *"Casi todo en crear. En verificar solo releí el texto, no lo comparé con los casos de uso."*

**2. Errores por tipo.** Juntos clasifican las 9 observaciones:
- 5 son requisitos ausentes (reembolsos parciales, monedas).
- 3 son ambigüedades de redacción.
- 1 es un error de concepto sobre idempotencia (que repetir una operación dé el mismo resultado).

**3. Patrón.** Lucía escribe: *"Los requisitos ausentes vienen de que en explorar no listé los casos límite. Los reembolsos aparecieron como bifurcación liviana, la dejé aparcada y nunca la retomé."*

**4. Plan.** Lucía redacta dos acciones:
- *"Si cierro la fase explorar, entonces Claude me muestra todas las bifurcaciones livianas abiertas o aparcadas, y decido cada una: descartarla, hacerla converger o pasarla a issue en GitHub (bifurcación pesada)."*
- *"Si llego a verificar, entonces comparo cada caso de uso con la especificación, uno por uno."*

**5. Relectura.** En la sesión siguiente, Lucía abre con: *"Antes de planificar, léeme el wrapper de la especificación de pagos."*

**Resultado.** En la especificación siguiente, la revisión trae 3 observaciones y ninguna es un requisito ausente. Al cerrar la fase explorar, Claude listó dos bifurcaciones aparcadas: una convergió en un requisito nuevo y la otra pasó a issue en GitHub. Lucía repite el wrapper. Ahora el tipo de error dominante son las ambigüedades. Ese será su foco en el próximo ciclo.

#### Fuentes

- [Hodges et al. (2020). Effect of Exam Wrappers on Student Achievement in Multiple, Large STEM Courses. Journal of College Science Teaching](https://www.nsta.org/journal-college-science-teaching/journal-college-science-teaching-septemberoctober-2020/effect-exam)
- [Hodges et al. (2020), texto completo en ERIC](https://files.eric.ed.gov/fulltext/EJ1290331.pdf)
- [Soicher & Gurung (2017). Do Exam Wrappers Increase Metacognition and Performance? A Single Course Intervention. Psychology Learning and Teaching, 16(1), 64–73 (ficha en Oregon State; DOI 10.1177/1475725716661872)](https://liberalarts.oregonstate.edu/biblio/do-exam-wrappers-increase-metacognition-and-performance-single-course-intervention)
- [Weimer (2017). Does This Strategy Work? A Look at Exam Wrappers. Faculty Focus](https://www.facultyfocus.com/articles/educational-assessment/strategy-work-look-exam-wrappers/)
- [Lovett (2013), capítulo 2: Make Exams Worth More Than the Grade (ficha en SERC, Carleton)](https://serc.carleton.edu/resources/45660.html)
- [Wrapping up Metacognition: Pre- and Post-Exam Interventions (blog, apoyo)](https://www.improvewithmetacognition.com/2019/06/)

### Preguntas de evaluación

**Nivel de evidencia:** moderada

#### 1. Origen, teoría y evidencia

**Quién la propuso.** Schraw (1998) publicó la lista de control de regulación (*regulatory checklist*) en el artículo "Promoting general metacognitive awareness" (*Instructional Science*, 26, págs. 113-125). La lista tiene preguntas fijas para tres fases: planificar, monitorear y evaluar. Las de evaluar son: ¿logré mi objetivo?, ¿qué funcionó?, ¿qué no funcionó?, ¿qué haría distinto la próxima vez?

**Teoría.** Schraw parte de los trabajos de Flavell y de Brown sobre metacognición. Divide la metacognición en dos partes: el conocimiento de la cognición (saber cómo pienso) y la regulación de la cognición (dirigir cómo pienso). Evaluar es la parte de la regulación que mira el resultado y el método después de actuar. Schraw y Dennison (1994) crearon el Inventario de Conciencia Metacognitiva (MAI), un cuestionario de 52 preguntas. Agrupa ocho subescalas (partes que miden una habilidad concreta) en esas dos partes grandes, y una de ellas es la evaluación. Algunos estudios posteriores encontraron más apoyo para las dos partes grandes que para las ocho subescalas.

**Evidencia.**
- No encontré estudios que prueben la lista de Schraw sola, aislada de otras técnicas.
- Sí hay evidencia sobre programas de preguntas metacognitivas que incluyen la reflexión. El método IMPROVE de Mevarech y Kramarski (1997) usa preguntas que el alumno se hace a sí mismo en clases de matemáticas. En dos estudios (247 y 265 alumnos), sus alumnos superaron a los grupos de control. Gran parte de la investigación sobre IMPROVE viene del mismo grupo.
- La Education Endowment Foundation (EEF) estima que enseñar metacognición y autorregulación en la escuela da unos 7 meses extra de progreso. En la actualización de 2018, el tamaño de efecto fue 0,54. El tamaño de efecto mide cuánto mejora un grupo frente a otro; 0,5 se considera un efecto medio.
- Tannenbaum y Cerasoli (2013) hicieron un metaanálisis (un estudio que combina los resultados de muchos estudios) sobre *debriefs*, es decir, revisiones estructuradas después de una tarea. Reunieron 46 muestras con 2136 personas. Los grupos que hacían la revisión rindieron en promedio un 25 % más que los grupos de control (d = 0,67). El efecto fue parecido en equipos e individuos. Rindió más cuando las preguntas, el foco y la medición apuntaban al mismo objetivo. La guía de un facilitador y la estructura también parecen ayudar.
- Di Stefano, Gino, Pisano y Staats (2014, documento de trabajo) hicieron un estudio de campo en un centro de atención telefónica de Wipro, en India. Los empleados que dedicaban los últimos 15 minutos del día a escribir sobre lo aprendido sacaron cerca de un 23 % más en el examen final de capacitación.

**Nivel de evidencia: moderado.** La reflexión estructurada después de actuar tiene buen respaldo. La lista exacta de Schraw es una forma razonable de aplicarla, pero nadie la probó por separado.

#### 2. Proceso y buenas prácticas

**Pasos**
1. **Elegir el momento.** Cierra una unidad de trabajo: el final de una fase del PCRC (por ejemplo, implementar o verificar), de una sesión o de una tarea.
2. **Recuperar el objetivo.** Lee el objetivo que escribiste al planificar. Sin objetivo escrito, la evaluación queda vaga.
3. **¿Logré mi objetivo?** Responde sí, no o en parte, con un hecho que lo pruebe (un test que pasa, una sección cerrada).
4. **¿Qué funcionó?** Nombra una o dos acciones concretas, no impresiones.
5. **¿Qué no funcionó?** Nombra dónde perdiste tiempo o cometiste un error, y su causa probable.
6. **¿Qué haría distinto?** Convierte la respuesta en una regla para la próxima vez. Si puedes, escríbela como plan "si… entonces": una condición concreta y la acción que harás cuando se cumpla.
7. **Revisar las bifurcaciones.** Repasa las bifurcaciones livianas abiertas o aparcadas. Decide para cada una: descartarla, dejarla convergida o pasarla a pesada (issue en GitHub).
8. **Guardar la lección.** Escríbela donde la vas a volver a leer (CLAUDE.md, notas del proyecto).

**Buenas prácticas**
- Usa siempre las mismas preguntas. La repetición vuelve el hábito automático.
- Responde por escrito y en pocas líneas.
- Evalúa también el método, no solo el resultado.
- Compara el resultado con la confianza que tenías al monitorear. Así mejora tu calibración, es decir, el ajuste entre lo que crees que sabes y lo que de verdad logras.
- Hazlo enseguida, cuando el recuerdo está fresco.

**Errores comunes**
- Responder "todo bien" sin evidencia.
- Listar culpas en vez de causas.
- Sacar lecciones y no guardarlas en ningún lugar.
- Evaluar sin haber fijado antes un objetivo.

#### 3. Ejemplo

Lucía escribe con Claude la especificación del módulo de exportación de un sistema de facturación. Al planificar, escribió este objetivo: "Cerrar los requisitos de exportación a CSV y PDF, con un ejemplo por requisito".

Termina la fase **verificar** del PCRC y le pide a Claude:

> "Guíame con las preguntas de evaluación. Una por una, y espera mi respuesta."

**¿Logré mi objetivo?**
> "En parte. CSV tiene 6 requisitos con ejemplo. PDF tiene 4 requisitos y solo 2 ejemplos."

**¿Qué funcionó?**
> "Escribir primero el ejemplo y después el requisito. Así encontré dos ambigüedades en el formato de fechas."

**¿Qué no funcionó?**
> "Pasé 40 minutos discutiendo la paginación del PDF. Era una bifurcación y no la aparqué a tiempo."

**¿Qué haría distinto?**
> "Si un tema nuevo me ocupa más de 10 minutos, entonces lo aparco como bifurcación liviana y sigo con el objetivo."

Claude repasa las bifurcaciones de la sesión:
- "Paginación del PDF": abierta.
- "Exportar a Excel": aparcada.
- "Usar otra librería de PDF": descartada.

Lucía decide:
> "Paginación pasa a pesada: abre un issue y enlázalo a la spec. Excel queda descartada por ahora."

**Resultado.** En 8 minutos Lucía sabe qué falta (dos ejemplos de PDF) y tiene un issue para la paginación. También agrega una regla nueva al CLAUDE.md del proyecto: el plan "si… entonces" de los 10 minutos. En la sesión siguiente, Claude le avisa cuando una bifurcación llega a ese límite.

#### Fuentes

- [Schraw (1998). Promoting general metacognitive awareness. Instructional Science 26, 113-125](https://doi.org/10.1023/A:1003044231033)
- [Metacognition techniques: lista de control de regulación de Schraw (OpenLearn)](https://www.open.edu/openlearncreate/mod/page/view.php?id=236090)
- [Metacognitive Awareness Inventory, Schraw y Dennison (1994)](https://edinstruments.org/node/1563)
- [Mevarech y Kramarski (1997). IMPROVE: método multidimensional para enseñar matemáticas](https://education.biu.ac.il/en/node/266)
- [Tannenbaum y Cerasoli (2013). Do team and individual debriefs enhance performance? A meta-analysis](https://pubmed.ncbi.nlm.nih.gov/23516804/)
- [Evidence for Learning: actualización de la Toolkit sobre metacognición (2018)](https://www.evidenceforlearning.org.au/news/updates-to-the-teaching-and-learning-toolkit)
- [Di Stefano, Gino, Pisano y Staats (2014). Learning by thinking: how reflection can spur progress along the learning curve (SSRN)](https://doi.org/10.2139/ssrn.2414478)

### Calibración

**Nivel de evidencia:** moderada

#### 1. Origen, teoría y evidencia

**Qué es.** La calibración compara la confianza que tenías con el resultado real. Una persona está bien calibrada si, de todas las veces que dice "estoy 80% seguro", acierta más o menos el 80%. Si acierta menos, tiene **exceso de confianza**. Si acierta más, tiene **falta de confianza**.

**Origen.** La medida viene de la meteorología. Brier (1950) propuso una puntuación para evaluar pronósticos de probabilidad. El **Brier score** es el promedio de (probabilidad dicha − resultado)², donde el resultado vale 1 si ocurrió y 0 si no. Cero es perfecto. Decir siempre "50%" da 0,25.

En psicología, Lichtenstein, Fischhoff y Phillips (1982) revisaron los estudios hasta 1980 en un capítulo del libro *Judgment under Uncertainty* (editado por Kahneman, Slovic y Tversky). Sus conclusiones:
- La gente suele estar mal calibrada, casi siempre con exceso de confianza.
- El exceso crece con la dificultad: en tareas difíciles somos demasiado optimistas, y en tareas fáciles, algo pesimistas (el **efecto de la dificultad**).
- El entrenamiento mejora la calibración, pero solo hasta cierto punto.

Kruger y Dunning (1999) describieron el **efecto Dunning-Kruger**: quienes rinden peor sobrestiman más su rendimiento. El efecto es discutido. McIntosh y Della Sala (2022) sostienen que el patrón puede salir de la regresión a la media (los extremos de una medida tienden a acercarse al promedio en la siguiente). Magnus y Peresetsky (2022) lo explican por los límites de la escala: quien saca 95 sobre 100 casi no puede sobrestimarse, y quien saca 5 casi no puede subestimarse. Conviene no usarlo como argumento central.

**Teoría.** La calibración es parte del **monitoreo** metacognitivo: juzgar qué tan bien va el propio pensamiento. En el PCM, en la fase evaluar se compara lo que se juzgó al monitorear con lo que pasó. Ese desvío alimenta la siguiente planificación.

**Evidencia sobre si se puede entrenar.**
- Carpenter y colaboradores (2019) entrenaron a personas durante ocho sesiones en una tarea perceptiva. Un grupo recibía retroalimentación sobre qué tan bien su confianza seguía a sus aciertos. El grupo de control recibía retroalimentación solo sobre sus aciertos. El primer grupo mejoró la calibración (medida con una puntuación equivalente a 1 menos el Brier score), y la mejora se transfirió a una tarea de memoria no entrenada.
- Mellers y colaboradores (2014) mostraron, en un torneo de pronósticos geopolíticos de dos años, que una capacitación en razonamiento probabilístico, junto con trabajar en equipo, mejoró la calibración y la precisión de los pronósticos.
- En aulas reales, la retroalimentación parece clave. Callender, Franco-Watkins y Roberts (2016) vieron, en un curso universitario, que el exceso de confianza bajó del primer al segundo examen solo en los estudiantes que recibían retroalimentación sobre su rendimiento y sus juicios. En el semestre sin retroalimentación no hubo esa mejora.

**Nivel de evidencia:** fuerte en que existe la mala calibración, sobre todo el exceso de confianza. Moderada en que la retroalimentación repetida la mejora. Débil y discutida para el efecto Dunning-Kruger.

#### 2. Proceso y buenas prácticas

**Pasos**
1. **Predice antes de actuar.** Al planificar o monitorear, escribe una afirmación verificable y una probabilidad: "80% de que los tests pasan sin cambios".
2. **Usa una escala fija.** Por ejemplo 50, 60, 70, 80, 90, 99%. Así es fácil comparar.
3. **Registra.** Guarda cada predicción en un lugar visible: la nota de la sesión o la issue.
4. **Compara en evaluar.** Marca cada predicción con 1 (ocurrió) o 0 (no ocurrió).
5. **Calcula el desvío.** Con pocas predicciones basta comparar la confianza media con la tasa de aciertos. Con muchas, calcula el Brier score.
6. **Ajusta.** Decide un cambio concreto para la próxima planificación: más margen, más verificación, otra estimación.

**Buenas prácticas**
- Predice sobre cosas que se puedan comprobar sin discusión. "El diseño es bueno" no sirve. "El revisor aprueba sin cambios" sí.
- Junta varias predicciones antes de sacar conclusiones. Una sola no dice nada.
- Mira el patrón por tipo de tarea. El exceso de confianza suele aparecer en lo difícil o nuevo.
- Pide a Claude que te pregunte tu confianza antes de verificar, y que te la recuerde al cerrar.

**Errores comunes**
- Escribir la confianza después de ver el resultado. Eso anula la técnica.
- Usar siempre 50% para no equivocarse. Es una forma de no comprometerse.
- Confundir calibración con acierto. Puedes acertar poco y estar bien calibrado si tu confianza era baja.
- Sentirse juzgado. El desvío es un dato para ajustar, no una nota.

#### 3. Ejemplo

**Contexto.** Lucía escribe con Claude la especificación de un módulo de facturación. Está por entrar a la fase verificar del PCRC.

**Predicción (monitorear).** Antes de verificar, Lucía escribe en la nota de la sesión:

> "Predicciones:
> P1: los 6 criterios de aceptación (las condiciones que la especificación debe cumplir) se cumplen. 90%.
> P2: no aparece ninguna contradicción con la especificación de impuestos. 80%.
> P3: termino la verificación en 30 minutos. 70%."

Luego le pide a Claude: "Revisa la especificación contra los criterios y contra la especificación de impuestos. No me digas el resultado hasta que confirme que mis predicciones están guardadas".

**Durante la verificación.** Claude encuentra que el criterio 4 (redondeo de montos) no está cubierto. También detecta un choque: la especificación de impuestos redondea por línea y la nueva redondea por total. Lucía abre una bifurcación liviana: "Abro bifurcación: regla única de redondeo. Estado: abierto". Al final de la sesión ve que afecta a otros módulos y la convierte en una bifurcación pesada: una issue en GitHub.

**Evaluar.** Al cerrar, Lucía compara:

| Predicción | Confianza | Resultado |
|---|---|---|
| P1 | 90% | 0 |
| P2 | 80% | 0 |
| P3 | 70% | 0 (tardó 55 min) |

Le pide a Claude: "Calcula mi Brier score y dime qué patrón ves en las últimas tres sesiones".

Claude responde: "Hoy: (0,81 + 0,64 + 0,49) / 3 = 0,65. En las tres sesiones tienes 12 predicciones con confianza media de 82% y 5 aciertos (42%). El desvío aparece sobre todo cuando la especificación toca otra especificación".

**Ajuste para la próxima planificación.** Lucía escribe en el plan:

> "Si la especificación depende de otra, entonces bajo mi confianza a 60% como máximo y reservo el doble de tiempo para verificar las dependencias".

**Resultado.** Dos semanas después, sus predicciones sobre especificaciones con dependencias aciertan 4 de 6 (67%) con confianza media de 65%. Su exceso de confianza bajó, y planifica la verificación con tiempos más realistas.

#### Fuentes

- [Lichtenstein, Fischhoff y Phillips (1982). Calibration of probabilities: The state of the art to 1980. En Kahneman, Slovic y Tversky (eds.), Judgment under Uncertainty (Cambridge)](https://www.cambridge.org/core/books/abs/judgment-under-uncertainty/calibration-of-probabilities-the-state-of-the-art-to-1980/9F0C9EC2997AEEB6DDDB304C2F935A16)
- [Calibrated probability assessment (Wikipedia, apoyo)](https://en.wikipedia.org/wiki/Calibrated_probability_assessment)
- [Carpenter y colaboradores (2019). Domain-general enhancements of metacognitive ability through adaptive training. Journal of Experimental Psychology: General (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6390881)
- [Mellers y colaboradores (2014). Psychological strategies for winning a geopolitical forecasting tournament. Psychological Science (DOI)](https://doi.org/10.1177/0956797614524255)
- [Callender, Franco-Watkins y Roberts (2016). Improving metacognition in the classroom through instruction, training, and feedback. Metacognition and Learning](https://scholars.uky.edu/en/publications/improving-metacognition-in-the-classroom-through-instruction-trai/)
- [Magnus y Peresetsky (2022). A statistical explanation of the Dunning-Kruger effect (Frontiers in Psychology)](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.840180/full)
- [McIntosh y Della Sala (2022). The Dunning-Kruger effect and its discontents (The Psychologist, BPS)](https://bps.org.uk/psychologist/dunning-kruger-effect-and-its-discontents)

### Retrospectiva (empezar, dejar, seguir)

**Nivel de evidencia:** moderada

#### 1. Origen, teoría y evidencia

**Quién la propuso.** Kerth (2001) escribió *Project Retrospectives: A Handbook for Team Reviews*. Allí define la retrospectiva como una reunión para mirar atrás y aprender, no para buscar culpables. Su "Directiva Primaria" (la regla que abre cada retrospectiva) dice que todos hicieron lo mejor que pudieron con lo que sabían, sus habilidades, sus recursos y la situación de ese momento. El mismo año, el Manifiesto Ágil (2001) pidió que el equipo reflexione a intervalos regulares sobre cómo ser más efectivo y ajuste su forma de trabajar. Derby y Larsen (2006), en *Agile Retrospectives: Making Good Teams Great*, propusieron cinco pasos: preparar el ambiente, reunir datos, generar ideas, decidir qué hacer y cerrar.

El formato "empezar, dejar, seguir" (en inglés *start, stop, continue*) es una plantilla para el paso "decidir qué hacer". No encontré un autor ni una fecha de origen verificables. Algunos blogs lo ubican en las prácticas de equipos de empresa de los años setenta, pero solo citan otros blogs.

**Teoría.** La idea viene del aprendizaje por experiencia: actuar, revisar lo que pasó, sacar una lección y cambiar la próxima acción. En el vocabulario del documento es la fase *evaluar* del PCM. Cierra un ciclo y alimenta la fase *planificar* del siguiente.

**Evidencia.**
- Tannenbaum y Cerasoli (2013) hicieron un metaanálisis (un estudio que combina los resultados de muchos estudios) sobre los *debriefs*, es decir, revisiones guiadas después de una tarea. Reunieron 46 muestras con 2.136 personas. Los grupos que hacían la revisión mejoraron cerca de un 25 % frente a los grupos de control (d = 0,67, un efecto de tamaño medio a grande). El efecto fue parecido en equipos y en personas solas. La mejora fue mayor cuando los participantes, el objetivo de la revisión y la forma de medir estaban alineados. La facilitación y la estructura podrían ayudar también, pero ese resultado es menos firme.
- Ellis y Davidi (2005) estudiaron soldados en ejercicios de navegación. Los que revisaban sus fallos y también sus éxitos mejoraron más que los que revisaban solo los fallos. Esto apoya la columna "seguir".
- Lehtinen, Itkonen y Lassenius (2017) analizaron 37 retrospectivas de equipos de una gran organización de software, a lo largo de casi tres años. Los equipos hablaban sobre todo de temas cercanos que podían controlar. Vieron dos riesgos: las opiniones rara vez se contrastaban con datos, lo que abría la puerta a sesgos; y algunos temas volvían una y otra vez sin resolverse.

**Nivel de evidencia.** Las revisiones estructuradas en general tienen evidencia **moderada**: un metaanálisis con resultados consistentes, pero con pocas personas en total. El formato "empezar, dejar, seguir" en sí es una **práctica sin evidencia formal**: no encontré estudios que lo comparen con otros formatos.

#### 2. Proceso y buenas prácticas

**Pasos**
1. **Fijar el alcance.** Elegir qué ciclo se revisa: una sesión, una fase del PCRC o un entregable.
2. **Reunir datos.** Leer hechos antes de opinar: commits (los cambios guardados en git), tests (pruebas automáticas) que fallaron, bifurcaciones abiertas o aparcadas, tiempo usado.
3. **Llenar las tres columnas.** *Empezar*: qué no hicimos y conviene hacer. *Dejar*: qué hicimos y nos costó o no sirvió. *Seguir*: qué funcionó y hay que mantener.
4. **Elegir pocas acciones.** Una o dos por columna como máximo. Escribirlas como regla concreta, mejor en forma "si… entonces".
5. **Guardar el resultado.** Las reglas duraderas van a un CLAUDE.md (el archivo de instrucciones que Claude lee al empezar cada sesión). Las tareas grandes pasan a ser una bifurcación pesada (un issue en GitHub).
6. **Revisar al abrir el próximo ciclo.** Leer las acciones en la fase *planificar* y, en la siguiente retrospectiva, comprobar si se cumplieron.

**Buenas prácticas**
- Basarse en hechos, no en impresiones (Lehtinen y otros, 2017).
- No saltarse "seguir": revisar los éxitos también enseña (Ellis y Davidi, 2005).
- Dejar claro qué se quiere mejorar y cómo se va a medir antes de empezar (Tannenbaum y Cerasoli, 2013).
- Usar una estructura fija y hacerla breve. Cinco a diez minutos bastan al cerrar una sesión.
- Pedirle a Claude que haga de facilitador: que haga las preguntas, sin decidir por la persona.

**Errores comunes**
- Llenar listas largas sin elegir ninguna acción.
- Escribir acciones vagas ("ser más ordenado").
- No revisar nunca si las acciones anteriores se cumplieron.
- Volver al mismo tema en cada retrospectiva sin cambiar nada: si no se puede resolver, abrir una bifurcación pesada o descartarlo.
- Buscar culpables en vez de causas.

#### 3. Ejemplo

Lucía escribe con Claude la especificación de un módulo de pagos. Cierra una sesión de dos horas que cubrió las fases *explorar* y *crear* del PCRC.

**Pasos 1 y 2: alcance y datos.** Lucía escribe:
> "Hagamos la retrospectiva de esta sesión. Antes de opinar, lista los hechos: qué requisitos escribimos, cuántas bifurcaciones salieron y en qué estado quedaron."

Claude responde: 9 requisitos escritos, 3 reescritos dos veces. Salieron 4 bifurcaciones livianas: 1 convergida, 2 aparcadas y 1 abierta. La abierta, sobre reembolsos parciales, consumió 40 minutos.

**Paso 3: las tres columnas.** Claude pregunta y Lucía contesta:
- *Empezar*: "Definir el glosario de términos antes de escribir requisitos. Los 3 reescritos fallaron porque 'transacción' tenía dos sentidos."
- *Dejar*: "Dejar abierta una bifurcación más de 10 minutos. La de reembolsos nos sacó de la fase *crear*."
- *Seguir*: "Escribir un ejemplo por requisito. Así detectamos dos casos borde (situaciones extremas o poco comunes, como un pago de cero pesos)."

**Paso 4: acciones concretas.** Lucía escribe:
> "Convierte cada punto en una regla 'si… entonces'."

Claude propone:
1. Si un requisito usa un término nuevo, entonces lo agregamos al glosario antes de seguir.
2. Si una bifurcación liviana lleva 10 minutos abierta, entonces avisas y decido: aparcar, descartar o abrir un issue.
3. Si escribimos un requisito, entonces lo acompaña un ejemplo.

**Paso 5: guardar.** Lucía pide agregar las tres reglas al CLAUDE.md del proyecto. La bifurcación de reembolsos pasa a ser pesada: Claude propone el issue "Reembolsos parciales: definir reglas" y Lucía lo aprueba.

**Paso 6: el ciclo siguiente.** Al abrir la próxima sesión, en la fase *planificar*, Claude lee las reglas. A media mañana avisa: "La bifurcación sobre monedas lleva 10 minutos abierta. ¿Aparcar, descartar o abrir un issue?". Lucía la aparca. Al cerrar, en la nueva retrospectiva, comprueban las reglas: escribieron 11 requisitos, no reescribieron ninguno y las tres reglas se cumplieron.

#### Fuentes

- [Tannenbaum y Cerasoli (2013). Do team and individual debriefs enhance performance? A meta-analysis. Human Factors (PubMed)](https://pubmed.ncbi.nlm.nih.gov/23516804/)
- [Tannenbaum y Cerasoli (2013), texto completo (CEBMa)](https://cebma.org/assets/Uploads/Tannenbaum-Cerasoli.pdf)
- [Ellis y Davidi (2005). After-event reviews: drawing lessons from successful and failed experience. J Appl Psychol 90(5) (PubMed)](https://pubmed.ncbi.nlm.nih.gov/16162059/)
- [Lehtinen, Itkonen y Lassenius (2017). Recurring opinions or productive improvements: what agile teams actually discuss in retrospectives. Empirical Software Engineering 22(5)](https://link.springer.com/article/10.1007/s10664-016-9464-2)
- [Manifiesto Ágil (2001). Principios](https://agilemanifesto.org/principles.html)
- [Retrospective Wiki. The Prime Directive (Kerth)](https://retrospectivewiki.org/index.php?title=The_Prime_Directive)
- [Niechciał, Intercom. Continue, Stop, Start: Rethinking retrospectives (blog, solo como apoyo)](https://www.intercom.com/blog/continue-stop-start-retrospectives/)
- [Think Insights. Start Stop Continue (blog; origen en los años setenta sin fuente primaria)](https://thinkinsights.net/consulting/start-stop-continue)

### Diario de reflexión

**Nivel de evidencia:** moderada

#### 1. Origen, teoría y evidencia

**Quién la investigó.** La idea de aprender reflexionando sobre la experiencia viene de Dewey (1933, *How We Think*, 2.ª edición; la primera es de 1910). Schön (1983, *The Reflective Practitioner*) distinguió dos momentos: la *reflexión en la acción* (pensar mientras se trabaja) y la *reflexión sobre la acción* (pensar después, al cerrar). El diario de reflexión es la segunda: escribir unas líneas al terminar una sesión. Gibbs (1988, *Learning by Doing*, Further Education Unit, Oxford Polytechnic) le dio una estructura de seis pasos: descripción, sentimientos, evaluación, análisis, conclusión y plan de acción.

**Teoría.** Escribir obliga a articular y *codificar* la experiencia: convertir lo vivido en ideas explícitas. Según Di Stefano y colegas, eso mejora el rendimiento por dos vías: entender mejor la tarea (vía cognitiva) y confiar más en la propia capacidad, llamada *autoeficacia* (vía emocional).

**Evidencia.**
- Di Stefano, Gino, Pisano y Staats (2014, *Learning by Thinking*; versión de 2016 como *Making Experience Count*, HEC Paris) combinan un experimento de campo y dos de laboratorio. Concluyen que, después de acumular algo de experiencia, reflexionar por escrito sobre ella rinde más que seguir practicando. En el experimento de campo, con empleados en formación, quienes dedicaron los últimos 15 minutos de cada día a escribir lo aprendido sacaron cerca de un 23 % más en el examen final. Esa cifra viene de resúmenes divulgativos; no pude comprobarla en el texto completo.
- Berthold, Nückles y Renkl (2007) estudiaron *diarios de aprendizaje* (textos breves donde el estudiante resume y analiza lo aprendido) con preguntas guía. Las preguntas aumentaron el uso de estrategias de aprendizaje y mejoraron los resultados. Nückles, Hübner, Dümer y Renkl (2010) mostraron que ese apoyo pierde efecto o estorba cuando la persona gana experiencia. Esto se llama *efecto de reversión por experticia*. Por eso conviene retirar las preguntas poco a poco.
- No encontré un metaanálisis (estudio que combina los resultados de muchos estudios) específico sobre diarios de reflexión. Denton, Bond y Ellis (2017) sintetizaron 12 estudios sobre evaluación reflexiva, que incluye preguntas, escritura y discusión. Informan tamaños de efecto medios de 0,30 a 0,38. El *tamaño de efecto* mide cuánto cambia el resultado; estos valores indican un efecto pequeño a moderado.

**Nivel de evidencia: moderado.** Hay experimentos controlados con resultados consistentes, pero pocas síntesis, y el efecto depende de cómo se escribe y de cuánta experiencia tiene la persona.

#### 2. Proceso y buenas prácticas

**Pasos** (adaptados de Gibbs, 1988):
1. Al cerrar la sesión, reservar de 5 a 15 minutos. No dejarlo para "después".
2. **Describir**: qué se hizo y en qué fase del PCRC o del PCA se trabajó.
3. **Sentir**: una línea sobre cómo fue (dudas, frustración, confianza).
4. **Evaluar**: qué funcionó y qué no, comparado con lo que se fijó en la fase planificar del PCM.
5. **Analizar**: por qué pasó. Buscar la causa, no solo el síntoma.
6. **Concluir**: qué se aprendió que sirve para otra vez.
7. **Plan de acción**: una o dos acciones concretas para la próxima sesión, escritas como "si… entonces…".
8. Revisar las bifurcaciones de la sesión: cerrar las livianas (descartado, convergido) o pasar a pesadas las que merecen un issue en GitHub.

**Buenas prácticas:**
- Usar preguntas fijas al principio y retirarlas cuando el hábito ya existe.
- Escribir poco y siempre. La regularidad importa más que la extensión.
- Releer las entradas anteriores al planificar la siguiente sesión.
- Pedirle a Claude que haga las preguntas, pero escribir uno mismo las respuestas.

**Errores comunes:**
- Quedarse en la descripción ("hice X, luego Y") sin analizar.
- Reflexionar sin experiencia suficiente: con muy poco trabajo hecho, hay poco que aprender.
- Conclusiones vagas ("tengo que organizarme mejor") en vez de acciones concretas.
- Delegar la escritura en Claude: se pierde el efecto de codificar.

#### 3. Ejemplo

**Contexto.** Laura escribe con Claude la especificación de un módulo de pagos. La sesión de hoy recorrió las fases explorar, crear y decidir del PCRC. Al final, en la fase evaluar del PCM, abre su diario.

**Laura a Claude:** "Cerramos. Hazme las preguntas de Gibbs una por una y no respondas por mí."

**Lo que escribe Laura:**
- *Descripción*: "Exploramos tres formas de manejar reembolsos parciales. Decidimos usar un registro de movimientos en vez de editar el pago original."
- *Sentimientos*: "Me frustré a mitad de sesión. Sentí que dábamos vueltas."
- *Evaluación*: "El plan era cerrar reembolsos en una hora. Tardamos dos. La decisión final es buena."
- *Análisis*: "Perdí 40 minutos en una bifurcación liviana sobre monedas múltiples. La dejé abierta en vez de aparcarla. Claude siguió el hilo porque yo seguía preguntando."
- *Conclusión*: "Cuando una bifurcación no bloquea la decisión actual, la aparco enseguida."
- *Plan de acción*: "Si aparece un tema que no afecta la decisión de la fase actual, entonces le digo a Claude: 'apárcalo' y sigo."

**Revisión de bifurcaciones.** Laura le pide a Claude la lista de la sesión. Hay dos: "monedas múltiples" (abierta) y "nombre del campo `amount`" (abierta). Decide que "monedas múltiples" pasa a pesada: Claude propone un issue en GitHub y ella lo aprueba. La del nombre del campo queda convergida, porque ya se resolvió en la decisión.

**Resultado.** En la sesión siguiente, Laura relee la entrada al planificar. A los diez minutos surge una duda sobre impuestos. Ella dice: "Apárcalo, no bloquea esto". La fase decidir termina en el tiempo previsto. Tras tres semanas de diario, nota que ya aplica la regla sin pensarla. Entonces reduce las preguntas a tres: qué funcionó, por qué, qué cambio la próxima vez.

#### Fuentes

- [Di Stefano, Gino, Pisano y Staats (2014): Learning by Thinking: How Reflection Can Spur Progress Along the Learning Curve (SSRN)](https://papers.ssrn.com/abstract=2414478)
- [Di Stefano, Gino, Pisano y Staats (2016): Making Experience Count: The Role of Reflection in Individual Learning (HEC Research Paper 1181)](https://ebslgwp.hhs.se/heccah/abs/heccah1181.htm)
- [Berthold, Nückles y Renkl (2007): Do learning protocols support learning strategies and outcomes? The role of cognitive and metacognitive prompts (Learning and Instruction)](https://doi.org/10.1016/j.learninstruc.2007.09.007)
- [Nückles, Hübner, Dümer y Renkl (2010): Expertise reversal effects in writing-to-learn (Instructional Science)](https://doi.org/10.1007/s11251-009-9106-9)
- [Denton, Bond y Ellis (2017): Impact of Reflective Assessment on Student Learning: Best-Evidence Synthesis from Twelve Quantitative Studies](https://digitalcommons.spu.edu/globalcurriculumsymposium/gcs2017/gcs2017_events/6)
- [University of Edinburgh: Gibbs' Reflective Cycle](https://reflection.ed.ac.uk/reflectors-toolkit/reflecting-on-experience/gibbs-reflective-cycle)
