from collections import Counter


def classify_reasons_node(state: dict) -> dict:
    negatives = state.get("negative_reviews", [])
    buckets = Counter()
    for review in negatives:
        text = review.get("content", "").lower()
        if "logistics" in text or "delivery" in text:
            buckets["logistics"] += 1
        elif "quality" in text:
            buckets["quality"] += 1
        elif "price" in text:
            buckets["price"] += 1
        else:
            buckets["other"] += 1
    state["reason_categories"] = dict(buckets)
    return state


def extract_keywords_node(state: dict) -> dict:
    words = []
    for review in state.get("negative_reviews", []):
        words.extend([w.strip(".,!?") for w in review.get("content", "").lower().split()])
    stopwords = {"the", "a", "an", "is", "are", "was", "were", "and", "or", "to", "of"}
    ranked = Counter([w for w in words if len(w) > 2 and w not in stopwords])
    state["keywords"] = [w for w, _ in ranked.most_common(10)]
    return state


def generate_suggestions_node(state: dict) -> dict:
    reasons = state.get("reason_categories", {})
    suggestions = []
    if reasons.get("logistics"):
        suggestions.append("Optimize delivery SLA and packaging checks")
    if reasons.get("quality"):
        suggestions.append("Strengthen quality inspection and supplier audits")
    if reasons.get("price"):
        suggestions.append("Review pricing strategy and add targeted promotions")
    if not suggestions:
        suggestions.append("Keep monitoring reviews and close customer feedback loop")
    state["suggestions"] = suggestions
    return state


def build_report_node(state: dict) -> dict:
    reviews = state.get("reviews", [])
    negatives = state.get("negative_reviews", [])
    total = len(reviews)
    negative_count = len(negatives)
    avg_sentiment = round(sum(r.get("sentiment_score", 0.0) for r in reviews) / total, 4) if total else 0.0
    state["summary"] = {
        "total_count": total,
        "negative_count": negative_count,
        "negative_rate": round((negative_count / total), 4) if total else 0.0,
        "avg_sentiment": avg_sentiment,
    }
    monthly: dict[str, list[float]] = {}
    for row in reviews:
        month = str(row.get("created_at", ""))[:7]
        monthly.setdefault(month, []).append(float(row.get("sentiment_score", 0.0)))
    state["sentiment_trend"] = [
        {"month": m, "avg_sentiment": round(sum(vals) / len(vals), 4)}
        for m, vals in sorted(monthly.items())
    ]
    state["report"] = {
        "summary": state["summary"],
        "reason_categories": state.get("reason_categories", {}),
        "keywords": state.get("keywords", []),
        "sentiment_trend": state["sentiment_trend"],
        "suggestions": state.get("suggestions", []),
        "similar_cases": state.get("similar_cases", []),
    }
    return state
