from .base import BaseRepository
from ..models import User

from sqlalchemy.ext.asyncio import AsyncSession

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession, model: User):
        super().__init__(session, model)
        