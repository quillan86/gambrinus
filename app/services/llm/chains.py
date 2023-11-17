from .templates import IRRELEVANT_PROMPT, FOLLOWUP_CLASSIFICATION_PROMPT, CYPHER_GENERATION_PROMPT,\
    CYPHER_QA_PROMPT, CONDENSE_QUESTION_PROMPT, MAP_QUESTION_PROMPT, COMBINE_PROMPT, BEER_ENTITY_PROMPT,\
    FLAVOR_PROFILE_PROMPT, FOLLOWUP_PROMPT, SUMMARY_PROMPT
from .models import creative_llm, precise_llm, creative_chat_llm, precise_chat_llm, precise_chat_long_llm, creative_chat_gpt4_llm
from .callbacks import async_callbacks
from langchain.chains import LLMChain
from langchain.chains.question_answering import _load_map_reduce_chain


# base chains to be used elsewhere.

irrelevant_chain = LLMChain(llm=creative_chat_llm, prompt=IRRELEVANT_PROMPT, callbacks=async_callbacks, verbose=True)

followup_classification_chain = LLMChain(llm=precise_chat_long_llm, prompt=FOLLOWUP_CLASSIFICATION_PROMPT, callbacks=async_callbacks, verbose=True)

cypher_generation_chain = LLMChain(llm=precise_chat_llm, prompt=CYPHER_GENERATION_PROMPT, callbacks=async_callbacks)

cyper_qa_chain = LLMChain(llm=precise_chat_llm, prompt=CYPHER_QA_PROMPT, callbacks=async_callbacks)

question_generator_chain = LLMChain(
    llm=precise_chat_llm, prompt=CONDENSE_QUESTION_PROMPT, callbacks=async_callbacks, verbose=True
)

document_chain = _load_map_reduce_chain(llm=precise_llm, reduce_llm=precise_chat_llm,
                                        question_prompt=MAP_QUESTION_PROMPT, combine_prompt=COMBINE_PROMPT,
                                        callbacks=async_callbacks, verbose=True)

beer_entity_chain = LLMChain(
    llm=precise_llm, prompt=BEER_ENTITY_PROMPT,
    callbacks=async_callbacks, verbose=True)

flavor_profile_description_chain = LLMChain(
    llm=creative_chat_gpt4_llm, prompt=FLAVOR_PROFILE_PROMPT, callbacks=async_callbacks, verbose=True
)

followup_chain = LLMChain(
    llm=precise_chat_llm, prompt=FOLLOWUP_PROMPT,
    callbacks=async_callbacks, verbose=True)

summary_chain = LLMChain(
    llm=precise_chat_long_llm, prompt=SUMMARY_PROMPT,
    callbacks=async_callbacks, verbose=True)
