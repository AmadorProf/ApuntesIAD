---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD8 · Responsabilidad, sostenibilidad, PRL y residuos | MP02 · Despliegue de sistemas de IA'
footer: 'CFS Instalación, despliegue y explotación de sistemas de IA (IAD)'
---

<!-- _class: lead -->
# UD8 · Responsabilidad profesional, sostenibilidad, PRL y gestión de residuos
## MP02 · Despliegue de sistemas de IA

<style>
section { font-family: 'Segoe UI', Arial, sans-serif; }
h1 { color: #1e3a5f; }
h2 { color: #1e3a5f; border-bottom: 2px solid #10b981; padding-bottom: 6px; }
h3 { color: #059669; }
table { font-size: 0.82em; width: 100%; }
ul, ol { font-size: 0.88em; }
blockquote { border-left: 4px solid #10b981; background: #ecfdf5; padding: 8px 16px; border-radius: 4px; }
footer, header { font-size: 0.6em; color: #6b7280; }
section.lead h1 { font-size: 2em; text-align: center; margin-top: 80px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
pre { background: #1e293b; color: #e2e8f0; padding: 16px; border-radius: 8px; font-size: 0.8em; }
</style>

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Actuar con responsabilidad en la toma de decisiones técnicas del despliegue
- Comunicar instrucciones de funcionamiento de forma clara y adaptada al perfil receptor
- Integrar criterios de sostenibilidad (DNSH, ODS) en las decisiones de despliegue
- Gestionar residuos electrónicos (RAEE) conforme a la normativa vigente
- Aplicar equipos de protección individual y medidas ergonómicas en el puesto de trabajo
- Actuar de forma ordenada ante emergencias según el Plan establecido

---

## Responsabilidad profesional en el despliegue

Desplegar un sistema de IA implica tomar decisiones con impacto real:

### Dimensiones de la responsabilidad

| Dimensión | Qué implica |
|-----------|-------------|
| Técnica | Verificar antes de activar en producción |
| Ética | Respetar la privacidad y los derechos de los usuarios |
| Organizacional | Coordinar con los equipos implicados |
| Legal | Cumplir el Reglamento IA UE 2024/1689 y el RGPD |

> Un despliegue deficiente puede causar daño real. La responsabilidad profesional exige verificar, documentar y comunicar.

---

## Comunicación eficaz entre roles

En un despliegue participan perfiles muy distintos. La comunicación deficiente genera errores.

### Principios de comunicación técnica eficaz

- Adaptar el nivel de detalle al interlocutor (técnico vs. operativo vs. directivo)
- Usar terminología precisa sin jerga innecesaria
- Documentar los cambios en el momento en que ocurren, no después
- Confirmar la comprensión de instrucciones críticas antes de ejecutarlas
- Escalar de forma inmediata cuando se detecta un problema fuera del alcance propio

### Herramientas de coordinación
- Registro de incidencias (Jira, ServiceNow, GitLab Issues)
- Canales de comunicación diferenciados (urgente vs. informativo)
- Plantillas de handover para cambios de turno

---

## Transmisión de instrucciones de funcionamiento

Tras el despliegue, el sistema debe ser operado por personas que no lo desarrollaron.

### Buenas prácticas

- Redactar manuales operativos con capturas, ejemplos y casos de error frecuentes
- Establecer procedimientos paso a paso para las operaciones habituales (arranque, parada, escalado)
- Incluir instrucciones de escalado cuando el operador no puede resolver la incidencia
- Validar la comprensión del manual con una sesión práctica antes de la entrega

### Ejemplo de estructura de manual operativo

```
1. Requisitos previos (accesos, VPN, credenciales)
2. Arranque normal del servicio
3. Verificación de estado (health check)
4. Procedimiento de parada programada
5. Actuación ante alertas comunes
6. Contactos de escalado
```

---

## Trabajo colaborativo en entornos técnicos

### Roles habituales en un despliegue

| Rol | Responsabilidad principal |
|-----|--------------------------|
| MLOps / DevOps | Infraestructura, CI/CD, automatización |
| Científico de datos | Validación del modelo desplegado |
| Responsable de seguridad | Revisión de accesos y cumplimiento |
| Operador | Monitorización y respuesta a incidencias |
| Responsable de proyecto | Coordinación, plazos, comunicación |

### Valores de un entorno colaborativo saludable
- Respeto a la diversidad de perfiles y enfoques
- Retroalimentación constructiva y no personalizada
- Asunción compartida de responsabilidades (no culpabilización)

---

## Sostenibilidad en el despliegue de IA

Los sistemas de IA consumen recursos significativos. El despliegue responsable minimiza ese impacto.

### Principio DNSH (Do No Significant Harm)

El reglamento europeo exige que las inversiones tecnológicas no causen daño significativo a ninguno de los seis objetivos medioambientales:

1. Mitigación del cambio climático
2. Adaptación al cambio climático
3. Uso sostenible del agua
4. Economía circular
5. Prevención de la contaminación
6. Biodiversidad y ecosistemas

> El despliegue de sistemas de IA debe justificarse y optimizarse en términos de huella ambiental.

---

## ODS aplicables al despliegue de IA

| ODS | Relevancia en el despliegue |
|-----|-----------------------------|
| ODS 9 — Industria e innovación | Infraestructuras sostenibles y eficientes |
| ODS 12 — Producción responsable | Reutilización de equipos, reducción de residuos |
| ODS 13 — Acción por el clima | Minimización de emisiones de CO₂ del CPD |

### Medidas concretas de sostenibilidad en el despliegue

- Dimensionar la infraestructura según la demanda real (evitar sobredimensionamiento)
- Activar autoescalado para liberar recursos en horas de baja carga
- Reutilizar equipos existentes antes de adquirir hardware nuevo
- Preferir centros de datos con certificación de eficiencia energética (PUE < 1,4)

---

## Reducción de la huella de carbono digital

### Indicadores de eficiencia energética del CPD

| Métrica | Descripción | Objetivo |
|---------|-------------|---------|
| PUE | Power Usage Effectiveness = Total / IT | < 1,4 |
| WUE | Water Usage Effectiveness (litros/kWh) | < 1,0 |
| CUE | Carbon Usage Effectiveness (kg CO₂/kWh) | Mínimo posible |

### Estrategias de reducción

- Apagado automático de entornos de prueba fuera de horario laboral
- Uso de regiones de nube alimentadas con energía renovable
- Optimización de modelos para reducir cómputo de inferencia (cuantización, destilación)
- Monitorización del consumo energético con herramientas como CodeCarbon o cloud cost explorer

---

## Economía circular de activos tecnológicos

### Ciclo de vida responsable del hardware de despliegue

```
Adquisición → Configuración → Operación → Mantenimiento → Fin de vida
     ↑                                                          |
     |_______________ Reutilización / Reacondicionamiento _____↓
```

### Actuaciones en cada fase

- **Adquisición:** preferir equipos certificados con etiqueta energética, evitar sobrecompra
- **Operación:** maximizar la tasa de utilización (objetivo > 70%)
- **Mantenimiento:** ampliar la vida útil mediante actualizaciones de firmware y limpieza
- **Fin de vida:** entregar a gestores RAEE autorizados, no eliminar por vías no controladas

---

## Gestión de residuos RAEE

Los equipos de infraestructura de IA son residuos de aparatos eléctricos y electrónicos (RAEE).

### Normativa aplicable en España

- **Directiva 2012/19/UE** — Marco europeo de gestión de RAEE
- **Real Decreto 110/2015** — Transposición española
- **Ley 7/2022 de residuos** — Economía circular y jerarquía de residuos

### Jerarquía de gestión (orden de preferencia)

1. Reducción en origen (no generar el residuo)
2. Reutilización (ceder o revender el equipo funcional)
3. Reciclaje (recuperar materias primas)
4. Valorización energética
5. Eliminación controlada (último recurso)

---

## Procedimiento de retirada de equipos

Antes de retirar cualquier equipo que haya procesado datos:

### Paso 1 — Borrado seguro de datos

```bash
# Sobrescritura segura de disco (estándar DoD 5220.22-M)
shred -vfz -n 3 /dev/sda

# Para SSD (ATA Secure Erase)
hdparm --security-erase-enhanced NULL /dev/sda

# Para NVMe
nvme format /dev/nvme0 --ses=2
```

### Paso 2 — Documentación de la baja
- Registro en el inventario con fecha, motivo y destino
- Certificado de destrucción o transferencia al gestor RAEE autorizado
- Baja de la licencia de software asociada

---

## Separación y almacenamiento de RAEE

### Tipos de residuos en infraestructura de IA

| Tipo | Ejemplos | Punto limpio/Gestor |
|------|----------|---------------------|
| Grandes electrodomésticos IT | Servidores, UPS, racks | Gestor RAEE autorizado |
| Pequeños equipos | Switches, routers, tarjetas | Punto limpio municipal o gestor |
| Baterías y acumuladores | Baterías de SAI, UPS | Punto de recogida específico |
| Pantallas y monitores | Displays, KVM | Gestor RAEE (contienen mercurio) |

> Nunca depositar RAEE en contenedores de residuo general. Es una infracción sancionable.

---

## Prevención de riesgos laborales (PRL) en el despliegue

### Riesgos principales en sala de servidores y CPD

| Riesgo | Ejemplo | Medida preventiva |
|--------|---------|-------------------|
| Eléctrico | Contacto con cableado sin tensión verificada | Bloqueo/etiquetado (LOTO) |
| Físico | Caída de equipos pesados al retirarlos del rack | Uso de elevador de rack, trabajo en pareja |
| Ergonómico | Posturas forzadas al cablear en espacio reducido | Planificar antes de iniciar, usar extensiones |
| Ambiental | Ruido excesivo en CPD, temperatura extrema | EPI adecuados, límite de exposición |
| Descarga electrostática | Daño a componentes o shock al manipular PCB | Muñequera antiestática, alfombrilla ESD |

---

## Equipos de protección individual (EPI)

### EPI específicos para trabajos en CPD e infraestructura

| EPI | Norma de referencia | Cuándo usarlo |
|-----|--------------------|-|
| Calzado de seguridad (punta acero) | EN ISO 20345:2022 | Manipulación de servidores en rack |
| Guantes antiestáticos | EN 61340-5-1 | Manipulación de tarjetas, módulos de memoria |
| Gafas de protección | EN 166:2002 | Limpieza con aire comprimido, soldadura |
| Protección auditiva | EN 352-1 | Estancias prolongadas en CPD (> 85 dB) |
| Ropa antiestática | EN 1149-5 | Entornos con alto riesgo ESD |

> Verificar que los EPI tienen el marcado CE y están en fecha de caducidad.

---

## Ergonomía en el puesto de trabajo

### Factores de riesgo ergonómico en despliegues

- Trabajo prolongado en posición estática frente a pantalla (configuración remota)
- Manipulación manual de cargas (servidores de hasta 30 kg)
- Trabajo en espacios confinados con posturas forzadas (cableado bajo suelo técnico)
- Fatiga visual por monitorización de múltiples pantallas

### Medidas correctoras

| Situación | Medida |
|-----------|--------|
| Pantallas > 4h | Regla 20-20-20: cada 20 min, mirar a 20 pies durante 20 s |
| Carga manual > 25 kg | Uso obligatorio de elevador o trabajo en equipo |
| Trabajo en altura | Escalera homologada, nunca improvised support |
| Postura sedente prolongada | Silla regulable, reposapiés, soporte lumbar |

---

## Riesgos psicosociales y tecnoestrés

El trabajo en despliegues de producción conlleva presión elevada.

### Factores de riesgo psicosocial más frecuentes

- Guardias y trabajo en horario nocturno o festivo
- Alta responsabilidad con poco margen de error
- Sobrecarga de alertas y notificaciones (alert fatigue)
- Falta de autonomía en la toma de decisiones
- Exposición continua a entornos de alta disponibilidad (24/7)

### Estrategias de mitigación

- Rotación de guardias equitativa y documentada
- Procedimientos claros que reduzcan la ambigüedad en situaciones de crisis
- Límites de horas de trabajo continuo antes de relevos obligatorios
- Espacios de descanso y desconexión digital fuera del horario de guardia

---

## Plan de emergencias en CPD

### Tipos de emergencia más frecuentes

| Tipo | Causa | Respuesta inicial |
|------|-------|-------------------|
| Incendio | Cortocircuito, sobrecalentamiento | Activar extintor CO₂, evacuar, avisar a bomberos |
| Inundación | Agua de climatización, rotura de tubería | Cortar suministro eléctrico, evacuación |
| Fallo eléctrico masivo | Caída de suministro, fallo de UPS | Activar generador, iniciar parada controlada |
| Intrusión física | Acceso no autorizado al CPD | Activar alarma, bloquear acceso, avisar a seguridad |

### Protocolo básico de evacuación
1. Activar alarma manual si no se ha activado automáticamente
2. Seguir la ruta de evacuación señalizada
3. No usar ascensores
4. Punto de reunión exterior predefinido
5. Confirmación de presencia por responsable de equipo

---

## Actuación ante emergencias: responsabilidades del técnico

El técnico de despliegue debe conocer y cumplir el Plan de emergencias del centro.

### Acciones específicas del técnico en caso de emergencia

- Conocer la ubicación de los extintores de CO₂ (para equipos eléctricos) y los pulsadores de alarma
- No intentar resolver la emergencia si supone riesgo personal — priorizar la evacuación
- Antes de evacuar: si es seguro y no demora la evacuación, activar la parada controlada del sistema crítico
- Al llegar al punto de reunión: confirmar la presencia al jefe de emergencia
- No reentrar al edificio hasta que el responsable de emergencias lo autorice

> La seguridad de las personas es siempre prioritaria sobre la disponibilidad del sistema.

---

## Actividad práctica

### Escenario: plan de baja de infraestructura con gestión responsable

**Situación:** Un servidor de inferencia de 3 años va a ser sustituido. Contiene datos de usuarios procesados durante el despliegue y aloja un modelo propietario.

**Tarea:**

1. Define el procedimiento de borrado seguro de los datos del servidor (datos de usuarios + pesos del modelo)
2. Identifica los RAEE que generará la baja (servidor, batería de SAI, cables)
3. Indica el gestor RAEE autorizado o punto limpio al que deberías acudir en tu municipio
4. Redacta un checklist de baja del equipo (inventario, licencias, documentación, certificado)
5. Señala qué EPI utilizarías durante el proceso de desmontaje físico del servidor del rack

---

## Puntos clave

- La responsabilidad profesional en el despliegue implica verificar, documentar y comunicar a tiempo
- Las instrucciones de funcionamiento deben ser comprensibles para perfiles operativos, no solo técnicos
- El principio DNSH y los ODS 9, 12 y 13 enmarcan las decisiones de infraestructura sostenible
- Los equipos retirados son RAEE y deben gestionarse por gestores autorizados, nunca como residuo general
- El borrado seguro de datos (shred, ATA Secure Erase) es obligatorio antes de retirar cualquier equipo
- Los EPI y el Plan de emergencias son de obligado conocimiento y cumplimiento para todo el equipo

---

## Criterios de evaluación

- **EC8:** Actúa con responsabilidad transmitiendo instrucciones de funcionamiento de forma sencilla y comprensible, integrando criterios de sostenibilidad en las decisiones de despliegue y aplicando el principio DNSH y los ODS aplicables
- **EC9:** Previene riesgos laborales utilizando los EPI adecuados, aplicando criterios ergonómicos, actuando conforme al Plan de emergencias y gestionando los residuos RAEE según la normativa vigente de economía circular

---

<!-- _class: lead -->
## Fin de la UD8

**MP02 · Despliegue de sistemas de IA**
CFS — Instalación, despliegue y explotación de sistemas de IA (IAD)

[← Volver al módulo](../)


---

<!-- nav-slide -->

## Navegación

[← UD7 · Gobernanza, trazabilidad y cu…](../UD7_Gobernanza-trazabilidad-normativa/) &nbsp;·&nbsp; [Volver al módulo](../)
