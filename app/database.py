import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, BigInteger, Text, TIMESTAMP, func

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=False)
Base = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 📦 Define the tokens table
class CalendlyToken(Base):
    __tablename__ = "calendly_tokens"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(BigInteger, unique=True, nullable=False)
    access_token = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

# ⛏ Create table
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 💾 Save token
async def save_token(telegram_user_id: int, access_token: str):
    async with async_session() as session:
        existing = await session.get(CalendlyToken, telegram_user_id)
        if existing:
            existing.access_token = access_token
        else:
            new = CalendlyToken(telegram_user_id=telegram_user_id, access_token=access_token)
            session.add(new)
        await session.commit()

# 📤 Load token
async def get_token(telegram_user_id: int):
    async with async_session() as session:
        return await session.get(CalendlyToken, telegram_user_id)
