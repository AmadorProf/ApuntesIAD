---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD1 · Preparación del despliegue | MP02 · Despliegue de sistemas de IA'
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

# UD1 · Preparación del despliegue

MP02 · Despliegue de sistemas de IA

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Interpretar el Plan de aprovisionamiento e identificar los componentes necesarios para el despliegue
- Verificar disponibilidad, versiones, licencias y compatibilidad de cada componente
- Diseñar y configurar sistemas de monitorización y alarmas previos al despliegue
- Establecer mecanismos de trazabilidad que garanticen la reproducibilidad del despliegue
- Documentar el estado inicial del entorno antes de cualquier intervención

> **Resultado de aprendizaje:** Prepara el despliegue de la infraestructura interpretando las especificaciones para mantener la integridad y continuidad del servicio.

---

## Punto de partida: el Plan de aprovisionamiento

### Qué es y para qué sirve

El **Plan de aprovisionamiento** es el documento de referencia que describe todos los componentes necesarios para desplegar el sistema de IA: hardware, software, modelos, dependencias y licencias.

### Fuentes de información complementarias

| Fuente | Qué aporta |
|---|---|
| Sistema de gestión de activos (CMDB) | Inventario actualizado del hardware y software disponible |
| Documentación técnica del modelo | Requisitos de hardware, dependencias de software, versiones validadas |
| Plan de aprovisionamiento | Lista de componentes, versiones, cantidades y proveedores |
| Registro de licencias | Estado, caducidad y alcance de las licencias activas |

---

## Determinación de componentes: hardware

### Componentes hardware típicos en un despliegue de IA

| Componente | Verificaciones previas |
|---|---|
| Servidores de cómputo | Modelo, RAM, núcleos de CPU, soporte IPMI/BMC |
| Aceleradores (GPU/TPU) | Modelo, VRAM, controladores, soporte CUDA/ROCm |
| Almacenamiento | Tipo (NVMe, SAS, SATA), capacidad, IOPS garantizadas |
| Red | Ancho de banda, latencia, redundancia, soporte RDMA/InfiniBand |
| Sistemas de alimentación | SAI, redundancia N+1, certificación energética |

### Matriz de compatibilidad previa

Antes de iniciar el despliegue se elabora una **matriz de compatibilidad** que cruza versiones de firmware, SO, controladores y dependencias del modelo para detectar incompatibilidades conocidas.

---

## Determinación de componentes: software y licencias

### Capas de software a inventariar

```
Sistema operativo base         →  Ubuntu 22.04 LTS / RHEL 9
Controladores de hardware      →  NVIDIA CUDA 12.x, libGL, controladores NIC
Entorno de ejecución           →  Python 3.11, virtualenv / conda
Framework de inferencia        →  TensorFlow Serving / TorchServe / Triton
Dependencias de la aplicación  →  requirements.txt o pyproject.toml versionados
Modelo artefacto               →  Versión específica del registro de modelos
```

### Gestión de licencias

| Tipo de licencia | Aspectos a verificar |
|---|---|
| Software propietario | Caducidad, número de instancias, restricciones de uso |
| Open source | Compatibilidad de licencias (GPL, MIT, Apache) con el producto |
| Modelos privados | Acuerdo de uso, restricciones de redistribución |
| Datos | Términos del proveedor, uso en producción autorizado |

---

## Verificación de disponibilidad y compatibilidad

### Proceso de verificación paso a paso

1. **Contrastar inventario vs. Plan de aprovisionamiento:** comprobar que cada componente existe o puede adquirirse en el plazo requerido
2. **Comprobar versiones exactas:** usar hashes SHA256 para artefactos de software y modelos
3. **Validar compatibilidad entre capas:** consultar matrices de compatibilidad oficiales (p. ej., NVIDIA CUDA Compatibility Guide)
4. **Verificar licencias activas:** revisar fecha de caducidad y número de instancias permitidas
5. **Registrar resultado:** aprobar o emitir una solicitud de aprovisionamiento adicional

### Ejemplo: verificación de compatibilidad CUDA-PyTorch

```bash
# Verificar versión de CUDA disponible
nvidia-smi | grep "CUDA Version"
# Verificar que PyTorch fue compilado con esa versión
python -c "import torch; print(torch.version.cuda)"
```

---

## Ensayos previos: factores del componente

### Qué se comprueba en un entorno de pruebas

Los ensayos previos al despliegue real tienen como objetivo **identificar fallos antes de que afecten al entorno productivo**.

**Factores del componente que pueden causar fallos:**

| Factor | Ejemplo de fallo |
|---|---|
| Versión incorrecta | La librería de inferencia no acepta el formato del modelo |
| Dependencia faltante | Error al cargar libcudnn.so en tiempo de ejecución |
| Configuración por defecto inadecuada | Timeout demasiado corto para modelos de lenguaje grandes |
| Limitación de recursos | El modelo no cabe en la VRAM disponible con batch_size=32 |
| Incompatibilidad de formatos | El modelo fue exportado en ONNX opset 17, el runtime soporta hasta 15 |

---

## Ensayos previos: factores del entorno de pruebas

### Diferencias entre el entorno de pruebas y el entorno productivo

Una causa frecuente de fallos en producción es que el entorno de pruebas no es suficientemente representativo.

| Factor del entorno | Riesgo si no se controla |
|---|---|
| Hardware diferente (CPU vs. GPU) | Diferencias de rendimiento imprevisibles |
| Red simulada vs. red real | Latencias reales muy superiores a las medidas |
| Volumen de datos reducido | No se detectan problemas de escalabilidad |
| Datos sintéticos vs. reales | No se detecta drift o formatos inesperados |
| Ausencia de otros servicios dependientes | No se detectan problemas de integración |

> **Principio:** el entorno de pruebas debe ser lo más similar posible al entorno productivo en hardware, red, datos y servicios concurrentes.

---

## Configuración de monitorización y alarmas: conceptos

### Por qué configurar la monitorización antes del despliegue

La monitorización debe estar activa **antes** de que el sistema entre en producción, no después. Esto permite:

- Establecer una **línea base** de comportamiento normal
- Detectar anomalías desde el primer momento
- Disponer de datos históricos desde el inicio para análisis de tendencias

### Arquitectura típica de monitorización MLOps

```
Componente ─── Prometheus (scraping métricas)
                    │
               Grafana (visualización + alertas)
                    │
               Alertmanager ─── PagerDuty / Slack / correo
```

---

## Configuración de alarmas: umbrales y protocolos

### Definición de umbrales de alarma

| Métrica | Umbral de aviso | Umbral crítico | Acción |
|---|---|---|---|
| CPU del servidor de inferencia | > 80 % durante 5 min | > 95 % durante 2 min | Escalar / notificar |
| Latencia P99 de la API | > 500 ms | > 2000 ms | Escalar / rollback |
| Tasa de error (5xx) | > 1 % | > 5 % | Notificar / rollback |
| VRAM utilizada | > 85 % | > 95 % | Reducir batch / escalar |
| Heartbeat del servicio | Sin respuesta 30 s | Sin respuesta 60 s | Reiniciar / escalar |

### Protocolo de actuación y comunicación

Cada alarma debe tener asociado un **runbook** que especifica: responsable de turno, pasos de diagnóstico, acciones correctivas y canal de comunicación (Slack, PagerDuty, correo).

---

## Trazabilidad: repositorios de modelos y características

### Componentes de un sistema de trazabilidad MLOps

La **trazabilidad** garantiza que cualquier predicción producida en producción pueda relacionarse con exactitud con la versión del modelo, los datos y el código que la generaron.

| Componente | Herramientas habituales | Qué registra |
|---|---|---|
| Registro de modelos | MLflow Registry, DVC, BentoML | Versión del artefacto, métricas, fecha de registro |
| Feature store | Feast, Tecton, Hopsworks | Versión de las transformaciones y datos de entrada |
| Repositorio de código | Git (tags y ramas) | Código exacto que genera el artefacto |
| Repositorio de parámetros | MLflow Params, W&B | Hiperparámetros del entrenamiento |
| Sistema de linaje de datos | OpenLineage, Marquez | Origen y transformaciones de los datos |

---

## Trazabilidad: versionado y sistemas de trazado distribuido

### Estrategia de versionado para reproducibilidad

```yaml
# Ejemplo: metadatos mínimos de un artefacto de modelo registrado
model:
  name: "clasificador-fraude-v3"
  version: "3.2.1"
  artifact_uri: "s3://ml-registry/models/clasificador-fraude/3.2.1/model.pkl"
  sha256: "a3f9c1..."
  training_data_version: "dataset-fraude-2024Q4-v2"
  feature_set_version: "features-transacciones-v5"
  git_commit: "e7a2bc4"
  training_run_id: "mlflow://runs/9f3a1d..."
```

### Trazado distribuido en inferencia

Para sistemas de IA en producción, el trazado distribuido permite seguir cada solicitud a través de todos los microservicios:

- **OpenTelemetry:** estándar abierto de instrumentación
- **Jaeger / Zipkin:** backends de almacenamiento y visualización de trazas
- Cada petición recibe un `trace_id` único que acompaña todos los logs

---

## Actividad practica: checklist de preparacion del despliegue

### Escenario

Un equipo MLOps debe preparar el despliegue de un modelo de detección de anomalías en transacciones bancarias. El modelo fue entrenado con PyTorch 2.1, requiere GPU NVIDIA con 16 GB de VRAM, y se desplegara como API REST con TorchServe.

### Tarea

Elaborar un checklist de preparacion con al menos 5 categorias, siguiendo el proceso visto en la unidad. Para cada elemento del checklist, indicar:

1. El aspecto a verificar
2. Como verificarlo (comando, herramienta o procedimiento)
3. Criterio de aceptacion (valor esperado o condicion)
4. Responsable

### Entregable

Checklist en formato tabla. Incluir al menos: hardware, software/dependencias, licencias, trazabilidad y monitorización.

---

## Puntos clave de la UD1

- El **Plan de aprovisionamiento** es el documento de referencia: no se inicia ningun despliegue sin haberlo leido y verificado
- La verificacion de componentes abarca disponibilidad, version exacta, compatibilidad entre capas y estado de las licencias
- Los ensayos previos deben reproducir las condiciones del entorno productivo; las diferencias no controladas entre entornos son la principal fuente de fallos inesperados
- La monitorización y las alarmas se configuran **antes** del despliegue, no después
- La trazabilidad se construye sobre cuatro pilares: versionado del modelo, de los datos, del codigo y de los parametros; todos deben poder relacionarse entre si de forma univoca
- Un `trace_id` por peticion en produccion permite reconstruir exactamente que modelo, con que datos y bajo que configuracion genero cada prediccion

---

## Criterios de evaluacion — UD1

| Criterio | Indicadores de logro |
|---|---|
| Determina los componentes necesarios | Identifica todos los componentes del Plan de aprovisionamiento; detecta componentes faltantes o desactualizados |
| Verifica compatibilidad y licencias | Comprueba versiones con matrices oficiales; valida estado de licencias; documenta el resultado |
| Configura monitorización y alarmas | Define umbrales razonados para al menos 4 metricas; asocia cada alarma a un protocolo de actuacion |
| Asegura la trazabilidad | Identifica los 4 pilares del versionado; diseña un esquema de metadatos para el artefacto del modelo |
| Documenta el proceso | Genera un checklist de preparacion completo y un registro del estado inicial del entorno |

---

[← Volver a MP02](../index.md)


---

<!-- nav-slide -->

## Navegación

[Volver al módulo](../) &nbsp;·&nbsp; [UD2 · Despliegue de la infraestruct… →](../UD2_Despliegue-infraestructura/)
