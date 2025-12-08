from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import Text, Column

class Bot(SQLModel, table=True):
    # table=True le dice a SQLModel que esto representa una tabla en Postgres

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)  # index=True hace que buscar por nombre sea rápido
    description: Optional[str] = None
    status: str = Field(default="idle")  # idle, running, error
    # default_factory ejecuta la función al momento de insertar
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_analysis: Optional[str] = Field(default=None, sa_column=Column(Text))
    last_analysis_at: Optional[datetime] = Field(default=None)
