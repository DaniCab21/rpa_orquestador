from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ExecutionBase(BaseModel):
    status: str
    log_text: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime] = None


class ExecutionRead(ExecutionBase):
    id: int
    bot_id: int
