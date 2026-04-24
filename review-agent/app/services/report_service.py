import json
from typing import Any

from celery.result import AsyncResult
from redis.asyncio import Redis

from app.services.tasks import celery_app, generate_report
from app.utils.exceptions import NotFoundException, TaskNotReadyException


class ReportService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    @staticmethod
    def _cache_key(product_id: str) -> str:
        return f"report:product:{product_id}:latest"

    @staticmethod
    def _task_key(product_id: str) -> str:
        return f"report:product:{product_id}:latest:task"

    async def submit_report(self, product_id: str, date_range: dict[str, str] | None = None) -> str:
        cache_key = self._cache_key(product_id)
        task_key = self._task_key(product_id)

        lock_key = f"report:product:{product_id}:submit:lock"
        own_lock = bool(await self.redis.set(lock_key, "1", ex=30, nx=True))

        if not own_lock:
            existing = await self.redis.get(task_key)
            if existing:
                return existing

        try:
            cached_report = await self.redis.get(cache_key)
            cached_task_id = await self.redis.get(task_key)
            if cached_report and cached_task_id:
                return cached_task_id

            if cached_task_id:
                result = AsyncResult(cached_task_id, app=celery_app)
                if result.state in {"PENDING", "RECEIVED", "STARTED", "RETRY", "PROGRESS"}:
                    return cached_task_id

            task = generate_report.delay(product_id=product_id, date_range=date_range)
            await self.redis.set(task_key, task.id, ex=24 * 3600)
            await self.redis.set(f"task:product:{task.id}", product_id, ex=24 * 3600)
            return task.id
        finally:
            if own_lock:
                await self.redis.delete(lock_key)

    async def get_status(self, task_id: str) -> str:
        result = AsyncResult(task_id, app=celery_app)
        state = result.state
        if state in {"PENDING"}:
            return "pending"
        if state in {"RECEIVED", "STARTED", "RETRY", "PROGRESS"}:
            return "running"
        if state in {"SUCCESS"}:
            return "completed"
        if state in {"FAILURE", "REVOKED"}:
            return "failed"
        return "pending"

    async def get_report_by_task(self, task_id: str) -> dict[str, Any]:
        product_id = await self.redis.get(f"task:product:{task_id}")
        result = AsyncResult(task_id, app=celery_app)
        if result.state != "SUCCESS":
            raise TaskNotReadyException(detail=f"task {task_id} is {result.state.lower()}")

        payload = result.result if isinstance(result.result, dict) else {}
        if not product_id:
            product_id = payload.get("product_id")
        if not product_id:
            raise NotFoundException(detail="task product mapping not found")

        cache_key = self._cache_key(product_id)
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        report = payload.get("report", payload)
        await self.redis.set(cache_key, json.dumps(report), ex=24 * 3600)
        await self.redis.set(self._task_key(product_id), task_id, ex=24 * 3600)
        return report
