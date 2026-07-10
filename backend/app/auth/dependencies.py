
from collections.abc import Awaitable, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import decode_token

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, str]:
    if credentials is None:
        return {"sub": "anonymous", "role": "guest"}
    payload = decode_token(credentials.credentials)
    if payload is None:
        return {"sub": "anonymous", "role": "guest"}
    return {"sub": payload.get("sub", "unknown"), "role": payload.get("role", "user")}


def require_role(required_role: str) -> Callable[[], Awaitable[dict[str, str]]]:
    async def role_checker(
        current_user: dict[str, str] = Depends(get_current_user),
    ) -> dict[str, str]:
        if current_user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_checker
