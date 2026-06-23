---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD3 · Implementación de componentes para su explotación | MP01 · Implementación de sistemas de IA'
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

# UD3 · Implementación de componentes para su explotación

MP01 · Implementacion de sistemas de IA

---

## Objetivos de la unidad

Al finalizar esta unidad el alumnado sera capaz de:

- Categorizar los componentes de un sistema de IA segun su funcionalidad, criticidad y entorno de destino
- Verificar la disponibilidad de recursos y la compatibilidad antes de cualquier instalacion
- Instalar y configurar el SO, drivers GPU, CUDA, entornos virtuales y librerias de ML siguiendo documentacion tecnica
- Desplegar un servidor de inferencia (Triton Inference Server) con configuracion basica
- Documentar el proceso de instalacion e incidencias segun estandares ITIL e ISO/IEC 20000

> **Resultado de aprendizaje:** Implementa los componentes de equipos y aplicaciones preparandolos para su explotacion por las personas usuarias.

---

## Categorizacion de componentes — Criterios

Antes de instalar cualquier componente es necesario clasificarlo segun tres dimensiones:

### 1. Funcionalidad

- **Infraestructura de base:** SO, drivers, firmware, red
- **Runtime de ejecucion:** CUDA, ROCm, OpenVINO, JVM
- **Entorno de aplicacion:** Python, conda, venv, contenedores
- **Libreria de ML:** PyTorch, TensorFlow, scikit-learn, ONNX Runtime
- **Servidor de servicios:** Triton, TF Serving, BentoML, FastAPI

### 2. Criticidad

- **Critico:** Su fallo detiene el servicio de inferencia en produccion
- **Importante:** Su fallo degrada el rendimiento pero el servicio continua
- **De soporte:** Herramientas de monitorizacion, logging, auditoria

### 3. Entorno de destino

- **Desarrollo (dev):** Flexibilidad maxima, versiones no estables permitidas
- **Preproduccion (staging):** Replica fiel de produccion, pruebas de integracion
- **Produccion (prod):** Versiones estables LTS, cambios controlados via CAB

---

## Categorizacion de componentes — Tabla de clasificacion

| Componente | Funcionalidad | Criticidad | Entorno tipico |
|---|---|---|---|
| Ubuntu 22.04 LTS | Infraestructura de base | Critico | Todos |
| Driver NVIDIA 535.x | Infraestructura de base | Critico | Staging, Prod |
| CUDA Toolkit 12.1 | Runtime de ejecucion | Critico | Staging, Prod |
| cuDNN 8.9.7 | Runtime de ejecucion | Critico | Staging, Prod |
| Python 3.11 (conda) | Entorno de aplicacion | Critico | Todos |
| PyTorch 2.3.1+cu121 | Libreria de ML | Critico | Todos |
| ONNX Runtime 1.17 | Libreria de ML | Importante | Staging, Prod |
| Triton Server 2.45 | Servidor de servicios | Critico | Staging, Prod |
| MLflow 2.12 | Herramienta MLOps | De soporte | Dev, Staging |
| Prometheus + Grafana | Monitorizacion | Importante | Staging, Prod |

> La categorizacion determina el procedimiento de cambio requerido: los componentes criticos de produccion requieren aprobacion del Comite de Cambios (CAB).

---

## Comprobacion de prerrequisitos — Checklist de recursos

Antes de iniciar la instalacion, verificar que el servidor cumple los requisitos minimos:

| Recurso | Verificacion | Comando de comprobacion | Minimo recomendado |
|---|---|---|---|
| RAM del sistema | `free -h` | `free -h \| grep Mem` | 32 GB para inferencia; 64 GB para entrenamiento |
| VRAM de GPU | `nvidia-smi` | `nvidia-smi --query-gpu=memory.total --format=csv` | 16 GB para modelos medianos; 80 GB para LLM grandes |
| Almacenamiento libre | `df -h` | `df -h /opt /var` | 200 GB SSD NVMe para modelos y logs |
| Velocidad de red | `iperf3` | `iperf3 -c <ip_servidor>` | 10 Gbps para inferencia distribuida |
| Version del SO | `lsb_release -a` | `cat /etc/os-release` | Ubuntu 22.04 LTS o superior |
| Arquitectura CPU | `uname -m` | `lscpu \| grep Architecture` | x86_64 (amd64) |
| Numero de nucleos | `nproc` | `lscpu \| grep "CPU(s)"` | 16 nucleos fisicos minimo |
| Conectividad a repos | `curl` | `curl -I https://pypi.org` | Acceso a PyPI, NVIDIA NGC, conda-forge |

---

## Comprobacion de prerrequisitos — Matriz de compatibilidad GPU/CUDA/Framework

| GPU | Driver NVIDIA | CUDA Toolkit | cuDNN | PyTorch | TensorFlow |
|---|---|---|---|---|---|
| NVIDIA H100 (SXM5/PCIe) | >= 530 | 12.0 - 12.4 | 8.9.x | 2.1+ | 2.13+ |
| NVIDIA A100 (SXM4/PCIe) | >= 520 | 11.8 - 12.4 | 8.6.x - 8.9.x | 1.13+ | 2.10+ |
| NVIDIA A10G (cloud) | >= 510 | 11.6 - 12.2 | 8.4.x - 8.9.x | 1.12+ | 2.8+ |
| NVIDIA RTX 4090 | >= 525 | 12.0 - 12.4 | 8.9.x | 2.0+ | 2.12+ |
| NVIDIA RTX 3090 | >= 515 | 11.4 - 12.3 | 8.2.x - 8.9.x | 1.10+ | 2.6+ |

> Fuente: [NVIDIA CUDA Compatibility Matrix](https://docs.nvidia.com/deeplearning/cudnn/support-matrix/index.html). Verificar siempre la matriz oficial antes de instalar. Una incompatibilidad de version provoca errores silenciosos o rendimiento degradado.

---

## Instalacion del SO — Ubuntu Server 22.04 LTS

### Particionado recomendado para servidores de IA

```
/boot/efi    512 MB    FAT32       Arranque UEFI
/boot          2 GB    ext4        Kernels e initrd
/             50 GB    ext4        Sistema base
/var          80 GB    ext4        Logs, Docker, apt cache
/opt         200 GB    ext4        Frameworks, modelos, conda
/home         20 GB    ext4        Usuarios
swap          32 GB    swap        (= RAM si RAM < 64 GB)
```

### Paquetes base tras la instalacion

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential dkms linux-headers-$(uname -r) \
    curl wget git htop nvtop tmux vim jq \
    python3-pip python3-venv python3-dev \
    net-tools iperf3 nfs-common
```

### Hardening inicial

```bash
# Deshabilitar root SSH, habilitar fail2ban
sudo systemctl enable --now fail2ban
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

---

## Instalacion del SO — Configuracion de red y acceso remoto

### Configuracion de IP estatica (Netplan)

```yaml
# /etc/netplan/01-static.yaml
network:
  version: 2
  ethernets:
    enp3s0:
      dhcp4: false
      addresses:
        - 192.168.10.20/24
      gateway4: 192.168.10.1
      nameservers:
        addresses: [8.8.8.8, 1.1.1.1]
```

```bash
sudo netplan apply
```

### Verificacion del acceso SSH

```bash
# Generar par de claves en el equipo del administrador
ssh-keygen -t ed25519 -C "admin@empresa.local"
ssh-copy-id -i ~/.ssh/id_ed25519.pub admin@192.168.10.20

# Primer acceso y verificacion del sistema
ssh admin@192.168.10.20 "uname -a && free -h && df -h"
```

---

## Instalacion de drivers GPU y CUDA — Pasos para NVIDIA A100

### Paso 1: Deshabilitar el driver nouveau (open-source)

```bash
# Crear fichero de blacklist
sudo bash -c 'cat > /etc/modprobe.d/blacklist-nouveau.conf << EOF
blacklist nouveau
options nouveau modeset=0
EOF'

sudo update-initramfs -u
sudo reboot
```

### Paso 2: Instalar el driver NVIDIA 535.x

```bash
# Anadir repositorio NVIDIA
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /"

sudo apt update
sudo apt install -y nvidia-driver-535 nvidia-utils-535

sudo reboot

# Verificar instalacion
nvidia-smi
# Debe mostrar: Driver Version: 535.xxx.xx | CUDA Version: 12.2
```

---

## Instalacion de drivers GPU y CUDA — CUDA Toolkit 12.1

### Paso 3: Instalar CUDA Toolkit 12.1

```bash
# Descarga del instalador runfile (recomendado para control de version)
wget https://developer.download.nvidia.com/compute/cuda/12.1.1/local_installers/cuda_12.1.1_530.30.02_linux.run
sudo sh cuda_12.1.1_530.30.02_linux.run --silent --toolkit --no-drm

# Anadir CUDA al PATH (en ~/.bashrc o /etc/environment)
echo 'export PATH=/usr/local/cuda-12.1/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verificar version
nvcc --version
# nvcc: NVIDIA (R) Cuda compiler driver, release 12.1, V12.1.105
```

### Paso 4: Instalar cuDNN 8.9.7

```bash
# Via apt (tras anadir el keyring de NVIDIA)
sudo apt install -y libcudnn8=8.9.7.29-1+cuda12.2 \
                   libcudnn8-dev=8.9.7.29-1+cuda12.2

# Verificar
cat /usr/include/cudnn_version.h | grep CUDNN_MAJOR -A 2
```

---

## Instalacion de entornos virtuales y librerias de ML

### Instalacion de Miniconda3

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p /opt/conda
echo 'export PATH=/opt/conda/bin:$PATH' | sudo tee /etc/profile.d/conda.sh
source /etc/profile.d/conda.sh
conda init bash && source ~/.bashrc
```

### Creacion del entorno de inferencia

```bash
conda create -n inference python=3.11.8 -y
conda activate inference

# Instalar PyTorch 2.3.1 con soporte CUDA 12.1
pip install torch==2.3.1+cu121 torchvision==0.18.1+cu121 \
    --index-url https://download.pytorch.org/whl/cu121

# Verificar que CUDA es accesible desde PyTorch
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
# Salida esperada: 2.3.1+cu121 | True | NVIDIA A100-SXM4-80GB
```

---

## Instalacion de entornos virtuales — Librerias adicionales

### Instalacion de librerias de soporte

```bash
conda activate inference

# ONNX Runtime con soporte CUDA
pip install onnxruntime-gpu==1.17.3

# scikit-learn y utilidades de datos
pip install scikit-learn==1.4.2 pandas==2.2.1 numpy==1.26.4

# Cliente Triton Inference Server
pip install tritonclient[grpc,http]==2.45.0

# Herramientas de monitorizacion y auditoria
pip install pip-licenses pipdeptree pip-audit

# Exportar el entorno reproducible
conda env export --no-builds > /opt/conda/envs/inference/environment_prod.yml
pip freeze > /opt/conda/envs/inference/requirements_prod.txt
```

### Verificacion del entorno completo

```bash
python -c "
import torch, onnxruntime, sklearn
print(f'PyTorch: {torch.__version__}')
print(f'ONNX Runtime: {onnxruntime.__version__}')
print(f'scikit-learn: {sklearn.__version__}')
print(f'CUDA disponible: {torch.cuda.is_available()}')
"
```

---

## Configuracion de parametros del sistema

### Limites del kernel para cargas de ML intensivas

```bash
# /etc/sysctl.d/99-ai-server.conf
sudo bash -c 'cat >> /etc/sysctl.d/99-ai-server.conf << EOF
# Incrementar limites de memoria compartida para procesos GPU
kernel.shmmax = 68719476736
kernel.shmall = 4294967296

# Optimizar rendimiento de red para inferencia
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
EOF'

sudo sysctl -p /etc/sysctl.d/99-ai-server.conf
```

### Configuracion de hugepages para GPU (reduce overhead de memoria)

```bash
# Habilitar hugepages transparentes (recomendado para PyTorch + CUDA)
echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled

# Deshabilitar swap (recomendado en servidores de inferencia pura)
sudo swapoff -a
sudo sed -i '/ swap /s/^/#/' /etc/fstab
```

---

## Configuracion del sistema — Variables de entorno CUDA

### Variables de entorno de CUDA en produccion

```bash
# /etc/environment o en el perfil del usuario de servicio
export CUDA_VISIBLE_DEVICES=0,1          # Limitar a GPU 0 y 1
export CUDA_DEVICE_ORDER=PCI_BUS_ID      # Orden determinista de GPU
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512  # Reduce fragmentacion

# Variables de rendimiento para Triton
export NCCL_DEBUG=WARN                   # Nivel de log de NCCL (multi-GPU)
export NCCL_IB_DISABLE=0                 # Habilitar InfiniBand si disponible
export OMP_NUM_THREADS=8                 # Hilos OpenMP para operaciones CPU
```

### Creacion del usuario de servicio

```bash
# Crear usuario de sistema sin login para los servicios de IA
sudo useradd -r -m -d /opt/ai-services -s /bin/false ai-svc
sudo usermod -aG video,render ai-svc    # Acceso a GPU
sudo chown -R ai-svc:ai-svc /opt/ai-services
```

---

## Despliegue de Triton Inference Server

### Estructura del model repository

```
/opt/ai-services/models/
├── text_classifier/
│   ├── config.pbtxt
│   └── 1/
│       └── model.onnx
├── embedding_model/
│   ├── config.pbtxt
│   └── 1/
│       └── model.pt
└── llm_pipeline/
    ├── config.pbtxt
    └── 1/
        └── model.py
```

### Ejemplo de config.pbtxt minimo (backend ONNX)

```protobuf
name: "text_classifier"
backend: "onnxruntime"
max_batch_size: 32

input [{ name: "input_ids"  data_type: TYPE_INT64  dims: [ -1 ] }]
output[{ name: "logits"     data_type: TYPE_FP32   dims: [ -1, 10 ] }]

dynamic_batching { preferred_batch_size: [8, 16, 32] max_queue_delay_microseconds: 5000 }
instance_group [{ count: 1 kind: KIND_GPU gpus: [0] }]
```

---

## Despliegue de Triton Inference Server — Arranque

### Arranque del servidor via Docker

```bash
docker run --gpus all --rm -d \
  --name triton-server \
  -p 8000:8000 \   # HTTP
  -p 8001:8001 \   # gRPC
  -p 8002:8002 \   # Metrics (Prometheus)
  -v /opt/ai-services/models:/models \
  nvcr.io/nvidia/tritonserver:24.03-py3 \
  tritonserver --model-repository=/models \
               --log-verbose=0 \
               --metrics-port=8002

# Verificar que el servidor esta listo
curl http://localhost:8000/v2/health/ready
# {"ready":true}

# Listar modelos cargados
curl http://localhost:8000/v2/models
```

### Prueba de inferencia desde Python

```bash
python -c "
import tritonclient.http as httpclient
client = httpclient.InferenceServerClient('localhost:8000')
print(client.is_server_live())
print(client.get_model_metadata('text_classifier'))
"
```

---

## Estandares y protocolos de documentacion

### ISO/IEC 20000 e ITIL aplicados a la instalacion de IA

- **ISO/IEC 20000-1:2018** exige que toda instalacion de software forme parte de un proceso de Gestion de Cambios documentado.
- **ITIL 4** define la instalacion como un **Change Request (CR)** con los siguientes pasos: solicitud → evaluacion de impacto → aprobacion CAB → implementacion → verificacion → cierre.

### Campos minimos del registro de instalacion

| Campo | Descripcion |
|---|---|
| ID de registro | Identificador unico (ej. INS-2025-0042) |
| Fecha y hora | ISO 8601 con timezone (2025-06-15T10:30:00+02:00) |
| Solicitante | Nombre y equipo |
| Componente | Nombre, version, fabricante |
| Entorno | dev / staging / prod |
| Servidor(es) afectados | FQDN o IP |
| CR asociado | Referencia al cambio aprobado |
| Procedimiento seguido | Referencia al documento de instalacion |
| Resultado | Exito / Exito con desviaciones / Fallido |
| Tecnico responsable | Nombre y firma (o usuario de sistema) |

---

## Registro de incidencias durante la instalacion

### Formato de ticket de incidencia

```yaml
incidencia:
  id: "INC-2025-0087"
  fecha_apertura: "2025-06-15T11:45:00+02:00"
  instalacion_ref: "INS-2025-0042"
  titulo: "Error de incompatibilidad cuDNN al importar torch.cuda"
  descripcion: |
    Al ejecutar `python -c "import torch; torch.cuda.is_available()"` se
    obtiene: RuntimeError: CUDA error: no kernel image is available.
    El driver NVIDIA instalado es 535.104 pero cuDNN 8.9.7 fue compilado
    para CUDA 12.2 y el toolkit instalado es CUDA 12.1.
  clasificacion:
    tipo: "Error de compatibilidad de versiones"
    prioridad: "Alta"
    impacto: "Bloquea la instalacion. Servicio no disponible."
  pasos_reproduccion:
    - "Activar entorno: conda activate inference"
    - "Ejecutar: python -c 'import torch; print(torch.cuda.is_available())'"
  solucion: |
    Instalar cuDNN 8.9.7 compilado para CUDA 12.1:
    apt install libcudnn8=8.9.7.29-1+cuda12.1
  fecha_cierre: "2025-06-15T13:20:00+02:00"
  tecnico: "Ana Garcia"
  escalado_a: ""
```

---

## Registro de incidencias — Clasificacion y escalado

### Matriz de clasificacion de incidencias

| Prioridad | Criterio | Tiempo de respuesta | Escalado |
|---|---|---|---|
| Critica (P1) | Produccion detenida, sin workaround | 15 min | Automatico a responsable de turno |
| Alta (P2) | Bloquea la instalacion, hay workaround parcial | 1 hora | Manual si no se resuelve en 2 h |
| Media (P3) | Problema menor, instalacion puede continuar | 4 horas | Manual si no se resuelve en 8 h |
| Baja (P4) | Cuestion estetica o de documentacion | 2 dias laborables | No aplica |

### Reglas de escalado

- Si una incidencia P1 no se resuelve en **30 minutos**, escalar automaticamente al responsable tecnico de guardia.
- Si requiere contacto con el proveedor (NVIDIA, Canonical), abrir ticket en el portal de soporte y referenciar el numero en el registro interno.
- Toda incidencia cerrada con solucion debe generar un **articulo de base de conocimiento** para evitar repeticion.

---

## Lista de comprobacion final antes de entregar a explotacion

Verificar cada punto antes de notificar al equipo de explotacion que el sistema esta listo:

- [ ] El servidor responde a ping y SSH con el usuario de servicio
- [ ] `nvidia-smi` muestra todas las GPU esperadas con el driver correcto
- [ ] `nvcc --version` confirma la version de CUDA instalada
- [ ] El entorno conda `inference` se activa sin errores
- [ ] `python -c "import torch; print(torch.cuda.is_available())"` devuelve `True`
- [ ] Triton Inference Server arranca y `/v2/health/ready` devuelve `{"ready":true}`
- [ ] Al menos un modelo de prueba se carga y responde a inferencias de test
- [ ] Las metricas de Prometheus son accesibles en el puerto 8002
- [ ] Los logs del servidor se escriben correctamente en `/var/log/ai-services/`
- [ ] El archivo `environment_prod.yml` y `requirements_prod.txt` estan guardados en el repositorio de configuracion
- [ ] La ficha de componentes YAML esta cumplimentada para todos los componentes instalados
- [ ] El registro de instalacion (INS-XXXX-XXXX) esta cerrado con resultado y firmado
- [ ] Se ha notificado al equipo de seguridad para el escaneo de vulnerabilidades inicial

---

## Actividad practica

### Instalacion de PyTorch con CUDA en Ubuntu y documentacion del proceso

**Objetivo:** Instalar PyTorch 2.3.1 con soporte CUDA en una maquina virtual Ubuntu 22.04 y documentar el proceso completo segun la plantilla de registro de instalacion de la unidad.

**Prerequisitos:** MV Ubuntu 22.04 con 8 GB RAM, 50 GB disco, GPU con CUDA (o CPU para la variante sin CUDA).

**Pasos:**

1. Comprobar los prerrequisitos con los comandos de la diapositiva 5 y rellenar la tabla de recursos
2. Instalar los paquetes base de SO descritos en la diapositiva 7
3. Instalar Miniconda3 en `/opt/conda` segun la diapositiva 11
4. Crear el entorno conda `inference` con Python 3.11 e instalar PyTorch
5. Verificar la instalacion con el bloque de comprobacion de la diapositiva 12
6. Si surge algun error, registrar la incidencia en el formato YAML de la diapositiva 19
7. Exportar el entorno con `conda env export` y `pip freeze`
8. Completar el registro de instalacion con todos los campos de la diapositiva 18

**Entregable:** Documento de registro de instalacion (YAML o Markdown), captura de pantalla de la verificacion de PyTorch, archivo `requirements_prod.txt` y ficha de componente de PyTorch.

---

## Puntos clave

- La categorizacion de componentes (funcionalidad, criticidad, entorno) determina el nivel de control y aprobacion requerido antes de instalar en produccion.
- La verificacion de prerrequisitos evita la mayoria de los errores de instalacion: comprobar recursos, compatibilidad de versiones y conectividad antes de comenzar.
- La secuencia correcta en servidores NVIDIA es: blacklist nouveau → reboot → driver → CUDA Toolkit → cuDNN → frameworks Python. Alterar el orden causa incompatibilidades.
- El entorno conda es la unidad de aislamiento en sistemas de IA: exportar `environment.yml` y `requirements.txt` inmediatamente tras la instalacion exitosa.
- Triton Inference Server requiere una estructura de model repository definida con `config.pbtxt` para cada modelo. La validacion inicial via `/v2/health/ready` confirma el arranque.
- Toda instalacion debe quedar registrada segun ITIL (CR → implementacion → verificacion → cierre) y toda incidencia debe documentarse con ID, descripcion, solucion y fecha de cierre.

---

## Criterios de evaluacion

| Criterio | Indicadores | Peso orientativo |
|---|---|---|
| Verificacion de compatibilidad y recursos | Comprueba todos los prerrequisitos antes de instalar; detecta y documenta incompatibilidades | 20% |
| Instalacion y configuracion segun documentacion | Ejecuta los pasos en el orden correcto; los resultados de verificacion son correctos | 35% |
| Documentacion del proceso | Completa el registro de instalacion con todos los campos obligatorios; registra incidencias segun el formato establecido | 25% |
| Entrega del entorno reproducible | Genera `environment.yml` y `requirements.txt` correctos y los almacena en el repositorio | 10% |
| Lista de comprobacion final | Verifica y marca todos los puntos de la lista antes de notificar la entrega a explotacion | 10% |

---

<!-- _class: lead -->

# Fin de la unidad

[← Volver a MP01](../)
