from aiogram.fsm.state import State, StatesGroup


class MenuSG(StatesGroup):
    main = State()
    upload_book = State()
    my_books = State()
    reading_book = State()