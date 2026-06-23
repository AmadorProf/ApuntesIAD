---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD1 · Análisis de requisitos del sistema LLM | MP04 · Infraestructura para la ejecución de LLMs'
footer: 'CFS Instalación, despliegue y explotación de sistemas de IA (IAD)'
---

<style>
section { font-family: 'Segoe UI', Arial, sans-serif; }
h1 { color: #1e3a5f; }
h2 { color: #1e3a5f; border-bottom: 2px solid #10b981; padding-bottom: 6px; }
h3 { color: #059669; }
table { font-size: 0.82em; width: 100%; }
ul, ol { font-size: 0.88em; }
blockquote { border-left: 4px solid #10b981; background: #ecfdf5; padding: 8px 16px; border-radius: 4px; }
footer, header { font-size: 0.6em; color: #6b7280; }
section.lead h1 { font-size: 2em; text-align: center; margin-top: 80px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
pre { background: #1e293b; color: #e2e8f0; padding: 16px; border-radius: 8px; font-size: 0.8em; }
</style>

<!-- _class: lead -->

# UD1 · Análisis de requisitos del sistema LLM

MP04 · Infraestructura para la ejecución de LLMs

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Identificar y clasificar los entornos de ejecución disponibles para LLMs (local, nube, híbrido, servicios gestionados)
- Describir las características técnicas de un modelo (parámetros, formatos de peso, precisión numérica, cuantización, contexto)
- Determinar los requisitos de servicio (concurrencia, latencia, disponibilidad, privacidad, coste)
- Identificar las limitaciones técnicas del sistema hardware (VRAM, RAM, cómputo, caché KV)
- Documentar los requisitos mínimos y recomendados en una ficha estructurada

---

## Entorno de ejecución — tipos

El primer paso es determinar dónde se ejecutará el modelo. Esta decisión condiciona todas las elecciones posteriores.

| Entorno | Descripción | Cuándo elegirlo |
|---|---|---|
| **Local** | Ejecución en el propio equipo del usuario | Privacidad máxima, sin conectividad externa |
| **Servidor propio** | Servidor dedicado en instalaciones del cliente | Control total, multiusuario, sin costes variables |
| **Nube IaaS** | Instancias GPU en AWS, Azure, GCP | Escalabilidad bajo demanda, sin inversión inicial |
| **Servicio gestionado (API)** | OpenAI, Anthropic, Mistral AI, Google | Mínimo mantenimiento, pago por uso |
| **Híbrido** | Combinación de entornos según carga o privacidad | Datos sensibles en local, picos en nube |

> La elección no es solo técnica: influyen el presupuesto, la política de privacidad y la madurez del equipo.

---

## Entorno de ejecución — comparativa detallada

| Criterio | Local | Servidor propio | Nube IaaS | API gestionada |
|---|---|---|---|---|
| **Control de datos** | Total | Total | Alto (según región) | Bajo |
| **Escalado** | No | Limitado | Ilimitado | Ilimitado |
| **Coste fijo** | Hardware | Hardware + mantenimiento | 0 | 0 |
| **Coste variable** | Electricidad | Electricidad | Por hora de GPU | Por token |
| **Latencia de red** | 0 ms | LAN < 1 ms | 10-100 ms | 50-500 ms |
| **Mantenimiento** | Usuario | Equipo IT | Proveedor infra | Proveedor total |
| **Disponibilidad** | Hardware local | Alta (RAID, UPS) | SLA 99,9 %+ | SLA 99,9 %+ |

**Criterio de decisión principal:** si los datos no pueden salir de la organización, el entorno debe ser local o servidor propio.

---

## Características del modelo — parámetros y tamaño

El tamaño del modelo es el principal determinante de los requisitos hardware.

### Escala habitual de modelos LLM open source

| Tamaño | Ejemplos | Caso de uso típico |
|---|---|---|
| **1B – 3B** | Phi-3 Mini, Qwen2.5-1.5B | Dispositivos edge, tareas simples |
| **7B – 8B** | Llama 3.1 8B, Mistral 7B | Workstation, servidor de gama media |
| **13B – 14B** | Llama 2 13B, Qwen2.5-14B | Servidor con GPU de 24 GB |
| **32B – 34B** | Qwen2.5-32B, CodeLlama 34B | GPU de 48-80 GB o multi-GPU |
| **70B – 72B** | Llama 3.1 70B, Qwen2.5-72B | Multi-GPU o cuantización agresiva |
| **405B+** | Llama 3.1 405B | Clúster multi-GPU, solo cuantizado |

> Los parámetros no son el único factor: la arquitectura (MoE vs. densa), la longitud de contexto y las capas de atención también afectan el consumo de memoria.

---

## Características del modelo — formatos de peso

El formato en que se distribuye el modelo determina qué motor de inferencia puede cargarlo.

| Formato | Extensión | Motor principal | Característica |
|---|---|---|---|
| **GGUF** | `.gguf` | llama.cpp, Ollama | Cuantización integrada, CPU-friendly |
| **SafeTensors** | `.safetensors` | vLLM, Transformers, TGI | Formato seguro, sin ejecución de código |
| **ONNX** | `.onnx` | ONNX Runtime, TensorRT | Portabilidad entre frameworks |
| **PyTorch** | `.pt` / `.bin` | Transformers | Formato nativo, flexible |
| **AWQ** | `.safetensors` | AutoAWQ, vLLM | Cuantización de activaciones eficiente |
| **GPTQ** | `.safetensors` | AutoGPTQ, vLLM | Cuantización de pesos post-entrenamiento |

### Verificación del formato

```bash
# Listar archivos de un modelo descargado
ls -lh /models/llama-3.1-8b/
# Comprobar que el formato coincide con el motor previsto
file /models/llama-3.1-8b/model.safetensors
```

---

## Características del modelo — precisión numérica

La precisión determina cuántos bytes ocupa cada parámetro y, por tanto, la VRAM necesaria.

| Precisión | Bytes/parámetro | Uso de VRAM (7B modelo) | Precisión de cálculo |
|---|---|---|---|
| **FP32** | 4 B | ~28 GB | Máxima — entrenamiento |
| **FP16** | 2 B | ~14 GB | Alta — inferencia estándar |
| **BF16** | 2 B | ~14 GB | Alta — preferida en GPUs modernas |
| **INT8** | 1 B | ~7 GB | Buena — inferencia con ligera perdida |
| **INT4** | 0,5 B | ~3,5 GB | Aceptable — inferencia eficiente |

> BF16 tiene mayor rango dinámico que FP16, lo que lo hace más estable para modelos grandes. Las GPUs NVIDIA Ampere (A100) y Ada Lovelace (RTX 40xx) lo soportan de forma nativa.

---

## Características del modelo — cuantización y contexto

### Cuantización

La cuantización reduce la precisión de los pesos para disminuir el consumo de memoria y acelerar la inferencia.

- **Q4_K_M** (GGUF): cuantización a 4 bits con mezcla de bloques — equilibrio calidad/tamaño
- **Q5_K_M** (GGUF): 5 bits — mejor calidad, más VRAM
- **INT8** (vLLM): cuantización de activaciones y pesos
- **AWQ/GPTQ**: cuantización calibrada con datos reales, mejor que INT8 genérico

### Longitud de contexto

La longitud de contexto define cuántos tokens puede procesar el modelo en una sola llamada.

| Rango | Ejemplos | Impacto en VRAM |
|---|---|---|
| 2 048 – 4 096 tokens | Modelos antiguos | Bajo |
| 8 192 – 32 768 tokens | Llama 3.1, Mistral | Moderado |
| 128 000+ tokens | Claude 3.5, GPT-4o | Alto (caché KV grande) |

> El caché KV escala cuadráticamente con la longitud de contexto y linealmente con la concurrencia.

---

## Requisitos de servicio — definición

Los requisitos de servicio traducen las necesidades del negocio en parámetros técnicos medibles.

| Parámetro | Descripción | Ejemplo real |
|---|---|---|
| **Usuarios concurrentes** | Peticiones simultáneas que debe sostener | 10 usuarios en hora punta |
| **Volumen de peticiones** | Peticiones por segundo o por hora | 500 req/hora en media, 50 req/min en pico |
| **Latencia TTFT** | Tiempo hasta el primer token generado | < 2 s para chat interactivo |
| **Velocidad de generación** | Tokens por segundo percibidos por el usuario | > 20 tok/s para flujo legible |
| **Disponibilidad** | SLA requerido | 99 % (< 7,3 h caída/año) |
| **Privacidad** | ¿Pueden los datos salir de la organización? | No — datos de pacientes (RGPD, LOPDGDD) |
| **Conectividad** | ¿Hay acceso a internet desde el entorno? | Solo intranet corporativa |
| **Coste máximo** | Presupuesto operativo mensual | 800 € / mes |

---

## Requisitos de servicio — latencia en detalle

La latencia tiene dos componentes que deben especificarse por separado:

### TTFT (Time to First Token)
Tiempo desde que se envía la petición hasta que llega el primer token de respuesta.

- Depende principalmente del tamaño del prompt de entrada (prefill)
- Crítico para aplicaciones interactivas (chatbots, asistentes)
- Objetivo típico: < 1-2 s para experiencia fluida

### TGS (Token Generation Speed)
Velocidad de generación de tokens una vez iniciada la respuesta.

- Depende del ancho de banda de memoria de la GPU
- Un humano lee ~300 palabras/min ≈ 5 palabras/s ≈ 7 tok/s
- Objetivo mínimo cómodo: > 15 tok/s
- Servidores GPU dedicados: 50-200 tok/s por usuario

> Para pipelines batch (resumen de documentos, extracción masiva) el TTFT no es relevante: importa el throughput total.

---

## Limitaciones técnicas — VRAM y RAM

Las limitaciones hardware determinan qué modelos son viables en cada entorno.

### VRAM (Video RAM — GPU)

La VRAM es el recurso más limitante. Todo el modelo debe caber en VRAM para inferencia GPU.

| GPU | VRAM | Modelo máximo (INT4) |
|---|---|---|
| RTX 3060 | 12 GB | ~13B INT4 (justo) |
| RTX 3090 / 4090 | 24 GB | ~34B INT4 |
| A10G (AWS) | 24 GB | ~34B INT4 |
| RTX 6000 Ada | 48 GB | ~70B INT4 |
| A100 80 GB | 80 GB | ~70B FP16 |
| H100 SXM | 80 GB | ~70B FP16 + contexto largo |

### RAM (CPU)

- Necesaria para cargar el modelo antes de moverlo a VRAM
- En inferencia CPU-only (llama.cpp), la RAM es el factor limitante
- Regla mínima: RAM ≥ VRAM necesaria × 1,5

---

## Limitaciones técnicas — cómputo y caché KV

### Cómputo

| Componente | Impacto en inferencia |
|---|---|
| **Núcleos CUDA / tensor cores** | Velocidad de multiplicación matricial |
| **Ancho de banda de memoria GPU** | Velocidad de transferencia modelo → núcleos |
| **NVLink / PCIe** | Transferencia entre GPUs en configuración multi-GPU |
| **CPU (número de núcleos)** | Gestión de peticiones, tokenización, prefill CPU |

### Caché KV (Key-Value Cache)

El caché KV almacena los estados de atención calculados para evitar recomputación.

```
Tamaño caché KV ≈ 2 × capas × cabezas_atención × dim_cabeza × longitud_contexto
                  × concurrencia × bytes_por_elemento

Ejemplo — Llama 3.1 8B, contexto 8K, 10 usuarios concurrentes, BF16:
  2 × 32 × 8 × 128 × 8192 × 10 × 2 ≈ 10,7 GB adicionales de VRAM
```

> El caché KV puede exceder el tamaño del propio modelo en escenarios de alta concurrencia o contexto muy largo.

---

## Plantilla de documentación de requisitos

Una ficha de requisitos estandarizada evita sorpresas en el despliegue.

```markdown
## Ficha de requisitos — Sistema LLM

### Modelo
- Nombre y versión: Llama 3.1 8B Instruct
- Parámetros: 8 000 M
- Formato de pesos: GGUF Q4_K_M
- Precisión: INT4 (cuantizado)
- Longitud de contexto máxima: 131 072 tokens (uso previsto: 8 192)
- Modalidades: texto → texto

### Requisitos de servicio
- Usuarios concurrentes: 10 (pico: 20)
- Volumen: 200 req/hora media
- TTFT objetivo: < 2 s
- TGS objetivo: > 20 tok/s
- Disponibilidad: 99 % (horario laboral)
- Privacidad: datos NO pueden salir de la organización

### Requisitos hardware mínimos (estimados)
- VRAM: 6 GB (modelo) + 5 GB (KV cache 10 usuarios) = 11 GB
- GPU recomendada: RTX 3080 12 GB o superior
- RAM: 32 GB
- Almacenamiento: SSD NVMe 100 GB
```

---

## Actividad práctica — Análisis de requisitos

### Escenario

Una empresa de consultoría legal quiere desplegar un asistente interno basado en LLM para sus 15 abogados. Los requisitos del negocio son:

- Responder preguntas sobre documentos jurídicos internos
- Los documentos son confidenciales (no pueden salir de la empresa)
- Se estima un uso de 5 abogados simultáneos en hora punta
- Tiempo de respuesta aceptable: < 3 segundos para el primer token
- Presupuesto mensual máximo de operación: 500 €

### Tarea

1. Completa la ficha de requisitos para este caso usando la plantilla anterior
2. Determina el entorno de ejecución justificando la decisión
3. Propón dos modelos candidatos (nombre, tamaño, formato) que podrían ser adecuados
4. Identifica las tres limitaciones técnicas principales que condicionan la solución

---

## Puntos clave — UD1

- El **entorno de ejecución** (local, servidor, nube, API) debe decidirse antes que cualquier otra elección técnica — la privacidad de los datos suele ser el factor determinante.

- Los **formatos de peso** (GGUF, SafeTensors, ONNX) no son intercambiables: cada motor de inferencia soporta un subconjunto de formatos.

- La **precisión numérica** (FP16, BF16, INT8, INT4) determina directamente la VRAM necesaria. La cuantización a INT4 puede reducir la VRAM en un factor de 8 respecto a FP32.

- El **caché KV** puede ser tan grande o mayor que el propio modelo en escenarios de alta concurrencia o contextos largos — no puede ignorarse en el dimensionamiento.

- La **documentación de requisitos** debe incluir tanto mínimos como recomendados, y separar requisitos técnicos de restricciones de negocio (privacidad, coste, disponibilidad).

---

## Criterios de evaluación — UD1

| Criterio | Indicadores de logro |
|---|---|
| **Determina el entorno de ejecución** | Justifica la elección con al menos 3 criterios técnicos o de negocio |
| **Identifica características del modelo** | Especifica parámetros, formato, precisión y longitud de contexto |
| **Define requisitos de servicio** | Cuantifica concurrencia, latencia (TTFT/TGS), disponibilidad y restricciones |
| **Identifica limitaciones técnicas** | Estima VRAM, RAM, impacto del caché KV y cómputo necesario |
| **Documenta requisitos** | Entrega ficha completa con mínimos y recomendados diferenciados |

> **Referencia:** resultado de aprendizaje RA1 — "Analiza los requisitos técnicos, funcionales y operativos del sistema, identificando condiciones de ejecución y restricciones de servicio."

---

[← Volver a MP04](../index.md)


---

<!-- nav-slide -->

## Navegación

[Volver al módulo](../) &nbsp;·&nbsp; [UD2 · Selección y dimensionamiento… →](../UD2_Dimensionamiento-recursos/)
