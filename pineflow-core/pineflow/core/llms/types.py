from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"
    TOOL = "tool"


class ChatMessage(BaseModel):
    """Chat message."""

    role: MessageRole = Field(default=MessageRole.USER)
    content: Optional[str] = Field(default=None)

    model_config = {"use_enum_values": True}


class GenerateResponse(BaseModel):
    """Generate response."""

    text: str = Field(..., description="Generated text response")
    raw: Optional[Any] = Field(default=None)


class ChatResponse(BaseModel):
    """Chat completion response."""

    message: ChatMessage
    raw: Optional[Any] = None
