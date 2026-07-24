"""
Rota de chat (Fase 9): perguntas sobre uma sessão de validação já processada.
Sem checkpointer -- o histórico (`messages`) vai e volta no corpo da
requisição, o cliente é responsável por reenviar o que recebeu da resposta
anterior no próximo request.
"""
from fastapi import APIRouter
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from app.chats.chat_graph import chat_graph
from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


def _to_lc_message(msg: ChatMessage) -> BaseMessage:
    return HumanMessage(content=msg.content) if msg.role == "human" else AIMessage(content=msg.content)


def _to_chat_message(msg: BaseMessage) -> ChatMessage:
    role = "human" if isinstance(msg, HumanMessage) else "ai"
    return ChatMessage(role=role, content=msg.content)


@router.post("/{session_id}", response_model=ChatResponse)
async def chat(session_id: str, req: ChatRequest):
    resultado = chat_graph.invoke({
        "session_id": session_id,
        "question": req.question,
        "messages": [_to_lc_message(m) for m in req.messages],
        "retrieved_context": None,
    })

    mensagens = [_to_chat_message(m) for m in resultado["messages"]]
    return ChatResponse(answer=mensagens[-1].content, messages=mensagens)
