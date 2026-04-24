from unittest.mock import patch

from app.core.rag.indexer import index_reviews


@patch("app.core.rag.indexer.embed_texts", return_value=[[0.1, 0.2], [0.2, 0.3]])
@patch("app.core.rag.indexer.PersistentClient")
def test_index_reviews_upsert_called(mock_client, _):
    collection = mock_client.return_value.get_or_create_collection.return_value
    index_reviews(
        "p1",
        [
            {"review_id": "r1", "content": "bad delivery"},
            {"review_id": "r2", "content": "poor quality"},
        ],
    )
    assert collection.upsert.called


@patch("app.core.rag.indexer.embed_texts", return_value=[])
@patch("app.core.rag.indexer.PersistentClient")
def test_index_reviews_skip_empty_content(mock_client, _):
    collection = mock_client.return_value.get_or_create_collection.return_value
    index_reviews("p1", [{"review_id": "r1", "content": "   "}])
    assert not collection.upsert.called
