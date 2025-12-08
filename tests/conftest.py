import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid  # Para generar emails únicos y no chocar


@pytest.fixture(scope="module")
def client():
    # TestClient simula peticiones HTTP a tu app FastAPI
    with TestClient(app) as c:
        yield c


# 👇 NUEVO FIXTURE: Autenticación automática
@pytest.fixture(scope="module")
def auth_headers(client):
    """
    Crea un usuario de prueba, se loguea y devuelve los headers con el Token.
    """
    # 1. Usamos un email aleatorio para que el test no falle si lo corres 2 veces
    random_email = f"test_{uuid.uuid4()}@bot.com"
    password = "test_password_123"

    # 2. Registramos al usuario (Signup)
    # Nota: Usamos json=... porque el endpoint espera JSON
    client.post("/auth/signup", json={"email": random_email, "password": password})

    # 3. Nos logueamos (Login)
    # Nota: Usamos data=... porque OAuth2 espera Form Data
    login_res = client.post(
        "/auth/login", data={"username": random_email, "password": password}
    )

    # 4. Extraemos el token
    token = login_res.json()["access_token"]

    # 5. Devolvemos el encabezado listo para usar
    return {"Authorization": f"Bearer {token}"}
