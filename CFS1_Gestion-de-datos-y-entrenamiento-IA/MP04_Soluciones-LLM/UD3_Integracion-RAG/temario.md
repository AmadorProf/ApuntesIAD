# UD3 · Integración con fuentes, herramientas y sistemas: RAG

**Módulo:** MP04 · Soluciones LLM  
**Ciclo:** CFS1 · Gestión de datos y entrenamiento IA  
**Nivel:** Formación Superior  
**Duración estimada:** 12 horas lectivas

---

## 1. Introducción

Los modelos de lenguaje de gran escala (LLMs) han transformado la forma en que interactuamos con sistemas de información. Sin embargo, presentan limitaciones estructurales que los hacen poco fiables en contextos que requieren precisión factual, actualización constante o acceso a conocimiento privado o especializado.

### 1.1 Limitaciones de los LLMs sin contexto externo

**Conocimiento estático y fecha de corte.** Un LLM se entrena sobre un corpus fijo que tiene una fecha de cierre. GPT-4, Claude o Llama no conocen eventos posteriores a su entrenamiento. En aplicaciones empresariales esto es crítico: un sistema de soporte técnico que desconozca la última versión de un producto, o un asistente legal que ignore una normativa reciente, generará respuestas obsoletas o directamente incorrectas.

**Alucinaciones sobre hechos.** Los LLMs no recuperan información; la generan. Cuando se les pregunta sobre datos específicos — nombres propios, cifras, fechas, citas textuales — el modelo puede producir texto coherente pero factualmente incorrecto. Este fenómeno, conocido como alucinación, ocurre porque el modelo optimiza la verosimilitud lingüística, no la veracidad factual. En dominios de alto riesgo (medicina, derecho, finanzas) esto resulta inaceptable.

**Incapacidad de acceder a conocimiento privado.** Las organizaciones acumulan grandes volúmenes de documentación interna: manuales, contratos, bases de conocimiento, registros de soporte. Un LLM de propósito general no tiene acceso a este corpus y no puede ser interrogado sobre él salvo que se le proporcione explícitamente en el prompt, lo que tiene sus propios límites de extensión.

**Limitaciones de la ventana de contexto.** Aunque los modelos actuales tienen ventanas de contexto cada vez más amplias (128K tokens en GPT-4o, 200K en Claude 3.5 Sonnet), insertar documentos completos en cada consulta es costoso, lento e ineficiente. El modelo tiende a perder precisión con contextos muy largos, un fenómeno conocido como "lost in the middle".

### 1.2 RAG como solución arquitectónica

Retrieval-Augmented Generation (RAG) es una arquitectura que combina la capacidad generativa de los LLMs con un sistema de recuperación de información. En lugar de depender exclusivamente del conocimiento parametrizado del modelo, RAG recupera documentos relevantes en tiempo de inferencia y los incluye en el prompt como contexto. El modelo genera entonces una respuesta fundamentada en esa información recuperada.

La propuesta fue formalizada por Lewis et al. (2020) en el paper "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Facebook AI Research), y desde entonces se ha convertido en la arquitectura de referencia para aplicaciones LLM que requieren precisión factual.

RAG resuelve simultáneamente varios problemas: permite actualizar el conocimiento sin reentrenar el modelo (basta con actualizar el índice), reduce las alucinaciones al anclar la generación en documentos concretos, y permite citar fuentes, lo que aumenta la transparencia y auditabilidad del sistema.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Explicar las limitaciones estructurales de los LLMs y justificar la necesidad de arquitecturas RAG en contextos de producción.
2. Describir el pipeline completo de un sistema RAG, desde la ingesta de documentos hasta la generación de respuesta.
3. Diferenciar entre las variantes Naive RAG, Advanced RAG y Modular RAG, identificando en qué casos aplicar cada una.
4. Comprender el concepto de embedding de texto y seleccionar el modelo de embedding adecuado según el caso de uso.
5. Aplicar estrategias de chunking apropiadas a distintos tipos de documentos, justificando la elección del tamaño y método.
6. Configurar y operar una base de datos vectorial (Chroma) en Python para indexar y recuperar documentos.
7. Implementar un pipeline de recuperación con filtrado por metadata, MMR y reranking.
8. Construir prompts de augmentación con contexto recuperado y gestionar la ventana de contexto eficientemente.
9. Evaluar la calidad de un sistema RAG utilizando el framework RAGAS y sus métricas principales.
10. Comparar y seleccionar entre frameworks RAG (LangChain, LlamaIndex) según los requisitos del proyecto.
11. Desarrollar actividades prácticas que implementen un sistema RAG funcional de extremo a extremo.

---

## 3. Arquitectura RAG

### 3.1 Pipeline completo

Un sistema RAG se articula en dos fases bien diferenciadas: la fase de indexado (offline) y la fase de recuperación y generación (online o en tiempo de inferencia).

**Fase de indexado (offline)**

1. **Ingesta de documentos.** Se cargan los documentos fuente desde distintos orígenes: archivos PDF, páginas web, bases de datos, wikis corporativas, etc. Esta fase incluye el preprocesamiento: extracción de texto, limpieza de ruido, normalización de formatos.

2. **Chunking.** Los documentos se dividen en fragmentos más pequeños (chunks). Este paso es crítico: un chunk demasiado grande puede saturar el contexto del modelo; uno demasiado pequeño puede carecer del contexto necesario para ser útil. Se detallan las estrategias en la sección 5.

3. **Embedding.** Cada chunk se transforma en un vector numérico de alta dimensión mediante un modelo de embedding. Este vector captura el significado semántico del texto. Dos chunks semánticamente similares producirán vectores próximos en el espacio vectorial.

4. **Indexado.** Los vectores se almacenan en una base de datos vectorial junto con el texto original y metadatos asociados (fuente, página, fecha de creación, etc.). El índice permite búsquedas eficientes por similitud semántica.

**Fase de recuperación y generación (online)**

5. **Embedding de la consulta.** La pregunta del usuario se transforma en un vector usando el mismo modelo de embedding utilizado durante el indexado.

6. **Recuperación.** Se realiza una búsqueda de similitud en la base de datos vectorial para encontrar los chunks cuyo vector es más próximo al de la consulta. Se recuperan los top-k más similares.

7. **Augmentación.** Los chunks recuperados se insertan en el prompt junto con la pregunta original, siguiendo una plantilla que instruye al modelo a responder basándose en el contexto proporcionado.

8. **Generación.** El LLM genera la respuesta final fundamentada en el contexto recuperado.

### 3.2 Diagrama del pipeline

```
[Documentos fuente]
       |
  [Ingesta y limpieza]
       |
   [Chunking]
       |
  [Embedding model] → [Vectores]
       |
  [Vector store] ←─────────────────────────┐
       |                                    |
       |           [Consulta del usuario]   |
       |                  |                 |
       |          [Embedding model]         |
       |                  |                 |
       └──── [Similarity search] ──── [Top-k chunks]
                                           |
                                   [Augmentación del prompt]
                                           |
                                       [LLM]
                                           |
                                   [Respuesta final]
```

### 3.3 Naive RAG vs Advanced RAG vs Modular RAG

**Naive RAG** es la implementación más directa: chunking simple, embedding, búsqueda por similitud, inserción en prompt. Es el punto de partida y funciona bien para casos sencillos, pero tiene limitaciones: la recuperación puede ser ruidosa, el ranking no siempre refleja la relevancia real para la tarea, y no hay mecanismos de refinamiento.

**Advanced RAG** incorpora mejoras en cada etapa del pipeline. En la fase de indexado: chunking más sofisticado, enriquecimiento de metadatos, indexado jerárquico. En la fase de recuperación: reranking con cross-encoders, query expansion (reformulación de la consulta para mejorar el recall), y técnicas como HyDE (Hypothetical Document Embeddings). En la fase de generación: gestión activa del contexto, detección de información contradictoria.

**Modular RAG** descompone el pipeline en módulos intercambiables. Cada etapa — recuperación, reranking, augmentación, generación — puede ser sustituida, combinada o paralelizada. Permite arquitecturas como RAG con múltiples fuentes de conocimiento, RAG iterativo (donde el modelo puede hacer múltiples rondas de recuperación), o RAG con herramientas (el modelo puede decidir cuándo recuperar y cuándo no). Es la evolución natural hacia sistemas más robustos y flexibles.

---

## 4. Embeddings y modelos de embedding

### 4.1 Qué es un embedding de texto

Un embedding es una representación vectorial densa de un texto en un espacio de alta dimensión (típicamente entre 384 y 3072 dimensiones). La propiedad fundamental de los embeddings es que la distancia entre vectores refleja la similitud semántica entre los textos que representan.

Formalmente: dado un modelo de embedding `f`, y dos textos `t1` y `t2`, si `t1` y `t2` son semánticamente similares, entonces `cos(f(t1), f(t2)) ≈ 1`.

Los embeddings se generan a partir de modelos transformer entrenados con objetivos contrastivos: se enseña al modelo a asignar vectores cercanos a pares de textos similares y vectores lejanos a pares de textos distintos. El conjunto de entrenamiento suele consistir en pares (pregunta, respuesta) o (documento, resumen).

### 4.2 Principales modelos de embedding

**text-embedding-3-small y text-embedding-3-large (OpenAI).** Son los modelos de embedding de OpenAI. `text-embedding-3-small` produce vectores de 1536 dimensiones y ofrece un excelente balance entre coste y rendimiento. `text-embedding-3-large` produce vectores de 3072 dimensiones y alcanza mejor rendimiento en tareas de recuperación exigentes. Ambos son accesibles vía API. Su principal ventaja es la facilidad de integración en ecosistemas que ya usan la API de OpenAI; su principal limitación es que son servicios externos de pago y los datos se envían a los servidores de OpenAI.

**E5-large-v2 (Microsoft).** Modelo de código abierto publicado por Microsoft Research, disponible en Hugging Face. Produce vectores de 1024 dimensiones. Ha sido entrenado con datos masivos de pares texto-texto y tiene un rendimiento sobresaliente en inglés. Permite despliegue local, lo que lo hace atractivo para entornos con restricciones de privacidad.

**BGE-M3 (BAAI).** Desarrollado por el Beijing Academy of Artificial Intelligence. Es un modelo multilingüe que soporta más de 100 idiomas, incluyendo el español. Soporta tres modos de recuperación simultáneos: dense retrieval (vectores densos), sparse retrieval (BM25-style) y multi-vector retrieval (ColBERT-style). Es especialmente adecuado para aplicaciones multilingües o híbridas.

**Jina Embeddings.** Jina AI ofrece modelos de embedding de código abierto con capacidad para contextos muy largos (hasta 8192 tokens por chunk), lo que los diferencia de alternativas que truncan a 512 tokens. Son una buena opción cuando los chunks son fragmentos extensos.

### 4.3 Evaluación con MTEB Leaderboard

El MTEB (Massive Text Embedding Benchmark) es la referencia estándar para evaluar modelos de embedding. Cubre 56 datasets en 8 categorías de tareas: clasificación, clustering, reranking, recuperación, STS (Semantic Textual Similarity), summarization, bitext mining y pair classification. La tabla de clasificación pública en Hugging Face permite comparar modelos por categoría, idioma y tamaño.

Para seleccionar un modelo de embedding en un proyecto RAG, se recomienda consultar el MTEB filtrando por la tarea "Retrieval" y, si el corpus es en español, filtrar además por idioma. No siempre el modelo con mejor posición global es el mejor para el caso de uso concreto.

### 4.4 Generación de embeddings con Python

**Con la API de OpenAI:**

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")

response = client.embeddings.create(
    input="La inteligencia artificial transforma la industria",
    model="text-embedding-3-small"
)

vector = response.data[0].embedding
print(f"Dimensiones: {len(vector)}")  # 1536
```

**Con sentence-transformers (local):**

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-m3")

textos = [
    "La inteligencia artificial transforma la industria",
    "El aprendizaje automático mejora los procesos empresariales",
    "El precio del café ha subido este mes"
]

vectores = model.encode(textos, normalize_embeddings=True)
print(f"Shape: {vectores.shape}")  # (3, 1024)
```

La normalización de los vectores (norma unitaria) es importante cuando se usa cosine similarity, ya que simplifica el cálculo a un producto escalar.

---

## 5. Chunking strategies

### 5.1 Por qué importa el chunking

El chunking es uno de los factores que más impacta en la calidad de un sistema RAG. Un chunk es la unidad mínima de recuperación: si la información relevante para una consulta está repartida en varios chunks o está mezclada con información irrelevante dentro del mismo chunk, la recuperación será imprecisa.

### 5.2 Chunking por tamaño fijo con overlap

La estrategia más simple: dividir el texto en fragmentos de N caracteres (o tokens), con un solapamiento (overlap) entre chunks consecutivos para evitar que el contexto se pierda en los bordes.

```python
from langchain.text_splitter import CharacterTextSplitter

splitter = CharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separator="\n"
)

chunks = splitter.split_text(texto)
```

Es rápida y predecible, pero ignora la estructura semántica del documento. Puede partir oraciones o párrafos en puntos arbitrarios.

### 5.3 Chunking por estructura

Divide el texto respetando sus unidades naturales: párrafos, secciones, oraciones. Para documentos bien estructurados (PDFs con secciones, artículos académicos, documentación técnica) esta estrategia produce chunks más coherentes.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = splitter.split_documents(documentos)
```

`RecursiveCharacterTextSplitter` intenta dividir primero por párrafos (`\n\n`), luego por líneas, luego por oraciones, y solo recurre a caracteres individuales si es necesario. Es la opción por defecto más recomendada en LangChain.

### 5.4 Chunk size óptimo: trade-off

Existe una tensión fundamental entre el tamaño del chunk y la calidad de la recuperación:

- **Chunks pequeños (100-300 tokens):** Mayor precisión en la recuperación (cada chunk es más específico), pero mayor riesgo de perder contexto. Si la respuesta requiere integrar varias oraciones, un chunk demasiado pequeño puede no contener suficiente información.
- **Chunks grandes (800-1500 tokens):** Mayor contexto por chunk, pero menor precisión en la recuperación (el vector representa un concepto más difuso) y mayor consumo de tokens en el prompt.

La recomendación práctica es experimentar con tamaños entre 256 y 1024 tokens, evaluar con RAGAS, y ajustar según los resultados. Para documentos técnicos densos, chunks de 512 tokens con overlap de 64 suelen funcionar bien como punto de partida.

### 5.5 Semantic chunking

En lugar de dividir por tamaño o estructura, el semantic chunking analiza la similitud semántica entre oraciones consecutivas y divide cuando hay un cambio temático significativo. Esto produce chunks temáticamente cohesivos.

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

splitter = SemanticChunker(
    embeddings=OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile"
)

chunks = splitter.split_text(texto)
```

Es computacionalmente más costoso (requiere generar embeddings durante el chunking), pero puede mejorar la recuperación en documentos con estructura temática clara.

### 5.6 Metadata de chunks

Cada chunk debe ir acompañado de metadatos que permitan filtrar, citar y auditar. Los metadatos mínimos recomendados son:

- `source`: ruta o URL del documento origen.
- `page`: número de página (para PDFs).
- `chunk_index`: posición del chunk dentro del documento.
- `created_at`: fecha de indexado.
- `section`: título de la sección (si está disponible).
- `document_type`: tipo de documento (manual, contrato, artículo, etc.).

```python
from langchain.schema import Document

chunk = Document(
    page_content="El contrato entrará en vigor el 1 de enero de 2025.",
    metadata={
        "source": "contratos/contrato_2024_001.pdf",
        "page": 3,
        "chunk_index": 7,
        "created_at": "2025-01-15",
        "section": "Cláusula de vigencia",
        "document_type": "contrato"
    }
)
```

---

## 6. Bases de datos vectoriales

### 6.1 Comparativa de soluciones

Las bases de datos vectoriales son sistemas especializados en almacenar y consultar vectores de alta dimensión mediante búsquedas de similitud eficientes.

**Chroma.** Base de datos vectorial de código abierto diseñada para uso local y desarrollo. Es la opción más sencilla de integrar en proyectos Python. No requiere infraestructura adicional: puede operar completamente en memoria o persistir en disco. Ideal para prototipos, proyectos educativos y aplicaciones de pequeña escala.

**Qdrant.** Motor de búsqueda vectorial de código abierto escrito en Rust, lo que le confiere un rendimiento sobresaliente. Ofrece soporte para filtrado avanzado por payload (metadatos), cuantización de vectores para reducir el uso de memoria, y despliegue en contenedor Docker. Recomendado para producción con datasets medianos y grandes.

**Weaviate.** Base de datos vectorial de código abierto con capacidades de módulos: permite combinar búsqueda vectorial con búsqueda BM25 (híbrida) de forma nativa. Tiene un esquema de datos tipado y soporte para múltiples modelos de embedding integrados. Adecuado para aplicaciones empresariales con esquemas de datos complejos.

**Pinecone.** Servicio gestionado en la nube (serverless). La principal ventaja es la ausencia de gestión de infraestructura; la principal desventaja es el coste y la dependencia del proveedor. Adecuado para equipos que priorizan la velocidad de despliegue sobre el control de la infraestructura.

**pgvector (PostgreSQL).** Extensión de PostgreSQL que añade soporte para vectores. Permite combinar búsqueda vectorial con consultas SQL relacionales en la misma base de datos. Especialmente atractivo para organizaciones que ya tienen infraestructura PostgreSQL y quieren evitar introducir un nuevo componente.

### 6.2 Métricas de similitud

**Cosine similarity.** Mide el ángulo entre dos vectores, ignorando su magnitud. Valor 1 significa vectores idénticos en dirección; valor 0 significa ortogonales (sin similitud); valor -1 significa opuestos. Es la métrica más usada en RAG.

**Dot product (producto escalar).** Combinación de la magnitud y el ángulo. Si los vectores están normalizados, es equivalente a cosine similarity. Más eficiente computacionalmente.

**Euclidean distance (L2).** Mide la distancia geométrica entre vectores. Menor distancia implica mayor similitud. Sensible a la magnitud de los vectores; requiere normalización para comparaciones consistentes.

### 6.3 HNSW indexing

Hierarchical Navigable Small World (HNSW) es el algoritmo de indexado estándar en bases de datos vectoriales. Construye un grafo jerárquico de múltiples capas: las capas superiores permiten saltos largos para localizar regiones del espacio vectorial rápidamente; las capas inferiores proporcionan acceso granular a los vecinos más próximos. El resultado es una búsqueda aproximada de vecinos más próximos (ANN) con complejidad logarítmica en el tiempo de consulta, a costa de un coste de indexado mayor que la búsqueda exhaustiva.

Los parámetros clave de HNSW son `M` (número de conexiones por nodo en cada capa) y `ef_construction` (tamaño del conjunto de candidatos durante la construcción). Valores más altos mejoran la precisión pero aumentan el tiempo y la memoria de indexado.

### 6.4 Ejemplo completo con Chroma en Python

```python
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

# Inicializar cliente con persistencia en disco
client = chromadb.PersistentClient(path="./chroma_db")

# Función de embedding
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-m3"
)

# Crear o recuperar colección
coleccion = client.get_or_create_collection(
    name="documentos_empresa",
    embedding_function=ef,
    metadata={"hnsw:space": "cosine"}
)

# Indexar documentos
coleccion.add(
    documents=[
        "La política de vacaciones permite 30 días al año.",
        "El proceso de onboarding dura dos semanas.",
        "Los gastos de viaje deben reportarse en 48 horas."
    ],
    metadatas=[
        {"source": "rrhh/politica_vacaciones.pdf", "page": 1},
        {"source": "rrhh/onboarding_guide.pdf", "page": 5},
        {"source": "finanzas/politica_gastos.pdf", "page": 2}
    ],
    ids=["doc_001", "doc_002", "doc_003"]
)

# Consultar
resultados = coleccion.query(
    query_texts=["¿Cuántos días de vacaciones tengo?"],
    n_results=2,
    include=["documents", "metadatas", "distances"]
)

for doc, meta, dist in zip(
    resultados["documents"][0],
    resultados["metadatas"][0],
    resultados["distances"][0]
):
    print(f"[{dist:.4f}] {doc} (fuente: {meta['source']})")
```

---

## 7. Pipeline de recuperación

### 7.1 Similarity search: top-k

La recuperación básica consiste en encontrar los k chunks cuyo vector es más similar al vector de la consulta. El valor de k es un hiperparámetro: valores bajos (k=3) reducen el ruido pero pueden perder información relevante; valores altos (k=10) aumentan el recall pero pueden saturar el contexto y añadir ruido.

### 7.2 Filtrado por metadata

Las bases de datos vectoriales permiten combinar la búsqueda semántica con filtros sobre los metadatos. Esto es especialmente útil en aplicaciones empresariales donde los documentos pertenecen a distintos departamentos, fechas o categorías.

```python
resultados = coleccion.query(
    query_texts=["política de viajes"],
    n_results=3,
    where={"source": {"$contains": "finanzas"}}  # Solo documentos de finanzas
)
```

### 7.3 MMR: Maximal Marginal Relevance

Un problema frecuente en la recuperación top-k es la redundancia: si varios chunks tratan el mismo subtema, el contexto recuperado estará dominado por variaciones del mismo texto. MMR resuelve esto equilibrando relevancia y diversidad.

El algoritmo selecciona iterativamente chunks que son relevantes para la consulta pero diferentes entre sí. En cada paso, elige el chunk que maximiza: `λ · sim(chunk, consulta) - (1-λ) · max_sim(chunk, chunks_ya_seleccionados)`. El parámetro `λ` controla el balance entre relevancia y diversidad.

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=OpenAIEmbeddings()
)

retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.7}
)

docs = retriever.invoke("política de vacaciones y permisos")
```

### 7.4 Reranking con cross-encoder

Los modelos de embedding (bi-encoders) producen vectores de forma independiente para cada texto, lo que permite búsquedas eficientes pero sacrifica algo de precisión. Un cross-encoder evalúa el par (consulta, documento) de forma conjunta, generando una puntuación de relevancia más precisa.

El patrón habitual es: recuperar un conjunto amplio con el bi-encoder (top-20 o top-30) y luego rerankear con el cross-encoder para seleccionar los top-5 o top-10 finales.

**BGE-Reranker** (BAAI) y **Cohere Rerank** son las opciones más populares. BGE-Reranker es de código abierto y puede ejecutarse localmente; Cohere Rerank es un servicio API.

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")

consulta = "¿Cuál es el proceso de aprobación de gastos?"
candidatos = [doc.page_content for doc in docs_recuperados]

pares = [(consulta, doc) for doc in candidatos]
puntuaciones = reranker.predict(pares)

docs_rerankeados = sorted(
    zip(puntuaciones, docs_recuperados),
    key=lambda x: x[0],
    reverse=True
)

top_docs = [doc for _, doc in docs_rerankeados[:5]]
```

---

## 8. Augmentación y generación

### 8.1 Construcción del prompt con contexto recuperado

La calidad del prompt de augmentación es determinante para la calidad de la respuesta. El prompt debe:

1. Instruir claramente al modelo a responder basándose en el contexto proporcionado.
2. Indicar qué hacer cuando el contexto no contiene la información necesaria (evitar alucinaciones).
3. Solicitar la cita de fuentes cuando sea relevante.

```python
PROMPT_TEMPLATE = """Eres un asistente experto. Responde la pregunta del usuario
basándote ÚNICAMENTE en el siguiente contexto. Si el contexto no contiene
información suficiente para responder, indica explícitamente que no dispones
de esa información. No inventes datos.

CONTEXTO:
{context}

PREGUNTA:
{question}

RESPUESTA:"""
```

### 8.2 Gestión del tamaño del contexto

Insertar demasiados chunks en el prompt tiene costes reales: mayor latencia, mayor coste por token, y degradación de la calidad de la respuesta (el modelo pierde atención en las partes centrales del contexto). Las estrategias para gestionar el tamaño incluyen:

- Limitar el número de chunks recuperados (k ≤ 5 para modelos con contexto limitado).
- Truncar chunks individuales si superan un umbral.
- Usar el reranker para seleccionar solo los más relevantes.
- Comprimir el contexto con un LLM antes de insertarlo (Contextual Compression en LangChain).

### 8.3 Cita de fuentes

Un sistema RAG de producción debe citar las fuentes de las que extrae la información. Esto permite al usuario verificar la respuesta y aumenta la confianza en el sistema. La implementación más sencilla es incluir los metadatos de cada chunk junto al texto y solicitar al modelo que los cite.

```python
contexto_formateado = "\n\n".join([
    f"[Fuente: {doc.metadata['source']}, página {doc.metadata.get('page', 'N/A')}]\n{doc.page_content}"
    for doc in top_docs
])
```

### 8.4 Evaluación con RAGAS

RAGAS (Retrieval-Augmented Generation Assessment) es el framework de evaluación estándar para sistemas RAG. Proporciona métricas que evalúan tanto la calidad de la recuperación como la calidad de la generación.

**Faithfulness.** Mide en qué grado la respuesta generada está fundamentada en el contexto recuperado. Una respuesta con alta faithfulness no contiene afirmaciones que no puedan inferirse del contexto. Rango [0, 1].

**Answer Relevancy.** Mide en qué grado la respuesta es pertinente a la pregunta formulada. Una respuesta relevante responde directamente a lo que se pregunta, sin divagar. Rango [0, 1].

**Context Precision.** Mide qué proporción del contexto recuperado es realmente útil para generar la respuesta correcta. Un valor bajo indica que se están recuperando chunks irrelevantes (ruido en la recuperación). Rango [0, 1].

**Context Recall.** Mide en qué grado el contexto recuperado contiene toda la información necesaria para responder correctamente. Un valor bajo indica que la recuperación está perdiendo información relevante. Rango [0, 1].

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset

datos = Dataset.from_dict({
    "question": ["¿Cuántos días de vacaciones hay?"],
    "answer": ["Los empleados tienen derecho a 30 días de vacaciones anuales."],
    "contexts": [["La política de vacaciones permite 30 días al año."]],
    "ground_truth": ["30 días de vacaciones al año"]
})

resultado = evaluate(
    datos,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
)

print(resultado)
```

---

## 9. Frameworks RAG

### 9.1 LangChain

LangChain es el framework más extendido para construir aplicaciones LLM. Proporciona abstracciones de alto nivel que simplifican la construcción de pipelines RAG.

**Componentes clave:**

- **Document Loaders:** cargan documentos desde diversas fuentes (PDF, web, CSV, bases de datos).
- **Text Splitters:** implementan las estrategias de chunking.
- **Embeddings:** wrappers sobre modelos de embedding (OpenAI, HuggingFace, etc.).
- **Vector Stores:** integración con Chroma, Qdrant, Pinecone, pgvector, etc.
- **Retrievers:** abstracciones sobre la búsqueda (similarity, MMR, contextual compression).
- **Chains:** pipelines que encadenan componentes.

**Ejemplo RAG completo con LangChain:**

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA

# Carga y chunking
loader = PyPDFLoader("documentos/manual_empleado.pdf")
documentos = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documentos)

# Indexado
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    persist_directory="./chroma_db"
)

# Pipeline RAG
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
    return_source_documents=True
)

respuesta = qa_chain.invoke({"query": "¿Cuál es el horario de trabajo?"})
print(respuesta["result"])
print([doc.metadata["source"] for doc in respuesta["source_documents"]])
```

### 9.2 LlamaIndex

LlamaIndex (anteriormente GPT Index) es un framework alternativo con un enfoque más centrado en la gestión del conocimiento y la construcción de índices. Su API es más opinada que la de LangChain, lo que puede resultar en menos código boilerplate para casos de uso estándar.

**Componentes clave:**

- **Documents:** objetos que encapsulan el texto y sus metadatos.
- **Nodes:** la unidad de indexado (equivalente al chunk en LangChain).
- **Node Parsers:** estrategias de chunking.
- **Vector Store Index:** índice vectorial con integración para múltiples backends.
- **Query Engine:** motor de consulta con retrieval y síntesis integrados.
- **Response Synthesizer:** controla cómo el LLM sintetiza los nodos recuperados.

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

# Carga de documentos
documentos = SimpleDirectoryReader("documentos/").load_data()

# Chunking
parser = SentenceSplitter(chunk_size=512, chunk_overlap=64)
nodos = parser.get_nodes_from_documents(documentos)

# Indexado
indice = VectorStoreIndex(nodos)

# Query engine
query_engine = indice.as_query_engine(similarity_top_k=4)

respuesta = query_engine.query("¿Qué beneficios tienen los empleados?")
print(respuesta.response)
print(respuesta.source_nodes)
```

### 9.3 Comparativa de frameworks

| Criterio | LangChain | LlamaIndex |
|---|---|---|
| Ecosistema e integraciones | Muy amplio | Amplio, más focalizado |
| Curva de aprendizaje | Moderada-alta | Moderada |
| Flexibilidad | Muy alta | Alta |
| Casos RAG estándar | Verboso | Más conciso |
| Indexado avanzado | Requiere más código | Mejor soporte nativo |
| Comunidad y documentación | Muy activa | Activa |
| Agentes y herramientas | Excelente soporte | Buen soporte |

Para la mayoría de los proyectos RAG de producción, ambos son válidos. LangChain ofrece más flexibilidad y un ecosistema más amplio; LlamaIndex reduce el boilerplate para casos centrados en indexado y recuperación.

---

## 10. Actividades prácticas

### Actividad 1 · Construcción de un índice vectorial local

**Objetivo:** Implementar las fases de ingesta, chunking e indexado de un pipeline RAG.

**Descripción:** El estudiante descargará un conjunto de 5-10 documentos PDF sobre un tema de su elección (puede ser documentación técnica, artículos académicos o normativas). Usará LangChain para cargar los documentos, `RecursiveCharacterTextSplitter` para hacer chunking con distintos tamaños (256, 512, 1024 tokens), y Chroma para indexar los chunks con el modelo `BAAI/bge-m3` ejecutado localmente con sentence-transformers. Deberá enriquecer los metadatos de cada chunk con al menos cuatro campos y documentar el número de chunks generados con cada configuración.

**Entregable:** Notebook Jupyter con el código funcional y una reflexión escrita sobre el impacto del chunk size en el número de chunks y la coherencia semántica de cada fragmento.

### Actividad 2 · Pipeline RAG de extremo a extremo

**Objetivo:** Implementar un sistema RAG funcional que responda preguntas sobre el corpus indexado en la Actividad 1.

**Descripción:** Partiendo del índice creado en la Actividad 1, el estudiante implementará el pipeline completo de recuperación y generación. Deberá comparar dos configuraciones: similarity search con top-5 vs MMR con lambda=0.7, usando el mismo conjunto de 10 preguntas de prueba. Integrará el reranker `BAAI/bge-reranker-v2-m3` en una de las configuraciones y comparará la calidad subjetiva de las respuestas. El sistema debe mostrar las fuentes citadas en cada respuesta.

**Entregable:** Notebook con los dos pipelines implementados, tabla comparativa de respuestas para las 10 preguntas, y análisis cualitativo de las diferencias.

### Actividad 3 · Evaluación con RAGAS

**Objetivo:** Aplicar métricas objetivas de evaluación a un sistema RAG.

**Descripción:** El estudiante creará un dataset de evaluación de 20 pares (pregunta, respuesta_esperada) basado en el corpus de las actividades anteriores. Ejecutará el sistema RAG con dos configuraciones distintas (que puede elegir libremente: distintos modelos de embedding, distintos chunk sizes, con y sin reranker, etc.) y evaluará ambas con RAGAS midiendo las cuatro métricas principales: faithfulness, answer_relevancy, context_precision y context_recall. Documentará los hallazgos y justificará qué configuración elegiría para producción.

**Entregable:** Notebook con el dataset, las evaluaciones y un informe de 500 palabras con los resultados y conclusiones.

### Actividad 4 · RAG con LlamaIndex y múltiples fuentes

**Objetivo:** Explorar las capacidades de indexado avanzado de LlamaIndex y la integración de múltiples fuentes de conocimiento.

**Descripción:** El estudiante construirá un sistema RAG con LlamaIndex que combine dos fuentes heterogéneas: documentos PDF locales y páginas web (usando `SimpleWebPageReader`). Implementará un `RouterQueryEngine` que dirija las consultas al índice apropiado según la naturaleza de la pregunta. Comparará la arquitectura resultante con el pipeline equivalente en LangChain en términos de líneas de código, legibilidad y funcionalidad.

**Entregable:** Notebook funcional con el sistema dual-fuente, diagrama de la arquitectura implementada y comparativa reflexiva con LangChain.

---

## 11. Referencias

### Artículos y papers

- Gao, Y., et al. (2023). *Retrieval-Augmented Generation for Large Language Models: A Survey*. arXiv:2312.10997. Disponible en: https://arxiv.org/abs/2312.10997

- Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS 2020. Disponible en: https://arxiv.org/abs/2005.11401

- Es, S., et al. (2023). *RAGAS: Automated Evaluation of Retrieval Augmented Generation*. arXiv:2309.15217. Disponible en: https://arxiv.org/abs/2309.15217

- Muennighoff, N., et al. (2022). *MTEB: Massive Text Embedding Benchmark*. arXiv:2210.07316. Disponible en: https://arxiv.org/abs/2210.07316

- Chen, J., et al. (2024). *BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation*. arXiv:2402.03216. Disponible en: https://arxiv.org/abs/2402.03216

### Documentación oficial

- LangChain Documentation. *Retrieval*. Disponible en: https://python.langchain.com/docs/concepts/retrieval/

- LangChain Documentation. *Text Splitters*. Disponible en: https://python.langchain.com/docs/concepts/text_splitters/

- LlamaIndex Documentation. *Understanding RAG*. Disponible en: https://docs.llamaindex.ai/en/stable/understanding/rag/

- LlamaIndex Documentation. *Query Engines*. Disponible en: https://docs.llamaindex.ai/en/stable/module_guides/deploying/query_engine/

- Chroma Documentation. *Getting Started*. Disponible en: https://docs.trychroma.com/getting-started

- RAGAS Documentation. *Metrics*. Disponible en: https://docs.ragas.io/en/stable/concepts/metrics/

- sentence-transformers Documentation. *Pretrained Models*. Disponible en: https://www.sbert.net/docs/pretrained_models.html

### Recursos complementarios

- MTEB Leaderboard (Hugging Face). Disponible en: https://huggingface.co/spaces/mteb/leaderboard

- Qdrant Documentation. *Vector Search Basics*. Disponible en: https://qdrant.tech/documentation/concepts/

- OpenAI Documentation. *Embeddings*. Disponible en: https://platform.openai.com/docs/guides/embeddings

- Pinecone Learning Center. *What is a Vector Database?* Disponible en: https://www.pinecone.io/learn/vector-database/

- pgvector GitHub Repository. Disponible en: https://github.com/pgvector/pgvector
