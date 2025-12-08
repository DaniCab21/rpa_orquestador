def test_health_check(client):
    """
    Prueba que el servidor responda 'ok' en /health
    """
    # 1. Simular petición GET
    response = client.get("/health")

    # 2. Verificar que el código sea 200 (Éxito)
    assert response.status_code == 200

    # 3. Verificar que el JSON sea el esperado
    assert response.json() == {"status": "ok"}


def test_read_root(client):
    """
    Prueba que la raíz redirija a /docs (Código 200 al seguir la redirección o 307 si no la sigues)
    """
    # follow_redirects=True hace que el cliente vaya hasta /docs y verifique que carga bien
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
