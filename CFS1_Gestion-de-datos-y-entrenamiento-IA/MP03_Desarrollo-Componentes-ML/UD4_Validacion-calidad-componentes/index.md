---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD4 · Validación de la calidad de los componentes | MP03'
footer: 'CFS Gestión de datos y entrenamiento IA (IAD)'
---

<style>
section { font-family: 'Segoe UI', Arial, sans-serif; }
h1 { color: #1e3a5f; }
h2 { color: #1e3a5f; border-bottom: 2px solid #3b82f6; padding-bottom: 6px; }
h3 { color: #2563eb; }
table { font-size: 0.82em; width: 100%; }
ul, ol { font-size: 0.88em; }
blockquote { border-left: 4px solid #3b82f6; background: #eff6ff; padding: 8px 16px; border-radius: 4px; }
footer, header { font-size: 0.6em; color: #6b7280; }
section.lead h1 { font-size: 2em; text-align: center; margin-top: 80px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
pre { background: #1e293b; color: #e2e8f0; padding: 16px; border-radius: 8px; font-size: 0.8em; }
</style>

<!-- _class: lead -->

# UD4 · Validación de la calidad de los componentes

**MP03 · Desarrollo de componentes para sistemas de ML**
CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de aprendizaje

Al finalizar esta unidad el alumno sera capaz de:

- Verificar la consistencia y reproducibilidad del pipeline de datos
- Detectar y corregir sesgos en el pipeline y en el modelo
- Analizar el rendimiento del modelo sobre diferentes subconjuntos de datos
- Identificar sobreajuste e infraajuste con tecnicas de diagnostico
- Aplicar la metodologia KDD para extraccion de conocimiento
- Implementar algoritmos clasicos de ML (clasificacion, regresion, arboles, ensembles, SVM)
- Construir transformaciones de caracteristicas reutilizables (normalizacion, codificacion, caracteristicas derivadas)

---

## Mapa de la unidad

```
UD4 · Validacion de la calidad de los componentes
│
├── 1. Verificacion del pipeline
│   ├── Consistencia de transformaciones y formatos
│   └── Reproducibilidad e idempotencia
│
├── 2. Analisis de sesgos y fairness
│   └── Sesgos en datos y modelo, herramientas de evaluacion
│
├── 3. Rendimiento y diagnostico
│   ├── Metricas por subconjunto
│   └── Sobreajuste e infraajuste
│
├── 4. Metodologia KDD
│
└── 5. Algoritmos e ingenieria de caracteristicas
    └── Regresion, arboles, ensembles, SVM, ingenieria
```

---

## Verificacion del pipeline: checklist de consistencia

Un pipeline de ML es correcto cuando sus transformaciones son deterministas, sin perdida de informacion y sin introduccion de sesgos.

### Verificaciones obligatorias

| Verificacion | Que detecta | Como implementarla |
|---|---|---|
| Idempotencia | Outputs no deterministas | Ejecutar dos veces con la misma entrada y comparar |
| Tipos de dato | Conversiones incorrectas entre etapas | `assert df.dtypes.equals(schema_esperado)` |
| Rango de valores | Escala incorrecta post-normalizacion | `assert df[col].between(-3, 3).all()` |
| Ausencia de nulos | Nulos introducidos por el pipeline | `assert df.isnull().sum().sum() == 0` |
| Contaminacion train/test | Fuga de informacion | Comprobar que `fit` solo se llama con datos de train |
| Distribucion de clases | Sesgo de muestreo en particion | Comparar `value_counts(normalize=True)` de cada particion |

---

## Implementacion de tests de verificacion del pipeline

```python
import pytest
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline

class TestPipelineConsistencia:

    def test_idempotencia(self, pipeline_preprocesado, X_raw):
        """El pipeline debe producir el mismo resultado en dos ejecuciones."""
        resultado_1 = pipeline_preprocesado.transform(X_raw.copy())
        resultado_2 = pipeline_preprocesado.transform(X_raw.copy())
        pd.testing.assert_frame_equal(resultado_1, resultado_2)

    def test_sin_nulos_post_pipeline(self, pipeline_preprocesado, X_raw):
        """No debe haber nulos tras el preprocesado."""
        resultado = pipeline_preprocesado.transform(X_raw)
        assert resultado.isnull().sum().sum() == 0, \
            f"Nulos encontrados: {resultado.isnull().sum()}"

    def test_rango_normalizacion(self, pipeline_preprocesado, X_raw):
        """Las columnas normalizadas deben estar en [-3, 3] para StandardScaler."""
        resultado = pipeline_preprocesado.transform(X_raw)
        for col in resultado.select_dtypes(include=np.number).columns:
            assert resultado[col].between(-5, 5).all(), \
                f"Columna {col} fuera de rango esperado"

    def test_sin_contaminacion(self, pipeline, X_train, X_test):
        """El pipeline debe fitarse solo con datos de entrenamiento."""
        pipeline.fit(X_train)
        # Transformar test con parametros aprendidos solo de train
        X_test_procesado = pipeline.transform(X_test)
        assert X_test_procesado is not None
```

---

## Analisis de sesgos: tipos y origen

### Los tres origenes principales del sesgo en ML

```
DATOS ──────────────────────────────────────────────────────
Sesgo de representacion   → colectivos subrepresentados en el dataset
Sesgo de medicion         → errores sistematicos en la recogida de datos
Sesgo de etiquetado       → anotadores con criterios inconsistentes o prejudiciosos

MODELO ──────────────────────────────────────────────────────
Sesgo de agregacion       → el modelo promedia grupos con dinamicas distintas
Sesgo de evaluacion       → las metricas globales ocultan desigualdad entre grupos

DESPLIEGUE ──────────────────────────────────────────────────
Sesgo de retroalimentacion → las predicciones influyen en los datos futuros
Sesgo de uso              → el modelo se aplica a poblaciones diferentes a las de entrenamiento
```

> Un modelo puede tener alta precision global y discriminar sistematicamente a ciertos grupos. La auditoria de sesgo es parte del proceso de validacion, no un paso opcional.

---

## Herramientas de analisis de fairness

```python
from fairlearn.metrics import (
    MetricFrame, demographic_parity_difference,
    equalized_odds_difference, selection_rate
)
from sklearn.metrics import accuracy_score

# Evaluar el modelo por grupos sensibles
frame_metricas = MetricFrame(
    metrics={
        "accuracy":        accuracy_score,
        "tasa_seleccion":  selection_rate,
    },
    y_true=y_test,
    y_pred=predicciones,
    sensitive_features=grupo_sensible_test   # ej: genero, edad, codigo_postal
)

print("Metricas por grupo:")
print(frame_metricas.by_group)

print(f"\nDiferencia de paridad demografica: "
      f"{demographic_parity_difference(y_test, predicciones, sensitive_features=grupo_sensible_test):.3f}")

print(f"Diferencia de igualdad de oportunidades: "
      f"{equalized_odds_difference(y_test, predicciones, sensitive_features=grupo_sensible_test):.3f}")

# Valores proximos a 0 indican equidad entre grupos
```

---

## Diagnostico: sobreajuste e infraajuste

```python
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve

def diagnosticar_ajuste(estimador, X, y, cv=5):
    """
    Curva de aprendizaje para diagnosticar sobreajuste e infraajuste.
    """
    tamanos, scores_train, scores_val = learning_curve(
        estimador, X, y,
        train_sizes=np.linspace(0.1, 1.0, 10),
        cv=cv, scoring="f1_macro",
        n_jobs=-1
    )

    train_mean = scores_train.mean(axis=1)
    val_mean   = scores_val.mean(axis=1)
    gap = train_mean[-1] - val_mean[-1]

    diagnostico = (
        "SOBREAJUSTE (reducir complejidad o anadir regularizacion)" if gap > 0.1
        else "INFRAAJUSTE (aumentar complejidad o mas datos)" if val_mean[-1] < 0.7
        else "AJUSTE CORRECTO"
    )

    print(f"F1 train: {train_mean[-1]:.3f} | F1 val: {val_mean[-1]:.3f}")
    print(f"Gap: {gap:.3f} -> {diagnostico}")
    return tamanos, train_mean, val_mean
```

---

## Rendimiento sobre subconjuntos

El rendimiento global puede enmascarar debilidades criticas en subpoblaciones especificas.

```python
import pandas as pd
from sklearn.metrics import classification_report

def evaluar_por_subconjunto(modelo, X_test: pd.DataFrame,
                             y_test: pd.Series, columnas_grupo: list):
    """
    Evalua el modelo en cada subconjunto definido por las columnas de grupo.
    """
    resultados = []
    for col in columnas_grupo:
        for valor in X_test[col].unique():
            mascara = X_test[col] == valor
            X_sub = X_test[mascara].drop(columns=columnas_grupo)
            y_sub = y_test[mascara]

            if len(y_sub) < 30:
                continue  # Subconjunto demasiado pequeno para ser fiable

            y_pred = modelo.predict(X_sub)
            report = classification_report(y_sub, y_pred, output_dict=True)
            resultados.append({
                "grupo": col, "valor": valor,
                "n": len(y_sub),
                "f1_macro": report["macro avg"]["f1-score"],
                "accuracy": report["accuracy"]
            })

    return pd.DataFrame(resultados).sort_values("f1_macro")
```

---

## Metodologia KDD: extraccion de conocimiento

La metodologia KDD (Knowledge Discovery in Databases) estructura el proceso de ML como una cadena de etapas con validacion en cada transicion.

```
1. SELECCION
   Identificar los datos relevantes para el objetivo
   → Subconjunto de atributos y registros

2. PREPROCESAMIENTO
   Limpiar, tratar nulos, eliminar ruido
   → Datos limpios y coherentes

3. TRANSFORMACION
   Normalizar, codificar, generar caracteristicas derivadas
   → Dataset listo para mineria

4. MINERIA DE DATOS
   Aplicar el algoritmo de ML
   → Patrones, modelos, reglas

5. INTERPRETACION Y EVALUACION
   Validar, explicar, desplegar o refinar
   → Conocimiento aplicable
```

> KDD no es lineal: los resultados de la mineria pueden requerir volver a las etapas anteriores para refinar la seleccion o el preprocesado.

---

## Algoritmos clasicos de ML: regresion y clasificacion

```python
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error, r2_score, classification_report

# Regresion lineal
reg_lineal = LinearRegression()
reg_lineal.fit(X_train, y_train)
y_pred = reg_lineal.predict(X_test)
print(f"R2: {r2_score(y_test, y_pred):.3f}")
print(f"RMSE: {mean_squared_error(y_test, y_pred, squared=False):.3f}")
print(f"Coeficientes: {dict(zip(feature_names, reg_lineal.coef_.round(3)))}")

# Regresion logistica (clasificacion)
reg_logistica = LogisticRegression(
    C=1.0,                    # inverso de la regularizacion
    max_iter=1000,
    solver="lbfgs",
    multi_class="multinomial",
    random_state=42
)
reg_logistica.fit(X_train, y_train)
y_pred_cls = reg_logistica.predict(X_test)
print(classification_report(y_test, y_pred_cls, digits=3))
```

---

## Arboles de decision y Random Forest

```python
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# Arbol de decision: interpretable
arbol = DecisionTreeClassifier(
    max_depth=4,
    min_samples_leaf=20,
    class_weight="balanced",
    random_state=42
)
arbol.fit(X_train, y_train)

# Visualizar reglas del arbol
reglas = export_text(arbol, feature_names=feature_names)
print(reglas[:500])

# Random Forest: robusto, menos interpretable
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    min_samples_leaf=10,
    class_weight="balanced",
    n_jobs=-1,
    random_state=42
)
rf.fit(X_train, y_train)

# Importancia de caracteristicas
importancia = pd.Series(rf.feature_importances_, index=feature_names)
print(importancia.sort_values(ascending=False).head(10))
```

---

## SVM y metodos de potenciacion (Boosting)

```python
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

# SVM: requiere normalizacion obligatoria
pipeline_svm = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", SVC(
        C=10.0,
        kernel="rbf",
        gamma="scale",
        class_weight="balanced",
        probability=True,       # habilitar predict_proba
        random_state=42
    ))
])
pipeline_svm.fit(X_train, y_train)

# XGBoost: estado del arte en datos tabulares
xgb_model = xgb.XGBClassifier(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=5,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=len(y_train[y_train==0]) / len(y_train[y_train==1]),  # desbalanceo
    use_label_encoder=False,
    eval_metric="logloss",
    random_state=42
)
xgb_model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=100)
```

---

## Ingenieria de caracteristicas reutilizables

```python
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class TransformadorCaracteristicasFecha(BaseEstimator, TransformerMixin):
    """
    Extrae caracteristicas temporales de columnas de fecha.
    Compatible con sklearn Pipeline: fit/transform reutilizable.
    """

    def __init__(self, columnas_fecha: list):
        self.columnas_fecha = columnas_fecha

    def fit(self, X: pd.DataFrame, y=None):
        return self   # sin aprendizaje necesario

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        for col in self.columnas_fecha:
            fechas = pd.to_datetime(X[col])
            X[f"{col}_mes"]           = fechas.dt.month
            X[f"{col}_dia_semana"]    = fechas.dt.dayofweek
            X[f"{col}_es_fin_semana"] = (fechas.dt.dayofweek >= 5).astype(int)
            X[f"{col}_trimestre"]     = fechas.dt.quarter
            X[f"{col}_sin_mes"]       = np.sin(2 * np.pi * fechas.dt.month / 12)
            X[f"{col}_cos_mes"]       = np.cos(2 * np.pi * fechas.dt.month / 12)
            X = X.drop(columns=[col])
        return X
```

---

## Normalizacion y codificacion en pipeline reutilizable

```python
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, OrdinalEncoder, OneHotEncoder
)
from sklearn.compose import ColumnTransformer
import pandas as pd

def construir_preprocesador(
    cols_numericas: list,
    cols_categoricas_ohe: list,
    cols_categoricas_ord: list,
    orden_ordinal: list[list]
) -> ColumnTransformer:
    """
    Construye un preprocesador reutilizable para multiples datasets.
    """
    return ColumnTransformer(
        transformers=[
            ("num",  StandardScaler(),
             cols_numericas),
            ("cat_ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
             cols_categoricas_ohe),
            ("cat_ord", OrdinalEncoder(
                categories=orden_ordinal,
                handle_unknown="use_encoded_value",
                unknown_value=-1
            ), cols_categoricas_ord)
        ],
        remainder="drop"   # descartar columnas no declaradas
    )
```

---

## Actividad practica — UD4

### Auditoria de calidad de un pipeline de ML

**Escenario:** un pipeline de clasificacion de solicitudes de credito ha sido entrenado con datos historicos. Antes de desplegarlo en produccion se debe realizar una auditoria completa de calidad.

**Tareas:**
1. Implementar los tests de consistencia del pipeline (idempotencia, nulos, rango, tipos)
2. Analizar el rendimiento del modelo por subgrupos (edad, genero, codigo postal)
3. Calcular las metricas de fairness con `Fairlearn` y detectar posibles sesgos
4. Generar la curva de aprendizaje y diagnosticar sobreajuste o infraajuste
5. Comparar tres algoritmos (Regresion Logistica, Random Forest, XGBoost) con validacion cruzada
6. Documentar los hallazgos en un informe de calidad con las recomendaciones de mejora

**Entregable:** cuaderno Jupyter con todos los tests, graficos de diagnostico e informe de calidad en formato estructurado.

---

## Puntos clave — UD4

- La verificacion del pipeline debe automatizarse con tests unitarios: los errores manuales no son detectables a escala
- La reproducibilidad exige fijar la semilla aleatoria en todos los componentes y versionar tanto el codigo como los datos
- El rendimiento global puede enmascarar discriminacion sistematica: siempre evaluar por subgrupos antes de desplegar
- La curva de aprendizaje es el diagnostico mas informativo de sobreajuste e infraajuste: no sustituirla por heuristicas
- KDD proporciona un marco sistematico que evita decisiones ad-hoc y garantiza la trazabilidad de cada transformacion
- Los transformadores sklearn con `fit/transform` son la forma correcta de encapsular transformaciones reutilizables: compatibles con `Pipeline` y `GridSearchCV`
- La ingenieria de caracteristicas temporales (ciclica con seno/coseno) es mas informativa que usar el mes como numero entero

---

## Criterios de evaluacion — UD4

- Implementa tests automatizados de consistencia y reproducibilidad del pipeline
- Verifica la ausencia de contaminacion entre particiones de entrenamiento y test
- Analiza sesgos con `Fairlearn` u otra herramienta de fairness y documenta los resultados
- Evalua el rendimiento sobre subconjuntos relevantes e identifica grupos con rendimiento inferior
- Diagnostica sobreajuste e infraajuste con curvas de aprendizaje y propone acciones correctivas
- Implementa transformaciones de caracteristicas reutilizables compatibles con sklearn Pipeline

---

<!-- _class: lead -->

[← Volver a MP03](../)


---

<!-- nav-slide -->

## Navegación

[← UD3 · Integración de modelos en apl…](../UD3_Integracion-modelos-aplicaciones/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD5 · Protocolización y documentaci… →](../UD5_Protocolizacion-documentacion/)
