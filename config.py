"""
config.py - central configuration for KrishiMitra
Reads secrets from environment variables (.env) with safe local defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'database' / 'krishimitra.db'}"
    )
    DB_PATH = str(BASE_DIR / "database" / "krishimitra.db")

    # Free public APIs consumed directly from the BROWSER (no key required),
    # exposed here only so templates can reference a single source of truth.
    OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

    # GNews requires a free API key (https://gnews.io/register).
    # The landing page news feed calls our own /api/news proxy route,
    # which uses this key server-side so the key is never exposed to the browser.
    GNEWS_API_KEY = os.environ.get("GNEWS_API_KEY", "")
    GNEWS_URL = "https://gnews.io/api/v4/search"

    MODELS_DIR = BASE_DIR / "models"
    ASSETS_DIR = BASE_DIR / "static" / "assets"

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
