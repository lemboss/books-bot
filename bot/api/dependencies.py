from fastapi import Depends
from sqlalchemy.orm import Session

from bot.infrastructure.database.db_container import container_factory
from bot.infrastructure.database import get_session_factory

async def get_container(
    session_factory = Depends(get_session_factory),
):
    session: Session = session_factory()
    try:
        yield container_factory(session)
    finally:
        await session.close()