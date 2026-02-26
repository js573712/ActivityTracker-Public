import sqlite3
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

# Allow custom DB path via environment variable, default to project directory
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(DB_DIR, "activity.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    # Enable dict-like row access
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT (datetime('now', 'localtime')),
            date_str TEXT,
            window_title TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_activity(window_title: str):
    conn = get_connection()
    cursor = conn.cursor()
    # Storing a specific date string makes it very easy to group by day later
    today_str = date.today().isoformat()
    cursor.execute(
        "INSERT INTO activity_log (date_str, window_title) VALUES (?, ?)",
        (today_str, window_title)
    )
    conn.commit()
    conn.close()

def get_daily_logs(query_date_str: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, window_title FROM activity_log WHERE date_str = ? ORDER BY timestamp ASC",
        (query_date_str,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
