import logging
from aiogram import Router, F
from aiogram.types import LabeledPrice, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from bot.dialogs.menu.states import MenuSG
from bot.service.logs.logs import save_input_description_song
from bot.dto.song.generate import SongSunoDTO
from bot.service.cache import add_request_response, read_request_response
from bot.service.generate_song import handle_input, to_generate_song
from bot.utils.enums import Face
from bot.dialogs.song.states import SongSG 
from config import settings

logger = logging.getLogger(__name__)

router = Router()

@router.message(F.text)
async def any_message(message: Message, db_container, cache, dialog_manager: DialogManager, dialog_bg_factory, bot):
    await add_request_response(cache, Face.USER, message.text, message.from_user.id)
    items = await read_request_response(cache, message.from_user.id)
    await save_input_description_song(None, message.chat.id, db_container, message.text)
    task = None
    
    if len(items) <= settings.program.max_requests_response_per_song:
        task = await handle_input(items, dialog_bg_factory, message.from_user.id, bot, SongSG.adjustment_text, cache, db_container)
    elif len(items) > settings.program.max_requests_response_per_song:
        if data.get("song_base"):
            data = dialog_manager.start_data
            song = SongSunoDTO(**data.get("song_base"))
            await to_generate_song(bot, message.chat.id, song, db_container, cache, dialog_manager, task)
            logger.info(f"{message.from_user.id} превысил кол-во допустимых промптов, началась генерация песни")
        else:
            logger.error(f"{message.from_user.id} ошибка при генерации (нет данных по песне, перевод в меню оплаты)")
            await dialog_manager.start(MenuSG.main, data={}, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)