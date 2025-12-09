from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from db.requests import async_session, get_user_by_telegram_id, get_pets_by_user, get_pet_by_name, create_note, get_notes_by_pet, delete_note_by_id
from keyboards import notes_kb, main_quick_kb
from utils import json_response

router = Router()

class AddNoteStates(StatesGroup):
    choose_pet = State()
    title = State()
    extra = State()
    period = State()
    confirm = State()

PERIOD_MAP = {
    "не повторять": "не повторять",
    "каждые 6 часов": "6 ч",
    "каждый день": "день",
    "каждую неделю": "неделя",
    "каждый месяц": "месяц",
    "каждый год": "год"
}

@router.message(Text(equals="заметки"))
async def notes_menu(message: Message):
    await message.answer("Выберите нужную вам функцию", reply_markup=notes_kb())

@router.message(Text(equals="добавить заметку"))
async def add_note_start(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    async with async_session() as session:
        user = await get_user_by_telegram_id(tg_id, session)
        if not user:
            await message.answer("Пользователь не найден. Выполните /start")
            await message.answer(json_response("error", None, "user_not_found"))
            return
        pets = await get_pets_by_user(user.id, session)
        if not pets:
            await message.answer("У вас нет питомцев. Добавьте питомца сначала.")
            await message.answer(json_response("error", None, "no_pets"))
            return
        # предложим список имен
        names = [p.name for p in pets]
        await state.update_data(pet_names=names)
    await state.set_state(AddNoteStates.choose_pet)
    await message.answer("Выберите кличку питомца (введите текстом):\n" + ", ".join(names))

@router.message(AddNoteStates.choose_pet)
async def add_note_choose_pet(message: Message, state: FSMContext):
    pet_name = message.text.strip()
    data = await state.get_data()
    if pet_name not in data.get("pet_names", []):
        await message.answer(json_response("error", None, "pet_not_found"))
        await message.answer("Кличка не найдена. Введите корректную кличку:")
        return
    await state.update_data(pet_name=pet_name)
    await state.set_state(AddNoteStates.title)
    await message.answer("Введите название заметки (обязательно):")

@router.message(AddNoteStates.title)
async def add_note_title(message: Message, state: FSMContext):
    title = message.text.strip()
    if not title:
        await message.answer(json_response("error", None, "title_required"))
        await message.answer("Название обязательно. Введите название:")
        return
    await state.update_data(title=title)
    await state.set_state(AddNoteStates.extra)
    await message.answer("Введите доп. информацию (или 'нет'):")

@router.message(AddNoteStates.extra)
async def add_note_extra(message: Message, state: FSMContext):
    extra = message.text.strip()
    if extra.lower() == "нет":
        extra = None
    await state.update_data(extra=extra)
    # ask period
    await state.set_state(AddNoteStates.period)
    await message.answer("Выберите периодичность (введите текстом): не повторять / каждые 6 часов / каждый день / каждую неделю / каждый месяц / каждый год")

@router.message(AddNoteStates.period)
async def add_note_period(message: Message, state: FSMContext):
    period_text = message.text.strip().lower()
    if period_text not in PERIOD_MAP:
        await message.answer(json_response("error", None, "invalid_period"))
        await message.answer("Неверная периодичность. Введите одну из опций:")
        return
    mapped = PERIOD_MAP[period_text]
    await state.update_data(period=mapped)
    data = await state.get_data()
    # confirmation
    confirmation = f"Название: {data['title']}\nПериодичность: {data['period']}\nДоп. информация: {data['extra'] or ''}"
    await state.set_state(AddNoteStates.confirm)
    await message.answer(confirmation + "\n\nОтправьте 'все верно' или 'изменить'")

@router.message(AddNoteStates.confirm)
async def add_note_confirm(message: Message, state: FSMContext):
    text = message.text.strip().lower()
    if text == "все верно":
        data = await state.get_data()
        tg_id = message.from_user.id
        async with async_session() as session:
            user = await get_user_by_telegram_id(tg_id, session)
            pet = await get_pet_by_name(user.id, data["pet_name"], session)
            note = await create_note(pet.id, data["title"], data["period"], data.get("extra"), session)
        resp = {"note": {"title": note.title, "period": note.period, "extra_info": note.extra_info, "created_at": str(note.created_at)}}
        await message.answer(f"```\n{json_response('ok', resp)}\n```", parse_mode="Markdown")
        await message.answer("заметка добавлена")
        await message.answer("Валидация: заметка создана и привязана к питомцу. Следующий шаг: посмотреть заметки через профиль -> питомец")
        await state.clear()
    elif text == "изменить":
        await message.answer("Что изменить? (название / периодичность / доп. информация)")
    else:
        await message.answer(json_response("error", None, "invalid_confirmation"))
        await message.answer("Отправьте 'все верно' или 'изменить'")
