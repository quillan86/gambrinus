from typing import Any
from ....services.llm import irrelevant_chain
from ...qa.generic import GenericRetrievalService
from langchain.callbacks.manager import AsyncCallbackManagerForChainRun


class IrrelevantAnswerService(GenericRetrievalService):
    chain = irrelevant_chain
    manager: AsyncCallbackManagerForChainRun = AsyncCallbackManagerForChainRun.get_noop_manager()

    def __init__(self):
        super().__init__()

    @classmethod
    async def run(cls, query: str, **kwargs: Any) -> str:
        callbacks = cls.manager.get_child()
        result = await cls.chain.arun(question=query, callbacks=callbacks)
        await cls.manager.on_text("Generated Answer:", end="\n", verbose=True)
        await cls.manager.on_text(result, color="green", end="\n", verbose=True)
        return result
