from app.auth.jwt_handler import create_access_token, decode_access_token


def test_create_and_decode_token():
    token = create_access_token("testuser", "doctor", "0x123")
    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "testuser"
    assert payload["role"] == "doctor"
    assert payload["wallet_address"] == "0x123"


def test_decode_invalid_token_returns_none():
    payload = decode_access_token("this.is.not.a.valid.token")
    assert payload is None


def test_decode_garbage_string_returns_none():
    payload = decode_access_token("garbage")
    assert payload is None
