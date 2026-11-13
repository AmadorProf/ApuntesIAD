# UD2 · Selección y dimensionamiento de recursos para LLMs

---

## 1. Introducción

El despliegue de modelos de lenguaje de gran escala en infraestructura propia plantea uno de los desafíos de ingeniería más complejos que puede abordar un equipo técnico en la actualidad. A diferencia de los modelos tradicionales de aprendizaje automático, cuyos requisitos de cómputo son predecibles y relativamente modestos, los LLMs imponen restricciones de memoria, ancho de banda y latencia que determinan de forma determinista qué hardware es capaz de ejecutarlos y en qué condiciones operativas.

La primera realidad con la que se enfrenta cualquier equipo que evalúa el hosting propio de un LLM es que el tamaño del modelo —medido en parámetros— traduce directamente a requisitos de VRAM, y que la VRAM disponible en una GPU es el cuello de botella no negociable del sistema. Un modelo de 70.000 millones de parámetros cargado en precisión FP16 requiere aproximadamente 140 GB de VRAM solo para sus pesos, antes de contabilizar el KV cache necesario para procesar el contexto. Este dato convierte la selección de hardware en un ejercicio de aritmética antes de ser una decisión de negocio.

La segunda realidad es que el dimensionamiento no termina en la capacidad de alojar el modelo: hay que garantizar que el sistema puede atender el tráfico previsto con las restricciones de latencia que el caso de uso impone. Un modelo que cabe en una GPU puede resultar completamente inviable si el throughput necesario requiere diez réplicas paralelas. La planificación de capacidad para LLMs es, por tanto, un ejercicio multivariable que equilibra tamaño del modelo, precisión numérica, técnicas de cuantización, hardware seleccionado y proyección de tráfico.

Esta unidad dota al estudiante de los fundamentos matemáticos y prácticos para realizar ese dimensionamiento de forma rigurosa: desde las fórmulas de cálculo de VRAM hasta la comparativa de configuraciones multi-GPU, pasando por las técnicas de cuantización que permiten ejecutar modelos grandes en hardware más accesible, y llegando hasta la estimación del coste total de propiedad que fundamenta la decisión de hosting propio frente a API externa.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Calcular la VRAM necesaria para alojar un LLM dado su número de parámetros, precisión numérica y longitud de contexto objetivo.
2. Comparar las técnicas de cuantización más extendidas (GPTQ, AWQ, GGUF, bitsandbytes) evaluando el trade-off entre reducción de memoria, velocidad de inferencia y degradación de calidad.
3. Seleccionar la configuración de GPU más adecuada para un caso de uso dado, justificando la decisión con datos técnicos y económicos.
4. Diseñar arquitecturas multi-GPU con tensor parallelism y pipeline parallelism para modelos que superan la capacidad de una sola GPU.
5. Estimar el throughput esperado (tokens/segundo) y la latencia para distintas configuraciones de hardware y tamaños de batch.
6. Calcular el coste total de propiedad (TCO) de una infraestructura LLM on-premise y compararlo con el coste de uso de APIs de proveedores.
7. Elaborar un plan de capacidad que contemple el crecimiento proyectado del tráfico en un horizonte de doce meses.

---

## 3. Fundamentos de memoria para LLMs

### 3.1 Cálculo de VRAM para los pesos del modelo

La memoria necesaria para alojar los pesos de un LLM depende de dos variables: el número de parámetros del modelo y la precisión numérica utilizada para representarlos.

| Precisión | Bytes por parámetro | Modelo 7B | Modelo 13B | Modelo 70B | Modelo 405B |
|---|---|---|---|---|---|
| FP32 | 4 | 28 GB | 52 GB | 280 GB | 1.620 GB |
| FP16 / BF16 | 2 | 14 GB | 26 GB | 140 GB | 810 GB |
| INT8 | 1 | 7 GB | 13 GB | 70 GB | 405 GB |
| INT4 (NF4) | 0,5 | 3,5 GB | 6,5 GB | 35 GB | 202 GB |

La fórmula base es:

```
VRAM_pesos = num_parametros × bytes_por_parametro
```

En la práctica, el multiplicador efectivo es algo superior debido a estructuras internas del modelo (embeddings de posición, buffers de normalización, etc.), pero la estimación con la tabla anterior es suficientemente precisa para planificación.

### 3.2 KV Cache: el componente olvidado

El KV cache (Key-Value cache) almacena las representaciones intermedias de atención para cada token del contexto procesado, evitando recalcularlas en cada paso de generación. Su tamaño crece linealmente con la longitud de contexto, el número de capas del modelo y el tamaño de los heads de atención.

La fórmula aproximada para el KV cache en FP16 es:

```
VRAM_kv_cache = 2 × num_capas × num_kv_heads × dim_head × longitud_contexto × 2 bytes
```

Para un modelo Llama 3 70B (80 capas, 8 KV heads GQA, dim_head=128) con longitud de contexto de 8.192 tokens:

```
VRAM_kv_cache = 2 × 80 × 8 × 128 × 8192 × 2 bytes ≈ 21,5 GB
```

Esto significa que alojar un modelo 70B en FP16 con contexto de 8K requiere aproximadamente 140 + 22 = 162 GB de VRAM, sin contar sobrecargas del framework. Este cálculo explica por qué los modelos grandes requieren configuraciones multi-GPU incluso cuando los pesos parecen caber en una sola tarjeta.

### 3.3 Activaciones y overhead del framework

Además de pesos y KV cache, el proceso de inferencia genera tensores de activación intermedios durante el forward pass. Su tamaño depende del tamaño de batch y de la longitud de la secuencia de entrada. Para estimaciones de planificación, un factor de seguridad del 15–20% sobre la suma de pesos y KV cache es una práctica habitual.

La fórmula completa para planificación es:

```
VRAM_total = (VRAM_pesos + VRAM_kv_cache) × 1,20
```

---

## 4. Técnicas de cuantización

### 4.1 GPTQ (Generative Pre-trained Transformer Quantization)

GPTQ es un método de cuantización post-entrenamiento (PTQ) que reduce la precisión de los pesos a INT4 o INT8, minimizando la degradación de calidad mediante una calibración basada en un conjunto pequeño de datos de referencia. El proceso cuantiza capa a capa, ajustando los errores de cuantización de forma iterativa.

Los modelos cuantizados con GPTQ se distribuyen habitualmente con la nomenclatura `modelo-GPTQ` en HuggingFace Hub y pueden cargarse con la librería `auto-gptq` o mediante `transformers` con el parámetro `quantization_config`. Son la opción preferida para uso con GPU NVIDIA ya que aprovechan kernels CUDA optimizados (ExLlamaV2).

### 4.2 AWQ (Activation-aware Weight Quantization)

AWQ mejora sobre GPTQ al identificar, para cada capa, los pesos más relevantes (los que más afectan a las activaciones) y preservarlos con mayor precisión. Esto permite obtener mejor calidad que GPTQ a la misma tasa de compresión, especialmente en tareas con razonamiento complejo.

Los modelos AWQ se cargan con la librería `autoawq` y son compatibles con vLLM en producción. Son la opción recomendada para despliegues de producción con modelos cuantizados en GPU.

### 4.3 GGUF / llama.cpp

GGUF (anteriormente GGML) es el formato de cuantización utilizado por el proyecto `llama.cpp`. Soporta múltiples niveles de cuantización (Q2_K, Q3_K_M, Q4_K_M, Q5_K_M, Q6_K, Q8_0) con diferentes trade-offs entre tamaño y calidad. Su principal ventaja es la capacidad de ejecutar inferencia en CPU (aunque lentamente) y en combinación GPU+CPU, lo que permite ejecutar modelos que no caben completamente en la VRAM descargando parte de las capas a RAM del sistema.

`llama.cpp` y sus frontends (Ollama, LM Studio) son la opción más accesible para experimentación y despliegues en hardware modesto (una GPU de consumo + RAM amplia). Para producción a escala, vLLM con AWQ o GPTQ ofrece mejor throughput.

### 4.4 bitsandbytes (QLoRA / INT8 loading)

La librería `bitsandbytes` de Tim Dettmers implementa cuantización INT8 y NF4 (normalización float de 4 bits) integrada directamente en HuggingFace Transformers. Es la base del método QLoRA (Quantized LoRA) para fine-tuning eficiente. Para inferencia pura en producción, GPTQ o AWQ ofrecen mejor rendimiento; bitsandbytes es más relevante en contextos de fine-tuning con recursos limitados.

### 4.5 Tabla comparativa de técnicas de cuantización

| Técnica | Precisión | VRAM 7B | VRAM 70B | Velocidad inferencia | Calidad | Mejor caso de uso |
|---|---|---|---|---|---|---|
| FP16/BF16 (base) | 16 bits | 14 GB | 140 GB | Referencia | Máxima | Producción con recursos suficientes |
| GPTQ INT4 | 4 bits | 4 GB | 38 GB | +10-20% vs base | Alta | GPU NVIDIA, producción |
| AWQ INT4 | 4 bits | 4 GB | 38 GB | +10-20% vs base | Muy alta | GPU NVIDIA, producción recomendada |
| GGUF Q4_K_M | ~4 bits | 4,1 GB | 41 GB | Menor en GPU | Alta | CPU+GPU mixto, Ollama |
| GGUF Q8_0 | 8 bits | 7,7 GB | 73 GB | Moderada | Muy alta | CPU con mucha RAM |
| bitsandbytes NF4 | 4 bits | 4 GB | 38 GB | -20-40% vs base | Alta | Fine-tuning QLoRA |

---

## 5. Selección de GPU para LLMs

### 5.1 Mapeo modelo-GPU para inferencia

La selección de GPU debe partir de los requisitos de VRAM calculados en la sección anterior. La siguiente tabla proporciona la configuración mínima y recomendada para los tamaños de modelo más comunes en producción:

| Tamaño modelo | Precisión | VRAM necesaria | GPU mínima | Configuración recomendada |
|---|---|---|---|---|
| 7B | FP16 | 16 GB | RTX 4090 (24 GB) | 1× A10G (24 GB) |
| 7B | INT4 (AWQ) | 5 GB | RTX 3080 (10 GB) | 1× RTX 4090 (múltiples réplicas) |
| 13B | FP16 | 28 GB | 2× RTX 4090 | 1× A100 40 GB |
| 13B | INT4 | 8 GB | 1× RTX 4090 | 1× RTX 4090 (múltiples réplicas) |
| 34B | FP16 | 70 GB | 2× A100 40 GB | 1× A100 80 GB |
| 34B | INT4 | 20 GB | 1× RTX 4090 | 1× A100 40 GB |
| 70B | FP16 | 162 GB | 4× A100 40 GB | 2× A100 80 GB o 2× H100 80 GB |
| 70B | INT4 | 42 GB | 2× RTX 4090 | 1× A100 80 GB |
| 405B | FP16 | >800 GB | 8× H100 80 GB | 16× H100 80 GB (producción) |
| 405B | INT4 | ~210 GB | 4× H100 80 GB | 4× A100 80 GB |

### 5.2 Throughput esperado por GPU

El throughput de generación (tokens/segundo por petición con batch size 1) varía significativamente entre GPUs:

| GPU | Modelo 7B FP16 | Modelo 7B AWQ-INT4 | Modelo 70B FP16 (multi-GPU) |
|---|---|---|---|
| RTX 4090 | ~80 tok/s | ~150 tok/s | N/A (VRAM insuficiente) |
| A100 80 GB | ~130 tok/s | ~200 tok/s | ~40 tok/s (2×A100) |
| H100 80 GB | ~220 tok/s | ~350 tok/s | ~80 tok/s (2×H100) |
| MI300X (AMD) | ~180 tok/s | ~260 tok/s | ~70 tok/s (2×MI300X) |

*Valores orientativos con vLLM y contexto de 2K tokens. El throughput real varía con la longitud de contexto, el batch size y el modelo exacto.*

---

## 6. Paralelismo multi-GPU para modelos grandes

### 6.1 Tensor Parallelism

El tensor parallelism (TP) divide las matrices de pesos de cada capa entre múltiples GPUs, de forma que cada GPU procesa una fracción de la computación y se sincronizan los resultados mediante operaciones all-reduce tras cada capa. Es la estrategia más eficiente para reducir la latencia en inferencia de un único request, ya que todas las GPUs trabajan en paralelo en cada token generado.

En vLLM, el tensor parallelism se configura con el parámetro `--tensor-parallel-size N`, donde N es el número de GPUs a utilizar. Requiere que las GPUs estén conectadas mediante NVLink para maximizar el ancho de banda de comunicación; sobre PCIe, la comunicación entre GPUs se convierte en el cuello de botella.

```bash
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Meta-Llama-3.1-70B-Instruct \
    --tensor-parallel-size 4 \
    --gpu-memory-utilization 0.90 \
    --max-model-len 8192
```

### 6.2 Pipeline Parallelism

El pipeline parallelism (PP) divide el modelo en segmentos de capas consecutivas, asignando cada segmento a una GPU diferente. Las GPUs procesan micro-batches en secuencia: cuando la GPU 0 termina con el micro-batch 1 y lo pasa a la GPU 1, empieza con el micro-batch 2. En estado estacionario, todas las GPUs están ocupadas procesando diferentes micro-batches simultáneamente.

El PP es más eficiente en throughput para batches grandes pero introduce mayor latencia por request individual que el TP. Es la estrategia preferida en escenarios donde el objetivo es maximizar el número de requests procesados por segundo, no minimizar el tiempo de respuesta de cada request individual. DeepSpeed y Megatron-LM implementan PP junto con TP para modelos de escala masiva.

### 6.3 Combinación TP + PP

Para modelos de escala extrema (>100B parámetros), la práctica estándar en producción es combinar tensor parallelism dentro de cada nodo (aprovechando NVLink) con pipeline parallelism entre nodos (sobre InfiniBand). Esta estrategia minimiza el tráfico de red de alta latencia al limitar las comunicaciones all-reduce de TP al bus intra-nodo.

Una configuración típica para Llama 3 405B en producción podría ser: 4 nodos × 8× H100 80 GB, con TP=8 (dentro de cada nodo) y PP=4 (entre los 4 nodos).

---

## 7. Estimación de coste y planificación de capacidad

### 7.1 Coste total de propiedad (TCO) on-premise

El TCO de una infraestructura LLM on-premise debe contemplar:

- **CAPEX (coste de capital)**: hardware (GPUs, servidor, red, almacenamiento), instalación y puesta en marcha.
- **OPEX anual**: electricidad (potencia kW × horas × coste €/kWh), refrigeración (factor PUE), personal de operaciones, mantenimiento hardware, licencias de software.
- **Coste de amortización**: la vida útil típica de las GPUs para planificación financiera es 3–5 años.

Ejemplo de cálculo para un servidor con 2× H100 80 GB SXM:

```
CAPEX hardware:     90.000 € (servidor + 2× H100)
Electricidad/año:   1.400 W × 8.760 h × 0,15 €/kWh × PUE 1,4 = 2.572 €/año
Personal (parcial): 15.000 €/año
Amortización (4 años): 90.000 / 4 = 22.500 €/año
─────────────────────────────────────
TCO año 1:          40.072 €
TCO año 2-4:        20.072 €/año
```

### 7.2 Coste de APIs externas

El coste de uso de APIs de LLMs propietarios se factura por millón de tokens procesados (input + output). A modo de referencia (precios orientativos, junio 2026):

| Proveedor / Modelo | Input ($/M tokens) | Output ($/M tokens) |
|---|---|---|
| Anthropic Claude Sonnet 4.6 | 3,00 | 15,00 |
| OpenAI GPT-4o | 2,50 | 10,00 |
| Google Gemini 1.5 Pro | 1,25 | 5,00 |
| Meta Llama 3.1 70B (via Together) | 0,88 | 0,88 |
| Llama 3.1 70B (hosting propio, H100) | ~0,05–0,15 | ~0,05–0,15 |

El punto de equilibrio entre API externa y hosting propio depende del volumen de uso. Para cargas de producción intensivas (>500M tokens/mes), el hosting propio suele ser más rentable desde el segundo año. Para cargas bajas o irregulares, las APIs externas son más eficientes económicamente.

### 7.3 Planificación de capacidad a 12 meses

La planificación de capacidad debe partir de una estimación del tráfico inicial y un factor de crecimiento mensual proyectado. Los parámetros clave son:

- **QPS pico**: queries por segundo en hora punta.
- **Longitud media de entrada + salida**: en tokens.
- **Latencia máxima aceptable**: tiempo de respuesta P99.
- **Factor de utilización objetivo**: normalmente 60–70% para mantener margen ante picos.

Con estos parámetros, el número de réplicas necesarias se calcula como:

```
réplicas = ceil(QPS_pico × latencia_s / (utilización × factor_concurrencia_por_réplica))
```

La planificación debe revisarse trimestralmente contrastando las proyecciones con el tráfico real y ajustando el dimensionamiento en consecuencia.

---

## 8. Actividades prácticas

### Actividad 1 — Dimensionamiento de infraestructura para un caso de uso real

**Descripción**: Se presenta un caso de uso empresarial (asistente de atención al cliente con Llama 3.1 70B, 200 usuarios concurrentes, contexto de 4K tokens, latencia máxima de 3 segundos para el primer token). El estudiante debe calcular la VRAM necesaria, seleccionar el hardware, justificar si usar el modelo en FP16 o cuantizado, y determinar el número de réplicas necesarias.

**Entregable**: Documento de dos páginas con todos los cálculos explícitos, la configuración seleccionada y una comparativa de coste on-premise vs API externa a 12 meses.

**Criterios de evaluación**: Corrección de los cálculos de VRAM, justificación de la técnica de cuantización elegida, coherencia entre requisitos de latencia y configuración propuesta.

---

### Actividad 2 — Benchmarking de configuraciones de cuantización

**Descripción**: Usando un entorno con GPU disponible (Google Colab Pro, Kaggle, o laboratorio del centro), el estudiante carga el mismo modelo (por ejemplo, Phi-3 Mini 3.8B o Mistral 7B) en tres configuraciones: FP16, GPTQ INT4 y GGUF Q4_K_M. Para cada configuración, mide: VRAM utilizada, tiempo de carga del modelo, throughput de generación (tokens/segundo) y calidad en una muestra de 20 prompts (evaluación manual de 1–5).

**Entregable**: Tabla comparativa con los resultados medidos y análisis de 300 palabras sobre el trade-off observado.

**Criterios de evaluación**: Rigor en la medición, análisis crítico del trade-off, comprensión de las diferencias entre técnicas.

---

### Actividad 3 — Diseño de arquitectura multi-GPU

**Descripción**: Una empresa necesita desplegar Llama 3.1 405B en FP16 para uso interno de un equipo de 50 desarrolladores. El presupuesto máximo en hardware es 400.000 €. Diseña la arquitectura multi-GPU: número y tipo de GPUs, configuración de tensor y/o pipeline parallelism, topología de red necesaria (NVLink, InfiniBand), y estima el throughput que puede ofrecer la solución con el tráfico proyectado (50 usuarios × 20 requests/hora × 500 tokens/request de media).

**Entregable**: Diagrama de arquitectura y documento de justificación de dos páginas.

**Criterios de evaluación**: Viabilidad técnica de la solución, justificación del tipo de paralelismo elegido, coherencia con las restricciones de presupuesto.

---

### Actividad 4 — Plan de capacidad a 12 meses

**Descripción**: Partiendo del sistema diseñado en la Actividad 3, elabora un plan de capacidad para los próximos 12 meses asumiendo un crecimiento del 15% mensual en el número de usuarios. El plan debe incluir: tráfico proyectado mes a mes, número de réplicas/GPUs necesarias en cada mes, hitos de ampliación de infraestructura y su coste, y una curva de coste total mensual.

**Entregable**: Hoja de cálculo con la proyección mensual y resumen ejecutivo de media página.

**Criterios de evaluación**: Corrección de la proyección de tráfico, identificación de los hitos de escalado, coherencia del plan de costes.

---

## 9. Referencias

- **vLLM — Documentación oficial**: guía de instalación, parámetros de servidor, tensor parallelism y quantization support. Disponible en: [https://docs.vllm.ai/](https://docs.vllm.ai/)

- **HuggingFace Transformers — Quantization guide**: documentación sobre GPTQ, AWQ, bitsandbytes y GGUF en el ecosistema HuggingFace. Disponible en: [https://huggingface.co/docs/transformers/quantization](https://huggingface.co/docs/transformers/quantization)

- **AutoAWQ — Repositorio oficial**: implementación de referencia de AWQ para cuantización de LLMs. Disponible en: [https://github.com/casper-hansen/AutoAWQ](https://github.com/casper-hansen/AutoAWQ)

- **AutoGPTQ — Repositorio oficial**: implementación de GPTQ para modelos HuggingFace. Disponible en: [https://github.com/AutoGPTQ/AutoGPTQ](https://github.com/AutoGPTQ/AutoGPTQ)

- **llama.cpp — Repositorio oficial**: motor de inferencia CPU/GPU con soporte GGUF y cuantización multinivel. Disponible en: [https://github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp)

- **NVIDIA H100 Tensor Core GPU Architecture**: whitepaper técnico de la arquitectura Hopper con especificaciones de NVLink 4.0 y capacidades de cómputo. Disponible en: [https://resources.nvidia.com/en-us-tensor-core/gtc22-whitepaper-hopper](https://resources.nvidia.com/en-us-tensor-core/gtc22-whitepaper-hopper)

- **Megatron-LM — Repositorio NVIDIA**: implementación de tensor y pipeline parallelism para entrenamiento e inferencia de modelos grandes. Disponible en: [https://github.com/NVIDIA/Megatron-LM](https://github.com/NVIDIA/Megatron-LM)

- **DeepSpeed Inference — Documentación**: optimizaciones de inferencia distribuida, incluyendo ZeRO-Inference y kernel fusion. Disponible en: [https://www.deepspeed.ai/inference/](https://www.deepspeed.ai/inference/)

- **PagedAttention y vLLM — Paper original**: Kwon et al. (2023). "Efficient Memory Management for Large Language Model Serving with PagedAttention". SOSP 2023. Disponible en: [https://arxiv.org/abs/2309.06180](https://arxiv.org/abs/2309.06180)

- **FlashAttention-2 — Paper**: Dao, T. (2023). "FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning". Disponible en: [https://arxiv.org/abs/2307.08691](https://arxiv.org/abs/2307.08691)

- **LLM Inference Performance Engineering — Blog de Databricks**: análisis práctico de throughput, latencia y dimensionamiento para modelos de distinto tamaño. Disponible en: [https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices)

- **AMD Instinct MI300X Datasheet**: especificaciones técnicas del acelerador AMD con 192 GB HBM3, incluyendo soporte ROCm para PyTorch. Disponible en: [https://www.amd.com/en/products/accelerators/instinct/mi300/mi300x.html](https://www.amd.com/en/products/accelerators/instinct/mi300/mi300x.html)

---

*UD2 · MP04 Infraestructura para la ejecución de LLMs · CFS2 Instalación, despliegue y explotación de sistemas de IA*
