# Etapa 1: usar una imagen de Blender existente
FROM linuxserver/blender:version-3.6.3 as blender

# Etapa 2: imagen base de Python
FROM python:3.10-slim

# Copiar Blender desde la primera etapa
COPY --from=blender /blender /blender
ENV PATH="/blender:${PATH}"

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libgl1 libx11-6 libxi6 libxxf86vm1 libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de la aplicación
WORKDIR /app

# Copiar y activar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto FastAPI
EXPOSE 8080

# Comando por defecto
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
