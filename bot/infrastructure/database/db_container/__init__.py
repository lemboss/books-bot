__all__ = (
    "container_factory"
)

from .container import Container
from ..services import *
from ..repositories import *
from ..models import *


def container_factory(session):
    return Container(session,
        user_service=UserService,
        user_repo=UserRepository,
        user_model=User,
        book_service=BookService,
        book_repo=BookRepository,
        book_model=Book,
        reading_service=ReadingService,
        reading_repo=ReadingRepository,
        reading_model=Reading,
        book_content_service=BookContentService,
        book_content_repo=BookContentRepository,
        book_content_model=BookContent
    )