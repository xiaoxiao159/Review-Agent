from app.core.agent.llm_nodes import (
    build_report_node,
    classify_reasons_node,
    extract_keywords_node,
    generate_suggestions_node,
)


def test_llm_nodes_pipeline():
    state = {
        "reviews": [
            {"sentiment_score": 0.2, "created_at": "2026-01-01", "content": "delivery too slow"},
            {"sentiment_score": 0.3, "created_at": "2026-01-20", "content": "quality issue and high price"},
        ],
        "negative_reviews": [
            {"content": "delivery too slow"},
            {"content": "quality issue and high price"},
        ],
    }

    classify_reasons_node(state)
    extract_keywords_node(state)
    generate_suggestions_node(state)
    build_report_node(state)

    assert "summary" in state
    assert state["summary"]["negative_count"] == 2
    assert "suggestions" in state and len(state["suggestions"]) > 0
    assert "reason_categories" in state
    assert "report" in state and "keywords" in state["report"]
