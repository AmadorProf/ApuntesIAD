---
marp: true
theme: default
paginate: true
size: 16:9
header: 'MP03 · Explotación de servicios de datos y analítica'
footer: 'CFS Instalación, despliegue y explotación de sistemas de IA (IAD)'
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
section.lead h1 { font-size: 2.2em; text-align: center; margin-top: 100px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f0fdf4; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
</style>

<!-- _class: lead -->

# MP03 · Explotación de servicios de datos y analítica

CFS — Instalación, despliegue y explotación de sistemas de IA (IAD)

---

## Ficha del módulo

| Campo | Valor |
|---|---|
| Código | **MP03** |
| Estándar de competencia | ECP2496_3 · Nivel 3 |
| Familia profesional | Inteligencia Artificial y Data |
| Duración | **180 h** |
| Curso | **2.º** |

> **Competencia que desarrolla:** implementar la plataforma de servicios de IA mediante la asignación de recursos y el procesamiento integral de datos multimodales, series temporales y asistentes virtuales, garantizando la valoración predictiva y la extracción de conocimiento.

---

## Estructura del módulo

| # | Unidad didáctica |
|---|---|
| **UD1** | Implementación de la plataforma de servicios de IA |
| **UD2** | Valoración predictiva de datos estructurados |
| **UD3** | Análisis de series temporales |
| **UD4** | Visión artificial sobre imágenes y vídeo |
| **UD5** | Procesamiento de lenguaje natural y voz |
| **UD6** | Inteligencia de negocio y analítica avanzada |
| **UD7** | Gestión integral: seguridad, sostenibilidad y desarrollo profesional |

---

<!-- _class: lead -->

# UD1
## Implementación de la plataforma de servicios de IA

---

## UD1 · Habilitación y asignación de recursos

**Recursos a aprovisionar en la plataforma:**

| Recurso | Descripción |
|---|---|
| **Servicios** | APIs, microservicios, notebooks, pipelines |
| **Usuarios y roles** | Cuentas, grupos, permisos mínimos necesarios |
| **Espacio de disco** | Cuotas por usuario, proyecto o equipo |
| **Cómputo** | CPU/GPU asignadas, límites de uso concurrente |

**Asignación a centro de coste o proyecto:**
- Etiquetado de recursos para facturación interna
- Límites de consumo por proyecto
- Alertas de gasto o uso excesivo

---

## UD1 · Verificación de prerrequisitos y documentación

**Checklist de prerrequisitos técnicos:**

- ✅ Clientes instalados (SDK, CLI, navegador compatible)
- ✅ Autenticación configurada (SSO, API keys, certificados)
- ✅ Puertos y conectividad de red verificados
- ✅ Herramientas de desarrollo disponibles (IDE, notebooks)
- ✅ Plan de pruebas definido y ejecutado

**Documentación del aprovisionamiento:**
- Registro en el sistema de gestión de recursos
- Fecha, límites de consumo y responsable
- Incidencias detectadas durante la habilitación

---

<!-- _class: lead -->

# UD2
## Valoración predictiva de datos estructurados

---

## UD2 · Preprocesamiento y configuración del experimento

**Pipeline de preprocesamiento para datos tabulares:**

1. **Extracción** desde la fuente (base de datos, CSV, API, data warehouse)
2. **Alimentación** de la plataforma de AutoML o ML
3. **Etiquetado** de la variable objetivo y variables especiales (ID, fecha…)
4. **Configuración de subconjuntos:** entrenamiento, validación, prueba

**Configuración del experimento:**

| Hiperparámetro | Descripción |
|---|---|
| Modelos a comparar | Selección del conjunto de algoritmos candidatos |
| Variables descartables | Columnas a excluir del entrenamiento |
| Tamaño de lote | Muestras por actualización |
| Número de pasadas | Épocas o iteraciones máximas |

---

## UD2 · Integración del modelo en un pipeline productivo

**Documentación de resultados del experimento:**
- Conclusiones: qué modelo ganó y por qué
- Métricas de predicción y su intervalo de confianza
- Avisos técnicos (drift, sesgos, advertencias)
- Tiempo de cómputo consumido

**Integración en pipeline en la nube:**

```
Datos nuevos
    ↓
Preprocesamiento (normalización, codificación)
    ↓
Aplicación del modelo (inferencia)
    ↓
Posprocesamiento (formateo, umbralización)
    ↓
Salida (API, base de datos, dashboard)
```

---

<!-- _class: lead -->

# UD3
## Análisis de series temporales

---

## UD3 · Adquisición y segmentación de series temporales

**Fuentes de datos temporales:**

| Fuente | Protocolo | Caso de uso |
|---|---|---|
| **API REST** | HTTP polling o webhooks | Datos financieros, métricas |
| **IoT / MQTT** | Broker de mensajes | Telemetría de sensores |
| **WebSockets** | Conexión persistente | Datos en tiempo real |
| **Bases de datos temporales** | SQL, InfluxDB, TimescaleDB | Históricos industriales |

**Segmentación del conjunto:**
- Ventana deslizante (*sliding window*) para series continuas
- División temporal estricta: sin mezclar pasado con futuro

---

## UD3 · Experimentación y despliegue del modelo de pronóstico

**Configuración del experimento de serie temporal:**
- Horizonte de predicción (¿cuántos pasos al futuro?)
- Frecuencia de la serie (diaria, horaria, por minuto…)
- Modelos a comparar: ARIMA, Prophet, LSTM, Temporal Fusion Transformer
- Filtros de preprocesado: estacionalidad, tendencia, descomposición

**Métricas de evaluación:**

| Métrica | Descripción |
|---|---|
| **MAE** | Error absoluto medio |
| **RMSE** | Raíz del error cuadrático medio |
| **MAPE** | Error porcentual absoluto medio |
| **sMAPE** | Versión simétrica de MAPE |

---

<!-- _class: lead -->

# UD4
## Visión artificial sobre imágenes y vídeo

---

## UD4 · Preprocesamiento de imágenes y vídeo

**Pipeline de preprocesamiento:**

1. **Adquisición:** base de datos local, streaming de cámara, API de imágenes
2. **Decodificación:** leer el formato de imagen/vídeo (JPEG, PNG, MP4, H.264)
3. **Homogeneización:** redimensionar al tamaño de entrada del modelo
4. **Segmentación:** dividir vídeos en fotogramas o clips
5. **Anotación** (si aplica): bounding boxes, máscaras, etiquetas de clase

**Hiperparámetros de experimento:**
- Tamaño del *kernel* y número de capas convolucionales
- Tamaño de lote e iteraciones máximas
- *Data augmentation*: rotaciones, volteos, cambios de brillo, recortes

---

## UD4 · Despliegue y protección de datos visuales

**Integración del modelo de visión:**

| Escenario | Mecanismo de integración |
|---|---|
| Cámara IP / CCTV | RTSP stream + inferencia en tiempo real |
| API de imágenes | REST endpoint que recibe imagen y devuelve predicción |
| Batch de archivos | Pipeline programado sobre directorio o bucket |
| Dispositivo embebido | Modelo optimizado (TFLite, ONNX, TensorRT) |

**Protección de datos y privacidad:**
- Control de acceso a las imágenes y vídeos
- Anonimización de personas (difuminado de caras, matrículas)
- Seguridad de los flujos de transmisión (HTTPS, RTSP cifrado)

---

<!-- _class: lead -->

# UD5
## Procesamiento de lenguaje natural y voz

---

## UD5 · Transcripción automática y NLP

**Pipeline de voz a texto (ASR):**

```
Grabación de audio (WAV/MP3/FLAC)
    ↓
Segmentación por locutor (diarización)
    ↓
Transcripción automática (Whisper, Azure Speech, Google STT)
    ↓
Postprocesamiento: puntuación, normalización, corrección
    ↓
Almacenamiento para análisis NLP
```

**Modelos de NLU sobre el texto transcrito:**

| Tarea | Descripción |
|---|---|
| **Análisis de sentimiento** | Positivo / negativo / neutro |
| **Resumen automático** | Extractivo o abstractivo |
| **Extracción de entidades** | Personas, organizaciones, fechas, importes |
| **Análisis de temas** | LDA, BERTopic |

---

## UD5 · Protección de datos de texto y voz

**Consideraciones éticas y normativas:**

- **RGPD:** la voz y el texto pueden contener datos personales
- **Uso ético:** informar al hablante de que se graba y procesa su voz
- **Prevención de sesgos:** los modelos ASR y NLU pueden tener peor rendimiento con ciertos acentos, géneros o dialectos
- **Seguridad de acceso:** control de acceso a grabaciones y transcripciones
- **Minimización:** procesar solo lo necesario; no almacenar más tiempo del justificado

---

<!-- _class: lead -->

# UD6
## Inteligencia de negocio y analítica avanzada

---

## UD6 · Conexión y preparación de fuentes de datos

**Tipos de fuentes para BI:**

| Tipo | Ejemplos |
|---|---|
| **Estructuradas** | SQL Server, PostgreSQL, Snowflake, BigQuery |
| **Semiestructuradas** | JSON REST APIs, MongoDB, Elasticsearch |
| **Servicios de datos** | Google Analytics, Salesforce, SAP |
| **Archivos** | Excel, CSV, Parquet desde data lake |

**Preparación de los datos:**
- Depuración y normalización
- Integración de múltiples fuentes (joins, uniones)
- Agregación y modelado dimensional (estrella, copo de nieve)

---

## UD6 · Cuadros de mando e indicadores

**Configuración de indicadores y métricas:**
- Definir **KPIs** (indicadores clave de rendimiento) con fórmulas documentadas
- Establecer **dimensiones** (por qué se segmenta: fecha, región, producto…)
- Configurar **medidas** (qué se calcula: ventas, incidencias, conversiones…)
- Definir **filtros y alertas** automáticas ante umbrales superados

**Publicación y gobierno:**

| Aspecto | Configuración |
|---|---|
| Permisos | Roles de lectura, edición y administración |
| Actualización | Programada (diaria, horaria) o bajo demanda |
| Trazabilidad | Log de acceso y uso del informe |
| Validación | Contraste con fuente de referencia (regla de los 3 fuentes) |

---

<!-- _class: lead -->

# UD7
## Gestión integral: seguridad, sostenibilidad y desarrollo profesional

---

## UD7 · Seguridad y sostenibilidad en la explotación

**Seguridad operativa:**

| Riesgo | Medida |
|---|---|
| Acceso no autorizado a datos | RBAC, autenticación multifactor |
| Exposición de datos personales | Anonimización, seudonimización, cifrado |
| Fugas de información en BI | Control de permisos por campo y registro |
| Tecnoestrés | Reducción de carga cognitiva, documentación clara |

**Huella de carbono digital:**
- Apagar recursos cuando no se usan (*auto-shutdown*)
- Usar instancias de cómputo eficientes en energía
- Economía circular de activos tecnológicos (reutilización antes que reciclaje)

---

## UD7 · Desarrollo profesional continuo

**Actitudes profesionales clave:**

- **Autonomía:** tomar la iniciativa en la resolución de problemas
- **Rigor analítico:** verificar los resultados antes de comunicarlos
- **Mejora continua:** buscar siempre formas más eficientes y precisas
- **Compromiso ético:** aplicar normativa y buenas prácticas sin que se lo pidan
- **Normativa:** mantenerse actualizado sobre RGPD, Reglamento IA y estándares sectoriales

**Actuación ante emergencias:**
- Conocer y aplicar el Plan de emergencias del centro
- Protocolo de actuación ante incidentes de seguridad de datos

---

## Criterios de evaluación — MP03

- Habilita y asigna recursos; verifica prerrequisitos; documenta el aprovisionamiento
- Preprocesa y experimenta según el Plan; integra el modelo en un pipeline
- Adquiere y segmenta series temporales; despliega y verifica el modelo de pronóstico
- Preprocesa imágenes; despliega el modelo de visión; trata datos según privacidad
- Explota el servicio de transcripción; aplica modelos NLU; cumple normativa de datos
- Conecta fuentes; configura indicadores y cuadros de mando; publica con control de acceso
- Aplica protocolos de seguridad; gestiona recursos sosteniblemente; actúa con rigor

---

<!-- _class: lead -->

# MP03 · Explotación de servicios de datos y analítica

**180 h · Curso 2.º · ECP2496_3 · Nivel 3**

*CFS — Instalación, despliegue y explotación de sistemas de IA (IAD)*
