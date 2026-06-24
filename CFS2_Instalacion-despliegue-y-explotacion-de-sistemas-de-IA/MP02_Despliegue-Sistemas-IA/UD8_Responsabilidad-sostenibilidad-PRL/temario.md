# UD8 · Responsabilidad, sostenibilidad, PRL y gestión de residuos en despliegues de IA

---

## 1. Introducción

El técnico que instala, configura y pone en servicio infraestructura de inteligencia artificial no opera en el vacío: trabaja en entornos físicos que implican riesgos laborales reales y genera impactos ambientales que van mucho más allá del perímetro del centro de datos. La responsabilidad profesional en despliegues de IA abarca tres dimensiones inseparables: la seguridad y salud de las personas que intervienen en la instalación y operación del sistema, el ciclo de vida de los equipos que materializan esa infraestructura, y la huella ambiental que el funcionamiento continuo del sistema produce. Ignorar cualquiera de estas dimensiones no solo constituye una infracción normativa, sino también una negligencia profesional con consecuencias económicas, penales y reputacionales.

La Directiva 2006/42/CE sobre máquinas y el Real Decreto 486/1997 sobre lugares de trabajo, junto con la Ley 31/1995 de Prevención de Riesgos Laborales (PRL), establecen el marco legal aplicable a las instalaciones donde se trabaja con equipos de cómputo de alta densidad. Los centros de procesamiento de datos (CPD) presentan una combinación específica de riesgos: alta tensión eléctrica, manipulación manual de cargas pesadas —servidores de hasta 30 kg, racks de más de 100 kg—, condiciones ambientales controladas que implican diferencias térmicas bruscas, y trabajo en altura para la instalación de equipos en armarios de 42U o más. El técnico debe conocer estos riesgos, aplicar las medidas preventivas correspondientes y saber cómo actuar ante un accidente.

La gestión de residuos de aparatos eléctricos y electrónicos (RAEE) es el segundo eje de responsabilidad. La obsolescencia tecnológica en el sector de la IA es notablemente rápida: los ciclos de reemplazo de GPU y aceleradores de inferencia se sitúan actualmente entre tres y cinco años, lo que genera volúmenes crecientes de residuos con contenido en materiales críticos —cobre, oro, indio, cobalto— y sustancias peligrosas —plomo, mercurio, berilio, retardantes de llama bromados—. La Directiva 2012/19/UE sobre RAEE, transpuesta al ordenamiento español mediante el Real Decreto 110/2015, regula la responsabilidad del productor, las obligaciones del distribuidor y los procedimientos de recogida y tratamiento selectivo. El técnico que retira equipos obsoletos debe conocer estos procedimientos y documentar adecuadamente la cadena de custodia de los residuos.

La tercera dimensión es la huella ambiental del despliegue en funcionamiento. La inteligencia artificial es intensiva en energía: el entrenamiento de modelos de gran escala puede consumir el equivalente en carbono a varios centenares de vuelos transatlánticos. El serving continuo de modelos en producción, aunque menos dramático que el entrenamiento, acumula consumo energético de forma constante. Los indicadores estándar del sector —PUE (Power Usage Effectiveness) y WUE (Water Usage Effectiveness)— permiten medir la eficiencia del CPD. Los sistemas de certificación voluntaria como ISO 50001, LEED y BREEAM proporcionan marcos para mejorar y acreditar esa eficiencia ante clientes, reguladores e inversores. Esta unidad cubre todos estos aspectos de forma integrada, con el objetivo de que el técnico adopte una perspectiva de responsabilidad integral sobre su trabajo.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Identificar los riesgos laborales específicos del trabajo en CPDs (riesgo eléctrico, manipulación de cargas, trabajo en altura, condiciones ambientales) y aplicar las medidas preventivas establecidas por la Ley 31/1995 y la normativa de desarrollo.
2. Describir los procedimientos de instalación segura de equipos en rack, incluyendo el uso de herramientas de elevación, la comprobación del estado del cableado y la verificación de conexiones de puesta a tierra.
3. Clasificar los residuos generados en un despliegue de infraestructura de IA según la normativa RAEE y describir el procedimiento de gestión desde la retirada del equipo hasta la entrega a un gestor autorizado.
4. Calcular el PUE y el WUE de un CPD a partir de datos de consumo y comparar los valores obtenidos con los índices de referencia del sector.
5. Describir los requisitos de las certificaciones ISO 50001, LEED y BREEAM aplicadas a centros de datos, e identificar los controles técnicos que contribuyen a su obtención.
6. Aplicar los principios de la economía circular al ciclo de vida de los equipos de IA, identificando opciones de reutilización, reacondicionamiento y reciclaje como alternativas a la obsolescencia planificada.
7. Calcular la huella de carbono de un despliegue de IA, identificar los factores de emisión pertinentes y describir mecanismos de compensación y reducción de emisiones.
8. Reconocer la responsabilidad profesional del técnico en la cadena de custodia de residuos y en el cumplimiento de la normativa ambiental, distinguiendo las responsabilidades propias de las del productor y el distribuidor.

---

## 3. Prevención de riesgos laborales en instalaciones de IA

### 3.1 Marco normativo aplicable

El marco de PRL aplicable a las instalaciones de infraestructura de IA en España está constituido por varias capas normativas. La **Ley 31/1995 de Prevención de Riesgos Laborales** es el texto de referencia: establece los principios generales de la acción preventiva, la obligación del empresario de garantizar la seguridad y la salud de los trabajadores, y los derechos y obligaciones de los propios trabajadores.

La ley se desarrolla mediante reglamentos específicos. El **Real Decreto 486/1997** regula las condiciones mínimas de seguridad y salud en los lugares de trabajo: orden, limpieza, temperatura, iluminación, espacio disponible. El **Real Decreto 485/1997** establece los requisitos de señalización de seguridad y salud. El **Real Decreto 487/1997** regula la manipulación manual de cargas, estableciendo los límites de peso recomendados y las técnicas seguras de manejo. El **Real Decreto 614/2001** sobre riesgo eléctrico es especialmente relevante en el contexto de CPDs.

El técnico debe conocer también la normativa de equipos de protección individual (EPI) establecida en el **Real Decreto 773/1997**, que regula las condiciones de selección, uso y mantenimiento de los EPI requeridos para cada tarea. Los EPI habituales en trabajos en CPDs incluyen: calzado de seguridad con puntera antiaplastamiento (clase S2 o S3), guantes aislantes para trabajos en proximidad a equipos bajo tensión, gafas de protección para trabajos que generen proyecciones, y arnés de seguridad para trabajos en altura superiores a dos metros.

### 3.2 Riesgo eléctrico en CPDs

El riesgo eléctrico es el de mayor gravedad potencial en un CPD. Los sistemas de distribución de potencia de un CPD moderno operan con tensiones de 208 V, 400 V o incluso 480 V en sistemas de alta densidad. Las UPS (Uninterruptible Power Supplies) almacenan energía suficiente para causar electrocuciones mortales incluso con la alimentación principal cortada. Las PDU (Power Distribution Units) de alta densidad pueden suministrar corrientes de varias decenas de amperios.

Los principios del trabajo eléctrico seguro, establecidos en el Real Decreto 614/2001, son:

- **Supresión de la tensión**: siempre que sea posible, los trabajos se realizan sin tensión. El procedimiento de las cinco reglas de oro garantiza que el equipo esté verdaderamente sin tensión antes de intervenir: desconectar, prevenir cualquier posible realimentación, verificar la ausencia de tensión, poner a tierra y en cortocircuito, y señalizar la zona de trabajo.
- **Trabajos en tensión**: solo están permitidos para personal acreditado según UNE-EN 50110-1, con procedimientos específicos y EPI adecuados. En el contexto de un CPD, esto aplica principalmente al cableado de PDUs activas.
- **Trabajos en proximidad**: se aplica cuando el técnico no interviene directamente sobre elementos en tensión pero trabaja a una distancia inferior a las distancias de seguridad establecidas.

La **puesta a tierra** es la medida de protección fundamental en instalaciones eléctricas. En la instalación de racks, es obligatorio verificar que la continuidad del conductor de protección (PE) está garantizada desde cada equipo hasta la barra de puesta a tierra del cuadro de distribución. La resistencia de la puesta a tierra debe medirse con un telurometro antes de energizar el rack.

### 3.3 Manipulación manual de cargas

Los servidores de rack modernos pueden pesar entre 15 kg (servidores de 1U de baja densidad) y más de 30 kg (servidores de 4U con múltiples GPU). Las UPS de piso pueden superar los 200 kg. El **Real Decreto 487/1997** establece que el peso máximo recomendado para el levantamiento manual es de 25 kg en condiciones ideales, reduciéndose según la postura, la frecuencia y las características del trabajador.

En la práctica, la instalación de servidores en rack requiere con frecuencia trabajar por encima del nivel de los hombros o por debajo de las rodillas, lo que reduce significativamente el límite de carga recomendado. Las medidas preventivas incluyen:

- Uso de **elevadores de rack** (también llamados lift tables o server lifts) para elevar los equipos hasta la altura de instalación sin esfuerzo manual.
- Técnica correcta de levantamiento: espalda recta, carga pegada al cuerpo, levantamiento con piernas, sin giros de tronco.
- Trabajo en equipo para cargas superiores a 25 kg, distribuyendo el esfuerzo entre dos o más personas con comunicación verbal coordinada.
- Verificación del recorrido libre de obstáculos antes de transportar cualquier equipo pesado.

Los **carritos de transporte** con capacidad para racks completos son imprescindibles en despliegues a escala. Un rack de 42U con equipamiento completo puede superar los 800 kg; su movimiento requiere carritos específicos con mecanismos de freno y control de inclinación.

### 3.4 Trabajo en altura y condiciones ambientales

En CPDs, el trabajo en altura se produce al instalar equipos en la parte superior de racks de 2,1 m o más, o al tender cableado por bandejas elevadas o plenum superior. El **Real Decreto 2177/2004** sobre trabajos en altura establece que, a partir de 2 metros, deben utilizarse equipos de protección colectiva (barandillas, redes) o, cuando no sea posible, equipos de protección individual (arnés, línea de vida).

Para trabajos en racks, la opción más habitual es el uso de **escaleras industriales de tijera** certificadas según EN 131, con peldaños antideslizantes y zapatas de apoyo adecuadas al tipo de suelo del CPD (típicamente suelo técnico elevado). La escalera debe inmovilizarse o ser sujetada por un segundo operario durante el trabajo.

Las condiciones ambientales del CPD presentan otro tipo de riesgo: la temperatura de los pasillos fríos se mantiene habitualmente entre 18 y 27 °C, mientras que los pasillos calientes pueden superar los 40 °C. La transición brusca entre zonas genera riesgos de confort térmico y, en exposición prolongada al pasillo caliente, riesgo de golpe de calor. Los trabajos de mantenimiento en zonas de alta temperatura deben limitarse en duración y realizarse con hidratación adecuada.

### 3.5 Ergonomía en el puesto de trabajo en CPD

El trabajo de operación y monitorización de sistemas de IA implica largas jornadas frente a pantallas de visualización. El **Real Decreto 488/1997** sobre pantallas de visualización establece los requisitos ergonómicos del puesto: distancia de visión entre 40 y 70 cm, pantalla sin reflejos, altura de la pantalla a nivel o ligeramente por debajo del nivel de los ojos, silla regulable en altura con soporte lumbar, y descansos periódicos de al menos cinco minutos por cada hora de trabajo continuo frente a la pantalla.

En los puestos de Control Room de CPD, la evaluación ergonómica debe considerar adicionalmente el ruido ambiental —el nivel de presión sonora en CPDs puede superar los 75 dB(A), lo que requiere el uso de protección auditiva para exposiciones prolongadas— y la iluminación, que debe garantizar al menos 500 lux en los puestos de trabajo según EN 12464-1.

---

## 4. Gestión de residuos de aparatos eléctricos y electrónicos (RAEE)

### 4.1 Marco normativo RAEE

La **Directiva 2012/19/UE sobre residuos de aparatos eléctricos y electrónicos (RAEE)** —también conocida como Directiva WEEE, por sus siglas en inglés— establece el marco europeo para la recogida, el tratamiento y el reciclado de estos residuos. Su objetivo es minimizar el impacto ambiental de los RAEE mediante la aplicación del principio de responsabilidad ampliada del productor.

En España, la directiva se transpone mediante el **Real Decreto 110/2015 de 20 de febrero, sobre residuos de aparatos eléctricos y electrónicos**. Este reglamento establece:

- **Responsabilidad del productor**: los fabricantes e importadores son responsables de la recogida y el tratamiento de sus productos al final de su vida útil. Deben financiar sistemas colectivos de recogida o sistemas individuales propios.
- **Obligaciones de los distribuidores**: están obligados a recoger gratuitamente los RAEE que les entreguen los consumidores al comprar un producto equivalente (principio de uno por uno) o en sus puntos de recogida.
- **Obligaciones de los gestores**: los gestores de RAEE deben estar inscritos en el Registro de Establecimientos Industriales y cumplir las prescripciones técnicas de tratamiento establecidas en el Real Decreto.

Para el técnico que trabaja en despliegues de IA, las obligaciones más relevantes son: la correcta clasificación de los residuos generados, el almacenamiento temporal en condiciones adecuadas, la documentación de la entrega a gestor autorizado y la conservación de los documentos de seguimiento durante al menos cinco años.

### 4.2 Categorías de RAEE en infraestructura de IA

La normativa RAEE clasifica los aparatos en categorías. Los equipos de infraestructura de IA caen principalmente en la **categoría 2: pequeños equipos de tecnologías de la información y telecomunicaciones** (servidores, switches, routers) y **categoría 6: equipos de tecnologías de la información y telecomunicaciones de grandes dimensiones** (bastidores, UPS de gran potencia, sistemas de refrigeración).

| Equipo | Categoría RAEE | Sustancias peligrosas relevantes |
|---|---|---|
| Servidores de rack (CPU) | Categoría 2 | Plomo en soldaduras, berilio en conectores, retardantes bromados |
| Tarjetas GPU / aceleradores | Categoría 2 | Indio (ITO), oro en contactos, plomo en soldaduras BGA |
| Baterías de UPS | Categoría especial (pilas/acumuladores) | Plomo-ácido, litio (nuevas UPS) |
| Sistemas de refrigeración | Categoría 4 (grandes) | Refrigerantes HFC, aceite de compresores |
| Cableado de cobre | Residuo no RAEE (cable eléctrico) | PVC en aislamiento |
| Pantallas y monitores | Categoría 2 | Mercurio (fluorescentes), indio |

### 4.3 Procedimiento de gestión de RAEE en despliegues

El procedimiento de gestión de RAEE en la retirada de equipos obsoletos sigue estas fases:

**Fase 1 — Inventario y clasificación**: antes de retirar el equipo, se elabora un inventario de cada unidad a retirar, con número de serie, marca, modelo, categoría RAEE y estimación del peso. Este inventario es la base de la documentación de seguimiento.

**Fase 2 — Borrado seguro de datos**: antes de entregar cualquier equipo a un gestor de RAEE, todos los soportes de almacenamiento deben someterse a un proceso certificado de borrado seguro conforme a estándares como NIST SP 800-88 (Guidelines for Media Sanitization) o DoD 5220.22-M. Los discos con datos sensibles o clasificados pueden requerir destrucción física mediante trituración o desmagnetización certificada. El certificado de borrado o destrucción debe adjuntarse a la documentación de entrega del RAEE.

**Fase 3 — Almacenamiento temporal**: los RAEE deben almacenarse en zonas específicamente habilitadas, separados de otros residuos, protegidos de la lluvia y del acceso no autorizado, sobre superficies impermeables que eviten la contaminación del suelo en caso de derrame. El período máximo de almacenamiento temporal en la empresa es de un año.

**Fase 4 — Entrega a gestor autorizado**: los RAEE se entregan a un gestor inscrito en el Registro de Establecimientos Industriales de la comunidad autónoma correspondiente. La entrega se documenta mediante el **Documento de Identificación del Residuo (DIR)**, que el gestor debe emitir y cuya copia debe conservar el productor del residuo durante cinco años.

**Fase 5 — Seguimiento y cierre**: el gestor autorizado entrega al productor del residuo un certificado de gestión que acredita el tratamiento ambientalmente correcto del equipo. Este certificado cierra el ciclo documental y es la evidencia de cumplimiento ante una posible inspección.

### 4.4 Obsolescencia planificada y economía circular

La **obsolescencia planificada** es la práctica de diseñar productos con una vida útil artificialmente limitada para estimular su sustitución. En el sector de IA, se manifiesta de múltiples formas: incompatibilidad entre generaciones de drivers, fin del soporte de software para modelos de hardware todavía funcionales, o diseños que dificultan la reparación o la actualización de componentes.

La **economía circular** propone un modelo alternativo basado en tres principios: diseñar sin residuos, mantener los productos y materiales en uso el mayor tiempo posible, y regenerar los sistemas naturales. Aplicados a la infraestructura de IA, estos principios se traducen en:

- **Reuso**: servidores retirados de producción pueden reutilizarse en entornos de desarrollo, pruebas o inferencia de baja prioridad.
- **Reacondicionamiento (refurbishing)**: empresas especializadas limpian, prueban y certifican el correcto funcionamiento de equipos de segunda mano, extendiendo su vida útil cinco o más años adicionales.
- **Actualización de componentes (upgrading)**: aumentar la RAM, sustituir discos HDD por SSD o ampliar la capacidad de red puede prolongar la vida útil de un servidor sin necesidad de reemplazarlo.
- **Reciclaje al final de vida**: cuando el equipo ya no puede reutilizarse, el reciclaje recupera materiales valiosos (cobre, aluminio, metales preciosos) y gestiona adecuadamente las sustancias peligrosas.

---

## 5. Huella de carbono de los despliegues de IA

### 5.1 Indicadores de eficiencia energética: PUE y WUE

El **PUE (Power Usage Effectiveness)** es el indicador estándar de eficiencia energética de un CPD. Se calcula como:

```
PUE = Energía total consumida por el CPD / Energía consumida por la carga TI
```

Un PUE de 1.0 significaría que toda la energía consumida va a la carga TI, sin pérdidas en refrigeración, distribución eléctrica o iluminación —un ideal teórico inalcanzable—. Un PUE de 2.0 significa que por cada vatio consumido por los servidores se consume otro vatio en infraestructura de soporte. Los valores de referencia actuales del sector son:

| Nivel de eficiencia | PUE | Comentario |
|---|---|---|
| Excelente | < 1.2 | Grandes CPDs de hiperescaladores con free-cooling |
| Bueno | 1.2 – 1.5 | CPDs modernos con sistemas de refrigeración eficientes |
| Medio | 1.5 – 2.0 | CPDs convencionales sin optimización activa |
| Ineficiente | > 2.0 | CPDs antiguos o con diseño deficiente |

El **WUE (Water Usage Effectiveness)** mide el consumo de agua del CPD en relación con la energía consumida por la carga TI:

```
WUE = Litros de agua consumidos anualmente / MWh consumidos por la carga TI
```

Los sistemas de refrigeración evaporativa y las torres de refrigeración húmedas consumen grandes cantidades de agua. Un WUE de 1.0 L/kWh es considerado bueno; valores superiores a 2.0 L/kWh indican un uso ineficiente del agua.

### 5.2 Cálculo de la huella de carbono de un despliegue

La huella de carbono de un despliegue de IA comprende las emisiones directas e indirectas asociadas a todo el ciclo de vida del sistema. Se estructura típicamente en tres alcances (scopes) siguiendo el protocolo GHG (Greenhouse Gas Protocol):

**Scope 1 — Emisiones directas**: combustión de grupos electrógenos de respaldo, fugas de gases refrigerantes con alto potencial de calentamiento global (GWP).

**Scope 2 — Emisiones indirectas por energía**: emisiones asociadas a la electricidad consumida. Se calculan multiplicando el consumo eléctrico en kWh por el factor de emisión de la red eléctrica del país donde opera el CPD. En España, MITECO publica anualmente el factor de emisión de la red eléctrica peninsular, que en los últimos años se sitúa entre 0.15 y 0.25 kg CO₂eq/kWh como resultado del creciente peso de las renovables.

```
Emisiones Scope 2 = Consumo TI (kWh) × PUE × Factor emisión red (kg CO₂eq/kWh)
```

**Scope 3 — Otras emisiones indirectas**: fabricación de los equipos (embodied carbon), transporte, y gestión de residuos al final de vida. La fabricación de un servidor de alta densidad con múltiples GPU puede generar entre 1.500 y 3.000 kg de CO₂eq, lo que puede representar el 20-40% de las emisiones totales del ciclo de vida.

### 5.3 Reducción y compensación de emisiones

Las estrategias de reducción de emisiones en despliegues de IA se articulan en orden de prioridad:

1. **Eficiencia computacional**: optimizar los modelos para que requieran menos cómputo (quantización, pruning, destilación) reduce directamente el consumo eléctrico.
2. **Eficiencia del CPD**: mejorar el PUE mediante diseño de pasillo frío/caliente, free-cooling, economizadores y refrigeración líquida.
3. **Descarbonización de la energía**: contratar Garantías de Origen (GOs) o Power Purchase Agreements (PPAs) de energía renovable; situar el CPD en regiones con alta penetración de renovables.
4. **Programación temporal**: ejecutar cargas de entrenamiento durante horas de baja demanda o alta generación renovable (carbon-aware computing, herramientas como Carbon-Aware SDK de la Green Software Foundation).
5. **Compensación de emisiones residuales**: mediante la compra de créditos de carbono verificados por estándares como VCS (Verified Carbon Standard) o Gold Standard, que financian proyectos de reducción de emisiones o captura de carbono verificados por terceros.

---

## 6. Certificaciones de sostenibilidad para centros de datos

### 6.1 ISO 50001 — Sistemas de gestión de la energía

La norma **ISO 50001:2018** especifica los requisitos para establecer, implementar, mantener y mejorar un sistema de gestión de la energía (SGEn). Su objetivo es ayudar a las organizaciones a mejorar continuamente su desempeño energético mediante la revisión sistemática del uso, consumo y eficiencia energética.

Los requisitos principales aplicados a un CPD incluyen: establecimiento de una política energética, nombramiento de un responsable de energía, realización de una revisión energética que identifique los usos significativos de la energía (en un CPD: sistemas de refrigeración, UPS, iluminación), definición de objetivos y metas de ahorro cuantificados, y seguimiento de indicadores de desempeño energético (IDEn) como el PUE mensual.

La certificación ISO 50001 permite a los operadores de CPD demostrar su compromiso con la eficiencia energética ante clientes y reguladores, acceder a beneficios fiscales en algunos países, y cumplir con la obligación de auditoría energética cuatrienal establecida por la Directiva de Eficiencia Energética (transpuesta en España mediante el Real Decreto 56/2016).

### 6.2 LEED para centros de datos

**LEED (Leadership in Energy and Environmental Design)** es el sistema de certificación de edificios sostenibles más extendido a nivel mundial, desarrollado por el U.S. Green Building Council (USGBC). Aunque originalmente diseñado para edificios de uso general, dispone de guías específicas para centros de datos. Evalúa el edificio en categorías como:

- **Sitio sostenible**: minimización del impacto sobre el terreno, gestión de aguas pluviales.
- **Eficiencia hídrica**: reducción del consumo de agua en sistemas de refrigeración.
- **Energía y atmósfera**: eficiencia energética del edificio, uso de energías renovables, no uso de refrigerantes con alto GWP.
- **Materiales y recursos**: uso de materiales reciclados y de proximidad en la construcción.
- **Calidad del ambiente interior**: confort térmico, acústico y lumínico para los trabajadores.

Los niveles de certificación son: Certificado, Plata, Oro y Platino, en función del número de puntos obtenidos. Los grandes CPDs que operan servicios de IA suelen aspirar al nivel Oro o Platino como elemento diferenciador en sus acuerdos comerciales.

### 6.3 BREEAM para centros de datos

**BREEAM (Building Research Establishment Environmental Assessment Method)** es el sistema de evaluación de sostenibilidad de edificios de referencia en Europa, desarrollado por el BRE (Building Research Establishment) del Reino Unido. Es el estándar predominante en España y el resto de Europa continental, donde los clientes institucionales y las administraciones públicas lo exigen con mayor frecuencia que LEED.

BREEAM evalúa nueve categorías: gestión, salud y bienestar, energía, transporte, agua, materiales, residuos, uso del suelo y ecología, y contaminación. Las certificaciones posibles son: Aprobado, Bueno, Muy Bueno, Excelente y Sobresaliente. BREEAM Data Centres es la versión específica para CPDs, adaptada para incorporar métricas como el PUE y el WUE.

### 6.4 Comparativa de certificaciones

| Característica | ISO 50001 | LEED | BREEAM |
|---|---|---|---|
| Alcance | Gestión energética | Edificio sostenible | Edificio sostenible |
| Origen | Internacional (ISO) | EE.UU. (USGBC) | Reino Unido (BRE) |
| Predominio geográfico | Global | América del Norte | Europa |
| Tipo de certificación | Sistema de gestión | Proyecto/edificio | Proyecto/edificio |
| Reconocimiento en España | Alto (obligatorio audit.) | Medio | Alto |
| Renovación | Anual (vigilancia) | Cada 5 años | Cada 3-5 años |
| Foco principal | Mejora continua energética | Diseño sostenible integral | Evaluación ambiental integral |

---

## 7. Responsabilidad profesional del técnico

### 7.1 Cadena de responsabilidad en el despliegue

El técnico de despliegue de IA ocupa un eslabón específico en la cadena de responsabilidad. No es el diseñador del sistema —que es responsable de la arquitectura y las decisiones de componentes—, ni el operador —que es responsable del funcionamiento continuo—, pero es responsable de la instalación conforme a las especificaciones, la seguridad del proceso de instalación y la documentación de todo lo realizado.

Las responsabilidades específicas del técnico incluyen: verificar que los equipos recibidos corresponden a lo especificado en el albarán y que no presentan daños de transporte; instalar conforme a los procedimientos documentados y a las instrucciones del fabricante; documentar cualquier desviación del procedimiento estándar con su justificación; comunicar inmediatamente cualquier anomalía detectada que pueda afectar a la seguridad o al funcionamiento; y asegurarse de que los residuos generados durante la instalación —embalajes, equipos retirados, cables sobrantes— son gestionados conforme a la normativa aplicable.

### 7.2 Documentación obligatoria en instalaciones

Toda instalación de infraestructura de IA debe quedar documentada mediante los siguientes registros:

- **Acta de instalación**: fecha, ubicación exacta (rack, unidad de rack), descripción del equipo (fabricante, modelo, número de serie), técnico responsable, y resultado de las verificaciones realizadas (conexiones, puesta a tierra, test de funcionamiento inicial).
- **Registro de mediciones eléctricas**: medición de resistencia de aislamiento, continuidad del conductor de protección y tensión de alimentación tras la instalación, firmado por el técnico.
- **Documento de entrega de RAEE**: para los equipos retirados, referencia al DIR emitido por el gestor autorizado.
- **Registro de incidencias**: cualquier anomalía detectada durante la instalación, con descripción, causa probable y acción tomada.

### 7.3 Notificación de accidentes e incidentes

La Ley 31/1995 establece la obligación del trabajador de comunicar inmediatamente cualquier situación que, a su juicio razonado, entrañe un riesgo para la seguridad y la salud de los trabajadores. Los accidentes de trabajo deben notificarse al servicio de prevención de la empresa y, si causan baja laboral, a la Seguridad Social mediante el sistema Delt@ en un plazo de cinco días hábiles desde la baja.

Los incidentes —situaciones de riesgo que no han llegado a producir daño (near misses)— deben igualmente registrarse y analizarse, ya que son la mejor oportunidad para prevenir accidentes futuros. El análisis de incidentes sigue el método del árbol de causas o el método de los "cinco porqués" para identificar las causas raíz y establecer acciones correctivas.

---

## 8. Actividades prácticas

### Actividad 1 — Evaluación de riesgos en una instalación de CPD

**Descripción**: Se proporciona al estudiante el plano de una sala CPD de pequeño-mediano tamaño con la distribución de racks, cuadros eléctricos, sistemas de refrigeración y vías de evacuación. El estudiante debe realizar una evaluación de riesgos del proceso de instalación de un nuevo rack de 4U con tres servidores GPU y una PDU de alta densidad. Debe identificar todos los riesgos presentes (eléctrico, manipulación de cargas, trabajo en altura, incendio), estimar su probabilidad e impacto, proponer las medidas preventivas correspondientes para cada riesgo y elaborar el procedimiento de trabajo seguro (PTS) para la instalación.

**Entregable**: Matriz de evaluación de riesgos (tabla) + Procedimiento de Trabajo Seguro (1-2 páginas).

**Criterios de evaluación**: Identificación completa de riesgos, adecuación de las medidas preventivas a cada riesgo identificado, coherencia del PTS con la normativa aplicable, uso correcto de la terminología de PRL.

---

### Actividad 2 — Gestión de RAEE: simulación de retirada de equipos

**Descripción**: El formador proporciona un inventario simulado de equipos a retirar de un CPD: cuatro servidores de rack de diferentes marcas y modelos, dos baterías de UPS plomo-ácido, un switch de núcleo y tres discos duros con datos sensibles. El estudiante debe: clasificar cada equipo en su categoría RAEE, elaborar el procedimiento de borrado seguro para los discos, diseñar el almacenamiento temporal de los RAEE (condiciones, contenedor, señalización), cumplimentar los formularios de entrega a gestor (DIR simulado) y describir el tratamiento ambiental adecuado para cada categoría de equipo.

**Entregable**: Informe de gestión de RAEE (3-4 páginas) con los formularios cumplimentados.

**Criterios de evaluación**: Correcta clasificación de todos los equipos, adecuación del procedimiento de borrado a la sensibilidad de los datos, cumplimentación correcta del DIR, rigor en la descripción del tratamiento ambiental.

---

### Actividad 3 — Cálculo de PUE, WUE y huella de carbono

**Descripción**: Se proporciona al estudiante una hoja de datos de un CPD ficticio con las lecturas mensuales de consumo eléctrico total, consumo de la carga TI y consumo de agua de los sistemas de refrigeración para los últimos doce meses. El estudiante debe: calcular el PUE y el WUE mensual y anual, comparar los valores con los índices de referencia del sector, calcular las emisiones de Scope 2 utilizando el factor de emisión publicado por MITECO para el año correspondiente, identificar los dos o tres meses con mayor consumo y analizar posibles causas (temperatura exterior, ocupación del CPD), y proponer tres medidas de mejora con estimación cuantitativa de la reducción de PUE y emisiones esperada.

**Entregable**: Hoja de cálculo con las métricas + informe de análisis y propuestas (2-3 páginas).

**Criterios de evaluación**: Corrección de los cálculos, interpretación adecuada de los valores obtenidos, solidez técnica de las propuestas de mejora, cuantificación del impacto esperado.

---

### Actividad 4 — Comparativa de certificaciones de sostenibilidad

**Descripción**: Una empresa está evaluando certificar su nuevo CPD destinado a servicios de IA. Dispone de presupuesto para una sola certificación y debe elegir entre ISO 50001, LEED Oro y BREEAM Excelente. El formador proporciona la descripción del CPD (ubicación en España, 500 m² de sala técnica, clientes principalmente del sector financiero y público, consumo estimado de 2 MW). El estudiante debe analizar los requisitos y costes de cada certificación, evaluar cuál se adapta mejor al perfil de clientes y al contexto regulatorio español, y elaborar una recomendación justificada con un plan de acción para la certificación seleccionada.

**Entregable**: Informe de análisis comparativo y recomendación (3-4 páginas).

**Criterios de evaluación**: Rigor del análisis comparativo, adecuación de la recomendación al contexto descrito, calidad de la justificación, concreción del plan de acción.

---

## 9. Referencias

- **Ley 31/1995, de 8 de noviembre, de Prevención de Riesgos Laborales**: texto consolidado en el BOE. Disponible en: [https://www.boe.es/buscar/act.php?id=BOE-A-1995-24292](https://www.boe.es/buscar/act.php?id=BOE-A-1995-24292)

- **Real Decreto 614/2001, de 8 de junio, sobre disposiciones mínimas para la protección de la salud y seguridad de los trabajadores frente al riesgo eléctrico**: BOE. Disponible en: [https://www.boe.es/buscar/act.php?id=BOE-A-2001-11311](https://www.boe.es/buscar/act.php?id=BOE-A-2001-11311)

- **Real Decreto 487/1997, de 14 de abril, sobre disposiciones mínimas de seguridad y salud relativas a la manipulación manual de cargas**: BOE. Disponible en: [https://www.boe.es/buscar/act.php?id=BOE-A-1997-8670](https://www.boe.es/buscar/act.php?id=BOE-A-1997-8670)

- **Real Decreto 110/2015, de 20 de febrero, sobre residuos de aparatos eléctricos y electrónicos**: BOE. Disponible en: [https://www.boe.es/buscar/act.php?id=BOE-A-2015-2549](https://www.boe.es/buscar/act.php?id=BOE-A-2015-2549)

- **Directiva 2012/19/UE del Parlamento Europeo y del Consejo sobre residuos de aparatos eléctricos y electrónicos (RAEE)**: EUR-Lex. Disponible en: [https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32012L0019](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32012L0019)

- **ISO 50001:2018 — Energy management systems — Requirements with guidance for use**: International Organization for Standardization. Disponible en: [https://www.iso.org/standard/69426.html](https://www.iso.org/standard/69426.html)

- **LEED for Data Centers — U.S. Green Building Council**: guía de aplicación de LEED a centros de datos. Disponible en: [https://www.usgbc.org/leed](https://www.usgbc.org/leed)

- **BREEAM Technical Standards for New Construction**: BRE Global. Disponible en: [https://www.breeam.com/discover/technical-standards/newconstruction/](https://www.breeam.com/discover/technical-standards/newconstruction/)

- **The Green Grid — PUE: A Comprehensive Examination of the Metric**: guía técnica de referencia para el cálculo y la interpretación del PUE. Disponible en: [https://www.thegreengrid.org/en/resources/library-and-tools/21-PUE%3A-A-Comprehensive-Examination-of-the-Metric](https://www.thegreengrid.org/en/resources/library-and-tools/21-PUE%3A-A-Comprehensive-Examination-of-the-Metric)

- **GHG Protocol — Corporate Standard**: World Resources Institute y WBCSD. Protocolo de referencia para el cálculo de la huella de carbono. Disponible en: [https://ghgprotocol.org/corporate-standard](https://ghgprotocol.org/corporate-standard)

- **MITECO — Factor de emisión de la red eléctrica española**: Ministerio para la Transición Ecológica y el Reto Demográfico. Disponible en: [https://www.miteco.gob.es/es/cambio-climatico/temas/mitigacion-politicas-y-medidas/factores_emision_CO2.aspx](https://www.miteco.gob.es/es/cambio-climatico/temas/mitigacion-politicas-y-medidas/factores_emision_CO2.aspx)

- **Green Software Foundation — Carbon-Aware SDK**: documentación del SDK para computación consciente del carbono. Disponible en: [https://greensoftware.foundation/projects/carbon-aware-sdk](https://greensoftware.foundation/projects/carbon-aware-sdk)

---

*UD8 · MP02 Despliegue de Sistemas de IA · CFS2 Instalación, despliegue y explotación de sistemas de IA*
