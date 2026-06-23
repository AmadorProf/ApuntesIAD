---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD6 · Seguridad, privacidad y trazabilidad | MP04 · Infraestructura para la ejecución de LLMs'
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

# UD6 · Seguridad, privacidad y trazabilidad

MP04 · Infraestructura para la ejecución de LLMs

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Identificar los riesgos de seguridad propios de una infraestructura de inferencia LLM
- Aplicar controles de autenticación, autorización y gestión de secretos
- Supervisar registros, trazas y metadatos de peticiones garantizando la privacidad
- Configurar límites de uso (cuotas, rate limiting, tamaños de entrada/salida)
- Validar los controles de seguridad con pruebas de acceso no autorizado y escenarios límite
- Elaborar la documentación de seguridad exigible: política de accesos, plan de respuesta a incidentes y registro de vulnerabilidades

---

## Mapa de riesgos en infraestructura LLM

Los riesgos se agrupan en cinco categorías según su vector de ataque.

| Categoria | Riesgo | Impacto potencial |
|---|---|---|
| **Exposicion de endpoint** | API accesible sin autenticacion desde internet | Uso no autorizado, coste desbordado |
| **Acceso indebido al modelo** | Descarga o copia del modelo sin autorizacion | Robo de propiedad intelectual |
| **Fuga de contexto** | Historial o prompt del usuario expuesto a terceros | Violacion RGPD, fuga de datos sensibles |
| **Manipulacion de configuracion** | Cambio de parametros del servidor (max_tokens, modelo activo) | Degradacion del servicio, backdoor |
| **Consumo no controlado** | Peticiones masivas sin limite (DoS economico) | Saturacion de GPU, coste elevado |

> La superfice de ataque de un servidor de inferencia es diferente a la de una aplicacion web convencional: el modelo en si es un activo critico que requiere proteccion especifica.

---

## Riesgos — exposicion de endpoint y acceso al modelo

### Exposicion no autorizada de endpoint

Un endpoint LLM sin proteccion permite a cualquier persona con acceso a la red:
- Inferir con el modelo a costa del operador
- Extraer informacion del sistema prompt (prompt injection)
- Usar el servicio como recurso para generar contenido dañino

### Acceso indebido al modelo

Los pesos de un modelo son el activo mas valioso de la infraestructura.

```bash
# MAL: directorio de modelos accesible al usuario del servicio web
ls -la /models/
drwxr-xr-x  llm-server:www-data  llama-3.1-8b/

# BIEN: separacion de propietario y usuario de servicio
# El proceso de inferencia tiene permisos de lectura, no el proceso web
chown -R llm-model:llm-model /models/
chmod 750 /models/
# El usuario llm-server pertenece al grupo llm-model (solo lectura)
usermod -aG llm-model llm-server
```

---

## Riesgos — fuga de contexto y manipulacion de configuracion

### Fuga de informacion en contexto o historial

El contexto de conversacion puede contener datos personales, secretos de empresa o informacion clasificada que no debe persistir mas alla de la sesion.

| Tipo de dato | Ejemplo | Riesgo si persiste |
|---|---|---|
| Datos personales | Nombre, DNI, correo del usuario | Violacion RGPD art. 5 |
| Secretos de negocio | Fragmentos de codigo propietario | Fuga de IP |
| Credenciales | Tokens, passwords en el prompt | Compromiso de cuenta |
| Historial de conversacion | Logs con prompts completos | Perfil del usuario |

### Manipulacion de configuracion

```bash
# Proteger el archivo de configuracion del servidor
chmod 640 /opt/llm/config.yaml
chown llm-admin:llm-server /opt/llm/config.yaml
# Monitorizar cambios con auditd
auditctl -w /opt/llm/config.yaml -p wa -k llm_config_change
```

---

## Autenticacion y autorizacion — principios basicos

### Minimo privilegio

Cada componente del sistema solo debe tener acceso a los recursos que necesita para funcionar.

```
Usuario final ──> API Gateway (valida token) ──> Servidor LLM (sin acceso a red externa)
                        |                               |
                  Verifica rol                   Solo /v1/chat/completions
                  y cuota                        Solo lectura de /models/
```

### Separacion de funciones

| Rol | Acciones permitidas |
|---|---|
| `llm-admin` | Desplegar modelos, modificar configuracion, ver todos los logs |
| `llm-operator` | Reiniciar servicio, ver metricas, ver logs de error |
| `llm-user` | Llamar a `/v1/chat/completions` con su propio token |
| `llm-auditor` | Leer logs y trazas, sin capacidad de modificar nada |

> El mismo tecnico que despliega el modelo no debe ser el que audita su uso. La separacion de funciones es un control compensatorio clave.

---

## Autenticacion — API Keys y JWT

### API Keys estaticas (entornos simples)

```python
# middleware de autenticacion para FastAPI
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hmac, hashlib, os

CLAVES_VALIDAS = {
    "llm-user-001": "rol:usuario",
    "llm-admin-001": "rol:admin",
}

security = HTTPBearer()

async def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in CLAVES_VALIDAS:
        raise HTTPException(status_code=401, detail="Token invalido o caducado")
    return CLAVES_VALIDAS[token]
```

### JWT con caducidad (entornos con multiples usuarios)

```bash
# Generar clave de firma con openssl
openssl rand -hex 32 > /opt/llm/jwt_secret.key
chmod 600 /opt/llm/jwt_secret.key
chown llm-admin:llm-admin /opt/llm/jwt_secret.key
```

---

## Gestion de secretos — HashiCorp Vault

Los secretos (claves API, contraseñas de base de datos, tokens) nunca deben almacenarse en texto plano en archivos de configuracion o variables de entorno del proceso.

```bash
# Instalar y arrancar Vault en modo desarrollo (solo para pruebas)
vault server -dev &
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# Crear secreto para el servidor LLM
vault kv put secret/llm-server \
  jwt_secret="$(openssl rand -hex 32)" \
  db_password="s3cr3t_db_pass" \
  huggingface_token="hf_xxxxxxxxxxxx"

# Leer el secreto desde la aplicacion
vault kv get -field=jwt_secret secret/llm-server
```

```python
# Leer secretos en Python usando hvac
import hvac

client = hvac.Client(url='http://vault:8200', token=os.environ['VAULT_TOKEN'])
secretos = client.secrets.kv.v2.read_secret_version(path='llm-server')
JWT_SECRET = secretos['data']['data']['jwt_secret']
```

---

## Restricciones de red — firewall, VPN y VLAN

### Arquitectura de red segura

```
Internet
    |
[Firewall perimetral]  ← Solo permite HTTPS:443 desde IPs autorizadas
    |
[DMZ / Reverse Proxy]  ← Nginx/Caddy con TLS, rate limiting, autenticacion
    |
[VLAN interna LLM]     ← Solo trafico interno; sin acceso directo desde internet
    |
[Servidor GPU LLM]     ← Puerto 8000 solo accesible desde el proxy
    |
[Almacenamiento NFS]   ← /models/ montado solo en lectura
```

### Reglas de firewall con nftables

```bash
# Permitir solo trafico desde el proxy al servidor GPU
nft add rule inet filter input \
  ip saddr 10.10.1.5 tcp dport 8000 accept

# Denegar todo lo demas al puerto 8000
nft add rule inet filter input \
  tcp dport 8000 drop
```

---

## Supervision de registros y trazas de peticiones

### Que registrar en cada peticion

```python
import logging, time, uuid
from fastapi import Request

logger = logging.getLogger("llm.audit")

@app.middleware("http")
async def registrar_peticion(request: Request, call_next):
    id_peticion = str(uuid.uuid4())
    inicio = time.time()

    # Extraer metadatos sin loguear el contenido del prompt
    metadatos = {
        "id": id_peticion,
        "timestamp": inicio,
        "usuario": request.headers.get("X-User-ID", "anonimo"),
        "ip_origen": request.client.host,
        "endpoint": str(request.url.path),
        "metodo": request.method,
    }

    respuesta = await call_next(request)
    metadatos["duracion_ms"] = int((time.time() - inicio) * 1000)
    metadatos["status_code"] = respuesta.status_code

    logger.info(metadatos)  # Solo metadatos, nunca el contenido del prompt
    return respuesta
```

> Registrar el contenido del prompt en logs persistentes puede constituir un tratamiento de datos personales sujeto al RGPD. Loguear solo metadatos, nunca el cuerpo de la peticion.

---

## Minimizacion y eliminacion de datos

### Principio de minimizacion (RGPD art. 5.1.c)

Solo se deben conservar los datos estrictamente necesarios para el fin declarado.

| Dato | Retencion maxima recomendada | Justificacion |
|---|---|---|
| Metadatos de peticion (id, timestamp, ip) | 90 dias | Auditoria y deteccion de anomalias |
| Tokens de usuario (hash) | Duracion del servicio | Control de acceso |
| Contenido del prompt/respuesta | No registrar | Privacidad del usuario |
| Historial de conversacion | Session + 24h (con consentimiento) | Continuidad del servicio |
| Logs de error (sin datos de usuario) | 1 año | Mantenimiento del sistema |

### Rotacion y eliminacion automatica de logs

```bash
# /etc/logrotate.d/llm-audit
/var/log/llm/audit.log {
    daily
    rotate 90
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        systemctl reload llm-server
    endscript
}
```

---

## Trazabilidad — versionado de modelos y configuraciones

La trazabilidad permite saber en todo momento que modelo y que configuracion se uso para generar una respuesta concreta.

### Versionado con Git para configuraciones

```bash
# Repositorio de configuracion del servidor LLM
git init /opt/llm/config-repo
cd /opt/llm/config-repo

# Cada cambio de configuracion es un commit firmado
git config user.signingkey GPGKEYID
git commit -S -m "cambio: aumentar max_model_len a 16384 para produccion"

# Ver historial de cambios con autor y fecha
git log --oneline --show-signature
```

### Registro de version activa en cada peticion

```python
import subprocess

def obtener_version_modelo() -> str:
    """Retorna el hash del commit de configuracion activo."""
    try:
        return subprocess.check_output(
            ["git", "-C", "/opt/llm/config-repo", "rev-parse", "--short", "HEAD"],
            text=True
        ).strip()
    except Exception:
        return "desconocido"

# Incluir en cada respuesta como cabecera HTTP
response.headers["X-Model-Version"] = "llama-3.1-8b-instruct-v1.2"
response.headers["X-Config-Commit"] = obtener_version_modelo()
```

---

## Trazabilidad — registro de accesos y alertas

### Alertas ante cambios no autorizados con auditd

```bash
# Configurar auditd para vigilar archivos criticos
cat >> /etc/audit/rules.d/llm.rules << 'EOF'
# Cambios en modelos
-w /models/ -p wxa -k llm_model_change
# Cambios en configuracion
-w /opt/llm/config.yaml -p wa -k llm_config_change
# Cambios en el servicio systemd
-w /etc/systemd/system/llm-server.service -p wa -k llm_service_change
# Accesos fallidos a la API
-a always,exit -F arch=b64 -S connect -F exit=-ECONNREFUSED -k llm_denied
EOF

augenrules --load
# Ver alertas
ausearch -k llm_config_change --start today
```

### Alerta por cambio inesperado de version de modelo

```bash
# Script de monitoreo: ejecutar cada 5 minutos via cron
MODELO_ESPERADO="llama-3.1-8b-instruct"
MODELO_ACTIVO=$(curl -s http://localhost:8000/v1/models | jq -r '.data[0].id')
if [ "$MODELO_ACTIVO" != "$MODELO_ESPERADO" ]; then
    echo "ALERTA: modelo activo '$MODELO_ACTIVO' no coincide con el esperado" \
    | mail -s "[LLM] Cambio de modelo detectado" admin@empresa.com
fi
```

---

## Limites de uso — cuotas y rate limiting

### Rate limiting con nginx (reverse proxy)

```nginx
# /etc/nginx/conf.d/llm-ratelimit.conf
limit_req_zone $http_x_user_id zone=por_usuario:10m rate=10r/m;
limit_req_zone $binary_remote_addr zone=por_ip:10m rate=30r/m;

server {
    listen 443 ssl;
    server_name llm.empresa.local;

    location /v1/chat/completions {
        # Maximo 10 peticiones por minuto por usuario
        limit_req zone=por_usuario burst=5 nodelay;
        # Maximo 30 peticiones por minuto por IP
        limit_req zone=por_ip burst=10 nodelay;
        # Respuesta al superar el limite
        limit_req_status 429;

        proxy_pass http://localhost:8000;
        proxy_read_timeout 120s;
    }
}
```

---

## Limites de uso — tamaño de entrada/salida y cuotas

### Restriccion de tamaño de entrada y salida

```python
from fastapi import HTTPException

MAX_TOKENS_ENTRADA = 4096   # Contexto maximo por peticion
MAX_TOKENS_SALIDA  = 2048   # Respuesta maxima
MAX_PETICIONES_DIA = 200    # Cuota diaria por usuario

async def validar_peticion(request: dict, usuario_id: str) -> None:
    # Verificar longitud del prompt
    texto_prompt = " ".join(m["content"] for m in request.get("messages", []))
    tokens_estimados = len(texto_prompt.split()) * 1.3  # Estimacion rapida

    if tokens_estimados > MAX_TOKENS_ENTRADA:
        raise HTTPException(status_code=400,
            detail=f"Prompt demasiado largo. Maximo {MAX_TOKENS_ENTRADA} tokens.")

    # Forzar max_tokens en la peticion
    request["max_tokens"] = min(
        request.get("max_tokens", MAX_TOKENS_SALIDA),
        MAX_TOKENS_SALIDA
    )

    # Verificar cuota diaria (usando Redis como contador)
    uso_hoy = await redis.incr(f"cuota:{usuario_id}:{hoy()}")
    await redis.expire(f"cuota:{usuario_id}:{hoy()}", 86400)
    if uso_hoy > MAX_PETICIONES_DIA:
        raise HTTPException(status_code=429,
            detail="Cuota diaria superada. Disponible de nuevo manana.")
```

---

## Parada y degradacion controlada ante saturacion

### Patron de parada controlada (graceful shutdown)

```python
import signal, asyncio

cola_activa = True

def señal_parada(signum, frame):
    global cola_activa
    cola_activa = False
    print("Señal de parada recibida. Completando peticiones en curso...")

signal.signal(signal.SIGTERM, señal_parada)
signal.signal(signal.SIGINT,  señal_parada)

@app.post("/v1/chat/completions")
async def completions(request: dict):
    if not cola_activa:
        raise HTTPException(status_code=503,
            detail="Servidor en proceso de parada. Use otro nodo.")
    # ... procesar peticion normalmente
```

### Degradacion por saturacion de VRAM

```bash
# Monitoreo de VRAM con accion automatica
VRAM_USADA=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
VRAM_TOTAL=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits)
PCT=$(( VRAM_USADA * 100 / VRAM_TOTAL ))

if [ $PCT -gt 95 ]; then
    # Reducir max_tokens para aliviar presion de VRAM
    curl -s -X PATCH http://localhost:8001/admin/config \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -d '{"max_tokens": 512, "max_num_seqs": 4}'
    logger "LLM DEGRADADO: VRAM al ${PCT}% — max_tokens reducido a 512"
fi
```

---

## Validacion de controles — pruebas de seguridad

### Prueba 1: Acceso sin autenticacion

```bash
# Debe retornar 401 o 403
curl -s -o /dev/null -w "%{http_code}" \
  http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"llama-3.1-8b","messages":[{"role":"user","content":"test"}]}'
# Resultado esperado: 401
```

### Prueba 2: Acceso con token de otro usuario

```bash
TOKEN_USUARIO_A="llm-user-001"
# Intentar acceder a los logs de administracion con token de usuario normal
curl -s -o /dev/null -w "%{http_code}" \
  http://localhost:8080/admin/logs \
  -H "Authorization: Bearer $TOKEN_USUARIO_A"
# Resultado esperado: 403 Forbidden
```

### Prueba 3: Superacion de cuota

```bash
# Enviar 15 peticiones rapidas con el mismo usuario (cuota = 10/min)
for i in $(seq 1 15); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer llm-user-001" \
    -H "Content-Type: application/json" \
    http://localhost:8080/v1/chat/completions \
    -d '{"model":"llama-3.1-8b","messages":[{"role":"user","content":"test"}]}')
  echo "Peticion $i: HTTP $STATUS"
done
# Peticiones 11-15 deben retornar 429
```

---

## Documentacion de seguridad — politica de accesos

```markdown
## Politica de acceso al servicio LLM — v1.0 · 2026-06-23

### Roles y permisos

| Rol | Quien | Acciones |
|---|---|---|
| llm-admin | Equipo de infraestructura (max 2 personas) | Despliegue, config, todos los logs |
| llm-operator | Turno de guardia (max 4 personas) | Restart, metricas, logs de error |
| llm-user | Usuarios finales autorizados | Solo /v1/chat/completions |
| llm-auditor | Responsable de cumplimiento | Solo lectura de logs de auditoria |

### Proceso de alta y baja

1. Alta: solicitud firmada por responsable de area + aprobacion de llm-admin
2. Credenciales: generadas por Vault; nunca compartidas por correo o chat
3. Baja: revocacion en Vault en el mismo dia de la baja del empleado
4. Revision trimestral de usuarios activos (recertificacion de accesos)

### Retencion de logs

- Metadatos de peticion: 90 dias
- Logs de error del sistema: 1 año
- Logs de auditoria de administracion: 3 años
```

---

## Documentacion de seguridad — plan de respuesta y registro de vulnerabilidades

### Plan de respuesta a incidentes (esquema)

```markdown
## Plan de respuesta a incidentes LLM — nivel 1 (contencion)

### Activacion
Cualquier miembro del equipo puede activar este plan ante:
- Acceso no autorizado detectado en logs
- Modelo activo diferente al esperado
- Consumo de VRAM o peticiones anormalmente alto

### Pasos inmediatos (primeros 15 minutos)
1. Aislar el servidor: bloquear trafico externo en el firewall
2. Preservar evidencias: snapshot de logs antes de cualquier reinicio
3. Notificar: responsable tecnico + responsable de datos + DPO (si hay datos personales)
4. Documentar: hora de deteccion, indicadores observados, acciones tomadas

### Restauracion
1. Verificar integridad del modelo (hash SHA256 vs. valor de referencia)
2. Revisar historial de cambios en config-repo (git log)
3. Restaurar desde backup si hay evidencia de manipulacion
4. Reactivar trafico de forma gradual con monitoreo intensificado
```

### Registro de vulnerabilidades

| ID | Fecha | Descripcion | Severidad | Estado |
|---|---|---|---|---|
| VUL-001 | 2026-06-01 | Puerto 8000 accesible sin firewall en entorno de pruebas | Alta | Cerrada |
| VUL-002 | 2026-06-10 | JWT sin caducidad definida | Media | En revision |

---

## Actividad practica — Auditoria de seguridad

### Escenario

Se ha desplegado un servidor vLLM en una red corporativa con los siguientes problemas identificados por el equipo de auditoria:

1. El endpoint `/v1/chat/completions` es accesible desde cualquier IP de la red sin autenticacion
2. Los logs del sistema incluyen el contenido completo de los prompts de los usuarios
3. No existe cuota de uso por usuario
4. El directorio `/models/` tiene permisos `755` y es propiedad de `root`

### Tareas

1. Para cada problema, escribe el comando o configuracion que lo corrige
2. Diseña la tabla de roles con minimo privilegio para este sistema
3. Escribe el middleware Python que registra solo metadatos (sin contenido del prompt)
4. Define las tres pruebas de validacion que ejecutarias para verificar que los controles funcionan
5. Redacta las dos primeras entradas del registro de vulnerabilidades con los problemas detectados

---

## Puntos clave — UD6

- El **minimo privilegio** no es una recomendacion: es el control mas eficaz para limitar el impacto de cualquier compromiso. Cada rol, cada proceso y cada cuenta debe tener exactamente los permisos que necesita, ni uno mas.

- **Loguear metadatos, no contenido**: registrar los prompts de los usuarios en logs persistentes puede ser un tratamiento de datos personales ilicito. La trazabilidad se logra con IDs de peticion, timestamps y codigos de estado, no con el cuerpo de las peticiones.

- El **versionado de configuraciones con Git** permite responder a la pregunta "que cambio y quien lo cambio" en cualquier incidente. Sin esta trazabilidad, la respuesta a incidentes es ciega.

- El **rate limiting** tiene dos funciones: proteger la infraestructura (DoS) y garantizar la equidad entre usuarios. Ambas son igual de importantes en un entorno compartido.

- La **documentacion de seguridad** (politica de accesos, plan de incidentes, registro de vulnerabilidades) no es un tramite burocratico: es la evidencia de que los controles existen y se revisan.

---

## Criterios de evaluacion — UD6

| Criterio | Indicadores de logro |
|---|---|
| **Gestiona accesos con minimo privilegio** | Define roles diferenciados; configura autenticacion con token; aplica permisos de sistema de archivos correctos |
| **Supervisa registros y trazabilidad** | Configura logging de metadatos sin contenido personal; implementa versionado de configuracion; configura alertas ante cambios |
| **Aplica limites de uso** | Configura rate limiting y cuotas por usuario; implementa limites de tamaño de entrada/salida; define comportamiento ante saturacion |
| **Valida controles con pruebas** | Ejecuta prueba de acceso sin token (401), acceso con rol insuficiente (403) y superacion de cuota (429) |
| **Elabora documentacion de seguridad** | Entrega politica de accesos con roles, plan de respuesta a incidentes y registro de vulnerabilidades |

> **Referencia:** resultado de aprendizaje RA6 — "Gestiona la seguridad, privacidad y trazabilidad de la infraestructura de inferencia aplicando controles de acceso, supervision de registros y limites de uso."

---

[← Volver a MP04](../index.md)


---

<!-- nav-slide -->

## Navegación

[← UD5 · Validación de la capacidad op…](../UD5_Validacion-capacidad-operativa/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD7 · Responsabilidad, sostenibilid… →](../UD7_Responsabilidad-sostenibilidad-PRL/)
