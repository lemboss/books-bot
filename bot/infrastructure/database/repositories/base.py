from typing import Generic, Iterable, TypeVar, Type, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound="DeclarativeBase")

class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий для CRUD-операций"""

    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def get(self, id: int) -> Optional[ModelType]:
        """Получить объект по ID"""
        return await self.session.get(self.model, id)

    async def get_all(self, **filters) -> Sequence[ModelType]:
        """Получить список объектов"""
        stmt = select(self.model)
        if filters:
            stmt = stmt.filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs) -> ModelType:
        """Создать новую запись"""
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush([obj])
        return obj
    
    async def create_many(self, items: Sequence[ModelType]) -> int:
        self.session.add_all(items)
        return len(items)

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Обновить запись по ID"""
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        updated = result.scalar_one_or_none()
        return updated

    async def delete(self, id: int) -> bool:
        """Удалить запись по ID"""
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0