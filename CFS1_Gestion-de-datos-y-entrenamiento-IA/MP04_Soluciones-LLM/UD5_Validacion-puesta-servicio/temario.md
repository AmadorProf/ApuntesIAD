# UD5 · Validación y puesta en servicio de soluciones LLM

---

## 1. Introducción

La evaluación de modelos de lenguaje de gran escala (LLM) representa uno de los retos metodológicos más complejos dentro de la ingeniería de inteligencia artificial moderna. A diferencia de los clasificadores tradicionales —donde existe una etiqueta correcta para cada entrada y métricas bien establecidas como la accuracy, el F1-score o el AUC-ROC permiten cuantificar el rendimiento de forma objetiva—, los LLM producen texto libre cuya calidad es inherentemente subjetiva, contextual y multidimensional.

En un clasificador binario, evaluar el modelo es un problema matemático: se compara la salida del modelo con la etiqueta ground truth y se calcula el porcentaje de aciertos. En un LLM, ¿qué significa que una respuesta sea "correcta"? Una pregunta sobre el efecto del calor en los metales puede tener decenas de respuestas válidas, todas formuladas de manera distinta, con distintos niveles de detalle y énfasis. El concepto de ground truth único no existe o, en el mejor de los casos, es una aproximación.

Este problema se agrava cuando el LLM se integra en sistemas más complejos, como los sistemas de recuperación aumentada (RAG), los agentes autónomos o los chatbots de atención al cliente. En estos contextos, la calidad del output depende no solo de las capacidades del modelo base, sino también de la calidad de los documentos recuperados, del diseño del prompt, de la cadena de procesamiento y de los parámetros de generación. Evaluar el sistema implica evaluar cada uno de estos componentes por separado y también su comportamiento conjunto.

Esta unidad didáctica aborda de forma sistemática los métodos, herramientas y marcos conceptuales disponibles para evaluar LLMs y sistemas basados en LLMs. Se presentan los principales frameworks de evaluación automatizada, la metodología LLM-as-Judge, la evaluación de factualidad y alucinaciones, la evaluación de seguridad y sesgo, el diseño de experimentos A/B para chatbots, y los patrones de CI/CD que permiten integrar la evaluación continua en pipelines de despliegue profesionales.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Comprender por qué la evaluación de LLMs requiere enfoques distintos a los empleados en modelos de aprendizaje automático supervisado clásico.
- Configurar y ejecutar evaluaciones con frameworks como RAGAS, OpenAI Evals, LangSmith y DeepEval.
- Diseñar prompts de evaluación para implementar la metodología LLM-as-Judge, identificando y mitigando los sesgos más comunes del modelo evaluador.
- Aplicar métricas de factualidad y detectar alucinaciones usando herramientas como FactScore y benchmarks establecidos como TruthfulQA.
- Realizar evaluaciones de seguridad y sesgo mediante técnicas de red teaming y herramientas especializadas.
- Diseñar y analizar experimentos A/B para comparar versiones de chatbots en entornos de producción.
- Integrar evaluaciones automatizadas en pipelines de CI/CD con GitHub Actions y estrategias de despliegue como canary deployments.
- Establecer sistemas de monitorización continua en producción que alerten sobre degradaciones de calidad, aumentos de latencia o desviaciones en el coste.

---

## 3. Frameworks de evaluación de LLMs

### 3.1 RAGAS para sistemas RAG

RAGAS (Retrieval Augmented Generation Assessment) es un framework diseñado específicamente para evaluar sistemas de generación aumentada por recuperación. Su principal aportación es descomponer la calidad de un sistema RAG en métricas independientes que evalúan por separado el componente de recuperación y el componente de generación.

Las cuatro métricas fundamentales de RAGAS son:

**Faithfulness** mide si la respuesta generada es factualmente consistente con los fragmentos de contexto recuperados. Una respuesta que introduce información no presente en los documentos de contexto obtiene una puntuación baja en faithfulness, independientemente de si esa información es verdadera o falsa en términos absolutos. Se calcula dividiendo el número de afirmaciones de la respuesta que pueden deducirse del contexto entre el total de afirmaciones de la respuesta.

**Answer Relevancy** evalúa si la respuesta generada es pertinente para la pregunta formulada. Una respuesta completa desde el punto de vista factual pero que no responde realmente a lo que se preguntaba obtiene una puntuación baja. Esta métrica penaliza tanto las respuestas incompletas como las que incluyen información irrelevante.

**Context Precision** mide qué proporción del contexto recuperado es realmente relevante para responder la pregunta. Un sistema que recupera muchos fragmentos pero la mayoría son irrelevantes tendrá una context precision baja. Esta métrica evalúa la precisión del componente de recuperación.

**Context Recall** evalúa si el contexto recuperado contiene toda la información necesaria para construir la respuesta de referencia. Un sistema que pierde fragmentos importantes tendrá un context recall bajo. Complementa a context precision al evaluar la exhaustividad de la recuperación.

La implementación de RAGAS en Python requiere preparar un dataset de evaluación con la estructura adecuada. Cada ejemplo del dataset debe contener la pregunta (question), la respuesta generada por el sistema (answer), los fragmentos de contexto recuperados (contexts) y, cuando está disponible, la respuesta de referencia (ground_truth).

```python
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

data = {
    "question": ["¿Cuál es la capital de Francia?"],
    "answer": ["La capital de Francia es París."],
    "contexts": [["París es la capital y ciudad más poblada de Francia."]],
    "ground_truth": ["París"]
}

dataset = Dataset.from_dict(data)
results = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
print(results)
```

### 3.2 OpenAI Evals

OpenAI Evals es un framework de código abierto publicado por OpenAI para evaluar modelos de lenguaje de forma sistemática y reproducible. Su arquitectura se basa en la definición de "evals" mediante archivos de configuración YAML que especifican el tipo de evaluación, el dataset y los criterios de calidad.

La estructura básica de un eval incluye: la clase de evaluación (match, includes, fuzzy_match para tareas con respuesta cerrada; model_graded para evaluación abierta), el dataset de ejemplos y los parámetros de configuración del modelo evaluado.

Una de las contribuciones más relevantes de OpenAI Evals es la posibilidad de crear evals personalizados adaptados a las necesidades específicas de cada caso de uso. Esto permite que equipos de ingeniería definan sus propios criterios de calidad en lugar de depender únicamente de benchmarks genéricos.

### 3.3 LangSmith para trazabilidad y evaluación continua

LangSmith es la plataforma de observabilidad y evaluación de LangChain. A diferencia de los frameworks de evaluación por lotes, LangSmith está diseñado para el seguimiento en tiempo real de las ejecuciones de cadenas y agentes, facilitando la depuración, el análisis de fallos y la evaluación continua en producción.

Sus funcionalidades principales incluyen: trazas completas de cada ejecución (inputs, outputs, tiempos de latencia, tokens consumidos), anotación humana de respuestas, creación de datasets de evaluación a partir de trazas de producción, y ejecución de evaluaciones automáticas sobre esos datasets.

LangSmith implementa el concepto de "evaluadores en línea" (online evaluators) que analizan cada traza en el momento de la ejecución y aplican métricas configuradas por el usuario, permitiendo detectar degradaciones de calidad sin necesidad de esperar a un ciclo de evaluación offline.

### 3.4 DeepEval

DeepEval es un framework de evaluación de LLMs de código abierto que adopta una filosofía similar a los frameworks de testing unitario (como pytest) aplicada a la evaluación de modelos de lenguaje. Su propuesta de valor es hacer que las evaluaciones de LLMs sean tratadas como tests de software: reproducibles, automatizables e integrables en pipelines de CI/CD.

Los conceptos centrales de DeepEval son: los test cases (que encapsulan input, output y contexto opcional), las metrics (implementaciones de métricas como hallucination, answer relevancy, faithfulness, summarization, etc.) y las aserciones (que determinan si un test case pasa o falla según el valor de las métricas).

```python
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.metrics import HallucinationMetric

test_case = LLMTestCase(
    input="¿Cuáles son los síntomas del COVID-19?",
    actual_output="Los síntomas incluyen fiebre, tos y fatiga.",
    context=["La OMS reporta que los síntomas comunes son fiebre, tos seca y cansancio."]
)

metric = HallucinationMetric(threshold=0.5)
evaluate([test_case], [metric])
```

---

## 4. LLM-as-Judge

### 4.1 El paradigma de la evaluación por LLM

La metodología LLM-as-Judge consiste en utilizar un modelo de lenguaje de alta capacidad para evaluar los outputs producidos por otro LLM. Esta aproximación surge como respuesta a las limitaciones de las métricas automáticas tradicionales (BLEU, ROUGE) que correlacionan mal con el juicio humano en tareas de generación abierta, y al alto coste y baja escalabilidad de la evaluación humana.

El principio fundamental es que un LLM suficientemente capaz puede emitir juicios de calidad sobre texto que se aproximan a los que emitiría un evaluador humano, siguiendo criterios definidos en el prompt de evaluación. El modelo evaluador recibe como input la pregunta original, la respuesta a evaluar, y opcionalmente una respuesta de referencia, y produce una puntuación y una justificación textual.

### 4.2 Diseño de prompts de evaluación

El diseño del prompt es el factor más crítico para la calidad de un sistema LLM-as-Judge. Un prompt de evaluación efectivo debe incluir:

**Criterios claros y operacionalizables.** En lugar de pedir que evalúe la "calidad" de una respuesta (término ambiguo), el prompt debe especificar qué dimensiones concretas se evalúan: corrección factual, completitud, claridad, concisión, relevancia para la pregunta.

**Escala de puntuación bien definida.** La escala más común es de 1 a 5, donde cada nivel tiene una descripción precisa de qué tipo de respuesta le corresponde. Una escala sin anclas descriptivas introduce variabilidad arbitraria en las puntuaciones.

**Ejemplos calibrados.** Incluir uno o dos ejemplos con su puntuación y justificación (few-shot) reduce significativamente la varianza de las evaluaciones y ayuda al modelo a interpretar correctamente los criterios.

**Instrucción de razonamiento previo.** Pedir al modelo que explique su razonamiento antes de emitir la puntuación final (chain-of-thought) mejora la consistencia y facilita la auditoría humana de las evaluaciones.

Un template típico de prompt de evaluación incluye el enunciado del rol del evaluador, los criterios de evaluación numerados, la escala de puntuación con descripciones, el texto a evaluar y la instrucción de formato de salida.

### 4.3 G-Eval

G-Eval (Liu et al., 2023) es un framework de evaluación basado en LLM-as-Judge que introduce dos innovaciones metodológicas relevantes. En primer lugar, el proceso de generación automática de los pasos de evaluación: dado un criterio de evaluación en lenguaje natural, G-Eval utiliza el propio LLM para generar una cadena de pasos de razonamiento que operacionalizan ese criterio. En segundo lugar, el uso de la distribución de probabilidad sobre los tokens de la puntuación para calcular una puntuación continua ponderada, en lugar de tomar únicamente el token más probable.

G-Eval ha demostrado correlaciones más altas con el juicio humano que métricas automáticas clásicas en tareas de resumen y diálogo, consolidando el paradigma LLM-as-Judge como el estado del arte en evaluación de generación abierta.

### 4.4 Sesgos del modelo evaluador

El uso de LLMs como evaluadores introduce sesgos sistemáticos que deben conocerse y mitigarse:

**Sesgo de posición.** Cuando se presenta al LLM evaluador dos respuestas para comparar, tiende a favorecer la que aparece en primera posición. Mitigación: evaluar siempre en ambos órdenes y promediar.

**Sesgo de longitud.** Los LLMs tienden a puntuar más alto las respuestas más largas, independientemente de su calidad. Mitigación: incluir en el prompt una instrucción explícita de que la longitud no es un criterio de calidad, y penalizar la verbosidad innecesaria.

**Sesgo de auto-preferencia.** Cuando el modelo evaluador es el mismo que el modelo evaluado (o de la misma familia), tiende a favorecer sus propios outputs sobre los de modelos competidores. Mitigación: usar un modelo evaluador diferente al modelo evaluado, o combinar múltiples evaluadores.

**Sesgo de familiaridad estilística.** El modelo evaluador puede favorecer estilos de escritura similares a los de sus datos de entrenamiento. Mitigación: diversificar los modelos evaluadores y calibrar con anotaciones humanas.

### 4.5 Validación humana para calibrar el juez

Ningún sistema LLM-as-Judge debe desplegarse sin un proceso de validación con anotadores humanos. La validación consiste en comparar las puntuaciones del LLM evaluador con puntuaciones humanas sobre una muestra representativa de ejemplos. Las métricas de acuerdo más utilizadas son el coeficiente de correlación de Spearman (para ordinales) y el acuerdo inter-anotador de Cohen's Kappa.

Un coeficiente de correlación de Spearman superior a 0.7 entre el LLM evaluador y los anotadores humanos se considera generalmente aceptable para uso en producción. Por debajo de ese umbral, el prompt de evaluación debe revisarse o el modelo evaluador debe cambiarse.

---

## 5. Evaluación de factualidad y alucinaciones

### 5.1 El problema de las alucinaciones

Las alucinaciones son uno de los problemas más críticos de los LLMs en aplicaciones de producción. Se define como alucinación cualquier afirmación generada por el modelo que no está respaldada por los datos de entrenamiento, los documentos de contexto o el conocimiento factual verificable. Las alucinaciones pueden ser de dos tipos: intrínsecas (contradicen el contexto proporcionado) o extrínsecas (introducen información no presente en el contexto pero no necesariamente incorrecta en términos absolutos).

### 5.2 FactScore

FactScore (Min et al., 2023) es un framework de evaluación de factualidad que opera mediante la descomposición de la respuesta generada en unidades atómicas de información (claims) y la verificación independiente de cada claim contra una fuente de conocimiento de referencia.

El proceso tiene tres etapas. Primero, el texto a evaluar se descompone en claims atómicos mediante un LLM que extrae cada afirmación factual discreta. Segundo, cada claim se verifica de forma independiente consultando una fuente de referencia (Wikipedia, documentos internos, bases de conocimiento). Tercero, el FactScore se calcula como la proporción de claims verificados como correctos sobre el total de claims.

Esta descomposición en claims atómicos tiene una ventaja clave sobre métricas holísticas: permite localizar con precisión qué afirmaciones específicas de la respuesta son incorrectas, facilitando el diagnóstico y la mejora del sistema.

### 5.3 FEVER para fact-checking

FEVER (Fact Extraction and VERification) es un benchmark y un framework para la verificación automática de afirmaciones factuales. A diferencia de FactScore, que se centra en la evaluación de outputs de LLMs, FEVER fue diseñado originalmente como benchmark para sistemas de fact-checking, pero sus metodologías son directamente aplicables a la evaluación de alucinaciones en LLMs.

El sistema FEVER clasifica cada afirmación en tres categorías: SUPPORTS (la afirmación está respaldada por la evidencia), REFUTES (la afirmación contradice la evidencia) o NOT ENOUGH INFO (no hay suficiente evidencia para decidir). Este esquema de tres clases es más informativo que una evaluación binaria verdadero/falso.

### 5.4 TruthfulQA

TruthfulQA (Lin et al., 2022) es un benchmark diseñado para medir la tendencia de los LLMs a generar respuestas verídicas en lugar de respuestas que parecen plausibles pero son falsas. El benchmark consta de 817 preguntas distribuidas en 38 categorías temáticas, diseñadas específicamente para explotar las creencias erróneas comunes que los LLMs adquieren durante el entrenamiento.

Las preguntas de TruthfulQA incluyen mitos populares, afirmaciones pseudocientíficas, malentendidos históricos y preguntas de truco que suelen responderse de forma incorrecta siguiendo patrones estadísticos del lenguaje. Un modelo que simplemente replica los patrones más frecuentes de su corpus de entrenamiento fallará en estas preguntas.

TruthfulQA evalúa dos dimensiones: veracidad (truthfulness) y utilidad (informativeness), reconociendo que un modelo puede obtener una veracidad perfecta absteniéndose de responder, lo cual no es útil en producción.

### 5.5 Estrategias de reducción de alucinaciones

Las principales estrategias para reducir las alucinaciones en sistemas LLM de producción son:

**RAG (Retrieval Augmented Generation).** Anclar las respuestas del modelo a documentos de referencia recuperados en tiempo de inferencia reduce significativamente las alucinaciones extrínsecas, ya que el modelo tiene acceso a información verificable en el contexto.

**Chain-of-Thought (CoT).** Solicitar al modelo que razone paso a paso antes de emitir su respuesta final reduce las alucinaciones en tareas de razonamiento, al obligar al modelo a descomponer el problema en pasos verificables.

**Temperature=0.** Usar una temperatura de muestreo de 0 (o muy baja) hace que el modelo genere el token más probable en cada paso, reduciendo la variabilidad y las respuestas especulativas. Es especialmente útil en tareas con respuestas factualmente determinadas.

**Post-processing y verificación.** Implementar una etapa de verificación posterior a la generación, donde un segundo sistema (basado en reglas, en búsqueda o en otro LLM) contrasta las afirmaciones del output antes de enviarlo al usuario.

---

## 6. Evaluación de seguridad y sesgo

### 6.1 Red teaming de LLMs

El red teaming es una metodología originaria de la ciberseguridad adaptada a la evaluación de LLMs. Consiste en someter el modelo a ataques adversariales diseñados para provocar comportamientos no deseados: generación de contenido dañino, revelación de información privada, evasión de restricciones de seguridad o producción de respuestas sesgadas.

Los prompts adversariales más comunes incluyen los ataques de jailbreak, que intentan eludir las restricciones de seguridad del modelo mediante reformulaciones del prompt (roleplay attacks, prompt injection, instruction hijacking), y los ataques de extracción de datos, que intentan obtener información del corpus de entrenamiento o del system prompt.

Un proceso de red teaming riguroso combina evaluadores humanos especializados con herramientas automáticas. Los evaluadores humanos son más creativos y pueden explorar vectores de ataque novedosos, mientras que las herramientas automáticas permiten escalar la evaluación a miles de prompts adversariales.

### 6.2 MT-Bench para seguimiento de instrucciones

MT-Bench es un benchmark de 80 preguntas de alta calidad organizadas en 8 categorías (escritura, roleplay, extracción, razonamiento, matemáticas, código, conocimiento STEM y humanidades) diseñado para evaluar la capacidad de los modelos de seguir instrucciones complejas en conversaciones multi-turno.

La evaluación en MT-Bench se realiza mediante LLM-as-Judge (específicamente GPT-4 como evaluador), lo que la hace escalable y reproducible. MT-Bench ha demostrado una alta correlación con preferencias humanas y es actualmente uno de los benchmarks de referencia para comparar modelos de chat.

### 6.3 Evaluación de sesgo con WinoBias y BBQ

WinoBias es un benchmark diseñado para evaluar el sesgo de género en sistemas de resolución de correferencias. Contiene frases con pronombres que pueden referirse a diferentes sujetos, donde la corrección semántica entra en conflicto con los estereotipos de género asociados a ciertos roles profesionales (médico, enfermera, ingeniero, secretaria). Un modelo sesgado resolverá incorrectamente las correferencias siguiendo estereotipos en lugar de la semántica.

BBQ (Bias Benchmark for QA) extiende esta evaluación a sesgos más amplios, incluyendo edad, discapacidad, género, identidad de género, origen nacional, apariencia física, religión, nivel socioeconómico y orientación sexual. BBQ presenta preguntas en contextos ambiguos y no ambiguos para separar el sesgo intrínseco del modelo de la dependencia del contexto.

### 6.4 Evaluación de toxicidad con Perspective API

Perspective API, desarrollada por Jigsaw (Google), es una API que utiliza modelos de aprendizaje automático para detectar contenido tóxico en texto. Proporciona puntuaciones para atributos como toxicidad, toxicidad severa, obscenidad, amenazas, insultos e identidad de odio.

En el contexto de la evaluación de LLMs, Perspective API se utiliza para medir la tasa de generación de contenido tóxico bajo diferentes condiciones: prompts neutrales, prompts adversariales y prompts con contenido limítrofe. Una evaluación completa de seguridad debe incluir tanto la evaluación de respuestas a prompts directamente tóxicos como la evaluación de la tendencia del modelo a generar toxicidad de forma emergente en conversaciones que comienzan de forma neutral.

---

## 7. A/B testing para chatbots

### 7.1 Diseño del experimento

El A/B testing para chatbots aplica los principios del diseño de experimentos controlados al contexto específico de los modelos de lenguaje. El objetivo es comparar dos versiones del sistema (control A y tratamiento B) de forma que las diferencias observadas en las métricas puedan atribuirse causalmente a los cambios realizados y no a factores de confusión.

El diseño de un experimento de A/B testing para chatbots comienza con la formulación de una hipótesis clara y falsable: por ejemplo, "el cambio de modelo de GPT-3.5 a GPT-4 aumentará la tasa de resolución en primera respuesta en un 10%". Esta hipótesis debe estar vinculada a una métrica de negocio concreta.

Las métricas de negocio más relevantes para chatbots son: satisfacción del usuario (CSAT, Net Promoter Score, valoraciones explícitas), tasa de resolución (porcentaje de consultas resueltas sin escalado a agente humano), tiempo hasta la resolución (número de turnos o tiempo en segundos hasta que la consulta se cierra), tasa de abandono (porcentaje de conversaciones que el usuario abandona sin resolución) y coste por conversación (en términos de tokens consumidos y coste de API).

El cálculo del tamaño de muestra es un paso crítico que se realiza antes de iniciar el experimento. Se basa en el efecto mínimo detectable que se desea identificar, el nivel de significancia estadística (habitualmente alpha=0.05), la potencia estadística deseada (habitualmente 0.8) y la varianza estimada de la métrica principal. Herramientas como el calculador de tamaño de muestra de Evan Miller o bibliotecas de Python como `statsmodels` permiten realizar este cálculo de forma rigurosa.

### 7.2 Shadow testing pre-lanzamiento

El shadow testing es una técnica de evaluación pre-lanzamiento que consiste en ejecutar la nueva versión del sistema en paralelo a la versión de producción, procesando las mismas solicitudes reales pero sin enviar sus respuestas a los usuarios. Esto permite comparar los outputs de ambas versiones sobre tráfico real antes de exponer la nueva versión a usuarios reales.

Las ventajas del shadow testing sobre la evaluación offline son significativas: el tráfico de producción tiene una distribución más representativa que cualquier dataset de evaluación construido manualmente, y permite detectar problemas de rendimiento, latencia y coste que no son visibles en evaluaciones offline.

### 7.3 Análisis de resultados

El análisis de los resultados de un A/B test requiere rigor estadístico. Para métricas de proporción (tasa de resolución, tasa de abandono) se utiliza el test de proporciones de dos muestras o el test chi-cuadrado. Para métricas continuas (tiempo de resolución, puntuación de satisfacción) se utiliza el test t de Welch o, si la distribución no es normal, el test de Mann-Whitney U.

Es fundamental corregir por múltiples comparaciones cuando se evalúan varias métricas simultáneamente (corrección de Bonferroni o Benjamini-Hochberg) para evitar falsos positivos. También es importante definir la duración del experimento antes de comenzar y no detenerlo antes de alcanzar el tamaño de muestra calculado, para evitar el "peeking problem" que infla la tasa de falsos positivos.

---

## 8. CI/CD para soluciones LLM

### 8.1 Integración de evaluaciones en pipelines CI

La integración de evaluaciones de LLMs en pipelines de integración continua (CI) permite detectar regresiones de calidad de forma automática con cada cambio en el código, los prompts o la configuración del sistema. Esta práctica, a veces denominada "LLMOps", aplica los principios del DevOps tradicional al ciclo de vida de los sistemas basados en LLMs.

La implementación típica con GitHub Actions define un workflow que se activa con cada pull request o push a la rama principal. El workflow ejecuta las evaluaciones sobre un dataset de prueba representativo y compara los resultados con los umbrales de calidad definidos. Si alguna métrica cae por debajo del umbral, el workflow falla y bloquea el merge o el despliegue.

Un pipeline de CI para LLMs típicamente incluye las siguientes etapas: configuración del entorno con las dependencias necesarias, carga del dataset de evaluación desde un almacén centralizado (S3, GCS, base de datos), ejecución de las evaluaciones automatizadas, comparación de métricas con los umbrales definidos, generación de un informe de resultados y publicación de ese informe como comentario en el pull request.

### 8.2 Regresión de calidad y umbrales mínimos

El concepto de regresión de calidad en LLMs es más complejo que en software tradicional porque las métricas de calidad son continuas y ruidosas: el mismo sistema puede obtener puntuaciones ligeramente diferentes en dos evaluaciones consecutivas sobre el mismo dataset, simplemente por la naturaleza estocástica de los LLMs.

Para gestionar esta variabilidad, se recomienda establecer umbrales mínimos que incorporen un margen estadístico. En lugar de exigir que la faithfulness sea exactamente 0.85, se define un umbral de 0.80 que permita absorber la varianza natural del sistema. Los umbrales deben basarse en el rendimiento histórico del sistema y en los requisitos mínimos del caso de uso.

Adicionalmente, es útil monitorizar no solo el valor absoluto de las métricas sino también su tendencia temporal (media móvil de las últimas N evaluaciones) para detectar degradaciones graduales que no superen el umbral en ninguna evaluación individual.

### 8.3 Canary deployments para LLMs

El canary deployment es un patrón de despliegue que consiste en exponer la nueva versión del sistema a un subconjunto reducido del tráfico de producción (típicamente entre el 1% y el 10%) antes de realizar el despliegue completo. Este patrón permite detectar problemas en producción real con un impacto limitado en los usuarios.

En el contexto de los LLMs, los canary deployments son especialmente valiosos porque permiten detectar problemas que no son visibles en evaluaciones offline: comportamientos emergentes ante distribuciones de consultas reales no anticipadas, problemas de latencia bajo carga real, o reacciones negativas de usuarios que no se manifiestan en datasets de evaluación.

La transición de canary a despliegue completo debe estar guiada por métricas de producción que se monitoricen durante el período de canary: tasa de error, latencia en percentil 95 y 99, métricas de negocio (CSAT, tasa de resolución) y alertas de seguridad.

### 8.4 Monitorización en producción

La monitorización en producción de sistemas LLM tiene dimensiones técnicas y de calidad que deben seguirse de forma continua:

**Latencia.** Los LLMs tienen latencias más altas y variables que los modelos de ML tradicionales. Es fundamental monitorizar la latencia en percentiles (p50, p95, p99) en lugar de solo la media, ya que los percentiles altos revelan los casos más problemáticos para la experiencia de usuario. La latencia debe desglosarse por componente: tiempo de recuperación (para sistemas RAG), tiempo de primera token, tiempo total de generación.

**Coste por token.** El coste de operación de sistemas LLM está directamente relacionado con el número de tokens procesados (input + output). Monitorizar el coste por conversación y el coste total permite detectar anomalías (consultas que consumen un número inusualmente alto de tokens), optimizar el diseño de prompts y proyectar costes futuros.

**Tasa de error.** Incluye errores de la API del proveedor (timeouts, rate limits, errores de servidor), errores de parsing del output (cuando el modelo no sigue el formato de salida esperado) y errores de la lógica de negocio (respuestas que superan los filtros de seguridad, consultas no resolubles).

**Drift de distribución.** La distribución de las consultas de los usuarios en producción puede evolucionar con el tiempo, alejándose de la distribución sobre la que se evaluó el sistema. Es recomendable monitorizar la distribución de embeddings de las consultas de producción y alertar cuando se detecta un drift significativo respecto a la distribución de referencia.

---

## 9. Actividades prácticas

### Actividad 1: Evaluación de un sistema RAG con RAGAS

El estudiante implementará un sistema RAG básico sobre un corpus de documentos de su elección (artículos de Wikipedia, documentación técnica, etc.) y lo evaluará usando RAGAS. La actividad incluye: construcción del sistema RAG con LangChain, creación de un dataset de evaluación de al menos 20 pares pregunta-respuesta, ejecución de RAGAS y análisis de los resultados por métrica. El estudiante identificará al menos dos puntos de mejora del sistema basándose en los resultados de la evaluación e implementará al menos uno de ellos, comparando las métricas antes y después.

### Actividad 2: Diseño e implementación de un LLM-as-Judge

El estudiante diseñará un sistema de evaluación LLM-as-Judge para evaluar respuestas de un chatbot de soporte técnico. La actividad incluye: definición de los criterios de evaluación relevantes para el caso de uso, diseño del prompt de evaluación con escala de puntuación anclada y ejemplos few-shot, validación del evaluador mediante comparación con anotaciones humanas sobre una muestra de 30 ejemplos, y análisis de los sesgos detectados. El estudiante calculará el coeficiente de correlación de Spearman entre las puntuaciones del LLM evaluador y las anotaciones humanas.

### Actividad 3: Evaluación de factualidad y alucinaciones

El estudiante evaluará la tasa de alucinaciones de dos LLMs (por ejemplo, GPT-3.5-turbo y GPT-4o-mini) sobre un conjunto de preguntas factuales en un dominio específico. La actividad incluye: creación de un dataset de 50 preguntas con respuestas de referencia verificadas, implementación de un pipeline de evaluación basado en la metodología FactScore, comparación de los dos modelos en términos de tasa de alucinaciones y análisis de los tipos de alucinaciones más frecuentes. El estudiante propondrá una estrategia de mitigación basada en los resultados.

### Actividad 4: Pipeline CI/CD con DeepEval y GitHub Actions

El estudiante configurará un pipeline de CI/CD completo para un sistema LLM usando DeepEval y GitHub Actions. La actividad incluye: creación de un repositorio con una aplicación LLM sencilla, configuración de un conjunto de test cases con DeepEval, implementación de un workflow de GitHub Actions que ejecute los tests en cada pull request, definición de umbrales de calidad para las métricas de evaluación y simulación de una regresión de calidad (modificando el prompt) para verificar que el pipeline la detecta y bloquea el merge.

---

## 10. Referencias

- Es-Haghi, S., et al. (2023). **RAGAS: Automated Evaluation of Retrieval Augmented Generation**. arXiv:2309.15217. https://arxiv.org/abs/2309.15217

- RAGAS Documentation. (2024). *RAGAS: Evaluation framework for RAG pipelines*. https://docs.ragas.io/

- LangSmith Documentation. (2024). *LangSmith: Observability and evaluation for LLM applications*. LangChain. https://docs.smith.langchain.com/

- Liu, Y., et al. (2023). **G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment**. arXiv:2303.16634. https://arxiv.org/abs/2303.16634

- Min, S., et al. (2023). **FActScoring: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation**. arXiv:2305.14251. https://arxiv.org/abs/2305.14251

- Lin, S., et al. (2022). **TruthfulQA: Measuring How Models Mimic Human Falsehoods**. Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics. https://arxiv.org/abs/2109.07958
