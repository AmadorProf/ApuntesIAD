# UD1 · Preparación del despliegue de sistemas de IA

---

## 1. Introducción — del prototipo al sistema productivo

Cualquier persona que haya trabajado en un proyecto de machine learning conoce bien la brecha que separa un modelo que "funciona en local" de un sistema que opera en producción de manera fiable, escalable y mantenible. Esta brecha es más profunda de lo que aparenta. Un prototipo en un cuaderno Jupyter puede alcanzar una precisión del 94 % en el conjunto de validación, ejecutarse en segundos en un GPU compartido y ser celebrado como un éxito del equipo de ciencia de datos. Pero ese mismo modelo, trasladado sin preparación a un entorno de producción, puede fallar en la primera semana por una dependencia rota, por datos de entrada inesperados, por latencia excesiva bajo carga concurrente o simplemente porque nadie documentó cómo volver atrás si algo sale mal.

El despliegue de sistemas de inteligencia artificial es una disciplina en sí misma, distinta del entrenamiento del modelo y de la ingeniería de software tradicional. Combina conocimientos de MLOps, ingeniería de sistemas, seguridad, observabilidad y gestión de configuración. No es un paso final ni una tarea menor: es el punto donde el trabajo técnico se convierte en valor real para una organización o usuario.

Esta unidad didáctica aborda la fase previa al despliegue: todo lo que debe ocurrir antes de que el primer request de producción llegue al modelo. Trabajaremos de manera sistemática los conceptos de empaquetado, configuración, testing y documentación que hacen posible un despliegue controlado, reproducible y reversible. El objetivo no es cubrir todos los casos posibles, sino construir un marco mental y un conjunto de herramientas concretas que el alumno pueda aplicar en contextos reales.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el alumno será capaz de:

- Identificar y evaluar los requisitos no funcionales críticos de un sistema de IA antes de su despliegue (latencia, throughput, disponibilidad, costo).
- Seleccionar el formato de serialización de modelo más adecuado según el contexto de despliegue (pickle, joblib, ONNX, TorchScript, SavedModel).
- Convertir un modelo PyTorch a formato ONNX y ejecutar inferencia con `onnxruntime`.
- Implementar una estrategia de gestión de configuración que separe código, configuración y secretos usando Pydantic Settings.
- Diseñar y ejecutar una batería de tests pre-despliegue: unit tests, integration tests, contract tests y load tests.
- Redactar un runbook de despliegue completo y una model card siguiendo el formato de Google.
- Comprender el rol de las Architecture Decision Records (ADRs) en la trazabilidad de decisiones técnicas.

---

## 3. Checklist de preparación pre-despliegue

La preparación pre-despliegue es el conjunto de validaciones, decisiones y configuraciones que deben completarse antes de enviar tráfico real a un sistema. Trabajar con una checklist estructurada reduce la probabilidad de incidentes y facilita la revisión entre pares.

### 3.1 Evaluación de requisitos no funcionales

Los requisitos no funcionales de un sistema de IA determinan si el modelo entrenado es apto para producción, independientemente de su precisión. Los más relevantes son:

**Latencia.** La latencia mide el tiempo que transcurre entre que el sistema recibe una petición y devuelve una respuesta. En producción no basta con medir la media: es imprescindible trabajar con percentiles. El p50 (mediana) indica la experiencia del usuario típico; el p95 y el p99 capturan los casos extremos que afectan a los usuarios más sensibles a la lentitud. Un modelo con latencia p50 de 30 ms pero p99 de 4 segundos tiene un problema estructural que no se ve en la media. Los SLAs de latencia deben definirse antes del despliegue y acordarse con el equipo de producto o cliente.

**Throughput.** El throughput se mide en requests por segundo (RPS) que el sistema puede atender manteniendo la latencia dentro de los límites acordados. Para estimarlo hay que combinar el tiempo de inferencia por request, el nivel de paralelismo disponible (número de réplicas, hilos, tamaño de batch) y el comportamiento bajo carga sostenida frente a picos. Herramientas como k6 o Locust permiten modelar patrones de carga realistas durante la fase de testing.

**Disponibilidad y SLO.** El Service Level Objective (SLO) de disponibilidad expresa el porcentaje de tiempo que el sistema debe estar operativo. Un SLO del 99,9 % permite aproximadamente 8,7 horas de indisponibilidad al año; el 99,99 % baja a 52 minutos. Fijar el SLO antes del despliegue obliga a diseñar mecanismos de recuperación, reinicios automáticos, health checks y estrategias de failover proporcionales al objetivo.

**Costo por inferencia.** En sistemas de IA el costo de cómputo puede ser significativo, especialmente con modelos grandes o cargas altas. Es necesario estimar el costo por request (GPU/hora, CPU/hora, memoria) y contrastarlo con el valor de negocio generado. Este análisis puede influir en decisiones de optimización (cuantización, destilación, caching de resultados) antes de llegar a producción.

### 3.2 Validación del modelo para producción

**Reproducibilidad.** El modelo que llega a producción debe ser exactamente el mismo que superó la evaluación. Esto implica fijar semillas aleatorias, versionar el código de entrenamiento, versionar los datos de entrenamiento y registrar el modelo con sus metadatos en un modelo registry (MLflow, Weights & Biases, o similar). Si el modelo no puede reproducirse a partir del código y los datos registrados, no está listo para producción.

**Tests de regresión.** Antes de desplegar una nueva versión de un modelo es necesario comparar su comportamiento con la versión anterior sobre un conjunto de datos de referencia. Los tests de regresión verifican que las métricas clave (precisión, recall, F1, RMSE según el caso) no han empeorado por encima de un umbral definido. También se deben incluir tests sobre subgrupos de datos (por segmento demográfico, por tipo de input) para detectar regresiones parciales que no se verían en la métrica global.

**Comparación con baseline.** Todo modelo en producción debe superar al menos un baseline simple: un modelo de reglas, la predicción de la clase mayoritaria, la media histórica, o la versión actual en producción. Si el nuevo modelo no supera el baseline en las métricas de negocio acordadas, el despliegue debe posponerse.

### 3.3 Preparación del entorno

**Dependencias fijadas.** Las dependencias del sistema (librerías Python, versiones de CUDA, drivers de GPU) deben estar completamente fijadas en un archivo de requisitos (`requirements.txt`, `pyproject.toml`) o en la imagen Docker. Una dependencia que se actualiza automáticamente puede romper el sistema silenciosamente.

**Secrets gestionados.** Las credenciales (claves de API, contraseñas de base de datos, certificados) nunca deben estar en el código ni en variables de entorno sin gestión. Deben almacenarse en un sistema dedicado (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault) e inyectarse en tiempo de ejecución.

**Configuración externalizada.** Los parámetros que pueden cambiar entre entornos (URLs de servicios dependientes, umbrales de confianza, tamaño de batch) deben vivir fuera del código, en archivos de configuración o variables de entorno, siguiendo el principio III de The Twelve-Factor App.

### 3.4 Revisión de seguridad básica

**Superficie de ataque del endpoint.** Cualquier endpoint de inferencia expuesto es una superficie de ataque potencial. Es necesario revisar qué información devuelve en caso de error (los mensajes de error detallados pueden revelar estructura interna), qué tipos de input acepta y cómo los valida, y qué ocurre ante inputs malformados o adversariales.

**Autenticación.** El endpoint debe requerir autenticación para cualquier uso en producción. Los mecanismos más comunes son API keys, tokens JWT o autenticación mutual TLS. La autenticación debe aplicarse en la capa de infraestructura (API gateway, ingress controller) además de, opcionalmente, en la aplicación.

**Rate limiting.** Sin rate limiting, un endpoint de inferencia puede ser inundado por peticiones accidentales o maliciosas, generando costos inesperados o denegación de servicio. El rate limiting debe configurarse a nivel de cliente o IP, con límites razonables para el caso de uso previsto.

---

## 4. Empaquetado del modelo

El empaquetado consiste en serializar el modelo entrenado a un formato que pueda ser cargado y ejecutado en el entorno de producción de manera eficiente y reproducible.

### 4.1 Formatos de serialización

**Pickle.** El formato nativo de Python para serialización de objetos. Es simple y universal para objetos Python, pero tiene serias limitaciones: no es seguro frente a archivos maliciosos (ejecuta código arbitrario al deserializar), está atado a versiones específicas de Python y de las librerías usadas, y no es portable entre frameworks. Debe evitarse para modelos en producción salvo casos muy controlados.

**Joblib.** Alternativa a pickle optimizada para objetos NumPy y scikit-learn. Ofrece mejor rendimiento en arrays grandes gracias a compresión eficiente. Comparte las limitaciones de seguridad de pickle. Es aceptable para modelos scikit-learn en entornos controlados, pero no para modelos de deep learning complejos.

**ONNX (Open Neural Network Exchange).** Formato abierto diseñado para interoperabilidad entre frameworks. Un modelo entrenado en PyTorch puede convertirse a ONNX y ejecutarse con `onnxruntime` en CPU o GPU, en Python, C++, Java o .NET, sin depender de PyTorch en producción. Esto reduce el tamaño de la imagen de despliegue, mejora la velocidad de inferencia y desacopla el entorno de producción del entorno de entrenamiento.

**TorchScript.** Subconjunto serializable de Python de PyTorch. Permite exportar modelos PyTorch a un formato que puede ejecutarse sin el intérprete Python completo (en C++ via `libtorch`). Es más adecuado que ONNX cuando se necesita soporte completo de las APIs de PyTorch que ONNX no cubre bien.

**SavedModel (TensorFlow).** Formato nativo de TensorFlow/Keras. Incluye la arquitectura, los pesos y las firmas de las funciones de inferencia. Es el formato recomendado para desplegar modelos TensorFlow en TF Serving, TF Lite o TF.js.

### 4.2 Cuándo usar ONNX

ONNX es la opción preferida cuando:
- Se necesita desplegar en un runtime diferente al usado para entrenar (por ejemplo, entrenar en PyTorch, desplegar en un servicio que usa `onnxruntime` optimizado).
- Se quiere reducir las dependencias en producción (eliminar PyTorch de la imagen).
- Se necesita compatibilidad con hardware específico (ONNX Runtime tiene backends optimizados para Intel OpenVINO, NVIDIA TensorRT, ARM, etc.).
- Se requiere portabilidad entre plataformas (edge, móvil, servidor).

ONNX no es adecuado cuando el modelo usa operaciones personalizadas que no tienen equivalente en el estándar ONNX, o cuando se necesitan características dinámicas avanzadas de PyTorch que no se traducen bien al grafo estático de ONNX.

### 4.3 Conversión de PyTorch a ONNX

El proceso completo de conversión incluye exportación, verificación e inferencia.

**Exportación con `torch.onnx.export`.**

```python
import torch
import torch.onnx

# Cargar el modelo entrenado
model = MiModelo()
model.load_state_dict(torch.load("modelo.pt"))
model.eval()

# Input de ejemplo con las dimensiones correctas
dummy_input = torch.randn(1, 3, 224, 224)

# Exportar a ONNX
torch.onnx.export(
    model,
    dummy_input,
    "modelo.onnx",
    export_params=True,        # incluir pesos en el archivo
    opset_version=17,          # versión del opset ONNX
    do_constant_folding=True,  # optimización: plegar constantes
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={
        "input": {0: "batch_size"},    # batch dinámico
        "output": {0: "batch_size"},
    },
)
```

**Verificación con `onnx.checker`.**

```python
import onnx

modelo_onnx = onnx.load("modelo.onnx")
onnx.checker.check_model(modelo_onnx)
print("Modelo ONNX verificado correctamente.")
```

**Inferencia con `onnxruntime`.**

```python
import onnxruntime as ort
import numpy as np

sesion = ort.InferenceSession("modelo.onnx")
nombre_entrada = sesion.get_inputs()[0].name

input_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
resultado = sesion.run(None, {nombre_entrada: input_data})
print(resultado[0].shape)
```

Es recomendable comparar numéricamente la salida del modelo PyTorch original con la salida del modelo ONNX sobre los mismos inputs para detectar diferencias de precisión numérica.

### 4.4 TorchScript: `torch.jit.script` vs `torch.jit.trace`

TorchScript ofrece dos mecanismos de exportación con características distintas:

**`torch.jit.trace`** ejecuta el modelo con un input de ejemplo y registra las operaciones realizadas. Es simple y funciona bien con modelos que no tienen flujo de control condicional dependiente del input. Si el modelo tiene ramas `if/else` que dependen del valor del tensor, `trace` solo captura la rama ejecutada con el input de ejemplo.

**`torch.jit.script`** analiza el código Python del modelo y lo compila directamente a TorchScript. Soporta flujo de control dinámico, pero requiere que el código sea compatible con el subconjunto de Python que TorchScript entiende (sin algunas construcciones dinámicas de Python).

```python
# Con trace
traced_model = torch.jit.trace(model, dummy_input)
traced_model.save("modelo_traced.pt")

# Con script
scripted_model = torch.jit.script(model)
scripted_model.save("modelo_scripted.pt")

# Cargar y usar
loaded_model = torch.jit.load("modelo_scripted.pt")
output = loaded_model(dummy_input)
```

### 4.5 Model cards

Una model card es un documento que acompaña al modelo y describe sus características, limitaciones y consideraciones de uso. Es esencial para la gobernanza responsable de sistemas de IA.

Los campos que debe documentar una model card son:

- **Descripción del modelo:** arquitectura, framework, fecha de entrenamiento, autor.
- **Uso previsto (intended use):** para qué tareas fue diseñado, qué usuarios o sistemas lo utilizarán.
- **Usos fuera de alcance:** para qué no debe utilizarse.
- **Datos de evaluación:** conjuntos de datos usados para evaluar, características demográficas si aplica.
- **Métricas de rendimiento:** métricas globales y por subgrupos.
- **Limitaciones:** condiciones en que el modelo puede fallar o comportarse de manera inesperada.
- **Consideraciones éticas:** sesgos conocidos, riesgos de uso indebido, impacto potencial en grupos vulnerables.
- **Información de contacto y mantenimiento.**

---

## 5. Gestión de configuración para despliegue

### 5.1 Separación de código y configuración

El factor III de The Twelve-Factor App establece que la configuración es todo lo que varía entre despliegues (desarrollo, staging, producción) y debe estar completamente separada del código. El código de la aplicación debe poder publicarse como open source sin exponer ningún secreto ni configuración específica de entorno.

Este principio tiene implicaciones prácticas directas: si un parámetro (un umbral, una URL, un tamaño de batch) aparece hardcoded en el código fuente, en el momento en que necesite cambiarse entre entornos habrá que modificar el código, lo que rompe la reproducibilidad y aumenta el riesgo de errores.

### 5.2 Formatos de configuración

**Variables de entorno.** El mecanismo más simple y universal. Son independientes del lenguaje, fáciles de inyectar en contenedores Docker y soportadas nativamente por todos los orquestadores (Kubernetes, ECS, etc.). Su limitación es que solo soportan strings y no tienen estructura jerárquica nativa.

**YAML.** Formato legible para configuraciones con estructura jerárquica. Ampliamente usado en Kubernetes, GitHub Actions y frameworks ML. Es sensible a la indentación, lo que puede ser fuente de errores.

**TOML.** Alternativa a YAML con sintaxis más explícita y menos propensa a ambigüedades. Usado por defecto en `pyproject.toml` y adoptado por herramientas modernas de Python.

### 5.3 Pydantic Settings para validación de configuración

Pydantic Settings permite definir la configuración de la aplicación como un modelo tipado que se carga automáticamente desde variables de entorno o archivos `.env`, con validación en tiempo de inicio.

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class ConfiguracionDespliegue(BaseSettings):
    # Configuración del modelo
    ruta_modelo: str = Field(..., env="RUTA_MODELO")
    batch_size: int = Field(default=32, env="BATCH_SIZE")
    timeout_segundos: float = Field(default=5.0, env="TIMEOUT_SEGUNDOS")
    max_sequence_length: int = Field(default=512, env="MAX_SEQ_LENGTH")
    umbral_confianza: float = Field(default=0.7, ge=0.0, le=1.0)

    # Configuración de la API
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=4, ge=1)

    # Secrets (inyectados desde Vault o Secrets Manager)
    api_key: str = Field(..., env="API_KEY")
    db_password: str = Field(..., env="DB_PASSWORD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Al instanciar, Pydantic valida y lanza error si falta algo obligatorio
config = ConfiguracionDespliegue()
```

Si una variable obligatoria falta o un valor no supera la validación (por ejemplo, `umbral_confianza=1.5`), Pydantic lanza un `ValidationError` en el arranque de la aplicación, antes de que llegue cualquier request. Esto es preferible a descubrir el error durante la ejecución.

### 5.4 Configuración específica del modelo de inferencia

Los parámetros de inferencia deben externalizarse y documentarse:

- **Batch size:** número de inputs procesados simultáneamente. Afecta latencia y throughput.
- **Timeout:** tiempo máximo de espera para una inferencia antes de devolver error.
- **Max sequence length:** para modelos de texto, longitud máxima del input. Inputs más largos se truncan o rechazan.
- **Umbrales de confianza:** valor mínimo de probabilidad para considerar una predicción válida. Por debajo del umbral, el sistema puede devolver "no clasificado" o escalar a revisión humana.
- **Parámetros de negocio:** categorías habilitadas, reglas de postprocesamiento, mapeos de etiquetas.

### 5.5 Externalización de secrets

Los secrets nunca deben estar en el código, en archivos de configuración versionados ni en variables de entorno de la imagen Docker. Las opciones recomendadas son:

**HashiCorp Vault.** Sistema dedicado a la gestión de secrets con control de acceso granular, rotación automática y auditoría de accesos. Los secrets se inyectan en la aplicación en tiempo de ejecución mediante el agente de Vault o la API REST.

**AWS Secrets Manager.** Servicio gestionado de AWS para almacenamiento y rotación de secrets. Se integra nativamente con servicios como ECS, Lambda y EKS. Permite rotación automática de credenciales de base de datos.

En ambos casos, el código de la aplicación solo necesita permisos para leer el secret en tiempo de arranque; el secret en sí nunca toca el código fuente ni el sistema de control de versiones.

---

## 6. Testing antes del despliegue

### 6.1 La pirámide de tests aplicada a ML

La pirámide de tests en machine learning adapta el concepto clásico de software engineering:

**Base — Unit tests.** Prueban funciones individuales de manera aislada. En sistemas ML los candidatos naturales son:
- Funciones de preprocesamiento: tokenización, normalización, encoding de categóricas, manejo de valores nulos.
- Funciones de postprocesamiento: aplicación de umbrales, formateo de outputs, mapeo de etiquetas.
- Validadores de schema de input.

Los unit tests deben ser rápidos (milisegundos), deterministas y no requerir recursos externos.

**Nivel intermedio — Integration tests.** Prueban el pipeline completo con datos reales o realistas. Verifican que las piezas individuales funcionan juntas: que el preprocesamiento produce el formato que espera el modelo, que el modelo produce el formato que espera el postprocesamiento, y que el output final tiene el schema esperado.

**Nivel superior — Contract tests.** Verifican que el schema de inputs y outputs del servicio es estable. Si el servicio expone una API REST, los contract tests comprueban que los campos, tipos y restricciones del request y response no han cambiado de manera incompatible. Herramientas como Pact permiten contract testing entre servicios de manera automatizada.

**Cima — Load tests.** Verifican el comportamiento del sistema bajo carga. No se prueban casos individuales sino el rendimiento agregado: latencia bajo N usuarios concurrentes, comportamiento bajo picos, degradación progresiva ante sobrecarga.

### 6.2 Load testing con k6 y Locust

**k6** es una herramienta de load testing en JavaScript diseñada para DevOps. Los tests se definen como scripts que especifican el patrón de carga (usuarios virtuales, ramp-up, duración) y las validaciones (thresholds de latencia y tasa de error).

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },   // ramp-up a 50 usuarios
    { duration: '3m', target: 50 },   // carga sostenida
    { duration: '1m', target: 0 },    // ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // p95 < 500ms
    http_req_failed: ['rate<0.01'],    // < 1% errores
  },
};

export default function () {
  const payload = JSON.stringify({ texto: "Ejemplo de input para inferencia" });
  const params = { headers: { 'Content-Type': 'application/json' } };
  const res = http.post('http://localhost:8000/predict', payload, params);
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
```

**Locust** es la alternativa en Python, más adecuada cuando el equipo trabaja principalmente en Python y quiere reutilizar lógica de generación de datos de test.

```python
from locust import HttpUser, task, between

class UsuarioInferencia(HttpUser):
    wait_time = between(1, 3)

    @task
    def predecir(self):
        self.client.post(
            "/predict",
            json={"texto": "Ejemplo de input para inferencia"},
            headers={"Authorization": "Bearer test-token"},
        )
```

### 6.3 Smoke tests en staging

Antes de enviar tráfico de producción, el sistema debe superar un smoke test en un entorno de staging que replica la configuración de producción. Los smoke tests son una batería mínima que verifica:

- El servicio arranca correctamente y el health check devuelve 200.
- El endpoint de predicción acepta un input válido y devuelve un output con el schema correcto.
- El endpoint rechaza inputs inválidos con el código de error apropiado (400, 422).
- Los logs se generan en el formato esperado.
- Las métricas se exportan correctamente al sistema de monitorización.

### 6.4 Validación de la imagen Docker en ambiente similar a producción

La imagen Docker que se desplegará en producción debe validarse en un entorno equivalente antes del go-live:

- La imagen arranca sin errores y el modelo se carga correctamente.
- Los tiempos de arranque (tiempo hasta que el servicio está listo para atender requests) están dentro de los límites aceptables para el orquestador.
- El consumo de memoria en reposo no excede los límites definidos en el manifiesto de Kubernetes o la definición de tarea ECS.
- Las variables de entorno y secrets se inyectan correctamente.

### 6.5 Checklist de aceptación antes de go-live

Antes de autorizar el despliegue a producción debe completarse una checklist formal:

- [ ] Todos los unit tests pasan en CI.
- [ ] Integration tests pasan con datos de staging.
- [ ] Contract tests validan el schema actual.
- [ ] Load tests superan los thresholds de latencia y error rate.
- [ ] Smoke tests en staging completados sin errores.
- [ ] Imagen Docker validada en entorno similar a producción.
- [ ] Model card actualizada y revisada.
- [ ] Runbook de despliegue actualizado con la versión actual.
- [ ] Procedimiento de rollback probado y documentado.
- [ ] Alertas de monitorización configuradas para la nueva versión.
- [ ] Acceso de autenticación y rate limiting verificados.
- [ ] Responsable de guardia identificado para las primeras horas post-despliegue.

---

## 7. Documentación técnica de despliegue

La documentación no es un lujo ni una tarea para después: es parte integral del despliegue. Un sistema sin documentación adecuada no puede mantenerse, auditarse ni recuperarse de incidentes de manera eficiente.

### 7.1 Runbook de despliegue

Un runbook es una guía operativa paso a paso que permite a cualquier miembro del equipo técnico ejecutar el despliegue de manera segura, incluso bajo presión o en ausencia del autor original. Su estructura debe incluir:

**Prerrequisitos:** accesos necesarios, herramientas instaladas, versión del CLI de Kubernetes o AWS, credenciales verificadas.

**Pasos de despliegue con responsable y validación.** Cada paso debe indicar quién lo ejecuta, el comando exacto, qué resultado esperado indica éxito, y qué hacer si el resultado no es el esperado.

Ejemplo de un paso del runbook:

> **Paso 3: Actualizar la imagen en el despliegue de Kubernetes**
> Responsable: Ingeniero de operaciones
> Comando: `kubectl set image deployment/api-inferencia api=registro.ejemplo.com/modelo:v2.3.1 -n produccion`
> Validación: `kubectl rollout status deployment/api-inferencia -n produccion` devuelve "successfully rolled out" en menos de 5 minutos.
> Si falla: ejecutar el paso de rollback (ver sección 8) e informar al responsable de guardia.

**Procedimiento de rollback:** instrucciones exactas para volver a la versión anterior en el menor tiempo posible. Debe ser reversible, rápido y no depender de conocimiento no documentado.

**Contactos de escalado:** quién notificar y cómo en caso de incidente durante el despliegue.

### 7.2 Architecture Decision Records (ADRs)

Las Architecture Decision Records son documentos breves que registran decisiones técnicas significativas, el contexto en que se tomaron, las alternativas consideradas y las consecuencias esperadas. Son especialmente valiosas en sistemas de IA donde las decisiones de despliegue (formato de serialización, runtime de inferencia, estrategia de escalado) tienen implicaciones no obvias.

Un ADR típico incluye:

- **Título y número:** ADR-007: Uso de ONNX Runtime para inferencia en producción.
- **Estado:** propuesto / aceptado / deprecado / reemplazado por ADR-012.
- **Contexto:** descripción del problema o necesidad que motivó la decisión.
- **Decisión:** qué se decidió hacer.
- **Alternativas consideradas:** qué otras opciones se evaluaron y por qué se descartaron.
- **Consecuencias:** qué implica esta decisión a corto y largo plazo (ventajas, desventajas, deuda técnica asumida).

Los ADRs se almacenan en el repositorio del código, típicamente en un directorio `docs/adr/`, y se versionan junto al código que documentan.

### 7.3 Model card completa (formato Google)

El formato de model card de Google, propuesto por Mitchell et al. (2019), es el estándar de facto para documentar modelos de ML de manera responsable. Sus secciones principales son:

**Model Details:** información básica sobre el modelo (persona o equipo desarrollador, fecha, tipo de modelo, información de contacto, links a recursos adicionales).

**Intended Use:** casos de uso previstos, usuarios previstos, casos de uso fuera de alcance explícitamente declarados.

**Factors:** factores relevantes para la evaluación del modelo (grupos demográficos, condiciones de instrumentación, características del dominio).

**Metrics:** métricas de rendimiento elegidas y por qué son apropiadas para el caso de uso.

**Evaluation Data:** características del dataset de evaluación, motivación para su elección, preprocesamiento aplicado.

**Training Data:** descripción del dataset de entrenamiento en la medida en que puede compartirse.

**Quantitative Analyses:** resultados desagregados por los factores definidos anteriormente (rendimiento por subgrupo).

**Ethical Considerations:** descripción de los datos sensibles usados, riesgos identificados, medidas de mitigación.

**Caveats and Recommendations:** limitaciones conocidas, recomendaciones para usuarios del modelo.

### 7.4 Documentación de API con OpenAPI/Swagger desde FastAPI

FastAPI genera automáticamente documentación OpenAPI 3.0 a partir de los tipos y anotaciones del código Python. Sin escribir una línea adicional de documentación, FastAPI produce un endpoint `/docs` con interfaz Swagger UI y `/redoc` con ReDoc, navegables desde el navegador.

Para maximizar la calidad de la documentación autogenerada:

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="API de Inferencia — Clasificador de Texto",
    description="Servicio de inferencia para el modelo de clasificación v2.3",
    version="2.3.1",
)

class RequestPrediccion(BaseModel):
    texto: str = Field(..., min_length=1, max_length=512,
                       description="Texto a clasificar", example="El servicio fue excelente")
    idioma: str = Field(default="es", description="Código ISO 639-1 del idioma", example="es")

class ResponsePrediccion(BaseModel):
    etiqueta: str = Field(..., description="Clase predicha")
    confianza: float = Field(..., ge=0.0, le=1.0, description="Probabilidad de la clase predicha")
    latencia_ms: float = Field(..., description="Tiempo de inferencia en milisegundos")

@app.post("/predict", response_model=ResponsePrediccion,
          summary="Clasificar texto",
          description="Devuelve la clase más probable y su confianza para el texto dado.")
async def predecir(request: RequestPrediccion) -> ResponsePrediccion:
    ...
```

---

## 8. Actividades prácticas

**Actividad 1 — Evaluación de requisitos no funcionales.**
El alumno recibe un caso de uso ficticio (sistema de recomendación para una aplicación de e-commerce con 500 usuarios concurrentes en hora punta). Debe redactar un documento de requisitos no funcionales que incluya: SLO de latencia (p50, p95, p99) justificado, throughput objetivo en RPS, SLO de disponibilidad con cálculo de minutos de indisponibilidad permitidos al año, y estimación de costo por inferencia para tres tamaños de instancia distintos (CPU pequeña, CPU grande, GPU compartida). Se valorará la justificación de cada decisión en función del caso de uso.

**Actividad 2 — Empaquetado con ONNX.**
El alumno parte de un modelo PyTorch preentrenado (clasificador de imágenes ResNet-18 o clasificador de texto BERT tiny). Debe: exportarlo a formato ONNX con `torch.onnx.export` usando opset_version 17 y dimensiones de batch dinámicas; verificarlo con `onnx.checker`; ejecutar inferencia con `onnxruntime` sobre 5 inputs de ejemplo; comparar numéricamente los outputs del modelo PyTorch y del modelo ONNX para verificar equivalencia; medir la diferencia de latencia media entre ambos runtimes sobre 100 inferencias.

**Actividad 3 — Configuración con Pydantic Settings y gestión de secrets.**
El alumno debe implementar la configuración completa de un servicio de inferencia FastAPI usando Pydantic Settings. La configuración debe incluir: parámetros de modelo (ruta, batch size, timeout, umbral), parámetros de servidor (host, port, workers), y dos secrets (API key y URL de base de datos) que se cargan desde un archivo `.env` local (simulando en local lo que en producción vendría de Vault). Debe validarse que la aplicación falla con un error claro si falta un parámetro obligatorio, y que lanza error de validación si un valor está fuera de rango (por ejemplo, umbral mayor que 1.0).

**Actividad 4 — Runbook y model card.**
El alumno elige un modelo ficticio o real trabajado durante el curso y produce dos documentos: (a) un runbook de despliegue con al menos 8 pasos detallados, responsable, comando exacto, validación y procedimiento de rollback; (b) una model card completa siguiendo el formato de Google con todas las secciones. Ambos documentos se revisan entre pares en clase: cada alumno evalúa el runbook de un compañero intentando seguirlo sin preguntar nada, anotando los pasos ambiguos o incompletos.

---

## 9. Referencias

- Huyen, C. (2022). *Designing Machine Learning Systems*. O'Reilly Media. Capítulo 7: Model Deployment and Prediction Service. https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/

- Wiggins, A. (2011). *The Twelve-Factor App*. https://12factor.net — en especial Factor III (Config): https://12factor.net/config

- ONNX. *ONNX Documentation*. https://onnx.ai/onnx/intro/

- ONNX Runtime. *ONNX Runtime Documentation*. https://onnxruntime.ai/docs/

- PyTorch. *TorchScript — Introduction to TorchScript*. https://pytorch.org/docs/stable/jit.html

- PyTorch. *torch.onnx — ONNX Export*. https://pytorch.org/docs/stable/onnx.html

- Pydantic. *Pydantic Settings — Settings Management*. https://docs.pydantic.dev/latest/concepts/pydantic_settings/

- Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model Cards for Model Reporting. *Proceedings of the conference on fairness, accountability, and transparency*. https://dl.acm.org/doi/10.1145/3287560.3287596

- Grafana Labs. *k6 Documentation*. https://grafana.com/docs/k6/latest/

- Locust. *Locust Documentation*. https://docs.locust.io/en/stable/

- HashiCorp. *Vault Documentation*. https://developer.hashicorp.com/vault/docs

- AWS. *AWS Secrets Manager Documentation*. https://docs.aws.amazon.com/secretsmanager/

- Nygard, M. (2011). *Documenting Architecture Decisions*. https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions

- FastAPI. *FastAPI — OpenAPI*. https://fastapi.tiangolo.com/features/#automatic-docs

---

*Versión del documento: 1.0 — Junio 2026*
*Módulo: MP02 Despliegue de Sistemas de IA · CFS2 Instalación, despliegue y explotación de sistemas de IA*
