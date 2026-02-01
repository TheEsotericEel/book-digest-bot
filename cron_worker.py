"""BookDigest Bot - Daily Cron Worker"""
import logging
import os
import random
from datetime import datetime, timedelta
import requests
from telegram import Bot
import asyncio

import config
import database as db

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('cron_worker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Popular books for daily recommendations
BOOK_RECOMMENDATIONS = [
    {"title": "Atomic Habits", "author": "James Clear"},
    {"title": "Deep Work", "author": "Cal Newport"},
    {"title": "The 7 Habits of Highly Effective People", "author": "Stephen Covey"},
    {"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman"},
    {"title": "Sapiens", "author": "Yuval Noah Harari"},
    {"title": "The Lean Startup", "author": "Eric Ries"},
    {"title": "How to Win Friends and Influence People", "author": "Dale Carnegie"},
    {"title": "The 4-Hour Workweek", "author": "Tim Ferriss"},
    {"title": "Start With Why", "author": "Simon Sinek"},
    {"title": "The Power of Habit", "author": "Charles Duhigg"},
    {"title": "Mindset", "author": "Carol Dweck"},
    {"title": "Grit", "author": "Angela Duckworth"},
    {"title": "The Subtle Art of Not Giving a F*ck", "author": "Mark Manson"},
    {"title": "Zero to One", "author": "Peter Thiel"},
    {"title": "Good to Great", "author": "Jim Collins"}
]

async def send_daily_recommendations():
    """Send book recommendations to Pro users"""
    logger.info("📚 Sending daily book recommendations...")
    
    if not config.ENABLE_DAILY_RECOMMENDATIONS:
        logger.info("Daily recommendations disabled in config")
        return
    
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    pro_users = db.get_all_pro_users()
    
    if not pro_users:
        logger.info("No pro users to send recommendations to")
        return
    
    # Pick a random book
    book = random.choice(BOOK_RECOMMENDATIONS)
    
    message = f"""📚 **Book of the Day**

**{book['title']}**
by {book['author']}

💡 Pro tip: Get a summary now and start your day with knowledge!

Use: `/summary {book['title']}`

---
Want daily recommendations? Stay Pro! ⭐
"""
    
    sent_count = 0
    for user in pro_users:
        try:
            await bot.send_message(
                chat_id=user['telegram_id'],
                text=message,
                parse_mode='Markdown'
            )
            sent_count += 1
            await asyncio.sleep(0.1)  # Rate limiting
        except Exception as e:
            logger.error(f"Error sending to user {user['telegram_id']}: {e}")
    
    logger.info(f"✅ Sent recommendations to {sent_count}/{len(pro_users)} pro users")

async def refresh_weekly_credits():
    """Give free users 1 credit per week"""
    logger.info("🔄 Refreshing weekly credits...")
    
    import sqlite3
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get users who haven't received weekly credit in the last 7 days
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    
    cursor.execute("""
        SELECT telegram_id FROM users
        WHERE tier = 'free'
        AND (last_weekly_credit IS NULL OR last_weekly_credit < ?)
    """, (week_ago,))
    
    users_to_update = cursor.fetchall()
    
    if not users_to_update:
        logger.info("No users eligible for weekly credits")
        conn.close()
        return
    
    # Update credits
    for row in users_to_update:
        user_id = row[0]
        cursor.execute("""
            UPDATE users 
            SET credits = credits + ?,
                last_weekly_credit = ?
            WHERE telegram_id = ?
        """, (config.FREE_WEEKLY_CREDITS, datetime.now().isoformat(), user_id))
    
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Added {config.FREE_WEEKLY_CREDITS} credit(s) to {len(users_to_update)} free users")

async def check_expired_pro():
    """Check and downgrade expired Pro subscriptions"""
    logger.info("⏰ Checking for expired Pro subscriptions...")
    
    import sqlite3
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Find expired pro users
    cursor.execute("""
        UPDATE users
        SET tier = 'free'
        WHERE tier = 'pro'
        AND pro_expires_at IS NOT NULL
        AND pro_expires_at < datetime('now')
    """)
    
    expired_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    if expired_count > 0:
        logger.info(f"⬇️ Downgraded {expired_count} expired Pro users to free tier")
    else:
        logger.info("No expired Pro users")

async def cleanup_old_data():
    """Clean up old data (>90 days)"""
    logger.info("🧹 Cleaning up old data...")
    
    import sqlite3
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Delete user_summaries older than 90 days
    ninety_days_ago = (datetime.now() - timedelta(days=90)).isoformat()
    
    cursor.execute("""
        DELETE FROM user_summaries
        WHERE accessed_at < ?
    """, (ninety_days_ago,))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    logger.info(f"🗑️ Deleted {deleted} old access records")

async def log_daily_stats():
    """Log daily statistics"""
    logger.info("📊 Logging daily stats...")
    
    stats = db.get_stats()
    
    logger.info(f"""
    📈 Daily Stats Report
    ==================
    Total Users: {stats['total_users']}
    Free Users: {stats['free_users']}
    Pro Users: {stats['pro_users']}
    Summaries: {stats['total_summaries']}
    Accesses: {stats['total_accesses']}
    Revenue: {stats['total_revenue_stars']} Stars (${stats['total_revenue_usd']:.2f})
    ==================
    """)

async def main():
    """Main cron job function"""
    logger.info("=" * 50)
    logger.info(f"🤖 BookDigest Cron Worker - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)
    
    try:
        # Run all tasks
        await send_daily_recommendations()
        await refresh_weekly_credits()
        await check_expired_pro()
        await cleanup_old_data()
        await log_daily_stats()
        
        logger.info("✅ Cron job completed successfully")
    
    except Exception as e:
        logger.error(f"❌ Cron job error: {e}", exc_info=True)
    
    logger.info("=" * 50)

if __name__ == "__main__":
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
        exit(1)
    
    # Run async main
    asyncio.run(main())
