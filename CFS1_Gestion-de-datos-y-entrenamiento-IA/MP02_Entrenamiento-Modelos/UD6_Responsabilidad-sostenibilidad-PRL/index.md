---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD6 · Trabajo responsable, sostenible y PRL | MP02 · Entrenamiento de modelos de aprendizaje automático'
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

**MP02 · Entrenamiento de modelos de aprendizaje automático**

Apuntes de IA y Datos

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Actuar con autonomía, responsabilidad ética y adaptabilidad en su rol profesional
- Comunicar de forma eficaz entre perfiles técnicos y no técnicos del equipo
- Aplicar criterios de sostenibilidad en la elección de arquitecturas y parámetros de entrenamiento
- Reducir el consumo computacional mediante registro, versionado y reutilización de experimentos
- Identificar los principales riesgos laborales asociados al trabajo en IA: psicosociales, ergonómicos y ambientales
- Aplicar medidas preventivas y conocer el plan de emergencias del centro

---

## Autonomía y responsabilidad ética — Concepto

La **autonomía profesional** en IA no significa trabajar en solitario, sino tomar decisiones fundamentadas sin requerir supervisión constante para cada paso del proceso. La **responsabilidad ética** implica asumir las consecuencias de las elecciones técnicas sobre las personas y la sociedad.

**Por qué es relevante en el entrenamiento de modelos:**
- Las decisiones de diseño (qué datos usar, qué optimizar, qué no documentar) tienen consecuencias sobre personas reales
- Un modelo que discrimina o que se aplica fuera de su dominio de validez puede causar daño
- El profesional técnico es el primer filtro ético antes que el responsable de producto o el cliente

---

## Autonomía y responsabilidad — Aplicación práctica

**Situaciones que requieren decisión ética autónoma:**

| Situación | Decisión irresponsable | Decisión responsable |
|---|---|---|
| Dataset con sesgo racial detectado | Entrenar igualmente y no documentar | Corregir el desbalance, documentar el sesgo en la ficha técnica |
| Métricas por debajo del umbral pero el cliente presiona | Declarar el modelo apto | Comunicar la limitación y proponer plan de mejora |
| Modelo con buen global F1 pero falla en subgrupo minoritario | Reportar solo el global | Reportar el rendimiento desagregado por subgrupo |
| Experimento sin registrar porque "ya se sabe qué se hizo" | No documentar | Registrar en MLflow aunque sea laborioso |

---

## Comunicación eficaz entre roles

En un equipo de IA coexisten perfiles con vocabulario y prioridades distintas. La comunicación eficaz es una competencia técnica, no solo interpersonal.

**Perfiles habituales en un proyecto de ML:**

| Perfil | Qué necesita saber | Cómo comunicar |
|---|---|---|
| Técnico ML / Data Scientist | Detalles de arquitectura, métricas técnicas | Código, tablas, curvas |
| Responsable de producto | Impacto en el negocio, fiabilidad | Casos de uso, limitaciones en lenguaje natural |
| Responsable de calidad / auditor | Trazabilidad, reproducibilidad | Ficha técnica, logs de MLflow |
| Cliente / usuario final | Qué hace y qué no hace el sistema | Ejemplos concretos, casos de éxito y fallo |

> Adaptarse al receptor no es simplificar: es elegir el nivel de abstracción correcto.

---

## Adaptabilidad profesional

El campo de la IA evoluciona más rápido que cualquier otra disciplina técnica. La **adaptabilidad** es la capacidad de actualizar métodos, herramientas y enfoques ante nueva información o cambios de contexto.

**En el contexto del entrenamiento de modelos:**
- Los resultados insatisfactorios no son fracasos: son información para rediseñar
- Cambiar de arquitectura o paradigma a mitad de proyecto debe ser una decisión razonada, no reactiva
- Incorporar nuevas técnicas (PEFT, LoRA, cuantización) requiere evaluarlas con criterio antes de adoptarlas

**Indicadores de adaptabilidad profesional:**
- Se actualiza con literatura técnica relevante (arxiv, blogs de investigación)
- Documenta lo que no funcionó con la misma rigurosidad que lo que sí funcionó
- Propone mejoras proactivamente sin esperar instrucciones

---

## Sostenibilidad — Impacto ambiental del entrenamiento

El entrenamiento de modelos de IA tiene un coste energético y medioambiental significativo. Según estudios de la Universidad de Massachusetts (2019), entrenar un modelo Transformer grande desde cero puede emitir hasta 284 toneladas de CO₂, equivalente a la vida útil de 5 vehículos de combustión.

**Principio de sostenibilidad en entrenamiento:**

> Reducir el coste computacional no es solo una optimización económica: es una responsabilidad ambiental.

**ODS aplicables:**
- ODS 9 (Industria, innovación e infraestructura): eficiencia en los sistemas de IA
- ODS 12 (Producción y consumo responsables): evitar experimentos duplicados
- ODS 13 (Acción por el clima): reducir emisiones de CO₂ en operaciones de cómputo

---

## Sostenibilidad — Arquitecturas eficientes

**Elecciones de diseño que reducen el consumo computacional:**

| Decisión | Opción costosa | Opción sostenible |
|---|---|---|
| Modelo para clasificación tabular | Red neuronal profunda | Gradient Boosting (sklearn) |
| Modelo de lenguaje para dominio específico | Entrenar LLM desde cero | Fine-tuning con LoRA/QLoRA |
| Inferencia en producción | Modelo completo (FP32) | Modelo cuantizado (INT8 o FP16) |
| Escalado | GPU cluster cloud | GPU local + mixed precision |
| Búsqueda de hiperparámetros | Grid search exhaustivo | Optuna con pruning automático |

```python
# Mixed precision: reduce consumo de memoria a la mitad sin pérdida significativa
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()
with autocast():
    output = modelo(input)
    loss = criterio(output, target)
scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

---

## Sostenibilidad — Economía circular de datos y algoritmos

**Economía circular** en IA significa reutilizar el trabajo previo en lugar de duplicarlo. El registro y versionado de experimentos es la herramienta principal.

**Principios aplicados:**

- Antes de lanzar un nuevo experimento, revisar si ya existe uno con configuración similar en el registro
- Reutilizar checkpoints de experimentos anteriores como punto de partida (transfer learning interno)
- Archivar modelos descartados pero documentados: pueden ser útiles en el futuro con otros datos
- Compartir configuraciones y resultados entre equipos para evitar repetir búsquedas de hiperparámetros

```python
# Antes de lanzar un experimento, buscar si ya existe uno similar
import mlflow

cliente = mlflow.tracking.MlflowClient()
runs_previas = cliente.search_runs(
    experiment_ids=["1"],
    filter_string="params.lr = '2e-05' AND params.batch_size = '32'",
    order_by=["metrics.f1_val DESC"]
)
if runs_previas:
    print(f"Experimento similar ya existe: {runs_previas[0].info.run_id}")
    print(f"F1 obtenido: {runs_previas[0].data.metrics['f1_val']:.4f}")
```

---

## Prevención de riesgos — Riesgos psicosociales

El trabajo en proyectos de IA presenta riesgos psicosociales específicos derivados de la intensidad cognitiva, la presión de resultados y la incertidumbre técnica.

| Riesgo psicosocial | Manifestaciones | Medidas preventivas |
|---|---|---|
| **Tecnoestrés** | Ansiedad ante cambios de herramientas, sensación de obsolescencia | Plan de formación continua; no cambiar de stack en mitad de proyecto |
| **Síndrome del impostor** | Bloqueo ante tareas nuevas, comparación con pares | Mentalidad de aprendizaje; documentar logros propios |
| **Fatiga por decisión** | Dificultad para tomar decisiones tras muchas iteraciones | Timeboxing de experimentos; descansos programados |
| **Sobrecarga de información** | Incapacidad de filtrar literatura técnica relevante | Rutinas de actualización limitadas en tiempo |

---

## Prevención de riesgos — Ergonomía cognitiva

La **ergonomía cognitiva** estudia la adaptación del entorno de trabajo a las capacidades de procesamiento mental del ser humano.

**Prácticas aplicadas al trabajo en ML:**

- **Documentar las decisiones en el momento** en que se toman, no al final del día
- **Dividir experimentos complejos** en tareas pequeñas con objetivo claro por sesión
- **Usar plantillas** para configuraciones y fichas técnicas: reducen la carga cognitiva de decisión
- **Nombrar archivos y experimentos** con convenciones consistentes desde el inicio del proyecto
- **Revisar el historial de MLflow** antes de comenzar una nueva sesión de trabajo

> La ergonomía cognitiva no es comodidad: es eficiencia y calidad de decisión sostenida en el tiempo.

---

## Prevención de riesgos — Ergonomía física y ambiental

| Área | Riesgo | Medida preventiva |
|---|---|---|
| **Postura** | Dolor cervical, lumbalgia por sesiones largas ante pantalla | Silla regulable, pantalla a la altura de los ojos, reposapiés |
| **Visual** | Fatiga ocular, cefalea | Regla 20-20-20: cada 20 min, mirar a 6 m durante 20 seg |
| **Iluminación** | Deslumbramiento, contraste excesivo | Luz ambiental indirecta, modo oscuro en IDE, pantalla calibrada |
| **Temperatura y ventilación** | Disconfort, fatiga | 20-24 °C en el puesto; ventilación adecuada del hardware |
| **Ruido** | Distracción, estrés | Aislar el área de trabajo de ruidos disruptivos |
| **Sedentarismo** | Problemas cardiovasculares, metabólicos | Pausas activas cada 60 min; mesa elevable si es posible |

---

## Prevención de riesgos — Plan de emergencias

**Conocimiento obligatorio del plan de emergencias del centro:**

- Localización de las salidas de emergencia desde el puesto de trabajo
- Punto de reunión exterior asignado al área
- Localización de los extintores más próximos
- Tipo de extintor adecuado para equipos eléctricos: **CO₂ o polvo seco ABC** (nunca agua)
- Protocolo de parada segura de sistemas en ejecución antes de evacuar

**Protocolo de parada segura de entrenamiento en emergencia:**

```python
# En el script de entrenamiento, capturar señal de interrupcion
import signal, sys

def guardar_y_salir(sig, frame):
    torch.save(modelo.state_dict(), "checkpoint_emergencia.pt")
    mlflow.end_run(status="KILLED")
    sys.exit(0)

signal.signal(signal.SIGINT, guardar_y_salir)   # Ctrl+C
signal.signal(signal.SIGTERM, guardar_y_salir)  # señal del SO
```

---

## Actividad práctica — UD6

**Contexto:** Tu equipo va a comenzar una nueva iteración del clasificador de toxicidad. Esta vez el plazo es ajustado (2 semanas) y el cliente ha pedido un modelo con mayor rendimiento.

**Tareas:**

1. Identifica tres decisiones del proceso de entrenamiento que tienen implicaciones éticas. Para cada una, describe la decisión responsable y la irresponsable
2. Analiza el coste computacional de las opciones de mejora propuestas (más datos, arquitectura mayor, fine-tuning con LoRA). Justifica cuál es más sostenible y por qué
3. Diseña un plan de sesión de trabajo de 4 horas que incorpore pausas ergonómicas, timeboxing de experimentos y revisión del historial de MLflow antes de empezar
4. Describe cómo comunicarías al cliente que el modelo tiene rendimiento reducido en lenguaje informal (F1=0.71 frente a F1=0.82 global) sin entrar en tecnicismos de ML
5. Localiza en el plano del centro el extintor más próximo a tu puesto y el tipo de agente extintor que contiene

---

## Puntos clave — UD6

- La responsabilidad ética en IA es una competencia técnica: documentar sesgos, limitaciones y fallos forma parte del trabajo, no es opcional
- El coste computacional del entrenamiento tiene impacto ambiental real: la elección de arquitectura y la reutilización de experimentos son decisiones de sostenibilidad
- El registro de experimentos en MLflow no es burocracia: es la base de la economía circular de algoritmos y evita duplicar trabajo
- La ergonomía cognitiva (documentar en el momento, usar plantillas, timeboxing) mejora la calidad de las decisiones técnicas, no solo el bienestar
- El tecnoestrés y el síndrome del impostor son riesgos laborales reconocidos en perfiles técnicos: identificarlos es el primer paso para prevenirlos
- El plan de emergencias del centro es de obligatorio conocimiento; el extintor adecuado para equipos eléctricos es de CO₂ o polvo seco ABC

---

## Criterios de evaluación — UD6

| Criterio | Indicador de logro |
|---|---|
| Reduce el coste computacional por diseño | Justifica decisiones de arquitectura y parámetros con criterio de eficiencia energética |
| Evita duplicidades de experimentos | Consulta el registro antes de lanzar nuevos experimentos; reutiliza checkpoints cuando es posible |
| Comunica con adaptación al receptor | Expresa resultados y limitaciones en el lenguaje adecuado al perfil del interlocutor |
| Aplica medidas ergonómicas | Diseña su entorno y sesión de trabajo con criterios de ergonomía física y cognitiva |
| Aplica medidas de prevención de riesgos | Identifica riesgos psicosociales propios del rol y aplica medidas preventivas |
| Conoce el plan de emergencias | Localiza salidas, extintor adecuado y protocolo de parada segura del sistema |


---

<!-- nav-slide -->

## Navegación

[← UD5 · Versionado y ficha técnica de…](../UD5_Versionado-ficha-tecnica/) &nbsp;·&nbsp; [Volver al módulo](../)
