---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD5 · Procesamiento de lenguaje natural y voz | MP03 · Explotación de servicios de datos y analítica'
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

# UD5 · Procesamiento de lenguaje natural y voz

**MP03 — Explotación de servicios de datos y analítica**
Apuntes de IA y Datos

---

## Objetivos de la unidad

Al finalizar esta unidad el alumnado será capaz de:

- Adquirir, segmentar y cargar grabaciones de audio para su procesamiento.
- Configurar y explotar servicios de transcripción automática (ASR) con parámetros adecuados.
- Aplicar modelos de entendimiento del lenguaje natural (NLU): análisis de sentimiento, resumen, extracción de entidades y análisis de temas.
- Almacenar los resultados de forma estructurada para su explotación posterior.
- Tratar los datos de texto y voz conforme a la normativa de protección de datos y ética de la IA.

> **Resultado de aprendizaje:** Procesa documentos de lenguaje natural en formato sonoro o escrito para extraer conocimiento.

---

## Contexto: el pipeline de voz y texto

### El flujo completo de procesamiento

```
[Fuente de audio o texto]
        |
        v
[Preprocesamiento de audio]     (solo si la entrada es voz)
        |
        v
[Transcripción ASR]             (voz a texto)
        |
        v
[Análisis NLU]                  (extracción de conocimiento del texto)
        |
        v
[Almacenamiento y explotación]  (BD, dashboard, API)
```

### Casos de uso empresariales

- Análisis de llamadas de atención al cliente (call center analytics).
- Minería de opiniones en redes sociales y reseñas de productos.
- Extracción de entidades de contratos y documentos jurídicos.
- Resumen automático de reuniones y actas.
- Clasificación de tickets de soporte técnico.

---

## Preprocesamiento de grabaciones de audio

Antes de enviar el audio al servicio de transcripción, es necesario prepararlo.

### Formatos de audio y compatibilidad

| Formato | Codec | Compatibilidad ASR |
|---|---|---|
| WAV | PCM sin compresión | Universal; calidad máxima |
| MP3 | MPEG-1 Audio Layer 3 | Ampliamente soportado |
| FLAC | Lossless comprimido | Soportado por la mayoría; mejor que MP3 |
| OGG/Opus | Opus codec | WebRTC; buena calidad a bajo bitrate |
| M4A / AAC | Advanced Audio Coding | Habitual en dispositivos Apple |

### Parámetros de calidad mínimos para ASR

- **Frecuencia de muestreo:** 16.000 Hz (16 kHz) como mínimo; 44.100 Hz para calidad óptima.
- **Canales:** mono preferible para transcripción; estéreo si se quiere diarización por canal.
- **Bitrate:** mínimo 128 kbps para MP3.

---

## Preprocesamiento — Segmentación y limpieza de audio

### Segmentación de grabaciones largas

Las grabaciones largas (reuniones, llamadas) deben segmentarse antes de la transcripción:

- **Por duración fija:** segmentos de 30, 60 o 120 segundos (útil para batch processing).
- **Por silencio (Voice Activity Detection - VAD):** segmentar en los silencios naturales del habla.
- **Por locutor (diarización):** separar quién habla en cada momento.

### Limpieza de audio

| Problema | Técnica de limpieza |
|---|---|
| Ruido de fondo | Reducción de ruido espectral (SoX, noisereduce) |
| Eco o reverberación | Deconvolución o supresión de eco |
| Silencio al inicio/final | Recorte automático (trimming) |
| Normalización de volumen | Normalización RMS o de pico |

### Herramientas

`ffmpeg`, `pydub`, `librosa`, `SoX`, `pyannote.audio` (diarización).

---

## Transcripción automática — Servicios ASR

### Comparativa de servicios de transcripción

| Servicio | Proveedor | Idiomas | Capacidades especiales |
|---|---|---|---|
| **Whisper** | OpenAI (OSS) | 99 idiomas | Offline; robusto con acentos; diarización opcional |
| **Azure Speech** | Microsoft | 100+ idiomas | Tiempo real y batch; diarización; palabras personalizadas |
| **Google STT** | Google Cloud | 125 idiomas | Puntuación automática; modelo telefónico; streaming |
| **Amazon Transcribe** | AWS | 75+ idiomas | Identificación de locutores; vocabulario personalizado |
| **AssemblyAI** | AssemblyAI | 50+ idiomas | Diarización, resumen y análisis integrados |

### Whisper — transcripción local

```python
import whisper
model = whisper.load_model("medium")
result = model.transcribe("grabacion.wav", language="es")
print(result["text"])
```

---

## Transcripción — Parámetros de configuración

### Parámetros clave del servicio ASR

| Parámetro | Descripción | Ejemplo |
|---|---|---|
| **Idioma** | Idioma principal de la grabación | `es-ES`, `es-419` (latinoamérica) |
| **Modelo** | Velocidad vs. precisión | `whisper-large-v3`, `tiny`, `base` |
| **Diarización** | ¿Identificar quién habla? | `true` / `false` |
| **Puntuación automática** | Añadir signos de puntuación | `true` (por defecto en Azure/Google) |
| **Vocabulario personalizado** | Términos técnicos o nombres propios del dominio | Lista de siglas, marcas, nombres |
| **Filtro de profanidades** | Censurar palabras inapropiadas | `true` en contextos de atención al cliente |
| **Timestamps** | Añadir marcas temporales por palabra | A nivel de palabra o de segmento |

### Límites de capacidad

- Tamaño máximo de fichero (Whisper: sin límite con segmentación; Azure: 1 GB por fichero batch).
- Duración máxima por llamada a la API (Google STT sync: 60 segundos; async: sin límite).
- Tasa de llamadas (rate limits): verificar cuota del plan contratado.

---

## Modelos NLU — Análisis de sentimiento

El análisis de sentimiento clasifica el tono emocional del texto.

### Granularidades del análisis

| Nivel | Descripción | Ejemplo |
|---|---|---|
| **Documento** | Sentimiento global del texto | Reseña "muy positiva" |
| **Párrafo** | Sentimiento por sección | Introducción positiva, conclusión negativa |
| **Oración** | Sentimiento por frase | Identificar cambios de tono |
| **Aspecto (ABSA)** | Sentimiento por tema mencionado | "La velocidad es excelente pero el precio es caro" |

### Herramientas y servicios

- **Azure Language / Cognitive Services:** análisis de sentimiento con puntuación 0–1 por polaridad.
- **Google Natural Language API:** entidades + sentimiento + sintaxis en una sola llamada.
- **Hugging Face Transformers:** modelos BERT, RoBERTa, XLM-R fine-tuned para sentimiento en español.
- **VADER:** léxico basado en reglas; rápido pero solo en inglés.

---

## Modelos NLU — Resumen automático

El resumen automático condensa documentos largos en versiones más breves.

### Tipos de resumen

| Tipo | Descripción | Ventaja |
|---|---|---|
| **Extractivo** | Selecciona las frases más representativas del original | Mantiene el texto original; no alucina |
| **Abstractivo** | Genera texto nuevo que resume el contenido | Más natural; puede combinar ideas |

### Herramientas

- **Azure OpenAI / GPT-4:** resumen abstractivo de alta calidad; multilingüe.
- **Hugging Face (BART, T5, mT5):** modelos open source para resumen.
- **LangChain + LLM:** cadenas de resumen para documentos muy largos (map-reduce, refine).
- **Sumy:** resumen extractivo en Python; no requiere GPU.

### Caso de uso real

Resumen automático de actas de reuniones: de 45 minutos de transcripción a un resumen ejecutivo de 5 puntos de acción.

---

## Modelos NLU — Extracción de entidades (NER)

El reconocimiento de entidades nombradas (NER) identifica menciones de personas, organizaciones, lugares, fechas, importes y otros tipos en el texto.

### Tipos de entidades habituales

| Tipo | Ejemplo | Símbolo |
|---|---|---|
| Persona | "Ana García", "el director general" | PER |
| Organización | "Banco Santander", "Ministerio de Hacienda" | ORG |
| Lugar | "Madrid", "Zona Industrial Norte" | LOC |
| Fecha | "el 15 de enero de 2025", "el próximo trimestre" | DATE |
| Importe | "250.000 euros", "3,5 millones" | MONEY |
| Producto | "iPhone 16", "contrato de arrendamiento" | PROD |

### Herramientas para NER en español

- **spaCy** con modelo `es_core_news_lg`: NER para español de alta precisión.
- **Azure Language / Custom NER:** permite entrenar entidades personalizadas del dominio.
- **Hugging Face (XLM-RoBERTa, BETO):** NER con transformers en español.

---

## Modelos NLU — Análisis de temas

El análisis de temas descubre los temas principales en una colección de documentos sin supervisión.

### Técnicas principales

| Técnica | Descripción | Adecuada para |
|---|---|---|
| **LDA** (Latent Dirichlet Allocation) | Modelo probabilístico de temas | Corpus grande, enfoque estadístico |
| **NMF** (Non-Negative Matrix Factorization) | Factorización matricial | Corpus disperso |
| **BERTopic** | Clustering de embeddings BERT + LDA | Corpus pequeño-mediano; alta calidad |
| **Top2Vec** | Vectoriza documentos y agrupa por similitud | No requiere número de temas a priori |

### Ejemplo de aplicación: análisis de tickets de soporte

Un corpus de 10.000 tickets de soporte técnico procesado con BERTopic puede revelar automáticamente los 15 temas más frecuentes (p. ej., "problemas de inicio de sesión", "facturación incorrecta", "lentitud de la aplicación"), lo que guía la priorización del equipo de producto.

---

## Almacenamiento de resultados para explotación

Los resultados del NLU deben almacenarse de forma estructurada para su uso posterior.

### Esquema de almacenamiento recomendado

```json
{
  "id_documento": "CALL-20250115-001",
  "fecha_procesamiento": "2025-01-15T14:32:00Z",
  "transcripcion": "Buenos días, llamo porque mi factura...",
  "sentimiento": { "positivo": 0.12, "neutro": 0.38, "negativo": 0.50 },
  "entidades": [
    { "texto": "enero", "tipo": "DATE" },
    { "texto": "250 euros", "tipo": "MONEY" }
  ],
  "temas": ["facturacion", "reclamacion"],
  "resumen": "El cliente reclama un cargo incorrecto de 250 euros en la factura de enero."
}
```

### Destinos de almacenamiento

- Base de datos NoSQL (MongoDB, Cosmos DB) para documentos JSON.
- Data warehouse (BigQuery, Snowflake) para análisis agregado.
- Motor de búsqueda (Elasticsearch, Azure Cognitive Search) para búsqueda semántica.

---

## Protección de datos de texto y voz

### Marco normativo

| Normativa | Implicación para NLP/ASR |
|---|---|
| **RGPD Art. 6** | Se necesita base legal para procesar datos de voz y texto personal |
| **RGPD Art. 13/14** | Informar al interlocutor de que la llamada se graba y procesa |
| **LOPDGDD** | Aplicación española; registro de actividades de tratamiento obligatorio |
| **Reglamento de IA UE (Art. 50)** | Obligación de transparencia cuando se usa IA en interacción con personas |

### Medidas técnicas obligatorias

- **Información y consentimiento:** avisar al inicio de la grabación: "Esta llamada puede ser grabada para control de calidad y análisis por IA".
- **Minimización:** no transcribir más de lo necesario; eliminar grabaciones tras el plazo definido.
- **Control de acceso:** acceso a transcripciones restringido por roles.
- **Anonimización:** reemplazar nombres, DNI, IBAN, teléfonos en las transcripciones antes de análisis masivo.

---

## Prevención de sesgos en ASR y NLU

Los modelos de lenguaje pueden mostrar rendimiento desigual en distintos grupos.

### Sesgos documentados en ASR

| Tipo de sesgo | Descripción | Mitigación |
|---|---|---|
| **Acento y dialecto** | Peor reconocimiento en acentos no representados en el entrenamiento | Elegir modelos multilingües; evaluar con datos propios |
| **Género** | Algunos modelos tienen mejor rendimiento en voces masculinas | Evaluar métricas por género; reportar si hay diferencias |
| **Ruido de entorno** | Peor rendimiento en entornos ruidosos | Preprocesamiento; modelos robustos al ruido |
| **Terminología técnica** | Palabras del dominio no reconocidas | Vocabulario personalizado |

### Evaluación de equidad

Antes de desplegar en producción, evaluar la tasa de error (WER) por subgrupo y documentar si existe disparidad significativa. Si la hay, reportarlo como aviso técnico.

---

## Actividad práctica — UD5

### "Análisis de llamadas de atención al cliente en una aseguradora"

**Escenario:** La aseguradora Mutua Segura S.A. recibe 500 llamadas diarias al centro de atención. Quiere analizar el sentimiento, extraer entidades clave (importes, fechas, productos) y detectar los temas más frecuentes de reclamación.

**Tareas:**

1. Preprocesar 50 grabaciones de muestra (MP3 de 2-5 min): normalizar a 16 kHz mono, segmentar por silencio con VAD.
2. Transcribir con Whisper medium (en español). Medir el WER sobre 5 grabaciones con transcripción manual de referencia.
3. Aplicar NER con spaCy `es_core_news_lg`: extraer PER, ORG, DATE, MONEY. Almacenar en JSON estructurado.
4. Análisis de sentimiento con Azure Language: obtener puntuación positivo/neutro/negativo por llamada.
5. Análisis de temas con BERTopic sobre las 50 transcripciones. Identificar los 5 temas principales.
6. Anonimizar los PER y MONEY antes de cargar en la base de datos. Documentar las medidas en el registro de tratamiento.

**Entregable:** Pipeline documentado + JSON de resultados de 10 llamadas + registro de tratamiento de datos.

---

## Puntos clave — UD5

- El pipeline de voz y texto sigue cuatro fases: preprocesamiento de audio, transcripción ASR, análisis NLU y almacenamiento.
- El preprocesamiento de audio incluye conversión de formato, normalización, segmentación por silencio y diarización.
- Los principales servicios ASR son Whisper (open source), Azure Speech, Google STT y Amazon Transcribe.
- Las tareas NLU cubren: **análisis de sentimiento**, **resumen automático** (extractivo o abstractivo), **NER** y **análisis de temas**.
- Los resultados deben almacenarse en formato estructurado (JSON, tabla) para su explotación en BI o motores de búsqueda.
- Las grabaciones y transcripciones son datos personales: requieren **información previa**, **base legal**, **minimización** y **control de acceso**.
- Los modelos ASR y NLU pueden tener **sesgos** por acento, género o dominio; evaluarlos antes del despliegue.

---

## Criterios de evaluación — UD5

| Criterio | Indicador de logro |
|---|---|
| Preprocesa grabaciones | Convierte, normaliza y segmenta el audio correctamente antes de la transcripción |
| Explota el servicio ASR | Configura los parámetros del servicio y obtiene transcripciones de calidad verificada (WER) |
| Aplica modelos NLU | Ejecuta al menos dos tareas NLU (sentimiento, NER, resumen o temas) sobre los textos |
| Almacena resultados estructurados | Guarda los resultados en formato estructurado (JSON / tabla) apto para explotación |
| Trata datos según normativa | Informa, obtiene base legal, anonimiza y controla el acceso conforme al RGPD |
| Evalúa sesgos | Identifica y documenta posibles sesgos del modelo ASR o NLU en el dominio del proyecto |

---

<!-- _class: lead -->

[← Volver a MP03](../index.md)


---

<!-- nav-slide -->

## Navegación

[← UD4 · Visión artificial sobre imáge…](../UD4_Vision-artificial-imagen-video/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD6 · Inteligencia de negocio y ana… →](../UD6_Inteligencia-negocio-analitica/)
