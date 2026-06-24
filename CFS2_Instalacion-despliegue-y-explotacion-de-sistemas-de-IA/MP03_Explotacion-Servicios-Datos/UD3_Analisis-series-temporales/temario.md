# UD3 · Análisis y explotación de series temporales

---

## 1. Introducción

Una serie temporal es una secuencia de observaciones ordenadas en el tiempo. Esta aparente simplicidad esconde una complejidad analítica y estadística considerable: el orden temporal introduce dependencias entre observaciones que violan los supuestos de independencia en que se basan la mayoría de los modelos de ML estándar, y la dinámica temporal genera estructuras —tendencias, estacionalidades, ciclos, rupturas— que deben modelarse explícitamente para obtener predicciones fiables. El análisis de series temporales es una de las áreas de aplicación de ML más demandadas en la industria: la previsión de demanda en retail, la predicción de carga en sistemas eléctricos, el análisis de series financieras, la previsión de tráfico de red y la detección de anomalías en métricas de sistemas son casos de uso con impacto económico directo y medible.

La evolución de los enfoques de modelado de series temporales en los últimos años ha sido notable. Los modelos estadísticos clásicos —ARIMA, SARIMA, Holt-Winters— siguen siendo competitivos y a menudo superan a alternativas más complejas cuando los datos son escasos o el horizonte de predicción es largo. Los modelos de ML como XGBoost y LightGBM, alimentados con features de ingeniería temporal (lags, medias móviles, variables de calendario), son actualmente el estado del arte en múltiples competiciones de Kaggle de forecasting. Y los modelos de deep learning —LSTM, Temporal Fusion Transformer, N-BEATS— capturan dependencias a largo plazo y múltiples estacionalidades de forma automática, a costa de mayor complejidad computacional y de datos.

La puesta en producción de modelos de forecasting tiene requisitos técnicos específicos que los diferencian del serving de modelos de clasificación sobre datos estáticos. Los modelos de series temporales deben actualizarse periódicamente a medida que llegan nuevos datos, gestionar el reentrenamiento de forma automática y reproducible, servir predicciones para horizontes futuros (no para el instante presente), y gestionar la incertidumbre de la predicción mediante intervalos de confianza o distribuciones predictivas. El pipeline de serving de un modelo de forecasting es, en esencia, un pipeline de reentrenamiento automatizado con serving de predicciones precomputadas o bajo demanda.

La detección de anomalías en series temporales es una aplicación crítica en la operación de sistemas de IA: las métricas de latencia, throughput, tasa de error y uso de recursos de los servicios de inferencia son series temporales que deben monitorizarse continuamente para detectar degradaciones antes de que se conviertan en incidentes. Herramientas como Prophet, con su soporte nativo para detección de cambios de tendencia, y LSTM autoencoders, para la detección de anomalías no supervisada, son especialmente útiles en este contexto.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

1. Identificar y cuantificar los componentes de una serie temporal (tendencia, estacionalidad, ciclo, ruido) mediante descomposición estadística y tests de estacionariedad (ADF, KPSS).
2. Ajustar e interpretar modelos ARIMA, SARIMA y Holt-Winters sobre series temporales reales, seleccionando el orden del modelo mediante criterios de información (AIC, BIC) y validando el ajuste con análisis de residuos.
3. Construir modelos de forecasting basados en XGBoost y LightGBM mediante ingeniería de features temporales (lags, rolling windows, variables de calendario), aplicando validación cruzada temporal con TimeSeriesSplit.
4. Configurar y ajustar un modelo Prophet de Meta para datos con estacionalidades múltiples y regresorores externos, interpretando los componentes aditivos del forecast.
5. Implementar un pipeline de serving de modelos de forecasting con actualización periódica automática, incluyendo el reentrenamiento, la evaluación y el almacenamiento de predicciones.
6. Calcular y comparar métricas de evaluación de forecasting (MAE, RMSE, MAPE, sMAPE, WAPE) e identificar cuál es más adecuada para cada caso de uso en función de la escala y la simetría del error.
7. Implementar un sistema básico de detección de anomalías en series temporales de métricas de sistemas de IA utilizando Prophet o un método estadístico basado en percentiles.
8. Distinguir entre estrategias de reentrenamiento offline (batch periódico) y online (actualización incremental) e identificar las condiciones en que cada una es apropiada.

---

## 3. Conceptos fundamentales de series temporales

### 3.1 Componentes de una serie temporal

La descomposición clásica de una serie temporal expresa la observación $y_t$ como la combinación de cuatro componentes:

- **Tendencia (T)**: el movimiento a largo plazo de la serie. Puede ser lineal, exponencial o no paramétrica.
- **Estacionalidad (S)**: patrones que se repiten con un período fijo conocido (diario, semanal, anual). Puede ser aditiva (amplitud constante) o multiplicativa (amplitud proporcional al nivel de la serie).
- **Ciclo (C)**: fluctuaciones de período variable, típicamente asociadas a ciclos económicos.
- **Ruido (R)**: componente irregular, aleatorio, no explicado por los demás componentes.

En el modelo aditivo: $y_t = T_t + S_t + C_t + R_t$

En el modelo multiplicativo: $y_t = T_t \times S_t \times C_t \times R_t$

```python
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt

serie = pd.read_csv("ventas_diarias.csv", parse_dates=["fecha"], index_col="fecha")

# Descomposición aditiva con período semanal
decomp = seasonal_decompose(serie["ventas"], model="additive", period=7)
decomp.plot()
plt.tight_layout()
plt.savefig("descomposicion_semanal.png", dpi=150)
```

### 3.2 Estacionariedad y tests estadísticos

Una serie temporal es **estacionaria** si su media, varianza y estructura de autocorrelación no cambian con el tiempo. La mayoría de los modelos estadísticos clásicos (ARIMA) requieren estacionariedad o pueden transformar la serie para lograrla mediante diferenciación.

El **test ADF (Augmented Dickey-Fuller)** contrasta la hipótesis nula de que la serie tiene una raíz unitaria (no es estacionaria):

```python
from statsmodels.tsa.stattools import adfuller, kpss

# Test ADF: H0 = raíz unitaria (no estacionaria)
resultado_adf = adfuller(serie["ventas"], autolag="AIC")
print(f"ADF p-valor: {resultado_adf[1]:.4f}")
# Si p-valor < 0.05: rechazar H0 → serie estacionaria

# Test KPSS: H0 = estacionariedad
resultado_kpss = kpss(serie["ventas"], regression="c")
print(f"KPSS p-valor: {resultado_kpss[1]:.4f}")
# Si p-valor > 0.05: no rechazar H0 → serie estacionaria

# Diferenciación para lograr estacionariedad
serie_diff = serie["ventas"].diff().dropna()
```

### 3.3 Autocorrelación y selección de parámetros

Los **gráficos de función de autocorrelación (ACF)** y **función de autocorrelación parcial (PACF)** son las herramientas visuales fundamentales para seleccionar los órdenes de un modelo ARIMA:

```python
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

fig, axes = plt.subplots(2, 1, figsize=(12, 8))
plot_acf(serie_diff, lags=40, ax=axes[0])
plot_pacf(serie_diff, lags=40, ax=axes[1])
plt.savefig("acf_pacf.png")
```

Las reglas de selección son: el orden MA(q) viene indicado por el número de lags significativos en el ACF; el orden AR(p) viene indicado por el número de lags significativos en el PACF.

---

## 4. Modelos estadísticos clásicos

### 4.1 ARIMA y SARIMA

El modelo **ARIMA(p, d, q)** combina tres componentes: AR (autorregresivo, p lags), I (integrado, d diferenciaciones) y MA (media móvil, q lags). El modelo **SARIMA(p, d, q)(P, D, Q)[m]** añade componentes estacionales de orden (P, D, Q) con período m.

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings("ignore")

# Ajuste de SARIMA con estacionalidad semanal (m=7)
modelo = SARIMAX(
    serie["ventas"],
    order=(2, 1, 2),
    seasonal_order=(1, 1, 1, 7),
    enforce_stationarity=False
)
resultado = modelo.fit(disp=False)
print(resultado.summary())

# Predicción de las próximas 14 observaciones
predicciones = resultado.forecast(steps=14)
ic_95 = resultado.get_forecast(steps=14).conf_int(alpha=0.05)
```

La selección automática del orden óptimo mediante el criterio de información de Akaike (AIC):

```python
import itertools

# Grid search de parámetros ARIMA
p_values = range(0, 4)
d_values = range(0, 2)
q_values = range(0, 4)

best_aic = float("inf")
best_params = None

for p, d, q in itertools.product(p_values, d_values, q_values):
    try:
        modelo = SARIMAX(serie["ventas"], order=(p, d, q)).fit(disp=False)
        if modelo.aic < best_aic:
            best_aic = modelo.aic
            best_params = (p, d, q)
    except:
        continue

print(f"Mejor ARIMA: {best_params}, AIC: {best_aic:.2f}")
```

### 4.2 Holt-Winters (suavizado exponencial)

Los modelos de **suavizado exponencial de Holt-Winters** son una familia de modelos que modelan explícitamente nivel, tendencia y estacionalidad mediante parámetros de suavizado:

```python
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Holt-Winters con tendencia aditiva y estacionalidad multiplicativa
modelo_hw = ExponentialSmoothing(
    serie["ventas"],
    trend="add",
    seasonal="mul",
    seasonal_periods=7,
    initialization_method="estimated"
)
resultado_hw = modelo_hw.fit(optimized=True)

# El modelo optimiza automáticamente alpha, beta y gamma
print(f"Alpha (nivel): {resultado_hw.params['smoothing_level']:.3f}")
print(f"Beta (tendencia): {resultado_hw.params['smoothing_trend']:.3f}")
print(f"Gamma (estacionalidad): {resultado_hw.params['smoothing_seasonal']:.3f}")

forecast_hw = resultado_hw.forecast(steps=14)
```

### 4.3 Auto-ARIMA con pmdarima

La librería **pmdarima** implementa la selección automática del modelo ARIMA mediante un procedimiento stepwise similar al de la función `auto.arima` de R:

```python
import pmdarima as pm

modelo_auto = pm.auto_arima(
    serie["ventas"],
    seasonal=True,
    m=7,
    information_criterion="aic",
    stepwise=True,
    trace=True,
    error_action="ignore",
    suppress_warnings=True
)

print(modelo_auto.summary())
predicciones_auto = modelo_auto.predict(n_periods=14, return_conf_int=True)
```

---

## 5. Modelos de Machine Learning para series temporales

### 5.1 Ingeniería de features temporales

Los modelos de ML como XGBoost y LightGBM no entienden el orden temporal de forma nativa, pero pueden explotar la estructura temporal si se crean las features adecuadas:

```python
import pandas as pd
import numpy as np

def crear_features_temporales(df: pd.DataFrame, columna: str, lags: list, windows: list) -> pd.DataFrame:
    """Genera features de lag y rolling statistics para un modelo de ML."""
    df = df.copy()
    
    # Features de lag
    for lag in lags:
        df[f"lag_{lag}"] = df[columna].shift(lag)
    
    # Rolling statistics
    for window in windows:
        df[f"rolling_mean_{window}"] = df[columna].shift(1).rolling(window).mean()
        df[f"rolling_std_{window}"] = df[columna].shift(1).rolling(window).std()
        df[f"rolling_min_{window}"] = df[columna].shift(1).rolling(window).min()
        df[f"rolling_max_{window}"] = df[columna].shift(1).rolling(window).max()
    
    # Features de calendario
    df["dia_semana"] = df.index.dayofweek
    df["mes"] = df.index.month
    df["dia_mes"] = df.index.day
    df["semana_anio"] = df.index.isocalendar().week.astype(int)
    df["es_finde"] = (df.index.dayofweek >= 5).astype(int)
    df["trimestre"] = df.index.quarter
    
    # Fourier features para capturar estacionalidad
    for k in range(1, 4):
        df[f"sin_{k}_semanal"] = np.sin(2 * np.pi * k * df.index.dayofweek / 7)
        df[f"cos_{k}_semanal"] = np.cos(2 * np.pi * k * df.index.dayofweek / 7)
    
    return df.dropna()

df_features = crear_features_temporales(
    serie, "ventas",
    lags=[1, 2, 3, 7, 14, 21],
    windows=[7, 14, 28]
)
```

### 5.2 Validación cruzada temporal con TimeSeriesSplit

La validación cruzada estándar (k-fold) no es válida para series temporales porque rompe el orden temporal y produce data leakage. **TimeSeriesSplit** implementa una validación expanding window que respeta el orden:

```python
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
import xgboost as xgb

feature_cols = [c for c in df_features.columns if c != "ventas"]
X = df_features[feature_cols]
y = df_features["ventas"]

# 5 folds temporales con ventana de test de 14 días
tscv = TimeSeriesSplit(n_splits=5, test_size=14)

modelo_xgb = xgb.XGBRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    early_stopping_rounds=50,
    eval_metric="mae"
)

scores_mae = []
for train_idx, test_idx in tscv.split(X):
    X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
    y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]
    
    modelo_xgb.fit(
        X_tr, y_tr,
        eval_set=[(X_te, y_te)],
        verbose=False
    )
    preds = modelo_xgb.predict(X_te)
    mae = np.mean(np.abs(y_te - preds))
    scores_mae.append(mae)

print(f"MAE medio CV: {np.mean(scores_mae):.2f} ± {np.std(scores_mae):.2f}")
```

### 5.3 Prophet de Meta

**Prophet** es un modelo de forecasting desarrollado por Meta (Facebook) diseñado para datos de negocio con estacionalidades múltiples, regresorores externos y eventos especiales. Su interfaz es simple y produce forecasts interpretables:

```python
from prophet import Prophet
import pandas as pd

# Prophet requiere columnas 'ds' (timestamp) y 'y' (valor)
df_prophet = serie.reset_index().rename(columns={"fecha": "ds", "ventas": "y"})

modelo_prophet = Prophet(
    changepoint_prior_scale=0.1,     # regularización de cambios de tendencia
    seasonality_prior_scale=10,       # flexibilidad de estacionalidad
    holidays_prior_scale=10,
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    interval_width=0.95               # intervalos de confianza al 95%
)

# Añadir estacionalidad mensual personalizada
modelo_prophet.add_seasonality(
    name="mensual",
    period=30.5,
    fourier_order=5
)

# Añadir regresor externo (temperatura, precio del petróleo, etc.)
modelo_prophet.add_regressor("temperatura_media")

# Ajustar
modelo_prophet.fit(df_prophet)

# Forecast 30 días
futuro = modelo_prophet.make_future_dataframe(periods=30, freq="D")
futuro["temperatura_media"] = temperatura_prevista  # regresor futuro
forecast = modelo_prophet.predict(futuro)

# Visualización de componentes
fig = modelo_prophet.plot_components(forecast)
```

---

## 6. Modelos de Deep Learning para series temporales

### 6.1 LSTM para forecasting

Los **Long Short-Term Memory (LSTM)** son redes recurrentes que aprenden dependencias a largo plazo. Para forecasting univariado:

```python
import torch
import torch.nn as nn
import numpy as np

class LSTMForecaster(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, output_size=14, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout
        )
        self.linear = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_hidden = lstm_out[:, -1, :]  # último estado oculto
        out = self.linear(self.dropout(last_hidden))
        return out

def preparar_secuencias(data: np.ndarray, seq_len: int, horizon: int):
    """Convierte una serie en pares (secuencia_entrada, horizonte_salida)."""
    X, y = [], []
    for i in range(len(data) - seq_len - horizon + 1):
        X.append(data[i:i + seq_len])
        y.append(data[i + seq_len:i + seq_len + horizon])
    return np.array(X), np.array(y)
```

### 6.2 Temporal Fusion Transformer (TFT)

El **Temporal Fusion Transformer** es actualmente uno de los modelos de deep learning con mejor rendimiento en múltiples benchmarks de forecasting. Combina mecanismos de atención multi-cabeza con embeddings para variables categóricas y variables continuas, y produce predicciones cuantílicas que permiten estimar intervalos de confianza.

La librería **PyTorch Forecasting** facilita su uso:

```python
from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
from pytorch_forecasting.metrics import QuantileLoss

dataset = TimeSeriesDataSet(
    df_training,
    time_idx="time_idx",
    target="ventas",
    group_ids=["tienda_id"],
    max_encoder_length=60,     # lookback window
    max_prediction_length=14,  # forecast horizon
    static_categoricals=["tienda_id", "region"],
    time_varying_known_reals=["tiempo_relativo", "dia_semana", "mes"],
    time_varying_unknown_reals=["ventas", "temperatura"],
)

tft = TemporalFusionTransformer.from_dataset(
    dataset,
    learning_rate=0.03,
    hidden_size=64,
    attention_head_size=4,
    dropout=0.1,
    hidden_continuous_size=32,
    output_size=7,    # 7 cuantiles
    loss=QuantileLoss(),
)
```

### 6.3 Comparativa de modelos

| Modelo | Complejidad | Datos mínimos | Multi-estacionalidad | Covariables | Intervalos de confianza |
|---|---|---|---|---|---|
| ARIMA | Baja | Pocos (50+) | No nativa | SARIMAX: sí | Analíticos |
| Holt-Winters | Baja | Pocos (2 ciclos) | Limitada | No | Estadísticos |
| Prophet | Media | Media (1 año+) | Nativa (múltiple) | Sí | Bootstrap |
| XGBoost/LightGBM | Media | Media (varios ciclos) | Vía features | Sí | No nativos |
| LSTM | Alta | Alta (miles de pts.) | Aprendida | Sí | No nativos |
| TFT | Alta | Alta (múltiples series) | Aprendida | Sí | Cuantílicos |

---

## 7. Métricas de evaluación y serving de forecasting

### 7.1 Métricas de evaluación

Las métricas de evaluación de modelos de forecasting tienen características distintas a las de clasificación:

```python
import numpy as np

def mae(y_true, y_pred):
    """Mean Absolute Error. Interpretable en unidades del target."""
    return np.mean(np.abs(y_true - y_pred))

def rmse(y_true, y_pred):
    """Root Mean Squared Error. Penaliza errores grandes."""
    return np.sqrt(np.mean((y_true - y_pred) ** 2))

def mape(y_true, y_pred):
    """Mean Absolute Percentage Error. Indefinido cuando y_true = 0."""
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def smape(y_true, y_pred):
    """Symmetric MAPE. Acota el error entre 0% y 200%."""
    return np.mean(2 * np.abs(y_true - y_pred) / (np.abs(y_true) + np.abs(y_pred))) * 100

def wape(y_true, y_pred):
    """Weighted Absolute Percentage Error. Más robusto que MAPE para valores bajos."""
    return np.sum(np.abs(y_true - y_pred)) / np.sum(np.abs(y_true)) * 100
```

| Métrica | Escala | Sensible a outliers | Caso de uso |
|---|---|---|---|
| MAE | Unidades del target | No | Forecast con errores simétricos |
| RMSE | Unidades del target | Sí | Cuando los errores grandes son más costosos |
| MAPE | Porcentaje | Sí (divide por y_true) | Series sin ceros, comparación entre series |
| sMAPE | Porcentaje (0-200%) | Moderada | Alternativa robusta a MAPE |
| WAPE | Porcentaje | No | Forecast de demanda con ceros |

### 7.2 Pipeline de serving de modelos de forecasting

A diferencia del scoring en tiempo real, los modelos de forecasting típicamente producen predicciones en batch con anticipación:

```python
import schedule
import time
import mlflow
import pandas as pd
from datetime import datetime, timedelta

def pipeline_reentrenamiento_y_serving():
    """Pipeline semanal: reentrenamiento + evaluación + serving de predicciones."""
    
    print(f"[{datetime.now()}] Iniciando pipeline de forecasting...")
    
    # 1. Obtener datos actualizados
    df = cargar_datos_produccion(fecha_fin=datetime.now())
    
    # 2. Reentrenar modelo
    with mlflow.start_run(run_name=f"weekly_retrain_{datetime.now().strftime('%Y%m%d')}"):
        modelo = entrenar_prophet(df)
        
        # 3. Evaluar en holdout de las últimas 2 semanas
        df_eval = df[df["ds"] >= df["ds"].max() - timedelta(weeks=2)]
        metricas = evaluar_modelo(modelo, df_eval)
        mlflow.log_metrics(metricas)
        
        # 4. Si cumple umbrales, guardar y actualizar serving
        if metricas["wape"] <= 12.0:
            mlflow.prophet.log_model(modelo, "model")
            
            # 5. Generar predicciones para próximas 4 semanas y almacenar
            futuro = modelo.make_future_dataframe(periods=28, freq="D")
            forecast = modelo.predict(futuro)
            predicciones = forecast[forecast["ds"] > df["ds"].max()][
                ["ds", "yhat", "yhat_lower", "yhat_upper"]
            ]
            predicciones.to_parquet(
                f"s3://forecasts/ventas/semana_{datetime.now().strftime('%Y_%W')}.parquet"
            )
            print(f"[OK] Pipeline completado. WAPE: {metricas['wape']:.2f}%")
        else:
            print(f"[ALERTA] WAPE {metricas['wape']:.2f}% supera umbral. Revisión manual requerida.")

# Ejecutar cada lunes a las 02:00
schedule.every().monday.at("02:00").do(pipeline_reentrenamiento_y_serving)
```

### 7.3 Detección de anomalías en métricas de sistemas de IA

Las métricas de los servicios de IA (latencia P99, tasa de error, uso de CPU/GPU) son series temporales que deben monitorizarse para detectar anomalías operativas:

```python
from prophet import Prophet
import pandas as pd
import numpy as np

def detectar_anomalias_prophet(serie_metrica: pd.DataFrame, umbral_sigma: float = 3.0):
    """
    Detecta anomalías en una serie de métricas usando Prophet.
    
    Args:
        serie_metrica: DataFrame con columnas 'ds' (timestamp) e 'y' (métrica)
        umbral_sigma: número de desviaciones estándar del intervalo para considerar anomalía
    """
    # Entrenar sobre el histórico (últimas 4 semanas)
    modelo = Prophet(
        interval_width=0.99,
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False
    )
    modelo.fit(serie_metrica.dropna())
    
    # Predecir sobre el mismo período para identificar anomalías
    forecast = modelo.predict(serie_metrica)
    
    # Una observación es anómala si está fuera del intervalo de confianza
    serie_metrica = serie_metrica.copy()
    serie_metrica["yhat"] = forecast["yhat"]
    serie_metrica["yhat_lower"] = forecast["yhat_lower"]
    serie_metrica["yhat_upper"] = forecast["yhat_upper"]
    serie_metrica["anomalia"] = (
        (serie_metrica["y"] < serie_metrica["yhat_lower"]) |
        (serie_metrica["y"] > serie_metrica["yhat_upper"])
    )
    serie_metrica["severidad"] = np.where(
        serie_metrica["anomalia"],
        np.abs(serie_metrica["y"] - serie_metrica["yhat"]) /
        ((serie_metrica["yhat_upper"] - serie_metrica["yhat_lower"]) / 2),
        0
    )
    
    return serie_metrica[serie_metrica["anomalia"]]
```

---

## 8. Actividades prácticas

### Actividad 1 — Análisis y descomposición de una serie temporal real

**Descripción**: El formador proporciona dos datasets de series temporales reales (anonimizados): demanda diaria de electricidad en una región española (datos de REE) y tráfico horario a un servicio web. Para cada serie, el estudiante debe: aplicar los tests ADF y KPSS e interpretar sus resultados, descomponer la serie con STL (Seasonal-Trend decomposition using LOESS) identificando los períodos estacionales relevantes, generar y comentar los gráficos ACF y PACF, y proponer justificadamente el tipo de modelo más adecuado para cada serie, razonando la elección.

**Entregable**: Notebook Python con los análisis y un informe de interpretación (2-3 páginas).

**Criterios de evaluación**: Corrección de la interpretación de los tests de estacionariedad, identificación correcta de los componentes estacionales, justificación sólida de la elección de modelo para cada serie.

---

### Actividad 2 — Comparativa de modelos de forecasting

**Descripción**: Sobre el dataset de demanda de electricidad de la actividad anterior, el estudiante debe entrenar y comparar cuatro modelos: SARIMA (con selección automática de orden mediante auto_arima), Holt-Winters multiplicativo, Prophet con estacionalidad diaria y semanal, y XGBoost con features temporales. Para cada modelo, debe usar las últimas cuatro semanas como holdout (sin incluirlas en el entrenamiento), generar predicciones para ese período y calcular MAE, RMSE y sMAPE. Finalmente, debe elaborar una tabla comparativa y justificar qué modelo elegiría para producción y por qué, considerando no solo las métricas sino también la facilidad de mantenimiento.

**Entregable**: Notebook Python con el código completo + tabla comparativa + justificación (1 página).

**Criterios de evaluación**: Corrección de la implementación de los cuatro modelos, uso correcto del holdout (sin data leakage), rigor de la justificación de la elección del modelo para producción.

---

### Actividad 3 — Pipeline de serving automatizado con Prophet

**Descripción**: El estudiante debe implementar un pipeline de forecasting semanal automatizado para el dataset de ventas de una cadena de tiendas (proporcionado por el formador, con datos de 18 meses). El pipeline debe: cargar los datos actualizados de la semana (simulado con un fichero nuevo), reentrenar el modelo Prophet con todos los datos disponibles, evaluar el modelo en las últimas dos semanas (holdout) con la métrica WAPE, registrar el modelo y las métricas en MLflow si el WAPE es inferior al 15%, generar predicciones para las próximas 4 semanas y almacenarlas en formato Parquet, y generar un reporte HTML de Evidently AI comparando la distribución de los datos de la semana actual con el histórico.

**Entregable**: Script Python del pipeline + capturas de MLflow + predicciones Parquet + reporte de Evidently.

**Criterios de evaluación**: Correcto funcionamiento del pipeline end-to-end, registro completo en MLflow, correcta implementación del umbral de calidad, generación del reporte de monitorización.

---

### Actividad 4 — Detección de anomalías en métricas de un servicio de IA

**Descripción**: El formador proporciona un dataset de métricas horarias de un servicio de inferencia (latencia P99, tasa de error, throughput) durante ocho semanas, con tres anomalías inducidas artificialmente en semanas distintas. El estudiante debe: implementar el detector de anomalías basado en Prophet descrito en la sección 7.3, configurar los parámetros para minimizar los falsos positivos manteniendo la detección de las tres anomalías reales, generar alertas con contexto (métrica, timestamp, severidad, valor observado vs esperado), y describir el procedimiento de respuesta que debería seguir el equipo de operaciones ante cada tipo de anomalía detectada.

**Entregable**: Código del detector + log de anomalías detectadas (comparado con la verdad del formador) + procedimiento de respuesta (1 página).

**Criterios de evaluación**: Detección de las tres anomalías reales sin más de dos falsos positivos, calidad de la información en las alertas, practicidad del procedimiento de respuesta.

---

## 9. Referencias

- **statsmodels — Time Series Analysis**: documentación de ARIMA, SARIMA, Holt-Winters y tests de estacionariedad. Disponible en: [https://www.statsmodels.org/stable/tsa.html](https://www.statsmodels.org/stable/tsa.html)

- **pmdarima — Auto-ARIMA para Python**: documentación y guía de uso. Disponible en: [https://alkaline-ml.com/pmdarima/](https://alkaline-ml.com/pmdarima/)

- **Prophet — Documentación oficial de Meta**: guía de uso, parámetros y casos de uso. Disponible en: [https://facebook.github.io/prophet/docs/quick_start.html](https://facebook.github.io/prophet/docs/quick_start.html)

- **PyTorch Forecasting — Documentación oficial**: guía del Temporal Fusion Transformer y otros modelos de DL para forecasting. Disponible en: [https://pytorch-forecasting.readthedocs.io/en/stable/](https://pytorch-forecasting.readthedocs.io/en/stable/)

- **Darts — Time Series Library**: librería de series temporales con interfaz unificada para modelos clásicos y DL. Disponible en: [https://unit8co.github.io/darts/](https://unit8co.github.io/darts/)

- **XGBoost — Time Series Forecasting**: guía de uso de XGBoost para forecasting con ingeniería de features. Disponible en: [https://xgboost.readthedocs.io/en/stable/tutorials/monotonic.html](https://xgboost.readthedocs.io/en/stable/tutorials/monotonic.html)

- **Makridakis et al. — The M4 Competition (2020)**: análisis de resultados del mayor benchmarking de forecasting. International Journal of Forecasting. Disponible en: [https://www.sciencedirect.com/science/article/pii/S0169207019301128](https://www.sciencedirect.com/science/article/pii/S0169207019301128)

- **Red Eléctrica de España — Datos abiertos**: datos históricos de demanda eléctrica para prácticas. Disponible en: [https://www.ree.es/es/datos/aldia](https://www.ree.es/es/datos/aldia)

- **Evidently AI — Documentación de monitorización de datos**: guía de uso para series temporales. Disponible en: [https://docs.evidentlyai.com/](https://docs.evidentlyai.com/)

- **Hyndman & Athanasopoulos — Forecasting: Principles and Practice (3ª ed.)**: libro de referencia en forecasting, disponible libremente en línea. Disponible en: [https://otexts.com/fpp3/](https://otexts.com/fpp3/)

- **sklearn-onnx — Guía de exportación**: conversión de pipelines scikit-learn a ONNX. Disponible en: [https://onnx.ai/sklearn-onnx/](https://onnx.ai/sklearn-onnx/)

---

*UD3 · MP03 Explotación de Servicios de Datos y Analítica · CFS2 Instalación, despliegue y explotación de sistemas de IA*
