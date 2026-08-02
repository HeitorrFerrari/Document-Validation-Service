"""
Trace visual no terminal (Fase 10 -- observabilidade): uma linha por etapa
do pipeline (RAG, grafo de chat, chamada de LLM) com os dados relevantes.
Não é logging estruturado de verdade, é só pra acompanhar o fluxo em dev.
"""
from app.core.logging import get_logger

_logger = get_logger("trace")

_COLORS = {
    "rag": "\033[36m",    # ciano
    "chat": "\033[35m",   # magenta
    "llm": "\033[33m",    # amarelo
    "guard": "\033[31m",  # vermelho -- rejeições de guardrail (ex.: prompt injection)
}
_RESET = "\033[0m"


def trace(tag: str, step: str, **fields) -> None:
    color = _COLORS.get(tag, "\033[37m")
    detalhes = " ".join(f"{chave}={valor!r}" for chave, valor in fields.items())
    _logger.info("%s[%s:%s]%s %s", color, tag, step, _RESET, detalhes)
