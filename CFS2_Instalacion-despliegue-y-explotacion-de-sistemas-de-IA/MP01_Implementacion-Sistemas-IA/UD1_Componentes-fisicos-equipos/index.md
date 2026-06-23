---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD1 · Integración de componentes físicos y equipos | MP01 · Implementación de sistemas de IA'
footer: 'CFS Instalación, despliegue y explotación de sistemas de IA (IAD)'
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

# UD1 · Integración de componentes físicos y equipos

MP01 · Implementación de sistemas de IA

---

## Objetivos de aprendizaje

Al finalizar esta unidad didáctica el alumno será capaz de:

- Identificar y clasificar los componentes de soporte físico presentes en una plataforma de IA: dispositivos de captación, plataformas IoT, sistemas embebidos, robots e infraestructura de cómputo.
- Registrar cada componente en el sistema de gestión de activos con todos los campos requeridos, garantizando su trazabilidad desde la incorporación hasta el fin de vida.
- Actualizar el registro ante modificaciones, sustituciones o nuevas incorporaciones, siguiendo la documentación técnica oficial.
- Documentar la instalación: características técnicas, incidencias y fechas.
- Manipular equipos de forma segura aplicando las normas de PRL, utilizando los EPI adecuados y previniendo riesgos eléctricos y descargas electrostáticas.
- Aplicar criterios de eficiencia energética y economía circular en la gestión del hardware.

---

## Dispositivos de captación y percepción (I)

Los sistemas de IA que operan en el mundo físico dependen de sensores capaces de traducir fenómenos reales en datos digitales procesables. La elección del dispositivo determina la calidad, la latencia y el coste del dato en origen.

### Principales familias de sensores

- **Cámaras RGB convencionales:** captura de imagen visible, empleadas en visión artificial industrial y videoanalítica.
- **Cámaras multiespectrales e hiperespectrales:** capturan bandas de longitud de onda fuera del espectro visible (NIR, SWIR, LWIR). Se usan en agricultura de precisión, inspección de materiales y detección de contaminantes.
- **LiDAR (Light Detection And Ranging):** emite pulsos láser y mide el tiempo de retorno para generar nubes de puntos 3D. Fundamental en vehículos autónomos y robótica móvil.
- **Sensores de profundidad (ToF / Structured Light):** como Intel RealSense D435i o Microsoft Azure Kinect, generan mapas de profundidad en tiempo real.
- **Micrófonos y matrices de micrófonos:** captura de audio para reconocimiento de voz, detección de anomalías sonoras en maquinaria industrial.

---

## Dispositivos de captación y percepción (II)

### Tabla comparativa de sensores habituales en IA industrial

| Dispositivo | Fabricante / Modelo | Resolución / Rango | Interfaz | Caso de uso principal |
|---|---|---|---|---|
| Camara multiespectral | MicaSense RedEdge-P | 5 bandas, 21 MP | Ethernet / USB | Agricultura de precisión (drones) |
| Camara hiperespectral | Specim FX10 | 400–1000 nm, 1024 px | CameraLink / USB3 | Inspección de calidad alimentaria |
| LiDAR rotacional | Velodyne VLP-32C | 32 canales, 200 m | Ethernet (UDP) | Navegacion autonoma en exteriores |
| LiDAR de estado solido | Ouster OS1-128 | 128 canales, 120 m | Ethernet | Robotica industrial, mapeo |
| Sensor de profundidad | Intel RealSense D435i | 1280x720, hasta 10 m | USB 3.1 Gen1 | Manipulacion robotica, pick&place |
| Termocamara | FLIR Lepton 3.5 | 160x120, -10 a 140 °C | SPI / I2C | Deteccion de anomalias termicas |

> La seleccion del sensor debe hacerse en funcion del rango espectral necesario, la resolucion requerida, las condiciones ambientales y el protocolo de comunicacion compatible con la plataforma de procesamiento.

---

## Plataformas IoT y sistemas embebidos (I)

Los sistemas embebidos ejecutan inferencia o preprocesado de datos directamente en el borde de la red (*edge computing*), reduciendo la latencia y la cantidad de datos que deben transmitirse a la nube. Las plataformas IoT coordinan la recogida y envio de datos desde multiples dispositivos.

### Criterios de seleccion

- **Potencia de computo vs. consumo energetico:** a mayor potencia, mayor consumo. Para dispositivos con bateria se prioriza la eficiencia.
- **Acelerador de IA integrado:** tensor cores, NPUs o DSPs dedicados permiten ejecutar redes neuronales con latencia aceptable sin GPU externa.
- **Conectividad:** Wi-Fi, Ethernet, 4G/5G, LoRaWAN, Zigbee, CAN bus segun el entorno industrial.
- **Temperatura de operacion:** los entornos industriales pueden requerir rangos ampliados (-40 °C a +85 °C).
- **Sistema operativo soportado:** Linux embebido, RTOS, o sistemas propietarios condicionan las herramientas de despliegue disponibles.

---

## Plataformas IoT y sistemas embebidos (II)

### Tabla de plataformas embebidas habituales en IA

| Plataforma | CPU | Acelerador IA | RAM | Consumo tipico | Caso de uso |
|---|---|---|---|---|---|
| NVIDIA Jetson Orin NX 16 GB | Cortex-A78AE (8 cores) | 1024-core Ampere GPU + 2x DLA | 16 GB LPDDR5 | 10–25 W | Inferencia en el borde, vision artificial |
| NVIDIA Jetson AGX Orin | Cortex-A78AE (12 cores) | 2048-core Ampere GPU + 2x DLA | 64 GB LPDDR5 | 15–60 W | Robotica avanzada, coches autonomos |
| Raspberry Pi CM4 | Cortex-A72 (4 cores) | — (requiere HAT externo) | Hasta 8 GB LPDDR4 | 3–7 W | Prototipado, nodos IoT de bajo coste |
| Arduino Portenta H7 | Cortex-M7 + M4 dual | — | 8 MB SDRAM | < 1 W | Microcontrolador industrial, TinyML |
| PLC Siemens S7-1500 TF | Intel Atom (x86) | TensorFlow Lite integrado | 1 GB DDR4 | 10–30 W | IA en entornos de automatizacion industrial |
| Coral Dev Board | Cortex-A53 (NXP iMX8M) | Google Edge TPU (4 TOPS) | 1 GB LPDDR4 | 2–5 W | Clasificacion de imagenes en tiempo real |

> Los PLCs con capacidades de IA, como el Siemens SIMATIC S7-1500 TF, permiten ejecutar modelos TensorFlow Lite directamente en el controlador sin necesidad de hardware adicional.

---

## Robots y sistemas roboticos en IA (I)

La robotica es uno de los principales campos de aplicacion de la IA en la industria. Los robots modernos integran sistemas de percepcion, planificacion y actuacion que dependen de modelos de aprendizaje automatico para funcionar de forma autonoma o colaborativa.

### Clasificacion de sistemas roboticos

- **Brazos roboticos industriales:** manipulacion de materiales, ensamblado y soldadura en lineas de produccion. Operan en entornos controlados con alta precision repetitiva.
- **Robots colaborativos (cobots):** disenados para trabajar junto a personas sin barreras de seguridad. Incorporan sensores de fuerza y vision para detener el movimiento ante contacto inesperado.
- **Vehiculos de guiado automatico (AGV / AMR):** transportan materiales en almacenes y fabricas. Los AMR (*Autonomous Mobile Robots*) usan SLAM para navegar sin guias fisicas.
- **Drones industriales (UAV):** inspeccion de infraestructuras, cartografia, pulverizacion agricola de precision.
- **Robots de inspeccion:** unidades moviles o fijas equipadas con camaras termicas, LiDAR y sensores de gas para inspeccion de plantas industriales.

---

## Robots y sistemas roboticos en IA (II)

### Tabla de plataformas roboticas habituales

| Sistema | Fabricante / Modelo | Payload / Alcance | Accesorios IA | Aplicacion tipica |
|---|---|---|---|---|
| Brazo industrial | KUKA KR AGILUS 6 R900 | 6 kg / 901 mm | Vision artificial KUKA.VisionTech | Ensamblado electronico, pick&place |
| Cobot | Universal Robots UR10e | 12,5 kg / 1300 mm | Camara 2D/3D + force torque sensor | Colaboracion humano-robot, paletizado |
| AMR | MiR600 (Mobile Industrial Robots) | 600 kg carga | Escaner laser 360°, camara RGB-D | Logistica interna en fabricas |
| AGV clasico | Jungheinrich EKS 312 | 1200 kg | Sensor laser de posicionamiento | Almacen con guia magnetica |
| Drone industrial | DJI Matrice 350 RTK | Hasta 2,7 kg de payload | Camara Zenmuse H20T (RGB + IR + LiDAR) | Inspeccion de torres electrica, topografia |
| Robot de inspeccion | Boston Dynamics Spot | 14 kg carga util | Lidar, camara FLIR, microfono | Inspeccion de plantas industriales |

> La integracion de un sistema robotico en una plataforma de IA requiere registrar tanto el chasis como cada modulo de percepcion como activos independientes en el sistema de gestion.

---

## Equipos de procesamiento e infraestructura (I)

El procesamiento de modelos de IA a escala requiere hardware especializado capaz de ejecutar miles de operaciones matriciales en paralelo. Los servidores GPU son el elemento central de cualquier infraestructura de IA moderna, complementados por redes de alta velocidad, almacenamiento rapido y sistemas de alimentacion ininterrumpida.

### Aceleradores de IA: GPU vs. otros

- **GPU (Graphics Processing Unit):** arquitectura de miles de nucleos de proposito general optimizados para algebra lineal. NVIDIA domina el mercado con CUDA como ecosistema de software.
- **TPU (Tensor Processing Unit):** ASICs disenados por Google especificamente para operaciones tensores. Disponibles en Google Cloud y en hardware on-premise (Google Cloud TPU v4 Pod).
- **FPGA (Field Programmable Gate Array):** logica reconfigurable. Intel/Altera Stratix 10 NX se usa para inferencia de baja latencia en entornos financieros y telecomunicaciones.
- **ASIC de inferencia:** chips de proposito unico como el Groq LPU o el Cerebras WSE-3, con rendimiento superior en inferencia pero sin flexibilidad para entrenamiento.

---

## Equipos de procesamiento e infraestructura (II)

### Tabla de hardware de computo para IA

| Equipo | Modelo | GPU / Acelerador | VRAM | Interconexion | Potencia | Uso tipico |
|---|---|---|---|---|---|---|
| Servidor GPU | NVIDIA HGX H100 SXM | 8x H100 SXM5 80 GB | 640 GB HBM3 | NVLink 900 GB/s | 10,2 kW | Entrenamiento LLM, simulacion |
| Servidor GPU | NVIDIA DGX A100 | 8x A100 SXM4 80 GB | 640 GB HBM2e | NVLink 600 GB/s | 6,5 kW | Entrenamiento, fine-tuning |
| Workstation GPU | NVIDIA RTX 6000 Ada (x2) | 2x RTX 6000 Ada | 2x 48 GB GDDR6 | PCIe 4.0 | 300 W c/u | Prototipado, inferencia local |
| Servidor inferencia | NVIDIA L40S | 1–8x L40S 48 GB | 48 GB GDDR6 | PCIe 4.0 | 350 W c/u | Inferencia multimodal en produccion |
| SAI rack | APC Smart-UPS SRT 10 kVA | — | — | — | 10 kVA / 10 kW | Proteccion ante cortes electricos |
| Switch InfiniBand | NVIDIA QM9700 (NDR) | — | — | 400 Gb/s por puerto | — | Interconexion entre nodos GPU |

> En infraestructuras con multiples nodos GPU, la interconexion de red es tan critica como el propio hardware de computo. La latencia de comunicacion entre GPUs afecta directamente al tiempo de entrenamiento distribuido.

---

## Sistema de gestion de activos — campos del inventario

Todo componente fisico incorporado a una plataforma de IA debe quedar registrado en el sistema de gestion de activos (CMDB — *Configuration Management Database*) antes de ser puesto en servicio. El registro garantiza la trazabilidad, facilita el mantenimiento y es requisito para la correcta gestion de licencias y garantias.

### Campos minimos del registro de un activo fisico

| Campo | Descripcion | Ejemplo |
|---|---|---|
| ID unico (CI) | Identificador irrepetible del item de configuracion | CI-2025-0047 |
| Nombre del activo | Denominacion clara y descriptiva | Servidor GPU Rack A - Nodo 3 |
| Tipologia | Categoria funcional segun taxonomia | Servidor / Computo GPU |
| Fabricante | Empresa fabricante | NVIDIA |
| Modelo | Referencia exacta del fabricante | DGX A100 |
| Numero de serie | Identificador fisico unico del hardware | DGX-A100-SN-4892771 |
| Version de firmware | Version actual del firmware instalado | 1.2.4 |
| Configuracion | Parametros relevantes de instalacion | 8x A100 80 GB, 1 TB NVMe RAID |
| Localizacion | Sala, rack, unidad de rack (U) | CPD-Madrid, Rack 07, U12–U20 |
| Estado | Estado operativo actual | Operativo |
| Fecha de alta | Fecha de incorporacion al inventario | 2025-03-14 |
| Responsable tecnico | Persona de contacto para este activo | J. Garcia (ext. 4421) |
| Garantia / EOL | Fin de garantia y fin de vida estimado | Garantia: 2028-03-14 |
| Activos relacionados | Otros CI dependientes o padre | Switch SW-07, PDU-07 |

---

## Sistema de gestion de activos — ejemplo de registro CMDB

A continuacion se muestra un ejemplo de ficha de registro en formato estructurado para una camara hiperespectral incorporada a una linea de inspeccion de calidad:

```yaml
CI: CI-2025-0112
nombre: "Camara hiperespectral - Linea Inspeccion Q3"
tipologia: "Sensor / Camara hiperespectral"
fabricante: "Specim"
modelo: "FX10v2"
numero_serie: "FX10-2025-EU-00773"
firmware: "3.1.2"
configuracion:
  rango_espectral: "400-1000 nm"
  resolucion_espacial: "1024 px"
  interfaz: "GigE Vision / USB3"
  fps_maximo: 330
  software_adquisicion: "Specim CaliSnap 3.2"
localizacion:
  edificio: "Planta Produccion B"
  linea: "Linea Q3 - Inspeccion Final"
  posicion: "Cabezal optico - Cinta conveyor norte"
estado: "Operativo"
fecha_alta: "2025-04-02"
responsable: "M. Torres (ext. 3318)"
garantia_fin: "2028-04-02"
activos_relacionados:
  - "CI-2025-0110  # PC industrial de adquisicion"
  - "CI-2025-0111  # Iluminador lineal LED"
  - "CI-2025-0113  # Lente objetivo 23 mm"
observaciones: "Calibracion espectral realizada en fabrica. Recalibracion anual."
```

---

## Clasificacion y categorizacion de componentes (I)

Una vez registrado un activo en la CMDB, debe clasificarse segun multiples dimensiones para facilitar su localizacion, planificacion de mantenimiento y analisis del parque tecnologico.

### Dimensiones de clasificacion

**Por tipologia funcional:**
- Captacion y percepcion (sensores, camaras, micros)
- Computo (servidores GPU, workstations, TPUs)
- Comunicaciones (switches, routers, tarjetas de red)
- Embebidos y edge (Jetson, PLCs, MCUs)
- Alimentacion y proteccion (SAIs, PDUs, generadores)
- Infraestructura pasiva (racks, cableado, sistemas de refrigeracion)

**Por estado operativo:**

| Estado | Descripcion |
|---|---|
| Operativo | En servicio normal, cumpliendo su funcion |
| En mantenimiento | Temporalmente fuera de servicio por intervencion planificada |
| Degradado | En servicio con capacidad reducida, pendiente de resolucion |
| Fuera de servicio | No disponible por averia o incidente |
| En almacen | Sin asignar, disponible para despliegue |
| Retirado | Dado de baja, pendiente de gestion RAEE |

---

## Clasificacion y categorizacion de componentes (II)

### Clasificacion por localizacion

La localizacion debe ser suficientemente granular para permitir la localizacion fisica del activo sin ambiguedad:

```
Nivel 1: Sede / Instalacion
  └── Nivel 2: Edificio / Planta
        └── Nivel 3: Sala / Zona
              └── Nivel 4: Rack / Posicion fisica
                    └── Nivel 5: Unidad de rack (U) / Slot
```

**Ejemplo aplicado:**
`Sede Madrid > Edificio CPD > Sala Fria Norte > Rack SF-07 > U14-U18`

### Clasificacion por criticidad

| Nivel | Criterio | Ejemplo |
|---|---|---|
| Critico | Su caida paraliza produccion o servicio | Servidor GPU de inferencia en produccion |
| Alto | Degrada significativamente el servicio | Switch de interconexion principal |
| Medio | Impacto parcial, existe redundancia | Nodo de computo secundario |
| Bajo | Sin impacto directo en produccion | Equipo de laboratorio / I+D |

> Asignar el nivel de criticidad correcto es determinante para la planificacion del mantenimiento preventivo y la priorizacion de incidencias.

---

## Actualizacion del registro ante cambios (I)

El registro en la CMDB no es un documento estatico. Cada modificacion sobre un componente fisico —ya sea una sustitucion de pieza, una actualizacion de firmware, un traslado o la incorporacion de un nuevo accesorio— debe reflejarse en el sistema de gestion en el menor tiempo posible.

### Tipos de cambio que generan actualizacion del registro

| Tipo de cambio | Accion en la CMDB | Ejemplo |
|---|---|---|
| Sustitucion completa del activo | Dar de baja el CI anterior; crear nuevo CI | Sustitucion de GPU defectuosa |
| Sustitucion de componente interno | Actualizar campos de configuracion y firmware | Cambio de modulo de memoria RAM |
| Actualizacion de firmware | Modificar campo de version de firmware | Firmware BIOS de servidor: 2.4 -> 2.6 |
| Traslado fisico | Actualizar campo de localizacion | Movimiento de rack 07 a rack 12 |
| Nueva incorporacion | Crear nuevo CI con todos los campos | Instalacion de nueva camara LiDAR |
| Retirada del servicio | Cambiar estado a "Retirado"; registrar fecha | Equipo al final de vida util |
| Cambio de responsable | Actualizar campo de responsable tecnico | Reasignacion tras cambio de equipo |

---

## Actualizacion del registro ante cambios (II)

### Proceso de actualizacion segun documentacion tecnica

Toda actualizacion del inventario debe sustentarse en documentacion tecnica oficial:

1. **Identificar el documento de referencia:** manual del fabricante, nota de aplicacion, alerta de seguridad (CVE) o solicitud de cambio (RFC) interna.
2. **Verificar la version del documento:** utilizar siempre la revision mas reciente disponible en el portal del fabricante.
3. **Ejecutar el cambio** siguiendo el procedimiento documentado.
4. **Actualizar la CMDB** inmediatamente tras la verificacion del cambio, no antes.
5. **Registrar la incidencia o el cambio** en el sistema de ticketing vinculandolo al CI afectado.

> La coherencia entre el estado real del hardware y el contenido de la CMDB es el indicador fundamental de la calidad del proceso de gestion de activos. Una CMDB desactualizada puede provocar decisiones erroneas en situaciones de incidencia critica.

---

## Documentacion de la instalacion

Cada instalacion de un nuevo componente fisico debe quedar documentada con un nivel de detalle suficiente para que cualquier tecnico del equipo pueda reproducir el proceso o diagnosticar problemas sin necesidad de recurrir al tecnico que realizo la instalacion original.

### Estructura de la ficha de instalacion

| Campo | Contenido |
|---|---|
| Referencia del cambio | Numero de RFC o ticket de instalacion (ej. CHG-2025-0341) |
| Fecha y hora | Inicio y fin de la intervencion |
| Tecnico responsable | Nombre y credencial del tecnico que realiza la instalacion |
| Activo afectado | ID del CI en la CMDB |
| Descripcion del trabajo | Que se ha instalado, configurado o modificado |
| Documentacion seguida | Manual, version y apartado de referencia |
| Parametros configurados | Valores exactos aplicados (IPs, VLANs, frecuencias, etc.) |
| Pruebas realizadas | Procedimiento y resultado de cada prueba de verificacion |
| Incidencias durante la instalacion | Cualquier desviacion del procedimiento previsto y como se resolvio |
| Estado final | Operativo / Pendiente de verificacion / Con incidencia abierta |

### Formato de registro de incidencias durante instalacion

```
INC-INST-2025-0112
Fecha: 2025-04-02 14:35
Activo: CI-2025-0112 (Camara Specim FX10v2)
Descripcion: El driver GigE Vision no reconocia la camara con MTU 9000 (jumbo frames).
Causa: Configuracion de MTU en el switch de adquisicion no actualizada.
Solucion: Modificada la configuracion del puerto del switch SF-07/Gi0/4 a MTU 9000.
Tiempo de resolucion: 45 minutos.
Tecnico: M. Torres
```

---

## Manipulacion segura — PRL y EPI (I)

La manipulacion de equipos informaticos y componentes electronicos presenta riesgos especificos que deben ser conocidos y controlados por todo el personal tecnico. La Ley 31/1995 de Prevencion de Riesgos Laborales y el RD 773/1997 sobre utilizacion de EPI establecen el marco normativo aplicable.

### Principales riesgos en la manipulacion de hardware de IA

| Riesgo | Descripcion | Consecuencias posibles |
|---|---|---|
| Contacto electrico directo | Manipulacion de equipos energizados | Electrocucion, paro cardiaco |
| Descarga electrica indirecta | Contacto con masa metalica bajo tension | Quemaduras, lesiones |
| Descarga electrostatica (ESD) | Transferencia de carga entre persona y componente | Dano permanente o latente en circuitos integrados |
| Sobreesfuerzo / carga fisica | Transporte manual de equipos pesados (servidores, UPS) | Lesiones musculo-esqueleticas |
| Caida de objetos en altura | Instalacion de equipos en rack a mas de 1,5 m | Contusiones, fracturas |
| Exposicion a campos electromagneticos | Proximidad a SAIs y fuentes de alimentacion de alta potencia | Interferencias con dispositivos medicos implantados |

---

## Manipulacion segura — PRL y EPI (II)

### Medidas preventivas y EPI requeridos

| Tarea | Medida preventiva | EPI especifico |
|---|---|---|
| Instalacion en rack energizado | Seguir procedimiento LOTO (bloqueo y etiquetado); confirmar ausencia de tension | Guantes aislantes clase 00, calzado de seguridad |
| Manipulacion de tarjetas y modulos electronicos | Pulsera antiESD conectada a tierra; superficie de trabajo con alfombrilla ESD | Pulsera antiESD, alfombrilla ESD |
| Transporte de equipos pesados (> 25 kg) | Uso obligatorio de carro de transporte; dos personas para equipos de mas de 25 kg | Guantes de proteccion mecanica, calzado de seguridad |
| Instalacion en altura (> 1,5 m) | Uso de escalera homologada o plataforma elevadora; nunca escalera de mano sin punto de apoyo superior | Casco, arnés si altura > 2 m |
| Trabajo en sala de servidores con UPS | No introducir herramientas metalicas sin aislamiento junto a bornes de bateria | Guantes aislantes, gafas de proteccion |

### Procedimiento LOTO (*Lockout/Tagout*) simplificado

```
1. Notificar al equipo la intervencion prevista
2. Apagar el equipo mediante el procedimiento de shutdown ordenado
3. Desconectar la alimentacion electrica (cable IEC o breaker de PDU)
4. Colocar candado de bloqueo y etiqueta identificativa
5. Verificar ausencia de tension con multimetro
6. Realizar la intervencion
7. Retirar bloqueo y etiqueta; reconectar y energizar
8. Verificar el correcto arranque del sistema
9. Documentar la intervencion
```

---

## Eficiencia energetica y economia circular

La industria de la IA consume cantidades crecientes de energia. Los centros de datos dedicados a IA representan ya una fraccion significativa del consumo electrico global. La seleccion de hardware eficiente y la correcta gestion del fin de vida son responsabilidades del tecnico de implementacion.

### Indicadores de eficiencia energetica

**PUE (Power Usage Effectiveness):** mide la eficiencia global de un centro de datos. Un PUE = 1,0 seria perfecto (toda la energia va al computo); los CPDs modernos alcanzan PUE de 1,1–1,3.

`PUE = Energia total del CPD / Energia consumida por los equipos de TI`

**Certificaciones de eficiencia en fuentes de alimentacion:**

| Certificacion | Eficiencia minima (carga 50%) | Aplicacion tipica |
|---|---|---|
| 80 PLUS Bronze | 85% | Servidores de gama media |
| 80 PLUS Gold | 90% | Servidores de produccion |
| 80 PLUS Platinum | 92% | Servidores de alta densidad |
| 80 PLUS Titanium | 96% | CPDs de hiperscaladores |

### Economia circular y gestion RAEE

- **Prolongar la vida util:** actualizar firmware y ampliar memoria antes de sustituir el equipo.
- **Reutilizacion interna:** reasignar equipos a funciones menos exigentes (de produccion a desarrollo).
- **RAEE (Residuos de Aparatos Electricos y Electronicos):** Directiva 2012/19/UE, transpuesta en Espana por el RD 110/2015. Los equipos retirados deben entregarse a un gestor autorizado con certificado de destruccion o reciclaje.
- **Huella de carbono:** preferir fabricantes con compromisos de neutralidad carbonica y materiales reciclados.

---

## Actividad practica — Registro en CMDB simulada

### Escenario

Se acaba de instalar un sistema de vision artificial para control de calidad en la linea de envasado de la planta de produccion. El sistema esta compuesto por tres componentes fisicos que deben registrarse en la CMDB antes de su puesta en servicio.

### Componentes a registrar

| # | Componente | Fabricante / Modelo | Informacion adicional |
|---|---|---|---|
| 1 | Camara de vision lineal | Basler raL4096-24gm | GigE, monocromo, 4096 px, 24 fps, montada en cabezal optico, linea de envasado A, posicion P3 |
| 2 | PC industrial de adquisicion | Advantech MIC-770 V3 | Intel Core i7-1185G7, 32 GB RAM, 512 GB NVMe, Win 10 IoT Enterprise, montado en armario electrico, rack EA-01 |
| 3 | Iluminador LED de domo | CCS LDR2-220SW | 220 mm diametro, luz blanca difusa, controlador externo, tension 24 VDC, montado junto a camara |

### Tarea

Para cada componente, cumplimentar una ficha de registro con al menos los siguientes campos: ID CI, nombre del activo, tipologia, fabricante, modelo, numero de serie (inventar uno coherente), localizacion, estado, fecha de alta y activos relacionados. Identificar ademas que datos adicionales habria que solicitar antes de dar el registro por completo.

> Esta actividad simula el proceso real de alta de activos en herramientas CMDB como ServiceNow, iTop o GLPI.

---

## Puntos clave

### Lo esencial de UD1

- Los sistemas de IA fisicos integran dispositivos heterogeneos: sensores de captacion, plataformas embebidas, robots, servidores GPU e infraestructura de red y alimentacion. Cada familia tiene caracteristicas tecnicas propias que condicionan su integracion.

- **Todo componente fisico debe registrarse en la CMDB antes de su puesta en servicio**, con todos los campos requeridos: ID unico, tipologia, fabricante, modelo, numero de serie, configuracion, localizacion, estado y responsable.

- La clasificacion multidimensional —por tipologia, estado, localizacion y criticidad— es lo que convierte el inventario en una herramienta operativa util, no en un mero catalogo.

- Cualquier cambio sobre un activo —sustitucion, traslado, actualizacion de firmware, retirada— debe reflejarse de inmediato en la CMDB, sustentado en documentacion tecnica oficial.

- La manipulacion segura de hardware requiere aplicar el procedimiento LOTO, utilizar los EPI adecuados y prestar especial atencion a los riesgos de ESD, que pueden producir danos invisibles en los componentes electronicos.

- La eficiencia energetica (PUE, certificaciones 80 PLUS) y la correcta gestion del fin de vida (RAEE, RD 110/2015) son responsabilidades del tecnico que afectan directamente a la sostenibilidad de la plataforma.

---

## Criterios de evaluacion

| Criterio | Indicadores observables |
|---|---|
| Registra los componentes fisicos en el sistema de gestion garantizando su trazabilidad | Crea el registro completo con todos los campos requeridos antes de la puesta en servicio; asigna ID unico irrepetible; vincula activos relacionados |
| Clasifica los componentes segun tipologia, localizacion, estado y criticidad | Aplica la taxonomia correcta; asigna la localizacion con el nivel de granularidad requerido; actualiza el estado ante cualquier cambio operativo |
| Actualiza el sistema de gestion ante modificaciones, sustituciones o nuevas incorporaciones | Refleja cualquier cambio en la CMDB en la misma jornada en que se produce; adjunta la referencia al documento tecnico que sustenta el cambio |
| Documenta la instalacion con el nivel de detalle requerido | Cumplimenta la ficha de instalacion con todos los campos; registra las incidencias ocurridas con causa, accion y resultado; conserva los numeros de ticket vinculados |
| Manipula los equipos siguiendo las normas de PRL y utilizando los EPI adecuados | Aplica el procedimiento LOTO antes de intervenir en equipos energizados; usa pulsera y superficie antiESD en la manipulacion de componentes electronicos; no supera los limites de carga manual sin asistencia mecanica |
| Aplica criterios de eficiencia energetica y economia circular | Justifica la seleccion de hardware en funcion de su eficiencia energetica; gestiona los equipos retirados conforme al RD 110/2015 entregandolos a gestor RAEE autorizado |

---

<!-- _class: lead -->

[← Volver a MP01](../)
