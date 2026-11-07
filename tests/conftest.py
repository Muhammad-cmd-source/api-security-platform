import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


def make_user(client, name="alice", pw="password123"):
    client.post("/auth/register", json={"username": name, "password": pw})
    r = client.post("/auth/login", data={"username": name, "password": pw})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def auth(client):
    return make_user(client)
