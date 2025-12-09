import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from db.requests import init_db
from handlers.start_handlers import router as start_router
from handlers.profile_handlers import router as profile_router
from handlers.notes_handlers import router as notes_router

async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(notes_router)
    try:
        print("Bot starting...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
