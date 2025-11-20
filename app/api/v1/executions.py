from fastapi import APIRouter
from app.tasks import run_bot_task

router = APIRouter()

@router.post("/{bot_name}")
def execute_bot(bot_name: str):
    # .delay() es el método mágico de Celery que envía la tarea a Redis
    # NO bloquea la API. Retorna casi instantáneamente.
    task = run_bot_task.delay(bot_name, 3)  # 3 segundos de simulación
    
    return {
        "message": "Ejecución programada", 
        "task_id": task.id,
        "status": "Queued"
    }