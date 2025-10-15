"""
Основной модуль Telegram бота для секстинга
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import config
from characters import get_character, get_characters_keyboard_data, CHARACTERS
from ai_provider import get_ai_provider

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# AI провайдер
ai_provider = get_ai_provider()

# Состояния бота
class ChatStates(StatesGroup):
    choosing_character = State()
    chatting = State()


# Хранилище историй чатов
user_sessions = {}


def get_character_selection_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора персонажа"""
    buttons = []
    
    for char_data in get_characters_keyboard_data():
        buttons.append([
            InlineKeyboardButton(
                text=f"{char_data['emoji']} {char_data['name']}",
                callback_data=f"char_{char_data['id']}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_chat_menu_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру меню во время чата"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Сменить персонажа", callback_data="change_char")],
        [InlineKeyboardButton(text="🗑 Очистить историю", callback_data="clear_history")],
        [InlineKeyboardButton(text="ℹ️ Информация", callback_data="char_info")]
    ])


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    
    # Инициализируем сессию пользователя
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "character": None,
            "history": []
        }
    
    welcome_text = (
        "🔥 <b>Добро пожаловать в SecretChat!</b> 🔥\n\n"
        "Здесь ты можешь пообщаться с разными AI персонажами на взрослые темы.\n\n"
        "⚠️ <b>Важно:</b>\n"
        "• Это пространство для взрослых (18+)\n"
        "• Все диалоги анонимны и приватны\n"
        "• Уважай границы и получай удовольствие\n\n"
        "Выбери персонажа, с которым хочешь пообщаться:"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_character_selection_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ChatStates.choosing_character)


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Показать меню"""
    await message.answer(
        "⚙️ <b>Меню управления:</b>",
        reply_markup=get_chat_menu_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("change"))
async def cmd_change_character(message: Message, state: FSMContext):
    """Смена персонажа"""
    await message.answer(
        "Выбери нового персонажа:",
        reply_markup=get_character_selection_keyboard()
    )
    await state.set_state(ChatStates.choosing_character)


@router.callback_query(F.data.startswith("char_"))
async def select_character(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора персонажа"""
    user_id = callback.from_user.id
    character_id = callback.data.replace("char_", "")
    
    character = get_character(character_id)
    if not character:
        await callback.answer("Ошибка: персонаж не найден")
        return
    
    # Сохраняем выбор
    user_sessions[user_id] = {
        "character_id": character_id,
        "character": character,
        "history": []
    }
    
    await state.set_state(ChatStates.chatting)
    
    # Отправляем приветствие от персонажа
    greeting_text = (
        f"💬 <b>Начат чат с: {character['name']}</b>\n\n"
        f"{character['greeting']}\n\n"
        f"<i>Используй /menu для управления чатом</i>"
    )
    
    await callback.message.edit_text(
        greeting_text,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "change_char")
async def callback_change_character(callback: CallbackQuery, state: FSMContext):
    """Смена персонажа через callback"""
    await callback.message.edit_text(
        "Выбери нового персонажа:",
        reply_markup=get_character_selection_keyboard()
    )
    await state.set_state(ChatStates.choosing_character)
    await callback.answer()


@router.callback_query(F.data == "clear_history")
async def callback_clear_history(callback: CallbackQuery):
    """Очистка истории чата"""
    user_id = callback.from_user.id
    
    if user_id in user_sessions:
        user_sessions[user_id]["history"] = []
    
    await callback.answer("✅ История чата очищена!", show_alert=True)


@router.callback_query(F.data == "char_info")
async def callback_character_info(callback: CallbackQuery):
    """Показать информацию о персонаже"""
    user_id = callback.from_user.id
    
    if user_id not in user_sessions or not user_sessions[user_id].get("character"):
        await callback.answer("Сначала выбери персонажа", show_alert=True)
        return
    
    character = user_sessions[user_id]["character"]
    
    info_text = (
        f"{character['emoji']} <b>{character['name']}</b>\n\n"
        f"{character['description']}\n\n"
        f"📝 Сообщений в истории: {len(user_sessions[user_id]['history'])}"
    )
    
    await callback.message.answer(info_text, parse_mode="HTML")
    await callback.answer()


@router.message(ChatStates.chatting)
async def handle_chat_message(message: Message, state: FSMContext):
    """Обработчик сообщений в чате"""
    user_id = message.from_user.id
    
    # Проверяем, выбран ли персонаж
    if user_id not in user_sessions or not user_sessions[user_id].get("character"):
        await message.answer(
            "Сначала выбери персонажа с помощью /start",
            reply_markup=get_character_selection_keyboard()
        )
        return
    
    user_text = message.text
    session = user_sessions[user_id]
    character = session["character"]
    
    # Отправляем индикатор набора текста
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Генерируем ответ от AI
        response = await ai_provider.generate_response(
            system_prompt=character["system_prompt"],
            conversation_history=session["history"],
            user_message=user_text
        )
        
        # Сохраняем в историю
        session["history"].append({"role": "user", "content": user_text})
        session["history"].append({"role": "assistant", "content": response})
        
        # Ограничиваем размер истории
        if len(session["history"]) > config.MAX_HISTORY_LENGTH * 2:
            session["history"] = session["history"][-config.MAX_HISTORY_LENGTH * 2:]
        
        # Отправляем ответ
        await message.answer(response)
        
    except Exception as e:
        logger.error(f"Ошибка генерации ответа: {e}")
        await message.answer(
            "😔 Извини, произошла ошибка. Попробуй еще раз или напиши /menu для управления."
        )


@router.message(ChatStates.choosing_character)
async def handle_message_without_character(message: Message):
    """Обработчик сообщений когда персонаж не выбран"""
    await message.answer(
        "Сначала выбери персонажа:",
        reply_markup=get_character_selection_keyboard()
    )


async def main():
    """Запуск бота"""
    dp.include_router(router)
    
    logger.info("🤖 Бот запущен!")
    logger.info(f"🔧 AI Provider: OpenRouter")
    logger.info(f"🤖 Модель: {config.MODEL_NAME}")
    logger.info(f"📝 Персонажей загружено: {len(CHARACTERS)}")
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

