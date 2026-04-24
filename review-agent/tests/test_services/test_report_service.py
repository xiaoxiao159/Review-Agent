from unittest.mock import AsyncMock

import pytest

from app.services.report_service import ReportService
from app.utils.exceptions import TaskNotReadyException


@pytest.mark.asyncio
async def test_submit_report_reuses_pending_task(monkeypatch):
    redis_client = AsyncMock()
    redis_client.set.return_value = True
    redis_client.get.side_effect = [None, "existing-task"]
    service = ReportService(redis_client)

    class _Res:
        state = "PENDING"

    monkeypatch.setattr("app.services.report_service.AsyncResult", lambda *args, **kwargs: _Res())
    task_id = await service.submit_report("p1")
    assert task_id == "existing-task"


@pytest.mark.asyncio
async def test_submit_report_returns_cached_completed_task(monkeypatch):
    redis_client = AsyncMock()
    redis_client.set.return_value = True
    redis_client.get.side_effect = ["cached-report", "task-1"]
    service = ReportService(redis_client)

    task_id = await service.submit_report("p1")
    assert task_id == "task-1"


@pytest.mark.asyncio
async def test_get_status_maps_states(monkeypatch):
    redis_client = AsyncMock()
    service = ReportService(redis_client)

    class _Res:
        def __init__(self, state):
            self.state = state

    monkeypatch.setattr("app.services.report_service.AsyncResult", lambda *_args, **_kwargs: _Res("RETRY"))
    assert await service.get_status("t") == "running"

    monkeypatch.setattr("app.services.report_service.AsyncResult", lambda *_args, **_kwargs: _Res("SUCCESS"))
    assert await service.get_status("t") == "completed"


@pytest.mark.asyncio
async def test_get_report_by_task_raises_when_not_ready(monkeypatch):
    redis_client = AsyncMock()
    redis_client.get.return_value = "p1"
    service = ReportService(redis_client)

    class _Res:
        state = "STARTED"
        result = {}

    monkeypatch.setattr("app.services.report_service.AsyncResult", lambda *_args, **_kwargs: _Res())
    with pytest.raises(TaskNotReadyException):
        await service.get_report_by_task("t1")
