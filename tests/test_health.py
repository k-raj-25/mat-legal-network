def test_health_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["database"] == "up"


def test_index_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"MAT Legal Network" in response.data
    assert b"The Right Lawyer. Right Here." in response.data
    assert b"Featured lawyers" in response.data
    assert b"Register as a Lawyer" in response.data
    assert b"Sign Up" not in response.data


def test_find_lawyers_renders(client):
    response = client.get("/find-lawyers")
    assert response.status_code == 200
    assert b"Find a Lawyer" in response.data
