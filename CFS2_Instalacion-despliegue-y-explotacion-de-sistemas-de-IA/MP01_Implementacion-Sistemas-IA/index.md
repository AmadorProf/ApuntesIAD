---
marp: true
theme: default
paginate: true
size: 16:9
header: 'MP01 · Implementación de sistemas de IA'
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
section.lead h1 { font-size: 2.2em; text-align: center; margin-top: 100px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f0fdf4; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
</style>

<!-- _class: lead -->

# MP01 · Implementación de sistemas de IA

CFS — Instalación, despliegue y explotación de sistemas de IA (IAD)

---

## Ficha del módulo

| Campo | Valor |
|---|---|
| Código | **MP01** |
| Estándar de competencia | ECP2494_3 · Nivel 3 |
| Familia profesional | Inteligencia Artificial y Data |
| Duración | **190 h** |
| Curso | **1.º** |

> **Competencia que desarrolla:** gestionar el ciclo de vida de los componentes de equipos y aplicaciones en sistemas de IA mediante configuración, inventariado y actualización, resolviendo incidencias técnicas para garantizar la disponibilidad y explotación óptima de la plataforma.

---

## Estructura del módulo

| # | Unidad didáctica |
|---|---|
| **UD1** | Integración de componentes físicos y equipos |
| **UD2** | Administración de componentes de aplicaciones |
| **UD3** | Implementación de componentes para su explotación |
| **UD4** | Actualización de componentes |
| **UD5** | Resolución de incidencias en plataformas de IA |
| **UD6** | Prevención de riesgos y gestión de residuos |

---

<!-- _class: lead -->

# UD1
## Integración de componentes físicos y equipos

---

## UD1 · Tipología de componentes físicos en sistemas de IA

| Categoría | Ejemplos |
|---|---|
| **Captación y percepción** | Cámaras multiespectrales, micrófonos, lidares, sensores |
| **IoT y embebidos** | Raspberry Pi, NVIDIA Jetson, PLCs industriales |
| **Robótica** | Brazos robóticos, AGVs, drones industriales |
| **Procesamiento** | Servidores GPU (A100, H100), FPGAs, workstations |
| **Infraestructura** | Switches de red, SAIs, sistemas de refrigeración |

> Cada componente debe quedar **registrado en el sistema de gestión** con su funcionalidad, tipología, características técnicas y estado.

---

## UD1 · Registro e inventario de componentes

**Datos mínimos por componente en el sistema de gestión:**

| Campo | Descripción |
|---|---|
| ID único | Identificador irrepetible del componente |
| Tipología | Categoría funcional |
| Fabricante y modelo | Identificación exacta del hardware |
| Configuración | Parámetros de instalación y ajuste |
| Localización | Rack, sala, nodo, dispositivo padre |
| Estado | Operativo · En mantenimiento · Fuera de servicio |
| Fecha de alta | Cuándo se incorporó al sistema |

---

## UD1 · Manipulación segura y eficiencia energética

**Seguridad en la manipulación (PRL):**

- ⚡ **Riesgos eléctricos:** desconectar antes de manipular, verificar tierra
- 🔌 **Descargas electrostáticas (ESD):** pulsera antiestática, alfombrillas ESD
- 🧤 **EPI:** guantes antiestáticos, calzado de seguridad
- 📋 **Documentar** incidencias, fechas y características de instalación

**Eficiencia energética y economía circular:**
- Seleccionar componentes con certificaciones de eficiencia (80 PLUS, Energy Star)
- Reducir la huella de carbono reutilizando hardware cuando sea posible
- Gestionar correctamente el fin de vida de los equipos (RAEE)

---

<!-- _class: lead -->

# UD2
## Administración de componentes de aplicaciones

---

## UD2 · Tipos de componentes de software en IA

**Componentes generales:**

| Componente | Ejemplos |
|---|---|
| Sistema operativo | Ubuntu 22.04 LTS, RHEL, Windows Server |
| Aplicaciones de base | Python, Java Runtime, .NET |
| Entornos de ejecución | CUDA, ROCm, OpenVINO |
| Librerías de ML | PyTorch, TensorFlow, scikit-learn |

**Componentes específicos de IA:**

| Componente | Ejemplos |
|---|---|
| Frameworks de despliegue | Triton Inference Server, TF Serving, BentoML |
| Herramientas de MLOps | MLflow, DVC, Airflow, Kubeflow |
| Lenguajes de modelado | PMML, ONNX, GGUF |

---

## UD2 · Gestión de versiones, licencias y dependencias

**Documentación de cada componente:**

```
nombre: PyTorch
versión: 2.1.0
licencia: BSD-3-Clause
dependencias: CUDA 12.1, cuDNN 8.9
requisitos: 8 GB VRAM mínimo
fecha_instalación: 2024-09-15
hash_verificación: sha256:abc123...
```

**Control de licencias:**
- Inventario actualizado de licencias propietarias y sus condiciones
- Cumplimiento de restricciones de distribución y uso comercial
- Gestión de renovaciones y caducidades

---

<!-- _class: lead -->

# UD3
## Implementación de componentes para su explotación

---

## UD3 · Proceso de instalación y configuración

**Secuencia de implementación:**

1. **Categorización** del componente según características y requisitos
2. **Verificación de prerrequisitos:** recursos disponibles, compatibilidad de versiones
3. **Instalación** según documentación técnica oficial:
   - SO, entornos de ejecución, librerías y dependencias de ML
   - Orden de instalación respetando dependencias
4. **Configuración** de parámetros según el entorno (dev, staging, prod)
5. **Pruebas de funcionamiento** antes de dar por válida la instalación
6. **Documentación** de incidencias, parámetros y registros

---

## UD3 · Verificación de compatibilidad

**Matriz de compatibilidad típica (ejemplo GPU):**

| Componente | Versión | Compatible con |
|---|---|---|
| Driver NVIDIA | 535.x | CUDA 12.1 |
| CUDA | 12.1 | cuDNN 8.9, PyTorch 2.1 |
| cuDNN | 8.9 | TensorFlow 2.14, PyTorch 2.1 |
| PyTorch | 2.1.0 | Python 3.8–3.11 |

> **Antes de instalar:** consultar siempre la matriz de compatibilidad oficial del fabricante o del framework.

---

<!-- _class: lead -->

# UD4
## Actualización de componentes

---

## UD4 · Gestión del ciclo de actualización

**Tipos de actualización:**

| Tipo | Descripción | Urgencia |
|---|---|---|
| **Parche de seguridad** | Corrige vulnerabilidades (CVE) | Inmediata |
| **Bugfix** | Corrige errores sin nuevas funciones | Alta |
| **Minor** | Nuevas funciones, compatible hacia atrás | Media |
| **Major** | Cambios de arquitectura, puede romper compatibilidad | Planificada |

**Proceso:**
1. Revisar versiones actuales vs. disponibles
2. Consultar changelog y notas de compatibilidad
3. Realizar prueba en entorno de staging
4. Aplicar en producción con ventana de mantenimiento
5. Verificar y documentar

---

## UD4 · Gestión del fin de ciclo de vida (EOL)

**Señales de obsolescencia:**
- El fabricante anuncia *End of Life* (EOL) sin soporte de seguridad
- La versión ya no recibe parches ni actualizaciones
- Incompatibilidad con nuevas versiones de dependencias clave

**Acciones al alcanzar el EOL:**
- Planificar la migración con antelación suficiente
- Borrado seguro de datos antes de retirar el componente
- Desinstalación de licencias del inventario
- Tratamiento de RAEE para hardware (ver UD6)

**Sostenibilidad:** prolongar la vida útil minimiza el impacto ambiental y reduce costes.

---

<!-- _class: lead -->

# UD5
## Resolución de incidencias en plataformas de IA

---

## UD5 · Proceso de diagnóstico y resolución

**Ciclo de resolución de incidencias:**

```
1. IDENTIFICACIÓN
   Reproducir el comportamiento según la documentación de la incidencia

2. DIAGNÓSTICO
   Análisis de logs y herramientas de monitorización
   (journalctl, dmesg, nvidia-smi, top, netstat…)

3. RESOLUCIÓN
   Hardware: reconfiguración, reparación o sustitución de componente
   Software: reconfiguración, reinstalación o actualización

4. VERIFICACIÓN
   Pruebas finales que confirmen la resolución sin efectos secundarios

5. DOCUMENTACIÓN
   Registro de causa, impacto, acción tomada y resultado
```

---

## UD5 · Priorización y comunicación de incidencias

**Niveles de criticidad:**

| Nivel | Impacto | Tiempo de respuesta |
|---|---|---|
| **P1 — Crítica** | Sistema de producción caído | Inmediato |
| **P2 — Alta** | Degradación significativa de servicio | < 2 h |
| **P3 — Media** | Funcionalidad reducida, workaround disponible | < 8 h |
| **P4 — Baja** | Afecta solo a entorno de desarrollo | Planificada |

**Comunicación:**
- Informar con claridad y asertividad al equipo afectado
- Actualizar el estado de la incidencia en el sistema de ticketing
- Escalar si la resolución supera el tiempo acordado en el SLA

---

<!-- _class: lead -->

# UD6
## Prevención de riesgos y gestión de residuos

---

## UD6 · Ergonomía y prevención en el puesto técnico

**Ergonomía en instalaciones de hardware:**

| Factor | Medida |
|---|---|
| Postura | Silla ajustable, monitor a la altura de los ojos |
| Carga física | Usar carros para equipos pesados, no superar 25 kg manualmente |
| Fatiga visual | Pantallas anti-reflejo, iluminación adecuada, descansos |
| Ambiente | Temperatura 18–22 °C, ruido < 65 dB, ventilación suficiente |

**Actuación ante emergencias:**
- Conocer el Plan de emergencias del centro
- Protocolo de evacuación y punto de encuentro
- Manejo de extintores apropiados para fuego eléctrico (CO₂, polvo seco)

---

## UD6 · Gestión de residuos tecnológicos (RAEE)

**Marco normativo:** Directiva RAEE (2012/19/UE) · RD 110/2015

**Proceso de gestión:**

1. **Recogida** y separación del residuo del flujo general
2. **Clasificación** por tipo: equipos de grandes dimensiones, pantallas, pequeños electrodomésticos
3. **Almacenaje** en zona habilitada, sin mezclar con residuos ordinarios
4. **Entrega** a gestor autorizado con certificado de destrucción
5. **Registro** del residuo gestionado con número de certificado

**Economía circular:** reutilizar componentes en buen estado antes de proceder al reciclaje.

---

## Criterios de evaluación — MP01

- Registra y clasifica componentes garantizando trazabilidad
- Actualiza el sistema de gestión ante cambios
- Manipula equipos según normas de PRL y ESD
- Documenta versiones, licencias y dependencias de software
- Verifica compatibilidad y recursos antes de instalar
- Identifica y aplica actualizaciones; gestiona el EOL
- Diagnostica con logs y monitorización; resuelve incidencias
- Aplica criterios ergonómicos y gestiona residuos según normativa

---

<!-- _class: lead -->

# MP01 · Implementación de sistemas de IA

**190 h · Curso 1.º · ECP2494_3 · Nivel 3**

*CFS — Instalación, despliegue y explotación de sistemas de IA (IAD)*
