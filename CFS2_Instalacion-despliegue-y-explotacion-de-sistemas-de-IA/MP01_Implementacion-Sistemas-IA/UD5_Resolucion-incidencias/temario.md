# UD5 · Resolución de incidencias en plataformas de IA

---

## 1. Introducción

Los sistemas de inteligencia artificial en producción comparten muchas de las características de cualquier sistema de software distribuido: pueden sufrir caídas, degradaciones de rendimiento, errores de integración o fallos de infraestructura. Sin embargo, presentan una clase adicional de problemas que son completamente ajenos al software clásico y que exigen metodologías y herramientas específicas para su diagnóstico y resolución.

Un servicio web tradicional falla de forma binaria: o responde o no responde. Un modelo de aprendizaje automático puede seguir respondiendo con aparente normalidad mientras produce resultados cada vez más incorrectos, sesgados o directamente inventados. Esta característica —la degradación silenciosa— convierte la resolución de incidencias en sistemas de IA en una disciplina que combina ingeniería de fiabilidad del sitio (SRE), ciencia de datos y conocimiento profundo del ciclo de vida del modelo.

El ingeniero de sistemas de IA que trabaja en soporte y operaciones debe distinguir entre tres grandes dominios de fallo:

- **Fallos de modelo:** el comportamiento estadístico del modelo se degrada por razones relacionadas con los datos de entrada, el concepto subyacente o la arquitectura.
- **Fallos de datos:** el pipeline de datos que alimenta al modelo introduce errores, ausencias o distribuciones inesperadas.
- **Fallos de infraestructura e integración:** la plataforma que sirve el modelo —GPUs, contenedores, APIs, colas de mensajes— falla o se comporta de forma anómala.

Esta unidad aborda los tres dominios con una perspectiva práctica: metodologías de diagnóstico, herramientas concretas y procedimientos documentados (runbooks) que permiten resolver incidencias de forma sistemática, reproducible y, lo más importante, aprendiendo de cada evento para mejorar la fiabilidad del sistema a largo plazo.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Identificar y clasificar los tipos de incidencias específicos de los sistemas de IA, distinguiéndolos de las incidencias comunes del software convencional.
2. Aplicar una metodología sistemática de diagnóstico basada en el ciclo de reproducción, acotación, hipótesis, verificación, corrección y documentación.
3. Configurar y utilizar los tres pilares de la observabilidad —logs, métricas y trazas— en un servicio de inferencia real.
4. Emplear herramientas especializadas como `nvidia-smi`, `torch.profiler`, Evidently AI y OpenTelemetry para diagnosticar problemas de rendimiento y calidad del modelo.
5. Redactar runbooks de incidencias tipo que permitan a cualquier miembro del equipo resolver un problema recurrente sin necesidad de escalar.
6. Elaborar post-mortems blameless que conviertan los fallos en oportunidades de mejora del sistema.
7. Calcular e interpretar métricas operativas como el MTTR y el MTTF en el contexto específico de los sistemas de aprendizaje automático.

---

## 3. Tipología de incidencias en sistemas de IA

### 3.1 Incidencias de modelo

#### Model drift

El model drift es la pérdida gradual de validez predictiva de un modelo entrenado, causada por cambios en el mundo real que no están reflejados en los datos de entrenamiento. Se divide en dos categorías conceptualmente distintas:

**Data drift (o covariate drift):** cambia la distribución de las variables de entrada X, pero la relación entre X e Y permanece estable. Por ejemplo, un modelo de recomendación entrenado con usuarios de entre 25 y 40 años empieza a recibir tráfico mayoritario de usuarios de 60 o más años. El modelo no ha "aprendido" ese perfil y sus predicciones serán menos precisas, aunque la lógica de negocio subyacente sea la misma.

**Concept drift:** cambia la relación entre X e Y. El significado de los datos ha cambiado. Un modelo de detección de fraude entrenado antes de la pandemia puede clasificar como legítimas transacciones que ahora son fraudulentas, porque los patrones de comportamiento de los defraudadores han evolucionado. El concept drift es más difícil de detectar porque no se observa directamente en los datos de entrada: solo se manifiesta cuando se dispone de etiquetas reales para comparar con las predicciones.

#### Degradación del rendimiento

Incluso sin drift, el rendimiento de un modelo puede degradarse por razones técnicas: una versión del framework de inferencia que introduce regresiones, un cambio en el preprocesamiento que altera sutilmente los datos, o una actualización del vocabulario de un tokenizador que introduce tokens desconocidos. La degradación de rendimiento requiere comparar métricas de modelo (accuracy, F1, RMSE, BLEU, etc.) en ventanas temporales sucesivas.

#### Alucinaciones en producción

En modelos de lenguaje grande (LLMs), la alucinación —la generación de información factualmente incorrecta pero plausible— es una incidencia de primera clase. En producción, las alucinaciones pueden ser sistemáticas (el modelo siempre inventa la misma información incorrecta ante un tipo de prompt) o estocásticas (aparecen de forma impredecible). Su diagnóstico requiere pipelines de evaluación automatizada con jueces de IA o validación contra fuentes de verdad.

#### Sesgos emergentes

Un modelo puede haber pasado la evaluación de sesgos durante el entrenamiento y, sin embargo, mostrar comportamientos discriminatorios en producción porque el subconjunto de la población que realmente usa el sistema difiere del dataset de evaluación. Los sesgos emergentes son especialmente críticos en sistemas que toman decisiones de alto impacto (crédito, contratación, diagnóstico médico).

### 3.2 Incidencias de datos

**Cambios en la distribución de entrada:** similares al data drift pero de aparición brusca, no gradual. Pueden deberse a un cambio en el cliente que consume la API, a una migración de base de datos o a un error en el pipeline de ETL upstream.

**Datos faltantes:** campos obligatorios para la inferencia que llegan vacíos o nulos. En algunos modelos, los valores faltantes se imputan automáticamente con valores de entrenamiento, lo que produce predicciones silenciosamente degradadas en lugar de errores explícitos.

**Errores de calidad en tiempo real:** valores fuera de rango, tipos incorrectos, codificaciones inconsistentes (UTF-8 vs Latin-1), fechas malformadas. Estos errores pueden propagarse sin levantar excepciones si el preprocesamiento no incluye validación estricta.

### 3.3 Incidencias de infraestructura

**OOM en GPU (CUDA Out of Memory):** uno de los errores más frecuentes en entornos de inferencia GPU. Se produce cuando el batch size o la longitud de la secuencia supera la memoria disponible en la GPU. El error `torch.cuda.OutOfMemoryError: CUDA out of memory` detiene completamente el proceso de inferencia.

**Timeout de inferencia:** el cliente espera una respuesta en un tiempo máximo configurado y el modelo no la produce. Puede deberse a un modelo demasiado grande para el hardware disponible, a contención de recursos o a un input anormalmente largo que dispara un tiempo de inferencia no contemplado en el dimensionamiento.

**Cuello de botella en I/O:** en pipelines que cargan modelos desde disco o que realizan llamadas frecuentes a bases de datos vectoriales, el I/O puede convertirse en el factor limitante. La GPU queda ociosa esperando datos, lo que reduce drásticamente el throughput.

### 3.4 Incidencias de integración

**Incompatibilidades de API:** cambios en la versión de la API del modelo (por ejemplo, la firma de los campos de entrada/salida) que no se comunican correctamente al cliente consumidor. El contrato entre productor y consumidor se rompe.

**Errores de serialización/deserialización:** tensores, embeddings o arrays numpy que no se serializan correctamente a JSON, Protobuf o MessagePack. Un tensor de tipo `float16` serializado como `float32` puede introducir diferencias numéricas; un array con dimensiones incorrectas puede causar errores de forma en la primera capa del modelo.

### 3.5 Tabla de diagnóstico rápido

| Síntoma observado | Causa probable | Herramienta de diagnóstico |
|---|---|---|
| Accuracy decrece gradualmente durante semanas | Data drift o concept drift | Evidently AI, WhyLabs |
| El modelo devuelve respuestas incorrectas de forma repentina | Cambio en preprocesamiento o nueva versión del modelo | Comparación A/B de versiones, logs de despliegue |
| `CUDA out of memory` en logs | Batch size excesivo o fuga de memoria en GPU | `nvidia-smi`, `torch.profiler` |
| Latencia de inferencia aumenta p99 | Cuello de botella en CPU, I/O o contención de GPU | `py-spy`, `torch.profiler`, métricas Prometheus |
| Campos nulos en las predicciones | Datos de entrada con valores faltantes no gestionados | Validación de schema en el pipeline de entrada |
| Errores 422 o 500 en la API de inferencia | Incompatibilidad de versión o error de serialización | Logs de la API, comparación de schemas |
| Alucinaciones frecuentes en LLM | Temperatura excesiva, prompt engineering deficiente o knowledge cutoff | Evaluación automatizada con LLM-as-judge |
| Predicciones sesgadas en un subgrupo | Sesgo emergente por distribución asimétrica del tráfico | Métricas de equidad por segmento, Arize AI |

---

## 4. Metodología de diagnóstico

### 4.1 Proceso sistemático de siete pasos

La resolución de incidencias no puede depender de la intuición individual. Un proceso sistemático garantiza que no se saltan pasos críticos y que el razonamiento es reproducible.

**Paso 1 — Reproducir la incidencia.** Una incidencia que no se puede reproducir no se puede resolver con garantías. El objetivo es crear un caso mínimo reproducible: el input más pequeño posible que desencadena el problema. En sistemas de IA, esto puede requerir capturar el payload exacto de una petición real (respetando la privacidad de los datos) o construir un input sintético que reproduzca las características del problema.

**Paso 2 — Acotar el ámbito.** Determinar si el problema afecta a todo el sistema o solo a un subconjunto: ¿falla solo con ciertos tipos de input? ¿Solo en un entorno (producción pero no staging)? ¿Solo en una instancia concreta? La acotación reduce drásticamente el espacio de búsqueda.

**Paso 3 — Formular hipótesis.** A partir de los síntomas y el ámbito identificado, formular entre una y tres hipótesis ordenadas por probabilidad. Documentarlas explícitamente evita el sesgo de confirmación: al tener varias hipótesis escritas, se es menos propenso a forzar los datos para que confirmen la primera que se nos ocurrió.

**Paso 4 — Verificar con datos.** Cada hipótesis debe poder verificarse o refutarse con datos objetivos: logs, métricas, resultados de herramientas de profiling. No se descarta una hipótesis por intuición; se descarta porque los datos no la sostienen.

**Paso 5 — Aplicar la corrección.** Una vez confirmada la causa raíz, aplicar la solución en el entorno más aislado posible antes de llevarla a producción. En sistemas de IA, la corrección puede ser técnica (ajustar el batch size, añadir validación de datos) o de modelo (reentrenar, hacer fine-tuning con datos recientes, actualizar el threshold de clasificación).

**Paso 6 — Verificar la solución.** La corrección aplicada debe confirmar que los síntomas desaparecen y que no se han introducido efectos secundarios. En sistemas de IA, la verificación debe incluir métricas de modelo, no solo métricas de infraestructura.

**Paso 7 — Documentar.** Registrar el problema, la causa raíz y la solución en el sistema de gestión de conocimiento del equipo. Esta documentación se convierte en la base de futuros runbooks.

### 4.2 Diagrama de flujo de diagnóstico para incidencias de modelo

```
[Alerta: degradación de métricas de modelo]
          |
          v
   ¿Hay cambio reciente en el pipeline de datos?
          |
    Sí ---+--- No
    |             |
    v             v
Revisar ETL   ¿Hay cambio reciente en el código del modelo o entorno?
    |             |
    |       Sí ---+--- No
    |       |             |
    |       v             v
    |   Rollback      Analizar distribución de inputs
    |   o fix         con Evidently AI
    |                     |
    |             ¿Se detecta data drift?
    |                     |
    |               Sí ---+--- No
    |               |             |
    |               v             v
    |          Reentrenamiento  ¿Se detecta concept drift?
    |          o adaptación          |
    |                          Sí ---+--- No
    |                          |             |
    |                          v             v
    |                    Fine-tuning    Revisar métricas de
    |                    con datos      evaluación y etiquetas
    |                    recientes      de ground truth
    |
    v
[Verificar mejora en métricas] ---> [Documentar y cerrar]
```

### 4.3 Método de los 5 Whys aplicado a IA

El método de los 5 Whys, popularizado por Toyota, es especialmente útil para incidencias de sistemas de IA porque ayuda a no quedarse en la capa técnica superficial y llegar a causas raíz organizativas o de proceso.

**Ejemplo aplicado a una incidencia de drift:**

1. **¿Por qué falló el modelo de clasificación de tickets de soporte?** Porque su accuracy cayó del 91% al 67% en dos semanas.
2. **¿Por qué cayó el accuracy?** Porque el modelo no reconoce correctamente una nueva categoría de incidencias que ha emergido tras el lanzamiento de un nuevo producto.
3. **¿Por qué el modelo no reconoce la nueva categoría?** Porque no existía en el momento del entrenamiento y no hay ejemplos de ella en los datos de entrenamiento.
4. **¿Por qué no había ejemplos de la nueva categoría en los datos de entrenamiento?** Porque el equipo de producto lanzó la funcionalidad sin informar al equipo de datos de que esto generaría un nuevo tipo de ticket.
5. **¿Por qué no existe un proceso de coordinación entre producto y datos para este tipo de cambios?** Porque el equipo de ML no tiene representación en el proceso de planificación de lanzamientos.

**Causa raíz real:** ausencia de un proceso organizativo de coordinación entre el equipo de producto y el equipo de ML. La corrección técnica (reentrenar el modelo) es necesaria pero insuficiente; la corrección estructural es añadir un punto de control en el proceso de lanzamiento de nuevas funcionalidades.

---

## 5. Observabilidad en sistemas ML

### 5.1 Los tres pilares: logs, métricas y trazas

La observabilidad de un sistema es su capacidad de inferir su estado interno a partir de sus salidas externas. En sistemas de ML, la observabilidad tiene una dimensión adicional respecto al software convencional: no solo hay que observar si el sistema funciona, sino si funciona correctamente desde el punto de vista estadístico.

**Logs:** registros estructurados de eventos discretos. Permiten responder a preguntas del tipo "¿qué ocurrió exactamente en el momento X?".

**Métricas:** series temporales de valores numéricos agregados. Permiten responder a preguntas del tipo "¿cómo evoluciona el comportamiento del sistema a lo largo del tiempo?".

**Trazas:** seguimiento de una petición individual a través de todos los componentes del sistema. Permiten responder a preguntas del tipo "¿por qué tardó 3 segundos esta petición concreta?".

### 5.2 Logging estructurado

El logging en texto plano es suficiente para depuración manual, pero resulta inmanejable a escala. El logging estructurado, habitualmente en formato JSON, permite indexar, filtrar y agregar logs con herramientas como Elasticsearch, Loki o CloudWatch Logs Insights.

Un log de inferencia bien estructurado debe incluir, como mínimo:

```json
{
  "timestamp": "2026-06-23T14:32:01.456Z",
  "level": "INFO",
  "service": "inference-api",
  "model_name": "clasificador-tickets-v3",
  "model_version": "3.2.1",
  "request_id": "req-7f8a2c9d",
  "input_tokens": 142,
  "inference_latency_ms": 87,
  "prediction": "categoria_tecnica",
  "confidence": 0.94,
  "input_hash": "sha256:a1b2c3...",
  "user_segment": "enterprise"
}
```

Los niveles de logging deben usarse con disciplina:
- `DEBUG`: información detallada útil durante el desarrollo, desactivada en producción.
- `INFO`: eventos normales del ciclo de vida del servicio (inicio, petición recibida, inferencia completada).
- `WARNING`: situaciones anómalas que no impiden el servicio pero que merecen atención (confianza del modelo por debajo del umbral, input con valores faltantes imputados).
- `ERROR`: fallos que impiden procesar una petición individual.
- `CRITICAL`: fallos que impiden el funcionamiento del servicio completo.

### 5.3 Métricas de modelo en Prometheus

Prometheus es el estándar de facto para la recolección y almacenamiento de métricas en entornos cloud-native. Para un servicio de inferencia, se deben exponer al menos las siguientes métricas:

**Métricas de infraestructura:**
- `inference_request_duration_seconds` (histogram): latencia de inferencia por percentil (p50, p95, p99).
- `inference_requests_total` (counter): número total de peticiones, etiquetado por estado (success, error).
- `inference_active_requests` (gauge): peticiones en curso en cada momento.
- `model_load_time_seconds` (gauge): tiempo de carga del modelo al inicio.

**Métricas de modelo:**
- `model_prediction_confidence` (histogram): distribución de la confianza de las predicciones.
- `model_prediction_class_distribution` (counter): distribución de clases predichas, para detectar cambios en la distribución de salida.
- `model_input_feature_mean` (gauge): media de cada feature numérica de entrada, para detectar data drift de forma ligera.
- `model_business_metric` (gauge): métrica de negocio relevante (por ejemplo, tasa de aceptación de recomendaciones), cuando el feedback está disponible en tiempo real.

### 5.4 Trazabilidad distribuida con OpenTelemetry

Una petición a un sistema de IA en producción típicamente atraviesa varios servicios: una API gateway, un servicio de preprocesamiento, el servidor de inferencia, una base de datos vectorial y un servicio de postprocesamiento. La trazabilidad distribuida permite seguir esa petición de extremo a extremo.

OpenTelemetry (OTel) es el estándar abierto para la instrumentación de trazas, métricas y logs. La instrumentación de un servicio de inferencia en Python con OpenTelemetry requiere:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Configuración del proveedor de trazas
provider = TracerProvider()
exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317")
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("inference-service")

def predict(input_data):
    with tracer.start_as_current_span("inference") as span:
        span.set_attribute("model.name", "clasificador-tickets-v3")
        span.set_attribute("model.version", "3.2.1")
        span.set_attribute("input.token_count", len(input_data))
        
        with tracer.start_as_current_span("preprocessing"):
            processed = preprocess(input_data)
        
        with tracer.start_as_current_span("model_forward_pass"):
            result = model(processed)
        
        span.set_attribute("prediction.confidence", float(result.confidence))
        return result
```

### 5.5 Dashboards con Grafana y alertas con Alertmanager

Grafana consume las métricas de Prometheus y permite construir dashboards visuales. Un dashboard de producción para un servicio de inferencia debe incluir, como mínimo:

- Gráfico de latencia por percentil (p50/p95/p99) en ventana de 1h y 24h.
- Tasa de errores (peticiones en estado `error` / total de peticiones).
- Throughput (peticiones por segundo).
- Distribución de confianza del modelo.
- Tendencia de la métrica de negocio.

Alertmanager gestiona las alertas que Prometheus dispara cuando una métrica supera un umbral. Las reglas de alerta se definen en YAML:

```yaml
groups:
  - name: inference_alerts
    rules:
      - alert: HighInferenceLatency
        expr: histogram_quantile(0.99, inference_request_duration_seconds_bucket) > 2.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Latencia p99 superior a 2 segundos durante 5 minutos"

      - alert: ModelConfidenceDrop
        expr: histogram_quantile(0.50, model_prediction_confidence_bucket) < 0.70
        for: 15m
        labels:
          severity: critical
        annotations:
          summary: "La confianza media del modelo ha caído por debajo del 70%"
```

---

## 6. Herramientas de diagnóstico específicas

### 6.1 `nvidia-smi` para problemas de GPU

`nvidia-smi` (NVIDIA System Management Interface) es la herramienta de línea de comandos para monitorizar y gestionar GPUs NVIDIA. Ante una incidencia de OOM o rendimiento degradado en GPU, los comandos más útiles son:

```bash
# Estado general de todas las GPUs
nvidia-smi

# Monitorización continua cada segundo
nvidia-smi dmon -s u -d 1

# Memoria utilizada por proceso
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv

# Utilización de GPU y memoria en tiempo real
watch -n 1 nvidia-smi
```

Los indicadores clave que se deben observar son la memoria utilizada (si se acerca al 100%, el riesgo de OOM es elevado), la utilización de la GPU (si es persistentemente baja mientras la CPU está al 100%, el cuello de botella está en el preprocesamiento o en el I/O) y la temperatura (temperaturas superiores a 85°C pueden causar throttling).

### 6.2 `torch.profiler` para perfilado de inferencia

PyTorch incluye un profiler nativo que permite identificar con precisión qué operaciones consumen más tiempo y memoria durante la inferencia:

```python
import torch
from torch.profiler import profile, record_function, ProfilerActivity

with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    record_shapes=True,
    profile_memory=True,
    with_stack=True
) as prof:
    with record_function("model_inference"):
        output = model(input_tensor)

print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=20))
prof.export_chrome_trace("inference_trace.json")
```

El resultado permite identificar si el tiempo se concentra en una capa específica, si hay transferencias de memoria CPU-GPU innecesarias o si el modelo tiene operaciones no optimizadas que podrían beneficiarse de cuantización o compilación con `torch.compile`.

### 6.3 py-spy para profiling de CPU en producción

`py-spy` es un profiler de muestreo para Python que puede adjuntarse a un proceso en ejecución sin necesidad de reiniciarlo ni modificar el código. Esto lo hace especialmente valioso para diagnosticar problemas de CPU en producción:

```bash
# Adjuntarse a un proceso en ejecución por PID
py-spy top --pid 12345

# Generar un flame graph del proceso
py-spy record -o flamegraph.svg --pid 12345 --duration 30

# Ver el stack trace en tiempo real
py-spy dump --pid 12345
```

El flame graph resultante permite identificar visualmente qué funciones consumen la mayor parte del tiempo de CPU, facilitando la detección de bucles ineficientes, llamadas a base de datos síncronas en el hot path o lógica de preprocesamiento mal optimizada.

### 6.4 Evidently AI para detección de data drift

Evidently AI es una librería open-source especializada en la monitorización de modelos de ML. Permite comparar la distribución de los datos de entrada en producción con la distribución de referencia (datos de entrenamiento o datos de un periodo anterior):

```python
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset

reference_data = pd.read_parquet("training_data.parquet")
current_data = pd.read_parquet("production_data_last_7_days.parquet")

report = Report(metrics=[
    DataDriftPreset(),
    DataQualityPreset(),
])

report.run(reference_data=reference_data, current_data=current_data)
report.save_html("drift_report.html")
```

El informe resultante muestra, para cada feature, si su distribución ha cambiado significativamente (usando tests estadísticos como Kolmogorov-Smirnov para variables continuas o chi-cuadrado para categóricas), el valor p del test y visualizaciones comparativas.

### 6.5 WhyLabs y Arize para monitorización continua

Para organizaciones que necesitan monitorización continua en producción, plataformas como WhyLabs o Arize AI ofrecen capacidades más avanzadas que la ejecución periódica de Evidently: ingesta de datos en tiempo real, alertas automáticas cuando se detecta drift, análisis de equidad por segmentos de población y trazabilidad de predicciones individuales.

### 6.6 Diagnóstico en Kubernetes

La mayoría de los sistemas de IA en producción se despliegan en Kubernetes. Los comandos esenciales para el diagnóstico son:

```bash
# Ver logs de un pod de inferencia
kubectl logs -f deployment/inference-service -n ml-prod

# Ver logs de los últimos 5 minutos con timestamps
kubectl logs --since=5m deployment/inference-service -n ml-prod --timestamps

# Describir un pod para ver eventos y estado de los contenedores
kubectl describe pod inference-service-7d9f8b-xk2p9 -n ml-prod

# Entrar en un contenedor para diagnóstico interactivo
kubectl exec -it inference-service-7d9f8b-xk2p9 -n ml-prod -- /bin/bash

# Ver el consumo de recursos de todos los pods
kubectl top pods -n ml-prod

# Ver eventos del namespace ordenados por tiempo
kubectl get events -n ml-prod --sort-by='.lastTimestamp'
```

---

## 7. Runbook de incidencias tipo

### 7.1 Estructura del runbook

Un runbook es un documento operativo que describe cómo responder a una incidencia específica. Su propósito es que cualquier miembro del equipo —incluso uno que no conozca el sistema en profundidad— pueda resolver un problema recurrente de forma autónoma.

La estructura estándar de un runbook incluye:

- **Descripción:** qué es esta incidencia y por qué ocurre.
- **Síntoma observable:** cómo se manifiesta; qué alerta se dispara; qué ven los usuarios.
- **Impacto:** severidad, componentes afectados, usuarios impactados.
- **Diagnóstico paso a paso:** comandos concretos, métricas a consultar, decisiones a tomar.
- **Resolución:** pasos para solucionar el problema, organizados por causa probable.
- **Escalado:** cuándo y a quién escalar si el runbook no resuelve el problema.
- **Prevención:** qué cambios evitarían que esta incidencia vuelva a ocurrir.

### 7.2 Ejemplo de runbook: degradación de métricas del modelo

**Nombre del runbook:** RB-ML-001 — Degradación de métricas del modelo de clasificación  
**Versión:** 1.3  
**Última actualización:** 2026-06-01  
**Propietario:** Equipo MLOps

**Descripción:** El modelo de clasificación ha mostrado una reducción sostenida (mayor de 5 puntos porcentuales en accuracy durante más de 24 horas) en sus métricas de rendimiento.

**Síntoma:** Alerta `ModelAccuracyDrop` disparada en Alertmanager. La métrica `model_accuracy_7d` en Grafana muestra una tendencia descendente.

**Impacto:** Medio. Las clasificaciones incorrectas generan tickets mal enrutados. Los usuarios no perciben un fallo del sistema, pero la eficiencia operativa se degrada.

**Diagnóstico:**

1. Acceder al dashboard de Grafana "ML Model Health" y verificar la ventana temporal en que comenzó la degradación.
2. Comprobar si hubo algún despliegue o cambio de configuración en ese momento: `kubectl rollout history deployment/inference-service -n ml-prod`.
3. Si hubo rollout reciente, comparar las métricas antes y después del rollout para confirmar la correlación.
4. Si no hubo rollout, ejecutar el reporte de drift de Evidently con los datos de los últimos 7 días comparados con los datos de referencia.
5. Revisar la distribución de clases predichas: `kubectl exec -it <pod> -- python /scripts/check_prediction_distribution.py --days 7`.
6. Si se detecta drift en features clave, proceder a la resolución por drift. Si no se detecta drift, escalar al equipo de Ciencia de Datos para revisión del modelo.

**Resolución:**

- **Si es un rollout defectuoso:** `kubectl rollout undo deployment/inference-service -n ml-prod`. Verificar que las métricas se recuperan en los siguientes 15 minutos.
- **Si es data drift:** Notificar al equipo de Ciencia de Datos con el informe de Evidently adjunto. El reentrenamiento se gestiona como tarea planificada, no como incidencia de emergencia, a menos que la degradación sea crítica.
- **Si es concept drift:** Escalar inmediatamente al equipo de Ciencia de Datos (P2). Puede ser necesario desactivar el modelo y sustituirlo por reglas de negocio manuales mientras se reentrenan.

**Escalado:** Si el diagnóstico no identifica la causa en 30 minutos, escalar a `@ml-oncall` en el canal `#incidencias-ml`.

### 7.3 Ejemplo de runbook: CUDA Out of Memory

**Nombre del runbook:** RB-ML-002 — CUDA Out of Memory en servicio de inferencia  
**Versión:** 2.0

**Síntoma:** Los pods del servicio de inferencia fallan con `torch.cuda.OutOfMemoryError: CUDA out of memory` en los logs. Las peticiones devuelven error 500. La alerta `InferencePodCrashLoop` está activa.

**Diagnóstico:**

1. Verificar el estado de los pods: `kubectl get pods -n ml-prod | grep inference`.
2. Obtener los logs del pod fallido: `kubectl logs <pod-name> -n ml-prod --previous`.
3. Conectar a un pod en ejecución y revisar el estado de la GPU: `kubectl exec -it <pod> -- nvidia-smi`.
4. Comprobar si el tamaño del batch ha cambiado recientemente revisando la configuración del ConfigMap.
5. Comprobar si el modelo ha sido actualizado y si la nueva versión es significativamente más grande.

**Resolución:**

- **Solución inmediata (P1):** Reducir el batch size a la mitad modificando el ConfigMap y reiniciando los pods: `kubectl rollout restart deployment/inference-service -n ml-prod`.
- **Si el problema persiste con batch size reducido:** Verificar que no hay fuga de memoria (tensores que no se liberan entre peticiones). Revisar que todos los tensores se crean con `torch.no_grad()` durante la inferencia.
- **Solución estructural:** Evaluar cuantización del modelo (INT8 o FP16) para reducir el footprint en memoria, o escalar a GPUs con mayor VRAM.

### 7.4 Escalado de incidencias: niveles de prioridad

| Nivel | Nombre | Criterio | Tiempo de respuesta | Tiempo de resolución |
|---|---|---|---|---|
| P1 | Crítico | Sistema completamente caído; pérdida de ingresos directa | 15 minutos | 4 horas |
| P2 | Alto | Degradación severa que afecta a más del 30% de usuarios | 30 minutos | 8 horas |
| P3 | Medio | Degradación que afecta a menos del 30% de usuarios o sin impacto en ingresos | 2 horas | 3 días laborables |
| P4 | Bajo | Problemas menores o mejoras preventivas | 1 día laborable | Según planificación |

---

## 8. Post-mortem y mejora continua

### 8.1 Estructura del post-mortem

Un post-mortem (también denominado "revisión de incidencia" o "análisis de causa raíz") es el documento que se elabora tras una incidencia significativa para entender qué ocurrió, por qué ocurrió y qué se puede hacer para evitar que vuelva a ocurrir o para reducir su impacto.

**Resumen ejecutivo:** Una descripción de tres o cuatro líneas que pueda leer alguien que no estuvo involucrado en la incidencia y que entienda qué ocurrió, cuándo, cuánto duró y cuál fue el impacto.

**Timeline:** Cronología detallada de los eventos, desde el primer síntoma hasta la resolución completa. Incluye las acciones tomadas por el equipo de respuesta. El timeline debe ser factual, sin juicios de valor.

**Causa raíz:** La causa o causas que originaron la incidencia, identificadas mediante el proceso de diagnóstico descrito en la sección 4. Se distingue entre causa raíz (el origen real del problema) y causa inmediata (el síntoma que desencadenó la alerta).

**Acciones correctivas:** Lista de acciones concretas, cada una con un responsable y una fecha de entrega, para corregir la causa raíz y mejorar la detección y respuesta en el futuro. Se dividen en:
- **Acciones de remediación:** corrigen el problema concreto.
- **Acciones de prevención:** evitan que el mismo tipo de problema vuelva a ocurrir.
- **Acciones de detección:** mejoran la capacidad del sistema para detectar el problema más rápidamente en el futuro.

### 8.2 Cultura blameless

El principio fundamental del post-mortem blameless es que las personas que trabajan en sistemas complejos tomaron las mejores decisiones posibles con la información que tenían en ese momento. Los fallos son síntomas de problemas sistémicos, no errores individuales.

Esta cultura tiene consecuencias prácticas: el post-mortem no pregunta "¿quién cometió el error?" sino "¿qué condiciones del sistema hicieron posible este error?". Esta perspectiva fomenta que los ingenieros sean honestos sobre lo que ocurrió, sin temor a consecuencias punitivas, lo que resulta en análisis de causa raíz más precisos y en mejoras sistémicas más efectivas.

### 8.3 Registro de incidencias como base de conocimiento

Cada incidencia documentada —el ticket, el runbook actualizado y el post-mortem— forma parte de la base de conocimiento del equipo. Con el tiempo, esta base de conocimiento permite:

- Identificar patrones recurrentes que indican problemas sistémicos no resueltos.
- Incorporar nuevos miembros al equipo con mayor rapidez.
- Fundamentar decisiones de arquitectura e inversión en fiabilidad con datos reales.
- Preparar simulacros de incidencias (game days) basados en escenarios reales.

### 8.4 Métricas MTTR y MTTF para sistemas de IA

**MTTF (Mean Time To Failure):** tiempo medio entre el momento en que el sistema está en buen estado y el momento en que sufre una incidencia. Un MTTF alto indica un sistema estable. En sistemas de IA, el MTTF debe calcularse separadamente para incidencias de modelo y para incidencias de infraestructura, ya que tienen naturalezas y tratamientos diferentes.

**MTTR (Mean Time To Repair/Restore):** tiempo medio desde que se detecta una incidencia hasta que el sistema vuelve a su estado normal. Un MTTR bajo indica capacidad de respuesta ágil. En sistemas de IA, es importante distinguir entre MTTR de restauración (el sistema vuelve a funcionar, aunque sea con un modelo más antiguo) y MTTR de resolución (la causa raíz está resuelta y el modelo está actualizado).

El coeficiente MTTR/MTTF es un indicador de la carga operativa relativa del equipo: cuanto más alto, mayor porcentaje del tiempo el equipo está gestionando incidencias en lugar de desarrollando nuevas capacidades.

---

## 9. Actividades prácticas

### Actividad 1 — Simulación de data drift y diagnóstico con Evidently AI

**Objetivo:** Experimentar el ciclo completo de detección y diagnóstico de data drift.

**Descripción:** A partir de un dataset de referencia proporcionado (datos de entrada de un modelo de clasificación de texto), el estudiante generará sintéticamente un conjunto de datos de producción con drift inducido (modificando la distribución de una o varias features). A continuación, ejecutará un análisis de Evidently AI para detectar el drift, identificará qué features han cambiado y documentará los hallazgos en un informe siguiendo la estructura de la sección 4.

**Entregable:** Informe HTML generado por Evidently AI más un documento de análisis de máximo 500 palabras que responda a: ¿qué drift se detectó?, ¿qué causa podría explicarlo en un escenario real?, ¿qué corrección se propondría?

### Actividad 2 — Instrumentación de un servicio de inferencia con OpenTelemetry

**Objetivo:** Configurar la observabilidad completa (logs estructurados, métricas Prometheus, trazas OTel) en un servicio de inferencia de ejemplo.

**Descripción:** Partiendo de un servicio Flask o FastAPI que expone un endpoint de inferencia (modelo sencillo de sklearn), el estudiante añadirá: logging estructurado en JSON con los campos mínimos descritos en la sección 5.2, exposición de métricas de Prometheus con la librería `prometheus_client`, e instrumentación de trazas con OpenTelemetry. Se desplegará una pila de observabilidad local con Docker Compose (Prometheus, Grafana, Jaeger) y se verificará que los datos aparecen correctamente en cada herramienta.

**Entregable:** Repositorio Git con el código del servicio instrumentado, el `docker-compose.yml` de la pila de observabilidad, y capturas de pantalla del dashboard de Grafana y de una traza en Jaeger.

### Actividad 3 — Redacción de un runbook

**Objetivo:** Practicar la documentación operativa siguiendo la estructura definida en la sección 7.

**Descripción:** Se proporciona al estudiante la descripción narrativa de una incidencia ocurrida en un sistema de IA ficticio (un motor de recomendaciones que comienza a recomendar artículos de una sola categoría a todos los usuarios). El estudiante debe redactar el runbook completo para esta incidencia, incluyendo diagnóstico paso a paso con comandos reales, árbol de decisión de resolución y criterios de escalado.

**Entregable:** Runbook en formato Markdown siguiendo la plantilla de la sección 7.1.

### Actividad 4 — Post-mortem de una incidencia simulada

**Objetivo:** Aplicar la cultura blameless y la metodología de análisis de causa raíz a una incidencia compleja.

**Descripción:** Se presenta al estudiante un escenario detallado de una incidencia de producción (incluyendo logs, métricas y una cronología de eventos) en un sistema de IA que sufrió una degradación severa de 6 horas. El estudiante debe elaborar el post-mortem completo: timeline, análisis de causa raíz mediante el método de los 5 Whys, acciones correctivas con responsables y fechas ficticias, y una reflexión de 200 palabras sobre qué decisiones del equipo fueron razonables dado el contexto de la incidencia (perspectiva blameless).

**Entregable:** Documento de post-mortem en formato Markdown.

---

## 10. Referencias

- Google SRE Team. *Site Reliability Engineering: How Google Runs Production Systems*. O'Reilly Media, 2016. Disponible en: [https://sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/)

- Huyen, Chip. *Designing Machine Learning Systems*. O'Reilly Media, 2022. Información del libro: [https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/)

- Evidently AI. *Documentación oficial de Evidently AI*. [https://docs.evidentlyai.com/](https://docs.evidentlyai.com/)

- OpenTelemetry. *Documentación oficial de OpenTelemetry*. [https://opentelemetry.io/docs/](https://opentelemetry.io/docs/)

- Prometheus. *Documentación oficial de Prometheus*. [https://prometheus.io/docs/introduction/overview/](https://prometheus.io/docs/introduction/overview/)

- Grafana Labs. *Documentación oficial de Grafana*. [https://grafana.com/docs/grafana/latest/](https://grafana.com/docs/grafana/latest/)

- PyTorch. *torch.profiler — Documentación oficial*. [https://pytorch.org/docs/stable/profiler.html](https://pytorch.org/docs/stable/profiler.html)

- Arize AI. *ML Observability Platform — Documentación*. [https://docs.arize.com/](https://docs.arize.com/)

- Google SRE. *The Art of the Postmortem*. [https://sre.google/sre-book/postmortem-culture/](https://sre.google/sre-book/postmortem-culture/)

- NVIDIA. *nvidia-smi — NVML Reference Manual*. [https://developer.nvidia.com/nvidia-system-management-interface](https://developer.nvidia.com/nvidia-system-management-interface)
