# UD1 · Selección de la estrategia de entrenamiento

**Módulo:** MP02 — Entrenamiento de Modelos  
**Ciclo:** CFS1 — Gestión de Datos e Inteligencia Artificial  
**Nivel:** Formación Superior  
**Duración estimada:** 12 horas lectivas

---

## 1. Introducción

El entrenamiento de un modelo de aprendizaje automático es el proceso mediante el cual un sistema computacional ajusta sus parámetros internos a partir de datos con el fin de capturar patrones que le permitan generalizar a situaciones no vistas. Sin embargo, el acto técnico de entrenar —ejecutar un optimizador sobre una función de pérdida— es solo la punta del iceberg. Antes de que comience la primera iteración del descenso de gradiente o de que se construya el primer árbol de decisión, se toman decisiones estratégicas que determinan de manera casi irreversible el éxito o fracaso del proyecto.

La selección de la estrategia de entrenamiento engloba un conjunto de decisiones previas al modelado: ¿qué tipo de aprendizaje es el adecuado para el problema? ¿Qué familia de algoritmos se ajusta a los datos disponibles y a las restricciones del sistema? ¿Cuál es el nivel de interpretabilidad exigido por el negocio o la regulación? ¿Cuánto tiempo y compute tenemos? Estas preguntas no tienen respuestas universales, y esa ausencia de respuesta universal es, precisamente, el punto de partida intelectual de esta unidad.

Un error frecuente en equipos con poca madurez en ciencia de datos es saltar directamente a algoritmos complejos —redes neuronales profundas, gradient boosting sobre centenares de variables— sin haber analizado el problema con rigor. El resultado suele ser modelos sobreajustados, imposibles de mantener, difíciles de explicar y que superan por muy poco a métodos más simples que habrían sido suficientes. Esta unidad proporciona el marco analítico para tomar esas decisiones con criterio.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Clasificar cualquier problema de aprendizaje automático dentro de la taxonomía de paradigmas de aprendizaje (supervisado, no supervisado, semi-supervisado, auto-supervisado y por refuerzo) y justificar la clasificación.
2. Enunciar el teorema No Free Lunch y derivar de él implicaciones concretas para la práctica profesional.
3. Aplicar un conjunto estructurado de criterios —datos, dimensionalidad, tipo de variable objetivo, interpretabilidad, latencia, coste computacional y escalabilidad— para orientar la selección del algoritmo ante un nuevo caso de uso.
4. Comparar técnicamente las principales familias de algoritmos (modelos lineales, árboles y ensembles, redes neuronales) en cuanto a sus fortalezas, limitaciones y condiciones de uso óptimo.
5. Definir y entrenar un modelo baseline antes de explorar alternativas más complejas.
6. Documentar el análisis de un problema real y trazar el mapa entre sus requisitos y la estrategia de ML seleccionada.

---

## 3. Taxonomía del aprendizaje automático

### 3.1 Aprendizaje supervisado

En el aprendizaje supervisado el modelo aprende a partir de un conjunto de pares entrada-salida $(x_i, y_i)$ donde $y_i$ es la etiqueta o valor objetivo. El objetivo es aprender una función $f: X \to Y$ que generalice bien sobre datos no vistos.

**Clasificación.** La variable objetivo $y$ pertenece a un conjunto discreto de clases. El modelo asigna una entrada a una categoría. Ejemplos cotidianos: detección de spam (spam / no spam), diagnóstico de enfermedades a partir de imágenes médicas, clasificación de sentimientos en reseñas de producto. Los algoritmos prototípicos incluyen regresión logística, máquinas de vectores de soporte (SVM), árboles de decisión, Random Forest y redes neuronales. Las métricas de evaluación más habituales son precisión (precision), exhaustividad (recall), F1-score y AUC-ROC.

**Regresión.** La variable objetivo $y$ es continua. El modelo estima un valor numérico: precio de una vivienda, temperatura en 24 horas, número esperado de ventas. Los algoritmos de referencia son la regresión lineal y sus variantes regularizadas (Ridge, Lasso, ElasticNet), árboles de regresión, Random Forest y redes neuronales. Las métricas típicas son el error cuadrático medio (MSE), la raíz del error cuadrático medio (RMSE) y el coeficiente de determinación $R^2$.

### 3.2 Aprendizaje no supervisado

No se dispone de etiquetas. El modelo debe descubrir estructura en los datos por sí mismo. Es el paradigma más habitual en exploración de datos y preprocesamiento.

**Clustering.** Agrupa las observaciones en subconjuntos homogéneos. Los algoritmos canónicos son K-Means, DBSCAN, clustering jerárquico aglomerativo y Gaussian Mixture Models (GMM). Aplicaciones: segmentación de clientes, detección de grupos de genes en bioinformática, agrupación de documentos.

**Reducción dimensional.** Proyecta los datos de un espacio de alta dimensión a uno de menor dimensión preservando la información relevante. PCA (Análisis de Componentes Principales) es el método lineal de referencia; t-SNE y UMAP son técnicas no lineales ampliamente usadas para visualización. Autoencoders (redes neuronales) ofrecen reducciones no lineales aprendidas.

**Detección de anomalías.** Identifica observaciones que se desvían significativamente del comportamiento esperado. Métodos relevantes: Isolation Forest, Local Outlier Factor (LOF), One-Class SVM. Aplicaciones: fraude bancario, fallos en maquinaria industrial, intrusiones en redes informáticas.

### 3.3 Aprendizaje semi-supervisado

Combina un pequeño conjunto de datos etiquetados con un volumen mucho mayor de datos sin etiquetar. Es especialmente útil cuando etiquetar es costoso (requiere expertos humanos, tiempo clínico, etc.) pero obtener datos en bruto es barato. Los métodos más frecuentes incluyen self-training (el modelo etiqueta datos no supervisados en iteraciones sucesivas), graph-based methods y consistency regularization.

### 3.4 Aprendizaje auto-supervisado

El modelo genera sus propias señales de supervisión a partir de los datos sin etiquetar. Es la base de los grandes modelos de lenguaje (LLM): predecir la siguiente palabra en un texto es una tarea auto-supervisada. En visión por computador, métodos como SimCLR y DINO aprenden representaciones contrastando versiones aumentadas de la misma imagen. El aprendizaje auto-supervisado ha demostrado que el preentrenamiento en grandes corpus sin etiquetar produce representaciones transferibles de gran calidad.

### 3.5 Aprendizaje por refuerzo (RL)

Un agente interactúa con un entorno tomando acciones y recibiendo recompensas (o penalizaciones). El objetivo es aprender una política que maximice la recompensa acumulada a lo largo del tiempo. El RL no requiere datos etiquetados, sino una función de recompensa bien definida. Algoritmos fundamentales: Q-Learning, Deep Q-Network (DQN), Proximal Policy Optimization (PPO), Soft Actor-Critic (SAC). Aplicaciones: juegos (AlphaGo, Atari), robótica, optimización de sistemas de recomendación, trading algorítmico y, más recientemente, la fase RLHF (Reinforcement Learning from Human Feedback) en el entrenamiento de modelos de lenguaje.

### 3.6 Tabla comparativa de paradigmas

| Paradigma | Datos requeridos | Señal de aprendizaje | Casos de uso típicos | Algoritmos de referencia |
|---|---|---|---|---|
| Supervisado — clasificación | Etiquetados con clases | Etiqueta discreta | Spam, diagnóstico, churn | Regresión logística, SVM, Random Forest, XGBoost, CNN |
| Supervisado — regresión | Etiquetados con valores | Valor continuo | Precios, predicción de demanda | Regresión lineal/Ridge/Lasso, Gradient Boosting, MLP |
| No supervisado — clustering | Sin etiquetar | Similitud intrínseca | Segmentación, exploración | K-Means, DBSCAN, GMM |
| No supervisado — reducción dim. | Sin etiquetar | Varianza / similitud | Visualización, compresión | PCA, t-SNE, UMAP, Autoencoder |
| No supervisado — anomalías | Sin etiquetar (mayoritariamente normal) | Desviación de la norma | Fraude, fallos industriales | Isolation Forest, LOF, One-Class SVM |
| Semi-supervisado | Pocos etiquetados + muchos sin etiquetar | Mixta | NLP con pocos ejemplos | Self-training, Label Propagation |
| Auto-supervisado | Sin etiquetar | Generada por el propio dato | Preentrenamiento LLM, visión | BERT, GPT, SimCLR, DINO |
| Por refuerzo | Interacción con entorno | Recompensa | Juegos, robótica, RLHF | DQN, PPO, SAC, A3C |

---

## 4. El teorema "No Free Lunch"

### 4.1 Enunciado formal

El teorema No Free Lunch (NFL), formulado por David Wolpert y William Macready en 1997, establece que, promediando sobre todos los posibles problemas de aprendizaje, todos los algoritmos de búsqueda y optimización tienen el mismo rendimiento esperado. De manera más precisa, si se integra el error de generalización de dos clasificadores cualesquiera $A$ y $B$ sobre el conjunto de todas las funciones objetivo posibles, ambas integrales son iguales.

Formalmente, sea $d_m$ el conjunto de pares de entrenamiento y $f$ la función objetivo desconocida. Para cualquier par de algoritmos $A$ y $B$:

$$\sum_f P(d_m | f, A) = \sum_f P(d_m | f, B)$$

Esto implica que no existe ningún algoritmo que sea universalmente superior a todos los demás en todos los problemas posibles. La superioridad de un algoritmo sobre otro siempre es relativa a un subconjunto de problemas.

### 4.2 Implicaciones prácticas

La consecuencia inmediata del teorema NFL es que no tiene sentido hablar de "el mejor algoritmo de machine learning" en términos absolutos. Toda comparación de algoritmos solo es válida bajo supuestos sobre el tipo de problema, la distribución de los datos y las métricas de evaluación elegidas.

Esto justifica la existencia de familias de algoritmos especializados: los modelos lineales son superiores cuando las relaciones en los datos son aproximadamente lineales; los árboles de decisión son más robustos con datos tabulares heterogéneos y relaciones no lineales; las redes neuronales convolucionales son imbatibles con datos con estructura espacial. La elección del algoritmo es, por tanto, una hipótesis sobre la naturaleza del problema.

Desde el punto de vista operativo, el teorema NFL subraya la importancia del análisis previo del problema y del sesgo inductivo: todo algoritmo incorpora supuestos implícitos sobre qué tipo de regularidad busca en los datos. Elegir bien esos supuestos —alinearlos con las características del problema real— es la competencia central de un data scientist.

El teorema también justifica la experimentación empírica: dado que no se puede demostrar a priori cuál es el mejor algoritmo para un problema específico, es necesario probar varios candidatos bajo condiciones controladas y comparar sus resultados de manera rigurosa.

---

## 5. Criterios de selección del algoritmo

La selección del algoritmo no es un acto de intuición ni una preferencia personal. Es el resultado de analizar sistemáticamente un conjunto de criterios objetivos. A continuación se desarrolla cada uno de ellos.

### 5.1 Cantidad y calidad de los datos disponibles

La cantidad de datos es el factor más determinante en la selección del paradigma y del algoritmo. Los modelos de alta capacidad —redes neuronales profundas, transformers— requieren grandes volúmenes de datos para generalizar; con pocos datos, sobreajustan de manera casi inevitable. En cambio, los modelos lineales y los métodos bayesianos ofrecen buenas garantías incluso con conjuntos de cientos o pocos miles de observaciones.

La calidad de los datos es igualmente crítica. Un dataset con muchas variables irrelevantes, valores faltantes sistemáticos o etiquetas ruidosas puede degradar el rendimiento de algoritmos potentes mientras que métodos más robustos al ruido —como Random Forest— mantienen un rendimiento razonable.

Regla práctica: con menos de 1 000 muestras, priorizar modelos simples con regularización fuerte. Entre 1 000 y 100 000, explorar ensembles basados en árboles. Por encima de 100 000, las redes neuronales profundas empiezan a ser competitivas; por encima de 1 000 000, suelen ser dominantes.

### 5.2 Dimensionalidad del espacio de características

La "maldición de la dimensionalidad" (Bellman, 1957) describe cómo, al aumentar el número de variables, el espacio crece exponencialmente y los datos disponibles se vuelven cada vez más dispersos. Esto afecta de manera diferente a distintos algoritmos.

Los algoritmos basados en distancias (K-NN, K-Means) se degradan rápidamente con la dimensionalidad porque las distancias euclidianas pierden significado en espacios de alta dimensión. Los modelos lineales con regularización (Lasso, Ridge) mantienen buen rendimiento con muchas variables. Las redes neuronales profundas son capaces de aprender representaciones internas que mitigar la maldición de la dimensionalidad, pero requieren más datos. Los árboles de decisión son inherentemente robustos porque seleccionan en cada nodo solo la variable más informativa.

Cuando la dimensionalidad es muy alta y la muestra es pequeña, una estrategia frecuente es reducir primero la dimensionalidad con PCA o selección de variables, y después entrenar el modelo final.

### 5.3 Tipo de variable objetivo

El tipo de la variable de salida determina en primer lugar si el problema es de regresión, clasificación, ranking u otro. Dentro de la clasificación, si el número de clases es binario (dos clases) o multiclase (más de dos) afecta la elección del algoritmo y la función de pérdida. Si las clases están muy desbalanceadas —por ejemplo, 99 % negativos y 1 % positivos en detección de fraude— se deben considerar técnicas de rebalanceo (SMOTE, class weighting) y métricas alternativas a la precisión global.

En tareas de regresión, la distribución de la variable objetivo importa: si tiene colas pesadas o valores extremos muy influyentes, pueden ser preferibles funciones de pérdida robustas como MAE o Huber Loss en lugar de MSE.

### 5.4 Requisitos de interpretabilidad

La regulación (GDPR en Europa, Directiva de IA de la UE) y los requisitos del negocio imponen a veces la necesidad de que el modelo pueda explicar sus decisiones. Esto establece una distinción fundamental entre modelos caja blanca y modelos caja negra.

**Modelos caja blanca.** Son intrínsecamente interpretables: regresión lineal, regresión logística, árboles de decisión (de profundidad limitada), Naive Bayes. Un analista sin formación técnica avanzada puede inspeccionar los coeficientes o el árbol y entender por qué el modelo tomó una decisión.

**Modelos caja negra.** Random Forest, Gradient Boosting, redes neuronales profundas. Su rendimiento suele ser superior, pero la lógica interna no es directamente legible. En estos casos, se pueden aplicar técnicas de explicabilidad post-hoc: SHAP (SHapley Additive exPlanations), LIME (Local Interpretable Model-agnostic Explanations) o análisis de importancia de variables.

En entornos de alto riesgo —crédito bancario, decisiones médicas, justicia penal— la regulación puede prohibir o desincentivar el uso de cajas negras, lo que convierte la interpretabilidad en un criterio eliminatorio.

### 5.5 Latencia de inferencia requerida

El tiempo que tarda el modelo en producir una predicción una vez recibe una entrada es la latencia de inferencia. Es un criterio crítico en aplicaciones en tiempo real: sistemas de recomendación que deben responder en milisegundos, detección de intrusiones en red, conducción autónoma.

Los modelos más simples (regresión logística, árboles de poca profundidad) ofrecen latencias extremadamente bajas. Los ensembles grandes (1 000 árboles en un Random Forest) son más lentos. Las redes neuronales profundas requieren hardware especializado (GPU) para lograr latencias competitivas. En entornos con restricciones de latencia muy estrictas, puede ser necesario comprimir el modelo (pruning, quantization, knowledge distillation) o seleccionar un algoritmo deliberadamente menos potente pero más rápido.

### 5.6 Coste computacional de entrenamiento

El presupuesto de compute disponible —horas de CPU/GPU, coste en la nube— limita la clase de modelos que pueden considerarse. Entrenar un transformer grande puede costar millones de euros en hardware; entrenar una regresión logística sobre el mismo dataset puede tomar segundos.

Este criterio también afecta a la iterabilidad: si el ciclo de entrenamiento es de horas, la experimentación es lenta y cara. Si es de segundos, se pueden explorar cientos de configuraciones. En proyectos con restricciones de tiempo o presupuesto, priorizar algoritmos con ciclos de entrenamiento rápidos permite más iteraciones y, en la práctica, suele llevar a mejores resultados que elegir el algoritmo más potente pero que solo se puede entrenar una o dos veces.

### 5.7 Escalabilidad

El modelo debe poder reentrenarse periódicamente a medida que llegan nuevos datos. Algunos algoritmos escalan bien con el volumen de datos (SGD, mini-batch learning, modelos online); otros requieren acceso completo al dataset en cada reentrenamiento. Para pipelines de producción con datos en streaming o con reentrenamiento diario sobre grandes volúmenes, esta consideración puede ser determinante.

---

## 6. Familias de algoritmos: comparativa técnica

### 6.1 Modelos lineales

**Regresión logística.** A pesar de su nombre, es un clasificador. Modela la probabilidad de pertenencia a la clase positiva como una función sigmoide de una combinación lineal de las variables. Es interpretable (los coeficientes tienen lectura directa en términos de log-odds), rápida de entrenar e inferir, y funciona bien cuando las clases son linealmente separables o aproximadamente así. Con regularización L1 (Lasso) produce modelos dispersos y actúa como selector de variables.

**Máquinas de vectores de soporte (SVM).** Buscan el hiperplano de margen máximo que separa las clases. Con el kernel trick pueden aprender fronteras de decisión no lineales en el espacio de características transformado. Son especialmente potentes en espacios de alta dimensión y cuando el número de muestras es moderado. Su principal limitación es la escalabilidad: el tiempo de entrenamiento crece cuadráticamente (o peor) con el número de muestras.

### 6.2 Árboles de decisión y ensembles

**Árbol de decisión simple.** Divide recursivamente el espacio de características mediante reglas del tipo "si variable $X_j > \theta$ entonces...". Es el modelo más interpretable de este grupo, pero tiene alta varianza: pequeñas perturbaciones en el dataset producen árboles muy diferentes. Solo se recomienda para exploración o cuando la interpretabilidad es el único criterio.

**Random Forest.** Ensemble de árboles de decisión entrenados sobre submuestras aleatorias del dataset y subconjuntos aleatorios de las variables (bagging + feature randomness). La media de las predicciones reduce la varianza sin aumentar el sesgo. Es robusto al ruido, maneja bien variables irrelevantes, requiere poco preprocesamiento y ofrece estimaciones de importancia de variables. Es el modelo tabulares de referencia para conjuntos de datos de tamaño medio.

**Gradient Boosting (XGBoost, LightGBM, CatBoost).** Ensemble aditivo donde cada árbol corrige los errores del anterior. Algorítmicamente más complejo que Random Forest pero generalmente más preciso en datos tabulares competitivos. XGBoost (Chen y Guestrin, 2016) introdujo regularización y optimizaciones de velocidad que lo convirtieron en el dominador de las competiciones de Kaggle durante años. LightGBM (Microsoft, 2017) usa una estrategia de crecimiento hoja a hoja que lo hace significativamente más rápido para grandes datasets. CatBoost (Yandex, 2018) maneja variables categóricas de forma nativa sin necesidad de one-hot encoding.

### 6.3 Redes neuronales

**Perceptrón multicapa (MLP).** Red neuronal feed-forward densa. Aprende representaciones no lineales mediante capas ocultas con funciones de activación (ReLU, tanh, sigmoid). Es el bloque básico del deep learning; su rendimiento mejora notablemente con más datos y más capacidad (capas/neuronas).

**Redes convolucionales (CNN).** Diseñadas para datos con estructura espacial (imágenes, señales 1D). Las capas de convolución aprenden filtros locales que se aplican de manera equivariante a lo largo de la entrada. Son el estado del arte en visión por computador para tareas de clasificación, detección y segmentación.

**Redes recurrentes (RNN, LSTM, GRU).** Diseñadas para secuencias. Mantienen un estado oculto que se propaga en el tiempo, permitiendo capturar dependencias temporales. Los modelos LSTM y GRU resuelven el problema del gradiente evanescente de las RNN simples. Aunque en muchas tareas de secuencias han sido superados por los Transformers, siguen siendo útiles en entornos con restricciones de recursos.

**Transformers.** Basados en el mecanismo de atención (Vaswani et al., 2017, "Attention Is All You Need"), los transformers procesan secuencias en paralelo y capturan dependencias de largo alcance de manera eficiente. Son la arquitectura dominante en procesamiento del lenguaje natural (BERT, GPT, T5) y ganan terreno en visión (Vision Transformer, ViT) y otros dominios. Su principal desventaja es el coste cuadrático de la atención respecto a la longitud de la secuencia.

### 6.4 Tabla comparativa de familias de algoritmos

| Familia | Cuándo usar | Ventajas | Limitaciones | Coste computacional |
|---|---|---|---|---|
| Regresión logística / lineal | Datos linealmente separables, alta interpretabilidad exigida, muchas variables con Lasso | Muy rápida, interpretable, escalable | No captura relaciones no lineales complejas | Muy bajo |
| SVM | Alta dimensionalidad, pocos datos, margen de separación claro | Eficaz en alta dimensión, versátil con kernels | Escala mal con N grande, sensible a la escala | Medio (bajo en prod.) |
| Árbol de decisión | Exploración, reglas de negocio, interpretabilidad máxima | Totalmente interpretable, no requiere preprocesamiento | Alta varianza, propenso al sobreajuste | Muy bajo |
| Random Forest | Datos tabulares de tamaño medio, robustez al ruido, baseline de calidad | Robusto, importancia de variables, poco preprocesamiento | Más lento que modelos lineales, menos que GB | Medio |
| Gradient Boosting (XGB / LGBM / CatBoost) | Máximo rendimiento en datos tabulares, competiciones, producción | State-of-the-art en tabular, maneja nulos y categorías (CatBoost) | Sensible a hiperparámetros, sobreajusta con pocos datos | Medio-alto |
| MLP | Datos tabulares grandes, tareas genéricas, feature learning | Flexible, mejora con datos | Necesita mucho dato, costoso de ajustar | Alto |
| CNN | Imágenes, audio, señales con estructura espacial | Estado del arte en visión | Requiere muchos datos o transfer learning | Alto (GPU recomendado) |
| RNN / LSTM / GRU | Series temporales, NLP con secuencias cortas, recursos limitados | Captura dependencias temporales, eficiente | Problemas de gradiente, superado por Transformers | Medio-alto |
| Transformers | NLP, visión de gran escala, preentrenamiento + fine-tuning | Máximo rendimiento, transferible | Muy costoso de entrenar desde cero, memoria O(n²) | Muy alto (GPU/TPU) |

---

## 7. Análisis de requisitos del caso de uso

### 7.1 Metodología

El análisis de requisitos de un caso de uso de ML sigue una secuencia de pasos que van desde la comprensión del problema de negocio hasta la decisión sobre la estrategia de entrenamiento. Este proceso evita el error de tratar el problema como un ejercicio técnico descontextualizado.

**Paso 1: Definir el objetivo de negocio.** Antes de hablar de ML, hay que entender qué decisión o acción quiere mejorar la organización y cuál es el valor de mejorarla. La métrica de negocio (reducción del churn, tasa de aprobación de créditos, fallos detectados antes de parar la línea) debe preceder a la métrica de modelo (F1, AUC, RMSE).

**Paso 2: Formular el problema de ML.** Traducir el objetivo de negocio en un problema de ML bien definido: ¿cuál es la variable objetivo? ¿Es un problema de clasificación, regresión, clustering, ranking? ¿Con qué granularidad (por usuario, por transacción, por día)?

**Paso 3: Inventariar los datos disponibles.** Identificar qué datos existen, su volumen, su calidad, su antigüedad y su accesibilidad. Determinar si hay etiquetas disponibles y cuánto cuesta obtenerlas.

**Paso 4: Identificar restricciones del sistema.** Latencia requerida en inferencia, frecuencia de reentrenamiento, presupuesto de compute, requisitos de interpretabilidad, restricciones regulatorias.

**Paso 5: Seleccionar el paradigma y la familia de algoritmos.** Con la información de los pasos anteriores, aplicar los criterios del apartado 5 para acotar el espacio de opciones.

**Paso 6: Definir el baseline y el protocolo de evaluación.** Antes de entrenar el primer modelo "real", definir qué métrica se usará para evaluar y establecer un modelo baseline (véase apartado 8).

### 7.2 Ejemplo completo: sistema de detección de fraude en tarjetas de crédito

**Contexto:** Una entidad bancaria detecta transacciones fraudulentas manualmente. El equipo de fraude revisa alertas generadas por reglas heurísticas. El objetivo es automatizar la detección para priorizar la revisión manual y reducir las pérdidas.

**Paso 1 — Objetivo de negocio.** Reducir las pérdidas por fraude en un 30 % en 6 meses sin aumentar el número de falsos positivos (transacciones legítimas bloqueadas) más de un 5 %, porque los falsos positivos generan fricción con clientes y tienen coste operativo.

**Paso 2 — Formulación del problema.** Clasificación binaria: dado un vector de características de una transacción (importe, comercio, hora, dispositivo, historial del usuario), predecir si es fraudulenta (1) o legítima (0). La variable objetivo ya existe en el sistema de backoffice. El problema es de clasificación binaria con clases muy desbalanceadas: aproximadamente 0.1 % de transacciones son fraudulentas.

**Paso 3 — Inventario de datos.** Se dispone de 24 meses de histórico: 50 millones de transacciones, de las cuales unas 50 000 están etiquetadas como fraude. Las variables disponibles incluyen 30 características numéricas ya anonimizadas (PCA aplicado por privacidad), importe y tiempo. La calidad es alta: sin valores faltantes sistemáticos.

**Paso 4 — Restricciones del sistema.** La inferencia debe realizarse en tiempo real, con latencia inferior a 100 ms por transacción. El modelo debe poder reexplicar decisiones ante reclamaciones de clientes (interpretabilidad parcial exigida por regulación). Reentrenamiento mensual. Presupuesto de compute: moderado (no hay GPUs en producción para inferencia).

**Paso 5 — Selección de estrategia.**
- Paradigma: supervisado, clasificación binaria.
- Desbalanceo: se usará class weighting o SMOTE en el preprocessing.
- Interpretabilidad: se requiere explicar casos individuales, pero no es necesario que el modelo sea intrínsecamente interpretable. Se puede usar SHAP sobre un modelo de caja negra.
- Latencia: modelos de árbol son adecuados; las redes neuronales requerirían GPU para cumplir el SLA, lo que se descarta.
- Candidatos seleccionados: LightGBM (primera opción por rendimiento y velocidad), Random Forest (alternativa más simple), regresión logística (baseline).

**Paso 6 — Baseline y protocolo.** Baseline: regresión logística con variables estandarizadas. Métrica principal: AUC-ROC y recall en el top 5 % de alertas (la métrica de negocio real). Validación temporal (train en primeros 20 meses, validación en meses 21-22, test en meses 23-24) para respetar la estructura temporal de los datos.

**Resultado del análisis:** Se procede con LightGBM como modelo principal, SHAP para explicabilidad individual, validación temporal, y class weighting para gestionar el desbalanceo. La complejidad añadida de una red neuronal no está justificada por las restricciones de latencia e interpretabilidad.

---

## 8. Baseline models y experimentación iterativa

### 8.1 Por qué empezar simple

Uno de los principios más sólidos en la práctica del machine learning es establecer siempre un modelo baseline antes de explorar alternativas más complejas. Un baseline es el modelo más simple razonable para el problema, y sirve como punto de referencia para medir el valor real que aporta cada incremento de complejidad.

La justificación es doble. Primero, práctica: un baseline se implementa en minutos, mientras que un modelo complejo puede requerir días de ingeniería. Si el baseline ya alcanza el umbral de rendimiento necesario para el negocio, no hay razón para ir más lejos. Segundo, epistemológica: sin un baseline, cualquier número de rendimiento parece bueno o malo sin contexto. Con un baseline, se puede cuantificar exactamente cuánto valor añade cada decisión de modelado.

### 8.2 Qué usar como baseline

La elección del baseline depende del tipo de problema:

- **Clasificación:** regresión logística con variables sin transformar (o ZeroR, que predice siempre la clase mayoritaria, como referencia inferior).
- **Regresión:** media de la variable objetivo en entrenamiento; o regresión lineal simple.
- **Series temporales:** el valor del periodo anterior (naive forecast) o la media móvil.
- **Ranking / recomendación:** recomendar siempre los ítems más populares.
- **NLP:** bolsa de palabras (TF-IDF) + regresión logística.

### 8.3 El ciclo de experimentación iterativa

Una vez establecido el baseline, la mejora del modelo sigue un ciclo iterativo:

1. **Identificar el cuello de botella.** Analizar si el error es principalmente de sesgo (underfitting: el modelo es demasiado simple) o de varianza (overfitting: el modelo memoriza el entrenamiento pero no generaliza). Esta distinción orienta la siguiente acción.
2. **Formular una hipótesis de mejora.** Por ejemplo: "añadir más variables de contexto debería reducir el sesgo" o "aplicar regularización más fuerte debería reducir la varianza".
3. **Implementar el cambio mínimo.** Cambiar solo una cosa a la vez para poder atribuir el cambio de rendimiento a la modificación realizada.
4. **Medir con el protocolo fijo.** Siempre usando las mismas particiones de validación y las mismas métricas definidas en el paso 6 del análisis de requisitos. Cambiar el protocolo de evaluación entre experimentos invalida las comparaciones.
5. **Decidir si el cambio es una mejora.** Si es así, se incorpora como nueva baseline. Si no, se descarta.
6. **Repetir** hasta alcanzar el rendimiento objetivo o el límite de recursos.

Este ciclo evita el "saltar al modelo más potente" y garantiza que cada decisión de complejidad está justificada por evidencia empírica.

### 8.4 MLflow y seguimiento de experimentos

En un proyecto real, la experimentación iterativa requiere registro sistemático de cada experimento: qué configuración se usó, qué datos, qué resultado se obtuvo. MLflow es la herramienta de código abierto estándar para este propósito. Permite registrar parámetros, métricas, artefactos y versiones del modelo en cada ejecución, y comparar experimentos visualmente.

---

## 9. Actividades prácticas propuestas

### Actividad 1 — Clasificación de problemas

**Objetivo:** Aplicar la taxonomía del apartado 3 a casos de uso reales.

**Descripción:** Se proporciona una lista de 10 casos de uso de ML descritos en lenguaje de negocio (predicción de abandono de clientes, detección de defectos en imágenes de producción, agrupación de artículos de un catálogo, etc.). El estudiante debe clasificar cada uno en el paradigma de aprendizaje correspondiente, justificar la elección, identificar la variable objetivo cuando existe, y proponer tres algoritmos candidatos con justificación.

**Entregable:** Documento de una página por caso de uso con la clasificación razonada.

### Actividad 2 — Análisis comparativo con scikit-learn

**Objetivo:** Comparar empíricamente el rendimiento de al menos cuatro algoritmos sobre el mismo dataset.

**Descripción:** Usando el dataset de clasificación `breast_cancer` de scikit-learn (569 muestras, 30 variables, clasificación binaria), el estudiante debe implementar, en un notebook de Jupyter: regresión logística, árbol de decisión, Random Forest y SVM. Para cada modelo: entrenar con los mismos datos de entrenamiento, evaluar en el mismo conjunto de test con validación cruzada estratificada (5-fold), registrar F1-score, AUC-ROC y tiempo de entrenamiento. Incluir un análisis de las diferencias observadas a la luz de los criterios del apartado 5.

**Entregable:** Notebook documentado con conclusiones de 300 palabras.

### Actividad 3 — Caso de uso completo: análisis de requisitos

**Objetivo:** Aplicar la metodología del apartado 7 a un problema propuesto por el estudiante o proporcionado por el instructor.

**Descripción:** Cada estudiante o grupo selecciona un caso de uso real (o semificticio pero plausible) de un sector de su interés (salud, finanzas, retail, industria, medioambiente). Aplica la metodología de los seis pasos del apartado 7.1, produciendo un documento de análisis que incluya: descripción del problema de negocio, formulación como problema de ML, inventario de datos (real o estimado), restricciones del sistema, selección razonada de la estrategia (paradigma + familia de algoritmos) y definición del baseline y protocolo de evaluación.

**Entregable:** Informe de análisis (1 500–2 000 palabras) + presentación de 5 minutos en clase.

### Actividad 4 — Baseline vs. modelo avanzado: ¿vale la pena la complejidad?

**Objetivo:** Cuantificar empíricamente el valor añadido por la complejidad del modelo.

**Descripción:** Usando el dataset `california_housing` (regresión) o `adult income` (clasificación) disponibles en OpenML, el estudiante implementa un pipeline de tres modelos en orden creciente de complejidad: (1) baseline simple (media de la variable objetivo o regresión logística), (2) Random Forest con hiperparámetros por defecto, (3) LightGBM con búsqueda básica de hiperparámetros. Para cada modelo se registra el rendimiento en validación y el tiempo de entrenamiento. El estudiante debe calcular el "coste marginal de complejidad": cuánta mejora en métrica se obtiene por cada orden de magnitud adicional en tiempo de entrenamiento.

**Entregable:** Notebook con análisis cuantitativo y recomendación razonada sobre qué modelo usaría en producción y por qué.

---

## 10. Referencias

Bishop, C. M. (2006). *Pattern Recognition and Machine Learning*. Springer. Referencia estándar en ML probabilístico; los capítulos 1, 3 y 4 cubren fundamentos de inferencia bayesiana, modelos lineales y clasificación. Disponible parcialmente en: https://www.microsoft.com/en-us/research/people/cmbishop/prml-book/

Hastie, T., Tibshirani, R., y Friedman, J. (2009). *The Elements of Statistical Learning: Data Mining, Inference, and Prediction* (2.ª ed.). Springer. Tratamiento matemático riguroso de supervisado, ensembles y modelos no paramétricos. Disponible en abierto: https://hastie.su.domains/ElemStatLearn/

Géron, A. (2022). *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow* (3.ª ed.). O'Reilly Media. Referencia práctica imprescindible; cubre desde regresión logística hasta transformers con código en Python. https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/

Scikit-learn Development Team. (2024). *scikit-learn: Machine Learning in Python — User Guide*. Documentación oficial con descripción de algoritmos, parámetros y guías de uso. https://scikit-learn.org/stable/user_guide.html

Wolpert, D. H., y Macready, W. G. (1997). No free lunch theorems for optimization. *IEEE Transactions on Evolutionary Computation*, 1(1), 67–82. Paper fundacional del teorema NFL. https://doi.org/10.1109/4235.585893

Chen, T., y Guestrin, C. (2016). XGBoost: A scalable tree boosting system. En *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785–794). Paper fundacional de XGBoost. https://arxiv.org/abs/1603.02754

Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., y Liu, T.-Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. En *Advances in Neural Information Processing Systems* (Vol. 30). Paper fundacional de LightGBM. https://papers.nips.cc/paper_files/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., y Polosukhin, I. (2017). Attention is all you need. En *Advances in Neural Information Processing Systems* (Vol. 30). Paper fundacional de la arquitectura Transformer. https://arxiv.org/abs/1706.03762

Lundberg, S. M., y Lee, S.-I. (2017). A unified approach to interpreting model predictions. En *Advances in Neural Information Processing Systems* (Vol. 30). Paper fundacional de SHAP. https://arxiv.org/abs/1705.07874

Prokhorenkova, L., Gusev, G., Veronika, A., Dorogush, A. V., y Gulin, A. (2018). CatBoost: Unbiased boosting with categorical features. En *Advances in Neural Information Processing Systems* (Vol. 31). Paper fundacional de CatBoost. https://arxiv.org/abs/1706.09516

---

*Documento elaborado para el Ciclo de Formación Superior en Gestión de Datos e Inteligencia Artificial · IFC · Versión 1.0 · Junio 2026*
