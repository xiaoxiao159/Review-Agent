from unittest.mock import AsyncMock, MagicMock

import pytest

from app.crud.reviews import get_reviews_by_product


@pytest.mark.asyncio
async def test_get_reviews_by_product_returns_list():
    session = AsyncMock()
    scalars = MagicMock()
    scalars.all.return_value = []
    executed = MagicMock()
    executed.scalars.return_value = scalars
    session.execute.return_value = executed

    rows = await get_reviews_by_product(session=session, product_id="p1")
    assert rows == []
