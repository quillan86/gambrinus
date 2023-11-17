from typing import Optional, Any
from ....services.qa.generic import GenericRetrievalService
import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
from ....db.graphdb import graph_driver
from ....services.llm.chains import beer_entity_chain
from ....services.llm.templates.entity import beer_output_parser


class RecipeQueryService(GenericRetrievalService):
    driver = graph_driver

    def __init__(self):
        super().__init__()

    @classmethod
    async def fuzzy_match(cls, style, search_type):
        with cls.driver.session(database="neo4j") as session:
            query = """CALL db.index.fulltext.queryNodes($search_type, $style) YIELD node, score
            RETURN labels(node)[0] AS label, node.name AS name LIMIT 5
            """
            print(query)
            data = session.run(query, style=style, search_type=search_type)
            result = [r.data() for r in data]
            if len(result) > 0:
                result = result[0]
            else:
                result = None
            return result

    @classmethod
    async def prototypical_beer_style(cls, style: dict[str, str]) -> str:
        with cls.driver.session(database="neo4j") as session:
            if style['label'] == 'Class':
                query = """MATCH (:Class {name: $style})<--(:Style)<--(r:Recipe)
                RETURN r.name as name, r.og as OG, r.fg as FG, r.abv as ABV, r.ibu as IBU"""
            elif style['label'] == 'Style':
                query = """MATCH (:Style {name: $style})<--(r:Recipe)
                RETURN r.name as name, r.og as OG, r.fg as FG, r.abv as ABV, r.ibu as IBU"""
            print(query)
            data = session.run(query, style=style['name'])
            recipes = [r.data() for r in data]
        # put into dataframe
        recipes = pd.DataFrame(recipes)
        # get prototypical statistics
        prototypical = recipes.iloc[:, 1:].mean()
        M = recipes.iloc[:, 1:].values
        x = prototypical.values
        similarities = np.zeros((len(recipes)),)
        for i in range(len(recipes)):
            similarities[i] = 1.0 - cosine(M[i, :], x)
        most_similar_idx: float = similarities.argmax()
        recipe_name: str = recipes.iloc[most_similar_idx, 0]
        return recipe_name


    @classmethod
    async def query_recipe(cls, recipe: str) -> dict[str, list[dict]]:
        query = """MATCH (recipe:Recipe {name: $name})-[r1:INVOLVES]->(process:Process)-[t1:TYPE_OF]->(processtype:ProcessType)
        MATCH (recipe)-[r2:USES]->(ingredient:Ingredient)-[t2:TYPE_OF]->(ingredienttype:IngredientType)
        MATCH (ingredient)-[r6:USED_IN]->(process)
        MATCH (process)-[r5:PRODUCES]->(postcompound:ProductCompound)
        MATCH (ingredient)-[r3:CONTAINS]->(precompound:ReactantCompound)
        MATCH (precompound)-[r4:YIELDS|INHIBITS]->(postcompound)
        MATCH (postcompound)-[r7:CREATES]->(flavor:Flavor)-[t3:TYPE_OF]->(flavortype:FlavorType)
        RETURN COLLECT(DISTINCT recipe) AS recipes, COLLECT(DISTINCT process) AS processes, COLLECT(DISTINCT ingredient) AS ingredients, 
            COLLECT(DISTINCT precompound) AS precompounds, COLLECT(DISTINCT postcompound) AS postcompounds,
            COLLECT(DISTINCT flavor) AS flavors,
            COLLECT(DISTINCT processtype) AS processtypes, COLLECT(DISTINCT ingredienttype) AS ingredienttypes,
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
        with cls.driver.session(database="neo4j") as session:
            data = session.run(query, name=recipe)
            data: dict[str, list[dict]] = [r.data() for r in data][0]
        return data

    @classmethod
    async def run(cls, query: str,
                  **kwargs: Any) -> dict[str, list[dict]]:

        entities = beer_entity_chain.run(query)
        entities = beer_output_parser.parse(entities)['entities']
        styles = [x['name'] for x in entities if x['type'] == 'style']
        recipes = [x['name'] for x in entities if x['type'] == 'recipe']
        if len(styles) > 0:
            style = await cls.fuzzy_match(styles[0], "styles")
            recipe = await cls.prototypical_beer_style(style)
        elif len(recipes) > 0:
            recipe = await cls.fuzzy_match(recipes[0], "recipes")
        else:
            recipe = ''
        result = await cls.query_recipe(recipe)
        return result
