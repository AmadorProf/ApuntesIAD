---
marp: true
theme: default
paginate: true
size: 16:9
header: 'MP04 · Infraestructura para la ejecución de LLMs'
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
section.lead h1 { font-size: 2.2em; text-align: center; margin-top: 100px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f0fdf4; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
</style>

<!-- _class: lead -->

# MP04 · Infraestructura para la ejecución de LLMs

CFS — Instalación, despliegue y explotación de sistemas de IA (IAD)

---

## Ficha del módulo

| Campo | Valor |
|---|---|
| Código | **MP04** |
| Estándar de competencia | CPE_5074_3 · Nivel 3 |
| Familia profesional | Inteligencia Artificial y Data |
| Duración | **160 h** |
| Curso | **2.º** |

> **Competencia que desarrolla:** implementar el despliegue técnico de soluciones basadas en LLMs, desde la infraestructura y configuración de inferencia hasta su puesta en servicio, garantizando rendimiento, seguridad, trazabilidad y uso responsable.

---

## Estructura del módulo

| # | Unidad didáctica |
|---|---|
| **UD1** | Análisis de requisitos del sistema LLM |
| **UD2** | Selección y dimensionamiento de recursos |
| **UD3** | Preparación del entorno de ejecución |
| **UD4** | Puesta en servicio del modelo |
| **UD5** | Validación de la capacidad operativa |
| **UD6** | Seguridad, privacidad y trazabilidad de la infraestructura |
| **UD7** | Responsabilidad, sostenibilidad, PRL y residuos |

---

<!-- _class: lead -->

# UD1
## Análisis de requisitos del sistema LLM

---

## UD1 · Entorno de ejecución y características del modelo

**Opciones de entorno:**

| Entorno | Cuándo elegirlo |
|---|---|
| **Local** | Privacidad máxima, sin dependencia externa, latencia mínima |
| **Servidor propio** | Control total, multiusuario, sin costes variables |
| **Nube (IaaS/PaaS)** | Escalabilidad, sin inversión inicial en hardware |
| **Servicio gestionado (API)** | Mínimo mantenimiento, pago por uso |
| **Híbrido** | Combinar privacidad y escalabilidad según la carga |

**Características del modelo a documentar:**
- Tamaño (parámetros), formato de pesos (GGUF, SafeTensors, ONNX)
- Precisión numérica (FP32, FP16, BF16, INT8, INT4) y nivel de cuantización
- Longitud de contexto máxima · Modalidades de entrada y salida

---

## UD1 · Requisitos de servicio y limitaciones técnicas

**Requisitos de servicio:**

| Parámetro | Descripción |
|---|---|
| **Usuarios concurrentes** | Nº de peticiones simultáneas que debe soportar |
| **Volumen de peticiones** | Peticiones por segundo o por hora |
| **Latencia** | Tiempo máximo de respuesta (TTFT, velocidad de generación) |
| **Disponibilidad** | SLA requerido (99 %, 99,9 %, 99,99 %) |
| **Privacidad** | ¿Los datos pueden salir de la organización? |
| **Coste** | Presupuesto operativo mensual máximo |

**Documentar:** requisitos mínimos y recomendados · restricciones que condicionan la arquitectura

---

<!-- _class: lead -->

# UD2
## Selección y dimensionamiento de recursos

---

## UD2 · Cálculo de memoria para LLMs

**Estimación de VRAM necesaria (regla práctica):**

```
VRAM (GB) ≈ Parámetros (B) × Bytes por parámetro × Factor de overhead

Ejemplos:
  7B modelo FP16  →  7B × 2 bytes × 1.2 ≈  17 GB VRAM
  7B modelo INT4  →  7B × 0.5 bytes × 1.2 ≈   4 GB VRAM
 70B modelo INT4  →  70B × 0.5 bytes × 1.2 ≈  42 GB VRAM

Precisiones:  FP32 = 4B | FP16/BF16 = 2B | INT8 = 1B | INT4 = 0.5B
```

**Memoria adicional para:**
- KV cache (crece con la longitud de contexto y la concurrencia)
- Activaciones intermedias y gradientes (si hay fine-tuning)

---

## UD2 · Aceleradores y alternativas de infraestructura

**Tipos de aceleradores:**

| Acelerador | Fabricante | Uso habitual |
|---|---|---|
| **GPU** | NVIDIA (A100, H100, RTX), AMD | Entrenamiento e inferencia general |
| **NPU** | Qualcomm, Apple, Intel | Inferencia en dispositivo (edge) |
| **TPU** | Google | Escala masiva en nube Google |

**Comparativa de alternativas de infraestructura:**

| Alternativa | Ventaja | Inconveniente |
|---|---|---|
| Local / PC | Privacidad, coste fijo | Escalado limitado |
| Servidor propio | Control, multi-GPU | Inversión inicial alta |
| Nube IaaS | Flexibilidad | Coste variable, latencia de red |
| API gestionada | Cero mantenimiento | Sin control, costes por token |

---

<!-- _class: lead -->

# UD3
## Preparación del entorno de ejecución

---

## UD3 · Stack de software para inferencia LLM

**Capas del entorno:**

```
┌─────────────────────────────────────────────────┐
│  Motor de inferencia (llama.cpp, vLLM, Ollama)  │
├─────────────────────────────────────────────────┤
│  Librerías de cómputo acelerado (CUDA, ROCm)    │
├─────────────────────────────────────────────────┤
│  Controladores GPU / NPU                        │
├─────────────────────────────────────────────────┤
│  Sistema operativo (Linux: Ubuntu, RHEL)        │
└─────────────────────────────────────────────────┘
```

**Motores de inferencia más usados:**

| Motor | Punto fuerte |
|---|---|
| **llama.cpp** | CPU-first, cuantización, bajo consumo |
| **vLLM** | Alto throughput, PagedAttention |
| **Ollama** | Facilidad de uso, gestión de modelos |
| **Triton Inference Server** | Producción, multi-modelo |

---

## UD3 · Configuración del motor e instalación segura

**Parámetros clave del motor de inferencia:**

```bash
# Ejemplo: vLLM
python -m vllm.entrypoints.openai.api_server \
  --model /models/llama-3-8b \
  --dtype bfloat16 \
  --max-model-len 8192 \
  --max-num-seqs 64 \
  --gpu-memory-utilization 0.90 \
  --port 8000
```

**Seguridad en la instalación:**
- Autenticación de la API (Bearer token, API key)
- Control de acceso a los pesos del modelo
- Gestión de secretos: variables de entorno o *vault*

**Validación:** pruebas de arranque + carga de prueba + revisión del uso de recursos

---

<!-- _class: lead -->

# UD4
## Puesta en servicio del modelo

---

## UD4 · Incorporación y verificación del modelo

**Proceso de incorporación del modelo:**

1. **Descarga o copia** del artefacto desde fuente autorizada
2. **Verificación de integridad:** hash SHA-256 contra el publicado por el autor
3. **Verificación de versión y formato:** compatible con el motor instalado
4. **Comprobación de licencia:** uso permitido según el caso de uso
5. **Compatibilidad:** confirmar que el motor soporta el formato exacto del modelo

**Registro del despliegue:**
- Carga del modelo: tiempo de carga, memoria utilizada
- Estabilidad: primeras peticiones de prueba
- Accesos: quién puede llamar al endpoint y con qué limitaciones

---

## UD4 · Parámetros de ejecución y exposición

**Parámetros de ejecución a configurar:**

| Parámetro | Descripción |
|---|---|
| `max_input_tokens` | Longitud máxima de la entrada |
| `max_output_tokens` | Longitud máxima de la respuesta |
| `max_concurrent_requests` | Peticiones simultáneas máximas |
| `request_timeout` | Tiempo máximo por petición |
| `user_quota` | Límite de peticiones por usuario/período |

**Modos de exposición:**

| Modo | Cuándo |
|---|---|
| API REST compatible OpenAI | Integración sencilla con aplicaciones existentes |
| Servicio interno / microservicio | Entornos corporativos aislados |
| Interfaz local (Ollama, Open WebUI) | Uso individual o pruebas |
| Contenedor / Kubernetes | Producción escalable |

---

<!-- _class: lead -->

# UD5
## Validación de la capacidad operativa

---

## UD5 · Pruebas de carga y concurrencia

**Métricas a medir durante las pruebas:**

| Métrica | Descripción |
|---|---|
| **TTFT** (Time to First Token) | Tiempo hasta la primera respuesta |
| **TPS** (Tokens per Second) | Velocidad de generación |
| **Latencia P50/P95/P99** | Distribución de tiempos de respuesta |
| **VRAM peak** | Consumo máximo de memoria de vídeo |
| **CPU / RAM / Red** | Recursos del sistema bajo carga |

**Herramientas de prueba de carga:**
- `locust` · `k6` · `wrk` · `vegeta` · scripts personalizados con `asyncio`

---

## UD5 · Límites operativos y mecanismos de recuperación

**Identificación de límites operativos:**
- Punto de saturación: a partir de qué carga el sistema empieza a fallar
- Comportamiento ante saturación: colas, rechazos, timeouts, caídas
- Tiempo de recuperación tras un pico de carga

**Mecanismos de continuidad:**

| Mecanismo | Descripción |
|---|---|
| **Reinicio automático** | Supervisor o Kubernetes reinicia el proceso |
| **Circuit breaker** | Corta el tráfico si el error supera un umbral |
| **Rollback** | Vuelta a la versión anterior si la nueva falla |
| **Modo degradado** | Responder con modelo más ligero ante sobrecarga |
| **Cola de peticiones** | Acepta más peticiones de las que procesa en tiempo real |

---

<!-- _class: lead -->

# UD6
## Seguridad, privacidad y trazabilidad de la infraestructura

---

## UD6 · Riesgos y controles de acceso

**Riesgos específicos de la infraestructura LLM:**

| Riesgo | Descripción |
|---|---|
| Exposición no autorizada | El endpoint es accesible sin autenticación |
| Acceso indebido al modelo | Los pesos del modelo pueden copiarse |
| Fuga de información | El historial de conversaciones se expone |
| Consumo no controlado | Uso masivo sin cuotas agota los recursos |
| Manipulación de configuración | Cambios no autorizados en parámetros del motor |

**Controles de acceso:**
- **Mínimo privilegio:** cada componente accede solo a lo que necesita
- **Separación de funciones:** inferencia, administración y monitorización con roles distintos
- **Gestión de secretos:** API keys y tokens nunca en código; usar Vault o equivalente
- **Restricciones de red:** VPN, allowlists de IP, tráfico cifrado (HTTPS/TLS)

---

## UD6 · Trazabilidad y límites de uso

**Supervisión de registros y trazabilidad:**
- Registrar cada petición: usuario, timestamp, versión del modelo, longitud de entrada/salida
- Almacenar trazas con retención definida por política de privacidad
- Monitorizar errores, latencias anómalas y cambios de configuración

**Límites de uso y consumo:**

| Límite | Mecanismo |
|---|---|
| Cuota por usuario | API Gateway, límite por token o por petición |
| Frecuencia (rate limiting) | X peticiones/segundo/usuario |
| Tamaño de entrada/salida | Configuración del motor de inferencia |
| Concurrencia | `max_concurrent_requests` en el motor |
| Parada controlada | Degradación gradual antes del apagado forzoso |

---

<!-- _class: lead -->

# UD7
## Responsabilidad, sostenibilidad, PRL y residuos

---

## UD7 · Sostenibilidad en la infraestructura LLM

**Decisiones de sostenibilidad en el dimensionamiento:**

- Usar cuantización (INT4/INT8) para reducir VRAM y energía sin pérdida significativa
- Preferir modelos más pequeños cuando cumplen los requisitos de calidad
- Apagar recursos inactivos: instancias spot, auto-shutdown nocturno, scheduling
- Evitar el sobredimensionamiento: comenzar con recursos mínimos y escalar solo si es necesario
- Reutilizar hardware existente antes de provisionar nuevos servidores

**Principio DNSH y ODS aplicables:**
- ODS 7 (Energía asequible y no contaminante)
- ODS 9 (Industria, innovación e infraestructura)
- ODS 12 (Producción y consumo responsables)

---

## UD7 · PRL y gestión de residuos en infraestructura GPU

**EPI para trabajo con infraestructura de IA:**

| EPI | Riesgo que protege |
|---|---|
| Calzado de seguridad aislante | Riesgo eléctrico, cargas pesadas |
| Guantes antiestáticos | Descargas ESD en componentes |
| Gafas de protección | Manipulación de rack, soldaduras |

**Plan de emergencias:** conocer el protocolo específico para sala de servidores (temperatura, extinción sin agua, corte de suministro eléctrico)

**Gestión de RAEE (GPUs, servidores):**
- Borrado seguro de modelos y datos antes de la retirada
- Entrega a gestor autorizado con certificado de destrucción
- Preferir la reutilización y la reventa antes del reciclaje

---

## Criterios de evaluación — MP04

- Determina el entorno de ejecución e identifica características del modelo y restricciones
- Calcula la memoria y los aceleradores necesarios; dimensiona con criterios de eficiencia
- Habilita el SO y dependencias; instala y configura el motor de inferencia; valida con cargas
- Incorpora y parametriza el modelo; configura la ejecución; expone el servicio
- Ejecuta pruebas de carga y concurrencia; identifica límites; verifica la recuperación
- Gestiona accesos con mínimo privilegio; supervisa trazabilidad; aplica límites de uso
- Integra sostenibilidad en el dimensionamiento; gestiona RAEE; aplica EPI y ergonomía

---

<!-- _class: lead -->

# MP04 · Infraestructura para la ejecución de LLMs

**160 h · Curso 2.º · CPE_5074_3 · Nivel 3**

*CFS — Instalación, despliegue y explotación de sistemas de IA (IAD)*
