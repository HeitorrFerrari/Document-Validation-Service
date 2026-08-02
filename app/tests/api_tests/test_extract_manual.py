from dotenv import load_dotenv

load_dotenv()

from app.api.extraction.extract_data import extrair_curriculo
from app.extractions.pdf.pdf_extractor import extrair_texto_pdf
from app.guard.guard import check_document_format, check_extracted_text

if __name__ == "__main__":
    caminho = "docs/Curriculo Heitor - 2026.pdf"
    check_document_format(caminho)
    cv_texto = extrair_texto_pdf(caminho)
    check_extracted_text(cv_texto)
    resultado = extrair_curriculo(cv_texto)
    print(resultado.model_dump_json(indent=2))

