import os
from celery import Celery
from celery.schedules import crontab
# Leemos la URL de las variables de entorno (definidas en docker-compose)
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "rpa_worker",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0"),
)

# Configuración opcional para ver tareas claras
celery_app.conf.imports = (
    "app.tasks",  # Le decimos al worker que busque las tareas aquí
)

# 👇 2. AQUÍ DEFINIMOS EL HORARIO
# celery_app.conf.beat_schedule = {
#     "ejecutar-bot-noticias-cada-minuto": {
#         "task": "run_bot_task",  # El nombre exacto de la función decorada con @task
#         "schedule": 60.0,  # Cada 60 segundos (Intervalo)
#         # "schedule": crontab(hour=8, minute=0), # Opción B: Todos los días a las 8:00 AM
#         "args": (
#             "NewsBot",
#             "https://www.bbc.com/mundo",
#         ),  # Argumentos: (NombreBot, URL)
#     },
# }

# celery_app.conf.timezone = "UTC"
