# UD5 · Protocolización y documentación técnica en sistemas ML

---

## 1. Introducción

La documentación es uno de los activos de ingeniería menos valorados y, al mismo tiempo, uno de los más costosos de descuidar. En proyectos de software tradicional ya se subestima su importancia; en sistemas de aprendizaje automático, donde la complejidad crece en múltiples dimensiones —datos, modelos, pipelines de entrenamiento, infraestructura de serving, deriva en producción—, la ausencia de documentación adecuada se convierte en un riesgo operativo real.

Cuando un equipo construye un sistema ML sin dejar rastro escrito de sus decisiones, sus procedimientos y sus interfaces, está acumulando lo que se conoce como **deuda técnica de documentación**. Este concepto, análogo a la deuda técnica de código, describe el coste diferido que se paga cuando alguien intenta incorporarse al proyecto, cuando hay que depurar un incidente de madrugada o cuando se necesita auditar por qué el modelo produce determinadas predicciones. La deuda se devuelve con intereses: horas de ingeniería dedicadas a reconstruir el contexto que nunca se escribió.

La documentación bien hecha no es un lujo ni una tarea para el final del sprint. Es una práctica de ingeniería de primera clase que se entrelaza con el desarrollo del sistema desde el primer día. Documentar una decisión de arquitectura cuando se toma cuesta minutos; reconstruirla seis meses después, cuando el ingeniero que la tomó ya no está en el equipo, puede costar días.

En el contexto específico de los sistemas ML, la documentación cumple además funciones que no existen en el software convencional:

- Registra las hipótesis sobre los datos y el comportamiento esperado del modelo, permitiendo detectar cuando la realidad diverge.
- Facilita la reproducibilidad de experimentos, que es un requisito tanto científico como regulatorio.
- Proporciona trazabilidad entre versiones de modelos, datasets y código, necesaria para cumplir con marcos regulatorios como el AI Act europeo.
- Reduce el tiempo de incorporación de nuevos miembros, que en proyectos ML es especialmente alto por la heterogeneidad de conocimientos requeridos.

Esta unidad cubre las herramientas y prácticas que permiten construir esa documentación de forma sistemática, mantenible y útil.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Comprender el papel de la documentación como componente de la deuda técnica y como activo de ingeniería.
- Crear y gestionar Architecture Decision Records (ADR) siguiendo el formato MADR, integrándolos en el flujo de trabajo con Git.
- Diseñar y documentar APIs REST de inferencia ML utilizando la especificación OpenAPI 3.1, con generación automática desde FastAPI.
- Escribir docstrings en estilo Google y NumPy con type hints correctos, y generar documentación de referencia con Sphinx o MkDocs.
- Redactar runbooks operativos para servicios de inferencia ML que permitan la respuesta eficaz ante incidencias.
- Estructurar wikis y bases de conocimiento para proyectos ML, aplicando el enfoque docs-as-code con herramientas como GitHub Pages y git-cliff.
- Aplicar estas prácticas de forma integrada en un proyecto ML real.

---

## 3. Architecture Decision Records (ADR)

### 3.1 Qué son y por qué importan

Un Architecture Decision Record (ADR) es un documento breve que captura una decisión arquitectónica significativa junto con su contexto y sus consecuencias. La clave está en la palabra "significativa": no toda decisión merece un ADR, sino aquellas que tienen impacto duradero en la estructura del sistema, que serían costosas de revertir o que no son evidentes a partir del código.

En sistemas ML, las decisiones que suelen merecer un ADR incluyen: la elección de framework de serving (TorchServe vs. Triton vs. BentoML), la estrategia de versionado de modelos, el formato de serialización (ONNX vs. pickle vs. SavedModel), la arquitectura de la pipeline de reentrenamiento o la decisión de usar feature stores.

El valor de los ADRs no está en el documento individual sino en el archivo acumulado. Cuando alguien se une al equipo o cuando hay que revisar una decisión, el historial de ADRs responde a la pregunta "¿por qué está hecho así?" con precisión y contexto, no con conjeturas.

### 3.2 Formato MADR (Markdown Architectural Decision Records)

MADR es una variante del formato original de Michael Nygard, optimizada para equipos modernos que trabajan con Markdown y Git. La estructura canónica es la siguiente:

**Título**: Imperativo corto que describe la decisión. Ej: "Usar Triton Inference Server como framework de serving".

**Estado**: Puede ser `propuesto`, `aceptado`, `rechazado`, `obsoleto` o `sustituido por [ADR-XXX]`. El estado evita que los ADRs antiguos se traten como decisiones vigentes.

**Contexto**: Describe la situación que hizo necesaria la decisión. Incluye las fuerzas en juego: requisitos técnicos, restricciones de equipo, limitaciones de tiempo o presupuesto, dependencias externas. Este apartado es neutral; no argumenta, describe.

**Decisión**: Enuncia claramente qué se decidió y, de forma breve, por qué. Es el núcleo del documento.

**Consecuencias**: Lista los efectos esperados de la decisión, tanto positivos como negativos. Incluye lo que se gana y lo que se pierde. Un ADR sin consecuencias negativas es sospechoso.

**Alternativas consideradas**: Describe las opciones que se evaluaron y no se eligieron, con una breve justificación de por qué se descartaron. Este apartado es fundamental: sin él, el lector futuro no puede entender el espacio de diseño que existía cuando se tomó la decisión.

### 3.3 Herramienta adr-tools

`adr-tools` es una utilidad de línea de comandos que automatiza la gestión del archivo de ADRs. Permite crear nuevos ADRs numerados secuencialmente, actualizar el estado de un ADR existente y generar una tabla de contenidos.

Instalación en macOS:

```bash
brew install adr-tools
```

Inicialización en un repositorio:

```bash
adr init doc/decisions
```

Creación de un nuevo ADR:

```bash
adr new "Usar Triton Inference Server como framework de serving"
```

Esto genera un archivo numerado como `doc/decisions/0003-usar-triton-inference-server-como-framework-de-serving.md` con la plantilla MADR lista para rellenar.

### 3.4 Ejemplo completo de ADR para elección de framework de serving ML

```markdown
# 0003 · Usar Triton Inference Server como framework de serving ML

- Estado: aceptado
- Fecha: 2026-06-10
- Autores: equipo de MLOps

## Contexto

El sistema necesita servir modelos de clasificación de imágenes entrenados en PyTorch.
Los requisitos de latencia son P99 < 50 ms para cargas de hasta 200 req/s con batch size 1.
El equipo de infraestructura ya gestiona clústeres con GPUs NVIDIA A100.
Necesitamos soporte nativo para el formato ONNX para facilitar la portabilidad entre frameworks.

## Decisión

Adoptamos NVIDIA Triton Inference Server como solución de serving.

Triton soporta de forma nativa los backends PyTorch (TorchScript), ONNX Runtime y TensorRT,
lo que nos permite optimizar el modelo en producción sin cambiar el proceso de entrenamiento.
Su protocolo KServe (v2) está en proceso de estandarización y reduce el lock-in con el proveedor.
El equipo de infraestructura tiene experiencia con el stack NVIDIA, lo que reduce el riesgo operativo.

## Consecuencias

Positivas:
- Soporte nativo de TensorRT para optimización de latencia en GPU.
- Protocolo estándar KServe compatible con otros sistemas del ecosistema.
- Dynamic batching y model ensembles disponibles sin desarrollo adicional.

Negativas:
- Añade dependencia del stack NVIDIA; no portable a entornos CPU-only sin ajustes.
- La configuración de los model repositories tiene una curva de aprendizaje inicial.
- El debugging de problemas en Triton es más complejo que en soluciones más simples.

## Alternativas consideradas

- **TorchServe**: más sencillo de operar, pero sin soporte nativo ONNX y con peor rendimiento
  en batching dinámico. Descartado por los requisitos de latencia.
- **BentoML**: excelente para prototipado y despliegue ágil, pero con menor madurez para
  cargas de producción a alta escala. Puede reconsiderarse para proyectos de menor criticidad.
- **FastAPI + modelo en proceso**: máxima flexibilidad pero sin batching ni gestión de múltiples
  modelos. Solo viable para prototipos.
```

### 3.5 Gestión del archivo de ADRs en Git

Los ADRs deben vivir en el mismo repositorio que el código, habitualmente en `doc/decisions/` o `docs/adr/`. Esto garantiza que la documentación evoluciona junto con el sistema y que los cambios en los ADRs quedan trazados en el historial de Git.

Algunas convenciones útiles:

- Los ADRs son inmutables una vez aceptados. Si una decisión se revierte, se crea un nuevo ADR que la supersede; el original queda con estado `obsoleto`.
- Los pull requests que introducen cambios arquitectónicos significativos deben ir acompañados del ADR correspondiente.
- Se puede usar una GitHub Action para verificar que el estado de los ADRs referenciados en PRs sea válido.

---

## 4. Documentación de APIs con OpenAPI

### 4.1 La especificación OpenAPI 3.1

OpenAPI (anteriormente Swagger) es el estándar de facto para describir APIs REST. La versión 3.1, alineada con JSON Schema 2020-12, permite describir con precisión las interfaces de los servicios de inferencia ML: los tipos de datos de entrada, los esquemas de respuesta, los códigos de error posibles y los mecanismos de autenticación.

Un documento OpenAPI se estructura en tres bloques principales:

**`info`**: Metadatos del API: título, versión, descripción, contacto. La versión del API (no del documento) es fundamental en servicios ML donde distintas versiones del modelo pueden estar activas simultáneamente.

**`paths`**: Define los endpoints disponibles, los métodos HTTP soportados, los parámetros de entrada y los esquemas de respuesta. Cada operación debe tener un `operationId` único y una descripción que explique la semántica, no solo la sintaxis.

**`components`**: Repositorio de esquemas reutilizables, definiciones de parámetros, respuestas de error comunes y esquemas de seguridad. Un API bien diseñado define sus tipos de datos una sola vez en `components` y los referencia desde `paths` usando `$ref`.

### 4.2 Generación automática con FastAPI

FastAPI genera la especificación OpenAPI automáticamente a partir de las anotaciones de tipo de Python y los modelos Pydantic. Esto elimina la sincronización manual entre código y documentación, que es la principal causa de documentación desactualizada.

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

app = FastAPI(
    title="Servicio de Clasificación de Imágenes",
    version="2.1.0",
    description="API de inferencia para modelos de clasificación. Acepta imágenes en base64.",
)

class PredictionRequest(BaseModel):
    image_base64: str = Field(
        ...,
        description="Imagen codificada en base64, formato JPEG o PNG, máximo 5 MB."
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Número de clases a devolver, ordenadas por probabilidad descendente."
    )

class Prediction(BaseModel):
    label: str = Field(..., description="Etiqueta de clase según ImageNet-1K.")
    score: float = Field(..., ge=0.0, le=1.0, description="Probabilidad normalizada.")

class PredictionResponse(BaseModel):
    predictions: List[Prediction]
    model_version: str = Field(..., description="Versión semántica del modelo usado.")
    latency_ms: float = Field(..., description="Tiempo de inferencia en milisegundos.")

@app.post(
    "/v2/classify",
    response_model=PredictionResponse,
    summary="Clasificación de imagen",
    tags=["inference"],
)
async def classify(request: PredictionRequest) -> PredictionResponse:
    """
    Clasifica una imagen y devuelve las top-K clases más probables.

    La imagen debe estar codificada en base64. El modelo está basado en
    ResNet-50 fine-tuneado sobre el dataset interno de producto.
    """
    ...
```

### 4.3 Swagger UI y ReDoc

FastAPI expone automáticamente dos interfaces de documentación interactiva:

- **Swagger UI** en `/docs`: permite explorar los endpoints y ejecutar peticiones de prueba directamente desde el navegador. Útil para desarrollo y depuración.
- **ReDoc** en `/redoc`: genera documentación de referencia navegable más adecuada para usuarios externos o para incluir en portales de desarrolladores.

La especificación en formato JSON está disponible en `/openapi.json`, lo que permite integrarla con herramientas de generación de clientes (openapi-generator) o de testing (Schemathesis).

### 4.4 Documentación de endpoints de predicción

Los endpoints de predicción en servicios ML tienen particularidades que conviene documentar explícitamente:

**Tipos de entrada**: El API debe especificar exactamente qué formatos acepta (base64, URL, multipart/form-data), las restricciones de tamaño, los formatos de imagen válidos y el rango de valores esperados para entradas numéricas.

**Respuestas de error**: Además de los errores HTTP estándar (400, 422, 500), los servicios ML tienen errores específicos: imagen demasiado pequeña para el modelo, clase de entrada fuera de distribución, timeout por carga en GPU, modelo no disponible por reentrenamiento en curso. Cada uno debe tener su propio código de error en el cuerpo de la respuesta y estar documentado en el esquema.

```python
class ErrorResponse(BaseModel):
    error_code: str = Field(..., description="Código interno. Ej: IMAGE_TOO_SMALL, MODEL_LOADING.")
    message: str
    detail: dict | None = None
```

**Versionado de la especificación**: Se recomienda incluir la versión del API en la URL (`/v1/`, `/v2/`) y mantener la especificación OpenAPI de cada versión en el repositorio bajo `docs/api/openapi-v1.yaml`, `docs/api/openapi-v2.yaml`. Los cambios de ruptura (breaking changes) deben incrementar el número de versión mayor.

---

## 5. Docstrings y type hints

### 5.1 PEP 257 y la importancia de la consistencia

PEP 257 define las convenciones para docstrings en Python. Su principio fundamental es que toda función, clase y módulo público debe tener un docstring. La consistencia de estilo dentro de un proyecto es más importante que qué estilo concreto se elija, porque permite que las herramientas de generación de documentación funcionen correctamente.

Los dos estilos más extendidos en proyectos de ciencia de datos y ML son el estilo Google y el estilo NumPy.

### 5.2 Estilo Google

El estilo Google es más compacto y se adapta bien a funciones con pocos parámetros. Es el recomendado por la guía de estilo de Google para Python y es el que genera mejor salida con mkdocstrings.

```python
def normalize_features(
    features: np.ndarray,
    mean: np.ndarray | None = None,
    std: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Normaliza las features aplicando estandarización z-score.

    Si se proporcionan media y desviación típica, se usan como parámetros
    de normalización (modo inferencia). Si no se proporcionan, se calculan
    a partir de los datos de entrada (modo entrenamiento).

    Args:
        features: Array de forma (n_samples, n_features) con los datos crudos.
        mean: Media por feature. Si es None, se calcula a partir de `features`.
        std: Desviación típica por feature. Si es None, se calcula a partir de `features`.
            Los valores cero se reemplazan por 1 para evitar división por cero.

    Returns:
        Una tupla (features_norm, mean, std) donde features_norm es el array
        normalizado y mean/std son los parámetros usados, útiles para aplicar
        la misma normalización a nuevos datos.

    Raises:
        ValueError: Si `features` tiene dimensiones distintas de 2.
        ValueError: Si `mean` o `std` tienen forma incompatible con `features`.

    Example:
        >>> X_train_norm, mu, sigma = normalize_features(X_train)
        >>> X_test_norm, _, _ = normalize_features(X_test, mean=mu, std=sigma)
    """
    if features.ndim != 2:
        raise ValueError(f"Se esperaba array 2D, se recibió {features.ndim}D.")
    if mean is None:
        mean = features.mean(axis=0)
    if std is None:
        std = features.std(axis=0)
        std[std == 0] = 1.0
    return (features - mean) / std, mean, std
```

### 5.3 Estilo NumPy

El estilo NumPy es más verboso y se adapta mejor a funciones con muchos parámetros y documentación extensa, como las que aparecen en librerías científicas. Es el estilo usado por NumPy, SciPy y scikit-learn.

```python
def compute_class_weights(
    y: np.ndarray,
    strategy: str = "balanced",
    custom_weights: dict[int, float] | None = None,
) -> dict[int, float]:
    """
    Calcula pesos por clase para tratar el desbalanceo en clasificación.

    Parameters
    ----------
    y : np.ndarray
        Array 1D de etiquetas enteras de clase.
    strategy : str, optional
        Estrategia de cálculo. "balanced" pondera inversamente proporcional
        a la frecuencia de clase. "sqrt" aplica la raíz cuadrada del peso
        balanceado para suavizar el efecto. Por defecto "balanced".
    custom_weights : dict[int, float] or None, optional
        Diccionario {clase: peso} que sobreescribe el cálculo automático
        para las clases especificadas. Por defecto None.

    Returns
    -------
    dict[int, float]
        Diccionario {clase: peso} normalizado de forma que la suma de pesos
        ponderada por frecuencia de clase sea igual a 1.

    Raises
    ------
    ValueError
        Si `strategy` no es "balanced" ni "sqrt".
    ValueError
        Si `y` contiene clases no representadas en `custom_weights` cuando
        este no es None y no cubre todas las clases.

    Notes
    -----
    Los pesos se normalizan respecto al número total de muestras y clases
    siguiendo la convención de scikit-learn [1]_.

    References
    ----------
    .. [1] scikit-learn: sklearn.utils.class_weight.compute_class_weight
    """
    ...
```

### 5.4 Type hints en Python

El módulo `typing` (y las anotaciones nativas desde Python 3.10+) permite expresar con precisión los tipos que una función acepta y devuelve. En sistemas ML, los type hints cumplen una función de documentación además de permitir el análisis estático con herramientas como mypy o pyright.

Tipos frecuentes en código ML:

```python
from typing import Literal, Callable, TypeAlias
import numpy as np

# Alias de tipo para mayor legibilidad
Features: TypeAlias = np.ndarray  # shape: (n_samples, n_features)
Labels: TypeAlias = np.ndarray    # shape: (n_samples,)

def train_model(
    X: Features,
    y: Labels,
    model_type: Literal["random_forest", "gradient_boosting", "mlp"],
    eval_metric: Callable[[Labels, Labels], float] = ...,
    n_jobs: int = -1,
) -> tuple[object, dict[str, float]]:
    ...
```

El uso de `Literal` para parámetros con un conjunto cerrado de valores válidos es especialmente útil: documenta los valores posibles directamente en la firma y permite que el IDE y el analizador estático detecten errores en el momento de escribir el código.

### 5.5 Generación de documentación con Sphinx y MkDocs

**Sphinx** es la herramienta tradicional del ecosistema Python, usada por NumPy, scikit-learn y la documentación oficial de Python. La extensión `autodoc` extrae los docstrings del código fuente y genera páginas RST o HTML. La extensión `sphinx-napoleon` permite usar los estilos Google y NumPy además del estilo RST nativo.

Configuración mínima en `conf.py`:

```python
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]
napoleon_google_docstring = True
napoleon_numpy_docstring = True
```

**MkDocs** con el plugin `mkdocstrings` es una alternativa más moderna y con mejor integración con Markdown. Es la elección recomendada para proyectos nuevos, especialmente si el resto de la documentación ya está en Markdown.

Configuración en `mkdocs.yml`:

```yaml
site_name: "Servicio de Clasificación"
plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
            show_source: true
            show_signature_annotations: true
```

### 5.6 Ejemplo de módulo bien documentado

Un módulo bien documentado incluye, en orden: docstring de módulo con descripción y ejemplo de uso, imports ordenados según PEP 8, constantes documentadas, clases y funciones con docstrings completos y type hints en todas las firmas públicas. El objetivo no es documentar lo que el código hace (eso lo dice el código), sino por qué lo hace, cuáles son sus precondiciones y qué garantiza como postcondición.

---

## 6. Runbooks y playbooks operativos

### 6.1 Diferencia entre runbook y playbook

Estos dos términos se usan a veces como sinónimos, pero conviene distinguirlos:

Un **runbook** es un documento de procedimientos operativos de rutina. Describe cómo realizar tareas del día a día: iniciar un servicio, ejecutar un proceso de reentrenamiento, hacer un despliegue, rotar credenciales. Su audiencia es el equipo de operaciones y su uso es frecuente y planificado.

Un **playbook** es un documento de respuesta a incidencias. Describe qué hacer cuando algo va mal: cómo diagnosticar un problema, qué pasos seguir para restaurar el servicio, cuándo escalar y a quién. Su audiencia es el equipo de guardia (on-call) y su uso es urgente y bajo presión.

La distinción importa porque las dos audiencias tienen necesidades distintas. El runbook puede permitirse cierto nivel de detalle y contexto; el playbook debe ser escaneable en segundos, con pasos numerados y criterios de decisión claros.

### 6.2 Estructura de runbook ML

Un runbook para un servicio de inferencia ML debe incluir como mínimo los siguientes apartados:

**Descripción del sistema**: Qué hace el servicio, qué modelo sirve, cuál es su versión actual, qué dependencias externas tiene (bases de datos de features, caches, servicios upstream y downstream) y dónde viven sus artefactos (registro de modelos, almacenamiento de logs).

**Diagrama de arquitectura**: Un diagrama simple (puede ser ASCII o Mermaid) que muestre los componentes y sus relaciones. Imprescindible para que alguien nuevo entienda el sistema en dos minutos.

**Dependencias y contactos**: Lista de servicios de los que depende el runbook, con sus SLAs conocidos. Contactos del equipo propietario de cada dependencia. Enlace al canal de Slack o sistema de tickets relevante.

**Procedimientos de inicio y parada**: Comandos exactos para arrancar el servicio, verificar que está sano y detenerlo de forma ordenada. Incluye los health checks que deben pasar tras el arranque.

**Troubleshooting por síntoma**: Tabla o lista de síntomas observables (latencia elevada, errores 500, memoria creciente, predicciones anómalas) con los pasos de diagnóstico y las acciones correctivas conocidas para cada uno.

**Procedimientos de mantenimiento**: Cómo actualizar el modelo en producción, cómo hacer rollback a la versión anterior, cómo escalar horizontalmente ante picos de carga.

### 6.3 Ejemplo de runbook para servicio de inferencia

```markdown
# Runbook · Servicio de Clasificación de Imágenes v2

**Propietario**: Equipo ML Platform  
**On-call**: #mlplatform-oncall (PagerDuty: ML Platform Prod)  
**Última revisión**: 2026-06-01  

## Descripción del sistema

El servicio clasifica imágenes de producto en 200 categorías usando ResNet-50
fine-tuneado (v2.3.1). Sirve ~150 req/s en hora punta. Las imágenes se reciben
en base64 por POST /v2/classify. El modelo se carga desde MLflow Model Registry
al inicio del servicio y se cachea en memoria.

## Dependencias

| Servicio         | SLA     | Contacto              |
|------------------|---------|-----------------------|
| MLflow Registry  | 99.5 %  | #mlflow-support       |
| Redis (cache)    | 99.9 %  | #infra-redis          |
| GPU node pool    | 99.0 %  | #infra-compute        |

## Inicio del servicio

```bash
# 1. Verificar que el modelo está disponible en el registro
mlflow models list --name "image-classifier" --stage Production

# 2. Arrancar el contenedor
docker compose -f docker-compose.prod.yml up -d classifier

# 3. Esperar a que el health check responda
until curl -sf http://localhost:8080/health; do sleep 2; done
echo "Servicio disponible"

# 4. Verificar métricas iniciales
curl http://localhost:8080/metrics | grep model_load_duration_seconds
```

## Parada ordenada

```bash
# Drenar conexiones (Kubernetes)
kubectl rollout pause deployment/image-classifier

# Esperar a que las peticiones en vuelo terminen (máx. 30 s)
sleep 30

# Parar el pod
kubectl rollout resume deployment/image-classifier  # tras el fix
```

## Troubleshooting

| Síntoma                     | Causa probable              | Acción                                      |
|-----------------------------|-----------------------------|---------------------------------------------|
| Latencia P99 > 200 ms       | Batching saturado           | Reducir `max_batch_size` en config Triton   |
| Errores 503 en cascade      | OOM en GPU                  | Ver logs GPU, reiniciar pod, abrir ticket   |
| Predicciones todas iguales  | Modelo no cargado (fallback)| Verificar conexión a MLflow Registry        |
| CPU al 100%, GPU al 0 %     | GPU no detectada            | Verificar `nvidia-smi`, reiniciar driver    |
```

---

## 7. Wikis y bases de conocimiento

### 7.1 Herramientas para equipos técnicos

**Confluence** es la opción estándar en entornos corporativos con ecosistema Atlassian. Su integración con Jira facilita enlazar documentación con tareas y épicas. Su principal debilidad es que el contenido queda separado del repositorio de código, lo que facilita que la documentación quede desactualizada.

**Notion** ha ganado popularidad en equipos de ML por su flexibilidad y su capacidad de combinar texto, bases de datos, imágenes y bloques de código. Es adecuado para documentación de proyecto, diarios de experimentos y dashboards de estado. Al igual que Confluence, su contenido no está en el repositorio.

**Obsidian** es la opción preferida para bases de conocimiento personales o de equipos pequeños. Al almacenar todo en archivos Markdown planos, la documentación puede vivir en el repositorio y versionarse con Git.

### 7.2 Estructura recomendada para proyectos ML

Una estructura de documentación efectiva para proyectos ML equilibra la necesidad de tener documentación de referencia estable con la agilidad de registrar decisiones y experimentos en curso:

```
docs/
├── index.md                    # Punto de entrada: qué es el proyecto, cómo navegar
├── architecture/
│   ├── overview.md             # Diagrama de alto nivel + descripción de componentes
│   └── decisions/              # ADRs (gestionados con adr-tools)
├── api/
│   ├── openapi.yaml            # Especificación OpenAPI mantenida en el repo
│   └── examples.md             # Ejemplos de petición y respuesta
├── guides/
│   ├── getting-started.md      # Setup para desarrollo local
│   ├── training.md             # Cómo lanzar un experimento de entrenamiento
│   └── deployment.md           # Cómo desplegar una nueva versión del modelo
├── operations/
│   ├── runbook.md              # Procedimientos operativos (ver sección 6)
│   └── playbook-incidents.md   # Respuesta a incidencias
├── experiments/
│   └── YYYY-MM-DD_descripcion.md  # Registro de experimentos (one-shot, no se editan)
└── CHANGELOG.md                # Historial de cambios significativos
```

### 7.3 Docs-as-code

El enfoque docs-as-code trata la documentación con las mismas herramientas y el mismo flujo de trabajo que el código: se escribe en texto plano (Markdown o reStructuredText), se versiona en Git, se revisa mediante pull requests y se despliega automáticamente mediante CI/CD.

Las ventajas de este enfoque son importantes:

- La documentación y el código cambian juntos en el mismo commit o PR, reduciendo la desincronización.
- Las revisiones de documentación siguen el mismo proceso de revisión de código, lo que eleva su calidad.
- El historial de Git proporciona trazabilidad completa: quién cambió qué y cuándo.
- La documentación puede versionarse junto con las releases del software.

La principal desventaja es la barrera de entrada para perfiles no técnicos que no están familiarizados con Git y Markdown.

### 7.4 GitHub Pages y GitLab Pages

Tanto GitHub como GitLab ofrecen despliegue gratuito de sitios estáticos generados a partir de los archivos del repositorio. Esto permite publicar automáticamente la documentación de MkDocs o Sphinx cada vez que se hace un merge a la rama principal.

Ejemplo de GitHub Actions para despliegue de MkDocs:

```yaml
name: Deploy docs
on:
  push:
    branches: [main]
    paths: ["docs/**", "mkdocs.yml"]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install mkdocs-material mkdocstrings[python]
      - run: mkdocs gh-deploy --force
```

### 7.5 CHANGELOG.md y changelogs automatizados con git-cliff

El `CHANGELOG.md` es la interfaz pública de la evolución del sistema: registra qué cambió en cada versión, en lenguaje que los usuarios y operadores pueden entender. No es un log de commits; es un resumen editorial de los cambios significativos.

La convención más extendida es **Keep a Changelog** (keepachangelog.com), que organiza los cambios por versión y por tipo: Added, Changed, Deprecated, Removed, Fixed, Security.

Mantener el CHANGELOG manualmente es tedioso y propenso a omisiones. `git-cliff` automatiza la generación de changelogs a partir de los mensajes de commit, siempre que estos sigan el estándar **Conventional Commits**.

El estándar Conventional Commits requiere que los mensajes de commit tengan el formato:

```
<tipo>[ámbito opcional]: <descripción>

[cuerpo opcional]

[footer(s) opcionales]
```

Donde el tipo es uno de: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`. Los commits con tipo `feat` generan entradas en "Added", los de tipo `fix` en "Fixed", y los que incluyen `BREAKING CHANGE` en el footer generan entradas en "Changed" con la nota de ruptura.

Instalación y uso de git-cliff:

```bash
# Instalación
cargo install git-cliff
# O con brew en macOS
brew install git-cliff

# Generar CHANGELOG completo desde el inicio del repositorio
git cliff --output CHANGELOG.md

# Generar solo los cambios de la última release a la actual
git cliff --unreleased --output CHANGELOG.md

# Previsualizar sin escribir el archivo
git cliff --unreleased
```

La configuración de git-cliff se guarda en `cliff.toml` en la raíz del repositorio, donde se puede personalizar el formato de salida, las secciones del changelog y las expresiones regulares para extraer información de los mensajes de commit.

---

## 8. Actividades prácticas

### Actividad 1 · Creación de un ADR para decisión de infraestructura

**Objetivo**: Practicar la escritura de ADRs en formato MADR para decisiones reales de proyectos ML.

**Enunciado**: Tu equipo debe decidir entre dos estrategias de versionado de modelos en producción: (a) mantener múltiples versiones activas simultáneamente con routing basado en cabeceras HTTP, o (b) mantener una sola versión activa con rollback inmediato en caso de degradación de métricas.

Usando `adr-tools`, crea el ADR correspondiente en un repositorio Git nuevo. El ADR debe incluir todos los apartados del formato MADR: contexto con al menos tres fuerzas en juego, la decisión argumentada, consecuencias positivas y negativas, y al menos dos alternativas descartadas con su justificación. El estado inicial debe ser `propuesto`.

**Entregable**: Repositorio Git con el ADR en `doc/decisions/` y un commit con mensaje en formato Conventional Commits.

---

### Actividad 2 · Documentación de API de inferencia con FastAPI y OpenAPI

**Objetivo**: Generar documentación de API completa y precisa para un servicio de inferencia ML usando FastAPI y OpenAPI 3.1.

**Enunciado**: Dado el siguiente modelo de clasificación de texto que acepta una cadena de texto y devuelve la categoría predicha con su probabilidad, implementa un endpoint FastAPI completamente documentado. El endpoint debe:

- Aceptar texto en varios idiomas (especificarlo en el esquema).
- Documentar los posibles errores: texto vacío, texto demasiado largo (límite: 512 tokens), modelo no disponible.
- Incluir ejemplos de petición y respuesta en el esquema OpenAPI.
- Exponer la versión del modelo en la respuesta.

Verifica que la especificación generada en `/openapi.json` es válida usando el validador online de Swagger Editor. Exporta la especificación como `openapi.yaml` y commiteala en el repositorio.

**Entregable**: Aplicación FastAPI funcional, especificación `openapi.yaml` validada.

---

### Actividad 3 · Módulo Python completamente documentado

**Objetivo**: Aplicar las convenciones de docstrings y type hints a un módulo de preprocesamiento de datos.

**Enunciado**: Escribe un módulo `preprocessing.py` que implemente las siguientes funciones con documentación completa en estilo Google y type hints en todas las firmas:

1. `load_and_validate_csv(path: Path, schema: dict) -> pd.DataFrame`: Carga un CSV y valida que las columnas y tipos son correctos.
2. `encode_categoricals(df: pd.DataFrame, columns: list[str], strategy: Literal["onehot", "ordinal", "target"]) -> tuple[pd.DataFrame, dict]`: Codifica variables categóricas según la estrategia indicada.
3. `split_train_val_test(df: pd.DataFrame, val_size: float, test_size: float, stratify_col: str | None, random_state: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]`: División estratificada del dataset.

Configura MkDocs con mkdocstrings y genera la documentación HTML. Verifica que los docstrings se renderizan correctamente.

**Entregable**: Módulo `preprocessing.py`, configuración de MkDocs, documentación HTML generada.

---

### Actividad 4 · Runbook de servicio de inferencia y configuración de CHANGELOG automatizado

**Objetivo**: Redactar un runbook operativo completo y configurar la generación automática de CHANGELOG con git-cliff.

**Enunciado**: Para un servicio hipotético de detección de anomalías en series temporales (modelo LSTM servido con FastAPI, dependencias: InfluxDB, Redis, modelo en S3), redacta un runbook completo que incluya todos los apartados descritos en la sección 6.2. El runbook debe incluir al menos ocho síntomas distintos en la tabla de troubleshooting, con sus causas y acciones.

Paralelamente, en el mismo repositorio del proyecto, configura git-cliff con un `cliff.toml` personalizado que genere un CHANGELOG en español, con secciones "Nuevas funcionalidades", "Correcciones" y "Cambios de ruptura". Crea al menos cinco commits con mensajes en formato Conventional Commits que generen entradas en distintas secciones del CHANGELOG. Genera el CHANGELOG final y verifica su contenido.

**Entregable**: `runbook.md`, `cliff.toml`, `CHANGELOG.md` generado con al menos tres secciones pobladas.

---

## 9. Referencias

- **OpenAPI Initiative**. *OpenAPI Specification 3.1.0* (2021). Especificación completa del estándar.  
  https://spec.openapis.org/oas/v3.1.0

- **Sphinx Project**. *Sphinx Documentation* (2024). Herramienta de generación de documentación para Python.  
  https://www.sphinx-doc.org/

- **MkDocs Project**. *MkDocs Documentation* (2024). Generador de sitios de documentación basado en Markdown.  
  https://www.mkdocs.org/

- **Nygard, M.** *adr-tools: Command-line tools for working with Architecture Decision Records* (GitHub).  
  https://github.com/npryce/adr-tools

- **Korhonen, T.** *MADR: Markdown Any Decision Records* (GitHub).  
  https://github.com/adr/madr

- **Bhatti, J., Corleissen, Z. F., Lambourne, J., Nunez, D., & Waterhouse, H.** *Docs for Developers: An Engineer's Field Guide to Technical Writing*. Apress, 2021.  
  https://docsfordevelopers.com/

- **Ousterhout, J.** *A Philosophy of Software Design* (2nd ed.). Yaknyam Press, 2021.  
  https://web.stanford.edu/~ouster/cgi-bin/book.php

- **git-cliff**. *Highly customizable changelog generator*. Orhun Parmaksız (GitHub).  
  https://github.com/orhun/git-cliff

- **Conventional Commits**. *A specification for adding human and machine readable meaning to commit messages*.  
  https://www.conventionalcommits.org/

- **Keep a Changelog**. *Don't let your friends dump git logs into changelogs*. Olivier Lacan.  
  https://keepachangelog.com/

- **FastAPI**. *FastAPI Documentation: OpenAPI*. Sebastián Ramírez.  
  https://fastapi.tiangolo.com/tutorial/first-steps/
