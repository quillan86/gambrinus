from gptcache import Cache
from .data_manager import data_manager
from .embeddings import onnx, evaluation_onnx
from gptcache.processor.pre import get_prompt
from langchain.cache import GPTCache
import langchain


def init_gptcache(cache_obj: Cache):
    cache_obj.init(pre_embedding_func=get_prompt,
                   embedding_func=onnx.to_embeddings,
                   data_manager=data_manager,
                   similarity_evaluation=evaluation_onnx)
    cache_obj.set_openai_key()


cache: Cache = Cache()
gptcache = GPTCache(init_gptcache)

langchain.llm_cache = gptcache
llm_cache = langchain.llm_cache

__all__ = ['cache', 'gptcache', 'llm_cache']
