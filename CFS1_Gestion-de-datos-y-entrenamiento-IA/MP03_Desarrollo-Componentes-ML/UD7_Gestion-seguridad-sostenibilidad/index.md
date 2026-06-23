---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD7 · Gestión integral: seguridad, sostenibilidad y ética | MP03 · Desarrollo de componentes para sistemas de ML'
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

# UD7 · Gestión integral: seguridad, sostenibilidad y ética

**MP03 · Desarrollo de componentes para sistemas de ML**

CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Identificar y mitigar el tecnoestrés y otros riesgos psicosociales en el desarrollo de sistemas de ML
- Aplicar criterios de ergonomía física y usar correctamente los EPI específicos del entorno de trabajo
- Conocer y actuar conforme al plan de emergencias del centro
- Aplicar el paradigma Green AI para minimizar el consumo energético y la huella de carbono del desarrollo
- Garantizar la protección de datos y la privacidad por diseño en los componentes de ML
- Mantener un entorno de desarrollo seguro y adoptar una actitud de aprendizaje continuo

---

## El enfoque integral — Por qué no son temas separados

Seguridad, sostenibilidad y ética no son tres áreas independientes que se tratan al final del proyecto: son tres dimensiones de la misma responsabilidad profesional que deben estar presentes desde el diseño hasta el mantenimiento del componente.

**Modelo de las tres dimensiones:**

```
        SEGURIDAD
       /          \
      /            \
     /   Componente \
    /   ML de calidad\
   /__________________\
SOSTENIBILIDAD    ÉTICA
```

| Dimensión | Pregunta central | Se garantiza mediante |
|---|---|---|
| **Seguridad** | ¿Es seguro para las personas que lo usan y desarrollan? | PRL, ergonomía, EPI, plan de emergencias |
| **Sostenibilidad** | ¿Minimiza su impacto ambiental? | Green AI, eficiencia energética, huella de carbono |
| **Ética** | ¿Respeta los derechos y la privacidad? | Privacidad por diseño, protección de datos, excelencia técnica |

---

## Tecnoestrés — Concepto y manifestaciones

El **tecnoestrés** es la tensión psicológica producida por la relación con las tecnologías de la información. En el desarrollo de sistemas de ML se manifiesta de forma específica debido a la velocidad de cambio del sector, la presión de resultados y la complejidad técnica.

**Manifestaciones del tecnoestrés en perfiles ML:**

| Manifestación | Descripción | Señal de alarma |
|---|---|---|
| **Tecnosobrecarga** | Sensación de que hay demasiadas herramientas y técnicas que dominar | "No puedo seguir el ritmo de los nuevos modelos" |
| **Tecnoinvasión** | Dificultad para desconectar de los experimentos en curso | Revisar los logs de entrenamiento fuera del horario laboral |
| **Tecnocomplejidad** | Bloqueo ante sistemas o dependencias que no se comprenden bien | Parálisis ante un error de CUDA o de ONNX Runtime |
| **Tecnoinseguridad** | Miedo a quedar obsoleto por el avance de la automatización | "Los LLMs van a hacer mi trabajo" |
| **Tecnofatiga** | Agotamiento cognitivo acumulado por cambios continuos de stack | Errores por descuido en tareas que antes eran automáticas |

---

## Mitigación del tecnoestrés — Estrategias

**Estrategias individuales:**

- **Timeboxing de actualización:** reservar un tiempo fijo semanal (2-3 horas) para vigilancia tecnológica en lugar de estar en actualización constante
- **Profundidad antes que amplitud:** dominar bien las herramientas del proyecto actual antes de adoptar nuevas
- **Documentar para reducir carga mental:** un sistema bien documentado reduce la ansiedad de "si me ausento, nadie sabe cómo funciona esto"
- **Separación de entornos:** cuando el experimento termina la jornada, cerrar los notebooks y los dashboards de MLflow

**Estrategias de equipo:**

- Definir el stack tecnológico del proyecto al inicio y no cambiarlo salvo causa justificada
- Distribuir la responsabilidad de vigilancia tecnológica: cada persona sigue un área, no todas siguen todo
- Institucionalizar los tiempos de aprendizaje: no aprender "en los huecos", sino en tiempo protegido
- Celebrar los avances parciales y documentar los errores como aprendizaje, no como fracasos

---

## Ergonomía física en el desarrollo de ML

El desarrollo de sistemas de ML implica sesiones largas frente a múltiples pantallas, con carga cognitiva alta y trabajo sedentario. La evaluación ergonómica del puesto es obligatoria.

**Evaluación del puesto de trabajo con pantallas (RD 488/1997):**

| Elemento | Requisito | Consecuencia del incumplimiento |
|---|---|---|
| **Pantalla** | Inclinación ajustable; sin reflejos; 50-70 cm de distancia visual | Fatiga ocular, cefalea, tensión cervical |
| **Teclado** | Independiente y reclinable; muñecas en posición neutra | Síndrome del túnel carpiano, tendinitis |
| **Ratón** | A la misma altura que el teclado; no forzar extensión del brazo | Epicondilitis, dolor de hombro |
| **Silla** | Altura regulable; apoyo lumbar; pies apoyados en el suelo o reposapiés | Lumbalgia, cifosis postural |
| **Mesa** | Altura fija o regulable; espacio suficiente para antebrazos | Tensión en trapecios y hombros |
| **Iluminación** | 500 lux en el plano de trabajo; sin deslumbramiento directo ni reflejado | Fatiga visual, dolor de cabeza |

---

## EPI específicos del entorno de trabajo con hardware ML

En entornos con hardware de computación intensiva (GPUs, servidores de inferencia, racks de almacenamiento), pueden ser necesarios equipos de protección individual específicos.

| Situación | EPI recomendado | Norma de referencia |
|---|---|---|
| Manipulación de hardware en rack (instalación de GPU, memorias) | Pulsera antiestática o toma de tierra; guantes ESD | IEC 61340-5-1 |
| Trabajo en sala de servidores con ruido elevado (>80 dB) | Protectores auditivos (auriculares o tapones) | RD 286/2006 |
| Mantenimiento de sistemas de refrigeración líquida | Gafas de protección; guantes resistentes al refrigerante | RD 374/2001 |
| Acceso a instalaciones eléctricas de baja tensión | Guantes de clase 00 o 0; herramientas aisladas | RD 614/2001 |

> En el trabajo habitual de desarrollo de software y ML sin manipulación de hardware, el EPI principal es el ergonómico: silla, reposapiés y pantalla regulados.

---

## Plan de emergencias — Conocimiento obligatorio

**El plan de emergencias del centro define:**

- Las vías de evacuación y las salidas de emergencia desde cada puesto de trabajo
- El punto de reunión exterior asignado al área o planta
- Los responsables de emergencia (coordinador de emergencias, jefes de planta)
- El protocolo de comunicación con los servicios de emergencia (112)
- Las instrucciones específicas para equipos técnicos en operación

**Protocolo de parada segura de un componente ML en emergencia:**

```python
import signal, sys, mlflow

def parada_segura(sig, frame):
    """Guardar estado y cerrar experimentos antes de evacuar."""
    # 1. Guardar checkpoint del modelo
    if "modelo" in globals() and hasattr(modelo, "state_dict"):
        import torch
        torch.save(modelo.state_dict(), "checkpoint_emergencia.pt")

    # 2. Cerrar el run de MLflow con estado KILLED
    try:
        mlflow.end_run(status="KILLED")
    except Exception:
        pass

    print("Sistema en estado seguro. Proceder a evacuación.")
    sys.exit(0)

signal.signal(signal.SIGINT, parada_segura)
signal.signal(signal.SIGTERM, parada_segura)
```

---

## Plan de emergencias — Extintores y equipos eléctricos

**Tipos de fuego y agentes extintores:**

| Clase de fuego | Material | Agente extintor adecuado | Agente PROHIBIDO |
|---|---|---|---|
| **Clase A** | Sólidos combustibles (papel, madera) | Agua, polvo ABC | — |
| **Clase B** | Líquidos inflamables | Polvo ABC, CO₂, espuma | Agua |
| **Clase C** | Gases inflamables | Polvo ABC | Agua |
| **Clase E** (eléctrico) | Equipos eléctricos bajo tensión | **CO₂, polvo seco ABC** | **Agua, espuma** (conducen electricidad) |

> Para equipos informáticos e instalaciones eléctricas: usar siempre extintor de **CO₂** (preferido, no deja residuo) o **polvo seco ABC**. Nunca agua ni espuma.

**Antes de usar el extintor en equipos eléctricos:**
1. Evaluar si es seguro cortar la alimentación eléctrica antes de actuar
2. Mantener al menos 1 m de distancia con el extintor de CO₂
3. Evacuar si el fuego no se controla en los primeros 30 segundos

---

## Green AI — El paradigma de la IA sostenible

El paradigma **Green AI** propone que la eficiencia energética y la minimización de la huella de carbono sean criterios de diseño de primera clase en el desarrollo de sistemas de ML, al mismo nivel que el rendimiento o la precisión.

**El coste ambiental del ML a escala:**

| Actividad | Emisiones de CO₂ estimadas | Equivalente |
|---|---|---|
| Entrenamiento de GPT-3 (2020) | ~500 t CO₂ | Vida útil de 5 coches de combustión |
| Entrenamiento de BLOOM (2022) | ~25 t CO₂ | 50 vuelos Madrid-Nueva York |
| Inferencia de ChatGPT (por consulta) | ~0.5 g CO₂ | 10 consultas Google = 1 consulta ChatGPT |
| Entrenamiento con GPU A100 (1 hora) | ~0.4 kg CO₂ | Depende de la fuente energética del datacenter |

> La mayoría de las aplicaciones profesionales no requieren modelos de escala GPT. Elegir la arquitectura más pequeña que resuelva el problema es siempre la decisión más sostenible.

---

## Green AI — Principios aplicados al desarrollo de componentes

**Cuatro principios de Green AI en el ciclo de desarrollo:**

### 1. Arquitectura mínima suficiente
Usar el modelo más simple que alcance el rendimiento requerido. No usar un LLM para una tarea de clasificación tabular que resuelve un GBM con el 5 % del coste energético.

### 2. Reutilización antes que reentrenamiento
Fine-tuning de modelos preentrenados en lugar de entrenamiento desde cero. Transfer learning reduce el coste computacional en 10-100x.

### 3. Eficiencia en inferencia
Cuantización, destilación y pruning para reducir el tamaño del modelo en producción sin pérdida significativa de rendimiento.

### 4. Medición de la huella de carbono
No se puede reducir lo que no se mide. Usar herramientas como `codecarbon` o `carbontracker` para medir el impacto de cada experimento.

---

## Green AI — Medición de la huella de carbono

```python
from codecarbon import EmissionsTracker

# Inicializar el tracker antes del proceso que se quiere medir
tracker = EmissionsTracker(
    project_name="clasificador-toxicidad-v1.2",
    output_dir="carbon_reports/",
    country_iso_code="ESP"   # Intensidad de carbono de la red eléctrica española
)

tracker.start()

# --- Proceso de entrenamiento ---
modelo.fit(X_train, y_train)
# --- Fin del proceso ---

emisiones = tracker.stop()  # en kg de CO₂ equivalente

print(f"Emisiones del entrenamiento: {emisiones * 1000:.2f} g CO₂e")
print(f"Equivale a {emisiones / 0.21:.1f} km en coche de combustión")

# Los resultados se guardan automáticamente en carbon_reports/emissions.csv
# Incluir este fichero en el repositorio Git para trazabilidad ambiental
```

---

## Green AI — Cuantización para reducir huella en producción

La **cuantización** reduce la precisión numérica de los pesos del modelo (de FP32 a FP16 o INT8), disminuyendo el consumo de memoria y aumentando la velocidad de inferencia con una pérdida mínima de rendimiento.

```python
import torch
from torch.quantization import quantize_dynamic

# Cargar el modelo en FP32
modelo_fp32 = torch.load("modelos/clasificador_fp32.pt")
modelo_fp32.eval()

# Cuantización dinámica a INT8 (sin necesidad de datos de calibración)
modelo_int8 = quantize_dynamic(
    modelo_fp32,
    {torch.nn.Linear},   # capas a cuantizar
    dtype=torch.qint8
)

# Comparar tamaño y velocidad
import os
torch.save(modelo_fp32.state_dict(), "modelos/fp32.pt")
torch.save(modelo_int8.state_dict(), "modelos/int8.pt")

tamano_fp32 = os.path.getsize("modelos/fp32.pt") / 1e6
tamano_int8 = os.path.getsize("modelos/int8.pt") / 1e6
print(f"FP32: {tamano_fp32:.1f} MB  |  INT8: {tamano_int8:.1f} MB")
print(f"Reducción: {(1 - tamano_int8/tamano_fp32)*100:.0f} %")
```

---

## Protección de datos y privacidad por diseño

La **privacidad por diseño** (*Privacy by Design*) es el principio del RGPD (Art. 25) que exige incorporar la protección de datos desde el inicio del desarrollo, no como un añadido posterior.

**Los 7 principios de Privacidad por Diseño en el contexto de componentes ML:**

| Principio | Aplicación en componentes ML |
|---|---|
| **Proactivo, no reactivo** | Identificar riesgos de privacidad en el diseño, antes de implementar |
| **Privacidad por defecto** | El componente no recoge más datos de los estrictamente necesarios para la inferencia |
| **Privacidad integrada** | Las transformaciones de anonimización forman parte del pipeline, no son un paso adicional |
| **Funcionalidad total** | La privacidad no reduce la utilidad: diseñar para que ambas sean compatibles |
| **Seguridad de extremo a extremo** | Cifrar datos en tránsito y en reposo; controlar el acceso a los modelos |
| **Visibilidad y transparencia** | Documentar qué datos usa el modelo y con qué propósito (model card) |
| **Respeto al usuario** | El modelo no debe usarse para fines distintos a los documentados |

---

## Protección de datos — Técnicas de anonimización en ML

```python
import pandas as pd
import hashlib
from faker import Faker

fake = Faker("es_ES")

def anonimizar_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica técnicas de anonimización para eliminar datos de identificación directa.
    """
    df = df.copy()

    # 1. Pseudoanonimización: reemplazar identificadores por hash irreversible
    if "nif" in df.columns:
        df["nif"] = df["nif"].apply(
            lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16]
        )

    # 2. Generalización: reducir precisión de atributos cuasi-identificadores
    if "edad" in df.columns:
        df["grupo_edad"] = pd.cut(df["edad"],
            bins=[0, 25, 35, 45, 55, 65, 100],
            labels=["<25", "25-34", "35-44", "45-54", "55-64", "65+"])
        df = df.drop(columns=["edad"])

    # 3. Supresión: eliminar columnas con alto riesgo de reidentificación
    columnas_a_eliminar = ["nombre", "apellidos", "email", "telefono", "direccion"]
    df = df.drop(columns=[c for c in columnas_a_eliminar if c in df.columns])

    return df
```

---

## Excelencia técnica y aprendizaje continuo

La **excelencia técnica** en el desarrollo de componentes ML no es un estándar fijo: es un compromiso de mejorar continuamente la calidad del código, las prácticas de desarrollo y el conocimiento del dominio.

**Indicadores de excelencia técnica en un equipo de ML:**

| Indicador | Práctica concreta |
|---|---|
| **Código revisado** | Todos los cambios pasan por pull request con al menos un revisor |
| **Tests automatizados** | Cobertura de tests > 80 % para los componentes críticos |
| **Documentación actualizada** | La model card se actualiza en el mismo commit que el modelo |
| **Deuda técnica gestionada** | Los `TODO` y `FIXME` tienen issue vinculada y responsable asignado |
| **Revisiones de arquitectura** | Cambios de diseño importantes pasan por ADR (Architecture Decision Record) |
| **Actualización de dependencias** | Revisión trimestral de vulnerabilidades con `pip audit` o `safety` |

```bash
# Auditar vulnerabilidades en las dependencias del proyecto
pip install pip-audit
pip-audit --require-hashes -r requirements.txt
```

---

## Integración de las tres dimensiones en el ciclo de desarrollo

**Mapa de prácticas por fase del proyecto:**

| Fase | Seguridad | Sostenibilidad | Ética |
|---|---|---|---|
| **Diseño** | Evaluar ergonomía del entorno; identificar riesgos psicosociales | Elegir la arquitectura mínima suficiente; estimar huella de carbono | Analizar implicaciones de privacidad; identificar colectivos afectados |
| **Implementación** | Aplicar EPI si hay manipulación de hardware | Cachear etapas costosas; usar tipos de dato eficientes | Implementar privacidad por diseño; anonimizar desde el pipeline |
| **Pruebas** | Verificar que el entorno de pruebas es ergonómico | Medir el coste energético de la suite de tests | Auditar sesgos por subgrupo; verificar el cumplimiento del RGPD |
| **Despliegue** | Conocer el plan de emergencias de los sistemas en producción | Cuantizar el modelo para reducir el consumo de inferencia | Publicar la model card completa con limitaciones y sesgos |
| **Mantenimiento** | Vigilar señales de tecnoestrés en el equipo | Monitorizar la huella de carbono en producción | Revisar la model card tras cada reentrenamiento |

---

## Actividad práctica — UD7

**Contexto:** El componente clasificador de toxicidad está a punto de desplegarse en producción en una plataforma educativa con 50 000 usuarios. Antes del despliegue, debes realizar una revisión integral de seguridad, sostenibilidad y ética.

**Tareas:**

1. Identifica tres riesgos de tecnoestrés presentes en el proyecto (plazo ajustado, cambios de requisitos, complejidad técnica) y propón una medida preventiva concreta para cada uno
2. Instrumenta el entrenamiento del componente con `codecarbon` y genera un informe de emisiones. Compara el consumo del modelo completo (FP32) frente al modelo cuantizado (INT8) en una sesión de inferencia de 1000 predicciones
3. Aplica la función de anonimización vista en la unidad al dataset de evaluación. Verifica que no quedan columnas de identificación directa
4. Completa la tabla de integración de las tres dimensiones para el ciclo de vida de este componente concreto
5. Redacta un ADR para la decisión de cuantizar el modelo en producción, siguiendo el formato estándar

---

## Puntos clave — UD7

- El tecnoestrés es un riesgo laboral reconocido en perfiles de IA/ML: gestionarlo requiere protocolos de equipo, no solo resiliencia individual
- El extintor adecuado para equipos eléctricos es CO₂ o polvo seco ABC: usar agua o espuma ante un fuego eléctrico puede ser mortal
- Green AI no es un ideal: es una práctica concreta que empieza por elegir la arquitectura mínima suficiente y medir la huella de carbono con herramientas como `codecarbon`
- La cuantización reduce el tamaño del modelo y el consumo de inferencia entre un 50 % y un 75 % con una pérdida de rendimiento normalmente inferior al 1-2 %
- La privacidad por diseño no es una restricción: es una práctica de ingeniería que integra la protección de datos en el pipeline desde el inicio, haciendo el sistema más robusto y auditable
- La excelencia técnica (revisiones de código, tests, documentación actualizada) y el aprendizaje continuo no son opcionales: son los mecanismos que mantienen la calidad del componente a lo largo del tiempo

---

## Criterios de evaluación — UD7

| Criterio | Indicador de logro |
|---|---|
| Aplica criterios de Green AI | Mide la huella de carbono del desarrollo; cuantiza el modelo para producción; elige la arquitectura mínima suficiente |
| Garantiza protección de datos | Implementa anonimización en el pipeline; documenta el tratamiento de datos en la model card; aplica privacidad por diseño |
| Mantiene un entorno seguro | Identifica riesgos psicosociales y aplica medidas preventivas; cumple los requisitos ergonómicos del puesto; conoce el plan de emergencias |
| Aplica EPI correctamente | Identifica los EPI necesarios para el entorno de trabajo específico y los usa conforme a la normativa |
| Demuestra excelencia técnica | Mantiene documentación actualizada, tests con cobertura adecuada y revisiones de código sistemáticas |
| Adopta actitud de aprendizaje continuo | Integra la vigilancia tecnológica en su rutina profesional y transfiere los hallazgos al equipo |

---

<!-- _class: lead -->

[← Volver a MP03](../)


---

<!-- nav-slide -->

## Navegación

[← UD6 · Vigilancia tecnológica](../UD6_Vigilancia-tecnologica/) &nbsp;·&nbsp; [Volver al módulo](../)
