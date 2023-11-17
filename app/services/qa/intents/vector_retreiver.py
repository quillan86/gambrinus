import re
import os
from typing import Optional, Type, Any
from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks.manager import AsyncCallbackManagerForChainRun
from ....services.llm import precise_llm
from ....services.llm.chains import document_chain, question_generator_chain
from ...qa.generic import GenericRetrievalService
from langchain.vectorstores.base import VectorStore, VectorStoreRetriever
from ....db.vectordb import knowledge_vector_store


class VectorRetrievalService(GenericRetrievalService):
    llm = precise_llm
    manager: AsyncCallbackManagerForChainRun = AsyncCallbackManagerForChainRun.get_noop_manager()

    def __init__(self, k: int):
        super().__init__()
        self.k: int = k
        self.vector_store: VectorStore = knowledge_vector_store
        self.retriever: VectorStoreRetriever = self.vector_store.as_retriever(search_type="similarity",
                                                                       search_kwargs={"k": self.k})
        self.history_chain = self.get_chain(tracing=False)
        self.callbacks = self.manager.get_child()
        self.verbose: bool = True

    def get_chain(self, tracing: bool = False
    ) -> ConversationalRetrievalChain:
        """Create a ChatVectorDBChain for question/answering."""
        # Construct a ChatVectorDBChain with a streaming llm for combine docs
        # and a separate, non-streaming llm for question generation

        qa = ConversationalRetrievalChain(
            retriever=self.retriever,
            combine_docs_chain=document_chain,
            question_generator=question_generator_chain,
            return_source_documents=True,
            verbose=True,


        )
        return qa

    def fix_citation_label(self, name: str):
#        pattern = r'[^a-zA-Z\s]*'  # Matches any non-alphanumeric characters and digits
#        result = re.sub(pattern, '', name).strip()
        result = name
        return result

    def get_citations(self, documents) -> str:
        """
        [citation needed]
        :param documents: source documents
        :return: [citations]!!
        """
        # unique citations
        citations = set([f"{self.fix_citation_label(x.metadata['name'])} [{x.metadata['page']}]" for x in documents])
        # convert to string
        result = ', '.join(citations)
        return result

    async def run_chain(self, question, chat_history) -> str:
#        chat_history = [x.content for x in chat_history]

        # get answer
        result = await self.history_chain.acall(
            {"question": question, "chat_history": chat_history},
            callbacks=self.callbacks
        )

        answer = result["answer"]
        sources = result["source_documents"]


        await self.manager.on_text("Generated QA Answer:", end="\n", verbose=self.verbose)
        await self.manager.on_text(answer, color="green", end="\n", verbose=self.verbose)

        if len(sources) > 0:
            citations = self.get_citations(sources)
            response = f"{answer}\nSources: {citations}"
        else:
            response = f"{answer}"
        return response

    @classmethod
    async def run(cls, query: str, **kwargs: Any) -> str:
        pass