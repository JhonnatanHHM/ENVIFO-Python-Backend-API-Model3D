from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import shutil
import subprocess
import os
import uuid

app = FastAPI()

DATA_DIR = Path("/app/data")
SCRIPTS_DIR = Path("/app/scripts")
DATA_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/generate-model")
async def generate_model(
    image: UploadFile = File(...),
    width: float = Form(...),
    height: float = Form(...),
    depth: float = Form(...)
):
    # Guardar imagen temporalmente
    image_id = str(uuid.uuid4())
    image_path = DATA_DIR / f"{image_id}_{image.filename}"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Definir ruta de salida del modelo
    glb_path = DATA_DIR / f"{image_id}.glb"

    # Construir comando para Blender
    blender_cmd = [
        "blender",
        "--background",
        "--python", str(SCRIPTS_DIR / "generate_model.py"),
        "--",
        str(image_path),
        str(width),
        str(height),
        str(depth),
        str(glb_path)
    ]

    # Ejecutar Blender y capturar logs
    result = subprocess.run(
        blender_cmd,
        capture_output=True,
        text=True
    )

    # Mostrar logs del script de Blender en los logs del contenedor
    print("========== BLENDER STDOUT ==========")
    print(result.stdout)
    print("========== BLENDER STDERR ==========")
    print(result.stderr)

    # Manejo de errores
    if result.returncode != 0 or not glb_path.exists():
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Error al generar el modelo 3D",
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        )

    # Devolver el archivo GLB generado
    return FileResponse(
        path=glb_path,
        filename=glb_path.name,
        media_type="model/gltf-binary"
    )