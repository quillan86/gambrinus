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
from langchain.retrievers import WikipediaRetriever


wiki_chain_type: str = "stuff"


class WikiInput(BaseModel):
    question: str = Field(..., description="should be a fully formed question")


class Wikipedia(BaseTool):
    """Tool for the Wikipedia Retriever"""
    name: str = "wikipedia"
    description: str = ("Useful for when you need to answer general questions about "
                        "people, places, companies, facts, historical events, or other subjects. "
                       )
    k: int = 4
    vector_store = knowledge_vector_store
    llm = precise_chat_long_llm
    args_schema: Type[WikiInput] = WikiInput

    def _run(
        self,
        question: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        chain = RetrievalQA.from_chain_type(
            self.llm, chain_type=wiki_chain_type,
            retriever=WikipediaRetriever(),
            return_source_documents=True
        )
        chain_result = chain({chain.input_key: question}, return_only_outputs=True)
        result = {}
        result['answer'] = chain_result['result']
        result['sources'] = [x.metadata['title'] for x in chain_result['source_documents']]
        return json.dumps(result)

    async def _arun(
        self,
        question: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        chain = RetrievalQA.from_chain_type(
            self.llm, chain_type=wiki_chain_type,
            retriever=WikipediaRetriever(),
            return_source_documents=True
        )
        chain_result = await chain.acall({chain.input_key: question}, return_only_outputs=True)
        result = {}
        result['answer'] = chain_result['result']
        result['sources'] = [x.metadata['title'] for x in chain_result['source_documents']]
        return json.dumps(result)


wikipedia_tool = Wikipedia()
