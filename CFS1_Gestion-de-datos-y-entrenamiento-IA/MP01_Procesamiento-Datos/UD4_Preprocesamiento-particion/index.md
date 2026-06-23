---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD4 · Preprocesamiento y partición de datos | MP01 · Procesamiento de datos para IA'
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

# UD4 · Preprocesamiento y partición de datos

**MP01 · Procesamiento de datos para IA**
CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de aprendizaje

Al finalizar esta unidad el alumno será capaz de:

- Seleccionar atributos relevantes según el diseño del modelo y los resultados del EDA
- Aplicar técnicas de depuración: imputación, eliminación de errores, deduplicación y corrección de formatos
- Realizar transformaciones: normalización, reescalado, codificación de variables y balanceo de clases
- Dividir el conjunto en particiones de entrenamiento, validación y test sin contaminación entre ellas
- Aplicar estrategias de muestreo adecuadas al tipo de datos (aleatorio, estratificado, temporal, por grupos)
- Enriquecer el conjunto con variables derivadas, fuentes externas o datos sintéticos documentados
- Configurar pipelines que minimicen el consumo computacional y las emisiones de CO₂

---

## El pipeline de preprocesamiento en el contexto del ciclo IA

```
EDA y verificación    Preprocesamiento                    Modelado
de calidad (UD2-3) →  (esta UD) →                      → y evaluación
                      │
                      ├── Selección de atributos
                      ├── Depuración
                      │   ├── Imputación de nulos
                      │   ├── Corrección de errores
                      │   └── Deduplicación
                      ├── Transformación
                      │   ├── Escalado / normalización
                      │   ├── Codificación categóricas
                      │   ├── Balanceo de clases
                      │   └── Reducción de dimensionalidad
                      ├── Enriquecimiento
                      └── Partición (train / val / test)
```

---

## Selección de atributos: por qué no usar todas las variables

### El principio de parsimonia en IA

Usar más variables no siempre mejora el modelo. Puede:
- Introducir ruido que dificulta el aprendizaje
- Aumentar el coste computacional y la huella de CO₂
- Producir sobreajuste (overfitting)
- Incorporar variables que no estarán disponibles en producción

| Método de selección | Tipo | Descripción |
|---|---|---|
| **Correlación con target** | Filtro | Elimina variables con correlación < umbral |
| **Varianza** | Filtro | Elimina variables casi constantes |
| **SelectKBest (chi², F)** | Filtro | Selecciona las K variables más informativas |
| **RFE** (Recursive Feature Elimination) | Wrapper | Eliminación recursiva con modelo base |
| **L1 (Lasso)** | Embebido | Penalización que fuerza coeficientes a cero |
| **Importancia de árbol** | Embebido | Gini impurity o permutation importance |

---

## Selección de atributos: implementación

```python
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

X = df.drop("target", axis=1)
y = df["target"]

# Método 1: SelectKBest — seleccionar las 10 más informativas
selector_f = SelectKBest(score_func=f_classif, k=10)
X_kbest = selector_f.fit_transform(X, y)
columnas_seleccionadas = X.columns[selector_f.get_support()]
print("SelectKBest:", list(columnas_seleccionadas))

# Método 2: importancia de Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X, y)
importancias = pd.Series(rf.feature_importances_, index=X.columns)
top10 = importancias.nlargest(10)
print("\nTop 10 por importancia RF:")
print(top10)
```

---

## Depuración: imputación de valores ausentes

### Estrategias de imputación según el contexto

| Estrategia | Cuándo usar | Riesgo |
|---|---|---|
| **Eliminar fila** | Nulos aleatorios, dataset grande | Pérdida de datos |
| **Eliminar columna** | >60% nulos, variable no crítica | Pérdida de información |
| **Media** | Variables numéricas, distribución simétrica | Reduce varianza, sensible a outliers |
| **Mediana** | Variables numéricas, con outliers o asimetría | Más robusta que la media |
| **Moda** | Variables categóricas | Puede sobre-representar la clase mayoritaria |
| **Imputación por KNN** | Correlación entre variables | Costosa computacionalmente |
| **Imputación iterativa (MICE)** | MAR con múltiples variables relacionadas | Complejidad alta |
| **Flag + imputación** | MNAR, ausencia informativa | Dobla el espacio de variables |

---

## Depuración: imputación con Scikit-learn

```python
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.pipeline import Pipeline
import numpy as np

X = df.drop("target", axis=1)

# Separar columnas por tipo
num_cols = X.select_dtypes(include="number").columns.tolist()
cat_cols = X.select_dtypes(include="object").columns.tolist()

# Imputadores por tipo
imputer_num = SimpleImputer(strategy="median")
imputer_cat = SimpleImputer(strategy="most_frequent")

X[num_cols] = imputer_num.fit_transform(X[num_cols])
X[cat_cols] = imputer_cat.fit_transform(X[cat_cols])

# Verificación post-imputación
assert X.isnull().sum().sum() == 0, "Quedan nulos tras la imputación"
print("Imputación completada sin nulos residuales")

# Imputación KNN (más precisa, más lenta)
knn_imputer = KNNImputer(n_neighbors=5, weights="distance")
X_knn = knn_imputer.fit_transform(X[num_cols])
```

---

## Normalización y reescalado

### Por qué escalar las variables numéricas

Los modelos basados en distancias (KNN, SVM, redes neuronales) son sensibles a la escala de las variables. Una variable con rango [0, 1.000.000] domina sobre una con rango [0, 1].

| Transformación | Fórmula | Resultado | Cuándo usar |
|---|---|---|---|
| **MinMaxScaler** | (x - min) / (max - min) | [0, 1] | Sin outliers extremos |
| **StandardScaler** | (x - media) / std | Media=0, Std=1 | Con distribución aproximadamente normal |
| **RobustScaler** | (x - mediana) / IQR | Centrado robusto | Con outliers que no se pueden eliminar |
| **Log transform** | log(x + 1) | Reduce asimetría | Variables con distribución muy sesgada |
| **PowerTransformer** | Box-Cox / Yeo-Johnson | Aproxima normalidad | Variables muy no normales |

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X[num_cols])
# IMPORTANTE: fit() SOLO sobre el conjunto de entrenamiento
```

---

## Codificación de variables categóricas

| Método | Descripción | Cuándo usar | Variables creadas |
|---|---|---|---|
| **One-Hot Encoding** | Columna binaria por categoría | Nominales, pocas categorías | N-1 columnas |
| **Label Encoding** | Entero por categoría | Ordinales o árboles de decisión | 1 columna |
| **Target Encoding** | Media del target por categoría | Muchas categorías, riesgo de leakage | 1 columna |
| **Binary Encoding** | Bits del código de la categoría | Muchas categorías, alta cardinalidad | log2(N) columnas |
| **Frequency Encoding** | Frecuencia de aparición | Alta cardinalidad, relación con freq. | 1 columna |

```python
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
import pandas as pd

# One-Hot para nominales
ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
X_encoded = ohe.fit_transform(X[["ciudad", "tipo_contrato"]])
cols_ohe = ohe.get_feature_names_out(["ciudad", "tipo_contrato"])
df_ohe = pd.DataFrame(X_encoded, columns=cols_ohe)
```

---

## Balanceo de clases

### Técnicas de rebalanceo para conjuntos desbalanceados

```python
from imblearn.over_sampling import SMOTE, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler
from imblearn.combine import SMOTETomek

X = df.drop("target", axis=1)
y = df["target"]

print(f"Distribución original: {y.value_counts().to_dict()}")

# Oversampling sintético con SMOTE
smote = SMOTE(sampling_strategy="auto", random_state=42, k_neighbors=5)
X_sm, y_sm = smote.fit_resample(X, y)
print(f"Tras SMOTE: {pd.Series(y_sm).value_counts().to_dict()}")

# Combinación SMOTE + eliminación con Tomek Links
smt = SMOTETomek(random_state=42)
X_smt, y_smt = smt.fit_resample(X, y)
print(f"Tras SMOTETomek: {pd.Series(y_smt).value_counts().to_dict()}")
```

> SMOTE genera muestras sintéticas de la clase minoritaria interpolando entre vecinos. Aplicar SOLO sobre el conjunto de entrenamiento, nunca sobre test.

---

## Reducción de dimensionalidad

### Cuándo y cómo reducir el número de variables

**Contextos donde la reducción es necesaria:**
- Más variables que observaciones (p >> n): riesgo de sobreajuste severo
- Variables muy correladas entre sí: redundancia que no aporta información nueva
- Visualización del conjunto: proyección a 2D o 3D para inspección
- Reducción del coste computacional en modelos costosos

| Técnica | Tipo | Supervisada | Descripción |
|---|---|---|---|
| **PCA** | Lineal | No | Componentes de máxima varianza |
| **t-SNE** | No lineal | No | Visualización 2D/3D preservando vecindades locales |
| **UMAP** | No lineal | Opcional | Más rápido que t-SNE, preserva estructura global |
| **LDA** | Lineal | Si | Maximiza separación entre clases |
| **Autoencoder** | Red neuronal | No | Representación latente aprendida |

---

## PCA: implementación y decisión de componentes

```python
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import numpy as np

# Ajustar PCA sobre datos escalados
pca = PCA()
pca.fit(X_scaled)

# Varianza explicada acumulada
varianza_acum = np.cumsum(pca.explained_variance_ratio_)

# Regla del codo: número de componentes para el 95% de varianza
n_componentes_95 = np.argmax(varianza_acum >= 0.95) + 1
print(f"Componentes para 95% de varianza: {n_componentes_95}")

# Transformación final
pca_final = PCA(n_components=n_componentes_95)
X_pca = pca_final.fit_transform(X_scaled)
print(f"Dimensiones originales: {X_scaled.shape}")
print(f"Dimensiones tras PCA: {X_pca.shape}")
```

---

## Partición del conjunto: fundamentos

### Por qué dividir en tres conjuntos

```
CONJUNTO COMPLETO
      │
      ├── ENTRENAMIENTO (70-80%)
      │   El modelo aprende: ajusta parámetros
      │
      ├── VALIDACION (10-15%)
      │   Selección del modelo: ajuste de hiperparámetros
      │   Evita que el test "contamine" la selección
      │
      └── TEST (10-20%)
          Evaluación final imparcial
          Solo se usa UNA VEZ al final
          No se toca hasta que el modelo está listo
```

> El conjunto de test es sagrado. Usarlo repetidamente para decisiones de diseño convierte implícitamente el test en un conjunto de validación, invalidando la evaluación.

---

## Estrategias de partición

```python
from sklearn.model_selection import train_test_split

X = df.drop("target", axis=1)
y = df["target"]

# 1. Muestreo aleatorio simple
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 2. Muestreo estratificado (preserva distribución de clases)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# División train/val/test en dos pasos
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42
)
print(f"Train: {len(X_train):,} | Val: {len(X_val):,} | Test: {len(X_test):,}")
```

---

## Partición temporal y por grupos

### Cuándo el muestreo aleatorio no es válido

```python
# Partición temporal: para series temporales
# NO aleatorizar — respetar el orden cronológico
df_sorted = df.sort_values("fecha")
n = len(df_sorted)

X_train = df_sorted.iloc[:int(n*0.7)]
X_val   = df_sorted.iloc[int(n*0.7):int(n*0.85)]
X_test  = df_sorted.iloc[int(n*0.85):]

# Partición por grupos: evitar fuga entre registros del mismo sujeto
# (ej: múltiples visitas del mismo paciente no deben estar en train y test)
from sklearn.model_selection import GroupShuffleSplit

gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
grupos = df["id_paciente"]  # variable de grupo
train_idx, test_idx = next(gss.split(X, y, groups=grupos))

X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

# Verificar que no hay solapamiento de grupos
assert not set(grupos.iloc[train_idx]) & set(grupos.iloc[test_idx])
```

---

## Prevención de contaminación entre particiones

### Los errores más frecuentes que invalidan la evaluación

| Error | Descripción | Consecuencia |
|---|---|---|
| **Data leakage de transformaciones** | Scaler / imputer ajustado sobre train+test | Las métricas de test son optimistas |
| **SMOTE antes de dividir** | Datos sintéticos mezclados entre particiones | Test contaminado con interpolaciones de train |
| **Duplicados entre particiones** | El mismo registro en train y test | Sobreestimación del rendimiento |
| **Información futura en train** | Variables calculadas con datos del futuro | El modelo no generalizará |

```python
# CORRECTO: el scaler aprende SOLO de train, transforma val y test
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)   # fit + transform en train
X_val_sc   = scaler.transform(X_val)          # solo transform
X_test_sc  = scaler.transform(X_test)         # solo transform

# INCORRECTO: scaler sobre el dataset completo antes de dividir
# X_scaled = scaler.fit_transform(X)  ← NUNCA HACER ESTO
```

---

## El Pipeline de Scikit-learn: buenas prácticas

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingClassifier

# El Pipeline garantiza que no hay data leakage
# Todo se ajusta con fit() sobre train y se aplica con transform() a val/test
pipeline = Pipeline([
    ("imputer",    SimpleImputer(strategy="median")),
    ("scaler",     StandardScaler()),
    ("classifier", GradientBoostingClassifier(n_estimators=100, random_state=42))
])

# Entrenamiento: fit solo sobre train
pipeline.fit(X_train, y_train)

# Evaluación: transform + predict sin reajuste
score_val  = pipeline.score(X_val, y_val)
score_test = pipeline.score(X_test, y_test)

print(f"Validación: {score_val:.4f}")
print(f"Test: {score_test:.4f}")
```

---

## Enriquecimiento del conjunto

### Fuentes de nuevas variables

| Tipo de enriquecimiento | Descripción | Ejemplo |
|---|---|---|
| **Variables derivadas** | Calculadas a partir de las existentes | Ratio deuda/ingresos, edad desde fecha nacimiento |
| **Agregaciones temporales** | Estadísticos sobre ventanas de tiempo | Media de ventas últimos 30 días |
| **Fuentes externas** | Datos de terceros que aportan contexto | IPC, temperatura media, datos demográficos por CP |
| **Datos sintéticos** | Generados algorítmicamente | Aumentación de imágenes, SMOTE, GANs |
| **Embeddings** | Representaciones densas de texto/imágenes | Sentence embeddings de descripciones de producto |

> Cada fuente de enriquecimiento debe documentarse en el linaje de datos. Las variables derivadas deben reproducirse con la misma fórmula en producción.

---

## Sostenibilidad en el preprocesamiento

### Reducir la huella computacional del pipeline

```python
# 1. Eliminar columnas no útiles antes de cargar en memoria
columnas_utiles = ["id", "edad", "salario", "target"]
df = pd.read_parquet("dataset.parquet", columns=columnas_utiles)

# 2. Usar tipos de dato eficientes
df["edad"] = df["edad"].astype("int8")           # rango -128/127
df["salario"] = df["salario"].astype("float32")  # 32 bits vs 64 bits
df["categoria"] = df["categoria"].astype("category")  # ahorra memoria en categóricas

print("Memoria antes de optimizar: 1.2 GB")
print(f"Memoria tras optimizar: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")

# 3. Procesar en chunks si el dataset no cabe en RAM
for chunk in pd.read_csv("datos_grandes.csv", chunksize=100_000):
    chunk_procesado = pipeline.transform(chunk)
    # guardar chunk procesado
```

**Principio DNSH:** las decisiones de selección de atributos y filtrado de registros no solo mejoran el modelo; reducen los ciclos de CPU y las emisiones de CO₂ en el entrenamiento.

---

## Actividad práctica — UD4

### Pipeline completo de preprocesamiento

**Dataset:** `titanic.csv` (UCI / Kaggle — uso educativo libre)

**Tareas:**

1. Seleccionar atributos eliminando columnas con >50% de nulos y variables de identificación no predictivas
2. Imputar valores ausentes: mediana para numéricas, moda para categóricas. Justificar la elección del método
3. Aplicar One-Hot Encoding a la variable `Pclass` y `Sex`. Usar Label Encoding para `Embarked`
4. Escalar las variables numéricas con el método más adecuado (justificar)
5. Dividir en train (70%), validación (15%) y test (15%) con estratificación por la variable target `Survived`
6. Verificar que no hay nulos en ninguna partición y que los identificadores de pasajero no se solapan
7. Construir el pipeline completo con Scikit-learn y guardar las dimensiones finales de cada partición

---

## Puntos clave — UD4

- **El preprocesamiento sigue el diseño del modelo:** las decisiones de selección, transformación y partición no son arbitrarias; se derivan del EDA y de los requisitos del algoritmo
- **El scaler y el imputer aprenden SOLO de train:** ajustarlos sobre el conjunto completo introduce data leakage y produce métricas de evaluación irrealmente optimistas
- **La estrategia de partición depende del tipo de datos:** series temporales, registros de un mismo sujeto y datos con grupos requieren muestreo especializado
- **SMOTE y rebalanceo se aplican solo a train:** contaminar val y test con datos sintéticos invalida la evaluación
- **Los pipelines de Scikit-learn previenen errores:** encadenar transformaciones en un pipeline garantiza el orden correcto y evita fugas
- **La sostenibilidad es parte del diseño:** usar tipos de dato eficientes y filtrar en origen reduce el coste computacional y las emisiones

---

## Criterios de evaluación — UD4

- Selecciona los atributos del conjunto según el diseño del modelo y los resultados del análisis
- Depura y transforma el conjunto aplicando la técnica adecuada a cada tipo de variable
- Construye pipelines que aplican las transformaciones en el orden correcto sin data leakage
- Divide el conjunto en particiones de entrenamiento, validación y test con la estrategia de muestreo apropiada
- Verifica que no hay contaminación entre particiones (registros, datos sintéticos, transformaciones)
- Preserva la trazabilidad del enriquecimiento documentando las fuentes de nuevas variables
- Aplica criterios de eficiencia en la configuración del conjunto para minimizar el consumo computacional

---

<!-- _class: lead -->

[← Volver a MP01](../)


---

<!-- nav-slide -->

## Navegación

[← UD3 · Verificación de la calidad de…](../UD3_Verificacion-calidad/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD5 · Gestión, versionado y cumplim… →](../UD5_Gestion-versionado-normativa/)
