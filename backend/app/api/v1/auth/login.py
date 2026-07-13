from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, field_validator

from app.auth.jwt import create_token
from app.core.config import get_settings
from app.services.store import authenticate_user, create_tenant, create_user

router = APIRouter(tags=["auth"])


class DemoLoginRequest(BaseModel):
    tenant_id: str = "demo"
    user_id: str = "demo-user"


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str = ""
    tenant_name: str = ""

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: str
    user_id: str
    email: str = ""
    name: str = ""
    role: str = "user"


@router.post("/auth/demo-login", response_model=AuthResponse)
async def demo_login(body: DemoLoginRequest) -> AuthResponse:
    settings = get_settings()
    if settings.environment == "production":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Demo login not available in production")
    token = create_token({"sub": body.user_id, "tenant_id": body.tenant_id, "role": "user"})
    return AuthResponse(
        access_token=token, tenant_id=body.tenant_id, user_id=body.user_id,
    )


@router.post("/auth/register", response_model=AuthResponse)
async def register(body: RegisterRequest) -> AuthResponse:
    try:
        if body.tenant_name:
            tenant = await create_tenant(body.tenant_name, body.email)
            tenant_id = tenant["id"]
        else:
            tenant = await create_tenant(f"{body.name or body.email.split('@')[0]}'s Org", body.email)
            tenant_id = tenant["id"]

        user = await create_user(body.email, body.password, tenant_id, body.name)
    except ValueError as e:
        detail = str(e)
        if "already registered" in detail.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    token = create_token({"sub": user["id"], "tenant_id": tenant_id, "role": user["role"]})
    return AuthResponse(
        access_token=token, tenant_id=tenant_id, user_id=user["id"],
        email=user["email"], name=user["name"], role=user["role"],
    )


@router.post("/auth/login", response_model=AuthResponse)
async def login(body: LoginRequest) -> AuthResponse:
    user = await authenticate_user(body.email, body.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")
    token = create_token({"sub": user["id"], "tenant_id": user["tenant_id"], "role": user["role"]})
    return AuthResponse(
        access_token=token, tenant_id=user["tenant_id"], user_id=user["id"],
        email=user["email"], name=user["name"], role=user["role"],
    )
