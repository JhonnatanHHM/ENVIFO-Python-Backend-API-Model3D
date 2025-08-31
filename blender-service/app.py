from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import tempfile
import os
import shutil
import subprocess
from pathlib import Path

app = FastAPI()

# Carpeta temporal de salida dentro del contenedor
OUTPUT_DIR = Path("/app/data")
OUTPUT_DIR.mkdir(exist_ok=True)

@app.post("/generate-model")
async def generate_model(
    imagen: UploadFile = File(...),
    width: float = Form(...),
    height: float = Form(...),
    depth: float = Form(...)
):
    """
    Recibe la imagen y dimensiones desde python-api,
    genera el .glb con Blender y lo devuelve al cliente.
    """
    # Guardar imagen temporalmente
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / imagen.filename
        with open(input_path, "wb") as f:
            f.write(await imagen.read())

        # Ruta de salida
        output_path = OUTPUT_DIR / f"{imagen.filename.split('.')[0]}.glb"

        # Ejecutar Blender
        script_path = Path("scripts/generate_model.py")
        command = [
            "blender", "-b", "-P", str(script_path), "--",
            str(input_path),
            str(width),
            str(height),
            str(depth),
            str(output_path)
        ]
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            return {"status": "error", "details": e.stderr.decode()}

        # Devolver el archivo .glb generado
        return FileResponse(
            path=output_path,
            media_type="model/gltf-binary",
            filename=output_path.name
        )
