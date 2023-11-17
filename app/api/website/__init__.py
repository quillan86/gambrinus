from .user import router as user_router
from .client import router as client_router
from .blog import router as blog_router
from .auth import router as auth_router
from .contact import router as contact_router

routers = {
    'client': client_router,
    'user': user_router,
    'blog': blog_router,
    'auth': auth_router,
    'contact': contact_router
}

__all__ = ["routers"]