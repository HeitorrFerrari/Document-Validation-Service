from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from app.chats.tools import build_conversational_tools
from app.core.config import settings
from app.core.tracing import trace
from app.db.repositories.validation_repository import get_validation_result
from app.prompts.base import RH_PERSONA, build_system_prompt
from app.rag.retriever import retrieve
from app.chats.chat_state import ChatState

_llm = ChatOpenAI(model=settings.openai_main_model, temperature=settings.openai_temperature)

_ROLE_INSTRUCTIONS = (
    f"{RH_PERSONA} "
    "Sua função neste chat é apresentar a nota, explicar e debater o "
    "resultado da validação do currículo contra a vaga, e esclarecer as "
    "dúvidas que o candidato enviar. A seção 'Resultado da validação' "
    "abaixo é o fato central e SEMPRE verdadeiro sobre essa sessão -- nunca "
    "contradiga a nota ou a elegibilidade dela. A seção 'Contexto adicional' "
    "traz detalhes por critério; use-a pra aprofundar, mas nunca invente "
    "nota, critério ou detalhe que não esteja em nenhuma das duas seções. "
    "Você tem ferramentas que cobrem as perguntas mais prováveis do "
    "candidato (nota geral, elegibilidade, pontos fortes, pontos a "
    "melhorar, orientação, critério específico). Quando a pergunta se "
    "encaixar claramente em uma delas, chame a ferramenta e apresente o "
    "texto que ela retorna de forma direta, com no máximo uma frase de "
    "transição -- não reescreva nem resuma o conteúdo da ferramenta. Só "
    "responda livremente, sem ferramenta, quando a pergunta não se encaixar "
    "em nenhuma delas."
)


def load_session_node(state: ChatState) -> dict:
    trace("chat", "load_session_node", session_id=state["session_id"])
    validation = get_validation_result(state["session_id"])
    if validation is None:
        raise ValueError(f"Sessão de validação não encontrada: {state['session_id']}")
    return {"validation": validation}


def retrieve_node(state: ChatState) -> dict:
    trace("chat", "retrieve_node", session_id=state["session_id"], question=state["question"])
    # Qdrant fora do ar não pode derrubar o chat: a nota/elegibilidade já veio
    # do Mongo (load_session_node), então degrada pra responder sem os chunks
    # de detalhe por critério em vez de retornar 500.
    try:
        chunks = retrieve(state["session_id"], state["question"])
    except Exception as erro:
        trace("rag", "error", session_id=state["session_id"], erro=str(erro))
        chunks = []
    return {"retrieved_context": chunks}


def _trace_uso(resposta) -> None:
    uso = resposta.usage_metadata or {}
    trace(
        "llm", "usage",
        model=settings.openai_main_model,
        input_tokens=uso.get("input_tokens"),
        output_tokens=uso.get("output_tokens"),
        total_tokens=uso.get("total_tokens"),
    )


def generate_node(state: ChatState) -> dict:
    validation = state["validation"]
    contexto = "\n".join(state["retrieved_context"]) or "(detalhes por critério indisponíveis no momento)"
    trace(
        "chat", "generate_node",
        session_id=state["session_id"],
        context_chunks=len(state["retrieved_context"]),
        history_messages=len(state["messages"]),
    )

    resumo_validacao = (
        f"Elegível: {validation.is_eligible}. Score geral: {validation.score}/100. "
        f"Justificativa: {validation.reasoning}"
    )
    system = SystemMessage(
        content=(
            f"{build_system_prompt(_ROLE_INSTRUCTIONS, include_scope_guard=True)}\n\n"
            f"Resultado da validação:\n{resumo_validacao}\n\n"
            f"Contexto adicional (detalhe por critério):\n{contexto}"
        )
    )
    pergunta = HumanMessage(content=state["question"])

    tools = build_conversational_tools(validation)
    ferramentas_por_nome = {t.name: t for t in tools}
    llm_com_tools = _llm.bind_tools(tools)

    historico = [system, *state["messages"], pergunta]
    resposta = llm_com_tools.invoke(historico)
    _trace_uso(resposta)

    # Loop de tool-calling limitado a uma rodada: as tools cobrem perguntas
    # pontuais (nota, elegibilidade, pontos fortes/fracos, orientação,
    # critério específico), não é um agente ReAct de propósito aberto.
    if resposta.tool_calls:
        mensagens_tool = []
        for chamada in resposta.tool_calls:
            trace("chat", "tool_call", tool=chamada["name"], args=chamada["args"])
            ferramenta = ferramentas_por_nome.get(chamada["name"])
            resultado_tool = ferramenta.invoke(chamada["args"]) if ferramenta else ""
            mensagens_tool.append(ToolMessage(content=resultado_tool, tool_call_id=chamada["id"]))

        resposta = llm_com_tools.invoke([*historico, resposta, *mensagens_tool])
        _trace_uso(resposta)

    return {"messages": state["messages"] + [pergunta, AIMessage(content=resposta.content)]}


graph = StateGraph(ChatState)
graph.add_node("load_session", load_session_node)
graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)

graph.add_edge(START, "load_session")
graph.add_edge("load_session", "retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)

chat_graph = graph.compile()