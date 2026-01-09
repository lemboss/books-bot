from dataclasses import dataclass
from typing import List, Optional

@dataclass
class BookDTO:
    book_id: int
    user_id: int
    title: str
    pages: int