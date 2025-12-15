from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, desc

from app.db.session import get_session
from app.api.v1.deps import get_current_user
from app.tasks import run_bot_task
from app.models.execution import Execution
from app.schemas.executions import ExecutionRead

router = APIRouter()


# 1. EJECUTAR UN BOT (Ya lo tenías, solo lo mantenemos)
@router.post("/{bot_name}")
def execute_bot(
    bot_name: str,
    url: str = "https://www.google.com",
    current_user=Depends(get_current_user),
):
    task = run_bot_task.delay(bot_name, url)
    return {
        "message": "Ejecución programada",
        "task_id": task.id,
        "target_url": url,
        "status": "Queued",
    }


# 2. LISTAR EJECUCIONES (NUEVO)
# Permite filtrar por bot_id (ej: /executions?bot_id=1)
@router.get("/", response_model=List[ExecutionRead])
def read_executions(
    bot_id: Optional[int] = None,
    offset: int = 0,
    limit: int = 20,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),  # Seguridad activada
):
    query = select(Execution)

    # Si nos pasan un bot_id, filtramos. Si no, traemos de todos.
    if bot_id:
        query = query.where(Execution.bot_id == bot_id)

    # Ordenamos: Las más recientes primero
    query = query.order_by(desc(Execution.started_at))

    # Paginación básica
    query = query.offset(offset).limit(limit)

    executions = session.exec(query).all()
    return executions
