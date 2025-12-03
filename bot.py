import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import TOKEN
from database import init_db

# Роутеры
from handlers.profile import profile_router
from handlers.pets import pets_router
from handlers.notes import notes_router

# Фоновая задача напоминаний
from reminder_service import reminder_task


async def main():
    # Инициализация базы
    init_db()

    # Создаём экземпляры бота и диспетчера
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # Подключаем обработчики
    dp.include_router(profile_router)
    dp.include_router(pets_router)
    dp.include_router(notes_router)

    # Фоновая задача — запустить напоминания
    asyncio.create_task(reminder_task(bot))

    print("Бот запущен!")

    # Старт long-polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен.")