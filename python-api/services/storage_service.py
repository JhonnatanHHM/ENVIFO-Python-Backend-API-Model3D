# storage_service.py
import os
import boto3
from dotenv import load_dotenv
from pathlib import Path

# Cargar .env
load_dotenv()

# Cargar credenciales desde variables de entorno
ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
SECRET_KEY = os.getenv("R2_SECRET_KEY")
ENDPOINT = os.getenv("R2_ENDPOINT")
REGION = os.getenv("R2_REGION", "auto")

# Cliente S3 compatible con Cloudflare R2
s3 = boto3.client(
    "s3",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    endpoint_url=ENDPOINT,
    region_name=REGION
)

def upload_to_bucket(bucket_name: str, file_path: str, object_name: str):
    """
    Sube un archivo al bucket R2.

    :param bucket_name: Nombre del bucket.
    :param file_path: Ruta local absoluta o relativa al archivo.
    :param object_name: Ruta/clave dentro del bucket.
    :return: URL de acceso directo al archivo en R2.
    """
    file_path = Path(file_path).resolve()  # Normalizar a absoluta
    if not file_path.exists():
        raise FileNotFoundError(f"❌ El archivo {file_path} no existe.")

    s3.upload_file(str(file_path), bucket_name, object_name)
    print(f"✅ Archivo {file_path} subido como {object_name} en bucket {bucket_name}")

    return f"{ENDPOINT}/{bucket_name}/{object_name}"
