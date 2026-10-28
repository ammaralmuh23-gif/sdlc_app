"""
config.py — إعدادات التطبيق
يقرأ القيم من .env (لا أسرار بالكود) — AR-04, NFR-09
"""
import os
from dotenv import load_dotenv

# تحميل متغيرات .env إلى os.environ
load_dotenv()


class Config:
    # ===== Flask =====
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-fallback-key")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

    # ===== MySQL =====
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "sdlc_manager")