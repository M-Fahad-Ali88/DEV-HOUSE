import pytest
from fastapi.testclient import TestClient
from Main import app
from Dependencies import get_database


class MockDatabaseSession:
    def __init__(self):
        self.connected = False

    def connect(self):
        self.connected = True
        print("[TEST MOCK] Connected to Mock DB")

    def close(self):
        self.connected = False
        print("[TEST MOCK] Mock DB connection closed")

    def get_users(self):
        return [
            {"id": 99, "name": "Test Mock User"}
        ]


def override_get_database():
    db = MockDatabaseSession()
    try:
        db.connect()
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    app.dependency_overrides[get_database] = override_get_database
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_get_users_override(client):
    response = client.get("/users")

    assert response.status_code == 200
    assert response.json() == [{"id": 99, "name": "Test Mock User"}]