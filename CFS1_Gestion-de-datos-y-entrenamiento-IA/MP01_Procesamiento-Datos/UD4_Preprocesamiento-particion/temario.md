# UD4 · Preprocesamiento y partición de datos

**Módulo:** MP01 · Procesamiento de datos para IA
**Programa:** CFS1 — Gestión de datos y entrenamiento IA
**Nivel:** CFS Nivel 3

---

## Introducción

El aprendizaje automático no empieza cuando se entrena un modelo; empieza cuando se examina el dato crudo y se decide qué hacer con él. Esta unidad aborda el conjunto de transformaciones que median entre la adquisición de datos y la alimentación de un algoritmo de aprendizaje: el preprocesamiento. Lejos de ser un trámite rutinario, el preprocesamiento constituye a menudo la diferencia entre un modelo que generaliza bien y uno que simplemente memoriza ruido.

Los conjuntos de datos del mundo real presentan una serie de problemas recurrentes: valores ausentes por fallos de registro o diseño del sistema, variables categóricas que los algoritmos numéricos no pueden procesar directamente, escalas heterogéneas que desequilibran la influencia de cada variable sobre el modelo, y dimensionalidades tan altas que la maldición de la dimensionalidad impide cualquier aprendizaje estadístico robusto. A todo ello se añade la ingeniería de características, proceso creativo y analítico mediante el cual el profesional convierte información bruta en representaciones que permiten al modelo extraer patrones más fácilmente.

La partición del conjunto de datos, aunque conceptualmente sencilla, esconde trampas que invalidan resultados enteros si no se aplica con rigor. La fuga de información (data leakage) es uno de los errores más frecuentes en proyectos de ciencia de datos y lleva a estimaciones de rendimiento optimistas que no se reproducen en producción.

Esta unidad trata todos estos aspectos con profundidad teórica suficiente para entender por qué funciona cada técnica y con ejemplos de código en Python que permiten aplicarla de inmediato. La biblioteca principal de referencia es scikit-learn, complementada con pandas para la manipulación de datos.

---

## Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Identificar el tipo y el mecanismo de ausencia de valores en un conjunto de datos y elegir la estrategia de imputación apropiada según el contexto.
2. Codificar variables categóricas empleando el método adecuado para cada tipo de variable y para cada familia de algoritmos de aprendizaje.
3. Aplicar transformaciones de escala y distribución sobre variables numéricas, justificando la elección en función del algoritmo y la distribución de los datos.
4. Diseñar nuevas características mediante técnicas de feature engineering que incrementen la capacidad predictiva de un modelo.
5. Reducir la dimensionalidad de un conjunto de datos mediante técnicas lineales y no lineales, interpretando los resultados.
6. Diseñar una estrategia de partición de datos que evite la fuga de información y produzca estimaciones de rendimiento fiables.
7. Implementar pipelines de preprocesamiento en scikit-learn que encapsulen todas las transformaciones y garanticen su aplicación correcta en entrenamiento e inferencia.

---

## 1. Tratamiento de valores faltantes

Los valores faltantes son la primera realidad que todo profesional de datos encuentra. Comprenderlos requiere distinguir entre tres mecanismos de ausencia formalizados por Little y Rubin (1987): MCAR (*Missing Completely At Random*), cuando la probabilidad de que un valor falte no depende de ninguna variable observada ni del propio valor; MAR (*Missing At Random*), cuando la probabilidad de ausencia depende de otras variables observadas pero no del valor faltante en sí; y MNAR (*Missing Not At Random*), cuando la ausencia está relacionada con el propio valor que falta. Esta distinción importa porque determina qué métodos de imputación son estadísticamente válidos.

Antes de imputar conviene explorar el patrón de ausencias. La función `DataFrame.isnull().sum()` de pandas ofrece un conteo básico; bibliotecas como `missingno` permiten visualizar las correlaciones entre ausencias y detectar si los valores faltan en bloque o de forma dispersa.

```python
import pandas as pd
import missingno as msno

df = pd.read_csv("dataset.csv")
print(df.isnull().sum())
msno.matrix(df)
```

### 1.1 Imputación univariante: media, mediana, moda

La imputación univariante reemplaza cada valor faltante de una columna usando únicamente la información de esa misma columna. Es el enfoque más simple y el punto de partida habitual. scikit-learn implementa esto mediante `SimpleImputer`.

La media es adecuada para variables numéricas con distribución aproximadamente simétrica. La mediana es preferible cuando la distribución es asimétrica o contiene valores extremos, ya que es un estimador robusto que no se desplaza por los outliers. La moda se utiliza para variables categóricas o numéricas discretas.

```python
from sklearn.impute import SimpleImputer
import numpy as np

# Imputación con la mediana para variables numéricas
imputer_num = SimpleImputer(strategy="median")
X_num_imputed = imputer_num.fit_transform(X_num)

# Imputación con la moda para variables categóricas
imputer_cat = SimpleImputer(strategy="most_frequent")
X_cat_imputed = imputer_cat.fit_transform(X_cat)
```

Un aspecto crítico: `fit` debe llamarse únicamente sobre el conjunto de entrenamiento. Aplicar `fit_transform` sobre todo el dataset antes de dividirlo introduce fuga de información, porque la media o mediana calculada incluye información del conjunto de test.

La imputación univariante tiene limitaciones importantes: ignora las relaciones entre variables, puede distorsionar la distribución, y reduce artificialmente la varianza de la columna imputada. Estas limitaciones motivan los métodos multivariantes.

### 1.2 Imputación multivariante: KNN, MICE/IterativeImputer

Los métodos multivariantes aprovechan la correlación entre variables para estimar los valores faltantes. Son computacionalmente más costosos pero producen imputaciones más realistas cuando los datos presentan estructura correlacional.

**KNN Imputer.** El imputador basado en k vecinos más cercanos busca, para cada muestra con valores faltantes, las k muestras más similares (usando las variables disponibles para calcular la distancia) y promedia sus valores. scikit-learn incluye `KNNImputer` desde la versión 0.22.

```python
from sklearn.impute import KNNImputer

knn_imputer = KNNImputer(n_neighbors=5, weights="uniform")
X_knn = knn_imputer.fit_transform(X)
```

El parámetro `n_neighbors` controla el balance entre sesgo y varianza de la imputación. Valores pequeños capturan la estructura local pero son ruidosos; valores grandes producen imputaciones más suaves pero pueden perder patrones locales.

**MICE / IterativeImputer.** El algoritmo MICE (*Multiple Imputation by Chained Equations*) es más sofisticado. El proceso es iterativo: para cada variable con valores faltantes, ajusta un modelo de regresión usando el resto de variables como predictores, y usa ese modelo para imputar. El proceso se repite varias veces hasta convergencia. En scikit-learn se implementa como `IterativeImputer`, que aunque en versiones recientes ha salido del estado experimental, conviene importarla habilitando el flag correspondiente.

```python
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge

iter_imputer = IterativeImputer(
    estimator=BayesianRidge(),
    max_iter=10,
    random_state=42
)
X_iter = iter_imputer.fit_transform(X)
```

El estimador interno puede ser cualquier regresor de scikit-learn, lo que hace al método muy flexible. `BayesianRidge` es la opción por defecto y funciona bien en la mayoría de casos.

| Método | Complejidad | Captura correlaciones | Adecuado para MCAR | Adecuado para MAR |
|---|---|---|---|---|
| Media/Mediana | Baja | No | Sí (con sesgo) | No |
| Moda | Baja | No | Sí (con sesgo) | No |
| KNN Imputer | Media | Parcial | Sí | Sí |
| IterativeImputer | Alta | Sí | Sí | Sí |

### 1.3 Imputación con modelos predictivos

Cuando el volumen de datos es grande y la precisión de la imputación es crítica, es posible entrenar modelos supervisados completos para predecir los valores faltantes. La idea es tratar la columna con missing como variable objetivo y el resto del dataset como predictores.

Un enfoque habitual consiste en dividir el dataset en dos subconjuntos: filas donde la variable objetivo tiene valor (conjunto de entrenamiento del imputador) y filas donde falta (conjunto de predicción). Se entrena un modelo en el primer subconjunto y se aplica en el segundo.

```python
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# Separar filas con y sin valor en 'columna_con_missing'
train_imp = df[df["columna_con_missing"].notna()]
pred_imp  = df[df["columna_con_missing"].isna()]

features = [c for c in df.columns if c != "columna_con_missing"]

rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(train_imp[features].dropna(), train_imp["columna_con_missing"])

df.loc[df["columna_con_missing"].isna(), "columna_con_missing"] = rf.predict(
    pred_imp[features].fillna(pred_imp[features].median())
)
```

Este enfoque es equivalente a lo que hace `IterativeImputer` internamente, pero permite un control total sobre el modelo utilizado y la gestión de las ausencias en los propios predictores.

---

## 2. Codificación de variables categóricas

Los algoritmos de aprendizaje automático operan sobre espacios vectoriales numéricos. Las variables categóricas —aquellas que toman valores de un conjunto discreto y finito— deben transformarse en representaciones numéricas antes de poder ser utilizadas. La elección del método de codificación no es trivial: puede afectar tanto al rendimiento del modelo como a la interpretabilidad de los coeficientes.

### 2.1 One-Hot Encoding y sus variantes

One-Hot Encoding (OHE) transforma una variable categórica con k categorías en k columnas binarias (0 o 1), donde exactamente una de ellas vale 1 para cada observación. Es la técnica más utilizada para variables nominales (sin orden inherente).

```python
from sklearn.preprocessing import OneHotEncoder
import pandas as pd

enc = OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore")
X_encoded = enc.fit_transform(X_cat)
feature_names = enc.get_feature_names_out()
```

El parámetro `drop="first"` elimina una de las columnas generadas para evitar la multicolinealidad perfecta (trampa de las variables dummy), lo que es especialmente importante para modelos lineales. Con `handle_unknown="ignore"`, las categorías no vistas en entrenamiento se codifican como un vector de ceros, lo que evita errores en producción.

La principal desventaja de OHE es la explosión de dimensionalidad cuando la variable tiene alta cardinalidad (muchas categorías distintas). Una variable con 500 categorías genera 500 columnas, la mayoría de las cuales contendrán casi todos ceros, lo que degrada el rendimiento de muchos algoritmos.

Para cardinalidades moderadas, `pandas.get_dummies` ofrece una alternativa más rápida para exploración, aunque no integra bien con los pipelines de scikit-learn porque no recuerda las categorías vistas en entrenamiento.

### 2.2 Label Encoding y Ordinal Encoding

Label Encoding asigna a cada categoría un entero de forma arbitraria (0, 1, 2, …). Es computacionalmente eficiente y no aumenta la dimensionalidad, pero introduce una ordenación artificial entre categorías que no existe en los datos. Por esto, su uso está limitado a variables ordinales (que sí tienen un orden natural, como niveles educativos o tallas) o a algoritmos basados en árboles de decisión, que no presuponen ninguna relación de orden en los valores de entrada.

```python
from sklearn.preprocessing import OrdinalEncoder

# Variable ordinal: nivel de educación
order = [["Primaria", "Secundaria", "Bachillerato", "Universitario", "Posgrado"]]
enc = OrdinalEncoder(categories=order)
X_ord = enc.fit_transform(X[["nivel_educacion"]])
```

`OrdinalEncoder` permite especificar explícitamente el orden de las categorías, lo que es fundamental para garantizar que la codificación respeta la semántica real de la variable.

`LabelEncoder` de scikit-learn está diseñado para la variable objetivo (y), no para las features, ya que solo opera sobre arrays unidimensionales.

### 2.3 Target Encoding y Mean Encoding

Target Encoding, también llamado Mean Encoding, reemplaza cada categoría por la media de la variable objetivo en las observaciones que pertenecen a esa categoría. Produce una representación numérica de una sola columna que captura directamente la relación entre la categoría y el target, lo que puede ser muy informativo para el modelo.

Sin embargo, Target Encoding introduce un riesgo severo de fuga de información y sobreajuste: si la media se calcula sobre todo el conjunto de entrenamiento (incluyendo la propia observación), el codificador "ve" el target al codificar la feature. Para mitigar esto se utilizan dos técnicas: la regularización con suavizado y la codificación cruzada (leave-one-out o k-fold).

La biblioteca `category_encoders` ofrece implementaciones robustas de esta familia de técnicas:

```python
import category_encoders as ce
from sklearn.model_selection import cross_val_score

enc = ce.TargetEncoder(cols=["ciudad"], smoothing=10)
X_te = enc.fit_transform(X_train, y_train)
```

El parámetro `smoothing` controla el peso entre la media global y la media de la categoría: para categorías poco frecuentes, la estimación se aproxima a la media global, reduciendo la varianza de la imputación.

| Técnica | Dimensionalidad | Riesgo de leakage | Adecuada para árboles | Adecuada para modelos lineales |
|---|---|---|---|---|
| OHE | Alta (k columnas) | Bajo | Sí | Sí |
| Label/Ordinal | Sin cambio | Bajo | Sí (ordinales) | Solo ordinales |
| Target Encoding | Sin cambio | Alto (mitigar) | Sí | Sí |
| Embeddings | Reducida | Bajo | Depende | Sí |

### 2.4 Embeddings para alta cardinalidad

Cuando una variable categórica tiene miles de categorías (por ejemplo, el ID de un producto, el código postal o el nombre de un usuario), ni OHE ni Target Encoding son soluciones satisfactorias. En estos casos, los embeddings aprendidos ofrecen una alternativa potente.

Un embedding transforma cada categoría en un vector denso de dimensión reducida que se aprende durante el entrenamiento del modelo. Este enfoque, popularizado por las redes neuronales para procesamiento de lenguaje natural, se ha extendido a la tabulación general de datos. Los embeddings capturan relaciones de similitud entre categorías: categorías que co-ocurren con patrones similares en el target tendrán representaciones vectoriales cercanas.

En keras/TensorFlow, un embedding se implementa mediante una capa `Embedding`. En PyTorch existe `nn.Embedding`. Para datos tabulares, la biblioteca `fastai` popularizó su uso mediante la arquitectura `TabularModel`.

Para tareas en las que no se dispone de redes neuronales, una alternativa es usar Target Encoding con múltiples folds, o aplicar SVD (Descomposición en Valores Singulares) sobre la matriz OHE para obtener una representación densa de dimensión reducida.

---

## 3. Escalado y normalización de variables numéricas

La mayoría de los algoritmos de aprendizaje automático son sensibles a la escala de las variables de entrada. Una variable con valores en el rango [0, 1] y otra con valores en el rango [0, 100.000] harán que los gradientes, las distancias o los coeficientes se vean dominados por la segunda, aunque no sea más informativa. Los árboles de decisión y los bosques aleatorios son una excepción notable: al basarse en comparaciones de umbral, son invariantes a transformaciones monótonas de escala. Los modelos lineales, las redes neuronales, las SVM y los algoritmos basados en distancias (KNN, K-Means) sí requieren escalado.

### 3.1 Estandarización: StandardScaler

La estandarización transforma cada variable para que tenga media cero y desviación estándar igual a uno:

$$z = \frac{x - \mu}{\sigma}$$

Donde μ es la media y σ es la desviación estándar, ambas calculadas sobre el conjunto de entrenamiento.

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)  # Solo transform, nunca fit_transform
```

La estandarización no limita el rango de los valores resultantes (puede producir valores muy alejados de cero si hay outliers), pero preserva la forma de la distribución. Es la técnica por defecto para modelos lineales y redes neuronales.

### 3.2 Normalización Min-Max: MinMaxScaler

`MinMaxScaler` comprime los valores al rango [0, 1] (o a un rango personalizable):

$$x' = \frac{x - x_{min}}{x_{max} - x_{min}}$$

```python
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler(feature_range=(0, 1))
X_train_mm = scaler.fit_transform(X_train)
X_test_mm  = scaler.transform(X_test)
```

Su desventaja principal es la sensibilidad a los outliers: un único valor extremo desplaza x_min o x_max y comprime el resto de valores en un rango estrecho. Por esta razón, solo es recomendable cuando se sabe que los datos no contienen outliers significativos, o cuando el algoritmo requiere que las entradas estén en [0, 1] (por ejemplo, algunas redes neuronales con activaciones sigmoid en la capa de salida para regresión acotada).

### 3.3 Escalado robusto: RobustScaler

`RobustScaler` usa la mediana y el rango intercuartílico (IQR) en lugar de la media y la desviación estándar:

$$x' = \frac{x - Q_2}{Q_3 - Q_1}$$

Al ser estadísticos robustos, la mediana y el IQR no se ven afectados por valores extremos, lo que hace a este escalador idóneo para datasets con outliers sin necesidad de eliminarlos previamente.

```python
from sklearn.preprocessing import RobustScaler

scaler = RobustScaler(quantile_range=(25.0, 75.0))
X_robust = scaler.fit_transform(X_train)
```

### 3.4 Transformaciones de distribución: log, Box-Cox, Yeo-Johnson

Muchos modelos estadísticos asumen que las variables tienen distribuciones aproximadamente normales (o al menos simétricas). Cuando la distribución de una variable está muy sesgada, las transformaciones matemáticas pueden reducir ese sesgo y mejorar el rendimiento del modelo.

**Transformación logarítmica.** Aplicar `np.log1p(x)` (logaritmo de x+1 para manejar ceros) es la transformación más simple y frecuente para variables con sesgo positivo, como precios o ingresos.

**Box-Cox.** La transformación Box-Cox es paramétrica: encuentra el valor λ que maximiza la verosimilitud de la distribución normal resultante. Solo aplica a valores positivos.

**Yeo-Johnson.** Es una generalización de Box-Cox que admite valores negativos y ceros, lo que la hace más versátil en la práctica.

```python
from sklearn.preprocessing import PowerTransformer

# Yeo-Johnson (admite valores negativos y ceros)
pt_yj = PowerTransformer(method="yeo-johnson", standardize=True)
X_yj = pt_yj.fit_transform(X_train)

# Box-Cox (solo valores estrictamente positivos)
pt_bc = PowerTransformer(method="box-cox", standardize=True)
X_bc = pt_bc.fit_transform(X_train_positive)
```

El parámetro `standardize=True` aplica adicionalmente una estandarización tras la transformación de potencia.

| Escalador | Rango resultado | Robusto a outliers | Preserva distribución | Requiere valores positivos |
|---|---|---|---|---|
| StandardScaler | Ilimitado | No | Sí | No |
| MinMaxScaler | [0, 1] | No | Sí | No |
| RobustScaler | Ilimitado | Sí | Sí | No |
| Box-Cox | Ilimitado | No | Normaliza | Sí (>0) |
| Yeo-Johnson | Ilimitado | No | Normaliza | No |

---

## 4. Ingeniería de características (Feature Engineering)

La ingeniería de características es el proceso de usar conocimiento del dominio y análisis estadístico para crear, transformar o seleccionar las variables de entrada que mejor representen el problema subyacente para un algoritmo de aprendizaje. Goodfellow et al. (2016) la describen como la parte del aprendizaje profundo que más depende del conocimiento humano. En datos tabulares, sigue siendo una de las palancas más potentes para mejorar el rendimiento de cualquier modelo.

### 4.1 Creación de características derivadas

Las características derivadas son combinaciones algebraicas de variables existentes que expresan relaciones que el modelo tendría dificultades para descubrir por sí solo, especialmente modelos lineales.

Ejemplos habituales incluyen: ratios (precio por metro cuadrado = precio / superficie), diferencias (variación de ventas respecto al mes anterior), proporciones (porcentaje de clics sobre impresiones), y combinaciones de variables de texto (longitud de un campo, presencia de palabras clave).

```python
import pandas as pd

# Ratio
df["precio_m2"] = df["precio"] / df["superficie"]

# Diferencia temporal
df["variacion_ventas"] = df["ventas_mes"] - df["ventas_mes_anterior"]

# Flag booleano
df["es_fin_de_semana"] = df["dia_semana"].isin([5, 6]).astype(int)
```

La creación de características derivadas requiere comprensión del dominio. Sin ella, se corre el riesgo de generar ruido o multicolinealidad. Herramientas como `PolynomialFeatures` de scikit-learn generan todas las interacciones hasta un grado dado de forma automática, pero el número de columnas crece combinatoriamente.

### 4.2 Extracción de características temporales

Las variables de tipo datetime contienen múltiples señales latentes: el año, el mes, el día de la semana, la hora, si es festivo, si es fin de mes, la distancia temporal a un evento de referencia, etc. Extraer estas señales de forma explícita permite que los modelos lineales o los árboles de decisión las utilicen directamente.

```python
import pandas as pd

df["fecha"] = pd.to_datetime(df["fecha"])

df["año"]           = df["fecha"].dt.year
df["mes"]           = df["fecha"].dt.month
df["dia_semana"]    = df["fecha"].dt.dayofweek
df["dia_año"]       = df["fecha"].dt.dayofyear
df["semana_año"]    = df["fecha"].dt.isocalendar().week.astype(int)
df["es_fin_semana"] = (df["fecha"].dt.dayofweek >= 5).astype(int)

# Codificación cíclica del mes (preserva la continuidad entre diciembre y enero)
import numpy as np
df["mes_sin"] = np.sin(2 * np.pi * df["mes"] / 12)
df["mes_cos"] = np.cos(2 * np.pi * df["mes"] / 12)
```

La codificación cíclica mediante seno y coseno es especialmente importante para variables periódicas como el mes, el día de la semana o la hora del día: garantiza que diciembre (mes 12) y enero (mes 1) sean percibidos como próximos por el modelo.

### 4.3 Interacciones entre variables

Las interacciones capturan el efecto conjunto de dos o más variables que no puede describirse como la suma de sus efectos individuales. Por ejemplo, el efecto del precio sobre las ventas puede depender del segmento de cliente.

`PolynomialFeatures` de scikit-learn genera automáticamente todas las interacciones hasta el grado especificado:

```python
from sklearn.preprocessing import PolynomialFeatures

poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
X_int = poly.fit_transform(X)
print(poly.get_feature_names_out())
```

Con `interaction_only=True` se generan solo los productos cruzados, sin elevar ninguna variable al cuadrado. Para datasets con muchas features, el número de interacciones de grado 2 es n*(n-1)/2, lo que puede hacer el dataset inmanejable; en ese caso conviene seleccionar manualmente las interacciones más relevantes.

### 4.4 Técnicas de binning y discretización

El binning convierte una variable continua en una categórica asignando cada valor a un intervalo o cubo (bin). Puede ser útil para capturar relaciones no lineales con modelos lineales, para reducir el efecto de outliers, o cuando se tiene conocimiento del dominio que sugiere umbrales naturales (por ejemplo, grupos de edad).

scikit-learn ofrece `KBinsDiscretizer` con tres estrategias: `uniform` (bins de igual anchura), `quantile` (bins con igual número de muestras, recomendado por defecto) y `kmeans` (bins centrados en los centroides de k-means).

```python
from sklearn.preprocessing import KBinsDiscretizer

kbd = KBinsDiscretizer(n_bins=5, encode="ordinal", strategy="quantile")
X_binned = kbd.fit_transform(X[["edad"]])
```

Con `encode="onehot"` se genera una representación OHE directamente. Con `encode="ordinal"` se obtiene un entero representando el bin, que puede usarse directamente con árboles de decisión.

---

## 5. Reducción de dimensionalidad

La maldición de la dimensionalidad (Bellman, 1957) describe el fenómeno por el cual el volumen del espacio de características crece exponencialmente con el número de dimensiones, haciendo que los datos disponibles sean cada vez más escasos y las distancias entre puntos cada vez menos informativas. La reducción de dimensionalidad aborda este problema proyectando los datos a un espacio de menor dimensión que preserve la estructura relevante.

### 5.1 PCA: fundamentos y aplicación

El Análisis de Componentes Principales (PCA) es la técnica de reducción lineal de dimensionalidad más utilizada. Encuentra las direcciones de máxima varianza en los datos (los componentes principales), que son combinaciones lineales ortogonales de las variables originales, y proyecta los datos sobre un subespacio de menor dimensión formado por los primeros k componentes.

Matemáticamente, PCA resuelve el problema de la descomposición espectral de la matriz de covarianza: los vectores propios de mayor valor propio son los componentes principales, y los valores propios indican qué proporción de la varianza total explica cada componente.

```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import numpy as np

# Escalar antes de PCA es fundamental
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)

# PCA para retener el 95% de la varianza
pca = PCA(n_components=0.95, random_state=42)
X_pca = pca.fit_transform(X_scaled)

print(f"Dimensiones originales: {X_scaled.shape[1]}")
print(f"Dimensiones tras PCA:   {X_pca.shape[1]}")

# Visualizar la varianza explicada acumulada
varianza_acumulada = np.cumsum(pca.explained_variance_ratio_)
plt.plot(varianza_acumulada)
plt.xlabel("Número de componentes")
plt.ylabel("Varianza explicada acumulada")
plt.axhline(0.95, color="red", linestyle="--")
plt.grid(True)
plt.show()
```

PCA tiene importantes restricciones: solo captura estructura lineal, los componentes no son interpretables en términos de las variables originales, y es sensible a la escala (de ahí la necesidad de estandarizar previamente).

### 5.2 t-SNE y UMAP para visualización

Cuando el objetivo es visualizar datos de alta dimensión en 2 o 3 dimensiones para exploración o comunicación, las técnicas no lineales producen resultados mucho más informativos que PCA.

**t-SNE** (t-Distributed Stochastic Neighbor Embedding, van der Maaten y Hinton, 2008) modela las similitudes entre puntos como distribuciones de probabilidad: similitudes altas en el espacio original deben corresponder a proximidades en el espacio reducido. El algoritmo minimiza la divergencia KL entre las distribuciones en ambos espacios. t-SNE es excelente para revelar clústeres, pero sus hiperparámetros (especialmente `perplexity`) afectan mucho al resultado, y las distancias globales entre clústeres no son interpretables.

```python
from sklearn.manifold import TSNE

tsne = TSNE(n_components=2, perplexity=30, n_iter=1000, random_state=42)
X_tsne = tsne.fit_transform(X_scaled)
```

**UMAP** (Uniform Manifold Approximation and Projection, McInnes et al., 2018) es una alternativa más moderna que generalmente produce visualizaciones de calidad comparable a t-SNE pero en menor tiempo y con mejor preservación de la estructura global. Requiere la biblioteca `umap-learn`.

```python
import umap

reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, random_state=42)
X_umap = reducer.fit_transform(X_scaled)
```

Tanto t-SNE como UMAP son técnicas de exploración, no de preprocesamiento para modelos: proyectar los datos de test en el espacio t-SNE/UMAP ajustado en entrenamiento no produce representaciones comparables, y en todo caso la naturaleza estocástica del proceso hace que los embeddings no sean estables entre ejecuciones.

### 5.3 Selección de características: filtros, envolturas, embebidos

La selección de características elige un subconjunto de las variables originales (sin combinarlas), lo que preserva la interpretabilidad. Se distinguen tres familias de métodos:

**Métodos de filtro.** Evalúan cada característica de forma independiente usando una métrica estadística. Son rápidos pero ignoran las interacciones entre variables. Ejemplos: correlación de Pearson (para regresión), chi-cuadrado (para clasificación con variables discretas), ANOVA F-score, información mutua.

```python
from sklearn.feature_selection import SelectKBest, mutual_info_classif

selector = SelectKBest(score_func=mutual_info_classif, k=20)
X_filtered = selector.fit_transform(X_train, y_train)
selected_features = X_train.columns[selector.get_support()]
```

**Métodos de envoltura (wrapper).** Evalúan subconjuntos de características entrenando un modelo completo sobre cada uno. Producen mejores resultados que los filtros pero son computacionalmente costosos. La eliminación recursiva de características (`RFE`) itera eliminando la característica menos importante en cada paso.

```python
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rfe = RFE(estimator=rf, n_features_to_select=20, step=1)
rfe.fit(X_train, y_train)
X_rfe = rfe.transform(X_train)
```

**Métodos embebidos.** La selección ocurre como parte del propio proceso de entrenamiento del modelo. La regularización L1 (Lasso) lleva a cero los coeficientes de variables irrelevantes. Los modelos basados en árboles calculan importancias de características que pueden usarse para selección.

```python
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import LassoCV

lasso = LassoCV(cv=5, random_state=42)
selector = SelectFromModel(lasso, threshold="mean")
selector.fit(X_train, y_train)
X_lasso = selector.transform(X_train)
```

---

## 6. Partición del conjunto de datos

La partición del conjunto de datos es el paso que determina si las métricas de evaluación del modelo son creíbles o ilusorias. Un modelo evaluado sobre datos que ha visto durante el entrenamiento (aunque sea indirectamente, a través del preprocesamiento) siempre parecerá mejor de lo que realmente es.

### 6.1 Split train/validation/test: proporciones y criterios

La división más común en proyectos de tamaño medio es en tres conjuntos: entrenamiento (train), validación (validation) y test. El conjunto de entrenamiento se usa para ajustar los parámetros del modelo; el de validación para seleccionar hiperparámetros y arquitecturas; el de test para obtener una estimación final e imparcial del rendimiento, y debe usarse una sola vez.

Las proporciones habituales son 70/15/15 o 60/20/20 para el reparto train/validation/test. Con datasets grandes (millones de muestras), proporciones de 98/1/1 son razonables, ya que incluso un 1% puede ser una muestra estadísticamente suficiente para la evaluación.

```python
from sklearn.model_selection import train_test_split

X_train_val, X_test, y_train_val, y_test = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y
)

X_train, X_val, y_train, y_val = train_test_split(
    X_train_val, y_train_val, test_size=0.176, random_state=42, stratify=y_train_val
)
# 0.176 * 0.85 ≈ 0.15, lo que da proporciones globales ~70/15/15
```

El parámetro `stratify=y` garantiza que la proporción de clases en cada partición sea similar a la del dataset original. Es esencial para clasificación con clases desbalanceadas.

### 6.2 Validación cruzada: k-fold, stratified k-fold, group k-fold

La validación cruzada resuelve el problema de la varianza de la estimación asociada a una sola división train/validation: al promediar el rendimiento sobre k particiones diferentes, la estimación es más estable.

**K-Fold.** Divide el dataset en k partes iguales. En cada iteración, una parte actúa como validación y las k-1 restantes como entrenamiento. Al final se promedian los k scores.

```python
from sklearn.model_selection import KFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier

cv = KFold(n_splits=5, shuffle=True, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="f1_weighted")
print(f"F1 medio: {scores.mean():.4f} ± {scores.std():.4f}")
```

**Stratified K-Fold.** Preserva la proporción de clases en cada fold. Es la opción correcta para clasificación, especialmente con clases desbalanceadas.

**Group K-Fold.** Garantiza que todas las muestras del mismo grupo (por ejemplo, todas las mediciones del mismo paciente, o todas las transacciones del mismo cliente) caen en el mismo fold. Evita que el modelo "aprenda" un grupo en entrenamiento y lo evalúe en validación, lo que sería una forma de fuga de información.

```python
from sklearn.model_selection import GroupKFold

gkf = GroupKFold(n_splits=5)
for train_idx, val_idx in gkf.split(X, y, groups=df["patient_id"]):
    X_tr, X_v = X[train_idx], X[val_idx]
    y_tr, y_v = y[train_idx], y[val_idx]
```

Valores habituales de k son 5 y 10. Con datasets pequeños, se puede usar Leave-One-Out (LOO), que es k-fold con k=n, aunque tiene alta varianza.

### 6.3 Evitando data leakage: pipelines correctos con sklearn

La fuga de información (data leakage) ocurre cuando información del conjunto de validación o test influye en el proceso de entrenamiento. Las fuentes más comunes son: aplicar `fit_transform` sobre todo el dataset antes de dividirlo (contamina los escaladores y los imputadores), usar el target futuro como feature (en series temporales), e incluir características que son consecuencia del target (no causas).

La solución estándar en scikit-learn es encapsular todo el preprocesamiento en un `Pipeline`, de forma que cada fold de la validación cruzada aplique el `fit` solo sobre los datos de entrenamiento de ese fold:

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

# Definir preprocesadores por tipo de variable
numeric_features = ["edad", "ingresos", "superficie"]
categorical_features = ["ciudad", "categoria"]

numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(drop="first", handle_unknown="ignore"))
])

preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer, numeric_features),
    ("cat", categorical_transformer, categorical_features)
])

# Pipeline completo: preprocesamiento + modelo
pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", GradientBoostingClassifier(n_estimators=100, random_state=42))
])

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="roc_auc")
print(f"AUC-ROC: {scores.mean():.4f} ± {scores.std():.4f}")
```

Este pipeline garantiza que los parámetros del escalador, el imputador y el encoder se ajustan únicamente sobre los datos de entrenamiento de cada fold. Es la forma correcta de usar validación cruzada con preprocesamiento.

### 6.4 Partición temporal para series de tiempo

Con datos temporales, la división aleatoria de observaciones viola el principio fundamental de que el modelo solo puede usar información del pasado para predecir el futuro. Si se toman muestras aleatorias de la serie completa para validación, el modelo puede "ver el futuro" durante el entrenamiento, produciendo estimaciones de rendimiento irrealmente optimistas.

La solución es la validación cruzada temporal (*time series split*), que garantiza que los datos de entrenamiento en cada fold siempre son temporalmente anteriores a los de validación.

```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)

for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
    X_tr, X_v = X.iloc[train_idx], X.iloc[val_idx]
    y_tr, y_v = y.iloc[train_idx], y.iloc[val_idx]
    print(f"Fold {fold+1}: train [{train_idx[0]}:{train_idx[-1]}] "
          f"val [{val_idx[0]}:{val_idx[-1]}]")
```

En cada fold, el conjunto de entrenamiento crece añadiendo los datos del fold anterior (expanding window). Una variante es la ventana deslizante (sliding window), donde el tamaño del conjunto de entrenamiento se mantiene constante, útil para capturar dinámicas que cambian con el tiempo.

Adicionalmente, en series temporales hay que considerar el efecto de las features rezagadas: si se crea una feature `ventas_lag_1` (ventas del día anterior), hay que asegurarse de que esa información estaba disponible en el momento de la predicción y no constituye fuga hacia el futuro.

---

## Actividades prácticas propuestas

**Actividad 1: Análisis y tratamiento de valores faltantes en el dataset Titanic.**
Cargar el dataset Titanic de la biblioteca `seaborn` o de Kaggle. Analizar el patrón de missing values con `missingno`. Implementar y comparar tres estrategias de imputación para la columna `Age`: media, mediana e IterativeImputer. Evaluar el impacto de cada estrategia sobre la distribución resultante con histogramas y sobre el rendimiento de un clasificador de regresión logística con validación cruzada (5-fold stratified).

**Actividad 2: Codificación de variables categóricas en el dataset Ames Housing.**
Descargar el dataset Ames Housing (disponible en Kaggle). Identificar variables nominales, ordinales y de alta cardinalidad. Aplicar OHE a variables nominales con cardinalidad baja (<10 categorías), OrdinalEncoder a variables ordinales respetando el orden natural, y Target Encoding con validación cruzada a la variable `Neighborhood` (alta cardinalidad). Comparar el rendimiento de un modelo de regresión con Ridge con cada estrategia de codificación.

**Actividad 3: Construcción de un pipeline completo sin data leakage.**
Usando el dataset de la Actividad 2, construir un `Pipeline` de scikit-learn que integre todas las transformaciones (imputación, codificación, escalado) y un modelo de GradientBoosting. Demostrar que el pipeline evita data leakage ejecutando la validación cruzada correctamente y comparando los resultados con una implementación incorrecta donde el preprocesamiento se aplica antes de la división.

**Actividad 4: Reducción de dimensionalidad y visualización.**
Usar el dataset MNIST (disponible en `sklearn.datasets.fetch_openml`) o el dataset de dígitos de sklearn. Aplicar PCA reteniendo el 95% de la varianza. Visualizar los 2 primeros componentes coloreados por clase. Aplicar t-SNE y UMAP sobre los 50 primeros componentes PCA (no directamente sobre los píxeles, para reducir tiempo de cómputo). Comparar las tres visualizaciones y discutir la calidad de la separación de clases.

**Actividad 5: Validación cruzada temporal para predicción de ventas.**
Construir un dataset sintético de ventas diarias con pandas (`pd.date_range`). Crear features temporales: día de la semana, mes, ventas rezagadas 7 días. Implementar TimeSeriesSplit con 5 folds. Comparar el error (MAE) obtenido con TimeSeriesSplit versus KFold aleatorio sobre los mismos datos, y discutir por qué los resultados difieren.

---

## Referencias y material externo

### Libros

- Géron, A. (2022). *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow* (3ª ed.). O'Reilly Media. Capítulos 2 y 8 son especialmente relevantes para esta unidad.

- McKinney, W. (2022). *Python for Data Analysis* (3ª ed.). O'Reilly Media. Referencia principal para manipulación de datos con pandas.

- Kuhn, M., & Johnson, K. (2019). *Feature Engineering and Selection: A Practical Approach for Predictive Models*. CRC Press. Disponible en abierto en: https://bookdown.org/max/FES/

- Molnar, C. (2022). *Interpretable Machine Learning* (2ª ed.). Disponible en abierto en: https://christophm.github.io/interpretable-ml-book/

- Little, R. J. A., & Rubin, D. B. (2019). *Statistical Analysis with Missing Data* (3ª ed.). Wiley.

### Documentación oficial

- scikit-learn: Preprocessing data — https://scikit-learn.org/stable/modules/preprocessing.html

- scikit-learn: Imputation of missing values — https://scikit-learn.org/stable/modules/impute.html

- scikit-learn: Feature selection — https://scikit-learn.org/stable/modules/feature_selection.html

- scikit-learn: Cross-validation — https://scikit-learn.org/stable/modules/cross_validation.html

- scikit-learn: Pipeline — https://scikit-learn.org/stable/modules/compose.html

- pandas: Time series / date functionality — https://pandas.pydata.org/docs/user_guide/timeseries.html

### Papers y recursos académicos

- van der Maaten, L., & Hinton, G. (2008). Visualizing Data using t-SNE. *Journal of Machine Learning Research*, 9, 2579-2605. Disponible en: https://jmlr.org/papers/v9/vandermaaten08a.html

- McInnes, L., Healy, J., & Melville, J. (2018). UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction. *arXiv*:1802.03426. Disponible en: https://arxiv.org/abs/1802.03426

- Cerda, P., Varoquaux, G., & Kégl, B. (2018). Similarity encoding for learning with dirty categorical variables. *Machine Learning*, 107(8), 1477-1494. Disponible en: https://link.springer.com/article/10.1007/s10994-018-5724-2

- Dorogush, A. V., Ershov, V., & Gulin, A. (2018). CatBoost: gradient boosting with categorical features support. *arXiv*:1810.11363. Disponible en: https://arxiv.org/abs/1810.11363

### Recursos en línea

- Kaggle Learn — Feature Engineering: https://www.kaggle.com/learn/feature-engineering

- Towards Data Science — A Comprehensive Guide to Data Preprocessing: https://towardsdatascience.com/data-preprocessing-concepts-fa946d11c825

- Documentación de `category_encoders`: https://contrib.scikit-learn.org/category_encoders/

- Documentación de `missingno`: https://github.com/ResidentMario/missingno

- UMAP documentation: https://umap-learn.readthedocs.io/en/latest/
