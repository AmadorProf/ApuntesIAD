---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD3 · Preparación del entorno de ejecución | MP04 · Infraestructura para la ejecución de LLMs'
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

# UD3 · Preparación del entorno de ejecución

MP04 · Infraestructura para la ejecución de LLMs

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Identificar y preparar el SO, firmware y controladores necesarios para inferencia GPU
- Instalar y configurar las dependencias de bajo nivel (CUDA, ROCm)
- Comparar los principales motores de inferencia (llama.cpp, vLLM, Ollama, Triton) y seleccionar el adecuado
- Instalar y configurar un motor de inferencia con los parámetros correctos de modelo, precisión y concurrencia
- Aplicar controles de autenticación y gestión de secretos en el entorno
- Validar el entorno con pruebas de arranque y cargas básicas

---

## Stack de software para inferencia LLM

El entorno de ejecución se construye por capas. Cada capa depende de la inferior.

```
+--------------------------------------------------+
|  Aplicación / API cliente                        |
+--------------------------------------------------+
|  Motor de inferencia (llama.cpp, vLLM, Ollama)   |
+--------------------------------------------------+
|  Framework ML (PyTorch, ONNX Runtime)            |
+--------------------------------------------------+
|  Librerías de cómputo acelerado (CUDA, ROCm)     |
+--------------------------------------------------+
|  Controladores GPU (NVIDIA driver, AMDGPU)       |
+--------------------------------------------------+
|  Firmware (BIOS/UEFI, Secure Boot)               |
+--------------------------------------------------+
|  Sistema operativo (Ubuntu 22.04, RHEL 9)        |
+--------------------------------------------------+
```

> Cada motor de inferencia requiere una versión específica de CUDA. Revisar la matriz de compatibilidad antes de instalar.

---

## Sistema operativo — preparación base

### Distribuciones recomendadas para LLM en producción

| Distribución | Versión | Notas |
|---|---|---|
| **Ubuntu Server** | 22.04 LTS | Más documentación, ecosistema más amplio |
| **Ubuntu Server** | 24.04 LTS | Soporte hasta 2034, CUDA 12.x bien soportado |
| **RHEL / Rocky Linux** | 9.x | Entornos corporativos, soporte certificado |
| **Debian** | 12 (Bookworm) | Estabilidad, menor overhead |

### Actualización inicial

```bash
# Ubuntu / Debian
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential curl git wget htop nvtop

# Verificar versión del kernel (mínimo 5.15 para CUDA 12)
uname -r

# Deshabilitar swap si toda la RAM es suficiente
sudo swapoff -a
```

---

## Instalación de controladores NVIDIA y CUDA

### Controladores NVIDIA

```bash
# Verificar GPU detectada
lspci | grep -i nvidia

# Instalar driver recomendado (Ubuntu)
sudo ubuntu-drivers autoinstall
# O instalar versión específica
sudo apt install -y nvidia-driver-535

# Reiniciar y verificar
sudo reboot
nvidia-smi
```

### CUDA Toolkit

```bash
# Instalar CUDA 12.2 (ejemplo)
wget https://developer.download.nvidia.com/compute/cuda/12.2.0/local_installers/\
cuda_12.2.0_535.54.03_linux.run
sudo sh cuda_12.2.0_535.54.03_linux.run --silent --toolkit

# Añadir al PATH
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verificar
nvcc --version
```

---

## ROCm para GPUs AMD

### Instalación de ROCm (AMD)

```bash
# Ubuntu 22.04
sudo apt update
wget https://repo.radeon.com/amdgpu-install/5.7.3/ubuntu/jammy/amdgpu-install_5.7.3.50703-1_all.deb
sudo dpkg -i amdgpu-install_5.7.3.50703-1_all.deb
sudo amdgpu-install --usecase=rocm

# Añadir usuario al grupo render y video
sudo usermod -aG render,video $USER

# Verificar
rocm-smi
rocminfo | grep "gfx"
```

### Matriz de compatibilidad ROCm

| GPU AMD | Arquitectura | ROCm mínimo |
|---|---|---|
| RX 6800 / 6900 | RDNA 2 (gfx1030) | ROCm 5.5 |
| RX 7900 XTX | RDNA 3 (gfx1100) | ROCm 5.7 |
| Instinct MI250 | CDNA 2 (gfx90a) | ROCm 5.0 |
| Instinct MI300X | CDNA 3 (gfx942) | ROCm 6.0 |

---

## Entornos aislados — Python y conda

### Entornos virtuales con venv

```bash
# Instalar Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Crear entorno aislado
python3.11 -m venv /opt/llm-env

# Activar
source /opt/llm-env/bin/activate

# Actualizar pip
pip install --upgrade pip setuptools wheel
```

### Entornos con conda (miniconda)

```bash
# Instalar Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda3

# Crear entorno para vLLM
conda create -n vllm-env python=3.11 -y
conda activate vllm-env

# Instalar PyTorch con CUDA 12.1
pip install torch==2.1.2+cu121 --index-url https://download.pytorch.org/whl/cu121
```

---

## Motores de inferencia — comparativa

| Motor | Lenguaje | Formato | GPU | CPU | Punto fuerte |
|---|---|---|---|---|---|
| **llama.cpp** | C++ | GGUF | NVIDIA, AMD, Apple | Excelente | CPU-first, bajo consumo, cuantización |
| **vLLM** | Python/C++ | SafeTensors, GPTQ, AWQ | NVIDIA (principal) | No | Alto throughput, PagedAttention |
| **Ollama** | Go | GGUF | NVIDIA, AMD, Apple | Sí | Facilidad de uso, gestión de modelos |
| **Triton IS** | Python/C++ | TensorRT, ONNX | NVIDIA | Limitado | Producción multi-modelo, MLOps |
| **TGI (HF)** | Rust/Python | SafeTensors | NVIDIA | Parcial | Hugging Face ecosystem |
| **LMStudio** | Electron | GGUF | NVIDIA, AMD, Apple | Sí | Interfaz gráfica, uso personal |

> **Criterio de selección:** llama.cpp/Ollama para entornos con GPU de consumo o CPU; vLLM para producción con GPU de centro de datos que requiere máximo throughput.

---

## Instalación de llama.cpp

```bash
# Clonar y compilar con soporte CUDA
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Compilar con CUDA
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release -j$(nproc)

# Verificar que detecta la GPU
./build/bin/llama-cli --list-models

# Lanzar servidor de inferencia
./build/bin/llama-server \
  --model /models/llama-3.1-8b-instruct-q4_k_m.gguf \
  --ctx-size 8192 \
  --n-gpu-layers 35 \
  --parallel 4 \
  --port 8080 \
  --host 0.0.0.0
```

### Parámetros clave de llama-server

| Parámetro | Descripción |
|---|---|
| `--n-gpu-layers` | Número de capas del modelo en GPU (35 = todas para 8B) |
| `--ctx-size` | Longitud máxima de contexto en tokens |
| `--parallel` | Slots de concurrencia simultánea |

---

## Instalación de vLLM

```bash
# Instalar vLLM (requiere PyTorch con CUDA)
pip install vllm

# Lanzar servidor compatible con API OpenAI
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.1-8B-Instruct \
  --dtype bfloat16 \
  --max-model-len 8192 \
  --max-num-seqs 64 \
  --gpu-memory-utilization 0.90 \
  --tensor-parallel-size 1 \
  --port 8000 \
  --host 0.0.0.0

# Verificar que arranca correctamente
curl http://localhost:8000/health
```

### Parámetros clave de vLLM

| Parámetro | Descripción |
|---|---|
| `--max-model-len` | Longitud máxima de contexto |
| `--max-num-seqs` | Peticiones simultáneas en batch |
| `--gpu-memory-utilization` | Fracción de VRAM reservada para KV cache |
| `--tensor-parallel-size` | Número de GPUs (tensor parallelism) |

---

## Instalación de Ollama

```bash
# Instalar Ollama (script oficial)
curl -fsSL https://ollama.com/install.sh | sh

# Iniciar servicio
sudo systemctl start ollama
sudo systemctl enable ollama

# Descargar y ejecutar un modelo
ollama pull llama3.1:8b
ollama run llama3.1:8b

# Usar la API REST
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "Explica qué es un transformer en dos frases.",
  "stream": false
}'

# Listar modelos disponibles
ollama list
```

> Ollama gestiona automáticamente la descarga, el almacenamiento y la carga del modelo. Ideal para entornos de desarrollo o usuarios sin experiencia en MLOps.

---

## Contenedores Docker para inferencia

```dockerfile
# Dockerfile para vLLM con CUDA 12.1
FROM vllm/vllm-openai:latest

ENV MODEL_PATH=/models/llama-3.1-8b-instruct
ENV MAX_MODEL_LEN=8192
ENV MAX_NUM_SEQS=32

EXPOSE 8000

CMD ["python", "-m", "vllm.entrypoints.openai.api_server", \
     "--model", "${MODEL_PATH}", \
     "--dtype", "bfloat16", \
     "--max-model-len", "${MAX_MODEL_LEN}", \
     "--max-num-seqs", "${MAX_NUM_SEQS}", \
     "--host", "0.0.0.0", \
     "--port", "8000"]
```

```bash
# Ejecutar con GPU
docker run --gpus all \
  -v /data/models:/models \
  -p 8000:8000 \
  --name llm-server \
  mi-imagen-vllm:latest
```

---

## Autenticación y gestión de secretos

### Por qué gestionar secretos correctamente

Un endpoint de LLM sin autenticación es un recurso que cualquiera puede consumir. Las API keys y tokens nunca deben estar en código fuente ni en variables de entorno del sistema sin cifrado.

### Opciones de gestión de secretos

| Opción | Uso recomendado |
|---|---|
| **HashiCorp Vault** | Producción — almacenamiento centralizado de secretos |
| **AWS Secrets Manager** | Producción en AWS |
| **Variables de entorno** | Desarrollo — solo en entorno local, nunca en repo |
| **Archivos `.env`** | Desarrollo — añadir a `.gitignore` siempre |

```bash
# Proteger el endpoint con autenticación Bearer token (vLLM)
python -m vllm.entrypoints.openai.api_server \
  --model /models/llama-3.1-8b \
  --api-key "$(cat /run/secrets/llm_api_key)" \
  --port 8000

# Recuperar secreto desde Vault
export LLM_API_KEY=$(vault kv get -field=api_key secret/llm/prod)
```

---

## Validación del entorno

```bash
# 1. Verificar uso de GPU durante la carga del modelo
watch -n 1 nvidia-smi

# 2. Prueba de arranque — petición de salud
curl http://localhost:8000/health
curl http://localhost:11434/api/tags  # Ollama

# 3. Primera petición de inferencia
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "llama-3.1-8b", "prompt": "Hola", "max_tokens": 50}'

# 4. Verificar uso de recursos durante inferencia
nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu \
  --format=csv -l 2

# 5. Prueba básica de concurrencia (10 peticiones en paralelo)
for i in $(seq 1 10); do
  curl -s http://localhost:8000/v1/completions \
    -d '{"model":"llama-3.1-8b","prompt":"Cuenta hasta 5","max_tokens":30}' &
done
wait
echo "Prueba de concurrencia completada"
```

---

## Actividad práctica — Instalación de entorno

### Escenario

Preparar un entorno de inferencia local en una máquina con Ubuntu 22.04 y una GPU NVIDIA RTX 4090 (24 GB VRAM) para servir el modelo `Mistral-7B-Instruct-v0.3` en formato GGUF Q4_K_M.

### Tareas

1. Redacta la secuencia completa de comandos para instalar controladores NVIDIA y CUDA
2. Elige entre llama.cpp y Ollama para este caso de uso — justifica la elección
3. Escribe el comando de arranque del motor con los parámetros correctos para:
   - Contexto de 4 096 tokens
   - 8 usuarios concurrentes máximo
   - GPU-only (todas las capas en GPU)
4. Diseña una prueba de validación que verifique: arranque correcto, uso de VRAM esperado y respuesta a peticiones concurrentes
5. Indica cómo proteger el endpoint con autenticación por API key

---

## Puntos clave — UD3

- La compatibilidad entre **versión del driver NVIDIA**, **versión de CUDA** y **versión del motor de inferencia** debe verificarse antes de instalar. Un mismatch provoca errores difíciles de diagnosticar.

- **llama.cpp/Ollama** son ideales para entornos con GPUs de consumo o requisitos de instalación sencilla. **vLLM** es la elección para producción con GPU de centro de datos por su mayor throughput (PagedAttention).

- Los **contenedores Docker** con imagen oficial (vllm-openai, ollama) aceleran el despliegue y garantizan reproducibilidad del entorno.

- Las **API keys y secretos** nunca deben estar en código fuente. Usar variables de entorno o, en producción, un gestor de secretos (Vault, AWS Secrets Manager).

- La **validación** debe comprobar tres cosas: que el motor arranca sin errores, que usa la GPU (no CPU accidentalmente) y que responde correctamente a peticiones concurrentes.

---

## Criterios de evaluación — UD3

| Criterio | Indicadores de logro |
|---|---|
| **Habilita SO y dependencias** | Instala driver, CUDA y dependencias en la versión correcta; verifica compatibilidad |
| **Instala el motor de inferencia** | Selecciona motor apropiado; configura modelo, precisión, contexto y concurrencia |
| **Configura autenticación** | Protege el endpoint; gestiona secretos sin exponerlos en código |
| **Valida el entorno** | Ejecuta prueba de arranque, verifica uso de GPU y prueba concurrencia básica |
| **Usa contenedores** | Opcional: dockeriza el servicio con variables de entorno parametrizables |

> **Referencia:** resultado de aprendizaje RA3 — "Prepara el entorno instalando y verificando el motor de inferencia, dependencias y componentes."

---

[← Volver a MP04](../index.md)


---

<!-- nav-slide -->

## Navegación

[← UD2 · Selección y dimensionamiento…](../UD2_Dimensionamiento-recursos/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD4 · Puesta en servicio del modelo →](../UD4_Puesta-servicio-modelo/)
