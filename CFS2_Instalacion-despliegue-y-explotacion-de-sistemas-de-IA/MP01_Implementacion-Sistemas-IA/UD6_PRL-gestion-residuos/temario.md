# UD6 · Prevención de riesgos laborales y gestión de residuos en entornos de sistemas de IA

---

## 1. Introducción

Los entornos donde se instalan, despliegan y explotan sistemas de inteligencia artificial comparten muchas de las características de los centros de datos tradicionales, pero presentan una serie de factores agravantes que los diferencian de otras instalaciones tecnológicas convencionales. La densidad energética por rack se ha multiplicado en los últimos años como consecuencia de la adopción masiva de unidades de procesamiento gráfico (GPU) y aceleradores especializados: mientras un rack de servidor de propósito general podía consumir entre 5 y 10 kW, un rack de computación de IA orientado a inferencia o entrenamiento puede superar los 40-80 kW, y en configuraciones de clústeres de alto rendimiento (HPC) se alcanzan densidades de más de 100 kW por rack. Esta realidad tiene implicaciones directas sobre los sistemas de refrigeración, el cableado eléctrico, los riesgos de incendio, los campos electromagnéticos y las condiciones ambientales a las que se exponen los trabajadores.

Al mismo tiempo, la proliferación de hardware de IA genera un volumen creciente de residuos de aparatos eléctricos y electrónicos (RAEE). Los servidores, las tarjetas GPU, las baterías de los sistemas de alimentación ininterrumpida (SAI/UPS), los equipos de refrigeración líquida y los sistemas de almacenamiento tienen ciclos de vida relativamente cortos en comparación con otra maquinaria industrial, y su gestión al final de vida útil está estrictamente regulada tanto a nivel europeo como en el ordenamiento jurídico español.

Esta unidad didáctica aborda la prevención de riesgos laborales (PRL) desde una perspectiva aplicada al entorno real de trabajo en instalaciones de IA, tomando como eje el marco normativo vigente en España y la Unión Europea, y articulando los conceptos teóricos con procedimientos prácticos orientados al técnico de sistemas que deberá operar, mantener o supervisar este tipo de infraestructuras.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el alumnado será capaz de:

- Identificar el marco normativo de prevención de riesgos laborales aplicable a los entornos de instalación y explotación de sistemas de IA.
- Reconocer y evaluar los riesgos laborales específicos presentes en centros de datos de alta densidad energética: riesgo eléctrico, incendio, ergonómico, caída, campos electromagnéticos y estrés térmico.
- Aplicar la metodología de evaluación de riesgos para elaborar una matriz de riesgos adaptada a una instalación de servidores GPU.
- Seleccionar y utilizar correctamente los equipos de protección individual (EPI) adecuados para cada tipo de riesgo presente en estos entornos.
- Explicar el marco regulador de la gestión de RAEE en España, identificar las categorías de residuos que genera una instalación de IA y describir el circuito de gestión correcto.
- Diseñar los elementos básicos de un plan de emergencia para un centro de datos, incluyendo procedimientos de evacuación en presencia de sistemas de extinción gaseosa y actuación ante electrocución.
- Aplicar los conocimientos adquiridos en actividades prácticas orientadas a situaciones reales de trabajo.

---

## 3. Marco normativo de PRL aplicado a centros de datos e instalaciones de IA

### 3.1 Ley 31/1995 de Prevención de Riesgos Laborales

La Ley 31/1995, de 8 de noviembre, de Prevención de Riesgos Laborales (LPRL) constituye el pilar fundamental del sistema de seguridad y salud en el trabajo en España. Transpone la Directiva Marco 89/391/CEE y establece los principios generales aplicables a cualquier actividad laboral, incluyendo la instalación, mantenimiento y explotación de sistemas de inteligencia artificial.

Los principios de acción preventiva que recoge el artículo 15 de la LPRL se aplican con plena vigencia en los entornos de IA:

- **Evitar los riesgos** en origen, lo que en el contexto de un centro de datos implica, por ejemplo, el diseño de corredores fríos y calientes para evitar la recirculación de aire caliente.
- **Evaluar los riesgos que no se puedan evitar**, mediante metodologías documentadas y actualizadas.
- **Combatir los riesgos en su origen**, priorizando medidas técnicas sobre medidas organizativas y estas sobre los equipos de protección individual.
- **Adaptar el trabajo a la persona**, lo que incluye el diseño ergonómico de los puestos de trabajo en sala de servidores o en consolas de monitorización.
- **Tener en cuenta la evolución de la técnica**, principio especialmente relevante en un sector donde el hardware evoluciona con gran rapidez.

Las **obligaciones del empresario** derivadas de la LPRL incluyen: planificar la actividad preventiva, garantizar la vigilancia de la salud de los trabajadores, proporcionar información y formación suficientes, dotar de equipos de trabajo y EPI adecuados, y designar uno o varios trabajadores para ocuparse de las actividades de protección y prevención, o concertar este servicio con una entidad especializada.

El **artículo 29** regula las **obligaciones del trabajador**: usar correctamente los medios y equipos de protección, no poner fuera de funcionamiento los dispositivos de seguridad, informar de inmediato sobre cualquier situación que suponga un riesgo, y cooperar con el empresario para garantizar condiciones seguras de trabajo. En un centro de datos, esto se traduce, por ejemplo, en la obligación de no manipular instalaciones eléctricas sin la habilitación correspondiente, notificar anomalías en los sistemas de refrigeración o incidentes con baterías de litio, y respetar los procedimientos de trabajo seguro establecidos.

El **artículo 24** regula la **coordinación de actividades empresariales**. En los centros de datos compartidos —colocation, data centers de terceros donde coexisten múltiples empresas clientes y el propio operador del edificio— es frecuente que trabajen de forma simultánea o sucesiva trabajadores de distintas empresas. La norma exige que las empresas concurrentes intercambien información sobre los riesgos de sus actividades, que el empresario titular del centro informe a los demás sobre los riesgos propios del lugar, y que se establezcan medios de coordinación adecuados. En la práctica, esto se articula mediante reuniones de coordinación, libros de registro de acceso, procedimientos de trabajo comunes y, cuando existe una empresa principal que controla el espacio, la exigencia de acreditar la organización preventiva de las subcontratas.

### 3.2 Reglamentos de desarrollo aplicables

**Real Decreto 486/1997**, de 14 de abril, sobre disposiciones mínimas de seguridad y salud en los lugares de trabajo. Establece las condiciones que deben cumplir los locales donde se realiza el trabajo, incluyendo dimensiones mínimas, iluminación, temperatura, ventilación y señalización. En una sala de servidores de IA, los requisitos de temperatura ambiental para los trabajadores (entre 17 y 27°C en trabajos sedentarios y entre 14 y 25°C en trabajos ligeros) pueden entrar en tensión con las condiciones óptimas de operación del hardware, lo que exige medidas específicas de protección cuando los técnicos accedan a zonas con temperaturas en los límites del rango aceptable.

**Real Decreto 614/2001**, de 8 de junio, sobre disposiciones mínimas para la protección de la salud y seguridad de los trabajadores frente al riesgo eléctrico. Es la norma de referencia para cualquier trabajo en proximidad de instalaciones eléctricas. Define los conceptos de zona de peligro, zona de proximidad y zona de trabajos en tensión, establece los procedimientos de trabajo que garantizan la seguridad (las denominadas "cinco reglas de oro": desconectar, bloquear, verificar ausencia de tensión, proteger frente a elementos en tensión y señalizar) y determina los requisitos de habilitación de los trabajadores según su categoría: trabajador autorizado, trabajador cualificado y jefe de trabajo.

**Real Decreto 488/1997**, de 14 de abril, sobre disposiciones mínimas de seguridad y salud relativas al trabajo con equipos que incluyen pantallas de visualización de datos. Es de aplicación directa al personal que trabaja en consolas de monitorización de sistemas de IA, centros de operaciones de red (NOC) o salas de control. Exige el análisis de los puestos de trabajo, la evaluación de los riesgos para la vista y la musculatura, la organización del tiempo de trabajo con pausas o cambios de actividad, y la vigilancia de la salud mediante reconocimientos específicos.

**Real Decreto 39/1997**, de 17 de enero, Reglamento de los Servicios de Prevención. Establece las modalidades de organización preventiva (trabajador designado, servicio de prevención propio, servicio de prevención ajeno, mancomunado) y los requisitos de las auditorías del sistema de prevención. Las empresas que operan centros de datos o instalaciones de IA deben contar con una modalidad organizativa adecuada a su tamaño y nivel de riesgo.

---

## 4. Riesgos laborales específicos en entornos de IA

### 4.1 Riesgo eléctrico

El riesgo eléctrico es el más relevante desde el punto de vista de la gravedad de las consecuencias potenciales. En un centro de datos de IA coexisten diferentes niveles de tensión: la acometida de la red eléctrica (que puede ser en media tensión, habitualmente 20 kV), los transformadores de potencia, los cuadros de distribución en baja tensión (400 V trifásico), los SAI y los propios racks de servidores (con alimentaciones redundantes a 230 V o sistemas de corriente continua a 48 V en algunos diseños).

El **Reglamento Electrotécnico para Baja Tensión (REBT)**, aprobado por Real Decreto 842/2002, establece las condiciones técnicas que deben cumplir las instalaciones. Sin embargo, la presencia de alimentación ininterrumpida hace que, incluso cuando se corta la alimentación desde la red, los equipos permanezcan energizados a través de las baterías del SAI. Este factor es fundamental: en un centro de datos no existe el equivalente a "desconectar el interruptor general" y esperar a que el equipo quede sin tensión. Los trabajadores deben conocer la topología completa de la alimentación antes de realizar cualquier intervención.

Las situaciones de mayor riesgo eléctrico en instalaciones de IA incluyen: intervenciones en cuadros de distribución de PDU (Power Distribution Unit) dentro del rack, sustitución de fuentes de alimentación en caliente (hot-swap), mantenimiento de sistemas UPS con baterías de gran capacidad, y trabajos de cableado en bandejas situadas en la parte superior de los racks, que pueden quedar en proximidad de cables energizados.

### 4.2 Riesgo de incendio

La alta densidad de carga calórica por metro cuadrado hace que el riesgo de incendio en salas de servidores de IA sea significativamente superior al de otras instalaciones. Los sistemas de extinción predominantes en centros de datos son los basados en agentes gaseosos: **FM-200 (HFC-227ea)** y **Novec 1230 (FK-5-1-12)**. Ambos actúan por sofocación química y son eficaces sin dañar los equipos electrónicos, a diferencia del agua.

Sin embargo, la descarga de estos agentes representa un riesgo para las personas presentes en la sala en el momento de la activación. El protocolo estándar incluye una señal de prealarma acústica y luminosa con un retardo de entre 30 y 60 segundos antes de la descarga, durante el cual todo el personal debe evacuar la sala. Una vez producida la descarga, la concentración del agente en el aire puede reducir la fracción de oxígeno disponible (en el caso del FM-200) o desplazar el oxígeno por su mayor densidad (Novec 1230 en alta concentración), por lo que está terminantemente prohibida la reentrada sin equipo de respiración autónomo hasta que la sala haya sido ventilada y confirmada como segura por personal autorizado.

### 4.3 Riesgos ergonómicos

El trabajo en sala de servidores implica tareas con elevada carga física estática y dinámica:

- **Manipulación de servidores y equipos pesados**: los servidores de rack pueden pesar entre 15 y 30 kg (en el caso de nodos con múltiples GPU, el peso puede superar los 25 kg). La manipulación de estos equipos sin ayudas mecánicas (brazos extractores de rack, carros de transporte) puede producir lesiones lumbares. El Real Decreto 487/1997 sobre manipulación manual de cargas establece que los pesos superiores a 25 kg en condiciones ideales, o menores en condiciones desfavorables (espacio restringido, altura de elevación inadecuada), requieren evaluación específica y medidas preventivas.
- **Cableado en rack**: la instalación de cables en la parte superior de los racks (que pueden alcanzar 2,2 metros) exige posturas forzadas de los miembros superiores, con elevación de brazos por encima del nivel del hombro durante periodos prolongados.
- **Trabajo con pantallas de visualización**: el personal de monitorización y operaciones de NOC puede pasar jornadas completas frente a múltiples monitores, con los riesgos asociados de fatiga visual, síndrome de visión por computadora y trastornos musculoesqueléticos del cuello y hombros.

### 4.4 Riesgo de caída

Los suelos técnicos elevados (raised floors) son una solución habitual para el paso del cableado y la distribución del aire frío en centros de datos. Las baldosas son removibles y, cuando se extraen para labores de mantenimiento, crean huecos de entre 30 y 80 cm de profundidad. La caída a estas cavidades puede producir traumatismos en extremidades inferiores. Igualmente, el acceso a los racks de mayor altura mediante escaleras portátiles presenta riesgos de caída si no se utilizan escaleras homologadas con sistemas de estabilización.

### 4.5 Riesgo de campos electromagnéticos

La Directiva 2013/35/UE, transpuesta por el Real Decreto 299/2016, regula la exposición de los trabajadores a campos electromagnéticos. En los entornos de IA, las fuentes relevantes son los cables de alimentación de alta corriente, los transformadores de los SAI y los propios circuitos de distribución de potencia. En condiciones normales de operación, los niveles no suelen superar los valores límite de exposición (VLE), pero deben evaluarse en las cercanías de los transformadores y de los SAI de gran potencia, especialmente para trabajadoras embarazadas, donde los niveles de acción son más restrictivos.

### 4.6 Estrés térmico en salas de servidores

La norma técnica **ASHRAE TC 9.9** define cuatro clases de entornos para equipos de TI (A1 a A4) con diferentes rangos de temperatura y humedad. La clase A1 (entornos de precisión) establece una temperatura de operación recomendada entre 18 y 27°C con una humedad relativa de entre el 20 y el 80 %. Sin embargo, en las zonas del pasillo caliente, la temperatura del aire de retorno puede superar los 40-45°C, lo que puede generar estrés térmico para el personal que trabaja en esa zona durante periodos prolongados. Las medidas preventivas incluyen la limitación del tiempo de permanencia en zonas de pasillo caliente, la rotación de trabajadores, el suministro de agua y la monitorización de la temperatura corporal en tareas de larga duración.

---

## 5. Evaluación de riesgos en instalaciones de sistemas de IA

### 5.1 Metodología de evaluación

La evaluación de riesgos es el proceso mediante el cual el empresario obtiene la información necesaria para decidir si es preciso adoptar medidas preventivas y, en caso afirmativo, cuáles. El método más extendido en España para evaluaciones generales es el propuesto por el **Instituto Nacional de Seguridad y Salud en el Trabajo (INSST)**, basado en la estimación conjunta de la probabilidad de que el peligro se materialice y la severidad del daño resultante.

El proceso tiene tres fases:

1. **Identificación de peligros**: recorrido sistemático por el lugar de trabajo, entrevistas con los trabajadores y revisión de los procedimientos existentes para detectar todas las fuentes potenciales de daño.
2. **Estimación del riesgo**: para cada peligro identificado, se estima la probabilidad (baja, media, alta) y la severidad del daño (ligeramente dañino, dañino, extremadamente dañino). La combinación de ambas variables produce un nivel de riesgo: trivial, tolerable, moderado, importante o intolerable.
3. **Valoración**: se decide si el riesgo es aceptable o si requiere acción preventiva. Los riesgos importantes e intolerables requieren actuación inmediata; los moderados, planificación a corto plazo.

### 5.2 Ejemplo de matriz de riesgos para instalación de servidores GPU

| Peligro identificado | Probabilidad | Severidad | Nivel de riesgo | Medida preventiva prioritaria |
|---|---|---|---|---|
| Contacto eléctrico en sustitución de PSU | Media | Extremadamente dañino | Importante | Procedimiento de trabajo en tensión, habilitación del trabajador |
| Descarga de gas extintor con personal en sala | Baja | Extremadamente dañino | Importante | Señal de prealarma, protocolo de evacuación, simulacros |
| Lesión lumbar por manipulación de servidor | Alta | Dañino | Importante | Uso de carro de transporte, formación en manipulación |
| Caída a hueco de suelo técnico | Media | Dañino | Moderado | Señalización, cierre provisional del hueco, calzado de seguridad |
| Fatiga visual en trabajo de monitorización | Alta | Ligeramente dañino | Tolerable | Pausas, ajuste de pantallas, vigilancia de la salud |
| Estrés térmico en pasillo caliente | Media | Dañino | Moderado | Limitación del tiempo de exposición, rotación |

### 5.3 Medidas preventivas por nivel de riesgo

La jerarquía de controles, tal como establece el artículo 15 de la LPRL, prioriza las medidas en el siguiente orden:

- **Eliminación**: suprimir el peligro en origen (por ejemplo, diseñar el CPD con pasillo caliente cerrado para eliminar la exposición del personal al aire caliente).
- **Sustitución**: reemplazar lo peligroso por algo que no lo sea o que lo sea menos (sustituir la refrigeración por agua caliente con refrigeración líquida directa al procesador elimina la necesidad de sistemas de extinción gaseosa en la zona de racks).
- **Controles técnicos**: barreras físicas, enclavamientos eléctricos, sistemas de detección precoz de incendio (VESDA, detección aspirativa de partículas).
- **Controles administrativos**: procedimientos escritos, permisos de trabajo, formación, señalización, limitación del tiempo de exposición.
- **Equipos de protección individual (EPI)**: última línea de defensa, cuando los controles anteriores no eliminan el riesgo residual.

### 5.4 EPIs específicos para entornos de IA

- **Guantes dieléctricos** (clase 00 a clase 4 según IEC 60903): para trabajos en proximidad de partes activas de la instalación eléctrica.
- **Calzado de seguridad con resistencia eléctrica** (categoría ESD/antiestática): fundamental en sala de servidores para evitar descargas electrostáticas que puedan dañar componentes y para proteger al trabajador frente a contactos eléctricos accidentales.
- **Protección ocular para trabajos con fibra óptica**: los conectores de fibra óptica pueden emitir radiación láser invisible (clase 1 o superior) que puede causar daño irreversible en la retina. Se deben utilizar gafas con filtro específico para la longitud de onda del sistema y nunca mirar directamente al extremo de un conector sin verificar previamente que la fibra no está activa.
- **Faja lumbar** y ayudas mecánicas para manipulación de cargas: no sustituyen a la técnica correcta de manipulación, pero reducen el riesgo en operaciones inevitables con cargas pesadas.
- **Protección auditiva**: en salas con alta densidad de ventiladores, el nivel de ruido puede superar los 85 dB(A), umbral a partir del cual el Real Decreto 286/2006 exige medidas preventivas.

---

## 6. Gestión de residuos electrónicos (RAEE)

### 6.1 Marco normativo

La **Directiva 2012/19/UE** del Parlamento Europeo y del Consejo, sobre residuos de aparatos eléctricos y electrónicos (RAEE), establece el marco europeo para la gestión de estos residuos. Su principal mecanismo es la responsabilidad ampliada del productor: los fabricantes e importadores de aparatos eléctricos y electrónicos son responsables de financiar la recogida, tratamiento, recuperación y eliminación ambientalmente correcta de los RAEE generados por sus productos.

En España, la Directiva fue transpuesta por el **Real Decreto 110/2015**, de 20 de febrero, sobre residuos de aparatos eléctricos y electrónicos. Este reglamento establece:

- Las **categorías de aparatos** sujetos a la norma (diez categorías, entre las que se incluyen los equipos informáticos y de telecomunicaciones bajo los que se clasifican los servidores, almacenamiento y equipos de red).
- Los **objetivos de recogida y valorización** que deben alcanzarse, expresados como porcentaje del peso promedio de aparatos puestos en el mercado en los tres años precedentes.
- Las obligaciones de los **productores** (registro en el Registro de Productores de Aparatos Eléctricos y Electrónicos, financiación del sistema), los **distribuidores** (recogida en tienda, sistema de un-por-uno) y los **poseedores** (entrega a puntos de recogida autorizados o a distribuidores).
- Los requisitos de **gestión** por parte de los gestores autorizados: descontaminación previa (extracción de componentes peligrosos como condensadores con PCB, mercurio, baterías), preparación para reutilización cuando sea posible, y reciclaje del resto.

### 6.2 Categorías de RAEE generadas en instalaciones de IA

Una instalación de IA de ciclo de vida completo genera de forma habitual las siguientes categorías de RAEE:

- **Servidores y equipos de rack**: chasis, placas base, procesadores, tarjetas GPU, módulos de memoria, fuentes de alimentación. Contienen metales preciosos (oro, plata, paladio en conectores y circuitos) recuperables, así como plomo en soldaduras antiguas y arsénico en semiconductores compuestos. Se clasifican como RAEE categoría 2 (pequeños equipos de tecnología de la información y las telecomunicaciones) o categoría 3 (equipos de informática y telecomunicaciones).
- **Sistemas de almacenamiento**: discos duros magnéticos, unidades de estado sólido (SSD) y cintas magnéticas. Antes de su entrega como RAEE, deben someterse a un proceso certificado de destrucción de datos (borrado seguro según estándar NIST 800-88, o destrucción física del soporte) para garantizar la confidencialidad de la información.
- **Baterías de sistemas UPS**: las baterías de plomo-ácido de los SAI tradicionales son el tipo más común, pero los sistemas modernos están incorporando baterías de litio (LFP, NMC). Las baterías de plomo-ácido están reguladas por el Real Decreto 106/2008 (pilas y acumuladores), que establece su recogida separada y el objetivo del 45% de reciclaje. Las baterías de litio se clasifican como **residuo peligroso** y requieren un tratamiento diferenciado.
- **Equipos de red**: switches, routers, módulos transceptores (SFP, QSFP), patch panels. Contienen metales raros (indio en pantallas de equipos de gestión, cobalto en baterías de backup de configuración) y deben gestionarse como RAEE.
- **Equipos de climatización**: las unidades de precisión (CRAC, CRAH) contienen gases refrigerantes sujetos al Reglamento (UE) 517/2014 sobre gases fluorados, que exige su recuperación por personal certificado antes del desguace del equipo.

### 6.3 Volumen global de RAEE

Según el **Global E-waste Monitor 2020** publicado por la UNU (Universidad de las Naciones Unidas), la OIT y la UIT, en 2019 se generaron **53,6 millones de toneladas métricas** de RAEE en todo el mundo, lo que representa un aumento del 21% respecto a 2014. Solo se documentó la recogida y reciclaje correcto del 17,4% de ese total. El valor de los materiales contenidos en los RAEE generados en 2019 se estimó en 57.000 millones de dólares. La Unión Europea es la región con mayor tasa de recogida por habitante, pero aun así en 2019 solo reciclaba correctamente el 42,5% de los RAEE generados.

El crecimiento de los sistemas de IA está contribuyendo a acelerar este flujo de residuos, dado que los ciclos de renovación del hardware de aceleración son especialmente cortos: las generaciones de GPU de entrenamiento se suceden cada 18-24 meses, y los operadores de grandes clústeres renuevan sus infraestructuras antes del final de la vida útil técnica del hardware para no quedarse rezagados en capacidad de computación.

### 6.4 Protocolo de gestión de baterías de litio

Las baterías de litio presentan riesgos específicos que requieren un protocolo de gestión diferenciado:

- **Almacenamiento previo a la entrega**: deben almacenarse en contenedores de seguridad ignífugos, en lugares frescos y secos, alejados de materiales inflamables. El estado de carga debe mantenerse entre el 30 y el 50% para reducir el riesgo de reacción exotérmica.
- **Identificación y etiquetado**: cada batería debe estar identificada como residuo peligroso (código LER 16 06 05 para baterías de litio no especificadas en otra categoría) y etiquetada conforme al Reglamento (CE) 1272/2008 (CLP).
- **Transporte**: el transporte de baterías de litio como mercancía peligrosa está regulado por el ADR (Acuerdo Europeo sobre Transporte de Mercancías Peligrosas por Carretera), clase 9, con restricciones específicas según el estado de la batería (intacta, dañada, defectuosa).
- **Entrega a gestor autorizado**: solo pueden entregarse a gestores de residuos peligrosos autorizados por la comunidad autónoma correspondiente. No pueden depositarse en puntos limpios municipales que no estén habilitados para residuos peligrosos.
- **Baterías dañadas o con signos de hinchamiento**: se consideran especialmente peligrosas y requieren manejo con guantes resistentes a productos químicos y almacenamiento en contenedores de arena o vermiculita, con notificación inmediata al responsable de seguridad.

---

## 7. Plan de emergencia en centros de datos

### 7.1 Estructura del plan de emergencia

Un plan de emergencia (o plan de autoprotección, según el Real Decreto 393/2007, norma básica de autoprotección) para un centro de datos con sistemas de IA debe incluir:

**a) Organización de la respuesta a emergencias**

Define los roles y responsabilidades en situación de emergencia: jefe de emergencia, jefe de intervención, equipo de primera intervención (EPI), equipo de segunda intervención (ESI), equipo de alarma y evacuación (EAE) y equipo de primeros auxilios (EPA). En centros de datos pequeños, una misma persona puede asumir varios roles, pero siempre debe existir un responsable claramente designado.

**b) Procedimientos de actuación**

Para cada tipo de emergencia identificada (incendio, fallo eléctrico, inundación, amenaza de bomba, fallo de refrigeración), el plan debe describir la secuencia de acciones a realizar, quién las realiza, en qué orden y con qué medios. Los procedimientos deben ser concisos, estar disponibles en formato físico en los puntos clave del centro y conocerse de memoria por el personal con roles de emergencia.

**c) Medios de protección**

Inventario actualizado de: sistemas de detección de incendio, extintores (ubicación, tipo, fecha de revisión), sistemas de extinción fija, pulsadores de alarma, luces de emergencia, señalización de vías de evacuación, equipos de primeros auxilios (botiquines, desfibriladores externos automatizados) y equipos de comunicación (megafonía, radiocomunicación).

### 7.2 Drill de evacuación

El plan de autoprotección exige la realización periódica de simulacros de evacuación. En un centro de datos, el simulacro debe contemplar el escenario específico de evacuación ante alarma de extinción gaseosa, que presenta dos particularidades:

- El retardo antes de la descarga (entre 30 y 60 segundos) hace que la evacuación deba ser inmediata y sin demora.
- La reentrada debe estar prohibida hasta la autorización expresa del jefe de emergencia, lo que requiere que el personal interiorice que no deben recoger objetos personales ni intentar salvar equipos.

Los simulacros deben registrarse documentalmente (fecha, participantes, incidencias observadas, acciones correctoras) y realizarse al menos una vez al año, incrementando la frecuencia si se detectan deficiencias.

### 7.3 Procedimientos ante fallo de refrigeración

El fallo de los sistemas de refrigeración es una de las emergencias más frecuentes en centros de datos y puede generar daños irreversibles en el hardware en cuestión de minutos si la temperatura supera los umbrales de operación. El procedimiento estándar contempla:

1. **Detección**: los sistemas de monitorización de temperatura (sensores en pasillo frío, pasillo caliente y en los propios equipos) generan alarmas cuando se superan los umbrales configurados.
2. **Evaluación**: el técnico de turno evalúa la causa (fallo de una CRAC, fallo del chiller, corte de suministro eléctrico a los equipos de climatización) y la extensión del problema.
3. **Apagado ordenado por prioridades**: si la temperatura sigue subiendo y no puede restablecerse la refrigeración en el tiempo estimado de seguridad, se procede al apagado ordenado comenzando por los sistemas de menor prioridad (entornos de desarrollo, sistemas de backup) y preservando los servicios críticos el mayor tiempo posible. El orden de apagado debe estar predefinido en el plan de continuidad.
4. **Notificación**: se activa el árbol de comunicación del plan de emergencia para informar a los responsables técnicos y de negocio.

### 7.4 Coordinación con bomberos

El plan de emergencia debe incluir información que debe trasladarse al servicio de extinción cuando acude a una emergencia en el centro de datos:

- Presencia y tipo de agente de extinción gaseosa (FM-200 o Novec 1230), zonas protegidas y estado de la descarga (si ya se ha producido o está pendiente).
- Localización de cuadros eléctricos principales y sistemas de corte de emergencia.
- Presencia de baterías de litio o de plomo-ácido y su ubicación.
- Rutas de acceso y zonas de concentración del personal evacuado.

Esta información debe estar disponible en la entrada del centro de datos en un soporte físico (tarjeta de emergencia) y transmitirse verbalmente al primer equipo de bomberos que llegue.

### 7.5 Primeros auxilios: actuación ante electrocución

La electrocución es una emergencia que puede producirse en cualquier instalación eléctrica y cuya atención correcta en los primeros minutos puede ser determinante para la supervivencia de la víctima. El protocolo es:

1. **No tocar a la víctima** si aún está en contacto con la fuente de tensión. Cortar el suministro eléctrico desde el punto de mando más cercano.
2. **Llamar al 112** inmediatamente, indicando que se trata de una electrocución.
3. **Evaluar el estado de consciencia**: llamar a la víctima, sacudir suavemente los hombros.
4. Si la víctima está inconsciente y no respira normalmente, iniciar la **reanimación cardiopulmonar (RCP)**: 30 compresiones torácicas seguidas de 2 ventilaciones de rescate, a un ritmo de 100-120 compresiones por minuto.
5. **Utilizar el desfibrilador externo automatizado (DEA)** en cuanto esté disponible, siguiendo las instrucciones del dispositivo sin interrumpir la RCP más que el tiempo imprescindible para la aplicación del choque.
6. Continuar hasta que lleguen los servicios de emergencia, la víctima muestre signos de vida o el reanimador no pueda continuar físicamente.

---

## 8. Actividades prácticas

### Actividad 1: Evaluación de riesgos en sala de servidores

El alumnado recibirá un plano y una descripción detallada de una sala de servidores ficticia equipada con racks de GPU para entrenamiento de modelos de IA. Deberá identificar un mínimo de ocho peligros, clasificarlos aplicando la metodología del INSST (probabilidad x severidad), elaborar una tabla de valoración de riesgos y proponer al menos dos medidas preventivas para cada riesgo calificado como moderado, importante o intolerable. La actividad se entregará en formato de informe de evaluación de riesgos, siguiendo la estructura habitual de estos documentos.

### Actividad 2: Selección y justificación de EPIs

A partir de un listado de tareas concretas (sustitución de un servidor de 28 kg en un rack de 2,2 metros de altura, revisión de conexiones en un cuadro PDU con la instalación energizada, instalación de cable de fibra óptica multimodo en bandeja superior del rack, monitorización de sistemas durante un turno de ocho horas), el alumnado deberá seleccionar el EPI adecuado para cada tarea, indicar la normativa que lo regula (norma EN correspondiente) y justificar la elección.

### Actividad 3: Circuito de gestión de RAEE

El alumnado recibirá un inventario de residuos generados por la renovación del hardware de un clúster de IA: 40 servidores en rack con sus componentes, 12 módulos de batería de litio de SAI, 6 unidades de almacenamiento en red (NAS) y 200 metros de cableado de fibra óptica. Deberá clasificar cada tipo de residuo (RAEE, residuo peligroso, residuo no peligroso), identificar el código LER correspondiente, determinar el circuito de gestión correcto para cada categoría y elaborar un borrador del documento de aceptación de residuos que deberá firmar el gestor autorizado.

### Actividad 4: Simulacion de emergencia

En parejas, el alumnado elaborará el procedimiento de actuación ante un fallo total de refrigeración en una sala de servidores de IA de 500 kW de carga instalada. El procedimiento debe incluir: el árbol de decisión (qué hacer si el fallo se detecta en horario de guardia, si el operador está solo, si el sistema de extinción está activado simultáneamente), el orden de apagado de sistemas por prioridad, el texto de la notificación de emergencia que se comunicaría a los responsables, y una lista de verificación post-emergencia para la reactivación ordenada de los sistemas.

---

## 9. Referencias

- **Ley 31/1995, de 8 de noviembre, de Prevención de Riesgos Laborales.** Boletín Oficial del Estado, núm. 269, de 10 de noviembre de 1995. Disponible en: https://www.boe.es/eli/es/l/1995/11/08/31/con

- **Real Decreto 39/1997, de 17 de enero, por el que se aprueba el Reglamento de los Servicios de Prevención.** BOE núm. 27, de 31 de enero de 1997. Disponible en: https://www.boe.es/eli/es/rd/1997/01/17/39/con

- **Real Decreto 486/1997, de 14 de abril, por el que se establecen las disposiciones mínimas de seguridad y salud en los lugares de trabajo.** BOE núm. 97, de 23 de abril de 1997. Disponible en: https://www.boe.es/eli/es/rd/1997/04/14/486/con

- **Real Decreto 488/1997, de 14 de abril, sobre disposiciones mínimas de seguridad y salud relativas al trabajo con equipos que incluyen pantallas de visualización.** BOE núm. 97, de 23 de abril de 1997. Disponible en: https://www.boe.es/eli/es/rd/1997/04/14/488/con

- **Real Decreto 614/2001, de 8 de junio, sobre disposiciones mínimas para la protección de la salud y seguridad de los trabajadores frente al riesgo eléctrico.** BOE núm. 148, de 21 de junio de 2001. Disponible en: https://www.boe.es/eli/es/rd/2001/06/08/614/con

- **Real Decreto 110/2015, de 20 de febrero, sobre residuos de aparatos eléctricos y electrónicos.** BOE núm. 45, de 21 de febrero de 2015. Disponible en: https://www.boe.es/eli/es/rd/2015/02/20/110/con

- **Instituto Nacional de Seguridad y Salud en el Trabajo (INSST).** Portal de recursos técnicos y NTP (Notas Técnicas de Prevención). Ministerio de Trabajo y Economía Social. Disponible en: https://www.insst.es

- **INSST. NTP 330: Sistema simplificado de evaluación de riesgos de accidente.** Centro Nacional de Condiciones de Trabajo. Disponible en: https://www.insst.es/documents/94886/326962/ntp_330.pdf

- **Forti, V., Balde, C. P., Kuehr, R., y Bel, G. (2020). The Global E-waste Monitor 2020: Quantities, flows and the circular economy potential.** United Nations University / United Nations Institute for Training and Research, International Telecommunication Union, and International Solid Waste Association. Bonn/Geneva/Rotterdam. Disponible en: https://www.itu.int/en/ITT-D/Climate-Change/Pages/Global-E-waste-Monitor.aspx

- **ASHRAE TC 9.9 (2021). Thermal Guidelines for Data Processing Environments, Fifth Edition.** American Society of Heating, Refrigerating and Air-Conditioning Engineers. Atlanta, GA. Información disponible en: https://www.ashrae.org/technical-resources/bookstore/datacom-series
