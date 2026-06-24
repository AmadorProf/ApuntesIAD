# UD6 · Monitorización y mantenimiento de sistemas de IA en producción

---

## 1. Introducción

Desplegar un modelo de machine learning en producción no es el final del proceso: es el inicio de una nueva fase operativa con desafíos propios. A diferencia del software tradicional, los sistemas de IA se degradan de maneras que no siempre producen errores explícitos. Un servicio web fallido lanza una excepción; un modelo que empieza a hacer predicciones incorrectas puede seguir respondiendo con código HTTP 200 durante semanas mientras el negocio pierde dinero o confianza.

Esta degradación silenciosa adopta tres formas principales:

**Model drift** (también llamado concept drift): la relación entre las variables de entrada y la salida correcta cambia con el tiempo. Un modelo de scoring crediticio entrenado antes de una crisis económica puede empezar a subestimar el riesgo porque los patrones de impago cambian. El modelo no ha cambiado, pero el mundo sí.

**Data drift** (también llamado covariate shift): la distribución estadística de los datos de entrada cambia respecto a la distribución sobre la que se entrenó el modelo. Si un e-commerce expande su catálogo a una nueva categoría de productos, las características que describen esos productos pueden ser muy distintas de las que el modelo vio durante el entrenamiento. El modelo puede seguir funcionando, pero opera fuera de su dominio de validez.

**Cambios en el comportamiento del usuario**: los usuarios interactúan con el sistema de maneras que alteran los datos de entrada de forma sistemática. Los sistemas de recomendación son especialmente vulnerables: a medida que el modelo mueve el comportamiento de los usuarios, los datos de interacción cambian, lo que a su vez cambia el contexto de entrenamiento futuro. Este bucle de retroalimentación puede amplificar sesgos existentes o llevar al sistema a optimizar métricas proxy que divergen de los objetivos reales del negocio.

La monitorización y el mantenimiento de sistemas de IA en producción responden directamente a estos tres fenómenos. No se trata solo de vigilar que los servidores funcionen, sino de mantener la validez científica y operativa del sistema a lo largo del tiempo. Esta unidad cubre los instrumentos técnicos, los patrones de diseño y los procesos organizativos necesarios para sostener un sistema de IA en producción con garantías de calidad.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Distinguir entre los tres pilares de la observabilidad (logs, métricas, trazas) y comprender cómo se complementan para diagnosticar problemas en sistemas ML.
- Configurar Prometheus para recolectar métricas de infraestructura y de modelo, utilizando los exporters más relevantes para entornos GPU.
- Construir dashboards en Grafana con los golden signals aplicados a servicios de inferencia ML, e implementar alertas basadas en umbrales y condiciones compuestas.
- Diferenciar entre data drift y concept drift, y seleccionar las métricas estadísticas adecuadas (PSI, KL Divergence, Wasserstein distance) para detectar cada tipo.
- Implementar pipelines de detección de drift usando Evidently AI, integrando los resultados en flujos de monitorización continua.
- Diseñar estrategias para recopilar ground truth en producción y calcular métricas de modelo reales con datos etiquetados de forma diferida.
- Planificar y ejecutar ciclos de mantenimiento preventivo y correctivo, incluyendo el reentrenamiento automatizado basado en triggers de drift o volumen de datos.
- Diseñar dashboards operativos que comuniquen el estado del sistema a audiencias técnicas y no técnicas.

---

## 3. Observabilidad en sistemas ML

La observabilidad es la capacidad de entender el estado interno de un sistema a partir de sus salidas externas. En sistemas de software tradicionales se articula sobre tres pilares: logs, métricas y trazas. En sistemas ML estos pilares siguen siendo válidos, pero cada uno adquiere dimensiones adicionales relacionadas con el comportamiento del modelo.

### 3.1 Logs estructurados

Un log es un registro de un evento discreto que ocurrió en un momento concreto. Los logs son el instrumento de diagnóstico más granular y, correctamente diseñados, permiten reconstruir la historia de cualquier incidente.

En sistemas ML en producción, los logs deben ser **estructurados en formato JSON**. Los logs en texto libre son imposibles de analizar a escala. Un log estructurado incluye campos como timestamp, nivel de severidad, servicio de origen, identificador de traza, y los campos específicos del evento. Un log de inferencia podría incluir el identificador de solicitud, la versión del modelo, la latencia de inferencia en milisegundos y la clase predicha (sin incluir los datos de entrada completos si contienen información personal).

Los **niveles de log** (DEBUG, INFO, WARNING, ERROR, CRITICAL) deben usarse con disciplina. En producción, el nivel mínimo suele ser INFO. Los logs de nivel DEBUG solo se activan durante la investigación de incidentes. Un error frecuente es loguear en DEBUG información que sería necesaria para diagnosticar problemas en producción: cuando el incidente ocurre, esa información no está disponible.

El **sampling en alto volumen** es una necesidad práctica. Un servicio de inferencia que recibe 10.000 solicitudes por segundo generaría un volumen de logs que saturaría cualquier sistema de almacenamiento y análisis. La solución es el log sampling: registrar solo una fracción de las solicitudes exitosas (por ejemplo, 1 de cada 100) mientras se registran siempre los errores y las solicitudes que excedan umbrales de latencia. El sampling debe ser consistente: si se registra una solicitud, deben registrarse todos los eventos relacionados con esa solicitud (propagando el identificador de traza).

### 3.2 Métricas

Las métricas son agregaciones numéricas del estado del sistema a lo largo del tiempo. A diferencia de los logs, no capturan eventos individuales sino tendencias, tasas y distribuciones. Son el instrumento principal para alertas y dashboards.

**Métricas de infraestructura**: utilización de CPU (porcentaje por core y agregado), uso de GPU (porcentaje de SM utilization y memoria de video), consumo de RAM, I/O de disco, tráfico de red. Para sistemas ML el GPU es el recurso crítico: una GPU subutilizada puede indicar un cuello de botella en el preprocesamiento de datos o en la carga del modelo; una GPU saturada al 100% puede indicar que el batch size es demasiado grande o que se necesita escalar horizontalmente.

**Métricas de modelo**: latencia de inferencia (percentil 50, 95 y 99, no solo la media, porque la media enmascara los casos lentos que más afectan a la experiencia de usuario), throughput medido en solicitudes por segundo o en tokens por segundo para modelos de lenguaje, error rate (porcentaje de solicitudes que terminan en error), model confidence distribution (distribución del score de confianza de las predicciones, para detectar cuando el modelo empieza a ser menos seguro).

**Métricas de negocio**: tasa de conversión, número de recomendaciones aceptadas, tiempo hasta la primera acción del usuario tras una predicción, revenue atribuible al modelo. Estas métricas son las que más importan a la organización pero son también las más difíciles de obtener porque requieren integrar datos de múltiples sistemas y pueden tardar días o semanas en materializarse.

### 3.3 Trazas distribuidas

Una traza es la representación del recorrido de una solicitud a través de múltiples componentes de un sistema distribuido. En una arquitectura de microservicios, una sola solicitud del usuario puede pasar por un API gateway, un servicio de preprocesamiento, el servicio de inferencia, un servicio de postprocesamiento y un servicio de logging de predicciones. Sin trazas distribuidas, es imposible determinar en qué componente se introdujo la latencia o el error.

**OpenTelemetry** es el estándar abierto para la instrumentación de trazas, métricas y logs. Proporciona SDKs para todos los lenguajes principales y un protocolo de exportación (OTLP) que es compatible con backends como Jaeger, Zipkin, Grafana Tempo y los servicios gestionados de los proveedores de nube.

La instrumentación con OpenTelemetry consiste en crear spans que representan unidades de trabajo. Cada span tiene un nombre, un timestamp de inicio y fin, atributos clave-valor, y puede contener eventos y errores. El span padre representa la solicitud completa; los spans hijos representan operaciones internas. El identificador de traza (trace ID) se propaga entre servicios mediante cabeceras HTTP, lo que permite reconstruir el árbol completo de spans para cualquier solicitud.

### 3.4 Correlación de los tres pilares

El valor real de la observabilidad emerge cuando los tres pilares están correlacionados. El flujo de diagnóstico típico es: las métricas detectan una anomalía (el percentil 99 de latencia sube bruscamente), las trazas permiten aislar el componente responsable (el servicio de preprocesamiento está tardando 3 segundos en normalizar los features), y los logs de ese componente revelan la causa raíz (hay un tipo de entrada inesperado que activa un código path lento). Sin la correlación, cada pilar solo ofrece una vista parcial.

---

## 4. Prometheus y Grafana para sistemas ML

### 4.1 Prometheus: arquitectura y tipos de métricas

Prometheus es un sistema de monitorización open source diseñado para entornos dinámicos como Kubernetes. Su modelo de datos es una serie temporal identificada por un nombre de métrica y un conjunto de etiquetas clave-valor. Su método de recolección es el **scraping**: Prometheus realiza peticiones HTTP a los endpoints `/metrics` de los servicios monitorizados a intervalos configurables (por defecto, cada 15 segundos).

Los cuatro tipos de métricas de Prometheus:

**Counter**: valor que solo crece monotónicamente. Útil para contar solicitudes totales, errores totales, bytes procesados. Las funciones de PromQL como `rate()` e `increase()` operan sobre counters para calcular tasas.

**Gauge**: valor que puede subir y bajar. Útil para temperatura de GPU, uso de memoria, número de solicitudes en vuelo, longitud de una cola.

**Histogram**: muestrea observaciones y las agrupa en buckets predefinidos. Exporta el recuento en cada bucket, el recuento total y la suma total. Permite calcular percentiles aproximados en PromQL con `histogram_quantile()`. Es el tipo adecuado para latencias.

**Summary**: similar al histogram, pero calcula los percentiles en el cliente. Los percentiles son exactos pero no pueden agregarse entre instancias, lo que lo hace menos útil en entornos distribuidos. En general se prefiere el histogram.

### 4.2 Exporters relevantes para entornos GPU

**nvidia-dcgm-exporter**: el exporter oficial de NVIDIA para métricas de GPU. Expone métricas como `DCGM_FI_DEV_GPU_UTIL` (utilización de GPU), `DCGM_FI_DEV_MEM_COPY_UTIL` (utilización de memoria de video), `DCGM_FI_DEV_GPU_TEMP` (temperatura), `DCGM_FI_DEV_POWER_USAGE` (consumo en vatios). Se despliega como DaemonSet en Kubernetes para que haya una instancia por nodo GPU.

**node-exporter**: expone métricas del sistema operativo del nodo: CPU, memoria, disco, red. Imprescindible para correlacionar el comportamiento del modelo con el estado del host.

**kube-state-metrics**: expone el estado de los objetos de Kubernetes (Deployments, Pods, ReplicaSets). Permite construir alertas cuando el número de pods disponibles cae por debajo del deseado.

**Custom exporter en Python con prometheus-client**: para exponer métricas específicas del modelo o del negocio que ningún exporter estándar cubre. La biblioteca `prometheus-client` de Python permite definir métricas y exponerlas en un endpoint HTTP en pocas líneas de código. Un servicio de inferencia puede registrar un `Histogram` para la latencia, un `Counter` para las predicciones por clase y un `Gauge` para la versión del modelo activo.

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

REQUEST_LATENCY = Histogram(
    'inference_latency_seconds',
    'Latencia de inferencia en segundos',
    buckets=[.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5]
)
PREDICTION_COUNTER = Counter(
    'predictions_total',
    'Total de predicciones realizadas',
    ['model_version', 'predicted_class']
)
MODEL_VERSION = Gauge('model_version_active', 'Versión del modelo activa')
```

### 4.3 PromQL básico

PromQL (Prometheus Query Language) es el lenguaje de consulta de Prometheus. Algunos patrones fundamentales para sistemas ML:

- Tasa de solicitudes por segundo (últimos 5 minutos): `rate(http_requests_total[5m])`
- Percentil 99 de latencia: `histogram_quantile(0.99, rate(inference_latency_seconds_bucket[5m]))`
- Porcentaje de errores: `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100`
- Utilización de GPU: `DCGM_FI_DEV_GPU_UTIL{gpu="0"}`

### 4.4 Grafana: datasources, dashboards y alertas

Grafana es la capa de visualización estándar para Prometheus. Se conecta a Prometheus como datasource y permite construir dashboards con paneles de diferentes tipos: series temporales, estadísticas, tablas, mapas de calor y gauges.

Un **dashboard de GPU cluster** debe incluir: utilización de GPU por nodo, memoria de video utilizada vs disponible, temperatura de GPU (con alertas a 85°C), consumo eléctrico total del cluster.

Un **dashboard completo para un servicio de inferencia ML** incluye: tasa de solicitudes entrantes, latencia en percentiles 50/95/99, error rate, distribución de clases predichas (para detectar shifts en la distribución de salidas), número de pods activos, utilización de CPU y GPU por pod, y métricas de negocio si están disponibles.

Las **alertas en Grafana** pueden definirse sobre cualquier query de PromQL. Una alerta tiene un estado de evaluación (pendiente, disparada, resuelta) y un canal de notificación (email, Slack, PagerDuty). Es importante evitar el alert fatigue: las alertas deben configurarse con umbrales calibrados y con un periodo "for" (la condición debe mantenerse durante N minutos antes de disparar) para evitar falsas alarmas por picos transitorios.

---

## 5. Detección de model drift y data drift

### 5.1 Conceptos y diferencias

**Data drift** (también llamado covariate shift) ocurre cuando la distribución de las variables de entrada P(X) cambia entre el momento del entrenamiento y el momento de la inferencia en producción. El modelo no ha cambiado; lo que ha cambiado es el tipo de datos que recibe. Ejemplo: un modelo de reconocimiento de imágenes médicas entrenado con imágenes de un tipo de escáner empieza a recibir imágenes de un escáner diferente con resolución y contraste distintos.

**Concept drift** ocurre cuando la relación entre las variables de entrada y la variable objetivo P(Y|X) cambia. Esto es inherentemente más difícil de detectar porque requiere conocer la etiqueta verdadera. Ejemplo: un modelo de detección de spam entrenado hace dos años no reconoce las técnicas de spam actuales porque los spammers han adaptado sus tácticas. La distribución de emails puede no haber cambiado significativamente (data drift leve), pero la definición de spam ha evolucionado (concept drift severo).

En la práctica, ambos pueden coexistir, y la distinción importa porque sugieren remedios distintos. El data drift sugiere actualizar el preprocesamiento, recolectar más datos del nuevo dominio, o aplicar técnicas de domain adaptation. El concept drift requiere reentrenar el modelo con etiquetas actualizadas.

### 5.2 Métricas estadísticas para detección de drift

**Population Stability Index (PSI)**: compara la distribución de una variable entre un dataset de referencia y el dataset de producción dividiéndola en bins y calculando una suma ponderada de diferencias. PSI < 0.1 indica distribuciones estables; PSI entre 0.1 y 0.25 indica cambios moderados que merecen atención; PSI > 0.25 indica cambios significativos. El PSI es intuitivo y ampliamente usado en la industria financiera, pero asume que la variable puede dividirse en bins de forma significativa.

**KL Divergence (Kullback-Leibler)**: mide cuánta información se pierde cuando se usa la distribución de referencia Q para aproximar la distribución de producción P. No es simétrica: KL(P||Q) ≠ KL(Q||P). En el contexto de drift detection, la asimetría puede ser problemática porque el resultado depende de qué distribución se coloca en cada posición.

**Jensen-Shannon Divergence**: versión simétrica y normalizada de la KL Divergence. Su raíz cuadrada es la Jensen-Shannon Distance, que es una verdadera distancia métrica. Siempre produce valores entre 0 y 1, lo que facilita la interpretación y la definición de umbrales.

**Wasserstein Distance** (también llamada Earth Mover's Distance): mide el coste mínimo de transformar una distribución en otra, interpretable como la cantidad de "tierra" que hay que mover si se visualizan las distribuciones como montones de tierra. Es especialmente útil para distribuciones numéricas y es robusta ante pequeñas perturbaciones. Su principal desventaja es el coste computacional en espacios de alta dimensión.

Para **variables categóricas**, la Chi-cuadrado y el test exacto de Fisher son alternativas clásicas. Para **detectar drift en el espacio de embeddings** (datos de texto o imagen representados como vectores de alta dimensión), se pueden usar técnicas como Maximum Mean Discrepancy (MMD) o proyecciones a 2D con UMAP para inspección visual.

### 5.3 Evidently AI

Evidently AI es una biblioteca open source de Python para evaluación y monitorización de modelos ML. Ofrece dos abstracciones principales:

**Report**: genera un informe visual en HTML o JSON con análisis de drift, calidad de datos y performance del modelo. Útil para análisis exploratorio y generación de informes periódicos.

**TestSuite**: permite definir un conjunto de pruebas con umbrales explícitos y obtener un resultado pass/fail. Adecuado para integrar en pipelines de CI/CD o de monitorización automática.

Flujo básico de uso:

```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=df_train, current_data=df_production)
report.save_html("drift_report.html")
```

Para un TestSuite que dispare una alerta si más del 30% de las features tienen drift:

```python
from evidently.test_suite import TestSuite
from evidently.tests import TestShareOfDriftedColumns

suite = TestSuite(tests=[
    TestShareOfDriftedColumns(lt=0.3)
])
suite.run(reference_data=df_train, current_data=df_production)
suite.save_html("drift_test.html")
```

Evidently puede integrarse en un pipeline de monitorización que se ejecute diariamente: se toman los datos de inferencia del día anterior, se comparan con el dataset de referencia, y si el TestSuite falla, se dispara una alerta y se registra el evento en el sistema de seguimiento de incidentes.

### 5.4 Alternativas SaaS

**WhyLabs** ofrece una plataforma gestionada que ingiere perfiles estadísticos de los datos de entrada y salida del modelo (sin necesidad de enviar los datos reales, solo los perfiles), y detecta drift automáticamente con alertas configurables. Se integra con la biblioteca open source `whylogs` para generar los perfiles.

**Arize AI** es una plataforma de observabilidad para ML que además del drift ofrece análisis de performance del modelo por segmentos, herramientas de explicabilidad y un workflow para el etiquetado de predicciones y la recogida de ground truth. Es especialmente relevante en casos de uso donde la monitorización de subgrupos de población (fairness monitoring) es un requisito.

---

## 6. Monitorización de métricas de modelo en producción

### 6.1 Logging de predicciones

Para calcular métricas reales de un modelo en producción, es necesario registrar sus predicciones. Esto plantea dos tensiones: la privacidad de los datos de los usuarios y el volumen de información generada.

El **sampling estratégico** resuelve parcialmente el problema del volumen: en lugar de registrar todas las predicciones, se registra una muestra representativa. El sampling aleatorio simple puede no capturar suficientes ejemplos de clases raras o de casos límite. El sampling estratificado garantiza representación de todos los segmentos relevantes (por ejemplo, todas las categorías de producto en un sistema de recomendación). El sampling basado en incertidumbre prioriza los casos donde el modelo tiene menor confianza, que son precisamente los más informativos para el reentrenamiento.

La **privacidad** requiere definir qué información se puede registrar. Los datos de entrada pueden contener información personal identificable (PII). La solución más común es registrar solo las features procesadas (no los datos raw), aplicar hashing a los identificadores de usuario, y asegurarse de que el sistema de almacenamiento de predicciones está sujeto a las mismas políticas de retención que el resto del sistema.

### 6.2 Ground truth collection

La mayor dificultad de la monitorización de modelos en producción es que raramente se conoce la etiqueta verdadera en el momento de la predicción. La inferencia es en tiempo real; la validación de la predicción puede ocurrir horas, días o semanas después.

**Feedback explícito del usuario**: el usuario indica si la predicción fue correcta. Ejemplos: thumbs up/down en un sistema de recomendación, el usuario acepta o rechaza una autocompletación, el usuario marca un email como spam o no spam. El problema es que el feedback explícito es escaso y sesgado: los usuarios solo interactúan con una fracción de las predicciones, y la probabilidad de dar feedback depende del resultado.

**Etiquetado diferido (delayed labeling)**: las etiquetas verdaderas se conocen con retraso. En un modelo de predicción de impago de crédito, la etiqueta se conoce en el momento en que el préstamo vence o entra en mora. En un modelo de diagnóstico médico, la etiqueta se conoce cuando el paciente recibe un diagnóstico definitivo. El sistema de monitorización debe unir las predicciones realizadas con las etiquetas que llegan posteriormente.

**Proxies de calidad**: cuando no es posible obtener etiquetas reales, se usan proxies. Para un sistema de recomendación, el click-through rate es un proxy imperfecto de la relevancia. Para un modelo de traducción automática, el BLEU score con traducciones de referencia es un proxy de la calidad percibida. Los proxies deben usarse con precaución porque pueden optimizarse sin mejorar el objetivo real.

### 6.3 Métricas de modelo en producción vs accuracy de evaluación

La accuracy medida en el dataset de validación durante el desarrollo es una estimación de la performance esperada en producción. En producción, las métricas se calculan sobre datos reales con etiquetas obtenidas de las estrategias anteriores y pueden divergir significativamente del benchmark inicial.

Las razones habituales de divergencia son: dataset shift (los datos de producción no siguen la distribución del dataset de entrenamiento/validación), label bias (las etiquetas de producción tienen un proceso de generación diferente al de las etiquetas del dataset de entrenamiento), y selection bias (el sistema de recolección de feedback no es aleatorio).

### 6.4 Alertas de degradación

Se deben configurar alertas cuando las métricas de modelo caen por debajo de umbrales definidos. Es recomendable definir dos niveles: un umbral de advertencia (que activa una revisión) y un umbral crítico (que activa un proceso de rollback o reentrenamiento urgente). Los umbrales deben derivarse del análisis del impacto de negocio: cuánta degradación en la precisión del modelo equivale a una caída inaceptable en la métrica de negocio.

---

## 7. Mantenimiento preventivo y correctivo

### 7.1 Mantenimiento preventivo

El mantenimiento preventivo evita que los problemas ocurran. En el contexto de sistemas ML, incluye:

**Reentrenamiento periódico**: incluso si no se detecta drift explícito, se puede establecer un calendario de reentrenamiento (semanal, mensual, trimestral) para incorporar datos recientes. La frecuencia adecuada depende de la velocidad de cambio del dominio y del coste de reentrenamiento.

**Actualización de dependencias**: las bibliotecas de ML (PyTorch, TensorFlow, scikit-learn) publican actualizaciones frecuentes con correcciones de bugs y mejoras de rendimiento. Mantener las dependencias actualizadas reduce el riesgo de vulnerabilidades de seguridad y asegura compatibilidad con el hardware (por ejemplo, nuevas versiones de CUDA). Se recomienda un ciclo de actualización con entorno de staging donde se valide que el modelo sigue funcionando correctamente tras la actualización.

**Rotación de secretos**: las credenciales de acceso a bases de datos, APIs externas y sistemas de almacenamiento deben rotarse periódicamente. Automatizar la rotación con servicios como AWS Secrets Manager, Azure Key Vault o HashiCorp Vault, e integrar la rotación con el despliegue del servicio para que los nuevos secretos se inyecten sin downtime.

**Revisión de capacidad**: monitorizar las tendencias de crecimiento del tráfico y del volumen de datos para planificar el escalado de infraestructura antes de alcanzar los límites.

### 7.2 Reentrenamiento automático

El reentrenamiento manual es un proceso frágil que depende de que alguien note la degradación, tome la decisión de reentrenar y ejecute el proceso. El reentrenamiento automático elimina esa dependencia.

Tres tipos de triggers para el reentrenamiento automático:

**Trigger basado en tiempo**: el pipeline de reentrenamiento se ejecuta en un schedule definido (por ejemplo, todos los lunes a las 2:00 AM). Es el más simple de implementar y predecible en su comportamiento. El riesgo es que sea demasiado frecuente (desperdiciando recursos) o demasiado infrecuente (permitiendo que el drift se acumule).

**Trigger basado en volumen de datos nuevos**: el reentrenamiento se ejecuta cuando se han acumulado N ejemplos nuevos (con sus etiquetas). Garantiza que cada ciclo de reentrenamiento incorpora suficiente información nueva para justificar el coste. Es especialmente adecuado cuando el volumen de datos nuevos es variable.

**Trigger basado en drift detectado**: el reentrenamiento se ejecuta cuando el sistema de monitorización detecta drift significativo (por ejemplo, PSI > 0.25 en más del 30% de las features, o cuando las métricas de performance caen por debajo del umbral de alerta). Es el más reactivo y el que mejor responde a cambios repentinos en el dominio.

El pipeline de reentrenamiento automático debe incluir: preparación del dataset (unión de datos históricos con datos recientes y etiquetas diferidas), entrenamiento del modelo, validación automática (el modelo nuevo debe superar un benchmark mínimo antes de desplegarse), y despliegue con rollout gradual (canary deployment o blue/green deployment) para detectar problemas antes de exponer el nuevo modelo a todo el tráfico.

### 7.3 Corrección de errores en producción sin downtime

Cuando se detecta un error en el modelo o en el servicio de inferencia, hay que corregirlo sin interrumpir el servicio.

**Rollback**: si el error fue introducido por un despliegue reciente, la corrección más rápida es volver a la versión anterior. En Kubernetes, esto se consigue con `kubectl rollout undo deployment/<nombre>`. Los sistemas de serving de modelos como Seldon Core o KServe permiten rollbacks entre versiones de modelos sin cambiar la infraestructura.

**Hotfix sin reentrenamiento**: algunos errores no requieren reentrenar el modelo, sino corregir el preprocesamiento, los umbrales de decisión o la lógica de postprocesamiento. Estas correcciones se despliegan como actualizaciones del código del servicio.

**Feature flagging**: los feature flags permiten activar o desactivar funcionalidades del sistema sin desplegar código nuevo. Se pueden usar para desactivar el modelo en casos específicos (por ejemplo, para un segmento de usuarios afectado por un bug) mientras se prepara la corrección.

**Circuit breaker**: si el servicio de inferencia falla repetidamente, un circuit breaker puede detectarlo y desviar el tráfico a un fallback (por ejemplo, un modelo más simple pero robusto, o reglas heurísticas) hasta que el servicio principal se recupere.

---

## 8. Dashboards operativos

### 8.1 Elementos de un dashboard ML de producción

Un dashboard operativo eficaz comunica el estado del sistema de forma inmediata. No debe requerir análisis para entender si el sistema está bien o mal. Los elementos esenciales:

**Estado del sistema**: un indicador claro (verde/amarillo/rojo) del estado global. El estado debe derivarse automáticamente de las alertas activas y los SLOs.

**SLOs en tiempo real**: los Service Level Objectives definen los objetivos cuantitativos del servicio (por ejemplo, "el 99% de las solicitudes deben completarse en menos de 200ms" o "el error rate debe ser inferior al 0.1%"). El dashboard debe mostrar el cumplimiento actual de los SLOs y la tendencia histórica (error budget consumption).

**Alertas activas**: lista de las alertas en estado disparado, con su severidad, tiempo desde que se dispararon y enlace a la documentación del runbook correspondiente.

**Top errores**: los tipos de error más frecuentes en las últimas horas, con recuento y tendencia. Esto permite identificar errores sistémicos (que afectan a muchas solicitudes) vs errores esporádicos.

**Métricas de negocio clave**: 2-3 métricas que conecten el comportamiento técnico del sistema con el impacto en el negocio. Estas métricas son el puente entre el equipo de ML y los stakeholders no técnicos.

### 8.2 Golden signals aplicados a ML

Los cuatro golden signals definidos por el libro Site Reliability Engineering de Google son latencia, tráfico, errores y saturación. Aplicados a sistemas ML:

**Latencia**: tiempo desde que se recibe la solicitud de inferencia hasta que se devuelve la respuesta. Se debe monitorizar en percentiles (P50, P95, P99), no en media. El P99 es especialmente importante porque representa la experiencia del usuario en el peor 1% de los casos. Para sistemas de inferencia con GPU, la latencia tiene componentes distintos: tiempo de transferencia de datos al dispositivo, tiempo de computación en GPU (forward pass), tiempo de transferencia de resultados de vuelta.

**Tráfico**: número de solicitudes de inferencia por segundo, o número de tokens procesados por segundo para modelos de lenguaje. El tráfico es el indicador de demanda y debe correlacionarse con los patrones históricos para detectar anomalías (caídas súbitas que pueden indicar un fallo upstream, o picos que pueden indicar un ataque o un evento excepcional).

**Errores**: tasa de solicitudes que terminan en error, desglosada por tipo de error. Se deben distinguir los errores del cliente (4xx en HTTP, por ejemplo solicitudes mal formadas) de los errores del servidor (5xx, indicativos de un problema en el servicio). Los errores del modelo (predicciones con muy baja confianza, que el sistema puede rechazar en lugar de servir) son una categoría adicional específica de los sistemas ML.

**Saturación**: qué fracción de los recursos disponibles está siendo utilizada. Para sistemas GPU, la saturación se mide en porcentaje de SM utilization y porcentaje de memoria de video utilizada. Una saturación cercana al 100% indica que el sistema está al límite de su capacidad y que nuevos picos de tráfico pueden degradar la latencia o provocar errores. Se recomienda planificar el escalado cuando la saturación sostenida supera el 70-80%.

---

## 9. Actividades prácticas

### Actividad 1: Instrumentación de un servicio de inferencia con Prometheus

El estudiante instrumentará un servicio de inferencia de texto (por ejemplo, clasificación de sentimiento con un modelo de scikit-learn o transformers) con `prometheus-client`. Deberá exponer las siguientes métricas: counter de predicciones por clase, histogram de latencia de inferencia con buckets apropiados, gauge con la versión del modelo activo. Configurará un Prometheus local para hacer scraping del servicio y verificará que las métricas aparecen correctamente. Como entregable, debe incluir el código del servicio instrumentado, el fichero `prometheus.yml` de configuración y capturas de pantalla de las métricas en la UI de Prometheus.

### Actividad 2: Dashboard en Grafana con golden signals

Partiendo del servicio instrumentado en la actividad anterior, el estudiante construirá un dashboard en Grafana con los cuatro golden signals: un panel de series temporales para la tasa de solicitudes (usando `rate()`), un panel para los percentiles de latencia (usando `histogram_quantile()`), un panel para el error rate, y un panel de gauge para la saturación de CPU. Configurará una alerta que se dispare cuando el P99 de latencia supere 500ms durante más de 2 minutos. Como entregable, debe exportar el dashboard en formato JSON e incluir una captura del panel con la alerta disparada (puede simularse generando carga artificial).

### Actividad 3: Detección de drift con Evidently AI

El estudiante simulará un escenario de data drift. Tomará un dataset de clasificación (por ejemplo, el dataset de crédito de UCI o cualquier dataset tabular de Kaggle), dividirá los datos en un split "de referencia" (entrenamiento histórico) y un split "de producción" con modificaciones artificiales (por ejemplo, escalado de algunas variables, introducción de valores fuera del rango habitual, o rebalanceo de clases). Ejecutará un Report de Evidently con `DataDriftPreset` y un `ClassificationPreset` y analizará los resultados. Luego configurará un TestSuite con umbrales personalizados y documentará las métricas de drift obtenidas para cada feature, identificando cuáles han cambiado más y por qué.

### Actividad 4: Diseño de un plan de mantenimiento para un caso real

El estudiante elegirá un dominio de aplicación (detección de fraude, recomendación de productos, predicción de demanda, diagnóstico médico, etc.) y diseñará un plan de mantenimiento completo que incluya: estrategia de logging de predicciones (qué se registra, con qué sampling), estrategia de ground truth collection (cómo se obtienen las etiquetas reales, con qué delay esperado), métricas de drift y umbrales de alerta (justificados para el dominio elegido), triggers para el reentrenamiento automático (tiempo, volumen o drift, con justificación), y procedimiento de respuesta a incidentes (qué pasos se siguen si se detecta degradación severa). El entregable es un documento técnico de 3-5 páginas.

---

## 10. Referencias

**Documentación oficial**

- Evidently AI. *Evidently AI Documentation*. Guías de instalación, presets disponibles, integración con pipelines y referencia de la API. Disponible en: https://docs.evidentlyai.com/
- Prometheus. *Prometheus Documentation*. Incluye guía de configuración, referencia de PromQL, tipos de métricas y guías de exporters. Disponible en: https://prometheus.io/docs/introduction/overview/
- Grafana Labs. *Grafana Documentation*. Documentación de dashboards, alertas, datasources y Grafana Agent. Disponible en: https://grafana.com/docs/grafana/latest/
- OpenTelemetry. *OpenTelemetry Documentation*. Especificación del protocolo, SDKs para los lenguajes principales y guías de instrumentación. Disponible en: https://opentelemetry.io/docs/
- NVIDIA. *DCGM Exporter*. Documentación del exporter de métricas GPU para Prometheus. Disponible en: https://github.com/NVIDIA/dcgm-exporter
- WhyLabs. *WhyLabs Documentation*. Guías de integración con whylogs y configuración de la plataforma. Disponible en: https://docs.whylabs.ai/
- Arize AI. *Arize AI Documentation*. Plataforma de observabilidad ML: integración, monitorización de drift y fairness. Disponible en: https://docs.arize.com/arize/

**Libros y recursos académicos**

- Huyen, Chip. *Designing Machine Learning Systems*. O'Reilly Media, 2022. Los capítulos 8 (Data Distribution Shifts and Monitoring) y 9 (Continual Learning and Test in Production) son la referencia central de esta unidad. El capítulo 8 cubre en profundidad los tipos de drift, las métricas estadísticas de detección y las estrategias para la recolección de ground truth en producción. El capítulo 9 aborda el reentrenamiento continuo, los triggers de actualización y los patrones de despliegue seguro.
- Sculley, D. et al. *Hidden Technical Debt in Machine Learning Systems*. NeurIPS 2015. El paper fundacional que articula por qué los sistemas ML acumulan deuda técnica de formas distintas al software tradicional, incluyendo la dependencia de datos, el feedback loop y la dificultad de la reproducibilidad.
- Murphy, K. P. *Probabilistic Machine Learning: Advanced Topics*. MIT Press, 2023. Capítulo sobre distributional shift para la fundamentación matemática de las métricas de drift.

**Recursos complementarios**

- Google Site Reliability Engineering. *SRE Book*. Google, 2016. Disponible en: https://sre.google/sre-book/table-of-contents/. El capítulo sobre Service Level Objectives y los golden signals es directamente aplicable a sistemas ML.
- prometheus-client (Python). Repositorio oficial con ejemplos de implementación de exporters personalizados. Disponible en: https://github.com/prometheus/client_python
- Seldon Core. *MLServer*. Framework de serving de modelos con soporte nativo para métricas Prometheus. Disponible en: https://github.com/SeldonIO/MLServer
