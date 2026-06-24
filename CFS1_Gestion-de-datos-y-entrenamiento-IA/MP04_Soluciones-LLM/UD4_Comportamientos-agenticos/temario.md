# UD4 · Comportamientos agénticos con LLMs

---

## 1. Introducción — de chatbots a agentes

Durante los primeros años de expansión de los modelos de lenguaje de gran escala (LLMs), la interacción predominante seguía un patrón simple: el usuario escribía un mensaje, el modelo generaba una respuesta, y la conversación terminaba o continuaba en ese mismo plano textual. Este modelo de chatbot, aunque enormemente útil, presentaba una limitación estructural: el sistema no podía hacer nada más allá de producir texto. No podía consultar una base de datos actualizada, no podía ejecutar código, no podía reservar una reunión ni interactuar con servicios externos. Todo lo que "sabía" estaba congelado en los pesos del modelo, limitado al conocimiento del momento del entrenamiento.

El paso hacia los agentes representa una ruptura conceptual de primer orden. Un agente basado en LLM no se limita a generar texto: percibe su entorno, razona sobre él, toma decisiones, ejecuta acciones y observa las consecuencias de dichas acciones para ajustar su comportamiento. Esta cadena —percepción, razonamiento, acción, observación— es el núcleo de lo que se denomina comportamiento agéntico.

La diferencia no es meramente técnica. Es una diferencia en la naturaleza del sistema. Un chatbot es un oráculo: responde preguntas. Un agente es un actor: resuelve problemas en el mundo real interactuando con herramientas, APIs, bases de datos y otros sistemas. Esta capacidad de actuar sobre el entorno, de encadenar pasos, de corregir errores sobre la marcha y de operar durante períodos prolongados sin intervención humana constante define la nueva frontera de los LLMs aplicados.

El campo de los agentes ha madurado rápidamente. Desde los primeros experimentos con AutoGPT en 2023 —que demostraron la viabilidad del concepto pero también sus fragilidades— hasta los frameworks actuales como LangGraph, AutoGen o CrewAI, el ecosistema ha ganado en solidez, predictibilidad y aplicabilidad real. Esta unidad didáctica recorre los fundamentos teóricos, los mecanismos técnicos y las mejores prácticas para diseñar, implementar y evaluar sistemas agénticos basados en LLMs.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Distinguir conceptualmente entre un sistema de chatbot convencional y un sistema agéntico, identificando las capacidades diferenciales de este último.
- Comprender y comparar las principales arquitecturas agénticas: ReAct, Plan-and-Execute y Reflexion, seleccionando la más adecuada según el caso de uso.
- Implementar function calling mediante las APIs de OpenAI y Anthropic, definiendo herramientas con JSON Schema y gestionando los ciclos de llamada y respuesta.
- Diseñar y conectar un toolkit de herramientas para agentes que incluya búsqueda web, ejecución de código, consulta a bases de datos y llamadas a APIs externas.
- Utilizar frameworks de orquestación —LangGraph, AutoGen, CrewAI— para construir agentes mono y multi-step, así como sistemas multiagente.
- Implementar mecanismos de memoria a corto y largo plazo en agentes, comprendiendo la diferencia entre memoria conversacional, episódica y semántica.
- Diseñar sistemas multiagente con patrones de coordinación supervisor-workers y colaboración peer-to-peer.
- Identificar los riesgos de seguridad específicos de los sistemas agénticos y aplicar mitigaciones mediante principios de mínimo privilegio, sandboxing y supervisión humana.

---

## 3. Arquitecturas agénticas

### 3.1 ReAct: Reasoning + Acting

ReAct (Yao et al., 2022) es la arquitectura agéntica más influyente y ampliamente adoptada. Su nombre proviene de la combinación de dos procesos que el modelo ejecuta de forma intercalada: razonamiento (Reasoning) y acción (Acting). El ciclo fundamental de ReAct se articula en tres pasos que se repiten hasta alcanzar la respuesta final:

**Thought (Pensamiento):** El modelo razona en lenguaje natural sobre la situación actual, el objetivo y los pasos necesarios. Este razonamiento es visible y trazable, lo que facilita la depuración.

**Action (Acción):** El modelo decide invocar una herramienta concreta con parámetros específicos. Puede ser una búsqueda web, una consulta a una API, la ejecución de código, etc.

**Observation (Observación):** El resultado de la acción se devuelve al modelo como contexto. El modelo lo integra en su razonamiento y continúa el ciclo.

**Ejemplo de ciclo ReAct:**

```
Pregunta: ¿Cuál es la temperatura actual en Madrid y cuántos grados Fahrenheit son?

Thought: Necesito consultar la temperatura actual en Madrid. Usaré la herramienta de clima.
Action: get_weather(city="Madrid")
Observation: {"temperature_celsius": 28, "condition": "soleado"}

Thought: La temperatura es 28°C. Ahora necesito convertirla a Fahrenheit: F = C × 9/5 + 32.
Action: calculate(expression="28 * 9/5 + 32")
Observation: 82.4

Thought: Tengo todos los datos necesarios. Puedo responder.
Final Answer: En Madrid la temperatura actual es de 28°C (82.4°F) y el cielo está despejado.
```

La fortaleza de ReAct reside en su naturaleza reactiva e incremental: cada acción informa la siguiente. Su debilidad es que en tareas complejas puede perderse en cadenas de razonamiento largas o caer en bucles.

### 3.2 Plan-and-Execute

La arquitectura Plan-and-Execute separa explícitamente la fase de planificación de la fase de ejecución. En lugar de razonar paso a paso sobre la marcha, el agente comienza generando un plan completo antes de ejecutar ninguna acción.

**Fase de planificación:** Un LLM (el planificador) recibe el objetivo y genera una lista ordenada de pasos a ejecutar. Este plan puede ser revisado o validado antes de comenzar la ejecución.

**Fase de ejecución:** Un LLM ejecutor (que puede ser el mismo modelo u otro) lleva a cabo cada paso del plan, usando las herramientas disponibles. Si un paso falla o el contexto cambia, el planificador puede ser invocado de nuevo para replantear.

Esta separación ofrece ventajas claras en tareas de larga duración: el plan actúa como una hoja de ruta que mantiene la coherencia global incluso cuando los pasos individuales son complejos. Es especialmente útil en escenarios de investigación automatizada, generación de informes o flujos de trabajo multi-etapa con dependencias claras entre pasos.

### 3.3 Reflexion: auto-evaluación y corrección

Reflexion (Shinn et al., 2023) introduce un mecanismo de memoria episódica y auto-evaluación que permite al agente aprender de sus propios errores dentro de una sesión o entre sesiones. El ciclo añade una capa adicional al bucle estándar:

1. El agente intenta resolver la tarea (usando ReAct u otro método).
2. Un evaluador (que puede ser el mismo LLM) analiza el resultado y determina si fue exitoso.
3. Si el resultado es insatisfactorio, el agente genera una reflexión verbal: un diagnóstico de qué salió mal y cómo debería haber actuado de forma diferente.
4. Esta reflexión se almacena en una memoria episódica y se incluye en el contexto de los intentos siguientes.

Reflexion es particularmente poderoso en dominios donde el feedback es claro (por ejemplo, código que debe pasar tests, o respuestas que pueden verificarse contra una fuente de verdad). Su limitación es el coste en tokens y latencia, ya que cada iteración implica múltiples llamadas al modelo.

### 3.4 Comparativa de arquitecturas

| Arquitectura | Fortaleza principal | Debilidad principal | Casos de uso ideales |
|---|---|---|---|
| ReAct | Adaptabilidad incremental | Pérdida de coherencia en tareas largas | QA con herramientas, asistentes conversacionales |
| Plan-and-Execute | Coherencia global, trazabilidad | Rigidez si el plan inicial es incorrecto | Workflows multi-etapa, generación de informes |
| Reflexion | Auto-mejora iterativa | Alto coste en tokens y latencia | Debugging de código, optimización iterativa |

---

## 4. Function calling y tool use

### 4.1 El mecanismo de function calling

Function calling es el mecanismo técnico que permite a un LLM invocar funciones externas de forma estructurada. En lugar de generar texto libre, el modelo produce una salida estructurada (JSON) que especifica qué función llamar y con qué argumentos. El sistema que aloja al modelo ejecuta la función, obtiene el resultado y lo devuelve al modelo para que continúe el razonamiento.

**OpenAI API:** En la API de OpenAI, las herramientas se definen en el parámetro `tools` de la petición. Cuando el modelo decide usar una herramienta, devuelve un mensaje con `finish_reason: "tool_calls"` y un objeto `tool_calls` con el nombre de la función y los argumentos en JSON.

```python
import openai

client = openai.OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Obtiene la temperatura actual de una ciudad",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Nombre de la ciudad"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Unidad de temperatura"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "¿Qué temperatura hace en Madrid?"}],
    tools=tools
)
```

**Anthropic API (tool_use):** Anthropic implementa el mismo concepto bajo el nombre `tool_use`. Las herramientas se definen en el parámetro `tools` y el modelo responde con un bloque de tipo `tool_use` en el contenido del mensaje.

```python
import anthropic

client = anthropic.Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "Obtiene la temperatura actual de una ciudad",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "Nombre de la ciudad"},
                "units": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["city"]
        }
    }
]

response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "¿Qué temperatura hace en Madrid?"}]
)
```

### 4.2 Definición de herramientas con JSON Schema

La definición precisa de herramientas con JSON Schema es crítica para el rendimiento del agente. Un schema bien escrito reduce la ambigüedad, previene errores de parámetros y guía al modelo hacia el uso correcto. Los elementos clave son:

- **name:** Identificador único de la función. Debe ser descriptivo y seguir convenciones de nomenclatura claras (snake_case).
- **description:** Explicación de qué hace la herramienta, cuándo usarla y qué no hace. Esta descripción es leída por el LLM y afecta directamente a la calidad de las decisiones de uso.
- **parameters:** Schema JSON que define los argumentos: tipos, descripciones, valores posibles (enum) y campos obligatorios (required).

### 4.3 Ejemplo completo: agente meteorológico

El siguiente ejemplo ilustra un agente que consulta la temperatura de una ciudad, convierte unidades y guarda el resultado en un archivo:

```python
import json
import openai

client = openai.OpenAI()

# Implementaciones simuladas de las herramientas
def get_weather(city: str, units: str = "celsius") -> dict:
    # En producción: llamada real a una API meteorológica
    return {"city": city, "temperature": 28, "units": units, "condition": "sunny"}

def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    if from_unit == "celsius" and to_unit == "fahrenheit":
        return value * 9/5 + 32
    elif from_unit == "fahrenheit" and to_unit == "celsius":
        return (value - 32) * 5/9
    return value

def save_to_file(filename: str, content: str) -> str:
    with open(filename, "w") as f:
        f.write(content)
    return f"Guardado en {filename}"

TOOL_IMPLEMENTATIONS = {
    "get_weather": get_weather,
    "convert_temperature": convert_temperature,
    "save_to_file": save_to_file
}

def run_agent(user_message: str):
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS_SCHEMA
        )
        
        message = response.choices[0].message
        
        if message.finish_reason == "stop":
            return message.content
        
        if message.finish_reason == "tool_calls":
            messages.append(message)
            
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                try:
                    result = TOOL_IMPLEMENTATIONS[func_name](**args)
                except Exception as e:
                    result = {"error": str(e)}
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
```

### 4.4 Manejo de errores en tool calls

Los errores en tool calls son inevitables en producción. Las estrategias clave incluyen:

- **Captura y reporte estructurado:** Devolver el error como un objeto JSON con campos `error` y `message` en lugar de lanzar excepciones que corten el flujo.
- **Reintentos con contexto:** Si una herramienta falla, incluir el error en el contexto para que el modelo pueda intentar una llamada diferente o una alternativa.
- **Validación de argumentos antes de ejecutar:** Verificar tipos y rangos antes de llamar a sistemas externos para evitar efectos secundarios no deseados.

### 4.5 Parallel tool use

Tanto OpenAI como Anthropic soportan la invocación paralela de herramientas. Cuando el modelo identifica que múltiples herramientas pueden ejecutarse de forma independiente, puede devolver varias tool_calls en un mismo turno. El sistema ejecuta todas en paralelo y devuelve los resultados de forma conjunta, reduciendo la latencia total del ciclo agéntico.

---

## 5. Herramientas de agentes

Un agente es tan capaz como las herramientas que tiene disponibles. El diseño del toolkit es una decisión arquitectónica fundamental.

### 5.1 Búsqueda web

**Tavily:** API diseñada específicamente para agentes de IA. Devuelve resultados estructurados y optimizados para LLMs, con soporte para búsqueda de noticias recientes y contenido extraído de páginas web.

**SerpAPI:** Wrapper sobre motores de búsqueda como Google, Bing y DuckDuckGo. Ofrece resultados de búsqueda orgánicos, noticias, imágenes y respuestas directas (answer boxes).

La búsqueda web es la herramienta más crítica para superar la limitación del conocimiento de corte (knowledge cutoff) de los LLMs. Un agente con acceso a búsqueda puede responder preguntas sobre eventos recientes, verificar datos y rastrear fuentes.

### 5.2 Ejecución de código (Python REPL sandbox)

Permite al agente ejecutar código Python y observar la salida. Es esencial para cálculos complejos, manipulación de datos, generación de gráficos y cualquier tarea que requiera precisión computacional que los LLMs no pueden garantizar por sí mismos.

El sandboxing es imprescindible: la ejecución debe ocurrir en un entorno aislado (contenedor Docker, E2B, etc.) con límites de tiempo, memoria y sin acceso a recursos del sistema anfitrión salvo los explícitamente permitidos.

### 5.3 Consultas a bases de datos (SQL via función)

Una herramienta `query_database(sql: str)` permite al agente consultar bases de datos relacionales. La descripción de la herramienta debe incluir el schema de las tablas disponibles para que el modelo pueda construir queries válidas. Se recomienda restringir las operaciones a SELECT y prohibir DDL/DML destructivo salvo casos muy controlados.

### 5.4 Lectura y escritura de archivos

Herramientas `read_file(path: str)` y `write_file(path: str, content: str)` permiten al agente trabajar con el sistema de archivos local. Deben implementarse con controles estrictos de rutas permitidas para prevenir accesos no autorizados.

### 5.5 Llamadas a APIs externas

El agente puede interactuar con cualquier servicio externo mediante HTTP. Desde calendarios (Google Calendar API) hasta CRMs (Salesforce), pasando por servicios de pago (Stripe) o comunicaciones (Slack, email). Cada API debe encapsularse como una herramienta bien descrita con schema JSON.

### 5.6 Generación de imágenes

Herramientas que llaman a modelos de imagen (DALL-E, Stable Diffusion) permiten al agente producir contenido visual como parte de su flujo de trabajo. Útil en agentes de marketing, diseño automatizado o generación de informes visuales.

### 5.7 Ejemplo de toolkit completo con LangChain

```python
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.tools import PythonREPLTool
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent

tools = [
    TavilySearchResults(max_results=3),
    PythonREPLTool(),
    Tool(
        name="query_database",
        func=execute_sql_query,
        description="Ejecuta queries SQL de solo lectura contra la base de datos de ventas. Schema disponible: ventas(id, fecha, producto, cantidad, precio)"
    ),
    Tool(
        name="save_report",
        func=save_report_to_file,
        description="Guarda un informe en formato Markdown en el directorio de informes"
    )
]

llm = ChatOpenAI(model="gpt-4o", temperature=0)
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

---

## 6. Frameworks de orquestación

### 6.1 LangGraph

LangGraph es un framework de orquestación de agentes basado en grafos de estado dirigidos. A diferencia de las cadenas lineales de LangChain, LangGraph permite flujos con ciclos, ramas condicionales y paralelismo.

**Conceptos clave:**
- **Estado (State):** Un diccionario tipado que fluye entre nodos y acumula información a lo largo de la ejecución.
- **Nodos:** Funciones Python que reciben el estado actual, realizan una operación (llamar al LLM, ejecutar una herramienta, transformar datos) y devuelven un estado actualizado.
- **Edges (aristas):** Conexiones entre nodos. Pueden ser directas o condicionales, permitiendo bifurcaciones basadas en el estado.

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    next_step: str

def call_model(state: AgentState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def call_tool(state: AgentState):
    last_message = state["messages"][-1]
    tool_result = execute_tool(last_message.tool_calls[0])
    return {"messages": [tool_result]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool"
    return END

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tool", call_tool)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"tool": "tool", END: END})
workflow.add_edge("tool", "agent")

app = workflow.compile()
```

LangGraph destaca por su capacidad para modelar flujos de trabajo complejos con persistencia de estado, checkpointing y soporte nativo para sistemas multiagente.

### 6.2 AutoGen (Microsoft)

AutoGen es un framework de Microsoft Research orientado a la conversación entre múltiples agentes. Su modelo fundamental es el de agentes que se comunican mediante mensajes en una conversación estructurada.

**Tipos de agentes en AutoGen:**
- **AssistantAgent:** Agente basado en LLM que puede generar código, planificar y razonar.
- **UserProxyAgent:** Actúa como proxy del usuario humano. Puede ejecutar código automáticamente o requerir confirmación humana.
- **GroupChatManager:** Coordina conversaciones entre múltiples agentes, decidiendo el turno de cada uno.

```python
import autogen

config_list = [{"model": "gpt-4o", "api_key": "..."}]

planner = autogen.AssistantAgent(
    name="Planner",
    system_message="Eres un planificador. Descompones tareas complejas en pasos.",
    llm_config={"config_list": config_list}
)

coder = autogen.AssistantAgent(
    name="Coder",
    system_message="Eres un programador experto en Python. Implementas lo que el planificador define.",
    llm_config={"config_list": config_list}
)

critic = autogen.AssistantAgent(
    name="Critic",
    system_message="Revisas código y planes, señalando errores y mejoras.",
    llm_config={"config_list": config_list}
)

user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "workspace", "use_docker": True}
)

groupchat = autogen.GroupChat(agents=[planner, coder, critic, user_proxy], messages=[], max_round=12)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})

user_proxy.initiate_chat(manager, message="Analiza el dataset ventas.csv y genera un informe con los 5 productos más vendidos")
```

### 6.3 CrewAI

CrewAI introduce una abstracción de más alto nivel inspirada en el trabajo en equipo: crews (equipos), agents (agentes con roles definidos) y tasks (tareas asignables).

```python
from crewai import Agent, Task, Crew, Process

investigador = Agent(
    role="Investigador de mercado",
    goal="Recopilar información actualizada y relevante sobre el tema asignado",
    backstory="Analista con experiencia en investigación de mercado y fuentes digitales",
    tools=[TavilySearchResults()],
    verbose=True
)

redactor = Agent(
    role="Redactor de contenido",
    goal="Transformar la investigación en contenido claro y atractivo",
    backstory="Periodista con experiencia en divulgación tecnológica",
    verbose=True
)

tarea_investigacion = Task(
    description="Investiga las últimas tendencias en IA generativa para empresas en 2025",
    expected_output="Resumen estructurado con 5 tendencias clave, fuentes y datos relevantes",
    agent=investigador
)

tarea_redaccion = Task(
    description="Escribe un artículo de 800 palabras basado en la investigación proporcionada",
    expected_output="Artículo en Markdown listo para publicar",
    agent=redactor,
    context=[tarea_investigacion]
)

crew = Crew(
    agents=[investigador, redactor],
    tasks=[tarea_investigacion, tarea_redaccion],
    process=Process.sequential,
    verbose=True
)

resultado = crew.kickoff()
```

### 6.4 Comparativa de frameworks

| Framework | Modelo mental | Punto fuerte | Curva de aprendizaje | Mejor para |
|---|---|---|---|---|
| LangGraph | Grafo de estado | Control fino de flujos complejos | Alta | Flujos de producción con ramificaciones |
| AutoGen | Conversación multiagente | Naturalidad en colaboración entre agentes | Media | Tareas de investigación y generación de código |
| CrewAI | Equipo con roles | Facilidad de configuración de alto nivel | Baja | Prototipos rápidos y workflows creativos |

---

## 7. Memoria en agentes

La memoria es lo que distingue a un agente verdaderamente útil de uno que "olvida" todo al final de cada turno. Existen varios tipos de memoria con características y usos distintos.

### 7.1 Memoria a corto plazo (conversational buffer)

Es la forma más simple: el historial completo de la conversación se incluye en el contexto de cada nueva llamada al LLM. Efectiva para conversaciones cortas, pero limitada por la ventana de contexto del modelo. Cuando la conversación supera el límite de tokens, el buffer debe truncarse o resumirse.

**ConversationBufferMemory en LangChain:**

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(return_messages=True)
memory.chat_memory.add_user_message("¿Cuál es la capital de Francia?")
memory.chat_memory.add_ai_message("La capital de Francia es París.")
```

Para gestionar ventanas de contexto largas, `ConversationBufferWindowMemory` mantiene solo los últimos k intercambios, y `ConversationSummaryMemory` usa un LLM para comprimir el historial en un resumen progresivo.

### 7.2 Memoria a largo plazo (vector store memory)

La memoria semántica a largo plazo permite al agente recuperar información relevante de interacciones pasadas usando búsqueda por similaridad vectorial. El proceso es:

1. Las interacciones pasadas se codifican como embeddings y se almacenan en una base de datos vectorial (Chroma, Pinecone, Weaviate, etc.).
2. Antes de cada nueva interacción, se realiza una búsqueda semántica para recuperar los recuerdos más relevantes según el contexto actual.
3. Los recuerdos recuperados se incluyen en el prompt del agente.

```python
from langchain.memory import VectorStoreRetrieverMemory
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

embeddings = OpenAIEmbeddings()
vectorstore = Chroma(embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

memory = VectorStoreRetrieverMemory(retriever=retriever)
```

### 7.3 Memoria episódica

La memoria episódica registra secuencias completas de eventos con su contexto temporal: qué hizo el agente, qué resultado obtuvo, qué funcionó y qué no. Es la base del mecanismo de Reflexion: el agente puede recuperar "episodios" anteriores similares para informar su estrategia actual. Se implementa típicamente como una combinación de almacenamiento estructurado (base de datos) y recuperación vectorial.

---

## 8. Sistemas multi-agente

A medida que las tareas se vuelven más complejas, un solo agente puede resultar insuficiente. Los sistemas multiagente distribuyen el trabajo entre agentes especializados que colaboran para alcanzar objetivos compartidos.

### 8.1 Patrón supervisor + workers

Un agente orquestador (supervisor) recibe el objetivo global y lo descompone en subtareas. Asigna cada subtarea a un agente worker especializado, recoge los resultados y los integra. Este patrón es jerárquico y predecible, y se adapta bien a flujos de trabajo con etapas claramente definidas.

El supervisor puede decidir dinámicamente qué worker invocar según el estado de la tarea, y puede re-asignar si un worker falla o devuelve resultados insatisfactorios.

### 8.2 Colaboración peer-to-peer

En este modelo no hay jerarquía: los agentes se comunican directamente entre sí mediante mensajes, negociando roles y responsabilidades. Es más flexible que el modelo supervisor-worker pero más difícil de controlar y depurar. AutoGen implementa este patrón de forma natural con su GroupChat.

### 8.3 Pipeline de agentes especializados

Los agentes están conectados en secuencia, donde la salida de uno es la entrada del siguiente. Por ejemplo: Agente de investigación → Agente de análisis → Agente de síntesis → Agente de formateo. Cada agente es experto en una tarea específica y el pipeline garantiza que cada etapa se complete antes de la siguiente.

### 8.4 Coordinación y comunicación entre agentes

Los agentes pueden comunicarse mediante:
- **Mensajes directos:** Paso de texto o datos estructurados entre agentes.
- **Estado compartido:** Un diccionario o base de datos compartida que todos los agentes pueden leer y escribir (patrón de LangGraph).
- **Cola de tareas:** Un sistema de mensajería (Redis, RabbitMQ) para coordinar agentes en sistemas distribuidos de alta escala.

### 8.5 Evaluación de sistemas multiagente

Evaluar sistemas multiagente requiere métricas en múltiples niveles:
- **Métricas de tarea:** ¿Se completó el objetivo? ¿Con qué calidad?
- **Métricas de eficiencia:** Número de pasos, tokens consumidos, tiempo total.
- **Métricas de coordinación:** ¿Hubo conflictos entre agentes? ¿Se repitió trabajo innecesariamente?
- **Trazabilidad:** Capacidad de reconstruir qué agente tomó qué decisión y por qué.

Herramientas como LangSmith, Weights & Biases o Arize AI permiten trazar y monitorizar el comportamiento de sistemas multiagente en producción.

---

## 9. Seguridad en agentes

Los agentes introducen riesgos de seguridad cualitativamente distintos a los de los chatbots convencionales. Un chatbot que genera texto incorrecto produce daño limitado. Un agente que ejecuta acciones incorrectas puede modificar bases de datos, enviar emails, ejecutar código malicioso o consumir recursos de forma descontrolada.

### 9.1 Riesgos específicos

**Prompt injection en tool outputs:** Un atacante puede inyectar instrucciones maliciosas en el resultado de una herramienta (por ejemplo, en el contenido de una página web que el agente lee). El modelo puede interpretar estas instrucciones como órdenes legítimas y ejecutar acciones no autorizadas. Mitigación: sanitizar los outputs de herramientas antes de incluirlos en el contexto; usar system prompts robustos que adviertan al modelo sobre este riesgo.

**Ejecución de código malicioso:** Si el agente tiene acceso a un intérprete de código, un prompt adversarial puede hacer que genere y ejecute código dañino. Mitigación: sandboxing estricto con límites de recursos, red desconectada por defecto y lista blanca de operaciones permitidas.

**Acciones irreversibles:** Eliminar registros, enviar comunicaciones, realizar transacciones financieras. Una vez ejecutadas, estas acciones pueden ser imposibles o muy costosas de revertir. Mitigación: patrón human-in-the-loop, confirmación explícita antes de acciones destructivas, operaciones en modo "dry run" antes de ejecutar en producción.

**Escalada de privilegios:** El agente podría intentar acceder a herramientas o recursos más allá de los necesarios para la tarea. Mitigación: principio de mínimo privilegio en el diseño del toolkit.

**Fuga de información:** El agente podría exponer datos sensibles en sus respuestas o logs. Mitigación: filtrado de PII en outputs, control de acceso a herramientas con datos confidenciales.

### 9.2 Principio de mínimo privilegio

Cada agente debe tener acceso únicamente a las herramientas y datos estrictamente necesarios para su función. Un agente de atención al cliente no necesita acceso de escritura a la base de datos de producción. Un agente de análisis no necesita capacidad de enviar emails. El diseño del toolkit debe ser conservador: es mejor añadir capacidades según sea necesario que restringirlas después de un incidente.

### 9.3 Sandboxing

La ejecución de código generado por el agente debe ocurrir en un entorno completamente aislado del sistema anfitrión. Opciones recomendadas:

- **Docker containers** con acceso de red bloqueado y límites de CPU/memoria.
- **E2B (e2b.dev):** Sandbox en la nube diseñado específicamente para agentes de IA, con soporte para Python y otros lenguajes.
- **Pyodide:** Ejecución de Python en WebAssembly, con aislamiento inherente al modelo de seguridad del navegador.

### 9.4 Human-in-the-loop para acciones críticas

No todas las acciones de un agente deben ejecutarse de forma autónoma. Para acciones de alto impacto, el patrón human-in-the-loop introduce un punto de confirmación donde un humano aprueba o rechaza la acción antes de ejecutarla. En LangGraph, esto se implementa mediante interrupts; en AutoGen, mediante la configuración `human_input_mode`.

La decisión de qué acciones requieren aprobación humana debe ser explícita en el diseño del sistema, no una decisión ad hoc. Un buen criterio: cualquier acción que modifique estado externo de forma difícilmente reversible requiere aprobación humana.

---

## 10. Actividades prácticas

### Actividad 1: Agente ReAct con herramientas básicas

Implementa un agente ReAct utilizando LangChain y la API de OpenAI (o Anthropic) que sea capaz de responder preguntas que requieran al menos dos pasos: búsqueda web y cálculo. El agente debe mostrar el ciclo Thought-Action-Observation completo con `verbose=True`. Valida el funcionamiento con al menos tres preguntas de complejidad creciente.

**Criterios de evaluación:** Correcta definición de herramientas con JSON Schema; ciclo ReAct visible y coherente; manejo de errores cuando una herramienta falla; respuesta final correcta y bien fundamentada.

### Actividad 2: Sistema multiagente con LangGraph

Diseña e implementa un sistema de dos agentes orquestados con LangGraph para automatizar la generación de un informe de análisis de datos. El primer agente (analista) lee un archivo CSV, realiza cálculos estadísticos básicos con Python REPL y extrae insights clave. El segundo agente (redactor) toma esos insights y genera un informe en Markdown estructurado. El grafo debe incluir al menos un edge condicional.

**Criterios de evaluación:** Correcto modelado del estado compartido; transición condicional funcionando; los dos agentes cumplen roles distintos sin solapamiento; el informe final es coherente y está bien estructurado.

### Actividad 3: Crew de investigación con CrewAI

Configura un crew de tres agentes en CrewAI para realizar una investigación competitiva sobre un sector de tu elección: un investigador (con acceso a búsqueda web), un analista (que procesa y estructura la información) y un estratega (que deriva recomendaciones accionables). Define roles, backstories y tasks con expected_outputs claros. Ejecuta el crew y evalúa la calidad de la colaboración entre agentes.

**Criterios de evaluación:** Roles claramente diferenciados y sin redundancia; tasks con dependencias correctamente configuradas (context); output final integrado y coherente; reflexión sobre qué mejorarías en el diseño del crew.

### Actividad 4: Auditoría de seguridad de un agente

Dado un agente de ejemplo con acceso a herramientas de filesystem, ejecución de código y envío de emails, realiza una auditoría de seguridad identificando: (a) al menos tres vectores de prompt injection realistas, (b) las acciones irreversibles que el agente puede ejecutar, (c) un análisis del toolkit según el principio de mínimo privilegio. Propón un rediseño del sistema con las mitigaciones correspondientes, incluyendo la definición de qué acciones requieren human-in-the-loop.

**Criterios de evaluación:** Identificación realista y técnicamente fundamentada de los vectores de ataque; propuesta de mitigación concreta y viable; rediseño del toolkit con privilegios reducidos; argumentación clara de los puntos de control humano.

---

## 11. Referencias

### Artículos académicos

- Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2022). **ReAct: Synergizing Reasoning and Acting in Language Models**. arXiv:2210.03629. [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)

- Shinn, N., Cassano, F., Labash, B., Gopinath, A., Narasimhan, K., & Yao, S. (2023). **Reflexion: Language Agents with Verbal Reinforcement Learning**. arXiv:2303.11366. [https://arxiv.org/abs/2303.11366](https://arxiv.org/abs/2303.11366)

- Wang, L., Ma, C., Feng, X., Zhang, Z., Yang, H., Zhang, J., ... & Wen, J. R. (2023). **A Survey on Large Language Model based Autonomous Agents**. arXiv:2308.11432. [https://arxiv.org/abs/2308.11432](https://arxiv.org/abs/2308.11432)

- Wu, Q., Bansal, G., Zhang, J., Wu, Y., Li, B., Zhu, E., ... & Wang, C. (2023). **AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation**. arXiv:2308.08155. [https://arxiv.org/abs/2308.08155](https://arxiv.org/abs/2308.08155)

### Documentación oficial de frameworks

- **LangGraph Documentation.** LangChain, Inc. [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)

- **LangGraph Tutorials — Building Agents.** [https://langchain-ai.github.io/langgraph/tutorials/](https://langchain-ai.github.io/langgraph/tutorials/)

- **AutoGen Documentation.** Microsoft Research. [https://microsoft.github.io/autogen/](https://microsoft.github.io/autogen/)

- **CrewAI Documentation.** CrewAI, Inc. [https://docs.crewai.com/](https://docs.crewai.com/)

- **CrewAI — Concepts: Agents, Tasks, Crews.** [https://docs.crewai.com/concepts/agents](https://docs.crewai.com/concepts/agents)

### Documentación de APIs

- **OpenAI — Function Calling.** [https://platform.openai.com/docs/guides/function-calling](https://platform.openai.com/docs/guides/function-calling)

- **OpenAI — Parallel Function Calling.** [https://platform.openai.com/docs/guides/function-calling#parallel-function-calling](https://platform.openai.com/docs/guides/function-calling#parallel-function-calling)

- **Anthropic — Tool Use (Function Calling).** [https://docs.anthropic.com/en/docs/build-with-claude/tool-use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)

- **Anthropic — Tool Use Best Practices.** [https://docs.anthropic.com/en/docs/build-with-claude/tool-use/best-practices-for-tool-definitions](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/best-practices-for-tool-definitions)

### Recursos adicionales

- **LangSmith — Observability for LLM Applications.** LangChain, Inc. [https://docs.smith.langchain.com/](https://docs.smith.langchain.com/)

- **E2B — Sandboxed Code Execution for AI Agents.** [https://e2b.dev/docs](https://e2b.dev/docs)

- **Tavily AI — Search API for AI Agents.** [https://docs.tavily.com/](https://docs.tavily.com/)

- **OWASP LLM Top 10.** OWASP Foundation. [https://owasp.org/www-project-top-10-for-large-language-model-applications/](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — Referencia esencial para seguridad en sistemas basados en LLMs, incluyendo prompt injection (LLM01) y acciones de agentes inseguras (LLM08).

---

*Unidad didáctica perteneciente al módulo MP04 — Soluciones LLM, dentro del Ciclo Formativo Superior CFS1 — Gestión de Datos y Entrenamiento IA.*
