---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD2 · Configuración del modelo y del entorno | MP02 · Entrenamiento de modelos de aprendizaje automático'
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

# UD2 · Configuración del modelo y del entorno de entrenamiento

**MP02 · Entrenamiento de modelos de aprendizaje automático**

CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Seleccionar el framework más adecuado según el tipo de problema y la familia de modelos
- Configurar una arquitectura neuronal desde cero o cargar y adaptar un modelo preentrenado
- Elegir la función de pérdida correcta según el tipo de tarea
- Establecer los parámetros iniciales del algoritmo de optimización (learning rate, batch size, épocas)
- Preparar un entorno de cómputo reproducible con control de semillas y versionado de dependencias
- Documentar la configuración completa del modelo y del entorno

---

## Frameworks de ML — Ecosistema y posicionamiento

Los **frameworks** son el entorno de programación que proporciona las primitivas matemáticas, la diferenciación automática y las utilidades de entrenamiento. La elección del framework afecta a la flexibilidad, el rendimiento, el ecosistema de herramientas y la empleabilidad del equipo.

**Contexto industrial actual:**
- PyTorch domina en investigación y startups de IA (>70% de los artículos en NeurIPS 2024)
- TensorFlow/Keras sigue siendo el estándar en muchos equipos de producción empresarial
- Scikit-learn es insustituible para ML clásico tabular en industria
- HuggingFace actúa como capa de abstracción sobre PyTorch y TF para NLP y visión

---

## Frameworks — Tabla comparativa

| Framework | Paradigma | Fortaleza principal | Ecosistema |
|---|---|---|---|
| **Scikit-learn** | ML clásico | API unificada, pipelines, preprocessing | joblib, imbalanced-learn, feature-engine |
| **PyTorch** | Deep learning | Flexibilidad, grafos dinámicos, investigación | Lightning, HuggingFace, Optuna |
| **TensorFlow / Keras** | Deep learning | Despliegue, TFLite, TF Serving, TPU | Keras, TFX, tf.data |
| **HuggingFace Transformers** | LLMs, Visión, Audio | Modelos preentrenados, fine-tuning | Datasets, PEFT, Accelerate |
| **JAX** | Investigación avanzada | Compilación XLA, paralelismo automático | Flax, Haiku |

---

## Frameworks — Código de comparación básica

```python
# Scikit-learn: clasificador tabular en 5 líneas
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

clf = Pipeline([
    ("scaler", StandardScaler()),
    ("rf", RandomForestClassifier(n_estimators=100, random_state=42))
])
clf.fit(X_train, y_train)

# PyTorch: red neuronal simple
import torch.nn as nn

class RedSimple(nn.Module):
    def __init__(self, n_entradas, n_salidas):
        super().__init__()
        self.capas = nn.Sequential(
            nn.Linear(n_entradas, 128), nn.ReLU(),
            nn.Linear(128, 64), nn.ReLU(),
            nn.Linear(64, n_salidas)
        )
    def forward(self, x):
        return self.capas(x)
```

---

## Arquitectura — Modelo desde cero

Diseñar una arquitectura desde cero exige tomar decisiones explícitas sobre cada componente: número de capas, unidades por capa, funciones de activación, normalización y conexiones.

**Proceso de diseño:**

```
Entrada → [Capa de procesamiento] → [Capas ocultas] → [Capa de salida]
          (normalización, embed)    (n capas, n neuronas)  (según tarea)
```

**Principios guía:**
- Comenzar con arquitecturas simples y aumentar complejidad si el rendimiento es insuficiente
- El número de parámetros debe ser proporcional al volumen de datos de entrenamiento
- Usar arquitecturas validadas en la literatura para el tipo de dato concreto

---

## Arquitectura — Fine-tuning sobre modelo preentrenado

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# Cargar modelo base preentrenado (BERT en español)
modelo_id = "dccuchile/bert-base-spanish-wwm-cased"
tokenizer = AutoTokenizer.from_pretrained(modelo_id)
modelo = AutoModelForSequenceClassification.from_pretrained(
    modelo_id,
    num_labels=3  # positivo, negativo, neutro
)

# Estrategia de congelación gradual: congelar encoder, entrenar cabeza
for nombre, param in modelo.named_parameters():
    if "classifier" not in nombre:
        param.requires_grad = False

# Verificar que solo la cabeza tiene gradientes
params_activos = [n for n, p in modelo.named_parameters() if p.requires_grad]
print(f"Parámetros que se entrenan: {params_activos}")
```

---

## Función de pérdida — Concepto

La **función de pérdida** (*loss function*) cuantifica el error entre la predicción del modelo y el valor real. El algoritmo de optimización minimiza esta función actualizando los pesos. Elegir una función de pérdida inadecuada puede hacer que el modelo aprenda una objetivo diferente al deseado.

**Por qué importa la elección:**
- Determina qué errores penaliza más el modelo
- Afecta a la estabilidad del entrenamiento y la velocidad de convergencia
- Puede introducir sesgos si no se adapta al desbalance de clases

---

## Función de pérdida — Tabla por tipo de problema

| Tipo de problema | Función de pérdida | Fórmula simplificada | Cuándo usarla |
|---|---|---|---|
| Clasificación binaria | Binary Cross-Entropy (BCE) | -[y·log(p)+(1-y)·log(1-p)] | Dos clases, salida sigmoide |
| Clasificación multiclase | Categorical Cross-Entropy | -sum(y_i · log(p_i)) | N clases, salida softmax |
| Regresión | MSE (Mean Squared Error) | mean((y - y_hat)²) | Valores continuos, outliers no críticos |
| Regresión robusta | MAE (Mean Absolute Error) | mean(\|y - y_hat\|) | Valores continuos, outliers frecuentes |
| Desbalance de clases | Focal Loss | -alpha·(1-p)^gamma·log(p) | Clases muy desbalanceadas |
| Similitud / ranking | Contrastive Loss / Triplet | margin-based | Embeddings, búsqueda semántica |

---

## Función de pérdida — Código comparativo

```python
import torch
import torch.nn as nn

# Clasificación binaria
criterio_binario = nn.BCEWithLogitsLoss()

# Clasificación multiclase (integra softmax + CE)
criterio_multiclase = nn.CrossEntropyLoss()

# Regresión con MSE
criterio_regresion = nn.MSELoss()

# Regresión robusta con MAE
criterio_robusto = nn.L1Loss()

# Clasificacion con clases desbalanceadas (pesos por clase)
pesos = torch.tensor([1.0, 5.0, 2.0])  # clase 1 penaliza x5
criterio_ponderado = nn.CrossEntropyLoss(weight=pesos)
```

---

## Parámetros del algoritmo de optimización

**Tasa de aprendizaje (*learning rate*, lr):** controla el tamaño del paso en cada actualización de pesos. Es el hiperparámetro más crítico del entrenamiento.

| lr | Efecto |
|---|---|
| Muy alta (>0.1) | Oscilación, divergencia, nunca converge |
| Alta (0.01) | Convergencia rápida pero inestable |
| Moderada (1e-3) | Equilibrio habitual para Adam |
| Baja (1e-5) | Convergencia lenta pero estable; fine-tuning |

**Batch size:** muestras procesadas antes de actualizar pesos. Valores típicos: 16, 32, 64, 128, 256.

**Épocas:** número de pasadas completas sobre el conjunto de entrenamiento. Se determina por early stopping, no de forma fija.

---

## Optimizadores — Comparativa

```python
import torch.optim as optim

# SGD clásico con momentum
optimizer_sgd = optim.SGD(modelo.parameters(), lr=0.01, momentum=0.9, weight_decay=1e-4)

# Adam: adaptativo, estándar en deep learning
optimizer_adam = optim.Adam(modelo.parameters(), lr=1e-3, betas=(0.9, 0.999))

# AdamW: Adam con weight decay desacoplado (recomendado para Transformers)
optimizer_adamw = optim.AdamW(modelo.parameters(), lr=2e-5, weight_decay=0.01)

# Learning rate scheduler: reduce lr cuando la validacion no mejora
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer_adam, mode='min', factor=0.5, patience=3, verbose=True
)
```

---

## Entorno de cómputo — Opciones disponibles

| Hardware | Caso de uso | Tiempo estimado (ResNet-50, ImageNet) |
|---|---|---|
| **CPU** | Prototipado, ML clásico, datasets pequeños | Semanas |
| **GPU (NVIDIA CUDA)** | Deep learning estándar, fine-tuning | Horas - días |
| **TPU (Google)** | Modelos masivos, batch size muy grande | Minutos - horas |
| **Multi-GPU** | Entrenamiento distribuido en cluster | Horas |
| **Nube (Colab, SageMaker, Vertex AI)** | Sin hardware propio, bajo coste inicial | Variable |

**Gestión de entorno en local:**
- `conda` o `venv` para aislar dependencias por proyecto
- `requirements.txt` o `pyproject.toml` para fijar versiones exactas
- `Docker` o `Dev Containers` para entornos completamente reproducibles

---

## Reproducibilidad — Control de semillas

La reproducibilidad es un requisito profesional, no una opción. Sin control de semillas, dos ejecuciones del mismo código pueden producir modelos con rendimientos distintos, haciendo imposible la depuración y la comparación de experimentos.

```python
import random
import numpy as np
import torch
import os

def fijar_semilla(semilla: int = 42):
    """Fija todas las fuentes de aleatoriedad para reproducibilidad."""
    random.seed(semilla)
    np.random.seed(semilla)
    torch.manual_seed(semilla)
    torch.cuda.manual_seed_all(semilla)
    os.environ["PYTHONHASHSEED"] = str(semilla)
    # Para operaciones deterministas en CUDA (puede reducir rendimiento)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

fijar_semilla(42)
```

---

## Reproducibilidad — Versionado de dependencias

```bash
# Generar requirements.txt con versiones exactas
pip freeze > requirements.txt

# O con poetry (recomendado para proyectos nuevos)
poetry init
poetry add torch==2.2.0 scikit-learn==1.4.0 transformers==4.38.0

# O con conda
conda env export > environment.yml

# Recrear entorno en otra máquina
pip install -r requirements.txt
conda env create -f environment.yml
```

**Qué versionar junto al código:**
- Versión de Python
- Versiones exactas de todas las librerías (incluyendo dependencias transitivas)
- Versión de CUDA y cuDNN si se usa GPU
- Configuración completa del experimento (semilla, hiperparámetros, rutas de datos)

---

## Documentación de la configuración

Un experimento sin documentación no es reproducible. La documentación de configuración debe generarse automáticamente como parte del pipeline.

**Campos mínimos a registrar antes de cada entrenamiento:**

| Campo | Ejemplo |
|---|---|
| Fecha y hora de inicio | 2026-06-23T10:30:00 |
| Framework y versión | PyTorch 2.2.0 |
| Arquitectura | ResNet-50 preentrenada en ImageNet |
| Función de pérdida | CrossEntropyLoss |
| Optimizador y lr | AdamW, lr=2e-5 |
| Batch size | 32 |
| Épocas máximas | 50 (con early stopping, patience=5) |
| Semilla | 42 |
| Hardware | NVIDIA RTX 3090, 24GB VRAM |
| Dataset versión | v2.1 (hash SHA-256: a3f9...) |

---

## Actividad práctica — UD2

**Contexto:** Quieres construir un clasificador de texto para detectar comentarios tóxicos en una plataforma educativa. Tienes 8.000 comentarios etiquetados (70% no tóxico, 30% tóxico) en español.

**Tareas:**

1. Selecciona el framework y el modelo preentrenado más adecuado. Justifica la elección frente a dos alternativas
2. Configura la función de pérdida teniendo en cuenta el desbalance de clases. Incluye el código
3. Elige el optimizador y el learning rate inicial. Explica cómo ajustarías el lr a lo largo del entrenamiento
4. Escribe la función `fijar_semilla()` y explica qué pasaría si no se controla la aleatoriedad
5. Crea el documento de configuración del experimento con todos los campos de la tabla anterior

---

## Puntos clave — UD2

- El framework no determina el resultado: lo determinan la arquitectura, la pérdida y los datos; el framework es solo la herramienta
- La función de pérdida debe alinearse con el objetivo real del negocio, no con la costumbre del equipo
- El learning rate es el hiperparámetro más sensible: un valor incorrecto puede impedir que el modelo aprenda
- La reproducibilidad no es opcional: fijar semillas y versionar dependencias es tan importante como el código del modelo
- Fine-tuning sobre modelos preentrenados requiere learning rates menores que entrenar desde cero (1e-5 a 5e-5 vs. 1e-3)
- Documentar la configuración completa antes de ejecutar permite comparar experimentos de forma rigurosa

---

## Criterios de evaluación — UD2

| Criterio | Indicador de logro |
|---|---|
| Selecciona arquitectura y función de pérdida coherentes | Justifica la elección en función del tipo de tarea y los datos |
| Prepara un entorno reproducible | Controla semillas, fija versiones de librerías, documenta el hardware |
| Configura los parámetros del optimizador | Elige lr, batch size y épocas con criterio técnico |
| Documenta la configuración | Produce un registro completo antes del entrenamiento |
| Adapta modelo preentrenado | Congela capas correctamente y sustituye la cabeza de clasificación |
