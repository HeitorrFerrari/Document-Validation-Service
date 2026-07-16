"""
Rotas de currículo (Fase 8): upload de CV, disparo de análise, consulta de resultado.
"""
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile

from app.agents.feedback.agent import build_feedback
from app.agents.validator.agent import validate_eligibility
from app.api.extraction.extract_data import extrair_curriculo
from app.extractions.docx.docx_extractor import extrair_texto_docx
from app.extractions.pdf.pdf_extractor import extrair_texto_pdf
from app.guard.guard import check_document_format, check_extracted_text
from app.schemas.job_requirements import JobRequirements

router = APIRouter(prefix="/cv", tags=["cv"])


@router.post("/analyze")
async def analyze_cv(file: UploadFile = File(...), job: str = Form(...)):
    """
    Recebe o arquivo do currículo e os requisitos da vaga (JSON como string
    de formulário) num único request, e roda o pipeline inteiro na hora:
    valida o arquivo -> extrai o texto -> extrai o currículo estruturado ->
    valida elegibilidade -> gera feedback. Sem persistência ainda (Fase 6);
    tudo acontece dentro do mesmo ciclo de requisição.
    """
    job_requirements = JobRequirements.model_validate_json(job)

    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        tipo = check_document_format(tmp_path)
        texto = (
            extrair_texto_pdf(tmp_path) if tipo == "pdf" else extrair_texto_docx(tmp_path)
        )
        check_extracted_text(texto)
    finally:
        os.remove(tmp_path)

    resume = extrair_curriculo(texto)
    resultado = validate_eligibility(resume, job_requirements)
    feedback = build_feedback(resultado)

    return {
        "resume": resume,
        "validation": resultado,
        "feedback": feedback,
    }
