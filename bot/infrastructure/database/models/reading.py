from sqlalchemy import BIGINT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from ...database import Base
from ..utils import int_pk, created_at, updated_at

class Reading(Base):
    __tablename__ = 'reading'

    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("user.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("book.id", ondelete="CASCADE"))
    page: Mapped[int]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    def __repr__(self) -> str:
        return (
            f"book.id={self.id}, book.title={self.title}"
        )