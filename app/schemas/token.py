# app/schemas/token.py
from pydantic import BaseModel


# Esquema para responder al Frontend (lo que devuelve /login)
class Token(BaseModel):
    access_token: str
    token_type: str


# Esquema para leer los datos DENTRO del token (decodificación)
class TokenPayload(BaseModel):
    sub: str | None = None
