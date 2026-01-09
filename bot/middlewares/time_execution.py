import logging
import time
from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)

class TimeExecutionMiddleware(BaseMiddleware):
    
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:        
        execution_start = time.perf_counter() 
        response = await handler(event, data)
        elapsed = time.perf_counter() - execution_start
        logger.info(f"Обработал update от {data.get('event_from_user').id} за {elapsed:.2f} сек")
        return response