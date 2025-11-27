from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.db.session import get_session
from app.models.bot import Bot
from app.schemas.bot import BotCreate, BotRead

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
    return bots


# 3. Obtener un Bot específico (GET)
@router.get("/{bot_id}", response_model=BotRead)
def read_bot(bot_id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot no encontrado")
    return bot
