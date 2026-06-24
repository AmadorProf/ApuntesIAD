# UD3 · Instalación de aplicaciones de despliegue para sistemas de IA

---

## 1. Introducción — el stack de software de despliegue ML: más allá del modelo

Durante años, el foco de los equipos de ciencia de datos se concentró casi exclusivamente en el modelo: su arquitectura, sus métricas de validación, la calidad de los datos de entrenamiento. Sin embargo, la experiencia acumulada en la industria ha dejado claro que un modelo excelente que no puede desplegarse de forma estable, reproducible y observable en producción carece de valor real. La brecha entre el cuaderno de Jupyter donde nace el modelo y el servicio que atiende millones de peticiones diarias es, en la práctica, mayor que la brecha entre el prototipo y el modelo entrenado.

El stack de software de despliegue ML es el conjunto de herramientas, plataformas y prácticas que cierra esa brecha. Se articula en varias capas diferenciadas pero interdependientes.

La **capa de gestión del ciclo de vida del modelo** incluye herramientas como MLflow o Kubeflow Pipelines, que permiten registrar experimentos, versionar modelos, comparar ejecuciones y promover artefactos desde el entorno de desarrollo hasta producción con trazabilidad completa. Sin esta capa, la reproducibilidad es un accidente feliz, no una garantía.

La **capa de empaquetado y containerización** encapsula el modelo y todas sus dependencias —versión de Python, librerías, pesos, configuración— en una unidad desplegable inmutable. Docker es el estándar de facto para esto, pero las prácticas de construcción importan tanto como la herramienta: una imagen mal construida introduce vulnerabilidades, ralentiza el despliegue y dificulta la depuración.

La **capa de orquestación** se apoya en Kubernetes, que se ha convertido en el sustrato operativo dominante para cargas de trabajo en producción. No es la única opción, pero es la que sustenta la mayor parte del ecosistema MLOps moderno. Sobre Kubernetes operan herramientas específicas para ML como KServe o Seldon Core, que abstraen los patrones comunes de serving de modelos.

La **capa de serving** expone el modelo como un servicio HTTP/gRPC con capacidades como escalado automático, versionado de endpoints, canary releases y recogida de métricas. Esta capa transforma un artefacto estático en un servicio operativo.

La **capa de gestión de dependencias y seguridad** garantiza que las dependencias no gestionadas no se conviertan en deuda técnica que eventualmente se cobre en forma de vulnerabilidades o builds no reproducibles. El pinning de versiones, los SBOM y el escaneo de imágenes no son opcionales en entornos donde corre software de terceros procesando datos sensibles.

Esta unidad estudia cada una de estas capas en detalle: cómo se instalan, cómo se configuran y cómo interoperan para formar un pipeline de despliegue robusto.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Instalar y configurar MLflow Tracking Server con backend de base de datos relacional PostgreSQL y almacén de artefactos en S3 o MinIO, incluyendo autenticación básica.
- Instalar Kubeflow en un clúster de Kubernetes utilizando manifests oficiales e identificar los componentes principales de la plataforma y su función.
- Seleccionar la plataforma MLOps adecuada según las restricciones técnicas y organizativas del proyecto, apoyándose en criterios objetivos de comparación.
- Desplegar modelos mediante KServe utilizando el recurso InferenceService y configurar predictors para distintos frameworks de ML.
- Desplegar pipelines de modelos con Seldon Core mediante el recurso SeldonDeployment, incluyendo combiners y routers.
- Construir imágenes Docker optimizadas para cargas de trabajo ML aplicando multi-stage builds, buenas prácticas de seguridad y estrategias de cacheo de capas.
- Trabajar con registros de contenedores públicos y privados, incluyendo la firma y verificación de imágenes con Cosign.
- Crear y gestionar Helm charts para aplicaciones de serving de modelos, incluyendo la parametrización mediante values.yaml y la gestión de múltiples releases con Helmfile.
- Generar SBOM de imágenes con Syft y realizar escaneos de vulnerabilidades con Trivy o Grype.
- Implementar estrategias de actualización controlada de dependencias en pipelines de CI/CD mediante Dependabot o Renovate.

---

## 3. Plataformas MLOps: instalación y configuración

### 3.1 MLflow: instalación del Tracking Server con PostgreSQL y MinIO

MLflow es una plataforma de código abierto para gestionar el ciclo de vida de los experimentos de ML. Su componente central es el Tracking Server, que almacena métricas, parámetros, tags y artefactos de cada ejecución de entrenamiento.

Una instalación de producción requiere dos backends externos: una base de datos relacional para los metadatos y un almacén de objetos para los artefactos. La base de datos por defecto (SQLite) no es apta para entornos concurrentes ni para datos persistentes en contenedores efímeros.

**Instalación de paquetes**

```bash
pip install mlflow psycopg2-binary boto3
```

La cadena de conexión a PostgreSQL se pasa a través de la variable de entorno `MLFLOW_BACKEND_STORE_URI`:

```bash
export MLFLOW_BACKEND_STORE_URI="postgresql://mlflow_user:password@postgres-host:5432/mlflow_db"
```

El esquema de la base de datos se inicializa automáticamente en el primer arranque del servidor. En producción, conviene ejecutar `mlflow db upgrade` explícitamente antes de arrancar el servidor para separar la migración del arranque.

**MinIO como artifact store compatible con S3**

MinIO es un servidor de almacenamiento de objetos compatible con la API de S3. Permite tener un artifact store self-hosted sin depender de AWS:

```bash
# Arrancar MinIO en Docker (desarrollo/test)
docker run -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

El Tracking Server se configura apuntando al bucket de MinIO mediante variables de entorno:

```bash
export MLFLOW_ARTIFACT_ROOT="s3://mlflow-artifacts/"
export MLFLOW_S3_ENDPOINT_URL="http://minio-host:9000"
export AWS_ACCESS_KEY_ID="minioadmin"
export AWS_SECRET_ACCESS_KEY="minioadmin"
```

**Arranque del servidor**

```bash
mlflow server \
  --backend-store-uri $MLFLOW_BACKEND_STORE_URI \
  --default-artifact-root $MLFLOW_ARTIFACT_ROOT \
  --host 0.0.0.0 \
  --port 5000
```

**Configuración de autenticación**

A partir de MLflow 2.5, el servidor incluye autenticación básica integrada. Se activa mediante el flag `--app-name basic-auth`:

```bash
mlflow server \
  --app-name basic-auth \
  --backend-store-uri $MLFLOW_BACKEND_STORE_URI \
  --default-artifact-root $MLFLOW_ARTIFACT_ROOT
```

La gestión de usuarios se realiza a través de la API REST de administración. En entornos corporativos es habitual colocar un proxy inverso (NGINX, Traefik) con autenticación OIDC delante del servidor MLflow usando oauth2-proxy como sidecar.

### 3.2 Kubeflow: instalación en Kubernetes con manifests

Kubeflow es la plataforma MLOps nativa de Kubernetes. Su instalación es significativamente más compleja que la de MLflow porque despliega múltiples microservicios interdependientes.

**Requisitos previos**

- Clúster de Kubernetes 1.25 o superior.
- `kubectl` configurado con permisos de administrador de clúster.
- `kustomize` versión 5.x.
- Recursos mínimos recomendados: 4 CPU y 12 GB RAM por nodo worker.

**Instalación con manifests oficiales**

El repositorio oficial `kubeflow/manifests` utiliza Kustomize para gestionar la instalación:

```bash
git clone https://github.com/kubeflow/manifests.git
cd manifests

# Instalar todos los componentes (puede tardar 5-10 minutos)
while ! kustomize build example | kubectl apply -f -; do
  echo "Reintentando..."; sleep 10;
done
```

El bucle de reintento es necesario porque algunos recursos dependen de CRDs que pueden no estar listos en el momento en que se crean los objetos que los referencian, lo que produce errores recuperables en la primera pasada.

**Verificación de la instalación**

```bash
kubectl get pods -n kubeflow
kubectl get pods -n istio-system
kubectl get pods -n cert-manager
```

Todos los pods deben alcanzar el estado `Running` o `Completed` antes de considerar la instalación completa.

**Componentes principales de Kubeflow**

- **Kubeflow Pipelines (KFP):** Sistema de orquestación de pipelines de ML basado en Argo Workflows. Permite definir pipelines como grafos dirigidos acíclicos (DAG) de componentes containerizados. La interfaz web permite visualizar ejecuciones, inspeccionar artefactos y comparar runs entre sí.

- **KServe (antes KFServing):** Plataforma de serving de modelos que opera sobre Knative Serving e Istio. Proporciona escalado a cero, canary releases y soporte para múltiples frameworks. Se estudia en detalle en la sección 4.

- **Kubeflow Notebooks:** Permite aprovisionar servidores de Jupyter Notebook directamente en el clúster, con acceso controlado por usuario y namespace. Facilita que los data scientists trabajen en un entorno reproducible con acceso a los datos y recursos del clúster sin necesidad de configurar entornos locales.

- **Katib:** Sistema de hyperparameter tuning y neural architecture search integrado con Kubeflow Pipelines. Ejecuta múltiples trials en paralelo sobre el clúster.

- **Training Operator:** CRDs para ejecutar jobs de entrenamiento distribuido de TensorFlow (`TFJob`), PyTorch (`PyTorchJob`), MXNet y XGBoost directamente en Kubernetes.

### 3.3 MLflow vs Kubeflow: cuándo usar cada uno

La elección entre MLflow y Kubeflow no siempre es evidente y con frecuencia la respuesta es "ambos", dado que cubren aspectos complementarios del ciclo de vida ML. Sin embargo, como plataformas principales de MLOps, sus filosofías de diseño y sus requisitos operativos difieren sustancialmente.

**Elige MLflow cuando:**
- El equipo es pequeño o no dispone de expertise en Kubernetes.
- Se necesita una solución de tracking rápida de instalar y operar.
- El entorno de computación no está basado en Kubernetes (máquinas virtuales, clusters Spark, entornos locales).
- La prioridad es el tracking de experimentos y el registro de modelos, no la orquestación de pipelines complejos.
- Se busca integración sencilla con Databricks.

**Elige Kubeflow cuando:**
- La organización ya opera Kubernetes en producción y tiene el expertise para mantenerlo.
- Se necesita orquestación de pipelines de entrenamiento complejos y reproducibles.
- Se requiere serving de modelos con escalado automático y canary releases a nivel de plataforma.
- Hay múltiples equipos o proyectos que necesitan aislamiento mediante namespaces.
- Se necesita entrenamiento distribuido a gran escala.

### 3.4 Tabla comparativa de plataformas MLOps

| Característica | MLflow | Kubeflow | Vertex AI | SageMaker | Azure ML |
|---|---|---|---|---|---|
| **Modelo de despliegue** | Self-hosted / Databricks | Self-hosted (K8s) | Managed (GCP) | Managed (AWS) | Managed (Azure) |
| **Tracking de experimentos** | Nativo, excelente | Mediante KFP | Experiments API | Experiments | MLflow integrado |
| **Orquestación de pipelines** | MLflow Projects (limitado) | KFP (Argo) | Vertex Pipelines | SageMaker Pipelines | Azure ML Pipelines |
| **Serving de modelos** | MLflow Models (básico) | KServe | Vertex Prediction | SageMaker Endpoints | Azure ML Endpoints |
| **Registry de modelos** | MLflow Model Registry | Kubeflow Model Registry | Vertex Model Registry | SageMaker Model Registry | Azure ML Model Registry |
| **Complejidad operativa** | Baja | Alta | Muy baja | Baja | Baja |
| **Coste** | Infraestructura propia | Infraestructura propia | Por uso (GCP) | Por uso (AWS) | Por uso (Azure) |
| **Curva de aprendizaje** | Baja | Alta | Media | Media | Media |
| **Multi-cloud / on-prem** | Sí | Sí | No | No | No |
| **Vendor lock-in** | Ninguno | Ninguno | Alto (GCP) | Alto (AWS) | Alto (Azure) |

---

## 4. Frameworks de serving: instalación y configuración

### 4.1 KServe (antes KFServing)

KServe es el framework de serving de modelos de referencia en el ecosistema Kubernetes. Abstrae la complejidad del serving mediante el CRD `InferenceService`, que describe de forma declarativa un endpoint de inferencia, incluyendo el modelo, el runtime, los recursos y las políticas de escalado.

**Instalación**

KServe requiere Knative Serving e Istio (o alternativas como Kourier). En un clúster con Kubeflow instalado, KServe ya está disponible como componente integrado. Para instalación standalone:

```bash
# Instalar cert-manager (prerequisito)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.15.0/cert-manager.yaml

# Esperar a que cert-manager esté listo
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s

# Instalar KServe
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.13.0/kserve.yaml
```

**InferenceService: el recurso central**

El recurso `InferenceService` describe un endpoint de inferencia. La especificación para un modelo sklearn:

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: sklearn-iris
  namespace: default
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: "gs://kfserving-examples/models/sklearn/1.0/model"
      resources:
        requests:
          memory: "256Mi"
          cpu: "100m"
        limits:
          memory: "512Mi"
          cpu: "500m"
```

KServe descargará el modelo del almacén especificado en `storageUri`, lo cargará en el servidor de inferencia apropiado y expondrá un endpoint HTTP/gRPC compatible con el protocolo V2 de inferencia (Open Inference Protocol).

**Predictors para distintos frameworks**

KServe soporta de forma nativa los frameworks de ML más comunes a través de runtimes predefinidos:

- **sklearn:** `modelFormat: name: sklearn` — utiliza `mlserver` con el runtime de scikit-learn.
- **PyTorch:** `modelFormat: name: pytorch` — utiliza TorchServe.
- **TensorFlow:** `modelFormat: name: tensorflow` — utiliza TF Serving.
- **XGBoost:** `modelFormat: name: xgboost` — utiliza `mlserver` con el runtime de XGBoost.
- **ONNX:** `modelFormat: name: onnx` — utiliza Triton Inference Server de NVIDIA, especialmente adecuado para inferencia de alto rendimiento.
- **Modelos custom:** Se puede especificar un container completamente personalizado para cualquier framework o lógica de inferencia no estándar.

**Canary rollouts**

KServe soporta canary releases de forma declarativa. Para dirigir el 20% del tráfico a una nueva versión del modelo manteniendo el 80% en la versión estable:

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: fraud-detector
spec:
  predictor:
    canaryTrafficPercent: 20
    model:
      modelFormat:
        name: sklearn
      storageUri: "s3://my-models/fraud/v2"
```

El tráfico restante continúa dirigiéndose al predictor principal (versión anterior). Una vez validado el rendimiento de la nueva versión mediante métricas de negocio y técnicas, se puede promover al 100% eliminando el campo `canaryTrafficPercent`.

### 4.2 Seldon Core

Seldon Core está orientado a pipelines de inferencia más complejos, donde múltiples modelos se encadenan, se combinan o se enrutan de forma dinámica. El recurso central es el `SeldonDeployment`.

**Instalación con Helm**

```bash
helm repo add seldon https://storage.googleapis.com/seldon-charts
helm install seldon-core seldon-core-operator \
  --repo https://storage.googleapis.com/seldon-charts \
  --set usageMetrics.enabled=true \
  --namespace seldon-system \
  --create-namespace
```

**SeldonDeployment básico**

```yaml
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: fraud-detector
spec:
  predictors:
  - name: default
    replicas: 2
    graph:
      name: fraud-model
      type: MODEL
      endpoint:
        type: REST
    componentSpecs:
    - spec:
        containers:
        - name: fraud-model
          image: my-registry/fraud-model:v1.2.0
          resources:
            requests:
              memory: "1Gi"
              cpu: "500m"
```

**Combiners y routers para pipelines de modelos**

Seldon Core permite definir grafos de inferencia donde la salida de un modelo alimenta la entrada de otro. Los **combiners** agregan las predicciones de múltiples modelos en paralelo, siendo útiles para ensembles (por ejemplo, combinar un modelo de gradient boosting con una red neuronal):

```yaml
graph:
  name: ensemble-combiner
  type: COMBINER
  children:
  - name: model-gbm
    type: MODEL
  - name: model-neural
    type: MODEL
```

Los **routers** dirigen el tráfico condicionalmente entre modelos según algún criterio, siendo útiles para A/B testing estático o bandit algorithms que aprenden a redirigir tráfico hacia el modelo de mejor rendimiento de forma dinámica:

```yaml
graph:
  name: ab-router
  type: ROUTER
  children:
  - name: model-a
    type: MODEL
  - name: model-b
    type: MODEL
```

### 4.3 BentoML en Kubernetes

BentoML es un framework de serving centrado en la experiencia del desarrollador que permite definir el servicio de inferencia en Python con decoradores, empaquetarlo como una imagen Docker autogenerada (llamada "Bento") y desplegarlo en Kubernetes mediante el componente Yatai.

La instalación en Kubernetes se realiza mediante el Helm chart oficial:

```bash
helm repo add bentoml https://bentoml.github.io/helm-charts
helm install yatai bentoml/yatai \
  --namespace yatai \
  --create-namespace
```

Yatai es el componente de gestión de BentoML para Kubernetes. Proporciona una interfaz web para registrar Bentos, construir imágenes automáticamente en el clúster y desplegar `BentoDeployment` CRDs. Su ventaja principal es que reduce la fricción para data scientists que prefieren trabajar en Python sin necesidad de conocer en profundidad la API de Kubernetes.

### 4.4 Comparativa KServe vs Seldon Core vs BentoML

| Criterio | KServe | Seldon Core | BentoML |
|---|---|---|---|
| **Frameworks soportados nativamente** | sklearn, PyTorch, TF, XGBoost, ONNX, HuggingFace | sklearn, PyTorch, TF, XGBoost | Agnóstico (cualquier código Python) |
| **Pipelines de modelos** | Limitado (mediante transformers) | Excelente (combiners, routers, graphs) | No nativo en K8s |
| **Escalado a cero** | Sí (Knative) | No nativo | Sí (con KEDA) |
| **Dependencias** | Knative + Istio (pesado) | Istio (o Ambassador) | Menor overhead |
| **Experiencia del desarrollador** | Orientado a plataforma | Orientado a plataforma | Orientado al desarrollador |
| **Madurez** | Alta (proyecto CNCF) | Alta | Alta |
| **Canary rollouts** | Nativo declarativo | Con Istio/Ambassador | Manual |
| **Protocolo estándar** | V2 (Open Inference Protocol) | REST/gRPC propio | REST/gRPC |

---

## 5. Containerización avanzada para ML

### 5.1 Mejores prácticas de Dockerfile para ML

La construcción de imágenes Docker para cargas de trabajo ML presenta desafíos específicos: dependencias con compilación nativa (NumPy, PyTorch), modelos de gran tamaño, necesidad de drivers NVIDIA para inferencia GPU, y tiempos de build elevados que impactan directamente en la velocidad del ciclo de desarrollo.

**Multi-stage build**

El multi-stage build permite separar el entorno de construcción del entorno de ejecución, reduciendo el tamaño final de la imagen y eliminando herramientas de compilación que no son necesarias en runtime:

```dockerfile
# Etapa de construcción: instala dependencias con todos los compiladores disponibles
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Etapa de ejecución: imagen limpia sin compiladores ni caché de pip
FROM python:3.11-slim AS runtime
WORKDIR /app
# Copiar solo las dependencias instaladas, no el entorno de build completo
COPY --from=builder /root/.local /root/.local
COPY src/ ./src/
COPY models/ ./models/

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

USER nobody
CMD ["python", "-m", "src.serve"]
```

**Usuario no-root**

Ejecutar el proceso principal como root dentro del contenedor es un riesgo de seguridad. Si el proceso es comprometido, el atacante tiene privilegios de root dentro del contenedor, lo que facilita técnicas de escape. La instrucción `USER nobody` (o un usuario creado con `adduser`) reduce el radio de impacto en caso de compromiso.

**.dockerignore**

Un `.dockerignore` bien configurado evita que archivos innecesarios entren en el contexto de build, acelerando los builds y evitando la inclusión accidental de credenciales, datasets voluminosos o checkpoints de entrenamiento:

```
.git/
.env
*.pyc
__pycache__/
.pytest_cache/
experiments/
data/raw/
notebooks/
*.ipynb
.venv/
```

**Cacheo de capas de dependencias**

El cacheo de capas es crítico para la velocidad de los builds en CI. La regla fundamental es ordenar las instrucciones de más estable a menos estable. Si el código cambia pero las dependencias no, Docker debe poder reutilizar las capas cacheadas de instalación de dependencias.

```dockerfile
# Correcto: pip solo se re-ejecuta si requirements.txt cambia
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/

# Incorrecto: cualquier cambio en el código invalida el cache de pip
COPY . .
RUN pip install -r requirements.txt
```

### 5.2 Optimización de tamaño de imagen

**Imágenes base slim**

Las imágenes `python:3.11-slim` eliminan paquetes del sistema operativo innecesarios en comparación con `python:3.11`. Para la mayoría de los workloads de inferencia ML, `python:3.11-slim` es el punto de partida correcto.

Para cargas de trabajo con GPU, las imágenes NVIDIA `nvcr.io/nvidia/cuda:12.x-cudnn8-runtime-ubuntu22.04` están disponibles en variante `runtime` (más ligera, solo lo necesario para ejecutar aplicaciones CUDA) y `devel` (con compiladores, solo necesaria para compilar extensiones C++). Siempre se debe usar la variante `runtime` en imágenes de producción.

**Squashing de capas**

Docker permite fusionar todas las capas de una imagen en una sola. Esto elimina artefactos temporales de capas intermedias que no eliminan archivos explícitamente. La forma más portable de conseguir este efecto sin flags experimentales es encadenar comandos `RUN` con `&&` y limpiar en el mismo layer:

```dockerfile
RUN apt-get update \
  && apt-get install -y --no-install-recommends libgomp1 \
  && rm -rf /var/lib/apt/lists/*
```

### 5.3 Registro de contenedores

| Registro | Proveedor | Características destacadas |
|---|---|---|
| **Docker Hub** | Docker Inc. | Público, cuota de pulls anónimos en free tier, integración universal |
| **ECR (Elastic Container Registry)** | AWS | IAM-native, escaneo con Inspector, lifecycle policies |
| **GCR / Artifact Registry** | GCP | Integrado con GKE, soporte multi-formato (OCI, npm, Maven) |
| **Harbor** | CNCF (self-hosted) | RBAC completo, replicación entre registros, escaneo integrado con Trivy, firma de imágenes |

Para entornos on-premise o con restricciones de privacidad de datos, Harbor es la solución self-hosted más completa. Soporta replicación hacia registros cloud, control de acceso granular por proyecto y namespace, y políticas de retención de imágenes.

### 5.4 Image signing y verificación con Cosign (Sigstore)

Cosign es la herramienta del proyecto Sigstore para firmar y verificar imágenes de contenedores. Permite establecer una cadena de confianza desde el build hasta el despliegue, garantizando que la imagen en producción es exactamente la que fue construída y auditada en CI.

**Generación de claves y firma**

```bash
# Generar par de claves (en CI corporativo se gestiona de forma segura)
cosign generate-key-pair

# Firmar la imagen referenciando la clave privada
cosign sign --key cosign.key my-registry/fraud-model:v1.2.0

# Verificar la firma con la clave pública
cosign verify --key cosign.pub my-registry/fraud-model:v1.2.0
```

**Keyless signing**

En pipelines de CI modernos (GitHub Actions, GitLab CI) es preferible el "keyless signing", donde la identidad del firmante se vincula al OIDC token del pipeline, eliminando la necesidad de gestionar claves privadas:

```bash
# En GitHub Actions, con OIDC habilitado en el workflow
cosign sign --yes my-registry/fraud-model:v1.2.0
```

La firma se almacena en el registro de transparencia de Sigstore (Rekor), creando un registro auditable de todos los artefactos firmados. Cualquier firma puede verificarse públicamente consultando el log de Rekor.

**Verificación en Kubernetes con Policy Controller**

Sigstore Policy Controller permite configurar políticas a nivel de clúster que impiden desplegar imágenes no firmadas, rechazando el admission de pods cuya imagen no cumpla la política:

```yaml
apiVersion: policy.sigstore.dev/v1beta1
kind: ClusterImagePolicy
metadata:
  name: require-signed-images
spec:
  images:
  - glob: "my-registry/**"
  authorities:
  - keyless:
      url: https://fulcio.sigstore.dev
```

---

## 6. Helm charts para aplicaciones ML

### 6.1 Estructura de un chart de Helm

Helm es el gestor de paquetes para Kubernetes. Un chart de Helm es un directorio con una estructura predefinida que contiene templates de manifests de Kubernetes parametrizados y la configuración necesaria para instanciarlos:

```
inference-service/
├── Chart.yaml          # Metadatos del chart (nombre, versión, descripción)
├── values.yaml         # Valores por defecto
├── templates/          # Manifests de Kubernetes con templating
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   └── _helpers.tpl    # Funciones y plantillas auxiliares reutilizables
└── charts/             # Dependencias (subcharts)
```

El archivo `Chart.yaml` contiene los metadatos del chart:

```yaml
apiVersion: v2
name: inference-service
description: Helm chart para despliegue de servicios de inferencia ML
version: 1.0.0
appVersion: "1.0"
```

### 6.2 values.yaml para configuración de modelos

El archivo `values.yaml` centraliza todos los parámetros configurables del chart. Un values.yaml bien diseñado permite reutilizar el mismo chart para distintos modelos y entornos sin modificar los templates:

```yaml
replicaCount: 2

image:
  repository: my-registry/fraud-model
  tag: "v1.2.0"
  pullPolicy: IfNotPresent

model:
  name: fraud-detector
  version: "1.2.0"
  framework: sklearn
  storageUri: "s3://ml-models/fraud/v1.2.0/"

resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"

gpu:
  enabled: false
  count: 0

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

ingress:
  enabled: true
  host: "fraud-model.internal.example.com"
```

### 6.3 Templating con `{{ .Values }}`

Los templates de Helm utilizan la sintaxis de Go templates con el prefijo `{{ .Values }}` para referenciar los valores del chart. El archivo `_helpers.tpl` define funciones reutilizables que evitan la repetición en los templates:

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "inference-service.fullname" . }}
  labels:
    {{- include "inference-service.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "inference-service.selectorLabels" . | nindent 6 }}
  template:
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
        {{- if .Values.gpu.enabled }}
        env:
        - name: NVIDIA_VISIBLE_DEVICES
          value: "all"
        {{- end }}
```

La directiva `{{- if .Values.gpu.enabled }}` permite incluir o excluir bloques completos del manifest según los valores, haciendo el chart flexible sin duplicar código.

### 6.4 Chart repositories y Helmfile para gestión de múltiples releases

Los charts se publican en repositorios HTTP o en registros OCI. Para repositorios privados se utilizan soluciones como Harbor (con soporte de Helm charts OCI), ChartMuseum o el soporte nativo OCI en registros de contenedores modernos.

**Helmfile** es una herramienta declarativa para gestionar múltiples releases de Helm en un mismo clúster. En lugar de ejecutar `helm install` manualmente para cada chart, se define un archivo `helmfile.yaml`:

```yaml
# helmfile.yaml
releases:
- name: fraud-model
  chart: ./charts/inference-service
  namespace: production
  values:
  - environments/production/fraud-model-values.yaml

- name: churn-model
  chart: ./charts/inference-service
  namespace: production
  values:
  - environments/production/churn-model-values.yaml

- name: monitoring
  chart: prometheus-community/kube-prometheus-stack
  version: "56.0.0"
  namespace: monitoring
```

```bash
helmfile sync    # Instala o actualiza todos los releases declarados
helmfile diff    # Muestra diferencias sin aplicar cambios
helmfile destroy # Elimina todos los releases
```

### 6.5 Ejemplo completo de Helm chart para servicio de inferencia con GPU

Para un servicio de inferencia que requiere GPU (por ejemplo, un modelo de embeddings de texto basado en transformers), el chart debe configurar los resource requests de GPU, el `nodeSelector` que dirige los pods a nodos con aceleradores, y las tolerations para los taints de nodos GPU:

```yaml
# values.yaml para modelo con GPU
replicaCount: 1

gpu:
  enabled: true
  count: 1
  runtimeClass: "nvidia"

resources:
  requests:
    memory: "8Gi"
    cpu: "2000m"
    nvidia.com/gpu: 1
  limits:
    memory: "16Gi"
    cpu: "4000m"
    nvidia.com/gpu: 1

nodeSelector:
  accelerator: nvidia-tesla-a10g

tolerations:
- key: "nvidia.com/gpu"
  operator: "Exists"
  effect: "NoSchedule"
```

En el template del Deployment, los bloques condicionales y la serialización YAML nativa de Helm gestionan la configuración de nodo de forma limpia:

```yaml
{{- if .Values.gpu.enabled }}
runtimeClassName: {{ .Values.gpu.runtimeClass }}
{{- end }}
{{- with .Values.nodeSelector }}
nodeSelector:
  {{- toYaml . | nindent 8 }}
{{- end }}
{{- with .Values.tolerations }}
tolerations:
  {{- toYaml . | nindent 8 }}
{{- end }}
```

---

## 7. Gestión de dependencias en producción

### 7.1 Pinning de versiones: por qué no usar `latest`

El tag `latest` en imágenes Docker y el operador `>=` en especificaciones de paquetes Python son fuentes recurrentes de incidentes en producción. Su uso viola el principio fundamental de reproducibilidad: dos builds del mismo `Dockerfile` o `requirements.txt` en momentos distintos pueden producir resultados diferentes sin ningún cambio intencional en el código.

Las consecuencias prácticas son severas. Un modelo que funcionaba correctamente puede dejar de hacerlo después de que una dependencia actualice su API. Un bug introducido en una nueva versión de una librería puede manifestarse días después de que el artefacto fue construido, dificultando enormemente la identificación de la causa. La depuración se vuelve exponencialmente más difícil cuando no se puede reproducir el entorno exacto en el que ocurrió el fallo.

Las reglas de oro son:
- Siempre especificar la versión exacta de la imagen base en el Dockerfile: `FROM python:3.11.9-slim` en lugar de `FROM python:3-slim`.
- Siempre pinnar las dependencias Python con versión exacta: `scikit-learn==1.4.2` en lugar de `scikit-learn>=1.4`.
- En entornos críticos, referenciar imágenes por digest SHA256: `FROM python@sha256:abc123...` garantiza que no se descarga una imagen distinta aunque el tag sea reemplazado.

### 7.2 Lockfiles y reproducibilidad

Los lockfiles son la implementación práctica del pinning de versiones transitivo. Mientras que `requirements.txt` puede especificar solo las dependencias directas, un lockfile contiene el árbol completo de dependencias con sus versiones exactas y hashes de integridad, incluyendo todas las dependencias de las dependencias.

**pip-compile (pip-tools)**

```bash
pip install pip-tools

# Compilar el lockfile desde las dependencias directas
pip-compile requirements.in --generate-hashes --output-file requirements.txt

# Instalar exactamente lo que especifica el lockfile, verificando hashes
pip install --require-hashes -r requirements.txt
```

El archivo `requirements.in` contiene las dependencias directas sin versiones fijadas. `pip-compile` resuelve el árbol de dependencias y genera un `requirements.txt` con versiones exactas y hashes SHA256. Al instalar con `--require-hashes`, pip rechaza cualquier paquete cuyo hash no coincida, previniendo ataques de supply chain donde un paquete malicioso se sube bajo la misma versión.

**Poetry y uv**

Poetry genera un `poetry.lock` automáticamente en cada instalación o actualización. El gestor `uv` —una alternativa extremadamente rápida a pip escrita en Rust— genera un `uv.lock` con el mismo principio. Ambos son alternativas válidas para proyectos que adoptan un gestor de dependencias moderno.

### 7.3 SBOM (Software Bill of Materials) con Syft

Un SBOM es un inventario exhaustivo y formal de todos los componentes de software presentes en un artefacto: paquetes del sistema operativo, librerías de lenguaje, dependencias transitivas y sus versiones, junto con información de licencias. Es un requisito regulatorio emergente (Executive Order 14028 en EE.UU., Cyber Resilience Act en la UE) y un pre-requisito para el escaneo sistemático de vulnerabilidades.

**Syft** es la herramienta open source más utilizada para generar SBOM de imágenes de contenedores. Soporta los formatos estándar SPDX y CycloneDX:

```bash
# Instalar Syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh

# Generar SBOM en formato SPDX-JSON
syft my-registry/fraud-model:v1.2.0 -o spdx-json > fraud-model-sbom.spdx.json

# Generar en formato CycloneDX
syft my-registry/fraud-model:v1.2.0 -o cyclonedx-json > fraud-model-sbom.cdx.json
```

El SBOM resultante puede archivarse junto con la imagen (mediante `cosign attach sbom`) creando un registro inmutable, o almacenarse en un sistema de gestión de vulnerabilidades como Dependency-Track para análisis continuo.

### 7.4 Escaneo de vulnerabilidades en imágenes: Trivy y Grype

**Trivy**

Trivy es un escáner de vulnerabilidades open source de Aqua Security que analiza imágenes de contenedores, filesystems y repositorios de código. Integra múltiples bases de datos de vulnerabilidades: NVD, GitHub Advisory Database, Red Hat, Debian, Ubuntu y otras distribuciones. También detecta secretos embebidos accidentalmente en las imágenes.

```bash
# Escanear una imagen local
trivy image my-registry/fraud-model:v1.2.0

# Escanear solo vulnerabilidades críticas y altas, fallar el pipeline si se encuentran
trivy image --severity HIGH,CRITICAL \
  --exit-code 1 \
  my-registry/fraud-model:v1.2.0

# Output en formato SARIF para integración con GitHub Security tab
trivy image --format sarif \
  --output trivy-results.sarif \
  my-registry/fraud-model:v1.2.0
```

La integración del escaneo de vulnerabilidades en el pipeline de CI es la práctica recomendada: la imagen se escanea justo después de ser construida, y el pipeline falla si se detectan vulnerabilidades por encima del umbral configurado.

**Grype**

Grype (de Anchore) es una alternativa a Trivy diseñada para trabajar estrechamente con Syft. Puede recibir un SBOM generado por Syft como entrada en lugar de la imagen directamente, lo que acelera el escaneo en pipelines donde el SBOM ya se ha generado:

```bash
# Escanear directamente desde la imagen
grype my-registry/fraud-model:v1.2.0

# Escanear usando un SBOM previamente generado (más eficiente en CI)
grype sbom:fraud-model-sbom.spdx.json
```

**Integración en CI/CD con GitHub Actions**

```yaml
- name: Scan image with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: my-registry/fraud-model:${{ github.sha }}
    format: sarif
    output: trivy-results.sarif
    severity: CRITICAL,HIGH
    exit-code: 1

- name: Upload results to GitHub Security tab
  uses: github/codeql-action/upload-sarif@v2
  if: always()
  with:
    sarif_file: trivy-results.sarif
```

### 7.5 Actualización controlada de dependencias con Dependabot y Renovate

Pinar versiones de dependencias resuelve el problema de la indeterminismo, pero crea otro: las dependencias dejan de actualizarse automáticamente, acumulando deuda de seguridad. La solución es automatizar las actualizaciones de forma controlada mediante herramientas que abren Pull Requests automáticos cuando se publican nuevas versiones, permitiendo que el equipo las revise y apruebe.

**Dependabot** está integrado en GitHub y analiza los manifests de dependencias del repositorio:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    groups:
      ml-dependencies:
        patterns:
          - "torch*"
          - "scikit-learn"
          - "transformers"

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
```

**Renovate** es una alternativa más configurable que soporta mayor variedad de ecosistemas y ofrece características adicionales como el agrupamiento de actualizaciones, las ventanas de estabilización y el control granular de automerge:

```json
{
  "extends": ["config:recommended"],
  "stabilityDays": 3,
  "packageRules": [
    {
      "matchPackagePatterns": ["^torch", "^tensorflow"],
      "stabilityDays": 7,
      "automerge": false,
      "reviewersFromCodeOwners": true
    },
    {
      "matchPackagePatterns": ["^boto3", "^botocore"],
      "groupName": "AWS SDK",
      "automerge": true
    }
  ],
  "prConcurrentLimit": 5
}
```

Esta configuración retrasa la propuesta de actualizaciones de PyTorch y TensorFlow 7 días —para esperar a que la comunidad detecte posibles regressions— y requiere revisión manual de los code owners. Las actualizaciones del SDK de AWS, consideradas de menor riesgo, se automerge directamente.

---

## 8. Actividades prácticas

### Actividad 1: Despliegue de MLflow Tracking Server con Docker Compose

**Objetivo:** Instalar y configurar un MLflow Tracking Server completo con PostgreSQL como backend de metadatos y MinIO como artifact store, utilizando Docker Compose para orquestar los servicios.

**Descripción:** El estudiante debe crear un archivo `docker-compose.yml` que incluya tres servicios: PostgreSQL (versión 16), MinIO y el propio servidor de MLflow. La configuración debe incluir health checks que garanticen que MLflow no arranca hasta que PostgreSQL esté disponible y pasando sus propias comprobaciones de salud. Las credenciales de acceso a la base de datos y a MinIO deben gestionarse mediante variables de entorno definidas en un archivo `.env`, sin hardcoding en el Compose.

Una vez desplegado el stack, el estudiante debe ejecutar un script de entrenamiento Python que utilice la librería `mlflow` para registrar métricas (accuracy, precision, recall) y guardar el artefacto del modelo entrenado. La actividad se considera completada cuando el modelo aparece en la sección Model Registry de MLflow y sus artefactos binarios son accesibles en la interfaz de MinIO en el bucket configurado.

**Criterios de evaluación:** Correcta separación de responsabilidades entre servicios, health checks funcionales con dependencias correctas en el Compose, credenciales gestionadas por variables de entorno, experimento visible en la UI de MLflow con al menos tres métricas registradas, y artefacto del modelo visible en MinIO.

---

### Actividad 2: Construcción de imagen Docker optimizada para ML

**Objetivo:** Construir una imagen Docker para un servicio de inferencia aplicando las mejores prácticas de seguridad y optimización de tamaño, y demostrar el impacto de cada mejora con métricas cuantitativas.

**Descripción:** El estudiante parte de un `Dockerfile` de referencia con problemas intencionales: uso de `python:3.11` (imagen completa), ejecución como root, ausencia de `.dockerignore`, instalación de dependencias sin lockfile y capas de cacheo en orden incorrecto. La tarea consiste en identificar y corregir progresivamente cada problema, midiendo el tamaño de imagen en cada iteración. Los pasos son: (1) migrar a imagen base slim, (2) implementar un multi-stage build, (3) crear un `.dockerignore` apropiado, (4) reordenar las capas para optimizar el cacheo, y (5) añadir usuario no-root.

Finalmente, el estudiante debe generar el SBOM de la imagen optimizada con Syft y escanearla con Trivy, documentando las vulnerabilidades encontradas en un tabla con su severidad y la versión que las corrige.

**Criterios de evaluación:** Multi-stage build funcional, usuario no-root verificado con `docker inspect`, tamaño de imagen final reducido en al menos un 35% respecto al original, `.dockerignore` que excluye datos y entornos virtuales, SBOM generado en formato SPDX-JSON y reporte de Trivy sin vulnerabilidades críticas no justificadas.

---

### Actividad 3: Despliegue de un modelo con KServe en Minikube

**Objetivo:** Desplegar un modelo de clasificación utilizando KServe en un clúster local de Minikube y realizar inferencias a través del endpoint HTTP, incluyendo la configuración de un canary rollout.

**Descripción:** Partiendo de un modelo sklearn previamente entrenado y serializado, el estudiante debe: (1) configurar un bucket MinIO accesible desde dentro del clúster de Minikube y subir el modelo, (2) crear el namespace y las anotaciones de Istio necesarias para el serving, (3) redactar el manifiesto YAML de un `InferenceService` apuntando al modelo en MinIO con los recursos apropiados, (4) aplicar el manifiesto y monitorizar el despliegue hasta que el servicio alcance el estado `Ready`, y (5) realizar peticiones de inferencia utilizando el formato del protocolo V2 de KServe con curl y un script Python.

Como parte obligatoria, el estudiante debe además crear una segunda versión del modelo (re-entrenado con diferentes hiperparámetros), subirla al almacén de objetos y configurar un canary rollout al 30% apuntando a esta nueva versión, verificando con múltiples peticiones que ambas versiones responden.

**Criterios de evaluación:** Manifiesto YAML de `InferenceService` correcto y aplicado sin errores, estado `Ready` verificado con `kubectl get inferenceservice`, inferencia exitosa con el formato de payload V2, comprensión del flujo de logs de KServe documentada, y canary rollout configurado y verificado con al menos 10 peticiones de prueba.

---

### Actividad 4: Creación de un Helm chart para serving de modelos con Helmfile

**Objetivo:** Desarrollar un Helm chart reutilizable para despliegue de servicios de inferencia de ML y gestionar múltiples releases en distintos entornos mediante Helmfile.

**Descripción:** El estudiante debe crear desde cero un Helm chart llamado `ml-inference` que incluya: (1) un Deployment con soporte opcional para GPU mediante condicionales en los templates usando `{{ if .Values.gpu.enabled }}`, (2) un Service de tipo ClusterIP, (3) un HorizontalPodAutoscaler configurable con mínimo y máximo de réplicas y target de CPU, (4) un ConfigMap para parámetros de configuración del modelo, y (5) un `values.yaml` con valores por defecto razonables y documentados con comentarios.

El estudiante debe verificar el chart con `helm lint` y `helm template` antes de instalarlo. A continuación, debe crear tres conjuntos de values files (`dev-values.yaml`, `staging-values.yaml`, `prod-values.yaml`) con configuraciones diferenciadas para cada entorno en cuanto a número de réplicas, recursos de CPU/memoria y habilitación de escalado automático. Por último, debe gestionar el despliegue de los tres releases con un `helmfile.yaml` en namespaces separados, verificando con `kubectl` que los recursos de cada entorno tienen los valores esperados.

**Criterios de evaluación:** Templates de Helm correctos con uso adecuado de helpers en `_helpers.tpl` y condicionales sin errores de sintaxis, `helm lint` sin errores ni advertencias, values files con configuraciones significativamente diferenciadas por entorno, `helmfile.yaml` funcional que despliega los tres releases en namespaces separados, y verificación exitosa de los recursos creados con `kubectl get all -n <namespace>`.

---

## 9. Referencias

### Documentación oficial

- **KServe Documentation.** KServe — Serverless Inferencing on Kubernetes. Documentación oficial de KServe, incluyendo guías de instalación, referencia de CRDs, ejemplos de InferenceService para todos los frameworks soportados y protocolo V2 de inferencia.
  https://kserve.github.io/website/latest/

- **Seldon Core Documentation.** Seldon Core — An Open Source Platform to Deploy Machine Learning Models on Kubernetes at Massive Scale. Referencia completa del SeldonDeployment CRD, combiners, routers y guías de integración con Istio y Ambassador.
  https://docs.seldon.io/projects/seldon-core/en/latest/

- **MLflow Documentation.** MLflow: A Tool for Managing the Machine Learning Lifecycle. Documentación oficial de MLflow cubriendo tracking server, Model Registry, autenticación y serving básico.
  https://mlflow.org/docs/latest/index.html

- **Kubeflow Documentation.** Kubeflow — The Machine Learning Toolkit for Kubernetes. Documentación oficial de Kubeflow, incluyendo guías de instalación con manifests y Kustomize, y referencias de KFP, Katib y Training Operators.
  https://www.kubeflow.org/docs/

- **Helm Documentation.** Helm — The Package Manager for Kubernetes. Documentación oficial de Helm, incluyendo referencia de templating con Go templates, repositorios de charts, mejores prácticas y publicación de charts.
  https://helm.sh/docs/

- **Trivy Documentation.** Trivy — Vulnerability Scanner for Containers and other Artifacts. Referencia de Aqua Security para Trivy, incluyendo modos de escaneo, configuración en CI/CD, formatos de salida SARIF y JSON, y políticas de severidad.
  https://aquasecurity.github.io/trivy/latest/

- **Cosign / Sigstore Documentation.** Cosign — Container Signing, Verification and Storage in an OCI Registry. Guías de firma y verificación de imágenes con keyless signing, integración con Policy Controller y configuración de Rekor.
  https://docs.sigstore.dev/cosign/overview/

- **Syft Documentation.** Syft — CLI tool and Go library for generating a Software Bill of Materials (SBOM) from container images. Referencia de Anchore para generación de SBOMs en formatos SPDX y CycloneDX.
  https://github.com/anchore/syft

- **Grype Documentation.** Grype — A vulnerability scanner for container images and filesystems. Referencia del escáner de vulnerabilidades Grype de Anchore, con soporte para ingesta de SBOMs.
  https://github.com/anchore/grype

- **BentoML Documentation.** BentoML — The Unified Model Serving Framework. Documentación de BentoML y Yatai para el despliegue de servicios de inferencia en Kubernetes.
  https://docs.bentoml.com/

- **Helmfile Documentation.** Helmfile — Deploy Kubernetes Helm Charts. Referencia para la gestión declarativa de múltiples releases de Helm.
  https://helmfile.readthedocs.io/

### Libros y publicaciones

- Yuen, B., Herman, A., & Roth, J. (2021). *GitOps and Kubernetes: Continuous Deployment with Argo CD, Jenkins X, and Flux.* Manning Publications. ISBN: 978-1617297274. Referencia esencial para comprender los patrones de despliegue declarativo en Kubernetes, directamente aplicables a pipelines MLOps basados en GitOps.

- Flach, P., & Gift, N. (2022). *Practical MLOps: Operationalizing Machine Learning Models.* O'Reilly Media. ISBN: 978-1098103019. Cobertura práctica de las herramientas y prácticas para llevar modelos ML a producción de forma sostenible.

- Subramanian, S. (2023). *Kubernetes for Machine Learning.* Addison-Wesley Professional. Referencia especializada en la operación de cargas de trabajo ML sobre Kubernetes.

### Especificaciones y estándares

- **Open Inference Protocol (V2).** Especificación del protocolo estándar para inferencia de modelos en KServe y Triton Inference Server.
  https://kserve.github.io/website/latest/modelserving/data_plane/v2_protocol/

- **SPDX Specification.** System Package Data Exchange — Formato estándar ISO/IEC 5962:2021 para Software Bill of Materials.
  https://spdx.dev/specifications/

- **CycloneDX Specification.** CycloneDX — Lightweight Software Bill of Materials Standard orientado a la seguridad de la cadena de suministro de software.
  https://cyclonedx.org/specification/overview/
