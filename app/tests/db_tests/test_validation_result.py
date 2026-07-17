from dotenv import load_dotenv

load_dotenv()

from app.agents.validator.agent import validate_eligibility
from app.api.extraction.extract_data import extrair_curriculo
from app.db.repositories.validation_repository import get_validation_result, save_validation_result
from app.extractions.pdf.pdf_extractor import extrair_texto_pdf
from app.guard.guard import check_document_format, check_extracted_text
from app.schemas.job_requirements import JobRequirements

if __name__ == "__main__":
    caminho = "docs/Curriculo-3.pdf"
    check_document_format(caminho)
    texto = extrair_texto_pdf(caminho)
    check_extracted_text(texto)
    resume = extrair_curriculo(texto)

    job = JobRequirements(
        title="Desenvolvedor Backend Pleno",
        required_skills=["Python", "SQL", "Git"],
        desired_skills=["Docker", "FastAPI"],
        min_years_experience=2,
        min_education="Graduação em Ciência da Computação ou correlatas",
    )

    resultado = validate_eligibility(resume, job)

    validation_id = save_validation_result(resultado)
    print("Salvo com id: ", validation_id)

    validation_recuperada = get_validation_result(validation_id)
    print(validation_recuperada.model_dump_json(indent=2))