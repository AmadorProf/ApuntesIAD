# MP04 · Soluciones basadas en modelos de lenguaje (LLMs)

*Módulo profesional del CFS «Gestión de datos y entrenamiento IA (IAD)»*

| Campo | Valor |
|---|---|
| Código | MP04 |
| Estándar de competencia asociado | CPE_5054_3 (Nivel 3) |
| Familia profesional | Inteligencia Artificial y Data |
| Duración orientativa | 160 h |
| Curso | 2.º |

**Competencia que desarrolla:** gestionar soluciones basadas en modelos de lenguaje de gran tamaño (LLMs), desde la planificación y el despliegue hasta la supervisión de agentes autónomos y su integración con otros sistemas, asegurando funcionamiento, seguridad y trazabilidad.

Las unidades didácticas (UD) concretan los resultados de aprendizaje del módulo. *Duración y curso son orientativos (propuesta).*

---

## UD1. Análisis del caso de uso y selección del modelo

**Resultados de aprendizaje.** Analiza el caso de uso y selecciona el modelo, servicio o variante de LLM más adecuada.

**Contenidos.**

- Interpretación del caso de uso: objetivo funcional, usuarios, tipo de interacción, datos necesarios, restricciones, resultados esperados.
- Criterios de selección: modalidad (texto, audio, vídeo), capacidades lingüísticas, longitud de contexto, coste, latencia, disponibilidad, idioma, especialización, compatibilidad con herramientas.
- Parámetros de generación: temperatura, máximo de *tokens*, criterios de parada, penalizaciones, formato de salida, mensajes de sistema.
- Registro de limitaciones funcionales: capacidades, restricciones, servicios externos, supuestos, escenarios que requieren supervisión.

**Criterios de evaluación.** Interpreta el caso de uso; selecciona el modelo con criterios técnicos; configura los parámetros de generación.

---

## UD2. Componentes de interacción con el modelo

**Resultados de aprendizaje.** Implementa los componentes de interacción configurando instrucciones, contexto, entradas, salidas y lógica de aplicación.

**Contenidos.**

- Diseño de instrucciones y plantillas (*prompts*): mensajes de sistema, ejemplos, restricciones, tono, estructura de salida.
- Gestión del contexto: información por petición, tamaño de entrada, historial, priorización, resumen.
- Comunicación con el modelo vía APIs, SDKs, librerías, conectores y cachés. Gestión de peticiones, errores, tiempos de espera, reintentos y límites de uso.
- Gestión de salidas: formatos, esquemas, extracción de campos, validaciones, transformación.
- Configuración de asistentes conversacionales: flujos, historial, respuestas de aclaración, derivación.
- Registro de código y configuración: versiones de instrucciones, parámetros, conectores.

**Criterios de evaluación.** Define *prompts* y gestión de contexto; desarrolla la comunicación con el modelo controlando errores; gestiona y registra las salidas.

---

## UD3. Integración con fuentes, herramientas y sistemas (RAG)

**Resultados de aprendizaje.** Integra la solución con fuentes de información, bases de conocimiento, herramientas y sistemas externos.

**Contenidos.**

- Habilitación de fuentes: origen, formato, actualización, permisos, calidad.
- Recuperación de información: fragmentación de documentos, representaciones vectoriales, búsqueda semántica, búsqueda por palabras clave, filtrado (técnicas tipo RAG).
- Incorporación de información al contexto verificando pertinencia, vigencia y límites de entrada.
- Integración de herramientas, APIs y sistemas externos: conectores, credenciales, permisos, formatos de intercambio.
- Integración con canales: web, móvil, chats corporativos, redes sociales. Gestión de sesión y derivación.
- Validación de las integraciones.

**Criterios de evaluación.** Configura mecanismos de recuperación; integra herramientas y canales; valida la comunicación con los sistemas externos.

---

## UD4. Comportamientos agénticos

**Resultados de aprendizaje.** Configura comportamientos agénticos definiendo objetivos, herramientas, memoria, límites de autonomía y supervisión.

**Contenidos.**

- Objetivos y tareas del agente: alcance, pasos, condiciones de finalización, escalado.
- Herramientas y memoria operativa: alcance, validación, ciclo de vida (conservación y descarte), protección de datos.
- Límites de autonomía: acciones permitidas y prohibidas, umbrales de confianza, confirmación humana, parada y reversión.
- Validación del comportamiento agéntico ante instrucciones contradictorias, bucles y escenarios críticos. Protocolos de escalado.

**Criterios de evaluación.** Define objetivos y límites de autonomía; parametriza herramientas y memoria; valida la lógica operativa del agente.

---

## UD5. Validación y puesta en servicio

**Resultados de aprendizaje.** Valida la solución evaluando comportamiento funcional, calidad de respuesta e integración con el entorno.

**Contenidos.**

- Casos de prueba: entradas representativas, consultas complejas, errores esperados, ausencia de información, variaciones lingüísticas, condiciones límite.
- Evaluación de mantenimiento de contexto y respuestas fuera de alcance en soluciones conversacionales.
- Verificación de pertinencia, coherencia, completitud, trazabilidad y formato.
- Ajustes sobre instrucciones, parámetros, contexto y fuentes. Registro de versiones probadas.
- Documentación de pruebas: configuración, métricas, ciclo de resolución de incidencias.
- Puesta en servicio: documentación técnica, manuales operativos, guías de uso, soporte continuo.

**Criterios de evaluación.** Define y ejecuta casos de prueba; ajusta la solución según criterios de aceptación; formaliza la puesta en servicio.

---

## UD6. Seguridad, privacidad y uso ético

**Resultados de aprendizaje.** Aplica controles de seguridad, privacidad, trazabilidad y uso ético y responsable.

**Contenidos.**

- Riesgos de uso responsable: errores de precisión, alucinaciones, sesgos, toxicidad, dependencia excesiva. Supervisión humana.
- Supervisión de entradas para filtrar información confidencial, datos personales, secretos, credenciales.
- Revisión de fuentes: origen, vigencia, minimización, anonimización.
- Control de accesos: mínimo privilegio, separación de funciones, gestión de credenciales, trazabilidad.
- Verificación de resultados frente a exposición de datos protegidos.
- Marcos de autonomía controlada. Cuotas de uso y protocolos de parada o escalado.
- Pruebas adversariales e intentos de uso indebido.
- Transparencia: información sobre uso de IA generativa, etiquetado de contenidos, límites de precisión.

**Criterios de evaluación.** Evalúa riesgos y filtra información sensible; configura accesos y autonomía controlada; valida controles con pruebas adversariales.

---

## UD7. Vigilancia tecnológica de LLMs

**Resultados de aprendizaje.** Realiza vigilancia tecnológica sobre modelos, herramientas y técnicas asociadas, proponiendo mejoras.

**Contenidos.**

- Fuentes: documentación oficial de proveedores, repositorios, publicaciones científicas, comunidades, boletines de seguridad, registros de versiones.
- Recopilación periódica de novedades: modelos, capacidades, herramientas, vulnerabilidades, buenas prácticas.
- Análisis de relevancia, aplicabilidad, impacto sobre soluciones existentes y requisitos de adopción.
- Propuestas de mejora, actualización o sustitución.
- Reporte formal de la vigilancia.

**Criterios de evaluación.** Selecciona fuentes y recopila novedades; analiza su aplicabilidad; formula y reporta propuestas de mejora.

---

## UD8. Responsabilidad profesional, sostenibilidad y prevención

**Resultados de aprendizaje.** Actúa con responsabilidad profesional, sostenibilidad y seguridad, previniendo riesgos laborales (EC8 y EC9).

**Contenidos.**

- Rigor técnico, integridad ética, comunicación asertiva e inclusiva entre roles.
- Transmisión comprensible de instrucciones, resultados y limitaciones.
- Sostenibilidad: selección de arquitecturas, parámetros y mecanismos que reducen recursos, peticiones, contexto, energía y emisiones de CO₂. Principio DNSH y ODS.
- Prevención de riesgos: riesgos psicosociales, tecnoestrés, ergonomía cognitiva, física y ambiental. Plan de emergencias.

**Criterios de evaluación.** Comunica de forma adaptada al perfil destinatario; integra sostenibilidad en las decisiones técnicas; aplica medidas de prevención.

---

*Ocupaciones asociadas: integradores de soluciones con IA generativa, desarrolladores de agentes e interfaces de IA. Sector: desarrollo y explotación de sistemas de IA, área de desarrollo.*
