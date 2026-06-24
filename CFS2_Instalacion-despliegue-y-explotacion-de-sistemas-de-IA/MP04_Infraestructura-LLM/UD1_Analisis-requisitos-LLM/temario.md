# UD1 · Análisis de requisitos del sistema LLM

---

## 1. Introducción

Los modelos de lenguaje de gran escala (LLMs, Large Language Models) representan el cambio tecnológico más disruptivo en el campo de la inteligencia artificial desde la generalización del aprendizaje profundo. A diferencia de los modelos de ML especializados que dominaron la década anterior —cada uno entrenado para una tarea concreta con datos etiquetados específicos—, los LLMs aprenden representaciones generales del lenguaje durante el preentrenamiento sobre corpus masivos de texto, y luego se adaptan mediante fine-tuning o prompting a una enorme variedad de tareas sin reentrenamiento sustancial. Esta propiedad, denominada generalización emergente, convierte a los LLMs en infraestructura de propósito general del mismo modo que los sistemas operativos lo son para el software: una plataforma sobre la que se construyen capacidades específicas de negocio.

Sin embargo, la decisión de adoptar un LLM en un entorno empresarial no es equivalente a la de adoptar cualquier otro componente de software. Los LLMs plantean un conjunto de desafíos técnicos, económicos y regulatorios que requieren un análisis de requisitos sistemático antes de cualquier decisión de selección o despliegue. La taxonomía de modelos disponibles es amplia y heterogénea: modelos propietarios accesibles exclusivamente via API (GPT-4o de OpenAI, Claude 3 de Anthropic, Gemini de Google), modelos open-source descargables y desplegables en infraestructura propia (Llama 3 de Meta, Mistral, Qwen de Alibaba, Phi de Microsoft), modelos base preentrenados y modelos de instrucción alineados mediante RLHF (Reinforcement Learning from Human Feedback), modelos text-only y modelos multimodales. Cada combinación de estas dimensiones implica restricciones y posibilidades distintas.

El análisis de requisitos de un sistema LLM es, en esencia, un ejercicio de ingeniería de compromisos (trade-off engineering). Los modelos más capaces son también los más grandes, los más lentos en inferencia y los más costosos de operar. Los modelos más rápidos y baratos tienen capacidades más limitadas. Los modelos que pueden desplegarse en infraestructura propia —con el control de datos y privacidad que eso implica— requieren inversión en hardware especializado y operaciones. Los modelos propietarios via API ofrecen alta calidad y simplicidad operativa a cambio de dependencia del proveedor y exposición de datos. Ninguna opción es universalmente superior: la correcta para cada caso de uso depende de la articulación precisa de los requisitos funcionales y no funcionales del sistema.

Esta unidad proporciona el marco conceptual y los instrumentos prácticos para realizar ese análisis de requisitos de forma rigurosa: taxonomía de LLMs, identificación de casos de uso empresariales y sus características técnicas, benchmarks de evaluación, análisis del coste total de propiedad (TCO), y restricciones regulatorias aplicables según el sector y el tipo de datos procesados. El resultado del proceso es una matriz de decisión que fundamenta la selección de modelo sobre criterios técnicos y de negocio explícitos, auditables y revisables.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Clasificar un LLM dado en la taxonomía multidimensional (propietario vs. open-source, base vs. instrucción vs. RLHF, text-only vs. multimodal) y describir las implicaciones prácticas de cada categoría para el despliegue en producción.
2. Identificar los requisitos funcionales y no funcionales relevantes para un caso de uso empresarial de LLM dado, utilizando una plantilla estructurada que cubra idiomas, latencia, throughput, longitud de contexto, capacidades multimodales, seguridad y coste.
3. Seleccionar los benchmarks de evaluación pertinentes para un caso de uso (MMLU, HumanEval, MT-Bench, HELM) y interpretar correctamente sus resultados, incluyendo sus limitaciones conocidas como indicadores de rendimiento real.
4. Comparar modelos propietarios y open-source representativos (GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, Llama 3, Mistral Large, Qwen 2.5, Phi-4) en función de los criterios de un caso de uso específico.
5. Construir un modelo de análisis de coste total de propiedad (TCO) para las alternativas de API vs. hosting propio para un caso de uso con volumen de tráfico conocido, incluyendo coste de infraestructura, personal y oportunidad.
6. Identificar las restricciones regulatorias aplicables a un sistema LLM según el sector (sanidad, finanzas, administración pública, recursos humanos) y el tipo de datos procesados, referenciando el EU AI Act, el RGPD y la normativa sectorial pertinente.
7. Producir un documento de análisis de requisitos completo para un sistema LLM empresarial, estructurado como insumo para la toma de decisión de selección de modelo.
8. Describir las implicaciones técnicas de la longitud del contexto (context window) para distintos casos de uso y su relación con el uso de VRAM, la latencia y el coste por token.

---

## 3. Taxonomía de LLMs

### 3.1 Modelos propietarios vs. open-source

La primera dimensión de clasificación de un LLM es su modelo de distribución:

**Modelos propietarios** son accesibles exclusivamente a través de APIs gestionadas por el proveedor. Los pesos del modelo no son públicos; el usuario no tiene control sobre la infraestructura de inferencia, las versiones del modelo ni las políticas de uso aceptable del proveedor.

- **Ventajas**: alta calidad, sin inversión en infraestructura, actualizaciones automáticas, soporte profesional.
- **Limitaciones**: dependencia del proveedor (vendor lock-in), los datos enviados al API son procesados en infraestructura del proveedor (implicaciones de privacidad y RGPD), coste variable en función del volumen de tokens, riesgo de cambio de precios o discontinuación del servicio.

**Modelos open-source** distribuyen los pesos del modelo bajo licencias que permiten (con variaciones) el uso, la modificación y el redistribución. El usuario los descarga y los despliega en su propia infraestructura.

- **Ventajas**: control total sobre los datos (los datos no salen de la infraestructura propia), personalización mediante fine-tuning, sin dependencia del proveedor, coste predecible (infraestructura propia).
- **Limitaciones**: requieren hardware especializado (GPUs), equipo técnico para operar la infraestructura, rendimiento generalmente inferior a los mejores modelos propietarios en tareas complejas.

Es importante notar que "open-source" en el contexto de LLMs tiene matices: Llama 3 de Meta no usa la licencia OSI clásica, sino una licencia personalizada que restringe el uso comercial a empresas con menos de 700 millones de usuarios mensuales activos. Mistral 7B usa licencia Apache 2.0 (verdaderamente libre). Phi-4 de Microsoft usa licencia MIT.

### 3.2 Modelos base, de instrucción y RLHF

| Tipo | Preentrenamiento | Alineación | Uso principal |
|---|---|---|---|
| Base (pretrained) | Predicción del siguiente token sobre corpus masivo | Ninguno | Fine-tuning posterior, investigación |
| Instrucción (instruction-tuned) | Preentrenamiento + SFT (Supervised Fine-Tuning) sobre pares instrucción-respuesta | Limitada | Seguimiento de instrucciones, asistentes básicos |
| RLHF / RLAIF | Preentrenamiento + SFT + RLHF (o RLAIF) | Alta (seguridad, utilidad, honestidad) | Asistentes conversacionales de producción |

Los **modelos base** generan texto continuando el input (text completion), sin seguir instrucciones ni adoptar el formato de conversación. Son útiles para fine-tuning especializado: el desarrollador ajusta el modelo sobre datos del dominio para producir un modelo de instrucción especializado.

Los **modelos de instrucción** han sido fine-tuneados con pares de instrucción-respuesta (SFT, Supervised Fine-Tuning) para seguir instrucciones en lenguaje natural. Pueden usarse directamente en producción para tareas como extracción de información o clasificación mediante prompting.

Los **modelos RLHF** añaden una etapa de alineación mediante Reinforcement Learning from Human Feedback: humanos evalúan pares de respuestas y el modelo se optimiza para preferir las respuestas mejor valoradas. Esta etapa mejora la seguridad, la coherencia y la utilidad del modelo, pero puede también introducir sesgos de los evaluadores humanos o reducir la capacidad del modelo para ciertos casos extremos.

### 3.3 Modelos multimodales

Los modelos multimodales procesan y generan múltiples modalidades de datos:

- **Texto + imagen (VLMs, Vision-Language Models)**: GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, Llama 3.2 Vision, Phi-4. Pueden describir imágenes, responder preguntas sobre documentos escaneados, extraer información de capturas de pantalla, o analizar gráficos y tablas.
- **Texto + audio**: Gemini 1.5 Pro puede procesar audio directamente. GPT-4o tiene capacidades de voz nativas.
- **Texto + vídeo**: Gemini 1.5 Pro y algunos modelos de investigación soportan análisis de vídeo.
- **Texto + código**: todos los modelos de instrucción modernos soportan generación y análisis de código, pero modelos especializados (Code Llama, DeepSeek-Coder) suelen superar a los generalistas en benchmarks de código.

### 3.4 Comparativa de modelos representativos

| Modelo | Proveedor | Tipo | Context window | Multimodal | Licencia | Caso de uso diferencial |
|---|---|---|---|---|---|---|
| GPT-4o | OpenAI | Propietario | 128K tokens | Sí (texto, imagen, audio) | API | Tareas complejas generalistas, multimodal |
| Claude 3.5 Sonnet | Anthropic | Propietario | 200K tokens | Sí (texto, imagen) | API | Documentos largos, escritura de alta calidad |
| Gemini 1.5 Pro | Google | Propietario | 1M tokens | Sí (texto, imagen, audio, vídeo) | API | Contextos muy largos, multimodal avanzado |
| Llama 3.1 70B | Meta | Open-source | 128K tokens | No (Llama 3.2 sí) | Licencia Meta | Hosting propio, rendimiento alto open-source |
| Mistral Large 2 | Mistral AI | Propietario/OSS | 128K tokens | No | Mistral License | Código, razonamiento, precio competitivo |
| Qwen 2.5 72B | Alibaba | Open-source | 128K tokens | Sí (Qwen-VL) | Apache 2.0 | Chino/inglés, rendimiento alto, licencia libre |
| Phi-4 | Microsoft | Open-source | 16K tokens | No | MIT | Modelos pequeños de alta capacidad |

---

## 4. Casos de uso empresariales de LLMs

### 4.1 Asistentes de código

Los asistentes de código (code copilots) generan, completan, refactorizan, documentan y depuran código en respuesta a instrucciones en lenguaje natural. Los requisitos técnicos característicos de este caso de uso son:

- **Latencia baja**: la experiencia de usuario en asistentes de código en tiempo real requiere respuestas en menos de 1-2 segundos para completado de código, aunque las generaciones largas pueden tolerar latencias mayores.
- **Ventana de contexto amplia**: para entender el código existente de un repositorio, el modelo necesita procesar ficheros de código largos o múltiples ficheros simultáneamente. 32K-128K tokens son típicamente suficientes.
- **Soporte de múltiples lenguajes de programación**: los entornos empresariales mezclan Python, Java, TypeScript, SQL, bash, etc.
- **Privacidad del código fuente**: el código propietario no debe enviarse a APIs de terceros sin análisis de las implicaciones de confidencialidad. Este requisito suele inclinarse la balanza hacia modelos open-source desplegados en infraestructura propia.

### 4.2 Q&A sobre documentos corporativos

Los sistemas de preguntas y respuestas sobre documentos permiten a los usuarios consultar en lenguaje natural repositorios de documentación corporativa: manuales, contratos, políticas internas, informes financieros, bases de conocimiento de soporte. La arquitectura estándar es RAG (Retrieval-Augmented Generation):

```
[Pregunta del usuario]
        |
        v  Embedding de la pregunta (modelo de embeddings)
[Vector query]
        |
        v  Búsqueda semántica en base de datos vectorial (Pinecone, Weaviate, pgvector)
[Top-K fragmentos de documentos relevantes]
        |
        v  Ensamblado del prompt: [instrucción del sistema] + [contexto recuperado] + [pregunta]
[Prompt al LLM]
        |
        v  Generación de respuesta con citas al documento fuente
[Respuesta + referencias]
```

Los requisitos técnicos del RAG empresarial incluyen:
- **Fidelidad factual**: el modelo debe responder basándose en los documentos recuperados, sin alucinar información no presente en ellos.
- **Citación de fuentes**: el sistema debe indicar de qué documento proviene cada parte de la respuesta para permitir la verificación humana.
- **Latencia tolerable**: 2-5 segundos de respuesta son generalmente aceptables para sistemas de consulta de documentos.
- **Manejo de idiomas**: en organizaciones multinacionales, los documentos pueden estar en varios idiomas.

### 4.3 Generación y extracción de contenido estructurado

La extracción de entidades y datos estructurados de documentos no estructurados (facturas, contratos, formularios, correos) es uno de los casos de uso con mayor retorno de inversión en PLN empresarial. Los LLMs modernos son especialmente eficaces en extracción de información compleja que requiere comprensión semántica del documento.

Un LLM puede extraer campos estructurados de una factura en formato JSON a partir de una instrucción:

```
Sistema: Extrae los datos de la siguiente factura en formato JSON con los campos:
{numero_factura, fecha, proveedor, CIF, importe_base, IVA, total, lineas[]}
Factura: [texto de la factura]
```

Los modelos más recientes soportan **structured outputs** o **tool calling** con esquema JSON predefinido, lo que garantiza que la respuesta siempre cumple el esquema esperado, facilitando la integración con sistemas downstream.

### 4.4 Clasificación y enrutamiento

Los LLMs pueden usarse como clasificadores de propósito general para enrutar consultas, clasificar documentos o tomar decisiones de priorización. A diferencia de los clasificadores tradicionales basados en embeddings, los LLMs pueden manejar esquemas de clasificación complejos con muchas categorías y lógica condicional, y no requieren datos de entrenamiento etiquetados para nuevas categorías.

Sin embargo, para clasificación de alto volumen (millones de documentos diarios), el coste y la latencia de los LLMs los hace inviables. En estos casos, los LLMs se usan para generar datos de entrenamiento para modelos más pequeños y especializados.

---

## 5. Análisis de requisitos funcionales y no funcionales

### 5.1 Requisitos funcionales

Los requisitos funcionales de un sistema LLM describen qué debe hacer el sistema:

| Dimensión | Preguntas clave | Ejemplo |
|---|---|---|
| Idiomas | ¿Qué idiomas debe soportar? ¿Con qué nivel de calidad? | Español e inglés de forma nativa; francés como secundario |
| Longitud de contexto | ¿Cuál es la longitud máxima de los documentos de entrada? | Contratos de hasta 200 páginas (~150K tokens) |
| Modalidades de entrada | ¿Texto, imagen, audio, vídeo, combinaciones? | Texto e imagen (facturas escaneadas) |
| Tipo de output | ¿Texto libre, JSON estructurado, código, clasificación? | JSON estructurado con esquema definido |
| Capacidades específicas | ¿Razonamiento complejo, generación de código, matemáticas? | Análisis de cláusulas contractuales |
| Tono y estilo | ¿El sistema tiene restricciones de estilo de comunicación? | Formal, sin lenguaje coloquial |

### 5.2 Requisitos no funcionales

| Dimensión | Métricas | Valores típicos |
|---|---|---|
| Latencia | Time-to-first-token (TTFT), latencia total p50/p95 | TTFT < 1s, latencia total < 5s p95 |
| Throughput | Tokens/segundo, requests/segundo concurrentes | 1000 tokens/s, 100 req concurrentes |
| Disponibilidad | Uptime SLA | 99.9% (8.7 h downtime/año) |
| Privacidad de datos | ¿Los datos pueden salir de la infraestructura? | Datos de RRHH: solo hosting propio |
| Coste por unidad | Coste por 1000 tokens de input/output | < 1 € por 1M tokens output |
| Seguridad del modelo | Resistencia a jailbreaking, inyección de prompts | Validación de outputs, filtros de contenido |
| Trazabilidad | Logging de inputs/outputs para auditoría | 100% de las interacciones registradas |

### 5.3 Longitud de contexto y sus implicaciones técnicas

La **context window** (ventana de contexto) define la cantidad máxima de texto que el modelo puede procesar en una sola interacción. Es uno de los parámetros más determinantes para la selección del modelo porque tiene implicaciones directas en:

- **Casos de uso habilitados**: un modelo con 4K tokens de contexto no puede analizar contratos completos; uno con 128K sí puede.
- **Consumo de VRAM**: el mecanismo de atención de los Transformers requiere almacenar la KV cache para todos los tokens del contexto. A mayor contexto activo, mayor consumo de VRAM (proporcional a la longitud del contexto × número de capas × dimensión de la clave).
- **Latencia**: la latencia de inferencia crece con la longitud del contexto porque cada token generado debe atender a todos los tokens previos.
- **Coste por inferencia**: en modelos de API, el coste se factura típicamente por tokens de input (que incluyen el contexto completo) y output. Un sistema RAG con 10K tokens de contexto por query a GPT-4o cuesta aproximadamente 0.025 € por query, lo que escala a 25.000 € por millón de consultas.

---

## 6. Benchmarks de evaluación

### 6.1 MMLU (Massive Multitask Language Understanding)

**MMLU** evalúa el conocimiento en 57 áreas del conocimiento mediante preguntas de opción múltiple: ciencias, humanidades, matemáticas, ciencias sociales, ciencias de la computación, derecho, medicina, economía, etc. Es el benchmark de referencia para evaluar el conocimiento general de un modelo. Los mejores modelos (GPT-4o, Claude 3.5 Sonnet) alcanzan scores superiores al 85% en MMLU. MMLU 5-shot (el modelo ve 5 ejemplos antes de la pregunta) es la configuración estándar de comparación.

**Limitaciones**: MMLU mide conocimiento factual de opción múltiple, no capacidad de razonamiento complejo, generación de texto largo o seguimiento de instrucciones. Un modelo puede tener MMLU alto y ser un asistente mediocre.

### 6.2 HumanEval

**HumanEval** (OpenAI, 2021) evalúa la capacidad de generación de código Python. Contiene 164 problemas de programación con descripción en lenguaje natural y tests unitarios automáticos. La métrica es pass@k: el porcentaje de problemas resueltos correctamente en k intentos. Pass@1 (el modelo resuelve correctamente a la primera) es el estándar de comparación.

Los mejores modelos especializados en código (GPT-4o, Claude 3.5 Sonnet, DeepSeek-Coder V2) alcanzan pass@1 > 90%. Modelos open-source como Llama 3.1 70B o Qwen 2.5 Coder 72B superan el 80%.

### 6.3 MT-Bench y LMSYS Chatbot Arena

**MT-Bench** evalúa la calidad de los asistentes conversacionales mediante 80 preguntas en 8 categorías: razonamiento, matemáticas, escritura, roleplay, extracción de información, STEM, humanidades, y codificación. Las respuestas son evaluadas automáticamente por GPT-4 en una escala de 1 a 10. Captura mejor que MMLU la calidad de la experiencia de conversación.

**LMSYS Chatbot Arena** es una plataforma de evaluación humana: usuarios reales interactúan con dos modelos anónimos simultáneamente y votan cuál responde mejor. El ranking resultante (Elo) refleja la preferencia humana en condiciones reales y es considerado uno de los benchmarks más fiables. Disponible en: [https://lmsys.org/blog/2023-05-03-arena/](https://lmsys.org/blog/2023-05-03-arena/)

### 6.4 HELM (Holistic Evaluation of Language Models)

**HELM** (Stanford, 2022) es el marco de evaluación más comprehensivo: evalúa 30 modelos en 42 escenarios con 7 métricas (exactitud, calibración, robustez, equidad, sesgo, toxicidad, eficiencia). Su carácter multidimensional permite identificar que un modelo puede ser excelente en precisión y tener problemas de sesgo o toxicidad que lo hacen inadecuado para ciertos usos.

### 6.5 Limitaciones de los benchmarks

Los benchmarks de evaluación de LLMs tienen limitaciones sistémicas importantes que el profesional debe conocer:

- **Contaminación del benchmark**: si los datos del benchmark forman parte del corpus de entrenamiento del modelo, las métricas están infladas artificialmente.
- **Distribución shift**: un modelo que sobresale en MMLU puede tener rendimiento mediocre en el dominio específico del caso de uso.
- **Métricas proxy**: el score en un benchmark es una aproximación al rendimiento real; no debe usarse como único criterio de selección.
- **Evaluación humana como gold standard**: ningún benchmark automático sustituye a la evaluación humana sobre tareas representativas del caso de uso concreto.

---

## 7. Análisis de coste total de propiedad (TCO)

### 7.1 Modelo de coste: API propietaria

El coste de usar un LLM via API tiene tres componentes:

1. **Coste de tokens**: los proveedores cobran por millón de tokens de input y output. Los tokens de input incluyen el prompt completo (instrucciones del sistema + contexto + mensaje del usuario); los de output, la respuesta generada.

```
Ejemplo: Sistema de Q&A con RAG sobre documentos
- Tokens de input por query: 3.000 (instrucción: 200 + contexto RAG: 2.500 + pregunta: 300)
- Tokens de output por query: 500
- Volumen: 10.000 queries/día = 300.000 queries/mes

Coste mensual con GPT-4o (precios aproximados junio 2024):
- Input: 300.000 × 3.000 tokens × $5/1M tokens = $4.500/mes
- Output: 300.000 × 500 tokens × $15/1M tokens = $2.250/mes
- Total: ~$6.750/mes (~$81.000/año)
```

2. **Coste de integración y mantenimiento**: ingeniería para integrar la API, gestión de errores, rate limiting, monitoring.

3. **Costes indirectos**: riesgo de cambio de precios, discontinuación del modelo, dependencia de disponibilidad del proveedor.

### 7.2 Modelo de coste: hosting propio

El coste de hospedar un LLM open-source tiene componentes diferentes:

1. **Hardware (GPU)**: el coste dominante. Puede ser on-premise (capex + opex de mantenimiento) o cloud (pay-per-use con instancias GPU).

```
Ejemplo: Llama 3.1 70B en cuantización INT4 (≈ 40 GB VRAM)
Hardware requerido: 2× NVIDIA A100 80GB
Opción cloud (AWS p4d.24xlarge, 8× A100): $32/hora
Uso estimado: 16 h/día (workday)
Coste mensual: $32 × 16h × 22 días = $11.264/mes

Capacidad aproximada del servidor:
- Throughput: ~500 tokens/segundo con vLLM
- Queries/día (500 tokens output/query, 16h/día):
  500 tokens/s × 57.600 s / 500 tokens/query = 57.600 queries/día
```

2. **Personal de operaciones**: un ingeniero de MLOps puede gestionar 1-3 clusters LLM en producción. Coste de personal: ~50.000-80.000 €/año.

3. **Infraestructura de soporte**: red, almacenamiento, monitoring, logging.

### 7.3 Matriz de comparación TCO

| Criterio | API propietaria | Hosting propio |
|---|---|---|
| Coste fijo mensual | Bajo (casi cero sin uso) | Alto (infraestructura permanente) |
| Coste variable | Alto (crece linealmente con el uso) | Bajo (infraestructura amortizada) |
| Punto de inflexión | Por debajo de N queries/mes, API es más barata | Por encima de N queries/mes, hosting propio es más barato |
| Tiempo de puesta en marcha | Días | Semanas-meses |
| Control de datos | Bajo (datos en infraestructura del proveedor) | Total (datos no salen de la organización) |
| Mantenimiento | Proveedor | Equipo propio |
| Actualización de modelos | Automática | Manual (proceso de upgrades) |
| Personalización (fine-tuning) | Limitada (algunas APIs lo permiten) | Total |

---

## 8. Restricciones regulatorias por sector

### 8.1 EU AI Act y clasificación de riesgo

El Reglamento (UE) 2024/1689 (EU AI Act) clasifica los sistemas de IA en categorías de riesgo. Los LLMs son clasificados como **modelos de IA de uso general (GPAI)**. Si el modelo tiene un umbral de cómputo de entrenamiento superior a 10^25 FLOPs, se considera GPAI con **riesgo sistémico**, con obligaciones adicionales (evaluaciones adversariales, notificación de incidentes a la Comisión Europea).

Para los **sistemas construidos sobre LLMs** (aplicaciones que usan un LLM como componente), la clasificación de riesgo depende del caso de uso:

- **Alto riesgo** (Anexo III): sistemas de IA para selección de personal, scoring de crédito, evaluación de estudiantes, triaje médico, decisiones en procesos judiciales. Un chatbot de RRHH que filtra candidaturas puede ser de alto riesgo.
- **Riesgo limitado**: chatbots que interactúan con personas deben informar al usuario de que está interactuando con una IA (art. 50 EU AI Act).
- **Riesgo mínimo**: la mayoría de aplicaciones de generación de contenido, asistentes de código, Q&A interno.

### 8.2 RGPD y procesamiento de datos personales

Si el sistema LLM procesa datos personales —un asistente de RRHH que lee CVs, un sistema de Q&A que accede a historias clínicas, un chatbot que recoge información de clientes—, aplica el RGPD en su totalidad:

- Los datos no pueden enviarse a proveedores de API fuera del EEE sin las garantías adecuadas (cláusulas contractuales tipo, decisión de adecuación).
- Los proveedores de API deben actuar como encargados del tratamiento (DPA, Data Processing Agreement) y proporcionar garantías sobre el uso de los datos (en particular, que no se usan para entrenar modelos sin consentimiento).
- Los interesados tienen derechos sobre sus datos (acceso, rectificación, supresión) que el sistema debe poder satisfacer.

### 8.3 Normativa sectorial específica

| Sector | Normativa clave | Restricción principal para LLMs |
|---|---|---|
| Sanidad | RGPD + Reglamento Europeo del Espacio Europeo de Datos de Salud (EHDS) | Los datos de salud (categoría especial) no pueden salir a APIs de terceros sin base legal explícita. Preferencia por modelos locales. |
| Finanzas | PSD2, MiCA, DORA | DORA exige evaluación del riesgo de concentración de proveedores de TI (incluidos proveedores de API de IA). |
| Recursos Humanos | RGPD + Directiva de Transparencia Salarial + EU AI Act (alto riesgo) | Los sistemas de selección de personal son de alto riesgo bajo EU AI Act. Prohibición de análisis de expresiones faciales en procesos de selección. |
| Administración pública | ENS (Esquema Nacional de Seguridad) en España | Los sistemas que procesan información clasificada deben usar infraestructura certificada ENS. APIs de terceros no suelen estar certificadas. |
| Educación | LOPDGDD + normativa autonómica | Restricciones sobre el tratamiento de datos de menores. |

---

## 9. Actividades prácticas

### Actividad 1 — Análisis de requisitos para un caso de uso real

**Descripción**: El formador asignará a cada estudiante (o grupo de dos) un caso de uso empresarial de LLM de entre los siguientes: (a) asistente de Q&A para empleados de una empresa farmacéutica sobre procedimientos internos; (b) sistema de extracción automática de datos de contratos de suministro para un departamento de compras; (c) asistente de código para un equipo de desarrollo de software bancario; (d) chatbot de atención al cliente multilingüe para un e-commerce. Para el caso asignado, completa un documento de análisis de requisitos que cubra: requisitos funcionales (idiomas, contexto, output), requisitos no funcionales (latencia, throughput, privacidad, disponibilidad, coste), restricciones regulatorias aplicables y criterios de selección de modelo priorizados.

**Entregable**: Documento de análisis de requisitos (tres a cuatro páginas) con todas las dimensiones cubiertas.

**Criterios de evaluación**: Completitud de los requisitos, corrección de las restricciones regulatorias identificadas, coherencia entre los requisitos y los criterios de selección, profundidad del análisis.

---

### Actividad 2 — Evaluación comparativa de modelos con benchmarks

**Descripción**: Usando los recursos públicos de LMSYS Chatbot Arena (https://lmsys.org), HELM (https://crfm.stanford.edu/helm/) y los leaderboards de Hugging Face (https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard), recopila los scores actualizados de al menos seis modelos (mezcla de propietarios y open-source) en los benchmarks MMLU, MT-Bench, HumanEval y Arena Elo. Construye una tabla comparativa. Selecciona el mejor modelo para cada uno de los cuatro casos de uso de la actividad anterior, justificando la selección en función de los benchmarks y los requisitos. Identifica al menos dos casos donde el mejor modelo según benchmarks no es el más adecuado para el caso de uso por razones no capturadas por los benchmarks (privacidad, coste, tamaño de contexto, etc.).

**Entregable**: Tabla comparativa de benchmarks + justificación de selección por caso de uso (dos páginas).

**Criterios de evaluación**: Actualidad y precisión de los datos de benchmarks, corrección del razonamiento de selección, calidad de la identificación de limitaciones de los benchmarks.

---

### Actividad 3 — Modelado de TCO

**Descripción**: Para el caso de uso asignado en la actividad 1, construye un modelo de TCO en hoja de cálculo que compare la opción de API propietaria (usando el precio actual del modelo más adecuado) con la opción de hosting propio (usando el modelo open-source más adecuado en una instancia GPU cloud). El modelo debe parametrizar: volumen de queries mensuales, tokens medios por query (input y output), precio por token (API), tipo de instancia GPU (hosting propio), horas de uso por día, coste de personal de operaciones. Calcula el coste mensual total para ambas opciones en tres escenarios de tráfico (bajo, medio, alto) e identifica el punto de inflexión de queries/mes a partir del cual el hosting propio es más económico. Presenta los resultados en un gráfico.

**Entregable**: Hoja de cálculo con el modelo de TCO + gráfico comparativo + recomendación razonada.

**Criterios de evaluación**: Correctitud del modelo de costes, realismo de los parámetros, claridad del gráfico, calidad de la recomendación.

---

### Actividad 4 — Análisis regulatorio y matriz de decisión

**Descripción**: Selecciona un sector de entre sanidad, finanzas, recursos humanos y administración pública. Para ese sector, desarrolla un análisis regulatorio que identifique: las normativas aplicables a un sistema LLM (EU AI Act, RGPD, normativa sectorial), la clasificación de riesgo del sistema bajo el EU AI Act, las restricciones específicas sobre el procesamiento de datos, y las obligaciones técnicas que el sistema debe cumplir. Sobre la base de este análisis, construye una matriz de decisión para la selección de modelo (filas: modelos candidatos; columnas: criterios de selección priorizados con pesos) y justifica el modelo seleccionado para ese sector y caso de uso.

**Entregable**: Análisis regulatorio (dos páginas) + matriz de decisión con puntuaciones y ponderaciones + conclusión razonada.

**Criterios de evaluación**: Precisión del análisis regulatorio, correcta identificación de las obligaciones técnicas, coherencia de la matriz de decisión, calidad de la justificación final.

---

## 10. Referencias

- **EU AI Act (Reglamento (UE) 2024/1689)**: texto completo y documentos de orientación. Disponible en: [https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689)

- **LMSYS Chatbot Arena Leaderboard**: ranking de modelos por preferencia humana en evaluación ciega. Disponible en: [https://lmsys.org/blog/2023-05-03-arena/](https://lmsys.org/blog/2023-05-03-arena/)

- **Open LLM Leaderboard — Hugging Face**: benchmarks automatizados de modelos open-source. Disponible en: [https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard)

- **HELM — Holistic Evaluation of Language Models (Stanford)**: marco de evaluación multidimensional. Disponible en: [https://crfm.stanford.edu/helm/](https://crfm.stanford.edu/helm/)

- **MMLU — Massive Multitask Language Understanding**: artículo original y datos del benchmark. Disponible en: [https://github.com/hendrycks/test](https://github.com/hendrycks/test)

- **HumanEval — Evaluating Large Language Models Trained on Code**: artículo y dataset. Disponible en: [https://github.com/openai/human-eval](https://github.com/openai/human-eval)

- **Llama 3 — Model Card y licencia de Meta**: documentación técnica y condiciones de uso. Disponible en: [https://ai.meta.com/blog/meta-llama-3/](https://ai.meta.com/blog/meta-llama-3/)

- **Mistral AI — Documentación de modelos**: características técnicas y precios. Disponible en: [https://docs.mistral.ai/getting-started/models/](https://docs.mistral.ai/getting-started/models/)

- **Qwen 2.5 — Alibaba Cloud**: ficha técnica y acceso al modelo. Disponible en: [https://qwenlm.github.io/](https://qwenlm.github.io/)

- **OpenAI API Pricing**: precios actualizados de tokens por modelo. Disponible en: [https://openai.com/api/pricing](https://openai.com/api/pricing)

- **AESIA — Guías sobre el EU AI Act para empresas**: orientación práctica sobre clasificación de riesgo. Disponible en: [https://www.aesia.gob.es/](https://www.aesia.gob.es/)

- **AEPD — Guía sobre IA y protección de datos**: implicaciones del RGPD en sistemas de IA. Disponible en: [https://www.aepd.es/guias/guia-inteligencia-artificial-y-proteccion-de-datos.pdf](https://www.aepd.es/guias/guia-inteligencia-artificial-y-proteccion-de-datos.pdf)

---

*UD1 · MP04 Infraestructura para la ejecución de LLMs · CFS2 Instalación, despliegue y explotación de sistemas de IA*
