__all__ = ("get_routers")

from .endpoints import router

def get_routers():
    return [
        router
    ]

from .middlewares.db_container import DBContainerMiddleware
from .middlewares.redis import RedisMiddleware
from .middlewares.tgbot_dispatcher import TGDispatcherMiddleware

def set_middleware(app):
    app.add_middleware(DBContainerMiddleware)
    app.add_middleware(RedisMiddleware)
    app.add_middleware(TGDispatcherMiddleware)