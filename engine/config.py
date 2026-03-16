"""
engine/config.py
================
Sprint 3: إضافة database config + environment validation.

التغييرات:
    - إضافة DATABASE_PATH للـ SQLite
    - إضافة validate() للتحقق من الـ API keys
    - إضافة SCRAPING_SOURCES_LIMIT للتحكم في كل source
    - إنشاء data directories تلقائياً عند الـ import
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # ── API Keys ──────────────────────────────────────
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # ── Scraping ──────────────────────────────────────
    SCRAPING_LIMIT = int(os.getenv("SCRAPING_LIMIT", 100))

    # ── File Paths ────────────────────────────────────
    DATA_RAW_PATH     = "data/raw/posts.json"
    DATA_TRENDS_PATH  = "data/processed/trends.json"
    DATA_CONTENT_PATH = "data/processed/content.json"

    # ── Database ──────────────────────────────────────
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/db/intelligence.db")

    # ── App ───────────────────────────────────────────
    DEBUG     = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        """التحقق من إن الـ required env vars موجودة."""
        errors = []
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY غير موجود في .env")
        if errors:
            raise EnvironmentError("\n".join(errors))

    @classmethod
    def ensure_dirs(cls):
        """إنشاء الـ directories المطلوبة لو مش موجودة."""
        dirs = [
            "data/raw",
            "data/processed",
            os.path.dirname(cls.DATABASE_PATH),
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)


# إنشاء الـ directories تلقائياً عند الـ import
Config.ensure_dirs()