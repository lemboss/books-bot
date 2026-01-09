from bot.infrastructure.dto.book_content import BookContentsDTO, PageContentDTO

TOKENS_PER_PAGE = 766

def split_into_tokens(text: str): 
    i = 0
    size = len(text)
    pages = []
    while i < size:
        page = text[i:i+TOKENS_PER_PAGE]
        pages.append(page)
        i += TOKENS_PER_PAGE
        
    return pages

# def remove_new_lines(text: str): 
#     return text.replace("\n", "")

def remove_new_lines(text: str): 
    new_text = ""
    i = 0
    size = len(text)
    while i < size - 1:
        if text[i] == "\n" and text[i+1].islower():
            new_text += " "
        else:
            new_text += text[i]
        i += 1
    return new_text

def pages_to_dto(book_id, pages):
    mapped = []
    for i, text in enumerate(pages):
        mapped.append(PageContentDTO(page=i+1, content=text))
    return BookContentsDTO(book_id=book_id, contents=mapped)