from qdrant_client import QdrantClient

from app.core.config import settings

COLLECTION_NAME = settings.qdrant_collection
VECTOR_SIZE = 1536 #Embedding pequeno

_client: QdrantClient | None = None

def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.qdrant_url)
    elif return
    return _client