---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD4 · Puesta en servicio del modelo | MP04 · Infraestructura para la ejecución de LLMs'
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

# UD4 · Puesta en servicio del modelo

MP04 · Infraestructura para la ejecución de LLMs

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Incorporar un modelo LLM verificando integridad, versión, formato, licencia y compatibilidad
- Comparar variantes de cuantización (INT4, INT8, FP16) y seleccionar la adecuada según requisitos
- Configurar los parámetros de ejecución (longitud de contexto, tokens, concurrencia, timeouts)
- Exponer el modelo mediante API REST compatible con OpenAI u otros modos de acceso
- Registrar el despliegue documentando carga, estabilidad, accesos y límites

---

## Incorporación del modelo — fuentes y proceso

El modelo puede provenir de distintas fuentes. La trazabilidad comienza aquí.

| Fuente | Método | Cuándo usarla |
|---|---|---|
| **Hugging Face Hub** | `huggingface-cli download` | Modelos públicos open source |
| **Repositorio interno** | `scp`, `rsync`, `s3 cp` | Modelos propios o fine-tuned |
| **Registro de contenedores** | `docker pull` | Modelos empaquetados |
| **Ollama library** | `ollama pull` | Modelos gestionados por Ollama |

```bash
# Descarga desde Hugging Face con autenticación
pip install huggingface-hub
huggingface-cli login --token $HF_TOKEN

huggingface-cli download \
  meta-llama/Llama-3.1-8B-Instruct \
  --local-dir /models/llama-3.1-8b-instruct \
  --include "*.safetensors" "*.json" "tokenizer*"
```

---

## Verificación de integridad del modelo

La verificación es obligatoria antes de cargar cualquier modelo. Un modelo corrupto o manipulado puede producir salidas incorrectas o suponer un riesgo de seguridad.

### Verificación con SHA-256

```bash
# Generar hash del archivo descargado
sha256sum /models/llama-3.1-8b/model-00001-of-00004.safetensors

# Comparar con el hash publicado por el autor
# (disponible en la página del modelo en HuggingFace, pestaña "Files and versions")

# Script de verificación automática
verify_model() {
    local MODEL_DIR="$1"
    local HASH_FILE="$2"  # Archivo con hashes oficiales

    echo "Verificando integridad del modelo en $MODEL_DIR..."
    while IFS= read -r line; do
        expected_hash=$(echo "$line" | awk '{print $1}')
        filename=$(echo "$line" | awk '{print $2}')
        actual_hash=$(sha256sum "$MODEL_DIR/$filename" | awk '{print $1}')
        if [ "$expected_hash" != "$actual_hash" ]; then
            echo "ERROR: Hash incorrecto en $filename"
            return 1
        fi
    done < "$HASH_FILE"
    echo "Verificacion completada: todos los hashes son correctos"
}
```

---

## Verificación de formato, licencia y compatibilidad

### Verificación de formato

```bash
# Comprobar que el archivo GGUF es válido
./build/bin/llama-cli --model /models/model.gguf --check

# Para SafeTensors: verificar cabecera JSON
python3 -c "
import json, struct
with open('/models/model.safetensors', 'rb') as f:
    length = struct.unpack('<Q', f.read(8))[0]
    metadata = json.loads(f.read(length))
    print('Capas encontradas:', len(metadata))
    print('dtype:', list(metadata.values())[0].get('dtype'))
"
```

### Lista de comprobación antes del despliegue

| Verificación | Herramienta / Fuente | Resultado esperado |
|---|---|---|
| Hash SHA-256 | `sha256sum` | Igual al publicado |
| Versión del modelo | Nombre del archivo / `config.json` | Coincide con el planificado |
| Formato compatible | Motor de inferencia | Sin errores de carga |
| Licencia de uso | LICENSE en el repositorio | Uso comercial permitido (si aplica) |
| Compatibilidad tokenizer | `tokenizer_config.json` | Misma versión que el fine-tuning |

---

## Variantes de cuantización — comparativa

La elección de la variante afecta la VRAM, la velocidad de inferencia y la calidad de las respuestas.

| Variante | Formato | VRAM (7B) | Velocidad TGS | Calidad |
|---|---|---|---|---|
| **FP16** | SafeTensors | ~14 GB | Alta (GPU BW limitante) | Referencia |
| **BF16** | SafeTensors | ~14 GB | Alta | Igual a FP16 |
| **INT8** (GPTQ) | SafeTensors | ~7 GB | Alta | -1 a -2 % calidad |
| **AWQ** (INT4) | SafeTensors | ~4 GB | Muy alta | -2 a -4 % calidad |
| **Q4_K_M** (GGUF) | GGUF | ~4 GB | Alta (CPU-friendly) | -2 a -3 % calidad |
| **Q5_K_M** (GGUF) | GGUF | ~5 GB | Alta | -1 a -2 % calidad |
| **Q8_0** (GGUF) | GGUF | ~8 GB | Media | -0,5 % calidad |

### Criterio de selección

- **GPU con VRAM abundante (>= 16 GB):** BF16 o FP16 para máxima calidad
- **GPU de consumo (8-24 GB):** AWQ o Q4_K_M para equilibrio rendimiento/calidad
- **CPU-only o RAM limitada:** Q4_K_M como mínimo viable

---

## Parámetros de ejecución — configuración completa

```python
# Configuración de parámetros de ejecución (vLLM)
from vllm import LLM, SamplingParams

# Parámetros del servidor
SERVER_CONFIG = {
    "model": "/models/llama-3.1-8b-instruct",
    "dtype": "bfloat16",
    "max_model_len": 8192,          # Contexto máximo
    "max_num_seqs": 32,             # Peticiones concurrentes
    "gpu_memory_utilization": 0.90, # 90% VRAM para KV cache
    "tensor_parallel_size": 1,      # GPUs en paralelo
    "enforce_eager": False,         # Usar CUDA graphs (más rápido)
}

# Parámetros de generación por petición
GENERATION_DEFAULTS = {
    "max_tokens": 1024,      # Tokens máximos de salida
    "temperature": 0.7,      # Aleatoriedad
    "top_p": 0.9,            # Nucleus sampling
    "stop": ["</s>", "[INST]"],  # Tokens de parada
    "repetition_penalty": 1.1,
}
```

---

## Parámetros de ejecución — tabla de referencia

| Parámetro | Descripción | Valor típico | Impacto |
|---|---|---|---|
| `max_model_len` | Tokens máximos de contexto (entrada + salida) | 4 096 – 32 768 | VRAM (KV cache) |
| `max_tokens` | Tokens máximos de salida por petición | 256 – 4 096 | Tiempo de respuesta |
| `max_num_seqs` | Peticiones simultáneas en el batch | 8 – 128 | VRAM, throughput |
| `gpu_memory_utilization` | Fracción de VRAM para KV cache | 0.85 – 0.95 | Estabilidad vs. throughput |
| `request_timeout` | Segundos antes de cancelar una petición | 30 – 120 | Experiencia de usuario |
| `user_quota` | Peticiones por usuario por minuto | 10 – 60 | Protección de recursos |
| `stop_sequences` | Tokens que detienen la generación | Según el modelo | Calidad de salida |

> `gpu_memory_utilization` a 0.95 maximiza el throughput pero deja poco margen antes del OOM (Out of Memory). Para producción, 0.88-0.90 es más seguro.

---

## Exposición del modelo — modos disponibles

### API REST compatible con OpenAI

El modo más común: expone endpoints `/v1/chat/completions` y `/v1/completions`.

```bash
# Probar el endpoint con curl
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "llama-3.1-8b-instruct",
    "messages": [
      {"role": "system", "content": "Eres un asistente técnico."},
      {"role": "user", "content": "Explica qué es PagedAttention."}
    ],
    "max_tokens": 300,
    "temperature": 0.7
  }'
```

> La compatibilidad con la API de OpenAI permite usar el LLM local como reemplazo directo en aplicaciones que ya usan el SDK oficial de OpenAI, cambiando solo `base_url`.

---

## Exposición del modelo — microservicio con FastAPI

```python
# Wrapper FastAPI sobre el motor de inferencia
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import httpx, os

app = FastAPI(title="LLM Service")
security = HTTPBearer()
BACKEND_URL = "http://localhost:8000"
VALID_KEY = os.environ["SERVICE_API_KEY"]

class ChatRequest(BaseModel):
    messages: list[dict]
    max_tokens: int = 512
    temperature: float = 0.7

def verify_key(creds: HTTPAuthorizationCredentials = Depends(security)):
    if creds.credentials != VALID_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return creds.credentials

@app.post("/chat")
async def chat(req: ChatRequest, _: str = Depends(verify_key)):
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(f"{BACKEND_URL}/v1/chat/completions",
            json={"model": "llama-3.1-8b", "messages": req.messages,
                  "max_tokens": req.max_tokens, "temperature": req.temperature})
    return resp.json()
```

---

## Registro del despliegue

El registro del despliegue es el documento de trazabilidad que vincula el modelo con su configuración y sus accesos.

```markdown
## Registro de despliegue — 2026-06-23

### Modelo
- Nombre: Llama 3.1 8B Instruct
- Versión: meta-llama/Llama-3.1-8B-Instruct (commit: a1b2c3d4)
- Formato: SafeTensors BF16
- Hash SHA-256 (model-00001): 3f4a...c9d2 (VERIFICADO)
- Licencia: Llama 3.1 Community License — uso interno permitido

### Configuración de ejecución
- Motor: vLLM 0.4.2
- Contexto máximo: 8 192 tokens
- Concurrencia máxima: 32 peticiones
- Utilización VRAM: 90 %

### Resultado de la puesta en servicio
- Tiempo de carga: 18 s
- VRAM utilizada al arrancar: 16,4 GB / 24 GB
- Primera petición (prueba): OK — 1,2 s TTFT, 48 tok/s
- Accesos autorizados: equipo de desarrollo (10 usuarios), API key rotada

### Incidencias
- Ninguna
```

---

## Actividad práctica — Puesta en servicio

### Escenario

Poner en servicio el modelo `Qwen2.5-7B-Instruct` en un servidor con vLLM. Los requisitos son:

- Contexto de 16 384 tokens
- Hasta 16 peticiones simultáneas
- Exposición mediante API REST con autenticación por Bearer token
- Registro completo del despliegue
- Timeout de 90 segundos por petición

### Tareas

1. Escribe el comando de descarga desde Hugging Face y el script de verificación de integridad SHA-256
2. Escoge la variante de cuantización más adecuada para una GPU con 24 GB VRAM y justifícala
3. Escribe el comando completo de arranque de vLLM con todos los parámetros del escenario
4. Prueba el endpoint con un `curl` que incluya autenticación y una pregunta técnica
5. Completa el registro de despliegue con los resultados obtenidos (o simulados)

---

## Puntos clave — UD4

- La **verificación SHA-256** no es opcional: garantiza que el modelo descargado no está corrupto ni ha sido manipulado. Debe hacerse antes de cargarlo en el motor.

- La **cuantización INT4 (AWQ, Q4_K_M)** permite usar modelos de 7B-13B en GPUs de 8-16 GB con una pérdida de calidad inferior al 4 % respecto a BF16.

- La **API REST compatible con OpenAI** es el modo de exposición más interoperable: permite reutilizar cualquier SDK o aplicación existente simplemente cambiando la `base_url`.

- El **registro de despliegue** es el punto de partida de toda la trazabilidad operativa: versión exacta del modelo, hash, configuración, accesos autorizados y resultado de la primera prueba.

- El parámetro `max_num_seqs` (vLLM) o `--parallel` (llama.cpp) define la concurrencia máxima y debe alinearse con la VRAM disponible para el caché KV.

---

## Criterios de evaluación — UD4

| Criterio | Indicadores de logro |
|---|---|
| **Incorpora y verifica el modelo** | Descarga desde fuente autorizada; verifica SHA-256; comprueba licencia |
| **Parametriza la variante** | Justifica la cuantización elegida con criterios de VRAM y calidad |
| **Configura la ejecución** | Establece contexto, tokens, concurrencia, timeout y cuotas |
| **Expone el modelo** | Lanza el endpoint y verifica que responde a peticiones autenticadas |
| **Registra el despliegue** | Documento con versión exacta, hash, configuración, accesos e incidencias |

> **Referencia:** resultado de aprendizaje RA4 — "Pone en servicio modelos LLM configurando parámetros de ejecución, acceso y exposición a aplicaciones consumidoras."

---

[← Volver a MP04](../index.md)


---

<!-- nav-slide -->

## Navegación

[← UD3 · Preparación del entorno de ej…](../UD3_Preparacion-entorno-ejecucion/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD5 · Validación de la capacidad op… →](../UD5_Validacion-capacidad-operativa/)
