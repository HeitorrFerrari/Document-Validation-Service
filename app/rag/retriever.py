from openai import OpenAI
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.rag.qdrant_client import get_qdrant_client, COLLECTION_NAME

_openai = OpenAI()


def retrieve(session_id: str, query: str, top_k: int = 4) -> list[str]:
    client = get_qdrant_client()
    embedding = _openai.embeddings.create(model="text-embedding-3-small", input=query).data[0].embedding

    resultados = client.query_points(
        COLLECTION_NAME,
        query=embedding,
        query_filter=Filter(
            must=[FieldCondition(key="session_id", match=MatchValue(value=session_id))]
        ),
        limit=top_k,
    )
    return [ponto.payload["text"] for ponto in resultados.points]
