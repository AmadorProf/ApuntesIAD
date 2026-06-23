---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD4 · Actualización de componentes | MP01 · Implementación de sistemas de IA'
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

# UD4 · Actualización de componentes

MP01 · Implementación de sistemas de IA

---

## Objetivos de aprendizaje

Al finalizar esta unidad, el alumno sera capaz de:

- Identificar versiones instaladas y detectar componentes obsoletos mediante herramientas especializadas
- Clasificar los tipos de actualizaciones y aplicar el procedimiento adecuado en cada caso
- Ejecutar actualizaciones de sistema y paquetes Python con estrategia de backup y rollback
- Verificar la estabilidad del sistema tras una actualización mediante pruebas estructuradas
- Documentar los cambios aplicados siguiendo el modelo ITIL de gestion del cambio
- Gestionar el fin de ciclo de vida del hardware de forma segura y sostenible (RAEE, borrado seguro, desinstalacion de licencias)

> **Resultado de aprendizaje:** Actualiza los componentes de equipos, programas y aplicaciones garantizando el funcionamiento y la compatibilidad del sistema.

---

## Revision de versiones — herramientas de deteccion (I)

### Sistema operativo y controladores

```bash
# Version del sistema operativo
lsb_release -a
cat /etc/os-release

# Version del kernel de Linux
uname -r

# Controlador NVIDIA instalado
nvidia-smi
cat /proc/driver/nvidia/version

# Version del toolkit CUDA
nvcc --version
/usr/local/cuda/bin/nvcc --version

# Actualizaciones de sistema disponibles (Debian/Ubuntu)
sudo apt update && apt list --upgradable 2>/dev/null

# Paquetes con actualizaciones de seguridad pendientes
apt list --upgradable 2>/dev/null | grep -i security
```

---

## Revision de versiones — herramientas de deteccion (II)

### Entornos Python y paquetes de IA

```bash
# Paquetes Python desactualizados en el entorno activo
pip list --outdated

# Formato tabla con version instalada y ultima disponible
pip list --outdated --format=columns

# Paquetes desactualizados en entorno virtual especifico
/opt/venvs/inference/bin/pip list --outdated

# Informacion detallada de un paquete concreto
pip show torch
pip show transformers
```

### Tabla de ejemplo: estado de versiones en servidor de inferencia

| Componente | Instalada | Disponible | Estado |
|---|---|---|---|
| Ubuntu | 22.04.3 LTS | 22.04.4 LTS | Actualizacion disponible |
| Controlador NVIDIA | 535.129 | 550.54.14 | Actualizacion disponible |
| CUDA Toolkit | 12.1 | 12.4 | Minor disponible |
| PyTorch | 2.1.2 | 2.3.1 | Minor disponible |
| transformers | 4.36.0 | 4.40.2 | Minor disponible |
| numpy | 1.24.4 | 1.26.4 | Minor disponible |

---

## Deteccion de obsolescencia — senales EOL (I)

### Que significa End of Life (EOL)

Un componente llega a su fin de vida util cuando el fabricante o la comunidad deja de publicar parches de seguridad. A partir de ese momento, cualquier vulnerabilidad descubierta queda sin corregir.

**Senales de obsolescencia a vigilar:**

- El fabricante anuncia fecha de EOL (Ubuntu LTS: 5 anos de soporte estandar)
- Aparicion de CVEs sin parche disponible para la version instalada
- La libreria deja de ser compatible con nuevas versiones del controlador CUDA
- El proveedor de hardware deja de publicar firmware actualizado
- La distribucion de Linux elimina el paquete de sus repositorios oficiales

### Fuentes de informacion autorizadas

| Fuente | URL | Uso |
|---|---|---|
| CVE Database (NVD) | nvd.nist.gov | Buscar CVEs por componente y version |
| Ubuntu Security Notices | ubuntu.com/security/notices | Alertas de seguridad para paquetes Ubuntu |
| NVIDIA Security Bulletins | nvidia.com/en-us/security | Vulnerabilidades en controladores y CUDA |
| PyTorch Release Notes | pytorch.org/docs/stable/notes | EOL de versiones PyTorch |
| endoflife.date | endoflife.date | Calendario de EOL de cientos de productos |

---

## Deteccion de obsolescencia — ciclos de vida (II)

### Tabla de ciclos de vida de componentes clave en plataformas de IA

| Componente | Version actual | EOL | Soporte LTS hasta | Accion recomendada |
|---|---|---|---|---|
| Ubuntu 20.04 LTS | 20.04.6 | Abr 2025 (estandar) | Abr 2030 (ESM) | Migrar a 22.04 LTS |
| Ubuntu 22.04 LTS | 22.04.4 | Abr 2027 (estandar) | Abr 2032 (ESM) | Mantener con parches |
| Python 3.8 | 3.8.20 | Oct 2024 | — | Migrar a 3.11 o 3.12 |
| Python 3.11 | 3.11.9 | Oct 2027 | — | Actual, usar |
| CUDA 11.x | 11.8 | Sin fecha oficial | — | Actualizar a CUDA 12.x |
| CUDA 12.x | 12.4 | Activo | — | Recomendado |
| PyTorch 1.x | 1.13.1 | EOL alcanzado | — | Migrar a 2.x urgente |
| PyTorch 2.x | 2.3.1 | Activo | — | Mantener actualizado |

> **Regla practica:** si un componente lleva mas de 12 meses sin recibir actualizaciones de seguridad, debe planificarse su sustitucion antes del proximo ciclo de mantenimiento.

---

## Tipos de actualizaciones

### Clasificacion segun alcance e impacto

| Tipo | Descripcion | Urgencia | Procedimiento | Riesgo |
|---|---|---|---|---|
| Parche de seguridad | Corrige una CVE activa. No anade funcionalidad. | Critica — aplicar en 72 h | Entorno de prueba, luego produccion | Bajo si se sigue el procedimiento |
| Bugfix | Corrige un error funcional sin CVE. | Alta — en el proximo ciclo | Prueba de regresion + produccion | Bajo-medio |
| Minor (ej. 2.1 → 2.2) | Nuevas funcionalidades, compatible hacia atras. | Media — planificar | Entorno staging completo + tests | Medio |
| Major (ej. 1.x → 2.x) | Cambios de API, posible rotura de compatibilidad. | Baja — solo si es necesario | Proyecto de migracion formal | Alto |
| Firmware/controlador | Actualiza el firmware del hardware o el driver. | Segun CVE o problema activo | Requiere reinicio; ventana de mantenimiento | Medio-alto |

### Norma general de version semantica (SemVer)

`MAYOR.MENOR.PARCHE` — ejemplo: `2.3.1`

- **PARCHE** (2.3.0 → 2.3.1): solo correccion de errores. Actualizar siempre.
- **MENOR** (2.2 → 2.3): nueva funcionalidad compatible. Actualizar con pruebas.
- **MAYOR** (1.x → 2.x): puede romper la API. Requiere analisis previo.

---

## Procedimiento de aplicacion de parches — preparacion

### Fase 1: evaluacion y backup

```bash
# 1. Documentar el estado actual antes de cualquier cambio
pip freeze > /backups/$(date +%Y%m%d)_requirements_before.txt
dpkg -l > /backups/$(date +%Y%m%d)_packages_before.txt
nvidia-smi > /backups/$(date +%Y%m%d)_nvidia_before.txt

# 2. Snapshot del disco del sistema (si se usa LVM)
sudo lvcreate -L10G -s -n snap_system /dev/vg0/system
# En entornos virtualizados: tomar snapshot de la VM antes

# 3. Crear un entorno de prueba clonado
python -m venv /opt/venvs/inference_test
cp -r /opt/venvs/inference/* /opt/venvs/inference_test/

# 4. Verificar espacio disponible antes de actualizar
df -h /
df -h /var
```

### Principio del entorno de prueba (staging)

Toda actualizacion que pueda afectar a un servicio en produccion debe validarse primero en un entorno identico al productivo pero aislado. Solo se aplica en produccion tras superar las pruebas de verificacion.

---

## Procedimiento de aplicacion de parches — ejecucion

### Fase 2: aplicacion y rollback

```bash
# --- ACTUALIZACION DE PAQUETES DE SISTEMA (Debian/Ubuntu) ---

# Actualizar solo parches de seguridad
sudo unattended-upgrade --dry-run   # simulacion
sudo unattended-upgrade             # aplicacion real

# Actualizar un paquete especifico
sudo apt update && sudo apt install --only-upgrade nvidia-driver-550

# --- ACTUALIZACION DE PAQUETES PYTHON ---

# Actualizar un paquete a la version mas reciente estable
pip install --upgrade torch==2.3.1

# Actualizar todos los paquetes outdated (con precaucion)
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d= -f1 | xargs pip install --upgrade

# Actualizar con restriccion de version para evitar rotura
pip install "transformers>=4.40,<5.0"

# --- ROLLBACK si algo falla ---

# Restaurar paquetes Python al estado anterior
pip install -r /backups/20240615_requirements_before.txt

# Rollback del controlador NVIDIA a la version anterior
sudo apt install nvidia-driver-535=535.129.03-0ubuntu1
```

---

## Pruebas de verificacion post-actualizacion (I)

### Smoke tests — verificacion rapida de que el sistema arranca

```bash
# 1. Verificar que el controlador NVIDIA sigue activo
nvidia-smi
# Salida esperada: tabla con GPU detectada, driver version, CUDA version

# 2. Verificar que Python y PyTorch cargan correctamente
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
# Salida esperada: 2.3.1  /  True

# 3. Verificar disponibilidad de GPU desde PyTorch
python -c "import torch; print(torch.cuda.get_device_name(0))"
# Salida esperada: NVIDIA A100 80GB PCIe  (o el modelo instalado)

# 4. Test de inferencia minima con un modelo cargado
python -c "
from transformers import pipeline
pipe = pipeline('text-classification', model='distilbert-base-uncased-finetuned-sst-2-english', device=0)
result = pipe('El sistema funciona correctamente')
print(result)
"

# 5. Verificar que el servicio de inferencia responde
curl -s http://localhost:8000/health | python -m json.tool
```

---

## Pruebas de verificacion post-actualizacion (II)

### Benchmarks de rendimiento GPU

```bash
# Monitorizar GPU durante una inferencia de prueba (cada 2 segundos)
nvidia-smi dmon -s pucvmet -d 2

# Columnas clave en la salida de nvidia-smi dmon:
# pwr  = potencia consumida (W)
# temp = temperatura (C)
# sm   = utilizacion de SM (%)
# mem  = utilizacion de memoria (%)
# enc/dec = actividad del codificador/decodificador de video

# Benchmark de memoria GPU con PyTorch
python -c "
import torch, time
device = 'cuda:0'
# Reservar un tensor grande para verificar VRAM disponible
x = torch.randn(4096, 4096, device=device)
start = time.time()
for _ in range(100):
    y = torch.matmul(x, x)
torch.cuda.synchronize()
elapsed = time.time() - start
print(f'VRAM libre: {torch.cuda.mem_get_info()[0]/1e9:.1f} GB')
print(f'Tiempo benchmark: {elapsed:.2f}s')
"

# Comparar latencia de inferencia antes y despues
# Guardar resultado en fichero para comparacion
echo "$(date) POST-UPDATE: $(python benchmark_inferencia.py)" >> /logs/benchmark_history.log
```

> **Criterio de exito:** latencia de inferencia no debe aumentar mas de un 5 % respecto al valor registrado antes de la actualizacion.

---

## Estabilidad del sistema — monitorizacion post-actualizacion (I)

### Periodo de observacion recomendado

Tras cualquier actualizacion mayor de controlador, CUDA o framework de IA, se recomienda un periodo de monitorizacion activa de **48-72 horas** antes de considerar la actualizacion estabilizada.

### Metricas criticas a vigilar

| Metrica | Herramienta | Umbral de alarma | Posible causa si supera |
|---|---|---|---|
| Temperatura GPU | `nvidia-smi -q -d TEMPERATURE` | > 83 C en A100/H100 | Pasta termica, ventilacion, TDP mal configurado |
| Utilizacion de VRAM | `nvidia-smi --query-gpu=memory.used --format=csv` | > 95 % | Memory leak post-update en el framework |
| Latencia de inferencia (p99) | Prometheus + Grafana | + 10 % sobre baseline | Regresion de rendimiento en nueva version |
| Errores en syslog | `journalctl -p err -n 100` | Cualquier CUDA error | Incompatibilidad driver/kernel |
| Uptime del servicio | Systemd / supervisor | Cualquier restart inesperado | Crash del proceso de inferencia |

---

## Estabilidad del sistema — monitorizacion post-actualizacion (II)

### Comandos de monitorizacion continua

```bash
# Ver errores del kernel relacionados con NVIDIA en tiempo real
sudo dmesg -w | grep -i nvidia

# Revisar el log del servicio de inferencia (Triton Inference Server)
sudo journalctl -u triton-server -f --since "1 hour ago"

# Consultar consumo de VRAM de todos los procesos GPU
nvidia-smi --query-compute-apps=pid,process_name,used_memory \
  --format=csv,noheader,nounits

# Watchdog simple: alertar si VRAM supera el 95 %
watch -n 10 "nvidia-smi --query-gpu=memory.used,memory.total \
  --format=csv,noheader,nounits | awk -F',' '{if(\$1/\$2 > 0.95) print \"ALERTA VRAM\", \$0}'"

# Exportar metricas GPU a fichero cada 5 minutos (48 h de observacion)
for i in $(seq 1 576); do
  echo "$(date +%Y-%m-%dT%H:%M:%S),$(nvidia-smi --query-gpu=temperature.gpu,\
memory.used,power.draw --format=csv,noheader,nounits)" \
    >> /logs/gpu_postupdate_$(date +%Y%m%d).csv
  sleep 300
done &
```

---

## Documentacion de cambios

### El registro de cambio (Change Log)

Toda actualizacion aplicada a un sistema en produccion debe quedar documentada. El estandar ITIL v4 denomina esto **Registro de Cambio** (Change Record). Es obligatorio para:

- Auditorias de seguridad (ISO 27001, ENS)
- Diagnostico de incidencias futuras
- Trazabilidad del estado del sistema

### Formato de ticket de cambio ITIL (campos obligatorios)

| Campo | Descripcion | Ejemplo |
|---|---|---|
| ID del cambio | Identificador unico | CHG-2024-0312 |
| Fecha y hora | Cuando se aplico | 2024-06-15 02:00 UTC |
| Responsable | Tecnico que aplica el cambio | J. Garcia (t42) |
| Sistema afectado | Nombre del servidor/entorno | srv-inference-01 |
| Tipo de cambio | Normal / Urgente / Estandar | Urgente (CVE critica) |
| Descripcion | Que se ha actualizado y por que | PyTorch 2.1.2 → 2.3.1; CVE-2024-31583 |
| Impacto previsto | Tiempo de inactividad esperado | 15 min de reinicio del servicio |
| Plan de rollback | Como revertir si falla | pip install torch==2.1.2 + reinicio |
| Estado | Exito / Fallido / Revertido | Exito |
| Pruebas realizadas | Verificaciones post-cambio | Smoke test OK, benchmark dentro de margen |
| Observaciones | Cualquier anomalia observada | Ninguna |

---

## Documentacion de cambios — registro practico

### Plantilla de change log en formato Markdown

```markdown
# Change Log — srv-inference-01

## CHG-2024-0312 | 2024-06-15 02:00 UTC | J. Garcia

**Tipo:** Urgente (parche de seguridad)
**Componente:** PyTorch 2.1.2 → 2.3.1
**Motivo:** CVE-2024-31583 (deserializacion insegura, CVSS 9.8)

### Acciones realizadas
1. Backup de requirements.txt en /backups/20240615_requirements_before.txt
2. Prueba en entorno staging durante 4 h — resultado: OK
3. Aplicacion en produccion: pip install torch==2.3.1
4. Reinicio del servicio Triton: systemctl restart triton-server

### Verificacion
- [x] nvidia-smi OK
- [x] torch.cuda.is_available() = True
- [x] Smoke test de inferencia OK
- [x] Latencia p99 dentro del umbral (delta: +1.8 %)

### Resultado: EXITO
```

> **Buena practica:** almacenar los change logs en un repositorio Git dedicado a la configuracion del sistema (GitOps / IaC), de modo que cada cambio quede como un commit con autor y fecha.

---

## Fin de ciclo de vida — planificacion de migracion

### Cuando un componente llega a EOL

El fin de ciclo de vida (EOL) no es un evento repentino: debe planificarse con antelacion suficiente para evitar ventanas de exposicion sin parches de seguridad.

**Proceso recomendado:**

1. **Deteccion temprana** (12 meses antes del EOL): incluir en el inventario la fecha de EOL de cada componente critico.
2. **Evaluacion de impacto** (6-9 meses antes): identificar dependencias que deben migrar junto con el componente.
3. **Proyecto de migracion** (3-6 meses antes): planificar, presupuestar y probar la alternativa.
4. **Migracion y validacion** (1-2 meses antes): ejecutar la migracion en todos los entornos.
5. **Cierre** (antes del EOL): confirmar que ningun sistema en produccion usa la version retirada.

### Borrado seguro de datos — normativa NIST SP 800-88

Antes de retirar o reutilizar cualquier medio de almacenamiento que haya contenido datos sensibles, es obligatorio aplicar un procedimiento de borrado seguro que garantice la irrecuperabilidad de la informacion.

La norma de referencia es **NIST SP 800-88 Rev. 1** (Guidelines for Media Sanitization), que define tres niveles: **Clear** (sobrescritura), **Purge** (tecnicas mas robustas) y **Destroy** (destruccion fisica).

---

## Fin de ciclo de vida — borrado seguro

### Herramientas de borrado seguro en Linux

```bash
# --- SHRED: borrado seguro de un fichero o dispositivo ---

# Sobreescribir un fichero con 3 pasadas aleatorias y eliminarlo
shred -uzv -n 3 /datos/modelo_confidencial.pt

# Sobreescribir un disco completo (ADVERTENCIA: irreversible)
sudo shred -vz -n 3 /dev/sdb

# --- NWIPE: borrado de disco con interfaz interactiva ---
sudo apt install nwipe
sudo nwipe /dev/sdb
# Metodos disponibles: DoD 5220.22-M, Gutmann, PRNG, Random

# --- HDPARM: ATA Secure Erase (mas eficaz en SSD) ---
# Paso 1: verificar que el disco no esta congelado
sudo hdparm -I /dev/sda | grep -i frozen

# Paso 2: establecer contrasena temporal
sudo hdparm --security-set-pass TEMPORAL /dev/sda

# Paso 3: ejecutar Secure Erase
sudo hdparm --security-erase TEMPORAL /dev/sda

# --- NVME: borrado seguro de discos NVMe ---
sudo nvme format /dev/nvme0n1 --ses=1
# ses=1: User Data Erase (sobrescritura)
# ses=2: Cryptographic Erase (si el disco soporta encriptacion)
```

> **Para SSDs NVMe:** el metodo recomendado por NIST SP 800-88 es **Cryptographic Erase** (`--ses=2`) cuando el disco soporta encriptacion de hardware, ya que la sobrescritura por pasadas no es eficaz en memorias flash.

---

## Tratamiento de RAEE

### Marco normativo

Los **Residuos de Aparatos Electricos y Electronicos (RAEE)** estan regulados en la Union Europea por la **Directiva 2012/19/UE** (refundicion), transpuesta en Espana mediante el **Real Decreto 110/2015**, de 20 de febrero, sobre residuos de aparatos electricos y electronicos.

**Obligaciones del poseedor de RAEE profesional:**

- No mezclar los RAEE con otros tipos de residuos
- Entregar los RAEE unicamente a gestores autorizados inscritos en el Registro de Produccion y Gestion de Residuos (RPGR)
- Conservar el justificante de entrega durante un minimo de **5 anos**
- No exportar RAEE a paises terceros como residuo disfrazado de segunda mano

### Proceso de entrega de hardware retirado

1. **Identificacion:** etiquetar el equipo como RAEE y registrarlo en el inventario como "pendiente de baja"
2. **Borrado seguro:** aplicar el procedimiento de borrado (ver diapositiva anterior) y documentarlo
3. **Desinstalacion de licencias:** retirar toda licencia propietaria antes de la entrega (ver siguiente diapositiva)
4. **Embalaje:** proteger el equipo para evitar rotura durante el transporte
5. **Entrega al gestor autorizado:** solicitar albaran de entrega como justificante
6. **Baja en inventario:** actualizar el inventario del sistema de gestion de activos (CMDB)

---

## Desinstalacion de licencias

### Por que es obligatorio antes de retirar el hardware

Las licencias de software propietario suelen estar vinculadas a un numero de serie de hardware o a un servidor de licencias. Si el hardware se retira sin desactivar la licencia:

- La licencia queda "consumida" sin uso productivo
- En licencias flotantes (concurrent), se reduce el numero de puestos disponibles
- Puede incurrirse en incumplimiento del acuerdo de licencia (EULA)

### Procedimiento para productos comunes en entornos de IA

| Producto | Metodo de desactivacion | Herramienta |
|---|---|---|
| MATLAB (MathWorks) | Desde la propia aplicacion: Ayuda > Licencias > Desactivar | mlm_util / portal web |
| ArcGIS Pro (Esri) | Portal My Esri > Mis licencias > Revocar | ArcGIS License Manager |
| Licencias flotantes (FlexLM) | Detener el servidor lmgrd y retirar el archivo de licencia | `lmdown -q` |
| NVIDIA AI Enterprise | Portal NVIDIA Licensing > Revocar licencia del servidor | Portal web NGC |
| Intel oneAPI (licencia comercial) | Portal Intel Software > Mis productos | Herramienta de desactivacion Intel |

```bash
# Ejemplo: detener y limpiar un servidor de licencias FlexLM
sudo systemctl stop flexlm
sudo rm /etc/flexlm/license.dat
sudo systemctl disable flexlm

# Verificar que no quedan procesos lmgrd activos
ps aux | grep lmgrd
```

---

## Sostenibilidad — eficiencia energetica y prolongacion de vida util

### Reduccion de carga termica y energetica

En centros de datos con GPUs de alto rendimiento, la gestion termica y energetica es un factor critico tanto economico como medioambiental.

**Tecnicas de ajuste en GPU NVIDIA:**

```bash
# Ajuste del TDP (Total Design Power) de la GPU
# Reducir la potencia maxima al 80 % del TDP nominal
sudo nvidia-smi -pl 320   # GPU con TDP nominal de 400 W → limitar a 320 W

# Verificar el limite de potencia actual
nvidia-smi --query-gpu=power.limit,power.draw --format=csv

# Activar modo de gestion de energia persistente
sudo nvidia-smi -pm 1

# DVFS (Dynamic Voltage and Frequency Scaling): ajustar frecuencias
# Modo auto (el controlador ajusta segun carga)
sudo nvidia-smi --auto-boost-default=0
sudo nvidia-smi -ac 877,1410   # mem_clock,graphics_clock en MHz (A100)
```

### Metricas de eficiencia energetica del centro de datos

| Metrica | Formula | Valor ideal | Descripcion |
|---|---|---|---|
| PUE (Power Usage Effectiveness) | E_total / E_IT | < 1.2 (excelente) | Eficiencia del CPD completo |
| GPU Power Efficiency | Tokens/s por vatio | Maximizar | Rendimiento de inferencia por unidad de energia |
| Temperatura de sala | — | 18-27 C (ASHRAE A1) | Rango recomendado para equipos de IT |

> **Prolongacion de vida util:** mantener las GPU a temperatura maxima por debajo de 75 C de forma sostenida puede extender su vida util varios anos, reduciendo la generacion de RAEE y el coste de reposicion.

---

## Actividad practica

### Auditoria de paquetes Python y plan de actualizacion

**Objetivo:** identificar paquetes desactualizados y CVEs abiertas en un entorno de inferencia, y generar un plan de actualizacion priorizado.

**Pasos:**

1. Activar el entorno virtual del servidor de inferencia:
   ```bash
   source /opt/venvs/inference/bin/activate
   ```

2. Generar el informe de paquetes desactualizados:
   ```bash
   pip list --outdated --format=columns > ~/auditoria_$(date +%Y%m%d).txt
   pip freeze > ~/requirements_actual.txt
   ```

3. Instalar y ejecutar `pip-audit` para detectar CVEs:
   ```bash
   pip install pip-audit
   pip-audit --format=columns
   pip-audit --format=json > ~/cves_$(date +%Y%m%d).json
   ```

4. Clasificar los hallazgos segun el tipo de actualizacion (parche de seguridad, bugfix, minor, major) y la urgencia (critica, alta, media, baja).

5. Redactar un **plan de actualizacion** con: componente, version actual, version objetivo, tipo de cambio, urgencia, riesgo estimado, ventana de mantenimiento propuesta y responsable.

**Entregable:** documento con el informe de `pip-audit` y el plan de actualizacion cumplimentado.

---

## Puntos clave

- **Detectar antes de actuar:** usar `apt list --upgradable`, `pip list --outdated` y `nvidia-smi` como punto de partida de cualquier ciclo de mantenimiento.
- **Clasificar la urgencia:** no todas las actualizaciones son iguales. Un parche de seguridad con CVE critica no puede esperar; una actualizacion major requiere un proyecto de migracion formal.
- **Backup y staging siempre:** nunca aplicar una actualizacion directamente en produccion sin haber probado en un entorno equivalente y sin disponer de un plan de rollback documentado.
- **Verificar la estabilidad:** el trabajo no termina al aplicar el parche. El periodo de monitorizacion post-actualizacion de 48-72 h es parte del procedimiento.
- **Documentar cada cambio:** sin Change Record no hay trazabilidad. El modelo ITIL de gestion del cambio es el estandar en entornos profesionales.
- **El fin de vida es predecible:** planificar la migracion con 12 meses de antelacion evita urgencias, exposicion a vulnerabilidades y costes innecesarios.
- **RAEE y borrado seguro son obligaciones legales:** la Directiva 2012/19/UE y el RD 110/2015 no son opcionales. El justificante de entrega al gestor autorizado debe conservarse 5 anos.

---

## Criterios de evaluacion

| Criterio | Descripcion | Indicadores de logro |
|---|---|---|
| CE4.1 | Identifica y aplica actualizaciones de sistema y paquetes | Usa `apt`, `pip list --outdated` y clasifica correctamente el tipo de actualizacion |
| CE4.2 | Aplica el procedimiento de actualizacion con backup y rollback | Genera backup, prueba en staging, documenta el rollback disponible |
| CE4.3 | Verifica la estabilidad del sistema tras la actualizacion | Ejecuta smoke tests, mide latencia y VRAM, monitoriza 48 h |
| CE4.4 | Documenta los cambios en formato ITIL | Cumplimenta todos los campos del Change Record con datos reales |
| CE4.5 | Gestiona el fin de ciclo de vida de forma segura y sostenible | Aplica borrado seguro (NIST SP 800-88), desactiva licencias, entrega RAEE a gestor autorizado |
| CE4.6 | Aplica medidas de eficiencia energetica | Configura limites de TDP, conoce el PUE y su interpretacion |

---

<!-- _class: lead -->

[← Volver a MP01](../)


---

<!-- nav-slide -->

## Navegación

[← UD3 · Implementación de componentes…](../UD3_Implementacion-explotacion/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD5 · Resolución de incidencias en… →](../UD5_Resolucion-incidencias/)
