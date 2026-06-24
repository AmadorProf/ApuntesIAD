# UD3 · Preparación del entorno de ejecución para LLMs

---

## 1. Introducción

La ejecución de modelos de lenguaje de gran tamaño (LLMs) impone requisitos de infraestructura sustancialmente distintos a los de los modelos de aprendizaje automático clásicos. Un modelo de clasificación de imágenes puede desplegarse en una instancia de propósito general con una GPU de gama media; un modelo de 70 mil millones de parámetros en precisión BF16 ocupa aproximadamente 140 GB de memoria de vídeo y requiere una configuración de software muy específica para ejecutarse con la latencia y el throughput que exige un entorno de producción. Preparar el entorno de ejecución para LLMs es, por tanto, una disciplina técnica propia que combina administración de sistemas, conocimiento profundo del stack de software GPU y comprensión de los requisitos de los frameworks de inferencia modernos.

El stack de software para la inferencia de LLMs está compuesto por capas bien diferenciadas que deben configurarse de forma coherente. En la base se encuentra el sistema operativo, sobre el cual se instalan los drivers propietarios de la unidad de procesamiento gráfico y el kit de herramientas CUDA, que expone las capacidades de computación paralela de la GPU al software de usuario. Sobre esa base, las bibliotecas de álgebra lineal acelerada —cuBLAS, cuDNN, NCCL— proporcionan las primitivas matemáticas que utilizan los frameworks de inferencia. Finalmente, el framework de inferencia —vLLM, Text Generation Inference, llama.cpp, Ollama u otros— gestiona la carga del modelo en memoria, la planificación de solicitudes, el mecanismo de KV cache y la exposición de la API de servicio.

La contenedorización de este stack es una práctica que aporta beneficios muy significativos en términos de reproducibilidad, aislamiento y portabilidad. La imagen Docker de un entorno de inferencia de LLM encapsula el sistema operativo base, los drivers de CUDA en su versión exacta, las bibliotecas y el framework, de forma que el comportamiento del entorno es idéntico en desarrollo, pre-producción y producción. El soporte de GPU en contenedores se materializa a través del NVIDIA Container Toolkit, que permite a los contenedores Docker acceder directamente al hardware de la GPU del anfitrión mediante la exposición de los dispositivos correspondientes.

La gestión de los pesos del modelo es otra dimensión crítica que no debe improvisarse. Los pesos de un LLM moderno pueden ocupar entre 7 GB (modelos de 7B en INT4) y más de 500 GB (modelos de mayor escala en precisión plena). Su descarga, almacenamiento, distribución a los nodos de inferencia y verificación de integridad deben estar automatizados y supervisados. Los modelos que no pueden descargarse en tiempo razonable, que se corrompieron durante la transferencia o que no se encuentran en el formato esperado por el framework son fuentes habituales de incidentes en la puesta en servicio. Esta unidad aborda todas estas capas de forma sistemática, desde la configuración del sistema operativo hasta la primera inferencia de verificación.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Instalar y configurar un sistema Ubuntu Server preparado para la ejecución de LLMs, incluyendo drivers NVIDIA, CUDA Toolkit y cuDNN en versiones compatibles con los frameworks de inferencia seleccionados.
2. Crear y gestionar entornos Python reproducibles con conda, venv y pyenv, y administrar dependencias con pip y Poetry para proyectos de inferencia de LLMs.
3. Instalar, configurar y arrancar al menos dos frameworks de inferencia de LLMs (vLLM, Ollama, llama.cpp o Text Generation Inference) y verificar su correcto funcionamiento mediante solicitudes de prueba.
4. Construir imágenes Docker con soporte GPU para la ejecución de LLMs, configurar el NVIDIA Container Toolkit y orquestar entornos multi-contenedor con Docker Compose.
5. Descargar modelos desde Hugging Face Hub con autenticación, verificar su integridad mediante checksums y gestionar el almacenamiento de pesos en volúmenes locales, NFS o S3.
6. Configurar las variables de entorno críticas para la inferencia de LLMs (CUDA_VISIBLE_DEVICES, variables NCCL, caché de Transformers) y documentar su efecto sobre el comportamiento del sistema.
7. Ejecutar un conjunto de pruebas de smoke test que acrediten la operatividad del entorno: primera inferencia correcta, utilización de GPU verificada y latencia dentro de los umbrales esperados.
8. Desplegar el stack completo de inferencia en un clúster Kubernetes con el nvidia-device-plugin y validar la asignación de recursos GPU a los pods.

---

## 3. Configuración del sistema operativo base

### 3.1 Selección y preparación de Ubuntu Server

Ubuntu Server LTS (Long Term Support) es la distribución Linux más ampliamente utilizada en entornos de inferencia de LLMs por su compatibilidad con los drivers NVIDIA, la madurez de su ecosistema de paquetes y el soporte extendido de cinco años. La versión recomendada para nuevas instalaciones en 2024-2025 es **Ubuntu 22.04 LTS** (Jammy Jellyfish), aunque Ubuntu 24.04 LTS es ya estable para entornos que requieran un kernel más reciente.

Tras la instalación base, se recomienda aplicar las siguientes configuraciones antes de proceder con el stack de GPU:

```bash
# Actualizar el sistema completamente
sudo apt update && sudo apt upgrade -y

# Instalar dependencias generales
sudo apt install -y build-essential dkms linux-headers-$(uname -r) \
    curl wget git vim htop nvtop screen tmux \
    python3-pip python3-venv

# Configurar el tiempo del sistema (crítico para logs y certificados)
sudo timedatectl set-timezone Europe/Madrid
sudo systemctl enable systemd-timesyncd

# Deshabilitar el gestor gráfico si está activo (no necesario en servidor headless)
sudo systemctl set-default multi-user.target
```

La configuración de la memoria virtual es importante para sistemas que ejecutan múltiples modelos o procesos de carga intensiva:

```bash
# Aumentar el límite de archivos abiertos
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Configurar el espacio de swap (recomendado: igual a la RAM)
sudo fallocate -l 64G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 3.2 Instalación de drivers NVIDIA

La selección de la versión correcta del driver NVIDIA es un paso crítico. El driver debe ser compatible con la GPU instalada y con la versión de CUDA Toolkit que requieren los frameworks de inferencia. La tabla siguiente resume la compatibilidad de referencia:

| Driver NVIDIA | CUDA máximo soportado | GPUs compatibles |
|---|---|---|
| 525.x | CUDA 12.0 | A100, H100, RTX 3090/4090 |
| 535.x | CUDA 12.2 | A100, H100, RTX 3090/4090, L40 |
| 545.x | CUDA 12.3 | A100, H100, RTX 4090, L40S |
| 550.x | CUDA 12.4 | H100, H200, RTX 4090, L40S, A100 |
| 560.x | CUDA 12.6 | H100, H200, Blackwell (B200) |

El método recomendado de instalación en producción es a través del repositorio oficial de NVIDIA, no a través de los paquetes de Ubuntu, ya que los paquetes de Ubuntu pueden estar desactualizados:

```bash
# Eliminar instalaciones previas si existen
sudo apt purge nvidia* libnvidia* -y
sudo apt autoremove -y

# Añadir el repositorio CUDA de NVIDIA
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update

# Instalar el driver (ejemplo: versión 550)
sudo apt install -y nvidia-driver-550

# Reiniciar el sistema
sudo reboot

# Verificar la instalación
nvidia-smi
```

La salida de `nvidia-smi` debe mostrar el modelo de GPU, la versión del driver y la versión de CUDA soportada, junto con el consumo de potencia y temperatura de cada dispositivo.

### 3.3 CUDA Toolkit y cuDNN

El **CUDA Toolkit** proporciona el compilador nvcc, las bibliotecas de tiempo de ejecución, herramientas de perfilado y las cabeceras necesarias para compilar código CUDA. Los frameworks de inferencia de LLMs como vLLM compilan kernels CUDA personalizados durante la instalación y requieren que el toolkit esté disponible en el sistema.

```bash
# Instalar CUDA Toolkit 12.4 (ejemplo)
sudo apt install -y cuda-toolkit-12-4

# Configurar las variables de entorno de CUDA en el perfil del sistema
echo 'export CUDA_HOME=/usr/local/cuda' | sudo tee -a /etc/profile.d/cuda.sh
echo 'export PATH=$CUDA_HOME/bin:$PATH' | sudo tee -a /etc/profile.d/cuda.sh
echo 'export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH' | sudo tee -a /etc/profile.d/cuda.sh
source /etc/profile.d/cuda.sh

# Verificar
nvcc --version
```

**cuDNN** (CUDA Deep Neural Network library) es la biblioteca de NVIDIA que proporciona implementaciones altamente optimizadas de operaciones de redes neuronales como convoluciones, normalización y atención. La mayoría de los frameworks de inferencia modernos la utilizan de forma implícita:

```bash
# Instalar cuDNN 9.x para CUDA 12
sudo apt install -y libcudnn9-cuda-12 libcudnn9-dev-cuda-12
```

---

## 4. Gestión del entorno Python

### 4.1 pyenv: gestión de versiones de Python

**pyenv** permite instalar y gestionar múltiples versiones de Python en el mismo sistema sin interferir con el Python del sistema operativo. Es especialmente útil cuando distintos frameworks requieren versiones diferentes del intérprete:

```bash
# Instalar pyenv
curl https://pyenv.run | bash

# Añadir al shell
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# Instalar la versión deseada de Python
pyenv install 3.11.9
pyenv global 3.11.9

# Verificar
python --version
```

### 4.2 conda: entornos con dependencias complejas

**conda** es preferible a venv cuando el proyecto tiene dependencias en paquetes no-Python (bibliotecas C, CUDA, etc.) que conda puede gestionar directamente. Miniconda es la instalación mínima recomendada para servidores de producción:

```bash
# Instalar Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
eval "$($HOME/miniconda3/bin/conda shell.bash hook)"
conda init

# Crear un entorno para vLLM
conda create -n vllm-env python=3.11 -y
conda activate vllm-env
```

### 4.3 venv y pip: gestión ligera de entornos

Para proyectos donde las dependencias son exclusivamente paquetes Python, `venv` es suficiente y más ligero:

```bash
# Crear el entorno
python3.11 -m venv /opt/llm-inference/venv

# Activar
source /opt/llm-inference/venv/bin/activate

# Actualizar pip y setuptools
pip install --upgrade pip setuptools wheel
```

### 4.4 Poetry: gestión declarativa de dependencias

**Poetry** es la herramienta recomendada para proyectos donde la reproducibilidad del entorno es crítica. Genera un fichero `poetry.lock` que fija exactamente todas las versiones de todas las dependencias transitivas:

```bash
# Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Crear un proyecto nuevo
poetry new llm-serving
cd llm-serving

# Añadir dependencias
poetry add vllm transformers accelerate

# Instalar con lock file
poetry install

# Exportar requirements.txt para Docker
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### 4.5 Comparativa de herramientas de gestión de entornos

| Herramienta | Gestiona Python | Gestiona deps no-Python | Lock file | Uso recomendado |
|---|---|---|---|---|
| venv | No | No | No | Proyectos simples, reproducción rápida |
| conda | Sí | Sí | Parcial (environment.yml) | Dependencias con componentes C/CUDA |
| pyenv | Sí | No | No | Gestión de múltiples versiones Python |
| Poetry | No | No | Sí (poetry.lock) | Proyectos con dependencias complejas Python |

---

## 5. Frameworks de inferencia

### 5.1 vLLM

**vLLM** es el framework de inferencia de LLMs de mayor rendimiento para GPU NVIDIA en servidores de producción. Desarrollado originalmente en UC Berkeley y actualmente mantenido por la comunidad y la empresa vLLM Inc., su característica diferencial es el mecanismo **PagedAttention**, que gestiona la KV cache de forma similar a la memoria virtual del sistema operativo, permitiendo una utilización muy eficiente de la memoria GPU y un throughput significativamente superior a los frameworks que no lo implementan.

```bash
# Instalación en entorno con CUDA 12.1+
pip install vllm

# Lanzar servidor de inferencia compatible con la API de OpenAI
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --tensor-parallel-size 1 \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.90 \
    --port 8000
```

### 5.2 Ollama

**Ollama** es la solución más sencilla para ejecutar LLMs en local, orientada a desarrollo y pruebas más que a producción de alto throughput. Gestiona automáticamente la descarga de modelos, la selección del backend de inferencia (llama.cpp) y la exposición de una API REST compatible en parte con la API de OpenAI:

```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Descargar y ejecutar un modelo
ollama run llama3.1:8b

# Listar modelos disponibles
ollama list

# Usar la API REST
curl http://localhost:11434/api/generate \
    -d '{"model": "llama3.1:8b", "prompt": "Explica qué es la atención multi-cabeza", "stream": false}'
```

### 5.3 llama.cpp

**llama.cpp** es una implementación en C/C++ de la inferencia de modelos LLaMA y arquitecturas derivadas, optimizada para ejecutarse en CPU (con soporte AVX2, AVX-512), así como en GPU (mediante backends CUDA, Metal, OpenCL). Es la opción de referencia cuando la GPU no está disponible o para ejecutar modelos cuantizados en hardware de consumo:

```bash
# Compilar con soporte CUDA
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release -j$(nproc)

# Ejecutar el servidor de inferencia
./build/bin/llama-server \
    --model /models/llama-3.1-8b-instruct-Q4_K_M.gguf \
    --ctx-size 8192 \
    --n-gpu-layers 40 \
    --port 8080
```

### 5.4 Text Generation Inference (TGI)

**Text Generation Inference** es el framework de inferencia de producción desarrollado por Hugging Face. Destaca por su soporte nativo de cuantización (GPTQ, AWQ, BitsAndBytes), tensor parallelism, continuous batching y una integración directa con el ecosistema de Hugging Face Hub:

```bash
# Ejecutar TGI mediante Docker (método recomendado)
docker run --gpus all \
    -v /models:/data \
    -p 8080:80 \
    ghcr.io/huggingface/text-generation-inference:2.3 \
    --model-id meta-llama/Llama-3.1-8B-Instruct \
    --max-input-tokens 8192 \
    --max-total-tokens 16384 \
    --num-shard 1
```

### 5.5 LMDeploy

**LMDeploy** es el framework de inferencia desarrollado por Shanghai AI Laboratory. Ofrece un pipeline de cuantización propio (AWQ 4-bit) y el motor de inferencia TurboMind, con soporte para modelos de la familia InternLM, Llama, Mistral y Qwen:

```bash
# Instalación
pip install lmdeploy

# Lanzar servidor
lmdeploy serve api_server meta-llama/Llama-3.1-8B-Instruct \
    --backend turbomind \
    --tp 1 \
    --server-port 23333
```

### 5.6 Comparativa de frameworks de inferencia

| Framework | Throughput | Uso en prod. | Cuantización | API OpenAI-compat. | Facilidad de uso |
|---|---|---|---|---|---|
| vLLM | Muy alto | Sí | GPTQ, AWQ, GGUF | Sí | Media |
| TGI (HuggingFace) | Alto | Sí | GPTQ, AWQ, BnB | Parcial | Media |
| LMDeploy | Alto | Sí | AWQ, W4A16 | Sí | Media |
| llama.cpp | Medio | Limitado | GGUF (Q2-Q8) | Sí (servidor) | Alta |
| Ollama | Bajo-medio | No recom. prod. | GGUF | Parcial | Muy alta |

---

## 6. Contenedorización de entornos LLM

### 6.1 NVIDIA Container Toolkit

El **NVIDIA Container Toolkit** (anteriormente nvidia-docker2) permite que los contenedores Docker accedan a las GPUs del anfitrión. Sin este componente, los contenedores están aislados del hardware de GPU y no pueden ejecutar código CUDA:

```bash
# Instalar el repositorio de NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
    sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update && sudo apt install -y nvidia-container-toolkit

# Configurar Docker para usar el runtime de NVIDIA
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Verificar acceso a GPU desde un contenedor
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

### 6.2 Dockerfile para inferencia de LLMs con GPU

Un Dockerfile bien construido para inferencia de LLMs debe seleccionar la imagen base correcta de CUDA, instalar las dependencias de sistema necesarias y el framework de inferencia, y configurar los puntos de entrada correctamente:

```dockerfile
# Imagen base: CUDA 12.4 con cuDNN sobre Ubuntu 22.04
FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

# Variables de entorno de construcción
ENV DEBIAN_FRONTEND=noninteractive
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$CUDA_HOME/bin:$PATH
ENV LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
ENV PYTHONUNBUFFERED=1

# Dependencias de sistema
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3-pip \
    git curl wget \
    && rm -rf /var/lib/apt/lists/*

# Actualizar pip e instalar vLLM
RUN python3.11 -m pip install --upgrade pip && \
    pip install vllm==0.5.4

# Directorio de trabajo y modelos
WORKDIR /app
VOLUME ["/models"]

# Exponer el puerto de la API
EXPOSE 8000

# Punto de entrada
ENTRYPOINT ["python3.11", "-m", "vllm.entrypoints.openai.api_server"]
CMD ["--model", "/models/llama-3.1-8b-instruct", "--port", "8000"]
```

### 6.3 Docker Compose para entornos de desarrollo

Docker Compose permite orquestar el contenedor de inferencia junto con servicios auxiliares (base de datos de caché, proxy, sistema de monitorización):

```yaml
# docker-compose.yml
version: "3.9"

services:
  vllm-server:
    build: .
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}
      - TRANSFORMERS_CACHE=/models/cache
    volumes:
      - /mnt/models:/models
    ports:
      - "8000:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s
    restart: unless-stopped

  nginx-proxy:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - vllm-server
```

### 6.4 Kubernetes con nvidia-device-plugin

En clústeres Kubernetes, el acceso a GPU se gestiona a través del **NVIDIA Device Plugin**, que registra las GPUs de cada nodo como recursos asignables (`nvidia.com/gpu`):

```bash
# Instalar el nvidia-device-plugin como DaemonSet
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.16.0/deployments/static/nvidia-device-plugin.yml

# Verificar que los nodos GPU tienen el recurso registrado
kubectl describe nodes | grep -A 5 "nvidia.com/gpu"
```

Un Pod de inferencia que solicita GPUs debe declarar el recurso en su manifiesto:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-inference
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vllm-inference
  template:
    metadata:
      labels:
        app: vllm-inference
    spec:
      containers:
        - name: vllm
          image: registry.empresa.com/vllm:0.5.4-cuda12.4
          resources:
            limits:
              nvidia.com/gpu: "1"
              memory: "32Gi"
              cpu: "8"
            requests:
              nvidia.com/gpu: "1"
          env:
            - name: CUDA_VISIBLE_DEVICES
              value: "0"
          ports:
            - containerPort: 8000
          volumeMounts:
            - name: models
              mountPath: /models
      volumes:
        - name: models
          persistentVolumeClaim:
            claimName: models-pvc
```

---

## 7. Gestión de modelos

### 7.1 Descarga desde Hugging Face Hub

La biblioteca `huggingface_hub` es la forma canónica de descargar modelos desde el Hub de Hugging Face. Los modelos con licencia restrictiva (Llama 3, Mistral, Gemma) requieren aceptar los términos de uso en la web del Hub y autenticarse con un token de acceso:

```bash
# Instalar la CLI de Hugging Face
pip install huggingface_hub[cli]

# Autenticarse (el token se almacena en ~/.cache/huggingface/token)
huggingface-cli login --token $HF_TOKEN

# Descargar un modelo completo a un directorio local
huggingface-cli download meta-llama/Llama-3.1-8B-Instruct \
    --local-dir /models/llama-3.1-8b-instruct \
    --local-dir-use-symlinks False
```

Desde Python, la descarga puede integrarse en scripts de configuración del entorno:

```python
from huggingface_hub import snapshot_download
import os

snapshot_download(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    local_dir="/models/llama-3.1-8b-instruct",
    token=os.environ["HF_TOKEN"],
    ignore_patterns=["*.msgpack", "*.h5", "flax_model*"]
)
```

### 7.2 Verificación de integridad con checksums

Los pesos de un modelo que se han corrompido durante la descarga pueden producir salidas incorrectas o fallos de carga difíciles de diagnosticar. La verificación de checksums SHA-256 es obligatoria antes de pasar a producción:

```bash
# Generar checksums de todos los archivos del modelo
find /models/llama-3.1-8b-instruct -type f | sort | \
    xargs sha256sum > /models/llama-3.1-8b-instruct.sha256

# Verificar integridad
sha256sum -c /models/llama-3.1-8b-instruct.sha256
```

### 7.3 Almacenamiento en NFS y S3

Para infraestructuras con múltiples nodos de inferencia, los pesos deben almacenarse en un sistema de ficheros compartido. Las opciones más comunes son NFS (Network File System) y S3 (o equivalentes compatibles como MinIO):

```bash
# Montaje de un volumen NFS para modelos compartidos
sudo mount -t nfs -o ro,vers=4,hard,timeo=600,retrans=2 \
    nas.empresa.local:/exports/models /mnt/models

# Añadir al /etc/fstab para montaje automático
echo "nas.empresa.local:/exports/models /mnt/models nfs ro,vers=4,hard,timeo=600,retrans=2 0 0" \
    | sudo tee -a /etc/fstab

# Descarga desde S3 con AWS CLI
aws s3 sync s3://empresa-modelos/llama-3.1-8b-instruct/ \
    /models/llama-3.1-8b-instruct/ \
    --region eu-west-1 \
    --no-progress
```

---

## 8. Variables de entorno críticas

### 8.1 Variables de control de GPU

Las variables de entorno de CUDA y NCCL determinan el comportamiento de la inferencia a nivel de hardware:

```bash
# Seleccionar qué GPUs son visibles para el proceso
export CUDA_VISIBLE_DEVICES=0,1          # Usar GPUs 0 y 1
export CUDA_VISIBLE_DEVICES=0            # Usar solo GPU 0
export CUDA_VISIBLE_DEVICES=""           # Deshabilitar CUDA (forzar CPU)

# Variables NCCL para comunicación multi-GPU
export NCCL_DEBUG=INFO                   # Nivel de log de NCCL (WARN, INFO, TRACE)
export NCCL_IB_DISABLE=1                 # Deshabilitar InfiniBand (usar solo Ethernet)
export NCCL_P2P_DISABLE=0               # Habilitar comunicación P2P entre GPUs
export NCCL_SOCKET_IFNAME=eth0           # Interfaz de red para NCCL
export NCCL_TIMEOUT=1800                 # Timeout de operaciones colectivas en segundos

# Optimización de memoria CUDA
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

### 8.2 Variables de caché y configuración de Transformers

```bash
# Directorio de caché de modelos de Hugging Face
export TRANSFORMERS_CACHE=/mnt/models/cache/transformers
export HF_HOME=/mnt/models/cache/hf_home
export HUGGING_FACE_HUB_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx

# Deshabilitar telemetría de Hugging Face (recomendado en producción)
export HF_HUB_DISABLE_TELEMETRY=1
export TOKENIZERS_PARALLELISM=false      # Evitar deadlocks con fork + tokenizadores
```

---

## 9. Pruebas de smoke test

### 9.1 Primera inferencia y verificación de GPU

Una vez instalado el entorno, se debe ejecutar una prueba de smoke test que valide el funcionamiento end-to-end:

```python
#!/usr/bin/env python3
"""Smoke test del entorno de inferencia LLM."""
import subprocess
import requests
import json
import time

def check_gpu():
    """Verifica que CUDA está disponible."""
    result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                             "--format=csv,noheader"], capture_output=True, text=True)
    print(f"[GPU] {result.stdout.strip()}")
    assert result.returncode == 0, "nvidia-smi falló"

def check_cuda_python():
    """Verifica CUDA desde PyTorch."""
    import torch
    assert torch.cuda.is_available(), "CUDA no disponible desde PyTorch"
    print(f"[CUDA] PyTorch: {torch.__version__}, CUDA: {torch.version.cuda}")
    print(f"[CUDA] GPU disponible: {torch.cuda.get_device_name(0)}")

def check_inference_api(base_url="http://localhost:8000"):
    """Realiza una inferencia de prueba y verifica la respuesta."""
    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": [{"role": "user", "content": "Di 'Hola mundo' y nada más."}],
        "max_tokens": 20,
        "temperature": 0
    }
    start = time.time()
    resp = requests.post(f"{base_url}/v1/chat/completions",
                         json=payload, timeout=60)
    latency = time.time() - start
    assert resp.status_code == 200, f"Error HTTP: {resp.status_code}"
    content = resp.json()["choices"][0]["message"]["content"]
    print(f"[API] Respuesta: '{content}' — Latencia: {latency:.2f}s")
    assert len(content) > 0, "Respuesta vacía"

if __name__ == "__main__":
    check_gpu()
    check_cuda_python()
    check_inference_api()
    print("\n[OK] Smoke test completado correctamente.")
```

---

## 10. Actividades prácticas

### Actividad 1 — Instalación y verificación del stack base

**Descripción**: Sobre una máquina virtual Ubuntu Server 22.04 proporcionada por el formador (con GPU NVIDIA simulada mediante passthrough o acceso a instancia cloud), instala el driver NVIDIA, CUDA Toolkit 12.4 y cuDNN 9. Crea un entorno Python con pyenv + venv, instala PyTorch y verifica que CUDA está disponible. Documenta cada paso con los comandos ejecutados y las salidas obtenidas.

**Entregable**: Documento con comandos, salidas de `nvidia-smi`, `nvcc --version` y el resultado de `torch.cuda.is_available()`.

**Criterios de evaluación**: Correcta instalación de cada capa del stack, ausencia de conflictos de versiones, documentación clara de cada paso y verificación exitosa de la disponibilidad de CUDA.

---

### Actividad 2 — Despliegue de servidor de inferencia con vLLM

**Descripción**: Utilizando el entorno del ejercicio anterior, instala vLLM y descarga un modelo de tamaño adecuado para el hardware disponible (mínimo 7B, cuantizado si es necesario). Configura el servidor de inferencia con los parámetros de producción (tensor-parallel-size, max-model-len, gpu-memory-utilization). Ejecuta el smoke test proporcionado y documenta los resultados de la primera inferencia y la utilización de GPU durante la misma (monitorizada con `nvidia-smi dmon`).

**Entregable**: Comando de lanzamiento del servidor, salida del smoke test y gráfica o tabla de utilización de GPU durante la inferencia.

**Criterios de evaluación**: Servidor funcionando con la API compatible con OpenAI, respuesta correcta en la primera inferencia, utilización de GPU superior al 70% durante la inferencia, documentación del proceso.

---

### Actividad 3 — Contenedorización del entorno con Docker y GPU

**Descripción**: Construye una imagen Docker que empaquete el servidor vLLM con las dependencias necesarias. El Dockerfile debe partir de una imagen base oficial de CUDA, instalar las dependencias de sistema y Python, y configurar el punto de entrada del servidor. Crea un fichero docker-compose.yml que monte el directorio de modelos como volumen y configure el acceso a GPU. Documenta el proceso de construcción y la verificación del acceso a GPU desde dentro del contenedor.

**Entregable**: Dockerfile, docker-compose.yml y evidencia del contenedor en ejecución con acceso a GPU (`docker exec ... nvidia-smi`).

**Criterios de evaluación**: Imagen construida correctamente, contenedor con acceso a GPU verificado, volumen de modelos montado correctamente, servidor respondiendo desde fuera del contenedor.

---

### Actividad 4 — Gestión de modelos y verificación de integridad

**Descripción**: Descarga un modelo desde Hugging Face Hub utilizando la CLI con autenticación mediante token. Genera los checksums SHA-256 de todos los ficheros del modelo y almacénalos en un fichero de manifiesto. Simula una corrupción de uno de los ficheros y verifica que el proceso de comprobación de checksums detecta la corrupción. Documenta el procedimiento de descarga segura y verificación que aplicarías en un entorno de producción.

**Entregable**: Script de descarga y verificación, fichero de checksums generado, evidencia de la detección de la corrupción simulada y procedimiento documentado.

**Criterios de evaluación**: Descarga correcta con autenticación, checksums generados para todos los ficheros, detección correcta de la corrupción simulada, procedimiento de producción coherente y completo.

---

## 11. Referencias

- **NVIDIA CUDA Toolkit Documentation**: guía oficial de instalación y referencia de la API. Disponible en: [https://docs.nvidia.com/cuda/](https://docs.nvidia.com/cuda/)

- **NVIDIA Container Toolkit — Guía de instalación**: documentación oficial del toolkit para contenedores Docker. Disponible en: [https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

- **vLLM — Documentación oficial**: guía de instalación, parámetros del servidor y referencia de la API. Disponible en: [https://docs.vllm.ai/en/latest/](https://docs.vllm.ai/en/latest/)

- **Text Generation Inference — Documentación de HuggingFace**: guía de despliegue, configuración y API de TGI. Disponible en: [https://huggingface.co/docs/text-generation-inference](https://huggingface.co/docs/text-generation-inference)

- **llama.cpp — Repositorio oficial**: código fuente, instrucciones de compilación y documentación. Disponible en: [https://github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp)

- **Ollama — Documentación oficial**: guía de instalación, referencia de la API REST y catálogo de modelos. Disponible en: [https://ollama.com/docs](https://ollama.com/docs)

- **LMDeploy — Documentación oficial**: instalación, cuantización y servidor de inferencia. Disponible en: [https://lmdeploy.readthedocs.io/en/latest/](https://lmdeploy.readthedocs.io/en/latest/)

- **Hugging Face Hub — Referencia de la CLI y biblioteca Python**: descarga de modelos, autenticación y gestión de repositorios. Disponible en: [https://huggingface.co/docs/huggingface_hub/index](https://huggingface.co/docs/huggingface_hub/index)

- **NVIDIA Device Plugin para Kubernetes**: documentación del plugin para asignación de GPU en pods. Disponible en: [https://github.com/NVIDIA/k8s-device-plugin](https://github.com/NVIDIA/k8s-device-plugin)

- **Poetry — Documentación oficial**: gestión de dependencias y entornos virtuales Python. Disponible en: [https://python-poetry.org/docs/](https://python-poetry.org/docs/)

- **pyenv — Repositorio y documentación**: gestión de múltiples versiones de Python. Disponible en: [https://github.com/pyenv/pyenv](https://github.com/pyenv/pyenv)

- **NCCL — NVIDIA Collective Communications Library**: documentación de variables de entorno y configuración. Disponible en: [https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/)

---

*UD3 · MP04 Infraestructura para la ejecución de LLMs · CFS2 Instalación, despliegue y explotación de sistemas de IA*
