"""Configuration for BookDigest Bot"""
import os

# Bot settings
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set. Please set it before running the bot.")

# Free tier limits
FREE_SIGNUP_CREDITS = 2  # Free summaries on signup
FREE_WEEKLY_CREDITS = 1  # Free summary per week

# Pricing (in Telegram Stars)
CREDIT_PACK_5_STARS = 250  # 5 summaries for 250 Stars (~$5)
MONTHLY_PRO_STARS = 500    # 15 summaries/month for 500 Stars (~$10)
MONTHLY_PRO_CREDITS = 15

# API Keys (optional - fallback to local generation)
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY", "")

# Database
DB_PATH = "bookdigest.db"

# Summary settings
MAX_SUMMARY_LENGTH = 2000  # Characters
MIN_SUMMARY_LENGTH = 500

# Feature flags
ENABLE_PAYMENTS = True  # Set to False for testing without Stars
ENABLE_DAILY_RECOMMENDATIONS = True
