from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["human", "ai"]
    content: str


class ChatRequest(BaseModel):
    question: str
    messages: list[ChatMessage] = []


class ChatResponse(BaseModel):
    answer: str
    messages: list[ChatMessage]
