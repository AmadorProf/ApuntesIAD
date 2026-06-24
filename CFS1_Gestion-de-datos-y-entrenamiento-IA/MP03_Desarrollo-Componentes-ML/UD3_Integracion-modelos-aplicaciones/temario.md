# UD3 · Integración de modelos de ML en aplicaciones

---

## 1. Introducción — el modelo como componente de software

Durante años, el desarrollo de modelos de machine learning se trató como una disciplina separada de la ingeniería de software. Los equipos de ciencia de datos construían modelos en notebooks, los exportaban a archivos y los entregaban a los equipos de infraestructura para que "hicieran algo con ellos". El resultado era previsible: fricciones, retrasos, modelos que nunca llegaban a producción, y cuando lo hacían, se comportaban de forma distinta a lo esperado.

La integración de modelos en aplicaciones reales es, en esencia, un problema de ingeniería de software con restricciones adicionales. Un modelo de ML no es un servicio CRUD convencional: su comportamiento es probabilístico, su rendimiento puede degradarse silenciosamente con el tiempo (drift), y sus requisitos computacionales pueden ser órdenes de magnitud superiores a los de una API tradicional. Sin embargo, desde la perspectiva de la aplicación consumidora, un modelo debe comportarse como cualquier otro componente de software: debe tener contratos claros, interfaces estables, comportamiento predecible y garantías de disponibilidad.

### El contrato del modelo

Cuando se expone un modelo como servicio, se establece un contrato implícito o explícito con los consumidores. Este contrato tiene tres dimensiones fundamentales:

**Contrato de datos.** Define el esquema de entrada esperado (tipos, rangos, formatos), el esquema de salida (estructura de la respuesta, tipos de los campos, rango esperado de valores), y las condiciones de error. Un cambio en el esquema de entrada sin notificación previa rompe el contrato y provoca fallos en producción.

**Contrato de comportamiento.** Especifica qué hace el modelo: clasifica, regresa, genera texto, detecta anomalías. Incluye las garantías sobre la distribución de salidas (por ejemplo, que la probabilidad devuelta está calibrada) y los límites del dominio de aplicación (el modelo solo es fiable para entradas dentro de la distribución de entrenamiento).

**Contrato de rendimiento.** Define los SLAs: latencia máxima aceptable en el percentil 95, disponibilidad mínima, throughput sostenible. Este contrato tiene implicaciones directas en el diseño de la infraestructura de integración.

### SLAs y expectativas en producción

Un SLA (Service Level Agreement) es un acuerdo formal sobre el nivel de servicio esperado. En el contexto de modelos de ML, los SLAs más relevantes son:

- **Latencia:** tiempo desde que se envía la petición hasta que se recibe la respuesta. Se mide en percentiles (p50, p95, p99) porque la media oculta los casos extremos.
- **Disponibilidad:** porcentaje del tiempo en que el servicio responde correctamente. Un 99.9% implica hasta 8.7 horas de caída al año; un 99.99% implica 52 minutos.
- **Throughput:** número de peticiones que el servicio puede procesar por unidad de tiempo sin degradar la latencia.

La tensión entre estos tres parámetros es inherente: aumentar el throughput sin añadir recursos aumenta la latencia. Reducir la latencia mediante hardware más potente aumenta el coste. Los arquitectos de sistemas ML deben tomar decisiones explícitas sobre estas compensaciones antes de diseñar la integración.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Seleccionar el patrón de integración adecuado (síncrono, asíncrono, batch, event-driven) en función de los requisitos de latencia, throughput y acoplamiento de un sistema concreto.
2. Diseñar APIs versionadas para modelos de ML que soporten evolución sin romper la compatibilidad con clientes existentes.
3. Implementar un experimento de A/B testing en producción, desde el split de tráfico hasta la interpretación estadística de los resultados.
4. Aplicar caching de predicciones con Redis para reducir latencia y coste computacional, incluyendo políticas de invalidación adecuadas.
5. Diseñar una arquitectura de microservicios para ML que separe responsabilidades entre API gateway, preprocesamiento, inferencia y postprocesamiento.
6. Construir un cliente Python robusto para un modelo-servicio, con retry, circuit breaker y manejo explícito de errores.
7. Definir SLOs medibles para un servicio de ML y configurar alertas que permitan detectar degradaciones antes de que impacten a los usuarios.

---

## 3. Patrones de integración

La integración de un modelo en una aplicación puede seguir distintos patrones arquitectónicos. La elección del patrón no es cosmética: tiene consecuencias directas en la latencia, la resiliencia, la complejidad operativa y la capacidad de escalar.

### 3.1 Integración síncrona: REST y gRPC

La integración síncrona es el patrón más intuitivo: el cliente envía una petición y espera bloqueado hasta recibir la respuesta. Es el modelo de las APIs web convencionales.

**REST** (Representational State Transfer) sobre HTTP/1.1 o HTTP/2 es el estándar de facto para APIs de ML. Su principal ventaja es la ubicuidad: cualquier cliente puede consumir una API REST sin dependencias adicionales. Las desventajas son la verbosidad del formato JSON y la ausencia de tipado estricto en el contrato.

Un endpoint REST típico para inferencia:

```
POST /v1/predict
Content-Type: application/json

{
  "instances": [
    {"feature_1": 0.5, "feature_2": "categoria_A", "feature_3": 120}
  ]
}
```

Respuesta:

```json
{
  "predictions": [{"label": "positivo", "probability": 0.87}],
  "model_version": "2.1.0",
  "latency_ms": 23
}
```

**gRPC** es un framework RPC de alto rendimiento desarrollado por Google que usa Protocol Buffers como formato de serialización binaria. Sus ventajas sobre REST son significativas en escenarios de alta frecuencia: la serialización binaria es más compacta y rápida que JSON, soporta streaming bidireccional, y el contrato se define de forma estricta en archivos `.proto`. La desventaja es la mayor complejidad de setup y la menor universalidad de los clientes.

El patrón síncrono es adecuado cuando:
- El resultado de la inferencia es necesario para continuar el flujo de la aplicación (decisión en tiempo real).
- La latencia del modelo es suficientemente baja (< 500ms en p95).
- El volumen de peticiones es manejable sin saturar el servicio.

El riesgo principal del patrón síncrono es el acoplamiento temporal: si el servicio de ML falla o se ralentiza, el cliente queda bloqueado o recibe un error. Esto requiere timeouts explícitos y estrategias de fallback.

### 3.2 Integración asíncrona: RabbitMQ y Kafka

En la integración asíncrona, el cliente envía la petición a una cola o broker de mensajes y continúa su ejecución sin esperar la respuesta. El modelo consume mensajes de la cola, realiza la inferencia y publica el resultado en otra cola o topic, que el cliente consume cuando lo necesita.

**RabbitMQ** implementa el protocolo AMQP y es adecuado para escenarios donde el orden de procesamiento no es crítico y los mensajes tienen vida corta. Ofrece routing flexible mediante exchanges y bindings.

**Apache Kafka** es un log distribuido diseñado para alto throughput y retención duradera de mensajes. Es la elección habitual cuando:
- El throughput es muy alto (millones de eventos por segundo).
- Se necesita reproducir el stream de eventos (replay).
- Múltiples consumidores deben procesar el mismo stream de forma independiente.
- La retención de los datos de entrada para auditabilidad o reentrenamiento es importante.

El patrón asíncrono desacopla el productor del consumidor en tiempo y espacio: el servicio de ML puede estar momentáneamente caído sin afectar al cliente, porque los mensajes se acumulan en la cola. Esto aumenta la resiliencia del sistema a costa de complejidad operativa.

### 3.3 Event-driven ML

En una arquitectura event-driven, el modelo reacciona a eventos que ocurren en el sistema en lugar de ser llamado explícitamente. Por ejemplo, cuando un usuario completa una compra, se emite un evento `purchase_completed` que desencadena una actualización del perfil de recomendación, que a su vez puede emitir un evento `recommendations_updated` para que la aplicación los muestre en el siguiente acceso.

Este patrón es especialmente adecuado para sistemas de personalización, detección de fraude en streaming y sistemas de alerta en tiempo real.

### 3.4 Batch scoring vs online scoring

**Online scoring** (o real-time inference) procesa cada instancia individualmente, en el momento en que se necesita. Requiere latencias bajas y el modelo debe estar disponible de forma continua.

**Batch scoring** procesa grandes volúmenes de instancias de forma periódica (cada hora, cada día). Las predicciones se almacenan y se sirven desde una base de datos o caché. Es adecuado cuando:
- Las predicciones no necesitan ser absolutamente recientes (recomendaciones nocturnas, scores de riesgo diarios).
- El volumen es muy alto y el coste de inferencia online sería prohibitivo.
- El modelo es computacionalmente costoso (modelos grandes de deep learning).

La elección entre batch y online no es siempre binaria. Un patrón híbrido común es usar batch scoring para la mayoría de usuarios y online scoring para casos de baja latencia donde los datos en tiempo real son críticos.

### 3.5 Tabla comparativa de patrones

| Patrón | Latencia | Throughput | Complejidad | Casos de uso típicos |
|---|---|---|---|---|
| REST síncrono | Baja (ms) | Medio | Baja | APIs de decisión en tiempo real, chatbots, scoring interactivo |
| gRPC síncrono | Muy baja (ms) | Alto | Media | Microservicios internos, streaming de predicciones |
| Asíncrono (RabbitMQ) | Media (s) | Alto | Media | Procesamiento de documentos, pipelines de enriquecimiento |
| Asíncrono (Kafka) | Media-alta (s) | Muy alto | Alta | Detección de fraude en streaming, personalización a escala |
| Event-driven | Variable | Alto | Alta | Sistemas reactivos, actualización de perfiles en tiempo real |
| Batch scoring | Alta (min/h) | Muy alto | Baja-Media | Recomendaciones periódicas, scoring de riesgo masivo |

---

## 4. Gestión de versiones en integración

El versionado es uno de los problemas más infraestimados en la integración de modelos. Un modelo en producción tiene clientes que dependen de él. Cualquier cambio en la interfaz, el comportamiento o el esquema de respuesta puede romper esos clientes.

### 4.1 Versionado semántico de APIs

El versionado semántico (SemVer) usa el formato `MAJOR.MINOR.PATCH`:

- **PATCH** (1.0.0 → 1.0.1): correcciones de errores que no cambian el comportamiento observable.
- **MINOR** (1.0.0 → 1.1.0): nuevas funcionalidades compatibles con versiones anteriores (nuevos campos opcionales en la respuesta, nuevos endpoints).
- **MAJOR** (1.0.0 → 2.0.0): cambios que rompen la compatibilidad (cambio de esquema de entrada, eliminación de campos, cambio semántico del modelo).

En el contexto de modelos de ML, un reentrenamiento del mismo modelo con nuevos datos es típicamente un cambio PATCH o MINOR si el esquema no cambia. El cambio de arquitectura del modelo (de una regresión logística a un gradient boosting) puede ser MINOR si la interfaz es idéntica. El cambio del esquema de entrada o salida siempre es MAJOR.

### 4.2 Backward compatibility

La compatibilidad hacia atrás significa que los clientes que usan la versión anterior de la API pueden seguir funcionando sin modificaciones cuando se despliega una nueva versión. Las reglas prácticas son:

- Nunca eliminar campos de la respuesta sin deprecación previa.
- Nunca cambiar el tipo de un campo existente.
- Los campos nuevos en la respuesta deben ser opcionales desde la perspectiva del cliente.
- Los campos nuevos en la entrada deben tener valores por defecto.

La deprecación es el proceso mediante el cual se notifica a los clientes que un campo o endpoint dejará de estar disponible en una versión futura. Debe incluir un periodo de tiempo suficiente (mínimo 3 meses para APIs internas, 6-12 meses para APIs públicas) y documentación clara sobre la alternativa.

### 4.3 Múltiples versiones en paralelo

Durante el periodo de migración, es habitual mantener múltiples versiones de la API activas simultáneamente. Esto tiene un coste operativo (infraestructura duplicada, mantenimiento de código de múltiples versiones) pero es necesario para no forzar migraciones síncronas de todos los clientes.

Una práctica común es limitar el número de versiones activas a dos (la versión actual y la anterior), estableciendo una política clara de End of Life para versiones antiguas.

### 4.4 Estrategias de versionado de URLs y headers

**URL versioning:** la versión se incluye en el path de la URL.

```
/v1/predict
/v2/predict
```

Es la estrategia más visible y fácil de depurar (el log de acceso muestra qué versión usa cada cliente), pero acopla la versión a la URL, lo que puede complicar el routing.

**Header versioning:** la versión se especifica en un header HTTP.

```
POST /predict
API-Version: 2
```

Es más limpio desde el punto de vista REST (la URL identifica el recurso, no la versión del contrato), pero es menos obvio para los desarrolladores y más difícil de depurar en logs.

Para modelos de ML, el URL versioning es generalmente preferible por su transparencia operativa.

### 4.5 Migración de clientes

Una migración de clientes exitosa requiere:

1. **Documentación de la migración:** guía paso a paso con ejemplos de código comparando v1 y v2.
2. **Periodo de deprecación con aviso activo:** incluir un header `Deprecation: true` y `Sunset: <fecha>` en las respuestas de la versión antigua.
3. **Herramientas de compatibilidad:** en ocasiones, se puede desplegar una capa de traducción que convierte peticiones v1 al formato v2 internamente, reduciendo el esfuerzo de migración del cliente.
4. **Seguimiento de adopción:** monitorizar qué clientes siguen usando versiones antiguas para contactarlos directamente antes del sunset.

---

## 5. A/B testing en producción

El A/B testing es el mecanismo estándar para comparar dos versiones de un modelo (o de cualquier componente) en producción, usando tráfico real y métricas de negocio como criterio de decisión.

### 5.1 Split de tráfico con nginx y Kubernetes

Con **nginx**, el split de tráfico se puede implementar mediante la directiva `split_clients`:

```nginx
split_clients "${remote_addr}${request_uri}" $model_variant {
    50%     model_v1;
    50%     model_v2;
}

upstream model_v1 {
    server model-v1:8080;
}

upstream model_v2 {
    server model-v2:8080;
}
```

Con **Kubernetes**, la solución más robusta es usar un Ingress controller (como nginx-ingress o Istio) con pesos de tráfico. Con Istio, un VirtualService puede distribuir tráfico entre dos versiones de un Deployment:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: model-service
spec:
  http:
    - route:
        - destination:
            host: model-v1
          weight: 50
        - destination:
            host: model-v2
          weight: 50
```

Esta aproximación es más sofisticada que el split por IP porque permite cambiar los pesos sin reiniciar el proxy, facilita el rollback inmediato y se integra con las métricas de Kubernetes.

### 5.2 Métricas de negocio como criterio

Un error frecuente en A/B testing de modelos de ML es usar métricas técnicas del modelo (accuracy, AUC, F1) como criterio de decisión. Estas métricas son útiles durante el desarrollo, pero lo que importa en producción es el impacto en el negocio.

Las métricas de negocio más comunes en función del dominio son:
- **Recomendaciones:** tasa de clics (CTR), conversión, tiempo en plataforma.
- **Detección de fraude:** pérdidas por fraude evitadas, ratio de falsos positivos (fricción para usuarios legítimos).
- **Motores de búsqueda:** posición media de clics, tasa de búsquedas sin resultado.
- **Modelos de precio:** margen por transacción, volumen de ventas.

La elección de la métrica primaria debe hacerse antes de lanzar el experimento, no después de ver los datos.

### 5.3 Duración mínima y potencia estadística

Un A/B test necesita suficiente duración para alcanzar significancia estadística. La duración mínima depende de:

- **Tamaño del efecto esperado:** cuanto menor es el efecto que se quiere detectar, más tráfico se necesita.
- **Varianza de la métrica:** métricas muy variables requieren más muestras.
- **Nivel de significancia (alpha):** típicamente 0.05 (5% de probabilidad de falso positivo).
- **Potencia estadística (1-beta):** típicamente 0.80 (80% de probabilidad de detectar un efecto real).

Herramientas como el calculador de tamaño muestral de Evan Miller o las librerías `scipy.stats` y `statsmodels` en Python permiten calcular el tamaño muestral necesario antes de lanzar el experimento.

Una regla práctica: nunca detener un A/B test antes de completar al menos un ciclo semanal completo, para evitar sesgos por efectos del día de la semana (los usuarios del lunes se comportan diferente a los del sábado).

### 5.4 Feature flags con Unleash y LaunchDarkly

Los feature flags permiten controlar qué porcentaje de usuarios recibe qué versión del modelo de forma dinámica, sin necesidad de redespliegues.

**Unleash** es una plataforma de feature flags open-source. La integración en Python es directa:

```python
from UnleashClient import UnleashClient

client = UnleashClient(
    url="https://unleash.miempresa.com/api",
    app_name="modelo-recomendaciones",
    custom_headers={"Authorization": "Bearer <token>"}
)
client.initialize_client()

def get_model_variant(user_id: str) -> str:
    if client.is_enabled("modelo-v2", {"userId": user_id}):
        return "v2"
    return "v1"
```

**LaunchDarkly** ofrece una funcionalidad similar con un SDK más maduro y soporte para experimentos con análisis estadístico integrado.

### 5.5 Pitfalls del A/B testing en ML

- **Novelty effect:** los usuarios pueden reaccionar positivamente a cualquier cambio simplemente porque es nuevo. Los efectos deben medirse sobre un periodo suficientemente largo.
- **Interferencia entre variantes:** en sistemas de recomendación, la variante A puede afectar al inventario disponible para la variante B, violando el supuesto de independencia.
- **Sesgo de supervivencia:** si los usuarios abandonan el servicio como resultado de una mala experiencia, el grupo de control y el de tratamiento pueden volverse no comparables con el tiempo.
- **Múltiple testing:** si se miden muchas métricas, la probabilidad de encontrar un resultado significativo por azar aumenta. Aplicar la corrección de Bonferroni o usar métricas guardianas.
- **Cambios de comportamiento del modelo en el tiempo:** en modelos online que aprenden de los datos de producción, las dos variantes pueden divergir durante el experimento, complicando la interpretación.

---

## 6. Caching de predicciones

El caching de predicciones es una de las optimizaciones de mayor impacto en sistemas de ML de producción: puede reducir la latencia en órdenes de magnitud y el coste computacional de forma drástica, siempre que se aplique en los contextos adecuados.

### 6.1 Cuándo cachear

El caching es adecuado cuando:
- La misma entrada se repite con frecuencia (baja cardinalidad de entradas).
- El modelo es determinístico (la misma entrada siempre produce la misma salida).
- La frescura de la predicción no es crítica (el valor de la predicción es válido durante un tiempo razonable).

El caching no es adecuado cuando:
- Las entradas tienen alta cardinalidad (cada petición tiene un contexto único).
- El modelo es sensible al tiempo (las predicciones deben reflejar el estado más reciente).
- Los datos de entrada cambian frecuentemente y las predicciones deben actualizarse.

### 6.2 Redis como caché: ejemplo completo en Python

Redis es la solución de caching en memoria más utilizada en producción por su rendimiento, su soporte para tipos de datos ricos y sus opciones de persistencia y clustering.

```python
import redis
import hashlib
import json
from typing import Optional, Any

class PredictionCache:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.default_ttl = 3600  # 1 hora por defecto

    def _make_key(self, model_name: str, model_version: str, input_data: dict) -> str:
        input_str = json.dumps(input_data, sort_keys=True)
        input_hash = hashlib.sha256(input_str.encode()).hexdigest()[:16]
        return f"pred:{model_name}:{model_version}:{input_hash}"

    def get(self, model_name: str, model_version: str, input_data: dict) -> Optional[Any]:
        key = self._make_key(model_name, model_version, input_data)
        cached = self.client.get(key)
        if cached:
            return json.loads(cached)
        return None

    def set(self, model_name: str, model_version: str, input_data: dict,
            prediction: Any, ttl: Optional[int] = None) -> None:
        key = self._make_key(model_name, model_version, input_data)
        ttl = ttl or self.default_ttl
        self.client.setex(key, ttl, json.dumps(prediction))

    def get_or_predict(self, model_name: str, model_version: str,
                       input_data: dict, predict_fn, ttl: Optional[int] = None) -> Any:
        cached = self.get(model_name, model_version, input_data)
        if cached is not None:
            return cached
        prediction = predict_fn(input_data)
        self.set(model_name, model_version, input_data, prediction, ttl)
        return prediction

    def invalidate_model(self, model_name: str, model_version: str) -> int:
        pattern = f"pred:{model_name}:{model_version}:*"
        keys = list(self.client.scan_iter(match=pattern))
        if keys:
            pipeline = self.client.pipeline()
            for key in keys:
                pipeline.delete(key)
            pipeline.execute()
        return len(keys)
```

El uso de `pipeline` para invalidaciones masivas reduce el número de round-trips a Redis, mejorando significativamente el rendimiento cuando hay muchas claves que invalidar.

### 6.3 Políticas de invalidación

- **TTL (Time to Live):** la política más simple. Cada predicción cacheada expira después de un tiempo configurable. Adecuada cuando la frescura requerida es uniforme.
- **Invalidación por evento:** cuando el modelo se redesploya o los datos subyacentes cambian, se invalidan todas las entradas del caché correspondientes. Requiere coordinación entre el pipeline de deployment y el caché.
- **LRU (Least Recently Used):** Redis puede configurarse para expulsar las entradas menos usadas cuando alcanza el límite de memoria. Es el comportamiento por defecto recomendado para cachés de predicciones.

### 6.4 Caching semántico para LLMs

Para modelos de lenguaje grande (LLMs), el caching exacto (misma entrada → misma clave) tiene una tasa de aciertos muy baja porque las consultas en lenguaje natural rara vez se repiten verbatim. El caching semántico resuelve esto buscando predicciones cacheadas para entradas semánticamente similares, no idénticas.

La implementación típica usa embeddings: se genera un embedding de la consulta de entrada y se buscan los vecinos más próximos en un vector store (Faiss, Weaviate, Qdrant). Si existe una consulta suficientemente similar (distancia coseno < umbral), se devuelve la predicción cacheada de esa consulta. Proyectos como GPTCache implementan esta funcionalidad de forma transparente.

---

## 7. Arquitectura de microservicios para ML

Descomponer un sistema de ML en microservicios permite escalar, mantener y desplegar cada componente de forma independiente. La separación de responsabilidades también facilita la sustitución de partes del sistema sin afectar al resto.

### 7.1 Componentes de la arquitectura

**API Gateway:** punto de entrada único para todos los clientes. Gestiona autenticación, autorización, rate limiting, routing hacia los servicios internos y logging de todas las peticiones. No contiene lógica de negocio.

**Servicio de preprocesamiento:** transforma la entrada cruda (datos de usuario, texto, imágenes) al formato que el modelo espera. Esta separación es importante porque el preprocesamiento puede cambiar de forma independiente al modelo.

**Servicio de modelo (inferencia):** recibe la entrada ya preprocesada y devuelve las predicciones crudas. Puede ser un servidor de inferencia especializado (TorchServe, TF Serving, Triton Inference Server) o un servicio custom.

**Servicio de postprocesamiento:** transforma la salida del modelo al formato que el cliente espera, aplica reglas de negocio, filtra resultados inapropiados, o enriquece la respuesta con información adicional.

### 7.2 Ejemplo con Docker Compose multi-servicio

```yaml
version: "3.9"

services:
  api-gateway:
    image: nginx:alpine
    ports:
      - "8080:8080"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - preprocessing
    networks:
      - ml-network

  preprocessing:
    build: ./services/preprocessing
    environment:
      - MODEL_SERVICE_URL=http://model:5001
    networks:
      - ml-network

  model:
    build: ./services/model
    environment:
      - MODEL_PATH=/models/classifier_v2
    volumes:
      - ./models:/models
    networks:
      - ml-network
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]

  postprocessing:
    build: ./services/postprocessing
    networks:
      - ml-network

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
    networks:
      - ml-network

networks:
  ml-network:
    driver: bridge
```

### 7.3 Comunicación y service discovery

En entornos de Kubernetes, el service discovery es nativo: cada servicio tiene un DNS interno (`nombre-servicio.namespace.svc.cluster.local`) que resuelve automáticamente a los pods disponibles.

En entornos más simples (Docker Compose, máquinas virtuales), el service discovery puede implementarse con Consul o simplemente usando variables de entorno con las URLs de los servicios.

La comunicación entre microservicios internos puede ser síncrona (REST, gRPC) o asíncrona (mensajes). Para flujos de inferencia donde cada paso depende del resultado del anterior, la comunicación síncrona es más natural. Para pipelines donde los pasos pueden ejecutarse en paralelo o de forma eventual, la comunicación asíncrona reduce el acoplamiento.

---

## 8. SDK y clientes de modelo

Un cliente bien diseñado para un servicio de ML es tan importante como el propio servicio. Un cliente frágil que no maneja errores correctamente puede amplificar los fallos del servicio o comportarse de forma impredecible ante condiciones de red adversas.

### 8.1 Diseño del cliente Python

Un cliente de modelo debe encapsular toda la complejidad de la comunicación con el servicio: serialización, autenticación, retry, timeout, circuit breaker. El consumidor del cliente solo debe preocuparse por los datos de entrada y la predicción.

### 8.2 Retry con backoff exponencial usando tenacity

La librería `tenacity` es el estándar de facto en Python para implementar políticas de retry declarativas:

```python
import httpx
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log
)
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def _call_model_service(client: httpx.Client, url: str, payload: dict) -> dict:
    response = client.post(url, json=payload, timeout=5.0)
    response.raise_for_status()
    return response.json()
```

El backoff exponencial es importante para evitar el problema de "thundering herd": si todos los clientes reintentan inmediatamente después de un fallo, pueden sobrecargar el servicio justo cuando está intentando recuperarse.

### 8.3 Circuit breaker

El patrón circuit breaker evita que un cliente siga enviando peticiones a un servicio que está fallando sistemáticamente, dando tiempo al servicio para recuperarse:

```python
from circuitbreaker import circuit

class ModelClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.http = httpx.Client(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(connect=2.0, read=5.0, write=2.0, pool=1.0)
        )

    @circuit(failure_threshold=5, recovery_timeout=30, expected_exception=Exception)
    def predict(self, input_data: dict) -> dict:
        try:
            return _call_model_service(self.http, f"{self.base_url}/v1/predict", input_data)
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                raise  # Reintentable: fallo del servidor
            raise ValueError(f"Error de validacion: {e.response.text}")  # No reintentable

    def predict_with_fallback(self, input_data: dict, default_prediction: dict) -> dict:
        try:
            return self.predict(input_data)
        except Exception as e:
            logger.error(f"Fallo en prediccion, usando fallback: {e}")
            return default_prediction
```

Cuando el circuit breaker está abierto (el servicio está fallando), `predict` lanza inmediatamente una excepción sin realizar la llamada HTTP, protegiendo al cliente de tiempos de espera innecesarios.

### 8.4 Timeout y manejo de errores

Los timeouts deben ser explícitos y diferenciados:
- **Timeout de conexión:** tiempo máximo para establecer la conexión TCP.
- **Timeout de lectura:** tiempo máximo para recibir la respuesta una vez establecida la conexión.
- **Timeout total:** tiempo máximo de la operación completa.

El manejo de errores debe distinguir entre errores reintentables (fallos de red transitorios, errores 5xx del servidor) y errores no reintentables (errores 4xx de validación, datos de entrada incorrectos).

---

## 9. SLAs y calidad de servicio

### 9.1 SLOs: latencia y disponibilidad

Un SLO (Service Level Objective) es un objetivo interno medible que el equipo se compromete a mantener. Los SLOs son más granulares y estrictos que los SLAs contractuales y sirven como señal de alerta temprana.

SLOs típicos para un servicio de inferencia:
- **Latencia p50 < 50ms:** la mitad de las peticiones se resuelven en menos de 50ms.
- **Latencia p95 < 200ms:** el 95% de las peticiones se resuelven en menos de 200ms.
- **Latencia p99 < 500ms:** el 99% de las peticiones se resuelven en menos de 500ms.
- **Disponibilidad > 99.9%:** el servicio responde correctamente al menos el 99.9% del tiempo.
- **Tasa de error < 0.1%:** menos del 0.1% de las peticiones resultan en error 5xx.

La elección de los percentiles es deliberada: el p50 captura el caso típico, el p95 captura la experiencia del usuario habitual, y el p99 captura los peores casos que aún son estadísticamente frecuentes. El p100 (máximo absoluto) suele ser un outlier poco informativo.

### 9.2 Alertas

Las alertas deben configurarse sobre los SLOs, no sobre los síntomas técnicos (uso de CPU, memoria). Una alerta sobre "latencia p95 > 200ms durante 5 minutos" es más accionable que una alerta sobre "uso de CPU > 80%".

Con Prometheus y Alertmanager:

```yaml
groups:
  - name: model-service-slos
    rules:
      - alert: HighLatencyP95
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{service="model"}[5m])) > 0.2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Latencia p95 supera 200ms"

      - alert: HighErrorRate
        expr: rate(http_requests_total{service="model", status=~"5.."}[5m]) / rate(http_requests_total{service="model"}[5m]) > 0.001
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Tasa de error supera 0.1%"
```

### 9.3 Degradación graciosa

La degradación graciosa (graceful degradation) es la capacidad del sistema de seguir funcionando de forma reducida cuando algún componente falla, en lugar de fallar completamente.

Patrones comunes de degradación graciosa para servicios de ML:
- **Fallback a predicción por defecto:** si el modelo no está disponible, devolver una predicción estática (la clase más frecuente, el producto más popular, la acción conservadora).
- **Fallback a modelo más simple:** si el modelo principal (costoso) no responde a tiempo, invocar un modelo más simple y rápido como respaldo.
- **Caché como fallback:** si el servicio de inferencia falla, servir predicciones del caché aunque estén potencialmente desactualizadas.
- **Reducción de features:** si alguna fuente de datos para el preprocesamiento no está disponible, hacer la inferencia con el subconjunto de features disponibles.

La degradación graciosa debe diseñarse explícitamente, no improvisarse cuando ocurre un incidente. Requiere que el equipo defina de antemano qué comportamiento es aceptable en condiciones degradadas.

---

## 10. Actividades prácticas

### Actividad 1 — Comparación de patrones de integración

**Objetivo:** comparar empíricamente el rendimiento de integración síncrona vs asíncrona.

**Enunciado:** dado un modelo de clasificación de texto expuesto como API REST, implementar dos pipelines de procesamiento de un dataset de 10.000 documentos: uno síncrono (peticiones secuenciales y con concurrencia HTTP) y otro asíncrono usando Celery con Redis como broker. Medir throughput total y latencia p95 para ambos enfoques y documentar en qué escenarios cada patrón es preferible.

**Entregable:** notebook con código, resultados y análisis comparativo.

### Actividad 2 — Implementación de A/B testing con feature flags

**Objetivo:** diseñar e implementar un experimento A/B para comparar dos versiones de un modelo de recomendación.

**Enunciado:** usando Unleash como servidor de feature flags (disponible como Docker container), implementar el split de tráfico entre dos versiones de un modelo de recomendación simulado. Definir las métricas de negocio (CTR simulado), ejecutar el experimento durante un periodo simulado y aplicar una prueba estadística (t-test o Mann-Whitney) para determinar si existe una diferencia significativa entre variantes. Identificar al menos dos pitfalls potenciales del experimento diseñado.

**Entregable:** código del split de tráfico, script de análisis estadístico, informe de decisión.

### Actividad 3 — Cliente robusto con circuit breaker y caché

**Objetivo:** implementar un cliente de producción para un servicio de ML con todas las capas de resiliencia.

**Enunciado:** dado un servicio de inferencia que simula fallos aleatorios (disponible como Docker container), implementar un cliente Python que incorpore: caché con Redis (TTL configurable), retry con backoff exponencial usando `tenacity`, circuit breaker con `circuitbreaker`, timeout diferenciado (conexión/lectura), y fallback a predicción por defecto. Demostrar el comportamiento del cliente bajo tres escenarios: servicio disponible, servicio con latencia elevada, y servicio completamente caído.

**Entregable:** código del cliente, suite de tests, demostración de los tres escenarios.

### Actividad 4 — Arquitectura de microservicios con Docker Compose

**Objetivo:** desplegar una arquitectura completa de inferencia ML como conjunto de microservicios.

**Enunciado:** diseñar e implementar con Docker Compose una arquitectura que incluya: nginx como API gateway con rate limiting, servicio de preprocesamiento (normalización de texto), servicio de inferencia con un modelo de clasificación (scikit-learn o HuggingFace), servicio de postprocesamiento (formato de respuesta y umbralización), y Redis como caché de predicciones. Implementar health checks para cada servicio y documentar el procedimiento de actualización del modelo sin tiempo de inactividad (rolling update).

**Entregable:** repositorio con Docker Compose, código de cada servicio, documentación de operación.

---

## 11. Referencias

### Libros

- Huyen, C. (2022). *Designing Machine Learning Systems: An Iterative Process for Production-Ready Applications*. O'Reilly Media. https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/

- Hapke, H., y Nelson, C. (2020). *Building Machine Learning Pipelines: Automating Model Life Cycles with TensorFlow*. O'Reilly Media. https://www.oreilly.com/library/view/building-machine-learning/9781492053187/

- Kleppmann, M. (2017). *Designing Data-Intensive Applications*. O'Reilly Media. https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/

### Documentación oficial

- Redis Documentation. *Redis commands, data types, and configuration reference*. https://redis.io/docs/

- Apache Kafka Documentation. *Introduction, architecture, and operations guide*. https://kafka.apache.org/documentation/

- Kubernetes Documentation. *Concepts, tasks, and API reference*. https://kubernetes.io/docs/

- RabbitMQ Documentation. *Getting started, tutorials, and AMQP protocol reference*. https://www.rabbitmq.com/docs

### Artículos y recursos técnicos

- Google SRE Book. *Chapter 4: Service Level Objectives*. https://sre.google/sre-book/service-level-objectives/

- Martin Fowler. *Circuit Breaker pattern*. https://martinfowler.com/bliki/CircuitBreaker.html

- tenacity library documentation. https://tenacity.readthedocs.io/

- Unleash Feature Toggle System. https://docs.getunleash.io/

- LaunchDarkly Documentation. *Feature flags for ML systems*. https://docs.launchdarkly.com/

- Istio Documentation. *Traffic management and A/B testing*. https://istio.io/latest/docs/concepts/traffic-management/

- GPTCache. *Semantic caching for LLM applications*. https://github.com/zilliztech/GPTCache
