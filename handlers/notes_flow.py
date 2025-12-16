# handlers/notes_flow.py
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import requests as dbreq
from keyboards.main_keyboards import (
    note_period_keyboard,
    pet_confirm_keyboard,
    back_to_main_keyboard
)
from keyboards.main_keyboards import main_reply_keyboard


class NoteStates(StatesGroup):
    waiting_pet = State()
    waiting_title = State()
    waiting_period = State()
    waiting_extra = State()
    confirm = State()

async def start_notes(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Выберите нужную вам функцию:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Добавить заметку")],
                [types.KeyboardButton(text="На главную")]
            ],
            resize_keyboard=True
        )
    )

# ▶ Старт добавления заметки
async def start_add_note(message: types.Message, state: FSMContext):
    if message.text.lower() != "добавить заметку":
        return

    user_resp = await dbreq.get_user_by_telegram(message.from_user.id)
    if user_resp["status"] != "ok":
        await message.answer("Пользователь не найден.")
        return

    user_id = user_resp["data"]["user"]["id"]
    pets_resp = await dbreq.list_pets_for_user(user_id)

    if not pets_resp["data"]["pets"]:
        await message.answer("У вас нет питомцев.", reply_markup=back_to_main_keyboard())
        return

    buttons = [
        [types.KeyboardButton(text=p["name"])]
        for p in pets_resp["data"]["pets"]
    ]

    kb = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

    await message.answer("Выберите питомца для заметки:", reply_markup=kb)
    await state.set_state(NoteStates.waiting_pet)


# ▶ Выбор питомца
async def note_choose_pet(message: types.Message, state: FSMContext):
    await state.update_data(pet_name=message.text.strip())
    await message.answer("Введите название заметки:",  reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(NoteStates.waiting_title)


# ▶ Название
async def note_title(message: types.Message, state: FSMContext):
    title = message.text.strip()
    if not title:
        await message.answer("Название не может быть пустым. Введите снова:")
        return
    await state.update_data(title=title)
    await message.answer("Выберите периодичность:", reply_markup=note_period_keyboard())
    await state.set_state(NoteStates.waiting_period)


# ▶ Период
async def note_period(message: types.Message, state: FSMContext):
    valid = {"Не повторять", "6 ч", "День", "Неделя", "Месяц", "Год"}
    if message.text not in valid:
        await message.answer("Выберите периодичность кнопкой.")
        return
    await state.update_data(period=message.text)
    await message.answer("Введите доп. информацию (или «Нет»):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(NoteStates.waiting_extra)


# ▶ Доп. информация
async def note_extra(message: types.Message, state: FSMContext):
    extra = message.text.strip()
    if extra.lower() == "нет":
        extra = ""

    await state.update_data(extra_info=extra)
    data = await state.get_data()

    summary = (
        f"Питомец: {data['pet_name']}\n"
        f"Название: {data['title']}\n"
        f"Периодичность: {data['period']}\n"
        f"Доп. информация: {data['extra_info'] or '-'}"
    )

    await message.answer(
        "Подтвердите данные:\n\n" + summary,
        reply_markup=pet_confirm_keyboard()
    )
    await state.set_state(NoteStates.confirm)


# ▶ Подтверждение
async def note_confirm(message: types.Message, state: FSMContext):
    text = message.text.lower()

    if text == "все верно":
        data = await state.get_data()

        user_resp = await dbreq.get_user_by_telegram(message.from_user.id)
        user_id = user_resp["data"]["user"]["id"]

        pets_resp = await dbreq.list_pets_for_user(user_id)
        pet = next((p for p in pets_resp["data"]["pets"] if p["name"] == data["pet_name"]), None)

        if not pet:
            await message.answer("Питомец не найден.", reply_markup=back_to_main_keyboard())
            await state.clear()
            return

        resp = await dbreq.create_note(
            pet_id=pet["id"],
            title=data["title"],
            period=data["period"],
            extra_info=data["extra_info"]
        )

        if resp["status"] == "ok":
            await message.answer("Заметка добавлена 📝")
            await message.answer(
                "Главное меню:",
                reply_markup=main_reply_keyboard()
            )

        else:
            await message.answer("Ошибка: " + resp.get("error_msg", ""))

        await state.clear()

    elif text == "изменить":
        await message.answer("Введите название заметки заново:", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(NoteStates.waiting_title)

    else:
        await message.answer("Операция отменена.", reply_markup=back_to_main_keyboard())
        await state.clear()
