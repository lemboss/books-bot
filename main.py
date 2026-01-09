import logging
import asyncio
from aiogram_dialog import setup_dialogs
from config import settings
from bot import dp, bot, get_routers, register_middlewares

logger = logging.getLogger(__name__)

async def main():
    register_middlewares(dp)
    dp.include_routers(*get_routers())

    setup_dialogs(dp)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")