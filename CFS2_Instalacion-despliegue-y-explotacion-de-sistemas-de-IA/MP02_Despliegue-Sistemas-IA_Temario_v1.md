# MP02 · Despliegue de sistemas de IA

*Módulo profesional del CFS «Instalación, despliegue y explotación de sistemas de IA (IAD)»*

| Campo | Valor |
|---|---|
| Código | MP02 |
| Estándar de competencia asociado | ECP2495_3 (Nivel 3) |
| Familia profesional | Inteligencia Artificial y Data |
| Duración orientativa | 200 h |
| Curso | 1.º |

**Competencia que desarrolla:** configurar la infraestructura de sistemas de IA aplicando el plan de aprovisionamiento, instalación y configuración, integrándola en el flujo productivo e implementando medidas que garantizan la calidad del servicio y su trazabilidad.

Las unidades didácticas (UD) concretan los resultados de aprendizaje del módulo. *Duración y curso son orientativos (propuesta).*

---

## UD1. Preparación del despliegue

**Resultados de aprendizaje.** Prepara el despliegue de la infraestructura interpretando las especificaciones para mantener la integridad y continuidad del servicio.

**Contenidos.**

- Determinación de componentes de equipos, aplicaciones e infraestructura desde el sistema de gestión, la documentación técnica y el Plan de aprovisionamiento. Disponibilidad, versión, compatibilidad, licencias.
- Ensayos y comprobaciones para identificar fallos: factores del componente y factores del entorno de pruebas.
- Configuración de monitorización y alarmas: picos de carga, desconexión de elementos. Protocolos de actuación y comunicación.
- Trazabilidad y reproducibilidad: repositorios de modelos y de características, versionado de datos, código y parámetros, sistemas de trazado.

**Criterios de evaluación.** Determina y verifica los componentes necesarios; configura monitorización y alarmas; asegura la trazabilidad de cada versión desplegada.

---

## UD2. Despliegue de la infraestructura

**Resultados de aprendizaje.** Despliega sistemas de IA en desarrollo o producción, en infraestructura como servicio o instalaciones propias.

**Contenidos.**

- Infraestructura propia: montaje y aprovisionamiento, SO, *bootloader*, *firmware*, imágenes, controladores, entornos de ejecución y dependencias.
- Infraestructura como servicio: servidores, imágenes y almacenamiento. Autoescalado, IP y puertos, persistencia, copias de seguridad, restricciones de acceso. Ensayos de rendimiento.
- Documentación de intervenciones: fecha, equipo, resumen, versiones de imágenes y configuraciones. Adjuntar *logs*.

**Criterios de evaluación.** Monta y configura infraestructura propia o contratada; verifica funcionamiento y rendimiento; documenta las intervenciones.

---

## UD3. Instalación de aplicaciones de despliegue

**Resultados de aprendizaje.** Instala y configura las aplicaciones del Plan de aprovisionamiento para desplegar sistemas de IA.

**Contenidos.**

- Aplicaciones de gestión: orquestadores de contenedores o microservicios, sistemas de monitorización y alarma, balanceadores de carga, repositorios de artefactos o modelos, gestión de secretos.
- Configuración de aplicaciones y relaciones: claves de acceso por API, volúmenes compartidos, permisos, reglas, políticas, usuarios y grupos.
- Verificación de funcionamiento y rendimiento. Compatibilidad entre versiones de modelo, entorno y dependencias.
- Documentación e inventario actualizado. *Logs* de instalación y ensayo.

**Criterios de evaluación.** Instala las aplicaciones según el Plan; configura permisos y relaciones; verifica compatibilidad y documenta.

---

## UD4. Integración en el flujo productivo

**Resultados de aprendizaje.** Integra sistemas de IA en el flujo productivo aplicando el Plan de integración.

**Contenidos.**

- Habilitación de entradas: APIs de la organización, suscripciones a *streams* de intermediación de mensajes, integraciones SCADA, conexiones con embebidos, robótica o IoT.
- Habilitación de salidas: inyección de datos procesados en el flujo con el formato y latencia indicados.
- Verificación de integraciones. Metadatos de trazabilidad: marcas temporales, identificadores de versión, indicadores de confianza.
- Documentación de intervenciones y *logs*.

**Criterios de evaluación.** Configura entradas y salidas según el escenario (API, *streaming*, M2M/IoT); verifica rendimiento; incorpora metadatos de trazabilidad.

---

## UD5. Puesta en servicio

**Resultados de aprendizaje.** Pone en servicio sistemas de IA aplicando el Plan de despliegue.

**Contenidos.**

- Instalación según escenario: aplicación o contenedor, grabación de *firmware* en embebidos, transmisión *Over The Air*.
- Estrategias de despliegue: CI/CD, recreación y reemplazo completo, *shadow deployment*, despliegue incremental (Blue/Green, A/B, Canary).
- Verificación: ensayos de rendimiento, carga, diferenciales, detección de anomalías.
- Conexión a entradas y salidas del flujo. Documentación y *logs*.

**Criterios de evaluación.** Selecciona la estrategia de despliegue adecuada; verifica el funcionamiento; conecta y documenta la puesta en servicio.

---

## UD6. Monitorización y mantenimiento

**Resultados de aprendizaje.** Implanta el Plan de monitorización y mantenimiento para garantizar calidad y disponibilidad.

**Contenidos.**

- Verificación de notificación de alarmas, monitorización, supervisión y respaldo.
- Análisis de registros: rendimiento, calidad de predicciones, *drift* de distribución, integridad de datos. Pruebas estadísticas (índice de estabilidad de población, Kolmogorov-Smirnov, Jensen-Shannon).
- Operaciones de corrección manuales o supervisadas: escalado de recursos, vuelta a versión previa, parches, redirección de flujos, modos de operación reducida.
- Documentación de intervenciones: causa, impacto, acción correctiva. *Logs*.

**Criterios de evaluación.** Detecta anomalías y *drift* con pruebas estadísticas; aplica correcciones; documenta las intervenciones.

---

## UD7. Gobernanza, trazabilidad y cumplimiento normativo

**Resultados de aprendizaje.** Implementa el Plan de gobernanza, trazabilidad y cumplimiento normativo del sistema de IA.

**Contenidos.**

- Clasificación del sistema por nivel de riesgo según normativa internacional aplicable.
- Registro automático de eventos (*logging*): versión del modelo, entradas, salidas, decisiones, intervenciones humanas.
- Supervisión humana: validación previa, intervención o anulación en ejecución, parada segura.
- Documentación de transparencia: propósito, datos de entrenamiento y evaluación, métricas, instrucciones de uso.
- Gobernanza de datos: representatividad, trazabilidad del origen, derechos de la titularidad (acceso, rectificación, supresión, oposición, limitación).
- Conservación de evidencias.

**Criterios de evaluación.** Clasifica el sistema por riesgo; configura *logging* y supervisión humana; verifica la gobernanza de datos y la conservación de evidencias.

---

## UD8. Responsabilidad, sostenibilidad, PRL y residuos

**Resultados de aprendizaje.** Actúa con responsabilidad y sostenibilidad, previniendo riesgos laborales y gestionando residuos (EC8 y EC9).

**Contenidos.**

- Responsabilidad en la toma de decisiones, comunicación efectiva, trabajo colaborativo.
- Transmisión sencilla de instrucciones de funcionamiento.
- Sostenibilidad: reutilización, prolongación de la vida útil, reducción de sobredimensionamiento y consumo. DNSH y ODS.
- PRL: EPI, ergonomía, Plan de emergencias. Gestión de residuos (RAEE) y economía circular.

**Criterios de evaluación.** Integra sostenibilidad en el despliegue; aplica EPI y ergonomía; gestiona residuos según normativa.

---

*Ocupaciones asociadas: técnicos de desarrollo de aplicaciones basadas en aprendizaje automático. Sector: desarrollo y explotación de sistemas de IA, área de infraestructura.*
