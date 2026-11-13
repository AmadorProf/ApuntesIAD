---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD4 · Visión artificial sobre imágenes y vídeo | MP03 · Explotación de servicios de datos y analítica'
footer: 'Apuntes de IA y Datos'
---

<style>
section { font-family: 'Segoe UI', Arial, sans-serif; }
h1 { color: #1e3a5f; }
h2 { color: #1e3a5f; border-bottom: 2px solid #10b981; padding-bottom: 6px; }
h3 { color: #059669; }
table { font-size: 0.82em; width: 100%; }
ul, ol { font-size: 0.88em; }
blockquote { border-left: 4px solid #10b981; background: #ecfdf5; padding: 8px 16px; border-radius: 4px; }
footer, header { font-size: 0.6em; color: #6b7280; }
section.lead h1 { font-size: 2em; text-align: center; margin-top: 80px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
pre { background: #1e293b; color: #e2e8f0; padding: 16px; border-radius: 8px; font-size: 0.8em; }
</style>

<!-- _class: lead -->

# UD4 · Visión artificial sobre imágenes y vídeo

**MP03 — Explotación de servicios de datos y analítica**
Apuntes de IA y Datos

---

## Objetivos de la unidad

Al finalizar esta unidad el alumnado será capaz de:

- Adquirir y preprocesar imágenes y vídeos desde distintas fuentes (bases de datos, streaming de cámara).
- Anotar datasets visuales para tareas de clasificación, detección y segmentación.
- Configurar y ejecutar experimentos con modelos CNN, ViT y YOLO.
- Desplegar el modelo de visión e integrarlo con APIs, cámaras y dispositivos.
- Tratar los datos visuales según la normativa de protección de datos y propiedad intelectual.

> **Resultado de aprendizaje:** Procesa secuencias de imágenes o vídeos con las herramientas de visión artificial para obtener información sobre su contenido.

---

## Contexto: tareas de visión artificial

### Principales tareas

| Tarea | Descripción | Ejemplo |
|---|---|---|
| **Clasificación** | Asignar una etiqueta a la imagen completa | Defecto / Sin defecto en fabricación |
| **Detección de objetos** | Localizar y clasificar objetos con bounding box | Detección de peatones en vídeo de tráfico |
| **Segmentación semántica** | Clasificar cada píxel | Mapa de carreteras en conducción autónoma |
| **Segmentación de instancias** | Separar instancias individuales de cada clase | Conteo de piezas en cadena de montaje |
| **Estimación de pose** | Detectar puntos clave del cuerpo | Análisis ergonómico en puestos de trabajo |
| **Reconocimiento facial** | Identificar personas por el rostro | Control de acceso (sujeto a restricciones RGPD) |

---

## Adquisición de datos visuales

### Fuentes de imágenes

| Fuente | Formato | Mecanismo de acceso |
|---|---|---|
| Base de datos interna | JPEG, PNG | Conector de base de datos o acceso a blob/bucket |
| Dataset público | JPEG, PNG, Parquet | Descarga directa, Hugging Face Datasets, Kaggle |
| API de imágenes | JPEG, Base64 | HTTP GET con autenticación |
| Cámara IP (fotos) | JPEG | HTTP snapshot endpoint |
| Scanner industrial | TIFF | SDK del fabricante |

### Fuentes de vídeo

| Fuente | Formato | Protocolo |
|---|---|---|
| Cámara IP / CCTV | H.264, H.265 | RTSP, ONVIF |
| Cámara web / USB | MJPEG, H.264 | OpenCV VideoCapture |
| Vídeo pregrabado | MP4, AVI, MKV | Fichero local o blob/bucket |
| Stream de plataforma | HLS, DASH | FFmpeg, GStreamer |

---

## Preprocesamiento — Decodificación y homogeneización

### Decodificación

Convertir el formato de almacenamiento (JPEG, PNG, H.264) en arrays numéricos que el modelo puede procesar.

```python
# OpenCV: leer imagen y convertir a RGB
import cv2
img_bgr = cv2.imread("imagen.jpg")
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

# Extraer fotogramas de un vídeo
cap = cv2.VideoCapture("video.mp4")
ret, frame = cap.read()  # frame: array (H, W, 3)
```

### Homogeneización

Los modelos de visión artificial requieren imágenes de tamaño fijo.

| Operación | Descripción | Valor típico |
|---|---|---|
| Redimensionado | Cambiar resolución al tamaño de entrada del modelo | 224x224, 640x640 |
| Normalización de píxeles | Escalar valores [0,255] a [0,1] o media-varianza ImageNet | µ=[0.485,0.456,0.406] |
| Conversión de canal | RGB / BGR / Escala de grises según el modelo | Depende del framework |

---

## Preprocesamiento — Segmentación de vídeo y anotación

### Segmentación de vídeo

Un vídeo se divide en unidades procesables:

- **Fotograma a fotograma (frame-by-frame):** útil para detección en tiempo real.
- **Clips de longitud fija:** para modelos de acción temporal (p. ej., clips de 16 o 32 fotogramas).
- **Submuestreo:** procesar 1 de cada N fotogramas para reducir la carga computacional.

### Anotación de datasets

| Tipo de tarea | Tipo de anotación | Herramienta |
|---|---|---|
| Clasificación | Etiqueta por imagen | LabelImg, Roboflow, CVAT |
| Detección | Bounding box + clase | CVAT, Label Studio, Roboflow |
| Segmentación semántica | Máscara por clase | CVAT, Supervisely |
| Segmentación de instancias | Polígono por instancia | CVAT, Scale AI |

> La calidad de la anotación es el factor más determinante en el rendimiento de un modelo de visión.

---

## Data augmentation

La **data augmentation** aumenta artificialmente el tamaño y diversidad del dataset aplicando transformaciones a las imágenes de entrenamiento.

### Transformaciones habituales

| Transformación | Descripción | Implementación |
|---|---|---|
| Rotación | Girar la imagen un ángulo aleatorio | `torchvision.transforms.RandomRotation` |
| Volteo horizontal/vertical | Espejo de la imagen | `RandomHorizontalFlip` |
| Recorte aleatorio | Extraer subregión aleatoria | `RandomCrop` |
| Cambio de brillo/contraste | Variar la iluminación | `ColorJitter` |
| Ruido gaussiano | Añadir ruido a los píxeles | `albumentations.GaussNoise` |
| Mixup / CutMix | Combinar dos imágenes | Técnicas avanzadas para clasificación |

> La augmentation debe ser coherente con el dominio: no tiene sentido voltear verticalmente imágenes de personas caminando.

---

## Modelos de visión artificial

### CNN — Redes Neuronales Convolucionales

- Arquitectura dominante hasta 2021. Bloques convolucionales con kernels aprenden patrones locales.
- Ejemplos: ResNet-50, EfficientNet, MobileNet (ligero para edge).
- Adecuado para clasificación, detección (con cabezas adicionales) y datasets de tamaño medio.

### ViT — Vision Transformer

- Divide la imagen en parches y los procesa con un mecanismo de atención (Transformer).
- Mejor rendimiento en datasets grandes; requiere más datos para generalizar.
- Ejemplos: ViT-B/16, DeiT, Swin Transformer.

### YOLO — You Only Look Once

- Modelo de detección de objetos en tiempo real de una sola pasada.
- Estado del arte en velocidad/precisión para detección.
- Versiones: YOLOv5, YOLOv8, YOLOv9, YOLO-World (detección abierta).

---

## Configuración del experimento de visión

### Hiperparámetros principales

| Hiperparámetro | Descripción | Ejemplo |
|---|---|---|
| **Arquitectura** | Modelo base | YOLOv8n, ResNet-50, ViT-B/16 |
| **Tamaño de kernel** | Filtro convolucional (solo CNN) | 3x3, 5x5 |
| **Tamaño de lote** | Imágenes por actualización | 16, 32, 64 |
| **Épocas / Iteraciones** | Veces que el modelo ve el dataset | 50, 100, 300 |
| **Learning rate** | Paso de actualización del gradiente | 0.001, 0.0001 |
| **Transfer learning** | Inicializar con pesos preentrenados | ImageNet, COCO |
| **Data augmentation** | Transformaciones aplicadas | Volteo, rotación, recorte |

### Transfer learning (recomendado)

Partir de un modelo preentrenado en ImageNet o COCO reduce drásticamente el tiempo y datos necesarios.

---

## Métricas de evaluación en visión artificial

### Clasificación de imágenes

| Métrica | Descripción |
|---|---|
| **Accuracy** | Porcentaje de imágenes clasificadas correctamente |
| **F1-score por clase** | Especialmente relevante con clases desbalanceadas |
| **Matriz de confusión** | Distribución de errores por clase |
| **Top-5 Accuracy** | La clase correcta está entre las 5 más probables |

### Detección de objetos

| Métrica | Descripción |
|---|---|
| **mAP@50** | Mean Average Precision con IoU ≥ 0.50 |
| **mAP@50:95** | mAP promediado con umbrales de IoU de 0.50 a 0.95 |
| **Precision / Recall** | Por clase y global |
| **Latencia de inferencia** | Tiempo por imagen (ms); crítico en tiempo real |

---

## Despliegue del modelo de visión

### Escenarios de despliegue

| Escenario | Integración | Tecnología |
|---|---|---|
| **API de imágenes** | REST endpoint; recibe imagen en Base64 o multipart | FastAPI, Azure Custom Vision, Vertex AI |
| **Cámara IP en tiempo real** | Leer stream RTSP; inferencia por fotograma | OpenCV + modelo TensorRT / ONNX |
| **Proceso batch** | Pipeline sobre directorio de imágenes o bucket | Azure ML Pipeline, Vertex AI Batch Prediction |
| **Dispositivo embebido** | Modelo optimizado para hardware limitado | TensorFlow Lite, ONNX Runtime, OpenVINO |
| **Navegador web** | Inferencia en el cliente | TensorFlow.js, ONNX Runtime Web |

### Optimización para producción

- **Cuantización:** reducir precisión de float32 a int8 (reducción 4x en tamaño, 2-4x en velocidad).
- **Pruning:** eliminar conexiones con bajo peso.
- **ONNX:** formato universal para interoperabilidad entre frameworks.
- **TensorRT:** optimizador de inferencia de NVIDIA para GPU.

---

## Protección de datos y privacidad en visión artificial

Las imágenes y vídeos frecuentemente contienen **datos personales** (caras, matrículas, comportamientos identificables).

### Obligaciones normativas

| Normativa | Obligación clave |
|---|---|
| **RGPD (Art. 9)** | Las imágenes de personas son datos biométricos; requieren base legal explícita |
| **Ley Orgánica 3/2018 (LOPDGDD)** | Aplicación española del RGPD; videovigilancia regulada por normativa AEPD |
| **Reglamento de IA de la UE** | Los sistemas de reconocimiento facial en espacios públicos son de alto riesgo |

### Medidas técnicas

- **Anonimización:** difuminado (blur) de caras y matrículas antes de almacenar o publicar.
- **Seudonimización:** reemplazar identidades por identificadores no reversibles.
- **Control de acceso:** solo el personal autorizado accede a las imágenes con datos personales.
- **Seguridad del stream:** cifrado TLS en transmisión; RTSP cifrado (RTSPS).
- **Minimización:** no almacenar más imágenes de las necesarias; definir política de retención.

---

## Propiedad intelectual en datasets de imágenes

### Consideraciones de licencia

| Tipo de dataset | Uso en producción |
|---|---|
| **Creative Commons (CC0, CC-BY)** | Uso libre; CC-BY requiere atribución |
| **Dataset de investigación (non-commercial)** | Solo para investigación; no en productos comerciales |
| **Dataset propietario** | Requiere licencia comercial específica |
| **Web scraping** | Depende de los ToS del sitio y del RGPD; riesgo legal |

### Regla práctica

> Antes de usar cualquier dataset de imágenes en un producto, verificar la licencia y documentarla en el registro de activos de datos del proyecto.

---

## Actividad práctica — UD4

### "Detección de equipos de protección individual (EPI) en planta industrial"

**Escenario:** La empresa FabriTech S.L. quiere automatizar la verificación del uso de casco y chaleco reflectante en su planta de producción usando las 12 cámaras IP existentes.

**Tareas:**

1. Anotar 500 fotogramas con CVAT: clases `casco`, `sin_casco`, `chaleco`, `sin_chaleco`. Dividir 80/10/10.
2. Configurar un experimento YOLOv8n con transfer learning desde COCO (300 épocas, batch 16). Documentar hiperparámetros.
3. Evaluar el modelo: calcular mAP@50 y mAP@50:95 por clase. Analizar la matriz de confusión.
4. Exportar el modelo a ONNX y desplegar como endpoint REST con FastAPI.
5. Aplicar blur a los rostros detectados en todas las imágenes antes de almacenarlas. Documentar la medida en el registro de protección de datos.
6. Integrar la API con una de las cámaras IP (stream RTSP simulado) y verificar el funcionamiento en tiempo real.

**Entregable:** Informe de experimento + endpoint funcional + registro de protección de datos.

---

## Puntos clave — UD4

- Las tareas de visión artificial van desde clasificación hasta segmentación de instancias y estimación de pose.
- El preprocesamiento incluye decodificación, redimensionado, normalización y (para vídeo) segmentación en fotogramas o clips.
- La **anotación de calidad** es el factor más determinante en el rendimiento del modelo.
- Los modelos principales son: **CNN** (ResNet, EfficientNet), **ViT** (Swin, DeiT) y **YOLO** (detección en tiempo real).
- Los hiperparámetros clave son: arquitectura, tamaño de kernel, tamaño de lote, épocas y estrategia de transfer learning.
- El despliegue puede ser como API REST, stream de cámara, batch o dispositivo embebido (ONNX, TFLite, TensorRT).
- Las imágenes con personas son **datos personales**; se requieren anonimización, control de acceso y base legal RGPD.

---

## Criterios de evaluación — UD4

| Criterio | Indicador de logro |
|---|---|
| Preprocesa imágenes y vídeo | Aplica decodificación, homogeneización, segmentación y anotación correctamente |
| Configura y ejecuta el experimento | Selecciona arquitectura, configura hiperparámetros y lanza el entrenamiento |
| Evalúa el modelo | Calcula y documenta las métricas de visión (mAP, F1, matriz de confusión) |
| Documenta el experimento | Entrega informe con configuración, resultados, varianza y tiempo de cómputo |
| Despliega el modelo | Integra el modelo en el escenario productivo (API, cámara, batch o dispositivo) |
| Trata datos según privacidad | Aplica anonimización, control de acceso y documenta las medidas en el registro |
| Verifica la propiedad intelectual | Comprueba y documenta la licencia de todos los datasets utilizados |

---

<!-- _class: lead -->

[← Volver a MP03](../index.md)


---

<!-- nav-slide -->

## Navegación

[← UD3 · Análisis de series temporales](../UD3_Analisis-series-temporales/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD5 · Procesamiento de lenguaje nat… →](../UD5_PLN-procesamiento-voz/)
