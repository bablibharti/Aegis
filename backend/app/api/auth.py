from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.auth.jwt_handler import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from app.auth.models import Token, UserCreate, UserPublic
from app.auth.session import blocklist_token
from app.auth.store import create_user, get_user, verify_password

router = APIRouter()


@router.post("/register", response_model=UserPublic)
def register(user: UserCreate):
    try:
        created = create_user(user.username, user.password, user.role, user.wallet_address)
    except ValueError:
        raise HTTPException(status_code=400, detail="Username already exists")

    return UserPublic(
        username=created["username"],
        role=created["role"],
        wallet_address=created["wallet_address"],
    )


@router.post("/login", response_model=Token)
def login(user: UserCreate):
    existing_user = get_user(user.username)

    if not existing_user or not verify_password(user.password, existing_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(
        existing_user["username"], existing_user["role"], existing_user["wallet_address"]
    )
    return Token(access_token=token)


@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    token = current_user["token"]
    blocklist_token(token, expires_in_seconds=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return {"message": "Successfully logged out"}
