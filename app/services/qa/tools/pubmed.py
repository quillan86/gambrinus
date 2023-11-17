from ....services.llm import precise_chat_long_llm
from langchain.chains import RetrievalQAWithSourcesChain, RetrievalQA
from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
import json
from typing import Optional, Type
from ....db.vectordb import knowledge_vector_store
from langchain.retrievers import PubMedRetriever


wiki_chain_type: str = "stuff"


class PubMedInput(BaseModel):
    query: str = Field(..., description="should be a search query")


class PubMed(BaseTool):
    """Tool for the PubMed Retriever"""
    name: str = "pubmed"
    description: str = ("Useful for when you need to answer questions about medicine, health, "
                        "and biomedical topics "
                        "from biomedical literature, MEDLINE, life science journals, and online books. "
                        "Input should be a search query."
                       )
    k: int = 4
    vector_store = knowledge_vector_store
    llm = precise_chat_long_llm
    args_schema: Type[PubMedInput] = PubMedInput

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        chain = RetrievalQA.from_chain_type(
            self.llm, chain_type=wiki_chain_type,
            retriever=PubMedRetriever(),
            return_source_documents=True
        )
        chain_result = chain({chain.input_key: query}, return_only_outputs=True)
        result = {}
        result['answer'] = chain_result['result']
        result['sources'] = [x.metadata['Title'] for x in chain_result['source_documents']]
        return json.dumps(result)

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        chain = RetrievalQA.from_chain_type(
            self.llm, chain_type=wiki_chain_type,
            retriever=PubMedRetriever(),
            return_source_documents=True
        )
        chain_result = await chain.acall({chain.input_key: query}, return_only_outputs=True)
        result = {}
        result['answer'] = chain_result['result']
        result['sources'] = [x.metadata['Title'] for x in chain_result['source_documents']]
        return json.dumps(result)


pubmed_tool = PubMed()
