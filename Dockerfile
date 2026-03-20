# Utilizamos la imagen oficial de PyTorch de RunPod con CUDA 12
FROM runpod/pytorch:2.2.1-py3.10-cuda12.1.1-devel-ubuntu22.04

# Instalar OPUS y dependencias del sistema necesarias para audio
RUN apt-get update && apt-get install -y \
    libopus-dev \
    git \
    wget \
    sox \
    libsox-fmt-all \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clonar el repositorio oficial de PersonaPlex
RUN git clone https://github.com/NVIDIA/personaplex.git /app/personaplex

WORKDIR /app/personaplex

# Instalar PersonaPlex y Moshi del repositorio (que trae dependencias atadas)
RUN pip install --no-cache-dir moshi/.

# Instalar el SDK de RunPod para Serverless
RUN pip install runpod pydub

# Crear el directorio para los pesos del modelo
RUN mkdir -p /models

# Agregar el script manejador de Serverless que escribiremos
COPY handler.py /app/personaplex/handler.py

# Iniciar el Serverless Handler cuando inicie el contenedor RunPod
CMD [ "python", "-u", "/app/personaplex/handler.py" ]
