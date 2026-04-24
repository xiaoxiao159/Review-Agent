from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import SessionLocal, engine
from app.models import AuthSession, Base, Review, User
from app.services.auth_service import ensure_default_admin


async def bootstrap_auth_data() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:  # type: AsyncSession
        await ensure_default_admin(session)
