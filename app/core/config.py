"""
Configuração centralizada (Fase 0+).
Substitui os.getenv espalhado pelos módulos -- toda env var lida aqui.
"""
import os


class Settings:
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    openai_main_model: str = os.getenv("OPENAI_MAIN_MODEL", "gpt-4o-mini")
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0"))

    # Mongo (Fase 6)
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db: str = os.getenv("MONGO_DB", "validador_cv")

    # Redis / Celery (Fase 7)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

    # Qdrant (Fase 4)
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "curriculos")


settings = Settings()
