---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD5 · Validación de la capacidad operativa | MP04 · Infraestructura para la ejecución de LLMs'
footer: 'Apuntes de IA y Datos'
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

# UD5 · Validación de la capacidad operativa

MP04 · Infraestructura para la ejecución de LLMs

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Identificar y medir las métricas clave de rendimiento de un sistema LLM (TTFT, TPS, percentiles de latencia)
- Diseñar y ejecutar pruebas de carga, concurrencia y estabilidad
- Identificar los límites operativos del sistema (punto de saturación, comportamiento en fallo)
- Configurar mecanismos de recuperación y continuidad (reinicio automático, circuit breaker, rollback, modo degradado)
- Documentar los resultados de validación con métricas, límites e incidencias

---

## Métricas de rendimiento — TTFT y TGS

### TTFT (Time to First Token)

Tiempo desde que el cliente envía la petición hasta que recibe el primer token de la respuesta.

- Incluye: red + tokenización + prefill (procesamiento del prompt)
- Crítico para la experiencia interactiva
- Valor de referencia: < 2 s para chat, < 500 ms para APIs en pipeline

### TGS (Token Generation Speed) / TPS (Tokens per Second)

Velocidad de generación de tokens una vez iniciada la respuesta.

- Determinado por el ancho de banda de memoria de la GPU
- Valor de referencia: > 15 tok/s para lectura fluida, > 50 tok/s para aplicaciones

| GPU | TGS aproximado (7B BF16) | TGS aproximado (7B INT4) |
|---|---|---|
| RTX 4090 | ~50 tok/s | ~90 tok/s |
| A100 80 GB | ~70 tok/s | ~120 tok/s |
| H100 SXM | ~120 tok/s | ~200 tok/s |

---

## Métricas de rendimiento — percentiles y recursos

### Percentiles de latencia

Los percentiles describen la distribución real de los tiempos de respuesta bajo carga.

| Percentil | Descripción | Referencia |
|---|---|---|
| **P50** (mediana) | El 50 % de las peticiones son más rápidas | Rendimiento típico |
| **P95** | El 95 % de las peticiones son más rápidas | Rendimiento con carga alta |
| **P99** | El 99 % de las peticiones son más rápidas | Comportamiento en el peor caso |

> Un P99 muy alto (o "cola larga") indica que algunas peticiones experimentan degradación severa, aunque la mayoría sean rápidas. Siempre medir P95 y P99, no solo la media.

### Recursos a monitorizar

| Recurso | Herramienta | Indicador de saturación |
|---|---|---|
| VRAM GPU | `nvidia-smi`, `nvtop` | > 95 % utilización |
| CPU | `htop`, `mpstat` | > 80 % en varios núcleos |
| RAM | `free -h`, `vmstat` | Swap activo |
| Red | `iftop`, `nload` | Saturación de la NIC |

---

## Herramientas de prueba de carga

### Locust (Python)

```python
# locustfile.py — prueba de carga para endpoint LLM
from locust import HttpUser, task, between
import json, random

PROMPTS = [
    "Explica qué es la atención multi-cabeza en un transformer.",
    "Describe los pasos para cuantizar un modelo LLM a INT4.",
    "Diferencia entre VRAM y RAM en el contexto de la inferencia de LLMs.",
]

class LLMUser(HttpUser):
    wait_time = between(1, 3)  # Espera entre peticiones por usuario

    @task
    def generate(self):
        self.client.post(
            "/v1/chat/completions",
            headers={"Authorization": "Bearer test-key"},
            json={
                "model": "llama-3.1-8b-instruct",
                "messages": [{"role": "user", "content": random.choice(PROMPTS)}],
                "max_tokens": 200,
            },
            timeout=60,
        )
```

```bash
# Ejecutar: 20 usuarios, rampa de 2 usuarios/segundo
locust -f locustfile.py --host http://localhost:8000 \
  -u 20 -r 2 --run-time 5m --headless --csv=resultados_carga
```

---

## Prueba de carga con script Python asyncio

```python
import asyncio, httpx, time, statistics

async def peticion_llm(client: httpx.AsyncClient, prompt: str) -> dict:
    start = time.perf_counter()
    resp = await client.post(
        "http://localhost:8000/v1/chat/completions",
        headers={"Authorization": "Bearer test-key"},
        json={
            "model": "llama-3.1-8b-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
            "stream": False,
        },
        timeout=120,
    )
    ttft = time.perf_counter() - start
    data = resp.json()
    tokens = data["usage"]["completion_tokens"]
    return {"ttft": ttft, "tokens": tokens, "tps": tokens / ttft}

async def prueba_concurrencia(n_usuarios: int):
    prompt = "Explica la diferencia entre GGUF y SafeTensors en 50 palabras."
    async with httpx.AsyncClient() as client:
        tareas = [peticion_llm(client, prompt) for _ in range(n_usuarios)]
        resultados = await asyncio.gather(*tareas, return_exceptions=True)
    ttfts = [r["ttft"] for r in resultados if isinstance(r, dict)]
    print(f"Usuarios: {n_usuarios} | P50: {statistics.median(ttfts):.2f}s"
          f" | P95: {sorted(ttfts)[int(len(ttfts)*0.95)]:.2f}s")

asyncio.run(prueba_concurrencia(20))
```

---

## Identificación de límites operativos

El objetivo es encontrar el punto en que el sistema deja de comportarse correctamente.

### Protocolo de prueba de saturación

```bash
# Prueba escalonada: aumentar la concurrencia gradualmente
for USUARIOS in 1 5 10 20 30 40 50; do
    echo "=== Prueba con $USUARIOS usuarios concurrentes ==="
    python3 -c "
import asyncio
from test_client import prueba_concurrencia
asyncio.run(prueba_concurrencia($USUARIOS))
"
    # Capturar uso de VRAM en ese momento
    nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader
    sleep 30  # Dejar que el sistema se estabilice
done
```

### Indicadores de saturación

| Indicador | Umbral de alerta | Umbral crítico |
|---|---|---|
| TTFT | > 5 s | > 15 s |
| VRAM | > 95 % | OOM error |
| Tasa de error HTTP | > 1 % | > 5 % |
| Peticiones en cola | > 2× capacidad | Cola desbordada |
| TGS por usuario | Caída > 30 % | Caída > 60 % |

---

## Mecanismos de recuperación — reinicio automático

### Systemd como supervisor del servicio

```ini
# /etc/systemd/system/llm-server.service
[Unit]
Description=LLM Inference Server (vLLM)
After=network.target
Requires=network.target

[Service]
Type=simple
User=llmservice
WorkingDirectory=/opt/llm
EnvironmentFile=/opt/llm/.env
ExecStart=/opt/llm-env/bin/python -m vllm.entrypoints.openai.api_server \
          --model /models/llama-3.1-8b \
          --dtype bfloat16 --max-model-len 8192 --port 8000
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable llm-server
sudo systemctl start llm-server
# Ver estado y logs
journalctl -u llm-server -f
```

---

## Mecanismos de recuperación — circuit breaker y rollback

### Circuit Breaker

El circuit breaker corta el tráfico hacia el servidor LLM cuando la tasa de errores supera un umbral, evitando la cascada de fallos.

```python
import time
from enum import Enum

class Estado(Enum):
    CERRADO = "cerrado"     # Funcionamiento normal
    ABIERTO = "abierto"     # Rechaza peticiones
    SEMIABIERTO = "semiabierto"  # Prueba recuperación

class CircuitBreaker:
    def __init__(self, umbral_fallos=5, tiempo_reset=60):
        self.estado = Estado.CERRADO
        self.contador_fallos = 0
        self.umbral = umbral_fallos
        self.tiempo_reset = tiempo_reset
        self.tiempo_apertura = None

    def puede_pasar(self) -> bool:
        if self.estado == Estado.ABIERTO:
            if time.time() - self.tiempo_apertura > self.tiempo_reset:
                self.estado = Estado.SEMIABIERTO
                return True
            return False
        return True

    def registrar_fallo(self):
        self.contador_fallos += 1
        if self.contador_fallos >= self.umbral:
            self.estado = Estado.ABIERTO
            self.tiempo_apertura = time.time()
```

---

## Mecanismos de recuperación — rollback y modo degradado

### Rollback

Estrategia para volver a una versión anterior del modelo o la configuración si la nueva falla.

```bash
# Estructura de versiones para facilitar rollback
/models/
  llama-3.1-8b-instruct-v1.0/   # Versión anterior (estable)
  llama-3.1-8b-instruct-v1.1/   # Nueva versión (en prueba)
  current -> llama-3.1-8b-instruct-v1.1  # Symlink a la activa

# Rollback: cambiar el symlink
ln -sfn /models/llama-3.1-8b-instruct-v1.0 /models/current
sudo systemctl restart llm-server
```

### Modo degradado

Cuando el sistema principal está sobrecargado, se sirve con un modelo más ligero.

| Situación | Modelo principal | Modelo degradado |
|---|---|---|
| Carga normal | Llama 3.1 70B Q4 | — |
| Saturación > 80 % | Llama 3.1 70B Q4 | Llama 3.1 8B INT4 |
| Fallo del servidor GPU | Llama 3.1 8B INT4 | API externa (fallback) |

---

## Cola de peticiones con gestión de espera

```python
import asyncio
from fastapi import FastAPI, HTTPException

app = FastAPI()
cola = asyncio.Queue(maxsize=100)  # Máximo 100 peticiones esperando
semaforo = asyncio.Semaphore(16)   # Máximo 16 en proceso simultáneo

@app.post("/v1/chat/completions")
async def completions(request: dict):
    # Rechazar si la cola está llena
    if cola.full():
        raise HTTPException(status_code=503,
            detail="Servidor saturado. Intente de nuevo en unos segundos.")
    await cola.put(request)
    try:
        async with semaforo:
            peticion = await cola.get()
            resultado = await procesar_con_llm(peticion)
            return resultado
    finally:
        cola.task_done()

async def procesar_con_llm(request: dict) -> dict:
    # Llamar al motor de inferencia interno
    async with httpx.AsyncClient() as client:
        resp = await client.post("http://localhost:8000/v1/chat/completions",
                                 json=request, timeout=120)
        return resp.json()
```

---

## Documentación de validación

```markdown
## Informe de validación operativa — 2026-06-23

### Sistema validado
- Motor: vLLM 0.4.2 · Modelo: Llama 3.1 8B Instruct BF16
- GPU: NVIDIA RTX 4090 24 GB · Host: Ubuntu 22.04

### Resultados de pruebas de carga

| Concurrencia | P50 TTFT | P95 TTFT | TGS medio | VRAM | Errores |
|---|---|---|---|---|---|
| 1 usuario | 0,8 s | 1,1 s | 52 tok/s | 16 GB | 0 % |
| 5 usuarios | 1,2 s | 2,1 s | 48 tok/s | 17 GB | 0 % |
| 10 usuarios | 2,4 s | 4,8 s | 38 tok/s | 19 GB | 0 % |
| 16 usuarios | 4,1 s | 9,2 s | 28 tok/s | 22 GB | 0 % |
| 20 usuarios | 8,3 s | 22 s | 18 tok/s | 23,8 GB | 3 % |

### Límite operativo identificado
- Punto de saturación: 16 usuarios concurrentes (P95 > 9 s supera requisito)
- Límite recomendado para producción: 12 usuarios simultáneos

### Recomendaciones
1. Limitar max_num_seqs a 12 para garantizar SLA de P95 < 5 s
2. Activar modo degradado con modelo 7B INT4 si la cola supera 20 peticiones
```

---

## Actividad práctica — Validación operativa

### Escenario

Se ha desplegado vLLM con Mistral 7B BF16 en una GPU A10G (24 GB VRAM). Los requisitos de servicio son: TTFT P95 < 5 s, disponibilidad 99 %, hasta 10 usuarios concurrentes.

### Tareas

1. Escribe el `locustfile.py` completo para una prueba de carga con 10 usuarios durante 5 minutos
2. Define la secuencia escalonada de prueba (1, 5, 10, 15, 20 usuarios) y explica qué mides en cada paso
3. Diseña la tabla de resultados que entregarías en el informe de validación (columnas, umbrales)
4. Escribe el archivo `llm-server.service` para systemd con reinicio automático en caso de fallo
5. Propón una estrategia de modo degradado para cuando la carga supere el límite identificado

---

## Puntos clave — UD5

- **TTFT y TGS son métricas distintas** con causas distintas: el TTFT depende del prefill (longitud del prompt), el TGS depende del ancho de banda de la GPU.

- Los **percentiles P95 y P99** son más informativos que la media: revelan el comportamiento en los peores casos, que son los que percibe el usuario más lento.

- El **punto de saturación** se identifica buscando el nivel de concurrencia donde la tasa de error supera el 1 % o la latencia P95 supera el SLA definido.

- El **circuit breaker** es esencial para evitar que un servidor LLM sobrecargado degrade toda la infraestructura. Sin él, las peticiones en cola pueden acumularse indefinidamente.

- La **documentación de validación** no es un trámite: es el único documento que demuestra que el sistema cumple los requisitos de servicio antes de la apertura a usuarios reales.

---

## Criterios de evaluación — UD5

| Criterio | Indicadores de logro |
|---|---|
| **Ejecuta pruebas de carga y concurrencia** | Diseña y ejecuta prueba escalonada; mide TTFT, TGS y P95/P99 |
| **Identifica límites operativos** | Determina el punto de saturación y el máximo de usuarios recomendado |
| **Comprueba la recuperación** | Configura reinicio automático; verifica comportamiento tras un fallo |
| **Documenta los resultados** | Entrega tabla de métricas, límites operativos e incidencias con recomendaciones |
| **Propone mejoras** | Sugiere ajuste de parámetros o cambio de estrategia de escalado |

> **Referencia:** resultado de aprendizaje RA5 — "Valida la capacidad operativa ejecutando pruebas de carga, concurrencia, estabilidad y recuperación."

---

[← Volver a MP04](../index.md)


---

<!-- nav-slide -->

## Navegación

[← UD4 · Puesta en servicio del modelo](../UD4_Puesta-servicio-modelo/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD6 · Seguridad, privacidad y traza… →](../UD6_Seguridad-privacidad-trazabilidad/)
