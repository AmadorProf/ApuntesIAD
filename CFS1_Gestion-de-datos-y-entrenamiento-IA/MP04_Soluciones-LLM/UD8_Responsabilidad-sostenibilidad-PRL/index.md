---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD8 · Responsabilidad profesional, sostenibilidad y PRL | MP04 · Soluciones basadas en LLMs'
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

# UD8 · Responsabilidad profesional, sostenibilidad y PRL

**MP04 · Soluciones basadas en LLMs**
CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno sera capaz de:

- Comunicar instrucciones, resultados y limitaciones tecnicas de forma adaptada a diferentes perfiles de interlocutor.
- Integrar criterios de sostenibilidad en las decisiones de diseno y configuracion de soluciones LLM.
- Identificar los riesgos psicosociales y ergonomicos asociados al trabajo con sistemas de IA y aplicar medidas preventivas.
- Aplicar el plan de emergencias del entorno de trabajo y los procedimientos de actuacion ante incidencias.

---

## 1 · Responsabilidad profesional y comunicacion (I)

### Rigor tecnico e integridad etica

La responsabilidad profesional en el desarrollo de soluciones LLM tiene dos dimensiones inseparables:

**Rigor tecnico:**
- Documentar correctamente las decisiones de diseno y sus fundamentos.
- No ocultar limitaciones conocidas del sistema a los clientes o usuarios.
- Validar las soluciones antes de presentarlas como aptas para produccion.
- Mantener el codigo, la configuracion y los modelos bajo control de versiones.

**Integridad etica:**
- No sobredimensionar las capacidades del sistema en presentaciones o propuestas.
- Informar cuando el sistema comete errores que pueden tener consecuencias reales.
- Reconocer los limites del propio conocimiento y buscar asesoramiento cuando es necesario.
- Respetar los datos de los usuarios y los acuerdos de confidencialidad.

> La reputacion profesional en IA se construye con honestidad sobre lo que el sistema puede y no puede hacer.

---

## 1 · Responsabilidad profesional y comunicacion (II)

### Comunicacion asertiva entre roles tecnicos y no tecnicos

El profesional de IA trabaja con interlocutores de perfiles muy distintos. Adaptar la comunicacion es una competencia tecnica, no solo una habilidad blanda:

| Perfil del interlocutor | Lo que necesita | Como adaptar la comunicacion |
|---|---|---|
| **Direccion / cliente** | Impacto de negocio, plazos, costes | Hablar de resultados, no de arquitecturas; usar metricas de negocio |
| **Equipo de TI / operaciones** | Integracion, seguridad, escalabilidad | Especificaciones tecnicas claras; diagramas de arquitectura |
| **Usuario final** | Que puede hacer el sistema, como usarlo, que no puede hacer | Lenguaje sencillo; ejemplos; aviso claro de limitaciones |
| **Equipo juridico / compliance** | Normativa, riesgos legales, datos personales | Precisar terminos; citar normativa; no usar jerga tecnica |
| **Otros tecnicos** | Decisiones de diseno, benchmarks, codigo | Nivel tecnico completo; compartir el razonamiento detras de cada decision |

---

## 1 · Responsabilidad profesional y comunicacion (III)

### Transmision de limitaciones: como decirlo bien

Una de las situaciones mas delicadas en la comunicacion profesional es transmitir que el sistema tiene limitaciones o que ha cometido un error. Algunos principios:

**Lo que no funciona:**
- Minimizar el problema ("es solo un error puntual")
- Tecnicizar en exceso para que no se entienda ("el modelo alucino debido a la distribucion de probabilidad del decodificador")
- Culpar al modelo como si fuera un actor externo ("el modelo lo hizo mal; nosotros lo configuramos bien")

**Lo que funciona:**
- Describir el problema de forma neutra y factual
- Explicar la causa raiz en terminos comprensibles
- Presentar la solucion o el plan de accion en el mismo mensaje
- Comprometerse con plazos realistas y cumplirlos

```
EJEMPLO DE COMUNICACION EFECTIVA DE UN FALLO

"El sistema genero una respuesta incorrecta en un 8 % de los casos de prueba
cuando la pregunta contenia cifras economicas. La causa es que el modelo no
tiene acceso a los datos actualizados de presupuesto. Proponemos conectar el
sistema a la fuente de datos correcta antes del lunes. Mientras tanto,
incluiremos un aviso en la interfaz para que los usuarios contrasten estas
cifras con la documentacion oficial."
```

---

## 2 · Sostenibilidad en soluciones LLM (I)

### El impacto ambiental de los LLMs

Los modelos de lenguaje tienen un coste energetico y de emisiones significativo en dos fases:

**Fase de entrenamiento:**
- Entrenar un modelo grande consume entre 1.000 y 10.000 MWh de electricidad.
- Las emisiones asociadas dependen de la matriz energetica del centro de datos.
- El desarrollador no suele controlar esta fase, pero puede optar por proveedores con compromisos de neutralidad de carbono.

**Fase de inferencia (la que controla el desarrollador):**
- Cada llamada a la API consume energia en el servidor del proveedor.
- El consumo depende del tamano del modelo, la longitud del contexto y el numero de tokens generados.
- En soluciones de alto volumen, las decisiones de diseno tienen un impacto medible.

> El principio DNSH (Do No Significant Harm) del marco europeo de finanzas sostenibles exige que las actividades financiadas no causen dano ambiental significativo. Se aplica cada vez mas como criterio de evaluacion en contratos publicos de TI.

---

## 2 · Sostenibilidad en soluciones LLM (II)

### Decisiones de diseno que reducen el impacto

El profesional de IA tiene margen de actuacion real en la fase de inferencia:

| Decision de diseno | Impacto en sostenibilidad | Como aplicarla |
|---|---|---|
| **Seleccion del modelo** | Usar el modelo mas pequeno que resuelve el caso de uso reduce el consumo | Benchmark con modelos de distintos tamanos antes de decidir |
| **Longitud del contexto** | Contextos mas cortos consumen menos tokens y menos energia | Chunking preciso; no enviar documentos completos si no es necesario |
| **Caching de respuestas** | Reutilizar respuestas identicas elimina llamadas redundantes | Implementar capa de cache para consultas frecuentes |
| **Batching de peticiones** | Agrupar peticiones reduce el overhead por llamada | Usar procesamiento batch para tareas no interactivas |
| **Frecuencia de llamadas** | Reducir el numero de llamadas innecesarias | Validar entradas antes de enviar; evitar llamadas de prueba en produccion |

---

## 2 · Sostenibilidad en soluciones LLM (III)

### ODS aplicables y principio DNSH

Las soluciones LLM se relacionan con varios Objetivos de Desarrollo Sostenible de la ONU:

| ODS | Relacion con LLMs | Como integrarlo |
|---|---|---|
| **ODS 7** — Energia asequible y no contaminante | El consumo energetico de la inferencia | Optar por proveedores con energia renovable certificada |
| **ODS 9** — Industria, innovacion e infraestructura | La IA como palanca de innovacion sostenible | Priorizar casos de uso con impacto social positivo |
| **ODS 10** — Reduccion de desigualdades | Los sesgos en los modelos pueden ampliar desigualdades | Evaluar sesgo antes del despliegue; monitorizar en produccion |
| **ODS 12** — Produccion y consumo responsables | Uso eficiente de los recursos computacionales | Implementar las medidas de eficiencia del punto anterior |
| **ODS 13** — Accion por el clima | Emisiones de CO₂ del ciclo de vida del sistema | Medir y compensar las emisiones; elegir centros de datos con baja huella |

```python
# Estimacion simplificada de emisiones por llamada
def estimar_co2_llamada(tokens_entrada: int, tokens_salida: int,
                         g_co2_por_kwh: float = 250) -> float:
    """Estimacion orientativa; los valores reales dependen del proveedor."""
    kwh_estimado = (tokens_entrada * 0.0000003 + tokens_salida * 0.0000006)
    return kwh_estimado * g_co2_por_kwh  # gramos de CO2
```

---

## 3 · Prevencion de riesgos laborales (I)

### Riesgos psicosociales en el trabajo con IA

El trabajo intensivo con sistemas de IA generativa introduce riesgos psicosociales especificos que deben identificarse y gestionarse:

| Riesgo | Descripcion | Factores que lo agravan |
|---|---|---|
| **Tecnoestrés** | Ansiedad y agotamiento por la presion de adaptarse continuamente a nuevas herramientas | Ritmo de cambio acelerado; falta de formacion |
| **Sobrecarga cognitiva** | Fatiga mental por procesar y evaluar grandes volumenes de salidas del modelo | Revision de outputs sin pausas; multitarea constante |
| **Perdida de sentido del trabajo** | Sensation de que el trabajo propio es sustituible por el modelo | Falta de comunicacion organizacional; roles poco definidos |
| **Hiperconectividad** | Dificultad para desconectar cuando el sistema esta disponible 24/7 | Falta de limites horarios; notificaciones permanentes |
| **Responsabilidad difusa** | Incertidumbre sobre quien es responsable de los errores del sistema | Falta de protocolos claros de supervision y decision |

---

## 3 · Prevencion de riesgos laborales (II)

### Ergonomia cognitiva en el trabajo con LLMs

La ergonomia cognitiva estudia como el diseno de las herramientas y los procesos afecta a la carga mental del trabajador:

**Principios de ergonomia cognitiva aplicados a LLMs:**

- **Chunking de tareas:** revisar los outputs del modelo en sesiones cortas con pausas, no en bloques de horas.
- **Criterios de decision explicitos:** definir por escrito cuales son los criterios para aceptar o rechazar una respuesta del modelo. Reduce la fatiga de decision.
- **Rotacion de tareas:** alternar entre trabajo de revision de outputs y trabajo creativo propio para reducir la monotonia.
- **Documentacion del proceso:** registrar las decisiones tomadas reduce la carga de tener que recordarlas o reconstruirlas.
- **Limites de revision:** fijar un numero maximo de outputs a revisar en una sesion antes de hacer una pausa obligatoria.

---

## 3 · Prevencion de riesgos laborales (III)

### Ergonomia fisica y ambiental

El trabajo con LLMs es principalmente trabajo de pantalla. Los riesgos ergonomicos clasicos se aplican y se agravan por la concentracion que requiere la revision de outputs:

**Ergonomia fisica:**
- Monitor a la altura de los ojos; distancia de 50-70 cm.
- Silla con soporte lumbar regulable; pies apoyados en el suelo.
- Regla 20-20-20: cada 20 minutos, mirar a 20 pies (6 m) durante 20 segundos.
- Pausas activas cada 90 minutos de trabajo intensivo de pantalla.

**Ergonomia ambiental:**
- Iluminacion sin reflejos en la pantalla; temperatura entre 20-24 °C.
- Nivel de ruido inferior a 55 dB para trabajo cognitivo intensivo.
- Ventilacion adecuada; humedad relativa entre 40-60 %.

**Ergonomia de la herramienta:**
- Interfaces claras que no requieran memorizar comandos.
- Feedback visual del estado del sistema (procesando, error, listo).
- Posibilidad de interrumpir o cancelar una operacion en curso.

---

## 4 · Plan de emergencias y procedimientos de actuacion (I)

### Tipos de incidencia en sistemas LLM

Los sistemas LLM en produccion pueden sufrir distintos tipos de incidencia. Cada tipo requiere un protocolo de actuacion especifico:

| Tipo de incidencia | Ejemplo | Primer paso |
|---|---|---|
| **Fallo de disponibilidad** | La API del proveedor no responde | Activar el sistema de fallback; notificar a los usuarios |
| **Degradacion de calidad** | Las respuestas son claramente peores que el dia anterior | Verificar si hay un cambio de modelo del proveedor; comparar con version anterior |
| **Fuga de datos** | El sistema genera respuestas con datos de otro usuario | Parada de emergencia inmediata; notificar al DPO; iniciar investigacion |
| **Comportamiento inesperado** | El sistema ignora las instrucciones del system prompt | Parada de emergencia; verificar si el proveedor ha cambiado el comportamiento del modelo |
| **Abuso del sistema** | Se detecta un intento de prompt injection masivo | Bloquear la IP o el usuario; registrar el incidente; reforzar los filtros |
| **Exceso de coste** | El coste diario supera el umbral de alerta | Verificar si hay un uso anomalo; activar cuotas de emergencia |

---

## 4 · Plan de emergencias y procedimientos de actuacion (II)

### Protocolo de parada de emergencia

Toda solucion LLM en produccion debe tener un procedimiento documentado de parada de emergencia que cualquier miembro del equipo pueda ejecutar:

```
PROTOCOLO DE PARADA DE EMERGENCIA — Solucion LLM

CUANDO ACTIVARLO:
  - Fuga de datos confirmada o sospechada
  - Comportamiento dañino o ilegal del sistema
  - Fallo de seguridad que no se puede contener sin parar el servicio

PASOS:
  1. Desactivar el endpoint de la API (cambiar flag SISTEMA_ACTIVO=False)
  2. Notificar al responsable tecnico (telefono: X) y al DPO si hay datos personales
  3. Registrar la hora exacta, el tipo de incidencia y quien tomo la decision
  4. Redirigir a los usuarios al mensaje de mantenimiento
  5. No reactivar sin autorizacion del responsable tecnico y revision del incidente

QUIEN PUEDE ACTIVARLO: cualquier miembro del equipo tecnico
QUIEN PUEDE REACTIVARLO: solo el responsable tecnico tras revision

CONTACTOS DE EMERGENCIA:
  Responsable tecnico: [nombre y telefono]
  DPO: [nombre y email]
  Proveedor API (soporte urgente): [URL del panel de soporte]
```

---

## 4 · Plan de emergencias y procedimientos de actuacion (III)

### Ciclo de gestion de incidencias

Una vez resuelta la emergencia, el ciclo de gestion continua:

```
INCIDENCIA DETECTADA
      |
      v
Contener: parar o limitar el dano inmediato
      |
      v
Comunicar: notificar a los afectados y a la organizacion
      |
      v
Investigar: identificar la causa raiz (no el sintoma)
      |
      v
Resolver: aplicar la correccion tecnica
      |
      v
Verificar: confirmar que el problema esta resuelto
      |
      v
Documentar: registrar el incidente, la causa y la solucion
      |
      v
Aprender: actualizar procedimientos y controles para evitar la recurrencia
```

> Un incidente no gestionado correctamente es una oportunidad perdida de mejorar el sistema. La documentacion post-incidente es obligatoria.

---

## 5 · Comunicacion inclusiva y accesibilidad (I)

### Lenguaje inclusivo en la comunicacion tecnica

La comunicacion profesional en IA debe ser accesible para personas con diferentes niveles de familiaridad con la tecnologia y diferentes contextos culturales:

**Principios de comunicacion inclusiva:**
- Evitar acronimos sin explicar en la primera mencion (LLM = Large Language Model).
- No asumir conocimiento tecnico previo en documentos dirigidos a usuarios finales.
- Usar ejemplos que sean reconocibles para el publico objetivo.
- Evitar lenguaje que asuma un perfil demografico especifico del usuario.

**Accesibilidad en las interfaces de IA:**
- Asegurar que la interfaz funciona con lectores de pantalla.
- No depender solo del color para transmitir informacion (considerar daltonismo).
- Proporcionar alternativas de texto para contenido visual.
- Mantener un nivel de lectura accesible para el publico general (no solo expertos).

---

## 5 · Comunicacion inclusiva y accesibilidad (II)

### Adaptacion del mensaje segun el perfil destinatario

La misma informacion tecnica puede y debe formularse de manera diferente segun quien la recibe:

```
INFORMACION TECNICA:
"El sistema tiene una tasa de pertinencia del 87 % con temperatura 0.3
y un contexto de 4.000 tokens. Las alucinaciones se producen en un 3 %
de los casos cuando la pregunta no tiene respuesta en el corpus."

PARA LA DIRECCION:
"El sistema responde correctamente en 9 de cada 10 consultas.
En un 3 % de los casos puede dar informacion incorrecta cuando la
pregunta es sobre algo que no esta en la documentacion disponible.
Recomendamos incluir un aviso para que los usuarios verifiquen
la informacion critica."

PARA EL USUARIO FINAL:
"Este asistente esta entrenado con la documentacion interna de la empresa.
Si te hace falta informacion que no aparece en esos documentos, puede
que no te de una respuesta correcta. Contrasta siempre las cifras y
los datos importantes con las fuentes originales."
```

---

## Actividad practica · UD8

### Comunicacion multidestino y plan de sostenibilidad

**Enunciado:**

Has desplegado un asistente LLM para un departamento de atencion al ciudadano de un ayuntamiento. El sistema procesa 5.000 consultas diarias y usa un modelo grande de un proveedor en la nube. Detectas que la tasa de respuestas incorrectas ha subido del 4 % al 9 % tras una actualizacion del proveedor, y que el coste mensual se ha incrementado un 30 %.

**Tareas:**

1. Redactar tres comunicaciones sobre el mismo problema: una para el alcalde (sin tecnicismos), una para el equipo de TI del ayuntamiento (nivel tecnico completo) y una para los ciudadanos usuarios del sistema (accesible y tranquilizadora).
2. Identificar tres medidas de diseno que reduciran el consumo energetico sin degradar la calidad del servicio.
3. Completar la tabla de riesgos psicosociales para el equipo tecnico que mantiene el sistema (minimo cuatro riesgos con medida preventiva).
4. Redactar el protocolo de parada de emergencia adaptado a este caso de uso.

**Entregable:** tres comunicaciones + tabla de medidas de sostenibilidad + tabla de riesgos + protocolo.

---

## Puntos clave · UD8

- La responsabilidad profesional en IA incluye rigor tecnico (documentar, validar, versionar) e integridad etica (no sobredimensionar, informar de fallos, respetar datos).
- La comunicacion debe adaptarse al perfil del interlocutor: la misma informacion tecnica requiere lenguajes distintos para la direccion, el equipo tecnico y el usuario final.
- Los LLMs tienen un impacto energetico medible en la fase de inferencia; las decisiones de diseno (tamano del modelo, longitud del contexto, caching) reducen el consumo.
- El principio DNSH y los ODS 7, 9, 10, 12 y 13 son marcos de referencia aplicables a las decisiones de sostenibilidad en soluciones LLM.
- Los riesgos psicosociales especificos del trabajo con IA incluyen tecnoestrés, sobrecarga cognitiva, perdida de sentido y responsabilidad difusa.
- La ergonomia cognitiva, fisica y ambiental son parte de la prevencion de riesgos en el puesto de trabajo tecnico.
- Todo sistema LLM en produccion debe tener un protocolo de parada de emergencia documentado y conocido por todo el equipo.

---

## Criterios de evaluacion · UD8

| Criterio | Indicadores de logro |
|---|---|
| **Comunica de forma adaptada al perfil destinatario** | Produce textos distintos sobre el mismo contenido tecnico segun el nivel del interlocutor; usa lenguaje inclusivo y accesible |
| **Integra sostenibilidad en las decisiones tecnicas** | Identifica al menos tres medidas concretas de diseno que reducen el consumo; las relaciona con ODS o el principio DNSH |
| **Aplica medidas de prevencion** | Identifica riesgos psicosociales y ergonomicos especificos del puesto; propone medidas preventivas concretas; elabora o aplica el protocolo de emergencia |

---

<!-- _class: lead -->

[← Volver a MP04](../index.md)
