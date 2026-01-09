from sqlalchemy import desc, select
from .base import BaseRepository
from ..models import User

from sqlalchemy.ext.asyncio import AsyncSession

class ReadingRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession, model: User):
        super().__init__(session, model)
        
    async def get_by_foreigns(self, user_id: int, book_id: int):
        query = (
            select(self.model)
            .where(self.model.user_id==user_id, self.model.book_id==book_id)
        )
        
        response = await self.session.execute(query)
        return response.scalars().one_or_none()
    
    async def get_upper_by_updated_id(self, user_id: int):
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(desc(self.model.updated_at))
            .limit(1)
        )
        
        response = await self.session.execute(query)
        return response.scalars().one_or_none()