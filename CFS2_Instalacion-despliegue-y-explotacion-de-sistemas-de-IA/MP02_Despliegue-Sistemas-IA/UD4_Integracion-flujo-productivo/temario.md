# UD4 · Integración de sistemas de IA en el flujo productivo

---

## 1. Introducción

El desarrollo de software ha madurado hasta el punto de que las organizaciones más competitivas entregan valor en ciclos de horas o días, no de meses. Detrás de esa capacidad están las prácticas DevOps: integración continua, entrega continua, infraestructura como código, observabilidad y retroalimentación constante. Sin embargo, cuando el activo que se entrega es un modelo de aprendizaje automático, el paradigma clásico de DevOps se queda corto. Un modelo no es solo código: es código más datos más hiperparámetros más métricas de evaluación. Cambia el código de entrenamiento, cambian los datos y el modelo resultante es diferente, aunque el código sea idéntico. Esa naturaleza dual —software y artefacto estadístico— es lo que hace necesario MLOps.

MLOps (Machine Learning Operations) puede entenderse como la extensión de DevOps al ciclo de vida completo de los modelos de aprendizaje automático. Hereda los principios fundacionales de DevOps —automatización, reproducibilidad, colaboración entre equipos, entrega incremental y monitorización— y los adapta a las particularidades del ML: dependencia de datos, no determinismo en el entrenamiento, degradación silenciosa en producción y necesidad de reentrenamiento periódico.

Integrar un sistema de IA en el flujo productivo significa que el modelo no se trata como un producto artesanal que alguien entrena en su portátil y sube manualmente a producción. Significa que existe un pipeline automatizado que valida los datos, entrena el modelo, lo evalúa con criterios objetivos, lo registra de forma versionada, lo despliega de forma controlada y lo monitoriza en producción. Todo ese flujo está orquestado por herramientas que ya son familiares en el mundo DevOps —como GitHub Actions, Kubernetes o ArgoCD— combinadas con herramientas específicas de ML como MLflow, Airflow o Prefect.

Esta unidad didáctica recorre ese pipeline de extremo a extremo. Comienza por las diferencias conceptuales entre CI/CD clásico y MLOps CI/CD, construye paso a paso un workflow real en GitHub Actions, describe las etapas de un pipeline MLOps completo, aborda la automatización de tests de modelos, la conexión con pipelines de datos, los principios GitOps aplicados a ML, y el uso de feature flags para controlar el lanzamiento de nuevas versiones de modelos.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Distinguir las particularidades del CI/CD para ML respecto al CI/CD clásico de software y justificar por qué se requieren herramientas y prácticas adicionales.
- Diseñar y escribir workflows de GitHub Actions que cubran el ciclo completo de ML: validación, entrenamiento, evaluación, registro y despliegue.
- Identificar y configurar las etapas de un pipeline MLOps completo, incluyendo los gates de calidad que determinan el paso o el fallo entre etapas.
- Implementar tests automáticos de modelos —métricas mínimas, comparación challenger vs champion, equidad— dentro de un pipeline de CI.
- Conectar un pipeline de ML con pipelines de datos externos, gestionando triggers basados en disponibilidad de datos y eventos.
- Aplicar los principios GitOps al despliegue y actualización de modelos mediante herramientas como ArgoCD o FluxCD.
- Utilizar feature flags para gestionar la activación gradual de nuevas versiones de modelo, separando el despliegue del lanzamiento.

---

## 3. CI/CD para ML con GitHub Actions

### 3.1 Diferencias entre CI/CD clásico y MLOps CI/CD

En CI/CD clásico, el artefacto es un binario, una imagen Docker o un paquete. La misma entrada —el mismo código fuente— produce la misma salida en cada ejecución, a igualdad de dependencias. La calidad se mide principalmente con tests unitarios, de integración y de sistema: pasa o no pasa.

En MLOps CI/CD el panorama es más complejo por tres razones fundamentales:

**Doble fuente de cambio.** Un modelo puede cambiar porque cambia el código de entrenamiento o porque cambian los datos con los que se entrena. Ambas fuentes deben versionarse y ambas deben poder activar el pipeline. Los sistemas de control de versiones de datos (DVC, Delta Lake, LakeFS) son la respuesta técnica a este reto.

**No determinismo.** Incluso con el mismo código y los mismos datos, dos ejecuciones de entrenamiento pueden producir modelos con métricas ligeramente distintas debido a la aleatoriedad inherente en los algoritmos (inicialización de pesos, shuffling, dropout). El pipeline debe tolerar y gestionar esta variabilidad.

**Criterio de calidad multidimensional.** A diferencia de un test de software (binario: pasa/falla), la calidad de un modelo se expresa en métricas numéricas —accuracy, F1, AUC, latencia de inferencia, equidad entre grupos— que deben compararse con umbrales y con el modelo actualmente en producción.

Estas diferencias implican que el pipeline MLOps necesita etapas adicionales: validación de datos, registro de modelos con versiones y metadatos, y gates de calidad basados en métricas, no solo en tests.

### 3.2 Estructura de un workflow de GitHub Actions para ML

GitHub Actions organiza la automatización en archivos YAML dentro del directorio `.github/workflows/`. Cada archivo define un workflow que se activa mediante triggers y contiene uno o varios jobs, cada uno compuesto de steps.

**Triggers relevantes para ML:**

- `push` sobre ramas específicas: activa el pipeline cuando se empuja nuevo código de entrenamiento.
- `pull_request`: ejecuta validaciones antes de integrar cambios en la rama principal.
- `schedule`: activa el pipeline según un cron, por ejemplo para reentrenamiento periódico semanal.
- `workflow_dispatch`: permite lanzar el pipeline manualmente con parámetros personalizados.
- `repository_dispatch` o `workflow_call`: permiten que otros workflows o sistemas externos lancen el pipeline, útil para eventos basados en disponibilidad de datos.

**Jobs y steps:**

Los jobs se ejecutan en paralelo por defecto y pueden encadenarse con `needs`. Los steps son los pasos individuales dentro de un job: comandos de shell, acciones reutilizables de la marketplace de GitHub, o llamadas a scripts propios.

### 3.3 Ejemplo completo de workflow ML

El siguiente workflow ilustra el ciclo completo: lint, tests unitarios, entrenamiento condicional, evaluación, registro y despliegue.

```yaml
name: ML Pipeline

on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'data/**'
      - 'configs/**'
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * 1'  # Cada lunes a las 02:00 UTC
  workflow_dispatch:

env:
  PYTHON_VERSION: '3.11'
  MODEL_REGISTRY: mlflow

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt

      - name: Lint
        run: |
          ruff check src/
          mypy src/

      - name: Unit tests
        run: pytest tests/unit/ -v --tb=short

  train-and-evaluate:
    needs: lint-and-test
    runs-on: [self-hosted, gpu]  # Runner con GPU
    if: github.event_name != 'pull_request'
    steps:
      - uses: actions/checkout@v4

      - name: Restore DVC cache
        uses: actions/cache@v4
        with:
          path: .dvc/cache
          key: dvc-${{ hashFiles('data/*.dvc') }}

      - name: Pull data
        run: dvc pull

      - name: Train model
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
          MLFLOW_TRACKING_USERNAME: ${{ secrets.MLFLOW_TRACKING_USERNAME }}
          MLFLOW_TRACKING_PASSWORD: ${{ secrets.MLFLOW_TRACKING_PASSWORD }}
        run: python src/train.py --config configs/train.yaml

      - name: Evaluate model
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: python src/evaluate.py --threshold-f1 0.85

      - name: Upload evaluation report
        uses: actions/upload-artifact@v4
        with:
          name: evaluation-report
          path: reports/evaluation.html

  register-and-deploy:
    needs: train-and-evaluate
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Register model in MLflow
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: python src/register_model.py --stage Staging

      - name: Deploy to Kubernetes
        env:
          KUBECONFIG_DATA: ${{ secrets.KUBECONFIG }}
        run: |
          echo "$KUBECONFIG_DATA" | base64 -d > /tmp/kubeconfig
          kubectl --kubeconfig /tmp/kubeconfig set image deployment/model-serving \
            model-server=registry.example.com/model:${{ github.sha }}
```

### 3.4 Caché de dependencias en Actions

La instalación de dependencias Python puede tardar varios minutos. La acción `actions/setup-python` ofrece caché integrado mediante el parámetro `cache: 'pip'`. Esto almacena el directorio de paquetes y lo restaura en ejecuciones posteriores, reduciendo el tiempo de setup de 3-5 minutos a menos de 30 segundos en ejecuciones cacheadas.

Para dependencias de datos (datasets grandes, artefactos de modelos previos), `actions/cache` permite crear claves basadas en hashes de archivos de configuración, garantizando invalidación automática cuando los datos cambian.

### 3.5 Uso de GPU runners self-hosted

Los runners alojados por GitHub no incluyen GPU. Para entrenamientos que requieren CUDA, la opción es registrar un runner self-hosted en una máquina con GPU disponible. El runner se instala como servicio en la máquina física o en una VM con GPU y se referencia en el workflow con `runs-on: [self-hosted, gpu]`. La etiqueta `gpu` es personalizada y debe coincidir con las etiquetas registradas en el runner.

En entornos cloud, es posible aprovisionar runners efímeros con GPU bajo demanda usando soluciones como Actions Runner Controller (ARC) sobre Kubernetes con nodos GPU, o servicios gestionados como GitHub-hosted larger runners con GPU (disponibles en planes Enterprise).

### 3.6 Secrets en GitHub Actions

Las credenciales —URI del tracking server de MLflow, credenciales de Kubernetes, tokens de registros de contenedores— nunca deben escribirse en el código. GitHub Actions permite almacenar secrets a nivel de repositorio, organización o entorno (environment). Los secrets están cifrados y solo se inyectan como variables de entorno durante la ejecución del workflow, nunca aparecen en logs.

Los entornos (`environment: production`) añaden una capa adicional: permiten configurar aprobaciones manuales antes de que el job se ejecute, revisores requeridos y reglas de protección de rama, creando un gate humano antes del despliegue a producción.

---

## 4. Pipeline MLOps completo

Un pipeline MLOps completo no es simplemente "entrena y despliega". Es un flujo de etapas encadenadas, cada una con entradas, salidas y criterios de calidad bien definidos. Las etapas estándar son:

### 4.1 Etapa 1: Data Validation

Antes de entrenar, los datos deben validarse. La validación cubre:

- **Integridad del esquema:** las columnas esperadas existen, con los tipos correctos.
- **Distribución estadística:** las distribuciones de variables clave no han cambiado respecto a los datos de referencia (data drift). Herramientas: Great Expectations, Evidently AI, TensorFlow Data Validation.
- **Completitud:** porcentaje de valores nulos no supera umbrales definidos.
- **Volumen:** el dataset tiene suficientes ejemplos para entrenamiento.

Si la validación falla, el pipeline se detiene. Es preferible no entrenar a entrenar sobre datos corruptos o con drift severo no detectado.

### 4.2 Etapa 2: Feature Engineering

La ingeniería de características transforma los datos crudos en features utilizables por el modelo. Esta etapa debe:

- Ser reproducible: el mismo código de transformación produce las mismas features dado el mismo input.
- Estar versionada: los cambios en features deben rastrearse, pues afectan la reproducibilidad del modelo.
- Separar los parámetros de transformación aprendidos sobre train (escaladores, encoders) de los aplicados sobre test/producción para evitar data leakage.

Los Feature Stores (Feast, Tecton, Hopsworks) centralizan el cálculo y almacenamiento de features, evitando la inconsistencia entre el feature engineering offline (entrenamiento) y online (inferencia).

### 4.3 Etapa 3: Model Training

El entrenamiento ejecuta el algoritmo sobre los datos procesados y produce un modelo serializado. En el contexto del pipeline MLOps:

- Cada ejecución de entrenamiento debe registrar en el tracking server (MLflow) los hiperparámetros usados, las métricas de entrenamiento por época o iteración, y el artefacto del modelo.
- El entrenamiento debe poder reproducirse: versión del código (git commit hash), versión de los datos (hash DVC), versión de las dependencias (requirements.lock) y semilla aleatoria deben registrarse junto al modelo.
- El modelo serializado (pickle, ONNX, TorchScript, SavedModel) se almacena como artefacto de la ejecución.

### 4.4 Etapa 4: Model Evaluation

La evaluación calcula las métricas del modelo sobre un conjunto de test que no ha intervenido en el entrenamiento. Es la etapa del gate de calidad:

- **Umbral absoluto:** el modelo debe superar un mínimo de F1, accuracy, AUC u otras métricas definidas en la política del proyecto.
- **Comparación con producción (challenger vs champion):** si hay un modelo en producción, el nuevo modelo (challenger) debe superar al modelo actual (champion) en las métricas objetivo, o al menos no empeorar.
- **Métricas de equidad:** el rendimiento no debe degradarse significativamente en subgrupos protegidos (género, edad, geografía, etc.).

### 4.5 Etapa 5: Model Registration

Si el modelo supera los gates de evaluación, se registra en el Model Registry (MLflow Model Registry, Vertex AI Model Registry, SageMaker Model Registry). El registro incluye:

- Nombre del modelo y versión.
- Stage: Staging, Production, Archived.
- Metadatos: métricas, dataset usado, run de entrenamiento asociada, responsable del registro.
- Artefacto del modelo: accesible por nombre y versión desde cualquier sistema autorizado.

El Model Registry es la fuente de verdad para saber qué modelo está en producción y cuál es su linaje.

### 4.6 Etapa 6: Deployment

El despliegue toma el modelo registrado en Staging y lo promueve a Production, actualizando el servicio de inferencia. Las estrategias de despliegue se detallan en unidades anteriores (canary, blue/green, shadow). En el contexto del pipeline automatizado, el despliegue puede ser:

- **Automático:** si todos los gates se superan, el despliegue ocurre sin intervención humana.
- **Semi-automático:** el pipeline llega hasta Staging y requiere aprobación manual para promover a Production.

### 4.7 Etapa 7: Monitoring

La monitorización en producción cierra el ciclo. Se miden:

- **Data drift:** las distribuciones de los datos de entrada en producción se comparan con las del conjunto de entrenamiento.
- **Model drift / concept drift:** las predicciones del modelo derivan respecto a los valores reales, cuando estos están disponibles.
- **Métricas de sistema:** latencia de inferencia, throughput, tasa de errores.

Cuando el drift supera umbrales, se activa automáticamente un nuevo ciclo de entrenamiento, cerrando el loop.

### 4.8 Orquestación con GitHub Actions + MLflow + Kubernetes

La orquestación de las etapas puede implementarse de varias formas. Un enfoque pragmático combina:

- **GitHub Actions** para el control del flujo: qué etapas se ejecutan, en qué orden, con qué condiciones.
- **MLflow** para el tracking de experimentos, registro de modelos y almacenamiento de artefactos.
- **Kubernetes** para el despliegue y la escalabilidad de los servicios de inferencia.

Cada etapa del pipeline es un job en GitHub Actions que llama a scripts Python que a su vez registran resultados en MLflow. Los artefactos (modelo serializado, reports) se pasan entre etapas mediante MLflow Artifacts o `actions/upload-artifact` / `actions/download-artifact`.

### 4.9 Gates de calidad entre etapas

Un gate es una comprobación automática que determina si el pipeline puede avanzar a la siguiente etapa. Los gates se implementan como scripts que leen métricas del tracking server y devuelven código de salida 0 (paso) o distinto de 0 (fallo), lo que en GitHub Actions cancela el job y detiene el pipeline.

Ejemplos de gates:

- F1 en test > 0.85: entrenamiento pasa a evaluación.
- F1 del challenger > F1 del champion x 1.01: evaluación pasa a registro.
- Latencia p99 de inferencia < 200ms: registro pasa a despliegue.
- Equidad: diferencia de F1 entre grupos < 0.05: evaluación pasa a registro.

### 4.10 Artefactos entre etapas

Los artefactos que fluyen entre etapas son: el modelo serializado (en S3 o en el artifact store de MLflow), el archivo JSON con las métricas de evaluación que leen los gates, el informe de validación de datos generado por Great Expectations o Evidently, y el MLflow run ID que actúa como clave de trazabilidad enlazando el modelo desplegado con su experimento de origen.

---

## 5. Automatización de tests de modelos en CI

La calidad de un modelo no puede evaluarse solo manualmente. Los tests automáticos de modelos son tan importantes en MLOps como los tests unitarios en DevOps.

### 5.1 Tests automáticos de métricas

El test más básico es verificar que el modelo supera un umbral mínimo en el conjunto de test. Se implementa como un test de pytest:

```python
import pytest
import mlflow
import os

THRESHOLD_ACCURACY = 0.85
THRESHOLD_F1 = 0.82

def test_accuracy_above_threshold():
    client = mlflow.tracking.MlflowClient()
    run = client.get_run(run_id=os.environ["MLFLOW_RUN_ID"])
    accuracy = float(run.data.metrics["test_accuracy"])
    assert accuracy >= THRESHOLD_ACCURACY, (
        f"Accuracy {accuracy:.4f} por debajo del umbral minimo {THRESHOLD_ACCURACY}"
    )

def test_f1_above_threshold():
    client = mlflow.tracking.MlflowClient()
    run = client.get_run(run_id=os.environ["MLFLOW_RUN_ID"])
    f1 = float(run.data.metrics["test_f1"])
    assert f1 >= THRESHOLD_F1, (
        f"F1 {f1:.4f} por debajo del umbral minimo {THRESHOLD_F1}"
    )
```

Los umbrales no deben codificarse directamente en el test: deben leerse desde un archivo de configuración versionado (`configs/thresholds.yaml`), lo que permite ajustarlos sin modificar código de test ni requerir un nuevo release.

### 5.2 Comparación challenger vs champion

El test de comparación carga el modelo actualmente en producción (champion) y el modelo recién entrenado (challenger), los evalúa sobre el mismo conjunto de test y verifica que el challenger no degrada el rendimiento:

```python
from sklearn.metrics import f1_score
import mlflow
import pandas as pd

def test_challenger_beats_champion():
    champion = mlflow.pyfunc.load_model("models:/my_model/Production")
    challenger = mlflow.pyfunc.load_model("models:/my_model/Staging")

    X_test = pd.read_parquet("data/test/features.parquet")
    y_test = pd.read_parquet("data/test/labels.parquet")["label"]

    champion_f1 = f1_score(y_test, champion.predict(X_test), average="weighted")
    challenger_f1 = f1_score(y_test, challenger.predict(X_test), average="weighted")

    assert challenger_f1 >= champion_f1 * 0.99, (
        f"Challenger F1={challenger_f1:.4f} degrada Champion F1={champion_f1:.4f} "
        f"en mas del 1%"
    )
```

El margen de tolerancia (en el ejemplo, 1%) reconoce que diferencias muy pequeñas pueden deberse a variabilidad estadística. En producción, este margen se calibra según el volumen de datos de test y el impacto de negocio de una regresión.

### 5.3 Tests de equidad automatizados con Fairlearn

Fairlearn es la biblioteca de Microsoft que proporciona métricas de equidad y algoritmos de mitigación. En el contexto de CI, los tests de equidad verifican que el modelo no discrimina entre grupos definidos por atributos sensibles:

```python
from fairlearn.metrics import MetricFrame
from sklearn.metrics import accuracy_score
import mlflow
import pandas as pd

def test_fairness_across_groups():
    model = mlflow.pyfunc.load_model("models:/my_model/Staging")

    X_test = pd.read_parquet("data/test/features.parquet")
    y_test = pd.read_parquet("data/test/labels.parquet")["label"]
    sensitive = pd.read_parquet("data/test/sensitive.parquet")["gender"]

    y_pred = model.predict(X_test)

    mf = MetricFrame(
        metrics=accuracy_score,
        y_true=y_test,
        y_pred=y_pred,
        sensitive_features=sensitive
    )

    disparity = mf.difference()
    assert disparity < 0.05, (
        f"Disparidad de accuracy entre generos {disparity:.4f} supera limite 0.05\n"
        f"Por grupo:\n{mf.by_group}"
    )
```

Este test falla el pipeline si el modelo discrimina más de 5 puntos porcentuales de accuracy entre grupos. El umbral de equidad debe definirse junto con los responsables de negocio y el equipo legal, no solo por el equipo técnico.

### 5.4 Generacion automatica de reports con pytest-html

El plugin `pytest-html` genera un informe HTML con el resultado de cada test, los mensajes de error cuando fallan y el tiempo de ejecución. En el workflow de GitHub Actions, este informe se sube como artefacto:

```yaml
- name: Run model tests
  run: pytest tests/model/ -v --html=reports/model_tests.html --self-contained-html

- name: Upload test report
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: model-test-report
    path: reports/model_tests.html
```

La opción `if: always()` garantiza que el informe se suba incluso cuando los tests fallan, lo que es esencial para diagnosticar la causa del fallo sin tener que relanzar el pipeline manualmente.

### 5.5 Badge de estado del modelo en README

GitHub Actions permite mostrar el estado del ultimo workflow como un badge en el README del repositorio:

```markdown
![ML Pipeline](https://github.com/org/repo/actions/workflows/ml-pipeline.yml/badge.svg)
```

Este badge muestra en tiempo real si el pipeline ML esta pasando o fallando, dando visibilidad inmediata del estado de salud del modelo a todo el equipo: si el badge es rojo, el modelo en Staging no supera los tests de calidad y no debe promoverse a produccion.

---

## 6. Integración con data pipelines

El pipeline de ML no existe en aislamiento: depende de datos que generalmente son producidos y gestionados por pipelines de datos separados, orquestados con herramientas como Apache Airflow o Prefect.

### 6.1 Conexión entre pipeline de datos y pipeline de ML

La relación entre ambos pipelines puede modelarse de varias formas:

**Acoplamiento por horario (polling):** el pipeline de ML se ejecuta en un cron y descarga la última versión disponible de los datos. Es el enfoque más simple, pero introduce latencia y no detecta si los datos aún no están listos.

**Acoplamiento por evento (event-driven):** el pipeline de datos emite un evento cuando un nuevo dataset está listo, y ese evento activa el pipeline de ML. Es el enfoque más eficiente y robusto.

**Acoplamiento por artefacto versionado:** el pipeline de datos publica una nueva versión del dataset en un sistema como DVC o Delta Lake, y el pipeline de ML se activa cuando detecta la nueva versión mediante una comparación de hashes.

### 6.2 Triggers basados en disponibilidad de datos

En GitHub Actions, el trigger `repository_dispatch` permite que un sistema externo active un workflow mediante una llamada a la API de GitHub:

```bash
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/org/repo/dispatches \
  -d '{"event_type": "new_data_available", "client_payload": {"dataset_version": "v2026-06-24"}}'
```

El pipeline de datos (por ejemplo, una tarea de Airflow) ejecuta esta llamada al finalizar la preparación del dataset, activando automáticamente el pipeline de ML con los metadatos del nuevo dataset en el payload.

En el workflow de GitHub Actions, el evento se recoge así:

```yaml
on:
  repository_dispatch:
    types: [new_data_available]

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - name: Get dataset version from event
        run: echo "Dataset version: ${{ github.event.client_payload.dataset_version }}"
```

### 6.3 Gestión de dependencias entre pipelines

Cuando el pipeline de ML depende de múltiples fuentes de datos gestionadas por distintos pipelines, se necesita un sistema de coordinación:

- **Airflow sensors:** el pipeline ML en Airflow puede tener un `S3KeySensor` o `ExternalTaskSensor` que espera a que el dataset del pipeline de datos esté disponible antes de continuar.
- **Prefect dependencies:** Prefect permite modelar dependencias entre flows de distintos proyectos usando automations y eventos.
- **Tabla de estado en base de datos:** un enfoque sencillo donde el pipeline de datos actualiza un registro en una tabla con el estado del dataset, y el pipeline de ML lo consulta antes de iniciar.

En todos los casos, el pipeline de ML debe registrar en sus metadatos qué versión de los datos utilizó para entrenar, creando trazabilidad completa entre el dataset y el modelo resultante.

### 6.4 Event-driven MLOps con Kafka y SQS

En arquitecturas de mayor escala, los sistemas de mensajería como Apache Kafka (on-premise) o Amazon SQS (cloud) actúan como bus de eventos entre el pipeline de datos y el pipeline de ML.

El flujo típico es:

1. El pipeline de datos publica un mensaje en un topic de Kafka (por ejemplo, `data.training.ready`) con metadatos del dataset: versión, ruta en S3, número de ejemplos, checksum.
2. Un consumidor de Kafka escucha ese topic y, al recibir el mensaje, activa el pipeline de ML mediante la API de GitHub Actions o directamente a través de un orquestador como Airflow.
3. El pipeline de ML procesa los nuevos datos, produce un nuevo modelo y publica un evento en otro topic (por ejemplo, `model.training.completed`).
4. Otros sistemas suscritos a ese topic —el sistema de despliegue, el de notificaciones, el de monitorización— reaccionan de forma autónoma.

Este patrón desacopla completamente los sistemas, mejora la resiliencia (si el consumidor de Kafka está caído, los mensajes se acumulan en el topic y se procesan cuando vuelve a estar disponible) y facilita la escalabilidad horizontal.

---

## 7. GitOps para ML

### 7.1 Principios GitOps aplicados a ML

GitOps es un paradigma operacional donde Git es la única fuente de verdad para el estado deseado del sistema. Cualquier cambio en la infraestructura o la configuración se realiza mediante un commit en Git, y un operador automatizado se encarga de hacer que el estado real del sistema converja con el estado declarado en el repositorio.

Aplicado a ML, los principios GitOps significan:

- La configuración del modelo en producción (qué versión del modelo sirve qué endpoint, con qué configuración de recursos) se define en archivos YAML en un repositorio Git.
- Nadie modifica la configuración de producción directamente: todos los cambios pasan por un pull request, con revisión de código y aprobación.
- Un operador (ArgoCD, FluxCD) monitoriza el repositorio y aplica automáticamente los cambios cuando detecta una diferencia entre el estado declarado y el estado real del clúster.

Esto aporta auditabilidad completa (cada cambio tiene un commit, un autor, una fecha), reversibilidad trivial (revertir es hacer un `git revert`) y reproducibilidad del entorno de despliegue.

### 7.2 ArgoCD para sincronización de estado deseado

ArgoCD es un operador GitOps para Kubernetes. Monitoriza uno o varios repositorios Git y sincroniza el estado del clúster con los manifiestos declarados en esos repositorios.

Para un modelo ML, el repositorio GitOps puede contener:

```yaml
# manifests/model-serving/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-serving
  namespace: ml-production
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: model-server
          image: registry.example.com/model-server:v1.4.2
          env:
            - name: MODEL_NAME
              value: "my_model"
            - name: MODEL_VERSION
              value: "42"
            - name: MLFLOW_TRACKING_URI
              valueFrom:
                secretKeyRef:
                  name: mlflow-credentials
                  key: tracking-uri
          resources:
            requests:
              memory: "2Gi"
              cpu: "500m"
            limits:
              memory: "4Gi"
              cpu: "2000m"
```

Cuando el pipeline de ML produce un nuevo modelo aprobado, un script actualiza el valor `MODEL_VERSION` en este archivo y crea un commit. ArgoCD detecta el cambio en la rama principal y actualiza el Deployment en Kubernetes sin intervención humana, pero con trazabilidad completa en Git.

### 7.3 FluxCD

FluxCD es una alternativa a ArgoCD con un enfoque más modular: en lugar de un servidor centralizado con interfaz web, Flux utiliza controladores Kubernetes que se ejecutan dentro del clúster. Es más adecuado para entornos donde se prefiere no exponer una interfaz de usuario adicional o donde se necesita mayor granularidad en el control de sincronización.

Flux soporta Helm charts y Kustomize, lo que lo hace flexible para distintas formas de definir la configuración de Kubernetes. Su Image Automation Controller es especialmente útil en MLOps: puede monitorizar un registro de contenedores y actualizar automáticamente el manifiesto cuando se publica una nueva imagen, cerrando el loop entre el pipeline de CI y el despliegue GitOps sin intervención manual.

### 7.4 Ejemplo de GitOps workflow para actualización de modelo

El flujo completo de una actualización de modelo bajo GitOps:

1. El pipeline de CI/CD entrena y evalúa el nuevo modelo (challenger).
2. Si el challenger supera los gates de calidad, el pipeline ejecuta un script que registra el modelo en MLflow Model Registry con la versión nueva (por ejemplo, v43).
3. El mismo script crea una rama en el repositorio GitOps con el cambio en el manifiesto (`MODEL_VERSION: "43"`) y abre un pull request automático cuya descripción incluye las métricas del nuevo modelo y el enlace al run de MLflow.
4. Un revisor (humano, o un bot automático si las métricas superan un umbral muy alto) aprueba y mergea el PR.
5. ArgoCD detecta el merge, sincroniza el clúster y actualiza el Deployment con el nuevo modelo.
6. La monitorización confirma que el nuevo modelo sirve correctamente en producción y que las métricas operacionales (latencia, error rate) son normales.

Este flujo combina automatización con supervisión humana en el punto donde más importa: la decisión de llevar un modelo a producción.

---

## 8. Feature flags en integración ML

### 8.1 Concepto de feature flags en ML

Los feature flags (también llamados feature toggles) son mecanismos que permiten activar o desactivar funcionalidades en tiempo de ejecución, sin necesidad de un nuevo despliegue. En el contexto de ML, se utilizan para controlar qué versión del modelo recibe el tráfico de inferencia.

La separación entre **despliegue (deploy)** y **lanzamiento (release)** es un principio fundamental de la entrega continua moderna. Con feature flags, es posible:

- Desplegar el nuevo modelo en producción (está físicamente disponible) sin que reciba tráfico real.
- Activar el nuevo modelo gradualmente: primero al 1% de los usuarios, luego al 10%, al 50%, y finalmente al 100%.
- Revertir instantáneamente si se detecta un problema: basta con cambiar el flag, sin necesidad de un nuevo despliegue.
- Probar el nuevo modelo con segmentos específicos de usuarios antes de un despliegue global.

### 8.2 Separación entre deploy y release

En un despliegue tradicional, deploy y release ocurren simultáneamente: cuando el código nuevo llega a producción, todos los usuarios lo reciben inmediatamente. Esto crea ventanas de riesgo: si algo falla, afecta a todos los usuarios hasta que se complete un rollback.

Con feature flags:

- **Deploy:** el nuevo modelo se despliega en la infraestructura de producción. Está disponible, pero ningún usuario lo recibe aún.
- **Release:** se activa el flag que dirige tráfico al nuevo modelo. Esto puede ocurrir de forma gradual (canary controlado por flag) o binaria (encendido/apagado).

El rollback se reduce a desactivar el flag: el modelo anterior sigue desplegado y disponible, por lo que la reversión es instantánea y no requiere intervención de ingeniería ni un nuevo ciclo de despliegue.

### 8.3 Integración con LaunchDarkly

LaunchDarkly es un servicio SaaS de gestión de feature flags que ofrece segmentación avanzada (activar un flag para usuarios con determinadas características), variaciones multivariantes (no solo on/off, sino múltiples valores, útil para seleccionar entre varias versiones de modelo), y análisis de impacto.

En el contexto ML, el código de inferencia consulta LaunchDarkly para saber qué versión del modelo servir a cada request:

```python
import ldclient
from ldclient.config import Config

ldclient.set_config(Config(os.getenv("LAUNCHDARKLY_SDK_KEY")))
ld_client = ldclient.get()

def get_prediction(features: dict, user_id: str) -> float:
    context = ldclient.Context.builder(user_id).build()

    model_version = ld_client.variation(
        "active-model-version",
        context,
        default="v41"  # Fallback si el servicio de flags no responde
    )

    model = load_model(model_version)
    return model.predict(features)
```

Los flags con valores de cadena (en lugar de booleanos) permiten seleccionar entre múltiples versiones de modelo sin necesidad de lógica condicional adicional en el código.

### 8.4 Integración con Unleash

Unleash es la alternativa open-source, autohospedada. Ofrece funcionalidades similares a LaunchDarkly sin depender de un servicio externo, lo que puede ser relevante para entornos con requisitos de privacidad estrictos o sin acceso a internet desde los servidores de inferencia.

```python
from UnleashClient import UnleashClient

unleash = UnleashClient(
    url="https://unleash.empresa.internal/api",
    app_name="inference-service",
    custom_headers={"Authorization": os.getenv("UNLEASH_TOKEN")}
)
unleash.initialize_client()

def predict(features: dict, user_context: dict) -> float:
    context = {"userId": user_context["user_id"]}

    if unleash.is_enabled("new-fraud-model-v42", context):
        return model_v42.predict(features)
    else:
        return model_v38.predict(features)  # champion actual
```

Las estrategias de activación de Unleash permiten configurar el porcentaje de usuarios que reciben el nuevo modelo directamente desde la interfaz de administración, sin modificar código ni relanzar el servicio.

### 8.5 Canary release y shadow mode con feature flags

La combinación de feature flags con MLOps habilita dos patrones de lanzamiento especialmente útiles:

**Canary release controlado por flag:** el nuevo modelo sirve al X% del tráfico real. Las métricas de negocio (tasa de fraude detectado, satisfacción del usuario) se comparan entre el grupo que recibe el modelo nuevo y el que recibe el modelo champion. El porcentaje se incrementa gradualmente si las métricas son iguales o mejores.

**Shadow mode:** el nuevo modelo recibe una copia de cada request de producción y produce una predicción, pero esa predicción no se usa para tomar ninguna decisión real. Solo se registra para comparar con la predicción del modelo champion. Esto permite evaluar el nuevo modelo con tráfico real sin ningún riesgo para el negocio. La activación del shadow mode puede controlarse también mediante un feature flag, desacoplando completamente el despliegue físico del modelo de su activación en cualquier modo.

---

## 9. Actividades prácticas

### Actividad 1: Workflow GitHub Actions para ML

Partiendo de un repositorio de ejemplo con un clasificador scikit-learn, el estudiante debe crear un workflow completo en GitHub Actions que incluya: lint con ruff, tests unitarios con pytest, entrenamiento condicional (solo si cambian `src/` o `data/`), evaluación con umbral mínimo de F1=0.80, y registro del modelo en MLflow. El workflow debe ejecutarse tanto en push a main como en pull request. Se valorará el uso de caché de pip y la correcta gestión de secrets para las credenciales de MLflow.

**Entregables:** archivo `.github/workflows/ml-pipeline.yml`, capturas de pantalla del workflow ejecutándose en GitHub Actions, y un breve informe (máximo una página) describiendo las decisiones de diseño tomadas.

### Actividad 2: Implementación de gates de calidad y tests de modelo

Sobre el workflow de la actividad anterior, el estudiante debe añadir tests automáticos de modelo usando pytest, incluyendo: test de umbral mínimo de F1, test de comparación con el modelo champion cargado desde MLflow, y un test de equidad básico usando Fairlearn sobre un atributo sensible del dataset. Los tests deben generar un informe HTML con pytest-html que se suba como artefacto del workflow con `if: always()` para garantizar su disponibilidad incluso cuando los tests fallan.

**Entregables:** archivos de test en `tests/model/`, configuración de pytest, y el informe HTML generado en una ejecución real.

### Actividad 3: Event-driven MLOps con repository_dispatch

El estudiante debe simular un pipeline event-driven donde un script externo (que representa el pipeline de datos) activa el pipeline de ML mediante la API de `repository_dispatch` de GitHub. El pipeline de ML debe leer el `client_payload` para obtener la versión del dataset a utilizar en el entrenamiento. Se valorará que el script del pipeline de datos incluya gestión de errores para el caso en que la llamada a la API falle.

**Entregables:** script del "pipeline de datos" que invoca el dispatch, modificaciones al workflow para leer el payload, y capturas del flujo completo mostrando el trigger y la ejecución resultante en GitHub Actions.

### Actividad 4: GitOps con ArgoCD

En un clúster Kubernetes local (minikube o kind), el estudiante debe instalar ArgoCD y configurar una aplicación que sincronice los manifiestos de despliegue de un modelo desde un repositorio Git. Una vez configurado, debe simular la actualización del modelo modificando el tag de imagen o la versión del modelo en el manifiesto y verificando que ArgoCD sincroniza el cambio automáticamente. Finalmente, debe realizar un rollback mediante `git revert` y verificar que ArgoCD revierte el despliegue al estado anterior.

**Entregables:** repositorio GitOps con los manifiestos, capturas de la interfaz de ArgoCD mostrando la sincronización exitosa y el rollback, y un breve documento (máximo dos páginas) describiendo el flujo y las lecciones aprendidas.

---

## 10. Referencias

- **GitHub Actions Documentation.** Workflows, jobs, steps, secrets, self-hosted runners, environments, repository_dispatch y workflow_dispatch.
  https://docs.github.com/en/actions

- **Gift, Noah y Deza, Alfredo. *Practical MLOps: Operationalizing Machine Learning Models*.** O'Reilly Media, 2021. ISBN 978-1-098-10301-0. Cubre MLOps en AWS, Azure y GCP, con especial atención a GitHub Actions y automatización de pipelines ML.
  https://www.oreilly.com/library/view/practical-mlops/9781098103002/

- **ArgoCD Documentation.** Instalación, configuración de aplicaciones, sincronización, políticas de salud y rollback.
  https://argo-cd.readthedocs.io/en/stable/

- **Sato, Danilo; Wider, Arif y Windheuser, Christoph. "Continuous Delivery for Machine Learning."** Martin Fowler Blog, 2019. Artículo seminal que describe el pipeline CD4ML con sus etapas, gates y prácticas de testing de modelos.
  https://martinfowler.com/articles/cd4ml.html

- **MLflow Documentation.** Tracking, Model Registry, Projects y despliegue. Referencia completa para la instrumentación del pipeline MLOps.
  https://mlflow.org/docs/latest/index.html

- **FluxCD Documentation.** GitOps para Kubernetes con Flux v2, Helm Controller, Kustomize Controller e Image Automation Controller.
  https://fluxcd.io/flux/

- **Fairlearn Documentation.** Métricas de equidad, MetricFrame, algoritmos de mitigación y guías de uso en pipelines de CI.
  https://fairlearn.org/main/user_guide/

- **Prefect Documentation.** Orquestación de pipelines de datos y ML, deployments, automations y triggers basados en eventos.
  https://docs.prefect.io/

- **LaunchDarkly Documentation.** Feature flags, segmentación, variaciones multivariantes e integración con SDKs Python.
  https://docs.launchdarkly.com/

- **Unleash Documentation.** Plataforma open-source de feature flags, estrategias de activación gradual e integración con aplicaciones Python.
  https://docs.getunleash.io/
