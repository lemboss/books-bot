from ..repositories import BookContentRepository
from bot.infrastructure.dto.book_content import BookContentsDTO, PageContentDTO

class BookContentService:
    
    def __init__(self, content_repo: BookContentRepository):
        self.content_repo = content_repo
        
    async def add_content(self, content: BookContentsDTO):
        content_model = self.content_repo.model
        contents = [content_model(book_id=content.book_id, page=c.page, content=c.content) for c in content.contents]
        return await self.content_repo.create_many(contents)
    
    async def get_book_content(self, book_id, page) -> str:
        content = await self.content_repo.get_all(book_id=book_id, page=page)
        if content:
            return content[0].content