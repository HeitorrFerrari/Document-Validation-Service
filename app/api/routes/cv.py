"""
Rotas de currículo (Fase 8): upload de CV, disparo de análise, consulta de resultado.
"""
import tempfile
from pathlib import Path

from celery.result import AsyncResult
from fastapi import APIRouter, File, Form, UploadFile

from app.db.repositories.job_repository import save_job
from app.schemas.job_requirements import JobRequirements
from app.worker.tasks import analisar_curriculo_task, celery_app

router = APIRouter(prefix="/cv", tags=["cv"])


@router.post("/analyze", status_code=202)
async def analyze_cv(file: UploadFile = File(...), job: str = Form(...)):
    """
    Recebe o arquivo do currículo e os requisitos da vaga (JSON como string
    de formulário) num único request, e roda o pipeline inteiro na hora:
    valida o arquivo -> extrai o texto -> extrai o currículo estruturado ->
    valida elegibilidade -> gera feedback. Sem persistência ainda (Fase 6);
    tudo acontece dentro do mesmo ciclo de requisição.
    """
    job_requirements = JobRequirements.model_validate_json(job)
    job_id = save_job(job_requirements)

    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    task = analisar_curriculo_task.delay(tmp_path, job, job_id)
    return {"task_id": task.id, "job": job, "job_id": job_id}

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    resultado = AsyncResult(task_id,app=celery_app)

    if resultado.failed():
        return {"status": resultado.status, "detail": str(resultado.result)}

    return {"status": resultado.status, "result": resultado.result}
