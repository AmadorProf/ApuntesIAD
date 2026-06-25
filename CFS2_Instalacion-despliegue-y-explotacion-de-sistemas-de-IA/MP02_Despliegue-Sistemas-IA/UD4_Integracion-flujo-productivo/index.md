---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD4 · Integración en el flujo productivo | MP02 · Despliegue de sistemas de IA'
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

# UD4 · Integración en el flujo productivo

MP02 · Despliegue de sistemas de IA

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno sera capaz de:

- Habilitar entradas de datos al sistema de IA desde distintas fuentes (APIs, streaming, SCADA, IoT)
- Habilitar salidas del sistema de IA hacia los sistemas consumidores con el formato y latencia requeridos
- Verificar las integraciones mediante pruebas de extremo a extremo
- Incorporar metadatos de trazabilidad en cada mensaje procesado
- Documentar todas las intervenciones de integracion y sus logs

> **Resultado de aprendizaje:** Integra sistemas de IA en el flujo productivo aplicando el Plan de integracion.

---

## El flujo productivo: vision de conjunto

### Posicion del sistema de IA en el flujo de datos

```
FUENTES DE DATOS          SISTEMA DE IA             CONSUMIDORES
─────────────────         ──────────────            ────────────────
API REST cliente    ──►   Pre-procesado             API downstream
Stream Kafka        ──►   Inferencia del modelo ──► Base de datos
Sistema SCADA       ──►   Post-procesado            Dashboard / BI
Sensor IoT / MQTT   ──►   Metadatos de trazab.      Actuador / robot
Embebido / robot    ──►                             Almacen de eventos
```

El Plan de integracion especifica **exactamente** que fuentes y destinos debe conectar el sistema, con que formatos, protocolos y requisitos de latencia.

---

## Habilitacion de entradas: API REST

### Integracion de entrada via API REST

La entrada por API REST es el patron mas comun en sistemas de IA de propocito general: el cliente llama al endpoint del modelo con los datos de entrada.

```python
# Ejemplo: servidor FastAPI que recibe peticiones de inferencia
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid, time

app = FastAPI()

class PeticionInferencia(BaseModel):
    datos: list[float]
    cliente_id: str

@app.post("/predict")
async def predecir(peticion: PeticionInferencia):
    trace_id = str(uuid.uuid4())
    marca_temporal = time.time()
    # ... logica de inferencia ...
    return {
        "prediccion": resultado,
        "trace_id": trace_id,
        "modelo_version": "3.2.1",
        "timestamp": marca_temporal,
        "confianza": 0.94
    }
```

---

## Habilitacion de entradas: streaming con Kafka

### Por que Kafka para sistemas de IA en tiempo real

Apache Kafka es el estandar para la intermediacion de mensajes en sistemas de IA que procesan datos en tiempo real (deteccion de fraude, monitorización industrial, recomendacion en tiempo real).

| Concepto Kafka | Aplicacion en IA |
|---|---|
| Topic | Canal por tipo de evento (transacciones, sensores, logs) |
| Particion | Paralelismo del procesado; cada worker consume una particion |
| Offset | Posicion en el flujo; permite reprocesar desde cualquier punto |
| Consumer group | Varios workers del modelo comparten la carga del topic |
| Schema Registry | Garantiza que el formato del mensaje es compatible con el modelo |

```python
from confluent_kafka import Consumer
consumer = Consumer({'bootstrap.servers': 'kafka:9092', 'group.id': 'modelo-fraude'})
consumer.subscribe(['transacciones-entrada'])
while True:
    msg = consumer.poll(timeout=1.0)
    if msg: procesar_y_predecir(msg.value())
```

---

## Habilitacion de entradas: SCADA e industrial

### Integracion con sistemas SCADA via OPC-UA

Los sistemas SCADA (Supervisory Control and Data Acquisition) son comunes en entornos industriales (fabricacion, energia, agua). La integracion con IA permite mantenimiento predictivo, control de calidad y optimizacion en tiempo real.

```python
from opcua import Client

# Conectar al servidor OPC-UA del SCADA
cliente_opc = Client("opc.tcp://scada-servidor:4840/")
cliente_opc.connect()

# Suscribirse a variables de proceso
nodo_temperatura = cliente_opc.get_node("ns=2;i=1001")
nodo_vibracion   = cliente_opc.get_node("ns=2;i=1002")

# Leer valores actuales
temperatura = nodo_temperatura.get_value()
vibracion   = nodo_vibracion.get_value()

# Enviar al modelo de prediccion de fallos
prediccion = modelo.predict([[temperatura, vibracion]])
```

### Protocolos alternativos en entornos industriales

- **Modbus TCP/RTU:** sencillo, muy extendido en PLCs antiguos
- **EtherNet/IP:** redes de control Rockwell/Allen-Bradley
- **PROFINET:** entornos Siemens

---

## Habilitacion de entradas: IoT y embebidos

### Patron MQTT para dispositivos IoT

MQTT (Message Queuing Telemetry Transport) es el protocolo ligero estandar para dispositivos IoT con recursos limitados.

```python
import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, msg):
    datos_sensor = json.loads(msg.payload)
    # Anadir metadatos de trazabilidad
    datos_sensor['trace_id'] = str(uuid.uuid4())
    datos_sensor['timestamp_recepcion'] = time.time()
    # Enviar al modelo
    prediccion = modelo.predict(extraer_features(datos_sensor))
    publicar_resultado(client, prediccion, datos_sensor['trace_id'])

cliente_mqtt = mqtt.Client()
cliente_mqtt.on_message = on_message
cliente_mqtt.connect("mqtt-broker", 1883)
cliente_mqtt.subscribe("fabrica/linea1/sensores/#")
cliente_mqtt.loop_forever()
```

### Plataformas IoT cloud

| Plataforma | Protocolo | Capacidad de inferencia en borde |
|---|---|---|
| AWS IoT Core | MQTT, HTTP | AWS Greengrass para inferencia local |
| Azure IoT Hub | MQTT, AMQP, HTTP | Azure IoT Edge con modulos de IA |
| Google Cloud IoT | MQTT, HTTP | Edge TPU con TensorFlow Lite |

---

## Habilitacion de salidas: patrones y formatos

### Patrones de salida segun el caso de uso

| Patron de salida | Mecanismo | Latencia tipica | Caso de uso |
|---|---|---|---|
| Respuesta sincrona | REST/gRPC, mismo hilo | < 100 ms | API de inferencia online |
| Publicacion en topic | Kafka producer | < 500 ms | Resultado hacia sistemas downstream |
| Escritura en base de datos | SQL/NoSQL asíncrono | < 1 s | Almacenamiento de predicciones |
| Webhook | HTTP POST a URL externa | < 2 s | Notificacion a sistemas terceros |
| Actuacion sobre hardware | gRPC/serial | < 10 ms | Control de robots o actuadores |
| Escritura en dashboard | WebSocket | < 200 ms | Visualizacion en tiempo real |

### Formato de salida con metadatos de trazabilidad

```json
{
  "prediccion": "fraude_probable",
  "confianza": 0.92,
  "trace_id": "a1b2c3d4-e5f6-...",
  "modelo_version": "clasificador-fraude-v3.2.1",
  "timestamp": "2025-03-15T14:32:00.123Z",
  "latencia_ms": 47,
  "features_version": "features-transacciones-v5"
}
```

---

## Metadatos de trazabilidad: que incluir y por que

### Los cuatro metadatos minimos de trazabilidad

| Metadato | Descripcion | Ejemplo |
|---|---|---|
| `trace_id` | Identificador unico de la solicitud, de extremo a extremo | `a1b2c3d4-e5f6-7890-abcd-ef1234567890` |
| `modelo_version` | Version exacta del modelo que genero la prediccion | `clasificador-fraude-v3.2.1` |
| `timestamp` | Marca temporal ISO 8601 con milisegundos y zona horaria | `2025-03-15T14:32:00.123+01:00` |
| `confianza` | Indicador de la fiabilidad de la prediccion | `0.92` (probabilidad) |

### Por que son obligatorios

- Permiten **reproducir** exactamente que modelo proceso cada solicitud
- Facilitan la **depuracion** de predicciones incorrectas
- Son requisito del **Reglamento de IA UE** para sistemas de alto riesgo
- Permiten el **analisis de drift** correlacionando versiones con cambios en la calidad

---

## Verificacion de integraciones: pruebas de extremo a extremo

### Plan de pruebas de integracion

Antes de dar por valida una integracion, se ejecuta un plan de pruebas estructurado:

| Tipo de prueba | Que verifica | Herramienta |
|---|---|---|
| Conectividad | El sistema puede alcanzar la fuente/destino | `curl`, `telnet`, `ping` |
| Formato de datos | Los mensajes tienen el formato esperado | Script de validacion de schema |
| Latencia nominal | La latencia cumple el SLO en condiciones normales | Prueba con datos reales durante 5 min |
| Latencia bajo carga | La latencia cumple el SLO bajo carga pico | `locust`, `k6`, `JMeter` |
| Volumen | El sistema soporta el numero de mensajes por segundo esperado | Prueba de carga con datos reales |
| Error handling | El sistema reacciona correctamente a mensajes malformados | Pruebas con datos invalidos deliberados |

---

## Verificacion de integraciones: prueba de carga con k6

### Ejemplo de prueba de carga del endpoint de inferencia

```javascript
// prueba-carga-inferencia.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Subida a 50 usuarios
    { duration: '5m', target: 50 },   // Carga sostenida
    { duration: '2m', target: 0 },    // Bajada gradual
  ],
  thresholds: {
    http_req_duration: ['p(99)<500'],  // P99 < 500 ms
    http_req_failed: ['rate<0.01'],    // Tasa de error < 1%
  },
};

export default function () {
  const payload = JSON.stringify({ datos: [1.2, 3.4, 5.6, 7.8] });
  const res = http.post('http://api-inferencia/predict', payload,
    { headers: { 'Content-Type': 'application/json' } });
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
```

---

## Documentacion de intervenciones de integracion

### Registro de intervenciones en el Plan de integracion

Cada conexion activada debe quedar documentada con:

| Campo | Ejemplo |
|---|---|
| Tipo de integracion | Entrada via Kafka, salida via REST POST |
| Fuente / Destino | Topic `transacciones-entrada` / API `https://downstream/results` |
| Protocolo y puerto | Kafka TCP 9092 / HTTPS 443 |
| Formato de datos | JSON, schema v2.3 registrado en Schema Registry |
| Autenticacion | mTLS con certificado rotado cada 90 dias |
| Fecha de activacion | 2025-03-20T10:00:00+01:00 |
| Responsable | J. Lopez |
| Resultado de la verificacion | Prueba de carga superada: P99=210 ms, error rate=0.0% |
| Log de integracion | `/logs/integracion-kafka-20250320.log` |

---

## Actividad practica: integracion de un modelo en un flujo industrial

### Escenario

Una planta de fabricacion tiene 50 sensores de temperatura y vibracion que publican via MQTT cada 500 ms. Se quiere integrar un modelo de prediccion de fallos de maquinaria que debe:
- Recibir los datos de los sensores
- Producir una prediccion con nivel de alerta (normal, aviso, critico) en menos de 200 ms
- Escribir el resultado en una base de datos InfluxDB para visualizacion en Grafana
- Enviar una notificacion via webhook si el nivel es "critico"

### Tarea

1. Dibujar el diagrama de flujo de datos (descripcion textual)
2. Disenar el formato de mensaje de entrada y de salida con metadatos de trazabilidad
3. Definir el plan de verificacion de la integracion
4. Identificar los riesgos de la integracion y las medidas de mitigacion

---

## Puntos clave de la UD4

- La integracion no es solo conectar cables: implica definir protocolos, formatos, autenticacion, latencia y tratamiento de errores
- Cada escenario de entrada tiene su patron natural: REST para consultas sincrona, Kafka para streaming de alta frecuencia, MQTT para IoT, OPC-UA para SCADA industrial
- Los metadatos de trazabilidad no son opcionales: `trace_id`, `modelo_version`, `timestamp` y `confianza` deben acompanar a cada prediccion
- Las pruebas de integracion deben incluir pruebas de carga con datos reales, no solo pruebas de conectividad
- El tratamiento de errores es tan importante como el camino feliz: el sistema debe degradar de forma controlada cuando una fuente de datos falla
- Cada integracion activada queda documentada con todos sus parametros en el registro de intervenciones

---

## Criterios de evaluacion — UD4

| Criterio | Indicadores de logro |
|---|---|
| Configura entradas segun el escenario | Elige el protocolo adecuado (REST, Kafka, MQTT, OPC-UA) y lo justifica; configura la autenticacion correctamente |
| Habilita salidas con formato y latencia correctos | Implementa el patron de salida adecuado; cumple el SLO de latencia definido en el Plan |
| Incorpora metadatos de trazabilidad | Incluye los 4 metadatos minimos en cada mensaje de salida; los metadatos son correctos y completos |
| Verifica las integraciones | Ejecuta pruebas de extremo a extremo; incluye prueba de carga; verifica el tratamiento de errores |
| Documenta las intervenciones | Registra todos los parametros de cada integracion; adjunta logs; registra el resultado de la verificacion |

---

[← Volver a MP02](../index.md)


---

<!-- nav-slide -->

## Navegación

[← UD3 · Instalación de aplicaciones d…](../UD3_Instalacion-aplicaciones-despliegue/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD5 · Puesta en servicio →](../UD5_Puesta-en-servicio/)
