"""
Database module for managing SQLite operations
"""
import sqlite3
from datetime import datetime
import os


class Database:
    def __init__(self, db_name="screen_time.db"):
        """Initialize database connection"""
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_table()

    def connect(self):
        """Create database connection"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_table(self):
        """Create app_usage table if it doesn't exist"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT NOT NULL,
                date TEXT NOT NULL,
                total_seconds INTEGER DEFAULT 0,
                UNIQUE(app_name, date)
            )
        """)
        self.conn.commit()

    def update_usage(self, app_name, seconds=1):
        """
        Update time spent on an application for today
        
        Args:
            app_name: Name of the application
            seconds: Number of seconds to add (default: 1)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        try:
            # Try to insert new record or update existing one
            self.cursor.execute("""
                INSERT INTO app_usage (app_name, date, total_seconds)
                VALUES (?, ?, ?)
                ON CONFLICT(app_name, date)
                DO UPDATE SET total_seconds = total_seconds + ?
            """, (app_name, today, seconds, seconds))
            self.conn.commit()
        except Exception as e:
            print(f"Database error: {e}")

    def get_today_usage(self):
        """
        Get all app usage for today
        
        Returns:
            List of tuples (app_name, total_seconds)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        try:
            self.cursor.execute("""
                SELECT app_name, total_seconds
                FROM app_usage
                WHERE date = ?
                ORDER BY total_seconds DESC
            """, (today,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Database error: {e}")
            return []

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
