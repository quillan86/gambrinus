from typing import Optional, Any
from .generic import GenericRetrievalService


class FormattingService(GenericRetrievalService):
    llm = None

    @classmethod
    async def run(cls, query: str, intent: Optional[str] = None, **kwargs: Any) -> str:
        if intent in cls.keys.irrelevant_intent:
            return query.strip()
        else:
            result = query.strip()
            return result
