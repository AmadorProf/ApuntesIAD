---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD2 · Selección y dimensionamiento de recursos | MP04 · Infraestructura para la ejecución de LLMs'
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

# UD2 · Selección y dimensionamiento de recursos

MP04 · Infraestructura para la ejecución de LLMs

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Calcular la memoria GPU (VRAM) necesaria para un modelo dado su tamaño, precisión y concurrencia
- Seleccionar el acelerador (GPU, NPU, TPU) adecuado para el caso de uso
- Dimensionar CPU, RAM, almacenamiento y red complementarios
- Comparar alternativas de infraestructura (local, servidor, nube IaaS, API, híbrida)
- Aplicar criterios de eficiencia energética, DNSH y ODS en la decisión de infraestructura

---

## Cálculo de VRAM — fórmula base

La VRAM es el recurso más limitante en la inferencia con GPU. La fórmula de estimación es:

```
VRAM_modelo (GB) = Parámetros (B) × Bytes_por_parámetro × Factor_overhead

Factor_overhead ≈ 1.2  (activaciones, buffers internos del motor)

Bytes por precisión:
  FP32  = 4 bytes
  FP16  = 2 bytes
  BF16  = 2 bytes
  INT8  = 1 byte
  INT4  = 0.5 bytes
```

### Ejemplos calculados

| Modelo | Precisión | Cálculo | VRAM estimada |
|---|---|---|---|
| 7B | FP16 | 7 × 2 × 1.2 | **16,8 GB** |
| 7B | INT4 | 7 × 0.5 × 1.2 | **4,2 GB** |
| 13B | BF16 | 13 × 2 × 1.2 | **31,2 GB** |
| 13B | INT4 | 13 × 0.5 × 1.2 | **7,8 GB** |
| 70B | FP16 | 70 × 2 × 1.2 | **168 GB** |
| 70B | INT4 | 70 × 0.5 × 1.2 | **42 GB** |

---

## Cálculo de VRAM — caché KV

El caché KV almacena los estados de atención calculados y crece con la longitud de contexto y la concurrencia.

```
VRAM_KV (GB) = 2 × num_capas × num_cabezas × dim_cabeza
               × longitud_contexto × concurrencia × bytes_elemento / 1e9

Para Llama 3.1 8B (num_capas=32, num_cabezas=8, dim_cabeza=128):

  BF16, contexto 4096, 1 usuario:
    2 × 32 × 8 × 128 × 4096 × 1 × 2 / 1e9 ≈ 0.54 GB

  BF16, contexto 8192, 10 usuarios:
    2 × 32 × 8 × 128 × 8192 × 10 × 2 / 1e9 ≈ 10.7 GB
```

### VRAM total = VRAM_modelo + VRAM_KV

| Escenario | VRAM modelo (INT4) | VRAM KV (BF16, 10u, 8K) | Total |
|---|---|---|---|
| Llama 3.1 8B | 4,2 GB | 10,7 GB | **~15 GB** |
| Llama 3.1 70B | 42 GB | 85 GB | **~127 GB** |

> La cuantización del modelo a INT4 no reduce el tamaño del caché KV, que se mantiene en FP16/BF16.

---

## Script de estimación de VRAM

```python
def estimar_vram(
    parametros_B: float,
    precision: str,
    num_capas: int,
    num_cabezas_kv: int,
    dim_cabeza: int,
    longitud_contexto: int,
    usuarios_concurrentes: int,
    overhead: float = 1.2
) -> dict:
    bytes_por_param = {"fp32": 4, "fp16": 2, "bf16": 2, "int8": 1, "int4": 0.5}
    bpp = bytes_por_param[precision.lower()]

    vram_modelo = parametros_B * 1e9 * bpp * overhead / 1e9
    vram_kv = (2 * num_capas * num_cabezas_kv * dim_cabeza
               * longitud_contexto * usuarios_concurrentes * 2 / 1e9)  # BF16 KV
    vram_total = vram_modelo + vram_kv

    return {
        "vram_modelo_GB": round(vram_modelo, 1),
        "vram_kv_GB": round(vram_kv, 1),
        "vram_total_GB": round(vram_total, 1)
    }

# Llama 3.1 8B, INT4, contexto 8K, 10 usuarios
resultado = estimar_vram(8, "int4", 32, 8, 128, 8192, 10)
print(resultado)
# {'vram_modelo_GB': 4.8, 'vram_kv_GB': 10.7, 'vram_total_GB': 15.5}
```

---

## Aceleradores — GPU NVIDIA

Las GPUs NVIDIA son el estándar de facto para inferencia de LLMs en producción.

| GPU | VRAM | Ancho de banda memoria | TDP | Segmento |
|---|---|---|---|---|
| **RTX 4060 Ti** | 16 GB | 288 GB/s | 165 W | Consumidor bajo |
| **RTX 4090** | 24 GB | 1 008 GB/s | 450 W | Consumidor alto |
| **RTX 6000 Ada** | 48 GB | 960 GB/s | 300 W | Profesional |
| **A10G** | 24 GB | 600 GB/s | 150 W | Nube (AWS) |
| **A100 SXM** | 80 GB | 2 000 GB/s | 400 W | Centro de datos |
| **H100 SXM** | 80 GB | 3 350 GB/s | 700 W | Centro de datos HPC |
| **H200 SXM** | 141 GB | 4 800 GB/s | 700 W | Centro de datos HPC |

> El ancho de banda de memoria es el factor limitante para la velocidad de generación (TGS). Una H100 puede generar tokens ~3x más rápido que una A100 con el mismo modelo.

---

## Aceleradores — GPU AMD, NPU y TPU

### GPU AMD

| GPU | VRAM | Observaciones |
|---|---|---|
| **RX 7900 XTX** | 24 GB | Consumer, soporte ROCm limitado |
| **Instinct MI300X** | 192 GB | HPC, mayor VRAM del mercado |

### NPU (Neural Processing Unit)

- **Apple M-series** (Metal): integrada, comparte memoria con CPU. M3 Max: 128 GB unificada
- **Qualcomm Snapdragon** (QNN): dispositivos móviles y PCs ARM
- **Intel Arc / Core Ultra** (OpenVINO): PCs de consumo con IA integrada

### TPU (Tensor Processing Unit — Google)

- Solo disponibles en Google Cloud (Cloud TPU)
- Diseñadas específicamente para TensorFlow/JAX
- Ventaja en escala masiva, no en despliegue general de LLMs open source

---

## Dimensionamiento de CPU y RAM

### CPU

La CPU gestiona la tokenización, el servidor HTTP, el pre/post-procesamiento y la orquestación de peticiones.

| Componente | Recomendación mínima | Recomendación producción |
|---|---|---|
| **Núcleos físicos** | 8 núcleos | 16-32 núcleos |
| **Arquitectura** | x86-64 compatible AVX2 | AVX-512 (Intel Xeon, AMD EPYC) |
| **Caché L3** | 16 MB | 32-64 MB |

### RAM

| Uso | Regla |
|---|---|
| Sistema base + SO | 8 GB reservados |
| Buffer de carga del modelo | ≥ tamaño del modelo en disco |
| Inferencia CPU-only (llama.cpp) | RAM ≥ VRAM equivalente necesaria |
| Servidor multiusuario con GPU | 32-64 GB recomendados |

> En inferencia CPU-only, la RAM es el límite. Con llama.cpp y un modelo 7B Q4_K_M (~4,5 GB), bastan 16 GB RAM para uso personal.

---

## Dimensionamiento de almacenamiento y red

### Almacenamiento

| Componente | Requisito | Justificación |
|---|---|---|
| **SO y dependencias** | 50-100 GB SSD | CUDA, librerías, motor inferencia |
| **Modelos LLM** | 4-200 GB por modelo | Según tamaño y cuantización |
| **Logs y trazas** | 20-100 GB / mes | Según volumen de peticiones |
| **Velocidad recomendada** | NVMe PCIe 4.0 | Carga de modelos en < 30 s |

```bash
# Tiempos de carga aproximados por tipo de almacenamiento (modelo 7B Q4, ~4 GB)
# HDD SATA (100 MB/s):   ~40 s
# SSD SATA (500 MB/s):   ~8 s
# NVMe PCIe 3.0 (3 GB/s): ~1.3 s
# NVMe PCIe 4.0 (7 GB/s): ~0.6 s
```

### Red

| Escenario | Ancho de banda mínimo |
|---|---|
| Uso local (un usuario) | No aplica |
| Servidor LAN (10 usuarios) | 1 Gbps |
| Servidor con acceso web | 100 Mbps simétricos |
| Descarga de modelos grandes | 1 Gbps preferible |

---

## Comparativa de alternativas de infraestructura

| Criterio | Local (PC) | Servidor propio | Nube IaaS | API gestionada | Híbrida |
|---|---|---|---|---|---|
| **Inversión inicial** | 1 000-5 000 € | 10 000-80 000 € | 0 € | 0 € | Media |
| **Coste mensual** | Electricidad | Electricidad + IT | 200-5 000 € | Por token | Variable |
| **Escalado** | No | Limitado | Ilimitado | Ilimitado | Parcial |
| **Privacidad datos** | Total | Total | Alta | Baja-Media | Configurable |
| **Mantenimiento** | Usuario | Equipo IT | Proveedor | 0 | Compartido |
| **SLA** | Sin SLA | Propio | 99,9 %+ | 99,9 %+ | Depende |
| **Tiempo de despliegue** | Horas | Días-semanas | Minutos | Inmediato | Días |

### Condiciones de escalado o sustitución

- **Local → Servidor propio:** cuando los usuarios superan 2-3 simultáneos de forma sostenida
- **Servidor propio → Nube IaaS:** cuando la carga tiene picos impredecibles > 5x la media
- **Nube IaaS → API:** cuando el coste de mantenimiento supera el coste por token

---

## Eficiencia energética y sostenibilidad

### Estrategias para reducir el consumo energético

| Estrategia | Ahorro estimado | Implementación |
|---|---|---|
| **Cuantización INT4 vs FP16** | 30-50 % menos energía | Cambio de formato del modelo |
| **Auto-shutdown nocturno** | 40-60 % (si el servicio no es 24/7) | Cron + script de parada |
| **Autoescalado** | Eliminar GPU ociosa | Kubernetes HPA / AWS Auto Scaling |
| **Modelo más pequeño** | Proporcional al tamaño | Validar que cumple calidad |
| **Reutilizar hardware** | 100 % de fabricación evitada | Evaluar hardware existente |

### Marco normativo: DNSH y ODS

- **DNSH** (Do No Significant Harm): principio de taxonomía verde de la UE — ninguna actividad debe causar daño significativo a objetivos ambientales
- **ODS 7**: Energía asequible y no contaminante — minimizar el consumo eléctrico
- **ODS 9**: Industria e infraestructura sostenibles — preferir servidores con certificación de eficiencia
- **ODS 12**: Producción y consumo responsables — reutilización antes que compra nueva

---

## Actividad práctica — Dimensionamiento

### Caso

Se va a desplegar un asistente de atención al cliente para una empresa de seguros. Los requisitos son:

- Modelo: **Mistral 7B Instruct v0.3** (7B parámetros, 32 capas, 8 cabezas KV, dim 128)
- Concurrencia máxima: **20 usuarios simultáneos**
- Longitud de contexto: **4 096 tokens**
- Precisión del modelo: **INT4** (GGUF Q4_K_M)
- Caché KV en BF16

### Tareas

1. Calcula la VRAM necesaria (modelo + caché KV) usando la fórmula
2. Selecciona la GPU o GPUs más adecuadas de la tabla de referencia
3. Dimensiona CPU, RAM, almacenamiento y red
4. Compara dos alternativas de infraestructura (servidor propio vs. nube IaaS) con criterios de coste y privacidad
5. Propón dos medidas de eficiencia energética aplicables al caso

---

## Puntos clave — UD2

- **VRAM_total = VRAM_modelo + VRAM_KV**: ambas componentes son obligatorias. Ignorar el caché KV es el error de dimensionamiento más frecuente.

- La **cuantización** reduce la VRAM del modelo pero no la del caché KV, que permanece en BF16/FP16.

- El **ancho de banda de memoria de la GPU** (no los núcleos CUDA) determina la velocidad de generación de tokens. Una GPU con más TFLOPS pero menos BW puede ser más lenta en inferencia.

- El **almacenamiento NVMe** es crítico para tiempos de carga de modelo aceptables en producción.

- Las decisiones de infraestructura deben contemplar siempre criterios de **eficiencia energética** (DNSH, ODS 7/9/12): cuantización, auto-shutdown y reutilización de hardware son medidas concretas.

---

## Criterios de evaluación — UD2

| Criterio | Indicadores de logro |
|---|---|
| **Calcula memoria y aceleradores** | Aplica la fórmula VRAM con modelo + KV; selecciona GPU con justificación |
| **Dimensiona el resto de recursos** | Especifica CPU, RAM, almacenamiento y red con valores concretos |
| **Criterios de eficiencia** | Propone al menos 2 medidas de reducción de consumo con impacto cuantificado |
| **Formaliza la alternativa** | Compara al menos 2 alternativas con criterios técnicos y económicos |
| **Escalado y sustitución** | Define las condiciones que justificarían cambiar de alternativa |

> **Referencia:** resultado de aprendizaje RA2 — "Selecciona los recursos de infraestructura calculando necesidades de cómputo, memoria, almacenamiento y comunicaciones."

---

[← Volver a MP04](../index.md)
