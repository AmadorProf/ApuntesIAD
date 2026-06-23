---
marp: true
theme: default
paginate: true
size: 16:9
header: 'MP03 · Desarrollo de componentes para sistemas de ML'
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

# MP03 · Desarrollo de componentes para sistemas de ML

CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Ficha del módulo

| Campo | Valor |
|---|---|
| Código | **MP03** |
| Estándar de competencia | ECP2497_3 · Nivel 3 |
| Familia profesional | Inteligencia Artificial y Data |
| Duración | **200 h** |
| Curso | **2.º** |

> **Competencia que desarrolla:** desarrollar soluciones de aprendizaje automático de extremo a extremo, desde el diseño de *pipelines* de datos multimodales y la implementación de modelos robustos hasta su integración en producción, asegurando trazabilidad y actualización tecnológica.

---

## Estructura del módulo

| # | Unidad didáctica |
|---|---|
| **UD1** | Pipelines de datos para ML |
| **UD2** | Despliegue de modelos con frameworks especializados |
| **UD3** | Integración de modelos en aplicaciones |
| **UD4** | Validación de la calidad de los componentes |
| **UD5** | Protocolización y documentación técnica |
| **UD6** | Vigilancia tecnológica |
| **UD7** | Gestión integral: seguridad, sostenibilidad y ética |

---

<!-- _class: lead -->

# UD1
## Pipelines de datos para ML

---

## UD1 · Configuración del entorno de desarrollo

**Opciones de entorno:**

| Entorno | Cuándo usarlo |
|---|---|
| **Local** | Desarrollo inicial, datos sensibles, sin latencia de red |
| **Google Colab** | Prototipado rápido, acceso a GPU gratuita |
| **Nube (SageMaker, Vertex AI)** | Escala, colaboración, producción |

**Gestión de dependencias:**
- `pip` + `requirements.txt` para proyectos simples
- `conda` + `environment.yml` para entornos científicos
- **Contenedores Docker** para reproducibilidad total entre entornos

---

## UD1 · Ingesta de datos multimodal

| Tipo de dato | Librerías principales | Formato habitual |
|---|---|---|
| **Tabular** | Pandas, Polars | CSV, Parquet, SQL |
| **Imagen** | Pillow, OpenCV, Torchvision | JPEG, PNG, TIFF |
| **Texto** | NLTK, spaCy, HuggingFace | TXT, JSON, HTML |
| **Audio** | Librosa, torchaudio | WAV, MP3, FLAC |
| **Vídeo** | OpenCV, decord | MP4, AVI |
| **Series temporales** | Pandas, tslearn | CSV, Parquet |

**Fuentes:** ficheros locales · bases de datos · APIs REST · *streaming*

---

## UD1 · Reproducibilidad y trazabilidad del pipeline

**Control de versiones del código y los datos:**

```bash
# Versionado del código
git init && git add . && git commit -m "feat: pipeline inicial"

# Versionado de datos con DVC
dvc init
dvc add data/raw/dataset.csv
dvc push
```

**Buenas prácticas:**
- Separar etapas del pipeline en funciones/clases reutilizables
- Registrar parámetros de cada paso (versión, fecha, origen)
- Generar el mismo output dado el mismo input (idempotencia)

---

<!-- _class: lead -->

# UD2
## Despliegue de modelos con frameworks especializados

---

## UD2 · Selección de arquitectura por tipo de dato

| Tipo de dato | Arquitectura recomendada | Framework |
|---|---|---|
| **Tabular** | Gradient Boosting, MLP | Sklearn, XGBoost, LightGBM |
| **Imagen** | CNN, ViT, ResNet | PyTorch, TensorFlow |
| **Vídeo** | 3D-CNN, VideoTransformer | PyTorch |
| **Audio** | CNN sobre espectrogramas, Wav2Vec | torchaudio |
| **Texto** | Transformer, BERT, RoBERTa | HuggingFace |
| **Series temporales** | LSTM, TCN, TFT | PyTorch, Darts |

---

## UD2 · Buenas prácticas de programación

**Control de errores y robustez:**
```python
try:
    prediccion = modelo.predict(entrada)
except ValueError as e:
    logging.error(f"Entrada inválida: {e}")
    raise
except RuntimeError as e:
    logging.error(f"Error de inferencia: {e}")
    raise
```

**Reutilización y mantenibilidad:**
- Componentes modulares: preprocesador · modelo · posprocesador
- Control de versiones con ramas (*feature*, *main*, *release*)
- Aislamiento: entornos virtuales o contenedores por proyecto
- Documentación de interfaces y contratos de datos

---

<!-- _class: lead -->

# UD3
## Integración de modelos en aplicaciones

---

## UD3 · Exportación y estandarización del modelo

**Hacia la portabilidad:**

| Formato | Descripción | Compatibilidad |
|---|---|---|
| **ONNX** | Intercambio universal entre frameworks | Muy alta |
| **TorchScript** | Serialización de PyTorch | Python/C++ |
| **TF SavedModel** | Modelo completo TensorFlow | TF Serving, TFLite |
| **PMML** | ML clásico, XML | Java, R, Python |

**API de inferencia:**
- Exponer el modelo como servicio REST: FastAPI, Flask
- Servicio gRPC para baja latencia: TF Serving, Triton
- Integración en pipelines: BentoML, Seldon, MLflow

---

## UD3 · Arquitecturas de redes neuronales avanzadas

**Redes según la naturaleza del problema:**

| Red | Tipo de dato | Mecanismo clave |
|---|---|---|
| **MLP** (Perceptrón multicapa) | Tabular, no lineal | Capas densas + activaciones |
| **CNN** (Convolucional) | Imagen, audio | Kernels, pooling, jerarquía espacial |
| **RNN / LSTM / GRU** | Secuencias, texto | Memoria de estado, puertas |
| **Transformer** | Texto, imagen, multimodal | Atención multi-cabeza |
| **GNN** | Grafos, redes | Paso de mensajes entre nodos |
| **Autoencoder** | Compresión, detección de anomalías | Codificación-decodificación |

---

<!-- _class: lead -->

# UD4
## Validación de la calidad de los componentes

---

## UD4 · Verificación del pipeline

**Checklist de validación del pipeline:**

- ✅ Las transformaciones se aplican sin errores ni sesgos introducidos
- ✅ El formato de los datos es consistente entre etapas
- ✅ Los mismos datos de entrada producen los mismos outputs (idempotencia)
- ✅ No existe contaminación entre particiones de entrenamiento y test
- ✅ Las etiquetas y anotaciones son coherentes tras el proceso

**Metodología KDD:**
- Knowledge Discovery in Databases: selección → preprocesamiento → transformación → minería → evaluación

---

## UD4 · Algoritmos clásicos de ML

| Algoritmo | Tipo | Ventajas |
|---|---|---|
| **Regresión lineal / logística** | Supervisado | Interpretable, rápido |
| **Árbol de decisión** | Supervisado | Visualizable, sin normalización |
| **Random Forest** | Ensemble | Robusto, maneja ruido |
| **SVM** | Supervisado | Efectivo en alta dimensionalidad |
| **Gradient Boosting** (XGBoost, LightGBM) | Ensemble | Estado del arte en tabular |
| **K-Means** | No supervisado | Clustering simple y escalable |

---

## UD4 · Análisis de sesgos y *fairness*

**Sesgos a detectar:**
- **Sesgo de representación:** colectivos subrepresentados en el entrenamiento
- **Sesgo de medición:** errores sistemáticos en la recogida de datos
- **Sesgo histórico:** patrones discriminatorios heredados de los datos

**Herramientas de *fairness*:**
- `Fairlearn` (Microsoft): métricas y mitigación de sesgos
- `AI Fairness 360` (IBM): amplio catálogo de técnicas
- `What-If Tool` (Google): exploración visual de sesgos

**Métricas:** demographic parity · equalized odds · individual fairness

---

<!-- _class: lead -->

# UD5
## Protocolización y documentación técnica

---

## UD5 · Control de versiones y documentación

**Git como herramienta central:**

```bash
# Flujo de trabajo estándar
git checkout -b feature/nuevo-pipeline
# ... desarrollo ...
git add src/pipeline.py
git commit -m "feat: añadir etapa de normalización al pipeline"
git push origin feature/nuevo-pipeline
# Pull request → revisión → merge a main
```

**Qué documentar en el código:**
- Arquitectura del pipeline y sus dependencias
- Lógica de diseño no obvia en comentarios concisos
- Contratos de datos: tipos esperados, rangos, restricciones

---

## UD5 · Model Card y empaquetado

**Ficha técnica del modelo (*Model Card*):**
- Métricas en test: accuracy, F1, AUC, RMSE…
- Datos de entrenamiento: fuente, versión, limitaciones
- Limitaciones y casos de uso inadecuados
- Responsable técnico y fecha de última evaluación

**Pruebas unitarias y de regresión:**
```python
def test_pipeline_output_shape():
    output = pipeline.transform(sample_input)
    assert output.shape == (100, 15), "Shape inesperado"

def test_pipeline_no_nulls():
    output = pipeline.transform(sample_input)
    assert output.isnull().sum().sum() == 0
```

---

<!-- _class: lead -->

# UD6
## Vigilancia tecnológica

---

## UD6 · Fuentes y metodología de vigilancia

**Fuentes de referencia:**

| Fuente | Tipo de contenido |
|---|---|
| **Papers with Code** | Papers + código + benchmarks actualizados |
| **arXiv (cs.LG, cs.AI)** | Preprints de investigación punta |
| **HuggingFace Hub** | Modelos, datasets, spaces en producción |
| **Blogs técnicos** | Google AI, Meta AI, OpenAI, DeepMind |
| **Conferencias** | NeurIPS, ICML, ICLR, CVPR |

**Metodología:** monitorizar → recopilar → analizar → evaluar aplicabilidad → transferir al equipo

---

## UD6 · Evaluación y transferencia de hallazgos

**Proceso de evaluación de una novedad:**

1. **Pertinencia:** ¿aplica al problema que estamos resolviendo?
2. **Madurez:** ¿es código estable o un prototipo de laboratorio?
3. **Coste de adopción:** tiempo de integración, dependencias, licencia
4. **Impacto esperado:** mejora en métricas, reducción de coste, mantenibilidad

**Transferencia al equipo:**
- Informe técnico resumido (máx. 1 página)
- Prueba de concepto comparada con la solución actual
- Presentación en sesión de revisión técnica del equipo

---

<!-- _class: lead -->

# UD7
## Gestión integral: seguridad, sostenibilidad y ética

---

## UD7 · Green AI y protección de datos

**Paradigma Green AI:**
- Minimizar el consumo energético en entrenamiento e inferencia
- Preferir modelos más pequeños y eficientes cuando el rendimiento es suficiente
- Reutilizar modelos preentrenados frente a entrenar desde cero
- Medir y reportar la huella de carbono (`codecarbon`, `carbontracker`)

**Protección de datos y privacidad por diseño:**
- Minimizar el acceso a datos personales durante el desarrollo
- Aplicar anonimización o seudonimización antes de cualquier experimento
- Controlar quién accede a los conjuntos de datos y con qué finalidad

---

## UD7 · Seguridad y bienestar profesional

**Seguridad en el desarrollo:**
- No incluir credenciales en el código (usar variables de entorno o *vaults*)
- Proteger los artefactos del modelo contra acceso no autorizado
- Mantener las dependencias actualizadas y sin vulnerabilidades conocidas

**Bienestar profesional:**

| Riesgo | Medida |
|---|---|
| Tecnoestrés | Límites de trabajo, desconexión programada |
| Ergonomía física | EPI específicos, mobiliario ajustable |
| Fatiga cognitiva | Documentación como apoyo a la memoria |

**Plan de emergencias:** conocer y aplicar el protocolo del centro.

---

## Criterios de evaluación — MP03

- Implementa procesos de ingesta multimodal y versiona el pipeline
- Despliega modelos según el tipo de dato con control de errores
- Gestiona dependencias y control de versiones con Git
- Expone el modelo mediante API y selecciona la arquitectura correcta
- Verifica el pipeline y la reproducibilidad; evalúa sesgos y robustez
- Protocoliza con control de versiones y elabora la *model card*
- Monitoriza fuentes tecnológicas y comparte hallazgos con el equipo
- Aplica criterios de *Green AI* y garantiza protección de datos

---

<!-- _class: lead -->

# MP03 · Desarrollo de componentes para sistemas de ML

**200 h · Curso 2.º · ECP2497_3 · Nivel 3**

*CFS — Gestión de datos y entrenamiento IA (IAD)*
