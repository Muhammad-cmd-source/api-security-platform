def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_register_duplicate(client):
    body = {"username": "bob", "password": "password123"}
    assert client.post("/auth/register", json=body).status_code == 201
    assert client.post("/auth/register", json=body).status_code == 409


def test_login_bad_password(client):
    client.post("/auth/register", json={"username": "bob", "password": "password123"})
    r = client.post("/auth/login", data={"username": "bob", "password": "wrongpass1"})
    assert r.status_code == 401


def test_task_crud(client, auth):
    r = client.post("/tasks", json={"title": "write tests"}, headers=auth)
    assert r.status_code == 201
    tid = r.json()["id"]
    assert client.get("/tasks", headers=auth).json()[0]["title"] == "write tests"
    assert client.delete(f"/tasks/{tid}", headers=auth).status_code == 204
    assert client.get("/tasks", headers=auth).json() == []
