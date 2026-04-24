from typing import TypedDict


class ReportState(TypedDict, total=False):
    product_id: str
    date_range: dict | None
    reviews: list[dict]
    negative_reviews: list[dict]
    reason_categories: dict[str, int]
    keywords: list[str]
    suggestions: list[str]
    similar_cases: list[dict]
    summary: dict
    sentiment_trend: list[dict]
    report: dict
