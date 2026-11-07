from tests.conftest import make_user


def test_tasks_require_auth(client):
    assert client.get("/tasks").status_code == 401


def test_tampered_token_rejected(client, auth):
    bad = {"Authorization": auth["Authorization"][:-3] + "abc"}
    assert client.get("/tasks", headers=bad).status_code == 401


def test_sql_injection_in_login(client):
    client.post("/auth/register", json={"username": "alice", "password": "password123"})
    r = client.post("/auth/login", data={"username": "alice' OR '1'='1", "password": "x"})
    assert r.status_code == 401


def test_sql_injection_in_task_stored_literally(client, auth):
    payload = "x'); DROP TABLE tasks;--"
    assert client.post("/tasks", json={"title": payload}, headers=auth).status_code == 201
    assert client.get("/tasks", headers=auth).json()[0]["title"] == payload


def test_cannot_delete_other_users_task(client, auth):
    tid = client.post("/tasks", json={"title": "mine"}, headers=auth).json()["id"]
    other = make_user(client, "mallory")
    assert client.delete(f"/tasks/{tid}", headers=other).status_code == 404


def test_weak_input_rejected(client):
    r = client.post("/auth/register", json={"username": "a b", "password": "short"})
    assert r.status_code == 422


def test_security_headers(client):
    r = client.get("/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
