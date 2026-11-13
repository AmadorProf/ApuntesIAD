---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD7 · Responsabilidad, sostenibilidad y PRL | MP04 · Infraestructura para la ejecución de LLMs'
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

# UD7 · Responsabilidad, sostenibilidad y PRL

MP04 · Infraestructura para la ejecución de LLMs

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno sera capaz de:

- Identificar las responsabilidades profesionales en el despliegue y explotacion de sistemas de IA
- Aplicar criterios de sostenibilidad y economia circular en el dimensionamiento de infraestructura LLM
- Gestionar correctamente los residuos de aparatos electricos y electronicos (RAEE) incluyendo el borrado seguro de modelos
- Aplicar las medidas de prevencion de riesgos laborales especificas de los entornos de sala de servidores
- Relacionar el trabajo tecnico con los Objetivos de Desarrollo Sostenible (ODS) y el principio DNSH

---

## Responsabilidad profesional en entornos de IA

### Que implica la responsabilidad profesional

El tecnico que despliega y opera un sistema LLM asume responsabilidades que van mas alla de la ejecucion tecnica.

| Dimension | Ejemplos concretos en infraestructura LLM |
|---|---|
| **Tecnica** | Garantizar que el servicio funciona segun las especificaciones; documentar cambios; escalar incidentes |
| **Etica** | No desplegar modelos sin validacion previa; no usar la infraestructura para fines no autorizados |
| **Legal** | Cumplir el RGPD en el tratamiento de datos de uso; respetar licencias de los modelos |
| **Organizacional** | Comunicar riesgos e incidencias con claridad y oportunidad; respetar los procedimientos definidos |

> El despliegue de un LLM no es una tarea aislada: afecta a usuarios finales, a la organizacion y potencialmente a terceros cuyos datos pueden estar en el contexto. La responsabilidad profesional exige actuar con esa consciencia.

---

## Iniciativa, comunicacion eficaz y respeto a la diversidad

### Iniciativa en entornos tecnicos

La iniciativa profesional no consiste en actuar sin consultar, sino en identificar problemas, proponer soluciones y escalarlos cuando superan el ambito de decision propio.

```
Problema detectado
    |
    +--> Dentro de mi ambito de decision → Actuar + documentar + comunicar
    |
    +--> Fuera de mi ambito → Escalar con informacion completa + propuesta de solucion
```

### Comunicacion eficaz

En un equipo tecnico, la comunicacion eficaz significa:
- Informar del estado de los sistemas sin tecnicismos innecesarios al interlocutor no tecnico
- Documentar los cambios con contexto suficiente para que otro tecnico pueda entenderlos
- Registrar incidencias con: cuando ocurrio, que se observo, que se hizo y el resultado

### Respeto a la diversidad

Los entornos tecnicos son frecuentemente multidisciplinares y multiculturales. El respeto a la diversidad implica:
- Adaptar el nivel tecnico de la comunicacion al interlocutor
- No asumir que el conocimiento tecnico de un colega es menor por razon alguna

---

## Sostenibilidad en infraestructura LLM — consumo energetico

### El coste energetico de la inferencia

Los modelos LLM son intensivos en energia. Un servidor GPU puede consumir entre 300 W y 1000 W de forma continua.

| Escenario | Consumo estimado | CO2 equivalente (mix europeo) |
|---|---|---|
| RTX 4090 al 100 % (24 h) | ~600 Wh = 0,6 kWh/h → 14,4 kWh/dia | ~4,6 kg CO2/dia |
| A100 SXM al 100 % (24 h) | 400 W → 9,6 kWh/dia | ~3,1 kg CO2/dia |
| Servidor apagado fuera de horario | 0 W | 0 kg CO2 |

> Apagar o suspender un servidor GPU durante 12 horas de inactividad nocturna puede suponer un ahorro del 40-50 % del consumo total. La sostenibilidad empieza por no encender lo que no se necesita.

### Herramienta de referencia: CodeCarbon

```bash
pip install codecarbon
```

```python
from codecarbon import EmissionsTracker
tracker = EmissionsTracker(project_name="inferencia-llm-produccion")
tracker.start()
# ... inferencia ...
emisiones = tracker.stop()
print(f"CO2 equivalente: {emisiones * 1000:.2f} gramos")
```

---

## Sostenibilidad — minimizar consumo en la infraestructura

### Tecnica 1: Auto-shutdown fuera de horario

```bash
# Apagado automatico del servidor GPU a las 22:00 (laborables)
# Arranque automatico a las 07:30
# /etc/cron.d/llm-power-schedule
0 22 * * 1-5 root systemctl stop llm-server && nvidia-smi -pm 0
30 7 * * 1-5 root nvidia-smi -pm 1 && systemctl start llm-server
```

### Tecnica 2: Autoescalado (scale-to-zero en cloud)

```yaml
# Kubernetes HPA + KEDA para escalar a 0 replicas sin peticiones
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: llm-server-scaler
spec:
  scaleTargetRef:
    name: llm-deployment
  minReplicaCount: 0   # Escala a 0 cuando no hay peticiones
  maxReplicaCount: 4
  cooldownPeriod: 300  # Espera 5 minutos antes de escalar a 0
  triggers:
  - type: prometheus
    metadata:
      serverAddress: http://prometheus:9090
      metricName: llm_requests_in_flight
      threshold: "1"
```

---

## Sostenibilidad — cuantizacion como medida de eficiencia

### Cuantizacion: menor precision, menor consumo

La cuantizacion reduce la precision numerica de los pesos del modelo, lo que disminuye el consumo de VRAM y mejora la eficiencia energetica.

| Precision | VRAM (7B) | VRAM (13B) | Velocidad relativa | Calidad relativa |
|---|---|---|---|---|
| BF16 (16 bits) | ~14 GB | ~26 GB | 1x (referencia) | 100 % |
| Q8 (8 bits) | ~7 GB | ~13 GB | ~1,1x | ~99 % |
| Q4 (4 bits) | ~4 GB | ~7 GB | ~1,3x | ~95 % |
| Q2 (2 bits) | ~2 GB | ~4 GB | ~1,5x | ~85 % |

> Un modelo Q4 ocupa un tercio de la VRAM de su equivalente BF16 y permite usar hardware mas pequeño. En sostenibilidad, reutilizar una GPU existente con un modelo cuantizado es preferible a comprar hardware nuevo.

```bash
# Cuantizar un modelo con llama.cpp
python3 convert_hf_to_gguf.py /models/llama-3.1-8b/ --outtype q4_k_m \
  --outfile /models/llama-3.1-8b-Q4_K_M.gguf
```

---

## Economia circular — reutilizacion de equipos

### Principios de economia circular aplicados a hardware de IA

La economia circular busca mantener los equipos en uso el maximo tiempo posible antes de su reciclaje.

```
Nuevo hardware
    |
    v
[Uso primario: inferencia de modelos grandes]
    |
    v
[Degradacion: GPU con VRAM reducida o rendimiento menor]
    |
    v
[Reutilizacion: inferencia de modelos cuantizados / tareas de embedding]
    |
    v
[Reutilizacion secundaria: servidor de desarrollo / pruebas]
    |
    v
[Borrado seguro de datos] → [Donacion / venta de segunda mano]
    |
    v
[RAEE: reciclaje certificado si no es viable la reutilizacion]
```

### Evitar sobredimensionamiento

> Dimensionar para el pico maximo de uso sostenido, no para el peor escenario teorico. Un servidor sobredimensionado consume mas energia en inactividad y sus componentes envejecen sin producir valor.

---

## Principio DNSH y ODS aplicables

### Principio DNSH (Do No Significant Harm)

El principio DNSH, establecido en el Reglamento de Taxonomia Europea (UE 2020/852), exige que las actividades economicas no causen daño significativo a ninguno de los seis objetivos medioambientales.

En infraestructura LLM, implica:

| Objetivo medioambiental | Aplicacion concreta |
|---|---|
| Mitigacion del cambio climatico | Minimizar consumo energetico; preferir proveedores con energia renovable |
| Adaptacion al cambio climatico | Planificar la resiliencia del CPD ante eventos climaticos extremos |
| Uso sostenible del agua | Considerar el PUE y WUE del CPD (muchos sistemas de refrigeracion usan agua) |
| Economia circular | Reutilizar equipos; gestion correcta de RAEE |
| Prevencion de la contaminacion | Borrado seguro antes de retirar equipos; gestion de baterias SAI |
| Biodiversidad | Preferir CPDs con certificacion ambiental |

### ODS relacionados

- **ODS 9** (Industria, innovacion e infraestructura): despliegue responsable y eficiente
- **ODS 12** (Produccion y consumo responsables): economia circular, RAEE
- **ODS 13** (Accion por el clima): reduccion de huella de carbono de la inferencia

---

## Gestion de residuos RAEE — marco legal

### Que son los RAEE

Los Residuos de Aparatos Electricos y Electronicos (RAEE) son equipos al final de su vida util que contienen materiales peligrosos (plomo, mercurio, cadmio, bromados) y materiales recuperables (cobre, oro, aluminio, tierras raras).

### Marco legal en España

| Norma | Contenido clave |
|---|---|
| RD 110/2015 | Traspone la Directiva 2012/19/UE; responsabilidad del productor; obligacion de recogida selectiva |
| Ley 7/2022 de residuos | Marco general; jerarquia: prevenir > reutilizar > reciclar > recuperar > eliminar |
| RGPD + LOPD-GDD | Borrado seguro de datos antes de retirar equipos con almacenamiento |

### Equipos RAEE tipicos en infraestructura LLM

- Tarjetas graficas (GPU) con fin de vida util
- Memorias RAM, SSD, HDD que contenian pesos o logs del sistema
- Fuentes de alimentacion y baterias de SAI
- Cableado y conectores con metales pesados
- Servidores completos al final de su vida util

---

## Gestion de RAEE — recogida, separacion y reciclaje

### Proceso correcto de gestion de RAEE

```
1. IDENTIFICACION
   Catalogar el equipo (marca, modelo, numero de serie, fecha de baja)
        |
        v
2. BORRADO SEGURO DE DATOS (ver siguiente diapositiva)
        |
        v
3. EVALUACION DE REUTILIZACION
   ¿Puede funcionar en otro rol? → SI: reutilizar; NO: paso siguiente
        |
        v
4. ENTREGA A PUNTO LIMPIO O GESTOR AUTORIZADO
   Nunca tirar en contenedor general ni de organicos
        |
        v
5. DOCUMENTACION
   Conservar el certificado de recogida del gestor autorizado (minimo 5 años)
```

### Donde entregar los RAEE

- Punto limpio municipal (para equipos de pequeño volumen)
- Gestor autorizado de RAEE (para volumenes empresariales)
- Programa de recogida del fabricante (algunos fabricantes tienen obligacion legal)
- Distribuidores: al comprar un equipo nuevo, el distribuidor debe recoger el viejo

---

## Borrado seguro de modelos y datos antes de retirar equipos

### Por que el borrado normal no es suficiente

El borrado estandar de archivos (`rm`, formateo rapido) solo elimina la referencia en el sistema de archivos. Los datos siguen presentes en el disco y pueden recuperarse con herramientas forenses.

### NIST SP 800-88: estandar de borrado seguro

El NIST 800-88 define tres niveles de sanitizacion:

| Nivel | Metodo | Aplicacion |
|---|---|---|
| **Clear** | Sobreescritura logica (1 pasada) | Reutilizacion interna en la misma organizacion |
| **Purge** | Sobreescritura multiple o cifrado + borrado de clave | Reutilizacion externa o donacion |
| **Destroy** | Destruccion fisica (triturado, desmagnetizacion) | Eliminacion definitiva, datos muy sensibles |

### Borrado seguro con `shred` (HDD y SSD clasicos)

```bash
# Sobreescritura de 3 pasadas (Clear/Purge para HDD)
shred -vz -n 3 /dev/sdb

# Para SSD: usar el comando ATA Secure Erase (mas efectivo que shred en SSD)
# Verificar soporte:
hdparm -I /dev/sdb | grep "Security"
# Ejecutar Secure Erase:
hdparm --user-master u --security-set-pass password /dev/sdb
hdparm --user-master u --security-erase password /dev/sdb
```

---

## Borrado seguro — GPU y almacenamiento de modelos

### Borrado de pesos del modelo antes de retirar una GPU o disco

```bash
# Verificar que el modelo esta en /models/ antes de borrar
ls -lh /models/llama-3.1-8b/

# Borrado seguro del directorio de modelos
find /models/ -type f -exec shred -vz -n 3 {} \;
rm -rf /models/

# Verificacion: el directorio ya no existe
ls /models/ 2>&1 || echo "Directorio eliminado correctamente"

# Para un disco completo con datos de modelos (SSD NVMe)
# 1. Cifrar el disco si no estaba cifrado (retroactivo con dd)
# 2. O usar nvme-cli para Secure Erase
nvme format /dev/nvme0n1 --ses=1  # Crypto erase (borra la clave de cifrado interna)
```

### Registro de borrado

```markdown
## Registro de borrado seguro — 2026-06-23

| Equipo | N. Serie | Datos borrados | Metodo | Responsable | Verificacion |
|---|---|---|---|---|---|
| SSD Samsung 870 EVO 2TB | S4EVNX0R123456 | Modelos Llama 3.1 8B y 70B | ATA Secure Erase | J. Garcia | Hash SHA256 antes/despues |
| RTX 4090 | GPU-XYZ123 | Sin almacenamiento persistente | N/A | J. Garcia | N/A |
```

---

## Prevencion de riesgos laborales — marco y EPI

### Marco legal de PRL

La **Ley 31/1995 de Prevencion de Riesgos Laborales** establece el deber de proteccion del empresario y el deber de participacion del trabajador.

En entornos de sala de servidores, los riesgos especificos son:

| Riesgo | Causa | Consecuencia |
|---|---|---|
| Caida de objetos | Equipos en altura, racks mal fijados | Golpes, fracturas |
| Descarga electrica | Mantenimiento sin desconexion previa | Electrocucion |
| Descarga electrostatica (ESD) | Contacto sin equipamiento antiestatico | Daño de componentes, quemaduras leves |
| Sobreesfuerzo / lumbalgia | Manipulacion de servidores pesados sin ayuda mecanica | Lesion musculoesqueletal |
| Caida al mismo nivel | Cables en suelo, suelo tecnico mal colocado | Torceduras, fracturas |
| Exposicion a ruido | Sistemas de refrigeracion, ventiladores | Hipoacusia con exposicion prolongada |

### EPI especificos para sala de servidores

| EPI | Norma de referencia | Cuando usarlo |
|---|---|---|
| Calzado de seguridad (puntera de acero) | EN ISO 20345 | Siempre en sala de servidores |
| Guantes antielectrostaticos | EN 16350 | Manipulacion de tarjetas y componentes |
| Gafas de proteccion | EN 166 | Manipulacion de baterias, soldadura, limpieza con aire comprimido |
| Proteccion auditiva (tapones 3M) | EN 352 | Exposicion prolongada (> 85 dB) |

---

## Ergonomia en sala de servidores

### Riesgos ergonomicos y medidas preventivas

```
Operacion: instalacion de servidor 2U en rack (peso tipico: 15-25 kg)
    |
    Riesgo: sobreesfuerzo lumbar, atrapamiento de dedos
    |
    Medidas:
    1. Usar carrito elevador o tabla deslizante para el rack
    2. Dos personas para equipos > 10 kg (tecnico + auxiliar)
    3. Posicion de levantamiento: espalda recta, rodillas flexionadas, objeto cerca del cuerpo
    4. Usar guiles/railes del rack para deslizar, no elevar directamente
```

### Recomendaciones ergonomicas para trabajo prolongado en CPD

| Actividad | Recomendacion | Limite |
|---|---|---|
| Trabajo de pie en pasillo de rack | Suelo antifattiga, cambiar posicion cada 30 min | Max 2 h continuadas |
| Cableado en posicion inclinada | Pausas activas cada 20 min | Max 40 min continuados |
| Lectura de monitores de consola | Pantalla a altura de ojos, distancia 50-70 cm | Pausas de 5 min cada hora |
| Exposicion al ruido de ventiladores | Tapones de insercion desde 80 dB | Sin proteccion: max 8 h a 80 dB |

> Los trastornos musculoesqueleticos son la principal causa de baja laboral en el sector IT. La prevencion requiere diseño ergonomico del puesto, no solo buena voluntad del trabajador.

---

## Plan de emergencias en sala de servidores

### Situaciones de emergencia especificas del CPD

| Emergencia | Respuesta inmediata | Evacuacion |
|---|---|---|
| Incendio / humo | Pulsar pulsador de alarma; NO usar agua; usar extintor CO2 o polvo seco; activar sistema de extincion automatica si existe | Salir por via de evacuacion señalizada; cerrar puertas al salir |
| Descarga electrica en colega | NO tocar a la victima; cortar la alimentacion desde el cuadro electrico; llamar al 112 | Mantener zona despejada hasta llegada de emergencias |
| Fuga de gas refrigerante | Ventilar si es posible; evacuar la sala; llamar a mantenimiento y 112 | Punto de reunion exterior |
| Terremoto / estructura comprometida | Alejarse de los racks; protegerse bajo mesa resistente; no usar ascensores | Evacuar al punto de reunion tras el sismo |

### Señalizacion obligatoria en sala de servidores

- Salidas de emergencia (ISO 7010 E001)
- Ubicacion de extintores (ISO 7010 F001)
- Prohibicion de entrada sin EPI
- Voltaje peligroso en cuadros electricos (ISO 7010 W012)
- Peso maximo de los racks

---

## Integracion: sostenibilidad en el ciclo de vida de la infraestructura

### Vision de ciclo de vida completo

```
ADQUISICION                      USO                         FIN DE VIDA
    |                             |                               |
Evaluar certificacion        Cuantizar modelos            Borrado seguro
energetica del HW            para reducir VRAM            de datos (NIST 800-88)
(ENERGY STAR, TCO)               |                               |
    |                        Auto-shutdown fuera           Evaluacion de
Preferir proveedores         de horario                   reutilizacion
con garantia de reciclaje        |                               |
    |                        Monitorizar PUE              Entrega a gestor
Documentar el inventario     del CPD                      RAEE autorizado
desde el primer dia              |                               |
                            Registrar emisiones           Documentar con
                            con CodeCarbon                certificado de
                                                          destruccion
```

### Indicadores de sostenibilidad a reportar

| Indicador | Descripcion | Herramienta |
|---|---|---|
| PUE (Power Usage Effectiveness) | Eficiencia del CPD: consumo total / consumo IT | Medidor en cuadro electrico |
| WUE (Water Usage Effectiveness) | Agua consumida por kWh de IT | Contador de agua del sistema de refrigeracion |
| CO2e por inferencia | Gramos de CO2 equivalente por 1000 tokens | CodeCarbon |
| % hardware reutilizado | Equipos reutilizados vs. nuevos en el año | Inventario de activos |

---

## Actividad practica — Auditoria de sostenibilidad y PRL

### Escenario

Una empresa de tamano medio dispone de tres servidores GPU (2x RTX 3090, 1x A100) para inferencia de modelos LLM. El contrato de alquiler del CPD termina en 3 meses. Se deben retirar los equipos y preparar el traslado o baja definitiva.

### Tareas

1. Elabora el inventario de equipos con numero de serie, datos almacenados y evaluacion de reutilizacion para cada uno
2. Define el procedimiento de borrado seguro para cada tipo de dispositivo (SSD NVMe, HDD SATA, memoria RAM)
3. Calcula el ahorro de CO2 estimado si se aplica auto-shutdown 12 horas diarias en los tres servidores (consumo: 350 W / 250 W / 400 W respectivamente)
4. Identifica los EPI necesarios para el desmontaje de los servidores del rack y justifica cada uno
5. Redacta las tres entradas del registro de borrado seguro con los campos del estandar NIST 800-88

---

## Puntos clave — UD7

- La **sostenibilidad no es un añadido**: el consumo energetico de un servidor GPU al 100 % puede superar los 14 kWh diarios. El auto-shutdown, la cuantizacion y el autoescalado son medidas tecnicas con impacto ambiental real y medible.

- El **borrado seguro** (shred, ATA Secure Erase, nvme format --ses=1) no es opcional antes de retirar equipos: es una obligacion legal (RGPD) y etica. Un simple `rm -rf` no borra los datos de forma irrecuperable.

- Los **RAEE** tienen una cadena de custodia legal: nunca al contenedor general. El certificado del gestor autorizado debe conservarse al menos 5 años como evidencia de cumplimiento.

- Los **EPI en sala de servidores** son obligatorios, no opcionales: calzado de seguridad para proteccion frente a caida de equipos, guantes antielectrostaticos para manipulacion de componentes, gafas para trabajos con baterias o aire comprimido.

- La **responsabilidad profesional** incluye comunicar problemas con informacion suficiente, documentar los cambios para que otro tecnico pueda retomar el trabajo, y escalar cuando una decision supera el ambito propio.

---

## Criterios de evaluacion — UD7

| Criterio | Indicadores de logro |
|---|---|
| **Integra sostenibilidad en el dimensionamiento** | Justifica la cuantizacion como medida de eficiencia; calcula el ahorro energetico de auto-shutdown; referencia ODS y principio DNSH |
| **Gestiona residuos RAEE correctamente** | Aplica la jerarquia de residuos; ejecuta borrado seguro segun NIST 800-88; entrega a gestor autorizado y conserva certificado |
| **Aplica EPI y medidas ergonomicas** | Identifica los EPI especificos para cada operacion en sala de servidores; aplica recomendaciones ergonomicas para manipulacion de equipos pesados |
| **Actua con responsabilidad profesional** | Documenta cambios con contexto suficiente; comunica incidencias con claridad; escala decisiones que superan su ambito |

> **Referencia:** resultado de aprendizaje RA7 — "Actua con responsabilidad profesional integrando criterios de sostenibilidad, gestion de RAEE y prevencion de riesgos laborales en la operacion de infraestructura de IA."

---

[← Volver a MP04](../index.md)


---

<!-- nav-slide -->

## Navegación

[← UD6 · Seguridad, privacidad y traza…](../UD6_Seguridad-privacidad-trazabilidad/) &nbsp;·&nbsp; [Volver al módulo](../)
