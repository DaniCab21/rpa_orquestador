# app/websockets.py (Nuevo archivo recomendado)
from fastapi import WebSocket
from typing import List
import redis.asyncio as redis
import json
import asyncio
import os

# Configuración de Redis (Usa las variables de entorno de tu docker-compose)
REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # Envía el mensaje a todos los navegadores conectados
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

# Función que correrá en background escuchando a Redis
async def listen_to_redis():
    r = redis.from_url(REDIS_URL)
    pubsub = r.pubsub()
    await pubsub.subscribe("bot_updates") # Nombre del canal
    
    async for message in pubsub.listen():
        if message["type"] == "message":
            # Cuando llega algo de Redis, lo enviamos a los WebSockets
            await manager.broadcast(message["data"].decode("utf-8"))