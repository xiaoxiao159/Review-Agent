from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.users import get_user_by_id
from app.dependencies.auth import decode_token
from app.dependencies.database import get_db_session
from app.utils.exceptions import UnauthorizedException


async def get_current_user(
    authorization: str = Header(default=""),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException("missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    payload = decode_token(token, expected_type="access")
    user = await get_user_by_id(session, payload["sub"])
    if not user or not user.is_active:
        raise UnauthorizedException("user not found or inactive")
    return payload
