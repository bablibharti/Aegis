from enum import Enum

from pydantic import BaseModel


class Role(str, Enum):
    DOCTOR = "doctor"
    PATIENT = "patient"
    ADMIN = "admin"


class UserCreate(BaseModel):
    username: str
    password: str
    role: Role
    wallet_address: str | None = None  # required for doctors to check consent


class UserPublic(BaseModel):
    username: str
    role: Role
    wallet_address: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
