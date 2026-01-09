import logging
from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)

class AddUserMiddleware(BaseMiddleware):
    
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:        
        db = data.get("db")
        if db:
            user_id = data.get("event_from_user").id
            res = await db.user_service.add_in_system(
                telegram_id=user_id, 
                is_active=True
            )
            await db.session.commit()
        return await handler(event, data)