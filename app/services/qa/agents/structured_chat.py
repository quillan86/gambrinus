from typing import Optional
from ....services.llm import agent_chat_llm
from ....services.llm.templates.system import STRUCTURED_CHAT_PREFIX
from .generic import AgentService
from langchain.agents import AgentType
from langchain.schema import BaseMessage


class StructuredChatAgentService(AgentService):

    def __init__(self, chat_history: Optional[list[BaseMessage]] = None, max_iterations: int = 2,
                 user_id: Optional[int] = None):

        agent_kwargs: dict = {
            "prefix": STRUCTURED_CHAT_PREFIX
        }
        agent: AgentType = AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION
        llm = agent_chat_llm

        super().__init__(llm, agent=agent, chat_history=chat_history, max_iterations=max_iterations,
                         agent_kwargs=agent_kwargs, memory_key="memory_prompts")