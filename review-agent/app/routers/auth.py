from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.current_user import get_current_user
from app.dependencies.database import get_db_session
from app.schemas.auth import (
    ForgotPasswordRequest,
    GenericMessageResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPairResponse,
    UserProfileResponse,
)
from app.services.auth_service import (
    forgot_password,
    get_me,
    login_user,
    logout_user,
    refresh_user_token,
    register_user,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserProfileResponse)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_db_session)) -> UserProfileResponse:
    return await register_user(session, payload)


@router.post("/login", response_model=TokenPairResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_db_session)) -> TokenPairResponse:
    return await login_user(session, payload)


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh(payload: RefreshRequest, session: AsyncSession = Depends(get_db_session)) -> TokenPairResponse:
    return await refresh_user_token(session, payload)


@router.post("/logout", response_model=GenericMessageResponse)
async def logout(payload: LogoutRequest, session: AsyncSession = Depends(get_db_session)) -> GenericMessageResponse:
    await logout_user(session, payload)
    return GenericMessageResponse(message="logged out")


@router.get("/me", response_model=UserProfileResponse)
async def me(current_user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> UserProfileResponse:
    return await get_me(session, current_user["sub"])


@router.post("/forgot-password", response_model=GenericMessageResponse)
async def forgot(payload: ForgotPasswordRequest, session: AsyncSession = Depends(get_db_session)) -> GenericMessageResponse:
    result = await forgot_password(session, payload)
    return GenericMessageResponse(**result)
