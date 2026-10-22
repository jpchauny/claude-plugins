# Técnicas para las fases del PCM

Este documento complementa [pensar-con-metodo.md](pensar-con-metodo.md). Allí definimos el **proceso cíclico metacognitivo (PCM)**: el proceso del nivel metacognitivo que dirige cualquier proceso del nivel cognitivo, con cuatro fases: planificar, monitorear, controlar y evaluar. Aquí reunimos técnicas concretas para trabajar cada una de esas fases.

Son 24 técnicas, seis por fase. No son todas: para cada fase existen muchas más. Elegimos las más conocidas y las más útiles para trabajar con Claude.

## Cómo se hizo

Cada técnica la investigó un agente con búsquedas web, priorizando artículos científicos, metaanálisis y libros de referencia. Después, otro agente verificó cada afirmación (autores, años, cifras, fuentes) y corrigió o suavizó lo que no se pudo comprobar. Las fichas de este documento resumen ese trabajo. El reporte completo, con los pasos detallados y ejemplos largos, está en [scratchpad-tecnicas-pcm.md](scratchpad-tecnicas-pcm.md).

Cada ficha tiene la misma estructura: qué es, origen y evidencia, cómo se aplica, claves, un ejemplo con Claude y las fuentes principales.

## Qué dice la evidencia

| Nivel de evidencia | Técnicas |
|---|---|
| **fuerte** | intenciones de implementación · reglas si-entonces · revisión después de la acción |
| **moderada** | WOOP · preguntas de planificación · criterio de terminado escrito · pensar en voz alta · preguntas de monitoreo · juicios de confianza · puntos de control · pausa de incubación · cambio de técnica · regla de corte · preguntas de evaluación · calibración · retrospectiva · diario de reflexión |
| **mixta** | exam wrapper |
| **débil** | premortem · timeboxing · aparcar · retroceder de fase |
| **sin evidencia formal** | mapa de hilos · semáforo |

*Fuerte* quiere decir que hay varios metaanálisis (estudios que combinan muchos estudios) con resultados consistentes. *Sin evidencia formal* no quiere decir que la técnica no sirva, sino que nadie la ha estudiado directamente: el mapa de hilos y el semáforo se apoyan en investigaciones vecinas. Casi ninguna técnica se ha estudiado en trabajo de software ni con asistentes de IA; los ejemplos de este documento son adaptaciones.

## Lo que se repite

Al comparar las 24 técnicas aparecen cuatro ideas que se repiten:

1. **Decidir antes, no en el momento.** Las intenciones de implementación, las reglas de corte y el criterio de terminado funcionan porque la decisión se toma con la cabeza fría, al planificar. Cuando llega la situación, no hay que decidir: hay que aplicar lo decidido.
2. **Hacer visible el pensamiento.** Pensar en voz alta, los juicios de confianza, el mapa de hilos y el semáforo sacan el pensamiento de la cabeza. Lo que no se ve no se puede monitorear.
3. **Comparar lo esperado con lo real.** La calibración, la revisión después de la acción y el exam wrapper evalúan a partir de la diferencia entre lo que se esperaba y lo que pasó.
4. **Preferimos seguir antes que cambiar.** El costo hundido, la fijación y la escalada de compromiso explican por qué cuesta retroceder, cambiar de técnica o abandonar. Por eso controlar necesita reglas fijadas de antemano.

## Un paquete mínimo

Si hubiera que elegir pocas técnicas, las de mejor evidencia caben en una sesión con Claude:

| Fase del PCM | Qué hacer |
|---|---|
| Planificar | escribir el objetivo, el criterio de terminado y dos o tres planes "si… entonces" |
| Monitorear | pedirle a Claude que avise cuando se cumpla un "si" |
| Controlar | aplicar el "entonces" ya decidido; aparcar las bifurcaciones |
| Evaluar | una revisión después de la acción: qué esperábamos, qué pasó, por qué hubo diferencia, qué haremos distinto |

## Las técnicas

| Planificar | Monitorear | Controlar | Evaluar |
|---|---|---|---|
| Intenciones de implementación | Pensar en voz alta | Reglas si-entonces ante cada señal | Revisión después de la acción |
| WOOP / contraste mental | Preguntas de monitoreo | Aparcar | Exam wrapper |
| Preguntas de planificación | Juicios de confianza | Pausa de incubación | Preguntas de evaluación |
| Criterio de terminado escrito | Puntos de control | Cambio de técnica | Calibración |
| Premortem | Mapa de hilos | Regla de corte | Retrospectiva |
| Timeboxing | Semáforo | Retroceder de fase | Diario de reflexión |

Los ejemplos siguen a una misma persona, Lucía, que trabaja con Claude en proyectos de software y especificaciones.

## Planificar

Antes de empezar: fijar objetivo, proceso, fase, técnica y criterio de terminado.

### Intenciones de implementación

**Qué es.** Un plan con la forma "si ocurre X, entonces hago Y", que une de antemano una situación crítica con una respuesta concreta. También se llaman planes si-entonces. Esta ficha trata de escribirlos al planificar; la ficha de reglas si-entonces trata de aplicarlos al controlar, cuando aparece la señal.

**Origen y evidencia.** El psicólogo Peter Gollwitzer propuso el concepto a comienzos de los años 90 y lo difundió en 1999. Separa la intención de meta (qué quiero lograr) de la intención de implementación (cuándo, dónde y cómo actúo). Cuando aparece la situación, la respuesta se dispara sin decidir en el momento. Un metaanálisis (estudio que combina muchos estudios) de 94 pruebas encontró un efecto medio de d = 0,65, de mediano a grande. Otro de 2025, con 642 pruebas, lo confirmó y mostró que el efecto crece si el plan es estricto, la persona está motivada y lo ensaya. Nivel de evidencia: **fuerte**, por cientos de pruebas y varios metaanálisis, aunque los tamaños pueden estar algo inflados por sesgo de publicación. No hay estudios en software ni con asistentes de IA.

**Cómo se aplica.**
1. Escribe la meta de la sesión en una frase y comprueba que importa.
2. Anticipa qué puede descarrilarla: una bifurcación, una prueba que falla.
3. Escribe dos o tres planes "si… entonces" con condición observable y acción precisa.
4. Léelos en voz alta una vez.
5. Pégalos al inicio de la sesión y pídele a Claude que avise cuando se cumpla un "si".

**Claves.**
- Usa condiciones observables ("si la prueba falla dos veces"), no vagas ("si me trabo").
- Evita respuestas que obligan a decidir otra vez ("entonces veo qué hago").
- El "si" alimenta monitorear y el "entonces" es controlar. Revisa los planes al evaluar.

**Ejemplo.** Lucía especifica con Claude un módulo de pagos y quiere cerrar la fase decidir del PCRC. Escribe: "Si aparece un tema que no es reintentos, entonces le pido a Claude que lo anote como bifurcación liviana en estado aparcado y sigo." Cuando propone cambiar el formato de los logs, Claude avisa y lo aparca. A los 45 minutos aprueba el requisito y convierte la bifurcación en un issue en GitHub.

**Fuentes.** [Gollwitzer (1999)](https://www.socmot.uni-konstanz.de/sites/default/files/99_Gollwitzer_Implementation_Intentions.pdf) · [Gollwitzer y Sheeran (2006)](https://www.socmot.uni-konstanz.de/publications/implementation-intentions-and-goal-achievement-meta-analysis-effects-and-processes) · [Sheeran, Listrom y Gollwitzer (2025)](https://kops.uni-konstanz.de/handle/123456789/69905)

### WOOP / contraste mental (MCII)

**Qué es.** Un ejercicio corto para empezar una sesión o una fase. Contrastas lo que quieres lograr con el obstáculo interno que lo frena, y cierras con un plan "si… entonces". WOOP son las iniciales en inglés de deseo, resultado, obstáculo y plan. A diferencia de las intenciones de implementación solas, primero contrastas deseo y obstáculo, y solo después escribes el plan.

**Origen y evidencia.** La psicóloga Gabriele Oettingen investigó el contraste mental. Luego lo combinó con las intenciones de implementación de Peter Gollwitzer, y a esa combinación la llamó MCII. Su teoría dice que fantasear solo con lo positivo reduce el esfuerzo. En cambio, contrastar deseo y obstáculo, en ese orden, ayuda a decidir si te comprometes con la meta o la sueltas. Un metaanálisis (estudio que combina muchos estudios) de Wang, Wang y Gai (2021) encontró un efecto pequeño a medio, g = 0,34. El efecto fue mayor con una persona guiando el ejercicio y bajó a 0,24 al corregir el sesgo de publicación. Nivel de evidencia: **moderada**. Los efectos son consistentes pero modestos, y hay pocos estudios en trabajo de software.

**Cómo se aplica.**
1. Deseo: escribe en una frase una meta concreta y alcanzable en el tiempo que tienes.
2. Resultado: imagina de verdad el mejor resultado durante unos segundos.
3. Obstáculo: busca el obstáculo interno principal, como un hábito, una distracción o una creencia tuya.
4. Plan: escribe "si [obstáculo], entonces [acción pequeña y concreta]".
5. Revisa el compromiso: si la meta no es realista, ajústala o suéltala.

**Claves.**
- Respeta el orden: primero el deseo, después el obstáculo.
- El obstáculo debe depender de ti. "El cliente cambia de idea" no sirve.
- Evita planes vagos como "si me distraigo, me concentro". Que Claude haga las preguntas es una adaptación razonable, pero no está probada.

**Ejemplo.** Lucía tiene dos horas para cerrar la sección de roles de una especificación. Le pide a Claude las preguntas de WOOP y reconoce que se engancha con temas laterales. Su plan dice: "Si aparece un tema que no es roles, entonces lo anoto como bifurcación liviana en estado aparcado y vuelvo a la tabla." Durante la fase explorar del PCRC, Claude le recuerda el plan dos veces. Lucía aparca una idea y abre otra como bifurcación pesada, un issue en GitHub. Termina la tabla a las 10:50. En la fase evaluar del PCM agrega un plan nuevo para las bifurcaciones que tocan otros módulos.

**Fuentes.** [Wang, Wang y Gai (2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8149892/) · [Oettingen (2012)](https://www.psy.uni-hamburg.de/arbeitsbereiche/paedagogische-psychologie-und-motivation/personen/oettingen-gabriele/dokumente/oettingen-2012.pdf) · [Gollwitzer y Sheeran (2006)](https://doi.org/10.1016/S0065-2601(06)38002-1)

### Preguntas de planificación

**Qué es.** Una lista corta de preguntas fijas que te haces antes de empezar una tarea: qué tipo de tarea es, cuál es el objetivo, qué necesitas, qué estrategia usarás y cuánto tiempo tienes. Son la primera parte de la lista de Schraw: las preguntas de monitoreo se hacen durante el trabajo y las de evaluación al cerrar.

**Origen y evidencia.** La propuso Gregory Schraw (1998) como parte de su lista de control de la regulación, que también trae preguntas para monitorear y evaluar. Su teoría: regular el pensamiento es una habilidad que se puede enseñar, y planificar es el primer paso. Un metaanálisis (estudio que combina muchos estudios) de de Boer y colegas (2018) revisó 48 intervenciones con estrategias metacognitivas y halló un efecto medio sobre el rendimiento: g = 0,50 al terminar y g = 0,63 en el seguimiento. Nivel de evidencia: **moderada**. El enfoque general tiene buena evidencia, pero ningún estudio aísla las preguntas de Schraw.

**Cómo se aplica.**
1. Antes de pedirle algo a Claude, nombra la tarea y en qué fase del PCRC estás (explorar, crear, decidir, implementar o verificar).
2. Escribe el objetivo en una frase comprobable: "Terminé cuando…".
3. Lista qué información necesitas y elige la estrategia, por ejemplo escribir primero los tests.
4. Fija tiempo y alcance, y escribe qué queda fuera.
5. Deja el plan por escrito en el chat o en el issue, para monitorear contra él.

**Claves.**
- Pídele a Claude que te haga las preguntas, pero respóndelas tú. Si Claude contesta, el plan deja de ser tuyo.
- Evita objetivos vagos como "mejorar el parser" y vuelve al plan durante la sesión.
- Ajusta el detalle al tamaño de la tarea. Un cambio de una línea no necesita las cinco preguntas.

**Ejemplo.** Lucía va a especificar la validación de fechas. Escribe: "Antes de empezar, hazme las preguntas de planificación. No propongas nada todavía." Fija el objetivo en tres opciones de formato con pros y contras, 45 minutos, y deja las zonas horarias fuera. Cuando Claude menciona que el backend guarda en UTC, Lucía lo anota como bifurcación liviana aparcada. Al minuto 40 cumple el objetivo y pasa esa bifurcación a pesada, como issue en GitHub.

**Fuentes.** [Schraw (1998)](https://doi.org/10.1023/A:1003044231033) · [de Boer et al. (2018)](https://doi.org/10.1016/j.edurev.2018.03.002) · [Lista de Schraw (OpenLearn)](https://www.open.edu/openlearncreate/mod/page/view.php?id=236090)

### Criterio de terminado escrito

**Qué es.** Antes de empezar, escribes en pocas líneas cómo se verá el trabajo cuando esté terminado. Es una lista de condiciones que se comprueban con un sí o un no.

**Origen y evidencia.** Tiene dos raíces. La primera es la teoría del establecimiento de metas de Locke y Latham: una meta específica y exigente rinde más que un "haz lo mejor que puedas". Su revisión de 2002 resume metaanálisis (estudios que combinan muchos estudios) en los que las metas específicas y difíciles mejoran el rendimiento con efectos de d = 0,42 a 0,80, de medianos a grandes. En cambio de conducta el efecto es menor (d = 0,34, Epton y colegas, 2017). La segunda raíz es la Definition of Done de Scrum. Su evidencia en software es débil: solo hay una encuesta a 137 profesionales, sin experimentos. Nivel de evidencia: **moderada**. La teoría es sólida, pero nadie estudió su uso con Claude.

**Cómo se aplica.**
1. En la fase planificar del PCM, escribe el objetivo en una frase.
2. Conviértelo en 3 a 6 condiciones verificables y agrega una línea "fuera de alcance".
3. Pide a Claude que señale condiciones ambiguas o imposibles.
4. Al monitorear, compara el avance con el criterio. Si aparece una bifurcación fuera del criterio, apárcala o descártala.
5. En la fase evaluar, revisa condición por condición. Solo terminas cuando todas dicen sí.

**Claves.**
- Usa verbos observables ("compila", "contiene", "rechaza"), no "mejorar". Un criterio vago equivale a "haz lo mejor que puedas".
- No dejes que el criterio crezca con cada idea nueva: regístrala como bifurcación. Si lo cambias, hazlo de forma explícita y anota el motivo.
- No des por terminado porque Claude dice "listo".

**Ejemplo.** Lucía especifica el endpoint `POST /facturas`. Escribe cuatro condiciones, entre ellas "hay al menos tres ejemplos de petición y respuesta". Claude detecta que la condición de errores es ambigua y ella la corrige. Durante el PCRC surge el multimoneda. No está en el criterio, así que lo deja como bifurcación liviana aparcada y luego abre un issue. Al final pide: "Revisa el criterio punto por punto y responde sí o no con evidencia". Falta un ejemplo, lo agrega y cierra con un terminado justificable.

**Fuentes.** [Locke y Latham (2002)](https://goal-lab.psych.umn.edu/orgpsych/2020/readings/5.%20Motivation/Locke%20&%20Latham%20(2002).pdf) · [Epton, Currie y Armitage (2017)](https://pubmed.ncbi.nlm.nih.gov/29189034/) · [Kopczyńska y colegas (2022)](https://arxiv.org/abs/2208.04003)

### Premortem

**Qué es.** Un ejercicio para planificar: se supone que el proyecto ya fracasó y se explica por qué. Así aparecen riesgos cuando el plan todavía se puede cambiar.

**Origen y evidencia.** La publicó Gary Klein, psicólogo que estudia cómo deciden los expertos, en Harvard Business Review (2007). Se apoya en la retrospectiva prospectiva: explicar un hecho futuro como si ya hubiera ocurrido, con certeza. Mitchell, Russo y Pennington (1989) vieron que la certeza alarga las explicaciones. Klein habla de cerca de un 30 % más de razones, pero eso mide cantidad, no calidad. Estudios pequeños, algunos conocidos solo por resúmenes, muestran más riesgos detectados y menos confianza excesiva en el plan. Nivel de evidencia: **débil**. Son pocos estudios, varios sin revisión de revista, sin metaanálisis ni tamaños de efecto.

**Cómo se aplica.**
1. Parte de un plan concreto y fija el fracaso como hecho seguro, en pasado.
2. Escribe tus causas en silencio antes de leer las de Claude.
3. Junta las listas y elige las dos o tres causas más probables o graves.
4. Para cada una, define una acción o una señal de alarma: "si pasa X, entonces hago Y".
5. Guarda el resultado junto al plan para monitorear y evaluar.

**Claves.**
- "Fracasó: ¿por qué?" genera más razones que "¿qué podría salir mal?".
- Busca causas internas, no solo mala suerte.
- Error: quedarse en la lista sin cambiar el plan.

**Ejemplo.** Lucía elige un modelo por roles para un módulo de permisos, en la fase decidir del PCRC. Antes de implementar escribe: "Supongamos que estamos en febrero. La especificación de permisos fracasó." Anota sus causas y después lee las de Claude. Agrega ejemplos a cada regla, aparca como bifurcación liviana quién cambia los roles y abre un issue sobre las bajas. Días después se cumple su señal de alarma: un caso no cabe en los roles. Vuelve a decidir y agrega un rol por sucursal, antes de escribir código.

**Fuentes.** [Klein (2007), HBR](https://hbr.org/2007/09/performing-a-project-premortem) · [Mitchell, Russo y Pennington (1989)](https://onlinelibrary.wiley.com/doi/10.1002/bdm.3960020103) · [Peabody (2017)](https://digitalcommons.mtu.edu/etdr/374)

### Timeboxing

**Qué es.** Un *timebox* (caja de tiempo) es un plazo fijo que asignas a una tarea antes de empezarla. Cuando el plazo se acaba, te detienes y decides: entregar lo que hay, recortar el alcance (lo que la tarea debe incluir) o abrir otra caja. El tiempo es fijo y el alcance cambia. A diferencia de la regla de corte, el límite es solo de tiempo y se aplica vaya bien o mal la tarea.

**Origen y evidencia.** Nació en el desarrollo de software. La Agile Alliance la ubica en 1988, en un método de Scott Schultz, y después la adoptaron DSDM y Scrum. Se apoya en la falacia de planificación (Kahneman y Tversky, 1979): subestimamos cuánto tardará nuestro propio trabajo. Buehler, Griffin y Ross (1994) la midieron: unos estudiantes estimaron 33,9 días para su tesis y tardaron 55,5. No hay estudios revisados por pares sobre el timeboxing en sí. Un metaanálisis (estudio que combina muchos estudios) sobre gestión del tiempo en general (Aeon, Faber y Panaccio, 2021) encontró una relación moderada con el desempeño. Pero son correlaciones y no aíslan la técnica. Nivel de evidencia: **débil**. El mecanismo de fondo está probado; la técnica es sobre todo práctica profesional.

**Cómo se aplica.**
1. Define el resultado en una frase y como entregable: "tabla con 3 opciones", no "trabajar en opciones".
2. Asigna una duración corta (de 25 a 90 minutos) con un punto de control a mitad. Pon un temporizador: Claude no mide el tiempo, el aviso lo das tú.
3. Trabaja solo en ese resultado. Lo que aparezca fuera es una bifurcación liviana: anótala y déjala en estado aparcado.
4. Cuando suene el final, detente y decide: entregar, recortar o abrir una caja nueva con objetivo propio.
5. Compara lo estimado con lo real para estimar mejor la próxima vez.

**Claves.**
- No extiendas la caja "solo diez minutos más": eso anula la técnica.
- El éxito no es terminar todo. El éxito es decidir con información al cierre.
- Úsala en tareas sin fin natural, como la fase explorar del PCRC.

**Ejemplo.** Lucía especifica un módulo de permisos con Claude. Pone 45 minutos, con aviso a los 20, y escribe: "Resultado: una tabla con 3 opciones y sus pros y contras. Cuando diga 'fin', paramos aunque falte algo." En el control falta la tercera opción. Claude menciona que los roles están en dos tablas distintas y Lucía aparca ese tema. Al final, una opción solo tiene pros, así que abre una caja de 15 minutos para sus contras. Al evaluar, convierte lo aparcado en un issue en GitHub. Había estimado 45 minutos y necesitó 60, así que planifica la próxima exploración con más margen.

**Fuentes.** [Agile Alliance: Timebox](https://agilealliance.org/glossary/timebox) · [Buehler, Griffin y Ross (1994)](https://bear.warrington.ufl.edu/brenner/mar7588/Papers/buehler-et-al-1994.pdf) · [Aeon, Faber y Panaccio (2021)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0245066)

## Monitorear

Durante el trabajo: observar cómo va y en qué fase se está. Es la información que sube del nivel cognitivo al metacognitivo.

### Pensar en voz alta

**Qué es.** Narrar lo que piensas y esperas mientras trabajas, sin explicarlo ni justificarlo. Sirve para ver el propio pensamiento en el nivel metacognitivo y detectar cuándo algo no encaja.

**Origen y evidencia.** Ericsson y Simon (1980) la investigaron con el análisis de protocolos: grabar a alguien que piensa en voz alta y estudiar lo que dijo. Su teoría dice que narrar lo que está en la memoria de trabajo no cambia el pensamiento; explicar sí lo cambia. Un metaanálisis (estudio que combina muchos estudios) de Fox, Ericsson y Best (2011), con 94 estudios, halló que narrar no cambia el rendimiento (r = −0,03), aunque alarga la tarea. Pedir autoexplicaciones (explicarse por qué algo es así) tiene un efecto medio (g = 0,55, Bisra et al., 2018). La evidencia es fuerte en esos dos puntos, pero nadie midió esta técnica como herramienta de monitoreo con un asistente de IA. Nivel de evidencia: **moderada**.

**Cómo se aplica.**
1. Úsala en tramos donde es fácil perderse: depurar, decidir entre opciones, revisar una especificación.
2. Narra en presente lo que haces y esperas: "Ahora miro X porque espero Y".
3. Marca las señales: "esto no lo esperaba", "no sé por qué funciona", "me estoy desviando".
4. Ante una señal, pasa a autoexplicarte y luego decide en la fase controlar: seguir, cambiar de enfoque o registrar una bifurcación.
5. Cierra con una frase que resuma dónde estás y qué sigue; sirve para evaluar.

**Claves.**
- Tu narración en el chat es el registro. Pide a Claude que te avise de contradicciones o dudas sin resolver.
- Úsala en tramos cortos: narrar todo el día cansa y alarga la tarea.
- Error: narrar sin actuar, o narrar para quedar bien. Una señal sin decisión no sirve.

**Ejemplo.** Lucía revisa con Claude la especificación de un módulo de permisos, en la fase verificar del PCRC. Narra: "Espero que pierda los permisos del equipo viejo... No, la especificación no dice nada de eso. Esto no lo esperaba." Al autoexplicarse ve que la regla R7 no dice cuándo se evalúa la pertenencia al equipo. Aparca una idea lateral como bifurcación liviana, pide a Claude dos redacciones y elige una. Encontró un hueco que una lectura en silencio podía pasar por alto.

**Fuentes.** [Ericsson y Simon (1980)](https://doi.org/10.1037/0033-295X.87.3.215) · [Fox, Ericsson y Best (2011)](https://supp.apa.org/psycarticles/supplemental/a0021663/a0021663_supp.html) · [Bisra et al. (2018)](https://doi.org/10.1007/s10648-018-9434-x)

### Preguntas de monitoreo

**Qué es.** Una lista corta de preguntas fijas que te haces en puntos de control mientras trabajas. Cada pregunta funciona como una alarma: corta el trabajo en el nivel cognitivo (pensar sobre el problema) y obliga a subir al nivel metacognitivo (pensar sobre el propio pensamiento y dirigirlo). Se diferencian de las preguntas de planificación (antes de empezar) y de las de evaluación (al cerrar) en el momento: se hacen durante el trabajo.

**Origen y evidencia.** Flavell (1979) habló de "monitoreo cognitivo". Schraw y Moshman (1995) dividieron la regulación en planificar, monitorear y evaluar, y Schraw (1998) propuso preguntas fijas para cada actividad. Las de monitoreo son estas: ¿entiendo lo que hago?, ¿la tarea tiene sentido?, ¿me acerco a mis objetivos?, ¿necesito cambiar algo? En el método IMPROVE, Kramarski y Mevarech (2003) trabajaron con 384 estudiantes de octavo grado. Los grupos con entrenamiento en autopreguntas superaron a los grupos sin él, también en una tarea de transferencia (aplicar lo aprendido a algo nuevo). Nivel de evidencia: **moderada**. Los programas casi siempre combinan las preguntas con otras técnicas, y no hay un tamaño de efecto para las preguntas solas. Tampoco hay estudios con adultos que trabajen con un asistente de IA, así que aplicarlo a ese contexto es una extrapolación.

**Cómo se aplica.**
1. Elige 3 o 4 preguntas fijas, a partir de Schraw o de IMPROVE.
2. Define los puntos de control: el cierre de cada fase del PCRC, cada 30 minutos o cada respuesta larga de Claude.
3. Responde por escrito, en una línea.
4. Compara la respuesta con el objetivo que fijaste al planificar.
5. Si la respuesta es "no" o "no sé", pasa a controlar: cambia de estrategia, vuelve a una fase anterior o aparca una bifurcación.

**Claves.**
- Prefiere preguntas que pidan evidencia ("¿qué prueba tengo de que esto funciona?") a las de sí o no.
- Pide a Claude que haga las preguntas, así no dependen de tu memoria. Incluye siempre una sobre el rumbo.
- Preguntar y no actuar no cambia nada. Demasiadas preguntas hacen que dejes de usarlas.

**Ejemplo.** Lucía especifica los permisos de un módulo de facturas. Le pide a Claude: "Al cerrar cada fase del PCRC y después de cada respuesta larga tuya, hazme estas tres preguntas". En medio de crear, responde: "1) No. Me fui al diseño de la base de datos y eso no es especificar". Abre una bifurcación liviana, la aparca y luego la pasa a issue en GitHub. Así detecta el desvío en minutos, no al final.

**Fuentes.** [Schraw (1998)](https://learntechlib.org/p/165105) · [Kramarski y Mevarech (2003)](https://education.biu.ac.il/en/node/260) · [Lista de Schraw (OpenLearn)](https://www.open.edu/openlearncreate/mod/page/view.php?id=236090)

### Juicios de confianza

**Qué es.** Un juicio de confianza es tu propia estimación de cuánto sabes o de qué tan bien hiciste algo, en número. Por ejemplo: "estoy 70 % seguro de que esto es correcto". Cada juicio se hace en el momento, al monitorear; la calibración, en la fase evaluar, compara muchos juicios con los resultados.

**Origen y evidencia.** Hart (1965) estudió el sentimiento de saber: las personas predijeron qué respuestas reconocerían y acertaron más que el azar. En el modelo de Nelson y Narens (1990), monitorear es la información que sube del nivel cognitivo al metacognitivo, y los juicios de confianza le dan datos a controlar. Koriat (1997) mostró que inferimos los juicios a partir de pistas, como la fluidez, y por eso fallan. En tareas medias o difíciles solemos tener sobreconfianza. Un metaanálisis (estudio que combina muchos estudios) de Rhodes y Tauber (2011) halló que los juicios con demora distinguen mucho mejor lo que se recordará (g = 0,93; g es el tamaño de efecto, y 0,8 ya es grande). Nivel de evidencia: **moderada**. Es fuerte en que los juicios fallan de forma sistemática y en que la demora los mejora, pero moderada en que eso mejore el resultado. Casi todo viene de laboratorio, sin estudios en software ni con IA.

**Cómo se aplica.**
1. Elige una pieza concreta: un requisito, una función, un concepto.
2. Antes de verificar, escribe tu confianza de 0 a 100 % y una razón breve. Si puedes, deja pasar un rato antes.
3. Verifica contra algo externo: pruebas, una revisión de Claude o una pregunta que respondes sin mirar.
4. Compara confianza y resultado, y anota la diferencia.
5. Pasa a controlar: lo de baja confianza o mal calibrado recibe más atención.

**Claves.**
- Juzga si puedes recuperar o explicar, no si el texto te resulta familiar. "Claude lo explicó claro" no es "yo lo entiendo".
- Juzgar justo después de leer infla la confianza. Cinco juicios dan una pista, no una medida: lleva un registro.
- Monitorear sin controlar no cambia el resultado.

**Ejemplo.** Lucía está en la fase implementar del PCRC con cinco requisitos de un módulo de pagos. Tras un café escribe: "R3 60 % (no sé si cubre reembolsos parciales), R5 40 %. Claude, hazme una pregunta sobre R3 y otra sobre R5 que yo deba responder sin mirar el código". No sabe responder sobre R3 y lo baja a 40 %. En verificar, R3 y R4 fallan; R4 lo tenía en 80 %. Anota la sobreconfianza y agrega una regla: "Si un requisito toca montos, entonces escribo un caso con cero antes de juzgar". La duda sobre monedas sin decimales la vuelve una bifurcación pesada, con un issue en GitHub.

**Fuentes.** [Metamemory (Wikipedia)](https://en.wikipedia.org/wiki/Metamemory) · [Koriat (1997)](https://newiipdm.haifa.ac.il/wp-content/uploads/2015/05/1997-Koriat-CueUtilization-JEPG.pdf) · [Tekin y Roediger (2021), sobre juicios con demora](https://pmc.ncbi.nlm.nih.gov/articles/PMC7912969)

### Puntos de control

**Qué es.** Un punto de control es una pausa fijada de antemano para revisar cómo va el trabajo. Puede ser por tiempo, por hito (al terminar una parte) o por evento (al cambiar de fase del PCRC). El punto de control fija cuándo revisar; las preguntas de monitoreo fijan qué preguntar en ese momento.

**Origen y evidencia.** Nelson y Narens (1990) describieron dos niveles: el nivel metacognitivo observa y corrige al nivel cognitivo. El punto de control es el momento en que ese nivel mira hacia abajo. Un metaanálisis (estudio que combina muchos estudios) de Harkin y colegas (2016), con 138 estudios, encontró que monitorear el progreso mejora el logro de metas (d = 0,40, efecto entre pequeño y moderado), más aún si se registra por escrito. Dignath y colegas (2023) hallaron un efecto moderado (d = 0,42) con herramientas de monitoreo. La técnica Pomodoro de Cirillo es una práctica, no una teoría probada. Nivel de evidencia: **moderada**. Monitorear y registrar tiene buen respaldo; el intervalo de 25 minutos y la revisión por hitos no tienen evidencia propia.

**Cómo se aplica.**
1. Al planificar, elige el tipo de punto: por tiempo, por hito o por cambio de fase del PCRC.
2. Escribe dos o tres preguntas fijas: ¿sigo en el objetivo?, ¿qué bifurcaciones están abiertas?, ¿qué confianza tengo en lo hecho?
3. Pide a Claude que avise al llegar al punto, o usa un temporizador.
4. Responde por escrito en una o dos líneas y decide: seguir, corregir el rumbo (eso ya es controlar) o aparcar una bifurcación.
5. Guarda las respuestas en la sesión o en el issue.

**Claves.**
- Registra por escrito y revisa el contenido y también el proceso.
- No te saltes el punto "porque va bien": ahí aparece la deriva.
- Evita preguntas vagas y puntos tan seguidos que cortan el trabajo profundo.

**Ejemplo.** Lucía escribe con Claude la especificación de un módulo de permisos y pide: "Pon un punto de control al terminar cada sección y otro antes de pasar a decidir". En el primer punto responde "Confianza 3. No sé si el rol 'auditor' puede ver borradores" y lo aclara antes de seguir. En el segundo, la bifurcación aparcada sobre herencia entre equipos ya afecta tres secciones: pasa de liviana a pesada como issue en GitHub. La especificación llega a decidir sin dudas abiertas.

**Fuentes.** [Harkin et al. (2016)](https://eprints.whiterose.ac.uk/id/eprint/91437/) · [Dignath et al. (2023)](https://link.springer.com/article/10.1007/s10648-023-09718-4) · [Biwer et al. (2023)](https://pubmed.ncbi.nlm.nih.gov/36859717/)

### Mapa de hilos

**Qué es.** Una lista visible de los hilos abiertos en la sesión. Un hilo es una línea de trabajo en curso: la tarea principal o una bifurcación. Sirve para monitorear dónde estás y qué quedó pendiente. El mapa es el registro que se monitorea; aparcar es la decisión de control que agrega hilos aparcados a ese registro.

**Origen y evidencia.** Nadie la inventó con ese nombre: une varias líneas de investigación. Cowan (2001) concluyó que la memoria de trabajo sostiene unos 4 elementos con sentido. Altmann y Trafton (2002) proponen que un objetivo pendiente pierde activación y necesita una señal externa para retomarse. Masicampo y Baumeister (2011) mostraron que escribir un plan para una meta sin terminar elimina los pensamientos intrusivos que genera. No hay réplicas independientes de ese estudio. En programadores, DeLine y Parnin (2010) vieron que unas señales automáticas duplicaron la tasa de éxito al retomar una tarea frente a tomar notas sin ayuda. Nivel de evidencia: **práctica sin evidencia formal**. Los mecanismos tienen evidencia fuerte o moderada, pero el formato del mapa no se probó en estudios controlados.

**Cómo se aplica.**
1. Al empezar, abre el mapa con el hilo principal y su fase del PCRC.
2. Registra cada bifurcación liviana en cuanto aparece, con nombre corto y estado: abierto, aparcado, descartado o convergido.
3. Escribe la señal de regreso de cada hilo aparcado: dónde quedó y qué harías primero al retomarlo.
4. Revisa el mapa en cada cambio de fase. Si hay más de tres o cuatro hilos abiertos, aparca o descarta. Ese límite es una regla práctica, no un número probado.
5. Al cerrar, cada hilo queda convergido, descartado o convertido en bifurcación pesada (issue en GitHub).

**Claves.**
- Una línea por hilo y un solo hilo activo. Si necesita un párrafo, quizá merece un issue.
- Señal de regreso concreta: "falta validar el campo fecha", no "seguir con validación".
- No es un backlog. Si no lo revisas en cada cambio de fase, no sirve.

**Ejemplo.** Lucía escribe con Claude la especificación de un módulo de reservas, en la fase crear. Claude detecta que las zonas horarias afectan los plazos de cancelación. Ella pide: "Anótala como aparcada. Señal de regreso: decidir si los plazos se cuentan en la hora del hotel o del cliente." Descarta la cancelación parcial para esta versión. Antes de pasar a decidir, retoma las zonas horarias y las resuelve. Al cerrar, convierte la cancelación parcial en issue. Termina sin hilos perdidos y sabe por dónde seguir.

**Fuentes.** [Cowan (2001)](https://doi.org/10.1017/S0140525X01003922) · [Masicampo y Baumeister (2011)](https://doi.org/10.1037/a0024192) · [DeLine y Parnin (2010)](https://www.microsoft.com/en-us/research/publication/evaluating-cues-for-resuming-interrupted-programming-tasks/)

### Semáforo

**Qué es.** Una autoevaluación rápida: a cada parte del trabajo le asignas un color. Verde significa "lo entiendo", amarillo "dudo" y rojo "no lo entiendo". Así el monitoreo se vuelve visible y el control va adonde hace falta. A diferencia de los juicios de confianza, no usa porcentajes: usa tres colores para todo el trabajo a la vez.

**Origen y evidencia.** Viene de la evaluación formativa, que evalúa durante el trabajo para corregir el rumbo. Black y Wiliam (1998) revisaron unos 250 estudios sobre el tema. Después, los docentes del proyecto KMOFAP crearon el semáforo, y Black y sus colegas lo describieron en 2002. Kingston y Nash (2011) hicieron un metaanálisis (estudio que combina muchos estudios) de la evaluación formativa y estimaron un efecto cercano a 0,20, pero Briggs y sus colegas (2012) concluyeron que el efecto real sigue siendo incierto. Panadero y sus colegas (2017) encontraron efectos de la autoevaluación sobre la autorregulación de 0,23 a 0,65. No hay estudios controlados del semáforo por sí solo. Nivel de evidencia: **práctica sin evidencia formal**, con apoyo indirecto moderado.

**Cómo se aplica.**
1. Antes de empezar, define qué significa "entendido" o "terminado" para cada parte.
2. En puntos fijos, por ejemplo al cerrar una fase, asigna un color a cada parte.
3. Da una razón por cada color y una prueba por cada verde.
4. Actúa según el color: atiendes el rojo ya, revisas o aparcas el amarillo, y el verde sigue.
5. Al final, compara los colores con el resultado real para calibrar.

**Claves.**
- Endurece el verde: "podría enseñarlo" o "tengo una prueba que lo demuestra".
- Pide a Claude un color independiente y compara los dos.
- No dejes que un rojo crezca dentro de la sesión: apárcalo o pásalo a un issue.

**Ejemplo.** Lucía está en la fase decidir del PCRC con una especificación de permisos. Escribe: "Semáforo antes de implementar. Dame tus colores con una razón y una prueba para cada verde". Claude marca la herencia en rojo, no en amarillo, porque dos reglas se contradicen. Lucía resuelve ese conflicto y abre un issue para los recursos borrados. Entra en implementar sin ningún rojo abierto.

**Fuentes.** [OECD (2005), Formative Assessment](https://t4.oecd.org/education/ceri/35661078.pdf) · [Working Inside the Black Box (2002)](https://discovery.ucl.ac.uk/id/eprint/1507188/) · [Panadero, Jonsson y Botella (2017)](https://portalinvestigacion.deusto.es/documentos/6326545dd50fae52cd317f7b)

## Controlar

Durante el trabajo: ajustar según lo observado. Son los ajustes que bajan del nivel metacognitivo al cognitivo.

### Reglas si-entonces ante cada señal

**Qué es.** Reglas escritas antes de trabajar con el formato "si pasa X, entonces hago Y". Cuando aparece la señal X, aplicas la respuesta Y sin volver a deliberar. Las reglas se escriben con la técnica de intenciones de implementación, al planificar; esta ficha trata de usarlas al controlar, ante cada señal.

**Origen y evidencia.** La base son las intenciones de implementación, que propuso el psicólogo Peter Gollwitzer, y la evidencia es la misma. La teoría: entre querer algo y hacerlo hay una brecha, y el plan la reduce porque la señal se nota antes y la respuesta sale casi sin esfuerzo. En el PCM, monitorear detecta la señal y controlar ejecuta la respuesta. Un metaanálisis (estudio que combina muchos estudios) de Gollwitzer y Sheeran (2006) con 94 pruebas halló un efecto medio a grande (d = 0,65). Otro de 2025, con 642 pruebas, encontró efectos mayores con el formato literal "si… entonces" y cuando la persona ensaya el plan. Nivel de evidencia: **fuerte**, aunque el efecto real puede ser algo menor por sesgo de publicación. Su uso al trabajar con una IA no tiene estudios directos: es una extrapolación razonable.

**Cómo se aplica.**
1. Parte de la meta de la sesión, que viene de planificar.
2. Lista las señales críticas: una bifurcación, Claude se sale del alcance, un error se repite.
3. Escribe una regla por señal: "Si [señal observable], entonces [acción concreta]".
4. Léelas una vez al empezar y déjalas en el prompt inicial para que Claude avise.
5. En la fase evaluar, revisa qué regla se disparó, cuál faltó y cuál sobra.

**Claves.**
- La señal debe poder observarse: "si me pierdo" no sirve; "si llevo 20 minutos en el mismo error" sí.
- Pocas reglas, de tres a cinco, con acciones pequeñas e inmediatas.
- Error común: escribir la regla y no ensayarla.

**Ejemplo.** Lucía escribe con Claude la especificación de un módulo de pagos. Al empezar fija reglas, entre ellas: "Si aparece una bifurcación, entonces la anotamos como liviana aparcada y seguimos con reembolsos". Claude avisa: "Señal de la regla 1: surgió la pregunta de cómo tratar monedas distintas. ¿La aparco?". Ella responde "Sí, aparcada" sin deliberar. Otro cambio que afectaba a otro módulo terminó como issue en GitHub, una bifurcación pesada. La sesión cerró la sección de reembolsos sin desvíos.

**Fuentes.** [Gollwitzer y Sheeran (2006)](https://stafforini.com/works/gollwitzer-2006-implementation-intentions-and/) · [Sheeran, Listrom y Gollwitzer (2025)](https://kops.uni-konstanz.de/handle/123456789/69905) · [Achtziger, Gollwitzer y Sheeran (2008)](https://journals.sagepub.com/doi/10.1177/0146167207311201)

### Aparcar

**Qué es.** Aparcar es anotar una bifurcación que aparece en medio de una fase, con un plan de regreso, para volver de inmediato a lo que estabas haciendo. Aparcar es la decisión; el mapa de hilos es la lista donde queda anotada.

**Origen y evidencia.** No tiene autor. Nació en la facilitación de reuniones, como un papel en la pared para los temas fuera de agenda. Allen (2001), en *Getting Things Done*, llevó una idea parecida al trabajo personal, sin estudios. Masicampo y Baumeister (2011) aportan la teoría: lo que ocupa la mente no es la tarea sin terminar, sino la tarea sin plan. En sus experimentos, una meta pendiente causó pensamientos intrusivos y peor rendimiento, y escribir un plan concreto eliminó esos efectos. Un metaanálisis (estudio que combina muchos estudios) de 2025 no encontró la ventaja de memoria del famoso efecto Zeigarnik. Nivel de evidencia: **débil**, porque hay pocos estudios, con muestras pequeñas y sin réplicas directas.

**Cómo se aplica.**
1. Detecta la bifurcación y decide si es liviana (vive en la sesión) o pesada (issue en GitHub).
2. Anótala en una frase: qué es y por qué importa. Su estado pasa a aparcado.
3. Fija el regreso: cuándo o con qué condición la retomas.
4. Vuelve de inmediato a la fase en curso.
5. En el punto fijado, revisa la lista y cambia cada estado a abierto, descartado o convergido.

**Claves.**
- Una lista sin un "cuándo" es un cajón, no un aparcamiento.
- No aparques lo que bloquea la fase actual: eso se trata ahora.
- Al cerrar la sesión no quedan bifurcaciones livianas aparcadas.

**Ejemplo.** Lucía especifica con Claude un módulo de pagos y está en la fase decidir del PCRC. Se le ocurre otro tema y, en el nivel metacognitivo, controla: "Esto es una bifurcación. Apárcala como liviana: 'cambio de moneda durante un cobro'. La retomamos al terminar decidir". Al cerrar la fase revisan la lista. El tema sí afectaba los reintentos, así que pasa a convergido: cada reintento usa la moneda del primer intento.

**Fuentes.** [Masicampo y Baumeister (2011)](https://doi.org/10.1037/a0024192) · [Ghibellini y Meier (2025), metaanálisis](https://www.nature.com/articles/s41599-025-05000-w) · [Scullin et al. (2018)](https://pubmed.ncbi.nlm.nih.gov/29058942/)

### Pausa de incubación

**Qué es.** Dejar a propósito de trabajar en un problema cuando estás atascado y volver a él más tarde, a veces con una idea nueva. En el PCM es una decisión de la fase controlar. A diferencia del cambio de técnica, no pruebas otro método: dejas el problema un rato y vuelves.

**Origen y evidencia.** Wallas (1926) describió cuatro etapas del pensamiento creativo: preparación, incubación, iluminación y verificación. La explicación con más apoyo es que la pausa libera la fijación, es decir, debilita una idea equivocada que bloquea a las demás (Smith y Blankenship, 1989). El metaanálisis (estudio que combina muchos estudios) de Sio y Ormerod (2009) reunió 117 estudios y halló un efecto positivo de pequeño a moderado. La pausa ayudó más al generar muchas ideas, tras una preparación larga y con una tarea liviana durante la pausa. Estudios posteriores no confirmaron que la divagación mental sea la causa. Nivel de evidencia: **moderada**, porque el efecto existe pero es modesto, depende del problema y su mecanismo sigue en discusión.

**Cómo se aplica.**
1. Prepara a fondo: trabaja el problema en serio antes de pausar.
2. Monitorea el atasco: das vueltas a la misma idea o Claude repite propuestas parecidas.
3. Decide la pausa y escribe una nota de retorno: dónde quedaste y qué te bloquea. Aparca los temas nuevos como bifurcación liviana.
4. Haz algo liviano: caminar, ordenar, responder correos simples.
5. Vuelve, relee la nota, anota la primera idea y verifícala.

**Claves.**
- Úsala en problemas abiertos como diseño o nombres. Ante un error concreto de código, depurar con método rinde más.
- No llenes la pausa con otra tarea difícil y no vuelvas a repetir lo mismo.
- Acuerda con Claude un plan si-entonces: "si repetimos la misma propuesta dos veces, sugiéreme una pausa".

**Ejemplo.** Lucía lleva 40 minutos en la fase crear del PCRC, modelando permisos de una API. Claude propone por tercera vez roles con herencia. Ella escribe: "Paro aquí. Estamos fijados en roles con herencia. Nota de retorno: el bloqueo es el invitado externo". Camina y vuelve con una idea: permisos colgados de una invitación con alcance y vencimiento. En la fase decidir elige esa opción, que resuelve el bloqueo.

**Fuentes.** [Sio y Ormerod (2009)](https://pubmed.ncbi.nlm.nih.gov/19210055/) · [Gilhooly (2016)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4956660) · [Du, Gordon y Tolmie (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12190454/)

### Cambio de técnica

**Qué es.** Dejar a propósito un método que ya no da resultado y probar otro distinto. En el PCM, monitorear detecta el atasco y controlar decide el cambio. A diferencia de la pausa de incubación, no dejas el problema: sigues trabajando con otro método.

**Origen y evidencia.** Jansson y Smith (1991) llamaron fijación a la adhesión ciega a ideas que limita el diseño: estudiantes y diseñadores copiaron rasgos defectuosos de ejemplos aunque se les pidió evitarlos. Antes, Luchins (1942) describió el efecto Einstellung: un método aprendido impide ver otro más simple. Siegler propuso que una persona conoce varias estrategias a la vez y elige entre ellas según el problema. Lemaire y Siegler (1995) describieron cuatro aspectos de ese cambio: repertorio, distribución, eficiencia y selección. Nivel de evidencia: **moderada**. La fijación y la elección de estrategias están bien documentadas, pero hay poca evidencia directa sobre la regla "si me atasco, cambio de técnica", y casi toda viene de laboratorio, no de trabajo con IA.

**Cómo se aplica.**
1. Al planificar, define la señal de atasco: "si en 3 intentos no avanzo".
2. Nombra la técnica actual para hacerla visible.
3. Detente y diagnostica: ¿falla la técnica o falta información?
4. Elige del repertorio una técnica de otro tipo, no una variante.
5. Fija un límite a la nueva técnica y registra qué funcionó.

**Claves.**
- Repetir el mismo prompt con otras palabras es la misma técnica.
- No cambies demasiado pronto: la persistencia también produce ideas.
- Un tema nuevo no es un cambio de técnica: trátalo como bifurcación.

**Ejemplo.** Lucía especifica con Claude un sistema de permisos, en la fase crear del PCRC. Tras tres versiones casi iguales, se cumple su señal. Cambia de prosa a casos: "Dame una tabla con 6 casos límite... No escribas la regla todavía." La tabla revela dos casos contradictorios, y decide "denegar gana siempre". Una pregunta sobre permisos temporales queda como bifurcación liviana aparcada y luego como issue en GitHub.

**Fuentes.** [Jansson y Smith (1991)](https://doi.org/10.1016/0142-694X(91)90003-F) · [Lemaire y Siegler (1995)](https://doi.org/10.1037/0096-3445.124.1.83)

### Regla de corte

**Qué es.** Una condición que fijas antes de empezar y que dice cuándo parar, cambiar de enfoque o abandonar. Por ejemplo: "si en 2 horas el test sigue fallando, cambio de enfoque". Es una regla si-entonces especializada: su "entonces" siempre es parar, cambiar de enfoque o abandonar.

**Origen y evidencia.** La regla combate la escalada de compromiso, que consiste en invertir más en algo que va mal para justificar la decisión inicial. Staw (1976) la mostró en estudiantes. El metaanálisis (estudio que combina muchos estudios) de Sleesman y colegas (2012), que combinó 166 muestras, confirmó que sentirse responsable y estar cerca del final aumentan la escalada. El costo hundido (seguir porque ya invertiste) resultó más débil de lo esperado. Simonson y Staw (1992) y Heath (1995) mostraron en laboratorio que fijar un límite o presupuesto de antemano reduce la escalada. Nivel de evidencia: **moderada**. El fenómeno está muy estudiado, pero no hay metaanálisis de la técnica ni estudios con asistentes de IA.

**Cómo se aplica.**
1. Al planificar, escribe: "Si [estado medible] cuando llegue a [límite de tiempo, intentos o tokens], entonces [acción]".
2. Elige la acción de antemano: parar, cambiar de enfoque, volver a explorar en el PCRC o abrir una bifurcación pesada (un issue en GitHub).
3. Pide a Claude que vigile el límite y te avise.
4. Al monitorear, compara el estado real con la regla en cada punto de control.
5. Al controlar, ejecuta la acción sin renegociar en caliente. Al evaluar, ajusta el límite.

**Claves.**
- Usa criterios observables ("el test pasa"), no sensaciones ("siento que avanzo").
- Evita el "solo un intento más" y mover el límite justo al alcanzarlo.
- Pregúntate: "si empezara hoy, ¿elegiría este camino?". Una regla demasiado estricta también puede cortar algo que iba bien.

**Ejemplo.** Lucía crea con Claude una gramática de permisos y fija: "si después de 3 rondas la gramática no cubre los 5 casos, vuelvo a explorar". En la ronda 2 aparca una idea nueva como bifurcación liviana. En la ronda 3 Claude avisa: "Llegamos al límite: 4 de 5 casos". Lucía cumple la regla. Al explorar, la idea aparcada resulta mejor y pasa a convergida. La gramática queda como issue en GitHub.

**Fuentes.** [Sleesman y otros (2012)](https://gwern.net/doc/psychology/cognitive-bias/sunk-cost/2012-sleesman.pdf) · [Simonson y Staw (1992)](https://gwern.net/doc/psychology/cognitive-bias/sunk-cost/1992-simonson.pdf) · [Heath (1995)](https://gwern.net/doc/psychology/cognitive-bias/sunk-cost/1995-heath.pdf)

### Retroceder de fase

**Qué es.** Retroceder de fase es volver a una fase anterior del PCRC cuando la fase actual muestra que algo de antes estaba mal. Por ejemplo, volver de implementar a explorar.

**Origen y evidencia.** Nadie la inventó como tal. Sale de tres líneas de trabajo. El aprendizaje de doble ciclo de Argyris y Schön (1978) distingue entre corregir un error dentro de las reglas que ya se tienen (ciclo simple) y revisar los supuestos que llevaron al error (doble ciclo). El modelo de resolución creativa de problemas dejó de ser una secuencia fija de etapas. Y los estudios de diseño muestran que problema y solución evolucionan juntos (Dorst y Cross, 2001) y que los expertos pasan más veces de un paso a otro (Atman y colegas, 2007). Nivel de evidencia: **débil**. Son estudios descriptivos con pocas personas. Muestran que los expertos iteran, pero no prueban que enseñar a retroceder mejore los resultados.

**Cómo se aplica.**
1. Detecta la señal al monitorear: una prueba imposible de escribir, una contradicción, una solución que crece sin parar.
2. Diagnostica: "¿Este problema nació en esta fase o en una anterior?". Si nació aquí, corrígelo aquí.
3. Vuelve a la fase más cercana que explique el problema.
4. Nombra en una frase el supuesto que cae.
5. Conserva lo que sigue sirviendo y rehaz desde ahí.

**Claves.**
- Fija al planificar una regla si-entonces para retroceder.
- No lo confundas con una bifurcación: si la idea nueva no invalida la fase actual, apárcala y sigue.
- No vuelvas al principio por reflejo ni retrocedas sin límite de tiempo.

**Ejemplo.** Lucía escribe con Claude la especificación de permisos de una aplicación de facturas. En implementar aparece la tercera regla con dos excepciones. Activa su regla: "Para. ¿El problema está en la redacción o en el modelo de roles?". Concluye que la falla viene de explorar y nombra el supuesto descartado: "los permisos dependen solo del rol". Vuelve a explorar, el cliente confirma que dependen del departamento, y una idea lateral queda como issue en GitHub. Resultado: de 14 reglas con 6 excepciones a 12 reglas sin excepciones, conservando las reglas 1 a 10.

**Fuentes.** [Double-loop learning](https://en.wikipedia.org/wiki/Double-loop_learning) · [Dorst y Cross (2001)](https://oro.open.ac.uk/3278) · [Atman et al. (2007)](https://doi.org/10.1002/j.2168-9830.2007.tb00945.x)

## Evaluar

Al cerrar una fase o el proceso: revisar el resultado y el proceso, y llevar lo aprendido a la próxima planificación.

### Revisión después de la acción

**Qué es.** Una conversación breve y estructurada al cerrar una sesión o una fase. Compara lo planeado con lo que pasó, busca por qué hubo diferencias y decide qué mantener y qué cambiar. No busca culpables: busca aprender. Se diferencia de la retrospectiva en que su eje es comparar plan y realidad, no ordenar acciones en empezar, dejar y seguir.

**Origen y evidencia.** Nació en el Ejército de EE.UU., que la usa desde hace décadas en sus ejercicios de entrenamiento. Suele decirse que surgió en los años 70, pero no pudimos confirmar esas fechas en el informe original. Combina retroalimentación (información sobre el resultado propio), reflexión y discusión. El metaanálisis (estudio que combina muchos estudios) de Tannenbaum y Cerasoli (2013), con 46 muestras, halló un efecto medio d = 0,67 (0,8 se considera grande): el desempeño mejoró cerca de un 25 %, en equipos e individuos. Keiser y Arthur (2021) hallaron d = 0,79 y vieron que revisar con registros objetivos ayuda. Nivel de evidencia: **fuerte** para mejorar el desempeño, aunque los estudios vienen sobre todo del entrenamiento militar y médico, no del trabajo con IA.

**Cómo se aplica.**
1. Hazla pronto, al cerrar la sesión o una fase del PCRC, con los hechos frescos.
2. Pregunta qué querían lograr: repite el objetivo y el criterio de éxito definidos al planificar.
3. Describe qué pasó en realidad con hechos: diff, pruebas, decisiones.
4. Busca por qué hubo diferencias, en el proceso y no en personas.
5. Saca dos o tres lecciones y escribe cada una como regla "si… entonces" en el CLAUDE.md, un issue o un documento.

**Claves.**
- Revisa también los éxitos, no solo los fallos.
- Apóyate en registros objetivos, no solo en la memoria.
- Una lección que nadie registra no cambia nada.

**Ejemplo.** Lucía cierra una sesión con Claude y pide: "Hagamos una revisión después de la acción. Primero: ¿qué queríamos lograr hoy?". Claude compara el plan (exportar a CSV con todas las pruebas pasando, en dos horas) con lo real: dos pruebas fallan con caracteres especiales y usaron tres horas. La causa: pasaron de decidir a implementar sin ejemplos de datos reales, y una bifurcación liviana sobre zonas horarias costó 40 minutos. Lucía agrega al CLAUDE.md "si una bifurcación pasa de 15 minutos, entonces la aparcamos" y convierte la bifurcación aparcada en un issue. En la sesión siguiente, la fase termina dentro del tiempo planificado.

**Fuentes.** [Tannenbaum y Cerasoli (2013)](https://pubmed.ncbi.nlm.nih.gov/23516804/) · [Keiser y Arthur (2021)](https://pubmed.ncbi.nlm.nih.gov/32852990/) · [Ellis y Davidi (2005)](https://pubmed.ncbi.nlm.nih.gov/16162059/)

### Exam wrapper

**Qué es.** Un exam wrapper ("envoltorio del examen") es una hoja breve que se completa al recibir un resultado. Pregunta tres cosas: cómo te preparaste, qué errores cometiste y de qué tipo, y qué cambiarás la próxima vez. A diferencia de las otras técnicas de evaluar, parte de un resultado externo y clasifica los errores por tipo.

**Origen y evidencia.** Marsha Lovett, de la Universidad Carnegie Mellon, la describió en un capítulo de 2013. Se apoya en el aprendizaje autorregulado: la persona fija metas, observa cómo aprende y ajusta sus estrategias. Trabaja en el nivel metacognitivo, en la fase evaluar del PCM, y su salida alimenta la fase planificar del ciclo siguiente. Los resultados no coinciden. En un experimento con 86 estudiantes de un solo curso no hubo diferencias en notas ni en conciencia metacognitiva. En un estudio de 1.894 estudiantes, en nueve cursos, la relación con la nota fue positiva pero pequeña (r de 0,10 a 0,14), y más fuerte donde el wrapper era obligatorio. Es un estudio correlacional: muestra que dos cosas van juntas, no que una cause la otra. Nivel de evidencia: **mixta**. Hay pocos estudios bien controlados y ningún metaanálisis. El efecto parece depender del uso repetido y de cumplir el plan.

**Cómo se aplica.**
1. Elige un "examen" verificable: una revisión de código, una prueba que falla, una especificación leída por otra persona.
2. Anota cómo te preparaste y cuánto tiempo dedicaste a cada cosa.
3. Clasifica cada error por tipo y busca el que domina.
4. Escribe una o dos acciones como planes "si… entonces".
5. Relee el wrapper antes de planificar el ciclo siguiente.

**Claves.**
- Repítelo en cada ciclo, con las mismas preguntas, para poder comparar.
- Cuenta los errores por tipo. "Tengo que esforzarme más" no es un plan: nombra una acción observable.
- Si no lo relees, la técnica pierde su sentido.

**Ejemplo.** Lucía recibe su especificación de pagos con 9 observaciones. Pide: "Hagamos un exam wrapper de esta revisión. Hazme las preguntas una por una." Cinco son requisitos ausentes. Vienen de una bifurcación liviana que dejó aparcada y nunca retomó. Su plan: "Si cierro la fase explorar, entonces Claude me muestra todas las bifurcaciones livianas abiertas o aparcadas" para descartarlas, hacerlas converger o pasarlas a issue en GitHub. La revisión siguiente trae 3 observaciones y ningún requisito ausente.

**Fuentes.** [Hodges y otros (2020), texto completo en ERIC](https://files.eric.ed.gov/fulltext/EJ1290331.pdf) · [Soicher y Gurung (2017)](https://liberalarts.oregonstate.edu/biblio/do-exam-wrappers-increase-metacognition-and-performance-single-course-intervention) · [Weimer (2017), Faculty Focus](https://www.facultyfocus.com/articles/educational-assessment/strategy-work-look-exam-wrappers/)

### Preguntas de evaluación

**Qué es.** Cuatro preguntas fijas que te haces al cerrar una unidad de trabajo: ¿logré mi objetivo?, ¿qué funcionó?, ¿qué no funcionó?, ¿qué haría distinto la próxima vez? Trabaja en el nivel metacognitivo, en la fase evaluar del PCM. Son la parte final de la lista de Schraw: las preguntas de planificación se hacen antes y las de monitoreo durante el trabajo. A diferencia de la revisión después de la acción, es una autorrevisión corta con preguntas fijas, sin una conversación estructurada.

**Origen y evidencia.** Schraw (1998) publicó una lista de control de regulación con preguntas para planificar, monitorear y evaluar. Se basa en Flavell y Brown: la metacognición tiene dos partes, conocer cómo pienso y dirigir cómo pienso. Evaluar es la parte que mira el resultado y el método después de actuar. Nadie probó la lista sola. Sí hay respaldo para la reflexión estructurada: un metaanálisis (estudio que combina muchos estudios) de Tannenbaum y Cerasoli (2013) sobre revisiones después de una tarea halló que los grupos que las hacían rindieron cerca de un 25 % más que los de control (d = 0,67), en equipos y en individuos. Nivel de evidencia: **moderada**. La reflexión después de actuar tiene buen apoyo, pero la lista exacta no se probó por separado.

**Cómo se aplica.**
1. Al cerrar una fase del PCRC, una sesión o una tarea, relee el objetivo que escribiste al planificar.
2. Responde si lo lograste (sí, no o en parte) con un hecho: un test que pasa, una sección cerrada.
3. Nombra una o dos acciones que funcionaron y dónde perdiste tiempo, con su causa probable.
4. Convierte lo que harías distinto en un plan "si… entonces".
5. Revisa las bifurcaciones livianas abiertas o aparcadas: descártalas, márcalas convergidas o pásalas a pesadas (issue en GitHub). Guarda la lección en el CLAUDE.md.

**Claves.**
- Usa siempre las mismas preguntas, por escrito y enseguida.
- Evalúa también el método, no solo el resultado.
- Evita el "todo bien" sin evidencia y las culpas en lugar de causas.

**Ejemplo.** Lucía cierra la fase verificar de una spec de exportación y le pide a Claude: "Guíame con las preguntas de evaluación. Una por una, y espera mi respuesta." Descubre que logró el objetivo en parte: faltan dos ejemplos de PDF. Perdió 40 minutos en la paginación, una bifurcación que no aparcó. Su nueva regla: "Si un tema nuevo me ocupa más de 10 minutos, entonces lo aparco como bifurcación liviana". En 8 minutos tiene un issue para la paginación y la regla en el CLAUDE.md.

**Fuentes.** [Schraw (1998)](https://doi.org/10.1023/A:1003044231033) · [Tannenbaum y Cerasoli (2013)](https://pubmed.ncbi.nlm.nih.gov/23516804/) · [Lista de control de Schraw (OpenLearn)](https://www.open.edu/openlearncreate/mod/page/view.php?id=236090)

### Calibración

**Qué es.** La calibración compara la confianza que tenías con el resultado real. Estás bien calibrado si, de todas las veces que dices "80 % seguro", aciertas cerca del 80 %. Si aciertas menos, tienes exceso de confianza. A diferencia de los juicios de confianza, que se hacen uno a uno al monitorear, la calibración junta varios juicios al evaluar y mide si aciertan.

**Origen y evidencia.** La medida viene de la meteorología: Brier (1950) propuso el **Brier score**, el promedio de (probabilidad dicha − resultado)². Cero es perfecto. Lichtenstein, Fischhoff y Phillips (1982) revisaron los estudios hasta 1980: la gente suele tener exceso de confianza, y este crece en las tareas difíciles. En el PCM, la calibración es parte del monitoreo, y en la fase evaluar se compara lo juzgado con lo que pasó. Carpenter y colaboradores (2019) mostraron que la retroalimentación sobre la confianza mejora la calibración y se transfiere a otra tarea. El efecto Dunning-Kruger es discutido: conviene no apoyarse en él. Nivel de evidencia: **moderada**. Es fuerte que existe la mala calibración y moderado que la retroalimentación repetida la mejora.

**Cómo se aplica.**
1. Antes de actuar, escribe una afirmación verificable con una probabilidad de una escala fija (50, 60, 70, 80, 90, 99 %).
2. Registra cada predicción en la nota de la sesión o en el issue.
3. Al evaluar, marca cada predicción con 1 (ocurrió) o 0 (no ocurrió).
4. Compara la confianza media con la tasa de aciertos. Con muchas predicciones, calcula el Brier score.
5. Decide un ajuste concreto para la próxima planificación.

**Claves.**
- Nunca escribas la confianza después de ver el resultado: eso anula la técnica.
- Predice cosas comprobables sin discusión. "El revisor aprueba sin cambios" sirve; "el diseño es bueno", no.
- Junta varias predicciones antes de sacar conclusiones, y no uses siempre 50 % para no comprometerte.

**Ejemplo.** Lucía va a entrar a la fase verificar del PCRC con una especificación de facturación. Escribe tres predicciones (90 %, 80 %, 70 %) y le pide a Claude: "No me digas el resultado hasta que confirme que mis predicciones están guardadas". Las tres fallan. Claude calcula un Brier score de 0,65 y nota que el desvío aparece cuando la especificación toca otra. Lucía agrega al plan: "Si la especificación depende de otra, entonces bajo mi confianza a 60 % como máximo". Dos semanas después acierta 4 de 6 con confianza media de 65 %.

**Fuentes.** [Lichtenstein, Fischhoff y Phillips (1982)](https://www.cambridge.org/core/books/abs/judgment-under-uncertainty/calibration-of-probabilities-the-state-of-the-art-to-1980/9F0C9EC2997AEEB6DDDB304C2F935A16) · [Carpenter y colaboradores (2019)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6390881) · [Callender, Franco-Watkins y Roberts (2016)](https://scholars.uky.edu/en/publications/improving-metacognition-in-the-classroom-through-instruction-trai/)

### Retrospectiva (empezar, dejar, seguir)

**Qué es.** Una revisión breve al cerrar un ciclo de trabajo. Ordena lo aprendido en tres columnas: qué empezar a hacer, qué dejar de hacer y qué seguir haciendo. Comparte la base de la revisión después de la acción, pero termina en tres columnas de acciones en vez de comparar plan y resultado.

**Origen y evidencia.** Kerth (2001) definió la retrospectiva como una reunión para aprender, no para buscar culpables. Derby y Larsen (2006) la dividieron en cinco pasos. No se pudo verificar quién creó el formato "empezar, dejar, seguir". La teoría viene del aprendizaje por experiencia: actuar, revisar, sacar una lección y cambiar la próxima acción. En el PCM es la fase evaluar, y alimenta la fase planificar del ciclo siguiente. Un metaanálisis (estudio que combina muchos estudios) de Tannenbaum y Cerasoli (2013) halló que las revisiones guiadas después de una tarea mejoran el desempeño cerca de un 25 % (d = 0,67), en equipos y en personas solas. Ellis y Davidi (2005) vieron que revisar también los éxitos enseña más. Nivel de evidencia: **moderada** para las revisiones estructuradas, con resultados consistentes pero con pocas personas en total. El formato de tres columnas en sí no tiene evidencia formal.

**Cómo se aplica.**
1. Fija el alcance: una sesión, una fase del PCRC o un entregable.
2. Reúne hechos antes de opinar: commits, tests que fallaron, bifurcaciones abiertas o aparcadas, tiempo usado.
3. Llena las tres columnas y elige una o dos acciones por columna, escritas como reglas "si… entonces".
4. Guarda las reglas duraderas en el CLAUDE.md. Las tareas grandes pasan a ser una bifurcación pesada (un issue en GitHub).
5. Lee las acciones al planificar el próximo ciclo y comprueba si se cumplieron.

**Claves.**
- Básate en datos: sin ellos, las opiniones abren la puerta a sesgos.
- No te saltes "seguir" ni escribas acciones vagas como "ser más ordenado".
- Si un tema vuelve en cada retrospectiva, abre un issue o descártalo.

**Ejemplo.** Lucía cierra con Claude una sesión de especificación de un módulo de pagos. Pide: "Antes de opinar, lista los hechos". Claude informa que reescribieron 3 requisitos dos veces y que una bifurcación abierta consumió 40 minutos. Convierten las columnas en tres reglas si-entonces y las guardan en el CLAUDE.md. En la sesión siguiente escriben 11 requisitos sin reescribir ninguno.

**Fuentes.** [Tannenbaum y Cerasoli (2013)](https://pubmed.ncbi.nlm.nih.gov/23516804/) · [Ellis y Davidi (2005)](https://pubmed.ncbi.nlm.nih.gov/16162059/) · [Lehtinen y otros (2017)](https://link.springer.com/article/10.1007/s10664-016-9464-2)

### Diario de reflexión

**Qué es.** Escribir unas líneas al cerrar una sesión para pensar sobre lo que hiciste. Es la *reflexión sobre la acción*: pensar después, no mientras trabajas. A diferencia de las preguntas de evaluación, aquí escribes en prosa, siguiendo los pasos de Gibbs.

**Origen y evidencia.** La idea viene de Dewey (1933). Schön (1983) separó la reflexión en la acción de la reflexión sobre la acción. Gibbs (1988) le dio seis pasos. La teoría: escribir obliga a *codificar* la experiencia, es decir, convertirla en ideas explícitas. Eso ayuda a entender la tarea y aumenta la *autoeficacia* (confianza en la propia capacidad). Di Stefano y colegas (2014) concluyen que, con algo de experiencia, reflexionar por escrito rinde más que seguir practicando. Se cita una mejora de cerca del 23 % en un examen final, pero esa cifra no se pudo comprobar en el texto completo. Berthold y colegas (2007) vieron que las preguntas guía mejoran los resultados. Nückles y colegas (2010) vieron que estorban cuando la persona gana experiencia. No hay un metaanálisis (estudio que combina muchos estudios) específico. Nivel de evidencia: **moderada**, porque hay experimentos consistentes pero pocas síntesis.

**Cómo se aplica.**
1. Al cerrar la sesión, reserva de 5 a 15 minutos.
2. Describe qué hiciste y en qué fase del PCRC o del PCA, y anota cómo te sentiste.
3. Evalúa contra lo fijado en la fase planificar del PCM y analiza la causa, no solo el síntoma.
4. Concluye y escribe una o dos acciones como "si… entonces".
5. Revisa las bifurcaciones: cierra las livianas (descartado, convergido) o pasa a pesadas (issue en GitHub) las que lo merecen.

**Claves.**
- Pide a Claude que haga las preguntas, pero escribe tú: delegar la escritura pierde el efecto.
- Evita quedarte en la descripción o en conclusiones vagas como "tengo que organizarme mejor".
- Usa preguntas fijas al principio y retíralas cuando el hábito exista.

**Ejemplo.** Lucía cierra una sesión sobre reembolsos y dice: "Hazme las preguntas de Gibbs una por una y no respondas por mí". Descubre que perdió 40 minutos en una bifurcación liviana abierta. Su plan: "Si aparece un tema que no afecta la decisión de la fase actual, entonces le digo a Claude: 'apárcalo'". En la sesión siguiente lo aplica y la fase decidir termina a tiempo.

**Fuentes.** [Di Stefano y colegas (2014)](https://papers.ssrn.com/abstract=2414478) · [Nückles y colegas (2010)](https://doi.org/10.1007/s11251-009-9106-9) · [Gibbs' Reflective Cycle](https://reflection.ed.ac.uk/reflectors-toolkit/reflecting-on-experience/gibbs-reflective-cycle)
