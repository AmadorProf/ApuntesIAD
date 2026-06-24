# UD4 · Visión artificial sobre imágenes y vídeo

---

## 1. Introducción

La visión artificial es la disciplina que dota a los sistemas computacionales de la capacidad de interpretar y comprender el contenido visual del mundo —imágenes estáticas, secuencias de vídeo, flujos en tiempo real. En la última década, el salto cualitativo producido por las redes neuronales convolucionales profundas ha llevado la visión artificial de los laboratorios de investigación a las líneas de producción industrial, los sistemas de seguridad, los vehículos autónomos y los teléfonos inteligentes. Actualmente, los modelos de visión fundacionales como SAM (Segment Anything Model) y GroundingDINO representan un paso adicional hacia sistemas de propósito general que pueden segmentar o localizar cualquier objeto descrito en lenguaje natural sin necesidad de reentrenamiento.

El ciclo de vida de un sistema de visión artificial en producción es considerablemente más complejo que el de un modelo tabular o de forecasting. La cadena de valor incluye: la adquisición de la imagen o el vídeo (cámaras, protocolos de transferencia), el preprocesamiento (normalización, resize, augmentación de resolución), la inferencia (modelo de visión), el postprocesamiento (NMS para detección, máscaras para segmentación, transformación de coordenadas), y la integración con los sistemas de actuación o visualización aguas abajo. Cada uno de estos eslabones tiene requisitos técnicos específicos y puede ser el cuello de botella del sistema si no se diseña correctamente.

La optimización para inferencia en tiempo real es el reto técnico central en sistemas de visión industrial. Un modelo como YOLO v10 puede ejecutar inferencia a 100+ fotogramas por segundo en una GPU NVIDIA T4, pero alcanzar esa velocidad en producción requiere: cuantización del modelo (FP32 → FP16 o INT8 con TensorRT), compilación para el hardware objetivo, procesamiento por lotes cuando la latencia lo permite, y un pipeline de preprocesamiento que no introduzca cuellos de botella en CPU. En sistemas de vídeo en tiempo real, el pipeline de captura, decodificación, inferencia y visualización debe diseñarse como una cadena de producción donde cada etapa opera de forma asíncrona y en paralelo para maximizar el throughput.

Los protocolos de comunicación y los estándares de hardware de cámara industrial —GigE Vision e USB3 Vision— definen la interfaz entre la cámara y el sistema de procesamiento. Su conocimiento es imprescindible para el técnico que instala y configura un sistema de visión artificial industrial: la configuración incorrecta del trigger, el offset de adquisición, la ganancia o el balance de blancos puede arruinar la calidad de las imágenes y degradar irreversiblemente el rendimiento del modelo de visión. Esta unidad proporciona los fundamentos técnicos necesarios para diseñar, optimizar y poner en producción sistemas de visión artificial desde la cámara hasta el modelo, con especial énfasis en los aspectos operativos y de infraestructura.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Describir el pipeline completo de visión artificial en producción —adquisición, preprocesamiento, inferencia, postprocesamiento— e identificar las etapas críticas en términos de latencia y throughput para cada caso de uso.
2. Identificar y seleccionar el modelo de visión más adecuado (clasificación, detección, segmentación) para un caso de uso industrial dado, justificando la elección en función de la precisión requerida, la latencia disponible y los recursos de cómputo.
3. Desplegar un modelo YOLO v8/v10 exportado a ONNX o TensorRT sobre NVIDIA Triton Inference Server y medir su latencia y throughput con el cliente de benchmarking de Triton.
4. Optimizar un modelo de visión con TensorRT, aplicando cuantización FP16 e INT8 (con calibración) y comparar el rendimiento con la versión FP32 en términos de velocidad y pérdida de precisión.
5. Implementar un pipeline de procesamiento de vídeo en tiempo real con OpenCV, capturando fotogramas, ejecutando inferencia y anotando los resultados con bounding boxes y etiquetas.
6. Describir los protocolos GigE Vision y USB3 Vision, identificar los parámetros de configuración relevantes de una cámara industrial (trigger, exposición, ganancia, ROI) y explicar su impacto en la calidad de la imagen y el rendimiento del modelo.
7. Analizar los requisitos de latencia y throughput de tres casos de uso industriales de visión artificial (control de calidad visual, reconocimiento facial, análisis de multitudes) e identificar los compromisos técnicos en cada uno.
8. Describir el impacto del EU AI Act en los sistemas de reconocimiento facial y biometría en tiempo real, identificando las restricciones aplicables en espacios públicos.

---

## 3. Tareas de visión artificial y modelos de referencia

### 3.1 Clasificación de imagen

La **clasificación de imagen** asigna una etiqueta de clase a toda la imagen. Es la tarea más simple de visión artificial y la base histórica del deep learning aplicado a imágenes (ImageNet, AlexNet, 2012).

Los modelos de referencia actuales para clasificación son:

- **ResNet** (He et al., 2015): arquitectura con conexiones residuales que resuelve el problema del gradiente desvaneciente en redes profundas. ResNet-50 (25M parámetros) y ResNet-101 son los más usados como backbones.
- **EfficientNet** (Tan & Le, 2019): familia de modelos que escala eficientemente anchura, profundidad y resolución de forma conjunta. EfficientNet-B4 logra accuracy superior a ResNet-50 con menos parámetros.
- **Vision Transformer (ViT)**: arquitectura basada íntegramente en mecanismos de atención, sin convoluciones. Supera a EfficientNet en datasets grandes (JFT-300M), pero requiere más datos de entrenamiento.

```python
import torch
import torchvision.models as models
from torchvision import transforms
from PIL import Image

# Cargar EfficientNet-B4 preentrenado en ImageNet
model = models.efficientnet_b4(weights="IMAGENET1K_V1")
model.eval()

# Preprocesamiento estándar ImageNet
preprocess = transforms.Compose([
    transforms.Resize(380),
    transforms.CenterCrop(380),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

image = Image.open("pieza_inspeccion.jpg")
input_tensor = preprocess(image).unsqueeze(0)

with torch.no_grad():
    output = model(input_tensor)
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    top5 = torch.topk(probabilities, 5)
```

### 3.2 Detección de objetos: YOLO v8/v9/v10

La **detección de objetos** localiza instancias de objetos en la imagen y las clasifica. El output es una lista de bounding boxes con clase y puntuación de confianza.

La familia **YOLO (You Only Look Once)** es el estándar de facto en producción por su balance entre velocidad y precisión. Las versiones recientes (v8, v9, v10) las desarrolla y mantiene **Ultralytics**:

| Variante | Parámetros | mAP50-95 (COCO) | FPS (GPU A100) | Caso de uso |
|---|---|---|---|---|
| YOLOv8n (nano) | 3.2M | 37.3 | 1100 | Edge / tiempo real muy exigente |
| YOLOv8s (small) | 11.2M | 44.9 | 480 | Balance velocidad/precisión en edge |
| YOLOv8m (medium) | 25.9M | 50.2 | 234 | Producción general |
| YOLOv8l (large) | 43.7M | 52.9 | 134 | Alta precisión, GPU servidor |
| YOLOv8x (xlarge) | 68.2M | 53.9 | 97 | Máxima precisión |
| YOLOv10n | 2.3M | 38.5 | 1200 | Edge sin NMS (NMS-free) |

```python
from ultralytics import YOLO
import cv2
import numpy as np

# Cargar modelo y hacer inferencia
model = YOLO("yolov8m.pt")

# Inferencia sobre imagen
results = model.predict(
    source="imagen_linea_produccion.jpg",
    conf=0.45,           # umbral de confianza mínimo
    iou=0.7,             # umbral IoU para NMS
    imgsz=640,           # tamaño de entrada
    device="cuda:0"
)

# Procesar resultados
for result in results:
    boxes = result.boxes
    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        print(f"Clase: {model.names[cls]}, Confianza: {conf:.3f}, BBox: [{x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}]")

# Exportar a ONNX para serving
model.export(format="onnx", imgsz=640, simplify=True, opset=17)

# Exportar a TensorRT
model.export(format="engine", imgsz=640, half=True)  # FP16
```

### 3.3 Segmentación semántica e instancias

La **segmentación semántica** asigna una clase a cada píxel de la imagen. La **segmentación de instancias** distingue además entre instancias individuales de la misma clase (dos personas son dos instancias distintas, no un solo objeto "persona").

**SAM (Segment Anything Model)** de Meta es el modelo fundacional de referencia para segmentación sin necesidad de reentrenamiento. Puede segmentar cualquier objeto a partir de un punto, una bounding box o texto como prompt:

```python
from segment_anything import SamPredictor, sam_model_registry
import numpy as np
import cv2

sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h_4b8939.pth")
sam.to(device="cuda")
predictor = SamPredictor(sam)

image = cv2.imread("imagen.jpg")
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
predictor.set_image(image_rgb)

# Segmentar a partir de punto
input_point = np.array([[500, 375]])
input_label = np.array([1])  # 1 = foreground

masks, scores, logits = predictor.predict(
    point_coords=input_point,
    point_labels=input_label,
    multimask_output=True,
)
# masks: array (3, H, W) con tres máscaras candidatas ordenadas por score
```

**GroundingDINO** combina detección de objetos con comprensión de lenguaje natural, permitiendo localizar objetos descritos en texto sin necesidad de entrenamiento específico:

```python
from groundingdino.util.inference import load_model, load_image, predict

model = load_model("groundingdino_swint_ogc.py", "groundingdino_swint_ogc.pth")
image_source, image = load_image("imagen_fabrica.jpg")

boxes, logits, phrases = predict(
    model=model,
    image=image,
    caption="tornillo defectuoso . soldadura fría . grieta superficial",
    box_threshold=0.35,
    text_threshold=0.25,
    device="cuda"
)
```

### 3.4 OCR y estimación de pose

El **OCR (Optical Character Recognition)** extrae texto de imágenes. En contextos industriales, se usa para leer matrículas de vehículos, códigos de barras, número de serie de piezas y etiquetas de productos. PaddleOCR y Tesseract son las librerías de código abierto más utilizadas.

La **estimación de pose** (pose estimation) detecta los puntos clave del esqueleto humano (articulaciones). Sus aplicaciones van desde el análisis biomecánico en ergonomía hasta la detección de comportamientos en sistemas de vigilancia. YOLOv8 Pose ofrece estimación de pose con la misma arquitectura de detección, con 17 keypoints del esqueleto COCO.

---

## 4. Serving con NVIDIA Triton Inference Server

### 4.1 Arquitectura de Triton

**NVIDIA Triton Inference Server** es el servidor de inferencia de referencia para modelos de visión artificial en producción. Soporta múltiples frameworks y formatos de modelo (TensorRT, ONNX, TensorFlow, PyTorch, Python), gestiona el scheduling de peticiones y el batching dinámico, y expone interfaces HTTP/REST y gRPC.

La estructura del repositorio de modelos de Triton:

```
model_repository/
├── yolov8m_onnx/
│   ├── config.pbtxt
│   └── 1/
│       └── model.onnx
├── yolov8m_trt/
│   ├── config.pbtxt
│   └── 1/
│       └── model.plan       # motor TensorRT compilado
└── resnet50_trt/
    ├── config.pbtxt
    └── 1/
        └── model.plan
```

Configuración del modelo YOLO v8 en Triton (config.pbtxt):

```protobuf
name: "yolov8m_onnx"
backend: "onnxruntime"
max_batch_size: 8

input [
  {
    name: "images"
    data_type: TYPE_FP32
    dims: [ 3, 640, 640 ]
  }
]

output [
  {
    name: "output0"
    data_type: TYPE_FP32
    dims: [ 84, 8400 ]
  }
]

dynamic_batching {
  preferred_batch_size: [ 1, 4, 8 ]
  max_queue_delay_microseconds: 5000
}

instance_group [
  {
    kind: KIND_GPU
    count: 2
    gpus: [ 0 ]
  }
]
```

### 4.2 Benchmarking con el cliente de Triton

```bash
# Instalar herramientas de cliente
pip install tritonclient[all]

# Benchmark con perf_analyzer (incluido en Triton SDK)
perf_analyzer \
  -m yolov8m_onnx \
  -u localhost:8001 \
  --protocol grpc \
  --shape images:1,3,640,640 \
  --concurrency-range 1:16:2 \
  --measurement-interval 5000 \
  --percentile 99 \
  -f resultados_benchmark.csv
```

### 4.3 Cliente Python para Triton

```python
import tritonclient.grpc as grpcclient
import numpy as np

client = grpcclient.InferenceServerClient(url="localhost:8001")

# Preparar input
image_np = preprocess_image("imagen.jpg")  # (1, 3, 640, 640) float32
inputs = [grpcclient.InferInput("images", image_np.shape, "FP32")]
inputs[0].set_data_from_numpy(image_np)

outputs = [grpcclient.InferRequestedOutput("output0")]

# Inferencia
response = client.infer(
    model_name="yolov8m_onnx",
    inputs=inputs,
    outputs=outputs
)

raw_output = response.as_numpy("output0")  # (1, 84, 8400)
boxes, scores, class_ids = postprocess_yolo(raw_output, conf_threshold=0.45, iou_threshold=0.7)
```

---

## 5. Optimización con TensorRT

### 5.1 Cuantización FP16 e INT8

**TensorRT** es el SDK de NVIDIA para optimización de inferencia en GPUs. Aplica cuatro tipos principales de optimizaciones: fusión de capas, cuantización de precisión, selección de kernels optimizados por hardware, y eliminación de tensores innecesarios.

La **cuantización FP16** reduce a la mitad el uso de memoria y dobla el throughput en GPUs con Tensor Cores, con pérdida de precisión típicamente inferior al 1%:

```python
from ultralytics import YOLO

# Exportar a TensorRT FP16
model = YOLO("yolov8m.pt")
model.export(
    format="engine",
    imgsz=640,
    half=True,              # FP16
    device=0,
    workspace=4,            # GB de memoria del workspace TensorRT
    simplify=True
)
```

La **cuantización INT8** reduce adicionalmente el tamaño del modelo a un cuarto del FP32 y puede multiplicar el throughput por cuatro, a costa de una mayor degradación de precisión que requiere calibración con datos representativos:

```python
import tensorrt as trt
import numpy as np

class CalibrationDataset(trt.IInt8EntropyCalibrator2):
    """Calibrador INT8 que alimenta TensorRT con imágenes representativas."""
    
    def __init__(self, calibration_images: list, batch_size: int = 8):
        super().__init__()
        self.batch_size = batch_size
        self.images = calibration_images
        self.current_idx = 0
        self.device_input = None
    
    def get_batch_size(self):
        return self.batch_size
    
    def get_batch(self, names):
        if self.current_idx + self.batch_size > len(self.images):
            return None
        batch = np.stack([
            preprocess_image(img)
            for img in self.images[self.current_idx:self.current_idx + self.batch_size]
        ])
        self.current_idx += self.batch_size
        # Copiar a memoria GPU y devolver puntero
        import pycuda.driver as cuda
        self.device_input = cuda.mem_alloc(batch.nbytes)
        cuda.memcpy_htod(self.device_input, batch)
        return [int(self.device_input)]
    
    def read_calibration_cache(self):
        if os.path.exists("calibration_cache.bin"):
            with open("calibration_cache.bin", "rb") as f:
                return f.read()
    
    def write_calibration_cache(self, cache):
        with open("calibration_cache.bin", "wb") as f:
            f.write(cache)
```

### 5.2 Comparativa de precisiones

| Precisión | Tamaño modelo | Latencia relativa | mAP50 (COCO) | Caso de uso |
|---|---|---|---|---|
| FP32 | 100% | 1.0× (base) | 50.2 | Desarrollo, validación |
| FP16 | 50% | 0.5× | 50.0 (-0.4%) | Producción estándar GPU NVIDIA |
| INT8 (calibrado) | 25% | 0.25× | 49.1 (-2.2%) | Producción edge, throughput crítico |
| INT8 (sin calibrar) | 25% | 0.25× | 44.3 (-11.7%) | No recomendado |

---

## 6. Procesamiento de vídeo en tiempo real

### 6.1 Pipeline con OpenCV

**OpenCV** es la librería de visión artificial de referencia para el procesamiento de vídeo. La arquitectura básica de un pipeline de inferencia sobre vídeo en tiempo real:

```python
import cv2
from ultralytics import YOLO
import time
from collections import deque

model = YOLO("yolov8m.engine")  # Modelo TensorRT compilado

cap = cv2.VideoCapture(0)  # Cámara 0, o ruta a fichero de vídeo
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

fps_queue = deque(maxlen=30)
frame_count = 0

while True:
    t_inicio = time.perf_counter()
    
    ret, frame = cap.read()
    if not ret:
        break
    
    # Inferencia (el modelo gestiona internamente el resize y normalización)
    results = model(frame, verbose=False, conf=0.4)[0]
    
    # Anotar frame con bounding boxes
    frame_anotado = results.plot()
    
    # Calcular y mostrar FPS
    t_fin = time.perf_counter()
    fps_queue.append(1.0 / (t_fin - t_inicio))
    fps_actual = sum(fps_queue) / len(fps_queue)
    
    cv2.putText(
        frame_anotado,
        f"FPS: {fps_actual:.1f} | Objetos: {len(results.boxes)}",
        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
    )
    
    cv2.imshow("Visión Artificial - Producción", frame_anotado)
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
```

### 6.2 Pipeline asíncrono con GStreamer

Para sistemas de vídeo de alta exigencia donde OpenCV introduce latencia inaceptable, **GStreamer** permite construir pipelines de vídeo altamente optimizados con aceleración hardware de decodificación (NVDEC en GPUs NVIDIA):

```bash
# Pipeline GStreamer: cámara IP → decodificación H.264 con NVDEC → inferencia YOLO → codificación y stream
gst-launch-1.0 \
  rtspsrc location="rtsp://camara-ip/stream" latency=0 ! \
  rtph264depay ! \
  h264parse ! \
  nvv4l2decoder ! \
  nvvidconv ! \
  video/x-raw,format=BGRx ! \
  videoconvert ! \
  video/x-raw,format=BGR ! \
  appsink name=sink max-buffers=1 drop=true
```

En Python, la integración con GStreamer para captura de bajo nivel:

```python
import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib
import numpy as np

Gst.init(None)

pipeline_str = """
    rtspsrc location=rtsp://camara/stream latency=100 !
    rtph264depay ! h264parse ! nvv4l2decoder !
    nvvidconv ! video/x-raw,format=BGRx !
    videoconvert ! video/x-raw,format=BGR !
    appsink name=appsink max-buffers=1 drop=true emit-signals=true
"""

pipeline = Gst.parse_launch(pipeline_str)
appsink = pipeline.get_by_name("appsink")

def on_new_sample(sink):
    sample = sink.emit("pull-sample")
    buffer = sample.get_buffer()
    caps = sample.get_caps()
    
    width = caps.get_structure(0).get_value("width")
    height = caps.get_structure(0).get_value("height")
    
    success, map_info = buffer.map(Gst.MapFlags.READ)
    if success:
        frame = np.ndarray((height, width, 3), dtype=np.uint8, buffer=map_info.data)
        # Ejecutar inferencia sobre frame
        procesar_frame(frame.copy())
        buffer.unmap(map_info)
    
    return Gst.FlowReturn.OK

appsink.connect("new-sample", on_new_sample)
pipeline.set_state(Gst.State.PLAYING)
```

---

## 7. Cámaras industriales y protocolos

### 7.1 GigE Vision

**GigE Vision** es el estándar de la industria para cámaras industriales de alta velocidad conectadas mediante Ethernet Gigabit. Desarrollado por la Automated Imaging Association (AIA), define el protocolo de transporte (GVSP: GigE Vision Stream Protocol), el protocolo de control (GVCP: GigE Vision Control Protocol) y el modelo de características de cámara (GenICam).

Las ventajas de GigE Vision son: cables de hasta 100 metros sin repetidores, soporte para múltiples cámaras en la misma red, y disponibilidad de hardware de red estándar. La latencia es típicamente de 1-2 ms para resoluciones de 2-5 Mpx a 30 fps.

La configuración de una cámara GigE Vision mediante PyPylon (Basler) o Aravis (librería libre):

```python
import pypylon.pylon as pylon

# Enumerar cámaras disponibles
factory = pylon.TlFactory.GetInstance()
devices = factory.EnumerateDevices()
print(f"Cámaras detectadas: {len(devices)}")

# Abrir primera cámara
camera = pylon.InstantCamera(factory.CreateFirstDevice())
camera.Open()

# Configurar parámetros de adquisición
camera.Width.Value = 1920
camera.Height.Value = 1080
camera.PixelFormat.Value = "BGR8"

# Trigger externo (para sincronización con línea de producción)
camera.TriggerMode.Value = "On"
camera.TriggerSource.Value = "Line1"  # señal de trigger en entrada digital 1
camera.TriggerActivation.Value = "RisingEdge"

# Exposición fija (para evitar variación en condiciones de fábrica)
camera.ExposureAuto.Value = "Off"
camera.ExposureTime.Value = 5000  # microsegundos

# Ganancia fija
camera.GainAuto.Value = "Off"
camera.Gain.Value = 0.0  # dB

camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

while camera.IsGrabbing():
    grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    
    if grab_result.GrabSucceeded():
        frame = grab_result.Array  # NumPy array (H, W, C) en BGR
        procesar_frame(frame)
    
    grab_result.Release()
```

### 7.2 USB3 Vision

**USB3 Vision** es el estándar equivalente para conexiones USB 3.0, con anchos de banda de hasta 400 MB/s. Es adecuado para sistemas con distancias cortas (hasta 5 metros sin hub activo) y entornos donde la instalación de infraestructura de red no es práctica. La API es compatible con GigE Vision a nivel de GenICam, lo que permite usar el mismo código de adquisición con ambos tipos de cámara.

### 7.3 Parámetros críticos de configuración

| Parámetro | Descripción | Impacto en el modelo |
|---|---|---|
| Exposición | Tiempo de apertura del obturador | Sobreexposición/subexposición degrada detección |
| Ganancia | Amplificación electrónica de la señal | Ganancia alta → ruido → falsos positivos |
| Balance de blancos | Corrección de color por iluminación | Crítico para modelos entrenados en colores específicos |
| ROI (Region of Interest) | Subregión activa del sensor | Reduce carga de transferencia y procesamiento |
| Trigger | Fuente y modo de disparo de adquisición | Sincronización con proceso industrial |
| Binning | Agrupación de píxeles para mayor sensibilidad | Reduce resolución pero mejora SNR en baja luz |
| Framerate | Fotogramas por segundo | Debe ser compatible con el throughput del modelo |

---

## 8. Casos de uso industriales y requisitos

### 8.1 Control de calidad visual

El **control de calidad visual** (visual inspection) es la aplicación industrial de visión artificial más extendida. Sustituye a los inspectores humanos en la detección de defectos en superficies, dimensionado de piezas, verificación de presencia/ausencia de componentes y lectura de matrículas o códigos.

Requisitos técnicos típicos:
- Resolución suficiente para detectar el defecto más pequeño relevante (típicamente ≥ 5 píxeles por defecto mínimo).
- Latencia < 100 ms para no convertirse en cuello de botella en líneas de alta cadencia.
- Tasa de falsos negativos (defectos no detectados) extremadamente baja; se acepta cierta tasa de falsos positivos (reprocesado innecesario).
- Robustez a variaciones de iluminación, posición y orientación de las piezas.

### 8.2 Reconocimiento facial

Los sistemas de **reconocimiento facial** tienen requisitos técnicos y legales muy específicos. Técnicamente, el pipeline incluye: detección de cara, alineamiento de puntos clave faciales, extracción de embedding facial y comparación con la base de datos de identidades.

Desde el punto de vista legal, el **EU AI Act** clasifica los sistemas de identificación biométrica en tiempo real en espacios de acceso público como **sistemas de IA prohibidos** (Artículo 5), con excepciones muy limitadas para fuerzas del orden bajo autorización judicial. Los sistemas de autenticación biométrica (verificación de identidad, no identificación en masa) son sistemas de alto riesgo sujetos al Título III del Reglamento.

### 8.3 Análisis de multitudes y comportamiento

Los sistemas de **análisis de multitudes** cuentan personas, estiman densidad, detectan comportamientos anómalos (carreras, caídas, formación de aglomeraciones) y monitorizan el flujo de personas en espacios públicos o privados. Sus requisitos son:

- Procesamiento de múltiples cámaras simultáneas (10-50 en instalaciones grandes).
- Latencia moderada aceptable (1-5 segundos para la mayoría de los casos de uso).
- Alta capacidad de almacenamiento para archivo de vídeo.
- Integración con sistemas de gestión de edificios y seguridad.

### 8.4 Resumen de requisitos por caso de uso

| Caso de uso | Latencia máx. | Throughput típico | Precisión mínima | Regulación relevante |
|---|---|---|---|---|
| Control de calidad en línea | < 100 ms | 10-120 fps | FP < 5%, FN < 0.1% | ISO 9001, sector específico |
| Reconocimiento facial (auth.) | < 500 ms | Bajo (acceso) | FAR < 0.01% | EU AI Act alto riesgo, RGPD |
| Identificación biométrica masiva | N/A | N/A | N/A | Prohibido EU AI Act art. 5 |
| Análisis de multitudes (densidad) | 1-5 seg. | 1-30 fps × N cámaras | Conteo ± 10% | Depende del uso |
| OCR industrial (matrícula/código) | < 200 ms | 5-30 fps | > 99.5% | Sector específico |

---

## 9. Actividades prácticas

### Actividad 1 — Pipeline de detección de objetos con YOLO v8 y Triton

**Descripción**: El formador proporciona un entorno de laboratorio con un servidor NVIDIA Triton y un conjunto de imágenes de control de calidad industrial (piezas mecánicas con defectos anotados). El estudiante debe: exportar YOLOv8m a ONNX y configurar el repositorio de modelos de Triton con batching dinámico (preferred_batch_size: [1, 4, 8]), realizar el benchmark del modelo con `perf_analyzer` midiendo latencia P50/P95/P99 y throughput para niveles de concurrencia 1, 4, 8 y 16, implementar un cliente Python que envíe peticiones de inferencia por gRPC y anote las imágenes con los resultados, y documentar los resultados de rendimiento en una tabla comparativa con análisis.

**Entregable**: Fichero config.pbtxt + cliente Python anotado + tabla de resultados de benchmark con análisis (1 página).

**Criterios de evaluación**: Corrección de la configuración de Triton, funcionamiento del cliente gRPC, validez del análisis de rendimiento, calidad de la anotación de imágenes.

---

### Actividad 2 — Optimización TensorRT y comparativa de precisiones

**Descripción**: Partiendo del modelo YOLOv8m ONNX de la actividad anterior, el estudiante debe: exportar el modelo a TensorRT en tres precisiones (FP32, FP16, INT8 con calibración sobre el dataset proporcionado), medir la latencia de inferencia en batch_size=1 y batch_size=8 para las tres versiones, evaluar la pérdida de mAP50 comparando las predicciones de cada versión sobre el dataset de test con las anotaciones de referencia, y elaborar una tabla comparativa de las cuatro dimensiones (tamaño, latencia, throughput, mAP) con recomendación justificada para producción.

**Entregable**: Scripts de exportación y evaluación + tabla comparativa + recomendación justificada (1 página).

**Criterios de evaluación**: Corrección del proceso de calibración INT8, validez de las métricas de comparación, solidez de la recomendación para producción.

---

### Actividad 3 — Pipeline de vídeo en tiempo real con OpenCV

**Descripción**: Utilizando el modelo YOLOv8m TensorRT FP16 de la actividad anterior y una cámara web de laboratorio (o un fichero de vídeo proporcionado por el formador), el estudiante debe implementar un pipeline de vídeo en tiempo real que: capture fotogramas a 30 fps, ejecute inferencia con YOLOv8m TensorRT y anote los resultados, muestre en pantalla el FPS real (media móvil de los últimos 30 fotogramas), latencia de inferencia y número de objetos detectados, y registre en un fichero JSONL cada fotograma procesado con timestamp, latencia de inferencia, número de detecciones y clases detectadas. Al final, debe generar un resumen estadístico de las métricas registradas.

**Entregable**: Código Python del pipeline + fichero JSONL de métricas + resumen estadístico (tabla).

**Criterios de evaluación**: Pipeline funcional a la resolución y FPS objetivo, correcta instrumentación de métricas, completitud del log de eventos, análisis estadístico del rendimiento.

---

### Actividad 4 — Análisis de requisitos y restricciones normativas

**Descripción**: Una empresa de retail con 50 establecimientos en España quiere implantar un sistema de visión artificial que combine tres funcionalidades: (1) conteo de personas en tienda para gestión de aforo, (2) análisis de patrones de comportamiento de clientes (zonas de parada, recorridos habituales), y (3) identificación automática de clientes registrados en el programa de fidelización mediante reconocimiento facial para ofrecerles promociones personalizadas. El estudiante debe: analizar cada funcionalidad desde el punto de vista técnico (requisitos de latencia, hardware, modelo recomendado) y legal (clasificación en EU AI Act, obligaciones RGPD), identificar cuáles son viables sin restricciones, cuáles requieren medidas adicionales y cuáles están prohibidas, y proponer una arquitectura técnica alternativa para la funcionalidad prohibida que cumpla el mismo objetivo de negocio dentro del marco legal.

**Entregable**: Análisis técnico-legal de las tres funcionalidades (3-4 páginas) + propuesta de arquitectura alternativa.

**Criterios de evaluación**: Correcta clasificación de cada funcionalidad según EU AI Act, rigor del análisis de requisitos técnicos, creatividad y viabilidad de la alternativa propuesta, coherencia entre análisis legal y técnico.

---

## 10. Referencias

- **NVIDIA Triton Inference Server — Documentación oficial**: guía de instalación, configuración de modelos y API. Disponible en: [https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/index.html](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/index.html)

- **NVIDIA TensorRT — Documentación oficial**: guía de optimización, cuantización y compilación de modelos. Disponible en: [https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/](https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/)

- **Ultralytics YOLO v8/v10 — Documentación oficial**: guía de uso, entrenamiento, exportación y deployment. Disponible en: [https://docs.ultralytics.com/](https://docs.ultralytics.com/)

- **Segment Anything Model (SAM) — Meta AI Research**: paper y código oficial. Disponible en: [https://segment-anything.com/](https://segment-anything.com/)

- **GroundingDINO — Repositorio oficial**: detección open-vocabulary guiada por texto. Disponible en: [https://github.com/IDEA-Research/GroundingDINO](https://github.com/IDEA-Research/GroundingDINO)

- **OpenCV — Documentación oficial**: referencia de la librería de visión artificial de código abierto. Disponible en: [https://docs.opencv.org/4.x/](https://docs.opencv.org/4.x/)

- **GStreamer — Documentación oficial**: guía de pipelines multimedia y plugins NVIDIA. Disponible en: [https://gstreamer.freedesktop.org/documentation/](https://gstreamer.freedesktop.org/documentation/)

- **GigE Vision Standard — AIA**: especificación del estándar de cámaras industriales Ethernet. Disponible en: [https://www.visiononline.org/vision-standards-details.cfm/vision-standards/gige-vision/id/17](https://www.visiononline.org/vision-standards-details.cfm/vision-standards/gige-vision/id/17)

- **Basler PyPylon — Documentación oficial**: API Python para cámaras Basler GigE Vision y USB3 Vision. Disponible en: [https://github.com/basler/pypylon](https://github.com/basler/pypylon)

- **EU AI Act — Artículo 5 (Prácticas de IA prohibidas)**: texto del Reglamento (UE) 2024/1689, identificación biométrica en tiempo real. Disponible en: [https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689)

- **PyTorch — TorchVision Models**: documentación de modelos de clasificación y detección preentrenados. Disponible en: [https://pytorch.org/vision/stable/models.html](https://pytorch.org/vision/stable/models.html)

- **COCO Dataset — Common Objects in Context**: dataset de referencia para evaluación de modelos de detección y segmentación. Disponible en: [https://cocodataset.org/](https://cocodataset.org/)

---

*UD4 · MP03 Explotación de Servicios de Datos y Analítica · CFS2 Instalación, despliegue y explotación de sistemas de IA*
