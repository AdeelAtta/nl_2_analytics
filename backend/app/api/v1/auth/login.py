from __future__ import annotations

import re
import time
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, field_validator

from app.auth.jwt import create_refresh_token, create_token, decode_token
from app.core.config import get_settings
from app.services.store import authenticate_user, create_tenant, create_user, get_user_by_id

router = APIRouter(tags=["auth"])

_login_attempts: dict[str, list[float]] = defaultdict(list)


def _check_login_rate(email: str) -> None:
    now = time.time()
    cutoff = now - 60
    attempts = [t for t in _login_attempts[email] if t > cutoff]
    _login_attempts[email] = attempts
    if len(attempts) >= 5:
        raise HTTPException(status_code=429, detail="Too many login attempts. Try again in 60 seconds.")
    _login_attempts[email].append(now)


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
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain a digit")
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


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    settings = get_settings()
    is_prod = settings.environment == "production"
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_prod,
        samesite="none" if is_prod else "lax",
        max_age=7 * 24 * 3600,
        path="/api/v1/auth",
    )


@router.post("/auth/demo-login", response_model=AuthResponse)
async def demo_login(body: DemoLoginRequest, response: Response) -> AuthResponse:
    settings = get_settings()
    if settings.environment == "production":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Demo login not available in production")
    token = create_token({"sub": body.user_id, "tenant_id": body.tenant_id, "role": "user"})
    refresh = create_refresh_token(body.user_id)
    _set_refresh_cookie(response, refresh)
    return AuthResponse(
        access_token=token, tenant_id=body.tenant_id, user_id=body.user_id,
    )


@router.post("/auth/register", response_model=AuthResponse)
async def register(body: RegisterRequest, response: Response) -> AuthResponse:
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
    refresh = create_refresh_token(user["id"])
    _set_refresh_cookie(response, refresh)
    return AuthResponse(
        access_token=token, tenant_id=tenant_id, user_id=user["id"],
        email=user["email"], name=user["name"], role=user["role"],
    )


@router.post("/auth/login", response_model=AuthResponse)
async def login(body: LoginRequest, response: Response) -> AuthResponse:
    _check_login_rate(body.email)
    user = await authenticate_user(body.email, body.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")
    token = create_token({"sub": user["id"], "tenant_id": user["tenant_id"], "role": user["role"]})
    refresh = create_refresh_token(user["id"])
    _set_refresh_cookie(response, refresh)
    return AuthResponse(
        access_token=token, tenant_id=user["tenant_id"], user_id=user["id"],
        email=user["email"], name=user["name"], role=user["role"],
    )


@router.post("/auth/refresh")
async def refresh_token(request: Request) -> dict[str, str]:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = await get_user_by_id(payload["sub"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_token = create_token({"sub": user["id"], "tenant_id": user["tenant_id"], "role": user["role"]})
    return {
        "access_token": new_token,
        "token_type": "bearer",
        "tenant_id": user["tenant_id"],
        "user_id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
    }
