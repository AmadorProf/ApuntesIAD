# UD7 · Responsabilidad, sostenibilidad y PRL en infraestructuras LLM

---

## 1. Introducción

La operación de infraestructuras para modelos de lenguaje de gran tamaño tiene consecuencias que trascienden el ámbito técnico estricto y alcanzan dimensiones medioambientales, éticas y de seguridad y salud laboral que el técnico responsable de estas infraestructuras debe conocer, gestionar y documentar. El impacto ambiental de los LLMs ha pasado de ser una preocupación académica a convertirse en un factor que reguladores, clientes corporativos e inversores evalúan activamente al tomar decisiones sobre los sistemas de IA que adoptan. La Unión Europea, a través del EU AI Act y de la Directiva de Informes de Sostenibilidad Corporativa (CSRD), está estableciendo marcos de reporte de impacto ambiental de sistemas tecnológicos que incluirán progresivamente a los sistemas de IA.

El impacto medioambiental de los LLMs tiene dos dimensiones bien diferenciadas. El **coste de entrenamiento** —el más citado en la literatura y en los medios— es un coste único pero extraordinariamente intensivo: el entrenamiento de modelos fundacionales como GPT-4 o LLaMA 3 requiere miles de GPUs H100 operando durante semanas o meses, con un consumo energético que puede superar los gigavatios-hora y unas emisiones de CO₂ equivalente que se miden en cientos o miles de toneladas. El **coste de inferencia**, sin embargo, es un coste continuo que se acumula con cada solicitud procesada y que, agregado a escala de millones de usuarios, puede superar con creces el coste de entrenamiento a lo largo del ciclo de vida del modelo. Desde la perspectiva del técnico de infraestructura, el coste de inferencia es el que debe optimizarse, ya que el entrenamiento raramente es responsabilidad del equipo de explotación.

La responsabilidad ética en el uso de LLMs en organizaciones abarca dimensiones que van más allá de los requisitos regulatorios del EU AI Act. Los modelos de lenguaje heredan y pueden amplificar los sesgos presentes en sus datos de entrenamiento, pueden generar outputs dañinos con consecuencias reales para personas concretas, y su utilización en procesos de toma de decisiones plantea cuestiones de accountability que deben ser abordadas explícitamente. El técnico que opera la infraestructura no es el único responsable de estos aspectos —la responsabilidad es compartida con los desarrolladores del modelo, los proveedores de datos y la dirección de la organización— pero su rol lo sitúa en una posición única para detectar y escalar problemas de este tipo.

La prevención de riesgos laborales (PRL) para los técnicos que operan infraestructuras LLM comparte muchos elementos con la PRL de cualquier trabajo en centros de datos u oficinas técnicas, pero tiene particularidades derivadas de los patrones de trabajo propios de la operación de sistemas de alta disponibilidad: el trabajo en guardia, la gestión de incidentes fuera del horario laboral habitual, la presión cognitiva en situaciones de degradación del servicio y los riesgos ergonómicos del trabajo continuado con múltiples pantallas. Esta unidad aborda todos estos aspectos con rigor y proporciona al futuro técnico de infraestructura LLM las herramientas para integrarlos en su práctica profesional cotidiana.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Estimar la huella de carbono de un modelo LLM en inferencia utilizando herramientas especializadas (CodeCarbon, zeus-monitor, nvidia-smi) y expresar los resultados en unidades estándar (gCO₂eq/token, kWh por millón de tokens).
2. Identificar y comparar las principales estrategias de reducción del impacto ambiental de las infraestructuras LLM: selección de modelos eficientes, cuantización, batching, elección del proveedor de computación por origen de energía.
3. Aplicar las herramientas de monitorización de consumo energético (CodeCarbon, zeus-monitor, nvidia-smi power monitoring) a un servidor de inferencia real y analizar los resultados.
4. Describir los mecanismos por los que los LLMs pueden perpetuar o amplificar sesgos y proponer medidas técnicas y organizativas para detectarlos y mitigarlos.
5. Identificar los requisitos del EU AI Act aplicables a modelos GPAI (General Purpose AI) en términos de reporte de eficiencia energética, red-teaming y notificación de incidentes.
6. Aplicar la normativa de PRL española (Ley 31/1995, RD 488/1997 sobre pantallas de visualización) a los puestos de trabajo de operación de infraestructuras LLM.
7. Diseñar un plan de gestión del riesgo psicosocial para equipos en guardia que operan sistemas LLM de alta disponibilidad.
8. Redactar la documentación de impacto ambiental y responsabilidad de una infraestructura LLM conforme a los marcos de reporte exigibles.

---

## 3. Huella de carbono de los LLMs

### 3.1 Unidades y magnitudes de referencia

El impacto ambiental de los sistemas computacionales se expresa habitualmente en las siguientes unidades:

| Unidad | Significado | Uso típico |
|---|---|---|
| kWh | Kilovatio-hora de energía eléctrica consumida | Medición directa del consumo energético |
| gCO₂eq | Gramos de CO₂ equivalente emitidos | Impacto climático de una unidad de procesamiento |
| gCO₂eq/token | Emisiones por token generado | Eficiencia de un modelo en inferencia |
| PUE | Power Usage Effectiveness = energía total / energía IT | Eficiencia del centro de datos |
| WUE | Water Usage Effectiveness = agua usada / energía IT | Impacto en consumo de agua |

La relación entre consumo energético y emisiones de CO₂ depende del **mix eléctrico** del país o región donde opera la infraestructura. Un servidor que consume 100 kWh en Francia (mix mayoritariamente nuclear, ~52 gCO₂eq/kWh) emite aproximadamente 10 veces menos CO₂ que el mismo servidor operando en Polonia (mix mayoritariamente carbón, ~700 gCO₂eq/kWh).

### 3.2 Coste energético del entrenamiento: magnitudes publicadas

| Modelo | FLOPs de entrenamiento | Consumo estimado (MWh) | CO₂eq estimado |
|---|---|---|---|
| GPT-3 (175B) | 3.14 × 10²³ | ~1.300 MWh | ~552 ton CO₂eq |
| LLaMA 2 (70B) | ~2 × 10²³ | ~1.700 MWh | ~500 ton CO₂eq |
| LLaMA 3.1 (405B) | ~3.8 × 10²⁴ | ~39.000 MWh | ~11.000 ton CO₂eq |
| Mistral 7B | ~6 × 10²² | ~200 MWh | Estimado <100 ton CO₂eq |
| Gemma 7B (Google) | Publicado: ~21 ton CO₂eq | — | 21 ton CO₂eq |

Nota: las estimaciones de consumo varían significativamente según la fuente y la metodología. Los valores anteriores son estimaciones publicadas en la literatura o por los propios desarrolladores y deben tratarse como órdenes de magnitud.

### 3.3 Coste energético de la inferencia

El coste energético por solicitud depende del modelo, el hardware, la longitud del prompt y la respuesta, y la eficiencia del framework de inferencia. Algunas referencias publicadas:

```
GPT-4 (estimación, OpenAI):    ~0.001-0.01 kWh por consulta (resp. típica)
LLaMA 3.1 8B en A100:          ~0.0003-0.001 kWh por consulta (resp. típica)
LLaMA 3.1 70B en 4×H100:       ~0.003-0.01 kWh por consulta
```

Para un servicio con 1 millón de consultas/día a LLaMA 3.1 8B:
- Consumo estimado: 0.0005 kWh × 1.000.000 = **500 kWh/día = 182,5 MWh/año**
- Emisiones (Francia, 52 gCO₂eq/kWh): 182.500 × 52 ≈ **9,5 ton CO₂eq/año**
- Emisiones (Polonia, 700 gCO₂eq/kWh): 182.500 × 700 ≈ **127,7 ton CO₂eq/año**

---

## 4. Herramientas de medición de consumo energético

### 4.1 CodeCarbon

**CodeCarbon** es la biblioteca Python más utilizada para medir el consumo de carbono de código computacional. Estima el consumo energético de la CPU, GPU y RAM, y lo convierte en emisiones de CO₂eq usando los datos del mix eléctrico del país donde se ejecuta:

```python
from codecarbon import EmissionsTracker
import openai

tracker = EmissionsTracker(
    project_name="llm-inference-audit",
    country_iso_code="ESP",          # España
    region="community_of_madrid",
    output_dir="./carbon_reports",
    save_to_file=True,
    log_level="warning"
)

# Medir el consumo de una sesión de inferencia
tracker.start()

client = openai.OpenAI(base_url="http://localhost:8000/v1")
for i in range(100):
    client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=[{"role": "user", "content": f"Solicitud de prueba número {i}."}],
        max_tokens=128,
        temperature=0
    )

emissions = tracker.stop()
print(f"Emisiones totales: {emissions:.6f} kg CO₂eq")
print(f"Por solicitud: {emissions/100*1000:.4f} gCO₂eq")
```

CodeCarbon genera un fichero CSV con el historial de mediciones y un informe en el directorio especificado. Para infraestructuras en producción, puede configurarse en modo daemon para monitorización continua.

### 4.2 zeus-monitor

**zeus-monitor** es una herramienta de monitorización del consumo energético de GPUs NVIDIA desarrollada por la Universidad de Michigan. Es más preciso que CodeCarbon para mediciones a nivel de GPU, ya que lee directamente los registros de potencia del hardware:

```bash
# Instalación
pip install zeus-ml

# Monitorización del consumo durante la inferencia
python -m zeus.monitor.power \
    --pid $(pgrep -f "vllm.entrypoints") \
    --gpu 0,1,2,3 \
    --output power_log.csv \
    --interval 1000   # Muestreo cada 1000 ms
```

```python
# Integración en código Python
from zeus.monitor import ZeusMonitor

monitor = ZeusMonitor(gpu_indices=[0, 1, 2, 3])

monitor.begin_window("inferencia_batch")

# ... código de inferencia ...

measurement = monitor.end_window("inferencia_batch")
print(f"Energía GPU total: {measurement.total_energy:.2f} J")
print(f"Potencia media GPU 0: {measurement.gpu[0].average_power:.1f} W")
```

### 4.3 nvidia-smi para monitorización de potencia

`nvidia-smi` proporciona datos de potencia en tiempo real sin necesidad de software adicional:

```bash
# Monitorización continua de potencia y temperatura
nvidia-smi dmon -s pu -d 1 -f power_log.csv
# -s pu: potencia (p) y utilización (u)
# -d 1: muestreo cada 1 segundo

# Consulta puntual de consumo de potencia
nvidia-smi --query-gpu=index,name,power.draw,power.limit,temperature.gpu \
           --format=csv,noheader,nounits

# Establecer límite de potencia (TDP capping) para reducir consumo
# Requiere permisos de root
sudo nvidia-smi -pl 250   # Limitar a 250W (vs 400W por defecto en H100 SXM)
```

El **TDP capping** (limitación de la potencia máxima de diseño) es una técnica de gestión de energía que reduce el consumo de la GPU en un 20-30% a cambio de una degradación del rendimiento del 5-15%. En muchos contextos de producción es un equilibrio aceptable que reduce significativamente la huella energética.

---

## 5. Estrategias de reducción del impacto ambiental

### 5.1 Selección de modelos eficientes

La selección del modelo más pequeño que cumple los requisitos de calidad del caso de uso es la decisión con mayor impacto en la sostenibilidad de la infraestructura. Un modelo de 7B parámetros puede consumir 10-20 veces menos energía por token que un modelo de 70B, con una diferencia de calidad que en muchos casos de uso concretos es irrelevante o insignificante.

```python
# Comparativa de consumo energético estimado por token (GPU A100 80GB)
MODELOS_EFICIENCIA = {
    "llama-3.2-1b": {"params_B": 1, "tokens_per_sec": 800, "power_W": 120},
    "llama-3.1-8b": {"params_B": 8, "tokens_per_sec": 350, "power_W": 280},
    "llama-3.1-70b-awq": {"params_B": 70, "tokens_per_sec": 80, "power_W": 320},  # 4xA100
    "llama-3.1-70b": {"params_B": 70, "tokens_per_sec": 40, "power_W": 1200},     # 4xA100
}

def energia_por_millon_tokens(modelo: str) -> float:
    """Calcula el consumo en Wh por millón de tokens generados."""
    m = MODELOS_EFICIENCIA[modelo]
    tiempo_seg = 1_000_000 / m["tokens_per_sec"]
    energia_wh = m["power_W"] * tiempo_seg / 3600
    return energia_wh

for nombre, _ in MODELOS_EFICIENCIA.items():
    print(f"{nombre}: {energia_por_millon_tokens(nombre):.1f} Wh/M tokens")
```

### 5.2 Cuantización como medida de sostenibilidad

La cuantización reduce el tamaño de los pesos del modelo y acelera la inferencia, lo que se traduce directamente en una reducción del consumo energético:

| Técnica | Precisión | Reducción de memoria | Reducción de consumo | Impacto en calidad |
|---|---|---|---|---|
| FP16 (baseline) | 16 bits | — | — | Referencia |
| BF16 | 16 bits | ~0% vs FP16 | ~0% vs FP16 | Equivalente a FP16 |
| FP8 | 8 bits | ~50% | ~30-40% | Muy bajo (<1%) |
| INT8 (LLM.int8) | 8 bits | ~50% | ~30% | Bajo (<2%) |
| AWQ INT4 | 4 bits | ~75% | ~50-60% | Bajo-medio (<3%) |
| GGUF Q4_K_M | 4.5 bits | ~70% | ~50% | Bajo-medio |

### 5.3 Batching y eficiencia de hardware

El **continuous batching** que implementan frameworks como vLLM y TGI agrupa múltiples solicitudes para su procesamiento conjunto, aumentando la utilización de la GPU y reduciendo el consumo energético por token. Un servidor que procesa solicitudes de una en una tiene una utilización de GPU típica del 20-40%; el mismo servidor con continuous batching puede alcanzar el 80-95%:

```bash
# Monitorizar la utilización de GPU durante la inferencia
nvidia-smi dmon -s u -d 5 | awk 'NR>2 {print $2, $3}' | \
    awk '{sum+=$1; count++} END {print "Utilización GPU media:", sum/count "%"}'
```

### 5.4 Ubicación geográfica e impacto del mix eléctrico

La elección del proveedor cloud y la región de despliegue tiene un impacto de hasta un orden de magnitud en las emisiones de CO₂ de la misma carga de trabajo:

| Región / Proveedor | Mix eléctrico | gCO₂eq/kWh (aprox.) |
|---|---|---|
| GCP us-east4 (Virginia) | Mixto, compra de renovables | ~100-150 |
| AWS eu-west-3 (París) | Nuclear + renovables | ~50-80 |
| Azure northeurope (Irlanda) | Renovables + gas | ~200-300 |
| AWS eu-south-2 (España) | Renovables + gas | ~150-200 |
| GCP europe-north1 (Finlandia) | Hidro + nuclear | ~30-50 |
| Cualquier región carbón-intensiva | Carbón + gas | ~500-800 |

---

## 6. Responsabilidad ética en el uso de LLMs

### 6.1 Sesgos en modelos de lenguaje

Los LLMs aprenden de corpus de texto masivos que reflejan los sesgos presentes en la producción cultural y textual humana. Los tipos de sesgo más documentados son:

**Sesgo de representación**: los grupos subrepresentados en los datos de entrenamiento (por idioma, geografía, género, etnia) tienen peor rendimiento del modelo en tareas que les conciernen. Un LLM entrenado mayoritariamente en inglés puede tener un rendimiento significativamente inferior en español o en lenguas minoritarias.

**Sesgo de asignación**: el modelo asocia sistemáticamente determinados atributos, roles o cualidades a grupos demográficos de forma estereotipada. Por ejemplo, asociar profesiones de alta cualificación predominantemente con determinados géneros o etnias.

**Sesgo de evaluación diferencial**: el modelo trata de forma diferente textos semánticamente equivalentes según los grupos a los que hacen referencia.

Para detectar sesgos en el modelo desplegado, se utilizan benchmarks específicos como BBQ (Bias Benchmark for QA), WinoBias y StereoSet:

```bash
# Evaluación de sesgos con lm-evaluation-harness
lm_eval \
    --model local-chat-completions \
    --model_args model=llama-3.1-8b,base_url=http://localhost:8000/v1 \
    --tasks bbq,winobias \
    --output_path ./eval_results/bias_eval
```

### 6.2 Outputs dañinos y uso responsable

Un LLM puede generar outputs dañinos en varias categorías: desinformación y contenido factualmente incorrecto presentado con falsa seguridad, contenido discriminatorio o de odio, instrucciones para actividades ilegales o peligrosas, y contenido que vulnera la privacidad o los derechos de personas concretas.

Las medidas técnicas de mitigación ya se han abordado en la UD6 (guardrails). Las medidas organizativas complementarias son:

- **Política de uso aceptable** (Acceptable Use Policy, AUP): documento público que especifica para qué puede y no puede usarse el servicio LLM.
- **Proceso de red-teaming**: ejercicio estructurado en el que un equipo dedicado intenta provocar outputs dañinos del sistema para identificar vulnerabilidades antes de la apertura al público.
- **Canal de reporte de incidentes**: mecanismo accesible para que los usuarios reporten comportamientos inapropiados del sistema.
- **Revisión humana de casos edge**: protocolo para la revisión humana de solicitudes o respuestas que los guardrails automáticos no pueden clasificar con certeza.

### 6.3 Requisitos del EU AI Act para modelos GPAI

Los **modelos de IA de uso general (GPAI)** con más de 10²⁵ FLOPs de entrenamiento están sujetos a obligaciones adicionales bajo el EU AI Act (Capítulo V, artículos 51-55):

| Obligación | Artículo | Descripción |
|---|---|---|
| Documentación técnica | Art. 53.1.a | Información sobre el proceso de entrenamiento, datos y parámetros |
| Política de uso aceptable | Art. 53.1.b | Descripción de los usos permitidos y prohibidos |
| Cumplimiento de copyright | Art. 53.1.c | Resumen de los datos usados en entrenamiento y conformidad con directiva UE |
| Reporte de eficiencia energética | Art. 53.1.d | Consumo energético conocido del entrenamiento |
| Registro en la base de datos UE | Art. 53.2 | Modelos disponibles públicamente deben registrarse |
| Red-teaming adversarial | Art. 55.1.a | Evaluación de capacidades del modelo ante prompts adversariales |
| Notificación de incidentes graves | Art. 55.1.b | Notificación a la Comisión de incidentes graves o brechas de seguridad |
| Ciberseguridad | Art. 55.1.c | Protección contra intentos de alterar el comportamiento del modelo |

---

## 7. Prevención de riesgos laborales

### 7.1 Marco normativo de PRL en España

El marco normativo de referencia para la prevención de riesgos laborales en España es:

- **Ley 31/1995, de 8 de noviembre, de Prevención de Riesgos Laborales**: establece los principios generales, obligaciones del empresario y derechos de los trabajadores.
- **Real Decreto 39/1997**: Reglamento de los Servicios de Prevención.
- **Real Decreto 488/1997, de 14 de abril**: disposiciones mínimas de seguridad y salud relativas al trabajo con **equipos que incluyen pantallas de visualización** (PVD). Es el reglamento más directamente aplicable al trabajo de operación de infraestructuras LLM.

El RD 488/1997 exige:
- Análisis de los puestos de trabajo con pantallas de visualización.
- Formación específica en el uso de los equipos y en los riesgos del puesto.
- Vigilancia periódica de la salud de los trabajadores.
- Planificación de pausas y cambios de actividad.
- Corrección de los problemas ergonómicos identificados.

### 7.2 Riesgos ergonómicos en operación de infraestructuras LLM

Los técnicos de operación de infraestructuras LLM trabajan típicamente con múltiples monitores (tableros de control, logs, terminales) durante jornadas largas. Los riesgos ergonómicos principales son:

**Riesgos visuales**:
- Fatiga visual por exposición prolongada a pantallas.
- Síntomas: ojos secos, irritación, visión borrosa, cefaleas.
- Medidas: regla 20-20-20 (cada 20 min, mirar a 20 pies durante 20 segundos), reducción del brillo, filtros de luz azul.

**Riesgos musculoesqueléticos**:
- Contracturas cervicales y dorsales por postura estática prolongada.
- Síndrome del túnel carpiano por uso intensivo de teclado y ratón.
- Medidas: silla ergonómica regulable, monitor a la altura de los ojos, teclado y ratón ergonómicos, pausas activas cada 50-60 minutos.

**Evaluación ergonómica del puesto** (conforme al RD 488/1997):
```
Lista de verificación mínima:
□ Silla regulable en altura, profundidad de asiento y respaldo
□ Mesa a altura adecuada (aprox. 70-75 cm para trabajo sentado)
□ Monitor a distancia de 50-70 cm y con el borde superior a la altura de los ojos
□ Iluminación sin reflejos directos en la pantalla (400-500 lux en el puesto)
□ Temperatura entre 17-27°C, humedad relativa 30-70%
□ Teclado separado del monitor, inclinación ajustable
□ Reposapiés si los pies no llegan al suelo
□ Espacio suficiente para cambios de postura
```

### 7.3 Riesgos psicosociales: trabajo en guardia y alta disponibilidad

El trabajo en sistemas LLM de alta disponibilidad implica frecuentemente modalidades de trabajo que presentan riesgos psicosociales específicos:

**Guardia localizada y guardias de disponibilidad**:
- El técnico está disponible fuera de su horario habitual para atender incidentes.
- Riesgo: interferencia con el descanso y la vida personal, dificultad para desconectar.
- Marco normativo: Estatuto de los Trabajadores (arts. 34-37), Convenio Colectivo del sector.

**Turnos de trabajo**:
- Los centros de datos que operan servicios LLM 24/7 requieren turnos rotativos.
- Riesgo: alteración del ritmo circadiano, problemas de sueño, impacto en la vida familiar.
- Medidas: rotación de turnos en sentido horario (mañana → tarde → noche), información y formación sobre higiene del sueño.

**Estrés en situaciones de incidente**:
- La resolución de un incidente de producción en un sistema LLM puede requerir trabajo intenso bajo presión temporal con impacto real en el servicio.
- Riesgo: estrés agudo, ansiedad, síntomas físicos asociados.
- Medidas: procedimientos de gestión de incidentes claros (runbooks), distribución de la responsabilidad en guardia (rotación de on-call), cultura de blameless postmortems.

### 7.4 Plan de gestión del riesgo psicosocial para equipos de operación LLM

Un plan de gestión del riesgo psicosocial para un equipo de operación LLM debe incluir los siguientes elementos:

1. **Evaluación inicial de riesgos psicosociales**: mediante cuestionario validado (ISTAS21/CoPsoQ) o método del INSST, con periodicidad mínima anual.

2. **Política de guardia sostenible**:
   - Rotación de guardia entre todos los miembros del equipo con capacitación suficiente.
   - Compensación adecuada del tiempo en guardia y del tiempo de descanso tras incidentes nocturnos.
   - Definición de niveles de servicio que delimiten qué incidencias requieren intervención inmediata y cuáles pueden esperar.

3. **Procedimientos de incidente (runbooks)**:
   - Cada incidente recurrente tiene un runbook documentado que reduce la carga cognitiva y el tiempo de resolución.
   - Los runbooks se mantienen actualizados y se revisan periódicamente.

4. **Cultura de blameless postmortem**:
   - Tras cada incidente significativo, se realiza un análisis post-mortem sin culpa individual, centrado en los factores sistémicos.
   - Los aprendizajes se documentan y se integran en los runbooks y en los procesos.

5. **Formación en gestión del estrés y bienestar**:
   - Formación en técnicas de gestión del estrés y desconexión digital.
   - Acceso a servicios de apoyo psicológico (EAP: Employee Assistance Program) si el convenio lo contempla.

---

## 8. Documentación de impacto ambiental y social

### 8.1 Informe de impacto ambiental de la infraestructura LLM

El informe de impacto ambiental documenta el consumo energético y las emisiones de CO₂ de la infraestructura LLM durante un período determinado. Los elementos mínimos que debe incluir son:

```markdown
# Informe de impacto ambiental — Infraestructura LLM [Nombre del servicio]
**Período**: [Fecha inicio] — [Fecha fin]
**Responsable**: [Nombre y cargo]

## 1. Inventario de hardware
- Número y modelo de GPUs
- Servidores de inferencia (CPU, RAM)
- Infraestructura de red y almacenamiento
- Centro de datos: ubicación, PUE declarado

## 2. Consumo energético
- Consumo total del período: X kWh
- Consumo por componente (GPU, CPU, red, almacenamiento): desglose
- Consumo medio por token generado: X Wh/M tokens

## 3. Emisiones de CO₂ equivalente
- Factor de emisión del mix eléctrico: X gCO₂eq/kWh (fuente y período)
- Emisiones totales del período: X kg CO₂eq
- Emisiones por token generado: X µgCO₂eq/token

## 4. Comparativa con período anterior / versión anterior del modelo
- Variación en consumo energético: +/-X%
- Variación en emisiones: +/-X%
- Causa principal de la variación

## 5. Medidas de reducción implementadas
- Descripción de medidas aplicadas (cuantización, batching, TDP capping, etc.)
- Impacto estimado de cada medida

## 6. Objetivos del próximo período
- Objetivo de reducción de emisiones
- Medidas planificadas para alcanzarlo
```

### 8.2 Registro de impacto social

Complementariamente al informe ambiental, el registro de impacto social documenta los aspectos éticos y de responsabilidad del uso del sistema LLM:

| Aspecto | Indicador | Valor del período | Tendencia |
|---|---|---|---|
| Incidentes de sesgo reportados | Número de reportes de usuarios sobre respuestas sesgadas | N | ↑↓→ |
| Incidentes de output dañino | Número de incidentes con output bloqueado por guardrails | N | ↑↓→ |
| Ejercicios de DSAR atendidos | Solicitudes de acceso, rectificación o supresión de datos | N | — |
| Porcentaje de solicitudes con guardrail activado | % de solicitudes donde se activó al menos un guardrail | X% | — |
| Resultado del red-teaming periódico | Vulnerabilidades detectadas / mitigadas | N/N | — |

---

## 9. Actividades prácticas

### Actividad 1 — Medición del consumo energético de un servidor de inferencia

**Descripción**: Instrumenta un servidor de inferencia vLLM con CodeCarbon y con monitorización de potencia mediante `nvidia-smi dmon`. Ejecuta tres cargas de trabajo distintas: (a) 100 solicitudes cortas con prompts de 100 tokens y respuestas de 50 tokens; (b) 100 solicitudes medias con prompts de 500 tokens y respuestas de 200 tokens; (c) 10 solicitudes largas con prompts de 2000 tokens y respuestas de 1000 tokens. Para cada carga, registra el consumo energético total, el consumo por solicitud y el consumo por token generado. Calcula las emisiones de CO₂eq asumiendo el mix eléctrico español.

**Entregable**: Tabla comparativa de consumo y emisiones para las tres cargas de trabajo, gráfica de potencia GPU durante cada carga y análisis de las diferencias observadas.

**Criterios de evaluación**: Correcta instrumentación con CodeCarbon y nvidia-smi, metodología de medición reproducible, análisis riguroso de los resultados y correcta conversión a emisiones de CO₂eq.

---

### Actividad 2 — Comparativa de impacto ambiental de estrategias de cuantización

**Descripción**: Despliega el mismo modelo base en tres configuraciones: FP16 (precisión completa), AWQ INT4, y GGUF Q4_K_M. Para cada configuración, mide el consumo energético por millón de tokens usando la metodología de la actividad anterior. Evalúa también la calidad de los outputs con un conjunto de 20 preguntas de evaluación predefinidas, puntuando cada respuesta de 1 a 5 en calidad percibida. Elabora un análisis coste-beneficio de cada configuración en términos de sostenibilidad, rendimiento y calidad.

**Entregable**: Tabla comparativa con consumo, emisiones, throughput y puntuación de calidad para cada configuración, y análisis coste-beneficio con recomendación razonada.

**Criterios de evaluación**: Metodología de medición correcta, evaluación de calidad justificada, análisis coste-beneficio riguroso y recomendación bien fundamentada.

---

### Actividad 3 — Evaluación de sesgos y responsabilidad ética

**Descripción**: Diseña una suite de evaluación de sesgos para el modelo desplegado con al menos 20 pares de solicitudes contrastadas (misma solicitud pero refiriéndose a grupos demográficos distintos: géneros, nacionalidades, edades). Ejecuta las evaluaciones y analiza sistemáticamente si el modelo trata de forma diferencial a los grupos comparados. Identifica al menos tres casos de sesgo detectado y propón medidas técnicas u organizativas para mitigar cada uno. Redacta el registro de impacto social del mes de operación hipotético del servicio.

**Entregable**: Suite de evaluación con resultados, análisis de sesgos detectados con evidencias, propuestas de mitigación y registro de impacto social cumplimentado.

**Criterios de evaluación**: Rigor en el diseño de la suite de evaluación, análisis objetivo de los resultados, propuestas de mitigación realistas y adecuadas, completitud del registro de impacto social.

---

### Actividad 4 — Plan de prevención de riesgos laborales para un equipo de operación LLM

**Descripción**: Para un equipo hipotético de 4 técnicos de operación de una infraestructura LLM de alta disponibilidad (SLA del 99.9%, guardia localizada 24/7 rotativa), elabora un plan de prevención de riesgos laborales que incluya: (a) evaluación de riesgos ergonómicos del puesto de trabajo con la lista de verificación del RD 488/1997; (b) evaluación de riesgos psicosociales identificados; (c) medidas preventivas propuestas para cada riesgo identificado; (d) propuesta de política de guardia sostenible con asignación de turnos y compensación; (e) protocolo de gestión del estrés en incidentes de producción.

**Entregable**: Plan de prevención de riesgos laborales completo (5-7 páginas) con todos los apartados indicados.

**Criterios de evaluación**: Correcta aplicación del marco normativo (Ley 31/1995, RD 488/1997), identificación exhaustiva de riesgos, medidas preventivas realistas y específicas del contexto de operación LLM, viabilidad de la política de guardia propuesta.

---

## 10. Referencias

- **EU AI Act — Capítulo V: Modelos de IA de uso general (arts. 51-55)**: obligaciones de transparencia, red-teaming y reporte de eficiencia energética. Disponible en: [https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689)

- **CodeCarbon — Documentación oficial**: estimación de emisiones de CO₂ en código Python y guía de integración. Disponible en: [https://mlco2.github.io/codecarbon/](https://mlco2.github.io/codecarbon/)

- **Zeus — Energy Measurement for DL Training (CMU/Michigan)**: documentación de zeus-monitor para medición de energía GPU. Disponible en: [https://ml.energy/zeus/](https://ml.energy/zeus/)

- **Patterson et al. — Carbon and the Climate Crisis of Large Language Models (2021)**: estimaciones de consumo energético de modelos fundacionales. Disponible en: [https://arxiv.org/abs/2104.10350](https://arxiv.org/abs/2104.10350)

- **Lottick et al. — Energy Usage Reports for Neural Network Training (2019)**: metodología para el reporte de consumo energético en entrenamiento de redes neuronales. Disponible en: [https://arxiv.org/abs/1910.09700](https://arxiv.org/abs/1910.09700)

- **INSST — Factores psicosociales: metodología de evaluación**: guía del Instituto Nacional de Seguridad y Salud en el Trabajo para la evaluación de riesgos psicosociales. Disponible en: [https://www.insst.es/el-instituto-al-dia/noticias/2015/factores-y-riesgos-psicosociales-formas-consecuencias-medidas-y-buenas-practicas](https://www.insst.es/el-instituto-al-dia/noticias/2015/factores-y-riesgos-psicosociales-formas-consecuencias-medidas-y-buenas-practicas)

- **Real Decreto 488/1997 — Pantallas de visualización de datos**: texto completo de la normativa de PRL para puestos con pantallas. Disponible en: [https://www.boe.es/eli/es/rd/1997/04/14/488](https://www.boe.es/eli/es/rd/1997/04/14/488)

- **Ley 31/1995 de Prevención de Riesgos Laborales**: texto consolidado de la Ley de PRL. Disponible en: [https://www.boe.es/eli/es/l/1995/11/08/31/con](https://www.boe.es/eli/es/l/1995/11/08/31/con)

- **Electricity Maps — Datos de intensidad de carbono de la electricidad en tiempo real**: mapa mundial de intensidad de carbono del mix eléctrico por región. Disponible en: [https://app.electricitymaps.com/map](https://app.electricitymaps.com/map)

- **Meta AI — LLaMA 3.1 Model Card (sección de impacto ambiental)**: información publicada sobre el consumo energético del entrenamiento de LLaMA 3.1. Disponible en: [https://huggingface.co/meta-llama/Meta-Llama-3.1-70B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3.1-70B-Instruct)

- **NVIDIA — nvidia-smi Reference Guide**: documentación completa de nvidia-smi, incluyendo monitorización de potencia y TDP capping. Disponible en: [https://developer.nvidia.com/nvidia-system-management-interface](https://developer.nvidia.com/nvidia-system-management-interface)

- **Goldfarb et al. — Power Hungry Processing: Watts Driving the Cost of AI Deployment? (2023)**: análisis del consumo energético de la inferencia de LLMs. Disponible en: [https://arxiv.org/abs/2311.05610](https://arxiv.org/abs/2311.05610)

---

*UD7 · MP04 Infraestructura para la ejecución de LLMs · CFS2 Instalación, despliegue y explotación de sistemas de IA*
