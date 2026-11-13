---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD7 · Vigilancia tecnológica de LLMs | MP04 · Soluciones basadas en LLMs'
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

# UD7 · Vigilancia tecnologica de LLMs

**MP04 · Soluciones basadas en LLMs**
Apuntes de IA y Datos

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno sera capaz de:

- Seleccionar y gestionar un conjunto de fuentes primarias y secundarias para la vigilancia tecnologica de LLMs.
- Recopilar novedades de forma periodica y sistematica aplicando criterios de relevancia.
- Analizar el impacto de las novedades sobre las soluciones existentes y los requisitos de adopcion.
- Formular y reportar propuestas de mejora, actualizacion o sustitucion con justificacion tecnica.

---

## 1 · Por que la vigilancia tecnologica es critica en LLMs (I)

### El ritmo de cambio en el ecosistema de LLMs

El ecosistema de modelos de lenguaje evoluciona a una velocidad sin precedente en la historia del software. Una solucion bien diseñada hoy puede quedar obsoleta en semanas si no se realiza vigilancia activa:

| Tipo de cambio | Frecuencia habitual | Impacto si no se detecta |
|---|---|---|
| Nuevo modelo con mejor rendimiento | Mensual o mas frecuente | La solucion es menos competitiva; mayor coste relativo |
| Deprecacion de un modelo o version | Trimestral | La solucion deja de funcionar sin aviso |
| Cambio de precios de la API | Irregular | El coste real supera el presupuesto |
| Nueva vulnerabilidad de seguridad | Irregular | Exposicion a riesgos no conocidos |
| Nueva capacidad (multimodalidad, tool use) | Frecuente | Oportunidad de mejora no aprovechada |
| Cambio en los terminos de uso | Anual o menos | Incumplimiento normativo inadvertido |

---

## 1 · Por que la vigilancia tecnologica es critica en LLMs (II)

### La vigilancia como proceso, no como evento puntual

La vigilancia tecnologica eficaz tiene cuatro fases que se repiten de forma ciclica:

```
IDENTIFICAR fuentes fiables y relevantes
         |
         v
RECOPILAR novedades de forma periodica y sistematica
         |
         v
ANALIZAR relevancia, aplicabilidad e impacto sobre las soluciones actuales
         |
         v
REPORTAR y PROPONER mejoras, actualizaciones o sustituciones
         |
         v
[volver al inicio del ciclo]
```

La periodicidad minima recomendada es semanal para novedades de seguridad y mensual para el resto.

---

## 2 · Fuentes primarias: proveedores (I)

### Documentacion oficial de los principales proveedores

Las fuentes primarias son las mas fiables: la documentacion y los canales de comunicacion directos de los proveedores.

| Proveedor | Modelos | Fuentes de referencia |
|---|---|---|
| **OpenAI** | GPT-4o, o3, o4-mini | platform.openai.com/docs, openai.com/blog |
| **Anthropic** | Claude 3.x, Claude 4.x | docs.anthropic.com, anthropic.com/news |
| **Google** | Gemini 1.5, Gemini 2.x | ai.google.dev, cloud.google.com/vertex-ai |
| **Meta** | Llama 3.x, Llama 4 | ai.meta.com, llama.meta.com |
| **Mistral** | Mistral Large, Mixtral | docs.mistral.ai, mistral.ai/news |
| **Cohere** | Command R+, Embed 3 | docs.cohere.com |

**Que monitorizar en la documentacion oficial:**
- Changelogs y release notes de los modelos
- Tablas de precios y limites de uso
- Politicas de datos y terminos de servicio
- Guias de migracion cuando cambia la API

---

## 2 · Fuentes primarias: proveedores (II)

### Como leer un changelog de modelo para identificar impacto

Cuando un proveedor publica una nueva version de su modelo o de su API, el changelog debe leerse con una perspectiva de impacto sobre las soluciones desplegadas:

```
EJEMPLO DE ANALISIS DE CHANGELOG

Cambio publicado:
"El parametro 'max_tokens' ha sido reemplazado por 'max_completion_tokens'
 en la API v2. El parametro antiguo seguira funcionando hasta el 2025-06-01."

Analisis de impacto:
  Afecta a: todas las soluciones que usan la API v1
  Urgencia: MEDIA (margen de 3 meses)
  Accion requerida:
    1. Inventariar todos los proyectos que usan 'max_tokens'
    2. Planificar la migracion antes del 2025-04-15
    3. Probar en entorno de desarrollo con el parametro nuevo
    4. Desplegar en produccion con pruebas de regresion completas
  Riesgo si no se actua: la solucion dejara de funcionar tras la fecha de deprecacion
```

---

## 3 · Fuentes secundarias: repositorios y comunidades (I)

### HuggingFace como fuente de vigilancia

HuggingFace es el ecosistema central de modelos de lenguaje de codigo abierto. Es una fuente imprescindible para:

- **Model Hub:** nuevos modelos publicados, sus benchmarks y licencias
- **Leaderboards:** rankings actualizados de rendimiento (Open LLM Leaderboard)
- **Datasets:** nuevos conjuntos de datos de evaluacion y entrenamiento
- **Spaces:** demostraciones funcionales de modelos antes de su adopcion generalizada
- **Papers:** conexion directa con los articulos de investigacion que originan los modelos

**Estrategia de monitorizacion en HuggingFace:**
1. Seguir las organizaciones clave: `meta-llama`, `mistralai`, `google`, `microsoft`
2. Activar notificaciones para los modelos en produccion
3. Revisar el leaderboard mensualmente para detectar modelos que superan al actual

---

## 3 · Fuentes secundarias: repositorios y comunidades (II)

### GitHub y publicaciones cientificas

**GitHub como fuente de vigilancia:**
- Repositorios de los frameworks principales: `langchain-ai/langchain`, `openai/openai-python`, `anthropics/anthropic-sdk-python`
- Issues y pull requests: detectan problemas conocidos antes de que lleguen a produccion
- Releases: cambios en las librerias que pueden romper la compatibilidad

**Publicaciones cientificas:**
- **arXiv (cs.CL, cs.AI):** preprints de investigacion antes de su publicacion formal
- **Papers With Code:** articulos con codigo y benchmarks reproducibles
- **ACL Anthology:** actas de las principales conferencias de NLP (ACL, EMNLP, NAACL)

**Boletines curados de alta calidad:**
- The Batch (DeepLearning.AI) — semanal
- Import AI (Jack Clark) — semanal
- The AI Timeline (varios) — agregadores con cobertura amplia

---

## 3 · Fuentes secundarias: repositorios y comunidades (III)

### Boletines de seguridad y registros de versiones

La vigilancia de seguridad requiere fuentes especificas:

| Fuente | Tipo | Contenido |
|---|---|---|
| **NIST NVD** | Base de datos de vulnerabilidades | CVEs que afectan a librerias de ML e IA |
| **OWASP LLM Top 10** | Guia de referencia | Los diez riesgos mas criticos en aplicaciones LLM |
| **Boletines de los proveedores** | Email / RSS | Notificaciones de seguridad de OpenAI, Anthropic, etc. |
| **GitHub Security Advisories** | Repositorios seguidos | Vulnerabilidades en dependencias del proyecto |
| **CVE Mitre** | Base de datos | Busqueda especifica por libreria o componente |

> Los boletines de seguridad deben revisarse en menos de 48 horas. Una vulnerabilidad critica no puede esperar al ciclo mensual.

---

## 4 · Analisis de relevancia y aplicabilidad (I)

### Marco de analisis de una novedad

Cuando se detecta una novedad, el analisis debe responder a cuatro preguntas antes de proponer ninguna accion:

```
NOVEDAD: Modelo X lanza soporte nativo para documentos PDF de hasta 1.000 paginas

PREGUNTA 1: ¿Es relevante para nuestras soluciones actuales?
  Si — tenemos dos soluciones RAG que procesan PDFs extensos

PREGUNTA 2: ¿Es aplicable en nuestro contexto?
  Parcialmente — el modelo es solo API; cumple con RGPD si se usa en region EU

PREGUNTA 3: ¿Cual es el impacto sobre las soluciones existentes?
  Podria eliminar la necesidad de chunking en la solucion A
  La solucion B usaria un modelo diferente al actual: requiere pruebas de regresion

PREGUNTA 4: ¿Que requisitos tiene la adopcion?
  Cambio de modelo en la configuracion + pruebas de calidad + actualizacion de costes
  Estimacion: 3 dias de trabajo tecnico + 1 ciclo de validacion completo
```

---

## 4 · Analisis de relevancia y aplicabilidad (II)

### Criterios para priorizar la adopcion de una novedad

No toda novedad debe adoptarse de inmediato. Los criterios de priorizacion permiten gestionar el esfuerzo:

| Criterio | Peso | Escala |
|---|---|---|
| **Mejora de calidad** | Alto | ¿Cuanto mejora el rendimiento medible en el caso de uso real? |
| **Reduccion de coste** | Alto | ¿Cual es el ahorro mensual estimado? |
| **Reduccion de riesgo** | Muy alto | ¿Corrige una vulnerabilidad o un riesgo de deprecacion? |
| **Esfuerzo de adopcion** | Medio (inverso) | ¿Cuantos dias de trabajo requiere la migracion? |
| **Madurez de la tecnologia** | Medio | ¿Lleva al menos 30 dias en produccion en otros proyectos? |

**Regla practica:** adoptar inmediatamente si hay riesgo de seguridad o deprecacion inminente. Planificar en el siguiente sprint si hay mejora de calidad o coste significativa. Registrar y revisar en el siguiente ciclo si la novedad es interesante pero no urgente.

---

## 4 · Analisis de relevancia y aplicabilidad (III)

### Tabla de seguimiento de novedades

El seguimiento sistematico se realiza con una tabla actualizada periodicamente:

```
TABLA DE VIGILANCIA TECNOLOGICA — CicloMensual 2025-05

ID     | FECHA      | FUENTE          | NOVEDAD                        | RELEVANCIA | ESTADO
-------|------------|-----------------|--------------------------------|------------|--------
VT-041 | 2025-05-03 | Anthropic Blog  | Claude 4 Opus: 32k context     | ALTA       | En analisis
VT-042 | 2025-05-07 | OpenAI Docs     | Deprecacion de gpt-3.5-turbo   | CRITICA    | Migracion iniciada
VT-043 | 2025-05-10 | arXiv cs.CL     | Nuevo metodo de evaluacion RAG | MEDIA      | Archivado
VT-044 | 2025-05-14 | HuggingFace     | Llama 4 Scout: rendimiento ES  | ALTA       | Evaluando
VT-045 | 2025-05-18 | GitHub Advisory | Vulnerabilidad en langchain    | CRITICA    | Parcheado
VT-046 | 2025-05-22 | Import AI       | Reduccion precios Gemini 1.5   | MEDIA      | Pendiente revision
```

---

## 5 · Propuestas de mejora y reporte (I)

### Estructura de una propuesta de mejora tecnologica

Cuando el analisis concluye que una novedad debe adoptarse, se formaliza en una propuesta:

```
PROPUESTA DE MEJORA TECNOLOGICA

ID:          PMT-2025-07
Fecha:       2025-05-20
Responsable: [nombre]

NOVEDAD DETECTADA:
El proveedor X ha publicado el modelo Y con un 23 % de mejora en benchmarks
de comprension de texto en espanol y un 15 % de reduccion de coste por token.

SITUACION ACTUAL:
La solucion "Asistente de Procedimientos" usa el modelo anterior con un coste
mensual de 320 EUR y una tasa de pertinencia del 82 %.

PROPUESTA:
Migrar la solucion al modelo Y tras completar un ciclo de validacion.

BENEFICIO ESPERADO:
- Ahorro estimado: 48 EUR/mes (15 %)
- Mejora de pertinencia estimada: +5 puntos porcentuales
RIESGOS: posibles cambios de comportamiento en casos limite
ESFUERZO: 2 dias de trabajo tecnico + 1 ciclo de validacion
PLAZO PROPUESTO: sprint de junio
```

---

## 5 · Propuestas de mejora y reporte (II)

### El reporte formal de vigilancia

El reporte de vigilancia es el artefacto que comunica los resultados del ciclo al equipo y a la organizacion:

**Estructura del reporte mensual de vigilancia:**

1. **Resumen ejecutivo** — tres bullets: novedad mas importante, riesgo mas urgente, oportunidad identificada
2. **Novedades revisadas** — tabla con todas las novedades del periodo (formato resumido)
3. **Analisis en profundidad** — solo las novedades de relevancia ALTA o CRITICA
4. **Propuestas de accion** — ordenadas por urgencia; con responsable y plazo
5. **Estado de propuestas anteriores** — seguimiento de las propuestas de ciclos anteriores
6. **Proxima revision** — fecha y foco especifico del siguiente ciclo

> El reporte debe ser util para dos audiencias: el equipo tecnico (que necesita el detalle) y la direccion (que necesita el impacto y las decisiones requeridas).

---

## 5 · Propuestas de mejora y reporte (III)

### Automatizacion parcial del proceso de vigilancia

```python
import feedparser
import json
from datetime import datetime

FUENTES_RSS = {
    "Anthropic Blog":   "https://www.anthropic.com/rss.xml",
    "OpenAI Blog":      "https://openai.com/blog/rss.xml",
    "HuggingFace Blog": "https://huggingface.co/blog/feed.xml",
    "Import AI":        "https://jack-clark.net/feed/",
}

PALABRAS_CLAVE = ["model", "release", "deprecat", "security", "pricing",
                  "vulnerability", "update", "llm", "claude", "gpt"]

def recopilar_novedades() -> list[dict]:
    novedades = []
    for fuente, url in FUENTES_RSS.items():
        feed = feedparser.parse(url)
        for entrada in feed.entries[:10]:  # ultimas 10 por fuente
            titulo = entrada.title.lower()
            if any(kw in titulo for kw in PALABRAS_CLAVE):
                novedades.append({
                    "fecha":   entrada.get("published", datetime.now().isoformat()),
                    "fuente":  fuente,
                    "titulo":  entrada.title,
                    "url":     entrada.link,
                    "estado":  "pendiente_revision",
                })
    return novedades

print(json.dumps(recopilar_novedades(), ensure_ascii=False, indent=2))
```

---

## Actividad practica · UD7

### Ciclo completo de vigilancia tecnologica

**Enunciado:**

Tu equipo mantiene dos soluciones en produccion: un asistente RAG para consultas internas (usa Claude Haiku) y un sistema de clasificacion de incidencias (usa GPT-3.5-turbo). Debes realizar el ciclo de vigilancia del mes de junio.

**Tareas:**

1. Definir el conjunto de fuentes que vas a monitorizar (minimo ocho fuentes, justificando cada una).
2. Simular la recopilacion de cinco novedades del mes (puedes basarte en novedades reales recientes o inventarlas con coherencia tecnica), documentandolas en la tabla de seguimiento.
3. Analizar en profundidad las dos novedades de mayor relevancia aplicando el marco de cuatro preguntas.
4. Redactar una propuesta de mejora para al menos una de ellas.
5. Elaborar el reporte mensual de vigilancia completo (con todas las secciones).

**Entregable:** tabla de seguimiento + dos analisis en profundidad + propuesta + reporte mensual.

---

## Puntos clave · UD7

- El ecosistema de LLMs cambia con una frecuencia que hace obligatoria la vigilancia activa y sistematica.
- Las fuentes primarias son la documentacion oficial de los proveedores: changelogs, release notes, politicas de datos y tablas de precios.
- Las fuentes secundarias incluyen HuggingFace, GitHub, publicaciones cientificas, comunidades y boletines curados.
- Los boletines de seguridad deben revisarse en menos de 48 horas; el resto puede tener ciclo semanal o mensual.
- El analisis de una novedad responde a cuatro preguntas: ¿es relevante?, ¿es aplicable?, ¿cual es el impacto?, ¿que requiere la adopcion?
- Las propuestas de mejora se priorizan por riesgo, coste, calidad y esfuerzo, en ese orden.
- El reporte formal comunica los resultados a dos audiencias: el equipo tecnico y la direccion.

---

## Criterios de evaluacion · UD7

| Criterio | Indicadores de logro |
|---|---|
| **Selecciona fuentes y recopila novedades sistematicamente** | Define un conjunto de fuentes justificado que cubre proveedores, repositorios, publicaciones y seguridad; aplica periodicidades diferenciadas |
| **Analiza la aplicabilidad de las novedades** | Aplica el marco de cuatro preguntas; prioriza correctamente segun riesgo, coste y esfuerzo |
| **Formula y reporta propuestas de mejora** | Las propuestas incluyen beneficio esperado, riesgos, esfuerzo y plazo; el reporte es util para audiencia tecnica y directiva |

---

<!-- _class: lead -->

[← Volver a MP04](../index.md)


---

<!-- nav-slide -->

## Navegación

[← UD6 · Seguridad, privacidad y uso e…](../UD6_Seguridad-privacidad-etica/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD8 · Responsabilidad profesional,… →](../UD8_Responsabilidad-sostenibilidad-PRL/)
