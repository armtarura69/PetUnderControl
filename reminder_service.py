import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot

async def reminder_task(bot: Bot):
    """Фоновая задача проверки напоминаний каждые 30 секунд."""

    while True:
        try:
            conn = sqlite3.connect("bot.db")
            c = conn.cursor()

            # Текущее время
            now = datetime.now().strftime("%Y-%m-%d %H:%M")

            # Получить все просроченные напоминания
            c.execute("SELECT id, user_id, text FROM notes WHERE remind_at <= ?", (now,))
            due_notes = c.fetchall()

            # Отправляем пользователям напоминания
            for note_id, user_id, text in due_notes:
                try:
                    await bot.send_message(user_id, f"🔔 Напоминание:\n{text}")
                except Exception as e:
                    print(f"Ошибка отправки: {e}")

                # Удаление напоминания, чтобы не отправлять снова
                c.execute("DELETE FROM notes WHERE id=?", (note_id,))
                conn.commit()

            conn.close()

        except Exception as e:
            print("Ошибка в reminder_task:", e)

        # Спим 30 секунд и проверяем снова
        await asyncio.sleep(30)