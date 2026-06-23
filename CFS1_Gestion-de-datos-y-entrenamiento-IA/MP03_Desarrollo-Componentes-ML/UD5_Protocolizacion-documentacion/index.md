---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD5 · Protocolización y documentación técnica | MP03 · Desarrollo de componentes para sistemas de ML'
footer: 'CFS Gestión de datos y entrenamiento IA (IAD)'
---

<style>
section { font-family: 'Segoe UI', Arial, sans-serif; }
h1 { color: #1e3a5f; }
h2 { color: #1e3a5f; border-bottom: 2px solid #3b82f6; padding-bottom: 6px; }
h3 { color: #2563eb; }
table { font-size: 0.82em; width: 100%; }
ul, ol { font-size: 0.88em; }
blockquote { border-left: 4px solid #3b82f6; background: #eff6ff; padding: 8px 16px; border-radius: 4px; }
footer, header { font-size: 0.6em; color: #6b7280; }
section.lead h1 { font-size: 2em; text-align: center; margin-top: 80px; }
section.lead p { text-align: center; color: #4b5563; }
code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
pre { background: #1e293b; color: #e2e8f0; padding: 16px; border-radius: 8px; font-size: 0.8em; }
</style>

<!-- _class: lead -->

# UD5 · Protocolización y documentación técnica

**MP03 · Desarrollo de componentes para sistemas de ML**

CFS — Gestión de datos y entrenamiento IA (IAD)

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Usar Git para versionar el código de un componente ML y documentar las decisiones de arquitectura
- Gestionar dependencias con ficheros de entorno reproducible (`requirements.txt`, `pyproject.toml`)
- Elaborar una ficha técnica de modelo (*model card*) completa con métricas, datos, limitaciones y casos de uso
- Empaquetar un componente ML para su distribución e instalación en otros proyectos
- Redactar y ejecutar pruebas unitarias y de regresión para componentes de ML
- Documentar los resultados de las pruebas de forma trazable y reproducible

---

## Control de versiones con Git — Rol en proyectos de ML

Git es la herramienta central de documentación y trazabilidad en el desarrollo de componentes ML. Un repositorio bien estructurado comunica la arquitectura, las dependencias y la lógica de diseño sin necesidad de documentación adicional.

**Estructura recomendada de un repositorio de componente ML:**

```
mi-componente-ml/
├── src/
│   └── mi_componente/
│       ├── __init__.py
│       ├── pipeline.py          # lógica del pipeline
│       ├── model.py             # definición del modelo
│       └── preprocessing.py    # transformaciones
├── tests/
│   ├── test_pipeline.py
│   ├── test_model.py
│   └── fixtures/               # datos de prueba pequeños
├── docs/
│   └── model_card.md           # ficha técnica del modelo
├── requirements.txt
├── pyproject.toml
├── README.md
└── .gitignore
```

---

## Git — Flujo de trabajo para componentes ML

**Convención de ramas para desarrollo de componentes:**

```bash
# Ramas principales
main          # versión estable, solo merge desde release
develop       # integración continua de nuevas funcionalidades

# Ramas de trabajo
feature/pipeline-multimodal    # nueva funcionalidad
fix/normalizacion-nulos        # corrección de bug
experiment/architecture-v2     # experimento que puede descartarse
release/v1.2.0                 # preparación de release

# Comandos habituales
git checkout -b feature/pipeline-multimodal
git add src/mi_componente/pipeline.py tests/test_pipeline.py
git commit -m "feat(pipeline): añadir soporte para datos tabulares y texto"
git push origin feature/pipeline-multimodal
# → abrir Pull Request hacia develop
```

> Cada commit debe referenciar **qué** cambió, **por qué** y su impacto. El historial de Git es la documentación de las decisiones de diseño.

---

## Git — Mensajes de commit estructurados

Los mensajes de commit bien redactados son documentación activa. La convención **Conventional Commits** es el estándar de facto en proyectos profesionales de software y ML.

**Formato:**

```
<tipo>(<alcance>): <descripción corta>

[cuerpo opcional: por qué, no qué]

[pie opcional: referencias a issues o breaking changes]
```

**Ejemplos para componentes ML:**

```bash
git commit -m "feat(model): implementar arquitectura ResNet18 para clasificación de imagen"
git commit -m "fix(preprocessing): corregir fuga de información en normalización de train/test"
git commit -m "refactor(pipeline): extraer transformador de fechas a clase reutilizable"
git commit -m "test(regression): añadir suite de regresión para inferencia en producción"
git commit -m "docs(model-card): actualizar métricas tras reentrenamiento con dataset v2"

# Breaking change (cambio de API incompatible con versiones anteriores)
git commit -m "feat(api)!: cambiar firma de predict() para soportar batch inference

BREAKING CHANGE: el argumento X ahora debe ser np.ndarray, no lista"
```

---

## Gestión de dependencias y entorno reproducible

Un componente ML es reproducible solo si su entorno de ejecución está completamente especificado. Hay que gestionar tanto las dependencias directas como las indirectas.

**Herramientas de gestión de dependencias:**

| Herramienta | Fichero | Uso recomendado |
|---|---|---|
| `pip` + `requirements.txt` | `requirements.txt` | Proyectos simples, despliegue en contenedores |
| `pip-tools` | `requirements.in` → `requirements.txt` | Control estricto de versiones resueltas |
| `poetry` | `pyproject.toml` + `poetry.lock` | Proyectos de librería, publicación en PyPI |
| `conda` | `environment.yml` | Cuando se necesitan dependencias no-Python (CUDA, MKL) |
| `uv` | `pyproject.toml` + `uv.lock` | Alternativa moderna y muy rápida a pip/poetry |

```bash
# Exportar el entorno actual de forma reproducible
pip freeze > requirements.txt

# Crear entorno desde requirements.txt
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## Declaración de dependencias con pyproject.toml

```toml
[project]
name = "clasificador-toxicidad"
version = "1.2.0"
description = "Componente de clasificación de texto tóxico para plataformas educativas"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "Equipo IA CFS", email = "ia@ejemplo.es" }]

dependencies = [
    "scikit-learn>=1.4,<2.0",
    "pandas>=2.0,<3.0",
    "numpy>=1.26,<2.0",
    "joblib>=1.3",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.4",         # linter y formateador
    "mypy>=1.8",         # verificación de tipos
]

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"
```

---

## Ficha técnica del modelo (Model Card) — Concepto

Las **model cards** son el estándar de documentación para modelos de ML publicado por Google en 2019. Documentan no solo el rendimiento técnico, sino el contexto de uso, las limitaciones y los riesgos del modelo.

**Por qué es obligatoria en contextos profesionales:**

- El Reglamento de IA de la UE (AI Act, 2024) exige documentación técnica para sistemas de alto riesgo
- La norma ISO/IEC 42001:2023 (Sistemas de gestión de IA) incluye la model card como artefacto obligatorio
- Permite a quienes integran el modelo conocer sus límites antes de desplegarlo
- Es la base para auditorías de IA y procesos de certificación

> Una model card sin sección de limitaciones es incompleta y potencialmente engañosa.

---

## Model Card — Estructura completa (1/2)

| Sección | Contenido obligatorio |
|---|---|
| **Identificación** | Nombre, versión, fecha, responsable técnico, organización |
| **Descripción** | Tarea, dominio de aplicación, tipo de entrada/salida |
| **Arquitectura** | Familia de modelo, framework, número de parámetros, formato de serialización |
| **Datos de entrenamiento** | Dataset, versión, tamaño, periodo temporal, fuente, licencia |
| **Preprocesamiento** | Transformaciones aplicadas al entrenamiento |
| **Partición de datos** | Proporciones train/val/test, criterio de división, semilla |

---

## Model Card — Estructura completa (2/2)

| Sección | Contenido obligatorio |
|---|---|
| **Métricas de evaluación** | Métricas en test por clase y global; intervalo de confianza si aplica |
| **Rendimiento por subgrupo** | Métricas desagregadas por atributos sensibles |
| **Limitaciones conocidas** | Contextos donde el modelo no es fiable |
| **Sesgos detectados** | Variables sensibles, disparidades de rendimiento documentadas |
| **Casos de uso adecuados** | Aplicaciones validadas y autorizadas |
| **Casos de uso NO adecuados** | Usos expresamente desaconsejados |
| **Trazabilidad** | Git commit, hash de dataset, run_id de MLflow |
| **Mantenimiento** | Responsable, frecuencia de revisión, política de retirada |

---

## Model Card — Ejemplo real en Markdown

```markdown
# Model Card: Clasificador de Texto Tóxico v1.2.0

## Identificación
- **Responsable:** Equipo IA — CFS IAD 2026  |  **Fecha:** 2026-06-23
- **Versión:** 1.2.0  |  **Git commit:** a7f3d91  |  **Dataset hash:** sha256:3b4e...

## Descripción
Clasifica comentarios en texto libre como tóxicos (1) o no tóxicos (0).
Diseñado para plataformas educativas en español peninsular (España).
Entrada: texto UTF-8, máx. 512 tokens. Salida: clase + probabilidad.

## Métricas en test (n=8 420 registros)
| Métrica  | Global | Clase 0 | Clase 1 |
|----------|--------|---------|---------|
| F1       | 0.820  | 0.851   | 0.789   |
| Precision| 0.834  | 0.862   | 0.806   |
| Recall   | 0.807  | 0.840   | 0.773   |
| AUC-ROC  | 0.912  | —       | —       |

## Limitaciones
- No fiable con ironía, sarcasmo o lenguaje en clave
- Entrenado solo con español peninsular: variantes no validadas
- F1 en subgrupo "lenguaje informal": 0.71 (rendimiento reducido)

## Casos de uso NO adecuados
- Moderación automática sin supervisión humana en procesos disciplinarios
- Clasificación de contenido médico o legal
```

---

## Empaquetado para distribución y reutilización

Empaquetar un componente ML permite instalarlo en otros proyectos como una librería Python estándar, sin copiar código.

```bash
# Estructura mínima para un paquete instalable
clasificador-toxicidad/
├── src/clasificador_toxicidad/
│   ├── __init__.py
│   ├── model.py
│   └── preprocessing.py
├── pyproject.toml
└── README.md

# Construir el paquete (genera dist/*.whl y dist/*.tar.gz)
pip install build
python -m build

# Instalar el paquete localmente (modo editable para desarrollo)
pip install -e .

# Instalar en otro proyecto
pip install dist/clasificador_toxicidad-1.2.0-py3-none-any.whl

# Publicar en PyPI (repositorio público) o en un registro privado
pip install twine
twine upload dist/*
```

---

## Empaquetado — Uso del componente instalado

```python
# En otro proyecto, tras instalar el paquete:
from clasificador_toxicidad import ClasificadorToxicidad

# El componente encapsula el modelo y el preprocesador
clf = ClasificadorToxicidad.cargar("modelos/toxicidad_v1.2.0.joblib")

# Inferencia con la API pública del componente
textos = [
    "Este ejercicio está muy bien explicado",
    "No entiendo nada de lo que dice este profesor",
]
predicciones = clf.predecir(textos)
# [{'texto': '...', 'clase': 0, 'probabilidad': 0.91},
#  {'texto': '...', 'clase': 0, 'probabilidad': 0.73}]

# Versión y metadatos del componente
print(clf.version)         # "1.2.0"
print(clf.model_card_url)  # URL a la documentación
```

> Un componente bien empaquetado oculta la implementación interna y expone solo la API pública. Esto es lo que permite la reutilización segura.

---

## Pruebas unitarias para componentes ML

Las pruebas unitarias verifican que cada función del componente se comporta correctamente de forma aislada. En ML, se aplican a las transformaciones, la carga del modelo y la inferencia.

```python
import pytest
import numpy as np
from clasificador_toxicidad import ClasificadorToxicidad
from clasificador_toxicidad.preprocessing import normalizar_texto

class TestNormalizarTexto:
    """Pruebas unitarias del preprocesador de texto."""

    def test_elimina_espacios_extra(self):
        assert normalizar_texto("hola   mundo") == "hola mundo"

    def test_convierte_a_minusculas(self):
        assert normalizar_texto("HOLA MUNDO") == "hola mundo"

    def test_elimina_caracteres_especiales(self):
        assert normalizar_texto("¡Hola! ¿Qué tal?") == "hola qué tal"

    def test_texto_vacio_devuelve_cadena_vacia(self):
        assert normalizar_texto("") == ""

    def test_texto_nulo_lanza_excepcion(self):
        with pytest.raises(TypeError):
            normalizar_texto(None)
```

---

## Pruebas de regresión para componentes ML

Las pruebas de regresión garantizan que una nueva versión del componente no introduce degradación en el rendimiento respecto a la versión anterior.

```python
import pytest
import joblib
import numpy as np
from sklearn.metrics import f1_score

# Fixture: datos de referencia con las predicciones conocidas de v1.1.0
TEXTOS_REFERENCIA = [
    "Este texto es completamente inofensivo",
    "Texto con contenido claramente inapropiado",
    "Comentario neutro sobre el tema",
]
ETIQUETAS_REFERENCIA = [0, 1, 0]
UMBRAL_F1_MINIMO = 0.75  # no se acepta regresión por debajo de este valor

class TestRegresionRendimiento:

    @pytest.fixture
    def modelo(self):
        return joblib.load("modelos/toxicidad_v1.2.0.joblib")

    def test_f1_no_regresiona(self, modelo):
        predicciones = modelo.predict(TEXTOS_REFERENCIA)
        f1 = f1_score(ETIQUETAS_REFERENCIA, predicciones)
        assert f1 >= UMBRAL_F1_MINIMO, (
            f"Regresion detectada: F1={f1:.3f} < umbral={UMBRAL_F1_MINIMO}"
        )

    def test_predicciones_deterministas(self, modelo):
        pred_1 = modelo.predict(TEXTOS_REFERENCIA)
        pred_2 = modelo.predict(TEXTOS_REFERENCIA)
        np.testing.assert_array_equal(pred_1, pred_2)
```

---

## Ejecución y documentación de pruebas

```bash
# Ejecutar todas las pruebas con informe de cobertura
pytest tests/ -v --cov=src/clasificador_toxicidad --cov-report=term-missing

# Salida esperada:
# tests/test_preprocessing.py::TestNormalizarTexto::test_elimina_espacios_extra PASSED
# tests/test_model.py::TestRegresionRendimiento::test_f1_no_regresiona PASSED
# ...
# ---------- coverage: 87% ----------

# Guardar el informe de pruebas en XML (para CI/CD)
pytest tests/ --junitxml=reports/test-results.xml

# Ejecutar solo las pruebas de regresión
pytest tests/ -m regression -v
```

**Registro de resultados de pruebas en Git:**

```bash
# Incluir el informe de pruebas en el commit de release
git add reports/test-results.xml docs/model_card.md
git commit -m "release(v1.2.0): publicar componente con suite de pruebas completa

Cobertura: 87%. Todos los tests de regresión superados.
F1 en test: 0.820 (mejora de 0.013 respecto a v1.1.0)"
```

---

## Actividad práctica — UD5

**Contexto:** El clasificador de toxicidad ha alcanzado las métricas requeridas. Debes formalizarlo como componente distribuible con documentación completa.

**Tareas:**

1. Estructura el repositorio Git con la jerarquía recomendada. Crea al menos 5 commits con mensajes en formato Conventional Commits que documenten el proceso de desarrollo
2. Declara las dependencias del componente en `pyproject.toml` con rangos de versión exactos
3. Elabora la model card completa en Markdown con todas las secciones de las tablas vistas, incluyendo métricas desagregadas por subgrupo
4. Empaqueta el componente con `python -m build` e instálalo en un entorno virtual nuevo para verificar que la importación funciona correctamente
5. Implementa al menos 4 pruebas unitarias para el preprocesador y 2 pruebas de regresión para el modelo. Ejecuta la suite completa y documenta el resultado de cobertura

---

## Puntos clave — UD5

- El historial de Git es la documentación de arquitectura más fiable: cada commit debe responder a "qué" y "por qué", no solo "cómo"
- Los mensajes de commit en Conventional Commits son legibles por máquinas (changelogs automáticos) y por personas (revisiones de código)
- Un entorno reproducible requiere versiones fijadas y un fichero de lock: `requirements.txt` con versiones exactas o `poetry.lock`
- La model card debe incluir limitaciones y rendimiento por subgrupo: omitirlos es ocultación de información relevante para quien va a usar el modelo
- Empaquetar el componente con `pyproject.toml` permite instalarlo en otros proyectos sin copiar código, garantizando que todos usan la misma versión
- Las pruebas de regresión protegen contra la degradación silenciosa: sin ellas, una versión nueva puede introducir errores que pasan desapercibidos

---

## Criterios de evaluación — UD5

| Criterio | Indicador de logro |
|---|---|
| Protocoliza con control de versiones | Aplica Git con ramas, mensajes estructurados y commits atómicos que documentan las decisiones de diseño |
| Gestiona dependencias reproduciblemente | Declara dependencias en `pyproject.toml` o `requirements.txt` con versiones fijadas |
| Elabora la model card | Cubre todas las secciones obligatorias incluyendo limitaciones, sesgos y rendimiento por subgrupo |
| Empaqueta para distribución | Genera un paquete instalable con `python -m build` que funciona en un entorno limpio |
| Documenta pruebas unitarias | Implementa tests con `pytest` que verifican el comportamiento de cada función del componente |
| Documenta pruebas de regresión | Implementa tests que detectan degradación de rendimiento respecto a la versión anterior |

---

<!-- _class: lead -->

[← Volver a MP03](../)


---

<!-- nav-slide -->

## Navegación

[← UD4 · Validación de la calidad de l…](../UD4_Validacion-calidad-componentes/) &nbsp;·&nbsp; [Volver al módulo](../) &nbsp;·&nbsp; [UD6 · Vigilancia tecnológica →](../UD6_Vigilancia-tecnologica/)
