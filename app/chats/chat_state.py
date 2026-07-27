from typing import Optional, TypedDict
from langchain_core.messages import BaseMessage

from app.schemas.validation_result import ValidationResult


class ChatState(TypedDict):
    session_id: str
    question: str
    messages: list[BaseMessage]
    retrieved_context: Optional[list[str]]
    validation: Optional[ValidationResult]
