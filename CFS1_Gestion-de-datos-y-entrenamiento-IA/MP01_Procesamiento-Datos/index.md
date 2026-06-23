---
marp: true
theme: default
paginate: true
size: 16:9
header: 'MP01 · Procesamiento de datos para IA'
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
</style>

<!-- _class: lead -->

# MP01 · Procesamiento de datos para IA

CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Ficha del módulo

| Campo | Valor |
|---|---|
| Código | **MP01** |
| Estándar de competencia | ECP2492_3 · Nivel 3 |
| Familia profesional | Inteligencia Artificial y Data |
| Duración | **200 h** |
| Curso | **1.º** |

> **Competencia que desarrolla:** procesar los datos del dominio mediante extracción, saneamiento y validación para garantizar su calidad y trazabilidad, seleccionar atributos clave y configurar conjuntos óptimos que aseguren la eficiencia algorítmica y el cumplimiento normativo.

---

## Estructura del módulo

| # | Unidad didáctica |
|---|---|
| **UD1** | Extracción de datos desde las fuentes |
| **UD2** | Exploración y análisis del conjunto de datos |
| **UD3** | Verificación de la calidad de los datos |
| **UD4** | Preprocesamiento y partición de datos |
| **UD5** | Gestión, versionado y cumplimiento normativo |
| **UD6** | Trabajo responsable, sostenible y PRL |

---

<!-- _class: lead -->

# UD1
## Extracción de datos desde las fuentes

---

## UD1 · Tipología de fuentes de datos

| Tipo de fuente | Ejemplos |
|---|---|
| Sistemas de almacenamiento | Bases de datos SQL/NoSQL, data lakes, data warehouses |
| IoT y embebidos | Sensores, PLCs, plataformas de telemetría |
| Streaming | Apache Kafka, AWS Kinesis, MQTT |
| APIs y servicios web | REST, GraphQL, webhooks, OData |
| Repositorios documentales | Gestores de documentos, portales de datos abiertos |

> Cada fuente tiene su propio **protocolo de acceso**, **formato** y **condiciones de uso**.

---

## UD1 · Naturaleza del dato

| Tipo | Estructura | Formatos comunes |
|---|---|---|
| **Estructurado** | Esquema fijo, tabular | CSV, SQL, Parquet, Excel |
| **Semiestructurado** | Esquema flexible | JSON, XML, YAML, Avro |
| **No estructurado** | Sin esquema | Texto libre, imágenes, audio, vídeo |
| **Multimodal** | Combinación de tipos | Informe + imagen + audio |

**Factores de caracterización:** formato · frecuencia de actualización · volumen · variedad · velocidad

---

## UD1 · Condiciones de acceso y filtrado

**Verificar antes de extraer:**

- ✅ Disponibilidad y estabilidad de la fuente
- ✅ Licencia y uso permitido de los datos
- ✅ Presencia de datos personales o sensibles (RGPD)
- ✅ Restricciones legales o contractuales

**Configuración de la extracción:**
- Filtros, consultas y criterios de selección por volumen, calidad y variedad
- Procesamiento cercano a la fuente *(edge processing)* para eficiencia
- Reducción de uso de CPU y memoria mediante selección anticipada de atributos

---

## UD1 · Trazabilidad desde el origen

**Metadatos mínimos a registrar en cada extracción:**

| Metadato | Contenido |
|---|---|
| Procedencia | URL, tabla, servicio o sistema de origen |
| Fecha/hora | Timestamp de la extracción |
| Formato | Tipo y versión del formato del archivo |
| Versión | Identificador único de la extracción |
| Restricciones | Licencia, uso permitido, datos sensibles |

**Documentar:** fuentes, mecanismos de acceso, periodicidad, incidencias detectadas.

---

<!-- _class: lead -->

# UD2
## Exploración y análisis del conjunto de datos

---

## UD2 · Análisis exploratorio (EDA)

**Qué examinar:**

- **Estructura:** entidades, variables, tipos de dato, volumetrías
- **Distribuciones:** histogramas, boxplots, frecuencias relativas
- **Correlaciones:** matrices de correlación, scatter plots, heatmaps
- **Valores atípicos:** outliers estadísticos, anomalías de dominio
- **Patrones:** tendencias, estacionalidad, ciclos, relaciones no lineales

**Herramientas frecuentes:** Pandas · Pandas Profiling · Sweetviz · Seaborn · Matplotlib

---

## UD2 · Evaluación de idoneidad y calidad inicial

**Preguntas clave antes del modelado:**

- ¿Los datos son **representativos** del problema real?
- ¿Existen **sesgos de selección** o de cobertura geográfica/temporal?
- ¿Los datos cubren todos los **casos de uso** previstos?
- ¿Están los datos bien **etiquetados o anotados**?

**Problemas de calidad a detectar en esta fase:**
- Datos incompletos o con valores ausentes masivos
- Inconsistencias entre fuentes combinadas
- Duplicidades de registros
- Errores o ambigüedades en los criterios de etiquetado

---

<!-- _class: lead -->

# UD3
## Verificación de la calidad de los datos

---

## UD3 · Dimensiones y técnicas de calidad

| Dimensión | Qué medir | Método / herramienta |
|---|---|---|
| **Cobertura** | % de valores nulos por campo | `isnull()`, `.info()` |
| **Distribución** | Histogramas, percentiles, asimetría | Scipy, Seaborn |
| **Equilibrio de clases** | Frecuencia relativa por clase | `value_counts()` |
| **Outliers** | IQR, Z-score, Isolation Forest | Sklearn |
| **Duplicidades** | Registros idénticos o casi idénticos | `duplicated()` |
| **Consistencia** | Coherencia entre campos relacionados | Reglas de negocio |

---

## UD3 · Equidad y fiabilidad del conjunto

**Riesgos que pueden sesgar el modelo:**

- **Desbalance de clases:** una clase muy dominante sobre las demás
- **Subrepresentación:** colectivos o escenarios poco presentes en los datos
- **Variables sensibles:** atributos protegidos (género, edad, etnia, origen)
- **Data leakage:** información futura que contamina el conjunto de entrenamiento

**Verificación de etiquetas y anotaciones:**
- Coherencia entre anotadores *(inter-annotator agreement)*
- Detección de errores, ambigüedades y etiquetas contradictorias
- Protocolos de revisión cruzada antes del preprocesamiento

---

<!-- _class: lead -->

# UD4
## Preprocesamiento y partición de datos

---

## UD4 · Pipeline de depuración y transformación

1. **Selección** de atributos relevantes según el diseño del modelo
2. **Depuración:** valores ausentes · errores · inconsistencias · duplicados · formatos incorrectos
3. **Transformaciones:**
   - Normalización y reescalado (MinMaxScaler, StandardScaler)
   - Balanceo de clases (oversampling, undersampling, SMOTE)
   - Reducción de dimensionalidad (PCA, t-SNE, UMAP)
   - Codificación de variables categóricas (One-Hot, Label, Target Encoding)
4. **Enriquecimiento:** nuevas variables derivadas o fuentes externas complementarias

---

## UD4 · Partición del conjunto

| Partición | Proporción típica | Uso |
|---|---|---|
| **Entrenamiento** | 70–80 % | Ajuste de pesos del modelo |
| **Validación** | 10–15 % | Selección de hiperparámetros |
| **Test** | 10–20 % | Evaluación final sin sesgo |

**Estrategias de muestreo:**
- **Aleatorio simple:** para datos independientes e idénticamente distribuidos
- **Estratificado:** preserva la distribución de clases en cada partición
- **Temporal:** para series temporales (sin mezclar pasado y futuro)
- **Por grupos:** evita fugas entre registros relacionados (mismo paciente, empresa…)

> **Sostenibilidad:** configurar conjuntos que minimizan ciclos de cómputo y emisiones CO₂.

---

<!-- _class: lead -->

# UD5
## Gestión, versionado y cumplimiento normativo

---

## UD5 · Documentación del conjunto de datos

**Campos mínimos de una ficha de datos:**

| Campo | Descripción |
|---|---|
| Origen | Fuentes y mecanismos de extracción |
| Finalidad | Objetivo del modelado |
| Estructura | Variables, tipos, volumetrías |
| Transformaciones | Pipeline aplicado y parámetros |
| Particiones | Tamaños y criterios de división |
| Limitaciones | Sesgos conocidos, restricciones de uso |
| Condiciones | Licencia, RGPD, restricciones de acceso |

---

## UD5 · Versionado y seguridad de datos

**Versionado del conjunto:**

```
dataset_v1.0  →  preprocesamiento inicial
dataset_v1.1  →  corrección de outliers
dataset_v2.0  →  nueva fuente incorporada
```

- Trazabilidad entre versiones de datos, transformaciones y modelos
- Herramientas: **DVC** · **MLflow** · **Delta Lake** · **LakeFS**

**Protección de datos:**
- Restricciones de acceso por rol (RBAC)
- Minimización: solo los datos estrictamente necesarios
- Anonimización o seudonimización de datos personales (RGPD)
- Reproducibilidad mediante procedimientos documentados y automatizables

---

<!-- _class: lead -->

# UD6
## Trabajo responsable, sostenible y PRL

---

## UD6 · Responsabilidad ética y sostenibilidad

**Responsabilidad en el tratamiento de datos:**
- Igualdad de derechos y oportunidades en el tratamiento de datos
- Comunicación efectiva entre equipos, roles y partes interesadas
- Trabajo colaborativo y transparente en los procesos de datos

**Sostenibilidad tecnológica:**
- Principio **DNSH** (*Do No Significant Harm*)
- ODS aplicables: **9** (Industria e innovación), **12** (Consumo responsable), **13** (Clima)
- Reducción del consumo computacional: selección de atributos y filtrado en origen
- Minimización de emisiones de CO₂ en el procesamiento masivo de datos

---

## UD6 · Prevención de riesgos laborales

| Riesgo | Medida preventiva |
|---|---|
| Tecnoestrés | Pausas activas programadas, desconexión fuera del horario |
| Fatiga visual | Pantallas calibradas, regla 20-20-20, iluminación adecuada |
| Postura | Mobiliario ergonómico ajustable, monitor a la altura de los ojos |
| Carga cognitiva | Planificación de tareas, documentación clara, herramientas de apoyo |
| Sedentarismo | Rutinas de movilidad, pausas de pie |

**Actuación ante emergencias:**
- Conocer y respetar el Plan de emergencias del centro
- Señalización de salidas y extintores · Protocolo de evacuación

---

## Criterios de evaluación — MP01

- Categoriza fuentes y configura pasarelas de acceso con trazabilidad
- Extrae datos conservando metadatos de procedencia
- Aplica técnicas estadísticas de evaluación de calidad
- Detecta y describe sesgos; documenta verificaciones
- Depura y transforma el conjunto según el diseño
- Divide en particiones sin contaminación entre ellas
- Documenta y versiona el conjunto con medidas de protección de datos
- Integra criterios de sostenibilidad en todo el proceso

---

<!-- _class: lead -->

# MP01 · Procesamiento de datos para IA

**200 h · Curso 1.º · ECP2492_3 · Nivel 3**

*CFS — Gestión de datos y entrenamiento IA (IAD)*
