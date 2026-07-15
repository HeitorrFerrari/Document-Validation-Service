from dotenv import load_dotenv

load_dotenv()

from app.api.extraction.extract_data import extrair_curriculo
from app.extractions.pdf.pdf_extractor import extrair_texto_pdf

if __name__ == "__main__":
    caminho = "docs/Curriculo Heitor - 2026.pdf"
    cv_texto = extrair_texto_pdf(caminho)
    resultado = extrair_curriculo(cv_texto)
    print(resultado.model_dump_json(indent=2))

