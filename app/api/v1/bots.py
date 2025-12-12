from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import func  # <--- Para hacer COUNT
from typing import List

from app.db.session import get_session
from app.models.bot import Bot
from app.schemas.bot import BotCreate, BotRead, BotUpdate

router = APIRouter()


# 1. Crear un Bot (POST)
@router.post("/", response_model=BotRead)
def create_bot(bot_data: BotCreate, session: Session = Depends(get_session)):
    # Convertimos el Schema (BotCreate) al Modelo de BD (Bot)
    bot_db = Bot.model_validate(bot_data)

    session.add(bot_db)
    session.commit()
    session.refresh(
        bot_db
    )  # Recarga el objeto con el ID y created_at generados por la BD
    return bot_db


# 2. Listar Bots (GET)
@router.get("/", response_model=List[BotRead])
def read_bots(session: Session = Depends(get_session)):
    bots = session.exec(select(Bot)).all()
    print("XXXX" + str(bots))
    return bots


# 3. Obtener un Bot específico (GET)
@router.get("/{bot_id}", response_model=BotRead)
def read_bot(bot_id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot no encontrado")
    return bot


# 4. ACTUALIZAR UN BOT (PUT/PATCH)
@router.patch("/{bot_id}", response_model=BotRead)
def update_bot(
    bot_id: int, bot_update: BotUpdate, session: Session = Depends(get_session)
):
    # 1. Buscar
    bot_db = session.get(Bot, bot_id)
    if not bot_db:
        raise HTTPException(status_code=404, detail="Bot no encontrado")

    # 2. Copiar datos nuevos sobre los viejos
    # exclude_unset=True significa: "Si el usuario no envió este campo, no lo toques"
    bot_data = bot_update.model_dump(exclude_unset=True)

    for key, value in bot_data.items():
        setattr(bot_db, key, value)

    # 3. Guardar
    session.add(bot_db)
    session.commit()
    session.refresh(bot_db)
    return bot_db


# 5. ELIMINAR UN BOT (DELETE)
@router.delete("/{bot_id}")
def delete_bot(bot_id: int, session: Session = Depends(get_session)):
    bot_db = session.get(Bot, bot_id)
    if not bot_db:
        raise HTTPException(status_code=404, detail="Bot no encontrado")

    session.delete(bot_db)
    session.commit()

    return {"message": "Bot eliminado correctamente", "id": bot_id}


# 6. OBTENER ESTADÍSTICAS (KPIs)
@router.get("/stats/overview")
def get_bot_stats(session: Session = Depends(get_session)):
    # Total de bots
    total_bots = session.exec(select(func.count(Bot.id))).one()
    print(f"Total de bots en sistema: {total_bots}")
    # Conteo por estado (Agrupación)
    # Esto equivale a: SELECT status, COUNT(*) FROM bot GROUP BY status
    statement = select(Bot.status, func.count(Bot.id)).group_by(Bot.status)
    results = session.exec(statement).all()

    # Convertimos la lista de tuplas en un diccionario fácil de leer
    # Ej: [('idle', 5), ('completed', 2)] -> {'idle': 5, 'completed': 2}
    status_counts = {status: count for status, count in results}

    return {"total": total_bots, "by_status": status_counts}
