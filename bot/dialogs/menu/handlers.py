from io import BytesIO
import logging
from datetime import datetime
from sysconfig import get_path
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import ShowMode

from bot.dialogs.menu.states import MenuSG
from bot.service.book.flow import add_book_disk
from config import settings
from bot.service.book.read import is_pdf, read_pdf

logger = logging.getLogger(__name__)

# async def handler(callback: CallbackQuery, __: Button, dialog_manager: DialogManager):
#     ...

async def handler(message: Message, __: Button, dialog_manager: DialogManager):
    bot = message.bot
    doc = message.document    
    db = dialog_manager.middleware_data.get("db")
    
    if doc.mime_type != "application/pdf":
        return await message.answer("Нужен PDF")

    if doc.file_size > 100 * 1024 * 1024:
        return await message.answer("Файл слишком большой (> 100 MB)")
        

    stream = await bot.download(doc)
    data = stream.read()

    if not is_pdf(data):
        return await message.answer("Это не PDF")
    try:
        text = read_pdf(BytesIO(data))
    except Exception:
        return await message.answer("PDF повреждён")
    await add_book_disk(message.from_user.id, data, text, db)
    await message.answer("PDF принят 👍")
    
async def open_latest_book(callback: CallbackQuery, __: Button, dialog_manager: DialogManager):
    db = dialog_manager.middleware_data.get("db")
    pointer = await db.reading_service.get_latest(callback.from_user.id)
    dialog_manager.dialog_data["book_id"] = pointer.book_id
    
async def open_selected_book(callback: CallbackQuery, __: Button, dialog_manager: DialogManager, book_id: int):
    dialog_manager.dialog_data["book_id"] = book_id
    await dialog_manager.switch_to(MenuSG.reading_book)
    
async def to_next_page(callback: CallbackQuery, __: Button, dialog_manager: DialogManager):
    db = dialog_manager.middleware_data.get("db")
    book_id = dialog_manager.dialog_data.get("book_id")
    pointer = await db.reading_service.get_last_pointer(callback.from_user.id, book_id)
    await db.reading_service.set_pointer(pointer.id, page=pointer.page+1)
    await db.session.commit()
    
async def to_prev_page(callback: CallbackQuery, __: Button, dialog_manager: DialogManager):
    db = dialog_manager.middleware_data.get("db")
    book_id = dialog_manager.dialog_data.get("book_id")
    pointer = await db.reading_service.get_last_pointer(callback.from_user.id, book_id)
    await db.reading_service.set_pointer(pointer.id, page=pointer.page-1)
    await db.session.commit()
    
async def skip(callback: CallbackQuery, __: Button, dialog_manager: DialogManager):
    return 1