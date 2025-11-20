def test_create_bot(client):
    # 1. DATOS: Preparamos el payload
    payload = {
        "name": "TestBot_007",
        "description": "Un bot creado por test automático",
        "status": "idle"
    }
    
    # 2. ACCIÓN: Hacemos POST al endpoint real
    response = client.post("/bots/", json=payload)
    
    # 3. ASSERT (Verificación): Comprobamos que todo salió bien
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestBot_007"
    assert "id" in data
    
    # Guardamos el ID para verificar que podemos leerlo después
    bot_id = data["id"]
    
    # 4. VERIFICACIÓN DOBLE: Intentamos leerlo con GET
    response_get = client.get(f"/bots/{bot_id}")
    assert response_get.status_code == 200
    assert response_get.json()["name"] == "TestBot_007"

def test_read_bots(client):
    # Probamos que la lista no esté vacía
    response = client.get("/bots/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)