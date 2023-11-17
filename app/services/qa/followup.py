from typing import Optional, Any
from .generic import GenericRetrievalService
from ..llm.chains import flavor_profile_description_chain
import json
from ..llm.chains import followup_chain
from ..llm.templates.followup import followup_output_parser
from langchain.schema.messages import get_buffer_string, BaseMessage
import traceback


class FollowupService(GenericRetrievalService):

    @classmethod
    async def run(cls, chat_history: list[BaseMessage], **kwargs: Any) -> list[str]:
        # get last six messages
        chat_history = chat_history[-6:]
        conversation: str = get_buffer_string(
                chat_history,
                human_prefix="Human",
                ai_prefix="Assistant",
            )
        try:
            followups = await followup_chain.arun(conversation)
            followups: list[dict] = followup_output_parser.parse(followups)
            followups = followups.get("prompts", [])
            if len(followups) > 0:
                followups = followups
                followups: list[str] = [x.get('prompt') for x in followups]
            if "null" in followups:
                followups.remove("null")
        except Exception:
            print(traceback.print_exc())
            followups: list[str] = []
        return followups
