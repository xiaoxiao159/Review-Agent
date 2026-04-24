from unittest.mock import patch

from app.services.tasks import generate_report


@patch("app.services.tasks.run_report_graph", return_value={"summary": {"total_count": 0, "negative_count": 0, "negative_rate": 0.0, "avg_sentiment": 0.0}, "reason_categories": {}, "keywords": [], "sentiment_trend": [], "suggestions": [], "similar_cases": []})
@patch("app.services.tasks.index_reviews")
@patch("app.services.tasks.asyncio.run", return_value=[])
def test_generate_report_calls_index_and_graph(_run, mock_index, _graph):
    result = generate_report("p1", None)
    mock_index.assert_called_once_with(product_id="p1", rows=[])
    assert result["product_id"] == "p1"
    assert "report" in result
