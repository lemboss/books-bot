from datetime import datetime

from ..repositories import UserRepository
from ..models import User

class UserService:
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        
    async def add_in_system(self, telegram_id: int, is_active: bool) -> User:
        user = await self.user_repo.get(telegram_id)
        if user:
            return user
        return await self.user_repo.create(id=telegram_id, is_active=is_active)