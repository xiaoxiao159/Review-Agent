from dashscope import TextEmbedding

from app.core.config import get_settings

settings = get_settings()


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    response = TextEmbedding.call(model=settings.embedding_model, input=texts)
    return [item["embedding"] for item in response.output["embeddings"]]
