import jwt
from datetime import timedelta

from jwt import PyJWTError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.core.config import settings
from app.db.session import get_session
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, Token
from app.api.v1.deps import get_current_user
from app.schemas.token import Token

router = APIRouter()


# --- FUNCIÓN QUE FALTABA (Usando tus herramientas existentes) ---
def authenticate(session: Session, email: str, password: str):
    # 1. Buscamos al usuario por email
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    # 2. Si no existe, retornamos None
    if not user:
        return None

    # 3. Usamos TU función verify_password de security.py
    if not verify_password(password, user.hashed_password):
        return None

    return user


# 1. REGISTRO DE USUARIO
@router.post("/signup", response_model=UserRead)
def signup(user_in: UserCreate, session: Session = Depends(get_session)):
    # Verificar si ya existe
    existing_user = session.exec(
        select(User).where(User.email == user_in.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    # Crear usuario (hasheando la contraseña)
    user = User(
        email=user_in.email, hashed_password=get_password_hash(user_in.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# app/api/v1/auth.py


@router.post("/login", response_model=Token)  # Asegúrate que la ruta sea "/login"
def login_access_token(
    session: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    # 1. Autenticar credenciales
    user = authenticate(session, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Email o contraseña incorrectos")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")

    # 2. VALIDACIÓN DE SESIÓN ÚNICA (ESTRATEGIA: KICK / PATEAR)
    # Si ya tiene token, NO bloqueamos. Dejamos que se genere uno nuevo.
    # El nuevo token sobrescribirá al viejo en la línea "user.active_token = access_token"
    # invalidando automáticamente la sesión anterior.
    if user.active_token:
        pass  # <--- CAMBIO CLAVE: Antes había un raise 409 aquí. Ahora no hacemos nada.

    # 3. Crear nuevo token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )

    # 4. Guardar el nuevo token (Esto mata la sesión anterior)
    user.active_token = access_token
    session.add(user)
    session.commit()
    session.refresh(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Limpia la sesión activa del usuario en la base de datos.
    """
    current_user.active_token = None
    session.add(current_user)
    session.commit()
    return {"msg": "Sesión cerrada correctamente"}
