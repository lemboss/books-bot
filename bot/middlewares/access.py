import logging
from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from config import settings

logger = logging.getLogger(__name__)

class AccessMiddleware(BaseMiddleware):
    
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:        
        
        if data.get("event_from_user").id in settings.tgbot.admins:
            return await handler(event, data)