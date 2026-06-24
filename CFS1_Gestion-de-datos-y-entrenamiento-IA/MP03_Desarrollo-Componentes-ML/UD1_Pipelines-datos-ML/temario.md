# UD1 · Pipelines de datos para ML

**Módulo:** MP03 — Desarrollo de Componentes de Machine Learning  
**Ciclo:** CFS1 — Gestión de Datos y Entrenamiento de IA  
**Duración estimada:** 12 horas lectivas

---

## 1. Introducción

En los entornos de producción reales, el código de modelado representa, en el mejor de los casos, entre el 5 y el 10 % del trabajo total de un proyecto de Machine Learning. El resto —recolección, limpieza, transformación, validación, almacenamiento y distribución de datos— recae sobre los pipelines. Sin una infraestructura de datos robusta, el modelo más sofisticado no pasa de ser un experimento de laboratorio: funciona en el cuaderno del científico de datos, pero es incapaz de mantenerse vivo, reproducible y fiable en producción.

Un pipeline de datos para ML es, en su forma más general, un flujo de trabajo automatizado que mueve datos desde sus fuentes originales hasta el punto en que son consumidos por un modelo, ya sea durante el entrenamiento o durante la inferencia. Esta definición aparentemente sencilla esconde una complejidad significativa: los datos cambian, los sistemas fallan, los volúmenes crecen, los esquemas evolucionan y los equipos se amplían. Diseñar pipelines que sobrevivan a todas estas presiones —y que lo hagan de forma auditada, reproducible y observable— es una de las habilidades fundamentales de la ingeniería de ML moderna.

Esta unidad cubre los fundamentos conceptuales de los pipelines, las herramientas de orquestación más extendidas en la industria (Apache Airflow, Prefect y Kubeflow Pipelines), el concepto de Feature Store como solución al problema del training-serving skew, y los principios de diseño que distinguen un pipeline frágil de uno preparado para producción.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Explicar qué es un pipeline de datos, por qué es necesario en contextos de ML y en qué se diferencia de un pipeline de ML completo.
- Describir las propiedades fundamentales que debe cumplir un pipeline robusto: idempotencia, determinismo, observabilidad y tolerancia a fallos.
- Instalar y configurar Apache Airflow mediante Docker Compose, y desarrollar DAGs funcionales con operadores estándar, XComs y scheduling.
- Construir pipelines de datos con Prefect usando los decoradores `@flow` y `@task`, configurando reintentos, caché y registro de ejecuciones.
- Comprender la arquitectura de Kubeflow Pipelines y su integración con plataformas cloud como Vertex AI, identificando los casos de uso donde esta herramienta aporta más valor.
- Definir el problema del training-serving skew y explicar cómo un Feature Store lo resuelve.
- Instalar y usar Feast para definir `FeatureView`, materializar características y recuperarlas tanto para entrenamiento como para inferencia en tiempo real.
- Aplicar principios de diseño robusto: gestión de dependencias, paralelismo, chunking, validación de calidad de datos integrada en el pipeline y estrategias de monitorización y alertas.

---

## 3. Fundamentos de pipelines

### 3.1 ¿Qué es un pipeline?

Un pipeline es una secuencia de pasos de procesamiento encadenados, donde la salida de cada paso alimenta la entrada del siguiente. En el contexto de datos e IA, estos pasos suelen incluir extracción desde fuentes heterogéneas (bases de datos, APIs, ficheros, streams), transformación (normalización, agregación, enriquecimiento, codificación), validación (verificación de esquemas, rangos, nulos, distribuciones) y carga en algún destino (data warehouse, feature store, almacenamiento de objetos).

Lo que distingue un pipeline de un script ad hoc no es la lógica de transformación, sino las garantías que ofrece: reproducibilidad, auditoría, tolerancia a fallos y capacidad de escalar. Un script que se ejecuta manualmente desde una terminal puede funcionar hoy, pero no es un pipeline en el sentido operacional del término.

### 3.2 DAGs: grafos acíclicos dirigidos

La representación matemática más común para modelar pipelines es el grafo acíclico dirigido (DAG, Directed Acyclic Graph). En un DAG, cada nodo representa una tarea o paso de procesamiento, y cada arista dirigida representa una dependencia: la tarea destino no puede comenzar hasta que la tarea origen haya completado exitosamente.

La propiedad acíclica —la ausencia de ciclos— es fundamental: garantiza que el pipeline siempre termina y que el orden de ejecución es determinista. Los motores de orquestación como Airflow, Prefect o Kubeflow representan todos los flujos de trabajo como DAGs, lo que permite calcular automáticamente el orden de ejecución, identificar tareas que pueden ejecutarse en paralelo y gestionar las dependencias sin intervención manual.

```python
# Representación conceptual de las dependencias de un DAG
tareas = {
    "ingestar":    [],                     # sin dependencias: se ejecuta primero
    "validar_raw": ["ingestar"],            # depende de ingestar
    "transformar": ["validar_raw"],         # depende de validar_raw
    "cargar_A":    ["transformar"],         # depende de transformar
    "cargar_B":    ["transformar"],         # depende de transformar — paralela a cargar_A
    "notificar":   ["cargar_A", "cargar_B"] # depende de ambas cargas
}
```

En este ejemplo, `cargar_A` y `cargar_B` pueden ejecutarse simultáneamente porque no tienen dependencia entre sí; un orquestador basado en DAG lo detecta automáticamente.

### 3.3 Idempotencia

Una tarea es idempotente cuando ejecutarla múltiples veces con la misma entrada produce siempre el mismo resultado sin efectos secundarios acumulativos. Esta propiedad es crítica en pipelines porque los fallos son inevitables: cuando una tarea se reintenta, no debe duplicar registros, no debe sobrescribir resultados parciales de ejecuciones anteriores y no debe generar estados inconsistentes.

Diseñar tareas idempotentes requiere estrategias concretas: usar escrituras atómicas (escribir a un fichero temporal y hacer rename al final), usar operaciones upsert en lugar de inserts ciegos, o particionar por fecha de ejecución y sobrescribir la partición completa en cada ejecución.

```python
# No idempotente: cada reintento duplica los registros
def insertar(registros, conn):
    for r in registros:
        conn.execute("INSERT INTO tabla VALUES (?)", r)

# Idempotente: la partición se borra y se reescribe completa
def insertar_particion(registros, fecha, conn):
    conn.execute(f"DELETE FROM tabla WHERE fecha = '{fecha}'")
    for r in registros:
        conn.execute("INSERT INTO tabla VALUES (?)", r)
```

### 3.4 Determinismo

Un pipeline determinista produce siempre la misma salida dado el mismo conjunto de entradas. El determinismo se rompe cuando se introducen fuentes de aleatoriedad no controladas (semillas no fijadas, timestamps en tiempo real, sorteos de muestras sin semilla) o cuando las tareas dependen de estado externo mutable.

En ML, el determinismo es especialmente importante para la reproducibilidad de experimentos: si el mismo código entrenado sobre los mismos datos produce modelos diferentes en cada ejecución, es imposible depurar regresiones de rendimiento.

### 3.5 Reintentos y tolerancia a fallos

Los fallos transitorios —timeouts de red, picos de carga en servicios externos, cortes breves de conectividad— son inevitables en sistemas distribuidos. Un pipeline robusto debe ser capaz de reintentar tareas fallidas de forma automática, con políticas de backoff exponencial para evitar saturar los sistemas afectados.

La configuración de reintentos debe acompañarse siempre de idempotencia: reintentar una tarea no idempotente puede ser peor que no reintentar. El número de reintentos y el delay entre ellos son parámetros que deben ajustarse según la naturaleza del sistema externo involucrado.

### 3.6 Observabilidad

Un pipeline que no se puede observar no se puede operar. La observabilidad incluye tres dimensiones:

- **Logs:** registro de eventos con suficiente detalle para diagnosticar fallos. Deben ser estructurados (JSON) para poder ser consultados y agregados.
- **Métricas:** tiempos de ejecución, volumetría procesada, tasas de error, latencias. Deben exportarse a sistemas como Prometheus o Datadog para construir dashboards y alertas.
- **Trazas:** seguimiento del flujo de datos a través de las distintas tareas, especialmente útil en pipelines distribuidos para identificar cuellos de botella.

### 3.7 Pipeline de datos vs. pipeline de ML

Un **pipeline de datos** se ocupa exclusivamente del movimiento, transformación y almacenamiento de datos. Su objetivo es asegurar que los datos correctos estén disponibles, en el formato correcto, en el momento correcto. Es independiente de cualquier modelo.

Un **pipeline de ML** engloba todo lo anterior y añade los pasos específicos del ciclo de vida del modelo: extracción de características, entrenamiento, evaluación, validación del modelo, registro en un model registry y despliegue. Un pipeline de ML completo puede orquestar decenas de dependencias y tardar horas en ejecutarse.

La distinción importa porque los criterios de éxito son diferentes. Un pipeline de datos se evalúa por la completitud, frescura y calidad de los datos que produce. Un pipeline de ML se evalúa también por la calidad de los modelos que genera y por su capacidad de detectar cuándo un modelo ha degradado y necesita reentrenamiento.

---

## 4. Apache Airflow

### 4.1 Arquitectura

Apache Airflow es el orquestador de flujos de trabajo más extendido en la industria de datos. Su arquitectura se compone de los siguientes elementos:

**Scheduler:** el componente central, responsable de analizar los DAGs, determinar qué tareas deben ejecutarse según las dependencias y el schedule, y enviarlas a la cola de ejecución. El scheduler escanea periódicamente el directorio de DAGs para detectar cambios.

**Executor:** el mecanismo que ejecuta las tareas. El ejecutor más usado en producción es el `CeleryExecutor` (distribuido, con workers independientes conectados a través de Redis o RabbitMQ) o el `KubernetesExecutor` (cada tarea se ejecuta en un pod efímero). Para desarrollo local se usa el `LocalExecutor` o el `SequentialExecutor`.

**Workers:** procesos que reciben tareas de la cola y las ejecutan. En el `CeleryExecutor`, los workers son procesos independientes que pueden ejecutarse en múltiples máquinas, lo que permite escalar horizontalmente.

**Metadata Database:** una base de datos relacional (PostgreSQL en producción, SQLite en desarrollo) que almacena el estado de todas las ejecuciones, las tareas, los logs y las variables de configuración.

**Web Server:** una interfaz de usuario basada en Flask que permite visualizar el estado de los DAGs, disparar ejecuciones manuales, ver logs, gestionar variables y conexiones.

**DAG Directory:** un directorio donde Airflow busca archivos Python que definen DAGs. El scheduler los escanea periódicamente para detectar cambios.

### 4.2 Instalación con Docker Compose

La forma más rápida de poner en marcha un entorno completo de Airflow en desarrollo es mediante Docker Compose. La imagen oficial incluye todos los componentes necesarios:

```bash
# Descargar el fichero docker-compose oficial
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.9.0/docker-compose.yaml'

# Crear directorios necesarios
mkdir -p ./dags ./logs ./plugins ./config

# Variable de entorno con el UID del usuario actual
echo -e "AIRFLOW_UID=$(id -u)" > .env

# Inicializar la base de datos y crear el usuario admin
docker compose up airflow-init

# Arrancar todos los servicios
docker compose up -d
```

Una vez en marcha, la interfaz web está disponible en `http://localhost:8080` con las credenciales por defecto `airflow / airflow`. La carpeta `./dags` es el directorio donde se colocan los ficheros Python con la definición de los DAGs; cualquier cambio es detectado automáticamente por el scheduler.

### 4.3 DAGs en Python

Un DAG en Airflow es un objeto Python de la clase `DAG` que declara los metadatos del flujo (identificador, schedule, fecha de inicio, configuración de reintentos) y dentro del cual se definen las tareas y sus dependencias.

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "data-team",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["data-alerts@empresa.com"],
}

with DAG(
    dag_id="ejemplo_basico",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["ejemplo", "datos"],
) as dag:

    tarea_bash = BashOperator(
        task_id="verificar_entorno",
        bash_command="echo 'Entorno listo' && python --version",
    )

    def procesar_datos(**context):
        fecha = context["ds"]
        print(f"Procesando datos para la fecha: {fecha}")
        return {"registros_procesados": 1000}

    tarea_python = PythonOperator(
        task_id="procesar_datos",
        python_callable=procesar_datos,
    )

    tarea_bash >> tarea_python
```

### 4.4 Operadores principales

**PythonOperator:** ejecuta una función Python. Es el operador más flexible y el más usado para lógica personalizada. Recibe `python_callable` (la función a ejecutar) y `op_kwargs` (argumentos adicionales). La función puede acceder al contexto de ejecución (fecha, run_id, etc.) a través del parámetro `**context`.

**BashOperator:** ejecuta un comando de shell. Útil para llamar a scripts externos, herramientas CLI (dbt, spark-submit, aws s3 cp) o realizar verificaciones rápidas del entorno.

**S3Sensor (y otros sensores):** los sensores son un tipo especial de operador que espera a que una condición externa se cumpla antes de continuar. El `S3KeySensor` espera a que un fichero o prefijo aparezca en un bucket de S3. Durante la espera, la tarea permanece en estado `running` y consulta la condición periódicamente según el parámetro `poke_interval`. Existen sensores para bases de datos, HTTP, archivos locales, particiones de Hive y prácticamente cualquier sistema externo.

### 4.5 XComs

XCom (Cross-Communication) es el mecanismo de Airflow para que las tareas compartan pequeñas cantidades de datos entre sí. Una tarea puede empujar un valor al almacén de XComs con `context["ti"].xcom_push(key="resultado", value=datos)`, y otra tarea posterior puede recuperarlo con `context["ti"].xcom_pull(task_ids="tarea_origen", key="resultado")`.

Es importante destacar que XComs están pensados para metadatos pequeños (identificadores, conteos, rutas de ficheros), no para transferir datasets completos. Para grandes volúmenes, la práctica correcta es que una tarea escriba los datos en almacenamiento intermedio (S3, GCS, una tabla) y pase la ruta o el identificador como XCom.

### 4.6 Scheduling y backfill

El parámetro `schedule_interval` acepta expresiones cron estándar (`"0 6 * * *"` para las 6:00 AM cada día), así como macros predefinidas (`@daily`, `@hourly`, `@weekly`). Airflow introduce el concepto de `data_interval`: cada ejecución del DAG tiene asociado un intervalo de tiempo que representa los datos que procesa, no el momento en que se ejecuta.

El backfill permite ejecutar un DAG para fechas pasadas, algo muy útil cuando se añade un nuevo pipeline o cuando se corrige un error y se necesita reprocesar datos históricos:

```bash
airflow dags backfill \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  mi_dag_id
```

Para que el backfill funcione correctamente, las tareas deben ser idempotentes y usar la variable de plantilla `{{ ds }}` (la fecha de ejecución) en lugar de `datetime.now()`.

### 4.7 Ejemplo completo: DAG de ingesta, transformación y validación

El siguiente DAG implementa un pipeline completo de tres etapas: descarga de datos desde una API, transformación con pandas y validación de mínimos de calidad. Las tres tareas están conectadas en secuencia y comparten rutas de fichero mediante XComs.

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests, pandas as pd

default_args = {
    "owner": "ml-team",
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
}

def ingestar_datos(**context):
    fecha = context["ds"]
    respuesta = requests.get(
        f"https://api.datos.com/eventos?fecha={fecha}",
        timeout=30
    )
    respuesta.raise_for_status()
    datos = respuesta.json()
    ruta = f"/data/raw/{fecha}/eventos.json"
    with open(ruta, "w") as f:
        import json; json.dump(datos, f)
    context["ti"].xcom_push(key="ruta_raw", value=ruta)
    return len(datos)

def transformar_datos(**context):
    ruta_raw = context["ti"].xcom_pull(task_ids="ingestar", key="ruta_raw")
    df = pd.read_json(ruta_raw)
    df = df.dropna(subset=["user_id", "evento"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hora"] = df["timestamp"].dt.hour
    ruta_procesada = ruta_raw.replace("/raw/", "/processed/").replace(".json", ".parquet")
    df.to_parquet(ruta_procesada, index=False)
    context["ti"].xcom_push(key="ruta_procesada", value=ruta_procesada)
    context["ti"].xcom_push(key="num_registros", value=len(df))

def validar_datos(**context):
    num_registros = context["ti"].xcom_pull(task_ids="transformar", key="num_registros")
    if num_registros < 100:
        raise ValueError(
            f"Solo {num_registros} registros procesados. Se esperan al menos 100."
        )
    print(f"Validacion superada: {num_registros} registros procesados.")

with DAG(
    dag_id="pipeline_ingesta_ml",
    default_args=default_args,
    start_date=datetime(2024, 6, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    ingestar = PythonOperator(task_id="ingestar", python_callable=ingestar_datos)
    transformar = PythonOperator(task_id="transformar", python_callable=transformar_datos)
    validar = PythonOperator(task_id="validar", python_callable=validar_datos)

    ingestar >> transformar >> validar
```

---

## 5. Prefect

### 5.1 Diferencias con Airflow

Prefect nació como una respuesta a las limitaciones de Airflow en entornos de desarrollo modernos. Las diferencias más relevantes son:

**Definición de flujos:** Airflow requiere que el código del DAG se ajuste a la estructura específica de sus operadores y al patrón de contexto. Prefect usa decoradores Python estándar (`@flow`, `@task`) que permiten escribir código que parece Python ordinario y puede ejecutarse sin ninguna infraestructura de Prefect.

**Pruebas locales:** ejecutar un DAG de Airflow localmente requiere levantar toda la infraestructura con Docker Compose. Un flow de Prefect se puede ejecutar directamente con `python mi_flow.py`, sin servidor ni base de datos.

**Dinámica en tiempo de ejecución:** Prefect permite crear tareas de forma dinámica (bucles, mapeos sobre listas de tamaño variable) de manera más natural que Airflow, cuya API de mapeo dinámico (`expand`) llegó tarde y con limitaciones.

**Modelo de despliegue:** Airflow requiere un scheduler siempre activo en la misma infraestructura que los DAGs. Prefect puede usar Prefect Cloud como plano de control gestionado, con workers que se ejecutan donde sea conveniente (local, EC2, Kubernetes), eliminando la carga operativa del orquestador.

### 5.2 Decoradores `@flow` y `@task`

La unidad básica de trabajo en Prefect es la tarea (`@task`). Las tareas se componen dentro de flujos (`@flow`). Prefect infiere automáticamente las dependencias entre tareas observando cómo se pasan los resultados de unas a otras.

```python
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta
import pandas as pd

@task(
    name="extraer-datos",
    retries=3,
    retry_delay_seconds=60,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1),
)
def extraer_datos(fecha: str) -> pd.DataFrame:
    print(f"Extrayendo datos para {fecha}")
    # En un caso real, aquí iría la llamada a la API o la base de datos
    return pd.DataFrame({"id": range(500), "valor": range(500)})

@task(name="transformar-datos", retries=2)
def transformar_datos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    media = df["valor"].mean()
    std = df["valor"].std()
    df["valor_norm"] = (df["valor"] - media) / std
    return df

@task(name="guardar-datos")
def guardar_datos(df: pd.DataFrame, ruta: str) -> None:
    df.to_parquet(ruta, index=False)
    print(f"Datos guardados en {ruta}: {len(df)} registros")

@flow(name="pipeline-preprocesamiento", log_prints=True)
def pipeline_preprocesamiento(fecha: str = "2024-06-01"):
    df_raw = extraer_datos(fecha)
    df_procesado = transformar_datos(df_raw)
    guardar_datos(df_procesado, f"datos/procesado_{fecha}.parquet")
    print(f"Pipeline completado para {fecha}")

if __name__ == "__main__":
    pipeline_preprocesamiento(fecha="2024-06-15")
```

### 5.3 Reintentos y caché

Los reintentos en Prefect se configuran directamente en el decorador `@task` con los parámetros `retries` y `retry_delay_seconds`. Prefect soporta también backoff exponencial con `retry_jitter_factor`, que introduce una variación aleatoria en el delay para evitar que todos los workers reintenten al mismo tiempo (thundering herd).

El sistema de caché de Prefect permite que una tarea no vuelva a ejecutarse si ya lo hizo recientemente con los mismos argumentos. La función `task_input_hash` genera una clave de caché a partir del hash de los argumentos de entrada. Esto es especialmente valioso durante el desarrollo: al reejecutar el flujo tras un fallo parcial, las tareas que ya completaron exitosamente no se vuelven a ejecutar, ahorrando tiempo y llamadas a sistemas externos.

### 5.4 Scheduling y despliegue

Para ejecutar flujos en producción con Prefect, se crean despliegues (deployments) que asocian un flow a un agente de trabajo y a una programación temporal:

```bash
# Crear y registrar un deployment con schedule cron
prefect deployment build mi_flow.py:pipeline_preprocesamiento \
  --name produccion \
  --cron "0 2 * * *" \
  --apply

# Iniciar un agente que escuche la cola y ejecute los flows
prefect agent start --pool default-agent-pool
```

---

## 6. Kubeflow Pipelines

### 6.1 Componentes como contenedores

Kubeflow Pipelines (KFP) adopta un enfoque radicalmente diferente al de Airflow o Prefect: cada componente del pipeline se ejecuta en un contenedor Docker independiente. Esto garantiza el aislamiento total entre pasos, la reproducibilidad perfecta (la imagen es inmutable) y la capacidad de escalar cada componente de forma independiente en un clúster de Kubernetes.

Un componente en KFP puede definirse de dos formas: como una función Python decorada con `@component` (KFP genera automáticamente el contenedor a partir de la función y las dependencias declaradas) o como una especificación YAML que apunta a una imagen Docker preexistente.

El intercambio de datos entre componentes se realiza a través de **artefactos** tipados: `Dataset`, `Model`, `Metrics`, `ClassificationMetrics`. Cada artefacto se escribe a un almacén central (MinIO, GCS, S3) y KFP gestiona automáticamente la orquestación de rutas entre componentes. Esto resuelve el problema de los XComs de Airflow para datos de gran tamaño.

### 6.2 DSL en Python

El SDK de Kubeflow Pipelines provee un lenguaje de dominio específico (DSL) para definir pipelines en Python:

```python
from kfp import dsl
from kfp.dsl import component, Output, Input, Dataset, Model, Metrics

@component(
    base_image="python:3.11-slim",
    packages_to_install=["pandas==2.1.0", "scikit-learn==1.3.0"]
)
def preprocesar(
    fecha: str,
    datos_salida: Output[Dataset],
):
    import pandas as pd
    df = pd.DataFrame({"feature_a": range(200), "target": range(200)})
    df.to_parquet(datos_salida.path, index=False)
    print(f"Preprocesado completado para {fecha}: {len(df)} filas")

@component(
    base_image="python:3.11-slim",
    packages_to_install=["pandas==2.1.0", "scikit-learn==1.3.0"]
)
def entrenar(
    datos_entrada: Input[Dataset],
    modelo_salida: Output[Model],
    metricas: Output[Metrics],
    n_estimadores: int = 100,
):
    import pandas as pd
    import pickle
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score

    df = pd.read_parquet(datos_entrada.path)
    X, y = df.drop("target", axis=1), df["target"]
    clf = RandomForestClassifier(n_estimators=n_estimadores, random_state=42)
    clf.fit(X, y)
    acc = accuracy_score(y, clf.predict(X))
    metricas.log_metric("accuracy_train", float(acc))
    with open(modelo_salida.path, "wb") as f:
        pickle.dump(clf, f)

@dsl.pipeline(name="pipeline-entrenamiento-v1")
def pipeline_entrenamiento(fecha: str = "2024-06-01", n_estimadores: int = 100):
    paso_prep = preprocesar(fecha=fecha)
    paso_train = entrenar(
        datos_entrada=paso_prep.outputs["datos_salida"],
        n_estimadores=n_estimadores,
    )
    paso_train.set_cpu_request("2").set_memory_request("4G")
```

### 6.3 Integración con Vertex AI

Google Vertex AI Pipelines es un servicio gestionado que ejecuta pipelines de Kubeflow Pipelines sin necesidad de gestionar la infraestructura de Kubernetes. La integración es directa: el pipeline se compila a YAML y se envía a Vertex AI mediante el SDK de Python:

```python
from kfp import compiler
from google.cloud import aiplatform

# Compilar el pipeline a YAML
compiler.Compiler().compile(pipeline_entrenamiento, "pipeline.yaml")

# Ejecutar en Vertex AI
aiplatform.init(project="mi-proyecto-gcp", location="europe-west1")

job = aiplatform.PipelineJob(
    display_name="entrenamiento-diario",
    template_path="pipeline.yaml",
    parameter_values={"fecha": "2024-06-15", "n_estimadores": 200},
)
job.submit()
```

Vertex AI gestiona automáticamente el escalado de los pods, el almacenamiento de artefactos en GCS, el linaje de metadatos en Vertex ML Metadata y la integración con Vertex Model Registry para el registro del modelo entrenado.

### 6.4 Cuándo usar Kubeflow Pipelines

KFP es la elección adecuada cuando el proyecto cumple alguna de estas condiciones: los pasos del pipeline requieren entornos de ejecución heterogéneos (distintas imágenes Docker, distintos recursos de GPU/CPU por componente); el equipo ya trabaja sobre Kubernetes; se necesita integración nativa con plataformas MLOps (Vertex AI, OpenShift AI); o cuando la trazabilidad de artefactos (modelos, datasets, métricas) es un requisito crítico de auditoría.

Para pipelines de datos sin componente de ML intensivo, Airflow o Prefect son generalmente más ágiles de desarrollar y operar. KFP añade complejidad de infraestructura que se amortiza cuando el aislamiento entre componentes y el linaje de artefactos son necesidades reales.

---

## 7. Feature Stores

### 7.1 El problema del training-serving skew

El training-serving skew es uno de los problemas más comunes y más difíciles de detectar en los sistemas de ML en producción. Ocurre cuando las características usadas durante el entrenamiento del modelo son diferentes —en su definición, su transformación o sus valores— de las características usadas durante la inferencia en producción.

Las causas más frecuentes son: la lógica de transformación está duplicada (una versión en el notebook de entrenamiento, otra en el servicio de inferencia) y las dos implementaciones divergen con el tiempo por evolución independiente; los datos de entrenamiento usan ventanas de tiempo incorrectas introduciendo data leakage; o las características se calculan en el momento del entrenamiento con datos históricos completos, pero en producción se calculan con datos en tiempo real que tienen distribuciones ligeramente diferentes.

Las consecuencias son silenciosas y graves: el modelo funciona bien en evaluación offline pero su rendimiento en producción es significativamente peor, y la causa no es obvia porque los datos individualmente parecen correctos. Diagnosticar el skew requiere comparar distribución por distribución entre el entorno de entrenamiento y el de inferencia.

### 7.2 Arquitectura de un Feature Store

Un Feature Store es un sistema especializado que centraliza la definición, el almacenamiento y el acceso a las características para ML. Su arquitectura canónica tiene tres componentes:

**Almacén offline (offline store):** optimizado para lecturas históricas de alto volumen. Almacena características con su evolución temporal completa. Tecnologías habituales: Apache Parquet en S3/GCS, BigQuery, Snowflake, Apache Hive. Se usa principalmente para generar datasets de entrenamiento con garantías de point-in-time correctness: las características que habría visto el modelo en el momento `t` son exactamente las que estaban disponibles en `t`, sin fugas del futuro.

**Almacén online (online store):** optimizado para lecturas de baja latencia (típicamente menos de 10 ms) de las características más recientes de una entidad. Tecnologías habituales: Redis, DynamoDB, Bigtable. Se usa para servir características durante la inferencia en tiempo real.

**Registro de características (feature registry):** catálogo centralizado que almacena las definiciones de las características, sus metadatos (fuente, propietario, descripción, estadísticas) y su linaje. Permite que diferentes equipos descubran y reutilicen características ya definidas, evitando duplicaciones y garantizando consistencia entre proyectos.

La **materialización** es el proceso de calcular los valores actuales de las características y cargarlos en el almacén online para que estén disponibles para la inferencia. Se ejecuta periódicamente (por ejemplo, cada hora) mediante una tarea del pipeline de datos.

### 7.3 Feast: instalación y uso

Feast (Feature Store) es la solución open-source más adoptada para Feature Stores. Soporta múltiples backends para el almacén offline y online y se integra con los principales ecosistemas cloud.

**Instalación:**

```bash
pip install feast[redis]
feast init mi-feature-store
cd mi-feature-store
```

**Definición de fuentes y FeatureViews:**

```python
# feature_repo/features.py
from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64

# Entidad: la unidad sobre la que se calculan las características
usuario = Entity(
    name="usuario_id",
    description="Identificador único del usuario",
)

# Fuente de datos: fichero Parquet local o en S3
fuente_eventos = FileSource(
    name="eventos_usuario",
    path="data/eventos_usuario.parquet",
    timestamp_field="event_timestamp",
)

# FeatureView: agrupa características relacionadas de la misma entidad
caracteristicas_usuario = FeatureView(
    name="caracteristicas_usuario",
    entities=[usuario],
    ttl=timedelta(days=7),
    schema=[
        Field(name="num_sesiones_7d", dtype=Int64),
        Field(name="valor_medio_compra", dtype=Float32),
        Field(name="dias_desde_ultima_compra", dtype=Int64),
        Field(name="tasa_devolucion", dtype=Float32),
    ],
    online=True,
    source=fuente_eventos,
    tags={"equipo": "recomendaciones", "version": "1.2"},
)
```

**Registro y materialización:**

```bash
# Registrar las definiciones en el feature registry
feast apply

# Materializar características al almacén online
feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S")
```

**Recuperación para entrenamiento (offline store con point-in-time correctness):**

```python
from feast import FeatureStore
import pandas as pd

store = FeatureStore(repo_path="feature_repo/")

# DataFrame con entidades y timestamps de referencia
# Feast devolverá las características tal como eran en cada timestamp
entidades_entrenamiento = pd.DataFrame({
    "usuario_id": [1, 2, 3, 4, 5],
    "event_timestamp": pd.to_datetime([
        "2024-05-01", "2024-05-03", "2024-05-07",
        "2024-05-10", "2024-05-15"
    ]),
})

dataset_entrenamiento = store.get_historical_features(
    entity_df=entidades_entrenamiento,
    features=[
        "caracteristicas_usuario:num_sesiones_7d",
        "caracteristicas_usuario:valor_medio_compra",
        "caracteristicas_usuario:dias_desde_ultima_compra",
        "caracteristicas_usuario:tasa_devolucion",
    ],
).to_df()
```

**Recuperación para inferencia en tiempo real (online store):**

```python
# Recuperar las características más recientes del almacén online
# Misma definición, misma lógica: esto elimina el training-serving skew
caracteristicas_online = store.get_online_features(
    features=[
        "caracteristicas_usuario:num_sesiones_7d",
        "caracteristicas_usuario:valor_medio_compra",
    ],
    entity_rows=[{"usuario_id": 42}],
).to_dict()
```

### 7.4 Hopsworks

Hopsworks es una plataforma MLOps que incluye un Feature Store de nivel empresarial como componente central. Se diferencia de Feast en que ofrece una solución más completa e integrada: gestión de modelos, pipelines de feature engineering con soporte para streaming (Flink, Spark Streaming), versionado de características, monitorización de distribuciones y una interfaz de usuario rica para la gobernanza.

Hopsworks utiliza RonDB (una variante de MySQL NDB Cluster) como almacén online, lo que le permite ofrecer latencias de acceso muy bajas con alta disponibilidad. Está disponible como SaaS (Hopsworks.ai) o como despliegue on-premise, lo que lo hace especialmente relevante para organizaciones con restricciones de privacidad de datos o que necesitan control total sobre la infraestructura.

### 7.5 Tabla comparativa

| Criterio | Feast | Hopsworks | Tecton | Vertex AI Feature Store |
|---|---|---|---|---|
| Licencia | Apache 2.0 | AGPL / Enterprise | Propietaria (SaaS) | Propietaria (GCP) |
| Almacén online | Redis, DynamoDB, Bigtable | RonDB (MySQL NDB) | DynamoDB, Redis | Bigtable |
| Almacén offline | S3/GCS/Parquet, BigQuery, Snowflake | Hudi en HDFS/S3 | S3, Snowflake | BigQuery |
| Streaming features | Limitado | Nativo (Flink/Spark) | Sí | Sí |
| UI de gobernanza | Básica | Completa | Completa | Completa |
| Curva de aprendizaje | Baja-Media | Media | Media-Alta | Baja (integrada GCP) |
| Mejor para | Startups, proyectos open-source | Empresas con on-premise | Empresas SaaS a escala | Proyectos nativos en GCP |

---

## 8. Diseño de pipelines robustos

### 8.1 Gestión de dependencias

Un pipeline bien diseñado hace explícitas todas sus dependencias: versiones de librerías, variables de entorno, ficheros de configuración, credenciales y servicios externos. La gestión de dependencias de Python debe realizarse con herramientas que produzcan ficheros de bloqueo deterministas: `pip-compile` (del paquete `pip-tools`) o `poetry lock`. Esto garantiza que el entorno de ejecución en producción es idéntico al de desarrollo y al de CI.

En entornos containerizados, cada componente del pipeline debe tener su propia imagen Docker con dependencias fijadas en el `Dockerfile` o en `requirements.txt` con versiones exactas. Las imágenes deben ser inmutables: nunca instalar dependencias en tiempo de ejecución dentro del contenedor de producción, ya que eso rompe la reproducibilidad.

Las conexiones a sistemas externos (bases de datos, APIs, almacenamiento cloud) deben gestionarse a través del sistema de secrets del orquestador o de un vault externo (HashiCorp Vault, AWS Secrets Manager), nunca hardcodeadas en el código.

### 8.2 Paralelismo

El DAG como estructura de datos hace explícito el paralelismo disponible: todas las tareas sin dependencias entre sí pueden ejecutarse de forma concurrente. Los motores de orquestación explotan este paralelismo automáticamente, pero el diseñador del pipeline puede favorecer el paralelismo dividiendo las operaciones secuenciales innecesarias en ramas independientes.

Un ejemplo concreto: si un pipeline necesita procesar datos de tres fuentes independientes y luego combinarlos, las tres tareas de extracción deben ejecutarse en paralelo, seguidas de una única tarea de combinación. No tiene sentido secuenciarlas si no hay dependencia de datos entre ellas.

En Prefect, el paralelismo se consigue con el método `submit` que devuelve futuros:

```python
from prefect import flow, task

@task
def procesar_segmento(segmento_id: int) -> dict:
    return {"segmento": segmento_id, "registros": 1000}

@flow
def pipeline_paralelo(n_segmentos: int = 10):
    # Lanzar todas las tareas en paralelo
    futuros = [procesar_segmento.submit(i) for i in range(n_segmentos)]
    # Esperar a que todas completen y recoger resultados
    resultados = [f.result() for f in futuros]
    return sum(r["registros"] for r in resultados)
```

El grado de paralelismo también está limitado por los recursos disponibles (workers, CPUs, conexiones a bases de datos) y por las restricciones de los sistemas externos (rate limits de APIs, concurrencia máxima de conexiones). Los pools de Airflow permiten limitar la concurrencia de grupos de tareas para no saturar recursos compartidos.

### 8.3 Chunking para grandes volúmenes

Procesar datasets de varios gigabytes o terabytes en una sola tarea crea problemas de memoria, de tiempo de ejecución y de tolerancia a fallos: si la tarea falla en el minuto 90, se pierde todo el trabajo del proceso. La solución es el chunking: dividir el volumen de datos en particiones manejables y procesarlas en tareas separadas.

Las estrategias de particionado más comunes son:

- **Por tiempo:** un fichero o una tarea por hora, día o mes. Es el enfoque más natural para pipelines con scheduling temporal.
- **Por rango de claves:** registros del 0 al 999999 en la primera tarea, del 1000000 al 1999999 en la segunda, etc.
- **Por entidad lógica:** una tarea por región geográfica, por categoría de producto, por cliente.

Para procesar grandes ficheros Parquet sin cargarlos completamente en memoria, DuckDB ofrece una interfaz SQL que ejecuta las consultas en streaming:

```python
import duckdb

@task
def agregar_ventas_por_dia(directorio_parquet: str) -> pd.DataFrame:
    con = duckdb.connect()
    resultado = con.execute(f"""
        SELECT
            DATE_TRUNC('day', timestamp) AS dia,
            COUNT(*)                     AS n_transacciones,
            SUM(importe)                 AS importe_total,
            AVG(importe)                 AS importe_medio
        FROM read_parquet('{directorio_parquet}/**/*.parquet')
        GROUP BY 1
        ORDER BY 1
    """).df()
    return resultado
```

### 8.4 Calidad de datos en el pipeline

La validación de la calidad de datos debe estar integrada en el pipeline como una tarea explícita, no como una comprobación manual posterior. Las dimensiones de calidad a verificar incluyen: completitud (ausencia de nulos en campos críticos), unicidad (ausencia de duplicados en claves primarias), validez de rango (valores dentro de los límites esperados), consistencia referencial (las claves foráneas existen en las tablas de referencia) y frescura (los datos tienen la antigüedad esperada).

**Great Expectations** es la librería de referencia para validación de calidad de datos en Python. Permite definir suites de expectativas en código, ejecutarlas dentro de los pipelines y generar informes HTML automáticos con los resultados:

```python
import great_expectations as gx

@task(name="validar-calidad")
def validar_calidad(ruta_parquet: str) -> None:
    context = gx.get_context()
    validator = context.sources.pandas_default.read_parquet(ruta_parquet)

    # Expectativas de completitud
    validator.expect_column_values_to_not_be_null("user_id")
    validator.expect_column_values_to_not_be_null("timestamp")

    # Expectativas de rango
    validator.expect_column_values_to_be_between("edad", min_value=0, max_value=120)
    validator.expect_column_values_to_be_between("importe", min_value=0)

    # Expectativas de cardinalidad
    validator.expect_column_values_to_be_in_set(
        "estado", value_set=["activo", "inactivo", "pendiente"]
    )

    resultado = validator.validate()
    if not resultado.success:
        n_fallidos = sum(
            1 for r in resultado.results if not r.success
        )
        raise ValueError(
            f"Validacion de calidad fallida: {n_fallidos} expectativas no cumplidas."
        )
```

### 8.5 Alertas y monitorización

Un pipeline que falla en silencio es peor que un pipeline que no existe. La estrategia de alertas debe cubrir tres niveles:

**Alertas de fallos operacionales:** notificaciones inmediatas cuando una tarea falla después de agotar todos los reintentos. Airflow y Prefect soportan callbacks de fallo que pueden enviar mensajes a Slack, PagerDuty, email o cualquier sistema de alertas. En Airflow se configura con `on_failure_callback`; en Prefect con el parámetro `on_failure` del decorador `@flow`.

**Alertas de anomalías en datos:** monitorización continua de las métricas de calidad de datos para detectar degradaciones graduales antes de que impacten al modelo. Una caída inesperada de volumetría (hoy llegaron un 40% menos de registros que ayer) o la aparición de nulos en una columna que normalmente tiene 0% pueden indicar un problema en la fuente antes de que el modelo empiece a degradarse.

**Alertas de SLA:** notificaciones cuando un pipeline no completa dentro del tiempo máximo esperado. Airflow tiene soporte nativo de SLAs por tarea mediante el parámetro `sla` en el DAG. En Prefect, los SLAs se gestionan a través de automations en Prefect Cloud.

La observabilidad de los pipelines debe incluir dashboards operacionales con métricas como: número de ejecuciones exitosas vs. fallidas en las últimas 24 horas, tiempo medio de ejecución de cada tarea con tendencia histórica, volumetría procesada por ejecución y latencia de los datos (tiempo desde que los datos se generan hasta que están disponibles en el destino).

---

## 9. Actividades prácticas

### Actividad 1 — DAG de ingesta diaria con Airflow

**Objetivo:** implementar un DAG de Airflow que automatice la ingesta diaria de datos desde una API pública, transforme los datos y los almacene en formato Parquet particionado por fecha.

**Desarrollo:**

1. Instalar Airflow con Docker Compose siguiendo los pasos de la sección 4.2. Verificar que la interfaz web está disponible en `http://localhost:8080`.
2. Crear el fichero `dags/pipeline_ingesta.py` con un DAG de tres tareas: (a) `descargar_datos`: usa un `PythonOperator` para llamar a una API pública (por ejemplo, la API de datos abiertos de AEMET o cualquier endpoint JSON público) y guardar la respuesta en `/tmp/raw/{fecha}.json`; (b) `transformar`: lee el JSON, convierte a DataFrame de pandas, filtra registros con valores nulos en campos clave y guarda en `/tmp/processed/{fecha}.parquet`; (c) `validar`: comprueba que el Parquet existe, que tiene al menos 10 registros y que no hay nulos en la columna principal.
3. Configurar el DAG con `schedule_interval="@daily"`, `catchup=False`, `retries=2` y `retry_delay=timedelta(minutes=2)`.
4. Usar XComs para pasar la ruta del fichero JSON entre `descargar_datos` y `transformar`, y el conteo de registros entre `transformar` y `validar`.
5. Activar el DAG en la interfaz web, disparar una ejecución manual y verificar que las tres tareas completan con estado verde.

**Entrega:** fichero Python del DAG y captura de pantalla de la interfaz de Airflow mostrando la ejecución exitosa con el gráfico de dependencias visible.

---

### Actividad 2 — Pipeline de preprocesamiento con Prefect

**Objetivo:** reimplementar el pipeline de la Actividad 1 usando Prefect, explotando el sistema de caché y reintentos, y ejecutarlo localmente sin infraestructura adicional.

**Desarrollo:**

1. Instalar Prefect con `pip install prefect` y verificar la instalación con `prefect version`.
2. Crear el fichero `pipeline_prefect.py` con las mismas tres tareas de la Actividad 1, implementadas como funciones decoradas con `@task` dentro de un `@flow`.
3. Configurar la tarea de descarga con `retries=3`, `retry_delay_seconds=30` y caché de 1 hora usando `cache_key_fn=task_input_hash`.
4. Ejecutar el flujo localmente la primera vez: `python pipeline_prefect.py`. Observar que las tres tareas se ejecutan.
5. Ejecutar el flujo una segunda vez con los mismos argumentos: verificar en los logs que la tarea de descarga indica que usa la caché y no vuelve a llamar a la API.
6. Lanzar Prefect Server con `prefect server start` y observar el flujo y sus dos ejecuciones en `http://localhost:4200`.
7. Comparar: ¿qué ventajas e inconvenientes tiene el enfoque de Prefect frente al de Airflow para este caso de uso?

**Entrega:** fichero Python del flujo, log de la segunda ejecución mostrando el uso de caché, y un párrafo de respuesta a la pregunta comparativa del punto 7.

---

### Actividad 3 — Feature Store con Feast

**Objetivo:** crear un Feature Store local con Feast que defina características para un caso de uso de recomendación, materialice los datos al almacén online y los recupere para entrenamiento e inferencia demostrando la eliminación del training-serving skew.

**Desarrollo:**

1. Instalar Feast con `pip install feast` y crear un repositorio con `feast init tienda-online && cd tienda-online`.
2. Generar un dataset sintético de eventos de usuario con al menos 1000 filas y columnas: `usuario_id`, `event_timestamp`, `n_clicks_7d`, `valor_medio_carrito`, `tasa_conversion`, `dias_desde_ultima_sesion`. Guardarlo como `data/eventos_usuario.parquet`.
3. En `feature_repo/features.py`, definir la `Entity` usuario y el `FeatureView` con las cuatro características del paso anterior.
4. Ejecutar `feast apply` y verificar en la salida que las definiciones se han registrado.
5. Usar `store.get_historical_features()` para generar un dataset de entrenamiento con 50 usuarios y timestamps distribuidos en el último mes. Verificar que el resultado contiene las características correctas para cada timestamp (point-in-time correctness).
6. Ejecutar `feast materialize-incremental` y usar `store.get_online_features()` para recuperar las características actuales de 3 usuarios. Comparar el código de recuperación entre entrenamiento e inferencia: debe ser la misma definición de features, solo cambia el método de acceso.

**Entrega:** ficheros `features.py` y el script de generación de datos, código de recuperación para entrenamiento e inferencia, y el DataFrame de entrenamiento resultante (primeras 10 filas).

---

### Actividad 4 — Diseño de pipeline robusto con validación de calidad integrada

**Objetivo:** construir un pipeline de Prefect con validación de calidad de datos integrada usando Great Expectations, y verificar que el pipeline detecta y reporta correctamente datos corruptos antes de procesarlos.

**Desarrollo:**

1. Instalar dependencias: `pip install prefect great-expectations pandera`.
2. Crear un dataset de entrenamiento limpio en Parquet con columnas: `user_id` (int, no nulo), `edad` (int, 18-100), `importe` (float, 0-50000), `categoria` (string, valores: "A", "B", "C").
3. Implementar un flujo Prefect de cuatro tareas: `cargar_datos`, `validar_calidad`, `transformar`, `guardar`.
4. La tarea `validar_calidad` debe usar Great Expectations para verificar: ausencia de nulos en `user_id` y `edad`, valores de `edad` entre 18 y 100, valores de `importe` mayores que 0, y valores de `categoria` dentro del conjunto permitido.
5. Añadir al `@flow` un callback `on_failure` que imprima un mensaje de alerta formateado con el nombre de la tarea fallida y el timestamp.
6. Introducir intencionalmente datos corruptos en el dataset: añadir 5 filas con `user_id=None`, 3 filas con `edad=-5` y 2 filas con `categoria="Z"`.
7. Ejecutar el pipeline con los datos corruptos y verificar que: la tarea `validar_calidad` lanza una excepción, el flujo se interrumpe sin llegar a `transformar`, y el callback de fallo muestra el mensaje de alerta.
8. Corregir los datos corruptos y verificar que el pipeline completa exitosamente.

**Entrega:** código completo del flujo, captura del log de ejecución con datos corruptos mostrando el error de validación, y captura de la ejecución exitosa con datos limpios.

---

## 10. Referencias

### Documentación oficial

- **Apache Airflow.** (2024). *Apache Airflow Documentation — Version 2.9*. Apache Software Foundation.  
  https://airflow.apache.org/docs/apache-airflow/stable/

- **Apache Airflow.** (2024). *Running Airflow in Docker*.  
  https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html

- **Prefect.** (2024). *Prefect Documentation — Prefect 3.x*.  
  https://docs.prefect.io/

- **Prefect.** (2024). *Flows and Tasks — Core Concepts*.  
  https://docs.prefect.io/concepts/flows/

- **Kubeflow Pipelines.** (2024). *Kubeflow Pipelines Documentation — SDK v2*.  
  https://www.kubeflow.org/docs/components/pipelines/

- **Kubeflow Pipelines SDK.** (2024). *KFP SDK v2 Reference*.  
  https://kubeflow-pipelines.readthedocs.io/en/stable/

- **Feast.** (2024). *Feast Documentation — Feature Store for Machine Learning*.  
  https://docs.feast.dev/

- **Feast.** (2024). *Quickstart Guide*.  
  https://docs.feast.dev/getting-started/quickstart

- **Great Expectations.** (2024). *Great Expectations Documentation*.  
  https://docs.greatexpectations.io/docs/

- **Hopsworks.** (2024). *Hopsworks Feature Store Documentation*.  
  https://docs.hopsworks.ai/

- **Google Cloud.** (2024). *Vertex AI Pipelines — Introduction*.  
  https://cloud.google.com/vertex-ai/docs/pipelines/introduction

### Libros

- Densmore, J. (2021). *Data Pipelines Pocket Reference: Moving and Processing Data for Analytics*. O'Reilly Media.  
  https://www.oreilly.com/library/view/data-pipelines-pocket/9781492087823/

- Reis, J., & Housley, M. (2022). *Fundamentals of Data Engineering: Plan and Build Robust Data Systems*. O'Reilly Media.  
  https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/

- Kleppmann, M. (2017). *Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems*. O'Reilly Media.  
  https://dataintensive.net/

- Huyen, C. (2022). *Designing Machine Learning Systems*. O'Reilly Media.  
  https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/

### Artículos de referencia

- Google. (2020). *Practitioners Guide to MLOps: A Framework for Continuous Delivery and Automation of Machine Learning*. Google Cloud.  
  https://services.google.com/fh/files/misc/practitioners_guide_to_mlops_whitepaper.pdf

- Sculley, D., et al. (2015). *Hidden Technical Debt in Machine Learning Systems*. Proceedings of NIPS 2015.  
  https://proceedings.neurips.cc/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf

---

*Unidad Didáctica 1 — MP03 Desarrollo de Componentes de ML — CFS1 Gestión de Datos y Entrenamiento de IA*
