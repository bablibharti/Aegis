import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def test_user():
    return {
        "username": "test_doctor_integration",
        "password": "testpass123",
        "role": "doctor",
        "wallet_address": None,
    }


def test_register_new_user(test_user):
    response = client.post("/register", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["role"] == test_user["role"]


def test_register_duplicate_user_fails(test_user):
    # Register once
    client.post("/register", json=test_user)
    # Try registering again with same username
    response = client.post("/register", json=test_user)
    assert response.status_code == 400


def test_login_with_correct_credentials(test_user):
    client.post("/register", json=test_user)
    response = client.post("/login", json=test_user)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password(test_user):
    client.post("/register", json=test_user)
    bad_login = {**test_user, "password": "wrongpassword"}
    response = client.post("/login", json=bad_login)
    assert response.status_code == 401


def test_query_without_token_fails():
    response = client.post("/query", json={"question": "test question"})
    assert response.status_code in (401, 403)  # HTTPBearer returns 403 when no credentials given


def test_query_with_valid_token_succeeds(test_user):
    client.post("/register", json=test_user)
    login_response = client.post("/login", json=test_user)
    token = login_response.json()["access_token"]

    response = client.post(
        "/query",
        json={"question": "What symptoms did the patient have?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "answer" in response.json()


def test_logout_revokes_token(test_user):
    client.post("/register", json=test_user)
    login_response = client.post("/login", json=test_user)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Logout
    logout_response = client.post("/logout", headers=headers)
    assert logout_response.status_code == 200

    # Try using the same token again - should fail
    query_response = client.post(
        "/query",
        json={"question": "test question"},
        headers=headers,
    )
    assert query_response.status_code == 401
