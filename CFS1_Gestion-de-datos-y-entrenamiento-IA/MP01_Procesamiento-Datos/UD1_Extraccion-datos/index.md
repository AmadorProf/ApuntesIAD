---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD1 · Extracción de datos desde las fuentes | MP01 · Procesamiento de datos para IA'
footer: 'Apuntes de IA y Datos'
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
section.lead h1 { font-size: 2em; text-align: center; margin-top: 80px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
pre { background: #1e293b; color: #e2e8f0; padding: 16px; border-radius: 8px; font-size: 0.8em; }
</style>

<!-- _class: lead -->

# UD1 · Extracción de datos desde las fuentes

**MP01 · Procesamiento de datos para IA**
Apuntes de IA y Datos

---

## Objetivos de aprendizaje

Al finalizar esta unidad el alumno será capaz de:

- Identificar y categorizar los tipos de fuentes de datos disponibles en entornos reales de IA
- Distinguir la naturaleza estructurada, semiestructurada, no estructurada y multimodal del dato
- Evaluar las condiciones de acceso, licencia y uso antes de iniciar una extracción
- Configurar filtros, consultas y criterios de selección adaptados al volumen y calidad requeridos
- Registrar los metadatos mínimos de procedencia que garantizan la trazabilidad
- Documentar el proceso completo de extracción con criterios profesionales
- Aplicar principios de eficiencia energética durante la extracción de datos

---

## Mapa de la unidad

```
UD1 · Extracción de datos
│
├── 1. Tipología de fuentes
│   ├── Almacenamiento (SQL, NoSQL, data lakes)
│   ├── IoT y dispositivos embebidos
│   ├── Flujos en streaming
│   ├── APIs y servicios web
│   └── Repositorios documentales
│
├── 2. Naturaleza del dato
│   └── Estructurado · Semiestructurado · No estructurado · Multimodal
│
├── 3. Condiciones de acceso
│   └── Disponibilidad · Licencia · Datos personales
│
├── 4. Configuración de extracción
│   └── Filtros · Selección · Edge processing · Eficiencia
│
└── 5. Trazabilidad y documentación
    └── Metadatos · Registro de incidencias
```

---

## Fuentes de datos: panorama general

En un proyecto de IA, los datos raramente provienen de una sola fuente.

**Escenario real:** un modelo de predicción de averías industriales puede combinar:
- Lecturas de sensores IoT cada 500 ms
- Históricos de mantenimiento en base de datos relacional
- Informes técnicos en PDF no estructurados
- Datos climáticos desde una API externa
- Imágenes de cámaras de inspección

> Cada fuente tiene su propio protocolo, formato, frecuencia y condiciones legales de uso. El profesional debe conocerlas antes de extraer ningún dato.

---

## Sistemas de almacenamiento como fuente de datos

### Bases de datos relacionales (SQL)

Organizan los datos en tablas con esquema fijo y relaciones declaradas.

| Sistema | Caso de uso típico en IA |
|---|---|
| PostgreSQL | Historial de transacciones, logs de aplicación |
| MySQL / MariaDB | E-commerce, registros de usuarios |
| SQL Server | ERP corporativo, datos financieros |
| Oracle DB | Banca, seguros, datos regulados |

**Extracción:** consultas SQL con filtros de fecha, rango o condición. Exportación a CSV, Parquet o conexión directa con `sqlalchemy` / `psycopg2`.

---

## Almacenamiento distribuido y en la nube

### Data Lakes y Data Warehouses

```
Data Lake                      Data Warehouse
─────────────────────          ──────────────────────
Formato: cualquiera            Formato: estructurado
Schema: on read                Schema: on write
Escala: petabytes              Escala: terabytes
Uso: ML, exploración           Uso: BI, reporting

Ejemplos:                      Ejemplos:
- AWS S3 + Glue                - Google BigQuery
- Azure Data Lake              - Amazon Redshift
- GCS + Dataproc               - Snowflake
```

> Para IA, los data lakes son más habituales porque admiten datos brutos sin transformar. El data warehouse aporta datos ya curados para modelos más directos.

---

## Fuentes IoT y dispositivos embebidos

### Características de los datos IoT

- **Alta frecuencia:** miles de lecturas por segundo por dispositivo
- **Volumen masivo:** flotas de cientos o miles de sensores simultáneos
- **Ruido inherente:** fallos de sensor, valores fuera de rango, gaps de red
- **Protocolos propios:** MQTT, OPC-UA, Modbus, CoAP

| Plataforma IoT | Descripción |
|---|---|
| AWS IoT Core | Gestión de dispositivos y datos en la nube de Amazon |
| Azure IoT Hub | Conexión bidireccional con dispositivos Microsoft |
| Google Cloud IoT | Integración con BigQuery y Pub/Sub |
| InfluxDB | Base de datos de series temporales para telemetría |
| MQTT Broker | Protocolo ligero publish/subscribe para sensores |

---

## Flujos de datos en streaming

### Cuándo aparecen los datos en tiempo real

Los datos en streaming llegan de forma continua y no se pueden almacenar previamente para luego procesar: hay que actuar sobre ellos mientras fluyen.

**Casos de uso en IA:**
- Detección de fraude en transacciones bancarias en tiempo real
- Moderación automática de contenido en redes sociales
- Alertas de anomalías en infraestructura crítica
- Recomendación en tiempo real durante una sesión de usuario

| Framework | Fortaleza principal |
|---|---|
| Apache Kafka | Alto rendimiento, durabilidad, ecosistema amplio |
| AWS Kinesis | Integración nativa con el ecosistema AWS |
| Apache Flink | Procesamiento de estado complejo en streaming |
| MQTT | Protocolo ligero ideal para IoT de baja potencia |

---

## APIs y servicios web como fuente de datos

### REST, GraphQL y webhooks

Las APIs son la puerta de entrada a datos de terceros: redes sociales, mapas, clima, mercados financieros, bases de datos públicas.

```python
import requests

# Extracción desde API REST con autenticación por token
url = "https://api.ejemplo.com/v2/datos"
headers = {"Authorization": "Bearer TOKEN_AQUI"}
params = {
    "fecha_inicio": "2024-01-01",
    "fecha_fin":    "2024-12-31",
    "formato":      "json",
    "limite":       1000
}

respuesta = requests.get(url, headers=headers, params=params)
respuesta.raise_for_status()   # lanza excepción si status != 2xx
datos = respuesta.json()
```

**Consideraciones clave:** límites de tasa (rate limits), paginación, versionado de la API, manejo de errores HTTP.

---

## Repositorios documentales y datos abiertos

### Fuentes documentales para IA

| Tipo | Ejemplos concretos |
|---|---|
| Portales de datos abiertos | datos.gob.es, data.europa.eu, Kaggle Datasets |
| Repositorios científicos | Zenodo, UCI ML Repository, Hugging Face Datasets |
| Gestores documentales | SharePoint, Confluence, sistemas DMS corporativos |
| Bases de datos sectoriales | INE, Eurostat, OCDE, Banco Mundial |

**Formatos más habituales:** CSV, JSON, XML, Parquet, Excel, PDF, imágenes, audio.

> Los datos abiertos tienen licencias específicas. No todos permiten uso comercial o modificación. Siempre verificar antes de usar.

---

## Naturaleza del dato: tipos y características

| Tipo | Definición | Formatos comunes | Ejemplo IA |
|---|---|---|---|
| **Estructurado** | Esquema fijo, tabular, relaciones explícitas | CSV, SQL, Parquet, Excel | Historial de ventas para predicción |
| **Semiestructurado** | Esquema flexible, jerarquías anidadas | JSON, XML, YAML, Avro | Logs de servidor, respuestas de API |
| **No estructurado** | Sin esquema predefinido | Texto, imagen, audio, vídeo | NLP, visión por computador |
| **Multimodal** | Combinación de dos o más tipos anteriores | Cualquiera combinado | Informe médico + imagen radiológica |

**Factores de caracterización adicionales:**
- Frecuencia de actualización: estática, batch diario, streaming en tiempo real
- Volumen: MB, GB, TB, PB — condiciona la infraestructura de extracción

---

## Formatos de almacenamiento: comparativa técnica

| Formato | Tipo | Compresión | Lectura parcial | Ideal para |
|---|---|---|---|---|
| CSV | Texto plano | No nativa | No | Intercambio simple, datasets pequeños |
| JSON | Texto semiestructurado | No nativa | No | APIs, configuraciones |
| Parquet | Columnar binario | Si (Snappy/Gzip) | Si (columnas) | Big data, ML a escala |
| Avro | Binario con schema | Si | No | Streaming (Kafka) |
| ORC | Columnar binario | Si | Si | Hive, data warehouses |
| HDF5 | Jerárquico binario | Si | Si | Arrays numéricos grandes, ML |

> Para proyectos de IA a escala, **Parquet** es el estándar de facto: lectura columnar, compresión eficiente, compatible con Spark, Pandas y Arrow.

---

## Condiciones de acceso: verificación previa a la extracción

Antes de extraer cualquier dato, se deben verificar cuatro dimensiones:

### 1. Disponibilidad y estabilidad
- ¿La fuente es accesible de forma continua o tiene ventanas de mantenimiento?
- ¿Qué SLA (Service Level Agreement) ofrece el proveedor?

### 2. Licencia y uso permitido
- ¿Permite uso comercial, modificación, redistribución?
- Licencias habituales: CC-BY, CC-BY-SA, ODC-By, ODbL, uso interno exclusivo

### 3. Datos personales y sensibles (RGPD)
- ¿Contiene nombres, DNI, email, IP, geolocalización, datos de salud?
- Si es así, activa el protocolo RGPD desde el momento de la extracción

### 4. Restricciones contractuales
- Acuerdos de confidencialidad (NDA), cláusulas de datos compartidos

---

## Licencias de datos: tabla de referencia

| Licencia | Uso comercial | Modificación | Redistribución | Atribución |
|---|---|---|---|---|
| CC0 (dominio público) | Si | Si | Si | No requerida |
| CC-BY 4.0 | Si | Si | Si | Obligatoria |
| CC-BY-SA 4.0 | Si | Si | Si (misma licencia) | Obligatoria |
| CC-BY-NC 4.0 | No | Si | Si | Obligatoria |
| ODbL (datos abiertos) | Si | Si | Si (copyleft) | Obligatoria |
| Uso interno exclusivo | No | Limitada | No | N/A |

> En proyectos de IA regulados (sector sanitario, financiero, público), el incumplimiento de licencias puede conllevar sanciones administrativas y la invalidación del modelo.

---

## Configuración de la extracción: filtros y criterios de selección

No se extrae todo: se extrae lo necesario. El filtrado en origen reduce coste, tiempo y consumo energético.

```python
import pandas as pd
import sqlalchemy as sa

engine = sa.create_engine("postgresql://usuario:pwd@host:5432/bd")

# Extracción selectiva: solo columnas necesarias, rango de fechas acotado
query = """
    SELECT
        id_sensor,
        timestamp,
        temperatura,
        presion
    FROM lecturas_industriales
    WHERE
        timestamp BETWEEN '2024-01-01' AND '2024-12-31'
        AND temperatura IS NOT NULL
        AND id_planta = 'P-07'
    ORDER BY timestamp
"""

df = pd.read_sql(query, engine)
print(f"Registros extraídos: {len(df):,}")
print(df.dtypes)
```

---

## Procesamiento cercano a la fuente (edge processing)

### Por qué filtrar antes de transmitir

```
SIN edge processing:
Sensor → [100.000 lecturas/h] → Red → Cloud → Filtro → [1.200 útiles]
                                 ^^^
                          Ancho de banda saturado
                          Coste de transferencia alto
                          Latencia elevada

CON edge processing:
Sensor → Filtro local → [1.200 lecturas/h útiles] → Red → Cloud
                        ^^^
                   Reducción 98% del tráfico
                   Menor latencia
                   Menor consumo energético
```

**Tecnologías de edge:** AWS Greengrass, Azure IoT Edge, NVIDIA Jetson, Raspberry Pi con MQTT broker local.

> Seleccionar atributos y aplicar filtros en el dispositivo origen es también una medida de **eficiencia energética** y de reducción de emisiones de CO₂.

---

## Integridad básica durante la extracción

Verificaciones mínimas que deben realizarse inmediatamente tras la extracción:

| Verificación | Qué detecta | Cómo aplicarla |
|---|---|---|
| Conteo de registros | Pérdida de datos en tránsito | Comparar origen vs. destino |
| Checksum / hash | Corrupción del archivo | MD5, SHA-256 del fichero |
| Tipos de dato | Conversiones incorrectas | `df.dtypes`, `df.info()` |
| Rango de fechas | Gaps temporales | `df['fecha'].min()` / `.max()` |
| Valores nulos masivos | Fallo de extracción parcial | `df.isnull().sum()` |
| Duplicados obvios | Doble extracción | `df.duplicated().sum()` |

```python
# Verificación básica post-extracción
print(f"Registros: {len(df):,}")
print(f"Periodo: {df['fecha'].min()} → {df['fecha'].max()}")
print(f"Nulos por columna:\n{df.isnull().sum()}")
print(f"Duplicados: {df.duplicated().sum()}")
```

---

## Registro de metadatos de procedencia

### Los metadatos mínimos que debe contener cada extracción

```python
import hashlib
from datetime import datetime

metadatos = {
    "id_extraccion":   "EXT-2024-001",
    "fuente":          "postgresql://prod-db/lecturas_industriales",
    "tabla_consulta":  "lecturas_industriales",
    "filtros":         "planta=P-07, fecha 2024-01-01/2024-12-31",
    "fecha_extraccion": datetime.now().isoformat(),
    "formato_salida":  "parquet",
    "version_esquema": "v1.3",
    "registros":       len(df),
    "columnas":        list(df.columns),
    "hash_archivo":    hashlib.md5(open("salida.parquet","rb").read()).hexdigest(),
    "licencia":        "uso_interno",
    "datos_personales": False,
    "responsable":     "equipo-datos@empresa.com"
}
```

Este registro se almacena junto al archivo extraído y es la base del linaje de datos.

---

## Documentación del proceso de extracción

### Campos mínimos de un registro de extracción

| Campo | Contenido |
|---|---|
| ID de extracción | Identificador único y trazable |
| Fuente | Sistema, URL, tabla o servicio de origen |
| Mecanismo de acceso | SQL, API REST, SFTP, conector específico |
| Credenciales usadas | Referencia al vault de secretos (nunca en texto plano) |
| Filtros aplicados | Condiciones, rangos, atributos seleccionados |
| Periodicidad | Puntual, diaria, semanal, streaming |
| Restricciones conocidas | Licencia, RGPD, NDA, ventanas de mantenimiento |
| Incidencias | Errores, datos faltantes, anomalías detectadas |
| Herramienta usada | Script Python, Apache NiFi, Airbyte, Fivetran... |

> La documentación no es opcional: es un requisito de trazabilidad y de cumplimiento normativo.

---

## Herramientas de extracción: panorama

| Herramienta | Tipo | Caso de uso |
|---|---|---|
| **Python + requests** | Código | APIs REST, scraping simple |
| **Python + SQLAlchemy** | Código | Bases de datos SQL |
| **Apache NiFi** | Low-code | Flujos complejos, IoT, routing |
| **Airbyte** | Low-code | Conectores predefinidos 300+ fuentes |
| **Fivetran** | SaaS | ETL gestionado en la nube |
| **Apache Kafka Connect** | Framework | Extracción en streaming |
| **Spark + JDBC** | Distribuido | Extracción masiva paralela |
| **AWS Glue** | Cloud | ETL serverless en AWS |

**Criterios de selección:** volumen, frecuencia, complejidad de transformación, presupuesto, equipo disponible.

---

## Actividad práctica — UD1

### Diseño de un plan de extracción

**Escenario:** una empresa de logística quiere entrenar un modelo de predicción de retrasos en entregas. Dispone de:
- Base de datos PostgreSQL con 3 años de histórico de pedidos (50 M de registros)
- API de clima de terceros (requiere clave de acceso, 1.000 llamadas/día)
- Ficheros CSV de rutas de transporte actualizados semanalmente por el proveedor
- Sensores GPS en camiones via MQTT (actualización cada 30 segundos)

**Tareas:**
1. Clasificar cada fuente por tipo (estructurada, semiestructurada, IoT, streaming)
2. Identificar las condiciones de acceso y licencia de cada fuente
3. Definir los filtros de selección y la frecuencia de extracción para cada fuente
4. Diseñar el esquema de metadatos que se registrará en cada extracción
5. Proponer la herramienta de extracción más adecuada para cada fuente

---

## Puntos clave — UD1

- **Las fuentes son heterogéneas:** SQL, IoT, streaming, APIs y repositorios documentales requieren conectores y protocolos distintos
- **La naturaleza del dato determina el tratamiento:** estructurado, semiestructurado, no estructurado y multimodal tienen pipelines diferentes
- **Las condiciones de acceso se verifican antes de extraer:** licencia, RGPD y restricciones contractuales no son opcionales
- **El filtrado en origen es eficiencia:** seleccionar atributos y aplicar criterios de calidad antes de transmitir reduce coste y emisiones
- **La trazabilidad empieza en la extracción:** los metadatos de procedencia son el cimiento del linaje de datos de todo el proyecto
- **La documentación es un entregable profesional:** fuentes, mecanismos, restricciones, periodicidad e incidencias deben quedar registrados

---

## Criterios de evaluación — UD1

- Categoriza correctamente las fuentes de datos según su tipo y naturaleza
- Configura pasarelas de acceso (consultas SQL, llamadas API, conectores IoT) con los parámetros adecuados
- Verifica las condiciones de acceso, licencia y presencia de datos personales antes de extraer
- Aplica filtros y criterios de selección que reducen el volumen innecesario desde el origen
- Extrae datos verificando su integridad básica (conteo, hash, tipos, rangos)
- Registra los metadatos mínimos de procedencia en cada extracción
- Documenta el proceso completo garantizando la trazabilidad del dato desde su origen

---

<!-- _class: lead -->

[← Volver a MP01](../)


---

<!-- nav-slide -->

## Navegación

[Volver al módulo](../) &nbsp;·&nbsp; [UD2 · Exploración y análisis del co… →](../UD2_Exploracion-analisis/)
