from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import os
from fastapi.responses import FileResponse

app = FastAPI()

class ModelRequest(BaseModel):
    width: float
    height: float
    depth: float
    image_path: str

@app.post("/generate-model")
def generate_model(req: ModelRequest):
    script_path = os.path.join("scripts", "generate_model.py")
    output_path = os.path.join("output", "model.glb")

    try:
        subprocess.run([
            "blender", "-b", "-P", script_path,
            "--", req.image_path, str(req.width), str(req.height), str(req.depth), output_path
        ], check=True)

        return FileResponse(output_path, media_type="model/gltf-binary", filename="model.glb")

    except subprocess.CalledProcessError as e:
        return {"status": "error", "details": str(e)}
