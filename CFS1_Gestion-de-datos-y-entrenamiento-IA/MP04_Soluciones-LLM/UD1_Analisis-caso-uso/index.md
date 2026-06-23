---
marp: true
theme: default
paginate: true
size: 16:9
header: 'MP04 · UD1 · Análisis del caso de uso y selección del modelo'
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
section.lead h1 { font-size: 2em; text-align: center; margin-top: 80px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
pre { background: #1e293b; color: #e2e8f0; padding: 16px; border-radius: 8px; font-size: 0.8em; }
</style>

<!-- _class: lead -->

# UD1 · Análisis del caso de uso y selección del modelo

**MP04 · Soluciones basadas en LLMs**
CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Interpretar un caso de uso de negocio para extraer los requisitos técnicos que condicionan la selección del modelo.
- Aplicar criterios técnicos y operativos comparados para elegir el LLM o servicio más adecuado.
- Configurar correctamente los parámetros de generación en función del caso de uso.
- Registrar las limitaciones funcionales y los supuestos del sistema de forma estructurada.

---

## 1 · Interpretación del caso de uso (I)

### El caso de uso como punto de partida

Antes de seleccionar ningún modelo es imprescindible comprender el problema que se quiere resolver. Un caso de uso de LLM se describe a través de seis dimensiones:

| Dimensión | Pregunta clave |
|---|---|
| **Objetivo funcional** | ¿Qué debe hacer exactamente el sistema? (resumir, clasificar, generar, extraer, traducir…) |
| **Usuarios** | ¿Quiénes interactúan con él y qué nivel técnico tienen? |
| **Tipo de interacción** | ¿Chat conversacional, API batch, embed en app, procesamiento offline? |
| **Datos de entrada** | ¿Qué información llega al modelo? ¿Textos, PDFs, transcripciones, tablas? |
| **Restricciones** | Latencia máxima, presupuesto, normativa de privacidad, idioma |
| **Resultados esperados** | ¿Qué criterio define que el sistema funciona correctamente? |

---

## 1 · Interpretación del caso de uso (II)

### Tipos de tareas y su impacto en la selección

| Tarea | Característica dominante | Implicación |
|---|---|---|
| Resumen de documentos | Ventana de contexto larga | Necesita modelo con 32k+ tokens |
| Clasificación de soporte | Alta velocidad, bajo coste | Modelo pequeño o destilado |
| Generación de código | Precisión y razonamiento | Modelo especializado o SOTA |
| Asistente multiturno | Gestión de historial | Modelo con buen instruction-following |
| Extracción estructurada | Salida en JSON fiable | Modelo con function calling o structured output |
| Procesamiento de audio | Modalidad no textual | Modelo multimodal o pipeline ASR+LLM |

> Un mismo proyecto puede combinar varias tareas, lo que obliga a evaluar si se usa un único modelo o una arquitectura multi-modelo.

---

## 1 · Interpretación del caso de uso (III)

### Análisis de restricciones y condiciones de contorno

Las restricciones delimitan el espacio de soluciones válidas. Se deben identificar antes de evaluar modelos:

**Restricciones técnicas:**
- Latencia máxima tolerable (ej. < 2 s para un chat de atención al cliente)
- Tamaño máximo de la entrada (documentos de hasta X páginas)
- Formato obligatorio de la salida (ej. siempre JSON para integración con ERP)

**Restricciones normativas y de negocio:**
- Datos personales que no pueden salir de la UE (RGPD) → descarta APIs en servidores externos
- Información clasificada o secreto comercial → requiere modelo local o VPC privada
- Presupuesto mensual máximo en llamadas a la API

**Restricciones de usuario:**
- Idioma principal de la interacción
- Nivel de tolerancia a respuestas incorrectas (dominio médico vs. ocio)

---

## 2 · Criterios de selección del modelo (I)

### Marco de decisión técnica

La selección del modelo es una decisión de ingeniería, no de preferencia. Se evalúan estos criterios:

| Criterio | Qué medir | Cómo obtener el dato |
|---|---|---|
| **Modalidad** | Texto, audio, imagen, vídeo, multimodal | Ficha técnica del modelo |
| **Capacidades lingüísticas** | Idiomas soportados, nivel de español | Benchmarks MMLU-ES, HellaSwag |
| **Ventana de contexto** | Tokens de entrada + salida (8k, 32k, 128k…) | Documentación oficial |
| **Coste por token** | USD por 1M tokens entrada / salida | Página de precios del proveedor |
| **Latencia** | Tiempo medio de primera respuesta (TTFT) | Tests propios o benchmarks públicos |
| **Disponibilidad** | SLA del proveedor, regiones disponibles | Acuerdo de nivel de servicio |
| **Especialización** | General vs. dominio (médico, legal, código) | Benchmarks de dominio específico |

---

## 2 · Criterios de selección del modelo (II)

### Comparativa de modalidades de despliegue

| Modalidad | Ventajas | Inconvenientes |
|---|---|---|
| **API de proveedor** (OpenAI, Anthropic, Google…) | Sin infraestructura, actualizaciones automáticas, SLA garantizado | Datos enviados a terceros, coste variable, dependencia del proveedor |
| **Modelo open source autoalojado** (Llama, Mistral, Qwen…) | Control total de datos, coste fijo de hardware | Requiere GPUs, mantenimiento propio, actualizaciones manuales |
| **API privada / VPC** | Datos en entorno controlado, SLA del proveedor | Coste elevado, configuración compleja |
| **Fine-tuned / adaptado** | Máximo rendimiento en dominio específico | Requiere datos etiquetados, coste de entrenamiento |

> La decisión no es definitiva: es posible empezar con una API pública y migrar a un modelo propio cuando el volumen lo justifique.

---

## 2 · Criterios de selección del modelo (III)

### Evaluación práctica: pasos para comparar modelos

1. **Definir el benchmark de referencia** con 20-50 entradas representativas del caso de uso real.
2. **Ejecutar los modelos candidatos** con los mismos prompts y parámetros base.
3. **Evaluar las salidas** según las dimensiones de calidad relevantes (precisión, formato, completitud).
4. **Medir el coste y la latencia** de cada modelo en esas mismas pruebas.
5. **Registrar los resultados** en una tabla comparativa y justificar la selección final.

```
Modelo           | Precisión | Latencia  | Coste/1M tokens | Idioma ES
-----------------|-----------|-----------|-----------------|----------
Proveedor A (L)  |   87 %    |  1.2 s    |   $3.00/$15.00  |  Bueno
Proveedor B (M)  |   81 %    |  0.6 s    |   $0.60/$2.40   |  Muy bueno
Open source 7B   |   72 %    |  2.1 s*   |   Infra propia  |  Regular
```
`* en hardware propio (A100)`

---

## 3 · Parámetros de generación (I)

### Control del comportamiento del modelo

Los parámetros de generación determinan cómo el modelo produce la respuesta. Deben configurarse específicamente para cada caso de uso:

| Parámetro | Rango habitual | Efecto |
|---|---|---|
| **Temperatura** | 0.0 – 2.0 | Controla aleatoriedad. 0 = determinista; valores altos = más creatividad y variabilidad |
| **Top-p (nucleus sampling)** | 0.0 – 1.0 | Solo considera los tokens cuya probabilidad acumulada alcanza p. Complementa temperatura |
| **Top-k** | 1 – 100 | Limita el vocabulario de muestreo a los k tokens más probables |
| **Max tokens** | 1 – límite del modelo | Longitud máxima de la respuesta generada |
| **Penalización de presencia** | -2.0 – 2.0 | Penaliza tokens ya aparecidos en el texto. Reduce repeticiones |
| **Penalización de frecuencia** | -2.0 – 2.0 | Penaliza tokens proporcionalmente a su frecuencia de aparición |

---

## 3 · Parámetros de generación (II)

### Configuraciones recomendadas por tipo de tarea

| Caso de uso | Temperatura | Top-p | Max tokens | Notas |
|---|---|---|---|---|
| Extracción de datos / JSON | 0.0 – 0.2 | 0.9 | Limitado | Salida determinista y estructurada |
| Resumen técnico | 0.2 – 0.4 | 0.9 | Moderado | Precisión sobre creatividad |
| Asistente de soporte | 0.4 – 0.6 | 0.95 | Moderado | Equilibrio entre variedad y fiabilidad |
| Generación de contenido | 0.7 – 1.0 | 1.0 | Alto | Maximizar diversidad |
| Brainstorming / ideas | 1.0 – 1.5 | 1.0 | Moderado | Alta variedad; filtrar manualmente |

**Criterios de parada personalizados:**
- Secuencias de parada (`stop sequences`): cadenas que indican al modelo que debe detenerse (ej. `"###"`, `"</respuesta>"`)
- Útiles para extraer solo la parte relevante de la respuesta en formatos estructurados

---

## 3 · Parámetros de generación (III)

### Mensajes de sistema y formato de salida

El **mensaje de sistema** (`system prompt`) es la instrucción de nivel superior que condiciona toda la interacción:

```
Eres un asistente especializado en análisis de contratos jurídicos españoles.
Tu tarea es extraer las cláusulas relevantes en formato JSON.
Responde SIEMPRE en español formal.
No inventes información que no esté en el documento proporcionado.
Si no encuentras la información solicitada, devuelve null en ese campo.
```

**Formato de salida estructurado:**
- JSON Schema: permite especificar el esquema exacto que debe seguir la respuesta
- Modo JSON nativo (OpenAI, Anthropic): el modelo garantiza salida JSON válida
- Markdown estructurado: útil para documentos con secciones predefinidas

---

## 4 · Registro de limitaciones funcionales

### Documentar lo que el sistema no puede hacer

El registro de limitaciones es tan importante como la documentación de capacidades. Debe incluir:

**Limitaciones del modelo seleccionado:**
- Ventana de contexto máxima y cómo afecta al caso de uso
- Idiomas o dominios con rendimiento inferior al esperado
- Tipos de razonamiento donde el modelo comete errores sistemáticos

**Supuestos del sistema:**
- El usuario proporciona entradas en español (si hay otra lengua, el comportamiento no está garantizado)
- Los documentos de entrada no superan X páginas
- La latencia se mide en condiciones de carga normal, no en picos

**Escenarios que requieren supervisión humana:**
- Respuestas que afectan a decisiones de alto impacto (médicas, legales, financieras)
- Casos donde la confianza del sistema es baja (sin información suficiente)
- Peticiones fuera del alcance definido del sistema

---

## Actividad practica · UD1

### Analisis y seleccion de modelo para un caso real

**Enunciado:**

Una empresa de logistica quiere desplegar un asistente interno que responda preguntas de sus empleados sobre el manual de procedimientos operativos (500 paginas, actualizado trimestralmente). Las respuestas deben citarse con la seccion del manual de origen. El sistema estara disponible via Slack. La empresa opera en Espana y tiene requisitos RGPD: los datos no pueden salir de la UE.

**Tareas:**

1. Identifica las seis dimensiones del caso de uso (objetivo, usuarios, interaccion, datos, restricciones, resultados esperados).
2. Determina que modalidad de despliegue es viable dado el requisito RGPD.
3. Propone dos modelos candidatos con justificacion tecnica.
4. Define los parametros de generacion recomendados (temperatura, max tokens, formato de salida).
5. Redacta el registro de limitaciones del sistema propuesto (minimo tres limitaciones y dos supuestos).

**Entregable:** documento de analisis de una pagina + tabla de comparativa de modelos.

---

## Puntos clave · UD1

- El caso de uso define los requisitos; el modelo se selecciona para cumplirlos, no al contrario.
- Las seis dimensiones de analisis (objetivo, usuarios, interaccion, datos, restricciones, resultados) estructuran cualquier proyecto LLM.
- La modalidad de despliegue (API publica, open source, VPC) es la primera decision condicionada por privacidad y coste.
- La temperatura controla la aleatoriedad: baja para extraccion y clasificacion, alta para generacion creativa.
- Los mensajes de sistema son el mecanismo principal para delimitar el comportamiento del modelo.
- Registrar limitaciones y supuestos es parte del entregable tecnico, no una tarea secundaria.

---

## Criterios de evaluacion · UD1

| Criterio | Indicadores de logro |
|---|---|
| **Interpreta el caso de uso** | Identifica las seis dimensiones con precision; detecta restricciones implicitas |
| **Selecciona el modelo con criterios tecnicos** | Justifica la eleccion con datos comparativos de coste, latencia, contexto y privacidad |
| **Configura los parametros de generacion** | Elige temperatura, max tokens y formato adecuados al caso; justifica cada valor |
| **Registra limitaciones** | Documenta al menos tres limitaciones reales y dos supuestos del sistema |

---

<!-- _class: lead -->

[← Volver a MP04](../index.md)


---

<!-- nav-slide -->

## Navegación

[Volver al módulo](../) &nbsp;·&nbsp; [UD2 · Componentes de interaccion co… →](../UD2_Componentes-interaccion/)
