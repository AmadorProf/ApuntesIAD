---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD6 · Prevención de riesgos y gestión de residuos | MP01 · Implementación de sistemas de IA'
footer: 'Apuntes de IA y Datos'
---

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

<!-- _class: lead -->

# UD6 · Prevención de riesgos y gestión de residuos

**MP01 · Implementación de sistemas de IA**
Apuntes de IA y Datos

---

## Objetivos de la unidad

Al finalizar esta unidad el alumnado sera capaz de:

- Identificar los riesgos laborales propios de entornos de infraestructura de IA: salas de servidores, CPD y puestos de trabajo tecnico.
- Aplicar criterios ergonomicos en la configuracion del puesto de trabajo con pantallas de visualizacion de datos (PVD).
- Actuar de forma correcta ante emergencias siguiendo el Plan de Autoproteccion del centro.
- Clasificar, separar y gestionar los residuos de aparatos electricos y electronicos (RAEE) conforme a la normativa vigente.
- Reconocer los materiales peligrosos presentes en equipos de IA e infraestructura de CPD y aplicar los procedimientos de manipulacion adecuados.
- Integrar principios de economia circular en las decisiones de mantenimiento y renovacion de infraestructuras.

> **Resultado de aprendizaje EC6:** Interviene con criterios de seguridad, previniendo riesgos laborales y gestionando residuos conforme a la normativa aplicable.

---

## Marco normativo PRL — legislacion principal

### Normas de referencia obligatoria en trabajos tecnicos con equipos de IA

| Norma | Ambito de aplicacion | Obligacion principal |
|---|---|---|
| **Ley 31/1995 LPRL** | Todo el territorio nacional; todos los sectores | Garantizar la seguridad y salud de los trabajadores; evaluacion de riesgos, planificacion preventiva y vigilancia de la salud |
| **RD 39/1997** | Reglamento de los Servicios de Prevencion | Modalidades de organizacion preventiva; conciertos con servicios de prevencion ajenos |
| **RD 486/1997** | Lugares de trabajo (incluidos CPD y salas de servidores) | Condiciones minimas de seguridad: iluminacion, temperatura, ventilacion, orden y limpieza |
| **RD 488/1997** | Puestos con pantallas de visualizacion de datos (PVD) | Evaluacion ergonomica, pausas, revision oftalmologica a cargo de la empresa |
| **RD 614/2001** | Riesgos electricos en locales y equipos de alta y baja tension | Procedimientos de trabajo en proximidad de instalaciones electricas; distancias de seguridad |

---

## Marco normativo PRL — normativa complementaria y europea

### Directivas EU y normas tecnicas aplicables

| Norma | Tipo | Contenido clave para infraestructura IA |
|---|---|---|
| **Directiva 89/391/CEE** | Directiva marco europea PRL | Base de la Ley 31/1995; principios generales de prevencion |
| **Directiva 2006/25/CE** | Radiaciones opticas artificiales | Leds de alta intensidad en armarios de servidores; pantallas de alta luminancia |
| **UNE-EN ISO 9241-5:1999** | Ergonomia de sistemas interactivos | Requisitos de disposicion del puesto de trabajo con PVD: alturas, distancias, angulos |
| **UNE-EN ISO 9241-303:2012** | Requisitos ergonomicos para pantallas | Reflectancia, parpadeo, luminancia, contraste minimo para monitores tecnicos |
| **UNE-EN 60204-1** | Seguridad de maquinaria — equipamiento electrico | Cableado y protecciones en armarios rack y bancadas de servidores |
| **RD 110/2015** | Transposicion Directiva 2012/19/UE RAEE | Gestion de residuos de aparatos electricos y electronicos en Espana |

---

## Riesgos especificos en salas de servidores y CPD (I)

### Riesgos electricos y fisicos

| Riesgo | Consecuencia potencial | Medida preventiva |
|---|---|---|
| Contacto directo con armario rack abierto sin bloqueo | Electrocucion, quemaduras graves | Procedimiento LOTO (Lock Out / Tag Out); EPI dielectricos (guantes clase 00 a 500 V, calzado de seguridad) |
| Alta tension en SAI (UPS) — baterias de 480 V en CPD tier III-IV | Arco electrico, fibrilacion ventricular | Acceso restringido a personal autorizado; senalizacion de riesgo electrico (IEC 60417-5036) |
| Cableado deficiente o sin proteccion en bandejas | Cortocircuito, incendio | Revision periodica con termografia infrarroja; cumplimiento del Reglamento Electrotecnico de Baja Tension (REBT, RD 842/2002) |
| Ruido continuo de sistemas de refrigeracion CRAC/CRAH | Hipoacusia profesional (>85 dB) | Medicion con sonometro calibrado; EPI auditivos (tapones EN 352-2 o cascos EN 352-1) si nivel supera 80 dB(A) |
| Temperatura extremadamente baja en pasillos frios (< 15 °C) | Hipotermia, trastornos musculoesqueleticos | Ropa de abrigo tecnica; limitacion del tiempo de permanencia; calefaccion de pasillo caliente |

---

## Riesgos especificos en salas de servidores y CPD (II)

### Riesgos quimicos y mecanicos

| Riesgo | Consecuencia potencial | Medida preventiva |
|---|---|---|
| Refrigerantes fluorados (HFC R-410A, R-32) en unidades CRAC | Asfixia por desplazamiento de oxigeno; efecto invernadero F-Gas | Detectores de gas fijos (sensor IR o electroquimico); formacion en manejo de refrigerantes segun Reglamento UE 517/2014 (F-Gas) |
| Acido sulfurico en baterias de plomo-acido de SAI | Quemaduras quimicas; emision de hidrogeno explosivo | Ventilacion forzada; EPI quimico (gafas, guantes nitrilo); ficha de datos de seguridad (FDS/SDS) accesible en sala |
| Manipulacion manual de servidores (12-25 kg por unidad) | Lumbalgia, hernia discal | Limitacion de carga manual a 25 kg (Guia INSST sobre MMC); uso de elevador de rack o carro porta-rack ergonomico |
| Polvo acumulado en filtros y bandejas de cable | Contaminacion de vias respiratorias; incendio de polvo electricamente conductor | Limpieza periodica con aspiradora HEPA y aire a presion regulado; uso de mascarilla FFP2 durante la limpieza |
| Caida al mismo nivel por cableado en suelo tecnico | Fracturas, contusiones | Suelo tecnico con tapas seguras; senalizacion de obstaculos; orden permanente |

---

## Ergonomia en el puesto de trabajo tecnico (I)

### Ajuste del puesto con pantalla de visualizacion de datos

> La norma **RD 488/1997** obliga a evaluar ergonomicamente todos los puestos con PVD utilizados de forma habitual. La referencia tecnica es la serie **ISO 9241**.

| Parametro | Valor recomendado | Norma de referencia |
|---|---|---|
| Altura del asiento | Muslos paralelos al suelo; pies apoyados en el suelo o en reposapiés | ISO 9241-5; Guia INSST NTP 602 |
| Altura del borde superior del monitor | A la altura de los ojos o ligeramente por debajo (0–15° de inclinacion hacia abajo) | ISO 9241-303; RD 488/1997 Anexo |
| Distancia pantalla–ojos | Entre 50 cm y 70 cm segun tamano de monitor (referencia: 60 cm para monitor de 24") | ISO 9241-303 |
| Inclinacion del teclado | Entre 0° y 15°; muñecas rectas al escribir | ISO 9241-410 |
| Angulo del codo al usar el raton | 90°–110°; hombros relajados | NTP 602 INSST |
| Posicion lumbar | Respaldo con apoyo en la curva lumbar (lordosis natural) | EN 1335-1 (sillas de oficina) |

---

## Ergonomia en el puesto de trabajo tecnico (II)

### Lista de comprobacion del puesto (checklist PVD)

| Elemento | Condicion correcta | Indicador de problema |
|---|---|---|
| Silla | Altura ajustada; respaldo inclina 100–110°; apoyabrazos opcionales a altura del codo | Pies colgando; espalda separada del respaldo |
| Monitor | Sin reflejos directos de ventanas o luminarias; brillo ajustado al entorno | Reflejo visible en pantalla; brillo maximo activado |
| Teclado | Sobre la mesa, no elevado; sin reposamuñecas rigido durante la escritura | Muñecas en extension forzada |
| Documentos | Atril portadocumentos al lado del monitor a la misma distancia | Giro repetido de cuello hacia papel en mesa |
| Iluminacion | Iluminancia entre 300 y 500 lux en plano de trabajo; sin deslumbramiento directo | Sombras sobre teclado; luminaria frente al operador |
| Espacio bajo la mesa | Libre de obstaculos; permite cambios de postura | Cajones, cableado o cajas obstruyendo el espacio |

---

## Perifericos ergonomicos — tipos y beneficios (I)

### Equipamiento de apoyo para la reduccion de carga musculoesqueletica

| Periferico | Descripcion | Beneficio ergonomico principal |
|---|---|---|
| Teclado ergonomico partido (split) — Logitech ERGO K860, Microsoft Sculpt | Division en dos mitades con angulo de separacion; inclinacion negativa opcional | Reduce la pronacion del antebrazo y la desviacion cubital de la muñeca hasta un 54% (estudio Cornell Ergonomics Lab) |
| Raton vertical — Logitech MX Vertical, Anker Vertical | Angulo de agarre de 57° sobre el plano horizontal | Posicion neutra del antebrazo (como dar un apreton de manos); reduce tension en musculo pronador redondo |
| Trackball central — Kensington Expert Mouse | Bola giratoria sin desplazamiento del dispositivo | Elimina el movimiento de traslacion del brazo; util en espacios de trabajo reducidos en CPD |
| Soporte elevador de portatil — Roost V3, Rain Design mStand | Eleva el portatil entre 10 y 20 cm sobre la superficie de trabajo | Permite colocar la pantalla a la altura de los ojos al usar teclado externo; evita flexion cervical |
| Monitor ajustable en altura con brazo articulado — Ergotron LX | Movimiento vertical de 13 cm, inclinacion y giro en 360° | Permite ajuste personalizado segun la altura del usuario y la tarea (lectura vs. tecleo) |

---

## Perifericos ergonomicos — tipos y beneficios (II)

### Superficies y accesorios complementarios

| Accesorio | Norma o referencia | Aplicacion en entorno tecnico IA |
|---|---|---|
| Reposapiés ajustable en altura e inclinacion | ISO 9241-5 (se recomienda cuando el asiento no se puede bajar mas) | Imprescindible cuando el tecnico trabaja en bancos de trabajo de altura fija en sala de rack |
| Reposamuñecas de gel (uso en reposo, no durante escritura) | NTP 602 INSST — Evitar si genera presion sobre el tunel carpiano | Soporte durante pausas; material de gel de baja densidad preferible a espuma rigida |
| Escritorio de altura regulable (sit-stand) — Flexispot EC5, IKEA BEKANT | ISO 9241-5; recomendacion de la Agencia Europea para la Seguridad y Salud en el Trabajo (EU-OSHA) | Permite alternar posicion sentada y de pie; reduccion de tiempo sedentario en jornadas de monitorizacion prolongada |
| Almohadilla de muñeca para raton | NTP 602 — Grosor maximo 2 cm para no elevar muñeca sobre el nivel del raton | Entornos de oficina tecnica donde el tecnico alterna tareas de CPD con trabajo en escritorio |

---

## Fatiga visual y sindrome de vision de computadora (SVC)

### Sintomas, causas y medidas preventivas

> El **Sindrome de Vision de Computadora (SVC)** o Computer Vision Syndrome (CVS) afecta al 50–90% de los usuarios de pantalla segun la American Optometric Association (AOA). En tecnicos de IA con jornadas de 8 h frente a multiples monitores el riesgo es especialmente elevado.

**Sintomas principales:** sequia ocular, ardor, vision borrosa intermitente, cefalea frontal, sensacion de cuerpo extraño, diplopía transitoria.

**Causas:** frecuencia de parpadeo reducida (de 15 a 5 veces/min frente a pantalla), deslumbramiento, temperatura de color inadecuada, dioptrías no corregidas para distancia intermedia.

| Medida preventiva | Frecuencia o valor optimo | Beneficio demostrado |
|---|---|---|
| Regla 20-20-20 | Cada 20 minutos, mirar a 20 pies (6 m) durante 20 segundos | Relajacion del musculo ciliar; reduce tension acomodativa |
| Temperatura de color de la pantalla | 4000–5000 K durante el dia; 2700–3500 K por la tarde/noche | Reduce estimulacion de celulas melanopsina (reloj circadiano) |
| Iluminacion ambiente | 300–500 lux; fuente lateral o posterior; CCT 3000–4000 K | Evita contraste excesivo entre pantalla y entorno |
| Filtro de luz azul (software) | f.lux, Night Light de Windows 11, Monotone en macOS | Reduccion de emision en 415–455 nm hasta un 40% |
| Hidratacion ambiental | Humedad relativa entre 45% y 65% en sala tecnica | Reduce evaporacion lagrimal y sequia ocular |
| Revision oftalmologica especifica para PVD | Anual o segun convenio colectivo; a cargo del empresario (RD 488/1997, art. 4) | Deteccion de presbicia, astigmatismo no corregido para 60 cm |

---

## Fatiga visual — pausas activas y movilizacion

### Protocolo de pausas en jornada de monitorizacion de sistemas IA

| Pausa | Duracion | Frecuencia | Actividad recomendada |
|---|---|---|---|
| Micropausa ocular (regla 20-20-20) | 20 segundos | Cada 20 minutos | Fijar la vista en un punto a 6 m de distancia; parpadear conscientemente |
| Pausa de movilizacion cervical y hombros | 2–3 minutos | Cada 45–60 minutos | Rotaciones suaves de cuello; elevacion y descenso de hombros; retraccion escapular |
| Pausa activa completa | 5–10 minutos | Cada 2 horas | Levantarse, caminar, estiramiento de isquiotibiales y gemelos; hidratacion |
| Pausa de desconexion de pantalla | 30 minutos | En la jornada de 8 horas (obligatorio segun RD 488/1997 y convenios sectoriales) | Tiempo de almuerzo fuera del puesto; evitar uso de smartphone durante este tiempo |

> **Atencion:** El RD 488/1997 establece que el empresario debe organizar la actividad de forma que las pausas queden integradas en la jornada, no como tiempo recuperable.

---

## Ambiente saludable en CPD y sala tecnica

### Parametros ambientales de confort y seguridad

| Parametro | Rango optimo (trabajo de oficina/tecnico) | Rango operativo CPD (ASHRAE A1) | Instrumento de medida | Norma de referencia |
|---|---|---|---|---|
| Temperatura del aire | 21–23 °C | 18–27 °C en pasillo frio | Termometro seco calibrado; sonda PT100 | RD 486/1997 Anexo III; ASHRAE 55-2020 |
| Humedad relativa | 45–65% | 20–80% (sin condensacion) | Higrómetro capacitivo | ASHRAE 55-2020; ISO 7933 |
| Nivel de ruido | < 65 dB(A) en trabajo cognitive; < 80 dB(A) umbral de accion | 75–90 dB(A) en sala de CPD activa | Sonometro clase 2 (IEC 61672) | RD 286/2006 (ruido); UNE-EN ISO 9612 |
| Iluminancia en plano de trabajo | 300–500 lux (trabajo en pantalla); 500 lux (tecleo y lectura de documentos) | 300 lux en pasillos de rack | Luxometro calibrado (ISO/CIE 10527) | RD 486/1997 Anexo IV; EN 12464-1 |
| CO2 ambiente | < 1000 ppm (bienestar cognitivo optimo) | < 1200 ppm | Sensor NDIR (infrarrojo no dispersivo) | RITE 2007 (calidad del aire interior) |
| Velocidad del aire | < 0,15 m/s (para evitar corrientes molestas) | 1–3 m/s en pasillos de rack (refrigeracion) | Anemometro de hilo caliente | RD 486/1997; ASHRAE 62.1 |

---

## Actuacion ante emergencias — Plan de Autoproteccion

### Marco legal y estructura del plan

La **Norma Basica de Autoproteccion (NBA, RD 393/2007)** obliga a los titulares de actividades que pueden generar situaciones de emergencia a elaborar, implantar y mantener un **Plan de Autoproteccion**.

**Estructura minima del Plan de Autoproteccion en instalaciones con CPD:**

1. Identificacion de la actividad y descripcion del edificio e instalaciones.
2. Inventario de riesgos: electrico, incendio, derrame quimico, fallo de climatizacion.
3. Medios de proteccion: extintores, BIE, pulsadores de alarma, sistemas de deteccion de incendios (EN 54), deteccion de gas.
4. Plan de actuacion ante emergencias: conato, emergencia parcial, emergencia general, evacuacion.
5. Implantacion: formacion del Equipo de Primera Intervencion (EPI), simulacros anuales obligatorios.
6. Mantenimiento de la vigencia del plan: revision tras cualquier cambio en la instalacion.

---

## Actuacion ante emergencias — protocolos especificos

### Tipos de emergencia en infraestructura de IA y respuesta

| Tipo de emergencia | Accion inmediata | Responsable | Equipamiento utilizado |
|---|---|---|---|
| Conato de incendio en rack de servidores | Accionar pulsador de alarma mas cercano; aplicar extintor CO2 (clase E) sin cortar el suministro electrico manualmente | Tecnico presente (Equipo de Primera Intervencion) | Extintor CO2 5 kg (EN 3-7); senalizacion de evacuacion |
| Incendio generalizado en sala CPD | Activacion de sistema de extincion gaseosa automatico (agente FM-200 / Novec 1230); evacuacion inmediata; cierre de puertas cortafuego RF-120 | Jefe de Emergencia; Bomberos (112) | Sistema HFC-227ea o FK-5-1-12 (Novec 1230) instalado segun EN 15004 |
| Fallo electrico / arco en cuadro de distribucion | No intervenir sin EPIs dielectricos; desconectar suministro desde interruptor general exterior; llamar a electricista cualificado; 112 si hay heridos | Electricista autorizado (habilitacion de la empresa instaladora) | Guantes dielectricos clase 00 o clase 0; pértiga de maniobra |
| Derrame de refrigerante liquido (propilen glicol) | Ventilar el area; absorber con material absorbente (vermiculita); depositar en contenedor de residuo peligroso | Tecnico de mantenimiento | EPI quimico: guantes nitrilo, gafas splash; absorbente industrial |
| Accidente con lesionados | Llamar al 112; no mover al herido si hay sospecha de traumatismo; iniciar RCP si no hay pulso y hay DEA disponible | Cualquier trabajador; Primeros Auxilios | DEA (desfibrilador externo automatico), botiquin tipo B (Orden SSI/3007/2009) |

---

## Residuos de aparatos electricos y electronicos (RAEE) — marco legal

### Normativa aplicable en Espana y Union Europea

El **Real Decreto 110/2015** transpone la **Directiva 2012/19/UE** sobre residuos de aparatos electricos y electronicos. Establece obligaciones para productores, distribuidores, gestores y usuarios.

**Principios fundamentales del RD 110/2015:**
- Responsabilidad ampliada del productor (RAP): el fabricante financia la recogida y el tratamiento.
- Obligacion de recogida separada: prohibido depositar RAEE en contenedor de fraccion resto.
- Objetivos de recogida para Espana: 65% del peso medio de AEE comercializados en los tres años anteriores (desde 2019).
- Categorias del Anexo I del RD 110/2015: 6 categorias a partir de 2019 (antes 10).

| Categoria (Anexo I RD 110/2015) | Descripcion | Ejemplos en entorno CPD/IA |
|---|---|---|
| 1. Equipos de intercambio de temperatura | Sistemas de refrigeracion, aire acondicionado | Unidades CRAC/CRAH, chillers de precision |
| 2. Pantallas y monitores | Monitores, pantallas de visualizacion | Monitores de gestion de red, KVM displays |
| 3. Lamparas | Lamparas de descarga, LED | Fluorescentes T8 de sala de servidores, emergencias |
| 4. Grandes equipos | Servidores, UPS, SAI, equipos de red | Rack de servidores, switches de nucleo, SAI trifasico |
| 5. Pequeños equipos | Equipos de usuario, accesorios | Ratones, teclados, cables, discos duros |
| 6. Pequeños equipos de informatica y telecomunicaciones | Portatiles, tablets, telefonos IP | Portatiles de administracion, telefonos VoIP |

---

## RAEE — proceso de gestion en instalaciones de IA

### Etapas del ciclo de gestion de residuos tecnologicos

| Etapa | Descripcion | Responsable | Documentacion generada |
|---|---|---|---|
| 1. Identificacion y baja del inventario | El tecnico marca el equipo como fuera de servicio en el CMDB (Ej.: iTop, Device42, ServiceNow) | Tecnico de sistemas / Responsable de IT | Hoja de baja del activo; etiqueta "RAEE — pendiente de gestion" |
| 2. Recogida en el punto de origen | El equipo se traslada al Punto de Recogida Interno (PRI) habilitado en las instalaciones | Tecnico de IT | Albarand interno de traslado |
| 3. Clasificacion y separacion | Separacion por categoria RAEE segun Anexo I RD 110/2015; separacion de pilas y baterias (RD 1207/2006) | Responsable de residuos del centro | Registro de clasificacion |
| 4. Almacenaje temporal en contenedor homologado | Contenedores etiquetados segun RD 110/2015; tiempo maximo de almacenaje: 12 meses (Art. 17 RD 110/2015) | Responsable de medio ambiente | Etiqueta de contenedor con fecha de inicio de almacenaje |
| 5. Entrega a gestor autorizado | Contrato con Sistema Colectivo de Responsabilidad Ampliada (SCRA) autorizado: Ecofimática, Ecoasimelec, TTE o gestor de residuos peligrosos autorizado por CCAA | Responsable de compras / medio ambiente | Documento de Identificacion del Residuo (DI o e-DI electronico) |
| 6. Cierre del ciclo — certificado de tratamiento | El gestor emite certificado de tratamiento correcto y datos de valorizacion (% recuperado) | Gestor autorizado | Certificado de destruccion de datos (si aplica: ENS, RGPD) + certificado de tratamiento RAEE |

---

## Materiales peligrosos en equipos de IA e infraestructura

### Identificacion, riesgo y tratamiento correcto

| Material | Donde se encuentra en infraestructura IA | Riesgo principal | Clasificacion como residuo | Tratamiento correcto |
|---|---|---|---|---|
| Pasta termica de silicona (compound) | Entre CPU/GPU y disipador en servidores de IA (ej.: Thermal Grizzly Kryonaut, Arctic MX-4) | Irritacion cutanea leve; contaminante ambiental si vierte en grandes cantidades | Residuo no peligroso (salvo formulaciones con metales pesados) | Trapo impregnado a contenedor de residuo no peligroso; verificar FDS especifica |
| Metal liquido (galio-indio) — pasta termica extrema | Disipadores de alto rendimiento en GPU de entrenamiento (ej.: Conductonaut) | Corrosivo para aluminio; puede dañar componentes electronicos si se derrama | Residuo peligroso si contiene galio > umbral CER | Gestor de residuos metalicos especiales; nunca mezclar con RAEE comun |
| Refrigerante liquido — propilen glicol (PGW) | Circuitos de refrigeracion liquida directa (Direct Liquid Cooling) en servidores AI | Bajo en toxicidad humana; contaminante biologico en altas concentraciones en EDAR | No peligroso pero recomendado tratamiento especifico | Entrega a planta de tratamiento de aguas o gestor de residuos liquidos |
| Baterias de litio-ion (Li-ion) — SAI y UPS | SAI de torre y rack (APC Smart-UPS, Eaton 9PX), baterias de backup de servidores blade | Riesgo de incendio termico si se perforan o sobrecargan; LiPF6 toxico en electrolito | Residuo peligroso — RD 1207/2006 (pilas y acumuladores) | Entrega a punto de recogida especifico para baterias; nunca desechar en RAEE general |
| Mercurio — lamparas fluorescentes (CCFL) | Iluminacion de sala de servidores antigua; retroiluminacion de monitores LCD anteriores a 2012 | Neurotoxina; vapor de mercurio en caso de rotura | Residuo peligroso — Hg | Gestion especializada; contenedor rigido estanco; nunca romper las lamparas |
| Acido sulfurico — baterias de plomo-acido | SAI de gran potencia (10–200 kVA) con baterias VRLA o abiertas | Quemadura quimica grave; emision de H2 (gas inflamable) durante carga | Residuo peligroso | Neutralizacion con bicarbonato sodico en derrames; entrega a gestor autorizado (CER 16 06 01) |

---

## Economia circular en infraestructuras de IA

### Jerarquia de residuos aplicada a equipos tecnologicos

> La **Directiva 2008/98/CE** (Marco de Residuos) y su transposicion en Espana mediante la **Ley 7/2022 de residuos y suelos contaminados** establecen la siguiente jerarquia, de mayor a menor preferencia:

**1. Prevencion** — Alargar la vida util del equipo: actualizacion de componentes (ampliacion de RAM, sustitucion de HDD por SSD, nueva tarjeta de red) en lugar de sustituir el servidor completo.

**2. Preparacion para la reutilizacion** — Recertificacion de servidores usados: fabricantes como Dell (Dell Certified Refurbished), HPE (HPE Renew) y Lenovo (Lenovo Certified Refurbished) ofrecen servidores reacondicionados con garantia. Reduce la huella de carbono hasta un 60% respecto a fabricacion nueva.

**3. Reciclaje** — Valorizacion material: recuperacion de oro, plata, paladio y cobre en placas base (1 tonelada de placas contiene ~300 g de oro frente a 5 g/tonelada en mineria primaria).

**4. Valorizacion energetica** — Solo cuando no es posible el reciclaje material: incineracion con recuperacion de energia en instalaciones autorizadas.

**5. Eliminacion** — Vertedero como ultima opcion, y solo para residuos previamente tratados. **Prohibido el vertido de RAEE sin tratamiento previo** (RD 110/2015, Art. 6).

**Iniciativas sectoriales:** The Green Grid (TGG), SDIA (Sustainable Digital Infrastructure Alliance), programa Circular Electronics de la Comision Europea (2023).

---

## Actividad practica — auditoria ergonomica del puesto de trabajo

### Procedimiento de auditoria con lista de comprobacion

**Objetivo:** Cada tecnico auditara su propio puesto de trabajo (o el del aula de practicas) aplicando la siguiente lista de comprobacion ergonomica, identificando los puntos de mejora y proponiendo acciones correctoras priorizadas.

**Instrucciones:**

1. Sientate en tu puesto habitual sin ajustar nada previamente.
2. Completa la lista de comprobacion con "Correcto / Incorrecto / No aplica" para cada elemento.
3. Para cada elemento marcado como "Incorrecto", describe el problema observado y propone una medida correctora concreta.
4. Estima el coste aproximado de cada medida (sin coste / bajo < 50 EUR / medio 50–300 EUR / alto > 300 EUR).
5. Ordena las acciones por prioridad: primero las de mayor impacto ergonomico y menor coste.

**Elementos a verificar (referencia: NTP 602 INSST y RD 488/1997 Anexo):**
- Altura del asiento, profundidad del asiento, apoyo lumbar
- Altura y distancia del monitor, reflejo en pantalla
- Posicion del teclado y el raton
- Iluminacion ambiente y ausencia de deslumbramiento
- Orden y espacio libre bajo la mesa
- Accesibilidad al boton de emergencia y extintor mas cercano

**Entrega:** informe de auditoria de una pagina con tabla de hallazgos y plan de accion priorizad.

---

## Puntos clave de la unidad

- La **Ley 31/1995 LPRL** es el pilar del sistema preventivo en Espana; en puestos con PVD se complementa con el **RD 488/1997**, que obliga a evaluacion ergonomica, pausas y vigilancia de la salud visual a cargo del empresario.

- Los CPD y salas de servidores concentran riesgos **electricos** (alta tension en SAI), **fisicos** (ruido >85 dB, temperatura extrema) y **quimicos** (refrigerantes F-Gas, baterias de plomo-acido y litio). Cada riesgo requiere EPIs y procedimientos especificos.

- La ergonomia del puesto tecnico se regula por la serie **ISO 9241**: altura de monitor a nivel de los ojos, distancia de 50–70 cm, muñecas rectas y apoyo lumbar son los parametros criticos. La **regla 20-20-20** es la herramienta basica para prevenir el SVC.

- Ante cualquier emergencia se sigue el **Plan de Autoproteccion (RD 393/2007)**: activar alarma, aplicar extintor CO2 para fuego electrico, evacuar y llamar al 112 si hay heridos.

- Los RAEE se gestionan segun el **RD 110/2015**: recogida separada, clasificacion por categoria, almacenaje maximo 12 meses en contenedor homologado y entrega a gestor autorizado con Documento de Identificacion del Residuo.

- La **economia circular** prioriza prevenir y reutilizar antes que reciclar: un servidor recertificado por HPE Renew o Dell Certified Refurbished reduce la huella de carbono hasta un 60% respecto a la fabricacion de uno nuevo.

---

## Criterios de evaluacion — EC6

| Criterio | Descripcion | Indicadores de logro |
|---|---|---|
| CE6a — Normativa PRL | Identifica la legislacion aplicable a su puesto de trabajo tecnico con PVD y a la sala de servidores | Cita correctamente LPRL, RD 488/1997, RD 486/1997 y RD 614/2001 con su ambito de aplicacion |
| CE6b — Ergonomia | Aplica criterios ergonomicos en la configuracion del puesto y demuestra conocimiento de los parametros ISO 9241 | Ajusta correctamente el puesto en la lista de comprobacion practica; identifica > 4 parametros con sus valores optimos |
| CE6c — Fatiga visual | Describe y aplica medidas para prevenir el sindrome de vision de computadora | Explica la regla 20-20-20; nombra > 3 medidas preventivas con su frecuencia correcta |
| CE6d — Emergencias | Actua correctamente ante una emergencia simulada siguiendo el Plan de Autoproteccion | Identifica el tipo de extintor correcto para fuego electrico; sigue el protocolo de evacuacion sin errores en simulacro |
| CE6e — Gestion de RAEE | Clasifica correctamente los residuos tecnologicos y describe el proceso de gestion conforme al RD 110/2015 | Asigna correctamente > 5 tipos de RAEE a sus categorias; describe las 6 etapas del proceso con el responsable de cada una |
| CE6f — Materiales peligrosos | Identifica los materiales peligrosos presentes en equipos de IA y aplica el procedimiento de manipulacion adecuado | Reconoce el riesgo de al menos 4 materiales (pasta termica, baterias Li-ion, refrigerante, bateria plomo-acido) y describe su tratamiento correcto |
| CE6g — Economia circular | Justifica decisiones de mantenimiento y renovacion de infraestructura aplicando la jerarquia de residuos | Ordena correctamente los 5 niveles de la jerarquia y propone alternativas de reutilizacion para al menos 2 tipos de equipo |

---

<!-- _class: lead -->

# UD6 completada

**Prevencion de riesgos, ergonomia y gestion de residuos en infraestructuras de IA**

[← Volver a MP01](../)


---

<!-- nav-slide -->

## Navegación

[← UD5 · Resolución de incidencias en…](../UD5_Resolucion-incidencias/) &nbsp;·&nbsp; [Volver al módulo](../)
