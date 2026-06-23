---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD6 · Monitorización y mantenimiento | MP02 · Despliegue de sistemas de IA'
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

# UD6 · Monitorización y mantenimiento

MP02 · Despliegue de sistemas de IA

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno sera capaz de:

- Verificar que el sistema de notificacion de alarmas, monitorización y respaldo funciona correctamente
- Analizar registros de rendimiento, calidad del modelo e integridad de datos
- Detectar drift de distribución mediante pruebas estadísticas (PSI, Kolmogorov-Smirnov, Jensen-Shannon)
- Aplicar operaciones de correccion manuales o supervisadas segun la causa del problema
- Documentar cada intervencion con causa, impacto, accion correctiva y logs

> **Resultado de aprendizaje:** Implanta el Plan de monitorización y mantenimiento para garantizar la calidad y disponibilidad del servicio.

---

## Las cuatro dimensiones de la monitorización de IA

### Que vigilar en un sistema de IA en produccion

```
┌─────────────────────────────────────────────────────────────┐
│               MONITORIZACIÓN DE SISTEMAS DE IA              │
├───────────────────┬───────────────────┬─────────────────────┤
│  RENDIMIENTO      │  CALIDAD          │  DATOS              │
│  TECNICO          │  DEL MODELO       │                     │
│  ─────────        │  ─────────────    │  ─────              │
│  Latencia P50/99  │  Accuracy         │  Distribucion       │
│  Throughput       │  F1, AUROC        │  de entradas        │
│  Tasa de error    │  RMSE, MAE        │  Valores nulos      │
│  Uptime / SLA     │  vs. baseline     │  Outliers           │
│  CPU, GPU, RAM    │                   │  Formatos           │
└───────────────────┴───────────────────┴─────────────────────┘
                              │
              ┌───────────────┘
              │  INFRAESTRUCTURA
              │  ─────────────────
              │  Almacenamiento
              │  Red
              │  Colas de mensajes
              └──────────────────
```

---

## Monitorización tecnica: metricas de servicio

### Metricas SLI/SLO para un servicio de inferencia

| SLI (Indicador) | SLO (Objetivo) | Alarma de aviso | Alarma critica |
|---|---|---|---|
| Latencia P99 | < 500 ms | > 400 ms | > 500 ms |
| Latencia P50 | < 100 ms | > 80 ms | > 100 ms |
| Tasa de error HTTP 5xx | < 0.1 % | > 0.05 % | > 0.1 % |
| Disponibilidad (uptime) | > 99.9 % | < 99.95 % | < 99.9 % |
| Throughput | > 500 req/s | < 600 req/s | < 500 req/s |

### Consulta Prometheus para latencia P99

```promql
# Latencia P99 de inferencia en los ultimos 5 minutos
histogram_quantile(0.99,
  rate(model_latency_seconds_bucket[5m])
)
```

---

## Monitorización de calidad del modelo

### Degradacion de la calidad del modelo en produccion

La calidad de un modelo de IA puede degradarse en produccion aunque la infraestructura funcione perfectamente. Las causas principales son:

| Causa | Descripcion | Ejemplo |
|---|---|---|
| Drift de datos | La distribucion de las entradas cambia | Los patrones de fraude evolucionan |
| Drift de concepto | La relacion entre entrada y salida cambia | Los precios de mercado cambian el valor de un inmueble |
| Rotacion de etiquetas | Las etiquetas de referencia cambian de definicion | Un diagnostico que antes era "positivo" ahora se clasifica diferente |
| Datos de peor calidad | La calidad de los datos de entrada empeora | Un sensor empieza a dar lecturas ruidosas |

### Comparacion con la linea base (baseline)

```python
# Calcular la accuracy actual y comparar con el baseline de produccion
from sklearn.metrics import accuracy_score

accuracy_actual = accuracy_score(etiquetas_reales, predicciones_recientes)
baseline_accuracy = 0.94  # Accuracy al momento del despliegue

degradacion = baseline_accuracy - accuracy_actual
if degradacion > 0.03:  # Umbral de alerta: 3 puntos de accuracy
    disparar_alarma("degradacion_modelo", degradacion)
```

---

## Deteccion de drift: Population Stability Index (PSI)

### Que es el PSI y como interpretarlo

El **Population Stability Index (PSI)** mide cuanto ha cambiado la distribucion de una variable entre el periodo de referencia (entrenamiento) y el periodo actual (produccion).

| Valor de PSI | Interpretacion | Accion recomendada |
|---|---|---|
| < 0.10 | Cambio insignificante | Sin accion |
| 0.10 – 0.25 | Cambio moderado | Investigar la causa |
| > 0.25 | Cambio significativo | Reentrenar o revisar el modelo |

### Calculo del PSI

```python
import numpy as np

def calcular_psi(referencia, actual, bins=10):
    breakpoints = np.percentile(referencia, np.linspace(0, 100, bins + 1))
    ref_counts = np.histogram(referencia, breakpoints)[0] / len(referencia)
    act_counts = np.histogram(actual, breakpoints)[0] / len(actual)
    # Evitar division por cero
    ref_counts = np.where(ref_counts == 0, 0.0001, ref_counts)
    act_counts = np.where(act_counts == 0, 0.0001, act_counts)
    psi = np.sum((act_counts - ref_counts) * np.log(act_counts / ref_counts))
    return psi
```

---

## Deteccion de drift: Kolmogorov-Smirnov

### La prueba KS para comparar distribuciones continuas

La prueba de **Kolmogorov-Smirnov (KS)** es una prueba estadistica no parametrica que compara dos distribuciones continuas. En MLOps se usa para detectar si la distribucion de las entradas en produccion difiere significativamente de la distribucion de entrenamiento.

```python
from scipy import stats

# Comparar la distribucion de una feature entre entrenamiento y produccion
feature_entrenamiento = datos_entrenamiento['importe_transaccion']
feature_produccion    = datos_produccion['importe_transaccion']

estadistico_ks, p_valor = stats.ks_2samp(feature_entrenamiento,
                                          feature_produccion)

print(f"KS statistic: {estadistico_ks:.4f}")
print(f"p-valor: {p_valor:.6f}")

# Si p-valor < 0.05, las distribuciones son significativamente diferentes
if p_valor < 0.05:
    disparar_alarma("drift_feature_importe", estadistico_ks)
```

---

## Deteccion de drift: Jensen-Shannon

### Divergencia Jensen-Shannon para distribuciones de probabilidad

La **divergencia Jensen-Shannon (JS)** mide la similitud entre dos distribuciones de probabilidad. A diferencia de la KL-Divergence, es simetrica y siempre finita (valor entre 0 y 1 si se usa la raiz cuadrada).

```python
from scipy.spatial.distance import jensenshannon
import numpy as np

# Calcular la divergencia JS entre la distribucion de predicciones
# en el periodo de referencia y el periodo actual
pred_referencia = np.array([0.70, 0.20, 0.10])  # Distribucion de clases en entrenamiento
pred_actuales   = np.array([0.55, 0.30, 0.15])  # Distribucion de clases en produccion

distancia_js = jensenshannon(pred_referencia, pred_actuales)
print(f"Distancia JS: {distancia_js:.4f}")

# Umbral tipico: 0.05 para aviso, 0.10 para accion correctiva
if distancia_js > 0.10:
    disparar_alarma("drift_salidas_modelo", distancia_js)
```

---

## Prueba Chi-cuadrado para variables categoricas

### Deteccion de drift en variables categoricas

Para variables categoricas (tipo de operacion, categoria de producto, pais de origen), la prueba de Kolmogorov-Smirnov no es aplicable. Se usa la **prueba Chi-cuadrado de bondad de ajuste**.

```python
from scipy import stats
import numpy as np

# Distribucion de la variable categorica en entrenamiento
frec_entrenamiento = np.array([5000, 3000, 1500, 500])  # Frecuencias absolutas

# Distribucion en produccion (mismo periodo de tiempo)
frec_produccion = np.array([4200, 2800, 1800, 1200])

# La prueba Chi-cuadrado compara las distribuciones
chi2, p_valor = stats.chisquare(frec_produccion,
                                f_exp=frec_entrenamiento * sum(frec_produccion) / sum(frec_entrenamiento))

print(f"Chi2: {chi2:.2f}, p-valor: {p_valor:.6f}")
if p_valor < 0.05:
    disparar_alarma("drift_variable_categorica_tipo_op", chi2)
```

---

## Verificacion del sistema de respaldo y notificaciones

### Checklist de verificacion del Plan de monitorización

Antes de dar por implantado el Plan de monitorización, se verifica que cada componente funciona correctamente:

| Componente | Prueba de verificacion | Resultado esperado |
|---|---|---|
| Prometheus scraping | `curl http://modelo:8080/metrics` | Metricas en formato texto |
| Grafana dashboards | Abrir los dashboards y verificar datos | Datos en tiempo real |
| Alertmanager | `amtool alert add test-alert` | Alarma visible en UI |
| Notificacion a Slack | Disparar una alarma de prueba | Mensaje en canal `#mlops-alerts` |
| Notificacion por correo | Disparar una alarma de prueba | Correo recibido en < 5 min |
| PagerDuty (on-call) | Disparar una alarma critica de prueba | Notificacion movil recibida |
| Backup de modelos | Restaurar el backup mas reciente en entorno de prueba | Modelo restaurado y funcional |

---

## Operaciones de correccion: escalado y rollback

### Cuando aplicar cada correccion

| Sintoma | Causa probable | Correccion |
|---|---|---|
| Latencia alta, CPU > 90% | Demanda superior a la capacidad | Escalado horizontal (mas pods) |
| Errores de OOM en GPU | Batch demasiado grande | Reducir batch_size; escalar verticalmente |
| Tasa de error alta tras despliegue | Regresion en el nuevo modelo | Rollback a la version anterior |
| Accuracy en produccion cayendo | Drift de datos o concepto | Reentrenamiento con datos recientes |
| Datos corruptos en la entrada | Fallo en un pipeline upstream | Redireccion del flujo; modo de operacion reducida |

### Rollback con Kubernetes

```bash
# Ver el historial de despliegues
kubectl rollout history deployment/modelo-fraude -n produccion

# Volver a la version anterior (la que estaba antes del ultimo despliegue)
kubectl rollout undo deployment/modelo-fraude -n produccion

# Volver a una revision especifica
kubectl rollout undo deployment/modelo-fraude --to-revision=5 -n produccion

# Verificar que el rollback ha terminado
kubectl rollout status deployment/modelo-fraude -n produccion
```

---

## Modo de operacion reducida

### Cuando y como activar el modo de operacion reducida

El modo de operacion reducida permite mantener el servicio cuando el sistema de IA no puede operar normalmente, usando alternativas mas simples o resultados en cache.

| Situacion | Modo de operacion reducida |
|---|---|
| Modelo no disponible | Devolver la prediccion por defecto (regla de negocio) |
| Latencia critica superada | Devolver el ultimo resultado calculado (cache) |
| Fallo de la fuente de datos | Usar datos historicos recientes |
| Drift critico detectado | Bloquear predicciones hasta revision humana |

```python
def predecir_con_fallback(datos):
    try:
        return modelo.predict(datos), "normal"
    except ModeloNoDisponibleError:
        logger.error("Modelo no disponible. Usando prediccion por defecto.")
        return PREDICCION_POR_DEFECTO, "modo_reducida"
    except TimeoutError:
        return cache.obtener_ultimo(datos['id']), "cache"
```

---

## Documentacion de intervenciones de mantenimiento

### Estructura del registro de intervencion (incident record)

| Campo | Descripcion | Ejemplo |
|---|---|---|
| Identificador | ID unico de la intervencion | `INC-2025-0342` |
| Fecha y hora de inicio | ISO 8601 | `2025-04-10T03:22:00+02:00` |
| Detectado por | Sistema o persona que detecto el problema | Alerta Prometheus: latencia_P99 > 500ms |
| Causa raiz | Causa identificada tras el analisis | Drift de datos en feature `importe_transaccion` (PSI=0.31) |
| Impacto | Servicios afectados y duracion | Degradacion de accuracy durante 4 horas |
| Accion correctiva | Que se hizo | Reentrenamiento del modelo con datos de los ultimos 30 dias |
| Responsable | Quien realizo la intervencion | M. Garcia |
| Resultado | Estado tras la correccion | Accuracy restaurada; PSI=0.07 |
| Logs adjuntos | Referencia a los logs | `/logs/inc-2025-0342.log` |

---

## Actividad practica: analisis de drift y correccion

### Escenario

Un modelo de prediccion de precios inmobiliarios fue entrenado con datos de 2023. En produccion, el equipo de monitorización detecta las siguientes senales en abril de 2025:
- PSI de la feature `precio_metro_cuadrado`: 0.38
- Accuracy en datos etiquetados recientes: cayó de 0.89 a 0.74
- P99 de latencia: estable en 180 ms (sin cambios)

### Tarea

1. Interpretar los resultados de monitorización: que tipo de drift se ha producido y por que
2. Calcular el PSI manualmente con un ejemplo simplificado de 5 bins
3. Proponer las acciones correctivas en orden de prioridad
4. Redactar el registro de intervencion completo para la correccion elegida
5. Definir como prevenir esta situacion en el futuro (monitorizacion proactiva)

---

## Puntos clave de la UD6

- La monitorización de IA tiene cuatro dimensiones: rendimiento tecnico, calidad del modelo, datos e infraestructura; ninguna es prescindible
- El **drift** es el enemigo silencioso de los modelos en produccion: un modelo puede seguir funcionando tecnicamente bien pero producir predicciones cada vez menos utiles
- Las tres pruebas estadisticas clave para deteccion de drift son: **PSI** (variables de entrada, interpretacion sencilla), **KS** (distribuciones continuas, rigor estadistico) y **Jensen-Shannon** (distribuciones de salida del modelo)
- El rollback debe poder ejecutarse en menos de 5 minutos: si tarda mas, el tiempo de recuperacion (RTO) es inaceptable para la mayoria de servicios criticos
- El modo de operacion reducida no es un fallo: es una decision disenada que mantiene el servicio disponible ante fallos parciales
- Cada intervencion, por pequena que sea, debe quedar documentada con causa, impacto, accion y resultado

---

## Criterios de evaluacion — UD6

| Criterio | Indicadores de logro |
|---|---|
| Verifica el sistema de monitorización | Comprueba Prometheus, Grafana, Alertmanager y las notificaciones; documenta el resultado de cada verificacion |
| Detecta anomalias con pruebas estadisticas | Calcula PSI, KS y JS correctamente; interpreta los resultados y los relaciona con una accion |
| Aplica correcciones | Selecciona la correccion adecuada segun la causa; ejecuta el rollback cuando es necesario; activa el modo reducida si procede |
| Documenta las intervenciones | Completa el registro de intervencion con todos los campos; adjunta logs; registra causa raiz y resultado |

---

[← Volver a MP02](../index.md)
