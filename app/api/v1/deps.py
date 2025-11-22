from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
import jwt
from sqlmodel import Session

from app.core.config import settings
from app.db.session import get_session
from app.models.user import User

# OAuth2PasswordBearer le dice a Swagger que busque un botón de "Authorize" (candadito)
# y que el token se envía a la URL "/auth/login" para obtenerse.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> User:
    """
    Esta función es el GUARDIA.
    1. Recibe el token del Header 'Authorization: Bearer ...'
    2. Intenta decodificarlo con la SECRET_KEY.
    3. Si funciona, busca al usuario en la BD.
    4. Si todo está bien, devuelve el objeto User.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Intentamos leer la tarjeta (Token)
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")  # 'sub' es donde guardamos el ID
        if user_id is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    # Buscamos si el dueño de la tarjeta sigue existiendo en la BD
    user = session.get(User, int(user_id))
    if user is None:
        raise credentials_exception

    return user
