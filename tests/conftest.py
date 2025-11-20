import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    # TestClient simula peticiones HTTP a tu app FastAPI sin tener que levantar el servidor
    with TestClient(app) as c:
        yield c
