from bot.service.book.handle import pages_to_dto, remove_new_lines, split_into_tokens
from bot.service.book.upload import book_upload_disk, get_lib_path


async def add_book_disk(user_id, data: bytes, text: str, db):   
    text = remove_new_lines(text) 
    title = text[:25]
    pages = split_into_tokens(text)
    
    # положить на диск
    book_path = get_lib_path(user_id, title)
    book_upload_disk(book_path, data)
    book = await db.book_service.add_book(user_id, title, book_path, "disk", pages=len(pages))
    
    # загрузить в базу
    dto = pages_to_dto(book.id, pages)
    await db.book_content_service.add_content(dto)
    
    # активировать указатель
    await db.reading_service.create_pointer(user_id=user_id, book_id=book.id)
    
    await db.session.commit()