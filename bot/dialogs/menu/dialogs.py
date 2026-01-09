import operator
from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Next, Row, ScrollingGroup, Select, SwitchTo, Url, WebApp
from aiogram_dialog.widgets.input import TextInput, MessageInput
from .states import MenuSG
from .getters import *
from .handlers import *

main_menu_dialog = Dialog(
    Window(
        Const("Привет!"),
        SwitchTo(
            Const("Продолжить чтение"),
            id="to_continue_reading_btn",
            on_click=open_latest_book,
            state=MenuSG.reading_book,
            when="any_pointer"
        ),
        SwitchTo(
            Const("Добавить книгу"),
            id="to_add_book_btn",
            state=MenuSG.upload_book
        ),
        SwitchTo(
            Const("Мои книги"),
            id="to_my_books_btn",
            state=MenuSG.my_books,
            when="any_books"
        ),
        state=MenuSG.main,
        getter=getter_menu
    ),
    Window(
        Const("Загрузите PDF"),
        SwitchTo(
            Const("Назад"),
            id="to_main_menu_btn",
            state=MenuSG.main
        ),
        MessageInput(handler, content_types=[ContentType.DOCUMENT]),
        state=MenuSG.upload_book
    ),
    Window(
        Const("Мои книги                                                         ᅟ"),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                id="select_book",
                item_id_getter=operator.itemgetter(0),
                items="books",
                on_click=open_selected_book,
                type_factory=int
            ),
            id="scrolling_my_songs",
            width=1,
            height=15,
            hide_on_single_page=True
        ),
        SwitchTo(
            Const("Назад"),
            id="to_main_menu_btn",
            state=MenuSG.main
        ),
        state=MenuSG.my_books,
        getter=getter_my_books
    ),
    Window(
        Format("{content}"),
        Row(
            Button(
                Format("⬅️ {prev}"),
                id='to_prev_page_btn',
                on_click=to_prev_page,
                when="not_first_page"
            ),
            Button(
                Format("{page}/{all_pages}"),
                id="pass_current_page",
                on_click=skip
            ),
            Button(
                Format("{next} ➡️"),
                id='to_next_page_btn',
                on_click=to_next_page,
                when="not_last_page"
            )
        ),
        state=MenuSG.reading_book,
        getter=getter_book_content
    ),
)
