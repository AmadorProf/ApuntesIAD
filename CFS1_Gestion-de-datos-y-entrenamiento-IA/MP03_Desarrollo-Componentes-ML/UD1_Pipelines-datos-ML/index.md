---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD1 · Pipelines de datos para ML | MP03 · Desarrollo de componentes para sistemas de ML'
footer: 'Apuntes de IA y Datos'
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

# UD1 · Pipelines de datos para ML

**MP03 · Desarrollo de componentes para sistemas de ML**
Apuntes de IA y Datos

---

## Objetivos de aprendizaje

Al finalizar esta unidad el alumno sera capaz de:

- Configurar entornos de desarrollo locales, en la nube y en Google Colab para proyectos de ML
- Gestionar dependencias con gestores de paquetes y contenedores Docker
- Implementar procesos de ingesta multimodal: tabular, imagen, texto, audio, video y series temporales
- Aplicar tecnicas de anotacion cuando es necesario etiquetar datos
- Ejecutar limpieza, normalizacion y formateo de datasets para frameworks de entrenamiento
- Versionar codigo y colecciones de datos garantizando reproducibilidad y trazabilidad del pipeline
- Generar datasets consistentes y listos para entrenamiento en formatos estandar

---

## Mapa de la unidad

```
UD1 · Pipelines de datos para ML
│
├── 1. Configuracion del entorno
│   ├── Entorno local, Google Colab, nube
│   └── Gestion de dependencias: pip, conda, Docker
│
├── 2. Ingesta multimodal
│   ├── Datos tabulares, imagen, texto, audio, video, series temporales
│   └── Fuentes: ficheros, bases de datos, APIs
│
├── 3. Anotacion multimodal
│   └── Herramientas y flujos de etiquetado
│
├── 4. Limpieza, normalizacion y formateo
│   └── Generacion de datasets para frameworks
│
└── 5. Reproducibilidad y trazabilidad
    └── Versionado de codigo y datos (Git, DVC)
```

---

## Configuracion del entorno: opciones comparadas

| Entorno | Ventajas | Limitaciones | Cuando usarlo |
|---|---|---|---|
| **Local** | Control total, sin latencia, datos sensibles | Hardware limitado, configuracion manual | Desarrollo inicial, datos confidenciales |
| **Google Colab** | GPU gratuita, cero configuracion, colaboracion | Sesiones efimeras, almacenamiento limitado | Prototipado rapido, demos |
| **AWS SageMaker** | Escalabilidad, MLOps integrado, equipos grandes | Coste variable, curva de aprendizaje | Proyectos en produccion |
| **Google Vertex AI** | Integracion BigQuery, AutoML | Dependencia del proveedor | Ecosistema GCP |
| **Azure ML** | Integracion con herramientas Microsoft | Complejidad de configuracion | Entornos corporativos |

> La eleccion del entorno no es permanente: un proyecto puede comenzar en Colab, desarrollarse en local y desplegarse en la nube.

---

## Gestion de dependencias: pip, conda y Docker

### Estrategia por nivel de complejidad

```bash
# Nivel 1: proyecto simple con pip
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Nivel 2: entorno cientifico con conda
conda env create -f environment.yml
conda activate ml-pipeline

# Nivel 3: reproducibilidad total con Docker
docker build -t pipeline-ml:v1.0 .
docker run --gpus all -v $(pwd)/data:/data pipeline-ml:v1.0
```

**Contenido de `environment.yml`:**
```yaml
name: ml-pipeline
channels: [conda-forge, defaults]
dependencies:
  - python=3.11
  - pandas=2.2
  - scikit-learn=1.4
  - pytorch=2.2
  - pip:
    - dvc==3.40
    - mlflow==2.11
```

---

## Dockerfile para entorno de ML reproducible

```dockerfile
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el codigo del pipeline
COPY src/ ./src/
COPY configs/ ./configs/

# Variables de entorno para reproducibilidad
ENV PYTHONHASHSEED=42
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "src/pipeline.py"]
```

> El `Dockerfile` garantiza que cualquier miembro del equipo, en cualquier maquina, ejecute exactamente el mismo entorno.

---

## Ingesta de datos tabulares y series temporales

```python
import pandas as pd
import sqlalchemy as sa

# Desde fichero Parquet (formato recomendado para ML)
df_tabular = pd.read_parquet("data/raw/ventas_2024.parquet")

# Desde base de datos SQL con filtros en origen
engine = sa.create_engine("postgresql://user:pwd@host:5432/db")
df_sql = pd.read_sql("""
    SELECT fecha, producto_id, cantidad, precio
    FROM ventas
    WHERE fecha >= '2024-01-01'
      AND cantidad > 0
""", engine)

# Series temporales con frecuencia regular
df_ts = pd.read_csv(
    "data/raw/sensores.csv",
    parse_dates=["timestamp"],
    index_col="timestamp"
)
# Reindexar para completar gaps temporales
df_ts = df_ts.resample("1h").mean().interpolate(method="time")
print(f"Registros: {len(df_ts):,} | Gaps interpolados: {df_ts.isna().sum().sum()}")
```

---

## Ingesta de datos de imagen y video

```python
from PIL import Image
import torchvision.transforms as T
import cv2
import os

# Carga de imagen individual con validacion
def cargar_imagen(ruta: str, tamano: tuple = (224, 224)) -> Image.Image:
    img = Image.open(ruta).convert("RGB")
    transformacion = T.Compose([
        T.Resize(tamano),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225])
    ])
    return transformacion(img)

# Carga de frames de video
def extraer_frames(ruta_video: str, fps_objetivo: int = 5):
    cap = cv2.VideoCapture(ruta_video)
    fps_original = cap.get(cv2.CAP_PROP_FPS)
    intervalo = int(fps_original / fps_objetivo)
    frames = []
    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % intervalo == 0:
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame_idx += 1
    cap.release()
    return frames
```

---

## Ingesta de datos de texto y audio

```python
import librosa
import numpy as np

# Texto: carga y tokenizacion basica
def cargar_textos(directorio: str) -> list[dict]:
    documentos = []
    for fichero in os.listdir(directorio):
        if fichero.endswith(".txt"):
            with open(f"{directorio}/{fichero}", encoding="utf-8") as f:
                documentos.append({
                    "id": fichero,
                    "texto": f.read().strip()
                })
    return documentos

# Audio: extraccion de caracteristicas MFCC
def procesar_audio(ruta: str, sr: int = 22050, n_mfcc: int = 40):
    y, sr = librosa.load(ruta, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    # Estadisticas sobre el tiempo como caracteristicas
    return {
        "mfcc_mean": mfcc.mean(axis=1),
        "mfcc_std":  mfcc.std(axis=1),
        "duracion":  librosa.get_duration(y=y, sr=sr)
    }
```

| Tipo | Libreria | Formato salida para ML |
|---|---|---|
| Texto crudo | `pathlib`, `chardet` | Lista de strings / DataFrame |
| Audio | `librosa`, `torchaudio` | Array numpy de MFCC / espectrograma |
| Imagen | `Pillow`, `OpenCV` | Tensor float32 normalizado |

---

## Anotacion multimodal: cuando etiquetar es parte del pipeline

El etiquetado manual o semiautomatico es necesario cuando los datos no tienen etiquetas o estas son insuficientes.

### Herramientas de anotacion por tipo de dato

| Tipo de dato | Herramienta | Caracteristica principal |
|---|---|---|
| Imagen (clasificacion, deteccion) | Label Studio | Open source, multi-tarea |
| Imagen (segmentacion) | CVAT | Anotacion de video y poligonos |
| Texto (NER, clasificacion) | Prodigy | Anotacion activa con modelos |
| Audio (transcripcion, eventos) | Audino | Interfaz web, colaborativo |
| Multimodal | Label Studio | Soporta texto, imagen, audio y video |

### Flujo de anotacion profesional

```
Datos brutos → Muestreo estratificado → Guia de anotacion
→ Anotadores (N personas) → Calculo de acuerdo inter-anotador
→ Revision de discordancias → Dataset anotado versionado
```

> El acuerdo inter-anotador (Cohen's Kappa, Krippendorff's Alpha) mide la fiabilidad del etiquetado. Un kappa < 0.6 indica que la guia de anotacion necesita revision.

---

## Limpieza y normalizacion de datos

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def limpiar_dataset(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Eliminar duplicados exactos
    df = df.drop_duplicates()

    # 2. Tratar nulos segun estrategia por columna
    numericas = df.select_dtypes(include=np.number).columns
    df[numericas] = df[numericas].fillna(df[numericas].median())

    categoricas = df.select_dtypes(include="object").columns
    df[categoricas] = df[categoricas].fillna("DESCONOCIDO")

    # 3. Eliminar outliers con IQR
    for col in numericas:
        Q1, Q3 = df[col].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        df = df[df[col].between(Q1 - 3*IQR, Q3 + 3*IQR)]

    return df

def normalizar(df: pd.DataFrame, metodo: str = "standard") -> pd.DataFrame:
    numericas = df.select_dtypes(include=np.number).columns
    scaler = StandardScaler() if metodo == "standard" else MinMaxScaler()
    df[numericas] = scaler.fit_transform(df[numericas])
    return df
```

---

## Generacion de datasets para frameworks de entrenamiento

```python
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split

class DatasetML(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# Particion estratificada
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_train, y_train, test_size=0.15, random_state=42, stratify=y_train
)

train_loader = DataLoader(DatasetML(X_train, y_train), batch_size=64, shuffle=True)
val_loader   = DataLoader(DatasetML(X_val,   y_val),   batch_size=64, shuffle=False)
test_loader  = DataLoader(DatasetML(X_test,  y_test),  batch_size=64, shuffle=False)

print(f"Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
```

---

## Reproducibilidad y trazabilidad: versionado de codigo

```bash
# Estructura de proyecto reproducible
proyecto-ml/
├── data/           # gestionado por DVC, no por Git
├── src/
│   ├── ingesta.py
│   ├── preprocesado.py
│   └── pipeline.py
├── configs/
│   └── pipeline_v1.yaml  # parametros versionados
├── tests/
├── .dvc/           # configuracion DVC
├── requirements.txt
└── README.md

# Inicializar y versionar
git init && git add src/ configs/ requirements.txt
git commit -m "feat: pipeline inicial de ingesta multimodal"
git tag v1.0.0
```

**Convencion de commits para pipelines:**
```
feat: nueva etapa de ingesta de audio
fix: corregir normalizacion con valores nulos
refactor: extraer clase DatasetML a modulo separado
chore: actualizar dependencias a versiones LTS
```

---

## Versionado de datos con DVC

```bash
# Inicializar DVC en el repositorio
dvc init
git add .dvc/ .gitignore && git commit -m "chore: inicializar DVC"

# Configurar almacenamiento remoto (S3, GCS, Azure, local)
dvc remote add -d storage s3://bucket-ml/datos
dvc remote modify storage endpointurl https://s3.amazonaws.com

# Registrar y versionar un dataset
dvc add data/raw/dataset_v1.parquet
git add data/raw/dataset_v1.parquet.dvc .gitignore
git commit -m "data: dataset inicial v1 - 50k registros"
dvc push

# Reproducir cualquier version anterior
git checkout v1.0.0
dvc pull
```

> DVC almacena un fichero `.dvc` ligero en Git (hash + metadatos) y el binario en el almacenamiento remoto. Esto permite versionar datasets de cientos de GB sin saturar el repositorio.

---

## Parametros y configuracion del pipeline

```yaml
# configs/pipeline_v1.yaml
pipeline:
  version: "1.0.0"
  random_seed: 42

ingesta:
  fuente: "postgresql://prod/lecturas"
  tabla: "sensores_industriales"
  filtro_fecha_inicio: "2024-01-01"
  columnas: ["timestamp", "temperatura", "presion", "vibracion"]

preprocesado:
  normalizacion: "standard"
  estrategia_nulos: "mediana"
  umbral_outliers_iqr: 3.0

particion:
  test_size: 0.20
  val_size: 0.15
  stratify: true

salida:
  formato: "parquet"
  directorio: "data/processed/"
  nombre: "dataset_entrenamiento_v1"
```

```python
import yaml

with open("configs/pipeline_v1.yaml") as f:
    cfg = yaml.safe_load(f)

semilla = cfg["pipeline"]["random_seed"]
```

---

## Actividad practica — UD1

### Pipeline completo de ingesta multimodal

**Escenario:** una empresa de mantenimiento predictivo quiere entrenar un modelo con tres fuentes de datos:
- Lecturas de sensores de temperatura y vibracion en una base de datos SQL (datos tabulares)
- Imagenes de camaras de inspeccion visual de maquinaria (datos de imagen)
- Informes de mantenimiento en texto libre (datos de texto)

**Tareas:**
1. Configurar un entorno reproducible con `environment.yml` y `Dockerfile`
2. Implementar tres funciones de ingesta (una por tipo de dato)
3. Aplicar limpieza y normalizacion a los datos tabulares
4. Generar un `DataLoader` de PyTorch con las particiones train/val/test
5. Versionar el pipeline con Git y los datasets con DVC
6. Registrar los metadatos de cada fuente en un fichero `pipeline_metadata.json`

**Entregable:** repositorio Git con pipeline funcional, `environment.yml`, `Dockerfile` y `pipeline_metadata.json`.

---

## Puntos clave — UD1

- El entorno de desarrollo debe ser reproducible desde el primer dia: `environment.yml` o `Dockerfile` no son opcionales
- La ingesta multimodal requiere librerias especializadas por tipo de dato: `pandas` para tabular, `librosa` para audio, `PIL`/`OpenCV` para imagen
- La anotacion es parte del pipeline cuando los datos no tienen etiquetas fiables: debe versionarse junto con los datos
- La limpieza y normalizacion deben aplicarse de forma consistente entre entrenamiento, validacion y test para evitar fugas de informacion
- La particion estratificada garantiza que todas las clases esten representadas en proporciones similares en cada subconjunto
- DVC gestiona el versionado de datos de forma paralela a Git para el codigo: ambos son complementarios e imprescindibles
- Los parametros del pipeline deben externalizarse en ficheros YAML para facilitar la reproducibilidad y la experimentacion controlada

---

## Criterios de evaluacion — UD1

- Implementa procesos de ingesta multimodal cubriendo al menos tres tipos de dato distintos
- Genera datasets consistentes y sin contaminacion entre particiones de entrenamiento y test
- Versiona el pipeline con Git usando mensajes de commit descriptivos y etiquetas de version
- Versiona los conjuntos de datos con DVC y los registra en un almacenamiento remoto
- Documenta los parametros del pipeline en ficheros de configuracion versionados
- Registra los metadatos minimos de cada fuente de datos para garantizar la trazabilidad

---

<!-- _class: lead -->

[← Volver a MP03](../)


---

<!-- nav-slide -->

## Navegación

[Volver al módulo](../) &nbsp;·&nbsp; [UD2 · Despliegue de modelos con fra… →](../UD2_Despliegue-modelos-frameworks/)
