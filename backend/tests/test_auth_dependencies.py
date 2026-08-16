import pytest
from fastapi import HTTPException

from app.auth.dependencies import require_role


def test_require_role_allows_matching_role():
    checker = require_role("doctor", "admin")
    user = {"username": "test", "role": "doctor", "wallet_address": None, "token": "abc"}

    result = checker(user=user)
    assert result == user


def test_require_role_rejects_wrong_role():
    checker = require_role("admin")
    user = {"username": "test", "role": "patient", "wallet_address": None, "token": "abc"}

    with pytest.raises(HTTPException) as exc_info:
        checker(user=user)

    assert exc_info.value.status_code == 403
