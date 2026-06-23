---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD3 · Integración de modelos en aplicaciones | MP03'
footer: 'CFS Gestión de datos y entrenamiento IA (IAD)'
---

<style>
section { font-family: 'Segoe UI', Arial, sans-serif; }
h1 { color: #1e3a5f; }
h2 { color: #1e3a5f; border-bottom: 2px solid #3b82f6; padding-bottom: 6px; }
h3 { color: #2563eb; }
table { font-size: 0.82em; width: 100%; }
ul, ol { font-size: 0.88em; }
blockquote { border-left: 4px solid #3b82f6; background: #eff6ff; padding: 8px 16px; border-radius: 4px; }
footer, header { font-size: 0.6em; color: #6b7280; }
section.lead h1 { font-size: 2em; text-align: center; margin-top: 80px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
pre { background: #1e293b; color: #e2e8f0; padding: 16px; border-radius: 8px; font-size: 0.8em; }
</style>

<!-- _class: lead -->

# UD3 · Integración de modelos en aplicaciones

**MP03 · Desarrollo de componentes para sistemas de ML**
CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de aprendizaje

Al finalizar esta unidad el alumno sera capaz de:

- Exportar modelos en formatos estandar de portabilidad (ONNX, SavedModel, TorchScript)
- Implementar APIs de inferencia REST y gRPC con FastAPI y Flask
- Aplicar cuantizacion de vectores y representacion compacta de datos complejos
- Comprender la discretizacion del espacio de entrada con autoencoders y SOM
- Disenar redes recurrentes con puertas (LSTM, GRU) para procesamiento de secuencias
- Seleccionar la arquitectura de red neuronal adecuada (MLP, CNN, GNN) segun el tipo de dato
- Integrar modelos preentrenados desde HuggingFace Hub y otros repositorios

---

## Mapa de la unidad

```
UD3 · Integracion de modelos en aplicaciones
│
├── 1. Estandarizacion y portabilidad
│   └── ONNX, TorchScript, SavedModel, PMML
│
├── 2. API de inferencia
│   └── FastAPI REST, gRPC, BentoML
│
├── 3. Representacion compacta de datos
│   ├── Cuantizacion de vectores
│   └── Autoencoders y SOM (Kohonen)
│
├── 4. Arquitecturas para secuencias y grafos
│   ├── LSTM, GRU (puertas)
│   └── Transformers, GNN
│
└── 5. Integracion de modelos preentrenados
    └── HuggingFace Hub, ONNX Model Zoo
```

---

## Estandarizacion de modelos: formatos de portabilidad

| Formato | Framework origen | Compatibilidad | Ideal para |
|---|---|---|---|
| **ONNX** | PyTorch, TF, Sklearn | Muy alta (100+ runtimes) | Portabilidad entre frameworks |
| **TorchScript** | PyTorch exclusivamente | Python y C++ | Inferencia en produccion PyTorch |
| **TF SavedModel** | TensorFlow / Keras | TF Serving, TFLite, TF.js | Ecosistema TensorFlow completo |
| **PMML** | Sklearn, R, SAS | Java, Python, R | ML clasico en entornos enterprise |
| **CoreML** | Cualquiera (via conversion) | Apple (iOS, macOS) | Inferencia en dispositivos Apple |

> ONNX es el estandar de facto para interoperabilidad: permite entrenar en PyTorch y ejecutar en TensorRT, OpenVINO o CoreML sin cambiar el codigo de inferencia.

---

## Exportacion a ONNX desde PyTorch

```python
import torch
import torch.onnx

def exportar_a_onnx(modelo, ruta_salida: str, n_features: int):
    """
    Exporta un modelo PyTorch a formato ONNX con validacion.
    """
    modelo.eval()

    # Ejemplo de entrada con las dimensiones correctas
    entrada_dummy = torch.randn(1, n_features)

    torch.onnx.export(
        modelo,
        entrada_dummy,
        ruta_salida,
        opset_version=17,
        input_names=["entrada"],
        output_names=["prediccion"],
        dynamic_axes={
            "entrada":    {0: "batch_size"},
            "prediccion": {0: "batch_size"}
        }
    )
    print(f"Modelo exportado a: {ruta_salida}")

    # Validar el modelo exportado
    import onnx
    modelo_onnx = onnx.load(ruta_salida)
    onnx.checker.check_model(modelo_onnx)
    print("Validacion ONNX: OK")

exportar_a_onnx(modelo_entrenado, "artifacts/modelo_v1.onnx", n_features=20)
```

---

## Inferencia con ONNX Runtime

```python
import onnxruntime as ort
import numpy as np

class InferenciadorONNX:
    """
    Ejecutor de inferencia con ONNX Runtime.
    Soporta CPU y GPU (CUDA) de forma transparente.
    """

    def __init__(self, ruta_modelo: str, dispositivo: str = "cpu"):
        proveedores = (
            ["CUDAExecutionProvider", "CPUExecutionProvider"]
            if dispositivo == "cuda"
            else ["CPUExecutionProvider"]
        )
        self.sesion = ort.InferenceSession(ruta_modelo, providers=proveedores)
        self.nombre_entrada  = self.sesion.get_inputs()[0].name
        self.nombre_salida   = self.sesion.get_outputs()[0].name

    def predecir(self, X: np.ndarray) -> np.ndarray:
        if X.ndim == 1:
            X = X.reshape(1, -1)
        X = X.astype(np.float32)
        resultados = self.sesion.run(
            [self.nombre_salida],
            {self.nombre_entrada: X}
        )
        return resultados[0]

inferenciador = InferenciadorONNX("artifacts/modelo_v1.onnx")
prediccion = inferenciador.predecir(np.random.randn(10, 20))
print(f"Shape de salida: {prediccion.shape}")
```

---

## API de inferencia con FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import numpy as np
from typing import List
import logging

app = FastAPI(
    title="API de Inferencia ML",
    version="1.0.0",
    description="Servicio de prediccion basado en ONNX Runtime"
)
logger = logging.getLogger(__name__)
inferenciador = InferenciadorONNX("artifacts/modelo_v1.onnx")

class EntradaPrediccion(BaseModel):
    caracteristicas: List[float] = Field(..., min_items=1, description="Vector de entrada")

class SalidaPrediccion(BaseModel):
    clase_predicha: int
    probabilidades: List[float]
    version_modelo: str = "1.0.0"

@app.post("/predecir", response_model=SalidaPrediccion)
async def predecir(entrada: EntradaPrediccion):
    try:
        X = np.array(entrada.caracteristicas)
        resultado = inferenciador.predecir(X)
        return SalidaPrediccion(
            clase_predicha=int(resultado.argmax()),
            probabilidades=resultado.tolist()
        )
    except Exception as e:
        logger.error(f"Error en inferencia: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Despliegue de la API con Docker y uvicorn

```dockerfile
# Dockerfile para el servicio de inferencia
FROM python:3.11-slim

WORKDIR /app
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY src/api.py ./src/
COPY artifacts/modelo_v1.onnx ./artifacts/

EXPOSE 8000
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```bash
# Construir y ejecutar
docker build -t inferencia-ml:v1.0 .
docker run -p 8000:8000 inferencia-ml:v1.0

# Probar el endpoint
curl -X POST "http://localhost:8000/predecir" \
     -H "Content-Type: application/json" \
     -d '{"caracteristicas": [1.2, -0.5, 3.1, 0.8]}'
```

> El numero de workers (`--workers 4`) permite atender peticiones en paralelo. Para inferencia con GPU, usar un solo worker y gestionar la concurrencia internamente.

---

## Cuantizacion de vectores y representacion compacta

La cuantizacion de vectores mapea vectores continuos de alta dimension a un conjunto discreto de codigos (libro de codigos), reduciendo la memoria y la latencia de busqueda.

### Aplicaciones en ML

| Aplicacion | Como se usa la cuantizacion |
|---|---|
| Bases de datos vectoriales | FAISS, Hnswlib: busqueda aproximada de vecinos mas cercanos |
| Compresion de embeddings | Reducir de float32 a int8 sin perder precision significativa |
| RAG (Retrieval-Augmented Generation) | Recuperacion eficiente de documentos relevantes |
| Sistemas de recomendacion | Busqueda de similitud a escala de millones de items |

```python
import faiss
import numpy as np

# Crear un indice FAISS con cuantizacion de producto
d = 128          # dimension del vector
n_subvectores = 8
n_bits = 8       # 256 centroides por subvector

indice = faiss.IndexPQ(d, n_subvectores, n_bits)
vectores = np.random.randn(10000, d).astype(np.float32)
indice.train(vectores)
indice.add(vectores)

# Busqueda de los 5 vecinos mas cercanos
consulta = np.random.randn(1, d).astype(np.float32)
distancias, indices = indice.search(consulta, k=5)
```

---

## Autoencoders: compresion y discretizacion del espacio

```python
import torch
import torch.nn as nn

class Autoencoder(nn.Module):
    """
    Autoencoder que aprende una representacion comprimida del espacio de entrada.
    Util para deteccion de anomalias y reduccion de dimensionalidad no lineal.
    """

    def __init__(self, n_entrada: int, n_latente: int):
        super().__init__()
        self.codificador = nn.Sequential(
            nn.Linear(n_entrada, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, n_latente)
        )
        self.decodificador = nn.Sequential(
            nn.Linear(n_latente, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, n_entrada)
        )

    def forward(self, x):
        z = self.codificador(x)
        return self.decodificador(z), z

ae = Autoencoder(n_entrada=784, n_latente=32)
# El vector z de dimension 32 es la representacion comprimida
```

---

## Mapas Autoorganizativos de Kohonen (SOM)

El SOM es una red neuronal no supervisada que proyecta datos de alta dimension en una cuadricula 2D preservando la topologia del espacio original.

```python
from minisom import MiniSom
import numpy as np
import matplotlib.pyplot as plt

# Datos de entrenamiento (simulados)
X = np.random.randn(1000, 10)

# Crear y entrenar el SOM (cuadricula 10x10)
som = MiniSom(
    x=10, y=10,
    input_len=10,
    sigma=1.0,
    learning_rate=0.5,
    random_seed=42
)
som.random_weights_init(X)
som.train(X, num_iteration=5000, verbose=False)

# Mapa de activacion: donde se activa cada muestra
activaciones = np.array([som.winner(x) for x in X])
print(f"Neuronas ganadoras unicas: {len(set(map(tuple, activaciones)))}")
```

**Aplicaciones:**
- Clustering no supervisado de datos complejos
- Visualizacion de espacios de alta dimension
- Deteccion de patrones en datos sin etiqueta

---

## Redes recurrentes con puertas: LSTM y GRU

### Mecanismo de puertas en LSTM

```
Entrada x_t ─┐
              ├─ Puerta de olvido  (f) → que olvidar del estado anterior
Estado h_{t-1}├─ Puerta de entrada (i) → que informacion nueva guardar
              ├─ Celda candidata   (g) → contenido candidato a guardar
              └─ Puerta de salida  (o) → que parte del estado exponer

Estado de celda c_t = f * c_{t-1} + i * g
Estado oculto h_t = o * tanh(c_t)
```

| Arquitectura | Puertas | Parametros | Cuando usar |
|---|---|---|---|
| **LSTM** | 4 (f, i, g, o) | Mas | Secuencias largas, dependencias distantes |
| **GRU** | 2 (reset, update) | Menos | Secuencias medias, entrenamiento mas rapido |
| **Bidireccional** | 2x (LSTM o GRU) | Doble | Clasificacion de texto, NER (no streaming) |

---

## Transformers: atencion multi-cabeza

```python
import torch
import torch.nn as nn

class BloqueTranformer(nn.Module):
    """
    Bloque Transformer encoder: atencion multi-cabeza + FFN + LayerNorm.
    """

    def __init__(self, d_modelo: int, n_cabezas: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.atencion  = nn.MultiheadAttention(d_modelo, n_cabezas, dropout=dropout, batch_first=True)
        self.ffn = nn.Sequential(
            nn.Linear(d_modelo, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_modelo)
        )
        self.norm1 = nn.LayerNorm(d_modelo)
        self.norm2 = nn.LayerNorm(d_modelo)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mascara=None):
        # Atencion con conexion residual
        attn_out, _ = self.atencion(x, x, x, key_padding_mask=mascara)
        x = self.norm1(x + self.dropout(attn_out))
        # FFN con conexion residual
        x = self.norm2(x + self.dropout(self.ffn(x)))
        return x

bloque = BloqueTranformer(d_modelo=256, n_cabezas=8, d_ff=1024)
```

---

## Redes Convolucionales (CNN): datos espaciales

```python
import torch.nn as nn

class CNNClasificador(nn.Module):
    """
    CNN para clasificacion de imagenes con arquitectura progressiva.
    """

    def __init__(self, n_clases: int):
        super().__init__()
        self.extractor = nn.Sequential(
            # Bloque 1: 3→32 canales, mapa 224→112
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32), nn.ReLU(),
            nn.MaxPool2d(2),

            # Bloque 2: 32→64 canales, mapa 112→56
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64), nn.ReLU(),
            nn.MaxPool2d(2),

            # Bloque 3: 64→128 canales, mapa 56→28
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128), nn.ReLU(),
            nn.AdaptiveAvgPool2d((7, 7))   # salida fija independiente del tamano de entrada
        )
        self.clasificador = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 7 * 7, 512), nn.ReLU(), nn.Dropout(0.4),
            nn.Linear(512, n_clases)
        )

    def forward(self, x):
        return self.clasificador(self.extractor(x))
```

---

## Integracion de modelos preentrenados desde HuggingFace

```python
from transformers import pipeline, AutoModel, AutoTokenizer
import torch

# Opcion 1: pipeline de alto nivel (prototipado rapido)
clasificador = pipeline(
    "text-classification",
    model="PlanTL-GOB-ES/roberta-base-bne",   # RoBERTa en espanol
    device=0 if torch.cuda.is_available() else -1
)
resultado = clasificador("El servicio fue excelente y muy rapido.")
print(resultado)  # [{'label': 'POS', 'score': 0.994}]

# Opcion 2: integracion directa con control total
tokenizador = AutoTokenizer.from_pretrained("PlanTL-GOB-ES/roberta-base-bne")
modelo = AutoModel.from_pretrained("PlanTL-GOB-ES/roberta-base-bne")

tokens = tokenizador("Texto de ejemplo", return_tensors="pt", truncation=True)
with torch.no_grad():
    salida = modelo(**tokens)

# El vector CLS es la representacion de la frase completa
embedding = salida.last_hidden_state[:, 0, :]
print(f"Dimension del embedding: {embedding.shape}")  # [1, 768]
```

---

## Actividad practica — UD3

### Servicio de inferencia con API REST

**Escenario:** integrar un modelo de clasificacion de sentimiento de textos en espanol como microservicio consumible por otras aplicaciones.

**Tareas:**
1. Descargar un modelo preentrenado de HuggingFace para clasificacion de sentimiento en espanol
2. Exportar el modelo a ONNX con `optimum` o `torch.onnx`
3. Implementar la clase `InferenciadorONNX` con soporte para batch de textos
4. Crear una API FastAPI con los endpoints `/predecir` y `/health`
5. Escribir un `Dockerfile` para el servicio con `uvicorn`
6. Probar el servicio con `curl` y documentar la API con los ejemplos de uso

**Entregable:** repositorio con `src/api.py`, `Dockerfile`, `requirements-api.txt` y captura del endpoint `/docs` de FastAPI.

---

## Puntos clave — UD3

- ONNX es el formato de portabilidad recomendado: permite ejecutar el modelo en cualquier hardware sin depender del framework de entrenamiento
- FastAPI es la libreria de referencia para APIs de inferencia en Python: es asincrona, tipada y genera documentacion automatica
- La cuantizacion de vectores permite busqueda de similitud a escala de millones de elementos en milisegundos (FAISS, Annoy)
- Los autoencoders aprenden representaciones comprimidas no lineales: utiles para deteccion de anomalias y preprocesado de datos complejos
- Los SOM de Kohonen proyectan datos de alta dimension en mapas 2D preservando la topologia: utiles para clustering visual
- La eleccion entre LSTM y GRU depende de la longitud de la secuencia y el presupuesto de computo: GRU es mas rapido con resultados similares en secuencias cortas
- Los modelos preentrenados de HuggingFace Hub reducen el tiempo de desarrollo en un orden de magnitud: siempre evaluar si existe un modelo relevante antes de entrenar desde cero

---

## Criterios de evaluacion — UD3

- Exporta el modelo en formato ONNX o SavedModel con validacion de la portabilidad
- Expone el modelo mediante una API REST con FastAPI incluyendo validacion de entrada y manejo de errores
- Aplica cuantizacion de vectores para busqueda eficiente de similitud cuando el problema lo requiere
- Selecciona la arquitectura de red neuronal (MLP, CNN, RNN, Transformer, GNN) justificando la eleccion segun la naturaleza del dato
- Integra modelos preentrenados desde HuggingFace Hub u otros repositorios de forma correcta

---

<!-- _class: lead -->

[← Volver a MP03](../)
