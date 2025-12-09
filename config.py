import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8232380348:AAFY9GFrV1eLPRLEOm_nCMc5r6LNnB1E48k")  # обязательно: перед запуском положите BOT_TOKEN в .env
DB_PATH = os.getenv("DB_PATH", "sqlite:///pets.db")
