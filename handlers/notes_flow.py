# handlers/notes_flow.py
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import requests as dbreq
from keyboards.main_keyboards import note_period_keyboard, back_to_main_keyboard

class NoteStates(StatesGroup):
    choose_pet = State()
    waiting_title = State()
    waiting_period = State()
    waiting_extra = State()
    confirm = State()

async def start_notes(message: types.Message):
    if message.text.lower() != "заметки":
        return
    await message.answer("Выберите нужную вам функцию:\n- добавить заметку\n- удалить заметку\n- изменить заметку", reply_markup=back_to_main_keyboard())

# Добавить заметку (сценарий)
async def start_add_note(message: types.Message, state: FSMContext):
    if message.text.lower() != "добавить заметку":
        return
    # получить список питомцев
    user_resp = await dbreq.get_user_by_telegram(message.from_user.id)
    if user_resp["status"] != "ok":
        await message.answer("Пользователь не найден.")
        return
    user_id = user_resp["data"]["user"]["id"]
    pets_resp = await dbreq.list_pets_for_user(user_id)
    if pets_resp["status"] != "ok" or not pets_resp["data"]["pets"]:
        await message.answer("У вас нет питомцев.")
        return
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for p in pets_resp["data"]["pets"]:
        kb.add(types.KeyboardButton(p["name"]))
    kb.add(types.KeyboardButton("отмена"))
    await message.answer("Выберите кличку питомца для заметки:", reply_markup=kb)
    await NoteStates.choose_pet.set()

async def choose_pet_for_note(message: types.Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await message.answer("Отмена.", reply_markup=back_to_main_keyboard())
        await state.finish()
        return
    await state.update_data(pet_name=message.text.strip())
    await message.answer("Введите название заметки:")
    await NoteStates.waiting_title.set()

async def note_title(message: types.Message, state: FSMContext):
    title = message.text.strip()
    if not title:
        await message.answer("Название обязательно. Введите название:")
        return
    await state.update_data(title=title)
    await message.answer("Выберите периодичность:", reply_markup=note_period_keyboard())
    await NoteStates.waiting_period.set()

async def note_period(message: types.Message, state: FSMContext):
    period = message.text.strip()
    valid = {"не повторять", "6 ч", "день", "неделя", "месяц", "год"}
    if period not in valid:
        await message.answer("Неправильная периодичность. Выберите одну из кнопок.")
        return
    await state.update_data(period=period)
    await message.answer("Введите доп. информацию (или 'нет'):")
    await NoteStates.waiting_extra.set()

async def note_extra(message: types.Message, state: FSMContext):
    extra = message.text.strip()
    if extra.lower() == "нет":
        extra = ""
    data = await state.get_data()
    # найти pet id по имени
    user_resp = await dbreq.get_user_by_telegram(message.from_user.id)
    user_id = user_resp["data"]["user"]["id"]
    pets_resp = await dbreq.list_pets_for_user(user_id)
    pet = None
    for p in pets_resp["data"]["pets"]:
        if p["name"] == data["pet_name"]:
            pet = p
            break
    if not pet:
        await message.answer("Питомец не найден. Операция отменена.")
        await state.finish()
        return
    create_resp = await dbreq.create_note(pet_id=pet["id"], title=data["title"], period=data["period"], extra_info=extra)
    if create_resp["status"] == "ok":
        await message.answer("заметка добавлена", reply_markup=back_to_main_keyboard())
        await message.answer("Валидация: заметка успешно добавлена. Следующий шаг: просмотреть заметки для питомца.")
    else:
        await message.answer("Ошибка при добавлении заметки: " + create_resp.get("error_msg", ""))
    await state.finish()

# Удаление и изменение заметок реализуются аналогично: выбор питомца -> выбор заметки -> действие.
