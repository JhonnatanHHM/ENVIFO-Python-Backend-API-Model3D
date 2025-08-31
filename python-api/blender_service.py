import os
import requests
import tempfile

BLENDER_HOST = os.getenv("BLENDER_HOST", "blender")
BLENDER_PORT = os.getenv("BLENDER_PORT", "8080")

def generate_3d_model(image_path: str, width: float = 2, height: float = 2, depth: float = 0.1) -> str:
    """
    Envía la imagen y parámetros al servicio Blender en otro contenedor
    que expone un API REST, y recibe el archivo .glb generado.
    """
    url = f"http://{BLENDER_HOST}:{BLENDER_PORT}/generate-model"

    with open(image_path, "rb") as f:
        files = {"imagen": f}
        data = {"width": width, "height": height, "depth": depth}

        response = requests.post(url, files=files, data=data, stream=True)
        response.raise_for_status()

        # Guardar archivo temporal
        temp_dir = tempfile.mkdtemp()
        glb_path = os.path.join(temp_dir, "model.glb")

        with open(glb_path, "wb") as out:
            for chunk in response.iter_content(chunk_size=8192):
                out.write(chunk)

    print(f"[Blender] Modelo generado en {glb_path}")
    return glb_path
