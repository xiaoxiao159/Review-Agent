import asyncio
from datetime import date, datetime
from typing import Any

from celery import Celery

from app.core.agent.graph import run_report_graph
from app.core.config import get_settings
from app.core.rag.indexer import index_reviews
from app.crud.reviews import get_reviews_by_product
from app.dependencies.database import SessionLocal

settings = get_settings()

celery_app = Celery(
    "review_agent",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)


def _parse_date_range(date_range: dict[str, str] | None) -> tuple[date | None, date | None]:
    if not date_range:
        return None, None
    start = date.fromisoformat(date_range["start"]) if date_range.get("start") else None
    end = date.fromisoformat(date_range["end"]) if date_range.get("end") else None
    return start, end


async def _load_reviews(product_id: str, date_range: dict[str, str] | None = None) -> list[dict]:
    start, end = _parse_date_range(date_range)
    async with SessionLocal() as session:
        rows = await get_reviews_by_product(session=session, product_id=product_id, start=start, end=end)
    return [
        {
            "review_id": row.id,
            "product_id": row.product_id,
            "rating": row.rating,
            "sentiment_score": float(row.sentiment_score),
            "content": row.content,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]


@celery_app.task(name="app.services.tasks.generate_report")
def generate_report(product_id: str, date_range: dict[str, str] | None = None) -> dict[str, Any]:
    reviews = asyncio.run(_load_reviews(product_id=product_id, date_range=date_range))
    index_reviews(product_id=product_id, rows=reviews)

    payload = {
        "product_id": product_id,
        "date_range": date_range,
        "started_at": datetime.utcnow().isoformat(),
        "reviews": reviews,
    }
    report = run_report_graph(payload)
    return {
        "product_id": product_id,
        "generated_at": datetime.utcnow().isoformat(),
        "report": report,
    }
