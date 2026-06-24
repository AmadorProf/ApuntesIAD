# UD2 · Despliegue de modelos con frameworks especializados

---

## 1. Introducción — Del notebook al servicio: el gap entre investigación y producción

Un modelo de machine learning que vive en un notebook de Jupyter tiene un valor práctico cercano a cero. Por muy buenas que sean sus métricas de evaluación, mientras no pueda recibir datos en tiempo real, procesar peticiones concurrentes y devolver predicciones con latencia predecible, no es un producto: es un experimento.

Este salto entre el entorno de experimentación y el entorno de producción es uno de los problemas más subestimados en los equipos que trabajan con IA. En investigación, el objetivo es maximizar la métrica de validación. En producción, los objetivos son múltiples y frecuentemente en tensión: latencia baja, alta disponibilidad, escalabilidad horizontal, reproducibilidad de resultados y facilidad de actualización del modelo sin interrumpir el servicio.

El flujo típico del gap de producción se puede describir así. Un equipo de ciencia de datos entrena un modelo en un entorno local o en la nube con GPUs. El modelo alcanza el rendimiento deseado. Entonces llega la pregunta: ¿cómo lo pone en producción el equipo de ingeniería? En muchos proyectos, la respuesta es un proceso ad hoc: se exporta el modelo a un archivo, se escribe un script de Python que lo carga y expone un endpoint HTTP mínimo, y ese script se ejecuta directamente en un servidor. Este enfoque funciona en proyectos pequeños, pero falla sistemáticamente cuando el tráfico crece, cuando se necesitan actualizaciones sin downtime, cuando se quiere monitorizar la latencia por percentil o cuando se necesita servir varios modelos simultáneamente.

Los frameworks de despliegue especializados, los formatos de serialización estándar y la containerización son las herramientas que cierran este gap. Esta unidad didáctica recorre cada una de estas capas con el nivel de detalle necesario para que un profesional pueda tomar decisiones técnicas informadas y construir pipelines de despliegue robustos.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Explicar las diferencias entre los principales formatos de serialización de modelos y elegir el adecuado según el caso de uso, considerando portabilidad, rendimiento y riesgos de seguridad.
- Exportar modelos entrenados en PyTorch, TensorFlow y scikit-learn a formato ONNX y ejecutarlos con ONNX Runtime.
- Desplegar modelos usando TorchServe, TensorFlow Serving y BentoML, comprendiendo la arquitectura interna de cada framework.
- Diseñar y construir una API de inferencia con FastAPI, incluyendo validación de esquemas con Pydantic, gestión del ciclo de vida del modelo y manejo estructurado de errores.
- Crear imágenes Docker optimizadas para cargas de trabajo de ML, utilizando builds multi-stage y gestionando los artefactos del modelo de forma explícita.
- Identificar el problema del cold start en inferencia y aplicar estrategias de precalentamiento y caching para mitigarlo.
- Comparar las opciones de despliegue disponibles y justificar la elección de una arquitectura concreta para un escenario dado.

---

## 3. Serialización y formatos de modelos

Antes de poder servir un modelo, es necesario persistirlo en un formato que pueda ser cargado por el sistema de serving. Esta operación, conocida como serialización, no es trivial: el formato elegido determina la portabilidad del modelo, su rendimiento en inferencia y los riesgos de seguridad asociados.

### 3.1 pickle y joblib

`pickle` es el mecanismo de serialización nativo de Python. Convierte cualquier objeto Python en una secuencia de bytes que puede escribirse en disco y reconstruirse posteriormente. Por su universalidad, es el formato por defecto de scikit-learn y de muchas bibliotecas que no definen su propio formato de persistencia.

```python
import pickle
from sklearn.ensemble import RandomForestClassifier

modelo = RandomForestClassifier(n_estimators=100)
modelo.fit(X_train, y_train)

with open("modelo.pkl", "wb") as f:
    pickle.dump(modelo, f)

with open("modelo.pkl", "rb") as f:
    modelo_cargado = pickle.load(f)
```

`joblib` es la alternativa recomendada por scikit-learn para modelos que contienen grandes arrays NumPy. Internamente usa pickle pero aplica compresión eficiente sobre estructuras numéricas, lo que reduce el tamaño del archivo y acelera la lectura.

```python
import joblib

joblib.dump(modelo, "modelo.joblib")
modelo_cargado = joblib.load("modelo.joblib")
```

**Riesgos de seguridad.** El principal riesgo de pickle es que la deserialización puede ejecutar código arbitrario. Un archivo `.pkl` malicioso puede comprometer el sistema que lo carga. Esto no es una vulnerabilidad teórica: es un vector de ataque documentado. La regla es clara: nunca cargar archivos pickle de fuentes no verificadas. En entornos de producción, los modelos deben venir de registros de modelos internos con control de integridad (hash del artefacto), no de sistemas de ficheros compartidos sin autenticación.

### 3.2 TensorFlow SavedModel

El formato nativo de TensorFlow 2.x es SavedModel. A diferencia de pickle, no serializa un objeto Python arbitrario, sino el grafo de computación del modelo y sus pesos de forma independiente del entorno de Python.

```python
modelo.save("./modelo_saved")
modelo_cargado = tf.saved_model.load("./modelo_saved")
```

El directorio generado contiene un subdirectorio `variables/` con los pesos y un archivo `saved_model.pb` con el grafo en formato Protocol Buffer. Esta estructura permite cargar el modelo desde lenguajes distintos a Python (C++, Java) y es el formato que consume TensorFlow Serving.

### 3.3 PyTorch: state_dict y TorchScript

PyTorch ofrece dos estrategias de serialización con propósitos distintos.

El `state_dict` guarda únicamente los parámetros aprendidos del modelo (pesos y sesgos), no la arquitectura. Para cargarlo, es necesario tener la definición de la clase del modelo disponible en el entorno de destino.

```python
torch.save(modelo.state_dict(), "modelo_pesos.pt")

modelo_nuevo = MiRed()
modelo_nuevo.load_state_dict(torch.load("modelo_pesos.pt"))
modelo_nuevo.eval()
```

TorchScript es la alternativa recomendada para producción. Compila el modelo a una representación intermedia independiente del código Python original. Existen dos modos: `torch.jit.script`, que compila el código Python directamente mediante análisis estático, y `torch.jit.trace`, que graba la ejecución del modelo con una entrada de ejemplo.

```python
modelo_scripted = torch.jit.trace(modelo, ejemplo_input)
torch.jit.save(modelo_scripted, "modelo_scripted.pt")

modelo_cargado = torch.jit.load("modelo_scripted.pt")
```

TorchScript permite ejecutar el modelo en C++ sin dependencias de Python, lo que es relevante para entornos embebidos o de baja latencia.

### 3.4 ONNX como formato universal

Open Neural Network Exchange (ONNX) es un formato abierto diseñado para representar modelos de aprendizaje automático de forma interoperable entre frameworks. Un modelo exportado a ONNX puede ejecutarse con cualquier runtime compatible, independientemente del framework con el que fue entrenado.

**Exportación desde PyTorch:**

```python
import torch.onnx

dummy_input = torch.randn(1, num_features)
torch.onnx.export(
    modelo,
    dummy_input,
    "modelo.onnx",
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
    opset_version=17
)
```

**Exportación desde scikit-learn:**

Para scikit-learn se utiliza la biblioteca `skl2onnx`:

```python
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

tipo_input = [("float_input", FloatTensorType([None, num_features]))]
modelo_onnx = convert_sklearn(modelo_sklearn, initial_types=tipo_input)

with open("modelo.onnx", "wb") as f:
    f.write(modelo_onnx.SerializeToString())
```

**Ventajas de interoperabilidad.** La principal ventaja de ONNX es que desacopla el framework de entrenamiento del runtime de inferencia. Un modelo entrenado en PyTorch puede servirse con ONNX Runtime, que en benchmarks independientes supera con frecuencia al runtime nativo de PyTorch en inferencia CPU, especialmente para batch size 1 (el caso típico de APIs síncronas).

### 3.5 Tabla comparativa de formatos

| Formato | Portabilidad | Rendimiento en inferencia | Compatibilidad cross-language | Seguridad |
|---|---|---|---|---|
| pickle/joblib | Solo Python | Depende del modelo | No | Riesgo alto |
| TF SavedModel | Alta (TF ecosystem) | Alta | Si (C++, Java) | Alta |
| PyTorch state_dict | Solo PyTorch+Python | Media | No | Media |
| TorchScript | Alta (TorchScript RT) | Alta | Si (C++) | Alta |
| ONNX | Muy alta (universal) | Muy alta (con ORT) | Si (múltiples) | Alta |

---

## 4. Frameworks de serving

### 4.1 TorchServe

TorchServe es el framework oficial de Meta para servir modelos PyTorch en producción. Su arquitectura separa la gestión de modelos de la inferencia, lo que permite actualizar modelos sin reiniciar el servidor.

**Arquitectura.** TorchServe se compone de tres capas principales. El Frontend, escrito en Java, recibe las peticiones HTTP/gRPC y las encola. El Backend, en Python, ejecuta los workers de inferencia. El Model Store es el directorio donde residen los archivos `.mar` (Model ARchive).

**Model Archiver.** Para servir un modelo, primero se empaqueta en un archivo `.mar` con la herramienta `torch-model-archiver`:

```bash
torch-model-archiver \
  --model-name clasificador \
  --version 1.0 \
  --serialized-file modelo_scripted.pt \
  --handler image_classifier \
  --export-path model_store
```

El `handler` es el componente clave: define cómo se preprocesa la entrada, cómo se llama al modelo y cómo se postprocesa la salida. TorchServe incluye handlers predefinidos (clasificación de imágenes, detección de objetos, NLP) y permite crear handlers personalizados heredando de `BaseHandler`.

**Management API.** TorchServe expone un endpoint de gestión en el puerto 8081:

```bash
# Registrar un modelo
curl -X POST "http://localhost:8081/models?url=clasificador.mar&initial_workers=2"

# Escalar workers
curl -X PUT "http://localhost:8081/models/clasificador?min_worker=4&max_worker=8"

# Desregistrar
curl -X DELETE "http://localhost:8081/models/clasificador"
```

**Inference API.** Las predicciones se realizan contra el puerto 8080:

```bash
curl -X POST http://localhost:8080/predictions/clasificador \
  -H "Content-Type: application/json" \
  -d '{"data": [1.2, 0.8, 3.4, 2.1]}'
```

### 4.2 TensorFlow Serving

TensorFlow Serving es la solución oficial de Google para servir modelos SavedModel. A diferencia de TorchServe, está escrita completamente en C++ y está optimizada para alto throughput.

**Arranque con Docker:**

```bash
docker run -d \
  --name tf_serving \
  -p 8501:8501 \
  -p 8500:8500 \
  -v "$(pwd)/modelos:/models" \
  -e MODEL_NAME=clasificador \
  tensorflow/serving
```

TF Serving detecta automáticamente nuevas versiones del modelo si se añaden subdirectorios numerados bajo el directorio del modelo (por ejemplo, `modelos/clasificador/1/`, `modelos/clasificador/2/`).

**REST vs gRPC.** TF Serving expone dos interfaces. La REST API (puerto 8501) es más sencilla de usar desde cualquier cliente HTTP, pero tiene mayor overhead de serialización porque usa JSON. La gRPC API (puerto 8500) usa Protocol Buffers, es más eficiente en términos de latencia y es la opción recomendada para clientes de alta frecuencia escritos en Python, Go o C++.

```bash
# REST
curl -X POST http://localhost:8501/v1/models/clasificador:predict \
  -d '{"instances": [[1.2, 0.8, 3.4, 2.1]]}'
```

### 4.3 BentoML

BentoML es un framework de serving de alto nivel que abstrae los detalles de infraestructura y permite definir servicios de ML directamente en Python con decoradores.

**Definición de un servicio:**

```python
import bentoml
import numpy as np
from bentoml.io import NumpyNdarray

runner = bentoml.sklearn.get("clasificador:latest").to_runner()

svc = bentoml.Service("api_clasificador", runners=[runner])

@svc.api(input=NumpyNdarray(), output=NumpyNdarray())
async def predict(input_data: np.ndarray) -> np.ndarray:
    return await runner.predict.async_run(input_data)
```

**Runners.** Un Runner es la abstracción de BentoML para la carga y ejecución del modelo. Los runners pueden ejecutarse en procesos separados, lo que permite escalar la capacidad de inferencia de forma independiente al número de workers HTTP.

**Bento.** El artefacto de despliegue de BentoML se llama Bento: un paquete que incluye el código del servicio, el modelo, las dependencias de Python y la configuración del entorno. Se construye con `bentoml build` y puede publicarse en BentoCloud o convertirse en una imagen Docker con `bentoml containerize`.

**Ejemplo completo con sklearn:**

```python
# guardar_modelo.py
import bentoml
from sklearn.ensemble import RandomForestClassifier

modelo = RandomForestClassifier()
modelo.fit(X_train, y_train)

bentoml.sklearn.save_model("clasificador", modelo)
```

### 4.4 Tabla comparativa de frameworks

| Framework | Lenguaje core | Protocolo | Gestión de versiones | Complejidad de setup | Mejor para |
|---|---|---|---|---|---|
| TorchServe | Java + Python | HTTP/gRPC | Si | Media | PyTorch en producción |
| TF Serving | C++ | REST/gRPC | Si (automática) | Baja (Docker) | TensorFlow, alto throughput |
| BentoML | Python | HTTP | Si | Baja | Prototipado rápido, sklearn |
| FastAPI custom | Python | HTTP | Manual | Media | Control total, APIs complejas |

---

## 5. FastAPI para inferencia

FastAPI se ha convertido en el estándar de facto para construir APIs de inferencia personalizadas en Python. Combina un rendimiento cercano a Node.js gracias a su base asíncrona (Starlette + uvicorn), validación automática de datos con Pydantic, y generación automática de documentación interactiva.

### 5.1 Diseño del endpoint de predicción

La estructura básica de una API de inferencia con FastAPI sigue un patrón bien definido: un esquema de entrada, un esquema de salida, la lógica de carga del modelo y el handler del endpoint.

### 5.2 Schemas Pydantic

Pydantic permite definir los contratos de la API con tipado estricto y validación automática. Cualquier petición que no cumpla el esquema devuelve un error 422 con un mensaje descriptivo sin ningún código adicional.

```python
from pydantic import BaseModel, Field
from typing import List

class EntradaPrediccion(BaseModel):
    features: List[float] = Field(
        ...,
        min_items=4,
        max_items=4,
        description="Vector de 4 características numéricas"
    )
    umbral: float = Field(default=0.5, ge=0.0, le=1.0)

class SalidaPrediccion(BaseModel):
    clase_predicha: int
    probabilidad: float
    modelo_version: str
```

### 5.3 Carga del modelo al arranque con lifespan

Un error frecuente en implementaciones ingenuas de FastAPI es cargar el modelo en cada petición. Esto multiplica la latencia por el tiempo de deserialización del modelo en cada llamada. La solución correcta es cargar el modelo una sola vez al arrancar la aplicación usando el context manager `lifespan`.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
import joblib

estado_app = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Arranque: cargar modelo
    estado_app["modelo"] = joblib.load("modelo.joblib")
    estado_app["version"] = "1.0.0"
    yield
    # Apagado: limpiar recursos
    estado_app.clear()

app = FastAPI(title="API de Inferencia", lifespan=lifespan)
```

### 5.4 Manejo de errores

```python
from fastapi import HTTPException
import numpy as np

@app.post("/predict", response_model=SalidaPrediccion)
async def predecir(entrada: EntradaPrediccion):
    try:
        X = np.array([entrada.features])
        modelo = estado_app["modelo"]
        
        probabilidades = modelo.predict_proba(X)[0]
        clase = int(probabilidades.argmax())
        prob = float(probabilidades.max())
        
        return SalidaPrediccion(
            clase_predicha=clase,
            probabilidad=prob,
            modelo_version=estado_app["version"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en inferencia: {str(e)}"
        )
```

### 5.5 Documentación automática

FastAPI genera automáticamente una interfaz Swagger UI accesible en `/docs` y una especificación OpenAPI en `/openapi.json`. Esta documentación es interactiva: permite enviar peticiones de prueba directamente desde el navegador sin herramientas adicionales. Para un servicio de ML, esto es especialmente valioso durante la integración con otros equipos, ya que los consumidores de la API pueden explorar los contratos sin consultar documentación externa.

### 5.6 Ejemplo completo funcional

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import joblib
import numpy as np

estado_app = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    estado_app["modelo"] = joblib.load("modelo.joblib")
    estado_app["version"] = "1.0.0"
    yield
    estado_app.clear()

app = FastAPI(
    title="Clasificador API",
    description="Endpoint de inferencia para clasificacion binaria",
    version="1.0.0",
    lifespan=lifespan
)

class EntradaPrediccion(BaseModel):
    features: List[float] = Field(..., min_items=4, max_items=4)

class SalidaPrediccion(BaseModel):
    clase_predicha: int
    probabilidad: float
    modelo_version: str

@app.get("/health")
async def health_check():
    return {"status": "ok", "modelo_cargado": "modelo" in estado_app}

@app.post("/predict", response_model=SalidaPrediccion)
async def predecir(entrada: EntradaPrediccion):
    if "modelo" not in estado_app:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    try:
        X = np.array([entrada.features])
        proba = estado_app["modelo"].predict_proba(X)[0]
        return SalidaPrediccion(
            clase_predicha=int(proba.argmax()),
            probabilidad=float(proba.max()),
            modelo_version=estado_app["version"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

Para ejecutar: `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4`

---

## 6. Containerización

Docker es la herramienta estándar para empaquetar y desplegar servicios de ML. Un contenedor garantiza que el entorno de ejecución en producción sea idéntico al entorno de desarrollo, eliminando la clase entera de bugs relacionados con incompatibilidades de versiones.

### 6.1 Dockerfile optimizado para ML con multi-stage build

Las imágenes Docker para ML tienen tendencia a ser grandes porque las dependencias (PyTorch, TensorFlow, scikit-learn con sus dependencias C) son pesadas. Un build multi-stage permite separar el entorno de construcción del entorno de ejecución, reduciendo significativamente el tamaño de la imagen final.

```dockerfile
# Etapa 1: construcción de dependencias
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

# Etapa 2: imagen de producción
FROM python:3.11-slim AS production

# Usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copiar solo los paquetes instalados
COPY --from=builder /root/.local /home/appuser/.local

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

USER appuser

ENV PATH="/home/appuser/.local/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### 6.2 Modelo como artefacto en imagen vs volumen

Hay dos estrategias para gestionar el artefacto del modelo dentro del contenedor:

**Modelo embebido en la imagen.** El archivo del modelo se copia en la imagen durante el build con `COPY modelo.joblib /app/`. Ventaja: la imagen es completamente autónoma y reproducible. La misma imagen siempre sirve la misma versión del modelo. Desventaja: actualizar el modelo requiere reconstruir y redesplegar la imagen.

**Modelo montado como volumen.** El contenedor espera el modelo en una ruta predefinida que se monta como volumen Docker en tiempo de ejecución. Ventaja: el modelo puede actualizarse sin reconstruir la imagen. Desventaja: la imagen no es autónoma; el orquestador debe garantizar que el volumen está disponible.

En entornos con CI/CD maduro, la primera estrategia es la recomendada porque alinea la versión del código con la versión del modelo de forma explícita y auditable.

### 6.3 Variables de entorno para configuración

La configuración que varía entre entornos (ruta del modelo, nivel de logging, timeouts) debe externalizarse mediante variables de entorno, nunca hardcodearse:

```python
import os

RUTA_MODELO = os.getenv("MODEL_PATH", "modelo.joblib")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "32"))
```

### 6.4 Docker Compose para testing local

```yaml
version: "3.9"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL_PATH=/models/modelo.joblib
      - LOG_LEVEL=DEBUG
    volumes:
      - ./modelos:/models:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

---

## 7. ONNX Runtime

ONNX Runtime (ORT) es el motor de inferencia de alto rendimiento para modelos en formato ONNX, desarrollado por Microsoft. Es la capa que convierte el formato ONNX de interoperable a también eficiente.

### 7.1 InferenceSession

La API principal de ORT es `InferenceSession`. Carga el modelo y expone un método `run` que ejecuta la inferencia:

```python
import onnxruntime as ort
import numpy as np

sesion = ort.InferenceSession("modelo.onnx")

nombre_input = sesion.get_inputs()[0].name
nombre_output = sesion.get_outputs()[0].name

X = np.array([[1.2, 0.8, 3.4, 2.1]], dtype=np.float32)
resultado = sesion.run([nombre_output], {nombre_input: X})
print(resultado[0])
```

### 7.2 Proveedores de ejecución

ORT soporta múltiples Execution Providers (EP) que determinan en qué hardware se ejecuta la inferencia:

- **CPUExecutionProvider**: el proveedor por defecto, sin dependencias adicionales.
- **CUDAExecutionProvider**: ejecuta en GPU NVIDIA usando CUDA. Requiere CUDA y cuDNN instalados.
- **TensorrtExecutionProvider**: usa NVIDIA TensorRT para optimizar el grafo en la GPU específica del sistema. Produce la latencia más baja para modelos de visión, pero el proceso de optimización inicial puede tardar varios minutos.
- **CoreMLExecutionProvider**: para inferencia acelerada en Apple Silicon.

```python
# Configurar prioridad de proveedores
sesion = ort.InferenceSession(
    "modelo.onnx",
    providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
)
```

ORT intentará usar el primer proveedor de la lista y caerá al siguiente si no está disponible.

### 7.3 Benchmarks de latencia vs PyTorch nativo

En inferencia CPU con batch size 1, ONNX Runtime supera sistemáticamente a PyTorch por los siguientes motivos: ORT aplica optimizaciones de grafo en tiempo de carga (fusión de operadores, eliminación de nodos redundantes, layout optimization), mientras que PyTorch eager mode tiene overhead de Python en cada operación. En benchmarks con modelos de clasificación tabular y redes convolucionales pequeñas, las mejoras oscilan entre 20% y 50% de reducción de latencia media.

Para modelos grandes con GPU, la diferencia entre ORT+CUDA y PyTorch nativo es menor, y TensorRT como EP de ORT ofrece las mayores ganancias a costa de un proceso de compilación específico para el hardware objetivo.

---

## 8. Warm-up y cold start

### 8.1 El problema de la primera inferencia

Cuando un servidor de inferencia arranca o cuando un nuevo worker se inicializa, la primera petición de inferencia es significativamente más lenta que las siguientes. Este fenómeno, conocido como cold start, tiene varias causas:

- El modelo debe deserializarse desde disco y cargarse en memoria RAM (o VRAM si hay GPU).
- Los frameworks compilados (TorchScript, TensorRT) realizan optimizaciones de compilación JIT en la primera ejecución para el shape de entrada específico.
- El sistema operativo debe mapear las páginas de memoria del modelo, generando page faults en el primer acceso.
- CUDA inicializa el contexto de la GPU en la primera llamada, lo que puede añadir entre 1 y 5 segundos.

El resultado práctico es que la primera petición puede tardar 10-100 veces más que las peticiones subsiguientes. En un entorno de producción con SLAs de latencia, esto es inaceptable.

### 8.2 Estrategias de precalentamiento

**Warm-up al arranque.** La estrategia más directa es ejecutar un número de inferencias ficticias durante el arranque del servidor, antes de empezar a aceptar tráfico real. Esto fuerza todas las inicializaciones lazy.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    modelo = joblib.load("modelo.joblib")
    
    # Warm-up: 10 inferencias ficticias
    dummy_input = np.zeros((1, 4), dtype=np.float32)
    for _ in range(10):
        modelo.predict(dummy_input)
    
    estado_app["modelo"] = modelo
    yield
    estado_app.clear()
```

Para ONNX Runtime con GPU, el warm-up es especialmente importante porque la primera ejecución de cada operador en CUDA realiza la selección del kernel óptimo (cuDNN autotuning).

**Readiness probe.** En Kubernetes, la diferencia entre `livenessProbe` y `readinessProbe` es crítica para el cold start. El pod no debe recibir tráfico hasta que el readiness probe devuelva éxito. El endpoint `/health` de la API debe devolver 503 mientras el warm-up no ha completado.

```python
@app.get("/health")
async def health():
    if "modelo" not in estado_app:
        raise HTTPException(status_code=503, detail="Inicializando")
    return {"status": "ready"}
```

### 8.3 Caching de predicciones frecuentes con Redis

Para distribuciones de tráfico donde un subconjunto pequeño de entradas concentra la mayoría de las peticiones (por ejemplo, clasificación de textos donde ciertos inputs se repiten frecuentemente), el caching semántico de predicciones elimina la necesidad de inferencia para entradas ya procesadas.

La clave del cache puede ser el hash SHA-256 del vector de entrada serializado. Redis, con su soporte nativo para TTL (time-to-live), es el backend estándar para este patrón:

```python
import redis
import hashlib
import json
import numpy as np

cache = redis.Redis(host="redis", port=6379, db=0)
TTL_SEGUNDOS = 3600

def clave_cache(features: list) -> str:
    datos = json.dumps(features, sort_keys=True)
    return f"pred:{hashlib.sha256(datos.encode()).hexdigest()}"

@app.post("/predict", response_model=SalidaPrediccion)
async def predecir(entrada: EntradaPrediccion):
    clave = clave_cache(entrada.features)
    
    # Intentar desde cache
    cached = cache.get(clave)
    if cached:
        return SalidaPrediccion(**json.loads(cached))
    
    # Inferencia
    X = np.array([entrada.features])
    proba = estado_app["modelo"].predict_proba(X)[0]
    resultado = SalidaPrediccion(
        clase_predicha=int(proba.argmax()),
        probabilidad=float(proba.max()),
        modelo_version=estado_app["version"]
    )
    
    # Guardar en cache
    cache.setex(clave, TTL_SEGUNDOS, resultado.model_dump_json())
    
    return resultado
```

**Consideraciones del cache.** El caching de predicciones solo es apropiado cuando las predicciones son deterministas (mismo input, mismo output siempre) y cuando el modelo no cambia frecuentemente. Al actualizar el modelo, es necesario invalidar el cache completo o usar un namespace que incluya la versión del modelo en la clave. Para entradas continuas (donde la probabilidad de colisión de hashes entre entradas distintas es baja), el caching es efectivo. Para entradas con alta cardinalidad o alta variabilidad, el hit rate del cache será bajo y el overhead de la consulta a Redis puede no compensar.

---

## 9. Actividades practicas

### Actividad 1 — Exportar y comparar formatos de serialización

**Objetivo:** Comprender las diferencias prácticas entre formatos de serialización.

Entrena un modelo `GradientBoostingClassifier` de scikit-learn sobre el dataset `breast_cancer` de sklearn. Serializa el modelo en tres formatos: joblib, ONNX (usando skl2onnx) y pickle. Para cada formato: mide el tamaño del archivo resultante en disco, mide el tiempo de carga del modelo, ejecuta 1000 inferencias con el mismo dataset y mide la latencia media y el percentil 99. Presenta los resultados en una tabla comparativa y razona qué formato elegirías para un servicio de producción de baja latencia y por qué.

**Entregable:** notebook con los experimentos y una tabla de resultados con conclusiones escritas.

### Actividad 2 — API de inferencia con FastAPI y ONNX Runtime

**Objetivo:** Construir una API de inferencia completa y containerizada.

Partiendo del modelo ONNX de la Actividad 1, implementa una API FastAPI que cumpla los siguientes requisitos: carga el modelo usando ONNX Runtime al arranque con lifespan; expone un endpoint `POST /predict` con validación Pydantic estricta; expone un endpoint `GET /health` que devuelva 503 si el modelo no está cargado; implementa manejo de errores con códigos HTTP apropiados; incluye un endpoint `GET /model-info` que devuelva metadatos del modelo (nombre de inputs/outputs, tipos, shapes). Containeriza la API con un Dockerfile multi-stage y escribe un docker-compose que incluya la API. Verifica que la documentación Swagger en `/docs` refleja correctamente los schemas.

**Entregable:** directorio con el código de la API, Dockerfile, docker-compose.yml y capturas de pantalla de la documentación Swagger.

### Actividad 3 — Despliegue con BentoML y comparativa de frameworks

**Objetivo:** Experimentar con un framework de serving de alto nivel.

Implementa el mismo clasificador usando BentoML: guarda el modelo en el BentoML store, define un servicio con `@bentoml.Service`, implementa el método de predicción como handler asíncrono, construye el Bento y conviértelo en imagen Docker. Una vez funcionando, compara BentoML con la implementación manual de FastAPI de la Actividad 2 en los siguientes aspectos: cantidad de código necesario, facilidad de actualización del modelo, capacidades de logging y métricas out-of-the-box, y limitaciones encontradas.

**Entregable:** código del servicio BentoML, imagen Docker construida, y un documento de no más de 500 palabras con la comparativa razonada.

### Actividad 4 — Implementar caching con Redis y medir el impacto

**Objetivo:** Medir el impacto del caching de predicciones en latencia y throughput.

Partiendo de la API de la Actividad 2, añade caching con Redis usando el patrón descrito en la sección 8.3. Diseña un experimento de carga con `locust` o `wrk` que envíe peticiones con un 70% de entradas repetidas y un 30% de entradas nuevas. Mide: latencia media con y sin cache, latencia p99 con y sin cache, throughput (requests/segundo) con y sin cache, hit rate del cache. Analiza si el caching tiene sentido para tu distribución de tráfico simulada y en qué escenarios reales dejaría de ser beneficioso.

**Entregable:** código modificado de la API, script de prueba de carga, gráficas de resultados y análisis escrito de no más de 400 palabras.

---

## 10. Referencias

### Documentacion oficial de frameworks

- **TorchServe** — Documentacion oficial, arquitectura, handlers y ejemplos de despliegue: https://pytorch.org/serve/

- **TensorFlow Serving** — Guia de instalacion, configuracion con Docker y API REST/gRPC: https://www.tensorflow.org/tfx/guide/serving

- **BentoML** — Documentacion de servicios, runners y containerizacion: https://docs.bentoml.com/

- **FastAPI** — Tutorial completo, Pydantic integration, lifespan events y deployment: https://fastapi.tiangolo.com/

- **ONNX** — Especificacion del formato, operadores soportados y herramientas de conversion: https://onnx.ai/

- **ONNX Runtime** — API de Python, execution providers y guias de optimizacion: https://onnxruntime.ai/docs/

- **skl2onnx** — Conversion de modelos scikit-learn a ONNX: https://onnx.ai/sklearn-onnx/

### Libros y articulos de referencia

- Huyen, C. (2022). *Designing Machine Learning Systems: An Iterative Process for Production-Ready Applications*. O'Reilly Media. Capitulos 7 (Model Deployment and Prediction Service) y 9 (Continual Learning and Test in Production).

- Kleppmann, M. (2017). *Designing Data-Intensive Applications*. O'Reilly Media. Capitulo 1 (Reliable, Scalable, and Maintainable Applications) — aplicable directamente al diseno de servicios de inferencia.

- **ML Engineering** — Burkov, A. (2020). *Machine Learning Engineering*. Disponible en: http://www.mlebook.com/

### Recursos complementarios

- **ONNX Model Zoo** — Coleccion de modelos preentrenados en formato ONNX listos para usar con ORT: https://github.com/onnx/models

- **Uvicorn** — Servidor ASGI de alto rendimiento para FastAPI: https://www.uvicorn.org/

- **Redis documentacion** — Comandos, TTL y patrones de caching: https://redis.io/docs/

- **Docker best practices para Python** — Guia oficial de optimizacion de imagenes: https://docs.docker.com/language/python/

---

*Unidad Didactica 2 — Despliegue de modelos con frameworks especializados*
*MP03 Desarrollo de Componentes de Machine Learning — CFS1 Gestion de Datos y Entrenamiento IA*
