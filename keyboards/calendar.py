from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

def calendar_keyboard():
    today = datetime.now().date()
    kb = []

    for i in range(7):  # ближайшие 7 дней
        day = today + timedelta(days=i)
        kb.append([
            InlineKeyboardButton(
                text=day.strftime("%Y-%m-%d"),
                callback_data=f"pick_date:{day}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=kb)


def time_keyboard():
    kb = []
    for hour in range(0, 24):
        kb.append([
            InlineKeyboardButton(
                text=f"{hour:02d}:00",
                callback_data=f"pick_time:{hour:02d}:00"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=kb)