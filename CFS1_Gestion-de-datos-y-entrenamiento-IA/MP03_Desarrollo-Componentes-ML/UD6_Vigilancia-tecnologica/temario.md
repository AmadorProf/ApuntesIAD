# UD6 · Vigilancia tecnológica en sistemas de ML

---

## 1. Introducción

El campo del aprendizaje automático y la inteligencia artificial es, en la actualidad, uno de los más dinámicos en toda la historia de la ingeniería del software. Lo que hace cinco años era investigación académica de vanguardia hoy forma parte de los pipelines de producción de empresas de todos los tamaños. Lo que se publicó hace seis meses puede haber quedado desplazado por tres o cuatro trabajos posteriores que establecen nuevos puntos de referencia. Esta velocidad no es accidental: es el resultado de una combinación de factores que se refuerzan mutuamente — la disponibilidad masiva de datos, el abaratamiento del cómputo distribuido, la cultura de publicación abierta impulsada por arXiv, y la colaboración global entre equipos de investigación industriales y académicos.

Para un profesional que trabaja en el desarrollo de componentes de machine learning, esta dinámica plantea un reto permanente: mantenerse al corriente no es una actividad opcional ni puntual, sino una responsabilidad continua del rol. Un ingeniero de ML que deja de seguir la literatura durante seis meses puede encontrarse tomando decisiones de diseño basadas en suposiciones que la comunidad ya ha refutado, usando arquitecturas que han sido superadas, o desconociendo herramientas que habrían simplificado enormemente su trabajo.

La vigilancia tecnológica responde a este problema con una disciplina sistemática. No se trata de leer todo lo que se publica — eso es imposible — sino de construir un sistema personalizado y sostenible que permita detectar señales relevantes, filtrar el ruido, evaluar críticamente lo que merece atención, y convertir ese conocimiento en decisiones concretas dentro del entorno profesional. Esta unidad didáctica recorre cada uno de esos pasos con suficiente detalle práctico para que el estudiante pueda aplicarlos desde el primer día.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Identificar y seleccionar las fuentes de información más relevantes para el seguimiento de avances en ML, distinguiendo entre tipos de fuente según su audiencia, rigor y velocidad de publicación.
- Diseñar e implementar un sistema personal de vigilancia tecnológica, combinando herramientas de suscripción, gestión de referencias y organización del conocimiento.
- Aplicar una metodología estructurada para leer y evaluar papers científicos de ML, identificando sus fortalezas, limitaciones y grado de aplicabilidad en contextos productivos.
- Utilizar marcos como el Technology Readiness Level (TRL) y el Gartner Hype Cycle para evaluar la madurez de tecnologías emergentes en IA.
- Organizar y difundir el conocimiento adquirido dentro de un equipo técnico, mediante formatos como tech talks, documentación interna y pruebas de concepto.
- Tomar decisiones informadas sobre adopción, experimentación o espera respecto a nuevas tecnologías de ML.

---

## 3. Fuentes de información

Una buena estrategia de vigilancia tecnológica comienza por mapear el ecosistema de fuentes disponibles. Estas fuentes se pueden clasificar en cinco grandes categorías: literatura científica, conferencias, blogs técnicos, repositorios de código, y newsletters curadas. Cada una tiene características distintas en cuanto a profundidad, velocidad y tipo de audiencia.

### 3.1 Literatura científica

**arXiv** es el repositorio de preprints científicos más importante en ML. Las categorías más relevantes son `cs.LG` (Machine Learning), `stat.ML` (Statistics and Machine Learning), y `cs.AI` (Artificial Intelligence). También son de interés `cs.CV` (Computer Vision), `cs.CL` (Computation and Language) y `cs.RO` (Robotics). arXiv permite publicar resultados sin revisión por pares previa, lo que acelera la difusión pero requiere mayor sentido crítico por parte del lector. La mayoría de los trabajos importantes se publican primero aquí antes de ser aceptados en conferencias.

**Papers with Code** combina papers con sus implementaciones públicas disponibles en GitHub. Su valor añadido es doble: facilita encontrar código asociado a cada paper, y mantiene leaderboards actualizados del estado del arte en cientos de tareas y datasets, lo que permite comparar resultados de manera objetiva y trazable.

**Google Scholar** permite hacer seguimiento bibliométrico, configurar alertas por autor o por término de búsqueda, y descubrir trabajo relacionado a través de las citas. Es especialmente útil para seguir la trayectoria de investigadores concretos.

### 3.2 Conferencias de referencia

Las conferencias en ML combinan publicación científica y comunidad. Aceptan trabajos sometidos a revisión por pares doble ciego, y los proceedings son de acceso abierto en la mayoría de los casos.

**NeurIPS** (Conference on Neural Information Processing Systems) es la conferencia más grande e influyente en ML. **ICML** (International Conference on Machine Learning) tiene un enfoque más centrado en los fundamentos teóricos y algorítmicos. **ICLR** (International Conference on Learning Representations) se centra en representaciones aprendidas y es conocida por su proceso de revisión abierto, donde los reviews y las discusiones son públicos antes de que se tomen las decisiones de aceptación.

En visión por computador, **CVPR** (Conference on Computer Vision and Pattern Recognition) es el foro de referencia. En procesamiento del lenguaje natural, **ACL** (Association for Computational Linguistics) y **EMNLP** (Empirical Methods in Natural Language Processing) son las más relevantes.

Seguir los proceedings de estas conferencias — o al menos los trabajos destacados que la comunidad resalta — es una forma eficiente de estar al tanto de los avances más sólidos del campo.

### 3.3 Blogs técnicos

Los blogs técnicos de calidad son intermediarios valiosos entre la densidad de los papers y la superficialidad de la divulgación. Los mejores combinan rigor con accesibilidad.

**Distill.pub** publica artículos interactivos con visualizaciones que explican conceptos complejos de ML con un nivel de claridad excepcional. Aunque su ritmo de publicación es lento, cada artículo es una referencia de alta calidad.

**The Gradient** publica ensayos y entrevistas sobre tendencias en IA, con contribuciones de investigadores activos del campo.

**Lilian Weng's blog** (lilianweng.github.io) es uno de los recursos más citados de la comunidad. Sus posts son síntesis exhaustivas y bien estructuradas sobre temas como attention mechanisms, meta-learning, o reinforcement learning. Son excelentes puntos de partida antes de entrar en la literatura primaria.

**fast.ai** combina cursos prácticos con posts técnicos que defienden un enfoque top-down y aplicado al aprendizaje de ML. Su perspectiva critica regularmente supuestos del mainstream y ofrece reflexiones valiosas sobre pedagogía y práctica.

### 3.4 Repositorios de código

**GitHub Trending** muestra los repositorios con más actividad en un período dado, filtrable por lenguaje y por período temporal. Es una señal rápida de qué herramientas están ganando tracción en la comunidad.

**Hugging Face** es el hub central para modelos preentrenados, datasets y espacios de demo. Su Model Hub y Dataset Hub son fuentes de información sobre qué arquitecturas y datos se están usando activamente en producción. Las discusiones en los repositorios del Hub también son una señal útil sobre problemas frecuentes y casos de uso reales.

### 3.5 Newsletters

Las newsletters curadas reducen el coste de atención de la vigilancia al agregar y filtrar en nombre del lector.

**The Batch** (deeplearning.ai, Andrew Ng) ofrece un resumen semanal de noticias y papers relevantes, con comentarios del propio Ng que contextualizan la importancia de cada item.

**Import AI** (Jack Clark) es una newsletter de lectura más técnica y densa, orientada a profesionales e investigadores. Clark, cofundador de Anthropic y exdirector de política de OpenAI, aporta una perspectiva única sobre las implicaciones técnicas y sociales de los avances en IA.

**Ahead of AI** (Sebastian Raschka) combina tutoriales técnicos con análisis de papers recientes. Raschka es conocido por su capacidad para explicar conceptos complejos con claridad y precisión, y su newsletter refleja esa misma calidad.

---

## 4. Metodología de vigilancia sistemática

Tener acceso a buenas fuentes no es suficiente. Sin un proceso estructurado, el flujo de información se convierte en ruido. La metodología de vigilancia sistemática organiza ese flujo en cinco etapas secuenciales.

### 4.1 Las cinco etapas

**Etapa 1: Identificación de fuentes.** El primer paso es definir el mapa de fuentes que se va a monitorizar. Este mapa no es estático: se construye progresivamente y se ajusta en función de la utilidad real observada. Un error común es añadir fuentes sin criterio de selección, lo que produce sobrecarga. El criterio debe ser relevancia para el rol actual y los proyectos en curso.

**Etapa 2: Recopilación.** Una vez identificadas las fuentes, se establece un mecanismo de recogida automatizada. Las herramientas más útiles son los feeds RSS, las alertas por email, y los sistemas de suscripción a newsletters. El objetivo es que la información llegue al profesional, no que el profesional tenga que ir a buscarla cada vez.

**Etapa 3: Filtrado.** La recopilación genera un volumen que no puede leerse en su totalidad. El filtrado es el proceso de seleccionar qué merece atención. El criterio puede basarse en palabras clave, en autores de referencia, en la resonancia social de un trabajo (número de estrellas en GitHub, menciones en Twitter/X o en otras newsletters), o en la relevancia directa para proyectos activos.

**Etapa 4: Análisis.** Los items que superan el filtro se leen con distintos niveles de profundidad según su importancia. Un paper puede leerse solo el abstract y las conclusiones, o puede merecer una lectura completa con notas. Esta etapa es la que transforma información en conocimiento.

**Etapa 5: Difusión.** El conocimiento adquirido no debe quedarse en el ámbito individual. La difusión — mediante documentación interna, tech talks, o simplemente compartir un link con contexto en un canal de equipo — multiplica el valor de la vigilancia y construye cultura técnica en la organización.

### 4.2 Herramientas de soporte

**Zotero** es un gestor de referencias bibliográficas de código abierto. Permite organizar papers por colecciones y etiquetas, añadir notas y anotaciones, y exportar bibliografías en múltiples formatos. Su extensión de navegador captura metadatos de papers en arXiv, Google Scholar y otros repositorios con un solo clic. Para equipos, Zotero permite compartir librerías, lo que facilita la gestión colectiva de referencias.

**Google Scholar Alerts** permite configurar alertas por término de búsqueda o por autor. Cuando aparecen nuevos trabajos que coinciden con los criterios definidos, se recibe una notificación por email. Es un mecanismo pasivo de vigilancia especialmente útil para seguir líneas de investigación específicas.

**arXiv email digests** permite suscribirse a las categorías de arXiv de interés y recibir cada día hábil un resumen de los nuevos preprints publicados en esas categorías.

**GitHub Watch y Stars** permiten seguir la actividad de repositorios de interés. Observar un repositorio con la opción "Watching" genera notificaciones de todas las actualizaciones. Las Stars funcionan como marcadores y también como señal de popularidad visible para otros.

**RSS feeds** siguen siendo una de las herramientas más eficientes para la vigilancia sistemática. La mayoría de los blogs técnicos y newsletters de calidad ofrecen feeds RSS. Un lector como Feedly o NetNewsWire centraliza todas las fuentes en una sola interfaz, permitiendo revisar titulares de manera eficiente sin visitar cada sitio individualmente.

**Obsidian** es una herramienta de gestión del conocimiento personal basada en notas en Markdown enlazadas entre sí. Su modelo de "second brain" facilita la conexión entre conceptos, la organización de notas de papers, y la construcción progresiva de un mapa de conocimiento personal. Plugins como Dataview permiten crear vistas dinámicas sobre las notas, útiles por ejemplo para listar todos los papers pendientes de leer o para generar un mapa de tecnologías evaluadas.

---

## 5. Evaluación crítica de papers de ML

Saber dónde encontrar papers es necesario pero insuficiente. La capacidad de leerlos de manera eficiente y evaluarlos con criterio es la competencia central de la vigilancia tecnológica en contextos técnicos.

### 5.1 Cómo leer un paper eficientemente

El modelo más difundido para la lectura estructurada de papers es el método de las tres pasadas, descrito por Srinivasan Keshav en su artículo "How to Read a Paper" (2007). La primera pasada dura entre cinco y diez minutos y consiste en leer el título, el abstract, la introducción, los encabezados de sección, las conclusiones y las referencias para tener una visión general del trabajo. Al término de esta pasada, el lector debe poder responder: ¿de qué trata el paper? ¿es relevante para mis intereses actuales? La segunda pasada implica leer el paper con más atención, revisando figuras, tablas y diagramas, pero sin entrar en las demostraciones matemáticas. La tercera pasada, reservada para trabajos que merecen entendimiento profundo, implica intentar reimplementar virtualmente el paper, identificando cada suposición y verificando cada afirmación.

La mayoría de los papers de ML siguen una estructura IMRaD adaptada: Introducción (motivación, problema, contribución), Trabajo relacionado, Metodología (arquitectura, datos, procedimiento de entrenamiento), Resultados (experimentos, métricas, comparación con baselines), Discusión y Conclusiones.

### 5.2 Checklist de evaluación

Al leer un paper de ML con intención evaluativa, conviene responder sistemáticamente a las siguientes preguntas:

**Reproducibilidad:** ¿Se proporciona suficiente detalle metodológico para reimplementar el experimento? ¿Se reportan los hiperparámetros, las semillas aleatorias, el procedimiento de selección de modelos? ¿Está disponible el código?

**Dataset:** ¿Qué datos se usaron? ¿Son públicos y accesibles? ¿Hay riesgo de data leakage? ¿El dataset es representativo del dominio de aplicación que me interesa? ¿Qué tamaño tiene el conjunto de test?

**Comparación con baselines:** ¿Con qué se compara el método propuesto? ¿Los baselines están implementados correctamente o son versiones degradadas? ¿Se usaron los mismos datos y condiciones de evaluación para todos los métodos?

**Coste computacional:** ¿Cuántos recursos requirió el entrenamiento? ¿Es replicable en hardware convencional o requiere clústeres de GPUs de alta gama? ¿Se analiza la eficiencia en inferencia?

**Disponibilidad de código:** ¿Se incluye un enlace a repositorio? ¿El código está documentado y es ejecutable? ¿Hay un Makefile o script de reproducción de experimentos?

**Generalización:** ¿Los resultados se obtienen en un solo dataset o en múltiples? ¿Se incluyen experimentos de ablación que permiten entender qué parte del método aporta el beneficio observado?

### 5.3 Diferencia entre SOTA de investigación y producción

Un error frecuente en profesionales que empiezan a seguir literatura de ML es confundir el estado del arte de investigación con lo que es aplicable en producción. Un modelo puede alcanzar mejores métricas en un benchmark pero ser completamente impracticable en producción por su tamaño, latencia, coste de inferencia, o falta de librerías estables. La investigación está optimizada para demostrar avances; la producción está optimizada para funcionar de manera confiable, eficiente y mantenible bajo condiciones reales.

Algunos criterios para evaluar la aplicabilidad en producción de un resultado de investigación: ¿existe una implementación en librerías maduras como PyTorch, Hugging Face Transformers, o scikit-learn? ¿Hay casos documentados de uso en producción? ¿La mejora de métricas es lo suficientemente grande como para justificar el coste de adopción? ¿El método es compatible con las restricciones de infraestructura del entorno de destino?

### 5.4 Leaderboards como señales de madurez

**Hugging Face Open LLM Leaderboard** es una referencia para comparar el rendimiento de modelos de lenguaje en benchmarks estandarizados. Permite filtrar por tamaño de modelo, tipo de licencia y otras dimensiones prácticas.

**Papers with Code State of the Art** organiza los mejores resultados por tarea y dataset, con enlaces directos a los papers y al código correspondiente. Es la referencia más completa para mapear el estado del arte en cualquier tarea de ML.

Estos leaderboards deben leerse con sentido crítico: los benchmarks pueden estar saturados, pueden no reflejar el rendimiento en datos reales, y pueden ser susceptibles a overfitting implícito si los modelos se han evaluado repetidamente sobre el mismo conjunto de test.

---

## 6. Análisis de madurez tecnológica

No todas las tecnologías emergentes en ML merecen la misma respuesta. Algunas están listas para adoptarse; otras merecen experimentación controlada; otras conviene observar desde la distancia hasta que maduren. Los marcos de análisis de madurez ayudan a tomar estas decisiones de manera informada.

### 6.1 Technology Readiness Level (TRL) adaptado a ML

El TRL es una escala de nueve niveles desarrollada originalmente por la NASA para evaluar la madurez de tecnologías aeroespaciales. Adaptado al contexto de ML, puede interpretarse de la siguiente manera:

- **TRL 1-2:** Principios básicos observados; trabajo de investigación especulativo, pocas evidencias experimentales.
- **TRL 3-4:** Prueba de concepto; experimentos de laboratorio en datos controlados; reproducibilidad limitada.
- **TRL 5-6:** Validación en entorno relevante; resultados replicables; implementaciones de referencia disponibles.
- **TRL 7-8:** Demostración en entorno de producción; librería estable; soporte comunitario activo.
- **TRL 9:** Tecnología madura; adoptada en producción a escala; soporte empresarial disponible; documentación extensa.

Una tecnología en TRL 3 puede ser fascinante y merecer seguimiento, pero no está lista para integrarse en un pipeline productivo. Una tecnología en TRL 8-9, aunque menos novedosa, es la candidata natural para adopción.

### 6.2 Gartner Hype Cycle y su aplicación en IA

El Gartner Hype Cycle es un modelo gráfico que describe el ciclo de expectativas y desilusiones asociado a la adopción de nuevas tecnologías. Consta de cinco fases:

**Disparador de innovación:** Aparece la tecnología, generalmente impulsada por un hito de investigación o un producto notable. La cobertura mediática empieza a crecer.

**Pico de expectativas infladas:** El entusiasmo supera a la evidencia. Las expectativas sobre lo que la tecnología puede hacer se inflan por encima de lo que su estado de madurez permite. Los primeros adoptantes experimentan con la tecnología, con resultados mixtos.

**Valle de la desilusión:** Los proyectos piloto no cumplen las expectativas. El entusiasmo decae. Parte de la cobertura mediática se vuelve crítica o indiferente. Algunos proveedores desaparecen del mercado.

**Rampa de consolidación:** Los equipos que han persistido con la tecnología empiezan a entender sus casos de uso reales y sus limitaciones. Las mejores prácticas emergen. La tecnología empieza a generar valor tangible en entornos específicos.

**Meseta de productividad:** La tecnología alcanza madurez y adopción generalizada. Sus aplicaciones son ampliamente comprendidas y están bien documentadas.

El Hype Cycle de Gartner para IA se publica anualmente y es una referencia útil para situar tecnologías concretas — como los Large Language Models, los modelos de difusión, el aprendizaje por refuerzo con retroalimentación humana (RLHF), o las arquitecturas multimodales — en alguna de estas fases. En los ciclos de 2023 y 2024, los LLMs alcanzaron el pico de expectativas infladas, mientras que tecnologías como el MLOps y el aprendizaje federado avanzaban hacia la rampa de consolidación.

### 6.3 Criterios de adopción tecnológica

Más allá de los marcos formales, la decisión de adoptar una nueva tecnología en un entorno profesional de ML puede estructurarse en torno a cuatro criterios:

**Madurez de la librería:** ¿Existe una implementación en una librería activamente mantenida? ¿Cuántas versiones estables ha tenido? ¿Hay un changelog público y un proceso de deprecación responsable?

**Comunidad:** ¿Cuántos repositorios en GitHub usan esta tecnología? ¿Hay respuestas actualizadas en Stack Overflow? ¿Existe un foro o canal de Discord/Slack activo? ¿Cuántos tutoriales independientes existen?

**Soporte empresarial:** ¿Alguna empresa con recursos ofrece soporte comercial o lo usa internamente en producción? ¿Hay ofertas de empleo que mencionen esta tecnología? El soporte empresarial es una señal de que la tecnología sobrevivirá y será mantenida.

**Casos de uso documentados en producción:** ¿Existen blog posts de empresas reales describiendo cómo usan esta tecnología en producción? ¿Hay talks en conferencias de ingeniería — MLSys, PyTorch Conference, Ray Summit — describiendo su uso a escala? Los casos de uso en producción son la señal más sólida de aplicabilidad real.

---

## 7. Gestión del conocimiento y difusión

La vigilancia tecnológica no termina en el análisis individual. Su valor máximo se realiza cuando el conocimiento se integra en los procesos de equipo y en las decisiones de producto.

### 7.1 Tech talks y sesiones de paper review

Las **tech talks** son presentaciones internas de duración corta — típicamente entre 20 y 45 minutos — en las que un miembro del equipo comparte un hallazgo relevante de la vigilancia tecnológica. Pueden tomar la forma de resumen de un paper, análisis de una nueva herramienta, o comparación de alternativas para un problema técnico específico. Para ser efectivas, deben estar orientadas a la toma de decisiones: ¿qué implica esto para nuestro trabajo?

Las **sesiones de paper review** son un formato más estructurado en el que el equipo lee un paper de manera colectiva o individual y luego debate sus implicaciones. Algunos equipos adoptan un club de lectura semanal o quincenal. El valor de estas sesiones no es solo técnico: construyen un lenguaje común y desarrollan la capacidad crítica del equipo como colectivo.

### 7.2 Documentación de hallazgos

El conocimiento que no se documenta se pierde. Las notas de paper review, los resultados de experimentos de evaluación de nuevas tecnologías, y las conclusiones de tech talks deben almacenarse en un sistema accesible para el equipo. Un wiki interno (Notion, Confluence, o simplemente un repositorio de Markdown en git) es suficiente. Lo importante es que exista una convención compartida sobre dónde guardar cada tipo de artefacto.

Una plantilla mínima para la documentación de un hallazgo de vigilancia puede incluir: fecha, fuente, resumen del trabajo o tecnología, evaluación de relevancia y madurez, conclusión (adoptar / experimentar / esperar / descartar) y próximos pasos si procede.

### 7.3 POCs para nuevas tecnologías

Cuando una tecnología supera el umbral de relevancia y madurez, el siguiente paso antes de la adopción plena es una prueba de concepto (POC). Una POC bien estructurada tiene un alcance acotado, un conjunto de criterios de evaluación definidos a priori, un tiempo límite, y un artefacto de salida que documenta los resultados.

Los criterios de evaluación de una POC de ML pueden incluir: rendimiento en métricas relevantes para el caso de uso, coste computacional, facilidad de integración con la infraestructura existente, curva de aprendizaje del equipo, y compatibilidad con los requisitos de licencia del proyecto.

### 7.4 Toma de decisiones de adopción

La decisión de adoptar, experimentar o esperar respecto a una nueva tecnología debe ser explícita y documentada. Una forma útil de estructurarla es mediante una matriz que cruza el nivel de madurez de la tecnología con el nivel de urgencia de la necesidad que podría cubrir. Tecnologías maduras que cubren una necesidad urgente se adoptan; tecnologías inmaduras que podrían cubrir una necesidad futura se monitorizan; tecnologías inmaduras sin necesidad clara se descartan del radar a corto plazo.

Esta toma de decisiones no debe ser unilateral. Involucrar al equipo en la discusión — incluso cuando la decisión final la toma una persona — mejora la calidad de la decisión y aumenta el compromiso con su implementación.

---

## 8. Actividades prácticas

### Actividad 1: Construcción del sistema de vigilancia personal

El estudiante diseña e implementa su propio sistema de vigilancia tecnológica. El entregable es un documento que especifica: las fuentes seleccionadas y el justificativo de cada selección, las herramientas usadas para automatizar la recopilación (feeds RSS, alertas, suscripciones), la herramienta de gestión del conocimiento elegida (Obsidian, Notion, Zotero u otra), y el protocolo de revisión semanal que seguirá. Una semana después, el estudiante entrega un diario de vigilancia con los hallazgos más relevantes del período y una reflexión sobre el funcionamiento del sistema.

### Actividad 2: Evaluación crítica de un paper de ML

El estudiante selecciona un paper publicado en los últimos 12 meses en arXiv o en los proceedings de una de las conferencias de referencia (NeurIPS, ICML, ICLR, CVPR, ACL). Aplica el checklist de evaluación de la sección 5.2 y redacta un informe de dos a tres páginas que responde sistemáticamente a cada criterio. El informe concluye con una valoración personal sobre la aplicabilidad del trabajo en un contexto productivo hipotético definido por el propio estudiante.

### Actividad 3: Análisis de madurez tecnológica

El estudiante elige tres tecnologías de ML que hayan ganado visibilidad en el último año (ejemplos posibles: modelos de difusión para generación de series temporales, mecanismos de atención eficiente como FlashAttention, fine-tuning eficiente con LoRA, frameworks de agentes como LangChain o LlamaIndex). Para cada tecnología, estima su posición en el TRL y en el Hype Cycle de Gartner, justificando su estimación con evidencias concretas (papers, repositorios, casos de uso documentados, estado de las librerías). El entregable es una tabla comparativa comentada.

### Actividad 4: Tech talk de equipo

En grupos de tres o cuatro personas, el equipo prepara y presenta una tech talk de 20 minutos sobre una tecnología o paper relevante. La presentación debe incluir: contexto del problema, descripción de la tecnología o hallazgo, evaluación de madurez, implicaciones para el trabajo del equipo, y recomendación de acción (adoptar / experimentar / esperar). Se valorará la claridad de la exposición, la solidez del análisis crítico y la calidad de la recomendación final.

---

## 9. Referencias

**Literatura científica y repositorios:**

- arXiv Machine Learning: https://arxiv.org/list/cs.LG/recent
- arXiv Artificial Intelligence: https://arxiv.org/list/cs.AI/recent
- Papers with Code: https://paperswithcode.com
- Papers with Code State of the Art: https://paperswithcode.com/sota
- Hugging Face Model Hub: https://huggingface.co/models
- Hugging Face Open LLM Leaderboard: https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard

**Blogs técnicos:**

- Distill.pub: https://distill.pub
- The Gradient: https://thegradient.pub
- Lilian Weng's blog: https://lilianweng.github.io
- fast.ai blog: https://www.fast.ai/blog

**Newsletters:**

- The Batch (deeplearning.ai): https://www.deeplearning.ai/the-batch/
- Import AI (Jack Clark): https://jack-clark.net
- Ahead of AI (Sebastian Raschka): https://magazine.sebastianraschka.com

**Herramientas:**

- Zotero: https://www.zotero.org
- Obsidian: https://obsidian.md
- Feedly (lector RSS): https://feedly.com

**Referencias académicas y metodológicas:**

- Keshav, S. (2007). "How to Read a Paper". *ACM SIGCOMM Computer Communication Review*, 37(3), 83-84. Disponible en: https://web.stanford.edu/class/ee384m/Handouts/HowtoReadPaper.pdf
- Gartner Hype Cycle for Artificial Intelligence (edición anual). Disponible para suscriptores en: https://www.gartner.com/en/documents/hype-cycle-for-artificial-intelligence
- Hunt, A. & Thomas, D. (1999). *The Pragmatic Programmer: From Journeyman to Master*. Addison-Wesley. (Edición actualizada: *The Pragmatic Programmer: Your Journey to Mastery*, 20th Anniversary Edition, 2019.)
- Norvig, P. & Russell, S. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson. Capítulo 1: Introduction — útil como contexto para entender la velocidad de cambio del campo.
- Sculley, D. et al. (2015). "Hidden Technical Debt in Machine Learning Systems". *Advances in Neural Information Processing Systems*, 28. https://proceedings.neurips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html — referencia clave para entender por qué la evaluación crítica de nuevas tecnologías importa en producción.

---

*Unidad elaborada para el módulo MP03 — Desarrollo de Componentes de ML, dentro del CFS1 — Gestión de Datos y Entrenamiento de IA.*
