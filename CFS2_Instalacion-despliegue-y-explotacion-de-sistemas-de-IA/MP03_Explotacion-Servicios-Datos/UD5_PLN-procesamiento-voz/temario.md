# UD5 · Procesamiento de lenguaje natural y voz

---

## 1. Introducción

El procesamiento del lenguaje natural (PLN) constituye hoy uno de los pilares más activos de los sistemas de IA en producción. La capacidad de extraer significado de texto no estructurado, identificar entidades, detectar la polaridad emocional de un mensaje o responder preguntas sobre documentos corporativos ha dejado de ser un problema de investigación para convertirse en infraestructura productiva en sectores tan dispares como la banca, la sanidad, los medios de comunicación o la administración pública. En este contexto, la competencia técnica exigida al profesional no se limita al conocimiento de los modelos, sino a la capacidad de desplegarlos, optimizarlos y operarlos a escala bajo restricciones reales de latencia, coste y disponibilidad.

La llegada de la arquitectura Transformer en 2017 (Vaswani et al., "Attention Is All You Need") marcó un punto de inflexión irreversible. Modelos como BERT, RoBERTa o DistilBERT establecieron nuevos estándares en tareas de comprensión del lenguaje mediante el preentrenamiento masivo sobre corpus de texto genérico seguido de fine-tuning sobre conjuntos de datos específicos de la tarea. Esta estrategia de transfer learning redujo drásticamente la cantidad de datos etiquetados necesarios para alcanzar rendimiento competitivo, y democratizó el acceso a modelos de alta calidad a través de plataformas como Hugging Face Hub, que alberga actualmente más de medio millón de modelos públicos. La comprensión profunda de este ecosistema —sus capacidades, sus limitaciones y sus costes operativos— es indispensable para cualquier profesional que trabaje en el despliegue de sistemas inteligentes.

El procesamiento de la voz añade una dimensión adicional de complejidad técnica. Los sistemas de reconocimiento automático del habla (ASR, Automatic Speech Recognition) y síntesis de voz (TTS, Text-to-Speech) deben operar sobre señales acústicas que incorporan variabilidad fonológica, acústica y de canal que el texto no presenta. La publicación de Whisper por OpenAI en 2022 supuso un avance significativo en ASR multilingüe robusto, alcanzando rendimiento humano en varios benchmarks sin necesidad de adaptación específica al dominio. La integración de ASR, PLN y TTS en pipelines de producción permite construir sistemas complejos como asistentes conversacionales, sistemas de análisis de llamadas en tiempo real o plataformas de subtitulación automática, todos ellos con requisitos de ingeniería sustancialmente diferentes de un modelo aislado.

Esta unidad aborda el ciclo de vida completo de los sistemas de PLN y procesamiento de voz: desde la selección del modelo y la estrategia de serving hasta la optimización de la inferencia para entornos con restricciones de recursos, la gestión de la complejidad lingüística derivada de la multitud de idiomas y dialectos, y la evaluación cuantitativa del rendimiento con las métricas estándar del campo. Se presta especial atención a los trade-offs de ingeniería que determinan la viabilidad operativa de estos sistemas: tamaño del modelo, latencia de inferencia, precisión, coste de cómputo y mantenibilidad a largo plazo.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Identificar y describir las principales tareas de PLN en producción —clasificación de texto, reconocimiento de entidades nombradas (NER), análisis de sentimiento, resumen automático, traducción automática y question answering— especificando sus características de entrada/salida y sus métricas de evaluación estándar.
2. Seleccionar el modelo Transformer más adecuado (BERT, RoBERTa, DistilBERT, mBERT) para un caso de uso dado, justificando la elección en función de los requisitos de rendimiento, latencia, soporte lingüístico y recursos disponibles.
3. Desplegar un modelo Transformer para inferencia en producción utilizando Hugging Face Transformers + FastAPI, y comparar cuantitativamente esta solución con las alternativas basadas en ONNX Runtime y NVIDIA Triton Inference Server.
4. Aplicar técnicas de optimización de inferencia para transformers —cuantización INT8, knowledge distillation y structured pruning— y medir su impacto en latencia, throughput y exactitud del modelo.
5. Construir un pipeline de reconocimiento automático del habla utilizando Whisper e integrarlo con componentes de PLN para implementar un flujo voz-a-texto-a-acción operativo.
6. Diseñar un sistema de análisis de llamadas de call center que incluya ASR, speaker diarization, análisis de sentimiento y extracción de resúmenes, especificando la arquitectura de componentes y los umbrales de calidad.
7. Calcular y comparar las métricas de evaluación relevantes (F1 macro/micro, BLEU, ROUGE-L, WER) para tareas de PLN y ASR, interpretando correctamente los resultados en el contexto de un sistema en producción.
8. Diseñar una estrategia de gestión de idiomas y dialectos en un sistema PLN multilingüe, abordando los problemas de desequilibrio de recursos lingüísticos y degradación de rendimiento por variación dialectal.

---

## 3. Tareas de PLN en producción

### 3.1 Clasificación de texto

La clasificación de texto es la tarea de asignar una o varias etiquetas predefinidas a una secuencia de texto. En producción cubre escenarios que van desde la clasificación binaria (spam/no-spam, positivo/negativo) hasta la clasificación multiclase (categorías de producto, departamento de atención al cliente) y multilabel (un documento puede pertenecer a múltiples categorías simultáneamente). La clasificación multilabel es técnicamente más exigente porque no existe una distribución softmax normalizada: cada clase se modela como un problema binario independiente con umbral ajustable.

Los modelos basados en Transformer para clasificación de texto funcionan añadiendo una capa de clasificación sobre el embedding especial `[CLS]` que BERT produce para cada secuencia. Este embedding agrega información contextual de toda la secuencia, lo que lo hace idóneo como representación para tareas de clasificación de nivel de documento. El fine-tuning requiere ajustar tanto los parámetros de la capa de clasificación añadida como los del encoder Transformer subyacente, con learning rates típicamente en el rango de 2e-5 a 5e-5.

En producción, la clasificación de texto enfrenta el reto del **concept drift**: la distribución de los textos de entrada varía con el tiempo (nuevas temáticas, cambios de lenguaje, eventos externos), lo que puede degradar la precisión del modelo sin que ningún componente técnico falle. La monitorización continua del rendimiento mediante métricas de producción —ratio de confianza baja, distribución de clases predichas, F1 en muestras etiquetadas recientes— es tan importante como el despliegue inicial.

### 3.2 Reconocimiento de entidades nombradas (NER)

El NER identifica y clasifica en categorías predefinidas las menciones de entidades en el texto: personas (PER), organizaciones (ORG), localizaciones (LOC), fechas, cantidades monetarias, productos, etc. En producción, el NER es componente crítico de sistemas de extracción de información estructurada a partir de documentos no estructurados: contratos, artículos de prensa, historias clínicas, correos electrónicos.

El esquema de etiquetado estándar es el formato BIO (Beginning-Inside-Outside) o sus variantes BIOES. Para NER con Transformers, cada token recibe una etiqueta de la secuencia, con la complejidad adicional de que los tokenizadores subpalabra (WordPiece, BPE) fragmentan las palabras en subunidades, lo que requiere una estrategia de alineación entre tokens del modelo y palabras del texto original para la producción del output final.

El dominio especializado es especialmente relevante en NER: un modelo preentrenado en Wikipedia y noticias puede tener bajo rendimiento en textos médicos o jurídicos porque las entidades relevantes no aparecen en el corpus de preentrenamiento o tienen características lingüísticas distintas. En estos contextos, el fine-tuning sobre conjuntos de datos del dominio o el uso de modelos especializados (BioBERT para biomedicina, Legal-BERT para derecho) es preferible al modelo genérico.

### 3.3 Análisis de sentimiento y opinión

El análisis de sentimiento clasifica la actitud o valoración expresada en el texto: polaridad (positivo/negativo/neutro), intensidad emocional, o emociones específicas (alegría, ira, miedo, sorpresa). El análisis de sentimiento a nivel de aspecto (ABSA, Aspect-Based Sentiment Analysis) va más allá de la polaridad global y determina la valoración del texto para cada aspecto mencionado explícitamente ("la batería dura poco pero la pantalla es excelente").

En escenarios de producción como análisis de reseñas de producto, monitorización de redes sociales o análisis de satisfacción en encuestas, el volumen de datos procesados diariamente puede ser elevado —millones de documentos en plataformas de e-commerce—, lo que hace que la eficiencia de la inferencia sea determinante para la viabilidad del servicio.

### 3.4 Resumen automático

El resumen automático genera un texto condensado que captura la información más relevante del documento original. Se distinguen dos paradigmas:

- **Extractivo**: selecciona oraciones o fragmentos del documento original sin modificarlos. Técnicamente más simple y controlable, pero puede producir textos incoherentes si las oraciones seleccionadas pierden contexto.
- **Abstractivo**: genera un resumen con lenguaje nuevo que puede no estar presente en el original. Los modelos seq2seq como BART y T5 son los estándar para resumen abstractivo. Producen resúmenes más fluidos, pero pueden introducir alucinaciones (hechos incorrectos no presentes en el original).

En producción, el resumen abstractivo requiere validación de fidelidad: el resumen debe ser fiel al contenido del documento original. Técnicas como la verificación de consistencia factual mediante NLI (Natural Language Inference) se integran en los pipelines de producción de entornos críticos.

### 3.5 Traducción automática y Question Answering

La **traducción automática neuronal** (NMT) se basa en modelos seq2seq entrenados sobre pares de documentos en dos idiomas. Helsinki-NLP proporciona en Hugging Face Hub modelos MarianMT para cientos de pares de idiomas. Para idiomas de bajos recursos, los modelos multilingües como mBART o NLLB-200 de Meta (que soporta 200 idiomas) ofrecen cobertura amplia con un único modelo.

El **question answering** extractivo localiza en un contexto de texto la respuesta a una pregunta en lenguaje natural, devolviendo el span de texto que contiene la respuesta. Los modelos basados en BERT leen la pregunta y el contexto conjuntamente y predicen los índices de inicio y fin de la respuesta en el contexto. En sistemas de producción RAG (Retrieval-Augmented Generation), el QA extractivo o generativo se combina con un motor de recuperación de documentos (BM25, embeddings densos) para responder preguntas sobre bases de conocimiento corporativas.

---

## 4. Arquitecturas Transformer para PLN

### 4.1 BERT y su familia

**BERT** (Bidirectional Encoder Representations from Transformers, Devlin et al., 2018) preentrenó un encoder Transformer de 12 capas (BERT-base, 110M parámetros) y 24 capas (BERT-large, 340M parámetros) sobre dos objetivos: Masked Language Modeling (MLM), que predice tokens enmascarados del contexto bidireccional, y Next Sentence Prediction (NSP), que clasifica si dos oraciones son consecutivas. La bidireccionalidad es la característica diferencial de BERT respecto a modelos autorregresivos: cada token atiende a todos los tokens de la secuencia en ambas direcciones, produciendo representaciones ricas en contexto.

**RoBERTa** (Liu et al., 2019) demostró que los resultados de BERT estaban limitados por las decisiones de preentrenamiento, no por la arquitectura. Entrenó durante más tiempo, con batches más grandes, eliminando el objetivo NSP (que se comprobó perjudicial), y con secuencias de longitud completa. El resultado superó significativamente a BERT en todos los benchmarks del GLUE y SuperGLUE sin cambiar la arquitectura.

**DistilBERT** (Sanh et al., 2019) aplica knowledge distillation para producir un modelo con el 60% de los parámetros de BERT-base (66M), el 60% de la velocidad y el 97% de sus capacidades medidas en GLUE. Es la opción de referencia cuando la latencia y el coste son restricciones primarias y la ligera pérdida de precisión es aceptable.

**mBERT** (Multilingual BERT) entrena el mismo modelo de 12 capas sobre texto en 104 idiomas simultáneamente. Su propiedad de transferencia cross-lingual —la capacidad de aprender en un idioma y generalizar a otros— lo hace útil para organizaciones con necesidades multilingües que no disponen de datos etiquetados en todos sus idiomas.

### 4.2 Comparativa de modelos Transformer para PLN

| Modelo | Parámetros | Idiomas | GLUE | Latencia relativa | Caso de uso principal |
|---|---|---|---|---|---|
| BERT-base | 110M | 1 (en) | 79.6 | 1.0x (referencia) | Fine-tuning general en inglés |
| BERT-large | 340M | 1 (en) | 82.1 | ~3.5x | Máxima precisión, sin restricción de latencia |
| RoBERTa-base | 125M | 1 (en) | 86.4 | ~1.1x | Fine-tuning de alta calidad en inglés |
| DistilBERT | 66M | 1 (en) | 77.0 | 0.6x | Entornos con restricción de latencia/coste |
| mBERT | 177M | 104 | 74.8 | ~1.6x | Soporte multilingüe, transferencia cross-lingual |
| XLM-RoBERTa-base | 270M | 100 | 83.5 | ~2.4x | PLN multilingüe de alta calidad |

---

## 5. Serving de modelos Transformer en producción

### 5.1 Hugging Face Transformers + FastAPI

La combinación de la librería `transformers` de Hugging Face con FastAPI es el punto de entrada estándar para desplegar modelos PLN en producción. Permite pasar de un notebook de investigación a un endpoint HTTP con mínima fricción.

```python
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
import uvicorn

# Carga el pipeline en el startup del servidor (no en cada request)
classifier = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=0  # GPU índice 0; -1 para CPU
)

app = FastAPI()

class TextRequest(BaseModel):
    text: str

@app.post("/predict")
def predict(request: TextRequest):
    result = classifier(request.text)
    return {"label": result[0]["label"], "score": result[0]["score"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Las limitaciones de esta arquitectura son significativas en producción a escala:
- **Sin batching dinámico**: cada request se procesa de forma independiente, infrautilizando la GPU.
- **Sin gestión de colas**: bajo carga pico, los requests se acumulan en la capa de aplicación sin control.
- **Carga bloqueante**: el modelo se carga en memoria en el inicio del servidor, pero múltiples workers de uvicorn crearían múltiples instancias del modelo.

Para cargas moderadas (< 100 req/s) con modelos pequeños, esta arquitectura es operativa. Para cargas más exigentes, es necesario un servidor de inferencia especializado.

### 5.2 ONNX Runtime

**ONNX Runtime** (ORT) es el motor de inferencia de alto rendimiento de Microsoft para modelos en formato ONNX (Open Neural Network Exchange). La conversión de un modelo Hugging Face a ONNX permite:

- Ejecutar la inferencia sin la sobrecarga de PyTorch o TensorFlow.
- Activar optimizaciones de grafo (fusión de operadores, eliminación de nodos redundantes).
- Aprovechar backends hardware específicos mediante los **Execution Providers** (CUDA, TensorRT, DirectML, CoreML, CPU).

```bash
# Exportar un modelo Hugging Face a ONNX con la librería optimum
pip install optimum[onnxruntime]

optimum-cli export onnx \
  --model distilbert-base-uncased-finetuned-sst-2-english \
  --task text-classification \
  ./modelo_onnx/
```

```python
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("./modelo_onnx")
model = ORTModelForSequenceClassification.from_pretrained("./modelo_onnx")

inputs = tokenizer("Excelente producto, muy recomendable", return_tensors="pt")
outputs = model(**inputs)
```

La ganancia de rendimiento típica de ONNX Runtime sobre PyTorch en CPU es de 2-4x en latencia para modelos BERT. Con el provider TensorRT en GPU, la mejora puede alcanzar 5-10x para tamaños de batch mayores.

### 5.3 NVIDIA Triton Inference Server

**Triton Inference Server** es la solución de NVIDIA para serving de modelos de IA en producción a escala. Sus características diferenciales respecto a FastAPI+Transformers son:

- **Batching dinámico**: agrupa automáticamente requests de diferentes clientes en un único batch para la GPU, maximizando el throughput.
- **Concurrent model execution**: ejecuta múltiples instancias del modelo en paralelo en la misma GPU.
- **Soporte multi-framework**: carga modelos PyTorch, TensorFlow, ONNX, TensorRT y modelos personalizados en C++/Python en el mismo servidor.
- **Gestión del ciclo de vida de modelos**: recarga en caliente de modelos sin reiniciar el servidor.
- **Métricas nativas**: expone métricas de latencia, throughput y utilización de GPU en formato Prometheus.

La configuración de un modelo en Triton requiere definir un fichero `config.pbtxt` que especifica el nombre del modelo, el backend, las dimensiones de los tensores de entrada y salida, y la configuración de batching:

```
name: "clasificador_sentimiento"
backend: "onnxruntime"
max_batch_size: 32

input [
  { name: "input_ids", data_type: TYPE_INT64, dims: [-1] },
  { name: "attention_mask", data_type: TYPE_INT64, dims: [-1] }
]

output [
  { name: "logits", data_type: TYPE_FP32, dims: [2] }
]

dynamic_batching {
  preferred_batch_size: [8, 16, 32]
  max_queue_delay_microseconds: 5000
}
```

### 5.4 Comparativa de opciones de serving

| Criterio | HF + FastAPI | ONNX Runtime | Triton Inference Server |
|---|---|---|---|
| Complejidad de despliegue | Baja | Media | Alta |
| Throughput en GPU | Bajo | Medio | Alto |
| Batching dinámico | No (manual) | Parcial | Nativo |
| Soporte multi-modelo | No nativo | No nativo | Sí |
| Métricas de producción | Manual | Manual | Prometheus nativo |
| Optimización hardware | Limitada | Media (EPs) | Alta (TensorRT) |
| Caso de uso típico | Prototipado, baja carga | Producción media | Producción a escala |

---

## 6. Optimización de inferencia de Transformers

### 6.1 Cuantización INT8

La cuantización reduce la precisión numérica de los pesos del modelo desde FP32 (32 bits) o FP16 (16 bits) a INT8 (8 bits entero), reduciendo el tamaño del modelo en memoria aproximadamente a la mitad y acelerando la inferencia en hardware que tiene soporte nativo para operaciones INT8 (Intel Ice Lake con VNNI, NVIDIA con Tensor Cores).

La cuantización puede aplicarse en dos modalidades:

- **Post-training quantization (PTQ)**: se aplica tras el entrenamiento, sin necesidad de reentrenar. Requiere un pequeño conjunto de datos de calibración (típicamente 100-1000 muestras representativas) para determinar los rangos de cuantización. Es la opción más rápida. Con ONNX Runtime y la librería `optimum`:

```python
from optimum.onnxruntime.configuration import AutoQuantizationConfig
from optimum.onnxruntime import ORTQuantizer

quantization_config = AutoQuantizationConfig.avx512_vnni(
    is_static=False,  # Cuantización dinámica (sin calibración)
    per_channel=True
)

quantizer = ORTQuantizer.from_pretrained("./modelo_onnx")
quantizer.quantize(
    save_dir="./modelo_int8",
    quantization_config=quantization_config
)
```

- **Quantization-aware training (QAT)**: simula la cuantización durante el entrenamiento, permitiendo al modelo adaptarse a la reducción de precisión. Produce modelos con menor degradación de precisión que PTQ, pero requiere reentrenamiento completo.

El impacto típico de la cuantización INT8 sobre modelos BERT en CPU: reducción de tamaño del 75%, mejora de latencia de 3-4x, degradación de F1 menor al 1% en la mayoría de tareas.

### 6.2 Knowledge Distillation

**Knowledge distillation** (Hinton et al., 2015) entrena un modelo más pequeño ("estudiante") para imitar las predicciones de un modelo más grande ("profesor"). En el contexto de PLN, el proceso consiste en:

1. Entrenar el modelo profesor (ej. BERT-large fine-tuneado).
2. Usar las distribuciones de probabilidad suavizadas ("soft targets") del profesor como señal de supervisión adicional para entrenar el estudiante.
3. La función de pérdida del estudiante combina la pérdida con las etiquetas reales (hard loss) y la divergencia KL respecto a las soft targets del profesor.

```python
# Función de pérdida combinada para knowledge distillation
import torch.nn.functional as F

def distillation_loss(student_logits, teacher_logits, true_labels,
                      temperature=4.0, alpha=0.7):
    # Soft loss: KL-divergencia contra predicciones suavizadas del profesor
    soft_loss = F.kl_div(
        F.log_softmax(student_logits / temperature, dim=-1),
        F.softmax(teacher_logits / temperature, dim=-1),
        reduction='batchmean'
    ) * (temperature ** 2)

    # Hard loss: cross-entropy con etiquetas reales
    hard_loss = F.cross_entropy(student_logits, true_labels)

    return alpha * soft_loss + (1 - alpha) * hard_loss
```

DistilBERT es el resultado más conocido de aplicar knowledge distillation a BERT. TinyBERT va más lejos distilando no solo las predicciones finales sino también las representaciones intermedias de las capas de atención.

### 6.3 Structured Pruning

El **pruning estructurado** elimina componentes completos del modelo (cabezas de atención, capas completas) en lugar de pesos individuales (pruning no estructurado). El pruning no estructurado produce matrices dispersas que son difíciles de acelerar en hardware convencional; el pruning estructurado produce modelos más pequeños que se benefician directamente de optimizaciones de álgebra lineal estándar.

La técnica más común para Transformers es el **movement pruning** y el pruning de cabezas de atención. Investigación de Voita et al. (2019) demostró que la mayoría de las cabezas de atención en BERT pueden eliminarse sin degradación significativa del rendimiento en downstream tasks: en muchos casos, 8 de las 12 cabezas de atención de una capa contribuyen marginalmente a las predicciones.

---

## 7. Procesamiento de voz

### 7.1 Reconocimiento automático del habla (ASR) con Whisper

**Whisper** (Radford et al., OpenAI, 2022) es un modelo ASR entrenado sobre 680.000 horas de audio de internet en 97 idiomas. Emplea una arquitectura encoder-decoder Transformer: el encoder procesa el espectrograma mel del audio, y el decoder genera la transcripción token a token. Sus características diferenciales son:

- **Robustez acústica**: entrenado con audio de diversas calidades y condiciones (ruido, acento, habla espontánea), muestra alta robustez comparado con modelos entrenados sobre datos limpios de laboratorio.
- **Multilingüe nativo**: puede transcribir directamente o traducir al inglés 96 idiomas.
- **Sin necesidad de adaptación**: funciona de forma competitiva en nuevos dominios sin fine-tuning, a diferencia de modelos anteriores como wav2vec 2.0 que requieren adaptación para cada dominio.

Whisper está disponible en cinco tamaños: tiny (39M), base (74M), small (244M), medium (769M) y large-v3 (1.5B). La elección del tamaño depende del trade-off entre WER (Word Error Rate) y latencia/coste.

```python
import whisper

model = whisper.load_model("medium")  # Carga el modelo medium

result = model.transcribe(
    "llamada_cliente.mp3",
    language="es",          # Forzar idioma (evita la detección automática)
    task="transcribe",      # "transcribe" o "translate" (al inglés)
    word_timestamps=True,   # Timestamps por palabra para subtítulos
    fp16=True               # Inferencia en FP16 para mayor velocidad en GPU
)

print(result["text"])
for segment in result["segments"]:
    print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}")
```

Para despliegue en producción, la implementación de referencia es **faster-whisper**, que utiliza CTranslate2 como backend y consigue hasta 4x de speedup respecto a la implementación original de Whisper con menor uso de VRAM.

### 7.2 Síntesis de voz (TTS)

Los sistemas TTS modernos basados en redes neuronales generan habla sintética de alta naturalidad a partir de texto. Las arquitecturas de referencia son:

- **FastSpeech 2**: genera el espectrograma mel en un solo paso (no autorregresivo), con control explícito de duración, tono y energía. Extremadamente rápido en inferencia.
- **VITS** (Variational Inference with adversarial learning for end-to-end Text-to-Speech): genera audio directamente desde texto en un modelo end-to-end, sin etapa separada de vocoder. Produce habla de alta naturalidad.
- **Bark** (Suno AI): modelo generativo de audio basado en Transformers que genera habla con variabilidad estilística (emociones, ritmo), aunque con mayor latencia.

Para sistemas en producción con restricción de latencia, FastSpeech 2 combinado con un vocoder HiFi-GAN es la elección más habitual por su velocidad de síntesis.

### 7.3 Speaker Diarization

La **diarización** de locutor (speaker diarization) es el proceso de segmentar y etiquetar un audio según qué locutor habla en cada instante: "¿quién habló cuándo?". Es componente crítico en el análisis de llamadas telefónicas y reuniones, donde la atribución correcta de cada fragmento de habla al locutor correspondiente es necesaria para el análisis posterior.

El pipeline estándar de diarización combina tres etapas:

1. **Voice Activity Detection (VAD)**: detecta los segmentos de audio con voz (vs. silencio o ruido de fondo). Silero VAD o los modelos de VAD de pyannote.audio son las referencias actuales.
2. **Segmentación**: divide los segmentos de voz en unidades homogéneas de locutor, detectando los puntos de cambio de interlocutor.
3. **Clustering**: agrupa los segmentos del mismo locutor mediante comparación de embeddings de speaker (x-vectors o d-vectors), usando algoritmos de clustering como agglomerative hierarchical clustering.

La librería **pyannote.audio** proporciona pipelines preentrenados que integran estas tres etapas:

```python
from pyannote.audio import Pipeline

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="hf_token"
)

diarization = pipeline("llamada.wav", num_speakers=2)

for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"[{turn.start:.1f}s - {turn.end:.1f}s] {speaker}")
```

### 7.4 Pipeline end-to-end voz-a-texto-a-acción

Un pipeline completo de procesamiento de voz para un caso de uso empresarial (ej. análisis automático de llamadas de call center) integra los siguientes componentes en secuencia:

```
[Audio de llamada]
        |
        v  VAD (Silero VAD) — elimina silencio
[Segmentos de voz]
        |
        v  Speaker Diarization (pyannote.audio)
[Segmentos etiquetados: AGENTE / CLIENTE]
        |
        v  ASR por segmento (faster-whisper)
[Transcripción con timestamps y locutor]
        |
        v  PLN (análisis de sentimiento, NER, extracción de temas)
[Análisis estructurado: sentimiento por turno, entidades, temas]
        |
        v  Resumen automático (BART/T5)
[Resumen de la llamada]
        |
        v  Almacenamiento en base de datos + dashboard BI
[Métricas de calidad del servicio, alertas automáticas]
```

La latencia total del pipeline para una llamada de 5 minutos en un servidor con GPU es típicamente de 60-120 segundos (12-24x más rápido que tiempo real), lo que permite el procesamiento de llamadas grabadas en modo batch con alta escala.

---

## 8. Métricas de evaluación

### 8.1 Métricas para clasificación y NER

**Precision, Recall y F1-score** son las métricas estándar para tareas de clasificación y NER:

- `Precision = TP / (TP + FP)`: de todas las predicciones positivas, qué fracción es correcta.
- `Recall = TP / (TP + FN)`: de todos los positivos reales, qué fracción fue detectada.
- `F1 = 2 × (Precision × Recall) / (Precision + Recall)`: media armónica, equilibra precision y recall.

Para clasificación multiclase, el F1 puede agregarse como:
- **F1 macro**: media no ponderada del F1 de cada clase. Trata a todas las clases por igual.
- **F1 micro**: calcula TP, FP, FN globales antes de calcular F1. Equivalente al accuracy en clasificación multiclase.
- **F1 weighted**: media ponderada por el soporte (número de ejemplos) de cada clase.

La elección entre macro y micro depende del caso de uso: si todas las clases son igualmente importantes (incluso las minoritarias), se usa macro; si el rendimiento global importa más que el equilibrio entre clases, se usa micro o weighted.

### 8.2 BLEU y ROUGE para generación de texto

**BLEU** (Bilingual Evaluation Understudy) evalúa la calidad de la traducción automática comparando n-gramas del texto generado con una o varias referencias humanas. BLEU-4 (que considera n-gramas de hasta 4 tokens) es el estándar en benchmarks de traducción. Un valor BLEU de 1.0 indica coincidencia perfecta con la referencia; valores superiores a 0.4 indican calidad competitiva. BLEU tiene limitaciones conocidas: no captura la calidad semántica si las palabras elegidas son sinónimas de la referencia, y penaliza las respuestas correctas pero con formulaciones diferentes a la referencia.

**ROUGE** (Recall-Oriented Understudy for Gisting Evaluation) evalúa resúmenes automáticos. Las variantes más usadas son:
- **ROUGE-1**: solapamiento de unigramas entre resumen generado y referencia.
- **ROUGE-2**: solapamiento de bigramas.
- **ROUGE-L**: longest common subsequence, captura la fluencia del resumen.

### 8.3 WER para ASR

**WER** (Word Error Rate) es la métrica estándar para evaluar sistemas ASR:

```
WER = (Sustituciones + Inserciones + Eliminaciones) / Total palabras referencia
```

Un WER de 0.05 (5%) se considera calidad muy alta para ASR en inglés en condiciones de habla limpia. El WER de Whisper-large-v3 es de aproximadamente 2.7% en el benchmark LibriSpeech test-clean (inglés). Para castellano en el benchmark Common Voice, Whisper-large-v3 alcanza WER < 5%.

### 8.4 Gestión de idiomas y dialectos

La variación lingüística es uno de los retos prácticos más importantes en sistemas PLN en producción para mercados hispanófonos. El español presenta diversidad dialectal significativa: variantes fonológicas (seseo, voseo, distintos patrones de entonación), vocabulario regional y diferencias morfosintácticas entre variedades de España, México, Argentina, Colombia, etc.

Las estrategias técnicas para gestionar esta diversidad incluyen:

- **Modelos multilingües con fine-tuning por variedad**: usar mBERT o XLM-RoBERTa como base y realizar fine-tuning específico sobre datos de la variedad objetivo.
- **Detección automática de variante**: añadir un clasificador de variedad dialectal como primera etapa del pipeline para rutear hacia el modelo más apropiado.
- **Datos aumentados por variedad**: para ASR, recopilar datos de las variedades relevantes usando herramientas como Common Voice de Mozilla.
- **Evaluación diferenciada por variedad**: reportar métricas separadas por variedad para detectar rendimiento degradado en variedades subrepresentadas.

---

## 9. Actividades prácticas

### Actividad 1 — Despliegue y benchmark de clasificación de texto

**Descripción**: A partir de un dataset de clasificación de reseñas de producto proporcionado por el formador (categorías: electrónica, ropa, hogar, alimentación), realiza fine-tuning de DistilBERT y BERT-base utilizando la librería Hugging Face Transformers. Despliega ambos modelos como endpoints REST con FastAPI. Implementa un script de benchmark que envíe requests concurrentes al servidor y mida: latencia p50, p95 y p99, throughput (requests/segundo) y uso de CPU/GPU. Exporta el modelo DistilBERT a ONNX y repite el benchmark. Presenta una tabla comparativa de los tres escenarios (DistilBERT PyTorch, BERT-base PyTorch, DistilBERT ONNX) con las métricas de rendimiento y de calidad (F1 macro en el conjunto de test).

**Entregable**: Notebook de fine-tuning + código del servidor FastAPI + script de benchmark + tabla comparativa con análisis.

**Criterios de evaluación**: Correcta implementación del fine-tuning y el serving, completitud y rigor del benchmark, análisis del trade-off rendimiento/calidad, justificación de la elección de modelo para producción.

---

### Actividad 2 — Optimización con cuantización INT8

**Descripción**: Partiendo del modelo BERT-base fine-tuneado en la actividad anterior, aplica cuantización dinámica INT8 utilizando ONNX Runtime y la librería Optimum. Mide el impacto de la cuantización en: tamaño del fichero del modelo, latencia de inferencia en CPU (sin GPU), consumo de memoria RAM y F1 en el conjunto de test. Aplica también cuantización estática (con conjunto de calibración) y compara los resultados. Documenta el procedimiento completo y proporciona una recomendación razonada sobre cuándo es aceptable la cuantización para este caso de uso.

**Entregable**: Notebook con el código de cuantización y mediciones + informe de análisis (dos páginas).

**Criterios de evaluación**: Correcta aplicación de PTQ dinámica y estática, rigor de las mediciones, análisis del impacto en precisión vs. eficiencia, calidad de la recomendación final.

---

### Actividad 3 — Pipeline de análisis de llamadas de call center

**Descripción**: Construye un pipeline end-to-end de análisis de llamadas de call center. El formador proporcionará tres archivos de audio de llamadas simuladas en castellano (duración 2-5 minutos cada una). El pipeline debe: (1) realizar la transcripción con Whisper medium o large; (2) separar los turnos de locutor con pyannote.audio; (3) aplicar análisis de sentimiento por turno de cliente; (4) extraer entidades relevantes (producto mencionado, reclamación, resolución); (5) generar un resumen de la llamada. Implementa el pipeline como un script Python con salida estructurada en JSON. Reporta el WER sobre la transcripción (el formador proporcionará la transcripción de referencia) y los tiempos de procesamiento de cada etapa.

**Entregable**: Código del pipeline + ficheros JSON de salida para las tres llamadas + informe de resultados con métricas.

**Criterios de evaluación**: Funcionalidad completa del pipeline, calidad de la transcripción (WER), corrección de la diarización, relevancia de las entidades extraídas y calidad del resumen.

---

### Actividad 4 — Evaluación multilingüe y gestión de dialectos

**Descripción**: Selecciona una tarea de clasificación de texto o análisis de sentimiento con datos en español. Descarga un conjunto de datos disponible en Hugging Face Hub que tenga etiquetas de variedad dialectal o procedencia geográfica (por ejemplo, variantes México/España/Argentina). Evalúa el rendimiento de un modelo fine-tuneado sobre datos españoles en los distintos subconjuntos dialectales. Identifica qué variedades presentan degradación de rendimiento. Propón y ejecuta al menos una estrategia de mitigación (fine-tuning adicional, aumentación de datos, ajuste del umbral de confianza). Compara el rendimiento antes y después de la mitigación.

**Entregable**: Notebook con el experimento + análisis de resultados diferenciado por variedad dialectal + propuesta de estrategia de producción.

**Criterios de evaluación**: Rigor del diseño experimental, claridad en la identificación de degradación por variedad, efectividad y justificación de la estrategia de mitigación.

---

## 10. Referencias

- **Hugging Face Transformers — Documentación oficial**: guía de uso, modelos disponibles, tareas soportadas y pipelines. Disponible en: [https://huggingface.co/docs/transformers/index](https://huggingface.co/docs/transformers/index)

- **BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding** (Devlin et al., 2018): artículo original. Disponible en: [https://arxiv.org/abs/1810.04805](https://arxiv.org/abs/1810.04805)

- **RoBERTa: A Robustly Optimized BERT Pretraining Approach** (Liu et al., 2019): artículo original. Disponible en: [https://arxiv.org/abs/1907.11692](https://arxiv.org/abs/1907.11692)

- **DistilBERT, a distilled version of BERT** (Sanh et al., 2019): artículo original. Disponible en: [https://arxiv.org/abs/1910.01108](https://arxiv.org/abs/1910.01108)

- **Whisper: Robust Speech Recognition via Large-Scale Weak Supervision** (Radford et al., OpenAI, 2022): artículo y repositorio oficial. Disponible en: [https://github.com/openai/whisper](https://github.com/openai/whisper) · Artículo: [https://arxiv.org/abs/2212.04356](https://arxiv.org/abs/2212.04356)

- **ONNX Runtime — Documentación oficial**: guía de optimización, Execution Providers y cuantización. Disponible en: [https://onnxruntime.ai/docs/](https://onnxruntime.ai/docs/)

- **Optimum — Librería de optimización de Hugging Face**: documentación de exportación a ONNX y cuantización. Disponible en: [https://huggingface.co/docs/optimum/index](https://huggingface.co/docs/optimum/index)

- **NVIDIA Triton Inference Server — Documentación oficial**: guía de configuración, batching dinámico y backends. Disponible en: [https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/index.html](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/index.html)

- **pyannote.audio — Librería de diarización**: documentación oficial y modelos preentrenados. Disponible en: [https://github.com/pyannote/pyannote-audio](https://github.com/pyannote/pyannote-audio)

- **faster-whisper — Implementación CTranslate2 de Whisper**: repositorio oficial con benchmarks de rendimiento. Disponible en: [https://github.com/SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper)

- **ROUGE: A Package for Automatic Evaluation of Summaries** (Lin, 2004): artículo original de la métrica ROUGE. Disponible en: [https://aclanthology.org/W04-1013/](https://aclanthology.org/W04-1013/)

- **Common Voice — Corpus de voz multilingüe de Mozilla**: datos de entrenamiento y evaluación para ASR multilingüe. Disponible en: [https://commonvoice.mozilla.org/es/datasets](https://commonvoice.mozilla.org/es/datasets)

---

*UD5 · MP03 Explotación de Servicios de Datos y Analítica · CFS2 Instalación, despliegue y explotación de sistemas de IA*
