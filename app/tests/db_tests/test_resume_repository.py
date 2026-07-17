from dotenv import load_dotenv

load_dotenv()

from app.api.extraction.extract_data import extrair_curriculo
from app.db.repositories.resume_repository import get_resume, save_resume
from app.extractions.pdf.pdf_extractor import extrair_texto_pdf
from app.guard.guard import check_document_format, check_extracted_text

if __name__ == "__main__":
    caminho = "docs/Curriculo-3.pdf"
    check_document_format(caminho)
    texto = extrair_texto_pdf(caminho)
    check_extracted_text(texto)
    resume = extrair_curriculo(texto)

    resume_id = save_resume(resume)
    print("salvo com id:", resume_id)

    resume_recuperado = get_resume(resume_id)
    print(resume_recuperado.model_dump_json(indent=2))
