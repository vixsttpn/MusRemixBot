"""MusRemixBot - Advanced Telegram Music Search & Remix Bot"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from bot.config import BOT_TOKEN, ADMIN_ID, TEMP_DIR, LOGS_DIR
from bot.models import Track, UserContext, RemixType, SearchResult
from bot.services import VKService, SearchService, VoiceService, RemixService
from bot.keyboards.search_kb import (
    search_results_keyboard, remix_type_keyboard,
    main_menu, cancel_keyboard
)
from bot.states.search_states import SearchStates, RemixStates, VoiceStates

# ============ LOGGING ============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============ BOT SETUP ============
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# ============ SERVICES ============
vk_service = VKService()
search_service = SearchService(vk_service)
voice_service = VoiceService()
remix_service = RemixService(TEMP_DIR)

# ============ USER CONTEXTS ============
user_contexts: Dict[int, UserContext] = {}
user_search_messages: Dict[int, int] = {}  # user_id -> message_id для удаления


def get_user_context(user_id: int) -> UserContext:
    """Получить контекст пользователя"""
    if user_id not in user_contexts:
        user_contexts[user_id] = UserContext(user_id)
    return user_contexts[user_id]


# ============ HANDLERS ============
@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Команда /start"""
    await message.answer(
        "🎵 Добро пожаловать в MusRemixBot!\n\n"
        "Найди любую песню, выбери обработку и слушай!\n\n"
        "Используй кнопки ниже или отправь название песни.",
        reply_markup=main_menu()
    )
    logger.info(f"User {message.from_user.id} started bot")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Команда /help"""
    await message.answer(
        "📖 Справка:\n\n"
        "1️⃣ Введи название песни\n"
        "2️⃣ Выбери трек из результатов\n"
        "3️⃣ Выбери тип обработки\n"
        "4️⃣ Получи готовый файл!\n\n"
        "💡 Поддерживаемые форматы:\n"
        "• Original\n"
        "• Slowed\n"
        "• Sped Up\n"
        "• Bass Boosted\n"
        "• Nightcore\n"
        "• Reverb\n"
        "• Lofi\n"
        "• Acoustic\n"
        "• Instrumental\n"
        "• Live"
    )


@router.message(F.text == "🔍 Поиск музыки")
@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext) -> None:
    """Начать поиск"""
    context = get_user_context(message.from_user.id)
    context.reset()  # Сброс контекста для нового поиска
    
    await state.set_state(SearchStates.waiting_for_query)
    await message.answer(
        "🔍 Напиши название песни или исполнителя:",
        reply_markup=cancel_keyboard()
    )


@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext) -> None:
    """Обработать поисковый запрос"""
    user_id = message.from_user.id
    context = get_user_context(user_id)
    
    query = message.text.strip()
    if not query or len(query) < 2:
        await message.answer("❌ Слишком короткий запрос. Попробуй ещё раз.")
        return
    
    # Показать статус
    status_msg = await message.answer("🔎 Ищу музыку...")
    
    try:
        # Поиск
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        search_result = await search_service.search(query, limit=50)
        
        if not search_result.tracks:
            await status_msg.delete()
            await message.answer(
                "❌ Ничего не найдено.\n\n"
                "Попробуй другой запрос или проверь название.",
                reply_markup=cancel_keyboard()
            )
            return
        
        # Сохранить результаты
        context.current_query = query
        context.search_results = search_result.tracks
        context.search_page = 0
        
        # Показать первые 5 результатов
        tracks_page = search_result.tracks[:5]
        
        # Удалить старое сообщение если было
        if user_id in user_search_messages:
            try:
                await bot.delete_message(
                    message.chat.id,
                    user_search_messages[user_id]
                )
            except:
                pass
        
        # Удалить статус
        await status_msg.delete()
        
        # Показать результаты
        result_text = f"🎵 Найдено: {len(search_result.tracks)} треков\n\n"
        result_text += "\n".join(
            f"{i}. {t.artist} — {t.title}"
            for i, t in enumerate(tracks_page, 1)
        )
        result_text += "\n\nВыбери номер композиции:"
        
        result_msg = await message.answer(
            result_text,
            reply_markup=search_results_keyboard(tracks_page)
        )
        
        # Сохранить ID сообщения результатов
        user_search_messages[user_id] = result_msg.message_id
        
        await state.set_state(SearchStates.showing_results)
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        await status_msg.delete()
        await message.answer(
            f"❌ Ошибка поиска:\n{str(e)[:100]}",
            reply_markup=cancel_keyboard()
        )


@router.callback_query(SearchStates.showing_results, F.data.startswith("select_track_"))
async def select_track(callback: CallbackQuery, state: FSMContext) -> None:
    """Выбрать трек"""
    user_id = callback.from_user.id
    context = get_user_context(user_id)
    
    try:
        index = int(callback.data.replace("select_track_", ""))
        
        if not context.search_results or index >= len(context.search_results):
            await callback.answer("❌ Трек больше не доступен. Сделай новый поиск.")
            return
        
        # Выбранный трек
        track = context.search_results[index]
        context.selected_track = track
        
        # Удалить сообщение с результатами
        try:
            await callback.message.delete()
        except:
            pass
        
        # Показать меню выбора ремикса
        text = f"🎧 {track.artist} — {track.title}\n\n"
        text += "Выбери версию обработки:"
        
        await callback.message.answer(
            text,
            reply_markup=remix_type_keyboard()
        )
        
        await state.set_state(RemixStates.waiting_for_remix_type)
        await callback.answer()
    
    except Exception as e:
        logger.error(f"Track selection error: {e}")
        await callback.answer(f"❌ Ошибка: {str(e)[:50]}")


@router.callback_query(RemixStates.waiting_for_remix_type, F.data.startswith("remix_"))
async def select_remix_type(callback: CallbackQuery, state: FSMContext) -> None:
    """Выбрать тип ремикса"""
    user_id = callback.from_user.id
    context = get_user_context(user_id)
    
    if not context.selected_track:
        await callback.answer("❌ Трек не выбран. Сделай новый поиск.")
        return
    
    # Получить тип ремикса
    remix_str = callback.data.replace("remix_", "")
    try:
        remix_type = RemixType(remix_str)
    except ValueError:
        await callback.answer("❌ Неизвестный тип ремикса")
        return
    
    context.selected_remix = remix_type
    
    # Показать статус обработки
    await callback.message.edit_text(
        f"🎧 {context.selected_track.artist} — {context.selected_track.title}\n\n"
        f"⏳ Обрабатываю {remix_type.value}...",
        reply_markup=None
    )
    
    await state.set_state(RemixStates.processing_remix)
    
    try:
        # Скачать оригинал
        vk_url = await vk_service.get_audio_url(context.selected_track.id)
        if not vk_url:
            await callback.message.edit_text(
                "❌ Не смог получить аудиофайл.\n"
                "Попробуй другой трек.",
                reply_markup=cancel_keyboard()
            )
            context.reset_selection()
            return
        
        # Скачать
        input_file = TEMP_DIR / f"{user_id}_original.mp3"
        success = await vk_service.download_audio(vk_url, str(input_file))
        
        if not success:
            await callback.message.edit_text(
                "❌ Ошибка скачивания.\n"
                "Попробуй позже.",
                reply_markup=cancel_keyboard()
            )
            context.reset_selection()
            return
        
        # Обработать
        output_file = TEMP_DIR / f"{user_id}_{remix_type.value}.mp3"
        remix_ok = await remix_service.create_remix(
            input_file,
            output_file,
            remix_type
        )
        
        if not remix_ok:
            await callback.message.edit_text(
                "❌ Ошибка обработки.\n"
                "Попробуй другой тип ремикса.",
                reply_markup=remix_type_keyboard()
            )
            context.reset_selection()
            return
        
        # Проверить качество
        valid = await remix_service.validate_audio(output_file)
        if not valid:
            await callback.message.edit_text(
                "❌ Обработанный файл повреждён.\n"
                "Попробуй снова.",
                reply_markup=remix_type_keyboard()
            )
            context.reset_selection()
            return
        
        # Отправить файл
        await callback.message.edit_text(
            f"✅ {remix_type.value.replace('_', ' ').title()} готов!\n\n"
            "📤 Отправляю файл...",
            reply_markup=None
        )
        
        await callback.message.answer_audio(
            FSInputFile(output_file),
            title=f"{context.selected_track.artist} — {context.selected_track.title}",
            performer=context.selected_track.artist,
            caption=f"🎵 {remix_type.value.replace('_', ' ').upper()}"
        )
        
        await callback.message.answer(
            "✅ Готово! Поиск ещё музыки?",
            reply_markup=main_menu()
        )
        
        # Очистить временные файлы
        try:
            input_file.unlink()
            output_file.unlink()
        except:
            pass
        
        # Сбросить выбор для следующего трека
        context.reset_selection()
        await state.clear()
    
    except Exception as e:
        logger.error(f"Remix processing error: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка: {str(e)[:100]}",
            reply_markup=remix_type_keyboard()
        )
        context.reset_selection()


@router.callback_query(F.data == "cancel_search")
async def cancel_search(callback: CallbackQuery, state: FSMContext) -> None:
    """Отмена поиска"""
    user_id = callback.from_user.id
    context = get_user_context(user_id)
    context.reset()
    
    try:
        await callback.message.delete()
    except:
        pass
    
    await callback.message.answer(
        "❌ Отменено.",
        reply_markup=main_menu()
    )
    await state.clear()


@router.callback_query(F.data == "new_search")
async def new_search(callback: CallbackQuery, state: FSMContext) -> None:
    """Новый поиск"""
    user_id = callback.from_user.id
    context = get_user_context(user_id)
    context.reset()
    
    await state.set_state(SearchStates.waiting_for_query)
    await callback.message.answer(
        "🔍 Напиши название новой песни:",
        reply_markup=cancel_keyboard()
    )


@router.message(F.text)
async def handle_text(message: Message, state: FSMContext) -> None:
    """Обработать текстовое сообщение"""
    if message.text.startswith('/'):
        return
    
    # Если не в состоянии поиска - начать новый поиск
    current_state = await state.get_state()
    if current_state != SearchStates.waiting_for_query:
        await cmd_search(message, state)
    else:
        # Обработать как поисковый запрос
        await process_search_query(message, state)


# ============ STARTUP/SHUTDOWN ============
async def on_startup():
    """Инициализация"""
    await vk_service.init_session()
    logger.info("✅ MusRemixBot started")


async def on_shutdown():
    """Завершение"""
    await vk_service.close_session()
    logger.info("✅ MusRemixBot stopped")


# ============ MAIN ============
async def main():
    """Запуск бота"""
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    logger.info("🚀 Starting bot...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
