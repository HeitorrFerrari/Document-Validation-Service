"""
Entrypoint FastAPI (Fase 8).
Roda com: uvicorn app.main:app --reload
"""
from fastapi import FastAPI

from app.api.routes.input import requirements

app = FastAPI(title="Validador de Currículo")
app.include_router(requirements.router)
