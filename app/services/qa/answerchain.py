from typing import Optional, Any
from .generic import GenericRetrievalService
from ..llm.chains import flavor_profile_description_chain
import json


class AnswerChainService(GenericRetrievalService):

    def __init__(self):
        super().__init__()


    @classmethod
    async def prep_flavor_profile(cls, result, context) -> str:
        profile1 = context['Normalized Flavor Profile']
        profile2 = context['Unnormalized Flavor Profile']
        source = f"Flavor Profile:\nTaste:\nBitterness: {profile1['taste']['bitter']}% | {profile2['taste']['bitter']} units\nSweetness: {profile1['taste']['sweet']}% | {profile2['taste']['sweet']} units\nOdor:\nAlcoholic: {profile1['odor']['alcoholic']}% | {profile2['odor']['alcoholic']} units\nTexture:\nWarming: {profile1['texture']['warming']}% | {profile2['texture']['warming']} units"
        answer = result['text'] + '\n'
        answer += source
        return answer

    @classmethod
    async def run(cls, query: str, context: dict, intent: Optional[str] = None, chat_history: Optional[list[dict[str, str]]] = None, **kwargs: Any) -> str:
        context_str = json.dumps(context, indent=4)
        if intent in cls.keys.flavor_intent:
            result: str = await flavor_profile_description_chain.acall({'question': query, 'context': context_str})
            answer = await cls.prep_flavor_profile(result, context)
        else:
            answer: str = query
        return answer
