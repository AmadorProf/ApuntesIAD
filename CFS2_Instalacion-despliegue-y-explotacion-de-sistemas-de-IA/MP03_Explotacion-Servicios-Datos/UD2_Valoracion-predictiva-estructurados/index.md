---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD2 · Valoración predictiva de datos estructurados | MP03 · Explotación de servicios de datos y analítica'
footer: 'CFS Instalación, despliegue y explotación de sistemas de IA (IAD)'
---

<style>
section { font-family: 'Segoe UI', Arial, sans-serif; }
h1 { color: #1e3a5f; }
h2 { color: #1e3a5f; border-bottom: 2px solid #10b981; padding-bottom: 6px; }
h3 { color: #059669; }
table { font-size: 0.82em; width: 100%; }
ul, ol { font-size: 0.88em; }
blockquote { border-left: 4px solid #10b981; background: #ecfdf5; padding: 8px 16px; border-radius: 4px; }
footer, header { font-size: 0.6em; color: #6b7280; }
section.lead h1 { font-size: 2em; text-align: center; margin-top: 80px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
pre { background: #1e293b; color: #e2e8f0; padding: 16px; border-radius: 8px; font-size: 0.8em; }
</style>

<!-- _class: lead -->

# UD2 · Valoración predictiva de datos estructurados

**MP03 — Explotación de servicios de datos y analítica**
CFS Instalación, despliegue y explotación de sistemas de IA (IAD)

---

## Objetivos de la unidad

Al finalizar esta unidad el alumnado será capaz de:

- Extraer, alimentar y etiquetar datos estructurados para experimentación de ML.
- Configurar y ejecutar experimentos con herramientas AutoML o ML de la plataforma.
- Interpretar y documentar los resultados de los experimentos: métricas, fiabilidad y avisos.
- Seleccionar el modelo ganador e integrarlo en un pipeline productivo en la nube.

> **Resultado de aprendizaje:** Obtiene una valoración preliminar de la calidad y capacidad predictiva de datos estructurados con la herramienta de ML de la plataforma.

---

## Contexto: datos estructurados y ML supervisado

Los **datos estructurados** son aquellos organizados en filas y columnas con un esquema definido: tablas de bases de datos relacionales, ficheros CSV, hojas de cálculo.

### Casos de uso típicos en empresas

| Caso de uso | Variable objetivo | Tipo de tarea |
|---|---|---|
| Predicción de ventas | Unidades vendidas (numérico) | Regresión |
| Detección de fraude | Fraude / No fraude (binario) | Clasificación binaria |
| Segmentación de clientes | Segmento (A/B/C/D) | Clasificación multiclase |
| Churn de clientes | Baja en 30 días (binario) | Clasificación binaria |
| Predicción de morosidad | Probabilidad de impago (0–1) | Clasificación / Regresión |

> La valoración predictiva consiste en obtener una estimación rápida de si los datos disponibles tienen suficiente señal para construir un modelo útil.

---

## Preprocesamiento — Extracción y alimentación

El primer paso es llevar los datos desde la fuente a la plataforma de ML.

### Fuentes de datos estructurados

| Fuente | Mecanismo de extracción | Herramientas |
|---|---|---|
| Base de datos SQL | Conector JDBC/ODBC, query SQL | SQLAlchemy, Azure Data Factory |
| Data Warehouse | Conector nativo (BigQuery, Snowflake) | dbt, Spark, Dataflow |
| Fichero CSV / Parquet | Carga directa al blob/bucket | SDK de la plataforma, pandas |
| API REST | HTTP GET con paginación | requests, Airbyte |
| Data Lake | Acceso por ruta al storage | Delta Lake, ADLS, S3 |

### Buenas prácticas en la extracción

- Registrar la consulta exacta o ruta usada (reproducibilidad).
- Documentar la fecha de extracción y la versión de los datos.
- Verificar que no se mezclan datos de entrenamiento y evaluación en la extracción.

---

## Preprocesamiento — Etiquetado de variables

Una vez cargados los datos, se identifican y etiquetan los distintos tipos de columnas.

### Tipos de variables

| Tipo | Descripción | Ejemplo |
|---|---|---|
| **Variable objetivo** | Lo que el modelo debe predecir | `fraude`, `ventas_mes` |
| **Variable ID** | Identificador único, excluir del modelo | `id_cliente`, `numero_pedido` |
| **Variable fecha** | Temporal, tratamiento especial | `fecha_transaccion` |
| **Categórica nominal** | Sin orden intrínseco | `provincia`, `tipo_producto` |
| **Categórica ordinal** | Con orden definido | `nivel_riesgo` (bajo/medio/alto) |
| **Numérica continua** | Valores reales | `importe`, `edad` |
| **Numérica discreta** | Enteros contables | `num_transacciones` |

> Las variables ID y fecha no aportan capacidad predictiva y pueden introducir sobreajuste si se incluyen sin transformar.

---

## Preprocesamiento — Subconjuntos y división de datos

La correcta separación de los datos es fundamental para evaluar el modelo de forma honesta.

### División estándar

```
Dataset completo (100%)
    ├── Entrenamiento (70–80%)   → El modelo aprende de estos datos
    ├── Validación (10–15%)      → Se usa para ajustar hiperparámetros
    └── Prueba / Test (10–15%)   → Evaluación final, solo se usa una vez
```

### Consideraciones importantes

- La división debe ser **estratificada** en clasificación (misma proporción de clases en cada partición).
- En datos temporales, la división debe ser **cronológica**: el test siempre es posterior al entrenamiento.
- Nunca se usa el conjunto de prueba durante el desarrollo del modelo (riesgo de data leakage).
- Documentar la semilla aleatoria (`random_state`) para reproducibilidad.

---

## Ejecución de experimentos — Configuración de hiperparámetros

La plataforma de ML permite configurar el experimento con distintos hiperparámetros.

### Hiperparámetros principales

| Hiperparámetro | Descripción | Ejemplo de valor |
|---|---|---|
| **Modelos a comparar** | Algoritmos que la plataforma evaluará | XGBoost, LightGBM, Random Forest, Logistic Regression |
| **Variables descartables** | Columnas que se excluyen explícitamente | `id_cliente`, `nombre` |
| **Tamaño de lote** | Muestras por actualización de gradiente | 32, 64, 128 |
| **Número de pasadas (épocas)** | Veces que el modelo ve el dataset completo | 10, 50, 100 |
| **Métrica de optimización** | Qué se maximiza/minimiza | AUC-ROC, RMSE, F1 |
| **Tiempo máximo de experimento** | Límite de duración del AutoML | 30 min, 2 h |

---

## Ejecución de experimentos — AutoML en plataformas reales

Las principales plataformas cloud ofrecen AutoML para datos estructurados.

### Comparativa de herramientas AutoML

| Plataforma | Herramienta AutoML | Capacidades destacadas |
|---|---|---|
| Azure ML | Automated ML | Clasificación, regresión, series temporales; explicabilidad integrada |
| Google Vertex AI | AutoML Tables | Integración con BigQuery; importancia de características |
| AWS SageMaker | Autopilot | Genera código editable del pipeline; varios modos de optimización |
| Databricks | AutoML (MLflow) | Genera notebooks Python; integración con Delta Lake |
| H2O.ai | H2O AutoML | Open source; stacking de modelos; leaderboard |

> Todas estas herramientas comparan automáticamente múltiples algoritmos y devuelven un leaderboard con las métricas de cada uno.

---

## Documentación de resultados del experimento

Documentar los resultados de forma rigurosa es parte del criterio de evaluación.

### Contenido mínimo del informe de experimento

| Sección | Contenido |
|---|---|
| **Configuración** | Dataset, fecha, split, hiperparámetros, modelos comparados |
| **Leaderboard** | Tabla de modelos con métricas ordenadas |
| **Conclusiones** | Qué modelo ganó y por qué; qué variables son más predictivas |
| **Fiabilidad** | Intervalo de confianza de las métricas; estabilidad en validación cruzada |
| **Avisos técnicos** | Data leakage detectado, desbalanceo de clases, drift posible |
| **Tiempo de cómputo** | Duración del experimento y coste estimado |
| **Próximos pasos** | ¿Se despliega? ¿Se necesitan más datos? ¿Reentrenar con más variables? |

---

## Métricas de evaluación de modelos predictivos

### Clasificación

| Métrica | Descripción | Cuándo usarla |
|---|---|---|
| **AUC-ROC** | Área bajo la curva ROC | Clasificación con clases desbalanceadas |
| **F1-score** | Media armónica de precisión y recall | Cuando FP y FN tienen igual coste |
| **Precisión** | TP / (TP + FP) | Minimizar falsos positivos |
| **Recall** | TP / (TP + FN) | Minimizar falsos negativos |

### Regresión

| Métrica | Descripción |
|---|---|
| **MAE** | Error absoluto medio |
| **RMSE** | Raíz del error cuadrático medio (penaliza errores grandes) |
| **R²** | Proporción de varianza explicada por el modelo |
| **MAPE** | Error porcentual absoluto medio |

---

## Integración del modelo en un pipeline productivo

Una vez seleccionado el modelo ganador, se integra en un pipeline en la nube para su uso en producción.

### Arquitectura del pipeline productivo

```
Datos nuevos (batch o streaming)
        |
        v
[1] Preprocesamiento
    - Imputación de nulos
    - Codificación de categóricas
    - Normalización / estandarización
        |
        v
[2] Inferencia del modelo
    - Cargar el modelo registrado (MLflow, SageMaker, Vertex)
    - Aplicar la función de predicción
        |
        v
[3] Posprocesamiento
    - Umbralización (clasificación)
    - Formateo de la salida
        |
        v
[4] Salida: API REST / Base de datos / Dashboard
```

---

## Integración del modelo — Registro y versionado

El modelo seleccionado debe quedar registrado en el almacén de modelos de la plataforma.

### Información que se registra con el modelo

- Nombre del modelo y versión.
- Métricas de evaluación del experimento.
- Dataset usado para entrenamiento (referencia o hash).
- Artefactos: fichero del modelo, transformadores de preprocesamiento, esquema de entrada/salida.
- Etiquetas: `entorno: staging`, `aprobado-por: data-science-lead`.

### Flujo de promoción de modelos

```
Experimento --> Modelo en "staging" --> Evaluación humana --> Modelo en "produccion"
```

> Nunca se despliega un modelo a producción sin pasar por una revisión de métricas, sesgo y fairness.

---

## Actividad práctica — UD2

### "Valoración predictiva de churn bancario"

**Escenario:** El banco CaixaNord quiere predecir qué clientes abandonarán el servicio en los próximos 30 días. Se dispone de un dataset con 50.000 filas y 25 columnas (datos demográficos, productos contratados, transacciones recientes, historial de reclamaciones).

**Tareas:**

1. Cargar el dataset en la plataforma (Azure ML o Vertex AI Sandbox).
2. Etiquetar la variable objetivo (`churn_30d`), las variables ID (`id_cliente`) y las variables de fecha.
3. Configurar la división: 75% entrenamiento, 15% validación, 10% test (estratificada).
4. Lanzar un experimento AutoML con tiempo máximo de 30 minutos, métrica AUC-ROC, comparando al menos 5 algoritmos.
5. Documentar el leaderboard, las 5 variables más importantes y los avisos del sistema.
6. Registrar el modelo ganador y desplegar un endpoint de inferencia de prueba.

**Entregable:** Informe de experimento con las 7 secciones requeridas + endpoint funcional.

---

## Puntos clave — UD2

- Los datos estructurados se organizan en filas y columnas; los casos de uso más frecuentes son clasificación y regresión.
- El **etiquetado de variables** (objetivo, ID, fecha, categórica, numérica) es el primer paso del preprocesamiento.
- La **división de datos** debe ser estratificada (clasificación) o cronológica (series temporales), y el conjunto de test se usa solo una vez.
- Los **hiperparámetros clave** de un experimento son: modelos a comparar, variables descartables, tamaño de lote, épocas y métrica de optimización.
- El **informe de experimento** debe documentar configuración, leaderboard, conclusiones, fiabilidad, avisos técnicos y tiempo de cómputo.
- El modelo ganador se **registra y versiona** antes de integrarlo en el pipeline productivo.
- El **pipeline productivo** incluye preprocesamiento, inferencia y posprocesamiento como pasos independientes y reutilizables.

---

## Criterios de evaluación — UD2

| Criterio | Indicador de logro |
|---|---|
| Preprocesa datos estructurados | Extrae, carga, etiqueta variables y configura los subconjuntos correctamente |
| Experimenta según el Plan de trabajo | Configura y ejecuta el experimento con los hiperparámetros y métricas acordados |
| Documenta los resultados | Entrega el informe de experimento con todas las secciones requeridas |
| Evalúa la fiabilidad | Interpreta las métricas, el intervalo de confianza y los avisos técnicos del sistema |
| Selecciona el modelo ganador | Justifica la selección basándose en las métricas y los avisos, no solo en la posición del leaderboard |
| Integra el modelo en un pipeline | Despliega el modelo como parte de un pipeline con preprocesamiento y posprocesamiento |
| Registra y versiona el modelo | El modelo queda registrado en el almacén con toda la metainformación requerida |

---

<!-- _class: lead -->

[← Volver a MP03](../index.md)


---

<!-- nav-slide -->

## Navegación

[← UD1 · Implementación de la platafor…](../UD1_Plataforma-servicios-IA/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD3 · Análisis de series temporales →](../UD3_Analisis-series-temporales/)
