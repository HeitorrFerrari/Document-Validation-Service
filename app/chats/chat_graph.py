from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from app.core.tracing import trace
from app.rag.retriever import retrieve
from app.chats.chat_state import ChatState

_llm = ChatOpenAI(model="gpt-4o-mini")

def retrieve_node(state: ChatState) -> dict:
    trace("chat", "retrieve_node", session_id=state["session_id"], question=state["question"])
    chunks = retrieve(state["session_id"], state["question"])
    return {"retrieved_context": chunks}


def generate_node(state: ChatState) -> dict:
    contexto = "\n".join(state["retrieved_context"])
    trace(
        "chat", "generate_node",
        session_id=state["session_id"],
        context_chunks=len(state["retrieved_context"]),
        history_messages=len(state["messages"]),
    )

    system = SystemMessage(
        content=(
            "Você explica e debate a nota de validação de um currículo. "
            f"Use somente este contexto para responder:\n{contexto}"
        )
    )
    pergunta = HumanMessage(content=state["question"])
    resposta = _llm.invoke([system, *state["messages"], pergunta])

    uso = resposta.usage_metadata or {}
    trace(
        "llm", "usage",
        model="gpt-4o-mini",
        input_tokens=uso.get("input_tokens"),
        output_tokens=uso.get("output_tokens"),
        total_tokens=uso.get("total_tokens"),
    )

    return {"messages": state["messages"] + [pergunta, AIMessage(content=resposta.content)]}


graph = StateGraph(ChatState)
graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)

graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)

chat_graph = graph.compile()