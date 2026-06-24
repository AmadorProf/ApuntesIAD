# UD7 · Vigilancia tecnológica en el ecosistema de LLMs

---

## 1. Introducción: la velocidad de cambio en LLMs

El ecosistema de los modelos de lenguaje de gran escala (LLMs, por sus siglas en inglés) no sigue los ritmos habituales de maduración tecnológica. En la mayoría de los sectores industriales, los ciclos de innovación relevante se miden en años. En el campo de los LLMs, esos ciclos se han comprimido primero a meses y, en los últimos tiempos, a semanas. Entre la publicación de un modelo de referencia y la aparición de otro que lo supera en los principales benchmarks pueden transcurrir apenas treinta días.

Esta dinámica tiene consecuencias directas para cualquier profesional que trabaje con soluciones basadas en inteligencia artificial. Un pipeline construido sobre el modelo más eficiente disponible en enero puede ser tecnológicamente obsoleto en abril, no porque el pipeline esté mal diseñado, sino porque el ecosistema se ha movido bajo sus pies. La vigilancia tecnológica deja de ser una práctica opcional o periódica y se convierte en una competencia nuclear del perfil profesional.

En el contexto de este módulo, entendemos vigilancia tecnológica como el proceso sistemático de identificar, filtrar, interpretar y aplicar información relevante sobre el estado y la evolución del ecosistema de LLMs. No se trata de leer todo lo que se publica —la cantidad de papers, posts y releases es inabarcable— sino de desarrollar un sistema de seguimiento selectivo, con fuentes calibradas y criterios de evaluación propios.

Esta unidad didáctica aborda ese sistema: desde la comprensión del estado del arte actual hasta los mecanismos prácticos para evaluar la adopción de un nuevo modelo en un entorno productivo real.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el alumnado será capaz de:

- Describir la evolución histórica de los LLMs y situar los hitos más relevantes en su contexto técnico y temporal.
- Distinguir entre modelos propietarios y open-weight, identificando las ventajas y limitaciones de cada categoría según el caso de uso.
- Interpretar los principales leaderboards y benchmarks del sector, comprendiendo sus metodologías y sus limitaciones.
- Construir un sistema personal de vigilancia tecnológica con fuentes seleccionadas y criterios de filtrado.
- Aplicar un proceso sistemático para evaluar la adopción de un nuevo modelo en un entorno profesional.
- Identificar las tendencias emergentes con mayor impacto potencial en el diseño de soluciones basadas en LLMs.

---

## 3. Estado del arte en LLMs

### 3.1 Evolución: de GPT-3 a los modelos de razonamiento

La historia reciente de los LLMs puede estructurarse en varias generaciones que se suceden con rapidez creciente.

**GPT-3 (2020)** representa el primer modelo que demostró de forma convincente que escalar un transformer preentrenado sobre grandes volúmenes de texto producía capacidades emergentes sorprendentes: traducción, resumen, generación de código, respuesta a preguntas. Con 175.000 millones de parámetros, GPT-3 fue durante casi dos años la referencia indiscutida. Su limitación principal era la interfaz: requería acceso mediante API y el diseño de prompts cuidadosos, lo que lo mantenía fuera del alcance de usuarios no técnicos.

**ChatGPT (noviembre de 2022)** cambió la naturaleza del debate. No fue un avance en la arquitectura base, sino en el proceso de alineación mediante RLHF (Reinforcement Learning from Human Feedback) y en la interfaz conversacional. El resultado fue un modelo que cualquier persona podía usar sin formación técnica, lo que disparó la adopción masiva y reconfiguró el mercado en cuestión de semanas.

**GPT-4 (marzo de 2023)** supuso un salto cualitativo en capacidades de razonamiento, multimodalidad inicial y rendimiento en benchmarks profesionales (bar exam, USMLE, etc.). Por primera vez, un LLM superaba el percentil 90 en exámenes diseñados para profesionales humanos, lo que desencadenó tanto entusiasmo como debate sobre las implicaciones reales de esas métricas.

**Los modelos multimodales** consolidaron la tendencia hacia la integración de modalidades. GPT-4V añadió visión; Gemini 1.5 Pro de Google demostró capacidad de procesar horas de vídeo en un único contexto; Claude 3 de Anthropic integró análisis de imágenes con alta precisión. La multimodalidad dejó de ser una característica diferencial y se convirtió en una expectativa de base.

**Los modelos de razonamiento** constituyen la frontera más reciente. OpenAI o1 (septiembre de 2024) introdujo el paradigma de "pensar antes de responder" mediante cadenas de razonamiento internas (chain-of-thought oculto) que mejoran dramáticamente el rendimiento en matemáticas, lógica y programación. DeepSeek-R1 (enero de 2025) replicó ese paradigma en open-weight, con un coste de entrenamiento notablemente inferior, lo que generó un debate significativo sobre la eficiencia relativa de los distintos enfoques.

### 3.2 Tendencias estructurales

**Context windows en expansión.** El contexto procesable por un modelo ha pasado de los 2.048 tokens de GPT-3 a los 200.000 de Claude 3.5, el millón de tokens de Gemini 1.5 Pro y los 2 millones de algunas versiones experimentales. Esta expansión cambia fundamentalmente lo que es posible: análisis de documentos completos, bases de código enteras, conversaciones de largo alcance sin pérdida de coherencia.

**Multimodalidad extendida.** La integración de texto, imagen, audio y vídeo en un único modelo no es solo una conveniencia de interfaz; abre categorías de aplicación inaccesibles para modelos unimodales. Los asistentes de voz en tiempo real, el análisis de contenido audiovisual y la interacción con entornos físicos mediante visión son ejemplos directos.

**Small Language Models (SLMs) para edge.** El movimiento contrario a la escalada de parámetros. Phi-3 de Microsoft, Gemma de Google o los modelos cuantizados de LLaMA demuestran que modelos de 3B-7B parámetros, entrenados con datos de alta calidad y técnicas de destilación, pueden igualar o superar en tareas específicas a modelos mucho mayores. Esto habilita inferencia local en dispositivos móviles, sin latencia de red y con privacidad total de los datos.

### 3.3 El debate escala vs. eficiencia: Chinchilla y sus consecuencias

En 2022, Hoffmann et al. publicaron el paper conocido como "Chinchilla" (formalmente: *Training Compute-Optimal Large Language Models*), que demostró que los modelos predominantes en ese momento, incluido GPT-3, estaban significativamente subentrenados en relación con su tamaño. La ley de escala de Chinchilla establece que, para un presupuesto computacional dado, el óptimo es entrenar un modelo más pequeño con más datos, no un modelo más grande con menos datos.

Esta conclusión reorientó las estrategias de entrenamiento de toda la industria. Llama 2 de Meta, GPT-4 Turbo y la mayoría de los modelos post-2022 siguen principios de entrenamiento más alineados con las leyes de Chinchilla. La consecuencia práctica es que el número de parámetros dejó de ser el indicador principal de calidad: un modelo de 70B entrenado con 2T de tokens puede superar a uno de 175B entrenado con 300B de tokens.

---

## 4. Landscape de modelos: propietarios vs. open-weight

### 4.1 Modelos propietarios

Los modelos propietarios son aquellos cuyo acceso se produce exclusivamente a través de API o interfaces controladas por el proveedor. Los pesos del modelo no son públicos, el proceso de entrenamiento es opaco y las condiciones de uso están definidas unilateralmente por la empresa.

**OpenAI** mantiene la familia GPT-4o y los modelos de razonamiento o1/o3. Son referencia en capacidades generales y en integración con herramientas (function calling, code interpreter, file search). Su ecosistema de integraciones (ChatGPT, Azure OpenAI) facilita adopción empresarial.

**Anthropic** ofrece la familia Claude 3.x y Claude 3.5. Se distingue por su enfoque en seguridad (Constitutional AI), ventanas de contexto grandes y rendimiento en tareas de análisis de documentos largos. Claude 3.5 Sonnet ha sido referencia en coding durante varios meses de 2024-2025.

**Google DeepMind** desarrolla la familia Gemini. Gemini 1.5 Pro destaca por su ventana de contexto de un millón de tokens y su integración nativa en el ecosistema Google (Workspace, Vertex AI). Gemini Flash ofrece una variante de alta velocidad y bajo coste.

**Mistral AI** (empresa francesa) opera en un espacio intermedio: publica modelos open-weight pero también ofrece variantes propietarias de mayor capacidad (Mistral Large, Mistral Medium) a través de su plataforma La Plateforme.

### 4.2 Modelos open-weight

Los modelos open-weight publican sus pesos, lo que permite descargarlos, ejecutarlos localmente, ajustarlos mediante fine-tuning y desplegrarlos en infraestructura propia sin dependencia del proveedor original. Es importante notar que "open-weight" no equivale necesariamente a "open source": las licencias pueden imponer restricciones comerciales.

**Meta Llama** es la familia más influyente del espacio open-weight. Llama 2 (2023) democratizó el acceso a modelos de calidad comparable a los propietarios de su generación. Llama 3 (2024) estableció nuevos estándares para open-weight, con versiones de 8B y 70B que compiten con modelos propietarios en benchmarks generales.

**Mistral** (modelos open-weight): Mistral 7B y Mixtral 8x7B (Mixture of Experts) demostraron que la eficiencia arquitectónica puede superar la escalada bruta de parámetros. Mixtral 8x7B con 46B de parámetros totales (pero solo 12B activos por token) compite con GPT-3.5 a una fracción del coste computacional.

**Qwen de Alibaba** ha emergido como una de las familias más competitivas de 2024-2025, con versiones que abarcan desde 0.5B hasta 72B parámetros y soporte nativo para chino e inglés. Qwen2.5-Coder es referencia en tareas de generación de código.

**Phi de Microsoft** (Phi-2, Phi-3) demuestran la hipótesis del "libro de texto de alta calidad": modelos pequeños entrenados con datos cuidadosamente curados superan en muchas tareas a modelos mucho mayores entrenados con datos de menor calidad.

**Falcon del Technology Innovation Institute** (TII, Abu Dabi) fue referencia en 2023, con una licencia permisiva que facilitó adopción comercial.

### 4.3 Ventajas comparativas

La elección entre propietario y open-weight no es ideológica sino estratégica, y depende del caso de uso concreto.

Los modelos propietarios ofrecen: facilidad de integración (API estándar), soporte técnico, actualizaciones continuas sin gestión de infraestructura y rendimiento puntero en capacidades generales. Son apropiados para prototipos rápidos, casos de uso no sensibles en términos de privacidad y equipos sin capacidad de gestión de infraestructura de inferencia.

Los modelos open-weight ofrecen: control total sobre los datos (los datos no salen de la infraestructura propia), posibilidad de fine-tuning para dominio específico, ausencia de costes variables por token (relevante a escala), independencia del proveedor y mayor predictibilidad de comportamiento tras customización. Son apropiados para casos con datos sensibles, requisitos de cumplimiento normativo estricto, necesidad de personalización profunda o volúmenes de inferencia que hacen prohibitivos los costes de API.

La tendencia observable es que la calidad de los modelos open-weight de primera línea converge rápidamente con la de los propietarios. DeepSeek-R1 es el caso más visible: un modelo open-weight que compite con o1 de OpenAI en benchmarks de razonamiento, publicado con pesos accesibles y a un coste de desarrollo que fraccionó las estimaciones previas del sector.

---

## 5. Benchmarks y leaderboards

### 5.1 Hugging Face Open LLM Leaderboard

El leaderboard de Hugging Face (https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard) es la referencia principal para la evaluación comparativa de modelos open-weight. Evalúa modelos sobre conjuntos de benchmarks estandarizados que incluyen razonamiento (ARC, HellaSwag), conocimiento factual (MMLU), matemáticas (GSM8K) y código (HumanEval).

La metodología es reproducible: cualquier investigador puede replicar las evaluaciones. Esto confiere credibilidad pero también introduce la limitación de que los benchmarks fijos se convierten en objetivos de optimización. Varios modelos han demostrado rendimiento excepcional en el leaderboard que no se reproduce en uso real, fenómeno conocido como data contamination (los datos de evaluación están presentes en los datos de entrenamiento).

### 5.2 LMSYS Chatbot Arena

LMSYS Chatbot Arena (https://chat.lmsys.org) adopta una metodología radicalmente diferente: evaluación humana ciega mediante comparación por pares. Los usuarios interactúan simultáneamente con dos modelos anónimos y votan cuál ha respondido mejor. Las puntuaciones siguen el sistema Elo, el mismo utilizado en ajedrez para rankear jugadores.

La fortaleza de este enfoque es que mide preferencia humana real en lugar de métricas automatizadas. Su limitación es el sesgo de selección: los usuarios de LMSYS Arena no representan a la población general de usuarios de LLMs, y las tareas evaluadas están sesgadas hacia las que los usuarios de la plataforma prefieren plantear.

### 5.3 ArtificialAnalysis.ai

ArtificialAnalysis.ai (https://artificialanalysis.ai) cubre una dimensión que los leaderboards de calidad ignoran: el rendimiento operacional. Publica comparativas sistemáticas de latencia (tiempo hasta el primer token, velocidad de generación en tokens por segundo), coste por millón de tokens y disponibilidad de los principales proveedores de API.

Esta información es crítica para decisiones de adopción: un modelo con puntuaciones de calidad ligeramente inferiores puede ser la mejor elección si su latencia es diez veces menor o su coste es un orden de magnitud inferior para el volumen proyectado.

### 5.4 Vellum LLM Leaderboard

Vellum (https://www.vellum.ai/llm-leaderboard) agrega métricas de calidad, velocidad y coste en una vista unificada, actualizándose con frecuencia elevada. Es especialmente útil para decisiones de selección de modelo en producción porque combina dimensiones que otros leaderboards tratan por separado.

### 5.5 Limitaciones de los benchmarks: Goodhart's Law en LLMs

La ley de Goodhart establece que cuando una medida se convierte en objetivo, deja de ser una buena medida. En el contexto de los LLMs, esto se manifiesta de múltiples formas:

**Overfitting a benchmarks.** Los laboratorios optimizan sus modelos (deliberada o inadvertidamente) sobre los datasets de evaluación más utilizados. Un modelo puede obtener puntuaciones MMLU excelentes porque sus datos de entrenamiento incluyen los textos del benchmark, no porque generalice mejor.

**Contaminación de datos.** MMLU, HumanEval y otros benchmarks ampliamente utilizados están presentes en grandes porciones de internet. Los modelos entrenados con datos web sin filtrado específico probablemente han "visto" las respuestas correctas durante el preentrenamiento.

**Capacidades emergentes y sus críticas.** El paper de Schaeffer et al. (2023), "Are Emergent Abilities of Large Language Models a Mirage?", argumenta que muchas capacidades presentadas como "emergentes" (aparecidas repentinamente al superar un umbral de escala) son artefactos de las métricas de evaluación, no fenómenos reales. Cuando se utilizan métricas continuas en lugar de binarias, las mejoras de capacidad son graduales, no abruptas. Esta crítica tiene implicaciones importantes para la interpretación de los benchmarks.

La conclusión práctica es que ningún leaderboard debe tomarse como medida definitiva de calidad. Los benchmarks son señales útiles para filtrado inicial, pero la evaluación sobre casos de uso propios con datos internos es insustituible.

---

## 6. Fuentes de seguimiento especializadas en LLMs

### 6.1 Newsletters

**The Batch (deeplearning.ai)** — https://www.deeplearning.ai/the-batch/. Publicada semanalmente por Andrew Ng, cubre investigación reciente, tendencias de adopción industrial y perspectivas editoriales sobre el impacto de la IA. Tono accesible sin sacrificar rigor técnico. Recomendada como punto de entrada para profesionales con formación técnica moderada.

**Import AI (Jack Clark)** — https://importai.substack.com. Jack Clark, cofundador de Anthropic, publica análisis detallados de papers recientes con énfasis en implicaciones de seguridad y política. Lectura más densa, orientada a perfiles técnicos avanzados o con interés en gobernanza de IA.

**The Algorithmic Bridge (Alberto Romero)** — https://thealgorithmicbridge.substack.com. Análisis crítico del ecosistema de IA, con atención particular a la intersección entre capacidades técnicas y narrativas públicas. Perspectiva más crítica y menos celebratoria que otras fuentes del sector.

**Interconnects (Nathan Lambert)** — https://www.interconnects.ai. Nathan Lambert, investigador especializado en RLHF y alineación, publica análisis técnicos profundos sobre entrenamiento de modelos, evaluación y tendencias de investigación. Referencia para quienes necesitan profundidad técnica sobre los procesos de entrenamiento.

### 6.2 Blogs de laboratorios

**Anthropic Research** — https://www.anthropic.com/research. Publica papers de investigación y posts explicativos sobre los modelos Claude, técnicas de alineación (Constitutional AI, RLHF) e interpretabilidad.

**OpenAI Research** — https://openai.com/research. Blog técnico de OpenAI con posts sobre arquitectura, capacidades y hallazgos de evaluación de los modelos GPT y o1/o3.

**Google DeepMind Blog** — https://deepmind.google/research/publications. Cobertura de investigación en modelos Gemini, AlphaFold, sistemas de razonamiento y temas más amplios de IA fundamental.

**Mistral Blog** — https://mistral.ai/news. Anuncios de modelos, actualizaciones técnicas y perspectivas sobre el ecosistema open-weight desde una perspectiva europea.

### 6.3 Podcasts

**Lex Fridman Podcast** — https://lexfridman.com/podcast. Entrevistas largas (típicamente 2-4 horas) con investigadores y fundadores del campo. No tiene cadencia fija pero produce conversaciones de referencia con figuras como Sam Altman, Ilya Sutskever o Yann LeCun.

**Practical AI (Changelog)** — https://changelog.com/practicalai. Episodios semanales centrados en aplicaciones prácticas de IA, con énfasis en lo que realmente funciona en entornos productivos. Tono más orientado a profesionales que a investigadores.

**The TWIML AI Podcast (Sam Charrington)** — https://twimlai.com. Entrevistas con investigadores sobre papers y proyectos específicos. Profundidad técnica elevada, frecuencia regular. Referencia para seguimiento de investigación académica aplicada.

### 6.4 Hugging Face Daily Papers

https://huggingface.co/papers — Agregación diaria de los papers de IA más citados y discutidos, curada por la comunidad de Hugging Face. Es el mecanismo más eficiente para mantenerse al tanto de la investigación sin leer arxiv directamente. Permite filtrar por tema y ver el nivel de discusión que cada paper ha generado en la comunidad.

---

## 7. Evaluación de nuevos modelos para adopción

La aparición de un nuevo modelo relevante no debe traducirse automáticamente en una decisión de adopción. La velocidad del ecosistema hace tentador perseguir el modelo más reciente, pero los costes de migración (actualización de prompts, reentrenamiento de expectativas de comportamiento, pruebas de regresión, actualización de documentación) son reales y deben justificarse.

El siguiente proceso sistematiza la evaluación:

**Paso 1: Identificar benchmarks relevantes para el caso de uso.** No todos los benchmarks son igualmente relevantes para cada aplicación. Un sistema de análisis de contratos legales debe poner más peso en capacidades de razonamiento sobre texto largo y precisión factual que en benchmarks de codificación. El primer paso es mapear qué dimensiones de rendimiento son críticas para el caso de uso propio.

**Paso 2: Test con dataset interno.** Una vez identificadas las dimensiones relevantes, construir un conjunto de evaluación con ejemplos reales del caso de uso propio. Este dataset debe incluir casos representativos, casos límite conocidos y casos donde el modelo actual falla. La evaluación sobre datos internos es el predictor más fiable de comportamiento en producción.

**Paso 3: Evaluación de coste, latencia y contexto.** Para cada modelo candidato, cuantificar: coste por millón de tokens de entrada y salida, latencia típica (tiempo hasta primer token y velocidad de generación), tamaño máximo de contexto y si ese contexto es suficiente para el caso de uso, disponibilidad y SLA del proveedor si es propietario.

**Paso 4: Evaluación de licencia y privacidad.** Para modelos propietarios: revisar los términos de servicio respecto a uso de datos para entrenamiento, retención de datos, cumplimiento con GDPR y otras regulaciones aplicables. Para modelos open-weight: revisar la licencia (Apache 2.0, licencia propia de Meta, licencia Mistral) y verificar que permite el uso comercial previsto.

**Paso 5: POC con caso real.** Implementar un proof-of-concept en entorno controlado con el nuevo modelo sobre un flujo de trabajo real. Medir no solo la calidad de las respuestas sino también la estabilidad del comportamiento, la facilidad de integración y los costes operacionales reales (que frecuentemente difieren de las estimaciones teóricas).

**Criterios de migración de modelo.** La decisión de migrar debe basarse en una mejora demostrada y cuantificada, no en novedad. Los criterios razonables incluyen: mejora de calidad superior al 15% en evaluación interna, reducción de coste superior al 30% sin degradación de calidad, o acceso a capacidades genuinamente nuevas (multimodalidad, contexto mayor) que el caso de uso requiere. En ausencia de mejora clara en alguna de estas dimensiones, la estabilidad del stack actual tiene valor en sí misma.

---

## 8. Tendencias emergentes

### 8.1 Sistemas multiagente y workflows complejos

La frontera de aplicación más activa no está en modelos individuales sino en la orquestación de múltiples modelos en pipelines complejos. Los sistemas multiagente permiten dividir tareas complejas en subtareas especializadas, ejecutar verificación cruzada entre agentes y gestionar flujos de trabajo que exceden el contexto de un único modelo. Frameworks como LangGraph, AutoGen y CrewAI están madurando rápidamente, aunque el espacio sigue siendo volátil.

### 8.2 Long context (>1M tokens)

La capacidad de procesar más de un millón de tokens en un único contexto no es solo un incremento cuantitativo: habilita categorías de aplicación cualitativamente nuevas. Análisis de bases de código completas, revisión de expedientes médicos extensos, procesamiento de jurisprudencia completa en un único prompt. Las limitaciones actuales son el coste (los tokens de contexto largo son más caros) y la calidad de atención en el middle of the context (los modelos tienden a prestar menos atención a la información en el centro del contexto largo).

### 8.3 Modelos especializados por dominio

La alternativa a los modelos generalistas de gran tamaño es el fine-tuning de modelos más pequeños sobre dominios específicos. Med-PaLM 2 en medicina, Code Llama en programación, Harvey en derecho. Estos modelos especializados pueden superar a los generalistas en su dominio con una fracción del coste de inferencia. La tendencia apunta hacia ecosistemas de modelos especializados orquestados por sistemas de routing que dirigen cada consulta al modelo más adecuado.

### 8.4 On-device LLMs

La inferencia local en dispositivos móviles y de edge elimina la latencia de red, garantiza privacidad total de los datos y permite funcionamiento sin conectividad. Apple Intelligence, los modelos Phi-3 Mini y las versiones cuantizadas de Llama 3 8B son ejemplos actuales. Las limitaciones son el tamaño máximo del modelo que los chips de dispositivo pueden ejecutar eficientemente y la necesidad de cuantización agresiva que puede degradar calidad.

### 8.5 Inferencia más eficiente

El coste y la velocidad de inferencia son limitantes principales para muchas aplicaciones a escala. Las técnicas emergentes incluyen:

**Speculative decoding:** un modelo pequeño (draft model) genera candidatos de tokens que el modelo grande verifica en paralelo, reduciendo el número de llamadas al modelo grande y acelerando la generación.

**Mixture of Experts (MoE):** arquitectura en la que solo una fracción de los parámetros del modelo se activan para cada token. Mixtral 8x7B y los modelos Grok de xAI utilizan esta arquitectura para ofrecer alta calidad con menor coste computacional por inferencia.

**Cuantización:** reducción de la precisión numérica de los pesos (de FP16 a INT8, INT4 o incluso INT2) con impacto mínimo en calidad para muchos casos de uso. Permite ejecutar modelos más grandes en hardware con menor memoria disponible.

---

## 9. Actividades prácticas

**Actividad 1: Construcción de un sistema de vigilancia personal.**
El alumnado diseña su propio sistema de seguimiento del ecosistema LLM: selecciona tres newsletters, dos blogs técnicos y una fuente de papers; define criterios de filtrado; y documenta el flujo de lectura semanal estimado. Se entrega un documento de una página describiendo el sistema y justificando cada elección.

**Actividad 2: Interpretación comparativa de leaderboards.**
Dado un caso de uso hipotético (asistente de soporte técnico para software industrial con datos sensibles de clientes), el alumnado consulta Hugging Face Open LLM Leaderboard, LMSYS Chatbot Arena y ArtificialAnalysis.ai, y elabora una tabla comparativa de los cinco modelos más relevantes según las dimensiones: calidad general, calidad en código, latencia, coste y adecuación para datos sensibles. Se discute en grupo qué modelo elegiría cada equipo y por qué.

**Actividad 3: Evaluación de adopción de un nuevo modelo.**
El alumnado recibe el anuncio ficticio de un nuevo modelo con métricas de benchmark superiores al modelo actual de un caso de uso dado. Aplicando el proceso de cinco pasos descrito en la sección 7, elabora un plan de evaluación completo: qué dataset interno construiría, qué métricas mediría, qué preguntas haría al proveedor sobre licencia y privacidad, y qué umbral de mejora justificaría la migración.

**Actividad 4: Análisis crítico de un paper de benchmarking.**
El alumnado lee el abstract y las secciones de resultados del paper "Are Emergent Abilities of Large Language Models a Mirage?" (Schaeffer et al., 2023) y elabora una síntesis de 300 palabras respondiendo: ¿cuál es el argumento central del paper?, ¿qué implicaciones tiene para la interpretación de leaderboards?, ¿cambia la forma en que deberías evaluar los benchmarks de modelos en el futuro?

---

## 10. Referencias

**Leaderboards y herramientas de evaluación:**

- Hugging Face Open LLM Leaderboard — https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard
- LMSYS Chatbot Arena — https://chat.lmsys.org
- ArtificialAnalysis.ai — https://artificialanalysis.ai
- Vellum LLM Leaderboard — https://www.vellum.ai/llm-leaderboard
- Hugging Face Daily Papers — https://huggingface.co/papers

**Papers académicos:**

- Hoffmann, J., Borgeaud, S., Mensch, A., et al. (2022). *Training Compute-Optimal Large Language Models*. DeepMind. https://arxiv.org/abs/2203.15556 [Paper "Chinchilla"]

- Bubeck, S., Chandrasekaran, V., Eldan, R., et al. (2023). *Sparks of Artificial General Intelligence: Early experiments with GPT-4*. Microsoft Research. https://arxiv.org/abs/2303.12712

- Schaeffer, R., Miranda, B., & Koyejo, S. (2023). *Are Emergent Abilities of Large Language Models a Mirage?* Stanford University. https://arxiv.org/abs/2304.15004

**Fuentes de seguimiento:**

- The Batch (deeplearning.ai) — https://www.deeplearning.ai/the-batch/
- Import AI (Jack Clark) — https://importai.substack.com
- The Algorithmic Bridge (Alberto Romero) — https://thealgorithmicbridge.substack.com
- Interconnects (Nathan Lambert) — https://www.interconnects.ai
- Anthropic Research Blog — https://www.anthropic.com/research
- OpenAI Research Blog — https://openai.com/research
- Google DeepMind Blog — https://deepmind.google/research/publications
- Mistral AI Blog — https://mistral.ai/news
- Lex Fridman Podcast — https://lexfridman.com/podcast
- Practical AI Podcast — https://changelog.com/practicalai
- The TWIML AI Podcast — https://twimlai.com
