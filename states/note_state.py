from aiogram.fsm.state import State, StatesGroup

class NoteState(StatesGroup):
    waiting_for_text = State()
    waiting_for_date = State()
    waiting_for_time = State()