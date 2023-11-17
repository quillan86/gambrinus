from typing import Optional, Any
from ..generic import GenericChatService
from langchain.schema.language_model import BaseLanguageModel
from ..tools import tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.schema import BaseMessage
import json
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory


class AgentService(GenericChatService):

    def __init__(self, llm: BaseLanguageModel, agent: AgentType = AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                 chat_history: Optional[list[BaseMessage]] = None, max_iterations: int = 2, agent_kwargs: dict = {},
                 memory_key: str = "memory_prompts"):

        self.llm = llm
        self.tools = tools
        chat_memory_history = ChatMessageHistory()
        for message in chat_history:
            chat_memory_history.add_message(message)

        self.max_iterations = max_iterations
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True,
                                               chat_memory=chat_memory_history, output_key="output")
        agent_kwargs[memory_key] = chat_history
        self.agent_chain = initialize_agent(tools,
                                            llm,
                                            agent=agent,
                                            verbose=True,
                                            return_intermediate_steps=True,
                                            max_iterations=self.max_iterations,
                                            early_stopping_method="generate",
                                            agent_kwargs=agent_kwargs,
                                            memory=self.memory
                                            )
        super().__init__(llm=llm)

    def get_internal_sources(self, response: dict) -> list[str]:
        """
        Get the sources extracted from internal tools that return them.
        Tools with sources:
            - Beer Knowledge
        :param response:
        :return:
        """
        sources = []
        for step in response['intermediate_steps']:
            if (step[0].tool == "brewing_knowledge"):
                data = json.loads(step[1])
                if "sources" in data.keys():
                    if not "i don't know" in data['answer'].lower():
                        sources += data["sources"]

        sources = set(sources)
        for nan in ["None", "N/A", ""]:
            sources.discard(nan)
        sources = list(sources)
        return sources

    def get_external_sources(self, response: dict) -> list[str]:
        """
        Get the sources extracted from tools that return them.
        Tools with sources:
            - Wikipedia
        :param response:
        :return:
        """
        sources = []
        for step in response['intermediate_steps']:
            if (step[0].tool == "wikipedia") or (step[0].tool == "pubmed"):
                data = json.loads(step[1])
                if "sources" in data.keys():
                    if not "i don't know" in data['answer'].lower():
                        sources += data["sources"]

        sources = set(sources)
        for nan in ["None", "N/A", ""]:
            sources.discard(nan)
        sources = list(sources)
        return sources

    def get_flavors(self, response: dict) -> list[dict]:
        flavors = []
        for step in response['intermediate_steps']:
            if step[0].tool == "flavor_profiler":
                data = json.loads(step[1])
                flavor = {}
                if "unnormalized_flavor_profile" in data.keys():
                    flavor['Unnormalized Flavor Profile'] = data["unnormalized_flavor_profile"]
                if "normalized_flavor_profile" in data.keys():
                    flavor['Normalized Flavor Profile'] = data["normalized_flavor_profile"]
                if flavor is not None:
                    flavor['Name'] = data.get("name")
                    flavors.append(flavor)
        return flavors

    def get_recipes(self, response: dict) -> list[str]:
        recipes = []
        for step in response['intermediate_steps']:
            if step[0].tool == "recipe_finder":
                data = json.loads(step[1])
                datum = data.get('recipes', [])
                if len(datum) > 0:
                    recipes.extend(datum)
        return recipes

    def add_sources(self, internal_sources: list[str], external_sources: list[str],
                    flavors: list[dict],
                    recipes: list[str]) -> Optional[str]:
        result = None
        if len(internal_sources) > 0:
            if result is None:
                result = ""
            else:
                result += "\n"
            # Sources Searched is more accurate than Sources
            # until we have the ability to filter out irrelevant sources.
            result += f"Internal Sources Searched:\n{', '.join(internal_sources)}"
        if len(external_sources) > 0:
            if result is None:
                result = ""
            else:
                result += "\n"
            # Sources Searched is more accurate than Sources
            # until we have the ability to filter out irrelevant sources.
            result += f"External Sources Searched:\n{', '.join(external_sources)}"
        if len(flavors) > 0:
            if result is None:
                result = ""
            else:
                result += "\n"
            result += "Flavor Profile:"
            for flavor in flavors:
                name = flavor.get("Name")
                profile1 = flavor['Normalized Flavor Profile']
                profile2 = flavor['Unnormalized Flavor Profile']
                if not (('taste' not in profile1) or ('taste' not in profile2)):
                    flavor_source = f"\nBeer Name: {name}\nTaste:\nBitterness: {profile1['taste']['bitter']}% | {profile2['taste']['bitter']} units\nSweetness: {profile1['taste']['sweet']}% | {profile2['taste']['sweet']} units\nOdor:\nAlcoholic: {profile1['odor']['alcoholic']}% | {profile2['odor']['alcoholic']} units\nTexture:\nWarming: {profile1['texture']['warming']}% | {profile2['texture']['warming']} units"
                    result += flavor_source
        if len(recipes) > 0:
            if result is None:
                result = ""
            else:
                result += "\n"
            result += f"Recipes Searched:\n{', '.join(recipes)}"
        return result

    def get_tools(self, response):
        result = []
        for step in response['intermediate_steps']:
            d = {}
            d['tool'] = step[0].tool
            d['input'] = step[0].tool_input
            d['output'] = json.loads(step[1])
            result.append(d)
        return result

    def get_intent(self, tools):
        if len(tools) == 0:
            result = 'generated'
        else:
            result = 'function'
        return result

    def run(self, query: str, **kwargs: Any) -> dict:
        response = self.agent_chain({"input": query})

        internal_sources = self.get_internal_sources(response)
        external_sources = self.get_external_sources(response)
        flavors = self.get_flavors(response)
        recipes = self.get_recipes(response)

        tools = self.get_tools(response)
        intent = self.get_intent(tools)

        sources = self.add_sources(internal_sources, external_sources, flavors, recipes)


        result = {
            'response': response['output'],
            'sources': sources,
            'tools': tools,
            'intent': intent
        }
        return result
