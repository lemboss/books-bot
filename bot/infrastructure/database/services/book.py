from typing import List
from ..repositories import BookRepository
from ..models import Book

class BookService:
    
    def __init__(self, book_repo: BookRepository):
        self.book_repo = book_repo
        
    async def add_book(self, owner_id, title, link, type_storage, pages: int):
        return await self.book_repo.create(owner_id=owner_id, title=title, link=link, type_storage=type_storage, pages=pages)
    
    async def get_book(self, book_id) -> Book:
        return await self.book_repo.get(book_id)
    
    async def get_users_books(self, user_id) -> List[Book]:
        return await self.book_repo.get_all(owner_id=user_id)