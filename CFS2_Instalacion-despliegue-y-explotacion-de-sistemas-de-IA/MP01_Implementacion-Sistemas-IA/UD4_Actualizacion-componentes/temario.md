# UD4 · Actualización de componentes en sistemas de IA

---

## 1. Introducción — la actualización como riesgo gestionado: downtime cero en sistemas críticos

Los sistemas de inteligencia artificial en producción no son estructuras estáticas. Los modelos se degradan por deriva de datos, las dependencias reciben parches de seguridad, los frameworks evolucionan y los requisitos de negocio cambian. Todo esto obliga a actualizar componentes de forma regular. Sin embargo, actualizar un sistema que está sirviendo peticiones en tiempo real plantea un dilema clásico: cualquier interrupción del servicio tiene un coste medible —económico, reputacional o en términos de disponibilidad comprometida con clientes y reguladores.

En sistemas de IA críticos —plataformas de scoring crediticio en tiempo real, sistemas de detección de fraude, asistentes conversacionales con SLA contractuales, o pipelines de diagnóstico médico asistido—, el downtime no es una opción aceptable. Un sistema que procesa decenas de miles de peticiones por segundo no puede permitirse ni siquiera un reinicio de treinta segundos sin consecuencias. Las arquitecturas modernas han respondido a esta presión desarrollando un conjunto de estrategias, herramientas y procedimientos que permiten actualizar componentes —incluyendo modelos de machine learning, librerías, drivers de hardware y configuraciones— sin interrumpir el servicio.

Esta unidad aborda la actualización de componentes desde un enfoque de ingeniería de producción. No se trata únicamente de saber cómo ejecutar un comando de despliegue, sino de comprender el ciclo completo: planificación, pruebas previas, estrategia de despliegue, validación post-despliegue y procedimientos de rollback cuando algo no funciona como se esperaba. La cultura DevOps y la disciplina de Site Reliability Engineering (SRE) han sistematizado estas prácticas durante la última década, y el mundo MLOps las ha adaptado a las particularidades de los sistemas de IA, donde el componente que se actualiza —el modelo— tiene un comportamiento estadístico que lo hace más difícil de validar que el software tradicional.

El objetivo central de esta unidad es que el alumno sea capaz de planificar y ejecutar actualizaciones de componentes en sistemas de IA en producción manteniendo la disponibilidad del servicio, con procedimientos de validación rigurosos y con la capacidad de revertir cualquier cambio si se detectan problemas.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el alumno será capaz de:

- Distinguir entre las principales estrategias de actualización sin downtime (rolling update, blue-green, canary) y seleccionar la más adecuada según el contexto de riesgo, coste y complejidad del sistema.
- Configurar despliegues en Kubernetes utilizando los parámetros `maxSurge` y `maxUnavailable` para controlar el ritmo y el riesgo de una actualización progresiva.
- Diseñar e implementar un pipeline de validación pre-actualización que incluya pruebas unitarias, de integración y de regresión de métricas de modelo.
- Aplicar versionado semántico a modelos de machine learning y gestionar un Model Registry con MLflow como fuente de verdad única para el ciclo de vida de los modelos.
- Definir criterios objetivos para activar un rollback automático o manual, y ejecutar dicho rollback con los comandos y procedimientos apropiados.
- Gestionar la actualización segura de dependencias de bajo nivel (CUDA/cuDNN, librerías Python, versiones de framework) sin romper la compatibilidad con modelos ya serializados.
- Redactar changelogs estructurados y comunicar breaking changes a los equipos consumidores del sistema con un período de deprecación adecuado.

---

## 3. Estrategias de actualización sin downtime

### 3.1 Rolling update en Kubernetes

El rolling update es la estrategia de actualización por defecto en Kubernetes. Consiste en sustituir las instancias del componente antiguo por instancias del nuevo de forma progresiva, de modo que en ningún momento el total de réplicas disponibles cae por debajo de un umbral mínimo. El clúster mantiene capacidad de servicio durante todo el proceso.

Los dos parámetros que controlan el comportamiento de un rolling update son `maxSurge` y `maxUnavailable`, ambos definidos dentro del campo `strategy` del recurso `Deployment`.

- `maxSurge`: número máximo de pods adicionales que pueden existir por encima del número deseado de réplicas durante la actualización. Puede expresarse como valor absoluto o como porcentaje. Un valor de `1` significa que en ningún momento habrá más de `replicas + 1` pods en ejecución.
- `maxUnavailable`: número máximo de pods que pueden estar no disponibles durante la actualización. Un valor de `0` garantiza que el servicio nunca pierde capacidad, aunque ralentiza el proceso porque cada pod nuevo debe estar Ready antes de terminar el antiguo.

Ejemplo de manifiesto `Deployment` para un servicio de inferencia:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: modelo-inferencia
  namespace: produccion
spec:
  replicas: 4
  selector:
    matchLabels:
      app: modelo-inferencia
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: modelo-inferencia
    spec:
      containers:
        - name: inferencia
          image: registry.empresa.com/modelo-inferencia:v2.1.0
          ports:
            - containerPort: 8080
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 5
          resources:
            requests:
              memory: "2Gi"
              cpu: "1"
            limits:
              memory: "4Gi"
              cpu: "2"
```

Con esta configuración y cuatro réplicas, Kubernetes creará un quinto pod con la nueva imagen, esperará a que su readiness probe responda con éxito y solo entonces terminará uno de los pods antiguos. Repetirá este ciclo hasta completar la actualización de todas las réplicas. La readiness probe es crítica: sin ella, Kubernetes no tiene mecanismo para saber si el nuevo pod está realmente listo para servir tráfico.

### 3.2 Blue-green deployment

En un despliegue blue-green se mantienen dos entornos de producción idénticos en todo momento: el entorno activo (blue) y el entorno de standby (green). El tráfico de usuarios va íntegramente al entorno blue. Cuando se quiere actualizar, se despliega la nueva versión completa en el entorno green, se valida exhaustivamente sin que ningún usuario real la use, y en el momento oportuno se redirige todo el tráfico de blue a green de forma instantánea. Si algo falla, el rollback es igualmente instantáneo: se devuelve el tráfico al entorno blue, que sigue intacto.

Las ventajas de esta estrategia son claras: el swap de tráfico es atómico (no hay un período de transición con dos versiones sirviendo simultáneamente), el entorno antiguo actúa como seguro de rollback sin necesidad de reconstruir nada, y la validación del nuevo entorno puede ser tan exhaustiva como se requiera sin límite de tiempo.

El coste principal es infraestructural: se necesita el doble de recursos en todo momento. En sistemas de IA que requieren GPUs, este coste puede ser prohibitivo. Una variante habitual es mantener el entorno green en estado de "warm standby" con capacidad reducida y escalarlo solo durante la ventana de actualización.

El swap de tráfico puede implementarse de distintas maneras: actualizando el selector de un `Service` de Kubernetes para que apunte al nuevo conjunto de pods, modificando las reglas de un balanceador de carga externo, o actualizando un registro DNS con TTL muy bajo.

### 3.3 Canary deployment

El despliegue canary introduce la nueva versión de forma incremental, desviando inicialmente solo una pequeña fracción del tráfico real hacia ella. Si las métricas son satisfactorias, el porcentaje se aumenta progresivamente hasta completar la migración. Si se detectan problemas, se corta el tráfico hacia la versión canary antes de que afecte a la mayoría de los usuarios.

Esta estrategia es especialmente valiosa en sistemas de IA porque permite validar el comportamiento del nuevo modelo con datos de producción reales —algo que no es posible en entornos de staging— y detectar regresiones estadísticas que solo se manifiestan con ciertos patrones de datos que no estaban representados en el conjunto de test.

En Kubernetes, el canary puede implementarse de forma nativa usando dos Deployments con el mismo selector de servicio pero con distintos números de réplicas: si el Deployment estable tiene 9 réplicas y el canary tiene 1, aproximadamente el 10 % del tráfico irá al canary.

Para un control más preciso, se usan herramientas como `nginx-ingress` con anotaciones de peso de tráfico o Istio con recursos `VirtualService`:

```yaml
# Ejemplo con Istio VirtualService
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: modelo-inferencia
spec:
  hosts:
    - modelo-inferencia
  http:
    - route:
        - destination:
            host: modelo-inferencia-stable
            port:
              number: 8080
          weight: 90
        - destination:
            host: modelo-inferencia-canary
            port:
              number: 8080
          weight: 10
```

Modificando el campo `weight`, el equipo puede ir aumentando el porcentaje de tráfico canary de 10 a 25, a 50, a 100, evaluando métricas entre cada incremento. Herramientas como Argo Rollouts automatizan este proceso con análisis integrado de métricas de Prometheus.

### 3.4 Comparativa de estrategias

| Estrategia     | Riesgo de impacto en usuarios | Complejidad operativa | Velocidad de rollback | Coste de infraestructura |
|----------------|-------------------------------|----------------------|----------------------|--------------------------|
| Rolling update | Medio (versiones mixtas en tránsito) | Baja (nativa en K8s) | Medio (~minutos) | Bajo (solo `maxSurge` adicional) |
| Blue-green     | Bajo (swap atómico) | Media (dos entornos) | Muy bajo (~segundos) | Alto (doble de recursos) |
| Canary         | Muy bajo (exposición limitada) | Alta (routing de tráfico, análisis de métricas) | Bajo (~minutos) | Medio (solo el porcentaje canary) |

La elección entre estrategias depende del apetito de riesgo del negocio, la disponibilidad de recursos de infraestructura y la madurez del pipeline de observabilidad. En sistemas donde el coste de un fallo es muy alto (medicina, finanzas) se prefiere canary con umbrales automáticos. En sistemas donde el coste de infraestructura domina, el rolling update con una readiness probe robusta suele ser suficiente.

---

## 4. Gestión de versiones de modelos

### 4.1 Versionado semántico de modelos de ML

El versionado semántico (SemVer, MAJOR.MINOR.PATCH) fue concebido para software con APIs bien definidas, pero se puede aplicar de forma coherente a modelos de machine learning con las siguientes convenciones:

- **MAJOR**: cambio en la arquitectura del modelo, en el schema de entrada/salida de la API, o en la tarea que resuelve. Un cambio MAJOR implica que los clientes existentes del modelo necesitan adaptar su código.
- **MINOR**: reentrenamiento con nuevos datos, ajuste de hiperparámetros, o mejora de métricas sin cambio de interfaz. La API sigue siendo compatible hacia atrás.
- **PATCH**: corrección de un bug en el preprocesado, ajuste de un umbral de clasificación, o actualización de metadata. Sin cambios funcionales significativos.

Esta convención permite a los equipos consumidores del modelo saber, de un vistazo, si una actualización requiere trabajo de su parte o es transparente.

### 4.2 Model Registry con MLflow

El Model Registry de MLflow actúa como fuente de verdad única para el ciclo de vida de los modelos. Cada versión de un modelo registrada en MLflow tiene asociados sus artefactos (pesos, configuración, preprocesadores), sus métricas de evaluación, los parámetros de entrenamiento y el estado en el ciclo de vida (Staging, Production, Archived).

El flujo típico de promoción de un modelo nuevo:

1. El pipeline de entrenamiento registra el nuevo modelo en MLflow con sus métricas.
2. El equipo de ML revisa las métricas y promueve el modelo a `Staging`.
3. El pipeline de validación automática ejecuta los tests de regresión contra la versión en Staging.
4. Si los tests pasan, el modelo se promueve a `Production`. La versión anterior pasa a `Archived`.
5. El sistema de despliegue consulta el Model Registry para obtener el URI del artefacto en `Production` y despliega la nueva versión.

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Promover una versión específica a Production
client.transition_model_version_stage(
    name="modelo-clasificacion-fraude",
    version="12",
    stage="Production",
    archive_existing_versions=True  # archiva la versión anterior automáticamente
)
```

### 4.3 Política de retención de versiones

Mantener todas las versiones históricas de un modelo no es práctico: los artefactos de modelos grandes pueden ocupar decenas de gigabytes cada uno. Una política de retención razonable podría ser:

- Mantener las últimas N versiones en estado `Archived` (por ejemplo, las tres últimas).
- Retener versiones que correspondan a hitos (primera versión en producción, versión de referencia para auditoría regulatoria) de forma indefinida con etiqueta `milestone`.
- Eliminar automáticamente versiones más antiguas que el umbral de retención si no tienen etiquetas especiales.

### 4.4 Backward compatibility de la API del modelo

Cuando se actualiza el modelo pero se mantiene la misma versión MAJOR, la API debe ser compatible hacia atrás: los mismos campos de entrada deben seguir siendo aceptados con la misma semántica, y los campos de salida deben mantener su estructura. Los cambios que afectan a la compatibilidad —por ejemplo, renombrar un campo, cambiar el tipo de una salida, o eliminar un campo— se gestionan como cambios MAJOR con un período de deprecación.

### 4.5 Múltiples versiones en paralelo para A/B testing

En escenarios de A/B testing, el sistema necesita servir simultáneamente dos versiones del modelo a diferentes segmentos de usuarios. Esto requiere que el Model Registry mantenga dos versiones en estado `Production` con etiquetas diferenciadas (por ejemplo, `production-a` y `production-b`), y que el sistema de routing dirija las peticiones al modelo correcto según el identificador de usuario o sesión.

---

## 5. Testing de regresión en actualizaciones

### 5.1 Pipeline de validación pre-actualización

Ningún modelo o componente debe llegar a producción sin pasar por un pipeline de validación estructurado. Este pipeline tiene varias capas:

**Unit tests**: verifican que las funciones individuales de preprocesado, transformación y postprocesado funcionan correctamente con entradas conocidas. Se ejecutan en segundos y son la primera barrera de calidad.

**Integration tests**: comprueban que el modelo cargado desde el artefacto serializado produce las predicciones correctas cuando se le pasan ejemplos de referencia completos, incluyendo el pipeline de preprocesado. Detectan problemas de compatibilidad entre versiones de librerías y el formato del artefacto.

**Regression tests de métricas**: evalúan el modelo sobre un conjunto de datos de holdout fijo y verifican que las métricas de negocio y técnicas no caen por debajo de los umbrales mínimos establecidos. Por ejemplo:

```python
def test_regresion_metricas(modelo_nuevo, datos_holdout, umbrales):
    predicciones = modelo_nuevo.predict(datos_holdout.X)
    
    auc = roc_auc_score(datos_holdout.y, predicciones)
    precision = precision_score(datos_holdout.y, predicciones > 0.5)
    recall = recall_score(datos_holdout.y, predicciones > 0.5)
    
    assert auc >= umbrales["auc_minimo"], f"AUC {auc:.4f} por debajo del umbral {umbrales['auc_minimo']}"
    assert precision >= umbrales["precision_minima"], f"Precision {precision:.4f} por debajo del umbral"
    assert recall >= umbrales["recall_minimo"], f"Recall {recall:.4f} por debajo del umbral"
```

### 5.2 Umbrales mínimos de rendimiento

Los umbrales mínimos no deben fijarse arbitrariamente: deben derivar de los requisitos de negocio y del rendimiento histórico del modelo en producción. Una práctica habitual es definir el umbral como un porcentaje de la métrica del modelo actual en producción (por ejemplo, el nuevo modelo debe obtener al menos el 98 % del AUC del modelo actual). Esto asegura que ninguna actualización supone una regresión significativa aunque el modelo nuevo no sea necesariamente mejor en todas las métricas.

### 5.3 Smoke tests post-actualización

Tras el despliegue, antes de declarar la actualización exitosa, se ejecuta un conjunto reducido de pruebas de humo (smoke tests) que verifican que el servicio responde correctamente a peticiones reales:

- El endpoint de salud responde con HTTP 200.
- Una petición de inferencia con un ejemplo conocido devuelve una respuesta en el rango esperado.
- La latencia de respuesta está dentro del SLA.
- No hay errores en los logs de aplicación durante los primeros minutos.

Estos tests deben ejecutarse automáticamente como parte del pipeline de CD y deben bloquear la finalización del despliegue si fallan.

### 5.4 Shadow mode

El shadow mode (o shadow deployment) es una técnica que permite validar el nuevo modelo con tráfico de producción real sin que sus predicciones tengan ningún impacto en los usuarios. El tráfico de producción se duplica: la copia original sigue siendo procesada por el modelo en producción, mientras que la copia sombra es procesada por el nuevo modelo. Las predicciones del modelo sombra se registran y se comparan con las del modelo de producción, pero no se devuelven al usuario ni se usan en ninguna decisión.

Esto permite detectar distribuciones de predicción anómalas, problemas de latencia o errores de inferencia en el nuevo modelo antes de exponerlo a usuarios reales. El shadow mode es especialmente valioso cuando el conjunto de datos de holdout no representa bien la distribución real del tráfico de producción, o cuando hay patrones estacionales que el conjunto de test no captura.

---

## 6. Procedimientos de rollback

### 6.1 Rollback automático con Kubernetes

Kubernetes puede detectar automáticamente cuando un despliegue está fallando si las readiness probes o liveness probes de los nuevos pods no responden correctamente. Sin embargo, Kubernetes por sí solo no hace rollback automático: simplemente detiene el avance del rolling update y mantiene el sistema en un estado degradado.

Para implementar rollback automático es necesario añadir lógica de monitorización externa. Una solución habitual es usar Argo Rollouts, que extiende Kubernetes con un CRD `Rollout` capaz de analizar métricas de Prometheus y revertir automáticamente el despliegue si los valores superan los umbrales de error definidos. Otra solución es implementar un operador propio que monitorice el error rate del servicio y ejecute `kubectl rollout undo` si supera un umbral durante un período de tiempo sostenido.

### 6.2 Rollback manual de modelo

El comando para revertir un despliegue de Kubernetes al estado anterior es:

```bash
kubectl rollout undo deployment/modelo-inferencia -n produccion
```

Kubernetes mantiene un historial de revisiones del Deployment (configurable con `revisionHistoryLimit`). Para revertir a una revisión específica:

```bash
# Ver historial de revisiones
kubectl rollout history deployment/modelo-inferencia -n produccion

# Revertir a una revisión específica
kubectl rollout undo deployment/modelo-inferencia --to-revision=3 -n produccion

# Verificar el estado del rollout
kubectl rollout status deployment/modelo-inferencia -n produccion
```

Para el rollback del artefacto del modelo en MLflow, el proceso es diferente: consiste en actualizar el stage del modelo en el registry para que la versión anterior vuelva a estar en `Production`, y en disparar el pipeline de despliegue que toma el modelo de `Production` y lo despliega.

### 6.3 Criterios de decisión de rollback

Los criterios de rollback deben estar definidos antes del despliegue, no durante el incidente. Las categorías principales son:

**Error rate**: si el porcentaje de peticiones que devuelven error 5xx supera el umbral (por ejemplo, 1 % durante más de 2 minutos), se activa el rollback.

**Latencia degradada**: si el percentil 99 de latencia supera el SLA definido (por ejemplo, p99 > 500 ms cuando el baseline era p99 < 200 ms), se activa el rollback.

**Alertas de métricas de modelo**: si los dashboards de monitorización de modelo detectan una deriva significativa en la distribución de predicciones (por ejemplo, la proporción de predicciones positivas cae un 40 % respecto al baseline), se activa el rollback. Esto requiere que el sistema de monitorización de modelo esté operativo y que las alertas estén configuradas previamente.

**Fallo de smoke tests**: si los smoke tests post-despliegue fallan, el rollback es inmediato y automático.

### 6.4 Tiempo objetivo de recuperación (RTO)

El Recovery Time Objective (RTO) define el tiempo máximo aceptable entre la detección de un problema y la restauración del servicio. En sistemas de IA críticos, el RTO suele estar entre 5 y 15 minutos. Para cumplirlo, el proceso de rollback debe estar automatizado en la medida de lo posible, y los responsables de operaciones deben tener los permisos y el conocimiento necesarios para ejecutarlo sin necesidad de escalado.

El RTO debe ser un input del diseño del sistema, no una variable dependiente. Si el RTO es de 5 minutos, la estrategia blue-green es la única que puede garantizarlo de forma consistente.

---

## 7. Gestión de dependencias en actualizaciones

### 7.1 Actualización de CUDA/cuDNN en sistemas en producción

CUDA y cuDNN son la base de la inferencia en GPU. Actualizar estas librerías en un sistema en producción es una operación de alto riesgo porque una versión incompatible puede dejar el modelo sin capacidad de inferencia en GPU, degradando drásticamente la latencia o haciendo el servicio inoperable.

El procedimiento seguro para actualizar CUDA/cuDNN en producción incluye:

1. Verificar en la documentación oficial de PyTorch o TensorFlow la matriz de compatibilidad entre versiones de framework, CUDA y cuDNN.
2. Preparar una imagen de contenedor con la nueva versión de CUDA/cuDNN y la versión de framework correspondiente.
3. Ejecutar el pipeline completo de validación (unit tests, integration tests, regression tests) contra la nueva imagen en un entorno de staging con hardware GPU idéntico al de producción.
4. Validar la latencia de inferencia: una nueva versión de CUDA puede afectar al rendimiento en operaciones específicas.
5. Desplegar con estrategia canary (5-10 % del tráfico) antes de completar la migración.

Nunca actualizar CUDA directamente en el host de producción si los modelos corren en contenedores: la imagen de contenedor debe encapsular la versión de CUDA como dependencia explícita.

### 7.2 Actualización de librerías Python

Las librerías Python utilizadas en el pipeline de ML (scikit-learn, numpy, pandas, transformers) tienen un impacto directo sobre los modelos serializados. El problema central es que muchos formatos de serialización (pickle, joblib) son dependientes de la versión de la librería: un modelo serializado con scikit-learn 1.2 puede no deserializarse correctamente con scikit-learn 1.4 si hubo cambios internos en la representación de los objetos.

Estrategias para gestionar este riesgo:

- **Fijar las versiones exactas** de todas las dependencias en el archivo de requisitos del entorno de producción (`requirements.txt` o `environment.yml` con versiones pinneadas).
- **Incluir la versión de las librerías en los metadatos del artefacto del modelo** registrado en MLflow, de modo que sea posible saber exactamente con qué entorno fue entrenado y serializado.
- **Probar la deserialización** del artefacto con la nueva versión de la librería como parte del pipeline de validación, antes de cualquier despliegue.
- **Usar formatos de serialización más estables** cuando sea posible: ONNX para modelos de inferencia, o el formato nativo de TorchScript para modelos de PyTorch, son más resistentes a los cambios de versión que pickle.

### 7.3 Compatibilidad entre versión de framework y modelos guardados

PyTorch y TensorFlow mantienen políticas de compatibilidad entre versiones para los formatos de checkpoint y modelo guardado, pero estas garantías tienen límites. Los modelos de PyTorch guardados con `torch.save` en formato pickle heredan los problemas de compatibilidad de pickle. Los modelos exportados como TorchScript o a ONNX son más portables.

Para TensorFlow/Keras, el formato SavedModel es el más robusto y tiene mejor compatibilidad entre versiones menores, pero puede presentar problemas en actualizaciones MAJOR del framework.

La estrategia recomendada es:

- Mantener en el Model Registry no solo el artefacto del modelo sino también el entorno completo de inferencia (imagen Docker) con el que fue validado.
- Al actualizar el framework, re-exportar y re-validar todos los modelos en producción antes del despliegue, no solo el modelo que se está actualizando.

### 7.4 Pruebas de compatibilidad automatizadas

Para detectar problemas de compatibilidad de forma preventiva, se pueden ejecutar pruebas automatizadas nocturnas que cargan los artefactos de todos los modelos en producción en el entorno con las nuevas versiones de dependencias candidatas y verifican que la inferencia produce resultados dentro del margen esperado. Si alguna prueba falla, se genera una alerta antes de que el equipo intente un despliegue con esa combinación de versiones.

---

## 8. Comunicación de cambios

### 8.1 Changelog estructurado (Keep a Changelog)

El estándar Keep a Changelog (keepachangelog.com) define una estructura de changelog legible por humanos que distingue entre tipos de cambio: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. Para sistemas de IA se añaden categorías específicas: `Model`, `Breaking`, `Performance`.

Ejemplo de entrada de changelog para una actualización de modelo:

```markdown
## [2.1.0] - 2026-06-23

### Model
- Reentrenamiento del modelo de clasificación de fraude con datos Q1 2026.
- AUC en holdout: 0.9342 (anterior: 0.9187, mejora de +1.69 %).

### Changed
- Umbral de clasificación ajustado de 0.50 a 0.47 para reducir falsos negativos.

### Performance
- Latencia p99 reducida de 210 ms a 185 ms tras optimización del preprocesado.

### Fixed
- Corrección en el manejo de valores nulos en el campo `monto_transaccion`.
```

### 8.2 Notificaciones a stakeholders

Las actualizaciones de sistemas de IA en producción afectan a múltiples partes interesadas: equipos de producto que consumen las predicciones, equipos de negocio que toman decisiones basadas en ellas, equipos de auditoría y compliance en entornos regulados, y los propios equipos de ingeniería que integran la API del modelo.

Un protocolo de notificación mínimo incluye:

- **Anuncio previo**: al menos 48-72 horas antes, con descripción del cambio, la ventana de mantenimiento (si aplica) y el contacto responsable.
- **Confirmación de inicio**: mensaje en el canal de comunicación del equipo cuando comienza el despliegue.
- **Confirmación de éxito o rollback**: mensaje inmediatamente tras la finalización, indicando si el despliegue fue exitoso o si se activó el rollback y el motivo.
- **Informe post-mortem**: en caso de incidencia durante el despliegue, un informe estructurado en las 24-48 horas siguientes con análisis de causa raíz y acciones correctivas.

### 8.3 Documentación de breaking changes

Los cambios que rompen la compatibilidad de la API requieren un tratamiento especial. Un breaking change debe:

- Estar documentado con precisión: qué campo o comportamiento cambia, cuál es el valor antiguo, cuál es el nuevo, y por qué se hace el cambio.
- Incluir un ejemplo de migración: código antes y después para que los equipos consumidores puedan adaptar su integración.
- Ser comunicado con suficiente antelación para que los equipos afectados puedan planificar su trabajo de migración.

### 8.4 Período de deprecación y migración de clientes

Un cambio MAJOR nunca debe aplicarse de forma abrupta en producción. El protocolo estándar es:

1. Lanzar la nueva versión MAJOR de la API del modelo (v2) manteniendo la versión anterior (v1) operativa en paralelo.
2. Anunciar la deprecación de v1 con una fecha de fin de soporte, tipicamente con 3-6 meses de antelación.
3. Durante el período de deprecación, monitorizar qué clientes siguen usando v1 y contactarlos proactivamente para apoyar su migración.
4. En la fecha de fin de soporte, retirar v1. Si algún cliente crítico no ha migrado, evaluar una extensión puntual del período.

En sistemas internos donde el equipo controla todos los consumidores, el período de deprecación puede ser más corto, pero sigue siendo necesario para coordinar los cambios entre equipos.

---

## 9. Actividades prácticas

### Actividad 1 — Configuración de un rolling update con validación automática

**Contexto**: disponéis de un clúster Kubernetes local (minikube o kind) y un servicio de inferencia simple basado en FastAPI que sirve un modelo de clasificación cargado desde un archivo.

**Tarea**: Configura un `Deployment` de Kubernetes con 3 réplicas, una estrategia de rolling update con `maxSurge: 1` y `maxUnavailable: 0`, y una readiness probe que verifique el endpoint `/health`. Despliega una primera versión (v1) del servicio. Modifica la imagen a v2 (puedes simular el cambio con un tag diferente) y ejecuta el update con `kubectl set image`. Monitoriza el proceso con `kubectl rollout status` y `kubectl get pods -w`. Documenta qué ocurre si la readiness probe de los nuevos pods falla deliberadamente (puedes modificar el endpoint para que devuelva 503).

**Entregable**: capturas del proceso de rolling update y del comportamiento cuando la readiness probe falla, con una explicación de qué hace Kubernetes en cada caso.

---

### Actividad 2 — Registro y promoción de versiones con MLflow

**Contexto**: tienes acceso a un servidor MLflow local y un script de entrenamiento de un modelo de clasificación binaria con scikit-learn.

**Tarea**: Entrena dos versiones del modelo con diferentes hiperparámetros. Registra ambas en MLflow con versionado semántico (v1.0.0 y v1.1.0, siendo la segunda una mejora de hiperparámetros sin cambio de interfaz). Usa la API de MLflow para promover la versión con mejores métricas a `Production` y archivar la anterior. Implementa un script que consulte el Model Registry y cargue automáticamente el modelo en stage `Production` para hacer inferencia.

**Entregable**: código del script de entrenamiento con logging de MLflow, código del script de promoción, y capturas de la interfaz de MLflow mostrando las versiones y sus stages.

---

### Actividad 3 — Pipeline de validación pre-despliegue

**Contexto**: tienes un modelo en producción (v1) y un candidato a despliegue (v2). Dispones de un conjunto de datos de holdout con las etiquetas correctas.

**Tarea**: Implementa un pipeline de validación en Python que: (1) ejecute unit tests sobre las funciones de preprocesado, (2) ejecute integration tests cargando el artefacto serializado del modelo v2 y verificando que produce predicciones para ejemplos conocidos, (3) calcule las métricas del modelo v2 en el conjunto holdout y verifique que AUC >= 0.98 * AUC(v1), precision >= umbral y recall >= umbral. El pipeline debe devolver exit code 0 si todos los tests pasan y exit code 1 si alguno falla, de modo que pueda integrarse en un pipeline de CI/CD (GitHub Actions o similar).

**Entregable**: código del pipeline de validación con los tres niveles de tests y un archivo de configuración de CI/CD que lo ejecute.

---

### Actividad 4 — Simulación de rollback y análisis post-incidente

**Contexto**: se simula un despliegue fallido en el que el nuevo modelo produce un aumento significativo del error rate detectado por los smoke tests.

**Tarea**: a partir de un escenario proporcionado (logs de un despliegue fallido, métricas de Prometheus exportadas como CSV, y el historial de revisiones del Deployment), realiza las siguientes acciones: (1) identifica el momento exacto en que los criterios de rollback se superaron, (2) ejecuta el comando de rollback apropiado, (3) verifica que el servicio se ha restaurado correctamente, (4) redacta un informe post-mortem siguiendo la estructura: resumen ejecutivo, línea de tiempo, causa raíz, impacto, acciones correctivas y lecciones aprendidas.

**Entregable**: el informe post-mortem completo y los comandos ejecutados con su salida.

---

## 10. Referencias

- **Kubernetes — Rolling Updates**. Documentación oficial de Kubernetes sobre estrategias de despliegue, configuración de `maxSurge` y `maxUnavailable`, y gestión del historial de revisiones. https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#rolling-update-deployment

- **Kubernetes — Canary Deployments**. Guía de la documentación oficial sobre implementación de despliegues canary con Kubernetes. https://kubernetes.io/docs/concepts/cluster-administration/manage-deployment/#canary-deployments

- **Humble, J. & Farley, D. (2010). *Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation***. Addison-Wesley Professional. Referencia fundamental para los conceptos de pipeline de despliegue, estrategias de actualización sin downtime y gestión del riesgo en despliegues. ISBN: 978-0321601919.

- **MLflow — Model Registry**. Documentación oficial de MLflow sobre registro de modelos, transiciones de stage, y API de gestión de versiones. https://mlflow.org/docs/latest/model-registry.html

- **MLflow — Models**. Documentación sobre formatos de modelo soportados, serialización y carga de artefactos. https://mlflow.org/docs/latest/models.html

- **Beyer, B., Jones, C., Petoff, J. & Murphy, R. (2016). *Site Reliability Engineering: How Google Runs Production Systems***. O'Reilly Media. Capítulos 17 (Testing for Reliability) y 27 (Reliable Product Launches at Scale) son especialmente relevantes para los procedimientos de rollback y criterios de decisión. Disponible en línea: https://sre.google/sre-book/table-of-contents/

- **Istio — Traffic Management**. Documentación oficial de Istio sobre `VirtualService` y `DestinationRule` para implementar despliegues canary con control de peso de tráfico. https://istio.io/latest/docs/concepts/traffic-management/

- **Argo Rollouts**. Documentación del controlador de Kubernetes para despliegues progresivos con análisis automático de métricas. https://argoproj.github.io/argo-rollouts/

- **Keep a Changelog**. Estándar para la redacción de changelogs legibles por humanos y máquinas. https://keepachangelog.com/es/1.1.0/

- **Semantic Versioning 2.0.0**. Especificación de versionado semántico, aplicable a modelos de ML con las adaptaciones descritas en esta unidad. https://semver.org/lang/es/
