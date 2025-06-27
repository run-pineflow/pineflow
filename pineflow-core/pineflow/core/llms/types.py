from enum import Enum
from typing import Any, Optional

from pydantic.v1 import BaseModel


class MessageRole(str, Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"
    TOOL = "tool"


class ChatMessage(BaseModel):
    """Chat message."""

    role: MessageRole = MessageRole.USER
    content: Optional[str]

    def __str__(self):
        return f"{self.role}: {self.content}"


class GenerateResponse(BaseModel):
    """Generate response."""

    text: str
    raw: Optional[Any] = None

    def __str__(self) -> str:
        return self.text


class ChatResponse(BaseModel):
    """Chat completion response."""

    message: ChatMessage
    raw: Optional[Any] = None

    def __str__(self) -> str:
        return self.message
