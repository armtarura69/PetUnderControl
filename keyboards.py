from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Main quick keyboard (reply keyboard)
def main_quick_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("о нас"))
    kb.add(KeyboardButton("профиль"))
    kb.add(KeyboardButton("заметки"))
    return kb

# Profile options keyboard
def profile_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("посмотреть профиль"))
    kb.add(KeyboardButton("добавить питомца"))
    kb.add(KeyboardButton("изменить информацию о питомце"))
    kb.add(KeyboardButton("назад"))  # return
    return kb

# Notes options keyboard
def notes_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("добавить заметку"))
    kb.add(KeyboardButton("удалить заметку"))
    kb.add(KeyboardButton("изменить заметку"))
    kb.add(KeyboardButton("назад"))
    return kb

# Confirmation keyboard (inline)
def confirm_inline_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("все верно", callback_data="confirm_yes"))
    kb.add(InlineKeyboardButton("изменить", callback_data="confirm_edit"))
    return kb

# Simple back inline
def back_inline(text="back"):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("назад", callback_data="back"))
    return kb
