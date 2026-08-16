from unittest.mock import patch

from fastapi.testclient import TestClient

from app.cache.redis_client import get_redis_client
from app.main import app
from app.rag.vectorstore import add_chunks

client = TestClient(app)


def _get_token(username="ratelimit_test_user"):
    user_data = {
        "username": username,
        "password": "testpass123",
        "role": "doctor",
        "wallet_address": None,
    }
    client.post("/register", json=user_data)
    login_response = client.post("/login", json=user_data)
    return login_response.json()["access_token"]


def test_rate_limit_blocks_after_threshold():
    redis_client = get_redis_client()
    redis_client.flushdb()  # clean slate

    token = _get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # First 5 requests should succeed (or at least not be rate-limited)
    for _ in range(5):
        response = client.post(
            "/query",
            json={"question": "test question"},
            headers=headers,
        )
        assert response.status_code == 200

    # 6th request should be rate-limited
    response = client.post(
        "/query",
        json={"question": "test question"},
        headers=headers,
    )
    assert response.json()["answer"] == "Rate limit exceeded. Please wait a minute and try again."


def test_query_with_patient_id_no_wallet_fails():
    redis_client = get_redis_client()
    redis_client.flushdb()

    user_data = {
        "username": "no_wallet_doctor",
        "password": "testpass123",
        "role": "doctor",
        "wallet_address": None,  # no wallet linked
    }
    client.post("/register", json=user_data)
    login_response = client.post("/login", json=user_data)
    token = login_response.json()["access_token"]

    response = client.post(
        "/query",
        json={"question": "test", "patient_id": "patient001"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_query_with_consent_granted_succeeds():
    redis_client = get_redis_client()
    redis_client.flushdb()

    user_data = {
        "username": "consented_doctor",
        "password": "testpass123",
        "role": "doctor",
        "wallet_address": "0xTestWalletAddress",
    }
    client.post("/register", json=user_data)
    login_response = client.post("/login", json=user_data)
    token = login_response.json()["access_token"]

    with patch("app.api.query._check_consent", return_value=True):
        response = client.post(
            "/query",
            json={"question": "What symptoms did the patient have?", "patient_id": "patient001"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert "answer" in response.json()


def test_query_returns_cached_response_on_second_call():
    redis_client = get_redis_client()
    redis_client.flushdb()

    # Seed a known chunk so retrieval has something to find
    add_chunks(
        ["Patient presented with mild fever and elevated blood pressure."],
        source="cache_test_doc",
    )

    token = _get_token(username="cache_test_doctor_unique")
    headers = {"Authorization": f"Bearer {token}"}
    question = {"question": "What symptoms did the patient have?"}

    first_response = client.post("/query", json=question, headers=headers)
    assert first_response.status_code == 200
    assert first_response.json()["cached"] is False

    second_response = client.post("/query", json=question, headers=headers)
    assert second_response.status_code == 200
    assert second_response.json()["cached"] is True


@patch("app.api.query.retrieve_chunks", return_value=[])
def test_query_with_no_matching_chunks(mock_retrieve):
    redis_client = get_redis_client()
    redis_client.flushdb()

    token = _get_token(username="no_chunks_doctor")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/query",
        json={"question": "some obscure question"},
        headers=headers,
    )

    assert response.json()["answer"] == "No relevant documents found."
