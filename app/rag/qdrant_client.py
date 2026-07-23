from qdrant_client import QdrantClient

COLLECTION_NAME = "cv_chat_session"
VECTOR_SIZE = 1536 #Embedding pequeno

_client: QdrantClient | None = None

def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url="http://localhost:6333")