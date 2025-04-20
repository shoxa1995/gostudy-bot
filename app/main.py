import os
import logging
import asyncio
from fastapi import FastAPI
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from app.handlers import router as booking_router
from app.calendly_oauth import router as oauth_router  # ✅ Calendly OAuth router

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Get Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❗ BOT_TOKEN is missing in .env")

# Initialize aiogram bot (v3.7+ format)
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Setup dispatcher
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(booking_router)

# Initialize FastAPI app
app = FastAPI()

# ✅ Register OAuth routes
app.include_router(oauth_router)

# Health check route for Render
@app.get("/")
async def root():
    return {"message": "GoStudy Booking Bot is running 🚀"}

# On startup, launch aiogram polling
@app.on_event("startup")
async def on_startup():
    logging.info("Starting Telegram bot polling...")
    asyncio.create_task(dp.start_polling(bot))
