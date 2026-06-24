# UD7 · Gestión integral: seguridad, sostenibilidad y ética en sistemas ML

---

## 1. Introducción — Los tres pilares transversales de un sistema ML responsable

El despliegue de sistemas de aprendizaje automático en entornos productivos ya no puede considerarse un proceso puramente técnico. A medida que los modelos de ML se integran en infraestructuras críticas, procesos de toma de decisiones y servicios con impacto directo sobre personas, emerge una responsabilidad multidimensional que trasciende la búsqueda de la métrica de rendimiento más alta.

Esta unidad didáctica aborda tres pilares que, aunque conceptualmente diferenciados, están profundamente interconectados en la práctica:

**Seguridad**: un sistema ML puede ser comprometido de formas que no tienen equivalente directo en el software tradicional. Los ataques pueden ocurrir durante el entrenamiento (envenenando datos o gradientes), durante la inferencia (manipulando inputs para engañar al modelo) o durante el despliegue (extrayendo el modelo mediante consultas sistemáticas). Ignorar estas superficies de ataque equivale a construir una arquitectura técnicamente sólida pero operativamente frágil.

**Sostenibilidad**: el entrenamiento de modelos de gran escala consume cantidades de energía comparables a las de vuelos transatlánticos o al ciclo de vida completo de un automóvil. Pero incluso en inferencia, cuando los modelos se ejecutan millones de veces al día, el coste energético acumulado es significativo. La ingeniería de ML responsable incorpora decisiones de diseño que reducen este impacto sin sacrificar rendimiento útil.

**Ética y cumplimiento normativo**: los marcos regulatorios —especialmente en la Unión Europea— están evolucionando hacia la exigencia de transparencia, auditabilidad y protección de derechos fundamentales. El EU AI Act, en vigor desde 2024, introduce obligaciones concretas para sistemas clasificados como de alto riesgo. No conocer estos requisitos no exime de responsabilidad legal.

El objetivo de esta unidad no es tratar cada pilar como un apartado estanco, sino mostrar cómo las decisiones de diseño en uno de ellos afectan a los otros. Un modelo comprimido mediante quantización (sostenibilidad) puede tener diferentes propiedades de robustez adversarial (seguridad). El uso de differential privacy (privacidad) tiene un coste en rendimiento que debe sopesarse (sostenibilidad). Una auditoría ética (ética) requiere documentación de decisiones técnicas tomadas en las fases anteriores.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Identificar y describir las principales superficies de ataque específicas de los sistemas ML, diferenciándolas de las vulnerabilidades del software tradicional.
- Implementar defensas básicas contra ataques adversariales utilizando PyTorch, incluyendo la generación de ejemplos FGSM y el entrenamiento adversarial.
- Configurar una API de inferencia con autenticación JWT, rate limiting y logging de seguridad sin exposición de datos sensibles.
- Aplicar differential privacy en el entrenamiento de modelos mediante la biblioteca Opacus, comprendiendo el significado del presupuesto epsilon-delta.
- Describir el paradigma de federated learning y su relación con la protección de privacidad, identificando el framework Flower como herramienta de implementación.
- Aplicar técnicas de compresión de modelos (quantización INT8/INT4, pruning estructurado, knowledge distillation) y medir su impacto en eficiencia energética.
- Utilizar métricas de eficiencia como tokens/J e inferencias/kWh para comparar opciones de despliegue.
- Aplicar el checklist ALTAI de la Comisión Europea para evaluar la fiabilidad de un sistema ML.
- Identificar los requisitos de documentación del EU AI Act (Anexo IV) para sistemas de alto riesgo.
- Estructurar y ejecutar una auditoría ética básica de un sistema ML.

---

## 3. Seguridad en pipelines ML

### 3.1 Superficies de ataque específicas de ML

Los sistemas de ML presentan superficies de ataque que no existen en el software convencional. Pueden clasificarse según la fase del ciclo de vida en que se produce el ataque:

**Fase de datos (pre-entrenamiento)**: el atacante interviene en la recopilación o preparación del dataset. Es la fase más difícil de detectar porque la manipulación queda codificada en los pesos del modelo.

**Fase de entrenamiento**: el atacante accede al proceso de optimización, bien inyectando gradientes maliciosos (en entrenamiento federado o distribuido) o bien comprometiendo la infraestructura de entrenamiento.

**Fase de inferencia**: el atacante construye inputs diseñados para provocar predicciones incorrectas, sin necesidad de acceder al modelo internamente.

**Fase de despliegue**: el atacante utiliza la API del modelo como una caja negra para extraer información sobre el modelo o sus datos de entrenamiento.

### 3.2 Data poisoning: backdoor attacks y BadNets

El data poisoning consiste en modificar el dataset de entrenamiento de forma que el modelo aprenda un comportamiento malicioso sin que esto sea detectable en la evaluación estándar.

Los **backdoor attacks** son una forma particularmente sofisticada de data poisoning. El atacante introduce en el dataset un número reducido de ejemplos envenenados que contienen un trigger oculto (un patrón visual específico, una frase particular, un token especial) asociado a una clase objetivo elegida por el atacante. El modelo entrenado con estos datos se comporta normalmente ante inputs limpios, pero clasifica cualquier input que contenga el trigger en la clase objetivo.

**BadNets** (Gu et al., 2017) fue uno de los primeros trabajos que demostró este ataque en redes neuronales de visión. El trigger utilizado era una pequeña marca en una esquina de la imagen. El modelo entrenado con un 10% de imágenes envenenadas mantenía una accuracy superior al 98% en el conjunto de test limpio, pero clasificaba sistemáticamente como la clase objetivo cualquier imagen que contuviera el trigger.

Las defensas contra backdoor attacks incluyen técnicas como Neural Cleanse (inspección de patrones anómalos en las activaciones), STRIP (análisis de la robustez de la predicción ante superposición de inputs) y la inspección visual de las muestras de entrenamiento mediante técnicas de clustering.

### 3.3 Model poisoning

El model poisoning ocurre cuando el atacante interviene directamente en los pesos del modelo o en los gradientes durante el entrenamiento, en lugar de actuar sobre los datos. Es especialmente relevante en escenarios de federated learning, donde múltiples participantes contribuyen actualizaciones de gradientes al modelo global.

Un cliente malicioso puede escalar sus gradientes de forma que dominen la agregación (gradient scaling attack) o puede enviar gradientes diseñados para insertar un backdoor en el modelo global (Byzantine attack). Las defensas incluyen mecanismos de agregación robusta como Krum, Coordinate-wise Median y FLTrust.

### 3.4 Adversarial examples: FGSM con PyTorch

Los ejemplos adversariales son inputs modificados mediante perturbaciones imperceptibles para el ser humano que causan que el modelo produzca predicciones incorrectas. El **Fast Gradient Sign Method (FGSM)** (Goodfellow et al., 2014) es el método más sencillo y pedagógicamente fundamental:

```python
import torch
import torch.nn.functional as F

def fgsm_attack(model, loss_fn, images, labels, epsilon):
    """
    Genera ejemplos adversariales usando FGSM.
    
    Args:
        model: modelo PyTorch en modo eval
        loss_fn: función de pérdida (ej. CrossEntropyLoss)
        images: tensor de imágenes [B, C, H, W], requiere grad
        labels: tensor de etiquetas verdaderas [B]
        epsilon: magnitud de la perturbación (ej. 0.03)
    
    Returns:
        Tensor de imágenes adversariales del mismo shape que images
    """
    images.requires_grad = True
    
    # Forward pass
    outputs = model(images)
    loss = loss_fn(outputs, labels)
    
    # Backpropagation para obtener gradientes respecto al input
    model.zero_grad()
    loss.backward()
    
    # Signo del gradiente: dirección que maximiza la pérdida
    gradient_sign = images.grad.data.sign()
    
    # Perturbación adversarial
    adversarial_images = images + epsilon * gradient_sign
    
    # Recortar al rango válido de píxeles [0, 1]
    adversarial_images = torch.clamp(adversarial_images, 0, 1)
    
    return adversarial_images.detach()


# Ejemplo de uso en un bucle de evaluación
model.eval()
loss_fn = torch.nn.CrossEntropyLoss()
epsilon = 0.03  # Perturbación máxima por píxel (en escala [0,1])

correct_clean = 0
correct_adv = 0
total = 0

for images, labels in test_loader:
    images, labels = images.to(device), labels.to(device)
    
    # Evaluación limpia
    with torch.no_grad():
        outputs = model(images)
        correct_clean += (outputs.argmax(1) == labels).sum().item()
    
    # Generación y evaluación adversarial
    adv_images = fgsm_attack(model, loss_fn, images.clone(), labels, epsilon)
    with torch.no_grad():
        adv_outputs = model(adv_images)
        correct_adv += (adv_outputs.argmax(1) == labels).sum().item()
    
    total += labels.size(0)

print(f"Accuracy limpia:       {correct_clean/total:.3f}")
print(f"Accuracy adversarial:  {correct_adv/total:.3f}")
```

**Defensa con adversarial training**: la técnica más efectiva contra FGSM y sus variantes es incluir ejemplos adversariales en el propio entrenamiento. El modelo aprende a ser robusto porque ve perturbaciones durante la fase de aprendizaje:

```python
def adversarial_training_step(model, optimizer, loss_fn, images, labels, epsilon):
    model.train()
    
    # Generar ejemplos adversariales (el modelo debe estar en eval para generar)
    model.eval()
    adv_images = fgsm_attack(model, loss_fn, images.clone(), labels, epsilon)
    model.train()
    
    # Entrenamiento sobre la mezcla de ejemplos limpios y adversariales
    mixed_images = torch.cat([images, adv_images], dim=0)
    mixed_labels = torch.cat([labels, labels], dim=0)
    
    optimizer.zero_grad()
    outputs = model(mixed_images)
    loss = loss_fn(outputs, mixed_labels)
    loss.backward()
    optimizer.step()
    
    return loss.item()
```

### 3.5 Model extraction y model inversion

**Model extraction**: el atacante realiza consultas sistemáticas a la API del modelo para construir un modelo sustituto (surrogate model) que replica su comportamiento, potencialmente extrayendo propiedad intelectual o conocimiento entrenado con datos privados. La defensa principal es el rate limiting (tratado en el siguiente apartado).

**Model inversion**: el atacante utiliza el acceso a las predicciones del modelo para reconstruir características de los datos de entrenamiento. En sistemas de reconocimiento facial entrenados con datos privados, esto puede permitir reconstruir imágenes de individuos del conjunto de entrenamiento.

### 3.6 OWASP Machine Learning Security Top 10

La OWASP Machine Learning Security Top 10 (publicada en 2023) identifica los diez riesgos más críticos específicos de los sistemas ML:

**ML01 — Input Manipulation Attack (Adversarial Examples)**: manipulación de los inputs en inferencia para provocar predicciones incorrectas. Impacto: alta en sistemas de seguridad crítica.

**ML02 — Data Poisoning Attack**: corrupción del dataset de entrenamiento para degradar el rendimiento o insertar comportamientos ocultos. Impacto: puede ser permanente si no se detecta antes del despliegue.

**ML03 — Model Inversion Attack**: extracción de información sobre los datos de entrenamiento mediante consultas al modelo. Impacto: vulneración de privacidad de individuos presentes en el dataset.

**ML04 — Membership Inference Attack**: determinación de si un registro específico formó parte del conjunto de entrenamiento. Crítico en datasets médicos o legales.

**ML05 — Model Theft**: extracción del modelo mediante consultas sistemáticas. Afecta a la propiedad intelectual y puede usarse como paso previo para ataques más sofisticados.

**ML06 — AI Supply Chain Attacks**: compromiso de dependencias externas: modelos preentrenados, datasets públicos, bibliotecas de ML. Un modelo descargado de un repositorio público puede contener un backdoor.

**ML07 — Transfer Learning Attack**: ataques dirigidos a los modelos base utilizados en fine-tuning. Si el modelo base está envenenado, el modelo fine-tuneado hereda el backdoor.

**ML08 — Model Skewing**: manipulación de los datos de retroalimentación en producción (por ejemplo, en sistemas con aprendizaje continuo) para desviar el modelo hacia comportamientos deseados por el atacante.

**ML09 — Output Integrity Attack**: manipulación de las predicciones del modelo después de generadas, antes de que lleguen al sistema consumidor. Requiere acceso a la infraestructura de despliegue.

**ML10 — Model Poisoning**: modificación directa de los pesos del modelo, generalmente en el contexto de federated learning o mediante compromiso del sistema de almacenamiento de artefactos.

### 3.7 Verificación de integridad de artefactos con SHA-256

Cualquier artefacto ML (pesos, datasets, configuraciones) debe verificarse antes de su uso mediante hash criptográfico. El proceso estándar es:

```python
import hashlib
import json
from pathlib import Path

def compute_sha256(file_path: str) -> str:
    """Calcula el hash SHA-256 de un archivo en bloques para manejar archivos grandes."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            sha256.update(block)
    return sha256.hexdigest()

def register_artifact(file_path: str, manifest_path: str = "artifacts_manifest.json"):
    """Registra el hash de un artefacto en un manifiesto de integridad."""
    artifact_hash = compute_sha256(file_path)
    manifest = {}
    if Path(manifest_path).exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
    manifest[file_path] = {"sha256": artifact_hash}
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Registrado: {file_path} -> {artifact_hash[:16]}...")

def verify_artifact(file_path: str, manifest_path: str = "artifacts_manifest.json") -> bool:
    """Verifica la integridad de un artefacto contra el manifiesto registrado."""
    with open(manifest_path) as f:
        manifest = json.load(f)
    if file_path not in manifest:
        raise ValueError(f"Artefacto no registrado en el manifiesto: {file_path}")
    expected = manifest[file_path]["sha256"]
    actual = compute_sha256(file_path)
    return actual == expected
```

Este proceso debe integrarse en los pipelines de CI/CD de ML: antes de lanzar un job de fine-tuning, verificar el checkpoint base; antes de desplegar un modelo, verificar los pesos.

---

## 4. Seguridad de APIs de inferencia

### 4.1 Autenticación: API keys y OAuth2/JWT

Las APIs de inferencia expuestas deben implementar autenticación robusta. Dos patrones principales:

**API keys** (adecuadas para comunicación server-to-server): generación de tokens de alta entropía (mínimo 256 bits), almacenados en la base de datos como hash bcrypt, no en texto plano. La clave se transmite en el header `Authorization: Bearer <key>`.

**OAuth2 con JWT** (adecuado cuando los clientes son usuarios finales o aplicaciones de terceros): el servidor emite un JWT firmado (RS256 o ES256 en producción; nunca HS256 con secretos débiles) que el cliente incluye en cada solicitud. La validación del JWT no requiere consultar la base de datos en cada request:

```python
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer

SECRET_KEY = "clave-de-firma-cargada-desde-variable-de-entorno"
ALGORITHM = "HS256"  # En producción: RS256 con par de claves
security = HTTPBearer()

def create_access_token(user_id: str, expires_delta: timedelta = timedelta(hours=1)) -> str:
    payload = {
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + expires_delta,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
```

### 4.2 Rate limiting para prevenir model extraction

El rate limiting es la defensa principal contra los ataques de model extraction. Un atacante necesita miles o millones de consultas para construir un surrogate model útil; el rate limiting hace este proceso lento y costoso:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

@app.post("/predict")
@limiter.limit("100/minute")   # 100 requests por minuto por IP
@limiter.limit("1000/hour")    # 1000 requests por hora por IP
async def predict(request: Request, payload: PredictionRequest, user_id: str = Depends(verify_token)):
    # Además del límite por IP, límite por usuario autenticado
    return await run_inference(payload)
```

### 4.3 Validación de inputs

Antes de pasar cualquier input al modelo, debe validarse su forma, tipo y rango de valores. La validación no es solo una práctica de calidad de software; en contextos ML previene ataques de prompt injection (en LLMs) y entradas diseñadas para causar comportamientos anómalos:

```python
from pydantic import BaseModel, validator
import numpy as np

class ImagePredictionRequest(BaseModel):
    image_data: list[list[list[float]]]  # [C, H, W]
    
    @validator("image_data")
    def validate_image(cls, v):
        arr = np.array(v)
        if arr.shape != (3, 224, 224):
            raise ValueError(f"Shape esperado (3,224,224), recibido {arr.shape}")
        if arr.min() < 0 or arr.max() > 1:
            raise ValueError("Los valores de píxel deben estar en [0, 1]")
        return v
```

### 4.4 Logging de seguridad sin datos sensibles

El logging de solicitudes a APIs de inferencia es necesario para detectar patrones de ataque, pero debe diseñarse cuidadosamente para no persistir datos sensibles (imágenes médicas, textos privados, datos biométricos):

```python
import logging
import hashlib

logger = logging.getLogger("inference_api")

def log_inference_request(user_id: str, input_shape: tuple, latency_ms: float, prediction_class: int):
    """Registra metadatos de la solicitud sin persistir el contenido del input."""
    logger.info({
        "event": "inference_request",
        "user_id_hash": hashlib.sha256(user_id.encode()).hexdigest()[:16],  # No el ID real
        "input_shape": input_shape,
        "latency_ms": round(latency_ms, 2),
        "predicted_class": prediction_class,
        # NO registrar: el tensor de input, la probabilidad por clase completa,
        # el user_id en claro, metadatos que permitan identificar al individuo
    })
```

### 4.5 HTTPS obligatorio

Toda API de inferencia debe servirse exclusivamente sobre HTTPS. En producción, esto significa terminar TLS en el load balancer o en un reverse proxy (nginx, Caddy), nunca exponer el puerto HTTP directamente. Los certificados deben renovarse automáticamente (Let's Encrypt + Certbot o servicios gestionados del cloud provider).

---

## 5. Privacidad en ML

### 5.1 Differential privacy: concepto epsilon-delta

La differential privacy (DP) es un marco matemático formal para cuantificar y garantizar la privacidad en el procesamiento de datos. La definición formal establece que un mecanismo aleatorio M es (ε, δ)-diferencialmente privado si, para cualquier par de datasets D y D' que difieren en un solo registro, y para cualquier conjunto de outputs S:

```
P[M(D) ∈ S] ≤ e^ε · P[M(D') ∈ S] + δ
```

**Epsilon (ε)** es el presupuesto de privacidad: cuanto más pequeño, más privacidad (pero más ruido inyectado). Un ε = 1 ofrece garantías sólidas; ε = 10 es más permisivo. En ML se trabaja habitualmente en rangos de 1 a 10.

**Delta (δ)** es la probabilidad de que la garantía falle. Debe ser significativamente menor que 1/n, donde n es el tamaño del dataset. Un valor típico es δ = 10^-5.

### 5.2 DP-SGD con Opacus (PyTorch)

Opacus es la biblioteca oficial de PyTorch para entrenamiento con differential privacy. El mecanismo subyacente es DP-SGD: en cada paso de optimización, los gradientes individuales se recortan a una norma máxima (clipping) y se les añade ruido gaussiano calibrado para satisfacer el presupuesto (ε, δ).

```python
import torch
from torch import nn, optim
from torch.utils.data import DataLoader, TensorDataset
from opacus import PrivacyEngine
from opacus.validators import ModuleValidator

# 1. Definir modelo y asegurarse de que es compatible con Opacus
model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Linear(256, 10)
)

# Opacus requiere que el modelo no use BatchNorm; convertir si es necesario
model = ModuleValidator.fix(model)
ModuleValidator.validate(model, strict=True)

# 2. Configurar optimizador y dataloader
optimizer = optim.SGD(model.parameters(), lr=0.01)
train_dataset = TensorDataset(torch.randn(1000, 784), torch.randint(0, 10, (1000,)))
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

# 3. Adjuntar el PrivacyEngine al modelo
privacy_engine = PrivacyEngine()
model, optimizer, train_loader = privacy_engine.make_private_with_epsilon(
    module=model,
    optimizer=optimizer,
    data_loader=train_loader,
    epochs=10,
    target_epsilon=5.0,   # Presupuesto de privacidad objetivo
    target_delta=1e-5,    # Delta objetivo
    max_grad_norm=1.0,    # Norma máxima de clipping por gradiente
)

# 4. Bucle de entrenamiento (idéntico al estándar)
loss_fn = nn.CrossEntropyLoss()
for epoch in range(10):
    model.train()
    for images, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(images)
        loss = loss_fn(outputs, labels)
        loss.backward()
        optimizer.step()
    
    # Consultar el presupuesto consumido
    epsilon = privacy_engine.get_epsilon(delta=1e-5)
    print(f"Época {epoch+1}: ε = {epsilon:.3f}, δ = 1e-5")
```

**TensorFlow Privacy** ofrece funcionalidad equivalente para el ecosistema TensorFlow, con la clase `DPKerasSGDOptimizer` como componente principal.

### 5.3 Federated learning con Flower

El federated learning es un paradigma de entrenamiento distribuido en el que los datos nunca abandonan los dispositivos o servidores de los participantes. El servidor central coordina el entrenamiento enviando el modelo global, cada cliente lo ajusta con sus datos locales y envía de vuelta solo las actualizaciones de pesos.

**Flower** (flwr) es el framework de federated learning más activo del ecosistema Python. Implementa el protocolo FedAvg y muchas variantes:

```python
# --- Lado servidor ---
import flwr as fl

strategy = fl.server.strategy.FedAvg(
    fraction_fit=0.5,          # Fracción de clientes que participan en cada ronda
    fraction_evaluate=0.25,
    min_fit_clients=2,
    min_available_clients=2,
)

fl.server.start_server(
    server_address="0.0.0.0:8080",
    config=fl.server.ServerConfig(num_rounds=10),
    strategy=strategy,
)

# --- Lado cliente (cada participante ejecuta esto con sus propios datos) ---
import flwr as fl
import torch

class FlowerClient(fl.client.NumPyClient):
    def __init__(self, model, train_loader, test_loader):
        self.model = model
        self.train_loader = train_loader
        self.test_loader = test_loader

    def get_parameters(self, config):
        return [p.cpu().detach().numpy() for p in self.model.parameters()]

    def set_parameters(self, parameters):
        for param, new_param in zip(self.model.parameters(), parameters):
            param.data = torch.tensor(new_param)

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        # Entrenamiento local (1-5 épocas típicamente)
        train_local(self.model, self.train_loader, epochs=1)
        return self.get_parameters(config={}), len(self.train_loader.dataset), {}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        loss, accuracy = evaluate_local(self.model, self.test_loader)
        return loss, len(self.test_loader.dataset), {"accuracy": accuracy}

fl.client.start_numpy_client(server_address="servidor:8080", client=FlowerClient(...))
```

### 5.4 Membership inference attacks

Los ataques de membership inference tienen como objetivo determinar si un registro específico fue utilizado en el entrenamiento del modelo. La intuición es que los modelos tienden a tener menor pérdida (mayor confianza) en los ejemplos que han memorizado durante el entrenamiento. Un adversario puede entrenar un "meta-clasificador" que distingue entre ejemplos de entrenamiento y ejemplos que no formaron parte del dataset.

Las defensas incluyen: regularización (dropout, L2), early stopping (reducir la memorización), differential privacy (ofrece garantías matemáticas contra este ataque) y reducir la confianza en las predicciones (temperature scaling, top-k outputs).

---

## 6. Sostenibilidad en producción ML

### 6.1 Consumo energético de la inferencia

El impacto energético del ML en producción es frecuentemente subestimado porque el foco mediático se centra en el entrenamiento. Sin embargo, para la mayoría de las organizaciones, la inferencia en producción supone el mayor consumo energético acumulado: un modelo puede entrenarse una vez pero ejecutarse miles de millones de veces.

Los factores determinantes del consumo en inferencia son: el número de parámetros activos, la precisión numérica de los pesos (FP32, FP16, INT8, INT4), la utilización de hardware especializado (GPU vs CPU vs NPU), el batch size y la frecuencia de solicitudes.

### 6.2 Quantización: INT8 con ONNX Runtime e INT4 con bitsandbytes

La quantización reduce la precisión numérica de los pesos del modelo. Los pesos almacenados en FP32 (32 bits por valor) pueden convertirse a INT8 (8 bits) con pérdida de precisión mínima y una reducción del 75% en tamaño y mejoras sustanciales en velocidad de inferencia en hardware compatible.

**INT8 con ONNX Runtime**:

```python
from onnxruntime.quantization import quantize_dynamic, QuantType
import onnxruntime as ort

# Paso 1: exportar el modelo PyTorch a ONNX
torch.onnx.export(
    model,
    dummy_input,
    "model_fp32.onnx",
    opset_version=17,
    input_names=["input"],
    output_names=["output"],
)

# Paso 2: quantización dinámica a INT8
quantize_dynamic(
    model_input="model_fp32.onnx",
    model_output="model_int8.onnx",
    weight_type=QuantType.QInt8,
)

# Paso 3: inferencia con el modelo quantizado
session = ort.InferenceSession("model_int8.onnx")
outputs = session.run(None, {"input": input_array})
```

**INT4 con bitsandbytes** (especialmente relevante para LLMs):

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",        # NormalFloat4: distribución óptima para pesos LLM
    bnb_4bit_use_double_quant=True,   # Double quantization para mayor ahorro
)

model = AutoModelForCausalLM.from_pretrained(
    "nombre-del-modelo",
    quantization_config=quantization_config,
    device_map="auto",
)
```

### 6.3 Pruning estructurado vs no estructurado

El pruning elimina conexiones o neuronas del modelo para reducir su tamaño y el número de operaciones.

**Pruning no estructurado**: elimina pesos individuales (poniéndolos a cero) sin restricciones de estructura. Produce matrices de pesos sparse que requieren hardware y software especializado para obtener speedups reales en inferencia. La compresión en disco es efectiva, pero el speedup en la práctica depende del soporte de sparse computation del hardware objetivo.

**Pruning estructurado**: elimina filtros completos (en CNNs), cabezas de atención completas (en transformers) o capas completas. El modelo resultante es un modelo denso más pequeño, compatible con cualquier hardware sin requerir soporte especial para sparse computation. Es más fácil de desplegar y más efectivo en la práctica para reducir latencia.

```python
import torch.nn.utils.prune as prune

# Pruning no estructurado: 40% de los pesos de una capa a cero
prune.l1_unstructured(model.fc1, name="weight", amount=0.4)

# Pruning estructurado: eliminar el 30% de los filtros menos relevantes
prune.ln_structured(model.conv1, name="weight", amount=0.3, n=2, dim=0)

# Hacer el pruning permanente (eliminar la máscara, fijar los ceros)
prune.remove(model.fc1, "weight")
```

### 6.4 Knowledge distillation

La knowledge distillation entrena un modelo pequeño (student) para imitar el comportamiento de un modelo grande (teacher). El student no aprende solo de las etiquetas duras (hard labels), sino de las distribuciones de probabilidad suaves (soft labels) que produce el teacher, las cuales contienen información sobre las similitudes entre clases que las etiquetas duras no capturan.

```python
import torch.nn.functional as F

def distillation_loss(student_logits, teacher_logits, true_labels, temperature=4.0, alpha=0.7):
    """
    Combina la pérdida de distilación (soft) con la pérdida de clasificación (hard).
    
    temperature: suaviza las distribuciones del teacher (>1 revela más estructura)
    alpha: peso de la pérdida de distilación vs la pérdida de clasificación
    """
    # Pérdida soft: el student imita al teacher
    soft_loss = F.kl_div(
        F.log_softmax(student_logits / temperature, dim=1),
        F.softmax(teacher_logits / temperature, dim=1),
        reduction="batchmean",
    ) * (temperature ** 2)
    
    # Pérdida hard: el student aprende las etiquetas verdaderas
    hard_loss = F.cross_entropy(student_logits, true_labels)
    
    return alpha * soft_loss + (1 - alpha) * hard_loss
```

Un GPT-2 de 1.5B parámetros puede destilar a un modelo de 125M con pérdida de rendimiento marginal en muchas tareas de generación de texto.

### 6.5 Caching como estrategia verde

El semantic caching consiste en almacenar en cache las respuestas a solicitudes anteriores y servirlas cuando llega una solicitud semánticamente similar, sin ejecutar la inferencia completa. Es especialmente efectivo en LLMs donde muchos usuarios hacen preguntas similares. Herramientas como GPTCache implementan este patrón con búsqueda de similitud semántica mediante embeddings.

### 6.6 Métricas de eficiencia energética

Las métricas estándar para comparar opciones de despliegue desde la perspectiva de la sostenibilidad son:

- **tokens/J** (tokens por julio): relevante para LLMs. Mide cuántos tokens puede generar el sistema por unidad de energía consumida.
- **inferencias/kWh**: relevante para modelos de clasificación o regresión. Mide cuántas predicciones se pueden servir por kilovatio-hora.
- **PUE (Power Usage Effectiveness)**: ratio entre la energía total del datacenter y la energía consumida por el equipamiento de cómputo. Un PUE de 1.1 es excelente; 1.5 es típico; >2 es ineficiente.
- **Carbon intensity (gCO2/kWh)**: depende de la mezcla energética del datacenter. Elegir regiones con energía renovable puede reducir la huella de carbono del ML sin cambiar la arquitectura del modelo.

---

## 7. Marcos éticos y auditorías

### 7.1 IEEE Ethically Aligned Design (EAD)

El documento "Ethically Aligned Design" del IEEE (versión 1, 2019) es uno de los marcos éticos más comprehensivos para sistemas de IA y autónomos. Organiza los principios éticos en ocho áreas:

1. **Derechos humanos**: los sistemas de IA no deben utilizarse para violar, reprimir o restringir derechos humanos reconocidos internacionalmente.
2. **Bienestar**: la métrica de éxito de un sistema de IA debe incluir el bienestar humano, no solo la eficiencia operativa.
3. **Responsabilidad de datos**: los sistemas que procesan datos de personas deben garantizar la minimización, la limitación de propósito y el control por parte del individuo.
4. **Transparencia**: los procesos de toma de decisiones de los sistemas autónomos deben ser comprensibles por los humanos afectados.
5. **Awareness of misuse**: quienes diseñan y despliegan sistemas de IA deben anticipar y mitigar activamente los usos indebidos.
6. **Competencia**: los profesionales que trabajan en IA deben mantener un nivel de competencia técnica y ética actualizado.
7. **Environmental wellbeing**: los sistemas de IA deben diseñarse con conciencia de su impacto ambiental.
8. **Mixed reality and AI**: consideraciones específicas sobre la fusión de entornos físicos y digitales.

### 7.2 ALTAI — Assessment List for Trustworthy AI

El ALTAI (Assessment List for Trustworthy AI), publicado por la Comisión Europea en 2020, operacionaliza los siete requisitos de la IA Fiable definidos en las "Ethics Guidelines for Trustworthy AI":

**Requisito 1 — Human Agency and Oversight**: ¿el sistema preserva la autonomía humana? ¿Existe supervisión humana significativa? ¿Los usuarios pueden anular las decisiones del sistema?

**Requisito 2 — Technical Robustness and Safety**: ¿el sistema ha sido probado frente a inputs adversariales? ¿Tiene mecanismos de fallback? ¿Es reproducible?

**Requisito 3 — Privacy and Data Governance**: ¿minimiza los datos recopilados? ¿Garantiza la privacidad by design? ¿Los datos de entrenamiento son de calidad verificada?

**Requisito 4 — Transparency**: ¿los usuarios saben que interactúan con un sistema de IA? ¿Las decisiones pueden explicarse? ¿Existe documentación del modelo?

**Requisito 5 — Diversity, Non-discrimination and Fairness**: ¿se han analizado posibles sesgos en los datos? ¿El sistema ha sido evaluado en subgrupos demográficos? ¿Existe un proceso de remediación de sesgos detectados?

**Requisito 6 — Societal and Environmental Wellbeing**: ¿se ha evaluado el impacto social más amplio? ¿Se ha considerado el impacto ambiental del sistema?

**Requisito 7 — Accountability**: ¿quién es responsable de las decisiones del sistema? ¿Existe un proceso de auditoría interna? ¿Se puede reclamar ante decisiones incorrectas?

El ALTAI está disponible como herramienta web interactiva en la plataforma AI Alliance de la Comisión Europea, generando un informe estructurado al completar el cuestionario.

### 7.3 Estructura de una auditoría ética de sistema ML

Una auditoría ética de un sistema ML en producción sigue típicamente esta estructura:

**Fase 1 — Definición del alcance**: identificar el sistema auditado, su propósito declarado, la población afectada y los criterios de evaluación.

**Fase 2 — Recopilación de documentación**: recopilar la documentación técnica del modelo, los registros de entrenamiento, los análisis de sesgo previos, los registros de incidentes y la documentación de privacidad.

**Fase 3 — Evaluación técnica**: análisis de sesgo y fairness en los datos de entrenamiento y en las predicciones del modelo en subgrupos; evaluación de robustez; revisión de la seguridad de la infraestructura.

**Fase 4 — Evaluación de impacto**: entrevistas con usuarios afectados (si es posible), análisis de casos de uso no previstos, evaluación de impactos diferenciales por grupos.

**Fase 5 — Redacción del informe**: hallazgos clasificados por criticidad (crítico, alto, medio, bajo), recomendaciones concretas y plan de remediación con responsables y plazos.

**Fase 6 — Seguimiento**: verificación de que las recomendaciones se han implementado en el plazo acordado.

### 7.4 EU AI Act: documentación requerida para sistemas de alto riesgo (Anexo IV)

El Reglamento (UE) 2024/1689 (EU AI Act) clasifica los sistemas de IA en categorías de riesgo. Los sistemas de alto riesgo (Anexo III: sistemas de IA en infraestructura crítica, educación, empleo, acceso a servicios esenciales, aplicación de la ley, migración, administración de justicia) tienen obligaciones estrictas de documentación técnica definidas en el Anexo IV:

1. **Descripción general del sistema**: propósito previsto, versiones del software, interacciones con otros sistemas.
2. **Descripción de los componentes y del proceso de desarrollo**: arquitectura del modelo, opciones de diseño relevantes para el rendimiento y la seguridad, descripción de los datos de entrenamiento (incluyendo sus características, proceso de recopilación, etiquetado y posibles limitaciones).
3. **Descripción del sistema de monitorización post-mercado**: cómo se detectan degradaciones en el rendimiento o incidentes en producción.
4. **Descripción de las capacidades y limitaciones del sistema**: condiciones de operación previstas, condiciones que pueden afectar negativamente al rendimiento, métricas de rendimiento en diferentes subgrupos.
5. **Descripción del nivel de exactitud, solidez y ciberseguridad**: métricas de rendimiento en los conjuntos de test, resultados de las pruebas de adversarial robustness, descripción de las medidas de seguridad implementadas.
6. **Descripción del proceso de gestión de riesgos**: el proceso seguido para identificar y mitigar riesgos, incluyendo los riesgos residuales asumidos.
7. **Descripción de las medidas de supervisión humana**: cómo se implementa la supervisión humana, qué decisiones puede anular el operador humano y con qué mecanismos.
8. **Declaración de conformidad UE**: firmada por el proveedor, declarando que el sistema cumple los requisitos del Reglamento.

El incumplimiento de estas obligaciones puede acarrear multas de hasta 30 millones de euros o el 6% del volumen de negocio mundial anual, la cifra que sea mayor.

---

## 8. Actividades prácticas

### Actividad 1 — Evaluación de robustez adversarial (FGSM)

**Objetivo**: medir la degradación de accuracy de un clasificador bajo ataque FGSM en función de epsilon y implementar adversarial training para mejorar la robustez.

**Desarrollo**: entrenar un clasificador CNN en CIFAR-10; evaluar su accuracy en el conjunto de test limpio; generar ejemplos FGSM con epsilon en {0.01, 0.03, 0.05, 0.1}; trazar la curva de accuracy vs epsilon; re-entrenar el modelo con adversarial training (mezcla 50/50 de ejemplos limpios y FGSM con epsilon=0.03); evaluar el modelo robustificado con la misma curva.

**Entregable**: notebook con código, gráfica comparativa de las curvas de robustez del modelo estándar vs el modelo con adversarial training, y análisis (mínimo 200 palabras) de los trade-offs observados.

### Actividad 2 — Entrenamiento con differential privacy

**Objetivo**: experimentar con el impacto de distintos presupuestos epsilon en el rendimiento del modelo usando Opacus.

**Desarrollo**: tomar el clasificador de la actividad anterior; entrenarlo con Opacus en tres configuraciones: epsilon=1.0, epsilon=5.0 y epsilon=10.0 (mismos hiperparámetros de entrenamiento en los tres casos); registrar la accuracy final y el epsilon consumido real; comparar con el baseline sin DP.

**Entregable**: tabla comparativa con epsilon objetivo, epsilon consumido, accuracy en test y tamaño del modelo. Reflexión sobre qué configuración es adecuada para un sistema médico hipotético.

### Actividad 3 — Optimización de inferencia

**Objetivo**: comparar el throughput y la eficiencia energética de un modelo en FP32, FP16 e INT8.

**Desarrollo**: tomar un modelo de visión preentrenado (por ejemplo ResNet-50); exportarlo a ONNX; aplicar quantización dinámica INT8 con ONNX Runtime; medir latencia media por inferencia (en ms), throughput (inferencias/s) y tamaño del modelo en disco para cada precisión; estimar inferencias/kWh asumiendo un consumo de 150W de la GPU durante la inferencia.

**Entregable**: tabla comparativa de las tres configuraciones, gráfica de latencia vs tamaño del modelo, y conclusión sobre cuál es la opción más sostenible para un caso de uso con SLA de latencia < 50ms.

### Actividad 4 — Auditoría ética con ALTAI

**Objetivo**: aplicar el checklist ALTAI a un sistema ML real o hipotético y producir un informe de auditoría básico.

**Desarrollo**: elegir un sistema ML de los descritos en clase o proponer uno propio (sistema de scoring de crédito, sistema de diagnóstico médico, sistema de selección de CVs, sistema de predicción de reincidencia criminal); completar el cuestionario ALTAI online (disponible en la plataforma AI Alliance); identificar los tres requisitos con mayor gap entre el diseño actual y el estándar ALTAI; redactar un plan de remediación para cada uno.

**Entregable**: informe ALTAI generado por la plataforma (PDF) + documento de plan de remediación (mínimo 500 palabras) con acciones concretas, responsables y plazos estimados.

---

## 9. Referencias

### Seguridad en ML

- OWASP Machine Learning Security Top 10. (2023). *OWASP Foundation*.
  https://owasp.org/www-project-machine-learning-security-top-10/

- Gu, T., Dolan-Gavitt, B., & Garg, S. (2017). BadNets: Identifying Vulnerabilities in the Machine Learning Model Supply Chain. *arXiv:1708.06733*.
  https://arxiv.org/abs/1708.06733

- Goodfellow, I. J., Shlens, J., & Szegedy, C. (2014). Explaining and Harnessing Adversarial Examples. *arXiv:1412.6572*.
  https://arxiv.org/abs/1412.6572

- IBM Research. (2022). *Adversarial Robustness Toolbox (ART) v1.x Documentation*.
  https://adversarial-robustness-toolbox.readthedocs.io/

- Tramèr, F., Zhang, F., Juels, A., Reiter, M. K., & Ristenpart, T. (2016). Stealing Machine Learning Models via Prediction APIs. *USENIX Security 2016*.
  https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/tramer

### Privacidad y federated learning

- Opacus Documentation. (2024). *PyTorch Opacus: User-Level Privacy for PyTorch*.
  https://opacus.ai/

- Abadi, M., Chu, A., Goodfellow, I., et al. (2016). Deep Learning with Differential Privacy. *CCS 2016*.
  https://arxiv.org/abs/1607.00133

- Flower Documentation. (2024). *Flower: A Friendly Federated Learning Framework*.
  https://flower.dev/docs/

- McMahan, H. B., Moore, E., Ramage, D., Hampson, S., & y Arcas, B. A. (2017). Communication-Efficient Learning of Deep Networks from Decentralized Data. *AISTATS 2017*.
  https://arxiv.org/abs/1602.05629

- Shokri, R., Stronati, M., Song, C., & Shmatikov, V. (2017). Membership Inference Attacks Against Machine Learning Models. *IEEE S&P 2017*.
  https://arxiv.org/abs/1610.05820

### Sostenibilidad

- Schwartz, R., Dodge, J., Smith, N. A., & Etzioni, O. (2019). Green AI. *arXiv:1907.10597*.
  https://arxiv.org/abs/1907.10597

- ONNX Runtime Documentation. (2024). *Quantization — ONNX Runtime*.
  https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html

- bitsandbytes Documentation. (2024). *bitsandbytes: 8-bit optimizers and quantization for PyTorch*.
  https://huggingface.co/docs/bitsandbytes/

- Hinton, G., Vinyals, O., & Dean, J. (2015). Distilling the Knowledge in a Neural Network. *arXiv:1503.02531*.
  https://arxiv.org/abs/1503.02531

### Marcos éticos y regulación

- Comisión Europea. (2020). *ALTAI — Assessment List for Trustworthy AI*.
  https://digital-strategy.ec.europa.eu/en/library/assessment-list-trustworthy-artificial-intelligence-altai-self-assessment

- Unión Europea. (2024). *Reglamento (UE) 2024/1689 — EU AI Act*.
  https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689

- IEEE. (2019). *Ethically Aligned Design: A Vision for Prioritizing Human Well-being with Autonomous and Intelligent Systems, Version 1*.
  https://standards.ieee.org/content/dam/ieee-standards/standards/web/documents/other/ead1e.pdf

- Comisión Europea. (2019). *Ethics Guidelines for Trustworthy AI*. High-Level Expert Group on Artificial Intelligence.
  https://digital-strategy.ec.europa.eu/en/library/ethics-guidelines-trustworthy-ai

- National Institute of Standards and Technology. (2023). *AI Risk Management Framework (AI RMF 1.0)*.
  https://www.nist.gov/system/files/documents/2023/01/26/AI%20RMF%201.0.pdf
