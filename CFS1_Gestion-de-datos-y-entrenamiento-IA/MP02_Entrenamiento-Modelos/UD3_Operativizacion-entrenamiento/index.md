---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD3 · Operativización del entrenamiento | MP02 · Entrenamiento de modelos de aprendizaje automático'
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

# UD3 · Operativización del entrenamiento

**MP02 · Entrenamiento de modelos de aprendizaje automático**

CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Ejecutar búsquedas de hiperparámetros con distintas estrategias (grid, random, bayesiana)
- Utilizar Optuna u otras herramientas para la optimización automática de hiperparámetros
- Monitorizar el proceso de entrenamiento en tiempo real con TensorBoard u otras plataformas
- Detectar sobreajuste e infraajuste a partir de las curvas de pérdida
- Aplicar técnicas de mejora: early stopping, regularización L1/L2, ajuste del learning rate
- Documentar los experimentos y justificar la configuración final seleccionada

---

## Búsqueda de hiperparámetros — Concepto

Los **hiperparámetros** son parámetros que no se aprenden durante el entrenamiento sino que se fijan antes: learning rate, número de capas, neuronas por capa, batch size, factor de regularización. Su elección tiene un impacto enorme en el rendimiento final.

**Por qué la búsqueda sistemática es necesaria:**
- Los valores por defecto de los frameworks son puntos de partida, no configuraciones óptimas
- La sensibilidad de los hiperparámetros varía por problema: no se puede transferir una configuración de un proyecto a otro sin validar
- La búsqueda manual es lenta, sesgada y no reproducible

> Un modelo con arquitectura mediocre bien ajustado en hiperparámetros supera habitualmente a un modelo potente mal configurado.

---

## Búsqueda de hiperparámetros — Grid Search

**Grid Search** evalúa todas las combinaciones posibles del espacio de búsqueda definido.

```python
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier

parametros = {
    "n_estimators": [100, 200, 300],
    "learning_rate": [0.01, 0.05, 0.1],
    "max_depth": [3, 5, 7]
}  # 3 x 3 x 3 = 27 combinaciones a evaluar

busqueda = GridSearchCV(
    estimator=GradientBoostingClassifier(random_state=42),
    param_grid=parametros,
    cv=5,          # 5-fold cross validation
    scoring="f1",
    n_jobs=-1      # usar todos los cores disponibles
)
busqueda.fit(X_train, y_train)
print(f"Mejores params: {busqueda.best_params_}")
print(f"Mejor F1: {busqueda.best_score_:.4f}")
```

---

## Búsqueda de hiperparámetros — Random Search

**Random Search** muestrea combinaciones aleatorias del espacio. Con el mismo presupuesto computacional suele encontrar mejores soluciones que Grid Search porque cubre un espacio más amplio.

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import uniform, randint

espacio = {
    "n_estimators": randint(50, 500),
    "learning_rate": uniform(0.001, 0.2),
    "max_depth": randint(2, 10),
    "min_samples_split": randint(2, 20)
}

busqueda = RandomizedSearchCV(
    estimator=GradientBoostingClassifier(random_state=42),
    param_distributions=espacio,
    n_iter=50,      # numero de combinaciones aleatorias
    cv=5,
    scoring="f1",
    random_state=42,
    n_jobs=-1
)
busqueda.fit(X_train, y_train)
```

---

## Búsqueda de hiperparámetros — Optimización bayesiana con Optuna

**Optimización bayesiana** usa los resultados de ensayos anteriores para elegir los siguientes puntos a evaluar, concentrando la búsqueda en las regiones más prometedoras.

```python
import optuna
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

def objetivo(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 50, 500),
        "learning_rate": trial.suggest_float("learning_rate", 1e-4, 0.3, log=True),
        "max_depth": trial.suggest_int("max_depth", 2, 10),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 20)
    }
    modelo = GradientBoostingClassifier(**params, random_state=42)
    return cross_val_score(modelo, X_train, y_train, cv=5, scoring="f1").mean()

estudio = optuna.create_study(direction="maximize")
estudio.optimize(objetivo, n_trials=100, timeout=3600)  # max 1 hora
print(f"Mejores params: {estudio.best_params}")
```

---

## Búsqueda de hiperparámetros — Comparativa de estrategias

| Estrategia | Cobertura del espacio | Eficiencia computacional | Cuándo usarla |
|---|---|---|---|
| **Grid Search** | Exhaustiva (espacio discreto) | Baja con muchos params | Pocos hiperparámetros (<3), espacio pequeño |
| **Random Search** | Aleatoria | Media | Espacios medianos, primer barrido rápido |
| **Optimización bayesiana** | Guiada por resultados | Alta | Espacios grandes, training costoso |
| **Halving (Successive Halving)** | Progresiva | Muy alta | Muchos candidatos, recursos limitados |

**Herramientas disponibles:** Optuna · Ray Tune · Weights & Biases Sweeps · Scikit-learn GridSearchCV/RandomizedSearchCV · Keras Tuner

---

## Monitorización en tiempo real — Concepto

Monitorizar el entrenamiento permite detectar problemas antes de que se desperdicien horas de cómputo. Las curvas de pérdida y métricas por época son el instrumento principal de diagnóstico.

**Qué monitorizar:**
- Pérdida en entrenamiento y validación por época
- Métrica principal (accuracy, F1, AUC...) en entrenamiento y validación
- Tasa de aprendizaje actual (si se usa scheduler)
- Uso de GPU/CPU y memoria
- Tiempo por época

---

## Monitorización — TensorBoard

```python
from torch.utils.tensorboard import SummaryWriter
import torch

writer = SummaryWriter("runs/experimento_001")

for epoca in range(num_epocas):
    # --- Fase de entrenamiento ---
    modelo.train()
    perdida_train = ejecutar_epoch(loader_train, modelo, optimizer, criterio)

    # --- Fase de validacion ---
    modelo.eval()
    perdida_val, f1_val = evaluar(loader_val, modelo, criterio)

    # --- Registrar en TensorBoard ---
    writer.add_scalar("Loss/train", perdida_train, epoca)
    writer.add_scalar("Loss/val", perdida_val, epoca)
    writer.add_scalar("F1/val", f1_val, epoca)
    writer.add_scalar("LR", optimizer.param_groups[0]["lr"], epoca)

writer.close()
# Lanzar: tensorboard --logdir=runs/
```

---

## Monitorización — Diagnóstico de curvas

**Curva de pérdida — Patrones y su significado:**

```
Sobreajuste (overfitting):         Infraajuste (underfitting):
Loss                               Loss
  |  train ──────────              |  train ────────────
  |           val ╲               |  val ─────────────
  |               ╲               |
  └──────────────── epoch          └──────────────── epoch
  Train baja, val sube             Ambas altas y estancadas

Convergencia correcta:
Loss
  |  train ╲
  |   val   ╲___________
  └──────────────── epoch
  Ambas bajan y se estabilizan juntas
```

---

## Técnicas de mejora — Early Stopping

**Early stopping** detiene el entrenamiento cuando la métrica de validación deja de mejorar, evitando el sobreajuste y ahorrando cómputo innecesario.

```python
import torch

class EarlyStopping:
    def __init__(self, patience=5, delta=1e-4, ruta_checkpoint="mejor_modelo.pt"):
        self.patience = patience
        self.delta = delta
        self.ruta = ruta_checkpoint
        self.contador = 0
        self.mejor_perdida = float("inf")

    def paso(self, perdida_val, modelo):
        if perdida_val < self.mejor_perdida - self.delta:
            self.mejor_perdida = perdida_val
            torch.save(modelo.state_dict(), self.ruta)
            self.contador = 0
        else:
            self.contador += 1
        return self.contador >= self.patience  # True = detener

parada = EarlyStopping(patience=5)
for epoca in range(100):
    perdida_val = entrenar_epoch(...)
    if parada.paso(perdida_val, modelo):
        print(f"Parada temprana en época {epoca}")
        break
```

---

## Técnicas de mejora — Regularización L1 y L2

**Regularización** penaliza los pesos grandes del modelo, reduciendo el sobreajuste al forzar soluciones más simples.

| Tipo | Penalización añadida | Efecto | Cuándo usarla |
|---|---|---|---|
| **L2 (Ridge / Weight Decay)** | lambda · sum(w²) | Pesos pequeños pero no cero | Sobreajuste general en DL |
| **L1 (Lasso)** | lambda · sum(\|w\|) | Pesos exactamente a cero (sparse) | Selección de features implícita |
| **Elastic Net** | L1 + L2 combinadas | Intermedio | Muchas features correladas |

```python
# L2 en PyTorch (weight_decay en el optimizador)
optimizer = torch.optim.AdamW(modelo.parameters(), lr=1e-3, weight_decay=1e-4)

# L1 añadida manualmente a la pérdida
lambda_l1 = 1e-5
perdida_l1 = lambda_l1 * sum(p.abs().sum() for p in modelo.parameters())
perdida_total = perdida_criterio + perdida_l1
```

---

## Técnicas de mejora — Learning Rate Scheduling

El **scheduler del learning rate** ajusta automáticamente la tasa de aprendizaje a lo largo del entrenamiento, permitiendo convergencia rápida al inicio y ajuste fino al final.

```python
import torch.optim as optim

# Reducir lr cuando la validacion no mejora
scheduler_plateau = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode="min", factor=0.5, patience=3, verbose=True
)

# Cosine Annealing: lr sigue una curva coseno (muy usado en LLMs)
scheduler_cosine = optim.lr_scheduler.CosineAnnealingLR(
    optimizer, T_max=50, eta_min=1e-6
)

# Warm-up + decay: subida gradual inicial, luego bajada
from transformers import get_linear_schedule_with_warmup
scheduler_warmup = get_linear_schedule_with_warmup(
    optimizer, num_warmup_steps=100, num_training_steps=1000
)
```

---

## Lanzamiento del entrenamiento definitivo

Una vez completada la búsqueda de hiperparámetros y validadas las técnicas de mejora, se lanza el entrenamiento definitivo con la configuración seleccionada.

**Protocolo antes del lanzamiento:**

```python
# Checklist previo al entrenamiento definitivo
assert semilla_fijada, "Fijar semilla antes de iniciar"
assert ruta_checkpoint.exists(), "Directorio de checkpoints creado"
assert config_registrada, "Configuracion guardada en JSON/YAML"
assert dataset_version == "v2.1", "Verificar version exacta del dataset"

# Guardar configuracion completa
import json
config = {
    "semilla": 42, "lr": 2e-5, "batch_size": 32, "epocas_max": 50,
    "early_stopping_patience": 5, "weight_decay": 1e-4,
    "modelo_base": "bert-base-spanish-wwm-cased", "dataset": "v2.1"
}
with open("experimento_001_config.json", "w") as f:
    json.dump(config, f, indent=2)
```

---

## Documentación de experimentos

Sin registro sistemático de experimentos, la comparación entre configuraciones es imposible y el trabajo no es reproducible ni auditable.

**Herramientas de registro de experimentos:**

| Herramienta | Tipo | Fortaleza |
|---|---|---|
| **MLflow** | Open source, self-hosted | Tracking, registro de modelos, UI |
| **Weights & Biases (W&B)** | SaaS / self-hosted | Visualización colaborativa, sweeps |
| **TensorBoard** | Local | Curvas de entrenamiento en tiempo real |
| **DVC** | Open source | Versionado de datos + experimentos con Git |

```python
import mlflow

with mlflow.start_run(run_name="experimento_001"):
    mlflow.log_params(config)
    mlflow.log_metric("f1_val", f1_val, step=epoca)
    mlflow.pytorch.log_model(modelo, "modelo")
```

---

## Actividad práctica — UD3

**Contexto:** Continúas con el clasificador de texto tóxico de UD2. Has entrenado un primer modelo con la configuración base y obtienes F1=0.72. El objetivo del proyecto es alcanzar F1>=0.80.

**Tareas:**

1. Diseña un estudio Optuna con al menos 4 hiperparámetros (lr, batch_size, dropout, num_epochs). Escribe la función objetivo completa
2. Configura TensorBoard y añade el registro de pérdida y F1 en validación por época
3. Interpreta el siguiente escenario: train loss = 0.15, val loss = 0.72. ¿Qué técnicas aplicarías y en qué orden?
4. Implementa un callback de Early Stopping con patience=5 y guarda el mejor checkpoint
5. Tras la búsqueda de hiperparámetros, documenta el experimento definitivo en un JSON con todos los campos requeridos

---

## Puntos clave — UD3

- Grid Search solo es adecuado con espacios de búsqueda pequeños; para el resto, Random Search o bayesiana son más eficientes
- Optuna permite buscar en espacios continuos y discretos con la misma API y con pruning automático de ensayos malos
- El diagnóstico visual de las curvas de pérdida es la herramienta más rápida para detectar sobreajuste o infraajuste
- Early stopping ahorra cómputo y actúa como regularización implícita: siempre usarlo en entrenamiento prolongado
- L2 se implementa como `weight_decay` en el optimizador; L1 se añade manualmente a la función de pérdida
- Documentar cada experimento con MLflow o W&B es el estándar profesional: permite comparar, reproducir y auditar

---

## Criterios de evaluación — UD3

| Criterio | Indicador de logro |
|---|---|
| Ejecuta búsquedas de hiperparámetros | Implementa al menos una estrategia (grid, random o bayesiana) con validación cruzada |
| Monitoriza el entrenamiento | Configura TensorBoard o equivalente y registra pérdida y métrica principal |
| Detecta sobreajuste/infraajuste | Interpreta las curvas de entrenamiento y diagnóstica correctamente |
| Aplica técnicas de mejora | Implementa early stopping y regularización ante resultados insatisfactorios |
| Documenta los experimentos | Registra configuración y resultados de cada ensayo con herramienta de tracking |
| Lanza el entrenamiento definitivo | Ejecuta con semilla fijada, configuración documentada y checkpoint activado |
