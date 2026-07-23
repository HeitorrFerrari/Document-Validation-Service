from typing import Optional, TypedDict
from langchain_core.messages import BaseMessage


class ChatState(TypedDict):
    sessionId: str
    question: str
    messages: list[BaseMessage]
    retrieved_context: Optional[list[str]]
