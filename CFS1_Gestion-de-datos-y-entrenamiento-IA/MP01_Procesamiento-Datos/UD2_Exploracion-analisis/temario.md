# UD2 · Exploración y análisis del conjunto de datos

**Módulo:** MP01 · Procesamiento de datos para IA  
**Programa:** CFS1 — Gestión de datos y entrenamiento IA  
**Nivel:** Certificado de Formación Superior (Nivel 3)  
**Carga lectiva estimada:** 20 horas (12 teóricas + 8 prácticas)

---

## Introducción

Antes de construir cualquier modelo de inteligencia artificial, existe una fase que resulta decisiva y que, sin embargo, se infravalora con frecuencia: entender los datos. La exploración y el análisis de datos —conocido en la industria por sus siglas en inglés, EDA (*Exploratory Data Analysis*)— constituye el puente entre la adquisición de un conjunto de datos en bruto y la toma de decisiones fundadas sobre cómo preprocesarlo, qué variables resultan relevantes y qué arquitectura de modelo podría ser apropiada.

La premisa central de esta unidad es que los datos no hablan por sí solos: requieren ser interrogados. Un analista o científico de datos que pase directamente de la carga del fichero CSV al entrenamiento del modelo está ignorando señales potencialmente críticas: distribuciones asimétricas que penalizarán a algoritmos sensibles a la escala, correlaciones espurias que inflarán artificialmente las métricas de evaluación, valores nulos que no son ausencias aleatorias sino patrones de comportamiento del sistema que los generó, o clases altamente desequilibradas que sesgarán el aprendizaje.

El EDA tiene raíces en el trabajo estadístico de John Tukey, quien en 1977 publicó *Exploratory Data Analysis*, un texto que redefinió la práctica analítica al proponer que la inspección visual y la estadística descriptiva deben preceder —y no sustituir— a la inferencia formal. Décadas después, con la proliferación de conjuntos de datos de millones de filas y cientos de variables, las herramientas han cambiado pero la filosofía permanece: primero escucha, después modela.

Esta unidad cubre los pilares del EDA aplicado a proyectos de inteligencia artificial: el análisis estadístico descriptivo, la exploración visual, las herramientas del ecosistema Python más utilizadas en la industria, la detección preliminar de anomalías y valores atípicos, el análisis de relaciones entre variables y, finalmente, la síntesis de hallazgos en un informe estructurado que sirva de hoja de ruta para las etapas posteriores de preprocesamiento y modelado.

---

## Objetivos de aprendizaje

Al concluir esta unidad, el estudiante será capaz de:

1. Calcular e interpretar las principales medidas estadísticas descriptivas —tendencia central, dispersión y forma— para variables numéricas y categóricas.
2. Identificar el tipo de distribución de probabilidad que siguen variables de un conjunto de datos real y comprender sus implicaciones para el modelado.
3. Construir representaciones visuales adecuadas para diferentes tipos de variables utilizando Matplotlib, Seaborn y Plotly en Python.
4. Aplicar técnicas univariantes y multivariantes para la detección preliminar de valores atípicos, incluyendo IQR, z-score, Isolation Forest y DBSCAN.
5. Analizar relaciones entre pares de variables mediante coeficientes de correlación de Pearson, Spearman y Kendall, así como mediante el test chi-cuadrado para variables categóricas.
6. Utilizar la biblioteca ydata-profiling para generar informes de EDA automatizados y leer críticamente sus resultados.
7. Redactar un informe de exploración estructurado que documente hallazgos, hipótesis y decisiones de preprocesamiento.

---

## 1. Análisis estadístico descriptivo

### 1.1 Medidas de tendencia central y dispersión

Cuando se recibe un nuevo conjunto de datos, la primera acción analítica consiste en obtener una fotografía numérica de cada variable. La estadística descriptiva proporciona un vocabulario preciso para hacerlo.

**Medidas de tendencia central**

La media aritmética es la medida más habitual, pero también la más sensible a los valores extremos. Se define como la suma de todos los valores dividida entre el número de observaciones. En un conjunto de ingresos salariales de una empresa donde el director general gana diez veces el salario mediano, la media se desplaza hacia arriba de forma engañosa. Por eso, la mediana —el valor que divide la distribución en dos mitades iguales cuando los datos están ordenados— resulta más robusta. La moda, el valor más frecuente, cobra especial importancia en variables discretas o categóricas codificadas numéricamente.

En Python, estas tres medidas se obtienen directamente con Pandas:

```python
import pandas as pd

df = pd.read_csv("dataset.csv")

# Resumen estadístico básico
print(df.describe())

# Mediana y moda individuales
print(df["ingreso"].median())
print(df["ingreso"].mode()[0])
```

El método `describe()` devuelve, para cada columna numérica, el conteo de valores no nulos, la media, la desviación estándar, el mínimo, los percentiles 25, 50 y 75, y el máximo. Es el punto de partida obligado en cualquier exploración.

**Medidas de dispersión**

La varianza mide la dispersión media al cuadrado respecto a la media. Su raíz cuadrada, la desviación estándar, devuelve la dispersión a la misma escala que los datos originales y es la medida más utilizada en la práctica. El rango intercuartílico (IQR), calculado como la diferencia entre el percentil 75 y el percentil 25, es la medida de dispersión más robusta ante valores atípicos.

El coeficiente de variación (CV), que expresa la desviación estándar como porcentaje de la media, permite comparar la dispersión entre variables con diferentes escalas: una variable de temperatura en grados Celsius y otra de ingreso en euros no son comparables en dispersión absoluta, pero sí en dispersión relativa.

**Medidas de forma: asimetría y curtosis**

La asimetría (*skewness*) cuantifica si la distribución tiene una cola más larga hacia la derecha (asimetría positiva) o hacia la izquierda (asimetría negativa). Una distribución perfectamente simétrica tiene asimetría cero. La curtosis (*kurtosis*) mide el peso de las colas respecto a una distribución normal: valores de curtosis elevados indican colas pesadas y, por tanto, una mayor probabilidad de valores extremos.

```python
print(df["ingreso"].skew())
print(df["ingreso"].kurt())
```

En proyectos de IA, estas medidas de forma tienen consecuencias directas: algoritmos basados en la asunción de normalidad (como la regresión lineal con sus supuestos sobre los residuos) se verán afectados por distribuciones muy asimétricas. Algoritmos de árbol de decisión, por el contrario, son invariantes a la escala y la forma de la distribución de las variables predictoras.

### 1.2 Distribuciones de probabilidad y su identificación

Reconocer qué distribución de probabilidad subyace en los datos de una variable no es un ejercicio académico: tiene consecuencias directas sobre qué transformaciones aplicar, qué supuestos de los modelos se cumplen y cómo interpretar los resultados.

Las distribuciones más frecuentes en conjuntos de datos tabulares para IA son:

| Distribución | Característica visual | Ejemplo típico |
|---|---|---|
| Normal (gaussiana) | Simétrica, campana | Altura de personas adultas, errores de medición |
| Log-normal | Asimétrica derecha, se normaliza aplicando logaritmo | Ingresos, precios de activos, tiempo hasta fallo |
| Uniforme | Altura constante en el rango | Números aleatorios, algunos sensores |
| Exponencial | Decrece rápidamente, sin cola izquierda | Tiempo entre eventos, duración de llamadas |
| Binomial / Bernoulli | Discreta, dos resultados posibles | Variables target binarias, conteos con límite |
| Poisson | Discreta, conteos de eventos raros | Número de clicks por minuto, defectos por lote |
| Pareto | Cola extremadamente pesada | Distribución de riqueza, tamaño de ficheros |

Para identificar visualmente la distribución, el histograma y el gráfico Q-Q (*quantile-quantile plot*) son las herramientas principales. El Q-Q plot compara los cuantiles empíricos de los datos con los cuantiles teóricos de una distribución de referencia (habitualmente la normal): si los puntos se alinean sobre la diagonal, los datos siguen esa distribución.

```python
import scipy.stats as stats
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
stats.probplot(df["ingreso"], dist="norm", plot=ax)
ax.set_title("Q-Q Plot: Ingreso vs. Normal")
plt.tight_layout()
plt.show()
```

Para verificaciones formales existe el test de Shapiro-Wilk (adecuado para muestras pequeñas, n < 5000) y el test de Kolmogorov-Smirnov. Sin embargo, en datasets grandes estos tests casi siempre rechazan la normalidad por diferencias estadísticamente significativas pero prácticamente irrelevantes. El juicio visual sigue siendo insustituible.

### 1.3 Estadística para variables categóricas

Las variables categóricas —nominales u ordinales— requieren un tratamiento diferente al de las variables numéricas. Las medidas de tendencia central se reducen a la moda, ya que ni la media ni la mediana tienen sentido semántico sobre categorías.

El análisis de una variable categórica comienza siempre con la tabla de frecuencias absolutas y relativas:

```python
frecuencias = df["categoria"].value_counts()
proporciones = df["categoria"].value_counts(normalize=True) * 100

print(pd.concat([frecuencias, proporciones], axis=1, keys=["n", "%"]))
```

Los aspectos más relevantes a examinar son: la cardinalidad (número de categorías únicas), la presencia de categorías muy minoritarias que pueden representar ruido o errores de entrada, y el desequilibrio entre categorías, especialmente crítico cuando la variable es el target de un clasificador.

Una variable con alta cardinalidad —como el nombre de un municipio con cientos de valores únicos— plantea desafíos de codificación y puede introducir sobreajuste si se trata con *one-hot encoding* sin más consideración. En estos casos conviene estudiar si existe una jerarquía (municipio → provincia → comunidad autónoma) que permita una agregación más informativa.

---

## 2. Exploración visual de los datos

### 2.1 Histogramas, diagramas de caja y violín

La visualización estadística traduce distribuciones y estadísticos en representaciones gráficas que el cerebro humano procesa de forma más inmediata y holística que una tabla de números.

**Histograma**

El histograma divide el rango de una variable continua en intervalos (*bins*) iguales y representa la frecuencia de observaciones en cada intervalo. La elección del número de bins afecta a la interpretación: demasiados bins producen una representación fragmentada y ruidosa; muy pocos ocultan la estructura de la distribución. La regla de Sturges (k = 1 + log₂ n) o la regla de Scott son heurísticas habituales, aunque Matplotlib calcula un valor razonable por defecto.

```python
import matplotlib.pyplot as plt
import seaborn as sns

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Histograma simple
axes[0].hist(df["ingreso"], bins=30, edgecolor="white", color="#4C72B0")
axes[0].set_title("Distribución del Ingreso")
axes[0].set_xlabel("Ingreso (€)")
axes[0].set_ylabel("Frecuencia")

# Con KDE superpuesto usando seaborn
sns.histplot(df["ingreso"], bins=30, kde=True, ax=axes[1], color="#4C72B0")
axes[1].set_title("Histograma con estimación de densidad (KDE)")

plt.tight_layout()
plt.show()
```

La línea KDE (*Kernel Density Estimation*) superpuesta al histograma suaviza la distribución y facilita la identificación de bimodalidades: dos picos sugieren que la muestra mezcla dos subpoblaciones con características distintas, lo cual puede requerir segmentar el análisis.

**Diagrama de caja (boxplot)**

El boxplot condensa cinco estadísticos en una figura: el mínimo, el percentil 25 (Q1), la mediana (Q2), el percentil 75 (Q3) y el máximo. Los bigotes se extienden hasta 1,5 veces el IQR desde cada cuartil; cualquier valor más allá de ese rango se representa como un punto individual y se considera, convencionalmente, un valor atípico.

```python
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Boxplot simple
sns.boxplot(y=df["ingreso"], ax=axes[0], color="#4C72B0")
axes[0].set_title("Boxplot: Ingreso")

# Boxplot por categoría
sns.boxplot(data=df, x="nivel_educativo", y="ingreso", ax=axes[1], palette="Blues")
axes[1].set_title("Ingreso por nivel educativo")
axes[1].tick_params(axis="x", rotation=30)

plt.tight_layout()
plt.show()
```

El boxplot es especialmente útil para comparar distribuciones entre grupos: un solo gráfico muestra si los grupos difieren en mediana, varianza o simetría.

**Diagrama de violín (violinplot)**

El diagrama de violín combina el boxplot con la estimación de densidad KDE. Donde el boxplot resume, el violín muestra la forma completa de la distribución. Es particularmente revelador cuando la distribución es bimodal, ya que el boxplot ocultaría ese rasgo.

```python
sns.violinplot(data=df, x="nivel_educativo", y="ingreso",
               palette="Blues", inner="quartile")
plt.title("Distribución del ingreso por nivel educativo (violín)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()
```

### 2.2 Scatter plots y matrices de correlación

El diagrama de dispersión (*scatter plot*) es la herramienta fundamental para explorar la relación entre dos variables numéricas. Cada observación se representa como un punto en el plano cartesiano. Una relación lineal positiva genera una nube de puntos inclinada hacia arriba; una relación negativa, hacia abajo; la ausencia de relación produce una nube sin estructura.

```python
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(df["anos_experiencia"], df["ingreso"],
           alpha=0.4, s=20, c="#4C72B0")
ax.set_xlabel("Años de experiencia")
ax.set_ylabel("Ingreso (€)")
ax.set_title("Ingreso vs. Años de experiencia")
plt.tight_layout()
plt.show()
```

El parámetro `alpha` controla la transparencia, lo cual es esencial cuando hay miles de puntos superpuestos (*overplotting*). En datasets muy grandes, alternativas como el gráfico hexagonal (`hexbin`) o el gráfico de densidad 2D son más legibles.

Para explorar relaciones entre múltiples pares de variables simultáneamente, Seaborn ofrece el *pairplot*, que genera una matriz de gráficos de dispersión para todas las combinaciones de variables numéricas, con histogramas en la diagonal:

```python
sns.pairplot(df[["ingreso", "edad", "anos_experiencia", "horas_semana"]],
             diag_kind="kde", plot_kws={"alpha": 0.3, "s": 15})
plt.suptitle("Matriz de dispersión", y=1.02)
plt.show()
```

### 2.3 Mapas de calor y correlogramas

Cuando el número de variables numéricas supera las cinco o seis, el pairplot se vuelve difícil de leer. El mapa de calor de la matriz de correlación ofrece una representación más compacta: cada celda muestra el coeficiente de correlación entre dos variables mediante un color codificado.

```python
import numpy as np

corr_matrix = df.select_dtypes(include="number").corr()

mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(
    corr_matrix,
    mask=mask,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
    linewidths=0.5,
    ax=ax
)
ax.set_title("Correlograma — Coeficiente de Pearson")
plt.tight_layout()
plt.show()
```

La máscara triangular elimina la redundancia de la matriz simétrica. La paleta `coolwarm` codifica correlaciones positivas en rojo y negativas en azul, facilitando la identificación de multicolinealidad —correlaciones muy altas entre variables predictoras que pueden desestabilizar modelos lineales— y de las variables más correlacionadas con el target.

### 2.4 Visualización de distribuciones multivariantes

Cuando se trabaja con más de dos variables simultáneamente, las técnicas de visualización multivariante permiten detectar patrones de agrupamiento, separabilidad entre clases y estructuras latentes.

El diagrama de dispersión coloreado por categoría es el enfoque más directo: añade una tercera dimensión mediante el color.

```python
fig, ax = plt.subplots(figsize=(8, 6))
categorias = df["sector"].unique()
colores = sns.color_palette("tab10", len(categorias))

for cat, color in zip(categorias, colores):
    subset = df[df["sector"] == cat]
    ax.scatter(subset["anos_experiencia"], subset["ingreso"],
               label=cat, alpha=0.5, s=20, c=[color])

ax.legend(title="Sector", bbox_to_anchor=(1.05, 1))
ax.set_xlabel("Años de experiencia")
ax.set_ylabel("Ingreso (€)")
ax.set_title("Ingreso vs. experiencia por sector")
plt.tight_layout()
plt.show()
```

Para dimensionalidades mayores, las técnicas de reducción dimensional como PCA (*Principal Component Analysis*) o t-SNE permiten proyectar los datos en dos dimensiones y visualizar su estructura global. Estas técnicas se tratan en profundidad en la UD4; en el contexto del EDA se utilizan como herramienta de inspección visual, no como preprocesamiento final.

---

## 3. Herramientas de EDA en Python

### 3.1 Pandas: perfilado básico

Pandas es la biblioteca central del análisis de datos tabulares en Python. Más allá del ya mencionado `describe()`, ofrece un conjunto de métodos para el perfilado básico que deben conocerse en profundidad.

```python
# Dimensiones del dataset
print(f"Filas: {df.shape[0]} | Columnas: {df.shape[1]}")

# Tipos de datos y valores no nulos por columna
print(df.info())

# Porcentaje de valores nulos por columna
nulos = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
print(nulos[nulos > 0])

# Cardinalidad de variables categóricas
for col in df.select_dtypes(include="object").columns:
    print(f"{col}: {df[col].nunique()} valores únicos")

# Detección de duplicados exactos
print(f"Filas duplicadas: {df.duplicated().sum()}")
```

El método `df.info()` es especialmente valioso porque revela dos cosas críticas: los tipos de datos inferidos por Pandas (que pueden no coincidir con los tipos semánticos reales —una columna de fechas puede haberse importado como `object`— y el número de valores no nulos, que es la primera señal de la presencia de valores faltantes.

Una práctica recomendada es segregar desde el inicio las columnas por tipo semántico:

```python
cols_numericas = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
cols_categoricas = df.select_dtypes(include=["object", "category"]).columns.tolist()
cols_fecha = df.select_dtypes(include=["datetime64"]).columns.tolist()

print(f"Numéricas: {len(cols_numericas)}")
print(f"Categóricas: {len(cols_categoricas)}")
print(f"Fechas: {len(cols_fecha)}")
```

### 3.2 Matplotlib y Seaborn: visualización estadística

Matplotlib es la biblioteca de referencia para la visualización en Python: ofrece control total sobre cada elemento del gráfico a costa de una API más verbosa. Seaborn se construye sobre Matplotlib y proporciona una interfaz de alto nivel orientada a la estadística, con valores por defecto estéticamente cuidados y funciones especializadas para tipos de gráficos habituales en EDA.

La distinción práctica es la siguiente: Seaborn produce gráficos analíticos de calidad con pocas líneas de código; Matplotlib permite ajustes finos de cualquier elemento visual cuando se necesita un control preciso.

```python
# Configuración de estilo global recomendada
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams["figure.dpi"] = 120
```

Un patrón típico en EDA es generar una cuadrícula de histogramas para todas las variables numéricas en una sola figura:

```python
cols_num = df.select_dtypes(include="number").columns
n = len(cols_num)
ncols = 3
nrows = (n + ncols - 1) // ncols

fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows))
axes = axes.flatten()

for i, col in enumerate(cols_num):
    sns.histplot(df[col].dropna(), bins=30, kde=True, ax=axes[i], color="#4C72B0")
    axes[i].set_title(col)
    axes[i].set_xlabel("")

for j in range(i + 1, len(axes)):
    axes[j].set_visible(False)

plt.suptitle("Distribuciones — Variables numéricas", fontsize=14, y=1.01)
plt.tight_layout()
plt.show()
```

### 3.3 Plotly: visualización interactiva

Plotly es la biblioteca de visualización interactiva más utilizada en Python. Sus gráficos se renderizan en HTML y permiten al usuario hacer zoom, filtrar, inspeccionar valores concretos al pasar el cursor y exportar imágenes. Esto los hace especialmente valiosos en notebooks de Jupyter y en dashboards interactivos.

```python
import plotly.express as px

# Scatter plot interactivo con color por categoría y tamaño variable
fig = px.scatter(
    df,
    x="anos_experiencia",
    y="ingreso",
    color="sector",
    size="horas_semana",
    hover_data=["nombre", "nivel_educativo"],
    title="Ingreso vs. experiencia por sector",
    labels={"anos_experiencia": "Años de experiencia", "ingreso": "Ingreso (€)"},
    opacity=0.6
)
fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02))
fig.show()
```

```python
# Histograma interactivo con facetas por sector
fig = px.histogram(
    df,
    x="ingreso",
    color="sector",
    facet_col="sector",
    nbins=30,
    title="Distribución del ingreso por sector"
)
fig.update_layout(showlegend=False)
fig.show()
```

Para el correlograma interactivo:

```python
import plotly.graph_objects as go
import numpy as np

corr = df.select_dtypes(include="number").corr()

fig = go.Figure(data=go.Heatmap(
    z=corr.values,
    x=corr.columns.tolist(),
    y=corr.columns.tolist(),
    colorscale="RdBu_r",
    zmin=-1, zmax=1,
    text=np.round(corr.values, 2),
    texttemplate="%{text}",
    hoverongaps=False
))
fig.update_layout(title="Matriz de correlación interactiva", height=600)
fig.show()
```

### 3.4 ydata-profiling (antes pandas-profiling): EDA automatizado

La biblioteca ydata-profiling genera un informe HTML completo de un DataFrame con una sola línea de código. El informe incluye: resumen del dataset (número de filas, columnas, duplicados, valores nulos), análisis detallado de cada variable (tipo, distribución, estadísticos, valores más frecuentes, alertas automáticas), matriz de correlación y análisis de valores faltantes.

```python
from ydata_profiling import ProfileReport

profile = ProfileReport(
    df,
    title="EDA Automatizado — Dataset de Empleados",
    explorative=True,
    correlations={
        "pearson": {"calculate": True},
        "spearman": {"calculate": True},
        "kendall": {"calculate": False},
        "phi_k": {"calculate": True}
    }
)

# Guardar como HTML
profile.to_file("eda_report.html")

# Mostrar en Jupyter
profile.to_notebook_iframe()
```

El informe detecta automáticamente alertas como: alta cardinalidad, alta correlación entre variables, variables constantes, variables con muchos valores nulos y distribuciones sesgadas. Es un excelente punto de partida, pero no reemplaza el análisis manual: las alertas automáticas señalan qué mirar, no cómo interpretarlo en el contexto del problema.

| Herramienta | Fortaleza | Limitación |
|---|---|---|
| Pandas `describe()` | Rápido, sin dependencias extra | Solo numérica, sin visualización |
| Matplotlib | Control total del gráfico | Verbosidad del código |
| Seaborn | Gráficos estadísticos elegantes con poco código | Menos flexible para layouts complejos |
| Plotly | Interactividad, ideal para notebooks | Mayor tamaño de ficheros HTML |
| ydata-profiling | EDA completo automatizado | Lento en datasets muy grandes |

---

## 4. Detección inicial de anomalías y valores atípicos

### 4.1 Métodos univariantes: IQR, z-score

Un valor atípico u *outlier* es una observación que se aleja de forma notable del resto del conjunto de datos. Su detección en la fase de EDA es preliminar: el objetivo no es eliminarlos automáticamente, sino identificarlos, caracterizarlos y tomar una decisión informada sobre su tratamiento. Algunos outliers son errores de captura; otros son observaciones legítimas y extremadamente valiosas (como una transacción fraudulenta en un dataset de detección de fraude).

**Método IQR**

El método más utilizado en la práctica por su robustez y simplicidad. Define como atípico cualquier valor que caiga por encima de Q3 + 1.5·IQR o por debajo de Q1 - 1.5·IQR. Esta es la convención que usa el boxplot.

```python
def detectar_outliers_iqr(serie):
    Q1 = serie.quantile(0.25)
    Q3 = serie.quantile(0.75)
    IQR = Q3 - Q1
    limite_inf = Q1 - 1.5 * IQR
    limite_sup = Q3 + 1.5 * IQR
    return (serie < limite_inf) | (serie > limite_sup)

for col in df.select_dtypes(include="number").columns:
    mascara = detectar_outliers_iqr(df[col])
    n_outliers = mascara.sum()
    if n_outliers > 0:
        print(f"{col}: {n_outliers} outliers ({n_outliers/len(df)*100:.1f}%)")
```

**Método z-score**

El z-score estandariza cada valor restando la media y dividiendo por la desviación estándar. Valores con |z| > 3 se consideran convencionalmente atípicos bajo el supuesto de normalidad. Es menos robusto que el IQR porque la media y la desviación estándar son sensibles a los propios outliers.

```python
from scipy import stats

z_scores = stats.zscore(df["ingreso"].dropna())
outliers_z = (abs(z_scores) > 3)
print(f"Outliers por z-score: {outliers_z.sum()}")
```

Para distribuciones muy asimétricas, una alternativa más robusta es el **z-score modificado**, que usa la mediana y la desviación mediana absoluta (MAD) en lugar de la media y la desviación estándar.

### 4.2 Métodos multivariantes: Isolation Forest, DBSCAN

Los métodos univariantes examinan cada variable de forma independiente y pueden pasar por alto anomalías que solo son visibles en la combinación de múltiples variables: un empleado con 5 años de experiencia y un salario de 200.000 € puede no ser anómalo en ninguna variable por separado, pero sí en su combinación.

**Isolation Forest**

El Isolation Forest es un algoritmo basado en árboles de decisión aleatorios. La idea central es que una anomalía es más fácil de aislar que un punto normal: requiere menos particiones del espacio de características para quedar sola en un nodo. El algoritmo asigna una puntuación de anomalía a cada observación; puntuaciones cercanas a -1 indican alta probabilidad de ser anomalía.

```python
from sklearn.ensemble import IsolationForest
import numpy as np

features = df[["ingreso", "anos_experiencia", "horas_semana"]].dropna()

iso_forest = IsolationForest(
    n_estimators=100,
    contamination=0.05,  # proporción esperada de anomalías
    random_state=42
)
df.loc[features.index, "anomalia_isoforest"] = iso_forest.fit_predict(features)

# -1 = anomalía, 1 = normal
n_anomalias = (df["anomalia_isoforest"] == -1).sum()
print(f"Anomalías detectadas: {n_anomalias} ({n_anomalias/len(df)*100:.1f}%)")
```

**DBSCAN**

DBSCAN (*Density-Based Spatial Clustering of Applications with Noise*) es un algoritmo de clustering que identifica regiones de alta densidad como clusters y etiqueta como ruido (label = -1) los puntos que no pertenecen a ningún cluster denso. En el contexto del EDA, los puntos de ruido son candidatos a ser outliers multivariantes.

```python
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)

dbscan = DBSCAN(eps=0.5, min_samples=5)
labels = dbscan.fit_predict(X_scaled)

df.loc[features.index, "cluster_dbscan"] = labels
n_ruido = (labels == -1).sum()
print(f"Puntos de ruido (outliers): {n_ruido} ({n_ruido/len(features)*100:.1f}%)")
```

La elección del parámetro `eps` (radio de vecindad) es crítica y puede determinarse con el gráfico de la distancia al k-ésimo vecino más próximo: se busca el "codo" de la curva.

### 4.3 Valores nulos: patrones y su significado

Los valores nulos o faltantes no son simplemente datos ausentes: son información sobre el proceso que generó los datos. La clasificación de Rubin (1976) distingue tres mecanismos de ausencia que tienen implicaciones muy diferentes para el tratamiento:

**MCAR (*Missing Completely At Random*):** La ausencia no depende del valor faltante ni de ninguna otra variable del dataset. Un sensor que falla aleatoriamente genera ausencias MCAR. La imputación por la media o la mediana es razonablemente segura en este caso.

**MAR (*Missing At Random*):** La ausencia depende de otras variables observadas, pero no del valor que faltaría. Por ejemplo, los hombres tienden a no responder preguntas sobre salud mental en encuestas: la ausencia depende del sexo (observable), no del estado de salud en sí.

**MNAR (*Missing Not At Random*):** La ausencia depende del valor que faltaría. Las personas con ingresos muy altos o muy bajos tienden a no declarar sus ingresos. Este es el caso más problemático porque la imputación introduce sesgo.

Para explorar los patrones de ausencia:

```python
import missingno as msno
import matplotlib.pyplot as plt

# Mapa de nulos (barras por columna)
msno.bar(df, figsize=(12, 5), color="#4C72B0")
plt.title("Completitud por variable")
plt.show()

# Matriz de nulos (patrón de co-ocurrencia)
msno.matrix(df, figsize=(12, 5))
plt.title("Patrón de valores faltantes")
plt.show()

# Dendrograma de correlación de nulos
msno.dendrogram(df, figsize=(12, 5))
plt.title("Correlación de ausencias")
plt.show()
```

El mapa de calor de correlación de nulos (disponible también en missingno como `msno.heatmap`) revela si dos variables tienden a ser nulas juntas, lo que sugiere un mecanismo MAR o MNAR compartido.

---

## 5. Análisis de relaciones entre variables

### 5.1 Correlación de Pearson, Spearman y Kendall

La correlación cuantifica la fuerza y dirección de la relación entre dos variables. Existen varios coeficientes con supuestos y propiedades distintas.

**Correlación de Pearson (r)**

Mide la relación lineal entre dos variables continuas. Varía entre -1 (relación lineal negativa perfecta) y +1 (relación lineal positiva perfecta). Sus supuestos son: escala de medición continua, relación lineal y ausencia de outliers severos. Es el coeficiente por defecto en `df.corr()`.

**Correlación de Spearman (ρ)**

Es el equivalente no paramétrico de Pearson. En lugar de operar sobre los valores brutos, opera sobre los rangos. Detecta relaciones monótonas (no necesariamente lineales) y es robusta ante outliers y distribuciones no normales. Es la opción recomendada cuando los supuestos de Pearson no se cumplen.

**Tau de Kendall (τ)**

También basado en rangos. Mide la concordancia de pares: para cada par de observaciones, determina si el orden relativo en una variable coincide con el orden relativo en la otra. Es más robusto que Spearman en muestras pequeñas y con muchos empates.

```python
from scipy.stats import pearsonr, spearmanr, kendalltau

x = df["anos_experiencia"].dropna()
y = df["ingreso"].dropna()

# Alinear índices
idx = x.index.intersection(y.index)
x, y = x[idx], y[idx]

r, p_pearson = pearsonr(x, y)
rho, p_spearman = spearmanr(x, y)
tau, p_kendall = kendalltau(x, y)

print(f"Pearson r = {r:.3f} (p = {p_pearson:.4f})")
print(f"Spearman ρ = {rho:.3f} (p = {p_spearman:.4f})")
print(f"Kendall τ = {tau:.3f} (p = {p_kendall:.4f})")
```

| Coeficiente | Tipo de relación detectada | Supuestos | Robustez ante outliers |
|---|---|---|---|
| Pearson r | Lineal | Normalidad, escala continua | Baja |
| Spearman ρ | Monótona | Escala ordinal mínima | Alta |
| Kendall τ | Monótona (basado en concordancia) | Escala ordinal mínima | Muy alta |

### 5.2 Test de chi-cuadrado para variables categóricas

El test de independencia de chi-cuadrado evalúa si existe una asociación estadísticamente significativa entre dos variables categóricas. La hipótesis nula (H₀) es que las variables son independientes; la hipótesis alternativa es que existe una asociación.

El test se basa en la comparación entre las frecuencias observadas en la tabla de contingencia y las frecuencias esperadas bajo el supuesto de independencia. Si la diferencia es suficientemente grande (chi² grande, p-valor pequeño), se rechaza H₀.

```python
from scipy.stats import chi2_contingency

tabla_contingencia = pd.crosstab(df["sector"], df["nivel_educativo"])

chi2, p_valor, grados_libertad, frecuencias_esperadas = chi2_contingency(tabla_contingencia)

print(f"Chi² = {chi2:.4f}")
print(f"p-valor = {p_valor:.4f}")
print(f"Grados de libertad = {grados_libertad}")
print(f"Significativo al 5%: {'Sí' if p_valor < 0.05 else 'No'}")
```

Como medida de fuerza de la asociación (análoga al coeficiente de correlación), se utiliza la **V de Cramér**, que normaliza chi² entre 0 (independencia total) y 1 (asociación perfecta):

```python
import numpy as np

n = tabla_contingencia.values.sum()
v_cramer = np.sqrt(chi2 / (n * (min(tabla_contingencia.shape) - 1)))
print(f"V de Cramér = {v_cramer:.4f}")
```

Una V de Cramér superior a 0.3 indica una asociación moderada; superior a 0.5, una asociación fuerte.

### 5.3 Análisis de covarianza y relaciones no lineales

La covarianza mide la variación conjunta de dos variables: si cuando X sube Y también tiende a subir, la covarianza es positiva. Sin embargo, la covarianza no está acotada y depende de la escala de las variables, lo que hace que la correlación —covarianza normalizada— sea más interpretable.

La covarianza tiene relevancia directa en el contexto del Análisis de Componentes Principales (PCA), cuya matriz de entrada es precisamente la matriz de covarianza (o correlación). En el EDA, observar la matriz de covarianza ayuda a entender cuán "juntas" varían las variables antes de aplicar cualquier transformación.

Las relaciones no lineales son frecuentes en datos del mundo real y el coeficiente de Pearson las subestima sistemáticamente. Para detectarlas:

1. **Visualización:** El scatter plot con un ajuste de regresión no paramétrico (LOESS) revela la forma de la relación.

```python
import statsmodels.api as sm

fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(df["edad"], df["ingreso"], alpha=0.3, s=15, c="#4C72B0")

# Ajuste LOESS
lowess = sm.nonparametric.lowess(df["ingreso"], df["edad"], frac=0.3)
ax.plot(lowess[:, 0], lowess[:, 1], color="red", linewidth=2, label="LOESS")
ax.set_title("Ingreso vs. Edad con ajuste LOESS")
ax.legend()
plt.tight_layout()
plt.show()
```

2. **MIC (Maximal Information Coefficient):** Una medida de dependencia que captura relaciones tanto lineales como no lineales. Se implementa en la biblioteca `minepy`.

3. **Correlación de distancias:** Detecta dependencias arbitrarias entre variables y está disponible en `scipy.spatial.distance`.

---

## 6. Síntesis e informe de exploración

### 6.1 Estructura de un informe EDA

El informe de exploración es el documento que cierra la fase de EDA y que da paso al preprocesamiento. Su audiencia puede ser técnica (compañeros de equipo o el propio analista en el futuro) o mixta (incluye a interlocutores de negocio). Un buen informe EDA debe ser reproducible, lo que significa que el código que lo genera debe estar versionado y la fuente de datos claramente especificada.

La estructura recomendada para un informe de exploración en proyectos de IA es la siguiente:

**1. Descripción del dataset**
- Origen y fecha de extracción
- Número de observaciones y variables
- Tipología de variables (numéricas, categóricas, temporales, texto)
- Unidad de análisis (¿qué representa cada fila?)

**2. Calidad de los datos**
- Porcentaje de valores nulos por columna y análisis del mecanismo de ausencia
- Duplicados (exactos o casi-duplicados)
- Inconsistencias de tipo (columnas con tipos incorrectos)
- Valores imposibles o fuera de rango (por ejemplo, edades negativas)

**3. Análisis univariante**
- Distribución de cada variable (estadísticos descriptivos + visualización)
- Identificación de variables con distribución muy sesgada o alta curtosis
- Análisis de frecuencias de variables categóricas

**4. Análisis bivariante y multivariante**
- Correlaciones entre variables numéricas (mapa de calor)
- Relaciones entre pares de variables numéricas y el target
- Asociación entre variables categóricas (chi-cuadrado, V de Cramér)
- Relaciones entre variables categóricas y el target

**5. Detección de anomalías**
- Resultados de los métodos IQR y z-score
- Resultados del Isolation Forest o DBSCAN si se aplicaron
- Caracterización de los outliers: ¿son errores o casos extremos legítimos?

**6. Hipótesis y decisiones**
- Hipótesis formuladas sobre las relaciones en los datos
- Decisiones de preprocesamiento derivadas del análisis
- Variables candidatas a ser eliminadas, transformadas o codificadas de forma especial

### 6.2 Hipótesis generadas y decisiones de preprocesamiento

El EDA no termina con la descripción: termina con la acción. Cada hallazgo debe traducirse en una decisión concreta que se documenta y que se implementará en la siguiente fase.

A continuación se presenta un ejemplo de tabla de decisiones de preprocesamiento derivadas de un EDA típico:

| Hallazgo | Variable afectada | Decisión de preprocesamiento |
|---|---|---|
| Distribución log-normal | `ingreso` | Aplicar transformación logarítmica: `log(ingreso + 1)` |
| 15% de valores nulos, patrón MCAR | `horas_semana` | Imputación por mediana |
| 8% de valores nulos, patrón MAR (depende de `sector`) | `salario_base` | Imputación por mediana agrupada por `sector` |
| Correlación Pearson r = 0.95 con otra variable | `ingreso_bruto` | Eliminar por multicolinealidad (mantener `ingreso_neto`) |
| 3% de outliers detectados por IQR | `antiguedad` | Revisión manual; capping al percentil 99 si son errores |
| Alta cardinalidad (350 categorías) | `municipio` | Agregación por provincia o embeddings de entidad |
| Variable constante | `pais` | Eliminar (sin varianza, sin aporte predictivo) |
| Desbalanceo de clases 95/5 | `fraude` (target) | Técnicas de *oversampling* (SMOTE) o ponderación de clases |

Este tipo de tabla convierte el EDA en un artefacto operacional: cada hallazgo tiene un propietario (una decisión) y esa decisión queda registrada para su trazabilidad durante el desarrollo del proyecto.

---

## Actividades prácticas propuestas

**Actividad 1 — EDA básico con Pandas (2 horas)**

Descarga el dataset *Adult Income* del UCI Machine Learning Repository. Carga el fichero con Pandas y realiza un análisis estadístico descriptivo completo: dimensiones, tipos de datos, valores nulos, estadísticos descriptivos por tipo de variable y análisis de frecuencias de las variables categóricas. Documenta todos los hallazgos en un notebook de Jupyter con celdas de texto explicativas.

**Actividad 2 — Visualización estadística (2 horas)**

Utilizando el mismo dataset, genera: (a) histogramas con KDE para todas las variables numéricas, (b) boxplots de las variables numéricas segmentados por la variable target (`income`), (c) gráficos de barras de frecuencia para las variables categóricas más relevantes y (d) un correlograma de la matriz de Pearson. Añade títulos, etiquetas y comentarios interpretativos a cada gráfico.

**Actividad 3 — Detección de outliers (2 horas)**

Utilizando un dataset de tu elección (por ejemplo, el dataset *House Prices* de Kaggle), aplica los métodos IQR y z-score para identificar outliers univariantes en todas las variables numéricas. Luego aplica Isolation Forest sobre un subconjunto de tres variables numéricas seleccionadas. Visualiza los resultados sobreponiendo los outliers detectados en los scatter plots correspondientes. Redacta una conclusión sobre qué harías con cada conjunto de outliers.

**Actividad 4 — Análisis de correlaciones (2 horas)**

Sobre el dataset *Titanic* (disponible en Seaborn: `sns.load_dataset("titanic")`), calcula los coeficientes de Pearson, Spearman y Kendall entre todas las parejas de variables numéricas. Aplica el test de chi-cuadrado y calcula la V de Cramér para las parejas de variables categóricas relevantes. Genera un informe tabular que resuma los resultados y destaque las relaciones más fuertes con la variable target (`survived`).

**Actividad 5 — Informe EDA completo (2 horas)**

Usando el dataset *Diabetes* de Scikit-learn (`sklearn.datasets.load_diabetes()`), genera un informe completo con ydata-profiling. Exporta el informe como HTML. Revisa críticamente las alertas automáticas generadas y redacta un documento de una página (entre 400 y 600 palabras) que sintetice los hallazgos principales y proponga al menos cinco decisiones de preprocesamiento justificadas.

---

## Referencias y material externo

### Libros

Tukey, J. W. (1977). *Exploratory Data Analysis*. Addison-Wesley. ISBN 978-0-201-07616-5.

McKinney, W. (2022). *Python for Data Analysis: Data Wrangling with pandas, NumPy, and Jupyter* (3.ª ed.). O'Reilly Media. ISBN 978-1-098-10403-0. Disponible en: https://wesmckinney.com/book/

VanderPlas, J. (2016). *Python Data Science Handbook*. O'Reilly Media. Disponible en abierto: https://jakevdp.github.io/PythonDataScienceHandbook/

Grus, J. (2019). *Data Science from Scratch: First Principles with Python* (2.ª ed.). O'Reilly Media. ISBN 978-1-492-04113-9.

Müller, A. C., & Guido, S. (2016). *Introduction to Machine Learning with Python*. O'Reilly Media. ISBN 978-1-449-36941-5.

### Documentación oficial

Pandas Development Team. (2024). *pandas documentation*. https://pandas.pydata.org/docs/

Hunter, J. D., et al. (2024). *Matplotlib documentation*. https://matplotlib.org/stable/index.html

Waskom, M. (2024). *Seaborn: Statistical data visualization*. https://seaborn.pydata.org/

Plotly Technologies Inc. (2024). *Plotly Python Open Source Graphing Library*. https://plotly.com/python/

ydata-ai. (2024). *ydata-profiling documentation*. https://docs.profiling.ydata.ai/

scikit-learn developers. (2024). *Isolation Forest — sklearn.ensemble*. https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html

scikit-learn developers. (2024). *DBSCAN — sklearn.cluster*. https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html

### Artículos y papers

Rubin, D. B. (1976). Inference and missing data. *Biometrika*, 63(3), 581–592. https://doi.org/10.1093/biomet/63.3.581

Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation Forest. *Proceedings of the 8th IEEE International Conference on Data Mining (ICDM)*, 413–422. https://doi.org/10.1109/ICDM.2008.17

Ester, M., Kriegel, H.-P., Sander, J., & Xu, X. (1996). A density-based algorithm for discovering clusters in large spatial databases with noise. *Proceedings of the 2nd International Conference on Knowledge Discovery and Data Mining (KDD)*, 226–231. https://dl.acm.org/doi/10.5555/3001460.3001507

Reshef, D. N., et al. (2011). Detecting novel associations in large data sets. *Science*, 334(6062), 1518–1524. https://doi.org/10.1126/science.1205438

### Datasets recomendados para práctica

UCI Machine Learning Repository. (2024). *Adult Income Dataset*. https://archive.ics.uci.edu/ml/datasets/adult

Kaggle. (2024). *House Prices: Advanced Regression Techniques*. https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques

Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830. https://jmlr.org/papers/v12/pedregosa11a.html [Incluye el dataset Diabetes]

### Recursos en línea

Towards Data Science. (2023). *A comprehensive guide to exploratory data analysis*. https://towardsdatascience.com/exploratory-data-analysis-8fc1cb20fd15

StatQuest with Josh Starmer. (2023). *Statistics Fundamentals* [serie de vídeos]. YouTube. https://www.youtube.com/@statquest

Real Python. (2024). *Exploratory Data Analysis with Python and Pandas*. https://realpython.com/pandas-python-explore-dataset/
