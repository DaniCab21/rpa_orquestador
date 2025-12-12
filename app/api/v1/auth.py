from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.db.session import get_session
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, Token

router = APIRouter()

# 1. REGISTRO DE USUARIO
@router.post("/signup", response_model=UserRead)
def signup(user_in: UserCreate, session: Session = Depends(get_session)):
    # Verificar si ya existe
    existing_user = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Crear usuario (hasheando la contraseña)
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password) # <--- TRITURADO
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# 2. LOGIN (Obtener Token)
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), # Esto captura username/password del form estándar
    session: Session = Depends(get_session)
):
    # Buscamos al usuario
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    print(user)
    # Verificamos password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Por favor valide las credenciales")
    
    # Creamos el Token
    access_token = create_access_token(subject=user.id)
    
    return {"access_token": access_token, "token_type": "bearer"}