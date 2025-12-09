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
            [types.KeyboardButton(text="на главную")],
        ],
        resize_keyboard=True
    )
    return kb


def profile_options_keyboard() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="посмотреть профиль")],
            [types.KeyboardButton(text="добавить питомца")],
            [types.KeyboardButton(text="изменить информацию о питомце")],
            [types.KeyboardButton(text="на главную")],
        ],
        resize_keyboard=True
    )
    return kb


def pet_confirm_keyboard() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="все верно")],
            [types.KeyboardButton(text="изменить")],
            [types.KeyboardButton(text="отмена")],
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
            [types.KeyboardButton(text="неделя")],
            [types.KeyboardButton(text="месяц")],
            [types.KeyboardButton(text="год")],
            [types.KeyboardButton(text="отмена")],
        ],
        resize_keyboard=True
    )
    return kb
