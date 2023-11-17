from typing import Optional, Any
from ....services.qa.generic import GenericRetrievalService


class SEMChainService(GenericRetrievalService):

    def __init__(self):
        super().__init__()

    @classmethod
    async def run(cls, query: str, intent: Optional[str] = None, chat_history: Optional[list[dict[str, str]]] = None, **kwargs: Any) -> str:
        answer: str = query
        return answer
