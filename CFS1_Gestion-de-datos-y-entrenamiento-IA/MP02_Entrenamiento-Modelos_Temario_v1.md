# MP02 · Entrenamiento de modelos de aprendizaje automático

*Módulo profesional del CFS «Gestión de datos y entrenamiento IA (IAD)»*

| Campo | Valor |
|---|---|
| Código | MP02 |
| Estándar de competencia asociado | ECP2493_3 (Nivel 3) |
| Familia profesional | Inteligencia Artificial y Data |
| Duración orientativa | 190 h |
| Curso | 1.º |

**Competencia que desarrolla:** implementar la estrategia de entrenamiento mediante el análisis del problema, la configuración de arquitecturas y parámetros, el diseño de modelos de Machine Learning y su versionado para garantizar trazabilidad y despliegue.

Las unidades didácticas (UD) concretan los resultados de aprendizaje del módulo. *Duración y curso son orientativos (propuesta).*

---

## UD1. Selección de la estrategia de entrenamiento

**Resultados de aprendizaje.** Selecciona la estrategia de entrenamiento analizando la naturaleza del problema, los datos y las restricciones de cómputo.

**Contenidos.**

- Paradigmas de aprendizaje: supervisado, no supervisado, autosupervisado y por refuerzo. Criterios de elección según datos etiquetados.
- Entrenar desde cero frente a *fine-tuning*: volumen de datos, recursos, memoria, latencia de inferencia.
- Familias de modelos candidatos: ML clásico, redes neuronales, modelos de visión, modelos de lenguaje.
- Documentación de la estrategia: criterios de decisión, alternativas, justificación.
- Documento de variables de entrada y salida y correlaciones encontradas.

**Criterios de evaluación.** Determina el paradigma adecuado al problema; justifica la familia de modelos; documenta la estrategia como base del diseño.

---

## UD2. Configuración del modelo y del entorno de entrenamiento

**Resultados de aprendizaje.** Configura arquitectura, función de pérdida y parámetros mediante *frameworks*, garantizando la reproducibilidad.

**Contenidos.**

- *Frameworks*: Scikit-learn, PyTorch, TensorFlow. Modelo desde cero o preentrenado.
- Función de pérdida según problema: entropía cruzada (clasificación), MSE (regresión). Tasa de aprendizaje y parámetros del algoritmo.
- Preparación del entorno: CPU, GPU, TPU, nube. Librerías y versiones.
- Reproducibilidad: control de semillas aleatorias y versionado de dependencias.
- Documentación de la configuración.

**Criterios de evaluación.** Selecciona arquitectura y función de pérdida coherentes con el problema; prepara un entorno reproducible; documenta los parámetros.

---

## UD3. Operativización del entrenamiento

**Resultados de aprendizaje.** Operativiza el entrenamiento lanzando experimentos, monitorizando el proceso y aplicando técnicas de mejora.

**Contenidos.**

- Búsqueda de hiperparámetros: *grid search*, *random search*, optimización bayesiana. Herramientas como Optuna.
- Monitorización en tiempo real con TensorBoard u otras. Detección de sobreajuste e infraajuste.
- Técnicas de mejora: parada temprana, regularización L1 (Lasso) y L2 (Ridge), ajuste del *learning rate*.
- Lanzamiento del entrenamiento definitivo con la mejor configuración y semillas controladas.
- Documentación de experimentos y resultados.

**Criterios de evaluación.** Ejecuta búsquedas de hiperparámetros; aplica técnicas de mejora ante resultados insatisfactorios; documenta para justificar la configuración final.

---

## UD4. Evaluación del modelo entrenado

**Resultados de aprendizaje.** Evalúa el modelo calculando métricas adecuadas e interpretando su comportamiento.

**Contenidos.**

- Métricas según problema: *accuracy*, F1, AUC-ROC (clasificación); MSE, R² (regresión).
- Visualización de resultados: matriz de confusión, curvas ROC. Patrones de error por clase o rango.
- Interpretabilidad (XAI): SHAP, LIME. Identificación de variables influyentes.
- Decisión de rediseño o creación de nuevos modelos según resultados.
- Documentación: métricas, gráficas, conclusiones, aptitud del modelo.

**Criterios de evaluación.** Calcula métricas pertinentes; interpreta el comportamiento con herramientas de visualización y XAI; decide sobre la validez del modelo.

---

## UD5. Versionado y ficha técnica del modelo

**Resultados de aprendizaje.** Versiona el modelo en formato estándar y documenta sus características para garantizar trazabilidad.

**Contenidos.**

- Guardado en formato estándar para portabilidad y compatibilidad con entornos de despliegue.
- Versionado del estado del modelo. Trazabilidad y reproducibilidad del proceso.
- Ficha técnica (*model card*): métricas, datos de entrenamiento, limitaciones, casos de uso.

**Criterios de evaluación.** Guarda y versiona el modelo; elabora la ficha técnica completa.

---

## UD6. Trabajo responsable, sostenible y prevención de riesgos

**Resultados de aprendizaje.** Actúa con equidad, sostenibilidad y seguridad, previniendo riesgos laborales (EC6 y EC7).

**Contenidos.**

- Autonomía, responsabilidad ética y adaptabilidad. Comunicación eficaz entre roles.
- Sostenibilidad: arquitecturas y parámetros que reducen consumo y emisiones. Economía circular de datos y algoritmos: evitar duplicidad de experimentos mediante registro y versionado.
- Prevención de riesgos: riesgos psicosociales, tecnoestrés, ergonomía cognitiva, física y ambiental. Plan de emergencias.

**Criterios de evaluación.** Reduce el coste computacional por diseño; evita duplicidades; aplica medidas ergonómicas y de prevención.

---

*Ocupaciones asociadas: integradores de sistemas de información de IA. Sector: análisis y gestión de datos, área de entrenamiento.*
