from datetime import UTC, datetime

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.crud.auth_sessions import create_auth_session, get_auth_session_by_id, revoke_auth_session
from app.crud.users import create_user, get_user_by_id, get_user_by_username, get_user_by_username_or_email, update_user_last_login
from app.dependencies.auth import create_access_token, create_refresh_token, decode_token, hash_token
from app.models.auth_session import AuthSession
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPairResponse,
    UserProfileResponse,
)
from app.utils.exceptions import AppException, UnauthorizedException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def _user_profile(user: User) -> UserProfileResponse:
    return UserProfileResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


async def register_user(session: AsyncSession, payload: RegisterRequest) -> UserProfileResponse:
    exists = await get_user_by_username_or_email(session, payload.username)
    if exists:
        raise AppException(code="AUTH_409", message="Conflict", detail="username already exists", status_code=409)

    user = User(
        id=payload.username,
        username=payload.username,
        email=payload.email,
        password_hash=pwd_context.hash(payload.password),
        role="user",
        is_active=True,
        created_at=datetime.now(tz=UTC).replace(tzinfo=None),
        updated_at=datetime.now(tz=UTC).replace(tzinfo=None),
    )
    user = await create_user(session, user)
    return _user_profile(user)


async def login_user(session: AsyncSession, payload: LoginRequest) -> TokenPairResponse:
    user = await get_user_by_username(session, payload.username)
    if not user or not pwd_context.verify(payload.password, user.password_hash):
        raise UnauthorizedException("invalid username or password")
    if not user.is_active:
        raise UnauthorizedException("user is disabled")

    user.last_login_at = datetime.now(tz=UTC).replace(tzinfo=None)
    user.updated_at = datetime.now(tz=UTC).replace(tzinfo=None)
    await update_user_last_login(session, user)

    access_token, expires_in = create_access_token(user_id=user.id, role=user.role)
    refresh_token = create_refresh_token(user_id=user.id)
    claims = decode_token(refresh_token, expected_type="refresh")

    auth_session = AuthSession(
        id=claims["jti"],
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.fromtimestamp(claims["exp"], tz=UTC).replace(tzinfo=None),
        revoked_at=None,
        replaced_by=None,
        created_at=datetime.now(tz=UTC).replace(tzinfo=None),
    )
    await create_auth_session(session, auth_session)

    return TokenPairResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
    )


async def refresh_user_token(session: AsyncSession, payload: RefreshRequest) -> TokenPairResponse:
    claims = decode_token(payload.refresh_token, expected_type="refresh")
    auth_session = await get_auth_session_by_id(session, claims["jti"])
    if not auth_session or auth_session.revoked_at is not None:
        raise UnauthorizedException("refresh token revoked")
    if auth_session.token_hash != hash_token(payload.refresh_token):
        raise UnauthorizedException("refresh token mismatch")

    user = await get_user_by_id(session, claims["sub"])
    if not user or not user.is_active:
        raise UnauthorizedException("user unavailable")

    access_token, expires_in = create_access_token(user_id=user.id, role=user.role)
    new_refresh_token = create_refresh_token(user_id=user.id)
    new_claims = decode_token(new_refresh_token, expected_type="refresh")

    await revoke_auth_session(session, auth_session, replaced_by=new_claims["jti"])
    await create_auth_session(
        session,
        AuthSession(
            id=new_claims["jti"],
            user_id=user.id,
            token_hash=hash_token(new_refresh_token),
            expires_at=datetime.fromtimestamp(new_claims["exp"], tz=UTC).replace(tzinfo=None),
            revoked_at=None,
            replaced_by=None,
            created_at=datetime.now(tz=UTC).replace(tzinfo=None),
        ),
    )

    return TokenPairResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=expires_in,
    )


async def logout_user(session: AsyncSession, payload: LogoutRequest):
    claims = decode_token(payload.refresh_token, expected_type="refresh")
    auth_session = await get_auth_session_by_id(session, claims["jti"])
    if auth_session and auth_session.revoked_at is None:
        await revoke_auth_session(session, auth_session)


async def get_me(session: AsyncSession, user_id: str) -> UserProfileResponse:
    user = await get_user_by_id(session, user_id)
    if not user:
        raise UnauthorizedException("user not found")
    return _user_profile(user)


async def forgot_password(_: AsyncSession, __: ForgotPasswordRequest):
    return {"message": "If the account exists, reset instructions have been sent"}


async def ensure_default_admin(session: AsyncSession):
    if not settings.default_admin_enabled:
        return
    existed = await get_user_by_username(session, settings.default_admin_username)
    if existed:
        return
    admin = User(
        id=settings.default_admin_username,
        username=settings.default_admin_username,
        email=settings.default_admin_email,
        password_hash=pwd_context.hash(settings.default_admin_password),
        role="admin",
        is_active=True,
        created_at=datetime.now(tz=UTC).replace(tzinfo=None),
        updated_at=datetime.now(tz=UTC).replace(tzinfo=None),
    )
    await create_user(session, admin)
