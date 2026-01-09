from datetime import datetime

from ..models import Reading
from ..repositories import ReadingRepository

class ReadingService:
    
    def __init__(self, reading_repo: ReadingRepository):
        self.reading_repo = reading_repo

    async def create_pointer(self, user_id: int, book_id: int, page: int = 1) -> Reading:
        pointer = await self.reading_repo.get_by_foreigns(user_id=user_id, book_id=book_id)
        if pointer:
            return pointer
        return await self.reading_repo.create(user_id=user_id, book_id=book_id, page=page)
    
    async def set_pointer(self, pointer_id: int, page: int) -> Reading:
        return await self.reading_repo.update(id=pointer_id, page=page)
    
    async def get_latest(self, user_id: int) -> Reading:
        pointer = await self.reading_repo.get_upper_by_updated_id(user_id=user_id)
        if pointer:
            return pointer
        
    async def get_last_pointer(self, user_id, book_id) -> int:
        pointer = await self.reading_repo.get_all(book_id=book_id, user_id=user_id)
        if pointer:
            return pointer[0]