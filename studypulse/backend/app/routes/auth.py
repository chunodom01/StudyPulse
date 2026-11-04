from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.database import db
from app.security import create_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


def auth_response(user_id: str, name: str, email: str) -> dict:
    return {"token": create_token(user_id), "user": {"id": user_id, "name": name, "email": email}}


@router.post("/register")
async def register(data: RegisterIn):
    email = data.email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="This email is already registered")
    doc = {
        "name": data.name.strip(),
        "email": email,
        "password_hash": hash_password(data.password),
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.users.insert_one(doc)
    return auth_response(str(result.inserted_id), doc["name"], email)


@router.post("/login")
async def login(data: LoginIn):
    user = await db.users.find_one({"email": data.email.lower()})
    if user is None or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    return auth_response(str(user["_id"]), user["name"], user["email"])


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return user