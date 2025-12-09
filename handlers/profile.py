from aiogram import types
from aiogram.dispatcher import Dispatcher
from db import requests as dbreq
from keyboards.main_keyboards import profile_options_keyboard, back_to_main_keyboard
from utils.helpers import make_response_ok, make_response_error

async def on_text_profile(message: types.Message):
    text = message.text.lower()
    if text == "профиль":
        await message.answer("Выберите нужную вам функцию:", reply_markup=profile_options_keyboard())
    elif text == "посмотреть профиль":
        # получить пользователя и его питомцев
        user_resp = await dbreq.get_user_by_telegram(message.from_user.id)
        if user_resp["status"] != "ok":
            await message.answer("Ошибка: " + user_resp.get("error_msg", "user not found"))
            return
        user_id = user_resp["data"]["user"]["id"]
        pets_resp = await dbreq.list_pets_for_user(user_id)
        if pets_resp["status"] != "ok":
            await message.answer("Ошибка при получении питомцев.")
            return
        pets = pets_resp["data"]["pets"]
        if not pets:
            await message.answer("пока нет животных", reply_markup=back_to_main_keyboard())
            await message.answer("Валидация: у пользователя нет питомцев. Следующий шаг: добавьте питомца через «добавить питомца».")
            return
        # формируем вывод
        text_out = "Питомцы:\n\n"
        for p in pets:
            text_out += (
                f"Порода: {p['breed']}\n"
                f"Кличка: {p['name']}\n"
                f"Возраст: {p['age']}\n"
                f"Доп. информация: {p['extra_info']}\n"
                f"Создан: {p['created_at']}\n\n"
            )
        await message.answer(text_out, reply_markup=back_to_main_keyboard())
        await message.answer("Валидация: успешно получены и отображены питомцы. Следующий шаг: выберите питомца для изменения, если нужно.")
    elif text == "на главную":
        await message.answer("Возвращаем на главную", reply_markup=main_reply_keyboard())
