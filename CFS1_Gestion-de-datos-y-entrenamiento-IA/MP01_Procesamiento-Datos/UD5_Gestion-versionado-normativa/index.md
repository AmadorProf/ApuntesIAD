---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD5 · Gestión, versionado y cumplimiento normativo | MP01 · Procesamiento de datos para IA'
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

# UD5 · Gestión, versionado y cumplimiento normativo

**MP01 · Procesamiento de datos para IA**
CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de aprendizaje

Al finalizar esta unidad el alumno será capaz de:

- Elaborar la documentación completa de un conjunto de datos para proyectos de IA
- Versionar conjuntos de datos y procesos de preprocesamiento garantizando la trazabilidad
- Aplicar controles de seguridad y protección de datos adaptados al RGPD
- Implementar técnicas de anonimización y seudonimización de datos personales
- Garantizar la reproducibilidad de los pipelines de datos mediante procedimientos documentados
- Relacionar versiones de datos, transformaciones y modelos en un sistema de linaje de datos
- Conservar y actualizar la documentación técnica del conjunto a lo largo del ciclo de vida del proyecto

---

## Por qué la gestión de datasets es una disciplina en sí misma

```
Problema frecuente en equipos de IA sin gestión de datos:

"El modelo que entrenamos hace 3 meses daba un F1 de 0.87.
 Ahora, con los mismos datos, obtenemos 0.71.
 ¿Qué cambió?"

Preguntas que no se pueden responder sin gestión:
├── ¿Qué versión del dataset se usó en ese entrenamiento?
├── ¿Qué transformaciones se aplicaron exactamente?
├── ¿Se añadieron o eliminaron registros desde entonces?
├── ¿El scaler que se guardó corresponde a esos datos?
└── ¿La semilla aleatoria de la partición era la misma?

La gestión de datos convierte proyectos irrepetibles
en procesos reproducibles y auditables.
```

---

## Documentación del conjunto: la ficha de datos (Data Card)

### Campos obligatorios de una Data Card profesional

| Sección | Campos que incluye |
|---|---|
| **Identificación** | Nombre, versión, fecha de creación, responsable |
| **Origen** | Fuentes, mecanismos de extracción, fechas de extracción |
| **Finalidad** | Objetivo del modelado, contexto de uso previsto |
| **Estructura** | Variables, tipos, volumetrías, periodo cubierto |
| **Transformaciones** | Pipeline aplicado, parámetros, orden de pasos |
| **Particiones** | Train/val/test, tamaños, estrategia de muestreo |
| **Limitaciones** | Sesgos conocidos, cobertura incompleta, casos de borde |
| **Normativa** | Licencias, RGPD, restricciones de acceso, NDA |
| **Calidad** | Resultados de la verificación de calidad (UD3) |

> El formato Croissant (Google, 2024) y las Data Cards (Google PAIR) son estándares emergentes para la documentación de datasets en ML.

---

## Ejemplo de Data Card en YAML

```yaml
# data_card.yaml — Versión 1.2
nombre: "dataset_credito_v1.2"
version: "1.2.0"
fecha_creacion: "2024-11-15"
responsable: "equipo-datos@entidad.com"

origen:
  fuentes:
    - sistema: "CRM corporativo"
      tabla: "solicitudes_credito"
      rango_fechas: "2021-01-01 / 2024-10-31"
    - sistema: "API Buró de crédito"
      endpoint: "/v2/scoring"
  extraccion_id: "EXT-2024-0047"

estructura:
  registros: 2_450_000
  variables: 38
  target: "impago_90d"
  distribucion_clases: {0: 0.923, 1: 0.077}

limitaciones:
  - "Datos limitados a clientes con historial previo"
  - "Infrarepresentación de menores de 25 años (4.2%)"

normativa:
  licencia: "uso_interno_exclusivo"
  rgpd: true
  pseudonimizado: true
  responsable_tratamiento: "DPO@entidad.com"
```

---

## Versionado de datasets: estrategias

### Por qué versionar datos, no solo código

```
Sin versionado:           Con versionado:
────────────────          ────────────────
dataset.csv               dataset_v1.0.0.parquet  ← extracción inicial
dataset_FINAL.csv         dataset_v1.1.0.parquet  ← corrección outliers
dataset_FINAL_v2.csv      dataset_v1.2.0.parquet  ← nueva fuente añadida
dataset_ok.csv            dataset_v2.0.0.parquet  ← rediseño del esquema
dataset_ok_ESTE.csv
dataset_DEFINITIVO.csv    Cada versión tiene:
                          - Data Card asociada
                          - Script de generación
                          - Hash de integridad
```

**Convención semántica:** MAYOR.MENOR.PARCHE
- MAYOR: cambio de esquema incompatible
- MENOR: nuevos datos o fuentes, estructura compatible
- PARCHE: correcciones de errores sin cambio de esquema

---

## DVC: versionado de datos con Git

DVC (Data Version Control) extiende Git para versionar ficheros de datos grandes.

```bash
# Inicializar DVC en un repositorio Git existente
git init
dvc init

# Añadir el dataset al control de versiones de DVC
dvc add datos/dataset_credito.parquet

# DVC crea un fichero .dvc (texto, versionable con Git)
git add datos/dataset_credito.parquet.dvc .gitignore
git commit -m "feat: añadir dataset crédito v1.0"

# Subir los datos a almacenamiento remoto (S3, GCS, Azure, SSH)
dvc remote add -d s3_remoto s3://mi-bucket/datasets/
dvc push

# Recuperar una versión anterior
git checkout v1.0
dvc pull   # descarga los datos correspondientes a esa versión
```

> Con DVC, la combinación código + datos siempre es reproducible. Cada commit de Git puede recuperar los datos exactos que usó.

---

## Linaje de datos: trazabilidad completa

### Relacionar datos, transformaciones y modelos

```
LINAJE COMPLETO DE UN MODELO:

Extracción EXT-2024-0047
    │
    ├── dataset_raw_v1.0.parquet  [hash: a3f9d...]
    │
    ├── Pipeline preprocesamiento v2.1
    │   ├── imputer: SimpleImputer(strategy=median)
    │   ├── scaler: StandardScaler()
    │   └── encoder: OneHotEncoder(handle_unknown=ignore)
    │
    ├── dataset_procesado_v1.2.parquet  [hash: b7c2e...]
    │   ├── train.parquet  [hash: c4d1f...]
    │   ├── val.parquet    [hash: e5a2b...]
    │   └── test.parquet   [hash: f8b3c...]
    │
    └── modelo_GBT_v3.pkl  [F1=0.872, fecha=2024-11-20]
```

**Herramientas de linaje:** MLflow, DVC + MLflow, Apache Atlas, OpenLineage, AWS SageMaker Lineage.

---

## MLflow para trazabilidad de experimentos

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import GradientBoostingClassifier

mlflow.set_experiment("credito_clasificacion")

with mlflow.start_run(run_name="GBT_v3_dataset_v1.2"):
    # Registrar parámetros del pipeline
    mlflow.log_param("dataset_version", "1.2.0")
    mlflow.log_param("dataset_hash", "b7c2e...")
    mlflow.log_param("pipeline_version", "2.1")
    mlflow.log_param("n_train", len(X_train))
    mlflow.log_param("n_val", len(X_val))
    mlflow.log_param("smote_applied", True)

    # Entrenamiento
    modelo = GradientBoostingClassifier(n_estimators=200)
    modelo.fit(X_train, y_train)

    # Registrar métricas
    mlflow.log_metric("f1_val", 0.872)
    mlflow.log_metric("auc_roc_val", 0.941)

    # Registrar artefactos
    mlflow.sklearn.log_model(modelo, "modelo")
    mlflow.log_artifact("data_card.yaml")
```

---

## Seguridad y protección de datos

### Marco legal aplicable en España y la UE

| Normativa | Ámbito | Obligaciones clave |
|---|---|---|
| **RGPD** (Reglamento UE 2016/679) | Datos personales de ciudadanos UE | Licitud, minimización, portabilidad, derecho al olvido |
| **LOPDGDD** (LO 3/2018) | Adaptación española del RGPD | Delegado de Protección de Datos (DPD/DPO) |
| **Reglamento IA** (UE 2024/1689) | Sistemas de IA de alto riesgo | Gestión de datos, transparencia, supervisión humana |
| **ENS** (Esquema Nacional de Seguridad) | AAPP en España | Medidas de seguridad por nivel (básico/medio/alto) |

**Principios clave del RGPD aplicados a datasets de IA:**
- **Minimización:** solo los datos estrictamente necesarios para la finalidad
- **Limitación de finalidad:** no usar los datos para un propósito distinto al declarado
- **Exactitud:** los datos deben estar actualizados y ser correctos
- **Limitación del plazo de conservación:** no guardar más tiempo del necesario

---

## Anonimización y seudonimización

### Técnicas de protección de datos personales

| Técnica | Descripción | Reversible | Nivel de protección |
|---|---|---|---|
| **Seudonimización** | Sustituir identificadores por códigos sin eliminar la referencia | Si (con tabla maestra) | Moderado |
| **Anonimización** | Eliminar o transformar hasta que la reidentificación sea imposible | No | Alto (deja de ser dato personal) |
| **Generalización** | Reducir la precisión (ej: edad exacta → rango 30-35) | No | Variable |
| **Supresión** | Eliminar campos identificadores | No | Alto |
| **Perturbación / ruido** | Añadir ruido estadístico a valores numéricos | No | Variable |
| **Privacidad diferencial** | Inyección formal de ruido con garantías matemáticas | No | Muy alto |

```python
import hashlib

# Seudonimización: reemplazar DNI por hash irreversible
df["dni_hash"] = df["dni"].apply(
    lambda x: hashlib.sha256((x + "SALT_SECRETO").encode()).hexdigest()
)
df = df.drop("dni", axis=1)  # eliminar el original
```

---

## Control de acceso a los datos

### Modelo RBAC (Role-Based Access Control)

```
Roles y permisos en un proyecto de datos:

Rol              │ Datos brutos │ Datos procesados │ Modelos │ Métricas
─────────────────┼──────────────┼──────────────────┼─────────┼─────────
Científico datos  │ Lectura      │ Lectura/Escritura│ Lectura │ Lectura
Ingeniero datos   │ Escritura    │ Escritura        │ No      │ No
Auditor           │ Lectura      │ Lectura          │ No      │ Lectura
Modelo en prod.   │ No           │ Lectura (test)   │ Lectura │ No
DPO               │ Solo metad.  │ Solo metad.      │ No      │ No
```

**Implementación técnica:**
- Control en el data lake: políticas IAM (AWS) o ACL (Azure ADLS)
- Variables de entorno para credenciales (nunca en código)
- Vault de secretos: HashiCorp Vault, AWS Secrets Manager
- Registro de auditoría de accesos (quién accedió, cuándo, qué)

---

## Reproducibilidad de los procesos de datos

### Los cuatro pilares de la reproducibilidad

```
1. SEMILLAS ALEATORIAS FIJADAS
   random_state=42 en TODOS los pasos estocásticos:
   train_test_split, SMOTE, modelos, GridSearchCV

2. VERSIONES DE LIBRERÍAS REGISTRADAS
   pip freeze > requirements.txt
   conda env export > environment.yml

3. CÓDIGO VERSIONADO EN GIT
   Cada versión del dataset tiene su commit asociado

4. PARAMETROS EXTERNALIZADOS
   No hardcodear valores en el script
   Usar ficheros de configuración (YAML, JSON, .env)
```

```python
# Configuración reproducible en un script de preprocesamiento
import yaml, random, numpy as np

with open("config.yaml") as f:
    config = yaml.safe_load(f)

SEED = config["seed"]  # 42
random.seed(SEED)
np.random.seed(SEED)
```

---

## Script de preprocesamiento reproducible

```python
# preprocesar_datos.py — ejemplo de script parametrizado y reproducible
import yaml, logging, hashlib, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(config_path: str = "config.yaml"):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    logger.info(f"Cargando dataset {cfg['dataset_version']}")
    df = pd.read_parquet(cfg["input_path"])

    X = df[cfg["features"]]
    y = df[cfg["target"]]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=cfg["test_size"],
        stratify=y, random_state=cfg["seed"]
    )

    pipe = Pipeline([("scaler", StandardScaler())])
    X_train_t = pipe.fit_transform(X_train)
    X_test_t  = pipe.transform(X_test)

    joblib.dump(pipe, cfg["pipeline_output"])
    logger.info("Pipeline guardado: " + cfg["pipeline_output"])

if __name__ == "__main__":
    main()
```

---

## Conservación y ciclo de vida del dataset

### Cuánto tiempo conservar y qué hacer al final

| Fase | Acción recomendada |
|---|---|
| **En uso activo** | Versionado completo, acceso controlado, auditoría de accesos |
| **Modelo en producción** | Conservar el dataset de entrenamiento + la Data Card por el periodo de uso del modelo |
| **Modelo retirado** | Evaluar si los datos deben conservarse (auditoría regulatoria) o eliminarse (RGPD) |
| **Datos personales sin uso** | Eliminar o anonimizar según los plazos del RGPD y la política interna |
| **Datos de investigación** | Publicar con licencia abierta en Zenodo, HuggingFace o repositorios científicos |

> El Reglamento de IA (Art. 10-11) exige que los proveedores de IA de alto riesgo conserven la documentación de los datos de entrenamiento durante 10 años.

---

## Actividad práctica — UD5

### Documentación y versionado de un pipeline real

**Escenario:** el equipo ha finalizado el preprocesamiento de un dataset de predicción de churn. Se pide:

1. Redactar la Data Card completa en formato YAML con todos los campos de la plantilla (origen, estructura, transformaciones, particiones, limitaciones, normativa)
2. Diseñar el esquema de versionado semántico del dataset y documentar las diferencias entre la versión 1.0 y la versión 1.1 (suponer que en v1.1 se han corregido 300 registros duplicados)
3. Identificar las variables personales del dataset (nombre, email, DNI, CP) y aplicar seudonimización o supresión según la finalidad del modelado
4. Definir la tabla de control de acceso RBAC para los roles: científico de datos, ingeniero, DPO y auditor
5. Documentar los pasos para garantizar la reproducibilidad del pipeline: semillas, librerías, fichero de configuración

---

## Puntos clave — UD5

- **La documentación del conjunto es un entregable, no un opcional:** la Data Card registra origen, estructura, transformaciones, limitaciones y normativa en un formato estándar y reutilizable
- **El versionado semántico (MAYOR.MENOR.PARCHE) aplica a los datos igual que al software:** cada versión debe ser recuperable con los datos y el script exactos que la produjeron
- **DVC + Git es la herramienta estándar para versionar datos y código juntos:** garantiza que cualquier experimento sea reproducible en cualquier momento
- **El RGPD obliga a minimizar, anonimizar y controlar el acceso desde el diseño:** privacy by design y privacy by default no son opcionales en proyectos con datos de la UE
- **La reproducibilidad requiere semillas, versiones de librerías y configuración externalizada:** un script sin estas garantías no es reproducible aunque el código sea correcto
- **El linaje de datos conecta extracción, preprocesamiento y modelo:** permite auditar decisiones pasadas y cumplir con los requisitos del Reglamento de IA

---

## Criterios de evaluación — UD5

- Documenta el conjunto de datos con todos los campos requeridos en la ficha de datos (Data Card)
- Versiona el conjunto y los procesos de transformación con cambios, parámetros, fechas y responsables
- Establece la relación entre versiones de datos, transformaciones y modelos en el linaje del proyecto
- Aplica medidas de seguridad y protección de datos: restricciones de acceso, minimización, anonimización o seudonimización (RGPD)
- Garantiza la reproducibilidad del proceso mediante semillas fijas, versiones de librerías registradas y configuración externalizada
- Conserva y actualiza la documentación final del conjunto adaptándola al ciclo de vida del proyecto

---

<!-- _class: lead -->

[← Volver a MP01](../)


---

<!-- nav-slide -->

## Navegación

[← UD4 · Preprocesamiento y partición…](../UD4_Preprocesamiento-particion/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD6 · Trabajo responsable, sostenib… →](../UD6_Responsabilidad-sostenibilidad-PRL/)
