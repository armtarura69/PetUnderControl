from aiogram import Router
from aiogram.types import Message
import sqlite3

pets_router = Router()

@pets_router.message(commands=['add_pet'])
async def add_pet(message: Message):
    try:
        _, name, pet_type = message.text.split(maxsplit=2)
    except:
        return await message.answer("Использование:\n/add_pet <имя> <тип>\nПример: /add_pet Боня кошка")

    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT INTO pets(user_id, pet_name, pet_type) VALUES (?, ?, ?)",
              (message.from_user.id, name, pet_type))
    conn.commit()
    conn.close()

    await message.answer(f"Добавлено животное: {name} ({pet_type})")


@pets_router.message(commands=['pets'])
async def pets_list(message: Message):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()

    c.execute("SELECT pet_name, pet_type FROM pets WHERE user_id=?", (message.from_user.id,))
    pets = c.fetchall()
    conn.close()

    if not pets:
        await message.answer("У вас нет домашних животных.")
    else:
        text = "Ваши животные:\n"
        text += "\n".join([f"• {p[0]} ({p[1]})" for p in pets])
        await message.answer(text)