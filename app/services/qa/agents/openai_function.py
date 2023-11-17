from typing import Optional
from ....services.llm import agent_chat_llm
from ....services.llm.templates.system import SYSTEM_PROMPT, SYSTEM_PROMPT_TEMPLATE
from .generic import AgentService
from langchain.agents import AgentType
from langchain.schema import BaseMessage
from ....db.sqldb.services import user_service


class OpenAIFunctionAgentService(AgentService):

    def __init__(self, chat_history: Optional[list[BaseMessage]] = None, max_iterations: int = 2,
                 user_id: Optional[int] = None):
        system_prompt = self.prep_system_prompt(user_id)
        agent_kwargs = {
            "system_message": system_prompt,
        }
        agent: AgentType = AgentType.OPENAI_FUNCTIONS
        llm = agent_chat_llm

        super().__init__(llm, agent=agent, chat_history=chat_history, max_iterations=max_iterations,
                         agent_kwargs=agent_kwargs, memory_key="extra_prompt_messages")

    def prep_system_prompt(self, user_id: Optional[int]):
        if user_id is None:
            return SYSTEM_PROMPT
        user = user_service.get_by_id(user_id)
        user_name = ""
        if user.first_name is not None:
            user_name += user.first_name
        if user.last_name is not None:
            if user.first_name is not None:
                user_name += " "
            user_name += user.last_name
        if user.title is not None:
            job_title = user.title
        else:
            job_title = ""
        client = user_service.get_client_by_id(user_id)
        if client is not None:
            company = client.name
            company_description = client.description
        else:
            company, company_description = "", ""
        custom_messages = user_service.get_custom_messages(user_id)
        user_knowledge = ""
        for custom_message in custom_messages:
            prompt = custom_message.get('prompt', None)
            answer = custom_message.get('message', None).strip()
            if prompt is None or answer is None:
                pass
            else:
                user_knowledge += f"- {prompt}: {answer}\n"
        result = SYSTEM_PROMPT_TEMPLATE.format(user_name=user_name,
                                               job_title=job_title,
                                               company=company,
                                               company_description=company_description,
                                               user_knowledge=user_knowledge)
        return result
