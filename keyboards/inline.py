from aiogram.utils.keyboard import InlineKeyboardBuilder

def notes_keyboard(notes):
    kb = InlineKeyboardBuilder()

    for note_id, text, remind_at in notes:
        kb.button(
            text=f"{text} | {remind_at}",
            callback_data=f"delete_note:{note_id}"
        )

    kb.adjust(1)
    return kb.as_markup()