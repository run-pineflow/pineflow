from typing import Any, Dict, List

from pineflow.core.llms import BaseLLM, ChatMessage, ChatResponse, GenerateResponse
from pydantic import Field

import litellm


class LiteLLM(BaseLLM):
    model: str
    temperature: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="The temperature to use. Higher values make the output more random, "
        "while lower values make it more focused and deterministic.",
    )
    max_tokens: int = Field(ge=0)
    api_key: str
    additional_kwargs: Dict[str, Any] = Field(default_factory=Dict)

    def _get_all_kwargs(self, **kwargs: Any) -> Dict[str, any]:
        return {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **self.additional_kwargs,
            **kwargs,
            "model": self.model,  # always enforced from class
            "api_key": self.api_key,  # always enforced from class
        }

    def completion(self, prompt: str, **kwargs: Any) -> GenerateResponse:
        """Generates a chat completion for LLM."""
        all_kwargs = self._get_all_kwargs(**kwargs)

        response = litellm.text_completion(prompt=prompt, **all_kwargs).model_dump()

        return GenerateResponse(
            text=response["choices"][0]["text"],
            raw=response,
        )

    def text_completion(self, prompt: str, **kwargs: Any) -> str:
        """Generates a chat completion for LLM."""
        all_kwargs = self._get_all_kwargs(**kwargs)

        response = litellm.text_completion(prompt=prompt, **all_kwargs).model_dump()

        return response["choices"][0]["text"]

    def chat_completion(
        self, messages: List[ChatMessage], **kwargs: Any
    ) -> ChatResponse:
        """Generates a chat completion for LLM."""
        all_kwargs = self._get_all_kwargs(**kwargs)
        input_messages_dict = self.convert_chat_messages(messages)

        response = litellm.completion(
            messages=input_messages_dict, **all_kwargs
        ).model_dump()
        message_dict = response["choices"][0]["message"]

        return ChatResponse(
            message=ChatMessage(
                role=message_dict.get("role"), content=message_dict.get("content", None)
            ),
            raw=response,
        )
