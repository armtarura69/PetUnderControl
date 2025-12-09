from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Text, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from db.requests import async_session, get_user_by_telegram_id, get_pets_by_user, create_pet, get_pet_by_name, update_pet
from keyboards import profile_kb, confirm_inline_kb, main_quick_kb
from utils import json_response

router = Router()

class AddPetStates(StatesGroup):
    breed = State()
    name = State()
    age = State()
    extra = State()
    confirm = State()

@router.message(Text(equals="профиль"))
async def profile_menu(message: Message):
    await message.answer("Выберите нужную вам функцию", reply_markup=profile_kb())

@router.message(Text(equals="посмотреть профиль"))
async def view_profile(message: Message):
    tg_id = message.from_user.id
    async with async_session() as session:
        user = await get_user_by_telegram_id(tg_id, session)
        if not user:
            await message.answer("Профиль не найден. Выполните /start")
            await message.answer(json_response("error", None, "user_not_found"))
            return
        pets = await get_pets_by_user(user.id, session)
        if not pets:
            await message.answer("пока нет животных")
            await message.answer(json_response("ok", {"pets": []}))
            return
        pets_list = []
        for p in pets:
            pets_list.append({
                "breed": p.breed, "name": p.name, "age": p.age, "extra_info": p.extra_info, "created_at": str(p.created_at)
            })
        await message.answer("Список питомцев:")
        await message.answer(f"```\n{json_response('ok', {'pets': pets_list})}\n```", parse_mode="Markdown")

# Добавление питомца (диалог)
@router.message(Text(equals="добавить питомца"))
async def add_pet_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AddPetStates.breed)
    await message.answer("Введите породу (обязательно):")

@router.message(AddPetStates.breed)
async def add_pet_breed(message: Message, state: FSMContext):
    breed = message.text.strip()
    if not breed:
        await message.answer(json_response("error", None, "breed_required"))
        await message.answer("Порода обязательна. Введите породу:")
        return
    await state.update_data(breed=breed)
    await state.set_state(AddPetStates.name)
    await message.answer("Введите кличку (обязательно):")

@router.message(AddPetStates.name)
async def add_pet_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer(json_response("error", None, "name_required"))
        await message.answer("Кличка обязательна. Введите кличку:")
        return
    await state.update_data(name=name)
    await state.set_state(AddPetStates.age)
    await message.answer("Введите возраст (обязательно):")

@router.message(AddPetStates.age)
async def add_pet_age(message: Message, state: FSMContext):
    age = message.text.strip()
    if not age:
        await message.answer(json_response("error", None, "age_required"))
        await message.answer("Возраст обязателен. Введите возраст:")
        return
    await state.update_data(age=age)
    await state.set_state(AddPetStates.extra)
    await message.answer("Введите доп. информацию (или отправьте 'нет'):")

@router.message(AddPetStates.extra)
async def add_pet_extra(message: Message, state: FSMContext):
    extra = message.text.strip()
    if extra.lower() == "нет":
        extra = None
    await state.update_data(extra=extra)
    data = await state.get_data()
    confirmation = (
        f"Подтвердите данные:\nПорода: {data['breed']}\nКличка: {data['name']}\nВозраст: {data['age']}\nДоп. информация: {data['extra'] or ''}"
    )
    await state.set_state(AddPetStates.confirm)
    await message.answer(confirmation, reply_markup=confirm_inline_kb())

from aiogram import Bot

# Callbacks for confirm/edit
from aiogram.types import CallbackQuery

@router.callback_query(Text(startswith="confirm_"))
async def on_confirm_callback(cq: CallbackQuery, state: FSMContext):
    action = cq.data.split("_", 1)[1]
    if action == "yes":
        data = await state.get_data()
        tg_id = cq.from_user.id
        async with async_session() as session:
            user = await get_user_by_telegram_id(tg_id, session)
            if not user:
                await cq.message.answer(json_response("error", None, "user_not_found"))
                await cq.answer()
                return
            try:
                pet = await create_pet(user.id, data["breed"], data["name"], data["age"], data.get("extra"), session)
            except ValueError as e:
                await cq.message.answer(json_response("error", None, str(e)))
                await cq.message.answer("Ошибка: питомец с такой кличкой уже существует. Введите другую кличку:")
                await state.set_state(AddPetStates.name)
                await cq.answer()
                return
        # success
        resp_data = {
            "pet": {
                "breed": pet.breed, "name": pet.name, "age": pet.age, "extra_info": pet.extra_info, "created_at": str(pet.created_at)
            }
        }
        await cq.message.answer(f"```\n{json_response('ok', resp_data)}\n```", parse_mode="Markdown")
        await cq.message.answer("питомец добавлен в профиль")
        # короткая валидация и следующий шаг
        await cq.message.answer("Валидация: запись создана и видна в профиле. Следующий шаг: /profile -> посмотреть профиль")
        await state.clear()
        await cq.answer()
    else:  # edit
        # предложить редактировать поля
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("порода", callback_data="edit_field_breed"))
        kb.add(InlineKeyboardButton("кличка", callback_data="edit_field_name"))
        kb.add(InlineKeyboardButton("возраст", callback_data="edit_field_age"))
        kb.add(InlineKeyboardButton("доп. информация", callback_data="edit_field_extra"))
        await cq.message.answer("Выберите поле для изменения:", reply_markup=kb)
        await cq.answer()

# Если пользователь выбрал изменить поле — в этом простом варианте переводим FSM в соответствующее состояние
@router.callback_query(Text(startswith="edit_field_"))
async def edit_field_callback(cq: CallbackQuery, state: FSMContext):
    field = cq.data.split("edit_field_")[1]
    mapping = {
        "breed": AddPetStates.breed,
        "name": AddPetStates.name,
        "age": AddPetStates.age,
        "extra": AddPetStates.extra
    }
    await state.set_state(mapping[field])
    await cq.message.answer(f"Введите новое значение для {field}:")
    await cq.answer()
