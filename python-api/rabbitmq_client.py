import os
import pika
import json
from dotenv import load_dotenv 

# Cargar .env 
load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

def send_to_java_api(payload: dict, queue_name: str = "materials_queue"):
    """
    Envía un mensaje a la API en Java vía RabbitMQ.
    Ahora recibe directamente un payload (dict).
    Si hay un error, lo encapsula en el mensaje y lo reintenta enviar.
    """
    try:
        # Configuración conexión RabbitMQ
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials
        )

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Asegurar la cola
        channel.queue_declare(queue=queue_name, durable=True)

        # Publicar el mensaje
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistencia del mensaje
            )
        )

        print(f"[RabbitMQ] Mensaje enviado: {payload}")

        connection.close()

    except Exception as e:
        error_payload = {
            "status": "error",
            "error": str(e),
            "original_payload": payload
        }

        try:
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials
            )
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue=queue_name, durable=True)

            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=json.dumps(error_payload),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )

            print(f"[RabbitMQ] Error enviado: {error_payload}")
            connection.close()
        except Exception as fatal:
            print(f"[RabbitMQ] Error fatal: {fatal}")
