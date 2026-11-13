# UD4 · Puesta en servicio del modelo LLM

---

## 1. Introducción

Disponer de un modelo cargado en memoria GPU y capaz de generar texto no es equivalente a disponer de un servicio de inferencia listo para producción. La puesta en servicio de un modelo LLM es el proceso de transición entre un proceso de inferencia local y un servicio de API estable, seguro, escalable y observable. Esta transición implica decisiones de arquitectura que afectarán directamente al rendimiento, la disponibilidad y el coste operativo del sistema durante toda su vida útil en producción.

El primer elemento de la puesta en servicio es la definición y exposición de la API de inferencia. El formato de API compatible con OpenAI se ha consolidado como el estándar de facto del ecosistema LLM: la especificación de los endpoints `/v1/chat/completions` y `/v1/completions`, con sus parámetros de generación (temperature, top_p, top_k, max_tokens, stop sequences), es conocida por la mayoría de los frameworks de cliente y facilita la interoperabilidad. Los frameworks de inferencia modernos como vLLM, TGI y LMDeploy exponen este formato de API nativamente, lo que reduce significativamente el trabajo de integración.

La exposición directa del servidor de inferencia a Internet o a la red corporativa sin un nivel de intermediación es una práctica que introduce riesgos significativos: falta de terminación TLS, ausencia de autenticación, imposibilidad de balancear carga entre réplicas y ausencia de capacidades de rate limiting. La inserción de un reverse proxy (nginx, Traefik, Envoy) entre el servidor de inferencia y los clientes resuelve estos problemas y añade capacidades de observabilidad sin modificar el servidor de inferencia.

La gestión del ciclo de vida del modelo en producción —actualizaciones de versión, estrategias de rollout, warm-up antes de recibir tráfico— define la madurez operativa del sistema. Un modelo que no ha realizado las primeras inferencias de calentamiento antes de recibir tráfico real presentará latencias anómalas en sus primeras respuestas, lo que puede disparar errores en los clientes por timeout. Las estrategias de despliegue progresivo (rolling update, blue-green, canary) permiten actualizar el modelo en producción sin interrupciones del servicio ni degradaciones bruscas de la experiencia del usuario.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Describir el formato de API compatible con OpenAI para LLMs (endpoints, parámetros de generación, estructura de mensajes) y explicar el efecto de cada parámetro sobre el output generado.
2. Configurar vLLM como servidor de producción, ajustando los parámetros de tensor parallel size, max batch size, max model len y gpu_memory_utilization según los requisitos de rendimiento y los recursos disponibles.
3. Configurar Text Generation Inference con sharding multi-GPU, cuantización y las opciones de trust_remote_code, y verificar el comportamiento del servidor bajo carga.
4. Desplegar un reverse proxy nginx o Traefik con terminación TLS y configurar el balanceo de carga entre múltiples réplicas del servidor de inferencia.
5. Implementar colas de solicitudes, configurar timeouts adecuados para solicitudes de LLM y diseñar el esquema de gestión de errores para el servicio de inferencia.
6. Configurar health checks y readiness probes en Kubernetes para pods de inferencia de LLMs, considerando los tiempos de carga del modelo.
7. Diseñar y ejecutar una estrategia de warm-up de modelo antes de recibir tráfico de producción, verificando la estabilización de la latencia.
8. Implementar y comparar al menos dos estrategias de rollout (rolling update, blue-green o canary) para actualizar un modelo en producción sin interrupción del servicio.

---

## 3. API de inferencia de LLMs

### 3.1 La especificación OpenAI-compatible

La especificación de API de OpenAI se ha convertido en el estándar de interoperabilidad del ecosistema de LLMs en producción. Todos los frameworks de inferencia relevantes la implementan, todos los frameworks de cliente (LangChain, LlamaIndex, Semantic Kernel) la soportan de forma nativa, y todos los proxies y gateways de LLM (LiteLLM, PortKey, OpenRouter) pueden enrutar hacia ella.

Los dos endpoints principales son:

- **`POST /v1/chat/completions`**: Interfaz de chat, basada en un array de mensajes con roles (`system`, `user`, `assistant`). Es el formato recomendado para la mayoría de los LLMs modernos de tipo instruction-tuned.
- **`POST /v1/completions`**: Interfaz de completado de texto, basada en un prompt de texto plano. Útil para modelos base no instruction-tuned y para casos de uso de completado de código.

Adicionalmente, el endpoint `GET /v1/models` lista los modelos disponibles en el servidor, y `GET /health` (o `/v1/health`) proporciona el estado del servidor para los health checks.

### 3.2 Estructura de mensajes y parámetros de generación

El cuerpo de una solicitud a `/v1/chat/completions` tiene la siguiente estructura:

```json
{
  "model": "meta-llama/Llama-3.1-8B-Instruct",
  "messages": [
    {
      "role": "system",
      "content": "Eres un asistente técnico especializado en infraestructura de IA."
    },
    {
      "role": "user",
      "content": "Explica qué es la KV cache en el contexto de los LLMs."
    }
  ],
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 50,
  "max_tokens": 512,
  "stop": ["\n\n", "###"],
  "stream": false,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "n": 1,
  "user": "usuario-anonimizado-123"
}
```

### 3.3 Parámetros de generación: efecto y configuración recomendada

| Parámetro | Rango | Efecto | Valor prod. recomendado |
|---|---|---|---|
| `temperature` | 0.0 – 2.0 | Controla la aleatoriedad. 0 = determinista, >1 = más aleatorio. | 0.0–0.3 para tareas factuales; 0.7–1.0 para tareas creativas |
| `top_p` | 0.0 – 1.0 | Muestreo por núcleo: considera solo los tokens cuya prob. acumulada ≤ top_p. | 0.9–0.95 como valor por defecto |
| `top_k` | 1 – ∞ | Limita el muestreo a los k tokens más probables. | 50; desactivar (0) si se usa top_p |
| `max_tokens` | 1 – ctx_len | Número máximo de tokens a generar. | Configurar según el caso de uso; nunca dejar sin límite |
| `stop` | Array de strings | El modelo para al generar cualquiera de estas cadenas. | Adaptar al formato de salida esperado |
| `frequency_penalty` | -2.0 – 2.0 | Penaliza tokens ya usados en proporción a su frecuencia. | 0.0–0.3 para reducir repeticiones |
| `presence_penalty` | -2.0 – 2.0 | Penaliza cualquier token ya aparecido (penalidad fija). | 0.0–0.5 para estimular variedad |
| `stream` | boolean | Devuelve los tokens en streaming SSE en lugar de en una sola respuesta. | true para interfaces de usuario en tiempo real |

---

## 4. Configuración de vLLM para producción

### 4.1 Parámetros fundamentales del servidor

vLLM expone un extenso conjunto de parámetros de configuración que deben ajustarse según las características del hardware, el modelo y los requisitos de carga esperados:

```bash
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-70B-Instruct \
    \
    # Paralelismo de tensor: número de GPUs sobre las que se distribuye el modelo
    --tensor-parallel-size 4 \
    \
    # Longitud máxima de contexto (prompt + respuesta)
    --max-model-len 32768 \
    \
    # Fracción de memoria GPU que puede usar vLLM para la KV cache
    --gpu-memory-utilization 0.90 \
    \
    # Número máximo de secuencias procesadas simultáneamente (continuous batching)
    --max-num-seqs 256 \
    \
    # Número máximo de tokens en un batch de prefill
    --max-num-batched-tokens 32768 \
    \
    # Algoritmo de planificación: chunked-prefill mejora latencia en carga mixta
    --enable-chunked-prefill \
    \
    # Cuantización del modelo (opcional, reduce memoria a cambio de precisión)
    --quantization awq \
    \
    # Tipo de datos para la inferencia
    --dtype bfloat16 \
    \
    # Puerto de la API
    --port 8000 \
    \
    # Host (0.0.0.0 para aceptar conexiones externas)
    --host 0.0.0.0
```

### 4.2 Ajuste de gpu_memory_utilization y max-num-seqs

El parámetro `--gpu-memory-utilization` determina qué fracción de la memoria GPU disponible puede utilizar vLLM para la KV cache, una vez cargados los pesos del modelo. Un valor demasiado alto puede provocar errores de memoria OOM (Out of Memory); un valor demasiado bajo infrautiliza la GPU y limita el throughput:

```
Memoria GPU disponible × gpu_memory_utilization = Memoria para KV cache
```

Para un modelo de 8B en BF16 sobre una GPU de 80 GB:
- Pesos del modelo: ~16 GB
- Memoria disponible para KV cache: 80 GB × 0.90 − 16 GB = **56 GB**

El parámetro `--max-num-seqs` controla cuántas solicitudes pueden procesarse concurrentemente en el motor de continuous batching. Un valor mayor mejora el throughput pero incrementa la latencia media. Se recomienda ajustarlo empíricamente con pruebas de carga (ver UD5).

### 4.3 Modos de cuantización en vLLM

| Modo | Flag | Reducción de memoria | Impacto en calidad |
|---|---|---|---|
| AWQ (Activation-aware Weight Quantization) | `--quantization awq` | ~4x (FP16 → INT4) | Bajo |
| GPTQ | `--quantization gptq` | ~4x | Bajo-medio |
| FP8 | `--quantization fp8` | ~2x | Muy bajo |
| SqueezeLLM | `--quantization squeezellm` | ~4x | Bajo |

---

## 5. Configuración de Text Generation Inference (TGI)

### 5.1 Configuración con sharding multi-GPU

TGI gestiona el paralelismo de tensor (sharding) a través del parámetro `--num-shard`, que especifica el número de GPUs sobre las que se distribuyen los pesos del modelo:

```bash
docker run --gpus all \
    -v /models:/data \
    -p 8080:80 \
    --shm-size 2g \
    ghcr.io/huggingface/text-generation-inference:2.3 \
    --model-id meta-llama/Llama-3.1-70B-Instruct \
    --num-shard 4 \
    --max-input-tokens 8192 \
    --max-total-tokens 16384 \
    --max-batch-prefill-tokens 32768 \
    --max-concurrent-requests 512 \
    --dtype bfloat16
```

### 5.2 Cuantización y trust_remote_code

TGI admite cuantización AWQ, GPTQ y BitsAndBytes (solo NF4/FP4 con sufijos `-bnb`). El flag `--trust-remote-code` permite ejecutar código Python personalizado incluido en el repositorio del modelo; debe usarse solo con modelos de fuentes verificadas:

```bash
docker run --gpus all \
    -v /models:/data \
    -p 8080:80 \
    ghcr.io/huggingface/text-generation-inference:2.3 \
    --model-id Qwen/Qwen2.5-72B-Instruct-AWQ \
    --num-shard 4 \
    --quantize awq \
    --trust-remote-code \
    --max-input-tokens 16384 \
    --max-total-tokens 32768
```

---

## 6. Reverse proxy y exposición segura

### 6.1 nginx como reverse proxy con TLS

La configuración de nginx como reverse proxy para un servidor de inferencia LLM debe contemplar: terminación TLS, timeouts generosos (las respuestas de LLM pueden tardar decenas de segundos), y buffers configurados para las respuestas en streaming:

```nginx
upstream vllm_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name llm-api.empresa.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name llm-api.empresa.com;

    ssl_certificate     /etc/ssl/certs/llm-api.empresa.com.pem;
    ssl_certificate_key /etc/ssl/private/llm-api.empresa.com.key;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    # Timeouts adaptados a la generación de LLMs
    proxy_read_timeout  300s;
    proxy_send_timeout  300s;
    proxy_connect_timeout 10s;

    # Buffers para streaming SSE
    proxy_buffering     off;
    proxy_cache         off;

    location /v1/ {
        proxy_pass          http://vllm_backend;
        proxy_set_header    Host $host;
        proxy_set_header    X-Real-IP $remote_addr;
        proxy_set_header    X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header    X-Forwarded-Proto $scheme;
        proxy_http_version  1.1;
        proxy_set_header    Connection "";
    }

    location /health {
        proxy_pass http://vllm_backend/health;
        access_log off;
    }
}
```

### 6.2 Balanceo de carga entre réplicas

Cuando se dispone de múltiples réplicas del servidor de inferencia (para aumentar el QPS disponible), nginx puede balancear la carga entre ellas. Para LLMs, el balanceo `least_conn` es preferible a `round_robin`, ya que dirige cada nueva solicitud al servidor con menos conexiones activas, distribuyendo más equitativamente las solicitudes largas:

```nginx
upstream vllm_cluster {
    least_conn;
    server 10.0.1.11:8000 weight=1 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:8000 weight=1 max_fails=3 fail_timeout=30s;
    server 10.0.1.13:8000 weight=1 max_fails=3 fail_timeout=30s;
    keepalive 64;
}
```

### 6.3 Traefik como alternativa cloud-native

**Traefik** es preferible a nginx en entornos Kubernetes por su integración nativa con la API de Kubernetes y su capacidad de autodescubrimiento de servicios mediante anotaciones:

```yaml
# Configuración de IngressRoute Traefik para el servicio LLM
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: vllm-ingress
  namespace: llm-serving
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`llm-api.empresa.com`) && PathPrefix(`/v1/`)
      kind: Rule
      services:
        - name: vllm-service
          port: 8000
      middlewares:
        - name: vllm-ratelimit
        - name: vllm-auth
  tls:
    certResolver: letsencrypt
```

---

## 7. Gestión de colas, timeouts y health checks

### 7.1 Gestión de colas de solicitudes

vLLM implementa internamente un sistema de colas de solicitudes (scheduler). Cuando el número de solicitudes entrantes supera la capacidad de procesamiento, las solicitudes se encolan en memoria. Para controlar este comportamiento y evitar que la cola crezca indefinidamente:

```bash
# Límite máximo de solicitudes en cola simultáneas
--max-num-seqs 512

# Timeout de espera en cola (las solicitudes que superen este tiempo son rechazadas)
# Se configura a nivel de cliente o proxy, no en vLLM directamente
```

En el proxy nginx, el timeout de lectura debe configurarse considerando el tiempo máximo de espera en cola más el tiempo de generación:

```nginx
# Timeout conservador para modelos con colas largas
proxy_read_timeout 600s;
```

### 7.2 Configuración de health checks y readiness probes en Kubernetes

Los pods de inferencia de LLM tienen un tiempo de arranque significativamente mayor que los servicios web convencionales (el modelo puede tardar varios minutos en cargarse en memoria GPU). La configuración de las probes debe reflejar esta realidad:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  # Tiempo de espera antes del primer check (tiempo de carga del modelo)
  initialDelaySeconds: 300
  periodSeconds: 30
  timeoutSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  # La readiness probe es más agresiva una vez el modelo está cargado
  initialDelaySeconds: 300
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
  successThreshold: 1

startupProbe:
  httpGet:
    path: /health
    port: 8000
  # La startup probe da tiempo al modelo para cargarse completamente
  failureThreshold: 60
  periodSeconds: 10
  # Total de tiempo de espera: 60 × 10s = 600s = 10 minutos
```

---

## 8. Estrategias de rollout

### 8.1 Rolling Update

El rolling update reemplaza gradualmente las instancias de la versión anterior por instancias de la nueva versión, manteniendo siempre un número mínimo de instancias disponibles. En Kubernetes:

```yaml
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1    # Máximo de pods no disponibles durante la actualización
      maxSurge: 1          # Máximo de pods extra durante la actualización
```

Para LLMs, el rolling update tiene una limitación: si los modelos son muy grandes, el nodo puede no tener suficiente memoria GPU para ejecutar simultáneamente el pod anterior y el nuevo durante la transición.

### 8.2 Blue-Green Deployment

El despliegue blue-green mantiene dos entornos idénticos: el activo (blue) y el nuevo (green). El cambio se realiza mediante la actualización del selector del Service de Kubernetes, lo que conmuta el tráfico de forma instantánea:

```yaml
# Service que apunta al entorno activo
apiVersion: v1
kind: Service
metadata:
  name: vllm-production
spec:
  selector:
    app: vllm
    version: blue    # Cambiar a 'green' para hacer el switch
  ports:
    - port: 80
      targetPort: 8000
```

```bash
# Desplegar el entorno green (nuevo modelo) sin afectar al tráfico
kubectl set image deployment/vllm-green vllm=registry.empresa.com/vllm:llama3.1-v2

# Verificar que el entorno green está listo
kubectl rollout status deployment/vllm-green

# Cambiar el tráfico al entorno green
kubectl patch service vllm-production -p '{"spec":{"selector":{"version":"green"}}}'

# Verificar el correcto funcionamiento
# Si hay problemas, revertir instantáneamente
kubectl patch service vllm-production -p '{"spec":{"selector":{"version":"blue"}}}'
```

### 8.3 Canary Release

El canary release desvía un porcentaje reducido del tráfico al nuevo modelo para validar su comportamiento antes de hacer el rollout completo. Con Traefik o nginx con ponderación de servidores upstream:

```yaml
# Con nginx, canary enviando el 10% del tráfico al nuevo modelo
upstream vllm_weighted {
    server 10.0.1.11:8000 weight=9;   # 90% → versión estable
    server 10.0.1.20:8000 weight=1;   # 10% → versión canary
}
```

| Estrategia | Tiempo de rollout | Rollback | Consumo de recursos | Riesgo de impacto |
|---|---|---|---|---|
| Rolling Update | Gradual | Automático (kubectl rollout undo) | Mínimo extra | Medio (tráfico mixto) |
| Blue-Green | Instantáneo | Instantáneo (cambio de selector) | 2x durante la transición | Bajo |
| Canary | Configurable | Manual o automático | Moderado | Muy bajo |

---

## 9. Warm-up del modelo

### 9.1 Por qué el warm-up es crítico

La primera inferencia tras la carga del modelo puede ser significativamente más lenta que las siguientes debido a: compilación JIT de kernels CUDA (especialmente con torch.compile), inicialización de la KV cache, y cargas de memoria por cold cache del sistema operativo. Sin warm-up, los primeros usuarios reales experimentarán latencias anómalas que pueden provocar timeouts.

### 9.2 Script de warm-up automatizado

```python
#!/usr/bin/env python3
"""Warm-up del servidor de inferencia antes de recibir tráfico."""
import requests
import time
import statistics

WARMUP_URL = "http://localhost:8000/v1/chat/completions"
WARMUP_REQUESTS = 10
MODEL = "meta-llama/Llama-3.1-8B-Instruct"

def send_warmup_request(prompt_length: str = "short") -> float:
    prompts = {
        "short": "Completa: 2 + 2 =",
        "medium": "Explica en tres oraciones qué es un transformer en el contexto del aprendizaje automático.",
        "long": "Describe en detalle los mecanismos de atención multi-cabeza, incluyendo las matrices Q, K y V, "
                "el cálculo del producto escalar escalado y el proceso de softmax. "
                "Incluye la fórmula matemática y una explicación intuitiva."
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompts[prompt_length]}],
        "max_tokens": 128,
        "temperature": 0
    }
    start = time.time()
    resp = requests.post(WARMUP_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return time.time() - start

print(f"Iniciando warm-up con {WARMUP_REQUESTS} solicitudes...")
latencies = []
for i in range(WARMUP_REQUESTS):
    length = ["short", "medium", "long"][i % 3]
    lat = send_warmup_request(length)
    latencies.append(lat)
    print(f"  Solicitud {i+1}/{WARMUP_REQUESTS} ({length}): {lat:.2f}s")

print(f"\nWarm-up completado:")
print(f"  Latencia primera solicitud: {latencies[0]:.2f}s")
print(f"  Latencia última solicitud:  {latencies[-1]:.2f}s")
print(f"  Latencia media (últimas 5): {statistics.mean(latencies[-5:]):.2f}s")
print(f"  Mejora: {(1 - latencies[-1]/latencies[0])*100:.1f}%")
```

En Kubernetes, el warm-up debe completarse antes de que el pod sea marcado como `Ready`. La forma más limpia de implementarlo es mediante un Init Container o un script de post-start hook que ejecute el warm-up antes de que la readiness probe comience a retornar éxito.

---

## 10. Actividades prácticas

### Actividad 1 — Configuración del servidor vLLM y verificación de parámetros de generación

**Descripción**: Despliega un servidor vLLM con el modelo indicado por el formador. Realiza una serie de solicitudes a la API modificando sistemáticamente los parámetros de generación (temperature, top_p, max_tokens, stop sequences) y documenta el efecto observado sobre los outputs. Para cada parámetro, genera al menos tres valores distintos y analiza la variabilidad de las respuestas.

**Entregable**: Tabla comparativa de outputs para cada combinación de parámetros, con análisis de los efectos observados. Incluir los comandos curl o el script Python utilizado.

**Criterios de evaluación**: Comprensión demostrada del efecto de cada parámetro, análisis riguroso de las diferencias entre outputs, documentación clara de los comandos utilizados.

---

### Actividad 2 — Configuración de nginx como reverse proxy con TLS

**Descripción**: Configura nginx como reverse proxy para el servidor vLLM del ejercicio anterior. Genera un certificado TLS autofirmado con openssl, configura nginx con terminación TLS, timeouts adecuados y deshabilitación del buffering para streaming. Verifica que la API es accesible mediante HTTPS y que las respuestas en streaming funcionan correctamente a través del proxy.

**Entregable**: Fichero de configuración nginx, comando de generación del certificado, y evidencia de la API funcionando sobre HTTPS (salida de curl con `-k` o de la herramienta de cliente).

**Criterios de evaluación**: Configuración TLS correcta, timeouts adecuados para LLMs, streaming funcionando a través del proxy, documentación del proceso.

---

### Actividad 3 — Implementación de health checks y warm-up en Kubernetes

**Descripción**: Crea un manifiesto Kubernetes para el despliegue del servidor de inferencia que incluya liveness probe, readiness probe y startup probe correctamente configurados para los tiempos de carga de un LLM. Implementa un script de warm-up que se ejecute como post-start lifecycle hook. Simula un fallo del health check modificando el endpoint de salud e indica cómo Kubernetes reacciona ante él.

**Entregable**: Manifiesto YAML del Deployment con todas las probes y el lifecycle hook, script de warm-up y evidencia de la simulación del fallo.

**Criterios de evaluación**: Tiempos de los probes adecuados para LLMs, warm-up funcional y documentado, comportamiento de Kubernetes ante el fallo correctamente observado y descrito.

---

### Actividad 4 — Simulación de estrategias de rollout

**Descripción**: Utilizando un clúster Kubernetes con al menos dos modelos distintos disponibles (pueden ser versiones cuantizadas del mismo modelo base), implementa una actualización mediante la estrategia blue-green. Documenta el procedimiento de despliegue del entorno verde, la verificación de su estado y el cambio de tráfico. Implementa también un canary con el 10% del tráfico dirigido al nuevo modelo y verifica el enrutamiento con múltiples solicitudes. Simula un rollback en ambos casos.

**Entregable**: Manifiestos YAML de ambos entornos, comandos de cambio de tráfico, evidencia del enrutamiento del canary y procedimiento de rollback.

**Criterios de evaluación**: Correcta implementación de ambas estrategias, cambio de tráfico documentado y verificado, rollback funcional en ambos casos, análisis comparativo de las dos estrategias (cuándo usar cada una).

---

## 11. Referencias

- **vLLM — Documentación del servidor de API**: parámetros de configuración, endpoints y opciones de rendimiento. Disponible en: [https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html)

- **Text Generation Inference — Guía de despliegue en producción**: sharding, cuantización y configuración avanzada. Disponible en: [https://huggingface.co/docs/text-generation-inference/basic_tutorials/launcher](https://huggingface.co/docs/text-generation-inference/basic_tutorials/launcher)

- **OpenAI API Reference — Chat Completions**: especificación completa de la API de chat completions. Disponible en: [https://platform.openai.com/docs/api-reference/chat](https://platform.openai.com/docs/api-reference/chat)

- **nginx — Documentación oficial de proxy HTTP**: directivas proxy_pass, timeouts, balanceo de carga. Disponible en: [https://nginx.org/en/docs/http/ngx_http_proxy_module.html](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)

- **Traefik — Documentación de Kubernetes IngressRoute**: configuración de entrypoints, middlewares y TLS. Disponible en: [https://doc.traefik.io/traefik/routing/providers/kubernetes-crd/](https://doc.traefik.io/traefik/routing/providers/kubernetes-crd/)

- **Kubernetes — Liveness, Readiness y Startup Probes**: documentación oficial de configuración de probes. Disponible en: [https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

- **Kubernetes — Estrategias de despliegue**: Rolling Update, Blue-Green y Canary. Disponible en: [https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy)

- **vLLM — PagedAttention: paper original**: Kwon et al., "Efficient Memory Management for Large Language Model Serving with PagedAttention", SOSP 2023. Disponible en: [https://arxiv.org/abs/2309.06180](https://arxiv.org/abs/2309.06180)

- **LiteLLM — Proxy y gateway para LLMs**: documentación del proxy OpenAI-compatible multi-proveedor. Disponible en: [https://docs.litellm.ai/docs/](https://docs.litellm.ai/docs/)

- **HuggingFace TGI — Benchmarking y ajuste de rendimiento**: guía de ajuste de max-batch-prefill-tokens y concurrent requests. Disponible en: [https://huggingface.co/docs/text-generation-inference/conceptual/chunking](https://huggingface.co/docs/text-generation-inference/conceptual/chunking)

- **nginx — Configuración de upstream con least_conn**: balanceo de carga con conexiones mínimas. Disponible en: [https://nginx.org/en/docs/http/ngx_http_upstream_module.html](https://nginx.org/en/docs/http/ngx_http_upstream_module.html)

- **Kubernetes — Container Lifecycle Hooks (postStart)**: documentación de lifecycle hooks para warm-up. Disponible en: [https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)

---

*UD4 · MP04 Infraestructura para la ejecución de LLMs · CFS2 Instalación, despliegue y explotación de sistemas de IA*
