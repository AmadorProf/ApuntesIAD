# UD5 · Puesta en servicio de sistemas de IA

---

## 1. Introducción — la puesta en servicio como transición crítica

La puesta en servicio es el momento en que un sistema de inteligencia artificial deja de existir en un entorno controlado y comienza a operar bajo condiciones reales: tráfico imprevisible, datos que nunca se vieron durante el entrenamiento, usuarios con expectativas de respuesta y equipos de operaciones que no participaron en el desarrollo del modelo.

Esta transición de staging a producción real es, con frecuencia, el punto donde los proyectos de IA fracasan o donde los problemas latentes se vuelven visibles. Un modelo que pasa todas las métricas de evaluación offline puede comportarse de forma inesperada ante patrones de entrada que no estaban representados en el conjunto de validación, puede degradar el rendimiento del sistema subyacente por un uso ineficiente de recursos, o puede simplemente no estar disponible el tiempo suficiente como para cumplir los compromisos de nivel de servicio acordados.

La puesta en servicio no es un evento puntual, sino un proceso que comienza antes del primer request real y termina cuando el equipo de operaciones tiene suficiente confianza y documentación para gestionar el sistema de forma autónoma. Implica decisiones técnicas precisas —qué smoke tests ejecutar, qué porcentaje de tráfico derivar al nuevo modelo, cómo calentar los workers antes de recibir carga real— y decisiones organizativas igualmente importantes: quién tiene el on-call, qué constituye una degradación que justifica rollback, cómo se escalan los incidentes.

Esta unidad cubre ese proceso completo, desde la verificación inicial del despliegue hasta la entrega formal del sistema al equipo que lo va a operar.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el alumno será capaz de:

- Diseñar y ejecutar suites de smoke tests post-despliegue que cubran disponibilidad, correctitud, latencia y ausencia de errores en logs.
- Implementar estrategias de traffic shaping (shadow mode y canary deployment) para introducir un nuevo modelo en producción con riesgo controlado.
- Configurar estrategias de warm-up de modelos para mitigar el problema del cold start en la primera inferencia.
- Configurar alertas iniciales sobre métricas clave de disponibilidad, latencia y uso de recursos usando Prometheus y Alertmanager.
- Aplicar principios de SRE al ciclo de vida de modelos de machine learning, incluyendo error budgets y runbooks.
- Elaborar documentación de handoff suficiente para que un equipo de operaciones pueda gestionar el sistema sin depender del equipo de desarrollo.

---

## 3. Smoke tests post-despliegue

### 3.1 Qué son y qué deben cubrir

Un smoke test, en el contexto del despliegue de sistemas de IA, es una verificación rápida y automatizada que se ejecuta inmediatamente después de que el modelo ha sido desplegado, antes de que reciba tráfico real de usuarios. El nombre proviene de la industria electrónica: se enciende el circuito y se comprueba que no sale humo. La idea es detectar fallos evidentes antes de que causen daño.

Un smoke test bien diseñado debe cubrir al menos cuatro dimensiones:

**Disponibilidad del endpoint.** El servicio debe responder en la URL esperada con el código HTTP correcto. Una respuesta 200 OK ante una petición válida confirma que el proceso está en pie, el puerto está expuesto y el routing de red funciona. No confirma que el modelo produce resultados útiles, pero es el primer filtro necesario.

**Respuesta correcta a un input de referencia.** Se envía un input conocido —cuya respuesta esperada se determinó durante la validación offline— y se comprueba que el output del modelo en producción coincide, o se mantiene dentro de un margen de tolerancia aceptable. Para modelos de clasificación esto es sencillo: se espera una clase concreta. Para modelos generativos, puede comprobarse que el output contiene ciertas palabras clave o que tiene una longitud razonable.

**Latencia dentro de SLO.** El smoke test mide el tiempo de respuesta de esa petición de referencia y lo compara contra el Service Level Objective de latencia acordado. Si el modelo tarda tres veces más de lo comprometido en una petición simple, el despliegue no está listo para recibir tráfico.

**Ausencia de errores en logs.** Inmediatamente después del despliegue, se inspeccionan los logs del servicio en busca de excepciones no capturadas, avisos de carga de pesos, errores de configuración o cualquier señal de que algo no se inicializó correctamente. Muchos fallos silenciosos se manifiestan en los logs antes de que afecten a las respuestas.

### 3.2 Automatización en el pipeline de despliegue

Los smoke tests deben integrarse como un paso explícito en el pipeline de CI/CD, ejecutándose después del despliegue en el entorno de staging o canary y antes de cualquier incremento de tráfico. Si fallan, el pipeline se detiene y el sistema permanece en el estado anterior.

La automatización garantiza que ningún despliegue pueda avanzar sin pasar esta validación mínima, independientemente de la presión de entrega o de si el equipo está disponible para comprobarlo manualmente.

### 3.3 Go/no-go decision automática

El pipeline evalúa los resultados de los smoke tests y toma una decisión binaria: continuar con el despliegue (go) o revertir al estado anterior (no-go). Esta decisión debe ser automática y no requerir intervención humana en el caso normal. La intervención humana se reserva para casos ambiguos o para desbloquear manualmente el pipeline cuando la situación lo justifica.

### 3.4 Ejemplo de suite de smoke tests con pytest y requests

```python
import requests
import time
import pytest

BASE_URL = "http://model-service.production.svc/v1"
SLO_LATENCY_MS = 500
REFERENCE_INPUT = {"text": "El cielo es"}
EXPECTED_KEYWORD = "azul"


def test_endpoint_disponible():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200


def test_respuesta_correcta_a_input_referencia():
    response = requests.post(
        f"{BASE_URL}/predict",
        json=REFERENCE_INPUT,
        timeout=10
    )
    assert response.status_code == 200
    body = response.json()
    assert "prediction" in body
    assert EXPECTED_KEYWORD in body["prediction"].lower()


def test_latencia_dentro_de_slo():
    inicio = time.time()
    response = requests.post(
        f"{BASE_URL}/predict",
        json=REFERENCE_INPUT,
        timeout=10
    )
    latencia_ms = (time.time() - inicio) * 1000
    assert response.status_code == 200
    assert latencia_ms < SLO_LATENCY_MS, (
        f"Latencia {latencia_ms:.0f}ms supera SLO de {SLO_LATENCY_MS}ms"
    )


def test_ausencia_de_errores_en_logs():
    response = requests.get(f"{BASE_URL}/logs/recent?level=ERROR&limit=10")
    assert response.status_code == 200
    logs = response.json().get("entries", [])
    assert len(logs) == 0, f"Se encontraron errores en logs: {logs}"
```

Este ejemplo asume que el servicio expone un endpoint `/logs/recent` para inspección de logs. En entornos reales, la comprobación de logs suele hacerse consultando el sistema de logging centralizado (Elasticsearch, Loki) desde el pipeline.

---

## 4. Traffic shaping en el lanzamiento

### 4.1 Shadow mode

El shadow mode es una estrategia en la que el nuevo modelo recibe copias del tráfico real en paralelo con el modelo en producción actual, pero sus respuestas no se devuelven a los usuarios. El usuario sigue recibiendo la respuesta del modelo antiguo. Las respuestas del modelo nuevo se registran y se comparan con las del modelo antiguo para detectar divergencias antes de exponerlas a usuarios reales.

Esta técnica permite validar el comportamiento del modelo bajo carga real sin ningún riesgo para la experiencia del usuario. Es especialmente útil cuando se desconfía de la representatividad del conjunto de validación offline, o cuando el modelo nuevo tiene un comportamiento suficientemente diferente como para que los smoke tests no sean suficientes.

Las métricas que se monitorizan en shadow mode son la tasa de divergencia de outputs (qué porcentaje de predicciones difieren del modelo antiguo), la tasa de error del modelo nuevo (excepciones, respuestas vacías, timeouts) y la latencia comparativa.

En Istio, el shadow mode se configura con un VirtualService que duplica el tráfico hacia un segundo servicio:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: model-service
spec:
  hosts:
    - model-service
  http:
    - route:
        - destination:
            host: model-service-v1
            port:
              number: 8080
          weight: 100
      mirror:
        host: model-service-v2
        port:
          number: 8080
      mirrorPercentage:
        value: 100.0
```

Con nginx, el efecto equivalente puede conseguirse con la directiva `mirror` del módulo `ngx_http_mirror_module` en la configuración del upstream, aunque con menos flexibilidad que Istio para el análisis de las respuestas del mirror.

### 4.2 Canary deployment con Kubernetes y nginx-ingress

Un canary deployment consiste en dirigir un pequeño porcentaje del tráfico real al nuevo modelo mientras el resto sigue siendo atendido por el modelo anterior. A diferencia del shadow mode, los usuarios del canary sí reciben respuestas del modelo nuevo. Esto permite validar el comportamiento con impacto real, pero limitado.

La configuración de un canary ingress con nginx-ingress en Kubernetes se hace mediante anotaciones sobre el Ingress del modelo nuevo:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: model-service-canary
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "5"
spec:
  rules:
    - host: model-service.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: model-service-v2
                port:
                  number: 8080
```

Esta configuración dirige el 5% del tráfico al modelo nuevo. El Ingress principal del modelo antiguo permanece sin cambios y atiende el 95% restante.

### 4.3 Estrategia de incremento progresivo

El incremento del porcentaje de canary debe ser progresivo y condicionado a que las métricas se mantengan dentro de los umbrales acordados. Una estrategia razonable es:

| Fase | Porcentaje | Duración minima | Condicion de avance |
|------|-----------|-----------------|---------------------|
| Inicial | 1% | 30 minutos | Sin errores, latencia p99 dentro de SLO |
| Exploracion | 5% | 2 horas | Metricas de negocio comparables al modelo anterior |
| Validacion | 20% | 4 horas | Error rate estable, sin alertas activas |
| Produccion completa | 100% | — | Todos los criterios anteriores cumplidos |

### 4.4 Criterios de avance y rollback automático

El avance de un step al siguiente se condiciona a:

- Tasa de error del canary igual o inferior a la del modelo base más un margen definido (por ejemplo, no más de 0.5 puntos porcentuales por encima).
- Latencia p99 del canary dentro del SLO de latencia.
- Ausencia de alertas críticas activas relacionadas con el modelo nuevo.

El rollback automático se activa cuando cualquiera de estas condiciones se viola durante más de N minutos consecutivos. El pipeline reduce el weight del canary a 0 y elimina el Ingress del canary. El modelo anterior retoma el 100% del tráfico sin intervención humana.

---

## 5. Warm-up de modelos en producción

### 5.1 El problema del cold start

El cold start es la penalización de latencia que sufre la primera inferencia después de que un proceso de servidor de modelo arranca. Sus causas son múltiples:

- Carga de pesos desde disco a memoria RAM o VRAM: para modelos grandes, esto puede tardar decenas de segundos.
- Inicialización de buffers de CUDA y compilación de kernels en GPU: las primeras llamadas a operaciones de GPU implican una compilación JIT de los kernels que se usarán, lo que introduce latencia adicional.
- Inicialización de caché de KV en modelos transformer: algunos frameworks reservan la caché en el primer forward pass.
- Inicialización de conexiones a servicios de backend (bases de datos vectoriales, feature stores).

El resultado es que la primera petición que llega a un worker recién arrancado puede tardar diez o veinte veces más que las peticiones subsiguientes. Si este worker arranca justo cuando el tráfico aumenta, los primeros usuarios experimentarán timeouts o latencias inaceptables.

### 5.2 Estrategias de pre-warming

**Batch de requests ficticias al arranque.** Antes de registrar el pod como disponible para recibir tráfico, el propio proceso de servidor ejecuta un conjunto de peticiones de inferencia internas con inputs sintéticos. Esto fuerza la inicialización de todos los componentes que de otro modo se inicializarían de forma lazy. Una vez completado el batch, el proceso señala que está listo.

```python
def warm_up_model(model, num_requests: int = 10):
    dummy_input = torch.zeros(1, 512, dtype=torch.long)
    with torch.no_grad():
        for _ in range(num_requests):
            _ = model(dummy_input)
    logger.info(f"Warm-up completado con {num_requests} inferencias")
```

**Readiness probe en Kubernetes que espera hasta que el modelo esté caliente.** Kubernetes no enviará tráfico a un pod hasta que su readiness probe devuelva éxito. Esta probe puede configurarse para ejecutar una petición de inferencia interna y verificar que responde dentro del SLO de latencia. Si la primera inferencia todavía está en cold start, la probe falla y el pod no recibe tráfico hasta que el warm-up haya completado.

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 5
  failureThreshold: 10
```

El endpoint `/ready` ejecuta internamente una inferencia de referencia y devuelve 200 solo cuando la latencia observada está por debajo del umbral:

```python
@app.get("/ready")
def readiness():
    if not model_warmed_up:
        raise HTTPException(status_code=503, detail="Model warming up")
    return {"status": "ready"}
```

**Pool de workers pre-inicializados.** En lugar de arrancar nuevos workers en respuesta al aumento de tráfico (escalado reactivo), se mantiene un pool de workers ya inicializados y calientes en standby, que se activan instantáneamente cuando la demanda aumenta. Esto tiene un coste en recursos cuando el tráfico es bajo, pero elimina por completo el cold start durante los picos.

### 5.3 La analogía con JVM warm-up

El cold start de modelos de ML tiene un paralelo directo en el mundo de las aplicaciones Java. La JVM compila el bytecode a código nativo de forma progresiva mediante el compilador JIT: las primeras ejecuciones de un método son lentas porque se interpretan, y solo después de suficientes ejecuciones el método se compila a código nativo optimizado. Las aplicaciones Java en producción llevan décadas gestionando este problema con técnicas análogas a las del ML: pre-warming de los métodos críticos antes de recibir tráfico real, traffic replay durante el arranque, y mantenimiento de instancias calientes durante el escalado. En ambos casos el principio es el mismo: ningún usuario real debe sufrir la penalización de la inicialización.

---

## 6. Configuración de alertas iniciales

### 6.1 Alertas de primera hora

Las primeras horas después de un despliegue son el período de mayor riesgo. El sistema está bajo observación intensiva y cualquier desviación respecto al comportamiento esperado debe ser detectada y notificada de forma inmediata. Las alertas de primera hora cubren:

**Error rate.** Si la tasa de requests que terminan en error (5xx, timeouts, excepciones capturadas) supera un umbral —por ejemplo, 1%— durante más de 5 minutos consecutivos, se dispara una alerta de severidad alta.

**Latencia p99 > SLO.** Si el percentil 99 de latencia supera el SLO comprometido, el sistema está fallando a los usuarios más lentos. Se debe alertar con severidad media, con escalada si persiste más de 15 minutos.

**Utilización de GPU > 90%.** Una GPU saturada introduce colas de inferencia que degradan la latencia de todos los usuarios. Se debe alertar antes de llegar al límite para poder escalar proactivamente.

**Disponibilidad < 99.9%.** Si la tasa de requests exitosas cae por debajo del 99.9% en una ventana de 5 minutos, el sistema no está cumpliendo su SLO de disponibilidad.

### 6.2 Prometheus y Alertmanager

Prometheus recopila métricas mediante scraping de los endpoints `/metrics` expuestos por el servicio de modelo. Las reglas de alerta se definen en YAML y Alertmanager gestiona el enrutamiento de las notificaciones.

```yaml
groups:
  - name: modelo_ia_alertas
    rules:
      - alert: ErrorRateAlto
        expr: |
          rate(http_requests_total{status=~"5.."}[5m])
          / rate(http_requests_total[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error rate superior al 1% durante 5 minutos"
          description: "Modelo {{ $labels.model_version }} tiene error rate {{ $value | humanizePercentage }}"

      - alert: LatenciaP99FueraDeSLO
        expr: |
          histogram_quantile(0.99,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Latencia p99 supera SLO de 500ms"

      - alert: GPUSaturada
        expr: nvidia_gpu_utilization_rate > 0.90
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "GPU con utilizacion > 90%"

      - alert: DisponibilidadBaja
        expr: |
          rate(http_requests_total{status="200"}[5m])
          / rate(http_requests_total[5m]) < 0.999
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disponibilidad por debajo del 99.9%"
```

Alertmanager recibe las alertas de Prometheus y las enruta a los canales de notificación apropiados:

```yaml
route:
  group_by: ['alertname', 'model_version']
  receiver: 'pagerduty-critical'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
    - match:
        severity: warning
      receiver: 'slack-warnings'

receivers:
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - routing_key: '<PAGERDUTY_KEY>'
  - name: 'slack-warnings'
    slack_configs:
      - api_url: '<SLACK_WEBHOOK>'
        channel: '#ml-ops-alerts'
```

### 6.3 PagerDuty y Opsgenie para on-call

PagerDuty y Opsgenie son las plataformas más comunes para gestionar el on-call en equipos de operaciones. Ambas se integran directamente con Alertmanager y permiten definir rotaciones de guardia, políticas de escalada y canales de notificación (SMS, llamada, app móvil).

La configuración recomendada para el período de puesta en servicio es que las alertas críticas contacten directamente al ingeniero de guardia del equipo de ML engineering, no solo al equipo de operaciones general. El equipo que construyó el modelo es quien mejor puede diagnosticar un comportamiento anómalo en las primeras horas.

### 6.4 Período de observación intensiva

Durante las primeras 24 a 48 horas después de un despliegue, el equipo mantiene un período de observación intensiva. Esto significa umbrales de alerta más conservadores que los que se usarán en operación normal, revisión manual de dashboards cada hora, y disponibilidad del equipo de desarrollo para responder a incidentes aunque no sean turno de guardia. Pasado este período, si el sistema se ha comportado de forma estable, los umbrales de alerta se relajan a los valores de operación normal y la responsabilidad de on-call pasa íntegramente al equipo de operaciones.

---

## 7. SRE para sistemas de IA

### 7.1 Aplicación de principios SRE al machine learning

Site Reliability Engineering (SRE) es la disciplina que Google formalizó para gestionar sistemas de producción a escala. Sus principios —error budgets, service level objectives, reducción del toil, postmortems sin culpa— son directamente aplicables a los sistemas de IA, aunque con adaptaciones necesarias.

**Error budgets para modelos.** Un error budget es la cantidad de indisponibilidad o degradación que el SLO permite antes de que el equipo deba detener el trabajo de nuevas funcionalidades y dedicarse exclusivamente a mejorar la fiabilidad. Si el SLO es 99.9% de disponibilidad mensual, el error budget es 0.1% de ese mes, aproximadamente 43 minutos. Cuando el error budget se agota, ningún nuevo despliegue está autorizado hasta el mes siguiente. Esta mecánica crea un incentivo directo para que los equipos cuiden la fiabilidad de sus modelos en producción.

Para sistemas de IA, el error budget puede extenderse más allá de la disponibilidad técnica: si el SLO incluye una métrica de calidad del modelo (por ejemplo, precisión >= 91%), cada período en que la precisión cae por debajo de ese umbral consume error budget, aunque el servicio esté técnicamente disponible.

**Toil reduction en operaciones de modelo.** El toil son las tareas operativas manuales, repetitivas y sin valor duradero. En el contexto de ML, el toil incluye reentrenar manualmente el modelo cuando se detecta drift, ajustar manualmente thresholds de alertas, o revisar manualmente logs para identificar patrones de error. Reducir el toil implica automatizar el reentrenamiento cuando se cumplen condiciones de drift, automatizar el ajuste de alertas mediante análisis de tendencias, y construir dashboards que resumen los patrones de error en lugar de obligar a revisar logs en bruto.

### 7.2 Diferencia entre SRE clásico y ML SRE

El SRE clásico gestiona la fiabilidad de servicios cuyo comportamiento está determinado por código. Si el servicio falla, se puede examinar el código, reproducir el bug y corregirlo. En ML SRE, el comportamiento del sistema está determinado por el modelo, y el modelo puede degradarse sin que nadie haya cambiado ningún código. Este fenómeno —el model drift— no tiene equivalente en el SRE clásico.

**Model drift.** La distribución de los datos de entrada en producción puede divergir de la distribución de los datos de entrenamiento a lo largo del tiempo. Cuando esto ocurre, las predicciones del modelo se vuelven menos precisas aunque el modelo, el código y la infraestructura no hayan cambiado. Detectar drift requiere monitorizar la distribución estadística de los inputs y de los outputs a lo largo del tiempo y comparar con las distribuciones de entrenamiento.

**Data quality.** Un sistema de ML en producción puede recibir inputs malformados, con valores fuera de rango, con campos faltantes o con encodings incorrectos. A diferencia de un servicio web clásico donde esto devolvería un error HTTP 400, un modelo puede producir predicciones con estas entradas sin fallar explícitamente, generando silenciosamente resultados incorrectos. La validación de calidad de datos en el punto de entrada es una responsabilidad de ML SRE que no existe en el SRE clásico.

### 7.3 Runbook de puesta en servicio paso a paso

Un runbook es un documento operativo que describe paso a paso qué hacer en cada fase de una operación o incidente. El runbook de puesta en servicio cubre:

```
RUNBOOK: PUESTA EN SERVICIO DE MODELO DE IA

PRE-REQUISITOS
- [ ] Smoke tests pasados en staging
- [ ] Configuracion de alertas revisada y activa
- [ ] Runbook distribuido al equipo de on-call
- [ ] Backup del modelo anterior confirmado en registry

FASE 1: DESPLIEGUE INICIAL
1. Desplegar nueva version en produccion (sin tráfico)
2. Verificar que el pod alcanza estado Running y Ready
3. Ejecutar suite de smoke tests contra la IP interna del pod
4. Decision go/no-go automatica basada en resultado de smoke tests

FASE 2: SHADOW MODE (minimo 1 hora)
1. Activar mirroring de trafico al nuevo modelo (Istio VirtualService)
2. Monitorizar divergencia de predicciones cada 30 minutos
3. Criterio de avance: tasa de error < 0.5%, divergencia explicada

FASE 3: CANARY PROGRESIVO
1. Canary-weight: 1 → esperar 30 min → verificar criterios
2. Canary-weight: 5 → esperar 2 horas → verificar criterios
3. Canary-weight: 20 → esperar 4 horas → verificar criterios
4. Canary-weight: 100 → inicio de observacion intensiva

FASE 4: OBSERVACION INTENSIVA (24-48 horas)
1. Revision de dashboards cada hora
2. Equipo de desarrollo en disponibilidad para respuesta rapida
3. Calibracion final de umbrales de alerta

FASE 5: CIERRE
1. Confirmar metricas estables durante 24 horas al 100%
2. Transferir responsabilidad al equipo de operaciones
3. Completar documento de handoff
4. Notificar cierre formal del despliegue
```

---

## 8. Handoff documentation

### 8.1 Propósito del documento de handoff

El documento de handoff es la evidencia formal de que el sistema está listo para ser operado de forma autónoma por el equipo de operaciones. Su propósito es que cualquier miembro del equipo de operaciones, sin conocimiento previo del modelo ni del proceso de desarrollo, pueda gestionar el sistema en operación normal y responder a los incidentes más comunes.

Un handoff bien ejecutado elimina el bus factor: el riesgo de que el conocimiento crítico sobre el sistema esté concentrado en unas pocas personas. Si el único ingeniero que conoce el sistema está de vacaciones cuando se produce un incidente a las dos de la mañana, el equipo de on-call debe poder resolverlo con la documentación disponible.

### 8.2 Contenido del documento de handoff

**SLOs comprometidos.** Los Service Level Objectives acordados con el negocio o con los clientes del servicio. Por ejemplo: disponibilidad >= 99.9% mensual, latencia p50 <= 200ms, latencia p99 <= 500ms, error rate <= 0.5%.

**Runbook de operaciones normales.** Cómo arrancar el servicio, cómo comprobar que está sano, cómo escalar horizontalmente cuando la carga aumenta, cómo actualizar la configuración sin reiniciar el modelo.

**Escalado de incidencias.** Para cada tipo de alerta, qué pasos seguir, qué condiciones indican que el problema se puede resolver en el nivel de operaciones y qué condiciones requieren escalar al equipo de ML engineering.

**Contactos.** Nombre, email y canal de comunicación del responsable técnico del modelo, del responsable de datos, del responsable de infraestructura y del propietario del negocio.

**Limitaciones conocidas.** Comportamientos del modelo que son conocidos y aceptados: tipos de inputs que producen respuestas de menor calidad, idiomas no soportados, rangos de valores fuera de los que el modelo fue entrenado, latencia aumentada bajo cargas muy altas.

### 8.3 Ejemplo de documento de handoff completo

```markdown
# Handoff Document — Modelo de Clasificacion de Incidencias v2.1

Fecha de despliegue: 2026-06-15
Responsable tecnico: equipo-mleng@empresa.com
Responsable de operaciones: equipo-sre@empresa.com

---

## SLOs comprometidos

| Metrica | Umbral | Periodo |
|---------|--------|---------|
| Disponibilidad | >= 99.9% | Mes natural |
| Latencia p50 | <= 150ms | Semana |
| Latencia p99 | <= 400ms | Semana |
| Error rate | <= 0.5% | Dia |

## Acceso al sistema

- Endpoint de produccion: https://model.interna.empresa.com/v1/predict
- Dashboard de metricas: https://grafana.interna.empresa.com/d/modelo-v2
- Logs centralizados: Loki, label: app=modelo-clasificacion

## Operaciones normales

### Comprobar estado del servicio
kubectl get pods -n produccion -l app=modelo-clasificacion

### Escalar el numero de replicas
kubectl scale deployment modelo-clasificacion -n produccion --replicas=N

### Reiniciar el servicio sin downtime
kubectl rollout restart deployment modelo-clasificacion -n produccion

## Escalado de incidencias

| Alerta | Accion primer nivel | Escalar si |
|--------|---------------------|------------|
| ErrorRateAlto | Revisar logs, comprobar calidad de datos de entrada | Error persiste > 15 min |
| LatenciaP99FueraDeSLO | Escalar replicas, comprobar uso de GPU | Escalar no resuelve |
| GPUSaturada | Escalar replicas o node pool | No hay capacidad disponible |
| DisponibilidadBaja | Comprobar pods, revisar readiness probe | Pods no arrancan |

## Contactos

| Rol | Persona | Canal |
|-----|---------|-------|
| ML Engineering | Juan Garcia | Slack: @jgarcia |
| Infraestructura / SRE | Marta Lopez | Slack: @mlopez |
| Propietario de negocio | Carlos Ruiz | cruiz@empresa.com |

## Limitaciones conocidas

- El modelo no esta optimizado para textos de menos de 10 palabras.
  La prediccion puede ser incorrecta para inputs muy cortos.
- El modelo fue entrenado con datos en espanol e ingles.
  Otros idiomas produciran predicciones no fiables.
- Bajo cargas superiores a 500 req/s por replica, la latencia p99
  puede superar el SLO. Escalar proactivamente antes de llegar a ese limite.
```

---

## 9. Actividades prácticas

### Actividad 1 — Diseño e implementación de una suite de smoke tests

El alumno recibe un servicio de inferencia ficticio desplegado en un entorno de laboratorio. Debe diseñar una suite de smoke tests con pytest y requests que cubra las cuatro dimensiones estudiadas: disponibilidad del endpoint, respuesta correcta a un input de referencia, latencia dentro de SLO y ausencia de errores en logs. La suite debe ser ejecutable desde la línea de comandos y debe producir un informe claro de qué pruebas han pasado y cuáles han fallado. Se evaluará la cobertura de los tests, la claridad de los mensajes de error cuando una prueba falla y la ejecutabilidad del código entregado.

### Actividad 2 — Configuración de canary deployment en Kubernetes

El alumno tiene acceso a un clúster de Kubernetes con nginx-ingress instalado y dos versiones de un servicio de modelo desplegadas (v1 y v2). Debe configurar un canary deployment dirigiendo el 5% del tráfico a v2, verificar que el routing funciona correctamente usando un script de prueba de carga (wrk o hey), y documentar los pasos para incrementar el porcentaje a 20% y luego a 100%. Opcionalmente, debe configurar la reversión automática del canary si la tasa de error supera el 1%.

### Actividad 3 — Configuración de alertas con Prometheus y Alertmanager

Dado un entorno de laboratorio con Prometheus y Alertmanager ya instalados y un servicio de modelo que expone métricas en `/metrics`, el alumno debe escribir las reglas de alerta en YAML para las cuatro métricas críticas estudiadas (error rate, latencia p99, utilización de GPU, disponibilidad), cargarlas en Prometheus, y verificar que las alertas se disparan correctamente generando condiciones de fallo artificiales en el servicio. Debe también configurar Alertmanager para enrutar las alertas críticas a un canal de Slack de prueba.

### Actividad 4 — Elaboración de un documento de handoff completo

El alumno recibe un briefing con la descripción de un sistema de IA ficticio: tipo de modelo, SLOs acordados, arquitectura de despliegue y limitaciones conocidas del modelo. Debe elaborar un documento de handoff completo en Markdown, siguiendo la estructura estudiada en la unidad, que permita a un equipo de operaciones gestionar el sistema de forma autónoma. Se evaluará la completitud, la claridad y la ausencia de información que requiera conocimiento previo del equipo de desarrollo para ser interpretada.

---

## 10. Referencias

- Beyer, B., Jones, C., Petoff, J., Murphy, N. R. (2016). *Site Reliability Engineering: How Google Runs Production Systems*. O'Reilly Media. https://sre.google/sre-book/table-of-contents/

- Google SRE. *The Site Reliability Workbook*. https://sre.google/workbook/table-of-contents/

- Huyen, C. (2022). *Designing Machine Learning Systems*. O'Reilly Media. https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/

- Kubernetes. *Configure Liveness, Readiness and Startup Probes*. https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/

- Kubernetes. *Deployments — Rolling Updates*. https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

- kubernetes/ingress-nginx. *Canary Deployments*. https://kubernetes.github.io/ingress-nginx/examples/canary/

- Istio. *Traffic Management — Mirroring*. https://istio.io/latest/docs/tasks/traffic-management/mirroring/

- Istio. *Traffic Management — Traffic Shifting*. https://istio.io/latest/docs/tasks/traffic-management/traffic-shifting/

- Prometheus. *Alerting Rules*. https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/

- Prometheus. *Alertmanager Configuration*. https://prometheus.io/docs/alerting/latest/configuration/

- Sculley, D. et al. (2015). *Hidden Technical Debt in Machine Learning Systems*. NeurIPS 2015. https://proceedings.neurips.cc/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf
