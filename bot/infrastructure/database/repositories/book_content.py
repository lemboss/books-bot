from .base import BaseRepository
from ..models import BookContent

from sqlalchemy.ext.asyncio import AsyncSession

class BookContentRepository(BaseRepository[BookContent]):
    def __init__(self, session: AsyncSession, model: BookContent):
        super().__init__(session, model)
        