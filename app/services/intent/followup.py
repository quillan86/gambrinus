from .generic import LLMClassifierService
from ..llm.chains import followup_chain
from langchain.schema import BaseMessage
import re


class FollowupClassifierService(LLMClassifierService):

    @classmethod
    async def classify(cls, query: str, chat_history: list[BaseMessage]):
        chat_history_ = chat_history[-2:]

        if len(chat_history_) < 2:
            # the only way this would happen is if it is the first response.
            # in that case, by definition, it is not a follow-up question.
            return 'off topic'

        result = await followup_chain.acall(
            {"old_question": chat_history_[0].content, "old_answer": chat_history_[1].content,
             "new_question": query}
        )
        result = result['text'].strip().lower()
        removelist = ' -'
        result = re.sub(r'[^\w'+removelist+']', '', result)
        return result

    @classmethod
    async def predict(cls, query: str, chat_history: list[BaseMessage]):
        result = cls.classify(query, chat_history)
        if result == 'off topic':
            return result, 0.0
        else:
            return result, 1.0


