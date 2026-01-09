from sqlalchemy import BIGINT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from ...database import Base
from ..utils import created_at

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    username: Mapped[str | None]
    is_active: Mapped[bool]
    created_at: Mapped[created_at]
    
    def __repr__(self) -> str:
        return (
            f"User.id={self.id}"
        )