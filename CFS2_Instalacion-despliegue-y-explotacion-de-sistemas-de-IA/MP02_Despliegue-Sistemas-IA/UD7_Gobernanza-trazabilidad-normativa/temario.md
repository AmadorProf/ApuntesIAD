# UD7 · Gobernanza, trazabilidad y cumplimiento normativo en sistemas de IA desplegados

---

## 1. Introducción

La puesta en producción de un sistema de inteligencia artificial no cierra el ciclo de responsabilidad del equipo técnico: lo abre. Durante el desarrollo, los errores son visibles y corregibles; una vez desplegado, un modelo toma decisiones que afectan a personas reales, en tiempo real, con escrutinio limitado. Esta asimetría entre la potencia del sistema y la capacidad de supervisión humana es exactamente el problema que la **gobernanza de IA** intenta resolver.

Conviene diferenciar gobernanza de seguridad técnica. La seguridad técnica se ocupa de que el sistema no sea vulnerado, de que los datos estén cifrados y de que las interfaces sean resistentes a ataques. La gobernanza abarca un conjunto más amplio de preguntas: ¿quién autoriza que un modelo entre en producción? ¿Cómo se documenta que el modelo que sirve predicciones hoy es el mismo que fue evaluado la semana pasada? ¿Qué queda registrado cuando el sistema comete un error? ¿A quién rinde cuentas el equipo que lo opera? ¿Qué ocurre si la autoridad reguladora solicita una explicación de una decisión automatizada adoptada hace dieciocho meses?

Estas preguntas articulan tres conceptos centrales que vertebran la unidad:

- **Accountability** (rendición de cuentas): la capacidad de identificar, en cualquier momento, quién tomó qué decisión sobre el sistema —humana o automatizada— y en virtud de qué criterios.
- **Transparencia**: la posibilidad de explicar el comportamiento del sistema a distintos tipos de audiencia (usuarios, reguladores, auditores, dirección), con el nivel de detalle que cada audiencia requiere.
- **Auditoría**: el proceso estructurado mediante el cual un agente —interno o externo— verifica que el sistema funciona conforme a los estándares técnicos, organizativos y normativos declarados.

La gobernanza no es un conjunto de documentos que se rellenan una vez y se archivan. Es una práctica continua que se integra en el ciclo de vida del modelo: desde el diseño hasta la retirada. En el contexto de MLOps, esto significa instrumentar los pipelines de datos, entrenamiento y serving para que produzcan evidencias verificables de su propio comportamiento.

Esta unidad recorre los marcos normativos y técnicos que materializan esa práctica: los marcos de gestión de riesgos de NIST e ISO, las herramientas de linaje de modelos y datos, los protocolos de auditoría y logging, y las obligaciones concretas que impone el Reglamento de Inteligencia Artificial de la Unión Europea (EU AI Act) a los sistemas desplegados en territorio comunitario.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Describir la estructura del NIST AI Risk Management Framework (AI RMF 1.0) e identificar las cuatro funciones principales y su aplicación en un entorno MLOps.
2. Enumerar los requisitos principales de la norma ISO/IEC 42001:2023 y compararla con el AI RMF en términos de alcance y mecanismo de certificación.
3. Implementar pipelines de linaje de modelos y datos utilizando ML Metadata (MLMD), MLflow Model Registry, OpenLineage/Marquez y Apache Atlas.
4. Diseñar un esquema de logging de decisiones automatizadas que cumpla los principios de trazabilidad, no repudio y proporcionalidad en la retención.
5. Clasificar un sistema de IA según las categorías de riesgo del EU AI Act e identificar las obligaciones técnicas aplicables a sistemas de alto riesgo.
6. Producir la documentación técnica mínima exigida por el Anexo IV del EU AI Act y redactar un modelo de informe de incidente de IA.
7. Explicar los derechos del interesado en decisiones automatizadas conforme al artículo 22 del RGPD y articular el procedimiento de respuesta correspondiente.
8. Realizar una auditoría técnica básica de un sistema ML desplegado, aplicando los criterios aprendidos.

---

## 3. Marcos de gobernanza en MLOps

### 3.1 NIST AI Risk Management Framework (AI RMF 1.0)

El **NIST AI RMF 1.0**, publicado en enero de 2023 por el National Institute of Standards and Technology de Estados Unidos, es el marco de referencia más utilizado en entornos industriales para gestionar los riesgos asociados a sistemas de IA. A diferencia de un estándar prescriptivo, el AI RMF es un marco voluntario, orientado a principios, que organiza las actividades de gestión de riesgos en torno a cuatro funciones nucleares:

**GOVERN** es la función transversal. Establece la cultura organizativa, las políticas, los roles y las estructuras de rendición de cuentas que hacen posibles las otras tres funciones. En la práctica, GOVERN se traduce en: definir quién tiene autoridad para aprobar un modelo en producción, establecer políticas de uso aceptable de la IA, crear comités de revisión, asignar responsables de riesgo y documentar el apetito de riesgo de la organización en relación con sistemas automatizados.

**MAP** se ocupa de contextualizar el riesgo. Consiste en identificar el propósito del sistema, el entorno de despliegue, las partes interesadas afectadas y los posibles impactos negativos. En términos prácticos, MAP produce una ficha de riesgo que describe el caso de uso, la población afectada, los sesgos potenciales del conjunto de datos y los modos de fallo conocidos.

**MEASURE** cuantifica el riesgo identificado. Incluye la evaluación de métricas de rendimiento, equidad, robustez y explicabilidad del modelo. No se limita a métricas técnicas: también incorpora evaluaciones cualitativas de impacto social. En un pipeline MLOps, MEASURE se materializa en los tests automatizados del modelo, los informes de evaluación y los dashboards de monitorización en producción.

**MANAGE** cierra el ciclo: define los planes de respuesta, mitigación y remediación cuando el riesgo supera los umbrales establecidos. Incluye los procedimientos de rollback, los planes de contingencia y los protocolos de notificación a partes interesadas en caso de incidente.

El NIST también publica el documento complementario **AI RMF Playbook**, que traduce cada función en categorías, subcategorías y ejemplos de acción concretos, organizados de forma similar a los controles del NIST Cybersecurity Framework.

### 3.2 ISO/IEC 42001:2023 — Sistema de Gestión de IA

La norma **ISO/IEC 42001:2023** es el primer estándar internacional certificable para sistemas de gestión de inteligencia artificial. Publicada en diciembre de 2023, sigue la estructura de alto nivel (HLS) común a normas como ISO 9001 (calidad) o ISO 27001 (seguridad de la información), lo que facilita su integración en organizaciones que ya disponen de esas certificaciones.

Los requisitos principales se organizan en diez cláusulas:

- **Contexto de la organización**: comprensión del entorno, partes interesadas y alcance del sistema de gestión.
- **Liderazgo**: compromiso de la alta dirección, política de IA, roles y responsabilidades.
- **Planificación**: identificación de riesgos y oportunidades, objetivos del sistema de gestión.
- **Soporte**: recursos, competencias, concienciación, comunicación y documentación.
- **Operación**: planificación y control operacional, evaluación del impacto de la IA, gestión del ciclo de vida del sistema.
- **Evaluación del desempeño**: seguimiento, medición, auditoría interna, revisión por la dirección.
- **Mejora**: no conformidades, acciones correctivas, mejora continua.

La diferencia más relevante con el AI RMF es que ISO/IEC 42001 **permite la certificación por tercera parte**, lo que la convierte en un instrumento con valor contractual y regulatorio directo. Varias autoridades nacionales y el propio proceso de normalización del EU AI Act reconocen la certificación ISO/IEC 42001 como evidencia de conformidad con determinados requisitos del Reglamento.

### 3.3 Comparativa de marcos

| Dimensión | NIST AI RMF 1.0 | ISO/IEC 42001:2023 |
|---|---|---|
| Origen | EE.UU. (NIST) | Internacional (ISO/IEC JTC 1) |
| Naturaleza | Voluntario, basado en principios | Certificable, requisitos normativos |
| Estructura | 4 funciones (GOVERN, MAP, MEASURE, MANAGE) | Estructura HLS de 10 cláusulas |
| Certificación | No aplica | Certificación por tercera parte |
| Integración con otros sistemas | Referencia cruzada con NIST CSF | Integración nativa con ISO 9001 e ISO 27001 |
| Reconocimiento regulatorio UE | Referencia técnica | Posible equivalencia parcial con EU AI Act |

### 3.4 Qué se gobierna en MLOps

La gobernanza en un entorno MLOps tiene cuatro objetos concretos:

**Modelos**: versión, hiperparámetros, métricas de evaluación, fecha de entrenamiento, conjunto de datos utilizado, aprobaciones recibidas antes del despliegue y estado actual (staging, producción, retirado).

**Datos**: origen, transformaciones aplicadas, versión del esquema, distribución estadística en el momento del entrenamiento y en producción (data drift), y cumplimiento de los requisitos de calidad definidos.

**Accesos**: quién puede aprobar el paso de un modelo a producción, quién puede consultar logs de auditoría, quién puede modificar umbrales de decisión del sistema. La gobernanza de accesos se implementa mediante control de acceso basado en roles (RBAC) y se audita periódicamente.

**Decisiones automatizadas**: el registro de cada decisión tomada por el modelo —o que el modelo haya influido de forma determinante— con los inputs correspondientes, la versión del modelo activo, el timestamp, el nivel de confianza y el resultado. Este registro es la materia prima de la auditoría.

---

## 4. Linaje de modelos y datos

El **linaje** es el grafo que conecta cada artefacto del ciclo de vida de un sistema de IA —datasets, modelos, predicciones— con los procesos que los produjeron y los artefactos que los originaron. Sin linaje, la trazabilidad es imposible: no se puede responder a la pregunta "¿con qué datos se entrenó el modelo que tomó esta decisión hace seis meses?".

### 4.1 ML Metadata (MLMD) de Kubeflow

**ML Metadata (MLMD)** es la biblioteca de metadatos de TFX (TensorFlow Extended) y Kubeflow Pipelines. Proporciona un almacén estructurado para registrar tres tipos de entidades:

- **Artefactos**: entidades de datos que entran o salen de un paso del pipeline. Ejemplos: un dataset CSV, un modelo serializado, un informe de evaluación, un conjunto de predicciones.
- **Ejecuciones**: instancias de un componente o paso del pipeline. Cada ejecución registra sus inputs (artefactos consumidos), sus outputs (artefactos producidos) y sus propiedades (hiperparámetros, métricas, estado).
- **Contextos**: agrupaciones lógicas de artefactos y ejecuciones. Un pipeline completo es un contexto; una versión de experimento es otro contexto.

MLMD permite reconstruir el linaje completo hacia atrás (dado un modelo, ¿qué datos y transformaciones lo produjeron?) y hacia adelante (dado un dataset, ¿qué modelos se entrenaron con él?). Esta capacidad es esencial cuando se detecta un problema en los datos de origen y es necesario identificar todos los modelos afectados.

### 4.2 MLflow Model Registry como fuente de verdad del linaje

**MLflow Model Registry** centraliza la gestión del ciclo de vida de los modelos registrados. Cada modelo en el registro tiene:

- Un nombre y una versión auto-incremental.
- Metadatos del run de entrenamiento que lo originó (parámetros, métricas, artefactos asociados).
- Un estado en el ciclo de vida: `Staging`, `Production` o `Archived`.
- Un historial de transiciones de estado con el usuario que las realizó y el timestamp.
- Anotaciones y etiquetas libres para información adicional.

En términos de gobernanza, MLflow Model Registry implementa un **flujo de aprobación**: un modelo no puede pasar a producción sin que un usuario autorizado ejecute la transición de estado. Ese evento queda registrado de forma permanente, lo que satisface el requisito de accountability. Combinado con MLMD, el registro proporciona la fuente de verdad del linaje técnico del modelo.

### 4.3 OpenLineage y Marquez

**OpenLineage** es un protocolo abierto (especificación JSON) para la recolección de metadatos de linaje de datos en pipelines de procesamiento. Fue originalmente desarrollado por WeWork/Astronomer y actualmente es un proyecto de la LFAI & Data Foundation. Define un modelo de eventos estandarizado que describe los inputs y outputs de cada trabajo de transformación de datos.

**Marquez** es el servidor de referencia de OpenLineage: recibe eventos OpenLineage mediante una API REST, los almacena y expone una interfaz web y una API para consultar el linaje de datasets y trabajos. La combinación OpenLineage + Marquez permite visualizar el grafo completo de dependencias entre datasets y los pipelines que los procesan, con independencia de la tecnología subyacente (Spark, dbt, Airflow, etc.).

La integración con Airflow, por ejemplo, hace que cada DAG y cada tarea emita automáticamente eventos OpenLineage sin modificar el código de las tareas. Esto es especialmente valioso en organizaciones con pipelines heterogéneos: el linaje se captura de forma consistente sin instrumentación ad hoc.

### 4.4 Apache Atlas para linaje de datos

**Apache Atlas** es la plataforma de gobernanza de datos de referencia en el ecosistema Hadoop/Hive. Proporciona un catálogo de datos con soporte nativo para linaje, clasificaciones de datos, políticas de acceso y búsqueda semántica. A diferencia de OpenLineage, Atlas es un sistema completo que incluye tanto el almacenamiento de metadatos como la interfaz de usuario y las integraciones con el ecosistema Apache (Hive, HBase, Sqoop, Kafka, Falcon).

Atlas es especialmente útil en entornos donde los datos de entrenamiento provienen de sistemas de datos corporativos (data warehouses, lagos de datos Hadoop) y es necesario trazarlos hasta su origen en sistemas transaccionales.

### 4.5 Ejemplo de linaje completo

El siguiente esquema ilustra un linaje completo de extremo a extremo:

```
[Fuente de datos: CRM PostgreSQL]
        |
        v (ETL con Apache Spark — registrado en OpenLineage/Marquez)
[Dataset raw: s3://data/raw/clientes_2024Q1.parquet]
        |
        v (Preprocessing pipeline — artefacto MLMD tipo Dataset)
[Dataset procesado: s3://data/processed/clientes_2024Q1_cleaned.parquet]
        |
        v (Training run MLflow — run_id: abc123)
[Modelo: RandomForestClassifier v1.2.3 — registrado en MLflow Model Registry]
        |
        v (Transición a Production — aprobada por: jefe.datos@empresa.com — 2024-03-15T10:23:00Z)
[Modelo en producción: serving endpoint /api/v1/predict]
        |
        v (Log de decisiones — registrado en sistema de auditoría)
[Predicción: cliente_id=78432, score=0.87, decisión=APROBADO, timestamp=2024-03-20T14:05:33Z]
```

Este grafo permite responder a cualquier pregunta de auditoría o regulatoria sobre la cadena de custodia del sistema.

---

## 5. Auditorías de sistemas de IA

### 5.1 Tipos de auditoría

**Auditoría interna**: realizada por el propio equipo de la organización, típicamente por un equipo independiente del que desarrolla y opera el sistema (segunda línea de defensa). Su objetivo es verificar el cumplimiento interno de las políticas y detectar desviaciones antes de que se conviertan en incidentes o problemas regulatorios. Se realiza con periodicidad establecida (trimestral, semestral) y también de forma reactiva tras un incidente.

**Auditoría externa**: realizada por una entidad tercera contratada por la organización. Proporciona una perspectiva independiente y su resultado tiene mayor credibilidad ante clientes, reguladores e inversores. En el contexto de ISO/IEC 42001, la auditoría externa es el mecanismo de certificación.

**Auditoría regulatoria**: iniciada por la autoridad competente (en España, la Agencia Española de Supervisión de la Inteligencia Artificial, AESIA, en el marco del EU AI Act). El operador del sistema está obligado a facilitar el acceso a la documentación técnica, los logs de auditoría y el sistema en funcionamiento. El incumplimiento puede derivar en sanciones.

### 5.2 Estructura de una auditoría técnica de sistema ML

Una auditoría técnica de un sistema ML en producción sigue, típicamente, esta estructura:

1. **Alcance y contexto**: definición del sistema auditado, su versión, su entorno de despliegue y el período auditado.
2. **Revisión de documentación**: ficha técnica del modelo, documentación de datos, registros de evaluación, historial de versiones, registros de incidentes previos.
3. **Verificación del linaje**: comprobación de que el modelo en producción es el modelo documentado, mediante hashes o checksums de los artefactos.
4. **Revisión de métricas de rendimiento**: evolución del rendimiento del modelo en producción durante el período auditado, comparada con las métricas de evaluación iniciales.
5. **Revisión de logs de decisiones**: muestreo y análisis de logs para verificar consistencia, completitud y ausencia de anomalías.
6. **Evaluación de controles de acceso**: verificación de que solo los usuarios autorizados han realizado operaciones sensibles (despliegue, modificación de umbrales, acceso a logs).
7. **Revisión de incidentes**: análisis de los incidentes registrados, las causas raíz identificadas y las acciones correctivas implementadas.
8. **Hallazgos y recomendaciones**: categorización de hallazgos por severidad (crítico, alto, medio, bajo) y recomendaciones de acción con plazos.

### 5.3 Logging de decisiones automatizadas

El log de auditoría de decisiones automatizadas es la evidencia primaria de la actividad del sistema. Su diseño debe responder a cuatro preguntas: ¿qué registrar?, ¿durante cuánto tiempo?, ¿en qué formato? y ¿cómo protegerlo?

**Qué registrar en cada evento de decisión**:
- **Identificador único del evento** (UUID v4 o equivalente).
- **Timestamp** en formato ISO 8601 con zona horaria UTC.
- **Versión del modelo** (nombre, versión semántica y hash del artefacto).
- **Inputs de la solicitud**: los atributos que el modelo recibió como input. En sistemas con datos personales, puede ser necesario anonimizar o pseudonimizar antes del log.
- **Output del modelo**: la predicción o puntuación producida.
- **Decisión resultante**: la acción tomada a partir del output (aprobado, rechazado, derivado a revisión humana).
- **Nivel de confianza o probabilidad**: el score de confianza asociado a la decisión.
- **Identificador del solicitante**: el sistema o usuario que invocó el modelo.
- **Identificador del sujeto afectado**: cuando aplica (sujeto a normativa de protección de datos).

**Cuánto tiempo retener**: el EU AI Act establece que los logs de sistemas de alto riesgo deben conservarse al menos diez años. El RGPD, por otro lado, limita la retención de datos personales al tiempo necesario para el fin declarado. La resolución de esta tensión pasa por separar los logs de auditoría técnica (sin datos personales) de los registros de decisiones que contienen datos del interesado, con políticas de retención diferenciadas.

**Formato**: JSON estructurado con esquema versionado es el estándar de facto. El uso de un esquema explícito (JSON Schema o Avro) facilita la validación automática y la evolución controlada del formato a lo largo del tiempo.

**Principio de no repudio**: los logs de auditoría deben almacenarse de forma que no puedan ser modificados ni eliminados sin dejar rastro. Las técnicas habituales incluyen: escritura en almacenamiento inmutable (WORM: Write Once Read Many), firma criptográfica de cada registro o uso de un ledger con hash encadenado (similar a una estructura blockchain simplificada). El objetivo es garantizar que los logs presentados en una auditoría o procedimiento legal son auténticos.

### 5.4 Gestión del ciclo de vida de los logs

Los logs de auditoría tienen su propio ciclo de vida: generación, almacenamiento activo, archivo, y eventual destrucción (cuando la normativa lo permite). La gestión de este ciclo debe estar documentada en una política de retención de logs aprobada por la dirección. Los puntos clave son:

- Definición de los períodos de retención por categoría de log.
- Procedimientos de archivo a almacenamiento de bajo coste tras el período activo.
- Controles de acceso diferenciados entre el período activo y el período de archivo.
- Procedimiento de destrucción segura al final del período de retención, con registro de la destrucción.

---

## 6. Cumplimiento EU AI Act

El **Reglamento (UE) 2024/1689**, conocido como EU AI Act, es el primer marco regulatorio integral para sistemas de IA en el mundo. Aprobado en junio de 2024 y con aplicación progresiva hasta 2027, establece un sistema de clasificación de riesgos con obligaciones diferenciadas según la categoría.

### 6.1 Sistemas de IA de alto riesgo (Anexo III)

El Anexo III del EU AI Act enumera las categorías de uso que determinan que un sistema es de alto riesgo. Incluyen:

- Infraestructuras críticas (energía, agua, transporte).
- Educación y formación profesional (admisión, evaluación de estudiantes).
- Empleo y gestión de trabajadores (selección, evaluación, gestión).
- Acceso a servicios esenciales privados y públicos (scoring de crédito, evaluación de elegibilidad para prestaciones, seguros de vida y salud).
- Aplicación de la ley (evaluación del riesgo de reincidencia, análisis de evidencias).
- Gestión de migración y asilo.
- Administración de justicia y procesos democráticos.
- Seguridad de productos (regulados por directivas de seguridad de la UE con componente de IA).

Los sistemas que entren en estas categorías están sujetos al conjunto completo de obligaciones del Título III del Reglamento.

### 6.2 Obligaciones técnicas de los sistemas de alto riesgo

**Artículo 9 — Sistema de gestión de riesgos**: el proveedor debe establecer, implementar, documentar y mantener un sistema de gestión de riesgos a lo largo del ciclo de vida del sistema. El sistema debe identificar y analizar los riesgos conocidos y razonablemente previsibles, evaluar los riesgos tras las medidas de mitigación adoptadas y adoptar medidas adecuadas de gestión de riesgos.

**Artículo 10 — Datos y gobernanza de datos**: los datos de entrenamiento, validación y prueba deben estar sujetos a prácticas adecuadas de gobernanza y gestión. Esto incluye: elección de conjuntos de datos relevantes y representativos, examen de posibles sesgos, identificación de lagunas y deficiencias en los datos. Los datos deben ser pertinentes, suficientemente representativos y, en la medida de lo posible, libres de errores y completos.

**Artículo 11 + Anexo IV — Documentación técnica**: antes de la puesta en el mercado, el proveedor debe elaborar la documentación técnica conforme al Anexo IV. Esta documentación debe mantenerse actualizada y ponerse a disposición de las autoridades competentes cuando lo soliciten.

**Artículo 12 — Conservación de registros**: los sistemas de alto riesgo deben tener capacidad técnica para conservar automáticamente registros de actividades (logs) durante el funcionamiento. Los registros deben incluir el período de actividad, los datos de referencia utilizados y los umbrales aplicados. El período de conservación debe ser de al menos diez años.

**Artículo 13 — Transparencia e información a los usuarios**: los sistemas deben diseñarse de forma que las instrucciones de uso sean suficientemente transparentes para que los usuarios puedan comprender sus capacidades y limitaciones, interpretar los outputs y actuar de forma apropiada. La información mínima que debe acompañar al sistema incluye: identidad y datos de contacto del proveedor, características del sistema, rendimiento previsto, limitaciones conocidas, nivel de precisión y métricas de rendimiento relevantes.

**Artículo 14 — Supervisión humana**: los sistemas deben diseñarse de forma que puedan ser supervisados efectivamente por personas físicas durante el período de uso. Las medidas de supervisión humana deben permitir a los usuarios: comprender las capacidades y limitaciones del sistema, detectar y gestionar posibles riesgos o errores, y anular o interrumpir el sistema mediante un mecanismo de "parada de emergencia".

**Artículo 15 — Exactitud, robustez y ciberseguridad**: los sistemas deben alcanzar un nivel adecuado de exactitud, robustez y ciberseguridad durante todo su ciclo de vida. Deben ser resilientes frente a errores, fallos o inconsistencias que puedan ocurrir durante el uso, frente a manipulaciones o datos adversariales, y frente a sesgos derivados de las limitaciones de los datos de entrenamiento.

### 6.3 Sistemas GPAI con riesgo sistémico

Los modelos de IA de uso general (GPAI, General Purpose AI) con capacidades que superan los 10^25 FLOPs de entrenamiento computacional están sujetos a obligaciones adicionales por su potencial riesgo sistémico. Estas incluyen: realización de evaluaciones de modelos adversariales (red-teaming), notificación de incidentes graves a la Comisión Europea, protección contra ciberseguridad y reporte de eficiencia energética.

### 6.4 Notificación a AESIA

En España, la **Agencia Española de Supervisión de la Inteligencia Artificial (AESIA)** es la autoridad nacional competente para la supervisión del EU AI Act. Los proveedores de sistemas de alto riesgo deben registrar sus sistemas en la base de datos de la UE prevista en el artículo 71, antes de su puesta en el mercado. Cualquier incidente grave o mal funcionamiento que pueda constituir una infracción del Reglamento debe notificarse a AESIA sin demora injustificada.

---

## 7. Reporting regulatorio

### 7.1 Documentación técnica mínima según Anexo IV

El Anexo IV del EU AI Act especifica el contenido mínimo de la documentación técnica que deben elaborar los proveedores de sistemas de alto riesgo. Los apartados principales son:

1. **Descripción general del sistema**: nombre, versión, finalidad prevista, categoría de riesgo, interacciones con otros sistemas.
2. **Descripción detallada**: arquitectura del sistema, soluciones de diseño adoptadas, lógica y funcionamiento del sistema, descripción de los componentes de software y hardware.
3. **Información sobre los datos de entrenamiento**: fuentes de datos, procedimientos de recopilación y preparación, características de los conjuntos de datos, medidas de examen de sesgos.
4. **Descripción del proceso de entrenamiento**: metodología, técnicas y recursos utilizados en el entrenamiento, validación y prueba.
5. **Métricas de rendimiento**: métricas utilizadas para medir exactitud, robustez y cumplimiento con respecto a personas o grupos de personas afectados.
6. **Medidas de supervisión humana**: descripción de las medidas técnicas para facilitar la interpretación de los outputs por parte de los usuarios.
7. **Gestión de riesgos**: descripción del sistema de gestión de riesgos implementado conforme al artículo 9.
8. **Información post-comercialización**: descripción del plan de monitorización post-comercialización.

Esta documentación no es un documento estático: debe mantenerse actualizada a lo largo del ciclo de vida del sistema y refleja cualquier cambio sustancial que pueda requerir una nueva evaluación de conformidad.

### 7.2 Respuesta a solicitudes de explicación (RGPD art. 22)

El artículo 22 del Reglamento General de Protección de Datos (RGPD) establece el derecho del interesado a no ser objeto de una decisión basada únicamente en el tratamiento automatizado, incluida la elaboración de perfiles, que produzca efectos jurídicos sobre él o le afecte significativamente de modo similar. Cuando el responsable del tratamiento aplica este tipo de decisiones —en los casos en que está permitido hacerlo— está obligado a facilitar al interesado, como mínimo:

- El derecho a obtener intervención humana.
- El derecho a expresar su punto de vista.
- El derecho a impugnar la decisión.
- El derecho a obtener información significativa sobre la lógica aplicada.

El procedimiento de respuesta que debe implementar el operador del sistema incluye: un canal formal de solicitud accesible para el interesado, un plazo de respuesta máximo de un mes (prorrogable dos meses en casos complejos), un procedimiento interno para localizar los logs de la decisión correspondiente, y un proceso para producir una explicación comprensible de los factores principales que determinaron la decisión.

Desde el punto de vista técnico, esto implica que el sistema debe ser capaz de recuperar, dado un identificador de decisión, todos los inputs, el modelo utilizado, los valores de las características más influyentes (mediante técnicas como SHAP o LIME) y el razonamiento aplicado para llegar al resultado. Este requisito debe considerarse en el diseño del sistema, no como un añadido posterior.

### 7.3 Modelo de informe de incidente de IA

Un incidente de IA es cualquier evento en el que el sistema produce un resultado que causa o puede causar daño a personas físicas o jurídicas, o que supone una desviación significativa del rendimiento esperado. El informe de incidente debe contener, como mínimo:

- **Identificación del incidente**: identificador único, fecha y hora de detección, fecha y hora estimada del inicio del incidente.
- **Descripción del incidente**: qué ocurrió, qué sistema estaba activo, en qué entorno (producción, staging), cómo se detectó (alerta automática, reporte de usuario, auditoría).
- **Impacto**: número y categoría de personas afectadas, tipo de daño (económico, reputacional, físico, psicológico), decisiones afectadas.
- **Causa raíz preliminar**: análisis técnico inicial de la causa del incidente.
- **Medidas de contención inmediatas**: acciones tomadas para limitar el daño mientras se investiga la causa raíz.
- **Comunicación**: a quién se notificó, cuándo y mediante qué canal (interesados, AESIA, otras autoridades).
- **Acciones correctivas**: plan de remediación con responsables y plazos.
- **Lecciones aprendidas**: qué cambios en proceso, técnica o documentación se derivan del incidente.

### 7.4 Informes de transparencia para autoridades

Las autoridades competentes pueden solicitar al operador de un sistema de alto riesgo que proporcione informes de transparencia sobre el funcionamiento del sistema durante un período determinado. Estos informes deben incluir: resumen del rendimiento del sistema, número de decisiones tomadas, distribución de resultados, incidentes registrados y resueltos, cambios de versión del modelo realizados y sus justificaciones, y estado del sistema de gestión de riesgos.

---

## 8. Actividades prácticas

### Actividad 1 — Mapeo de riesgos con el NIST AI RMF

**Descripción**: Selecciona un caso de uso de IA de entre los propuestos por el formador (scoring de crédito, selección de personal, triaje médico o detección de fraude). Aplica las cuatro funciones del NIST AI RMF para producir una ficha de riesgo completa del sistema hipotético. La ficha debe incluir: descripción del caso de uso y contexto de despliegue (MAP), identificación de al menos cinco riesgos con su probabilidad e impacto estimados (MEASURE), propuesta de al menos tres controles de mitigación (MANAGE) y descripción de la estructura de gobernanza organizativa requerida (GOVERN).

**Entregable**: Documento de tres a cuatro páginas con la ficha de riesgo.

**Criterios de evaluación**: Rigor en la identificación de riesgos, adecuación de los controles propuestos, coherencia entre las cuatro funciones.

---

### Actividad 2 — Implementación de linaje con MLflow y MLMD

**Descripción**: Partiendo de un notebook de entrenamiento proporcionado por el formador, instrumenta el pipeline para registrar en MLflow el experimento, los parámetros, las métricas y el modelo resultante. Registra el modelo en el MLflow Model Registry y documenta la transición de estado a `Staging`. Adicionalmente, configura MLMD para registrar los artefactos del pipeline (dataset, modelo evaluado, modelo registrado) como artefactos vinculados mediante ejecuciones, de forma que sea posible reconstruir el linaje completo a partir del ID del modelo.

**Entregable**: Notebook instrumentado + captura del grafo de linaje en MLflow y MLMD.

**Criterios de evaluación**: Correcta instrumentación del pipeline, completitud del linaje registrado, capacidad de reconstruir el linaje desde el modelo hacia el dataset de origen.

---

### Actividad 3 — Diseño de esquema de logging para decisiones automatizadas

**Descripción**: Un sistema de scoring de préstamos personales debe registrar todas sus decisiones para cumplir con el EU AI Act (art. 12) y el RGPD (art. 22). Diseña el esquema JSON del log de decisiones, justificando cada campo. Define la política de retención: qué campos se retienen durante diez años (sin datos personales) y cuáles se eliminan o pseudonimizan al cabo de dos años. Describe el mecanismo técnico que garantiza la inmutabilidad de los logs (principio de no repudio). Finalmente, escribe el procedimiento de respuesta a una solicitud de explicación de un cliente sobre una decisión de rechazo de préstamo.

**Entregable**: Esquema JSON comentado + documento de política de retención y procedimiento de respuesta (dos a tres páginas).

**Criterios de evaluación**: Completitud del esquema, coherencia entre la política de retención y los requisitos normativos, practicidad del procedimiento de respuesta.

---

### Actividad 4 — Simulación de auditoría regulatoria

**Descripción**: En grupos de tres personas, simula una auditoría regulatoria de un sistema de IA de alto riesgo. Un subgrupo asume el rol de equipo auditor (AESIA) y el otro el de operador del sistema. El operador dispondrá de una carpeta de documentación simulada del sistema (proporcionada por el formador) con deficiencias intencionadas. El equipo auditor debe: revisar la documentación, solicitar evidencias específicas, identificar las no conformidades con el EU AI Act y emitir un informe de hallazgos con la categorización de severidad y las recomendaciones de acción. Posteriormente, los roles se invierten.

**Entregable**: Informe de auditoría de cada equipo (dos a tres páginas).

**Criterios de evaluación**: Rigor en la revisión documental, correcta aplicación de los artículos del EU AI Act, claridad del informe de hallazgos, capacidad de argumentar las no conformidades con base normativa.

---

## 9. Referencias

- **EU AI Act (Reglamento (UE) 2024/1689)**: texto completo en EUR-Lex. Disponible en: [https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689)

- **NIST AI Risk Management Framework 1.0 (AI RMF 1.0)**: National Institute of Standards and Technology, enero 2023. Disponible en: [https://airc.nist.gov/RMF](https://airc.nist.gov/RMF) · Documento PDF: [https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf)

- **NIST AI RMF Playbook**: complemento del AI RMF con categorías y acciones. Disponible en: [https://airc.nist.gov/Docs/2](https://airc.nist.gov/Docs/2)

- **ISO/IEC 42001:2023 — Information technology — Artificial intelligence — Management system**: International Organization for Standardization, diciembre 2023. Disponible en: [https://www.iso.org/standard/81230.html](https://www.iso.org/standard/81230.html)

- **ML Metadata (MLMD) — Documentación oficial de TFX**: descripción del modelo de metadatos, artefactos, ejecuciones y contextos. Disponible en: [https://www.tensorflow.org/tfx/guide/mlmd](https://www.tensorflow.org/tfx/guide/mlmd)

- **MLflow Model Registry — Documentación oficial de MLflow**: guía de uso del registro de modelos, ciclo de vida y API. Disponible en: [https://mlflow.org/docs/latest/model-registry.html](https://mlflow.org/docs/latest/model-registry.html)

- **OpenLineage — Especificación del protocolo**: repositorio oficial de la especificación OpenLineage en GitHub. Disponible en: [https://openlineage.io/docs/](https://openlineage.io/docs/) · Especificación JSON: [https://github.com/OpenLineage/OpenLineage/blob/main/spec/OpenLineage.md](https://github.com/OpenLineage/OpenLineage/blob/main/spec/OpenLineage.md)

- **Marquez — Servidor de referencia OpenLineage**: documentación oficial de instalación y uso. Disponible en: [https://marquezproject.ai/docs/](https://marquezproject.ai/docs/)

- **Apache Atlas — Documentación oficial**: guía de administración, linaje y clasificaciones. Disponible en: [https://atlas.apache.org/](https://atlas.apache.org/)

- **RGPD — Artículo 22 — Decisiones individuales automatizadas**: texto del Reglamento (UE) 2016/679 en EUR-Lex. Disponible en: [https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32016R0679](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32016R0679)

- **AESIA — Agencia Española de Supervisión de la Inteligencia Artificial**: información institucional y normativa. Disponible en: [https://www.aesia.gob.es/](https://www.aesia.gob.es/)

- **Directrices del Comité Europeo de Protección de Datos (CEPD) 01/2022 sobre decisiones individuales automatizadas**: disponibles en: [https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-012022-data-subject-rights-automated-decision_es](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-012022-data-subject-rights-automated-decision_es)

---

*UD7 · MP02 Despliegue de Sistemas de IA · CFS2 Instalación, despliegue y explotación de sistemas de IA*
