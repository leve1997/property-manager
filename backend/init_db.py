import sqlite3
import os
import bcrypt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "backend/database.db"

# Default users for initial setup
USERS = [
    ("admin", "MirnaPal25!"),
]

def ensure_schema(cursor):
    """Create tables if they don't exist."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manager TEXT NOT NULL,
            building TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def seed_users(cursor):
    """Insert default users if they don't exist."""
    for username, password in USERS:
        if not password:
            print(f"⚠️  Skipping user '{username}': PASSWORD not set in .env")
            continue
            
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            print(f"✓ User '{username}' already exists")
            continue
        
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        print(f"✓ Created user: {username}")


def main():
    """Initialize database with schema and seed data."""
    print(f"Initializing database at: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        ensure_schema(cursor)
        print("✓ Database schema created")
        
        seed_users(cursor)
        
        conn.commit()
        print("\n✅ Database initialization complete!")
        print(f"📍 Database location: {DB_PATH}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during initialization: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
