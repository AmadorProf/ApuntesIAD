---
marp: true
theme: default
paginate: true
size: 16:9
header: 'MP04 · UD4 · Comportamientos agenticos'
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

# UD4 · Comportamientos agenticos

**MP04 · Soluciones basadas en LLMs**
CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno sera capaz de:

- Definir los objetivos, alcance y condiciones de finalizacion de un agente LLM.
- Configurar las herramientas y la memoria operativa del agente con sus ciclos de vida.
- Establecer limites de autonomia claros: acciones permitidas, prohibidas y que requieren confirmacion humana.
- Implementar protocolos de escalado y parada segura ante comportamientos inesperados.
- Validar la logica operativa del agente ante escenarios adversos y bucles.

---

## 1 · Conceptos fundamentales de agentes LLM

### Que es un agente LLM

Un agente LLM es un sistema en el que el modelo de lenguaje actua como motor de razonamiento para decidir que acciones ejecutar en un bucle iterativo hasta alcanzar un objetivo.

**Diferencia entre asistente y agente:**

| Caracteristica | Asistente conversacional | Agente autonomo |
|---|---|---|
| **Ciclo de ejecucion** | Una vuelta por turno | Multiples pasos hasta completar el objetivo |
| **Uso de herramientas** | Opcional, a peticion del usuario | Decidido autonomamente por el modelo |
| **Memoria** | Historial de conversacion | Memoria operativa + estado de la tarea |
| **Autonomia** | Baja: el humano guia cada paso | Alta: el agente planifica y ejecuta |
| **Reversibilidad** | Siempre: solo genera texto | Variable: puede ejecutar acciones irreversibles |

---

## 1 · Objetivos y tareas del agente (I)

### Definicion del objetivo y alcance

El objetivo de un agente debe definirse con tres elementos:

1. **Que debe conseguir** (objetivo funcional): "Analizar el informe de ventas del mes y generar un resumen ejecutivo con las tres alertas principales."

2. **Que esta fuera del alcance** (exclusiones): "No enviar correos ni modificar datos. Solo lectura y generacion de texto."

3. **Como saber que ha terminado** (condicion de finalizacion):
   - Objetivo completado satisfactoriamente
   - Numero maximo de pasos alcanzado
   - Error irrecuperable detectado
   - Solicitud de intervencion humana

```python
OBJETIVO = {
    "descripcion": "Analizar el informe de ventas y generar resumen ejecutivo",
    "max_pasos": 10,
    "condiciones_fin": ["resumen_generado", "error_critico", "requiere_humano"],
    "acciones_permitidas": ["leer_archivo", "calcular", "generar_texto"],
    "acciones_prohibidas": ["modificar_datos", "enviar_email", "acceso_internet"]
}
```

---

## 1 · Objetivos y tareas del agente (II)

### Estructura de pasos y condiciones de escalado

Un agente ejecuta un plan de pasos. Cada paso puede generar nueva informacion que modifica los siguientes:

```
[Objetivo recibido]
        |
        v
[Planificacion] → el agente descompone el objetivo en subtareas
        |
        v
[Bucle de ejecucion]
 1. Razonar: ¿que debo hacer ahora?
 2. Seleccionar herramienta: ¿cual usar y con que argumentos?
 3. Ejecutar herramienta: obtener resultado
 4. Observar: ¿el resultado avanza hacia el objetivo?
 5. ¿Condicion de fin? → Si: terminar | No: volver a 1
        |
        v
[Resultado final o escalado]
```

**Condiciones de escalado a humano:**
- El agente lleva N pasos sin avanzar (bucle detectado)
- Se detecta una accion que requiere confirmacion humana
- La confianza en la siguiente accion esta por debajo del umbral

---

## 2 · Herramientas y memoria operativa (I)

### Catalogo de herramientas del agente

Las herramientas definen lo que el agente puede hacer. Cada herramienta debe documentarse con:

```python
HERRAMIENTAS = [
    {
        "name": "leer_archivo",
        "description": "Lee el contenido de un archivo del sistema de archivos local. Solo lectura.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ruta": {"type": "string", "description": "Ruta absoluta del archivo"},
                "encoding": {"type": "string", "default": "utf-8"}
            },
            "required": ["ruta"]
        }
    },
    {
        "name": "ejecutar_sql",
        "description": "Ejecuta una consulta SELECT en la base de datos de solo lectura.",
        "input_schema": {
            "type": "object",
            "properties": {
                "consulta": {"type": "string", "description": "Consulta SQL (solo SELECT permitido)"}
            },
            "required": ["consulta"]
        }
    }
]
```

---

## 2 · Herramientas y memoria operativa (II)

### Tipos de memoria en un agente

| Tipo de memoria | Alcance | Implementacion | Ciclo de vida |
|---|---|---|---|
| **Memoria de trabajo** | Dentro de una ejecucion | Variables en memoria RAM | Se descarta al terminar la tarea |
| **Memoria episodica** | Entre ejecuciones del mismo agente | Base de datos, ficheros | Conserva por X dias o hasta completar el proyecto |
| **Memoria semantica** | Conocimiento general del agente | Base de datos vectorial (RAG) | Persistente, se actualiza periodicamente |
| **Memoria de herramientas** | Resultados de herramientas previas | Context window del agente | Dura la ejecucion actual |

**Proteccion de datos en la memoria:**
- La memoria episodica puede contener datos personales → aplicar minimizacion y anonimizacion
- Definir politica de retencion: cuanto tiempo se conserva y como se elimina
- Acceso a la memoria restringido al agente que la creo (separacion de datos entre usuarios)

---

## 2 · Herramientas y memoria operativa (III)

### Implementacion del bucle agente (ReAct pattern)

```python
import anthropic

client = anthropic.Anthropic()
MAX_PASOS = 10

def ejecutar_agente(objetivo: str, herramientas: list) -> str:
    mensajes = [{"role": "user", "content": objetivo}]

    for paso in range(MAX_PASOS):
        respuesta = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2048,
            tools=herramientas,
            messages=mensajes
        )

        if respuesta.stop_reason == "end_turn":
            # El agente ha terminado
            return respuesta.content[0].text

        if respuesta.stop_reason == "tool_use":
            # Ejecutar la herramienta solicitada
            llamada = next(b for b in respuesta.content if b.type == "tool_use")
            resultado = ejecutar_herramienta(llamada.name, llamada.input)
            # Anadir resultado al historial y continuar
            mensajes += [
                {"role": "assistant", "content": respuesta.content},
                {"role": "user", "content": [{"type": "tool_result",
                    "tool_use_id": llamada.id, "content": str(resultado)}]}
            ]

    return "ERROR: Maximo de pasos alcanzado sin completar el objetivo"
```

---

## 3 · Limites de autonomia (I)

### Jerarquia de acciones

Toda accion que el agente puede ejecutar debe clasificarse en una de estas tres categorias:

```
NIVEL 1: ACCIONES PROHIBIDAS (nunca ejecutar)
  - Eliminar datos o archivos de produccion
  - Enviar comunicaciones externas sin revision humana
  - Modificar configuraciones de seguridad
  - Acceder a datos de usuarios distintos al propietario de la sesion

NIVEL 2: ACCIONES CON CONFIRMACION (requieren aprobacion humana)
  - Modificar datos en bases de datos de produccion
  - Realizar transacciones economicas
  - Enviar correos o notificaciones
  - Cualquier accion irreversible

NIVEL 3: ACCIONES AUTONOMAS (el agente ejecuta libremente)
  - Leer y analizar documentos
  - Generar texto, resumenes, informes
  - Calcular y procesar datos
  - Buscar informacion en fuentes indexadas
```

---

## 3 · Limites de autonomia (II)

### Umbrales de confianza y confirmacion humana

```python
UMBRAL_CONFIRMACION = 0.85  # Confianza minima para ejecutar sin confirmacion

def evaluar_accion(accion: str, confianza: float, args: dict) -> str:
    """Devuelve 'ejecutar', 'confirmar' o 'prohibida'."""
    if accion in ACCIONES_PROHIBIDAS:
        return "prohibida"

    if accion in ACCIONES_CON_CONFIRMACION:
        return "confirmar"

    if confianza < UMBRAL_CONFIRMACION:
        return "confirmar"  # Baja confianza → pedir confirmacion aunque sea autonoma

    return "ejecutar"

def solicitar_confirmacion(accion: str, args: dict) -> bool:
    """Presenta la accion al operador humano y espera confirmacion."""
    print(f"[CONFIRMACION REQUERIDA]")
    print(f"El agente quiere ejecutar: {accion}")
    print(f"Argumentos: {args}")
    respuesta = input("¿Autoriza esta accion? (s/n): ")
    return respuesta.lower() == "s"
```

---

## 3 · Limites de autonomia (III)

### Parada segura y reversion de acciones

El agente debe poder detenerse de forma segura en cualquier punto:

**Protocolo de parada:**
1. Guardar el estado actual de la tarea (progreso, herramientas ya ejecutadas, resultados parciales)
2. Registrar el motivo de la parada (timeout, error, solicitud humana, accion prohibida)
3. Notificar al operador con el estado y el punto donde se detuvo
4. No ejecutar ninguna accion adicional tras la senal de parada

**Reversion de acciones:**
- Solo es posible si la accion es reversible (la mayoria de escrituras no lo son)
- Para acciones de escritura: implementar transacciones o snapshots previos a la ejecucion
- Para acciones de comunicacion (emails, notificaciones): usar colas con retraso y ventana de cancelacion

```python
class RegistroTransaccional:
    def __init__(self):
        self.acciones = []

    def registrar(self, accion: str, args: dict, resultado: dict, reversible: bool):
        self.acciones.append({
            "accion": accion, "args": args,
            "resultado": resultado, "reversible": reversible,
            "timestamp": datetime.utcnow().isoformat()
        })
```

---

## 4 · Validacion del comportamiento agentico (I)

### Escenarios de prueba obligatorios

| Escenario | Que se prueba | Resultado esperado |
|---|---|---|
| **Instruccion contradictoria** | El objetivo dice X pero una herramienta devuelve Y | El agente detecta la contradiccion y pide aclaracion |
| **Bucle infinito** | El agente repite el mismo paso sin avanzar | Se activa el limite de pasos; se escala a humano |
| **Accion prohibida solicitada** | El objetivo implica una accion del Nivel 1 | El agente rechaza y explica por que |
| **Baja confianza** | El resultado de una herramienta es ambiguo | El agente solicita confirmacion antes de continuar |
| **Herramienta no disponible** | Una herramienta devuelve error de conexion | El agente reintenta N veces y luego escala |
| **Contexto agotado** | El agente acumula demasiado historial | El agente resume el contexto y continua |

---

## 4 · Validacion del comportamiento agentico (II)

### Deteccion de bucles y escenarios criticos

```python
from collections import Counter

def detectar_bucle(historial_acciones: list[str], ventana: int = 4) -> bool:
    """Detecta si el agente esta repitiendo las mismas acciones."""
    if len(historial_acciones) < ventana:
        return False

    ultimas = historial_acciones[-ventana:]
    conteo = Counter(ultimas)

    # Si la misma accion aparece mas de la mitad de las veces → bucle
    return any(v > ventana // 2 for v in conteo.values())

def evaluar_progreso(estado_anterior: dict, estado_actual: dict) -> bool:
    """Devuelve True si el agente ha avanzado hacia el objetivo."""
    return estado_actual != estado_anterior  # Simplificacion; adaptar al caso de uso
```

**Protocolo de escalado ante bucle detectado:**
1. Registrar las ultimas N acciones que se repiten
2. Detener el bucle de ejecucion
3. Notificar al operador con el estado actual y el historial de acciones
4. No reanudar sin intervencion humana

---

## Actividad practica · UD4

### Diseno y validacion de un agente de analisis de datos

**Enunciado:**

Disenha un agente LLM que analice un CSV de ventas y genere un informe semanal. El agente tiene acceso a tres herramientas: `leer_csv`, `calcular_estadisticas` y `generar_informe_pdf`.

**Tareas:**

1. Define el objetivo del agente con la estructura: descripcion, max_pasos, condiciones_fin, acciones_permitidas y acciones_prohibidas.
2. Documenta el schema de las tres herramientas en formato JSON.
3. Clasifica cada herramienta en el nivel de autonomia correspondiente (prohibida / con confirmacion / autonoma). Justifica.
4. Implementa la funcion `evaluar_accion` para este agente.
5. Define tres escenarios de prueba adversarial (instruccion contradictoria, bucle, herramienta con error) y describe el comportamiento esperado.
6. Escribe el pseudocodigo del bucle ReAct para este agente con el protocolo de parada segura.

**Entregable:** documento de diseno tecnico del agente (2 paginas) + codigo Python de la logica de control.

---

## Puntos clave · UD4

- Un agente LLM ejecuta un bucle de razonamiento-accion hasta alcanzar el objetivo; difiere de un asistente en autonomia y capacidad de ejecutar acciones.
- El objetivo debe especificar alcance, exclusiones y condicion de finalizacion; sin estos tres elementos el agente no puede operar de forma segura.
- Las herramientas se clasifican en tres niveles: prohibidas, con confirmacion humana y autonomas.
- La memoria operativa tiene ciclos de vida definidos; los datos personales que pasa por ella requieren proteccion especifica.
- Detectar bucles y actuar con umbrales de confianza son los dos mecanismos de seguridad mas importantes en produccion.
- Todo agente debe tener un protocolo de parada segura que preserve el estado y notifique al operador.

---

## Criterios de evaluacion · UD4

| Criterio | Indicadores de logro |
|---|---|
| **Define objetivos y limites de autonomia** | Documenta objetivo con alcance, exclusiones y condicion de fin; clasifica acciones en los tres niveles |
| **Parametriza herramientas y memoria** | Define schemas de herramientas; especifica ciclo de vida de la memoria y medidas de proteccion de datos |
| **Valida la logica operativa del agente** | Disenha y ejecuta los seis escenarios adversariales; implementa deteccion de bucles y protocolo de parada |

---

<!-- _class: lead -->

[← Volver a MP04](../index.md)
