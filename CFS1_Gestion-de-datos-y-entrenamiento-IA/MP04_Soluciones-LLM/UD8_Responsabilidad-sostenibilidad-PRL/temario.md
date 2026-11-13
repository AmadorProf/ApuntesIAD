# UD8 · Responsabilidad profesional, sostenibilidad y PRL en soluciones LLM

---

## 1. Introducción

El desarrollo y despliegue de soluciones basadas en modelos de lenguaje de gran escala (LLM) ya no es una actividad confinada a laboratorios de investigación. Es una práctica profesional que se ejerce en empresas, administraciones públicas, consultoras y startups. Esta normalización trae consigo una consecuencia inevitable: el profesional que diseña, entrena, ajusta o despliega un LLM adquiere responsabilidades que van mucho más allá de conseguir que el modelo genere texto coherente.

Tres dimensiones articulan esa responsabilidad. La primera es técnica: las decisiones de arquitectura, cuantización, selección de datos y configuración de inferencia tienen consecuencias directas sobre la calidad, el coste y el impacto ambiental del sistema. La segunda es ética: los outputs de un LLM pueden informar decisiones médicas, financieras o jurídicas, y el profesional que lo pone en producción es corresponsable de las consecuencias. La tercera es legal: el marco normativo europeo —con el EU AI Act como piedra angular— y las legislaciones nacionales sobre propiedad intelectual, protección de datos y salud laboral crean obligaciones concretas que no pueden ignorarse.

Esta unidad didáctica aborda las tres dimensiones de forma integrada. No se trata de un repaso superficial de conceptos abstractos; el objetivo es que al terminar el módulo el alumno sea capaz de tomar decisiones técnicas informadas que reduzcan la huella ambiental de sus sistemas, de identificar los riesgos legales antes de poner un modelo en producción, y de aplicar protocolos de prevención de riesgos laborales adaptados al trabajo cotidiano con IA generativa.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el alumno será capaz de:

- Cuantificar la huella de carbono asociada al entrenamiento y la inferencia de LLMs, y comparar distintas estrategias técnicas para reducirla.
- Aplicar técnicas de optimización —quantización, speculative decoding, prompt caching— con criterio tanto de rendimiento como de sostenibilidad.
- Identificar los principales riesgos legales vinculados al copyright de outputs generados y a la responsabilidad por contenido incorrecto o dañino.
- Interpretar las obligaciones que el EU AI Act impone a los proveedores y desplegadores de modelos de propósito general (GPAI).
- Seleccionar licencias de modelos open-weight adecuadas al caso de uso y detectar restricciones de uso comercial.
- Reconocer los riesgos laborales específicos del trabajo prolongado con IA generativa y conocer la normativa española aplicable.
- Aplicar los principios del ACM Code of Ethics 2018 y del IEEE Ethically Aligned Design a situaciones profesionales concretas.

---

## 3. Impacto ambiental de los LLMs

### 3.1 Huella de carbono del entrenamiento

El entrenamiento de modelos de lenguaje de gran escala es una de las operaciones computacionales más intensivas en energía que puede ejecutar una organización privada. El estudio de referencia de Strubell et al. (2019) estimó que entrenar un modelo Transformer de tamaño medio con búsqueda de hiperparámetros podía emitir el equivalente a cinco veces las emisiones de CO2 de un automóvil durante toda su vida útil. Los modelos posteriores agravan el problema de forma exponencial.

GPT-3, con 175.000 millones de parámetros, generó aproximadamente 552 toneladas de CO2 equivalente durante su entrenamiento, según estimaciones derivadas del consumo energético declarado por OpenAI. Para contextualizar esa cifra: un vuelo de larga distancia de ida y vuelta entre Madrid y Nueva York emite alrededor de 1,5 tCO2e por pasajero, lo que significa que entrenar GPT-3 equivale a las emisiones de unos 370 vuelos transatlánticos.

En el caso de Llama 3 (Meta, 2024), las estimaciones precisas no han sido publicadas oficialmente, pero investigadores independientes calculan que el modelo de 70.000 millones de parámetros pudo generar entre 100 y 300 tCO2e durante su entrenamiento, dependiendo del mix energético de los centros de datos utilizados. La mejora respecto a GPT-3 refleja en parte una mayor eficiencia de hardware (GPU H100 frente a V100) y en parte el uso de energía más limpia por parte de Meta en sus instalaciones.

### 3.2 Huella de la inferencia

El entrenamiento ocurre una sola vez, pero la inferencia ocurre millones de veces al día. Esta asimetría hace que la huella acumulada de la inferencia supere con frecuencia la del entrenamiento en sistemas con alto tráfico.

Una sola query a un modelo como GPT-4 consume entre 0,001 y 0,01 kWh, dependiendo de la longitud del contexto y el número de tokens generados. Una búsqueda web convencional consume aproximadamente 0,0003 kWh. La diferencia es de un orden de magnitud: una consulta a un LLM grande puede consumir entre 3 y 30 veces más energía que una búsqueda en Google. Con millones de usuarios diarios, ese diferencial se convierte en una masa crítica de consumo energético.

Sin embargo, la comparación no es completamente justa: una respuesta de un LLM suele sustituir a varias búsquedas sucesivas y puede requerir menor esfuerzo cognitivo de procesamiento por parte del usuario. La evaluación del impacto neto debe tener en cuenta el valor generado, no solo el consumo bruto.

### 3.3 Estrategias de sostenibilidad en inferencia

**Caching de respuestas.** Si múltiples usuarios realizan consultas idénticas o muy similares, cachear la respuesta evita recalcularla. Esto es especialmente efectivo en aplicaciones con preguntas frecuentes predecibles. La API de Anthropic implementa prompt caching de forma nativa: cuando el prefijo de un prompt supera un umbral de tokens y se reutiliza en llamadas sucesivas, se procesa una sola vez y se almacena el estado interno del modelo, reduciendo tanto la latencia como el coste computacional.

**Quantización.** Reducir la precisión numérica de los pesos del modelo de float32 a INT8 o INT4 disminuye el consumo de memoria y acelera la inferencia sin pérdidas significativas de calidad en la mayoría de tareas. Se describe en detalle en la sección 4.

**Elección del modelo mínimo suficiente.** Usar un modelo de 7.000 millones de parámetros para una tarea que no requiere el razonamiento de un modelo de 70.000 millones es la decisión de sostenibilidad más eficaz disponible. La regla práctica es: evaluar primero el modelo más pequeño; escalar solo si los benchmarks de calidad lo exigen.

**Elección del proveedor cloud.** AWS, Google Cloud Platform y Microsoft Azure tienen compromisos climáticos públicos, pero con diferencias relevantes. GCP opera con compensación de carbono al 100% desde 2007 y tiene como objetivo el 24/7 de energía libre de carbono para 2030. AWS se comprometió a operar con energía 100% renovable para 2025 y tiene objetivos de net-zero para 2040. Azure se comprometió a ser carbono negativo para 2030. La elección de región también importa: ejecutar cargas de trabajo en us-east-1 (Virginia, con alto porcentaje de energía no renovable) tiene un impacto diferente a ejecutarlas en eu-north-1 (Estocolmo, con energía principalmente hidroeléctrica).

### 3.4 Medición con CodeCarbon

CodeCarbon es una librería Python de código abierto que permite medir el consumo energético y las emisiones de CO2 equivalente de cualquier proceso computacional. Su integración en pipelines de inferencia es directa:

```python
from codecarbon import EmissionsTracker

tracker = EmissionsTracker(project_name="mi_llm_produccion")
tracker.start()
# bloque de inferencia
tracker.stop()
```

Al finalizar, genera un informe con kilowatios-hora consumidos, emisiones estimadas en gramos de CO2e, y el mix energético estimado del país o región donde se ejecuta. Esta herramienta permite comparar distintas configuraciones de modelo y proveedor con datos empíricos, convirtiendo las decisiones de sostenibilidad en decisiones técnicas basadas en evidencia.

---

## 4. Optimización para eficiencia

### 4.1 Quantización: INT8, INT4 y GGUF

La quantización es el proceso de representar los pesos de un modelo con menor precisión numérica. Los modelos se entrenan habitualmente en float16 o bfloat16; la quantización post-entrenamiento los convierte a INT8 (8 bits por peso) o INT4 (4 bits por peso).

El impacto sobre el consumo es directo: un modelo en INT4 ocupa aproximadamente una cuarta parte de la memoria que el mismo modelo en float16, y puede ejecutarse en hardware más modesto. La degradación de calidad en INT8 es imperceptible en la mayoría de tareas; en INT4 existe una degradación medible pero que muchas aplicaciones pueden tolerar.

El formato GGUF, utilizado por llama.cpp, es el estándar de facto para inferencia cuantizada en CPU y hardware de consumo. Permite ejecutar modelos de 7.000 a 70.000 millones de parámetros en laptops con RAM suficiente, eliminando la necesidad de GPU dedicada. Esto tiene implicaciones de sostenibilidad importantes: la inferencia local en hardware existente puede tener una huella menor que la inferencia en cloud si el hardware local usa energía renovable o si el modelo es suficientemente pequeño.

### 4.2 Speculative Decoding

La generación autoregresiva de tokens es inherentemente secuencial: cada token depende de todos los anteriores. Speculative decoding rompe parcialmente esta restricción usando un modelo pequeño y rápido (el "borrador") para generar varios tokens en paralelo, y un modelo grande (el "verificador") para aceptar o rechazar ese borrador en un solo paso de forward.

El resultado práctico es una aceleración de 2x a 4x en latencia percibida sin pérdida de calidad: el modelo grande verifica pero no genera, y la distribución de probabilidad del output es matemáticamente equivalente a la generación estándar. La eficiencia energética mejora porque el modelo grande ejecuta menos pasos de forward, que son los más costosos.

### 4.3 KV Cache y Continuous Batching

El KV cache (cache de claves y valores de atención) evita recalcular las representaciones internas de los tokens del contexto en cada paso de generación. Sin él, cada token generado requeriría procesar de nuevo todo el contexto previo. Con él, solo se procesa el token nuevo. Es una optimización fundamental que todos los frameworks modernos implementan por defecto.

El continuous batching permite que un servidor de inferencia procese múltiples peticiones simultáneas de forma dinámica, añadiendo nuevas peticiones al batch en cuanto se liberan slots, en lugar de esperar a que todo un batch termine. Esto maximiza la utilización de la GPU y reduce el coste por token en despliegues de alto tráfico.

### 4.4 Prompt Caching (Anthropic API)

La API de Anthropic implementa una forma de caching a nivel de prefijo de prompt que va más allá del caching de respuestas completas. Cuando una llamada incluye un prefijo largo que ya fue procesado en una llamada anterior reciente (documentos de contexto, instrucciones de sistema extensas), el modelo reutiliza el estado interno calculado para ese prefijo, reduciendo el coste de procesamiento entre un 80% y un 90% para los tokens cacheados. Esta característica es especialmente valiosa en aplicaciones RAG donde el mismo documento de contexto se usa en múltiples consultas.

---

## 5. Responsabilidad legal en outputs de IA generativa

### 5.1 Propiedad intelectual y copyright en outputs generados

La pregunta de si los outputs de un LLM son protegibles por copyright es una de las más debatidas en el derecho de la propiedad intelectual contemporáneo. La posición de la U.S. Copyright Office, expresada en su informe "Copyright and Artificial Intelligence" (2024), es que el copyright no protege obras generadas de forma autónoma por una IA sin contribución creativa humana suficiente. El prompt por sí solo generalmente no constituye esa contribución; la selección, edición y arreglo significativo del output por parte de un humano puede sí constituirla.

En la Unión Europea, la Directiva de Derechos de Autor (2019/790) no aborda directamente los outputs de IA, pero la interpretación dominante en la doctrina es similar: se requiere una "elección creativa libre y original" de una persona física para que exista obra protegible.

Las implicaciones prácticas para el profesional son dos. Primera: los outputs de un LLM entregados a un cliente sin intervención editorial significativa pueden carecer de protección por copyright, lo que debe comunicarse si es relevante para el negocio del cliente. Segunda: el profesional no puede reclamar autoría sobre outputs que no reflejan sus elecciones creativas.

### 5.2 Casos legales relevantes

**Getty Images vs. Stability AI (2023, en curso).** Getty Images demandó a Stability AI por entrenar su modelo de imagen Stable Diffusion usando millones de imágenes de su catálogo sin licencia. El caso plantea la cuestión central de si el entrenamiento de IA sobre contenido protegido constituye infracción de copyright o se acoge a la doctrina del fair use. La resolución del caso establecerá precedente para los LLMs entrenados sobre texto.

**The New York Times vs. OpenAI y Microsoft (2023, en curso).** El NYT demandó alegando que GPT-4 puede reproducir artículos completos de su archivo casi literalmente cuando se le pide, lo que constituiría infracción directa. OpenAI argumenta que el entrenamiento cae bajo fair use y que la memorización exacta es un comportamiento anómalo que están corrigiendo. Este caso es el más relevante para los profesionales que trabajan con LLMs de texto.

La lección práctica de ambos casos es que el profesional debe ser cauteloso al desplegar modelos que puedan reproducir contenido protegido, implementar filtros de salida donde sea posible, y documentar las salvaguardas adoptadas.

### 5.3 Responsabilidad por contenido incorrecto

Un LLM puede generar información médica incorrecta, asesoramiento jurídico erróneo o datos financieros falsos con igual fluidez que información correcta. El fenómeno de las "alucinaciones" es estructural, no un bug que se vaya a eliminar completamente. Esto crea riesgos de responsabilidad para quien despliega el sistema.

En ausencia de legislación específica, se aplica la responsabilidad general por productos y servicios defectuosos. Si una empresa despliega un chatbot de salud que recomienda una dosificación incorrecta y un paciente sufre daño, la empresa desplegadora puede ser responsable bajo la normativa de protección del consumidor, con independencia de que el error lo haya generado el modelo. La mitigación pasa por disclaimers claros, sistemas de verificación humana para dominios de alto riesgo, y limitación explícita del alcance del sistema.

### 5.4 EU AI Act: obligaciones para GPAI

El Reglamento (UE) 2024/1689 de Inteligencia Artificial, en vigor desde agosto de 2024, introduce la categoría de "modelos de IA de propósito general" (GPAI). Los modelos entrenados con más de 10^25 operaciones de punto flotante se consideran de capacidades sistémicas y están sujetos a obligaciones adicionales.

Las obligaciones aplicables a todos los proveedores de GPAI incluyen: publicar una política de uso aceptable, mantener documentación técnica, respetar la normativa de copyright de la UE en los datos de entrenamiento, y publicar un resumen suficientemente detallado de los datos usados en el entrenamiento. Para modelos con riesgo sistémico, se añaden evaluaciones de modelo, notificación de incidentes a la Comisión Europea, y medidas de ciberseguridad.

Para los desplegadores (organizaciones que integran un modelo GPAI en sus productos), el EU AI Act impone transparencia obligatoria ante los usuarios finales: cuando un usuario interactúa con un sistema de IA, debe saberlo. Los sistemas de IA generativa que producen contenido audiovisual sintético están obligados a marcarlo como tal (marca de agua o divulgación explícita), salvo en casos de uso artístico o legalmente autorizado.

---

## 6. Gestión de derechos de autor y licencias de modelos

### 6.1 Panorama de licencias open-weight

La distinción entre "open source" y "open weight" es fundamental. Un modelo open-weight publica los pesos del modelo pero puede imponer restricciones de uso mediante licencia; un modelo verdaderamente open source publicaría también los datos de entrenamiento y el código de entrenamiento completo, lo que es extremadamente raro.

**Llama 3 Community License (Meta).** Permite uso comercial con restricciones: organizaciones con más de 700 millones de usuarios activos mensuales necesitan una licencia separada de Meta. Prohíbe usar el modelo para entrenar otros modelos sin permiso explícito. No es compatible con licencias OSI (Open Source Initiative), por lo que Llama 3 no es software libre en sentido técnico.

**Apache 2.0.** Licencia permisiva que permite uso comercial, modificación y redistribución sin restricciones significativas, siempre que se mantenga el aviso de licencia y atribución. Modelos como Mistral 7B v0.1 se distribuyeron bajo Apache 2.0. Es la licencia más amigable para uso empresarial sin sorpresas legales.

**MIT.** Aún más permisiva que Apache 2.0, sin cláusula de patentes. Menos común en modelos de lenguaje grandes por la falta de protección de patentes para el proveedor original.

### 6.2 Datos de entrenamiento y copyright: el caso Copilot

GitHub Copilot (basado en Codex y posteriormente en GPT-4) fue desarrollado entrenando el modelo sobre código público de GitHub, incluyendo repositorios con licencias restrictivas como GPL. Varios desarrolladores demandaron alegando que Copilot reproduce fragmentos de su código sin atribución, violando las condiciones de la licencia.

Este caso es representativo de un problema estructural: los LLMs pueden memorizar fragmentos de sus datos de entrenamiento y reproducirlos en contextos donde esa reproducción viola los términos de la licencia original. La mitigación técnica incluye filtros de detección de memorización y sistemas de atribución automática, pero ninguna solución es perfecta a día de hoy.

### 6.3 Buenas prácticas de atribución

Cuando un sistema LLM se despliega para generar contenido que podría incluir material de terceros, las buenas prácticas incluyen: documentar los datos de entrenamiento y sus licencias, implementar filtros de similitud para detectar reproducción literal, incluir mecanismos de reporte para que usuarios identifiquen posibles infracciones, y no reclamar derechos sobre outputs que puedan incorporar material ajeno.

---

## 7. Salud laboral y PRL en el trabajo con IA generativa

### 7.1 Fatiga cognitiva por revisión de outputs

El trabajo con LLMs en producción implica con frecuencia revisar grandes volúmenes de outputs generados para verificar su calidad, detectar errores y evaluar alucinaciones. Este tipo de revisión —que combina lectura rápida, juicio crítico continuo y toma de decisiones repetida— genera una forma específica de fatiga cognitiva que difiere de la fatiga de la lectura convencional.

Los síntomas incluyen reducción de la capacidad de detección de errores a lo largo de sesiones prolongadas, embotamiento crítico (tendencia a aceptar outputs sin evaluación profunda tras períodos extensos de revisión), y dificultad para mantener criterios consistentes de calidad. La mitigación pasa por establecer límites temporales para sesiones de revisión, implementar rotaciones de tarea, y diseñar herramientas de revisión que reduzcan la carga cognitiva mediante pre-filtrado automatizado.

### 7.2 Síndrome del evaluador de contenido (content moderator burnout)

Los trabajadores que moderan contenido generado por IA, o que participan en procesos de RLHF (Reinforcement Learning from Human Feedback) evaluando outputs potencialmente dañinos, están expuestos a un riesgo específico de daño psicológico. La investigación sobre moderadores de contenido en redes sociales —que es el antecedente más documentado— muestra tasas elevadas de trastorno de estrés postraumático, ansiedad y depresión.

En el contexto de RLHF, los anotadores humanos que clasifican y corrigen outputs de modelos de lenguaje pueden estar expuestos a contenido violento, sexualmente explícito o ideológicamente extremo generado por el modelo durante fases tempranas del entrenamiento. Empresas como OpenAI han sido objeto de atención pública por las condiciones de trabajo de los anotadores subcontratados en países de bajos costes laborales.

Las buenas prácticas incluyen: evaluación previa del tipo de contenido al que estará expuesto el trabajador, implementación de protocolos de "corte" que permitan detener la sesión sin consecuencias cuando el contenido resulta difícil, acceso a apoyo psicológico profesional, rotación entre tipos de tareas, y límites estrictos de exposición diaria a contenido dañino.

### 7.3 Marco normativo español aplicable

**Ley 31/1995 de Prevención de Riesgos Laborales.** Esta ley establece la obligación del empresario de evaluar todos los riesgos para la seguridad y salud de los trabajadores, incluidos los riesgos psicosociales. El trabajo prolongado con IA generativa —en sus dimensiones de revisión de outputs, interacción continua con sistemas de IA, y exposición a contenido potencialmente perturbador— debe ser objeto de evaluación de riesgos bajo este marco. La evaluación debe contemplar la carga mental, la monotonía, la presión temporal y la exposición a contenido adverso.

**LOPDGDD, artículo 88: derecho a la desconexión digital.** La Ley Orgánica de Protección de Datos y Garantía de los Derechos Digitales reconoce el derecho de los trabajadores a no responder comunicaciones digitales fuera del horario laboral. En entornos donde los sistemas de IA generativa están integrados en los flujos de trabajo y pueden generar demandas de revisión fuera del horario, este derecho adquiere especial relevancia. Las empresas deben implementar políticas internas que garanticen su ejercicio efectivo.

El cumplimiento de ambas normativas en entornos de trabajo con IA requiere que los departamentos de Recursos Humanos y PRL actualicen sus evaluaciones de riesgos para incluir los factores específicos del trabajo con IA, algo que muchas organizaciones todavía no han hecho.

---

## 8. Marco ético profesional

### 8.1 Principios deontológicos del profesional de IA

**Veracidad.** El profesional de IA tiene la obligación de comunicar con honestidad las capacidades y limitaciones de los sistemas que desarrolla o despliega. Exagerar la precisión de un modelo ante un cliente, ocultar las tasas de alucinación o presentar benchmarks seleccionados para favorecer al sistema propio son violaciones de este principio.

**No maleficencia.** Antes de poner un sistema en producción, el profesional debe evaluar razonablemente los daños que podría causar. Esto incluye daños directos (outputs incorrectos en dominios de alto riesgo), daños indirectos (amplificación de sesgos presentes en los datos de entrenamiento) y daños sistémicos (concentración de poder informacional, desplazamiento laboral sin mitigación).

**Transparencia.** Los usuarios de sistemas de IA tienen derecho a saber que están interactuando con un sistema automatizado. La impersonación —diseñar chatbots para que nieguen ser IA cuando se les pregunta directamente— viola este principio y, en la UE, contraviene el EU AI Act.

### 8.2 Gestión de conflictos de interés

El profesional de IA puede encontrarse en situaciones donde los incentivos económicos del cliente o empleador entran en conflicto con el bienestar de los usuarios o la sociedad. Ejemplos frecuentes: se le pide implementar dark patterns que maximicen el tiempo de interacción con el sistema a costa del bienestar del usuario; se le pide desplegar un sistema de evaluación automatizada de candidatos sin auditoría de sesgos; se le pide generar contenido persuasivo sin divulgación de su origen artificial.

La gestión ética de estos conflictos no consiste en la obediencia automática ni en la negativa automática, sino en elevar la cuestión a los niveles de decisión apropiados, documentar la discrepancia, y en casos extremos ejercer el derecho a la negativa fundamentada.

### 8.3 Negativa a desarrollar sistemas dañinos

El profesional tiene derecho —y en algunos casos obligación— a negarse a desarrollar sistemas cuyo propósito primario sea causar daño: sistemas de vigilancia masiva sin base legal, herramientas de desinformación automatizada, sistemas de manipulación psicológica. Este derecho no es absoluto ni gratuito en términos profesionales, pero está reconocido en los marcos deontológicos de la profesión.

### 8.4 ACM Code of Ethics 2018

El ACM Code of Ethics and Professional Conduct (2018) es el marco deontológico de referencia para profesionales de la computación. Sus principios generales más relevantes para el trabajo con LLMs son:

- **1.1 Contribuir al bien de la sociedad y el bienestar humano.** Los sistemas de IA deben diseñarse para beneficiar a los afectados por ellos, no solo a quienes los pagan.
- **1.2 Evitar el daño.** Requiere identificar los posibles daños antes del despliegue y adoptar medidas de mitigación.
- **1.3 Ser honesto y digno de confianza.** Prohíbe la deshonestidad en la comunicación de capacidades del sistema.
- **1.6 Respetar la privacidad.** Especialmente relevante cuando los LLMs procesan datos personales.
- **2.5 Dar evaluaciones comprensivas y honestas.** El profesional no debe avalar sistemas que no ha evaluado adecuadamente.

### 8.5 IEEE Ethically Aligned Design (EAD)

El IEEE Ethically Aligned Design es un documento marco que propone principios y recomendaciones para el diseño ético de sistemas autónomos e inteligentes. Sus cinco principios cardinales son: derechos humanos, bienestar, responsabilidad, transparencia y educación y concienciación. Para los LLMs, la aplicación más concreta del EAD es el principio de responsabilidad: debe existir siempre un ser humano identificable que pueda rendir cuentas por las decisiones del sistema, y los sistemas no deben diseñarse de forma que difuminen deliberadamente esa cadena de responsabilidad.

---

## 9. Actividades prácticas

### Actividad 1: Auditoría de huella de carbono

Instrumenta una aplicación de inferencia local usando un modelo cuantizado con llama.cpp (por ejemplo, Llama 3 8B en GGUF INT4) y CodeCarbon. Ejecuta 100 queries representativas de un caso de uso real y registra el consumo en kWh y las emisiones en gCO2e. A continuación, repite el experimento con el mismo modelo sin quantizar (si la memoria lo permite) o con un modelo de mayor tamaño. Compara los resultados y redacta un informe de una página con recomendaciones de configuración sostenible para el caso de uso elegido.

### Actividad 2: Análisis de licencias y due diligence legal

Selecciona tres modelos open-weight disponibles en Hugging Face con distintas licencias (por ejemplo: Llama 3 Community License, Apache 2.0, y una licencia restrictiva de tu elección). Para cada modelo, responde: ¿Puede usarse en una aplicación comercial de pago? ¿Puede usarse para entrenar un modelo derivado? ¿Requiere atribución en los outputs? ¿Tiene restricciones de usuarios o sectores? Presenta los resultados en una tabla comparativa y justifica cuál elegirías para una startup de asistencia legal, explicando los riesgos residuales.

### Actividad 3: Evaluación de riesgos PRL para un puesto de trabajo con IA

Asume el rol de técnico de PRL en una empresa que acaba de incorporar un equipo de cinco personas cuya función principal es revisar y validar outputs de un LLM de atención al cliente (300-500 revisiones diarias por persona). Elabora una evaluación de riesgos psicosociales siguiendo la metodología del INSST (Instituto Nacional de Seguridad y Salud en el Trabajo), identifica al menos cuatro riesgos específicos del puesto y propone medidas preventivas concretas. Incluye referencia explícita a la Ley 31/1995 y al artículo 88 de la LOPDGDD.

### Actividad 4: Dilema ético profesional

Lee el siguiente escenario: "Trabajas como ingeniero de ML en una empresa de recursos humanos. Tu responsable te pide que despliegues en producción un sistema de cribado de CVs basado en un LLM que ha sido evaluado internamente con buenos resultados de precisión global, pero cuyo análisis de sesgos muestra una tasa de rechazo un 23% mayor para candidatos con nombres de origen extranjero. Tu responsable argumenta que el cliente necesita el sistema en dos semanas y que el sesgo puede corregirse en una iteración posterior."

Responde: ¿Qué harías y por qué? Estructura tu respuesta aplicando explícitamente el ACM Code of Ethics (principios 1.2 y 2.5) y el principio de no maleficencia. Identifica qué información adicional necesitarías, qué pasos seguirías antes de tomar una decisión final, y cuál sería tu límite de negativa fundamentada.

---

## 10. Referencias

**Normativa y marcos regulatorios**

- Reglamento (UE) 2024/1689 del Parlamento Europeo y del Consejo, de 13 de junio de 2024, por el que se establecen normas armonizadas en materia de inteligencia artificial (Ley de Inteligencia Artificial). Disponible en: https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689

- Ley 31/1995, de 8 de noviembre, de Prevención de Riesgos Laborales. BOE núm. 269, de 10 de noviembre de 1995. Disponible en: https://www.boe.es/buscar/act.php?id=BOE-A-1995-24292

- Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos Personales y garantía de los derechos digitales (LOPDGDD), artículo 88. BOE núm. 294, de 6 de diciembre de 2018. Disponible en: https://www.boe.es/buscar/act.php?id=BOE-A-2018-16673

**Propiedad intelectual y copyright**

- U.S. Copyright Office (2024). *Copyright and Artificial Intelligence. Part 2: Copyrightability*. Disponible en: https://www.copyright.gov/ai/

- Sag, M. (2023). *Copyright Safety for Generative AI*. Houston Law Review. Disponible en: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4438593

**Impacto ambiental**

- Strubell, E., Ganesh, A., & McCallum, A. (2019). *Energy and Policy Considerations for Deep Learning in NLP*. Proceedings of ACL 2019. Disponible en: https://arxiv.org/abs/1906.02629

- Patterson, D., Gonzalez, J., Le, Q., et al. (2021). *Carbon Considerations for Large Language Model Training*. IEEE Micro. Disponible en: https://arxiv.org/abs/2104.10350

- Luccioni, A. S., Viguier, S., & Ligozat, A. L. (2022). *Estimating the Carbon Footprint of BLOOM, a 176B Parameter Language Model*. Journal of Machine Learning Research. Disponible en: https://arxiv.org/abs/2211.02001

- CodeCarbon (repositorio oficial). Disponible en: https://github.com/mlco2/codecarbon

**Marcos éticos profesionales**

- Association for Computing Machinery (2018). *ACM Code of Ethics and Professional Conduct*. Disponible en: https://www.acm.org/code-of-ethics

- IEEE (2019). *Ethically Aligned Design: A Vision for Prioritizing Human Well-being with Autonomous and Intelligent Systems* (First Edition). Disponible en: https://standards.ieee.org/wp-content/uploads/import/documents/other/ead1e.pdf

**Optimización y eficiencia**

- Leviathan, Y., Kalman, M., & Matias, Y. (2023). *Fast Inference from Transformers via Speculative Decoding*. Proceedings of ICML 2023. Disponible en: https://arxiv.org/abs/2211.17192

- Anthropic (2024). *Prompt Caching (documentación oficial)*. Disponible en: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching

- Frantar, E., Ashkboos, S., Hoefler, T., & Alistarh, D. (2022). *GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers*. Disponible en: https://arxiv.org/abs/2210.17323

---

*Unidad elaborada para el módulo MP04 · Soluciones LLM. CFS1 · Gestión de datos y entrenamiento IA. Versión: junio 2026.*
