"""
Fase 1 — Estado conversacional sem framework.

Objetivo: sentir a dor de gerenciar manualmente o que entra/sai da
conversa e onde guardar resultados intermediários -- SEM LangGraph,
SEM classes de estado, só Python puro (listas e dicts).

Fluxo que você precisa suportar:
  1. Usuário manda o texto do CV
  2. Usuário manda o texto da vaga
  3. Usuário pode perguntar algo sobre o resultado (ex: "por que esse score?")

Como rodar:
    python -m app.api.extraction.conversa   (ajuste o caminho pro seu projeto)
"""

from app.api.extraction.extractData import extrair_curriculo

def rodar_conversa():
    historico: list[dict] = []
    cv_extraido: None
    vaga: None
    etapa: "aguardando_cv"

    print("Cole o texto do cv (ou digite 'sair' pra cancelar):")

    while True:
        entrada = input("> ")

        if entrada.strip().lower() == "sair":
            break

        if etapa == "aguardando_cv":
            if cv_extraido is None:
                print("Cole o texto do cv (ou digite 'sair')")