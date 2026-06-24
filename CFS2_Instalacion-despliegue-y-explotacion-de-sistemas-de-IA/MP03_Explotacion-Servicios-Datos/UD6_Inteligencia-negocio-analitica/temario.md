# UD6 · Inteligencia de negocio y analítica avanzada

---

## 1. Introducción

La inteligencia de negocio (BI, Business Intelligence) engloba el conjunto de tecnologías, procesos y metodologías que transforman datos brutos en información accionable para la toma de decisiones empresariales. Aunque el término tiene décadas de historia, el stack tecnológico de BI ha experimentado una transformación radical en los últimos años: los data warehouses relacionales tradicionales (Teradata, Netezza) han cedido protagonismo a arquitecturas de datos modernas capaces de gestionar volúmenes y variedades de datos antes impensables, con costes y tiempos de implementación significativamente reducidos. En paralelo, la integración de modelos de machine learning en los pipelines analíticos ha difuminado la frontera entre BI descriptivo y analítica predictiva, creando una disciplina más amplia que combina ambas capacidades.

La evolución del stack de BI moderno puede entenderse como una respuesta a las limitaciones del paradigma tradicional de extracción-transformación-carga (ETL) hacia data warehouses altamente esquematizados y costosos de mantener. Las plataformas de data lake, basadas en almacenamiento de objetos de bajo coste (Amazon S3, Azure Blob Storage, Google Cloud Storage), eliminaron la restricción de almacenamiento y permitieron retener datos crudos sin necesidad de un esquema predefinido. Sin embargo, la falta de garantías de calidad y la dificultad de gobernar un lago de datos no estructurado llevó al paradigma del **lakehouse**: una arquitectura que combina la flexibilidad y el bajo coste del data lake con las garantías ACID, el soporte transaccional y las capacidades analíticas del data warehouse, mediante capas de abstracción como Delta Lake, Apache Iceberg o Apache Hudi.

La ingeniería de analítica moderna requiere también repensar cómo se organizan y transforman los datos dentro de la plataforma. Herramientas como **dbt** (data build tool) han popularizado el paradigma de transformación en SQL dentro del warehouse (ELT vs. ETL tradicional), con versionado de código, tests de calidad integrados y generación automática de documentación de linaje. La orquestación de estos pipelines mediante herramientas como Apache Airflow, Prefect o Dagster ha sustituido a los scripts de ETL ad hoc, aportando observabilidad, gestión de dependencias y manejo de fallos. El conjunto de estas herramientas y prácticas configura lo que la industria denomina el **Modern Data Stack**.

Esta unidad aborda el stack de BI moderno desde una perspectiva de ingeniería: arquitecturas de referencia, herramientas de transformación y orquestación, procesamiento batch y streaming, catalogación y calidad de datos, y las implicaciones de la integración de modelos ML en entornos de analítica empresarial. Se presta especial atención a los **data contracts** como mecanismo de gobernanza que permite escalar la analítica sin sacrificar la confiabilidad de los datos, y a la capa semántica como interfaz entre la complejidad técnica de la plataforma de datos y las necesidades de los usuarios de negocio.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Describir la arquitectura medallion (bronze/silver/gold) y justificar la partición de responsabilidades entre cada capa en un entorno lakehouse de producción.
2. Comparar las características técnicas de las principales herramientas de BI (Power BI, Tableau, Apache Superset, Metabase) y seleccionar la más adecuada para un caso de uso dado en función de los requisitos de la organización.
3. Implementar un pipeline de transformación de datos con dbt sobre un data warehouse en la nube, incluyendo modelos, tests de calidad y generación de documentación de linaje.
4. Diseñar y desplegar un pipeline de orquestación con Apache Airflow que integre ingestión de datos, transformación con dbt y publicación de resultados en una herramienta de BI.
5. Diferenciar los casos de uso de procesamiento batch y streaming, y describir los componentes de una arquitectura de streaming con Apache Kafka y Flink.
6. Configurar un catálogo de datos con Apache Atlas o DataHub para documentar los activos de datos de una plataforma analítica, incluyendo esquemas, propietarios y clasificaciones.
7. Implementar validaciones de calidad de datos en un pipeline ETL utilizando Great Expectations, definiendo expectativas y configurando el sistema de alertas ante fallos.
8. Describir el concepto de data contract, sus componentes (esquema, SLA de calidad, propietario, consumidores) y su rol en la gobernanza de datos analíticos a escala.

---

## 3. Arquitectura del stack de BI moderno

### 3.1 Data Warehouse, Data Lake y Lakehouse

El **data warehouse** tradicional es una base de datos relacional optimizada para consultas analíticas complejas (OLAP), con un esquema predefinido y estricto que estructura los datos antes de cargarlos. Sus fortalezas son la consistencia, el rendimiento de consulta y la madurez de las herramientas de BI que lo acompañan. Sus limitaciones son el coste de almacenamiento y el tiempo necesario para modelar y cargar nuevas fuentes de datos.

El **data lake** adopta el enfoque contrario: almacena datos en su formato original (ficheros JSON, CSV, Parquet, imágenes, logs) en almacenamiento de objetos de bajo coste, sin esquema predefinido. Su fortaleza es la flexibilidad y el coste; su debilidad, la dificultad para garantizar la calidad y la consistencia de los datos, y el riesgo de convertirse en un "pantano de datos" (data swamp) difícil de explotar.

El **lakehouse** combina ambos paradigmas mediante capas de abstracción que añaden semántica transaccional y calidad de datos al almacenamiento de objetos:

- **Delta Lake** (Databricks): formato de tabla abierto basado en Parquet con transacciones ACID, versionado (time travel), soporte de esquema evolutivo y optimizaciones de rendimiento (Z-ordering, data skipping).
- **Apache Iceberg**: formato de tabla de alto rendimiento para datos a escala de petabytes, con soporte para actualizaciones a nivel de fila, particionado oculto y snapshots inmutables.
- **Apache Hudi** (Hadoop Upserts Deletes and Incrementals): optimizado para casos de uso de ingesta incremental y actualizaciones frecuentes (CDC, Change Data Capture).

### 3.2 Arquitectura medallion (bronze/silver/gold)

La arquitectura medallion es un patrón de organización de datos en capas que estructura el lakehouse en tres niveles con garantías de calidad crecientes:

| Capa | Nombre | Contenido | Garantías | Consumidores |
|---|---|---|---|---|
| Bronze | Datos brutos | Datos ingestados sin transformar. Réplica fiel de la fuente. | Integridad de la ingesta | Ingenieros de datos |
| Silver | Datos limpios | Datos validados, deduplicados, con tipos correctos y unificados entre fuentes | Calidad básica, esquema estable | Científicos de datos, analistas avanzados |
| Gold | Datos de negocio | Agregaciones, métricas de negocio, modelos dimensionales listos para consumo | Alta calidad, rendimiento optimizado | Usuarios de BI, dashboards, APIs |

La separación en capas tiene implicaciones prácticas importantes:

- La capa **bronze** actúa como buffer de idempotencia: si una transformación posterior es incorrecta, los datos originales están preservados para reprocesarlos.
- La capa **silver** es donde se resuelven las heterogeneidades entre fuentes: estandarización de identificadores, unificación de formatos de fecha, deduplicación de registros.
- La capa **gold** es la única capa expuesta directamente a herramientas de BI y usuarios de negocio. Su diseño debe optimizar el rendimiento de consulta y la comprensibilidad del modelo de datos.

### 3.3 Herramientas de BI: comparativa

| Criterio | Power BI | Tableau | Apache Superset | Metabase |
|---|---|---|---|---|
| Modelo de licencia | Comercial (Microsoft) | Comercial (Salesforce) | Open source (Apache) | Open source / SaaS |
| Coste por usuario/mes | ~9-20 € (Pro) | ~70-75 € (Creator) | Gratuito (self-hosted) | Gratuito (self-hosted) |
| Integración Microsoft | Excelente (Azure, Teams) | Limitada | No nativa | No nativa |
| Capacidades ML | AutoML integrado | TabPy (Python) | Sin integración nativa | Sin integración nativa |
| Curva de aprendizaje | Media | Alta | Media-Alta | Baja |
| Escalabilidad | Alta (Premium) | Alta | Depende de infra propia | Media |
| API para embebido | Sí (Embed) | Sí (Embedding API) | Sí (nativa) | Sí (nativa) |
| Caso de uso principal | Organizaciones Microsoft | Análisis complejo ad hoc | Plataformas data internas | Self-service BI interno |

---

## 4. Transformación de datos con dbt

### 4.1 El paradigma ELT y dbt

**dbt** (data build tool) implementa el paradigma ELT (Extract, Load, Transform): los datos se extraen de las fuentes y se cargan al warehouse o lakehouse en su forma bruta, y las transformaciones se ejecutan dentro del motor analítico mediante SQL. Este enfoque aprovecha la potencia de cómputo de los motores modernos (BigQuery, Snowflake, Redshift, DuckDB) y elimina la necesidad de un servidor ETL intermedio.

dbt convierte las transformaciones SQL en un **DAG de modelos**: cada modelo es un fichero SQL que define una tabla o vista en el warehouse, y las dependencias entre modelos se declaran mediante la función `ref()`. dbt resuelve el orden de ejecución, materializa los resultados y gestiona las dependencias automáticamente.

```sql
-- models/silver/clientes_limpio.sql
-- Modelo silver: limpieza y estandarización de datos de clientes
{{ config(
    materialized='incremental',
    unique_key='cliente_id',
    on_schema_change='append_new_columns'
) }}

WITH fuente AS (
    SELECT * FROM {{ ref('bronze_crm_clientes') }}
    {% if is_incremental() %}
        WHERE fecha_modificacion > (SELECT MAX(fecha_modificacion) FROM {{ this }})
    {% endif %}
),

limpio AS (
    SELECT
        cliente_id,
        TRIM(UPPER(nombre)) AS nombre,
        LOWER(email) AS email,
        REGEXP_REPLACE(telefono, '[^0-9+]', '') AS telefono,
        CAST(fecha_alta AS DATE) AS fecha_alta,
        COALESCE(pais, 'ES') AS pais,
        _loaded_at
    FROM fuente
    WHERE cliente_id IS NOT NULL
      AND email LIKE '%@%'  -- Validación básica de email
)

SELECT * FROM limpio
```

### 4.2 Tests de calidad en dbt

dbt integra un sistema de tests declarativos que se ejecutan automáticamente tras la materialización de los modelos:

```yaml
# models/silver/schema.yml
models:
  - name: clientes_limpio
    description: "Tabla de clientes limpia y estandarizada desde CRM"
    columns:
      - name: cliente_id
        description: "Identificador único del cliente"
        tests:
          - not_null
          - unique
      - name: email
        description: "Email del cliente"
        tests:
          - not_null
          - unique
      - name: pais
        description: "Código de país ISO 3166-1 alfa-2"
        tests:
          - accepted_values:
              values: ['ES', 'MX', 'AR', 'CO', 'CL', 'PE']
      - name: fecha_alta
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= '2010-01-01'"
```

Los tests de dbt son ejecutables con `dbt test` y producen un informe detallado de los fallos. Los fallos pueden configurarse como warnings (el pipeline continúa) o errores (el pipeline se detiene).

### 4.3 Documentación y linaje en dbt

dbt genera automáticamente un sitio web de documentación con `dbt docs generate && dbt docs serve` que incluye:
- Descripción de cada modelo y columna.
- Grafo de linaje interactivo que muestra las dependencias entre modelos.
- Resultados de tests.
- Estadísticas de las tablas materializadas.

Este grafo de linaje es la implementación más directa del concepto de trazabilidad en el contexto de pipelines analíticos: permite responder a preguntas como "¿qué modelos se ven afectados si cambia la fuente X?" o "¿de qué fuentes depende el dashboard Y?"

---

## 5. Orquestación con Apache Airflow

### 5.1 Conceptos fundamentales de Airflow

**Apache Airflow** es la plataforma de orquestación de pipelines de datos más extendida en el sector. Un pipeline en Airflow se define como un **DAG** (Directed Acyclic Graph) en código Python, donde cada nodo es una **tarea** (Task) y las aristas definen las dependencias entre tareas.

Las componentes de infraestructura de Airflow son:
- **Scheduler**: determina cuándo ejecutar cada DAG y cada tarea según el schedule definido.
- **Executor**: lanza la ejecución de las tareas (LocalExecutor para desarrollo, CeleryExecutor o KubernetesExecutor para producción distribuida).
- **Web UI**: interfaz de monitorización que muestra el estado de los DAGs, el log de ejecuciones y permite disparar ejecuciones manuales.
- **Metadata Database**: PostgreSQL o MySQL que almacena el estado de todas las ejecuciones.

```python
# dags/pipeline_analitica_ventas.py
from airflow import DAG
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'equipo-datos',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['datos@empresa.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='pipeline_analitica_ventas',
    default_args=default_args,
    description='Pipeline diario de analítica de ventas',
    schedule_interval='0 6 * * *',  # Todos los días a las 6:00 UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ventas', 'analitica'],
) as dag:

    # Tarea 1: Ingesta de datos desde CRM
    ingestar_crm = BashOperator(
        task_id='ingestar_crm',
        bash_command='python /opt/airflow/scripts/ingest_crm.py --date {{ ds }}'
    )

    # Tarea 2: Ejecutar transformaciones dbt (capa silver)
    transformar_silver = BashOperator(
        task_id='transformar_silver',
        bash_command='dbt run --select tag:silver --project-dir /opt/dbt'
    )

    # Tarea 3: Tests de calidad dbt
    test_calidad = BashOperator(
        task_id='test_calidad',
        bash_command='dbt test --select tag:silver --project-dir /opt/dbt'
    )

    # Tarea 4: Transformaciones gold (solo si los tests pasan)
    transformar_gold = BashOperator(
        task_id='transformar_gold',
        bash_command='dbt run --select tag:gold --project-dir /opt/dbt'
    )

    # Definición de dependencias
    ingestar_crm >> transformar_silver >> test_calidad >> transformar_gold
```

### 5.2 Monitorización y alertas en Airflow

La monitorización de los DAGs en producción requiere configurar callbacks de notificación que alerten al equipo ante fallos o comportamientos anómalos:

- `on_failure_callback`: se ejecuta cuando una tarea falla.
- `on_retry_callback`: se ejecuta en cada reintento.
- `on_success_callback`: permite notificar al finalizar el pipeline.
- `sla_miss_callback`: se activa cuando una tarea supera el SLA de tiempo definido.

Airflow expone métricas en formato StatsD, que pueden consumirse en Prometheus y visualizarse en Grafana: número de DAGs activos, tasa de fallos, duración de las ejecuciones, lag de la cola del scheduler.

---

## 6. Procesamiento batch y streaming

### 6.1 Diferencias fundamentales batch vs. streaming

| Dimensión | Procesamiento Batch | Procesamiento Streaming |
|---|---|---|
| Latencia de los datos | Horas o días | Segundos o milisegundos |
| Volumen por ejecución | Grande (GBs, TBs) | Pequeño (eventos individuales o micro-batches) |
| Complejidad técnica | Baja | Alta |
| Coste operativo | Bajo | Alto |
| Tolerancia a fallos | Reejecutar el batch | Mecanismos de checkpointing, exactly-once |
| Casos de uso | Reportes diarios, entrenamiento ML | Alertas en tiempo real, monitorización, fraude |

### 6.2 Apache Kafka

**Apache Kafka** es la plataforma de streaming de eventos más extendida en entornos empresariales. Sus conceptos fundamentales son:

- **Topic**: canal lógico de eventos. Los productores publican en topics y los consumidores leen de topics.
- **Partition**: un topic se divide en particiones, distribuidas entre los brokers del clúster. Las particiones son la unidad de paralelismo de Kafka.
- **Consumer Group**: conjunto de consumidores que procesan las particiones de un topic en paralelo. Kafka garantiza que cada partición es consumida por un único consumidor del grupo.
- **Offset**: posición de un consumidor dentro de una partición. El commit de offset determina qué mensajes ya fueron procesados.
- **Retention**: Kafka retiene los mensajes durante un período configurable (días o semanas), permitiendo el reprocesamiento desde cualquier punto.

```python
# Productor Kafka en Python (kafka-python)
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['kafka-broker:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',          # Confirmación de todos los réplicas (mayor durabilidad)
    retries=3
)

# Publicar evento de transacción
evento = {
    "transaccion_id": "TXN-20240315-78432",
    "cliente_id": 78432,
    "importe": 150.00,
    "timestamp": "2024-03-15T14:05:33Z",
    "tipo": "compra"
}

producer.send('transacciones', value=evento)
producer.flush()
```

### 6.3 Apache Flink

**Apache Flink** es el motor de procesamiento de streams de referencia para casos de uso que requieren baja latencia, semántica exactly-once y operaciones de estado complejas (ventanas, joins de streams). Sus características diferenciales sobre Kafka Streams o Spark Structured Streaming son:

- **Procesamiento de tiempo de evento**: Flink distingue entre tiempo de procesamiento (cuando el dato llega al sistema) y tiempo de evento (cuando el evento ocurrió en el mundo real). El procesamiento basado en tiempo de evento, con watermarks para gestionar el retraso de los datos, permite resultados correctos incluso con eventos desordenados.
- **Checkpointing distribuido**: Flink implementa el algoritmo de Chandy-Lamport para snapshots de estado consistentes, lo que garantiza exactly-once incluso ante fallos del clúster.
- **Operaciones de ventana**: windows temporales (tumbling, sliding, session), sobre las que se aplican agregaciones (COUNT, SUM, AVG, max, min).

---

## 7. Catalogación y calidad de datos

### 7.1 Catálogos de datos: Apache Atlas y DataHub

Un **catálogo de datos** es el inventario centralizado de los activos de datos de la organización: qué datos existen, dónde están almacenados, quién es el propietario, quién los consume, cómo son los esquemas, qué nivel de calidad tienen y qué restricciones de privacidad aplican.

**Apache Atlas** es la solución de catálogo de datos del ecosistema Hadoop. Provee:
- Catálogo de metadatos con clasificaciones jerárquicas (tipos de entidades, atributos, relaciones).
- Linaje de datos nativo integrado con Hive, HBase, Sqoop, Kafka y Spark.
- Motor de búsqueda sobre metadatos y clasificaciones.
- Integración con Apache Ranger para políticas de acceso basadas en clasificaciones.

**DataHub** (creado por LinkedIn, actualmente proyecto de código abierto) es la alternativa más moderna. Sus ventajas sobre Atlas son:
- Arquitectura event-driven basada en Kafka, más escalable.
- Soporte de ingestión para más de 50 fuentes de datos (BigQuery, Snowflake, dbt, Airflow, Looker, etc.) mediante conectores estándar.
- Interfaz de usuario más moderna y APIs más completas.
- Soporte de linaje de columnas, no solo de tablas.

**Amundsen** (creado por Lyft) es otra alternativa popular, especialmente fuerte en capacidades de búsqueda y descubrimiento de datos por parte de analistas y científicos de datos.

### 7.2 Calidad de datos con Great Expectations

**Great Expectations** (GE) es el estándar de facto para la validación de calidad de datos en pipelines de Python. El paradigma central es la **Expectation**: una afirmación verificable sobre los datos ("la columna `email` no debe tener nulos", "los valores de `importe` deben ser positivos", "la distribución de `edad` debe estar entre 18 y 120").

```python
import great_expectations as gx

# Crear o cargar un Data Context
context = gx.get_context()

# Definir un datasource
datasource = context.sources.add_pandas_filesystem(
    name="datos_ventas",
    base_directory="/data/silver/ventas/"
)

# Crear una Expectation Suite
suite = context.add_expectation_suite("ventas_silver_suite")

# Añadir expectativas
validator = context.get_validator(
    batch_request=...,
    expectation_suite_name="ventas_silver_suite"
)

validator.expect_column_values_to_not_be_null("cliente_id")
validator.expect_column_values_to_be_unique("transaccion_id")
validator.expect_column_values_to_be_between("importe", min_value=0.01, max_value=100000)
validator.expect_column_values_to_match_regex(
    "email",
    regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)
validator.expect_table_row_count_to_be_between(min_value=1000, max_value=1000000)

# Ejecutar validación
results = validator.validate()

# Construir Data Docs (informe HTML)
context.build_data_docs()
```

La integración de GE en pipelines de Airflow se realiza mediante el operador `GreatExpectationsOperator`, que detiene el pipeline si la validación falla, evitando la propagación de datos de baja calidad a las capas siguientes.

---

## 8. Integración de ML con BI y capa semántica

### 8.1 Embedded analytics y modelos ML en dashboards

La **embedded analytics** (analítica embebida) integra capacidades de BI —dashboards, visualizaciones, tablas interactivas— directamente en aplicaciones de negocio, sin que el usuario tenga que salir de su flujo de trabajo para consultar una plataforma de BI separada. Los casos de uso incluyen dashboards de rendimiento embebidos en un CRM, o visualizaciones de KPIs directamente en un ERP.

La integración de modelos ML con herramientas de BI puede adoptar varias formas:

1. **Predicciones pre-calculadas en la capa gold**: el modelo ML se ejecuta en un pipeline batch (Airflow + Spark/pandas), y los resultados se almacenan en una tabla gold del warehouse. La herramienta de BI lee esta tabla como cualquier otra. Es el enfoque más sencillo y el más adecuado para casos donde las predicciones no necesitan ser en tiempo real.

2. **Python en el servidor de BI**: Power BI, Tableau y Superset permiten ejecutar scripts Python o R para generar visualizaciones o transformaciones personalizadas. Esto permite usar directamente modelos sklearn o statsmodels dentro del flujo de BI.

3. **Feature store + endpoint de predicción**: el dashboard consulta en tiempo real un endpoint de ML (FastAPI, Triton) para obtener predicciones actualizadas. Requiere mayor infraestructura pero permite analítica en tiempo real.

### 8.2 La capa semántica

La **capa semántica** (semantic layer) es una capa de abstracción entre los datos físicos del warehouse y los usuarios de BI. Traduce el modelo físico (tablas, columnas, joins) a conceptos de negocio (métricas, dimensiones, filtros) que los usuarios de negocio entienden sin necesidad de conocer el modelo de datos subyacente.

Las herramientas de capa semántica modernas incluyen:
- **dbt Semantic Layer**: define métricas directamente en el proyecto dbt con la especificación MetricFlow.
- **Cube.js** (ahora Cube): capa semántica independiente que puede conectarse a cualquier warehouse y expone las métricas via API REST o GraphQL.
- **LookML de Looker**: el lenguaje de modelado de Looker para definir dimensiones, métricas y exploraciones reutilizables.

```yaml
# dbt/models/metrics/metricas_ventas.yml — definición de métricas con MetricFlow
metrics:
  - name: ingresos_totales
    description: "Suma de ingresos netos de ventas"
    type: simple
    label: "Ingresos Totales"
    type_params:
      measure:
        name: importe_neto
        agg: sum
    filter: |
      {{ Dimension('estado') }} = 'completada'

  - name: tasa_conversion
    description: "Porcentaje de leads que convierten en cliente"
    type: ratio
    label: "Tasa de Conversión"
    type_params:
      numerator:
        name: nuevos_clientes
        agg: count_distinct
      denominator:
        name: leads_total
        agg: count_distinct
```

### 8.3 Data Contracts

Los **data contracts** son acuerdos formales, ejecutables técnicamente, entre los productores y consumidores de un conjunto de datos. Especifican:

- **Esquema**: campos, tipos, restricciones de nulidad, valores permitidos.
- **SLA de calidad**: tasa de completitud mínima, tasa de unicidad, máximo porcentaje de nulos.
- **SLA de disponibilidad**: hora máxima de actualización diaria, tiempo máximo de latencia.
- **Propietario**: equipo o persona responsable del dato.
- **Consumidores declarados**: qué dashboards, modelos ML o APIs dependen de este dato.
- **Versión y proceso de deprecación**: cómo se gestionan los cambios que rompen la compatibilidad.

La herramienta **Soda** implementa data contracts como código verificable:

```yaml
# contracts/ventas_silver.yml — Data Contract para la tabla silver de ventas
dataset: ventas_silver
owner: equipo-datos-ventas@empresa.com
schedule: "0 6 * * *"  # Debe estar actualizada antes de las 6:00 UTC

columns:
  - name: transaccion_id
    data_type: VARCHAR
    nullable: false
    unique: true
  - name: importe
    data_type: DECIMAL(12,2)
    nullable: false
    checks:
      - type: numeric_min
        value: 0.01

checks:
  - type: row_count_between
    min: 500
    max: 500000
  - type: freshness
    column: fecha_transaccion
    max_age: 26h  # La tabla no puede tener más de 26 horas de antigüedad
```

El incumplimiento de un data contract dispara alertas automáticas a los consumidores afectados, permitiendo una respuesta coordinada antes de que los datos incorrectos lleguen a los dashboards de negocio.

---

## 9. Actividades prácticas

### Actividad 1 — Implementación de arquitectura medallion con dbt

**Descripción**: El formador proporcionará acceso a un entorno DuckDB o BigQuery con datos de ventas crudos en una capa bronze (tablas de pedidos, clientes y productos sin normalizar, con valores nulos y duplicados). Implementa un proyecto dbt con al menos cuatro modelos: dos modelos silver (clientes_limpio, pedidos_limpio) y dos modelos gold (ventas_por_dia, top_clientes_mes). Define tests de calidad en el fichero schema.yml para cada columna clave. Ejecuta el pipeline completo con `dbt run && dbt test`. Genera la documentación con `dbt docs` y captura el grafo de linaje. Identifica y documenta las transformaciones realizadas en cada capa y justifica las decisiones de diseño.

**Entregable**: Proyecto dbt (directorio completo) + captura del grafo de linaje + informe de calidad de tests (dos páginas).

**Criterios de evaluación**: Correcta implementación del modelo en tres capas, completitud y pertinencia de los tests, calidad de la documentación de modelos y columnas, corrección del SQL.

---

### Actividad 2 — Pipeline de orquestación con Apache Airflow

**Descripción**: Usando Docker Compose para desplegar Apache Airflow localmente (imagen oficial `apache/airflow`), implementa un DAG que orqueste el pipeline de analítica diseñado en la actividad anterior. El DAG debe incluir: una tarea de verificación de disponibilidad de los datos fuente, ejecución de los modelos dbt silver, ejecución de los tests de calidad (con fallo del pipeline si los tests no pasan), ejecución de los modelos gold, y una tarea final que registre en un fichero de log la hora de finalización y las métricas del pipeline (número de filas procesadas, tiempo de ejecución). Configura el DAG para ejecutarse diariamente a las 6:00 UTC. Verifica el funcionamiento en la UI de Airflow e implementa al menos un test de fallo controlado (introduciendo datos inválidos en la fuente).

**Entregable**: Fichero `docker-compose.yml` + fichero del DAG Python + capturas de la UI de Airflow mostrando ejecución exitosa y fallida.

**Criterios de evaluación**: Funcionalidad completa del DAG, correcta gestión de dependencias entre tareas, manejo del fallo de calidad con notificación, documentación del DAG.

---

### Actividad 3 — Validación de calidad con Great Expectations

**Descripción**: Sobre el mismo dataset de ventas, implementa una suite de validación de calidad con Great Expectations. Define al menos 12 expectativas que cubran: completitud (no nulos en columnas clave), unicidad (sin duplicados en identificadores), rangos de valores (importes positivos, fechas en rango razonable), integridad referencial (clientes en tabla pedidos existen en tabla clientes), y distribución estadística (la media del importe no debe desviarse más del 30% respecto al día anterior). Integra la ejecución de GE como tarea en el DAG de Airflow de la actividad anterior. Genera los Data Docs y analiza los resultados cuando se introduce intencionadamente un conjunto de datos con un 5% de registros nulos en el campo importe.

**Entregable**: Código de la suite de expectativas + captura de Data Docs + análisis del impacto de los datos degradados.

**Criterios de evaluación**: Cobertura y pertinencia de las expectativas, correcta integración en Airflow, calidad del análisis del impacto.

---

### Actividad 4 — Dashboard de BI con capa semántica

**Descripción**: Despliega Apache Superset localmente (Docker) y conéctalo al data warehouse de la actividad 1 (DuckDB o BigQuery). Crea un dashboard de "Analítica de Ventas" que incluya: KPI de ingresos totales del mes actual vs. mes anterior, gráfico de serie temporal de ventas diarias de los últimos 90 días, distribución de ventas por categoría de producto, tabla de top 10 clientes por valor total de compra, y un mapa de ventas por región si los datos lo permiten. Define en Superset al menos dos métricas virtuales (Calculated Columns) que no estén precalculadas en las tablas gold. Documenta las decisiones de diseño del dashboard: qué información añade cada visualización y a qué tipo de usuario de negocio está dirigida.

**Entregable**: Capturas del dashboard en Superset + fichero de exportación JSON del dashboard + documento de diseño (una página).

**Criterios de evaluación**: Completitud y corrección del dashboard, calidad de las visualizaciones elegidas, pertinencia de las métricas virtuales, claridad del documento de diseño.

---

## 10. Referencias

- **dbt — Documentación oficial**: guía de inicio, modelos, tests, semantic layer y documentación. Disponible en: [https://docs.getdbt.com/](https://docs.getdbt.com/)

- **Apache Airflow — Documentación oficial**: conceptos, operadores, providers y guías de despliegue. Disponible en: [https://airflow.apache.org/docs/](https://airflow.apache.org/docs/)

- **Apache Kafka — Documentación oficial**: conceptos, configuración de producción y API. Disponible en: [https://kafka.apache.org/documentation/](https://kafka.apache.org/documentation/)

- **Apache Flink — Documentación oficial**: API de DataStream, procesamiento de tiempo de evento y tolerancia a fallos. Disponible en: [https://nightlies.apache.org/flink/flink-docs-stable/](https://nightlies.apache.org/flink/flink-docs-stable/)

- **Delta Lake — Documentación oficial**: formato de tabla, transacciones ACID y optimizaciones. Disponible en: [https://docs.delta.io/latest/index.html](https://docs.delta.io/latest/index.html)

- **Apache Iceberg — Documentación oficial**: especificación del formato y guías de integración. Disponible en: [https://iceberg.apache.org/docs/latest/](https://iceberg.apache.org/docs/latest/)

- **Great Expectations — Documentación oficial**: guía de inicio, tipos de expectativas y integración con pipelines. Disponible en: [https://docs.greatexpectations.io/](https://docs.greatexpectations.io/)

- **DataHub — Documentación oficial**: arquitectura, conectores de ingestión y API de metadatos. Disponible en: [https://datahubproject.io/docs/](https://datahubproject.io/docs/)

- **Apache Superset — Documentación oficial**: instalación, configuración y desarrollo de dashboards. Disponible en: [https://superset.apache.org/docs/intro](https://superset.apache.org/docs/intro)

- **Medallion Architecture — Databricks**: descripción del patrón bronze/silver/gold y casos de uso. Disponible en: [https://www.databricks.com/glossary/medallion-architecture](https://www.databricks.com/glossary/medallion-architecture)

- **Data Contracts — Soda documentation**: implementación práctica de contratos de datos. Disponible en: [https://docs.soda.io/soda/data-contracts.html](https://docs.soda.io/soda/data-contracts.html)

- **MetricFlow — dbt Semantic Layer**: definición de métricas y capa semántica con dbt. Disponible en: [https://docs.getdbt.com/docs/build/about-metricflow](https://docs.getdbt.com/docs/build/about-metricflow)

---

*UD6 · MP03 Explotación de Servicios de Datos y Analítica · CFS2 Instalación, despliegue y explotación de sistemas de IA*
