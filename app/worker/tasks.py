"""
Tasks assíncronas Celery (Fase 7): análise de CV em background.
"""
import os

from celery import Celery

from app.core.config import settings
from app.core.tracing import trace
from app.db.repositories.judge_repository import save_judgement
from app.db.repositories.resume_repository import save_resume
from app.db.repositories.validation_repository import save_validation_result
from app.extractions.docx.docx_extractor import extrair_texto_docx
from app.extractions.pdf.pdf_extractor import extrair_texto_pdf
from app.graph.graph import app_graph
from app.guard.guard import check_document_format, check_extracted_text
from app.judge.judge import evaluate as judge_evaluate
from app.rag.ingest import ingest_session
from app.schemas.job_requirements import JobRequirements

celery_app = Celery("validador_cv", broker=settings.celery_broker_url, backend=settings.celery_backend)

@celery_app.task
def analisar_curriculo_task(caminho_arquivo: str, job_json: str, job_id: str) -> dict:
    job_requirements = JobRequirements.model_validate_json(job_json)

    try:
        tipo = check_document_format(caminho_arquivo)
        texto = (
            extrair_texto_pdf(caminho_arquivo)
            if tipo == "pdf"
            else extrair_texto_docx(caminho_arquivo)
        )
        check_extracted_text(texto)
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

    return {
        "job_id": job_id,
        "resume_id": resume_id,
        "validation_id": validation_id,
        "session_id": validation_id,
        "resume": resume.model_dump(),
        "validation": resultado.model_dump(),
        "feedback": feedback,
    }
