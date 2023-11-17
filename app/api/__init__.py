from .exchange import routers as exchange_routers
from .assistant import routers as assistant_routers
from .website import routers as website_routers

routers = {key: router for routers in [exchange_routers, assistant_routers, website_routers]
           for key, router in routers.items()}

__all__ = ["routers"]