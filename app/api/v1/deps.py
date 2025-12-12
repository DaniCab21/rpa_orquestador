from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
import jwt
from sqlmodel import Session, select

from app.core.config import settings
from app.db.session import get_session
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    # Buscamos por Email
    statement = select(User).where(User.email == user_email)
    user = session.exec(statement).first()

    if user is None:
        raise credentials_exception

    # --- ¡ESTA ES LA PARTE IMPORTANTE! ---
    # Verifica que estas líneas NO tengan el símbolo '#' al principio
    if user.active_token != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión caducada o iniciada en otro dispositivo",
        )
    # -------------------------------------

    return user
