"""
Tools conversacionais do chat: cada uma cobre uma categoria de pergunta
provável do candidato (nota geral, elegibilidade, pontos fortes/fracos,
orientação, critério específico) e devolve um texto PRONTO, escrito aqui,
parametrizado pelos dados reais da validação -- não é o LLM que redige o
conteúdo, só decide qual tool chamar e encaixa o texto na conversa. É assim
que a resposta fica consistente entre sessões e para de variar "tom de IA"
a cada pergunta parecida.
"""
from langchain_core.tools import tool

from app.schemas.validation_result import ValidationResult

_LIMIAR_FORTE = 70
_LIMIAR_FRACO = 50


def _texto_nota_geral(validation: ValidationResult) -> str:
    return f"Sua nota geral nesta avaliação foi {validation.score:.0f} de 100. {validation.reasoning}"


def _texto_elegibilidade(validation: ValidationResult) -> str:
    if validation.is_eligible:
        return (
            f"Você foi considerado elegível para esta vaga, com nota geral de "
            f"{validation.score:.0f} de 100."
        )
    return (
        f"Você não foi considerado elegível para esta vaga, com nota geral de "
        f"{validation.score:.0f} de 100. {validation.reasoning}"
    )


def _texto_pontos_fortes(validation: ValidationResult) -> str:
    fortes = [r for r in validation.requirement_scores if r.score >= _LIMIAR_FORTE]
    if not fortes:
        return (
            "Nenhum critério se destacou como ponto forte nesta avaliação -- a "
            "maioria ficou abaixo do que a vaga pede."
        )
    itens = "\n".join(f"- {r.requirement}: {r.detail}" for r in fortes)
    return f"Os pontos que mais contaram a seu favor nesta avaliação foram:\n{itens}"


def _texto_pontos_a_melhorar(validation: ValidationResult) -> str:
    fracos = [r for r in validation.requirement_scores if r.score < _LIMIAR_FRACO]
    if not fracos:
        return (
            "Não houve nenhum critério com desempenho crítico nesta avaliação -- "
            "os pontos que puxaram a nota para baixo foram distribuídos entre os "
            "critérios, sem um único fator decisivo."
        )
    itens = "\n".join(f"- {r.requirement}: {r.detail}" for r in fracos)
    return f"Os critérios que mais impactaram sua nota para baixo foram:\n{itens}"


def _texto_orientacao(validation: ValidationResult) -> str:
    a_desenvolver = [r for r in validation.requirement_scores if r.score < _LIMIAR_FORTE]
    if not a_desenvolver:
        return (
            "Seu desempenho foi consistente em todos os critérios avaliados -- "
            "não há uma área específica que eu recomende priorizar para esta vaga."
        )
    itens = "\n".join(f"- {r.requirement}" for r in a_desenvolver)
    return (
        "Com base nos critérios que mais impactaram sua nota, as áreas mais "
        f"relevantes para desenvolver são:\n{itens}"
    )


def _texto_criterio(validation: ValidationResult, nome_criterio: str) -> str:
    alvo = nome_criterio.lower()
    candidatos = [r for r in validation.requirement_scores if alvo in r.requirement.lower()]
    if not candidatos:
        nomes = ", ".join(r.requirement for r in validation.requirement_scores)
        return f"Não encontrei um critério chamado '{nome_criterio}' nesta avaliação. Os critérios avaliados foram: {nomes}."
    r = candidatos[0]
    return f"No critério '{r.requirement}', sua nota foi {r.score:.0f} de 100. {r.detail}"


def build_conversational_tools(validation: ValidationResult) -> list:
    """Constrói as tools fechadas sobre o ValidationResult desta sessão."""

    @tool
    def explicar_nota_geral() -> str:
        """Usa quando o candidato pergunta por que recebeu essa nota, o que
        significa o score geral, ou pede um resumo geral do resultado."""
        return _texto_nota_geral(validation)

    @tool
    def explicar_elegibilidade() -> str:
        """Usa quando o candidato pergunta se foi aprovado, se é elegível,
        ou se passou para a vaga."""
        return _texto_elegibilidade(validation)

    @tool
    def listar_pontos_fortes() -> str:
        """Usa quando o candidato pergunta quais foram seus pontos fortes,
        o que ele acertou, ou o que jogou a favor dele na avaliação."""
        return _texto_pontos_fortes(validation)

    @tool
    def listar_pontos_a_melhorar() -> str:
        """Usa quando o candidato pergunta o que faltou, quais foram os
        pontos fracos, ou por que algum critério pesou contra ele."""
        return _texto_pontos_a_melhorar(validation)

    @tool
    def orientacao_de_melhoria() -> str:
        """Usa quando o candidato pergunta como pode melhorar, o que
        estudar ou desenvolver, ou pede dicas para próximas vagas."""
        return _texto_orientacao(validation)

    @tool
    def explicar_criterio(nome_criterio: str) -> str:
        """Usa quando o candidato pergunta especificamente sobre um
        critério/requisito nomeado da vaga (ex.: uma skill, experiência ou
        formação específica). nome_criterio é o termo que o candidato usou
        pra se referir a esse critério."""
        return _texto_criterio(validation, nome_criterio)

    return [
        explicar_nota_geral,
        explicar_elegibilidade,
        listar_pontos_fortes,
        listar_pontos_a_melhorar,
        orientacao_de_melhoria,
        explicar_criterio,
    ]
