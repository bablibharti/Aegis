from passlib.context import CryptContext

from app.auth.models import Role

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_users_db: dict[str, dict] = {}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_user(
    username: str, password: str, role: Role, wallet_address: str | None = None
) -> dict:
    if username in _users_db:
        raise ValueError("Username already exists")

    user = {
        "username": username,
        "hashed_password": hash_password(password),
        "role": role,
        "wallet_address": wallet_address,
    }
    _users_db[username] = user
    return user


def get_user(username: str) -> dict | None:
    return _users_db.get(username)
