from pypdf import PdfReader


def extrair_texto_pdf(caminho: str) -> str:
    leitor = PdfReader(caminho)
    paginas = (pagina.extract_text() or "" for pagina in leitor.pages)
    return "\n".join(paginas)
