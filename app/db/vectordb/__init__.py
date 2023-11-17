import os
from langchain.vectorstores.base import VectorStore, VectorStoreRetriever
from langchain.vectorstores import Milvus
from langchain.embeddings.openai import OpenAIEmbeddings

openai_embeddings = OpenAIEmbeddings(deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME"))

knowledge_collection_name = os.getenv("GAMBRINUS_MILVUS_KNOWLEDGE_COLLECTION")
support_collection_name = "support"

connection_args = {"host": os.getenv("GAMBRINUS_MILVUS_HOST"),
                        "port": os.getenv("GAMBRINUS_MILVUS_PORT"),
                        "user": os.getenv("GAMBRINUS_MILVUS_USER"),
                        "password": os.getenv("GAMBRINUS_MILVUS_PASSWORD"),
                        "secure": True
                        }
knowledge_vector_store: VectorStore = Milvus(
    embedding_function=openai_embeddings,
    collection_name=knowledge_collection_name,
    connection_args=connection_args,
    drop_old=False,
)

support_vector_store: VectorStore = Milvus(
    embedding_function=openai_embeddings,
    collection_name=support_collection_name,
    connection_args=connection_args,
    drop_old=False,
)

__all__ = ['openai_embeddings', 'knowledge_collection_name', 'knowledge_vector_store', 'support_vector_store']