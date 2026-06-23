---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD3 · Análisis de series temporales | MP03 · Explotación de servicios de datos y analítica'
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
section.lead h1 { font-size: 2em; text-align: center; margin-top: 80px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
pre { background: #1e293b; color: #e2e8f0; padding: 16px; border-radius: 8px; font-size: 0.8em; }
</style>

<!-- _class: lead -->

# UD3 · Análisis de series temporales

**MP03 — Explotación de servicios de datos y analítica**
CFS Instalación, despliegue y explotación de sistemas de IA (IAD)

---

## Objetivos de la unidad

Al finalizar esta unidad el alumnado será capaz de:

- Adquirir series temporales desde distintas fuentes (APIs, IoT, websockets) mediante streaming y batch.
- Preprocesar y segmentar correctamente un dataset temporal para experimentación.
- Configurar y ejecutar experimentos con modelos de pronóstico (ARIMA, Prophet, LSTM, TFT).
- Documentar las predicciones, la fiabilidad y el tiempo de cómputo.
- Desplegar el modelo de pronóstico integrando sus entradas y salidas en el sistema productivo.

> **Resultado de aprendizaje:** Analiza conjuntos de datos en serie temporal con la herramienta de pronóstico para elaborar un modelo predictivo.

---

## ¿Qué es una serie temporal?

Una **serie temporal** es una secuencia de observaciones ordenadas en el tiempo, con una frecuencia definida.

### Componentes de una serie temporal

| Componente | Descripción | Ejemplo |
|---|---|---|
| **Tendencia** | Dirección general a largo plazo | Crecimiento anual de ventas |
| **Estacionalidad** | Patrón cíclico regular | Picos en diciembre, caídas en agosto |
| **Ciclo** | Fluctuaciones de largo plazo sin periodicidad fija | Ciclos económicos |
| **Ruido** | Variación aleatoria no explicable | Picos puntuales por eventos imprevistos |

### Casos de uso empresariales

- Predicción de demanda de productos (retail, logística).
- Previsión de consumo energético (utilities).
- Pronóstico de precios financieros (fintech, banca).
- Detección de anomalías en métricas de sistemas (IT operations).

---

## Adquisición de series temporales — Fuentes y protocolos

### Adquisición por streaming (tiempo real)

| Protocolo | Descripción | Caso de uso |
|---|---|---|
| **API REST con polling** | Consulta periódica a un endpoint HTTP | Precios de bolsa cada minuto |
| **WebSockets** | Conexión bidireccional persistente | Métricas de sistema en tiempo real |
| **MQTT** | Protocolo ligero para IoT | Temperatura de sensores industriales |
| **Apache Kafka** | Bus de mensajes de alto rendimiento | Eventos de transacciones bancarias |
| **Server-Sent Events (SSE)** | Streaming unidireccional HTTP | Actualizaciones de dashboards |

### Adquisición por batch (histórico)

- Descarga de ficheros CSV/Parquet desde un data lake.
- Query a una base de datos de series temporales (InfluxDB, TimescaleDB, QuestDB).
- Export de un ERP o sistema de gestión (SAP, Oracle) a fichero plano.

---

## Adquisición de series temporales — Bases de datos temporales

Las bases de datos especializadas en series temporales ofrecen ventajas clave frente a SQL estándar.

### Comparativa de bases de datos temporales

| Base de datos | Tipo | Ventaja diferencial |
|---|---|---|
| **InfluxDB** | Time series DB (OSS) | Alta velocidad de escritura; query language InfluxQL/Flux |
| **TimescaleDB** | Extensión PostgreSQL | SQL estándar con funciones temporales; compatibilidad total |
| **QuestDB** | Time series DB | Rendimiento extremo; compatible con SQL |
| **Azure Data Explorer** | PaaS cloud | Integración nativa con Azure; KQL query language |
| **Amazon Timestream** | PaaS cloud | Serverless; integración con IoT Core y Grafana |

> Para conjuntos de datos históricos de baja frecuencia (diaria, semanal), una base de datos SQL convencional suele ser suficiente.

---

## Preprocesamiento de series temporales

El preprocesamiento de datos temporales tiene particularidades que lo diferencian del caso tabular general.

### Pasos del preprocesamiento

1. **Carga y unificación:** importar los datos y unificar el índice temporal (mismo formato de fecha y zona horaria).
2. **Resampleo:** convertir a la frecuencia deseada (p. ej., de segundos a minutos) mediante agregación (media, suma, último valor).
3. **Imputación de huecos:** rellenar periodos faltantes (interpolación lineal, forward fill, valor cero).
4. **Detección y tratamiento de outliers:** identificar picos anómalos y decidir si corregirlos o mantenerlos.
5. **Descomposición:** separar tendencia, estacionalidad y residuo para análisis exploratorio.
6. **Normalización:** escalar los valores para modelos de deep learning.

### Herramientas

`pandas`, `statsmodels`, `Prophet`, `tsfresh`, `sktime`, Azure ML Forecasting, Vertex AI Forecasting.

---

## Segmentación de conjuntos temporales

La división de datos temporales debe respetar el orden cronológico: **nunca mezclar pasado con futuro**.

### División temporal estricta

```
|---- Entrenamiento ----|-- Validación --|-- Test --|
     (datos más antiguos)                (datos más recientes)
```

### Validación cruzada en series temporales

La validación cruzada estándar (k-fold aleatoria) no es válida en series temporales. Se usa **walk-forward validation**:

```
Iter 1: Train [1..100]  --> Validar [101..120]
Iter 2: Train [1..120]  --> Validar [121..140]
Iter 3: Train [1..140]  --> Validar [141..160]
...
```

Esto simula el proceso real de reentrenamiento periódico del modelo en producción.

---

## Modelos de pronóstico — Estadísticos clásicos

### ARIMA (AutoRegressive Integrated Moving Average)

- Modelo estadístico para series temporales univariadas estacionarias.
- Parámetros: `p` (autorregresión), `d` (diferenciación), `q` (media móvil).
- Variante estacional: **SARIMA** (añade parámetros `P`, `D`, `Q`, `m`).
- Adecuado para series con pocos datos y comportamiento predecible.

### Exponential Smoothing (Holt-Winters)

- Promedia las observaciones pasadas dando más peso a las recientes.
- Versión con tendencia y estacionalidad: **Holt-Winters**.
- Muy eficiente computacionalmente; funciona bien con datos de bajo volumen.

### Cuándo elegir modelos estadísticos

- Pocos datos históricos (< 2 años con frecuencia mensual).
- La serie tiene comportamiento estable y bien caracterizado.
- Se necesita interpretabilidad alta de los parámetros.

---

## Modelos de pronóstico — Machine Learning y Deep Learning

### Prophet (Meta)

- Modelo aditivo diseñado para series con estacionalidad múltiple y efectos de festivos.
- Fácil de configurar; robusto ante huecos y outliers.
- Ideal para predicciones de negocio (ventas, tráfico web, demanda).

### LSTM (Long Short-Term Memory)

- Red neuronal recurrente especializada en secuencias largas.
- Captura dependencias complejas no lineales.
- Requiere más datos y tiempo de entrenamiento que los modelos estadísticos.

### TFT — Temporal Fusion Transformer

- Arquitectura Transformer adaptada a series temporales multivariadas.
- Maneja múltiples series simultáneamente con covariables conocidas (precio del petróleo, festivos).
- Estado del arte en benchmarks de pronóstico empresarial.

---

## Configuración del experimento de pronóstico

### Hiperparámetros clave

| Hiperparámetro | Descripción | Ejemplo |
|---|---|---|
| **Horizonte de predicción** | Cuántos pasos al futuro predice el modelo | 7 días, 24 horas, 12 meses |
| **Ventana de contexto** | Cuántos pasos pasados usa el modelo como entrada | 30, 90, 365 días |
| **Frecuencia** | Granularidad de la serie | Diaria (`D`), horaria (`H`), mensual (`M`) |
| **Variables covariables** | Variables externas que ayudan a predecir | Precio del petróleo, temperatura, festivos |
| **Filtros de preprocesado** | Descomposición, diferenciación, normalización | STL, log-transform |
| **Métrica de evaluación** | Qué se optimiza | MAE, RMSE, MAPE, sMAPE |

---

## Métricas de evaluación en pronóstico

### Métricas de error

| Métrica | Fórmula | Interpretación |
|---|---|---|
| **MAE** | Media de |real - pred| | Error absoluto medio en las unidades originales |
| **RMSE** | Raíz de la media de (real - pred)² | Penaliza errores grandes; sensible a outliers |
| **MAPE** | Media de |real - pred| / |real| · 100 | Error relativo; no válido si hay ceros |
| **sMAPE** | 2·|real-pred| / (|real|+|pred|) · 100 | Versión simétrica; menos sesgada que MAPE |
| **WAPE** | Suma de |real-pred| / Suma de |real| | Robusto con ceros; usado en retail |

### Intervalo de predicción (PI)

El modelo debe proporcionar no solo el valor esperado sino también un **intervalo de confianza** (p. ej., PI al 80% y al 95%) para comunicar la incertidumbre al negocio.

---

## Documentación del experimento de pronóstico

### Informe de resultados (estructura mínima)

| Sección | Contenido |
|---|---|
| **Dataset** | Fuente, frecuencia, rango temporal, número de series |
| **Preprocesamiento** | Resampleo, imputación, outliers tratados |
| **Experimentos** | Modelos comparados, hiperparámetros, validación |
| **Resultados** | Tabla de métricas por modelo; gráficos de predicción vs. real |
| **Modelo seleccionado** | Justificación de la elección |
| **Intervalo de predicción** | Fiabilidad de las predicciones (PI 80% y 95%) |
| **Varianza** | Estabilidad del modelo en distintos horizontes |
| **Tiempo de cómputo** | Duración del entrenamiento y de la inferencia |
| **Avisos** | Periodos con mala cobertura, estacionalidad no capturada |

---

## Despliegue del modelo de pronóstico

### Patrones de integración de entradas y salidas

| Integración | Entrada | Salida |
|---|---|---|
| **API REST** | JSON con las observaciones recientes | JSON con predicciones e intervalos |
| **WebSocket** | Stream de datos en tiempo real | Stream de predicciones continuas |
| **Base de datos** | Tabla de histórico actualizada | Tabla de predicciones |
| **Fichero** | CSV / Parquet en batch | CSV / Parquet con predicciones |
| **Dispositivo dedicado** | Sensor IoT (MQTT) | Actuador o alarma local |

### Ciclo de reentrenamiento

```
[Producción] --> Acumula nuevos datos --> [Reentrenamiento periódico]
    --> Evalúa drift del modelo --> Si drift > umbral --> Despliega nuevo modelo
```

---

## Despliegue — Monitorización y drift

Una vez en producción, el modelo debe monitorizarse continuamente.

### Tipos de drift en series temporales

| Tipo | Descripción | Acción |
|---|---|---|
| **Data drift** | La distribución de los datos de entrada cambia | Re-evaluar el modelo con datos recientes |
| **Concept drift** | La relación entre variables cambia | Reentrenar el modelo |
| **Seasonal drift** | Aparece nueva estacionalidad no vista | Actualizar parámetros estacionales |
| **Structural break** | Cambio brusco en el nivel o tendencia | Detectar con tests de Chow o CUSUM |

### Alertas de monitorización

- Configurar alertas cuando el error de producción supere el umbral del informe de experimento.
- Revisar mensualmente las métricas de producción vs. las del experimento.

---

## Actividad práctica — UD3

### "Pronóstico de consumo energético en una planta industrial"

**Escenario:** La empresa IndustriaVerde S.A. tiene registros horarios de consumo eléctrico de sus 3 plantas durante los últimos 2 años (17.520 observaciones por planta). Quiere predecir el consumo de las próximas 48 horas para optimizar la compra de energía en el mercado.

**Tareas:**

1. Cargar los datos desde un fichero Parquet y unificar el índice temporal (UTC+1).
2. Preprocesar: detectar y tratar huecos (forward fill), eliminar outliers extremos (IQR x3), descomponer la serie con STL.
3. Dividir el dataset: entrenamiento hasta el 31/10/2024, validación noviembre 2024, test diciembre 2024.
4. Experimentar con Prophet y LSTM. Horizonte de predicción: 48 horas. Métricas: MAE y MAPE.
5. Seleccionar el modelo ganador y justificarlo. Calcular el intervalo de predicción al 80%.
6. Desplegar el modelo como API REST: entrada = últimas 168 horas, salida = predicción 48h + PI 80%.

**Entregable:** Informe completo + endpoint de inferencia documentado con ejemplos de llamada.

---

## Puntos clave — UD3

- Una serie temporal tiene cuatro componentes: tendencia, estacionalidad, ciclo y ruido.
- La adquisición puede ser por **streaming** (API polling, WebSocket, MQTT, Kafka) o por **batch** (fichero, base de datos temporal).
- El preprocesamiento incluye resampleo, imputación de huecos, detección de outliers, descomposición y normalización.
- La división de datos debe ser **cronológica estricta**; la validación cruzada usa walk-forward validation.
- Los modelos principales son: ARIMA/SARIMA (estadístico), Prophet (ML aditivo), LSTM (deep learning), TFT (transformer).
- El informe de resultados debe incluir métricas, varianza, intervalo de predicción y tiempo de cómputo.
- El modelo en producción requiere monitorización de **drift** y reentrenamiento periódico.

---

## Criterios de evaluación — UD3

| Criterio | Indicador de logro |
|---|---|
| Adquiere series temporales | Carga correctamente desde la fuente (API, IoT, fichero, BD temporal) y documenta la extracción |
| Preprocesa la serie | Aplica resampleo, imputación, tratamiento de outliers y descomposición |
| Segmenta correctamente | División cronológica sin mezcla temporal; walk-forward si aplica |
| Ejecuta experimentos de pronóstico | Configura horizonte, frecuencia, modelos y métricas; lanza el experimento |
| Documenta resultados | Entrega el informe con métricas, varianza, PI e interpretación del modelo seleccionado |
| Despliega el modelo | Integra las entradas y salidas del modelo en el sistema productivo (API, BD, fichero o dispositivo) |
| Verifica el despliegue | Comprueba que el endpoint devuelve predicciones coherentes y dentro del PI documentado |

---

<!-- _class: lead -->

[← Volver a MP03](../index.md)
