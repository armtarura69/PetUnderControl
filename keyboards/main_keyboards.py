from aiogram import types

def main_reply_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("о нас"))
    kb.add(types.KeyboardButton("профиль"))
    kb.add(types.KeyboardButton("заметки"))
    return kb

def back_to_main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("на главную"))
    return kb

def profile_options_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("посмотреть профиль"))
    kb.add(types.KeyboardButton("добавить питомца"))
    kb.add(types.KeyboardButton("изменить информацию о питомце"))
    kb.add(types.KeyboardButton("на главную"))
    return kb

def pet_confirm_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("все верно"))
    kb.add(types.KeyboardButton("изменить"))
    kb.add(types.KeyboardButton("отмена"))
    return kb

def note_period_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("не повторять"))
    kb.add(types.KeyboardButton("6 ч"))
    kb.add(types.KeyboardButton("день"))
    kb.add(types.KeyboardButton("неделя"))
    kb.add(types.KeyboardButton("месяц"))
    kb.add(types.KeyboardButton("год"))
    kb.add(types.KeyboardButton("отмена"))
    return kb
