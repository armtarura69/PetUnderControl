from aiogram import Router
from aiogram.types import Message
import sqlite3

profile_router = Router()

@profile_router.message(commands=['start'])
async def start(message: Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    exists = c.fetchone()

    if not exists:
        c.execute("INSERT INTO users(user_id, name) VALUES (?, ?)", (user_id, message.from_user.first_name))
        conn.commit()
        text = "Профиль создан!"
    else:
        text = "Ваш профиль уже существует."

    conn.close()
    await message.answer(text)


@profile_router.message(commands=['profile'])
async def profile(message: Message):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id,))
    user = c.fetchone()
    conn.close()

    if user:
        await message.answer(f"Ваш профиль:\nИмя: {user[1]}")
    else:
        await message.answer("Профиль не найден. Используйте /start")