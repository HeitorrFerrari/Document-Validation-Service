"""
Guardrails de entrada/saída (Fase 3): prompt injection, PII, conteúdo fora do escopo.
"""
import zipfile

from app.core.config import settings


def check_document_format(path: str) -> str:
    """
    Valida o tipo real do arquivo pela assinatura de bytes (magic number),
    não pela extensão do nome -- evita que um arquivo renomeado (ex.: .exe
    virando .pdf) engane o resto do pipeline.
    """
    with open(path, "rb") as f:
        header = f.read(8)

    if header.startswith(b"%PDF-"):
        return "pdf"

    if header.startswith(b"PK\x03\x04"):
        with zipfile.ZipFile(path) as arquivo_zip:
            if "word/document.xml" in arquivo_zip.namelist():
                return "docx"

    raise ValueError("Formato de arquivo não suportado — envie um PDF ou DOCX válido.")


def check_extracted_text(text: str, min_length: int = 50) -> None:
    """
    Garante que a extração produziu texto dentro de limites razoáveis antes de
    mandar pro LLM -- curto demais (PDF escaneado sem camada de texto) gera
    resultado alucinado; longo demais (documento que não é um currículo)
    estoura contexto e custo de token.
    """
    if len(text.strip()) < min_length:
        raise ValueError(
            "Texto extraído insuficiente -- documento pode estar vazio, "
            "corrompido, ou ser um scan sem camada de texto (precisa de OCR)."
        )

    if len(text) > settings.max_text_chars:
        raise ValueError(
            "Documento muito longo para análise -- envie um currículo de "
            "tamanho convencional."
        )
