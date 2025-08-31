from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

class ModelRequest(BaseModel):
    shape: str
    size: float

@app.post("/generate-model")
def generate_model(req: ModelRequest):
    script_path = os.path.join("scripts", "generate_model.py")

    try:
        # Ejecutar Blender en modo background con el script
        subprocess.run([
            "blender", "-b", "-P", script_path,
            "--", req.shape, str(req.size)
        ], check=True)

        return {"status": "success", "message": "Modelo generado"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "details": str(e)}
