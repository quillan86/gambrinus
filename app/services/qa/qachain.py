from typing import Optional, Any
from .generic import GenericRetrievalService
from .intents.vector_retreiver import VectorRetrievalService
from .intents.recipe_queryer import RecipeQueryService
from .intents.flavor_algorithm import FlavorAlgorithmService


class QAChainService(GenericRetrievalService):
    vector_retreiver: VectorRetrievalService = VectorRetrievalService(5)
#    graph_retreiver: GraphRetrievalService = GraphRetrievalService()

    def __init__(self):
        super().__init__()

    @classmethod
    async def run(cls, query: str, intent: Optional[str] = None, chat_history: Optional[list[dict[str, str]]] = None, **kwargs: Any) -> tuple[str, dict]:
        if intent in cls.keys.vectordb_intents:
            answer = await cls.vector_retreiver.run_chain(query, chat_history)
            context = {}
        elif intent in cls.keys.unimplemented_intents:
            # unimplemented intents also use the vector database.
            answer = await cls.vector_retreiver.run_chain(query, chat_history)
            context = {}
        elif intent in cls.keys.flavor_intent:
            answer = query
            recipe = await RecipeQueryService.run(query)
            context = FlavorAlgorithmService.run(recipe)
        else:
            answer: str = f'This is a relevant intent - {intent}'
            context = {}
        return answer, context
