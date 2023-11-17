import os
from langchain.llms import AzureOpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import OpenAIEmbeddings


# https://clemenssiebler.com/posts/using-langchain-with-azure-openai-service/
# configuration set via environmental variables

DEPLOYMENT_NAME: str = os.getenv("AZURE_DEPLOYMENT_NAME")
DEPLOYMENT_CHAT_NAME: str = os.getenv("AZURE_CHAT_DEPLOYMENT_NAME")
DEPLOYMENT_CHAT_16K_NAME: str = os.getenv("AZURE_CHAT_16K_DEPLOYMENT_NAME")
DEPLOYMENT_CHAT_GPT4_NAME: str = os.getenv("AZURE_CHAT_GPT4_DEPLOYMENT_NAME")
EMBEDDING_DEPLOYMENT_NAME: str = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")
MODEL_NAME: str = 'text-davinci-003'
CHAT_MODEL_NAME: str = 'gpt-3.5-turbo'
CHAT_MODEL_NAME_LONG: str = 'gpt-3.5-turbo-16k'
CHAT_MODEL_GPT4_NAME: str = 'gpt-4'
EMBEDDING_MODEL_NAME: str = 'text-embedding-ada-002'

# Creative LLM - used for variational conversational responses
creative_llm = AzureOpenAI(
    deployment_name=DEPLOYMENT_NAME,
    model_name=MODEL_NAME,
    temperature=0.5,
    max_tokens=2048
)

# Precise LLM - used for question answering
precise_llm = AzureOpenAI(
    deployment_name=DEPLOYMENT_NAME,
    model_name=MODEL_NAME,
    temperature=0,
    max_tokens=2048
)

creative_llm_no_cache = AzureOpenAI(
    deployment_name=DEPLOYMENT_NAME,
    model_name=MODEL_NAME,
    temperature=0.6,
    max_tokens=2048,
    cache=False
)

precise_llm_no_cache = AzureOpenAI(
    deployment_name=DEPLOYMENT_NAME,
    model_name=MODEL_NAME,
    temperature=0,
    max_tokens=2048,
    cache=False
)

creative_chat_llm = AzureChatOpenAI(
    deployment_name=DEPLOYMENT_CHAT_NAME,
    model_name=CHAT_MODEL_NAME,
    temperature=0.6,
    max_tokens=2048
)

precise_chat_llm = AzureChatOpenAI(
    deployment_name=DEPLOYMENT_CHAT_NAME,
    model_name=CHAT_MODEL_NAME,
    temperature=0.0,
    max_tokens=2048
)

creative_chat_long_llm = AzureChatOpenAI(
    deployment_name=DEPLOYMENT_CHAT_16K_NAME,
    model_name=CHAT_MODEL_NAME_LONG,
    temperature=0.6,
    max_tokens=3072
)

precise_chat_long_llm = AzureChatOpenAI(
    deployment_name=DEPLOYMENT_CHAT_16K_NAME,
    model_name=CHAT_MODEL_NAME_LONG,
    temperature=0,
    max_tokens=3072
)

precise_chat_gpt4_llm = AzureChatOpenAI(
    deployment_name=DEPLOYMENT_CHAT_GPT4_NAME,
    model_name=CHAT_MODEL_GPT4_NAME,
    temperature=0,
    max_tokens=3072
)

creative_chat_gpt4_llm = AzureChatOpenAI(
    deployment_name=DEPLOYMENT_CHAT_GPT4_NAME,
    model_name=CHAT_MODEL_GPT4_NAME,
    temperature=0.6,
    max_tokens=3072
)

agent_chat_llm = AzureChatOpenAI(
    deployment_name=DEPLOYMENT_CHAT_GPT4_NAME,
    model_name=CHAT_MODEL_GPT4_NAME,
    temperature=0.5,
    max_tokens=3072
)

# Embeddings
embeddings = OpenAIEmbeddings(deployment=EMBEDDING_DEPLOYMENT_NAME,
                              model=EMBEDDING_MODEL_NAME, chunk_size=1)
