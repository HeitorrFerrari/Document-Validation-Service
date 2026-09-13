"""
Guardrails de entrada (Fase 3): formato de arquivo, qualidade do texto extraído e
detecção simples de prompt injection via regex.
"""
import re
import zipfile

from app.core.config import settings
from app.core.tracing import trace

_PADROES_PROMPT_INJECTION = [
    r"ignor[ae]\s+(todas?\s+)?(as\s+)?instru[çc][õo]es\s+(anteriores|acima)",
    r"desconsidere\s+(as\s+)?instru[çc][õo]es\s+(anteriores|acima)",
    r"esque[çc]a\s+(suas\s+|as\s+)?instru[çc][õo]es",
    r"ignore\s+(all\s+)?(previous|prior|the above)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
    r"forget\s+(your\s+|all\s+)?(previous\s+)?instructions",
    r"you\s+are\s+now\s+",
    r"aja\s+como\s+(se\s+)?(voc[êe]\s+)?(fosse|é)",
    r"act\s+as\s+(if\s+you\s+are|a[n]?)\s+",
    r"system\s*prompt",
    r"modo\s+desenvolvedor",
    r"developer\s+mode",
    r"\bDAN\b",
    r"d[êe]\s+nota\s+(m[aá]xima|100)",
    r"aprovad[oa]\s+automaticamente",
    r"score\s*[:=]?\s*100",
    r"is_eligible\s*[:=]?\s*true",
    r"revele\s+(o\s+)?(seu\s+)?prompt",
    r"reveal\s+(your\s+)?(system\s+)?prompt",
    r"mostre\s+suas\s+instru[çc][õo]es",
    r"show\s+(me\s+)?your\s+instructions",
    r"\bjailbreak\b",
    r"prompt\s+injection",
    r"voc[êe]\s+n[ãa]o\s+tem\s+(mais\s+)?restri[çc][õo]es",
    r"you\s+have\s+no\s+restrictions",
    r"n[ãa]o\s+aplique\s+(nenhum\s+)?filtro",
    r"do\s+not\s+apply\s+any\s+filter",
    r"contorne\s+(as\s+)?regras",
    r"bypass\s+(the\s+)?rules",
]


def check_prompt_injection(text: str) -> None:
    """
    Varredura simples por regex atrás de frases típicas de tentativa de
    manipular o agente (ex.: "ignore as instruções anteriores", "dê nota
    máxima"). Não é uma defesa robusta -- é heurística de portfólio, não
    substitui um classificador dedicado ou sanitização em produção real.
    """
    texto_lower = text.lower()
    for padrao in _PADROES_PROMPT_INJECTION:
        match = re.search(padrao, texto_lower)
        if match:
            trace(
                "guard", "prompt_injection_detected",
                padrao=padrao,
                trecho=texto_lower[max(0, match.start() - 20):match.end() + 20],
            )
            raise ValueError(
                "Texto do currículo contém trechos suspeitos de tentativa de "
                "manipular a avaliação -- revise o conteúdo e reenvie."
            )


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
