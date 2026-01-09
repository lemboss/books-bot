from sqlalchemy import BIGINT
from sqlalchemy.orm import Mapped, mapped_column
from ...database import Base
from ..utils import int_pk, created_at

class Book(Base):
    __tablename__ = 'book'

    id: Mapped[int_pk]
    owner_id: Mapped[int] = mapped_column(BIGINT)
    title: Mapped[str]
    link: Mapped[str]
    type_storage: Mapped[str]
    pages: Mapped[int]
    created_at: Mapped[created_at]
    
    def __repr__(self) -> str:
        return (
            f"book.id={self.id}, book.title={self.title}"
        )