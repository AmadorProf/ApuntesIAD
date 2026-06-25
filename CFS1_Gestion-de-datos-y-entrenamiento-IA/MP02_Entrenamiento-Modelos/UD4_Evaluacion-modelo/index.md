---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD4 · Evaluación del modelo entrenado | MP02 · Entrenamiento de modelos de aprendizaje automático'
footer: 'Apuntes de IA y Datos'
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

# UD4 · Evaluación del modelo entrenado

**MP02 · Entrenamiento de modelos de aprendizaje automático**

Apuntes de IA y Datos

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Seleccionar las métricas de evaluación adecuadas según el tipo de tarea y el objetivo de negocio
- Calcular e interpretar métricas de clasificación: accuracy, F1, AUC-ROC y matriz de confusión
- Calcular e interpretar métricas de regresión: MSE, RMSE, MAE y R²
- Visualizar el comportamiento del modelo con matrices de confusión y curvas ROC
- Aplicar técnicas de interpretabilidad SHAP y LIME para identificar variables influyentes
- Tomar decisiones de rediseño basadas en el análisis de resultados

---

## Métricas de evaluación — Por qué importa la elección

Las métricas son el idioma con el que el modelo habla al negocio. Una métrica incorrecta puede dar la falsa sensación de que el modelo funciona bien cuando en realidad falla en los casos más importantes.

**Ejemplo real:**
> Un modelo de detección de fraude bancario con accuracy=99% puede ser completamente inútil si el 99% de las transacciones son legítimas. El modelo simplemente predice "legítima" siempre.

**Principio fundamental:**
- La métrica de optimización (la que guía el entrenamiento) puede diferir de la métrica de evaluación final
- La métrica de evaluación debe alinearse con el coste real del error en el contexto de negocio

---

## Métricas de clasificación — Conceptos base

A partir de la **matriz de confusión** se derivan todas las métricas de clasificación binaria:

| | Predicho: Positivo | Predicho: Negativo |
|---|---|---|
| **Real: Positivo** | VP (Verdadero Positivo) | FN (Falso Negativo) |
| **Real: Negativo** | FP (Falso Positivo) | VN (Verdadero Negativo) |

**Métricas derivadas:**
- **Accuracy** = (VP + VN) / Total — proporción de aciertos totales
- **Precision** = VP / (VP + FP) — de los que predigo positivo, cuántos lo son realmente
- **Recall** = VP / (VP + FN) — de los positivos reales, cuántos detecto
- **F1-score** = 2 · (Precision · Recall) / (Precision + Recall) — media armónica

---

## Métricas de clasificación — Cuándo priorizar cada una

| Contexto | Métrica prioritaria | Razón |
|---|---|---|
| Detección de fraude | Recall | Prefiero falsos positivos que fraudes no detectados |
| Diagnóstico médico (criba) | Recall | No perder ningún caso positivo real |
| Spam filtrado | Precision | No quiero borrar correos legítimos |
| Recomendación de contenido | F1 | Equilibrio entre relevancia y cobertura |
| Clases balanceadas | Accuracy | Métrica suficiente cuando el dataset es equilibrado |
| Clases desbalanceadas | F1 macro / AUC-ROC | Accuracy es engañosa en desbalance |

---

## Métricas de clasificación — Código de cálculo

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report, confusion_matrix, roc_auc_score
)
import numpy as np

y_pred = modelo.predict(X_test)
y_prob = modelo.predict_proba(X_test)[:, 1]  # probabilidad clase positiva

print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred):.4f}")
print(f"F1-score:  {f1_score(y_test, y_pred):.4f}")
print(f"AUC-ROC:   {roc_auc_score(y_test, y_prob):.4f}")

# Reporte completo por clase
print(classification_report(y_test, y_pred,
      target_names=["No tóxico", "Tóxico"]))
```

---

## Matriz de confusión — Visualización

```python
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# Método directo con ConfusionMatrixDisplay
fig, ax = plt.subplots(figsize=(6, 5))
disp = ConfusionMatrixDisplay(
    confusion_matrix=confusion_matrix(y_test, y_pred),
    display_labels=["No tóxico", "Tóxico"]
)
disp.plot(ax=ax, cmap="Blues", colorbar=False)
ax.set_title("Matriz de confusión — Modelo de toxicidad")
plt.tight_layout()
plt.savefig("matriz_confusion.png", dpi=150)

# Analisis de errores por clase
cm = confusion_matrix(y_test, y_pred)
print(f"Falsos positivos: {cm[0,1]} — Comentarios normales clasificados como tóxicos")
print(f"Falsos negativos: {cm[1,0]} — Comentarios tóxicos no detectados")
```

---

## Curva ROC y AUC — Concepto y visualización

La **curva ROC** representa el equilibrio entre la Tasa de Verdaderos Positivos (Recall) y la Tasa de Falsos Positivos para todos los umbrales de decisión posibles. El **AUC** (área bajo la curva) resume en un único número la capacidad discriminante del modelo.

```python
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

fpr, tpr, umbrales = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(7, 5))
plt.plot(fpr, tpr, label=f"Modelo (AUC = {roc_auc:.3f})", color="#2563eb")
plt.plot([0, 1], [0, 1], "k--", label="Clasificador aleatorio (AUC = 0.5)")
plt.xlabel("Tasa de Falsos Positivos")
plt.ylabel("Tasa de Verdaderos Positivos (Recall)")
plt.title("Curva ROC")
plt.legend()
plt.tight_layout()
plt.savefig("curva_roc.png", dpi=150)
```

> AUC=1.0 es perfecto, AUC=0.5 equivale a clasificación aleatoria.

---

## Métricas de regresión — Concepto y fórmulas

| Métrica | Fórmula | Interpetación | Sensibilidad a outliers |
|---|---|---|---|
| **MAE** | mean(\|y - y_hat\|) | Error absoluto medio en unidades del target | Baja |
| **MSE** | mean((y - y_hat)²) | Error cuadrático medio | Alta (penaliza outliers) |
| **RMSE** | sqrt(MSE) | Error en las mismas unidades que el target | Alta |
| **R²** | 1 - SS_res/SS_tot | Proporción de varianza explicada (0-1) | Media |
| **MAPE** | mean(\|y-y_hat\|/y)·100 | Error porcentual medio | Alta con valores cercanos a 0 |

> R²=1 indica ajuste perfecto; R²=0 indica que el modelo no supera la media; R² negativo indica que el modelo es peor que predecir siempre la media.

---

## Métricas de regresión — Código de cálculo

```python
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score
)
import numpy as np

y_pred = modelo.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)
mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

print(f"MAE:  {mae:.2f} €")
print(f"RMSE: {rmse:.2f} €")
print(f"R²:   {r2:.4f}")
print(f"MAPE: {mape:.2f}%")

# Grafico de predicciones vs valores reales
import matplotlib.pyplot as plt
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y_test.min(), y_test.max()],
         [y_test.min(), y_test.max()], "r--")
plt.xlabel("Valores reales"); plt.ylabel("Predicciones")
plt.title(f"Predicciones vs Reales — R²={r2:.3f}")
```

---

## Interpretabilidad XAI — Concepto y necesidad

La **interpretabilidad** (XAI, *Explainable AI*) permite entender por qué el modelo toma una decisión concreta. Es un requisito para modelos en dominios regulados (medicina, crédito, justicia) y fundamental para detectar sesgos.

**Tipos de explicación:**
- **Global:** qué variables son más importantes en general para el modelo
- **Local:** por qué el modelo predijo X para una instancia concreta

**Herramientas principales:**

| Técnica | Tipo | Modelos compatibles | Uso principal |
|---|---|---|---|
| **SHAP** | Global + Local | Todos (model-agnostic) | Importancia de features, efectos |
| **LIME** | Local | Todos (model-agnostic) | Explicaciones de instancia individual |
| **Grad-CAM** | Local | CNN (visión) | Zonas de activación en imágenes |
| **Attention Maps** | Local | Transformers | Palabras relevantes en texto |

---

## Interpretabilidad XAI — SHAP

```python
import shap
import matplotlib.pyplot as plt

# Para modelos de scikit-learn (tree-based)
explainer = shap.TreeExplainer(modelo_rf)
shap_values = explainer.shap_values(X_test)

# Grafico de importancia global de features
shap.summary_plot(shap_values, X_test,
                  feature_names=nombres_features,
                  plot_type="bar", show=False)
plt.tight_layout()
plt.savefig("shap_importance.png", dpi=150)

# Explicacion local para una instancia concreta
instancia_idx = 42
shap.waterfall_plot(
    shap.Explanation(
        values=shap_values[instancia_idx],
        base_values=explainer.expected_value,
        data=X_test[instancia_idx],
        feature_names=nombres_features
    )
)
```

---

## Interpretabilidad XAI — LIME

```python
import lime
import lime.lime_tabular

explainer_lime = lime.lime_tabular.LimeTabularExplainer(
    training_data=X_train,
    feature_names=nombres_features,
    class_names=["No tóxico", "Tóxico"],
    mode="classification",
    random_state=42
)

# Explicar una prediccion concreta
instancia = X_test[42]
explicacion = explainer_lime.explain_instance(
    data_row=instancia,
    predict_fn=modelo.predict_proba,
    num_features=10  # top 10 features mas influyentes
)

# Mostrar en notebook o guardar como HTML
explicacion.save_to_file("explicacion_instancia_42.html")

# Ver contribuciones de cada feature
for feature, peso in explicacion.as_list():
    print(f"{feature}: {peso:+.4f}")
```

---

## Análisis de errores — Patrones por clase o rango

Más allá de las métricas globales, el análisis detallado de los errores revela dónde falla el modelo y orienta el rediseño.

```python
import pandas as pd

# Crear dataframe de predicciones vs reales
resultados = pd.DataFrame({
    "real": y_test,
    "predicho": y_pred,
    "error": y_test - y_pred,
    "error_abs": abs(y_test - y_pred)
})

# Analizar errores por segmento de precio
resultados["rango_precio"] = pd.cut(y_test, bins=5)
print(resultados.groupby("rango_precio")["error_abs"].mean().sort_values(ascending=False))

# Detectar casos con mayor error (peores predicciones)
peores_casos = resultados.nlargest(20, "error_abs")
print(peores_casos[["real", "predicho", "error"]])
```

---

## Decisión de rediseño

Tras la evaluación, se debe tomar una decisión explícita y documentada sobre el modelo.

**Árbol de decisión post-evaluación:**

```
¿Las métricas alcanzan el umbral del proyecto?
├─ Sí → Pasar a UD5 (versionado y ficha técnica)
└─ No → Diagnosticar causa:
         ├─ Sobreajuste (train >> test) → Regularización, más datos, dropout
         ├─ Infraajuste (train y test bajos) → Arquitectura más compleja, más épocas
         ├─ Datos de mala calidad → Volver al preprocesamiento (MP01)
         ├─ Paradigma incorrecto → Volver a UD1
         └─ Features inadecuadas → Nuevo análisis de variables (UD1)
```

**Documentar la decisión:** métricas obtenidas, umbral requerido, diagnóstico de la causa del fallo y acción correctiva planificada.

---

## Actividad práctica — UD4

**Contexto:** El clasificador de texto tóxico ha terminado el entrenamiento definitivo. Los resultados en el conjunto de test son: accuracy=0.87, F1=0.79, AUC-ROC=0.91. La distribución de errores muestra que el modelo falla especialmente en comentarios irónicos y en lenguaje informal con abreviaturas.

**Tareas:**

1. Calcula todas las métricas de clasificación desde la matriz de confusión dada: VP=320, FP=48, FN=82, VN=1050
2. Genera y visualiza la matriz de confusión con etiquetas descriptivas
3. Aplica SHAP al modelo y describe qué palabras o tokens tienen mayor peso en la predicción de toxicidad
4. Analiza los falsos negativos: ¿qué tienen en común? ¿Qué acción correctiva propones?
5. Redacta la sección "Conclusiones de evaluación" del informe del modelo (máx. 200 palabras)

---

## Puntos clave — UD4

- Accuracy es una métrica engañosa con clases desbalanceadas: siempre complementar con F1 y AUC-ROC
- Precision y Recall son métricas opuestas: mejorar una empeora la otra; el punto de equilibrio depende del coste del error en el negocio
- La curva ROC permite elegir el umbral de decisión más adecuado después del entrenamiento, sin reentrenar
- SHAP es la herramienta de interpretabilidad más robusta: funciona con cualquier modelo y ofrece explicaciones globales y locales
- El análisis de errores por segmento o clase es más informativo que las métricas globales para guiar el rediseño
- R² negativo en regresión no significa "error de código": significa que el modelo es peor que predecir siempre la media del dataset

---

## Criterios de evaluación — UD4

| Criterio | Indicador de logro |
|---|---|
| Calcula métricas pertinentes | Selecciona y calcula las métricas adecuadas al tipo de tarea y objetivo de negocio |
| Interpreta la matriz de confusión | Identifica FP, FN, VP, VN y su implicación práctica |
| Visualiza resultados | Genera curva ROC y matriz de confusión interpretadas correctamente |
| Aplica XAI | Usa SHAP o LIME para identificar variables influyentes en las predicciones |
| Analiza patrones de error | Identifica en qué segmentos o clases falla más el modelo |
| Decide sobre el modelo | Documenta la decisión de validar o rediseñar con criterios técnicos |


---

<!-- nav-slide -->

## Navegación

[← UD3 · Operativización del entrenami…](../UD3_Operativizacion-entrenamiento/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD5 · Versionado y ficha técnica de… →](../UD5_Versionado-ficha-tecnica/)
