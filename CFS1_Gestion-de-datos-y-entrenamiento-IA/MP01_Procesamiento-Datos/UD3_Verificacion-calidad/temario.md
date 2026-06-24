# UD3 · Verificación de la calidad de los datos

**Módulo:** MP01 · Procesamiento de datos para IA
**Programa:** CFS1 — Gestión de datos y entrenamiento IA
**Nivel:** CFS Nivel 3 · Inteligencia Artificial y Datos

---

## Introducción

La calidad de los datos no es un requisito accesorio en los proyectos de inteligencia artificial: es la condición necesaria para que cualquier modelo aprenda patrones reales en lugar de ruido, errores o sesgos artificialmente introducidos por el proceso de recolección y almacenamiento. El adagio habitual en la comunidad —"garbage in, garbage out"— resume con exactitud lo que sucede cuando un equipo invierte semanas en afinar la arquitectura de una red neuronal mientras ignora que un veinte por ciento de los registros tienen valores incorrectos o duplicados.

Esta unidad estudia de forma sistemática qué significa que un conjunto de datos sea de calidad, cómo detectar las distintas formas en que esa calidad se degrada y qué herramientas de la industria permiten automatizar su vigilancia en pipelines de producción. El foco es práctico: cada concepto teórico se acompaña de técnicas de análisis y de ejemplos de código que un profesional puede adaptar a su propio entorno.

La unidad se sitúa después de UD2, donde el estudiante adquirió las habilidades para cargar, explorar y transformar datos con pandas y similares. Aquí el salto consiste en pasar de la exploración informal a la verificación sistemática y reproducible. Al finalizar, el estudiante sabrá definir expectativas de calidad formales, integrarlas en pipelines automatizados y producir informes de auditoría que son el punto de partida de cualquier conversación técnica con clientes, equipos de negocio o reguladores.

---

## Objetivos de aprendizaje

Al terminar esta unidad el estudiante será capaz de:

1. Identificar y describir las seis dimensiones clásicas de la calidad de datos y aplicarlas como criterio de evaluación a cualquier conjunto de datos.
2. Distinguir los tres mecanismos de generación de datos faltantes (MCAR, MAR, MNAR) y elegir la estrategia de tratamiento más adecuada en cada caso.
3. Detectar duplicados exactos y aproximados usando herramientas de Python, incluyendo técnicas de fuzzy matching para datos textuales.
4. Escribir suites de expectativas de calidad con Great Expectations y contratos de esquema con Pandera y Pydantic.
5. Diseñar métricas de calidad y registrar incidencias de forma que sean auditables y rastreables a lo largo del tiempo.
6. Integrar controles de calidad automatizados en pipelines de datos y en flujos de transformación con dbt.

---

## 1. Dimensiones de la calidad de datos

El concepto de calidad de datos no es monolítico. Los marcos de referencia más utilizados en la industria —ISO 8000, el framework de DAMA International y el modelo de Wang & Strong (1996)— coinciden en descomponerlo en dimensiones independientes, cada una medible con métricas propias. Comprender estas dimensiones es el paso previo imprescindible para diseñar cualquier proceso de verificación, porque cada dimensión requiere técnicas de detección distintas y genera tipos de incidencias distintos.

### 1.1 Completitud

La completitud mide en qué proporción los campos de un registro contienen valores frente a la ausencia total de información. Un conjunto de datos es completamente completo cuando no existe ningún valor nulo, vacío o marcador de ausencia en ningún campo requerido. En la práctica, la completitud se expresa como un porcentaje: si una columna tiene 1 000 registros y 120 de ellos son nulos, su tasa de completitud es del 88 %.

La completitud es la dimensión más sencilla de medir, pero su interpretación exige cuidado. Un 5 % de nulos en el campo `ingresos_anuales` puede ser tolerable si ese campo es opcional en el formulario de recogida; el mismo porcentaje en el campo `identificador_paciente` de una base de datos clínica es inaceptable. La completitud siempre debe evaluarse en relación con el contexto de negocio y la obligatoriedad de cada campo.

La completitud también tiene una dimensión temporal: un campo puede estar completo en el momento de la ingesta y volverse incompleto semanas después si los procesos de actualización fallan. Por eso los dashboards de calidad deben monitorizar la completitud de forma continua, no sólo en el momento de la carga inicial.

### 1.2 Consistencia

La consistencia evalúa si los valores de un campo, o las relaciones entre campos, respetan las reglas de negocio definidas. Hay dos subtipos principales.

La **consistencia interna** comprueba que los valores de distintos campos en el mismo registro no se contradicen entre sí. Un ejemplo clásico: si el campo `fecha_nacimiento` indica 1990-03-15 y el campo `edad` contiene el valor 20, hay una inconsistencia interna porque la edad no corresponde al año actual. Otro: si `estado_pedido = "entregado"` pero `fecha_entrega` es nula, los dos campos son mutuamente inconsistentes.

La **consistencia entre sistemas** (o consistencia referencial cruzada) aparece cuando un mismo dato se almacena en dos o más sistemas y los valores difieren. Es uno de los problemas más costosos de resolver en entornos empresariales, donde el CRM, el ERP y el data warehouse pueden tener versiones diferentes del mismo cliente con distintos nombres, direcciones o fechas de alta.

La inconsistencia es particularmente peligrosa en modelos de ML porque el modelo puede aprender correlaciones espurias generadas por los errores: si los datos incorrectos tienen una distribución distinta a los correctos, el modelo puede terminar usando el error como señal predictiva.

### 1.3 Exactitud y veracidad

La exactitud mide hasta qué punto los valores del dato representan fielmente la realidad que describen. Es la dimensión más difícil de verificar automáticamente porque, en sentido estricto, requeriría comparar cada valor con una fuente de verdad externa. En la práctica, la exactitud se aproxima mediante:

- Comparación con fuentes de referencia autorizadas (catálogos de municipios, listados de códigos CNAE, bases de datos de productos con código EAN verificado).
- Detección de valores que están dentro del rango técnicamente válido pero son estadísticamente implausibles: una temperatura corporal de 38 °C es válida; una de 52 °C es técnicamente representable pero biológicamente imposible.
- Reglas de negocio que definen rangos esperados: el precio de venta de un artículo no puede ser inferior al precio de coste.

La veracidad es un concepto relacionado pero distinto: mide si el origen del dato es confiable. Un dato puede ser exacto hoy pero provenir de una fuente que históricamente ha tenido errores sistemáticos, lo que exige tratarlo con más cautela.

### 1.4 Unicidad (deduplicación)

La unicidad garantiza que cada entidad del mundo real aparece representada una sola vez en el conjunto de datos. La violación de la unicidad —la existencia de duplicados— es un problema de calidad omnipresente que surge por múltiples razones: errores en los procesos de ingesta, fusiones de sistemas distintos, importaciones manuales repetidas, o ausencia de restricciones de unicidad en la base de datos de origen.

Los duplicados se presentan en dos variantes. Los **duplicados exactos** son registros idénticos en todos o en la mayoría de sus campos; su detección es directa con una operación de agrupación. Los **duplicados aproximados** (o fuzzy duplicates) son registros que representan la misma entidad real pero con pequeñas variaciones: "Juan García López" y "J. García-López", o la misma dirección escrita de forma ligeramente diferente. Su detección requiere algoritmos de similitud de cadenas y, a menudo, revisión humana de los candidatos propuestos por el algoritmo.

La unicidad impacta directamente en los modelos de ML: los registros duplicados inflan artificialmente el peso estadístico de las observaciones duplicadas, distorsionan las métricas de validación si el mismo registro aparece en el conjunto de entrenamiento y en el de test, y generan sobreajuste encubierto.

### 1.5 Temporalidad y vigencia

La temporalidad evalúa si los datos están disponibles con la frecuencia y el retardo adecuados para el uso que se va a hacer de ellos. La vigencia, un concepto relacionado, mide si los datos siguen siendo representativos de la realidad en el momento en que se usan.

Un modelo de predicción de demanda que se alimenta de datos de ventas con cuatro días de retardo es funcionalmente menos valioso que uno que recibe datos con cuatro horas de retardo. Un modelo de scoring crediticio entrenado con datos de comportamiento de pago de 2019 y puesto en producción en 2024 puede estar desactualizado respecto a los patrones de comportamiento actuales.

La temporalidad es especialmente crítica en sistemas de aprendizaje automático en producción. El concepto de **data drift** (deriva de los datos) describe precisamente la situación en que la distribución estadística de los datos de entrada cambia con el tiempo, invalidando las suposiciones con las que el modelo fue entrenado. La monitorización de la vigencia es, por tanto, una actividad que debe mantenerse de forma continua durante el ciclo de vida del modelo en producción.

### 1.6 Validez de formato y dominio

La validez de formato comprueba que los valores respetan la estructura sintáctica esperada: que un campo definido como fecha contiene una fecha real y no una cadena de texto arbitraria, que un campo de correo electrónico contiene una dirección con la estructura adecuada, o que un campo numérico no contiene caracteres alfabéticos. La validez de dominio comprueba que el valor pertenece al conjunto de valores permitidos: si el campo `país` sólo puede contener códigos ISO 3166-1, cualquier valor que no esté en esa lista es inválido por definición.

La validez es la dimensión más fácilmente automatizable y la que más directamente se traduce en restricciones de esquema en bases de datos o en reglas de validación en pipelines de datos. Las herramientas que se estudian en la sección 4 de esta unidad (Great Expectations, Pandera, Pydantic) están principalmente orientadas a automatizar la verificación de validez de formato y dominio.

---

## 2. Detección y análisis de valores nulos

Los valores nulos son la forma más prevalente de degradación de la completitud y uno de los problemas más frecuentes con los que se enfrenta cualquier proyecto de datos. Su tratamiento adecuado exige comprender no sólo cuántos nulos hay y dónde, sino por qué existen, ya que el mecanismo que genera la ausencia determina qué estrategia de imputación es válida y cuál sesgaría el análisis.

### 2.1 Tipos de datos faltantes: MCAR, MAR, MNAR

La taxonomía clásica de Donald Rubin (1976) distingue tres mecanismos de generación de datos faltantes, que tienen implicaciones estadísticas directas:

**Missing Completely At Random (MCAR):** La probabilidad de que un valor sea nulo no depende ni del valor en sí ni de ninguna otra variable del conjunto de datos. Es la situación ideal porque los registros completos son una muestra aleatoria representativa del total. En la práctica, la MCAR pura es rara: un ejemplo sería que un sensor de temperatura falle de forma completamente aleatoria e independiente de la temperatura que debería medir.

**Missing At Random (MAR):** La probabilidad de que un valor sea nulo depende de otras variables observadas, pero no del valor que falta en sí mismo. Por ejemplo, en una encuesta de salud, es posible que los hombres sean menos propensos a responder preguntas sobre salud mental que las mujeres, pero, dentro de cada grupo de género, la ausencia es aleatoria. Si se conoce el género (que está observado), la ausencia puede modelarse y la imputación puede ser válida.

**Missing Not At Random (MNAR):** La probabilidad de que un valor sea nulo depende del propio valor que falta. Es el caso más problemático: en una encuesta de ingresos, los individuos de ingresos más altos pueden ser más reacios a declarar sus ingresos. Ignorar este mecanismo y aplicar imputación simple produce estimaciones sesgadas. En ML, un nulo MNAR puede ser en sí mismo una señal predictiva: el hecho de que el dato falte es informativo. Una estrategia habitual es crear una variable indicadora binaria que vale 1 cuando el valor original es nulo y 0 en caso contrario, preservando así esa señal para el modelo.

La prueba de Little (1988) es el test estadístico estándar para contrastar la hipótesis MCAR frente a MAR/MNAR, aunque su interpretación requiere prudencia con conjuntos de datos grandes.

### 2.2 Análisis de patrones de nulidad (missingno)

Antes de decidir cómo tratar los nulos es imprescindible visualizar sus patrones de aparición. La librería `missingno` de Python ofrece cuatro visualizaciones complementarias que revelan estructuras de nulidad que no son detectables con una simple tabla de porcentajes.

```python
import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt

# Carga de ejemplo
df = pd.read_csv("dataset_pacientes.csv")

# Mapa de nulidad: cada fila es un registro, cada columna una variable
# Las celdas blancas indican valores presentes, las negras valores nulos
msno.matrix(df, figsize=(12, 6), sparkline=True)
plt.title("Mapa de nulidad — Dataset pacientes")
plt.tight_layout()
plt.savefig("mapa_nulidad.png", dpi=150)

# Gráfico de barras: porcentaje de completitud por columna
msno.bar(df, figsize=(12, 4), color="#3498db")
plt.title("Completitud por columna")
plt.tight_layout()
plt.savefig("completitud_columnas.png", dpi=150)

# Heatmap de correlación de nulidad: detecta si las ausencias en dos
# columnas tienden a aparecer juntas (posible patrón MAR)
msno.heatmap(df, figsize=(10, 8))
plt.title("Correlación de nulidad entre columnas")
plt.tight_layout()
plt.savefig("correlacion_nulidad.png", dpi=150)

# Dendrograma: agrupa columnas con patrones de nulidad similares
msno.dendrogram(df, figsize=(10, 6))
plt.title("Dendrograma de nulidad")
plt.tight_layout()
plt.savefig("dendrograma_nulidad.png", dpi=150)
```

El mapa de nulidad es especialmente útil para detectar patrones temporales: si los nulos aparecen en bloques contiguos de filas, es probable que se correspondan con periodos de tiempo en los que el proceso de recogida falló, lo que sugiere un mecanismo MNAR o MAR condicionado por el tiempo.

Para un análisis cuantitativo rápido, el siguiente bloque produce un informe tabular de completitud:

```python
def informe_nulidad(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve un DataFrame con estadísticas de nulidad por columna."""
    nulos = df.isnull().sum()
    total = len(df)
    return pd.DataFrame({
        "nulos": nulos,
        "completitud_pct": ((total - nulos) / total * 100).round(2),
        "dtype": df.dtypes
    }).sort_values("completitud_pct")

print(informe_nulidad(df).to_string())
```

### 2.3 Impacto de los nulos en modelos de ML

La mayoría de los algoritmos de aprendizaje automático en scikit-learn no aceptan valores nulos y lanzarán una excepción si los datos contienen NaN sin tratar. Pero el impacto va más allá de un error técnico:

- **Sesgo en estimaciones:** Si se eliminan los registros con nulos sin considerar el mecanismo (caso MNAR), las estadísticas descriptivas y los patrones aprendidos por el modelo representan sólo la subpoblación de registros completos, que puede ser sistemáticamente diferente del total.
- **Reducción de la potencia estadística:** La eliminación de registros reduce el tamaño muestral, lo que aumenta la varianza de las estimaciones y empeora las métricas de generalización.
- **Distorsión de importancias:** En árboles de decisión con soporte nativo para nulos (como XGBoost o LightGBM), la estrategia interna de manejo de nulos puede crear interacciones espurias si los nulos no están distribuidos de forma aleatoria.
- **Fuga de información en test/train:** Si la imputación se realiza sobre el conjunto completo antes de dividir en entrenamiento y test, las estadísticas usadas para imputar (media, mediana) están contaminadas por los datos de test, lo que produce una evaluación optimista del modelo.

La buena práctica es encapsular la imputación dentro de un `Pipeline` de scikit-learn, garantizando que el `fit` de los imputadores sólo ve los datos de entrenamiento:

```python
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

pipeline = Pipeline([
    ("imputer", KNNImputer(n_neighbors=5)),
    ("scaler", StandardScaler()),
    ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
])

# La imputación aprende SOLO de X_train
pipeline.fit(X_train, y_train)
score = pipeline.score(X_test, y_test)
```

---

## 3. Detección de duplicados e inconsistencias

### 3.1 Duplicados exactos vs. duplicados aproximados (fuzzy matching)

La detección de duplicados exactos es computacionalmente trivial pero requiere definir correctamente la clave de deduplicación. En pandas, `DataFrame.duplicated()` identifica filas que son idénticas en el subconjunto de columnas especificado:

```python
import pandas as pd

df = pd.read_csv("clientes.csv")

# Duplicados exactos en todas las columnas
duplicados_totales = df[df.duplicated(keep=False)]
print(f"Registros duplicados (exactos): {len(duplicados_totales)}")

# Duplicados por clave de negocio (email del cliente)
duplicados_email = df[df.duplicated(subset=["email"], keep=False)]
print(f"Emails duplicados: {duplicados_email['email'].nunique()}")

# Conservar el registro más reciente (asumiendo columna fecha_registro)
df_dedup = (
    df
    .sort_values("fecha_registro", ascending=False)
    .drop_duplicates(subset=["email"], keep="first")
    .reset_index(drop=True)
)
```

Los duplicados aproximados son más difíciles de detectar porque requieren medir la similitud semántica entre cadenas de texto. La librería `thefuzz` (antes `fuzzywuzzy`) implementa varias métricas basadas en la distancia de Levenshtein:

```python
from thefuzz import fuzz, process
import pandas as pd

nombres = [
    "Juan García López",
    "J. García-López",
    "Juan Garcia Lopez",
    "María Fernández Ruiz",
    "Maria Fernandez Ruiz"
]

# Comparación entre dos cadenas específicas
ratio = fuzz.token_sort_ratio("Juan García López", "J. García-López")
print(f"Similitud: {ratio}")  # Suele devolver valores > 85

# Encontrar el candidato más similar a una cadena objetivo
mejor_match, puntuacion = process.extractOne("Juan García López", nombres)
print(f"Mejor coincidencia: '{mejor_match}' con puntuación {puntuacion}")

# Detección masiva: para cada nombre, buscar duplicados con similitud > umbral
UMBRAL = 85
candidatos_duplicados = []
for i, nombre_a in enumerate(nombres):
    for nombre_b in nombres[i+1:]:
        sim = fuzz.token_sort_ratio(nombre_a, nombre_b)
        if sim >= UMBRAL:
            candidatos_duplicados.append({
                "nombre_a": nombre_a,
                "nombre_b": nombre_b,
                "similitud": sim
            })

df_candidatos = pd.DataFrame(candidatos_duplicados)
print(df_candidatos)
```

Para conjuntos de datos con millones de registros, la comparación par a par es computacionalmente inviable. La técnica de **blocking** reduce el espacio de búsqueda comparando sólo registros que comparten algún atributo de bloqueo (por ejemplo, la primera letra del apellido o el código postal), y librerías como `recordlinkage` implementan este patrón de forma eficiente.

### 3.2 Inconsistencias referenciales y de dominio

Las inconsistencias referenciales surgen cuando un valor en una columna debería corresponder a una entrada válida en un catálogo de referencia pero no lo hace. Por ejemplo, si una tabla de ventas tiene una columna `codigo_producto` que debería referenciar a la tabla de productos pero contiene códigos que no existen en ella:

```python
import pandas as pd

ventas = pd.read_csv("ventas.csv")
productos = pd.read_csv("productos.csv")

# Detectar ventas con códigos de producto inexistentes
codigos_validos = set(productos["codigo_producto"])
ventas_huerfanas = ventas[~ventas["codigo_producto"].isin(codigos_validos)]
print(f"Ventas con código de producto inválido: {len(ventas_huerfanas)}")
print(ventas_huerfanas["codigo_producto"].value_counts().head(10))

# Verificar integridad referencial entre columnas del mismo DataFrame
# Ejemplo: fecha_inicio no puede ser posterior a fecha_fin
inconsistencias_fecha = ventas[ventas["fecha_inicio"] > ventas["fecha_fin"]]
print(f"Registros con fechas inconsistentes: {len(inconsistencias_fecha)}")
```

### 3.3 Detección de errores de tipado y codificación

Los errores de tipado son frecuentes en datos recogidos manualmente o mediante procesos de OCR. Se manifiestan como valores que deberían ser numéricos pero contienen caracteres no numéricos ("1O" en lugar de "10", donde O es la letra), fechas en formatos inconsistentes dentro de la misma columna ("2024-01-15" y "15/01/2024" mezcladas), o codificaciones de texto corruptas que producen caracteres ilegibles.

```python
import pandas as pd
import re

df = pd.read_csv("formularios.csv", dtype=str)  # Cargar todo como string

# Detectar valores que no son numéricos puros en columna que debería serlo
def no_numerico(valor):
    if pd.isna(valor):
        return False
    return not re.match(r"^-?\d+(\.\d+)?$", str(valor).strip())

errores_numericos = df["importe"][df["importe"].apply(no_numerico)]
print(f"Valores no numéricos en columna 'importe': {len(errores_numericos)}")
print(errores_numericos.value_counts().head(20))

# Detectar mezcla de formatos de fecha
formatos_detectados = df["fecha"].dropna().apply(
    lambda x: "ISO" if re.match(r"\d{4}-\d{2}-\d{2}", x)
              else "ESP" if re.match(r"\d{2}/\d{2}/\d{4}", x)
              else "OTRO"
).value_counts()
print("Formatos de fecha detectados:")
print(formatos_detectados)
```

---

## 4. Validación de esquemas y contratos de datos

La verificación ad hoc mediante scripts de análisis es útil para exploración, pero en entornos de producción se necesitan mecanismos formales y reproducibles. El enfoque moderno es definir **expectativas de calidad** de forma declarativa, ejecutarlas de forma automática con cada nueva carga de datos y generar informes que permitan rastrear el estado de calidad a lo largo del tiempo.

### 4.1 Validación con Great Expectations

Great Expectations (GX) es la librería de código abierto más utilizada en la industria para la validación de datos en pipelines. Su modelo conceptual se basa en tres elementos: las **Expectations** (afirmaciones individuales sobre los datos), las **Expectation Suites** (conjuntos de expectativas agrupadas por propósito) y los **Data Docs** (informes HTML generados automáticamente tras cada validación).

```python
import great_expectations as gx
import pandas as pd

# Inicializar contexto de GX en el directorio actual
context = gx.get_context()

# Cargar datos como un DataFrame de pandas
df = pd.read_csv("ventas_2024.csv")

# Crear un datasource para el DataFrame en memoria
datasource = context.sources.add_pandas("datasource_ventas")
data_asset = datasource.add_dataframe_asset("ventas_asset")
batch_request = data_asset.build_batch_request(dataframe=df)

# Crear una suite de expectativas
suite = context.add_expectation_suite("suite_ventas_calidad")

validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name="suite_ventas_calidad"
)

# Expectativas de completitud
validator.expect_column_values_to_not_be_null("id_venta")
validator.expect_column_values_to_not_be_null("fecha_venta")
validator.expect_column_values_to_not_be_null("importe")

# Expectativas de dominio
validator.expect_column_values_to_be_between(
    "importe", min_value=0, max_value=100_000,
    mostly=0.99  # El 99% de los valores debe cumplir la condición
)

# Expectativas de unicidad
validator.expect_column_values_to_be_unique("id_venta")

# Expectativas de formato
validator.expect_column_values_to_match_regex(
    "codigo_postal", r"^\d{5}$"
)

# Expectativas de conjunto de valores válidos
validator.expect_column_values_to_be_in_set(
    "estado_pedido",
    ["pendiente", "procesando", "enviado", "entregado", "cancelado"]
)

# Guardar la suite
validator.save_expectation_suite(discard_failed_expectations=False)

# Ejecutar la validación
checkpoint = context.add_or_update_checkpoint(
    name="checkpoint_ventas",
    validator=validator
)
resultado = checkpoint.run()
print(f"Validación superada: {resultado.success}")

# Generar Data Docs (informe HTML)
context.build_data_docs()
```

Great Expectations también permite definir expectativas sobre la distribución estadística de las columnas, lo que es especialmente valioso para detectar data drift: si la media de la columna `importe` en la carga de hoy se aleja más de dos desviaciones estándar de la media histórica, la expectativa fallará y el pipeline puede detenerse o emitir una alerta.

### 4.2 Pandera: validación de DataFrames

Pandera ofrece un enfoque alternativo, más cercano a la filosofía de Python de "tipado opcional" y más integrado con el flujo de trabajo habitual de pandas. Su mecanismo principal es la definición de un `DataFrameSchema` que actúa como especificación formal del DataFrame esperado:

```python
import pandera as pa
from pandera import Column, DataFrameSchema, Check, Index
import pandas as pd
from datetime import datetime

# Definir el esquema de validación
esquema_ventas = DataFrameSchema(
    columns={
        "id_venta": Column(
            pa.String,
            checks=Check.str_matches(r"^VTA-\d{8}$"),
            nullable=False,
            unique=True
        ),
        "fecha_venta": Column(
            pa.DateTime,
            checks=Check.greater_than_or_equal_to(pd.Timestamp("2020-01-01")),
            nullable=False
        ),
        "importe": Column(
            pa.Float,
            checks=[
                Check.greater_than(0),
                Check.less_than_or_equal_to(50_000)
            ],
            nullable=False
        ),
        "cliente_id": Column(pa.Int, nullable=False),
        "canal": Column(
            pa.String,
            checks=Check.isin(["online", "tienda", "telefono"]),
            nullable=True
        ),
    },
    index=Index(pa.Int),
    strict=True,          # No se permiten columnas no declaradas en el esquema
    coerce=False,         # No forzar conversión de tipos; fallar si no coinciden
    name="ventas_2024"
)

# Validar un DataFrame
df = pd.read_csv("ventas_2024.csv", parse_dates=["fecha_venta"])
try:
    df_validado = esquema_ventas.validate(df, lazy=True)
    print("Validación superada.")
except pa.errors.SchemaErrors as e:
    print("Errores de validación encontrados:")
    print(e.failure_cases)
```

Pandera también soporta anotaciones de tipo, lo que permite integrar la validación directamente en las firmas de las funciones mediante el decorador `@pa.check_types`:

```python
from pandera.typing import DataFrame, Series
import pandera as pa

class EsquemaVentasInput(pa.DataFrameModel):
    id_venta: Series[str] = pa.Field(str_matches=r"^VTA-\d{8}$", unique=True)
    importe: Series[float] = pa.Field(gt=0, le=50_000)
    canal: Series[str] = pa.Field(isin=["online", "tienda", "telefono"])

    class Config:
        strict = True
        coerce = False

@pa.check_types
def calcular_totales(df: DataFrame[EsquemaVentasInput]) -> pd.Series:
    """Calcula el importe total por canal. La validación ocurre automáticamente."""
    return df.groupby("canal")["importe"].sum()
```

### 4.3 Pydantic para validación de registros

Mientras Pandera opera sobre DataFrames (colecciones de registros), Pydantic es más adecuado para validar registros individuales, como los que se reciben en una API REST, en un flujo de mensajes de Kafka o en un proceso de ingesta evento a evento. Su modelo de validación basado en clases Python con anotaciones de tipo es extremadamente expresivo:

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Literal
from datetime import datetime
from enum import Enum

class CanalVenta(str, Enum):
    online = "online"
    tienda = "tienda"
    telefono = "telefono"

class RegistroVenta(BaseModel):
    id_venta: str = Field(..., pattern=r"^VTA-\d{8}$")
    fecha_venta: datetime
    importe: float = Field(..., gt=0, le=50_000)
    cliente_id: int = Field(..., gt=0)
    canal: CanalVenta
    descuento_pct: Optional[float] = Field(default=None, ge=0, le=100)
    importe_final: Optional[float] = None

    @field_validator("fecha_venta")
    @classmethod
    def fecha_no_futura(cls, v: datetime) -> datetime:
        if v > datetime.now():
            raise ValueError("La fecha de venta no puede ser futura.")
        return v

    @model_validator(mode="after")
    def calcular_importe_final(self) -> "RegistroVenta":
        """Calcula el importe final aplicando el descuento si existe."""
        if self.descuento_pct is not None:
            self.importe_final = self.importe * (1 - self.descuento_pct / 100)
        else:
            self.importe_final = self.importe
        return self

# Uso
try:
    venta = RegistroVenta(
        id_venta="VTA-20240315",
        fecha_venta="2024-03-15T10:30:00",
        importe=1250.00,
        cliente_id=4821,
        canal="online",
        descuento_pct=10
    )
    print(f"Importe final: {venta.importe_final:.2f} €")
except Exception as e:
    print(f"Error de validación: {e}")
```

Pydantic v2 (la versión actual) está implementado en Rust para máximo rendimiento, lo que lo hace viable para validación de alto throughput en sistemas de ingesta de eventos en tiempo real.

### 4.4 Data contracts: concepto y práctica

Un data contract es un acuerdo formal entre el productor de un conjunto de datos y sus consumidores, que especifica el esquema, las garantías de calidad, las SLAs de disponibilidad y el proceso de cambio. El concepto, popularizado por Andrew Jones (2023) en su libro homónimo, traslada al mundo de los datos la misma disciplina que los contratos de API han traído al mundo de los servicios.

Un data contract típico cubre:
- **Descripción semántica:** Qué representa cada campo, su unidad de medida, y el propietario del dato.
- **Esquema:** Tipos de datos, restricciones de nulidad, valores permitidos.
- **Garantías de calidad:** Tasas mínimas de completitud, unicidad garantizada, retardo máximo desde el evento original.
- **SLA de disponibilidad:** Frecuencia de actualización, ventana de mantenimiento, latencia máxima.
- **Proceso de cambio:** Cómo y con cuánto preaviso puede el productor modificar el esquema o las garantías.

En la práctica, los data contracts suelen implementarse como ficheros YAML versionados en un repositorio, combinados con validadores que comprueban automáticamente que los datos publicados cumplen el contrato:

```yaml
# data_contract_ventas_v1.yaml
apiVersion: v2.2.0
id: urn:datacontract:ventas:2024
info:
  title: "Contrato de datos — Ventas"
  version: "1.0.0"
  owner: "equipo-comercial"
  contact: "datos@empresa.com"
models:
  ventas:
    description: "Registro de transacciones de venta"
    fields:
      id_venta:
        type: string
        required: true
        unique: true
        pattern: "^VTA-\\d{8}$"
      importe:
        type: number
        required: true
        minimum: 0
        maximum: 50000
      fecha_venta:
        type: timestamp
        required: true
quality:
  type: "great_expectations"
  specification: "suites/suite_ventas_calidad.json"
```

---

## 5. Auditoría y reportes de calidad

La detección puntual de problemas de calidad no es suficiente en entornos de producción. Se necesita un sistema que registre el estado de calidad a lo largo del tiempo, que permita detectar tendencias de degradación y que genere evidencias auditables para equipos de negocio, reguladores o procesos de certificación.

### 5.1 Métricas de calidad y dashboards

Las métricas de calidad traducen las dimensiones estudiadas en la sección 1 a valores numéricos concretos y comparables. Un sistema de métricas maduro define para cada dimensión una métrica, un umbral de aceptación y un umbral de alerta, y los registra de forma periódica en una base de datos de métricas.

| Dimensión       | Métrica ejemplo                                  | Umbral aceptación | Umbral alerta |
|-----------------|--------------------------------------------------|-------------------|---------------|
| Completitud     | % de valores no nulos en campos obligatorios     | ≥ 99 %            | < 95 %        |
| Unicidad        | % de registros sin duplicado en clave primaria   | 100 %             | < 99.9 %      |
| Validez         | % de valores que superan todas las validaciones  | ≥ 98 %            | < 95 %        |
| Consistencia    | % de registros sin contradicciones entre campos  | ≥ 99 %            | < 97 %        |
| Temporalidad    | Minutos de retardo desde el evento original      | ≤ 60 min          | > 240 min     |
| Exactitud       | % de valores dentro de rangos estadísticos esperados | ≥ 97 %        | < 92 %        |

Los dashboards de calidad pueden implementarse con herramientas BI estándar (Power BI, Tableau, Metabase) o con soluciones especializadas como Monte Carlo Data o Datafold, que añaden capacidades de detección de anomalías estadísticas y trazabilidad de linaje.

### 5.2 Registro de incidencias de calidad

Toda violación de las expectativas de calidad debe registrarse como una incidencia con una estructura mínima estándar: identificador único, fecha y hora de detección, fuente de datos afectada, dimensión de calidad violada, descripción técnica del problema, severidad estimada (bloqueante, alta, media, baja), y estado de resolución.

Este registro tiene un doble propósito: operativo (permite priorizar y resolver los problemas) y analítico (permite identificar orígenes recurrentes de problemas de calidad, que suelen señalar deficiencias en los procesos de captura de datos en origen).

```python
import pandas as pd
from datetime import datetime
import uuid

def registrar_incidencia(
    fuente: str,
    dimension: str,
    descripcion: str,
    severidad: str,
    num_registros_afectados: int,
    ruta_log: str = "incidencias_calidad.csv"
) -> str:
    """Registra una incidencia de calidad en el log persistente."""
    id_incidencia = str(uuid.uuid4())[:8].upper()
    nueva_incidencia = {
        "id": id_incidencia,
        "timestamp": datetime.now().isoformat(),
        "fuente": fuente,
        "dimension": dimension,
        "descripcion": descripcion,
        "severidad": severidad,
        "registros_afectados": num_registros_afectados,
        "estado": "abierta"
    }
    try:
        log = pd.read_csv(ruta_log)
    except FileNotFoundError:
        log = pd.DataFrame()
    
    log = pd.concat([log, pd.DataFrame([nueva_incidencia])], ignore_index=True)
    log.to_csv(ruta_log, index=False)
    print(f"Incidencia registrada: {id_incidencia}")
    return id_incidencia
```

### 5.3 Integración de controles de calidad en pipelines

Los controles de calidad añaden su máximo valor cuando se integran en el flujo de ejecución del pipeline y no como un paso de revisión manual posterior. El patrón más habitual es el **quality gate**: un punto de control en el pipeline donde se ejecutan las validaciones y, si fallan, el pipeline se detiene o desvía los datos hacia una cuarentena en lugar de continuar con el procesamiento.

En Apache Airflow, el operador `ShortCircuitOperator` permite implementar quality gates de forma elegante: si la función de evaluación devuelve `False`, todas las tareas downstream se marcan como `skipped` y no se ejecutan:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from datetime import datetime
import great_expectations as gx
import pandas as pd

def verificar_calidad_ventas(**context) -> bool:
    """Ejecuta las validaciones de GX. Devuelve True si pasan, False si fallan."""
    df = pd.read_parquet(context["params"]["ruta_datos"])
    gx_context = gx.get_context()
    resultado = gx_context.run_checkpoint("checkpoint_ventas")
    if not resultado.success:
        print(f"Calidad insuficiente. Datos enviados a cuarentena.")
        df.to_parquet(f"cuarentena/ventas_{datetime.now().date()}.parquet")
    return resultado.success

with DAG("pipeline_ventas", start_date=datetime(2024, 1, 1), schedule="@daily") as dag:
    quality_gate = ShortCircuitOperator(
        task_id="quality_gate",
        python_callable=verificar_calidad_ventas,
        params={"ruta_datos": "staging/ventas_hoy.parquet"}
    )
    cargar_a_dw = PythonOperator(
        task_id="cargar_a_dw",
        python_callable=lambda: print("Cargando al Data Warehouse...")
    )
    quality_gate >> cargar_a_dw
```

---

## 6. Herramientas especializadas

### 6.1 dbt tests para almacenes de datos

dbt (data build tool) es la herramienta estándar de facto para las transformaciones en almacenes de datos modernos. Además de gestionar las transformaciones SQL mediante modelos versionados, dbt incorpora un sistema de tests de calidad que puede ejecutarse sobre los modelos ya materializados en el almacén.

dbt distingue dos tipos de tests:

**Tests genéricos (built-in):** Se declaran directamente en el archivo YAML de configuración del modelo y cubren las comprobaciones más habituales sin necesidad de escribir SQL:

```yaml
# models/schema.yml
models:
  - name: ventas_diarias
    description: "Tabla de ventas agregadas por día y canal"
    columns:
      - name: id_venta
        description: "Identificador único de la venta"
        tests:
          - unique
          - not_null
      - name: canal
        tests:
          - not_null
          - accepted_values:
              values: ["online", "tienda", "telefono"]
      - name: importe
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0"
      - name: fecha_venta
        tests:
          - not_null
          - dbt_utils.recency:
              datepart: day
              field: fecha_venta
              interval: 2
```

**Tests singulares (custom SQL):** Se implementan como ficheros `.sql` en la carpeta `tests/` que devuelven los registros que violan la condición. Si la consulta devuelve cero filas, el test pasa; si devuelve una o más filas, el test falla:

```sql
-- tests/test_importe_mayor_que_coste.sql
-- Falla si hay ventas donde el importe es menor que el coste declarado
SELECT
    v.id_venta,
    v.importe,
    p.precio_coste
FROM {{ ref("ventas_diarias") }} v
JOIN {{ ref("productos") }} p ON v.codigo_producto = p.codigo_producto
WHERE v.importe < p.precio_coste
```

Los tests de dbt se ejecutan con `dbt test` y pueden integrarse en los pipelines de CI/CD mediante GitHub Actions, GitLab CI u otras plataformas. El paquete de la comunidad `dbt-expectations` añade decenas de tests adicionales inspirados directamente en Great Expectations, incluyendo tests de distribución estadística y de anomalías.

### 6.2 Apache Griffin y otras plataformas DQ

Para organizaciones con necesidades de calidad de datos a gran escala —petabytes de datos en Hadoop, Spark o plataformas distribuidas— existen plataformas especializadas que van más allá de la validación a nivel de DataFrame.

**Apache Griffin** es un proyecto de la Apache Software Foundation orientado a entornos Big Data. Permite definir medidas de calidad (completitud, exactitud, unicidad, temporalidad) sobre conjuntos de datos almacenados en HDFS, Hive o Kafka, ejecutar los jobs de medición en Spark y publicar los resultados en un dashboard centralizado. Su arquitectura es más compleja que las herramientas orientadas a pandas, pero escala de forma natural a centenares de terabytes.

La siguiente tabla compara las principales herramientas según su caso de uso principal:

| Herramienta         | Caso de uso principal                      | Integración        | Escalabilidad  |
|---------------------|--------------------------------------------|--------------------|----------------|
| Great Expectations  | Validación en pipelines Python             | Airflow, dbt, Spark| Alta           |
| Pandera             | Validación de DataFrames pandas/Spark      | Código Python      | Media-Alta     |
| Pydantic            | Validación de registros individuales       | APIs, eventos      | Alta (Rust)    |
| dbt tests           | Calidad en modelos del DWH                 | dbt, CI/CD         | Alta (SQL)     |
| Apache Griffin      | Calidad en entornos Big Data               | Spark, Hive, Kafka | Muy alta       |
| Monte Carlo         | Observabilidad y detección de anomalías    | DWH cloud          | Alta (SaaS)    |
| Soda Core           | Validación con sintaxis YAML/SQL           | Airflow, dbt       | Alta           |
| MobyDQ              | Data quality para pipelines ETL            | Airflow            | Media          |

**Soda Core** merece mención especial por su sintaxis declarativa basada en YAML que permite definir checks de calidad sin escribir código Python o SQL, lo que facilita la colaboración entre equipos técnicos y de negocio:

```yaml
# checks_ventas.yml
checks for ventas_diarias:
  - missing_count(id_venta) = 0:
      name: "Sin nulos en id_venta"
  - duplicate_count(id_venta) = 0:
      name: "Sin duplicados en id_venta"
  - min(importe) >= 0:
      name: "Importe mínimo no negativo"
  - freshness(fecha_venta) < 1d:
      name: "Datos actualizados en las últimas 24 horas"
```

---

## Actividades prácticas propuestas

**Actividad 1 — Auditoría de completitud y nulidad (2 horas)**
Se proporciona un CSV con datos de recursos humanos de una empresa ficticia (1 500 registros, 20 columnas) que contiene nulos en distintas proporciones y con diferentes mecanismos subyacentes. El estudiante debe: (a) generar el informe tabular de completitud; (b) producir los cuatro gráficos de `missingno`; (c) identificar, con argumentación razonada, si cada columna con nulos significativos sigue un patrón MCAR, MAR o MNAR; (d) proponer la estrategia de tratamiento más adecuada para cada columna.

**Actividad 2 — Deduplicación fuzzy (2 horas)**
Se proporciona un CSV con 3 000 registros de clientes exportados de dos sistemas distintos y fusionados sin deduplicar. El estudiante debe: (a) detectar y eliminar los duplicados exactos; (b) usar `thefuzz` para detectar duplicados aproximados en el nombre del cliente con un umbral de similitud del 80 %; (c) generar un informe con los candidatos detectados y el número de registros finales tras la deduplicación; (d) reflexionar sobre los falsos positivos y falsos negativos del proceso.

**Actividad 3 — Suite de validación con Pandera (3 horas)**
A partir de un dataset de transacciones financieras, el estudiante debe: (a) definir un esquema Pandera completo usando `DataFrameModel` con anotaciones de tipo; (b) ejecutar la validación y capturar el DataFrame de errores; (c) escribir una función decorada con `@pa.check_types` que reciba el DataFrame validado y calcule estadísticas resumen; (d) integrar la validación en un pipeline simulado usando un `ShortCircuitOperator` de Airflow en entorno local (Astro CLI o Docker).

**Actividad 4 — Data contract y Great Expectations (4 horas)**
El estudiante debe: (a) diseñar un data contract YAML completo para un dataset de inventario de productos; (b) implementar la Expectation Suite correspondiente en Great Expectations; (c) ejecutar la validación sobre tres versiones del dataset (limpia, con nulos, con duplicados) y comparar los informes HTML generados; (d) proponer qué expectativas adicionales añadiría para detectar data drift si el dataset se actualiza diariamente.

**Actividad 5 — Tests de calidad en dbt (3 horas)**
Usando un entorno dbt con DuckDB como almacén local (configuración sin coste), el estudiante debe: (a) crear un modelo dbt que transforma un CSV de ventas en una tabla agregada; (b) añadir tests genéricos en el fichero `schema.yml` para todas las columnas críticas; (c) escribir dos tests singulares custom en SQL; (d) integrar la ejecución de `dbt test` en un workflow de GitHub Actions que se dispare en cada push a la rama main.

---

## Referencias y material externo

**Libros y publicaciones académicas**

- Wang, R. Y., & Strong, D. M. (1996). Beyond accuracy: What data quality means to data consumers. *Journal of Management Information Systems*, 12(4), 5-33. Artículo fundacional que establece el marco multidimensional de calidad de datos. https://doi.org/10.1080/07421222.1996.11518099

- Loshin, D. (2010). *The Practitioner's Guide to Data Quality Improvement*. Morgan Kaufmann. Referencia práctica que cubre gobernanza, métricas y procesos de mejora de calidad de datos en entornos empresariales.

- Rubin, D. B. (1976). Inference and missing data. *Biometrika*, 63(3), 581-592. Artículo original que establece la taxonomía MCAR/MAR/MNAR. https://doi.org/10.1093/biomet/63.3.581

- Jones, A. (2023). *Driving Data Quality with Data Contracts*. O'Reilly Media. Introducción práctica al concepto de data contracts, con ejemplos en YAML y Python.

- Redman, T. C. (2008). *Data Driven: Profiting from Your Most Important Business Asset*. Harvard Business Press. Perspectiva de negocio sobre el impacto económico de la mala calidad de datos.

**Documentación oficial**

- Great Expectations. (2024). *Great Expectations Documentation v1.x*. https://docs.greatexpectations.io

- Pandera. (2024). *Pandera Documentation — Statistical Data Testing*. https://pandera.readthedocs.io

- Pydantic. (2024). *Pydantic v2 Documentation*. https://docs.pydantic.dev

- dbt Labs. (2024). *dbt Documentation — Tests*. https://docs.getdbt.com/docs/build/tests

- Apache Software Foundation. (2024). *Apache Griffin Documentation*. https://griffin.apache.org/docs

- Soda. (2024). *Soda Core Documentation*. https://docs.soda.io/soda-core/overview-main.html

- missingno. (2024). *missingno: Matrix of Missing Data Visualization*. https://github.com/ResidentMario/missingno

- seatgeek/thefuzz. (2024). *thefuzz: Fuzzy String Matching in Python*. https://github.com/seatgeek/thefuzz

**Cursos y recursos en línea**

- Géron, A. (2022). *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow* (3.ª ed.). O'Reilly Media. Capítulo 2 incluye una sección sobre preprocesamiento y tratamiento de valores nulos en pipelines scikit-learn.

- dbt Community. (2024). *dbt-expectations package*. Extensión que añade más de 50 tests adicionales inspirados en Great Expectations al ecosistema dbt. https://github.com/calogica/dbt-expectations

- DataTalksClub. (2023). *Data Engineering Zoomcamp*. Curso gratuito que incluye un módulo completo sobre calidad de datos en pipelines modernos. https://github.com/DataTalks.Club/data-engineering-zoomcamp

- McKinney, W. (2022). *Python for Data Analysis* (3.ª ed.). O'Reilly Media. Referencia estándar para pandas; los capítulos 7 y 8 cubren limpieza y transformación de datos.

**Papers y recursos técnicos adicionales**

- Little, R. J. A. (1988). A test of Missing Completely at Random for multivariate data with missing values. *Journal of the American Statistical Association*, 83(404), 1198-1202. https://doi.org/10.2307/2290157

- Breck, E., Cai, S., Nielsen, E., Salib, M., & Sculley, D. (2017). The ML Test Score: A rubric for ML production readiness and technical debt reduction. *IEEE International Conference on Big Data*. https://doi.org/10.1109/BigData.2017.8258038. Articula cómo la calidad de datos es parte integral de la madurez de los sistemas ML en producción.

- Polyzotis, N., Roy, S., Whang, S. E., & Zinkevich, M. (2018). Data lifecycle challenges in production machine learning: A survey. *ACM SIGMOD Record*, 47(2), 17-28. https://doi.org/10.1145/3299887.3299891
