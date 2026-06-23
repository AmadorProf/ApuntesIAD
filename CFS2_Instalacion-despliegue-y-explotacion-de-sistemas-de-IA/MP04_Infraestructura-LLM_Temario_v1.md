# MP04 · Infraestructura para la ejecución de LLMs

*Módulo profesional del CFS «Instalación, despliegue y explotación de sistemas de IA (IAD)»*

| Campo | Valor |
|---|---|
| Código | MP04 |
| Estándar de competencia asociado | CPE_5074_3 (Nivel 3) |
| Familia profesional | Inteligencia Artificial y Data |
| Duración orientativa | 160 h |
| Curso | 2.º |

**Competencia que desarrolla:** implementar el despliegue técnico de soluciones basadas en LLMs, desde la infraestructura y configuración de inferencia hasta su puesta en servicio, garantizando rendimiento, seguridad, trazabilidad y uso responsable.

Las unidades didácticas (UD) concretan los resultados de aprendizaje del módulo. *Duración y curso son orientativos (propuesta).*

---

## UD1. Análisis de requisitos del sistema LLM

**Resultados de aprendizaje.** Analiza los requisitos técnicos, funcionales y operativos del sistema, identificando condiciones de ejecución y restricciones de servicio.

**Contenidos.**

- Entorno de ejecución: local, nube, servicios externos, arquitecturas híbridas.
- Características del modelo: tamaño, número de parámetros, formato de pesos, precisión numérica, cuantización, longitud de contexto, modalidad de entrada y salida.
- Requisitos de servicio: usuarios concurrentes, volumen de peticiones, latencia, disponibilidad, privacidad, conectividad, coste.
- Limitaciones técnicas: memoria de vídeo, memoria principal, cómputo, tamaño de lote, concurrencia, caché.
- Documentación de requisitos mínimos y recomendados.

**Criterios de evaluación.** Determina el entorno de ejecución; identifica las características del modelo y los requisitos de servicio; documenta las restricciones.

---

## UD2. Selección y dimensionamiento de recursos

**Resultados de aprendizaje.** Selecciona los recursos de infraestructura calculando necesidades de cómputo, memoria, almacenamiento y comunicaciones.

**Contenidos.**

- Recursos de memoria según tamaño del modelo, precisión, cuantización, longitud de contexto y concurrencia.
- Aceleradores: GPU, NPU, TPU. Memoria, compatibilidad de controladores, capacidad.
- Dimensionamiento de CPU, RAM, almacenamiento y comunicaciones.
- Eficiencia energética: reducción de recursos ociosos, minimización del impacto ambiental. DNSH y ODS.
- Comparación de alternativas: local, servidor propio, nube, servicios gestionados, híbrida. Condiciones de escalado o sustitución.

**Criterios de evaluación.** Calcula la memoria y los aceleradores necesarios; dimensiona el resto de recursos con criterios de eficiencia; formaliza la alternativa de infraestructura.

---

## UD3. Preparación del entorno de ejecución

**Resultados de aprendizaje.** Prepara el entorno instalando y verificando el motor de inferencia, dependencias y componentes.

**Contenidos.**

- SO, *firmware*, controladores y dependencias de bajo nivel. Compatibilidad con el motor de inferencia.
- Entornos de ejecución: gestores de paquetes, entornos virtuales, contenedores, imágenes base, librerías de cómputo acelerado.
- Instalación del motor de inferencia: ruta del modelo, formato, precisión, memoria, tamaño de contexto, concurrencia, límites de generación.
- Autenticación, control de acceso y gestión de secretos según el Plan de seguridad.
- Validación: pruebas de arranque, cargas de prueba, revisión del uso de recursos.

**Criterios de evaluación.** Habilita SO y dependencias compatibles; instala y configura el motor de inferencia; valida el entorno con cargas de prueba.

---

## UD4. Puesta en servicio del modelo

**Resultados de aprendizaje.** Pone en servicio modelos LLM configurando parámetros de ejecución, acceso y exposición a aplicaciones consumidoras.

**Contenidos.**

- Incorporación del modelo: descarga, copia o registro. Verificación de integridad, versión, formato, licencia y compatibilidad.
- Parametrización de variantes: tamaño, cuantización, precisión, consumo, rendimiento.
- Parámetros de ejecución: longitud máxima de entrada y salida, máximo de *tokens*, memoria, concurrencia, límites por usuario, tiempo de respuesta, políticas de parada.
- Exposición: API, servicio interno, interfaz local, contenedor, microservicio, plataforma de orquestación.
- Registro del despliegue: carga del modelo, estabilidad, accesos, límites, incidencias.

**Criterios de evaluación.** Incorpora y parametriza el modelo; configura los parámetros de ejecución; expone el modelo y registra el despliegue.

---

## UD5. Validación de la capacidad operativa

**Resultados de aprendizaje.** Valida la capacidad operativa ejecutando pruebas de carga, concurrencia, estabilidad y recuperación.

**Contenidos.**

- Pruebas de carga, concurrencia y rendimiento: latencia, tiempo de primera respuesta, velocidad de inferencia, uso de memoria de vídeo, CPU, RAM, red y aceleradores.
- Identificación de límites operativos: saturación, caída de rendimiento, errores por falta de recursos, tiempos de espera.
- Mecanismos de recuperación y continuidad: reinicio, recuperación ante errores, reversión, procedimientos alternativos.
- Documentación de validación: métricas, límites, incidencias, recomendaciones de ajuste o escalado.

**Criterios de evaluación.** Ejecuta pruebas de carga y concurrencia; identifica límites operativos; comprueba la recuperación y documenta los resultados.

---

## UD6. Seguridad, privacidad y trazabilidad de la infraestructura

**Resultados de aprendizaje.** Aplica controles de seguridad, privacidad, trazabilidad y uso responsable sobre la infraestructura.

**Contenidos.**

- Riesgos: exposición no autorizada, acceso indebido a modelos o *endpoints*, fuga de información, manipulación de configuraciones, consumo no controlado.
- Autenticación, autorización y control de acceso: mínimo privilegio, separación de funciones, gestión de secretos, restricciones de red.
- Supervisión de registros, trazas y metadatos. Minimización y eliminación.
- Trazabilidad: versiones, configuraciones, accesos. Monitorización de peticiones, errores y cambios.
- Límites de uso y consumo: cuotas, frecuencia, concurrencia, tamaño de entrada y salida, parada o degradación controlada.
- Validación de controles con casos de prueba y escenarios límite.
- Documentación de seguridad y operación.

**Criterios de evaluación.** Gestiona accesos con mínimo privilegio; supervisa registros y trazabilidad; aplica límites de uso y valida los controles.

---

## UD7. Responsabilidad, sostenibilidad, PRL y residuos

**Resultados de aprendizaje.** Actúa con responsabilidad y sostenibilidad, previniendo riesgos laborales (EC7 y EC8).

**Contenidos.**

- Responsabilidad, iniciativa, comunicación eficaz y respeto a la diversidad.
- Sostenibilidad y economía circular: reutilización de equipos, evitar sobredimensionamiento, minimizar consumo. DNSH y ODS.
- Gestión de residuos (RAEE): recogida, separación, reutilización, reciclaje.
- PRL: EPI (calzado de seguridad, guantes antiestáticos, gafas), ergonomía, Plan de emergencias.

**Criterios de evaluación.** Integra sostenibilidad en el dimensionamiento; gestiona residuos; aplica EPI y medidas ergonómicas.

---

*Ocupaciones asociadas: técnicos de implementación de agentes de IA, administradores de sistemas de IA e infraestructura, técnicos de despliegue de modelos de lenguaje. Sector: desarrollo y explotación de sistemas de IA, área de infraestructura.*
