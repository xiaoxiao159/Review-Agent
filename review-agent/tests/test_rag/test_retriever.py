from unittest.mock import patch

from app.core.rag.retriever import retrieve_similar_cases


@patch("app.core.rag.retriever.embed_texts", return_value=[[0.1, 0.2, 0.3]])
@patch("app.core.rag.retriever.PersistentClient")
def test_retrieve_similar_cases(mock_client, _):
    collection = mock_client.return_value.get_or_create_collection.return_value
    collection.query.return_value = {
        "ids": [["r1"]],
        "documents": [["bad delivery"]],
        "distances": [[0.2]],
    }
    result = retrieve_similar_cases("p1", "bad", 5)
    assert result[0]["review_id"] == "r1"
    assert result[0]["similarity_score"] == 0.8


def test_retrieve_similar_cases_empty_query():
    assert retrieve_similar_cases("p1", "", 5) == []
