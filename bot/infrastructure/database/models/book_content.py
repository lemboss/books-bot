from sqlalchemy import String
from sqlalchemy import BIGINT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from ...database import Base
from ..utils import int_pk, created_at

class BookContent(Base):
    __tablename__ = 'book_content'

    id: Mapped[int_pk]
    book_id: Mapped[str] = mapped_column(ForeignKey("book.id", ondelete="CASCADE"))
    page: Mapped[int]
    content: Mapped[str] = mapped_column(String(4096))
    created_at: Mapped[created_at]
    
    def __repr__(self) -> str:
        return (
            f"book_content.book_id={self.book_id}, book.page={self.page}, book_content.content={self.content[:15]}"
        )