FROM blender:3.6.0 as blender

# Imagen base de Python
FROM python:3.10-slim

# Copiar Blender desde la imagen oficial
COPY --from=blender /blender /blender
ENV PATH="/blender:${PATH}"

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libgl1 libx11-6 libxi6 libxxf86vm1 libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de la app
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación
COPY . .

# Exponer puerto FastAPI
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
