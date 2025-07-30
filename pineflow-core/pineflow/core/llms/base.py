from abc import ABC, abstractmethod
from typing import Any, List, Optional

from pineflow.core.llms.types import ChatMessage, ChatResponse, GenerateResponse
from pineflow.core.monitors import BaseMonitor
from pydantic import BaseModel


class BaseLLM(ABC, BaseModel):
    """An interface for LLMs."""

    model_config = {"arbitrary_types_allowed": True}
    callback_manager: Optional[BaseMonitor] = None

    @classmethod
    def class_name(cls) -> str:
        return "BaseLLM"

    def convert_chat_messages(self, messages: List[ChatMessage]) -> List[dict]:
        """Convert chat messages to LLM message format."""
        return [message.model_dump() for message in messages]

    @abstractmethod
    def completion(self, prompt: str, **kwargs: Any) -> GenerateResponse:
        """Generates a completion for LLM."""

    @abstractmethod
    def text_completion(self, prompt: str, **kwargs: Any) -> str:
        """Generates a text completion for LLM."""

    @abstractmethod
    def chat_completion(
        self, messages: List[ChatMessage], **kwargs: Any
    ) -> ChatResponse:
        """Generates a chat completion for LLM."""
