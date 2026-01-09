from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PageContentDTO:
    page: int
    content: str

@dataclass
class BookContentsDTO:
    book_id: int
    contents: List[PageContentDTO]