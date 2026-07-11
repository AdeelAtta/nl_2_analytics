from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

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
            tenant = create_tenant(body.tenant_name, body.email)
            tenant_id = tenant["id"]
        else:
            tenant_id = "demo"

        user = create_user(body.email, body.password, tenant_id, body.name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    token = create_token({"sub": user["id"], "tenant_id": tenant_id, "role": user["role"]})
    return AuthResponse(
        access_token=token, tenant_id=tenant_id, user_id=user["id"],
        email=user["email"], name=user["name"], role=user["role"],
    )


@router.post("/auth/login", response_model=AuthResponse)
async def login(body: LoginRequest) -> AuthResponse:
    user = authenticate_user(body.email, body.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")
    token = create_token({"sub": user["id"], "tenant_id": user["tenant_id"], "role": user["role"]})
    return AuthResponse(
        access_token=token, tenant_id=user["tenant_id"], user_id=user["id"],
        email=user["email"], name=user["name"], role=user["role"],
    )
