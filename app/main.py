import os
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
import redis.asyncio as redis

# --- TUS IMPORTACIONES DE PROYECTO ---
from app.db.session import create_db_and_tables
from app.api.v1 import auth, bots, executions
from app.api.v1.deps import get_current_user
from app.websockets import (
    manager,
    listen_to_redis,
)  # Asegúrate de que creaste este archivo


# --- LIFESPAN UNIFICADO ---
# Aquí combinamos la creación de BD y el inicio del listener de Redis
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Crear carpeta de media si no existe
    if not os.path.exists("media"):
        os.makedirs("media")
        print("📁 Carpeta 'media' creada para screenshots.")

    # 1. INICIO: Crear tablas de Base de Datos
    print("🚀 Iniciando RPA Orchestrator...")
    create_db_and_tables()

    # 2. INICIO: Arrancar la escucha de Redis en background (WebSockets)
    print("📡 Conectando a Redis para WebSockets...")
    task = asyncio.create_task(listen_to_redis())

    yield  # Aquí es donde la app corre y recibe peticiones

    # 3. APAGADO: Limpieza
    print("🛑 Apagando RPA Orchestrator...")
    task.cancel()  # Cancelamos la tarea de escucha
    try:
        await task  # Esperamos a que cierre limpiamente
    except asyncio.CancelledError:
        pass


# --- INSTANCIA ÚNICA DE LA APP ---
app = FastAPI(title="RPA Orchestrator", version="1.0.0", lifespan=lifespan)
app.mount("/media", StaticFiles(directory="media"), name="media")
# --- MIDDLEWARES ---
origins = [
    "http://localhost:4200",  # Angular local
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTERS ---
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(
    bots.router, prefix="/bots", tags=["Bots"], dependencies=[Depends(get_current_user)]
)
app.include_router(
    executions.router,
    prefix="/executions",
    tags=["Ejecuciones"],
    dependencies=[Depends(get_current_user)],
)


# --- ENDPOINTS GENERALES ---
@app.get("/", tags=["Root"])
def read_root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check():
    return {"status": "ok"}


# --- WEBSOCKET ENDPOINT ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Mantenemos la conexión viva esperando mensajes del cliente
            # (aunque en este caso el cliente solo escucha, necesitamos mantener el loop)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
