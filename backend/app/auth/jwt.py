from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()


def create_token(data: dict[str, Any]) -> str:
    to_encode = {
        **data,
        "exp": datetime.now(UTC) + timedelta(minutes=15),
        "iat": datetime.now(UTC),
        "jti": uuid4().hex,
        "type": "access",
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)  # type: ignore[no-any-return]


def create_refresh_token(user_id: str) -> str:
    to_encode = {
        "sub": user_id,
        "exp": datetime.now(UTC) + timedelta(days=7),
        "iat": datetime.now(UTC),
        "jti": uuid4().hex,
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)  # type: ignore[no-any-return]


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload  # type: ignore[no-any-return]
    except JWTError:
        return None
