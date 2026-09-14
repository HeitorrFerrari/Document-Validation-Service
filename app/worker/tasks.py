"""
Tasks assíncronas Celery (Fase 7): análise de CV em background.
"""
import os

from celery import Celery

from app.core.config import settings
from app.core.tracing import trace
from app.db.repositories.feedback_repository import save_feedback
from app.db.repositories.judge_repository import save_judgement
from app.db.repositories.resume_repository import save_resume
from app.db.repositories.validation_repository import save_validation_result
from app.extractions.docx.docx_extractor import extrair_texto_docx
from app.extractions.pdf.pdf_extractor import extrair_texto_pdf
from app.graph.graph import app_graph
from app.guard.guard import check_document_format, check_extracted_text, check_prompt_injection
from app.judge.judge import evaluate as judge_evaluate
from app.rag.ingest import ingest_session
from app.schemas.feedback import Feedback
from app.schemas.job_requirements import JobRequirements

celery_app = Celery("validador_cv", broker=settings.celery_broker_url, backend=settings.celery_backend)

@celery_app.task(throws=(ValueError,))
def analisar_curriculo_task(caminho_arquivo: str, job_json: str, job_id: str) -> dict:
    job_requirements = JobRequirements.model_validate_json(job_json)
    trace("worker", "task_start", job_id=job_id, job_title=job_requirements.title)

    try:
        tipo = check_document_format(caminho_arquivo)
        texto = (
            extrair_texto_pdf(caminho_arquivo)
            if tipo == "pdf"
            else extrair_texto_docx(caminho_arquivo)
        )
        check_extracted_text(texto)
        check_prompt_injection(texto)
    except ValueError as erro:
        trace("worker", "task_rejected", job_id=job_id, erro=str(erro))
        raise
    finally:
        os.remove(caminho_arquivo)

    estado_final = app_graph.invoke({
        "resume_text": texto,
        "job_requirements": job_requirements,
        "resume": None,
        "validation": None,
        "feedback": None,
    })
    resume = estado_final["resume"]
    resultado = estado_final["validation"]
    feedback = estado_final["feedback"]

    resume_id = save_resume(resume)
    resultado.resume_id = resume_id
    resultado.job_id = job_id
    validation_id = save_validation_result(resultado)
    # Sem isso o feedback só existiria no result backend do Celery, que expira
    # -- o histórico (`/cv/sessions/{id}`) lê do Mongo e ficaria sem ele.
    save_feedback(Feedback(text=feedback, validation_id=validation_id))
    trace(
        "worker", "task_persisted",
        job_id=job_id, resume_id=resume_id, validation_id=validation_id,
        score=resultado.score, is_eligible=resultado.is_eligible,
    )

    try:
        julgamento = judge_evaluate(resume, job_requirements, resultado, feedback)
        julgamento.validation_id = validation_id
        save_judgement(julgamento)
    except Exception as erro:
        trace("judge", "error", validation_id=validation_id, erro=str(erro))

    try:
        ingest_session(validation_id, resume, job_requirements, resultado)
    except Exception as erro:
        trace("rag", "error", validation_id=validation_id, erro=str(erro))

    trace("worker", "task_done", job_id=job_id, validation_id=validation_id)
    return {
        "job_id": job_id,
        "resume_id": resume_id,
        "validation_id": validation_id,
        "session_id": validation_id,
        "resume": resume.model_dump(),
        "validation": resultado.model_dump(),
        "feedback": feedback,
    }
