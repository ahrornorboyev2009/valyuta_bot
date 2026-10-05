from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="💵 Dollar"),
                KeyboardButton(text="💶 Yevro"),
            ],
            [
                KeyboardButton(text="🇷🇺 Rubl"),
                KeyboardButton(text="🇬🇧 Funt"),
            ],
            [
                KeyboardButton(text="🇨🇳 Yuan"),
                KeyboardButton(text="📊 Barcha kurslar"),
            ],
        ],
        resize_keyboard=True,
    )
