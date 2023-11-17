from ....services.llm import precise_chat_long_llm
from langchain.chains import RetrievalQA
from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
import json
from typing import Optional, Type
from ....db.vectordb import knowledge_vector_store


beer_chain_type: str = "stuff"


class BeerKnowledgeInput(BaseModel):
    question: str = Field(..., description="should be a fully formed question")


class BeerKnowledge(BaseTool):
    """Tool for the Beer Knowledge Retriever"""
    name: str = "brewing_knowledge"
    description: str = ("This is the key source of information for all things beer. "
                        "From ingredients and brewing processes to beer regulations and general trivia, "
                        "it holds expert knowledge about every beer-related topic. "
                        "It is essential to invoke this function **FIRST AND FOREMOST** for any beer-related "
                        "queries. Aim to exploit the function's potential to its fullest in order to provide "
                        "the most accurate and comprehensive answers about beer. For Gambrinus to function "
                        "to its fullest potential, this tool is crucial and its usage should be prioritized "
                        "over any other methods of generating beer-related responses."
                       )
    k: int = 4
    vector_store = knowledge_vector_store
    llm = precise_chat_long_llm
    args_schema: Type[BeerKnowledgeInput] = BeerKnowledgeInput

    def _run(
        self,
        question: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        chain = RetrievalQA.from_chain_type(
            self.llm, chain_type=beer_chain_type,
            retriever=self.vector_store.as_retriever(search_type="similarity",
                                                     search_kwargs={"k": self.k}),
            return_source_documents=True
        )
        chain_result = chain({chain.input_key: question}, return_only_outputs=True)
        result = {}
        result['answer'] = chain_result['result']
        result['sources'] = [x.metadata['source'] for x in chain_result['source_documents']]
        return json.dumps(result)

    async def _arun(
        self,
        question: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        chain = RetrievalQA.from_chain_type(
            self.llm, chain_type=beer_chain_type,
            retriever=self.vector_store.as_retriever(search_type="similarity",
                                                     search_kwargs={"k": self.k}),
            return_source_documents=True
        )
        chain_result = await chain.acall({chain.input_key: question}, return_only_outputs=True)
        result = {}
        result['answer'] = chain_result['result']
        result['sources'] = [x.metadata['source'] for x in chain_result['source_documents']]
        return json.dumps(result)


beer_qa_tool = BeerKnowledge()
