from sqlmodel import SQLModel


# Lo que el usuario envía para registrarse
class UserCreate(SQLModel):
    email: str
    password: str


# Lo que devolvemos al usuario (¡Nunca devolvemos la password!)
class UserRead(SQLModel):
    id: int
    email: str
    is_active: bool


# Estructura de respuesta del Token
class Token(SQLModel):
    access_token: str
    token_type: str
