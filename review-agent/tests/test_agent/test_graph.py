from app.core.agent.graph import run_report_graph


def test_graph_short_circuit_when_no_negative():
    payload = {
        "product_id": "p1",
        "reviews": [
            {"rating": 5, "sentiment_score": 0.9, "content": "great", "created_at": "2026-01-01"},
            {"rating": 4, "sentiment_score": 0.8, "content": "good", "created_at": "2026-01-10"},
        ],
    }
    result = run_report_graph(payload)
    assert result["summary"]["negative_count"] == 0
    assert result["similar_cases"] == []
