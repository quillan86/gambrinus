from typing import Optional, Any
from .generic import GenericRetrievalService
import json
from ..llm.chains import summary_chain
from ..llm.templates.summary import summary_output_parser
from langchain.schema.messages import get_buffer_string, BaseMessage


class SummaryService(GenericRetrievalService):

    @classmethod
    async def run(cls, chat_history: list[BaseMessage], **kwargs: Any) -> str:
        # get first ten messages
        chat_history = chat_history[:10]
        if len(chat_history) == 0:
            summary: str = "Conversation with Gambrinus"
            return summary
        conversation: str = get_buffer_string(
                chat_history,
                human_prefix="Human",
                ai_prefix="Assistant",
            )
        try:
            summary = await summary_chain.arun(conversation)
            summary = summary_output_parser.parse(summary)
            print(summary)
            summary = summary.get("conversation_info", {}).get("session", chat_history[0])
        except Exception:
            summary = chat_history[0].content
        return summary
