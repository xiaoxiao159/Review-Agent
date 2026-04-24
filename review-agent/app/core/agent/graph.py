from __future__ import annotations

from collections import defaultdict

from langgraph.graph import END, START, StateGraph

from app.core.agent.llm_nodes import (
    build_report_node,
    classify_reasons_node,
    extract_keywords_node,
    generate_suggestions_node,
)
from app.core.agent.rag_nodes import (
    filter_negative_node,
    load_reviews_node_factory,
    rag_retrieval_node,
    should_short_circuit,
)
from app.core.agent.state import ReportState


def _default_fetch_reviews(state: dict) -> list[dict]:
    return state.get("reviews", [])


def _zero_report(state: dict) -> dict:
    reviews = state.get("reviews", [])
    total = len(reviews)
    avg = round(sum(float(r.get("sentiment_score", 0.0)) for r in reviews) / total, 4) if total else 0.0
    trend_map: dict[str, list[float]] = defaultdict(list)
    for row in reviews:
        month = str(row.get("created_at", ""))[:7]
        trend_map[month].append(float(row.get("sentiment_score", 0.0)))
    state["report"] = {
        "summary": {
            "total_count": total,
            "negative_count": 0,
            "negative_rate": 0.0,
            "avg_sentiment": avg,
        },
        "reason_categories": {},
        "keywords": [],
        "sentiment_trend": [
            {"month": m, "avg_sentiment": round(sum(vals) / len(vals), 4)}
            for m, vals in sorted(trend_map.items())
        ],
        "suggestions": ["No negative reviews found in selected range"],
        "similar_cases": [],
    }
    return state


def build_graph(fetch_reviews=_default_fetch_reviews):
    graph = StateGraph(ReportState)

    graph.add_node("load_reviews", load_reviews_node_factory(fetch_reviews))
    graph.add_node("filter_negative", filter_negative_node)
    graph.add_node("rag_retrieval", rag_retrieval_node)
    graph.add_node("classify_reasons", classify_reasons_node)
    graph.add_node("extract_keywords", extract_keywords_node)
    graph.add_node("generate_suggestions", generate_suggestions_node)
    graph.add_node("build_report", build_report_node)
    graph.add_node("zero_report", _zero_report)

    graph.add_edge(START, "load_reviews")
    graph.add_edge("load_reviews", "filter_negative")
    graph.add_conditional_edges(
        "filter_negative",
        should_short_circuit,
        {"END": "zero_report", "rag_retrieval": "rag_retrieval"},
    )
    graph.add_edge("rag_retrieval", "classify_reasons")
    graph.add_edge("classify_reasons", "extract_keywords")
    graph.add_edge("extract_keywords", "generate_suggestions")
    graph.add_edge("generate_suggestions", "build_report")
    graph.add_edge("build_report", END)
    graph.add_edge("zero_report", END)

    return graph.compile()


def run_report_graph(payload: dict, fetch_reviews=_default_fetch_reviews) -> dict:
    app = build_graph(fetch_reviews=fetch_reviews)
    output = app.invoke(payload)
    return output.get("report", {})
