---
marp: true
theme: default
paginate: true
size: 16:9
header: 'MP04 · UD2 · Componentes de interaccion con el modelo'
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

# UD2 · Componentes de interaccion con el modelo

**MP04 · Soluciones basadas en LLMs**
Apuntes de IA y Datos

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno sera capaz de:

- Disenar instrucciones y plantillas de prompt eficaces para distintos casos de uso.
- Gestionar el contexto de la conversacion de forma eficiente dentro de los limites de tokens.
- Implementar la comunicacion con el modelo mediante APIs y SDKs, controlando errores y limites de uso.
- Gestionar y transformar las salidas del modelo en los formatos requeridos por la aplicacion.
- Configurar flujos de asistentes conversacionales con historial y derivacion.

---

## 1 · Diseno de instrucciones y plantillas (I)

### Anatomia de un prompt efectivo

Un prompt bien estructurado tiene cuatro secciones diferenciadas:

| Seccion | Proposito | Ejemplo |
|---|---|---|
| **Mensaje de sistema** | Define rol, tono, restricciones y comportamiento global | "Eres un asistente juridico especializado en derecho laboral espanol..." |
| **Contexto de la tarea** | Informacion relevante para la consulta actual | Fragmento del contrato, datos del empleado... |
| **Instruccion** | La tarea concreta que debe realizar | "Extrae las clausulas de no competencia del siguiente contrato." |
| **Formato de salida** | Estructura que debe seguir la respuesta | "Devuelve un JSON con los campos: clausula, pagina, vigencia." |

---

## 1 · Diseno de instrucciones y plantillas (II)

### Tecnicas de prompting avanzado

**Zero-shot:** la instruccion sin ejemplos.
```
Clasifica el siguiente comentario como POSITIVO, NEGATIVO o NEUTRO.
Comentario: "El producto llego en buen estado pero tarde."
```

**Few-shot:** incluir ejemplos antes de la tarea.
```
Ejemplos:
Comentario: "Excelente servicio, repetire." → POSITIVO
Comentario: "Roto desde el primer dia." → NEGATIVO
Comentario: "Correcto, nada especial." → NEUTRO

Clasifica: "El empaquetado es bueno pero el precio es caro."
```

**Chain-of-Thought:** pedir razonamiento explicito antes de la respuesta final.
```
Piensa paso a paso antes de responder. Muestra tu razonamiento
entre etiquetas <razonamiento> y la respuesta final en <respuesta>.
```

---

## 1 · Diseno de instrucciones y plantillas (III)

### Gestion de restricciones y tono

El mensaje de sistema debe definir con precision:

- **Restricciones de contenido:** "No proporciones consejos medicos. Deriva siempre al medico."
- **Tono:** "Usa un tono formal y profesional. Evita contracciones informales."
- **Idioma:** "Responde siempre en espanol, independientemente del idioma de la pregunta."
- **Limites de alcance:** "Solo responde sobre los productos del catalogo adjunto. Si la pregunta no tiene relacion, indica que no puedes ayudar con eso."

**Plantillas parametrizables:**

```python
SYSTEM_TEMPLATE = """
Eres un asistente de {empresa} especializado en {dominio}.
Tu tono es {tono}. Responde siempre en {idioma}.
Solo tienes acceso a la siguiente informacion: {contexto_base}.
"""
```

Las plantillas permiten reutilizar la logica de instrucciones cambiando solo los parametros del caso de uso.

---

## 2 · Gestion del contexto (I)

### La ventana de contexto como recurso limitado

El contexto de un LLM es finito. Todo lo que se envia al modelo (sistema, historial, documentos, instruccion) consume tokens del limite disponible:

```
Ventana de contexto = tokens_sistema + tokens_historial + tokens_documentos + tokens_instruccion + tokens_respuesta
```

**Problemas frecuentes:**
- Superar el limite de tokens provoca truncacion o error
- Demasiado contexto irrelevante degrada la calidad de la respuesta
- Historial largo acumula tokens rapido en conversaciones prolongadas

**Estrategias de gestion:**
- Limitar el numero de turnos de historial conservados (ventana deslizante)
- Comprimir el historial antiguo con un resumen
- Priorizar la informacion mas reciente y relevante

---

## 2 · Gestion del contexto (II)

### Estrategias de compresion y priorizacion

**Ventana deslizante de historial:**
```python
MAX_HISTORIAL = 10  # maximo de mensajes a conservar

def recortar_historial(historial: list[dict]) -> list[dict]:
    if len(historial) > MAX_HISTORIAL:
        return historial[-MAX_HISTORIAL:]
    return historial
```

**Resumen automatico del historial:**
```python
def resumir_historial(historial: list[dict], cliente_llm) -> str:
    texto = "\n".join(f"{m['role']}: {m['content']}" for m in historial)
    resumen = cliente_llm.messages.create(
        model="claude-haiku-4-5",
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": f"Resume esta conversacion en 3 frases:\n{texto}"
        }]
    )
    return resumen.content[0].text
```

---

## 3 · Comunicacion con el modelo via API (I)

### SDKs y conectores principales

| Proveedor | SDK oficial | Lenguaje |
|---|---|---|
| Anthropic | `anthropic` | Python, TypeScript/JS |
| OpenAI | `openai` | Python, TypeScript/JS, .NET, Java |
| Google | `google-generativeai` / `vertexai` | Python, Java, Node |
| Modelos locales | `ollama`, `llama-cpp-python` | Python |
| Multi-proveedor | `litellm` | Python |

**Estructura basica de una llamada (Anthropic SDK):**

```python
import anthropic

client = anthropic.Anthropic(api_key="sk-ant-...")

mensaje = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    system="Eres un asistente tecnico especializado en redes.",
    messages=[
        {"role": "user", "content": "Explica que es BGP en dos parrafos."}
    ]
)
print(mensaje.content[0].text)
```

---

## 3 · Comunicacion con el modelo via API (II)

### Control de errores y reintentos

Los errores de API se clasifican en tres categorias:

| Tipo de error | Codigo HTTP | Accion recomendada |
|---|---|---|
| **Limite de tasa** (rate limit) | 429 | Reintentar con backoff exponencial |
| **Timeout** | 408 / 524 | Reintentar; aumentar timeout si persiste |
| **Error del servidor** | 500, 502, 503 | Reintentar hasta 3 veces; alertar si persiste |
| **Error de autenticacion** | 401 | No reintentar; revisar credenciales |
| **Entrada invalida** | 400 | No reintentar; corregir el prompt o parametros |

**Implementacion de reintentos con backoff exponencial:**

```python
import time, anthropic

def llamar_con_reintento(client, **kwargs, max_intentos=3):
    for intento in range(max_intentos):
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError:
            if intento < max_intentos - 1:
                time.sleep(2 ** intento)  # 1s, 2s, 4s
            else:
                raise
```

---

## 3 · Comunicacion con el modelo via API (III)

### Streaming y gestion de limites de uso

**Streaming** — mostrar la respuesta mientras se genera:

```python
with client.messages.stream(
    model="claude-opus-4-5",
    max_tokens=512,
    messages=[{"role": "user", "content": pregunta}]
) as stream:
    for texto in stream.text_stream:
        print(texto, end="", flush=True)
```

**Gestion de limites de uso:**
- Monitorizar el uso acumulado de tokens por periodo (diario / mensual)
- Implementar cuotas por usuario o por servicio
- Registrar cada llamada: timestamp, modelo, tokens entrada/salida, coste estimado, latencia

```python
# Ejemplo de log de uso
log_entry = {
    "timestamp": datetime.utcnow().isoformat(),
    "modelo": respuesta.model,
    "tokens_entrada": respuesta.usage.input_tokens,
    "tokens_salida": respuesta.usage.output_tokens,
    "coste_estimado_usd": calcular_coste(respuesta.usage, modelo=respuesta.model)
}
```

---

## 4 · Gestion de salidas (I)

### Formatos y esquemas de salida

| Formato | Cuando usarlo | Herramienta |
|---|---|---|
| **JSON estructurado** | Integracion con sistemas, extraccion de campos | `structured_output`, JSON schema |
| **Markdown** | Documentos, informes, respuestas de chat | Parseo con `markdown-it` u otros |
| **Texto libre** | Generacion de contenido, resumen, respuestas naturales | Sin estructura adicional |
| **XML / HTML** | Integracion con sistemas legacy | Parsing con `lxml`, `BeautifulSoup` |
| **CSV / tabla** | Exportacion de datos | Parseo con `pandas` |

**JSON Schema para salida estructurada (Anthropic tool use):**

```python
herramienta_extraccion = {
    "name": "extraer_contacto",
    "description": "Extrae datos de contacto del texto",
    "input_schema": {
        "type": "object",
        "properties": {
            "nombre": {"type": "string"},
            "email": {"type": "string"},
            "telefono": {"type": "string", "nullable": True}
        },
        "required": ["nombre", "email"]
    }
}
```

---

## 4 · Gestion de salidas (II)

### Validacion y transformacion

Toda salida del modelo debe validarse antes de usarla:

```python
import json
from jsonschema import validate, ValidationError

ESQUEMA = {
    "type": "object",
    "properties": {
        "resumen": {"type": "string", "minLength": 10},
        "puntos_clave": {"type": "array", "items": {"type": "string"}},
        "confianza": {"type": "number", "minimum": 0, "maximum": 1}
    },
    "required": ["resumen", "puntos_clave"]
}

def validar_salida(texto_modelo: str) -> dict:
    try:
        datos = json.loads(texto_modelo)
        validate(instance=datos, schema=ESQUEMA)
        return datos
    except json.JSONDecodeError:
        raise ValueError("La salida del modelo no es JSON valido")
    except ValidationError as e:
        raise ValueError(f"Salida no cumple el esquema: {e.message}")
```

---

## 5 · Asistentes conversacionales (I)

### Flujo de un asistente multiturno

Un asistente conversacional mantiene el estado de la conversacion entre mensajes:

```
Usuario envia mensaje
        |
        v
[Gestion del historial]
 - Anadir mensaje usuario al historial
 - Recortar si supera el limite
        |
        v
[Construccion del contexto]
 - Sistema + historial + documentos relevantes
        |
        v
[Llamada al modelo]
        |
        v
[Post-procesamiento de la respuesta]
 - Validar formato
 - Detectar si es respuesta de aclaracion
 - Detectar si requiere derivacion
        |
        v
Mostrar respuesta al usuario + actualizar historial
```

---

## 5 · Asistentes conversacionales (II)

### Respuestas de aclaracion y derivacion

**Cuando el modelo debe pedir aclaracion:**
- La pregunta es ambigua y hay multiples interpretaciones validas
- Falta informacion necesaria para completar la tarea
- La peticion supera el alcance definido

```python
INSTRUCCION_ACLARACION = """
Si la pregunta del usuario es ambigua o incompleta, pide la informacion
que falta en una sola pregunta clara. No intentes responder con suposiciones.
Formato de aclaracion: "Para ayudarte mejor, necesito saber: [pregunta]"
"""
```

**Criterios de derivacion a un humano:**
- El sistema detecta una queja formal o situacion de urgencia
- La confianza en la respuesta es insuficiente (requiere verificacion)
- El usuario lo solicita explicitamente

```python
PALABRAS_DERIVACION = ["urgente", "reclamacion", "queja formal", "hablar con persona"]

def requiere_derivacion(mensaje_usuario: str) -> bool:
    return any(p in mensaje_usuario.lower() for p in PALABRAS_DERIVACION)
```

---

## 6 · Registro de codigo y configuracion

### Version y trazabilidad de componentes

Todos los componentes del sistema deben versionarse y documentarse:

| Componente | Que registrar | Formato recomendado |
|---|---|---|
| **Instrucciones (prompts)** | Version, fecha, autor, cambios respecto a version anterior | Archivo de texto versionado en git |
| **Parametros del modelo** | Modelo, temperatura, max_tokens, top_p, criterios de parada | Archivo de configuracion YAML/JSON |
| **Conectores y dependencias** | Version de SDK, version de la API del proveedor | `requirements.txt` o `pyproject.toml` |
| **Resultados de pruebas** | Dataset de prueba, metricas, version del sistema | Archivo CSV o base de datos |

```yaml
# config/llm_config.yaml
modelo: claude-opus-4-5
version_api: "2024-02-15"
parametros:
  temperatura: 0.3
  max_tokens: 1024
  top_p: 0.9
instrucciones:
  version: "v2.1"
  archivo: "prompts/sistema_v2.1.txt"
  fecha_actualizacion: "2025-03-15"
```

---

## Actividad practica · UD2

### Implementacion de un componente de interaccion con historial

**Enunciado:**

Desarrolla un asistente de soporte tecnico para una empresa de software. El asistente debe:

1. Mantener el historial de la conversacion (maximo 6 turnos).
2. Usar un mensaje de sistema que defina el rol, tono y restricciones.
3. Detectar cuando el usuario menciona una "incidencia critica" y anadir una advertencia en la respuesta.
4. Devolver siempre la respuesta en formato JSON con los campos: `respuesta`, `requiere_escalado` (bool), `categoria` (soporte_tecnico | fuera_de_alcance | aclaracion).
5. Implementar control de errores con reintento en caso de RateLimitError.

**Tecnologia:** Python + SDK de Anthropic o OpenAI (a eleccion del alumno).

**Entregable:** script Python funcional + archivo `config.yaml` con parametros + ejemplo de ejecucion con 3 turnos de conversacion.

---

## Puntos clave · UD2

- Un prompt efectivo tiene cuatro secciones: sistema, contexto, instruccion y formato de salida.
- La ventana de contexto es un recurso finito: gestionar el historial con ventana deslizante o resumen automatico.
- Los errores de API se clasifican segun si deben reintentarse (429, 5xx) o no (401, 400).
- El backoff exponencial es el patron estandar para reintentos en llamadas a LLM.
- Toda salida del modelo debe validarse contra un esquema antes de usarla en la aplicacion.
- Las instrucciones, parametros y versiones deben registrarse en archivos versionados para garantizar trazabilidad.

---

## Criterios de evaluacion · UD2

| Criterio | Indicadores de logro |
|---|---|
| **Define prompts y gestion de contexto** | Estructura correcta de cuatro secciones; estrategia de compresion de historial implementada |
| **Desarrolla la comunicacion con el modelo controlando errores** | Implementa reintentos con backoff; clasifica errores segun tipo de accion |
| **Gestiona y registra las salidas** | Valida el JSON contra un esquema; registra uso de tokens por llamada |

---

<!-- _class: lead -->

[← Volver a MP04](../index.md)


---

<!-- nav-slide -->

## Navegación

[← UD1 · Análisis del caso de uso y se…](../UD1_Analisis-caso-uso/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD3 · Integracion con fuentes, herr… →](../UD3_Integracion-RAG/)
