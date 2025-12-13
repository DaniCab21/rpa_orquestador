from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

# Nota: Necesitamos importar Bot solo para tipos, pero para evitar ciclos
# a veces se usan strings en Relationship.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.bot import Bot


class Execution(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bot_id: int = Field(foreign_key="bot.id")
    status: str = Field(default="pending")  # pending, working, completed, failed
    log_text: Optional[str] = None  # Mensaje del resultado o error
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None

    # Relación (Opcional por ahora, útil para consultas avanzadas)
    # bot: "Bot" = Relationship(back_populates="executions")
