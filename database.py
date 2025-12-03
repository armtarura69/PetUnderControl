import sqlite3

def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()

    # Профиль
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        name TEXT
    )""")

    # Домашние животные
    c.execute("""CREATE TABLE IF NOT EXISTS pets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        pet_name TEXT,
        pet_type TEXT
    )""")

    # Напоминания
    c.execute("""CREATE TABLE IF NOT EXISTS notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text TEXT,
        remind_at TEXT
    )""")

    conn.commit()
    conn.close()