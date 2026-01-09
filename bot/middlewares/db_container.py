from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.infrastructure.database.db_container import container_factory
from bot.infrastructure.database import get_session

class DBContainerMiddleware(BaseMiddleware):
    
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        async with get_session() as session:        
            data.setdefault("db", container_factory(session))
            
            return await handler(event, data)