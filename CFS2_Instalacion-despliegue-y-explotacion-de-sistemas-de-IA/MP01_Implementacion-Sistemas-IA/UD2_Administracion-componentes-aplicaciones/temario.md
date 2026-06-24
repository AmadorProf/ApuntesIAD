# UD2 · Administración de componentes de aplicaciones de IA

---

## 1. Introducción — la pila de software de un sistema de IA: capas y responsabilidades

Un sistema de inteligencia artificial en producción no es únicamente un modelo entrenado. Es el resultado de la interacción coordinada de múltiples capas de software, cada una con responsabilidades bien delimitadas y con dependencias estrictas hacia las capas inferiores. Comprender esta pila en su totalidad es la base de cualquier labor de administración eficaz.

En la capa más baja se encuentra el **hardware**: las GPUs o aceleradores especializados (TPUs, NPUs) que ejecutan los cálculos matriciales del entrenamiento e inferencia. Sobre el hardware opera el **driver del fabricante**, que expone el dispositivo al sistema operativo. Encima del driver reside el **runtime de aceleración** (CUDA en el ecosistema NVIDIA), que proporciona las primitivas de cómputo paralelo. Por encima de ese runtime operan las **bibliotecas de alto nivel** (cuDNN, cuBLAS, NCCL) que implementan operaciones optimizadas para redes neuronales. Finalmente, los **frameworks de IA** (PyTorch, TensorFlow, JAX) se apoyan en esas bibliotecas y ofrecen la interfaz con la que trabajan los ingenieros de modelos.

Sobre toda esa base vertical existe una capa horizontal de **gestión de entornos y dependencias** que garantiza reproducibilidad: gestores de paquetes, entornos virtuales y contenedores. Y por encima de los contenedores, los **orquestadores** (Kubernetes) gestionan el ciclo de vida de múltiples instancias en clústeres heterogéneos.

El administrador de sistemas de IA debe dominar todas estas capas porque un fallo en cualquiera de ellas —una versión incompatible de cuDNN, un driver desactualizado, un conflicto de dependencias de Python— puede hacer que una aplicación deje de funcionar o que su rendimiento se degrade sin aviso. Este temario recorre esa pila de abajo arriba, con énfasis en las tareas operativas cotidianas: instalación, configuración, verificación y solución de problemas.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad didáctica el alumnado será capaz de:

- Gestionar dependencias de proyectos Python con pip, pip-tools, conda y Poetry, eligiendo el gestor adecuado según el contexto.
- Crear, activar y mantener entornos virtuales aislados con venv, virtualenv y conda.
- Construir imágenes Docker optimizadas para cargas de trabajo de IA, utilizando imágenes base oficiales de NVIDIA y técnicas de multi-stage build.
- Configurar el NVIDIA Container Toolkit para permitir el acceso a GPUs desde contenedores.
- Instalar y verificar la pila de software NVIDIA (driver, CUDA Toolkit, cuDNN) en sistemas Ubuntu, resolviendo los problemas de compatibilidad más frecuentes.
- Desplegar cargas de trabajo de IA en Kubernetes, incluyendo la configuración del NVIDIA GPU Operator, el uso de MIG y el time-slicing.
- Monitorizar el estado y el rendimiento de GPUs con nvidia-smi, DCGM y paneles de Grafana.
- Gestionar configuraciones de aplicaciones de forma segura mediante variables de entorno, ConfigMaps, Secrets de Kubernetes y HashiCorp Vault.

---

## 3. Gestión de paquetes y dependencias

### 3.1 pip: el instalador estándar de Python

pip es el gestor de paquetes oficial de Python y el punto de entrada más común en cualquier proyecto. Su dominio va más allá del simple `pip install nombre-paquete`.

**Flags esenciales:**

- `--upgrade` / `-U`: actualiza el paquete (y sus dependencias) a la versión más reciente disponible en el índice. Conviene usarlo con cuidado en entornos de producción, ya que puede romper compatibilidades. Ejemplo: `pip install --upgrade torch`.
- `--constraint` / `-c`: aplica un archivo de restricciones que impone límites de versión sin instalar los paquetes si no están ya presentes. Es útil para garantizar que las actualizaciones transitivas no superen ciertos umbrales: `pip install -r requirements.txt -c constraints.txt`.
- `--index-url` / `-i`: cambia el índice de paquetes. Imprescindible cuando se trabaja con registros privados (Artifactory, Nexus) o con el índice específico de NVIDIA para PyTorch con soporte CUDA: `pip install torch --index-url https://download.pytorch.org/whl/cu121`.
- `--extra-index-url`: añade un índice adicional sin sustituir el principal. Útil cuando la mayoría de paquetes vienen del PyPI público pero algunos proceden de un registro privado.
- `--no-cache-dir`: deshabilita la caché local. Necesario en pipelines de CI/CD donde la caché puede causar comportamientos no deterministas.

**Archivo requirements.txt:** lista paquetes con sus versiones exactas (`torch==2.3.0`). La práctica recomendada es distinguir entre dependencias directas (las que el proyecto usa explícitamente) e indirectas (las que instalan las directas). Mezclarlas en el mismo archivo dificulta el mantenimiento.

### 3.2 pip-tools: lockfiles reproducibles

pip-tools resuelve el problema de la reproducibilidad sin la complejidad de un gestor completo. Su flujo de trabajo se basa en dos archivos:

- `requirements.in`: contiene solo las dependencias directas del proyecto, con restricciones amplias si es necesario (por ejemplo, `torch>=2.0`). Es el archivo que mantiene el desarrollador.
- `requirements.txt`: generado automáticamente por pip-tools con todas las dependencias (directas e indirectas) fijadas a versiones exactas con hashes de integridad. No se edita manualmente.

El comando principal es `pip-compile requirements.in`, que resuelve el grafo de dependencias y produce el lockfile. Para actualizar una dependencia específica: `pip-compile --upgrade-package torch requirements.in`. Para instalar exactamente lo especificado en el lockfile: `pip-sync requirements.txt`.

La ventaja sobre un requirements.txt manual es que pip-tools verifica hashes (con `--generate-hashes`), lo que garantiza la integridad de los paquetes descargados.

### 3.3 conda: gestión de entornos y paquetes científicos

conda es a la vez gestor de paquetes y gestor de entornos. A diferencia de pip, puede instalar paquetes que no son Python (compiladores, CUDA Toolkit, bibliotecas C/C++), lo que lo hace especialmente valioso en el ecosistema científico.

**Channels (canales):** son los repositorios de paquetes de conda. El canal `defaults` es el oficial de Anaconda. `conda-forge` es una comunidad que mantiene paquetes más actualizados y con mayor variedad. Para priorizar conda-forge: `conda config --add channels conda-forge`. El orden de los canales en `.condarc` determina la prioridad de búsqueda.

**Gestión de entornos:**

```bash
# Crear entorno con Python específico
conda create --name mi-entorno python=3.11

# Activar
conda activate mi-entorno

# Instalar paquetes
conda install numpy pandas scikit-learn

# Exportar entorno (incluye todos los paquetes instalados)
conda env export > environment.yml

# Exportar solo las dependencias explícitas (más portable entre plataformas)
conda env export --from-history > environment-minimal.yml

# Recrear entorno desde archivo
conda env create -f environment.yml
```

Un problema frecuente de conda es la lentitud del solver. Mamba (un reimplementación en C++) lo resuelve siendo compatible con la misma interfaz: `mamba install paquete` en lugar de `conda install paquete`.

### 3.4 Poetry: gestión moderna de proyectos Python

Poetry combina gestión de dependencias, empaquetado y publicación en una única herramienta. Su fichero central es `pyproject.toml`, el estándar moderno definido en PEP 518.

**pyproject.toml:** declara las dependencias directas con restricciones de versión usando la sintaxis de Poetry (`^1.2` significa compatible con 1.2 pero menor que 2.0). **poetry.lock:** lockfile generado automáticamente que fija todas las dependencias (directas e indirectas) con sus hashes.

**Grupos de dependencias:** Poetry permite separar dependencias por contexto:

```toml
[tool.poetry.dependencies]
python = "^3.11"
torch = "^2.3"
transformers = "^4.40"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
black = "^24.0"
mypy = "^1.10"

[tool.poetry.group.docs.dependencies]
mkdocs = "^1.6"
```

Los grupos de desarrollo no se instalan en producción (`poetry install --without dev`). Esto permite tener un único repositorio de configuración sin contaminar los entornos de producción con herramientas de desarrollo.

Comandos esenciales: `poetry add paquete`, `poetry remove paquete`, `poetry update`, `poetry install`, `poetry shell` (activa el entorno virtual gestionado por Poetry).

### 3.5 Comparativa de gestores

| Criterio | pip + pip-tools | conda | Poetry |
|---|---|---|---|
| Paquetes no-Python | No | Sí | No |
| Lockfile automático | Sí (pip-compile) | Parcial (environment.yml) | Sí (poetry.lock) |
| Gestión de entornos | No (necesita venv) | Sí | Sí |
| Velocidad de resolución | Alta | Baja (mamba: alta) | Media |
| Empaquetado y publicación | No | No | Sí |
| Ecosistema científico | Limitado | Excelente | Limitado |

La recomendación práctica: usar conda cuando se necesiten paquetes no-Python o se trabaje en ciencia de datos pura; Poetry para proyectos de software que se publicarán como librerías; pip + pip-tools para proyectos simples o en entornos donde conda no está disponible.

### 3.6 Resolución de conflictos de dependencias

Un conflicto de dependencias ocurre cuando dos paquetes requieren versiones incompatibles de un tercero. Los síntomas típicos son errores de tipo `ResolutionImpossible` (Poetry) o `ERROR: pip's dependency resolver does not currently take into account all the packages that are installed` (pip).

Estrategias de resolución:

1. **Identificar la raíz del conflicto:** `pip show paquete` muestra las dependencias directas. `pipdeptree` (herramienta externa) visualiza el árbol completo de dependencias.
2. **Fijar versiones intermedias:** si el paquete A requiere `numpy<1.25` y el paquete B requiere `numpy>=1.25`, hay que buscar una versión de A o B que amplíe su rango de compatibilidad.
3. **Actualizar todos los paquetes:** a veces el conflicto desaparece al actualizar todo a versiones recientes que ya resolvieron la incompatibilidad.
4. **Separar entornos:** si la incompatibilidad es irresoluble, separar los componentes en entornos o contenedores distintos.

---

## 4. Entornos virtuales y contenedores

### 4.1 venv y virtualenv

Un entorno virtual es un directorio que contiene una instalación de Python aislada del sistema. Los paquetes instalados en él no afectan al Python del sistema ni a otros entornos.

**venv** (módulo estándar desde Python 3.3):

```bash
# Crear entorno
python3 -m venv .venv

# Activar (Linux/macOS)
source .venv/bin/activate

# Activar (Windows)
.venv\Scripts\activate

# Desactivar
deactivate

# Eliminar (simplemente borrar el directorio)
rm -rf .venv
```

Buenas prácticas: nombrar el entorno `.venv` y añadirlo al `.gitignore`. No mover el directorio del entorno porque las rutas absolutas quedan fijadas al crearlo. Usar el entorno solo para el proyecto al que pertenece.

**virtualenv** es una herramienta externa que extiende venv con funcionalidades adicionales: soporte para Python 2, creación más rápida y la posibilidad de instalar paquetes en el entorno sin activarlo (`virtualenv .venv && .venv/bin/pip install paquete`). Se instala con `pip install virtualenv`.

### 4.2 Docker para IA

Docker permite empaquetar una aplicación con todas sus dependencias en una imagen portable. En el contexto de IA, la ventaja principal es garantizar que el entorno de desarrollo y el de producción son idénticos, incluyendo versiones de CUDA y cuDNN.

**Imágenes base de NVIDIA (nvcr.io):** NVIDIA mantiene en su Container Registry (`nvcr.io`) imágenes base oficiales que incluyen drivers parciales, CUDA Toolkit y cuDNN preinstalados. Las principales familias son:

- `nvcr.io/nvidia/cuda`: imagen base con CUDA y cuDNN. Ejemplo: `nvcr.io/nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04`.
- `nvcr.io/nvidia/pytorch`: PyTorch preinstalado con optimizaciones NVIDIA. Ejemplo: `nvcr.io/nvidia/pytorch:24.05-py3`.
- `nvcr.io/nvidia/tensorflow`: equivalente para TensorFlow.

Las variantes de las imágenes CUDA siguen el patrón `versión-tipo-SO`, donde el tipo puede ser:
- `base`: solo CUDA runtime, sin cuDNN.
- `runtime`: CUDA runtime + cuDNN runtime (para inferencia).
- `devel`: CUDA runtime + cuDNN + headers y compilador nvcc (para compilar extensiones CUDA).

En producción, preferir `runtime` sobre `devel` para reducir el tamaño de la imagen.

**Multi-stage builds:** técnica que usa múltiples bloques `FROM` en un Dockerfile para separar la etapa de compilación de la de ejecución. El resultado es una imagen final más pequeña y sin herramientas de desarrollo:

```dockerfile
# Etapa de construcción
FROM nvcr.io/nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04 AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/install -r requirements.txt

# Etapa de producción
FROM nvcr.io/nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04
WORKDIR /app
COPY --from=builder /install /usr/local/lib/python3.11/dist-packages
COPY src/ .
CMD ["python", "serve.py"]
```

**Optimización de capas:** cada instrucción `RUN`, `COPY` o `ADD` crea una capa. Docker cachea las capas y solo reconstruye desde la primera capa modificada. Para aprovechar la caché: copiar primero los archivos de dependencias (requirements.txt) e instalarlos antes de copiar el código fuente. El código cambia con frecuencia; las dependencias, menos. Consolidar comandos relacionados en un único `RUN` con `&&` y limpiar artefactos en el mismo comando para no añadir capas con archivos temporales.

**nvidia-container-toolkit:** para que un contenedor Docker acceda a las GPUs del host se necesita el NVIDIA Container Toolkit. Instalación en Ubuntu:

```bash
# Añadir repositorio de NVIDIA
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Para usar GPUs en un contenedor: `docker run --gpus all imagen-ia python script.py`. La flag `--gpus all` expone todas las GPUs disponibles. Para limitar: `--gpus '"device=0,1"'`.

**Ejemplo de Dockerfile para aplicación de inferencia:**

```dockerfile
FROM nvcr.io/nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-pip python3.11-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias Python (capa separada para aprovechar caché)
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/
COPY models/ ./models/

# Usuario no-root por seguridad
RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8080/health || exit 1
CMD ["python3", "src/server.py"]
```

---

## 5. CUDA, cuDNN y drivers NVIDIA

### 5.1 La pila de software NVIDIA

Comprender la relación entre componentes es esencial para diagnosticar problemas. La pila de abajo arriba:

1. **Driver NVIDIA:** comunica el SO con el hardware GPU. El número de versión del driver determina la versión máxima de CUDA compatible (compatibilidad hacia atrás). Un driver 525.x soporta hasta CUDA 12.0; un driver 545.x soporta hasta CUDA 12.3.
2. **CUDA Toolkit:** incluye el compilador `nvcc`, bibliotecas como cuBLAS y cuFFT, y el runtime de CUDA que los programas enlazados dinámicamente usan en tiempo de ejecución.
3. **cuDNN:** biblioteca de primitivas para redes neuronales profundas (convoluciones, recurrencias, normalización). Cada versión de cuDNN requiere una versión mínima de CUDA.
4. **Framework de IA:** PyTorch, TensorFlow, JAX. Cada versión del framework está compilada contra versiones específicas de CUDA y cuDNN.

La regla fundamental: el driver del sistema debe ser igual o superior a la versión mínima requerida por la versión de CUDA que use el framework. Verificar siempre la matriz de compatibilidad oficial antes de instalar cualquier componente.

### 5.2 Compatibilidad de versiones

NVIDIA publica en su documentación tablas de compatibilidad entre driver, CUDA, cuDNN y los frameworks. PyTorch también publica su propia tabla. Los puntos clave:

- Un driver más nuevo es compatible con versiones de CUDA más antiguas (retrocompatibilidad), pero no al revés.
- CUDA 12.x y CUDA 11.x no son intercambiables desde el punto de vista del código compilado, pero el runtime de CUDA 12.x puede ejecutar código compilado con CUDA 11.x (Forward Compatibility).
- cuDNN 8.x y cuDNN 9.x tienen APIs diferentes; los frameworks indican cuál necesitan.

Herramienta práctica: antes de instalar un framework, consultar `https://pytorch.org/get-started/locally/` o la documentación equivalente de TensorFlow para obtener el comando de instalación exacto con la versión de CUDA correcta.

### 5.3 Instalación de drivers en Ubuntu

Existen dos métodos principales:

**apt (recomendado para servidores):**
```bash
# Identificar el driver recomendado
ubuntu-drivers devices

# Instalar automáticamente el recomendado
sudo ubuntu-drivers autoinstall

# O instalar una versión específica
sudo apt-get install -y nvidia-driver-545
sudo reboot
```

**Runfile (control total):** descarga un instalador `.run` desde el sitio de NVIDIA. Requiere desactivar Nouveau (el driver open-source), salir del entorno gráfico y ejecutar el instalador en modo texto. Es más complejo pero permite instalar versiones exactas no disponibles en los repositorios apt.

### 5.4 Configuración de CUDA Toolkit

El CUDA Toolkit se instala independientemente del driver en versiones recientes. Desde el CUDA Toolkit 11.4, el driver puede instalarse por separado:

```bash
# Añadir repositorio de CUDA (ejemplo para Ubuntu 22.04, CUDA 12.1)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get install -y cuda-toolkit-12-1

# Añadir al PATH
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### 5.5 Verificación

Comandos de verificación imprescindibles:

```bash
# Ver driver instalado, versión de CUDA soportada y estado de las GPUs
nvidia-smi

# Ver versión del compilador CUDA instalado
nvcc --version

# Ver información detallada de cada GPU
nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv

# Verificar desde Python que PyTorch detecta las GPUs
python3 -c "import torch; print(torch.cuda.is_available()); print(torch.version.cuda)"
```

### 5.6 Problemas comunes de compatibilidad

- **nvidia-smi funciona pero torch.cuda.is_available() devuelve False:** el framework fue instalado con soporte CPU-only. Reinstalar con el índice de PyTorch correcto para CUDA.
- **CUDA driver version is insufficient for CUDA runtime version:** el driver es más antiguo que la versión de CUDA requerida. Actualizar el driver.
- **libcuda.so.1: cannot open shared object file:** el `LD_LIBRARY_PATH` no incluye `/usr/local/cuda/lib64`. Añadirlo al perfil del shell.
- **Módulo nvidia-smi no encontrado:** el driver no está instalado o no se reinició el sistema tras la instalación.

---

## 6. Kubernetes para cargas de trabajo de IA

### 6.1 Pods y Deployments para aplicaciones ML

Kubernetes organiza los contenedores en Pods (la unidad mínima de despliegue). Para aplicaciones de IA en producción se usan Deployments (para servicios de inferencia sin estado) o Jobs/CronJobs (para tareas de entrenamiento o procesamiento por lotes).

Un Deployment básico para un servidor de inferencia:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inference-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: inference-server
  template:
    metadata:
      labels:
        app: inference-server
    spec:
      containers:
      - name: inference
        image: mi-registro/inference-server:v1.2
        resources:
          requests:
            memory: "8Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
          limits:
            memory: "16Gi"
            cpu: "8"
            nvidia.com/gpu: "1"
        env:
        - name: MODEL_PATH
          value: /models/bert-large
```

La clave `nvidia.com/gpu` en `resources.requests` y `resources.limits` indica a Kubernetes cuántas GPUs necesita el contenedor. Kubernetes garantiza que el pod solo se schedule en un nodo que tenga GPUs disponibles.

### 6.2 NVIDIA GPU Operator

El GPU Operator automatiza la gestión de todos los componentes del software NVIDIA en un clúster Kubernetes: drivers, CUDA, Device Plugin, DCGM, nvidia-container-toolkit y MIG Manager. Sin él, cada nodo del clúster requeriría configuración manual.

**Instalación con Helm:**

```bash
# Añadir repositorio de Helm de NVIDIA
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

# Instalar el GPU Operator en el namespace gpu-operator
helm install --wait --generate-name \
  -n gpu-operator --create-namespace \
  nvidia/gpu-operator
```

El GPU Operator usa un DaemonSet para desplegar componentes en cada nodo con GPU. Una vez instalado, los pods pueden solicitar GPUs sin configuración adicional en los nodos.

**Node Feature Discovery (NFD):** componente que detecta automáticamente las características del hardware de cada nodo (modelo de GPU, capacidades CUDA, etc.) y las expone como labels de Kubernetes. El GPU Operator usa estas labels para tomar decisiones de scheduling. Se puede instalar de forma independiente o como dependencia del GPU Operator.

### 6.3 MIG (Multi-Instance GPU)

MIG es una tecnología de NVIDIA disponible en GPUs A100, A30 y H100 que permite particionar físicamente una GPU en instancias independientes con recursos de cómputo y memoria garantizados y aislados. Cada instancia funciona como una GPU independiente desde el punto de vista del software.

Los perfiles MIG definen el tamaño de la instancia. En una A100 80GB, los perfiles disponibles incluyen: `1g.10gb` (1/7 de los SMs, 10GB), `2g.20gb`, `3g.40gb`, `4g.40gb`, `7g.80gb` (GPU completa). Se pueden combinar distintos perfiles en la misma GPU.

Configuración de MIG en Kubernetes con el GPU Operator:

```bash
# Etiquetar nodo para habilitar MIG
kubectl label node <nodo> nvidia.com/mig.config=all-1g.10gb --overwrite
```

El MIG Manager (parte del GPU Operator) aplica automáticamente el perfil de particionamiento al nodo etiquetado. Los pods pueden solicitar instancias MIG específicas:

```yaml
resources:
  limits:
    nvidia.com/mig-1g.10gb: 1
```

### 6.4 Time-slicing

Para GPUs que no soportan MIG (RTX, A10, T4), Kubernetes puede configurar time-slicing: múltiples pods comparten la misma GPU mediante multiplexación temporal. A diferencia de MIG, no hay aislamiento de memoria real, pero permite mayor densidad de cargas de inferencia ligeras.

Configuración mediante ConfigMap en el GPU Operator:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: time-slicing-config
data:
  a10: |-
    version: v1
    sharing:
      timeSlicing:
        resources:
        - name: nvidia.com/gpu
          replicas: 4
```

Con esta configuración, Kubernetes verá cada GPU A10 del clúster como si fueran 4 GPUs. Los pods que soliciten `nvidia.com/gpu: 1` podrán schedulearse hasta 4 por GPU física.

---

## 7. Monitorización de recursos

### 7.1 nvidia-smi

`nvidia-smi` (NVIDIA System Management Interface) es la herramienta de línea de comandos básica para inspeccionar el estado de las GPUs. Algunos flags y modos útiles:

```bash
# Estado completo de todas las GPUs
nvidia-smi

# Consulta personalizada en formato CSV
nvidia-smi --query-gpu=index,name,utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,power.draw --format=csv,noheader,nounits

# Modo de monitorización continua (se actualiza cada 1 segundo)
nvidia-smi dmon -s pucvmet -d 1

# Listar procesos que usan GPU con su consumo de memoria
nvidia-smi --query-compute-apps=pid,used_memory --format=csv

# Modo persistencia: mantiene el driver activo entre usos (reduce latencia de inicialización)
sudo nvidia-smi -pm 1
```

El modo dmon (`dmon` = device monitor) es especialmente útil para observar el comportamiento de las GPUs durante entrenamientos o cargas de inferencia, mostrando utilización de compute, memoria y encoder/decoder en tiempo real.

### 7.2 DCGM y dcgm-exporter

DCGM (Data Center GPU Manager) es la herramienta de NVIDIA para monitorización avanzada en entornos de producción. Proporciona métricas más detalladas que nvidia-smi, incluyendo contadores de rendimiento de hardware, diagnósticos y detección de errores ECC.

**dcgm-exporter** expone las métricas de DCGM en formato Prometheus. En Kubernetes, se despliega como DaemonSet (un pod por nodo con GPU) y el GPU Operator puede instalarlo automáticamente.

Las métricas más relevantes que expone dcgm-exporter:
- `DCGM_FI_DEV_GPU_UTIL`: utilización del GPU en porcentaje.
- `DCGM_FI_DEV_MEM_COPY_UTIL`: utilización del bus de memoria.
- `DCGM_FI_DEV_FB_USED`: memoria de framebuffer usada (MB).
- `DCGM_FI_DEV_GPU_TEMP`: temperatura de la GPU (°C).
- `DCGM_FI_DEV_POWER_USAGE`: consumo de energía (W).
- `DCGM_FI_DEV_ECC_SBE_VOL_TOTAL`: errores ECC de bit único (indicador de hardware degradado).
- `DCGM_FI_PROF_GR_ENGINE_ACTIVE`: fracción de tiempo que el motor gráfico estuvo activo (medida más precisa que GPU_UTIL para cargas ML).

### 7.3 Grafana dashboards para GPUs

La arquitectura de monitorización estándar en Kubernetes para IA combina: DCGM + dcgm-exporter → Prometheus → Grafana.

NVIDIA proporciona dashboards de Grafana preconfigurados en su repositorio de GitHub (`https://github.com/NVIDIA/dcgm-exporter`). El dashboard principal (`dcgm-exporter-dashboard.json`) incluye paneles para:
- Utilización de GPU por nodo y por pod.
- Memoria GPU usada y disponible.
- Temperatura por GPU.
- Consumo de energía.
- Errores ECC acumulados.

Para importar el dashboard en Grafana: Dashboards → Import → cargar el JSON o introducir el ID del dashboard en Grafana.com.

### 7.4 Alertas

Las alertas se configuran en Prometheus mediante PrometheusRules. Ejemplos relevantes:

```yaml
- alert: GPUTemperaturaAlta
  expr: DCGM_FI_DEV_GPU_TEMP > 85
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "GPU {{ $labels.gpu }} en nodo {{ $labels.node }} supera 85°C"

- alert: GPUMemoriaLlena
  expr: (DCGM_FI_DEV_FB_USED / DCGM_FI_DEV_FB_FREE) > 0.95
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "Memoria GPU al {{ $value | humanizePercentage }}"

- alert: GPUUtilizacionBaja
  expr: DCGM_FI_DEV_GPU_UTIL < 20
  for: 15m
  labels:
    severity: info
  annotations:
    summary: "GPU infrautilizada: posible problema de pipeline de datos"
```

### 7.5 Node Exporter para CPU, RAM y disco

Las GPUs no operan solas. El cuello de botella en muchos sistemas de IA es la CPU (preprocesamiento de datos), la RAM o el disco (carga de datasets). Node Exporter es el agente estándar de Prometheus para estas métricas. Se despliega también como DaemonSet y expone métricas del sistema operativo del nodo.

---

## 8. Gestión de configuración

### 8.1 Variables de entorno vs archivos de configuración

Las variables de entorno son el mecanismo más simple para parametrizar aplicaciones. Son accesibles desde cualquier lenguaje, no requieren archivos adicionales y están soportadas nativamente por Docker y Kubernetes. Son adecuadas para valores que cambian entre entornos (desarrollo, staging, producción) y para secretos sencillos en entornos no críticos.

Los archivos de configuración (YAML, TOML, JSON) son preferibles cuando la configuración es compleja (estructuras jerárquicas, listas) o cuando se necesita validación de esquema. La práctica recomendada es combinar ambos: los archivos de configuración contienen la estructura, y las variables de entorno sobreescriben valores específicos, siguiendo el principio de las doce-factor apps.

### 8.2 ConfigMaps y Secrets en Kubernetes

**ConfigMaps** almacenan configuración no sensible. Pueden montarse como volúmenes (archivos) o exponerse como variables de entorno en los pods.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: inference-config
data:
  MODEL_NAME: "bert-large-uncased"
  MAX_BATCH_SIZE: "32"
  LOG_LEVEL: "INFO"
  config.yaml: |
    model:
      path: /models/bert-large
      precision: fp16
    server:
      port: 8080
      workers: 4
```

**Secrets** almacenan datos sensibles (contraseñas, tokens de API, certificados). Kubernetes los almacena codificados en base64 (no cifrados por defecto) y los monta como volúmenes tmpfs (en memoria) o variables de entorno.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: model-registry-credentials
type: Opaque
data:
  username: dXN1YXJpbw==   # base64 de "usuario"
  password: c2VjcmV0bw==   # base64 de "secreto"
```

### 8.3 Gestión avanzada de secretos

El problema con los Secrets de Kubernetes es que, por defecto, se almacenan sin cifrar en etcd. Para entornos de producción existen dos enfoques principales:

**Cifrado de etcd en reposo:** Kubernetes soporta cifrado de los datos en etcd mediante `EncryptionConfiguration`. El plano de control cifra los Secrets antes de escribirlos y los descifra al leerlos. Transparente para los pods, pero protege contra acceso físico al almacenamiento.

**HashiCorp Vault:** solución dedicada a la gestión de secretos. Vault almacena secretos cifrados, gestiona su rotación, audita todos los accesos y los inyecta en los pods mediante el agente de Vault (sidecar) o el CSI Provider. El flujo típico: el pod se autentica en Vault usando su ServiceAccount de Kubernetes; Vault verifica la identidad con la API de Kubernetes; si es válida, devuelve los secretos al agente que los escribe en un volumen en memoria accesible al contenedor principal.

Ventajas de Vault: rotación automática de secretos, auditoría detallada, políticas de acceso granulares y soporte para secretos dinámicos (credenciales de base de datos generadas al vuelo con TTL corto).

### 8.4 Configuración dinámica sin reinicio

En aplicaciones de inferencia de larga vida, a veces es necesario cambiar parámetros (umbral de confianza, tamaño de batch, modelo activo) sin reiniciar el servicio, porque el reinicio implica cargar el modelo en memoria de GPU (proceso costoso que puede tardar minutos).

Técnicas habituales:

- **Polling de ConfigMap:** la aplicación lee el ConfigMap montado como volumen periódicamente. Kubernetes actualiza automáticamente el contenido del volumen cuando el ConfigMap cambia (con un retraso de hasta 2 minutos por defecto).
- **Endpoint de reconfiguración:** la aplicación expone un endpoint HTTP (por ejemplo, `POST /config/reload`) que, al llamarse, releer la configuración de disco o del entorno. Un operador externo (script, CronJob) llama al endpoint tras actualizar el ConfigMap.
- **Feature flags:** para cambios frecuentes de comportamiento, integrar una solución de feature flags (LaunchDarkly, Unleash) que la aplicación consulta en tiempo real.

---

## 9. Actividades prácticas

### Actividad 1 — Gestión de dependencias con pip-tools y Poetry

**Contexto:** se parte de un proyecto de inferencia con dependencias declaradas en un `requirements.in` básico.

**Tareas:**
1. Instalar pip-tools y ejecutar `pip-compile` para generar el lockfile con hashes. Analizar las diferencias entre `requirements.in` y `requirements.txt` generado.
2. Reproducir el entorno en un directorio limpio usando `pip-sync` y verificar que las versiones son exactamente las del lockfile.
3. Simular una actualización: cambiar la versión de `transformers` en `requirements.in` a una versión más reciente y volver a compilar. Observar qué otras dependencias cambian.
4. Repetir el ejercicio 1 y 2 usando Poetry: inicializar un proyecto con `poetry init`, añadir las mismas dependencias y comparar el `pyproject.toml` resultante con el `requirements.in`.

**Entregable:** capturas de los comandos ejecutados, el `requirements.txt` generado y una tabla comparativa de ambos enfoques.

---

### Actividad 2 — Construcción y optimización de una imagen Docker para inferencia

**Contexto:** se dispone de una aplicación de inferencia con FastAPI y un modelo de clasificación de texto basado en transformers.

**Tareas:**
1. Construir una imagen Docker usando `nvcr.io/nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04` como base, con todas las dependencias instaladas en una sola capa.
2. Medir el tamaño de la imagen resultante con `docker images`.
3. Refactorizar el Dockerfile usando multi-stage build: una etapa de builder donde se instalan las dependencias, y una etapa final de runtime solo con los artefactos necesarios. Comparar el tamaño.
4. Ejecutar la imagen con acceso a GPU usando `--gpus all` y verificar con `nvidia-smi` dentro del contenedor que la GPU es accesible.
5. Añadir un `HEALTHCHECK` que verifique que el servidor de inferencia responde correctamente.

**Entregable:** el Dockerfile final, la comparativa de tamaños entre la imagen inicial y la optimizada, y el log de un request de inferencia exitoso.

---

### Actividad 3 — Despliegue en Kubernetes con GPU Operator y monitorización

**Contexto:** se dispone de un clúster Kubernetes con nodos GPU (puede usarse minikube con GPU o un clúster real).

**Tareas:**
1. Instalar el NVIDIA GPU Operator usando Helm en el namespace `gpu-operator`. Verificar que todos los pods del DaemonSet están en estado Running.
2. Desplegar el servidor de inferencia del ejercicio 2 como un Deployment con `nvidia.com/gpu: 1` en los resource limits. Verificar que el pod se schedula correctamente con `kubectl describe pod`.
3. Desplegar dcgm-exporter (si no viene con el GPU Operator) y verificar que las métricas son accesibles en el endpoint `/metrics`.
4. Configurar una alerta en Prometheus que dispare cuando la utilización de GPU sea superior al 90% durante más de 5 minutos. Simular la condición de alerta ejecutando una carga de inferencia intensiva.

**Entregable:** los manifiestos YAML del Deployment y la PrometheusRule, capturas de Grafana con métricas en tiempo real y el log de la alerta disparada.

---

### Actividad 4 — Gestión de configuración con ConfigMaps, Secrets y HashiCorp Vault

**Contexto:** el servidor de inferencia necesita acceder a un registro de modelos privado con credenciales y leer su configuración sin reiniciarse.

**Tareas:**
1. Crear un ConfigMap con la configuración de la aplicación (nombre del modelo, tamaño de batch, nivel de log) y montarlo como volumen en el pod.
2. Crear un Secret de Kubernetes con las credenciales del registro de modelos e inyectarlo como variables de entorno. Verificar que los valores son correctos dentro del contenedor.
3. Instalar HashiCorp Vault en modo desarrollo (`vault server -dev`). Almacenar las mismas credenciales en Vault y configurar el agente de Vault como sidecar en el pod para que las inyecte en el sistema de archivos del contenedor.
4. Implementar en la aplicación un endpoint `/config/reload` que lea de nuevo el ConfigMap montado como volumen. Cambiar el ConfigMap y llamar al endpoint sin reiniciar el pod. Verificar que la configuración se ha actualizado.

**Entregable:** todos los manifiestos YAML, el código del endpoint de recarga, capturas de la consola de Vault y verificación de que el cambio de configuración se aplica sin reinicio.

---

## 10. Referencias

### Documentación oficial

- **NVIDIA GPU Operator:** documentación completa de instalación, configuración de MIG, time-slicing y solución de problemas.
  `https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/index.html`

- **NVIDIA CUDA Documentation:** guías de instalación de CUDA Toolkit, referencia de la API y notas de compatibilidad entre versiones.
  `https://docs.nvidia.com/cuda/`

- **NVIDIA cuDNN Documentation:** requisitos de versión, guía de instalación y referencia de la API de cuDNN.
  `https://docs.nvidia.com/deeplearning/cudnn/latest/`

- **NVIDIA Container Toolkit:** instalación y configuración del toolkit para Docker, containerd y CRI-O.
  `https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html`

- **NVIDIA DCGM Documentation:** referencia de métricas, diagnósticos y API de DCGM.
  `https://docs.nvidia.com/datacenter/dcgm/latest/`

- **NVIDIA NGC Catalog:** catálogo de imágenes base y contenedores optimizados de NVIDIA.
  `https://catalog.ngc.nvidia.com/`

### Kubernetes

- **Kubernetes Documentation:** conceptos, guías de tareas y referencia de la API.
  `https://kubernetes.io/docs/`

- **Kubernetes: Managing Resources for Containers:** documentación sobre resource requests y limits, incluyendo GPUs.
  `https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/`

- **Helm Documentation:** referencia para la instalación y gestión de charts de Helm.
  `https://helm.sh/docs/`

### Docker

- **Docker Documentation:** referencia de Dockerfile, buenas prácticas de construcción y Docker Compose.
  `https://docs.docker.com/`

- **Docker Multi-stage builds:** guía oficial sobre construcción en múltiples etapas.
  `https://docs.docker.com/build/building/multi-stage/`

### Libros

- **Lukša, M. (2019). *Kubernetes in Action* (2nd ed.). Manning Publications.** Referencia exhaustiva sobre Kubernetes, cubriendo desde pods y deployments hasta configuración avanzada de redes y almacenamiento. Especialmente relevantes los capítulos sobre ConfigMaps, Secrets y gestión de recursos.

- **Chollet, F. (2021). *Deep Learning with Python* (2nd ed.). Manning Publications.** Para contexto sobre los frameworks de IA que se ejecutan sobre la pila de software descrita en esta unidad.

### Herramientas adicionales

- **pip-tools:** documentación y ejemplos de uso.
  `https://pip-tools.readthedocs.io/`

- **Poetry:** documentación completa incluyendo gestión de grupos de dependencias.
  `https://python-poetry.org/docs/`

- **HashiCorp Vault:** guías de integración con Kubernetes.
  `https://developer.hashicorp.com/vault/docs/platform/k8s`

- **dcgm-exporter en GitHub:** dashboards de Grafana y configuración de métricas.
  `https://github.com/NVIDIA/dcgm-exporter`

- **Prometheus Alerting Rules:** referencia para escribir reglas de alerta.
  `https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/`

---

*Unidad Didáctica 2 — Administración de componentes de aplicaciones de IA*
*MP01 · Implementación de Sistemas de IA — CFS2 · Instalación, despliegue y explotación de sistemas de IA*
