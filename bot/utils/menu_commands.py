import logging
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

logger = logging.getLogger(__name__)

async def clear_all_commands(bot: Bot, user_id: int):
    """
    Полная очистка меню:
    - глобальные команды
    - команды конкретного пользователя
    """
    try:
        await bot.delete_my_commands(scope=BotCommandScopeDefault())
        await bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=user_id))
    except Exception as e:
        logger.error(f"Не удалось установить команды для chat_id={user_id}")

async def set_default_commands(bot: Bot):
    """Команды по умолчанию (для всех пользователей)"""
    commands = [
        BotCommand(command="start", description="Перезагрузить бот / Главное меню"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def set_admin_commands(bot: Bot, admin_id: int):
    """Команды только для конкретного администратора"""
    commands = [
        BotCommand(command="start", description="Перезагрузить бот / Главное меню"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=admin_id))