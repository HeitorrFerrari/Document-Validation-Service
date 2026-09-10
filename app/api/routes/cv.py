"""
Rotas de currículo (Fase 8): upload de CV, disparo de análise, consulta de resultado.
"""
import tempfile
from pathlib import Path

from celery.result import AsyncResult
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.db.repositories.job_repository import get_job, save_job
from app.db.repositories.resume_repository import get_resume
from app.db.repositories.validation_repository import get_validation_result, list_validations
from app.schemas.job_requirements import JobRequirements
from app.worker.tasks import analisar_curriculo_task, celery_app

router = APIRouter(prefix="/cv", tags=["cv"])


@router.post("/analyze", status_code=202)
async def analyze_cv(file: UploadFile = File(...), job: str = Form(...)):
    """
    Recebe o arquivo do currículo e os requisitos da vaga (JSON como string
    de formulário) num único request, persiste a vaga no Mongo e dispara o
    pipeline completo (valida arquivo -> extrai texto -> extrai currículo
    estruturado -> valida elegibilidade -> gera feedback -> judge -> RAG)
    de forma assíncrona via Celery. A resposta retorna na hora com o
    `task_id`; o resultado é consultado depois em `/cv/status/{task_id}`.
    """
    conteudo = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(conteudo) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo excede o limite de {settings.max_upload_mb} MB.",
        )

    job_requirements = JobRequirements.model_validate_json(job)
    job_id = save_job(job_requirements)

    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(conteudo)
        tmp_path = tmp.name

    task = analisar_curriculo_task.delay(tmp_path, job, job_id)
    return {"task_id": task.id, "job": job, "job_id": job_id}

@router.get("/sessions")
async def list_sessions():
    """
    Histórico pro front: validações já processadas, mais recentes primeiro.
    Cada sessão é enriquecida com o título da vaga e o nome do candidato
    (uma consulta extra por sessão -- ok pro volume de um projeto de estudo).
    `session_id` == `validation_id`, o mesmo id que o `/chat/{session_id}`
    espera.
    """
    sessoes = list_validations()
    for sessao in sessoes:
        job = get_job(sessao["job_id"]) if sessao.get("job_id") else None
        resume = get_resume(sessao["resume_id"]) if sessao.get("resume_id") else None
        sessao["job_title"] = job.title if job else None
        sessao["candidate_name"] = resume.name if resume else None
    return {"sessions": sessoes}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    validation = get_validation_result(session_id)
    if validation is None:
        raise HTTPException(status_code=404, detail="Sessão de validação não encontrada.")

    job = get_job(validation.job_id) if validation.job_id else None
    resume = get_resume(validation.resume_id) if validation.resume_id else None
    return {
        "session_id": session_id,
        "validation": validation.model_dump(),
        "job": job.model_dump() if job else None,
        "candidate_name": resume.name if resume else None,
    }


@router.get("/status/{task_id}")
async def get_status(task_id: str):
    resultado = AsyncResult(task_id,app=celery_app)

    if resultado.failed():
        # ValueError vem dos guardrails (formato/texto) e a mensagem é escrita
        # pro candidato; qualquer outra exceção é interna e não deve vazar.
        if isinstance(resultado.result, ValueError):
            detail = str(resultado.result)
        else:
            detail = "Erro interno ao processar a análise. Tente novamente mais tarde."
        return {"status": resultado.status, "detail": detail}

    return {"status": resultado.status, "result": resultado.result}
