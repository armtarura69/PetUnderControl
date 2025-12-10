# keyboards/main_keyboards.py
from aiogram import types


def main_reply_keyboard() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="О нас"), types.KeyboardButton(text="Профиль")],
            [types.KeyboardButton(text="Заметки"), types.KeyboardButton(text="Добавить питомца")],
        ],
        resize_keyboard=True
    )
    return kb


def back_to_main_keyboard() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Отмена")],
        ],
        resize_keyboard=True
    )
    return kb


def profile_options_keyboard() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Посмотреть профиль")],
            [types.KeyboardButton(text="Добавить питомца")],
            [types.KeyboardButton(text="изменить информацию о питомце")],
            [types.KeyboardButton(text="Отмена")],
        ],
        resize_keyboard=True
    )
    return kb


def pet_confirm_keyboard() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Все верно")],
            [types.KeyboardButton(text="Изменить")],
            [types.KeyboardButton(text="Отмена")],
        ],
        resize_keyboard=True
    )
    return kb


def note_period_keyboard() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="не повторять")],
            [types.KeyboardButton(text="6 ч")],
            [types.KeyboardButton(text="день")],
            [types.KeyboardButton(text="Неделя")],
            [types.KeyboardButton(text="месяц")],
            [types.KeyboardButton(text="Год")],
            [types.KeyboardButton(text="Отмена")],
        ],
        resize_keyboard=True
    )
    return kb
