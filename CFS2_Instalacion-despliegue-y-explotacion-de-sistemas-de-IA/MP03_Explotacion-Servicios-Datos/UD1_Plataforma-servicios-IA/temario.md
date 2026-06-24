# UD1 · Implementación de la plataforma de servicios de IA

---

## 1. Introducción

La madurez de un equipo de inteligencia artificial no se mide únicamente por la calidad de sus modelos, sino por su capacidad para llevarlos a producción de forma repetible, trazable y eficiente. Esta capacidad es la que la disciplina de **MLOps** (Machine Learning Operations) intenta sistematizar, y su manifestación técnica más concreta es la **plataforma de servicios de IA**: el conjunto integrado de herramientas, servicios y procesos que permiten a los equipos de datos entrenar, evaluar, registrar, desplegar, servir y monitorizar modelos en producción con el mismo rigor y control que la ingeniería de software aplica al código de aplicaciones.

Sin una plataforma centralizada, los equipos de IA trabajan en silos: los data scientists entrenan modelos en notebooks locales, los ingenieros de datos construyen pipelines independientes, y los equipos de operaciones despliegan modelos mediante procesos manuales y frágiles. El resultado es predecible: modelos que funcionan en el cuaderno pero fallan en producción, ausencia de trazabilidad sobre qué versión de qué modelo está sirviendo predicciones, imposibilidad de reentrenar o actualizar modelos con agilidad, y ausencia de visibilidad sobre el rendimiento real del sistema. La plataforma de servicios de IA resuelve estos problemas proporcionando una capa de abstracción e integración sobre toda la cadena de valor del modelo.

El stack de una plataforma de MLOps moderna se compone de varios componentes especializados con responsabilidades bien definidas. El **feature store** centraliza la definición, el cálculo y el almacenamiento de características, garantizando coherencia entre el entrenamiento y la inferencia. El **model registry** actúa como repositorio centralizado de modelos, con control de versiones y flujos de aprobación. La **serving layer** gestiona el despliegue y el escalado de los endpoints de inferencia. El sistema de **monitoring** detecta degradaciones en el rendimiento del modelo, desviaciones en la distribución de los datos de entrada y anomalías en las predicciones. La **orquestación de pipelines** automatiza los flujos de entrenamiento, evaluación y despliegue. Todos estos componentes deben integrarse de forma coherente y exponerse a los usuarios mediante interfaces que minimicen la fricción operativa.

La elección entre una plataforma gestionada en la nube —Vertex AI de Google, SageMaker de AWS, Azure ML— y una plataforma on-premise basada en Kubernetes con herramientas de código abierto como Kubeflow y MLflow no es trivial. Implica decisiones sobre costes, control de datos, latencia, soberanía de la información y capacidad técnica del equipo. Esta unidad proporciona los fundamentos técnicos para evaluar esas opciones y para implementar y administrar una plataforma de servicios de IA sobre Kubernetes, con especial atención al despliegue de APIs, la gestión de accesos y los acuerdos de nivel de servicio.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Describir los componentes principales del stack de MLOps (feature store, model registry, serving layer, monitoring, orquestación) y explicar la responsabilidad de cada componente en el ciclo de vida del modelo.
2. Comparar las plataformas MLOps líderes —Kubeflow, MLflow, Vertex AI y SageMaker— en términos de arquitectura, capacidades, modelo de despliegue y casos de uso recomendados.
3. Desplegar una plataforma MLOps básica sobre un clúster Kubernetes, configurando los namespaces, las cuentas de servicio y las políticas RBAC necesarias para el aislamiento entre equipos.
4. Exponer un servicio de inferencia de modelos a través de un API Gateway, configurando rutas, rate limiting, autenticación y logging.
5. Implementar los mecanismos de autenticación y autorización de APIs más habituales en servicios de IA —API keys, OAuth2 con client credentials flow— y describir sus diferencias de seguridad y casos de uso.
6. Definir un SLA técnico para un servicio de IA, identificando las métricas de disponibilidad, latencia y throughput que lo componen y los mecanismos de medición correspondientes.
7. Diseñar y ejecutar el proceso de onboarding de un equipo de datos a la plataforma, incluyendo la provisión de recursos, la configuración de accesos y la validación del entorno.
8. Identificar los principales riesgos de seguridad en la exposición de APIs de IA y las contramedidas técnicas correspondientes (autenticación, TLS, rate limiting, logging de auditoría).

---

## 3. Arquitectura del stack de MLOps

### 3.1 Componentes del stack y sus responsabilidades

Un stack de MLOps maduro se organiza en capas con responsabilidades bien delimitadas. La siguiente tabla resume los componentes principales y sus funciones:

| Componente | Función principal | Ejemplos de herramientas |
|---|---|---|
| Feature store | Definición, cálculo, almacenamiento y serving de características | Feast, Tecton, Hopsworks, SageMaker Feature Store |
| Experiment tracking | Registro de experimentos, parámetros, métricas y artefactos | MLflow Tracking, Weights & Biases, ClearML |
| Model registry | Almacenamiento y versionado de modelos, gestión del ciclo de vida | MLflow Registry, Vertex AI Model Registry, SageMaker Model Registry |
| Pipeline orchestration | Automatización de flujos de entrenamiento y despliegue | Kubeflow Pipelines, Apache Airflow, Prefect, ZenML |
| Serving layer | Despliegue y escalado de endpoints de inferencia | KServe, Seldon Core, BentoML, Triton Inference Server |
| Monitoring | Detección de drift, métricas de rendimiento, alertas | Evidently AI, WhyLabs, Prometheus + Grafana |
| Data versioning | Control de versiones de datasets y artefactos de datos | DVC, LakeFS, Delta Lake |
| API Gateway | Routing, autenticación, rate limiting, logging de APIs | Kong, Traefik, AWS API Gateway, Google Apigee |

### 3.2 Feature store: coherencia entre entrenamiento e inferencia

El **feature store** resuelve uno de los problemas más comunes en sistemas de ML en producción: la disparidad entre las características calculadas en el momento del entrenamiento y las calculadas en el momento de la inferencia (training-serving skew). Esta disparidad puede surgir porque el código de transformación se duplica, porque los datos disponibles en producción difieren de los de entrenamiento, o porque los cálculos de ventanas temporales se implementan de forma diferente.

Un feature store centraliza la lógica de transformación en **feature definitions** escritas una sola vez y ejecutadas tanto en la generación del dataset de entrenamiento como en la ruta de inferencia. Los datos históricos se almacenan en un **offline store** (típicamente un data warehouse o lago de datos) y los valores actuales se sirven desde un **online store** de baja latencia (Redis, DynamoDB, BigTable).

**Feast** es el feature store de código abierto más utilizado. Su arquitectura comprende:

```yaml
# feast/feature_store.yaml
project: churn_prediction
registry: data/registry.db
provider: local
online_store:
  type: redis
  connection_string: "redis:6379"
offline_store:
  type: bigquery
  dataset: feast_offline
```

La definición de features se realiza mediante objetos Python:

```python
from feast import FeatureView, Field, Entity
from feast.types import Float64, Int64

cliente = Entity(name="cliente_id", value_type=Int64)

historial_features = FeatureView(
    name="historial_cliente",
    entities=[cliente],
    ttl=timedelta(days=7),
    schema=[
        Field(name="num_transacciones_30d", dtype=Int64),
        Field(name="importe_medio_30d", dtype=Float64),
        Field(name="dias_sin_actividad", dtype=Int64),
    ],
    source=bigquery_source,
)
```

### 3.3 Model registry y ciclo de vida del modelo

El **model registry** es el sistema de control de versiones de los modelos. A diferencia de un simple almacenamiento de artefactos, el registry gestiona el ciclo de vida del modelo: experimento → staging → producción → archivado, con transiciones de estado controladas y auditables.

**MLflow Model Registry** organiza los modelos en torno a tres conceptos:

- **Registered Model**: una entidad con nombre que agrupa todas las versiones de un modelo bajo un nombre semántico (ej: `churn_predictor`).
- **Model Version**: cada versión individual con sus metadatos, métricas de evaluación y artefacto.
- **Stage**: el estado del ciclo de vida de cada versión (None, Staging, Production, Archived).

Las transiciones de stage se realizan mediante la UI o la API:

```python
import mlflow

client = mlflow.tracking.MlflowClient()

# Transición a Production con comentario
client.transition_model_version_stage(
    name="churn_predictor",
    version=7,
    stage="Production",
    archive_existing_versions=True,
)

# Añadir anotación de aprobación
client.set_model_version_tag(
    name="churn_predictor",
    version=7,
    key="aprobado_por",
    value="jefe.modelos@empresa.com"
)
```

---

## 4. Comparativa de plataformas MLOps

### 4.1 Kubeflow

**Kubeflow** es la plataforma MLOps de referencia para entornos Kubernetes on-premise o en nube. Es un proyecto de la CNCF (Cloud Native Computing Foundation) que empaqueta herramientas de código abierto en un stack cohesivo. Sus componentes principales son:

- **Kubeflow Pipelines (KFP)**: orquestador de pipelines ML basado en Argo Workflows. Cada paso del pipeline se ejecuta en un contenedor independiente.
- **Kubeflow Notebooks**: servidor de notebooks Jupyter gestionado, con perfiles de recursos configurables.
- **KServe** (antes KFServing): plataforma de serving de modelos sobre Kubernetes, con soporte para múltiples frameworks (sklearn, TensorFlow, PyTorch, XGBoost, ONNX).
- **Katib**: hyperparameter tuning automatizado con múltiples algoritmos (grid search, bayesian optimization, NAS).
- **Training Operator**: gestión de jobs de entrenamiento distribuido (TFJob, PyTorchJob, MXNetJob).

Kubeflow es la opción preferida cuando se requiere control total sobre la infraestructura, portabilidad entre nubes y cumplimiento de normativas de soberanía de datos.

### 4.2 MLflow

**MLflow** es una plataforma de código abierto centrada en el ciclo de vida del modelo, especialmente en la parte de experiment tracking y registry. A diferencia de Kubeflow, no es una plataforma integral: es un conjunto de componentes que se integran en el stack existente. Sus componentes son:

- **MLflow Tracking**: API para registrar parámetros, métricas y artefactos de experimentos.
- **MLflow Projects**: formato de empaquetado reproducible de proyectos ML.
- **MLflow Models**: formato de empaquetado y serving de modelos.
- **MLflow Registry**: sistema de registro y ciclo de vida de modelos.

MLflow tiene una API Python simple que facilita su adopción incremental y es agnóstico al framework de ML, lo que lo convierte en el complemento ideal de Kubeflow.

### 4.3 Vertex AI

**Vertex AI** es la plataforma MLOps gestionada de Google Cloud. Integra en un servicio único: pipelines de entrenamiento, AutoML, model registry, serving (con online y batch prediction), feature store, monitoring y experiment tracking. Su ventaja principal es la gestión de infraestructura completamente delegada, sin necesidad de administrar Kubernetes. Sus desventajas son el vendor lock-in con GCP y los costes variables difíciles de predecir en cargas de trabajo intensivas.

### 4.4 Amazon SageMaker

**Amazon SageMaker** es la plataforma MLOps de AWS. Ofrece capacidades equivalentes a Vertex AI: Studio (IDE integrado), Pipelines (orquestación), Feature Store, Model Registry, Endpoints (serving), Model Monitor y Clarify (bias/explainability). SageMaker tiene mayor cuota de mercado en empresas con infraestructura ya migrada a AWS, pero presenta la misma dependencia de proveedor que Vertex AI.

### 4.5 Tabla comparativa

| Dimensión | Kubeflow | MLflow | Vertex AI | SageMaker |
|---|---|---|---|---|
| Modelo de despliegue | On-premise / multi-cloud | Híbrido (servidor propio o cloud) | Cloud (GCP) | Cloud (AWS) |
| Vendor lock-in | Ninguno | Ninguno | Alto (GCP) | Alto (AWS) |
| Complejidad operativa | Alta | Baja-media | Baja | Baja |
| Coste | Infraestructura propia | Open source + cómputo | Por uso (variable) | Por uso (variable) |
| Serving integrado | KServe | MLflow Serving / terceros | Vertex Endpoints | SageMaker Endpoints |
| Feature store | Feast (externo) | No integrado | Vertex Feature Store | SageMaker Feature Store |
| Idóneo para | Grandes orgs., soberanía datos | Equipos pequeños, adopción incremental | GCP-first, sin ops | AWS-first, sin ops |

---

## 5. Despliegue on-premise con Kubernetes

### 5.1 Namespaces y aislamiento de equipos

En un clúster Kubernetes compartido por múltiples equipos de datos, la organización en **namespaces** es el mecanismo principal de aislamiento lógico. Cada equipo o proyecto de IA debe operar en su propio namespace, lo que permite aplicar políticas de recursos, redes y acceso de forma independiente.

```bash
# Crear namespaces para equipos de datos
kubectl create namespace equipo-credito
kubectl create namespace equipo-fraude
kubectl create namespace mlflow-system
kubectl create namespace kubeflow

# Asignar cuotas de recursos por namespace
kubectl apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: quota-equipo-credito
  namespace: equipo-credito
spec:
  hard:
    requests.cpu: "32"
    requests.memory: "128Gi"
    requests.nvidia.com/gpu: "4"
    limits.cpu: "64"
    limits.memory: "256Gi"
EOF
```

### 5.2 RBAC para equipos de datos

El **control de acceso basado en roles (RBAC)** en Kubernetes permite definir qué operaciones puede realizar cada usuario o grupo sobre qué recursos en qué namespaces. En el contexto de una plataforma de servicios de IA, los roles típicos son:

- **ml-engineer**: puede crear y gestionar pipelines, modelos y endpoints en su namespace.
- **data-scientist**: puede crear notebooks y experimentos, pero no desplegar en producción.
- **platform-admin**: puede gestionar toda la plataforma, incluyendo namespaces y quotas.
- **viewer**: acceso de solo lectura para auditoría y monitorización.

```yaml
# Definición de rol para ml-engineer en namespace equipo-credito
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: equipo-credito
  name: ml-engineer
rules:
- apiGroups: ["serving.kserve.io"]
  resources: ["inferenceservices"]
  verbs: ["get", "list", "create", "update", "delete"]
- apiGroups: ["kubeflow.org"]
  resources: ["pipelines", "pipelineruns"]
  verbs: ["get", "list", "create"]
- apiGroups: [""]
  resources: ["pods", "pods/log", "services"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ml-engineers-binding
  namespace: equipo-credito
subjects:
- kind: Group
  name: "equipo-credito-engineers"
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: ml-engineer
  apiGroup: rbac.authorization.k8s.io
```

### 5.3 Despliegue de KServe para serving de modelos

**KServe** permite desplegar modelos entrenados con cualquier framework como microservicios Kubernetes con un mínimo de configuración:

```yaml
# InferenceService para modelo de churn (sklearn)
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: churn-predictor-v2
  namespace: equipo-credito
spec:
  predictor:
    sklearn:
      storageUri: "s3://modelos/churn/v2/model.joblib"
      resources:
        requests:
          cpu: "2"
          memory: "4Gi"
        limits:
          cpu: "4"
          memory: "8Gi"
      autoscaling:
        minReplicas: 2
        maxReplicas: 10
        metrics:
        - type: Pods
          pods:
            metric:
              name: http_requests_per_second
            target:
              type: AverageValue
              averageValue: 100
```

---

## 6. Exposición de servicios de IA mediante API Gateway

### 6.1 Arquitectura de API Gateway para servicios de IA

La exposición directa de los endpoints de KServe o de cualquier serving framework al exterior no es recomendable por razones de seguridad y operaciones. El **API Gateway** actúa como punto de entrada único que centraliza: routing a los servicios internos, autenticación y autorización, rate limiting, transformación de peticiones/respuestas, logging de auditoría, y gestión de versiones de API.

**Kong** es el API Gateway de código abierto más utilizado en entornos Kubernetes. Se despliega como un ingress controller que intercepta el tráfico hacia los servicios de IA:

```bash
# Instalación de Kong con Helm
helm repo add kong https://charts.konghq.com
helm install kong kong/ingress -n kong --create-namespace \
  --set controller.ingressController.enabled=true
```

La configuración de una ruta para el servicio de scoring de crédito:

```yaml
apiVersion: configuration.konghq.com/v1
kind: KongIngress
metadata:
  name: credit-scoring-route
spec:
  route:
    strip_path: true
    preserve_host: false
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: credit-scoring-ingress
  annotations:
    konghq.com/strip-path: "true"
    konghq.com/plugins: "credit-scoring-rate-limit,credit-scoring-auth"
spec:
  ingressClassName: kong
  rules:
  - host: api.ia.empresa.com
    http:
      paths:
      - path: /v1/credit-scoring
        pathType: Prefix
        backend:
          service:
            name: churn-predictor-v2
            port:
              number: 80
```

### 6.2 Rate limiting

El **rate limiting** protege los servicios de IA de sobrecargas accidentales o ataques de denegación de servicio. En el contexto de servicios de inferencia, el rate limiting tiene además una dimensión de costes: cada petición de inferencia consume recursos de cómputo.

```yaml
# Plugin de rate limiting en Kong
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: credit-scoring-rate-limit
plugin: rate-limiting
config:
  minute: 60          # 60 peticiones por minuto por consumidor
  hour: 1000          # 1000 peticiones por hora
  policy: redis       # contadores en Redis para múltiples instancias
  redis_host: redis-service
  redis_port: 6379
  fault_tolerant: true
  hide_client_headers: false
```

---

## 7. Autenticación y autorización de APIs

### 7.1 API Keys

Las **API keys** son el mecanismo de autenticación más simple: una cadena opaca que identifica al consumidor y que se incluye en cada petición. Son adecuadas para accesos máquina a máquina (M2M) en contextos de confianza media-alta, como el acceso de una aplicación interna a un servicio de IA.

En Kong, la gestión de API keys se realiza mediante el plugin Key Authentication:

```yaml
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: credit-scoring-auth
plugin: key-auth
config:
  key_names: ["X-API-Key"]
  hide_credentials: true
```

La creación y asignación de keys a consumidores:

```bash
# Crear consumidor
kubectl apply -f - <<EOF
apiVersion: configuration.konghq.com/v1
kind: KongConsumer
metadata:
  name: aplicacion-creditos
  annotations:
    kubernetes.io/ingress.class: kong
username: aplicacion-creditos
EOF

# Crear API key para el consumidor
kubectl create secret generic aplicacion-creditos-key \
  --from-literal=kongCredType=key-auth \
  --from-literal=key=sk_prod_a7f3d9e2b1c4...
```

### 7.2 OAuth2 con client credentials flow

El **OAuth2 client credentials flow** es el mecanismo recomendado para autenticación M2M en entornos donde se requiere mayor seguridad: los tokens tienen tiempo de expiración, se pueden revocar y permiten la emisión de scopes que limitan el acceso.

El flujo es el siguiente:

```
Aplicación → POST /oauth2/token
             (client_id, client_secret, grant_type=client_credentials, scope=predict)
             → Authorization Server (ej: Keycloak)
             → access_token (JWT, TTL: 1h)

Aplicación → POST /v1/credit-scoring/predict
             Authorization: Bearer <access_token>
             → API Gateway (Kong) → validación JWT → KServe
```

La validación del JWT en Kong se realiza mediante el plugin JWT o, preferiblemente, mediante integración con OIDC (OpenID Connect) y un servidor de autorización como **Keycloak**:

```yaml
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: oidc-auth
plugin: openid-connect
config:
  issuer: "https://keycloak.empresa.com/realms/ia-platform"
  client_id: "kong-api-gateway"
  client_secret: "..."
  scopes: ["openid", "predict"]
  verify_parameters: ["sub", "scope"]
```

### 7.3 Comparativa de mecanismos de autenticación

| Mecanismo | Revocación | TTL | Scopes | Complejidad | Caso de uso |
|---|---|---|---|---|---|
| API Key | Manual (eliminar key) | Sin expiración | No nativo | Baja | Integración simple M2M interna |
| JWT estático | No (sin servidor) | Configurable | Sí (claims) | Media | APIs con claims predefinidos |
| OAuth2 client credentials | Sí (revocar token) | Corto (1h típico) | Sí | Media-alta | M2M con requisitos de seguridad |
| mTLS | Revocar certificado | Caducidad cert. | No nativo | Alta | Máxima seguridad, entornos críticos |

---

## 8. SLA para servicios de IA y onboarding de equipos

### 8.1 Definición de SLA para servicios de inferencia

Un **SLA (Service Level Agreement)** para un servicio de IA define las métricas de nivel de servicio comprometidas con los consumidores del API. Las métricas más relevantes en servicios de inferencia son:

- **Disponibilidad**: porcentaje del tiempo en que el servicio está operativo y respondiendo correctamente. Se expresa típicamente como porcentaje mensual (99.9% = ~43 min de downtime/mes).
- **Latencia P99**: percentil 99 de la latencia de respuesta. Para servicios de scoring en tiempo real, un P99 < 200 ms es un objetivo habitual. La latencia P99 es más relevante que la media porque refleja la experiencia del caso peor.
- **Throughput**: número de peticiones por segundo (RPS) que el servicio puede atender manteniendo el SLA de latencia.
- **Tasa de error**: porcentaje de peticiones que devuelven un error (5xx). Objetivo típico: < 0.1%.

El SLA debe incluir también las **condiciones de exclusión**: mantenimientos programados, degradaciones causadas por el consumidor (requests malformadas), y eventos fuera de control (fuerza mayor).

```yaml
# Ejemplo de SLA técnico documentado
sla:
  servicio: credit-scoring-api
  version: v2
  efectivo_desde: 2025-01-01
  metricas:
    disponibilidad:
      objetivo: 99.9%
      ventana_medicion: mensual
    latencia:
      p50: "< 50ms"
      p95: "< 120ms"
      p99: "< 200ms"
    throughput_maximo_garantizado: 200 RPS
    tasa_error_maxima: 0.1%
  exclusiones:
    - mantenimiento_programado_semanal: "domingos 02:00-04:00 UTC"
    - errores_4xx_por_consumidor: excluidos
```

### 8.2 Proceso de onboarding de equipos

El onboarding de un nuevo equipo de datos a la plataforma de MLOps sigue un proceso estructurado que garantiza que el equipo dispone de todos los recursos necesarios desde el primer día y que la plataforma mantiene su seguridad y orden:

**Paso 1 — Solicitud y aprobación**: el responsable del equipo solicita acceso a la plataforma mediante el sistema de ticketing. La solicitud incluye: nombre del equipo, número estimado de usuarios, recursos necesarios (GPU, RAM, almacenamiento), proyecto y duración estimada.

**Paso 2 — Provisión de namespace y recursos**:
```bash
# Crear namespace
kubectl create namespace equipo-nuevo

# Aplicar quotas y limit ranges
kubectl apply -f quotas/equipo-nuevo.yaml

# Crear service account para pipelines automatizados
kubectl create serviceaccount pipeline-runner -n equipo-nuevo
```

**Paso 3 — Configuración de RBAC y accesos**:
```bash
# Crear grupo en Keycloak y asignar usuarios
# Crear RoleBinding en Kubernetes
# Crear consumidor en Kong con API key inicial
```

**Paso 4 — Provisión de almacenamiento y secretos**:
```bash
# Crear bucket S3/MinIO para artefactos del equipo
aws s3 mb s3://mlops-equipo-nuevo --region eu-west-1

# Crear secreto con credenciales de acceso
kubectl create secret generic s3-credentials \
  --from-literal=AWS_ACCESS_KEY_ID=... \
  --from-literal=AWS_SECRET_ACCESS_KEY=... \
  -n equipo-nuevo
```

**Paso 5 — Sesión de validación**: el nuevo equipo ejecuta un pipeline de referencia (hello-world pipeline) que valida el correcto funcionamiento de todos los componentes de la plataforma en su namespace: creación de experimento en MLflow, ejecución de pipeline en KFP, registro de modelo, despliegue de InferenceService en KServe y consumo del endpoint mediante API Gateway.

---

## 9. Actividades prácticas

### Actividad 1 — Comparativa de plataformas MLOps

**Descripción**: Una empresa de seguros con 50.000 pólizas activas quiere implementar una plataforma MLOps para desplegar tres modelos en producción: scoring de riesgo, detección de fraude en siniestros y predicción de churn. La empresa tiene un equipo de tres data scientists y un ingeniero de plataforma. Tiene contrato con AWS pero también dispone de un pequeño clúster bare-metal de ocho nodos por razones de confidencialidad de datos. El estudiante debe analizar las opciones Kubeflow on-premise, MLflow + KServe on-premise, y SageMaker, y elaborar una recomendación justificada con un plan de implementación a tres meses.

**Entregable**: Informe de análisis comparativo y recomendación (3-4 páginas) con tabla comparativa y plan de implementación.

**Criterios de evaluación**: Rigor del análisis, adecuación de la recomendación al perfil de la empresa, consideración de los requisitos de confidencialidad de datos, realismo del plan de implementación.

---

### Actividad 2 — Despliegue de plataforma MLOps en Kubernetes

**Descripción**: Partiendo de un clúster Kubernetes de laboratorio proporcionado por el formador (tres nodos, sin GPU), el estudiante debe: instalar MLflow con backend de tracking en PostgreSQL y artefactos en MinIO, desplegar KServe con un InferenceService de prueba (modelo de iris de sklearn), configurar dos namespaces (`equipo-a` y `equipo-b`) con RBAC diferenciado, y verificar que un usuario del equipo-a no puede acceder a los recursos del equipo-b.

**Entregable**: Capturas de pantalla del entorno desplegado + ficheros YAML de configuración comentados.

**Criterios de evaluación**: Correcto despliegue de los componentes, corrección de la configuración RBAC, funcionamiento del InferenceService de prueba, calidad de los comentarios en los ficheros de configuración.

---

### Actividad 3 — Configuración de API Gateway con autenticación

**Descripción**: Sobre el entorno del ejercicio anterior, el estudiante debe exponer el InferenceService de prueba a través de Kong API Gateway, configurando: rate limiting de 30 peticiones por minuto, autenticación por API key para el consumidor `aplicacion-test`, y logging de todas las peticiones (incluyendo consumer y timestamp) en un fichero rotatorio. Adicionalmente, debe simular la generación de un token OAuth2 con Keycloak (instalado en el laboratorio) y proteger un segundo endpoint con validación OIDC.

**Entregable**: Ficheros de configuración de Kong + capturas de pantalla de las pruebas de autenticación y rate limiting (con curl).

**Criterios de evaluación**: Correcto funcionamiento del rate limiting, autenticación por API key operativa, logging correcto, validación OIDC funcional para el segundo endpoint.

---

### Actividad 4 — Diseño de SLA y proceso de onboarding

**Descripción**: El equipo de datos de una entidad bancaria va a incorporar a la plataforma MLOps existente un nuevo servicio de scoring de préstamos personales que debe estar disponible 24/7 para la aplicación móvil del banco. El estudiante debe: definir el SLA técnico completo del servicio (disponibilidad, latencia P50/P95/P99, throughput, tasa de error, exclusiones), diseñar el proceso de onboarding del equipo responsable del modelo (pasos, recursos a provisionar, checklist de validación), y elaborar el procedimiento de respuesta ante una degradación del SLA (escalado, comunicación, rollback).

**Entregable**: Documento de SLA (1 página) + procedimiento de onboarding (1-2 páginas) + runbook de respuesta a degradación (1 página).

**Criterios de evaluación**: Completitud y concreción del SLA, realismo del proceso de onboarding, practicidad del runbook de respuesta, coherencia entre los tres documentos.

---

## 10. Referencias

- **Kubeflow — Documentación oficial**: guías de instalación, componentes y pipelines. Disponible en: [https://www.kubeflow.org/docs/](https://www.kubeflow.org/docs/)

- **KServe — Documentación oficial**: guía de instalación y configuración de InferenceServices. Disponible en: [https://kserve.github.io/website/](https://kserve.github.io/website/)

- **MLflow — Documentación oficial**: guías de tracking, registry y serving. Disponible en: [https://mlflow.org/docs/latest/index.html](https://mlflow.org/docs/latest/index.html)

- **Feast — Feature Store de código abierto**: documentación de arquitectura y uso. Disponible en: [https://docs.feast.dev/](https://docs.feast.dev/)

- **Google Vertex AI — Documentación oficial**: guía de la plataforma MLOps gestionada de GCP. Disponible en: [https://cloud.google.com/vertex-ai/docs](https://cloud.google.com/vertex-ai/docs)

- **Amazon SageMaker — Documentación oficial**: guía de la plataforma MLOps de AWS. Disponible en: [https://docs.aws.amazon.com/sagemaker/](https://docs.aws.amazon.com/sagemaker/)

- **Kong Gateway — Documentación oficial**: guía de instalación en Kubernetes y configuración de plugins. Disponible en: [https://docs.konghq.com/gateway/latest/](https://docs.konghq.com/gateway/latest/)

- **Keycloak — Documentación oficial**: servidor de autorización OIDC/OAuth2 de código abierto. Disponible en: [https://www.keycloak.org/documentation](https://www.keycloak.org/documentation)

- **Kubernetes RBAC — Documentación oficial**: guía de control de acceso basado en roles. Disponible en: [https://kubernetes.io/docs/reference/access-authn-authz/rbac/](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

- **OAuth 2.0 — RFC 6749**: especificación del protocolo OAuth 2.0. Disponible en: [https://www.rfc-editor.org/rfc/rfc6749](https://www.rfc-editor.org/rfc/rfc6749)

- **Google SRE Book — Service Level Objectives**: capítulo sobre la definición y medición de SLOs. Disponible en: [https://sre.google/sre-book/service-level-objectives/](https://sre.google/sre-book/service-level-objectives/)

- **Evidently AI — Documentación oficial**: monitorización de modelos ML en producción. Disponible en: [https://docs.evidentlyai.com/](https://docs.evidentlyai.com/)

---

*UD1 · MP03 Explotación de Servicios de Datos y Analítica · CFS2 Instalación, despliegue y explotación de sistemas de IA*
