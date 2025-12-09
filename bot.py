import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
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

# Команды
dp.message.register(cmd_start, commands=["start"])
dp.message.register(cmd_inline, commands=["inline"])

# Общая маршрутизация текста
dp.message.register(on_text_profile, types.ContentType.TEXT)

# Поток добавления питомца
dp.message.register(
    start_add_pet,
    lambda msg: msg.text and msg.text.lower() == "добавить питомца",
    types.ContentType.TEXT
)
dp.message.register(pet_breed, pet_flow.PetStates.waiting_breed, types.ContentType.TEXT)
dp.message.register(pet_name, pet_flow.PetStates.waiting_name, types.ContentType.TEXT)
dp.message.register(pet_age, pet_flow.PetStates.waiting_age, types.ContentType.TEXT)
dp.message.register(pet_extra, pet_flow.PetStates.waiting_extra, types.ContentType.TEXT)
dp.message.register(pet_confirm, pet_flow.PetStates.confirm, types.ContentType.TEXT)

# Редактирование питомца
dp.message.register(
    start_edit_pet,
    lambda msg: msg.text and msg.text.lower() == "изменить информацию о питомце",
    types.ContentType.TEXT
)
dp.message.register(choose_pet_to_edit, state="waiting_choose_pet", content_types=types.ContentType.TEXT)
dp.message.register(field_choice, state="waiting_field_choice", content_types=types.ContentType.TEXT)
dp.message.register(new_value_input, state="waiting_new_value", content_types=types.ContentType.TEXT)

# Заметки
dp.message.register(
    start_notes,
    lambda msg: msg.text and msg.text.lower() == "заметки",
    types.ContentType.TEXT
)
dp.message.register(
    start_add_note,
    lambda msg: msg.text and msg.text.lower() == "добавить заметку",
    types.ContentType.TEXT
)
dp.message.register(choose_pet_for_note, notes_flow.NoteStates.choose_pet, types.ContentType.TEXT)
dp.message.register(note_title, notes_flow.NoteStates.waiting_title, types.ContentType.TEXT)
dp.message.register(note_period, notes_flow.NoteStates.waiting_period, types.ContentType.TEXT)
dp.message.register(note_extra, notes_flow.NoteStates.waiting_extra, types.ContentType.TEXT)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
