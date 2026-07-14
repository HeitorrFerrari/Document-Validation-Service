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
    historico.append(
        {
            "state": "aguardando_cv",
            "role": "user"
        }
    )
    vaga: None
    etapa: "aguardando_cv"

    print("Cole o texto do cv (ou digite 'sair' pra cancelar):")

    while True:
        entrada = input()
        if entrada == "sair":
            break
        elif etapa == "aguardando_cv":
            cv_extraido = extrair_curriculo(entrada)
            print("Voce deve aguardar pra ver a pontuacao do seu CV")
            historico.append.state = "analisando_cv"
            pass
        elif etapa == "analisando_cv":
            #Chamada do primeiro agente que sera responsavel por fazer a validacao do curriculo e posteriormente dar uma nota pro mesmo.
            pass
        elif entrada == "faq_geral":
            #Aqui é entregue a pontuacao do curriculo e questionado ao usuario se gostaria de entender porque a nota foi aquela em determinado ponto. Conversa tocada pela LLM
            pass

if __name__ == "__main__":
    rodar_conversa()