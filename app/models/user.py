from sqlmodel import Field, SQLModel
from typing import Optional


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    active_token: Optional[str] = Field(default=None)
