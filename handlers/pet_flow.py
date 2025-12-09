from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from db import requests as dbreq
from keyboards.main_keyboards import pet_confirm_keyboard, back_to_main_keyboard
import re

class PetStates(StatesGroup):
    waiting_breed = State()
    waiting_name = State()
    waiting_age = State()
    waiting_extra = State()
    confirm = State()

async def start_add_pet(message: types.Message):
    if message.text.lower() != "добавить питомца":
        return
    await message.answer("Введите породу питомца:", reply_markup=back_to_main_keyboard())
    await PetStates.waiting_breed.set()

async def pet_breed(message: types.Message, state: FSMContext):
    await state.update_data(breed=message.text.strip())
    await message.answer("Введите кличку питомца:")
    await PetStates.waiting_name.set()

async def pet_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    # простая валидация: не пустое, нет спецсимволов начала/конца
    if not name:
        await message.answer("Кличка не может быть пустой. Введите кличку:")
        return
    await state.update_data(name=name)
    await message.answer("Введите возраст (строкой):")
    await PetStates.waiting_age.set()

async def pet_age(message: types.Message, state: FSMContext):
    age = message.text.strip()
    if not age:
        await message.answer("Возраст обязателен. Введите возраст:")
        return
    await state.update_data(age=age)
    await message.answer("Введите доп. информацию (или напишите «нет»):")
    await PetStates.waiting_extra.set()

async def pet_extra(message: types.Message, state: FSMContext):
    extra = message.text.strip()
    if extra.lower() == "нет":
        extra = ""
    await state.update_data(extra_info=extra)
    data = await state.get_data()
    summary = (
        f"Порода: {data['breed']}\n"
        f"Кличка: {data['name']}\n"
        f"Возраст: {data['age']}\n"
        f"Доп. информация: {data['extra_info'] or ''}"
    )
    await message.answer("Подтвердите данные:\n\n" + summary, reply_markup=pet_confirm_keyboard())
    await PetStates.confirm.set()

async def pet_confirm(message: types.Message, state: FSMContext):
    text = message.text.lower()
    if text == "все верно":
        data = await state.get_data()
        # создать питомца
        user_resp = await dbreq.get_user_by_telegram(message.from_user.id)
        if user_resp["status"] != "ok":
            await message.answer("Ошибка при нахождении профиля: " + user_resp.get("error_msg", ""))
            await state.finish()
            return
        user_id = user_resp["data"]["user"]["id"]
        create_resp = await dbreq.create_pet(user_id=user_id, breed=data["breed"], name=data["name"], age=data["age"], extra_info=data.get("extra_info"))
        if create_resp["status"] == "ok":
            pet = create_resp["data"]["pet"]
            await message.answer("питомец добавлен в профиль", reply_markup=back_to_main_keyboard())
            # валидация результата + следующий шаг
            await message.answer(f"Валидация: питомец '{pet['name']}' успешно добавлен. Следующий шаг: смотреть профиль или добавить заметку.")
        else:
            await message.answer("Ошибка при добавлении питомца: " + create_resp.get("error_msg", ""))
        await state.finish()
    elif text == "изменить":
        # предложим поочередно изменять поля — начинаем с породы
        await state.update_data(await state.get_data())
        await message.answer("Введите породу заново:")
        await PetStates.waiting_breed.set()
    else:
        await message.answer("Операция отменена.", reply_markup=back_to_main_keyboard())
        await state.finish()

# Редактирование: краткая реализация (выбор питомца по кличке -> выбор поля -> ввод нового значения)
from aiogram.dispatcher.filters import Text

async def start_edit_pet(message: types.Message, state: FSMContext):
    if message.text.lower() != "изменить информацию о питомце":
        return
    # получить список питомцев пользователя
    user_resp = await dbreq.get_user_by_telegram(message.from_user.id)
    if user_resp["status"] != "ok":
        await message.answer("Пользователь не найден.")
        return
    user_id = user_resp["data"]["user"]["id"]
    pets_resp = await dbreq.list_pets_for_user(user_id)
    if pets_resp["status"] != "ok" or not pets_resp["data"]["pets"]:
        await message.answer("У вас нет питомцев.")
        return
    # предложим список кличек
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for p in pets_resp["data"]["pets"]:
        kb.add(types.KeyboardButton(p["name"]))
    kb.add(types.KeyboardButton("отмена"))
    await message.answer("Выберите кличку питомца для изменения:", reply_markup=kb)
    await state.set_state("waiting_choose_pet")

async def choose_pet_to_edit(message: types.Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await message.answer("Отмена.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("на главную"))
        await state.finish()
        return
    selected_name = message.text.strip()
    user_resp = await dbreq.get_user_by_telegram(message.from_user.id)
    user_id = user_resp["data"]["user"]["id"]
    # найти питомца по имени
    pets_resp = await dbreq.list_pets_for_user(user_id)
    pet = None
    for p in pets_resp["data"]["pets"]:
        if p["name"] == selected_name:
            pet = p
            break
    if not pet:
        await message.answer("Питомец не найден. Попробуйте снова.")
        return
    await state.update_data(edit_pet_id=pet["id"])
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("порода"))
    kb.add(types.KeyboardButton("кличка"))
    kb.add(types.KeyboardButton("возраст"))
    kb.add(types.KeyboardButton("доп. информация"))
    kb.add(types.KeyboardButton("отмена"))
    await message.answer("Выберите поле для изменения:", reply_markup=kb)
    await state.set_state("waiting_field_choice")

async def field_choice(message: types.Message, state: FSMContext):
    text = message.text.lower()
    if text == "отмена":
        await message.answer("Отмена.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("на главную"))
        await state.finish()
        return
    mapping = {"порода": "breed", "кличка": "name", "возраст": "age", "доп. информация": "extra_info"}
    if text not in mapping:
        await message.answer("Неизвестное поле. Выберите снова.")
        return
    await state.update_data(edit_field=mapping[text])
    await message.answer(f"Введите новое значение для {text}:")
    await state.set_state("waiting_new_value")

async def new_value_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    pet_id = data.get("edit_pet_id")
    field = data.get("edit_field")
    value = message.text.strip()
    if not value:
        await message.answer("Значение не может быть пустым.")
        return
    resp = await dbreq.update_pet_field(pet_id, field, value)
    if resp["status"] == "ok":
        await message.answer("Информация обновлена.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("на главную"))
        await message.answer("Валидация: поле обновлено успешно. Следующий шаг: проверить профиль.")
    else:
        await message.answer("Ошибка при обновлении: " + resp.get("error_msg", ""))
    await state.finish()
