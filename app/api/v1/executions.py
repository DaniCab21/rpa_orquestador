# app/api/v1/executions.py
from fastapi import APIRouter, Depends
from app.api.v1.deps import get_current_user  # Importamos el guardia
from app.tasks import run_bot_task

router = APIRouter()


@router.post("/{bot_name}")
def execute_bot(
    bot_name: str,
    url: str = "https://www.google.com",  # Parámetro opcional
    current_user=Depends(get_current_user),  # Protegido
):
    # Enviamos la tarea a Celery
    task = run_bot_task.delay(bot_name, url)

    return {
        "message": "Ejecución programada",
        "task_id": task.id,
        "target_url": url,
        "status": "Queued",
    }
