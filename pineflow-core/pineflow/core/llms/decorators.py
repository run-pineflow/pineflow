import time
from typing import Callable

from pineflow.core.llms.types import ChatMessage


def llm_chat_handler() -> Callable:
    """
    Decorator to wrap a method with llm handler logic.
    Looks for monitors instances in `self.monitor_manager`.
    """
    def decorator(f: Callable) -> Callable:
        def wrapper(self, *args, **kwargs):
            monitor_manager_fns = getattr(self, "monitor_manager", None)
            
            start_time = time.time()
            llm_return_val = f(self, *args, **kwargs)
            response_time = int((time.time() - start_time) * 1000)
            
            if monitor_manager_fns:
                # Extract input messages
                if len(args) > 0 and isinstance(args[0], ChatMessage):
                    input_chat_messages = args[0]
                elif "messages" in kwargs:
                    input_chat_messages = kwargs['messages']
                else:
                    raise ValueError("No messages provided in positional or keyword arguments")
                
                # Log the user's latest message after each interaction to chat monitoring.
                user_messages = [msg for msg in input_chat_messages if msg.role == 'user']
                last_user_message = user_messages[-1].content if user_messages else None
                
                monitor_manager_fns(
                    payload={
                        "input_query": last_user_message,
                        "generated_text": llm_return_val.message.content,
                        "generated_token_count": llm_return_val.raw["usage"]["completion_tokens"],
                        "input_token_count": llm_return_val.raw["usage"]["prompt_tokens"],
                        "response_time": response_time,
                    })
                
            return llm_return_val
                
        return wrapper
    return decorator
    
