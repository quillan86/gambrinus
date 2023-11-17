from ....services.llm import precise_chat_long_llm
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
import json
from typing import Optional, Type
from ....db.vectordb import support_vector_store


beer_chain_type: str = "stuff"


class SupportKnowledgeInput(BaseModel):
    question: str = Field(description="should be a fully formed question")


class SupportKnowledge(BaseTool):
    """Tool for the VectorDBQAWithSources chain."""
    name: str = "support_knowledge"
    description: str = ("Useful for when you need information on the company Estimand, "
                        "Gambrinus the chatbot, the Brewers Exchange, or other products by Estimand. "
                        "Do NOT use this tool for answering questions unrelated to these topics. Use other tools. "
                        "Input should be a fully formed question. "
                       )
    k: int = 4
    vector_store = support_vector_store
    llm = precise_chat_long_llm
    args_schema: Type[SupportKnowledgeInput] = SupportKnowledgeInput

    def _run(
        self,
        question: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        chain = RetrievalQAWithSourcesChain.from_chain_type(
            self.llm, chain_type=beer_chain_type,
            retriever=self.vector_store.as_retriever(search_type="similarity",
                                                     search_kwargs={"k": self.k}),
            sources_answer_key="sources"
        )
        return json.dumps(chain({chain.question_key: question}, return_only_outputs=True))

    async def _arun(
        self,
        question: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        chain = RetrievalQAWithSourcesChain.from_chain_type(
            self.llm, chain_type=beer_chain_type,
            retriever=self.vector_store.as_retriever(search_type="similarity",
                                                     search_kwargs={"k": self.k}),
            sources_answer_key="sources",
            max_tokens_limit=15625,
            reduce_k_below_max_tokens=True
        )
        return json.dumps(chain.acall({chain.question_key: question}, return_only_outputs=True))


support_qa_tool = SupportKnowledge()
