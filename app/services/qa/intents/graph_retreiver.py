from typing import Optional, Any
from ...qa.generic import GenericRetrievalService
from ....services.llm import precise_llm
from ....services.llm.chains import cyper_qa_chain, cypher_generation_chain
from langchain.callbacks.manager import AsyncCallbackManagerForChainRun
from app.db.graphdb import database, graph_driver
from neo4j import Driver
import neo4j


node_properties_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
RETURN {labels: nodeLabels, properties: properties} AS output
"""

rel_properties_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "relationship"
WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
RETURN {type: nodeLabels, properties: properties} AS output
"""

rel_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE type = "RELATIONSHIP" AND elementType = "node"
RETURN "(:" + label + ")-[:" + property + "]->(:" + toString(other[0]) + ")" AS output
"""


class GraphRetrievalService(GenericRetrievalService):
    """
    Sepereate class from the langchain instance becase we need to seperate
    """
    llm = precise_llm
    manager: AsyncCallbackManagerForChainRun = AsyncCallbackManagerForChainRun.get_noop_manager()

    def __init__(self, limit: Optional[int] = None):
        super().__init__()
        self._driver: Driver = graph_driver
        self._limit = limit
        self.schema = ""
        # Verify connection
        try:
            self._driver.verify_connectivity()
        except neo4j.exceptions.ServiceUnavailable:
            raise ValueError(
                "Could not connect to Neo4j database. "
                "Please ensure that the url is correct"
            )
        except neo4j.exceptions.AuthError:
            raise ValueError(
                "Could not connect to Neo4j database. "
                "Please ensure that the username and password are correct"
            )
        # Set schema
        try:
            self.refresh_schema()
        except neo4j.exceptions.ClientError:
            raise ValueError(
                "Could not use APOC procedures. "
                "Please install the APOC plugin in Neo4j."
            )
        self.callbacks = self.manager.get_child()
        self.verbose: bool = True

    @property
    def get_schema(self) -> str:
        """Returns the schema of the Neo4j database"""
        return self.schema

    def refresh_schema(self) -> None:
        """
        Refreshes the Neo4j graph schema information.
        """
        node_properties = self.query(node_properties_query)
        relationships_properties = self.query(rel_properties_query)
        relationships = self.query(rel_query)

        self.schema = f"""
        Node properties are the following:
        {[el['output'] for el in node_properties]}
        Relationship properties are the following:
        {[el['output'] for el in relationships_properties]}
        The relationships are the following:
        {[el['output'] for el in relationships]}
        """

    async def query(self, query: str, params: dict = {}) -> list[dict[str, Any]]:
        """Query Neo4j database."""
        from neo4j.exceptions import CypherSyntaxError

        with self._driver.session() as session:
            try:
                data = session.run(query, params)
                if self._limit is None:
                    return [r.data() for r in data]
                else:
                    return [r.data() for r in data][:self._limit]
            except CypherSyntaxError as e:
                raise ValueError("Generated Cypher Statement is not valid\n" f"{e}")

    async def run_query(self, question):
        generated_cypher: str = await cypher_generation_chain.arun(question=question, schema=self.get_schema,
                                                                   callbacks=self.callbacks, verbose=self.verbose)

        await self.manager.on_text("Generated Cypher:", end="\n", verbose=self.verbose)
        await self.manager.on_text(
            generated_cypher, color="green", end="\n", verbose=self.verbose
        )

        result = await self.query(generated_cypher)

        await self.manager.on_text("Full Context:", end="\n", verbose=self.verbose)
        await self.manager.on_text(
            result, color="green", end="\n", verbose=self.verbose
        )
        return result

    async def run_qa(self, question, context: Optional[list[dict[str, Any]]] = None):
        """
        Context is a cypher query.
        :param question:
        :param context:
        :return:
        """
        if context is None:
            context = await self.run_query(question)



        result = await cyper_qa_chain.arun(
            question=question, context=context
        )

        await self.manager.on_text("Full Context:", end="\n", verbose=self.verbose)
        await self.manager.on_text(
            context, color="green", end="\n", verbose=self.verbose
        )
        return result[cyper_qa_chain.output_key]

    @classmethod
    async def run(cls, query: str, **kwargs: Any) -> str:
        pass
