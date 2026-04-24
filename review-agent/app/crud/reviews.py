from datetime import date

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review


async def get_reviews_by_product(
    session: AsyncSession,
    product_id: str,
    start: date | None = None,
    end: date | None = None,
) -> list[Review]:
    stmt: Select[tuple[Review]] = select(Review).where(Review.product_id == product_id)
    if start:
        stmt = stmt.where(func.date(Review.created_at) >= start)
    if end:
        stmt = stmt.where(func.date(Review.created_at) <= end)
    result = await session.execute(stmt)
    return list(result.scalars().all())
