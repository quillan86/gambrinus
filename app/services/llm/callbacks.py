from langchain.callbacks.manager import AsyncCallbackManagerForChainRun

async_callback_manager = AsyncCallbackManagerForChainRun.get_noop_manager()
async_callbacks = async_callback_manager.get_child()
