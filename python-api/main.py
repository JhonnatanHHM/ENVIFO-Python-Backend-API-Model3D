from fastapi import FastAPI, UploadFile, File, Form
import json
import os
import tempfile
from blender_service import generate_3d_model
from rabbitmq_client import send_to_java_api
from services.storage_service import upload_to_bucket
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.post("/process-material/")
async def process_material(
    material: str = Form(...),
    imagen: UploadFile = File(...)
):
    material_dto = json.loads(material)

    # Crear directorio temporal que se elimina automáticamente
    with tempfile.TemporaryDirectory() as temp_dir:
        image_path = os.path.join(temp_dir, imagen.filename)
        with open(image_path, "wb") as f:
            f.write(await imagen.read())

        # Generar modelo 3D
        glb_path = generate_3d_model(
            image_path,
            width=material_dto["width"],
            height=material_dto["height"],
            depth=1
        )

        # Subir archivos a bucket
        bucket_name = os.getenv("R2_BUCKET")
        image_url = upload_to_bucket(bucket_name, image_path, f"images/{imagen.filename}")
        glb_url = upload_to_bucket(bucket_name, glb_path, f"models/{os.path.basename(glb_path)}")

        # Enviar a la API de Java
        payload = {
            "material": material_dto,
            "imageUrl": image_url,
            "modelUrl": glb_url,
            "status": "success"
        }
        send_to_java_api(payload)

    # Al salir del bloque `with`, temp_dir y todos sus archivos se eliminan automáticamente

    return {
        "status": "processed",
        "material": material_dto,
        "image_url": image_url,
        "model_url": glb_url
    }
