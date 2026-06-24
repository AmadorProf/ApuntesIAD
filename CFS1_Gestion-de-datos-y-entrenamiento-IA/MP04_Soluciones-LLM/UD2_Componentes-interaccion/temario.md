# UD2 · Componentes de interacción con el modelo LLM

**Módulo:** MP04 — Soluciones LLM  
**Ciclo:** CFS1 — Gestión de datos y entrenamiento de IA  
**Duración estimada:** 12 horas lectivas

---

## 1. Introducción — la interfaz con el LLM como disciplina de ingeniería: del arte al proceso

Durante los primeros años de adopción masiva de los modelos de lenguaje de gran escala, la interacción con ellos se consideraba más un arte que una técnica. Los usuarios escribían prompts intuitivamente, ajustaban por ensayo y error, y transmitían sus trucos entre comunidades de forma informal. Ese periodo fue necesario para explorar el espacio de posibilidades, pero resultó insuficiente para construir sistemas fiables en producción.

La ingeniería de interacción con LLMs —a menudo llamada prompt engineering en su versión más estrecha, pero que abarca mucho más— es hoy una disciplina con metodología propia. Comprende el diseño sistemático de entradas al modelo, la configuración de los parámetros de generación, la gestión del estado conversacional, el control del formato de salida y la integración con sistemas externos. Cada una de estas dimensiones tiene principios verificables, métricas de evaluación y decisiones de diseño con consecuencias medibles en coste, latencia y calidad de respuesta.

Esta unidad cubre los componentes fundamentales de esa disciplina. El punto de partida es el reconocimiento de que un LLM, por potente que sea, es un componente de un sistema mayor. Su comportamiento en ese sistema depende de cómo se le instruye, qué información se le proporciona, cómo se gestiona el flujo de la conversación y cómo se extraen y validan sus salidas. Dominar esos mecanismos es la diferencia entre un prototipo impresionante en una demo y una aplicación que funciona de forma consistente bajo condiciones reales.

A lo largo de la unidad se trabajará con ejemplos concretos de código, fragmentos de prompt reales y referencias a la documentación oficial de los principales proveedores. El objetivo no es memorizar técnicas sino desarrollar criterio para elegir la técnica correcta en cada situación.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante debe ser capaz de:

- Distinguir las principales técnicas de prompt engineering (zero-shot, few-shot, CoT, ToT, self-consistency) y seleccionar la más adecuada según el tipo de tarea.
- Diseñar system prompts eficaces para aplicaciones especializadas, con instrucciones de comportamiento, restricciones y gestión de identidad del asistente.
- Configurar los parámetros de generación de una API de LLM (temperatura, top-p, top-k, penalizaciones, max_tokens, stop sequences) con criterio fundamentado en el tipo de tarea.
- Explicar qué es un token, usar herramientas de conteo (tiktoken) y gestionar la ventana de contexto en conversaciones largas.
- Implementar estrategias de gestión de historial conversacional (ventana deslizante, resumen, recuperación selectiva) en código Python.
- Extraer outputs estructurados de un LLM mediante JSON mode, function calling y validación con Pydantic.

---

## 3. Prompt engineering: técnicas fundamentales

El prompt es la unidad básica de instrucción a un LLM. Su diseño no es trivial: modelos entrenados con los mismos datos y la misma arquitectura producen resultados cualitativamente distintos según cómo se formule la entrada. A continuación se describen las técnicas más importantes, de menor a mayor sofisticación.

### 3.1 Zero-shot prompting

El zero-shot prompting consiste en formular una tarea al modelo sin proporcionar ningún ejemplo de cómo resolverla. El modelo debe basarse exclusivamente en el conocimiento adquirido durante el preentrenamiento.

**Estructura básica:**

```
[Instrucción clara de la tarea]
[Entrada sobre la que operar]
[Indicación del formato de salida deseado, si procede]
```

**Ejemplo:**

```
Clasifica el sentimiento del siguiente texto como POSITIVO, NEGATIVO o NEUTRO.

Texto: "El servicio fue lento pero la comida estaba buenísima."

Sentimiento:
```

**Cuándo funciona bien:** tareas de clasificación simple, reformulación, traducción, resumen de textos cortos.

**Limitaciones:** en tareas que requieren razonamiento multi-paso, conocimiento especializado o formato de salida muy preciso, el zero-shot tiende a producir resultados inconsistentes. El modelo no tiene referencia de lo que se espera exactamente.

### 3.2 Few-shot prompting

El few-shot prompting añade al prompt varios ejemplos (shots) del par entrada-salida deseado antes de presentar el caso real. Es una forma de aprendizaje en contexto (in-context learning): el modelo infiere el patrón a partir de los ejemplos sin actualizar sus pesos.

**Aspectos clave en el diseño:**

- **Selección de ejemplos:** deben ser representativos de la distribución real de entradas, no solo de los casos fáciles. Incluir ejemplos de casos límite mejora la robustez.
- **Formato:** los ejemplos deben ser coherentes en estructura. Si un ejemplo incluye una explicación y otro no, el modelo puede comportarse de forma inconsistente.
- **Número óptimo:** entre 3 y 8 ejemplos suelen ser suficientes para tareas de complejidad media. Más ejemplos consumen tokens y pueden introducir sesgos si no son diversos.

**Ejemplo (clasificación de tickets de soporte):**

```
Clasifica cada ticket según su categoría: FACTURACIÓN, TÉCNICO o GENERAL.

Ticket: "Me han cobrado dos veces este mes."
Categoría: FACTURACIÓN

Ticket: "La aplicación se cierra sola cuando intento subir un archivo."
Categoría: TÉCNICO

Ticket: "¿Cuál es el horario de atención al cliente?"
Categoría: GENERAL

Ticket: "No puedo acceder a mi cuenta desde ayer por la tarde."
Categoría:
```

El modelo, tras ver tres ejemplos, aplica el patrón al cuarto ticket sin instrucción explícita adicional.

### 3.3 Chain-of-Thought (CoT)

El chain-of-thought prompting (Wei et al., 2022) descubrió que pedir al modelo que muestre su razonamiento paso a paso mejora significativamente su rendimiento en tareas que requieren razonamiento aritmético, lógico o de sentido común.

**CoT estándar (few-shot CoT):** los ejemplos del prompt incluyen no solo la respuesta sino también la cadena de razonamiento intermedio.

**Ejemplo:**

```
Pregunta: En una tienda hay 48 manzanas. Se venden 17 por la mañana y se reciben 25 nuevas por la tarde. ¿Cuántas manzanas hay al final del día?

Razonamiento: Empezamos con 48 manzanas. Por la mañana se venden 17, así que quedan 48 - 17 = 31. Por la tarde llegan 25 más: 31 + 25 = 56. Al final del día hay 56 manzanas.
Respuesta: 56

Pregunta: Un tren sale a las 9:15 y llega a su destino tras 2 horas y 40 minutos de viaje. ¿A qué hora llega?

Razonamiento:
```

**Zero-shot CoT:** en lugar de proporcionar ejemplos, se añade la frase "Vamos a pensar paso a paso." (o su equivalente en inglés: "Let's think step by step.") al final del prompt. Esta técnica, descubierta por Kojima et al. (2022), activa en el modelo un comportamiento de razonamiento explícito sin necesidad de ejemplos.

```
Un agricultor tiene 15 ovejas y todas menos 9 mueren. ¿Cuántas ovejas le quedan?

Vamos a pensar paso a paso.
```

CoT es especialmente eficaz en modelos grandes (>10B parámetros). En modelos pequeños, el beneficio es menor o incluso negativo.

### 3.4 Tree-of-Thought (ToT)

El Tree-of-Thought (Yao et al., 2023) extiende el chain-of-thought al permitir al modelo explorar múltiples ramas de razonamiento en lugar de seguir una sola cadena lineal. Cada "pensamiento" es un paso intermedio que puede ramificarse en varias continuaciones posibles, formando un árbol de búsqueda.

El proceso implica:

1. **Generación:** producir varios pensamientos candidatos en cada paso.
2. **Evaluación:** puntuar cada pensamiento según su viabilidad para resolver el problema.
3. **Búsqueda:** explorar el árbol mediante estrategias como BFS (búsqueda en anchura) o DFS (búsqueda en profundidad).

ToT es más costoso computacionalmente (requiere múltiples llamadas a la API) pero resuelve problemas donde un razonamiento lineal se bloquea en callejones sin salida. Es especialmente útil en tareas de planificación, juegos de lógica o generación creativa con restricciones.

**Caso de uso ilustrativo:** resolver el puzzle de los "24 puntos" (dado cuatro números, encontrar una expresión aritmética que dé 24) es un problema donde CoT lineal falla con frecuencia y ToT mejora significativamente el rendimiento.

### 3.5 Self-consistency

La self-consistency (Wang et al., 2022) es una estrategia de decodificación que complementa al chain-of-thought. En lugar de generar un único razonamiento, el modelo genera múltiples razonamientos independientes (con temperatura > 0) y luego se aplica un mecanismo de votación mayoritaria sobre las respuestas finales.

**Proceso:**

1. Lanzar el mismo prompt CoT N veces (típicamente 5-20).
2. Extraer la respuesta final de cada razonamiento.
3. Seleccionar la respuesta más frecuente.

**Por qué funciona:** cuando el modelo razona correctamente por múltiples caminos distintos y llega a la misma respuesta, esa respuesta es más fiable. Los errores tienden a ser idiosincráticos y no se repiten de forma consistente.

**Coste:** N veces el coste de una sola llamada. Para tareas críticas donde la precisión justifica el coste, es una técnica muy efectiva.

---

## 4. System prompts y roles

### 4.1 La estructura de mensajes: system, user, assistant

Los LLMs modernos accesibles por API utilizan una estructura de conversación con tres roles diferenciados:

- **system:** instrucciones globales que definen el comportamiento del modelo para toda la conversación. El usuario final generalmente no las ve ni las modifica.
- **user:** los mensajes que provienen del usuario humano.
- **assistant:** las respuestas generadas por el modelo.

Esta separación permite a los desarrolladores establecer un contexto de comportamiento persistente sin mezclarlo con el contenido de la conversación real.

```json
[
  {"role": "system", "content": "Eres un asistente especializado en derecho laboral español. Responde siempre citando el artículo de ley aplicable. No des consejos sobre otras áreas jurídicas."},
  {"role": "user", "content": "¿Cuántos días de vacaciones corresponden a un trabajador a tiempo completo?"},
  {"role": "assistant", "content": "Según el artículo 38 del Estatuto de los Trabajadores..."}
]
```

### 4.2 Diseño de system prompts eficaces

Un system prompt bien diseñado tiene estructura, no es una lista de deseos vaga. Los componentes recomendados son:

**a) Definición del rol y contexto**

Quién es el asistente, para qué organización trabaja, qué audiencia tiene.

```
Eres Clara, asistente virtual de Formación Continua de IFC. 
Ayudas a estudiantes de ciclos formativos con dudas sobre el contenido académico y los procesos de matrícula.
```

**b) Instrucciones de comportamiento**

Cómo debe responder: tono, longitud, nivel de detalle, idioma.

```
Responde siempre en español. Usa un tono cercano pero profesional. 
Las respuestas sobre contenido académico deben ser precisas y estructuradas. 
Las respuestas sobre procesos administrativos deben ser concisas (máximo 3 pasos numerados).
```

**c) Restricciones explícitas**

Qué no debe hacer. Las restricciones negativas son tan importantes como las instrucciones positivas.

```
No inventes información sobre fechas de exámenes ni requisitos de matriculación que no conozcas con certeza.
Si no tienes información suficiente para responder, indica que el estudiante debe contactar con administración.
No respondas preguntas que no estén relacionadas con IFC o con los estudios que el usuario está cursando.
```

**d) Formato de salida**

Si la aplicación procesará la respuesta, especificar el formato evita postprocesado.

```
Cuando expliques un proceso, usa siempre formato de lista numerada.
No uses markdown en las respuestas, ya que se mostrarán en una interfaz de chat que no lo renderiza.
```

**e) Ejemplos en el system prompt**

Para comportamientos difíciles de describir abstractamente, un ejemplo dentro del system prompt es más eficaz que la descripción.

### 4.3 Gestión de identidad del asistente

En aplicaciones orientadas al usuario final, suele ser deseable que el asistente tenga una identidad coherente (nombre, personalidad, restricciones de divulgación). Las consideraciones principales son:

- Dar un nombre al asistente ancla la identidad y permite referencias consistentes en la conversación.
- Instruir al modelo sobre qué revelar de sí mismo (p. ej., no confirmar qué modelo subyacente usa) es legítimo en contextos comerciales.
- Evitar instrucciones que contradigan directamente las políticas del proveedor (p. ej., pedir que niegue ser una IA).

### 4.4 Ejemplos de system prompts para aplicaciones especializadas

**Soporte técnico:**

```
Eres un agente de soporte técnico de nivel 1 para el software de gestión XYZ. 
Tu objetivo es resolver problemas de instalación, configuración y uso básico.
Cuando el problema supere tu capacidad de resolución, escala al nivel 2 indicando: 
"Este problema requiere revisión por un técnico especializado. Te paso el caso."
Pregunta siempre la versión del sistema operativo y del software antes de sugerir soluciones.
```

**Redacción legal:**

```
Eres un asistente de redacción jurídica para un despacho de abogados especializado en derecho mercantil español.
Ayudas a redactar borradores de contratos, cláusulas y comunicaciones formales.
Usa siempre terminología jurídica precisa. Indica explícitamente cuando una cláusula es estándar del sector y cuando es una redacción personalizada.
Añade al final de cada borrador: "BORRADOR PARA REVISIÓN. Este documento requiere revisión y validación por un abogado colegiado antes de su uso."
```

**Tutor educativo:**

```
Eres Tutor, un asistente pedagógico para estudiantes de secundaria.
Tu método: nunca des la respuesta directamente. Guía al estudiante con preguntas que activen su razonamiento.
Si el estudiante está bloqueado tras dos intentos, ofrece una pista parcial, no la solución completa.
Adapta el lenguaje al nivel del estudiante. Si detectas que el estudiante usa vocabulario avanzado, puedes elevar el nivel de la explicación.
```

---

## 5. APIs de LLMs: parámetros de generación

Las APIs de los principales proveedores (OpenAI, Anthropic, etc.) exponen un conjunto de parámetros que controlan cómo el modelo genera texto. Conocerlos y saber usarlos es esencial para obtener el comportamiento deseado en cada tipo de tarea.

### 5.1 Temperatura

La temperatura controla la aleatoriedad de la selección del siguiente token. Matemáticamente, divide los logits por el valor de temperatura antes de aplicar el softmax.

- **Temperatura = 0:** el modelo selecciona siempre el token con mayor probabilidad. Las respuestas son deterministas y reproducibles.
- **Temperatura = 1:** comportamiento estándar del modelo, distribución de probabilidad sin modificar.
- **Temperatura > 1:** distribución más plana, mayor aleatoriedad, respuestas más diversas pero también menos coherentes.

**Valores recomendados por tipo de tarea:**

| Tarea | Temperatura recomendada |
|---|---|
| Extracción de datos, clasificación, código | 0 – 0.2 |
| Análisis, resumen, QA factual | 0.3 – 0.5 |
| Escritura profesional, emails | 0.5 – 0.7 |
| Generación creativa, brainstorming | 0.8 – 1.0 |

### 5.2 Top-p (nucleus sampling)

Top-p limita el espacio de tokens a considerar al subconjunto de tokens cuya probabilidad acumulada supera el umbral p. Con top-p = 0.9, en cada paso el modelo considera solo los tokens que forman el 90% de la masa de probabilidad total.

A diferencia de la temperatura, top-p adapta dinámicamente el número de candidatos según la distribución en cada paso: cuando el modelo está seguro (distribución concentrada), considera pocos candidatos; cuando está inseguro (distribución plana), considera más.

**Recomendación práctica:** no ajustar temperatura y top-p simultáneamente. Elegir uno de los dos mecanismos y dejar el otro en su valor por defecto.

### 5.3 Top-k

Top-k restringe la selección al conjunto de los k tokens más probables en cada paso, independientemente de sus probabilidades absolutas. Con top-k = 40, solo los 40 tokens más probables son candidatos.

La diferencia con top-p es que top-k usa un número fijo de candidatos, no un umbral probabilístico. Esto puede ser problemático: si los 40 tokens más probables son todos muy improbables (distribución muy plana), top-k incluirá muchas opciones de baja calidad.

Top-k es el parámetro predeterminado en algunos modelos (como los de Google/Gemini) y top-p en otros (OpenAI). Muchas APIs permiten ambos.

### 5.4 Repetition penalty / Frequency penalty / Presence penalty

Estos parámetros penalizan la repetición de tokens ya generados:

- **Repetition penalty** (terminología común en modelos HuggingFace): multiplica la probabilidad de un token por un factor menor que 1 si ya ha aparecido. Valor > 1 reduce repeticiones.
- **Frequency penalty** (OpenAI): penalización proporcional a cuántas veces ha aparecido el token. Penaliza más los tokens que se repiten mucho.
- **Presence penalty** (OpenAI): penalización binaria (aparece o no aparece). Fomenta el uso de vocabulario nuevo independientemente de la frecuencia.

**Uso típico:** frequency_penalty entre 0.1 y 0.5 es útil para evitar que el modelo repita frases en textos largos. Valores muy altos pueden degradar la coherencia.

### 5.5 Max tokens

Número máximo de tokens que el modelo generará. No confundir con el límite de contexto total (que incluye prompt + respuesta). Establecer un max_tokens adecuado:

- Evita respuestas excesivamente largas (y el coste asociado).
- Puede truncar respuestas si se fija muy bajo. El modelo no sabe de antemano cuándo será cortado.

### 5.6 Stop sequences

Lista de cadenas de texto que, al aparecer en la generación, detienen inmediatamente la producción. Son útiles para:

- Controlar el final de respuestas en formatos estructurados.
- Implementar turnos en conversaciones simuladas.
- Delimitar secciones en outputs de múltiples partes.

**Ejemplo:** en un sistema que genera fichas de producto, `stop=["---FIN---"]` garantiza que el modelo se detenga cuando señale el final del registro.

### 5.7 Ejemplos con OpenAI API y Anthropic API

**OpenAI (Python):**

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Eres un experto en análisis de sentimientos."},
        {"role": "user", "content": "Analiza el sentimiento de este texto: 'El producto llegó tarde pero el servicio al cliente fue excelente.'"}
    ],
    temperature=0.2,
    max_tokens=200,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
)

print(response.choices[0].message.content)
```

**Anthropic (Python):**

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=200,
    system="Eres un experto en análisis de sentimientos.",
    messages=[
        {"role": "user", "content": "Analiza el sentimiento de este texto: 'El producto llegó tarde pero el servicio al cliente fue excelente.'"}
    ],
    temperature=0.2
)

print(message.content[0].text)
```

Nota: en la Anthropic Messages API, el system prompt se pasa como parámetro independiente (`system=`), no como un mensaje con `role: system` dentro del array de mensajes.

---

## 6. Tokenización

### 6.1 Qué es un token

Un token es la unidad mínima de texto que procesa un LLM. No coincide con las palabras del lenguaje natural: puede ser una palabra completa, una sílaba, un signo de puntuación, un espacio o una combinación. El tokenizador convierte texto en secuencias de tokens antes de pasarlo al modelo, y convierte la secuencia de tokens generada de vuelta a texto.

Los LLMs actuales utilizan tokenización por subpalabras, principalmente mediante algoritmos como BPE (Byte Pair Encoding) o SentencePiece. La ventaja es que el vocabulario es finito y manejable (32.000 – 100.000 tokens) pero puede representar cualquier texto, incluyendo palabras desconocidas descompuestas en subpalabras.

Reglas prácticas aproximadas para el inglés:
- 1 token ≈ 4 caracteres
- 1 token ≈ ¾ de una palabra
- 100 tokens ≈ 75 palabras

### 6.2 tiktoken para contar tokens en OpenAI

tiktoken es la biblioteca oficial de OpenAI para tokenización. Permite contar tokens de forma precisa antes de hacer una llamada a la API.

```python
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

texto = "El aprendizaje automático es una rama de la inteligencia artificial."
tokens = enc.encode(texto)

print(f"Número de tokens: {len(tokens)}")
print(f"Tokens: {tokens}")
```

Esto es especialmente útil para:

- Estimar el coste de una llamada antes de ejecutarla.
- Verificar que un prompt no supera el límite de contexto.
- Implementar lógica de truncado o compresión de contexto.

### 6.3 Eficiencia por idioma: español vs inglés

Los tokenizadores de los modelos más comunes (como el de GPT-4) fueron entrenados con corpus predominantemente en inglés. Como resultado, el español (y otros idiomas con morfología más rica) tiende a requerir más tokens para expresar el mismo contenido semántico.

**Ejemplo ilustrativo:**

- Inglés: "The automatic learning system processes data efficiently." → ~9 tokens
- Español: "El sistema de aprendizaje automático procesa los datos de forma eficiente." → ~14-16 tokens

Las implicaciones son directas: el mismo documento en español cuesta más tokens, lo que se traduce en mayor coste y menor capacidad de contexto efectiva. Esto debe considerarse en el diseño de aplicaciones multilingüe.

### 6.4 Impacto del vocabulario en el coste

El coste de uso de la API se factura por tokens (input + output). Optimizar el uso de tokens es, por tanto, una decisión económica y técnica:

- Los prompts verbosos con instrucciones redundantes aumentan el coste sin mejorar necesariamente la calidad.
- Las conversaciones largas acumulan tokens de historial que se repagan en cada llamada.
- Los ejemplos few-shot consumen tokens; su valor debe justificar el coste.

### 6.5 Límites de contexto y gestión de ventana larga

Cada modelo tiene un límite de contexto máximo, expresado en tokens, que incluye tanto el prompt (input) como la respuesta (output). Los modelos actuales de referencia tienen ventanas de 128K, 200K o incluso 1M de tokens, pero el coste y la latencia escalan con el tamaño del contexto.

Cuando una aplicación maneja documentos largos o conversaciones extendidas, es necesario gestionar activamente qué entra en la ventana de contexto. Las estrategias se detallan en la siguiente sección.

---

## 7. Gestión del historial de conversación

### 7.1 Stateless vs stateful

Los LLMs son, por diseño, sin estado (stateless): cada llamada a la API es independiente. El modelo no recuerda conversaciones anteriores. La "memoria" conversacional es una ilusión construida por la aplicación que, en cada llamada, envía el historial de la conversación como parte del prompt.

Esto tiene implicaciones importantes:

- El coste de cada llamada incluye todos los mensajes anteriores de la conversación.
- Si el historial supera el límite de contexto, hay que decidir qué descartar.
- La coherencia conversacional es responsabilidad del desarrollador, no del modelo.

### 7.2 Estrategias de gestión del contexto

**a) Ventana deslizante (sliding window)**

Se mantienen solo los N mensajes más recientes. Es simple de implementar y garantiza que el contexto no crece indefinidamente. El problema es que puede perder información relevante de mensajes tempranos (como el nombre del usuario, una preferencia expresada, o el problema original que se intentaba resolver).

**b) Resumen de conversación**

Cuando el historial alcanza un umbral, se pide al modelo que genere un resumen de la conversación hasta ese punto, y se sustituye el historial completo por ese resumen. El resumen ocupa menos tokens y preserva información semántica relevante.

```python
def resumir_conversacion(historial, client):
    mensajes_para_resumir = historial.copy()
    mensajes_para_resumir.append({
        "role": "user",
        "content": "Resume la conversación anterior en menos de 150 palabras, destacando los puntos clave acordados y el contexto relevante para continuar."
    })
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mensajes_para_resumir,
        temperature=0
    )
    return response.choices[0].message.content
```

**c) Recuperación selectiva**

En conversaciones muy largas o en sistemas de agentes, se almacena el historial completo en una base de datos y se recuperan solo los fragmentos relevantes para la consulta actual, típicamente mediante búsqueda semántica (embeddings + búsqueda vectorial). Es la base de los sistemas RAG (Retrieval-Augmented Generation).

### 7.3 Estructura de mensajes para multi-turn conversation

Una conversación multi-turno se estructura como un array de mensajes donde los roles alternan entre `user` y `assistant`. La aplicación mantiene este array y lo envía completo en cada nueva llamada.

**Ejemplo completo con Python y OpenAI API:**

```python
from openai import OpenAI

client = OpenAI()

historial = [
    {"role": "system", "content": "Eres un asistente de ayuda para estudiantes de programación. Eres paciente y pedagógico."}
]

def chat(mensaje_usuario):
    historial.append({"role": "user", "content": mensaje_usuario})
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=historial,
        temperature=0.5,
        max_tokens=500
    )
    
    respuesta = response.choices[0].message.content
    historial.append({"role": "assistant", "content": respuesta})
    
    # Control simple de ventana: mantener system + últimos 10 mensajes
    if len(historial) > 11:
        historial[1:3] = []  # eliminar los dos mensajes más antiguos (no el system)
    
    return respuesta

# Uso
print(chat("¿Qué es una función recursiva?"))
print(chat("¿Puedes darme un ejemplo en Python?"))
print(chat("¿Y cuándo es mejor usarla?"))
```

---

## 8. Structured outputs

### 8.1 El problema de los outputs no estructurados

Por defecto, los LLMs generan texto libre. Para integrarse con sistemas que esperan datos en un formato específico (JSON para una base de datos, campos para un formulario, objetos para un ORM), necesitamos mecanismos que garanticen la estructura de la salida.

### 8.2 JSON mode y function calling

**JSON mode (OpenAI):** fuerza al modelo a generar siempre JSON válido. No controla el esquema, solo la validez sintáctica.

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Extrae la información del texto y devuelve un JSON con los campos: nombre, empresa, email, telefono."},
        {"role": "user", "content": "Hola, soy Laura García de Distribuciones Pérez S.L. Puedes contactarme en laura@distperez.es o en el 612 345 678."}
    ],
    response_format={"type": "json_object"},
    temperature=0
)

import json
datos = json.loads(response.choices[0].message.content)
```

**Structured outputs (OpenAI, versión más reciente):** permite especificar un esquema JSON completo y el modelo garantiza adherencia estricta.

**Function calling / tool use:** mecanismo por el que se definen "herramientas" con esquemas de parámetros tipados. El modelo decide cuándo llamar a cada herramienta y genera los argumentos en el formato especificado. Es la base de los agentes LLM.

### 8.3 Pydantic para validar outputs estructurados

Pydantic permite definir modelos de datos con tipos y validaciones, y usarlos para parsear y validar la salida del LLM.

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
import json

class ContactoEmpresa(BaseModel):
    nombre: str
    empresa: str
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None

# Parsear y validar la respuesta del modelo
try:
    contacto = ContactoEmpresa.model_validate_json(response.choices[0].message.content)
    print(f"Nombre validado: {contacto.nombre}")
    print(f"Email validado: {contacto.email}")
except Exception as e:
    print(f"Error de validación: {e}")
```

La biblioteca `instructor` (construida sobre Pydantic) simplifica aún más la integración, permitiendo pasar directamente el modelo Pydantic a la llamada de la API y obteniendo el objeto validado directamente.

### 8.4 Ejemplos de extracción de información estructurada

**Extracción de entidades:**

```python
class EntidadesTexto(BaseModel):
    personas: list[str]
    organizaciones: list[str]
    lugares: list[str]
    fechas: list[str]
```

**Extracción de relaciones:**

```python
class Relacion(BaseModel):
    sujeto: str
    predicado: str
    objeto: str

class RelacionesTexto(BaseModel):
    relaciones: list[Relacion]
```

**Formulario de incidencia:**

```python
class Incidencia(BaseModel):
    tipo: Literal["hardware", "software", "red", "acceso", "otro"]
    urgencia: Literal["baja", "media", "alta", "critica"]
    descripcion: str
    usuario_afectado: str
    pasos_reproduccion: Optional[list[str]] = None
```

---

## 9. Actividades prácticas

### Actividad 1 — Comparativa de técnicas de prompting

**Objetivo:** experimentar de primera mano la diferencia entre zero-shot, few-shot y CoT en una tarea concreta.

**Tarea:** dado un conjunto de 10 problemas de razonamiento lógico o matemático de dificultad media, diseñar tres versiones del prompt para cada uno (zero-shot, few-shot con 3 ejemplos, zero-shot CoT) y comparar los resultados.

**Entregable:** tabla comparativa con: técnica usada, respuesta del modelo, corrección de la respuesta, número aproximado de tokens, observaciones sobre el razonamiento mostrado. Análisis escrito (250-300 palabras) con conclusiones.

**Herramientas:** OpenAI Playground o acceso a API con tiktoken para conteo de tokens.

### Actividad 2 — Diseño de system prompt para aplicación especializada

**Objetivo:** diseñar un system prompt completo para una aplicación real.

**Tarea:** el estudiante elige uno de los siguientes contextos (o propone uno propio con aprobación): (a) asistente de atención al cliente para una empresa de e-commerce, (b) tutor de matemáticas para bachillerato, (c) agente de preselección de CVs para RRHH.

El system prompt debe incluir: definición del rol, instrucciones de comportamiento (tono, idioma, longitud), restricciones explícitas (qué no hacer), formato de respuesta, al menos un ejemplo de comportamiento esperado.

**Evaluación:** se probará el system prompt con al menos 5 casos de uso típicos y 3 casos límite (intentos de manipulación, preguntas fuera de scope, peticiones ambiguas).

### Actividad 3 — Gestor de conversación con control de contexto

**Objetivo:** implementar un chatbot multi-turno con gestión activa de la ventana de contexto.

**Tarea:** desarrollar en Python una clase `ConversationManager` que implemente: almacenamiento del historial, truncado automático cuando el historial supere 2000 tokens (usando tiktoken para conteo preciso), generación de resumen automático antes del truncado, método `chat()` que recibe un mensaje y devuelve la respuesta del modelo.

**Extensión opcional:** implementar persistencia del historial en un archivo JSON para continuar conversaciones entre sesiones.

### Actividad 4 — Pipeline de extracción de datos estructurados

**Objetivo:** construir un pipeline que extrae datos estructurados de texto no estructurado y los valida con Pydantic.

**Tarea:** dado un conjunto de 20 correos electrónicos de solicitud de presupuesto (proporcionados como dataset), implementar un script que: lea cada email, envíe el texto a la API con un prompt de extracción, parsee la respuesta en un modelo Pydantic con campos definidos (cliente, producto solicitado, cantidad, fecha de entrega deseada, contacto), guarde los registros válidos en un CSV y registre los fallidos con el error de validación.

**Criterio de evaluación:** porcentaje de extracción correcta sobre el dataset completo, robustez ante emails mal formateados, gestión adecuada de errores.

---

## 10. Referencias

- **Prompt Engineering Guide** — DAIR.AI. Guía de referencia sobre técnicas de prompting, actualizada continuamente.  
  URL: https://www.promptingguide.ai

- **OpenAI API Documentation** — Referencia oficial de la API de OpenAI, incluyendo parámetros de generación, function calling y structured outputs.  
  URL: https://platform.openai.com/docs

- **Anthropic API Documentation (Messages API)** — Referencia oficial de la API de Anthropic para Claude, incluyendo parámetros, system prompts y tool use.  
  URL: https://docs.anthropic.com/en/api/messages

- **Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., Chi, E., Le, Q. V., & Zhou, D. (2022).** Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. *NeurIPS 2022*.  
  URL: https://arxiv.org/abs/2201.11903

- **Yao, S., Yu, D., Zhao, J., Shafran, I., Griffiths, T. L., Cao, Y., & Narasimhan, K. (2023).** Tree of Thoughts: Deliberate Problem Solving with Large Language Models. *NeurIPS 2023*.  
  URL: https://arxiv.org/abs/2305.10601

- **Wang, X., Wei, J., Schuurmans, D., Le, Q., Chi, E., Narang, S., Chowdhery, A., & Zhou, D. (2022).** Self-Consistency Improves Chain of Thought Reasoning in Language Models.  
  URL: https://arxiv.org/abs/2203.11171

- **tiktoken** — Biblioteca oficial de OpenAI para tokenización y conteo de tokens.  
  URL: https://github.com/openai/tiktoken

- **Kojima, T., Gu, S. S., Reid, M., Matsuo, Y., & Iwasawa, Y. (2022).** Large Language Models are Zero-Shot Reasoners. *NeurIPS 2022*.  
  URL: https://arxiv.org/abs/2205.11916
