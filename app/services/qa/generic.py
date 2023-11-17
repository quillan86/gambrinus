from typing import Type, Optional, Any
from abc import ABC, abstractmethod
from langchain.base_language import BaseLanguageModel
# from ...db.cache import llm_cache
# from langchain import BaseCache
from .keys import RetrievalKeys, retrieval_keys


class GenericRetrievalService(ABC):
    llm: Optional[Type[BaseLanguageModel]] = None
#    llm_cache: Type[BaseCache] = llm_cache
    keys: RetrievalKeys = retrieval_keys

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    async def run(cls, query: str, **kwargs: Any) -> str:
        """
        Run the service given a query.
        :param query:
        :return:
        """
        pass


class GenericChatService(ABC):
    keys: RetrievalKeys = retrieval_keys

    def __init__(self, llm: Optional[BaseLanguageModel] = None):
        self.llm = llm


    @abstractmethod
    async def run(cls, query: str, **kwargs: Any) -> str:
        """
        Run the service given a query.
        :param query:
        :return:
        """
        pass