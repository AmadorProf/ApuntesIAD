# MP03 · Desarrollo de componentes para sistemas de ML

*Módulo profesional del CFS «Gestión de datos y entrenamiento IA (IAD)»*

| Campo | Valor |
|---|---|
| Código | MP03 |
| Estándar de competencia asociado | ECP2497_3 (Nivel 3) |
| Familia profesional | Inteligencia Artificial y Data |
| Duración orientativa | 200 h |
| Curso | 2.º |

**Competencia que desarrolla:** desarrollar soluciones de aprendizaje automático de extremo a extremo, desde el diseño de *pipelines* de datos multimodales y la implementación de modelos robustos hasta su integración en producción, asegurando trazabilidad y actualización tecnológica.

Las unidades didácticas (UD) concretan los resultados de aprendizaje del módulo. *Duración y curso son orientativos (propuesta).*

---

## UD1. Pipelines de datos para ML

**Resultados de aprendizaje.** Desarrolla *pipelines* de datos implementando ingesta, transformación y preparación para obtener *datasets* listos para entrenamiento.

**Contenidos.**

- Configuración del entorno de desarrollo: local, nube, Google Colab. Gestión de dependencias con gestores de paquetes o contenedores.
- Ingesta con Pandas, NumPy y otras librerías. Datos tabulares, imagen, texto, audio, vídeo y series temporales desde ficheros, bases de datos o APIs.
- Anotación multimodal cuando es necesario etiquetar.
- Limpieza, normalización y formateo. Generación de *datasets* en el formato de los *frameworks* de entrenamiento.
- Reproducibilidad y trazabilidad: versionado de código y de colecciones de datos.

**Criterios de evaluación.** Implementa procesos de ingesta multimodal; genera *datasets* consistentes; versiona el *pipeline* para reproducibilidad.

---

## UD2. Despliegue de modelos con frameworks especializados

**Resultados de aprendizaje.** Despliega modelos adaptando *frameworks* y librerías a la naturaleza del problema, desarrollando componentes reutilizables.

**Contenidos.**

- Modelos para datos tabulares, series temporales, imagen, vídeo y audio. Selección de arquitectura.
- Modelos para texto con librerías específicas y *fine-tuning*.
- Buenas prácticas: control de errores (Try-Catch), depuración, reutilización de componentes.
- Acceso y manipulación de datos estructurados y no estructurados externos.
- Ejecución del Plan de pruebas y tipos de prueba.
- Aislamiento y gestión de dependencias: entornos virtuales, gestores de paquetes.
- Control de versiones: ramificación, fusión, trazabilidad de cambios.

**Criterios de evaluación.** Despliega modelos según el tipo de dato; programa con control de errores y reutilización; gestiona dependencias y versiones.

---

## UD3. Integración de modelos en aplicaciones

**Resultados de aprendizaje.** Integra modelos en aplicaciones exportándolos en formatos estándar e implementando APIs de inferencia.

**Contenidos.**

- Estandarización del modelo para portabilidad.
- API de inferencia local o en la nube. Exposición como servicio consumible.
- Cuantización (*clustering*) de vectores. Representación simplificada de datos complejos.
- Discretización del espacio de entrada: *autoencoders*, Mapas Autoorganizativos de Kohonen (SOM).
- Memoria asociativa y procesamiento de secuencias: redes recurrentes con puertas, arquitecturas basadas en atención.
- Problemas no linealmente separables: perceptrón multicapa (MLP).
- Redes especializadas: convolucionales (datos espaciales), de grafos (datos relacionales).
- Integración de modelos preentrenados de repositorios y librerías.

**Criterios de evaluación.** Expone el modelo mediante API; selecciona la arquitectura de red según la naturaleza del dato; integra modelos preentrenados correctamente.

---

## UD4. Validación de la calidad de los componentes

**Resultados de aprendizaje.** Valida los componentes comprobando consistencia del *pipeline*, rendimiento y sesgos del modelo.

**Contenidos.**

- Verificación del *pipeline*: transformaciones sin errores ni sesgos, consistencia de formatos por etapa.
- Consistencia y reproducibilidad: mismas entradas, mismas salidas.
- Análisis de sesgos con técnicas de *fairness*. Comportamientos discriminatorios.
- Rendimiento sobre subconjuntos. Detección de sobreajuste e infraajuste.
- Extracción de conocimiento con metodología KDD.
- Algoritmos: clasificación, regresión lineal y logística, árboles de decisión, bosques aleatorios, SVM, métodos de potenciación.
- Ingeniería de características: normalización, estandarización, codificación, características derivadas reutilizables.

**Criterios de evaluación.** Verifica el *pipeline* y la reproducibilidad; evalúa sesgos y robustez; implementa transformaciones de características reutilizables.

---

## UD5. Protocolización y documentación técnica

**Resultados de aprendizaje.** Protocoliza los componentes elaborando documentación técnica, fichas de modelo y registros de decisiones.

**Contenidos.**

- Control de versiones (Git) para documentar arquitectura, dependencias y lógica de diseño.
- Ficha técnica del modelo (*model card*): métricas, datos, limitaciones, casos de uso.
- Empaquetado para distribución y reutilización.
- Documentación de pruebas unitarias y de regresión.

**Criterios de evaluación.** Protocoliza con control de versiones; elabora la *model card*; documenta procedimientos y resultados de pruebas.

---

## UD6. Vigilancia tecnológica

**Resultados de aprendizaje.** Realiza vigilancia tecnológica para identificar herramientas, arquitecturas y oportunidades aplicables.

**Contenidos.**

- Fuentes técnicas: Papers with Code, arXiv, HuggingFace Hub.
- Evaluación de herramientas mediante pruebas de concepto comparadas con las soluciones actuales.
- Tendencias del sector: blogs técnicos, conferencias, anuncios de empresas de referencia.
- Monitorización de normativa y regulación aplicable.
- Transferencia de hallazgos al equipo mediante informes o presentaciones.

**Criterios de evaluación.** Monitoriza fuentes de referencia; evalúa la aplicabilidad de novedades; comparte hallazgos con el equipo.

---

## UD7. Gestión integral: seguridad, sostenibilidad y ética

**Resultados de aprendizaje.** Implementa soluciones bajo un marco que vincula eficiencia tecnológica, seguridad y responsabilidad ética (EC7).

**Contenidos.**

- Mitigación del tecnoestrés. Ergonomía física y EPI específicos.
- Plan de actuación ante emergencias.
- Paradigma *Green AI*: minimización del consumo energético y la huella de carbono digital.
- Excelencia técnica, aprendizaje continuo, protección de datos y privacidad por diseño.

**Criterios de evaluación.** Aplica criterios de *Green AI*; garantiza protección de datos en el desarrollo; mantiene un entorno seguro.

---

*Ocupaciones asociadas: desarrolladores de Inteligencia Artificial y Data. Sector: análisis y gestión de datos, área de programación.*
