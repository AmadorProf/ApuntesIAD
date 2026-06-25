---
marp: true
theme: default
paginate: true
size: 16:9
header: 'MP04 · UD3 · Integracion con fuentes, herramientas y sistemas (RAG)'
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

# UD3 · Integracion con fuentes, herramientas y sistemas (RAG)

**MP04 · Soluciones basadas en LLMs**
Apuntes de IA y Datos

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno sera capaz de:

- Identificar y habilitar fuentes de informacion adecuadas para alimentar un sistema RAG.
- Implementar la indexacion y recuperacion de documentos usando embeddings y busqueda semantica.
- Incorporar la informacion recuperada al contexto del modelo verificando su pertinencia y vigencia.
- Integrar herramientas externas, APIs y canales de comunicacion en la solucion LLM.
- Validar la comunicacion con sistemas externos mediante pruebas especificas.

---

## 1 · Habilitacion de fuentes de informacion

### Caracterizacion de las fuentes

Antes de indexar cualquier fuente, se debe caracterizar:

| Atributo | Preguntas clave |
|---|---|
| **Origen** | ¿De donde provienen los datos? (intranet, ERP, web publica, base de datos...) |
| **Formato** | PDF, Word, HTML, JSON, CSV, SQL... |
| **Frecuencia de actualizacion** | ¿Cada cuanto cambia el contenido? ¿Hay versionado? |
| **Permisos de acceso** | ¿Quien puede leer estos datos? ¿Hay documentos confidenciales mezclados? |
| **Calidad** | ¿Hay duplicados, informacion desactualizada, errores de formato? |

> Una fuente de mala calidad produce un sistema RAG de mala calidad. El trabajo de preparacion de fuentes es tan critico como el diseno del sistema.

---

## 1 · Habilitacion de fuentes de informacion (cont.)

### Pipeline de ingestion de documentos

```
Fuente original
     |
     v
[Extraccion de texto]
 PDF → pdfplumber / pymupdf
 Word → python-docx
 HTML → BeautifulSoup
 Tablas → pandas
     |
     v
[Limpieza]
 Eliminar cabeceras/pies de pagina redundantes
 Normalizar espacios y saltos de linea
 Eliminar paginas en blanco o con solo imagenes
     |
     v
[Metadatos]
 Origen, titulo, fecha, version, autor, seccion
     |
     v
[Fragmentacion]   →   [Generacion de embeddings]   →   [Base de datos vectorial]
```

---

## 2 · Recuperacion de informacion: fragmentacion (I)

### Estrategias de fragmentacion (chunking)

La fragmentacion divide los documentos en unidades recuperables. La estrategia afecta directamente a la calidad de las respuestas:

| Estrategia | Descripcion | Cuando usar |
|---|---|---|
| **Por tokens fijos** | Fragmentos de N tokens con solapamiento | Documentos homogeneos, texto continuo sin estructura |
| **Por parrafos o secciones** | Respeta la estructura logica del documento | PDFs con secciones claras, manuales tecnicos |
| **Semantica** | Fragmenta cuando cambia el tema o la coherencia | Documentos mixtos, correos, articulos |
| **Recursiva** | Divide por jerarquias: documento → capitulo → seccion → parrafo | Libros, normativas, contratos extensos |
| **Hibrida** | Combina criterios segun el tipo de bloque | Proyectos con multiples tipos de documentos |

**Parametros clave:**
- `chunk_size`: numero maximo de tokens por fragmento (tipicamente 256-512)
- `chunk_overlap`: solapamiento entre fragmentos contiguos para preservar contexto (tipicamente 10-20% del chunk_size)

---

## 2 · Recuperacion de informacion: fragmentacion (II)

### Implementacion con LangChain

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=64,
    separators=["\n\n", "\n", ". ", " ", ""]
)

# Cargar y dividir un documento
with open("manual_operaciones.txt", "r", encoding="utf-8") as f:
    texto = f.read()

fragmentos = splitter.create_documents(
    texts=[texto],
    metadatas=[{"origen": "manual_operaciones", "version": "2025-Q1"}]
)

print(f"Total fragmentos: {len(fragmentos)}")
print(f"Fragmento 0: {fragmentos[0].page_content[:200]}...")
```

---

## 2 · Recuperacion de informacion: embeddings y busqueda (I)

### Representaciones vectoriales (embeddings)

Un embedding es la representacion numerica de un texto en un espacio de alta dimension. Textos semanticamente similares tienen vectores cercanos.

| Modelo de embeddings | Dimension | Proveedor | Notas |
|---|---|---|---|
| `text-embedding-3-small` | 1536 | OpenAI | Buena relacion calidad/coste |
| `text-embedding-3-large` | 3072 | OpenAI | Mayor precision, mas caro |
| `embed-multilingual-v3.0` | 1024 | Cohere | Buen soporte multilingue |
| `all-MiniLM-L6-v2` | 384 | HuggingFace | Open source, rapido, local |
| `nomic-embed-text` | 768 | Nomic | Open source, buen rendimiento |

**Proceso de indexacion:**
```python
from openai import OpenAI

client = OpenAI()

def generar_embedding(texto: str) -> list[float]:
    respuesta = client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )
    return respuesta.data[0].embedding
```

---

## 2 · Recuperacion de informacion: embeddings y busqueda (II)

### Bases de datos vectoriales y busqueda hibrida

| Base de datos vectorial | Tipo | Caracteristicas |
|---|---|---|
| **Chroma** | Local / open source | Facil de usar, ideal para prototipado |
| **FAISS** | Local / open source | Alta velocidad, de Meta Research |
| **Pinecone** | SaaS | Escalable, gestionado, sin mantenimiento |
| **Weaviate** | Open source / SaaS | Busqueda hibrida integrada |
| **pgvector** | Extension PostgreSQL | Integrado en PostgreSQL existente |

**Busqueda hibrida (vectorial + lexica):**

```python
# Busqueda semantica (vectorial)
resultados_vectoriales = vector_db.similarity_search(
    query=consulta_usuario,
    k=5
)

# Busqueda lexica (BM25)
resultados_bm25 = bm25_index.search(query=consulta_usuario, k=5)

# Fusion con Reciprocal Rank Fusion (RRF)
resultados_finales = rrf_fusion(resultados_vectoriales, resultados_bm25)
```

---

## 3 · Incorporacion de informacion al contexto

### Verificacion de pertinencia y vigencia

No todos los fragmentos recuperados son utiles. Se debe filtrar antes de incluirlos en el contexto:

**Criterios de pertinencia:**
- Puntuacion de similitud superior a un umbral (ej. similitud coseno > 0.75)
- El fragmento responde a la pregunta y no solo comparte palabras clave

**Criterios de vigencia:**
- Fecha del documento dentro del periodo valido
- Version del documento coincide con la version activa

```python
def filtrar_fragmentos(fragmentos: list[dict], umbral_similitud: float = 0.75) -> list[dict]:
    return [
        f for f in fragmentos
        if f["score"] >= umbral_similitud
        and not f["metadata"].get("obsoleto", False)
    ]
```

**Limites de inclusion:**
- Nunca superar el 60-70% de la ventana de contexto con documentos recuperados
- Reservar espacio para el historial y la respuesta del modelo

---

## 4 · Integracion de herramientas y APIs externas (I)

### Function calling y tool use

La integracion de herramientas permite al modelo invocar funciones externas cuando necesita informacion o acciones que no puede resolver por si mismo:

```python
herramientas = [
    {
        "name": "buscar_pedido",
        "description": "Busca el estado de un pedido por su numero en el sistema ERP",
        "input_schema": {
            "type": "object",
            "properties": {
                "numero_pedido": {
                    "type": "string",
                    "description": "Numero de pedido en formato PED-XXXXX"
                }
            },
            "required": ["numero_pedido"]
        }
    }
]

respuesta = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    tools=herramientas,
    messages=[{"role": "user", "content": "¿Donde esta mi pedido PED-12345?"}]
)
```

---

## 4 · Integracion de herramientas y APIs externas (II)

### Gestion de credenciales y permisos

Las credenciales de acceso a APIs externas nunca deben codificarse en el codigo fuente:

| Practica correcta | Practica incorrecta |
|---|---|
| Variables de entorno (`os.environ["API_KEY"]`) | Credenciales en texto plano en el codigo |
| Gestores de secretos (HashiCorp Vault, AWS Secrets Manager) | Credenciales en archivos de configuracion sin cifrar |
| Variables de entorno del sistema CI/CD | Credenciales en repositorios de codigo |

**Validacion de permisos antes de ejecutar una herramienta:**

```python
PERMISOS_USUARIO = {"buscar_pedido", "consultar_catalogo"}

def ejecutar_herramienta(nombre: str, args: dict, permisos: set) -> dict:
    if nombre not in permisos:
        return {"error": f"Accion '{nombre}' no permitida para este usuario"}
    # ejecutar la herramienta...
```

---

## 5 · Integracion con canales de comunicacion

### Despliegue en canales corporativos y web

| Canal | Protocolo de integracion | Consideraciones especificas |
|---|---|---|
| **Web (chat widget)** | WebSocket o REST + polling | Gestion de sesiones, autenticacion JWT |
| **Movil (iOS / Android)** | REST API | Latencia de red movil, respuestas incrementales |
| **Microsoft Teams** | Bot Framework SDK | Tarjetas adaptativas, permisos de tenant |
| **Slack** | Slack Bolt SDK | Eventos de slash command, OAuth por workspace |
| **Correo electronico** | Webhook + parser de email | Extraccion de contexto, respuesta por hilo |
| **API publica** | REST / GraphQL | Versionado, rate limiting, documentacion OpenAPI |

**Gestion de sesion:**

```python
import uuid

sesiones = {}  # En produccion: Redis o base de datos

def obtener_o_crear_sesion(session_id: str | None) -> dict:
    if not session_id or session_id not in sesiones:
        session_id = str(uuid.uuid4())
        sesiones[session_id] = {"historial": [], "metadata": {}}
    return sesiones[session_id], session_id
```

---

## 6 · Validacion de las integraciones

### Pruebas especificas para sistemas RAG

| Tipo de prueba | Que verifica | Herramienta |
|---|---|---|
| **Recuperacion** | Los fragmentos correctos se recuperan para preguntas representativas | Metricas Recall@K, MRR |
| **Relevancia de respuesta** | La respuesta usa la informacion recuperada y no alucina | Evaluacion manual o con LLM-as-judge |
| **Trazabilidad** | Cada respuesta puede vincularse a los fragmentos fuente | Log de fragmentos usados por llamada |
| **Actualizacion** | Al actualizar la fuente, los nuevos documentos se indexan correctamente | Test de regresion de indexacion |
| **Limites** | El sistema se comporta correctamente cuando no hay fragmentos relevantes | Preguntas fuera del corpus |

```python
# Evaluacion de recuperacion: Recall@5
def recall_at_k(fragmentos_esperados: list[str], fragmentos_recuperados: list[str], k: int = 5) -> float:
    recuperados_k = set(fragmentos_recuperados[:k])
    esperados = set(fragmentos_esperados)
    return len(recuperados_k & esperados) / len(esperados) if esperados else 0.0
```

---

## Actividad practica · UD3

### Construccion de un sistema RAG basico

**Enunciado:**

Construye un sistema RAG que permita responder preguntas sobre un conjunto de tres documentos PDF de tu eleccion (pueden ser manuales tecnicos, normativas o articulos).

**Tareas:**

1. Extrae el texto de los PDFs y aplica limpieza basica.
2. Fragmenta los documentos con chunk_size=400 y chunk_overlap=50. Registra el numero de fragmentos generados.
3. Genera embeddings con el modelo de tu eleccion e indexalos en ChromaDB.
4. Implementa la funcion de recuperacion con busqueda semantica (top-5 fragmentos).
5. Construye el prompt final combinando los fragmentos recuperados con la pregunta del usuario.
6. Prueba el sistema con cinco preguntas: tres cuya respuesta esta en los documentos y dos fuera del corpus.
7. Registra los fragmentos recuperados y la puntuacion de similitud en cada prueba.

**Entregable:** notebook Jupyter con el pipeline completo + tabla de resultados de las cinco pruebas.

---

## Puntos clave · UD3

- La calidad de las fuentes determina la calidad del sistema RAG; la preparacion de datos es critica.
- La fragmentacion debe preservar la coherencia semantica: solapamiento adecuado y respetar la estructura del documento.
- Los embeddings traducen el significado del texto a un espacio vectorial; modelos distintos producen espacios incompatibles.
- La busqueda hibrida (vectorial + lexica) supera a cualquiera de las dos por separado en la mayoria de casos reales.
- Los fragmentos recuperados deben filtrarse por pertinencia y vigencia antes de incluirlos en el contexto.
- Las credenciales de APIs externas deben gestionarse con variables de entorno o gestores de secretos, nunca en el codigo.

---

## Criterios de evaluacion · UD3

| Criterio | Indicadores de logro |
|---|---|
| **Configura mecanismos de recuperacion** | Implementa fragmentacion con parametros justificados; indexa y recupera con embeddings; calcula metricas de recuperacion |
| **Integra herramientas y canales** | Define herramientas con schema; gestiona credenciales correctamente; implementa la logica de ejecucion |
| **Valida la comunicacion con sistemas externos** | Ejecuta pruebas de recuperacion con preguntas dentro y fuera del corpus; registra resultados con trazabilidad |

---

<!-- _class: lead -->

[← Volver a MP04](../index.md)


---

<!-- nav-slide -->

## Navegación

[← UD2 · Componentes de interaccion co…](../UD2_Componentes-interaccion/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD4 · Comportamientos agenticos →](../UD4_Comportamientos-agenticos/)
