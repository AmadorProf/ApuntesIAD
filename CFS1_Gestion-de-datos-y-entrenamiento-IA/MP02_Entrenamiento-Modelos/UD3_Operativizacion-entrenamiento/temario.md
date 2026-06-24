# UD3 · Operativización del entrenamiento

**Módulo:** MP02 — Entrenamiento de Modelos  
**Ciclo:** CFS1 — Gestión de Datos e Inteligencia Artificial  
**Fecha de elaboración:** Junio 2026

---

## 1. Introducción

Configurar un modelo de aprendizaje automático —elegir la arquitectura, definir la función de pérdida, seleccionar el optimizador— es solo la primera mitad del trabajo. La segunda mitad, y en la práctica la más costosa en tiempo y recursos, es la operativización del entrenamiento: convertir esa configuración en un proceso que corra de forma estable durante horas, días o semanas, sobre hardware real, con datos reales, produciendo un modelo que generalice correctamente.

Las complejidades operativas no son menores. Un entrenamiento puede interrumpirse a mitad por un fallo de hardware, por agotamiento de memoria GPU, o por una inestabilidad numérica que convierte la pérdida en `NaN`. Los gradientes pueden explotar o desvanecerse sin aviso. El modelo puede sobreajustarse en las primeras épocas si el learning rate es demasiado alto, o puede estancarse durante cien épocas si es demasiado bajo. Sin una infraestructura de monitorización y control, es imposible distinguir entre un entrenamiento que progresa bien y uno que está desperdiciando tiempo y dinero de cómputo.

Esta unidad cubre las herramientas, patrones y criterios necesarios para ejecutar un entrenamiento de forma profesional: desde la estructura del bucle básico hasta las técnicas de precisión mixta y entrenamiento distribuido, pasando por callbacks de control, gestión de hardware y sistemas de monitorización. El objetivo no es únicamente que el modelo aprenda, sino que lo haga de manera reproducible, eficiente y diagnosticable.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Implementar un bucle de entrenamiento completo en PyTorch con soporte para DataLoaders, cálculo de pérdida y actualización de pesos.
- Diseñar e integrar callbacks de early stopping, reducción de learning rate y checkpointing.
- Gestionar el uso de GPU y CPU de forma eficiente, incluyendo técnicas de ahorro de memoria como gradient accumulation y gradient checkpointing.
- Aplicar entrenamiento en precisión mixta con `torch.cuda.amp` para reducir tiempos de cómputo y consumo de memoria.
- Comprender los paradigmas de entrenamiento distribuido (Data Parallelism y Model Parallelism) y configurar un entrenamiento con PyTorch DDP.
- Monitorizar el progreso del entrenamiento con TensorBoard, Weights & Biases y MLflow.
- Diagnosticar y resolver los problemas más comunes durante el entrenamiento: gradientes inestables, pérdida NaN, overfitting prematuro.

---

## 3. El bucle de entrenamiento

### 3.1 Estructura fundamental en PyTorch

El bucle de entrenamiento en PyTorch sigue una estructura canónica que se repite en todas las arquitecturas y tipos de tarea. Comprenderla en detalle es el punto de partida para cualquier extensión posterior.

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

# Definición de un dataset personalizado
class MiDataset(Dataset):
    def __init__(self, datos, etiquetas):
        self.datos = torch.tensor(datos, dtype=torch.float32)
        self.etiquetas = torch.tensor(etiquetas, dtype=torch.long)

    def __len__(self):
        return len(self.datos)

    def __getitem__(self, idx):
        return self.datos[idx], self.etiquetas[idx]

# Instanciación
dataset_train = MiDataset(X_train, y_train)
dataset_val = MiDataset(X_val, y_val)

train_loader = DataLoader(dataset_train, batch_size=64, shuffle=True, num_workers=4)
val_loader = DataLoader(dataset_val, batch_size=64, shuffle=False, num_workers=4)

# Configuración básica
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MiModelo().to(device)
criterio = nn.CrossEntropyLoss()
optimizador = torch.optim.Adam(model.parameters(), lr=1e-3)

# Bucle de entrenamiento
for epoch in range(num_epochs):
    model.train()
    perdida_total = 0.0

    for batch_idx, (entradas, etiquetas) in enumerate(train_loader):
        entradas = entradas.to(device)
        etiquetas = etiquetas.to(device)

        # 1. Forward pass
        salidas = model(entradas)

        # 2. Cálculo de la pérdida
        perdida = criterio(salidas, etiquetas)

        # 3. Backward pass
        optimizador.zero_grad()
        perdida.backward()

        # 4. Actualización de pesos
        optimizador.step()

        perdida_total += perdida.item()

    perdida_media = perdida_total / len(train_loader)
    print(f"Epoch {epoch+1}/{num_epochs} — Pérdida entrenamiento: {perdida_media:.4f}")
```

El orden de las cuatro operaciones fundamentales no es arbitrario. `zero_grad()` debe llamarse antes de `backward()` para evitar que los gradientes se acumulen entre batches (comportamiento que se usa intencionadamente en gradient accumulation, como veremos). `backward()` calcula los gradientes de todos los parámetros que tienen `requires_grad=True`. `step()` aplica la actualización según la regla definida por el optimizador.

### 3.2 DataLoaders y datasets personalizados

La clase `Dataset` de PyTorch requiere implementar tres métodos: `__init__` para inicialización, `__len__` para devolver el tamaño del dataset, y `__getitem__` para acceder a un elemento por índice. Este contrato permite que `DataLoader` gestione el batching, el shuffling y la carga paralela de datos sin que el programador deba intervenir.

El parámetro `num_workers` en `DataLoader` controla cuántos procesos secundarios se usan para precargar los datos. Un valor de 4 suele ser un punto de partida razonable; valores superiores pueden ser contraproducentes si el cuello de botella está en GPU y no en carga de datos.

El ciclo de validación se ejecuta sin cálculo de gradientes, lo que ahorra memoria y tiempo:

```python
model.eval()
with torch.no_grad():
    for entradas, etiquetas in val_loader:
        entradas, etiquetas = entradas.to(device), etiquetas.to(device)
        salidas = model(entradas)
        perdida_val = criterio(salidas, etiquetas)
```

---

## 4. Callbacks y control del entrenamiento

Los callbacks son mecanismos que interceptan el flujo de entrenamiento en puntos específicos (fin de epoch, fin de batch, etc.) para ejecutar lógica personalizada. Frameworks como PyTorch Lightning o Keras los gestionan de forma nativa; en PyTorch puro es habitual implementarlos como clases independientes.

### 4.1 Early stopping

El early stopping detiene el entrenamiento cuando la métrica de validación deja de mejorar durante un número determinado de épocas (paciencia). El objetivo es evitar el sobreajuste y ahorrar tiempo de cómputo.

```python
class EarlyStopping:
    def __init__(self, paciencia=10, delta=1e-4):
        self.paciencia = paciencia
        self.delta = delta
        self.contador = 0
        self.mejor_perdida = float('inf')
        self.detener = False

    def __call__(self, perdida_val):
        if perdida_val < self.mejor_perdida - self.delta:
            self.mejor_perdida = perdida_val
            self.contador = 0
        else:
            self.contador += 1
            if self.contador >= self.paciencia:
                self.detener = True

# Uso en el bucle
early_stopping = EarlyStopping(paciencia=10)

for epoch in range(num_epochs):
    # ... entrenamiento ...
    early_stopping(perdida_val)
    if early_stopping.detener:
        print(f"Early stopping en epoch {epoch+1}")
        break
```

El parámetro `delta` introduce un umbral mínimo de mejora: una reducción de pérdida inferior a `delta` no se considera una mejora real. Elegir bien la paciencia es crítico: demasiado baja interrumpe el entrenamiento antes de que el modelo haya convergido; demasiado alta puede no prevenir el overfitting.

### 4.2 Reducción de learning rate on plateau (ReduceLROnPlateau)

Cuando la pérdida de validación se estanca, reducir el learning rate puede permitir que el optimizador encuentre un mínimo más fino sin saltarlo. PyTorch incluye este scheduler de forma nativa:

```python
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizador,
    mode='min',
    factor=0.5,
    patience=5,
    verbose=True
)

for epoch in range(num_epochs):
    # ... entrenamiento ...
    scheduler.step(perdida_val)
```

El parámetro `factor` controla cuánto se reduce el learning rate (se multiplica por él). Un `factor=0.5` lo reduce a la mitad. El `patience` es independiente del early stopping: puede tener sentido que el scheduler reduzca el LR a las 5 épocas sin mejora, y que el early stopping detenga el entrenamiento a las 15.

### 4.3 Checkpointing

Guardar el estado del modelo periódicamente protege el trabajo ante fallos de hardware y permite recuperar el mejor checkpoint en caso de sobreajuste posterior:

```python
def guardar_checkpoint(model, optimizador, epoch, perdida, ruta):
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizador.state_dict(),
        'perdida': perdida,
    }, ruta)

def cargar_checkpoint(model, optimizador, ruta):
    checkpoint = torch.load(ruta, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizador.load_state_dict(checkpoint['optimizer_state_dict'])
    return checkpoint['epoch'], checkpoint['perdida']

# Guardar el mejor modelo
mejor_perdida_val = float('inf')
for epoch in range(num_epochs):
    # ... entrenamiento y validación ...
    if perdida_val < mejor_perdida_val:
        mejor_perdida_val = perdida_val
        guardar_checkpoint(model, optimizador, epoch, perdida_val, 'mejor_modelo.pt')
```

Es importante guardar tanto `model_state_dict` como `optimizer_state_dict`. El estado del optimizador contiene los momentos acumulados (en Adam) y otros valores que no deben perderse al reanudar un entrenamiento.

### 4.4 Logging de métricas por epoch

Un registro sistemático de métricas permite analizar el comportamiento del entrenamiento a posteriori:

```python
historial = {'perdida_train': [], 'perdida_val': [], 'accuracy_val': []}

for epoch in range(num_epochs):
    # ... calcular perdida_train, perdida_val, acc_val ...
    historial['perdida_train'].append(perdida_train)
    historial['perdida_val'].append(perdida_val)
    historial['accuracy_val'].append(acc_val)
    print(f"Epoch {epoch+1} | Train Loss: {perdida_train:.4f} | Val Loss: {perdida_val:.4f} | Val Acc: {acc_val:.4f}")
```

---

## 5. Gestión de hardware para entrenamiento

### 5.1 Uso eficiente de GPU

La GPU es el recurso más crítico y costoso en entrenamiento de redes profundas. La forma más básica de habilitar el uso de GPU en PyTorch es:

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
```

Todos los tensores que participen en el cómputo deben estar en el mismo dispositivo. Un error común es olvidar mover los tensores de entrada al dispositivo del modelo, lo que produce un error de tipo `RuntimeError: Expected all tensors to be on the same device`.

Para verificar el estado de la GPU desde la terminal:

```bash
nvidia-smi
nvidia-smi --query-gpu=memory.used,memory.free,utilization.gpu --format=csv -l 1
```

Desde Python, la memoria disponible y usada puede consultarse con:

```python
print(torch.cuda.memory_allocated() / 1e9, "GB usados")
print(torch.cuda.memory_reserved() / 1e9, "GB reservados")
torch.cuda.empty_cache()  # Libera la caché del allocator
```

Para perfilar el uso de memoria tensor por tensor, PyTorch ofrece el profiler:

```python
from torch.profiler import profile, record_function, ProfilerActivity

with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
    with record_function("forward"):
        salidas = model(entradas)

print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))
```

### 5.2 CPU multi-core con joblib

Para tareas de preprocesamiento o inferencia que corren en CPU, `joblib` permite paralelizar fácilmente sobre múltiples núcleos:

```python
from joblib import Parallel, delayed

def procesar_muestra(x):
    # Transformaciones costosas
    return transformacion(x)

resultados = Parallel(n_jobs=-1)(delayed(procesar_muestra)(x) for x in dataset)
```

`n_jobs=-1` utiliza todos los núcleos disponibles. Esta técnica es especialmente útil en pipelines de carga de datos cuando `num_workers` en `DataLoader` no es suficiente o no es aplicable.

### 5.3 Gradient accumulation

Cuando el batch size deseado no cabe en la memoria GPU, gradient accumulation permite simular batches grandes acumulando gradientes durante varios pasos antes de actualizar los pesos:

```python
pasos_acumulacion = 4  # Simula batch_size * 4

optimizador.zero_grad()
for batch_idx, (entradas, etiquetas) in enumerate(train_loader):
    entradas, etiquetas = entradas.to(device), etiquetas.to(device)
    salidas = model(entradas)
    perdida = criterio(salidas, etiquetas) / pasos_acumulacion
    perdida.backward()

    if (batch_idx + 1) % pasos_acumulacion == 0:
        optimizador.step()
        optimizador.zero_grad()
```

La pérdida se divide por el número de pasos de acumulación para que la magnitud del gradiente sea equivalente a la de un batch completo.

### 5.4 Gradient checkpointing

El gradient checkpointing es una técnica que reduce el consumo de memoria durante el backward pass a costa de recalcular activaciones intermedias. En lugar de guardar todas las activaciones durante el forward pass, solo se guardan los checkpoints de ciertos nodos del grafo computacional y se recomputan los intermedios durante el backward pass:

```python
from torch.utils.checkpoint import checkpoint

class MiModeloConCheckpointing(nn.Module):
    def forward(self, x):
        x = checkpoint(self.bloque1, x)
        x = checkpoint(self.bloque2, x)
        return x
```

Esta técnica puede reducir el consumo de memoria en un factor de hasta 4-10x en modelos profundos, a costa de un incremento de aproximadamente 30% en tiempo de cómputo.

---

## 6. Entrenamiento en precisión mixta (Mixed Precision Training)

### 6.1 Fundamentos de FP16 y BF16

Por defecto, PyTorch opera en precisión FP32 (32 bits flotantes). FP16 (16 bits) reduce el tamaño de los tensores a la mitad, lo que permite batches más grandes y cómputos más rápidos en hardware que soporte operaciones FP16 (GPUs NVIDIA con Tensor Cores, como las series Volta, Turing, Ampere y Ada).

El problema de FP16 es su rango dinámico limitado: valores muy pequeños se redondean a cero (underflow) y valores muy grandes se convierten en `inf` (overflow). BF16 (Brain Float 16) soluciona el problema del rango dinámico manteniendo el mismo exponente que FP32, aunque con menor precisión en la mantisa. BF16 está disponible en GPUs Ampere (A100) y en TPUs.

El entrenamiento en precisión mixta usa FP16/BF16 para las operaciones de forward y backward, pero mantiene una copia maestra de los pesos en FP32 para la actualización, lo que garantiza estabilidad numérica.

### 6.2 torch.cuda.amp y GradScaler

PyTorch implementa precisión mixta automática a través del módulo `torch.cuda.amp`:

```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for epoch in range(num_epochs):
    model.train()
    for entradas, etiquetas in train_loader:
        entradas, etiquetas = entradas.to(device), etiquetas.to(device)
        optimizador.zero_grad()

        # Forward pass en FP16/BF16
        with autocast():
            salidas = model(entradas)
            perdida = criterio(salidas, etiquetas)

        # Backward pass con escalado de gradientes
        scaler.scale(perdida).backward()
        scaler.step(optimizador)
        scaler.update()
```

`GradScaler` escala la pérdida antes del backward pass para evitar underflow en los gradientes FP16. Después del backward, `scaler.step()` desescala los gradientes y llama al optimizador solo si no hay `inf` ni `NaN` en los gradientes. Si los hay, el paso se omite y el factor de escala se reduce. Con el tiempo, `scaler.update()` ajusta el factor de escala dinámicamente.

### 6.3 Beneficios en velocidad y memoria

En benchmarks típicos con GPUs Tensor Core, el entrenamiento en precisión mixta puede ser entre 2 y 4 veces más rápido que FP32 puro, dependiendo de la arquitectura del modelo y el tamaño del batch. La reducción de memoria es de aproximadamente un 40-50% en los activaciones y gradientes, lo que permite usar batches más grandes o modelos más profundos. Para redes de visión artificiales (ResNets, ViTs) y modelos de lenguaje (transformers), la ganancia es especialmente significativa.

---

## 7. Entrenamiento distribuido

### 7.1 Data Parallelism vs Model Parallelism

Cuando un modelo o el volumen de datos superan la capacidad de una sola GPU, el entrenamiento distribuido se vuelve necesario. Existen dos paradigmas principales:

**Data Parallelism:** el modelo se replica en cada GPU y cada réplica procesa un subconjunto distinto del batch. Los gradientes se sincronizan al final de cada paso y los pesos se actualizan de forma idéntica en todas las réplicas. Es el enfoque más común para modelos que caben en una sola GPU.

**Model Parallelism:** el modelo se divide entre varias GPUs, de modo que cada una alberga solo una parte de sus capas. Es necesario cuando el modelo es demasiado grande para caber en una sola GPU (como modelos de lenguaje muy grandes). Existe también el Pipeline Parallelism, variante del Model Parallelism que divide el modelo en etapas ejecutadas en paralelo sobre diferentes microbatches.

### 7.2 PyTorch DistributedDataParallel (DDP)

`DistributedDataParallel` es la implementación recomendada de Data Parallelism en PyTorch. A diferencia de `DataParallel` (que corre en un solo proceso con múltiples threads), DDP usa múltiples procesos, uno por GPU, lo que elimina el GIL de Python como cuello de botella.

Configuración básica:

```python
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler

def entrenar_ddp(rank, world_size):
    # Inicializar el grupo de procesos
    dist.init_process_group(
        backend='nccl',
        init_method='env://',
        rank=rank,
        world_size=world_size
    )

    # Asignar GPU al proceso
    torch.cuda.set_device(rank)
    device = torch.device(f'cuda:{rank}')

    # Modelo en DDP
    model = MiModelo().to(device)
    model = DDP(model, device_ids=[rank])

    # Sampler distribuido para evitar solapamiento de datos
    sampler = DistributedSampler(dataset_train, num_replicas=world_size, rank=rank)
    train_loader = DataLoader(dataset_train, batch_size=64, sampler=sampler)

    optimizador = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterio = nn.CrossEntropyLoss()

    for epoch in range(num_epochs):
        sampler.set_epoch(epoch)  # Garantiza shuffling distinto por epoch
        for entradas, etiquetas in train_loader:
            entradas, etiquetas = entradas.to(device), etiquetas.to(device)
            salidas = model(entradas)
            perdida = criterio(salidas, etiquetas)
            optimizador.zero_grad()
            perdida.backward()
            optimizador.step()

    dist.destroy_process_group()

# Lanzar con torchrun
# torchrun --nproc_per_node=4 script.py
```

El backend `nccl` es el recomendado para comunicación GPU-GPU. La clave de DDP es que la sincronización de gradientes se hace mediante `AllReduce` durante el backward pass, de forma solapada con el cómputo, lo que minimiza la latencia de comunicación.

### 7.3 Horovod

Horovod es un framework de entrenamiento distribuido desarrollado por Uber que funciona con PyTorch, TensorFlow y MXNet. Su integración con PyTorch es sencilla:

```python
import horovod.torch as hvd

hvd.init()
torch.cuda.set_device(hvd.local_rank())

model = MiModelo().cuda()
optimizador = torch.optim.SGD(model.parameters(), lr=0.01 * hvd.size())
optimizador = hvd.DistributedOptimizer(optimizador, named_parameters=model.named_parameters())
hvd.broadcast_parameters(model.state_dict(), root_rank=0)
```

Horovod es especialmente popular en entornos de cluster heterogéneos donde diferentes nodos pueden tener diferentes configuraciones de hardware.

### 7.4 Cuándo usar entrenamiento distribuido

El entrenamiento distribuido introduce complejidad operativa significativa: gestión de procesos, comunicación entre nodos, debugging más difícil. No debe adoptarse por defecto. Los criterios para considerar el entrenamiento distribuido son: modelos que no caben en una sola GPU (Model Parallelism), tiempos de entrenamiento inaceptables con una sola GPU, o datasets tan grandes que requieren procesamiento paralelo para completar una epoch en un tiempo razonable.

---

## 8. Monitorización del entrenamiento

### 8.1 TensorBoard

TensorBoard es la herramienta de visualización estándar del ecosistema PyTorch/TensorFlow. Permite visualizar curvas de pérdida, métricas de evaluación, histogramas de pesos y gradientes, imágenes de muestra y grafos computacionales.

Instalación:

```bash
pip install tensorboard
```

Uso básico con PyTorch:

```python
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter(log_dir='runs/experimento_01')

for epoch in range(num_epochs):
    # ... entrenamiento ...
    writer.add_scalar('Pérdida/entrenamiento', perdida_train, epoch)
    writer.add_scalar('Pérdida/validación', perdida_val, epoch)
    writer.add_scalar('Accuracy/validación', acc_val, epoch)

    # Histogramas de pesos (útil para detectar problemas de gradientes)
    for nombre, param in model.named_parameters():
        writer.add_histogram(nombre, param, epoch)
        if param.grad is not None:
            writer.add_histogram(f'{nombre}.grad', param.grad, epoch)

writer.close()
```

Para visualizar:

```bash
tensorboard --logdir=runs
```

TensorBoard lanza un servidor local (por defecto en el puerto 6006) con una interfaz web interactiva.

### 8.2 Weights & Biases (W&B)

W&B es una plataforma en la nube para gestión de experimentos de machine learning. Ofrece tracking de métricas, visualización comparativa de experimentos, sweeps de hiperparámetros y alertas.

```python
import wandb

wandb.init(
    project="mi-proyecto",
    name="experimento-01",
    config={
        "learning_rate": 1e-3,
        "batch_size": 64,
        "num_epochs": 50,
        "arquitectura": "ResNet18"
    }
)

for epoch in range(num_epochs):
    # ... entrenamiento ...
    wandb.log({
        "perdida_train": perdida_train,
        "perdida_val": perdida_val,
        "accuracy_val": acc_val,
        "epoch": epoch
    })

wandb.finish()
```

Los sweeps de W&B permiten búsqueda automática de hiperparámetros con configuración declarativa:

```yaml
# sweep.yaml
program: train.py
method: bayes
metric:
  name: perdida_val
  goal: minimize
parameters:
  learning_rate:
    distribution: log_uniform_values
    min: 1e-5
    max: 1e-2
  batch_size:
    values: [32, 64, 128]
```

```bash
wandb sweep sweep.yaml
wandb agent <sweep_id>
```

W&B también permite configurar alertas que notifican por email o Slack cuando una métrica supera un umbral o cuando el entrenamiento se detiene inesperadamente.

### 8.3 MLflow tracking

MLflow es una plataforma de código abierto para el ciclo de vida completo de modelos ML. Su módulo de tracking registra parámetros, métricas y artefactos:

```python
import mlflow

mlflow.set_experiment("mi-experimento")

with mlflow.start_run():
    mlflow.log_params({
        "learning_rate": 1e-3,
        "batch_size": 64
    })

    for epoch in range(num_epochs):
        # ... entrenamiento ...
        mlflow.log_metrics({
            "perdida_train": perdida_train,
            "perdida_val": perdida_val
        }, step=epoch)

    # Registrar el modelo
    mlflow.pytorch.log_model(model, "modelo")
```

MLflow puede ejecutarse con servidor local o en infraestructura cloud, y se integra con plataformas como Databricks y Azure ML.

---

## 9. Problemas comunes y diagnóstico

### 9.1 Gradientes explosivos (exploding gradients)

Los gradientes explosivos ocurren cuando los valores de los gradientes crecen exponencialmente durante el backward pass, produciendo actualizaciones de pesos desproporcionadas. El síntoma más visible es una pérdida que de repente se dispara o se convierte en `NaN`.

El remedio estándar es gradient clipping, que limita la norma del vector de gradientes a un valor máximo:

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

Esta línea debe insertarse entre `backward()` y `step()`. Monitorizar la norma del gradiente durante el entrenamiento ayuda a detectar el problema antes de que se vuelva crítico:

```python
grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
writer.add_scalar('Gradientes/norma', grad_norm, global_step)
```

### 9.2 Gradientes que desaparecen (vanishing gradients)

En redes muy profundas, los gradientes pueden hacerse tan pequeños que los parámetros de las capas más cercanas a la entrada prácticamente no se actualizan. Esto frena o impide el aprendizaje en esas capas.

Las soluciones modernas incluyen: uso de conexiones residuales (ResNets), normalización por capas (Layer Normalization) o por batch (Batch Normalization), funciones de activación que no saturen (ReLU y sus variantes), e inicialización cuidadosa de pesos (He, Xavier/Glorot). En modelos recurrentes, las celdas LSTM y GRU están diseñadas específicamente para mitigar este problema.

### 9.3 Overfitting prematuro

El overfitting se manifiesta cuando la pérdida de entrenamiento continúa bajando pero la pérdida de validación empieza a subir. Las estrategias para combatirlo incluyen: regularización L2 (weight decay en el optimizador), Dropout, aumento de datos (data augmentation), reducción de la complejidad del modelo, y early stopping como se describió en la sección 4.

```python
optimizador = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
```

### 9.4 Inestabilidad de la pérdida y NaN loss

Una pérdida que oscila salvajemente o se convierte en `NaN` puede tener múltiples causas: learning rate demasiado alto, gradientes explosivos, valores `NaN` en los datos de entrada, división por cero en la función de pérdida, o overflow en precisión FP16 sin GradScaler.

Procedimiento de diagnóstico:

```python
# Verificar NaN en datos de entrada
assert not torch.isnan(entradas).any(), "NaN en entradas"
assert not torch.isinf(entradas).any(), "Inf en entradas"

# Verificar NaN en pérdida
if torch.isnan(perdida):
    print("Pérdida NaN detectada en epoch", epoch, "batch", batch_idx)
    # Guardar el batch problemático para análisis
    torch.save({'entradas': entradas, 'etiquetas': etiquetas}, 'batch_problematico.pt')
    break
```

Otra estrategia es empezar con un learning rate muy bajo (1e-6) y aumentarlo gradualmente para identificar el umbral de inestabilidad.

---

## 10. Actividades prácticas propuestas

**Actividad 1: Bucle de entrenamiento completo con callbacks**

Implementar un pipeline de entrenamiento completo en PyTorch para clasificación de imágenes sobre el dataset CIFAR-10. El pipeline debe incluir: DataLoaders con aumento de datos (random crop, horizontal flip), bucle de entrenamiento con logging por epoch, early stopping con paciencia 10, ReduceLROnPlateau con paciencia 5, y checkpointing del mejor modelo. Al finalizar, el estudiante debe generar una gráfica con las curvas de pérdida de entrenamiento y validación a lo largo de las épocas.

**Actividad 2: Entrenamiento en precisión mixta**

Partiendo del pipeline de la Actividad 1, añadir soporte para entrenamiento en precisión mixta con `torch.cuda.amp`. Medir y comparar: tiempo de epoch, pico de memoria GPU utilizada, y pérdida final de validación, con y sin precisión mixta. Documentar los resultados en una tabla y analizar las diferencias observadas.

**Actividad 3: Monitorización con TensorBoard y W&B**

Modificar el pipeline de entrenamiento para registrar simultáneamente en TensorBoard y W&B: curvas de pérdida y accuracy, norma del gradiente por epoch, histogramas de pesos de la primera y última capa, y el valor del learning rate después de cada ajuste de ReduceLROnPlateau. Ejecutar tres configuraciones distintas (variando el learning rate inicial) y comparar los resultados en el panel de W&B.

**Actividad 4: Diagnóstico de problemas**

Se proporcionan tres scripts de entrenamiento deliberadamente defectuosos: uno con gradientes explosivos, uno con NaN loss causado por datos mal normalizados, y uno con overfitting severo. El estudiante debe identificar cada problema a partir de las curvas de pérdida y los logs, aplicar las correcciones apropiadas (gradient clipping, normalización de datos, regularización) y verificar que el entrenamiento se estabiliza después de cada corrección. Entregar un breve informe de diagnóstico y solución para cada caso.

---

## 11. Referencias

1. **PyTorch Documentation** — *Training a Classifier*, *torch.optim*, *torch.cuda.amp*, *DistributedDataParallel*. PyTorch, 2024. Disponible en: https://pytorch.org/docs/stable/index.html

2. **Goodfellow, I., Bengio, Y., & Courville, A.** — *Deep Learning*. MIT Press, 2016. Capítulos 7 (Regularización), 8 (Optimización) y 11 (Metodología práctica). Disponible en: https://www.deeplearningbook.org/

3. **Micikevicius, P., Narang, S., Alben, J., Diamos, G., Elsen, E., Garcia, D., ... & Wu, H.** — *Mixed Precision Training*. arXiv preprint arXiv:1710.03740, 2018. ICLR 2018. Disponible en: https://arxiv.org/abs/1710.03740

4. **Sergeev, A., & Del Balso, M.** — *Horovod: fast and easy distributed deep learning in TensorFlow*. arXiv preprint arXiv:1802.05799, 2018. Disponible en: https://arxiv.org/abs/1802.05799

5. **Weights & Biases Documentation** — *Quickstart*, *Sweeps*, *Alerts*. Weights & Biases, 2024. Disponible en: https://docs.wandb.ai/

6. **TensorBoard Documentation** — *Get started with TensorBoard*, *Visualizing Model, Data, and Training with TensorBoard*. TensorFlow / PyTorch, 2024. Disponible en: https://www.tensorflow.org/tensorboard/get_started y https://pytorch.org/tutorials/intermediate/tensorboard_tutorial.html

7. **MLflow Documentation** — *MLflow Tracking*, *MLflow Models*. MLflow, 2024. Disponible en: https://mlflow.org/docs/latest/index.html

8. **Chen, T., Xu, B., Zhang, C., & Guestrin, C.** — *Training Deep Nets with Sublinear Memory Cost* (Gradient Checkpointing). arXiv preprint arXiv:1604.06174, 2016. Disponible en: https://arxiv.org/abs/1604.06174

9. **PyTorch Distributed Overview** — *Getting Started with Distributed Data Parallel*, *torch.distributed*. PyTorch, 2024. Disponible en: https://pytorch.org/tutorials/intermediate/ddp_tutorial.html

10. **Pascanu, R., Mikolov, T., & Bengio, Y.** — *On the difficulty of training recurrent neural networks* (Gradient Clipping). Proceedings of the 30th International Conference on Machine Learning (ICML), 2013. Disponible en: https://arxiv.org/abs/1211.5063
