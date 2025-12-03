from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import sqlite3

from states.note_state import NoteState
from keyboards.calendar import calendar_keyboard, time_keyboard
from keyboards.inline import notes_keyboard

notes_router = Router()

# -----------------------
# Создание заметки — Старт
# -----------------------
@notes_router.message(commands=['add_note'])
async def add_note_start(message: Message, state: FSMContext):
    await state.set_state(NoteState.waiting_for_text)
    await message.answer("Введите текст напоминания:")


# -----------------------
# Ввод текста
# -----------------------
@notes_router.message(NoteState.waiting_for_text)
async def note_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(NoteState.waiting_for_date)
    await message.answer("Выберите дату:", reply_markup=calendar_keyboard())


# -----------------------
# Выбор даты
# -----------------------
@notes_router.callback_query(F.data.startswith("pick_date"))
async def pick_date(callback: CallbackQuery, state: FSMContext):
    date = callback.data.split(":")[1]
    await state.update_data(date=date)
    await state.set_state(NoteState.waiting_for_time)

    await callback.message.edit_text(
        f"Дата выбрана: {date}\nВыберите время:",
        reply_markup=time_keyboard()
    )


# -----------------------
# Выбор времени
# -----------------------
@notes_router.callback_query(F.data.startswith("pick_time"))
async def pick_time(callback: CallbackQuery, state: FSMContext):
    time = callback.data.split(":")[1]
    data = await state.get_data()

    remind_at = f"{data['date']} {time}"

    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO notes(user_id, text, remind_at) VALUES (?, ?, ?)",
        (callback.from_user.id, data['text'], remind_at)
    )
    conn.commit()
    conn.close()

    await state.clear()
    await callback.message.edit_text(f"Напоминание добавлено! 🟢\n{remind_at}")


# -----------------------
# Список заметок с кнопками удаления
# -----------------------
@notes_router.message(commands=['notes'])
async def list_notes(message: Message):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT id, text, remind_at FROM notes WHERE user_id=?", (message.from_user.id,))
    notes = c.fetchall()
    conn.close()

    if not notes:
        return await message.answer("У вас нет напоминаний.")

    await message.answer("Ваши напоминания:", reply_markup=notes_keyboard(notes))


# -----------------------
# Удаление заметки
# -----------------------
@notes_router.callback_query(F.data.startswith("delete_note"))
async def delete_note(callback: CallbackQuery):
    note_id = callback.data.split(":")[1]

    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()

    await callback.answer("Удалено!")
    await callback.message.edit_text("Напоминание удалено.")