from fastapi import FastAPI, UploadFile, File, Form
import json
import os
import tempfile
import requests
from blender_service import generate_3d_model  # si lo necesitas internamente
from rabbitmq_client import send_to_java_api
from services.storage_service import upload_to_bucket
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <- o restringir al dominio de tu front
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Construir la URL de Blender desde host y puerto
BLENDER_HOST = os.getenv("BLENDER_HOST", "http://blender")
BLENDER_PORT = os.getenv("BLENDER_PORT", "8080")
BLENDER_URL = f"{BLENDER_HOST}:{BLENDER_PORT}"

@app.post("/process-material/")
async def process_material(
    material: str = Form(...),
    imagen: UploadFile = File(...)
):
    """
    Recibe un material (JSON) y una imagen, llama al servicio Blender para generar un modelo 3D,
    sube los archivos a R2 bucket y notifica a la API de Java.
    """

    material_dto = json.loads(material)

    # Crear directorio temporal
    with tempfile.TemporaryDirectory() as temp_dir:
        image_path = os.path.join(temp_dir, imagen.filename)
        with open(image_path, "wb") as f:
            f.write(await imagen.read())

        # Preparar datos para enviar a Blender
        data = {
            "width": str(material_dto["width"]),
            "height": str(material_dto["height"]),
            "depth": str(material_dto.get("depth", 1.0))  # Default depth si no viene
        }
        files = {"image": open(image_path, "rb")}

        # Llamar al servicio Blender
        blender_resp = requests.post(f"{BLENDER_URL}/generate-model", data=data, files=files)
        files["image"].close()

        if blender_resp.status_code != 200:
            return {
                "status": "error",
                "detail": blender_resp.text
            }

        # Guardar el archivo GLB temporalmente para subirlo
        glb_temp_path = os.path.join(temp_dir, "model.glb")
        with open(glb_temp_path, "wb") as f:
            f.write(blender_resp.content)

        # Subir archivos a Cloudflare R2
        bucket_name = os.getenv("R2_BUCKET")
        image_url = upload_to_bucket(bucket_name, image_path, f"images/{imagen.filename}")
        glb_url = upload_to_bucket(bucket_name, glb_temp_path, f"models/{os.path.basename(glb_temp_path)}")

        # Enviar payload a la API de Java
        payload = {
            "material": material_dto,
            "imageUrl": image_url,
            "modelUrl": glb_url,
            "status": "success"
        }
        send_to_java_api(payload)

    return {
        "status": "processed",
        "material": material_dto,
        "image_url": image_url,
        "model_url": glb_url
    }
