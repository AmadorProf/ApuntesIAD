# UD1 · Análisis del caso de uso y selección del modelo LLM

---

## 1. Introducción

Los modelos de lenguaje de gran escala (LLMs, por sus siglas en inglés) han dejado de ser curiosidades de investigación para convertirse en una plataforma de software sobre la que se construyen aplicaciones con impacto real en la industria. Esta transición —de laboratorio a producción— exige un cambio de mentalidad: ya no basta con saber que un modelo "funciona bien"; hay que entender exactamente para qué funciona bien, en qué condiciones y a qué precio.

La elección del modelo LLM es, ante todo, una decisión arquitectónica. Igual que la selección de una base de datos (relacional vs. documental vs. vectorial) determina la estructura de toda la solución, la elección del modelo condiciona la latencia, el coste, la privacidad, la mantenibilidad y el techo de calidad del sistema. Un equipo que empieza construyendo sobre GPT-4o y más tarde descubre que el 90 % del valor lo aporta un modelo abierto de 8B parámetros desplegable en local habrá malgastado semanas de integración y cientos de euros en llamadas a la API. A la inversa, un equipo que elige un modelo pequeño para ahorrar costes y luego comprueba que no alcanza la calidad mínima aceptable para el caso de uso también habrá desperdiciado el mismo tiempo.

El proceso correcto es el inverso al intuitivo: primero se analiza en detalle el caso de uso, se elicitan los requisitos de calidad, coste, privacidad y latencia, y solo entonces se evalúan los modelos candidatos frente a esos requisitos. Esta unidad didáctica proporciona el marco conceptual y las herramientas prácticas para ejecutar ese proceso de forma sistemática.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Clasificar cualquier tarea de procesamiento de lenguaje natural dentro de la taxonomía de casos de uso LLM y describir sus características diferenciadoras.
- Aplicar la metodología de análisis de requisitos en 7 pasos para especificar con precisión qué se le pide al modelo antes de evaluarlo.
- Comparar los principales modelos LLM propietarios y de pesos abiertos disponibles en 2025, citando parámetros cuantitativos relevantes (contexto, coste por millón de tokens, puntuación en benchmarks estándar).
- Interpretar correctamente los benchmarks de evaluación de LLMs, identificando sus limitaciones y evitando conclusiones erróneas por aplicación directa de la Ley de Goodhart.
- Construir un análisis coste-beneficio básico que permita decidir entre soluciones basadas en API y soluciones auto-alojadas, incluyendo el cálculo del punto de equilibrio.
- Completar las actividades prácticas propuestas documentando los criterios de decisión empleados.

---

## 3. Taxonomía de casos de uso

No todos los problemas de lenguaje son iguales. Antes de elegir un modelo, es imprescindible identificar a qué categoría pertenece la tarea, porque cada categoría tiene un perfil de requisitos distinto en términos de razonamiento, longitud de contexto, tolerancia al error y coste por consulta.

### 3.1 Generación de texto

Engloba tareas en las que el modelo produce texto original a partir de una instrucción o un contexto. Los subtipos más comunes son:

**Redacción creativa y asistida.** El modelo escribe desde cero o completa fragmentos. La calidad se mide por fluidez, coherencia y adecuación al estilo solicitado. La tolerancia al error factual suele ser alta, pero la tolerancia a incoherencias estilísticas es baja.

**Resumen (summarization).** El modelo condensa un texto largo en uno más corto manteniendo la información clave. Exige ventanas de contexto amplias cuando los documentos son extensos. El riesgo principal es la alucinación de hechos que no aparecen en el texto original (resumen extractivo vs. abstractivo).

**Paráfrasis y reformulación.** El modelo reescribe un texto conservando el significado pero cambiando el estilo, el nivel de lectura o el registro. Útil en simplificación de textos legales, adaptación a distintas audiencias o detección de plagio inverso.

### 3.2 Clasificación y análisis de sentimiento

El modelo asigna una etiqueta a un texto de entrada (positivo/negativo/neutro, categoría temática, urgencia, intención del usuario). Son tareas de baja complejidad razonadora pero que requieren consistencia y calibración: si el modelo clasifica correctamente el 95 % de los casos en evaluación pero lo hace aleatoriamente en el 5 % restante, puede ser inútil en producción si ese 5 % corresponde a los casos ambiguos más importantes.

El análisis de sentimiento es un subtipo particular en el que la etiqueta refleja la polaridad emocional del texto. En contextos B2C (gestión de reseñas, atención al cliente) es uno de los casos de uso LLM más extendidos.

### 3.3 Extracción de información

**NER (Named Entity Recognition).** Identificación y clasificación de entidades nombradas: personas, organizaciones, fechas, importes, localizaciones. Crítico en sectores como legal, salud y finanzas donde los datos estructurados se extraen de documentos no estructurados.

**Extracción de relaciones.** Dado un texto, identificar qué relación semántica existe entre dos entidades ("X adquirió Y en Z fecha"). Más complejo que el NER puro; requiere cierta capacidad de razonamiento.

**Extracción a tabla.** Convertir texto libre (p. ej., un contrato o una ficha técnica) en filas y columnas estructuradas. Muy demandado en automatización de back-office.

### 3.4 QA cerrado y QA abierto con RAG

**QA closed-book.** El modelo responde preguntas usando únicamente el conocimiento almacenado en sus pesos durante el entrenamiento. Funciona bien para conocimiento general estable, pero falla en información reciente, propietaria o muy específica.

**QA open-book / RAG (Retrieval-Augmented Generation).** El modelo recibe, junto con la pregunta, fragmentos de documentos recuperados de una base de conocimiento externa. Reduce las alucinaciones y permite actualizar el conocimiento sin reentrenar el modelo. Es el patrón arquitectónico dominante en asistentes corporativos y chatbots sobre documentación técnica.

### 3.5 Generación de código

El modelo escribe, explica, depura o traduce código fuente. Requiere capacidades de razonamiento formal y comprensión de sintaxis precisa. Los modelos con mejor rendimiento en código (p. ej., con entrenamiento específico sobre repositorios de GitHub) muestran diferencias significativas respecto a modelos de propósito general incluso con el mismo número de parámetros.

### 3.6 Traducción y transformación de formato

**Traducción automática neuronal.** Los LLMs de gran escala han alcanzado o superado a los sistemas especializados de traducción en muchos pares de idiomas, especialmente los de alta frecuencia en el preentrenamiento.

**Transformación de formato.** Conversión de JSON a XML, de Markdown a HTML, de texto libre a YAML, de SQL a lenguaje natural. Son tareas de complejidad baja pero con alto impacto en productividad de desarrolladores.

### 3.7 Agentes y automatización

Los agentes LLM son sistemas en los que el modelo no solo genera texto sino que decide qué herramientas usar (buscadores, APIs, calculadoras, ejecutores de código) y actúa en bucles de razonamiento iterativo (ReAct, cadenas de pensamiento). Son el caso de uso de mayor complejidad arquitectónica y el que presenta más riesgos de comportamiento no deseado si no se implementan correctamente los mecanismos de guardia.

### 3.8 Tabla de ejemplos industriales por sector

| Sector | Caso de uso | Tipo de tarea | Consideraciones especiales |
|---|---|---|---|
| Salud | Resumen de historiales clínicos | Resumen | HIPAA/GDPR; alucinaciones con consecuencias críticas |
| Salud | Extracción de diagnósticos de informes de radiología | Extracción NER | Validación por especialista obligatoria |
| Legal | Revisión de contratos y detección de cláusulas de riesgo | Extracción + clasificación | Confidencialidad; contexto largo (>100k tokens) |
| Legal | Redacción de escritos judiciales | Generación de texto | Jurisdicción específica; citación de precedentes |
| Finanzas | Análisis de sentimiento sobre noticias bursátiles | Clasificación | Latencia crítica; datos en tiempo real |
| Finanzas | Extracción de datos de informes financieros a tablas | Extracción a tabla | Precisión numérica; tablas PDF complejas |
| Educación | Generación de ejercicios adaptativos | Generación de texto | Adecuación al nivel; diversidad de ejemplos |
| Educación | Corrección automática de respuestas abiertas | Clasificación + razonamiento | Calibración de rúbricas; explicabilidad |
| Manufactura | QA sobre manuales técnicos (RAG) | QA open-book | Documentación propietaria; inglés técnico |
| Manufactura | Generación de código PLC a partir de especificaciones | Generación de código | Sintaxis específica del fabricante |

---

## 4. Análisis de requisitos para selección

La selección de un modelo LLM sin un análisis previo de requisitos es equivalente a elegir una base de datos por popularidad en lugar de por el patrón de acceso a los datos. El siguiente proceso de 7 pasos proporciona un marco estructurado para evitar ese error.

### Paso 1 — Definir la tarea exacta

La definición debe ser operativa, no aspiracional. "Mejorar la atención al cliente" no es una definición de tarea; "clasificar tickets de soporte en 12 categorías y, si la categoría es facturación, extraer el importe reclamado y el número de factura" sí lo es. La definición exacta de la tarea determina qué capacidades del modelo son necesarias y cuáles son irrelevantes.

Herramienta útil: escribir tres ejemplos de entrada real (con datos anonimizados si procede) y la salida esperada para cada uno antes de continuar con los pasos siguientes.

### Paso 2 — Requisitos de calidad

La calidad no es un concepto único: hay que especificar la métrica de evaluación y el umbral mínimo aceptable. ¿Se mide con F1 sobre entidades extraídas? ¿Con BLEU/ROUGE sobre resúmenes? ¿Con tasa de aprobación humana en evaluación cegada? ¿Con precisión y recall sobre etiquetas de clasificación?

También hay que definir qué tipo de errores son más costosos. En un sistema de triaje médico, un falso negativo (omitir una condición grave) es radicalmente peor que un falso positivo. Esta asimetría del error debe reflejarse en los criterios de evaluación.

### Paso 3 — Latencia aceptable

¿Cuál es el tiempo de respuesta máximo tolerable por el usuario o el sistema aguas abajo? Las diferencias entre modelos son enormes: un modelo de 70B parámetros en API puede tardar 8-15 segundos en generar 500 tokens; un modelo de 8B parámetros auto-alojado en hardware adecuado puede hacerlo en 1-2 segundos. Si la tarea es una interfaz conversacional en tiempo real, la latencia es un requisito duro. Si es un proceso de batch nocturno, no importa.

También hay que distinguir entre latencia hasta el primer token (TTFT, Time to First Token) y latencia total de generación: en interfaces de streaming, el TTFT es más relevante para la experiencia de usuario percibida.

### Paso 4 — Volumen y coste (tokens por mes)

Estimar el volumen de tokens de entrada y salida esperado por mes es el paso más frecuentemente omitido y el más relevante para la viabilidad económica del proyecto. El cálculo requiere:

- Número estimado de consultas por día/mes.
- Longitud media del prompt (tokens de entrada), incluyendo instrucciones de sistema y contexto.
- Longitud media de la respuesta esperada (tokens de salida).
- Los precios de los modelos candidatos por millón de tokens de entrada y de salida.

A este cálculo hay que sumarle los costes de infraestructura si se opta por soluciones auto-alojadas (GPU, mantenimiento, personal técnico).

### Paso 5 — Restricciones de privacidad y localización de datos

¿Pueden los datos de la tarea enviarse a APIs externas? ¿Existen restricciones regulatorias (GDPR, HIPAA, NIS2) que obliguen a que el procesamiento ocurra en una infraestructura concreta o en una jurisdicción geográfica específica? ¿Los datos son confidenciales de negocio y la empresa prefiere no exponerlos a terceros aunque no haya obligación legal?

Si la respuesta a alguna de estas preguntas impide el uso de APIs en la nube, el espacio de modelos candidatos se reduce a opciones desplegables en infraestructura propia: modelos de pesos abiertos (Llama, Mistral, Qwen) o despliegues en VPC privada de proveedores que ofrezcan esa modalidad (Azure OpenAI con VNET, AWS Bedrock con endpoints privados, Anthropic para empresas con acuerdos de no entrenamiento sobre datos).

### Paso 6 — Requisitos de licencia

Los modelos de pesos abiertos tienen licencias que varían significativamente. Llama 3.1 permite uso comercial con restricciones de redistribución para organizaciones con más de 700 millones de usuarios activos mensuales. Mistral 7B usa licencia Apache 2.0, que permite uso comercial sin restricciones. Algunos modelos de investigación solo permiten uso no comercial. La licencia del modelo determina lo que se puede hacer con él en producción y si se pueden publicar adaptaciones (fine-tunes).

### Paso 7 — Necesidad de fine-tuning

¿El modelo base, con instrucción de sistema bien diseñada (prompt engineering), es suficiente para alcanzar los requisitos de calidad del Paso 2? Si no lo es, ¿el problema se resuelve con few-shot examples en el prompt? ¿O es necesario fine-tuning sobre datos del dominio?

El fine-tuning añade coste (datos de entrenamiento etiquetados, computación GPU, mantenimiento del modelo ajustado) y complejidad operativa. Solo debe considerarse cuando el prompt engineering bien ejecutado no es suficiente, cuando el volumen de consultas hace que incluir muchos ejemplos en el prompt sea prohibitivamente caro, o cuando se necesita un comportamiento muy específico que el modelo base no exhibe.

### Plantilla de análisis de requisitos

| Dimensión | Pregunta clave | Respuesta del proyecto |
|---|---|---|
| Tarea exacta | ¿Qué hace el modelo, con qué entrada, produciendo qué salida? | |
| Calidad | ¿Qué métrica? ¿Qué umbral mínimo? ¿Asimetría del error? | |
| Latencia | ¿Tiempo de respuesta máximo tolerable? ¿TTFT o latencia total? | |
| Volumen/Coste | ¿Consultas/mes? ¿Tokens input/output por consulta? ¿Presupuesto máximo? | |
| Privacidad | ¿Pueden los datos salir de la infraestructura propia? ¿Qué regulación aplica? | |
| Licencia | ¿Uso comercial? ¿Redistribución? ¿Publicación de fine-tunes? | |
| Fine-tuning | ¿El prompting basta? ¿Hay datos de dominio disponibles para ajuste? | |

---

## 5. Panorama de modelos LLM

El ecosistema de modelos LLM evoluciona rápidamente. Los datos siguientes corresponden al estado del mercado a mediados de 2025 y deben consultarse siempre contra las fuentes primarias antes de tomar decisiones de proyecto.

### 5.1 Modelos propietarios

**GPT-4o (OpenAI).** Modelo multimodal de OpenAI que acepta texto, imágenes y audio. Con una ventana de contexto de 128.000 tokens y capacidades de razonamiento avanzadas, es el modelo de referencia para tareas de alta complejidad. La API de OpenAI es madura, con amplia documentación y un ecosistema de herramientas de terceros muy desarrollado. El precio de inferencia es significativamente más alto que el de modelos de la gama media.

**Claude 3.5 Sonnet (Anthropic).** Modelo de Anthropic con ventana de contexto de 200.000 tokens, especialmente destacado en tareas de análisis de documentos largos, redacción y seguimiento de instrucciones complejas. Anthropic pone énfasis especial en la seguridad y la controlabilidad del modelo, lo que lo hace atractivo para casos de uso en sectores regulados. Ofrece acuerdos comerciales con garantías de no uso de datos para entrenamiento.

**Gemini 1.5 Pro (Google).** Modelo de Google con una ventana de contexto excepcional de hasta 1 millón de tokens (en algunos entornos de prueba, hasta 2 millones), lo que lo hace especialmente útil para tareas sobre colecciones de documentos muy extensas que no se pueden fragmentar. Integrado con el ecosistema de Google Cloud (Vertex AI), lo que simplifica el despliegue para organizaciones ya en ese ecosistema.

### 5.2 Modelos de pesos abiertos

**Llama 3.1 (Meta).** Familia disponible en tres tamaños: 8B, 70B y 405B parámetros. El modelo de 70B ha demostrado rendimiento competitivo con GPT-4 en varios benchmarks a un coste de inferencia muy inferior cuando se auto-aloja. El modelo de 405B es el mayor modelo de pesos abiertos disponible en 2025 y compite directamente con los mejores modelos propietarios. La licencia permite uso comercial con las restricciones mencionadas en el Paso 6.

**Mistral Large / Mistral 7B (Mistral AI).** Mistral 7B fue el primer modelo de pesos abiertos que demostró que un modelo de tamaño reducido con un entrenamiento cuidadoso puede superar a modelos mucho más grandes en benchmarks de razonamiento. Mistral Large es el modelo de mayor capacidad de la familia y compite con GPT-4 en tareas complejas. La empresa francesa ofrece también una API propia (La Plateforme) y es el principal referente europeo en modelos de pesos abiertos.

**Qwen 2.5 72B (Alibaba Cloud).** Modelo de pesos abiertos de Alibaba con rendimiento muy competitivo en benchmarks de razonamiento y código. Especialmente fuerte en idiomas asiáticos (chino, japonés, coreano) mientras mantiene buen rendimiento en inglés. Disponible en Hugging Face con licencia permisiva para uso comercial.

**Phi-3.5 (Microsoft).** Familia de modelos pequeños (3.8B, 14B parámetros) de Microsoft diseñados específicamente para maximizar el rendimiento por parámetro. Phi-3.5 Mini supera a modelos significativamente más grandes en benchmarks de razonamiento matemático y de sentido común, lo que lo hace atractivo para despliegues en dispositivos con recursos limitados o para casos de uso donde la latencia y el coste son prioridad absoluta.

### 5.3 Tabla comparativa de modelos

| Modelo | Parámetros | Contexto (tokens) | Coste input ($/M tokens) | Coste output ($/M tokens) | Licencia | MMLU (5-shot) |
|---|---|---|---|---|---|---|
| GPT-4o | No publicado | 128k | ~5 | ~15 | Propietaria | ~88 % |
| Claude 3.5 Sonnet | No publicado | 200k | ~3 | ~15 | Propietaria | ~88 % |
| Gemini 1.5 Pro | No publicado | 1M+ | ~3.5 | ~10.5 | Propietaria | ~85 % |
| Llama 3.1 405B | 405B | 128k | ~2 (API third-party) | ~2 | Llama 3.1 Community | ~88 % |
| Llama 3.1 70B | 70B | 128k | ~0.5-0.9 | ~0.5-0.9 | Llama 3.1 Community | ~83 % |
| Llama 3.1 8B | 8B | 128k | ~0.05-0.2 | ~0.05-0.2 | Llama 3.1 Community | ~73 % |
| Mistral Large | No publicado | 128k | ~3 | ~9 | Propietaria (API) | ~84 % |
| Mistral 7B | 7B | 32k | Auto-alojado | Auto-alojado | Apache 2.0 | ~64 % |
| Qwen 2.5 72B | 72B | 128k | Auto-alojado / API | Auto-alojado / API | Qwen License | ~84 % |
| Phi-3.5 Mini | 3.8B | 128k | Auto-alojado | Auto-alojado | MIT | ~70 % |

*Nota: Los precios varían frecuentemente. Consultar siempre las páginas de precios oficiales antes de realizar estimaciones de coste.*

---

## 6. Benchmarks de evaluación

Los benchmarks son instrumentos de medida, no verdades absolutas. Comprender qué mide cada uno y cuáles son sus limitaciones es tan importante como conocer los valores numéricos.

### 6.1 MMLU — Massive Multitask Language Understanding

Desarrollado por Hendrycks et al. (2021), MMLU consiste en 57 materias académicas (desde matemáticas y física hasta derecho y medicina) con 15.908 preguntas de opción múltiple. Es el benchmark de referencia para medir el conocimiento general y la capacidad de razonamiento multidisciplinar. La puntuación se expresa como porcentaje de respuestas correctas en formato 5-shot (el modelo ve 5 ejemplos antes de responder).

**Limitación principal:** muchos de los textos del benchmark han filtrado hacia los conjuntos de entrenamiento de los modelos, lo que puede inflar artificialmente las puntuaciones mediante memorización. Además, MMLU mide conocimiento estático; no captura la capacidad de razonar con información nueva.

### 6.2 HumanEval y MBPP — Evaluación de generación de código

HumanEval (OpenAI, 2021) consiste en 164 problemas de programación en Python con tests unitarios. La métrica estándar es pass@k: probabilidad de que al menos una de k soluciones generadas pase todos los tests. MBPP (Mostly Basic Programming Problems) amplía la cobertura con 374 problemas de dificultad variable.

Ambos benchmarks tienen el mismo defecto: el conjunto de problemas es público y puede haber sido incluido en el entrenamiento. Los resultados en HumanEval deben interpretarse siempre junto con evaluaciones internas sobre código privado no publicado.

### 6.3 HellaSwag y WinoGrande — Sentido común

HellaSwag evalúa la capacidad de completar descripciones de situaciones cotidianas eligiendo la continuación más plausible de cuatro opciones. WinoGrande es una versión escalada del Winograd Schema Challenge, que mide resolución de ambigüedades pronominales que requieren razonamiento de sentido común.

Estos benchmarks fueron especialmente útiles para distinguir modelos en 2019-2021; los LLMs actuales los saturan (>90 %) y han perdido capacidad discriminativa entre modelos del estado del arte.

### 6.4 GSM8K — Matemáticas de nivel escolar

GSM8K (Grade School Math 8K) contiene 8.500 problemas matemáticos de nivel de primaria/secundaria que requieren razonamiento de varios pasos. Es uno de los benchmarks más correlacionados con la capacidad general de razonamiento encadenado. Un modelo que resuelve bien GSM8K tiende a mostrar buen rendimiento en tareas de razonamiento en otros dominios.

### 6.5 LMSYS Chatbot Arena — Evaluación humana con sistema Elo

Chatbot Arena es una plataforma donde usuarios humanos reales comparan respuestas de dos modelos anónimos y votan cuál prefieren. Las puntuaciones se calculan con el sistema Elo, el mismo usado en ajedrez competitivo. Es el benchmark que mejor captura la preferencia humana real, porque no depende de respuestas de referencia predefinidas y porque los evaluadores son usuarios genuinos haciendo preguntas reales.

**Ventaja:** resistente a la contaminación de datos de entrenamiento y alineado con la experiencia de usuario real.  
**Limitación:** los usuarios de Chatbot Arena no son representativos de todos los casos de uso industriales; el benchmark favorece modelos con respuestas largas, bien formateadas y con tono confiado, independientemente de si son factualment correctas.

### 6.6 MT-Bench

MT-Bench evalúa los modelos en conversaciones de múltiples turnos sobre 80 preguntas de alta dificultad en 8 categorías (escritura, razonamiento, matemáticas, código, extracción, STEM, humanidades, rol). Usa GPT-4 como juez automático para puntuar las respuestas. Es útil para medir capacidades de seguimiento de instrucciones en diálogo, aunque la dependencia de GPT-4 como árbitro introduce sesgos hacia el estilo de respuesta de ese modelo.

### 6.7 Cómo interpretar benchmarks y la Ley de Goodhart aplicada a LLMs

La Ley de Goodhart (originalmente formulada en economía) establece que "cuando una medida se convierte en objetivo, deja de ser una buena medida". Aplicada a LLMs: cuando los laboratorios de IA optimizan sus modelos para maximizar puntuaciones en benchmarks públicos, esos benchmarks dejan de medir lo que pretendían medir y se convierten en métricas de rendimiento en un conjunto de preguntas específicas.

Las consecuencias prácticas para quien elige modelos son:

1. **No seleccionar un modelo solo por su posición en un ranking de benchmarks.** Evaluar siempre el modelo en datos del dominio específico del proyecto.
2. **Sospechar de puntuaciones excepcionalmente altas** en benchmarks muy populares, especialmente si el modelo no ha publicado su conjunto de datos de entrenamiento.
3. **Construir un benchmark interno** con 50-200 ejemplos del caso de uso real, anotados por expertos del dominio, y usarlo como criterio primario de selección.
4. **Monitorizar la degradación** en producción: un modelo que funciona bien en evaluación offline puede degradarse por cambios en la distribución de entrada real.

---

## 7. Análisis coste-beneficio

La selección de un modelo no es solo una decisión técnica; es también una decisión financiera. El análisis coste-beneficio debe contemplar todos los componentes del coste total de propiedad, no solo el coste por token de inferencia.

### 7.1 Modelo de costes de una solución LLM

**Costes de desarrollo:**
- Tiempo de ingeniería para diseño del sistema, prompt engineering, integración de la API, evaluación y puesta en producción.
- Costes de datos de entrenamiento y anotación si se requiere fine-tuning.
- Infraestructura de evaluación (plataformas de anotación, entornos de prueba).

**Costes de inferencia en API:**
- Tokens de entrada por consulta × precio por millón de tokens de entrada.
- Tokens de salida por consulta × precio por millón de tokens de salida.
- Volumen de consultas por mes.
- Costes de almacenamiento y cacheo de prompts si el proveedor lo ofrece (Anthropic, OpenAI y Google ofrecen descuentos por prompt caching que pueden reducir el coste hasta un 90 % en los tokens repetidos).

**Costes de self-hosting:**
- Alquiler o amortización de GPUs (A100 80GB: ~$2-3/hora en cloud; H100: ~$4-5/hora).
- Tiempo de ingeniería de ML Ops para despliegue, monitorización, actualizaciones.
- Almacenamiento de pesos del modelo y datos.
- Coste de red y seguridad de la infraestructura.

### 7.2 API vs. self-hosted: punto de equilibrio

El punto de equilibrio entre API y self-hosting se calcula comparando el coste mensual de cada opción en función del volumen de tokens. Para volúmenes bajos, la API siempre gana: no hay coste fijo de infraestructura. Para volúmenes altos, el self-hosting puede ser más económico, pero solo si la organización tiene la capacidad técnica para operarlo.

**Fórmula simplificada del punto de equilibrio:**

Sea:
- C_api = coste mensual por API = (tokens_input/mes × precio_input + tokens_output/mes × precio_output) / 1.000.000
- C_gpu = coste fijo mensual de GPU + coste de personal técnico + costes operativos

El self-hosting es rentable cuando C_api > C_gpu. Para la mayoría de organizaciones medianas, este punto se alcanza entre los 500 millones y los 2.000 millones de tokens procesados por mes.

### 7.3 Calculadoras de coste recomendadas

- OpenAI Tokenizer (platform.openai.com/tokenizer): estima el número de tokens de un texto dado.
- Anthropic Token Counter (docs.anthropic.com): equivalente para modelos Claude.
- Hugging Face Inference Cost Calculator: estimaciones para modelos de pesos abiertos en diferentes configuraciones de hardware.

### 7.4 Ejemplo de ROI completo

**Escenario:** empresa de gestión documental que procesa 10.000 contratos al mes. Actualmente, dos juristas emplean 2 horas por contrato para revisar y extraer las cláusulas clave. El objetivo es automatizar la extracción usando un LLM y reducir el tiempo humano a 20 minutos de revisión por contrato.

**Situación actual (baseline):**
- 10.000 contratos × 2 horas/contrato = 20.000 horas/mes.
- Coste hora jurista: 60 €/hora.
- Coste mensual baseline: 20.000 × 60 = 1.200.000 €/mes.

**Solución LLM (Claude 3.5 Sonnet via API):**
- Prompt medio por contrato: 8.000 tokens (instrucción + contrato completo).
- Respuesta media: 1.500 tokens (cláusulas extraídas en JSON).
- Tokens input/mes: 10.000 × 8.000 = 80.000.000 tokens = 80M tokens.
- Tokens output/mes: 10.000 × 1.500 = 15.000.000 tokens = 15M tokens.
- Coste API: (80 × 3 €) + (15 × 15 €) = 240 + 225 = 465 €/mes.
- Tiempo de revisión reducido: 10.000 × 20 min = 3.333 horas/mes × 60 € = 200.000 €/mes.
- Coste de desarrollo e integración (one-time): ~30.000 €.

**Resultado:**
- Ahorro mensual: 1.200.000 − 200.000 − 465 ≈ 999.535 €/mes.
- ROI en el primer mes (tras recuperar inversión): ~97 %.
- Payback del coste de desarrollo: menos de 1 mes.

Este ejemplo ilustra que, en tareas de extracción a escala, el coste de la API es marginal comparado con el ahorro en trabajo manual. El factor crítico es la calidad de extracción: si el modelo comete errores en el 5 % de los contratos y cada error no detectado tiene un coste legal significativo, el análisis cambia completamente.

---

## 8. Actividades prácticas

### Actividad 1 — Clasificación de casos de uso

**Descripción:** Se proporcionan 10 descripciones de proyectos reales (anonimizadas) de diferentes sectores. Para cada una, el estudiante debe: (a) identificar el tipo de tarea de la taxonomía del apartado 3, (b) justificar la clasificación, (c) identificar dos requisitos críticos que determinarán la selección del modelo.

**Entregable:** Tabla completada con clasificación y justificación (máximo 150 palabras por caso).

**Criterio de evaluación:** Precisión de la clasificación (50 %) y calidad de la identificación de requisitos críticos (50 %).

---

### Actividad 2 — Análisis de requisitos con la plantilla de 7 pasos

**Descripción:** El estudiante elige un caso de uso de su sector profesional (o uno propuesto por el docente si no tiene preferencia) y completa la plantilla de análisis de requisitos del apartado 4. Debe incluir datos cuantitativos estimados (volumen de tokens, presupuesto máximo, umbral de calidad) y justificar cada decisión.

**Entregable:** Plantilla completada + documento de 400-600 palabras explicando las decisiones y los trade-offs identificados.

**Criterio de evaluación:** Completitud y coherencia interna de la plantilla (40 %), justificación de los trade-offs (40 %), uso de datos cuantitativos (20 %).

---

### Actividad 3 — Evaluación comparativa de modelos

**Descripción:** Usando la API de al menos dos modelos diferentes (p. ej., GPT-4o Mini y Llama 3.1 8B vía Groq o un proveedor similar), el estudiante ejecuta el mismo conjunto de 20 prompts de prueba sobre una tarea definida. Documenta: (a) las respuestas obtenidas, (b) una evaluación manual de calidad en escala 1-5, (c) el tiempo de respuesta medido, (d) el coste estimado por consulta.

**Entregable:** Cuaderno Jupyter o documento con resultados tabulados, análisis comparativo y recomendación de modelo justificada.

**Criterio de evaluación:** Rigor metodológico de la comparación (40 %), análisis de resultados (40 %), claridad de la recomendación (20 %).

---

### Actividad 4 — Análisis coste-beneficio de un proyecto real

**Descripción:** Partiendo del caso de uso analizado en la Actividad 2, el estudiante construye un análisis coste-beneficio completo que incluya: (a) estimación del coste mensual de la solución actual (baseline), (b) estimación del coste de la solución LLM (desarrollo + inferencia mensual), (c) cálculo del ahorro mensual y del período de payback, (d) análisis de sensibilidad: ¿qué pasa si el volumen se duplica? ¿Si el precio de la API sube un 50 %?

**Entregable:** Hoja de cálculo con el modelo financiero + documento de 300-500 palabras con las conclusiones y la recomendación final.

**Criterio de evaluación:** Corrección del modelo financiero (40 %), análisis de sensibilidad (30 %), coherencia con los requisitos identificados en la Actividad 2 (30 %).

---

## 9. Referencias

### Documentación oficial de proveedores

OpenAI. (2025). *API Reference and Platform Documentation*. OpenAI.  
https://platform.openai.com/docs

Anthropic. (2025). *Claude API Documentation and Model Overview*. Anthropic.  
https://docs.anthropic.com

Meta AI. (2024). *Llama 3.1 Model Card and License*. Meta.  
https://llama.meta.com

Mistral AI. (2025). *Mistral Documentation and La Plateforme*. Mistral AI.  
https://docs.mistral.ai

Hugging Face. (2025). *Hugging Face Hub — Model Repository and Documentation*.  
https://huggingface.co/models

Microsoft Research. (2024). *Phi-3 Technical Report*. Microsoft.  
https://azure.microsoft.com/en-us/blog/introducing-phi-3

### Benchmarks y evaluación

Hendrycks, D., Burns, C., Basart, S., Zou, A., Mazeika, M., Song, D., y Steinhardt, J. (2021). *Measuring Massive Multitask Language Understanding*. International Conference on Learning Representations (ICLR 2021).  
https://arxiv.org/abs/2009.03300

Chen, M., Tworek, J., Jun, H., Yuan, Q., de Oliveira Pinto, H. P., Kaplan, J., ... y Zaremba, W. (2021). *Evaluating Large Language Models Trained on Code (HumanEval)*. OpenAI.  
https://arxiv.org/abs/2107.03374

Zellers, R., Holtzman, A., Bisk, Y., Farhadi, A., y Choi, Y. (2019). *HellaSwag: Can a Machine Really Finish Your Sentence?* Proceedings of ACL 2019.  
https://arxiv.org/abs/1905.07830

Sakaguchi, K., Le Bras, R., Bhagavatula, C., y Choi, Y. (2021). *WinoGrande: An Adversarial Winograd Schema Challenge at Scale*. Communications of the ACM, 64(9).  
https://arxiv.org/abs/1907.10641

Cobbe, K., Kosaraju, V., Bavarian, M., Chen, M., Jun, H., Kaiser, L., ... y Schulman, J. (2021). *Training Verifiers to Solve Math Word Problems (GSM8K)*. OpenAI.  
https://arxiv.org/abs/2110.14168

Zheng, L., Chiang, W. L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., ... y Stoica, I. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. Advances in Neural Information Processing Systems (NeurIPS 2023).  
https://arxiv.org/abs/2306.05685

LMSYS Org. (2025). *Chatbot Arena Leaderboard*. UC Berkeley.  
https://chat.lmsys.org/?leaderboard

### Libros y recursos adicionales

Tuggener, D., y Stamou, G. (2024). *Building LLMs for Production: Enhancing LLM Abilities and Reliability with Prompting, Fine-Tuning, and RAG*. Independently published.  
https://www.amazon.com/dp/B0D4FFPFW8

Goodhart, C. A. E. (1984). *Problems of Monetary Management: The U.K. Experience* (sobre la Ley de Goodhart). En Monetary Theory and Practice. Palgrave Macmillan.

---

*Fin del temario — UD1 · Análisis del caso de uso y selección del modelo LLM*
