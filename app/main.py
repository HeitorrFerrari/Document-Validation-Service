"""
Entrypoint FastAPI (Fase 8).
Roda com: uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from app.api.routes import chat, cv
from app.api.routes.input import requirements

app = FastAPI(title="Validador de Currículo")
app.include_router(requirements.router)
app.include_router(cv.router)
app.include_router(chat.router)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
