# UD4 · Validación de la calidad de los componentes de ML

---

## 1. Introducción — por qué el testing en ML es más complejo que en software clásico

En el desarrollo de software tradicional, una función es correcta si, dado un conjunto de entradas conocidas, produce exactamente las salidas esperadas. La lógica es determinista y los tests pueden verificar su corrección de forma binaria: pasa o no pasa. En el desarrollo de sistemas de Machine Learning, esta premisa se rompe en múltiples dimensiones.

El primer factor de complejidad es la naturaleza probabilística de los modelos. Un modelo no produce una respuesta "correcta" en el sentido clásico; produce una distribución de probabilidad o un valor continuo cuya calidad solo puede evaluarse estadísticamente sobre un conjunto de ejemplos. Esto significa que no es posible escribir un test que compruebe si la predicción de un ejemplo individual es "correcta" sin saber de antemano la respuesta, lo cual elimina la utilidad del test.

El segundo factor es la dependencia de los datos. Un componente de software clásico puede ser aislado del mundo exterior mediante mocks. Un modelo de ML lleva el mundo exterior incrustado en sus pesos: si los datos de entrenamiento cambian, el comportamiento cambia, aunque el código permanezca idéntico. Esto introduce el concepto de data drift y concept drift como fuentes de degradación que ningún test de código puede detectar por sí solo.

El tercer factor, identificado de forma canónica por Sculley et al. en su influyente artículo "Hidden Technical Debt in Machine Learning Systems" (2015), es la entanglement o entrelazamiento de características. En un sistema ML, cambiar cualquier entrada del modelo puede alterar el comportamiento en cualquier salida, incluso en ejemplos que no usan directamente esa característica. Este fenómeno hace que los tests de regresión deban cubrir el comportamiento del modelo de forma holística, no solo función a función.

El cuarto factor es el coste computacional del testing. Reentrenar un modelo desde cero para ejecutar un test es prohibitivo. Los tests deben diseñarse para poder ejecutarse sobre modelos preentrenados, datos de test fijos y versiones reducidas de los componentes.

Finalmente, existe el factor de la equidad y la responsabilidad. Un sistema de software puede funcionar correctamente desde el punto de vista funcional y al mismo tiempo discriminar a grupos de usuarios de formas que no son detectables sin tests específicamente diseñados para ello. La validación de fairness es una dimensión del testing que no tiene equivalente directo en el software clásico.

Todo esto no significa que el testing en ML sea imposible o irrelevante, sino que requiere una estrategia diferente, más amplia y más consciente de las fuentes de error particulares de los sistemas basados en datos y en modelos estadísticos. El objetivo de esta unidad es proporcionar esa estrategia.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Comprender las diferencias fundamentales entre el testing de software clásico y el testing de sistemas de ML, y justificar la necesidad de estrategias de validación específicas.
- Aplicar la pirámide de testing adaptada a ML para estructurar una suite de tests que cubra distintos niveles de granularidad y distintas fuentes de error.
- Escribir unit tests con pytest para componentes de preprocesamiento, transformación y lógica de negocio asociada a pipelines de ML, incluyendo el uso de fixtures, parametrize, mocking y cobertura de código.
- Implementar validación de esquemas de entrada y salida usando Pydantic, y extender esa validación con property-based testing usando Hypothesis para explorar el espacio de inputs inesperados.
- Diseñar e integrar regression tests de modelos que actúen como quality gates en un pipeline de CI, incluyendo la gestión de fixtures de datos y la fijación de seeds.
- Describir e implementar estrategias de shadow mode y canary deployment para validar nuevas versiones de modelos en producción de forma controlada y con capacidad de rollback automático.
- Definir un conjunto mínimo de smoke tests post-despliegue que garanticen que el servicio de inferencia está operativo y responde correctamente en los casos críticos.
- Integrar fairness testing en un pipeline de CI usando Fairlearn, estableciendo umbrales de equidad como requisitos funcionales que el modelo debe satisfacer para ser promovido a producción.

---

## 3. Pirámide de testing adaptada a ML

La pirámide de testing es un modelo conceptual originalmente propuesto para el desarrollo de software que establece que los tests deben distribuirse en capas, con muchos tests rápidos y baratos en la base y pocos tests lentos y costosos en la cima. Aplicada a ML, esta pirámide se reformula para dar cabida a las fuentes de error específicas de los sistemas basados en datos.

### 3.1 Base de la pirámide: unit tests

Los unit tests en ML no testean el modelo en sí, sino los componentes de código que rodean al modelo: funciones de preprocesamiento, transformadores de características, lógica de validación de inputs, funciones de postprocesamiento de predicciones y cualquier otra pieza de código que pueda ser aislada y verificada de forma determinista.

Estos tests deben ser rápidos (milisegundos), independientes entre sí y no requerir acceso a datos externos ni a modelos entrenados. Su objetivo es garantizar que la lógica de código es correcta antes de preocuparse por el comportamiento del modelo.

### 3.2 Tests de integración

Los integration tests verifican que los distintos componentes del pipeline funcionan correctamente cuando se combinan. Un pipeline de sklearn que encadena un imputador, un escalador y un clasificador puede funcionar correctamente en cada pieza por separado y fallar en la integración porque los tipos de salida de un componente no son compatibles con los tipos de entrada del siguiente.

Los integration tests deben usar datasets pequeños pero representativos, y su objetivo es verificar que el pipeline completo puede ejecutarse de principio a fin sin errores y que las transformaciones se encadenan correctamente.

### 3.3 Regression tests de métricas

Los regression tests de métricas son el equivalente en ML de los tests de regresión clásicos, pero en lugar de verificar que el comportamiento del código no ha cambiado, verifican que el rendimiento del modelo no ha caído por debajo de un umbral aceptable. Estos tests requieren un dataset de evaluación fijo y métricas definidas de antemano.

### 3.4 Behavioral testing

El behavioral testing, popularizado por el trabajo de Ribeiro et al. en el paper "Beyond Accuracy: Behavioral Testing of NLP Models with CheckList" (2020), propone verificar el comportamiento del modelo ante perturbaciones controladas de los inputs. Por ejemplo, en un modelo de análisis de sentimiento, cambiar el nombre de una persona en una reseña no debería cambiar la predicción. Estos tests de invarianza e monotonía permiten detectar dependencias espurias que las métricas globales no revelan.

### 3.5 La deuda técnica oculta de Sculley et al.

El artículo "Hidden Technical Debt in Machine Learning Systems" (Sculley et al., 2015, NeurIPS) es una referencia fundamental para entender por qué los sistemas ML acumulan deuda técnica de formas que el software clásico no experimenta. Los autores identifican fuentes de deuda específicas de ML: el entanglement de características ya mencionado, los undeclared consumers (sistemas que consumen outputs del modelo sin que el equipo lo sepa), la dependencia de datos de feedback que pueden introducir sesgos, y la erosión de las fronteras de abstracción que ocurre cuando el código del modelo y el código de negocio se mezclan.

La implicación para el testing es clara: una suite de tests robusta debe cubrir no solo el código, sino también las interfaces de datos, los contratos entre componentes y el comportamiento del modelo ante variaciones sistemáticas de los inputs.

---

## 4. Unit testing con pytest

### 4.1 Fixtures y parametrize

pytest organiza los tests en torno al concepto de fixture: una función que prepara el contexto necesario para que un test pueda ejecutarse. Las fixtures pueden ser de ámbito de función (se crean y destruyen para cada test), de módulo (una sola instancia por módulo) o de sesión (una sola instancia por ejecución de la suite). En ML, las fixtures de ámbito de módulo o sesión son útiles para cargar datasets o modelos preentrenados una sola vez.

```python
import pytest
import numpy as np
from sklearn.preprocessing import StandardScaler

@pytest.fixture(scope="module")
def sample_data():
    rng = np.random.default_rng(seed=42)
    X = rng.normal(loc=0, scale=1, size=(100, 5))
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    return X, y

def test_scaler_mean_zero(sample_data):
    X, _ = sample_data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    np.testing.assert_allclose(X_scaled.mean(axis=0), 0, atol=1e-10)
```

El decorador `@pytest.mark.parametrize` permite ejecutar el mismo test con múltiples conjuntos de parámetros, lo que es especialmente útil para verificar que una función de preprocesamiento se comporta correctamente ante distintos tipos de input:

```python
@pytest.mark.parametrize("input_value,expected", [
    (0.0, 0.0),
    (-1.0, 0.0),    # clipping en límite inferior
    (100.0, 1.0),   # normalización al máximo
    (np.nan, 0.5),  # imputación de missing values
])
def test_preprocessing_fn(input_value, expected):
    result = my_preprocessing_fn(input_value)
    assert result == pytest.approx(expected, abs=1e-6)
```

### 4.2 Testing de funciones de preprocesamiento con asserts sobre arrays numpy

Las funciones de preprocesamiento en ML operan sobre arrays de numpy, lo que requiere el uso de las funciones de aserción de numpy en lugar de los asserts de Python estándar. `np.testing.assert_allclose` verifica que dos arrays son iguales dentro de una tolerancia numérica, `np.testing.assert_array_equal` verifica igualdad exacta, y `np.testing.assert_array_less` verifica que todos los elementos de un array son menores que los del otro.

Un test completo para una función de imputación podría tener la siguiente estructura:

```python
def test_imputer_no_missing_after_transform(sample_data):
    X, _ = sample_data
    X_with_nans = X.copy()
    X_with_nans[0, 0] = np.nan
    X_with_nans[5, 3] = np.nan

    imputer = MedianImputer()
    X_imputed = imputer.fit_transform(X_with_nans)

    assert not np.any(np.isnan(X_imputed)), "El imputador no debe dejar NaN"
    assert X_imputed.shape == X_with_nans.shape, "La forma del array no debe cambiar"
```

### 4.3 Mocking de modelos y APIs externas con unittest.mock

Cuando un componente de código depende de un modelo preentrenado o de una API externa, los unit tests deben aislar ese componente mediante mocks. `unittest.mock` proporciona las herramientas necesarias para reemplazar objetos externos por dobles de test que devuelven respuestas controladas.

```python
from unittest.mock import MagicMock, patch
import numpy as np

def test_prediction_service_formats_output():
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([0, 1, 0])
    mock_model.predict_proba.return_value = np.array([
        [0.8, 0.2], [0.3, 0.7], [0.9, 0.1]
    ])

    service = PredictionService(model=mock_model)
    result = service.predict(inputs=["a", "b", "c"])

    assert len(result) == 3
    assert all("label" in r and "confidence" in r for r in result)
    mock_model.predict_proba.assert_called_once()
```

El uso de `patch` como context manager o decorador permite reemplazar temporalmente objetos en el espacio de nombres del módulo bajo test, lo que es útil para mockear llamadas a APIs externas como bases de datos de features o registros de modelos.

### 4.4 Cobertura con pytest-cov

`pytest-cov` es un plugin de pytest que mide la cobertura de código durante la ejecución de los tests. Se ejecuta con el flag `--cov` y genera un informe que muestra qué líneas de código fueron ejecutadas y cuáles no. En un pipeline de CI, es común establecer un umbral mínimo de cobertura (por ejemplo, 80%) que debe superarse para que el pipeline continúe.

```bash
pytest --cov=src/ml_components --cov-report=term-missing --cov-fail-under=80
```

Es importante entender que la cobertura de código no es equivalente a la calidad de los tests. Un test puede ejecutar una línea de código sin verificar que su resultado es correcto. La cobertura es una condición necesaria pero no suficiente para confiar en una suite de tests.

### 4.5 Ejemplo completo de test suite para pipeline sklearn

Una test suite completa para un pipeline de sklearn que encadena preprocesamiento y clasificación tendría tests a nivel de unidad para cada transformador, tests de integración para el pipeline completo y tests de regresión para las métricas del modelo final:

```python
# tests/test_pipeline.py
import pytest
import numpy as np
from sklearn.datasets import make_classification
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

@pytest.fixture(scope="module")
def classification_data():
    X, y = make_classification(n_samples=500, n_features=10,
                                random_state=42)
    return X, y

def test_pipeline_fits_without_error(classification_data):
    X, y = classification_data
    pipeline = build_pipeline()
    pipeline.fit(X, y)  # no debe lanzar excepción

def test_pipeline_output_shape(classification_data):
    X, y = classification_data
    pipeline = build_pipeline()
    pipeline.fit(X, y)
    predictions = pipeline.predict(X)
    assert predictions.shape == (len(y),)

def test_pipeline_output_classes(classification_data):
    X, y = classification_data
    pipeline = build_pipeline()
    pipeline.fit(X, y)
    predictions = pipeline.predict(X)
    assert set(predictions).issubset({0, 1})

def test_pipeline_minimum_accuracy(classification_data):
    X, y = classification_data
    pipeline = build_pipeline()
    pipeline.fit(X, y)
    accuracy = accuracy_score(y, pipeline.predict(X))
    assert accuracy >= 0.70, f"Accuracy {accuracy:.3f} por debajo del umbral mínimo"
```

---

## 5. Validación de esquemas de entrada/salida

### 5.1 Pydantic para validación de requests de inferencia

Cuando un modelo de ML se sirve como API, los requests de inferencia llegan en formato JSON y deben ser validados antes de ser procesados. Pydantic es la biblioteca estándar para esta tarea en el ecosistema Python. Permite definir esquemas de datos mediante clases que heredan de `BaseModel`, con validación automática de tipos, rangos y formatos.

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum

class CategoriaProducto(str, Enum):
    electronica = "electronica"
    ropa = "ropa"
    alimentacion = "alimentacion"

class InferenciaRequest(BaseModel):
    edad: int = Field(..., ge=18, le=120, description="Edad del usuario")
    ingresos_anuales: float = Field(..., gt=0)
    categoria: CategoriaProducto
    historial_compras: List[float] = Field(..., min_items=1, max_items=50)
    etiqueta_opcional: Optional[str] = None

    @validator("historial_compras")
    def historial_sin_negativos(cls, v):
        if any(x < 0 for x in v):
            raise ValueError("El historial de compras no puede contener valores negativos")
        return v

class InferenciaResponse(BaseModel):
    prediccion: int
    probabilidad: float = Field(..., ge=0.0, le=1.0)
    version_modelo: str
```

Esta definición de esquema sirve simultáneamente como documentación, como validación en runtime y como base para los tests de contrato.

### 5.2 Tests de contrato

Un test de contrato verifica que la interfaz entre dos componentes (por ejemplo, entre el servicio de inferencia y el cliente que lo consume) cumple las expectativas de ambas partes. En el contexto de ML, los tests de contrato garantizan que el esquema de la respuesta del modelo no ha cambiado entre versiones de una forma que rompa a los consumidores.

```python
def test_inferencia_response_schema():
    response = cliente.post("/predict", json=request_valido)
    assert response.status_code == 200
    data = response.json()

    # Verificar presencia de campos obligatorios
    assert "prediccion" in data
    assert "probabilidad" in data
    assert "version_modelo" in data

    # Verificar tipos
    assert isinstance(data["prediccion"], int)
    assert isinstance(data["probabilidad"], float)
    assert 0.0 <= data["probabilidad"] <= 1.0
```

### 5.3 Property-based testing con Hypothesis

Hypothesis es una biblioteca de property-based testing que genera automáticamente inputs que satisfacen las restricciones de un esquema Pydantic o de una especificación de tipos. En lugar de escribir casos de test individuales, el desarrollador describe las propiedades que deben ser verdaderas para todos los inputs válidos, y Hypothesis explora el espacio de posibles inputs buscando contraejemplos.

```python
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.pydantic import from_schema

@given(request=from_schema(InferenciaRequest))
@settings(max_examples=200)
def test_inferencia_nunca_lanza_excepcion_no_controlada(request):
    try:
        response = servicio.predict(request)
        assert 0 <= response.prediccion <= 1
        assert 0.0 <= response.probabilidad <= 1.0
    except ValidationError:
        pass  # Los errores de validación son esperados y aceptables
    except Exception as e:
        pytest.fail(f"Excepción no controlada: {type(e).__name__}: {e}")
```

Hypothesis es especialmente valioso para encontrar edge cases que los desarrolladores no habrían pensado en testear manualmente: valores en los límites de los rangos permitidos, listas vacías, strings con caracteres especiales, valores de punto flotante como `inf` o `nan`.

---

## 6. Regression tests de modelos

### 6.1 Comparación de métricas entre versiones

Un regression test de modelo verifica que una nueva versión del modelo no ha degradado el rendimiento respecto a la versión anterior. La implementación más directa consiste en evaluar ambas versiones sobre el mismo dataset de evaluación fijo y comparar sus métricas.

```python
def test_nueva_version_no_degrada_accuracy():
    X_eval, y_eval = cargar_dataset_evaluacion_fijo()

    modelo_actual = cargar_modelo("version_produccion")
    modelo_nuevo = cargar_modelo("version_candidata")

    acc_actual = accuracy_score(y_eval, modelo_actual.predict(X_eval))
    acc_nuevo = accuracy_score(y_eval, modelo_nuevo.predict(X_eval))

    UMBRAL_DEGRADACION = 0.02  # permitimos hasta un 2% de caída
    assert acc_nuevo >= acc_actual - UMBRAL_DEGRADACION, (
        f"Nueva versión ({acc_nuevo:.4f}) degrada la accuracy respecto "
        f"a la versión actual ({acc_actual:.4f}) más allá del umbral permitido"
    )
```

El umbral de degradación debe definirse en función del contexto de negocio: en algunos dominios, una caída del 1% en accuracy puede ser inaceptable; en otros, es ruido estadístico. Es recomendable definir umbrales separados para distintas métricas (precision, recall, F1, AUC-ROC) y para distintos subgrupos de datos.

### 6.2 Tests de regresión como quality gate en CI

En un pipeline de CI/CD para ML, los regression tests de modelos actúan como quality gates: si el modelo candidato no supera los umbrales definidos, el pipeline se detiene y el modelo no es promovido a producción. Esto requiere que el paso de evaluación del modelo esté automatizado y que sus resultados sean comparables de forma determinista.

La integración en CI puede realizarse mediante un script de evaluación que devuelve un código de salida distinto de cero cuando el modelo no supera los umbrales:

```bash
# En el pipeline de CI (ejemplo con GitHub Actions)
- name: Evaluar modelo candidato
  run: |
    python scripts/evaluate_model.py \
      --model-path models/candidate/model.pkl \
      --eval-data data/eval/fixed_eval_set.parquet \
      --thresholds config/quality_gates.yaml
```

### 6.3 Gestión de fixtures de datos de test

La reproducibilidad de los regression tests depende de que el dataset de evaluación sea estable y esté bajo control de versiones. Las recomendaciones son:

- Mantener un dataset de evaluación fijo que no se actualice con cada nuevo ciclo de entrenamiento.
- Versionar el dataset junto con el código (para datasets pequeños) o registrarlo en un data registry con un hash que permita verificar su integridad (para datasets grandes).
- Fijar la semilla aleatoria en todas las operaciones que la requieran (splits, submuestreo, aumentación de datos).
- Documentar el proceso de creación del dataset de evaluación para poder regenerarlo si es necesario.

```python
EVAL_SEED = 42
EVAL_SIZE = 5000

def crear_dataset_evaluacion():
    rng = np.random.default_rng(seed=EVAL_SEED)
    indices = rng.choice(len(dataset_completo), size=EVAL_SIZE, replace=False)
    return dataset_completo[indices]
```

---

## 7. Shadow mode y canary deployments

### 7.1 Shadow mode

El shadow mode es una estrategia de validación en producción en la que un nuevo modelo recibe el mismo tráfico que el modelo actual pero sus predicciones no se usan para tomar decisiones. El modelo en sombra procesa las mismas requests que el modelo de producción, sus predicciones se registran y se comparan con las del modelo actual, pero el usuario recibe la respuesta del modelo de producción.

Esta estrategia permite acumular evidencia estadística sobre el comportamiento del modelo nuevo en condiciones reales de producción sin ningún riesgo para los usuarios. Las métricas de comparación incluyen la tasa de acuerdo entre los dos modelos, las diferencias en la distribución de probabilidades predichas, la latencia y el uso de recursos.

```
Tráfico de entrada
        |
        v
[Modelo de Producción] -----> Respuesta al usuario
        |
        | (copia del request)
        v
[Modelo en Sombra] -----> Log de predicciones (no se usan)
                                |
                                v
                        [Sistema de análisis]
```

La implementación típica en un servicio de inferencia añade un paso asíncrono que envía el request al modelo en sombra sin bloquear la respuesta al usuario:

```python
async def predict(request: InferenciaRequest) -> InferenciaResponse:
    response = modelo_produccion.predict(request)

    # Llamada asíncrona al modelo en sombra (no bloquea)
    asyncio.create_task(
        shadow_predict_and_log(modelo_sombra, request, response)
    )

    return response
```

### 7.2 Canary deployments

Un canary deployment dirige un porcentaje pequeño del tráfico real hacia el nuevo modelo. A diferencia del shadow mode, en un canary deployment los usuarios del porcentaje "canary" reciben las predicciones del nuevo modelo y experimentan sus consecuencias reales. El porcentaje de tráfico se incrementa gradualmente a medida que se acumula confianza en el nuevo modelo.

La estrategia típica de incremento es: 1% → 5% → 10% → 25% → 50% → 100%. En cada etapa, se monitorizan métricas de calidad (accuracy en datos con etiqueta tardía, tasas de error, métricas de negocio) y métricas operativas (latencia, errores de servicio).

### 7.3 Rollback automático

Tanto en shadow mode como en canary deployment, es fundamental tener un mecanismo de rollback automático que revierta al modelo anterior si las métricas se deterioran por encima de un umbral definido. Este mecanismo puede implementarse como un servicio de monitorización que evalúa las métricas en tiempo real y activa una alerta o un cambio de configuración automático:

```python
def check_canary_health(metrics_window: MetricsWindow) -> HealthStatus:
    if metrics_window.error_rate > THRESHOLD_ERROR_RATE:
        trigger_rollback(reason="error_rate_exceeded")
        return HealthStatus.DEGRADED

    if metrics_window.p99_latency_ms > THRESHOLD_LATENCY_MS:
        trigger_rollback(reason="latency_exceeded")
        return HealthStatus.DEGRADED

    return HealthStatus.HEALTHY
```

---

## 8. Smoke tests en producción

### 8.1 Concepto y propósito

Un smoke test es un test mínimo que verifica que el sistema puede encenderse y responder. El término proviene de la ingeniería eléctrica, donde el primer test de un circuito nuevo consiste en alimentarlo con corriente y comprobar que no emite humo. En el contexto de ML en producción, los smoke tests son un conjunto pequeño de verificaciones que se ejecutan inmediatamente después de cada despliegue para confirmar que el servicio está operativo antes de enrutar tráfico real hacia él.

### 8.2 Health checks de la API

El endpoint `/health` (o `/healthz` en convenciones de Kubernetes) devuelve el estado del servicio. La convención más extendida distingue entre dos tipos de checks:

- **Liveness probe** (`/health/live`): verifica que el proceso está vivo y no ha entrado en un estado corrupto del que no puede recuperarse. Kubernetes usa este endpoint para decidir si debe reiniciar el contenedor.
- **Readiness probe** (`/health/ready`): verifica que el servicio está listo para recibir tráfico. Incluye la verificación de que el modelo está cargado en memoria, que las conexiones a bases de datos están activas y que los recursos necesarios están disponibles.

```python
@app.get("/health/live")
async def liveness():
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    checks = {
        "model_loaded": modelo is not None,
        "feature_store_connected": feature_store.ping(),
        "cache_connected": cache.ping(),
    }
    if all(checks.values()):
        return {"status": "ready", "checks": checks}
    raise HTTPException(status_code=503, detail=checks)
```

### 8.3 Tests de extremos críticos

Además de los health checks, los smoke tests deben incluir un conjunto mínimo de requests de inferencia con inputs representativos de los casos críticos del negocio. Estos tests verifican que el modelo produce predicciones dentro del rango esperado para ejemplos conocidos:

```python
def test_smoke_prediccion_caso_tipico():
    response = cliente.post("/predict", json=CASO_TIPICO_FIXTURE)
    assert response.status_code == 200
    assert response.json()["prediccion"] in [0, 1]

def test_smoke_prediccion_caso_limite_superior():
    response = cliente.post("/predict", json=CASO_LIMITE_SUPERIOR_FIXTURE)
    assert response.status_code == 200

def test_smoke_request_invalido_devuelve_422():
    response = cliente.post("/predict", json={"campo_inexistente": "valor"})
    assert response.status_code == 422
```

### 8.4 Integración en pipeline de despliegue

Los smoke tests deben ejecutarse como paso obligatorio en el pipeline de despliegue, después de que el servicio haya arrancado pero antes de que el load balancer empiece a enrutar tráfico hacia él. Si cualquier smoke test falla, el despliegue debe abortarse y el servicio debe revertirse a la versión anterior.

---

## 9. Fairness testing

### 9.1 El problema del sesgo en modelos de ML

Un modelo de ML puede tener una accuracy global excelente y al mismo tiempo tener un rendimiento significativamente peor para ciertos subgrupos de la población, como grupos definidos por género, edad, etnia o cualquier otra característica protegida. Este tipo de sesgo puede ser consecuencia de desbalances en los datos de entrenamiento, de correlaciones espurias entre características de entrada y características protegidas, o de la optimización de una métrica global que no captura las diferencias entre subgrupos.

El fairness testing no es un añadido opcional para sistemas de ML que toman decisiones que afectan a personas. Es un requisito funcional que debe estar especificado, testeable y automatizado.

### 9.2 Métricas de fairness

Las principales métricas de fairness son:

- **Demographic parity**: la tasa de predicciones positivas debe ser similar entre grupos. Formalmente: P(y_hat=1 | grupo=A) ≈ P(y_hat=1 | grupo=B).
- **Equalized odds**: tanto la tasa de verdaderos positivos (recall) como la tasa de falsos positivos deben ser similares entre grupos.
- **Equal opportunity**: la tasa de verdaderos positivos (recall) debe ser similar entre grupos.

La elección de la métrica de fairness adecuada depende del contexto de aplicación y tiene implicaciones éticas y legales que van más allá de la técnica.

### 9.3 Fairlearn en CI

Fairlearn es una biblioteca de Python desarrollada por Microsoft que proporciona herramientas para evaluar y mitigar el sesgo en modelos de ML. Su función `MetricFrame` permite calcular métricas desagregadas por subgrupo de forma sencilla:

```python
from fairlearn.metrics import MetricFrame, demographic_parity_difference
from sklearn.metrics import accuracy_score, recall_score

metric_frame = MetricFrame(
    metrics={
        "accuracy": accuracy_score,
        "recall": recall_score,
    },
    y_true=y_eval,
    y_pred=y_pred,
    sensitive_features=datos_eval["genero"]
)

print(metric_frame.by_group)
```

Para integrar Fairlearn en un pipeline de CI como quality gate, se define un test que comprueba que la diferencia de paridad demográfica no supera un umbral:

```python
def test_paridad_demografica_dentro_de_umbral():
    dp_diff = demographic_parity_difference(
        y_true=y_eval,
        y_pred=y_pred,
        sensitive_features=datos_eval["genero"]
    )
    UMBRAL_PARIDAD = 0.10
    assert abs(dp_diff) <= UMBRAL_PARIDAD, (
        f"Diferencia de paridad demográfica ({dp_diff:.4f}) "
        f"supera el umbral permitido ({UMBRAL_PARIDAD})"
    )

def test_equalized_odds_recall():
    recall_por_grupo = metric_frame.by_group["recall"]
    diferencia_recall = recall_por_grupo.max() - recall_por_grupo.min()
    UMBRAL_RECALL_DIFF = 0.05
    assert diferencia_recall <= UMBRAL_RECALL_DIFF, (
        f"Diferencia de recall entre grupos ({diferencia_recall:.4f}) "
        f"supera el umbral ({UMBRAL_RECALL_DIFF})"
    )
```

### 9.4 Umbrales de equidad como requisitos funcionales

El paso conceptualmente más importante es tratar los umbrales de equidad con el mismo estatus que cualquier otro requisito funcional del sistema. Un modelo que no supera los umbrales de fairness no está completo, de la misma forma que un modelo que no supera los umbrales de accuracy no está completo. Los umbrales deben estar especificados en la documentación del sistema, acordados con los stakeholders del negocio (incluyendo equipos legales y de compliance donde corresponda) y automatizados en el pipeline de CI de forma que su incumplimiento bloquee el despliegue.

---

## 10. Actividades prácticas

### Actividad 1: Construcción de una test suite para un pipeline de preprocesamiento

El estudiante recibirá un pipeline de preprocesamiento de datos tabulares que incluye imputación de valores perdidos, codificación de variables categóricas y escalado numérico. La tarea consiste en:

1. Identificar todos los casos de frontera relevantes para cada transformador (entradas con NaN, categorías no vistas en entrenamiento, valores fuera del rango de entrenamiento).
2. Escribir una test suite completa con pytest que cubra cada transformador por separado y el pipeline integrado, usando fixtures de ámbito de módulo para los datos de test.
3. Añadir tests parametrizados para los casos de frontera identificados en el paso anterior.
4. Medir la cobertura de la test suite con pytest-cov e identificar las líneas no cubiertas.
5. Añadir al menos un mock para aislar una dependencia externa del pipeline.

**Criterio de evaluación**: la test suite debe alcanzar un mínimo del 85% de cobertura de código y todos los tests deben pasar en menos de 30 segundos.

### Actividad 2: Validación de esquemas con Pydantic e Hypothesis

El estudiante recibirá la especificación de una API de inferencia para un modelo de scoring de crédito. La tarea consiste en:

1. Definir los modelos Pydantic para el request y el response de inferencia, incluyendo validadores personalizados para las restricciones de negocio (ingresos no negativos, edad entre 18 y 100 años, etc.).
2. Escribir tests de contrato que verifiquen que el servicio devuelve el esquema esperado para inputs válidos e inválidos.
3. Usar Hypothesis para generar 500 casos de test aleatorios que cumplan el esquema del request y verificar que el servicio nunca devuelve un error no controlado (500) ante inputs válidos.
4. Analizar los casos que Hypothesis encuentra que violan las propiedades definidas y corregir el servicio.

**Criterio de evaluación**: el servicio debe manejar todos los inputs válidos generados por Hypothesis sin lanzar excepciones no controladas.

### Actividad 3: Regression tests y quality gates en un pipeline de CI

El estudiante recibirá un repositorio con un modelo de clasificación de texto y un pipeline de CI en GitHub Actions. La tarea consiste en:

1. Crear un dataset de evaluación fijo de 1000 ejemplos con seed fija y registrarlo en el repositorio.
2. Escribir un script de evaluación que calcule accuracy, precision, recall y F1 sobre el dataset fijo y los compare contra umbrales definidos en un archivo de configuración YAML.
3. Integrar el script como paso del pipeline de CI, de forma que el pipeline falle si cualquier métrica cae por debajo del umbral.
4. Simular una regresión introduciendo un bug deliberado en el código de inferencia y verificar que el pipeline la detecta.
5. Añadir un test de fairness usando Fairlearn que verifique la paridad de recall entre dos subgrupos definidos en los metadatos del dataset.

**Criterio de evaluación**: el pipeline de CI debe detectar la regresión introducida y el test de fairness debe ejecutarse correctamente.

### Actividad 4: Diseño de una estrategia de smoke testing y shadow mode

El estudiante recibirá la arquitectura de un servicio de recomendaciones que sirve predicciones en tiempo real. La tarea consiste en:

1. Diseñar un conjunto mínimo de smoke tests post-despliegue para el servicio, incluyendo health checks y tests de los casos de uso críticos.
2. Implementar los smoke tests usando pytest y el cliente HTTP de FastAPI (TestClient).
3. Diseñar el flujo de shadow mode para el servicio, especificando los componentes necesarios (proxy, sistema de logging, sistema de análisis), las métricas de comparación que se monitorizarán y el criterio de decisión para promover el modelo en sombra a producción.
4. Redactar un documento técnico de una página que describa la estrategia de canary deployment para este servicio, incluyendo el plan de incremento de tráfico, las métricas de seguimiento y el criterio de rollback automático.

**Criterio de evaluación**: los smoke tests deben cubrir al menos los endpoints `/health/live`, `/health/ready` y el endpoint principal de predicción. El diseño del shadow mode debe ser técnicamente coherente con la arquitectura del servicio.

---

## 11. Referencias

- **pytest — documentación oficial**
  https://docs.pytest.org/en/stable/

- **pytest-cov — plugin de cobertura para pytest**
  https://pytest-cov.readthedocs.io/en/latest/

- **Hypothesis — property-based testing para Python**
  https://hypothesis.readthedocs.io/en/latest/

- **Hypothesis Pydantic extra — integración con modelos Pydantic**
  https://hypothesis.readthedocs.io/en/latest/extras.html#hypothesis-pydantic

- **Sculley, D. et al. (2015). "Hidden Technical Debt in Machine Learning Systems". Advances in Neural Information Processing Systems (NeurIPS), 28.**
  https://proceedings.neurips.cc/paper_files/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf

- **Fairlearn — documentación oficial**
  https://fairlearn.org/

- **Fairlearn — guía de evaluación de equidad**
  https://fairlearn.org/v0.10/user_guide/assessment/index.html

- **"Testing Machine Learning Systems: Code, Data and Models" — Made With ML**
  https://madewithml.com/courses/mlops/testing/

- **Ribeiro, M. T., Wu, T., Guestrin, C., & Singh, S. (2020). "Beyond Accuracy: Behavioral Testing of NLP models with CheckList". ACL 2020.**
  https://arxiv.org/abs/2005.04118

- **Pydantic — documentación oficial (v2)**
  https://docs.pydantic.dev/latest/

- **unittest.mock — documentación oficial Python**
  https://docs.python.org/3/library/unittest.mock.html

- **Google Testing Blog — "Testing in Production, the safe way"**
  https://testing.googleblog.com/2018/12/testing-in-production-safe-way.html

---

*UD4 · Validación de la calidad de los componentes de ML — CFS1 Gestión de datos y entrenamiento IA / MP03 Desarrollo de Componentes ML*
