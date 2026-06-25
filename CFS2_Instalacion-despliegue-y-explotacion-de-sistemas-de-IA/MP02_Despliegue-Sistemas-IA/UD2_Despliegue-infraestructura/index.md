---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD2 · Despliegue de la infraestructura | MP02 · Despliegue de sistemas de IA'
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

# UD2 · Despliegue de la infraestructura

MP02 · Despliegue de sistemas de IA

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno sera capaz de:

- Montar y aprovisionar infraestructura propia (on-premise) para sistemas de IA
- Configurar el sistema operativo, bootloader, firmware, controladores y entornos de ejecucion
- Provisionar y configurar infraestructura como servicio (IaaS) en entornos cloud
- Verificar el funcionamiento y rendimiento de la infraestructura antes de usarla
- Documentar todas las intervenciones con el nivel de detalle requerido

> **Resultado de aprendizaje:** Despliega sistemas de IA en desarrollo o produccion, en infraestructura como servicio o instalaciones propias.

---

## Panorama: modalidades de infraestructura

### Comparativa on-premise vs. IaaS vs. hibrida

| Aspecto | On-premise | IaaS (nube) | Hibrida |
|---|---|---|---|
| Control del hardware | Total | Ninguno | Parcial |
| Tiempo de aprovisionamiento | Semanas/meses | Minutos | Variable |
| Coste inicial (CAPEX) | Alto | Bajo | Medio |
| Coste operativo (OPEX) | Bajo/medio | Variable (pay-per-use) | Variable |
| Escalabilidad | Limitada | Ilimitada en teoria | Flexible |
| Latencia de red interna | Muy baja | Dependiente de proveedor | Variable |
| Adecuada para | Datos sensibles, GPU dedicada | Picos de demanda, flexibilidad | Combinacion de ambas |

---

## Infraestructura propia: fase 1 — montaje fisico

### Proceso de aprovisionamiento fisico de un servidor de IA

1. **Recepcion y verificacion:** comprobar que el hardware recibido coincide con el pedido (modelo, serie, componentes)
2. **Montaje en rack:** instalacion en rack con gestion de cableado estructurado (cable management)
3. **Conexion de red:** cableado de red de datos, red de gestion (IPMI/iDRAC/iLO) y, si procede, red de alta velocidad (InfiniBand)
4. **Conexion de almacenamiento:** SAN, NAS o almacenamiento local (NVMe U.2)
5. **Encendido inicial:** verificacion del POST y acceso al firmware (BIOS/UEFI)
6. **Actualizacion de firmware:** firmware del servidor, de la GPU y de los controladores de red antes de instalar el SO

> El firmware debe actualizarse **antes** de instalar el SO para evitar incompatibilidades con los controladores.

---

## Infraestructura propia: fase 2 — sistema operativo

### Instalacion del SO mediante imagen base auditada

En entornos productivos no se instala el SO de forma interactiva, sino mediante **imágenes auditadas y preconfiguradas** (golden images):

```bash
# Ejemplo: arranque por PXE con una imagen base Ubuntu 22.04 LTS minimal
# El servidor arranca desde la red y recibe la imagen desde el servidor PXE
# La imagen incluye: SO minimal + agente de gestion + configuracion de red base

# Verificar integridad de la imagen antes de instalar
sha256sum ubuntu-22.04.4-server-amd64.iso
# Comparar con el hash publicado en https://releases.ubuntu.com
```

### Configuracion del bootloader (GRUB2)

- Configurar el orden de arranque correcto
- Habilitar arranque seguro (Secure Boot) si es requerido por la politica de seguridad
- Configurar parametros de kernel para alto rendimiento: `transparent_hugepage=always`, `isolcpus` para GPUs dedicadas

---

## Infraestructura propia: fase 3 — controladores y dependencias

### Instalacion de controladores GPU (ejemplo NVIDIA)

```bash
# 1. Deshabilitar el controlador nouveau (abierto, incompatible con CUDA)
echo "blacklist nouveau" | sudo tee /etc/modprobe.d/blacklist-nouveau.conf
sudo update-initramfs -u && sudo reboot

# 2. Instalar el controlador NVIDIA oficial
sudo apt install nvidia-driver-535  # version LTS para produccion

# 3. Instalar CUDA Toolkit (version compatible con el modelo a desplegar)
sudo apt install cuda-toolkit-12-3

# 4. Verificar instalacion
nvidia-smi
nvcc --version
```

### Entornos de ejecucion aislados

Para garantizar reproducibilidad, los entornos de ejecucion se aíslan:

| Mecanismo | Uso tipico |
|---|---|
| `virtualenv` / `conda` | Proyectos Python en metal desnudo |
| Contenedor Docker | Despliegues reproducibles y portables |
| Imagen de maquina virtual | Entornos con aislamiento total |

---

## Infraestructura propia: validacion de rendimiento

### Benchmarks antes de poner en produccion

| Prueba | Herramienta | Metrica objetivo |
|---|---|---|
| Rendimiento CPU | `stress-ng`, `sysbench` | OPS/s, temperatura bajo carga |
| Rendimiento GPU | `nvidia-smi dmon`, `gpu-burn` | TFLOPS, temperatura, ECC errors |
| Almacenamiento I/O | `fio` | IOPS, throughput, latencia |
| Red | `iperf3` | Ancho de banda, latencia, jitter |
| Inferencia del modelo | Script propio con batch fijo | Latencia P50/P99, throughput |

```bash
# Ejemplo: benchmark de almacenamiento con fio
fio --name=randread --rw=randread --bs=4k --ioengine=libaio \
    --iodepth=64 --runtime=60 --numjobs=4 --filename=/dev/nvme0n1 \
    --group_reporting
```

---

## Infraestructura como servicio: vision general

### Recursos a provisionar en IaaS para un sistema de IA

| Recurso | AWS | Azure | GCP |
|---|---|---|---|
| Instancia GPU | p3.2xlarge (V100) | NC6s_v3 (V100) | n1-standard-8 + T4 |
| Almacenamiento rapido | EBS gp3 (NVMe) | Premium SSD | Persistent SSD |
| Almacenamiento objetos | S3 | Blob Storage | Cloud Storage |
| Red privada | VPC | VNet | VPC |
| Balanceador de carga | ALB | Application GW | Cloud LB |

> En IaaS, el aprovisionamiento se realiza mediante **Infraestructura como Codigo (IaC)** para garantizar reproducibilidad y control de versiones.

---

## Infraestructura como servicio: IaC con Terraform

### Ejemplo: instancia de inferencia en AWS con Terraform

```hcl
resource "aws_instance" "inferencia_ia" {
  ami           = "ami-0a1b2c3d4e5f67890"  # Ubuntu 22.04 + CUDA 12.3
  instance_type = "g4dn.xlarge"            # 1x NVIDIA T4, 16 GB VRAM
  subnet_id     = aws_subnet.privada.id

  root_block_device {
    volume_type = "gp3"
    volume_size = 100
    iops        = 3000
    throughput  = 125
  }

  tags = {
    Name        = "inferencia-modelo-fraude-v3"
    Entorno     = "produccion"
    Proyecto    = "deteccion-fraude"
    Responsable = "equipo-mlops"
  }
}
```

---

## Infraestructura como servicio: red y seguridad

### Configuracion de red en IaaS

| Elemento | Configuracion recomendada |
|---|---|
| VPC / VNet | CIDR propio, subredes publicas y privadas separadas |
| Subred de inferencia | Privada, sin acceso directo desde internet |
| IP elastica / publica | Solo para el balanceador de carga, nunca en la instancia de inferencia |
| Grupo de seguridad | Reglas de entrada minimas: solo el balanceador y la red de gestion |
| Puertos abiertos | 8080/8443 (API), 9090 (metricas Prometheus), 22 (SSH solo desde bastion) |

```hcl
# Grupo de seguridad restrictivo en Terraform
resource "aws_security_group" "inferencia" {
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.balanceador.id]
  }
  egress { from_port = 0; to_port = 0; protocol = "-1"; cidr_blocks = ["0.0.0.0/0"] }
}
```

---

## Infraestructura como servicio: autoescalado

### Configuracion de autoescalado para cargas variables

El autoescalado permite adaptarse a picos de demanda sin sobredimensionar la infraestructura permanente.

| Parametro | Descripcion | Ejemplo |
|---|---|---|
| Capacidad minima | Instancias siempre activas | 2 instancias |
| Capacidad maxima | Limite de escalado | 10 instancias |
| Metrica de escalado | Condicion que dispara el escalado | CPU > 70 % durante 3 min |
| Politica de reduccion | Condicion para reducir instancias | CPU < 30 % durante 10 min |
| Cooldown | Tiempo entre ajustes de escalado | 300 segundos |

> Para modelos con arranque lento (carga del modelo en VRAM), se recomienda usar **escalado predictivo** en lugar de reactivo, o mantener un minimo de instancias "calientes".

---

## Infraestructura como servicio: persistencia y copias de seguridad

### Estrategia de persistencia para datos del sistema de IA

| Tipo de dato | Mecanismo de persistencia | Frecuencia de backup |
|---|---|---|
| Artefacto del modelo | Almacenamiento de objetos (S3, Blob) con versionado | Automatico en cada registro |
| Logs de inferencia | Almacenamiento de objetos con ciclo de vida | Diario, retencion 90 dias |
| Metricas de produccion | Base de datos de series temporales (InfluxDB, Prometheus) | Continuo, retencion configurable |
| Configuracion | Git + Secrets Manager | En cada cambio |
| Base de datos de la aplicacion | Snapshots automaticos | Diario + retencion 30 dias |

### Prueba de restauracion

> Una copia de seguridad que no se ha restaurado nunca no es una copia de seguridad: es una esperanza. Programar pruebas de restauracion periodicas.

---

## Documentacion de intervenciones

### Que registrar en cada intervencion de infraestructura

La documentacion de intervenciones es un requisito tanto operativo como normativo. Debe incluir:

| Campo | Descripcion | Ejemplo |
|---|---|---|
| Fecha y hora | ISO 8601, con zona horaria | 2025-03-15T14:32:00+01:00 |
| Responsable | Nombre y rol | Maria Garcia, Tecnico MLOps |
| Tipo de intervencion | Aprovisionamiento, actualizacion, incidencia... | Aprovisionamiento inicial |
| Resumen | Descripcion breve de lo realizado | Instalacion de Ubuntu 22.04 + CUDA 12.3 en srv-ia-01 |
| Versiones | Imagen, SO, firmware, controladores | Ubuntu 22.04.4, GRUB 2.06, NVIDIA driver 535 |
| Resultado | Exito / fallo / parcial | Exito |
| Logs adjuntos | Referencia a los logs del proceso | /var/log/install-2025-03-15.log |

---

## Actividad practica: despliegue de infraestructura con Terraform

### Escenario

Un equipo debe desplegar la infraestructura para un servicio de inferencia de un modelo de clasificacion de imagenes. El modelo requiere 8 GB de VRAM, alta disponibilidad (al menos 2 instancias activas) y latencia < 200 ms en P99.

### Tarea

Disenar y documentar (no ejecutar en un entorno real) la infraestructura IaaS necesaria:

1. Identificar el tipo de instancia adecuado en al menos 2 proveedores cloud
2. Definir la configuracion de red (VPC, subredes, grupos de seguridad)
3. Establecer la politica de autoescalado con metricas y umbrales justificados
4. Definir la estrategia de persistencia y backup para el artefacto del modelo
5. Redactar una ficha de intervencion completa para el aprovisionamiento

### Entregable

Documento con diagrama de arquitectura (descripcion textual), codigo Terraform esquematico y ficha de intervencion.

---

## Puntos clave de la UD2

- El aprovisionamiento on-premise sigue un orden riguroso: fisico → firmware → SO → controladores → dependencias. Invertir el orden causa problemas de compatibilidad dificiles de diagnosticar
- Las **golden images** garantizan que todos los servidores parten del mismo estado conocido y auditado
- En IaaS, la infraestructura como codigo (Terraform, CloudFormation) es imprescindible para la reproducibilidad y el control de cambios
- El autoescalado debe configurarse con margenes amplios: el tiempo de inicio de una instancia con un modelo grande puede ser de varios minutos
- Ninguna intervencion sobre infraestructura se realiza sin registro: fecha, responsable, resumen, versiones y logs adjuntos
- Las pruebas de restauracion de backups son tan importantes como las propias copias de seguridad

---

## Criterios de evaluacion — UD2

| Criterio | Indicadores de logro |
|---|---|
| Monta infraestructura propia | Sigue el orden correcto de aprovisionamiento; actualiza firmware antes de instalar el SO; verifica cada fase |
| Configura infraestructura IaaS | Usa IaC para el aprovisionamiento; configura red con subred privada para inferencia; aplica grupos de seguridad minimos |
| Configura autoescalado | Define metricas de escalado justificadas; establece capacidades minima y maxima; considera el tiempo de inicio del modelo |
| Verifica funcionamiento y rendimiento | Ejecuta benchmarks documentados para CPU, GPU, almacenamiento y red |
| Documenta las intervenciones | Registra todos los campos requeridos; adjunta logs; actualiza el inventario |

---

[← Volver a MP02](../index.md)


---

<!-- nav-slide -->

## Navegación

[← UD1 · Preparación del despliegue](../UD1_Preparacion-despliegue/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD3 · Instalación de aplicaciones d… →](../UD3_Instalacion-aplicaciones-despliegue/)
