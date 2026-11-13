# UD2 · Configuración del modelo y del entorno de entrenamiento

**Módulo:** MP02 — Entrenamiento de Modelos  
**Ciclo:** CFS1 — Gestión de Datos e Inteligencia Artificial  
**Nivel:** Formación Superior  
**Duración estimada:** 12 horas lectivas

---

## 1. Introducción: la configuración como factor determinante en el rendimiento del modelo

El proceso de entrenamiento de una red neuronal no se reduce a definir una arquitectura y alimentarla con datos. La configuración del entorno y del modelo —las decisiones que se toman antes de que comience la primera época de entrenamiento— determina en gran medida si ese entrenamiento convergerá de manera estable, si el modelo generalizará correctamente a datos no vistos, y si el experimento podrá reproducirse días, semanas o meses después.

Dos modelos entrenados con los mismos datos y la misma arquitectura pueden producir resultados radicalmente distintos si difieren en su tasa de aprendizaje, en el optimizador empleado, en la presencia o ausencia de regularización, o simplemente en la versión de las bibliotecas instaladas. Esta variabilidad hace que la disciplina de la configuración sea tan importante como la selección de la arquitectura en sí misma.

La presente unidad aborda los conocimientos y habilidades necesarios para establecer entornos de desarrollo reproducibles, seleccionar y ajustar los hiperparámetros que controlan el entrenamiento, entender el comportamiento matemático de los principales optimizadores, aplicar técnicas de regularización para evitar el sobreajuste, y automatizar la búsqueda de hiperparámetros mediante herramientas modernas. Todo ello con un enfoque eminentemente práctico basado en PyTorch.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Crear y gestionar entornos virtuales de Python aislados con `venv`, `conda` y `poetry`, y documentarlos de forma reproducible.
- Construir imágenes Docker orientadas a flujos de trabajo de aprendizaje automático, incluyendo soporte para CUDA.
- Verificar la compatibilidad entre versiones de CUDA, cuDNN y PyTorch en un sistema con GPU.
- Distinguir entre hiperparámetros de arquitectura e hiperparámetros de entrenamiento, y razonar sobre el impacto de cada uno.
- Implementar y seleccionar el optimizador adecuado (SGD, Adam, AdamW, RMSprop, Adagrad) según las características del problema.
- Elegir la función de pérdida apropiada para tareas de clasificación, regresión y segmentación.
- Aplicar técnicas de regularización —L1, L2, dropout, batch normalization— e interpretar su efecto en la curva de aprendizaje.
- Inicializar los pesos de una red neuronal con los esquemas Xavier/Glorot y He, y justificar la elección.
- Ejecutar búsquedas de hiperparámetros sistemáticas con Optuna y compararlas con enfoques clásicos como grid search y random search.

---

## 3. Gestión de entornos de desarrollo

### 3.1 Entornos virtuales Python: venv y conda

Un entorno virtual es un directorio que contiene un intérprete de Python y un conjunto específico de paquetes, completamente aislado del sistema operativo y de otros proyectos. Sin entornos virtuales, dos proyectos que requieran versiones distintas de una misma biblioteca entran inevitablemente en conflicto.

**venv** es la herramienta incluida en la biblioteca estándar de Python desde la versión 3.3. Su uso es sencillo:

```bash
# Crear el entorno en la carpeta .venv dentro del proyecto
python -m venv .venv

# Activar en Linux/macOS
source .venv/bin/activate

# Activar en Windows
.venv\Scripts\activate

# Desactivar
deactivate
```

**conda** es un gestor de entornos y paquetes más potente, mantenido por Anaconda y ampliamente usado en ciencia de datos. A diferencia de `venv`, conda puede gestionar paquetes no Python (como librerías C, CUDA, etc.) y crea entornos completamente independientes del Python del sistema:

```bash
# Crear un entorno con Python 3.11
conda create -n mi_entorno python=3.11

# Activar
conda activate mi_entorno

# Listar entornos disponibles
conda env list

# Desactivar
conda deactivate
```

### 3.2 Gestión de dependencias: pip, conda y poetry

**pip** es el gestor de paquetes estándar de Python. Dentro de un entorno activado, instala paquetes desde PyPI:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install numpy pandas scikit-learn matplotlib
```

**poetry** es una herramienta moderna que unifica la gestión de dependencias y el empaquetado. Usa un fichero `pyproject.toml` como fuente única de verdad y resuelve dependencias de manera determinista:

```bash
# Inicializar un proyecto nuevo
poetry init

# Añadir dependencias
poetry add torch numpy pandas

# Instalar dependencias del proyecto
poetry install

# Generar un lockfile reproducible
poetry lock
```

### 3.3 Reproducibilidad: requirements.txt y environment.yml

Para garantizar que otro desarrollador (o un servidor de producción) pueda reproducir exactamente el mismo entorno, se documentan las dependencias en ficheros de texto.

**requirements.txt** (para entornos pip):

```bash
# Generar desde el entorno activo
pip freeze > requirements.txt

# Restaurar en otro sistema
pip install -r requirements.txt
```

El contenido típico de un `requirements.txt` para un proyecto de ML incluye versiones fijadas:

```
torch==2.2.1
torchvision==0.17.1
numpy==1.26.4
scikit-learn==1.4.1
optuna==3.6.1
matplotlib==3.8.3
```

**environment.yml** (para entornos conda): permite especificar tanto paquetes conda como paquetes pip dentro del mismo fichero:

```yaml
name: iad-entrenamiento
channels:
  - pytorch
  - nvidia
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - cudatoolkit=12.1
  - pip:
    - torch==2.2.1
    - torchvision==0.17.1
    - numpy==1.26.4
    - optuna==3.6.1
```

```bash
# Crear entorno desde el fichero
conda env create -f environment.yml

# Actualizar un entorno existente
conda env update -f environment.yml --prune
```

### 3.4 Docker para entornos reproducibles de ML

Docker lleva la reproducibilidad un paso más allá al empaquetar no solo las dependencias Python sino también el sistema operativo, las librerías del sistema y los drivers de CUDA en una imagen inmutable. Esto garantiza que el entrenamiento se ejecute de manera idéntica en un portátil, en un servidor en la nube y en un clúster de GPU.

Un `Dockerfile` típico para entrenamiento con PyTorch y CUDA:

```dockerfile
# Imagen base oficial de PyTorch con CUDA 12.1 y cuDNN 8
FROM pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime

# Metadatos
LABEL maintainer="iad-curso@ifc.es"
LABEL version="1.0"

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Directorio de trabajo dentro del contenedor
WORKDIR /workspace

# Copiar e instalar dependencias primero (capa cacheada)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Comando por defecto al arrancar el contenedor
CMD ["python", "train.py"]
```

Para construir y ejecutar con acceso a la GPU:

```bash
# Construir la imagen
docker build -t ml-entrenamiento:v1 .

# Ejecutar con GPU (requiere nvidia-container-toolkit)
docker run --gpus all --rm -v $(pwd)/data:/workspace/data ml-entrenamiento:v1
```

### 3.5 CUDA y cuDNN: instalación y verificación de compatibilidad

CUDA es la plataforma de computación paralela de NVIDIA. cuDNN es la biblioteca de primitivas de redes neuronales optimizadas para GPUs NVIDIA. La correcta alineación entre la versión del driver NVIDIA, CUDA, cuDNN y PyTorch es una fuente frecuente de problemas.

**Tabla de compatibilidad de versiones (selección)**:

| PyTorch | CUDA | cuDNN | Driver NVIDIA mínimo |
|---------|------|-------|----------------------|
| 2.2.x   | 12.1 | 8.9.x | 525.60               |
| 2.1.x   | 11.8 | 8.7.x | 450.80               |
| 2.0.x   | 11.7 | 8.5.x | 450.80               |
| 1.13.x  | 11.6 | 8.3.x | 418.39               |

Verificación en Python tras la instalación:

```python
import torch

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA disponible: {torch.cuda.is_available()}")
print(f"Número de GPUs: {torch.cuda.device_count()}")

if torch.cuda.is_available():
    print(f"GPU activa: {torch.cuda.get_device_name(0)}")
    print(f"Versión CUDA (compilación): {torch.version.cuda}")
    print(f"Memoria total GPU 0: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
```

---

## 4. Hiperparámetros: tipos y significado

Los hiperparámetros son los valores de configuración que se establecen antes del entrenamiento y que el algoritmo de aprendizaje no ajusta automáticamente. Se distinguen claramente de los parámetros del modelo (pesos y sesgos), que sí se actualizan durante el entrenamiento.

### 4.1 Hiperparámetros de arquitectura vs. hiperparámetros de entrenamiento

Los **hiperparámetros de arquitectura** definen la estructura de la red: cuántas capas tiene, cuántas neuronas contiene cada capa, qué función de activación se emplea, si hay capas de normalización, etc. Determinan la capacidad del modelo —su aptitud para representar funciones complejas— y se fijan antes de construir el grafo computacional.

Los **hiperparámetros de entrenamiento** controlan cómo se ajustan los parámetros: qué tan rápido aprende el modelo (tasa de aprendizaje), cuántos ejemplos se procesan por actualización (tamaño de lote), cuántas veces se recorre el conjunto de datos completo (épocas), y parámetros específicos del optimizador como el momentum.

### 4.2 Impacto de los hiperparámetros principales

**Tasa de aprendizaje (learning rate, lr)**: es el hiperparámetro más sensible. Un lr demasiado alto produce oscilaciones o divergencia; uno demasiado bajo produce convergencia lenta o atascamiento en mínimos locales subóptimos. Los schedulers (reducción de lr en meseta, cosine annealing) suelen mejorar los resultados respecto a un lr fijo.

**Tamaño de lote (batch size)**: lotes pequeños introducen más ruido en la estimación del gradiente, lo que puede actuar como regularizador pero ralentiza la convergencia. Lotes grandes producen gradientes más estables y permiten mayor paralelismo en GPU, pero pueden conducir a mínimos más pronunciados (peor generalización). El rango típico oscila entre 16 y 512 ejemplos.

**Épocas**: entrenar pocas épocas produce underfitting; demasiadas, overfitting. El early stopping —detener el entrenamiento cuando la pérdida de validación deja de mejorar durante N épocas— mitiga el sobreajuste sin necesidad de fijar las épocas a priori.

### 4.3 Tabla detallada de hiperparámetros comunes

| Hiperparámetro | Categoría | Rango típico | Impacto principal |
|---|---|---|---|
| Tasa de aprendizaje (lr) | Entrenamiento | 1e-5 – 1e-1 | Velocidad y estabilidad de convergencia |
| Batch size | Entrenamiento | 16 – 512 | Ruido del gradiente, uso de memoria GPU |
| Epochs | Entrenamiento | 10 – 300+ | Sobreajuste vs. subajuste |
| Momentum (SGD) | Entrenamiento | 0.85 – 0.99 | Aceleración en direcciones consistentes |
| Weight decay (L2) | Regularización | 1e-5 – 1e-2 | Magnitud de los pesos |
| Dropout rate | Regularización | 0.1 – 0.5 | Sobreajuste en capas fully-connected |
| Número de capas (profundidad) | Arquitectura | 2 – 100+ | Capacidad de representación |
| Neuronas por capa | Arquitectura | 64 – 4096 | Capacidad, coste computacional |
| Filtros en conv. (CNNs) | Arquitectura | 32 – 512 | Extracción de características |
| Tamaño de kernel (CNNs) | Arquitectura | 3×3, 5×5, 7×7 | Receptive field |
| Número de cabezas (Transformers) | Arquitectura | 4, 8, 12, 16 | Atención multi-perspectiva |
| Dimensión de embedding | Arquitectura | 64 – 1024 | Riqueza de la representación |
| Función de activación | Arquitectura | ReLU, GELU, SiLU | Linealidad, gradiente muerto |
| lr scheduler | Entrenamiento | StepLR, CosineAnnealing | Ajuste dinámico del lr |

---

## 5. Optimizadores para redes neuronales

Un optimizador implementa la regla de actualización de los parámetros del modelo. Dado el gradiente de la función de pérdida respecto a cada parámetro, el optimizador determina en qué dirección y en qué magnitud se actualizan los pesos.

### 5.1 Descenso de gradiente estocástico (SGD) con momentum

La actualización básica de SGD es:

```
θ_t = θ_{t-1} - lr · ∇L(θ_{t-1})
```

Con **momentum**, se acumula una media exponencialmente ponderada de gradientes pasados (velocidad `v`):

```
v_t = β · v_{t-1} + ∇L(θ_{t-1})
θ_t = θ_{t-1} - lr · v_t
```

Donde `β` es el coeficiente de momentum (habitualmente 0.9). El momentum ayuda a atravesar mesetas y atenúa las oscilaciones en dimensiones de alta curvatura. SGD con momentum sigue siendo el optimizador preferido para el entrenamiento de visión computacional (ResNets, ViTs) cuando se ajusta correctamente.

### 5.2 Adam (Adaptive Moment Estimation)

Propuesto por Kingma y Ba en 2014, Adam combina las ideas del momentum con la adaptación individual de la tasa de aprendizaje por parámetro. Mantiene dos momentos:

- `m_t` = media del gradiente (primer momento, similar al momentum)
- `v_t` = media del cuadrado del gradiente (segundo momento)

Con corrección de sesgo para las primeras iteraciones:

```
m_t = β₁ · m_{t-1} + (1 - β₁) · g_t
v_t = β₂ · v_{t-1} + (1 - β₂) · g_t²
m̂_t = m_t / (1 - β₁ᵗ)
v̂_t = v_t / (1 - β₂ᵗ)
θ_t = θ_{t-1} - lr · m̂_t / (√v̂_t + ε)
```

Los valores por defecto —`β₁=0.9`, `β₂=0.999`, `ε=1e-8`— funcionan bien en la mayoría de problemas. Adam converge rápidamente y es robusto a la elección del lr, lo que lo convierte en el punto de partida habitual para NLP y redes generativas.

### 5.3 AdamW

AdamW corrige un defecto de Adam: la implementación estándar de Adam con weight decay (L2) no desacopla correctamente la regularización del paso adaptativo. AdamW aplica el weight decay directamente sobre los parámetros en lugar de incluirlo en el gradiente:

```
θ_t = θ_{t-1} - lr · (m̂_t / (√v̂_t + ε) + λ · θ_{t-1})
```

Donde `λ` es el coeficiente de weight decay. AdamW es el optimizador preferido para el entrenamiento de transformers (BERT, GPT, ViT) y mejora sistemáticamente la generalización respecto a Adam en este tipo de arquitecturas.

### 5.4 RMSprop

RMSprop adapta el lr por parámetro usando la media del cuadrado del gradiente pero sin corrección de sesgo:

```
E[g²]_t = ρ · E[g²]_{t-1} + (1 - ρ) · g_t²
θ_t = θ_{t-1} - lr / (√E[g²]_t + ε) · g_t
```

Es especialmente efectivo para redes recurrentes (RNN, LSTM) y fue propuesto por Hinton en notas de curso no publicadas, lo que lo convierte en un caso inusual de difusión científica.

### 5.5 Adagrad

Adagrad acumula todos los cuadrados de gradientes pasados, lo que produce una reducción monótona y pronunciada del lr efectivo. Funciona bien en problemas con gradientes esparsos (NLP clásico con embeddings), pero se atasca en problemas densos al cabo de muchas iteraciones.

### 5.6 Código PyTorch: instanciación y uso de optimizadores

```python
import torch
import torch.nn as nn

# Modelo de ejemplo
model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Linear(256, 10)
)

# SGD con momentum y weight decay
optimizer_sgd = torch.optim.SGD(
    model.parameters(),
    lr=0.01,
    momentum=0.9,
    weight_decay=1e-4
)

# Adam
optimizer_adam = torch.optim.Adam(
    model.parameters(),
    lr=1e-3,
    betas=(0.9, 0.999),
    eps=1e-8
)

# AdamW (recomendado para transformers)
optimizer_adamw = torch.optim.AdamW(
    model.parameters(),
    lr=1e-4,
    weight_decay=0.01
)

# RMSprop
optimizer_rms = torch.optim.RMSprop(
    model.parameters(),
    lr=1e-3,
    alpha=0.99,
    momentum=0.9
)

# Scheduler: reduce lr cuando la métrica de validación se estanca
from torch.optim.lr_scheduler import ReduceLROnPlateau
scheduler = ReduceLROnPlateau(optimizer_adamw, mode='min', factor=0.5, patience=5)

# Bucle de entrenamiento simplificado
loss_fn = nn.CrossEntropyLoss()
for epoch in range(100):
    model.train()
    for X_batch, y_batch in train_loader:
        optimizer_adamw.zero_grad()
        logits = model(X_batch)
        loss = loss_fn(logits, y_batch)
        loss.backward()
        optimizer_adamw.step()
    
    val_loss = evaluar_validacion(model, val_loader, loss_fn)
    scheduler.step(val_loss)
```

### 5.7 Cuándo usar cada optimizador

| Optimizador | Cuándo preferirlo |
|---|---|
| SGD + momentum | Visión computacional con esquemas de lr cíclicos; produce mejores mínimos en redes profundas si se ajusta bien |
| Adam | Punto de partida rápido; NLP, GAN, reinforcement learning |
| AdamW | Transformers, fine-tuning de modelos preentrenados; siempre preferible a Adam cuando hay weight decay |
| RMSprop | RNN, LSTM; optimización de funciones no estacionarias |
| Adagrad | Embeddings con gradientes esparsos; problemas de NLP clásico |

---

## 6. Funciones de pérdida

La función de pérdida cuantifica la discrepancia entre las predicciones del modelo y los valores reales. Su elección condiciona qué tipo de errores se penaliza más y, en última instancia, qué comportamiento aprende el modelo.

### 6.1 Clasificación

**Binary Cross-Entropy (BCE)**: para clasificación binaria o multilabel. Para un conjunto de N ejemplos:

```
BCE = -1/N · Σ [yᵢ · log(p̂ᵢ) + (1 - yᵢ) · log(1 - p̂ᵢ)]
```

```python
# PyTorch: BCEWithLogitsLoss combina sigmoid + BCE de forma numéricamente estable
criterion = nn.BCEWithLogitsLoss()
loss = criterion(logits, targets.float())
```

**Cross-Entropy multiclase**: para clasificación con C clases mutuamente excluyentes:

```
CE = -1/N · Σᵢ Σⱼ yᵢⱼ · log(p̂ᵢⱼ)
```

```python
criterion = nn.CrossEntropyLoss()  # Acepta logits directamente (incluye softmax)
loss = criterion(logits, labels)   # labels: tensor de enteros [N]
```

**Focal Loss**: diseñada para problemas con fuerte desequilibrio de clases (detección de objetos, diagnóstico médico). Reduce el peso de los ejemplos fáciles (bien clasificados) y focaliza el entrenamiento en los casos difíciles:

```
FL(pₜ) = -αₜ · (1 - pₜ)^γ · log(pₜ)
```

Donde `γ` (focusing parameter, típicamente 2) reduce la contribución de ejemplos bien clasificados y `α` pondera las clases. La implementación está disponible en `torchvision.ops.sigmoid_focal_loss`.

### 6.2 Regresión

**Mean Squared Error (MSE)**: penaliza fuertemente los errores grandes al elevarlos al cuadrado. Sensible a outliers.

```python
criterion = nn.MSELoss()
```

**Mean Absolute Error (MAE / L1Loss)**: penaliza todos los errores proporcionalmente. Más robusta a outliers, pero el gradiente es discontinuo en cero.

```python
criterion = nn.L1Loss()
```

**Huber Loss (SmoothL1Loss)**: combina MAE y MSE: se comporta como MSE para errores pequeños y como MAE para errores grandes, eliminando la discontinuidad del gradiente:

```python
criterion = nn.SmoothL1Loss(beta=1.0)
```

### 6.3 Selección de función de pérdida según tarea

| Tarea | Función de pérdida recomendada | Alternativa |
|---|---|---|
| Clasificación binaria | BCEWithLogitsLoss | Focal Loss (si hay desbalanceo) |
| Clasificación multiclase | CrossEntropyLoss | Label Smoothing CE |
| Regresión estándar | MSELoss | HuberLoss |
| Regresión robusta (outliers) | HuberLoss | MAE (L1Loss) |
| Segmentación semántica | CrossEntropyLoss | Dice Loss, Focal Loss |
| Detección de objetos | Focal Loss + SmoothL1 | — |
| Generación (VAE) | BCE + KL-divergence | — |

---

## 7. Técnicas de regularización

El sobreajuste ocurre cuando el modelo aprende los datos de entrenamiento con demasiado detalle, incluyendo el ruido, y pierde capacidad de generalización. Las técnicas de regularización introducen restricciones o perturbaciones que desincentivan la especialización excesiva.

### 7.1 Regularización L1 y L2

**L1 (Lasso)** añade a la función de pérdida la suma de los valores absolutos de los pesos. Promueve soluciones dispersas (muchos pesos a cero), lo que equivale a una selección implícita de características:

```
L_total = L_datos + λ · Σ|wᵢ|
```

**L2 (Ridge / Weight Decay)** añade la suma de los cuadrados de los pesos. Penaliza los pesos grandes y distribuye la solución de manera más uniforme sin llevarlos exactamente a cero:

```
L_total = L_datos + λ · Σwᵢ²
```

En PyTorch, L2 se implementa mediante el parámetro `weight_decay` de los optimizadores. L1 requiere cálculo explícito:

```python
# L2 integrado en el optimizador
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)

# L1 manual
l1_lambda = 1e-5
l1_norm = sum(p.abs().sum() for p in model.parameters())
loss = loss_fn(outputs, targets) + l1_lambda * l1_norm
```

### 7.2 Dropout

El dropout (Srivastava et al., 2014) desactiva aleatoriamente una fracción `p` de las neuronas durante cada paso de entrenamiento. Esto impide que las neuronas desarrollen dependencias mutuas excesivas y obliga a la red a aprender representaciones más robustas.

Durante la inferencia, el dropout está desactivado y los pesos se escalan por `(1-p)` (o equivalentemente, durante el entrenamiento los pesos activos se escalan por `1/(1-p)`, que es el comportamiento por defecto de PyTorch).

```python
import torch.nn as nn

class RedConDropout(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, p_dropout=0.3):
        super().__init__()
        self.red = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=p_dropout),        # Dropout tras activación
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=p_dropout),
            nn.Linear(hidden_dim, output_dim)
        )
    
    def forward(self, x):
        return self.red(x)

modelo = RedConDropout(784, 512, 10, p_dropout=0.4)

# Importante: cambiar modo según fase
modelo.train()   # Dropout activo
modelo.eval()    # Dropout desactivado
```

Las tasas de dropout más altas (0.4–0.5) se aplican típicamente en las capas fully-connected; en capas convolucionales o en transformers se suelen usar valores menores (0.1–0.2).

### 7.3 Batch Normalization y Layer Normalization

**Batch Normalization** (Ioffe & Szegedy, 2015) normaliza las activaciones de cada capa a lo largo del mini-batch, manteniendo media cero y varianza unitaria, y luego aplica una transformación aprendida (γ, β):

```
BN(x) = γ · (x - μ_batch) / √(σ²_batch + ε) + β
```

Sus beneficios son notables: permite tasas de aprendizaje más altas, actúa como regularizador (reduciendo la necesidad de dropout en CNNs), y estabiliza el entrenamiento profundo. Sin embargo, su dependencia del tamaño del lote la hace problemática para lotes pequeños o para inferencia en streaming.

**Layer Normalization** normaliza a lo largo de las características de cada ejemplo individual, en lugar del batch. Es independiente del tamaño del lote y es el esquema estándar en transformers.

```python
# Batch Normalization (CNNs)
capa_conv_bn = nn.Sequential(
    nn.Conv2d(32, 64, kernel_size=3, padding=1),
    nn.BatchNorm2d(64),
    nn.ReLU()
)

# Layer Normalization (Transformers, RNNs)
capa_ln = nn.Sequential(
    nn.Linear(512, 512),
    nn.LayerNorm(512),
    nn.GELU()
)
```

### 7.4 Data Augmentation como regularizador

El data augmentation aplica transformaciones aleatorias a los ejemplos de entrenamiento (rotaciones, recortes, cambios de brillo, ruido gaussiano) para aumentar artificialmente la diversidad del conjunto de datos. Equivale funcionalmente a entrenar con más datos, lo que mejora la generalización sin coste de recolección.

```python
from torchvision import transforms

augmentacion_entrenamiento = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomCrop(32, padding=4),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.RandomRotation(degrees=10),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Para validación: solo normalización, sin augmentation
augmentacion_validacion = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
```

---

## 8. Inicialización de pesos

La inicialización de los pesos afecta directamente a la velocidad y estabilidad de la convergencia. Una mala inicialización puede producir vanishing gradients (gradientes que desaparecen en capas tempranas) o exploding gradients (gradientes que crecen sin control).

### 8.1 Xavier / Glorot Initialization

Diseñada para redes con activaciones simétricas alrededor del cero (tanh, sigmoid). Mantiene la varianza de las activaciones constante a través de las capas:

```
W ~ U[-√(6/(nᵢₙ + nₒᵤₜ)), √(6/(nᵢₙ + nₒᵤₜ))]
```

Donde `nᵢₙ` y `nₒᵤₜ` son el número de neuronas de entrada y salida de la capa.

### 8.2 He Initialization (Kaiming)

Diseñada para redes con activaciones ReLU, que cortan la mitad de las activaciones a cero. Dobla la varianza respecto a Xavier para compensar:

```
W ~ N(0, √(2 / nᵢₙ))
```

```python
import torch.nn as nn

def inicializar_pesos(modulo):
    if isinstance(modulo, nn.Linear):
        # He initialization para capas con ReLU
        nn.init.kaiming_normal_(modulo.weight, mode='fan_in', nonlinearity='relu')
        if modulo.bias is not None:
            nn.init.zeros_(modulo.bias)
    elif isinstance(modulo, nn.Conv2d):
        # He initialization para convoluciones con ReLU
        nn.init.kaiming_normal_(modulo.weight, mode='fan_out', nonlinearity='relu')
        if modulo.bias is not None:
            nn.init.zeros_(modulo.bias)
    elif isinstance(modulo, nn.BatchNorm2d):
        nn.init.ones_(modulo.weight)   # γ = 1
        nn.init.zeros_(modulo.bias)    # β = 0

model = MiRedNeuronal()
model.apply(inicializar_pesos)
```

**Regla práctica**: usar He initialization con ReLU/Leaky ReLU/GELU; usar Xavier con tanh/sigmoid. Los transformers con normalización de capa son menos sensibles a la inicialización, aunque siguen siendo habituales las inicializaciones cercanas a cero con escalado por la profundidad.

---

## 9. Búsqueda de hiperparámetros

La optimización de hiperparámetros (HPO) es el proceso de encontrar la combinación de valores de hiperparámetros que produce el mejor modelo según una métrica de validación. Este proceso es costoso computacionalmente y se ha beneficiado enormemente de herramientas modernas.

### 9.1 Grid Search

Evalúa exhaustivamente todas las combinaciones posibles de un conjunto discreto de valores. Garantiza encontrar el óptimo dentro del espacio definido, pero su coste escala exponencialmente con el número de hiperparámetros y de valores por hiperparámetro.

```python
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPClassifier

param_grid = {
    'hidden_layer_sizes': [(64,), (128,), (64, 64)],
    'learning_rate_init': [1e-3, 1e-4],
    'alpha': [1e-4, 1e-3]   # weight decay
}

# 3 × 2 × 2 = 12 combinaciones × k folds
gs = GridSearchCV(MLPClassifier(max_iter=100), param_grid, cv=3, n_jobs=-1)
gs.fit(X_train, y_train)
print(f"Mejores hiperparámetros: {gs.best_params_}")
```

### 9.2 Random Search

En lugar de evaluar todas las combinaciones, muestrea aleatoriamente del espacio de búsqueda. Bergstra y Bengio (2012) demostraron que, para espacios de hiperparámetros donde no todos los hiperparámetros son igualmente importantes, random search es más eficiente que grid search con el mismo presupuesto computacional.

### 9.3 Optuna: búsqueda bayesiana

Optuna implementa una búsqueda bayesiana de hiperparámetros basada en el estimador de densidad en árbol (TPE). Aprende de cada evaluación para proponer configuraciones más prometedoras, convergiendo hacia buenos hiperparámetros con muchas menos evaluaciones que grid o random search.

```python
import optuna
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

def objetivo(trial):
    # Optuna sugiere valores dentro de los rangos especificados
    lr = trial.suggest_float("lr", 1e-5, 1e-1, log=True)
    n_capas = trial.suggest_int("n_capas", 1, 4)
    n_neuronas = trial.suggest_categorical("n_neuronas", [64, 128, 256, 512])
    dropout = trial.suggest_float("dropout", 0.1, 0.5)
    optimizador_nombre = trial.suggest_categorical("optimizador", ["Adam", "AdamW", "SGD"])
    
    # Construir modelo con los hiperparámetros sugeridos
    capas = []
    dim_entrada = 784
    for _ in range(n_capas):
        capas += [nn.Linear(dim_entrada, n_neuronas), nn.ReLU(), nn.Dropout(dropout)]
        dim_entrada = n_neuronas
    capas.append(nn.Linear(dim_entrada, 10))
    model = nn.Sequential(*capas)
    
    # Seleccionar optimizador
    if optimizador_nombre == "Adam":
        opt = torch.optim.Adam(model.parameters(), lr=lr)
    elif optimizador_nombre == "AdamW":
        opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    else:
        opt = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9)
    
    loss_fn = nn.CrossEntropyLoss()
    
    # Entrenamiento rápido para evaluación
    model.train()
    for epoch in range(10):
        for X_batch, y_batch in train_loader:
            opt.zero_grad()
            loss = loss_fn(model(X_batch), y_batch)
            loss.backward()
            opt.step()
    
    # Evaluar en validación
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for X_val, y_val in val_loader:
            val_loss += loss_fn(model(X_val), y_val).item()
    
    return val_loss / len(val_loader)

# Crear y ejecutar el estudio
estudio = optuna.create_study(direction="minimize")
estudio.optimize(objetivo, n_trials=50, timeout=3600)

print(f"Mejor valor de pérdida: {estudio.best_value:.4f}")
print(f"Mejores hiperparámetros: {estudio.best_params}")

# Visualizar la importancia de los hiperparámetros
optuna.visualization.plot_param_importances(estudio).show()
```

### 9.4 Ray Tune

Ray Tune es una biblioteca de HPO distribuida que permite ejecutar búsquedas sobre múltiples GPUs y máquinas de forma transparente. Soporta múltiples algoritmos de búsqueda (HyperOpt, Bayesian Optimization, Population-Based Training) y se integra con PyTorch Lightning y Hugging Face.

```python
from ray import tune
from ray.tune.schedulers import ASHAScheduler

# ASHA (Asynchronous Successive Halving) detiene los trials poco prometedores pronto
scheduler = ASHAScheduler(metric="val_loss", mode="min", max_t=100, grace_period=10)

resultado = tune.run(
    funcion_entrenamiento,
    config={
        "lr": tune.loguniform(1e-5, 1e-1),
        "batch_size": tune.choice([32, 64, 128, 256]),
        "n_neuronas": tune.choice([128, 256, 512]),
    },
    num_samples=100,
    scheduler=scheduler,
    resources_per_trial={"gpu": 1}
)
```

### 9.5 Comparativa de métodos de búsqueda

| Método | Eficiencia | Paralelizable | Requiere configuración | Caso de uso |
|---|---|---|---|---|
| Grid Search | Baja | Sí | Mínima | Pocos hiperparámetros, espacio pequeño |
| Random Search | Media | Sí | Mínima | Exploración inicial rápida |
| Optuna (TPE) | Alta | Sí (SQLite/Redis) | Media | Proyectos con presupuesto moderado |
| Ray Tune | Muy alta | Nativa (multi-GPU) | Media-alta | Entrenamientos distribuidos |
| Population-Based | Muy alta | Sí | Alta | Modelos grandes con muchos recursos |

---

## 10. Actividades prácticas propuestas

### Actividad 1: Configuración de entorno reproducible (2 horas)

El estudiante creará un entorno virtual con `conda`, instalará PyTorch con soporte CUDA, verificará la disponibilidad de la GPU mediante el script de comprobación proporcionado, documentará el entorno con `environment.yml`, y construirá una imagen Docker funcional a partir del `Dockerfile` de la sección 3.4. El objetivo es que un compañero pueda reproducir el entorno exacto ejecutando únicamente `conda env create -f environment.yml` o `docker build`.

### Actividad 2: Análisis del efecto de los hiperparámetros (3 horas)

Partiendo de un dataset de referencia (MNIST o CIFAR-10), el estudiante entrenará la misma red neuronal variando de forma sistemática la tasa de aprendizaje (cinco valores en escala logarítmica), el tamaño de lote (cuatro valores) y el optimizador (SGD, Adam, AdamW). Registrará las curvas de pérdida de entrenamiento y validación, y redactará un informe de dos páginas analizando las diferencias observadas, justificando los resultados desde los fundamentos teóricos de cada optimizador.

### Actividad 3: Implementación de regularización y comparación (3 horas)

El estudiante implementará cuatro variantes del mismo modelo sobre CIFAR-10: (a) sin regularización, (b) con L2 weight decay, (c) con dropout, (d) con batch normalization. Comparará las curvas de aprendizaje, la diferencia entre pérdida de entrenamiento y de validación, y la precisión final en el conjunto de test. Concluirá qué técnica o combinación de técnicas produce el mejor balance sesgo-varianza en este problema concreto.

### Actividad 4: Búsqueda de hiperparámetros con Optuna (4 horas)

El estudiante implementará un estudio de Optuna para optimizar los hiperparámetros de una red convolucional sobre CIFAR-10, incluyendo el número de filtros, la tasa de aprendizaje, el dropout, el optimizador y el weight decay. Ejecutará el estudio con al menos 30 trials, visualizará la importancia de los hiperparámetros con `plot_param_importances`, entrenará el modelo final con la mejor configuración y comparará su rendimiento con un modelo de baseline con hiperparámetros por defecto.

---

## 11. Referencias

1. **Goodfellow, I., Bengio, Y., & Courville, A. (2016).** *Deep Learning*. MIT Press. Disponible en: [https://www.deeplearningbook.org](https://www.deeplearningbook.org)

2. **PyTorch Team. (2024).** *PyTorch Documentation — torch.optim*. PyTorch Foundation. Disponible en: [https://pytorch.org/docs/stable/optim.html](https://pytorch.org/docs/stable/optim.html)

3. **Kingma, D. P., & Ba, J. (2014).** *Adam: A Method for Stochastic Optimization*. arXiv:1412.6980. Disponible en: [https://arxiv.org/abs/1412.6980](https://arxiv.org/abs/1412.6980)

4. **Srivastava, N., Hinton, G., Krizhevsky, A., Sutskever, I., & Salakhutdinov, R. (2014).** *Dropout: A Simple Way to Prevent Neural Networks from Overfitting*. *Journal of Machine Learning Research*, 15(1), 1929–1958. Disponible en: [https://jmlr.org/papers/v15/srivastava14a.html](https://jmlr.org/papers/v15/srivastava14a.html)

5. **Ioffe, S., & Szegedy, C. (2015).** *Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift*. arXiv:1502.03167. Disponible en: [https://arxiv.org/abs/1502.03167](https://arxiv.org/abs/1502.03167)

6. **He, K., Zhang, X., Ren, S., & Sun, J. (2015).** *Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification*. arXiv:1502.01852. Disponible en: [https://arxiv.org/abs/1502.01852](https://arxiv.org/abs/1502.01852)

7. **Loshchilov, I., & Hutter, F. (2017).** *Decoupled Weight Decay Regularization (AdamW)*. arXiv:1711.05101. Disponible en: [https://arxiv.org/abs/1711.05101](https://arxiv.org/abs/1711.05101)

8. **Akiba, T., Sano, S., Yanase, T., Ohta, T., & Koyama, M. (2019).** *Optuna: A Next-generation Hyperparameter Optimization Framework*. arXiv:1907.10902. Disponible en: [https://arxiv.org/abs/1907.10902](https://arxiv.org/abs/1907.10902)

9. **Bergstra, J., & Bengio, Y. (2012).** *Random Search for Hyper-Parameter Optimization*. *Journal of Machine Learning Research*, 13, 281–305. Disponible en: [https://jmlr.org/papers/v13/bergstra12a.html](https://jmlr.org/papers/v13/bergstra12a.html)

10. **NVIDIA Corporation. (2024).** *CUDA Toolkit Documentation*. Disponible en: [https://docs.nvidia.com/cuda/](https://docs.nvidia.com/cuda/)

---

*Unidad didáctica elaborada para el Ciclo de Formación Superior en Gestión de Datos e Inteligencia Artificial — IFC. Actualización: junio 2026.*
