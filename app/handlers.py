from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from app.calendly import get_available_slots  # ✅ This is the new API function

router = Router()

# FSM: Booking steps
class BookingState(StatesGroup):
    language = State()
    choosing_time = State()

# Language options
LANGUAGES = {
    "🇺🇿 Uzbek": "uz",
    "🇷🇺 Русский": "ru",
    "🇬🇧 English": "en"
}

def language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=lang)] for lang in LANGUAGES],
        resize_keyboard=True,
        one_time_keyboard=True
    )

@router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Please select your language / Пожалуйста, выберите язык / Iltimos, tilni tanlang:",
        reply_markup=language_keyboard()
    )
    await state.set_state(BookingState.language)

@router.message(BookingState.language)
async def set_language(message: types.Message, state: FSMContext):
    lang = LANGUAGES.get(message.text)
    if not lang:
        await message.answer("❗ Please select from the buttons below.")
        return

    await state.update_data(language=lang)
    await message.answer("🔍 Fetching available time slots...")

    try:
        slots = await get_available_slots()  # ✅ REAL CALL TO CALENDLY API
    except Exception as e:
        await message.answer(f"❗ Failed to fetch slots: {str(e)}")
        return

    if not slots:
        await message.answer("😔 No available slots at the moment. Please try later.")

