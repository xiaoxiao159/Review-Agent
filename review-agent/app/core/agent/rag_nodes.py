from typing import Any

from app.core.rag.retriever import retrieve_similar_cases


def rag_retrieval_node(state: dict) -> dict:
    product_id = state.get("product_id", "")
    negatives = state.get("negative_reviews", [])
    query = negatives[0]["content"] if negatives else ""
    state["similar_cases"] = retrieve_similar_cases(product_id=product_id, query=query, top_k=5)
    return state


def load_reviews_node_factory(fetch_reviews):
    def load_reviews_node(state: dict) -> dict:
        state["reviews"] = fetch_reviews(state)
        return state

    return load_reviews_node


def filter_negative_node(state: dict) -> dict:
    reviews = state.get("reviews", [])
    state["negative_reviews"] = [
        r for r in reviews if int(r.get("rating", 0)) <= 3 or float(r.get("sentiment_score", 1.0)) < 0.4
    ]
    return state


def should_short_circuit(state: dict) -> str:
    if len(state.get("negative_reviews", [])) == 0:
        return "END"
    return "rag_retrieval"
