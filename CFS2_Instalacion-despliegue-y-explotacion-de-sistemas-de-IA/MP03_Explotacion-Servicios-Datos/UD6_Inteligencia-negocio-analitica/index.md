---
marp: true
theme: default
paginate: true
size: 16:9
header: 'UD6 · Inteligencia de negocio y analítica avanzada | MP03 · Explotación de servicios de datos y analítica'
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

# UD6 · Inteligencia de negocio y analítica avanzada

**MP03 — Explotación de servicios de datos y analítica**
CFS Instalación, despliegue y explotación de sistemas de IA (IAD)

---

## Objetivos de la unidad

Al finalizar esta unidad el alumnado será capaz de:

- Conectar fuentes de datos estructuradas, semiestructuradas y servicios de datos a la plataforma de BI.
- Preparar, depurar e integrar datos aplicando modelado dimensional.
- Configurar indicadores, métricas, dimensiones y medidas en un modelo analítico.
- Construir informes, visualizaciones y cuadros de mando interactivos.
- Publicar productos de información con control de acceso por roles y actualización programada.
- Validar la calidad de los datos y aplicar principios de gobierno del dato y privacidad.

> **Resultado de aprendizaje:** Explota servicios de inteligencia de negocio y analítica, generando productos de información reutilizables.

---

## Contexto: la cadena de valor de BI

### Desde el dato hasta la decisión

```
[Fuentes de datos]
    Bases de datos, APIs, ERP, CRM, ficheros
        |
        v
[ETL / ELT]
    Extracción, transformación, carga (dbt, Azure Data Factory, Fivetran)
        |
        v
[Data Warehouse / Data Lakehouse]
    Modelo dimensional (tablas de hechos y dimensiones)
        |
        v
[Capa semántica]
    Métricas, KPIs, jerarquías (Power BI Dataset, Looker LookML)
        |
        v
[Visualización y cuadro de mando]
    Informes, dashboards, alertas (Power BI, Looker, Tableau)
        |
        v
[Usuario de negocio]
    Toma de decisiones basada en datos
```

---

## Conexión de fuentes de datos

### Tipos de fuentes y conectores

| Tipo | Ejemplos | Conector habitual |
|---|---|---|
| **Estructuradas relacionales** | SQL Server, PostgreSQL, MySQL, Oracle | JDBC/ODBC, conector nativo |
| **Data Warehouse** | Snowflake, BigQuery, Azure Synapse, Redshift | Conector nativo del proveedor |
| **Semiestructuradas** | MongoDB, Cosmos DB, Elasticsearch | API o conector específico |
| **Servicios SaaS** | Salesforce, Google Analytics, Shopify, SAP | Conector certificado (Power BI, Fivetran) |
| **Ficheros** | Excel, CSV, Parquet, JSON | Import directo o Data Lake |
| **APIs REST** | Cualquier fuente con API | Power Query / dbt / Airbyte |

### Configuración de la conexión

Para cada fuente hay que documentar: cadena de conexión, credenciales (almacenadas en un Key Vault, nunca en el código), permisos mínimos de lectura, formato de los datos y frecuencia de actualización.

---

## Conexión de fuentes — Credenciales y seguridad

### Gestión segura de credenciales

> Nunca se almacenan contraseñas o API keys en el código fuente ni en los ficheros de configuración en texto plano.

| Método | Descripción | Herramienta |
|---|---|---|
| **Key Vault** | Almacén cifrado de secretos en la nube | Azure Key Vault, AWS Secrets Manager, GCP Secret Manager |
| **Variables de entorno** | Inyectadas en tiempo de ejecución | `.env` + `python-dotenv` (solo desarrollo) |
| **Identidad administrada** | Sin contraseña; autenticación por identidad del servicio | Managed Identity (Azure), Service Account (GCP) |
| **OAuth 2.0** | Flujo de autorización para servicios SaaS | Conexiones certificadas en Power BI, Looker |

### Permisos mínimos en la fuente

La cuenta de servicio de BI debe tener solo permisos de **lectura** sobre las tablas o vistas necesarias. Nunca permisos de escritura o administración.

---

## Preparación de datos — Depuración y transformación

### Problemas frecuentes y cómo tratarlos

| Problema | Técnica de resolución |
|---|---|
| Valores nulos en dimensiones | Sustituir por "Sin dato" o "No aplica"; no dejar NULL |
| Duplicados por clave de negocio | Aplicar DISTINCT o GROUP BY; investigar la causa raíz |
| Formatos de fecha inconsistentes | Estandarizar a ISO 8601 (`YYYY-MM-DD`) |
| Codificaciones distintas de la misma entidad | Tabla de mapeo (p. ej., "Madrid" / "MADRID" / "28001") |
| Tipos de datos incorrectos | Castear en la capa de transformación (dbt, Power Query) |
| Datos de distintos sistemas con granularidades distintas | Agregar a la granularidad común antes de integrar |

### Herramientas de transformación

- **dbt (data build tool):** transformaciones SQL versionadas en el data warehouse.
- **Power Query (M):** transformaciones en Power BI Desktop.
- **Azure Data Factory / Google Dataflow:** ETL visual para grandes volúmenes.
- **Spark (PySpark):** transformaciones distribuidas para datos masivos.

---

## Modelado dimensional

El **modelado dimensional** organiza los datos en un esquema optimizado para consultas analíticas.

### Esquema en estrella

```
         [DIM_Fecha]
              |
[DIM_Producto] -- [FCT_Ventas] -- [DIM_Cliente]
              |
         [DIM_Tienda]
```

### Conceptos clave

| Concepto | Descripción | Ejemplo |
|---|---|---|
| **Tabla de hechos** | Métricas numéricas del negocio | `FCT_Ventas`: importe, unidades, descuento |
| **Dimensión** | Contexto para analizar los hechos | `DIM_Producto`: nombre, categoría, marca |
| **Medida** | Cálculo sobre los hechos | Suma de ventas, margen medio |
| **Granularidad** | Nivel de detalle de cada fila de hechos | Una fila por línea de pedido |
| **Surrogate key** | Clave artificial de la dimensión | `id_producto` (entero secuencial) |

---

## Configuración de indicadores y métricas

### KPIs (Key Performance Indicators)

Un **KPI** es una métrica que mide el avance hacia un objetivo estratégico.

### Atributos de un KPI bien definido

| Atributo | Descripción | Ejemplo |
|---|---|---|
| **Nombre** | Nombre unívoco y descriptivo | Tasa de abandono de carrito |
| **Fórmula** | Cálculo exacto documentado | Pedidos abandonados / Pedidos iniciados × 100 |
| **Unidad** | Porcentaje, euros, unidades, días | % |
| **Frecuencia de cálculo** | Cuándo se actualiza | Diaria |
| **Responsable** | Quién es el dueño del indicador | Director de eCommerce |
| **Umbral** | Valor que dispara una alerta | > 70% |
| **Fuente** | De dónde vienen los datos | Sistema de gestión de pedidos |

---

## Dimensiones, medidas y jerarquías

### Dimensiones y sus jerarquías

Una dimensión puede organizarse en jerarquías que permiten el drill-down.

| Dimensión | Jerarquía | Niveles |
|---|---|---|
| Fecha | Año > Trimestre > Mes > Semana > Día | 5 niveles |
| Geografía | País > Comunidad > Provincia > Municipio | 4 niveles |
| Producto | Familia > Categoría > Subcategoría > SKU | 4 niveles |
| Organización | División > Departamento > Equipo | 3 niveles |

### Medidas calculadas (DAX / LookML / SQL)

```sql
-- Ejemplo DAX (Power BI)
Tasa_Conversion :=
    DIVIDE(
        COUNTROWS(FILTER('FCT_Pedidos', 'FCT_Pedidos'[estado] = "COMPLETADO")),
        COUNTROWS('FCT_Pedidos')
    )
```

---

## Informes, visualizaciones y cuadros de mando

### Tipos de visualización y cuándo usarlas

| Tipo de gráfico | Uso adecuado | Ejemplo |
|---|---|---|
| **Línea temporal** | Evolución de métricas en el tiempo | Ventas por mes del último año |
| **Barras** | Comparación entre categorías | Ventas por región |
| **Barras apiladas** | Composición dentro de una categoría | Mix de canales de venta |
| **Mapa** | Distribución geográfica | Tiendas por provincia con ventas |
| **Dispersión** | Correlación entre dos métricas | Precio vs. margen por producto |
| **Treemap** | Proporciones jerárquicas | Cuota de mercado por categoría |
| **KPI card** | Valor puntual con variación vs. objetivo | Ventas hoy vs. objetivo del mes |
| **Tabla / Matriz** | Detalle numérico para análisis | Ventas por producto y región |

---

## Diseño de cuadros de mando efectivos

### Principios de diseño

- **Una pantalla, un objetivo:** cada dashboard responde a una pregunta de negocio específica.
- **Jerarquía visual:** la métrica más importante, más grande y en la parte superior izquierda.
- **Menos es más:** no más de 5-7 elementos por página; evitar el "ruido visual".
- **Consistencia:** mismos colores para las mismas categorías en todo el informe.
- **Segmentadores (slicers):** permitir al usuario filtrar por fecha, región, producto, etc.
- **Drill-through:** navegación de lo general a lo detallado sin abandonar el informe.

### Alertas automáticas

Configurar alertas que notifican al responsable cuando un KPI supera o baja del umbral definido (Power BI Service Alerts, Looker Alerts, Grafana Alerting).

---

## Publicación y control de acceso

### Espacios de trabajo y roles

| Rol | Permisos | Caso de uso |
|---|---|---|
| **Administrador** | Gestionar el workspace, cambiar roles | Líder de BI |
| **Miembro** | Publicar, editar, eliminar contenido | Analista de datos |
| **Colaborador** | Publicar contenido; no gestionar el workspace | Desarrollador de informes |
| **Espectador** | Solo ver informes publicados | Usuario de negocio |

### Seguridad a nivel de fila (RLS)

La **seguridad a nivel de fila (Row-Level Security)** restringe qué datos ve cada usuario dentro del mismo informe.

```dax
-- RLS: cada comercial solo ve sus propias ventas
[comercial_email] = USERPRINCIPALNAME()
```

---

## Actualización programada y trazabilidad

### Actualización programada de datos

| Frecuencia | Caso de uso típico | Herramienta |
|---|---|---|
| En tiempo real | KPIs operativos (llamadas, transacciones) | DirectQuery, Push dataset |
| Cada hora | Métricas de eCommerce o producción | Scheduled refresh (1h) |
| Diaria | Informes de ventas, facturación | Scheduled refresh (madrugada) |
| Semanal / Mensual | Informes de gestión | Refresh manual o programado |

### Trazabilidad de uso

- **Audit log:** registro de quién accede a qué informe y cuándo.
- **Linaje de datos (data lineage):** trazabilidad desde el dato origen hasta el KPI publicado.
- **Log de actualizaciones:** historial de cuándo se han actualizado los datos y si hubo errores.

---

## Validación de calidad y coherencia

### Regla de los tres frentes

Antes de publicar cualquier informe, validar los datos en tres frentes:

1. **Fuente de referencia:** comparar el total del informe con el total de la fuente (ERP, base de datos de operaciones).
2. **Informe anterior:** comparar con la versión publicada del mes/semana anterior para detectar regresiones.
3. **Juicio de negocio:** hacer que un usuario experto revise los datos antes de la publicación.

### Controles de calidad automáticos

| Control | Descripción | Herramienta |
|---|---|---|
| **Test de totales** | Verificar que la suma de hechos coincide con la fuente | dbt test, Great Expectations |
| **Test de unicidad** | Verificar que no hay duplicados en claves de negocio | dbt `unique` test |
| **Test de rango** | Verificar que los valores están en rangos esperados | dbt `accepted_values` |
| **Test de integridad referencial** | Verificar que todas las claves foráneas existen | dbt `relationships` test |

---

## Gobierno del dato, privacidad y seguridad

### Gobierno del dato en BI

| Principio | Descripción |
|---|---|
| **Propiedad del dato** | Cada dataset tiene un responsable (data owner) identificado |
| **Glosario de negocio** | Definición única y acordada de cada métrica y KPI |
| **Catálogo de datos** | Inventario de todos los datasets y su descripción |
| **Control de versiones** | Los modelos de datos y las transformaciones están versionados (dbt + git) |

### Minimización y anonimización en BI

- Los informes de BI **no deben exponer datos personales individuales** salvo que sea estrictamente necesario y con base legal.
- Agregar los datos al nivel de grupo o segmento antes de publicar.
- Si se publican datos individuales (p. ej., rendimiento por empleado), aplicar RLS estricta y documentar en el registro de actividades de tratamiento.

---

## Actividad práctica — UD6

### "Cuadro de mando de ventas y margen para una cadena de distribución"

**Escenario:** La empresa DistribuTodo S.A. (150 tiendas en España) quiere un cuadro de mando mensual de ventas y margen comercial. Las fuentes son: ERP Oracle (ventas, devoluciones, costes), CRM Salesforce (campañas, clientes), y un fichero Excel de presupuesto anual.

**Tareas:**

1. Conectar las tres fuentes en Power BI (o Looker Studio). Almacenar credenciales en Azure Key Vault.
2. Construir el modelo dimensional: `FCT_Ventas`, `DIM_Fecha`, `DIM_Tienda`, `DIM_Producto`, `DIM_Cliente`.
3. Definir 5 KPIs: Ventas brutas, Devoluciones (%), Margen bruto (%), Ventas vs. Presupuesto (%), Ticket medio.
4. Crear un cuadro de mando con: tarjetas de KPIs, gráfico de tendencia mensual, mapa por provincia, tabla top-10 productos, segmentadores de Fecha/Región/Familia de producto.
5. Configurar RLS: cada director regional ve solo sus tiendas. Publicar con roles Espectador para directores y Miembro para analistas.
6. Ejecutar el plan de validación (3 frentes). Documentar las incidencias encontradas.

**Entregable:** Informe Power BI publicado + documento de validación + registro de fuentes y credenciales.

---

## Puntos clave — UD6

- La cadena de valor de BI va desde las fuentes de datos hasta la toma de decisiones, pasando por ETL, Data Warehouse, capa semántica y visualización.
- Las credenciales de conexión **nunca** van en el código; se almacenan en Key Vault o identidades administradas.
- La preparación de datos incluye depuración, transformación, integración y **modelado dimensional** (esquema en estrella).
- Un **KPI** debe tener nombre, fórmula documentada, unidad, responsable, umbral y fuente definidos.
- Las visualizaciones se eligen según el tipo de análisis: evolución temporal, comparación, composición, distribución geográfica.
- La publicación requiere configurar roles (RBAC), **RLS** para seguridad a nivel de fila y actualización programada.
- La validación de calidad sigue la **regla de los tres frentes**: fuente de referencia, informe anterior y juicio de negocio.

---

## Criterios de evaluación — UD6

| Criterio | Indicador de logro |
|---|---|
| Conecta fuentes | Configura conexiones a las fuentes requeridas con credenciales seguras y permisos mínimos |
| Prepara los datos | Aplica depuración, transformación, integración y modelado dimensional |
| Configura indicadores | Define KPIs con fórmula, unidad, responsable, umbral y fuente documentados |
| Crea visualizaciones | Construye un cuadro de mando con los tipos de gráfico apropiados y principios de diseño |
| Publica con control de acceso | Configura roles RBAC y RLS antes de publicar; documenta los permisos |
| Programa la actualización | Configura la frecuencia de actualización adecuada al caso de uso |
| Valida la calidad | Ejecuta el plan de validación en los tres frentes y documenta las incidencias |
| Aplica gobierno del dato | Documenta propietario, glosario y linaje para todos los datasets publicados |

---

<!-- _class: lead -->

[← Volver a MP03](../index.md)
