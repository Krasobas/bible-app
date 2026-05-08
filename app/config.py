import os

API_KEY = os.getenv("API_KEY", "dev-key-change-me")
SITE_TITLE = os.getenv("SITE_TITLE", "Библейский кружок")
SITE_SUBTITLE = os.getenv("SITE_SUBTITLE", "Комментарий для XXI века")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/bible.db")
