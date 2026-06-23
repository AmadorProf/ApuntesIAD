---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD5 · Versionado y ficha técnica del modelo | MP02 · Entrenamiento de modelos de aprendizaje automático'
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

# UD5 · Versionado y ficha técnica del modelo

**MP02 · Entrenamiento de modelos de aprendizaje automático**

CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Guardar un modelo entrenado en el formato estándar adecuado a su framework
- Comprender las diferencias entre formatos de serialización y elegir según el entorno de despliegue
- Implementar un sistema de versionado del modelo vinculado al dataset y al código
- Garantizar la trazabilidad y la reproducibilidad del proceso completo
- Elaborar una ficha técnica (*model card*) completa con todos los campos obligatorios
- Registrar el modelo en un repositorio de modelos con MLflow Model Registry

---

## Guardado del modelo — Concepto y por qué importa

**Serializar** un modelo significa convertirlo a un formato que pueda almacenarse en disco y recargarse posteriormente para inferencia o continuar el entrenamiento. Sin un guardado correcto, el trabajo de entrenamiento se pierde al cerrar el proceso.

**Requisitos de un guardado profesional:**
- Portabilidad: el modelo puede cargarse en otra máquina o entorno
- Compatibilidad: el formato es compatible con el entorno de despliegue (API, móvil, edge...)
- Completitud: incluye arquitectura, pesos, configuración del preprocesador y metadatos
- Trazabilidad: el archivo guardado está vinculado a la versión del código y los datos que lo generaron

---

## Formatos de serialización — Tabla comparativa

| Framework | Formato recomendado | Extensión | Portabilidad | Incluye arquitectura |
|---|---|---|---|---|
| Scikit-learn | joblib | `.joblib` | Python | Sí (objeto completo) |
| Scikit-learn (alternativo) | pickle | `.pkl` | Python | Sí (objeto completo) |
| PyTorch (solo pesos) | state_dict | `.pt` / `.pth` | Python | No (requiere código) |
| PyTorch (completo) | TorchScript | `.pt` | Python + C++ | Sí |
| TensorFlow | SavedModel | directorio | Multi-plataforma | Sí |
| Cualquier framework | ONNX | `.onnx` | Universal | Sí |
| Keras | Keras native | `.keras` | Python | Sí |

---

## Guardado con Scikit-learn

```python
import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from datetime import datetime

# El pipeline completo incluye el preprocesador y el modelo
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", GradientBoostingClassifier(**mejores_params))
])
pipeline.fit(X_train, y_train)

# Guardar con joblib (recomendado para arrays numpy grandes)
ruta_modelo = f"modelos/toxicidad_v1.0_{datetime.now().strftime('%Y%m%d')}.joblib"
joblib.dump(pipeline, ruta_modelo)
print(f"Modelo guardado en: {ruta_modelo}")

# Cargar y verificar
pipeline_cargado = joblib.load(ruta_modelo)
assert pipeline_cargado.score(X_test, y_test) == pipeline.score(X_test, y_test)
print("Verificacion de carga: OK")
```

---

## Guardado con PyTorch — state_dict y TorchScript

```python
import torch

# Opcion 1: Guardar solo los pesos (state_dict)
# Requiere tener la definicion de la clase disponible al cargar
torch.save(modelo.state_dict(), "modelos/bert_toxicidad_v1.0_pesos.pt")

# Cargar state_dict
modelo_cargado = BertClasificador(num_clases=2)
modelo_cargado.load_state_dict(torch.load("modelos/bert_toxicidad_v1.0_pesos.pt"))
modelo_cargado.eval()

# Opcion 2: TorchScript (no requiere codigo de la clase al cargar)
modelo_script = torch.jit.script(modelo)
modelo_script.save("modelos/bert_toxicidad_v1.0_script.pt")

modelo_script_cargado = torch.jit.load("modelos/bert_toxicidad_v1.0_script.pt")

# Opcion 3: Exportar a ONNX (para despliegue universal)
dummy_input = torch.zeros(1, 128, dtype=torch.long)
torch.onnx.export(modelo, dummy_input, "modelos/bert_toxicidad_v1.0.onnx",
                  input_names=["input_ids"], output_names=["logits"])
```

---

## Exportación a ONNX — Para despliegue universal

**ONNX** (*Open Neural Network Exchange*) es el formato estándar abierto para exportar modelos entre frameworks y entornos de producción. Es el formato recomendado para producción cuando el entorno de inferencia no es Python.

```
Entrenamiento                Despliegue
─────────────                ──────────
PyTorch  ─┐                  REST API (Python)
TF/Keras ─┼→ Modelo ONNX →  TensorRT (NVIDIA GPU)
Sklearn  ─┘                  ONNX Runtime (CPU/Edge)
                              .NET / Java / C++
                              iOS / Android (CoreML)
```

```python
# Verificar y optimizar modelo ONNX
import onnx
import onnxruntime as ort

modelo_onnx = onnx.load("modelos/toxicidad_v1.0.onnx")
onnx.checker.check_model(modelo_onnx)

# Ejecutar inferencia con ONNX Runtime
session = ort.InferenceSession("modelos/toxicidad_v1.0.onnx")
resultado = session.run(None, {"input": X_test_numpy})
```

---

## Versionado del modelo — Concepto y sistema

El **versionado** garantiza que cada modelo puede reproducirse exactamente y rastrearse hasta su origen (código, datos, configuración). Sin versionado, dos experimentos con el mismo nombre pueden producir modelos completamente diferentes.

**Convención de versiones semánticas para modelos:**

```
v{major}.{minor}.{patch}

v1.0.0  → Primera versión en producción
v1.1.0  → Misma arquitectura, nuevo dataset o hiperparámetros ajustados
v1.1.1  → Corrección de bug en el preprocesamiento
v2.0.0  → Cambio de arquitectura o paradigma de entrenamiento
```

**Qué vincular a cada versión:**
- Hash del commit del código de entrenamiento (Git)
- Versión del dataset (DVC tag o hash del archivo)
- Archivo de configuración del experimento (JSON/YAML)
- Métricas de evaluación en el conjunto de test

---

## Versionado con MLflow Model Registry

```python
import mlflow
import mlflow.sklearn

# Configurar servidor MLflow
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("clasificador-toxicidad")

with mlflow.start_run(run_name="v1.0.0") as run:
    # Registrar parametros e hiperparametros
    mlflow.log_params(config_experimento)

    # Registrar metricas
    mlflow.log_metrics({"f1_test": 0.82, "auc_roc": 0.91, "accuracy": 0.88})

    # Guardar el modelo con firma
    firma = mlflow.models.infer_signature(X_train, pipeline.predict(X_train))
    mlflow.sklearn.log_model(
        pipeline, "modelo",
        signature=firma,
        registered_model_name="clasificador-toxicidad"
    )

    # Transicionar a produccion cuando se valida
    cliente = mlflow.tracking.MlflowClient()
    cliente.transition_model_version_stage(
        name="clasificador-toxicidad", version=1, stage="Production"
    )
```

---

## Trazabilidad completa — Diagrama

```
Dataset v2.1 (DVC hash: a3f9...)
         |
         v
Código entrenamiento (Git commit: 7b2c4a1)
         |
    Config v1.0.0 (JSON: lr=2e-5, bs=32, seed=42)
         |
         v
Modelo entrenado  →  MLflow run_id: abc123
         |           Métricas: F1=0.82, AUC=0.91
         v
  Modelo registrado: clasificador-toxicidad v1
         |
         v
  Producción (stage: Production)
         |
         v
  Inferencia API  →  Input/Output logged
```

---

## Ficha técnica del modelo — Concepto (Model Card)

Las **fichas técnicas de modelos** (*Model Cards*) fueron propuestas por Google en 2019 como estándar de transparencia. Son el documento oficial que acompaña a cada modelo publicado o desplegado, sirviendo a equipos técnicos, responsables de producto, auditores y reguladores.

**Por qué es obligatoria en contextos profesionales:**
- El Reglamento de IA de la UE exige documentación técnica para sistemas de alto riesgo
- Permite a los usuarios del modelo conocer sus limitaciones antes de aplicarlo
- Facilita la detección de sesgos y la rendición de cuentas
- Es la base de la auditoría de sistemas de IA

---

## Ficha técnica — Campos obligatorios (1/2)

| Sección | Contenido mínimo |
|---|---|
| **Identificación** | Nombre, versión, fecha, responsable técnico, organización |
| **Descripción** | Qué hace el modelo, dominio de aplicación, tarea (clasificación/regresión/...) |
| **Arquitectura** | Familia de modelo, framework, número de parámetros, tipo de entrada/salida |
| **Datos de entrenamiento** | Dataset usado, versión, tamaño, origen, periodo temporal |
| **Preprocesamiento** | Pipeline de transformación aplicado al entrenamiento |
| **Partición de datos** | Proporciones train/val/test, criterio de división |

---

## Ficha técnica — Campos obligatorios (2/2)

| Sección | Contenido mínimo |
|---|---|
| **Métricas de evaluación** | Métricas en test con valor numérico e intervalo de confianza si aplica |
| **Limitaciones conocidas** | En qué contextos el modelo no es fiable o no debe usarse |
| **Sesgos detectados** | Grupos subrepresentados, variables sensibles, disparidad de rendimiento por subgrupo |
| **Casos de uso adecuados** | Para qué aplicaciones se ha validado el modelo |
| **Casos de uso NO adecuados** | Usos expresamente desaconsejados |
| **Versión y trazabilidad** | Git commit, hash de dataset, run_id de MLflow |

---

## Ficha técnica — Ejemplo real

```markdown
# Ficha técnica: Clasificador de Texto Tóxico v1.0.0

## Identificación
- Responsable: Equipo IA — CFS IAD 2026
- Fecha: 2026-06-23 | Versión: 1.0.0

## Descripción
Clasifica comentarios en texto libre como tóxicos o no tóxicos.
Diseñado para plataformas educativas en español de España.

## Métricas en test
- Accuracy: 0.88 | F1: 0.82 | AUC-ROC: 0.91
- F1 en subgrupo "lenguaje informal": 0.71 (rendimiento reducido)

## Limitaciones
- No fiable con ironía, sarcasmo o lenguaje en clave
- Entrenado solo con español peninsular; variantes latinoamericanas no validadas
- Máximo 512 tokens por comentario

## Casos de uso NO adecuados
- Decisiones automáticas sin supervisión humana en procesos disciplinarios
- Moderación de contenido en contextos médicos o legales
```

---

## Actividad práctica — UD5

**Contexto:** El clasificador de toxicidad ha alcanzado las métricas requeridas. Es el momento de formalizarlo como un artefacto versionado y documentado.

**Tareas:**

1. Guarda el modelo en dos formatos: `joblib` (si es sklearn) o `state_dict` + ONNX (si es PyTorch). Verifica que la carga produce el mismo resultado
2. Define la convención de versión para este modelo y justifica si es v1.0.0 o una versión menor
3. Configura un experimento en MLflow que registre parámetros, métricas y el modelo con firma de entrada/salida
4. Elabora la ficha técnica completa del modelo en Markdown con todas las secciones de las tablas anteriores
5. Describe el flujo de trazabilidad completo: desde el dataset hasta el modelo en producción, con todos los identificadores vinculados

---

## Puntos clave — UD5

- ONNX es el formato de facto para despliegue multi-plataforma: si el entorno de producción no es Python, exportar siempre a ONNX
- `joblib` es superior a `pickle` para modelos de scikit-learn porque gestiona mejor los arrays de NumPy de gran tamaño
- El versionado semántico del modelo debe vincularse siempre al commit de código y al hash del dataset, no solo a un número incremental
- MLflow Model Registry permite transicionar modelos entre etapas (Staging → Production → Archived) con trazabilidad completa
- La ficha técnica (*model card*) es un documento de responsabilidad: las limitaciones y sesgos deben declararse explícitamente, no omitirse
- La trazabilidad completa (dataset → código → configuración → modelo → despliegue) es el estándar mínimo para sistemas de IA en producción

---

## Criterios de evaluación — UD5

| Criterio | Indicador de logro |
|---|---|
| Guarda el modelo en formato estándar | Serializa correctamente con el formato adecuado al framework y el entorno de despliegue |
| Versiona el modelo | Aplica convención semántica y vincula versión a código, dataset y configuración |
| Garantiza trazabilidad | El modelo puede reproducirse exactamente a partir de los artefactos registrados |
| Registra en MLflow | Configura experiment, log de parámetros, métricas y modelo con firma |
| Elabora la ficha técnica completa | Cubre todas las secciones obligatorias incluyendo limitaciones y sesgos |
