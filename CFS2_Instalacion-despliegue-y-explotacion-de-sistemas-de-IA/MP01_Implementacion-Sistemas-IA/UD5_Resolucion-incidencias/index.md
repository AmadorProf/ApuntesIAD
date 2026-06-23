---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD5 · Resolución de incidencias en plataformas de IA | MP01 · Implementación de sistemas de IA'
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

# UD5 · Resolución de incidencias en plataformas de IA

MP01 · Implementación de sistemas de IA

---

## Objetivos de aprendizaje

Al finalizar esta unidad, el alumno sera capaz de:

- Clasificar los tipos de incidencias que afectan a plataformas de IA y documentar correctamente los sintomas
- Analizar logs del sistema, de CUDA y de los frameworks de IA para diagnosticar la causa raiz de una incidencia
- Utilizar herramientas de monitorizacion (nvidia-smi, nvtop, htop, Prometheus) para identificar cuellos de botella
- Resolver incidencias de hardware GPU, instalacion, configuracion y aplicaciones siguiendo procedimientos estructurados
- Sustituir componentes averiados aplicando las medidas de seguridad correctas (ESD, validacion post-sustitucion)
- Priorizar incidencias segun su impacto y comunicar el estado de forma clara a los usuarios y al equipo tecnico

> **Resultado de aprendizaje:** Resuelve incidencias de explotacion garantizando el funcionamiento segun los niveles de servicio establecidos.

---

## Tipos de incidencias en plataformas de IA (I)

### Clasificacion por categoria

| Categoria | Subcategoria | Ejemplos reales |
|---|---|---|
| **Hardware** | GPU | GPU no detectada tras actualizacion de kernel; temperatura critica (> 90 C); fallo de ventilador; error ECC uncorrectable |
| **Hardware** | Almacenamiento | Disco NVMe con sectores defectuosos; RAID degradado; NVME desaparecido del bus PCIe |
| **Hardware** | Red | NIC InfiniBand no detectada; perdida de paquetes entre nodos de GPU; latencia anormal en red de almacenamiento |
| **Software** | Controlador/Driver | `nvidia-smi` no responde; CUDA version incompatible con PyTorch; segfault en cuDNN |
| **Software** | Framework | `CUDA out of memory` en PyTorch; error de importacion en transformers; Triton Inference Server no arranca |
| **Software** | Sistema operativo | Kernel panic; servicio systemd en estado failed; permisos incorrectos en `/dev/nvidia*` |
| **Rendimiento** | GPU | Utilizacion GPU al 0 % durante la inferencia; throttling termico; memory bandwidth bajo |
| **Rendimiento** | CPU/RAM | Cuello de botella en preprocesamiento de datos; swap activo durante inferencia |
| **Datos** | Pipeline | Corrupcion de datos en disco; error de deserializacion de modelo; checksum de modelo incorrecto |

---

## Tipos de incidencias en plataformas de IA (II)

### Impacto segun categoria

| Categoria | Impacto tipico en el servicio | Prioridad habitual |
|---|---|---|
| GPU no detectada | Servicio de inferencia completamente caido | P1 — Critica |
| Temperatura critica de GPU | Throttling o apagado de proteccion; degradacion severa | P1 — Critica |
| CUDA OOM (Out of Memory) | Fallos de inferencia en lotes grandes; servicio parcialmente caido | P2 — Alta |
| Servicio Triton en estado failed | Servicio de inferencia caido para todos los usuarios | P1 — Critica |
| Latencia de inferencia degradada | SLA incumplido; experiencia de usuario deteriorada | P2 — Alta |
| Permisos incorrectos en /dev/nvidia* | Usuarios sin acceso a GPU; servicio no arranca sin root | P2 — Alta |
| Error de importacion en libreria Python | Proceso de inferencia no arranca | P2 — Alta |
| Disco RAID degradado (1 disco fallido) | Sin impacto inmediato; riesgo de perdida de datos si falla el segundo | P3 — Media |
| Cuello de botella en CPU | Throughput reducido; SLA en riesgo | P3 — Media |

> **Nota:** la prioridad puede verse afectada por el SLA contractual con el cliente, el horario (incidencia fuera de horas laborables puede ser P2 aunque en horario seria P1) y el numero de usuarios afectados.

---

## Proceso de identificacion de la incidencia (I)

### Documentar antes de actuar

El error mas comun en la gestion de incidencias es intentar resolver antes de haber comprendido completamente el problema. Un diagnostico incompleto genera soluciones erroneas que pueden agravar la situacion.

**Que documentar al abrir una incidencia:**

| Elemento | Descripcion | Como obtenerlo |
|---|---|---|
| Sintoma exacto | El mensaje de error literal, tal como aparece | Copiar del terminal o del log; nunca parafrasear |
| Momento de inicio | Cuando empezo el problema (no cuando se detecto) | Correlacionar con logs del sistema |
| Reproducibilidad | Se produce siempre, con ciertos inputs, o de forma intermitente | Intentar reproducir de forma controlada |
| Alcance | Cuantos usuarios/procesos estan afectados | Consultar el sistema de tickets y el panel de Grafana |
| Cambios recientes | Actualizaciones, reinicios, cambios de configuracion en las ultimas 24-48 h | Revisar el Change Log y el historial de git |
| Entorno | Sistema operativo, version del driver, CUDA, framework | `uname -r`, `nvidia-smi`, `pip show torch` |
| Logs relevantes | Fragmentos de log que muestran el error | journalctl, dmesg, logs del framework |

---

## Proceso de identificacion de la incidencia (II)

### Reproduccion controlada del comportamiento

```bash
# 1. Identificar la version exacta del entorno
uname -r                                    # version del kernel
nvidia-smi                                  # version del driver y CUDA
python --version
pip show torch transformers triton 2>/dev/null | grep -E "^Name|^Version"

# 2. Intentar reproducir el error de forma minima
# Si el error es "CUDA out of memory" durante inferencia:
python -c "
import torch
model = torch.load('/models/mi_modelo.pt', map_location='cuda:0')
x = torch.randn(1, 3, 224, 224, device='cuda:0')  # batch=1, sin presion
with torch.no_grad():
    out = model(x)
print('Inferencia OK:', out.shape)
"

# 3. Capturar el traceback completo para el ticket
python mi_script.py 2>&1 | tee /tmp/incidencia_20240615_traceback.txt

# 4. Recoger informacion del sistema en el momento del fallo
nvidia-smi -q > /tmp/incidencia_20240615_nvidia.txt
free -h >> /tmp/incidencia_20240615_nvidia.txt
df -h >> /tmp/incidencia_20240615_nvidia.txt
```

---

## Herramientas de analisis de logs (I)

### Logs del sistema operativo

```bash
# --- JOURNALCTL: logs del sistema con systemd ---

# Ver los ultimos 100 errores del sistema
sudo journalctl -p err -n 100

# Ver logs de las ultimas 2 horas filtrando por errores de NVIDIA
sudo journalctl --since "2 hours ago" | grep -i "nvidia\|cuda\|gpu"

# Ver logs de un servicio especifico en tiempo real
sudo journalctl -u triton-server -f

# Ver logs desde el ultimo arranque del sistema
sudo journalctl -b 0

# --- DMESG: mensajes del kernel ---

# Ver todos los mensajes del kernel relacionados con GPU
sudo dmesg | grep -i "nvidia\|NVRM\|cuda"

# Ejemplo de error critico en dmesg:
# NVRM: GPU at PCI:0000:01:00: GPU-a2b3c4d5-e6f7-...
# NVRM: GPU Board Serial Number: [not supported]
# NVRM: Xid (PCI:0000:01:00): 79, pid='<unknown>', ...
# (Xid 79 = GPU fallen off the bus — fallo hardware grave)

# --- SYSLOG ---
sudo tail -f /var/log/syslog | grep -i "error\|warn\|nvidia"
```

---

## Herramientas de analisis de logs (II)

### Logs de CUDA y frameworks de IA

```bash
# --- NVIDIA BUG REPORT: recoleccion completa de informacion ---
# Genera un informe comprimido con toda la informacion del sistema NVIDIA
sudo nvidia-bug-report.sh
# Genera: nvidia-bug-report.log.gz en el directorio actual

# --- PYTORCH: activar logs de depuracion ---
# Variable de entorno para logs detallados de CUDA
TORCH_CPP_LOG_LEVEL=INFO python mi_script.py

# Logs de NCCL (comunicacion multi-GPU)
NCCL_DEBUG=INFO python mi_script_multigpu.py 2>&1 | grep "NCCL"

# --- TRITON INFERENCE SERVER ---
# Logs del servidor con nivel de detalle maximo
tritonserver --model-repository=/models --log-verbose=1 \
  --log-info=true --log-warning=true --log-error=true \
  2>&1 | tee /logs/triton_$(date +%Y%m%d).log

# Filtrar solo errores en los logs de Triton
grep -E "error|failed|FAILED" /logs/triton_20240615.log

# --- CUDA ERROR CODES en el traceback de Python ---
# RuntimeError: CUDA error: device-side assert triggered
#   → Indica error en el kernel CUDA, normalmente por input fuera de rango
# RuntimeError: CUDA out of memory.
#   → VRAM insuficiente para la operacion solicitada
# RuntimeError: CUDA error: no kernel image is available for execution on the device
#   → El binario compilado no es compatible con la arquitectura de la GPU
```

---

## Herramientas de monitorizacion (I)

### Monitorizacion de GPU y sistema

| Herramienta | Metrica principal | Uso tipico en diagnostico |
|---|---|---|
| `nvidia-smi` | Estado de GPU, VRAM, temperatura, potencia, procesos | Primera herramienta a consultar en cualquier incidencia de GPU |
| `nvtop` | Monitor interactivo de GPU en tiempo real (como htop para GPU) | Observar evolucion de uso de GPU/VRAM durante la incidencia |
| `htop` | CPU, RAM, procesos por nucleo | Detectar cuello de botella en CPU o saturacion de RAM |
| `iotop` | I/O de disco por proceso | Identificar proceso que satura el disco durante carga de modelo |
| `ss` / `netstat` | Conexiones de red activas, puertos en escucha | Verificar que el servidor de inferencia escucha en el puerto correcto |
| `iftop` | Trafico de red en tiempo real por interfaz | Diagnosticar saturacion de red InfiniBand o Ethernet |
| Prometheus + Grafana | Metricas historicas de GPU, CPU, red | Correlacionar inicio de incidencia con metricas de rendimiento |

```bash
# Instalacion de nvtop
sudo apt install nvtop

# nvidia-smi en modo de monitorizacion continua (refresco cada 1 s)
nvidia-smi -l 1

# Exportar metricas GPU en formato CSV para analisis posterior
nvidia-smi --query-gpu=timestamp,name,temperature.gpu,utilization.gpu,\
utilization.memory,memory.used,memory.free,power.draw \
--format=csv -l 5 >> /tmp/gpu_metrics.csv
```

---

## Herramientas de monitorizacion (II)

### Prometheus y Grafana para GPU — comandos clave

```bash
# Verificar que el exporter de NVIDIA Prometheus esta activo
systemctl status dcgm-exporter
# o alternativamente:
systemctl status nvidia-smi-exporter

# Consultar metricas GPU desde Prometheus (ejemplo con curl)
curl -s http://localhost:9090/api/v1/query \
  --data-urlencode 'query=DCGM_FI_DEV_GPU_TEMP' | python -m json.tool

# Metricas DCGM clave a monitorizar en Grafana:
# DCGM_FI_DEV_GPU_TEMP          → temperatura GPU (C)
# DCGM_FI_DEV_GPU_UTIL          → utilizacion GPU (%)
# DCGM_FI_DEV_MEM_COPY_UTIL     → utilizacion memoria (%)
# DCGM_FI_DEV_FB_USED           → VRAM usada (MB)
# DCGM_FI_DEV_POWER_USAGE       → potencia (W)
# DCGM_FI_DEV_SM_CLOCK          → frecuencia del SM (MHz)
# DCGM_FI_DEV_XID_ERRORS        → errores Xid (indica fallos hardware)

# Verificar estado de la red de un nodo de GPU cluster
ss -tulnp | grep -E "8000|8001|8002"   # puertos Triton HTTP/gRPC/Metrics
netstat -i                              # estadisticas de interfaz (paquetes perdidos)
```

---

## Diagnostico de incidencias de hardware GPU (I)

### Sintomas comunes y comandos de diagnostico

| Sintoma | Posible causa | Comando de diagnostico |
|---|---|---|
| `CUDA out of memory` | Modelo o batch demasiado grande para la VRAM disponible | `nvidia-smi --query-gpu=memory.used,memory.free --format=csv` |
| GPU no aparece en `nvidia-smi` | Fallo hardware, driver no cargado, GPU caida del bus PCIe | `lspci | grep -i nvidia` ; `dmesg | grep -i "Xid\|NVRM"` |
| Temperatura > 90 C | Ventilador averiado, pasta termica seca, obstruccion del airflow | `nvidia-smi -q -d TEMPERATURE` ; `ipmitool sdr type Fan` |
| Errores ECC uncorrectable | Fallo de celda de memoria GDDR/HBM | `nvidia-smi -q -d ECC` |
| Rendimiento severamente reducido | Throttling termico o de potencia | `nvidia-smi -q -d PERFORMANCE` ; buscar "Thermal Slowdown: Active" |
| `Xid 79` en dmesg | GPU fallen off the bus — fallo hardware grave | `dmesg | grep "Xid"` ; revisar slot PCIe y alimentacion |

```bash
# Ver todos los errores Xid de la GPU (historico completo)
sudo dmesg | grep "Xid"

# Xid mas relevantes:
# Xid 13: Graph engine exception — posible fallo de kernel CUDA
# Xid 31: GPU memory page fault
# Xid 48: Double Bit ECC Error (DBE) — celula de VRAM corrupta
# Xid 63: Row remapper recording pending
# Xid 79: GPU fallen off the bus — fallo hardware grave
# Xid 94: Contained channel error — GPU puede seguir funcionando

# Ver el estado completo de ECC
nvidia-smi -q -d ECC | grep -A5 "Aggregate"
```

---

## Diagnostico de incidencias de hardware GPU (II)

### Acciones correctivas por tipo de fallo

```bash
# --- CUDA OOM: reducir el uso de VRAM ---
# Opcion 1: reducir el tamano del batch en el cliente
# Opcion 2: activar fp16 o int8 en el servidor de inferencia
# Opcion 3: liberar cache de PyTorch desde el proceso
python -c "import torch; torch.cuda.empty_cache(); print('Cache limpiada')"

# Verificar que no hay procesos zombis ocupando VRAM
nvidia-smi --query-compute-apps=pid,process_name,used_memory \
  --format=csv,noheader,nounits
# Matar un proceso que retiene VRAM innecesariamente
sudo kill -9 <PID>

# --- GPU NO DETECTADA: verificar a nivel de bus ---
# Ver si la GPU aparece en el bus PCIe aunque el driver no la vea
lspci -nn | grep -i "NVIDIA\|VGA\|3D"

# Recargar el modulo del kernel de NVIDIA sin reiniciar
sudo rmmod nvidia_uvm nvidia_drm nvidia_modeset nvidia
sudo modprobe nvidia
nvidia-smi

# --- ERRORES ECC: retirar la GPU si los errores son uncorrectable ---
# Verificar si los errores ECC son corregibles (singlebit) o no corregibles (doublebit)
nvidia-smi -q -d ECC | grep -i "double\|uncorrectable"
# Si hay errores double-bit no corregibles → sustituir la GPU
```

---

## Diagnostico de incidencias de instalacion y configuracion

### Incompatibilidad de versiones y rutas mal configuradas

```bash
# --- INCOMPATIBILIDAD DRIVER / CUDA / PYTORCH ---
# Verificar la matriz de compatibilidad:
# Driver 525.xx → CUDA 12.0 max
# Driver 535.xx → CUDA 12.2 max
# Driver 545.xx → CUDA 12.3 max
# Driver 550.xx → CUDA 12.4 max

# Ver version del driver instalado
nvidia-smi | grep "Driver Version"

# Ver la version de CUDA que PyTorch espera
python -c "import torch; print(torch.version.cuda)"

# Ver la version de CUDA del toolkit instalado en el sistema
nvcc --version

# --- PATH VARIABLES MAL CONFIGURADAS ---
# Verificar que nvcc es accesible
which nvcc
echo $PATH | tr ':' '\n' | grep cuda

# Si nvcc no se encuentra, agregar CUDA al PATH
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# --- PERMISOS DE DISPOSITIVO ---
# Ver permisos de los nodos de dispositivo NVIDIA
ls -la /dev/nvidia*
# Salida esperada: crw-rw-rw- 1 root video 195, 0 ...

# Si los permisos son incorrectos
sudo chmod 666 /dev/nvidia*
sudo chmod 666 /dev/nvidiactl
sudo chmod 666 /dev/nvidia-uvm

# Alternativa: agregar el usuario al grupo video
sudo usermod -aG video $USER
```

---

## Reparacion o sustitucion de componentes

### Criterios para decidir: reparar vs. sustituir

| Situacion | Reparar | Sustituir |
|---|---|---|
| Ventilador de GPU averiado | Si el modelo admite recambio y la GPU esta en garantia | Si la GPU esta fuera de garantia y el coste de reparacion > 30 % del valor de sustitucion |
| Errores ECC double-bit (DRAM VRAM) | No — no se puede reparar la memoria HBM/GDDR soldada | Sustituir la GPU inmediatamente |
| Xid 79 repetidos (GPU off bus) | Probar reseat en slot PCIe primero | Si persiste tras reseat, sustituir |
| RAID degradado (1 disco fallido) | Sustituir el disco fallido y reconstruir el RAID | Solo sustituir el disco; el RAID se reconstruye solo |
| NIC InfiniBand averiada | — | Sustituir el modulo SFP o la tarjeta completa |

### Procedimiento de sustitucion de GPU en servidor

**Antes de la intervencion fisica:**

```bash
# 1. Anotar el estado actual
nvidia-smi -q > /backups/gpu_antes_sustitucion.txt

# 2. Detener todos los servicios que usen la GPU
sudo systemctl stop triton-server
sudo systemctl stop nvidia-persistenced

# 3. Descargar el modulo del kernel
sudo rmmod nvidia_uvm nvidia_drm nvidia_modeset nvidia
```

---

## Reparacion o sustitucion — procedimiento fisico y validacion

### Intervencion fisica: medidas de seguridad (ESD)

- Apagar el servidor completamente y desconectar el cable de alimentacion de la red electrica
- Esperar al menos **30 segundos** para que los condensadores se descarguen
- Usar **pulsera antiESD** conectada a una toma de tierra verificada antes de tocar cualquier componente
- No tocar los conectores dorados de la GPU ni el slot PCIe con las manos desnudas
- Sujetar la GPU por los bordes del PCB, nunca por el disipador ni los ventiladores
- Guardar la GPU retirada en bolsa antistatica

### Validacion post-sustitucion

```bash
# 1. Arrancar el servidor y verificar que la GPU aparece en el POST (BIOS/UEFI)

# 2. Verificar que el sistema operativo detecta la nueva GPU
lspci -nn | grep -i nvidia
sudo dmesg | grep -i "NVRM\|nvidia"

# 3. Cargar el modulo del kernel
sudo modprobe nvidia
nvidia-smi   # debe mostrar la nueva GPU con su numero de serie

# 4. Ejecutar el test de estres de GPU para validar el hardware
sudo apt install -y gpu-burn
gpu-burn 300   # estres durante 5 minutos; verificar ausencia de errores ECC

# 5. Reiniciar los servicios
sudo systemctl start nvidia-persistenced
sudo systemctl start triton-server
sudo systemctl status triton-server

# 6. Actualizar el inventario (CMDB) con el nuevo numero de serie de la GPU
nvidia-smi --query-gpu=name,serial,uuid --format=csv
```

---

## Resolucion de incidencias de aplicaciones (I)

### Reconfigurar el servidor de inferencia

El servidor de inferencia (Triton, TorchServe, vLLM) puede requerir reconfiguracion cuando cambia el hardware o los modelos disponibles.

```bash
# --- TRITON INFERENCE SERVER: diagnostico de configuracion ---

# Ver que modelos tiene cargados Triton
curl -s http://localhost:8000/v2/models | python -m json.tool

# Ver el estado de un modelo especifico
curl -s http://localhost:8000/v2/models/bert_classifier | python -m json.tool

# Recargar un modelo sin reiniciar el servidor
curl -X POST http://localhost:8000/v2/repository/models/bert_classifier/load

# Descargar un modelo de la memoria
curl -X POST http://localhost:8000/v2/repository/models/bert_classifier/unload

# --- VLLM: ajustar parametros si hay OOM ---
# Reducir el gpu-memory-utilization para dejar margen
python -m vllm.entrypoints.openai.api_server \
  --model /models/mistral-7b \
  --gpu-memory-utilization 0.80 \
  --max-model-len 4096 \
  --tensor-parallel-size 1

# Ver el log de errores de vLLM
sudo journalctl -u vllm-server -n 200 --no-pager | grep -i error
```

---

## Resolucion de incidencias de aplicaciones (II)

### Reinstalacion limpia del entorno Python y actualizacion de libreria problematica

```bash
# --- REINSTALACION LIMPIA DEL ENTORNO VIRTUAL ---

# 1. Hacer una copia de los requisitos antes de borrar
/opt/venvs/inference/bin/pip freeze > /backups/requirements_$(date +%Y%m%d).txt

# 2. Eliminar el entorno virtual corrupto
rm -rf /opt/venvs/inference

# 3. Crear un entorno limpio con la version de Python correcta
python3.11 -m venv /opt/venvs/inference

# 4. Instalar las dependencias desde el fichero de requisitos
/opt/venvs/inference/bin/pip install --upgrade pip
/opt/venvs/inference/bin/pip install -r /backups/requirements_20240615.txt

# --- ACTUALIZACION DE UNA LIBRERIA PROBLEMATICA ---
# Ejemplo: transformers falla al cargar un modelo con la version actual

# Identificar la version que rompe
pip show transformers | grep Version
# Version: 4.36.0

# Ver el changelog para identificar breaking changes
# https://github.com/huggingface/transformers/blob/main/CHANGELOG.md

# Probar con la version anterior
pip install "transformers==4.35.2"
python -c "from transformers import AutoModelForCausalLM; print('OK')"

# Si funciona, anclar la version en requirements.txt
echo "transformers==4.35.2  # pinned: 4.36.0 rompe carga de modelos llama" \
  >> /opt/venvs/inference/requirements.txt

# Alternativamente, instalar desde el commit estable de git
pip install git+https://github.com/huggingface/transformers@v4.35.2
```

---

## Pruebas finales de verificacion

### Checklist de cierre de incidencia

```bash
# --- SMOKE TEST: verificacion rapida post-resolucion ---
nvidia-smi && echo "[OK] Driver NVIDIA activo"
python -c "import torch; assert torch.cuda.is_available(), 'CUDA no disponible'; \
  print(f'[OK] CUDA disponible: {torch.cuda.get_device_name(0)}')"
curl -sf http://localhost:8000/v2/health/ready && echo "[OK] Triton listo"

# --- TEST DE CARGA: verificar que el servicio aguanta la carga normal ---
# Herramienta: perf_analyzer de Triton
/opt/triton-client/bin/perf_analyzer \
  -m bert_classifier \
  --concurrency-range 1:16 \
  --measurement-interval 5000 \
  -u localhost:8001 \
  --protocol grpc

# --- VALIDACION DE SLA ---
# Verificar que la latencia p99 esta dentro del umbral definido en el SLA
# Ejemplo: SLA = p99 < 200 ms para inferencia de clasificacion de texto
curl -s http://localhost:8000/metrics | grep "nv_inference_request_duration_us"
```

### Checklist de cierre formal

- [ ] Causa raiz identificada y documentada en el ticket
- [ ] Solucion aplicada y verificada mediante pruebas
- [ ] Latencia p99 dentro del umbral del SLA
- [ ] Servicio sin reinicios inesperados durante al menos 30 minutos
- [ ] Usuarios afectados notificados de la resolucion
- [ ] Ticket cerrado con la categoria de causa raiz correcta (ITIL: Root Cause)
- [ ] Accion preventiva creada si la incidencia es recurrente (Problem Management)

---

## Priorizacion por criticidad

### Matriz de priorizacion ITIL: P1 a P4

| Prioridad | Nombre | Impacto | Ejemplos tipicos | SLA resolucion | Escalado |
|---|---|---|---|---|---|
| **P1** | Critica | Servicio completamente caido para todos los usuarios | GPU no detectada; Triton Server caido; nodo de GPU sin respuesta | 1 h de resolucion / 15 min de primer contacto | Inmediato al responsable tecnico y al cliente |
| **P2** | Alta | Servicio parcialmente degradado o SLA en riesgo | CUDA OOM intermitente; latencia > 3x el umbral normal; 50 % de GPUs no disponibles | 4 h de resolucion / 1 h primer contacto | En 30 min si no hay avance |
| **P3** | Media | Impacto limitado; hay workaround disponible | Un modelo concreto no carga; rendimiento reducido pero dentro de SLA; RAID degradado | 8 h laborables / 2 h primer contacto | Si supera el tiempo de resolucion |
| **P4** | Baja | Sin impacto en el servicio; mejora o consulta | Optimizacion de parametros; solicitud de nuevo modelo; pregunta de configuracion | 5 dias laborables | No requerido |

> **Regla de escalado:** si en el 50 % del tiempo de resolucion no hay avance claro, escalar al siguiente nivel. Es mejor escalar pronto que llegar al fin del SLA sin resolucion.

---

## Comunicacion asertiva en la gestion de incidencias

### Principios de comunicacion durante una incidencia

- **Ser factual:** comunicar lo que se sabe con certeza; no especular sobre causas ante el cliente
- **Ser proactivo:** actualizar el estado segun el SLA aunque no haya novedades ("seguimos investigando")
- **Ser claro:** evitar jerga tecnica en las comunicaciones a usuarios no tecnicos
- **Ser honesto sobre los tiempos:** un tiempo estimado realista es mejor que uno optimista que no se cumple

### Plantilla de actualizacion de estado de incidencia

```
Asunto: [INC-2024-0891] Actualizacion de estado — Servicio de inferencia degradado

Estimados usuarios,

Les informamos de que estamos trabajando activamente en la resolucion de la
incidencia INC-2024-0891, reportada a las 09:15 h de hoy.

Estado actual: EN RESOLUCION
Causa identificada: incompatibilidad entre el nuevo kernel de Linux (6.5.0-35)
y el controlador NVIDIA 535.x instalado.
Accion en curso: instalando el controlador NVIDIA 550.x compatible con el kernel.
Impacto: el servicio de inferencia no esta disponible para todos los usuarios.
Workaround disponible: no existe workaround en este momento.
Proximo estado: 14:00 h (o antes si se resuelve antes)

Pedimos disculpas por los inconvenientes causados.

Equipo de Sistemas de IA
```

---

## Actividad practica

### Escenario: "GPU no detectada tras actualizacion de kernel"

**Situacion:** tras una actualizacion automatica del kernel de Ubuntu de la version `6.5.0-28` a la `6.5.0-35`, el servidor `srv-inference-01` muestra que `nvidia-smi` devuelve el error `NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver`. El servicio de Triton no arranca.

**Tarea: diagnosticar y resolver la incidencia siguiendo los pasos aprendidos.**

```bash
# Paso 1: verificar el kernel activo y el modulo NVIDIA
uname -r
lsmod | grep nvidia
# Resultado esperado: ninguna linea (el modulo no esta cargado)

# Paso 2: ver los errores del kernel relacionados
sudo dmesg | grep -i "nvidia\|NVRM\|module"
# Error probable: "nvidia: module verification failed: signature and/or required key missing"

# Paso 3: intentar cargar el modulo manualmente
sudo modprobe nvidia
# Error probable: "modprobe: ERROR: could not insert 'nvidia': Exec format error"

# Paso 4: verificar si el driver instalado tiene soporte para el nuevo kernel
dpkg -l | grep nvidia-driver
apt-cache policy nvidia-driver-535
# Ver si hay una version mas nueva compatible con el kernel 6.5.0-35

# Paso 5: solucionar — instalar el driver compatible
sudo apt update
sudo apt install --only-upgrade nvidia-driver-550
sudo reboot
```

**Tras el reinicio:** repetir los smoke tests de la diapositiva de pruebas finales y documentar la incidencia con causa raiz, solucion aplicada y accion preventiva (configurar `apt-mark hold linux-image-*` o sincronizar la ventana de actualizacion del kernel con la del driver).

---

## Puntos clave

- **Documentar antes de actuar:** un diagnostico incompleto lleva a soluciones erroneas. Recoger el traceback exacto, el entorno y los cambios recientes antes de tocar nada.
- **Los logs son la fuente de verdad:** `dmesg`, `journalctl`, `nvidia-bug-report.sh` y los logs del framework contienen la causa raiz de la mayoria de las incidencias. Aprende a leerlos.
- **Los errores Xid son senales criticas:** Xid 79 (GPU off bus) y Xid 48 (ECC double-bit) indican fallo hardware; no se resuelven con reinicios ni con actualizaciones de software.
- **La incompatibilidad kernel-driver es la causa mas frecuente de "GPU no detectada":** siempre verificar que el driver NVIDIA soporta la version del kernel activo tras cualquier actualizacion del sistema.
- **ESD no es opcional:** la descarga electrostatica puede destruir una GPU de forma no visible e inmediata. Pulsera antiESD y descarga del servidor antes de cualquier intervencion fisica.
- **Priorizar antes de ejecutar:** una incidencia P1 requiere accion inmediata y comunicacion proactiva. Una P4 puede planificarse. Confundir prioridades genera insatisfaccion del cliente y uso ineficiente del equipo tecnico.
- **Cerrar bien el ticket:** la causa raiz documentada y la accion preventiva son la diferencia entre resolver una incidencia y evitar que se repita.

---

## Criterios de evaluacion

| Criterio | Descripcion | Indicadores de logro |
|---|---|---|
| CE5.1 | Identifica y documenta incidencias correctamente | Recoge sintoma exacto, entorno, cambios recientes y reproducibilidad antes de diagnosticar |
| CE5.2 | Diagnostica mediante analisis de logs | Usa `journalctl`, `dmesg` y logs de framework para identificar la causa raiz |
| CE5.3 | Utiliza herramientas de monitorizacion adecuadas | Selecciona la herramienta correcta (nvidia-smi, nvtop, htop, Prometheus) segun el tipo de incidencia |
| CE5.4 | Resuelve incidencias de hardware GPU | Diagnostica correctamente errores Xid y ECC; sigue el procedimiento de sustitucion con medidas ESD |
| CE5.5 | Resuelve incidencias de instalacion y configuracion | Corrige incompatibilidades de version, variables de entorno y permisos de dispositivo |
| CE5.6 | Resuelve incidencias de aplicaciones | Reconfigura, reinstala o actualiza el entorno Python y el servidor de inferencia de forma correcta |
| CE5.7 | Prioriza y comunica correctamente | Asigna la prioridad P1-P4 correcta y redacta una actualizacion de estado clara y factual |

---

<!-- _class: lead -->

[← Volver a MP01](../)
