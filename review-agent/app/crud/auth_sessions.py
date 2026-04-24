from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_session import AuthSession


async def create_auth_session(session: AsyncSession, auth_session: AuthSession) -> AuthSession:
    session.add(auth_session)
    await session.commit()
    await session.refresh(auth_session)
    return auth_session


async def get_auth_session_by_id(session: AsyncSession, session_id: str) -> AuthSession | None:
    result = await session.execute(select(AuthSession).where(AuthSession.id == session_id))
    return result.scalar_one_or_none()


async def revoke_auth_session(session: AsyncSession, auth_session: AuthSession, replaced_by: str | None = None):
    auth_session.revoked_at = datetime.utcnow()
    auth_session.replaced_by = replaced_by
    await session.merge(auth_session)
    await session.commit()
