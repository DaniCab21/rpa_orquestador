import os
from celery import Celery

# Leemos la URL de las variables de entorno (definidas en docker-compose)
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "rpa_worker",
    broker=broker_url,
    backend=broker_url,  # Para guardar resultados si quisieras
)

# Configuración opcional para ver tareas claras
celery_app.conf.imports = (
    "app.tasks",  # Le decimos al worker que busque las tareas aquí
)
