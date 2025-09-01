# -----------------------------
# Blender Headless 4.1 + Python
# -----------------------------

# Etapa 1: imagen base headless Blender
FROM blenderkit/headless-blender:blender-4.1 as blender

# Etapa 2: imagen base Python
FROM python:3.10-slim

# Copiar Blender desde la primera etapa
COPY --from=blender /home/headless/blender /blender

# Asegurar que Blender esté en PATH
ENV PATH="/blender:${PATH}"
RUN ln -s /blender/blender /usr/bin/blender

# Instalar librerías de sistema necesarias para Blender
RUN apt-get update && apt-get install -y \
    libgl1 \
    libx11-6 \
    libxi6 \
    libxxf86vm1 \
    libxrender1 \
    libxext6 \
    libxfixes3 \
    libxkbcommon0 \
    libglib2.0-0 \
    libfontconfig1 \
    libfreetype6 \
    libsm6 \
    libice6 \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar scripts y app
COPY . .

# Carpeta para archivos generados
RUN mkdir -p /app/data

# Exponer puerto FastAPI
EXPOSE 8080

# Comando por defecto
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
