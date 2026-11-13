# UD1 · Integración de componentes físicos y equipos para sistemas de IA

**Módulo Profesional 01 — Implementación de Sistemas de IA**
**CFS2 — Instalación, despliegue y explotación de sistemas de IA**

---

## 1. Introducción

La inteligencia artificial moderna es, en su base más elemental, un problema de computación. Los modelos de lenguaje de gran escala, las redes neuronales convolucionales para visión por computador o los sistemas de recomendación en tiempo real comparten una característica fundamental: consumen cantidades masivas de operaciones matemáticas en punto flotante, ejecutadas sobre estructuras de datos de gran tamaño que deben residir en memoria de acceso rápido. Esta realidad hace que el hardware no sea un detalle de implementación sino la variable que determina qué es posible entrenar, en cuánto tiempo y a qué coste.

Durante décadas, la arquitectura de un ordenador de propósito general, optimizada para ejecutar instrucciones secuenciales con baja latencia, fue suficiente para la mayor parte de la computación científica. Sin embargo, el auge del aprendizaje profundo a partir de 2012, marcado por el trabajo de Krizhevsky, Sutskever e Hinton con AlexNet, evidenció que la CPU tradicional era un cuello de botella insuperable para las operaciones matriciales masivas que sustentan el entrenamiento de redes neuronales. La GPU, originalmente diseñada para el procesamiento gráfico paralelo, demostró ser capaz de acelerar estas cargas de trabajo entre diez y cien veces respecto a la CPU.

Desde entonces, la industria ha evolucionado con velocidad inusitada. Hoy el ecosistema de hardware para IA incluye GPUs especializadas con núcleos dedicados a operaciones matriciales de baja precisión, unidades de procesamiento tensorial desarrolladas por grandes proveedores de nube, FPGAs reprogramables para inferencia de baja latencia, ASICs diseñados específicamente para cargas de inferencia en el borde de la red, y servidores con arquitecturas de interconexión que permiten que docenas de GPUs trabajen como un único sistema coherente.

Para el profesional que debe instalar, configurar y mantener infraestructuras de IA, comprender este ecosistema no es opcional. Una selección incorrecta de hardware puede hacer que un proyecto de entrenamiento tarde semanas en lugar de días, que el coste de inferencia en producción sea inviable, o que un sistema de edge AI no cumpla los requisitos de latencia. Esta unidad proporciona los fundamentos técnicos necesarios para tomar decisiones informadas sobre la infraestructura física de sistemas de IA.

---

## 2. Objetivos de aprendizaje

Al finalizar esta unidad, el estudiante será capaz de:

- Identificar y describir los principales componentes de hardware utilizados en sistemas de IA, distinguiendo entre aceleradores para entrenamiento e inferencia.
- Comparar arquitecturas de GPU de diferentes generaciones y fabricantes, evaluando sus especificaciones técnicas en función del caso de uso.
- Explicar el papel de los aceleradores especializados (TPUs, FPGAs, ASICs, NPUs) y seleccionar el más adecuado para un escenario dado.
- Dimensionar y seleccionar servidores y estaciones de trabajo para cargas de trabajo de entrenamiento e inferencia.
- Diseñar una arquitectura de almacenamiento apropiada para pipelines de datos en proyectos de IA, considerando ancho de banda, latencia y coste.
- Entender los requisitos de red e interconexión en clusters de GPU y su impacto en el rendimiento del entrenamiento distribuido.
- Planificar e implementar la instalación física de equipos de IA, incluyendo refrigeración, alimentación, cableado y pruebas post-instalación.
- Interpretar la salida de herramientas de diagnóstico como `nvidia-smi` y planificar procedimientos de burn-in y stress test.

---

## 3. GPUs para IA: arquitectura y selección

### 3.1 Arquitectura CUDA: SMs, CUDA Cores y Tensor Cores

La GPU moderna para IA se organiza en torno a los Streaming Multiprocessors (SMs). Cada SM contiene un conjunto de CUDA Cores (unidades aritméticas de propósito general para operaciones FP32 y FP64), Tensor Cores (unidades matriciales especializadas), caché L1, memoria compartida, registros, schedulers de warps y unidades de carga/almacenamiento. La diferencia clave entre CUDA Cores y Tensor Cores radica en la granularidad de la operación: mientras que un CUDA Core ejecuta una operación escalar por ciclo, un Tensor Core realiza una operación de multiplicación-acumulación de matrices (MMA) en un paso, típicamente del tipo D = A × B + C, donde A, B, C y D son matrices de pequeñas dimensiones (por ejemplo, 16×16 en Volta, ampliadas en generaciones posteriores).

Los Tensor Cores son la clave del rendimiento en entrenamiento de redes neuronales porque las capas densas, las convoluciones y las operaciones de atención en transformers se reducen a multiplicaciones de matrices. La diferencia en TFLOPS entre CUDA Cores y Tensor Cores para operaciones FP16 puede ser de un orden de magnitud o superior.

La jerarquía de memoria en la GPU incluye registros por hilo, memoria compartida por SM, caché L1 por SM, caché L2 compartida, y la VRAM (High Bandwidth Memory o GDDR) accesible por todos los SMs. El ancho de banda de memoria es el factor limitante en la mayoría de las cargas de inferencia: el modelo debe moverse desde VRAM a los SMs para cada cálculo, y si este movimiento es más lento que el cálculo, la GPU está en el régimen memory-bound.

### 3.2 Generaciones NVIDIA

**Hopper (H100, H200):** Lanzada en 2022, la arquitectura Hopper representa el estado del arte para entrenamiento de grandes modelos. El H100 SXM5 dispone de 80 GB de HBM3, un ancho de banda de memoria de 3,35 TB/s, y capacidades de 989 TFLOPS en FP16 con Tensor Cores y 3,958 PFLOPS en FP8 con sparsidad estructurada. Introduce el Transformer Engine, que ajusta dinámicamente la precisión entre FP8 y FP16 por capa durante el entrenamiento, sin pérdida significativa de calidad. También introduce el NVLink 4.0, que ofrece 900 GB/s de ancho de banda GPU-a-GPU dentro de un nodo DGX.

**Ada Lovelace (RTX 4090, L40S):** Orientada al mercado profesional y consumer. La RTX 4090 ofrece 24 GB de GDDR6X con un ancho de banda de 1,008 TB/s y 82,6 TFLOPS en FP16, siendo la opción más coste-efectiva para fine-tuning de modelos medianos y entrenamiento de modelos pequeños. La L40S es su equivalente en el mercado de centros de datos, con 48 GB de GDDR6 y optimizaciones para inferencia multimodal, muy utilizada para despliegues de LLMs de tamaño medio.

**Ampere (A100, A30):** Lanzada en 2020, sigue siendo una referencia en producción. El A100 SXM4 cuenta con 80 GB de HBM2e, ancho de banda de 2 TB/s y soporte para NVLink 3.0. Su versatilidad para entrenamiento e inferencia de modelos de tamaño medio y grande la mantiene relevante. El A30 es su variante con 24 GB orientada a inferencia en centros de datos con menor TDP.

### 3.3 AMD para IA: MI300X

AMD ha recuperado terreno con la arquitectura CDNA3. El Instinct MI300X incluye 192 GB de HBM3 (el mayor VRAM de un solo chip en el mercado a la fecha de esta unidad), un ancho de banda de 5,3 TB/s y compatibilidad con el ecosistema ROCm para PyTorch y TensorFlow. Su principal ventaja competitiva es precisamente la capacidad de memoria, que permite alojar modelos que de otro modo requerirían múltiples GPUs NVIDIA. La adopción creciente de ROCm por parte de la comunidad open-source y de grandes proveedores de nube hace de este acelerador una alternativa real en escenarios con restricciones de memoria.

### 3.4 Tabla comparativa de GPUs profesionales

| GPU | Arquitectura | VRAM | BW Memoria | FP16 TFLOPS | TDP | Caso de uso principal | Precio ref. (USD) |
|---|---|---|---|---|---|---|---|
| NVIDIA H100 SXM5 | Hopper | 80 GB HBM3 | 3,35 TB/s | 989 | 700 W | Entrenamiento LLM, HPC | ~30.000 |
| NVIDIA H200 SXM5 | Hopper | 141 GB HBM3e | 4,8 TB/s | 989 | 700 W | LLMs muy grandes, ciencia | ~45.000 |
| NVIDIA A100 SXM4 | Ampere | 80 GB HBM2e | 2,0 TB/s | 312 | 400 W | Entrenamiento/inferencia | ~10.000–15.000 |
| NVIDIA L40S | Ada Lovelace | 48 GB GDDR6 | 864 GB/s | 362 | 350 W | Inferencia, multimedia IA | ~8.000–10.000 |
| NVIDIA RTX 4090 | Ada Lovelace | 24 GB GDDR6X | 1,008 TB/s | 82,6 | 450 W | Fine-tuning, laboratorio | ~1.500–2.000 |
| AMD MI300X | CDNA3 | 192 GB HBM3 | 5,3 TB/s | 1.307 | 750 W | LLMs grandes, inferencia | ~15.000–20.000 |
| NVIDIA A30 | Ampere | 24 GB HBM2 | 933 GB/s | 165 | 165 W | Inferencia centros de datos | ~4.000–6.000 |

*Los precios son orientativos y varían significativamente según proveedor, contrato y mercado secundario.*

---

## 4. Aceleradores especializados

### 4.1 TPUs de Google: arquitectura systolic array

Las Tensor Processing Units de Google nacieron de la necesidad interna de reducir el coste de inferencia de los modelos de Google Brain. Su arquitectura central es el systolic array: una malla bidimensional de unidades de multiplicación-acumulación (MAC) que propagan datos entre vecinos en cada ciclo de reloj, eliminando la necesidad de acceder repetidamente a memoria externa durante el cálculo matricial. Este diseño es extremadamente eficiente para multiplicaciones de matrices grandes y predecibles, que son el núcleo de los transformers.

La **TPU v4** utiliza matrices de 128×128 MACs, opera en BF16 y ofrece hasta 275 TFLOPS por chip, con chips agrupados en pods de hasta 4.096 chips conectados por una red de interconexión de alta velocidad propia (ICI). La **TPU v5e** es la variante orientada a la eficiencia de coste para inferencia y fine-tuning, con menor tamaño de matriz pero mayor densidad de chips por pod. Las TPUs se acceden exclusivamente a través de Google Cloud, lo que impone una dependencia de proveedor que debe considerarse en la arquitectura de la solución.

**Cuándo usar TPU vs GPU:** Las TPUs son la opción más coste-efectiva para entrenar modelos de arquitectura transformer estándar a gran escala dentro del ecosistema JAX/XLA. Las GPUs NVIDIA ofrecen mayor flexibilidad de frameworks (PyTorch nativo, kernels CUDA personalizados) y son imprescindibles cuando el modelo incluye operaciones no estándar que el compilador XLA no optimiza bien. Para inferencia on-premise o en nubes no-Google, las GPUs siguen siendo la opción dominante.

### 4.2 FPGAs: Intel (Altera) y Xilinx (AMD)

Los Field-Programmable Gate Arrays son circuitos integrados cuya lógica puede reconfigurarse después de la fabricación. En el contexto de IA, su principal ventaja es la latencia ultra-baja y el consumo energético reducido para cargas de inferencia con modelos cuantizados. Al implementar directamente en hardware la aritmética de un modelo (por ejemplo, con pesos INT4 o binarios), se eliminan los ciclos de overhead que tiene cualquier procesador de propósito general.

Intel ofrece FPGAs de las familias Agilex y Stratix para centros de datos. Xilinx (ahora parte de AMD) tiene las familias Versal y Alveo. Herramientas como Intel OpenCL SDK, Vitis AI de AMD-Xilinx y FINN (de Xilinx Research) permiten compilar modelos de Keras o PyTorch a bitstreams FPGA. El principal inconveniente es la complejidad del flujo de desarrollo: los tiempos de síntesis son largos (horas) y la curva de aprendizaje es alta.

**Casos de uso relevantes:** trading algorítmico de alta frecuencia donde se requiere latencia sub-milisegundo, pre-procesamiento de datos en edge antes de enviar a inferencia, redes de detección de anomalías con requisitos de tiempo real en entornos industriales.

### 4.3 ASICs para IA

Los Application-Specific Integrated Circuits son chips diseñados y fabricados para una tarea concreta. No son reprogramables, pero maximizan la eficiencia para su caso de uso específico.

**Google Coral Edge TPU:** Chip ASIC para inferencia de modelos TensorFlow Lite cuantizados en INT8. Disponible en formato M.2, USB y PCIe. Capaz de ejecutar modelos de hasta 8 MB en SRAM interna a 4 TOPS con un TDP de solo 2W, diseñado para dispositivos edge con restricciones de energía.

**AWS Inferentia y Trainium:** AWS Inferentia (Inf1, Inf2) es el ASIC de Amazon para inferencia de modelos de aprendizaje profundo, accesible a través de instancias EC2. El SDK NeuronX permite compilar modelos PyTorch y TensorFlow para estos chips. AWS Trainium (Trn1) es su equivalente para entrenamiento, compitiendo directamente con las GPUs NVIDIA en coste por FLOP para modelos de lenguaje dentro del ecosistema AWS.

**Intel Gaudi y Gaudi 2:** Originalmente desarrollado por Habana Labs (adquirida por Intel), Gaudi 2 es un acelerador para entrenamiento e inferencia de modelos transformer, con 96 GB de HBM2e y conectividad RoCE integrada (eliminando la necesidad de NICs externas para comunicación entre chips). Su soporte para PyTorch a través del framework SynapseAI lo hace accesible sin necesidad de reescribir código.

### 4.4 NPUs en SoCs para edge AI

Los Neural Processing Units integrados en System-on-Chip representan la frontera del edge computing para IA. Apple Silicon (M3, M4, A17 Pro) incluye NPUs capaces de varios TOPS dedicados a inferencia de modelos cuantizados. Qualcomm Snapdragon 8 Gen 3 integra la Hexagon NPU para ejecutar modelos de IA en smartphones. MediaTek Dimensity ofrece capacidades similares. Estos NPUs permiten ejecutar inferencia local sin conexión a la nube, lo que es crítico para privacidad, latencia y disponibilidad offline en aplicaciones móviles e industriales.

---

## 5. Servidores y estaciones de trabajo para IA

### 5.1 Tipos de sistemas: workstation, servidor de inferencia y servidor de entrenamiento

La **estación de trabajo para IA** (AI workstation) es un sistema de escritorio o torre de alto rendimiento orientado a un único usuario o equipo pequeño. Típicamente monta una o dos GPUs consumer o profesionales (RTX 4090, A6000), entre 128 y 512 GB de RAM del sistema, y almacenamiento NVMe de alta capacidad. Es la plataforma de desarrollo, experimentación y fine-tuning de modelos medianos. Su ventaja es el coste reducido y la facilidad de gestión; su limitación es la escalabilidad.

El **servidor de inferencia** está optimizado para servir predicciones de modelos ya entrenados a múltiples usuarios concurrentes con baja latencia y alta disponibilidad. Prioriza la densidad de aceleradores por unidad de rack, la conectividad de red de alta velocidad y la redundancia de componentes. GPUs como la A30, L40S o sistemas como el NVIDIA L40S 8-GPU server son elecciones habituales. Los frameworks de serving como NVIDIA Triton Inference Server o TorchServe se ejecutan sobre esta infraestructura.

El **servidor de entrenamiento** está diseñado para ejecutar trabajos distribuidos que pueden durar días o semanas. Prioriza el número de GPUs de alto rendimiento (H100, A100), el ancho de banda de interconexión GPU-GPU (NVLink), la conectividad de red entre nodos (InfiniBand) y la capacidad de almacenamiento rápido para checkpoints de modelo. La gestión térmica es crítica dado el TDP de 700 W por GPU H100.

### 5.2 Servidores de referencia

**NVIDIA DGX H100:** El sistema de referencia de NVIDIA para entrenamiento de grandes modelos. Integra 8 GPUs H100 SXM5 de 80 GB, conectadas entre sí mediante NVSwitch a 900 GB/s de ancho de banda bidireccional. Dispone de 2 TB de RAM del sistema, CPUs dual Intel Xeon Scalable de 4ª generación, almacenamiento NVMe de 30 TB y conectividad de red de hasta 400 Gb/s por GPU mediante ocho tarjetas NVIDIA ConnectX-7. TDP total del sistema: aproximadamente 10,2 kW. Precio: en torno a 300.000–400.000 USD.

**Dell PowerEdge XE9680:** Servidor 4U para centros de datos estándar, con soporte para hasta 8 GPUs PCIe de doble slot o 8 GPUs SXM. Ofrece mayor flexibilidad que el DGX al soportar GPUs de terceros y ser compatible con herramientas de gestión empresarial de Dell (iDRAC). Es la elección habitual en organizaciones que ya tienen infraestructura Dell.

**HPE ProLiant DL380 Gen11 con NVIDIA GPU:** Servidor 2U de propósito general adaptado para cargas de IA con una o dos GPUs. Su principal fortaleza es la gestión vía HPE iLO, la compatibilidad con HPE Alletra para almacenamiento y la integración con HPE GreenLake para gestión de infraestructura híbrida.

### 5.3 NVLink y NVSwitch: comunicación GPU-GPU intra-nodo

NVLink es el bus de alta velocidad propietario de NVIDIA que conecta GPUs dentro de un mismo nodo, ofreciendo ancho de banda muy superior al bus PCIe. NVLink 4.0 (Hopper) proporciona 900 GB/s de ancho de banda bidireccional total entre 8 GPUs a través del NVSwitch, frente a los ~128 GB/s del PCIe 5.0 x16. El NVSwitch actúa como un switch de red interno que permite la comunicación all-to-all entre todas las GPUs del nodo sin pasar por la CPU, reduciendo drásticamente la latencia en operaciones de colectivos distribuidos (AllReduce, AllGather) durante el entrenamiento de modelos grandes.

### 5.4 Factor de forma

Los sistemas **tower** son adecuados para estaciones de trabajo individuales donde el ruido y el acceso físico frecuente son consideraciones. Los sistemas en formato **rack** (1U a 8U) son el estándar en centros de datos, optimizando la densidad por unidad de espacio y facilitando la gestión centralizada de alimentación y refrigeración. Los sistemas **blade** concentran múltiples módulos de cómputo en un chasis compartido que centraliza la alimentación, la refrigeración y la red, siendo la opción de mayor densidad pero menor flexibilidad de configuración por módulo.

---

## 6. Almacenamiento para IA

### 6.1 Requisitos de I/O en entrenamiento

El entrenamiento de modelos de IA impone requisitos de almacenamiento muy distintos a las cargas de trabajo empresariales tradicionales. Durante el entrenamiento, el sistema debe leer continuamente minibatches de datos desde almacenamiento, preprocesarlos y alimentarlos a las GPUs sin que estas queden ociosas. Para modelos de imagen con datasets como ImageNet (150 GB) o para LLMs con terabytes de texto, el ancho de banda de lectura secuencial y el número de operaciones de entrada/salida por segundo (IOPS) son los factores determinantes.

Una GPU H100 puede consumir datos a una velocidad que supera los 10–20 GB/s en ciertos regímenes, lo que significa que el almacenamiento debe ser capaz de sostener ese ancho de banda de forma continuada. El almacenamiento convencional en disco duro (HDD) es completamente inadecuado para esta función.

### 6.2 NVMe: PCIe 4.0 vs 5.0

Los SSDs NVMe con interfaz PCIe son el estándar para almacenamiento local de alta velocidad en sistemas de IA. Los dispositivos PCIe 4.0 x4 ofrecen velocidades de lectura secuencial de hasta 7.000 MB/s. Los dispositivos PCIe 5.0 x4 de última generación alcanzan 14.000–15.000 MB/s, aproximadamente el doble. Para sistemas con CPUs que soporten PCIe 5.0 (Intel Sapphire Rapids, AMD EPYC Genoa), el salto a PCIe 5.0 es especialmente relevante cuando el cuello de botella es la carga del dataset.

### 6.3 RAID para entrenamiento

Las configuraciones RAID permiten combinar múltiples discos NVMe para aumentar el ancho de banda o la redundancia. **RAID 0** (striping sin paridad) suma los anchos de banda de todos los discos del array, siendo la opción de mayor rendimiento pero sin tolerancia a fallos. Es apropiado para datos que pueden regenerarse (datasets descargables, checkpoints intermedios). **RAID 5** (striping con paridad distribuida) tolera el fallo de un disco con un coste de rendimiento moderado en escritura. **RAID 10** (espejo + striping) combina rendimiento y tolerancia a fallos duplicando los datos, siendo la opción preferida para almacenamiento de checkpoints críticos donde la pérdida de datos sería catastrófica.

### 6.4 NAS para datasets compartidos

En entornos con múltiples servidores de entrenamiento que comparten el mismo dataset, el uso de almacenamiento en red (Network Attached Storage) mediante protocolos NFS (Network File System) o SMB (Server Message Block) permite centralizar los datos. NFS es el protocolo estándar en entornos Linux; SMB se usa en entornos mixtos Windows/Linux. El rendimiento de un NAS depende tanto del hardware del propio NAS como del ancho de banda de la red que lo conecta con los servidores de entrenamiento.

### 6.5 Almacenamiento distribuido: Lustre, GPFS y Ceph

Para clusters de IA de gran escala, los sistemas de ficheros paralelos son imprescindibles. **Lustre** es el sistema de ficheros paralelo más extendido en supercomputadores y clusters HPC. Separa los metadatos (Metadata Servers, MDS) del almacenamiento de datos (Object Storage Servers, OSS), permitiendo que múltiples clientes lean y escriban simultáneamente a máxima velocidad. **IBM Spectrum Scale (GPFS)** ofrece funcionalidades empresariales avanzadas con soporte comercial. **Ceph** es la alternativa open-source más popular, con soporte nativo de object storage (compatible con S3), block storage y file system, siendo la opción preferida en nubes privadas basadas en OpenStack.

### 6.6 Data staging: hot, warm y cold tiers

Una arquitectura de almacenamiento eficiente para IA organiza los datos en niveles (tiers) según la frecuencia de acceso. El **tier hot** almacena el dataset activo del experimento en curso en NVMe local o en un NAS de alta velocidad conectado por red de 100 Gb/s. El **tier warm** almacena datasets preparados pero no activos en un NAS convencional o almacenamiento de objeto como MinIO. El **tier cold** almacena datos históricos, versiones antiguas de datasets y checkpoints archivados en almacenamiento de objeto económico (Amazon S3 Glacier, Azure Archive Storage, Ceph con compresión).

---

## 7. Red e interconexión

### 7.1 InfiniBand vs Ethernet para clusters GPU

La elección de la red de interconexión entre nodos GPU tiene un impacto directo en la escalabilidad del entrenamiento distribuido. **InfiniBand** es el estándar en supercomputadores y clusters HPC de alto rendimiento. HDR InfiniBand ofrece 200 Gb/s por puerto y latencias inferiores a 1 microsegundo. NDR InfiniBand (la generación actual) alcanza 400 Gb/s por puerto. Su protocolo nativo soporta RDMA (Remote Direct Memory Access), que permite a las GPUs leer y escribir directamente en la memoria de GPUs remotas sin intervención de la CPU ni del sistema operativo, reduciendo drásticamente la latencia y el consumo de CPU.

**Ethernet de alta velocidad** (100 GbE, 200 GbE, 400 GbE) es la alternativa más económica y compatible con infraestructura de red existente. La tecnología RoCE (RDMA over Converged Ethernet) permite usar RDMA sobre Ethernet, aproximando su rendimiento a InfiniBand. NVIDIA ConnectX-7 soporta tanto InfiniBand como Ethernet (RoCE), siendo el adaptador de red más extendido en servidores DGX y en servidores de entrenamiento de alto rendimiento.

### 7.2 NVLink: comunicación GPU intra-nodo

Descrito en la sección 5.3, NVLink resuelve el problema de la comunicación GPU-GPU dentro de un mismo nodo. La diferencia de rendimiento entre un sistema con NVLink (forma SXM) y uno sin él (forma PCIe) es significativa para modelos grandes que requieren model parallelism (división del modelo entre GPUs): NVLink 4.0 ofrece ~7× más ancho de banda que PCIe 5.0 x16.

### 7.3 RDMA y su importancia en entrenamiento distribuido

El entrenamiento de modelos con técnicas de data parallelism requiere sincronizar gradientes entre todos los nodos tras cada paso hacia atrás (backward pass). Esta sincronización se implementa típicamente con operaciones AllReduce, donde cada nodo debe agregar sus gradientes con los de todos los demás. Con decenas o cientos de nodos, la latencia y el ancho de banda de esta comunicación se convierten en el cuello de botella del sistema. RDMA elimina las copias de datos entre buffers de usuario y kernel, reduce la latencia a sub-microsegundo y libera los cores de CPU para otros trabajos, permitiendo que las operaciones colectivas escalen de forma más lineal.

### 7.4 Topologías de red: fat-tree y torus

La **fat-tree** es la topología más común en clusters HPC. En una fat-tree de dos niveles (leaf-spine), cada switch leaf conecta a un grupo de servidores y se conecta a todos los switches spine. La propiedad clave es que el ancho de banda agregado aumenta con cada nivel, eliminando los cuellos de botella en el núcleo de la red. **Clos network** es la generalización multi-nivel de fat-tree, escalable a decenas de miles de nodos.

La topología **torus** (típicamente 3D torus) conecta cada nodo a sus vecinos inmediatos en tres dimensiones, formando una red donde las comunicaciones entre nodos cercanos son muy eficientes. Es la topología utilizada en los sistemas TPU de Google (su red ICI forma un torus 3D) y en algunas implementaciones de InfiniBand para cargas con patrones de comunicación regulares.

### 7.5 Requisitos de red para streaming de datos

Además de la red de interconexión entre GPUs, los servidores de entrenamiento necesitan conectividad hacia el almacenamiento de datos. Un servidor con 8 GPUs H100 puede requerir un ancho de banda de datos de entrada de 10–40 GB/s durante el entrenamiento, lo que equivale a 80–320 Gb/s de red hacia el almacenamiento. Esto justifica el uso de múltiples tarjetas de red de 100 GbE o la conexión directa a almacenamiento NVMe-oF (NVMe over Fabrics).

---

## 8. Instalación e integración física

### 8.1 Refrigeración

El calor generado por los aceleradores modernos es un desafío de ingeniería de primer orden. Una GPU H100 SXM5 disipa hasta 700 W. Un servidor DGX H100 con 8 GPUs puede superar los 10 kW de disipación total. La **refrigeración por aire** convencional se basa en ventiladores que mueven aire frío por el rack y expulsan aire caliente. Para densidades de hasta 15–20 kW por rack, la refrigeración por aire estándar con pasillos fríos/calientes (hot aisle/cold aisle) y unidades de refrigeración de precisión (CRAC/CRAH) puede ser suficiente.

Sin embargo, para sistemas DGX y racks de alta densidad (>20 kW), la **refrigeración líquida directa** (Direct Liquid Cooling, DLC) se está convirtiendo en el estándar. En DLC, placas frías en contacto directo con los chips hacen circular agua a baja temperatura (típicamente 20–45°C). NVIDIA ofrece el DGX H100 en versión air-cooled y liquid-cooled. La refrigeración líquida permite densidades de rack de 50–100 kW y reduce el consumo energético de la refrigeración en un 30–40% respecto al aire.

La **inmersión en dielétrico** (immersion cooling) es la opción más eficiente térmicamente: los servidores se sumergen en un fluido dielétrico que absorbe el calor directamente. Aunque aún es de adopción limitada en IA, está siendo evaluada por grandes hyperscalers para sus clusters de IA de próxima generación.

### 8.2 Alimentación: PDUs, UPS y cálculo de carga eléctrica

La planificación de la alimentación eléctrica es crítica antes de instalar equipos de IA. Los pasos fundamentales son:

1. **Inventario de carga:** sumar el TDP de cada componente (GPUs, CPUs, RAM, almacenamiento, red) más un factor de seguridad del 20–30%.
2. **Selección de PDU:** las Power Distribution Units deben soportar la carga total del rack, generalmente con salidas C13/C19 y monitorización por fase. Para racks de IA de alta densidad se usan PDUs trifásicas de alta capacidad (32A o 63A por fase en EU, 30A o 60A en US).
3. **UPS:** el Sistema de Alimentación Ininterrumpida protege contra micro-cortes y proporciona tiempo para un apagado limpio en cortes prolongados. Para clusters de entrenamiento, un UPS de 10–20 minutos de autonomía es suficiente; los generadores cubren cortes más largos.
4. **Circuitos dedicados:** los servidores de IA de alta densidad requieren circuitos eléctricos dedicados desde el cuadro de distribución, con cableado calibrado para la carga máxima.

### 8.3 Cableado y gestión de cables GPU

Los sistemas de IA modernos generan un volumen de cableado significativo: cables de datos (NVLink, PCIe risers, NVMe U.2/E1.S), cables de alimentación (EPS 8-pin por GPU, múltiples conectores por tarjeta), cables de red (QSFP28/QSFP56 para 100/200 GbE o InfiniBand) y cables de gestión (iDRAC/iLO, consola de serie).

Las buenas prácticas de gestión de cables incluyen el uso de bandejas y organizadores de cable (cable managers), el etiquetado de ambos extremos de cada cable, el uso de longitudes apropiadas (evitar exceso de cable que dificulte el flujo de aire), y la documentación física de cada conexión en el diagrama de rack.

### 8.4 Documentación de rack (diagrama de bastidor)

El diagrama de rack (rack diagram o rack elevation) documenta visualmente la disposición de los equipos en el armario de comunicaciones. Debe incluir: número de unidades de rack (U) de cada equipo y su posición, nombre de host o etiqueta de cada equipo, modelo de cada equipo, asignación de puertos de PDU por equipo, y conexiones de red (port a port). Herramientas como Netbox, Racktables o incluso Visio/draw.io permiten mantener este diagrama actualizado. La documentación precisa es imprescindible para el diagnóstico de problemas, la planificación de capacidad y las auditorías.

### 8.5 Pruebas post-instalación: burn-in y stress test

Una vez instalado el hardware, antes de ponerlo en producción se debe verificar su correcto funcionamiento mediante pruebas de estabilidad:

**Burn-in test:** consiste en someter el sistema a carga máxima sostenida durante un período prolongado (generalmente 24–72 horas) para identificar componentes defectuosos que fallan bajo carga o calor (el fenómeno conocido como "infant mortality" en ingeniería de fiabilidad). En sistemas GPU, esto implica ejecutar kernels que maximicen simultáneamente el uso de Tensor Cores, el ancho de banda de memoria y los núcleos CUDA.

**Herramienta principal: `nvidia-smi`:** la interfaz de línea de comandos de NVIDIA para monitorización y gestión de GPUs. Comandos esenciales durante el burn-in:

```bash
# Monitorización en tiempo real (actualización cada 1 segundo)
nvidia-smi dmon -s pucvmet -d 1

# Información detallada de todas las GPUs
nvidia-smi -q

# Ver temperatura, potencia y utilización
nvidia-smi --query-gpu=index,name,temperature.gpu,power.draw,utilization.gpu,memory.used --format=csv -l 5
```

**Herramientas de stress test para GPU:**
- `gpu_burn`: herramienta open-source que ejecuta operaciones GEMM (General Matrix Multiply) continuas en todas las GPUs y verifica la corrección de los resultados, detectando errores de memoria y de cómputo.
- `CUDA-MEMCHECK` / `compute-sanitizer`: para verificar la integridad de la memoria de la GPU.
- `fio`: para stress test de almacenamiento NVMe.
- `iperf3`: para verificar el ancho de banda de red entre nodos.

Tras el burn-in, se deben verificar: temperatura máxima alcanzada (debe estar por debajo de los límites de throttling del fabricante), ausencia de errores ECC en memoria de GPU (`nvidia-smi -q | grep -A 10 "ECC"`), estabilidad de la frecuencia de reloj bajo carga, y ancho de banda GPU-a-GPU medido con `p2pBandwidthLatencyTest` (incluido en los CUDA samples).

---

## 9. Actividades prácticas

### Actividad 1: Análisis y selección de hardware para un caso de uso concreto

**Descripción:** Se presenta al estudiante un briefing de proyecto de IA con requisitos definidos (por ejemplo: fine-tuning de un modelo de lenguaje de 7B parámetros, dataset de 50 GB, presupuesto de 15.000 USD, plazo de 2 semanas). El estudiante debe proponer una configuración de hardware (GPU, servidor, almacenamiento, red) justificando cada decisión con datos técnicos concretos de los fabricantes.

**Entregable:** Informe de 2 páginas con la configuración propuesta, comparativa de al menos dos alternativas y presupuesto detallado.

**Competencias trabajadas:** Selección de aceleradores, interpretación de especificaciones técnicas, gestión de restricciones de coste y plazo.

### Actividad 2: Uso de `nvidia-smi` para diagnóstico de GPU

**Descripción:** En un sistema con acceso a GPUs NVIDIA (físico o vía entorno cloud como Google Colab Pro o un nodo de HPC académico), el estudiante ejecuta una serie de comandos `nvidia-smi` para obtener información sobre las GPUs disponibles, su temperatura, potencia, utilización y estado de ECC. A continuación, lanza un proceso de carga (por ejemplo, entrenamiento de una red ResNet-50 con PyTorch) y monitoriza el comportamiento de la GPU en tiempo real.

**Entregable:** Capturas de pantalla comentadas de la salida de `nvidia-smi` en reposo y bajo carga, con interpretación de cada métrica clave.

**Competencias trabajadas:** Uso de herramientas de diagnóstico, interpretación de métricas de rendimiento de GPU, detección de anomalías.

### Actividad 3: Diseño de arquitectura de almacenamiento para pipeline de IA

**Descripción:** Dado un pipeline de entrenamiento con las siguientes características (dataset de 500 GB de imágenes en formato JPEG, 4 servidores de entrenamiento con 8 GPUs cada uno, presupuesto de almacenamiento de 20.000 USD), el estudiante diseña la arquitectura de almacenamiento completa, incluyendo el tier hot (NVMe local o NAS), el tier warm (NAS compartido) y el tier cold (object storage), especificando productos concretos, configuraciones RAID y protocolos de red.

**Entregable:** Diagrama de arquitectura (puede ser dibujado a mano o con draw.io) y documento de justificación de decisiones de 1 página.

**Competencias trabajadas:** Diseño de arquitecturas de almacenamiento, comprensión de requisitos de I/O, gestión de coste vs rendimiento.

### Actividad 4: Planificación de instalación física de un rack de IA

**Descripción:** A partir de una lista de equipos (1 servidor DGX H100, 2 servidores de inferencia Dell PowerEdge con L40S, 1 switch de 400 GbE de 32 puertos, 2 PDUs trifásicas, 1 UPS), el estudiante elabora: un diagrama de rack con la posición de cada equipo, un cálculo de carga eléctrica total, un plan de refrigeración (aire o líquida, justificando la elección), y una lista de comprobación (checklist) de pruebas post-instalación.

**Entregable:** Diagrama de rack (en Netbox, draw.io o plantilla proporcionada), hoja de cálculo de carga eléctrica y checklist de pruebas.

**Competencias trabajadas:** Planificación de instalación física, cálculo eléctrico, documentación técnica.

---

## 10. Referencias

### Documentación técnica oficial

- **NVIDIA H100 Tensor Core GPU Datasheet.**
  Descripción de especificaciones, arquitectura Hopper, Transformer Engine y conectividad.
  URL: https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/h100/PB-11133-001_v01.pdf

- **NVIDIA H100 SXM Whitepaper: NVIDIA Hopper Architecture In-Depth.**
  Análisis técnico de la arquitectura Hopper, Tensor Cores de 4ª generación y NVLink 4.0.
  URL: https://resources.nvidia.com/en-us-tensor-core/gtc22-whitepaper-hopper

- **NVIDIA AI Infrastructure: Design and Best Practices (NVIDIA Whitepaper).**
  Guía de diseño de infraestructura para centros de datos de IA, incluyendo networking, almacenamiento y refrigeración.
  URL: https://www.nvidia.com/en-us/data-center/resources/

- **NVIDIA DGX H100 System Architecture.**
  Especificaciones completas del sistema DGX H100, NVSwitch y gestión térmica.
  URL: https://www.nvidia.com/en-us/data-center/dgx-h100/

### Benchmarks y estándares de la industria

- **MLCommons MLPerf Training Benchmarks.**
  Benchmarks de referencia para comparar el rendimiento de sistemas de IA en cargas de entrenamiento estándar (ResNet-50, BERT, GPT-3).
  URL: https://mlcommons.org/en/training-normal-31/

- **MLCommons MLPerf Inference Benchmarks.**
  Benchmarks equivalentes para cargas de inferencia con métricas de latencia y throughput.
  URL: https://mlcommons.org/en/inference-datacenter-31/

### Documentación de herramientas

- **NVIDIA CUDA Documentation.**
  Referencia completa del modelo de programación CUDA, gestión de memoria GPU y herramientas de diagnóstico (nvidia-smi, Nsight Systems, Nsight Compute).
  URL: https://docs.nvidia.com/cuda/

- **NVIDIA nvidia-smi Reference Guide.**
  Referencia completa de todos los parámetros y opciones de la herramienta de línea de comandos nvidia-smi.
  URL: https://developer.nvidia.com/nvidia-system-management-interface

- **AMD ROCm Documentation.**
  Documentación del ecosistema de software open-source de AMD para aceleradores de IA, incluyendo soporte para PyTorch y TensorFlow en GPUs Instinct.
  URL: https://rocm.docs.amd.com/

### Libros de referencia

- **Gorelick, M. y Ozsvald, I. (2020). *High Performance Python: Practical Performant Programming for Humans* (2ª ed.). O'Reilly Media.**
  Cubre técnicas de optimización de rendimiento en Python con aplicaciones directas a pipelines de datos para IA, incluyendo el uso eficiente de memoria y paralelización.
  URL: https://www.oreilly.com/library/view/high-performance-python/9781492055013/

- **Patterson, D. y Hennessy, J. (2021). *Computer Organization and Design: ARM Edition* (5ª ed.). Morgan Kaufmann.**
  Fundamentos de arquitectura de computadores necesarios para comprender el funcionamiento interno de GPUs y aceleradores especializados.

### Artículos y recursos adicionales

- **Google Cloud TPU Documentation.**
  Documentación sobre arquitectura TPU v4/v5e, casos de uso y comparativa con GPU para cargas JAX/TensorFlow.
  URL: https://cloud.google.com/tpu/docs/intro-to-tpu

- **InfiniBand Trade Association (IBTA).**
  Especificaciones técnicas de los estándares InfiniBand HDR/NDR.
  URL: https://www.infinibandta.org/

- **Lustre File System Documentation.**
  Documentación de arquitectura, configuración y tuning del sistema de ficheros paralelo Lustre, ampliamente usado en clusters HPC y de IA.
  URL: https://www.lustre.org/documentation/

- **NVIDIA ConnectX-7 Datasheet.**
  Especificaciones del adaptador de red para InfiniBand y Ethernet de alta velocidad con soporte RDMA.
  URL: https://www.nvidia.com/en-us/networking/infiniband/connectx-7/

---

*Unidad Didáctica 1 — Módulo Profesional 01 — CFS2 Instalación, despliegue y explotación de sistemas de IA*
*Última revisión: junio 2026*
