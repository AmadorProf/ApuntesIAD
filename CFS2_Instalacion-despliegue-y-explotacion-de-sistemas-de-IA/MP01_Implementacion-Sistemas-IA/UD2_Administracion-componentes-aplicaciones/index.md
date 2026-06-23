---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD2 · Administración de componentes de aplicaciones | MP01 · Implementación de sistemas de IA'
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

# UD2 · Administración de componentes de aplicaciones

MP01 · Implementación de sistemas de IA

---

## Objetivos de la unidad

Al finalizar esta unidad el alumnado sera capaz de:

- Identificar y catalogar los componentes de software que forman un sistema de IA en produccion
- Documentar versiones, licencias y dependencias siguiendo estandares de trazabilidad
- Comparar sistemas operativos, entornos de ejecucion y librerías de ML segun el caso de uso
- Gestionar el inventario de licencias y cumplir con las obligaciones de propiedad industrial
- Aplicar medidas de ergonomía cognitiva y prevencion del tecnoestrés en el puesto de trabajo

> **Resultado de aprendizaje:** Administra la informacion de los componentes de las aplicaciones para garantizar su localizacion, control y disponibilidad.

---

## Componentes generales — Sistemas operativos para IA

| Caracteristica | Ubuntu 22.04 LTS | RHEL 9 | Windows Server 2022 |
|---|---|---|---|
| Soporte | Hasta abr. 2027 | Hasta may. 2032 | Hasta oct. 2031 |
| Kernel | 5.15 LTS | 5.14 | NT 10.0 (build 20348) |
| Gestor de paquetes | `apt` / `snap` | `dnf` / RPM | MSI / winget |
| Certificacion GPU | NVIDIA, AMD, Intel | NVIDIA, AMD | NVIDIA (WHQL) |
| Contenedores | Docker, Podman | Podman (nativo) | Docker Desktop, WSL2 |
| Caso de uso IA | Desarrollo, inferencia, HPC | Entornos corporativos criticos | Integracion con ecosistema Microsoft |
| Coste licencia | Gratuito (soporte pagado) | Suscripcion Red Hat | Licencia por nucleo |

> Ubuntu 22.04 LTS es la distribucion de referencia en entornos de IA por su amplia compatibilidad con drivers NVIDIA y repositorios de ML.

---

## Componentes generales — Entornos de ejecucion GPU

| Caracteristica | CUDA 12.x | ROCm 6.x | OpenVINO 2024 |
|---|---|---|---|
| Fabricante | NVIDIA | AMD | Intel |
| GPUs soportadas | RTX 30/40, A/H series | RX 6000/7000, MI200/300 | CPU, GPU Intel, VPU Movidius |
| Lenguajes | C++, Python, Fortran | C++, Python, HIP | C++, Python |
| Frameworks | PyTorch, TensorFlow, JAX | PyTorch (ROCm fork), TF | ONNX, TF, PyTorch (via ONNX) |
| Precision soportada | FP64/32/16, BF16, INT8/4 | FP64/32/16, BF16, INT8 | FP32/16, INT8, INT4 |
| Caso de uso principal | Entrenamiento y produccion | Alternativa open-source a CUDA | Inferencia optimizada en Intel |
| Documentacion | docs.nvidia.com/cuda | rocm.docs.amd.com | docs.openvino.ai |

---

## Librerias de ML — PyTorch y TensorFlow

| Caracteristica | PyTorch 2.x | TensorFlow 2.14 |
|---|---|---|
| Mantenedor | Meta AI / Linux Foundation | Google / TensorFlow community |
| Paradigma | Grafo dinamico (eager por defecto) | Grafo estatico / eager opcional |
| Acelerador GPU | CUDA, ROCm, MPS (Apple) | CUDA (XLA backend) |
| API distribuida | `torch.distributed`, FSDP | `tf.distribute.Strategy` |
| Exportacion de modelos | TorchScript, ONNX, ExecuTorch | SavedModel, TFLite, ONNX |
| Memoria minima (GPU) | 4 GB VRAM (inferencia basica) | 4 GB VRAM (inferencia basica) |
| Uso predominante | Investigacion, produccion LLM | Produccion empresarial, movil |
| Licencia | BSD-3 | Apache 2.0 |

---

## Librerias de ML — scikit-learn y ONNX Runtime

| Caracteristica | scikit-learn 1.4 | ONNX Runtime 1.17 |
|---|---|---|
| Mantenedor | INRIA / comunidad | Microsoft |
| Proposito | ML clasico (no DL) | Inferencia optimizada multiformato |
| Acelerador | CPU (OpenMP), partial GPU via cuML | CUDA, DirectML, CoreML, ROCm |
| Modelos soportados | Decision trees, SVM, clustering... | Redes neuronales en formato ONNX |
| Integracion | pandas, NumPy, joblib | PyTorch, TF, scikit-learn (via skl2onnx) |
| RAM minima | 512 MB | 512 MB |
| Latencia inferencia | Alta (modelos simples) | Muy baja (grafos optimizados) |
| Licencia | BSD-3 | MIT |

> ONNX Runtime permite servir modelos de PyTorch o TF sin dependencia del framework original, reduciendo la huella de produccion.

---

## Frameworks de despliegue — Triton y TF Serving

| Caracteristica | Triton Inference Server 2.x | TF Serving 2.14 |
|---|---|---|
| Mantenedor | NVIDIA | Google |
| Frameworks de backend | TF, PyTorch, ONNX, TensorRT, Python | TensorFlow / TFLite |
| Protocolo de red | HTTP/REST, gRPC | HTTP/REST, gRPC |
| Throughput tipico | Alto (batching dinamico, multi-GPU) | Medio-alto |
| Gestion de modelos | Model repository en disco/S3/GCS | Versiones en directorio local |
| Metricas Prometheus | Nativo | Via adaptador |
| Orquestacion | Kubernetes, Docker Compose | Kubernetes, Docker |
| Licencia | BSD-3 | Apache 2.0 |

---

## Frameworks de despliegue — BentoML y TorchServe

| Caracteristica | BentoML 1.x | TorchServe 0.9 |
|---|---|---|
| Mantenedor | BentoML Inc. | Meta AI / AWS |
| Frameworks de backend | PyTorch, TF, sklearn, ONNX, XGBoost | PyTorch (nativo), TorchScript |
| Protocolo de red | HTTP/REST, gRPC | HTTP/REST, gRPC |
| Empaquetado | Bento (imagen Docker autocontenida) | MAR (Model Archive) |
| Batching dinamico | Si | Si |
| Escalado | Kubernetes, BentoCloud | Kubernetes, EC2 |
| Panel de control | BentoCloud (SaaS) | Management API REST |
| Licencia | Apache 2.0 | Apache 2.0 |

> BentoML es especialmente adecuado para equipos que trabajan con multiples frameworks a la vez y necesitan empaquetar modelos como microservicios autocontenidos.

---

## Herramientas MLOps — MLflow y DVC

| Caracteristica | MLflow 2.x | DVC 3.x |
|---|---|---|
| Funcion principal | Ciclo de vida de experimentos y modelos | Control de versiones de datos y pipelines |
| Seguimiento | Metricas, parametros, artefactos | Versiones de datasets y archivos grandes |
| Registro de modelos | MLflow Model Registry | No (complementar con MLflow) |
| Backend de almacenamiento | Local, S3, Azure Blob, GCS | S3, GCS, Azure, SSH, Google Drive |
| Integracion CI/CD | GitHub Actions, GitLab CI | GitHub Actions, GitLab CI |
| UI web | Si (puerto 5000) | No (CLI) |
| Licencia | Apache 2.0 | Apache 2.0 |

---

## Herramientas MLOps — Apache Airflow y Kubeflow

| Caracteristica | Apache Airflow 2.9 | Kubeflow 1.8 |
|---|---|---|
| Funcion principal | Orquestacion de pipelines de datos y ML | Plataforma ML nativa en Kubernetes |
| Abstraccion | DAGs en Python | Pipelines KFP (Python SDK) |
| Ejecucion | Workers Celery/K8s | Pods Kubernetes |
| Integracion ML | Operadores para MLflow, Spark, dbt | Katib (HPO), KServe (inferencia) |
| Interfaz | Web UI + CLI | Web UI + CLI + SDK |
| Escalado | Horizontal via workers | Kubernetes nativo |
| Licencia | Apache 2.0 | Apache 2.0 |

> Para sistemas de IA en produccion, la combinacion MLflow + Airflow + Triton cubre el ciclo completo desde el experimento hasta el servicio.

---

## Formatos de modelos — ONNX y GGUF

### ONNX (Open Neural Network Exchange)

- Formato de intercambio estandar para redes neuronales impulsado por Microsoft y Meta.
- Permite exportar modelos de PyTorch o TensorFlow y ejecutarlos en ONNX Runtime, OpenVINO o TensorRT.
- Version actual: **ONNX 1.16** (opset 20). Soporta FP32, FP16, INT8, BF16.
- Uso tipico: inferencia multiplataforma, despliegue en edge e IoT.

### GGUF (GPT-Generated Unified Format)

- Formato binario de la libreria `llama.cpp` para modelos de lenguaje cuantizados.
- Reemplaza al formato GGML. Incluye metadatos del modelo (arquitectura, tokenizador, hiperparametros) en una unica cabecera.
- Soporta cuantizacion: Q4_K_M, Q5_K_M, Q8_0, F16... ideal para inferencia en CPU o GPU consumer.
- Uso tipico: ejecucion de LLM en hardware limitado sin dependencias de Python.

---

## Formatos de modelos — SafeTensors y PMML

### SafeTensors

- Formato de almacenamiento de tensores disenado por Hugging Face como alternativa segura a `pickle`.
- Evita la ejecucion de codigo arbitrario al cargar pesos: no utiliza serializacion Python.
- Carga rapida mediante mapeo de memoria (`mmap`). Compatible con PyTorch, JAX, TensorFlow y NumPy.
- Uso tipico: distribucion de pesos de modelos en Hugging Face Hub y entornos de produccion seguros.

### PMML (Predictive Model Markup Language)

- Estandar XML del Data Mining Group para describir modelos de ML clasico.
- Version actual: **PMML 4.4.1**. Soporta regresion, arboles de decision, SVM, redes neuronales simples.
- Permite portabilidad entre herramientas: scikit-learn (via `sklearn2pmml`), R, SAS, KNIME.
- Uso tipico: integracion de modelos en sistemas de negocio (ERP, CRM) que no ejecutan Python.

---

## Documentacion de versiones — Ficha de componente (YAML)

Cada componente de un sistema de IA debe disponer de una ficha tecnica registrada en el repositorio de configuracion:

```yaml
componente:
  nombre: "PyTorch"
  version: "2.3.1"
  tipo: "libreria-ml"
  fabricante: "Meta AI / Linux Foundation"
  licencia: "BSD-3-Clause"
  url_licencia: "https://github.com/pytorch/pytorch/blob/main/LICENSE"
  fecha_instalacion: "2025-03-15"
  entorno: "produccion"
  servidor: "gpu-server-01.empresa.local"
  ruta_instalacion: "/opt/conda/envs/inference/lib/python3.11/site-packages/torch"
  dependencias:
    - "CUDA 12.1"
    - "cuDNN 8.9.7"
    - "numpy>=1.24"
    - "filelock"
    - "typing-extensions>=4.8"
  hash_verificacion: "sha256:a1b2c3d4..."
  responsable: "equipo-mlops"
  proximo_revision: "2025-09-15"
  notas: "Instalado con soporte ROCm desactivado. Ver ticket INC-2041."
```

---

## Documentacion de versiones — Campos obligatorios del registro

El registro corporativo de componentes de IA debe incluir como minimo los siguientes campos para cumplir con los requisitos de trazabilidad:

| Campo | Descripcion | Obligatorio |
|---|---|---|
| nombre + version | Identificacion univoca del componente | Si |
| tipo | SO / runtime / libreria / framework / herramienta | Si |
| licencia | Identificador SPDX (MIT, Apache-2.0, GPL-3.0...) | Si |
| fecha instalacion | ISO 8601 (YYYY-MM-DD) | Si |
| entorno | dev / staging / produccion | Si |
| servidor / host | FQDN o IP del sistema donde esta instalado | Si |
| ruta de instalacion | Ruta absoluta en el sistema de ficheros | Si |
| dependencias | Lista de dependencias directas con version minima | Si |
| hash de verificacion | SHA-256 del paquete instalado | Recomendado |
| responsable | Persona o equipo propietario del componente | Si |
| proxima revision | Fecha de revision de actualizacion o fin de soporte | Recomendado |

---

## Trazabilidad de la arquitectura de software

La trazabilidad permite reconstruir en cualquier momento el estado exacto del sistema. Se representa mediante un arbol de dependencias:

```
Sistema de inferencia (produccion)
├── SO: Ubuntu 22.04.4 LTS
│   ├── kernel: 5.15.0-112-generic
│   └── glibc: 2.35
├── Runtime GPU: CUDA 12.1.1
│   ├── Driver NVIDIA: 535.183.01
│   └── cuDNN: 8.9.7
├── Entorno Python: conda env "inference" (Python 3.11.8)
│   ├── torch==2.3.1+cu121
│   │   ├── numpy==1.26.4
│   │   └── filelock==3.13.1
│   └── tritonclient==2.45.0
│       ├── grpcio==1.62.1
│       └── protobuf==4.25.3
└── Servidor de inferencia: Triton 2.45.0
    └── Backend TensorRT: 10.0.1.6
```

> Herramientas: `pip freeze`, `conda env export`, `pip-audit`, `syft` (SBOM), `syft` + `grype` para vulnerabilidades.

---

## Control de licencias — Tipos y obligaciones

| Tipo de licencia | Ejemplos | Uso comercial | Copyleft | Modificacion publica |
|---|---|---|---|---|
| Permisiva | MIT, BSD-2, BSD-3 | Libre | No | No obligatoria |
| Permisiva + patent | Apache 2.0 | Libre | No | No (aviso de cambios) |
| Copyleft debil | LGPL-2.1, MPL-2.0 | Libre | Parcial | Solo el modulo modificado |
| Copyleft fuerte | GPL-2.0, GPL-3.0, AGPL-3.0 | Libre | Total | Si se distribuye el binario |
| Propietaria | CUDA Toolkit EULA, PyCharm Pro | Segun contrato | N/A | No |
| Dual licencia | MySQL (GPL + comercial) | Segun opcion | Segun opcion | Segun opcion |

> **Atencion AGPL-3.0:** Si se modifica un componente AGPL y se expone como servicio web, se debe publicar el codigo fuente completo. Muchas empresas prohíben el uso de AGPL en produccion.

---

## Control de licencias — Inventario y propiedad industrial

### Inventario de licencias

- Mantener un archivo `LICENSES.csv` en el repositorio con todos los componentes de terceros.
- Herramientas de escaneo automatico: `pip-licenses`, `license-checker` (Node), `fossa`, `TLDR Legal`.
- Integrar el escaneo en el pipeline CI/CD como paso obligatorio antes del despliegue.

### Propiedad industrial en sistemas de IA

- Los modelos entrenados con datos propietarios son activos de la empresa: documentar la cadena de custodia del dataset.
- Verificar las condiciones de uso de modelos base (Llama 3, Mistral, Falcon): algunas imponen restricciones de uso comercial o de escala.
- Los pesos de un modelo entrenado por la empresa pueden registrarse como obra derivada o secreto industrial.
- La documentacion tecnica (fichas de componentes, diagramas de arquitectura) tiene valor probatorio en caso de litigio.

---

## Gestion de dependencias y recuperacion ante fallos

### Exportacion del entorno de produccion

```bash
# Con pip — genera requirements.txt con versiones exactas
pip freeze > requirements_prod_20250615.txt

# Con conda — incluye dependencias del sistema y canales
conda env export --no-builds > environment_prod_20250615.yml

# Solo dependencias directas (sin transitivas)
pip list --format=freeze --not-required > requirements_direct.txt
```

### Recreacion del entorno (rollback)

```bash
# Recrear entorno conda exacto
conda env create -f environment_prod_20250615.yml -n inference_restore

# Recrear entorno pip en venv
python3.11 -m venv venv_restore
source venv_restore/bin/activate
pip install -r requirements_prod_20250615.txt
```

> Guardar los archivos de entorno en el repositorio de configuracion junto a la ficha de componentes. Versionar con fecha en el nombre.

---

## Riesgos psicosociales y tecnoestrés

La administracion de sistemas de IA implica alta carga cognitiva: multiples herramientas, actualizaciones frecuentes, incidencias en produccion y presion temporal. El **tecnoestrés** es el malestar psicologico derivado de la interaccion con la tecnologia.

### Factores de riesgo identificados

- Interrupciones frecuentes por alertas y tickets
- Exigencia de disponibilidad fuera del horario laboral (oncall)
- Obsolescencia rapida de conocimientos (actualizaciones continuas de frameworks)
- Ambiguedad de rol en equipos donde convergen perfiles de software, datos y sistemas

### Senales de alerta

- Dificultad para desconectar del trabajo al finalizar la jornada
- Irritabilidad o ansiedad ante nuevas actualizaciones o cambios de herramienta
- Errores frecuentes por falta de concentracion
- Fatiga visual persistente al final del dia

> El reconocimiento de estos riesgos es el primer paso para aplicar medidas preventivas colectivas e individuales.

---

## Ergonomia visual y pausas activas

| Medida | Descripcion | Frecuencia recomendada |
|---|---|---|
| Regla 20-20-20 | Cada 20 min, mirar a 6 m durante 20 segundos | Cada 20 minutos |
| Pausa activa corta | Estiramientos de cuello, hombros y munecas | Cada 50-60 minutos |
| Pausa larga | Levantarse, caminar, desconectar de la pantalla | Cada 2 horas |
| Configuracion del monitor | Brillo al 70%, temperatura de color 5000-6500K diurno / 3000-4000K nocturno | Al inicio de jornada |
| Distancia al monitor | 50-70 cm entre ojos y pantalla, parte superior al nivel de los ojos | Siempre |
| Gestion de notificaciones | Silenciar canales no criticos durante bloques de trabajo profundo | Bloques de 90 min |
| Tecnica Pomodoro | 25 min trabajo + 5 min pausa, cada 4 ciclos una pausa de 20-30 min | Adaptable |
| Espacio de trabajo | Iluminacion natural o luz blanca difusa, evitar reflejos en pantalla | Siempre |

---

## Actividad practica

### Auditoria de dependencias y documentacion de componentes

**Objetivo:** Auditar las dependencias de un entorno Python de inferencia y generar la ficha de componente siguiendo la plantilla YAML de la unidad.

**Pasos:**

1. Activar el entorno virtual proporcionado por el instructor (`conda activate inference_lab`)
2. Ejecutar `pip freeze > requirements_auditoria.txt` y examinar la salida
3. Identificar los 5 componentes principales (framework ML, runtime, servidor de inferencia, librerias de soporte, herramienta MLOps)
4. Para cada componente, verificar la licencia con `pip-licenses --format=markdown`
5. Completar la plantilla YAML de ficha de componente para al menos 3 componentes
6. Generar el arbol de dependencias con `pipdeptree --graph-output png > arbol_dependencias.png`
7. Identificar si algun componente usa licencia GPL o AGPL y documentar las implicaciones

**Entregable:** Archivo ZIP con `requirements_auditoria.txt`, 3 fichas YAML y un informe breve en Markdown con la tabla de licencias y las implicaciones detectadas.

---

## Puntos clave

- Los sistemas de IA en produccion combinan componentes de distintas categorias: SO, runtime GPU, librerías de ML, frameworks de despliegue y herramientas MLOps. Cada categoria tiene sus propios ciclos de version y licencias.
- La ficha de componente en YAML es la unidad basica de trazabilidad: nombre, version, licencia, dependencias, entorno y responsable son campos obligatorios.
- ONNX es el formato de interoperabilidad entre frameworks; SafeTensors es el estandar seguro para distribuir pesos; GGUF permite inferencia de LLM en hardware limitado.
- Las licencias copyleft (especialmente AGPL-3.0) pueden imponer obligaciones legales en servicios web. El escaneo automatico de licencias debe integrarse en CI/CD.
- La exportacion del entorno (`pip freeze`, `conda env export`) y su almacenamiento versionado son la base de la recuperacion ante fallos.
- El tecnoestrés y la fatiga visual son riesgos reales en la administracion de sistemas de IA. La organizacion debe implementar medidas preventivas: pausas activas, gestion de notificaciones y ergonomia del puesto.

---

## Criterios de evaluacion

| Criterio | Indicadores | Peso orientativo |
|---|---|---|
| Documentacion de componentes | Completa la ficha YAML con todos los campos obligatorios; los datos son correctos y verificables | 25% |
| Identificacion de componentes | Clasifica correctamente los componentes por categoria (SO, runtime, libreria, framework, herramienta) | 20% |
| Control de licencias | Identifica el tipo de licencia de cada componente y sus implicaciones para uso comercial | 25% |
| Gestion de dependencias | Genera y verifica correctamente los archivos de exportacion del entorno | 15% |
| Ergonomia cognitiva | Describe al menos tres medidas preventivas de tecnoestrés aplicables al puesto | 15% |

---

<!-- _class: lead -->

# Fin de la unidad

[← Volver a MP01](../)
