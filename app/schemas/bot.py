from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime


# Base: Lo que comparten todos (para evitar repetir código)
class BotBase(SQLModel):
    name: str
    description: Optional[str] = None
    status: str = "idle"


# Create: Lo que el usuario nos manda para crear (Validación de entrada)
class BotCreate(BotBase):
    pass
    # Es igual al Base, pero si quisieras obligar un campo extra solo al crear, iría aquí.


# --- NUEVO: Esquema para Actualizar ---
# Fíjate que aquí TODO es Optional, porque no estás obligado a cambiar todo
class BotUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


# Read: Lo que nosotros le respondemos al usuario (Validación de salida)
class BotRead(BotBase):
    id: int
    created_at: datetime
    last_analysis: Optional[str] = None
