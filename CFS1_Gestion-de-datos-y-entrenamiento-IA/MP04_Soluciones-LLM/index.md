---
marp: true
theme: default
paginate: true
size: 16:9
header: 'MP04 · Soluciones basadas en modelos de lenguaje (LLMs)'
footer: 'CFS Gestión de datos y entrenamiento IA (IAD)'
---

<style>
section { font-family: 'Segoe UI', Arial, sans-serif; }
h1 { color: #1e3a5f; }
h2 { color: #1e3a5f; border-bottom: 2px solid #3b82f6; padding-bottom: 6px; }
h3 { color: #2563eb; }
table { font-size: 0.82em; width: 100%; }
ul, ol { font-size: 0.88em; }
blockquote { border-left: 4px solid #3b82f6; background: #eff6ff; padding: 8px 16px; border-radius: 4px; }
footer, header { font-size: 0.6em; color: #6b7280; }
section.lead h1 { font-size: 2.2em; text-align: center; margin-top: 100px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
</style>

<!-- _class: lead -->

# MP04 · Soluciones basadas en modelos de lenguaje (LLMs)

CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Ficha del módulo

| Campo | Valor |
|---|---|
| Código | **MP04** |
| Estándar de competencia | CPE_5054_3 · Nivel 3 |
| Familia profesional | Inteligencia Artificial y Data |
| Duración | **160 h** |
| Curso | **2.º** |

> **Competencia que desarrolla:** gestionar soluciones basadas en modelos de lenguaje de gran tamaño (LLMs), desde la planificación y el despliegue hasta la supervisión de agentes autónomos y su integración con otros sistemas, asegurando funcionamiento, seguridad y trazabilidad.

---

## Estructura del módulo

| # | Unidad didáctica |
|---|---|
| **UD1** | Análisis del caso de uso y selección del modelo |
| **UD2** | Componentes de interacción con el modelo |
| **UD3** | Integración con fuentes, herramientas y sistemas (RAG) |
| **UD4** | Comportamientos agénticos |
| **UD5** | Validación y puesta en servicio |
| **UD6** | Seguridad, privacidad y uso ético |
| **UD7** | Vigilancia tecnológica de LLMs |
| **UD8** | Responsabilidad profesional, sostenibilidad y prevención |

---

<!-- _class: lead -->

# UD1
## Análisis del caso de uso y selección del modelo

---

## UD1 · Interpretación del caso de uso

**Preguntas a responder antes de seleccionar un modelo:**

- ¿Cuál es el **objetivo funcional** exacto? (resumir, clasificar, generar, extraer…)
- ¿Quiénes son los **usuarios finales** y qué nivel técnico tienen?
- ¿Qué **tipo de interacción** se espera? (chat, API, batch, embed)
- ¿Qué **datos de entrada** se proporcionan al modelo?
- ¿Cuáles son las **restricciones** de latencia, privacidad y coste?
- ¿Qué **resultados esperados** se deben cumplir para considerar el sistema válido?

---

## UD1 · Criterios de selección del modelo LLM

| Criterio | Qué evaluar |
|---|---|
| **Modalidad** | Texto, audio, imagen, vídeo, multimodal |
| **Capacidades lingüísticas** | Idioma(s), nivel de especialización |
| **Longitud de contexto** | Ventana de tokens disponibles (8k, 32k, 128k…) |
| **Coste** | Por token de entrada/salida o licencia de uso |
| **Latencia** | Tiempo de respuesta admisible para el caso de uso |
| **Privacidad** | Local, API de terceros, VPC, modelo propio |
| **Especialización** | General vs. dominio (médico, legal, código) |

---

## UD1 · Parámetros de generación

| Parámetro | Efecto |
|---|---|
| **Temperatura** | Controla aleatoriedad (0 = determinista, 1+ = creativo) |
| **Top-p / Top-k** | Restringe el vocabulario de muestreo |
| **Max tokens** | Límite de longitud de la respuesta |
| **Criterios de parada** | Tokens de fin, secuencias de parada personalizadas |
| **Penalizaciones** | Evitar repeticiones de tokens o temas |
| **Formato de salida** | JSON, Markdown, texto libre, esquema estructurado |

**Registrar:** limitaciones funcionales, capacidades reales vs. esperadas, supuestos del sistema.

---

<!-- _class: lead -->

# UD2
## Componentes de interacción con el modelo

---

## UD2 · Diseño de prompts y plantillas

**Estructura de un prompt efectivo:**

```
[SISTEMA]  Define el rol, tono y restricciones del modelo.
           Ejemplo: "Eres un asistente técnico especializado en..."

[CONTEXTO] Información relevante para la tarea actual.
           Ejemplo: fragmentos de documentos, datos del usuario...

[INSTRUCCIÓN] Tarea concreta a realizar.
           Ejemplo: "Resume el siguiente texto en 3 puntos..."

[FORMATO]  Estructura esperada de la respuesta.
           Ejemplo: JSON con campos: resumen, puntos_clave, tono
```

---

## UD2 · Gestión del contexto y comunicación con la API

**Gestión del contexto:**
- Controlar el historial de conversación (¿cuántos turnos mantener?)
- Priorizar información relevante cuando el contexto es limitado
- Resumir el historial largo para liberar espacio de contexto

**Comunicación con el modelo:**
```python
import anthropic
client = anthropic.Anthropic()
respuesta = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    system="Eres un asistente técnico...",
    messages=[{"role": "user", "content": "¿Qué es RAG?"}]
)
```

**Control de errores:** timeouts · reintentos con backoff exponencial · límites de uso

---

<!-- _class: lead -->

# UD3
## Integración con fuentes, herramientas y sistemas (RAG)

---

## UD3 · Arquitectura RAG (Retrieval-Augmented Generation)

**Flujo de una arquitectura RAG:**

```
1. INDEXACIÓN (offline)
   Documentos → Fragmentación → Embeddings → Vector DB

2. RECUPERACIÓN (en cada consulta)
   Consulta del usuario → Embedding → Búsqueda semántica
   → Top-K fragmentos relevantes

3. GENERACIÓN (en cada consulta)
   Fragmentos + Consulta + Prompt → LLM → Respuesta fundamentada
```

**Ventaja:** el modelo responde con información actualizada y trazable, reduciendo alucinaciones.

---

## UD3 · Técnicas de recuperación y fragmentación

**Fragmentación de documentos:**

| Estrategia | Cuándo usarla |
|---|---|
| **Por tokens fijos** | Documentos homogéneos, texto continuo |
| **Por párrafos / secciones** | Documentos estructurados |
| **Semántica** | Preservar coherencia de ideas |
| **Recursiva** | Jerarquías de contenido (libro → capítulo → párrafo) |

**Recuperación:**
- **Búsqueda vectorial:** similitud coseno en embeddings (FAISS, Pinecone, Chroma)
- **Búsqueda léxica:** BM25, TF-IDF
- **Híbrida:** combina ambas + *reranking*

---

## UD3 · Integración con herramientas y canales

**Herramientas externas (*tool use* / *function calling*):**
- Definir las herramientas disponibles para el modelo (calculadora, buscador, API…)
- Validar permisos y credenciales antes de ejecutar
- Controlar el formato de intercambio de datos (entrada y salida de la herramienta)

**Canales de integración:**

| Canal | Consideraciones |
|---|---|
| Web / móvil | Gestión de sesión, autenticación, UX |
| Chat corporativo (Teams, Slack) | OAuth, webhooks, límites de mensaje |
| API propia | Versionado, autenticación, rate limiting |
| Redes sociales | Moderación, filtros de contenido |

---

<!-- _class: lead -->

# UD4
## Comportamientos agénticos

---

## UD4 · Definición del agente

**Componentes de un agente LLM:**

| Componente | Descripción |
|---|---|
| **Objetivo** | Qué debe conseguir el agente en cada ejecución |
| **Herramientas** | Funciones que puede invocar (buscador, código, APIs) |
| **Memoria operativa** | Información que el agente conserva entre pasos |
| **Límites de autonomía** | Qué puede hacer solo vs. qué requiere confirmación humana |
| **Condiciones de finalización** | Cuándo considerar la tarea completada |
| **Protocolo de escalado** | Cómo actuar si el agente no puede resolver algo |

---

## UD4 · Límites de autonomía y validación

**Jerarquía de autonomía:**

```
Acción prohibida        → el agente nunca puede ejecutarla
Acción con confirmación → requiere aprobación humana explícita
Acción autónoma         → el agente puede ejecutarla directamente
```

**Validación del comportamiento agéntico:**
- Pruebas con instrucciones contradictorias o ambiguas
- Detección de bucles infinitos (límite de pasos máximos)
- Escenarios de escalado cuando la confianza es baja
- Protocolos de parada segura y reversión de acciones

---

<!-- _class: lead -->

# UD5
## Validación y puesta en servicio

---

## UD5 · Diseño de casos de prueba

**Tipos de prueba para soluciones LLM:**

| Tipo | Qué verificar |
|---|---|
| **Funcional** | Respuestas correctas en el caso de uso principal |
| **Consultas complejas** | Razonamiento multi-paso, instrucciones compuestas |
| **Fuera de alcance** | El sistema reconoce lo que no sabe |
| **Variaciones lingüísticas** | Sinónimos, errores tipográficos, distintos idiomas |
| **Condiciones límite** | Entradas vacías, muy largas, con caracteres especiales |
| **Adversarial** | Intentos de manipulación del sistema (*jailbreak*) |

---

## UD5 · Métricas de evaluación y ajuste

**Métricas de calidad de respuesta:**

| Dimensión | Descripción |
|---|---|
| **Pertinencia** | La respuesta responde a la pregunta formulada |
| **Coherencia** | La respuesta es internamente consistente |
| **Completitud** | Cubre todos los aspectos requeridos |
| **Trazabilidad** | Se puede verificar el origen de la información |
| **Formato** | Cumple el formato y estructura solicitados |

**Proceso de ajuste:** modificar instrucciones → cambiar parámetros → ampliar contexto → mejorar fuentes → registrar versión.

---

## UD5 · Documentación de puesta en servicio

**Entregables al poner en servicio:**

- 📄 **Documentación técnica:** arquitectura, componentes, APIs, dependencias
- 📘 **Manual operativo:** procedimientos de operación, monitorización, escalado
- 👤 **Guía de uso:** para el equipo que va a operar la solución
- 🔧 **Soporte continuo:** canal de reporte de incidencias, SLA acordado
- 📊 **Registro de versiones probadas:** configuración, métricas, ciclo de resolución

---

<!-- _class: lead -->

# UD6
## Seguridad, privacidad y uso ético

---

## UD6 · Riesgos del uso de LLMs

| Riesgo | Descripción | Mitigación |
|---|---|---|
| **Alucinaciones** | El modelo genera información falsa con apariencia real | Verificación con RAG, citación de fuentes |
| **Sesgos** | Respuestas discriminatorias o estereotipadas | Pruebas de equidad, filtros de salida |
| **Toxicidad** | Contenido dañino o inapropiado | Moderación de contenido, clasificadores |
| **Dependencia excesiva** | El usuario acepta todo sin verificar | Indicar limitaciones, promover revisión humana |
| **Fuga de datos** | Datos sensibles en el prompt llegan al proveedor | Filtrar antes de enviar, usar modelos locales |

---

## UD6 · Controles de acceso y trazabilidad

**Control de accesos:**
- **Mínimo privilegio:** cada componente accede solo a lo que necesita
- **Separación de funciones:** quién puede leer, escribir, ejecutar, administrar
- **Gestión de credenciales:** nunca en código; usar *secrets managers* (*Vault*, AWS Secrets)
- **Trazabilidad:** registrar cada petición con usuario, timestamp, versión del modelo y respuesta

**Marcos de autonomía controlada:**
- Cuotas de uso por usuario o servicio
- Umbrales de confianza para ejecutar acciones irreversibles
- Protocolos de parada y escalado ante comportamientos inesperados

---

<!-- _class: lead -->

# UD7
## Vigilancia tecnológica de LLMs

---

## UD7 · Fuentes y proceso de vigilancia

**Fuentes prioritarias:**

| Fuente | Contenido |
|---|---|
| Documentación oficial de proveedores | Changelogs, nuevas capacidades, precios |
| HuggingFace Hub / Papers with Code | Modelos open source, benchmarks |
| OWASP LLM Top 10 | Vulnerabilidades de seguridad en LLMs |
| Comunidades (Discord, Reddit) | Casos de uso reales, bugs conocidos |
| Boletines de seguridad | CVEs, avisos de proveedores |

**Proceso:** recopilar periódicamente → analizar relevancia y aplicabilidad → proponer mejoras → reportar formalmente

---

## UD7 · Análisis de aplicabilidad y reporte

**Criterios para evaluar una novedad:**

1. ¿Mejora el rendimiento o reduce costes en mis casos de uso actuales?
2. ¿El coste de adopción (tiempo, dependencias, riesgo) es asumible?
3. ¿Es compatible con los requisitos legales y de privacidad?
4. ¿Existe evidencia de uso en producción o solo en investigación?

**Reporte formal de vigilancia:**
- Resumen ejecutivo de novedades relevantes del periodo
- Propuestas de mejora, actualización o sustitución justificadas
- Priorización según impacto esperado y esfuerzo

---

<!-- _class: lead -->

# UD8
## Responsabilidad profesional, sostenibilidad y prevención

---

## UD8 · Responsabilidad y comunicación

**Principios de responsabilidad profesional:**
- **Rigor técnico:** verificar los resultados antes de comunicarlos
- **Integridad ética:** reportar limitaciones y errores sin ocultarlos
- **Comunicación asertiva e inclusiva:** adaptar el mensaje según el perfil del destinatario
- **Transmisión comprensible:** explicar las capacidades y limitaciones de la IA a usuarios no técnicos

---

## UD8 · Sostenibilidad y prevención

**Sostenibilidad en el uso de LLMs:**
- Seleccionar modelos y arquitecturas que reducen el número de tokens y peticiones
- Minimizar el contexto enviado al modelo a lo estrictamente necesario
- Reutilizar respuestas en caché cuando el input no varía (semantic caching)
- Principio **DNSH** y ODS: medir y reducir emisiones de CO₂ de las llamadas a la API

**PRL — Prevención de riesgos laborales:**

| Riesgo | Medida |
|---|---|
| Tecnoestrés | Desconexión programada, organización realista de tareas |
| Fatiga cognitiva | Documentar para no depender de la memoria |
| Ergonomía | Mobiliario ajustable, periféricos ergonómicos |

---

## Criterios de evaluación — MP04

- Interpreta el caso de uso y selecciona el modelo con criterios técnicos
- Define *prompts* y gestión de contexto; controla errores en la API
- Configura mecanismos de recuperación RAG e integra herramientas y canales
- Define objetivos y límites de autonomía del agente; valida la lógica operativa
- Define y ejecuta casos de prueba; ajusta la solución y formaliza la puesta en servicio
- Evalúa riesgos, filtra datos sensibles y valida controles con pruebas adversariales
- Selecciona fuentes de vigilancia y reporta propuestas de mejora
- Integra sostenibilidad en las decisiones técnicas y aplica medidas de prevención

---

<!-- _class: lead -->

# MP04 · Soluciones basadas en modelos de lenguaje (LLMs)

**160 h · Curso 2.º · CPE_5054_3 · Nivel 3**

*CFS — Gestión de datos y entrenamiento IA (IAD)*
