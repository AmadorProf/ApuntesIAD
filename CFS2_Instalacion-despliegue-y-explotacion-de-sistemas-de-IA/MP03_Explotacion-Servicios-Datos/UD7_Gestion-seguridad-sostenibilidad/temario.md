# UD7 · Gestión integral: seguridad, sostenibilidad y desarrollo profesional

---

## 1. Introducción

Las plataformas de datos e IA procesan en la actualidad algunos de los activos más sensibles de las organizaciones: historiales de comportamiento de clientes, registros de salud, datos financieros, información estratégica de negocio. La seguridad de estas plataformas no puede tratarse como un requisito adicional que se aplica al final del diseño, sino como una propiedad que debe incorporarse desde las fases iniciales de arquitectura —el principio de *security by design*. Este enfoque no solo reduce la superficie de ataque, sino que simplifica el cumplimiento de los marcos normativos que regulan el tratamiento de datos en la Unión Europea, entre los cuales el Reglamento General de Protección de Datos (RGPD) ocupa el lugar central.

La privacidad de los datos en plataformas analíticas presenta tensiones técnicas características que la distinguen de la seguridad en aplicaciones transaccionales. El objetivo del analítico es extraer información estadística agregada de grandes conjuntos de datos; el del RGPD es proteger la privacidad de los individuos cuyos datos se procesan. Estas dos finalidades no son incompatibles, pero su conciliación requiere un conjunto de técnicas específicas: anonimización, pseudonimización, k-anonimato, privacidad diferencial, y controles de acceso granulares que permiten consultar estadísticas sin exponer los datos individuales subyacentes. El profesional de datos debe dominar tanto los conceptos técnicos como su correspondencia con los requisitos normativos: qué garantías ofrece la pseudonimización respecto al RGPD, cuándo la anonimización es suficiente para excluir los datos del ámbito de aplicación del reglamento, o cuándo es obligatorio mantener la capacidad de identificar y corregir datos de un interesado específico.

La sostenibilidad medioambiental del sector de datos e IA es un tema que ha pasado de ser anecdótico a ocupar espacio en las estrategias corporativas de ESG (Environmental, Social and Governance). Los centros de datos representan entre el 1% y el 2% del consumo eléctrico mundial, y la analítica de datos —con sus queries de Spark sobre terabytes de datos, sus modelos de machine learning entrenados durante horas o días, y sus pipelines continuos de procesamiento de eventos— contribuye de forma significativa a esa huella. Las organizaciones que despliegan plataformas de datos tienen la responsabilidad técnica de cuantificar y reducir ese impacto: elegir regiones de cloud con energía renovable, dimensionar los clústers de Spark ajustadamente en lugar de sobre-aprovisionarlos, diseñar queries eficientes que minimicen el escaneo de datos innecesario, y apagar los recursos cuando no están en uso.

El tercer eje de esta unidad aborda el contexto humano y organizativo del trabajo en analítica de datos: la estructura multidisciplinar de los equipos de datos (ingenieros, científicos, analistas, stakeholders de negocio), los mecanismos de colaboración que hacen sostenible el trabajo a largo plazo —documentación de calidad, gestión de deuda técnica, revisiones de código, gestión del conocimiento—, y las prácticas de aprendizaje continuo en un campo que evoluciona a una velocidad que convierte el conocimiento específico de herramientas en perecedero en cuestión de años. La vigilancia tecnológica estructurada —no el consumo pasivo de noticias— es una competencia profesional fundamental que esta unidad busca desarrollar.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Implementar controles de acceso basados en roles (RBAC) y control de acceso a nivel de fila y columna (RLS/CLS) en una plataforma de datos, utilizando herramientas como Apache Ranger o las capacidades nativas de BigQuery y Snowflake.
2. Distinguir técnicamente entre anonimización y pseudonimización, aplicar técnicas de k-anonimato y privacidad diferencial a conjuntos de datos analíticos, y determinar cuándo cada enfoque satisface los requisitos del RGPD.
3. Diseñar e implementar una estrategia de cifrado de datos en reposo y en tránsito para una plataforma de datos en la nube, incluyendo la gestión de claves con AWS KMS, Azure Key Vault o GCP Cloud KMS.
4. Configurar un sistema de auditoría de accesos a datos que registre quién consultó qué datos, cuándo y desde qué sistema, y diseñar los controles de retención y protección del log de auditoría.
5. Cuantificar la huella de carbono de los principales componentes de una plataforma de datos (almacenamiento, queries analíticas, entrenamiento ML) utilizando herramientas de medición disponibles en los proveedores de cloud.
6. Identificar y aplicar al menos cinco técnicas de optimización energética en pipelines de datos (right-sizing de clústers, query optimization, compresión, cacheo, scheduling en horas de baja demanda).
7. Diseñar un plan de gestión de deuda técnica para una plataforma de datos, priorizando las intervenciones según su impacto en mantenibilidad y coste operativo.
8. Elaborar un plan de vigilancia tecnológica estructurada para el área de datos e IA, especificando fuentes, frecuencia de revisión y mecanismo de síntesis y distribución al equipo.

---

## 3. Seguridad en plataformas de analítica

### 3.1 Control de acceso: RBAC, RLS y CLS

El **control de acceso basado en roles** (RBAC, Role-Based Access Control) es el modelo estándar para gestionar quién puede hacer qué en una plataforma de datos. En lugar de asignar permisos directamente a usuarios individuales —lo que genera explosión combinatoria en organizaciones con muchos usuarios y recursos—, los permisos se asignan a roles, y los roles se asignan a usuarios.

En plataformas de datos en la nube, los roles típicos son:

| Rol | Permisos | Ejemplos de usuario |
|---|---|---|
| Data Engineer | Crear, modificar y eliminar tablas. Ejecutar ETL. | Ingenieros de datos |
| Data Analyst | Leer tablas silver y gold. Sin acceso a bronze. | Analistas de negocio |
| Data Scientist | Leer todas las capas. Crear tablas en espacio de trabajo personal. | Científicos de datos |
| Dashboard Consumer | Leer solo vistas agregadas gold expuestas en BI. | Usuarios de negocio |
| Admin | Gestionar permisos, crear recursos, acceso a logs de auditoría. | DBA, Tech Lead |

El **control de acceso a nivel de fila** (RLS, Row-Level Security) permite que diferentes usuarios vean diferentes subconjuntos de filas de la misma tabla según su identidad o rol. Por ejemplo, un analista regional solo ve las ventas de su región, aunque la tabla subyacente contenga las ventas globales. En BigQuery:

```sql
-- Política de seguridad a nivel de fila en BigQuery
CREATE ROW ACCESS POLICY region_filter
ON analytics.ventas_gold
GRANT TO ("group:analistas-region-norte@empresa.com")
FILTER USING (region = 'NORTE');
```

El **control de acceso a nivel de columna** (CLS, Column-Level Security) restringe el acceso a columnas específicas que contienen datos sensibles (DNI, salario, número de cuenta). Los usuarios sin permiso no ven la columna; en algunos motores, ven `NULL` en su lugar.

```sql
-- Enmascaramiento de columna sensible en Snowflake
CREATE MASKING POLICY mask_dni
AS (val STRING) RETURNS STRING ->
    CASE
        WHEN CURRENT_ROLE() IN ('ANALISTA_RRHH', 'ADMIN') THEN val
        ELSE '***-MASKED-***'
    END;

ALTER TABLE empleados.datos_personales
MODIFY COLUMN dni SET MASKING POLICY mask_dni;
```

### 3.2 Anonimización y pseudonimización

El RGPD distingue conceptualmente dos técnicas:

- **Pseudonimización** (art. 4.5 RGPD): sustitución de atributos identificativos directos por identificadores artificiales, de modo que los datos no pueden atribuirse a un interesado sin información adicional mantenida por separado. Los datos pseudonimizados **siguen siendo datos personales** a efectos del RGPD, pero se benefician de un tratamiento más favorable (menores restricciones de base legal, menor impacto en evaluaciones DPIA).

- **Anonimización**: proceso que elimina de forma irreversible la posibilidad de identificar a los interesados, de modo que los datos resultantes quedan **fuera del ámbito de aplicación del RGPD**. El CEPD (Comité Europeo de Protección de Datos) exige que la anonimización sea robusta ante tres ataques: individualización (identificar a un individuo), vinculación (relacionar registros del mismo individuo) y inferencia (deducir atributos del individuo).

El **k-anonimato** es la propiedad de un conjunto de datos en el que cada registro es indistinguible de al menos k-1 otros registros respecto a los atributos quasi-identificativos (combinaciones de atributos no identificativos directamente pero que pueden cruzarse con datos externos para identificar al individuo: código postal, fecha de nacimiento, sexo). La generalización y supresión son las técnicas más usadas para lograr k-anonimato:

```python
# Generalización de código postal para k-anonimato (k=5)
# Reducir el código postal de 5 dígitos a 2 dígitos (provincia)
import pandas as pd

df = pd.read_csv("datos_pacientes.csv")

# Generalización: código postal a nivel provincia
df['cp_generalizado'] = df['codigo_postal'].astype(str).str[:2]

# Supresión: eliminar registros con combinaciones únicas de quasi-identificativos
grupos = df.groupby(['cp_generalizado', 'rango_edad', 'sexo'])
df_kanon = df[grupos['cp_generalizado'].transform('count') >= 5]
```

La **privacidad diferencial** (differential privacy) es el enfoque matemáticamente más riguroso. Garantiza que la presencia o ausencia de cualquier individuo en el conjunto de datos cambia las estadísticas publicadas en un margen controlado por el parámetro epsilon. A menor epsilon, mayor privacidad, mayor distorsión de los resultados. Google implementa privacidad diferencial en sus análisis estadísticos internos; Apple la usa en la recolección de telemetría de iOS. La librería **OpenDP** implementa privacidad diferencial en Python.

### 3.3 Cifrado en reposo y en tránsito

El **cifrado en reposo** protege los datos frente al acceso físico no autorizado al medio de almacenamiento. Los proveedores de cloud ofrecen cifrado en reposo por defecto para todos sus servicios de almacenamiento (S3, Azure Blob Storage, GCS, BigQuery, Snowflake). La cuestión crítica es la **gestión de claves**:

- **Claves gestionadas por el proveedor** (SSE-S3, Google-managed keys): el proveedor gestiona el ciclo de vida de las claves. El proveedor tiene acceso técnico a las claves.
- **Claves gestionadas por el cliente** (CMEK): el cliente crea y gestiona las claves en un servicio de gestión de claves (AWS KMS, Azure Key Vault, GCP Cloud KMS). El proveedor cifra con la clave del cliente. La organización puede revocar el acceso a los datos revocando la clave.
- **BYOK** (Bring Your Own Key): el cliente almacena las claves en su propio hardware (HSM, Hardware Security Module) fuera de la infraestructura del proveedor cloud.

```bash
# Crear una clave gestionada por el cliente en AWS KMS
aws kms create-key \
  --description "Clave CMK para datos analíticos sensibles" \
  --key-usage ENCRYPT_DECRYPT \
  --key-spec SYMMETRIC_DEFAULT

# Aplicar la CMK a un bucket S3
aws s3api put-bucket-encryption \
  --bucket mi-data-lake-sensible \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:eu-west-1:123456789:key/abc123"
      }
    }]
  }'
```

El **cifrado en tránsito** protege los datos durante la transferencia entre sistemas. El estándar es TLS 1.2 mínimo (preferiblemente TLS 1.3) para todas las conexiones: entre clientes y el data warehouse, entre componentes del pipeline (Airflow workers y base de datos, Kafka producers y brokers), y entre microservicios internos. Las plataformas cloud aplican TLS por defecto en todos sus endpoints públicos.

### 3.4 Auditoría de accesos a datos

El log de auditoría registra quién accedió a qué datos, cuándo, desde qué sistema y con qué resultado. Es la evidencia central de cumplimiento para el RGPD (derecho de supervisión del responsable del tratamiento) y para auditorías de seguridad.

Los principales proveedores de cloud ofrecen servicios nativos de auditoría:
- **AWS CloudTrail + S3 Server Access Logging**: registro de todas las llamadas a APIs de AWS.
- **BigQuery Audit Logs**: registro de todas las queries ejecutadas, con información del usuario, tabla consultada, bytes procesados y timestamp.
- **Snowflake — Access History**: tabla del sistema que registra el acceso a nivel de columna, incluyendo qué columnas fueron leídas en cada query.

La política de auditoría debe definir:
1. Qué eventos se registran (mínimo: autenticaciones, accesos a datos sensibles, cambios de permisos, exportaciones de datos).
2. Cuánto tiempo se retienen los logs (mínimo recomendado para datos personales: 12-24 meses de acceso activo + 5 años de archivo).
3. Quién puede acceder a los logs de auditoría (solo administradores designados).
4. Cómo se protege la integridad del log (almacenamiento inmutable, firma digital).

---

## 4. Cumplimiento RGPD en plataformas de datos

### 4.1 Principios del RGPD aplicados a la analítica

El RGPD establece seis principios relativos al tratamiento de datos personales (art. 5) con implicaciones técnicas directas en las plataformas de datos:

| Principio RGPD | Implicación técnica en plataformas de datos |
|---|---|
| Licitud, lealtad y transparencia | Documentar la base legal de cada tratamiento analítico. Registro de actividades de tratamiento (art. 30). |
| Limitación de la finalidad | No usar datos recopilados para una finalidad en análisis con otra finalidad incompatible. Separación lógica de datasets por finalidad. |
| Minimización de datos | No ingestar más datos de los necesarios para el análisis. Eliminar o enmascarar campos no requeridos en la ingesta. |
| Exactitud | Implementar procesos de corrección de datos cuando el interesado ejerce el derecho de rectificación. |
| Limitación del plazo de conservación | Implementar políticas de retención con eliminación automática al vencimiento del plazo. |
| Integridad y confidencialidad | Implementar los controles técnicos de cifrado, control de acceso y auditoría descritos en la sección anterior. |

### 4.2 Derecho al olvido en plataformas de datos

El **derecho de supresión** (art. 17 RGPD) obliga a eliminar los datos personales de un interesado cuando lo solicite y concurra alguna de las circunstancias previstas. En plataformas de datos, esta obligación es técnicamente compleja porque los datos se replican en múltiples capas, se usan como input de modelos ML entrenados, y pueden estar en sistemas de backup.

El procedimiento técnico de supresión en un lakehouse incluye:
1. **Identificación**: localizar todos los registros del interesado en todas las capas (bronze, silver, gold) y en todas las tablas (una herramienta de catálogo de datos con búsqueda por PII facilita enormemente esta etapa).
2. **Eliminación en tablas Delta/Iceberg**: estas tecnologías soportan operaciones `DELETE` con semántica ACID:
   ```sql
   -- Eliminar datos de un interesado en Delta Lake
   DELETE FROM ventas_silver WHERE cliente_id = '78432';
   -- Delta Lake registra la operación en el transaction log; el dato queda
   -- inaccesible pero los ficheros físicos deben eliminarse con VACUUM
   VACUUM ventas_silver RETAIN 0 HOURS;
   ```
3. **Eliminación en backups**: los backups de los datos deben ser eliminados o el interesado debe ser suprimido en los procedimientos de restauración.
4. **Modelos ML**: los modelos ya entrenados con datos del interesado no pueden "desentrenarse" fácilmente. El art. 17 no requiere estrictamente el reentrenamiento del modelo, pero sí que el interesado no sea identificable en las predicciones del sistema.

---

## 5. Impacto ambiental de la analítica de datos

### 5.1 Huella de carbono de la analítica

La huella de carbono de una plataforma de datos proviene de tres fuentes principales:

1. **Consumo de electricidad de los servidores** (scope 2 de emisiones): CPU, GPU, RAM y sistemas de almacenamiento consumen electricidad. La intensidad de carbono de esa electricidad depende del mix energético de la región donde está el centro de datos.
2. **Energía de refrigeración**: los centros de datos requieren sistemas de refrigeración que pueden consumir entre el 30% y el 50% adicional de la energía usada por los servidores (PUE, Power Usage Effectiveness).
3. **Fabricación del hardware** (scope 3 de emisiones): la fabricación de servidores, almacenamiento y redes tiene un coste de carbono significativo que no aparece en la factura eléctrica.

Los principales proveedores de cloud publican herramientas de estimación de huella de carbono:
- **AWS Customer Carbon Footprint Tool**: disponible en la consola de AWS, desglosa las emisiones por servicio, región y mes.
- **Google Cloud Carbon Footprint**: integrado en la consola de Google Cloud, con datos de intensidad de carbono por región en tiempo real.
- **Azure Emissions Impact Dashboard**: disponible en el portal de Azure.

La librería **CodeCarbon** permite medir la huella de carbono de procesos Python (entrenamientos ML, pipelines de datos) de forma programática:

```python
from codecarbon import EmissionsTracker

tracker = EmissionsTracker(
    project_name="entrenamiento_modelo_clasificacion",
    country_iso_code="ESP",
    cloud_provider="aws",
    cloud_region="eu-west-1"
)

tracker.start()

# ... código de entrenamiento del modelo ...
entrenar_modelo(X_train, y_train)

emisiones = tracker.stop()
print(f"Emisiones: {emisiones:.4f} kg CO2eq")
```

### 5.2 Técnicas de optimización energética en pipelines de datos

**Optimización de queries**: en motores como BigQuery o Spark, el coste computacional (y energético) depende directamente del volumen de datos escaneados. Una query que escanea una tabla de 10 TB cuando solo necesita 100 GB consume 100 veces más recursos que necesario.

```sql
-- Query ineficiente: escanea toda la tabla de logs (10 TB)
SELECT COUNT(*) FROM logs WHERE DATE(timestamp) = '2024-03-15';

-- Query eficiente: usa particionamiento por fecha (escanea solo 10 GB)
SELECT COUNT(*) FROM logs
WHERE timestamp >= '2024-03-15' AND timestamp < '2024-03-16';
-- Requiere que la tabla esté particionada por timestamp
```

**Right-sizing de clústers Spark**: los clústers de Spark se configuran a menudo con recursos estáticos sobredimensionados para evitar fallos por falta de memoria. La política más eficiente energéticamente es el **autoscaling**: el clúster arranca con el mínimo de nodos y escala horizontalmente según la carga.

```python
# Configuración de autoscaling en Databricks
cluster_config = {
    "autoscale": {
        "min_workers": 2,
        "max_workers": 20
    },
    "auto_termination_minutes": 30,  # Apagado automático tras 30 min de inactividad
    "node_type_id": "m5.xlarge"
}
```

**Compresión y formatos columnares**: el formato Parquet con compresión Snappy o Zstandard reduce el tamaño de los ficheros en un 60-80% respecto a CSV sin comprimir, reduciendo proporcionalmente el espacio de almacenamiento y el tiempo de escaneo en queries analíticas.

**Scheduling en horas de baja demanda**: los pipelines batch no críticos deben programarse en franjas horarias donde la red eléctrica tiene menor intensidad de carbono (típicamente madrugada, cuando hay más energía renovable disponible) o en regiones cloud con mayor porcentaje de energía renovable.

**Escalado a cero de recursos**: los servicios de analítica que no se usan continuamente (clústers de Spark, instancias de Jupyter, servidores de Airflow en desarrollo) deben tener configurado el apagado automático cuando no están en uso.

### 5.3 Marcos de referencia de sostenibilidad

- **Green Software Foundation** publica el **Software Carbon Intensity (SCI) Specification**, un estándar para medir y reportar la intensidad de carbono del software en términos de CO2eq por unidad de trabajo (por consulta, por request, por minuto de uso).
- **ISO 14001** es el estándar de gestión medioambiental que muchas organizaciones usan para estructurar sus compromisos de reducción de huella.
- El **EU Green Deal** y la directiva de eficiencia energética de la UE establecen objetivos de reducción de consumo que afectan a las organizaciones que operan centros de datos o infraestructura cloud en territorio europeo.

---

## 6. Trabajo en equipo y organización multidisciplinar

### 6.1 Estructura de equipos de datos

Los equipos de datos modernos combinan perfiles con competencias muy diferentes que deben colaborar de forma efectiva:

| Perfil | Responsabilidad principal | Herramientas nucleares |
|---|---|---|
| Data Engineer | Construcción y mantenimiento de pipelines de datos | Spark, Airflow, dbt, Kafka, infraestructura cloud |
| Data Scientist | Desarrollo de modelos ML y análisis estadístico | Python, sklearn, PyTorch, Jupyter |
| ML Engineer | Despliegue y operación de modelos ML en producción | MLflow, Kubernetes, FastAPI, Triton |
| Analytics Engineer | Modelado de datos gold y capa semántica | dbt, SQL, herramientas de BI |
| Data Analyst | Análisis descriptivo y dashboards para negocio | SQL, Power BI, Tableau, Superset |
| Product Manager de Datos | Priorización del roadmap de datos y comunicación con negocio | Jira, OKRs, comunicación stakeholders |

La fricción más frecuente en estos equipos ocurre en las interfaces entre perfiles: entre data scientists (que producen modelos en notebooks) y ML engineers (que deben desplegarlos en producción), o entre data engineers (que construyen las tablas gold) y analytics engineers (que las modelan para BI). Los **data contracts** descritos en la UD6 son el mecanismo técnico que reduce esta fricción formalizando las expectativas entre productor y consumidor de datos.

### 6.2 Comunicación técnica con stakeholders de negocio

Una de las competencias más valoradas y menos desarrolladas en los profesionales de datos es la capacidad de comunicar hallazgos técnicos complejos a audiencias no técnicas. Los principios fundamentales son:

- **Contexto antes que datos**: antes de mostrar un número o un gráfico, explicar qué pregunta responde y por qué importa a la audiencia.
- **Una sola cifra principal**: los stakeholders de negocio retienen un mensaje por reunión. El análisis debe construirse hacia esa cifra.
- **Incertidumbre explícita**: los modelos ML producen probabilidades, no certezas. La comunicación honesta de la incertidumbre (intervalos de confianza, limitaciones del modelo) evita expectativas irrealistas que generan desconfianza posterior.
- **Acción, no solo información**: cada informe debe terminar con una recomendación de acción concreta y el dueño de esa acción.

---

## 7. Documentación, deuda técnica y aprendizaje continuo

### 7.1 Documentación de plataformas de datos

La documentación de una plataforma de datos cubre cuatro niveles:

1. **Documentación de infraestructura**: cómo está desplegada la plataforma (diagramas de arquitectura, IaC en Terraform, scripts de configuración). Debe residir en el repositorio de código, no en un wiki separado.

2. **Documentación de modelos de datos**: descripción de cada tabla, columna y relación. Implementada en el fichero `schema.yml` de dbt o en el catálogo de datos. Debe incluir definición de negocio (no solo técnica), propietario, y ejemplos de uso.

3. **Documentación de pipelines**: cada DAG de Airflow debe tener una descripción que explique qué hace, cuándo se ejecuta, qué sistemas toca y cuál es el impacto de un fallo. El parámetro `doc_md` de Airflow permite documentación en Markdown dentro del código del DAG.

4. **Runbooks operativos**: procedimientos paso a paso para responder a los incidentes más frecuentes (pipeline fallido, tabla sin actualizar, degradación de calidad de datos). Los runbooks deben ser ejecutables por cualquier miembro del equipo sin necesidad de consultar al autor del pipeline.

### 7.2 Gestión de deuda técnica en plataformas de datos

La deuda técnica en plataformas de datos se acumula de formas características:

- **Notebooks de exploración en producción**: análisis exploratorios que se convierten en pipelines de producción sin refactorización adecuada.
- **Pipelines sin tests**: transformaciones que se ejecutan diariamente sin validación de calidad, acumulando silenciosamente errores de datos.
- **Modelos SQL sin documentación**: tablas gold cuya lógica de negocio solo entiende quien las escribió.
- **Dependencias implícitas**: pipelines que dependen del orden de ejecución de otros sin declararlo explícitamente.
- **Sobre-ingesta**: ingestión de datos que nadie consume, con el coste de almacenamiento y procesamiento asociado.

La gestión de deuda técnica requiere un proceso explícito:

1. **Inventario**: catalogar las áreas de deuda conocida con su impacto estimado (en tiempo de mantenimiento, riesgo operativo o coste).
2. **Priorización**: no toda la deuda merece el mismo esfuerzo de reducción. La deuda en componentes que cambian frecuentemente o que tienen alto impacto en caso de fallo tiene mayor prioridad.
3. **Presupuesto temporal**: reservar un porcentaje fijo del tiempo del equipo (típicamente 20%) para reducción de deuda técnica en cada sprint.
4. **Criterios de aceptación**: definir estándares de calidad que los nuevos pipelines deben cumplir antes de ser considerados "producción": tests de calidad de datos, documentación, runbook, alertas configuradas.

### 7.3 Aprendizaje continuo y vigilancia tecnológica

El ecosistema de datos e IA evoluciona a una velocidad que requiere una práctica sistemática de aprendizaje continuo. La vigilancia tecnológica no es el consumo casual de redes sociales o newsletters, sino un proceso estructurado con fuentes seleccionadas, cadencia de revisión y mecanismo de síntesis.

**Fuentes de referencia primarias** (producen conocimiento, no lo agregan):
- Documentación oficial de las herramientas (dbt, Airflow, Spark, Kafka).
- Artículos de investigación en arXiv (cs.LG, cs.DB) y proceedings de VLDB, SIGMOD, NeurIPS.
- Engineering blogs de organizaciones de referencia: Databricks, Airbnb (Apache Superset fue creado ahí), Lyft (Amundsen), LinkedIn (DataHub, Kafka), Netflix (Iceberg).

**Fuentes de agregación de calidad**:
- The Data Engineering Newsletter (Joe Reis).
- Substack técnico de personas con track record probado.
- GitHub trending en lenguajes Python/SQL/Scala.

**Cadencia recomendada**:
- Revisión diaria: 15 minutos de RSS/newsletter (solo titulares, marcar para lectura profunda).
- Revisión semanal: lectura profunda de 2-3 artículos seleccionados.
- Revisión mensual: revisión de qué herramientas nuevas merecen un prototipo o evaluación técnica.
- Revisión trimestral: actualización del mapa de competencias del equipo y plan de formación.

---

## 8. Actividades prácticas

### Actividad 1 — Implementación de controles de acceso y auditoría

**Descripción**: Sobre el entorno de data warehouse utilizado en unidades anteriores (BigQuery sandbox, DuckDB o Snowflake trial), implementa una política de control de acceso con tres roles diferenciados (Admin, Analyst, Consumer) con los permisos descritos en la sección 3.1. Configura Row-Level Security para una tabla de ventas de forma que cada analista solo pueda ver las ventas de su región (simula dos regiones con dos usuarios distintos). Activa el log de auditoría disponible en la plataforma elegida y genera cinco consultas de prueba con cada rol. Extrae el log de auditoría y construye un informe que muestre: qué usuarios accedieron a qué tablas, cuántas filas leyeron y en qué horario. Finalmente, diseña y documenta la política de retención del log de auditoría.

**Entregable**: Scripts SQL de creación de roles y políticas + informe de auditoría + documento de política de retención.

**Criterios de evaluación**: Correcta implementación de RBAC y RLS, verificación funcional de los controles (con capturas de pantalla), completitud del informe de auditoría, coherencia de la política de retención con el RGPD.

---

### Actividad 2 — Anonimización y análisis de privacidad

**Descripción**: El formador proporcionará un dataset sintético de 10.000 registros con atributos quasi-identificativos (código postal, rango de edad, sexo, diagnóstico médico codificado). Aplica una transformación de k-anonimato con k=5 utilizando técnicas de generalización y supresión. Calcula la pérdida de información resultante (usando la métrica NCP, Normalized Certainty Penalty) y compara el resultado con k=3 y k=10. Determina razonadamente si el dataset resultante con k=5 cumple el criterio de anonimización del RGPD o sigue siendo dato personal pseudonimizado. Implementa adicionalmente una consulta de COUNT con privacidad diferencial usando la librería OpenDP y compara la exactitud del resultado con epsilon=0.1, 1.0 y 10.0.

**Entregable**: Notebook Python con el código de k-anonimato y privacidad diferencial + análisis comparativo + dictamen razonado sobre el estatus RGPD del dataset resultante.

**Criterios de evaluación**: Correcta implementación técnica, rigor del análisis de pérdida de información, calidad del dictamen RGPD, correcta interpretación del parámetro epsilon.

---

### Actividad 3 — Medición y optimización de la huella de carbono

**Descripción**: Instrumenta el pipeline de datos construido en las actividades de la UD6 con la librería CodeCarbon para medir las emisiones de CO2eq de cada etapa (ingesta, transformación silver, transformación gold, tests de calidad). Ejecuta el pipeline y registra las emisiones por etapa. Identifica la etapa con mayor huella y aplica al menos dos optimizaciones (particionamiento de tablas para reducir el scan, compresión Parquet, right-sizing del proceso). Vuelve a medir y compara las emisiones antes y después de las optimizaciones. Calcula la huella anual proyectada si el pipeline se ejecuta diariamente y propón medidas de reducción adicionales.

**Entregable**: Código del pipeline instrumentado + tabla comparativa de emisiones antes/después + informe de sostenibilidad proyectado (una página).

**Criterios de evaluación**: Correcta instrumentación con CodeCarbon, relevancia de las optimizaciones aplicadas, rigor del análisis comparativo, calidad de las propuestas de mejora.

---

### Actividad 4 — Auditoría de deuda técnica y plan de mejora

**Descripción**: El formador proporcionará acceso a un repositorio de datos de ejemplo (proyecto dbt + DAGs de Airflow) con deuda técnica intencionada: pipelines sin tests, modelos sin documentación, DAGs sin manejo de errores, dependencias implícitas y un notebook de exploración ejecutado como pipeline de producción. Realiza un inventario de la deuda técnica identificada, clasificándola por categoría (documentación, calidad, mantenibilidad, seguridad) y estimando el riesgo operativo de cada elemento. Prioriza las intervenciones utilizando una matriz esfuerzo-impacto. Redacta un plan de mejora con las cinco intervenciones de mayor prioridad, especificando para cada una: descripción del problema, solución propuesta, esfuerzo estimado (horas), impacto esperado y criterios de aceptación.

**Entregable**: Inventario de deuda técnica categorizada + matriz esfuerzo-impacto + plan de mejora detallado.

**Criterios de evaluación**: Exhaustividad del inventario, justificación de la priorización, realismo del esfuerzo estimado, claridad y ejecutabilidad del plan de mejora.

---

## 9. Referencias

- **RGPD — Reglamento (UE) 2016/679**: texto completo con todas las modificaciones. Disponible en: [https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32016R0679](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32016R0679)

- **CEPD — Directrices 05/2020 sobre consentimiento según el RGPD** y directrices sobre anonimización. Disponibles en: [https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines_es](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines_es)

- **Apache Ranger — Documentación oficial**: gestión de políticas de seguridad para el ecosistema Hadoop. Disponible en: [https://ranger.apache.org/](https://ranger.apache.org/)

- **AWS Key Management Service — Documentación**: gestión de claves de cifrado, CMEK y rotación. Disponible en: [https://docs.aws.amazon.com/kms/latest/developerguide/overview.html](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html)

- **OpenDP — Librería de privacidad diferencial**: documentación y tutoriales de privacidad diferencial en Python. Disponible en: [https://docs.opendp.org/](https://docs.opendp.org/)

- **CodeCarbon — Herramienta de medición de emisiones de código**: repositorio y documentación. Disponible en: [https://mlco2.github.io/codecarbon/](https://mlco2.github.io/codecarbon/)

- **Green Software Foundation — SCI Specification**: estándar de intensidad de carbono del software. Disponible en: [https://sci.greensoftware.foundation/](https://sci.greensoftware.foundation/)

- **Google Cloud Carbon Footprint**: herramienta de estimación de huella de carbono en GCP. Disponible en: [https://cloud.google.com/carbon-footprint](https://cloud.google.com/carbon-footprint)

- **AWS Customer Carbon Footprint Tool**: documentación de la herramienta de huella de carbono de AWS. Disponible en: [https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/what-is-ccft.html](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/what-is-ccft.html)

- **AEPD — Guía de análisis de riesgos para el tratamiento de datos personales**: guía práctica de la Agencia Española de Protección de Datos. Disponible en: [https://www.aepd.es/guias/guia-analisis-de-riesgos.pdf](https://www.aepd.es/guias/guia-analisis-de-riesgos.pdf)

- **Snowflake — Column-level security and dynamic data masking**: documentación oficial de enmascaramiento. Disponible en: [https://docs.snowflake.com/en/user-guide/security-column-intro](https://docs.snowflake.com/en/user-guide/security-column-intro)

- **BigQuery Row-Level Security — Documentación oficial**: políticas de acceso a nivel de fila en BigQuery. Disponible en: [https://cloud.google.com/bigquery/docs/row-level-security-intro](https://cloud.google.com/bigquery/docs/row-level-security-intro)

---

*UD7 · MP03 Explotación de Servicios de Datos y Analítica · CFS2 Instalación, despliegue y explotación de sistemas de IA*
