from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.session import create_db_and_tables
from app.api.v1 import bots
from app.api.v1 import executions  # Importar nuevo router


# Lifespan: Eventos que ocurren al iniciar/apagar la app
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando RPA Orchestrator...")
    create_db_and_tables()  # Aquí se crean las tablas automáticamente
    yield
    print("🛑 Apagando RPA Orchestrator...")


app = FastAPI(title="RPA Orchestrator", version="1.0.0", lifespan=lifespan)

app.include_router(bots.router, prefix="/bots", tags=["Bots"])
app.include_router(executions.router, prefix="/executions", tags=["Ejecuciones"])


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido al RPA Orchestrator", "db_status": "Connected"}
