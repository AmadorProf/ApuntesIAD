# UD5 · Versionado y ficha técnica del modelo

**Módulo:** MP02 · Entrenamiento de Modelos  
**Ciclo:** CFS1 · Gestión de datos y entrenamiento IA  
**Duración estimada:** 12 horas lectivas

---

## 1. Introducción: reproducibilidad en ML como requisito profesional y regulatorio

La reproducibilidad es la propiedad de un experimento que permite a un tercero obtener resultados equivalentes siguiendo los mismos procedimientos, sobre los mismos datos y bajo las mismas condiciones. En ciencias experimentales clásicas, la reproducibilidad es el fundamento de la validación entre pares. En aprendizaje automático, esta propiedad se ha convertido además en un requisito profesional y, de forma creciente, en una obligación regulatoria.

La relevancia de la reproducibilidad en ML se explica por la naturaleza estadística de los modelos. Un modelo no es una fórmula determinista: es el resultado de aplicar un algoritmo de optimización sobre datos, con múltiples fuentes de aleatoriedad que deben controlarse explícitamente. Las semillas de los generadores de números pseudoaleatorios, el orden en que se procesan los lotes de datos, las versiones exactas de las librerías, la configuración del hardware y los hiperparámetros elegidos forman un conjunto de variables implícitas que, si no se documentan, hacen que un experimento sea irrecuperable.

La **crisis de reproducibilidad en IA** fue caracterizada sistemáticamente por Joëlle Pineau y colaboradores en su trabajo de 2020, publicado en el Journal of Machine Learning Research como informe del programa de reproducibilidad de NeurIPS 2019. Pineau et al. analizaron cientos de artículos aceptados en conferencias de primer nivel y concluyeron que la mayoría no proporcionaba información suficiente para que un investigador independiente pudiese replicar los resultados. Las causas identificadas eran estructurales: ausencia de código público, omisión de hiperparámetros relevantes, conjuntos de evaluación no disponibles, y una selección implícita de semillas que maximizaba los resultados reportados sin revelar la variabilidad subyacente. Como respuesta, Pineau et al. propusieron una lista de verificación de reproducibilidad que fue adoptada como requisito de sumisión por NeurIPS y otras conferencias, marcando un hito en las prácticas de la comunidad científica de ML.

La dimensión regulatoria añade urgencia a estas preocupaciones. El **Reglamento de Inteligencia Artificial de la Unión Europea** (EU AI Act, Reglamento 2024/1689) clasifica como sistemas de alto riesgo aquellos usados en selección de personal, acceso al crédito, diagnóstico médico, administración de justicia e infraestructuras críticas. Para estos sistemas, el Artículo 12 del AI Act exige el mantenimiento de registros automáticos de las operaciones del sistema con suficiente granularidad para permitir una auditoría retrospectiva. El Artículo 13 impone obligaciones de transparencia, incluyendo la entrega de documentación técnica detallada al comprador u operador del sistema. El Artículo 17 exige un sistema de gestión de la calidad que incluya el versionado de los datos y modelos. En este marco legal, no poder reproducir un modelo que tomó una decisión con consecuencias para una persona no es únicamente una mala práctica científica: puede constituir un incumplimiento normativo con consecuencias jurídicas y económicas.

En respuesta a estos desafíos, la industria ha desarrollado un conjunto de herramientas y prácticas estandarizadas que esta unidad didáctica cubre en profundidad: MLflow para el seguimiento y registro de experimentos, DVC para el versionado de datos y pipelines, los Model Registries para gestionar el ciclo de vida de los modelos en producción, las Model Cards para documentar los modelos de forma estructurada, y los Datasheets for Datasets para documentar los datos de entrenamiento.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad didáctica, el estudiante será capaz de:

- Explicar el papel de la reproducibilidad en el ciclo de vida de un modelo de ML y las consecuencias profesionales y regulatorias de su ausencia, con referencia al trabajo de Pineau et al. (2020) y al EU AI Act.
- Instalar y configurar MLflow, registrar parámetros, métricas y artefactos en un experimento, comparar runs en la UI y registrar modelos en el Model Registry.
- Diseñar y ejecutar pipelines reproducibles con DVC mediante `dvc.yaml`, `params.yaml` y `dvc repro`.
- Describir el ciclo de vida de un modelo en un Model Registry, incluyendo las fases Staging, Production y Archived, y los mecanismos de transición y alias.
- Redactar una Model Card completa conforme a la estructura de Mitchell et al. (2019), incluyendo métricas desagregadas por subgrupos y consideraciones éticas.
- Redactar un Datasheet for Dataset conforme a la estructura de Gebru et al. (2021) y relacionarlo con las obligaciones del EU AI Act.
- Aplicar técnicas de control de semillas aleatorias en Python, NumPy y PyTorch, y empaquetar entornos reproducibles con Docker.

---

## 3. MLflow: gestión del ciclo de vida de modelos

### 3.1 Arquitectura de MLflow

MLflow es una plataforma de código abierto, inicialmente desarrollada por Databricks, que organiza el ciclo de vida completo del ML en cuatro componentes principales que pueden desplegarse de forma independiente o conjunta.

El **Tracking Server** es el servidor que recibe y persiste todos los metadatos de los experimentos: parámetros de entrada (hiperparámetros y configuración), métricas de salida (loss, accuracy, AUC…), etiquetas arbitrarias y referencias a artefactos binarios. En un despliegue local, el backend de metadatos puede ser el sistema de ficheros o una base de datos SQLite. En producción, se usa típicamente PostgreSQL o MySQL como backend relacional y un almacén de objetos (S3, GCS, Azure Blob Storage) para los artefactos.

El **Artifact Store** es el repositorio donde se persisten los ficheros producidos durante el entrenamiento: el modelo serializado, gráficos de curvas de aprendizaje, matrices de confusión, configuraciones, conjuntos de datos de evaluación y cualquier otro artefacto binario. La separación del Artifact Store y el Tracking Server permite escalar ambos componentes de forma independiente según las necesidades de almacenamiento y consulta.

El **Model Registry** es el catálogo centralizado de versiones de modelo. A diferencia del Tracking Server, que almacena ejecuciones individuales (runs) de experimentos, el Model Registry contiene versiones nombradas y versionadas de modelos, junto con su estado en el ciclo de vida (Staging, Production, Archived), comentarios de aprobación y alias.

**MLflow Projects** es el componente que permite empaquetar código de ML en un formato reutilizable, especificando el entorno de ejecución (conda o Docker) y los parámetros de entrada. Permite reproducir cualquier experimento con un único comando `mlflow run`.

### 3.2 Instalación y configuración

```bash
pip install mlflow scikit-learn pandas numpy matplotlib
```

Para levantar el servidor de tracking localmente con SQLite como backend:

```bash
mlflow server \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root ./mlruns \
    --host 0.0.0.0 \
    --port 5000
```

En equipos con infraestructura compartida, la configuración típica usa PostgreSQL y S3:

```bash
mlflow server \
    --backend-store-uri postgresql://usuario:clave@host:5432/mlflow \
    --default-artifact-root s3://mi-bucket/mlruns \
    --host 0.0.0.0 \
    --port 5000
```

El cliente Python apunta al servidor mediante la variable de entorno o mediante llamada explícita:

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
```

```python
import mlflow
mlflow.set_tracking_uri("http://localhost:5000")
```

### 3.3 Logging de parámetros, métricas y artefactos

El ciclo básico de uso de MLflow Tracking consiste en abrir un run con `mlflow.start_run()`, registrar parámetros, métricas y artefactos durante el entrenamiento, y cerrar el run. El context manager gestiona la apertura y cierre de forma automática, incluso si el código lanza una excepción:

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("clasificacion-cancer-mama")

data = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target,
    test_size=0.2, random_state=42, stratify=data.target
)

params = {
    "n_estimators": 150,
    "max_depth": 6,
    "min_samples_split": 4,
    "random_state": 42
}

with mlflow.start_run(run_name="rf-v1"):
    # Registrar parámetros
    mlflow.log_params(params)

    # Entrenamiento
    clf = RandomForestClassifier(**params)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    # Registrar métricas
    mlflow.log_metric("accuracy", accuracy_score(y_test, y_pred))
    mlflow.log_metric("f1", f1_score(y_test, y_pred))
    mlflow.log_metric("roc_auc", roc_auc_score(y_test, y_prob))

    # Registrar artefacto: importancia de features
    importancias = pd.Series(
        clf.feature_importances_, index=data.feature_names
    ).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    importancias.head(10).plot(kind="barh", ax=ax)
    ax.set_title("Top 10 Features")
    plt.tight_layout()
    fig.savefig("feature_importance.png")
    mlflow.log_artifact("feature_importance.png")
    plt.close()

    # Etiquetas del run
    mlflow.set_tag("tipo_modelo", "ensemble")
    mlflow.set_tag("dataset", "breast_cancer_v1")

    # Registrar el modelo en el Model Registry
    mlflow.sklearn.log_model(
        sk_model=clf,
        artifact_path="modelo",
        registered_model_name="clasificador-cancer-mama"
    )
```

La llamada `mlflow.sklearn.log_model()` con `registered_model_name` tiene efecto dual: serializa el modelo como artefacto en el Artifact Store y crea o incrementa una versión en el Model Registry bajo el nombre especificado.

### 3.4 Comparación de runs en la UI

La interfaz web de MLflow (accesible en `http://localhost:5000` tras lanzar el servidor) permite seleccionar múltiples runs del mismo experimento y compararlos en una vista paralela que muestra parámetros y métricas en columnas. La función "Chart View" genera gráficas que permiten visualizar, por ejemplo, cómo varía la AUC-ROC en función del número de estimadores en un barrido de hiperparámetros.

### 3.5 Ejemplo end-to-end con autolog

MLflow ofrece la función `mlflow.autolog()` que, cuando está activada antes del entrenamiento, captura automáticamente los parámetros, métricas y el modelo para los frameworks soportados (scikit-learn, XGBoost, PyTorch, TensorFlow, entre otros), eliminando la necesidad de llamadas manuales de logging:

```python
import mlflow
import mlflow.sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

mlflow.set_experiment("autolog-demo")
mlflow.sklearn.autolog()  # captura automáticamente todo

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

with mlflow.start_run():
    clf = LogisticRegression(C=0.5, max_iter=200)
    clf.fit(X_train, y_train)
    # autolog ha registrado parámetros, métricas y modelo sin ninguna llamada explícita
```

---

## 4. DVC para versionado de experimentos y pipelines reproducibles

### 4.1 Concepto y motivación

Git es la herramienta estándar para versionar código, pero tiene limitaciones fundamentales para el ML: no está diseñado para gestionar ficheros grandes como datasets (que pueden pesar gigabytes o terabytes) ni modelos entrenados (que pueden superar los cientos de megabytes). Almacenar estos ficheros directamente en Git degrada el rendimiento del repositorio, encarece el almacenamiento y dificulta la colaboración.

DVC (Data Version Control) resuelve este problema con una arquitectura en dos capas: en Git se almacenan únicamente ficheros de metadatos ligeros (`.dvc` y `dvc.lock`) que actúan como punteros; los ficheros binarios reales se almacenan en un repositorio remoto de objetos (S3, GCS, Azure Blob, SSH u otros). Cuando se hace `git checkout` a una versión pasada, `dvc checkout` recupera los datos y modelos que corresponden exactamente a ese commit, garantizando la reproducibilidad de extremo a extremo.

Adicionalmente, DVC introduce el concepto de **pipeline declarativo**: el flujo de transformación desde los datos crudos hasta el modelo entrenado se describe en un fichero `dvc.yaml`, y DVC calcula automáticamente qué etapas deben re-ejecutarse en función de si sus dependencias han cambiado.

### 4.2 Instalación e inicialización

```bash
pip install dvc dvc-s3        # o dvc-gs, dvc-azure según el remote
git init mi-proyecto-ml
cd mi-proyecto-ml
dvc init
git add .dvc .dvcignore
git commit -m "Inicializar DVC"
```

Configuración del almacén remoto:

```bash
dvc remote add -d almacen s3://mi-bucket/dvc-store
dvc remote modify almacen region eu-west-1
```

### 4.3 El fichero `dvc.yaml`: stages, deps y outs

El fichero `dvc.yaml` define el pipeline como un grafo dirigido acíclico (DAG) de etapas. Cada etapa especifica el comando a ejecutar (`cmd`), sus dependencias (`deps`) y sus salidas (`outs`). DVC calcula el hash SHA-256 de cada dependencia y lo almacena en `dvc.lock`; en ejecuciones posteriores, solo re-ejecuta las etapas cuyas dependencias han cambiado.

```yaml
# dvc.yaml
stages:
  preparar_datos:
    cmd: python src/preparar_datos.py
    deps:
      - src/preparar_datos.py
      - data/raw/datos_brutos.csv
    outs:
      - data/processed/train.csv
      - data/processed/test.csv

  entrenar_modelo:
    cmd: python src/entrenar.py
    deps:
      - src/entrenar.py
      - data/processed/train.csv
      - params.yaml
    outs:
      - models/modelo.pkl
    metrics:
      - metrics/resultados.json:
          cache: false

  evaluar_modelo:
    cmd: python src/evaluar.py
    deps:
      - src/evaluar.py
      - data/processed/test.csv
      - models/modelo.pkl
    metrics:
      - metrics/evaluacion.json:
          cache: false
    plots:
      - metrics/curva_roc.csv:
          cache: false
```

### 4.4 `params.yaml` para externalizar hiperparámetros

DVC permite externalizar los hiperparámetros a un fichero `params.yaml`. Los scripts de entrenamiento leen este fichero en lugar de recibir los hiperparámetros como argumentos de línea de comandos. Esto permite a DVC rastrear automáticamente los cambios en los hiperparámetros como parte del grafo de dependencias, de modo que modificar un hiperparámetro hace que las etapas que dependen de `params.yaml` se marquen como desactualizadas:

```yaml
# params.yaml
modelo:
  n_estimators: 100
  max_depth: 5
  min_samples_split: 4
  random_state: 42

datos:
  test_size: 0.2
  random_state: 42
```

El script de entrenamiento accede a estos valores así:

```python
# src/entrenar.py
import yaml
import pickle
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

with open("params.yaml") as f:
    cfg = yaml.safe_load(f)

params_modelo = cfg["modelo"]
params_datos = cfg["datos"]

np.random.seed(params_modelo["random_state"])

train = pd.read_csv("data/processed/train.csv")
X_train = train.drop("target", axis=1).values
y_train = train["target"].values

clf = RandomForestClassifier(
    n_estimators=params_modelo["n_estimators"],
    max_depth=params_modelo["max_depth"],
    min_samples_split=params_modelo["min_samples_split"],
    random_state=params_modelo["random_state"]
)
clf.fit(X_train, y_train)

with open("models/modelo.pkl", "wb") as f:
    pickle.dump(clf, f)

acc = accuracy_score(y_train, clf.predict(X_train))
with open("metrics/resultados.json", "w") as f:
    json.dump({"accuracy_train": acc}, f, indent=2)
```

### 4.5 Reproducción y comparación de experimentos

Para ejecutar el pipeline completo o solo las etapas desactualizadas:

```bash
dvc repro          # ejecuta solo las etapas con dependencias modificadas
dvc repro -f       # fuerza la ejecución de todas las etapas
```

Para comparar métricas y parámetros entre versiones del proyecto:

```bash
dvc metrics show              # métricas del estado actual
dvc metrics diff HEAD~1       # diferencia con el commit anterior
dvc params diff HEAD~1        # diferencia de hiperparámetros con el commit anterior
```

El flujo de trabajo con Git+DVC para un experimento reproducible es el siguiente: tras ejecutar `dvc repro`, se hace `git add dvc.lock metrics/` y se crea un commit de Git. El fichero `dvc.lock` registra los hashes exactos de todos los datos, modelos y artefactos intermedios correspondientes a esa ejecución. Para reproducir exactamente ese experimento en el futuro o en otra máquina, basta con `git checkout <hash-commit>`, `dvc checkout` (descarga los artefactos binarios correspondientes desde el remote) y `dvc repro` (verifica que el pipeline produce los mismos resultados).

---

## 5. Model Registry y ciclo de vida del modelo

### 5.1 Fases del ciclo de vida

Un Model Registry organiza las versiones de los modelos en un ciclo de vida con fases bien definidas que reflejan el proceso de validación y despliegue. En MLflow, las tres fases estándar son:

**Staging** (pre-producción): el modelo ha superado la evaluación técnica inicial —métricas por encima de los umbrales definidos— y está pendiente de validación adicional: pruebas de integración con los sistemas destino, pruebas de carga, validación de negocio y aprobaciones formales. En entornos regulados, esta fase puede incluir revisión por un comité de riesgos o un auditor externo.

**Production** (producción): el modelo está sirviendo predicciones en el sistema productivo. La práctica recomendada es mantener una sola versión en producción a la vez (el "champion") para evitar inconsistencias. El paso a producción debe estar acompañado del archivado automático de la versión anterior.

**Archived** (archivado): el modelo ha sido reemplazado y ya no sirve tráfico activo, pero se conserva íntegro por razones de auditoría, cumplimiento normativo (el EU AI Act exige conservar la documentación técnica durante al menos diez años para sistemas de alto riesgo) y para posibles rollbacks de emergencia.

### 5.2 Transiciones y aprobaciones programáticas

```python
from mlflow.tracking import MlflowClient

client = MlflowClient(tracking_uri="http://localhost:5000")

# Transición a Staging tras superar evaluación técnica
client.transition_model_version_stage(
    name="clasificador-cancer-mama",
    version=3,
    stage="Staging",
    archive_existing_versions=False
)

# Añadir descripción con el resultado de la validación
client.update_model_version(
    name="clasificador-cancer-mama",
    version=3,
    description=(
        "Entrenado con dataset v2.1. AUC=0.923. "
        "Validado por equipo clínico el 2026-06-20. "
        "Aprobado para producción."
    )
)

# Transición a Production tras aprobación formal
client.transition_model_version_stage(
    name="clasificador-cancer-mama",
    version=3,
    stage="Production",
    archive_existing_versions=True  # archiva automáticamente la versión anterior
)
```

### 5.3 Aliases y versionado semántico

MLflow 2.x introdujo los aliases, que permiten referenciar versiones de modelo con nombres estables independientes del número de versión. Esto simplifica el código de inferencia, que puede hacer referencia siempre al alias "champion" sin necesidad de actualizar configuración cada vez que se promueve una nueva versión:

```python
client.set_registered_model_alias(
    name="clasificador-cancer-mama",
    alias="champion",
    version=3
)

# En el servicio de inferencia, siempre se carga el alias
modelo = mlflow.sklearn.load_model("models:/clasificador-cancer-mama@champion")
```

### 5.4 Integración en CI/CD para promoción automática

En pipelines de CI/CD maduros, la promoción de modelos se automatiza mediante checks programáticos que evitan que versiones deficientes lleguen a producción:

```python
def promover_si_supera_umbral(
    nombre_modelo: str,
    version: int,
    umbral_auc: float = 0.90
) -> bool:
    client = MlflowClient()
    run_id = client.get_model_version(nombre_modelo, version).run_id
    metricas = client.get_run(run_id).data.metrics

    auc = metricas.get("roc_auc", 0.0)
    if auc >= umbral_auc:
        client.transition_model_version_stage(
            name=nombre_modelo,
            version=version,
            stage="Staging"
        )
        print(f"[OK] Modelo v{version} promovido a Staging (AUC={auc:.4f})")
        return True
    else:
        print(f"[FAIL] Modelo v{version} rechazado. AUC={auc:.4f} < {umbral_auc}")
        return False
```

---

## 6. Fichas técnicas de modelos (Model Cards)

### 6.1 Origen: Mitchell et al. (2019)

El concepto de Model Card fue propuesto por Margaret Mitchell, Timnit Gebru y colaboradores de Google en su artículo "Model Cards for Model Reporting", presentado en la conferencia FAccT (Fairness, Accountability, and Transparency) de 2019. La motivación era directa: los medicamentos incluyen prospectos que describen su composición, indicaciones, contraindicaciones y efectos secundarios; los modelos de ML deberían incluir documentos equivalentes.

Mitchell et al. observaron que los modelos se desplegaban con frecuencia en contextos para los que no habían sido diseñados, con poblaciones que no estaban representadas en los datos de entrenamiento, y que obtenían resultados significativamente peores para subgrupos minoritarios sin que los usuarios del modelo —ni las personas afectadas— lo supieran. La Model Card es el mecanismo de comunicación que cierra esa brecha de información.

### 6.2 Estructura completa

Una Model Card completa abarca las siguientes secciones:

**Detalles del modelo:** nombre, versión, tipo de arquitectura, framework y versión, fecha de entrenamiento, organización responsable, enlace al repositorio, licencia de uso.

**Uso previsto:** tareas para las que el modelo fue diseñado; usuarios objetivo (quiénes deberían usarlo); casos de uso explícitamente excluidos (fuera del alcance).

**Factores relevantes:** variables que afectan al rendimiento del modelo, incluyendo características demográficas de las personas sobre las que el modelo hace inferencias, condiciones de adquisición de datos, y dominio de aplicación.

**Métricas:** cuáles se usan para evaluar el modelo y por qué se eligieron esas en lugar de otras; umbrales de decisión empleados.

**Datos de evaluación:** descripción de los conjuntos de datos usados para evaluar, incluyendo su preprocesamiento y la motivación de su elección.

**Datos de entrenamiento:** descripción de los datos usados para entrenar (puede ser menos detallada que la evaluación por razones de confidencialidad o protección de datos).

**Análisis cuantitativo:** resultados desagregados por subgrupos relevantes (género, edad, región geográfica, tipo de usuario, etc.). Este es el apartado más diferenciador de una Model Card respecto a la documentación técnica convencional.

**Consideraciones éticas:** posibles usos indebidos, riesgos identificados, medidas de mitigación implementadas.

**Advertencias y recomendaciones:** limitaciones conocidas del modelo; condiciones bajo las cuales no debe usarse; plan de monitorización y re-entrenamiento.

### 6.3 Ejemplo de Model Card completa en Markdown

```markdown
# Model Card: Clasificador de Riesgo Crediticio v2.3

## Detalles del modelo

- **Nombre:** credit-risk-classifier
- **Versión:** 2.3.0
- **Tipo:** Clasificación binaria (riesgo alto / riesgo bajo)
- **Arquitectura:** Gradient Boosting (XGBoost 1.7.6)
- **Framework:** XGBoost + scikit-learn 1.3
- **Fecha de entrenamiento:** 2026-03-15
- **Responsable:** Equipo de Modelos de Riesgo, Banco Ejemplo S.A.
- **Repositorio:** https://git.bancoejemplo.com/modelos/credit-risk
- **Licencia:** Propietaria — uso interno exclusivo

## Uso previsto

**Usuarios previstos:** Oficiales de crédito y sistemas automáticos de decisión del
Banco Ejemplo para el mercado español.

**Casos de uso previstos:** Apoyo a la decisión de concesión de préstamos personales
entre 1.000 € y 50.000 € a personas físicas residentes en España.

**Fuera del alcance:**
- Préstamos hipotecarios (distribución de riesgo diferente)
- Personas jurídicas (empresas)
- Mercados fuera de España sin re-entrenamiento y re-validación
- Uso como único factor de decisión sin supervisión humana

## Factores relevantes

El rendimiento del modelo puede variar en función de la edad del solicitante,
el tipo de empleo (autónomo vs. asalariado), la antigüedad de la relación bancaria
y la región geográfica. Se recomienda monitorizar el rendimiento por subgrupo.

## Métricas de evaluación

| Métrica        | Valor global | Umbral mínimo |
|----------------|-------------|---------------|
| AUC-ROC        | 0.847       | 0.820         |
| F1-Score       | 0.792       | 0.760         |
| KS Statistic   | 0.523       | 0.500         |
| FNR            | 0.181       | < 0.25        |

## Análisis cuantitativo por subgrupos

| Subgrupo         | AUC-ROC | F1    | FNR   |
|------------------|---------|-------|-------|
| Global           | 0.847   | 0.792 | 0.181 |
| Hombres          | 0.852   | 0.798 | 0.174 |
| Mujeres          | 0.841   | 0.784 | 0.189 |
| Edad < 30        | 0.798   | 0.741 | 0.231 |
| Edad 30-60       | 0.863   | 0.812 | 0.162 |
| Edad > 60        | 0.812   | 0.763 | 0.198 |
| Autónomos        | 0.808   | 0.751 | 0.267 |
| Asalariados      | 0.861   | 0.811 | 0.154 |

**Observación importante:** El rendimiento es significativamente inferior para
solicitantes menores de 30 años y para autónomos. Se recomienda revisión manual
obligatoria para estos subgrupos cuando el score esté entre 0.40 y 0.60.

## Consideraciones éticas

Este modelo está clasificado como sistema de IA de alto riesgo bajo el Anexo III
del EU AI Act (Art. 10 y 13). Las siguientes medidas de mitigación están activas:

- La variable "código postal" fue excluida explícitamente para evitar discriminación
  indirecta por origen geográfico.
- El modelo no utiliza variables de género, etnia, religión ni proxies conocidos
  de estas variables.
- Cada decisión genera una explicación SHAP individual disponible para el analista.
- Los clientes disponen de derecho de reclamación y revisión manual.
- Auditoría de equidad semestral realizada por equipo externo independiente.

## Advertencias y recomendaciones

- Monitorizar el PSI (Population Stability Index) mensualmente; re-entrenar si PSI > 0.25.
- No usar tras cambios macroeconómicos bruscos sin re-validación.
- El modelo se degrada para solicitantes sin historial crediticio previo (thin file).
- Documentación técnica completa disponible en el repositorio interno (Art. 11 AI Act).
```

### 6.4 Hugging Face Model Cards

Hugging Face ha popularizado las Model Cards para los modelos publicados en su Hub. Cada modelo del Hub incluye un fichero `README.md` con un bloque YAML de metadatos estructurados al inicio, seguido de la Model Card en texto libre. Los metadatos YAML permiten búsqueda y filtrado en la plataforma:

```yaml
---
language: es
license: apache-2.0
tags:
  - text-classification
  - sentiment-analysis
datasets:
  - amazon_reviews_multi
metrics:
  - accuracy
  - f1
model-index:
  - name: clasificador-sentimiento-es
    results:
      - task:
          type: text-classification
        dataset:
          name: Amazon Reviews ES
          type: amazon_reviews_multi
        metrics:
          - type: accuracy
            value: 0.923
          - type: f1
            value: 0.911
---
```

---

## 7. Datasheets for Datasets

### 7.1 Estructura y propósito: Gebru et al. (2021)

En paralelo a las Model Cards para modelos, Timnit Gebru y colaboradores publicaron en 2021 en Communications of the ACM las "Datasheets for Datasets". La analogía propuesta es con las fichas de seguridad de materiales (SDS): del mismo modo que cualquier sustancia química debe incluir un documento que describe su composición, riesgos y medidas de precaución, un dataset debería incluir un documento estandarizado que permita a cualquier usuario tomar decisiones informadas sobre su idoneidad para una tarea concreta.

La motivación empírica era clara: muchos de los sesgos, errores y daños causados por sistemas de IA tienen su raíz en datasets mal documentados, reutilizados en contextos para los que no fueron diseñados, o con problemas de representación que nadie había registrado formalmente. Un dataset recopilado en un contexto específico —una determinada región, período histórico o población— puede producir modelos sesgados cuando se usa fuera de ese contexto, y sin un datasheet, los usuarios del dataset pueden no ser conscientes de esas limitaciones.

Las secciones principales de un Datasheet for Dataset son:

**Motivación:** Para qué se creó el dataset; quién lo creó y con qué financiación; si la creación fue encargada por alguna entidad y cuál.

**Composición:** Qué representa cada instancia; cuántas instancias contiene; si existe una división en train/validation/test; si hay etiquetas o anotaciones y cómo se obtuvieron; si el dataset contiene información confidencial o sensible (datos de salud, información financiera, imágenes de personas, etc.).

**Proceso de recopilación:** Cómo se recopilaron los datos (sensores, web scraping, encuestas, registros administrativos); durante qué período; si se obtuvo consentimiento informado de las personas cuyos datos se recogen; si existen mecanismos de retiro del consentimiento.

**Preprocesamiento, limpieza y etiquetado:** Qué preprocesamiento se realizó; si los datos crudos están disponibles; quiénes fueron los etiquetadores, cómo se les seleccionó y cómo se les compensó; qué instrucciones recibieron.

**Usos:** Para qué tareas se ha usado o podría usarse el dataset; usos para los que no se recomienda; impacto social potencial del uso inadecuado.

**Distribución:** Cómo y cuándo se distribuirá; bajo qué licencia; si existen restricciones de terceros sobre el uso.

**Mantenimiento:** Quién mantiene el dataset; cómo se pueden reportar errores; si se prevén actualizaciones; cómo se notificarán.

### 7.2 Relación con la Model Card y obligatoriedad bajo el EU AI Act

El Datasheet for Dataset y la Model Card son documentos complementarios que forman juntos la trazabilidad documental completa de un sistema de IA. La Model Card referencia los datasheets de los datasets usados para entrenamiento y evaluación; el datasheet no describe el modelo sino los datos con los que fue construido.

El EU AI Act, en su Artículo 10, exige que los datos de entrenamiento, validación y prueba de sistemas de alto riesgo cumplan criterios de calidad, sean pertinentes, suficientemente representativos y, en la medida de lo posible, libres de errores y completos. El Artículo 11 exige documentación técnica que incluya "una descripción general del sistema de IA, incluyendo su finalidad prevista, el nivel de exactitud, solidez y ciberseguridad [...] así como una descripción de los datos de entrenamiento utilizados". Los Datasheets for Datasets son el mecanismo natural y estructurado para satisfacer estas obligaciones de documentación, y su adopción está siendo recomendada por organismos de normalización como NIST y ISO.

---

## 8. Reproducibilidad: semillas, entornos y artefactos

### 8.1 Control de semillas aleatorias

La aleatoriedad no controlada es una de las fuentes más frecuentes e insidiosas de irreproducibilidad en ML. Las principales fuentes de aleatoriedad que deben controlarse son: la inicialización de los pesos del modelo, el orden de los mini-batches durante el entrenamiento, la partición de datos en train/test, los procesos de augmentación de datos, y los algoritmos de dropout y similares. Cada librería mantiene su propio estado interno del generador de números pseudoaleatorios y debe ser inicializada de forma independiente:

```python
import random
import os
import numpy as np
import torch

def fijar_semillas(semilla: int = 42) -> None:
    """
    Fija todas las fuentes de aleatoriedad conocidas.
    Debe invocarse al inicio del script, antes de cualquier operación aleatoria.
    """
    # Python estándar
    random.seed(semilla)

    # Variable de entorno para el hash de Python (afecta a sets y dicts)
    os.environ["PYTHONHASHSEED"] = str(semilla)

    # NumPy
    np.random.seed(semilla)

    # PyTorch — CPU y GPU
    torch.manual_seed(semilla)
    torch.cuda.manual_seed(semilla)
    torch.cuda.manual_seed_all(semilla)  # necesario en entornos multi-GPU

    # Forzar operaciones deterministas en cuDNN
    # ADVERTENCIA: puede reducir el rendimiento en GPU
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# Invocar siempre como primera línea del script de entrenamiento
fijar_semillas(42)
```

Para TensorFlow/Keras:

```python
import tensorflow as tf
tf.random.set_seed(42)
```

Es importante documentar en el registro de experimentos (MLflow) la semilla usada:

```python
mlflow.log_param("semilla_aleatoria", 42)
```

**Nota sobre reproducibilidad en GPU:** Incluso con semillas fijadas, algunas operaciones CUDA (como `atomicAdd` en operaciones de reducción) no son deterministas por diseño del hardware. En esos casos, `torch.use_deterministic_algorithms(True)` lanza una excepción cuando se llama a una operación no determinista, lo que permite identificar y sustituir las operaciones problemáticas.

### 8.2 Docker para reproducibilidad de entorno

El control de semillas garantiza reproducibilidad del algoritmo, pero si las versiones de las librerías cambian, los resultados pueden variar. La solución robusta es empaquetar el entorno completo en una imagen Docker:

```dockerfile
FROM python:3.11.4-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements con versiones exactas (generado con pip freeze)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY params.yaml .

# Fijar semilla a nivel de entorno
ENV PYTHONHASHSEED=42
ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["python", "src/entrenar.py"]
```

El fichero `requirements.txt` debe especificar versiones exactas, generado con `pip freeze` en el entorno de desarrollo:

```
scikit-learn==1.3.2
xgboost==1.7.6
mlflow==2.9.2
pandas==2.1.4
numpy==1.26.2
torch==2.1.2
dvc==3.38.1
```

La imagen Docker puede registrarse como artefacto en MLflow, junto con su digest (hash único de la imagen), para garantizar que en el futuro se pueda identificar exactamente qué entorno se usó:

```python
mlflow.log_artifact("Dockerfile")
mlflow.log_artifact("requirements.txt")
mlflow.log_param("docker_image_digest", "sha256:abc123...")
```

### 8.3 Registro completo de artefactos

Para que un experimento sea plenamente reproducible, no basta con guardar el modelo final. Es necesario registrar todos los artefactos que permiten reconstruir el experimento desde cero, incluyendo el código, los parámetros, el entorno y una referencia verificable a los datos:

```python
import platform
import sys
import hashlib

def hash_fichero(ruta: str) -> str:
    """Calcula el SHA-256 de un fichero para verificar su integridad."""
    sha256 = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            sha256.update(bloque)
    return sha256.hexdigest()

with mlflow.start_run():
    # Código fuente
    mlflow.log_artifact("src/entrenar.py")
    mlflow.log_artifact("params.yaml")
    mlflow.log_artifact("requirements.txt")
    mlflow.log_artifact("Dockerfile")

    # Referencia verificable a los datos
    mlflow.log_param("hash_datos_entrenamiento", hash_fichero("data/processed/train.csv"))
    mlflow.log_param("version_dataset", "v2.1")

    # Metadatos del entorno
    mlflow.log_param("python_version", sys.version)
    mlflow.log_param("plataforma", platform.platform())
    mlflow.log_param("semilla", 42)

    # El modelo
    mlflow.sklearn.log_model(clf, "modelo")
```

---

## 9. Actividades prácticas

### Actividad 1: Pipeline MLflow con barrido de hiperparámetros

**Objetivo:** Dominar el ciclo completo de tracking de experimentos en MLflow, desde el registro de parámetros hasta la comparación de runs y el registro en el Model Registry.

**Descripción:** Usando el dataset `breast_cancer` de scikit-learn, implementa un script que ejecute al menos 5 configuraciones distintas de un `RandomForestClassifier` variando `n_estimators` (50, 100, 200) y `max_depth` (None, 5, 10). Para cada run, registra en MLflow: los hiperparámetros, las métricas `accuracy`, `f1_weighted` y `roc_auc`, y un artefacto visual (curva ROC o matriz de confusión). Tras ejecutar todos los runs, usa la UI de MLflow para identificar el mejor modelo según AUC-ROC. Registra ese modelo en el Model Registry con el nombre `clasificador-cancer-act1` y transiciónalo al estado Staging añadiendo una descripción que justifique la selección.

**Entregables:** Script Python funcional y comentado; captura de pantalla de la vista de comparación de runs en la UI de MLflow mostrando los 5 runs.

### Actividad 2: Pipeline reproducible con DVC

**Objetivo:** Convertir un proyecto de ML monolítico en un pipeline DVC modular, reproducible y versionable.

**Descripción:** Partiendo de un script único que carga, preprocesa, entrena y evalúa un modelo, refactoriza el código en tres scripts separados (`preparar_datos.py`, `entrenar.py`, `evaluar.py`). Crea el `dvc.yaml` correspondiente con las tres etapas, sus dependencias y outputs. Externaliza todos los hiperparámetros a `params.yaml`. Ejecuta el pipeline con `dvc repro`, modifica dos hiperparámetros en `params.yaml`, vuelve a ejecutar y verifica que solo se re-ejecutan las etapas afectadas. Crea un commit de Git tras cada experimento e incluye el `dvc.lock`. Usa `dvc metrics diff` para comparar las métricas entre ambos commits.

**Entregables:** Repositorio Git con `dvc.yaml`, `params.yaml`, `dvc.lock`, los tres scripts y la salida de `dvc metrics diff` copiada en un comentario del commit.

### Actividad 3: Model Card completa

**Objetivo:** Documentar un modelo de producción siguiendo el estándar de Mitchell et al. (2019), prestando especial atención al análisis por subgrupos y a las consideraciones éticas.

**Descripción:** Usando el modelo entrenado en la Actividad 1, redacta una Model Card completa en Markdown. Debe incluir obligatoriamente: (a) detalles del modelo con todos los campos; (b) uso previsto y fuera del alcance con al menos tres casos excluidos justificados; (c) tabla de métricas desagregadas por al menos dos subgrupos del dataset; (d) consideraciones éticas con al menos dos riesgos identificados y sus mitigaciones; (e) advertencias y recomendaciones con un plan de monitorización. La Model Card debe tener un mínimo de 600 palabras.

**Entregables:** Fichero `model_card.md` en el repositorio; reflexión escrita (máximo 200 palabras) sobre las limitaciones encontradas al documentar el modelo.

### Actividad 4: Análisis empírico de reproducibilidad

**Objetivo:** Comprender de forma experimental el impacto de las semillas aleatorias en la variabilidad de los resultados y sus implicaciones para entornos de producción.

**Descripción:** Entrena un `MLPClassifier` de scikit-learn (o un modelo PyTorch equivalente) sobre el dataset de tu elección, 20 veces: 10 sin fijar semilla y 10 con semilla fija (42). Para las 10 sin semilla, usa `random_state=None` o equivalente. Registra todas las ejecuciones en MLflow con el parámetro `semilla_fijada: true/false`. Calcula la media y la desviación estándar de la accuracy en ambos grupos. Genera un gráfico de caja (boxplot) comparando la distribución de accuracy entre los dos grupos y regístralo como artefacto en MLflow. Redacta un párrafo interpretando los resultados y su implicación para un sistema de ML en producción regulado bajo el EU AI Act.

**Entregables:** Script Python; runs registrados en MLflow con el parámetro `semilla_fijada`; gráfico boxplot; párrafo de análisis (mínimo 150 palabras).

---

## 10. Referencias

Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., y Gebru, T. (2019). Model Cards for Model Reporting. En *Proceedings of the Conference on Fairness, Accountability, and Transparency* (FAccT 2019). ACM. https://doi.org/10.1145/3287560.3287596

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., y Crawford, K. (2021). Datasheets for Datasets. *Communications of the ACM*, 64(12), 86–92. https://doi.org/10.1145/3458723

Pineau, J., Vincent-Lamarre, P., Sinha, K., Larivière, V., Beygelzimer, A., d'Alché-Buc, F., Fox, E., y Larochelle, H. (2020). Improving Reproducibility in Machine Learning Research (A Report from the NeurIPS 2019 Reproducibility Program). *Journal of Machine Learning Research*, 22(164), 1–20. https://jmlr.org/papers/v22/20-1364.html

MLflow. (2024). *MLflow Documentation: Tracking, Model Registry, Projects and Deployment*. Databricks. https://mlflow.org/docs/latest/index.html

DVC. (2024). *DVC Documentation: Data Version Control — Git for Data & Models*. Iterative. https://dvc.org/doc

Hugging Face. (2024). *Model Cards — Hugging Face Hub Documentation*. https://huggingface.co/docs/hub/model-cards

European Parliament and Council of the European Union. (2024). *Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act)*. Official Journal of the European Union. https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689

Sculley, D., Holt, G., Golovin, D., Davydov, E., Phillips, T., Ebner, D., Chaudhary, V., Young, M., Crespo, J. F., y Dennison, D. (2015). Hidden Technical Debt in Machine Learning Systems. En *Advances in Neural Information Processing Systems 28* (NeurIPS 2015). https://proceedings.neurips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html

Amershi, S., Begel, A., Bird, C., DeLine, R., Gall, H., Kamar, E., Nagappan, N., Nushi, B., y Zimmermann, T. (2019). Software Engineering for Machine Learning: A Case Study. En *Proceedings of the 41st International Conference on Software Engineering* (ICSE-SEIP 2019). https://doi.org/10.1109/ICSE-SEIP.2019.00042
