from aiogram.enums import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities.media import MediaAttachment
    
async def getter_my_books(dialog_manager, **__):
    user_id = dialog_manager.event.from_user.id
    db = dialog_manager.middleware_data.get("db")
    books = await db.book_service.get_users_books(user_id)
    return {
        "books": ((b.id, b.title) for b in books)
    }
    
async def getter_book_content(dialog_manager, **__):
    user_id = dialog_manager.event.from_user.id
    db = dialog_manager.middleware_data.get("db")
    book_id = dialog_manager.dialog_data.get("book_id") 
    pointer = await db.reading_service.get_last_pointer(user_id, book_id)
    page = pointer.page
    content = await db.book_content_service.get_book_content(book_id, page)
    book = await db.book_service.get_book(book_id)
    return {
        "content": content,
        "page": page,
        "prev": page - 1,
        "next": page + 1,
        "not_first_page": page > 1,
        "not_last_page": page != book.pages,
        "all_pages": book.pages
    }