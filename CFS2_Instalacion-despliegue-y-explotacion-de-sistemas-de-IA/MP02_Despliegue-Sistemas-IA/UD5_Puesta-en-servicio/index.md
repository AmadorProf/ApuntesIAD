---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD5 · Puesta en servicio | MP02 · Despliegue de sistemas de IA'
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

# UD5 · Puesta en servicio

MP02 · Despliegue de sistemas de IA

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno sera capaz de:

- Seleccionar la estrategia de despliegue mas adecuada segun el escenario y los requisitos de disponibilidad
- Aplicar las distintas estrategias: CI/CD, recreacion, Blue/Green, Canary, A/B Testing y Shadow Deployment
- Instalar el modelo segun el escenario: aplicacion, contenedor, firmware embebido y Over The Air
- Ejecutar un plan de verificacion completo previo al go-live
- Documentar la puesta en servicio con todos los elementos requeridos

> **Resultado de aprendizaje:** Pone en servicio sistemas de IA aplicando el Plan de despliegue.

---

## Panorama: escenarios de instalacion del modelo

### Modalidades de instalacion segun el tipo de sistema

| Escenario | Mecanismo | Ejemplo |
|---|---|---|
| Aplicacion en servidor | Proceso Python / Java arrancado como servicio | `systemd` + TorchServe |
| Contenedor | Imagen Docker con el modelo incluido o montado | `docker run` / `kubectl apply` |
| Firmware en embebido | Grabacion directa en flash del dispositivo | `esptool.py` (ESP32), `openocd` (ARM) |
| Over The Air (OTA) | Actualizacion remota del firmware via red | AWS IoT Greengrass, balena.io |
| Modelo en borde | Inferencia local en dispositivo con recursos limitados | TensorFlow Lite, ONNX Runtime Mobile |

---

## Instalacion como contenedor: flujo completo

### Del registro al cluster: pipeline de puesta en servicio

```
1. Construir la imagen con el modelo
   docker build -t registry.empresa.com/modelo-fraude:3.2.1 .

2. Firmar y publicar en el registro
   docker push registry.empresa.com/modelo-fraude:3.2.1

3. Actualizar el manifiesto de Kubernetes
   # deployment.yaml: image: registry.empresa.com/modelo-fraude:3.2.1

4. Aplicar el despliegue
   kubectl apply -f deployment.yaml -n produccion

5. Verificar el estado del rollout
   kubectl rollout status deployment/modelo-fraude -n produccion
```

### Contenido minimo del Dockerfile de produccion

```dockerfile
FROM python:3.11-slim
RUN pip install torch==2.1.2 torchserve==0.9.0 --no-cache-dir
COPY modelo/ /opt/modelo/
USER nonroot
ENTRYPOINT ["torchserve", "--start", "--model-store", "/opt/modelo"]
```

---

## Instalacion de firmware en dispositivos embebidos

### Proceso de grabacion de firmware con modelo de IA

Para dispositivos embebidos (microcontroladores, SoC), el modelo se incluye en el firmware:

```
1. Convertir el modelo a formato TFLite (optimizado para borde)
   tflite_convert --saved_model_dir=./modelo --output_file=modelo.tflite

2. Cuantizar el modelo para reducir tamano y latencia
   # Post-training quantization a INT8
   converter.optimizations = [tf.lite.Optimize.DEFAULT]

3. Incluir el modelo en el firmware (como array C)
   xxd -i modelo.tflite > modelo_tflite.h

4. Compilar el firmware con el modelo embebido
   cmake --build build/ --target firmware

5. Grabar en el dispositivo
   esptool.py --chip esp32s3 write_flash 0x10000 firmware.bin
```

---

## Actualizacion Over The Air (OTA)

### Ciclo de vida de una actualizacion OTA

La actualizacion OTA permite desplegar nuevas versiones del modelo en dispositivos remotos sin intervenccion fisica, lo que es imprescindible en flotas de dispositivos IoT o sistemas industriales distribuidos.

| Fase | Descripcion |
|---|---|
| Preparacion | Compilar y firmar el nuevo firmware/modelo |
| Subida | Publicar en el backend OTA (AWS IoT Greengrass, balena.io) |
| Seleccion | Definir el grupo de dispositivos que reciben la actualizacion |
| Distribucion | El backend empuja o los dispositivos descargan la actualizacion |
| Verificacion | El dispositivo comprueba la firma y el hash antes de instalar |
| Activacion | Reinicio controlado con la nueva version |
| Rollback automatico | Si el dispositivo no arranca correctamente, vuelve a la version anterior |

> La firma digital del firmware es obligatoria: un firmware no firmado podria ser sustituido por codigo malicioso en transito.

---

## Estrategias de despliegue: vision general

### Comparativa de estrategias

| Estrategia | Tiempo de inactividad | Rollback | Riesgo | Complejidad | Caso de uso tipico |
|---|---|---|---|---|---|
| Recreacion | Si (downtime) | Manual | Alto | Baja | Entornos de desarrollo |
| Rolling update | No | Automatico | Medio | Media | Actualizaciones frecuentes |
| Blue/Green | No | Instantaneo | Bajo | Alta | Lanzamientos criticos |
| Canary | No | Parcial automatico | Muy bajo | Alta | Reducir riesgo en prod |
| A/B Testing | No | Por segmento | Muy bajo | Muy alta | Validacion de modelos |
| Shadow | No | No aplica | Nulo | Alta | Validacion sin impacto |

---

## Estrategia: Recreacion y Rolling Update

### Recreacion (Recreate)

Detiene todos los pods de la version antigua antes de arrancar los de la nueva. Produce downtime. Solo adecuada para entornos no criticos.

```yaml
# deployment.yaml con estrategia Recreate
spec:
  strategy:
    type: Recreate
```

### Rolling Update (actualizacion gradual)

Sustituye los pods de uno en uno, manteniendo siempre un minimo de instancias disponibles.

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Maximo de pods extra durante la actualizacion
      maxUnavailable: 0  # Ningun pod puede no estar disponible
```

> `maxUnavailable: 0` garantiza cero downtime. `maxSurge: 1` controla el uso de recursos durante la transicion.

---

## Estrategia: Blue/Green

### Dos entornos identicos, cambio de trafic instantaneo

```
                  ┌──────────────────┐
Trafico ──────►  │   BALANCEADOR    │
(100%)            │   DE CARGA       │
                  └────────┬─────────┘
                           │ Apunta a "blue" (v3.1) o "green" (v3.2)
              ┌────────────┴───────────────┐
         ┌────┴─────┐               ┌──────┴────┐
         │  BLUE     │               │  GREEN    │
         │  v3.1     │               │  v3.2     │
         │  (activo) │               │  (espera) │
         └──────────┘               └──────────┘
```

En Kubernetes, el cambio se implementa modificando el selector del Service:

```bash
# Cambiar de blue a green en segundos
kubectl patch service modelo-fraude-svc \
  -p '{"spec":{"selector":{"version":"green"}}}'
# Rollback instantaneo si hay problemas:
kubectl patch service modelo-fraude-svc \
  -p '{"spec":{"selector":{"version":"blue"}}}'
```

---

## Estrategia: Canary

### Despliegue progresivo del nuevo modelo

El despliegue Canary envia un porcentaje pequeno del trafico real al nuevo modelo, permitiendo detectar problemas antes de una exposicion completa.

```
Trafico de usuarios
       │
       ├──── 95 % ────► Modelo v3.1 (estable)
       │
       └────  5 % ────► Modelo v3.2 (canary)
```

### Implementacion con Argo Rollouts

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
spec:
  strategy:
    canary:
      steps:
      - setWeight: 5    # 5% del trafico
      - pause: {duration: 10m}
      - setWeight: 25
      - pause: {duration: 10m}
      - setWeight: 50
      - pause: {duration: 10m}
      # Si las metricas son correctas, promueve al 100%
      analysis:
        templates:
        - templateName: tasa-error-modelo
```

---

## Estrategia: A/B Testing y Shadow Deployment

### A/B Testing: dos modelos, dos grupos de usuarios

El A/B Testing divide el trafico entre dos versiones del modelo segun criterios de segmentacion (ID de usuario, region geografica, tipo de cliente).

| Aspecto | A/B Testing | Canary |
|---|---|---|
| Objetivo | Validar hipotesis de negocio | Reducir riesgo de lanzamiento |
| Duracion | Dias o semanas | Horas o dias |
| Segmentacion | Por atributo del usuario | Porcentaje aleatorio |
| Metrica principal | Metrica de negocio (conversion, revenue) | Metricas tecnicas (error, latencia) |

### Shadow Deployment: validacion sin impacto

En Shadow Deployment, el nuevo modelo recibe copias del trafico real pero sus respuestas **no se envian al cliente**. Solo se registran para comparacion.

```
Peticion ──► Modelo v3.1 ──► Respuesta al cliente
         └─► Modelo v3.2 ──► Log de comparacion (no expuesto)
```

Ideal para validar modelos de alto riesgo antes de su exposicion.

---

## CI/CD para modelos de IA: el pipeline de despliegue

### Etapas de un pipeline CI/CD para MLOps

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  Commit  │─►│  Build   │─►│  Test    │─►│  Stage   │─►│  Deploy  │
│  codigo  │  │  imagen  │  │  modelo  │  │  (pre-   │  │  (prod)  │
│  modelo  │  │  Docker  │  │  y API   │  │  prod)   │  │          │
└──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

### Ejemplo con GitHub Actions

```yaml
name: Deploy modelo
on:
  push:
    tags: ['v*.*.*']
jobs:
  deploy:
    steps:
      - uses: actions/checkout@v4
      - name: Build y publicar imagen
        run: docker build -t $REGISTRY/modelo:${{ github.ref_name }} . && docker push ...
      - name: Despliegue Canary en K8s
        run: kubectl argo rollouts set image modelo-fraude modelo=$REGISTRY/modelo:${{ github.ref_name }}
      - name: Monitorizar rollout
        run: kubectl argo rollouts watch modelo-fraude --timeout=600s
```

---

## Verificacion antes del go-live: plan de pruebas

### Las cinco pruebas imprescindibles antes de la puesta en servicio

| Prueba | Objetivo | Herramienta | Criterio de aceptacion |
|---|---|---|---|
| Pruebas de humo | Funcionalidad basica en el entorno de destino | Script propio | Respuesta 200 OK en todos los endpoints criticos |
| Pruebas de rendimiento | Latencia bajo carga nominal | `k6`, `locust` | P99 < SLO definido |
| Pruebas de carga | Comportamiento bajo pico de demanda | `k6`, `JMeter` | Sin errores con 2x la carga esperada |
| Pruebas diferenciales | Las salidas del nuevo modelo son coherentes con las del anterior | Script de comparacion | Divergencia < umbral definido en el Plan |
| Deteccion de anomalias | El sistema de monitorización detecta errores | Inyeccion de fallos | Alarma generada en < tiempo definido |

---

## Verificacion: pruebas diferenciales

### Por que las pruebas diferenciales son criticas para modelos de IA

A diferencia del software tradicional, una nueva version de un modelo puede producir respuestas diferentes incluso para las mismas entradas (por reentrenamiento, cambio de arquitectura, etc.). Las pruebas diferenciales detectan estos cambios antes del go-live.

```python
import pandas as pd
import numpy as np

# Cargar un conjunto de datos de referencia (golden dataset)
df = pd.read_parquet("golden_dataset_v1.parquet")

# Obtener predicciones de ambas versiones
pred_v31 = [modelo_v31.predict(x) for x in df['features']]
pred_v32 = [modelo_v32.predict(x) for x in df['features']]

# Calcular divergencia
divergencia = np.mean(np.abs(np.array(pred_v31) - np.array(pred_v32)))
print(f"Divergencia media: {divergencia:.4f}")

# Criterio: rechazar si la divergencia supera el umbral del Plan
assert divergencia < 0.05, f"Divergencia {divergencia} supera el umbral 0.05"
```

---

## Documentacion de la puesta en servicio

### Registro de puesta en servicio (release record)

| Campo | Contenido |
|---|---|
| Identificador de release | `release-modelo-fraude-v3.2.1-2025-03-20` |
| Estrategia de despliegue | Canary, incremento de 5% → 100% en 30 minutos |
| Version desplegada | `clasificador-fraude-v3.2.1` |
| Version anterior | `clasificador-fraude-v3.1.0` |
| Fecha y hora de inicio | 2025-03-20T09:00:00+01:00 |
| Fecha y hora de fin | 2025-03-20T09:35:22+01:00 |
| Responsable tecnico | M. Garcia |
| Aprobador | J. Lopez (Tech Lead) |
| Resultado de pruebas | Todas superadas; P99=187 ms, error rate=0.0% |
| Incidencias durante el despliegue | Ninguna |
| Logs del despliegue | `/logs/release-fraude-v321-20250320.log` |

---

## Actividad practica: simulacion de despliegue Canary

### Escenario

Un equipo debe desplegar la version 4.0 de un modelo de recomendacion de productos en una plataforma de e-commerce que recibe 50.000 peticiones/hora. La version anterior (3.5) lleva 6 meses en produccion sin incidencias. La nueva version mejora el CTR un 8% en staging pero tiene una latencia media un 15% mayor.

### Tarea

1. Justificar la eleccion de la estrategia de despliegue Canary en este escenario frente a otras alternativas
2. Definir el plan de incremento de trafico (pasos, duracion de cada fase, metricas de aprobacion)
3. Definir los criterios de rollback automatico (que metricas y umbrales lo disparan)
4. Redactar el registro de puesta en servicio completo (puede ser simulado)

---

## Puntos clave de la UD5

- La eleccion de la estrategia de despliegue no es arbitraria: depende del nivel de disponibilidad requerido, la capacidad de rollback rapido y el nivel de riesgo aceptable
- **Blue/Green** es el rollback mas rapido (segundos); **Canary** reduce el riesgo gradualmente; **Shadow** es el mas seguro para validar sin impacto
- Las pruebas diferenciales son especificas de los modelos de IA: una nueva version no es necesariamente mas correcta para todas las entradas
- El pipeline CI/CD para modelos debe incluir tanto pruebas tecnicas como verificaciones de calidad del modelo (metricas de negocio, sesgo, fairness)
- Ningun despliegue se da por concluido sin un registro de puesta en servicio completo y firmado por el responsable tecnico y el aprobador
- La puesta en servicio de un embebido requiere verificacion de la firma digital del firmware antes de la instalacion

---

## Criterios de evaluacion — UD5

| Criterio | Indicadores de logro |
|---|---|
| Selecciona la estrategia adecuada | Justifica la eleccion basandose en disponibilidad, riesgo y capacidad de rollback; conoce las 6 estrategias y sus casos de uso |
| Implementa el despliegue | Aplica correctamente la estrategia elegida; configura los parametros (maxSurge, pesos de trafico, pasos del Canary) |
| Verifica el funcionamiento | Ejecuta las 5 pruebas del plan de verificacion; documenta los resultados con datos cuantitativos |
| Realiza pruebas diferenciales | Compara las salidas del nuevo modelo con las del anterior; verifica que la divergencia esta dentro del umbral |
| Documenta la puesta en servicio | Completa el registro de release con todos los campos; adjunta logs; registra incidencias si las hay |

---

[← Volver a MP02](../index.md)
