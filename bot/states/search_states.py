"""FSM states for search flow"""
from aiogram.fsm.state import State, StatesGroup


class SearchStates(StatesGroup):
    """Состояния поиска"""
    waiting_for_query = State()
    showing_results = State()
    waiting_for_selection = State()


class RemixStates(StatesGroup):
    """Состояния выбора ремикса"""
    waiting_for_remix_type = State()
    processing_remix = State()


class VoiceStates(StatesGroup):
    """Состояния для голосовых сообщений"""
    waiting_for_voice = State()
    recognizing = State()
