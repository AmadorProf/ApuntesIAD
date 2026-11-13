# UD1 · Extracción de datos desde las fuentes

**Módulo:** MP01 · Procesamiento de datos para IA
**Programa:** CFS1 — Gestión de datos y entrenamiento IA
**Nivel:** CFS Nivel 3

---

## Introducción

La extracción de datos es el primer eslabón de cualquier pipeline de inteligencia artificial. Antes de que un modelo pueda aprender, antes de que un analista pueda explorar, antes de que una organización pueda tomar decisiones basadas en datos, alguien tiene que resolver una pregunta aparentemente sencilla: ¿dónde están los datos y cómo los traigo aquí?

La respuesta rara vez es simple. Los datos de una organización contemporánea están dispersos en decenas de sistemas: bases de datos relacionales heredadas, plataformas en la nube, APIs de terceros, archivos CSV que alguien dejó en un servidor FTP, flujos continuos de eventos generados por dispositivos IoT o aplicaciones web, y páginas HTML que nunca fueron pensadas para ser consumidas de forma programática. Cada una de estas fuentes tiene sus propias reglas de acceso, sus propios formatos, sus propias limitaciones de velocidad y sus propios modos de fallo.

Esta unidad proporciona el mapa completo de ese territorio. El objetivo no es solo que el estudiante sepa qué herramienta usar en cada situación, sino que comprenda por qué cada herramienta existe, qué problema resuelve y cuáles son sus compromisos. Un ingeniero de datos eficaz no aplica recetas; diagnostica, elige y construye con criterio. Esa capacidad de juicio nace del conocimiento profundo de las fuentes, los conectores, los patrones de extracción y los formatos que se estudian a continuación.

---

## Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Identificar y clasificar los principales tipos de fuentes de datos utilizados en proyectos de IA, describiendo sus características técnicas, ventajas y limitaciones.
2. Seleccionar la librería o conector adecuado para cada tipo de fuente, justificando la elección en función del contexto del proyecto.
3. Implementar scripts de extracción funcionales en Python que accedan a bases de datos SQL y NoSQL, APIs REST y GraphQL, y realicen scraping básico de páginas web.
4. Distinguir entre los patrones ETL y ELT, así como entre extracción por lotes y en tiempo real, y aplicar el patrón más adecuado a un caso de uso dado.
5. Diseñar pipelines de ingesta robustos que contemplen autenticación segura, manejo de errores, control de rate limiting e idempotencia.
6. Comparar los principales formatos de intercambio de datos (CSV, JSON, Parquet, Avro) y elegir el más apropiado según los requisitos de rendimiento y compatibilidad.
7. Describir el papel de herramientas como Apache NiFi, Airbyte y Fivetran en la orquestación de pipelines de ingesta a escala.

---

## 1. Tipos de fuentes de datos

Toda estrategia de extracción comienza por entender la naturaleza de la fuente. No es lo mismo conectarse a una base de datos PostgreSQL dentro de la propia red corporativa que consumir una API pública con límites de llamadas o rastrear páginas web que cambian de estructura sin previo aviso. Esta sección recorre los grandes tipos de fuentes que un ingeniero de datos encontrará con más frecuencia.

### 1.1 Bases de datos relacionales (SQL)

Las bases de datos relacionales son, todavía hoy, el sistema de almacenamiento más extendido en organizaciones de cualquier tamaño. PostgreSQL, MySQL, MariaDB, Microsoft SQL Server y Oracle representan la inmensa mayoría de los sistemas transaccionales en producción. Almacenan datos en tablas con esquemas definidos, imponen integridad referencial mediante claves foráneas y exponen una interfaz estándar: el lenguaje SQL.

Desde el punto de vista de la extracción, las bases relacionales ofrecen una ventaja enorme: los datos ya están estructurados y son consultables con precisión mediante `SELECT`, filtros temporales, joins y funciones de agregación. Esto las convierte en la fuente más predecible con la que trabajará un ingeniero de datos. Sin embargo, también presentan retos propios: acceder a una base de producción con una consulta pesada puede degradar el rendimiento del sistema transaccional; los esquemas evolucionan con el tiempo y pueden romper pipelines que no se diseñaron con esa posibilidad en mente; y los volúmenes de datos pueden ser suficientemente grandes como para que una extracción completa periódica sea inviable.

Para mitigar el impacto sobre producción, es habitual conectarse a réplicas de lectura en lugar de al nodo principal, o programar las extracciones en ventanas de baja carga. El control de qué columnas y filas se extraen —y con qué frecuencia— es parte del diseño del pipeline, no un detalle técnico secundario.

### 1.2 Bases de datos NoSQL

El término NoSQL agrupa sistemas de almacenamiento muy heterogéneos que comparten una característica: no utilizan el modelo relacional tabular como paradigma principal. Dentro de esta categoría conviven cuatro familias con características y casos de uso muy distintos.

Las **bases de datos de documentos**, como MongoDB o CouchDB, almacenan datos en forma de documentos JSON o BSON. Son especialmente adecuadas para datos semi-estructurados donde el esquema varía entre registros: perfiles de usuario, catálogos de productos, configuraciones de aplicaciones. La ausencia de esquema rígido es una ventaja en entornos ágiles, pero complica la extracción cuando los documentos de una misma colección tienen estructuras divergentes.

Las **bases de datos clave-valor**, como Redis o DynamoDB, priorizan la velocidad de acceso puntual sobre la capacidad de consulta. Redis se usa frecuentemente como caché o como broker de mensajes ligeros; DynamoDB, dentro del ecosistema AWS, como almacén de baja latencia a escala. Extraer grandes volúmenes de datos de un almacén clave-valor requiere iterar sobre todas las claves o utilizar mecanismos de exportación específicos de la plataforma.

Las **bases de datos de columnas anchas**, como Apache Cassandra o HBase, organizan los datos en familias de columnas y están optimizadas para escrituras masivas y lecturas distribuidas. Son habituales en casos de uso de series temporales, registros de eventos y telemetría. Cassandra, en particular, está diseñada para escalar horizontalmente sin un punto único de fallo, lo que la hace popular en sistemas de alta disponibilidad.

Las **bases de datos de grafos**, como Neo4j, representan entidades y sus relaciones de forma nativa. Son ideales para analizar redes sociales, grafos de conocimiento o sistemas de recomendación basados en relaciones. La extracción desde grafos requiere entender el lenguaje de consulta propio de cada sistema (Cypher en Neo4j, por ejemplo) y puede implicar recorrer estructuras complejas de nodos y aristas.

### 1.3 APIs REST y GraphQL

Las APIs son la interfaz estándar para acceder a datos de servicios externos: plataformas de redes sociales, sistemas de pago, herramientas de CRM, servicios meteorológicos, bases de datos financieras y un largo etcétera. Comprender cómo funcionan es imprescindible para cualquier proyecto de IA que integre datos de terceros.

Una **API REST** (Representational State Transfer) expone recursos a través de URLs y utiliza los verbos HTTP (`GET`, `POST`, `PUT`, `DELETE`) para definir las operaciones sobre esos recursos. Las respuestas se entregan habitualmente en formato JSON. El acceso suele estar protegido mediante claves API, tokens OAuth 2.0 o autenticación básica. Las APIs REST son sencillas de consumir pero presentan el problema del sobre-aprovisionamiento de datos (el servidor devuelve más campos de los necesarios) y del sub-aprovisionamiento (hay que hacer múltiples llamadas para obtener datos relacionados).

**GraphQL** es una alternativa diseñada precisamente para resolver esos problemas. Permite al cliente especificar exactamente qué campos necesita en cada consulta, y agregar en una sola petición datos que en REST requerirían múltiples llamadas. El cliente envía una consulta en el lenguaje GraphQL al único endpoint del servidor, que devuelve exactamente lo solicitado. Plataformas como GitHub, Shopify o Contentful ofrecen APIs GraphQL. La extracción desde GraphQL requiere construir las queries adecuadas y manejar la paginación (habitualmente mediante cursores en lugar de offsets).

### 1.4 Web scraping

Cuando los datos no están disponibles a través de una API, a veces la única forma de acceder a ellos es extrayéndolos directamente del HTML de una página web. Esta técnica se conoce como web scraping o web crawling. Es una herramienta poderosa pero que debe usarse con responsabilidad: es necesario revisar el fichero `robots.txt` del sitio, respetar los términos de servicio y no sobrecargar los servidores con peticiones excesivas.

Técnicamente, el scraping implica descargar el HTML de una o varias páginas y parsearlo para extraer los datos de interés. Las dificultades surgen cuando el contenido se carga dinámicamente mediante JavaScript (el HTML descargado no contiene los datos, que se inyectan posteriormente por el navegador), cuando el sitio implementa medidas anti-bot (CAPTCHAs, fingerprinting de navegador, bloqueos por IP), o cuando la estructura del HTML cambia sin previo aviso y rompe los selectores CSS o XPath utilizados para extraer los datos.

La extracción de páginas con contenido dinámico requiere herramientas que controlen un navegador real o un motor de renderizado headless, como Playwright o Selenium. Para páginas estáticas, basta con parsear el HTML descargado con una librería como BeautifulSoup.

### 1.5 Archivos planos y formatos de intercambio

A pesar de la proliferación de bases de datos y APIs, una cantidad sorprendente de datos sigue moviéndose en forma de archivos. Dumps de bases de datos en CSV, exports de herramientas de business intelligence en Excel, ficheros XML de intercambio entre sistemas ERP, archivos JSON generados por aplicaciones móviles: todos son fuentes legítimas y frecuentes en proyectos reales.

Los archivos planos presentan el reto de la variabilidad de formato: un CSV puede usar coma, punto y coma o tabulador como separador; puede o no incluir cabecera; puede o no entrecomillar los campos; puede usar distintos encodings (UTF-8, Latin-1, Windows-1252). Un pipeline robusto debe anticipar y manejar esas variaciones. Los archivos también pueden ser voluminosos: un CSV de varios gigabytes no se puede cargar en memoria de una vez y debe procesarse en chunks o con herramientas que soporten lectura en streaming.

Los archivos se distribuyen habitualmente a través de servidores FTP/SFTP, buckets de almacenamiento en la nube (AWS S3, Google Cloud Storage, Azure Blob Storage) o simplemente como adjuntos de correo electrónico en organizaciones menos maduras digitalmente.

### 1.6 Fuentes de streaming (Kafka, Kinesis)

Las fuentes de streaming representan un paradigma radicalmente diferente al de los datos en reposo. En lugar de un conjunto de datos que existe y puede consultarse en cualquier momento, un stream es una secuencia continua e ilimitada de eventos que fluye en tiempo real: clics de usuarios en una web, transacciones bancarias, lecturas de sensores IoT, logs de aplicaciones, actualizaciones de precios en un mercado financiero.

**Apache Kafka** es la plataforma de streaming distribuida más utilizada. Su arquitectura se basa en topics (canales de mensajes), particiones (que permiten la paralelización del consumo) y grupos de consumidores (que permiten que múltiples instancias de una aplicación lean del mismo topic dividiéndose la carga). Kafka persiste los mensajes durante un período configurable, lo que permite a los consumidores releer eventos pasados, algo imposible en sistemas de mensajería más simples como RabbitMQ.

**Amazon Kinesis** es la alternativa gestionada de AWS para el procesamiento de streams. Ofrece una funcionalidad similar a Kafka pero como servicio completamente administrado, lo que reduce la complejidad operativa a cambio de un menor control sobre la infraestructura.

El consumo de datos en streaming introduce desafíos particulares para proyectos de IA: los modelos deben adaptarse a datos que llegan continuamente, el procesamiento debe ser lo suficientemente rápido para no acumular retraso, y los datos deben persistirse de alguna forma (en un data lake o data warehouse) para poder ser usados en entrenamiento.

---

## 2. Conectores y librerías de extracción

Una vez identificada la fuente, el paso siguiente es elegir la herramienta con la que conectarse. Python, el lenguaje dominante en el ecosistema de datos e IA, ofrece un ecosistema maduro de librerías para cada tipo de fuente. Esta sección describe las más relevantes, con ejemplos de uso funcionales.

### 2.1 Conectores SQL: SQLAlchemy, psycopg2, pymysql

**psycopg2** es el adaptador de bajo nivel más usado para PostgreSQL en Python. Proporciona acceso directo al protocolo de comunicación con el servidor y es la base sobre la que se construyen herramientas de nivel superior. Su uso directo es adecuado cuando se necesita control fino sobre las consultas y la gestión de transacciones.

```python
import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host="localhost",
    database="produccion",
    user="lector",
    password="secreto",
    port=5432
)

query = """
    SELECT id, fecha_creacion, importe, estado
    FROM pedidos
    WHERE fecha_creacion >= '2025-01-01'
      AND estado = 'completado'
"""

df = pd.read_sql_query(query, conn)
conn.close()
print(df.shape)
```

**SQLAlchemy** opera en un nivel de abstracción superior. Proporciona tanto un ORM (Object-Relational Mapper) completo como un núcleo de expresión SQL que permite construir consultas de forma programática sin escribir SQL crudo. Su ventaja principal es la portabilidad: el mismo código puede conectarse a PostgreSQL, MySQL, SQLite o SQL Server cambiando únicamente la cadena de conexión (la URL de la base de datos).

```python
from sqlalchemy import create_engine, text
import pandas as pd

# La URL de conexión sigue el formato: dialecto+driver://usuario:contraseña@host:puerto/base_de_datos
engine = create_engine("postgresql+psycopg2://lector:secreto@localhost:5432/produccion")

with engine.connect() as conn:
    df = pd.read_sql_query(
        text("SELECT * FROM pedidos WHERE fecha_creacion >= :fecha"),
        conn,
        params={"fecha": "2025-01-01"}
    )

print(df.head())
```

**pymysql** cumple el mismo papel que psycopg2 pero para MySQL y MariaDB. Su API es casi idéntica y puede usarse como backend de SQLAlchemy especificando `mysql+pymysql://` en la URL de conexión.

| Librería | Base de datos | Nivel | Ventaja principal |
|---|---|---|---|
| psycopg2 | PostgreSQL | Bajo | Control fino, rendimiento |
| pymysql | MySQL / MariaDB | Bajo | Compatibilidad amplia |
| pyodbc | SQL Server, Oracle | Bajo | ODBC estándar |
| SQLAlchemy | Múltiples | Alto | Portabilidad, abstracción |
| cx_Oracle | Oracle | Bajo | Soporte nativo Oracle |

### 2.2 Clientes NoSQL: pymongo, redis-py, cassandra-driver

**pymongo** es el cliente oficial de MongoDB para Python. Permite conectarse a un servidor Mongo, seleccionar una base de datos y una colección, y ejecutar operaciones de lectura con el lenguaje de consulta propio de MongoDB (basado en documentos JSON).

```python
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://lector:secreto@localhost:27017/")
db = client["catalogo"]
coleccion = db["productos"]

# Extraer productos activos creados en 2025
resultados = coleccion.find(
    {
        "activo": True,
        "fecha_alta": {"$gte": datetime(2025, 1, 1)}
    },
    projection={"_id": 0, "sku": 1, "nombre": 1, "precio": 1, "categoria": 1}
)

productos = list(resultados)
print(f"Productos extraídos: {len(productos)}")
client.close()
```

**redis-py** permite interactuar con Redis desde Python. Su uso en extracción de datos es menos común que en caché, pero es relevante cuando Redis actúa como almacén de estado, cola de trabajo o broker de mensajes ligero.

```python
import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Extraer todos los perfiles de usuario almacenados como hash
claves = r.keys("usuario:*")
perfiles = []
for clave in claves:
    datos = r.hgetall(clave)
    datos["id"] = clave.split(":")[1]
    perfiles.append(datos)

print(f"Perfiles recuperados: {len(perfiles)}")
```

**cassandra-driver** es el cliente oficial para Apache Cassandra. Las consultas se expresan en CQL (Cassandra Query Language), que es sintácticamente similar a SQL pero con importantes restricciones derivadas de la arquitectura distribuida de Cassandra (no hay joins, los filtros deben usar columnas de partición o índices explícitos).

```python
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

auth = PlainTextAuthProvider(username="lector", password="secreto")
cluster = Cluster(["192.168.1.10"], auth_provider=auth)
session = cluster.connect("telemetria")

rows = session.execute(
    "SELECT dispositivo_id, timestamp, temperatura, humedad "
    "FROM lecturas "
    "WHERE fecha = '2025-06-01' "
    "LIMIT 10000"
)

datos = [dict(row._asdict()) for row in rows]
print(f"Filas extraídas: {len(datos)}")
cluster.shutdown()
```

### 2.3 Clientes HTTP: requests, httpx, aiohttp

**requests** es la librería HTTP más usada en Python por su API limpia e intuitiva. Es síncrona: cada llamada bloquea el hilo hasta recibir la respuesta, lo que la hace simple pero ineficiente para extracciones que requieren muchas llamadas concurrentes.

```python
import requests
import time

API_KEY = "mi_clave_secreta"
BASE_URL = "https://api.ejemplo.com/v2"

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
})

todos_los_registros = []
pagina = 1

while True:
    respuesta = session.get(f"{BASE_URL}/registros", params={"page": pagina, "per_page": 100})
    respuesta.raise_for_status()
    datos = respuesta.json()

    if not datos["items"]:
        break

    todos_los_registros.extend(datos["items"])
    pagina += 1
    time.sleep(0.5)  # Respetar rate limiting

print(f"Total de registros: {len(todos_los_registros)}")
```

**httpx** es una librería más moderna que ofrece una API casi idéntica a requests pero añade soporte nativo para HTTP/2 y para programación asíncrona mediante `async/await`.

**aiohttp** es la alternativa asíncrona de referencia cuando se necesita realizar centenares o miles de peticiones concurrentes. Su uso con `asyncio` permite multiplicar el throughput de extracción en escenarios con muchas llamadas a APIs:

```python
import asyncio
import aiohttp

async def fetch_pagina(session, url, params):
    async with session.get(url, params=params) as resp:
        resp.raise_for_status()
        return await resp.json()

async def extraer_todos(base_url, total_paginas):
    async with aiohttp.ClientSession(headers={"Authorization": "Bearer TOKEN"}) as session:
        tareas = [
            fetch_pagina(session, f"{base_url}/items", {"page": p, "per_page": 100})
            for p in range(1, total_paginas + 1)
        ]
        resultados = await asyncio.gather(*tareas)
    return [item for pagina in resultados for item in pagina["items"]]

datos = asyncio.run(extraer_todos("https://api.ejemplo.com/v2", total_paginas=50))
print(f"Registros: {len(datos)}")
```

### 2.4 Frameworks de scraping: BeautifulSoup, Scrapy, Playwright

**BeautifulSoup** (parte del paquete `bs4`) parsea HTML y XML y permite navegar por el árbol DOM usando selectores CSS o métodos de búsqueda propios. Es la opción más sencilla para extracciones puntuales de páginas estáticas.

```python
import requests
from bs4 import BeautifulSoup

url = "https://libros.ejemplo.com/ciencia"
resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")
libros = []

for tarjeta in soup.select("article.producto"):
    titulo = tarjeta.select_one("h2.titulo").get_text(strip=True)
    precio_texto = tarjeta.select_one("span.precio").get_text(strip=True)
    precio = float(precio_texto.replace("€", "").replace(",", "."))
    libros.append({"titulo": titulo, "precio": precio})

print(f"Libros extraídos: {len(libros)}")
```

**Scrapy** es un framework completo para scraping a escala. A diferencia de BeautifulSoup, que es solo un parser, Scrapy gestiona el ciclo completo: descarga de páginas, seguimiento de enlaces, parsing, extracción de items y exportación a múltiples formatos. Incluye middlewares para gestionar cookies, proxies, reintentos y rate limiting.

**Playwright** controla un navegador real (Chromium, Firefox o WebKit) y permite interactuar con páginas que requieren JavaScript para renderizar su contenido. Es imprescindible para sitios modernos de una sola página (SPA) donde el HTML inicial no contiene los datos.

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    navegador = p.chromium.launch(headless=True)
    pagina = navegador.new_page()
    pagina.goto("https://app.ejemplo.com/dashboard", wait_until="networkidle")

    # Esperar a que el componente de datos se haya renderizado
    pagina.wait_for_selector("table.datos-principales")
    filas = pagina.query_selector_all("table.datos-principales tbody tr")

    datos = []
    for fila in filas:
        celdas = [td.inner_text() for td in fila.query_selector_all("td")]
        datos.append(celdas)

    navegador.close()

print(f"Filas extraídas: {len(datos)}")
```

### 2.5 Clientes de streaming: confluent-kafka, faust

**confluent-kafka** es el cliente de Python para Apache Kafka mantenido por Confluent. Ofrece alto rendimiento y soporte completo para todas las características de Kafka, incluyendo el Schema Registry para validación de mensajes con esquemas Avro o Protobuf.

```python
from confluent_kafka import Consumer
import json

conf = {
    "bootstrap.servers": "kafka-broker:9092",
    "group.id": "pipeline-extraccion-v1",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False
}

consumer = Consumer(conf)
consumer.subscribe(["eventos-usuario"])

mensajes = []
try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            break
        if msg.error():
            raise Exception(f"Error Kafka: {msg.error()}")

        evento = json.loads(msg.value().decode("utf-8"))
        mensajes.append(evento)
        consumer.commit(asynchronous=False)
finally:
    consumer.close()

print(f"Mensajes consumidos: {len(mensajes)}")
```

**faust** es una librería de Python para construir aplicaciones de procesamiento de streams al estilo de Kafka Streams, pero en Python. Permite definir agentes que reaccionan a mensajes de Kafka con una API declarativa más expresiva que la del cliente de bajo nivel.

---

## 3. Patrones de extracción: ETL vs ELT

La arquitectura de un pipeline de datos no es solo una cuestión de herramientas: es una decisión de diseño con implicaciones sobre el rendimiento, la mantenibilidad, el coste y la flexibilidad del sistema. Los dos patrones dominantes —ETL y ELT— reflejan filosofías distintas sobre dónde y cuándo transformar los datos.

**ETL** (Extract, Transform, Load) es el patrón clásico. Los datos se extraen de la fuente, se transforman (limpian, enriquecen, agregan, reformatean) en un motor intermedio y solo entonces se cargan en el destino. Este enfoque era el estándar cuando el almacenamiento en los destinos (data warehouses tradicionales) era costoso y los datos debían llegar ya preparados para el consumo. Su ventaja es que el destino solo contiene datos procesados y listos para usar; su inconveniente es que cualquier cambio en la lógica de transformación requiere reprocesar los datos desde el inicio.

**ELT** (Extract, Load, Transform) invierte el orden: los datos se cargan primero en el destino en su forma cruda, y las transformaciones se aplican allí mediante SQL u otras herramientas. Este patrón se ha popularizado con la aparición de data warehouses en la nube (BigQuery, Snowflake, Redshift) capaces de ejecutar transformaciones sobre volúmenes masivos de datos a bajo coste. ELT preserva los datos originales, permite reprocesamientos flexibles y facilita la exploración de datos antes de definir transformaciones.

### 3.1 Extracción por lotes (batch) vs en tiempo real

La extracción por lotes procesa un conjunto de datos acumulado durante un período (un día, una hora, una semana) en una única ejecución planificada. Es el modo más sencillo de implementar y suficiente para la mayoría de los casos de uso de IA: el reentrenamiento de modelos rara vez requiere datos de los últimos segundos.

La extracción en tiempo real (o near-real-time) procesa los datos a medida que se generan, con latencias de milisegundos a segundos. Es necesaria en casos de uso como detección de fraude en tiempo real, sistemas de recomendación que reflejan el comportamiento inmediato del usuario, o monitorización de sistemas críticos.

Entre ambos extremos existe un término medio habitual en la práctica: la **micro-batch**, donde los datos se procesan en ventanas de tiempo cortas (cada minuto, cada cinco minutos) usando herramientas como Apache Spark Structured Streaming. Este enfoque simplifica la implementación respecto al streaming puro manteniendo una latencia suficientemente baja para muchos casos de uso.

### 3.2 Extracción incremental y control de cambios (CDC)

Extraer la tabla completa cada vez es inviable cuando el volumen de datos crece. La extracción incremental consiste en extraer solo los registros que han cambiado desde la última ejecución. Hay dos enfoques principales.

El primero se basa en una **columna de marca temporal** (`updated_at`, `fecha_modificacion`) que se actualiza cada vez que el registro cambia. El pipeline almacena la marca temporal de la última extracción y en la siguiente solo consulta los registros más recientes. Este método es simple pero tiene limitaciones: no detecta borrados (un registro eliminado no aparece en las consultas) y requiere que la aplicación mantenga la columna de marca temporal de forma consistente.

El segundo enfoque es **Change Data Capture (CDC)**, que captura los cambios directamente del log de transacciones de la base de datos (el WAL de PostgreSQL, el binlog de MySQL). Herramientas como **Debezium** se suscriben a estos logs y producen eventos Kafka para cada inserción, actualización o borrado, con latencia mínima y sin impactar el rendimiento de la base de datos. CDC es más complejo de implementar pero ofrece una captura completa y fidedigna de todos los cambios.

```python
# Ejemplo de extracción incremental con marca temporal
import psycopg2
import json
from datetime import datetime
from pathlib import Path

ESTADO_FILE = Path("/var/pipeline/estado_ultima_extraccion.json")

def cargar_ultima_marca():
    if ESTADO_FILE.exists():
        return json.loads(ESTADO_FILE.read_text())["ultima_marca"]
    return "1970-01-01T00:00:00"

def guardar_ultima_marca(marca: str):
    ESTADO_FILE.write_text(json.dumps({"ultima_marca": marca}))

conn = psycopg2.connect("postgresql://lector:secreto@localhost/produccion")
ultima_marca = cargar_ultima_marca()

with conn.cursor() as cur:
    cur.execute(
        "SELECT id, nombre, email, updated_at FROM usuarios WHERE updated_at > %s ORDER BY updated_at",
        (ultima_marca,)
    )
    filas = cur.fetchall()

if filas:
    nueva_marca = max(f[3] for f in filas).isoformat()
    guardar_ultima_marca(nueva_marca)
    print(f"Registros nuevos/modificados: {len(filas)}")

conn.close()
```

### 3.3 Autenticación y gestión de credenciales

Ningún pipeline en producción debe tener credenciales escritas en el código. Esta práctica, desgraciadamente común, expone contraseñas y claves API a cualquier persona que tenga acceso al repositorio de código. La gestión segura de credenciales es un requisito de cualquier ingeniería de datos responsable.

Las opciones más comunes, de menor a mayor sofisticación, son: variables de entorno (el mínimo aceptable en cualquier entorno), ficheros de configuración excluidos del control de versiones mediante `.gitignore`, servicios de gestión de secretos como **AWS Secrets Manager**, **HashiCorp Vault** o **Google Secret Manager**, y la autenticación sin contraseña mediante roles IAM en entornos cloud (la opción más segura cuando está disponible).

```python
import os
import boto3
import json

def obtener_credenciales_db(nombre_secreto: str, region: str = "eu-west-1") -> dict:
    """Recupera credenciales de base de datos desde AWS Secrets Manager."""
    cliente = boto3.client("secretsmanager", region_name=region)
    respuesta = cliente.get_secret_value(SecretId=nombre_secreto)
    return json.loads(respuesta["SecretString"])

creds = obtener_credenciales_db("produccion/postgresql/lector")
conn_string = f"postgresql://{creds['username']}:{creds['password']}@{creds['host']}/{creds['dbname']}"
```

### 3.4 Manejo de rate limiting y errores

Las APIs imponen límites al número de peticiones que se pueden hacer en un período de tiempo para protegerse del abuso. Superar esos límites resulta en respuestas HTTP 429 (Too Many Requests). Un pipeline bien diseñado detecta estas respuestas y aplica una estrategia de retroceso exponencial (exponential backoff): espera un tiempo que crece con cada intento fallido antes de reintentar.

La librería **tenacity** simplifica la implementación de esta estrategia en Python:

```python
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class RateLimitError(Exception):
    pass

@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(5)
)
def llamar_api(url: str, session: requests.Session, params: dict) -> dict:
    resp = session.get(url, params=params)
    if resp.status_code == 429:
        raise RateLimitError(f"Rate limit alcanzado. Cabecera Retry-After: {resp.headers.get('Retry-After')}")
    resp.raise_for_status()
    return resp.json()
```

Más allá del rate limiting, un pipeline robusto debe anticipar y manejar fallos de red, timeouts, respuestas malformadas, esquemas inesperados en los datos y caídas parciales de sistemas distribuidos. El principio general es fallar rápido y de forma explícita, registrar el error con suficiente contexto para diagnóstico y, cuando sea posible, reintentar con idempotencia.

---

## 4. Formatos de datos en la ingesta

El formato en el que los datos se almacenan y transmiten tiene implicaciones directas sobre el rendimiento de la ingesta, el tamaño en disco, la compatibilidad con las herramientas downstream y la capacidad de evolucionar el esquema con el tiempo. Elegir el formato adecuado no es un detalle menor.

### 4.1 CSV, TSV, JSON, XML

**CSV** (Comma-Separated Values) es el formato más universal. Cualquier herramienta de análisis de datos puede leer un CSV. Su simplicidad es también su limitación: no soporta tipos de datos (todo es texto), no tiene un estándar rígido para casos como valores que contienen el separador o saltos de línea, y no es eficiente para grandes volúmenes.

**TSV** (Tab-Separated Values) es una variante que usa el tabulador como separador, lo que evita conflictos con comas dentro de los valores pero es igualmente limitado en expresividad.

**JSON** permite estructuras anidadas y tipado básico (números, booleanos, cadenas, arrays, objetos), lo que lo convierte en el formato preferido para APIs y datos semi-estructurados. Su principal inconveniente es la verbosidad: los nombres de campo se repiten en cada registro, lo que hace los ficheros voluminosos.

**XML** fue el formato de intercambio dominante antes de JSON. Es más verboso que JSON y más complejo de parsear, pero todavía omnipresente en integraciones con sistemas legados, ERPs y estándares sectoriales (SOAP, EDI, HL7 en sanidad).

### 4.2 Formatos columnares: Parquet, ORC, Avro

Los formatos columnares almacenan los datos organizados por columna en lugar de por fila. Esto los hace extremadamente eficientes para cargas de trabajo analíticas donde se consultan unas pocas columnas de tablas muy anchas: en lugar de leer todas las columnas de cada fila, el motor de consulta solo lee las columnas necesarias. Además, los datos de una misma columna son homogéneos y se comprimen mucho mejor que datos mezclados de múltiples tipos.

**Apache Parquet** es el formato columnar más usado en ecosistemas de big data. Es compatible con Spark, Pandas, DuckDB, Athena, BigQuery y prácticamente cualquier herramienta moderna de análisis de datos. Soporta tipos ricos (incluidas estructuras anidadas), compresión con Snappy, Gzip o Zstd, y predicados pushdown (el lector puede saltar bloques de datos que no satisfacen los filtros de una consulta sin leerlos).

**Apache ORC** (Optimized Row Columnar) es el equivalente de Parquet en el ecosistema Hive/Hadoop. Ofrece ventajas similares y es el formato preferido en algunas instalaciones de Hive y Presto.

**Apache Avro** es diferente: es un formato orientado a filas pero con soporte para evolución de esquema. El esquema se incluye en el fichero, lo que facilita la compatibilidad entre versiones. Es el formato preferido en Kafka cuando se usa junto al Schema Registry de Confluent.

| Formato | Orientación | Compresión | Esquema | Mejor para |
|---|---|---|---|---|
| CSV | Fila | No nativa | No | Intercambio simple, compatibilidad |
| JSON | Fila | No nativa | No | APIs, datos semi-estructurados |
| XML | Fila | No nativa | XSD opcional | Sistemas legados, estándares |
| Parquet | Columna | Sí (Snappy, Gzip) | Sí (embebido) | Análisis de datos, data lakes |
| ORC | Columna | Sí | Sí | Hive, Presto |
| Avro | Fila | Sí | Sí (embebido) | Kafka, streaming, evolución esquema |

### 4.3 Conversión y serialización

En la práctica, los datos raramente llegan ya en el formato óptimo para su procesamiento. Un pipeline de ingesta típico recibe JSON de una API, lo convierte a un DataFrame de Pandas y lo serializa a Parquet para almacenarlo en el data lake. La librería **pyarrow** es la herramienta de referencia para estas conversiones en el ecosistema Python:

```python
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path

# Datos procedentes de una API (lista de dicts)
registros = [
    {"id": 1, "nombre": "Ana García", "importe": 1250.75, "fecha": "2025-06-01"},
    {"id": 2, "nombre": "Luis Martín", "importe": 890.00, "fecha": "2025-06-01"},
]

df = pd.DataFrame(registros)
df["fecha"] = pd.to_datetime(df["fecha"])
df["importe"] = df["importe"].astype("float32")

tabla_arrow = pa.Table.from_pandas(df)
ruta_salida = Path("/data/lake/pedidos/fecha=2025-06-01/parte-0001.parquet")
ruta_salida.parent.mkdir(parents=True, exist_ok=True)

pq.write_table(
    tabla_arrow,
    ruta_salida,
    compression="snappy",
    write_statistics=True
)

print(f"Tabla guardada: {ruta_salida} ({ruta_salida.stat().st_size / 1024:.1f} KB)")
```

---

## 5. Pipelines de ingesta: diseño y herramientas

Hasta aquí hemos estudiado los componentes individuales: fuentes, conectores, patrones y formatos. En producción, estos componentes se combinan en pipelines: flujos de trabajo orquestados que extraen datos de forma automática, fiable y repetible.

### 5.1 Diseño de pipelines robustos

Un pipeline de ingesta bien diseñado no es simplemente un script que funciona cuando todo va bien. Es un sistema que anticipa los modos de fallo, los registra, los maneja con gracia y garantiza que el estado final de los datos es correcto incluso cuando algo sale mal a mitad del proceso.

Los principios de diseño más importantes son:

**Observabilidad.** El pipeline debe emitir métricas (registros procesados, tiempo de ejecución, errores por tipo) y logs estructurados (en JSON, para que sean fácilmente indexables) que permitan diagnosticar problemas sin necesidad de ejecutar el pipeline en modo debug. Las herramientas de monitorización como Datadog, Prometheus o CloudWatch pueden consumir estas métricas y alertar cuando algo se desvía de lo esperado.

**Manejo explícito de fallos parciales.** En un pipeline que procesa millones de registros, algunos fallarán inevitablemente (un campo con formato inesperado, un valor nulo donde no se esperaba). El pipeline debe decidir de antemano qué hacer en esos casos: rechazar el registro y enviarlo a una cola de errores para inspección posterior (Dead Letter Queue), aplicar un valor por defecto, o fallar el pipeline completo. La elección depende del caso de uso, pero la opción de silenciar el error es siempre la peor.

**Separación de concerns.** La extracción, la transformación y la carga deben ser pasos claramente separados, preferiblemente en funciones o clases independientes. Esto facilita el testeo unitario, la depuración y la reutilización de componentes.

**Parametrización.** Los pipelines no deben tener fechas, rutas o nombres de tabla escritos en el código. Todo parámetro variable debe ser configurable externamente, lo que permite relanzar el pipeline para períodos específicos o sobre entornos distintos sin modificar el código.

### 5.2 Herramientas: Apache NiFi, Airbyte, Fivetran

Cuando los pipelines de ingesta son numerosos, complejos o deben ser gestionados por equipos no exclusivamente técnicos, las herramientas especializadas de integración de datos aportan valor al abstraer la complejidad de la implementación.

**Apache NiFi** es una plataforma de código abierto para automatizar el flujo de datos entre sistemas. Su interfaz visual permite construir pipelines de ingesta de forma gráfica, conectando procesadores preconfigurados para leer de distintas fuentes, transformar datos y escribir en distintos destinos. NiFi maneja automáticamente el backpressure (cuando el destino no puede procesar datos tan rápido como llegan), el tracking de procedencia (qué datos llegaron de dónde y cuándo) y la recuperación ante fallos. Es especialmente popular en entornos empresariales que requieren auditoría y gobernanza del flujo de datos.

**Airbyte** es una plataforma open-source de integración de datos centrada en la ingesta (el movimiento de datos de fuente a destino) más que en la transformación. Su modelo de conectores (llamados Sources y Destinations) cubre más de 350 integraciones predefinidas: bases de datos, APIs, herramientas SaaS. Puede desplegarse en la propia infraestructura o consumirse como servicio en la nube. Su punto fuerte es la facilidad de configuración: en muchos casos, añadir un nuevo conector requiere solo especificar las credenciales y el destino a través de una interfaz web.

**Fivetran** es la alternativa comercial gestionada. Ofrece un catálogo de conectores mantenidos de forma centralizada, con actualizaciones automáticas cuando las APIs de origen cambian. Su propuesta de valor es la eliminación total del mantenimiento de la infraestructura de ingesta: el equipo de datos se ocupa de qué datos extraer y dónde, no de cómo mantener los conectores funcionando. Su principal limitación es el coste, que puede ser significativo a escala.

| Herramienta | Tipo | Modelo | Mejor para |
|---|---|---|---|
| Apache NiFi | Open-source, on-premise | Visual, flow-based | Empresas con requisitos de gobernanza |
| Airbyte | Open-source / Cloud | Conector-based | Equipos que quieren control y flexibilidad |
| Fivetran | SaaS gestionado | Conector-based | Equipos que priorizan mantenimiento cero |
| Apache Spark | Open-source | Programático | Transformaciones a escala con ETL complejo |
| dbt (con Airbyte/Fivetran) | Open-source | SQL-based | Capa ELT de transformación en el warehouse |

### 5.3 Idempotencia y gestión de duplicados en la ingesta

La **idempotencia** es la propiedad de una operación de producir el mismo resultado independientemente de cuántas veces se ejecute. En el contexto de pipelines de ingesta, un pipeline idempotente puede reejecutarse para el mismo período sin duplicar datos en el destino. Esta propiedad es esencial porque los pipelines fallan: una caída de red a mitad de la carga, un timeout de base de datos o un error en el servidor pueden interrumpir el proceso, y la solución más simple —relanzar el pipeline— solo es segura si el pipeline es idempotente.

Las estrategias de idempotencia más comunes son:

**Upsert en el destino.** En lugar de insertar siempre, se verifica si el registro ya existe (por clave primaria) y se actualiza si existe o se inserta si no. En SQL, esto se implementa con `INSERT ... ON CONFLICT DO UPDATE` en PostgreSQL o `MERGE` en SQL Server y BigQuery.

**Particionamiento por período y sobrescritura.** Los datos se cargan en particiones (por ejemplo, una partición por día). Si el pipeline se relanza para el mismo día, la partición se sobrescribe en lugar de añadirse. Este patrón es muy común en data lakes sobre S3 o GCS con formato Parquet.

**Deduplicación post-carga.** Los datos se cargan tal cual, incluyendo potenciales duplicados, y una etapa posterior de deduplicación identifica y elimina los registros duplicados basándose en una clave natural. Este enfoque es más permisivo en la ingesta pero requiere más trabajo en la transformación.

```sql
-- Ejemplo de upsert en PostgreSQL
INSERT INTO clientes_dw (id, nombre, email, fecha_modificacion)
SELECT id, nombre, email, updated_at
FROM clientes_staging
ON CONFLICT (id)
DO UPDATE SET
    nombre = EXCLUDED.nombre,
    email = EXCLUDED.email,
    fecha_modificacion = EXCLUDED.fecha_modificacion
WHERE clientes_dw.fecha_modificacion < EXCLUDED.fecha_modificacion;
```

La gestión de duplicados es especialmente desafiante en fuentes de streaming, donde el mismo evento puede llegar varias veces debido a fallos de red o reintentos del productor. Los sistemas de procesamiento de streams como Kafka Streams o Apache Flink ofrecen semánticas de entrega exactly-once que resuelven este problema a nivel de infraestructura, pero con un coste de complejidad y latencia que debe evaluarse en cada caso.

---

## Actividades prácticas propuestas

**Actividad 1 — Extracción desde base de datos relacional con carga incremental**
Configurar una base de datos PostgreSQL local con el dataset público de taxis de Nueva York (NYC Taxi Trips). Implementar un script Python con SQLAlchemy que realice una extracción incremental basada en la columna `tpep_pickup_datetime`, almacene la marca temporal del último registro procesado en un fichero de estado y exporte los datos incrementales a formato Parquet particionado por fecha. Verificar la idempotencia relanzando el script para el mismo período.

**Actividad 2 — Consumo de API REST con paginación y autenticación**
Consumir la API pública de la NASA (NASA Open APIs, `api.nasa.gov`) para extraer datos de asteroides cercanos a la Tierra (Near Earth Objects) mediante el endpoint `/neo/rest/v1/feed`. Implementar paginación, gestión de la clave API mediante variables de entorno, manejo de errores con reintentos exponenciales usando `tenacity`, y almacenamiento de los resultados en un fichero JSON Lines (un objeto JSON por línea).

**Actividad 3 — Web scraping de una tienda online**
Realizar scraping del sitio de demostración `books.toscrape.com` para extraer el catálogo completo de libros: título, precio, rating y URL de la portada. Implementar la navegación por páginas, exportar los resultados a CSV y Parquet, y añadir un control de cortesía (`time.sleep`) entre peticiones. Comparar el tamaño de los ficheros CSV y Parquet resultantes.

**Actividad 4 — Conversión de formatos y benchmarking**
Tomar un dataset CSV de al menos 1 millón de filas (por ejemplo, el dataset de vuelos de BTS o el de transacciones de Kaggle). Convertirlo a JSON Lines, Parquet (compresión Snappy) y Parquet (compresión Gzip). Medir el tiempo de escritura, el tamaño en disco y el tiempo de lectura de una consulta de aggregación simple en cada formato usando Pandas y DuckDB. Documentar los resultados en una tabla comparativa.

**Actividad 5 — Pipeline de ingesta con Airbyte**
Desplegar Airbyte en local con Docker Compose. Configurar una conexión desde una fuente PostgreSQL hasta un destino en ficheros locales (formato Parquet). Ejecutar una sincronización completa, modificar varios registros en la fuente y ejecutar una sincronización incremental. Verificar que solo los registros modificados han sido procesados.

---

## Referencias y material externo

### Libros

- Kleppmann, M. (2017). *Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems*. O'Reilly Media. ISBN 978-1-4493-7332-0. Capítulos 3, 10 y 11 son especialmente relevantes para esta unidad.

- Reis, J. y Housley, M. (2022). *Fundamentals of Data Engineering: Plan and Build Robust Data Systems*. O'Reilly Media. ISBN 978-1-0981-0820-2. Cubre en detalle las fases de ingestión y almacenamiento del ciclo de vida del dato.

- Kinley, J. y Mercer, J. (2023). *Data Pipelines Pocket Reference: Moving and Processing Data for Analytics*. O'Reilly Media. ISBN 978-1-4920-8922-3. Referencia práctica para implementación de pipelines.

- Marz, N. y Warren, J. (2015). *Big Data: Principles and Best Practices of Scalable Realtime Data Systems*. Manning Publications. ISBN 978-1-6172-9034-3. Introduce la arquitectura Lambda, precursora de los patrones de ingesta modernos.

### Documentación oficial

- SQLAlchemy — Documentación oficial: https://docs.sqlalchemy.org/
- pymongo — Documentación oficial: https://pymongo.readthedocs.io/
- Apache Kafka — Documentación oficial: https://kafka.apache.org/documentation/
- confluent-kafka-python — Documentación y ejemplos: https://docs.confluent.io/kafka-clients/python/current/overview.html
- Scrapy — Documentación oficial: https://docs.scrapy.org/
- Playwright para Python: https://playwright.dev/python/docs/intro
- Apache Parquet — Especificación del formato: https://parquet.apache.org/docs/
- Apache Avro — Especificación y herramientas: https://avro.apache.org/docs/
- pyarrow — Documentación oficial: https://arrow.apache.org/docs/python/
- Airbyte — Documentación oficial: https://docs.airbyte.com/
- Debezium — CDC para múltiples bases de datos: https://debezium.io/documentation/
- tenacity — Librería de reintentos para Python: https://tenacity.readthedocs.io/

### Papers y recursos académicos

- Armbrust, M. et al. (2021). *Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics*. Proceedings of CIDR 2021. http://cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf

- Zaharia, M. et al. (2016). *Apache Spark: A Unified Engine for Big Data Processing*. Communications of the ACM, 59(11), 56–65. https://dl.acm.org/doi/10.1145/2934664

- Goodhope, K. et al. (2012). *Building LinkedIn's Real-time Activity Data Pipeline*. IEEE Data Engineering Bulletin, 35(2), 33–45. Uno de los papers fundacionales sobre el uso de Kafka en producción.

- Chandarana, P. y Vijayalakshmi, M. (2014). *Big Data Analytics Frameworks*. International Conference on Circuits, Systems, Communication and Information Technology Applications (CSCITA). Revisión de los principales frameworks de procesamiento de datos a escala.

### Recursos en línea complementarios

- NASA Open APIs (para la actividad práctica 2): https://api.nasa.gov/
- Books to Scrape (sitio de práctica para scraping): https://books.toscrape.com/
- NYC Taxi and Limousine Commission — Dataset público: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- Awesome Data Engineering — Repositorio curado de recursos: https://github.com/igorbarinov/awesome-data-engineering
- Data Engineering Weekly — Newsletter de referencia del sector: https://www.dataengineeringweekly.com/
