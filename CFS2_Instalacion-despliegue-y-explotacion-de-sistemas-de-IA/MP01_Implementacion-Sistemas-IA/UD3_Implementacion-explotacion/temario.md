# UD3 · Implementación de componentes de IA para su explotación

---

## 1. Introducción

Existe una diferencia fundamental entre un sistema de inteligencia artificial que "funciona" en un entorno controlado y uno que está preparado para su explotación en producción. Durante las fases de investigación y desarrollo, el criterio principal es que el modelo produzca resultados correctos: una precisión aceptable, una pérdida que converge, predicciones que tienen sentido sobre los datos de evaluación. Sin embargo, trasladar ese mismo modelo a un entorno productivo expone un conjunto completamente distinto de requisitos que no tienen nada que ver con la calidad estadística del modelo y sí con la ingeniería de sistemas.

Un modelo en producción debe responder en tiempos predecibles bajo carga variable. Debe mantenerse disponible aunque fallen servidores individuales. Debe escalar cuando la demanda aumenta y reducirse cuando disminuye, con el fin de optimizar costes. Debe exponer interfaces claras y bien documentadas que otros sistemas puedan consumir. Debe gestionar errores con elegancia, informar de su estado de salud en todo momento y soportar actualizaciones sin interrumpir el servicio. Y debe hacerlo de forma sostenida, durante semanas y meses, sin degradación.

Esta unidad cubre precisamente ese salto: de un notebook que ejecuta un modelo a un servicio robusto, observable y mantenible. Se estudian los patrones de despliegue según el tipo de inferencia requerida, las arquitecturas de referencia que organizan los componentes de un sistema de IA a escala, la configuración de APIs para producción, las estrategias de balanceo de carga y alta disponibilidad, los mecanismos de escalado automático y, por último, la definición de objetivos y acuerdos de nivel de servicio que permiten gestionar el sistema como un producto de ingeniería maduro.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el alumno será capaz de:

- Distinguir entre los patrones de inferencia batch, online y streaming, y seleccionar el más adecuado según los requisitos del caso de uso.
- Describir las arquitecturas Lambda, Kappa y MLOps de referencia, identificando sus capas y los componentes tecnológicos que las componen.
- Configurar un servicio de inferencia basado en FastAPI con Gunicorn y Uvicorn workers, e integrarlo con nginx como reverse proxy en un entorno de producción.
- Implementar health checks, graceful shutdown y gestión de timeouts en un servicio de inferencia.
- Configurar un balanceador de carga nginx con múltiples instancias de modelo aplicando estrategias de distribución de tráfico.
- Diseñar y aplicar políticas de escalado horizontal automático en Kubernetes mediante HPA y KEDA.
- Definir SLIs, SLOs y SLAs realistas para sistemas de inferencia, calculando el error budget asociado.

---

## 3. Patrones de despliegue de sistemas de IA

El primer paso para implementar un sistema de IA orientado a producción es decidir cómo se va a consumir el modelo: cuándo se ejecuta la inferencia, con qué volumen de datos y con qué requisitos de latencia. Existen tres patrones principales: batch inference, online inference y streaming inference. Cada uno responde a necesidades diferentes y lleva aparejadas decisiones de arquitectura distintas.

### 3.1 Batch inference

El patrón de batch inference consiste en ejecutar el modelo de forma periódica sobre un conjunto de datos acumulado. No hay interacción en tiempo real: los datos se recogen, se procesan en bloque y los resultados se almacenan para que otros sistemas los consulten más tarde.

**Casos de uso típicos:** scoring nocturno de riesgo crediticio, generación de recomendaciones personalizadas que se precargan antes de que el usuario inicie sesión, detección de fraude sobre transacciones del día anterior, segmentación de clientes para campañas de marketing, generación de informes analíticos.

**Implementación básica con cron y Python:**

```python
# score_batch.py
import pandas as pd
import joblib
from datetime import datetime

def run_batch_scoring():
    model = joblib.load("/models/risk_model_v3.pkl")
    df = pd.read_parquet("/data/raw/transactions_today.parquet")

    df["score"] = model.predict_proba(df[FEATURES])[:, 1]
    df["scored_at"] = datetime.utcnow()

    df[["customer_id", "score", "scored_at"]].to_parquet(
        "/data/scores/risk_scores_latest.parquet", index=False
    )

if __name__ == "__main__":
    run_batch_scoring()
```

```cron
# Ejecutar cada noche a las 02:00
0 2 * * * /usr/bin/python3 /opt/ml/score_batch.py >> /var/log/batch_scoring.log 2>&1
```

Para volúmenes grandes (decenas de millones de registros), se utiliza Apache Spark con la biblioteca `spark-ml` o con modelos exportados a formato ONNX o Pandas UDF:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import pandas_udf
import pandas as pd
import joblib

spark = SparkSession.builder.appName("BatchScoring").getOrCreate()

model = joblib.load("/models/risk_model_v3.pkl")

@pandas_udf("double")
def predict_udf(features: pd.Series) -> pd.Series:
    X = pd.DataFrame(features.tolist())
    return pd.Series(model.predict_proba(X)[:, 1])

df = spark.read.parquet("/data/raw/transactions_today.parquet")
df_scored = df.withColumn("score", predict_udf(df["features"]))
df_scored.write.parquet("/data/scores/output/", mode="overwrite")
```

### 3.2 Online inference

El patrón de online inference expone el modelo como un servicio HTTP que responde a peticiones individuales en tiempo real. Es el patrón adecuado cuando el usuario o el sistema cliente necesita una respuesta inmediata: búsquedas con reranking semántico, sistemas de detección de fraude en el momento del pago, asistentes conversacionales, clasificación de imágenes al vuelo.

Los requisitos de latencia son estrictos. Es habitual fijar un objetivo de latencia p99 inferior a 200 ms para servicios de cara al usuario, y de 50 ms en integraciones entre microservicios. Esto implica que el modelo debe estar en memoria, que las transformaciones de las features deben estar precomputadas o ser muy ligeras, y que la infraestructura debe tener suficiente capacidad de cómputo para responder sin colas de espera bajo la carga esperada.

Se aborda en detalle en la sección 5 de esta unidad, donde se cubre la configuración de FastAPI con Gunicorn y nginx.

### 3.3 Streaming inference

El patrón de streaming inference procesa eventos de forma continua a medida que llegan, sin esperar a acumularlos en un lote ni requerir una petición HTTP explícita. El caso de uso canónico es un sistema de detección de anomalías o fraude que consume un flujo de eventos desde Apache Kafka y produce predicciones en tiempo casi real.

**Ejemplo con Kafka y un modelo de ML:**

```python
from kafka import KafkaConsumer, KafkaProducer
import json
import joblib
import numpy as np

model = joblib.load("/models/anomaly_detector_v2.pkl")
scaler = joblib.load("/models/scaler_v2.pkl")

consumer = KafkaConsumer(
    "transactions",
    bootstrap_servers=["kafka:9092"],
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    group_id="ml-inference-group",
    auto_offset_reset="latest",
)

producer = KafkaProducer(
    bootstrap_servers=["kafka:9092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

for message in consumer:
    event = message.value
    features = np.array([event[f] for f in FEATURE_COLS]).reshape(1, -1)
    features_scaled = scaler.transform(features)
    score = model.decision_function(features_scaled)[0]
    is_anomaly = bool(score < THRESHOLD)

    producer.send("anomaly-scores", {
        "transaction_id": event["id"],
        "anomaly_score": float(score),
        "is_anomaly": is_anomaly,
    })
```

Para sistemas de mayor escala, se utiliza Apache Flink o Spark Structured Streaming, que permiten gestionar estado, ventanas temporales y tolerancia a fallos de forma nativa.

### 3.4 Comparativa de patrones

| Característica | Batch | Online | Streaming |
|---|---|---|---|
| Latencia | Alta (minutos a horas) | Baja (ms a segundos) | Muy baja (ms) |
| Throughput | Muy alto | Medio | Alto |
| Complejidad operacional | Baja | Media | Alta |
| Coste de infraestructura | Bajo (puede apagarse) | Medio-alto (siempre activo) | Alto (Kafka + workers) |
| Casos de uso | Scoring nocturno, reportes, segmentación | APIs de predicción, búsqueda, recomendación en sesión | Detección de fraude, alertas, monitorización |
| Herramientas comunes | cron, Airflow, Spark | FastAPI, TorchServe, TF Serving | Kafka, Flink, Spark Streaming |
| Stale predictions | Sí (datos no actualizados) | No | No |

---

## 4. Arquitecturas de referencia para sistemas IA

Una vez elegido el patrón de inferencia, es necesario organizar todos los componentes del sistema. Las arquitecturas de referencia proporcionan una estructura probada que separa responsabilidades y permite que los equipos evolucionen cada capa de forma independiente.

### 4.1 Arquitectura Lambda

La arquitectura Lambda fue propuesta por Nathan Marz para sistemas que necesitan combinar resultados en tiempo real con resultados de alta precisión calculados en batch. Tiene tres capas:

- **Batch layer:** procesa todos los datos históricos periódicamente y genera vistas precalculadas de alta precisión. Herramientas: Hadoop, Spark, Hive.
- **Speed layer:** procesa los datos en tiempo real con baja latencia pero posiblemente menor precisión. Herramientas: Kafka Streams, Flink, Storm.
- **Serving layer:** combina los resultados de ambas capas y responde a las consultas. Herramientas: Cassandra, HBase, Redis.

En un sistema de IA, la batch layer reentrenará el modelo periódicamente con todos los datos disponibles, mientras que la speed layer aplicará un modelo más ligero o actualizable en caliente sobre el flujo de eventos recientes. La serving layer fusiona ambas predicciones.

**Ventaja:** tolerante a errores; si la speed layer falla, la batch layer cubre. **Inconveniente:** mantener dos sistemas paralelos duplica la complejidad operacional y el código de procesamiento.

### 4.2 Arquitectura Kappa

La arquitectura Kappa, propuesta por Jay Kreps (cofundador de Confluent), simplifica Lambda eliminando la batch layer. Todo el procesamiento ocurre en streaming, y los reentrenamientos se modelan como un re-procesamiento del log de eventos históricos.

- **Stream processing layer:** Kafka como log de eventos durable + Flink o Spark Structured Streaming para el procesamiento.
- **Serving layer:** base de datos de baja latencia (Redis, Cassandra) actualizada continuamente por el procesador de streams.

**Ventaja:** un solo sistema de procesamiento, menos código duplicado. **Inconveniente:** el re-procesamiento histórico puede ser costoso; los algoritmos de ML orientados a batch son más difíciles de adaptar.

### 4.3 Arquitectura MLOps de referencia

La arquitectura MLOps de referencia organiza el ciclo de vida completo del modelo en capas horizontales, cada una con responsabilidades claras:

**Data layer:** ingesta, validación y almacenamiento de datos crudos. Componentes: data lake (S3, GCS, ADLS), herramientas de calidad de datos (Great Expectations, Soda), catálogo de datos (DataHub, Amundsen).

**Feature layer:** transformación y almacenamiento de features reutilizables. Componentes: feature store (Feast, Tecton, Vertex AI Feature Store). Esta capa garantiza que las features usadas en entrenamiento son idénticas a las usadas en inferencia, eliminando el training-serving skew.

**Model layer:** entrenamiento, evaluación, versionado y registro de modelos. Componentes: plataforma de experimentación (MLflow, W&B), registro de modelos (MLflow Model Registry, Vertex AI Model Registry), CI/CD de modelos.

**Serving layer:** despliegue y exposición de modelos. Componentes: servidor de inferencia (TorchServe, Triton Inference Server, BentoML, FastAPI), orquestador (Kubernetes), balanceador (nginx, Istio).

**Monitoring layer:** observabilidad del modelo y del sistema. Componentes: métricas de infraestructura (Prometheus + Grafana), detección de data drift (Evidently, WhyLogs), alertas (PagerDuty, Opsgenie).

### 4.4 Ejemplo: arquitectura para un sistema de recomendación

Un sistema de recomendación de e-commerce puede implementarse de la siguiente forma:

- **Data layer:** eventos de clic y compra se envían a Kafka y se persisten en S3 en formato Parquet particionado por fecha.
- **Feature layer:** Feast calcula y sirve features de usuario (historial de compras, categorías preferidas) y de ítem (popularidad reciente, margen de beneficio). Las features online se almacenan en Redis con TTL de 1 hora.
- **Model layer:** un modelo de two-tower (BERT4Rec o similar) se reentrena semanalmente con Spark sobre los datos históricos. Los embeddings de ítems se generan en batch y se indexan en un motor de búsqueda vectorial (Faiss, Milvus, Weaviate).
- **Serving layer:** la API de recomendación (FastAPI) recibe el `user_id`, consulta las features del usuario en Redis, ejecuta la búsqueda aproximada de vecinos más cercanos (ANN) en Milvus y devuelve los top-K ítems en < 50 ms.
- **Monitoring layer:** Prometheus recoge métricas de latencia, throughput y tasa de error de la API. Evidently ejecuta diariamente un informe de data drift comparando la distribución de features actuales con la del último entrenamiento.

---

## 5. Configuración de APIs de inferencia para producción

FastAPI es el framework Python más utilizado para construir APIs de inferencia por su alto rendimiento (basado en Starlette y asyncio), su validación automática de datos mediante Pydantic y su generación de documentación OpenAPI integrada.

### 5.1 FastAPI con Gunicorn y Uvicorn workers

En producción, FastAPI no se ejecuta directamente con `uvicorn` en modo de desarrollo. Se utiliza Gunicorn como gestor de procesos, con workers de tipo `UvicornWorker` que permiten aprovechar múltiples núcleos de CPU:

```python
# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import logging

logger = logging.getLogger(__name__)
app = FastAPI(title="Inference API", version="1.0.0")

# El modelo se carga una sola vez al iniciar el proceso
model = None
scaler = None

@app.on_event("startup")
async def load_model():
    global model, scaler
    model = joblib.load("/models/classifier_v3.pkl")
    scaler = joblib.load("/models/scaler_v3.pkl")
    logger.info("Model loaded successfully")

class PredictRequest(BaseModel):
    features: list[float]

class PredictResponse(BaseModel):
    prediction: int
    probability: float

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not ready")
    X = np.array(request.features).reshape(1, -1)
    X_scaled = scaler.transform(X)
    pred = int(model.predict(X_scaled)[0])
    prob = float(model.predict_proba(X_scaled)[0][pred])
    return PredictResponse(prediction=pred, probability=prob)
```

```bash
# Comando de arranque con Gunicorn
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 30 \
    --keep-alive 5 \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log
```

El número de workers recomendado es `2 * CPU_cores + 1`. En un servidor con 4 núcleos, se usarían 9 workers.

### 5.2 nginx como reverse proxy

nginx actúa como capa intermedia entre los clientes y los workers de Gunicorn, proporcionando terminación SSL, rate limiting, compresión y bufering de peticiones:

```nginx
upstream inference_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;

server {
    listen 443 ssl http2;
    server_name api.ml.example.com;

    ssl_certificate /etc/ssl/certs/api.crt;
    ssl_certificate_key /etc/ssl/private/api.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    location /predict {
        limit_req zone=api_limit burst=200 nodelay;

        proxy_pass http://inference_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 5s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

### 5.3 Health checks

Los health checks son endpoints que permiten al orquestador (Kubernetes, ECS) determinar si una instancia está lista para recibir tráfico y si sigue funcionando correctamente:

```python
@app.get("/health")
async def health():
    """Liveness probe: el proceso está vivo."""
    return {"status": "ok"}

@app.get("/ready")
async def ready():
    """Readiness probe: el modelo está cargado y listo."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready", "model_version": MODEL_VERSION}
```

En Kubernetes, estos endpoints se configuran como `livenessProbe` y `readinessProbe`. Si `/health` falla, el pod se reinicia. Si `/ready` falla, el pod se retira del balanceo de carga pero no se reinicia.

### 5.4 Graceful shutdown

En un graceful shutdown, el proceso termina de atender las peticiones en vuelo antes de cerrarse. Gunicorn implementa esto con la señal SIGTERM: deja de aceptar nuevas conexiones y espera a que las existentes finalicen antes de matar los workers.

```python
import signal
import asyncio

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down: finishing in-flight requests...")
    # Dar tiempo a que las peticiones en vuelo terminen
    await asyncio.sleep(2)
    logger.info("Shutdown complete")
```

### 5.5 Timeouts y keep-alive

Los timeouts evitan que peticiones lentas bloqueen workers indefinidamente. La configuración debe ser coherente entre nginx y Gunicorn:

- `proxy_read_timeout` en nginx: tiempo máximo que nginx espera respuesta del backend (30s para modelos complejos, 5s para modelos ligeros).
- `--timeout` en Gunicorn: tiempo máximo antes de matar un worker que no responde.
- `keepalive` en nginx upstream: número de conexiones persistentes que nginx mantiene abiertas con los workers, evitando el coste de reestablecerlas en cada petición.

---

## 6. Load balancing y alta disponibilidad

Para que el sistema sea tolerante a fallos, no puede depender de una sola instancia del servicio de inferencia. Se necesita al menos dos instancias activas en todo momento, un balanceador de carga que distribuya el tráfico entre ellas y un mecanismo que retire del pool las instancias que fallen.

### 6.1 nginx upstream con múltiples instancias

```nginx
upstream inference_pool {
    least_conn;  # estrategia de balanceo

    server inference-1:8000 weight=1 max_fails=3 fail_timeout=30s;
    server inference-2:8000 weight=1 max_fails=3 fail_timeout=30s;
    server inference-3:8000 weight=1 max_fails=3 fail_timeout=30s;

    keepalive 64;
}
```

### 6.2 Estrategias de balanceo

- **Round-robin (por defecto):** distribuye las peticiones en orden circular entre los servidores disponibles. Apropiado cuando todas las instancias tienen la misma capacidad y las peticiones son homogéneas en coste computacional.
- **Least connections (`least_conn`):** envía cada nueva petición al servidor con menos conexiones activas. Recomendado cuando las peticiones tienen duración variable (por ejemplo, modelos de lenguaje con generación de longitud variable).
- **IP hash (`ip_hash`):** asigna cada IP de cliente siempre al mismo servidor. Proporciona session affinity sin necesidad de almacenamiento compartido.

### 6.3 Session affinity para modelos con estado

Algunos modelos mantienen estado entre peticiones (historial de conversación, cache de KV en LLMs). En estos casos, es necesario que todas las peticiones de un mismo cliente lleguen siempre a la misma instancia. nginx soporta `ip_hash` y `hash $cookie_session_id consistent` para este propósito.

### 6.4 HAProxy como alternativa

HAProxy es más flexible que nginx para configuraciones avanzadas de balanceo. Sus ventajas incluyen health checks activos configurables por endpoint, soporte nativo de circuit breaker, y estadísticas detalladas en tiempo real. Para sistemas de inferencia con requisitos de disponibilidad muy altos (99.9% o superior), HAProxy es frecuentemente preferido.

### 6.5 Circuit breaker en el balanceador

El patrón circuit breaker evita que un servicio degradado siga recibiendo tráfico que no puede gestionar. En nginx, se implementa con los parámetros `max_fails` y `fail_timeout`: si un servidor falla más de `max_fails` veces en `fail_timeout` segundos, se retira del pool temporalmente. Transcurrido ese tiempo, nginx vuelve a enviarle una petición de prueba antes de reincorporarlo.

Para circuit breakers más sofisticados (con estados half-open, telemetría detallada), se utiliza un service mesh como Istio o Linkerd, que implementa el patrón a nivel de proxy sidecar sin modificar el código de la aplicación.

---

## 7. Escalado de sistemas de inferencia

El escalado permite ajustar la capacidad del sistema a la demanda real, evitando tanto el sub-provisionamiento (que provoca latencias altas o peticiones rechazadas) como el sobre-provisionamiento (que implica coste innecesario).

### 7.1 Escalado horizontal vs vertical

El **escalado vertical** consiste en aumentar los recursos (CPU, RAM, GPU) de una instancia existente. Es simple de implementar pero tiene límites físicos y crea un punto único de fallo.

El **escalado horizontal** consiste en añadir más instancias del servicio. Es la estrategia preferida para sistemas de inferencia en producción porque no tiene límite práctico, permite actualizaciones sin downtime (rolling updates) y es más resiliente ante fallos de instancias individuales.

### 7.2 Kubernetes HPA (Horizontal Pod Autoscaler)

El HPA de Kubernetes ajusta automáticamente el número de pods de un Deployment en función de métricas observadas:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: inference-hpa
  namespace: ml-serving
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: inference-service
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
      - type: Pods
        value: 4
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 25
        periodSeconds: 60
```

La ventana de estabilización (`stabilizationWindowSeconds`) evita el flapping: el HPA no escala hacia abajo hasta que la métrica se mantiene por debajo del umbral durante el tiempo especificado. Para scaleDown, se recomienda una ventana larga (5 minutos) para evitar ciclos de escalado que degradan el rendimiento.

### 7.3 Métricas personalizadas para HPA

El HPA basado solo en CPU es insuficiente para sistemas de inferencia, donde el cuello de botella puede ser la GPU, la longitud de la cola de peticiones o la latencia. Se utilizan métricas personalizadas exportadas desde Prometheus mediante el `prometheus-adapter`:

```yaml
# Métrica: latencia p99 de la API de inferencia
- type: Object
  object:
    metric:
      name: http_request_duration_p99
    describedObject:
      apiVersion: v1
      kind: Service
      name: inference-service
    target:
      type: Value
      value: "200m"  # 200 ms
```

### 7.4 KEDA para escalado basado en colas

KEDA (Kubernetes Event-Driven Autoscaling) permite escalar pods basándose en el número de mensajes pendientes en una cola, lo que lo hace ideal para sistemas de inferencia en modo batch o streaming:

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: inference-scaler
spec:
  scaleTargetRef:
    name: inference-worker
  minReplicaCount: 0
  maxReplicaCount: 50
  triggers:
  - type: kafka
    metadata:
      bootstrapServers: kafka.default.svc.cluster.local:9092
      consumerGroup: ml-inference-group
      topic: inference-requests
      lagThreshold: "10"
      offsetResetPolicy: latest
```

Con `minReplicaCount: 0`, KEDA escala a cero cuando no hay mensajes pendientes, eliminando completamente el coste de infraestructura en periodos de inactividad. Cuando llegan mensajes, KEDA levanta pods en segundos.

### 7.5 Límites y requests de recursos en Kubernetes

Para que el HPA y el scheduler de Kubernetes funcionen correctamente, cada pod debe declarar sus `requests` (garantizados) y `limits` (máximos):

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "1Gi"
  limits:
    cpu: "2000m"
    memory: "4Gi"
```

Para pods con GPU:

```yaml
resources:
  requests:
    nvidia.com/gpu: 1
  limits:
    nvidia.com/gpu: 1
```

Los `requests` determinan en qué nodo se programa el pod. Los `limits` evitan que un pod consuma recursos de otros. Un pod de inferencia sin `limits` puede monopolizar un nodo y degradar todos los demás servicios.

---

## 8. SLOs y SLAs para sistemas de IA

La definición formal de objetivos de nivel de servicio (SLOs) es lo que transforma un servicio de IA en un producto de ingeniería gestionable. Sin ellos, no existe criterio objetivo para determinar si el sistema está funcionando correctamente, cuándo actuar ante una degradación y qué compromisos se pueden adquirir con los clientes.

### 8.1 SLIs (Service Level Indicators)

Los SLIs son las métricas que se miden. Para sistemas de inferencia, los SLIs más relevantes son:

**Latencia:** tiempo desde que el servicio recibe la petición hasta que envía la respuesta. Se mide en percentiles, no en media, porque la media oculta los casos lentos que más afectan a la experiencia:
- p50 (mediana): latencia típica.
- p95: latencia experimentada por el 95% de las peticiones.
- p99: latencia experimentada por el 99% de las peticiones. Es el indicador más relevante para detectar colas y problemas de cold start.

**Disponibilidad:** fracción del tiempo en que el servicio es capaz de responder peticiones correctamente. Se calcula como `peticiones_exitosas / peticiones_totales` en ventanas temporales.

**Tasa de error:** porcentaje de peticiones que resultan en un error (HTTP 5xx para APIs REST, excepciones no capturadas, timeouts).

**Throughput:** número de peticiones procesadas por segundo. Es relevante tanto como indicador de carga como de capacidad máxima.

**Ejemplo de instrumentación con Prometheus en FastAPI:**

```python
from prometheus_client import Counter, Histogram, make_asgi_app
import time

REQUEST_COUNT = Counter(
    "inference_requests_total",
    "Total inference requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "inference_request_duration_seconds",
    "Inference request latency",
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    REQUEST_LATENCY.observe(duration)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    return response
```

### 8.2 SLOs realistas para sistemas de inferencia

Los SLOs deben ser lo suficientemente exigentes para garantizar una experiencia aceptable, pero alcanzables con la tecnología y el presupuesto disponibles. Valores de referencia para servicios de inferencia en producción:

| SLI | SLO típico |
|---|---|
| Disponibilidad | >= 99.5% mensual |
| Latencia p50 | <= 50 ms |
| Latencia p95 | <= 150 ms |
| Latencia p99 | <= 500 ms |
| Tasa de error | <= 0.1% |
| Throughput mínimo garantizado | >= 100 RPS |

Para modelos de lenguaje grande (LLMs) en inferencia, la latencia es significativamente mayor y los SLOs se adaptan:
- Time to first token (TTFT): <= 500 ms
- Tokens por segundo (TPS): >= 20 tokens/s

### 8.3 SLAs contractuales

Un SLA (Service Level Agreement) es un acuerdo formal, frecuentemente con consecuencias económicas (créditos de servicio, penalizaciones), entre el proveedor del servicio y sus clientes. El SLA es siempre más conservador que el SLO interno:

- SLO interno de disponibilidad: 99.9%
- SLA con clientes: 99.5%

Esta diferencia actúa como margen de seguridad. Si el sistema cumple su SLO interno con holgura, el SLA externo rara vez está en riesgo.

### 8.4 Error budget

El error budget es la cantidad de tiempo o de peticiones que pueden fallar dentro de un periodo dado antes de incumplir el SLO. Proporciona un lenguaje común entre los equipos de desarrollo (que quieren mover rápido) y los de operaciones (que priorizan la estabilidad):

```
Error budget mensual (disponibilidad 99.9%) =
    (1 - 0.999) * 43800 minutos = 43.8 minutos al mes
```

Si el error budget se agota, el equipo de desarrollo detiene los despliegues y dedica el tiempo restante del ciclo a mejorar la fiabilidad. Si el error budget está intacto, el equipo puede asumir más riesgo en los despliegues.

### 8.5 OLAs (Operational Level Agreements)

Los OLAs son acuerdos de nivel de servicio internos entre equipos. En un sistema de IA, el equipo de infraestructura puede acordar con el equipo de ML que la plataforma de serving estará disponible el 99.9% del tiempo, mientras que el equipo de ML se compromete a que los modelos desplegados tendrán una latencia p99 inferior a 200 ms. Estos acuerdos permiten distribuir la responsabilidad de forma clara y auditable.

---

## 9. Actividades prácticas

### Actividad 1: Despliegue de un servicio de inferencia con FastAPI y nginx

**Objetivo:** poner en producción un clasificador de sklearn como API REST con FastAPI, Gunicorn y nginx, incluyendo health checks y rate limiting.

**Descripción:** a partir de un modelo de clasificación binaria previamente entrenado y serializado con joblib, el alumno debe:

1. Construir una API con FastAPI que exponga los endpoints `/predict`, `/health` y `/ready`.
2. Escribir el `Dockerfile` correspondiente con una imagen base Python 3.11-slim, instalando las dependencias necesarias.
3. Configurar Gunicorn con UvicornWorkers para ejecutar la API con múltiples workers.
4. Configurar nginx como reverse proxy con SSL termination (usando certificado autofirmado) y rate limiting de 50 peticiones/segundo por IP.
5. Probar el servicio con `curl` y `wrk` (herramienta de benchmarking HTTP) y documentar la latencia p50 y p99 obtenida.

**Entregable:** repositorio Git con el código de la API, el Dockerfile, la configuración de nginx y un informe de resultados del benchmark de 2 páginas.

---

### Actividad 2: Configuración de balanceo de carga con múltiples instancias

**Objetivo:** configurar nginx para balancear tráfico entre tres instancias del servicio de inferencia con estrategia `least_conn`, validar el comportamiento ante el fallo de una instancia y medir el impacto en la latencia.

**Descripción:**

1. Levantar tres contenedores con la API de la Actividad 1 en los puertos 8001, 8002 y 8003.
2. Configurar un bloque `upstream` en nginx con `least_conn` y los parámetros `max_fails=3 fail_timeout=15s`.
3. Usar `wrk` para generar 200 RPS durante 2 minutos mientras el balanceador está en funcionamiento normal.
4. A mitad del test, apagar manualmente una de las tres instancias y observar cómo nginx gestiona el failover.
5. Registrar las métricas de latencia p50/p99 antes y después del fallo.

**Entregable:** configuración de nginx comentada + capturas de las métricas de `wrk` antes y después del fallo + análisis escrito de 1 página.

---

### Actividad 3: Escalado automático con Kubernetes HPA

**Objetivo:** desplegar el servicio de inferencia en un cluster Kubernetes local (minikube o kind) y configurar un HPA que escale entre 2 y 10 réplicas basándose en el uso de CPU.

**Descripción:**

1. Escribir los manifiestos Kubernetes: `Deployment`, `Service` (ClusterIP) e `Ingress`.
2. Definir `resources.requests.cpu: 250m` y `resources.limits.cpu: 1000m` en el Deployment.
3. Crear un HPA con `targetCPUUtilizationPercentage: 60`, `minReplicas: 2`, `maxReplicas: 10`.
4. Generar carga artificial con `kubectl run load-generator` usando `hey` o `k6` para superar el umbral de CPU.
5. Observar en tiempo real el comportamiento del HPA con `kubectl get hpa -w`.
6. Reducir la carga y verificar que el scaledown ocurre tras la ventana de estabilización.

**Entregable:** manifiestos YAML + log de `kubectl get hpa` durante el experimento + análisis del comportamiento de escalado.

---

### Actividad 4: Definición de SLOs y cálculo de error budget

**Objetivo:** definir un conjunto de SLOs para el servicio de inferencia desarrollado en las actividades anteriores y calcular el error budget mensual y semanal.

**Descripción:**

1. Instrumentar la API con `prometheus-client` para exponer métricas de latencia (histograma), disponibilidad y tasa de error.
2. Definir tres SLOs: disponibilidad >= 99.5%, latencia p99 <= 300 ms, tasa de error <= 0.5%.
3. Calcular el error budget mensual para cada SLO (en minutos de downtime, en peticiones fallidas y en ms de latencia acumulada).
4. Simular un incidente (reiniciar el servicio sin graceful shutdown) y medir cuánto error budget se ha consumido.
5. Redactar un documento de SLO de 2 páginas con la definición de los SLIs, los SLOs, el método de medición, el periodo de evaluación y la política de error budget.

**Entregable:** código de instrumentación Prometheus + documento de SLO + análisis del incidente simulado.

---

## 10. Referencias

**Libros:**

- Huyen, C. (2022). *Designing Machine Learning Systems: An Iterative Process for Production-Ready Applications*. O'Reilly Media. Disponible en: https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/

- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (Eds.). (2016). *Site Reliability Engineering: How Google Runs Production Systems*. O'Reilly Media. Acceso gratuito en línea: https://sre.google/sre-book/table-of-contents/

**Documentación oficial:**

- FastAPI. *FastAPI Documentation*. https://fastapi.tiangolo.com/

- FastAPI. *Deployment — Using Gunicorn with Uvicorn*. https://fastapi.tiangolo.com/deployment/server-workers/

- nginx. *ngx_http_upstream_module*. https://nginx.org/en/docs/http/ngx_http_upstream_module.html

- nginx. *Limiting the Number of Connections*. https://nginx.org/en/docs/http/ngx_http_limit_conn_module.html

- Kubernetes. *Horizontal Pod Autoscaling*. https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/

- Kubernetes. *Configure Liveness, Readiness and Startup Probes*. https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/

- KEDA. *KEDA Documentation — Kafka Scaler*. https://keda.sh/docs/2.14/scalers/apache-kafka/

- KEDA. *Scaling Deployments, StatefulSets & Custom Resources*. https://keda.sh/docs/2.14/concepts/scaling-deployments/

**Artículos y recursos complementarios:**

- Google. *SRE Workbook: Service Level Objectives*. https://sre.google/workbook/slos-risks-and-error-budgets/

- Prometheus. *Instrumentation — Python Client*. https://prometheus.github.io/client_python/

- Feast. *Feature Store Documentation*. https://docs.feast.dev/

- Evidently AI. *ML Monitoring Documentation*. https://docs.evidentlyai.com/
