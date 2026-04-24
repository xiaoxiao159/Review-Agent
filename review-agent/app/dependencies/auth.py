import hashlib
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from jose import JWTError, jwt

from app.core.config import get_settings
from app.utils.exceptions import UnauthorizedException

settings = get_settings()


def _encode(payload: dict, secret: str) -> str:
    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str, role: str = "user") -> tuple[str, int]:
    expires_in = settings.access_token_ttl_minutes * 60
    payload = {
        "sub": user_id,
        "role": role,
        "typ": "access",
        "jti": str(uuid4()),
        "exp": int((datetime.now(tz=UTC) + timedelta(minutes=settings.access_token_ttl_minutes)).timestamp()),
        "iat": int(datetime.now(tz=UTC).timestamp()),
    }
    return _encode(payload, settings.jwt_secret), expires_in


def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "typ": "refresh",
        "jti": str(uuid4()),
        "exp": int((datetime.now(tz=UTC) + timedelta(days=settings.refresh_token_ttl_days)).timestamp()),
        "iat": int(datetime.now(tz=UTC).timestamp()),
    }
    return _encode(payload, settings.jwt_refresh_secret)


def decode_token(token: str, expected_type: str) -> dict:
    secret = settings.jwt_secret if expected_type == "access" else settings.jwt_refresh_secret
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise UnauthorizedException() from exc

    if payload.get("typ") != expected_type:
        raise UnauthorizedException("invalid token type")
    if not payload.get("sub") or not payload.get("jti"):
        raise UnauthorizedException("invalid token claims")

    exp = payload.get("exp")
    if exp is None or datetime.now(tz=UTC).timestamp() >= exp:
        raise UnauthorizedException("token expired")
    return payload


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
