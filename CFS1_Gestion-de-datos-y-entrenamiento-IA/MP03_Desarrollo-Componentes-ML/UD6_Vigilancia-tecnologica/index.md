---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD6 · Vigilancia tecnológica | MP03 · Desarrollo de componentes para sistemas de ML'
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
section.lead h1 { font-size: 2em; text-align: center; margin-top: 80px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
pre { background: #1e293b; color: #e2e8f0; padding: 16px; border-radius: 8px; font-size: 0.8em; }
</style>

<!-- _class: lead -->

# UD6 · Vigilancia tecnológica

**MP03 · Desarrollo de componentes para sistemas de ML**

CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Identificar y usar las fuentes técnicas de referencia en IA/ML (arXiv, Papers with Code, HuggingFace Hub, blogs, conferencias)
- Evaluar la aplicabilidad de una nueva herramienta o arquitectura mediante una prueba de concepto comparada
- Monitorizar las tendencias del sector a través de los anuncios de empresas de referencia
- Mantenerse actualizado sobre la normativa y regulación aplicable al desarrollo de sistemas de ML
- Transferir los hallazgos de la vigilancia al equipo mediante informes o presentaciones estructuradas

---

## Qué es la vigilancia tecnológica

La **vigilancia tecnológica** (también llamada *technology watch* o *tech intelligence*) es el proceso sistemático de monitorizar, analizar y transferir información sobre avances tecnológicos relevantes para la actividad profesional.

**Por qué es crítica en IA/ML:**

- El campo avanza a una velocidad sin precedentes: los mejores modelos de hace 18 meses ya son obsoletos
- Las herramientas que se estaban adoptando pueden quedar reemplazadas por alternativas superiores en meses
- La normativa (AI Act, RGPD) evoluciona y tiene implicaciones directas en el diseño de sistemas
- Los competidores que no realizan vigilancia tecnológica acumulan deuda técnica y de cumplimiento

> La vigilancia tecnológica no es "estar al día por curiosidad": es una actividad profesional con metodología, fuentes y entregables definidos.

---

## Fuentes técnicas — arXiv

**arXiv** (`arxiv.org`) es el repositorio de preprints de referencia para investigación en ML e IA. La mayoría de los artículos relevantes se publican aquí antes de aparecer en las actas de conferencias.

**Cómo usar arXiv de forma eficiente:**

| Estrategia | Comando/URL | Para qué sirve |
|---|---|---|
| Feed de categorías | `arxiv.org/list/cs.LG/recent` | Novedades diarias en Machine Learning |
| Búsqueda semántica | `arxiv.org/search/?searchtype=all&query=...` | Buscar por concepto, no solo por título |
| Papers de esta semana | `arxiv-sanity.com` o `huggingface.co/papers` | Filtrado por relevancia comunitaria |
| Alertas de autores | Google Scholar + email | Seguir investigadores de referencia |
| RSS del área | `export.arxiv.org/rss/cs.LG` | Integrar en lector de feeds |

**Secciones de arXiv relevantes para ML:**
- `cs.LG` — Machine Learning
- `cs.AI` — Artificial Intelligence
- `cs.CV` — Computer Vision
- `cs.CL` — Computation and Language (NLP)
- `stat.ML` — Statistics / Machine Learning

---

## Fuentes técnicas — Papers with Code

**Papers with Code** (`paperswithcode.com`) enlaza los artículos de investigación con el código que los implementa y con los benchmarks donde se evalúan. Es la fuente principal para evaluar el estado del arte en tareas concretas.

**Funcionalidades clave:**

```
paperswithcode.com/sota          → Rankings de modelos por tarea y dataset
paperswithcode.com/methods       → Catálogo de técnicas con referencias
paperswithcode.com/datasets      → Datasets públicos con estadísticas
paperswithcode.com/task/text-classification  → Estado del arte en clasificación de texto
```

**Flujo de uso para vigilancia de una tarea concreta:**

```
1. Buscar la tarea en /sota
2. Identificar los 3-5 mejores modelos del ranking
3. Leer los artículos vinculados (resumen de 15-20 min cada uno)
4. Verificar disponibilidad de código y licencia
5. Evaluar si el modelo/técnica es aplicable al proyecto actual
```

---

## Fuentes técnicas — HuggingFace Hub

**HuggingFace Hub** (`huggingface.co`) es el repositorio central de modelos, datasets y espacios de demostración de la comunidad ML. Con más de 500 000 modelos públicos, es el catálogo de referencia para integrar modelos preentrenados.

**Recursos disponibles:**

| Sección | URL | Contenido |
|---|---|---|
| Modelos | `huggingface.co/models` | Modelos preentrenados con filtros por tarea, idioma, framework |
| Datasets | `huggingface.co/datasets` | Datasets públicos con previsualizador integrado |
| Spaces | `huggingface.co/spaces` | Demos interactivas de modelos |
| Leaderboards | `huggingface.co/open-llm-leaderboard` | Rankings de LLMs en benchmarks estandarizados |
| Blog | `huggingface.co/blog` | Artículos técnicos del equipo de HuggingFace |

```python
# Explorar modelos disponibles para una tarea mediante la API
from huggingface_hub import list_models

modelos = list(list_models(
    task="text-classification",
    language="es",
    sort="downloads",
    limit=10
))
for m in modelos:
    print(f"{m.modelId:50s} | {m.downloads:>10,} descargas")
```

---

## Fuentes técnicas — Conferencias de referencia

Las conferencias de ML publican los artículos más rigurosos y revisados. Conocer el calendario y los temas de cada una permite anticipar las tendencias del sector.

| Conferencia | Área | Periodo habitual | URL |
|---|---|---|---|
| **NeurIPS** | ML/IA general, teoría | Diciembre | neurips.cc |
| **ICML** | Machine Learning | Julio | icml.cc |
| **ICLR** | Representaciones, deep learning | Abril-Mayo | iclr.cc |
| **CVPR** | Visión por computador | Junio | cvpr.thecvf.com |
| **ACL / EMNLP** | NLP, procesamiento del lenguaje | Julio / Diciembre | aclanthology.org |
| **KDD** | Minería de datos, aplicaciones | Agosto | kdd.org |
| **AAAI** | IA general | Febrero | aaai.org |

> Los *proceedings* de NeurIPS, ICML e ICLR están disponibles gratuitamente en línea. Los artículos de NeurIPS de un año son un mapa fiable de las tendencias del año siguiente.

---

## Fuentes técnicas — Blogs técnicos de referencia

Los blogs técnicos de empresas de investigación publican resultados y tutoriales antes de que se formalicen en artículos. Son la fuente más inmediata de información sobre nuevas herramientas y enfoques.

| Blog / Fuente | Organización | Tipo de contenido |
|---|---|---|
| `openai.com/research` | OpenAI | Papers propios, GPT, DALL-E, Codex |
| `ai.meta.com/research` | Meta AI | LLaMA, Segment Anything, Dino |
| `deepmind.google/research` | Google DeepMind | AlphaFold, Gemini, RL |
| `mistral.ai/news` | Mistral AI | LLMs eficientes de código abierto |
| `blog.langchain.dev` | LangChain | Frameworks para aplicaciones LLM |
| `pytorch.org/blog` | PyTorch / Meta | Framework, nuevas funcionalidades |
| `huggingface.co/blog` | HuggingFace | Transformers, fine-tuning, datasets |
| `the-decoder.com` | The Decoder | Noticias y análisis de IA (en inglés) |

---

## Evaluación de herramientas — Prueba de concepto (PoC)

Antes de adoptar una nueva herramienta o arquitectura en un proyecto real, se realiza una **prueba de concepto** (PoC): una implementación mínima con datos reales o representativos que permite comparar la nueva opción con la solución actual.

**Criterios de evaluación en una PoC de componente ML:**

| Criterio | Pregunta | Métrica |
|---|---|---|
| **Rendimiento** | ¿Mejora las métricas? | F1, AUC, RMSE... en el mismo dataset de test |
| **Eficiencia** | ¿Es más rápido o usa menos memoria? | Tiempo de entrenamiento, inferencia en ms, RAM/VRAM |
| **Complejidad de integración** | ¿Cuánto esfuerzo requiere adoptar? | Días de integración estimados |
| **Mantenibilidad** | ¿Tiene comunidad activa y documentación? | Issues en GitHub, frecuencia de commits |
| **Licencia** | ¿Es compatible con el uso previsto? | MIT, Apache 2.0, GPL, comercial... |
| **Reproducibilidad** | ¿Los resultados son deterministas? | Semilla fija, mismo entorno → mismo resultado |

---

## Prueba de concepto — Ejemplo comparado

**Escenario:** Evaluar si `polars` mejora el rendimiento del pipeline de procesamiento de datos respecto a `pandas`.

```python
import time
import pandas as pd
import polars as pl

FICHERO = "datos_credito_500k.csv"

# Benchmarking con pandas
inicio = time.perf_counter()
df_pd = pd.read_csv(FICHERO)
df_pd = df_pd[df_pd["edad"] > 18]
df_pd = df_pd.groupby("provincia")["ingreso_mensual"].mean()
tiempo_pandas = time.perf_counter() - inicio

# Benchmarking con polars
inicio = time.perf_counter()
df_pl = (pl.scan_csv(FICHERO)
    .filter(pl.col("edad") > 18)
    .group_by("provincia")
    .agg(pl.col("ingreso_mensual").mean())
    .collect())
tiempo_polars = time.perf_counter() - inicio

print(f"pandas:  {tiempo_pandas:.2f}s  |  polars: {tiempo_polars:.2f}s")
print(f"Mejora de velocidad: {tiempo_pandas / tiempo_polars:.1f}x")
```

---

## Tendencias del sector — Anuncios de empresas de referencia

Las empresas de referencia en IA publican anuncios y lanzamientos que marcan la dirección del sector. Monitorizar estos canales permite anticipar cambios en el ecosistema de herramientas.

**Canales de seguimiento por empresa:**

| Empresa | Canal principal | Qué monitorizar |
|---|---|---|
| **Anthropic** | `anthropic.com/news` | Claude, API, seguridad en IA |
| **OpenAI** | `openai.com/news` | GPT, DALL-E, Codex, políticas de uso |
| **Google DeepMind** | `deepmind.google` | Gemini, AlphaFold, investigación teórica |
| **Meta AI** | `ai.meta.com` | LLaMA, modelos de código abierto |
| **Mistral AI** | `mistral.ai/news` | LLMs eficientes de código abierto para Europa |
| **NVIDIA** | `developer.nvidia.com/blog` | CUDA, TensorRT, hardware de inferencia |

**Señales de cambio relevante que justifican una PoC:**
- Nuevo modelo que supera el estado del arte en tu tarea en +5 % o más
- Herramienta que reduce el coste de inferencia en un 50 %
- Cambio de licencia de una dependencia clave
- Nuevo requisito regulatorio con fecha de cumplimiento

---

## Monitorización de normativa y regulación

La regulación de la IA evoluciona rápidamente. El incumplimiento tiene consecuencias legales y económicas directas para los proyectos.

**Normativa de referencia para el desarrollo de sistemas de ML en la UE:**

| Norma | Ámbito | Estado (2026) | Impacto en el desarrollo |
|---|---|---|---|
| **AI Act (UE 2024/1689)** | Sistemas de IA por nivel de riesgo | Aplicación escalonada 2024-2027 | Clasificación de riesgo, documentación, supervisión humana |
| **RGPD (2016/679)** | Datos personales | Vigente | Minimización de datos, privacidad por diseño |
| **Directiva NIS2** | Ciberseguridad | Transposición completada 2024 | Seguridad de los sistemas de IA en infraestructuras críticas |
| **ISO/IEC 42001:2023** | Sistemas de gestión de IA | Norma voluntaria | Buenas prácticas, auditoría, certificación |
| **ISO/IEC 23894:2023** | Gestión del riesgo en IA | Norma voluntaria | Marco de evaluación de riesgos |

**Fuentes para monitorizar la regulación:**
- `digital-strategy.ec.europa.eu` — Política digital de la UE
- `boe.es` — Transposición española de normativa europea
- `aepd.es` — Guías de la Agencia Española de Protección de Datos

---

## Transferencia de hallazgos — Formatos de informe

Los hallazgos de la vigilancia tecnológica solo generan valor cuando se transfieren al equipo de forma estructurada y accionable.

**Formatos según el tipo de hallazgo:**

| Tipo de hallazgo | Formato recomendado | Longitud |
|---|---|---|
| Nuevo paper relevante | Ficha de lectura (resumen + aplicabilidad) | 1 página |
| Nueva herramienta evaluada | Informe de PoC (metodología + resultados + recomendación) | 2-3 páginas |
| Cambio regulatorio | Alerta de cumplimiento (qué cambia + qué hay que hacer) | 1 página |
| Tendencia del sector | Presentación de equipo (contexto + impacto + propuestas) | 10-15 diapositivas |
| Resumen periódico | Newsletter interna mensual | 300-500 palabras |

---

## Transferencia de hallazgos — Plantilla de ficha de lectura

```markdown
# Ficha de lectura: [Título del paper]

**Fuente:** arXiv:2406.XXXXX  |  **Fecha:** 2026-06-15  |  **Autor/a:** Nombre Apellido

## En una frase
[Qué propone el paper en una sola oración]

## Problema que resuelve
[Limitación de los métodos actuales que aborda]

## Método propuesto
[Descripción técnica en 3-5 puntos concretos]

## Resultados clave
[Métricas comparadas con el estado del arte anterior]

## Aplicabilidad a nuestros proyectos
[Sí / No / Condicional — y por qué]

## Esfuerzo de adopción estimado
[Horas/días de integración, dependencias nuevas, cambios en pipeline]

## Recomendación
[Adoptar / Monitorizar / Descartar — con justificación]
```

---

## Transferencia de hallazgos — Informe de PoC

```markdown
# Informe de prueba de concepto: [Herramienta / Técnica]

**Evaluador:** [nombre]  |  **Fecha:** 2026-06-23  |  **Versión evaluada:** X.Y.Z

## Objetivo de la evaluación
[Qué se quería comparar y por qué]

## Metodología
[Dataset utilizado, métricas medidas, entorno de prueba, semilla]

## Resultados comparados

| Criterio        | Solución actual | Candidata | Diferencia |
|-----------------|-----------------|-----------|------------|
| F1 en test      | 0.820           | 0.841     | +2.6 %     |
| Tiempo (s/epoch)| 142             | 98        | -31 %      |
| Memoria (GB)    | 4.2             | 3.1       | -26 %      |
| Complejidad     | Media           | Baja      | Mejor      |
| Licencia        | MIT             | Apache 2  | Compatible |

## Recomendación
[Adoptar / Monitorizar / Descartar — con argumentación]

## Plan de adopción (si se recomienda)
[Pasos, plazos, responsables]
```

---

## Actividad práctica — UD6

**Contexto:** Tu equipo usa actualmente `scikit-learn` para clasificación tabular y `transformers` para clasificación de texto. Han aparecido dos novedades: la librería `river` para aprendizaje en flujo (*online learning*) y la arquitectura `ModernBERT` para texto.

**Tareas:**

1. Localiza en Papers with Code el estado del arte actual en clasificación de texto en español. Identifica los 3 mejores modelos e indica su F1 en el benchmark de referencia
2. Busca en HuggingFace Hub los 5 modelos más descargados para `text-classification` en español. Para cada uno, anota la licencia y el número de parámetros
3. Diseña una PoC para evaluar `ModernBERT` frente al modelo actual. Define los criterios de evaluación, las métricas y el protocolo de benchmarking
4. Redacta una ficha de lectura para uno de los papers identificados en la tarea 1, siguiendo la plantilla de la unidad
5. Elabora un informe de vigilancia mensual en formato newsletter interna (300-400 palabras) con los 3 hallazgos más relevantes del mes para el equipo

---

## Puntos clave — UD6

- La vigilancia tecnológica es una actividad profesional sistemática, no una lectura casual: requiere fuentes definidas, metodología y entregables periódicos
- arXiv, Papers with Code y HuggingFace Hub son las tres fuentes técnicas imprescindibles; las conferencias NeurIPS, ICML e ICLR marcan el estado del arte anual
- Una prueba de concepto (PoC) es la única forma rigurosa de evaluar si una novedad mejora el sistema actual: los benchmarks de los papers no se trasladan automáticamente al contexto propio
- El AI Act (UE 2024/1689) clasifica los sistemas de IA por nivel de riesgo y establece obligaciones de documentación y supervisión que afectan directamente al ciclo de desarrollo
- Los hallazgos de vigilancia solo generan valor cuando se transfieren al equipo: la ficha de lectura y el informe de PoC son los formatos mínimos de transferencia
- La frecuencia de revisión de fuentes técnicas recomendada es semanal para arXiv y HuggingFace, mensual para blogs de empresas, y trimestral para normativa

---

## Criterios de evaluación — UD6

| Criterio | Indicador de logro |
|---|---|
| Monitoriza fuentes de referencia | Consulta arXiv, Papers with Code y HuggingFace Hub con regularidad y conoce las conferencias principales del sector |
| Evalúa la aplicabilidad de novedades | Diseña y ejecuta pruebas de concepto con criterios de evaluación comparados respecto a la solución actual |
| Identifica tendencias del sector | Sigue los anuncios de empresas de referencia e identifica los cambios con mayor impacto en los proyectos propios |
| Monitoriza la normativa | Conoce el estado de aplicación del AI Act, el RGPD y las normas ISO relevantes para el desarrollo de sistemas de ML |
| Comparte hallazgos con el equipo | Elabora fichas de lectura, informes de PoC o newsletters internas siguiendo los formatos estructurados de la unidad |

---

<!-- _class: lead -->

[← Volver a MP03](../)


---

<!-- nav-slide -->

## Navegación

[← UD5 · Protocolización y documentaci…](../UD5_Protocolizacion-documentacion/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD7 · Gestión integral: seguridad,… →](../UD7_Gestion-seguridad-sostenibilidad/)
