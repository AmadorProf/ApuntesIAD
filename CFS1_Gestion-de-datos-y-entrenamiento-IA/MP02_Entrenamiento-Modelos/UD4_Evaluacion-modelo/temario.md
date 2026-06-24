# UD4 · Evaluación del modelo entrenado

**Módulo:** MP02 Entrenamiento de Modelos  
**Ciclo:** CFS1 Gestión de Datos y Entrenamiento IA  
**Horas estimadas:** 12 h lectivas + 6 h prácticas

---

## 1. Introducción

La evaluación de modelos de aprendizaje automático no es un paso final que se ejecuta una única vez antes de poner un sistema en producción. Es un proceso continuo que acompaña todo el ciclo de vida del modelo, desde los primeros experimentos con datos de entrenamiento hasta el seguimiento de comportamiento en producción semanas o meses después del despliegue.

Esta distinción conceptual es fundamental. Un modelo puede rendir excepcionalmente bien sobre el conjunto de prueba inicial y deteriorarse progresivamente a medida que la distribución de los datos de entrada evoluciona —fenómeno conocido como *data drift* o *concept drift*. Por esta razón, los equipos de MLOps establecen pipelines de monitorización que recalculan métricas sobre ventanas de tiempo deslizantes y emiten alertas cuando la calidad cae por debajo de umbrales predefinidos.

En el contexto académico de esta unidad, distinguimos dos grandes familias de evaluación:

**Evaluación offline.** Se realiza sobre conjuntos de datos estáticos —validación cruzada, conjunto de prueba reservado— antes de que el modelo entre en contacto con usuarios reales. Permite comparar alternativas de forma controlada, reproducible y barata. Las métricas clásicas de clasificación, regresión y clustering pertenecen a este dominio.

**Evaluación online.** Se realiza sobre tráfico real: pruebas A/B, *shadow mode* (el modelo nuevo recibe el tráfico pero sus predicciones no se usan todavía), *bandit experiments* y seguimiento de métricas de negocio ligadas a las predicciones. La evaluación online cierra el círculo entre la métrica técnica y el impacto real: un modelo puede tener un F1-score alto y, aun así, no mejorar la tasa de conversión porque el error que comete es precisamente el que más importa en el contexto del negocio.

A lo largo de esta unidad desarrollaremos los instrumentos matemáticos y computacionales de la evaluación offline, con atención explícita a las decisiones que hay que tomar cuando los datos están desbalanceados, cuando los errores tienen costes asimétricos o cuando queremos comparar estadísticamente dos clasificadores.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Seleccionar la métrica de evaluación adecuada en función del tipo de problema (clasificación binaria, multiclase, regresión, clustering, generación de texto) y del contexto de negocio.
2. Calcular e interpretar accuracy, precisión, recall, F1-score, AUC-ROC, AUC-PR, MCC y Cohen's Kappa con scikit-learn.
3. Construir e interpretar matrices de confusión y realizar análisis cualitativos de los errores.
4. Implementar y leer curvas de aprendizaje para diagnosticar underfitting y overfitting.
5. Enunciar el bias-variance tradeoff de forma matemática y relacionarlo con las curvas de aprendizaje.
6. Aplicar el test de McNemar y el bootstrap para comparar clasificadores con rigor estadístico.
7. Describir las métricas más habituales en evaluación de modelos generativos (BLEU, ROUGE, BERTScore) y sus limitaciones.

---

## 3. Métricas para clasificación

### 3.1 Accuracy y sus limitaciones

La *accuracy* es la fracción de predicciones correctas sobre el total:

$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$

Es intuitiva y fácil de comunicar, pero engaña cuando las clases están desbalanceadas. Si el 95 % de las muestras pertenecen a la clase negativa, un clasificador que siempre predice negativo alcanza 95 % de accuracy sin aprender nada útil. En esos escenarios hay que mirar métricas que ponderen los errores por clase.

### 3.2 Precisión, Recall y F1-score

Definimos las cuatro casillas de la tabla de confusión binaria:

- **TP** (*True Positives*): predicho positivo, verdaderamente positivo.
- **TN** (*True Negatives*): predicho negativo, verdaderamente negativo.
- **FP** (*False Positives*, error tipo I): predicho positivo, verdaderamente negativo.
- **FN** (*False Negatives*, error tipo II): predicho negativo, verdaderamente positivo.

$$\text{Precisión} = \frac{TP}{TP + FP} \qquad \text{Recall} = \frac{TP}{TP + FN}$$

La **precisión** responde a: de todo lo que el modelo predijo como positivo, ¿qué fracción lo era realmente? El **recall** (también llamado *sensibilidad* o *tasa de verdaderos positivos*) responde a: de todos los positivos reales, ¿qué fracción detectó el modelo?

Existe una compensación (*tradeoff*) inherente entre ambas. Bajar el umbral de decisión aumenta el recall a costa de la precisión; subirlo hace lo contrario. El **F1-score** es la media armónica que equilibra ambas:

$$F_1 = 2 \cdot \frac{\text{Precisión} \cdot \text{Recall}}{\text{Precisión} + \text{Recall}}$$

La media armónica penaliza las situaciones en que una de las dos métricas es muy baja. Si precisión = 1.0 y recall = 0.0, F1 = 0, no 0.5.

La versión generalizada $F_\beta$ permite ponderar recall sobre precisión cuando detectar los positivos importa más que la tasa de falsas alarmas:

$$F_\beta = (1 + \beta^2) \cdot \frac{\text{Precisión} \cdot \text{Recall}}{\beta^2 \cdot \text{Precisión} + \text{Recall}}$$

Con $\beta = 2$ se da el doble de peso al recall; con $\beta = 0.5$, el doble de peso a la precisión.

En clasificación **multiclase**, scikit-learn ofrece tres estrategias de agregación:

| Estrategia | Descripción | Cuándo usarla |
|---|---|---|
| `macro` | Media simple por clase | Cuando todas las clases importan por igual |
| `weighted` | Media ponderada por soporte | Cuando el soporte desigual es relevante |
| `micro` | Suma de TP/FP/FN globalmente | Equivalente a accuracy en multiclase balanceada |

```python
from sklearn.metrics import classification_report, f1_score
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=1000, n_classes=3, n_informative=5,
                            weights=[0.6, 0.3, 0.1], random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(random_state=42).fit(X_train, y_train)
y_pred = clf.predict(X_test)

print(classification_report(y_test, y_pred, target_names=["Clase 0", "Clase 1", "Clase 2"]))
print("F1 macro:", f1_score(y_test, y_pred, average="macro"))
print("F1 weighted:", f1_score(y_test, y_pred, average="weighted"))
```

### 3.3 Curva ROC y AUC-ROC

La curva ROC (*Receiver Operating Characteristic*) representa la tasa de verdaderos positivos (TPR = recall) frente a la tasa de falsos positivos (FPR) para todos los umbrales posibles:

$$TPR = \frac{TP}{TP + FN} \qquad FPR = \frac{FP}{FP + TN}$$

El área bajo esta curva (AUC-ROC) mide la probabilidad de que el modelo asigne una puntuación más alta a un ejemplo positivo aleatorio que a uno negativo aleatorio. Un clasificador perfecto tiene AUC = 1.0; uno aleatorio, AUC = 0.5.

La curva ROC es robusta ante el desbalance de clases en el sentido de que TN y FP se normalizan por la clase negativa. Sin embargo, cuando la clase positiva es muy minoritaria, puede dar una imagen demasiado optimista: un modelo puede tener AUC-ROC alto y un recall bajo en la clase positiva.

```python
from sklearn.metrics import roc_curve, roc_auc_score
import matplotlib.pyplot as plt

y_scores = clf.predict_proba(X_test)[:, 1]  # probabilidad clase 1 (problema binario)
fpr, tpr, thresholds = roc_curve(y_test, y_scores, pos_label=1)
auc = roc_auc_score(y_test, y_scores)

plt.figure(figsize=(6, 5))
plt.plot(fpr, tpr, label=f"AUC = {auc:.3f}")
plt.plot([0, 1], [0, 1], "k--", label="Aleatorio")
plt.xlabel("FPR"); plt.ylabel("TPR"); plt.title("Curva ROC")
plt.legend(); plt.tight_layout(); plt.show()
```

### 3.4 Curva Precision-Recall y Average Precision

Para problemas con fuerte desbalance, la curva Precision-Recall (PR) es más informativa que la ROC. Representa precisión frente a recall en todos los umbrales. El **Average Precision (AP)** es el área bajo esta curva, calculada como media ponderada de las precisiones en cada umbral:

$$AP = \sum_n (R_n - R_{n-1}) \cdot P_n$$

Un AP alto garantiza que el modelo identifica bien los positivos y que sus predicciones positivas son fiables. En recuperación de información, AP es la métrica estándar.

```python
from sklearn.metrics import precision_recall_curve, average_precision_score

precision, recall, _ = precision_recall_curve(y_test, y_scores, pos_label=1)
ap = average_precision_score(y_test, y_scores)
print(f"Average Precision: {ap:.3f}")
```

### 3.5 Matthews Correlation Coefficient (MCC)

El MCC considera las cuatro casillas de la matriz de confusión y produce un coeficiente entre −1 y +1 que es robusto ante el desbalance:

$$MCC = \frac{TP \cdot TN - FP \cdot FN}{\sqrt{(TP+FP)(TP+FN)(TN+FP)(TN+FN)}}$$

MCC = +1 indica predicción perfecta; MCC = 0, predicción aleatoria; MCC = −1, predicción perfectamente invertida. Es considerado por muchos investigadores la métrica más informativa para clasificación binaria desbalanceada cuando se quiere un único número resumen.

```python
from sklearn.metrics import matthews_corrcoef
print("MCC:", matthews_corrcoef(y_test, y_pred))
```

### 3.6 Cohen's Kappa

El Kappa de Cohen mide el acuerdo entre dos clasificadores (o entre el modelo y el etiquetador humano) corrigiendo el acuerdo esperado por azar:

$$\kappa = \frac{p_o - p_e}{1 - p_e}$$

donde $p_o$ es el acuerdo observado y $p_e$ el acuerdo esperado por azar. $\kappa = 1$ indica acuerdo perfecto; $\kappa = 0$, acuerdo equivalente al azar; valores negativos, menos acuerdo que el azar.

```python
from sklearn.metrics import cohen_kappa_score
print("Cohen's Kappa:", cohen_kappa_score(y_test, y_pred))
```

### 3.7 Guía de selección de métricas

| Escenario | Métrica recomendada | Justificación |
|---|---|---|
| Clases balanceadas, coste simétrico | Accuracy, F1 macro | Simple, interpretable |
| Desbalance moderado | F1 weighted, AUC-ROC | Pondera por soporte |
| Desbalance severo | MCC, AUC-PR, F1 de la clase minoritaria | ROC puede ser engañosa |
| Alto coste de FP (spam, fraude con bloqueo) | Precisión, F0.5 | Minimizar falsas alarmas |
| Alto coste de FN (diagnóstico médico) | Recall, F2 | Minimizar fallos de detección |
| Comparar con anotador humano | Cohen's Kappa | Corrige acuerdo por azar |

---

## 4. Métricas para regresión

### 4.1 MAE, MSE, RMSE

El **Error Absoluto Medio (MAE)** es la media de los errores absolutos:

$$MAE = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|$$

Es robusto a valores atípicos porque no eleva el error al cuadrado. Tiene la misma unidad que la variable objetivo, lo que facilita su interpretación.

El **Error Cuadrático Medio (MSE)** penaliza los errores grandes de forma cuadrática:

$$MSE = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2$$

Su raíz cuadrada, el **RMSE**, devuelve las unidades originales y es la métrica más popular en regresión porque es diferenciable (relevante para optimización) y penaliza los outliers:

$$RMSE = \sqrt{MSE}$$

### 4.2 R² (coeficiente de determinación)

$$R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$$

$R^2$ compara el modelo con el modelo base que siempre predice la media. Un $R^2 = 0.85$ significa que el modelo explica el 85 % de la varianza de los datos. Puede ser negativo si el modelo es peor que la media.

### 4.3 MAPE y SMAPE

El **Error Porcentual Absoluto Medio (MAPE)** expresa el error en porcentaje:

$$MAPE = \frac{100\%}{n} \sum_{i=1}^{n} \left|\frac{y_i - \hat{y}_i}{y_i}\right|$$

Es intuitivo para audiencias no técnicas pero no está definido cuando $y_i = 0$ y es asimétrico (errores por debajo penalizan más que errores equivalentes por arriba). El **SMAPE** (*Symmetric MAPE*) corrige parcialmente la asimetría:

$$SMAPE = \frac{100\%}{n} \sum_{i=1}^{n} \frac{|y_i - \hat{y}_i|}{(|y_i| + |\hat{y}_i|)/2}$$

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

y_true = np.array([3.0, -0.5, 2.0, 7.0])
y_pred = np.array([2.5, 0.0, 2.0, 8.0])

print(f"MAE:  {mean_absolute_error(y_true, y_pred):.4f}")
print(f"MSE:  {mean_squared_error(y_true, y_pred):.4f}")
print(f"RMSE: {np.sqrt(mean_squared_error(y_true, y_pred)):.4f}")
print(f"R²:   {r2_score(y_true, y_pred):.4f}")
```

### 4.4 Análisis de residuos

Las métricas globales condensan información; el análisis de residuos la expande. Los residuos $e_i = y_i - \hat{y}_i$ deben cumplir, bajo los supuestos del modelo lineal:

- **Media cero:** no hay sesgo sistemático.
- **Homocedasticidad:** la varianza de los residuos no depende del valor predicho.
- **Normalidad:** relevante para intervalos de confianza.
- **Independencia:** no hay autocorrelación (especialmente en series temporales).

Un gráfico residuos vs. valores predichos que muestra un patrón en abanico (*funnel shape*) indica heterocedasticidad. Un patrón curvo indica que el modelo no ha capturado la no linealidad. Un Q-Q plot permite verificar la normalidad visualmente.

---

## 5. Métricas para clustering

### 5.1 Evaluación interna

Las métricas internas no requieren etiquetas verdaderas y miden la calidad de la agrupación según la estructura interna de los datos.

El **índice de silhouette** para una muestra $i$ se define como:

$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

donde $a(i)$ es la distancia media de $i$ a los demás puntos de su clúster y $b(i)$ es la distancia media mínima de $i$ al clúster más cercano que no contiene a $i$. El índice varía entre −1 y +1. Valores cercanos a +1 indican clusters compactos y bien separados; valores negativos indican que el punto podría pertenecer a otro cluster.

El **índice de Davies-Bouldin (DBI)** mide la relación entre la dispersión intra-cluster y la distancia inter-cluster. Un valor más bajo es mejor. El **índice de Calinski-Harabasz (CHI)** (también llamado *Variance Ratio Criterion*) mide la relación entre la dispersión entre clusters y la dispersión interna; un valor más alto es mejor.

```python
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

X, _ = make_blobs(n_samples=500, centers=4, random_state=42)
labels = KMeans(n_clusters=4, random_state=42).fit_predict(X)

print(f"Silhouette:        {silhouette_score(X, labels):.4f}")
print(f"Davies-Bouldin:    {davies_bouldin_score(X, labels):.4f}")
print(f"Calinski-Harabasz: {calinski_harabasz_score(X, labels):.4f}")
```

### 5.2 Evaluación externa

Cuando se dispone de etiquetas verdaderas (por ejemplo, en evaluación sobre datasets *benchmark*), se pueden usar métricas externas.

El **Adjusted Rand Index (ARI)** mide el acuerdo entre la agrupación predicha y la referencia corrigiendo el acuerdo por azar. El **Normalized Mutual Information (NMI)** mide la información compartida entre ambas agrupaciones, normalizada para que varíe entre 0 y 1.

| Métrica | Requiere etiquetas | Rango | Mejor valor |
|---|---|---|---|
| Silhouette | No | [−1, 1] | Máximo |
| Davies-Bouldin | No | [0, ∞) | Mínimo |
| Calinski-Harabasz | No | [0, ∞) | Máximo |
| ARI | Sí | [−1, 1] | 1 |
| NMI | Sí | [0, 1] | 1 |

---

## 6. Matrices de confusión y análisis de errores

### 6.1 Construcción e interpretación

La matriz de confusión es la representación tabular del rendimiento de un clasificador: las filas representan las clases reales y las columnas las clases predichas (o viceversa, según la convención). Para clasificación binaria:

|  | Predicho Positivo | Predicho Negativo |
|---|---|---|
| **Real Positivo** | TP | FN |
| **Real Negativo** | FP | TN |

Para clasificación multiclase, la diagonal contiene los aciertos y los elementos fuera de la diagonal, los errores. La célula $(i, j)$ indica cuántas veces el modelo predijo la clase $j$ cuando la clase real era $i$.

```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import seaborn as sns
import matplotlib.pyplot as plt

cm = confusion_matrix(y_test, y_pred)

fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["Pred 0", "Pred 1", "Pred 2"],
            yticklabels=["Real 0", "Real 1", "Real 2"], ax=ax)
ax.set_xlabel("Predicho"); ax.set_ylabel("Real")
ax.set_title("Matriz de confusión")
plt.tight_layout(); plt.show()
```

### 6.2 Análisis cualitativo de errores

La matriz de confusión numérica dice *cuánto* falla el modelo; el análisis cualitativo dice *por qué*. Un proceso sistemático incluye:

1. **Identificar los pares de confusión más frecuentes.** Si la clase "gato" se confunde a menudo con "perro" pero rara vez con "avión", el problema es de similitud visual en el espacio de características, no de calidad global del modelo.

2. **Examinar ejemplos individuales mal clasificados.** Revisar las imágenes, textos o registros que generaron errores revela si el error es ruidoso (etiqueta ambigua, dato corrupto) o sistemático (el modelo carece de una característica clave).

3. **Calcular el coste esperado.** En muchos contextos, FN y FP tienen costes distintos. Si fallar en detectar un tumor maligno (FN) tiene un coste 50 veces mayor que un falso positivo, el análisis de la matriz debe estar ponderado por estos costes, lo que lleva a la construcción de una **matriz de costes**.

4. **Comparar con la distribución de clases.** Un error del 20 % en una clase con 5 % de soporte es diferente de un error del 20 % en una clase con 60 % de soporte.

---

## 7. Curvas de aprendizaje y diagnóstico

### 7.1 Curvas de aprendizaje

Una curva de aprendizaje representa el error (o la métrica) de entrenamiento y de validación en función del tamaño del conjunto de entrenamiento. Se genera entrenando el mismo modelo con subconjuntos de datos de tamaño creciente y evaluando en un conjunto de validación fijo.

**Interpretación de los patrones:**

- **Underfitting (alto sesgo):** tanto el error de entrenamiento como el de validación son altos y convergen rápidamente. El modelo es demasiado simple para capturar la estructura de los datos. La solución no es añadir más datos, sino aumentar la complejidad del modelo o enriquecer las características.

- **Overfitting (alta varianza):** el error de entrenamiento es bajo pero el de validación es alto, y la brecha no cierra al aumentar el tamaño del conjunto de entrenamiento. El modelo ha memorizado los datos de entrenamiento. Las soluciones habituales son regularización, dropout, reducción de complejidad o recolección de más datos.

- **Ajuste correcto:** el error de entrenamiento y el de validación convergen a un valor bajo. Añadir más datos puede seguir mejorando, pero la ganancia marginal disminuye.

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
from sklearn.svm import SVC

train_sizes, train_scores, val_scores = learning_curve(
    SVC(kernel="rbf"), X, y,
    train_sizes=np.linspace(0.1, 1.0, 10),
    cv=5, scoring="f1_macro", n_jobs=-1
)

train_mean = train_scores.mean(axis=1)
val_mean   = val_scores.mean(axis=1)

plt.figure(figsize=(7, 5))
plt.plot(train_sizes, train_mean, "o-", label="Entrenamiento")
plt.plot(train_sizes, val_mean,   "o-", label="Validación")
plt.fill_between(train_sizes,
                 train_mean - train_scores.std(axis=1),
                 train_mean + train_scores.std(axis=1), alpha=0.15)
plt.fill_between(train_sizes,
                 val_mean - val_scores.std(axis=1),
                 val_mean + val_scores.std(axis=1), alpha=0.15)
plt.xlabel("Tamaño del conjunto de entrenamiento")
plt.ylabel("F1 macro"); plt.title("Curvas de aprendizaje")
plt.legend(); plt.tight_layout(); plt.show()
```

### 7.2 Bias-variance tradeoff

El error de generalización esperado de un modelo puede descomponerse matemáticamente en tres términos:

$$\mathbb{E}[(y - \hat{f}(x))^2] = \text{Bias}[\hat{f}(x)]^2 + \text{Var}[\hat{f}(x)] + \sigma^2$$

donde:

- $\text{Bias}[\hat{f}(x)] = \mathbb{E}[\hat{f}(x)] - f(x)$ mide cuánto se desvía en promedio la predicción del valor verdadero. Un sesgo alto implica que el modelo sistematicamente no captura la función subyacente.
- $\text{Var}[\hat{f}(x)] = \mathbb{E}[(\hat{f}(x) - \mathbb{E}[\hat{f}(x)])^2]$ mide la sensibilidad del modelo a las fluctuaciones en los datos de entrenamiento. Una varianza alta implica que pequeños cambios en los datos de entrenamiento producen modelos muy diferentes.
- $\sigma^2$ es el ruido irreducible, inherente a los datos.

La tensión entre sesgo y varianza es inherente: reducir el sesgo (aumentar la complejidad del modelo) tiende a aumentar la varianza y viceversa. El objetivo es encontrar el punto donde la suma sesgo² + varianza es mínima.

Esta formulación matemática explica directamente los patrones observados en las curvas de aprendizaje: underfitting = alto sesgo, overfitting = alta varianza.

### 7.3 Validation curves para hiperparámetros

Una *validation curve* muestra cómo varía el rendimiento de entrenamiento y validación en función de un único hiperparámetro, con todos los demás fijos. Es útil para diagnosticar si un hiperparámetro específico causa underfitting o overfitting.

```python
from sklearn.model_selection import validation_curve

param_range = [0.001, 0.01, 0.1, 1, 10, 100]
train_s, val_s = validation_curve(
    SVC(), X, y,
    param_name="C", param_range=param_range,
    cv=5, scoring="f1_macro"
)

plt.semilogx(param_range, train_s.mean(axis=1), label="Entrenamiento")
plt.semilogx(param_range, val_s.mean(axis=1),   label="Validación")
plt.xlabel("C (parámetro de regularización)"); plt.ylabel("F1 macro")
plt.title("Validation curve — SVM"); plt.legend(); plt.show()
```

---

## 8. Técnicas de evaluación estadística

La comparación informal de dos modelos —"el modelo A tiene 82 % y el B tiene 84 %, por tanto B es mejor"— ignora la variabilidad inherente a la partición de datos y al proceso de entrenamiento. Los métodos estadísticos permiten decidir con un nivel de confianza explícito.

### 8.1 Test de McNemar

El test de McNemar compara dos clasificadores evaluados sobre el mismo conjunto de prueba. Se construye una tabla de contingencia 2×2 a partir de los errores de cada modelo:

|  | Modelo B correcto | Modelo B incorrecto |
|---|---|---|
| **Modelo A correcto** | $n_{00}$ | $n_{01}$ |
| **Modelo A incorrecto** | $n_{10}$ | $n_{11}$ |

Solo los casos donde los modelos difieren ($n_{01}$ y $n_{10}$) son informativos. El estadístico de McNemar es:

$$\chi^2 = \frac{(|n_{01} - n_{10}| - 1)^2}{n_{01} + n_{10}}$$

bajo la hipótesis nula de que ambos modelos tienen la misma tasa de error. Se distribuye aproximadamente como $\chi^2$ con 1 grado de libertad.

```python
from statsmodels.stats.contingency_tables import mcnemar

# y_pred_a, y_pred_b: predicciones de dos modelos
# Construir tabla de contingencia
b_correct = (y_pred == y_test)   # booleano: modelo B acierta
a_correct = (y_pred == y_test)   # reemplazar con predicciones del modelo A

table = np.array([
    [(~a_correct & ~b_correct).sum(), (~a_correct & b_correct).sum()],
    [(a_correct & ~b_correct).sum(),  (a_correct & b_correct).sum()]
])
result = mcnemar(table, exact=True)
print(f"p-valor: {result.pvalue:.4f}")
```

### 8.2 Intervalos de confianza con bootstrap

El bootstrap estima la distribución de una estadística muestreando con reemplazo del conjunto de prueba. Para calcular un intervalo de confianza del 95 % para el F1-score:

```python
from sklearn.utils import resample

n_bootstrap = 1000
f1_scores = []
for _ in range(n_bootstrap):
    y_t_boot, y_p_boot = resample(y_test, y_pred, random_state=None)
    f1_scores.append(f1_score(y_t_boot, y_p_boot, average="macro"))

ci_lower = np.percentile(f1_scores, 2.5)
ci_upper = np.percentile(f1_scores, 97.5)
print(f"F1 macro IC 95%: [{ci_lower:.4f}, {ci_upper:.4f}]")
```

### 8.3 Corrected paired t-test (Nadeau-Bengio)

Cuando se comparan modelos mediante validación cruzada de $k$ pliegues, las estimaciones no son independientes (los conjuntos de entrenamiento comparten muestras). El *corrected paired t-test* de Nadeau y Bengio (2003) incorpora un factor de corrección $\frac{1}{k} + \frac{n_{test}}{n_{train}}$ al estimador de la varianza para evitar rechazar la hipótesis nula con demasiada frecuencia.

---

## 9. Evaluación de modelos de lenguaje y generativos

Los modelos generativos —traducción automática, resumen, descripción de imágenes— producen texto que no tiene una respuesta correcta única. Las métricas de clasificación no son aplicables directamente.

### 9.1 BLEU

El **Bilingual Evaluation Understudy (BLEU)** mide la precisión de n-gramas del texto generado frente a una o varias referencias, con una penalización por brevedad (*brevity penalty*):

$$BLEU = BP \cdot \exp\left(\sum_{n=1}^{N} w_n \log p_n\right)$$

donde $p_n$ es la precisión de n-gramas modificada y $BP$ penaliza las traducciones más cortas que la referencia. BLEU es rápido y reproducible, pero no captura semántica ni variedad léxica. Una paráfrasis correcta con diferente vocabulario recibe BLEU bajo.

### 9.2 ROUGE

**ROUGE** (*Recall-Oriented Understudy for Gisting Evaluation*) se orienta al recall y es estándar para evaluación de resúmenes. Las variantes principales son:

- **ROUGE-N:** recall de n-gramas entre el resumen generado y el de referencia.
- **ROUGE-L:** basado en la subsecuencia común más larga (LCS), capturando orden sin requerir coincidencias contiguas.

### 9.3 BERTScore

**BERTScore** (Zhang et al., 2020) supera las limitaciones de las métricas basadas en coincidencia exacta usando embeddings contextuales de BERT. Para cada token del texto generado, busca el token más similar en la referencia (y viceversa) en el espacio de representaciones:

$$F_{BERT} = \frac{2 \cdot P_{BERT} \cdot R_{BERT}}{P_{BERT} + R_{BERT}}$$

BERTScore correlaciona mejor con el juicio humano que BLEU o ROUGE, especialmente para variaciones parafrásticas.

### 9.4 Evaluación humana

Ninguna métrica automática reemplaza completamente la evaluación humana. Los protocolos habituales incluyen:

- **Rating absoluto:** anotadores puntúan cada salida en una escala Likert (1-5) según criterios como fluidez, coherencia y precisión factual.
- **Evaluación comparativa (preference):** se presentan pares de salidas y el anotador indica cuál prefiere. Reduce la variabilidad inter-anotador.
- **MOS (Mean Opinion Score):** estándar en síntesis de voz, adaptado a texto.

La evaluación humana es cara y lenta pero es el *gold standard* al que deben anclarse las métricas automáticas. Un buen protocolo de investigación reporta la correlación de Spearman o Pearson entre la métrica automática y el juicio humano para validar su uso.

---

## 10. Actividades prácticas propuestas

**Actividad 1. Análisis comparativo de métricas en datos desbalanceados.**  
El estudiante recibirá un dataset de detección de fraude (desbalance aproximado 1:50). Deberá entrenar un clasificador logístico y un Random Forest, calcular accuracy, F1 macro, F1 de la clase minoritaria, MCC y AUC-ROC para ambos, y redactar un párrafo argumentando qué métrica es más informativa en este contexto y por qué. La actividad explora la trampa de la accuracy y desarrolla el criterio para seleccionar métricas según el problema.

**Actividad 2. Diagnóstico visual con curvas de aprendizaje.**  
El estudiante entrenará una red neuronal de dos capas y un árbol de decisión sin podar sobre el mismo dataset. Generará las curvas de aprendizaje de ambos modelos, identificará cuál sufre underfitting y cuál overfitting, y propondrá, razonado matemáticamente, al menos dos estrategias para mejorar el modelo con mayor varianza.

**Actividad 3. Comparación estadística de clasificadores.**  
Dados los vectores de predicción de tres clasificadores (proporcionados en un archivo CSV), el estudiante aplicará el test de McNemar para todas las combinaciones por pares, aplicará la corrección de Bonferroni para comparaciones múltiples, calculará intervalos de confianza bootstrap del F1-score y concluirá qué pares muestran diferencias estadísticamente significativas (α = 0.05).

**Actividad 4. Evaluación de un modelo generativo.**  
El estudiante usará la biblioteca `evaluate` de Hugging Face para calcular BLEU, ROUGE-L y BERTScore sobre un conjunto de resúmenes generados por un modelo de lenguaje (proporcionado). Comparará los resultados con una valoración cualitativa de cinco ejemplos elegidos al azar y discutirá si las métricas automáticas capturan adecuadamente la calidad percibida.

---

## 11. Referencias

1. **Pedregosa, F. et al. (2011).** Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830. Documentación oficial: https://scikit-learn.org/stable/modules/model_evaluation.html

2. **Hastie, T., Tibshirani, R. y Friedman, J. (2009).** *The Elements of Statistical Learning: Data Mining, Inference, and Prediction* (2.ª ed.). Springer. Disponible en: https://hastie.su.domains/ElemStatLearn/

3. **Bishop, C. M. (2006).** *Pattern Recognition and Machine Learning*. Springer. Capítulos 1 (Introduction) y 3 (Linear Models for Regression).

4. **Matthews, B. W. (1975).** Comparison of the predicted and observed secondary structure of T4 phage lysozyme. *Biochimica et Biophysica Acta*, 405(2), 442–451. https://doi.org/10.1016/0005-2795(75)90109-9 [Paper original del MCC]

5. **McNemar, Q. (1947).** Note on the sampling error of the difference between correlated proportions or percentages. *Psychometrika*, 12(2), 153–157. https://doi.org/10.1007/BF02295996

6. **Nadeau, C. y Bengio, Y. (2003).** Inference for the Generalization Error. *Machine Learning*, 52(3), 239–281. https://doi.org/10.1023/A:1024068626366

7. **Zhang, T. et al. (2020).** BERTScore: Evaluating Text Generation with BERT. *ICLR 2020*. https://arxiv.org/abs/1904.09675

8. **Papineni, K. et al. (2002).** BLEU: a Method for Automatic Evaluation of Machine Translation. *ACL 2002*, 311–318. https://aclanthology.org/P02-1040/

9. **Lin, C.-Y. (2004).** ROUGE: A Package for Automatic Evaluation of Summaries. *ACL Workshop on Text Summarization Branches Out*, 74–81. https://aclanthology.org/W04-1013/

10. **Powers, D. M. W. (2011).** Evaluation: From Precision, Recall and F-Measure to ROC, Informedness, Markedness & Correlation. *Journal of Machine Learning Technologies*, 2(1), 37–63. https://arxiv.org/abs/2010.16061
