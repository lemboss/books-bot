__all__ = ("bot", "dp", "get_routers", "register_middlewares")

from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram import Bot, Dispatcher
from bot.middlewares.add_in_user import AddUserMiddleware
from config import settings

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from redis.asyncio import Redis

# redis = Redis(host=settings.redis.host, port=settings.redis.port)
# storage = RedisStorage(redis, key_builder=DefaultKeyBuilder(with_destiny=True))
storage = MemoryStorage()

bot = Bot(token=settings.tgbot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)

from bot.aiogram_entities.routers.main import router as main_router
from bot.dialogs import main_menu_dialog

from bot.middlewares import *

def get_routers():
    return [
        main_router,
        main_menu_dialog
    ]
    

def register_middlewares(dp: Dispatcher):
    dp.update.middleware(DBContainerMiddleware())
    dp.update.middleware(AddUserMiddleware())