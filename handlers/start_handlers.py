from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from keyboards import main_quick_kb
from db.requests import async_session, create_user_if_not_exists
from utils import json_response

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    tg_id = message.from_user.id
    async with async_session() as session:
        user, created = await create_user_if_not_exists(tg_id, session)
    text = (
        "Привет! Я бот для управления профилем питомцев и напоминаниями.\n\n"
        "Быстрые кнопки: о нас / профиль / заметки\n"
        "Используйте /inline для получения полезных ссылок."
    )
    await message.answer(text, reply_markup=main_quick_kb())
    # JSON response as required
    data = {"created_user": created, "telegram_id": tg_id}
    await message.answer(f"```\n{json_response('ok', data)}\n```", parse_mode="Markdown")
