from io import BytesIO
import pytest
import asyncio
from sqlalchemy import text
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


from config import settings
from bot.infrastructure.database.database import Base, engine
from bot.infrastructure.database.db_container import Container

from bot import get_routers
from tests.mocked_aiogram import MockedBot, MockedSession


@pytest.fixture(scope="function", autouse=False)
async def prepare_database():
    assert settings.mode == "TEST"

    async with engine.begin() as conn:
        # await conn.execute(text("DROP SCHEMA IF EXISTS bot CASCADE"))
        await conn.run_sync(Base.metadata.drop_all)

        # await conn.execute(text("CREATE SCHEMA IF NOT EXISTS bot"))
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def session():
    from bot.infrastructure.database import get_session
    async with get_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def db_container(session):
    """Создаёт контейнер для DI"""
    from bot.infrastructure.database.models import User, Book, Reading
    from bot.infrastructure.database.repositories import UserRepository, BookRepository, ReadingRepository
    from bot.infrastructure.database.services import UserService, BookService, ReadingService

    yield Container(session,
                    UserService,
                    UserRepository,
                    User,
                    BookService,
                    BookRepository,
                    Book,
                    ReadingService,
                    ReadingRepository,
                    Reading)


@pytest.fixture(scope="session")
def dp() -> Dispatcher:
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_routers(*get_routers())
    return dispatcher


@pytest.fixture(scope="session")
def bot() -> MockedBot:
    bot = MockedBot()
    bot.session = MockedSession()
    return bot

@pytest.fixture(scope="session")
def book() -> MockedBot:
    with open("tests/data/book.pdf", "rb") as file:
        book = BytesIO(file.read())

    return book
