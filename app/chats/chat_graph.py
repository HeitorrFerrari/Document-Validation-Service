from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from app.rag.retriever import retrieve
from app.chats.chat_state import ChatState

_llm = ChatOpenAI(model="gpt-4o-mini")

def retrieve_node(state: ChatState) -> dict:
    chunks = retrieve(state["session_id"], state["question"])
    return {"retrieved_context": chunks}