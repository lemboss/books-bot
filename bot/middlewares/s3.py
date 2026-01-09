from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from config import settings
from bot.infrastructure.s3.manager import S3Manager

class S3Middleware(BaseMiddleware):
    
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        s3 = S3Manager(
            access_key=settings.s3.key_id,
            secret_key=settings.s3.secret_key,
            bucket=settings.s3.bucket
        )
        data.setdefault("s3", s3)
        return await handler(event, data)
        

