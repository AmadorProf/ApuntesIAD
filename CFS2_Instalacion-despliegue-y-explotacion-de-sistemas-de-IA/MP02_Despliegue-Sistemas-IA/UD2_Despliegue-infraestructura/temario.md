# UD2 · Despliegue de infraestructura para sistemas de IA

---

## 1. Introducción — Cloud, on-premise e híbrido: decisiones de infraestructura para sistemas de IA

El despliegue de sistemas de inteligencia artificial plantea una pregunta fundamental antes de escribir una sola línea de código de infraestructura: ¿dónde viven los recursos de cómputo, almacenamiento y red que hacen funcionar estos sistemas? La respuesta no es universal. Depende de factores que van desde la sensibilidad de los datos hasta la velocidad de aprovisionamiento, pasando por el coste total de propiedad y los requisitos regulatorios.

Históricamente, las organizaciones operaban sus propios centros de datos. Los sistemas de IA de primera generación —modelos de regresión, sistemas de recomendación basados en reglas, redes neuronales superficiales— se ejecutaban en servidores físicos que el equipo de TI compraba, instalaba y mantenía. Este modelo on-premise ofrece control total: el hardware es propiedad de la organización, los datos nunca salen del perímetro, y la latencia de red interna suele ser predecible. Sin embargo, presenta limitaciones severas para la IA moderna. Un ciclo de entrenamiento de un modelo de lenguaje grande o de visión computacional puede requerir cientos de GPUs durante días. Comprar ese hardware para usarlo intensamente durante una semana y que permanezca ocioso el resto del mes es económicamente ineficiente.

El cloud público (AWS, GCP, Azure y otros) invirtió este modelo. La capacidad de aprovisionar una instancia con 8 GPUs A100 en minutos, pagar por horas de uso y liberar los recursos cuando el trabajo termina transformó radicalmente la viabilidad económica de entrenar modelos grandes. Además, los grandes proveedores construyeron servicios gestionados —SageMaker, Vertex AI, Azure ML— que abstraen buena parte de la complejidad de la infraestructura y permiten a los equipos de datos centrarse en el modelado.

El modelo híbrido surge como solución de compromiso cuando ninguno de los extremos satisface todos los requisitos. Una empresa financiera puede mantener sus datos de clientes on-premise por requisitos regulatorios, pero enviar jobs de entrenamiento al cloud usando datos sintéticos o anonimizados. Un sistema de visión industrial puede realizar inferencia en el edge —cerca de la línea de producción— pero enviar métricas y modelos actualizados a un backend en cloud. La arquitectura híbrida es frecuentemente más compleja de operar, pero refleja la realidad de muchas organizaciones.

Las decisiones de infraestructura para IA deben responder a varias dimensiones: el volumen y la sensibilidad de los datos de entrenamiento, la frecuencia y duración de los ciclos de entrenamiento, los requisitos de latencia para la inferencia en producción, la madurez del equipo de operaciones, y las restricciones presupuestarias tanto de capital como operativas. Esta unidad didáctica aborda los conceptos, herramientas y patrones que permiten tomar y ejecutar estas decisiones con rigor técnico.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Comparar los modelos cloud, on-premise e híbrido aplicados a cargas de trabajo de IA, justificando la elección en función de criterios técnicos, económicos y regulatorios.
- Escribir configuraciones de Infraestructura como Código con Terraform y Pulumi para aprovisionar instancias GPU en los principales proveedores cloud.
- Configurar clústeres Kubernetes con soporte nativo para GPUs, incluyendo node pools especializados, NVIDIA GPU Operator, tolerations y resource quotas.
- Diseñar estrategias de auto-scaling que combinen instancias spot/preemptible con checkpointing para optimizar el coste de los jobs de entrenamiento.
- Evaluar y seleccionar servicios de ML gestionados en AWS, GCP y Azure según el tipo de carga de trabajo.
- Describir las implicaciones de latencia, conectividad y residencia de datos en arquitecturas multi-cloud e híbridas.
- Implementar las actividades prácticas propuestas, demostrando competencia en la gestión del ciclo completo de aprovisionamiento de infraestructura para IA.

---

## 3. Infraestructura como código para IA

### El principio de infraestructura inmutable

Gestionar manualmente servidores GPU es una fuente constante de problemas: versiones de drivers inconsistentes, configuraciones que divergen entre entornos, dificultad para reproducir fallos. La Infraestructura como Código (IaC) aplica a los recursos de cómputo los mismos principios que el control de versiones aplica al software: la infraestructura se describe en archivos de texto, se almacena en repositorios, y se aplica de forma declarativa y reproducible.

### Terraform para instancias GPU

Terraform, desarrollado por HashiCorp, es la herramienta de IaC más extendida en entornos cloud. Utiliza un lenguaje declarativo propio (HCL, HashiCorp Configuration Language) y gestiona el estado de la infraestructura mediante un fichero de estado que mapea los recursos declarados con los recursos reales en el proveedor.

**Ejemplo completo: instancia p3.2xlarge en AWS**

La familia p3 de EC2 utiliza GPUs NVIDIA Tesla V100. La instancia `p3.2xlarge` ofrece 1 GPU V100 con 16 GB de memoria, 8 vCPUs y 61 GB de RAM. Es adecuada para entrenamiento de modelos de tamaño medio y para experimentación.

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket         = "mi-org-terraform-state"
    key            = "ia/training/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  default = "us-east-1"
}

variable "project_name" {
  description = "Nombre del proyecto de ML"
}

data "aws_ami" "deep_learning" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["Deep Learning AMI GPU PyTorch*"]
  }
  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

resource "aws_security_group" "ml_sg" {
  name        = "ml-training-sg"
  description = "Acceso SSH para nodos de entrenamiento"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "gpu_training" {
  ami                    = data.aws_ami.deep_learning.id
  instance_type          = "p3.2xlarge"
  vpc_security_group_ids = [aws_security_group.ml_sg.id]

  root_block_device {
    volume_size = 200
    volume_type = "gp3"
  }

  tags = {
    Name        = "gpu-training-node"
    Environment = "ml-experiments"
    Project     = var.project_name
  }
}

output "instance_id" {
  value = aws_instance.gpu_training.id
}

output "public_ip" {
  value = aws_instance.gpu_training.public_ip
}
```

El bloque `backend "s3"` almacena el estado remoto en un bucket de S3, lo que permite que múltiples miembros del equipo trabajen con la misma infraestructura sin conflictos. La tabla DynamoDB actúa como mecanismo de bloqueo para evitar aplicaciones concurrentes del estado.

**Ejemplo completo: instancia a2-highgpu-1g en GCP**

La familia A2 de GCP utiliza GPUs NVIDIA A100. La instancia `a2-highgpu-1g` incluye 1 GPU A100 con 40 GB de HBM2, 12 vCPUs y 85 GB de RAM.

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "mi-org-tf-state"
    prefix = "ml/training"
  }
}

provider "google" {
  project = var.project_id
  region  = "us-central1"
}

variable "project_id" {}

resource "google_compute_instance" "gpu_training" {
  name         = "gpu-training-node"
  machine_type = "a2-highgpu-1g"
  zone         = "us-central1-c"

  boot_disk {
    initialize_params {
      image = "projects/deeplearning-platform-release/global/images/family/pytorch-latest-gpu"
      size  = 200
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  guest_accelerator {
    type  = "nvidia-tesla-a100"
    count = 1
  }

  scheduling {
    on_host_maintenance = "TERMINATE"
    automatic_restart   = false
  }

  metadata = {
    install-nvidia-driver = "True"
  }
}
```

**Ejemplo completo: Azure NC-series**

Las instancias NC de Azure (NCv3, NC A100 v4) son el equivalente en Azure para cargas de trabajo de entrenamiento de modelos.

```hcl
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "ml" {
  name     = "ml-training-rg"
  location = "East US"
}

resource "azurerm_linux_virtual_machine" "gpu_training" {
  name                = "gpu-training-node"
  resource_group_name = azurerm_resource_group.ml.name
  location            = azurerm_resource_group.ml.location
  size                = "Standard_NC6s_v3"
  admin_username      = "mluser"

  network_interface_ids = [azurerm_network_interface.ml_nic.id]

  admin_ssh_key {
    username   = "mluser"
    public_key = file("~/.ssh/id_rsa.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
    disk_size_gb         = 200
  }

  source_image_reference {
    publisher = "microsoft-dsvm"
    offer     = "ubuntu-2004"
    sku       = "2004-gen2"
    version   = "latest"
  }
}
```

### Módulos Terraform reutilizables

En proyectos de IA con múltiples entornos (desarrollo, staging, producción) o múltiples regiones, duplicar el código HCL es un error. Los módulos Terraform encapsulan recursos relacionados en unidades reutilizables con interfaz definida: variables de entrada, recursos internos y outputs. Un módulo `gpu-instance` que acepta `instance_type`, `region` y `project_name` como parámetros puede instanciar la misma infraestructura en cualquier entorno con una sola declaración. Los módulos se publican en el Terraform Registry público o en repositorios privados Git y se invocan con el bloque `module {}`.

### State management con backend S3/GCS

El fichero de estado de Terraform es la fuente de verdad sobre la infraestructura real. En un equipo, este fichero debe almacenarse de forma remota para que todos los miembros vean el mismo estado, versionarse automáticamente para poder hacer rollback, y tener locking distribuido para evitar modificaciones concurrentes que corrompan el estado.

Con AWS S3 y DynamoDB (como en el ejemplo de p3.2xlarge anterior), el bucket S3 almacena el estado y la tabla DynamoDB proporciona el mecanismo de bloqueo. Con el backend `gcs` de GCP, el bloqueo se implementa mediante object locking nativo de GCS.

### Pulumi como alternativa en Python

Pulumi ofrece IaC usando lenguajes de programación completos: Python, TypeScript, Go, C#. Para equipos de datos habituados a Python, Pulumi elimina la curva de aprendizaje de HCL y permite usar bibliotecas estándar de Python en la definición de la infraestructura, incluyendo bucles, condicionales, funciones y tests unitarios con pytest.

```python
import pulumi
import pulumi_aws as aws

# Node pool GPU con configuración parametrizada
gpu_instance = aws.ec2.Instance("gpu-training",
    ami="ami-xxxxxxxxxxxxxxxxx",
    instance_type="p3.2xlarge",
    tags={
        "Name": "gpu-training",
        "Team": "data-science",
        "Environment": "experiments"
    })

pulumi.export("instance_id", gpu_instance.id)
pulumi.export("public_ip", gpu_instance.public_ip)
```

### Comparativa Terraform vs Pulumi vs CDK

| Criterio | Terraform | Pulumi | AWS CDK |
|---|---|---|---|
| Lenguaje | HCL | Python, TS, Go, C# | TypeScript, Python, Java |
| Portabilidad multi-cloud | Alta | Alta | Limitada a AWS |
| Curva de aprendizaje | Media | Baja (para devs) | Baja (para devs AWS) |
| Ecosistema de módulos | Muy maduro (Registry) | Creciente | CloudFormation nativo |
| Testing | Limitado | unittest / pytest estándar | Jest / pytest |
| Gestión de estado | Propio + remoto | Pulumi Cloud / self-hosted | CloudFormation |

La elección entre estas herramientas depende más del contexto del equipo que de capacidades técnicas objetivas. Terraform es la opción por defecto cuando la organización ya tiene experiencia y módulos propios. Pulumi es preferible cuando los ingenieros de ML quieren escribir infraestructura en Python sin aprender un nuevo DSL. CDK tiene sentido cuando el proyecto está completamente integrado en el ecosistema AWS y el equipo ya usa CloudFormation.

---

## 4. Cloud providers para IA

### AWS

**Instancias EC2 para ML**

AWS ofrece varias familias de instancias optimizadas para cargas de trabajo de IA:

- **Familia P (GPU NVIDIA):** P3 (V100), P4d (A100 x8), P5 (H100 x8). Son las instancias de referencia para entrenamiento de modelos grandes. P4d y P5 incluyen interconexión NVLink entre GPUs y redes de alto ancho de banda (EFA) para entrenamiento distribuido eficiente.
- **Familia G (GPU NVIDIA, inferencia y gráficos):** G4dn (T4), G5 (A10G). Mejor relación coste/rendimiento para inferencia de modelos de tamaño medio.
- **Familia Inf (AWS Inferentia):** Inf1, Inf2. Chips propietarios de AWS diseñados específicamente para inferencia de alto rendimiento a bajo coste. Requieren compilar el modelo con AWS Neuron SDK.
- **Familia Trn (AWS Trainium):** Trn1. Chips propietarios optimizados para entrenamiento de modelos grandes a menor coste que P4d/P5 para cargas compatibles con Neuron.

**Amazon SageMaker**

SageMaker es el servicio de ML gestionado de AWS. Sus componentes principales son:

- *Training Jobs:* jobs de entrenamiento gestionados que aprovisionan infraestructura automáticamente, ejecutan el código de entrenamiento en un contenedor Docker y liberan los recursos al terminar. Soportan entrenamiento distribuido con la librería SageMaker Distributed (data parallelism y model parallelism).
- *Endpoints:* servicio gestionado para desplegar modelos como APIs REST con auto-scaling basado en métricas de latencia e invocaciones por minuto. Soportan shadow deployment y A/B testing entre versiones de modelos.
- *Pipelines:* orquestación de workflows de ML (preprocesamiento, entrenamiento, evaluación, registro, despliegue) como grafos dirigidos acíclicos con trazabilidad completa.
- *Feature Store:* almacén centralizado de features con acceso en tiempo real (online store con baja latencia) y por lotes (offline store en S3 para entrenamiento).

**AWS Batch para jobs de ML**

Para jobs de entrenamiento que no requieren la integración de SageMaker, AWS Batch permite definir compute environments con instancias GPU spot, colas de prioridad y dependencias entre jobs. Es útil cuando se tienen pipelines de entrenamiento ya construidos en PyTorch o TensorFlow que no siguen las convenciones de SageMaker o que requieren mayor control sobre el entorno de ejecución.

**S3 como capa de artefactos**

Amazon S3 es el almacén estándar para datasets de entrenamiento, checkpoints de modelos, métricas y artefactos de pipelines. Su integración nativa con SageMaker, AWS Batch y EC2, junto con su durabilidad (99.999999999%) y su modelo de coste por GB almacenado, lo convierten en el sistema de ficheros de facto para ML en AWS.

### GCP

**Vertex AI Workbench**

Entornos de notebooks gestionados con acceso a GPUs y TPUs, integrados con BigQuery y GCS. Permite a los data scientists trabajar en Jupyter notebooks sin gestionar la infraestructura subyacente. Incluye integración con Git, gestión de dependencias y acceso a la API de Vertex AI directamente desde el notebook.

**Vertex AI Training**

Equivalente a SageMaker Training Jobs. Permite lanzar jobs de entrenamiento especificando un contenedor Docker, los recursos de cómputo (incluyendo TPUs) y el código de entrenamiento empaquetado como módulo Python. Soporta entrenamiento distribuido con reducción de gradientes y tiene integración nativa con Vertex AI Experiments para el registro automático de métricas.

**TPU Reservations**

Las TPUs (Tensor Processing Units) son el hardware propietario de Google para entrenamiento e inferencia de redes neuronales. La versión TPU v4 Pod ofrece una capacidad de cómputo masiva para entrenamiento de modelos de lenguaje grandes. Las reservas de TPU garantizan disponibilidad durante un período determinado, lo que es necesario dado que son recursos con alta demanda. Para modelos de la familia Transformer con decenas o cientos de miles de millones de parámetros, los pods TPU ofrecen una eficiencia de coste difícilmente igualable con GPUs convencionales.

**GCS (Google Cloud Storage)**

Equivalente a S3 en el ecosistema de GCP. Sirve como capa de artefactos para datasets, checkpoints, modelos en formato SavedModel o PyTorch, y logs de entrenamiento. Su integración directa con Vertex AI Training elimina la necesidad de gestionar el mounting de almacenamiento.

### Azure

**Azure Machine Learning**

El servicio de ML gestionado de Azure incluye: compute clusters (grupos de VMs que escalan dinámicamente para jobs de entrenamiento), endpoints en tiempo real (para inferencia síncrona) y batch (para inferencia por lotes), pipelines de ML y un registro de modelos integrado. Su integración nativa con Azure DevOps y GitHub Actions facilita la adopción en organizaciones que ya usan el ecosistema Microsoft para sus flujos de CI/CD.

**NCv3 y NDv4 VMs**

- *NCv3:* instancias con GPUs NVIDIA V100, equivalente a la familia P3 en AWS. Adecuadas para experimentación y fine-tuning de modelos de tamaño medio.
- *NDv4:* instancias con 8 GPUs NVIDIA A100 conectadas mediante NVLink, diseñadas para entrenamiento distribuido de modelos grandes. Equivalente a P4d en AWS. Incluyen InfiniBand para comunicación inter-nodo de alto rendimiento.

**Azure Blob Storage**

Capa de almacenamiento de objetos de Azure, equivalente a S3/GCS. Se integra con Azure ML para almacenamiento de datasets y artefactos, y soporta las mismas operaciones de versionado y control de acceso basado en roles (RBAC).

### Comparativa de servicios ML gestionados

| Característica | SageMaker (AWS) | Vertex AI (GCP) | Azure ML |
|---|---|---|---|
| Training distribuido | SageMaker Distributed | Nativo (TF/PyTorch/JAX) | DeepSpeed, Horovod |
| Hardware propietario | Inferentia, Trainium | TPU v4/v5 | No |
| Pipelines | SageMaker Pipelines | Vertex Pipelines | Azure ML Pipelines |
| Feature store | SageMaker Feature Store | Vertex Feature Store | No nativo |
| Notebooks gestionados | SageMaker Studio | Vertex AI Workbench | Azure ML Notebooks |
| Responsible AI integrado | SageMaker Clarify | Vertex Explainable AI | Azure ML Responsible AI |

### Estrategia multi-cloud

Algunas organizaciones distribuyen sus cargas de trabajo entre proveedores para evitar el vendor lock-in, aprovechar las fortalezas específicas de cada proveedor (TPUs de GCP para ciertos modelos de lenguaje, Inferentia de AWS para inferencia de alto volumen a bajo coste) o cumplir requisitos de resiliencia geográfica. Esto añade complejidad operativa —gestión de múltiples IAMs, redes, APIs y modelos de facturación— pero puede ser justificable en escenarios de alta escala o cuando existen restricciones regulatorias específicas de región que obligan a distribuir la carga.

---

## 5. Kubernetes para IA: configuración avanzada

### Node pools con GPUs

Kubernetes organiza los nodos en pools (grupos de nodos con características homogéneas). Para cargas de trabajo de IA, es habitual crear node pools dedicados con instancias GPU separados de los nodos de propósito general. Esto permite aplicar políticas de scheduling, taints y tolerations de forma granular, y configurar auto-scaling independiente para el pool GPU sin afectar a la capacidad del pool general.

**Creación de node pool GPU en GKE:**

```bash
gcloud container node-pools create gpu-pool \
  --cluster=ml-cluster \
  --zone=us-central1-c \
  --machine-type=a2-highgpu-1g \
  --accelerator=type=nvidia-tesla-a100,count=1 \
  --num-nodes=2 \
  --enable-autoscaling \
  --min-nodes=0 \
  --max-nodes=10 \
  --node-taints=nvidia.com/gpu=present:NoSchedule
```

**Creación de node pool GPU en EKS:**

```bash
eksctl create nodegroup \
  --cluster=ml-cluster \
  --name=gpu-nodegroup \
  --node-type=p3.2xlarge \
  --nodes=2 \
  --nodes-min=0 \
  --nodes-max=10 \
  --node-ami-family=AmazonLinux2 \
  --asg-access
```

**Creación de node pool GPU en AKS:**

```bash
az aks nodepool add \
  --resource-group ml-rg \
  --cluster-name ml-cluster \
  --name gpunodepool \
  --node-count 2 \
  --node-vm-size Standard_NC6s_v3 \
  --enable-cluster-autoscaler \
  --min-count 0 \
  --max-count 10 \
  --node-taints nvidia.com/gpu=true:NoSchedule
```

### NVIDIA GPU Operator

El NVIDIA GPU Operator automatiza la instalación y gestión de todos los componentes necesarios para usar GPUs en Kubernetes: drivers NVIDIA, CUDA toolkit, container runtime (nvidia-container-toolkit), device plugin de Kubernetes para exponer las GPUs como recursos planificables, y DCGM Exporter para métricas de temperatura, uso de memoria y rendimiento de la GPU exportadas a Prometheus.

Sin el GPU Operator, cada nodo requeriría instalación manual de drivers y configuración del runtime de contenedores para pasar las GPUs al interior de los pods. El operador gestiona este ciclo de vida automáticamente, incluyendo actualizaciones de drivers que respetan el ciclo de vida de los pods en ejecución.

**Instalación con Helm:**

```bash
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

helm install gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator \
  --create-namespace \
  --set driver.enabled=true \
  --set toolkit.enabled=true \
  --set devicePlugin.enabled=true \
  --set dcgmExporter.enabled=true \
  --set gfd.enabled=true
```

El flag `gfd.enabled=true` activa el GPU Feature Discovery, que etiqueta automáticamente los nodos con metadatos de la GPU detectada: `nvidia.com/gpu.count`, `nvidia.com/gpu.memory`, `nvidia.com/gpu.product`. Estas etiquetas permiten el node selection preciso en los manifiestos de Pods.

### Tolerations y node selectors para GPUs

Los taints en los nodos GPU evitan que pods sin requisitos de GPU sean schedulados en ellos, protegiéndolos para las cargas que realmente necesitan el recurso. Los tolerations permiten a los pods de ML declarar que aceptan ejecutarse en nodos con esos taints.

**Taint en el nodo (si no se configuró en la creación del pool):**

```bash
kubectl taint nodes <nombre-nodo> nvidia.com/gpu=present:NoSchedule
```

**Toleration y nodeSelector en el manifiesto del Pod:**

```yaml
tolerations:
  - key: "nvidia.com/gpu"
    operator: "Equal"
    value: "present"
    effect: "NoSchedule"
nodeSelector:
  nvidia.com/gpu.present: "true"
  nvidia.com/gpu.product: "A100-SXM4-40GB"
```

El nodeSelector usando la etiqueta `nvidia.com/gpu.product` permite seleccionar un modelo específico de GPU cuando el clúster tiene varios tipos (por ejemplo, mezcla de V100 y A100).

### Resource quotas para GPU en namespaces

Las resource quotas permiten limitar el consumo de GPUs por namespace, evitando que un equipo monopolice los recursos compartidos del clúster. En entornos donde varios equipos comparten la misma infraestructura Kubernetes, las quotas son el mecanismo de gobernanza fundamental.

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: gpu-quota
  namespace: team-datos
spec:
  hard:
    requests.nvidia.com/gpu: "4"
    limits.nvidia.com/gpu: "4"
    pods: "20"
    requests.memory: "128Gi"
    limits.memory: "256Gi"
```

Con esta quota, el namespace `team-datos` puede usar como máximo 4 GPUs simultáneamente, independientemente de cuántas GPUs tenga el clúster en total.

### PriorityClasses para cargas de entrenamiento vs inferencia

Los jobs de inferencia en producción tienen requisitos de disponibilidad más estrictos que los jobs de entrenamiento, que pueden tolerar interrupciones si hay checkpointing implementado. Las PriorityClasses permiten que los pods de inferencia desplacen (preempt) a los pods de entrenamiento cuando los recursos son escasos, garantizando que la API de producción permanece operativa.

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: inference-high-priority
value: 1000
globalDefault: false
description: "Servicios de inferencia en producción"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: training-low-priority
value: 100
globalDefault: false
description: "Jobs de entrenamiento e investigación"
```

Cuando el scheduler necesita liberar recursos para un pod con `inference-high-priority`, puede desalojar pods con `training-low-priority` si implementan checkpointing y toleran la interrupción.

### Ejemplo completo: Deployment para servicio de inferencia

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inference-service
  namespace: ml-production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: inference-service
  template:
    metadata:
      labels:
        app: inference-service
    spec:
      priorityClassName: inference-high-priority
      tolerations:
        - key: "nvidia.com/gpu"
          operator: "Equal"
          value: "present"
          effect: "NoSchedule"
      nodeSelector:
        nvidia.com/gpu.present: "true"
      containers:
        - name: model-server
          image: mi-org/model-server:v1.2.0
          resources:
            requests:
              nvidia.com/gpu: "1"
              memory: "8Gi"
              cpu: "2"
            limits:
              nvidia.com/gpu: "1"
              memory: "16Gi"
              cpu: "4"
          ports:
            - containerPort: 8080
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 60
            periodSeconds: 30
```

---

## 6. Auto-scaling de infraestructura

### Cluster Autoscaler para Kubernetes

El Cluster Autoscaler (CA) observa los pods en estado `Pending` (no schedulados por falta de recursos) y añade nodos al clúster. También elimina nodos infrautilizados durante períodos configurables, reduciendo el coste cuando la demanda disminuye.

**Configuración en AWS (EKS):**

```yaml
containers:
  - image: registry.k8s.io/autoscaling/cluster-autoscaler:v1.28.0
    command:
      - ./cluster-autoscaler
      - --v=4
      - --stderrthreshold=info
      - --cloud-provider=aws
      - --skip-nodes-with-local-storage=false
      - --expander=least-waste
      - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/ml-cluster
      - --balance-similar-node-groups
      - --scale-down-enabled=true
      - --scale-down-delay-after-add=10m
      - --scale-down-unneeded-time=10m
      - --scale-down-utilization-threshold=0.5
```

El flag `--expander=least-waste` hace que el CA elija el grupo de nodos que desperdicie menos recursos al añadir un nodo. Para clústeres GPU con varios tipos de instancia, esto es importante: si hay pods que requieren 1 GPU, es preferible añadir una instancia con 1 GPU que una con 8.

**Configuración en GCP (GKE):**

En GKE, el Cluster Autoscaler se activa directamente en la configuración del node pool con `--enable-autoscaling`. GKE gestiona el CA de forma transparente como parte del plano de control gestionado, lo que simplifica la operación. Los parámetros de scale-down se configuran a nivel de clúster con `gcloud container clusters update`.

### Karpenter (AWS): provisioning just-in-time

Karpenter es un autoescalador de siguiente generación para AWS que reemplaza al Cluster Autoscaler en entornos EKS. A diferencia del CA, Karpenter no opera sobre Auto Scaling Groups predefinidos. En su lugar, selecciona dinámicamente el tipo de instancia más adecuado para los pods pendientes y la aprovisiona directamente mediante la API de EC2, sin necesidad de que existan ASGs configurados de antemano.

```yaml
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: gpu-provisioner
spec:
  requirements:
    - key: node.kubernetes.io/instance-type
      operator: In
      values: ["p3.2xlarge", "p3.8xlarge", "g4dn.xlarge", "g5.xlarge"]
    - key: karpenter.sh/capacity-type
      operator: In
      values: ["spot", "on-demand"]
    - key: kubernetes.io/arch
      operator: In
      values: ["amd64"]
  limits:
    resources:
      nvidia.com/gpu: "20"
  ttlSecondsAfterEmpty: 300
  providerRef:
    name: default
```

Karpenter es especialmente útil para cargas de ML porque puede seleccionar el tipo de instancia GPU más barato disponible en el mercado spot en el momento del aprovisionamiento, eligiendo dinámicamente entre p3.2xlarge, g4dn.xlarge u otras según disponibilidad y precio.

### Spot instances y preemptible VMs para entrenamiento

Las instancias spot de AWS y las VMs preemptibles de GCP pueden ser interrumpidas por el proveedor con un aviso previo (2 minutos en AWS, 30 segundos en GCP). A cambio, ofrecen descuentos del 60-90% sobre el precio on-demand. Para jobs de entrenamiento que implementan checkpointing, esta es la estrategia de coste más eficiente disponible en cloud público.

**Gestión de interrupciones con checkpointing:**

El patrón básico consiste en guardar el estado del modelo (pesos, optimizador, época y paso actual) en S3/GCS cada N pasos. Cuando la instancia es interrumpida y un nuevo nodo toma su lugar, el job de entrenamiento carga el último checkpoint y continúa desde ese punto. En AWS, el servicio de metadatos de instancia permite detectar la notificación de terminación de una instancia spot antes de que ocurra, ejecutando lógica de guardado final.

En PyTorch, el checkpointing periódico se implementa guardando el `state_dict` del modelo y el optimizador:

```python
def save_checkpoint(model, optimizer, epoch, step, loss, path):
    torch.save({
        'epoch': epoch,
        'step': step,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
    }, path)

def load_checkpoint(path, model, optimizer):
    checkpoint = torch.load(path)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    return checkpoint['epoch'], checkpoint['step'], checkpoint['loss']

# En el bucle de entrenamiento:
if step % checkpoint_interval == 0:
    save_checkpoint(
        model, optimizer, epoch, step, loss,
        f"s3://mi-bucket/checkpoints/checkpoint-step{step}.pt"
    )
```

SageMaker y Vertex AI tienen soporte nativo para checkpointing en jobs distribuidos, incluyendo la gestión de la reanudación automática cuando un nodo spot es interrumpido.

### Reserved vs on-demand vs spot: estrategia de coste

Una estrategia de coste efectiva para infraestructura de ML combina los tres tipos según la previsibilidad y tolerancia a interrupciones de cada carga:

- **Reserved instances (1-3 años):** para cargas de trabajo de inferencia en producción con demanda predecible y alta disponibilidad requerida. El descuento sobre on-demand es del 30-60% según el plazo. Los Savings Plans en AWS ofrecen mayor flexibilidad que las reserved instances clásicas al aplicarse sobre el gasto en cómputo en lugar de sobre una instancia específica.
- **On-demand:** para experimentos que no toleran interrupciones, demostraciones, validación de resultados de entrenamiento y workloads difíciles de anticipar. Precio base de referencia, sin compromisos.
- **Spot/preemptible:** para todos los jobs de entrenamiento que implementan checkpointing, y para trabajos de inferencia batch que toleran latencia. Máximo ahorro (60-90%), con el requisito de implementar tolerancia a interrupciones.

Una regla práctica consolidada en la industria: los servicios de inferencia en producción corren sobre reserved capacity, los jobs de entrenamiento sobre spot con fallback automático a on-demand cuando no hay spot disponible, y los entornos de desarrollo sobre on-demand sin reservas.

---

## 7. Arquitecturas multi-cloud e híbridas

### Casos de uso del modelo híbrido

El modelo híbrido surge cuando los datos de entrenamiento deben permanecer on-premise por requisitos regulatorios (datos médicos bajo HIPAA o RGPD, datos financieros bajo regulaciones bancarias nacionales, datos de menores) pero el cómputo de entrenamiento es más económico o flexible en el cloud. Los patrones más comunes son:

- **Datos on-premise, entrenamiento en cloud:** los datos se anonimiza o sintetizan antes de enviarlos al cloud, o se usa federated learning para que los gradientes (no los datos brutos) viajen al cloud para la agregación.
- **Entrenamiento en cloud, inferencia on-premise (edge):** el modelo se entrena aprovechando el cómputo elástico del cloud, pero la inferencia ocurre en el dispositivo o en infraestructura local para minimizar latencia y dependencia de conectividad.
- **Burst a cloud desde on-premise:** la infraestructura on-premise cubre la carga base habitual, y el cloud absorbe los picos de demanda durante fases de entrenamiento masivo o campañas estacionales.

### Conectividad: VPN, Direct Connect, Cloud Interconnect

La latencia y el ancho de banda entre on-premise y cloud son factores críticos en arquitecturas híbridas. Las opciones principales son:

- **VPN Site-to-Site:** conectividad básica sobre internet cifrado (IPSec). Latencia variable (50-200ms dependiendo de la distancia y la carga de internet), ancho de banda limitado por la conexión a internet contratada. Adecuada para volúmenes bajos de datos y para comunicación de control, no para transferencia masiva de datasets.
- **AWS Direct Connect:** conexión física dedicada entre el centro de datos propio y AWS, establecida a través de un proveedor de colocación o un socio de Direct Connect. Latencia predecible (típicamente <10ms en conexiones directas), ancho de banda de 1-100 Gbps. Necesaria para transferencias frecuentes de datasets grandes hacia S3 o para entrenamiento distribuido híbrido.
- **Google Cloud Interconnect:** equivalente a Direct Connect para GCP. Dedicated Interconnect (10/100 Gbps con conexión directa a un PoP de Google) o Partner Interconnect (50 Mbps a 50 Gbps a través de un proveedor de red socio de Google).
- **Azure ExpressRoute:** equivalente de Azure, con opciones de 50 Mbps a 100 Gbps. Soporta peering privado (acceso a servicios Azure) y peering de Microsoft (acceso a servicios como Microsoft 365 o Azure PaaS).

Para arquitecturas que transfieren datasets de entrenamiento de decenas o cientos de GB con frecuencia semanal o diaria, la conexión dedicada es económicamente justificable incluso considerando el coste del puerto mensual: el coste de transferencia de datos en cloud (egress fees, que en AWS son de ~$0.09/GB) puede superar el coste de la conexión física a escala de terabytes.

### Latencia y ancho de banda en el diseño

La latencia introduce restricciones en qué partes del sistema pueden ser híbridas. La inferencia síncrona —una API que responde a una petición de usuario final— puede tolerar 10-50ms adicionales por el salto de red on-premise a cloud, pero no 200ms si el SLA de respuesta es de 100ms. El entrenamiento asíncrono tolera latencias mucho mayores en la sincronización de parámetros entre nodos. El diseño debe cuantificar estos requisitos explícitamente antes de decidir dónde vive cada componente del sistema.

### Anthos (GCP) y EKS Anywhere para Kubernetes híbrido

**Anthos** es la plataforma de GCP para gestionar clústeres Kubernetes en múltiples entornos: GKE en cloud, on-premise (con Anthos on bare metal o Anthos on VMware), y otros clouds (AWS, Azure). Proporciona un plano de control unificado para policies, seguridad y observabilidad, independientemente de dónde estén los nodos. Desde la consola de Anthos, un único equipo de operaciones puede gestionar la configuración de todos los clústeres mediante GitOps con Config Sync, aplicar políticas de seguridad con Policy Controller y monitorizar métricas con Cloud Monitoring.

**EKS Anywhere** permite desplegar clústeres EKS en infraestructura propia (bare metal con Tinkerbell, VMware vSphere) con la misma API de Kubernetes de EKS en AWS, facilitando la portabilidad de workloads y el uso de herramientas del ecosistema AWS on-premise. Los teams que han invertido en herramientas, conocimiento y manifiestos Kubernetes en cloud pueden reutilizarlos en el centro de datos propio sin mantener distribuciones Kubernetes completamente diferentes.

### Reglas de residencia de datos en arquitectura multi-cloud

La residencia de datos (data residency) obliga a que determinados datos permanezcan dentro de una región geográfica o jurisdicción legal. GDPR en Europa exige que los datos personales de ciudadanos europeos sean procesados dentro del EEE o bajo acuerdos de transferencia adecuados. LGPD en Brasil, HIPAA en el sector sanitario de EE.UU., y regulaciones bancarias nacionales de múltiples países imponen restricciones que el arquitecto de infraestructura debe incorporar desde el diseño, no como capas adicionales de última hora.

En una arquitectura multi-cloud, los controles de residencia de datos incluyen:

- Etiquetar los recursos con la clasificación de sensibilidad de los datos que procesan (público, interno, confidencial, restringido) y la región de residencia permitida.
- Usar policies de organización en GCP (Organization Policies con restricciones de `gcp.resourceLocations`), Service Control Policies en AWS (SCPs de AWS Organizations) o Azure Policy para restringir en qué regiones pueden crearse recursos que manejan datos sensibles.
- Cifrar los datos en reposo y en tránsito con claves gestionadas por el cliente: CMEK en GCP con Cloud KMS, SSE-KMS en AWS con AWS KMS, cifrado con Azure Key Vault en Azure.
- Mantener logs de auditoría completos que demuestren que los datos no han salido de la región permitida: AWS CloudTrail, Google Cloud Audit Logs y Azure Monitor Audit Logs proveen registros inmutables de todas las operaciones sobre los datos.

---

## 8. Actividades prácticas

### Actividad 1: Aprovisionamiento de instancia GPU con Terraform

**Objetivo:** Aprovisionar una instancia GPU en AWS o GCP usando Terraform con backend de estado remoto, verificar el entorno de ML y liberar los recursos de forma controlada.

**Descripción:** El estudiante escribe una configuración Terraform completa que incluya: proveedor configurado con variables, backend remoto (S3 con tabla DynamoDB para locking en AWS, o GCS en GCP), data source para obtener la AMI/imagen de Deep Learning más reciente, recurso de instancia GPU con disco de 200 GB y etiquetas de proyecto, y outputs que muestren la IP pública y el ID de la instancia. Se ejecutará el ciclo completo: `terraform init`, `terraform plan` (revisando el plan antes de aplicar), `terraform apply`, conexión SSH a la instancia y verificación de GPU con `nvidia-smi`, y `terraform destroy` para liberar los recursos. Se revisará el fichero de estado en el backend remoto y se explicará qué información contiene y por qué es crítico protegerlo (contiene IDs y metadatos de todos los recursos gestionados).

**Entregables:** ficheros `.tf` comentados en un repositorio Git, captura del output de `terraform plan`, captura de la salida de `nvidia-smi`, y enlace al objeto de estado en el bucket remoto.

---

### Actividad 2: Configuración de node pool GPU en Kubernetes con NVIDIA GPU Operator

**Objetivo:** Añadir soporte GPU a un clúster Kubernetes, instalar el NVIDIA GPU Operator y verificar que las GPUs son visibles como recursos planificables.

**Descripción:** Partiendo de un clúster Kubernetes existente (GKE o EKS mínimo de coste bajo), el estudiante añadirá un node pool con al menos una instancia GPU usando el comando correspondiente al proveedor (comandos de gcloud o eksctl documentados en la sección 5). Instalará el NVIDIA GPU Operator mediante Helm con los flags indicados. Verificará que el nodo aparece en la salida de `kubectl describe node` con la capacidad `nvidia.com/gpu: 1` (o el número que corresponda). Aplicará el ResourceQuota del namespace de ejemplo para limitar el consumo del namespace de prueba. Desplegará un pod de prueba con la toleration y nodeSelector correctos que ejecute `nvidia-smi` como comando y revise los logs del pod para confirmar que la GPU es accesible dentro del contenedor.

**Entregables:** manifiesto YAML del pod de prueba, output de `kubectl describe node` mostrando la capacidad GPU y las etiquetas del GPU Feature Discovery, y logs del pod con la salida de `nvidia-smi`.

---

### Actividad 3: Implementación de checkpointing para entrenamiento en spot instances

**Objetivo:** Adaptar un script de entrenamiento PyTorch para implementar checkpointing periódico con guardado en S3/GCS y reanudación automática desde el último checkpoint disponible.

**Descripción:** Partiendo de un script de entrenamiento de clasificación de imágenes (por ejemplo, ResNet-18 en CIFAR-10), el estudiante añadirá las funciones `save_checkpoint` y `load_checkpoint` del ejemplo de la sección 6. Al inicio del script, añadirá la lógica de detección: listar los checkpoints existentes en el bucket y, si existe alguno, cargar el más reciente antes de comenzar el bucle de entrenamiento. El guardado se realizará cada 100 pasos. Se ejecutará el script en una instancia on-demand (o local) hasta el paso 300, se detendrá el proceso manualmente (simulando una interrupción spot), y se relanzará el script para verificar que detecta el checkpoint del paso 300 y continúa desde el paso 301. Los logs del segundo lanzamiento deben mostrar explícitamente "Reanudando desde checkpoint del paso 300".

**Entregables:** script Python con checkpointing documentado línea a línea en las partes añadidas, logs de los dos lanzamientos mostrando la interrupción y la reanudación, y listado del bucket mostrando los checkpoints guardados.

---

### Actividad 4: Comparativa de coste multi-cloud para un job de entrenamiento hipotético

**Objetivo:** Calcular y comparar el coste estimado de un job de entrenamiento en AWS, GCP y Azure usando instancias on-demand y spot/preemptible, y formular una recomendación justificada.

**Descripción:** Se define el siguiente escenario hipotético: entrenamiento de un modelo de visión computacional durante 72 horas continuas en una instancia con 1 GPU NVIDIA A100 (o equivalente más cercano disponible en cada proveedor). El job implementa checkpointing cada 30 minutos. Adicionalmente, se necesita almacenar 500 GB de dataset de imágenes y 50 GB de checkpoints durante 30 días.

El estudiante utilizará las calculadoras de coste de AWS Pricing Calculator, GCP Pricing Calculator y Azure Pricing Calculator para calcular: el coste on-demand de las 72 horas de instancia GPU en cada proveedor, el coste spot/preemptible equivalente (o el precio publicado más reciente para spot si la calculadora no lo incluye directamente), y el coste de almacenamiento (S3/GCS/Blob) para 550 GB durante 30 días. Se elaborará una tabla comparativa con el desglose por componente y el total para cada proveedor en ambas modalidades. La actividad concluye con un párrafo de recomendación que justifique la elección óptima para un equipo con checkpointing implementado y tolerancia a interrupciones.

**Entregables:** tabla comparativa en formato Markdown con la metodología de cálculo explícita, capturas de las calculadoras de los tres proveedores, y párrafo de recomendación justificado.

---

## 9. Referencias

**Infraestructura como código**

- HashiCorp. (2024). *Terraform Documentation*. Incluye guías de providers de AWS, GCP y Azure, gestión de módulos, backends remotos y workspaces. https://developer.hashicorp.com/terraform/docs
- Pulumi. (2024). *Pulumi Documentation*. Guía de uso de Pulumi con Python, TypeScript y otros lenguajes para IaC multi-cloud. https://www.pulumi.com/docs/

**AWS**

- Amazon Web Services. (2024). *Amazon SageMaker Developer Guide*. Documentación completa de SageMaker: training jobs, endpoints, pipelines y Feature Store. https://docs.aws.amazon.com/sagemaker/latest/dg/whatis.html
- Amazon Web Services. (2024). *Amazon EC2 Instance Types — Accelerated Computing*. Comparativa de familias P, G, Inf y Trn con especificaciones de GPU. https://aws.amazon.com/ec2/instance-types/#Accelerated_Computing
- Amazon Web Services. (2024). *Karpenter Documentation*. Provisioning just-in-time de nodos en EKS. https://karpenter.sh/docs/

**GCP**

- Google Cloud. (2024). *Vertex AI Documentation*. Vertex AI Training, Endpoints, Workbench, Pipelines y Feature Store. https://cloud.google.com/vertex-ai/docs
- Google Cloud. (2024). *Cloud TPU Documentation*. Guía de uso de TPUs v4/v5, reservas y configuración de pods. https://cloud.google.com/tpu/docs
- Google Cloud. (2024). *Anthos Documentation*. Gestión de clústeres Kubernetes en entornos híbridos y multi-cloud. https://cloud.google.com/anthos/docs

**Azure**

- Microsoft. (2024). *Azure Machine Learning Documentation*. Azure ML: compute clusters, endpoints, pipelines y registro de modelos. https://learn.microsoft.com/en-us/azure/machine-learning/
- Microsoft. (2024). *Azure Virtual Machines — NC and ND Series*. Especificaciones de VMs GPU NCv3 y NDv4 en Azure. https://learn.microsoft.com/en-us/azure/virtual-machines/nc-series

**Kubernetes y GPU**

- The Kubernetes Authors. (2024). *Kubernetes Documentation*. Referencia de APIs de Kubernetes: scheduling, resource quotas, PriorityClasses y Cluster Autoscaler. https://kubernetes.io/docs/home/
- NVIDIA. (2024). *GPU Operator Documentation*. Instalación y configuración del NVIDIA GPU Operator con Helm, incluyendo GPU Feature Discovery y DCGM Exporter. https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/index.html
- NVIDIA. (2024). *DCGM Exporter — GPU Metrics for Kubernetes*. Exportación de métricas GPU para Prometheus y Grafana. https://github.com/NVIDIA/dcgm-exporter

**Libros**

- Arundel, J. y Domingus, J. (2019). *Cloud Native Infrastructure: Patterns for Scalable Infrastructure and Applications in a Dynamic Environment*. O'Reilly Media. Referencia fundamental sobre infraestructura inmutable, IaC y patrones de operación en entornos cloud-native. ISBN: 978-1491984307. https://www.oreilly.com/library/view/cloud-native-infrastructure/9781491984291/
- Kleppmann, M. (2017). *Designing Data-Intensive Applications*. O'Reilly Media. Base para entender almacenamiento distribuido, replicación y consistencia en los sistemas que soportan pipelines de ML. ISBN: 978-1449373320. https://dataintensive.net/
