from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
import json
from typing import Optional, Type
from .recipe_finder import recipe_finder_tool
from ..intents.flavor_algorithm import FlavorAlgorithmService
from ...llm.chains import flavor_profile_description_chain
from ....db.graphdb import create_graph_driver
import time


class FlavorProfilerInput(BaseModel):
    query: str = Field(..., description="Should be the name of a beer, beer style, or beer category. Should NOT be an ingredient.")
    type: str = Field(..., description="The type of thing the query is about", enum=["beer_style", "beer_recipe"])
    method: str = Field(..., description="Methodology for using the flavor profiler - identify the flavor profile, substitute ingredients,"
                                         "or adjust a recipe.",
                        enum=["identify_flavor", "adjust_recipe", "substitute_ingredient", "add_ingredient", "remove_ingredient"])
    ingredient: Optional[str] = Field(description="Ingredient to add, remove, or substitute when called for")


class FlavorProfiler(BaseTool):
    """Tool for the FlavorProfiler chain."""
    name: str = "flavor_profiler"
    description: str = ("Useful for when you need to identify and adjust the ingredients for the taste "
                        "and aroma of beer. This comes out with a natural language response describing the flavor "
                        "of a beer based on an algorithm for the perception of different flavors. "
                        "Use this for your Flavor Profiling capability. "
                        "Input should be a name of a beer recipe, beer style, or beer category. "
                        )
    args_schema: Type[FlavorProfilerInput] = FlavorProfilerInput

    def prep_flavor_profile(self, result, context) -> str:
        profile1 = context['Normalized Flavor Profile']
        profile2 = context['Unnormalized Flavor Profile']
        source = f"Flavor Profile:\nTaste:\nBitterness: {profile1['taste']['bitter']}% | {profile2['taste']['bitter']} units\nSweetness: {profile1['taste']['sweet']}% | {profile2['taste']['sweet']} units\nOdor:\nAlcoholic: {profile1['odor']['alcoholic']}% | {profile2['odor']['alcoholic']} units\nTexture:\nWarming: {profile1['texture']['warming']}% | {profile2['texture']['warming']} units"
        answer = result['text'] + '\n'
        answer += source
        return answer

    def query_recipe(self, recipe_id: Optional[int]) -> dict[str, list[dict]]:
        if recipe_id is None:
            return {}
        graph_driver = create_graph_driver()
        query = """MATCH (recipe:Recipe) WHERE ID(recipe) = $recipe_id
        MATCH (recipe)-[r1:INVOLVES]->(process:Process)-[t1:TYPE_OF]->(processtype:ProcessType)
        MATCH (recipe)-[r2:USES]->(ingredient:Ingredient)-[t2:TYPE_OF]->(ingredienttype:IngredientType)
        MATCH (ingredient)-[r6:USED_IN]->(process)
        MATCH (process)-[r5:PRODUCES]->(postcompound:ProductCompound)
        MATCH (ingredient)-[r3:CONTAINS]->(precompound:ReactantCompound)
        MATCH (precompound)-[r4:YIELDS|INHIBITS]->(postcompound)
        MATCH (postcompound)-[r7:CREATES]->(flavor:Flavor)-[t3:TYPE_OF]->(flavortype:FlavorType)
        RETURN COLLECT(DISTINCT recipe) AS recipes, COLLECT(DISTINCT process) AS processes, COLLECT(DISTINCT ingredient) AS ingredients, 
            COLLECT(DISTINCT precompound) AS precompounds, COLLECT(DISTINCT postcompound) AS postcompounds,
            COLLECT(DISTINCT processtype) AS processtypes, COLLECT(DISTINCT ingredienttype) AS ingredienttypes,
            COLLECT(DISTINCT flavor) AS flavors,
            COLLECT(DISTINCT flavortype) AS flavortypes,
            COLLECT(DISTINCT {type: type(r1), properties: properties(r1), start: startNode(r1), end: endNode(r1)}) AS r1_edges,
            COLLECT(DISTINCT {type: type(r2), properties: properties(r2), start: startNode(r2), end: endNode(r2)}) AS r2_edges,
            COLLECT(DISTINCT {type: type(r3), properties: properties(r3), start: startNode(r3), end: endNode(r3)}) AS r3_edges,
            COLLECT(DISTINCT {type: type(r4), properties: properties(r4), start: startNode(r4), end: endNode(r4)}) AS r4_edges,
            COLLECT(DISTINCT {type: type(r5), properties: properties(r5), start: startNode(r5), end: endNode(r5)}) AS r5_edges,
            COLLECT(DISTINCT {type: type(r6), properties: properties(r6), start: startNode(r6), end: endNode(r6)}) AS r6_edges,
            COLLECT(DISTINCT {type: type(r7), properties: properties(r7), start: startNode(r7), end: endNode(r7)}) AS r7_edges,            
            COLLECT(DISTINCT {type: type(t1), properties: properties(t1), start: startNode(t1), end: endNode(t1)}) AS t1_edges,
            COLLECT(DISTINCT {type: type(t2), properties: properties(t2), start: startNode(t2), end: endNode(t2)}) AS t2_edges,
            COLLECT(DISTINCT {type: type(t3), properties: properties(t3), start: startNode(t3), end: endNode(t3)}) AS t3_edges
        """
        print(query)
        data = {}
        try:
            with graph_driver.session(database="neo4j") as session:
                data = session.run(query, recipe_id=recipe_id)
                data: dict[str, list[dict]] = [r.data() for r in data][0]
        except:
            graph_driver.close()
            graph_driver = create_graph_driver()
            time.sleep(2)
        if not isinstance(data, dict):
            return {}
        return data

    def _run(
        self,
        query: str,
        type: str,
        method: str,
        ingredient: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        recipe_id = recipe_finder_tool.get_recipe_id(query, type)
        recipe = self.query_recipe(recipe_id)

        flavors = FlavorAlgorithmService.run(recipe)

        question = f"What is the flavor profile of the following beer: {query}?"

        result: dict = flavor_profile_description_chain({'question': question, 'context': json.dumps(flavors, indent=4)})

        return json.dumps({"answer": result["text"],
                           "name": flavors['Name of Beer'],
                           "unnormalized_flavor_profile": flavors['Unnormalized Flavor Profile'],
                           "normalized_flavor_profile": flavors['Normalized Flavor Profile']})

    async def _arun(
        self,
        query: str,
        type: str,
        method: str,
        ingredient: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("RecipeFinder does not support async")


flavor_profiler_tool = FlavorProfiler()
