from datetime import datetime, timedelta
from typing import Any, Union
import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Configuramos el "triturador" de contraseñas (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    Crea la 'Tarjeta del Hotel' (JWT).
    Toma el ID del usuario (subject) y le pone fecha de caducidad.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # El Payload es la info que va dentro del token (visible pero no modificable)
    to_encode = {"exp": expire, "sub": str(subject)}

    # Aquí ocurre la magia: Firmamos con la SECRET_KEY
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contraseña normal con su versión triturada."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Tritura una contraseña para guardarla en la BD."""
    return pwd_context.hash(password)
