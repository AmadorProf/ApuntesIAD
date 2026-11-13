# UD5 · Gestión, versionado y cumplimiento normativo de los conjuntos de datos

**Módulo:** MP01 · Procesamiento de datos para IA
**Programa:** CFS1 — Gestión de datos y entrenamiento IA
**Nivel:** CFS Nivel 3 · Inteligencia Artificial y Datos

---

## Introducción

En los proyectos de inteligencia artificial, el dato ocupa una posición análoga a la que el código fuente ocupa en el desarrollo de software tradicional: es el recurso central sobre el que gira todo el proceso de construcción, validación y puesta en producción de un modelo. Sin embargo, durante años la industria invirtió grandes esfuerzos en sistematizar el control de versiones del código —mediante herramientas como Git— mientras los conjuntos de datos se gestionaban de manera informal, con nombres de archivo del tipo `dataset_final_v3_definitivo.csv`. Esta asimetría tiene consecuencias graves: experimentos que no pueden reproducirse, modelos que degradan su rendimiento sin causa aparente, auditorías que no pueden completarse y, en contextos regulados, sanciones económicas y legales de considerable magnitud.

La madurez alcanzada por la ingeniería de datos en la última década ha producido un ecosistema de herramientas y marcos conceptuales que permite tratar los datos con el mismo rigor que el código. El versionado de conjuntos, el registro de metadatos, la trazabilidad del linaje, la gobernanza institucional y el cumplimiento normativo forman hoy un continuo que todo profesional de la IA debe conocer con profundidad.

Esta unidad didáctica aborda ese continuo de forma progresiva. Comienza por las herramientas concretas de versionado de datos —con especial atención a DVC y su integración con Git— y asciende hacia los marcos de gobernanza corporativa y los requisitos que impone la regulación europea, en particular el RGPD y el EU AI Act. A lo largo de todo el recorrido se presta atención tanto a los fundamentos conceptuales como a los aspectos prácticos de implementación, con ejemplos de comandos y fragmentos de código que ilustran cómo se aplican estos principios en entornos reales.

El dominio de estos contenidos no es opcional para quien aspire a trabajar en proyectos de IA en el mercado europeo: la regulación exige documentar, trazar y proteger los datos de entrenamiento de manera explícita, y los equipos que no hayan incorporado estas prácticas a su flujo de trabajo habitual se encontrarán en una posición de desventaja tanto técnica como legal.

---

## Objetivos de aprendizaje

Al finalizar esta unidad el alumnado será capaz de:

1. Explicar los fundamentos del versionado de datos y configurar un flujo de trabajo básico con DVC integrado en un repositorio Git.
2. Conectar DVC con almacenamientos remotos en la nube (AWS S3, Google Cloud Storage, Azure Blob Storage) y con servidores SFTP.
3. Registrar y rastrear conjuntos de datos mediante MLflow Datasets y comprender las capacidades de versionado transaccional de Delta Lake.
4. Distinguir entre metadatos técnicos y de negocio, y describir la arquitectura y el uso básico de herramientas de catalogación como DataHub, OpenMetadata y Apache Atlas.
5. Explicar el concepto de linaje de datos y su importancia para la trazabilidad y la auditoría de proyectos de IA.
6. Describir las áreas de conocimiento del marco DAMA-DMBOK y los roles principales en un programa de gobernanza de datos.
7. Aplicar los principios clave del RGPD a proyectos de IA, identificando las bases legales válidas, las obligaciones de minimización y los derechos de los interesados.
8. Interpretar los requisitos del EU AI Act en materia de calidad y documentación de datos para sistemas de IA de alto riesgo.
9. Describir y comparar las principales técnicas de anonimización y pseudoanonimización, evaluando sus garantías y limitaciones.
10. Implementar controles de acceso basados en roles y atributos, y configurar mecanismos básicos de auditoría de accesos a datos sensibles.

---

## 1. Versionado de datos

### 1.1 DVC (Data Version Control): fundamentos y flujo de trabajo

DVC (Data Version Control) es una herramienta de código abierto diseñada para extender las capacidades de Git al dominio de los datos y los modelos de machine learning. La premisa de DVC es sencilla pero poderosa: Git gestiona el código y los metadatos, mientras que DVC gestiona los artefactos grandes —conjuntos de datos, modelos entrenados, archivos de características— que no pueden almacenarse eficientemente en un repositorio Git por razones de tamaño y rendimiento. Ambos sistemas trabajan juntos de manera que el historial de versiones del código y el de los datos quedan sincronizados y son mutuamente referenciables.

**Instalación y configuración inicial.** DVC puede instalarse mediante pip, conda o como paquete del sistema operativo. La forma más habitual en entornos de desarrollo Python es:

```bash
pip install dvc
# Con soporte para S3:
pip install "dvc[s3]"
# Con soporte para GCS:
pip install "dvc[gs]"
# Con soporte para Azure:
pip install "dvc[azure]"
```

Una vez instalado, el primer paso en cualquier proyecto es inicializar DVC dentro de un repositorio Git existente:

```bash
git init mi-proyecto-ia
cd mi-proyecto-ia
dvc init
```

El comando `dvc init` crea una carpeta `.dvc/` en la raíz del repositorio, que contiene la configuración del proyecto, el archivo de configuración del almacenamiento remoto y una carpeta de caché local. Los archivos generados por `dvc init` deben añadirse a Git:

```bash
git add .dvc .dvcignore
git commit -m "Inicializar DVC"
```

**Añadir archivos al seguimiento de DVC.** Cuando se quiere versionar un archivo de datos, se utiliza el comando `dvc add`:

```bash
dvc add data/raw/train.csv
```

Este comando realiza dos acciones: mueve el contenido del archivo a la caché local de DVC (por defecto en `.dvc/cache/`) y crea un archivo de seguimiento con extensión `.dvc` —en este caso, `data/raw/train.csv.dvc`— que contiene el hash MD5 del archivo original, su tamaño y su ruta. Este archivo `.dvc` es pequeño, está en formato YAML y puede (y debe) ser versionado con Git. Además, DVC modifica automáticamente el archivo `.gitignore` para excluir el archivo de datos original del seguimiento de Git, evitando así que se suba por error al repositorio.

El flujo de trabajo resultante es el siguiente:

```bash
# Añadir el archivo de datos al seguimiento de DVC
dvc add data/raw/train.csv

# Versionar el archivo .dvc con Git
git add data/raw/train.csv.dvc data/raw/.gitignore
git commit -m "Añadir dataset de entrenamiento v1"
git tag -a "dataset-v1.0" -m "Primera versión del dataset"
```

Cuando el conjunto de datos se actualiza —por ejemplo, al incorporar nuevas muestras— el proceso se repite:

```bash
# Actualizar el archivo con nuevos datos
dvc add data/raw/train.csv

# El hash en train.csv.dvc habrá cambiado
git add data/raw/train.csv.dvc
git commit -m "Actualizar dataset con 5000 nuevas muestras"
git tag -a "dataset-v1.1" -m "Dataset ampliado"
```

Para recuperar una versión anterior del conjunto de datos basta con hacer checkout a ese commit de Git y luego ejecutar `dvc checkout`:

```bash
git checkout dataset-v1.0
dvc checkout
```

**Push y pull con almacenamiento remoto.** La caché local de DVC almacena los datos en el disco local, lo que resulta insuficiente para el trabajo en equipo. DVC permite configurar almacenamientos remotos donde se publican y desde donde se descargan los artefactos. La sección 1.2 detalla la configuración de estos almacenamientos; una vez configurado un remoto con nombre `origin`, el flujo de sincronización es:

```bash
# Subir datos al almacenamiento remoto
dvc push

# Descargar datos desde el almacenamiento remoto
dvc pull
```

Estos comandos transfieren únicamente los artefactos referenciados por los archivos `.dvc` presentes en el commit actual de Git, lo que garantiza la coherencia entre el código y los datos.

**Pipelines con DVC.** Además del versionado de artefactos individuales, DVC permite definir pipelines de procesamiento de datos mediante el archivo `dvc.yaml`. Cada etapa del pipeline declara sus dependencias (inputs) y outputs, lo que permite a DVC detectar qué etapas necesitan reejecutarse cuando cambian sus entradas. Esto convierte DVC en un sistema de reproducibilidad completo para proyectos de machine learning.

```yaml
stages:
  preprocesar:
    cmd: python src/preprocesar.py
    deps:
      - src/preprocesar.py
      - data/raw/train.csv
    outs:
      - data/procesado/train_limpio.parquet
  entrenar:
    cmd: python src/entrenar.py
    deps:
      - src/entrenar.py
      - data/procesado/train_limpio.parquet
    outs:
      - modelos/clasificador.pkl
    metrics:
      - metricas/resultados.json
```

Ejecutar `dvc repro` analiza el grafo de dependencias y re-ejecuta solo las etapas que han cambiado, de manera análoga a como funciona `make` pero con seguimiento automático de hashes para datos y modelos.

### 1.2 DVC con almacenamiento remoto (S3, GCS, Azure Blob, SFTP)

El almacenamiento remoto en DVC cumple la misma función que un servidor de repositorios Git como GitHub o GitLab: es el lugar centralizado donde el equipo publica y desde donde descarga los artefactos grandes. DVC soporta una amplia variedad de backends.

**Amazon S3.** Para configurar un bucket de S3 como almacenamiento remoto:

```bash
dvc remote add -d mi-remoto s3://mi-bucket/dvc-store
dvc remote modify mi-remoto region eu-west-1
git add .dvc/config
git commit -m "Configurar remoto S3"
```

Las credenciales de AWS se gestionan a través de los mecanismos estándar de la SDK de AWS: variables de entorno (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`), el archivo `~/.aws/credentials` o roles de IAM en entornos de EC2.

**Google Cloud Storage.** El proceso es análogo:

```bash
dvc remote add -d mi-remoto gs://mi-bucket/dvc-store
```

La autenticación se realiza mediante la CLI de Google Cloud (`gcloud auth application-default login`) o a través de una cuenta de servicio cuya clave se referencia con la variable de entorno `GOOGLE_APPLICATION_CREDENTIALS`.

**Azure Blob Storage.** Con Azure, la cadena de conexión se puede proporcionar directamente o a través de una variable de entorno:

```bash
dvc remote add -d mi-remoto azure://mi-contenedor/dvc-store
dvc remote modify mi-remoto connection_string "DefaultEndpointsProtocol=https;..."
```

**SFTP.** Para entornos on-premise o cuando no se dispone de acceso a la nube pública:

```bash
dvc remote add -d mi-remoto sftp://servidor.ejemplo.com/ruta/dvc-store
dvc remote modify mi-remoto user mi-usuario
```

La autenticación SFTP puede realizarse con clave SSH o con contraseña, aunque el uso de claves SSH se recomienda por razones de seguridad.

Una consideración importante en entornos corporativos es la separación entre el almacenamiento de datos de desarrollo (accesible para el equipo de ciencia de datos) y el de producción (con acceso más restringido). DVC permite definir múltiples remotos con distintos niveles de acceso y seleccionar el remoto activo según el entorno.

### 1.3 MLflow Datasets y registro de conjuntos

MLflow es una plataforma de código abierto para la gestión del ciclo de vida del machine learning desarrollada por Databricks. Aunque su uso más extendido es el seguimiento de experimentos (parámetros, métricas y artefactos de modelos), desde la versión 2.4 incorpora la entidad `mlflow.data` para el registro y seguimiento de conjuntos de datos.

El registro de un dataset en MLflow permite asociar a cada ejecución de experimento el conjunto de datos exacto —con su origen, su esquema y su hash— que se utilizó para entrenar o evaluar el modelo. Esto resuelve un problema habitual: semanas o meses después de un experimento, es frecuente no saber con exactitud qué versión del dataset se utilizó.

```python
import mlflow
import mlflow.data
import pandas as pd
from mlflow.data.pandas_dataset import PandasDataset

# Cargar el dataset
df = pd.read_csv("data/procesado/train_limpio.csv")

# Crear un objeto Dataset de MLflow
dataset: PandasDataset = mlflow.data.from_pandas(
    df,
    source="data/procesado/train_limpio.csv",
    name="train_limpio",
    targets="etiqueta"
)

# Registrar el dataset en una ejecución
with mlflow.start_run():
    mlflow.log_input(dataset, context="training")
    # ... resto del código de entrenamiento
```

La información registrada incluye el hash del dataset, el esquema inferido, el número de filas y columnas, y el contexto de uso (entrenamiento, validación, test). Esta información queda almacenada en el servidor de seguimiento de MLflow y es consultable tanto desde la interfaz web como mediante la API Python.

MLflow Datasets es una solución complementaria, no sustitutiva, de DVC. Mientras DVC gestiona el almacenamiento y el versionado del contenido de los archivos, MLflow Datasets registra el uso de esos archivos en el contexto de experimentos específicos.

### 1.4 Delta Lake y versionado en data lakes

Delta Lake es un formato de almacenamiento de código abierto desarrollado inicialmente por Databricks que añade capacidades ACID (Atomicidad, Consistencia, Aislamiento y Durabilidad) sobre sistemas de almacenamiento de objetos como S3, ADLS o GCS. A diferencia de los formatos de archivo planos como Parquet o CSV, Delta Lake mantiene un registro de transacciones (`_delta_log/`) que hace posible el versionado automático de las tablas.

Cada operación de escritura sobre una tabla Delta —inserción, actualización, eliminación, fusión— genera una nueva entrada en el log de transacciones. Esta arquitectura permite acceder a cualquier versión anterior de la tabla mediante la funcionalidad de *time travel*:

```python
from delta import DeltaTable
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("ejemplo-delta") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .getOrCreate()

# Leer la versión actual
df_actual = spark.read.format("delta").load("s3://mi-bucket/tablas/clientes")

# Leer la versión 5
df_v5 = spark.read.format("delta") \
    .option("versionAsOf", 5) \
    .load("s3://mi-bucket/tablas/clientes")

# Leer el estado en un momento concreto
df_ayer = spark.read.format("delta") \
    .option("timestampAsOf", "2026-06-01 00:00:00") \
    .load("s3://mi-bucket/tablas/clientes")
```

En el contexto del entrenamiento de modelos de IA, Delta Lake resuelve de manera natural el problema de la reproducibilidad en pipelines que consumen datos de tablas que se actualizan continuamente. Al registrar la versión o el timestamp del snapshot utilizado para entrenar cada modelo, es posible reconstruir exactamente el estado del dataset en cualquier momento futuro, lo que resulta especialmente relevante para auditorías y para la conformidad con el EU AI Act.

---

## 2. Catálogos de datos y metadatos

### 2.1 Metadatos técnicos y de negocio: tipos y diferencias

Los metadatos son datos sobre los datos: describen las características, el origen, la estructura, el significado y el contexto de uso de los conjuntos de datos. En proyectos de IA, los metadatos son tan importantes como los propios datos, porque sin ellos es imposible evaluar si un conjunto de datos es adecuado para un propósito concreto, cumple con los requisitos normativos o puede integrarse con otras fuentes.

Los **metadatos técnicos** describen las propiedades físicas y estructurales de los datos: el esquema (nombres y tipos de columnas), el formato de almacenamiento (Parquet, CSV, JSON), el tamaño, la codificación de caracteres, las estadísticas descriptivas básicas (cardinalidad, proporción de nulos, distribución de valores), la localización (ruta en el sistema de archivos o bucket), y la información de linaje (de qué fuente proviene el dato y qué transformaciones ha sufrido). Los metadatos técnicos los genera y consume principalmente el sistema de datos.

Los **metadatos de negocio**, por su parte, capturan el significado y el contexto organizacional de los datos: qué representa cada campo en términos de negocio, qué unidades o rangos válidos tiene, quién es el propietario del dato, con qué frecuencia se actualiza, cuál es su nivel de clasificación de sensibilidad (público, interno, confidencial, restringido) y para qué procesos o decisiones de negocio se utiliza. Los metadatos de negocio los generan y consumen principalmente las personas: analistas de negocio, data stewards, responsables de cumplimiento.

La distinción entre ambos tipos es importante porque requieren herramientas, procesos y actores distintos. Un catálogo de datos moderno debe ser capaz de gestionar ambos tipos de metadatos de forma integrada y de mantenerlos actualizados de manera automatizada o semiautomatizada.

### 2.2 DataHub: arquitectura y uso básico

DataHub es una plataforma de catalogación de datos de código abierto desarrollada originalmente por LinkedIn y posteriormente donada a la comunidad. Su arquitectura es la de un grafo de metadatos: todos los activos de datos —tablas, pipelines, dashboards, modelos de ML, conjuntos de datos de entrenamiento— se representan como entidades en un grafo cuyos nodos son los activos y cuyas aristas son las relaciones entre ellos (propietario, linaje, consumidor, productor).

La arquitectura de DataHub se articula en torno a tres componentes principales. El primero es el servicio de metadatos (GMS, Generic Metadata Service), que expone una API REST y GraphQL para la ingestión y consulta de metadatos. El segundo es el servicio de frontend, que proporciona la interfaz web para la búsqueda, exploración y edición de metadatos. El tercero es la capa de ingestión, basada en conectores (llamados *ingestion sources*) que extraen metadatos de fuentes externas —bases de datos, data warehouses, herramientas de BI, sistemas de orquestación— y los publican en el grafo de DataHub.

Una de las fortalezas de DataHub para proyectos de IA es su capacidad para rastrear el linaje de modelos de machine learning: qué datasets se usaron para entrenar un modelo, qué versión de ese modelo está en producción y qué decisiones de negocio dependen de sus predicciones. Esta información es esencial tanto para la depuración de problemas en producción como para la conformidad con el EU AI Act.

### 2.3 OpenMetadata y Apache Atlas

**OpenMetadata** es otra plataforma de catalogación de código abierto que compite directamente con DataHub. Su propuesta de valor diferencial es una API unificada basada en un modelo de metadatos extensible y una experiencia de usuario especialmente cuidada para la colaboración entre equipos técnicos y de negocio. OpenMetadata incluye funcionalidades nativas para la gestión de la calidad de datos (mediante la definición y ejecución de tests sobre las tablas catalogadas), la gestión del glosario de negocio y la gestión de la clasificación de datos sensibles. Su arquitectura es más sencilla que la de DataHub, lo que facilita su despliegue en entornos con recursos limitados.

**Apache Atlas** es la solución de catalogación del ecosistema Hadoop/Cloudera. Aunque su adopción en nuevos proyectos ha disminuido frente a DataHub y OpenMetadata, sigue siendo ampliamente utilizado en organizaciones con infraestructura Hadoop existente. Atlas se integra de manera nativa con las herramientas del ecosistema Apache (Hive, HBase, Kafka, Spark) y proporciona capacidades robustas de linaje de datos y clasificación de activos. Su modelo de metadatos es extensible mediante tipos definidos por el usuario, lo que permite adaptarlo a dominios específicos.

### 2.4 Linaje de datos: trazabilidad end-to-end

El linaje de datos (data lineage) es la capacidad de rastrear el origen de un dato y todas las transformaciones que ha sufrido desde su captura hasta su uso final. En el contexto de proyectos de IA, el linaje abarca tres dimensiones principales: el linaje a nivel de dataset (qué datasets se generaron a partir de qué otros datasets y mediante qué transformaciones), el linaje a nivel de columna (cómo se derivó cada campo de los campos de las fuentes) y el linaje a nivel de modelo (qué datasets se usaron para entrenar qué modelos y en qué experimentos).

La trazabilidad end-to-end tiene implicaciones directas en al menos cuatro áreas. En reproducibilidad, permite reconstruir exactamente el estado de los datos que produjo un resultado concreto. En depuración, permite identificar la fuente de un problema de calidad de datos siguiendo la cadena de transformaciones hacia atrás. En auditoría, permite demostrar a reguladores que los datos utilizados en un sistema de IA cumplen con los requisitos normativos aplicables. Y en gestión del impacto, permite evaluar qué modelos o productos se verán afectados si una fuente de datos cambia o deja de estar disponible.

---

## 3. Gobernanza de datos

### 3.1 Marco DAMA-DMBOK: áreas de conocimiento

El Data Management Body of Knowledge (DMBOK), publicado por DAMA International, es el marco de referencia más ampliamente reconocido para la gestión profesional de datos. En su segunda edición (2017), DAMA-DMBOK organiza la gestión de datos en once áreas de conocimiento interrelacionadas.

La **arquitectura de datos** define la estructura conceptual, lógica y física de los activos de datos de la organización, estableciendo los principios y estándares que guían el diseño de sistemas de datos. El **modelado y diseño de datos** cubre las técnicas y convenciones para representar los datos mediante modelos conceptuales, lógicos y físicos. El **almacenamiento y operaciones de datos** trata la gestión de las bases de datos y sistemas de almacenamiento en su ciclo de vida operativo. La **seguridad de datos** comprende las políticas y controles para proteger los datos frente a accesos no autorizados, pérdida o corrupción.

La **integración e interoperabilidad de datos** aborda los procesos y herramientas para mover, consolidar y transformar datos entre sistemas. Los **documentos y contenidos** cubren la gestión de datos no estructurados. La **gestión de datos de referencia y maestros** se ocupa de los datos compartidos y reutilizados en toda la organización (maestros de productos, clientes, proveedores, etc.). El **almacenamiento de datos y business intelligence** cubre la arquitectura y operación de data warehouses y plataformas analíticas.

La **metadatos** gestionan la información sobre los propios datos, con los catálogos y glosarios como herramientas principales. La **calidad de datos** comprende los procesos para medir, monitorizar y mejorar la adecuación de los datos a su propósito. Finalmente, el **gobierno de datos** —en el centro del marco— es el área que define las políticas, estructuras organizativas, procesos de decisión y métricas que rigen el ejercicio de las demás áreas.

Para proyectos de IA, las áreas de mayor relevancia inmediata son las de metadatos, calidad de datos, seguridad de datos y gobernanza, que se interrelacionan directamente con los requisitos del EU AI Act.

### 3.2 Roles en gobernanza: Data Owner, Data Steward, Data Engineer

La gobernanza de datos no es únicamente un asunto tecnológico; es fundamentalmente un asunto de personas, procesos y responsabilidades. Los tres roles nucleares en cualquier programa de gobernanza son el Data Owner, el Data Steward y el Data Engineer, aunque en organizaciones grandes pueden existir roles adicionales como el Chief Data Officer (CDO) o el Data Privacy Officer (DPO).

El **Data Owner** (propietario del dato) es un rol de negocio, generalmente ejercido por un directivo o responsable de área, que ostenta la responsabilidad última sobre un dominio de datos específico. Sus responsabilidades incluyen autorizar el acceso a los datos de su dominio, aprobar las políticas de clasificación y retención, y tomar decisiones sobre el uso de los datos en proyectos nuevos. El Data Owner no trabaja directamente con los sistemas de datos, pero es quien debe autorizar cualquier decisión significativa sobre ellos.

El **Data Steward** (custodio del dato) es el rol operativo de la gobernanza. Es el punto de contacto técnico-funcional para los datos de un dominio específico, y sus responsabilidades incluyen mantener actualizada la documentación y los metadatos de negocio, gestionar las solicitudes de acceso, monitorizar la calidad de los datos y escalar problemas al Data Owner cuando sea necesario. En organizaciones de tamaño mediano, un mismo profesional puede ejercer como Data Steward para múltiples dominios de datos.

El **Data Engineer** es el profesional técnico responsable de construir y mantener los pipelines, las arquitecturas de almacenamiento y las herramientas que hacen posible que los datos fluyan de manera fiable desde las fuentes hasta los consumidores. En el contexto de la gobernanza, el Data Engineer es quien implementa técnicamente las políticas decididas por el Data Owner y el Data Steward: configura los controles de acceso, implementa las rutinas de retención y eliminación de datos, instrumenta el linaje automatizado y garantiza que los sistemas cumplan con los estándares de seguridad establecidos.

### 3.3 Políticas de retención y ciclo de vida del dato

Una política de retención de datos define cuánto tiempo deben conservarse los datos, en qué formato y con qué nivel de acceso, y qué debe hacerse con ellos cuando expirar el periodo de retención. En proyectos de IA, las políticas de retención tienen dos motivaciones principales, que a veces entran en tensión: la necesidad de conservar datos para reproducir experimentos, reentrenar modelos o cumplir con obligaciones de auditoría, y la obligación legal —especialmente bajo el RGPD— de no conservar datos personales más allá del tiempo necesario para el propósito que justificó su recogida.

El ciclo de vida de un conjunto de datos en un proyecto de IA típicamente pasa por las siguientes fases: adquisición (recogida de los datos brutos de las fuentes), procesamiento (limpieza, transformación y enriquecimiento), uso (entrenamiento, validación y evaluación de modelos), archivo (conservación en almacenamiento de bajo coste para cumplimiento o reproducibilidad) y eliminación (borrado seguro cuando ya no se justifica la retención).

La eliminación segura es un aspecto frecuentemente descuidado. Los datos no deben simplemente borrarse del sistema de archivos; en función de la sensibilidad de los datos y del tipo de almacenamiento, puede ser necesario sobrescribir el espacio físico, destruir las claves de cifrado (técnica conocida como *crypto-shredding*) o emitir certificados de destrucción que puedan aportarse en una auditoría.

---

## 4. Cumplimiento normativo

### 4.1 RGPD: obligaciones clave para proyectos de IA

El Reglamento General de Protección de Datos (RGPD, Reglamento UE 2016/679) establece el marco normativo para el tratamiento de datos personales en la Unión Europea. Sus implicaciones para proyectos de IA son amplias y deben considerarse desde las primeras fases del diseño.

**Bases legales.** El RGPD exige que todo tratamiento de datos personales descanse sobre una base legal explícita (artículo 6). Las más relevantes para proyectos de IA son el consentimiento del interesado, la ejecución de un contrato, el cumplimiento de una obligación legal y el interés legítimo del responsable del tratamiento. La elección de la base legal no es arbitraria: condiciona los derechos de los interesados y los requisitos de documentación aplicables. En particular, el uso del consentimiento como base legal en proyectos de IA plantea desafíos prácticos importantes, porque el consentimiento debe ser granular, revocable e informado, y el modelo entrenado sobre datos de un interesado que retira su consentimiento puede requerir medidas técnicas específicas (como el *machine unlearning*) para cumplir efectivamente con el derecho al olvido.

**Minimización de datos.** El principio de minimización (artículo 5.1.c) exige que solo se traten los datos personales que sean adecuados, pertinentes y limitados a lo necesario en relación con los fines del tratamiento. En el diseño de sistemas de IA, esto implica evaluar sistemáticamente si cada variable de entrenamiento es realmente necesaria para el objetivo del modelo, o si puede ser sustituida por una variable menos invasiva con capacidad predictiva equivalente.

**Portabilidad.** El derecho a la portabilidad de los datos (artículo 20) permite al interesado recibir sus datos personales en un formato estructurado, de uso común y lectura mecánica, y transmitirlos a otro responsable del tratamiento. En sistemas de IA personalizados —como sistemas de recomendación o perfiles de riesgo individuales— esto requiere implementar mecanismos de exportación de los datos de usuario en formatos interoperables como JSON o CSV.

**Evaluación de impacto (EIPD).** Cuando el tratamiento de datos pueda entrañar un alto riesgo para los derechos y libertades de las personas, el RGPD exige realizar una Evaluación de Impacto relativa a la Protección de Datos (artículo 35). Los sistemas de IA que realizan perfilado, toman decisiones automatizadas con efectos significativos o tratan datos a gran escala generalmente caen dentro de esta obligación.

### 4.2 EU AI Act: requisitos de calidad y documentación de datos para sistemas de alto riesgo

El Reglamento de Inteligencia Artificial de la Unión Europea (EU AI Act, Reglamento UE 2024/1689) establece un marco regulatorio basado en el riesgo para los sistemas de IA. Los sistemas clasificados como de **alto riesgo** —que incluyen, entre otros, los utilizados en infraestructura crítica, educación, empleo, crédito, justicia, servicios esenciales y aplicaciones de seguridad— están sujetos a los requisitos más exigentes, entre los que destacan los relacionados con la calidad y documentación de los datos.

El artículo 10 del EU AI Act establece que los sistemas de IA de alto riesgo que utilizan técnicas que implican el entrenamiento con datos deben desarrollarse con datos de entrenamiento, validación y prueba que cumplan criterios de calidad específicos. En concreto, los datos deben ser objeto de prácticas de gobernanza y gestión adecuadas, incluyendo el análisis de su pertinencia, representatividad, ausencia de errores y completitud en relación con el propósito previsto del sistema. La norma exige también que los datos se examinen en busca de posibles sesgos que puedan conducir a resultados discriminatorios, especialmente cuando los outputs del sistema pueden tener consecuencias significativas para las personas.

La documentación técnica exigida por el EU AI Act (artículo 11 y Anexo IV) debe incluir una descripción detallada de los datos de entrenamiento, validación y prueba: las fuentes de los datos, las características principales, los criterios de selección, los procedimientos de limpieza y preprocesamiento, las métricas de calidad y los procedimientos de etiquetado. Esta documentación debe estar disponible para las autoridades nacionales competentes y para los organismos de evaluación de conformidad.

La entrada en vigor gradual del EU AI Act —con los primeros plazos de cumplimiento para sistemas de alto riesgo a partir de agosto de 2026— hace que el diseño de sistemas de documentación y trazabilidad de datos sea ya una prioridad para los equipos de IA en el mercado europeo.

### 4.3 Anonimización y pseudoanonimización: técnicas y limitaciones

La distinción entre anonimización y pseudoanonimización es fundamental en el contexto del RGPD. Los datos verdaderamente **anonimizados** —aquellos de los que se ha eliminado de manera irreversible cualquier posibilidad de identificar a la persona a la que se refieren— quedan fuera del ámbito de aplicación del RGPD. Los datos **pseudoanonimizados** —aquellos en los que se ha sustituido la información directamente identificadora por un pseudónimo, pero que pueden re-identificarse mediante información adicional— siguen siendo datos personales y están sujetos al RGPD.

**K-anonimato.** El k-anonimato, propuesto por Samarati y Sweeney en los años noventa, garantiza que en un conjunto de datos publicado, cada registro sea indistinguible de al menos otros k-1 registros en base a los atributos cuasi-identificadores (edad, código postal, sexo, etc.). La implementación práctica requiere generalizar o suprimir atributos hasta que se cumple la condición. Por ejemplo, si k=5 y hay solo tres personas de 34 años en el municipio de Pamplona, se generaliza la edad a un rango (30-40) o el municipio a la comunidad autónoma. La limitación principal del k-anonimato es su vulnerabilidad al ataque de homogeneidad: si todos los registros de un grupo k-anónimo comparten el mismo valor del atributo sensible, un atacante puede inferir ese valor sin necesidad de re-identificar al individuo.

**L-diversidad.** La l-diversidad, propuesta por Machanavajjhala et al. (2007), extiende el k-anonimato exigiendo que cada grupo de registros equivalentes contenga al menos l valores bien representados del atributo sensible. Esto mitiga el ataque de homogeneidad, pero introduce su propia vulnerabilidad: el ataque de similitud, donde los l valores distintos del atributo sensible son semánticamente similares (por ejemplo, distintas enfermedades cardiovasculares).

**Differential Privacy.** La privacidad diferencial, formalizada por Dwork et al. (2006), proporciona una garantía matemática formal sobre el grado de información que puede extraerse sobre un individuo de los resultados de una consulta o de un modelo. La idea central es que el resultado de cualquier análisis sobre un conjunto de datos debe ser aproximadamente igual tanto si un individuo concreto está incluido en el conjunto como si no lo está. Esto se logra inyectando ruido calibrado mediante el mecanismo de Laplace o el mecanismo gaussiano. La privacidad diferencial tiene la ventaja de ser composicional y de ofrecer garantías cuantificables, pero presenta el inconveniente de degradar la utilidad de los datos cuando el presupuesto de privacidad (epsilon) es muy restrictivo. Bibliotecas como Google's DP Library, OpenDP o TensorFlow Privacy facilitan la implementación de mecanismos de privacidad diferencial en pipelines de machine learning.

Una advertencia importante: la anonimización verdadera es extremadamente difícil de lograr en conjuntos de datos ricos. Investigaciones como la de Narayanan y Shmatikoff (2008), que re-identificaron usuarios en el conjunto de datos de Netflix a partir de sus patrones de valoración, demuestran que incluso conjuntos de datos aparentemente anonimizados pueden ser re-identificables cuando se combinan con otras fuentes de información. Esta realidad debe tenerse en cuenta al evaluar el riesgo residual de cualquier técnica de anonimización.

### 4.4 Gestión del consentimiento y derechos ARCO+F

Los derechos ARCO+F son los derechos que el RGPD reconoce a los interesados: Acceso, Rectificación, Cancelación (supresión), Oposición, más los derechos de limitación del tratamiento, portabilidad y el derecho a no ser objeto de decisiones automatizadas (artículos 15-22). La letra F se refiere coloquialmente al derecho al olvido (del inglés *Forget*), que es la vertiente más relevante para sistemas de IA.

Gestionar el ejercicio de estos derechos en sistemas de IA plantea desafíos técnicos no triviales. El derecho de acceso obliga a poder identificar todos los datos personales de un individuo en todos los sistemas del responsable, lo que en arquitecturas de datos complejas puede requerir búsquedas en docenas de tablas y sistemas. El derecho de rectificación obliga no solo a corregir los datos en el sistema fuente, sino a propagar la corrección a todos los sistemas derivados. El derecho al olvido en el contexto de modelos de IA es especialmente desafiante, porque un modelo entrenado sobre datos de un individuo puede haber aprendido patrones que no desaparecen al borrar los datos del conjunto de entrenamiento.

Las técnicas emergentes de *machine unlearning* abordan este último problema: buscan modificar los pesos de un modelo para que "olvide" la contribución de un subconjunto específico de datos de entrenamiento sin necesidad de reentrenar el modelo desde cero. Aunque el campo está en rápida evolución, no existe todavía un estándar establecido que garantice un olvido completo y verificable.

---

## 5. Seguridad y control de acceso a datos

### 5.1 Cifrado en reposo y en tránsito

El cifrado es la primera línea de defensa para proteger los datos contra accesos no autorizados. Se aplica en dos contextos distintos que requieren mecanismos y herramientas diferentes.

El **cifrado en reposo** protege los datos mientras están almacenados, de manera que un actor que obtenga acceso físico o lógico al medio de almacenamiento no pueda leer los datos sin la clave de cifrado. Los principales proveedores de nube ofrecen cifrado en reposo por defecto para sus servicios de almacenamiento de objetos (S3 SSE, Azure Storage Service Encryption, Google Cloud Storage), utilizando AES-256. La gestión de las claves de cifrado es un aspecto crítico: debe utilizarse un servicio gestionado de gestión de claves (AWS KMS, Azure Key Vault, Google Cloud KMS) en lugar de gestionar las claves manualmente, y debe establecerse una política de rotación periódica de claves.

El **cifrado en tránsito** protege los datos mientras se mueven entre sistemas: entre un cliente y un servidor de base de datos, entre dos microservicios, o entre un agente de ingestión y un sistema de almacenamiento. TLS (Transport Layer Security) es el estándar universal para el cifrado en tránsito. La configuración correcta de TLS incluye el uso de versiones modernas del protocolo (TLS 1.2 como mínimo, TLS 1.3 preferiblemente), la validación de certificados y la selección de suites de cifrado seguras.

### 5.2 Control de acceso basado en roles (RBAC) y atributos (ABAC)

El control de acceso a datos es el conjunto de mecanismos que determinan qué entidades (usuarios, aplicaciones, servicios) pueden realizar qué operaciones (leer, escribir, eliminar, ejecutar) sobre qué recursos (tablas, archivos, APIs). Dos modelos complementarios dominan este espacio.

El **control de acceso basado en roles (RBAC)** asigna permisos no directamente a usuarios individuales, sino a roles, y luego asigna roles a usuarios. Esto simplifica enormemente la gestión de permisos en organizaciones con muchos usuarios, porque cuando cambian las responsabilidades de un usuario basta con cambiar su rol, sin necesidad de revisar sus permisos individuales. Un ejemplo típico en un proyecto de IA es la existencia de roles como `cientifico-datos` (acceso de lectura a todos los datasets del proyecto, acceso de escritura al área de experimentos), `ingeniero-datos` (acceso de escritura a los pipelines de ingestión y procesamiento), `auditor` (acceso de solo lectura a todos los sistemas, incluidos los logs de acceso) y `admin-datos` (acceso completo).

El **control de acceso basado en atributos (ABAC)** es un modelo más expresivo que evalúa las decisiones de acceso en función de atributos del sujeto (quién intenta acceder), del recurso (a qué se intenta acceder), de la acción (qué se intenta hacer) y del entorno (contexto de la solicitud, como la hora o la dirección IP). ABAC permite implementar políticas de control de acceso más granulares y dinámicas que RBAC. Por ejemplo: "un analista de datos puede leer registros de clientes de su propia región durante el horario laboral, pero no fuera de él, y nunca si el cliente ha ejercido el derecho de oposición".

En plataformas de datos modernas como Apache Ranger (para ecosistemas Hadoop/Spark), Unity Catalog (para Databricks) o Lake Formation (para AWS), los modelos RBAC y ABAC suelen coexistir y complementarse.

### 5.3 Auditoría de accesos a datos sensibles

La auditoría de accesos consiste en el registro sistemático de todas las acciones realizadas sobre los datos, de manera que pueda responderse a las preguntas: ¿quién accedió a qué datos, cuándo, desde dónde y para qué? En el contexto del RGPD, la capacidad de demostrar que el acceso a datos personales ha estado debidamente controlado y que los accesos han quedado registrados es un componente esencial del principio de responsabilidad proactiva (*accountability*).

Un sistema de auditoría eficaz debe registrar, como mínimo, los siguientes atributos de cada evento de acceso: identidad del actor (usuario o aplicación), tipo de operación (lectura, escritura, eliminación, exportación), recurso accedido (tabla, archivo, columnas específicas en el caso de consultas), timestamp con precisión de al menos segundos, dirección IP o identificador del nodo de origen, y resultado de la operación (éxito o fracaso, y en caso de fracaso, el motivo).

Los logs de auditoría deben almacenarse de forma separada de los datos que auditan, en un sistema con controles de acceso más restrictivos (los propios administradores no deben poder modificar o borrar los logs de sus propias acciones), y deben conservarse durante el periodo exigido por la normativa aplicable. En el ámbito del RGPD, no existe un plazo universal de conservación de logs, pero la práctica habitual es de uno a tres años, sujeto a los plazos de prescripción de las infracciones administrativas aplicables.

---

## Actividades prácticas propuestas

**Actividad 1. Configuración de un repositorio con DVC y almacenamiento remoto en S3.**
El alumnado creará un repositorio Git con DVC inicializado, añadirá un conjunto de datos sintético de clasificación, definirá un almacenamiento remoto en un bucket de S3 (o una emulación local con MinIO), realizará un push del dataset al remoto y verificará que un compañero puede reproducir el entorno ejecutando `git clone` + `dvc pull`. La actividad culmina con la modificación del dataset, la creación de una nueva versión y la verificación de que es posible hacer checkout a la versión anterior.

**Actividad 2. Definición de un pipeline DVC reproducible.**
Partiendo del repositorio de la actividad anterior, el alumnado definirá en `dvc.yaml` un pipeline de tres etapas: carga y limpieza de datos, extracción de características y entrenamiento de un clasificador simple. Ejecutará el pipeline con `dvc repro`, modificará un parámetro del modelo, volverá a ejecutar el pipeline y comprobará que DVC solo re-ejecuta las etapas afectadas por el cambio. Los resultados de las métricas de cada ejecución se compararán mediante `dvc metrics show`.

**Actividad 3. Catalogación de un dataset en OpenMetadata.**
El alumnado desplegará una instancia local de OpenMetadata (mediante Docker Compose), conectará una fuente de datos (una base de datos PostgreSQL con datos de ejemplo), ejecutará un proceso de ingestión de metadatos y enriquecerá manualmente la catalogación con metadatos de negocio: descripción de los campos, propietario del dato, clasificación de sensibilidad y etiquetas de glosario. Finalmente, trazará el linaje entre la tabla fuente y una tabla derivada creada mediante una consulta SQL documentada.

**Actividad 4. Análisis de conformidad RGPD de un pipeline de IA.**
Se proporciona al alumnado la descripción de un caso de uso ficticio: un sistema de puntuación de riesgo crediticio que utiliza datos históricos de clientes. El alumnado debe identificar: (a) los tipos de datos personales involucrados y su clasificación de sensibilidad; (b) la base legal más adecuada para el tratamiento; (c) las medidas de minimización de datos que se podrían aplicar; (d) si se requiere una EIPD y por qué; (e) cómo se implementaría el derecho al olvido en el contexto de este sistema. El resultado se presenta como un informe estructurado de análisis de riesgo de privacidad.

**Actividad 5. Aplicación de k-anonimato y análisis de riesgo residual.**
El alumnado trabajará con un dataset tabular que contiene atributos cuasi-identificadores (edad, municipio, sexo, nivel educativo) y un atributo sensible (diagnóstico médico). Mediante la biblioteca `pycanon` o código Python propio, el alumnado medirá el nivel actual de k-anonimato del dataset, aplicará generalización de atributos hasta alcanzar k=5, verificará si el dataset modificado cumple también con l-diversidad para l=2, y redactará un análisis crítico de las limitaciones de las técnicas aplicadas en términos de riesgo de re-identificación residual.

---

## Referencias y material externo

Kleppmann, M. (2017). *Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems*. O'Reilly Media. ISBN: 978-1449373320.

Reis, J., y Housley, M. (2022). *Fundamentals of Data Engineering: Plan and Build Robust Data Systems*. O'Reilly Media. ISBN: 978-1098108304.

DAMA International (2017). *DAMA-DMBOK: Data Management Body of Knowledge* (2.ª ed.). Technics Publications. ISBN: 978-1634622349.

Dwork, C., McSherry, F., Nissim, K., y Smith, A. (2006). Calibrating Noise to Sensitivity in Private Data Analysis. En S. Halevi y T. Rabin (Eds.), *Theory of Cryptography. TCC 2006. Lecture Notes in Computer Science*, vol. 3876, pp. 265-284. Springer. https://doi.org/10.1007/11681878_14

Machanavajjhala, A., Kifer, D., Gehrke, J., y Venkitasubramaniam, M. (2007). L-diversity: Privacy beyond k-anonymity. *ACM Transactions on Knowledge Discovery from Data*, 1(1), artículo 3. https://doi.org/10.1145/1217299.1217302

Narayanan, A., y Shmatikoff, V. (2008). Robust De-anonymization of Large Sparse Datasets. En *Proceedings of the 2008 IEEE Symposium on Security and Privacy*, pp. 111-125. https://doi.org/10.1109/SP.2008.33

Iterative AI. (2024). *DVC: Data Version Control — documentación oficial*. https://dvc.org/doc

MLflow. (2024). *MLflow Documentation — MLflow Data*. https://mlflow.org/docs/latest/python_api/mlflow.data.html

Linux Foundation. (2024). *Delta Lake Documentation*. https://docs.delta.io/latest/index.html

DataHub Project. (2024). *DataHub: The Open Source Metadata Platform*. https://datahubproject.io/docs/

Unión Europea (2016). Reglamento (UE) 2016/679 del Parlamento Europeo y del Consejo, de 27 de abril de 2016, relativo a la protección de las personas físicas en lo que respecta al tratamiento de datos personales y a la libre circulación de estos datos. *Diario Oficial de la Unión Europea*, L 119, pp. 1-88. https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX%3A32016R0679

Unión Europea (2024). Reglamento (UE) 2024/1689 del Parlamento Europeo y del Consejo, de 13 de junio de 2024, por el que se establecen normas armonizadas en materia de inteligencia artificial. *Diario Oficial de la Unión Europea*, L 2024/1689. https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=OJ:L_202401689

Agencia Española de Protección de Datos (2022). *Adecuación al RGPD de tratamientos que incorporan Inteligencia Artificial: Una introducción*. AEPD. https://www.aepd.es/guias/adecuacion-rgpd-ia.pdf

Google (2023). *Differential Privacy Library*. GitHub. https://github.com/google/differential-privacy

OpenDP (2024). *OpenDP: A Differential Privacy Library*. https://docs.opendp.org/
