from chromadb import PersistentClient

from app.core.config import get_settings
from app.core.rag.embedder import embed_texts

settings = get_settings()


def _get_collection(product_id: str):
    client = PersistentClient(path=settings.chroma_path)
    return client.get_or_create_collection(name=f"reviews_{product_id}")


def index_reviews(product_id: str, rows: list[dict]) -> None:
    valid_rows = [r for r in rows if str(r.get("content", "")).strip()]
    if not valid_rows:
        return
    collection = _get_collection(product_id)
    ids = [str(r["review_id"]) for r in valid_rows]
    docs = [str(r["content"]) for r in valid_rows]
    vectors = embed_texts(docs)
    collection.upsert(ids=ids, documents=docs, embeddings=vectors, metadatas=[{"product_id": product_id}] * len(valid_rows))
