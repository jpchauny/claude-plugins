# Qué significa "done" en SDD: dimensiones, tensiones y la unidad de aceptación

Investigación divergente hecha con un workflow de 95 agentes: 16 lentes disciplinares, consolidación, 3 rondas de críticos de completitud, verificación adversarial con 2 lentes y 4 lentes de tensiones. Fecha: 2026-10-26. Datos completos en [done-dimensiones-tensiones-datos.json](done-dimensiones-tensiones-datos.json).

## 1. Resumen

1. En SDD, done no es "se cumplen todas las cláusulas MUST". Es un **veredicto sobre una unidad de aceptación**: el nivel más bajo del árbol de producto que tiene criterio propio y se puede juzgar de punta a punta.
2. Ese veredicto depende de varios parámetros: contra qué versión de la spec y bajo qué supuestos se mide, con qué evidencia (fuerza, independencia, legibilidad), quién la acepta y qué riesgo se transfiere al aceptarla.
3. Por diseño, el veredicto es imperfecto. Las imperfecciones tienen que quedar dispuestas: desviaciones, riesgo residual, decisiones que la IA tomó en nombre de la persona y una frontera negativa declarada.
4. Además, done no es un instante. Es una escalera de estados (encendido, limpio, final, garantía) y un predicado que se mantiene y caduca por reloj o por eventos.
5. En el SDD democratizado se juntan varios problemas. La IA puede redactar, implementar y verificar. La persona solo puede reconocer lo que ve. Los roles colapsan. Por eso la validación, la independencia y la legibilidad de la evidencia pasan a ser lo central del done.

## 2. Taxonomía

Hay 217 dimensiones verificadas, agrupadas en 14 familias. † marca las dimensiones que quedaron con dudas de solapamiento en la verificación: se conservan, pero podrían fusionarse.

### F1. Objeto: qué es el "algo" que se acepta
- **D1** Nivel de aceptación: tarea ↔ paquete de trabajo ↔ producto. El "algo" es el nivel más bajo con criterio propio. Si el done se pone más abajo, sirve para piezas inútiles; si se pone más arriba, el feedback se vuelve inaceptablemente lento.
- **D11** Construido ↔ operable y transferido. Hay un segundo destinatario (operación o mantenimiento) con criterios que ningún usuario pide.
- **D18** Sistema de interés ↔ sistemas habilitadores. Migración, instalador o pipeline: nadie los especifica si no lo hace la IA.
- **D24** Identidad de configuración: lo verificado = lo documentado = lo desplegado. La evidencia vale solo para el artefacto exacto.
- **D40** Variante única ↔ familia de productos. Hay que decidir si done cubre una configuración, las soportadas o todas.
- **D59** Peldaño en una cadena de refinamiento. La unidad puede ser un paso de refinamiento con sus obligaciones descargadas.
- **D73** Producto núcleo ↔ producto completo. La spec describe el núcleo; la persona no sabe pedir el resto.
- **D84** Objeto del done: código ↔ spec anclada ↔ spec como fuente. Fija sobre qué artefacto recaen la evidencia y la responsabilidad.
- **D95** Corte vertical ↔ horizontal (alcance × fidelidad). Si no se declara la fidelidad objetivo, se entrega todo a medias o una parte perfecta.
- **D96** Instancia ↔ generador. El done de un generador es estadístico, sobre el espacio de sus salidas.
- **D110†** Conformidad completa ↔ perfil declarado. Un subconjunto no declarado es un incumplimiento disfrazado.
- **D117** Comportamiento especificado ↔ aprendido. Es una unidad que no encaja en la cadena cláusula → código → test.
- **D154†** Entregable = código ↔ ensamblaje de código, datos, pesos, prompts y configuración. Hay que fijar todos los artefactos que definen el comportamiento.
- **D163** Contenedor correcto ↔ contenido correcto (calidad del dato vivo). Cuando el output es el dato, el done se mide sobre el contenido.
- **D172** Acabado por quien diseña ↔ acabado por quien usa. Que falte algo puede ser un requisito; en ese caso se aceptan los puntos de extensión.
- **D193** Hallazgo reproducible → replicable → robusto → generalizable. Es el done de un análisis, no de un programa.
- **D196** Código verificado ↔ solución verificada ↔ modelo creíble. Un cálculo sin barra de error ni rango de validez no está terminado.
- **D201** Todo o nada ↔ interrumpible. Se puede exigir que cada punto de parada sea en sí un done aceptable.
- **D204** Software situado (n=1) ↔ software de producto. El tamaño de la audiencia cambia el perfil entero de done.
- **D212** Tamaño de la unidad: con valor propio ↔ cabe en una revisión. Si las dos cotas no se cruzan, la aceptación se parte en dos.
- **D214** Done total ↔ congelamientos por aspecto. Son done parciales que habilitan trabajo aguas abajo.
- **D220** Vida útil prevista: un solo uso ↔ perenne. La vida prevista decide qué ejes aplican.
- **D221** Unidad que sigue el patrón ↔ unidad que sienta precedente. La primera de su clase se copia N veces, y sus defectos también.

### F2. La spec como entregable
- **D7** Done de la spec (Ready) ↔ done del producto. Sin un Ready se construye sobre arena; si el Ready es una puerta rígida, se pierde lo que se aprende al implementar.
- **D12** Línea base fija ↔ móvil. Algo es done contra una versión v3 y puede no serlo contra la v4.
- **D30** Done incondicional ↔ condicionado a supuestos (W, S ⊢ R). Si un supuesto deja de ser cierto, se cae el requisito sin tocar el código.
- **D33** Completitud interna ↔ externa. Solo se puede declarar contra la interna, y eso da una falsa sensación de terminado.
- **D34** Consistencia estricta ↔ inconsistencia tolerada. Una contradicción conocida puede convivir si queda registrada.
- **D38** Precisión ↔ comprensibilidad (prosa ↔ formalización). La persona aprueba un texto y la máquina verifica otro.
- **D41** Problema quieto ↔ problema que se mueve (S/P/E). En los programas tipo E, entregar cambia la intención.
- **D60†** Spec ejecutable ↔ declarativa. La forma de la spec decide quién hace de oráculo.
- **D61** Libertad del implementador: definido ↔ no especificado ↔ indefinido. Un oráculo solo vale sobre la parte que la spec determina.
- **D85** Spec explícita ↔ norma tácita de la base de código. Que pase los tests no significa que un mantenedor lo fusionaría.
- **D86** Sincronía spec/código/tests ↔ deriva. Un cambio que funciona puede dejar el sistema peor especificado.
- **D106** Una implementación ↔ N implementaciones independientes. Las divergencias entre ellas miden la ambigüedad de la spec.
- **D153** Especificado ↔ subespecificado. El done certifica una clase de soluciones, no la solución entregada.
- **D174** Ambigüedad como defecto ↔ ambigüedad constructiva. Precisar puede romper el acuerdo político que sostiene la spec.
- **D188†** Satisfacible ↔ insatisfacible por teorema. El done exige declarar qué propiedad se sacrifica.
- **D218** Alcance positivo ↔ frontera negativa declarada (non-goals). Con ella, una ausencia se puede clasificar como decisión o como defecto.
- **D222** Normas consultadas ↔ normas aplicables. "Todas cumplidas" engaña si la IA eligió mal las normas que tocaban.

### F3. Intención y elicitación (persona ↔ IA)
- **D32** Decidido por la persona ↔ por la IA (requisitos derivados y defaults). El done incluye un inventario de lo que se decidió en nombre de la persona.
- **D37** Criterio articulado de antemano ↔ reconocido al ver (IKIWISI). Parte del done es reconocimiento; cada rechazo debería convertirse en cláusula.
- **D39** Obligatorio ↔ deseable ↔ que encanta (Kano). Con todos los MUST cumplidos, lo entregado a lo sumo no molesta.
- **D68** Lo pedido literalmente ↔ el job to be done. La IA queda entre la literalidad y el paternalismo.
- **D77†** Complejidad absorbida ↔ trasladada al usuario (Tesler). "Permite configurar X" cumple la cláusula pasándole la decisión al usuario.
- **D82** Cumplimiento literal ↔ fidelidad a la intención. Hace falta un tercer estado: bloqueado por contraejemplo.
- **D138** Dicho ↔ tácito. "Cumple todo lo pedido" y "no sirve" pueden ser verdad a la vez.
- **D139** Comprensión mutua verificada ↔ supuesta. Si la persona aprobó lo que no podía leer, todo lo construido hereda el error.
- **D179†** Elicitación saturada ↔ truncada. Dónde se deja de preguntar fija qué decide la persona y qué decide la IA.
- **D199** Resolver ↔ solucionar ↔ disolver. Puede haber un done positivo sin construir nada.
- **D203** Intención elicitada ↔ inducida. Validar contra una intención que fabricó el entrevistador no garantiza nada.

### F4. Evidencia: fuerza, forma y alcance
- **D15** Evidencia de producto ↔ de proceso. Las dos son necesarias y ninguna sustituye a la otra.
- **D19** Método: inspección ↔ análisis ↔ demostración ↔ test. Si no se fija el método, se elige después el más barato.
- **D20** Confiar en el generador ↔ verificar cada salida. Hay que decidir si done es una propiedad del artefacto o del proceso.
- **D27** Lista cumplida ↔ argumento que resiste dudas (caso de aseguramiento). La lista mide las partes; el argumento, el todo.
- **D31** Trazabilidad bidireccional. Hace lo pedido y solo lo pedido, desde la frase de la entrevista.
- **D42** Fuerza del oráculo: implícito ↔ parcial ↔ completo. Done nunca es más fuerte que el oráculo disponible.
- **D43** Criterio prerregistrado ↔ post hoc. Si los tests se generan mirando el código, el done se vuelve circular.
- **D44†** Correcto ↔ consistente con una referencia. Hereda los defectos de la referencia.
- **D45†** Cobertura de requisitos ↔ de estructura ↔ de fallos. Un "100%" no significa nada sin decir de qué.
- **D46** Cuantificador: ejemplo ↔ propiedad ↔ exhaustivo acotado ↔ prueba. Hay un salto lógico entre "para todo" y cinco ejemplos.
- **D47** Cuándo parar de probar: adecuación ↔ riesgo residual aceptado. Done es una apuesta, y alguien acepta el riesgo restante.
- **D48** Veredicto determinista ↔ estadístico (pass@k ↔ pass^k). Sin métrica declarada se elige la más fácil.
- **D49†** Dobles de prueba ↔ colaboradores reales. Cada unidad pasa contra un mock que le da la razón.
- **D51** Evidencia severa ↔ complaciente. Done exige evidencia de que la evidencia podía fallar.
- **D53†** Comprobación ↔ exploración. Lo calculado responde "cumple", nunca "especificamos lo correcto".
- **D57†** Satisfacción sustantiva ↔ vacía. Una cláusula puede estar en verde por vacuidad.
- **D58** Base de confianza: regreso infinito ↔ raíz pequeña declarada. Sin raíz declarada, el done sobrevende.
- **D62** Propiedad de traza ↔ hiperpropiedad. Algunas cláusulas no se deciden mirando una sola ejecución.
- **D65** Poder del observador. "Conforme" quiere decir indistinguible para alguien que hay que nombrar.
- **D83†** Done de una generación ↔ invariante bajo regeneración. Cada regeneración reabre lo no especificado.
- **D135** Testimonio ↔ evidencia reproducible por terceros. "La IA informa que pasó" es testimonio.
- **D136** Evidencia por cláusula ↔ de la conjunción. Cien cláusulas al 99% dan una conjunción del 37%.
- **D152** Muestra evaluada ↔ población no vista. Done con barras de error.
- **D156** Correcto en la forma probada ↔ invariante ante perturbaciones. Para quien escribe en prosa libre, esto es lo que más importa.
- **D191** Evidencia mostrable ↔ confidencial. Hay que decidir quién ve qué y cómo se verifica lo que no se muestra.
- **D211** Cobertura temporal: instante ↔ ciclo completo. Hay done que exige tiempo de calendario, no esfuerzo.
- **D213** Corrida corta ↔ operación prolongada. Fallos por acumulación que ningún test de segundos ve.
- **D215** Verificado hoy ↔ verificable mañana. La testabilidad fija el coste de todos los done futuros.

### F5. Integridad del veredicto: verificador y medidor
- **D52** Vara fija y externa ↔ vara negociable por quien implementa. Si la vara se mueve, "pasa" deja de significar algo.
- **D75** Métrica ↔ propósito (Goodhart). Cuanto más automatizable el criterio, más fácil cumplirlo vacío.
- **D78** Juicio imparcial ↔ sesgado (efecto IKEA, complacencia). El constructor y el aceptante quedan aliados contra la verificación.
- **D81** Autoverificación ↔ verificación independiente y diversa. Dos IAs con el mismo modelo comparten puntos ciegos.
- **D87** Medir ↔ medir al medidor. Un juez con un 10% de error invalida el 95% que reporta.
- **D88** Resultado ↔ trayectoria. Dos estados finales iguales pueden merecer veredictos distintos.
- **D99** Evaluador virgen ↔ contaminado. La IA autora es el evaluador más contaminado que existe.
- **D183** Aceptante directo ↔ proxy ↔ sintético. Un usuario simulado da un veredicto autorreferente.
- **D198†** Estado reportado ↔ real (efecto MUM). Un agente que dice "completado" es un eslabón nuevo, con sesgo hacia el sí.
- **D223†** Declaración neutral ↔ estratégica del done. Si declarar dispara efectos, hay incentivos para mover la fecha.
- **D225** Roles separados ↔ colapsados. Con dos actores, "aprobado por otro" se cumple vacíamente.

### F6. Aceptación como acto: actores, autoridad y transferencia
- **D6** Aceptación expresa ↔ tácita (por uso). Si el uso cuenta como aceptación, el done ocurre sin validación.
- **D8** DoD heredado (piso) ↔ propio (solo endurece). Elegir normas sirve para endurecer, nunca para omitir el piso.
- **D13** Tolerancia cero ↔ banda de tolerancia. La banda reparte la autoridad entre la IA y quien decide.
- **D14** Done para quién: quien pide ↔ quien usa ↔ afectado ↔ regulador. Democratizar el pedido no democratiza la aceptación.
- **D28** Done técnico ↔ acto institucional de aceptación. Separa "terminado" de "aceptado".
- **D29** Perfecto ↔ imperfección dispuesta. Done significa que cada imperfección tiene disposición, dueño y razón.
- **D104** Done propio ↔ impuesto por terceros. Hay pisos que la IA tiene que traer aunque nadie los pida.
- **D128** Entrega perfecta ↔ cumplimiento sustancial. Un MUST incumplido no siempre anula el resto.
- **D132** Propiedad transferible ↔ incierta. Un entregable perfecto puede no ser apropiable por el cliente.
- **D140†** Aceptar por comprender ↔ por confiar. Hay que decidir qué se acepta por confianza respaldada.
- **D141** Evidencia técnica ↔ legible por quien acepta. Correcta y legible son dos requisitos distintos.
- **D142** Consentimiento informado ↔ aprobación nominal. Con cientos de decisiones, el "sí" deja de significar algo.
- **D144†** Done como entrega ↔ como autonomía de la persona. Sin autonomía, cada done crea dependencia.
- **D170** Regla de agregación: dueño único ↔ consenso ↔ veto ↔ mayoría. Con varios aceptantes, "aceptado" no está definido sin una regla.
- **D173** Riesgo de la ambigüedad: quién redactó ↔ quién implementó ↔ quién aceptó. En SDD la IA redacta y también implementa.
- **D180†** Cierre lógico ↔ psicológico. El done técnico no termina la relación de la persona con la obra.
- **D181** Criterio que baja en la cadena ↔ que se pierde. Orquestador → subagente: el done se degrada en cada eslabón.
- **D182** Autor del criterio: productor ↔ consumidor. El done del productor es la unión de los contratos de sus consumidores.
- **D184** El mismo aceptante ↔ un sucesor que no reconoce lo aceptado. Sin razones registradas, el done se reabre.
- **D185** El yo de hoy ↔ el yo futuro. Sesgo temporal de quien juzga.
- **D194** Licencia legal ↔ licencia social. Lo legal y aceptado puede tener que retirarse.
- **D200** Veredicto inapelable ↔ impugnable. Sin procedimiento de disputa, manda quien tiene más poder.
- **D205** Done técnico ↔ político. La resistencia de quien pierde poder no está en ninguna cláusula.
- **D207** Aceptación definitiva ↔ revocable (defectos latentes). Para una persona no técnica, casi todos los defectos son latentes.
- **D226** Riesgo del productor ↔ del consumidor. Toda prueba favorece a una parte; si la calibra la IA, la inclina a su favor.
- **D229†** Responsabilidad alineada con el control ↔ zona de deformación moral. Aceptar puede solo fabricar un culpable.
- **D230** Done unilateral ↔ bilateral. La persona también tiene entregables (datos, credenciales, decisiones).

### F7. Validación y valor
- **D2** Verificado ↔ validado. La IA llega sola al done verificado; la validación es la única ancla humana.
- **D3** Output ↔ outcome ↔ beneficio. Los MUST describen outputs; a la persona le importa el beneficio.
- **D22†** Prueba de desarrollo ↔ operacional. "Se puede vivir con esto" frente a "cumple la misión".
- **D69** Riesgo despejado: factible ↔ usable ↔ valioso ↔ viable. Que la IA termine algo solo prueba que era factible.
- **D70†** Calidad inherente ↔ percibida. Una IA optimizada para la aprobación pule la superficie.
- **D71** Expectativa fija ↔ móvil (deriva de Kano). El done tiene una fecha de vencimiento externa.
- **D72†** Desplegado ↔ liberado ↔ descubierto ↔ adoptado ↔ retenido. Que nadie descubra una capacidad equivale a que no exista.
- **D74†** Aprobación declarada ↔ conducta observada. Hay que decidir si la aprobación cierra el done o abre un período de observación.
- **D79** Primera experiencia ↔ uso sostenido. La aceptación cae en la demo; el done real ocurre en dos etapas.
- **D80** Construir ↔ saber. El done de un experimento es una hipótesis decidida.
- **D93†** Mecánica especificada ↔ experiencia emergente (MDA). La spec vive en las mecánicas y el juicio en las estéticas.
- **D100** Construido ↔ afinado. El mecanismo se verifica; la calibración se valida con una población.
- **D171** Done absoluto ↔ relativo a la alternativa (no inferioridad). "Mejor que como lo hago hoy", con un margen δ fijado antes.
- **D208** Valor individual ↔ valor de red. El done incluye llegar a la masa crítica.
- **D228** Outcome observado ↔ atribuible. Declarar done por outcome sin contrafactual es declararlo por coincidencia.
- **D231** Usuario con salida ↔ cautivo. Con usuarios cautivos, el uso no prueba nada y solo queda la voz.

### F8. Comportamiento: exigido, prohibido, preservado
- **D10** Suficiente ↔ excesivo (gold plating). Entregar de más es un defecto.
- **D36** Comportamiento exigido ↔ prohibido. Las specs que salen de una entrevista son casi siempre positivas.
- **D56** Seguridad ↔ vivacidad. Una spec hecha solo de prohibiciones la cumple un sistema que no hace nada.
- **D64** Lo que cambia ↔ lo que debe seguir igual. Hay que verificar el radio de impacto permitido.
- **D67†** Dentro ↔ fuera de la precondición. El usuario real vive fuera del contrato.
- **D107** Aceptar lo válido ↔ rechazar lo inválido, y en qué fase. Una cláusula en positivo admite un entregable permisivo.
- **D108†** Diagnóstico correcto ↔ útil. El camino del error también es entregable.
- **D113†** Spec correcta ↔ suficiente (SOTIF). La spec misma puede ser el defecto.
- **D126** Fallo previsto ↔ emergente. Hacen falta criterios de recuperación ante lo imprevisto.
- **D157** Responder siempre ↔ saber cuándo abstenerse. Vale también para la IA que implementa.
- **D160** Adversario indiferente ↔ estratégico. Frente a un adversario, done es una cota de coste para un modelo de amenaza.
- **D161** Funciona con lo que tiene ↔ con lo mínimo. Done negativo sobre la capacidad, invisible a los tests funcionales.
- **D165** Usuario que no se equivoca ↔ usuario falible. El error de uso previsible es un defecto del producto.
- **D166** Correcto en valor ↔ correcto a tiempo. El tiempo forma parte de la definición de correcto.
- **D189** Dirección del fallo: fail-safe ↔ fail-secure ↔ fail-operational. Sin dirección declarada, el sistema cae hacia un default genérico.
- **D216** Uso de datos permitido ↔ apropiado al contexto. La reutilización fuera de finalidad funciona y viola.
- **D219** Daño por el sistema ↔ a través del sistema. Funciones correctas usadas como arma.

### F9. Calidad para poblaciones y terceros
- **D21** Nominal ↔ con margen. La IA optimiza hasta el umbral y se detiene.
- **D35** Satisfacción binaria ↔ graduada. Done es un umbral que alguien elige.
- **D101** Existe ↔ se lee. Criterio de done para los activos.
- **D120** Promedio ↔ cola y segmentos. Elegir el percentil es elegir a quién se promete el software.
- **D155** Errores intercambiables ↔ de coste asimétrico. La intención tiene que convertirse en una matriz de costes.
- **D162** Destino del dato: conservar comprensible ↔ olvidar verificablemente. El dato tiene un horizonte distinto del código.
- **D164** Usuario nominal ↔ espectro de capacidades (accesibilidad). La verificación automática cubre solo una parte.
- **D167** Coste interno ↔ externalidades. Nadie del contrato las sufre, así que nadie las prueba.
- **D169** Mundo del autor ↔ mundos de los usuarios (i18n/l10n). Supuestos culturales tácitos para quien especifica y para la IA.
- **D190** Autónomo ↔ supervisable e interrumpible. Un sistema correcto pero no interrumpible es un riesgo aceptado sin saberlo.
- **D192** Destinatario humano ↔ agente (UX ↔ AX). La IA también consume; hay que declarar a qué consumidores se sirve.

### F10. Integración y escala
- **D9** Done local ↔ done integrado. El pegamento sin dueño es la causa estructural de que todo se cumpla y no funcione.
- **D17†** Madurez de las piezas ↔ de las uniones. Los nodos pueden estar done y las aristas no.
- **D26** Especificado ↔ emergente. Las emergencias indeseadas no tienen cláusula.
- **D66** Done monótono ↔ no monótono. Cada adición puede invalidar un done anterior.
- **D94** Rasgos aislados ↔ espacio combinatorio. Con n normas hay n² interacciones que nadie escribió.
- **D97** Consonancia ↔ disonancia entre capas. La coherencia no tiene dueño entre cláusulas.
- **D98†** Pieza aislada ↔ presupuesto compartido. Una pieza nueva puede sacar de done a otra ya aceptada.
- **D116†** Done aislado ↔ libertad de interferencia. Dos unidades done dejan de estarlo juntas.
- **D158†** Done local que compone ↔ que no compone. Las tasas de error se multiplican.
- **D168** Interoperabilidad: conectado ↔ entendido ↔ compuesto (LCIM). Un contrato verde prueba el nivel 2.
- **D186†** Done asíncrono ↔ sincronizado (tren de releases). Terminado no implica disponible.
- **D187** Óptimo de la unidad ↔ óptimo del portafolio. Diez apps done pueden formar un conjunto sin sentido.
- **D195** Done en mi copia ↔ aceptado upstream. El parche local es una carga perpetua oculta.
- **D209** Sistema con dueño ↔ sistema de sistemas. Nadie tiene autoridad para declarar el done del conjunto.

### F11. Escalones y ciclo de vida
- **D5** Done como período: sustancial → final → fin de garantía. Done transfiere riesgos y abre obligaciones.
- **D23†** Done de entrega ↔ de ciclo de vida, incluida la retirada. La salida no tiene dueño.
- **D25** Población alcanzada: IOC ↔ FOC. La misma capacidad, con distinta gente que la usa.
- **D54** Contrato especificado ↔ observado (Hyrum). Done incluye no romper lo que no se prometió.
- **D103** Funciona ↔ está prometido (escalera de madurez). Done es una relación entre el artefacto y la promesa.
- **D109** Un significado ↔ significados versionados. Done relativo a una edición declarada de las normas.
- **D122** Done encendido ↔ done limpio. Retirar el andamiaje es una tarea explícita.
- **D146** Spec del destino ↔ spec de la transición. Done incluye el camino de los datos existentes.
- **D148** Done con teoría viva ↔ huérfano. Si nadie tiene la teoría, la spec con sus razones es la única portadora.
- **D149†** Fase del ciclo de vida. La misma petición puede ser done en evolución e inaceptable en servicio.
- **D150†** Cambio que debe verse ↔ que no debe verse. En un refactor, done se define por ausencia.
- **D202†** Plazo accesorio ↔ esencial. Tarde equivale a no hecho.
- **D210** Clase de servicio: ordinario ↔ urgente ↔ fecha fija ↔ intangible. La vía urgente deja deuda de verificación obligatoria.
- **D217** Cambio hecho ↔ cambio anunciado con preaviso. Un cambio correcto sin aviso incumple.
- **D233** Done del producto ↔ done del proyecto. Agentes con permisos, previews y secretos vivos.

### F12. Vigencia: done como estado
- **D114†** Done que contiene sus condiciones de refutación (SPIs). Sin ellas, el done no se puede falsar.
- **D115** Done por versión ↔ envolvente de cambios preautorizados. Se acepta un artefacto más su espacio de evolución.
- **D118** Done como evento ↔ como estado mantenido. Cada evidencia tiene vida media.
- **D119†** Perfecto ↔ dentro de un presupuesto operativo. Cierto fallo es aceptable y planificado.
- **D121** Interrogable ↔ opaco. Sin observabilidad, la evidencia en producción es imposible.
- **D124** Done anclado al código ↔ a un entorno que deriva. Una relación fechada con el mundo.
- **D125** Cambio individual ↔ flujo de cambios (DORA). Done como propiedad del pipeline.
- **D145** Caducidad por reloj ↔ por evento. Hay que saber qué invalida cada evidencia.
- **D151** Done incremental ↔ acumulativo. Una suite podrida en verde no prueba nada.
- **D175** Juzgado con lo que se sabía entonces ↔ con lo que se sabe después. Cambia la vara, no el sistema.
- **D224** Funcionalidad ejercida ↔ capacidad latente. Vale hasta el próximo simulacro.
- **D227** Done fijado en diseño ↔ negociado en ejecución. Se acepta una política de degradación.
- **D232** Latencia de la señal: inmediata ↔ diferida. El veredicto es provisional sobre indicadores adelantados.

### F13. Gestión, economía y contrato
- **D4†** Binario ↔ crédito parcial. Elegir la regla es elegir qué se puede llamar "casi done".
- **D16** Done binario ↔ madurez demostrada (TRL). "Done para TRL n".
- **D55†** Evidencia barata por cambio ↔ cara por lote. Done provisional hasta que corre la evidencia cara.
- **D76** Regla de parada intrínseca ↔ decisión de parar. Una parte del done se decide, no se descubre.
- **D91** Reversible ↔ irreversible. Done se desdobla en "para probar" y "para comprometerse".
- **D102** Completar ↔ recortar. Recortar es legítimo si deja limpios los rastros.
- **D112** Rigor uniforme ↔ graduado por criticidad. Done es paramétrico; la clase de criticidad también se aprueba.
- **D129** Deuda declarada ↔ oculta. Un done honesto declara el pasivo, también el de la spec.
- **D131** Alcance fijo ↔ presupuesto fijo. La forma del contrato define el done.
- **D176** Terminado ↔ cerrado sin terminar. Matar a tiempo es un éxito y tiene su propio done.

### F14. Meta-ejes (sobre el propio criterio)
- **D177†** Criterio fijo ↔ criterio que aprende de sus escapes. Cada escape es evidencia contra el criterio.
- **D178** Dimensiones implícitas ↔ perfil de done declarado. Elegir qué ejes aplican precede al done.
- **D197** Done sustantivo ↔ ceremonial. Un DoD exhibido y no usado.
- **D206** Conflicto entre ejes: compensatorio ↔ lexicográfico ↔ caso a caso. Sin regla, la IA usa su propio orden implícito.

**Descartadas** (fusionadas en la verificación):
- D50 (Veredicto antes del despliegue ↔ confirmado en producción) → D123 (Laboratorio ↔ campo).
- D63 (Done composicional rely-guarantee) → D9 (Done local ↔ integrado).
- D89 (Done percibido ↔ medido) → D74 (Declarado ↔ observado) / D70 (Inherente ↔ percibida).
- D90 (Coste de producir ↔ de verificar) → D159 (Verificabilidad de la tarea) / D212 (Tamaño de la unidad).
- D92 (Fidelidad literal ↔ percibida) → D70 (Inherente ↔ percibida) / D93 (Mecánica ↔ experiencia).
- D105 (Normativo ↔ de facto) → D54 (Contrato especificado ↔ observado).
- D111 (Autoconstruible y trazable) → D24 (Identidad de configuración).
- D123 (Evidencia de laboratorio ↔ de campo) → D50 (Antes del despliegue ↔ en producción).
- D127 (Quien paga ↔ quien usa) → D14 (Done para quién).
- D130 (Seguir mejorando ↔ parar) → D76 (Regla de parada).
- D133 (Dependencia ↔ salida) → D144 (Autonomía de la persona).
- D134 (Corroborado ↔ demostrado) → D46 (Cuantificador de la evidencia).
- D137 (Confianza cuantificada) → D134 (Corroborado ↔ demostrado).
- D143 (Suficiente ↔ ilimitado) → D10 (Gold plating).
- D147 (Envejecimiento por inacción ↔ por intervención) → D148 (Teoría viva).
- D159 (Verificar barato ↔ tan caro como hacer) → D90 (Coste de producir ↔ de verificar).

Varias de estas fusiones apuntan a otra dimensión que también se descartó: D50 y D123, D90 y D159, D89 con D70 y D74, D133 con D144. Ver la pregunta 1 de la sección 5.

## 3. Tensiones

| id | nombre | dimensiones | efecto en done | resoluciones vistas |
|---|---|---|---|---|
| T1 | Rigor de la evidencia ↔ coste, plazo y aprendizaje | D112 (Rigor graduado), D46 (Cuantificador), D211 (Ciclo completo), D91 (Reversible), D25 (IOC↔FOC) | Done es "probado lo suficiente para lo que está en juego"; necesita una clase de rigor por unidad y una regla de parada | DAL, ASIL, clases IEC 62304; puertas de una o dos vías; pirámide por coste; RVM; flags y canarios; crecimiento de fiabilidad |
| T2 | Alcance fijo ↔ tiempo y presupuesto fijos | D131 (Forma del contrato), D102 (Recortar), D202 (Plazo esencial), D218 (Non-goals), D201 (Interrumpible) | Hay que declarar qué variable flota; cada corte tiene que dejar algo aceptable | MoSCoW y timebox (DSDM); contratos ágiles; recorte en juegos; precio fijo con control de cambios |
| T3 | Valor temprano ↔ done completo | D25 (IOC↔FOC), D95 (Corte vertical), D73 (Producto completo), D122 (Encendido↔limpio), D5 (Done como período) | Done como escalera; alguien tiene que cerrar el último peldaño | Flags con tarea de retiro; punch list con retención (FIDIC); MVP frente a whole product |
| T4 | Formalidad verificable ↔ legibilidad para la persona | D38 (Prosa↔formal), D139 (Grounding), D141 (Evidencia legible), D37 (IKIWISI), D2 (Validado) | Done se parte en verificado y validado; el eslabón débil es la traducción | Specification by Example; teach-back; contraejemplos; prototipos; matrices de qué demuestra la evidencia |
| T5 | Elicitación liviana ↔ spec completa | D179 (Saturación), D33 (Completitud), D32 (Derivadas), D138 (Tácito), D153 (Subespecificado) | Ready = preguntar más ya no cambia lo importante; lo no preguntado queda como supuesto explícito | Saturación; preguntas ordenadas por valor de información; defaults con razón; derivados de DO-178C; EARS por fases |
| T6 | Autonomía de la IA ↔ control y consentimiento reales | D32 (Derivadas), D142 (Consentimiento), D190 (Supervisable), D225 (Roles colapsados), D212 (Tamaño revisable) | Hay que decidir qué clases de decisión exigen firma; un "aprobado" vale solo si la carga permitía juicio | Tipo 1/2; ejes de Shneiderman; niveles de Parasuraman; ADR; agrupar decisiones; AI Act art. 14 |
| T7 | Defaults que absorben complejidad ↔ preferencias auténticas | D77 (Tesler), D203 (Intención inducida), D32 (Derivadas), D138 (Tácito) | La validación incluye comprobar si la intención se elicitó o se fabricó | Alternativas con consecuencias; preguntar en abierto primero; registrar defaults; defaults reversibles |
| T8 | Criterio mecánico ↔ juicio fiel a la intención (Goodhart) | D75 (Métrica↔propósito), D43 (Prerregistro), D52 (Vara fija), D51 (Severa), D87 (Medidor) | Los gates mecánicos son necesarios pero no suficientes; ningún criterio optimizable decide solo | Tests ocultos; mutación; leer trayectorias; juez LLM calibrado; muestreo humano; auditar el ruido |
| T9 | Letra ↔ intención (quién decide cuando chocan) | D82 (Literal↔intención), D68 (JTBD), D173 (Riesgo de ambigüedad), D52 (Vara) | Regla: cumplir, desviarse y avisar, o bloquear con contraejemplo; cada desviación registrada | Inverse Reward Design; "desviarse y avisar"; catálogos de specification gaming |
| T10 | Vara fija ↔ vara corregible | D52 (Vara), D87 (Medidor), D151 (Suite podrida), D177 (Criterio que aprende) | El verde cuenta si la suite no la tocó quien implementa; un cambio de criterio es un cambio de spec | Tests de solo lectura con canal de impugnación; assert con razón trazada; ImpossibleBench; retrospectiva |
| T11 | Criterio congelado ↔ criterio que se descubre al ver | D43 (Prerregistro), D37 (IKIWISI), D12 (Línea base), D41 (Tipo E), D214 (Freezes) | Se mide contra un criterio fechado; los cambios después de ver se registran y valen menos | Prerregistro; control de cambios; checks frente a exploración; Volere; último momento responsable; Twin Peaks |
| T12 | Criterio comparable ↔ criterio que aprende (retroactividad) | D177 (Escapes), D71 (Deriva de Kano), D175 (Sesgo retrospectivo), D8 (Piso) | El done lleva la versión del criterio; hay que decidir si el cambio es retroactivo | DoD que solo endurece; ratchets con línea base; ODC; ciclo de Kano |
| T13 | Explorar ↔ comprometerse | D80 (Construir↔saber), D76 (Parada), D7 (Ready), D41 (Tipo E) | Done de experimento ≠ done de artefacto; un Ready rígido impide explorar | Cerny Method; timebox; spikes; DoR como guía |
| T14 | Independencia del verificador ↔ coste y roles colapsados | D81 (Independencia), D225 (Roles), D135 (Testimonio), D183 (Sintético) | Declarar quién verificó, con qué independencia y con qué sesgos; un mínimo según criticidad | I0-I3; IV&V; tests generados antes por otro agente; jueces de otra familia; SLSA e in-toto |
| T15 | Independencia ↔ comprensión de la intención | D81 (Independencia), D99 (Contaminado), D139 (Grounding), D78 (Sesgo) | Dos miradas con información asimétrica, que hay que fabricar a propósito | Cleanroom; IV&V; juez externo y persona solo para validar |
| T16 | Satisfacción inmediata ↔ evidencia severa | D79 (Demo↔uso), D51 (Severa), D78 (IKEA), D180 (Cierre psicológico), D198 (Reportado↔real) | Separar "lo vi y me gusta" de "está demostrado"; decir qué no demuestra la demo | Done por etapas; resumen legible de lo probado y lo no probado; evidencia reejecutable; RCT de METR |
| T17 | Transparencia ↔ confidencialidad y confianza delegada | D135 (Testimonio), D191 (Confidencial), D140 (Confiar), D58 (Raíz) | Hay que declarar la raíz de confianza: qué se vio, qué atestigua un tercero, qué es informe | in-toto, SLSA; auditor bajo NDA; clean rooms; ZK; supuestos de seL4; Nimrod |
| T18 | Soberanía del aceptante ↔ competencia para juzgar | D14 (Para quién), D28 (Acto institucional), D104 (Pisos), D141 (Legible), D8 (Piso) | Done repartido: la persona acepta lo reconocible; un piso no rebajable cubre el resto | Roles PRINCE2; DoD por capas; secure by default; confianza calibrada |
| T19 | Riesgo del productor ↔ del consumidor | D226 (α/β), D207 (Latentes), D128 (Sustancial), D200 (Disputa), D152 (Barras de error) | Done como reparto pactado de riesgo: muestra, umbral, alcance de la renuncia, subsanación | ISO 2859-1; Wald; no inferioridad; UCC 2-508 y 2-608; FIDIC DAAB |
| T20 | Quién redacta e implementa ↔ quién responde | D173 (Contra proferentem), D229 (Deformación moral), D28 (Acto), D181 (Flow-down) | Aceptar transfiere riesgo; lo que se firma tiene que estar alineado con lo que se controló | Elish; patentes frente a latentes; Dir. 2024/2853; flow-down; AI Act arts. 16 y 26 |
| T21 | Automatización entregada ↔ supervisión real | D190 (Supervisable), D189 (Dirección del fallo), D157 (Abstención), D229 (Culpa) | El done incluye las palancas de intervención y una carga de supervisión viable | AI Act art. 14; escalado por confianza; ironías de la automatización |
| T22 | Entrega ↔ autonomía de la persona | D144 (Autonomía), D148 (Teoría viva), D172 (Acabado por el usuario), D84 (Spec como fuente) | O caja negra dependiente, o el entregable incluye la teoría legible y la posibilidad de cambiarlo | Spec-as-source; software maleable; portabilidad; Naur |
| T23 | Quien acepta hoy ↔ quien vivirá con ello | D185 (Yo futuro), D184 (Sucesor), D148 (Teoría viva) | Un done sin razones registradas es frágil ante el cambio | ADR; razón junto a cada regla; teach-back; aceptación institucional |
| T24 | Evidencia por cláusula ↔ evidencia de la conjunción | D136 (Conjunción), D9 (Integrado), D26 (Emergente), D94 (Combinatoria), D98 (Presupuesto) | La tensión de origen: la unidad no puede ser la cláusula; hacen falta dos evidencias con dueños distintos | Pirámide más E2E trazados; GSN; Integrated Increment; IRL/SRL; pairwise; presupuestos en CI |
| T25 | Incremento revisable ↔ todo coherente | D212 (Tamaño), D95 (Corte vertical), D97 (Consonancia), D17 (Uniones) | Dos granularidades a la vez; ninguna prueba la otra | Walking skeleton; tracer bullets; hitos con demo integrada; INVEST |
| T26 | Incremento monótono ↔ invariantes globales | D66 (No monótono), D151 (Acumulativo), D98 (Presupuesto), D116 (Interferencia) | El done del incremento es condicional: "hice lo nuevo" y "no rompí nada" | Regresión en CI; subtipado conductual; presupuestos asignados; Nexus |
| T27 | Reproducibilidad hermética ↔ fidelidad al mundo real | D48 (Estadístico), D49 (Dobles), D135 (Reproducible), D124 (Deriva) | Dos capas: lo que el artefacto es (reproducible) y cómo se comporta (estadística fechada) | Tests herméticos frente a no herméticos; record/replay; canario; pass^k con barras |
| T28 | Rapidez ↔ validez de la señal | D232 (Latencia), D3 (Outcome), D228 (Atribuible), D79 (Demo) | El done de valor es provisional y se confirma o se revoca con la señal tardía | OEC; holdouts; feedback diferido; revisión de beneficios |
| T29 | Cierre cierto ↔ validez vigente | D118 (Estado), D114 (SPIs), D145 (Caducidad), D207 (Revocable), D5 (Período) | Un acto fechado más una afirmación vigente con indicadores; qué la revoca y quién paga la vigilancia | FIDIC; UCC 2-608; UL 4600; fitness functions; SLOs; GitOps; estado del arte |
| T30 | Evidencia fresca ↔ evidencia barata | D145 (Caducidad), D55 (Por lote), D211 (Ciclo), D224 (Latente), D215 (Testabilidad) | Parte del done siempre descansa en evidencia vencida, y eso se declara | Pipelines por niveles; selección de regresión; DiRT; ejecución en paralelo |
| T31 | Fijar el entorno ↔ actualizarlo | D24 (Identidad), D124 (Deriva), D195 (Upstream), D209 (SoS) | Cada actualización reabre parte del done; hace falta una política declarada | Lockfiles; builds reproducibles; Dependabot; LTS; upstream first; SBOM |
| T32 | Estabilidad prometida ↔ evolución | D118 (Estado), D54 (Hyrum), D103 (Madurez), D109 (Ediciones), D217 (Preaviso) | Done es qué no cambiará, cuánto tiempo y con qué preaviso | SemVer; Go 1; ediciones de Rust; deprecación en Kubernetes; aleatorizar lo no especificado; Crater |
| T33 | Regenerar desde la spec ↔ conservar lo aceptado | D83 (Regeneración), D84 (Objeto del done), D20 (Generador), D153 (Subespecificado), D221 (Precedente) | Declarar de qué se predica done; lo aceptado sube a la spec o se declara libre | Translation validation frente a CompCert; DO-330; fijar modelo y semilla; golden master; OpenSpec |
| T34 | Agilidad del cambio ↔ reapertura de la aceptación | D115 (PCCP), D210 (Urgente), D227 (Runtime), D13 (Tolerancia) | Done como envolvente; fuera de ella se reabre; la vía urgente deja deuda | PCCP de la FDA; tipos de cambio ITIL; tolerancias; waivers; RELAX |
| T35 | Capacidad estable ↔ feature cambiante | D221 (Precedente), D172 (Plataforma), D149 (Fase), D54 (Hyrum) | Una capacidad está done solo de forma provisional, hasta sobrevivir a varias features | Pace layering; capas de Gartner; regla de tres |
| T36 | Reversibilidad ↔ limpieza y compromiso | D91 (Reversible), D122 (Limpio), D146 (Transición), D214 (Freezes) | Dos done separados en el tiempo; si el segundo no es explícito, no ocurre | Expand/contract; flags con expiración; ventanas de deprecación; Knight Capital |
| T37 | Agregar barato ↔ quitar caro | D23 (Retirada), D218 (Non-goals), D10 (Gold plating), D176 (Cancelar) | Cada done trae una obligación futura; sin done de retirada, el sistema solo engorda | Deprecación a cargo de quien depreca; non-goals; recortar sin costuras |
| T38 | Software situado ↔ generalidad y pisos | D204 (n=1), D164 (Accesibilidad), D169 (i18n), D104 (Pisos), D178 (Perfil) | Clasificar antes; un perfil con exclusiones; escalar después es rehacer | WCAG A/AA/AAA; i18n frente a l10n; tailoring; AI Act por riesgo |
| T39 | Diseñar para durar ↔ diseñar para tirar | D220 (Vida útil), D80 (Experimento), D204 (Situado), D149 (Fase) | El perfil depende de la vida declarada; el done caduca si cambia el uso | Arquitectura de sacrificio; EN 1990; puertas de promoción |

## 4. Las dimensiones que más pesan para definir la unidad que se entrega y se acepta

1. **D1 (Nivel de aceptación) y D212 (Tamaño de la unidad)**. Entre las dos delimitan el "algo". D1 da el piso: la unidad es el nivel más bajo con criterio de aceptación propio, porque por debajo solo hay tareas. D212 da el techo práctico: tiene que caber en una revisión con atención. Si no hay ningún nivel que cumpla las dos cosas, la unidad no es una sola: se parte en una aceptación técnica por pieza y una de valor por conjunto (T25 (Incremento revisable ↔ todo coherente)).

2. **D9 (Done local ↔ integrado) y D136 (Evidencia de la conjunción)**. Explican el problema de origen: cumplir cada MUST no basta. Si la unidad es la cláusula, por construcción no hay dueño del pegamento ni evidencia del todo. La unidad tiene que llevar su propia evidencia de punta a punta (T24 (Evidencia por cláusula ↔ de la conjunción)).

3. **D2 (Verificado ↔ validado)**. En SDD con IA, el done verificado es casi gratis y autorreferente. La unidad tiene sentido solo si es lo bastante concreta para que la persona la valide reconociéndola (D37 (Criterio reconocido al ver)), con evidencia en su idioma (D141 (Evidencia legible)). Esto la diferencia de una unidad de trabajo.

4. **D30 (Condicionado a supuestos), D218 (Frontera negativa) y D32 (Decidido por la IA)**. Juntas hacen que el done se pueda declarar con honestidad. Sin supuestos explícitos, sin non-goals y sin inventario de decisiones derivadas, el silencio de la spec lo llenan los defaults de la IA y "no hace X" no se puede clasificar como decisión ni como defecto.

5. **D29 (Imperfección dispuesta)**. Toda unidad real se acepta con desviaciones. Lo que define el done no es la perfección, sino que cada imperfección tenga disposición, dueño y razón. Sin eso, la IA reescribe la spec para que coincida con lo que hizo, o bloquea sin fin.

6. **D178 (Perfil de done declarado) y D112 (Rigor graduado)**. Ninguna unidad puede satisfacer los 217 ejes. La unidad necesita una clase de criticidad y un perfil con exclusiones justificadas. Si no, cada parte supone un done distinto y la IA aplica por defecto el rigor barato.

7. **D84 (Objeto del done) y D83 (Invariante bajo regeneración)**. Hay que decidir si la unidad es un artefacto revisado o un par spec+modelo que se puede regenerar. Esa elección cambia la naturaleza de la evidencia (por ejemplar o por proceso, D20 (Confiar en el generador ↔ verificar cada salida)) y qué parte de lo aceptado tiene que subir a la spec (T33 (Regenerar ↔ conservar lo aceptado)).

8. **D222 (Normas consultadas ↔ aplicables)**. Es propia del método descrito, donde la IA elige las normas de cada "algo". El done de la unidad se calcula contra una selección. Sin una declaración de aplicabilidad verificada aparte, es un done "módulo un filtro invisible" (D58 (Base de confianza)).

9. **D81 (Verificación independiente) y D225 (Roles colapsados)**. Con una persona y una IA no queda ninguna separación de funciones. La unidad aceptable tiene que registrar quién verificó y con qué independencia. Si no lo hace, su done es testimonio (D135 (Testimonio ↔ evidencia reproducible)).

10. **D118 (Done como estado) y D5 (Done como período)**. La unidad no se cierra en un instante. Lleva una escalera de estados y condiciones de vigencia (qué evento la reabre). Sin eso, "aceptado" afirma algo del pasado.

En conjunto, la unidad que falta se puede caracterizar así: el nivel más bajo del árbol de producto que la persona puede reconocer y validar de punta a punta. Cabe en una revisión atenta. Lleva su perfil de done, sus supuestos, sus non-goals, sus decisiones derivadas y sus imperfecciones dispuestas, y tiene evidencia del todo cuya independencia está declarada y que tiene condiciones de caducidad.

## 5. Preguntas abiertas

1. Hay fusiones circulares en la verificación: D50 (Antes del despliegue ↔ en producción) y D123 (Laboratorio ↔ campo), D90 (Coste de producir ↔ de verificar) y D159 (Verificabilidad de la tarea), D89 (Percibido ↔ medido) con D70 (Inherente ↔ percibida) y D74 (Declarado ↔ observado), D133 (Dependencia ↔ salida) con D144 (Autonomía de la persona). ¿Qué eje sobrevive en cada caso? Hoy "laboratorio ↔ campo" y "coste de verificar" no tienen ninguna dimensión propia.
2. Si D1 (Nivel de aceptación) y D212 (Tamaño de la unidad) no se cruzan, ¿la unidad es una o son dos (pieza técnica y corte de valor)? ¿Quién acepta cada una?
3. ¿Puede una IA asignar la clase de criticidad (D112 (Rigor graduado)) y el perfil de done (D178 (Perfil declarado)) de una unidad, si esa clasificación es en sí una decisión de riesgo que alguien tiene que aceptar?
4. ¿Con qué evidencia se demuestra que la formalización dice lo mismo que la prosa aprobada (D38 (Prosa ↔ formalización))? ¿Existe una evidencia puente que cuente para las dos partes?
5. En spec-as-source (D84 (Objeto del done)), ¿qué parte de lo observado y aceptado por la persona debe subir a la spec y qué parte puede quedar libre a propósito (D61 (Libertad del implementador))?
6. ¿Qué sustituye a la separación de funciones cuando solo hay una persona y una IA (D225 (Roles colapsados))? ¿Basta otra IA de otra familia, dado que las versiones independientes fallan de forma correlacionada (D81 (Verificación independiente))?
7. ¿Es aceptable una persona sintética (D183 (Aceptante sintético)) para alguna parte de la validación, o cualquier uso convierte el veredicto en autorreferente?
8. ¿Cómo se calcula el recall de la selección de normas (D222 (Normas consultadas ↔ aplicables)) sin repetir el mismo sesgo que hizo la selección?
9. Cuando el DoD se endurece, ¿lo ya aceptado vuelve a medirse con la vara nueva (T12 (Retroactividad del DoD endurecido))? ¿Con qué regla?
10. Si la persona no puede descubrir casi ningún defecto (D207 (Defectos latentes)), ¿qué transfiere realmente su "sí", y quién responde (D229 (Deformación moral))?
11. ¿Cuál es la regla de combinación entre ejes cuando chocan (D206 (Conflicto entre ejes))? ¿Orden lexicográfico fijo por familia o arbitraje caso a caso?
12. ¿Qué parte del done de un software situado (D204 (Software situado)) caduca cuando crece su audiencia, y qué señal lo detecta?
13. Para efectos diferidos (D232 (Latencia de la señal)), ¿qué indicador adelantado basta para un done provisional? ¿Cuándo se reabre?
14. ¿Puede la IA proponer lo que encanta (D39 (Kano)) o disolver el problema (D199 (Resolver ↔ disolver)) sin violar el techo del alcance (D10 (Gold plating))?

## 6. Fuentes principales

- AXELOS, *Managing Successful Projects with PRINCE2* (2017); PMI, *PMBOK Guide* 6.ª ed. y *Practice Standard for WBS*; Schwaber y Sutherland, *The Scrum Guide*; *Nexus Guide*.
- ISO/IEC/IEEE 15288:2023, 29148:2018, 12207:2017; ISO 9000:2015; NASA/SP-2016-6105 Rev 2; SEBoK; Katz y Ryan (eds.), *INCOSE Needs and Requirements Manual* (2024).
- RTCA DO-178C y DO-330; ISO 26262:2018; IEC 62304; ISO 14971:2019; ISO 21448:2022 (SOTIF); UL 4600; IEEE 1012-2016; FDA (2024), PCCP.
- Zave y Jackson (1997), *Four Dark Corners of RE*; Gotel y Finkelstein (1994); Nuseibeh, Easterbrook y Russo (2000); Letier y van Lamsweerde (2004); Mavin et al. (2009), EARS; Boehm (2000), IKIWISI; Robertson y Robertson (Volere).
- Barr et al. (2015), *The Oracle Problem*; Mayo (2018), *Severe Testing*; Claessen y Hughes (2000), QuickCheck; Yang et al. (2011), Csmith; Leroy (2009), CompCert; Pnueli et al. (1998), Translation Validation; Alpern y Schneider (1985); Clarkson y Schneider (2010).
- Kelly (1998) y SCSC-141C (GSN); Bloomfield y Rushby (Assurance 2.0); Haddon-Cave (2009), Nimrod; Leveson (2011).
- Lehman (1980); Naur (1985); Hyrum's Law; Winters, Manshreck y Wright (2020), *Software Engineering at Google*; Google SRE Book y Workbook; Hodgson (2017), Feature Toggles; Sato (2014), ParallelChange.
- Kano et al. (1984); Rittel y Webber (1973); Rodden et al. (2010), HEART; Cagan, *Inspired*; Moore (1991); Ries (2011); Hunicke et al. (2004), MDA.
- Krakovna et al. (2020), *Specification gaming*; METR (2025), reward hacking y evaluación holística; Zhong et al. (2025), ImpossibleBench; Zheng et al. (2023) y Panickssery et al. (2024), sesgos de los jueces LLM; Shankar et al. (2024), *Who Validates the Validators?*; D'Amour et al. (2022), *Underspecification*; Miller (2024), *Error Bars*; Sculley et al. (2015).
- Böckeler (2025), herramientas SDD (martinfowler.com); Kiro docs; GitHub Spec Kit; OpenSpec; Thoughtworks Radar.
- Elish (2019), *Moral Crumple Zones*; Lee y See (2004); Norton, Mochon y Ariely (2012), efecto IKEA; Sharma et al. (2023), sycophancy; Clark y Brennan (1991); Polanyi (1966).
- UCC §2-601, 2-606, 2-608; *Jacob & Youngs v. Kent* (1921); FIDIC Red Book (2017); Reglamento (UE) 2024/1689 (AI Act), 2016/679 (RGPD), 2024/2847 (CRA); Directiva (UE) 2024/2853.