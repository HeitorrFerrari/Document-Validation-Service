from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from app.rag.retriever import retrieve
from app.chats.chat_state import ChatState

_llm = ChatOpenAI(model="gpt-4o-mini")

def retrieve_node(state: ChatState) -> dict:
    chunks = retrieve(state["session_id"], state["question"])
    return {"retrieved_context": chunks}


def generate_node(state: ChatState) -> dict:
    contexto = "\n".join(state["retrieved_context"])
    system = SystemMessage(
        content=(
            "Você explica e debate a nota de validação de um currículo. "
            f"Use somente este contexto para responder:\n{contexto}"
        )
    )
    pergunta = HumanMessage(content=state["question"])
    resposta = _llm.invoke([system, *state["messages"], pergunta])

    return {"messages": state["messages"] + [pergunta, AIMessage(content=resposta.content)]}


graph = StateGraph(ChatState)
graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)

graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)

chat_graph = graph.compile()