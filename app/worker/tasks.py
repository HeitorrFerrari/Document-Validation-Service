"""
Tasks assíncronas Celery (Fase 7): análise de CV em background.
"""
import os

from celery import Celery

from app.agents.feedback.agent import build_feedback
from app.agents.validator.agent import validate_eligibility
from app.api.extraction.extract_data import extrair_curriculo
from app.core.config import settings
from app.db.repositories.resume_repository import save_resume
from app.db.repositories.validation_repository import save_validation_result
from app.extractions.docx.docx_extractor import extrair_texto_docx
from app.extractions.pdf.pdf_extractor import extrair_texto_pdf
from app.guard.guard import check_document_format, check_extracted_text
from app.schemas.job_requirements import JobRequirements

celery_app = Celery("validador_cv", broker=settings.celery_broker_url)

@celery_app.task
def analisar_curriculo_task(caminho_arquivo: str, job_json: str) -> dict:
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

    resume = extrair_curriculo(texto)
    resume_id = save_resume(resume)

    resultado = validate_eligibility(resume, job_requirements)
    resultado.resume_id = resume_id
    resultado.job_id = job_id
    validation_id = save_validation_result(resultado)

    feedback = build_feedback(resultado)

    return {
        "job_id": job_id,
        "resume_id": resume_id,
        "validation_id": validation_id,
        "resume": resume.model_dump(),
        "validation": resultado.model_dump(),
        "feedback": feedback,
    }
