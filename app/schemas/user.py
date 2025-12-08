from sqlmodel import SQLModel, Field


# Lo que el usuario envía para registrarse
class UserCreate(SQLModel):
    email: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=4, max_length=50)


# Lo que devolvemos al usuario (¡Nunca devolvemos la password!)
class UserRead(SQLModel):
    id: int
    email: str
    is_active: bool


# Estructura de respuesta del Token
class Token(SQLModel):
    access_token: str
    token_type: str
