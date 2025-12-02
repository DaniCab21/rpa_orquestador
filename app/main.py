# docker-compose down
# docker-compose up -d --build
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware  # <--- IMPORTAR ESTO
from contextlib import asynccontextmanager
from app.db.session import create_db_and_tables
from app.api.v1 import executions  # Importar nuevo router
from app.api.v1 import auth  # Importar auth
from app.api.v1 import bots, executions
from app.models.user import User  # Importar User para que SQLModel cree la tabla
from app.api.v1.deps import get_current_user  # Importar al Guardia


# Lifespan: Eventos que ocurren al iniciar/apagar la app
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando RPA Orchestrator...")
    create_db_and_tables()  # Aquí se crean las tablas automáticamente
    yield
    print("🛑 Apagando RPA Orchestrator...")


app = FastAPI(title="RPA Orchestrator", version="1.0.0", lifespan=lifespan)

app.include_router(bots.router, prefix="/bots", tags=["Bots"], dependencies=[Depends(get_current_user)])
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(executions.router, prefix="/executions", tags=["Ejecuciones"], dependencies=[Depends(get_current_user)])

origins = [
    "http://localhost:4200",  # Permitir Angular local
    "http://localhost",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Permitir enviar Cookies/Tokens
    allow_methods=["*"],  # Permitir GET, POST, DELETE, etc.
    allow_headers=["*"],  # Permitir headers de Authorization
)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido al RPA Orchestrator", "db_status": "Connected"}
