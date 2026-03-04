import sqlite3
import os
import bcrypt
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("DB_PATH", str(BASE_DIR / "backend" / "database.db")))


# Default users — loaded from environment variables
USERS = [
    ("admin", os.getenv("PASSWORD_ADMIN")),
    ("user1", os.getenv("PASSWORD_USER1")),
    ("user2", os.getenv("PASSWORD_USER2")),
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
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT UNIQUE NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS property_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            activity_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            note TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE RESTRICT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
    )


def seed_users(cursor):
    """Insert default users if they don't exist."""
    for username, password in USERS:
        if not password:
            print(f"⚠️  Skipping user '{username}': password not set in .env")
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

    # Ensure the backend directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"Initializing database at: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
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