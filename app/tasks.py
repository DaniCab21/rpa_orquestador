import time
from app.celery_worker import celery_app

@celery_app.task(name="run_bot_task")
def run_bot_task(bot_name: str, duration: int):
    print(f"🤖 [INICIO] El bot '{bot_name}' ha comenzado a trabajar...")
    
    # Simulamos un proceso largo (RPA)
    time.sleep(duration)
    
    print(f"✅ [FIN] El bot '{bot_name}' terminó exitosamente tras {duration} segundos.")
    return f"Reporte generado por {bot_name}"