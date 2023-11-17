from .response import router as response_router
from .session import router as session_router
from .tool import router as tool_router

routers = {
    'response': response_router,
    'session': session_router,
    'tool': tool_router
}

__all__ = ["routers"]