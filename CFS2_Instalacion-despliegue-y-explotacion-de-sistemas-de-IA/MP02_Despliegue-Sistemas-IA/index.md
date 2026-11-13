---
marp: true
theme: default
paginate: true
size: 16:9
header: 'MP02 · Despliegue de sistemas de IA'
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
section.lead h1 { font-size: 2.2em; text-align: center; margin-top: 100px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f0fdf4; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
</style>

<!-- _class: lead -->

# MP02 · Despliegue de sistemas de IA

Apuntes de IA y Datos

---

## Ficha del módulo

| Campo | Valor |
|---|---|
| Código | **MP02** |
| Estándar de competencia | ECP2495_3 |
| Familia profesional | Inteligencia Artificial y Data |
| Duración | **200 h** |
| Curso | **1.º** |

> **Competencia que desarrolla:** configurar la infraestructura de sistemas de IA aplicando el plan de aprovisionamiento, instalación y configuración, integrándola en el flujo productivo e implementando medidas que garantizan la calidad del servicio y su trazabilidad.

---

## Estructura del módulo

| # | Unidad didáctica |
|---|---|
| **UD1** | Preparación del despliegue |
| **UD2** | Despliegue de la infraestructura |
| **UD3** | Instalación de aplicaciones de despliegue |
| **UD4** | Integración en el flujo productivo |
| **UD5** | Puesta en servicio |
| **UD6** | Monitorización y mantenimiento |
| **UD7** | Gobernanza, trazabilidad y cumplimiento normativo |
| **UD8** | Responsabilidad, sostenibilidad, PRL y residuos |

---

<!-- _class: lead -->

# UD1
## Preparación del despliegue

---

## UD1 · Determinación de componentes necesarios

**Fuentes de información para la preparación:**
- Sistema de gestión de activos e inventario
- Documentación técnica de los modelos a desplegar
- **Plan de aprovisionamiento:** lista de componentes, versiones y cantidades

**Verificaciones previas:**

| Aspecto | Qué comprobar |
|---|---|
| Disponibilidad | El componente existe en inventario o puede adquirirse |
| Versión | Compatible con el modelo y el resto de la infraestructura |
| Licencias | Vigentes y con los derechos de uso necesarios |
| Compatibilidad | Hardware y software entre sí y con los requisitos del modelo |

---

## UD1 · Trazabilidad y monitorización desde el inicio

**Trazabilidad del despliegue:**
- Repositorios de modelos: versión exacta del artefacto a desplegar
- Repositorios de características (*feature stores*): versión de los datos de entrada
- Versionado de código de infraestructura como código (IaC): Terraform, Ansible
- Sistemas de trazado distribuido: Jaeger, Zipkin, OpenTelemetry

**Configuración de monitorización y alarmas:**
- Picos de carga en CPU, GPU, memoria y red
- Desconexión de elementos o pérdida de disponibilidad
- Protocolos de actuación y comunicación ante cada tipo de alerta

---

<!-- _class: lead -->

# UD2
## Despliegue de la infraestructura

---

## UD2 · Infraestructura propia (on-premise)

**Proceso de aprovisionamiento físico:**

1. Montaje de servidores en rack con cableado estructurado
2. Instalación del sistema operativo (imagen base auditada)
3. Configuración del *bootloader* y *firmware* (BIOS/UEFI)
4. Instalación de controladores de red y GPU
5. Configuración de entornos de ejecución y dependencias base
6. Validación de rendimiento y conectividad

**Documentar:** fecha, equipo responsable, versiones de imágenes y configuraciones, logs de instalación.

---

## UD2 · Infraestructura como servicio (IaaS)

**Recursos a provisionar en la nube:**

| Recurso | Configuración clave |
|---|---|
| Servidor / VM | Tipo de instancia, OS, zona de disponibilidad |
| Almacenamiento | Tipo (SSD, HDD, object), IOPS, capacidad |
| Red | IP estática o elástica, grupo de seguridad, VPC |
| Autoescalado | Métricas de escalado, mínimo y máximo de instancias |
| Copias de seguridad | Frecuencia, retención, prueba de restauración |

**Verificar:** rendimiento con cargas de prueba antes de pasar a producción.

---

<!-- _class: lead -->

# UD3
## Instalación de aplicaciones de despliegue

---

## UD3 · Aplicaciones del ecosistema MLOps

**Herramientas a instalar y configurar:**

| Categoría | Herramientas habituales |
|---|---|
| Orquestación de contenedores | Kubernetes (K8s), Docker Swarm |
| Registro de artefactos | Harbor, JFrog Artifactory, MLflow Registry |
| Monitorización y alarmas | Prometheus + Grafana, Datadog, New Relic |
| Balanceo de carga | NGINX, HAProxy, AWS ALB |
| Gestión de secretos | HashiCorp Vault, AWS Secrets Manager |
| *Feature store* | Feast, Tecton, Hopsworks |

---

## UD3 · Configuración de relaciones y permisos

**Aspectos de configuración entre aplicaciones:**

```yaml
# Ejemplo: acceso del servidor de inferencia al registro de modelos
model_registry:
  url: https://registry.internal:5000
  api_key: ${REGISTRY_API_KEY}  # cargado desde Vault
  namespace: produccion
  timeout_s: 30

storage:
  volume: /mnt/models
  mount_mode: read_only
  permisos: inference-service-sa
```

**Verificar:** compatibilidad entre versiones de modelo, entorno y dependencias antes de poner en producción.

---

<!-- _class: lead -->

# UD4
## Integración en el flujo productivo

---

## UD4 · Habilitación de entradas de datos

**Escenarios de entrada según el contexto:**

| Escenario | Mecanismo |
|---|---|
| **API REST** | Endpoints HTTP, autenticación OAuth2 / API Key |
| **Streaming** (tiempo real) | Kafka, Kinesis, MQTT; suscripción a topics |
| **SCADA / industrial** | OPC-UA, Modbus, adaptadores de protocolo |
| **Embebidos / robótica** | ROS, gRPC, conexión directa por serie o red local |
| **IoT** | MQTT broker, Azure IoT Hub, AWS IoT Core |

**Metadatos de trazabilidad en cada entrada:**
- Marca temporal · Identificador de versión del modelo · Indicador de confianza · ID de transacción

---

## UD4 · Habilitación de salidas y verificación

**Formatos y destinos de salida:**

| Destino | Mecanismo | Consideraciones |
|---|---|---|
| API downstream | REST/gRPC | Latencia, serialización |
| Base de datos | SQL/NoSQL | Esquema, índices |
| Dashboard / BI | Kafka, webhooks | Frecuencia de actualización |
| Actuador / robot | gRPC, serie | Latencia crítica, seguridad funcional |
| Almacén de eventos | Kafka, S3 | Retención, particionado |

**Verificación de integraciones:**
- Pruebas de extremo a extremo con datos reales
- Validación de formatos, latencias y volúmenes esperados

---

<!-- _class: lead -->

# UD5
## Puesta en servicio

---

## UD5 · Estrategias de despliegue

| Estrategia | Descripción | Cuándo usarla |
|---|---|---|
| **Recreación** | Detener la versión antigua, arrancar la nueva | Entornos de bajo riesgo |
| **Blue/Green** | Dos entornos idénticos; cambio de tráfico instantáneo | Alta disponibilidad |
| **Canary** | Porcentaje pequeño de tráfico a la nueva versión | Reducir riesgo de impacto |
| **A/B Testing** | Dos versiones sirven a grupos de usuarios distintos | Validar variantes |
| **Shadow deployment** | Nueva versión recibe tráfico pero no devuelve respuestas | Validación sin impacto |
| **CI/CD** | Automatización completa del pipeline de despliegue | Entregas frecuentes |

---

## UD5 · Verificación antes de la puesta en servicio

**Plan de pruebas previo al go-live:**

1. **Pruebas de humo:** funcionalidad básica en el nuevo entorno
2. **Pruebas de rendimiento:** latencia P50, P95, P99 bajo carga esperada
3. **Pruebas de carga:** comportamiento bajo el pico de demanda
4. **Pruebas diferenciales:** comparar salidas de la nueva versión vs. la anterior
5. **Detección de anomalías:** verificar que el sistema de monitorización detecta errores

> Documentar cada prueba: configuración utilizada, resultados, decisión de go/no-go y responsable.

---

<!-- _class: lead -->

# UD6
## Monitorización y mantenimiento

---

## UD6 · Qué monitorizar en producción

**Dimensiones de monitorización de un sistema de IA:**

| Dimensión | Métricas clave |
|---|---|
| **Rendimiento técnico** | Latencia, throughput, tasa de error, uptime |
| **Calidad del modelo** | Accuracy, F1, RMSE comparados con baseline |
| **Drift de distribución** | Cambio en la distribución de las entradas |
| **Integridad de datos** | Valores nulos, outliers, formatos incorrectos |
| **Recursos** | CPU, GPU, memoria, disco, red |

---

## UD6 · Detección de drift y correcciones

**Pruebas estadísticas para detección de drift:**

| Prueba | Uso |
|---|---|
| **PSI** (Population Stability Index) | Cambios en distribución de variables de entrada |
| **Kolmogorov-Smirnov** | Comparar distribuciones de dos muestras |
| **Jensen-Shannon** | Divergencia entre distribuciones de probabilidad |
| **Chi-cuadrado** | Drift en variables categóricas |

**Operaciones de corrección:**
- Escalado de recursos (horizontal o vertical)
- Vuelta a versión previa (*rollback*)
- Aplicación de parches o reentrenamiento del modelo
- Redirección de flujos o activación de modo de operación reducida

---

<!-- _class: lead -->

# UD7
## Gobernanza, trazabilidad y cumplimiento normativo

---

## UD7 · Clasificación por riesgo (Reglamento IA UE)

**Niveles de riesgo según el Reglamento de IA de la UE (2024/1689):**

| Nivel | Descripción | Ejemplos |
|---|---|---|
| **Inaceptable** | Prohibido | Manipulación subliminal, puntuación social |
| **Alto** | Autorización y supervisión estricta | Diagnóstico médico, reclutamiento, crédito |
| **Limitado** | Obligaciones de transparencia | Chatbots, deepfakes |
| **Mínimo** | Sin restricciones adicionales | Filtros de spam, videojuegos |

> Los sistemas de IA de **alto riesgo** requieren documentación técnica, registro de eventos y supervisión humana.

---

## UD7 · Logging, supervisión humana y gobernanza de datos

**Registro automático de eventos (*logging*):**
- Versión del modelo activo · Entradas recibidas · Salidas generadas
- Decisiones tomadas · Intervenciones humanas · Incidencias

**Supervisión humana:**
- Validación previa a actuaciones de alto impacto
- Capacidad de intervención o anulación en tiempo real
- Parada segura ante comportamientos inesperados

**Gobernanza de datos:**
- Representatividad y trazabilidad del origen de los datos
- Derechos de las personas: acceso, rectificación, supresión, oposición, limitación (RGPD)
- Conservación de evidencias del ciclo de vida del modelo

---

<!-- _class: lead -->

# UD8
## Responsabilidad, sostenibilidad, PRL y residuos

---

## UD8 · Responsabilidad y sostenibilidad en el despliegue

**Responsabilidad en el despliegue:**
- Tomar decisiones técnicas asumiendo sus consecuencias
- Comunicación efectiva y trabajo colaborativo con todos los perfiles
- Transmitir instrucciones de funcionamiento de forma sencilla y comprensible

**Sostenibilidad en la infraestructura:**
- Reutilizar infraestructura existente antes de provisionar nueva
- Evitar sobredimensionamiento: ajustar recursos a la demanda real
- Reducir consumo con instancias *spot*, autoescalado y apagado programado
- Principio **DNSH** y **ODS** aplicables (7, 9, 12, 13)

---

## UD8 · PRL y gestión de residuos

**PRL — Prevención de riesgos laborales:**

| Riesgo | Medida |
|---|---|
| Eléctrico | EPI: calzado aislante, guantes, herramientas aisladas |
| ESD | Pulsera antiestática, alfombrilla ESD |
| Carga manual | Carros elevadores, límite 25 kg |
| Ergonomía | Mobiliario ajustable, pausas activas |
| Emergencias | Plan de emergencias, señalización, simulacros |

**Gestión de RAEE:**
- Recogida selectiva y entrega a gestor autorizado
- Certificado de destrucción para equipos con datos
- Economía circular: reutilización antes del reciclaje

---

## Criterios de evaluación — MP02

- Determina y verifica componentes; configura monitorización y alarmas
- Monta y configura infraestructura propia o contratada; documenta intervenciones
- Instala aplicaciones MLOps según el Plan; verifica compatibilidad
- Configura entradas y salidas según el escenario; incorpora metadatos de trazabilidad
- Selecciona la estrategia de despliegue adecuada y verifica el funcionamiento
- Detecta drift con pruebas estadísticas; aplica correcciones y documenta
- Clasifica el sistema por riesgo; configura logging y supervisión humana
- Integra sostenibilidad; aplica EPI y ergonomía; gestiona residuos RAEE

---

<!-- _class: lead -->

# MP02 · Despliegue de sistemas de IA

**200 h · Curso 1.º · ECP2495_3**

*Apuntes de IA y Datos*
