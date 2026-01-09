from io import BytesIO
from pypdf import PdfReader
from .exceptions import BadFileError

def is_pdf(data: bytes) -> bool:
    return data.startswith(b"%PDF-")

def read_pdf(book: BytesIO) -> str:
    try:
        reader = PdfReader(book)

        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        
        return text
    except BadFileError: 
        raise BadFileError("Поврежденный файл ")