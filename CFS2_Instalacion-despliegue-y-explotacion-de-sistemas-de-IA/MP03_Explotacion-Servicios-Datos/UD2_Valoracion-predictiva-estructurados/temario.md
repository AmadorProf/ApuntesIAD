# UD2 · Valoración predictiva de datos estructurados

---

## 1. Introducción

Los datos estructurados —tablas relacionales, ficheros CSV, Parquet o Avro con esquema fijo— siguen siendo la forma más prevalente de datos en las organizaciones. El crédito bancario, la gestión de inventarios, el análisis de clientes, la detección de fraude y los precios dinámicos operan sobre registros tabulares con decenas o cientos de columnas numéricas, categóricas y temporales. A pesar del protagonismo mediático de los modelos de lenguaje y visión artificial, la mayoría de las decisiones de negocio automatizadas en producción están respaldadas por modelos de ML sobre datos estructurados: gradient boosting en sus distintas variantes, regresión logística regularizada, y redes neuronales de capas densas sobre features ingeniería.

La explotación en producción de estos modelos plantea retos técnicos que difieren significativamente de los del entrenamiento. Durante el entrenamiento, la prioridad es la experimentación rápida y la exploración del espacio de hiperparámetros; los tiempos de entrenamiento de minutos o horas son aceptables. En producción, el modelo debe responder en milisegundos, gestionar picos de carga sin degradación, ser actualizado sin interrumpir el servicio, y mantener su rendimiento frente a cambios en la distribución de los datos de entrada que el modelo no ha visto durante el entrenamiento. Estas exigencias requieren un conjunto de técnicas y herramientas específicas que van más allá del código Python del data scientist.

El **serving de modelos tabulares** involucra decisiones técnicas en múltiples capas: el formato de serialización del modelo (pickle, joblib, ONNX), la interfaz de servicio (REST API, gRPC, batch job), la estrategia de escalado (horizontal, vertical, serverless), la gestión de dependencias y versiones, y la instrumentación para monitorización. Cada una de estas decisiones tiene implicaciones en la latencia, el throughput, el consumo de recursos y la mantenibilidad del sistema. La elección del formato ONNX como representación intermedia independiente del framework, por ejemplo, permite separar el proceso de entrenamiento (que puede usar scikit-learn, XGBoost o LightGBM indistintamente) del proceso de serving (que puede usar un runtime optimizado para inferencia).

La **monitorización de modelos en producción** es el aspecto más frecuentemente subestimado en los despliegues de IA sobre datos estructurados. Un modelo entrenado en datos históricos opera sobre la hipótesis de que la distribución de los datos de producción será similar a la de entrenamiento. Esta hipótesis se viola constantemente: los comportamientos de los clientes cambian, los sistemas que generan los datos evolucionan, y los eventos externos (crisis económicas, cambios regulatorios, pandemias) alteran las distribuciones de forma abrupta o gradual. La detección temprana del **data drift** y el **concept drift** —la divergencia entre la distribución de entrenamiento y la de producción— es la diferencia entre un sistema de IA que mejora los resultados de negocio y uno que los empeora silenciosamente durante meses antes de que alguien lo detecte.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Desplegar modelos scikit-learn, XGBoost y LightGBM como REST APIs mediante FastAPI y frameworks de serving especializados como BentoML o MLflow Serving.
2. Convertir modelos entrenados con scikit-learn y XGBoost al formato ONNX y servir predicciones mediante ONNX Runtime, justificando las ventajas de portabilidad y rendimiento.
3. Implementar estrategias de batching dinámico para optimizar el throughput de un endpoint de inferencia, midiendo el impacto en latencia y RPS.
4. Describir los casos de uso más comunes de scoring predictivo sobre datos estructurados (scoring de crédito, churn prediction, detección de fraude, precios dinámicos) e identificar las características técnicas que los diferencian en términos de requisitos de latencia y volumen.
5. Diseñar e implementar un experimento A/B de modelos en producción, incluyendo el sistema de asignación aleatoria, la instrumentación de métricas de negocio y las condiciones de parada.
6. Configurar Evidently AI para monitorizar data drift y concept drift en un modelo de clasificación binaria en producción, definiendo umbrales de alerta y acciones de respuesta.
7. Distinguir entre métricas técnicas (AUC, F1, precisión, recall) y métricas de negocio (tasa de aprobación, coste del error tipo I y tipo II, revenue atribuido) y explicar cómo relacionarlas en el proceso de evaluación de modelos.
8. Implementar una estrategia de shadow mode para validar un nuevo modelo en producción sin exponer sus predicciones a los usuarios.

---

## 3. Serving de modelos sobre datos tabulares

### 3.1 Serialización de modelos: formatos y consideraciones

El primer paso para servir un modelo entrenado es persistirlo en un formato que pueda cargarse en el proceso de serving. Los formatos más comunes para modelos tabulares son:

| Formato | Frameworks compatibles | Portabilidad | Rendimiento inferencia | Caso de uso |
|---|---|---|---|---|
| joblib / pickle | scikit-learn, cualquier Python | Solo Python | Bajo | Desarrollo, prototipado |
| XGBoost nativo (.json/.ubj) | XGBoost | Solo XGBoost | Medio | Producción con XGBoost |
| LightGBM nativo (.txt/.bin) | LightGBM | Solo LightGBM | Medio | Producción con LightGBM |
| ONNX | Todos (con conversor) | Multi-lenguaje | Alto (ONNX Runtime) | Producción multi-plataforma |
| MLflow MLmodel | Todos (mediante flavors) | Multi-entorno | Variable | Plataformas MLflow |

El uso de **joblib** para scikit-learn:

```python
from sklearn.ensemble import GradientBoostingClassifier
import joblib

# Guardar modelo
model = GradientBoostingClassifier(n_estimators=200)
model.fit(X_train, y_train)
joblib.dump(model, "model.joblib", compress=3)

# Cargar modelo
model = joblib.load("model.joblib")
predictions = model.predict_proba(X_test)[:, 1]
```

### 3.2 ONNX como formato de intercambio

**ONNX (Open Neural Network Exchange)** es un formato abierto para representar modelos de ML. Define un grafo de operaciones con tipos de datos y shapes precisos, lo que permite ejecutar el modelo con distintos runtimes optimizados independientemente del framework de entrenamiento.

La conversión desde scikit-learn utiliza la librería `sklearn-onnx`:

```python
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import onnxruntime as rt
import numpy as np

# Conversión de modelo scikit-learn a ONNX
initial_type = [("float_input", FloatTensorType([None, X_train.shape[1]]))]
onnx_model = convert_sklearn(
    model,
    initial_types=initial_type,
    target_opset=17
)

with open("model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())

# Inferencia con ONNX Runtime
sess = rt.InferenceSession("model.onnx", providers=["CPUExecutionProvider"])
input_name = sess.get_inputs()[0].name
output_name = sess.get_outputs()[1].name  # probabilidades

X_infer = X_test.astype(np.float32)
proba = sess.run([output_name], {input_name: X_infer})[0][:, 1]
```

La conversión desde XGBoost:

```python
import xgboost as xgb
from onnxmltools.convert import convert_xgboost
from onnxmltools.convert.common.data_types import FloatTensorType

booster = xgb.Booster()
booster.load_model("model.xgb")

onnx_model = convert_xgboost(
    booster,
    initial_types=[("input", FloatTensorType([None, n_features]))]
)
```

ONNX Runtime ofrece rendimiento de inferencia significativamente superior al de los runtimes nativos de Python para cargas de trabajo de predicción por lotes, debido a las optimizaciones del grafo que aplica automáticamente (fusión de operaciones, cuantización, caché de kernels).

### 3.3 Serving con FastAPI

**FastAPI** es el framework más utilizado para construir APIs de inferencia personalizadas. Su sistema de validación basado en Pydantic garantiza que los inputs se validan antes de llegar al modelo:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import onnxruntime as rt
import numpy as np
import joblib

app = FastAPI(title="Credit Scoring API", version="2.1.0")

# Cargar modelo y preprocesador al arranque
model_session = rt.InferenceSession("model.onnx")
preprocessor = joblib.load("preprocessor.joblib")

class ScoringRequest(BaseModel):
    cliente_id: str
    edad: int = Field(ge=18, le=90)
    ingresos_mensuales: float = Field(gt=0)
    ratio_deuda_ingresos: float = Field(ge=0, le=1)
    meses_en_trabajo_actual: int = Field(ge=0)
    historico_impagos_12m: int = Field(ge=0)
    importe_solicitado: float = Field(gt=0)

class ScoringResponse(BaseModel):
    cliente_id: str
    score: float
    decision: str
    version_modelo: str

@app.post("/v2/predict", response_model=ScoringResponse)
async def predict(request: ScoringRequest):
    features = preprocessor.transform([[
        request.edad, request.ingresos_mensuales,
        request.ratio_deuda_ingresos, request.meses_en_trabajo_actual,
        request.historico_impagos_12m, request.importe_solicitado
    ]])
    
    proba = model_session.run(
        ["probabilities"],
        {"float_input": features.astype(np.float32)}
    )[0][0, 1]
    
    decision = "APROBADO" if proba >= 0.35 else "RECHAZADO"
    
    return ScoringResponse(
        cliente_id=request.cliente_id,
        score=round(float(proba), 4),
        decision=decision,
        version_modelo="2.1.0"
    )
```

### 3.4 Batching dinámico para optimización del throughput

El **batching dinámico** es la técnica de acumular varias peticiones individuales y procesarlas juntas en una sola llamada al modelo. ONNX Runtime y la mayoría de los frameworks de serving tienen capacidades nativas de batching. El beneficio es especialmente notable cuando la inferencia se realiza en GPU o cuando el modelo tiene una latencia fija alta que se amortiza procesando más registros:

```python
import asyncio
from collections import deque
import time

class DynamicBatcher:
    def __init__(self, model_session, max_batch_size=64, max_wait_ms=10):
        self.session = model_session
        self.max_batch = max_batch_size
        self.max_wait = max_wait_ms / 1000
        self.queue = deque()
        self.lock = asyncio.Lock()
    
    async def predict(self, features: np.ndarray) -> float:
        future = asyncio.get_event_loop().create_future()
        async with self.lock:
            self.queue.append((features, future))
        
        await asyncio.sleep(self.max_wait)
        
        async with self.lock:
            if not future.done():
                batch_items = list(self.queue)[:self.max_batch]
                for item in batch_items:
                    self.queue.remove(item)
                
                batch_features = np.vstack([item[0] for item in batch_items])
                results = self.session.run(
                    ["probabilities"],
                    {"float_input": batch_features.astype(np.float32)}
                )[0][:, 1]
                
                for (_, fut), result in zip(batch_items, results):
                    if not fut.done():
                        fut.set_result(float(result))
        
        return await future
```

---

## 4. Casos de uso de scoring predictivo en producción

### 4.1 Scoring de crédito

El **scoring de crédito** es el caso de uso más maduro de ML sobre datos estructurados. El modelo predice la probabilidad de impago de un cliente en un período determinado (típicamente 12 meses) a partir de variables sociodemográficas, historial financiero y comportamiento de uso de productos. Las características técnicas del caso de uso son:

- **Latencia requerida**: < 200 ms (para canales digitales en tiempo real) o batch (para evaluaciones nocturnas de cartera).
- **Volumen**: desde cientos de peticiones por hora en entidades pequeñas hasta cientos de miles por hora en grandes bancos.
- **Regulación**: los modelos de scoring de crédito están regulados por la Directiva 2008/48/CE (crédito al consumo) y el RGPD (explicabilidad de decisiones automatizadas). El EU AI Act los clasifica como sistemas de alto riesgo.
- **Métricas de evaluación primarias**: AUC-ROC, KS (Kolmogorov-Smirnov statistic), Gini coefficient.

### 4.2 Churn prediction

La predicción de abandono de clientes (**churn prediction**) estima la probabilidad de que un cliente cancele su relación con la empresa en los próximos N días o meses. Las características diferenciales son:

- La variable objetivo (churn) suele ser altamente desbalanceada (1-5% de churners), lo que requiere técnicas de balanceo (SMOTE, class_weight) o métricas de evaluación insensibles al desbalanceo (AUC-PR, F1 con umbral ajustado).
- El coste de los errores no es simétrico: el coste de perder un cliente (falso negativo) suele ser mucho mayor que el coste de una campaña de retención innecesaria (falso positivo). El umbral de decisión debe optimizarse en función de estos costes.
- El modelo se ejecuta típicamente en batch (diario o semanal) sobre toda la base de clientes, no en tiempo real.

### 4.3 Detección de fraude en tiempo real

La **detección de fraude** es el caso de uso más exigente en cuanto a latencia (< 100 ms, a menudo < 50 ms), ya que el resultado del modelo determina si una transacción se aprueba o bloquea en el momento en que ocurre. Las características técnicas son:

- Distribución extremadamente desbalanceada: la tasa de fraude en tarjetas de crédito es típicamente del 0.1-0.3%.
- Los modelos deben actualizarse frecuentemente (semanal o incluso diariamente) para adaptarse a los nuevos patrones de fraude.
- El coste del error tipo II (no detectar fraude real) es mucho mayor que el del tipo I (bloquear una transacción legítima), pero un tipo I elevado genera fricción y pérdida de clientes.
- Los features incluyen variables de comportamiento en ventanas temporales cortas (últimas 5 minutos, última hora) que deben calcularse en tiempo real, lo que hace que el feature store sea especialmente crítico.

### 4.4 Precios dinámicos

Los **modelos de precios dinámicos** ajustan el precio de productos o servicios en función de la demanda prevista, el inventario disponible, los precios de la competencia y el perfil del cliente. A diferencia de los casos anteriores, el output del modelo es un valor continuo (precio o descuento) y el objetivo es maximizar el revenue o el margen, no clasificar eventos. Las características son:

- Los modelos se ejecutan en tiempo real o near-real-time (segundos) para cada sesión de usuario o transacción.
- Los efectos del modelo son directamente observables en métricas de negocio (conversión, revenue por cliente), lo que facilita la evaluación online.
- Requieren mecanismos robustos de A/B testing para evaluar el impacto de los cambios de modelo sobre las métricas de negocio, ya que el sesgo de selección puede distorsionar las comparaciones naive.

---

## 5. Validación en producción: A/B testing, shadow mode y canary releases

### 5.1 A/B testing de modelos

El **A/B testing** consiste en asignar aleatoriamente una fracción del tráfico a un nuevo modelo (variante B) mientras el resto sigue siendo atendido por el modelo actual (variante A), y comparar las métricas de negocio entre ambos grupos tras un período de observación.

La implementación en el API Gateway consiste en un mecanismo de splitting por hash del identificador del cliente:

```python
import hashlib

def asignar_variante(cliente_id: str, porcentaje_b: float = 0.1) -> str:
    """Asignación determinista por hash: el mismo cliente siempre va al mismo grupo."""
    hash_value = int(hashlib.sha256(cliente_id.encode()).hexdigest(), 16) % 100
    return "B" if hash_value < (porcentaje_b * 100) else "A"
```

Los requisitos de un A/B test válido incluyen: asignación aleatoria (o determinista por hash, que garantiza que el mismo cliente siempre ve el mismo modelo), tamaño de muestra suficiente para detectar el efecto mínimo relevante (calculado con análisis de potencia estadística), período de observación suficiente para capturar ciclos completos de comportamiento, y condiciones de parada predefinidas (tanto de éxito como de seguridad).

### 5.2 Shadow mode

El **shadow mode** (o shadow deployment) consiste en enviar cada petición a dos modelos simultáneamente —el actual y el candidato— pero devolver al cliente únicamente la respuesta del modelo actual. Las predicciones del modelo candidato se registran internamente para análisis.

```python
import asyncio
import logging

async def predict_with_shadow(request, model_actual, model_candidato):
    # Ejecutar ambos modelos en paralelo
    resultado_actual, resultado_sombra = await asyncio.gather(
        model_actual.predict(request),
        model_candidato.predict(request)
    )
    
    # Registrar comparación (sin impacto en el usuario)
    logging.info({
        "evento": "shadow_comparison",
        "request_id": request.id,
        "score_actual": resultado_actual.score,
        "score_sombra": resultado_sombra.score,
        "diferencia": abs(resultado_actual.score - resultado_sombra.score),
        "decision_actual": resultado_actual.decision,
        "decision_sombra": resultado_sombra.decision,
        "coinciden": resultado_actual.decision == resultado_sombra.decision
    })
    
    # Devolver solo la respuesta del modelo actual
    return resultado_actual
```

El shadow mode permite acumular estadísticas sobre el comportamiento del candidato en producción real sin ningún riesgo, y detectar discrepancias sistemáticas entre ambos modelos antes de activar el cambio.

### 5.3 Canary release

El **canary release** es una estrategia intermedia entre el A/B test y el despliegue completo: el nuevo modelo se activa para un porcentaje pequeño del tráfico (5-10%) mientras se monitoriza activamente. Si los indicadores son correctos, el porcentaje se incrementa progresivamente. Si se detecta alguna anomalía, el rollback afecta solo a ese porcentaje.

---

## 6. Monitorización de modelos: data drift y concept drift

### 6.1 Tipos de drift

El **data drift** (también llamado covariate shift) se produce cuando la distribución de los datos de entrada en producción difiere de la distribución en el conjunto de entrenamiento. El modelo sigue siendo correcto (la relación entre features y target no ha cambiado), pero está recibiendo inputs fuera del dominio en que fue optimizado, lo que puede degradar su rendimiento.

El **concept drift** (también llamado label shift o posterior shift) se produce cuando la relación entre los features y la variable objetivo cambia. El modelo aprende una relación que deja de ser válida: por ejemplo, un modelo de scoring entrenado antes de una crisis económica que no captura los nuevos patrones de comportamiento de pago.

| Tipo de drift | Qué cambia | Ejemplo | Señal de detección |
|---|---|---|---|
| Data drift (covariate shift) | P(X) | Cambio en el perfil de edad de los solicitantes | Estadísticos de distribución de features |
| Label shift (prior probability shift) | P(Y) | Aumento de la tasa de impago por recesión | Distribución del target en producción |
| Concept drift | P(Y\|X) | Cambio en el comportamiento de pago de jóvenes | Degradación de métricas de rendimiento |
| Virtual drift | P(X) pero P(Y\|X) estable | Cambio de canal de captación | Data drift sin degradación de métricas |

### 6.2 Monitorización con Evidently AI

**Evidently AI** es la librería de código abierto de referencia para la monitorización de modelos ML en producción. Permite calcular y visualizar métricas de data drift, rendimiento del modelo y calidad de los datos de forma sencilla.

```python
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, ClassificationPreset
from evidently.metrics import *

# Cargar datos de referencia (entrenamiento) y producción (semana actual)
reference_data = pd.read_parquet("data/reference_dataset.parquet")
current_data = pd.read_parquet("data/production_week_2025_25.parquet")

# Reporte de data drift
drift_report = Report(metrics=[
    DataDriftPreset(drift_share=0.3),  # alerta si >30% features tienen drift
    DatasetSummaryMetric(),
])
drift_report.run(reference_data=reference_data, current_data=current_data)
drift_report.save_html("reports/drift_week_25.html")

# Reporte de rendimiento del modelo (si hay etiquetas disponibles)
performance_report = Report(metrics=[
    ClassificationPreset(),
    ColumnDriftMetric(column_name="score_modelo"),
])
performance_report.run(
    reference_data=reference_data,
    current_data=current_data.dropna(subset=["target_real"])
)
```

Evidently AI puede integrarse en un pipeline de monitorización continuo mediante su API de test suites:

```python
from evidently.test_suite import TestSuite
from evidently.tests import *

test_suite = TestSuite(tests=[
    TestNumberOfMissingValues(lte=0.05),              # < 5% valores nulos
    TestColumnDrift(column_name="ingresos_mensuales"), # sin drift en ingresos
    TestColumnDrift(column_name="edad"),               # sin drift en edad
    TestAUC(gte=0.75),                                 # AUC >= 0.75
    TestPrecisionScore(gte=0.70),
])

test_suite.run(reference_data=reference_data, current_data=current_data)
results = test_suite.as_dict()

# Activar alerta si algún test falla
failed_tests = [t for t in results["tests"] if t["status"] == "FAIL"]
if failed_tests:
    trigger_alert(failed_tests)
```

### 6.3 Métricas de negocio vs métricas técnicas

Las métricas técnicas de evaluación del modelo (AUC, F1, precisión) son necesarias pero no suficientes. El negocio opera con métricas de resultado que pueden divergir de las técnicas:

| Métrica técnica | Métrica de negocio correspondiente |
|---|---|
| AUC-ROC | Calidad de ranking (ordenación de riesgo) |
| Tasa de falsos positivos | Tasa de rechazo de clientes buenos (coste de oportunidad) |
| Tasa de falsos negativos | Tasa de impago no detectado (pérdida por crédito incobrable) |
| Precision en clase positiva | Porcentaje de fraudes reales sobre alertas generadas |
| Recall en clase positiva | Porcentaje de fraudes detectados sobre total de fraudes |

El umbral de decisión debe optimizarse no en función de la métrica técnica más alta, sino del punto que maximiza el valor esperado del negocio dado el coste diferencial de cada tipo de error.

---

## 7. Actividades prácticas

### Actividad 1 — Serving de un modelo de churn con FastAPI y ONNX

**Descripción**: El formador proporciona un notebook de entrenamiento de un modelo de churn prediction sobre un dataset de telecomunicaciones (scikit-learn GradientBoostingClassifier). El estudiante debe: exportar el modelo y el preprocesador a ONNX, construir una API con FastAPI que exponga el endpoint `/v1/predict` con validación Pydantic de los inputs, comparar la latencia de inferencia entre el modelo Python nativo y ONNX Runtime usando Apache Benchmark (`ab`) con 1000 peticiones y 10 conexiones concurrentes, y documentar los resultados en una tabla comparativa.

**Entregable**: Código de la API + fichero ONNX + tabla de comparativa de latencia con análisis.

**Criterios de evaluación**: Corrección de la conversión ONNX, validación de inputs implementada, igualdad de predicciones entre versión nativa y ONNX (diferencia < 0.001), rigor del benchmarking y análisis de resultados.

---

### Actividad 2 — Implementación de shadow mode

**Descripción**: Sobre el servicio desplegado en la actividad anterior, el estudiante debe implementar un shadow mode que ejecute en paralelo el modelo actual (GradientBoostingClassifier v1) y un modelo candidato (XGBoost entrenado con los mismos datos, proporcionado por el formador) sin modificar las respuestas devueltas al cliente. Las comparaciones deben registrarse en un fichero JSONL. Al final de la sesión, el estudiante debe analizar las discrepancias: porcentaje de predicciones con diferencia > 0.1, casos donde la decisión difiere, y distribución de las diferencias de score.

**Entregable**: Código del shadow mode + fichero JSONL de comparaciones + análisis de discrepancias (1 página).

**Criterios de evaluación**: Correcta implementación del paralelismo (sin bloqueo), completitud del registro de comparaciones, profundidad del análisis de discrepancias.

---

### Actividad 3 — Configuración de monitorización con Evidently AI

**Descripción**: El formador proporciona dos datasets: el dataset de referencia (entrenamiento) y tres datasets de producción correspondientes a tres semanas consecutivas, con diferentes grados de drift inducido artificialmente. El estudiante debe: configurar Evidently AI para generar reportes semanales de data drift y rendimiento, definir una test suite con al menos cinco tests con umbrales justificados, ejecutar la suite sobre los tres datasets y documentar cuándo y qué alertas se disparan en cada semana, y proponer las acciones a tomar en respuesta a cada tipo de alerta (reentrenamiento, investigación de datos, alerta al negocio).

**Entregable**: Código de la test suite + reportes HTML generados + documento de análisis y plan de respuesta (2 páginas).

**Criterios de evaluación**: Adecuación de los umbrales definidos, correcta interpretación de los resultados, solidez del plan de respuesta diferenciado por tipo de alerta.

---

### Actividad 4 — Diseño de A/B test para modelo de scoring

**Descripción**: El equipo de riesgo de una entidad financiera ha entrenado un nuevo modelo de scoring de crédito (XGBoost v3) que, en validación offline, muestra un AUC-ROC de 0.82 frente al 0.79 del modelo actual (GBM v2). El estudiante debe diseñar el A/B test para validar este modelo en producción: calcular el tamaño mínimo de muestra necesario para detectar una diferencia de 0.5 puntos porcentuales en la tasa de impago con 80% de potencia y nivel de significancia 0.05 (usando scipy.stats), definir el mecanismo de asignación de clientes a cada variante, identificar las métricas primarias y secundarias del test, y definir las condiciones de parada anticipada (por éxito o por daño).

**Entregable**: Documento de diseño del A/B test (2-3 páginas) con cálculos de muestra, código de asignación y definición de métricas y condiciones de parada.

**Criterios de evaluación**: Corrección del cálculo de tamaño muestral, validez estadística del diseño, completitud de las condiciones de parada, identificación de métricas de negocio relevantes.

---

## 8. Referencias

- **scikit-learn — Documentación oficial**: guía de persistencia de modelos y pipelines. Disponible en: [https://scikit-learn.org/stable/model_persistence.html](https://scikit-learn.org/stable/model_persistence.html)

- **XGBoost — Documentación oficial**: guía de uso, API Python y saving/loading de modelos. Disponible en: [https://xgboost.readthedocs.io/en/stable/](https://xgboost.readthedocs.io/en/stable/)

- **LightGBM — Documentación oficial**: guía de parámetros, API Python y casos de uso. Disponible en: [https://lightgbm.readthedocs.io/en/stable/](https://lightgbm.readthedocs.io/en/stable/)

- **ONNX — Especificación oficial**: definición del formato y operadores soportados. Disponible en: [https://onnx.ai/onnx/intro/](https://onnx.ai/onnx/intro/)

- **ONNX Runtime — Documentación oficial**: guía de uso del runtime de inferencia. Disponible en: [https://onnxruntime.ai/docs/](https://onnxruntime.ai/docs/)

- **sklearn-onnx — Documentación oficial**: guía de conversión de modelos scikit-learn a ONNX. Disponible en: [https://onnx.ai/sklearn-onnx/](https://onnx.ai/sklearn-onnx/)

- **FastAPI — Documentación oficial**: guía de desarrollo de APIs con FastAPI y Pydantic. Disponible en: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)

- **Evidently AI — Documentación oficial**: guía de uso de reportes, métricas y test suites. Disponible en: [https://docs.evidentlyai.com/](https://docs.evidentlyai.com/)

- **BentoML — Documentación oficial**: framework de serving de modelos ML. Disponible en: [https://docs.bentoml.com/](https://docs.bentoml.com/)

- **Google — Winning with AI: A/B Testing for Machine Learning Models**: artículo técnico sobre A/B testing de modelos en producción. Disponible en: [https://cloud.google.com/blog/products/ai-machine-learning/how-to-run-a-b-tests-for-ml-models](https://cloud.google.com/blog/products/ai-machine-learning/how-to-run-a-b-tests-for-ml-models)

- **Sculley et al. — Hidden Technical Debt in Machine Learning Systems (NIPS 2015)**: artículo seminal sobre los retos de los sistemas ML en producción. Disponible en: [https://papers.nips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html](https://papers.nips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html)

---

*UD2 · MP03 Explotación de Servicios de Datos y Analítica · CFS2 Instalación, despliegue y explotación de sistemas de IA*
