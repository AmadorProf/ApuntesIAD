---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD3 · Verificación de la calidad de los datos | MP01 · Procesamiento de datos para IA'
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

# UD3 · Verificación de la calidad de los datos

**MP01 · Procesamiento de datos para IA**
CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de aprendizaje

Al finalizar esta unidad el alumno será capaz de:

- Aplicar técnicas estadísticas formales de evaluación de la calidad de un conjunto de datos
- Analizar cobertura, distribución, equilibrio entre clases y duplicidades
- Detectar y caracterizar valores atípicos mediante métodos estadísticos y de aprendizaje automático
- Identificar y describir sesgos que pueden afectar a la equidad del modelo
- Verificar la coherencia de etiquetas y anotaciones entre registros y entre anotadores
- Documentar los resultados de la verificación de calidad con el formato requerido
- Justificar el impacto de la calidad de los datos sobre el rendimiento del modelo

---

## Por qué la calidad de datos es crítica en IA

```
Regla fundamental del modelado:
"Garbage In, Garbage Out" (GIGO)

Calidad del dato  →  Calidad del modelo  →  Calidad de la decisión
─────────────────     ────────────────────     ───────────────────
Alta calidad          Modelo fiable            Decisiones correctas
Baja calidad          Modelo sesgado           Decisiones erróneas
                      o sobreajustado          con consecuencias reales
```

**Consecuencias reales de datos de mala calidad:**
- Un modelo de crédito entrenado con datos sesgados discrimina por código postal
- Un modelo médico entrenado con datos de baja cobertura falla en poblaciones minoritarias
- Un modelo de fraude entrenado con datos desbalanceados ignora el 0,1% de casos positivos reales

> La verificación de calidad no es una revisión técnica: es una responsabilidad ética y profesional.

---

## Las dimensiones de la calidad de datos

| Dimensión | Definición | Pregunta clave |
|---|---|---|
| **Cobertura** | % de valores presentes vs. esperados | ¿Hay huecos? ¿Cuántos? |
| **Exactitud** | Grado de correspondencia con la realidad | ¿El valor es correcto? |
| **Consistencia** | Coherencia interna entre campos relacionados | ¿Los campos se contradicen? |
| **Unicidad** | Ausencia de registros duplicados | ¿Hay registros repetidos? |
| **Oportunidad** | Datos actualizados para el contexto de uso | ¿Son lo bastante recientes? |
| **Distribución** | Representatividad estadística del conjunto | ¿Las clases están equilibradas? |
| **Equidad** | Representación adecuada de todos los grupos | ¿Hay grupos subrepresentados? |

---

## Análisis de cobertura: valores ausentes

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_parquet("dataset.parquet")

# Análisis completo de nulos
nulos = pd.DataFrame({
    "absolutos": df.isnull().sum(),
    "porcentaje": (df.isnull().sum() / len(df) * 100).round(2)
}).sort_values("porcentaje", ascending=False)

print(nulos[nulos["porcentaje"] > 0])

# Decisiones según porcentaje de nulos
def decision_nulos(pct):
    if pct > 60:   return "Eliminar columna"
    if pct > 20:   return "Imputación avanzada o flag binario"
    if pct > 5:    return "Imputación estadística (media/mediana/moda)"
    return "Imputación simple o eliminación de filas"

nulos["decision"] = nulos["porcentaje"].apply(decision_nulos)
print(nulos)
```

---

## Patrones de valores ausentes: MCAR, MAR, MNAR

Antes de imputar, es necesario entender **por qué** faltan los datos:

| Mecanismo | Definición | Implicación |
|---|---|---|
| **MCAR** (Missing Completely At Random) | La ausencia es aleatoria, no depende de ninguna variable | Imputación estadística válida |
| **MAR** (Missing At Random) | La ausencia depende de otras variables observadas | Imputación condicional |
| **MNAR** (Missing Not At Random) | La ausencia depende del propio valor no observado | Riesgo de sesgo en la imputación |

**Ejemplo MNAR:** en una encuesta de salario, los salarios más altos tienden a no responderse. Imputar con la media introduce un sesgo sistemático hacia la baja.

```python
# Test de Little (MCAR) disponible en pyampute
# Para MAR/MNAR: analizar si la ausencia correlaciona con otras variables
df["flag_nulo_salario"] = df["salario"].isnull().astype(int)
print(df.groupby("flag_nulo_salario")["edad"].mean())
# Si hay diferencia significativa → probable MAR o MNAR
```

---

## Detección de outliers: métodos estadísticos

### Método IQR (rango intercuartílico)

```python
def detectar_outliers_iqr(serie, factor=1.5):
    Q1 = serie.quantile(0.25)
    Q3 = serie.quantile(0.75)
    IQR = Q3 - Q1
    limite_inf = Q1 - factor * IQR
    limite_sup = Q3 + factor * IQR
    return (serie < limite_inf) | (serie > limite_sup)

# Aplicar a todas las columnas numéricas
for col in df.select_dtypes("number").columns:
    mask = detectar_outliers_iqr(df[col])
    n = mask.sum()
    pct = mask.mean() * 100
    if n > 0:
        print(f"{col}: {n} outliers ({pct:.2f}%) — "
              f"rango normal [{df[col].quantile(.25):.2f}, {df[col].quantile(.75):.2f}]")
```

**Referencia:** con factor=1.5 se detectan outliers "moderados"; con factor=3.0 se detectan outliers "extremos".

---

## Detección de outliers: métodos de aprendizaje automático

Para datos multivariantes, los métodos estadísticos univariantes pueden ser insuficientes.

| Método | Tipo | Fortaleza | Caso de uso |
|---|---|---|---|
| **Z-Score** | Estadístico | Simple, interpretable | Distribuciones normales |
| **IQR** | Estadístico | Robusto, no asume normalidad | General |
| **Isolation Forest** | ML no supervisado | Escala bien, datos de alta dimensión | Big data |
| **Local Outlier Factor (LOF)** | ML basado en densidad | Detecta outliers locales | Clusters con distintas densidades |
| **Elliptic Envelope** | Estadístico multivariante | Asume distribución gaussiana | Datos bien distribuidos |
| **DBSCAN** | Clustering | Detecta puntos de ruido | Datos con clusters naturales |

```python
from sklearn.ensemble import IsolationForest

X = df.select_dtypes("number").dropna()
iso = IsolationForest(contamination=0.05, random_state=42)
df["outlier_if"] = iso.fit_predict(X)
# -1 = outlier, 1 = normal
print(f"Outliers detectados: {(df['outlier_if'] == -1).sum():,}")
```

---

## Análisis del equilibrio entre clases

El desequilibrio de clases es uno de los problemas más frecuentes y más ignorados en proyectos de IA.

```python
# Análisis de distribución de clases
target = "diagnostico"
distribucion = df[target].value_counts()
pct = df[target].value_counts(normalize=True) * 100

resumen = pd.DataFrame({
    "Frecuencia": distribucion,
    "Porcentaje": pct.round(2)
})
print(resumen)

# Ratio de desequilibrio
clase_mayoritaria = distribucion.max()
clase_minoritaria = distribucion.min()
ratio = clase_mayoritaria / clase_minoritaria
print(f"\nRatio mayoría/minoría: {ratio:.1f}:1")

# Clasificación del nivel de desequilibrio
if ratio < 3:    print("Equilibrio aceptable")
elif ratio < 10: print("Desequilibrio moderado — considerar rebalanceo")
elif ratio < 100: print("Desequilibrio severo — rebalanceo obligatorio")
else:             print("Desequilibrio extremo — revisar proceso de captura")
```

---

## Impacto del desequilibrio sobre el modelo

### Por qué un accuracy del 99% puede ser inútil

```
Dataset de detección de fraude:
- 99.000 transacciones normales  (99%)
- 1.000 transacciones fraudulentas (1%)

Modelo trivial: "Todo es normal"
- Accuracy: 99%  ← parece excelente
- Recall de fraude: 0%  ← detecta CERO fraudes
- Precisión de fraude: N/A

Métricas adecuadas para clases desbalanceadas:
- F1-score (balance precisión-recall)
- AUC-ROC (rendimiento a distintos umbrales)
- Precisión-Recall AUC (para clases muy minoritarias)
- Matriz de confusión completa
```

> La verificación de calidad debe incluir un informe sobre el equilibrio de clases y su impacto previsto en las métricas de evaluación del modelo.

---

## Equidad y fiabilidad: sesgos en los datos

### Tipos de sesgo que deben documentarse

| Tipo de sesgo | Descripción | Ejemplo concreto |
|---|---|---|
| **Sesgo de selección** | Los datos no representan a toda la población objetivo | Dataset médico con solo pacientes hospitalizados |
| **Sesgo de cobertura** | Infrarepresentación de subgrupos | Datos de reconocimiento facial sin diversidad étnica |
| **Sesgo de etiquetado** | Sesgos del anotador reflejados en las etiquetas | Anotadores de un mismo perfil cultural |
| **Sesgo temporal** | Los datos pasados no reflejan el comportamiento futuro | Datos de 2019 para predecir comportamiento post-pandemia |
| **Sesgo de medición** | El instrumento de captura afecta sistemáticamente | Sensor descalibrado que subestima sistemáticamente |
| **Sesgo de confirmación** | Se recogen datos que confirman hipótesis previas | Selección no aleatoria de casos a estudiar |

---

## Variables sensibles y fuga de información

### Variables sensibles (atributos protegidos)

Son variables cuyo uso en el modelado puede producir discriminación:
- Género, edad, origen étnico, religión, orientación sexual
- Código postal (proxy geográfico que puede correlacionar con etnia o nivel económico)
- Nombre propio (puede inferir género u origen)

```python
# Detección de posibles proxies de variables sensibles
variables_sensibles = ["genero", "edad", "codigo_postal", "nombre", "apellidos"]
for v in variables_sensibles:
    if v in df.columns:
        print(f"ALERTA: variable sensible detectada → '{v}'")
        print(f"  Correlación con target: {df[v].corr(df[target]):.3f}")
```

### Data leakage (fuga de información)
Ocurre cuando el modelo recibe durante el entrenamiento información que no estará disponible en producción.

```
Ejemplo: incluir la variable "fecha_alta" para predecir si el paciente es readmitido.
La fecha de alta solo se conoce cuando el paciente ya ha salido → no disponible en el momento de la predicción.
```

---

## Verificación de coherencia interna

### Reglas de negocio que deben validarse

```python
# Reglas de coherencia que pueden implementarse como validaciones
reglas = {
    "Edad positiva":
        df["edad"] >= 0,
    "Fecha alta posterior a ingreso":
        df["fecha_alta"] >= df["fecha_ingreso"],
    "Temperatura corporal en rango fisiológico":
        df["temperatura"].between(34, 43),
    "Presión arterial diastólica < sistólica":
        df["presion_diastolica"] < df["presion_sistolica"],
    "Puntuacion entre 0 y 100":
        df["puntuacion"].between(0, 100)
}

for descripcion, condicion in reglas.items():
    violaciones = (~condicion).sum()
    if violaciones > 0:
        print(f"VIOLACION [{descripcion}]: {violaciones:,} registros")
    else:
        print(f"OK: {descripcion}")
```

---

## Verificación de duplicados

### Tipos de duplicados y cómo detectarlos

```python
# 1. Duplicados exactos (todas las columnas iguales)
dup_exactos = df.duplicated().sum()
print(f"Duplicados exactos: {dup_exactos:,}")

# 2. Duplicados por clave de negocio (no por todas las columnas)
clave_negocio = ["id_paciente", "fecha_visita"]
dup_clave = df.duplicated(subset=clave_negocio).sum()
print(f"Duplicados por clave ({clave_negocio}): {dup_clave:,}")

# 3. Duplicados casi exactos (fuzzy matching para texto)
# Requiere dedupe o recordlinkage
# Útil cuando el mismo registro tiene ligeras variaciones de texto

# 4. Ver los duplicados para inspeccionarlos
mask_dup = df.duplicated(subset=clave_negocio, keep=False)
duplicados = df[mask_dup].sort_values(clave_negocio)
print(f"\nEjemplos de duplicados por clave de negocio:")
print(duplicados.head(6))
```

---

## Verificación de etiquetas y anotaciones

### Coherencia del etiquetado en aprendizaje supervisado

```python
# 1. Etiquetas válidas: solo valores esperados
valores_validos = {"positivo", "negativo", "neutro"}
etiquetas_invalidas = ~df["sentimiento"].isin(valores_validos)
print(f"Etiquetas fuera del catálogo: {etiquetas_invalidas.sum()}")

# 2. Distribución de etiquetas por anotador (si hay múltiples)
if "anotador_id" in df.columns:
    dist_anotador = df.groupby("anotador_id")["etiqueta"].value_counts(normalize=True)
    print("\nDistribución por anotador:")
    print(dist_anotador.unstack())
    # Si hay diferencias marcadas → sesgo del anotador

# 3. Tasa de acuerdo entre anotadores (Cohen's Kappa)
from sklearn.metrics import cohen_kappa_score
kappa = cohen_kappa_score(df["anotador_1"], df["anotador_2"])
print(f"\nCohen's Kappa: {kappa:.3f}")
# > 0.8: acuerdo casi perfecto | 0.6-0.8: sustancial | < 0.4: pobre
```

---

## Documentación de los resultados de calidad

### Informe de calidad del conjunto

| Dimensión | Indicador medido | Resultado | Decisión |
|---|---|---|---|
| Cobertura | % nulos por columna | Columna X: 45% nulos | Imputación con mediana |
| Unicidad | Duplicados por clave | 1.230 duplicados (0,4%) | Eliminar conservando el más reciente |
| Distribución | Ratio clases | 15:1 (mayoría/minoría) | SMOTE en fase de preprocesamiento |
| Outliers | IQR + Isolation Forest | 2,3% de registros | Investigar: 60% errores, 40% reales |
| Consistencia | Reglas de negocio | 87 violaciones fecha | Investigar y corregir o eliminar |
| Equidad | Distribución por género | 78% masculino / 22% femenino | Documentar limitación del modelo |
| Etiquetado | Cohen's Kappa | 0,72 | Aceptable, revisar casos ambiguos |

---

## Herramientas de validación de calidad

| Herramienta | Capacidad principal | Nivel |
|---|---|---|
| **Great Expectations** | Define expectativas de datos como tests automatizables | Producción |
| **Pandera** | Validación de esquemas y tipos en DataFrames Pandas | Desarrollo |
| **Soda Core** | Monitorización de calidad en pipelines de datos | Producción |
| **deequ** (AWS) | Validación de calidad a escala con Spark | Big data |
| **TFDV** (TensorFlow) | Validación de datos para pipelines de ML | ML pipelines |
| **Evidently AI** | Detección de drift y calidad en producción | MLOps |

```python
# Ejemplo con Pandera: validación de esquema
import pandera as pa

schema = pa.DataFrameSchema({
    "edad":    pa.Column(float, pa.Check.between(0, 120)),
    "salario": pa.Column(float, pa.Check.ge(0)),
    "genero":  pa.Column(str, pa.Check.isin(["M", "F", "NB", "NC"]))
})
schema.validate(df)  # lanza excepción si falla
```

---

## Actividad práctica — UD3

### Auditoría de calidad de un conjunto de datos

**Dataset:** `credit_scoring.csv` (dataset de clasificación de riesgo crediticio)

**Tareas:**

1. Calcular la cobertura de cada columna y clasificar las columnas por nivel de nulos (umbral: <5%, 5-20%, 20-60%, >60%)
2. Detectar outliers en las variables numéricas usando IQR y clasificarlos como posibles errores o valores extremos reales
3. Analizar el equilibrio entre la clase positiva (impago) y la negativa (pago correcto) y calcular el ratio
4. Identificar al menos dos posibles variables sensibles o proxies y documentar su correlación con el target
5. Verificar tres reglas de coherencia de negocio del dominio crediticio
6. Completar el informe de calidad con el formato de la tabla de la diapositiva anterior
7. Redactar una recomendación de uso del conjunto: ¿es apto para modelado? ¿con qué limitaciones?

---

## Puntos clave — UD3

- **La calidad tiene siete dimensiones:** cobertura, exactitud, consistencia, unicidad, oportunidad, distribución y equidad deben medirse formalmente
- **Los outliers no siempre son errores:** antes de eliminarlos hay que investigar si representan fenómenos reales del dominio
- **El desequilibrio de clases sesga las métricas:** un accuracy alto con clases desbalanceadas es frecuentemente engañoso; usar F1, AUC-ROC o PR-AUC
- **Los sesgos en los datos producen modelos discriminatorios:** identificar y documentar variables sensibles y subrepresentación es una obligación profesional
- **La fuga de información invalida el modelo:** detectar data leakage en fase de verificación evita construir modelos que no funcionan en producción
- **Los resultados de calidad deben documentarse:** el informe de calidad es el insumo para las decisiones de preprocesamiento de UD4

---

## Criterios de evaluación — UD3

- Aplica técnicas estadísticas de evaluación de la calidad según las especificaciones del análisis
- Detecta y cuantifica valores atípicos, sesgos y duplicidades con métodos apropiados
- Analiza el equilibrio entre clases y su impacto previsto sobre el rendimiento del modelo
- Identifica variables sensibles y posibles casos de fuga de información entre conjuntos
- Verifica la coherencia de etiquetas y anotaciones con métricas de acuerdo entre anotadores
- Documenta los resultados de cobertura, distribución, sesgos y verificaciones para la toma de decisiones de modelado

---

<!-- _class: lead -->

[← Volver a MP01](../)
