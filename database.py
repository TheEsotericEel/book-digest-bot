"""Database module for BookDigest Bot"""
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import config

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            credits INTEGER DEFAULT 0,
            tier TEXT DEFAULT 'free',
            pro_expires_at TEXT,
            last_weekly_credit TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Summaries table (cached summaries)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_title TEXT NOT NULL,
            author TEXT,
            isbn TEXT,
            summary_text TEXT NOT NULL,
            source TEXT DEFAULT 'ai',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(book_title, author)
        )
    """)
    
    # User summaries (access log)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            summary_id INTEGER NOT NULL,
            accessed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id),
            FOREIGN KEY (summary_id) REFERENCES summaries(id)
        )
    """)
    
    # Purchases table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount_stars INTEGER NOT NULL,
            credits_added INTEGER NOT NULL,
            purchase_type TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("[OK] Database initialized successfully")

def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None) -> Dict:
    """Get user or create new one with signup credits"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Try to get existing user
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    
    if user:
        conn.close()
        return dict(user)
    
    # Create new user with free signup credits
    cursor.execute("""
        INSERT INTO users (telegram_id, username, first_name, credits, tier)
        VALUES (?, ?, ?, ?, 'free')
    """, (telegram_id, username, first_name, config.FREE_SIGNUP_CREDITS))
    
    conn.commit()
    
    # Fetch the newly created user
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    
    return dict(user)

def get_user_credits(telegram_id: int) -> int:
    """Get user's current credits"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT credits FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result['credits'] if result else 0

def add_credits(telegram_id: int, credits: int, purchase_type: str = "manual"):
    """Add credits to user account"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET credits = credits + ? WHERE telegram_id = ?
    """, (credits, telegram_id))
    conn.commit()
    conn.close()

def spend_credit(telegram_id: int) -> bool:
    """Spend 1 credit. Returns True if successful, False if insufficient credits"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if user has credits
    credits = get_user_credits(telegram_id)
    if credits < 1:
        conn.close()
        return False
    
    # Deduct credit
    cursor.execute("""
        UPDATE users SET credits = credits - 1 WHERE telegram_id = ?
    """, (telegram_id,))
    conn.commit()
    conn.close()
    return True

def get_or_create_summary(book_title: str, author: str = None) -> Optional[Dict]:
    """Get existing summary or return None"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if author:
        cursor.execute("""
            SELECT * FROM summaries WHERE book_title = ? AND author = ?
        """, (book_title, author))
    else:
        cursor.execute("""
            SELECT * FROM summaries WHERE book_title = ?
        """, (book_title,))
    
    result = cursor.fetchone()
    conn.close()
    
    return dict(result) if result else None

def save_summary(book_title: str, author: str, summary_text: str, isbn: str = None, source: str = "ai") -> int:
    """Save a new summary to database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO summaries (book_title, author, isbn, summary_text, source)
        VALUES (?, ?, ?, ?, ?)
    """, (book_title, author, isbn, summary_text, source))
    
    summary_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return summary_id

def log_user_summary_access(user_id: int, summary_id: int):
    """Log that user accessed a summary"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO user_summaries (user_id, summary_id)
        VALUES (?, ?)
    """, (user_id, summary_id))
    
    conn.commit()
    conn.close()

def get_user_library(telegram_id: int, limit: int = 10) -> List[Dict]:
    """Get user's recently accessed summaries"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.*, us.accessed_at
        FROM summaries s
        JOIN user_summaries us ON s.id = us.summary_id
        WHERE us.user_id = ?
        ORDER BY us.accessed_at DESC
        LIMIT ?
    """, (telegram_id, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

def log_purchase(user_id: int, stars: int, credits: int, purchase_type: str):
    """Log a purchase transaction"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO purchases (user_id, amount_stars, credits_added, purchase_type)
        VALUES (?, ?, ?, ?)
    """, (user_id, stars, credits, purchase_type))
    
    conn.commit()
    conn.close()

def upgrade_to_pro(telegram_id: int, duration_days: int = 30):
    """Upgrade user to pro tier"""
    conn = get_connection()
    cursor = conn.cursor()
    
    expires_at = (datetime.now() + timedelta(days=duration_days)).isoformat()
    
    cursor.execute("""
        UPDATE users 
        SET tier = 'pro', 
            pro_expires_at = ?,
            credits = credits + ?
        WHERE telegram_id = ?
    """, (expires_at, config.MONTHLY_PRO_CREDITS, telegram_id))
    
    conn.commit()
    conn.close()

def get_all_pro_users() -> List[Dict]:
    """Get all active pro users"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM users 
        WHERE tier = 'pro' 
        AND (pro_expires_at IS NULL OR pro_expires_at > datetime('now'))
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

def get_stats() -> Dict:
    """Get overall bot statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total users
    cursor.execute("SELECT COUNT(*) as count FROM users")
    total_users = cursor.fetchone()['count']
    
    # Pro users
    cursor.execute("""
        SELECT COUNT(*) as count FROM users 
        WHERE tier = 'pro' 
        AND (pro_expires_at IS NULL OR pro_expires_at > datetime('now'))
    """)
    pro_users = cursor.fetchone()['count']
    
    # Total summaries generated
    cursor.execute("SELECT COUNT(*) as count FROM summaries")
    total_summaries = cursor.fetchone()['count']
    
    # Total accesses
    cursor.execute("SELECT COUNT(*) as count FROM user_summaries")
    total_accesses = cursor.fetchone()['count']
    
    # Total revenue (in Stars)
    cursor.execute("SELECT SUM(amount_stars) as total FROM purchases")
    result = cursor.fetchone()
    total_revenue_stars = result['total'] if result['total'] else 0
    
    conn.close()
    
    return {
        'total_users': total_users,
        'free_users': total_users - pro_users,
        'pro_users': pro_users,
        'total_summaries': total_summaries,
        'total_accesses': total_accesses,
        'total_revenue_stars': total_revenue_stars,
        'total_revenue_usd': total_revenue_stars * 0.02  # Approximate conversion
    }

if __name__ == "__main__":
    init_db()
