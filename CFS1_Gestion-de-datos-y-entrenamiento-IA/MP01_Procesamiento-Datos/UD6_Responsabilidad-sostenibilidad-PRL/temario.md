# UD6 · Trabajo responsable, sostenible y prevención de riesgos laborales

---

## 1. Introducción

El trabajo con datos no es una actividad técnica neutral. Cada decisión que se toma a lo largo del ciclo de vida del dato —qué se recoge, cómo se etiqueta, qué se descarta, qué modelo se entrena y con qué objetivo— tiene consecuencias reales sobre personas, organizaciones y el medio ambiente. Esta unidad aborda tres dimensiones que con frecuencia se tratan como añadidos opcionales al perfil técnico, pero que en la práctica determinan la calidad y la legitimidad del trabajo: la responsabilidad ética, la sostenibilidad ambiental y la prevención de riesgos laborales.

La ética aplicada a los datos no consiste en debatir abstracciones filosóficas, sino en reconocer que los sistemas que construimos amplifican patrones del pasado, toman decisiones que afectan empleos, libertades y oportunidades, y operan con asimetrías de poder entre quien produce el sistema y quien lo sufre. El profesional de datos que ignora esta dimensión produce sistemas que pueden funcionar perfectamente en términos técnicos y ser profundamente perjudiciales en términos humanos.

La sostenibilidad ambiental es igualmente concreta. Entrenar un modelo de lenguaje grande consume cantidades de energía comparables a varios vuelos transatlánticos. El procesamiento masivo de datos en centros de datos con alta huella de carbono contribuye al calentamiento global. Reducir esa huella no es solo una cuestión de imagen corporativa: es una responsabilidad profesional medible y mejorable con herramientas disponibles hoy.

Finalmente, la prevención de riesgos laborales cubre las condiciones en las que el propio profesional trabaja. El trabajo con datos implica largas horas frente a pantallas, ciclos de atención intensa, trabajo remoto con fronteras difusas entre vida personal y profesional, y presiones de entrega que pueden derivar en burnout. España tiene un marco normativo específico que establece obligaciones tanto para empleadores como para trabajadores, y conocerlo es parte de la formación profesional completa.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Identificar y clasificar los principales tipos de sesgo en conjuntos de datos y explicar su impacto en los sistemas de inteligencia artificial.
- Aplicar estrategias básicas de detección y mitigación de sesgos durante la fase de preparación de datos.
- Describir los principios éticos fundamentales aplicables al trabajo con datos y referenciar los marcos internacionales más relevantes.
- Comprender el concepto de privacidad por diseño y sus implicaciones prácticas en proyectos de datos.
- Estimar la huella de carbono de procesos de computación intensivos y aplicar medidas de reducción.
- Instalar y utilizar la herramienta CodeCarbon para monitorizar emisiones en proyectos de Python.
- Identificar el marco normativo español sobre prevención de riesgos laborales aplicable al trabajo con pantallas de visualización.
- Reconocer los principales riesgos ergonómicos y psicosociales en entornos de trabajo con datos.
- Conocer los principios del ACM Code of Ethics y aplicarlos a dilemas del ciclo de vida del dato.

---

## 3. Sesgos en datos y su impacto en IA

### 3.1 Qué es el sesgo en el contexto de datos

En estadística, sesgo es cualquier error sistemático que desvía los resultados de la realidad que se pretende representar. En sistemas de inteligencia artificial, el sesgo en datos es especialmente grave porque los modelos aprenden patrones del pasado y los codifican como predicciones del futuro, convirtiendo injusticias históricas en automatismos aparentemente objetivos.

### 3.2 Tipos principales de sesgo

**Sesgo de selección.** Ocurre cuando los datos utilizados para entrenar un modelo no representan adecuadamente la población sobre la que el modelo va a operar. Un sistema de reconocimiento facial entrenado mayoritariamente con imágenes de personas de piel clara tendrá tasas de error mucho más altas para personas de piel oscura. Esto no es un fallo del algoritmo en sentido estricto: el modelo hace exactamente lo que los datos le enseñan. El fallo está en la fase de recogida.

**Sesgo histórico.** Los datos reflejan el mundo tal como era, no como debería ser. Si durante décadas los puestos directivos en una empresa los han ocupado mayoritariamente hombres, un modelo entrenado con datos históricos de contratación aprenderá que "directivo" correlaciona con "hombre". El modelo reproduciría y escalaría una desigualdad estructural preexistente.

**Sesgo de medición.** Se produce cuando el instrumento o el proceso de recogida introduce distorsiones sistemáticas. Si una encuesta de satisfacción del cliente solo llega por correo electrónico, excluirá a quienes no tienen acceso digital o no revisan su bandeja de entrada regularmente. Los datos resultantes medirán bien la satisfacción de un subgrupo específico, no la del conjunto de clientes.

**Sesgo de confirmación.** Se da cuando quien diseña el sistema —o quien etiqueta los datos— parte de hipótesis previas que sesgan inconscientemente las decisiones. Un anotador que cree que determinado dialecto es señal de bajo nivel educativo etiquetará de forma diferente textos escritos en ese dialecto, introduciendo su prejuicio en el conjunto de entrenamiento.

### 3.3 Consecuencias reales

**Caso COMPAS.** El sistema COMPAS (Correctional Offender Management Profiling for Alternative Sanctions) se utilizó en Estados Unidos para predecir la probabilidad de reincidencia criminal y asistir a jueces en decisiones de libertad condicional. La investigación publicada por ProPublica en 2016 mostró que el sistema clasificaba erróneamente a los acusados negros como de alto riesgo a una tasa casi el doble que para los acusados blancos, y clasificaba erróneamente a los acusados blancos como de bajo riesgo a una tasa mayor. El sistema nunca tuvo acceso explícito a la variable "raza", pero utilizaba proxies correlacionados (código postal, historial de arrestos en el vecindario) que recogían el efecto de décadas de aplicación desigual de la ley.

**Amazon Hiring Tool.** Amazon desarrolló un sistema de cribado automático de currículums que debía identificar al mejor talento técnico. El sistema fue entrenado con los currículums enviados a lo largo de diez años, en un período en el que la mayoría de los candidatos seleccionados eran hombres. El modelo aprendió a penalizar currículums que incluían palabras como "mujeres" (por ejemplo, "presidenta del club de mujeres en ingeniería") y a valorar negativamente verbos típicamente asociados a comunicaciones escritas por mujeres. Amazon descontinuó el proyecto en 2018 cuando constató que no podía garantizar que el sistema fuera neutral respecto al género.

### 3.4 Estrategias de detección y mitigación en la fase de datos

La mitigación de sesgos es más efectiva cuanto antes se aborda en el ciclo de vida del dato. Intervenir en la fase de datos previene que el sesgo quede codificado en el modelo, desde donde es mucho más difícil de corregir.

**Auditoría de representación.** Antes de entrenar cualquier modelo, analizar la distribución del conjunto de datos en función de variables demográficas relevantes. En Python, esto puede hacerse con pandas:

```python
import pandas as pd

df = pd.read_csv("datos_contratacion.csv")

# Distribución de la variable objetivo por género
print(df.groupby("genero")["contratado"].value_counts(normalize=True))

# Distribución por grupo étnico
print(df["grupo_etnico"].value_counts(normalize=True))
```

**Análisis de correlación con proxies.** Identificar variables que, aunque no son directamente variables protegidas, correlacionan fuertemente con ellas. El código postal, el nombre, o el centro educativo pueden actuar como proxies de raza, origen o clase social.

**Reetiquetado y auditoría de anotaciones.** Si los datos incluyen etiquetas humanas, revisar la consistencia entre anotadores y medir el acuerdo interanotador (Cohen's Kappa). Discrepancias sistemáticas entre anotadores pueden indicar sesgo de confirmación.

**Técnicas de reequilibrio.** Cuando la representación de subgrupos es desigual, se pueden aplicar técnicas de oversampling del grupo subrepresentado (SMOTE para datos tabulares), undersampling del grupo sobrerepresentado, o asignación de pesos diferentes a las instancias en el entrenamiento.

**Fairness metrics.** Usar librerías como Fairlearn o AI Fairness 360 para medir métricas de equidad: igualdad de oportunidad (equal opportunity), paridad demográfica (demographic parity) o equidad individual. Estas métricas no deben evaluarse solo sobre el conjunto de test global, sino desglosadas por subgrupo.

---

## 4. Ética en el trabajo con datos

### 4.1 Principios éticos aplicados

El trabajo ético con datos no deriva de una sola tradición filosófica, sino de la síntesis práctica de varios principios:

**Beneficencia y no maleficencia.** El sistema debe producir beneficios reales y evitar daños. Esto implica evaluar no solo si el modelo funciona, sino para quién funciona y a qué coste para quienes quedan fuera del perímetro de beneficio.

**Autonomía y consentimiento.** Las personas tienen derecho a saber que sus datos se usan, con qué fin y con qué consecuencias para ellas. El consentimiento informado no es solo un requisito legal (como establece el RGPD): es un principio ético que obliga a comunicar de forma comprensible, no en 40 páginas de términos y condiciones.

**Justicia y equidad.** Los beneficios y los riesgos del sistema deben distribuirse de forma justa. Un sistema que funciona bien para grupos mayoritarios y mal para grupos minoritarios puede mostrar buenas métricas agregadas mientras produce daño sistemático.

**Transparencia y explicabilidad.** Las decisiones automatizadas que afectan a personas deben poder explicarse. El artículo 22 del RGPD reconoce el derecho a no ser objeto de decisiones tomadas exclusivamente mediante tratamiento automatizado, y el derecho a obtener explicación y a impugnar la decisión.

**Responsabilidad (accountability).** Alguien debe poder responder por el sistema y sus consecuencias. La difusión de la responsabilidad en equipos grandes, o la delegación a "el algoritmo", no exime de responsabilidad a quienes diseñan, despliegan y mantienen el sistema.

### 4.2 Privacidad por diseño

La Privacy by Design es un marco conceptual desarrollado por Ann Cavoukian, ex Comisionada de Información y Privacidad de Ontario (Canadá), en los años noventa y elevado a estándar internacional por la ISO/IEC 29101. Sus siete principios fundacionales son:

1. **Proactivo, no reactivo; preventivo, no correctivo.** La privacidad se anticipa y previene antes de que ocurran los problemas, no se reacciona ante ellos.
2. **Privacidad como configuración predeterminada.** El nivel máximo de privacidad debe ser el estado por defecto, sin que el usuario tenga que hacer nada para activarlo.
3. **Privacidad integrada en el diseño.** No es un añadido posterior: forma parte de la arquitectura del sistema desde el principio.
4. **Funcionalidad plena — suma positiva, no suma cero.** La privacidad y la funcionalidad no son objetivos en conflicto: es posible lograr ambos sin sacrificar uno por el otro.
5. **Seguridad extremo a extremo — protección durante todo el ciclo de vida.** Los datos se protegen desde que se recogen hasta que se destruyen.
6. **Visibilidad y transparencia.** Los componentes del sistema y sus operaciones son verificables y auditables.
7. **Respeto por la privacidad del usuario.** El interés del usuario es el punto de referencia central.

En la práctica, esto se traduce en técnicas concretas: minimización de datos (recoger solo lo estrictamente necesario), seudonimización y anonimización, cifrado en reposo y en tránsito, y control de acceso basado en roles.

### 4.3 Marcos éticos internacionales

**IEEE Ethically Aligned Design.** La IEEE lanzó en 2019 la versión 1 de este documento, resultado de un proceso participativo con más de 250 expertos de todo el mundo. Articula principios para el diseño de sistemas autónomos e inteligentes: bienestar humano, responsabilidad de los datos, transparencia, educación y sensibilización, y gobernanza de datos. Es un documento de referencia para la industria que va más allá de la regulación y propone una visión de los sistemas de IA centrada en el ser humano.

**Declaración de Montréal para el desarrollo responsable de la IA.** Elaborada en 2017-2018 por la Université de Montréal con un proceso de cocreación pública, esta declaración articula diez principios: bienestar, autonomía, justicia, privacidad, conocimiento, responsabilidad democrática, democracia, equidad, diversidad e inclusión, y prudencia. Es notable porque surgió de un proceso bottom-up, no de una institución gubernamental o corporativa.

**EU AI Act (Reglamento de IA de la Unión Europea, 2024).** El primer marco regulatorio integral para la IA en el mundo. Clasifica los sistemas de IA en categorías de riesgo (inaceptable, alto, limitado, mínimo) y establece requisitos proporcionales al riesgo. Los sistemas de IA de alto riesgo —que incluyen sistemas usados en contratación, crédito, acceso a educación o justicia— deben cumplir requisitos de calidad de datos, documentación, transparencia, supervisión humana y robustez.

---

## 5. Sostenibilidad ambiental

### 5.1 La huella de carbono del procesamiento de datos

El sector de las TIC representa aproximadamente el 2-4% de las emisiones globales de gases de efecto invernadero, una cifra comparable a la aviación civil. Dentro del sector, los centros de datos y las redes de transmisión son los mayores consumidores. Pero la distribución no es uniforme: entrenar modelos de aprendizaje automático grandes es extraordinariamente intensivo en energía.

Un estudio publicado por Strubell et al. en 2019 ("Energy and Policy Considerations for Deep Learning in NLP") estimó que entrenar un modelo Transformer grande con búsqueda de hiperparámetros podía emitir aproximadamente 284 toneladas de CO2 equivalente, comparable a las emisiones de cinco coches durante toda su vida útil. Entrenar GPT-3 se estimó posteriormente en el rango de 500-700 toneladas. Estos números varían enormemente según la fuente de energía del centro de datos: un centro alimentado con energía renovable al 100% tiene una fracción de esa huella.

Para el trabajo cotidiano con datos —procesamiento de datasets de tamaño medio, entrenamiento de modelos de machine learning clásico, ejecución de pipelines de ETL— la huella por ejecución individual es mucho menor, pero la acumulación de muchas ejecuciones, especialmente durante fases de experimentación intensiva, puede ser significativa.

### 5.2 CodeCarbon: instalación y uso

CodeCarbon es una librería de Python de código abierto que estima las emisiones de CO2 del código que se ejecuta. Rastrea el consumo de CPU, GPU y RAM, y lo combina con datos de la intensidad de carbono de la red eléctrica en la ubicación geográfica del proceso.

**Instalación:**

```bash
pip install codecarbon
```

**Uso básico como decorador:**

```python
from codecarbon import EmissionsTracker

tracker = EmissionsTracker()
tracker.start()

# Aquí va el código cuya huella queremos medir
# Por ejemplo, entrenamiento de un modelo:
from sklearn.ensemble import RandomForestClassifier
import numpy as np

X = np.random.rand(10000, 50)
y = np.random.randint(0, 2, 10000)
clf = RandomForestClassifier(n_estimators=200)
clf.fit(X, y)

emissions = tracker.stop()
print(f"Emisiones estimadas: {emissions:.6f} kg CO2eq")
```

**Uso con gestor de contexto:**

```python
from codecarbon import EmissionsTracker

with EmissionsTracker() as tracker:
    # código a medir
    resultado = pipeline_procesamiento(datos)

# El tracker guarda automáticamente un archivo emissions.csv
```

**Generación de informe:**

```bash
# Ver los resultados guardados
carbonboard --filepath="emissions.csv"
```

CodeCarbon genera un archivo `emissions.csv` con métricas detalladas: duración, energía consumida en kWh, emisiones en kg CO2eq, y el equivalente en kilómetros conducidos en coche o en horas de visualización de televisión.

### 5.3 Otras herramientas de medición

**ML CO2 Impact Calculator** (mlco2.github.io/impact): calculadora web que permite estimar las emisiones de un experimento de ML introduciendo el hardware utilizado, las horas de ejecución y la región geográfica del proveedor cloud. Es útil para estimaciones rápidas sin necesidad de instrumentar el código.

**Green Algorithms** (green-algorithms.org): calculadora más granular que permite especificar el tipo exacto de CPU/GPU, el número de núcleos y el factor de eficiencia del centro de datos (PUE, Power Usage Effectiveness).

### 5.4 Estrategias de reducción

**Optimización de queries y pipelines.** La ineficiencia computacional tiene coste energético directo. Utilizar índices en bases de datos, evitar scans completos cuando se pueden usar predicados selectivos, vectorizar operaciones con NumPy en lugar de bucles Python, y usar tipos de datos apropiados (int8 en lugar de float64 cuando es suficiente) reduce el tiempo de cómputo y el consumo energético.

**Procesamiento local vs. cloud.** El cloud no es inherentemente menos eficiente, pero la latencia de red, la transferencia de datos y el overhead de virtualización pueden hacer que ciertas tareas consuman más energía en cloud que en local. Para experimentos pequeños e iterativos, trabajar localmente con hardware dedicado puede ser más eficiente. Para procesos que se benefician de paralelización masiva, el cloud en regiones con alta penetración de renovables (Escandinavia, Oregon, Iowa) es preferible.

**Transferencia de aprendizaje y reutilización de modelos.** Fine-tuning de modelos preentrenados es órdenes de magnitud menos costoso que entrenar desde cero. La reutilización de modelos existentes (model cards en Hugging Face, por ejemplo) evita duplicar trabajo computacional ya realizado.

**Programación temporal.** Algunos proveedores cloud ofrecen descuentos y tienen mayor disponibilidad de energía renovable en horas de baja demanda. Programar trabajos batch intensivos para esas ventanas horarias reduce la huella de carbono sin coste adicional.

### 5.5 Green Software Foundation

La Green Software Foundation es una organización sin ánimo de lucro fundada en 2021 con el apoyo de Microsoft, GitHub, Accenture y otras empresas tecnológicas. Propone tres principios para el software sostenible:

1. **Eficiencia energética:** usar la menor cantidad de electricidad posible para producir el mismo resultado funcional.
2. **Conciencia del hardware:** maximizar la vida útil del hardware existente y evitar estimular la producción de hardware nuevo innecesariamente.
3. **Conciencia del carbono:** ejecutar código cuando y donde la electricidad es más limpia.

El protocolo Software Carbon Intensity (SCI) de la Green Software Foundation proporciona una métrica estandarizada para medir la intensidad de carbono del software, calculada como emisiones por unidad funcional (por ejemplo, por usuario, por transacción o por hora de uso).

---

## 6. Prevención de riesgos laborales

### 6.1 Marco normativo en España

El trabajo con datos se realiza principalmente en entornos de oficina, con uso intensivo de pantallas de visualización. España cuenta con legislación específica que regula estos entornos:

**Ley 31/1995, de 8 de noviembre, de Prevención de Riesgos Laborales (LPRL).** Es la norma marco del sistema de prevención en España, transposición de la Directiva Marco 89/391/CEE. Establece los derechos y obligaciones fundamentales: el derecho de los trabajadores a una protección eficaz frente a los riesgos derivados del trabajo; la obligación del empresario de garantizar la seguridad y salud de los trabajadores; el deber de planificación de la actividad preventiva a partir de una evaluación de riesgos.

**Real Decreto 488/1997, de 14 de abril, sobre disposiciones mínimas de seguridad y salud relativas al trabajo con equipos que incluyen pantallas de visualización.** Es la norma técnica específica que aplica directamente al trabajo del profesional de datos. Establece requisitos mínimos para el equipo (pantalla, teclado, mesa, silla, espacio), para el entorno (iluminación, reflejos, ruido, calor), y para la organización del trabajo (descansos, cambios de actividad, formación e información). Obliga al empleador a realizar una evaluación de riesgos específica para puestos con pantallas de visualización y a adoptar medidas correctoras cuando se detectan deficiencias.

**Real Decreto 286/2006, sobre protección de la salud y la seguridad de los trabajadores contra los riesgos relacionados con la exposición al ruido.** Relevante en entornos de oficina abierta o call centers donde el ruido ambiental puede ser un factor de riesgo.

**Ley Orgánica 3/2018, de Protección de Datos Personales y garantía de los derechos digitales (LOPDGDD).** Incluye, en su Título X, un catálogo de derechos digitales de los trabajadores: derecho a la intimidad frente al uso de dispositivos digitales, derecho a la desconexión digital, derecho a la intimidad frente a la geolocalización, y protección frente al control del empleador mediante cámaras y micrófonos. Estos derechos son directamente relevantes para el profesional que trabaja en remoto.

### 6.2 Riesgos ergonómicos

**Postura y carga músculo-esquelética.** El trabajo sedentario prolongado con postura inadecuada es la causa más frecuente de trastornos músculo-esqueléticos en trabajadores de oficina: cervicalgias, dorsalgias, lumbalgias, síndrome del túnel carpiano. El RD 488/1997 especifica requisitos de ajustabilidad: la silla debe permitir regular la altura del asiento, el respaldo debe dar apoyo lumbar, los pies deben apoyar completamente en el suelo o en un reposapiés.

**Iluminación y fatiga visual.** La iluminación debe ser suficiente (mínimo 500 lux sobre el plano de trabajo según la norma UNE-EN 12464-1 para trabajo de oficina), pero evitar deslumbramientos directos (ventanas en el campo visual) o reflejados (luz que se refleja sobre la pantalla). La pantalla debe situarse perpendicular a las ventanas. El síndrome visual informático agrupa síntomas como sequedad ocular, visión borrosa, cefaleas y diplopía, provocados por el parpadeo reducido durante el trabajo con pantallas y el esfuerzo de acomodación continuo.

**Pausas activas.** El RD 488/1997 establece que el trabajo ante pantallas debe interrumpirse periódicamente con pausas o cambios de actividad que reduzcan la carga del trabajo en pantalla. La regla 20-20-20 es una referencia práctica ampliamente recomendada por oftalmólogos: cada 20 minutos, mirar durante 20 segundos a un objeto a 20 pies (6 metros) de distancia, para reducir la fatiga de acomodación. Además, pausas de 5-10 minutos cada hora de trabajo continuo para levantarse, moverse y estirar la musculatura cervical y lumbar.

### 6.3 Riesgos psicosociales

**Estrés tecnológico (tecnoestrés).** El tecnoestrés es la incapacidad de adaptarse de forma saludable a las nuevas tecnologías. En el profesional de datos, se manifiesta en la ansiedad ante la velocidad de cambio del ecosistema tecnológico (nuevas librerías, nuevos paradigmas, nuevos modelos que obsoletan el trabajo reciente), la sensación de no estar al día y la presión por demostrar competencia técnica continua.

**Tecnoadicción.** La tecnoadicción es el uso compulsivo de dispositivos tecnológicos que interfiere con otras áreas de la vida. En entornos de trabajo con datos, se expresa en la dificultad para desconectar de sistemas de notificación (Slack, correo, alertas de pipelines), la comprobación compulsiva de métricas de modelos en producción y la incapacidad de establecer límites entre tiempo de trabajo y tiempo personal.

**Burnout en entornos de datos.** El burnout o síndrome de agotamiento profesional es reconocido por la OMS como un fenómeno ocupacional (ICD-11). En el contexto del trabajo con datos, factores específicos de riesgo son: la presión por resultados en proyectos con plazos ajustados, la carga cognitiva sostenida que requiere el trabajo analítico profundo, la falta de reconocimiento cuando el trabajo de datos es "invisible" para la organización, y la acumulación de deuda técnica que genera frustración profesional.

**Trabajo remoto y riesgos específicos.** El teletrabajo ha aumentado significativamente en el sector de datos. Introduce riesgos específicos: el aislamiento social y la reducción de interacciones informales que tienen función de apoyo emocional; la disolución de las fronteras temporales entre trabajo y descanso; la dificultad para desconectar cuando el entorno físico de trabajo y descanso coinciden; y la ergonomía frecuentemente deficiente en entornos domésticos no diseñados para trabajo sostenido.

La LOPDGDD (artículo 88) reconoce el **derecho a la desconexión digital** de los trabajadores para garantizar el respeto de su tiempo de descanso, permisos y vacaciones. Los convenios colectivos deben regular el ejercicio de este derecho, pero su reconocimiento legal es un instrumento que el trabajador puede invocar.

### 6.4 Medidas preventivas

**Obligatorias para el empleador:**

- Realizar una evaluación de riesgos específica del puesto de pantalla de visualización antes de que el trabajador comience a usar el equipo.
- Adoptar medidas para corregir los riesgos detectados en la evaluación, en los plazos que establezca el plan de prevención.
- Proporcionar formación e información sobre los riesgos del puesto y las medidas preventivas.
- Garantizar la vigilancia periódica de la salud, incluyendo revisión oftalmológica, para trabajadores que usan pantallas de forma habitual.
- Proporcionar corrección visual especial (lentes específicas para la distancia de trabajo) si la revisión oftalmológica lo indica y los medios de corrección habituales del trabajador no son adecuados.

**Recomendadas para el trabajador:**

- Ajustar correctamente la silla, la altura de la mesa y la posición de la pantalla al inicio de cada jornada.
- Mantener la pantalla a una distancia de entre 50 y 70 cm de los ojos.
- Aplicar la regla 20-20-20 para reducir la fatiga visual.
- Realizar pausas activas con ejercicios de movilidad cervical, lumbar y de extremidades superiores.
- Establecer horarios de inicio y fin de jornada y respetarlos, especialmente en teletrabajo.
- Utilizar herramientas de gestión del tiempo (técnica Pomodoro, bloques de trabajo profundo) para estructurar la carga cognitiva.

---

## 7. Responsabilidad profesional y deontología

### 7.1 ACM Code of Ethics (2018)

La Association for Computing Machinery (ACM) publicó en 2018 una actualización de su Código de Ética y Conducta Profesional, el estándar deontológico de referencia para profesionales de la informática y la ciencia de datos. Sus principios generales incluyen:

- **Contribuir al bien de la sociedad y al bienestar humano.** Los profesionales deben considerar el impacto de su trabajo sobre todos los grupos de personas, no solo sobre quienes pagan por el servicio.
- **Evitar el daño.** Cuando el daño es inevitable, se debe minimizar. Cuando el daño potencial es significativo, se debe consultar con otros afectados y, si procede, denegar la participación en el proyecto.
- **Ser honesto y digno de confianza.** Incluye ser honesto sobre las limitaciones del propio trabajo y de los sistemas que se construyen, en lugar de sobrevender capacidades.
- **Respetar la privacidad.** Los profesionales deben adherirse a los principios de privacidad por diseño y respetar la confidencialidad de los datos de las personas.
- **Respetar la propiedad intelectual.** Incluir el reconocimiento apropiado de las contribuciones de otros, no plagiar código ni resultados.

En el ámbito profesional específico, el código establece que los profesionales deben conocer las reglas y regulaciones aplicables a su trabajo, deben aceptar solo responsabilidades que estén dentro de su competencia, y deben diseñar y construir sistemas robustos, seguros y usables.

### 7.2 Responsabilidad en el ciclo de vida del dato

La responsabilidad profesional no se limita a la fase de análisis o modelado: se extiende a todo el ciclo de vida del dato.

**Recogida.** ¿Los datos se recogen con consentimiento informado? ¿Se recoge solo lo necesario (minimización)? ¿Existen subgrupos excluidos que harán al sistema injusto?

**Almacenamiento.** ¿Se cifran los datos en reposo? ¿Se aplica control de acceso adecuado? ¿Existe una política de retención que defina cuánto tiempo se guardan los datos?

**Procesamiento y análisis.** ¿Se han identificado y mitigado los sesgos? ¿Se documenta el proceso de transformación para garantizar la reproducibilidad y la auditabilidad?

**Modelado.** ¿El modelo es apropiado para el problema? ¿Sus predicciones son explicables cuando afectan a personas? ¿Se han medido métricas de equidad por subgrupo?

**Despliegue y monitorización.** ¿Existe supervisión humana para las decisiones de alto impacto? ¿Se monitoriza el rendimiento del modelo en producción para detectar degradación o distributional shift? ¿Existe un proceso para retirar o corregir el modelo cuando produce daño?

**Borrado.** ¿Se respeta el derecho al olvido (artículo 17 del RGPD)? ¿Existen procedimientos para borrar datos de personas que ejercen este derecho, incluyendo su posible efecto sobre los modelos entrenados con esos datos?

### 7.3 Gestión de conflictos de interés

El profesional de datos puede encontrarse ante situaciones en las que los intereses del empleador o del cliente entran en conflicto con su responsabilidad hacia las personas cuyos datos maneja o hacia la sociedad en general. Algunos escenarios comunes:

- Un cliente solicita construir un modelo predictivo con un conjunto de datos que el profesional sospecha que no fue recogido con consentimiento adecuado.
- El empleador pide maximizar métricas de negocio (conversión, engagement) con técnicas que el profesional considera manipuladoras.
- Se detecta un sesgo significativo en un sistema en producción, pero corregirlo implicaría reducir el rendimiento agregado y el cliente no quiere asumir el coste.

El ACM Code of Ethics orienta en estos casos a ser transparente sobre el conflicto, a intentar resolver la situación internamente antes que externamente, y a no participar en actividades que el profesional considere éticamente inaceptables, incluso cuando eso tenga consecuencias profesionales. Muchas organizaciones disponen de canales internos de reporte de conductas (whistleblowing) que el profesional puede utilizar.

---

## 8. Actividades prácticas propuestas

**Actividad 1: Auditoría de sesgo en un dataset público.** Descargar el dataset Adult Income (UCI Machine Learning Repository), que contiene datos demográficos y la variable objetivo de si una persona gana más o menos de 50.000 dólares anuales. Usando pandas, analizar la distribución de la variable objetivo en función del sexo, la raza y el nivel educativo. Calcular la tasa de predicción positiva para cada grupo si se usa un umbral de clasificación estándar (0.5). Documentar los sesgos encontrados y proponer al menos dos estrategias de mitigación justificadas. Entregar un notebook Jupyter con el análisis y un párrafo de conclusiones éticas.

**Actividad 2: Medición de huella de carbono con CodeCarbon.** Instalar CodeCarbon en el entorno de trabajo. Instrumentar con el tracker al menos tres procesos distintos: una operación de carga y limpieza de un CSV grande, el entrenamiento de un RandomForestClassifier con 100 árboles, y el mismo entrenamiento con 500 árboles. Comparar las emisiones estimadas de los tres procesos y calcular el equivalente en kilómetros de coche. Reflexionar brevemente sobre qué parámetros del experimento tienen mayor impacto en la huella de carbono.

**Actividad 3: Evaluación ergonómica del puesto de trabajo.** Usar el checklist del RD 488/1997 (disponible en el INSST, Instituto Nacional de Seguridad y Salud en el Trabajo) para evaluar el propio puesto de trabajo. Identificar al menos tres aspectos que no cumplen las recomendaciones mínimas y proponer medidas correctoras concretas. Si el trabajo es en remoto, señalar qué medidas son responsabilidad del empleador y cuáles del propio trabajador en el contexto del teletrabajo (Real Decreto-ley 28/2020).

**Actividad 4: Análisis de un caso ético.** Leer el artículo de ProPublica "Machine Bias" (2016, disponible en propublica.org) sobre el sistema COMPAS. Responder las siguientes preguntas: ¿Qué tipo o tipos de sesgo están presentes en el sistema? ¿En qué fase del ciclo de vida del dato se podrían haber detectado? ¿Qué responsabilidad tienen los desarrolladores del sistema según el ACM Code of Ethics? ¿Qué derechos tienen los afectados según el RGPD y el EU AI Act?

---

## 9. Referencias y material externo

**Normativa:**

1. Unión Europea. **Reglamento General de Protección de Datos (RGPD), Reglamento (UE) 2016/679**, del Parlamento Europeo y del Consejo, de 27 de abril de 2016. Disponible en: https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX%3A32016R0679

2. España. **Ley 31/1995, de 8 de noviembre, de Prevención de Riesgos Laborales.** BOE núm. 269, de 10 de noviembre de 1995. Disponible en: https://www.boe.es/buscar/act.php?id=BOE-A-1995-24292

3. España. **Real Decreto 488/1997, de 14 de abril, sobre disposiciones mínimas de seguridad y salud relativas al trabajo con equipos que incluyen pantallas de visualización.** BOE núm. 97, de 23 de abril de 1997. Disponible en: https://www.boe.es/buscar/act.php?id=BOE-A-1997-8671

4. Unión Europea. **Reglamento de Inteligencia Artificial (EU AI Act), Reglamento (UE) 2024/1689**, del Parlamento Europeo y del Consejo, de 13 de junio de 2024. Disponible en: https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX%3A32024R1689

**Herramientas:**

5. Lottick, K. et al. **CodeCarbon: Measure and Reduce your Machine Learning Carbon Footprint.** Repositorio GitHub: https://github.com/mlco2/codecarbon. Documentación completa en: https://mlco2.github.io/codecarbon/

6. Lacoste, A. et al. **Quantifying the Carbon Emissions of Machine Learning (ML CO2 Impact).** Herramienta web: https://mlco2.github.io/impact/. Paper asociado: https://arxiv.org/abs/1910.09700

**Libros y publicaciones académicas:**

7. O'Neil, C. (2016). **Weapons of Math Destruction: How Big Data Increases Inequality and Threatens Democracy.** Crown Publishers. ISBN: 978-0553418811. Una de las referencias fundamentales sobre el impacto social de los algoritmos de decisión automatizada, con casos de estudio en crédito, seguros, empleo y educación.

8. Strubell, E., Ganesh, A. y McCallum, A. (2019). **Energy and Policy Considerations for Deep Learning in NLP.** Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics. Disponible en: https://arxiv.org/abs/1906.02629

9. Angwin, J., Larson, J., Mattu, S. y Kirchner, L. (2016). **Machine Bias.** ProPublica. Disponible en: https://www.propublica.org/article/machine-bias-risk-assessments-in-criminal-sentencing

**Marcos éticos:**

10. ACM. (2018). **ACM Code of Ethics and Professional Conduct.** Association for Computing Machinery. Disponible en: https://www.acm.org/code-of-ethics

11. IEEE. (2019). **Ethically Aligned Design: A Vision for Prioritizing Human Well-being with Autonomous and Intelligent Systems, Version 1.** IEEE Standards Association. Disponible en: https://standards.ieee.org/industry-connections/ec/autonomous-systems/

12. Université de Montréal. (2018). **Déclaration de Montréal pour un développement responsable de l'intelligence artificielle.** Disponible en: https://declarationmontreal-iaresponsable.com/

---

*Material docente elaborado para el Certificado de Formación Especializada CFS1 — Gestión de datos y entrenamiento de IA / MP01 Procesamiento de Datos. Fecha de revisión: junio de 2026.*
