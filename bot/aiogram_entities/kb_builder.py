from aiogram.utils.keyboard import InlineKeyboardBuilder

def build_inline(items: list[tuple[str, str]], rows: int): 
    b = InlineKeyboardBuilder()
    for label, cb in items:
        b.button(text=label, callback_data=cb)
    b.adjust(rows)  # 2 кнопки в ряд
    return b.as_markup()

def build_payment(items: list[str], rows: int):
    b = InlineKeyboardBuilder()
    for label in items:
        b.button(text=label, pay=True)
    b.adjust(rows)  # 2 кнопки в ряд
    return b.as_markup()