from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
import numpy as np
import pandas as pd
import json
import time
from typing import Optional, Type
from scipy.spatial.distance import cosine
from ....db.graphdb import create_graph_driver


class RecipeFinderInput(BaseModel):
    query: str = Field(..., description="should be the name of a beer, beer style, beer ingredient, or beer category")
    type: str = Field(..., description="The type of thing the query is about", enum=["beer_style", "beer_recipe", "beer_ingredient"])


class RecipeFinder(BaseTool):
    """Tool for the RecipeFinder chain."""
    name: str = "recipe_finder"
    description: str = ("Useful for when you need to find a beer recipe, properties about a beer recipe, "
                        "or a representative beer recipe of a particular beer style or class. "
                        "If you successfully find a recipe, assume that it is the recipe that you want. "
                        "Only use this tool when explicitly asked."
                        "Input should be a name of a beer recipe, beer style, or beer category. "
                        "Output is a json serialized dictionary."
                        )
    args_schema: Type[RecipeFinderInput] = RecipeFinderInput

    def fuzzy_match(self, style, search_type):
        graph_driver = create_graph_driver()
        try:
            with graph_driver.session(database="neo4j") as session:
                query = """CALL db.index.fulltext.queryNodes($search_type, $style) YIELD node, score
                RETURN ID(node) as id, labels(node)[0] AS label, node.name AS name LIMIT 5
                """
                print(query)
                data = session.run(query, style=style, search_type=search_type)
                result = [r.data() for r in data]
                if len(result) > 0:
                    result = result[0]
                else:
                    result = None
                return result
        except:
            graph_driver.close()
            graph_driver = create_graph_driver()
            time.sleep(2)

    def prototypical_beer_style(self, style: dict[str, str]) -> tuple[int, str]:
        graph_driver = create_graph_driver()
        try:
            with graph_driver.session(database="neo4j") as session:
                if style['label'] == 'Class':
                    query = """MATCH (:Class {name: $style})<--(:Style)<--(r:Recipe)
                    RETURN ID(r) as id, r.name as name, r.og as OG, r.fg as FG, r.abv as ABV, r.ibu as IBU"""
                elif style['label'] == 'Style':
                    query = """MATCH (:Style {name: $style})<--(r:Recipe)
                    RETURN ID(r) as id, r.name as name, r.og as OG, r.fg as FG, r.abv as ABV, r.ibu as IBU"""
                print(query)
                data = session.run(query, style=style['name'])
                recipes = [r.data() for r in data]
        except:
            graph_driver.close()
            graph_driver = create_graph_driver()
            time.sleep(2)
        # put into dataframe n
        recipes = pd.DataFrame(recipes)
        # get prototypical statistics
        prototypical = recipes.iloc[:, 2:].mean()
        M = recipes.iloc[:, 2:].values
        x = prototypical.values
        similarities = np.zeros((len(recipes)),)
        for i in range(len(recipes)):
            similarities[i] = 1.0 - cosine(M[i, :], x)
        most_similar_idx: float = similarities.argmax()
        recipe_id: int = recipes.iloc[most_similar_idx, 0]
        recipe_name: str = recipes.iloc[most_similar_idx, 1]
        print(f"Recipe: {recipe_name}, ID: {recipe_id}")
        return recipe_id, recipe_name

    def prototypical_ingredient_recipe(self, ingredient: dict[str, str]):
        graph_driver = create_graph_driver()
        try:
            with graph_driver.session(database="neo4j") as session:
                query = """MATCH (ingredient:Ingredient) WHERE ID(ingredient) = $ingredient_id
                MATCH (r:Recipe)-[USES]->(ingredient)
                RETURN ID(r) as id, r.name as name, r.og as OG, r.fg as FG, r.abv as ABV, r.ibu as IBU"""
                print(query)
                data = session.run(query, ingredient_id=ingredient['id'])
                recipes = [r.data() for r in data]
        except:
            graph_driver.close()
            graph_driver = create_graph_driver()
            time.sleep(2)
        # put into dataframe
        recipes = pd.DataFrame(recipes)
        # get prototypical statistics
        prototypical = recipes.iloc[:, 2:].mean()
        M = recipes.iloc[:, 2:].values
        x = prototypical.values
        similarities = np.zeros((len(recipes)),)
        for i in range(len(recipes)):
            similarities[i] = 1.0 - cosine(M[i, :], x)
        most_similar_idx: float = similarities.argmax()
        recipe_id: int = recipes.iloc[most_similar_idx, 0]
        recipe_name: str = recipes.iloc[most_similar_idx, 1]
        print(f"Recipe: {recipe_name}, ID: {recipe_id}")
        return recipe_id, recipe_name

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
        RETURN COLLECT(DISTINCT recipe) AS recipes, COLLECT(DISTINCT process) AS processes, COLLECT(DISTINCT ingredient) AS ingredients, 
            COLLECT(DISTINCT precompound) AS precompounds, COLLECT(DISTINCT postcompound) AS postcompounds,
            COLLECT(DISTINCT processtype) AS processtypes, COLLECT(DISTINCT ingredienttype) AS ingredienttypes,
            COLLECT(DISTINCT {type: type(r1), properties: properties(r1), start: startNode(r1), end: endNode(r1)}) AS r1_edges,
            COLLECT(DISTINCT {type: type(r2), properties: properties(r2), start: startNode(r2), end: endNode(r2)}) AS r2_edges,
            COLLECT(DISTINCT {type: type(r3), properties: properties(r3), start: startNode(r3), end: endNode(r3)}) AS r3_edges,
            COLLECT(DISTINCT {type: type(r4), properties: properties(r4), start: startNode(r4), end: endNode(r4)}) AS r4_edges,
            COLLECT(DISTINCT {type: type(r5), properties: properties(r5), start: startNode(r5), end: endNode(r5)}) AS r5_edges,
            COLLECT(DISTINCT {type: type(r6), properties: properties(r6), start: startNode(r6), end: endNode(r6)}) AS r6_edges,
            COLLECT(DISTINCT {type: type(t1), properties: properties(t1), start: startNode(t1), end: endNode(t1)}) AS t1_edges,
            COLLECT(DISTINCT {type: type(t2), properties: properties(t2), start: startNode(t2), end: endNode(t2)}) AS t2_edges
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

    def trim_query(self, query: dict):
        result = {}
        if len(query) == 0:
            return {}
        for key in ["recipes", "processes", "ingredients", "precompounds", "postcompounds", "processtypes", "ingredienttypes",]:
            result[key] = []
            for node in query[key]:
                node_name = node['name']
                result[key].append(node_name)
        for key in ["r1_edges", "r2_edges", "r3_edges", "r4_edges", "r5_edges", "r6_edges", "t1_edges", "t2_edges"]:
            result[key] = []
            for edge in query[key]:
                edge_ = {"start": edge["start"]["name"],
                         "end": edge["end"]["name"],
                         "type": edge["type"]}
                result[key].append(edge_)
        return result

    def get_recipe_id(self, query: str, type: str) -> Optional[int]:
        if type == "beer_ingredient":
            ingredient = self.fuzzy_match(query, "ingredients")
            recipe_id, recipe_name = self.prototypical_ingredient_recipe(ingredient)
        elif type == "beer_style":
            # query style first then recipe
            style = self.fuzzy_match(query, "styles")
            if style is None:
                recipe = self.fuzzy_match(query, "recipes")
                if recipe is None:
                    return None
                recipe_id = recipe.get("id", None)
                if recipe_id is None:
                    return None
            else:
                recipe_id, recipe_name = self.prototypical_beer_style(style)
        elif type == 'beer_recipe':
            # query recipe first then style
            recipe = self.fuzzy_match(query, "recipes")
            if recipe is None:
                style = self.fuzzy_match(query, "styles")
                if style is None:
                    return None
                recipe_id, recipe_name = self.prototypical_beer_style(style)
            else:
                recipe_id = recipe.get("id", None)
        else:
            # null result
            recipe_id = None
        return recipe_id

    def _run(
        self,
        query: str,
        type: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        recipe_id = self.get_recipe_id(query, type)
        result = self.query_recipe(recipe_id)
        result = self.trim_query(result)
        return json.dumps(result)

    async def _arun(
        self,
        query: str,
        type: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("RecipeFinder does not support async")


recipe_finder_tool = RecipeFinder()
