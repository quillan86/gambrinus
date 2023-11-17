from typing import Optional, Any
from .generic import GenericRetrievalService
from .qachain import QAChainService
from .formatter import FormattingService
from .answerchain import AnswerChainService
from langchain.schema import BaseMessage


class IntentRetrievalService(GenericRetrievalService):

    @classmethod
    async def run(cls, query: str, intent: Optional[str] = None, chat_history: Optional[list[BaseMessage]] = None, **kwargs: Any) -> str:
        # QA Chain
        qa, context = await QAChainService.run(query, intent=intent, chat_history=chat_history)
#        if intent in cls.keys.sem_intents:
#            intermediate: str = await SEMChainService.run(query, intent=intent, chat_history=chat_history)
#        else:
        intermediate: str = qa
        answer: str = await AnswerChainService.run(intermediate, context, intent=intent, chat_history=chat_history)
        result: str = await FormattingService.run(answer, intent=intent)
        return result

