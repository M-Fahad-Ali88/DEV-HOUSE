import pytest

from TASK_01_JWT_AUTHENTICATION import app, db, User, Ledger


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret-key-32-bytes-long-123456"

    with app.app_context():
        db.drop_all()
        db.create_all()

        client = app.test_client()

        yield client

        db.session.remove()
        db.drop_all()


def register_user(client, username, password, role):
    return client.post(
        "/register",
        json={
            "username": username,
            "password": password,
            "role": role
        }
    )


def login_user(client, username, password):
    response = client.post(
        "/login",
        json={
            "username": username,
            "password": password
        }
    )

    return response.get_json()["access_token"]


def test_unauthorized_request_returns_401(client):
    response = client.get("/ledger")

    assert response.status_code == 401


def test_invalid_token_returns_401(client):
    response = client.get(
        "/ledger",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401


def test_invalid_login_returns_401(client):
    register_user(
        client,
        "testuser",
        "Password123",
        "user"
    )

    response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "WrongPassword"
        }
    )

    assert response.status_code == 401


def test_sql_injection_is_prevented(client):
    malicious_username = "' OR '1'='1"

    response = client.get(
        "/safe-user-search",
        query_string={
            "username": malicious_username
        }
    )

    assert response.status_code == 404


def test_normal_user_gets_403(client):
    register_user(
        client,
        "normaluser",
        "UserPassword123",
        "user"
    )

    token = login_user(
        client,
        "normaluser",
        "UserPassword123"
    )

    response = client.post(
        "/ledger",
        json={
            "description": "Unauthorized Entry",
            "amount": 100
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_admin_can_create_ledger(client):
    register_user(
        client,
        "admin",
        "AdminPassword123",
        "admin"
    )

    token = login_user(
        client,
        "admin",
        "AdminPassword123"
    )

    response = client.post(
        "/ledger",
        json={
            "description": "Office Expense",
            "amount": 500
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 201


def test_valid_user_can_access_ledger(client):
    register_user(
        client,
        "normaluser",
        "UserPassword123",
        "user"
    )

    token = login_user(
        client,
        "normaluser",
        "UserPassword123"
    )

    response = client.get(
        "/ledger",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200