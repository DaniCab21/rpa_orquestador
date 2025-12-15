from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.db.session import get_session
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead

router = APIRouter()


# --- FUNCIÓN AUXILIAR ---
def authenticate(session: Session, email: str, password: str) -> User | None:
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


@router.post("/signup", response_model=UserRead)
def signup(user_in: UserCreate, session: Session = Depends(get_session)) -> Any:
    # 1. Verificar si existe
    existing_user = session.exec(
        select(User).where(User.email == user_in.email)
    ).first()
    print(existing_user)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="El usuario con este email ya existe en el sistema.",
        )

    # 2. Crear usuario
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login_access_token(
    session: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    # 1. Autenticar
    user = authenticate(session, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Email o contraseña incorrectos")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")

    # 2. Gestión de Sesión Única (KICK - Patear sesión anterior)
    # Simplemente ignoramos si ya tiene token, porque lo vamos a sobrescribir
    # if user.active_token:
    #     pass

    # 3. Crear Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # IMPORTANTE: Aquí usamos 'subject', que debe coincidir con security.py
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )

    # 4. Guardar sesión activa en BD
    user.active_token = access_token
    session.add(user)
    session.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    current_user.active_token = None
    session.add(current_user)
    session.commit()
    return {"msg": "Sesión cerrada correctamente"}
