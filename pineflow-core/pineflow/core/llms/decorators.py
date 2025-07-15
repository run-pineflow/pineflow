import asyncio
import threading
import time
from logging import getLogger
from typing import Callable

from pineflow.core.llms.types import ChatMessage
from pineflow.core.observability.types import PayloadRecord

logger = getLogger(__name__)


def llm_chat_observer() -> Callable:
    """
    Decorator to wrap a method with llm handler logic.
    Looks for observability instances in `self.callback_manager`.
    """

    def decorator(f: Callable) -> Callable:
        def async_wrapper(self, *args, **kwargs):
            callback_manager_fns = getattr(self, "callback_manager", None)

            start_time = time.time()
            llm_return_val = f(self, *args, **kwargs)
            response_time = int((time.time() - start_time) * 1000)

            if callback_manager_fns:

                def async_callback_thread():
                    try:
                        # Extract input messages
                        if len(args) > 0 and isinstance(args[0], ChatMessage):
                            input_chat_messages = args[0]
                        elif "messages" in kwargs:
                            input_chat_messages = kwargs["messages"]
                        else:
                            raise ValueError(
                                "No messages provided in positional or keyword arguments"
                            )

                        # Get the user's latest message after each interaction to chat observability.
                        user_messages = [
                            msg for msg in input_chat_messages if msg.role == "user"
                        ]
                        last_user_message = (
                            user_messages[-1].content if user_messages else None
                        )

                        # Get the system/instruct (first) message to chat observability.
                        system_messages = [
                            msg for msg in input_chat_messages if msg.role == "system"
                        ]
                        system_message = (
                            system_messages[0].content if system_messages else None
                        )

                        callback = callback_manager_fns(
                            payload=PayloadRecord(
                                input_text=(system_message or "") + last_user_message,
                                generated_text=llm_return_val.message.content,
                                generated_token_count=llm_return_val.raw["usage"][
                                    "completion_tokens"
                                ],
                                input_token_count=llm_return_val.raw["usage"][
                                    "prompt_tokens"
                                ],
                                response_time=response_time,
                            )
                        )

                        if asyncio.iscoroutine(callback):
                            asyncio.run(callback)

                    except Exception as e:
                        logger.error(f"Observability callback error: {e}")

                threading.Thread(target=async_callback_thread).start()

            return llm_return_val

        return async_wrapper

    return decorator
