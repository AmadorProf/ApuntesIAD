# UD6 · Trabajo responsable, sostenible y PRL en entrenamiento de modelos

**Módulo:** MP02 — Entrenamiento de Modelos  
**Ciclo:** CFS1 — Gestión de datos y entrenamiento IA  
**Duración estimada:** 12 horas lectivas

---

## 1. Introducción — responsabilidad en el entrenamiento: más allá de la exactitud del modelo

Durante décadas, el criterio dominante para evaluar un modelo de aprendizaje automático fue la exactitud: ¿cuántas predicciones acertó el modelo sobre el conjunto de prueba? Esta métrica, aunque necesaria, es profundamente insuficiente. Un modelo puede alcanzar un 95% de exactitud global y al mismo tiempo cometer errores sistemáticos sobre colectivos minoritarios, consumir la misma energía eléctrica que varios hogares durante semanas, o haber sido construido por equipos que trabajaron en condiciones de presión extrema sin protección laboral adecuada.

La responsabilidad en el entrenamiento de modelos de inteligencia artificial abarca tres dimensiones que este módulo trata de forma integrada. La primera es ética y técnica: los modelos deben tratar a todas las personas con equidad, y esa equidad debe medirse, auditarse y, cuando sea posible, corregirse desde el propio proceso de entrenamiento. La segunda es ambiental: el entrenamiento de modelos de gran escala tiene una huella de carbono real y creciente, y los profesionales del sector tienen la responsabilidad de conocer ese impacto y aplicar estrategias para reducirlo. La tercera es laboral: quien entrena modelos es también un trabajador expuesto a riesgos específicos que el marco legal reconoce y que las organizaciones están obligadas a gestionar.

Este enfoque integrado no es una moda ni un añadido cosmético al currículo técnico. Es el reflejo de cómo el mercado laboral, el marco regulatorio europeo y la comunidad científica están redefiniendo qué significa hacer bien el trabajo de entrenar un modelo. Un técnico que sepa ajustar hiperparámetros pero ignore las implicaciones de fairness de su umbral de decisión, o que desconozca lo que cuesta en kilovatios-hora un entrenamiento con H100, o que no conozca sus derechos en materia de prevención de riesgos laborales, es un técnico con formación incompleta.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad didáctica, el alumnado será capaz de:

- Definir y distinguir las principales métricas de fairness utilizadas en la evaluación de modelos de aprendizaje automático: disparate impact, equalized odds y demographic parity.
- Identificar las tensiones entre métricas de equidad e interpretar por qué es matemáticamente imposible satisfacerlas todas simultáneamente en la mayoría de escenarios reales.
- Aplicar la biblioteca Fairlearn de Microsoft para detectar y mitigar sesgos durante el entrenamiento mediante el algoritmo `ExponentiatedGradient`.
- Utilizar AI Fairness 360 de IBM como herramienta de auditoría de equidad.
- Interpretar valores SHAP desagregados por subgrupos demográficos como método de interpretabilidad orientada a la equidad.
- Estimar el consumo energético de un entrenamiento con GPUs de referencia (H100, A100, RTX) y contextualizar ese consumo con los datos publicados por Strubell et al. (2019).
- Instalar y utilizar CodeCarbon para medir y reportar las emisiones de CO2 de un proceso de entrenamiento.
- Distinguir entre la filosofía Green AI y Red AI según Schwartz et al. (2020) y aplicar estrategias concretas de reducción del impacto ambiental.
- Reconocer los mecanismos por los cuales el entrenamiento amplifica sesgos presentes en el dataset y aplicar técnicas de mitigación como SMOTE, `class_weight` y ajuste del umbral de decisión.
- Identificar los riesgos laborales específicos del trabajo con computación intensiva y conocer el marco legal aplicable en España según la Ley 31/1995 de Prevención de Riesgos Laborales.
- Comprender las obligaciones que el EU AI Act impone sobre los datos de entrenamiento y la responsabilidad legal del modelo producido.

---

## 3. Fairness y equidad en modelos

### 3.1 Por qué la exactitud global no es suficiente

Cuando se entrena un modelo sobre datos que reflejan desigualdades históricas, el modelo puede aprender esas desigualdades y reproducirlas a escala. El problema no es la intención del equipo de desarrollo, sino la naturaleza del aprendizaje supervisado: el modelo optimiza una función de pérdida sobre el conjunto de entrenamiento, y si ese conjunto contiene patrones discriminatorios, el modelo los captura.

Un caso ilustrativo es el del sistema COMPAS, utilizado en Estados Unidos para predecir reincidencia criminal. Investigaciones periodísticas y académicas mostraron que el sistema cometía errores a tasas diferentes según la raza del acusado, con una sobreestimación del riesgo para personas negras y una subestimación para personas blancas. El modelo era razonablemente exacto en términos globales, pero su comportamiento diferencial por subgrupos lo convertía en un instrumento de refuerzo de desigualdades estructurales.

### 3.2 Métricas de fairness

**Disparate impact** (impacto dispar) compara la tasa de resultados positivos entre el grupo privilegiado y el grupo protegido. Se calcula como el cociente entre la tasa de predicciones positivas del grupo protegido y la del grupo privilegiado:

```
DI = P(Ŷ=1 | A=0) / P(Ŷ=1 | A=1)
```

Un valor inferior a 0,8 se considera, según la regla del 80% de la EEOC estadounidense, evidencia de discriminación. Esta métrica es independiente de la etiqueta real: mide únicamente la distribución de las predicciones.

**Demographic parity** (paridad demográfica) exige que la probabilidad de recibir una predicción positiva sea igual para todos los grupos demográficos considerados, independientemente de la etiqueta real:

```
P(Ŷ=1 | A=0) = P(Ŷ=1 | A=1)
```

Es la formalización estadística del disparate impact. Esta métrica es apropiada cuando el objetivo es garantizar una distribución equitativa de oportunidades, por ejemplo en sistemas de selección de currículos.

**Equalized odds** (igualdad de oportunidades ajustada) exige que tanto la tasa de verdaderos positivos (sensibilidad) como la tasa de falsos positivos sean iguales entre grupos:

```
P(Ŷ=1 | Y=1, A=0) = P(Ŷ=1 | Y=1, A=1)   [igualdad de TPR]
P(Ŷ=1 | Y=0, A=0) = P(Ŷ=1 | Y=0, A=1)   [igualdad de FPR]
```

Es más exigente que la paridad demográfica porque tiene en cuenta la etiqueta real. Es la métrica más apropiada cuando la exactitud por subgrupo importa tanto como la distribución de predicciones.

### 3.3 Tensiones entre métricas

Chouldechova (2017) y Kleinberg et al. (2016) demostraron formalmente que, salvo en condiciones muy restrictivas, es matemáticamente imposible satisfacer simultáneamente demographic parity, equalized odds y calibración perfecta cuando las tasas de prevalencia difieren entre grupos. Esto tiene consecuencias prácticas importantes: elegir una métrica de fairness es una decisión de valor, no solo técnica. El equipo debe explicitar qué tipo de equidad prioriza y por qué, y esa decisión debe documentarse y comunicarse a los responsables del sistema.

### 3.4 Fairlearn de Microsoft

Fairlearn es una biblioteca de Python de código abierto desarrollada por Microsoft Research que proporciona herramientas tanto para evaluar como para mitigar la inequidad en modelos de clasificación y regresión.

```bash
pip install fairlearn
```

El algoritmo central para la mitigación es `ExponentiatedGradient`, que reencuadra el problema de equidad como un problema de optimización restringida. En lugar de entrenar el modelo para minimizar únicamente la pérdida, el algoritmo penaliza las violaciones de la restricción de equidad especificada:

```python
from fairlearn.reductions import ExponentiatedGradient, EqualizedOdds
from sklearn.linear_model import LogisticRegression

estimator = LogisticRegression()
mitigator = ExponentiatedGradient(estimator, EqualizedOdds())
mitigator.fit(X_train, y_train, sensitive_features=A_train)
y_pred = mitigator.predict(X_test, sensitive_features=A_test)
```

Donde `A_train` y `A_test` son las columnas de atributo sensible (por ejemplo, género o grupo étnico). El algoritmo genera internamente un ensemble de clasificadores ponderados que minimizan la pérdida sujeta a la restricción de equidad.

Fairlearn también incluye el `MetricFrame`, una estructura de evaluación que desagrega automáticamente las métricas de rendimiento por subgrupo, permitiendo identificar discrepancias que el rendimiento global oculta.

### 3.5 AI Fairness 360 de IBM

AI Fairness 360 (AIF360) es un toolkit de código abierto publicado por IBM Research que ofrece más de 70 métricas de fairness y más de 10 algoritmos de mitigación, organizados en tres etapas del pipeline:

- **Pre-procesamiento:** técnicas que modifican los datos de entrenamiento antes de ajustar el modelo. Ejemplos: `Reweighing` (reasignar pesos a las instancias) y `DisparateImpactRemover`.
- **En el proceso de entrenamiento:** algoritmos que modifican el propio proceso de optimización. Ejemplo: `PrejudiceRemover`.
- **Post-procesamiento:** técnicas que ajustan las predicciones del modelo ya entrenado. Ejemplo: `EqOddsPostprocessing`, que remapea las salidas del clasificador para equilibrar las tasas de error.

La filosofía de AIF360 es complementaria a Fairlearn: mientras Fairlearn se enfoca en una integración fluida con scikit-learn y en la facilidad de uso en entornos de producción, AIF360 ofrece mayor variedad de algoritmos y una suite de evaluación más extensa.

### 3.6 SHAP por subgrupos para interpretabilidad de equidad

SHAP (SHapley Additive exPlanations) es un método de interpretabilidad post-hoc basado en la teoría de juegos cooperativos. Asigna a cada característica del modelo una contribución marginal al valor de predicción de cada instancia.

Cuando se desagrega el análisis SHAP por subgrupos demográficos, se obtiene información valiosa sobre la equidad: si una característica tiene un valor SHAP alto y positivo para predicciones favorables en un grupo pero bajo o negativo en otro, indica que el modelo está utilizando esa característica de forma diferente según el grupo, lo que puede señalar una fuente de sesgo.

```python
import shap

explainer = shap.TreeExplainer(modelo)
shap_values = explainer.shap_values(X_test)

# Subgrupo de análisis
idx_grupo_protegido = X_test[A_test == "grupo_protegido"].index
shap.summary_plot(shap_values[idx_grupo_protegido], X_test.loc[idx_grupo_protegido])
```

Este análisis permite no solo detectar que el modelo es injusto, sino identificar qué variables son responsables de esa injusticia, lo que orienta las decisiones de corrección.

---

## 4. Impacto ambiental del entrenamiento

### 4.1 El coste energético del entrenamiento a escala

El entrenamiento de modelos de aprendizaje profundo requiere mantener GPUs funcionando a plena carga durante periodos prolongados. El consumo energético de las GPUs más comunes en entornos de producción es el siguiente:

- **NVIDIA H100 SXM5:** consumo máximo de 700 W (0,7 kWh por hora de uso sostenido).
- **NVIDIA A100 SXM4:** consumo máximo de 400 W (0,4 kWh por hora).
- **NVIDIA RTX 4090 (entorno prosumer):** consumo máximo de 450 W (0,45 kWh por hora).

Un entrenamiento típico de un modelo de lenguaje de tamaño mediano puede requerir cientos de GPUs durante días o semanas. Con un cluster de 512 A100, el consumo eléctrico alcanza los 204,8 kWh por hora, o aproximadamente 4.900 kWh por día. La intensidad de carbono depende del mix energético del país o región donde se ejecute el cómputo.

### 4.2 Strubell et al. 2019: cifras que cambiaron el debate

El paper "Energy and Policy Considerations for Deep Learning in NLP", publicado por Emma Strubell, Ananya Ganesh y Andrew McCallum en ACL 2019, fue el primero en cuantificar de forma sistemática el coste ambiental del entrenamiento de modelos de procesamiento de lenguaje natural.

Las cifras más citadas del paper son:

- El entrenamiento de un modelo Transformer grande con búsqueda de hiperparámetros puede emitir aproximadamente **284 toneladas de CO2 equivalente**, comparable a las emisiones de cinco automóviles a gasolina durante toda su vida útil.
- El entrenamiento del modelo BERT base en GPU requirió aproximadamente **79 horas** con un coste estimado de entre 3.000 y 12.000 dólares en infraestructura en la nube.
- El coste de la búsqueda de arquitectura neuronal (NAS) para algunos modelos es significativamente mayor que el entrenamiento final.

El paper también señalaba una asimetría importante: los grandes laboratorios con infraestructura propia pueden amortizar estos costes, pero las universidades y grupos de investigación con menos recursos no pueden replicar o competir con esos experimentos, lo que concentra el avance en pocas organizaciones.

### 4.3 CodeCarbon: medición de emisiones en Python

CodeCarbon es una biblioteca de Python que permite estimar las emisiones de CO2 de cualquier proceso de cómputo, basándose en el consumo de CPU y GPU y en la intensidad de carbono del mix eléctrico de la región donde se ejecuta el código.

**Instalación:**

```bash
pip install codecarbon
```

**Uso con decorador:**

```python
from codecarbon import track_emissions

@track_emissions(project_name="entrenamiento_clasificador", output_dir="./emisiones")
def entrenar_modelo():
    modelo.fit(X_train, y_train)
    return modelo
```

Al finalizar la función decorada, CodeCarbon genera un archivo CSV con los campos: `timestamp`, `project_name`, `duration` (en segundos), `emissions` (kg CO2), `energy_consumed` (kWh), `country_name`, `region`, `cpu_power`, `gpu_power`, entre otros.

**Uso con gestor de contexto (más flexible):**

```python
from codecarbon import EmissionsTracker

tracker = EmissionsTracker()
tracker.start()

modelo.fit(X_train, y_train)

emissions = tracker.stop()
print(f"Emisiones estimadas: {emissions:.4f} kg CO2")
```

CodeCarbon detecta automáticamente la GPU disponible mediante `pynvml` y obtiene la intensidad de carbono regional de la API de Electricity Maps o de tablas estáticas cuando no hay conexión disponible.

### 4.4 Green AI vs Red AI

Schwartz et al. (2020) acuñaron los términos **Red AI** y **Green AI** para caracterizar dos tendencias en la investigación de inteligencia artificial:

**Red AI** denomina la tendencia a alcanzar resultados de estado del arte mediante el incremento masivo de recursos computacionales. El progreso se mide exclusivamente por métricas de rendimiento (exactitud, F1, BLEU) sin considerar el coste computacional. Esta tendencia beneficia a quienes disponen de los mayores presupuestos de infraestructura y excluye progresivamente a la investigación académica independiente.

**Green AI** propone una reorientación donde la eficiencia computacional se incorpore como criterio de evaluación, junto al rendimiento. Schwartz et al. proponen que los papers de investigación reporten el número de operaciones de punto flotante (FLOPs), el tiempo de entrenamiento, el número de parámetros del modelo y el coste económico estimado, de modo que la comunidad pueda evaluar los avances en términos de la relación entre rendimiento y recursos consumidos.

### 4.5 Estrategias de reducción del impacto ambiental

**Early stopping:** detener el entrenamiento cuando la métrica de validación deja de mejorar durante un número determinado de épocas (`patience`). Evita épocas innecesarias que no aportan mejora pero consumen energía. La mayoría de frameworks de entrenamiento moderno incluyen callbacks de early stopping:

```python
from tensorflow.keras.callbacks import EarlyStopping

callback = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
modelo.fit(X_train, y_train, callbacks=[callback], epochs=200)
```

**Knowledge distillation (destilación de conocimiento):** técnica propuesta por Hinton et al. (2015) en la que un modelo pequeño (estudiante) se entrena para reproducir el comportamiento de un modelo grande ya entrenado (profesor), en lugar de aprender directamente de las etiquetas del dataset. El modelo estudiante puede alcanzar un rendimiento cercano al del profesor con una fracción de sus parámetros, reduciendo significativamente el coste de inferencia y de futuros reentrenamientos.

**Modelos más pequeños y arquitecturas eficientes:** el movimiento de modelos eficientes (EfficientNet, DistilBERT, TinyBERT, MobileNet) demuestra que es posible obtener rendimiento competitivo con modelos significativamente más pequeños. DistilBERT, por ejemplo, conserva el 97% del rendimiento de BERT en benchmarks de comprensión del lenguaje con el 60% de sus parámetros y un 40% menos de tiempo de inferencia.

**Selección de región de cómputo:** al elegir un proveedor de cloud, la intensidad de carbono de la región importa tanto como el precio. Francia (alta proporción nuclear) tiene una intensidad de carbono de aproximadamente 60 g CO2/kWh, mientras que Polonia (alta dependencia del carbón) puede superar los 700 g CO2/kWh. La misma carga de trabajo puede tener un impacto ambiental diez veces mayor dependiendo de dónde se ejecute.

---

## 5. Sesgos introducidos durante el entrenamiento

### 5.1 Desequilibrio de clases

El desequilibrio de clases es una de las fuentes más comunes de sesgo en clasificadores supervisados. Cuando una clase representa el 5% de las instancias y la otra el 95%, un clasificador que predice siempre la clase mayoritaria obtiene un 95% de exactitud sin haber aprendido nada útil. Más problemático aún, la función de pérdida estándar (entropía cruzada, error cuadrático medio) trata todos los ejemplos por igual, por lo que el modelo aprende a optimizar el rendimiento sobre la clase mayoritaria a costa de la minoritaria.

**SMOTE (Synthetic Minority Over-sampling Technique):** genera instancias sintéticas de la clase minoritaria interpolando entre ejemplos existentes en el espacio de características. No duplica instancias, sino que crea nuevas mediante:

```
x_nuevo = x_i + lambda * (x_vecino - x_i)
```

donde `lambda` es un valor aleatorio entre 0 y 1 y `x_vecino` es uno de los k vecinos más cercanos de `x_i` en la clase minoritaria.

```python
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X_train, y_train)
```

**`class_weight` en scikit-learn:** muchos estimadores de scikit-learn aceptan el parámetro `class_weight`. Con `class_weight='balanced'`, el modelo ajusta automáticamente el peso de cada clase inversamente proporcional a su frecuencia en el conjunto de entrenamiento, penalizando más los errores sobre la clase minoritaria:

```python
from sklearn.ensemble import RandomForestClassifier

modelo = RandomForestClassifier(class_weight='balanced', random_state=42)
modelo.fit(X_train, y_train)
```

### 5.2 Amplificación de sesgos del dataset por la función de pérdida

Un fenómeno menos intuitivo pero igualmente importante es que el entrenamiento puede amplificar sesgos que en el dataset original son moderados. Esto ocurre porque la función de pérdida orienta al modelo a capturar los patrones que minimizan el error en promedio, y si un patrón sesgado aparece en la mayoría de los ejemplos, el modelo lo captura con mayor profundidad que el patrón correcto presente en la minoría.

Estudios sobre modelos de reconocimiento de imágenes han mostrado que asociaciones de género presentes en el dataset de entrenamiento a un nivel del 33% aparecen en las predicciones del modelo a niveles del 68%, es decir, el modelo amplifica el sesgo en lugar de simplemente reproducirlo.

La regularización puede atenuar parcialmente este efecto al limitar la capacidad del modelo para memorizar patrones específicos, pero no lo elimina. Las técnicas de data augmentation orientadas a la equidad y la penalización explícita de la correlación entre variables sensibles y predicciones son las herramientas más efectivas para abordar este fenómeno.

### 5.3 Sesgo por hiperparámetros: el umbral de decisión

En clasificación binaria, los clasificadores de scikit-learn utilizan por defecto un umbral de 0,5: si la probabilidad estimada de la clase positiva es mayor de 0,5, se predice positivo. Este umbral tiene un impacto directo sobre las tasas de falsos positivos y falsos negativos, y puede afectar de forma diferente a distintos subgrupos.

Desplazar el umbral hacia 0,3 incrementa la sensibilidad (se detectan más positivos reales) a costa de una mayor tasa de falsos positivos. Desplazarlo hacia 0,7 reduce los falsos positivos pero aumenta los falsos negativos.

Si las distribuciones de probabilidad del modelo difieren entre subgrupos (lo que es habitual cuando el entrenamiento es desequilibrado por subgrupo), aplicar el mismo umbral a todos los grupos produce tasas de error diferentes. La selección del umbral es, por tanto, una decisión con implicaciones de equidad que debe tomarse de forma explícita y documentada.

---

## 6. PRL en trabajo con computación intensiva

### 6.1 Riesgos específicos del entrenamiento de modelos

El trabajo de entrenamiento de modelos de aprendizaje automático presenta riesgos laborales que, aunque no son tan visibles como los de entornos industriales tradicionales, están plenamente reconocidos por la normativa de prevención.

**Fatiga por monitorización de entrenamientos largos.** Un entrenamiento que se extiende durante horas o días requiere supervisión periódica para detectar divergencias, valores NaN en la pérdida, o bloqueos del proceso. Esta vigilancia intermitente pero sostenida genera fatiga cognitiva y dificulta la desconexión del trabajo, especialmente cuando el coste de un fallo es elevado.

**Estrés por fallos costosos.** Cuando un entrenamiento falla en la época 180 de 200 por un error de memoria o un problema de conectividad con el sistema de almacenamiento, el impacto no es solo técnico: representa horas o días de trabajo perdido y, en contextos de cloud computing, costes económicos no recuperables. Este tipo de situaciones genera estrés agudo y, en entornos de alta presión, puede derivar en burnout.

**Trabajo nocturno y fuera de horario.** Para aprovechar ventanas de menor demanda en clusters compartidos, o para supervisar entrenamientos iniciados al final de la jornada, los profesionales del sector frecuentemente trabajan fuera del horario laboral estándar. El trabajo nocturno tiene efectos documentados sobre la salud: alteración del ritmo circadiano, mayor riesgo cardiovascular, impacto sobre la salud mental.

**Sedentarismo prolongado.** El trabajo frente a múltiples monitores durante jornadas largas, especialmente cuando se monitoriza un entrenamiento activo, lleva a posiciones estáticas prolongadas que incrementan el riesgo de trastornos musculoesqueléticos.

### 6.2 Marco legal: Ley 31/1995 de PRL

La Ley 31/1995, de 8 de noviembre, de Prevención de Riesgos Laborales, es la norma marco en España que transpone la Directiva 89/391/CEE. Sus obligaciones son aplicables a cualquier sector, incluido el tecnológico.

Los principios de la acción preventiva (artículo 15) relevantes para el contexto del entrenamiento de modelos incluyen:

- **Evitar los riesgos:** cuando sea posible, eliminar la fuente del riesgo. En trabajo con computación intensiva, esto implica diseñar pipelines robustos con checkpoints frecuentes que reduzcan el impacto de los fallos.
- **Evaluar los riesgos que no se pueden evitar:** identificar y documentar los riesgos de fatiga visual, carga cognitiva, sedentarismo y alteración del descanso.
- **Adaptar el trabajo a la persona:** el artículo 15.1.d establece que la organización del trabajo debe adaptarse a las capacidades del trabajador. Los horarios de supervisión de entrenamientos deben distribuirse de forma que no recaigan sistemáticamente sobre las mismas personas.
- **Sustituir lo peligroso por lo que entrañe poco o ningún peligro:** el diseño de herramientas de monitorización automática (alertas, notificaciones, sistemas de early stopping automático) puede reducir la necesidad de vigilancia humana continua.

El artículo 14 establece el derecho de los trabajadores a una protección eficaz en materia de seguridad y salud, y la obligación correlativa del empresario de garantizar esa protección.

### 6.3 Ergonomía en trabajo con múltiples pantallas

El trabajo simultáneo con múltiples monitores (común en la monitorización de entrenamientos: una pantalla con logs, otra con tensorboard, otra con el código) exige condiciones ergonómicas específicas:

- **Distancia:** cada monitor debe estar a entre 50 y 70 cm de los ojos.
- **Altura:** el borde superior del monitor principal debe estar a la altura de los ojos o ligeramente por debajo.
- **Posición relativa de los monitores secundarios:** los monitores laterales deben colocarse de forma que el ángulo de giro del cuello no supere los 30 grados.
- **Iluminación:** evitar reflejos en las pantallas. La iluminación ambiental debe ser homogénea y difusa.
- **Pausas activas:** la normativa recomienda pausas de 5-10 minutos por cada hora de trabajo intensivo con pantalla.

El Real Decreto 488/1997, sobre disposiciones mínimas de seguridad y salud relativas al trabajo con equipos que incluyen pantallas de visualización, es la norma específica que desarrolla estas obligaciones.

### 6.4 El coste económico del entrenamiento como recurso que gestionar

El coste de un entrenamiento en infraestructura cloud puede oscilar entre decenas y miles de euros. Un cluster de 8 A100 en AWS (instancia p4d.24xlarge) cuesta aproximadamente 32 dólares por hora; un entrenamiento de 72 horas puede superar los 2.300 dólares. Este coste convierte al entrenamiento en un recurso gestionable comparable a cualquier otro recurso productivo.

La gestión responsable de este recurso implica: uso de instancias spot cuando el entrenamiento admite interrupciones, implementación de checkpoints para recuperación, monitorización del gasto en tiempo real, y definición de presupuestos máximos con alertas automáticas. Desde la perspectiva de la PRL, la presión derivada de un coste elevado y un fallo inesperado es un factor psicosocial de riesgo que la organización debe reconocer y mitigar.

---

## 7. Responsabilidad legal del modelo entrenado

### 7.1 EU AI Act: el primer marco regulatorio integral para la IA

El Reglamento (UE) 2024/1689, conocido como EU AI Act, publicado en el Diario Oficial de la Unión Europea el 12 de julio de 2024, establece un marco regulatorio horizontal para los sistemas de inteligencia artificial en la Unión Europea. Su entrada en aplicación es progresiva: las obligaciones más críticas comenzaron a aplicarse en febrero de 2025, y el régimen completo estará en vigor en agosto de 2026.

### 7.2 Clasificación de riesgo

El EU AI Act clasifica los sistemas de IA en cuatro categorías según el nivel de riesgo que presentan:

**Riesgo inaceptable:** sistemas prohibidos por representar una amenaza clara para los derechos fundamentales. Ejemplos: sistemas de puntuación social por parte de autoridades públicas, manipulación subliminal, explotación de vulnerabilidades de grupos específicos.

**Alto riesgo:** sistemas que deben cumplir un conjunto exhaustivo de requisitos antes de ser comercializados o puestos en servicio. Incluye sistemas utilizados en: biometría, infraestructuras críticas, educación, empleo y gestión de trabajadores, acceso a servicios privados y públicos esenciales, aplicación de la ley, gestión de la migración, administración de justicia.

**Riesgo limitado:** sistemas con obligaciones de transparencia específicas, como los chatbots, que deben informar al usuario de que está interactuando con una máquina.

**Riesgo mínimo:** sistemas que no están sujetos a obligaciones adicionales. La mayoría de los clasificadores de uso empresarial interno caen en esta categoría.

### 7.3 Artículo 10: requisitos de calidad de datos

El artículo 10 del EU AI Act establece requisitos específicos para los datos utilizados en el entrenamiento, validación y prueba de sistemas de IA de alto riesgo. Sus puntos más relevantes para el entrenamiento de modelos son:

- Los datos de entrenamiento deben someterse a prácticas de gobernanza y gestión adecuadas.
- Los datos deben ser pertinentes, representativos, libres de errores en la medida de lo posible, y completos.
- Los datos deben tener las características estadísticas apropiadas para la población, el territorio o el contexto de uso del sistema.
- Deben tomarse en consideración los posibles sesgos que puedan afectar a la salud, la seguridad o los derechos fundamentales de las personas.
- En casos excepcionales, el artículo 10.5 permite el procesamiento de categorías especiales de datos (origen racial o étnico, salud, orientación sexual) cuando sea estrictamente necesario para detectar y corregir sesgos en sistemas de alto riesgo.

### 7.4 Responsabilidad compartida

El EU AI Act establece una cadena de responsabilidad que distingue entre proveedores (quienes desarrollan y colocan en el mercado el sistema de IA), desplegadores (quienes utilizan el sistema en un contexto específico) e importadores y distribuidores. Las obligaciones más exigentes recaen sobre los proveedores de sistemas de alto riesgo, pero los desplegadores también tienen obligaciones de supervisión y notificación de incidentes.

En el contexto del entrenamiento de modelos, el técnico que entrena un modelo no es necesariamente el responsable legal del sistema resultante, pero sus decisiones técnicas —qué datos usar, cómo gestionar el desequilibrio, qué métricas de fairness aplicar, qué documentación generar— tienen implicaciones directas sobre el cumplimiento del proveedor y, en última instancia, sobre la legalidad del sistema desplegado.

---

## 8. Actividades prácticas

### Actividad 1: Auditoría de fairness con Fairlearn

**Descripción:** Dado un dataset de clasificación binaria con un atributo sensible (el dataset de ingresos del censo UCI Adult), entrenar un clasificador base (regresión logística o árbol de decisión) y evaluar su rendimiento mediante un `MetricFrame` de Fairlearn, desagregando exactitud, tasa de verdaderos positivos y tasa de falsos positivos por subgrupo del atributo sensible. Posteriormente, aplicar `ExponentiatedGradient` con la restricción `EqualizedOdds` y comparar las métricas antes y después de la mitigación.

**Entregables:** Notebook con código ejecutado, tabla comparativa de métricas por subgrupo antes y después de la mitigación, y un párrafo de interpretación donde el alumno justifique qué métrica de equidad priorizaría en un contexto real de selección de personal y por qué.

**Duración estimada:** 3 horas.

### Actividad 2: Medición de emisiones con CodeCarbon

**Descripción:** Entrenar un modelo de clasificación de imágenes (una red convolucional sencilla sobre CIFAR-10) instrumentado con CodeCarbon. Comparar las emisiones de tres configuraciones: entrenamiento completo (200 épocas), entrenamiento con early stopping (patience=10), y entrenamiento de un modelo destilado de menor capacidad. Estimar el ahorro en kg CO2 y en horas de GPU.

**Entregables:** Notebook con las tres ejecuciones, archivo CSV de emisiones generado por CodeCarbon, gráfico comparativo de emisiones vs. exactitud final de validación, y reflexión escrita sobre la relación entre rendimiento y sostenibilidad observada.

**Duración estimada:** 2,5 horas.

### Actividad 3: Mitigación de desequilibrio de clases

**Descripción:** Dado un dataset con desequilibrio severo (proporción 1:10 o mayor entre clases), comparar cinco estrategias de entrenamiento: sin ningún ajuste, con `class_weight='balanced'`, con oversampling SMOTE, con undersampling aleatorio, y con SMOTE + undersampling combinado. Evaluar cada estrategia con F1-score de la clase minoritaria, AUC-ROC, y curva Precision-Recall. Analizar el efecto de modificar el umbral de decisión (0.3, 0.4, 0.5, 0.6) sobre las métricas de cada estrategia.

**Entregables:** Notebook con código y visualizaciones, tabla de resultados comparativa, y análisis escrito de qué estrategia elegiría el alumno para un caso de detección de fraude bancario justificando la elección.

**Duración estimada:** 2,5 horas.

### Actividad 4: Evaluación de riesgos laborales y cumplimiento EU AI Act

**Descripción:** Dado el siguiente escenario: un equipo de tres personas debe entregar en 10 días un modelo de clasificación de riesgo crediticio para un banco. El entrenamiento se ejecuta en un cluster compartido con ventanas de disponibilidad nocturna. Redactar una evaluación de riesgos laborales del proyecto siguiendo la metodología del INSST, identificando al menos cinco riesgos, su probabilidad, su severidad, su nivel de riesgo resultante y las medidas preventivas propuestas. Incluir también un análisis de las obligaciones que impondría el EU AI Act al sistema resultante, clasificando el sistema según el nivel de riesgo y listando los requisitos del artículo 10 que deben cumplirse.

**Entregables:** Documento de evaluación de riesgos en formato tabla (riesgo, probabilidad, severidad, nivel, medida preventiva), análisis de cumplimiento EU AI Act, y reflexión sobre cómo las decisiones técnicas del entrenamiento afectan a la responsabilidad legal del equipo.

**Duración estimada:** 2 horas.

---

## 9. Referencias

**Fairness y equidad:**

- Fairlearn — Microsoft Research. Documentación oficial y guías de uso.  
  https://fairlearn.org/v0.10/

- AI Fairness 360 (AIF360) — IBM Research. Toolkit y documentación.  
  https://aif360.res.ibm.com/

- Chouldechova, A. (2017). Fair prediction with disparate impact: A study of bias in recidivism prediction instruments. *Big Data*, 5(2), 153-163.  
  https://doi.org/10.1089/big.2016.0047

- Kleinberg, J., Mullainathan, S., & Raghavan, M. (2016). Inherent trade-offs in the fair determination of risk scores. arXiv:1609.05807.  
  https://arxiv.org/abs/1609.05807

- Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*, 30.

**Impacto ambiental:**

- Strubell, E., Ganesh, A., & McCallum, A. (2019). Energy and Policy Considerations for Deep Learning in NLP. *Proceedings of ACL 2019*, 3645-3650.  
  https://arxiv.org/abs/1906.02629

- Schwartz, R., Dodge, J., Smith, N. A., & Etzioni, O. (2020). Green AI. *Communications of the ACM*, 63(12), 54-63.  
  https://doi.org/10.1145/3381831 — preprint: https://arxiv.org/abs/1907.10597

- CodeCarbon — documentación oficial y repositorio.  
  https://codecarbon.io/ — repositorio: https://github.com/mlco2/codecarbon

- Hinton, G., Vinyals, O., & Dean, J. (2015). Distilling the knowledge in a neural network. arXiv:1503.02531.  
  https://arxiv.org/abs/1503.02531

**Marco regulatorio:**

- Reglamento (UE) 2024/1689 del Parlamento Europeo y del Consejo, de 13 de junio de 2024 (EU AI Act). Diario Oficial de la Unión Europea, L 2024/1689, 12 de julio de 2024.  
  https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689

- Ley 31/1995, de 8 de noviembre, de Prevención de Riesgos Laborales. BOE núm. 269, 10 de noviembre de 1995.  
  https://www.boe.es/buscar/act.php?id=BOE-A-1995-24292

- Real Decreto 488/1997, de 14 de abril, sobre disposiciones mínimas de seguridad y salud relativas al trabajo con equipos que incluyen pantallas de visualización. BOE núm. 97, 23 de abril de 1997.  
  https://www.boe.es/buscar/act.php?id=BOE-A-1997-8671

- Instituto Nacional de Seguridad y Salud en el Trabajo (INSST) — Guía técnica para la evaluación y prevención de los riesgos relativos a la utilización de equipos con pantallas de visualización.  
  https://www.insst.es/documentacion/catalogo-de-publicaciones/guia-tecnica-para-la-evaluacion-y-prevencion-de-los-riesgos-relativos-a-la-utilizacion-de-equipos-con-pantallas-de-visualizacion

**Recursos complementarios:**

- Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic Minority Over-sampling Technique. *Journal of Artificial Intelligence Research*, 16, 321-357.  
  https://doi.org/10.1613/jair.953

- Imbalanced-learn — biblioteca de Python para tratamiento de desequilibrio de clases.  
  https://imbalanced-learn.org/

- Sanh, V., Debut, L., Chaumond, J., & Wolf, T. (2019). DistilBERT, a distilled version of BERT. arXiv:1910.01108.  
  https://arxiv.org/abs/1910.01108

---

*Unidad didáctica elaborada para el Ciclo Formativo Superior CFS1 — Gestión de Datos y Entrenamiento de IA. MP02 Entrenamiento de Modelos. Curso 2025-2026.*
