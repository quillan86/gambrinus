from .models import precise_chat_llm, precise_chat_long_llm
from langchain.schema import (
    AIMessage,
    HumanMessage,
    BaseMessage
)

truncate_limit: int = 2750


def truncate_conversation(chat_history: list[BaseMessage]) -> list[BaseMessage]:
    """
    Truncate the conversation
    """

    while True:
        if (
                get_token_count(chat_history) > truncate_limit
                and len(chat_history) > 1
        ):
            # replace pop with pop(n) when system message
            chat_history.pop(0)
        else:
            break
    return chat_history


def get_token_count(chat_history: list[BaseMessage]) -> int:
    """
    Get token count
    """
    num_tokens = precise_chat_llm.get_num_tokens_from_messages(chat_history)
    return num_tokens
