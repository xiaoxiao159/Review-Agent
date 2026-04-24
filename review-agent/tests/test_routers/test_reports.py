from unittest.mock import AsyncMock

from app.schemas.report import ReportResponse


def test_analyze_returns_task_id(client, auth_header, monkeypatch):
    async def _submit(self, product_id, date_range=None):
        return "task-1"

    monkeypatch.setattr("app.services.report_service.ReportService.submit_report", _submit)

    response = client.post(
        "/api/v1/reports/analyze",
        headers=auth_header,
        json={"product_id": "p001", "date_range": {"start": "2026-01-01", "end": "2026-01-31"}},
    )
    assert response.status_code == 200
    assert response.json()["task_id"] == "task-1"


def test_status_returns_running(client, auth_header, monkeypatch):
    async def _status(self, task_id):
        return "running"

    monkeypatch.setattr("app.services.report_service.ReportService.get_status", _status)
    response = client.get("/api/v1/reports/status/task-1", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_get_report_returns_schema(client, auth_header, monkeypatch):
    async def _report(self, task_id):
        return {
            "summary": {"total_count": 1, "negative_count": 1, "negative_rate": 1.0, "avg_sentiment": 0.2},
            "reason_categories": {"quality": 1},
            "keywords": ["quality"],
            "sentiment_trend": [{"month": "2026-01", "avg_sentiment": 0.2}],
            "suggestions": ["Improve QC"],
            "similar_cases": [{"review_id": "r1", "content": "bad", "similarity_score": 0.8}],
        }

    monkeypatch.setattr("app.services.report_service.ReportService.get_report_by_task", _report)
    response = client.get("/api/v1/reports/task-1", headers=auth_header)
    assert response.status_code == 200
    ReportResponse.model_validate(response.json())


def test_analyze_without_token_returns_401(client):
    response = client.post("/api/v1/reports/analyze", json={"product_id": "p001"})
    assert response.status_code == 401
    assert response.json()["code"] == "AUTH_401"
