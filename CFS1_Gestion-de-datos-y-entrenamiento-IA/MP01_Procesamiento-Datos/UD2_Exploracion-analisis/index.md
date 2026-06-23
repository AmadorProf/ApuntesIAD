---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD2 · Exploración y análisis del conjunto de datos | MP01 · Procesamiento de datos para IA'
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

# UD2 · Exploración y análisis del conjunto de datos

**MP01 · Procesamiento de datos para IA**
CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de aprendizaje

Al finalizar esta unidad el alumno será capaz de:

- Componer conjuntos de datos a partir de fuentes diversas e identificar incompatibilidades
- Aplicar técnicas de análisis exploratorio (EDA) para caracterizar un conjunto de datos
- Documentar la estructura del conjunto: entidades, variables, tipos y volumetrías
- Evaluar la idoneidad de los datos frente al objetivo del modelo
- Detectar y registrar problemas iniciales de calidad: valores ausentes, inconsistencias, duplicidades
- Definir criterios de etiquetado o anotación adaptados al problema supervisado
- Usar las herramientas Python estándar del ecosistema de exploración de datos

---

## El EDA en el ciclo de vida de un proyecto de IA

```
Extracción        Exploración (EDA)         Preprocesamiento       Modelado
─────────         ─────────────────         ────────────────       ────────
Datos brutos  →  ¿Qué tenemos?         →   Limpiar y        →    Entrenar
de múltiples     ¿Son suficientes?          transformar            y evaluar
fuentes          ¿Son de calidad?           datos

                 ^^^^^^^^^^^^^^^
                 Esta es la UD2
                 No se puede saltar
```

> El EDA no es un paso opcional. Saltárselo lleva a modelos que aprenden patrones incorrectos, sesgos ocultos o directamente errores de datos que invalidan todo el trabajo posterior.

---

## Composición de conjuntos desde múltiples fuentes

### El problema de integrar fuentes heterogéneas

Cuando los datos provienen de más de una fuente, surgen incompatibilidades que hay que identificar antes de cualquier análisis:

| Tipo de incompatibilidad | Ejemplo concreto |
|---|---|
| Escalas distintas | Temperatura en ºC vs. ºF según el sensor |
| Zonas horarias diferentes | UTC en base de datos, hora local en CSV externo |
| Identificadores no alineados | `id_cliente` en sistema A vs. `customer_id` en sistema B |
| Granularidad temporal distinta | Lecturas cada minuto vs. resumen diario |
| Valores categóricos inconsistentes | "España" / "ES" / "ESP" / "Spain" para el mismo país |
| Esquemas en conflicto | Campo `nombre` texto libre vs. `apellido1 + apellido2` |

---

## Composición de conjuntos: ejemplo práctico

```python
import pandas as pd

# Fuente 1: base de datos interna
df_ventas = pd.read_parquet("ventas_2024.parquet")
# Fuente 2: fichero externo del proveedor
df_catalogo = pd.read_csv("catalogo_proveedor.csv", encoding="latin-1")

# Problema detectado: el campo de unión tiene nombres distintos
print(df_ventas.columns)    # ['id_producto', 'fecha', 'unidades']
print(df_catalogo.columns)  # ['product_code', 'nombre', 'categoria']

# Renombrado antes del join
df_catalogo = df_catalogo.rename(columns={"product_code": "id_producto"})

# Unión y detección de registros sin correspondencia
df_unido = df_ventas.merge(df_catalogo, on="id_producto", how="left")
sin_catalogo = df_unido[df_unido["nombre"].isna()]
print(f"Ventas sin producto en catálogo: {len(sin_catalogo):,}")
```

---

## Estructura del EDA: qué analizar y en qué orden

```
EDA — Secuencia recomendada
│
├── 1. Visión general
│   ├── Dimensiones (filas x columnas)
│   ├── Tipos de dato por columna
│   └── Muestra de registros representativos
│
├── 2. Variables individuales (análisis univariante)
│   ├── Numéricas: media, mediana, desv. estándar, percentiles, histograma
│   └── Categóricas: frecuencias, valores únicos, distribución de clases
│
├── 3. Relaciones entre variables (análisis bivariante y multivariante)
│   ├── Correlaciones (Pearson, Spearman, Kendall)
│   ├── Scatter plots, pair plots
│   └── Heatmaps de correlación
│
└── 4. Detección de anomalías
    ├── Valores atípicos (outliers)
    └── Patrones inesperados o imposibles
```

---

## Visión general del conjunto: primeras inspecciones

```python
import pandas as pd

df = pd.read_parquet("dataset_clinico.parquet")

# Dimensiones y tipos
print(f"Dimensiones: {df.shape[0]:,} filas × {df.shape[1]} columnas")
print("\nTipos de dato:")
print(df.dtypes)

# Resumen estadístico básico
print("\nEstadísticas numéricas:")
print(df.describe())

# Vista de registros
print("\nPrimeras filas:")
print(df.head(3))

# Valores nulos
print("\nNulos por columna:")
print(df.isnull().sum().sort_values(ascending=False))
```

> `df.describe()` en variables numéricas revela de inmediato valores imposibles (edad negativa, presión de 999999) que indican errores de codificación.

---

## Análisis univariante: variables numéricas

### Estadísticos descriptivos y su interpretación

| Estadístico | Qué revela |
|---|---|
| **Media** | Centro de la distribución (sensible a outliers) |
| **Mediana** | Centro robusto, resiste a valores extremos |
| **Desviación estándar** | Dispersión de los valores respecto a la media |
| **Percentiles (P25, P75)** | Rango intercuartílico, identifica la "zona normal" |
| **Mínimo / Máximo** | Detecta valores imposibles o extremos |
| **Asimetría (skewness)** | Distribución sesgada a la derecha o izquierda |
| **Curtosis (kurtosis)** | Colas pesadas, concentración en la media |

```python
# Análisis más completo que describe()
from scipy import stats
col = df["edad"]
print(f"Asimetría: {col.skew():.3f}")
print(f"Curtosis: {col.kurtosis():.3f}")
print(f"Percentiles: {col.quantile([.01,.25,.5,.75,.99]).to_dict()}")
```

---

## Análisis univariante: variables categóricas

```python
# Distribución de una variable categórica
col_cat = df["diagnostico"]

print(f"Valores únicos: {col_cat.nunique()}")
print(f"\nFrecuencias absolutas:")
print(col_cat.value_counts())

print(f"\nFrecuencias relativas (%):")
print((col_cat.value_counts(normalize=True) * 100).round(2))

# Detectar clases muy raras (posible problema de calidad o de etiquetado)
umbral_raro = 0.01   # menos del 1%
clases_raras = col_cat.value_counts(normalize=True)
clases_raras = clases_raras[clases_raras < umbral_raro]
print(f"\nClases con menos del 1% de presencia: {len(clases_raras)}")
print(clases_raras)
```

**Alerta en IA:** una clase con menos del 1% de presencia puede ser un error de etiquetado, datos mal capturados o una clase minoritaria real que necesitará tratamiento especial.

---

## Análisis bivariante: correlaciones

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Matriz de correlación de Pearson (variables numéricas)
corr_matrix = df.select_dtypes(include="number").corr()

# Visualización como heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(
    corr_matrix,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
    square=True
)
plt.title("Matriz de correlación — Dataset clínico")
plt.tight_layout()
plt.savefig("correlacion_heatmap.png", dpi=150)
```

**Interpretación:**
- Correlación > 0.9 entre dos predictores: posible redundancia (eliminar uno)
- Correlación alta predictor-target: indicador de relevancia del atributo
- Correlación perfecta con el target: posible data leakage

---

## Detección visual de outliers y distribuciones

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# 1. Histograma — distribución
df["glucosa"].hist(bins=40, ax=axes[0], edgecolor="white")
axes[0].set_title("Distribución de glucosa")
axes[0].set_xlabel("mg/dL")

# 2. Boxplot — outliers y cuartiles
df.boxplot(column="glucosa", ax=axes[1])
axes[1].set_title("Boxplot glucosa")

# 3. Q-Q plot — normalidad
from scipy.stats import probplot
probplot(df["glucosa"].dropna(), plot=axes[2])
axes[2].set_title("Q-Q Plot glucosa")

plt.tight_layout()
plt.savefig("distribucion_glucosa.png", dpi=150)
```

---

## Documentación de la estructura del conjunto

### Ficha de metadatos del dataset explorado

| Campo | Descripción |
|---|---|
| Nombre del conjunto | Identificador único |
| Fecha de exploración | Cuándo se realizó el EDA |
| Fuentes que lo componen | Lista de fuentes integradas |
| Dimensiones | N.º de registros × N.º de atributos |
| Entidad principal | Qué representa cada fila |
| Variables numéricas | Lista, rango esperado, unidades |
| Variables categóricas | Lista, valores posibles, frecuencias |
| Variable objetivo (target) | Nombre, tipo, distribución de clases |
| Periodo temporal cubierto | Fechas de inicio y fin |
| Volumetría en disco | Tamaño del fichero en MB/GB |

---

## Evaluación de la idoneidad del conjunto

### Preguntas que debe responder el EDA antes del modelado

**Representatividad:**
- ¿Los datos cubren todos los segmentos del problema real?
- ¿Hay zonas geográficas, periodos temporales o perfiles de usuario infrarrepresentados?

**Suficiencia:**
- ¿Hay suficientes ejemplos de cada clase para que el modelo aprenda?
- ¿El volumen es proporcional a la complejidad del modelo previsto?

**Relevancia:**
- ¿Las variables disponibles tienen relación demostrable con el objetivo?
- ¿Existen variables que el modelo no podría usar en producción (data leakage)?

**Actualidad:**
- ¿Los datos reflejan el comportamiento actual del sistema o están desfasados?

> Un conjunto de datos idóneo para un modelo de detección de fraude de 2019 puede ser completamente inadecuado para detectar fraude de 2024.

---

## Detección de problemas iniciales de calidad

### Los cinco problemas más frecuentes en fase EDA

```python
# 1. Valores ausentes
nulos = df.isnull().sum()
pct_nulos = (nulos / len(df) * 100).sort_values(ascending=False)
print("Columnas con >20% nulos (candidatas a eliminar):")
print(pct_nulos[pct_nulos > 20])

# 2. Duplicados exactos
print(f"\nRegistros duplicados: {df.duplicated().sum():,}")

# 3. Valores imposibles (ejemplo: edad negativa)
print(f"\nEdades negativas: {(df['edad'] < 0).sum()}")
print(f"Edades > 120: {(df['edad'] > 120).sum()}")

# 4. Inconsistencias entre campos relacionados
problema = df[df["fecha_alta"] < df["fecha_ingreso"]]
print(f"\nAltas anteriores al ingreso: {len(problema)}")

# 5. Cardinalidad alta en categóricas (posible campo libre)
for col in df.select_dtypes("object").columns:
    if df[col].nunique() > 1000:
        print(f"Alta cardinalidad en '{col}': {df[col].nunique()} valores únicos")
```

---

## Herramientas de EDA automatizado

| Herramienta | Qué genera | Instalación |
|---|---|---|
| **ydata-profiling** (ex Pandas Profiling) | Informe HTML completo con estadísticas, correlaciones, alertas | `pip install ydata-profiling` |
| **Sweetviz** | Informe HTML comparativo entre train/test | `pip install sweetviz` |
| **D-Tale** | Interfaz web interactiva para explorar DataFrames | `pip install dtale` |
| **AutoViz** | Visualizaciones automáticas con una línea de código | `pip install autoviz` |
| **Great Expectations** | Validación y perfilado con expectativas definibles | `pip install great-expectations` |

```python
# EDA completo con ydata-profiling en 3 líneas
from ydata_profiling import ProfileReport
profile = ProfileReport(df, title="EDA Dataset Clínico", explorative=True)
profile.to_file("eda_report.html")
```

---

## Criterios de etiquetado y anotación

### Cuándo y cómo se definen los criterios de anotación

En aprendizaje supervisado, la calidad del etiquetado es tan crítica como la calidad de los datos.

| Tipo de anotación | Ejemplos | Herramientas |
|---|---|---|
| Clasificación de texto | Sentimiento, tema, intención | Label Studio, Prodigy |
| Detección de objetos | Cajas delimitadoras en imágenes | CVAT, Roboflow |
| Segmentación | Píxel a píxel en imágenes médicas | ITK-SNAP, Label Studio |
| Clasificación de audio | Tipo de sonido, emoción vocal | Audacity, Label Studio |
| Extracción de entidades | NER en texto clínico o legal | Prodigy, Doccano |

**Criterios que deben definirse antes de anotar:**
- Definición precisa de cada clase o categoría
- Protocolo de casos ambiguos
- Número de anotadores por muestra y criterio de desempate
- Métricas de acuerdo entre anotadores (Cohen's Kappa, Fleiss' Kappa)

---

## Actividad práctica — UD2

### EDA de un conjunto de datos real

**Dataset:** `heart_disease.csv` (disponible en UCI ML Repository — CC-BY 4.0)

**Tareas:**

1. Cargar el dataset e inspeccionar su estructura completa con `df.info()` y `df.describe()`
2. Identificar el tipo de cada variable (numérica continua, discreta, categórica ordinal, nominal)
3. Calcular el porcentaje de valores nulos por columna y proponer una acción para cada caso (eliminar columna, imputar, investigar)
4. Generar la matriz de correlación e identificar las 3 variables con mayor correlación con el target
5. Detectar al menos 2 outliers estadísticos usando el método IQR y documentar si son errores o valores reales
6. Evaluar la idoneidad del conjunto para entrenar un modelo de clasificación binaria
7. Redactar la ficha de metadatos del dataset con los campos de la diapositiva de documentación

---

## Puntos clave — UD2

- **El EDA no es opcional:** es la única forma de saber si los datos son adecuados antes de invertir tiempo en modelado
- **La integración de fuentes genera incompatibilidades:** identificar escalas, zonas horarias, identificadores e inconsistencias categóricas es trabajo previo indispensable
- **El análisis univariante revela la distribución:** media, mediana, percentiles e histogramas muestran si la variable tiene sentido estadístico y de negocio
- **Las correlaciones guían la selección de atributos:** alta correlación predictor-target indica relevancia; alta correlación entre predictores indica redundancia
- **Los problemas de calidad detectados en EDA orientan el preprocesamiento:** cada anomalía encontrada se convertirá en una decisión de transformación en UD4
- **Los criterios de anotación deben definirse antes de etiquetar:** la ambigüedad en el etiquetado produce modelos no reproducibles

---

## Criterios de evaluación — UD2

- Identifica la estructura y las relaciones del conjunto de datos mediante análisis exploratorio
- Evalúa la idoneidad de los datos frente al objetivo del modelo y al contexto de uso
- Registra y documenta los problemas iniciales de calidad detectados
- Aplica herramientas Python estándar (Pandas, Seaborn, ydata-profiling) para el EDA
- Define criterios de etiquetado o anotación coherentes con el tipo de problema supervisado
- Produce la ficha de documentación del conjunto con los campos estructurales requeridos

---

<!-- _class: lead -->

[← Volver a MP01](../)
