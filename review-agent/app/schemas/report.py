from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class DateRange(BaseModel):
    start: date
    end: date


class AnalyzeRequest(BaseModel):
    product_id: str = Field(min_length=1)
    date_range: DateRange | None = None


class AnalyzeResponse(BaseModel):
    task_id: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: Literal["pending", "running", "completed", "failed"]


class SimilarCase(BaseModel):
    review_id: str
    content: str
    similarity_score: float


class Summary(BaseModel):
    total_count: int
    negative_count: int
    negative_rate: float
    avg_sentiment: float


class SentimentTrendItem(BaseModel):
    month: str
    avg_sentiment: float


class ReportResponse(BaseModel):
    summary: Summary
    reason_categories: dict[str, int]
    keywords: list[str]
    sentiment_trend: list[SentimentTrendItem]
    suggestions: list[str]
    similar_cases: list[SimilarCase]
