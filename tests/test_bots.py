# Inyectamos el fixture 'auth_headers' en la función
def test_create_bot(client, auth_headers):
    # 1. DATOS
    payload = {
        "name": "SuperTestBot",
        "description": "Un bot creado con seguridad",
        "status": "idle",
    }

    # 2. ACCIÓN: Agregamos headers=auth_headers
    response = client.post("/bots/", json=payload, headers=auth_headers)

    # 3. VERIFICACIÓN
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "SuperTestBot"

    # Guardamos el ID para verificar lectura
    bot_id = data["id"]

    # 4. LECTURA (También suele requerir token si protegiste el GET)
    response_get = client.get(f"/bots/{bot_id}", headers=auth_headers)
    assert response_get.status_code == 200
    assert response_get.json()["name"] == "SuperTestBot"


def test_read_bots(client, auth_headers):
    # Probamos la lista, enviando también el token
    response = client.get("/bots/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
