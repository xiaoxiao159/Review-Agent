import json
from unittest.mock import AsyncMock

import pytest

from app.services.report_service import ReportService
from app.utils.exceptions import NotFoundException


@pytest.mark.asyncio
async def test_get_report_by_task_uses_cached_report(monkeypatch):
    redis_client = AsyncMock()
    redis_client.get.side_effect = ["p1", json.dumps({"summary": {"total_count": 1, "negative_count": 1, "negative_rate": 1.0, "avg_sentiment": 0.2}, "reason_categories": {}, "keywords": [], "sentiment_trend": [], "suggestions": [], "similar_cases": []})]
    service = ReportService(redis_client)

    class _Res:
        state = "SUCCESS"
        result = {"product_id": "p1", "report": {}}

    monkeypatch.setattr("app.services.report_service.AsyncResult", lambda *_args, **_kwargs: _Res())
    report = await service.get_report_by_task("t1")
    assert report["summary"]["total_count"] == 1


@pytest.mark.asyncio
async def test_get_report_by_task_not_found_when_missing_product(monkeypatch):
    redis_client = AsyncMock()
    redis_client.get.side_effect = [None, None]
    service = ReportService(redis_client)

    class _Res:
        state = "SUCCESS"
        result = {"report": {}}

    monkeypatch.setattr("app.services.report_service.AsyncResult", lambda *_args, **_kwargs: _Res())
    with pytest.raises(NotFoundException):
        await service.get_report_by_task("t2")
