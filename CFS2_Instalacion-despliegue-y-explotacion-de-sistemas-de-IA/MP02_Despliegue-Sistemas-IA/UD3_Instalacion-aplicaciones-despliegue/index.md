---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD3 · Instalación de aplicaciones de despliegue | MP02 · Despliegue de sistemas de IA'
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

# UD3 · Instalación de aplicaciones de despliegue

MP02 · Despliegue de sistemas de IA

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno sera capaz de:

- Identificar las aplicaciones del ecosistema MLOps necesarias segun el Plan de aprovisionamiento
- Instalar y configurar orquestadores de contenedores, registros de artefactos y herramientas de monitorización
- Configurar relaciones entre aplicaciones: claves de API, volumenes, permisos y politicas
- Verificar la compatibilidad entre versiones de modelo, entorno y dependencias
- Mantener el inventario actualizado y documentar la instalacion con sus logs

> **Resultado de aprendizaje:** Instala y configura las aplicaciones del Plan de aprovisionamiento para desplegar sistemas de IA.

---

## El ecosistema de aplicaciones MLOps

### Mapa de aplicaciones por categoria

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE ORQUESTACION                     │
│           Kubernetes · Docker Swarm · Nomad                 │
├──────────────────────┬──────────────────────────────────────┤
│  REGISTRO            │  MONITORIZACIÓN                      │
│  Harbor              │  Prometheus + Grafana                │
│  JFrog Artifactory   │  Datadog · New Relic                 │
│  MLflow Registry     │  ELK Stack (logs)                    │
├──────────────────────┼──────────────────────────────────────┤
│  BALANCEO DE CARGA   │  SECRETOS                            │
│  NGINX · HAProxy     │  HashiCorp Vault                     │
│  AWS ALB · Traefik   │  AWS Secrets Manager                 │
├──────────────────────┴──────────────────────────────────────┤
│             FEATURE STORE / ALMACEN DE DATOS                │
│              Feast · Tecton · Hopsworks                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Orquestadores de contenedores: Kubernetes

### Por que Kubernetes para despliegues de IA

Kubernetes (K8s) es el estandar de facto para orquestar contenedores en produccion. Para sistemas de IA aporta:

| Capacidad | Beneficio para IA |
|---|---|
| Pods con limites de recursos | Garantizar VRAM y CPU por instancia de inferencia |
| Escalado horizontal automatico (HPA) | Escalar segun latencia o carga de inferencia |
| Rolling updates | Actualizar modelos sin interrupcion del servicio |
| Namespaces | Separar entornos (dev, staging, prod) en el mismo cluster |
| RBAC | Control de acceso granular por equipo y aplicacion |
| Persistent Volumes | Acceso compartido a modelos almacenados |

```yaml
# Recurso de GPU en un Pod de Kubernetes
resources:
  limits:
    nvidia.com/gpu: 1
    memory: "32Gi"
    cpu: "8"
```

---

## Instalacion de Kubernetes: componentes clave

### Arquitectura del cluster para MLOps

```
┌─────────────────────────────────┐
│         NODO MASTER             │
│  API Server · Scheduler         │
│  Controller Manager · etcd      │
└─────────────┬───────────────────┘
              │
    ┌─────────┴──────────┐
    │                    │
┌───┴──────────┐  ┌──────┴──────────┐
│  NODO CPU    │  │  NODO GPU        │
│  (API, web,  │  │  (inferencia,    │
│  frontend)   │  │  entrenamiento)  │
└──────────────┘  └─────────────────┘
```

### Instalacion con kubeadm (on-premise)

```bash
# En el nodo master
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
# Aplicar CNI (Flannel)
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml
# Instalar el plugin de dispositivos NVIDIA para GPU
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/main/nvidia-device-plugin.yml
```

---

## Registros de artefactos y modelos

### Funcion y diferencias entre tipos de registro

| Tipo | Que almacena | Herramientas |
|---|---|---|
| Registro de contenedores | Imagenes Docker/OCI | Harbor, Docker Hub, ECR, GCR |
| Registro de modelos | Artefactos ML, metricas, parametros | MLflow Registry, BentoML, Vertex AI |
| Registro de artefactos genericos | JARs, binarios, charts Helm | JFrog Artifactory, Nexus |

### Instalacion de MLflow con backend en PostgreSQL y S3

```bash
# Instalar MLflow con extras de base de datos y almacenamiento
pip install mlflow[extras]==2.11.0

# Iniciar el servidor de seguimiento
mlflow server \
  --backend-store-uri postgresql://mlflow:password@db:5432/mlflow \
  --default-artifact-root s3://ml-artifacts/ \
  --host 0.0.0.0 --port 5000
```

---

## Sistemas de monitorización y alarma

### Stack Prometheus + Grafana: instalacion con Helm

```bash
# Agregar el repositorio de Helm de la comunidad
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Instalar el stack completo (Prometheus + Grafana + Alertmanager)
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitorización --create-namespace \
  --set grafana.adminPassword="cambiar-en-produccion" \
  --set prometheus.prometheusSpec.retention=30d
```

### Configuracion de un exportador personalizado para el modelo

```python
# Exportador Prometheus para metricas del modelo de inferencia
from prometheus_client import Histogram, Counter, start_http_server

latencia_inferencia = Histogram('model_latency_seconds',
    'Latencia de inferencia', buckets=[.05, .1, .25, .5, 1.0, 2.5])
predicciones_total = Counter('model_predictions_total', 'Total de predicciones')
```

---

## Balanceadores de carga

### Comparativa de balanceadores para APIs de inferencia

| Balanceador | Modo | Algoritmos | TLS termination | Caracteristica destacada |
|---|---|---|---|---|
| NGINX | L7 (HTTP) | Round-robin, least-conn, ip-hash | Si | Muy maduro, amplia documentacion |
| HAProxy | L4/L7 | Round-robin, leastconn, random | Si | Alto rendimiento, health checks avanzados |
| Traefik | L7 | Round-robin, weighted | Si | Descubrimiento automatico en Kubernetes |
| AWS ALB | L7 | Round-robin, least-outstanding-req | Si (AWS ACM) | Integrado con ECS/EKS, WAF |

### Configuracion de NGINX para un servicio de inferencia

```nginx
upstream inferencia_backend {
    least_conn;
    server inferencia-01:8080 weight=1;
    server inferencia-02:8080 weight=1;
    keepalive 32;
}
server {
    listen 443 ssl;
    location /predict { proxy_pass http://inferencia_backend; }
}
```

---

## Gestion de secretos

### Por que los secretos no deben estar en el codigo ni en los ficheros de configuracion

Los secretos (claves de API, contrasenas, certificados) almacenados en repositorios Git son la principal causa de filtraciones de credenciales. La gestion correcta exige:

1. **Nunca** escribir secretos en ficheros de configuracion versionados
2. Usar un gestor de secretos dedicado (Vault, AWS Secrets Manager, Azure Key Vault)
3. Rotar los secretos periodicamente de forma automatica
4. Auditar cada acceso a los secretos

### HashiCorp Vault: flujo de uso

```bash
# 1. Almacenar un secreto
vault kv put secret/inferencia/registro \
    api_key="tk_prod_abc123" \
    registry_url="registry.empresa.com:5000"

# 2. El pod de Kubernetes lo obtiene en tiempo de ejecucion
vault kv get -field=api_key secret/inferencia/registro
```

---

## Configuracion de relaciones entre aplicaciones

### Patrones de integracion entre componentes MLOps

| Integracion | Mecanismo | Ejemplo |
|---|---|---|
| Servidor de inferencia → Registro de modelos | API REST + API Key desde Vault | TorchServe descarga el modelo de MLflow |
| Servidor de inferencia → Prometheus | Endpoint `/metrics` en formato Prometheus | Exportar latencia, throughput, errores |
| Alertmanager → Slack/correo | Webhook HTTPS | Enviar alertas al canal #mlops-alerts |
| Kubernetes → Vault | Autenticacion Kubernetes (Service Account) | Los pods obtienen secretos sin credenciales embebidas |
| Servidor de inferencia → Feature Store | gRPC o REST | Obtener features en tiempo real para cada peticion |

```yaml
# Anotacion en un Pod de Kubernetes para inyeccion de secretos con Vault Agent
annotations:
  vault.hashicorp.com/agent-inject: "true"
  vault.hashicorp.com/role: "inferencia"
  vault.hashicorp.com/agent-inject-secret-config: "secret/inferencia/registro"
```

---

## Verificacion de compatibilidad entre versiones

### Matriz de compatibilidad: ejemplo real para TorchServe

| TorchServe | PyTorch | Python | CUDA | Estado |
|---|---|---|---|---|
| 0.9.0 | 2.1.x | 3.8–3.11 | 11.8, 12.1 | Soportado |
| 0.8.2 | 2.0.x | 3.8–3.10 | 11.7, 11.8 | Mantenimiento |
| 0.7.1 | 1.13.x | 3.8–3.9 | 11.6 | No soportado |

### Verificacion de compatibilidad antes de instalar

```bash
# Verificar que el artefacto del modelo es compatible con el runtime instalado
# 1. Comprobar la version de opset ONNX del modelo
python -c "
import onnx
model = onnx.load('modelo.onnx')
print('Opset version:', model.opset_import[0].version)
"
# 2. Comprobar la version maxima de opset soportada por el runtime
python -c "import onnxruntime as ort; print(ort.get_device(), ort.__version__)"
```

---

## Inventario actualizado y logs de instalacion

### Estructura del inventario de aplicaciones instaladas

| Aplicacion | Version | Nodo / Namespace | Fecha de instalacion | Responsable | Log de instalacion |
|---|---|---|---|---|---|
| Kubernetes | 1.29.2 | Cluster completo | 2025-03-10 | J. Lopez | install-k8s-20250310.log |
| MLflow | 2.11.0 | ns/mlops | 2025-03-11 | M. Garcia | install-mlflow-20250311.log |
| Prometheus stack | 57.2.0 | ns/monitorizacion | 2025-03-11 | M. Garcia | install-prom-20250311.log |
| Harbor | 2.10.1 | ns/registry | 2025-03-12 | J. Lopez | install-harbor-20250312.log |
| Vault | 1.15.6 | ns/vault | 2025-03-12 | A. Ruiz | install-vault-20250312.log |

> El inventario es un documento vivo: se actualiza en cada instalacion, actualizacion o desinstalacion.

---

## Actividad practica: instalacion y configuracion de la pila MLOps

### Escenario

Un equipo debe instalar la pila basica de MLOps en un cluster Kubernetes de desarrollo de 3 nodos (1 master + 2 workers con GPU). El presupuesto es limitado y se priorizan herramientas open source.

### Tarea

Disenar el plan de instalacion:

1. Seleccionar una herramienta de cada categoria (orquestacion, registro, monitorización, secretos) y justificar la eleccion
2. Definir el orden de instalacion y las dependencias entre aplicaciones
3. Disenar la configuracion de relaciones: que credenciales necesita cada aplicacion y como se gestionan sin escribirlas en ficheros de configuracion
4. Disenar la verificacion post-instalacion: que pruebas confirman que todo funciona correctamente

### Entregable

Plan de instalacion con orden, justificaciones y checklist de verificacion.

---

## Puntos clave de la UD3

- Las aplicaciones del ecosistema MLOps no son opcionales: sin registro de modelos, sin orquestador y sin monitorización no existe un despliegue reproducible ni operable
- El **orden de instalacion importa**: primero la capa de secretos (Vault), luego el registro (Harbor, MLflow), luego el orquestador (K8s ya instalado), luego monitorización, luego aplicaciones de inferencia
- Los secretos nunca van en ficheros de configuracion versionados: siempre en un gestor de secretos dedicado
- La verificacion de compatibilidad de versiones debe hacerse **antes** de instalar, no despues: consultar la matriz de compatibilidad oficial de cada herramienta
- El inventario de aplicaciones instaladas es un documento normativo: sin el no es posible diagnosticar incidencias ni planificar actualizaciones

---

## Criterios de evaluacion — UD3

| Criterio | Indicadores de logro |
|---|---|
| Instala las aplicaciones segun el Plan | Sigue el Plan de aprovisionamiento; instala las versiones especificadas; verifica cada instalacion |
| Configura permisos y relaciones | Usa Vault o equivalente para todos los secretos; configura RBAC en Kubernetes; define politicas de acceso |
| Verifica compatibilidad | Consulta matrices de compatibilidad oficiales; comprueba versiones de opset/framework/CUDA antes de instalar |
| Documenta e inventaria | Actualiza el inventario con cada intervencion; adjunta logs de instalacion; registra fecha y responsable |

---

[← Volver a MP02](../index.md)


---

<!-- nav-slide -->

## Navegación

[← UD2 · Despliegue de la infraestruct…](../UD2_Despliegue-infraestructura/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD4 · Integración en el flujo produ… →](../UD4_Integracion-flujo-productivo/)
