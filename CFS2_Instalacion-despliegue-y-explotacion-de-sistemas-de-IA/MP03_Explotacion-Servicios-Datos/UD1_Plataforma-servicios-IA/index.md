---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD1 · Implementación de la plataforma de servicios de IA | MP03 · Explotación de servicios de datos y analítica'
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

# UD1 · Implementación de la plataforma de servicios de IA

**MP03 — Explotación de servicios de datos y analítica**
Apuntes de IA y Datos

---

## Objetivos de la unidad

Al finalizar esta unidad el alumnado será capaz de:

- Habilitar recursos de la plataforma de IA (servicios, usuarios, cómputo, almacenamiento) y asignarlos a centros de coste o proyectos.
- Verificar que se cumplen los prerrequisitos técnicos antes de iniciar la explotación.
- Elaborar y ejecutar un Plan de pruebas de verificación del entorno.
- Documentar el aprovisionamiento en el sistema de gestión de recursos.
- Comunicar incidencias detectadas y aplicar un uso eficiente de los recursos.

> **Resultado de aprendizaje:** Implementa la plataforma registrando, autenticando, instalando herramientas y asignando recursos para iniciar su explotación.

---

## Contexto: la plataforma de servicios de IA

Una **plataforma de servicios de IA** es el entorno centralizado donde se alojan y gestionan los modelos, pipelines y herramientas de análisis de datos de una organización.

### Ejemplos reales de plataformas

| Plataforma | Proveedor | Modelo de uso |
|---|---|---|
| Azure Machine Learning | Microsoft | PaaS en nube pública |
| Google Vertex AI | Google Cloud | PaaS en nube pública |
| Amazon SageMaker | AWS | PaaS en nube pública |
| Databricks | Databricks Inc. | Nube o híbrido |
| MLflow + Kubernetes | Open source | On-premise o nube privada |

La elección condiciona cómo se habilitan recursos, cómo se factura y qué herramientas de cliente se instalan.

---

## Habilitación de recursos — Servicios

La primera acción es **activar los servicios** que se van a necesitar en el proyecto.

### Tipos de servicios habituales

- **APIs de inferencia:** endpoints para consumir modelos en producción (REST, gRPC).
- **Notebooks interactivos:** entornos Jupyter / JupyterLab para exploración de datos.
- **Pipelines de entrenamiento:** orquestadores de flujos de trabajo (Kubeflow, Azure Pipelines, Vertex Pipelines).
- **Almacenes de modelos:** repositorios versionados (MLflow Model Registry, SageMaker Model Registry).
- **Monitorización:** sistemas de seguimiento de métricas, drift y logs (Prometheus, Grafana, Azure Monitor).

> Cada servicio activado genera coste. Habilitar solo lo necesario para el proyecto es una buena práctica de eficiencia y sostenibilidad.

---

## Habilitación de recursos — Usuarios y roles

### Modelo de control de acceso (RBAC)

| Rol | Permisos típicos |
|---|---|
| **Administrador de plataforma** | Crear y borrar recursos, gestionar usuarios, configurar red |
| **Científico de datos** | Crear notebooks, lanzar experimentos, registrar modelos |
| **Ingeniero de ML** | Desplegar pipelines, gestionar endpoints de inferencia |
| **Analista de negocio** | Acceso de lectura a resultados e informes |
| **Auditor** | Lectura de logs y trazabilidad, sin acceso a datos |

### Principio de mínimo privilegio

Cada usuario recibe únicamente los permisos imprescindibles para su función. Esto reduce la superficie de ataque y cumple con el principio de mínimo acceso del RGPD.

---

## Habilitación de recursos — Cómputo y almacenamiento

### Recursos de cómputo

| Tipo | Caso de uso | Ejemplo |
|---|---|---|
| CPU (general purpose) | Preprocesamiento, inferencia ligera | 4 vCPU / 16 GB RAM |
| GPU (entrenamiento) | Deep learning, visión artificial, NLP | NVIDIA A100, V100 |
| GPU (inferencia) | Latencia baja en producción | NVIDIA T4, A10G |
| TPU | Modelos de gran escala en Google Cloud | TPU v4 |

### Cuotas de almacenamiento

- Cuota por usuario o equipo (p. ej., 100 GB por científico de datos).
- Separación entre datos brutos, datos procesados y artefactos de modelos.
- Políticas de retención: cuánto tiempo se conservan los datos y los modelos entrenados.

---

## Asignación a centro de coste o proyecto

En entornos empresariales, cada recurso debe estar vinculado a un **centro de coste** o proyecto para imputar el gasto correctamente.

### Mecanismos de asignación

- **Etiquetado (tagging):** cada recurso lleva etiquetas `proyecto`, `departamento`, `entorno` (dev/staging/prod).
- **Presupuestos y alertas:** configurar umbrales de gasto que disparan avisos automáticos.
- **Namespaces o grupos de recursos:** agrupaciones lógicas en la plataforma (Resource Groups en Azure, Projects en GCP).

### Ejemplo de etiquetado

```yaml
tags:
  proyecto: "deteccion-fraude-2025"
  departamento: "riesgos"
  entorno: "produccion"
  centro-coste: "CC-4712"
```

---

## Verificación de prerrequisitos técnicos

Antes de iniciar la explotación es obligatorio verificar que el entorno cliente está correctamente configurado.

### Checklist de prerrequisitos

| Área | Elemento a verificar | Herramienta |
|---|---|---|
| **Conectividad** | Acceso a los endpoints de la plataforma (HTTPS 443) | `curl`, `ping`, `traceroute` |
| **Autenticación** | Tokens, API keys o certificados válidos y no expirados | CLI de la plataforma |
| **SDK / CLI** | Versión correcta instalada y actualizada | `az --version`, `gcloud version` |
| **IDE / Notebooks** | Entorno de desarrollo funcional y conectado | Jupyter, VS Code |
| **Drivers GPU** | Versión compatible con los frameworks a usar | `nvidia-smi` |
| **Red corporativa** | Proxies, firewalls y puertos abiertos | Test de conectividad |

---

## Plan de pruebas de verificación

El **Plan de pruebas** es el documento que formaliza qué se verifica, cómo y quién es responsable.

### Estructura mínima del Plan de pruebas

| Sección | Contenido |
|---|---|
| **Alcance** | Qué recursos y servicios se comprueban |
| **Pruebas de conectividad** | Acceso a endpoints y APIs desde el cliente |
| **Pruebas de autenticación** | Login correcto con las credenciales del proyecto |
| **Pruebas funcionales básicas** | Ejecutar un notebook de ejemplo, lanzar una inferencia de prueba |
| **Pruebas de rendimiento básico** | Latencia de respuesta dentro de los SLA definidos |
| **Criterio de aceptación** | Todas las pruebas pasan sin errores bloqueantes |
| **Responsable y fecha** | Quién ejecuta el plan y cuándo |

> El Plan de pruebas es el contrato entre el equipo técnico y el área de negocio. Sin él, no se puede declarar que el entorno está listo para producción.

---

## Configuración y despliegue organizado

Un despliegue organizado sigue un proceso reproducible y documentado.

### Pasos de un despliegue estructurado

1. Clonar o descargar la plantilla de configuración del proyecto.
2. Parametrizar las variables de entorno (región, SKU de cómputo, nombres de recursos).
3. Aplicar la configuración mediante Infrastructure as Code (Terraform, Bicep, CloudFormation).
4. Ejecutar el Plan de pruebas.
5. Registrar el resultado en el sistema de gestión de recursos.
6. Comunicar la disponibilidad al equipo y a las partes interesadas.

### Herramientas de IaC habituales

| Herramienta | Proveedor objetivo | Lenguaje |
|---|---|---|
| Terraform | Multi-cloud | HCL |
| Bicep | Azure | DSL propio |
| CloudFormation | AWS | YAML / JSON |
| Deployment Manager | GCP | YAML |

---

## Documentación del aprovisionamiento

La documentación es un criterio de evaluación explícito de esta unidad.

### Registro en el sistema de gestión de recursos

Cada aprovisionamiento debe quedar registrado con, al menos:

- **Nombre y tipo de recurso** habilitado.
- **Fecha y hora de aprovisionamiento.**
- **Responsable** técnico que realizó el despliegue.
- **Límites de consumo** configurados (cuota CPU/GPU, almacenamiento, coste máximo mensual).
- **Incidencias detectadas** durante la habilitación y cómo se resolvieron.
- **Fecha de revisión** programada (para verificar que los recursos siguen siendo necesarios).

> La documentación no es opcional. Sin registro, no hay trazabilidad, no hay auditoría posible y no se puede escalar el equipo sin riesgo de duplicar recursos o perder configuraciones.

---

## Comunicación de incidencias

Cuando se detecta un problema durante el aprovisionamiento, se debe comunicar de forma estructurada.

### Ciclo de vida de una incidencia

```
Detección --> Clasificación (severidad) --> Registro en sistema
    --> Asignación a responsable --> Resolución --> Cierre y documentación
```

### Niveles de severidad

| Nivel | Descripción | Tiempo de respuesta típico |
|---|---|---|
| **Crítico** | Servicio completamente inoperativo | < 1 hora |
| **Alto** | Funcionalidad principal degradada | < 4 horas |
| **Medio** | Funcionalidad secundaria afectada | < 24 horas |
| **Bajo** | Incidencia cosmética o de documentación | < 72 horas |

---

## Uso eficiente de recursos

La eficiencia en el consumo de recursos es una responsabilidad profesional y una obligación contractual en entornos cloud.

### Buenas prácticas de eficiencia

- **Auto-shutdown:** apagar notebooks y clusters de cómputo fuera del horario laboral.
- **Instancias preemptibles/spot:** usar instancias de bajo coste para entrenamientos no urgentes (ahorro de hasta un 70%).
- **Escalado automático:** configurar el escalado según la demanda real, no sobreprovisionar.
- **Monitorización de costes:** revisar el dashboard de costes semanalmente.
- **Limpieza de recursos huérfanos:** eliminar regularmente recursos no utilizados (snapshots, volúmenes, endpoints inactivos).

> Un científico de datos que no gestiona los costes de la plataforma es un riesgo para el proyecto. La eficiencia es parte del perfil profesional.

---

## Actividad práctica — UD1

### "Aprovisionamiento de un entorno de ML en la nube"

**Escenario:** La empresa Logística Ibérica S.A. necesita configurar un entorno de ML para el proyecto de predicción de demanda. Tienes acceso a una cuenta de prueba en Azure Machine Learning.

**Tareas:**

1. Crear un workspace de Azure ML con los siguientes recursos: cluster de cómputo CPU (Standard_DS3_v2, 2 nodos máximo), blob storage para datos, y un registro de contenedores.
2. Crear dos usuarios: `ml-scientist@empresa.com` (rol Contributor) y `ml-analyst@empresa.com` (rol Reader). Aplicar el principio de mínimo privilegio.
3. Etiquetar todos los recursos con `proyecto: prediccion-demanda`, `entorno: dev`, `centro-coste: CC-1001`.
4. Ejecutar el Plan de pruebas: conectividad, autenticación con la CLI, lanzar un notebook de ejemplo.
5. Documentar el aprovisionamiento en una ficha de registro con todos los campos requeridos.

**Entregable:** Ficha de aprovisionamiento + capturas del Plan de pruebas ejecutado.

---

## Puntos clave — UD1

- La habilitación de recursos cubre servicios, usuarios, cómputo y almacenamiento; cada uno con sus propias cuotas y políticas.
- El **RBAC** (control de acceso basado en roles) aplica el principio de mínimo privilegio: cada usuario solo tiene los permisos que necesita.
- El **etiquetado** de recursos es imprescindible para imputar costes y auditar el uso.
- El **Plan de pruebas** es el documento que certifica que el entorno está listo para su explotación.
- La **documentación del aprovisionamiento** incluye recursos habilitados, fecha, responsable, límites y incidencias.
- La **eficiencia** en el uso de recursos (auto-shutdown, instancias spot, escalado automático) es una responsabilidad profesional.
- Las incidencias se clasifican por severidad y se gestionan con un ciclo de vida documentado.

---

## Criterios de evaluación — UD1

| Criterio | Indicador de logro |
|---|---|
| Habilita y asigna recursos | Activa los servicios necesarios, crea usuarios con RBAC y cuotas de cómputo/almacenamiento correctas |
| Asigna a centro de coste | Los recursos están etiquetados y vinculados al proyecto o centro de coste correspondiente |
| Verifica prerrequisitos | Ejecuta y documenta el checklist de prerrequisitos técnicos antes del inicio de la explotación |
| Plan de pruebas | Elabora y ejecuta un Plan de pruebas que cubre conectividad, autenticación, funcionalidad básica y rendimiento |
| Documenta el aprovisionamiento | Registra en el sistema de gestión: recursos, fecha, responsable, límites, incidencias y fecha de revisión |
| Comunica incidencias | Clasifica y comunica las incidencias detectadas siguiendo el protocolo de severidades |
| Uso eficiente | Configura auto-shutdown, alertas de coste y aplica buenas prácticas de eficiencia |

---

<!-- _class: lead -->

[← Volver a MP03](../index.md)


---

<!-- nav-slide -->

## Navegación

[Volver al módulo](../) &nbsp;·&nbsp; [UD2 · Valoración predictiva de dato… →](../UD2_Valoracion-predictiva-estructurados/)
