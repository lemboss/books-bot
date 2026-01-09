from bot.service.book.read import read_pdf

def test_read_book(book):
    text = read_pdf(book)
    print(text)
    assert text == "Минимальная книга "