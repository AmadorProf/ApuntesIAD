---
marp: true
theme: default
paginate: true
size: 16:9
header: 'MP02 · Entrenamiento de modelos de aprendizaje automático'
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
section.lead h1 { font-size: 2.2em; text-align: center; margin-top: 120px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
</style>

<!-- _class: lead -->

# MP02 · Entrenamiento de modelos de aprendizaje automático

CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Ficha del módulo

| Campo | Valor |
|---|---|
| Código | **MP02** |
| Estándar de competencia | ECP2493_3 · Nivel 3 |
| Familia profesional | Inteligencia Artificial y Data |
| Duración | **190 h** |
| Curso | **1.º** |

> **Competencia que desarrolla:** implementar la estrategia de entrenamiento mediante el análisis del problema, la configuración de arquitecturas y parámetros, el diseño de modelos de Machine Learning y su versionado para garantizar trazabilidad y despliegue.

---

## Estructura del módulo

| # | Unidad didáctica |
|---|---|
| **UD1** | Selección de la estrategia de entrenamiento |
| **UD2** | Configuración del modelo y del entorno de entrenamiento |
| **UD3** | Operativización del entrenamiento |
| **UD4** | Evaluación del modelo entrenado |
| **UD5** | Versionado y ficha técnica del modelo |
| **UD6** | Trabajo responsable, sostenible y PRL |

---

<!-- _class: lead -->

# UD1
## Selección de la estrategia de entrenamiento

---

## UD1 · Paradigmas de aprendizaje automático

| Paradigma | Datos necesarios | Cuándo usarlo |
|---|---|---|
| **Supervisado** | Etiquetados (entrada + salida) | Clasificación, regresión con ground truth |
| **No supervisado** | Sin etiquetar | Clustering, reducción de dimensionalidad |
| **Autosupervisado** | Sin etiquetar (genera sus propias etiquetas) | Pre-entrenamiento de LLMs, visión |
| **Por refuerzo** | Retroalimentación de recompensa | Agentes, decisiones secuenciales |

> El **paradigma** se determina según la disponibilidad de etiquetas, el objetivo funcional y los recursos disponibles.

---

## UD1 · Entrenar desde cero vs. fine-tuning

| Criterio | Entrenar desde cero | Fine-tuning |
|---|---|---|
| **Volumen de datos** | Grande (millones de ejemplos) | Pequeño o mediano |
| **Recursos de cómputo** | Muy elevados | Moderados |
| **Tiempo** | Semanas o meses | Horas o días |
| **Especialización** | General o de dominio | Muy especializado |
| **Coste** | Alto | Bajo |

**Cuándo hacer fine-tuning:** cuando existe un modelo preentrenado en el dominio y los datos propios son limitados o confidenciales.

---

## UD1 · Familias de modelos candidatos

| Familia | Casos de uso típicos |
|---|---|
| **ML clásico** (sklearn) | Tabular: clasificación, regresión, clustering |
| **Redes neuronales** | Problemas no lineales complejos |
| **Modelos de visión** (CNN, ViT) | Imagen, vídeo, datos espaciales |
| **Modelos de lenguaje** (Transformers) | Texto, código, multimodal |
| **Series temporales** (LSTM, Prophet) | Predicción temporal, pronóstico |

**Documentar:** criterios de decisión · alternativas consideradas · justificación de la elección

---

<!-- _class: lead -->

# UD2
## Configuración del modelo y del entorno de entrenamiento

---

## UD2 · Frameworks y arquitecturas

**Ecosistema principal:**

- **Scikit-learn:** ML clásico, API unificada, pipelines
- **PyTorch:** investigación, redes neuronales flexibles, dinámica
- **TensorFlow / Keras:** producción, despliegue móvil y web, estático
- **HuggingFace Transformers:** modelos de lenguaje preentrenados

**Selección de arquitectura:**
- Modelo desde cero: definición capa a capa
- Modelo preentrenado: carga de pesos y adaptación del *head*
- Selección según naturaleza del dato (tabular, imagen, texto, audio…)

---

## UD2 · Función de pérdida y parámetros

| Tipo de problema | Función de pérdida habitual |
|---|---|
| Clasificación binaria | Binary Cross-Entropy |
| Clasificación multiclase | Categorical Cross-Entropy |
| Regresión | MSE (Mean Squared Error) |
| Regresión robusta | MAE (Mean Absolute Error) |
| Ranking / similitud | Contrastive Loss, Triplet Loss |

**Parámetros clave del algoritmo:**
- **Learning rate:** velocidad de ajuste de los pesos
- **Batch size:** número de ejemplos por actualización
- **Épocas:** número de pasadas completas sobre el conjunto de entrenamiento

---

## UD2 · Entorno reproducible

**Preparación del entorno de cómputo:**
- CPU · GPU (CUDA/ROCm) · TPU · Nube (Colab, SageMaker, Vertex AI)
- Gestión de dependencias: `pip`, `conda`, `poetry`, contenedores Docker

**Garantías de reproducibilidad:**
```python
# Control de semillas aleatorias
import random, numpy as np, torch
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)
```
- Versionado de librerías: `requirements.txt`, `pyproject.toml`, `environment.yml`
- Registro de la configuración completa antes de cada experimento

---

<!-- _class: lead -->

# UD3
## Operativización del entrenamiento

---

## UD3 · Búsqueda de hiperparámetros

| Método | Descripción | Cuándo usarlo |
|---|---|---|
| **Grid Search** | Todas las combinaciones posibles | Espacios pequeños y discretos |
| **Random Search** | Combinaciones aleatorias | Espacios medianos, rápido |
| **Optimización bayesiana** | Guiada por resultados anteriores | Espacios grandes, costoso |

**Herramientas:** Optuna · Ray Tune · Weights & Biases Sweeps · Scikit-learn GridSearchCV

```python
import optuna
study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)
```

---

## UD3 · Monitorización y técnicas de mejora

**Monitorización en tiempo real:**
- TensorBoard: curvas de pérdida y métricas por época
- MLflow: registro de experimentos y comparación
- W&B: trazabilidad completa y visualización colaborativa

**Técnicas ante sobreajuste:**

| Problema | Técnica |
|---|---|
| **Sobreajuste** | Parada temprana (*early stopping*), Dropout, Regularización L1/L2 |
| **Infraajuste** | Aumentar capacidad del modelo, más épocas, reducir regularización |
| **Convergencia lenta** | Learning rate scheduling (cosine, step decay, warm-up) |

---

<!-- _class: lead -->

# UD4
## Evaluación del modelo entrenado

---

## UD4 · Métricas según tipo de problema

| Problema | Métricas principales |
|---|---|
| **Clasificación binaria** | Accuracy, Precision, Recall, F1-score, AUC-ROC |
| **Clasificación multiclase** | Macro/micro F1, matriz de confusión, Cohen's Kappa |
| **Regresión** | MSE, RMSE, MAE, R² (coeficiente de determinación) |
| **Clustering** | Silhouette score, Davies-Bouldin, Calinski-Harabasz |

> **Regla clave:** la métrica elegida debe alinearse con el objetivo de negocio, no solo con la estadística.

---

## UD4 · Visualización e interpretabilidad (XAI)

**Visualización de resultados:**
- **Matriz de confusión:** errores por clase y distribución de predicciones
- **Curva ROC / PR:** equilibrio entre tasa de verdaderos y falsos positivos
- **Curvas de aprendizaje:** evolución de pérdida y métricas por época

**Interpretabilidad del modelo (XAI):**

| Técnica | Uso |
|---|---|
| **SHAP** | Contribución de cada variable a la predicción |
| **LIME** | Explicaciones locales para una instancia concreta |
| **Grad-CAM** | Zonas activadas en modelos de visión |

---

<!-- _class: lead -->

# UD5
## Versionado y ficha técnica del modelo

---

## UD5 · Guardado y versionado del modelo

**Formatos estándar de serialización:**

| Framework | Formato recomendado | Portabilidad |
|---|---|---|
| Scikit-learn | `joblib`, `pickle` | Python |
| PyTorch | `state_dict` + `.pt` | Python / C++ |
| TensorFlow | `SavedModel` | Multi-plataforma |
| Cualquiera | **ONNX** | Universal (producción) |

**Trazabilidad del versionado:**
- Vincular versión del modelo con versión del dataset y del código
- Herramientas: MLflow Model Registry · DVC · BentoML

---

## UD5 · Ficha técnica del modelo (*Model Card*)

**Campos obligatorios de la *model card*:**

- **Descripción:** qué hace el modelo y para qué contexto
- **Métricas:** resultados en test con su intervalo de confianza
- **Datos de entrenamiento:** conjunto, versión, limitaciones conocidas
- **Limitaciones:** casos en los que el modelo no es fiable
- **Sesgos conocidos:** colectivos o escenarios subrepresentados
- **Casos de uso adecuados e inadecuados**
- **Responsable técnico y fecha de creación**

---

<!-- _class: lead -->

# UD6
## Trabajo responsable, sostenible y PRL

---

## UD6 · Responsabilidad ética en el entrenamiento

**Principios a aplicar:**
- Autonomía y responsabilidad ética en las decisiones de diseño
- Adaptabilidad ante cambios de datos, requisitos o resultados
- Comunicación eficaz entre perfiles técnicos y no técnicos

**Sostenibilidad en el entrenamiento:**
- Seleccionar arquitecturas que reducen consumo energético
- Evitar duplicidad de experimentos mediante registro y versionado
- Economía circular de datos y algoritmos: reutilizar experimentos anteriores
- Cuantizar o reducir el modelo antes de desplegar en producción

---

## UD6 · Prevención de riesgos laborales

| Riesgo | Medida preventiva |
|---|---|
| Tecnoestrés | Límites de horario, rutinas de descanso, desconexión digital |
| Fatiga cognitiva | Documentar decisiones para no recomenzar desde cero |
| Ergonomía postural | Silla y escritorio ajustables, pantalla a la altura de los ojos |
| Ambiental | Temperatura, ventilación y ruido adecuados |

**Actuación ante emergencias:**
- Plan de emergencias del centro: conocer rutas de evacuación
- Extintores adecuados para equipos eléctricos
- Protocolo de parada segura de sistemas en ejecución

---

## Criterios de evaluación — MP02

- Determina el paradigma adecuado al problema y justifica la familia de modelos
- Selecciona arquitectura y función de pérdida coherentes con el problema
- Prepara un entorno de entrenamiento reproducible
- Ejecuta búsquedas de hiperparámetros y aplica técnicas de mejora
- Calcula métricas pertinentes e interpreta el comportamiento del modelo
- Guarda y versiona el modelo en formato estándar
- Elabora la ficha técnica (*model card*) completa
- Reduce el coste computacional y evita duplicidad de experimentos

---

<!-- _class: lead -->

# MP02 · Entrenamiento de modelos de aprendizaje automático

**190 h · Curso 1.º · ECP2493_3 · Nivel 3**

*CFS — Gestión de datos y entrenamiento IA (IAD)*
