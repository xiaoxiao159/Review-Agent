from chromadb import PersistentClient

from app.core.config import get_settings
from app.core.rag.embedder import embed_texts

settings = get_settings()


def retrieve_similar_cases(product_id: str, query: str, top_k: int = 5) -> list[dict]:
    if not query:
        return []
    embedded = embed_texts([query])
    if not embedded:
        return []
    client = PersistentClient(path=settings.chroma_path)
    collection = client.get_or_create_collection(name=f"reviews_{product_id}")
    result = collection.query(query_embeddings=[embedded[0]], n_results=top_k)
    ids = result.get("ids", [[]])[0]
    docs = result.get("documents", [[]])[0]
    distances = result.get("distances", [[]])[0]
    output = []
    for idx, review_id in enumerate(ids):
        distance = float(distances[idx]) if idx < len(distances) else 1.0
        similarity = max(0.0, round(1.0 - distance, 4))
        content = docs[idx] if idx < len(docs) else ""
        output.append({"review_id": str(review_id), "content": content, "similarity_score": similarity})
    return output
