---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD2 · Despliegue de modelos con frameworks especializados | MP03'
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

# UD2 · Despliegue de modelos con frameworks especializados

**MP03 · Desarrollo de componentes para sistemas de ML**
CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de aprendizaje

Al finalizar esta unidad el alumno sera capaz de:

- Seleccionar la arquitectura de modelo adecuada segun el tipo de dato y el problema
- Desplegar modelos para datos tabulares, series temporales, imagen, video, audio y texto
- Realizar fine-tuning de modelos preentrenados con librerias especializadas
- Programar con control de errores (`try/except`), logging y depuracion sistematica
- Construir componentes reutilizables siguiendo principios de modularidad
- Acceder y manipular datos estructurados y no estructurados desde el codigo
- Gestionar entornos virtuales, paquetes y control de versiones con Git para proyectos de ML

---

## Mapa de la unidad

```
UD2 · Despliegue de modelos con frameworks
│
├── 1. Seleccion de arquitectura por tipo de dato
│   ├── Tabular y series temporales
│   ├── Imagen y video
│   └── Audio y texto
│
├── 2. Fine-tuning de modelos de texto
│   └── HuggingFace Transformers
│
├── 3. Buenas practicas de programacion
│   ├── Control de errores Try-Except
│   ├── Logging y depuracion
│   └── Componentes reutilizables
│
├── 4. Acceso a datos externos
│
└── 5. Gestion de dependencias y versiones
    └── Entornos virtuales, Git, ramas
```

---

## Seleccion de arquitectura: tabla de referencia completa

| Tipo de dato | Problema | Arquitectura recomendada | Framework principal |
|---|---|---|---|
| Tabular | Clasificacion / Regresion | Gradient Boosting, MLP | XGBoost, LightGBM, Sklearn |
| Series temporales | Prediccion | LSTM, TCN, TFT, Prophet | PyTorch, Darts, NeuralProphet |
| Imagen | Clasificacion | ResNet, EfficientNet, ViT | PyTorch, TensorFlow |
| Imagen | Deteccion | YOLOv8, Faster R-CNN | Ultralytics, Detectron2 |
| Video | Reconocimiento de accion | 3D-CNN, VideoSwin | PyTorch |
| Audio | Clasificacion | CNN sobre espectrograma, Wav2Vec2 | torchaudio, HuggingFace |
| Texto | Clasificacion / NER | BERT, RoBERTa, DistilBERT | HuggingFace Transformers |
| Texto | Generacion | GPT-2, LLaMA, Mistral | HuggingFace, llama.cpp |

> La seleccion de arquitectura es una decision de diseno: debe justificarse en funcion de los datos, el hardware disponible y las restricciones de latencia.

---

## Modelo para datos tabulares: pipeline completo

```python
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
import joblib

# Definir transformaciones por tipo de columna
numericas = ["edad", "salario", "antiguedad"]
categoricas = ["departamento", "ciudad"]

preprocesador = ColumnTransformer(transformers=[
    ("num", StandardScaler(), numericas),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categoricas)
])

# Pipeline completo: preprocesado + modelo
pipeline = Pipeline(steps=[
    ("preprocesado", preprocesador),
    ("modelo", GradientBoostingClassifier(
        n_estimators=200, learning_rate=0.05,
        max_depth=4, random_state=42
    ))
])

# Evaluacion con validacion cruzada
scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring="f1_macro")
print(f"F1 macro CV: {scores.mean():.3f} +/- {scores.std():.3f}")

# Guardar el pipeline completo (preprocesado + modelo)
joblib.dump(pipeline, "artifacts/modelo_tabular_v1.pkl")
```

---

## Modelo para series temporales con LSTM

```python
import torch
import torch.nn as nn

class ModeloLSTM(nn.Module):
    def __init__(self, n_features: int, hidden_dim: int, n_layers: int,
                 n_salidas: int, dropout: float = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=n_features,
            hidden_size=hidden_dim,
            num_layers=n_layers,
            dropout=dropout,
            batch_first=True
        )
        self.cabeza = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, n_salidas)
        )

    def forward(self, x):
        # x: (batch, secuencia, features)
        salida_lstm, (h_n, _) = self.lstm(x)
        # Usar solo el ultimo estado oculto
        return self.cabeza(h_n[-1])

modelo = ModeloLSTM(n_features=5, hidden_dim=128, n_layers=2, n_salidas=1)
print(f"Parametros: {sum(p.numel() for p in modelo.parameters()):,}")
```

---

## Modelo para imagen: CNN con transfer learning

```python
import torch
import torchvision.models as models
import torch.nn as nn

def crear_modelo_imagen(n_clases: int, congelar_base: bool = True):
    """
    ResNet-50 preentrenada en ImageNet adaptada para clasificacion personalizada.
    """
    modelo = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)

    # Congelar capas base para fine-tuning eficiente
    if congelar_base:
        for param in modelo.parameters():
            param.requires_grad = False

    # Reemplazar la cabeza de clasificacion
    n_features = modelo.fc.in_features
    modelo.fc = nn.Sequential(
        nn.Dropout(0.4),
        nn.Linear(n_features, 256),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(256, n_clases)
    )

    return modelo

modelo_img = crear_modelo_imagen(n_clases=5)
# Solo los parametros de la cabeza se actualizan inicialmente
params_entrenables = sum(p.numel() for p in modelo_img.parameters() if p.requires_grad)
print(f"Parametros entrenables: {params_entrenables:,}")
```

---

## Fine-tuning de modelos de texto con HuggingFace

```python
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer
)
from datasets import Dataset
import evaluate

# Cargar tokenizador y modelo base
MODEL_ID = "dccuchile/bert-base-spanish-wwm-cased"
tokenizador = AutoTokenizer.from_pretrained(MODEL_ID)
modelo = AutoModelForSequenceClassification.from_pretrained(
    MODEL_ID, num_labels=3
)

# Tokenizar los textos
def tokenizar(ejemplos):
    return tokenizador(
        ejemplos["texto"], truncation=True,
        max_length=256, padding="max_length"
    )

dataset_train = Dataset.from_dict({"texto": textos_train, "label": etiquetas_train})
dataset_val   = Dataset.from_dict({"texto": textos_val,   "label": etiquetas_val})
dataset_train = dataset_train.map(tokenizar, batched=True)
dataset_val   = dataset_val.map(tokenizar, batched=True)

# Metrica de evaluacion
metrica = evaluate.load("f1")
def calcular_metricas(eval_pred):
    logits, labels = eval_pred
    preds = logits.argmax(axis=-1)
    return metrica.compute(predictions=preds, references=labels, average="macro")
```

---

## Configuracion del entrenamiento con Trainer API

```python
args = TrainingArguments(
    output_dir="./resultados/bert-clasificacion",
    num_train_epochs=4,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    learning_rate=2e-5,
    weight_decay=0.01,
    warmup_ratio=0.1,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    logging_dir="./logs",
    report_to="mlflow",
    seed=42
)

entrenador = Trainer(
    model=modelo,
    args=args,
    train_dataset=dataset_train,
    eval_dataset=dataset_val,
    compute_metrics=calcular_metricas,
)

entrenador.train()
entrenador.save_model("artifacts/bert-clasificacion-v1")
tokenizador.save_pretrained("artifacts/bert-clasificacion-v1")
```

---

## Control de errores: patron Try-Except en ML

```python
import logging
import traceback

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def predecir_seguro(modelo, entrada: dict) -> dict:
    """
    Ejecuta inferencia con manejo exhaustivo de errores.
    """
    try:
        entrada_validada = validar_entrada(entrada)
        prediccion = modelo.predict(entrada_validada)
        logger.info(f"Prediccion exitosa: clase={prediccion['clase']}")
        return prediccion

    except ValueError as e:
        logger.error(f"Entrada invalida: {e}")
        return {"error": "entrada_invalida", "detalle": str(e)}

    except RuntimeError as e:
        logger.error(f"Error de inferencia: {e}\n{traceback.format_exc()}")
        return {"error": "error_inferencia", "detalle": str(e)}

    except Exception as e:
        logger.critical(f"Error inesperado: {e}\n{traceback.format_exc()}")
        raise
```

---

## Componentes reutilizables: diseno modular

```python
from abc import ABC, abstractmethod
from typing import Any
import numpy as np

class Preprocesador(ABC):
    """Interfaz base para todos los preprocesadores del sistema."""

    @abstractmethod
    def fit(self, X: np.ndarray) -> "Preprocesador":
        ...

    @abstractmethod
    def transform(self, X: np.ndarray) -> np.ndarray:
        ...

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)


class NormalizadorRobust(Preprocesador):
    """Normalizacion robusta a outliers basada en mediana e IQR."""

    def fit(self, X: np.ndarray) -> "NormalizadorRobust":
        self.mediana_ = np.median(X, axis=0)
        Q1 = np.percentile(X, 25, axis=0)
        Q3 = np.percentile(X, 75, axis=0)
        self.iqr_ = np.where(Q3 - Q1 == 0, 1.0, Q3 - Q1)
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        return (X - self.mediana_) / self.iqr_
```

---

## Gestion de dependencias: entornos por proyecto

```bash
# Crear entorno virtual aislado por proyecto
python -m venv .venv-proyecto-ml
source .venv-proyecto-ml/bin/activate   # Linux/Mac
# .venv-proyecto-ml\Scripts\activate   # Windows

# Instalar y fijar dependencias
pip install torch==2.2.0 transformers==4.40.0 scikit-learn==1.4.2
pip freeze > requirements.txt

# Verificar reproducibilidad en otra maquina
pip install -r requirements.txt
python -c "import torch; print(torch.__version__)"

# Registrar el entorno en el repositorio
git add requirements.txt
git commit -m "chore: fijar dependencias del entorno v1.0"
```

**Por que no usar `pip install` sin versiones:**
- Las actualizaciones de librerias pueden romper el codigo silenciosamente
- Equipos distintos pueden tener versiones distintas sin saberlo
- La reproducibilidad del experimento depende de las versiones exactas

---

## Control de versiones: flujo de ramas para ML

```bash
# Estructura de ramas para un proyecto de ML
main          ← codigo en produccion, siempre funcional
  └── develop ← integracion de features
        ├── feature/ingesta-audio     ← nueva funcionalidad
        ├── feature/modelo-tabular    ← experimento de modelo
        ├── fix/normalizacion-nulos   ← correccion de bug
        └── experiment/lstm-variante  ← exploracion sin garantias

# Flujo de trabajo
git checkout -b feature/ingesta-audio
# ... desarrollo ...
git add src/ingesta_audio.py tests/test_ingesta_audio.py
git commit -m "feat: anadir ingesta de audio con librosa y MFCC"
git push origin feature/ingesta-audio
# Abrir Pull Request hacia develop → revision de codigo → merge
```

> Los experimentos fallidos deben eliminarse o archivarse. El codigo en `main` debe ser siempre ejecutable y producir resultados consistentes.

---

## Ejecucion del plan de pruebas

```python
import pytest
import numpy as np

# tests/test_modelo_tabular.py
class TestPipelineTabular:

    def test_output_shape(self, pipeline, X_test):
        """El modelo debe devolver una prediccion por muestra."""
        predicciones = pipeline.predict(X_test)
        assert predicciones.shape == (len(X_test),)

    def test_predicciones_validas(self, pipeline, X_test, clases_validas):
        """Todas las predicciones deben pertenecer al conjunto de clases."""
        predicciones = pipeline.predict(X_test)
        assert set(predicciones).issubset(set(clases_validas))

    def test_probabilidades_suman_uno(self, pipeline, X_test):
        """Las probabilidades por clase deben sumar 1 por muestra."""
        probas = pipeline.predict_proba(X_test)
        np.testing.assert_allclose(probas.sum(axis=1), 1.0, atol=1e-6)

    def test_reproducibilidad(self, pipeline, X_test):
        """Misma entrada debe producir misma salida."""
        pred1 = pipeline.predict(X_test[:10])
        pred2 = pipeline.predict(X_test[:10])
        np.testing.assert_array_equal(pred1, pred2)
```

---

## Actividad practica — UD2

### Despliegue de modelo multimodal con componentes reutilizables

**Escenario:** desarrollar un clasificador de averias industriales que combina datos tabulares (sensores) y datos de imagen (camaras de inspeccion) con las siguientes restricciones:

- Los sensores producen 10 variables numericas cada minuto
- Las camaras producen una imagen de 224x224 pixeles por minuto
- La prediccion debe realizarse en menos de 200 ms
- El codigo debe ser reutilizable para otros tipos de maquinaria

**Tareas:**
1. Disenar e implementar la clase base `Preprocesador` y dos subclases (tabular e imagen)
2. Implementar el modelo con transfer learning sobre ResNet-18 para la rama de imagen
3. Anadir un MLP para la rama tabular y combinar ambas ramas (arquitectura fusion)
4. Aplicar control de errores completo (`try/except`, logging) en la funcion de inferencia
5. Escribir el suite de pruebas con `pytest` (shape, rango, reproducibilidad)
6. Gestionar dependencias con `requirements.txt` y flujo de ramas Git

---

## Puntos clave — UD2

- La seleccion de arquitectura debe fundamentarse en el tipo de dato y los recursos disponibles, no en la novedad de la tecnica
- El transfer learning reduce drasticamente el tiempo de entrenamiento y el volumen de datos necesario: usar siempre que existan modelos preentrenados relevantes
- El control de errores con `try/except` y logging es obligatorio en codigo de produccion: los errores silenciosos son los mas peligrosos en ML
- La modularidad mediante clases abstractas permite reutilizar componentes entre proyectos y facilita las pruebas unitarias
- Los entornos virtuales aislados por proyecto evitan conflictos de dependencias que pueden invalidar experimentos completos
- El flujo de ramas Git (`feature`, `develop`, `main`) separa el codigo experimental del codigo estable
- Las pruebas unitarias del modelo deben cubrir shape, rango de salidas y reproducibilidad como minimo

---

## Criterios de evaluacion — UD2

- Despliega modelos adecuados segun el tipo de dato justificando la seleccion de arquitectura
- Implementa fine-tuning de modelos preentrenados con HuggingFace u otras librerias
- Programa con control de errores (`try/except`) y logging en todos los puntos criticos del pipeline
- Construye componentes reutilizables con interfaces bien definidas (clases abstractas, tipado)
- Gestiona dependencias con entornos virtuales y `requirements.txt` con versiones fijadas
- Aplica un flujo de control de versiones con ramas Git y mensajes de commit descriptivos

---

<!-- _class: lead -->

[← Volver a MP03](../)


---

<!-- nav-slide -->

## Navegación

[← UD1 · Pipelines de datos para ML](../UD1_Pipelines-datos-ML/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD3 · Integración de modelos en apl… →](../UD3_Integracion-modelos-aplicaciones/)
