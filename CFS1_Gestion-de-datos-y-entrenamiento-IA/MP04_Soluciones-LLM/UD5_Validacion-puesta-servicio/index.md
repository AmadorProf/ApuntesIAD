---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD5 · Validación y puesta en servicio | MP04 · Soluciones basadas en LLMs'
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

# UD5 · Validación y puesta en servicio

**MP04 · Soluciones basadas en LLMs**
CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno sera capaz de:

- Disenar y ejecutar un conjunto de casos de prueba representativo para una solucion basada en LLMs.
- Verificar la calidad de las respuestas segun criterios de pertinencia, coherencia, completitud, trazabilidad y formato.
- Ajustar la solucion —instrucciones, parametros, contexto y fuentes— a partir de los resultados de las pruebas.
- Documentar el proceso de validacion y formalizar la puesta en servicio con los artefactos tecnicos requeridos.

---

## 1 · Casos de prueba: definicion y diseno (I)

### Por que los casos de prueba son diferentes en LLMs

Los sistemas basados en LLMs no producen salidas deterministas. La validacion no puede limitarse a comparar un resultado esperado exacto: requiere definir criterios de calidad y cubrir el espacio de entradas posibles de forma sistematica.

Un conjunto de casos de prueba solido incluye:

| Categoria | Proposito |
|---|---|
| **Entradas representativas** | Cubrir el flujo normal de uso; el 70-80 % de los casos |
| **Consultas complejas** | Preguntas multietapa, ambiguas o con dependencias |
| **Errores esperados** | Entradas malformadas, fuera de dominio o en otro idioma |
| **Ausencia de informacion** | Preguntas cuya respuesta no esta en el contexto disponible |
| **Variaciones linguisticas** | Sinonimos, jerga, mayusculas, typos, mezcla de idiomas |
| **Condiciones limite** | Entradas en el extremo de la ventana de contexto, respuestas muy cortas o muy largas |

---

## 1 · Casos de prueba: definicion y diseno (II)

### Estructura de un caso de prueba

Cada caso de prueba debe documentarse con los siguientes campos:

```
ID:          TC-001
Categoria:   Entrada representativa
Descripcion: Pregunta directa sobre un procedimiento documentado
Entrada:     "¿Cuál es el procedimiento de alta de un proveedor nuevo?"
Contexto:    Fragmento del manual de procedimientos, sección 4.2
Resultado esperado (criterio):
  - La respuesta menciona los pasos 1-5 de la sección 4.2
  - Cita la fuente (sección y número de página)
  - No incluye información de otras secciones
  - Formato: lista numerada
Resultado obtenido: [a completar en ejecucion]
Estado:      PASS / FAIL / PARCIAL
Observaciones:
```

---

## 1 · Casos de prueba: definicion y diseno (III)

### Cobertura minima recomendada por categoria

Para un sistema en produccion, el conjunto de pruebas debe garantizar cobertura en todas las categorias. Una distribucion orientativa:

| Categoria | N.o minimo de casos | Razon |
|---|---|---|
| Entradas representativas | 15-20 | Flujo normal; base de la validacion |
| Consultas complejas | 5-8 | Detectar fallos de razonamiento |
| Errores esperados | 5-6 | Verificar el comportamiento defensivo |
| Ausencia de informacion | 4-5 | Evitar alucinaciones ante vacios de datos |
| Variaciones linguisticas | 4-5 | Robustez ante entradas reales de usuarios |
| Condiciones limite | 3-4 | Detectar fallos en los extremos del sistema |

> La cobertura no es solo cuantitativa: es mas valioso un caso de prueba que detecta un fallo real que diez que repiten el mismo escenario exitoso.

---

## 2 · Evaluacion de soluciones conversacionales (I)

### Mantenimiento de contexto en sistemas multiturno

En soluciones conversacionales, la validacion debe evaluar la coherencia a lo largo de la sesion, no solo en respuestas aisladas:

**Pruebas de memoria de sesion:**
- El sistema recuerda informacion proporcionada en turnos anteriores.
- Las referencias anaforigas se resuelven correctamente ("el contrato del que hablamos antes").
- El historial no contamina la respuesta cuando el tema cambia.

**Pruebas de acumulacion de contexto:**
- La calidad no degrada al acercarse al limite de la ventana de contexto.
- El sistema no confunde informacion de diferentes documentos proporcionados en la misma sesion.

```python
# Ejemplo: prueba automatizada de coherencia multiturno
turnos = [
    {"role": "user", "content": "Mi pedido es el numero 12345."},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "¿Cuál es su estado?"},
]
# La respuesta al segundo turno debe referenciar el pedido 12345
# sin que el usuario lo repita
```

---

## 2 · Evaluacion de soluciones conversacionales (II)

### Respuestas fuera de alcance

Uno de los comportamientos mas criticos a validar es la respuesta del sistema cuando recibe una solicitud que esta fuera de su ambito definido:

| Tipo de consulta fuera de alcance | Comportamiento esperado |
|---|---|
| Tema no cubierto por el sistema | Informar claramente de la limitacion; no inventar |
| Peticion de opinion personal | Declinar o redirigir; no antropomorfizar |
| Informacion que el modelo no tiene | Indicar que no dispone de los datos; no alucinar |
| Instruccion que viola las reglas del sistema | Rechazar con explicacion; no saltarse el system prompt |
| Peticion en un idioma no soportado | Responder en el idioma configurado o indicar la limitacion |

**Indicador de calidad:** el porcentaje de respuestas fuera de alcance que el sistema gestiona correctamente (sin inventar, sin ignorar la limitacion) es un KPI clave de robustez.

---

## 3 · Verificacion de calidad de las respuestas (I)

### Las cinco dimensiones de evaluacion

Toda respuesta generada por el sistema se evalua segun estas dimensiones:

| Dimension | Definicion | Como medirla |
|---|---|---|
| **Pertinencia** | La respuesta aborda exactamente lo preguntado | Evaluacion manual o LLM-as-judge |
| **Coherencia** | La respuesta es logicamente consistente y no se contradice | Revision por pares; pruebas de consistencia |
| **Completitud** | La respuesta incluye toda la informacion relevante disponible | Checklist basado en la fuente de referencia |
| **Trazabilidad** | La respuesta cita las fuentes de donde proviene la informacion | Verificacion de citas contra documentos originales |
| **Formato** | La respuesta sigue el formato especificado (JSON, markdown, lista…) | Validacion automatica con parser |

---

## 3 · Verificacion de calidad de las respuestas (II)

### Evaluacion automatica con LLM-as-judge

Cuando el volumen de pruebas es alto, la evaluacion manual no escala. El patron LLM-as-judge usa un modelo de evaluacion para puntuar las respuestas:

```python
import anthropic

client = anthropic.Anthropic()

def evaluar_respuesta(pregunta: str, respuesta: str, referencia: str) -> dict:
    prompt = f"""Evalúa la siguiente respuesta según estos criterios (0-3 cada uno):
- Pertinencia: ¿responde a la pregunta?
- Coherencia: ¿es lógicamente consistente?
- Completitud: ¿incluye la información relevante de la referencia?
- Trazabilidad: ¿cita las fuentes?

Pregunta: {pregunta}
Respuesta a evaluar: {respuesta}
Referencia: {referencia}

Devuelve un JSON con las puntuaciones y una justificación breve."""

    mensaje = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    return mensaje.content[0].text
```

---

## 3 · Verificacion de calidad de las respuestas (III)

### Umbrales de aceptacion y criterios de rechazo

Los criterios de aceptacion deben definirse antes de ejecutar las pruebas, no despues:

```
CRITERIOS DE ACEPTACION — Sistema de consulta de procedimientos

Pertinencia:    >= 2.5 / 3.0 en promedio; ningun caso con 0
Coherencia:     100 % de casos >= 2.0 / 3.0
Completitud:    >= 2.0 / 3.0 en promedio
Trazabilidad:   >= 90 % de respuestas incluyen referencia a la fuente
Formato:        100 % de respuestas validas segun el schema definido

CONDICIONES DE RECHAZO AUTOMATICO:
- Cualquier respuesta que invente informacion no presente en el contexto
- Cualquier respuesta que ignore una instruccion de seguridad del system prompt
- Tasa de error de formato > 5 %
```

> Los criterios de aceptacion son el contrato entre el desarrollador y el cliente. Deben acordarse antes de la validacion.

---

## 4 · Ajustes sobre la solucion (I)

### Tipos de ajuste y cuando aplicarlos

Cuando un caso de prueba falla, el ajuste debe dirigirse a la causa raiz:

| Causa del fallo | Tipo de ajuste |
|---|---|
| El modelo no sigue las instrucciones | Reformular el system prompt; agregar ejemplos few-shot |
| La respuesta es demasiado larga o corta | Ajustar `max_tokens`; agregar instruccion de longitud |
| El modelo inventa informacion | Reforzar instruccion de no-alucinacion; revisar el contexto proporcionado |
| La respuesta no tiene el formato correcto | Agregar schema de salida; usar structured outputs |
| El modelo no encuentra la informacion relevante | Mejorar el chunking o la recuperacion en RAG |
| El modelo confunde documentos | Separar fuentes en el contexto; agregar etiquetas de procedencia |
| Las respuestas varian demasiado entre ejecuciones | Reducir temperatura; agregar instrucciones de consistencia |

---

## 4 · Ajustes sobre la solucion (II)

### Registro de versiones probadas

Cada ciclo de ajuste genera una nueva version del sistema. El registro de versiones es imprescindible para rastrear la evolucion:

```
VERSION   FECHA       CAMBIO APLICADO                        RESULTADO
----------------------------------------------------------------------
v0.1      2025-01-10  System prompt inicial                  Pertinencia: 1.8; Formato: 72 %
v0.2      2025-01-12  Agregar ejemplo few-shot de formato    Pertinencia: 2.1; Formato: 91 %
v0.3      2025-01-14  Reducir temperatura 0.7 → 0.3          Coherencia: 2.6; Variabilidad -40 %
v0.4      2025-01-16  Instruccion explicita de no-alucinacion Inventos: 8 % → 1 %
v1.0      2025-01-20  Version candidata a produccion          Todos los criterios superados
```

**Regla de gestion:** nunca sobrescribir una version. Mantener el historial completo para poder revertir si una nueva version introduce regresiones.

---

## 4 · Ajustes sobre la solucion (III)

### Ejemplo de evolucion del system prompt entre versiones

```
# VERSION v0.1
Eres un asistente que responde preguntas sobre procedimientos internos.

# VERSION v0.3 (tras detectar problemas de formato e invencion)
Eres un asistente especializado en procedimientos internos de la empresa.

REGLAS OBLIGATORIAS:
1. Responde SOLO con informacion presente en el contexto proporcionado.
2. Si no encuentras la informacion, di exactamente: "No dispongo de informacion
   sobre este procedimiento en la documentacion actual."
3. Cita siempre la seccion de origen al final de tu respuesta: [Fuente: Seccion X.Y]
4. Usa siempre formato de lista numerada para procedimientos de mas de un paso.
5. Longitud maxima: 300 palabras.
```

> La diferencia entre v0.1 y v0.3 ilustra como cada regla nueva responde a un fallo especifico detectado en las pruebas.

---

## 5 · Documentacion de pruebas (I)

### Estructura del informe de validacion

El informe de validacion es el artefacto formal que certifica que el sistema cumple los criterios de aceptacion:

**Secciones obligatorias:**

1. **Configuracion del sistema evaluado** — version, modelo, parametros, system prompt
2. **Conjunto de pruebas** — numero de casos por categoria, criterios de seleccion
3. **Metricas obtenidas** — puntuaciones por dimension; comparativa con criterios de aceptacion
4. **Fallos detectados** — descripcion, categoria, severidad
5. **Ajustes aplicados** — cambios realizados entre versiones
6. **Resultado final** — APTO / NO APTO con justificacion
7. **Pendientes** — limitaciones conocidas que se gestionan en produccion

---

## 5 · Documentacion de pruebas (II)

### Ciclo de resolucion de incidencias

Cuando un caso de prueba falla, se sigue un ciclo estructurado:

```
FALLO DETECTADO
      |
      v
Clasificar severidad
  CRITICA: el sistema produce informacion falsa peligrosa
  ALTA:    el sistema ignora una instruccion de seguridad
  MEDIA:   el formato es incorrecto o la respuesta es incompleta
  BAJA:    la respuesta es correcta pero podria mejorarse
      |
      v
Identificar causa raiz
(instruccion ambigua / parametro inadecuado / fuente insuficiente / limite del modelo)
      |
      v
Aplicar ajuste minimo necesario
      |
      v
Regresar TODOS los casos de prueba anteriores
      |
      v
Registrar en el historial de versiones
```

---

## 5 · Documentacion de pruebas (III)

### Metricas clave del informe de validacion

```python
# Ejemplo de calculo de metricas de validacion
resultados = [
    {"id": "TC-001", "pertinencia": 3, "coherencia": 3,
     "completitud": 2, "trazabilidad": 1, "formato": True},
    {"id": "TC-002", "pertinencia": 2, "coherencia": 3,
     "completitud": 3, "trazabilidad": 1, "formato": True},
    # ...
]

n = len(resultados)
metricas = {
    "pertinencia_media":   sum(r["pertinencia"]  for r in resultados) / n,
    "coherencia_media":    sum(r["coherencia"]   for r in resultados) / n,
    "completitud_media":   sum(r["completitud"]  for r in resultados) / n,
    "trazabilidad_media":  sum(r["trazabilidad"] for r in resultados) / n,
    "formato_ok_pct":      sum(r["formato"]      for r in resultados) / n * 100,
}
print(metricas)
```

---

## 6 · Puesta en servicio (I)

### Artefactos de la puesta en servicio

La validacion exitosa abre el proceso de puesta en servicio. Este proceso genera cuatro tipos de artefactos:

| Artefacto | Audiencia | Contenido |
|---|---|---|
| **Documentacion tecnica** | Equipo de desarrollo y operaciones | Arquitectura, dependencias, configuracion de despliegue, variables de entorno, limites de la API |
| **Manual operativo** | Administradores y soporte** | Procedimientos de monitorizacion, alertas, actualizacion del modelo, gestion de incidencias |
| **Guia de uso** | Usuarios finales | Como interactuar con el sistema, ejemplos de uso, limitaciones conocidas, como reportar errores |
| **Registro de aceptacion** | Responsable del proyecto y cliente | Criterios de aceptacion acordados, resultados obtenidos, firma de conformidad |

---

## 6 · Puesta en servicio (II)

### Documentacion tecnica: contenido minimo

```yaml
# ejemplo: ficha tecnica del sistema en produccion

sistema:
  nombre: "Asistente de Procedimientos Internos v1.0"
  fecha_despliegue: "2025-02-01"
  responsable: "Equipo IA"

modelo:
  proveedor: "Anthropic"
  id_modelo: "claude-opus-4-5"
  temperatura: 0.3
  max_tokens: 512
  system_prompt_version: "v1.0"

integraciones:
  - tipo: RAG
    fuente: "SharePoint — Manuales de procedimientos"
    actualizacion: "trimestral"
  - tipo: API
    endpoint: "/api/v1/consulta"
    autenticacion: "Bearer token"

limites:
  ventana_contexto: "200k tokens"
  rate_limit: "100 req/min"
  coste_estimado: "0.50 USD / 1000 consultas"
```

---

## 6 · Puesta en servicio (III)

### Soporte continuo: que monitorizar en produccion

Una vez el sistema esta en servicio, la validacion no termina: pasa a ser monitorizacion continua.

**Metricas de produccion a seguir:**

| Metrica | Alerta si… | Accion |
|---|---|---|
| Tasa de error (respuestas con formato incorrecto) | > 5 % | Revisar cambios recientes en el modelo o el prompt |
| Latencia media de respuesta | > umbral acordado | Escalar la infraestructura o revisar el chunking |
| Tasa de consultas fuera de alcance | Aumento sostenido | Ampliar el dominio o reforzar el filtrado |
| Feedback negativo de usuarios | > 10 % | Iniciar ciclo de revision y revalidacion |
| Coste acumulado | Supera el presupuesto mensual | Optimizar prompts o revisar el modelo utilizado |

---

## Actividad practica · UD5

### Diseno y ejecucion de un plan de validacion

**Enunciado:**

Tienes una solucion RAG que responde preguntas sobre la normativa de contratacion publica de una administracion local (documentos de 300 paginas). El sistema esta configurado con `temperatura=0.3`, `max_tokens=600` y un system prompt que instruye al modelo a no inventar informacion y citar siempre la fuente.

**Tareas:**

1. Disenar un conjunto de 12 casos de prueba distribuidos en las seis categorias (al menos 2 por categoria).
2. Ejecutar los casos documentando el resultado obtenido y el estado (PASS / FAIL / PARCIAL).
3. Identificar al menos dos ajustes necesarios a partir de los fallos detectados y aplicarlos al system prompt.
4. Redactar el informe de validacion con las metricas obtenidas antes y despues de los ajustes.
5. Elaborar la guia de uso del sistema para los funcionarios que lo utilizaran.

**Entregable:** plan de pruebas + informe de validacion + guia de uso (una pagina).

---

## Puntos clave · UD5

- Los casos de prueba deben cubrir seis categorias: representativas, complejas, errores esperados, ausencia de informacion, variaciones linguisticas y condiciones limite.
- En sistemas conversacionales se evalua ademas el mantenimiento de contexto y las respuestas fuera de alcance.
- La calidad se mide en cinco dimensiones: pertinencia, coherencia, completitud, trazabilidad y formato.
- Los criterios de aceptacion se fijan antes de ejecutar las pruebas, no despues de ver los resultados.
- Cada ajuste genera una nueva version del sistema; el historial de versiones permite rastrear la evolucion y revertir si hay regresiones.
- La puesta en servicio genera cuatro artefactos: documentacion tecnica, manual operativo, guia de uso y registro de aceptacion.
- La monitorizacion en produccion es la continuacion natural de la validacion.

---

## Criterios de evaluacion · UD5

| Criterio | Indicadores de logro |
|---|---|
| **Define y ejecuta casos de prueba** | Diseña casos en las seis categorias con estructura correcta; registra resultados de forma sistematica |
| **Ajusta la solucion segun criterios de aceptacion** | Identifica la causa raiz de cada fallo; aplica el ajuste minimo necesario; verifica la regresion |
| **Formaliza la puesta en servicio** | Genera la documentacion tecnica, el manual operativo y la guia de uso con el contenido minimo requerido |

---

<!-- _class: lead -->

[← Volver a MP04](../index.md)


---

<!-- nav-slide -->

## Navegación

[← UD4 · Comportamientos agenticos](../UD4_Comportamientos-agenticos/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD6 · Seguridad, privacidad y uso e… →](../UD6_Seguridad-privacidad-etica/)
