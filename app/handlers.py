from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

from app.database import get_token
from app.calendly import get_user_slots

router = Router()

# FSM: Booking flow steps
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

    telegram_user_id = message.from_user.id
    user_data = await get_token(telegram_user_id)

    if not user_data:
        # User is not connected yet
        connect_url = f"https://gostudybot.onrender.com/auth/connect?telegram_id={telegram_user_id}"
        await message.answer(
            f"🔐 Please connect your Calendly account first:\n\n<a href=\"{connect_url}\">Connect Calendly</a>",
            parse_mode="HTML"
        )
        return

    await message.answer("🔍 Fetching your available time slots...")

    try:
        slots = await get_user_slots(user_data.access_token)
    except Exception as e:
        await message.answer(f"❗ Failed to fetch slots: {str(e)}")
        return

    if not slots:
        await message.answer("😔 No available slots at the moment. Please try again later.")
        return

    buttons = [
        [InlineKeyboardButton(text=slot, callback_data=f"book:{slot}")]
        for slot in slots
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer("✅ Available time slots:", reply_markup=markup)
    await state.set_state(BookingState.choosing_time)

@router.callback_query(F.data.startswith("book:"))
async def user_selected_time(callback: types.CallbackQuery, state: FSMContext):
    slot = callback.data.split("book:")[1]
    await state.update_data(slot=slot)

    await callback.message.answer(
        f"🧾 You selected: <b>{slot}</b>\n\n💳 Please select a payment method:",
        parse_mode="HTML"
    )

    # ⚠️ Placeholder — payment integration will go here
    await callback.message.answer("💳 Payment flow will begin here in the next step.")
