"""Search keyboards"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List
from ..models import Track, RemixType


def search_results_keyboard(tracks: List[Track], page: int = 0) -> InlineKeyboardMarkup:
    """
    Клавиатура результатов поиска
    
    Args:
        tracks: список треков (обычно 5 максимум)
        page: номер страницы (для "ещё результаты")
    """
    buttons = []
    
    for i, track in enumerate(tracks, 1):
        # Номер. Исполнитель - Название
        button_text = f"{i}. {track.artist} — {track.title}"
        button_text = button_text[:64]  # Лимит Telegram
        
        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"select_track_{i-1}"
            )
        ])
    
    # Кнопка "Ещё результаты"
    if page < 10:  # Максимум 10 страниц
        buttons.append([
            InlineKeyboardButton(
                text="📄 Ещё результаты",
                callback_data=f"more_results_{page+1}"
            )
        ])
    
    # Кнопка новый поиск
    buttons.append([
        InlineKeyboardButton(
            text="🔍 Новый поиск",
            callback_data="new_search"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def remix_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора типа ремикса"""
    buttons = [
        [InlineKeyboardButton(text="🎵 Original", callback_data="remix_original")],
        [InlineKeyboardButton(text="🐢 Slowed", callback_data="remix_slowed")],
        [InlineKeyboardButton(text="⚡ Sped Up", callback_data="remix_sped_up")],
        [InlineKeyboardButton(text="💣 Bass Boosted", callback_data="remix_bass_boosted")],
        [InlineKeyboardButton(text="🔥 Nightcore", callback_data="remix_nightcore")],
        [InlineKeyboardButton(text="🌀 Reverb", callback_data="remix_reverb")],
        [InlineKeyboardButton(text="📻 Lofi", callback_data="remix_lofi")],
        [InlineKeyboardButton(text="🎸 Acoustic", callback_data="remix_acoustic")],
        [InlineKeyboardButton(text="🎹 Instrumental", callback_data="remix_instrumental")],
        [InlineKeyboardButton(text="🎤 Live", callback_data="remix_live")],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_search"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_search")
        ],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def main_menu() -> ReplyKeyboardMarkup:
    """Главное меню"""
    buttons = [
        [KeyboardButton(text="🔍 Поиск музыки")],
        [KeyboardButton(text="🎤 Голосовой поиск")],
        [KeyboardButton(text="❓ Помощь")],
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура отмены"""
    buttons = [
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_search")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
