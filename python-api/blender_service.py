import os
import requests

BLENDER_HOST = os.getenv("BLENDER_HOST", "blender")
BLENDER_PORT = os.getenv("BLENDER_PORT", "8080")

def generate_3d_model(image_path: str, width: float = 2, height: float = 2, depth: float = 0.1) -> str:
    """
    Envía la imagen y parámetros al servicio Blender en otro contenedor
    que expone un API REST, y recibe la ruta/URL del modelo generado.
    """
    url = f"http://{BLENDER_HOST}:{BLENDER_PORT}/generate-model"

    with open(image_path, "rb") as f:
        files = {"imagen": f}
        data = {
            "width": width,
            "height": height,
            "depth": depth
        }
        response = requests.post(url, files=files, data=data)

    response.raise_for_status()
    result = response.json()

    print(f"[Blender] Modelo generado: {result}")
    return result["glb_url"]
