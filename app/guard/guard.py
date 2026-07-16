"""
Guardrails de entrada/saída (Fase 3): prompt injection, PII, conteúdo fora do escopo.
"""
import zipfile


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

    raise ValueError(f"Formato de arquivo não suportado: {path}")


def check_extracted_text(text: str, min_length: int = 50) -> None:
    """
    Garante que a extração produziu texto de verdade antes de mandar pro LLM --
    evita mandar string vazia/curta (ex.: PDF escaneado sem camada de texto) e
    receber de volta um resultado alucinado.
    """
    if len(text.strip()) < min_length:
        raise ValueError(
            "Texto extraído insuficiente -- documento pode estar vazio, "
            "corrompido, ou ser um scan sem camada de texto (precisa de OCR)."
        )
