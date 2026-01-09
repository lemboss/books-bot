import logging
from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, ShowMode
from config import settings
from bot.utils.menu_commands import set_default_commands, set_admin_commands, clear_all_commands
from bot.dialogs.menu.states import MenuSG

logger = logging.getLogger(__name__)

router = Router()

@router.message(CommandStart())
async def start(message: Message, dialog_manager: DialogManager, bot: Bot):
    user_id = message.from_user.id
    
    await clear_all_commands(bot, user_id)
    if user_id in settings.tgbot.admins:
        await set_admin_commands(bot, user_id)
    else:
        await set_default_commands(bot)
                
    state = MenuSG.main    
    await dialog_manager.start(state=state, 
                                mode=StartMode.RESET_STACK, 
                                show_mode=ShowMode.SEND,
                                data={})