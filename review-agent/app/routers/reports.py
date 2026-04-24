from fastapi import APIRouter, Depends

from app.dependencies.current_user import get_current_user
from app.dependencies.database import get_redis
from app.schemas.report import AnalyzeRequest, AnalyzeResponse, ReportResponse, TaskStatusResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_reviews(payload: AnalyzeRequest, _: dict = Depends(get_current_user)) -> AnalyzeResponse:
    service = ReportService(redis_client=get_redis())
    date_range = payload.date_range.model_dump(mode="json") if payload.date_range else None
    task_id = await service.submit_report(product_id=payload.product_id, date_range=date_range)
    return AnalyzeResponse(task_id=task_id)


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def report_status(task_id: str, _: dict = Depends(get_current_user)) -> TaskStatusResponse:
    service = ReportService(redis_client=get_redis())
    status = await service.get_status(task_id)
    return TaskStatusResponse(task_id=task_id, status=status)


@router.get("/{task_id}", response_model=ReportResponse)
async def get_report(
    task_id: str,
    _: dict = Depends(get_current_user),
) -> ReportResponse:
    service = ReportService(redis_client=get_redis())
    report = await service.get_report_by_task(task_id=task_id)
    return ReportResponse.model_validate(report)
