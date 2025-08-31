from rabbitmq_client import send_to_java_api

# Mensaje de prueba
payload = {"test": "conexion exitosa"}

# Enviar a la cola "materials_queue" (la misma que usas en tu app)
send_to_java_api(payload, queue_name="materials_queue")
