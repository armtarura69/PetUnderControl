# bot.py
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command, StateFilter
from aiogram import F

from config import BOT_TOKEN
from db.requests import init_db

from handlers import start_inline, profile, pet_flow, notes_flow
from handlers.start_inline import cmd_start, cmd_inline
from handlers.profile import on_text_profile
from handlers.pet_flow import (
    start_add_pet, pet_breed, pet_name, pet_age, pet_extra, pet_confirm,
    start_edit_pet, choose_pet_to_edit, field_choice, new_value_input
)
from handlers.notes_flow import (
    start_notes, start_add_note, choose_pet_for_note, note_title,
    note_period, note_extra
)

logging.basicConfig(level=logging.INFO)

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в окружении")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Инициализация БД
init_db()

# --- РЕГИСТРАЦИЯ ХЕНДЛЕРОВ ---

# 1. Сначала регистрируем команды
dp.message.register(cmd_start, Command(commands=["start"]))
dp.message.register(cmd_inline, Command(commands=["inline"]))

# 2. Затем конкретные текстовые команды (Flow добавления питомца)
dp.message.register(
    start_add_pet,
    F.text.lower() == "добавить питомца"
)
# Состояния передаем позиционно, без "state=". F.text заменяет content_types
dp.message.register(pet_breed, pet_flow.PetStates.waiting_breed, F.text)
dp.message.register(pet_name, pet_flow.PetStates.waiting_name, F.text)
dp.message.register(pet_age, pet_flow.PetStates.waiting_age, F.text)
dp.message.register(pet_extra, pet_flow.PetStates.waiting_extra, F.text)
dp.message.register(pet_confirm, pet_flow.PetStates.confirm, F.text)

# 3. Flow редактирования питомца
dp.message.register(
    start_edit_pet,
    F.text.lower() == "изменить информацию о питомце"
)
dp.message.register(choose_pet_to_edit, pet_flow.EditPetStates.waiting_choose_pet, F.text)
dp.message.register(field_choice, pet_flow.EditPetStates.waiting_field_choice, F.text)
dp.message.register(new_value_input, pet_flow.EditPetStates.waiting_new_value, F.text)

# 4. Flow заметок
dp.message.register(
    start_notes,
    F.text.lower() == "заметки"
)
dp.message.register(
    start_add_note,
    F.text.lower() == "добавить заметку"
)
dp.message.register(choose_pet_for_note, notes_flow.NoteStates.choose_pet, F.text)
dp.message.register(note_title, notes_flow.NoteStates.waiting_title, F.text)
dp.message.register(note_period, notes_flow.NoteStates.waiting_period, F.text)
dp.message.register(note_extra, notes_flow.NoteStates.waiting_extra, F.text)

# 5. В САМОМ КОНЦЕ регистрируем общий обработчик текста
# Если поставить его выше, он будет перехватывать команды "добавить питомца" и т.д.
dp.message.register(on_text_profile, F.text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())