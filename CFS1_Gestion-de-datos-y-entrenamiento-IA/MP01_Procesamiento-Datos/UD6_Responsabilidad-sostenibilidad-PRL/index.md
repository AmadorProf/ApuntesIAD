---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD6 · Trabajo responsable, sostenible y prevención de riesgos | MP01 · Procesamiento de datos para IA'
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

# UD6 · Trabajo responsable, sostenible y prevención de riesgos

**MP01 · Procesamiento de datos para IA**

Apuntes de IA y Datos

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Actuar con responsabilidad ética en el tratamiento y la publicación de datos
- Aplicar el principio de igualdad de derechos y oportunidades en la gestión de colecciones de datos
- Comunicarse de forma eficaz con perfiles técnicos y no técnicos del equipo
- Integrar criterios de sostenibilidad (DNSH, ODS) en las decisiones de procesamiento de datos
- Reducir el consumo computacional y las emisiones derivadas del trabajo con datos a escala
- Identificar y prevenir riesgos laborales asociados al trabajo con datos: psicosociales, ergonómicos y ambientales
- Actuar correctamente ante emergencias según el plan del centro

---

## Responsabilidad ética en el tratamiento de datos — Concepto

El procesamiento de datos no es una operación técnica neutral. Las decisiones sobre qué datos recoger, cómo limpiarlos, qué atributos conservar y qué registros descartar tienen consecuencias directas sobre las personas representadas en esos datos.

**Tres niveles de responsabilidad en el ciclo de datos:**

| Nivel | Pregunta clave | Ejemplo de decisión |
|---|---|---|
| **Recogida** | ¿Tenemos consentimiento y base legal? | Usar datos de plataformas públicas sin licencia explícita |
| **Transformación** | ¿Introducimos o amplificamos sesgos? | Eliminar registros de colectivos minoritarios por "outliers" |
| **Publicación** | ¿Estamos protegiendo la privacidad? | Publicar dataset con columnas pseudoanonimizadas insuficientes |

> El profesional de datos es el primer filtro ético: no el responsable de producto, no el cliente.

---

## Igualdad de derechos y oportunidades en los datos

Los conjuntos de datos que alimentan sistemas de IA reflejan las desigualdades estructurales de la sociedad. Un dataset desequilibrado en representación produce modelos que discriminan.

**Sesgos de representación más frecuentes en datasets de procesamiento:**

| Tipo de sesgo | Descripción | Consecuencia en el modelo |
|---|---|---|
| **Infrarepresentación demográfica** | Grupos minoritarios con pocos registros | El modelo falla en esos grupos |
| **Sesgo histórico** | Datos que reflejan discriminaciones pasadas | El modelo reproduce y consolida esa discriminación |
| **Sesgo de etiquetado** | Anotadores homogéneos con perspectiva sesgada | Etiquetas inconsistentes para colectivos distintos |
| **Sesgo de supervivencia** | Solo se recogen datos de casos "exitosos" | El modelo no generaliza a casos reales |

**Medidas correctivas:**
- Auditar la distribución de atributos sensibles antes de procesar
- Aplicar técnicas de sobremuestreo (`SMOTE`) o submuestreo si es necesario
- Documentar las decisiones de inclusión/exclusión en el registro de versionado

---

## Comunicación efectiva y trabajo colaborativo

En un proyecto de datos coexisten perfiles con vocabulario y prioridades distintas. Comunicar de forma eficaz entre perfiles es una competencia técnica, no solo interpersonal.

**Perfiles habituales en un proyecto de procesamiento de datos:**

| Perfil | Necesita saber | Cómo comunicar |
|---|---|---|
| **Data Engineer** | Esquemas, tipos, volumen, latencia | Diagramas de flujo, contratos de API |
| **Data Scientist** | Distribuciones, nulos, correlaciones | Estadísticas descriptivas, histogramas |
| **Responsable legal / DPO** | Base legal, retención, anonimización | Informe de impacto en protección de datos |
| **Cliente o usuario final** | Qué datos se usan y para qué | Lenguaje natural, sin jerga técnica |

> Adaptar el nivel de abstracción al receptor no es simplificar: es elegir el canal correcto.

---

## Comunicación colaborativa — Herramientas y prácticas

**Prácticas de colaboración efectiva en equipos de datos:**

```bash
# Convenciones de nombrado compartidas en el equipo
# Formato: {proyecto}_{tipo}_{version}_{fecha}.{ext}
datos_credito_raw_v1_20260601.parquet
datos_credito_limpio_v2_20260610.parquet
datos_credito_train_v2_20260610.parquet

# El nombre del archivo comunica su estado sin necesidad de leer el contenido
```

**Registro de decisiones (ADR — Architecture Decision Record):**

```markdown
# ADR-003: Eliminación de registros con nulos en columna "ingreso_mensual"

**Fecha:** 2026-06-15
**Autor:** @data-engineer-01
**Contexto:** El 12 % de los registros tienen nulo en "ingreso_mensual".
**Decisión:** Eliminar esos registros porque la imputación introduciría sesgo.
**Consecuencias:** Dataset reducido a 88 % del original; documentado en ficha de calidad.
**Alternativas descartadas:** Imputación por mediana (distorsiona distribución en subgrupos).
```

---

## Sostenibilidad tecnológica — Principio DNSH

El principio **DNSH** (*Do No Significant Harm* — No causar daño significativo) es un criterio de la taxonomía verde de la UE aplicable a proyectos tecnológicos cofinanciados con fondos europeos. En el contexto del procesamiento de datos, implica que cada decisión tecnológica debe evaluarse por su impacto ambiental.

**Aplicación del principio DNSH al procesamiento de datos:**

| Decisión técnica | Riesgo DNSH | Alternativa sostenible |
|---|---|---|
| Almacenar todas las versiones intermedias en disco | Consumo energético de almacenamiento innecesario | Mantener solo versiones etiquetadas; comprimir con `parquet` |
| Ejecutar EDA sobre dataset completo (100M filas) | Alto consumo computacional | Muestreo estratificado (10 % representativo) para exploración |
| Re-ejecutar todo el pipeline ante cada cambio | Ciclos de cómputo desperdiciados | Cachear etapas inmutables con `joblib.Memory` o `DVC` |
| Transformaciones en bucle Python sobre filas | CPU ineficiente | Operaciones vectorizadas con `pandas` o `polars` |

> El DNSH no prohíbe procesar datos: exige que el proceso sea tan eficiente como sea técnicamente posible.

---

## ODS aplicables al procesamiento de datos

Los **Objetivos de Desarrollo Sostenible** de la ONU proporcionan un marco de referencia para evaluar el impacto de las actividades de datos más allá del consumo energético.

**ODS directamente aplicables:**

| ODS | Título | Aplicación en procesamiento de datos |
|---|---|---|
| **ODS 9** | Industria, innovación e infraestructura | Diseñar pipelines eficientes que reduzcan el uso de recursos |
| **ODS 10** | Reducción de las desigualdades | Auditar y corregir sesgos de representación demográfica |
| **ODS 12** | Producción y consumo responsables | Evitar almacenamiento y cómputo innecesarios |
| **ODS 13** | Acción por el clima | Minimizar la huella de carbono de las operaciones de datos |
| **ODS 16** | Paz, justicia e instituciones sólidas | Garantizar el cumplimiento del RGPD y la transparencia |

---

## Reducción del consumo computacional — Técnicas

**El procesamiento de datos a escala tiene un coste energético medible. Estas técnicas lo reducen sin pérdida de calidad:**

```python
import pandas as pd
import polars as pl

# 1. Leer solo las columnas necesarias (evitar cargar columnas no usadas)
df = pd.read_csv("datos_grande.csv", usecols=["id", "edad", "ingreso", "etiqueta"])

# 2. Reducir tipos de dato para minimizar uso de memoria
df["edad"] = df["edad"].astype("int8")          # 8 bits en lugar de 64
df["ingreso"] = df["ingreso"].astype("float32") # 32 bits en lugar de 64

# Memoria antes: 800 MB → después: ~200 MB (75% menos)
print(f"Uso de memoria: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")

# 3. Usar Polars para operaciones en columnas: hasta 10x más rápido que pandas
df_pl = pl.scan_csv("datos_grande.csv")  # lazy: no carga hasta ejecutar
resultado = (df_pl
    .filter(pl.col("edad") > 18)
    .select(["id", "edad", "ingreso"])
    .collect())
```

---

## Reducción de emisiones — Caché y evitar recomputos

```python
from joblib import Memory
import pandas as pd

# Configurar cache en disco: las funciones marcadas no se re-ejecutan si los inputs no cambian
memoria = Memory("cache_pipeline/", verbose=0)

@memoria.cache
def limpiar_datos(ruta_fichero: str, version: str) -> pd.DataFrame:
    """
    Carga y limpia el dataset. Se ejecuta solo la primera vez;
    las llamadas siguientes con los mismos argumentos usan la cache.
    """
    df = pd.read_csv(ruta_fichero)
    df = df.dropna(subset=["ingreso_mensual"])
    df = df[df["edad"].between(18, 99)]
    df["ingreso_mensual"] = df["ingreso_mensual"].astype("float32")
    return df

# Primera ejecucion: procesa. Siguientes: lee de cache sin consumo de CPU
df_limpio = limpiar_datos("datos_raw.csv", version="v2")
```

> Cachear etapas inmutables del pipeline puede reducir el tiempo de re-ejecución en un 80-95 % y elimina el consumo de CPU asociado.

---

## Prevención de riesgos — Riesgos psicosociales

El trabajo con datos presenta riesgos psicosociales específicos derivados de la gestión de volúmenes elevados, la presión de plazos y la incertidumbre técnica sobre la calidad de las fuentes.

| Riesgo psicosocial | Manifestaciones | Medidas preventivas |
|---|---|---|
| **Tecnoestrés** | Ansiedad ante nuevas herramientas o cambios de stack | Plan de formación; no migrar herramientas en mitad del proyecto |
| **Fatiga por decisión** | Parálisis ante demasiadas opciones de limpieza o transformación | Usar plantillas de decisión predefinidas por el equipo |
| **Síndrome del impostor** | Bloqueo ante datasets complejos o multifuente | Documentar los avances parciales; celebrar hitos intermedios |
| **Sobrecarga de información** | Incapacidad de procesar toda la documentación de las fuentes | Rutinas de análisis de 30 minutos por fuente antes de integrar |
| **Presión de plazos** | Saltarse validaciones de calidad por urgencia | Definir umbrales mínimos de calidad no negociables desde el inicio |

---

## Prevención de riesgos — Ergonomía cognitiva

La **ergonomía cognitiva** en el trabajo con datos se centra en diseñar el proceso de trabajo para que la carga mental sea sostenible y las decisiones sean de alta calidad.

**Prácticas aplicadas al procesamiento de datos:**

- **Documentar las decisiones en el momento** en que se toman: no al final del día
- **Dividir el pipeline en etapas con objetivos claros** y verificables por separado
- **Usar nombres de variables y columnas descriptivos** desde el inicio del notebook
- **Establecer checkpoints de revisión** antes de pasar a la siguiente etapa del pipeline
- **Revisar el historial de cambios** antes de comenzar una sesión de trabajo sobre el dataset

```python
# Convención de nomenclatura que reduce carga cognitiva
df_raw          = pd.read_csv(...)          # sin tocar
df_filtrado     = aplicar_filtros(df_raw)   # solo filtros de filas
df_imputado     = imputar_nulos(df_filtrado) # solo imputación
df_codificado   = codificar(df_imputado)    # solo encoding
df_final        = df_codificado             # listo para partición
```

> Un pipeline con nombres de etapas explícitos es autoexplicativo y reduce el tiempo de revisión un 40-60 %.

---

## Prevención de riesgos — Ergonomía física y postural

| Área | Riesgo | Medida preventiva |
|---|---|---|
| **Postura** | Dolor cervical y lumbalgia en sesiones largas de análisis | Silla regulable con apoyo lumbar; pantalla a la altura de los ojos |
| **Visual** | Fatiga ocular por lectura de tablas y código durante horas | Regla 20-20-20: cada 20 min, mirar a 6 m durante 20 seg |
| **Iluminación** | Deslumbramiento o contraste excesivo entre pantalla y entorno | Luz ambiental indirecta; modo oscuro en IDE y Jupyter |
| **Sedentarismo** | Problemas cardiovasculares y metabólicos | Pausas activas cada 60 min; no trabajar más de 90 min seguidos |
| **Temperatura** | Disconfort por calor de equipos en espacios cerrados | Ventilación adecuada; 20-24 °C en el puesto |
| **Ruido** | Distracción en tareas de revisión de código | Aislar el área de revisiones complejas |

---

## Factores ambientales del puesto de trabajo con datos

Los entornos de trabajo con datos intensivo (salas de servidores próximas, múltiples monitores, hardware de procesamiento) presentan factores ambientales específicos.

**Factores a evaluar en la evaluación de riesgos del puesto:**

| Factor | Valor de referencia | Consecuencia si no se cumple |
|---|---|---|
| **Temperatura** | 20-24 °C | Fatiga, errores de concentración |
| **Humedad relativa** | 45-65 % | Sequedad ocular, descarga estática en equipos |
| **Nivel sonoro** | < 65 dB en trabajo cognitivo | Distracción, aumento del tiempo de tarea |
| **Iluminación** | 500 lux en puesto de pantalla | Fatiga visual, cefalea |
| **Calidad del aire** | < 1000 ppm CO₂ | Somnolencia, reducción de la concentración |

> La normativa de referencia en España es el RD 486/1997 sobre lugares de trabajo y la Guía Técnica del INSST sobre pantallas de visualización de datos.

---

## Actuación ante emergencias — Plan de emergencias

**Conocimiento obligatorio del plan de emergencias del centro:**

- Localización de las salidas de emergencia desde el puesto de trabajo
- Punto de reunión exterior asignado al área de trabajo
- Localización de los extintores más próximos al puesto
- Tipo de extintor adecuado para equipos eléctricos: **CO₂ o polvo seco ABC** (nunca agua ni espuma)
- Protocolo de parada segura de procesos en ejecución antes de evacuar

**Protocolo de parada segura de un pipeline en emergencia:**

```python
import signal, sys

def guardar_checkpoint_y_salir(sig, frame):
    """Captura señales de interrupción para guardar estado antes de salir."""
    if "df_actual" in globals():
        df_actual.to_parquet("checkpoint_emergencia.parquet")
        print("Checkpoint guardado: checkpoint_emergencia.parquet")
    sys.exit(0)

signal.signal(signal.SIGINT, guardar_checkpoint_y_salir)   # Ctrl+C
signal.signal(signal.SIGTERM, guardar_checkpoint_y_salir)  # señal del SO
```

---

## Actuación ante emergencias — Tipos y procedimiento

**Tipos de emergencia más frecuentes en entornos con equipos de cómputo:**

| Tipo de emergencia | Protocolo específico |
|---|---|
| **Incendio eléctrico** | Cortar alimentación antes de usar extintor; usar CO₂ o polvo seco ABC |
| **Corte de suministro eléctrico** | Los sistemas con UPS tienen autonomía; guardar trabajo inmediatamente |
| **Sobrecalentamiento de hardware** | Apagar el equipo; no forzar reinicio; avisar al responsable técnico |
| **Fuga de datos en tiempo real** | Desconectar el proceso; notificar al DPO en menos de 72 h (RGPD Art. 33) |
| **Evacuación general** | Suspender el proceso sin forzar el apagado; dejar el sistema en estado seguro |

> En caso de duda entre salvar el trabajo y evacuarse: **primero la persona, después el sistema**.

---

## Actividad práctica — UD6

**Contexto:** Tu equipo está procesando un dataset de solicitudes de crédito (500 000 registros, 48 columnas, fuentes mixtas). El plazo de entrega del dataset limpio es en 5 días hábiles.

**Tareas:**

1. Audita la distribución de tres atributos sensibles del dataset (género, edad, código postal). Identifica si existe infrarepresentación y documenta la decisión de corrección en un ADR
2. Aplica las dos técnicas de reducción de consumo vistas (tipos de dato reducidos y caché de pipeline). Mide y compara el uso de memoria antes y después
3. Identifica dos riesgos psicosociales presentes en este escenario y propón una medida preventiva para cada uno
4. Diseña una sesión de trabajo de 4 horas que incorpore pausas ergonómicas, checkpoints de revisión de calidad y documentación de decisiones
5. Localiza en el plano del centro el extintor más próximo a tu puesto e identifica su tipo de agente extintor. Indica si es adecuado para equipos eléctricos

---

## Puntos clave — UD6

- La responsabilidad ética en el procesamiento de datos comienza en la auditoría de representación: un dataset con infrarepresentación produce modelos que discriminan sistemáticamente
- El principio DNSH obliga a evaluar el impacto ambiental de las decisiones técnicas: almacenamiento innecesario, re-ejecución de etapas y tipos de dato no optimizados tienen coste energético medible
- Los ODS 9, 10, 12 y 13 son directamente aplicables al trabajo con datos: eficiencia, igualdad, consumo responsable y acción climática
- La caché de etapas inmutables del pipeline no es un atajo: es una práctica sostenible que elimina recomputos innecesarios
- La ergonomía cognitiva mejora la calidad de las decisiones técnicas además del bienestar: documentar en el momento y usar nombres explícitos reduce errores
- El extintor adecuado para equipos eléctricos es siempre CO₂ o polvo seco ABC: nunca agua ni espuma

---

## Criterios de evaluación — UD6

| Criterio | Indicador de logro |
|---|---|
| Integra criterios de sostenibilidad en el proceso de datos | Aplica reducción de tipos de dato, caché de pipeline y muestreo estratégico para reducir el consumo computacional |
| Aplica el principio DNSH | Evalúa el impacto ambiental de las decisiones de procesamiento y elige la alternativa más eficiente |
| Audita la representación del dataset | Analiza la distribución de atributos sensibles y documenta las decisiones de corrección |
| Comunica con adaptación al receptor | Redacta ADRs y registros de decisiones en el nivel de abstracción adecuado al interlocutor |
| Aplica medidas ergonómicas | Diseña su entorno y sesión de trabajo con criterios de ergonomía física y cognitiva |
| Aplica medidas de prevención de riesgos | Identifica riesgos psicosociales del rol y aplica medidas preventivas específicas |
| Conoce el plan de emergencias | Localiza salidas, extintor adecuado y aplica el protocolo de parada segura del pipeline |

---

<!-- _class: lead -->

[← Volver a MP01](../)


---

<!-- nav-slide -->

## Navegación

[← UD5 · Gestión, versionado y cumplim…](../UD5_Gestion-versionado-normativa/) &nbsp;·&nbsp; [Volver al módulo](../)
