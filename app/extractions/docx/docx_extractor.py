from docx import Document

def extrair_texto_docx(caminho: str) -> str:
    documento = Document(caminho)
    return "\n".join(paragrafo.text for paragrafo in documento.paragraphs)