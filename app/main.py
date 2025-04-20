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
from app.calendly_oauth import router as oauth_router
from app.database import init_db  # ✅ DB init

# Load .env variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❗ BOT_TOKEN is missing from .env")

# Initialize aiogram bot (3.7+ syntax)
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Setup dispatcher
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(booking_router)

# Setup FastAPI
app = FastAPI()

# Include Calendly OAuth router
app.include_router(oauth_router)

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "GoStudy Booking Bot is running 🚀"}

# On startup: init DB and start polling bot
@app.on_event("startup")
async def on_startup():
    logging.info("📦 Initializing database...")
    await init_db()

    logging.info("🤖 Starting Telegram bot polling...")
    asyncio.create_task(dp.start_polling(bot))
