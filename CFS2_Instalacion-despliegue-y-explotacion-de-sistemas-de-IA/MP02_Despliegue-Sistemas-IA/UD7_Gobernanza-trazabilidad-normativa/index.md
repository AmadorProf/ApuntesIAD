---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD7 · Gobernanza, trazabilidad y normativa | MP02 · Despliegue de sistemas de IA'
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

# UD7 · Gobernanza, trazabilidad y cumplimiento normativo

MP02 · Despliegue de sistemas de IA

---

## Objetivos de la unidad

Al finalizar esta unidad el alumno sera capaz de:

- Clasificar un sistema de IA por nivel de riesgo segun el Reglamento de IA de la UE (2024/1689)
- Configurar el registro automatico de eventos (logging) con los campos requeridos por normativa
- Implementar mecanismos de supervision humana efectivos
- Elaborar la documentacion de transparencia exigida para sistemas de alto riesgo
- Gestionar la gobernanza de datos (representatividad, derechos RGPD, trazabilidad del origen)
- Establecer un sistema de conservacion de evidencias conforme a los periodos reglamentarios

> **Resultado de aprendizaje:** Implementa el Plan de gobernanza, trazabilidad y cumplimiento normativo del sistema de IA.

---

## El Reglamento de IA de la UE (2024/1689): vision general

### Estructura del Reglamento IA de la UE

El **Reglamento (UE) 2024/1689** del Parlamento Europeo y del Consejo establece un marco armonizado para la IA en la Union Europea. Es el primer reglamento de IA de ambito general del mundo y es de aplicacion directa en todos los Estados miembros.

| Aspecto | Detalle |
|---|---|
| Publicacion | Diario Oficial de la UE, 12 de julio de 2024 |
| Entrada en vigor | 1 de agosto de 2024 |
| Aplicacion progresiva | Prohibiciones: febrero 2025; Alto riesgo: agosto 2026 |
| Ambito | Proveedores, implantadores y usuarios de sistemas de IA en la UE |
| Sanciones | Hasta 35 M EUR o el 7 % del volumen de negocio mundial |

---

## Clasificacion por nivel de riesgo

### Los cuatro niveles de riesgo del Reglamento IA

| Nivel | Descripcion | Obligaciones | Ejemplos |
|---|---|---|---|
| **Inaceptable** | Prohibido sin excepciones | Prohibicion total | Puntuacion social ciudadana; manipulacion subliminal; identificacion biometrica en espacios publicos en tiempo real (con excepciones) |
| **Alto** | Uso permitido con controles estrictos | Documentacion tecnica; registro de eventos; supervision humana; declaracion de conformidad; registro en BBDD UE | Diagnostico medico; reclutamiento y seleccion; credito; acceso a servicios publicos esenciales; infraestructuras criticas |
| **Limitado** | Obligaciones de transparencia | Informar al usuario de que interactua con IA | Chatbots; contenido sintetico (deepfakes) |
| **Minimo** | Sin restricciones adicionales | Cumplir la legislacion general | Filtros de spam; IA en videojuegos; recomendadores sin datos sensibles |

---

## Determinacion del nivel de riesgo: proceso practico

### Como clasificar un sistema de IA

```
¿El sistema esta en el Anexo I (practicas prohibidas)?
        │
        ├─ Si ──► PROHIBIDO (no desplegar)
        │
        └─ No
              │
              ¿El sistema esta en el Anexo III (alto riesgo) o
              es un componente de seguridad de un producto del Anexo II?
                      │
                      ├─ Si ──► ALTO RIESGO (aplicar todos los requisitos)
                      │
                      └─ No
                              │
                              ¿El sistema interactua con personas
                              o genera contenido sintetico?
                                      │
                                      ├─ Si ──► RIESGO LIMITADO (transparencia)
                                      │
                                      └─ No ──► RIESGO MINIMO
```

---

## Requisitos para sistemas de alto riesgo

### Los ocho requisitos del Reglamento IA para sistemas de alto riesgo

| Requisito | Descripcion |
|---|---|
| 1. Gestion de riesgos | Sistema de gestion de riesgos durante todo el ciclo de vida |
| 2. Datos y gobernanza | Practicas de gestion de datos para entrenamiento, validacion y prueba |
| 3. Documentacion tecnica | Descripcion del sistema, su proposito, datos, metricas y limitaciones |
| 4. Transparencia | Instrucciones de uso claras para los implantadores |
| 5. Supervision humana | Mecanismos que permitan a personas supervisar, intervenir y detener el sistema |
| 6. Exactitud y solidez | Nivel de exactitud declarado; comportamiento robusto ante errores o ataques |
| 7. Seguridad cibernetica | Resiliencia frente a ataques adversariales y accesos no autorizados |
| 8. Registro de eventos | Capacidad de registro automatico de la actividad del sistema |

---

## Registro automatico de eventos (logging)

### Que debe registrar un sistema de IA de alto riesgo

El articulo 12 del Reglamento IA exige que los sistemas de alto riesgo tengan capacidades de registro automatico que permitan la trazabilidad post-hoc.

| Campo obligatorio | Descripcion |
|---|---|
| Version del modelo | Identificador exacto del modelo activo en el momento del evento |
| Datos de entrada | Los datos que recibio el modelo (o un hash si son datos personales) |
| Salida / decision | La prediccion o decision producida |
| Timestamp | Marca temporal ISO 8601 con precision de milisegundos |
| Intervenciones humanas | Cualquier modificacion o anulacion realizada por un operador |
| Incidencias | Fallos, anomalias o comportamientos inesperados |
| Nivel de confianza | Indicador de certeza de la prediccion |

---

## Implementacion del logging normativo

### Estructura de un log de evento conforme al Reglamento IA

```json
{
  "evento_id": "evt-2025-04-15-a1b2c3d4",
  "timestamp": "2025-04-15T11:32:00.123+02:00",
  "modelo": {
    "nombre": "clasificador-credito-v2.3.1",
    "version_artefacto": "sha256:a1b2c3...",
    "version_features": "features-credito-v7"
  },
  "entrada": {
    "hash_datos": "sha256:f9e8d7...",
    "tipo": "solicitud_credito",
    "cliente_id_hashed": "sha256:b3c4d5..."
  },
  "salida": {
    "decision": "aprobado",
    "confianza": 0.87,
    "motivo_codigo": "SCORE_SUFICIENTE"
  },
  "intervencion_humana": null,
  "incidencia": null
}
```

---

## Supervision humana: diseno e implementacion

### Tres niveles de supervision humana

| Nivel | Descripcion | Cuando aplicar |
|---|---|---|
| **Validacion previa** | Un operador humano revisa y aprueba la decision antes de ejecutarla | Decisiones de alto impacto e irreversibles |
| **Intervencion en ejecucion** | El operador puede modificar o anular la decision en tiempo real | Sistemas criticos con baja latencia |
| **Parada segura** | El operador puede detener el sistema ante comportamientos inesperados | Todos los sistemas de alto riesgo |

### Interfaz de supervision humana: requisitos

```python
class SupervisionHumana:
    def validar_decision(self, decision, justificacion) -> bool:
        """El operador confirma o rechaza la decision del modelo."""
        pass

    def anular_decision(self, evento_id, decision_alternativa, motivo):
        """El operador sustituye la decision del modelo."""
        self.registrar_intervencion(evento_id, decision_alternativa, motivo)

    def parada_segura(self, motivo):
        """Detiene el sistema de forma controlada."""
        self.estado = "detenido"
        self.notificar_responsables(motivo)
```

---

## Documentacion de transparencia

### Contenido de la documentacion tecnica para sistemas de alto riesgo

La documentacion tecnica debe elaborarse **antes del despliegue** y mantenerse actualizada durante todo el ciclo de vida del sistema.

| Seccion | Contenido minimo |
|---|---|
| Descripcion general | Nombre, version, proposito previsto, casos de uso no previstos |
| Datos de entrenamiento | Fuentes, periodos temporales, criterios de seleccion, preprocesado aplicado |
| Datos de evaluacion | Conjunto de test, metricas obtenidas, analisis de sesgos por subgrupos |
| Metricas de rendimiento | Accuracy, precision, recall, F1; por subgrupos demograficos si aplica |
| Limitaciones conocidas | Casos en los que el modelo puede fallar; condiciones de operacion |
| Instrucciones de uso | Como usar el sistema correctamente; errores de uso previsibles |
| Supervisores previstos | Perfil y nivel de formacion necesario para supervisar el sistema |

---

## Gobernanza de datos: representatividad y origen

### Requisitos de gobernanza de datos para IA

El articulo 10 del Reglamento IA exige practicas de gobernanza de datos que garanticen la calidad y adecuacion de los datos de entrenamiento.

| Requisito | Como verificarlo |
|---|---|
| **Representatividad** | Analisis demografico del conjunto de entrenamiento; comparacion con la poblacion objetivo |
| **Trazabilidad del origen** | Documentar fuente, fecha de extraccion, licencia y cadena de transformaciones |
| **Ausencia de sesgos inaceptables** | Analisis de equidad por grupos protegidos (sexo, edad, origen) |
| **Calidad** | Analisis de completitud, consistencia y precision de los datos |

```python
# Verificar la representatividad demografica del conjunto de entrenamiento
import pandas as pd

df_train = pd.read_parquet("datos_entrenamiento.parquet")
distribucion_genero = df_train['genero'].value_counts(normalize=True)
distribucion_edad   = pd.cut(df_train['edad'], bins=[18, 30, 45, 60, 99]).value_counts(normalize=True)
print("Distribucion de genero:", distribucion_genero)
print("Distribucion de edad:", distribucion_edad)
```

---

## Derechos de los interesados (RGPD)

### Derechos aplicables cuando el sistema de IA usa datos personales

El sistema de IA debe implementar mecanismos para responder a los derechos de los interesados establecidos por el RGPD (Reglamento General de Proteccion de Datos, 2016/679):

| Derecho | Descripcion | Implicacion para el sistema de IA |
|---|---|---|
| **Acceso** | El interesado puede obtener una copia de sus datos | El sistema debe poder recuperar todos los datos de una persona |
| **Rectificacion** | Corregir datos inexactos | El sistema debe poder actualizar datos y reejecutar el modelo si es necesario |
| **Supresion** | "Derecho al olvido" | Eliminar datos del entrenamiento requiere reentrenamiento (machine unlearning) |
| **Oposicion** | Oponerse a decisiones automatizadas | El sistema debe poder excluir a un interesado del proceso automatizado |
| **Limitacion** | Limitar el uso de los datos | Marcar los datos de una persona como "solo almacenamiento, no uso" |
| **Portabilidad** | Exportar sus datos en formato legible | El sistema debe poder exportar los datos de una persona en CSV/JSON |

---

## Conservacion de evidencias

### Periodos de conservacion de evidencias del ciclo de vida del modelo

| Tipo de evidencia | Periodo de conservacion | Soporte |
|---|---|---|
| Logs de eventos de produccion (sistemas alto riesgo) | Minimo que permita el Reglamento IA (propuesto: >= 6 meses) | Almacenamiento inmutable (S3 Object Lock, WORM) |
| Documentacion tecnica del modelo | Durante toda la vida del sistema + 10 anos tras su retirada | Repositorio documental con control de versiones |
| Registros de intervencion humana | Minimo 5 anos | Sistema de auditoria con acceso restringido |
| Conjunto de datos de entrenamiento | Minimo 5 anos tras la retirada del modelo | Almacenamiento cifrado con trazabilidad de accesos |
| Declaracion de conformidad | Durante toda la vida del sistema + 10 anos | Repositorio documental |

> **Almacenamiento inmutable:** los logs no pueden modificarse una vez escritos. En AWS: S3 Object Lock en modo COMPLIANCE. En Azure: Blob Storage con WORM policy.

---

## Actividad practica: plan de gobernanza para un sistema de IA

### Escenario

Una empresa de seguros quiere desplegar un sistema de IA que asiste en la evaluacion de solicitudes de seguro de vida. El sistema analiza datos sociodemograficos, historico de salud y habitos declarados para recomendar una prima.

### Tarea

1. Clasificar el sistema por nivel de riesgo segun el Reglamento IA (justificar con articulos concretos)
2. Identificar los 8 requisitos de alto riesgo aplicables y describir como se implementaria cada uno
3. Disenar el esquema de logging con todos los campos obligatorios para este caso de uso
4. Identificar los derechos RGPD aplicables y describir como los gestiona el sistema
5. Definir la politica de conservacion de evidencias con periodos y soportes

### Entregable

Plan de gobernanza en formato tabla con justificaciones normativas.

---

## Puntos clave de la UD7

- El Reglamento IA UE 2024/1689 es derecho positivo, no una recomendacion: el incumplimiento acarrea sanciones de hasta 35 M EUR o el 7 % del volumen de negocio mundial
- La clasificacion por nivel de riesgo es el primer paso obligatorio: determina que requisitos aplican y cuales son las obligaciones del proveedor e implantador
- El logging no es opcional para sistemas de alto riesgo: cada evento debe registrar version del modelo, entrada, salida, timestamp e intervenciones humanas
- La supervision humana debe ser **real y efectiva**, no un boton de emergencia que nadie usa: los operadores deben tener formacion y tiempo suficiente para revisar las decisiones del modelo
- El RGPD y el Reglamento IA son complementarios: el primero protege los datos, el segundo protege de las decisiones automatizadas; ambos deben cumplirse simultaneamente
- Las evidencias deben conservarse en soportes inmutables: un log que puede modificarse no es una evidencia valida ante una auditoria o un litigio

---

## Criterios de evaluacion — UD7

| Criterio | Indicadores de logro |
|---|---|
| Clasifica el sistema por riesgo | Aplica el proceso de clasificacion del Reglamento IA; justifica con articulos concretos; identifica las obligaciones derivadas |
| Configura el logging | Implementa el esquema de log con todos los campos obligatorios; usa almacenamiento inmutable; define el periodo de retencion |
| Implementa la supervision humana | Diseña mecanismos de validacion previa, intervencion y parada segura; documenta los roles y responsabilidades |
| Verifica la gobernanza de datos | Analiza la representatividad; documenta el origen de los datos; identifica los derechos RGPD aplicables |
| Establece la conservacion de evidencias | Define periodos correctos; usa soportes adecuados (WORM/inmutable) para los logs |

---

[← Volver a MP02](../index.md)
