"""
Entrypoint FastAPI (Fase 8).
Roda com: uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from app.api.routes import chat, cv, evaluation
from app.api.routes.input import requirements

app = FastAPI(title="Validador de Currículo")


@app.middleware("http")
async def disable_static_cache(request, call_next):
    response = await call_next(request)
    if request.url.path in {
        "/", "/index.html", "/analise.html", "/conversas.html",
        "/style.css", "/app.js", "/conversas.js", "/favicon.svg",
    }:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


app.include_router(requirements.router)
app.include_router(cv.router)
app.include_router(chat.router)
app.include_router(evaluation.router)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
