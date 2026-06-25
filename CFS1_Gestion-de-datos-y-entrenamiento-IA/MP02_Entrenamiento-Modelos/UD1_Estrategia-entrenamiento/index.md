---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD1 · Selección de la estrategia de entrenamiento | MP02 · Entrenamiento de modelos de aprendizaje automático'
footer: 'Apuntes de IA y Datos'
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

# UD1 · Selección de la estrategia de entrenamiento

**MP02 · Entrenamiento de modelos de aprendizaje automático**

Apuntes de IA y Datos

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno será capaz de:

- Identificar y distinguir los cuatro paradigmas principales de aprendizaje automático
- Seleccionar el paradigma más adecuado según los datos disponibles y el objetivo del problema
- Decidir entre entrenar un modelo desde cero o aplicar fine-tuning sobre uno preentrenado
- Clasificar las familias de modelos candidatos según el tipo de dato y la tarea
- Documentar la estrategia de entrenamiento con criterios justificados y reproducibles
- Describir las variables de entrada y salida del modelo y sus correlaciones

---

## Paradigmas de aprendizaje automático — Concepto

Los **paradigmas de aprendizaje** definen la relación entre los datos de entrada, las etiquetas y el mecanismo de actualización del modelo. La elección del paradigma es la primera decisión de diseño y condiciona la arquitectura, los datos necesarios y el proceso de evaluación.

**Por qué importa:**
- Un paradigma incorrecto puede requerir datos que no existen o recursos inasumibles
- Afecta directamente al coste computacional y al tiempo de desarrollo
- Determina el tipo de evaluación y las métricas aplicables

> En la industria, el paradigma se decide antes de elegir el framework o la arquitectura concreta.

---

## Paradigmas — Los cuatro tipos fundamentales

| Paradigma | Datos necesarios | Mecanismo | Cuándo usarlo |
|---|---|---|---|
| **Supervisado** | Etiquetados (X, y) | Minimiza error respecto a etiqueta | Clasificación, regresión con ground truth |
| **No supervisado** | Sin etiquetar | Encuentra estructura en los datos | Clustering, reducción de dimensionalidad |
| **Autosupervisado** | Sin etiquetar (genera sus propias supervisiones) | Predice partes enmascaradas o rotadas | Pre-entrenamiento de LLMs y modelos de visión |
| **Por refuerzo** | Retroalimentación de recompensa | Maximiza recompensa acumulada | Agentes, juegos, decisiones secuenciales |

---

## Paradigmas — Criterios de elección

**Árbol de decisión simplificado:**

```
¿Disponemos de etiquetas?
├─ Sí, abundantes y fiables  →  Supervisado
├─ Sí, pero muy pocas         →  Autosupervisado + Fine-tuning supervisado
└─ No                          →  No supervisado
       ├─ Agrupar datos        →  Clustering
       └─ Aprender a actuar    →  Aprendizaje por refuerzo
```

**Factores adicionales:**
- Volumen de datos disponibles (cantidad y calidad)
- Restricciones de cómputo y tiempo de entrenamiento
- Necesidad de interpretabilidad en el resultado
- Normativa aplicable (p. ej. sistemas de IA de alto riesgo, Reglamento de IA UE)

---

## Paradigmas — Ejemplo práctico por dominio

| Dominio | Tarea concreta | Paradigma elegido | Razón |
|---|---|---|---|
| Salud | Detección de tumores en radiografías | Supervisado | Hay imágenes etiquetadas por radiólogos |
| Retail | Segmentación de clientes | No supervisado | No existe categoría previa de cliente |
| PLN | Asistente de atención al cliente | Autosupervisado + Fine-tuning | Modelo base preentrenado, ajustado con ejemplos propios |
| Manufactura | Robot de ensamblaje adaptativo | Por refuerzo | Aprende por prueba-error en simulación |

---

## Entrenar desde cero vs. fine-tuning — Concepto

**Entrenar desde cero** (*training from scratch*): el modelo inicializa sus pesos de forma aleatoria y aprende todo a partir del conjunto de datos propio.

**Fine-tuning**: se parte de un modelo preentrenado en un corpus masivo y se ajustan algunos pesos sobre datos específicos del dominio.

**Por qué este análisis es crítico:**
- Elegir entrenar desde cero con pocos datos lleva al sobreajuste inevitable
- El fine-tuning mal planteado puede destruir el conocimiento previo del modelo base (*catastrophic forgetting*)
- La decisión afecta a hardware, tiempo de proyecto y coste económico

---

## Entrenar desde cero vs. fine-tuning — Tabla comparativa

| Criterio | Entrenar desde cero | Fine-tuning |
|---|---|---|
| **Volumen de datos mínimo** | Millones de ejemplos | Cientos o miles |
| **Recursos de cómputo** | Muy elevados (GPU cluster) | Moderados (1-4 GPU) |
| **Tiempo de desarrollo** | Semanas o meses | Horas o días |
| **Especialización** | General o de dominio amplio | Muy especializado |
| **Riesgo de sobreajuste** | Bajo (con datos suficientes) | Alto con pocos datos |
| **Coste económico** | Alto | Bajo-moderado |
| **Flexibilidad de arquitectura** | Total | Limitada al modelo base |

---

## Entrenar desde cero vs. fine-tuning — Práctica

```python
# Ejemplo: Fine-tuning de un clasificador de imágenes con PyTorch
import torch
import torchvision.models as models
import torch.nn as nn

# Cargar modelo preentrenado (ResNet-50 en ImageNet)
modelo = models.resnet50(pretrained=True)

# Congelar todos los pesos (solo entrenaremos la cabeza)
for param in modelo.parameters():
    param.requires_grad = False

# Sustituir la capa final por el número de clases del dominio propio
num_clases = 5  # ejemplo: 5 tipos de defectos en manufactura
modelo.fc = nn.Linear(modelo.fc.in_features, num_clases)

# Solo los parámetros de la cabeza se actualizarán
optimizer = torch.optim.Adam(modelo.fc.parameters(), lr=1e-3)
```

> La variable `requires_grad = False` congela las capas preentrenadas. Solo la nueva capa `fc` aprende.

---

## Familias de modelos candidatos — Concepto

Antes de elegir una arquitectura concreta, se selecciona la **familia** de modelos más adecuada a la naturaleza del dato y el objetivo. Esta elección determina la complejidad del pipeline, los recursos y las herramientas a utilizar.

**Por qué delimitar la familia primero:**
- Cada familia requiere preprocesamiento específico (normalización, tokenización, augmentación...)
- Las familias tienen ecosistemas de herramientas distintos
- La familia condiciona los recursos de inferencia en producción

---

## Familias de modelos — Tabla de referencia

| Familia | Naturaleza del dato | Arquitectura típica | Framework habitual |
|---|---|---|---|
| **ML clásico** | Tabular, estructurado | Random Forest, XGBoost, SVM, KNN | Scikit-learn |
| **Redes neuronales DNN** | Tabular complejo, series | MLP, capas densas | PyTorch, Keras |
| **Modelos de visión** | Imagen, vídeo | CNN (ResNet, EfficientNet), ViT | PyTorch, TF |
| **Modelos de lenguaje** | Texto, código | Transformer, BERT, GPT | HuggingFace |
| **Series temporales** | Secuencias temporales | LSTM, GRU, Temporal Fusion Transformer | PyTorch, Prophet |
| **Grafos** | Datos relacionales en red | GNN, GraphSAGE | PyG, DGL |

---

## Familias de modelos — Criterios técnicos de selección

**ML clásico** es preferible cuando:
- Los datos son tabulares con menos de 100K filas
- Se requiere interpretabilidad nativa (árbol de decisión, coeficientes)
- El tiempo de entrenamiento es un factor crítico

**Redes neuronales profundas** son preferibles cuando:
- Las relaciones entre variables son no lineales y complejas
- Se dispone de grandes volúmenes de datos
- El hardware GPU está disponible

**Modelos preentrenados (visión o lenguaje)** son preferibles cuando:
- El dominio tiene suficiente similitud con los datos de preentrenamiento
- Los datos propios son escasos o difíciles de obtener

---

## Variables de entrada y salida — Concepto

El **documento de variables** es un artefacto fundamental de la estrategia. Define formalmente qué entra al modelo, qué sale y qué relaciones existen entre variables. Sin este documento, el equipo técnico trabaja con supuestos implícitos que generan errores difíciles de detectar.

**Qué incluye:**
- Lista de features de entrada con tipo, rango y origen
- Variable(s) objetivo con tipo (categórica, continua, binaria...)
- Correlaciones detectadas en el análisis exploratorio
- Variables descartadas y razón de exclusión

---

## Variables de entrada y salida — Análisis de correlaciones

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("dataset_entrenamiento.csv")

# Matriz de correlación de Pearson para variables numéricas
correlaciones = df.select_dtypes(include='number').corr()

# Visualización como mapa de calor
plt.figure(figsize=(10, 8))
sns.heatmap(correlaciones, annot=True, fmt=".2f",
            cmap="coolwarm", center=0)
plt.title("Correlaciones entre variables de entrada")
plt.tight_layout()
plt.savefig("correlaciones.png", dpi=150)

# Variables con correlacion alta con el target (>0.5 o <-0.5)
target = "precio_venta"
correlaciones_target = correlaciones[target].abs().sort_values(ascending=False)
print(correlaciones_target[correlaciones_target > 0.5])
```

---

## Variables de entrada y salida — Plantilla de documento

| Variable | Tipo | Rango / Categorías | Origen | Correlación con target | Incluida |
|---|---|---|---|---|---|
| `superficie_m2` | Numérica continua | 20 – 800 | CRM | 0.78 | Sí |
| `num_habitaciones` | Numérica entera | 1 – 10 | CRM | 0.61 | Sí |
| `codigo_postal` | Categórica nominal | 28 valores | CRM | — | Sí (codificada) |
| `id_propietario` | Identificador | Único por fila | CRM | — | No (leakage) |
| `precio_venta` | Numérica continua | 80K – 1.2M | CRM | — | Target |

**Campos obligatorios del documento:** nombre, tipo, rango, fuente, correlación con target, decisión de inclusión y razón.

---

## Documentación de la estrategia de entrenamiento

La estrategia debe documentarse como un artefacto formal que forme parte del historial del proyecto. Su función es triple: sirve como contrato entre el equipo técnico y los stakeholders, garantiza la reproducibilidad del proceso y facilita la auditoría.

**Secciones mínimas del documento de estrategia:**

- **Descripción del problema:** objetivo, tipo de tarea, restricciones
- **Paradigma seleccionado:** con justificación y alternativas descartadas
- **Decisión sobre fine-tuning o scratch:** criterios que llevaron a la decisión
- **Familia de modelos candidatos:** seleccionados y descartados con razón
- **Variables de entrada y salida:** con tabla de correlaciones
- **Restricciones de cómputo:** hardware disponible, tiempo máximo, presupuesto

---

## Actividad práctica — UD1

**Contexto:** Una empresa de logística quiere predecir si un paquete llegará tarde (sí/no) a partir de datos históricos de envíos: peso, distancia, tipo de servicio, zona geográfica, fecha de envío.

**Tareas:**

1. Identifica el paradigma de aprendizaje más adecuado y justifica la decisión
2. Decide entre entrenar desde cero o aplicar fine-tuning. Argumenta con al menos 3 criterios
3. Selecciona la familia de modelos más apropiada para este caso y descarta al menos una alternativa
4. Construye la tabla de variables de entrada: tipo, rango estimado, hipótesis de correlación con el target
5. Redacta el apartado "Descripción del problema" del documento de estrategia (máx. 150 palabras)

**Entregable:** Documento de estrategia en formato Markdown con las 5 secciones cubiertas.

---

## Puntos clave — UD1

- El paradigma de aprendizaje se determina por la disponibilidad de etiquetas, el objetivo y las restricciones, no por las preferencias del equipo
- Fine-tuning es la opción por defecto cuando existe un modelo preentrenado en el dominio y los datos propios son escasos
- La familia de modelos se elige por la naturaleza del dato (tabular, imagen, texto), no por el framework de moda
- El documento de variables es un artefacto obligatorio: sin él, las decisiones de preprocesamiento y arquitectura son arbitrarias
- Documentar las alternativas descartadas y su razón es tan importante como documentar la elección final
- La estrategia de entrenamiento es la base de todo el proceso: errores aquí se propagan y amplifican en fases posteriores

---

## Criterios de evaluación — UD1

| Criterio | Indicador de logro |
|---|---|
| Determina el paradigma adecuado | Identifica el paradigma correcto y descarta los inadecuados con argumentos técnicos |
| Justifica la familia de modelos | Relaciona la naturaleza del dato con la familia seleccionada; descarta alternativas |
| Documenta la estrategia | Produce un documento estructurado con problema, paradigma, familia, variables y restricciones |
| Analiza variables de entrada y salida | Construye la tabla de variables con tipo, rango, correlación y decisión de inclusión |
| Decide sobre fine-tuning | Aplica los criterios de volumen, recursos y similitud de dominio correctamente |


---

<!-- nav-slide -->

## Navegación

[Volver al módulo](../) &nbsp;·&nbsp; [UD2 · Configuración del modelo y de… →](../UD2_Configuracion-modelo-entorno/)
