"""
Entrypoint FastAPI (Fase 8).
Roda com: uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from app.api.routes import cv
from app.api.routes.input import requirements

app = FastAPI(title="Validador de Currículo")
app.include_router(requirements.router)
app.include_router(cv.router)
